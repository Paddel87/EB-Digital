"""Tests für ``eb_digital.realtime.publisher`` (Schritt 4.4)."""

from __future__ import annotations

import json
import uuid

import fakeredis.aioredis
import pytest

from eb_digital.realtime.publisher import RealtimePublisher
from eb_digital.realtime.topics import KIND_ORDER_STATUS, topic_for


@pytest.mark.asyncio
async def test_publish_writes_to_valkey_channel() -> None:
    fake = fakeredis.aioredis.FakeRedis()
    topic = topic_for(uuid.uuid4(), KIND_ORDER_STATUS)
    ps = fake.pubsub()
    await ps.subscribe(topic)

    publisher = RealtimePublisher(fake)
    tenant = uuid.uuid4()
    await publisher.publish(
        topic=topic,
        payload={"event_type": "order_placed", "order_id": "1"},
        tenant_scope=tenant,
    )

    message = None
    for _ in range(50):
        m = await ps.get_message(ignore_subscribe_messages=True, timeout=0.05)
        if m and m.get("type") == "message":
            message = m
            break
    await ps.aclose()
    await fake.aclose()

    assert message is not None
    body = json.loads(message["data"])
    assert body["topic"] == topic
    assert body["event_type"] == "order_placed"
    assert body["tenant_scope"] == str(tenant)
    assert body["payload"]["order_id"] == "1"


@pytest.mark.asyncio
async def test_publish_tenant_scope_none() -> None:
    fake = fakeredis.aioredis.FakeRedis()
    topic = topic_for(uuid.uuid4(), KIND_ORDER_STATUS)
    ps = fake.pubsub()
    await ps.subscribe(topic)
    publisher = RealtimePublisher(fake)
    await publisher.publish(topic=topic, payload={"event_type": "x"}, tenant_scope=None)
    message = None
    for _ in range(50):
        m = await ps.get_message(ignore_subscribe_messages=True, timeout=0.05)
        if m and m.get("type") == "message":
            message = m
            break
    await ps.aclose()
    await fake.aclose()
    assert message is not None
    assert json.loads(message["data"])["tenant_scope"] is None
