"""Tests für ``eb_digital.realtime.topics`` (Schritt 4.4)."""

from __future__ import annotations

import uuid

from eb_digital.realtime import topics


def test_topic_for_builds_canonical_name() -> None:
    op = uuid.uuid4()
    assert topics.topic_for(op, topics.KIND_ORDER_STATUS) == f"operation.{op}.order_status"


def test_topics_for_kinds_returns_all() -> None:
    op = uuid.uuid4()
    result = topics.topics_for_kinds(op, topics.CARER_KINDS)
    assert result == {
        topics.topic_for(op, topics.KIND_ASSIGNMENT),
        topics.topic_for(op, topics.KIND_CHAT),
    }


def test_parse_topic_roundtrip() -> None:
    op = uuid.uuid4()
    topic = topics.topic_for(op, topics.KIND_BUNDLE)
    assert topics.parse_topic(topic) == (op, topics.KIND_BUNDLE)


def test_parse_topic_rejects_wrong_prefix() -> None:
    assert topics.parse_topic(f"foo.{uuid.uuid4()}.order_status") is None


def test_parse_topic_rejects_unknown_kind() -> None:
    assert topics.parse_topic(f"operation.{uuid.uuid4()}.bogus") is None


def test_parse_topic_rejects_bad_uuid() -> None:
    assert topics.parse_topic("operation.not-a-uuid.order_status") is None


def test_parse_topic_rejects_wrong_arity() -> None:
    assert topics.parse_topic("operation.only_two") is None
    assert topics.parse_topic("operation.a.b.c.d") is None


def test_role_kind_sets() -> None:
    assert {topics.KIND_ORDER_STATUS} == topics.ANON_KINDS
    assert topics.KIND_ORDER_STATUS in topics.DISPATCHER_KINDS
    assert topics.KIND_HELP_ALERT in topics.DISPATCHER_KINDS  # reserviert, aber abonnierbar
    assert topics.TOPIC_PATTERN == "operation.*"
