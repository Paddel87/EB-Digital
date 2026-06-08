"""S3-Publisher-Vertrag für ``backend/operations`` (Detail-Plan 4.4-10A).

``backend/operations`` hängt **nicht** an der konkreten Realtime-
Implementierung, sondern an der ``RealtimePublisher``-Protocol hier. Den
echten, Valkey-basierten Publisher liefert ``backend/realtime`` (er erfüllt
die Protocol strukturell); ``app.state.realtime_publisher`` wird in
``operations/api.py`` injiziert.

``NullRealtimePublisher`` (alias ``RealtimeAdapter`` für Abwärtskompatibilität
mit den 4.3a/4.3b-Tests) ist ein No-Op mit strukturiertem Log — Fallback für
Test-Kontexte ohne aktiven Hub. Bis Schritt 4.4 war dieser No-Op die
produktive Implementierung; jetzt ist er reiner Test-/Fallback-Pfad.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any, Protocol, runtime_checkable

logger = logging.getLogger(__name__)


@runtime_checkable
class RealtimePublisher(Protocol):
    """S3-Vertrag: veröffentliche ein Operations-Event an ``backend/realtime``."""

    async def publish(
        self,
        *,
        topic: str,
        payload: dict[str, Any],
        tenant_scope: uuid.UUID | None,
    ) -> None: ...


class NullRealtimePublisher:
    """No-Op-Publisher (Fallback/Test). Schreibt nur ein PII-freies Log-Event."""

    async def publish(
        self,
        *,
        topic: str,
        payload: dict[str, Any],
        tenant_scope: uuid.UUID | None,
    ) -> None:
        logger.info(
            "operations.realtime.publish.noop",
            extra={
                "realtime_topic": topic,
                "realtime_event_type": payload.get("event_type"),
                "realtime_tenant_scope": str(tenant_scope) if tenant_scope else None,
            },
        )


# Abwärtskompatibler Alias: 4.3a/4.3b-Tests konstruieren ``RealtimeAdapter()``.
RealtimeAdapter = NullRealtimePublisher


__all__ = ["NullRealtimePublisher", "RealtimeAdapter", "RealtimePublisher"]
