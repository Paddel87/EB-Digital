"""Tests für die WebSocket-Endpunkte ``eb_digital.realtime.api`` (Schritt 4.4).

Auth wird auf Modul-Ebene gestubbt (``get_current_session_user`` /
``get_current_anonymous_session`` / ``verify_url_token``), die S10-Lookups
über ``eb_digital.tenants.participation``. Der Hub ist real, aber ohne
Valkey-Listener — der Fan-out-Pfad selbst ist in ``test_realtime_hub`` /
``test_realtime_publisher`` abgedeckt.
"""

from __future__ import annotations

import time
import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from eb_digital.auth.repositories import KIND_CARER, KIND_DISPATCHER
from eb_digital.auth.sessions import SessionUser
from eb_digital.auth_anonymous.sessions import AnonymousSessionUser
from eb_digital.realtime import api as rt_api
from eb_digital.realtime import messages
from eb_digital.realtime.hub import WebSocketHub
from eb_digital.realtime.topics import (
    KIND_ASSIGNMENT,
    KIND_ORDER_STATUS,
    topic_for,
)


class _StubSession:
    async def __aenter__(self) -> _StubSession:
        return self

    async def __aexit__(self, *_a: object) -> bool:
        return False


def _make_app(monkeypatch: pytest.MonkeyPatch) -> tuple[Any, WebSocketHub]:
    from eb_digital.app import create_app

    app = create_app()
    hub = WebSocketHub()
    app.state.realtime_hub = hub
    app.state.db_session_factory = lambda: _StubSession()
    return app, hub


def _dispatcher(tenant_id: uuid.UUID) -> SessionUser:
    return SessionUser(
        kind=KIND_DISPATCHER,
        id=uuid.uuid4(),
        username="disp",
        tenant_id=tenant_id,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )


def _carer(tenant_id: uuid.UUID) -> SessionUser:
    return SessionUser(
        kind=KIND_CARER,
        id=uuid.uuid4(),
        username="carer",
        tenant_id=tenant_id,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )


# ─── Auth-Reject ──────────────────────────────────────────────────────────────


def test_dispatcher_unauthenticated_closes_4401(monkeypatch: pytest.MonkeyPatch) -> None:
    app, _hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_session_user", lambda _ws: None)
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as ei, client.websocket_connect("/api/ws/dispatcher"):
        pass
    assert ei.value.code == rt_api.CLOSE_UNAUTHENTICATED


def test_dispatcher_wrong_role_closes_4401(monkeypatch: pytest.MonkeyPatch) -> None:
    app, _hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_session_user", lambda _ws: _carer(uuid.uuid4()))
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as ei, client.websocket_connect("/api/ws/dispatcher"):
        pass
    assert ei.value.code == rt_api.CLOSE_UNAUTHENTICATED


def test_anon_unauthenticated_closes_4401(monkeypatch: pytest.MonkeyPatch) -> None:
    app, _hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_anonymous_session", lambda _ws: None)
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as ei, client.websocket_connect("/api/ws/anon/tok"):
        pass
    assert ei.value.code == rt_api.CLOSE_UNAUTHENTICATED


