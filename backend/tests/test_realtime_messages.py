"""Tests für ``eb_digital.realtime.messages`` (Schritt 4.4)."""

from __future__ import annotations

import json

from eb_digital.realtime import messages


def test_client_frame_shape() -> None:
    frame = messages.client_frame("operation.x.order_status", "order_placed", {"order_id": "1"})
    assert frame["topic"] == "operation.x.order_status"
    assert frame["event_type"] == "order_placed"
    assert frame["payload"] == {"order_id": "1"}
    assert isinstance(frame["ts"], str)


def test_error_frame() -> None:
    frame = messages.error_frame(messages.ERROR_FORBIDDEN, "nope", topic="t")
    assert frame["event_type"] == messages.EVENT_ERROR
    assert frame["topic"] == "t"
    assert frame["payload"] == {"code": messages.ERROR_FORBIDDEN, "message": "nope"}


def test_ping_and_subscribed_frames() -> None:
    assert messages.ping_frame()["event_type"] == messages.EVENT_PING
    sub = messages.subscribed_frame(["a", "b"])
    assert sub["event_type"] == messages.EVENT_SUBSCRIBED
    assert sub["payload"] == {"topics": ["a", "b"]}


def test_wire_roundtrip() -> None:
    payload = {"event_type": "order_placed", "order_id": "42", "anonymous_session_id": "s1"}
    raw = messages.wire_message("operation.o.order_status", payload, "tenant-1")
    parsed = messages.parse_wire_message(raw)
    assert parsed is not None
    assert parsed["topic"] == "operation.o.order_status"
    assert parsed["event_type"] == "order_placed"
    assert parsed["tenant_scope"] == "tenant-1"
    assert parsed["payload"] == payload


def test_client_frame_from_wire_drops_tenant_scope() -> None:
    raw = messages.wire_message("operation.o.order_status", {"event_type": "x"}, "tenant-1")
    parsed = messages.parse_wire_message(raw)
    assert parsed is not None
    frame = messages.client_frame_from_wire(parsed)
    assert "tenant_scope" not in frame
    assert frame["topic"] == "operation.o.order_status"
    assert frame["event_type"] == "x"


def test_parse_wire_message_rejects_garbage() -> None:
    assert messages.parse_wire_message("{not json") is None
    assert messages.parse_wire_message(json.dumps([1, 2, 3])) is None


def test_supported_actions() -> None:
    assert messages.ACTION_SUBSCRIBE in messages.SUPPORTED_ACTIONS
    assert messages.ACTION_CHAT not in messages.SUPPORTED_ACTIONS
