"""Topic-Schema für den Realtime-Hub (Schnittstelle S3 / S9).

Topic-Namen folgen dem Schema ``operation.{operation_id}.{kind}``. Sie sind
zugleich die Valkey-Pub/Sub-Channel-Namen — ein Topic 1:1 ein Channel. Der
Hub abonniert per Pattern ``operation.*`` (Redis-Glob ``*`` matcht auch ``.``)
und routet anhand des Channel-Namens an die lokalen WebSocket-Abonnenten.

`help_alert` und `chat` sind in Phase 4 reserviert (kein Produzent bis
Phase 5/6, Detail-Plan 4.4-8A); ihre Topic-Namen stehen aber bereits fest,
damit spätere Phasen additiv andocken.
"""

from __future__ import annotations

import uuid
from typing import Final

TOPIC_PREFIX: Final[str] = "operation"

KIND_LIFECYCLE: Final[str] = "lifecycle"
KIND_ORDER_STATUS: Final[str] = "order_status"
KIND_ASSIGNMENT: Final[str] = "assignment"
KIND_AUDIT_LOG: Final[str] = "audit_log"
KIND_BUNDLE: Final[str] = "bundle"
KIND_HELP_ALERT: Final[str] = "help_alert"  # reserviert (Spike K, Phase 5)
KIND_CHAT: Final[str] = "chat"  # reserviert (Phase 6)

ALL_TOPIC_KINDS: Final[frozenset[str]] = frozenset(
    {
        KIND_LIFECYCLE,
        KIND_ORDER_STATUS,
        KIND_ASSIGNMENT,
        KIND_AUDIT_LOG,
        KIND_BUNDLE,
        KIND_HELP_ALERT,
        KIND_CHAT,
    }
)

# Rollen-Topic-Mengen (Detail-Plan 4.4-3A):
#   • Disponent: alle Topic-Arten teilnehmender Operationen (audit-/lage-zentral).
#   • Carer: Auftrags-Zuweisungen + Mandanten-Chat (S9).
#   • Anon-Einsatzkraft: nur Auftragsstatus der eigenen Operation, zusätzlich
#     server-seitig nach ``session_id`` gefiltert.
DISPATCHER_KINDS: Final[frozenset[str]] = ALL_TOPIC_KINDS
CARER_KINDS: Final[frozenset[str]] = frozenset({KIND_ASSIGNMENT, KIND_CHAT})
ANON_KINDS: Final[frozenset[str]] = frozenset({KIND_ORDER_STATUS})

# Valkey-Pattern für den Hub-Listener (PSUBSCRIBE).
TOPIC_PATTERN: Final[str] = f"{TOPIC_PREFIX}.*"


def topic_for(operation_id: uuid.UUID, kind: str) -> str:
    """Baue den Topic/Channel-Namen für ``operation_id`` und ``kind``."""
    return f"{TOPIC_PREFIX}.{operation_id}.{kind}"


def topics_for_kinds(operation_id: uuid.UUID, kinds: frozenset[str]) -> set[str]:
    """Liefert die Topic-Namen einer Operation für die gegebene Kind-Menge."""
    return {topic_for(operation_id, kind) for kind in kinds}


def parse_topic(topic: str) -> tuple[uuid.UUID, str] | None:
    """Zerlege ``operation.{uuid}.{kind}`` in ``(operation_id, kind)``.

    Liefert ``None`` bei Schema-Verstoß oder unbekannter Kind/UUID — der
    Hub verwirft solche Channel-Nachrichten still.
    """
    parts = topic.split(".")
    if len(parts) != 3 or parts[0] != TOPIC_PREFIX:
        return None
    _, raw_id, kind = parts
    if kind not in ALL_TOPIC_KINDS:
        return None
    try:
        operation_id = uuid.UUID(raw_id)
    except ValueError:
        return None
    return operation_id, kind


__all__ = [
    "ALL_TOPIC_KINDS",
    "ANON_KINDS",
    "CARER_KINDS",
    "DISPATCHER_KINDS",
    "KIND_ASSIGNMENT",
    "KIND_AUDIT_LOG",
    "KIND_BUNDLE",
    "KIND_CHAT",
    "KIND_HELP_ALERT",
    "KIND_LIFECYCLE",
    "KIND_ORDER_STATUS",
    "TOPIC_PATTERN",
    "TOPIC_PREFIX",
    "parse_topic",
    "topic_for",
    "topics_for_kinds",
]
