"""ORM-Modelle für ``backend/operations``.

Phase 2 Schritt 2.1: ``Operation`` (Einsatz, ohne direkte Tenant-FK gemäß
ADR-009 Invariante I1) und ``OperationAuditLog`` (Strukturskelett gemäß
ADR-008 — Multi-Disponent ohne Lead, vollständiges Audit-Log).

Die Operation↔Tenant-Verknüpfung läuft ausschließlich über
``operation_tenant_participation`` (siehe ``eb_digital.tenants.models``).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any, Final

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base, TimestampMixin

# Operation-Lebenszyklus. Whitelist-Constraint statt PostgreSQL-ENUM
# (Erweiterungen via einfacher ALTER-Migration).
OPERATION_STATUS_PLANNED: Final[str] = "planned"
OPERATION_STATUS_ACTIVE: Final[str] = "active"
OPERATION_STATUS_CLOSED: Final[str] = "closed"
ALLOWED_OPERATION_STATUS: Final[frozenset[str]] = frozenset(
    {OPERATION_STATUS_PLANNED, OPERATION_STATUS_ACTIVE, OPERATION_STATUS_CLOSED}
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Operation(Base, TimestampMixin):
    """Einsatz (zeitlich begrenzte Großlage).

    Verknüpfung zu Mandanten ausschließlich über
    ``operation_tenant_participation`` (Invariante I1, ADR-009). Phase 1
    hat genau einen Owner-Eintrag pro Operation; Phase X (Verbund-Modus)
    erweitert additiv um Participant-Einträge.

    Der ``access_code_hash`` speichert den Argon2id-Hash des Crockford-
    Base32-AccessCodes (ADR-005). Klartext wird nie persistiert; Verify
    läuft konstant-zeitig (Regel-006).
    """

    __tablename__ = "operation"
    __table_args__ = (
        CheckConstraint(
            "status IN ('planned', 'active', 'closed')",
            name="status_allowed",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    # Stadt-/Region-Label vom Disponenten beim Eröffnen gesetzt
    # (z. B. „Bremen Innenstadt"). Quelle für ADR-006-Aggregat.
    city_label: Mapped[str] = mapped_column(String(120), nullable=False)
    # Kryptographisch zufälliger Token für die Einsatzkraft-URL.
    # Generierung via ``itsdangerous`` in Schritt 2.3.
    url_token: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    # Argon2id-PHC-Hash des AccessCodes; nullable, weil Code opt-in ist.
    access_code_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    access_code_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    opened_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    closed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class OperationAuditLog(Base):
    """Audit-Log-Eintrag für eine Operation (ADR-008).

    Eine Zeile pro destruktiver oder konfigurierender Aktion. Audit-Log
    ist immutable — kein ``updated_at``. ``actor_dispatcher_id`` ist
    nullable und ``ON DELETE SET NULL``, damit DSGVO-Anonymisierung den
    Personenbezug entfernen kann, ohne den Audit-Eintrag selbst zu
    löschen.

    Das Action-Vokabular wächst mit Phase 4 (``backend/operations`` Use-
    Cases); deshalb in Phase 2.1 kein DB-CHECK auf ``action_type``,
    sondern eine String-Spalte. Ein CHECK-Constraint kann später additiv
    via Migration ergänzt werden, sobald das Vokabular stabil ist.
    """

    __tablename__ = "operation_audit_log"
    __table_args__ = (
        # Standard-Query: „letzte Audit-Einträge einer Operation".
        Index(
            "ix_operation_audit_log_operation_id_at",
            "operation_id",
            "at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operation.id", ondelete="CASCADE"),
        nullable=False,
    )
    actor_dispatcher_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("dispatcher.id", ondelete="SET NULL"),
        nullable=True,
    )
    action_type: Mapped[str] = mapped_column(String(64), nullable=False)
    at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    target_kind: Mapped[str] = mapped_column(String(32), nullable=False)
    # Convention: bei Operation-Level-Aktionen ``target_id = operation_id``.
    target_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    # Aktion-spezifische Detail-Daten ohne PII (ADR-008-Konsequenz).
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)


__all__ = [
    "ALLOWED_OPERATION_STATUS",
    "OPERATION_STATUS_ACTIVE",
    "OPERATION_STATUS_CLOSED",
    "OPERATION_STATUS_PLANNED",
    "Operation",
    "OperationAuditLog",
]
