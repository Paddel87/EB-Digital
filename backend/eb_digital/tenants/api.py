"""FastAPI-Router für Mandanten-Verwaltung unter ``/api/tenants``.

Endpunkte:

  • ``GET /api/tenants`` — Plattform-Admin: alle (optional ``?status=`` Filter);
    Dispatcher: nur eigener Tenant; Carer: 403.
  • ``GET /api/tenants/{tenant_id}`` — Plattform-Admin: jeder; Dispatcher: nur
    eigener Tenant; Carer: 403.
  • ``POST /api/tenants/{tenant_id}/approve`` — nur Plattform-Admin. Idempotent.
  • ``POST /api/tenants/{tenant_id}/deactivate`` — nur Plattform-Admin. Idempotent.
  • ``POST /api/tenants/{tenant_id}/dispatchers`` — Plattform-Admin oder
    bestehender Dispatcher des Mandanten. Antwort enthält ``reset_token`` (in
    Phase 1, bis Email-Versand kommt).
  • ``POST /api/tenants/{tenant_id}/carers`` — analog.

Berechtigungs-Modell folgt ADR-008 (Multi-Disponent ohne Lead): alle
Dispatcher des Mandanten sind in Verwaltungs-Aktionen gleichberechtigt.
Plattform-Admin hat Cross-Mandanten-Zugriff.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.api import get_db_session
from eb_digital.auth.repositories import KIND_DISPATCHER, KIND_PLATFORM_ADMIN
from eb_digital.auth.sessions import SessionUser, get_current_session_user
from eb_digital.settings import Settings, get_settings
from eb_digital.tenants import repositories as tenants_repo
from eb_digital.tenants import use_cases as tenants_use_cases
from eb_digital.tenants.models import (
    ALLOWED_TENANT_STATUS,
    Tenant,
)

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


async def _require_admin_or_dispatcher_of(
    request: Request,
    tenant_id: uuid.UUID,
    session: AsyncSession,
) -> SessionUser:
    """Plattform-Admin **oder** Dispatcher des angegebenen Mandanten.

    Carer wird konsequent geblockt — Dispatcher-/Carer-Verwaltung ist
    Anbieterseiten-Hoheit der Disponenten und der Plattform-Administration.
    """
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN:
        return user
    if user.kind == KIND_DISPATCHER:
        ok = await tenants_repo.is_dispatcher_of_tenant(
            session,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
        )
        if ok:
            return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Only platform admin or dispatcher of this tenant may act here.",
    )


# ─── Pydantic-Modelle ────────────────────────────────────────────────────────


class TenantResponse(BaseModel):
    id: str
    name: str
    slug: str
    status: str
    applied_at: str
    activated_at: str | None
    deactivated_at: str | None

    @classmethod
    def from_tenant(cls, tenant: Tenant) -> TenantResponse:
        return cls(
            id=str(tenant.id),
            name=tenant.name,
            slug=tenant.slug,
            status=tenant.status,
            applied_at=tenant.applied_at.isoformat(),
            activated_at=tenant.activated_at.isoformat() if tenant.activated_at else None,
            deactivated_at=(tenant.deactivated_at.isoformat() if tenant.deactivated_at else None),
        )


class InviteUserRequest(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    # Email ist optional. In Phase 1 kein Email-Versand — das Feld ist Vorrat
    # für Phase 7 (dort folgt strenge Validierung via ``email-validator`` als
    # neue Top-Level-Dep). Hier nur Length-Constraint, um eklatante
    # Müll-Werte (Mega-Strings) abzuwehren.
    email: str | None = Field(default=None, max_length=254)


class InviteUserResponse(BaseModel):
    user_id: str
    reset_token: str
    expires_in_seconds: int


# ─── Router ──────────────────────────────────────────────────────────────────


router = APIRouter(prefix="/tenants", tags=["tenants"])

PLATFORM_ADMIN_TENANT_LIST_DESCRIPTION: Final[str] = (
    "Plattform-Admin sieht alle Tenants (optional gefiltert nach status). "
    "Dispatcher sieht nur den eigenen Tenant."
)


@router.get(
    "",
    response_model=list[TenantResponse],
    description=PLATFORM_ADMIN_TENANT_LIST_DESCRIPTION,
)
async def list_tenants_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> list[TenantResponse]:
    user = _require_session(request)
    if status_filter is not None and status_filter not in ALLOWED_TENANT_STATUS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown status filter: {status_filter!r}",
        )
    if user.kind == KIND_PLATFORM_ADMIN:
        tenants = await tenants_repo.list_tenants(db, status_filter=status_filter)
    elif user.kind == KIND_DISPATCHER:
        if user.tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Dispatcher session is missing tenant binding.",
            )
        tenant = await tenants_repo.find_tenant_by_id(db, user.tenant_id)
        tenants = [tenant] if tenant is not None else []
        if status_filter is not None:
            tenants = [t for t in tenants if t.status == status_filter]
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Carer role may not access tenants endpoint.",
        )
    return [TenantResponse.from_tenant(t) for t in tenants]


@router.get(
    "/{tenant_id}",
    response_model=TenantResponse,
    responses={
        status.HTTP_404_NOT_FOUND: {"description": "Tenant not found."},
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden for current role."},
    },
)
async def get_tenant_endpoint(
    tenant_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantResponse:
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN:
        tenant = await tenants_repo.find_tenant_by_id(db, tenant_id)
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found.",
            )
        return TenantResponse.from_tenant(tenant)
    if user.kind == KIND_DISPATCHER and user.tenant_id == tenant_id:
        tenant = await tenants_repo.find_tenant_by_id(db, tenant_id)
        if tenant is None:
            # Ungewöhnlicher Pfad: Session sagt Dispatcher dieses Mandanten,
            # aber Tenant-Zeile fehlt — vermutlich gerade gelöscht. 404 ist
            # konsistent zur Plattform-Admin-Sicht.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found.",
            )
        return TenantResponse.from_tenant(tenant)
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden.",
    )


@router.post(
    "/{tenant_id}/approve",
    response_model=TenantResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Tenant not found."}},
)
async def approve_tenant_endpoint(
    tenant_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantResponse:
    _require_platform_admin(request)
    try:
        tenant = await tenants_use_cases.approve_tenant(db, tenant_id)
    except tenants_use_cases.TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        ) from exc
    await db.commit()
    return TenantResponse.from_tenant(tenant)


@router.post(
    "/{tenant_id}/deactivate",
    response_model=TenantResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Tenant not found."}},
)
async def deactivate_tenant_endpoint(
    tenant_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> TenantResponse:
    _require_platform_admin(request)
    try:
        tenant = await tenants_use_cases.deactivate_tenant(db, tenant_id)
    except tenants_use_cases.TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        ) from exc
    await db.commit()
    return TenantResponse.from_tenant(tenant)


@router.post(
    "/{tenant_id}/dispatchers",
    response_model=InviteUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Tenant not found."},
        status.HTTP_409_CONFLICT: {"description": "Username already taken in tenant."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid username."},
    },
)
async def invite_dispatcher_endpoint(
    tenant_id: uuid.UUID,
    payload: InviteUserRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> InviteUserResponse:
    await _require_admin_or_dispatcher_of(request, tenant_id, db)
    try:
        result = await tenants_use_cases.invite_dispatcher(
            db,
            tenant_id=tenant_id,
            username=payload.username,
            email=str(payload.email) if payload.email else None,
            secret=settings.secret_key.get_secret_value(),
        )
    except tenants_use_cases.TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        ) from exc
    except tenants_use_cases.TenantNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant is not active (status={exc.status!r}).",
        ) from exc
    except tenants_repo.UsernameTakenInTenantError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken in this tenant.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    await db.commit()
    return InviteUserResponse(
        user_id=str(result.user_id),
        reset_token=result.reset_token,
        expires_in_seconds=result.expires_in_seconds,
    )


@router.post(
    "/{tenant_id}/carers",
    response_model=InviteUserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Tenant not found."},
        status.HTTP_409_CONFLICT: {"description": "Username already taken in tenant."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid username."},
    },
)
async def invite_carer_endpoint(
    tenant_id: uuid.UUID,
    payload: InviteUserRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> InviteUserResponse:
    await _require_admin_or_dispatcher_of(request, tenant_id, db)
    try:
        result = await tenants_use_cases.invite_carer(
            db,
            tenant_id=tenant_id,
            username=payload.username,
            email=str(payload.email) if payload.email else None,
            secret=settings.secret_key.get_secret_value(),
        )
    except tenants_use_cases.TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found.",
        ) from exc
    except tenants_use_cases.TenantNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant is not active (status={exc.status!r}).",
        ) from exc
    except tenants_repo.UsernameTakenInTenantError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken in this tenant.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    await db.commit()
    return InviteUserResponse(
        user_id=str(result.user_id),
        reset_token=result.reset_token,
        expires_in_seconds=result.expires_in_seconds,
    )


__all__ = [
    "InviteUserRequest",
    "InviteUserResponse",
    "TenantResponse",
    "router",
]
