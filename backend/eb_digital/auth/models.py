"""ORM-Modelle für ``backend/auth``.

Phase 1: nur ``PlatformAdmin``. Disponent-, Betreuer- und Einsatzkraft-
Modelle folgen in Phase 2 zusammen mit der vollen Auth-Logik.

Schema-Felder ergeben sich aus Fahrplan-Schritt 1.6:
``id``, ``username`` (unique), ``password_hash``, ``created_at``, ``created_via``.
``updated_at`` ist hier bewusst nicht enthalten — Passwort-Rotation und
weitere Audit-Spalten kommen mit dem produktiven Auth-Modul in Phase 2.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Final

from sqlalchemy import CheckConstraint, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base

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


__all__ = [
    "ALLOWED_CREATED_VIA",
    "CREATED_VIA_ADMIN_CLI",
    "CREATED_VIA_BOOTSTRAP_CLI",
    "PlatformAdmin",
]
