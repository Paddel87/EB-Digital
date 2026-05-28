"""Tests für ``backend/eb_digital/fleet/use_cases``.

Fokus: Vorbedingungs-Prüfungen und Domain-Exception-Mapping. Repository-
Pfade werden gestubbt, weil sie in ``test_fleet_repositories`` separat
abgedeckt sind.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest

from eb_digital.catalog import repositories as catalog_repo
from eb_digital.catalog.models import (
    CatalogItemBase,
    CatalogItemTenantExtension,
)
from eb_digital.fleet import repositories as fleet_repo
from eb_digital.fleet import use_cases as fleet_use_cases
from eb_digital.fleet.models import (
    SUPPLY_MODE_LARGE_ORDER,
    SUPPLY_MODE_OFF,
    VEHICLE_TYPE_REGULAR,
    VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    TenantHeadOffice,
    Vehicle,
    VehicleLoadout,
    VehicleLoadoutItem,
)
from eb_digital.tenants import repositories as tenants_repo
from eb_digital.tenants.models import (
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_APPLIED,
    Tenant,
)
from eb_digital.tenants.use_cases import TenantNotActiveError, TenantNotFoundError


def _make_tenant(*, status: str = TENANT_STATUS_ACTIVE) -> Tenant:
    tenant = Tenant(
        name="DPolG Bremen",
        slug="dpolg-bremen",
        status=status,
    )
    tenant.id = uuid.uuid4()
    tenant.applied_at = datetime.now(UTC)
    tenant.activated_at = datetime.now(UTC) if status == TENANT_STATUS_ACTIVE else None
    tenant.created_at = datetime.now(UTC)
    tenant.updated_at = datetime.now(UTC)
    return tenant


def _make_vehicle(
    *,
    tenant_id: uuid.UUID,
    type_: str = VEHICLE_TYPE_REGULAR,
    mode: str | None = None,
) -> Vehicle:
    v = Vehicle(
        tenant_id=tenant_id,
        type=type_,
        mode=mode,
        name="V",
        is_active=True,
    )
    v.id = uuid.uuid4()
    v.created_at = datetime.now(UTC)
    v.updated_at = datetime.now(UTC)
    return v


def _make_base_item(*, is_active: bool = True) -> CatalogItemBase:
    item = CatalogItemBase(
        name="Wasser",
        unit="liter",
        default_unit_label="Liter",
        category_id=uuid.uuid4(),
        is_active=is_active,
    )
    item.id = uuid.uuid4()
    item.created_at = datetime.now(UTC)
    item.updated_at = datetime.now(UTC)
    return item


def _make_own_ext(
    *,
    tenant_id: uuid.UUID,
    is_disabled: bool = False,
) -> CatalogItemTenantExtension:
    ext = CatalogItemTenantExtension(
        tenant_id=tenant_id,
        base_item_id=None,
        name="Brot",
        unit="piece",
        default_unit_label="Stück",
        category_id=uuid.uuid4(),
        is_disabled=is_disabled,
    )
    ext.id = uuid.uuid4()
    ext.created_at = datetime.now(UTC)
    ext.updated_at = datetime.now(UTC)
    return ext


# ─── create_vehicle ────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_vehicle_requires_active_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inactive_tenant = _make_tenant(status=TENANT_STATUS_APPLIED)

    async def _find_tenant(_db: Any, _tid: uuid.UUID) -> Tenant:
        return inactive_tenant

    monkeypatch.setattr(tenants_repo, "find_tenant_by_id", _find_tenant)
    monkeypatch.setattr(fleet_use_cases, "find_tenant_by_id", _find_tenant)

    with pytest.raises(TenantNotActiveError):
        await fleet_use_cases.create_vehicle(
            None,  # type: ignore[arg-type]
            tenant_id=inactive_tenant.id,
            type_=VEHICLE_TYPE_REGULAR,
            name="X",
        )


@pytest.mark.asyncio
async def test_create_vehicle_raises_when_tenant_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _find_tenant(_db: Any, _tid: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(fleet_use_cases, "find_tenant_by_id", _find_tenant)

    with pytest.raises(TenantNotFoundError):
        await fleet_use_cases.create_vehicle(
            None,  # type: ignore[arg-type]
            tenant_id=uuid.uuid4(),
            type_=VEHICLE_TYPE_REGULAR,
            name="X",
        )


@pytest.mark.asyncio
async def test_create_vehicle_happy_path_delegates_to_repo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant()
    expected = _make_vehicle(tenant_id=tenant.id, type_=VEHICLE_TYPE_SUPPLY_TRANSPORTER, mode="off")

    async def _find_tenant(_db: Any, _tid: uuid.UUID) -> Tenant:
        return tenant

    async def _create(_db: Any, **kw: Any) -> Vehicle:
        del kw
        return expected

    monkeypatch.setattr(fleet_use_cases, "find_tenant_by_id", _find_tenant)
    monkeypatch.setattr(fleet_repo, "create_vehicle", _create)

    result = await fleet_use_cases.create_vehicle(
        None,  # type: ignore[arg-type]
        tenant_id=tenant.id,
        type_=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        name="VT-1",
    )
    assert result is expected


# ─── update_supply_transporter_mode ───────────────────────────────────────


@pytest.mark.asyncio
async def test_update_mode_on_regular_vehicle_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    regular = _make_vehicle(tenant_id=uuid.uuid4(), type_=VEHICLE_TYPE_REGULAR)

    async def _find(_db: Any, _vid: uuid.UUID) -> Vehicle:
        return regular

    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _find)

    with pytest.raises(fleet_use_cases.VehicleNotSupplyTransporterError):
        await fleet_use_cases.update_supply_transporter_mode(
            None,  # type: ignore[arg-type]
            vehicle_id=regular.id,
            mode=SUPPLY_MODE_LARGE_ORDER,
        )


@pytest.mark.asyncio
async def test_update_mode_unknown_vehicle_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _find(_db: Any, _vid: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _find)

    with pytest.raises(fleet_use_cases.VehicleNotFoundError):
        await fleet_use_cases.update_supply_transporter_mode(
            None,  # type: ignore[arg-type]
            vehicle_id=uuid.uuid4(),
            mode=SUPPLY_MODE_LARGE_ORDER,
        )


@pytest.mark.asyncio
async def test_update_mode_supply_transporter_happy_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transporter = _make_vehicle(
        tenant_id=uuid.uuid4(),
        type_=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        mode=SUPPLY_MODE_OFF,
    )

    async def _find(_db: Any, _vid: uuid.UUID) -> Vehicle:
        return transporter

    async def _set(_db: Any, **kw: Any) -> Vehicle:
        transporter.mode = kw["mode"]
        return transporter

    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _find)
    monkeypatch.setattr(fleet_repo, "set_vehicle_mode", _set)

    result = await fleet_use_cases.update_supply_transporter_mode(
        None,  # type: ignore[arg-type]
        vehicle_id=transporter.id,
        mode=SUPPLY_MODE_LARGE_ORDER,
    )
    assert result.mode == SUPPLY_MODE_LARGE_ORDER


# ─── set_loadout ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_loadout_rejects_inactive_base_item(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vehicle = _make_vehicle(tenant_id=uuid.uuid4())
    inactive_base = _make_base_item(is_active=False)

    async def _find_v(_db: Any, _vid: uuid.UUID) -> Vehicle:
        return vehicle

    async def _find_base(_db: Any, _bid: uuid.UUID) -> CatalogItemBase:
        return inactive_base

    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _find_v)
    monkeypatch.setattr(catalog_repo, "find_base_item_by_id", _find_base)

    with pytest.raises(fleet_use_cases.CatalogItemNotAvailableError) as exc:
        await fleet_use_cases.set_loadout(
            None,  # type: ignore[arg-type]
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            items=[(inactive_base.id, None, 1)],
        )
    assert exc.value.kind == "base"
    assert exc.value.ref_id == inactive_base.id


@pytest.mark.asyncio
async def test_set_loadout_rejects_cross_tenant_extension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vehicle_tenant = uuid.uuid4()
    other_tenant = uuid.uuid4()
    vehicle = _make_vehicle(tenant_id=vehicle_tenant)
    ext = _make_own_ext(tenant_id=other_tenant)

    async def _find_v(_db: Any, _vid: uuid.UUID) -> Vehicle:
        return vehicle

    async def _find_ext(_db: Any, _eid: uuid.UUID) -> CatalogItemTenantExtension:
        return ext

    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _find_v)
    monkeypatch.setattr(catalog_repo, "find_extension_by_id", _find_ext)

    with pytest.raises(fleet_use_cases.CrossTenantExtensionError) as exc:
        await fleet_use_cases.set_loadout(
            None,  # type: ignore[arg-type]
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            items=[(None, ext.id, 2)],
        )
    assert exc.value.extension_id == ext.id
    assert exc.value.vehicle_tenant == vehicle_tenant
    assert exc.value.extension_tenant == other_tenant


@pytest.mark.asyncio
async def test_set_loadout_rejects_disabled_extension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    vehicle_tenant = uuid.uuid4()
    vehicle = _make_vehicle(tenant_id=vehicle_tenant)
    disabled_ext = _make_own_ext(tenant_id=vehicle_tenant, is_disabled=True)

    async def _find_v(_db: Any, _vid: uuid.UUID) -> Vehicle:
        return vehicle

    async def _find_ext(_db: Any, _eid: uuid.UUID) -> CatalogItemTenantExtension:
        return disabled_ext

    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _find_v)
    monkeypatch.setattr(catalog_repo, "find_extension_by_id", _find_ext)

    with pytest.raises(fleet_use_cases.CatalogItemNotAvailableError) as exc:
        await fleet_use_cases.set_loadout(
            None,  # type: ignore[arg-type]
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            items=[(None, disabled_ext.id, 1)],
        )
    assert exc.value.kind == "extension"


@pytest.mark.asyncio
async def test_set_loadout_happy_path_first_snapshot(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Erstes Laden ohne existierenden Snapshot → keine History-Kopie."""
    vehicle = _make_vehicle(tenant_id=uuid.uuid4())
    base = _make_base_item(is_active=True)

    async def _find_v(_db: Any, _vid: uuid.UUID) -> Vehicle:
        return vehicle

    async def _find_base(_db: Any, _bid: uuid.UUID) -> CatalogItemBase:
        return base

    async def _find_current_loadout(_db: Any, _vid: uuid.UUID) -> None:
        return None

    seen_history: dict[str, Any] = {}

    async def _replace(_db: Any, **kw: Any) -> VehicleLoadout:
        seen_history["history_snapshot_items"] = kw["history_snapshot_items"]
        loadout = VehicleLoadout(
            vehicle_id=kw["vehicle_id"],
            recorded_at=datetime.now(UTC),
            recorded_by_dispatcher_id=kw["dispatcher_id"],
        )
        loadout.id = uuid.uuid4()
        return loadout

    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _find_v)
    monkeypatch.setattr(catalog_repo, "find_base_item_by_id", _find_base)
    monkeypatch.setattr(fleet_repo, "find_current_loadout", _find_current_loadout)
    monkeypatch.setattr(fleet_repo, "replace_loadout", _replace)

    result = await fleet_use_cases.set_loadout(
        None,  # type: ignore[arg-type]
        vehicle_id=vehicle.id,
        dispatcher_id=uuid.uuid4(),
        items=[(base.id, None, 5)],
    )
    assert isinstance(result, VehicleLoadout)
    assert seen_history["history_snapshot_items"] is None


