"""Tests for the PlatformAdmin ORM model (Schritt 1.6)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint
from sqlalchemy.dialects.postgresql import UUID

from eb_digital.auth.models import (
    ALLOWED_CREATED_VIA,
    CREATED_VIA_ADMIN_CLI,
    CREATED_VIA_BOOTSTRAP_CLI,
    PlatformAdmin,
)
from eb_digital.db import Base


def test_platform_admin_table_registered_with_metadata() -> None:
    assert "platform_admin" in Base.metadata.tables


def test_platform_admin_id_is_uuid_primary_key() -> None:
    pk_columns = list(PlatformAdmin.__table__.primary_key.columns)
    assert len(pk_columns) == 1
    assert pk_columns[0].name == "id"
    assert isinstance(pk_columns[0].type, UUID)


def test_platform_admin_id_default_is_uuid4_callable() -> None:
    column = PlatformAdmin.__table__.c["id"]
    assert column.default is not None
    value = column.default.arg(None) if callable(column.default.arg) else column.default.arg
    assert isinstance(value, uuid.UUID)
    assert value.version == 4


def test_platform_admin_username_unique_and_not_null() -> None:
    column = PlatformAdmin.__table__.c["username"]
    assert column.unique is True
    assert column.nullable is False


def test_platform_admin_password_hash_not_null_and_long_enough_for_argon2() -> None:
    column = PlatformAdmin.__table__.c["password_hash"]
    assert column.nullable is False
    # Argon2id PHC strings can exceed 100 chars; 255 leaves headroom.
    assert column.type.length is not None
    assert column.type.length >= 128


def test_platform_admin_created_at_is_timezone_aware_utc_default() -> None:
    column = PlatformAdmin.__table__.c["created_at"]
    assert column.nullable is False
    assert column.type.timezone is True
    # The python-side default produces a UTC-aware datetime.
    default_callable = column.default.arg
    assert callable(default_callable)
    now = default_callable(None) if default_callable.__code__.co_argcount else default_callable()
    assert isinstance(now, datetime)
    assert now.tzinfo is UTC


def test_platform_admin_created_via_check_constraint_present() -> None:
    constraints = [c for c in PlatformAdmin.__table__.constraints if isinstance(c, CheckConstraint)]
    names = {c.name for c in constraints}
    assert "ck_platform_admin_created_via_allowed" in names


def test_naming_convention_applied_to_primary_key() -> None:
    assert PlatformAdmin.__table__.primary_key.name == "pk_platform_admin"


def test_naming_convention_applied_to_unique_constraint() -> None:
    uniques = [
        c.name
        for c in PlatformAdmin.__table__.constraints
        if c.__class__.__name__ == "UniqueConstraint"
    ]
    inline_unique_indexes = {idx.name for idx in PlatformAdmin.__table__.indexes if idx.unique}
    assert "uq_platform_admin_username" in (set(uniques) | inline_unique_indexes)


def test_allowed_created_via_set_matches_expected_values() -> None:
    assert "bootstrap_cli" in ALLOWED_CREATED_VIA
    assert "admin_cli" in ALLOWED_CREATED_VIA
    assert len(ALLOWED_CREATED_VIA) == 2
    assert CREATED_VIA_BOOTSTRAP_CLI == "bootstrap_cli"
    assert CREATED_VIA_ADMIN_CLI == "admin_cli"
