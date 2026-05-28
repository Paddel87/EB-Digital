"""FastAPI-Router für ``backend/fleet`` unter ``/api/fleet`` (Phase 4 Schritt 4.2).

Rollen-Matrix (Detail-Plan-Freigabe 7A):

  • **Disponent** — R/W auf Vehicles, Mode, Loadout, HeadOffice, History
    **nur** für den eigenen Mandanten (Regel-014, Cross-Tenant verboten).
  • **Plattform-Admin** — R-only über alle Tenants. ``?tenant_id=<uuid>``
    ist Pflicht für Listen-Endpunkte; Detail-Endpunkte funktionieren über
    die Vehicle-ID direkt. **Kein** Schreib-Zugriff (Detail-Plan 7A; PA-
    Wartung ist nicht im Phase-4.2-Scope, vgl. Catalog-Linie aus 4.1).
  • **Carer** — R-only auf ``/vehicles`` und ``/vehicles/{id}/loadout``
    für eigenen Tenant. Keine History (interne Disponenten-Sache).
  • **Anon** — 403 auf allen Pfaden.

Berechtigungs-Helper sind die in ``backend/catalog.api`` etablierten:
``_require_session``, ``_require_dispatcher_with_tenant``,
``_require_carer_or_dispatcher`` — funktionell identisch, hier eigene
Kopien für Modul-Isolation (Catalog importiert sie nicht öffentlich).
"""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.api import get_db_session
from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
)
from eb_digital.auth.sessions import SessionUser, get_current_session_user
from eb_digital.fleet import repositories as fleet_repo
from eb_digital.fleet import use_cases as fleet_use_cases
from eb_digital.fleet.models import (
    TenantHeadOffice,
    Vehicle,
    VehicleLoadout,
    VehicleLoadoutHistory,
    VehicleLoadoutItem,
)
from eb_digital.fleet.schemas import (
    HeadOfficeOut,
    HeadOfficeUpsert,
    LoadoutHistoryEntryOut,
    LoadoutHistoryOut,
    LoadoutItemOut,
    LoadoutOut,
    LoadoutUpsert,
    VehicleCreate,
    VehicleModeUpdate,
    VehicleOut,
    VehicleUpdate,
)
from eb_digital.tenants.use_cases import TenantNotActiveError, TenantNotFoundError

# ─── Berechtigungs-Helper ────────────────────────────────────────────────────


def _require_session(request: Request) -> SessionUser:
    user = get_current_session_user(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return user


def _require_dispatcher_with_tenant(request: Request) -> tuple[SessionUser, uuid.UUID]:
    user = _require_session(request)
    if user.kind != KIND_DISPATCHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispatcher role required.",
        )
    if user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispatcher session is missing tenant binding.",
        )
    return user, user.tenant_id


def _require_read_access_for_vehicle(
    request: Request,
    vehicle: Vehicle,
) -> SessionUser:
    """Read-Zugriff auf ein konkretes Vehicle.

    Erlaubt: Plattform-Admin (jedes Vehicle), Dispatcher oder Carer des
    Tenant-Owners. Sonst 403.
    """
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN:
        return user
    if user.kind in (KIND_DISPATCHER, KIND_CARER) and user.tenant_id == vehicle.tenant_id:
        return user
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Forbidden.",
    )


def _require_dispatcher_of_vehicle(
    request: Request,
    vehicle: Vehicle,
) -> tuple[SessionUser, uuid.UUID]:
    """Schreib-Zugriff auf ein konkretes Vehicle — nur Dispatcher des Tenants.

    Plattform-Admin hat **kein** Schreib-Recht in 4.2 (Detail-Plan 7A).
    """
    user, tenant_id = _require_dispatcher_with_tenant(request)
    if tenant_id != vehicle.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden.",
        )
    return user, tenant_id


# ─── Response-Builder ───────────────────────────────────────────────────────


def _vehicle_to_out(v: Vehicle) -> VehicleOut:
    return VehicleOut.model_validate(v)


def _head_office_to_out(h: TenantHeadOffice) -> HeadOfficeOut:
    return HeadOfficeOut.model_validate(h)


def _loadout_to_out(
    loadout: VehicleLoadout,
    items: list[VehicleLoadoutItem],
) -> LoadoutOut:
    return LoadoutOut(
        id=loadout.id,
        vehicle_id=loadout.vehicle_id,
        recorded_at=loadout.recorded_at,
        recorded_by_dispatcher_id=loadout.recorded_by_dispatcher_id,
        items=[LoadoutItemOut.model_validate(i) for i in items],
    )


def _history_entry_to_out(h: VehicleLoadoutHistory) -> LoadoutHistoryEntryOut:
    return LoadoutHistoryEntryOut(
        id=h.id,
        vehicle_id=h.vehicle_id,
        recorded_at=h.recorded_at,
        recorded_by_dispatcher_id=h.recorded_by_dispatcher_id,
        items=h.items,
    )


