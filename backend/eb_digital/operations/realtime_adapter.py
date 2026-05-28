"""Stub-Adapter für ``backend/realtime`` (Detail-Plan 4.3a-Frage 6A).

In 4.3a ist ``backend/realtime`` noch nicht implementiert; trotzdem
emittieren die Operations-Use-Cases ihre Events bereits über diesen
Adapter. ``publish`` ist hier ein No-Op-Logger; in 4.4 wird die
Implementierung durch Valkey-Pub/Sub ersetzt — die Aufrufstellen in
``use_cases.py`` bleiben unverändert.

S3 (Operations Event Bus → Realtime) bleibt deshalb in 4.3a
``[VORLÄUFIG]`` — Konsument fehlt. Sie wird mit 4.4 belastbar.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class RealtimeAdapter:
    """Adapter zur ``backend/realtime``-Pub/Sub-Schicht.

    4.3a-Implementierung schreibt nur ein strukturiertes Log-Event
    (PII-frei, Topic-Name plus Event-Type). Keine Netzwerk-Aufrufe.
    4.4 ersetzt diesen Adapter durch einen Valkey-basierten Pub/Sub-
    Adapter mit identischer Signatur.
    """

    async def publish(
        self,
        *,
        topic: str,
        payload: dict[str, Any],
        tenant_scope: uuid.UUID | None,
    ) -> None:
        """Veröffentlicht ein Event.

        In 4.3a No-Op + strukturiertes Log; in 4.4 echte Pub/Sub-Brücke.

        ``payload`` enthält keinen PII; siehe ADR-008 und
        ``project-context.md`` §6 (PII-Redaction).
        """
        logger.info(
            "operations.realtime.publish.stub",
            extra={
                "realtime_topic": topic,
                "realtime_event_type": payload.get("event_type"),
                "realtime_tenant_scope": str(tenant_scope) if tenant_scope else None,
            },
        )


__all__ = ["RealtimeAdapter"]
