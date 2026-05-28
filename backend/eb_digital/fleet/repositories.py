"""Async-Repositories für ``backend/fleet`` (Phase 4 Schritt 4.2).

Funktions-basiertes Layout analog zu ``backend/catalog.repositories``.

Repository-Bereiche:

  • ``Vehicle`` — CRUD plus Mode-Wechsel.
  • ``TenantHeadOffice`` — Upsert plus Lookup.
  • ``VehicleLoadout`` + ``VehicleLoadoutItem`` — atomares Replace mit
    Snapshot-Kopie in die History-Tabelle.
  • ``VehicleLoadoutHistory`` — paginierte Listen-Abfrage.

DB-Constraint-Verstöße werden hier gefangen und auf Domain-Exceptions
gemappt, die der Use-Case auf API-Status-Codes mappt.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.fleet.models import (
    SUPPLY_MODE_OFF,
    VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    TenantHeadOffice,
    Vehicle,
    VehicleLoadout,
    VehicleLoadoutHistory,
    VehicleLoadoutItem,
)

# ─── Vehicle-Repository ──────────────────────────────────────────────────────


async def create_vehicle(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    type_: str,
    name: str,
    license_plate: str | None = None,
    capacity_label: str | None = None,
) -> Vehicle:
    """Legt ein Fahrzeug an.

    Für Supply-Transporter wird ``mode`` automatisch auf ``off`` gesetzt;
    für reguläre Fahrzeuge bleibt ``mode`` NULL (DB-CHECK ``type_mode_constraint``).
    """
    initial_mode = SUPPLY_MODE_OFF if type_ == VEHICLE_TYPE_SUPPLY_TRANSPORTER else None
    vehicle = Vehicle(
        tenant_id=tenant_id,
        type=type_,
        mode=initial_mode,
        name=name,
        license_plate=license_plate,
        capacity_label=capacity_label,
        is_active=True,
    )
    session.add(vehicle)
    await session.flush()
    return vehicle


async def find_vehicle_by_id(
    session: AsyncSession,
    vehicle_id: uuid.UUID,
) -> Vehicle | None:
    return (
        await session.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    ).scalar_one_or_none()


async def list_vehicles_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
    *,
    include_inactive: bool = False,
) -> list[Vehicle]:
    """Fahrzeuge eines Tenants, alphabetisch nach Name.

    ``include_inactive=False`` (Default) versteckt Soft-Delete-Einträge.
    """
    stmt = select(Vehicle).where(Vehicle.tenant_id == tenant_id).order_by(Vehicle.name.asc())
    if not include_inactive:
        stmt = stmt.where(Vehicle.is_active.is_(True))
    return list((await session.execute(stmt)).scalars().all())


async def update_vehicle_stammdaten(
    session: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
    name: str | None = None,
    license_plate: str | None = None,
    capacity_label: str | None = None,
) -> Vehicle | None:
    """PATCH-Semantik für Stammdaten. ``None`` heißt „nicht ändern".

    Typ-Wechsel (``type``) ist hier bewusst nicht erlaubt — der Use-Case
    weist Anfragen ab, bevor sie ins Repository gelangen.
    """
    vehicle = await find_vehicle_by_id(session, vehicle_id)
    if vehicle is None:
        return None
    if name is not None:
        vehicle.name = name
    if license_plate is not None:
        vehicle.license_plate = license_plate
    if capacity_label is not None:
        vehicle.capacity_label = capacity_label
    await session.flush()
    return vehicle


async def deactivate_vehicle(
    session: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
) -> Vehicle | None:
    """Soft-Delete via ``is_active=FALSE``."""
    vehicle = await find_vehicle_by_id(session, vehicle_id)
    if vehicle is None:
        return None
    vehicle.is_active = False
    await session.flush()
    return vehicle


async def set_vehicle_mode(
    session: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
    mode: str,
) -> Vehicle | None:
    """Setzt ``vehicle.mode``. Der Use-Case prüft vorher den Typ."""
    vehicle = await find_vehicle_by_id(session, vehicle_id)
    if vehicle is None:
        return None
    vehicle.mode = mode
    await session.flush()
    return vehicle


# ─── HeadOffice-Repository ──────────────────────────────────────────────────


async def upsert_head_office(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    lat: float,
    lng: float,
    label: str | None = None,
) -> TenantHeadOffice:
    """Upsert für 1:1-Geschäftsstelle (Tenant-PK)."""
    head_office = (
        await session.execute(
            select(TenantHeadOffice).where(TenantHeadOffice.tenant_id == tenant_id)
        )
    ).scalar_one_or_none()
    if head_office is None:
        head_office = TenantHeadOffice(
            tenant_id=tenant_id,
            lat=lat,
            lng=lng,
            label=label,
        )
        session.add(head_office)
    else:
        head_office.lat = lat
        head_office.lng = lng
        head_office.label = label
    await session.flush()
    return head_office


async def find_head_office_by_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> TenantHeadOffice | None:
    return (
        await session.execute(
            select(TenantHeadOffice).where(TenantHeadOffice.tenant_id == tenant_id)
        )
    ).scalar_one_or_none()


# ─── Loadout-Repository ─────────────────────────────────────────────────────


async def find_current_loadout(
    session: AsyncSession,
    vehicle_id: uuid.UUID,
) -> VehicleLoadout | None:
    """Aktueller Loadout-Snapshot eines Fahrzeugs (oder ``None``)."""
    return (
        await session.execute(select(VehicleLoadout).where(VehicleLoadout.vehicle_id == vehicle_id))
    ).scalar_one_or_none()


async def list_loadout_items(
    session: AsyncSession,
    loadout_id: uuid.UUID,
) -> list[VehicleLoadoutItem]:
    """Alle Items eines Loadout, in Insert-Reihenfolge (``created_at`` ASC)."""
    stmt = (
        select(VehicleLoadoutItem)
        .where(VehicleLoadoutItem.loadout_id == loadout_id)
        .order_by(VehicleLoadoutItem.created_at.asc(), VehicleLoadoutItem.id.asc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def replace_loadout(
    session: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    items: list[tuple[uuid.UUID | None, uuid.UUID | None, int]],
    history_snapshot_items: list[dict[str, str | int]] | None,
) -> VehicleLoadout:
    """Ersetzt den Loadout-Snapshot eines Fahrzeugs atomar.

    Reihenfolge im Use-Case:

      1. Vorherigen Snapshot lesen (falls vorhanden) und seinen Frozen-
         Items-Stand in ``history_snapshot_items`` aufgelöst übergeben.
      2. Diese Funktion ruft ``append_history`` für den alten Stand auf,
         löscht den alten Loadout (CASCADE räumt Items), legt den neuen
         Loadout an und fügt die neuen Items hinzu.
      3. Alles in einer Transaktion — gemeinsamer ``session.flush()``
         am Ende sorgt für Atomizität gegenüber Rollback.

    Items sind 3-Tupel ``(base_item_id|None, tenant_extension_id|None, quantity)``
    — die Use-Case-Schicht hat die Catalog-Refs bereits validiert.
    """
    now = datetime.now(UTC)

    # 1) Alten Snapshot in History sichern (falls History-Items vorliegen).
    existing = await find_current_loadout(session, vehicle_id)
    if existing is not None and history_snapshot_items is not None:
        session.add(
            VehicleLoadoutHistory(
                vehicle_id=vehicle_id,
                recorded_at=existing.recorded_at,
                recorded_by_dispatcher_id=existing.recorded_by_dispatcher_id,
                items=history_snapshot_items,
                created_at=now,
            )
        )

    # 2) Alten Loadout löschen (CASCADE räumt Items mit).
    if existing is not None:
        await session.execute(delete(VehicleLoadout).where(VehicleLoadout.id == existing.id))

    # 3) Neuen Loadout anlegen.
    loadout = VehicleLoadout(
        vehicle_id=vehicle_id,
        recorded_at=now,
        recorded_by_dispatcher_id=dispatcher_id,
    )
    session.add(loadout)
    await session.flush()

    # 4) Neue Items anhängen.
    for base_id, ext_id, qty in items:
        session.add(
            VehicleLoadoutItem(
                loadout_id=loadout.id,
                base_item_id=base_id,
                tenant_extension_id=ext_id,
                quantity=qty,
                created_at=now,
            )
        )
    await session.flush()

    return loadout


async def list_loadout_history(
    session: AsyncSession,
    vehicle_id: uuid.UUID,
    *,
    limit: int = 50,
) -> list[VehicleLoadoutHistory]:
    """Letzte ``limit`` History-Snapshots eines Fahrzeugs, neueste zuerst."""
    stmt = (
        select(VehicleLoadoutHistory)
        .where(VehicleLoadoutHistory.vehicle_id == vehicle_id)
        .order_by(VehicleLoadoutHistory.recorded_at.desc())
        .limit(limit)
    )
    return list((await session.execute(stmt)).scalars().all())


__all__ = [
    "create_vehicle",
    "deactivate_vehicle",
    "find_current_loadout",
    "find_head_office_by_tenant",
    "find_vehicle_by_id",
    "list_loadout_history",
    "list_loadout_items",
    "list_vehicles_for_tenant",
    "replace_loadout",
    "set_vehicle_mode",
    "update_vehicle_stammdaten",
    "upsert_head_office",
]
