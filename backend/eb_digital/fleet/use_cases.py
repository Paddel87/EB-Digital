"""Use-Case-Schicht für ``backend/fleet`` (Phase 4 Schritt 4.2).

Dünne Orchestrierungs-Schicht über den Repositories. Validierung von
Vorbedingungen (Tenant aktiv, Vehicle existiert, Mode-Wechsel nur für
Supply-Transporter, Catalog-Refs gültig, Tenant-Extension gehört zum
Vehicle-Tenant) und Mapping auf Domain-Exceptions. Berechtigungs-Checks
(Disponent eigener Tenant / Plattform-Admin / Carer) liegen in der
API-Schicht.

**Phase-4.2-Sonderfall:** ``update_supply_transporter_mode`` schreibt
**kein** Audit-Log (Detail-Plan-Freigabe 3B). Die ADR-008/Regel-011-
Audit-Pflicht für Mode-Wechsel wird in Phase 4.3 durch
``backend/operations.SwitchSupplyTransporterMode`` umhüllt — der dortige
Use-Case wird das Fleet-Use-Case aufrufen und das Audit-Log dazu schreiben.
"""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.catalog import repositories as catalog_repo
from eb_digital.fleet import repositories as fleet_repo
from eb_digital.fleet.models import (
    SUPPLY_MODE_OFF,
    VEHICLE_TYPE_REGULAR,
    VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    TenantHeadOffice,
    Vehicle,
    VehicleLoadout,
    VehicleLoadoutHistory,
)
from eb_digital.tenants.models import TENANT_STATUS_ACTIVE
from eb_digital.tenants.repositories import find_tenant_by_id
from eb_digital.tenants.use_cases import TenantNotActiveError, TenantNotFoundError

# ─── Domain-Exceptions ───────────────────────────────────────────────────────


class VehicleNotFoundError(Exception):
    """Fahrzeug mit angegebener ID existiert nicht."""

    def __init__(self, vehicle_id: uuid.UUID) -> None:
        super().__init__(f"Vehicle not found: {vehicle_id}")
        self.vehicle_id = vehicle_id


class VehicleNotSupplyTransporterError(Exception):
    """Mode-Operation auf einem regulären Fahrzeug versucht."""

    def __init__(self, vehicle_id: uuid.UUID) -> None:
        super().__init__(
            f"Vehicle {vehicle_id} is not a supply_transporter; mode operations are not allowed."
        )
        self.vehicle_id = vehicle_id


class VehicleTypeChangeNotAllowedError(Exception):
    """``type``-Wechsel ist verboten — Anlage des Fahrzeugs bestimmt den Typ."""

    def __init__(self, vehicle_id: uuid.UUID) -> None:
        super().__init__(f"Vehicle {vehicle_id} type cannot be changed after creation.")
        self.vehicle_id = vehicle_id


class CatalogItemNotAvailableError(Exception):
    """Referenziertes Catalog-Item existiert nicht oder ist deaktiviert.

    Greift sowohl für ``base_item_id`` (deaktiviert via ``is_active=FALSE``)
    als auch für ``tenant_extension_id`` (deaktiviert via
    ``is_disabled=TRUE``).
    """

    def __init__(self, *, kind: str, ref_id: uuid.UUID) -> None:
        super().__init__(f"Catalog {kind} not available: {ref_id}")
        self.kind = kind
        self.ref_id = ref_id


class CrossTenantExtensionError(Exception):
    """Tenant-Extension gehört zu einem anderen Tenant als das Vehicle."""

    def __init__(
        self, *, extension_id: uuid.UUID, vehicle_tenant: uuid.UUID, extension_tenant: uuid.UUID
    ) -> None:
        super().__init__(
            f"Extension {extension_id} belongs to tenant {extension_tenant}, "
            f"vehicle tenant is {vehicle_tenant}."
        )
        self.extension_id = extension_id
        self.vehicle_tenant = vehicle_tenant
        self.extension_tenant = extension_tenant


