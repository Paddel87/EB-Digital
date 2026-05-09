"""ORM models registered with the shared declarative base.

Phase 1 owns only the ``HealthMarker`` sentinel, used to validate the
SQLAlchemy + Alembic setup end-to-end (autogenerate produces a migration,
``alembic upgrade head`` applies it). Real domain models arrive in Phase 2.
"""

from __future__ import annotations

import uuid

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base, TimestampMixin


class HealthMarker(Base, TimestampMixin):
    """Setup-validation sentinel.

    Carrying ``id`` (UUID v4), ``label`` and the timestamp mixin lets us
    exercise UUID columns, the naming convention, the audit defaults and
    Alembic autogenerate without touching the real domain.
    """

    __tablename__ = "health_marker"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    label: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)


__all__ = ["HealthMarker"]
