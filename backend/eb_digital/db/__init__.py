"""Database access layer.

Provides the SQLAlchemy 2.0 async engine factory, an async session factory,
the declarative base with a deterministic naming convention for constraints,
and a timestamp mixin for audit columns.

The naming convention is required by Alembic's ``compare_type`` /
``render_as_batch`` workflows so that auto-generated migrations produce
stable constraint names across environments.
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

NAMING_CONVENTION: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""

    metadata = metadata


def _utcnow() -> datetime:
    return datetime.now(UTC)


class TimestampMixin:
    """Adds ``created_at`` and ``updated_at`` audit columns in UTC.

    Default values are produced in Python rather than via ``server_default``
    so tests can rely on them without a live database round-trip.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        onupdate=_utcnow,
    )


def create_db_engine(database_url: str, *, echo: bool = False) -> AsyncEngine:
    """Build the async engine for the given URL.

    Connection pooling defaults are SQLAlchemy's; tuning is deferred until a
    real workload exists (Phase 7 STABILISIERUNG).
    """
    return create_async_engine(database_url, echo=echo, future=True)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Build an async session factory bound to ``engine``.

    ``expire_on_commit=False`` matches FastAPI request-scoped patterns where
    response models access attributes after commit.
    """
    return async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


__all__ = [
    "NAMING_CONVENTION",
    "Base",
    "TimestampMixin",
    "create_db_engine",
    "create_session_factory",
    "metadata",
]
