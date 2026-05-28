"""FastAPI-Router für ``backend/catalog`` unter ``/api/catalog`` und
``/api/anon/{operation_url}/catalog`` (Phase 4 Schritt 4.1).

Vier Rollen-Sichten:

  • **Plattform-Admin** — voller CRUD auf ``/categories`` und ``/base``.
  • **Disponent** — voller CRUD auf ``/tenant`` (Tenant-Extensions) **nur**
    für den eigenen Mandanten.
  • **Carer** — nur Read auf ``/`` (effektiver Catalog des eigenen
    Mandanten); kein Schreib-Zugriff.
  • **Anon** — Read auf ``/anon/{operation_url}/catalog`` (effektiver
    Catalog der Operation, die zur aktiven anonymen Session gehört).
    Session-Pflicht plus Rate-Limit IP+URL-AND analog ADR-013, mit
    eigenem Schlüsselraum und großzügigeren Limits (Catalog-Read ist
    kein Brute-Force-Pfad — Rate-Limit dient nur als Anti-DoS und Anti-
    Programmer-Loop-Bug-Schutz).

Berechtigungs-Modell folgt ADR-008 (Multi-Disponent ohne Lead) und
Regel-014 (Teilnahme-Filter): Disponent darf nur eigenen Tenant
verwalten. Cross-Tenant-Zugriff für Disponent → 403.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.api import extract_client_ip, get_db_session, get_valkey_client
from eb_digital.auth.rate_limit import incr_and_check, reset
from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
)
from eb_digital.auth.sessions import SessionUser, get_current_session_user
from eb_digital.auth_anonymous.sessions import get_current_anonymous_session
from eb_digital.auth_anonymous.tokens import verify_url_token
from eb_digital.catalog import repositories as catalog_repo
from eb_digital.catalog import use_cases as catalog_use_cases
from eb_digital.catalog.models import (
    CatalogCategory,
    CatalogItemBase,
    CatalogItemTenantExtension,
)
from eb_digital.catalog.schemas import (
    BaseItemCreate,
    BaseItemResponse,
    BaseItemUpdate,
    CategoryCreate,
    CategoryResponse,
    ResolvedCatalogItem,
    TenantExtensionOverrideCreate,
    TenantExtensionOwnCreate,
    TenantExtensionResponse,
    TenantExtensionUpdate,
    iso,
)
from eb_digital.operations.models import OPERATION_STATUS_ACTIVE
from eb_digital.operations.models import Operation as OperationModel
from eb_digital.settings import get_settings
from eb_digital.tenants.use_cases import TenantNotActiveError, TenantNotFoundError

# Rate-Limit-Konfiguration für den Anon-Catalog-Pfad. Analog ADR-013-Pattern
# (IP+URL AND), aber großzügigere Limits: Catalog-Read ist kein Brute-Force-
# Pfad — Schutz richtet sich gegen Programmer-Loop-Bugs (z. B. Reconnect-
# Schleife im Frontend) und gegen DoS.
_ANON_CATALOG_LIMIT: Final[int] = 60
_ANON_CATALOG_WINDOW_SECONDS: Final[int] = 15 * 60
_ANON_CATALOG_RATELIMIT_PREFIX: Final[str] = "catalog:ratelimit:anon"


def _anon_catalog_ip_key(ip: str) -> str:
    return f"{_ANON_CATALOG_RATELIMIT_PREFIX}:ip:{ip}"


def _anon_catalog_url_key(url_token: str) -> str:
    """Hashed Key analog ``auth_anonymous`` — Klartext-Token nie im Valkey-Key."""
    digest = hashlib.sha256(url_token.encode("utf-8")).hexdigest()
    return f"{_ANON_CATALOG_RATELIMIT_PREFIX}:url:{digest}"


# ─── Berechtigungs-Helper ────────────────────────────────────────────────────


def _require_session(request: Request) -> SessionUser:
    user = get_current_session_user(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return user


def _require_platform_admin(request: Request) -> SessionUser:
    user = _require_session(request)
    if user.kind != KIND_PLATFORM_ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Platform admin role required.",
        )
    return user


def _require_dispatcher_with_tenant(request: Request) -> tuple[SessionUser, uuid.UUID]:
    """Dispatcher der aktiven Session, mit explizitem ``tenant_id``-Binding.

    Rückgabe als Tupel (User, Tenant-ID), damit das Tenant-Binding für mypy
    sichtbar non-None ist — Defense-in-depth-Pattern statt asserts.
    """
    user = _require_session(request)
    if user.kind != KIND_DISPATCHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispatcher role required.",
        )
    if user.tenant_id is None:
        # Sollte technisch nicht eintreten (Dispatcher-Login setzt tenant_id),
        # ist aber Defense-in-depth.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispatcher session is missing tenant binding.",
        )
    return user, user.tenant_id


def _require_admin_or_dispatcher_of_tenant(
    request: Request,
    tenant_id: uuid.UUID,
) -> SessionUser:
    """Plattform-Admin (jeder Tenant) **oder** Dispatcher des angegebenen Mandanten.

    Carer wird abgelehnt — Catalog-Pflege liegt auf der Anbieterseite, nicht
    bei Carer-Accounts.
    """
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN:
        return user
    if user.kind == KIND_DISPATCHER and user.tenant_id == tenant_id:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only platform admin or dispatcher of this tenant may act here.",
    )


def _require_carer_or_dispatcher(request: Request) -> tuple[SessionUser, uuid.UUID]:
    """Carer **oder** Dispatcher mit Tenant-Binding (für Read auf ``/catalog``).

    Rückgabe als Tupel (User, Tenant-ID) für mypy-sichtbares Non-None.
    """
    user = _require_session(request)
    if user.kind in (KIND_CARER, KIND_DISPATCHER):
        if user.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Session is missing tenant binding.",
            )
        return user, user.tenant_id
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Carer or dispatcher role required.",
    )


# ─── Response-Builder ────────────────────────────────────────────────────────


def _category_to_response(category: CatalogCategory) -> CategoryResponse:
    return CategoryResponse(
        id=str(category.id),
        name=category.name,
        created_at=iso(category.created_at),
        updated_at=iso(category.updated_at),
    )


def _base_item_to_response(item: CatalogItemBase) -> BaseItemResponse:
    return BaseItemResponse(
        id=str(item.id),
        name=item.name,
        unit=item.unit,
        default_unit_label=item.default_unit_label,
        description=item.description,
        category_id=str(item.category_id),
        is_active=item.is_active,
        created_at=iso(item.created_at),
        updated_at=iso(item.updated_at),
    )


def _extension_to_response(ext: CatalogItemTenantExtension) -> TenantExtensionResponse:
    return TenantExtensionResponse(
        id=str(ext.id),
        tenant_id=str(ext.tenant_id),
        base_item_id=str(ext.base_item_id) if ext.base_item_id is not None else None,
        name=ext.name,
        unit=ext.unit,
        default_unit_label=ext.default_unit_label,
        description=ext.description,
        category_id=str(ext.category_id) if ext.category_id is not None else None,
        override_name=ext.override_name,
        override_unit_label=ext.override_unit_label,
        is_disabled=ext.is_disabled,
        created_at=iso(ext.created_at),
        updated_at=iso(ext.updated_at),
    )


# ─── Authenticated Router (``/api/catalog``) ─────────────────────────────────


router = APIRouter(prefix="/catalog", tags=["catalog"])


# Categories ─────────────────────────────────────────────────────────────────


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_409_CONFLICT: {"description": "Category name already taken."},
    },
)
async def create_category_endpoint(
    payload: CategoryCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> CategoryResponse:
    _require_platform_admin(request)
    try:
        category = await catalog_use_cases.create_category(db, name=payload.name)
    except catalog_repo.CategoryNameTakenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category name already taken.",
        ) from exc
    await db.commit()
    return _category_to_response(category)


@router.get(
    "/categories",
    response_model=list[CategoryResponse],
    responses={status.HTTP_403_FORBIDDEN: {"description": "Forbidden."}},
)
async def list_categories_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[CategoryResponse]:
    # Read-Zugriff für jede authentifizierte Rolle — Kategorien sind nicht
    # mandantenspezifisch und können auch von Disponenten gelesen werden
    # (sie brauchen die Liste beim Anlegen eigener Tenant-Items).
    _require_session(request)
    categories = await catalog_repo.list_categories(db)
    return [_category_to_response(c) for c in categories]


# Base Items ─────────────────────────────────────────────────────────────────


@router.post(
    "/base",
    response_model=BaseItemResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Category not found."},
    },
)
async def create_base_item_endpoint(
    payload: BaseItemCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> BaseItemResponse:
    _require_platform_admin(request)
    try:
        category_id = uuid.UUID(payload.category_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="category_id is not a valid UUID.",
        ) from exc
    try:
        item = await catalog_use_cases.create_base_item(
            db,
            name=payload.name,
            unit=payload.unit,
            default_unit_label=payload.default_unit_label,
            category_id=category_id,
            description=payload.description,
        )
    except catalog_use_cases.CategoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        ) from exc
    await db.commit()
    return _base_item_to_response(item)


@router.get(
    "/base",
    response_model=list[BaseItemResponse],
    responses={status.HTTP_403_FORBIDDEN: {"description": "Forbidden."}},
)
async def list_base_items_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    include_inactive: Annotated[bool, Query()] = False,
) -> list[BaseItemResponse]:
    """Liste aller Base-Items.

    ``include_inactive=True`` ist nur für Plattform-Admin erlaubt (sieht
    auch deaktivierte Einträge). Disponent/Carer: nur aktive Items.
    """
    user = _require_session(request)
    effective_include_inactive = include_inactive and user.kind == KIND_PLATFORM_ADMIN
    items = await catalog_repo.list_base_items(db, include_inactive=effective_include_inactive)
    return [_base_item_to_response(i) for i in items]


@router.get(
    "/base/{base_item_id}",
    response_model=BaseItemResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Base item not found."},
    },
)
async def get_base_item_endpoint(
    base_item_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> BaseItemResponse:
    _require_session(request)
    item = await catalog_repo.find_base_item_by_id(db, base_item_id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base item not found.",
        )
    return _base_item_to_response(item)


@router.patch(
    "/base/{base_item_id}",
    response_model=BaseItemResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Base item or category not found."},
    },
)
async def update_base_item_endpoint(
    base_item_id: uuid.UUID,
    payload: BaseItemUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> BaseItemResponse:
    _require_platform_admin(request)
    category_uuid: uuid.UUID | None = None
    if payload.category_id is not None:
        try:
            category_uuid = uuid.UUID(payload.category_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="category_id is not a valid UUID.",
            ) from exc
    try:
        item = await catalog_use_cases.update_base_item(
            db,
            base_item_id=base_item_id,
            name=payload.name,
            unit=payload.unit,
            default_unit_label=payload.default_unit_label,
            category_id=category_uuid,
            description=payload.description,
            is_active=payload.is_active,
        )
    except catalog_use_cases.BaseItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base item not found.",
        ) from exc
    except catalog_use_cases.CategoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        ) from exc
    await db.commit()
    return _base_item_to_response(item)


# Tenant Extensions ──────────────────────────────────────────────────────────


@router.post(
    "/tenant/override",
    response_model=TenantExtensionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Base item or tenant not found."},
        status.HTTP_409_CONFLICT: {
            "description": "Override already exists or base item not active.",
        },
    },
)
async def create_override_endpoint(
    payload: TenantExtensionOverrideCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantExtensionResponse:
    _, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        base_item_id = uuid.UUID(payload.base_item_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="base_item_id is not a valid UUID.",
        ) from exc
    try:
        ext = await catalog_use_cases.create_tenant_override(
            db,
            tenant_id=tenant_id,
            base_item_id=base_item_id,
            override_name=payload.override_name,
            override_unit_label=payload.override_unit_label,
        )
    except TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        ) from exc
    except TenantNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant is not active (status={exc.status!r}).",
        ) from exc
    except catalog_use_cases.BaseItemNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Base item not found.",
        ) from exc
    except catalog_use_cases.BaseItemNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Base item is not active; cannot override.",
        ) from exc
    except catalog_repo.DuplicateOverrideError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Override for this base item already exists for tenant.",
        ) from exc
    await db.commit()
    return _extension_to_response(ext)


@router.post(
    "/tenant/own",
    response_model=TenantExtensionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Category or tenant not found."},
        status.HTTP_409_CONFLICT: {"description": "Tenant not active."},
    },
)
async def create_own_item_endpoint(
    payload: TenantExtensionOwnCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantExtensionResponse:
    _, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        category_id = uuid.UUID(payload.category_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="category_id is not a valid UUID.",
        ) from exc
    try:
        ext = await catalog_use_cases.create_tenant_own_item(
            db,
            tenant_id=tenant_id,
            name=payload.name,
            unit=payload.unit,
            default_unit_label=payload.default_unit_label,
            category_id=category_id,
            description=payload.description,
        )
    except TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        ) from exc
    except TenantNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant is not active (status={exc.status!r}).",
        ) from exc
    except catalog_use_cases.CategoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        ) from exc
    await db.commit()
    return _extension_to_response(ext)


@router.get(
    "/tenant",
    response_model=list[TenantExtensionResponse],
    responses={status.HTTP_403_FORBIDDEN: {"description": "Forbidden."}},
)
async def list_tenant_extensions_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    tenant_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[TenantExtensionResponse]:
    """Liste der Tenant-Extensions.

    Plattform-Admin kann ``tenant_id``-Query-Parameter setzen, um einen
    beliebigen Mandanten zu inspizieren. Dispatcher: Query wird ignoriert
    und auf den eigenen ``tenant_id`` gesetzt (Regel-014, Cross-Tenant-
    Read verboten).
    """
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN:
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Platform admin must specify ?tenant_id=… to list extensions.",
            )
        effective_tenant_id = tenant_id
    elif user.kind == KIND_DISPATCHER and user.tenant_id is not None:
        effective_tenant_id = user.tenant_id
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    extensions = await catalog_repo.list_extensions_for_tenant(db, effective_tenant_id)
    return [_extension_to_response(e) for e in extensions]


@router.patch(
    "/tenant/{extension_id}",
    response_model=TenantExtensionResponse,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Extension or category not found."},
        status.HTTP_409_CONFLICT: {"description": "Mode mismatch."},
    },
)
async def update_extension_endpoint(
    extension_id: uuid.UUID,
    payload: TenantExtensionUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantExtensionResponse:
    # Berechtigung: Plattform-Admin oder Dispatcher des zugehörigen Tenants.
    # Tenant-Match wird hier explizit geprüft, weil die Extension-ID nicht
    # implizit die Tenant-Zugehörigkeit trägt.
    existing = await catalog_repo.find_extension_by_id(db, extension_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant extension not found.",
        )
    _require_admin_or_dispatcher_of_tenant(request, existing.tenant_id)

    category_uuid: uuid.UUID | None = None
    if payload.category_id is not None:
        try:
            category_uuid = uuid.UUID(payload.category_id)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="category_id is not a valid UUID.",
            ) from exc

    try:
        ext = await catalog_use_cases.update_tenant_extension(
            db,
            extension_id=extension_id,
            override_name=payload.override_name,
            override_unit_label=payload.override_unit_label,
            name=payload.name,
            unit=payload.unit,
            default_unit_label=payload.default_unit_label,
            category_id=category_uuid,
            description=payload.description,
            is_disabled=payload.is_disabled,
        )
    except catalog_use_cases.ExtensionNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant extension not found.",
        ) from exc
    except catalog_use_cases.ExtensionModeError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Extension is not in {exc.expected_mode!r} mode; "
                "cannot apply update for that mode."
            ),
        ) from exc
    except catalog_use_cases.CategoryNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found.",
        ) from exc
    await db.commit()
    return _extension_to_response(ext)


# Resolver — Read für Carer/Dispatcher ───────────────────────────────────────


@router.get(
    "",
    response_model=list[ResolvedCatalogItem],
    responses={status.HTTP_403_FORBIDDEN: {"description": "Forbidden."}},
)
async def resolve_for_own_tenant_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[ResolvedCatalogItem]:
    """Effektiver Katalog für den Tenant der aktuellen Session.

    Carer oder Dispatcher; Plattform-Admin sollte den Resolver pro
    Tenant über ``/anon/{operation_url}/catalog`` o. ä. nutzen — die
    Plattform-Admin-Sicht auf einen Mandanten ist hier bewusst nicht
    exponiert, weil Plattform-Admin im Normalfall keine Operation-/
    Tenant-Bindung in der Session hat.
    """
    _, tenant_id = _require_carer_or_dispatcher(request)
    return await catalog_use_cases.resolve_catalog_for_tenant(db, tenant_id)


# ─── Anon Router (``/api/anon/{operation_url}/catalog``) ─────────────────────


anon_router = APIRouter(prefix="/anon", tags=["catalog_anon"])


@anon_router.get(
    "/{url_token}/catalog",
    response_model=list[ResolvedCatalogItem],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Active anonymous session required."},
        status.HTTP_403_FORBIDDEN: {"description": "Session does not match URL token."},
        status.HTTP_410_GONE: {"description": "Operation not active."},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded."},
    },
)
async def anon_catalog_endpoint(
    url_token: Annotated[str, Path(min_length=1)],
    request: Request,
    response: Response,
    valkey: Annotated[Redis, Depends(get_valkey_client)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[ResolvedCatalogItem]:
    """Effektiver Catalog der Operation, die zur aktiven Anon-Session gehört.

    Ablauf:
      1. Rate-Limit IP+URL AND (analog ADR-013, eigener Schlüsselraum).
      2. URL-Token verifizieren (Signatur muss stimmen).
      3. Anonyme Session aus Cookie lesen; muss zur Operation passen.
      4. Operation muss ``active`` sein.
      5. Resolver-Aufruf gegen die Operation.
    """
    # 1) Rate-Limit
    ip = extract_client_ip(request)
    ip_key = _anon_catalog_ip_key(ip)
    url_key = _anon_catalog_url_key(url_token)
    ip_result = await incr_and_check(
        valkey, ip_key, limit=_ANON_CATALOG_LIMIT, window_seconds=_ANON_CATALOG_WINDOW_SECONDS
    )
    url_result = await incr_and_check(
        valkey, url_key, limit=_ANON_CATALOG_LIMIT, window_seconds=_ANON_CATALOG_WINDOW_SECONDS
    )
    if not (ip_result.allowed and url_result.allowed):
        retry_after = max(ip_result.retry_after_seconds, url_result.retry_after_seconds)
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many catalog requests. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    # 2) URL-Token verifizieren
    settings = get_settings()
    operation_id_from_url = verify_url_token(url_token, settings.secret_key.get_secret_value())
    if operation_id_from_url is None:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Operation nicht erreichbar.")

    # 3) Anonyme Session prüfen + Operation-Match
    anon_session = get_current_anonymous_session(request)
    if anon_session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Active anonymous session required.",
        )
    if anon_session.operation_id != operation_id_from_url:
        # Cookie-Operation passt nicht zur URL — verdächtig (Session-Reuse?).
        # 403 statt 401, damit Frontend kein erneutes /session anstößt.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Session does not match URL token.",
        )

    # 4) Operation aktiv?
    op_stmt = select(OperationModel).where(OperationModel.id == operation_id_from_url)
    operation = (await db.execute(op_stmt)).scalar_one_or_none()
    if operation is None or operation.status != OPERATION_STATUS_ACTIVE:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Operation nicht erreichbar.")

    # 5) URL-Counter zurücksetzen bei erfolgreichem Read (analog 2.2/2.3-Pattern).
    await reset(valkey, url_key)
    return await catalog_use_cases.resolve_catalog_for_operation(db, operation_id_from_url)


__all__ = [
    "anon_router",
    "router",
]
