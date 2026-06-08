"""Echter Realtime-Publisher (Schnittstelle S3, Detail-Plan 4.4-10A).

Ersetzt den No-Op-``RealtimeAdapter`` aus 4.3a. ``backend/operations``
ruft ``publish(topic, payload, tenant_scope)`` über die unveränderte
S3-Signatur auf; hier wird die Nachricht auf den gleichnamigen Valkey-
Pub/Sub-Channel veröffentlicht. Der Hub-Listener (`hub.py`) liest sie per
``PSUBSCRIBE operation.*`` wieder ein und fan-outet an lokale WebSockets.

PII: ``payload`` enthält keine Roh-Koordinaten (ADR-008, ``project-context``
§6); Standort-Felder kommen als Tile-Hash. Das strukturierte Log-Event
nutzt den zentralen JSON-Logger, dessen Redaction-Liste sensible Felder
zusätzlich absichert.
"""

from __future__ import annotations

import uuid

from redis.asyncio import Redis

from eb_digital.logging import get_logger
from eb_digital.realtime.messages import wire_message

logger = get_logger(__name__)


class RealtimePublisher:
    """Veröffentlicht Operations-Events auf Valkey-Pub/Sub.

    Erfüllt die S3-``RealtimePublisher``-Protocol aus
    ``eb_digital.operations.realtime_adapter`` strukturell (gleiche
    ``publish``-Signatur) — ``backend/operations`` hängt nicht an dieser
    Klasse, sondern an der Protocol.
    """

    def __init__(self, valkey: Redis) -> None:
        self._valkey = valkey

    async def publish(
        self,
        *,
        topic: str,
        payload: dict[str, object],
        tenant_scope: uuid.UUID | None,
    ) -> None:
        scope = str(tenant_scope) if tenant_scope is not None else None
        await self._valkey.publish(topic, wire_message(topic, dict(payload), scope))
        logger.info(
            "realtime.publish",
            extra={
                "realtime_topic": topic,
                "realtime_event_type": payload.get("event_type"),
                "realtime_tenant_scope": scope,
            },
        )


__all__ = ["RealtimePublisher"]
