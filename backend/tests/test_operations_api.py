"""Tests für ``backend/eb_digital/operations/api`` (Sub-Surface S8e + S2c).

Pattern analog ``test_fleet_api``: ``make_client(behavior)`` baut eine App mit
gestubbten Use-Cases / Repositories / Session-Helpern auf. Fokus: Auth +
Rollen-Matrix (Disp R/W teilnehmend, PA R-only via ?tenant_id, Carer
R+complete, Anon 403 auf S8e), Exception→HTTP-Mapping, Anon-Order-Pfad mit
Rate-Limit.
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

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
from eb_digital.fleet.use_cases import VehicleNotSupplyTransporterError
from eb_digital.operations import api as ops_api
from eb_digital.operations import use_cases as uc
from eb_digital.operations.exceptions import (
    AnonymousSessionInvalidError,
    NotParticipantError,
    OperationAlreadyClosedError,
    OperationNotFoundError,
    OrderNotInModerationError,
    OrderNotPendingError,
    VehicleNotEligibleError,
)
from eb_digital.operations.models import (
    OPERATION_STATUS_ACTIVE,
    ORDER_STATUS_PENDING,
    PLAUSIBILITY_ACCEPTED,
    Operation,
)
from eb_digital.operations.repository import (
    CustomerOrderRepository,
    OperationAreaRepository,
    OperationAuditLogRepository,
    OperationRepository,
)

_GEOMETRY: dict[str, Any] = {
    "type": "Polygon",
    "coordinates": [[[8.80, 53.07], [8.81, 53.07], [8.81, 53.08], [8.80, 53.07]]],
}
_AREA_PAYLOAD = {"area_index": 1, "label": "Osterdeich", "polygon": _GEOMETRY}


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


def _subject(*, kind: str, username: str, tenant_id: uuid.UUID | None = None) -> AuthSubject:
    return AuthSubject(
        kind=kind,  # type: ignore[arg-type]
        id=uuid.uuid4(),
        username=username,
        password_hash=hash_password("correcthorsebattery"),
        is_active=True,
        tenant_id=tenant_id
        if tenant_id is not None
        else (None if kind == KIND_PLATFORM_ADMIN else uuid.uuid4()),
    )


def _operation(*, tenant_id: uuid.UUID | None = None) -> Operation:
    op = Operation(
        id=uuid.uuid4(),
        status=OPERATION_STATUS_ACTIVE,
        city_label="Bremen",
        url_token="tok",
        access_code_active=False,
        plausibility_threshold_m=None,
    )
    op.opened_at = datetime.now(UTC)
    op.closed_at = None
    op.created_at = datetime.now(UTC)
    op.updated_at = datetime.now(UTC)
    return op


def _order_ns(*, operation_id: uuid.UUID) -> Any:
    return SimpleNamespace(
        id=uuid.uuid4(),
        operation_id=operation_id,
        anonymous_session_id=None,
        placed_at=datetime.now(UTC),
        status=ORDER_STATUS_PENDING,
        location_lat=53.07,
        location_lng=8.80,
        location_accuracy_m=10.0,
        location_text=None,
        plausibility_outcome=PLAUSIBILITY_ACCEPTED,
        plausibility_distance_m=10.0,
        plausibility_threshold_m=5000,
        plausibility_variant="dynamic_2_accuracy",
        moderation_actor_dispatcher_id=None,
        moderation_at=None,
    )


@pytest.fixture
def make_client(monkeypatch: pytest.MonkeyPatch, fake_valkey: fakeredis.aioredis.FakeRedis) -> Any:
    def _make(behavior: dict[str, Any]) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()
        subjects: dict[str, AuthSubject | None] = behavior.get("subjects", {})

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return _StubDbSession()

        async def _find_by_username(_s: Any, username: str) -> AuthSubject | None:
            return subjects.get(username)

        async def _tenant_login_allowed(_db: Any, _subject: AuthSubject) -> bool:
            return True

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(auth_api, "find_by_username", _find_by_username)
        monkeypatch.setattr(auth_api, "_tenant_login_allowed", _tenant_login_allowed)

        # Repository-Lookups
        op = behavior.get("operation")
        monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
        monkeypatch.setattr(
            OperationRepository,
            "owner_tenant_id",
            AsyncMock(return_value=behavior.get("owner_tenant_id")),
        )
        monkeypatch.setattr(
            OperationRepository,
            "list_for_tenant",
            AsyncMock(return_value=behavior.get("operations_list", [])),
        )
        monkeypatch.setattr(
            OperationRepository,
            "find_by_url_token",
            AsyncMock(return_value=behavior.get("operation_by_token")),
        )
        monkeypatch.setattr(
            OperationAreaRepository, "list_for_operation", AsyncMock(return_value=[])
        )
        monkeypatch.setattr(
            CustomerOrderRepository, "find_by_id", AsyncMock(return_value=behavior.get("order"))
        )
        monkeypatch.setattr(
            CustomerOrderRepository,
            "list_for_operation",
            AsyncMock(return_value=behavior.get("orders_list", [])),
        )
        monkeypatch.setattr(CustomerOrderRepository, "items_for_order", AsyncMock(return_value=[]))
        monkeypatch.setattr(
            OperationAuditLogRepository,
            "list_for_operation",
            AsyncMock(return_value=behavior.get("audit_entries", [])),
        )

        # Use-Case-Stubs (Resultat oder Exception)
        ucr: dict[str, Any] = behavior.get("use_case_result", {})

        def _uc_stub(name: str) -> Any:
            async def _inner(**_kw: Any) -> Any:
                v = ucr.get(name)
                if isinstance(v, Exception):
                    raise v
                return v

            return _inner

        for name in (
            "open_operation",
            "close_operation",
            "change_operation_areas",
            "toggle_access_code",
            "switch_supply_transporter_mode",
            "approve_low_plausibility_order",
            "assign_vehicle",
            "cancel_order",
            "complete_order",
            "place_order",
        ):
            monkeypatch.setattr(uc, name, _uc_stub(name))

        # Anon-Session + Rate-Limit (für S2c)
        monkeypatch.setattr(
            ops_api, "get_current_anonymous_session", lambda _request: behavior.get("anon_session")
        )
        allowed = behavior.get("rate_allowed", True)
        monkeypatch.setattr(
            ops_api,
            "incr_and_check",
            AsyncMock(return_value=SimpleNamespace(allowed=allowed, retry_after_seconds=60)),
        )
        return TestClient(app)

    return _make


def _login(client: TestClient, *, username: str) -> None:
    r = client.post(
        "/api/auth/login", json={"username": username, "password": "correcthorsebattery"}
    )
    assert r.status_code == 200, r.text


# ─── POST /operations ────────────────────────────────────────────────────────


def test_open_without_auth_401(make_client: Any) -> None:
    with make_client({}) as client:
        r = client.post("/api/operations", json={"city_label": "B", "areas": [_AREA_PAYLOAD]})
    assert r.status_code == 401


def test_open_as_carer_403(make_client: Any) -> None:
    with make_client({"subjects": {"c": _subject(kind=KIND_CARER, username="c")}}) as client:
        _login(client, username="c")
        r = client.post("/api/operations", json={"city_label": "B", "areas": [_AREA_PAYLOAD]})
    assert r.status_code == 403


def test_open_as_platform_admin_403(make_client: Any) -> None:
    with make_client(
        {"subjects": {"a": _subject(kind=KIND_PLATFORM_ADMIN, username="a")}}
    ) as client:
        _login(client, username="a")
        r = client.post("/api/operations", json={"city_label": "B", "areas": [_AREA_PAYLOAD]})
    assert r.status_code == 403


def test_open_happy_201(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"open_operation": (op, "CODE12")},
        "owner_tenant_id": disp.tenant_id,
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(
            "/api/operations",
            json={"city_label": "Bremen", "areas": [_AREA_PAYLOAD], "access_code_active": True},
        )
    assert r.status_code == 201, r.text
    assert r.json()["url_token"] == "tok"


def test_open_invalid_geometry_422(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    with make_client({"subjects": {"d": disp}}) as client:
        _login(client, username="d")
        bad = {
            "area_index": 1,
            "polygon": {"type": "Polygon", "coordinates": [[[8.8, 53.0], [8.9, 53.0]]]},
        }
        r = client.post("/api/operations", json={"city_label": "B", "areas": [bad]})
    assert r.status_code == 422


# ─── GET /operations ─────────────────────────────────────────────────────────


def test_list_as_dispatcher(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    behavior = {"subjects": {"d": disp}, "operations_list": [op], "owner_tenant_id": disp.tenant_id}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.get("/api/operations")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_list_platform_admin_without_tenant_400(make_client: Any) -> None:
    with make_client(
        {"subjects": {"a": _subject(kind=KIND_PLATFORM_ADMIN, username="a")}}
    ) as client:
        _login(client, username="a")
        r = client.get("/api/operations")
    assert r.status_code == 400


def test_list_platform_admin_with_tenant(make_client: Any) -> None:
    op = _operation()
    behavior = {
        "subjects": {"a": _subject(kind=KIND_PLATFORM_ADMIN, username="a")},
        "operations_list": [op],
        "owner_tenant_id": uuid.uuid4(),
    }
    with make_client(behavior) as client:
        _login(client, username="a")
        r = client.get(f"/api/operations?tenant_id={uuid.uuid4()}")
    assert r.status_code == 200


# ─── GET /operations/{id} ────────────────────────────────────────────────────


def test_get_operation_not_found_404(make_client: Any) -> None:
    with make_client(
        {"subjects": {"d": _subject(kind=KIND_DISPATCHER, username="d")}, "operation": None}
    ) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{uuid.uuid4()}")
    assert r.status_code == 404


def test_get_operation_wrong_tenant_403(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    behavior = {"subjects": {"d": disp}, "operation": op, "owner_tenant_id": uuid.uuid4()}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{op.id}")
    assert r.status_code == 403


def test_get_operation_dispatcher_ok(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    behavior = {"subjects": {"d": disp}, "operation": op, "owner_tenant_id": disp.tenant_id}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{op.id}")
    assert r.status_code == 200


def test_get_operation_platform_admin_ok(make_client: Any) -> None:
    op = _operation()
    behavior = {
        "subjects": {"a": _subject(kind=KIND_PLATFORM_ADMIN, username="a")},
        "operation": op,
        "owner_tenant_id": uuid.uuid4(),
    }
    with make_client(behavior) as client:
        _login(client, username="a")
        r = client.get(f"/api/operations/{op.id}")
    assert r.status_code == 200


# ─── close / areas / access-code / supply-mode ───────────────────────────────


def test_close_happy(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"close_operation": op},
        "owner_tenant_id": disp.tenant_id,
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{op.id}/close")
    assert r.status_code == 200


def test_close_already_closed_409(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"close_operation": OperationAlreadyClosedError("x")},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{uuid.uuid4()}/close")
    assert r.status_code == 409


def test_close_not_found_404(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"close_operation": OperationNotFoundError("x")},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{uuid.uuid4()}/close")
    assert r.status_code == 404


def test_change_areas_happy(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"change_operation_areas": op},
        "owner_tenant_id": disp.tenant_id,
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{op.id}/areas", json={"areas": [_AREA_PAYLOAD]})
    assert r.status_code == 200


def test_access_code_toggle_returns_code(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    op.access_code_active = True
    behavior = {"subjects": {"d": disp}, "use_case_result": {"toggle_access_code": (op, "CODE99")}}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{op.id}/access-code", json={"activate": True})
    assert r.status_code == 200
    body = r.json()
    assert body["access_code"] == "CODE99"
    assert body["access_code_active"] is True


def test_supply_mode_happy(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    vehicle = SimpleNamespace(id=uuid.uuid4(), mode="large_order")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"switch_supply_transporter_mode": vehicle},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(
            f"/api/operations/{uuid.uuid4()}/supply-transporter-mode",
            json={"vehicle_id": str(vehicle.id), "mode": "large_order"},
        )
    assert r.status_code == 200
    assert r.json()["mode"] == "large_order"


def test_supply_mode_not_supply_transporter_422(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {
            "switch_supply_transporter_mode": VehicleNotSupplyTransporterError(uuid.uuid4())
        },
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(
            f"/api/operations/{uuid.uuid4()}/supply-transporter-mode",
            json={"vehicle_id": str(uuid.uuid4()), "mode": "large_order"},
        )
    assert r.status_code == 422


# ─── orders read + actions ────────────────────────────────────────────────────


def test_list_orders_404_when_operation_missing(make_client: Any) -> None:
    with make_client(
        {"subjects": {"d": _subject(kind=KIND_DISPATCHER, username="d")}, "operation": None}
    ) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{uuid.uuid4()}/orders")
    assert r.status_code == 404


def test_list_orders_ok(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    order = _order_ns(operation_id=op.id)
    behavior = {
        "subjects": {"d": disp},
        "operation": op,
        "owner_tenant_id": disp.tenant_id,
        "orders_list": [order],
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{op.id}/orders")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_order_404_wrong_operation(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    order = _order_ns(operation_id=uuid.uuid4())
    behavior = {"subjects": {"d": disp}, "order": order}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{uuid.uuid4()}/orders/{order.id}")
    assert r.status_code == 404


def test_get_order_ok(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    order = _order_ns(operation_id=op.id)
    behavior = {"subjects": {"d": disp}, "order": order, "owner_tenant_id": disp.tenant_id}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{op.id}/orders/{order.id}")
    assert r.status_code == 200


def test_approve_moderated_happy(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    order = _order_ns(operation_id=op.id)
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"approve_low_plausibility_order": order},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{op.id}/orders/{order.id}/approve-moderated")
    assert r.status_code == 200


def test_assign_vehicle_201(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    assignment = SimpleNamespace(
        id=uuid.uuid4(),
        order_id=uuid.uuid4(),
        vehicle_id=uuid.uuid4(),
        dispatcher_id=disp.id,
        status="assigned",
        assigned_at=datetime.now(UTC),
        completed_at=None,
    )
    behavior = {"subjects": {"d": disp}, "use_case_result": {"assign_vehicle": assignment}}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(
            f"/api/operations/{uuid.uuid4()}/orders/{uuid.uuid4()}/assignments",
            json={"vehicle_id": str(uuid.uuid4())},
        )
    assert r.status_code == 201


def test_assign_vehicle_not_eligible_422(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"assign_vehicle": VehicleNotEligibleError("x")},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(
            f"/api/operations/{uuid.uuid4()}/orders/{uuid.uuid4()}/assignments",
            json={"vehicle_id": str(uuid.uuid4())},
        )
    assert r.status_code == 422


def test_cancel_order_happy(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    order = _order_ns(operation_id=op.id)
    behavior = {"subjects": {"d": disp}, "use_case_result": {"cancel_order": order}}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{op.id}/orders/{order.id}/cancel")
    assert r.status_code == 200


def test_complete_order_as_carer(make_client: Any) -> None:
    carer = _subject(kind=KIND_CARER, username="c")
    op = _operation()
    order = _order_ns(operation_id=op.id)
    behavior = {"subjects": {"c": carer}, "use_case_result": {"complete_order": order}}
    with make_client(behavior) as client:
        _login(client, username="c")
        r = client.post(f"/api/operations/{op.id}/orders/{order.id}/complete")
    assert r.status_code == 200


def test_complete_order_as_platform_admin_403(make_client: Any) -> None:
    with make_client(
        {"subjects": {"a": _subject(kind=KIND_PLATFORM_ADMIN, username="a")}}
    ) as client:
        _login(client, username="a")
        r = client.post(f"/api/operations/{uuid.uuid4()}/orders/{uuid.uuid4()}/complete")
    assert r.status_code == 403


# ─── audit-log ────────────────────────────────────────────────────────────────


def test_audit_log_ok(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    entry = SimpleNamespace(
        id=uuid.uuid4(),
        operation_id=op.id,
        actor_dispatcher_id=disp.id,
        action_type="operation_opened",
        at=datetime.now(UTC),
        target_kind="operation",
        target_id=op.id,
        payload={"k": "v"},
    )
    behavior = {
        "subjects": {"d": disp},
        "operation": op,
        "owner_tenant_id": disp.tenant_id,
        "audit_entries": [entry],
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{op.id}/audit-log")
    assert r.status_code == 200
    assert r.json()[0]["action_type"] == "operation_opened"


def test_audit_log_wrong_tenant_403(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    op = _operation()
    behavior = {"subjects": {"d": disp}, "operation": op, "owner_tenant_id": uuid.uuid4()}
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.get(f"/api/operations/{op.id}/audit-log")
    assert r.status_code == 403


# ─── Anon-Order (S2c) ──────────────────────────────────────────────────────────


def _anon_payload() -> dict[str, Any]:
    return {
        "items": [{"base_item_id": str(uuid.uuid4()), "quantity": 2}],
        "location_text": "Marktplatz",
    }


def test_anon_order_rate_limited_429(make_client: Any) -> None:
    with make_client({"rate_allowed": False}) as client:
        r = client.post(f"/api/anon/{uuid.uuid4()}/order", json=_anon_payload())
    assert r.status_code == 429


def test_anon_order_operation_not_found_404(make_client: Any) -> None:
    with make_client({"operation_by_token": None}) as client:
        r = client.post(f"/api/anon/{uuid.uuid4()}/order", json=_anon_payload())
    assert r.status_code == 404


def test_anon_order_no_session_401(make_client: Any) -> None:
    op = _operation()
    with make_client({"operation_by_token": op, "anon_session": None}) as client:
        r = client.post(f"/api/anon/{op.url_token}/order", json=_anon_payload())
    assert r.status_code == 401


def test_anon_order_session_mismatch_401(make_client: Any) -> None:
    op = _operation()
    anon = SimpleNamespace(session_id=uuid.uuid4(), operation_id=uuid.uuid4())
    with make_client({"operation_by_token": op, "anon_session": anon}) as client:
        r = client.post(f"/api/anon/{op.url_token}/order", json=_anon_payload())
    assert r.status_code == 401


def test_anon_order_use_case_anon_invalid_401(make_client: Any) -> None:
    op = _operation()
    anon = SimpleNamespace(session_id=uuid.uuid4(), operation_id=op.id)
    behavior = {
        "operation_by_token": op,
        "anon_session": anon,
        "use_case_result": {"place_order": AnonymousSessionInvalidError("x")},
    }
    with make_client(behavior) as client:
        r = client.post(f"/api/anon/{op.url_token}/order", json=_anon_payload())
    assert r.status_code == 401


def test_anon_order_use_case_unhandled_500(make_client: Any) -> None:
    op = _operation()
    anon = SimpleNamespace(session_id=uuid.uuid4(), operation_id=op.id)
    behavior = {
        "operation_by_token": op,
        "anon_session": anon,
        "use_case_result": {"place_order": RuntimeError("boom")},
    }
    with make_client(behavior) as client:
        r = client.post(f"/api/anon/{op.url_token}/order", json=_anon_payload())
    assert r.status_code == 500


# ─── Exception-Mapping (_exc_to_http) ─────────────────────────────────────────


def test_close_not_participant_403(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"close_operation": NotParticipantError("x")},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{uuid.uuid4()}/close")
    assert r.status_code == 403


def test_assign_order_not_pending_409(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"assign_vehicle": OrderNotPendingError("x")},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(
            f"/api/operations/{uuid.uuid4()}/orders/{uuid.uuid4()}/assignments",
            json={"vehicle_id": str(uuid.uuid4())},
        )
    assert r.status_code == 409


def test_approve_not_in_moderation_409(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"approve_low_plausibility_order": OrderNotInModerationError("x")},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{uuid.uuid4()}/orders/{uuid.uuid4()}/approve-moderated")
    assert r.status_code == 409


def test_close_unhandled_exception_500(make_client: Any) -> None:
    disp = _subject(kind=KIND_DISPATCHER, username="d")
    behavior = {
        "subjects": {"d": disp},
        "use_case_result": {"close_operation": RuntimeError("boom")},
    }
    with make_client(behavior) as client:
        _login(client, username="d")
        r = client.post(f"/api/operations/{uuid.uuid4()}/close")
    assert r.status_code == 500


def test_anon_order_happy_201(make_client: Any) -> None:
    op = _operation()
    anon = SimpleNamespace(session_id=uuid.uuid4(), operation_id=op.id)
    order = _order_ns(operation_id=op.id)
    result = SimpleNamespace(accepted=True)
    behavior = {
        "operation_by_token": op,
        "anon_session": anon,
        "use_case_result": {"place_order": (order, result)},
    }
    with make_client(behavior) as client:
        r = client.post(f"/api/anon/{op.url_token}/order", json=_anon_payload())
    assert r.status_code == 201
    assert r.json()["plausibility_outcome"] == PLAUSIBILITY_ACCEPTED
