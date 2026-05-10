"""ORM-Modelle für ``backend/auth``.

Phase 1 hat nur ``PlatformAdmin`` produktiv (Bootstrap-CLI, ADR-004).
Phase 2 Schritt 2.1 ergänzt das Skelett der mandanten-gebundenen Auth-
Entitäten ``Dispatcher`` (Disponent) und ``Carer`` (Betreuer). Login,
Cookie-Sessions, Rate-Limit und Multi-User-Verwaltung folgen in 2.2; die
anonyme Einsatzkraft-Session liegt bewusst in einem eigenen Modul
(``backend/auth_anonymous``, Schritt 2.3).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Final

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base, TimestampMixin

# Erlaubte Werte für ``created_via``. Bootstrap-CLI ist der einzige Pfad in
# Phase 1; ``admin_cli`` deckt zukünftige In-App-Anlage durch einen bereits
# eingerichteten Plattform-Admin (Phase 2) vorab ab, damit das Schema bei
# erster Erweiterung nicht migriert werden muss.
CREATED_VIA_BOOTSTRAP_CLI: Final[str] = "bootstrap_cli"
CREATED_VIA_ADMIN_CLI: Final[str] = "admin_cli"
ALLOWED_CREATED_VIA: Final[frozenset[str]] = frozenset(
    {CREATED_VIA_BOOTSTRAP_CLI, CREATED_VIA_ADMIN_CLI}
)


def _utcnow() -> datetime:
    return datetime.now(UTC)


class PlatformAdmin(Base):
    """Plattform-weiter Administrator-Account (Multi-Tenant-übergreifend).

    Wird via CLI angelegt (ADR-004, Schritt 1.6). Nur ``password_hash``
    persistiert; Klartext-Passwort und Salt werden niemals gespeichert oder
    geloggt.
    """

    __tablename__ = "platform_admin"
    __table_args__ = (
        # Whitelist-Constraint statt PostgreSQL-ENUM, weil Erweiterung um neue
        # Werte mit einer einfachen ALTER-Migration möglich bleibt.
        CheckConstraint(
            "created_via IN ('bootstrap_cli', 'admin_cli')",
            name="created_via_allowed",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    # Argon2id-Hash im PHC-Format ``$argon2id$v=19$m=…,t=…,p=…$<salt>$<hash>``
    # — typische Länge ~100 Zeichen; 255 lässt Spielraum für veränderte Defaults.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    created_via: Mapped[str] = mapped_column(String(32), nullable=False)


class Dispatcher(Base, TimestampMixin):
    """Disponent — mandanten-gebundener Account mit voller Anbieterseiten-Rolle.

    Anbieterseiten-Trennung Pflicht: jeder Disponent gehört zu genau einem
    Mandanten (``tenant_id`` Pflicht). Username ist nicht global unique,
    sondern unique pro Mandant — zwei Mandanten dürfen denselben Spitznamen
    haben. ``email`` ist optional (nur für Reset-Flow); fehlt sie, ist Reset
    durch den Mandanten-Admin-Disponent oder Plattform-Administrator
    erforderlich.

    ``ondelete='RESTRICT'`` auf ``tenant_id`` schützt vor versehentlicher
    Mandanten-Löschung — die DSGVO-Art.-17-Löschung läuft über den
    expliziten Deactivation-Pfad in ``backend/tenants``, nicht über DB-
    Cascade.
    """

    __tablename__ = "dispatcher"
    __table_args__ = (
        UniqueConstraint("tenant_id", "username", name="uq_dispatcher_tenant_id_username"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="RESTRICT"),
        nullable=False,
    )
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Carer(Base, TimestampMixin):
    """Betreuer — mandanten-gebundener Account für mobile PWA.

    Strukturell parallel zu ``Dispatcher`` (eigene Tabelle, weil
    Lebenszyklus und Berechtigungen sich von Disponenten unterscheiden:
    Betreuer-Account ggf. nur für eine Schicht aktiv).
    """

    __tablename__ = "carer"
    __table_args__ = (
        UniqueConstraint("tenant_id", "username", name="uq_carer_tenant_id_username"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="RESTRICT"),
        nullable=False,
    )
    username: Mapped[str] = mapped_column(String(64), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(254), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


__all__ = [
    "ALLOWED_CREATED_VIA",
    "CREATED_VIA_ADMIN_CLI",
    "CREATED_VIA_BOOTSTRAP_CLI",
    "Carer",
    "Dispatcher",
    "PlatformAdmin",
]