@pytest.mark.asyncio
async def test_set_loadout_freezes_existing_snapshot_with_base(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Bei bestehendem Snapshot wird der alte Stand Frozen JSONB serialisiert."""
    vehicle = _make_vehicle(tenant_id=uuid.uuid4())
    base = _make_base_item(is_active=True)

    existing_loadout = VehicleLoadout(
        vehicle_id=vehicle.id,
        recorded_at=datetime.now(UTC),
        recorded_by_dispatcher_id=uuid.uuid4(),
    )
    existing_loadout.id = uuid.uuid4()

    existing_item = VehicleLoadoutItem(
        loadout_id=existing_loadout.id,
        base_item_id=base.id,
        tenant_extension_id=None,
        quantity=3,
        created_at=datetime.now(UTC),
    )
    existing_item.id = uuid.uuid4()

    async def _find_v(_db: Any, _vid: uuid.UUID) -> Vehicle:
        return vehicle

    async def _find_base(_db: Any, _bid: uuid.UUID) -> CatalogItemBase:
        return base

    async def _find_current(_db: Any, _vid: uuid.UUID) -> VehicleLoadout:
        return existing_loadout

    async def _list_items(_db: Any, _lid: uuid.UUID) -> list[VehicleLoadoutItem]:
        return [existing_item]

    seen: dict[str, Any] = {}

    async def _replace(_db: Any, **kw: Any) -> VehicleLoadout:
        seen["history_snapshot_items"] = kw["history_snapshot_items"]
        seen["items"] = kw["items"]
        loadout = VehicleLoadout(
            vehicle_id=kw["vehicle_id"],
            recorded_at=datetime.now(UTC),
            recorded_by_dispatcher_id=kw["dispatcher_id"],
        )
        loadout.id = uuid.uuid4()
        return loadout

    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _find_v)
    monkeypatch.setattr(catalog_repo, "find_base_item_by_id", _find_base)
    monkeypatch.setattr(fleet_repo, "find_current_loadout", _find_current)
    monkeypatch.setattr(fleet_repo, "list_loadout_items", _list_items)
    monkeypatch.setattr(fleet_repo, "replace_loadout", _replace)

    await fleet_use_cases.set_loadout(
        None,  # type: ignore[arg-type]
        vehicle_id=vehicle.id,
        dispatcher_id=uuid.uuid4(),
        items=[(base.id, None, 10)],
    )

    history = seen["history_snapshot_items"]
    assert isinstance(history, list)
    assert len(history) == 1
    assert history[0]["ref_kind"] == "base"
    assert history[0]["quantity"] == 3
    assert history[0]["name_at_snapshot"] == base.name
    assert history[0]["unit_at_snapshot"] == base.default_unit_label


# ─── set_head_office ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_set_head_office_requires_active_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    inactive = _make_tenant(status=TENANT_STATUS_APPLIED)

    async def _find(_db: Any, _tid: uuid.UUID) -> Tenant:
        return inactive

    monkeypatch.setattr(fleet_use_cases, "find_tenant_by_id", _find)

    with pytest.raises(TenantNotActiveError):
        await fleet_use_cases.set_head_office(
            None,  # type: ignore[arg-type]
            tenant_id=inactive.id,
            lat=10.0,
            lng=20.0,
        )


@pytest.mark.asyncio
async def test_get_head_office_raises_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _find(_db: Any, _tid: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(fleet_repo, "find_head_office_by_tenant", _find)

    with pytest.raises(fleet_use_cases.HeadOfficeNotFoundError):
        await fleet_use_cases.get_head_office(
            None,  # type: ignore[arg-type]
            uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_get_head_office_returns_when_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    head = TenantHeadOffice(tenant_id=uuid.uuid4(), lat=1.0, lng=2.0)

    async def _find(_db: Any, _tid: uuid.UUID) -> TenantHeadOffice:
        return head

    monkeypatch.setattr(fleet_repo, "find_head_office_by_tenant", _find)
    result = await fleet_use_cases.get_head_office(
        None,  # type: ignore[arg-type]
        head.tenant_id,
    )
    assert result is head
