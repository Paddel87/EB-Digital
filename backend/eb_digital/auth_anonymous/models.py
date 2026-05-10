"""ORM-Modell für ``backend/auth_anonymous``.

Phase 2 Schritt 2.3: ``AnonymousSession`` — anonyme Bezieher-Session, an
``operation_id`` gebunden, ohne Identitäts-PII (Vision-Constraint),
24-h-Hard-Cap-Ablauf zusätzlich zur Operation-Status-Bindung.

Bewusste Design-Entscheidungen:
  • **Kein Tenant-FK.** Die Bezieher-Seite ist mandantenneutral; der
    Mandanten-Bezug entsteht indirekt über die Operation
    (``operation_tenant_participation`` mit ``role='owner'``).
  • **Kein ``client_ip_hash``.** Vision-Constraint „keine PII" wird strikt
    gezogen; Rate-Limit-Counter im Valkey (mit 15-min-TTL) ist die einzige
    IP-Berührung im Anon-Pfad. Forensik bei Missbrauchsverdacht müsste
    additiv per ADR ergänzt werden.
  • **``ON DELETE CASCADE`` auf ``operation_id``.** Operation-Löschung
    räumt Anon-Sessions mit ab (analog ``operation_audit_log``).
  • **24-h-Hard-Cap auf ``expires_at``.** Defense-in-depth gegen vergessene
    parkende Sessions auf alten Geräten; Default ist
    ``_utcnow() + timedelta(hours=24)`` (Patrick freigegeben 2026-05-11
    als Frage-3-B).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Final

from sqlalchemy import DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base

ANONYMOUS_SESSION_HARD_CAP: Final[timedelta] = timedelta(hours=24)


def _utcnow() -> datetime:
    return datetime.now(UTC)


def _default_expires_at() -> datetime:
    return _utcnow() + ANONYMOUS_SESSION_HARD_CAP


class AnonymousSession(Base):
    """Anonyme Bezieher-Session für eine Operation.

    Cleanup abgelaufener Sessions ist Phase-4-Aufgabe (Procrastinate-Job in
    ``backend/retention``); in Phase 2.3 reicht der Read-Pfad mit
    Ablauf-Check.
    """

    __tablename__ = "anonymous_session"
    __table_args__ = (
        # Standard-Query: „aktive Sessions einer Operation" + Cleanup-Job.
        Index(
            "ix_anonymous_session_operation_id",
            "operation_id",
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_default_expires_at,
    )


__all__ = [
    "ANONYMOUS_SESSION_HARD_CAP",
    "AnonymousSession",
]
