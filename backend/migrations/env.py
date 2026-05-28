"""Alembic environment running migrations against the async engine."""

from __future__ import annotations

import asyncio
from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from eb_digital.auth import models as _auth_models  # noqa: F401  # register ORM models
from eb_digital.auth_anonymous import (  # noqa: F401  # register ORM models
    models as _auth_anonymous_models,
)
from eb_digital.catalog import models as _catalog_models  # noqa: F401  # register ORM models
from eb_digital.db import (
    Base,
    models,  # noqa: F401  # register ORM models with metadata
)
from eb_digital.operations import models as _operations_models  # noqa: F401  # register ORM models
from eb_digital.settings import get_settings
from eb_digital.tenants import models as _tenants_models  # noqa: F401  # register ORM models

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Procrastinate verwaltet seine eigenen Tabellen, Funktionen und Typen
# (Schritt 1.5, Migration ``add_procrastinate_schema``). Sie tauchen nicht in
# unseren ORM-Modellen auf, sind aber in der Datenbank vorhanden — Autogenerate
# und ``alembic check`` würden sonst Drop-Operationen vorschlagen.
_PROCRASTINATE_PREFIX = "procrastinate_"


def _include_object(
    object_: Any,  # noqa: ANN401  # alembic callback signature uses Any
    name: str | None,
    type_: str,
    reflected: bool,  # alembic callback signature
    compare_to: Any,  # noqa: ANN401  # alembic callback signature
) -> bool:
    # ``reflected`` and ``compare_to`` are part of the alembic callback signature;
    # they are intentionally unused.
    del reflected, compare_to
    if name and name.startswith(_PROCRASTINATE_PREFIX):
        return False
    # Indizes haben keinen Tabellennamen als ``name``, sondern den Index-Namen.
    # Foreign-Keys liegen über ``object_.table`` — beide Pfade über Präfix abdecken.
    if type_ in {"index", "foreign_key_constraint", "unique_constraint"}:
        table = getattr(object_, "table", None)
        if table is not None and table.name.startswith(_PROCRASTINATE_PREFIX):
            return False
    return True


def _include_name(
    name: str | None,
    type_: str,
    parent_names: dict[str, str | None],
) -> bool:
    # ``type_`` and ``parent_names`` are part of the alembic callback signature;
    # they are intentionally unused.
    del type_, parent_names
    return not (name and name.startswith(_PROCRASTINATE_PREFIX))


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
        include_object=_include_object,
        include_name=_include_name,
    )

    with context.begin_transaction():
        context.run_migrations()


def _run_sync_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        include_object=_include_object,
        include_name=_include_name,
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