def test_anon_token_mismatch_closes_4403(monkeypatch: pytest.MonkeyPatch) -> None:
    app, _hub = _make_app(monkeypatch)
    anon = AnonymousSessionUser(
        session_id=uuid.uuid4(),
        operation_id=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    monkeypatch.setattr(rt_api, "get_current_anonymous_session", lambda _ws: anon)
    # Token verweist auf eine ANDERE Operation.
    monkeypatch.setattr(rt_api, "verify_url_token", lambda _t, _s: uuid.uuid4())
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as ei, client.websocket_connect("/api/ws/anon/tok"):
        pass
    assert ei.value.code == rt_api.CLOSE_FORBIDDEN


def test_anon_invalid_token_closes_4403(monkeypatch: pytest.MonkeyPatch) -> None:
    app, _hub = _make_app(monkeypatch)
    anon = AnonymousSessionUser(
        session_id=uuid.uuid4(),
        operation_id=uuid.uuid4(),
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    monkeypatch.setattr(rt_api, "get_current_anonymous_session", lambda _ws: anon)
    monkeypatch.setattr(rt_api, "verify_url_token", lambda _t, _s: None)
    client = TestClient(app)
    with pytest.raises(WebSocketDisconnect) as ei, client.websocket_connect("/api/ws/anon/tok"):
        pass
    assert ei.value.code == rt_api.CLOSE_FORBIDDEN


# ─── Dispatcher Subscribe ─────────────────────────────────────────────────────


def test_dispatcher_subscribe_authorized(monkeypatch: pytest.MonkeyPatch) -> None:
    tenant = uuid.uuid4()
    op = uuid.uuid4()
    app, _hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_session_user", lambda _ws: _dispatcher(tenant))

    async def _participates(_s: Any, *, tenant_id: uuid.UUID, operation_id: uuid.UUID) -> bool:
        return True

    monkeypatch.setattr(
        "eb_digital.tenants.participation.tenant_participates_in_operation", _participates
    )
    client = TestClient(app)
    with client.websocket_connect("/api/ws/dispatcher") as ws:
        ws.send_json({"action": "subscribe", "data": {"operations": [str(op)]}})
        frame = ws.receive_json()
    assert frame["event_type"] == messages.EVENT_SUBSCRIBED
    assert topic_for(op, KIND_ORDER_STATUS) in frame["payload"]["topics"]


def test_dispatcher_subscribe_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    tenant = uuid.uuid4()
    op = uuid.uuid4()
    app, _hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_session_user", lambda _ws: _dispatcher(tenant))

    async def _participates(_s: Any, *, tenant_id: uuid.UUID, operation_id: uuid.UUID) -> bool:
        return False

    monkeypatch.setattr(
        "eb_digital.tenants.participation.tenant_participates_in_operation", _participates
    )
    client = TestClient(app)
    with client.websocket_connect("/api/ws/dispatcher") as ws:
        ws.send_json({"action": "subscribe", "data": {"operations": [str(op)]}})
        frame = ws.receive_json()
    assert frame["event_type"] == messages.EVENT_ERROR
    assert frame["payload"]["code"] == messages.ERROR_FORBIDDEN


def test_dispatcher_bad_operations_field(monkeypatch: pytest.MonkeyPatch) -> None:
    app, _hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_session_user", lambda _ws: _dispatcher(uuid.uuid4()))
    client = TestClient(app)
    with client.websocket_connect("/api/ws/dispatcher") as ws:
        ws.send_json({"action": "subscribe", "data": {"operations": "not-a-list"}})
        frame = ws.receive_json()
    assert frame["payload"]["code"] == messages.ERROR_BAD_REQUEST


def test_dispatcher_unknown_action(monkeypatch: pytest.MonkeyPatch) -> None:
    app, _hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_session_user", lambda _ws: _dispatcher(uuid.uuid4()))
    client = TestClient(app)
    with client.websocket_connect("/api/ws/dispatcher") as ws:
        ws.send_json({"action": "frobnicate", "data": {}})
        frame = ws.receive_json()
    assert frame["payload"]["code"] == messages.ERROR_UNSUPPORTED_ACTION


def test_dispatcher_unsubscribe(monkeypatch: pytest.MonkeyPatch) -> None:
    tenant = uuid.uuid4()
    op = uuid.uuid4()
    app, _hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_session_user", lambda _ws: _dispatcher(tenant))

    async def _participates(_s: Any, **_kw: Any) -> bool:
        return True

    monkeypatch.setattr(
        "eb_digital.tenants.participation.tenant_participates_in_operation", _participates
    )
    client = TestClient(app)
    with client.websocket_connect("/api/ws/dispatcher") as ws:
        ws.send_json({"action": "subscribe", "data": {"operations": [str(op)]}})
        ws.receive_json()
        ws.send_json({"action": "unsubscribe", "data": {"operations": [str(op)]}})
        frame = ws.receive_json()
    assert frame["event_type"] == messages.EVENT_SUBSCRIBED
    assert frame["payload"]["topics"] == []


# ─── Carer Auto-Subscribe ─────────────────────────────────────────────────────


def test_carer_autosubscribes_assignment(monkeypatch: pytest.MonkeyPatch) -> None:
    tenant = uuid.uuid4()
    op = uuid.uuid4()
    app, hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_session_user", lambda _ws: _carer(tenant))

    async def _list_ops(_s: Any, _tenant_id: uuid.UUID) -> list[uuid.UUID]:
        return [op]

    monkeypatch.setattr("eb_digital.tenants.participation.list_operations_for_tenant", _list_ops)
    client = TestClient(app)
    with client.websocket_connect("/api/ws/carer") as ws:
        # Auto-Subscribe geschieht beim Connect; kurz pollen.
        expected = topic_for(op, KIND_ASSIGNMENT)
        deadline = time.monotonic() + 2.0
        while hub.subscriber_count(expected) == 0 and time.monotonic() < deadline:
            time.sleep(0.02)
        assert hub.subscriber_count(expected) == 1
        # Carer-Aktionen sind nicht unterstützt.
        ws.send_json({"action": "chat", "data": {}})
        frame = ws.receive_json()
    assert frame["payload"]["code"] == messages.ERROR_UNSUPPORTED_ACTION


# ─── Anon ─────────────────────────────────────────────────────────────────────


def test_anon_connect_subscribes_order_status(monkeypatch: pytest.MonkeyPatch) -> None:
    op = uuid.uuid4()
    anon = AnonymousSessionUser(
        session_id=uuid.uuid4(),
        operation_id=op,
        expires_at=datetime.now(UTC) + timedelta(hours=1),
    )
    app, hub = _make_app(monkeypatch)
    monkeypatch.setattr(rt_api, "get_current_anonymous_session", lambda _ws: anon)
    monkeypatch.setattr(rt_api, "verify_url_token", lambda _t, _s: op)
    client = TestClient(app)
    with client.websocket_connect("/api/ws/anon/tok") as ws:
        expected = topic_for(op, KIND_ORDER_STATUS)
        deadline = time.monotonic() + 2.0
        while hub.subscriber_count(expected) == 0 and time.monotonic() < deadline:
            time.sleep(0.02)
        assert hub.subscriber_count(expected) == 1
        ws.send_json({"action": "subscribe", "data": {}})
        frame = ws.receive_json()
    assert frame["payload"]["code"] == messages.ERROR_UNSUPPORTED_ACTION
