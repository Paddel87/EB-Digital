"""Tests für ``backend/eb_digital/fleet/api`` mit TestClient.

Pattern analog ``test_catalog_api``: ``make_client(behavior)`` baut eine
App mit gestubbten Repositories / Use-Cases auf. Wir validieren primär:

  • Authentifizierung (401 ohne Session) und Rollen-Matrix
    (Disponent eigener Tenant R/W, PA R-only via ?tenant_id, Carer R-only
    eigener Tenant, Cross-Tenant 403, Anon 403).
  • Mode-Endpoint inklusive 422 für reguläres Fahrzeug.
  • Loadout-Set inklusive 422 für deaktivierte Catalog-Items + Cross-
    Tenant-Extension.
  • HeadOffice-Upsert inklusive Range-Validation.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from eb_digital.auth import api as auth_api
from eb_digital.auth.api import get_db_session, get_valkey_client
from eb_digital.auth.hashing import hash_password
from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
    AuthSubject,
)
from eb_digital.fleet import repositories as fleet_repo
from eb_digital.fleet import use_cases as fleet_use_cases
from eb_digital.fleet.models import (
    SUPPLY_MODE_OFF,
    VEHICLE_TYPE_REGULAR,
    VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    TenantHeadOffice,
    Vehicle,
    VehicleLoadout,
    VehicleLoadoutHistory,
    VehicleLoadoutItem,
)


class _StubDbSession:
    async def commit(self) -> None:
        return None


@pytest.fixture
async def fake_valkey() -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    client = fakeredis.aioredis.FakeRedis()
    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()


def _make_subject(
    *,
    kind: str,
    username: str = "user",
    password: str = "correcthorsebattery",
    tenant_id: uuid.UUID | None = None,
) -> AuthSubject:
    return AuthSubject(
        kind=kind,  # type: ignore[arg-type]
        id=uuid.uuid4(),
        username=username,
        password_hash=hash_password(password),
        is_active=True,
        tenant_id=tenant_id
        if tenant_id is not None
        else (None if kind == KIND_PLATFORM_ADMIN else uuid.uuid4()),
    )


def _make_vehicle(
    *,
    tenant_id: uuid.UUID,
    type_: str = VEHICLE_TYPE_REGULAR,
    mode: str | None = None,
    is_active: bool = True,
) -> Vehicle:
    v = Vehicle(
        tenant_id=tenant_id,
        type=type_,
        mode=mode,
        name="V",
        is_active=is_active,
    )
    v.id = uuid.uuid4()
    v.created_at = datetime.now(UTC)
    v.updated_at = datetime.now(UTC)
    return v


def _make_loadout(*, vehicle_id: uuid.UUID, dispatcher_id: uuid.UUID) -> VehicleLoadout:
    loadout = VehicleLoadout(
        vehicle_id=vehicle_id,
        recorded_at=datetime.now(UTC),
        recorded_by_dispatcher_id=dispatcher_id,
    )
    loadout.id = uuid.uuid4()
    loadout.created_at = datetime.now(UTC)
    loadout.updated_at = datetime.now(UTC)
    return loadout


def _make_loadout_item(
    *,
    loadout_id: uuid.UUID,
    base_item_id: uuid.UUID,
    quantity: int = 5,
) -> VehicleLoadoutItem:
    item = VehicleLoadoutItem(
        loadout_id=loadout_id,
        base_item_id=base_item_id,
        tenant_extension_id=None,
        quantity=quantity,
        created_at=datetime.now(UTC),
    )
    item.id = uuid.uuid4()
    return item


def _make_head_office(
    *, tenant_id: uuid.UUID, lat: float = 53.0, lng: float = 8.0
) -> TenantHeadOffice:
    head = TenantHeadOffice(tenant_id=tenant_id, lat=lat, lng=lng, label="DPolG Bremen")
    head.created_at = datetime.now(UTC)
    head.updated_at = datetime.now(UTC)
    return head


@pytest.fixture
def make_client(
    monkeypatch: pytest.MonkeyPatch,
    fake_valkey: fakeredis.aioredis.FakeRedis,
) -> Any:
    """Liefert ``make_client(behavior)`` mit Stubs für Fleet-Pfade."""

    def _make(behavior: dict[str, Any]) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()

        subjects: dict[str, AuthSubject | None] = behavior.get("subjects", {})

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return _StubDbSession()

        async def _fake_find_by_username(_session: Any, username: str) -> AuthSubject | None:
            return subjects.get(username)

        async def _fake_tenant_login_allowed(_db: Any, _subject: AuthSubject) -> bool:
            return bool(behavior.get("tenant_login_active", True))

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(auth_api, "find_by_username", _fake_find_by_username)
        monkeypatch.setattr(
            auth_api,
            "_tenant_login_allowed",
            _fake_tenant_login_allowed,
        )

        # Vehicle-Lookup-Stubs
        find_vehicle = behavior.get("find_vehicle_by_id")

        async def _fake_find_vehicle(_db: Any, vehicle_id: uuid.UUID) -> Vehicle | None:
            if callable(find_vehicle):
                return find_vehicle(vehicle_id)
            return None

        monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", _fake_find_vehicle)

        async def _fake_list_vehicles(
            _db: Any, tenant_id: uuid.UUID, *, include_inactive: bool = False
        ) -> list[Vehicle]:
            items = list(behavior.get("vehicles_list", []))
            items = [v for v in items if v.tenant_id == tenant_id]
            if not include_inactive:
                items = [v for v in items if v.is_active]
            return items

        monkeypatch.setattr(fleet_repo, "list_vehicles_for_tenant", _fake_list_vehicles)

        find_loadout = behavior.get("find_current_loadout")
        loadout_items = behavior.get("loadout_items", [])

        async def _fake_find_loadout(_db: Any, vehicle_id: uuid.UUID) -> VehicleLoadout | None:
            if callable(find_loadout):
                return find_loadout(vehicle_id)
            return None

        async def _fake_list_loadout_items(
            _db: Any, _loadout_id: uuid.UUID
        ) -> list[VehicleLoadoutItem]:
            return list(loadout_items)

        async def _fake_list_history(
            _db: Any,
            _vehicle_id: uuid.UUID,
            *,
            limit: int = 50,
        ) -> list[VehicleLoadoutHistory]:
            del limit
            return list(behavior.get("loadout_history", []))

        monkeypatch.setattr(fleet_repo, "find_current_loadout", _fake_find_loadout)
        monkeypatch.setattr(fleet_repo, "list_loadout_items", _fake_list_loadout_items)
        monkeypatch.setattr(fleet_repo, "list_loadout_history", _fake_list_history)

        # Use-Case-Stubs
        ucr: dict[str, Any] = behavior.get("use_case_result", {})

        async def _make_uc_stub(name: str) -> Any:
            v = ucr.get(name)
            if isinstance(v, Exception):
                raise v
            return v

        async def _fake_create_vehicle(_db: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("create_vehicle")

        async def _fake_update_vehicle_stammdaten(_db: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("update_vehicle_stammdaten")

        async def _fake_deactivate_vehicle(_db: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("deactivate_vehicle")

        async def _fake_update_mode(_db: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("update_supply_transporter_mode")

        async def _fake_set_loadout(_db: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("set_loadout")

        async def _fake_set_head_office(_db: Any, **_kw: Any) -> Any:
            return await _make_uc_stub("set_head_office")

        async def _fake_get_head_office(_db: Any, _tid: uuid.UUID) -> Any:
            return await _make_uc_stub("get_head_office")

        monkeypatch.setattr(fleet_use_cases, "create_vehicle", _fake_create_vehicle)
        monkeypatch.setattr(
            fleet_use_cases, "update_vehicle_stammdaten", _fake_update_vehicle_stammdaten
        )
        monkeypatch.setattr(fleet_use_cases, "deactivate_vehicle", _fake_deactivate_vehicle)
        monkeypatch.setattr(fleet_use_cases, "update_supply_transporter_mode", _fake_update_mode)
        monkeypatch.setattr(fleet_use_cases, "set_loadout", _fake_set_loadout)
        monkeypatch.setattr(fleet_use_cases, "set_head_office", _fake_set_head_office)
        monkeypatch.setattr(fleet_use_cases, "get_head_office", _fake_get_head_office)

        return TestClient(app)

    return _make


def _login(client: TestClient, *, username: str) -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": "correcthorsebattery"},
    )
    assert response.status_code == 200, response.text


# ─── /api/fleet/vehicles ───────────────────────────────────────────────────


def test_create_vehicle_without_auth_returns_401(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.post(
            "/api/fleet/vehicles",
            json={"type": "regular", "name": "ELW-1"},
        )
    assert response.status_code == 401


def test_create_vehicle_as_carer_forbidden(make_client: Any) -> None:
    carer = _make_subject(kind=KIND_CARER, username="bob")
    with make_client({"subjects": {"bob": carer}}) as client:
        _login(client, username="bob")
        response = client.post(
            "/api/fleet/vehicles",
            json={"type": "regular", "name": "ELW-1"},
        )
    assert response.status_code == 403


def test_create_vehicle_as_dispatcher_returns_201(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    new_vehicle = _make_vehicle(tenant_id=tenant_id, type_=VEHICLE_TYPE_REGULAR)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {"create_vehicle": new_vehicle},
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            "/api/fleet/vehicles",
            json={"type": "regular", "name": "ELW-1"},
        )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["type"] == "regular"
    assert body["mode"] is None
    assert body["tenant_id"] == str(tenant_id)


def test_create_supply_transporter_returns_mode_off(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    new_vehicle = _make_vehicle(
        tenant_id=tenant_id,
        type_=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        mode=SUPPLY_MODE_OFF,
    )
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {"create_vehicle": new_vehicle},
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            "/api/fleet/vehicles",
            json={"type": "supply_transporter", "name": "VT-1"},
        )
    assert response.status_code == 201
    assert response.json()["mode"] == "off"


def test_create_vehicle_invalid_type_returns_422(make_client: Any) -> None:
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice")
    with make_client({"subjects": {"alice": dispatcher}}) as client:
        _login(client, username="alice")
        response = client.post(
            "/api/fleet/vehicles",
            json={"type": "truck", "name": "X"},
        )
    assert response.status_code == 422


def test_list_vehicles_platform_admin_without_tenant_id_returns_422(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client({"subjects": {"patrick": admin}}) as client:
        _login(client, username="patrick")
        response = client.get("/api/fleet/vehicles")
    assert response.status_code == 422


def test_list_vehicles_platform_admin_with_tenant_id_returns_200(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    v1 = _make_vehicle(tenant_id=tenant_id)
    v2 = _make_vehicle(tenant_id=uuid.uuid4())  # anderer Tenant
    with make_client(
        {
            "subjects": {"patrick": admin},
            "vehicles_list": [v1, v2],
        },
    ) as client:
        _login(client, username="patrick")
        response = client.get(f"/api/fleet/vehicles?tenant_id={tenant_id}")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["tenant_id"] == str(tenant_id)


def test_list_vehicles_dispatcher_sees_only_own_tenant(make_client: Any) -> None:
    own_tenant = uuid.uuid4()
    other_tenant = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=own_tenant)
    own_vehicle = _make_vehicle(tenant_id=own_tenant)
    other_vehicle = _make_vehicle(tenant_id=other_tenant)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "vehicles_list": [own_vehicle, other_vehicle],
        },
    ) as client:
        _login(client, username="alice")
        # Cross-Tenant-Query wird ignoriert.
        response = client.get(f"/api/fleet/vehicles?tenant_id={other_tenant}")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["tenant_id"] == str(own_tenant)


def test_get_vehicle_cross_tenant_forbidden(make_client: Any) -> None:
    own_tenant = uuid.uuid4()
    other_tenant = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=own_tenant)
    foreign_vehicle = _make_vehicle(tenant_id=other_tenant)

    def _find(_vid: uuid.UUID) -> Vehicle:
        return foreign_vehicle

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_vehicle_by_id": _find,
        },
    ) as client:
        _login(client, username="alice")
        response = client.get(f"/api/fleet/vehicles/{foreign_vehicle.id}")
    assert response.status_code == 403


def test_get_vehicle_unknown_returns_404(make_client: Any) -> None:
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice")
    with make_client({"subjects": {"alice": dispatcher}}) as client:
        _login(client, username="alice")
        response = client.get(f"/api/fleet/vehicles/{uuid.uuid4()}")
    assert response.status_code == 404


def test_get_vehicle_pa_can_see_any_tenant(make_client: Any) -> None:
    other_tenant = uuid.uuid4()
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    foreign_vehicle = _make_vehicle(tenant_id=other_tenant)

    def _find(_vid: uuid.UUID) -> Vehicle:
        return foreign_vehicle

    with make_client(
        {
            "subjects": {"patrick": admin},
            "find_vehicle_by_id": _find,
        },
    ) as client:
        _login(client, username="patrick")
        response = client.get(f"/api/fleet/vehicles/{foreign_vehicle.id}")
    assert response.status_code == 200
    assert response.json()["tenant_id"] == str(other_tenant)


# ─── /api/fleet/vehicles/{id}/mode ────────────────────────────────────────


def test_mode_endpoint_regular_vehicle_returns_422(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    regular = _make_vehicle(tenant_id=tenant_id, type_=VEHICLE_TYPE_REGULAR)

    def _find(_vid: uuid.UUID) -> Vehicle:
        return regular

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_vehicle_by_id": _find,
            "use_case_result": {
                "update_supply_transporter_mode": fleet_use_cases.VehicleNotSupplyTransporterError(
                    regular.id
                ),
            },
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            f"/api/fleet/vehicles/{regular.id}/mode",
            json={"mode": "large_order"},
        )
    assert response.status_code == 422


def test_mode_endpoint_supply_transporter_returns_200(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    transporter = _make_vehicle(
        tenant_id=tenant_id,
        type_=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        mode=SUPPLY_MODE_OFF,
    )
    updated = _make_vehicle(
        tenant_id=tenant_id,
        type_=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        mode="large_order",
    )
    updated.id = transporter.id

    def _find(_vid: uuid.UUID) -> Vehicle:
        return transporter

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_vehicle_by_id": _find,
            "use_case_result": {"update_supply_transporter_mode": updated},
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            f"/api/fleet/vehicles/{transporter.id}/mode",
            json={"mode": "large_order"},
        )
    assert response.status_code == 200
    assert response.json()["mode"] == "large_order"


def test_mode_endpoint_invalid_value_returns_422(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    transporter = _make_vehicle(
        tenant_id=tenant_id,
        type_=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        mode=SUPPLY_MODE_OFF,
    )

    def _find(_vid: uuid.UUID) -> Vehicle:
        return transporter

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_vehicle_by_id": _find,
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            f"/api/fleet/vehicles/{transporter.id}/mode",
            json={"mode": "turbo"},
        )
    assert response.status_code == 422


# ─── /api/fleet/vehicles/{id}/loadout ─────────────────────────────────────


def test_put_loadout_inactive_base_item_returns_422(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    vehicle = _make_vehicle(tenant_id=tenant_id)

    def _find(_vid: uuid.UUID) -> Vehicle:
        return vehicle

    bad_id = uuid.uuid4()
    err = fleet_use_cases.CatalogItemNotAvailableError(kind="base", ref_id=bad_id)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_vehicle_by_id": _find,
            "use_case_result": {"set_loadout": err},
        },
    ) as client:
        _login(client, username="alice")
        response = client.put(
            f"/api/fleet/vehicles/{vehicle.id}/loadout",
            json={"items": [{"base_item_id": str(bad_id), "quantity": 1}]},
        )
    assert response.status_code == 422


def test_put_loadout_cross_tenant_extension_returns_422(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    other_tenant = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    vehicle = _make_vehicle(tenant_id=tenant_id)
    ext_id = uuid.uuid4()
    err = fleet_use_cases.CrossTenantExtensionError(
        extension_id=ext_id,
        vehicle_tenant=tenant_id,
        extension_tenant=other_tenant,
    )

    def _find(_vid: uuid.UUID) -> Vehicle:
        return vehicle

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_vehicle_by_id": _find,
            "use_case_result": {"set_loadout": err},
        },
    ) as client:
        _login(client, username="alice")
        response = client.put(
            f"/api/fleet/vehicles/{vehicle.id}/loadout",
            json={"items": [{"tenant_extension_id": str(ext_id), "quantity": 2}]},
        )
    assert response.status_code == 422
    assert "cross-tenant" in response.json()["detail"]


def test_put_loadout_happy_path_returns_200(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    vehicle = _make_vehicle(tenant_id=tenant_id)
    base_id = uuid.uuid4()
    loadout = _make_loadout(vehicle_id=vehicle.id, dispatcher_id=dispatcher.id)
    item = _make_loadout_item(loadout_id=loadout.id, base_item_id=base_id, quantity=10)

    def _find(_vid: uuid.UUID) -> Vehicle:
        return vehicle

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_vehicle_by_id": _find,
            "use_case_result": {"set_loadout": loadout},
            "loadout_items": [item],
        },
    ) as client:
        _login(client, username="alice")
        response = client.put(
            f"/api/fleet/vehicles/{vehicle.id}/loadout",
            json={"items": [{"base_item_id": str(base_id), "quantity": 10}]},
        )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["vehicle_id"] == str(vehicle.id)
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 10


def test_get_loadout_history_carer_forbidden(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    carer = _make_subject(kind=KIND_CARER, username="bob", tenant_id=tenant_id)
    vehicle = _make_vehicle(tenant_id=tenant_id)

    def _find(_vid: uuid.UUID) -> Vehicle:
        return vehicle

    with make_client(
        {
            "subjects": {"bob": carer},
            "find_vehicle_by_id": _find,
        },
    ) as client:
        _login(client, username="bob")
        response = client.get(f"/api/fleet/vehicles/{vehicle.id}/loadout/history")
    assert response.status_code == 403


def test_get_loadout_history_dispatcher_returns_200(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    vehicle = _make_vehicle(tenant_id=tenant_id)
    history_entry = VehicleLoadoutHistory(
        vehicle_id=vehicle.id,
        recorded_at=datetime.now(UTC),
        recorded_by_dispatcher_id=dispatcher.id,
        items=[{"ref_kind": "base", "ref_id": str(uuid.uuid4()), "quantity": 3}],
        created_at=datetime.now(UTC),
    )
    history_entry.id = uuid.uuid4()

    def _find(_vid: uuid.UUID) -> Vehicle:
        return vehicle

    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "find_vehicle_by_id": _find,
            "loadout_history": [history_entry],
        },
    ) as client:
        _login(client, username="alice")
        response = client.get(f"/api/fleet/vehicles/{vehicle.id}/loadout/history")
    assert response.status_code == 200
    body = response.json()
    assert len(body["entries"]) == 1


# ─── /api/fleet/head-office ──────────────────────────────────────────────


def test_put_head_office_dispatcher_returns_200(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    head = _make_head_office(tenant_id=tenant_id, lat=53.07, lng=8.80)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {"set_head_office": head},
        },
    ) as client:
        _login(client, username="alice")
        response = client.put(
            "/api/fleet/head-office",
            json={"lat": 53.07, "lng": 8.80, "label": "DPolG Bremen"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["lat"] == 53.07


def test_put_head_office_invalid_lat_returns_422(make_client: Any) -> None:
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice")
    with make_client({"subjects": {"alice": dispatcher}}) as client:
        _login(client, username="alice")
        response = client.put(
            "/api/fleet/head-office",
            json={"lat": 91.0, "lng": 0.0},
        )
    assert response.status_code == 422


def test_get_head_office_pa_without_tenant_id_returns_422(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client({"subjects": {"patrick": admin}}) as client:
        _login(client, username="patrick")
        response = client.get("/api/fleet/head-office")
    assert response.status_code == 422


def test_get_head_office_dispatcher_returns_200(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    head = _make_head_office(tenant_id=tenant_id)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {"get_head_office": head},
        },
    ) as client:
        _login(client, username="alice")
        response = client.get("/api/fleet/head-office")
    assert response.status_code == 200


def test_get_head_office_missing_returns_404(make_client: Any) -> None:
    tenant_id = uuid.uuid4()
    dispatcher = _make_subject(kind=KIND_DISPATCHER, username="alice", tenant_id=tenant_id)
    err = fleet_use_cases.HeadOfficeNotFoundError(tenant_id)
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "use_case_result": {"get_head_office": err},
        },
    ) as client:
        _login(client, username="alice")
        response = client.get("/api/fleet/head-office")
    assert response.status_code == 404