# ─── Router ─────────────────────────────────────────────────────────────────


router = APIRouter(prefix="/fleet", tags=["fleet"])


# Vehicle CRUD ─────────────────────────────────────────────────────────────


@router.post(
    "/vehicles",
    response_model=VehicleOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_409_CONFLICT: {"description": "Tenant not active."},
    },
)
async def create_vehicle_endpoint(
    payload: VehicleCreate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> VehicleOut:
    _, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        vehicle = await fleet_use_cases.create_vehicle(
            db,
            tenant_id=tenant_id,
            type_=payload.type,
            name=payload.name,
            license_plate=payload.license_plate,
            capacity_label=payload.capacity_label,
        )
    except TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found."
        ) from exc
    except TenantNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant is not active (status={exc.status!r}).",
        ) from exc
    await db.commit()
    return _vehicle_to_out(vehicle)


@router.get(
    "/vehicles",
    response_model=list[VehicleOut],
    responses={status.HTTP_403_FORBIDDEN: {"description": "Forbidden."}},
)
async def list_vehicles_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    tenant_id: Annotated[uuid.UUID | None, Query()] = None,
    include_inactive: Annotated[bool, Query()] = False,
) -> list[VehicleOut]:
    """Listet Fahrzeuge.

    Plattform-Admin: ``?tenant_id=`` Pflicht. Disponent/Carer: eigener
    Tenant (Query-Parameter wird ignoriert).
    """
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN:
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Platform admin must specify ?tenant_id=…",
            )
        effective_tenant = tenant_id
        effective_include_inactive = include_inactive
    elif user.kind in (KIND_DISPATCHER, KIND_CARER) and user.tenant_id is not None:
        effective_tenant = user.tenant_id
        # ``include_inactive`` für Disponent erlaubt (Wartung); für Carer
        # bewusst auf False geclamped — Carer sieht nur aktive Fahrzeuge.
        effective_include_inactive = include_inactive if user.kind == KIND_DISPATCHER else False
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    vehicles = await fleet_repo.list_vehicles_for_tenant(
        db,
        effective_tenant,
        include_inactive=effective_include_inactive,
    )
    return [_vehicle_to_out(v) for v in vehicles]


