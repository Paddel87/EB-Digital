"""Tests for the database layer (engine, session factory, base, mixin)."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from eb_digital.db import (
    NAMING_CONVENTION,
    Base,
    TimestampMixin,
    create_db_engine,
    create_session_factory,
    metadata,
)


def test_metadata_uses_shared_naming_convention() -> None:
    assert metadata.naming_convention == NAMING_CONVENTION


def test_base_metadata_is_shared_metadata() -> None:
    assert Base.metadata is metadata


def test_naming_convention_covers_all_constraint_kinds() -> None:
    for key in ("ix", "uq", "ck", "fk", "pk"):
        assert key in NAMING_CONVENTION


def test_create_db_engine_returns_async_engine() -> None:
    engine = create_db_engine("postgresql+asyncpg://u:p@localhost/db")
    try:
        assert isinstance(engine, AsyncEngine)
        assert engine.url.get_backend_name() == "postgresql"
        assert engine.url.get_driver_name() == "asyncpg"
    finally:
        # `dispose()` is a coroutine on AsyncEngine; sync_engine.dispose() is
        # the sync equivalent and is safe before any connection has opened.
        engine.sync_engine.dispose()


def test_create_db_engine_echo_default_is_false() -> None:
    engine = create_db_engine("postgresql+asyncpg://u:p@localhost/db")
    try:
        assert engine.echo is False
    finally:
        engine.sync_engine.dispose()


def test_create_db_engine_echo_can_be_enabled() -> None:
    engine = create_db_engine("postgresql+asyncpg://u:p@localhost/db", echo=True)
    try:
        assert engine.echo is True
    finally:
        engine.sync_engine.dispose()


def test_create_session_factory_returns_async_sessionmaker() -> None:
    engine = create_db_engine("postgresql+asyncpg://u:p@localhost/db")
    try:
        factory = create_session_factory(engine)
        assert isinstance(factory, async_sessionmaker)
        assert factory.class_ is AsyncSession
        assert factory.kw["expire_on_commit"] is False
    finally:
        engine.sync_engine.dispose()


def test_session_factory_emits_async_sessions() -> None:
    engine = create_db_engine("postgresql+asyncpg://u:p@localhost/db")
    try:
        factory = create_session_factory(engine)
        session = factory()
        try:
            assert isinstance(session, AsyncSession)
        finally:
            # Closing an unconnected AsyncSession is a no-op but keeps the
            # lifecycle symmetric.
            session.sync_session.close()
    finally:
        engine.sync_engine.dispose()


@pytest.mark.asyncio
async def test_engine_dispose_releases_resources() -> None:
    """Dispose-without-connect path must not leak or raise."""
    engine = create_db_engine("postgresql+asyncpg://u:p@localhost/db")
    await engine.dispose()


def test_timestamp_mixin_exposes_audit_columns() -> None:
    created_at = TimestampMixin.__dict__["created_at"].column
    updated_at = TimestampMixin.__dict__["updated_at"].column
    assert created_at.nullable is False
    assert updated_at.nullable is False
    assert created_at.type.timezone is True
    assert updated_at.type.timezone is True


def test_timestamp_mixin_default_is_utc_aware() -> None:
    # The mixin's column default is the module-level `_utcnow` callable. We
    # invoke it via the column default to confirm UTC-awareness without
    # needing a real INSERT.
    from eb_digital.db import _utcnow

    now = _utcnow()
    assert isinstance(now, datetime)
    assert now.tzinfo is UTC


def test_timestamp_mixin_updated_at_has_onupdate() -> None:
    column = TimestampMixin.__dict__["updated_at"]
    assert column.column.onupdate is not None
