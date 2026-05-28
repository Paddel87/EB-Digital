"""Tests für ``backend/eb_digital/fleet/repositories``.

Strategie analog ``test_catalog_repositories``: ``_StubSession`` für die
Add/Flush-Pfade. SELECT-Logik wird im Compose-Smoke gegen die echte
Postgres-DB validiert.

``replace_loadout`` wird hier nur teilweise getestet (Append-Pfad ohne
existierenden Snapshot); der vollständige Replace-Pfad mit History-Kopie
und Item-CASCADE hängt von echten DB-Operationen ab → Smoke-Test.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest

from eb_digital.fleet import repositories as fleet_repo
from eb_digital.fleet.models import (
    SUPPLY_MODE_OFF,
    VEHICLE_TYPE_REGULAR,
    VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    TenantHeadOffice,
    Vehicle,
    VehicleLoadout,
)


class _StubResult:
    def __init__(self, *, single: Any = None) -> None:
        self._single = single

    def scalar_one_or_none(self) -> Any:
        return self._single


class _StubSession:
    """Minimaler Stub für add/flush + execute, kein Query-Verständnis."""

    def __init__(self, *, select_result: Any = None) -> None:
        self._select_result = select_result
        self.added: list[Any] = []
        self.flushes = 0

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1

    async def execute(self, _stmt: Any) -> _StubResult:
        return _StubResult(single=self._select_result)


# ─── Vehicle-Repository ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_vehicle_regular_has_no_mode() -> None:
    session = _StubSession()
    result = await fleet_repo.create_vehicle(
        session,  # type: ignore[arg-type]
        tenant_id=uuid.uuid4(),
        type_=VEHICLE_TYPE_REGULAR,
        name="ELW-1",
    )
    assert isinstance(result, Vehicle)
    assert result.type == VEHICLE_TYPE_REGULAR
    assert result.mode is None
    assert result.is_active is True
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_create_vehicle_supply_transporter_defaults_mode_off() -> None:
    session = _StubSession()
    result = await fleet_repo.create_vehicle(
        session,  # type: ignore[arg-type]
        tenant_id=uuid.uuid4(),
        type_=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        name="VT-1",
        license_plate="HB-EB 1",
        capacity_label="3.5t",
    )
    assert result.type == VEHICLE_TYPE_SUPPLY_TRANSPORTER
    assert result.mode == SUPPLY_MODE_OFF
    assert result.license_plate == "HB-EB 1"
    assert result.capacity_label == "3.5t"


@pytest.mark.asyncio
async def test_update_vehicle_stammdaten_partial_update() -> None:
    existing = Vehicle(
        tenant_id=uuid.uuid4(),
        type=VEHICLE_TYPE_REGULAR,
        mode=None,
        name="ELW-1",
        license_plate="HB-AB 1",
        capacity_label=None,
        is_active=True,
    )
    existing.id = uuid.uuid4()
    session = _StubSession(select_result=existing)

    result = await fleet_repo.update_vehicle_stammdaten(
        session,  # type: ignore[arg-type]
        vehicle_id=existing.id,
        name="ELW-1-Updated",
    )
    assert result is existing
    assert existing.name == "ELW-1-Updated"
    assert existing.license_plate == "HB-AB 1"


@pytest.mark.asyncio
async def test_update_vehicle_stammdaten_missing_returns_none() -> None:
    session = _StubSession(select_result=None)
    result = await fleet_repo.update_vehicle_stammdaten(
        session,  # type: ignore[arg-type]
        vehicle_id=uuid.uuid4(),
        name="X",
    )
    assert result is None


@pytest.mark.asyncio
async def test_deactivate_vehicle_sets_is_active_false() -> None:
    existing = Vehicle(
        tenant_id=uuid.uuid4(),
        type=VEHICLE_TYPE_REGULAR,
        mode=None,
        name="ELW-1",
        is_active=True,
    )
    existing.id = uuid.uuid4()
    session = _StubSession(select_result=existing)

    result = await fleet_repo.deactivate_vehicle(
        session,  # type: ignore[arg-type]
        vehicle_id=existing.id,
    )
    assert result is existing
    assert existing.is_active is False


@pytest.mark.asyncio
async def test_set_vehicle_mode_updates_field() -> None:
    existing = Vehicle(
        tenant_id=uuid.uuid4(),
        type=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        mode=SUPPLY_MODE_OFF,
        name="VT-1",
        is_active=True,
    )
    existing.id = uuid.uuid4()
    session = _StubSession(select_result=existing)
    result = await fleet_repo.set_vehicle_mode(
        session,  # type: ignore[arg-type]
        vehicle_id=existing.id,
        mode="large_order",
    )
    assert result is existing
    assert existing.mode == "large_order"


# ─── HeadOffice-Repository ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_upsert_head_office_inserts_when_missing() -> None:
    session = _StubSession(select_result=None)
    tenant_id = uuid.uuid4()
    result = await fleet_repo.upsert_head_office(
        session,  # type: ignore[arg-type]
        tenant_id=tenant_id,
        lat=53.0793,
        lng=8.8017,
        label="DPolG Bremen",
    )
    assert isinstance(result, TenantHeadOffice)
    assert result.tenant_id == tenant_id
    assert result.lat == 53.0793
    assert result.label == "DPolG Bremen"
    assert len(session.added) == 1


@pytest.mark.asyncio
async def test_upsert_head_office_updates_when_exists() -> None:
    existing = TenantHeadOffice(
        tenant_id=uuid.uuid4(),
        lat=10.0,
        lng=20.0,
        label="Old",
    )
    session = _StubSession(select_result=existing)
    result = await fleet_repo.upsert_head_office(
        session,  # type: ignore[arg-type]
        tenant_id=existing.tenant_id,
        lat=11.0,
        lng=21.0,
        label="New",
    )
    assert result is existing
    assert existing.lat == 11.0
    assert existing.lng == 21.0
    assert existing.label == "New"
    # Existierende Instanz wird nicht erneut hinzugefügt.
    assert len(session.added) == 0


# ─── Loadout-Repository (Snapshot-Pfad ohne History) ──────────────────────


class _ReplaceSession:
    """Stub für ``replace_loadout`` ohne existierenden Snapshot.

    Trennt sich von ``_StubSession``, weil ``replace_loadout`` mehrere
    ``execute``-Aufrufe und ``flush`` in einer Reihenfolge macht — wir
    geben für den ersten Lookup ``None`` zurück (kein bestehender Loadout).
    """

    def __init__(self) -> None:
        self.added: list[Any] = []
        self.flushes = 0
        self.deletes = 0

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1
        # Simuliere DB-generated id setzen — die Use-Cases verlassen sich darauf.
        for obj in self.added:
            if isinstance(obj, VehicleLoadout) and obj.id is None:
                obj.id = uuid.uuid4()

    async def execute(self, stmt: Any) -> Any:
        # ``find_current_loadout``-Pfad: scalar_one_or_none → None.
        # ``delete``-Pfad: wir merken uns nur, dass es lief.
        stmt_text = str(stmt)
        if "DELETE" in stmt_text:
            self.deletes += 1
            return _StubResult(single=None)
        return _StubResult(single=None)


@pytest.mark.asyncio
async def test_replace_loadout_creates_new_when_none_exists() -> None:
    session = _ReplaceSession()
    base_id = uuid.uuid4()
    vehicle_id = uuid.uuid4()
    dispatcher_id = uuid.uuid4()
    items = [(base_id, None, 5)]

    result = await fleet_repo.replace_loadout(
        session,  # type: ignore[arg-type]
        vehicle_id=vehicle_id,
        dispatcher_id=dispatcher_id,
        items=items,
        history_snapshot_items=None,
    )

    assert isinstance(result, VehicleLoadout)
    assert result.vehicle_id == vehicle_id
    assert result.recorded_by_dispatcher_id == dispatcher_id
    assert isinstance(result.recorded_at, datetime)
    assert result.recorded_at.tzinfo == UTC
    # Loadout + ein Item wurden hinzugefügt.
    loadouts = [o for o in session.added if isinstance(o, VehicleLoadout)]
    assert len(loadouts) == 1
    # Items hängen via FK am loadout — wir prüfen die Anzahl der nicht-Loadout-Adds.
    item_adds = [o for o in session.added if not isinstance(o, VehicleLoadout)]
    assert len(item_adds) == 1
    # Kein Delete-Aufruf, weil kein existierender Snapshot.
    assert session.deletes == 0