@router.get(
    "/vehicles/{vehicle_id}",
    response_model=VehicleOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
    },
)
async def get_vehicle_endpoint(
    vehicle_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> VehicleOut:
    vehicle = await fleet_repo.find_vehicle_by_id(db, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    _require_read_access_for_vehicle(request, vehicle)
    return _vehicle_to_out(vehicle)


@router.patch(
    "/vehicles/{vehicle_id}",
    response_model=VehicleOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
    },
)
async def update_vehicle_endpoint(
    vehicle_id: uuid.UUID,
    payload: VehicleUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> VehicleOut:
    vehicle = await fleet_repo.find_vehicle_by_id(db, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    _require_dispatcher_of_vehicle(request, vehicle)
    updated = await fleet_use_cases.update_vehicle_stammdaten(
        db,
        vehicle_id=vehicle_id,
        name=payload.name,
        license_plate=payload.license_plate,
        capacity_label=payload.capacity_label,
    )
    await db.commit()
    return _vehicle_to_out(updated)


@router.delete(
    "/vehicles/{vehicle_id}",
    response_model=VehicleOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
    },
)
async def deactivate_vehicle_endpoint(
    vehicle_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> VehicleOut:
    vehicle = await fleet_repo.find_vehicle_by_id(db, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    _require_dispatcher_of_vehicle(request, vehicle)
    deactivated = await fleet_use_cases.deactivate_vehicle(db, vehicle_id=vehicle_id)
    await db.commit()
    return _vehicle_to_out(deactivated)


# Vehicle Mode ──────────────────────────────────────────────────────────────


@router.post(
    "/vehicles/{vehicle_id}/mode",
    response_model=VehicleOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Vehicle is not a supply transporter."
        },
    },
)
async def update_vehicle_mode_endpoint(
    vehicle_id: uuid.UUID,
    payload: VehicleModeUpdate,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> VehicleOut:
    vehicle = await fleet_repo.find_vehicle_by_id(db, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    _require_dispatcher_of_vehicle(request, vehicle)
    try:
        updated = await fleet_use_cases.update_supply_transporter_mode(
            db, vehicle_id=vehicle_id, mode=payload.mode
        )
    except fleet_use_cases.VehicleNotSupplyTransporterError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Vehicle is not a supply transporter; mode operations are not allowed.",
        ) from exc
    await db.commit()
    return _vehicle_to_out(updated)


# Vehicle Loadout ──────────────────────────────────────────────────────────


@router.get(
    "/vehicles/{vehicle_id}/loadout",
    response_model=LoadoutOut | None,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
    },
)
async def get_vehicle_loadout_endpoint(
    vehicle_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoadoutOut | None:
    """Aktueller Loadout-Snapshot. ``null`` wenn noch keiner gesetzt."""
    vehicle = await fleet_repo.find_vehicle_by_id(db, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    _require_read_access_for_vehicle(request, vehicle)
    loadout = await fleet_repo.find_current_loadout(db, vehicle_id)
    if loadout is None:
        return None
    items = await fleet_repo.list_loadout_items(db, loadout.id)
    return _loadout_to_out(loadout, items)


@router.put(
    "/vehicles/{vehicle_id}/loadout",
    response_model=LoadoutOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
        status.HTTP_422_UNPROCESSABLE_CONTENT: {
            "description": "Item ref invalid, deactivated, or cross-tenant."
        },
    },
)
async def set_vehicle_loadout_endpoint(
    vehicle_id: uuid.UUID,
    payload: LoadoutUpsert,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> LoadoutOut:
    """Setzt die Beladung des Fahrzeugs atomar.

    Vorbedingungen: Dispatcher des Tenants, Vehicle existiert, alle
    Catalog-Refs sind aktiv und Tenant-konsistent. Vorheriger Snapshot
    wird automatisch als Frozen JSONB in die History-Tabelle kopiert.
    """
    vehicle = await fleet_repo.find_vehicle_by_id(db, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    user, _tenant_id = _require_dispatcher_of_vehicle(request, vehicle)
    items = [(it.base_item_id, it.tenant_extension_id, it.quantity) for it in payload.items]
    try:
        loadout = await fleet_use_cases.set_loadout(
            db,
            vehicle_id=vehicle_id,
            dispatcher_id=user.id,
            items=items,
        )
    except fleet_use_cases.CatalogItemNotAvailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"Catalog {exc.kind} not available: {exc.ref_id}.",
        ) from exc
    except fleet_use_cases.CrossTenantExtensionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=(
                f"Extension {exc.extension_id} belongs to a different tenant; "
                "cross-tenant extensions are not allowed."
            ),
        ) from exc
    await db.commit()
    items_db = await fleet_repo.list_loadout_items(db, loadout.id)
    return _loadout_to_out(loadout, items_db)


@router.get(
    "/vehicles/{vehicle_id}/loadout/history",
    response_model=LoadoutHistoryOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Vehicle not found."},
    },
)
async def get_vehicle_loadout_history_endpoint(
    vehicle_id: uuid.UUID,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    limit: Annotated[int, Query(ge=1, le=200)] = 50,
) -> LoadoutHistoryOut:
    """History-Liste (neueste zuerst). Dispatcher des Tenants oder Plattform-Admin.

    Carer hat **keinen** Zugriff — History ist interne Disponenten-Sache.
    """
    vehicle = await fleet_repo.find_vehicle_by_id(db, vehicle_id)
    if vehicle is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found.")
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN or (
        user.kind == KIND_DISPATCHER and user.tenant_id == vehicle.tenant_id
    ):
        pass
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    entries = await fleet_repo.list_loadout_history(db, vehicle_id, limit=limit)
    return LoadoutHistoryOut(entries=[_history_entry_to_out(e) for e in entries])


# HeadOffice ──────────────────────────────────────────────────────────────


@router.get(
    "/head-office",
    response_model=HeadOfficeOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_404_NOT_FOUND: {"description": "Head office not set."},
    },
)
async def get_head_office_endpoint(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    tenant_id: Annotated[uuid.UUID | None, Query()] = None,
) -> HeadOfficeOut:
    """Liest HeadOffice. PA: ``?tenant_id=`` Pflicht. Dispatcher: eigener Tenant."""
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN:
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Platform admin must specify ?tenant_id=…",
            )
        effective_tenant = tenant_id
    elif user.kind == KIND_DISPATCHER and user.tenant_id is not None:
        effective_tenant = user.tenant_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    try:
        head_office = await fleet_use_cases.get_head_office(db, effective_tenant)
    except fleet_use_cases.HeadOfficeNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Head office not set."
        ) from exc
    return _head_office_to_out(head_office)


@router.put(
    "/head-office",
    response_model=HeadOfficeOut,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Forbidden."},
        status.HTTP_409_CONFLICT: {"description": "Tenant not active."},
    },
)
async def set_head_office_endpoint(
    payload: Annotated[HeadOfficeUpsert, Body()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> HeadOfficeOut:
    """Upsert HeadOffice für eigenen Tenant. Nur Dispatcher (PA hat in 4.2 keinen Write)."""
    _, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        head_office = await fleet_use_cases.set_head_office(
            db,
            tenant_id=tenant_id,
            lat=payload.lat,
            lng=payload.lng,
            label=payload.label,
        )
    except TenantNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found."
        ) from exc
    except TenantNotActiveError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tenant is not active (status={exc.status!r}).",
        ) from exc
    await db.commit()
    return _head_office_to_out(head_office)


__all__ = ["router"]
