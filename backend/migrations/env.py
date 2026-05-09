"""Alembic environment running migrations against the async engine."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from eb_digital.db import (
    Base,
    models,  # noqa: F401  # register ORM models with metadata
)
from eb_digital.settings import get_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _resolved_url() -> str:
    settings = get_settings()
    return settings.database_url


def run_migrations_offline() -> None:
    """Generate SQL without a live database connection."""
    context.configure(
        url=_resolved_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def _run_sync_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations against a live async engine."""
    cfg = config.get_section(config.config_ini_section) or {}
    cfg["sqlalchemy.url"] = _resolved_url()

    engine = async_engine_from_config(cfg, prefix="sqlalchemy.", poolclass=pool.NullPool)

    async with engine.connect() as connection:
        await connection.run_sync(_run_sync_migrations)

    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
