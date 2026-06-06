"""Audit-Log-Infrastruktur (ADR-008 / Regel-011).

Expliziter Aufruf am Ende jedes destruktiven oder konfigurierenden Use-
Cases (Detail-Plan 4.3a-Frage 7A) — kein Decorator-Magic. Audit-Schreiben
läuft im selben Transaktions-Scope wie der Use-Case-Effekt.

Die Action-Type-Whitelist wird hier als ``Final[str]``-Konstanten gepflegt;
4.3b erweitert das Vokabular um die Bündelungs-Aktionen
(``orders_bundled``, ``bundle_dissolved``, ``bundle_cancelled``).
"""

from __future__ import annotations

import uuid
from typing import Any, Final

from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.operations.models import OperationAuditLog

# Action-Type-Whitelist für Phase 4.3a. Strings sind Wire-Format und
# erscheinen 1:1 in ``operation_audit_log.action_type``.
ACTION_OPERATION_OPENED: Final[str] = "operation_opened"
ACTION_OPERATION_CLOSED: Final[str] = "operation_closed"
ACTION_OPERATION_AREA_CHANGED: Final[str] = "operation_area_changed"
ACTION_ACCESS_CODE_TOGGLED: Final[str] = "access_code_toggled"
ACTION_SUPPLY_TRANSPORTER_MODE_CHANGED: Final[str] = "supply_transporter_mode_changed"
ACTION_ORDER_PLACED: Final[str] = "order_placed"
ACTION_ORDER_MODERATION_APPROVED: Final[str] = "order_moderation_approved"
ACTION_ORDER_ASSIGNED: Final[str] = "order_assigned"
ACTION_ORDER_CANCELLED: Final[str] = "order_cancelled"
ACTION_ORDER_COMPLETED: Final[str] = "order_completed"

ALLOWED_ACTION_TYPES_4_3A: Final[frozenset[str]] = frozenset(
    {
        ACTION_OPERATION_OPENED,
        ACTION_OPERATION_CLOSED,
        ACTION_OPERATION_AREA_CHANGED,
        ACTION_ACCESS_CODE_TOGGLED,
        ACTION_SUPPLY_TRANSPORTER_MODE_CHANGED,
        ACTION_ORDER_PLACED,
        ACTION_ORDER_MODERATION_APPROVED,
        ACTION_ORDER_ASSIGNED,
        ACTION_ORDER_CANCELLED,
        ACTION_ORDER_COMPLETED,
    }
)

# Target-Kind-Whitelist. Convention aus ADR-008: bei Operation-Level-
# Aktionen ist ``target_id = operation_id`` und ``target_kind = 'operation'``.
TARGET_OPERATION: Final[str] = "operation"
TARGET_OPERATION_AREA: Final[str] = "operation_area"
TARGET_ORDER: Final[str] = "customer_order"
TARGET_VEHICLE: Final[str] = "vehicle"


class AuditLogger:
    """Schreibt Audit-Einträge in ``operation_audit_log``.

    Die Klasse ist transaktions-agnostisch: ``log`` führt nur ein
    ``session.add(...)`` aus; das Commit liegt beim Aufrufer (Use-Case)
    bzw. der Request-Scoped-DB-Session-Dependency.

    Action-Type wird gegen die Whitelist geprüft, um stillschweigende
    Tippfehler zu vermeiden — eine unbekannte Aktion ist ein Code-Bug,
    kein Daten-Bug, und wird hart abgewiesen.
    """

    def __init__(self, *, allowed_actions: frozenset[str] = ALLOWED_ACTION_TYPES_4_3A) -> None:
        self._allowed_actions = allowed_actions

    async def log(
        self,
        *,
        session: AsyncSession,
        operation_id: uuid.UUID,
        actor_dispatcher_id: uuid.UUID | None,
        action_type: str,
        target_kind: str,
        target_id: uuid.UUID,
        payload: dict[str, Any] | None = None,
    ) -> OperationAuditLog:
        """Hängt einen Audit-Eintrag an die Session.

        Schreibt **nicht** explizit; das Commit erfolgt im Use-Case
        oder über die Request-Scoped-Session.
        """
        if action_type not in self._allowed_actions:
            raise ValueError(
                f"Unknown audit action_type {action_type!r} "
                "(extend ALLOWED_ACTION_TYPES if intentional)."
            )
        entry = OperationAuditLog(
            operation_id=operation_id,
            actor_dispatcher_id=actor_dispatcher_id,
            action_type=action_type,
            target_kind=target_kind,
            target_id=target_id,
            payload=payload,
        )
        session.add(entry)
        await session.flush()
        return entry


__all__ = [
    "ACTION_ACCESS_CODE_TOGGLED",
    "ACTION_OPERATION_AREA_CHANGED",
    "ACTION_OPERATION_CLOSED",
    "ACTION_OPERATION_OPENED",
    "ACTION_ORDER_ASSIGNED",
    "ACTION_ORDER_CANCELLED",
    "ACTION_ORDER_COMPLETED",
    "ACTION_ORDER_MODERATION_APPROVED",
    "ACTION_ORDER_PLACED",
    "ACTION_SUPPLY_TRANSPORTER_MODE_CHANGED",
    "ALLOWED_ACTION_TYPES_4_3A",
    "TARGET_OPERATION",
    "TARGET_OPERATION_AREA",
    "TARGET_ORDER",
    "TARGET_VEHICLE",
    "AuditLogger",
]
