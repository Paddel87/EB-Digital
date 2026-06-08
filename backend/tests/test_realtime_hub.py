"""Tests für ``eb_digital.realtime.hub`` (Schritt 4.4)."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import fakeredis.aioredis
import pytest

from eb_digital.realtime import messages
from eb_digital.realtime.connection import KIND_ANON, KIND_DISPATCHER, Connection
from eb_digital.realtime.hub import WebSocketHub
from eb_digital.realtime.publisher import RealtimePublisher
from eb_digital.realtime.topics import KIND_ORDER_STATUS, topic_for
from tests.test_realtime_connection import FakeWebSocket


def _conn(kind: str = KIND_DISPATCHER, **kw: Any) -> Connection:
    return Connection(websocket=FakeWebSocket(), kind=kind, subject_id=uuid.uuid4(), **kw)


def _wire(topic: str, *, event_type: str = "order_placed", **payload: Any) -> str:
    return messages.wire_message(topic, {"event_type": event_type, **payload}, None)


def test_subscribe_unsubscribe_and_count() -> None:
    hub = WebSocketHub()
    conn = _conn()
    topic = topic_for(uuid.uuid4(), KIND_ORDER_STATUS)
    hub.subscribe(conn, topic)
    assert hub.subscriber_count(topic) == 1
    assert topic in conn.topics
    hub.unsubscribe(conn, topic)
    assert hub.subscriber_count(topic) == 0
    assert topic not in conn.topics


def test_unregister_removes_from_all_topics() -> None:
    hub = WebSocketHub()
    conn = _conn()
    op = uuid.uuid4()
    t1 = topic_for(op, KIND_ORDER_STATUS)
    hub.subscribe(conn, t1)
    hub.register(conn)
    hub.unregister(conn)
    assert hub.subscriber_count(t1) == 0
    assert conn.topics == set()


def test_dispatch_delivers_to_subscriber() -> None:
    hub = WebSocketHub()
    conn = _conn()
    topic = topic_for(uuid.uuid4(), KIND_ORDER_STATUS)
    hub.subscribe(conn, topic)
    delivered = hub.dispatch(topic, _wire(topic, order_id="1"))
    assert delivered == 1
    frame = conn.queue.get_nowait()
    assert frame["event_type"] == "order_placed"
    assert frame["payload"]["order_id"] == "1"


def test_dispatch_no_subscribers() -> None:
    hub = WebSocketHub()
    assert hub.dispatch("operation.x.order_status", _wire("operation.x.order_status")) == 0


def test_dispatch_bad_wire_returns_zero() -> None:
    hub = WebSocketHub()
    conn = _conn()
    topic = topic_for(uuid.uuid4(), KIND_ORDER_STATUS)
    hub.subscribe(conn, topic)
    assert hub.dispatch(topic, "{not json") == 0


def test_dispatch_anon_filter() -> None:
    hub = WebSocketHub()
    sid = uuid.uuid4()
    mine = _conn(kind=KIND_ANON, anon_session_id=sid)
    other = _conn(kind=KIND_ANON, anon_session_id=uuid.uuid4())
    topic = topic_for(uuid.uuid4(), KIND_ORDER_STATUS)
    hub.subscribe(mine, topic)
    hub.subscribe(other, topic)
    raw = messages.wire_message(topic, {"event_type": "x", "anonymous_session_id": str(sid)}, None)
    delivered = hub.dispatch(topic, raw)
    assert delivered == 1
    assert mine.queue.qsize() == 1
    assert other.queue.qsize() == 0


def test_dispatch_counts_only_enqueued() -> None:
    hub = WebSocketHub()
    conn = _conn()
    topic = topic_for(uuid.uuid4(), KIND_ORDER_STATUS)
    hub.subscribe(conn, topic)
    # Queue füllen → enqueue schlägt fehl → 0 zugestellt, kein Crash.
    while True:
        try:
            conn.queue.put_nowait({"x": 1})
        except asyncio.QueueFull:
            break
    assert hub.dispatch(topic, _wire(topic)) == 0


@pytest.mark.asyncio
async def test_listener_end_to_end_through_valkey() -> None:
    """Publish → Valkey-Pub/Sub → Listener → lokaler Fan-out (Detail-Plan 7A)."""
    fake = fakeredis.aioredis.FakeRedis()
    hub = WebSocketHub()
    op = uuid.uuid4()
    topic = topic_for(op, KIND_ORDER_STATUS)
    conn = _conn()
    hub.subscribe(conn, topic)
    await hub.start_listener(fake)
    # Idempotenz: zweiter Start ist ein No-Op.
    await hub.start_listener(fake)

    publisher = RealtimePublisher(fake)
    await publisher.publish(
        topic=topic,
        payload={"event_type": "order_placed", "order_id": "7"},
        tenant_scope=uuid.uuid4(),
    )

    frame = None
    for _ in range(50):
        if conn.queue.qsize():
            frame = conn.queue.get_nowait()
            break
        await asyncio.sleep(0.02)
    await hub.stop_listener()
    await fake.aclose()

    assert frame is not None
    assert frame["event_type"] == "order_placed"
    assert frame["payload"]["order_id"] == "7"


@pytest.mark.asyncio
async def test_stop_listener_without_start_is_safe() -> None:
    hub = WebSocketHub()
    await hub.stop_listener()  # darf nicht werfen
