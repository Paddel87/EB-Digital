"""ORM-Modelle für ``backend/tenants``.

Phase 2 Schritt 2.1: ``Tenant`` (Mandanten-Stammdaten) und
``OperationTenantParticipation`` (Operation↔Tenant-Verknüpfung gemäß
ADR-009 Invariante I1 — kein direkter ``operation.tenant_id``-FK).

Use-Case-Logik (Antrag, Freischaltung, Status-Übergänge, Teilnahme-Filter
für Invariante I2) folgt in Schritt 2.4.

Phase 4 Schritt 4.3a: additive Spalte ``plausibility_default_threshold_m``
(ADR-017, dreistufige Konfigurations-Hierarchie — Tenant-Default zwischen
Plattform-Konstante und Operation-Override).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Final

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base, TimestampMixin

# Tenant-Lebenszyklus: Self-Service-Antrag → Plattform-Admin-Freischaltung →
# optional Deaktivierung (DSGVO-Art. 17). Whitelist statt PostgreSQL-ENUM,
# weil Erweiterungen via einfacher ALTER-Migration möglich bleiben sollen.
TENANT_STATUS_APPLIED: Final[str] = "applied"
TENANT_STATUS_ACTIVE: Final[str] = "active"
TENANT_STATUS_DEACTIVATED: Final[str] = "deactivated"
ALLOWED_TENANT_STATUS: Final[frozenset[str]] = frozenset(
    {TENANT_STATUS_APPLIED, TENANT_STATUS_ACTIVE, TENANT_STATUS_DEACTIVATED}
)

# Rolle eines Mandanten an einer Operation. Phase 1 immer ``owner``;
# ``participant`` ist für Phase X (Verbund-Modus, ADR-009) reserviert.
PARTICIPATION_ROLE_OWNER: Final[str] = "owner"
PARTICIPATION_ROLE_PARTICIPANT: Final[str] = "participant"
ALLOWED_PARTICIPATION_ROLES: Final[frozenset[str]] = frozenset(
    {PARTICIPATION_ROLE_OWNER, PARTICIPATION_ROLE_PARTICIPANT}
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class Tenant(Base, TimestampMixin):
    """Mandant (Berufsverband / Landesverband).

    Phase 1 initial DPolG Bremen. Mandanten-Trennung erfolgt domänenintern;
    Operation↔Tenant-Verknüpfung läuft ausschließlich über
    ``operation_tenant_participation`` (Invariante I1, ADR-009).
    """

    __tablename__ = "tenant"
    __table_args__ = (
        CheckConstraint(
            "status IN ('applied', 'active', 'deactivated')",
            name="status_allowed",
        ),
        # ADR-017: Tenant-Default für die Plausibilitäts-Schwelle. Plattform-
        # Konstanten (Min/Max) garantieren die DB-seitige Bandbreite; Operation-
        # Overrides werden auf demselben Range geprüft (siehe Operation-Modell).
        CheckConstraint(
            "plausibility_default_threshold_m BETWEEN 50 AND 50000",
            name="plausibility_default_threshold_m_range",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Verbandsname zur Anzeige (z. B. „DPolG Bremen"). Unique, weil ein
    # Verband nicht zweimal als Mandant geführt werden soll.
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    # URL-/CLI-tauglicher Bezeichner (z. B. ``dpolg-bremen``). Format-
    # Validierung erfolgt im Use-Case (Schritt 2.4); hier nur Unique +
    # Längenbeschränkung.
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(16), nullable=False)
    applied_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    activated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    deactivated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    # ADR-017 dreistufige Konfigurations-Hierarchie:
    #   Plattform-Konstante (Min/Max-Range, Accuracy-Cutoff)
    #   → Tenant-Default (hier)
    #   → optionaler Operation-Override (``operation.plausibility_threshold_m``).
    # Default 5 000 m (Vision-/project-context-Initialwert).
    plausibility_default_threshold_m: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5000,
        server_default=text("5000"),
    )


class OperationTenantParticipation(Base):
    """Operation↔Tenant-Verknüpfung (alleinige Quelle gemäß I1).

    Composite-PK ``(operation_id, tenant_id)``. Phase 1: genau ein Eintrag
    mit ``role='owner'`` pro Operation, durchgesetzt durch den Partial-
    Unique-Index ``ix_operation_tenant_participation_owner_unique``. Phase
    X (Verbund-Modus) fügt ``role='participant'`` additiv hinzu, ohne den
    Index zu brechen.
    """

    __tablename__ = "operation_tenant_participation"
    __table_args__ = (
        CheckConstraint(
            "role IN ('owner', 'participant')",
            name="role_allowed",
        ),
        # Genau ein Owner pro Operation. ``postgresql_where`` filtert den
        # Index auf Owner-Einträge; Participant-Zeilen sind nicht eindeutig.
        Index(
            "ix_operation_tenant_participation_owner_unique",
            "operation_id",
            unique=True,
            postgresql_where=text("role = 'owner'"),
        ),
        # S10-Spec (architecture.md Abschnitt 4): Lookup-Pfade für die
        # Participation-Funktionen. PK liefert ``(operation_id, tenant_id)``-
        # Index automatisch — wir brauchen zusätzlich:
        #   • ``(tenant_id, operation_id)`` für ``list_operations_for_tenant``
        #   • ``(operation_id, role)`` für ``owners_of_operation``
        # Ergänzt in 2.4 als additive Migration; 2.1-Migration hatte das
        # versehentlich ausgelassen.
        Index(
            "ix_operation_tenant_participation_tenant_id_operation_id",
            "tenant_id",
            "operation_id",
        ),
        Index(
            "ix_operation_tenant_participation_operation_id_role",
            "operation_id",
            "role",
        ),
    )

    operation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("operation.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(String(16), nullable=False)
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )


__all__ = [
    "ALLOWED_PARTICIPATION_ROLES",
    "ALLOWED_TENANT_STATUS",
    "PARTICIPATION_ROLE_OWNER",
    "PARTICIPATION_ROLE_PARTICIPANT",
    "TENANT_STATUS_ACTIVE",
    "TENANT_STATUS_APPLIED",
    "TENANT_STATUS_DEACTIVATED",
    "OperationTenantParticipation",
    "Tenant",
]
