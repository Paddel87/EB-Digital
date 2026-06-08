"""Tests für ``eb_digital.realtime.connection`` (Schritt 4.4)."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import pytest
from starlette.websockets import WebSocketDisconnect

from eb_digital.realtime import messages
from eb_digital.realtime.connection import (
    KIND_ANON,
    KIND_DISPATCHER,
    Connection,
    heartbeat_loop,
    receive_loop,
    writer_loop,
)


class FakeWebSocket:
    """Minimaler WebSocket-Doppelgänger für die Loop-Tests."""

    def __init__(self, incoming: list[Any] | None = None) -> None:
        self.sent: list[dict[str, Any]] = []
        self._incoming: list[Any] = list(incoming or [])
        self.closed_code: int | None = None
        self.accepted = False

    async def accept(self) -> None:
        self.accepted = True

    async def send_json(self, data: dict[str, Any]) -> None:
        self.sent.append(data)

    async def receive_text(self) -> str:
        if not self._incoming:
            raise WebSocketDisconnect(code=1000)
        item = self._incoming.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    async def close(self, code: int = 1000) -> None:
        self.closed_code = code


def _conn(kind: str = KIND_DISPATCHER, **kw: Any) -> Connection:
    return Connection(websocket=FakeWebSocket(), kind=kind, subject_id=uuid.uuid4(), **kw)


def test_enqueue_returns_false_when_full() -> None:
    conn = _conn()
    # Queue künstlich füllen.
    while True:
        try:
            conn.queue.put_nowait({"x": 1})
        except asyncio.QueueFull:
            break
    assert conn.enqueue({"y": 2}) is False


def test_enqueue_ok() -> None:
    conn = _conn()
    assert conn.enqueue({"y": 2}) is True


def test_accepts_anon_only_own_session() -> None:
    sid = uuid.uuid4()
    conn = _conn(kind=KIND_ANON, anon_session_id=sid)
    assert conn.accepts({"payload": {"anonymous_session_id": str(sid)}}) is True
    assert conn.accepts({"payload": {"anonymous_session_id": str(uuid.uuid4())}}) is False
    assert conn.accepts({"payload": {}}) is False


def test_accepts_non_anon_always_true() -> None:
    conn = _conn(kind=KIND_DISPATCHER)
    assert conn.accepts({"payload": {"anonymous_session_id": str(uuid.uuid4())}}) is True


def test_touch_resets_idle() -> None:
    conn = _conn()
    conn._last_activity -= 100
    assert conn.idle_seconds() > 50
    conn.touch()
    assert conn.idle_seconds() < 1


@pytest.mark.asyncio
async def test_writer_loop_sends_queued_frames() -> None:
    conn = _conn()
    ws: FakeWebSocket = conn.websocket  # type: ignore[assignment]
    conn.enqueue({"hello": "world"})
    task = asyncio.create_task(writer_loop(conn))
    await asyncio.sleep(0.02)
    task.cancel()
    assert {"hello": "world"} in ws.sent


@pytest.mark.asyncio
async def test_heartbeat_closes_on_timeout() -> None:
    conn = _conn()
    ws: FakeWebSocket = conn.websocket  # type: ignore[assignment]
    conn._last_activity -= 100  # weit in der Vergangenheit → Timeout
    await heartbeat_loop(conn, interval=0.01, timeout=0.01)
    assert ws.closed_code is not None


@pytest.mark.asyncio
async def test_heartbeat_sends_ping_when_active() -> None:
    conn = _conn()
    task = asyncio.create_task(heartbeat_loop(conn, interval=0.01, timeout=10.0))
    await asyncio.sleep(0.03)
    task.cancel()
    pings = [conn.queue.get_nowait() for _ in range(conn.queue.qsize())]
    assert any(f["event_type"] == messages.EVENT_PING for f in pings)


@pytest.mark.asyncio
async def test_receive_loop_delegates_action() -> None:
    received: list[tuple[str, dict[str, Any]]] = []

    async def on_action(_conn: Connection, action: str, data: dict[str, Any]) -> None:
        received.append((action, data))

    conn = _conn()
    conn.websocket = FakeWebSocket(['{"action": "subscribe", "data": {"operations": ["x"]}}'])
    await receive_loop(conn, on_action)
    assert received == [("subscribe", {"operations": ["x"]})]


@pytest.mark.asyncio
async def test_receive_loop_bad_json_emits_error() -> None:
    async def on_action(_c: Connection, _a: str, _d: dict[str, Any]) -> None:  # pragma: no cover
        raise AssertionError("should not be called")

    conn = _conn()
    conn.websocket = FakeWebSocket(["{not json"])
    await receive_loop(conn, on_action)
    frame = conn.queue.get_nowait()
    assert frame["event_type"] == messages.EVENT_ERROR
    assert frame["payload"]["code"] == messages.ERROR_BAD_REQUEST


@pytest.mark.asyncio
async def test_receive_loop_pong_is_noop_but_touches() -> None:
    calls: list[str] = []

    async def on_action(
        _c: Connection, action: str, _d: dict[str, Any]
    ) -> None:  # pragma: no cover
        calls.append(action)

    conn = _conn()
    conn._last_activity -= 100
    conn.websocket = FakeWebSocket(['{"action": "pong"}'])
    await receive_loop(conn, on_action)
    assert calls == []
    assert conn.idle_seconds() < 1  # touch() lief


@pytest.mark.asyncio
async def test_receive_loop_returns_on_disconnect() -> None:
    async def on_action(_c: Connection, _a: str, _d: dict[str, Any]) -> None:  # pragma: no cover
        raise AssertionError

    conn = _conn()
    conn.websocket = FakeWebSocket([])  # leeres incoming → sofort Disconnect
    await receive_loop(conn, on_action)  # darf nicht hängen / werfen
