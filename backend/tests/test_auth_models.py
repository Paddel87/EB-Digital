"""Tests for the auth ORM models.

Covers ``PlatformAdmin`` (Schritt 1.6) plus ``Dispatcher`` and ``Carer``
(Phase 2 Schritt 2.1).
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, ForeignKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID

from eb_digital.auth.models import (
    ALLOWED_CREATED_VIA,
    CREATED_VIA_ADMIN_CLI,
    CREATED_VIA_BOOTSTRAP_CLI,
    Carer,
    Dispatcher,
    PlatformAdmin,
)
from eb_digital.db import Base, TimestampMixin


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


# ---- Dispatcher / Carer (Phase 2 Schritt 2.1) -----------------------------


def _foreign_keys(table) -> dict[str, ForeignKeyConstraint]:  # type: ignore[no-untyped-def]
    return {
        fk.column_keys[0]: fk for fk in table.constraints if isinstance(fk, ForeignKeyConstraint)
    }


def test_dispatcher_table_registered() -> None:
    assert "dispatcher" in Base.metadata.tables


def test_carer_table_registered() -> None:
    assert "carer" in Base.metadata.tables


def test_dispatcher_uses_timestamp_mixin() -> None:
    assert issubclass(Dispatcher, TimestampMixin)
    assert "created_at" in Dispatcher.__table__.c
    assert "updated_at" in Dispatcher.__table__.c


def test_carer_uses_timestamp_mixin() -> None:
    assert issubclass(Carer, TimestampMixin)
    assert "created_at" in Carer.__table__.c
    assert "updated_at" in Carer.__table__.c


def test_dispatcher_id_is_uuid_primary_key_with_uuid4_default() -> None:
    pk_columns = list(Dispatcher.__table__.primary_key.columns)
    assert len(pk_columns) == 1
    assert pk_columns[0].name == "id"
    assert isinstance(pk_columns[0].type, UUID)
    column = Dispatcher.__table__.c["id"]
    value = column.default.arg(None) if callable(column.default.arg) else column.default.arg
    assert isinstance(value, uuid.UUID)
    assert value.version == 4


def test_carer_id_is_uuid_primary_key_with_uuid4_default() -> None:
    pk_columns = list(Carer.__table__.primary_key.columns)
    assert len(pk_columns) == 1
    assert pk_columns[0].name == "id"
    assert isinstance(pk_columns[0].type, UUID)
    column = Carer.__table__.c["id"]
    value = column.default.arg(None) if callable(column.default.arg) else column.default.arg
    assert isinstance(value, uuid.UUID)
    assert value.version == 4


def test_dispatcher_tenant_fk_restrict_on_delete() -> None:
    """RESTRICT schützt vor versehentlicher Mandanten-Löschung; DSGVO-Art.-17
    läuft über expliziten Deactivation-Pfad in ``backend/tenants``.
    """
    fks = _foreign_keys(Dispatcher.__table__)
    assert fks["tenant_id"].ondelete == "RESTRICT"
    assert Dispatcher.__table__.c["tenant_id"].nullable is False


def test_carer_tenant_fk_restrict_on_delete() -> None:
    fks = _foreign_keys(Carer.__table__)
    assert fks["tenant_id"].ondelete == "RESTRICT"
    assert Carer.__table__.c["tenant_id"].nullable is False


def test_dispatcher_username_unique_per_tenant() -> None:
    """``(tenant_id, username)`` UNIQUE — nicht global, weil zwei Mandanten
    denselben Spitznamen haben dürfen.
    """
    uniques = {
        c.name: c for c in Dispatcher.__table__.constraints if isinstance(c, UniqueConstraint)
    }
    assert "uq_dispatcher_tenant_id_username" in uniques
    columns = [c.name for c in uniques["uq_dispatcher_tenant_id_username"].columns]
    assert columns == ["tenant_id", "username"]


def test_carer_username_unique_per_tenant() -> None:
    uniques = {c.name: c for c in Carer.__table__.constraints if isinstance(c, UniqueConstraint)}
    assert "uq_carer_tenant_id_username" in uniques
    columns = [c.name for c in uniques["uq_carer_tenant_id_username"].columns]
    assert columns == ["tenant_id", "username"]


def test_dispatcher_password_hash_long_enough_for_argon2() -> None:
    column = Dispatcher.__table__.c["password_hash"]
    assert column.nullable is False
    assert column.type.length is not None
    assert column.type.length >= 128


def test_carer_password_hash_long_enough_for_argon2() -> None:
    column = Carer.__table__.c["password_hash"]
    assert column.nullable is False
    assert column.type.length is not None
    assert column.type.length >= 128


def test_dispatcher_email_optional() -> None:
    """Email ist nur für den Reset-Flow nötig — fehlt sie, läuft Reset über
    Mandanten-Admin oder Plattform-Administrator.
    """
    column = Dispatcher.__table__.c["email"]
    assert column.nullable is True
    assert column.type.length == 254


def test_carer_email_optional() -> None:
    column = Carer.__table__.c["email"]
    assert column.nullable is True
    assert column.type.length == 254


def test_dispatcher_is_active_default_true() -> None:
    column = Dispatcher.__table__.c["is_active"]
    assert column.nullable is False
    assert column.default.arg is True


def test_carer_is_active_default_true() -> None:
    column = Carer.__table__.c["is_active"]
    assert column.nullable is False
    assert column.default.arg is True


def test_dispatcher_naming_convention_applied() -> None:
    assert Dispatcher.__table__.primary_key.name == "pk_dispatcher"


def test_carer_naming_convention_applied() -> None:
    assert Carer.__table__.primary_key.name == "pk_carer"