class HeadOfficeNotFoundError(Exception):
    """Kein HeadOffice für den angegebenen Tenant gesetzt."""

    def __init__(self, tenant_id: uuid.UUID) -> None:
        super().__init__(f"Head office not found for tenant: {tenant_id}")
        self.tenant_id = tenant_id


# ─── Helpers ────────────────────────────────────────────────────────────────


async def _require_tenant_active(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    tenant = await find_tenant_by_id(session, tenant_id)
    if tenant is None:
        raise TenantNotFoundError(tenant_id)
    if tenant.status != TENANT_STATUS_ACTIVE:
        raise TenantNotActiveError(tenant_id=tenant_id, status=tenant.status)


# ─── Vehicle Use-Cases ─────────────────────────────────────────────────────


async def create_vehicle(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    type_: str,
    name: str,
    license_plate: str | None = None,
    capacity_label: str | None = None,
) -> Vehicle:
    """Legt ein Fahrzeug an. Vorbedingung: Tenant aktiv.

    Für Supply-Transporter wird ``mode='off'`` als Default gesetzt
    (Detail-Plan 2A); reguläre Fahrzeuge haben ``mode=NULL``.
    """
    await _require_tenant_active(session, tenant_id)
    return await fleet_repo.create_vehicle(
        session,
        tenant_id=tenant_id,
        type_=type_,
        name=name,
        license_plate=license_plate,
        capacity_label=capacity_label,
    )


async def update_vehicle_stammdaten(
    session: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
    name: str | None = None,
    license_plate: str | None = None,
    capacity_label: str | None = None,
) -> Vehicle:
    """PATCH-Semantik für Vehicle-Stammdaten.

    ``None``-Felder bleiben unverändert. ``type`` ist nicht im Schema, weil
    Typ-Wechsel verboten ist (``VehicleTypeChangeNotAllowedError`` greift
    nicht, da das Schema ``type`` schon nicht akzeptiert).
    """
    vehicle = await fleet_repo.update_vehicle_stammdaten(
        session,
        vehicle_id=vehicle_id,
        name=name,
        license_plate=license_plate,
        capacity_label=capacity_label,
    )
    if vehicle is None:
        raise VehicleNotFoundError(vehicle_id)
    return vehicle


async def deactivate_vehicle(
    session: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
) -> Vehicle:
    """Soft-Delete via ``is_active=FALSE``."""
    vehicle = await fleet_repo.deactivate_vehicle(session, vehicle_id=vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(vehicle_id)
    return vehicle


async def update_supply_transporter_mode(
    session: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
    mode: str,
) -> Vehicle:
    """Setzt den Versorgungs-Transporter-Modus.

    Vorbedingungen: Vehicle existiert, ``type='supply_transporter'``. Bei
    regulärem Fahrzeug → ``VehicleNotSupplyTransporterError``.

    **Kein Audit-Log in 4.2** (Detail-Plan 3B). Audit-Pflicht aus
    ADR-008/Regel-011 wird in 4.3 durch
    ``backend/operations.SwitchSupplyTransporterMode``-Umhüllung erfüllt.
    """
    vehicle = await fleet_repo.find_vehicle_by_id(session, vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(vehicle_id)
    if vehicle.type != VEHICLE_TYPE_SUPPLY_TRANSPORTER:
        raise VehicleNotSupplyTransporterError(vehicle_id)
    updated = await fleet_repo.set_vehicle_mode(session, vehicle_id=vehicle_id, mode=mode)
    # ``set_vehicle_mode`` kann theoretisch ``None`` liefern (race condition),
    # aber wir haben gerade gelesen — Defense-in-Depth, kein realistischer Pfad.
    if updated is None:
        raise VehicleNotFoundError(vehicle_id)
    return updated


# ─── HeadOffice Use-Cases ──────────────────────────────────────────────────


async def set_head_office(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    lat: float,
    lng: float,
    label: str | None = None,
) -> TenantHeadOffice:
    """Upsert für die Geschäftsstelle eines Tenants. Vorbedingung: Tenant aktiv."""
    await _require_tenant_active(session, tenant_id)
    return await fleet_repo.upsert_head_office(
        session,
        tenant_id=tenant_id,
        lat=lat,
        lng=lng,
        label=label,
    )


async def get_head_office(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> TenantHeadOffice:
    """Liest die Geschäftsstelle eines Tenants. ``HeadOfficeNotFoundError`` wenn nicht gesetzt."""
    head_office = await fleet_repo.find_head_office_by_tenant(session, tenant_id)
    if head_office is None:
        raise HeadOfficeNotFoundError(tenant_id)
    return head_office


# ─── Loadout Use-Cases ─────────────────────────────────────────────────────


async def _validate_loadout_items(
    session: AsyncSession,
    *,
    vehicle_tenant_id: uuid.UUID,
    items: list[tuple[uuid.UUID | None, uuid.UUID | None, int]],
) -> None:
    """Prüft alle Item-Refs auf Existenz, Aktivität und Tenant-Bindung.

    Wirft die erste gefundene Verletzung — kein Bulk-Result, weil die
    Frontend-UX einzelne Items behebt. Reihenfolge:

      1. ``base_item_id`` → existiert + ``is_active=TRUE``.
      2. ``tenant_extension_id`` → existiert + ``is_disabled=FALSE``
         + ``tenant_id == vehicle_tenant_id``.
    """
    for base_id, ext_id, _qty in items:
        if base_id is not None:
            base_item = await catalog_repo.find_base_item_by_id(session, base_id)
            if base_item is None or not base_item.is_active:
                raise CatalogItemNotAvailableError(kind="base", ref_id=base_id)
        elif ext_id is not None:
            # ``LoadoutItemInput``-Schema garantiert XOR: hier ist ext_id non-None.
            ext = await catalog_repo.find_extension_by_id(session, ext_id)
            if ext is None or ext.is_disabled:
                raise CatalogItemNotAvailableError(kind="extension", ref_id=ext_id)
            if ext.tenant_id != vehicle_tenant_id:
                raise CrossTenantExtensionError(
                    extension_id=ext_id,
                    vehicle_tenant=vehicle_tenant_id,
                    extension_tenant=ext.tenant_id,
                )


async def _freeze_existing_loadout(
    session: AsyncSession,
    loadout: VehicleLoadout,
) -> list[dict[str, str | int]]:
    """Baut den Frozen-JSONB-Snapshot des aktuellen Loadouts für die History-Tabelle.

    Auflösung über Catalog-Refs: pro Item ``ref_kind`` (``base|extension``),
    ``ref_id``, ``quantity``, plus ``name_at_snapshot``/``unit_at_snapshot``
    als Klartext-Felder, damit die History interpretierbar bleibt, auch
    wenn das Catalog-Item später deaktiviert oder umbenannt wird.
    """
    items = await fleet_repo.list_loadout_items(session, loadout.id)
    frozen: list[dict[str, str | int]] = []
    for item in items:
        if item.base_item_id is not None:
            base = await catalog_repo.find_base_item_by_id(session, item.base_item_id)
            name = base.name if base is not None else "<deleted>"
            unit = base.default_unit_label if base is not None else "<deleted>"
            frozen.append(
                {
                    "ref_kind": "base",
                    "ref_id": str(item.base_item_id),
                    "quantity": item.quantity,
                    "name_at_snapshot": name,
                    "unit_at_snapshot": unit,
                }
            )
        elif item.tenant_extension_id is not None:
            # DB-CHECK ``exactly_one_ref`` garantiert XOR — wir landen hier nur,
            # wenn ``tenant_extension_id`` gesetzt ist.
            ext = await catalog_repo.find_extension_by_id(session, item.tenant_extension_id)
            # Override-Felder priorisieren, sonst eigenständige Felder.
            if ext is None:
                name = "<deleted>"
                unit = "<deleted>"
            elif ext.override_name is not None:
                name = ext.override_name
                unit = ext.override_unit_label or "<unset>"
            elif ext.name is not None:
                name = ext.name
                unit = ext.default_unit_label or "<unset>"
            else:
                name = "<unknown>"
                unit = "<unknown>"
            frozen.append(
                {
                    "ref_kind": "extension",
                    "ref_id": str(item.tenant_extension_id),
                    "quantity": item.quantity,
                    "name_at_snapshot": name,
                    "unit_at_snapshot": unit,
                }
            )
    return frozen


async def set_loadout(
    session: AsyncSession,
    *,
    vehicle_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    items: list[tuple[uuid.UUID | None, uuid.UUID | None, int]],
) -> VehicleLoadout:
    """Setzt die Beladung eines Fahrzeugs atomar.

    Reihenfolge:

      1. Vehicle existiert.
      2. Catalog-Refs validieren (existieren, aktiv, Tenant-Bindung).
      3. Aktuellen Snapshot Frozen-JSONB-serialisieren.
      4. Repository macht ``replace_loadout`` (History-Append + Delete +
         Insert + Items).
    """
    vehicle = await fleet_repo.find_vehicle_by_id(session, vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(vehicle_id)
    await _validate_loadout_items(
        session,
        vehicle_tenant_id=vehicle.tenant_id,
        items=items,
    )
    existing = await fleet_repo.find_current_loadout(session, vehicle_id)
    history_snapshot = (
        await _freeze_existing_loadout(session, existing) if existing is not None else None
    )
    return await fleet_repo.replace_loadout(
        session,
        vehicle_id=vehicle_id,
        dispatcher_id=dispatcher_id,
        items=items,
        history_snapshot_items=history_snapshot,
    )


async def get_current_loadout(
    session: AsyncSession,
    vehicle_id: uuid.UUID,
) -> tuple[VehicleLoadout | None, list[tuple[uuid.UUID, uuid.UUID | None, uuid.UUID | None, int]]]:
    """Liest den aktuellen Loadout eines Fahrzeugs + seine Items.

    Liefert ``(None, [])`` wenn noch kein Loadout existiert.

    Items werden als ``(item_id, base_item_id|None, tenant_extension_id|None, quantity)``-
    Tupel zurückgegeben — die API-Schicht baut daraus das Output-Schema.
    """
    loadout = await fleet_repo.find_current_loadout(session, vehicle_id)
    if loadout is None:
        return (None, [])
    items = await fleet_repo.list_loadout_items(session, loadout.id)
    return (
        loadout,
        [(it.id, it.base_item_id, it.tenant_extension_id, it.quantity) for it in items],
    )


async def get_loadout_history(
    session: AsyncSession,
    vehicle_id: uuid.UUID,
    *,
    limit: int = 50,
) -> list[VehicleLoadoutHistory]:
    """Liest die ``limit`` neuesten History-Einträge eines Fahrzeugs."""
    return await fleet_repo.list_loadout_history(session, vehicle_id, limit=limit)


# Re-exports für API/Test-Schicht.
__all__ = [
    "SUPPLY_MODE_OFF",
    "VEHICLE_TYPE_REGULAR",
    "VEHICLE_TYPE_SUPPLY_TRANSPORTER",
    "CatalogItemNotAvailableError",
    "CrossTenantExtensionError",
    "HeadOfficeNotFoundError",
    "VehicleNotFoundError",
    "VehicleNotSupplyTransporterError",
    "VehicleTypeChangeNotAllowedError",
    "create_vehicle",
    "deactivate_vehicle",
    "get_current_loadout",
    "get_head_office",
    "get_loadout_history",
    "set_head_office",
    "set_loadout",
    "update_supply_transporter_mode",
    "update_vehicle_stammdaten",
]
