"""Nachrichten-Schema für den Realtime-Hub (Schnittstelle S9).

Zwei Richtungen:

* **Server → Client** (an die WebSocket): ``{topic, event_type, payload, ts}``.
  Fehler werden als reguläres Frame mit ``event_type="error"`` zugestellt
  (kein Connection-Drop, Detail-Plan 4.4-3A/8A).
* **Client → Server**: ``{action, data}`` mit ``action`` aus
  ``subscribe|unsubscribe|pong``. ``chat``/``gps_push`` sind reserviert
  (Phase 6) und werden in Phase 4 mit einem Fehler-Frame quittiert.

Die **Wire-Nachricht** auf dem Valkey-Channel ist das Server-Frame plus
``tenant_scope`` (intern, wird beim Fan-out an Clients entfernt).
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any, Final

ACTION_SUBSCRIBE: Final[str] = "subscribe"
ACTION_UNSUBSCRIBE: Final[str] = "unsubscribe"
ACTION_PONG: Final[str] = "pong"
ACTION_CHAT: Final[str] = "chat"  # reserviert (Phase 6)
ACTION_GPS_PUSH: Final[str] = "gps_push"  # reserviert (Phase 6)

SUPPORTED_ACTIONS: Final[frozenset[str]] = frozenset(
    {ACTION_SUBSCRIBE, ACTION_UNSUBSCRIBE, ACTION_PONG}
)

EVENT_PING: Final[str] = "ping"
EVENT_ERROR: Final[str] = "error"
EVENT_SUBSCRIBED: Final[str] = "subscribed"

ERROR_BAD_REQUEST: Final[str] = "bad_request"
ERROR_FORBIDDEN: Final[str] = "forbidden"
ERROR_UNSUPPORTED_ACTION: Final[str] = "unsupported_action"


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def client_frame(
    topic: str | None, event_type: str | None, payload: dict[str, Any]
) -> dict[str, Any]:
    """Baue ein Server→Client-Frame gemäß S9."""
    return {
        "topic": topic,
        "event_type": event_type,
        "payload": payload,
        "ts": _utcnow_iso(),
    }


def error_frame(code: str, message: str, *, topic: str | None = None) -> dict[str, Any]:
    """Fehler-Frame (kein Drop) mit ``event_type='error'``."""
    return client_frame(topic, EVENT_ERROR, {"code": code, "message": message})


def ping_frame() -> dict[str, Any]:
    """Heartbeat-Ping (Detail-Plan 4.4-6A)."""
    return client_frame(None, EVENT_PING, {})


def subscribed_frame(topics: list[str]) -> dict[str, Any]:
    """Bestätigung erfolgreicher Subscriptions."""
    return client_frame(None, EVENT_SUBSCRIBED, {"topics": topics})


def wire_message(topic: str, payload: dict[str, Any], tenant_scope: str | None) -> str:
    """Serialisiere die Valkey-Wire-Nachricht für ``topic``.

    ``payload`` enthält das ``event_type``-Feld (von ``backend/operations``
    gesetzt); es wird zusätzlich auf Top-Level gespiegelt, damit der Hub
    nicht ins Payload greifen muss.
    """
    message = {
        "topic": topic,
        "event_type": payload.get("event_type"),
        "payload": payload,
        "ts": _utcnow_iso(),
        "tenant_scope": tenant_scope,
    }
    return json.dumps(message, separators=(",", ":"))


def parse_wire_message(raw: bytes | str) -> dict[str, Any] | None:
    """Parse eine Valkey-Wire-Nachricht; ``None`` bei ungültigem JSON/Schema."""
    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    return data


def client_frame_from_wire(message: dict[str, Any]) -> dict[str, Any]:
    """Reduziere eine Wire-Nachricht auf das Client-Frame (ohne ``tenant_scope``)."""
    return {
        "topic": message.get("topic"),
        "event_type": message.get("event_type"),
        "payload": message.get("payload") or {},
        "ts": message.get("ts"),
    }


__all__ = [
    "ACTION_CHAT",
    "ACTION_GPS_PUSH",
    "ACTION_PONG",
    "ACTION_SUBSCRIBE",
    "ACTION_UNSUBSCRIBE",
    "ERROR_BAD_REQUEST",
    "ERROR_FORBIDDEN",
    "ERROR_UNSUPPORTED_ACTION",
    "EVENT_ERROR",
    "EVENT_PING",
    "EVENT_SUBSCRIBED",
    "SUPPORTED_ACTIONS",
    "client_frame",
    "client_frame_from_wire",
    "error_frame",
    "parse_wire_message",
    "ping_frame",
    "subscribed_frame",
    "wire_message",
]
