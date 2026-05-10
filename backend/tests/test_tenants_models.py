"""Tests for the tenants ORM models (Phase 2 Schritt 2.1)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID

from eb_digital.db import Base, TimestampMixin
from eb_digital.tenants.models import (
    ALLOWED_PARTICIPATION_ROLES,
    ALLOWED_TENANT_STATUS,
    PARTICIPATION_ROLE_OWNER,
    PARTICIPATION_ROLE_PARTICIPANT,
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_APPLIED,
    TENANT_STATUS_DEACTIVATED,
    OperationTenantParticipation,
    Tenant,
)

# ---- Tenant ----------------------------------------------------------------


def test_tenant_table_registered() -> None:
    assert "tenant" in Base.metadata.tables


def test_tenant_uses_timestamp_mixin() -> None:
    assert issubclass(Tenant, TimestampMixin)
    assert "created_at" in Tenant.__table__.c
    assert "updated_at" in Tenant.__table__.c


def test_tenant_id_is_uuid_primary_key_with_uuid4_default() -> None:
    pk_columns = list(Tenant.__table__.primary_key.columns)
    assert len(pk_columns) == 1
    assert pk_columns[0].name == "id"
    assert isinstance(pk_columns[0].type, UUID)
    column = Tenant.__table__.c["id"]
    value = column.default.arg(None) if callable(column.default.arg) else column.default.arg
    assert isinstance(value, uuid.UUID)
    assert value.version == 4


def test_tenant_name_is_unique_and_not_null() -> None:
    column = Tenant.__table__.c["name"]
    assert column.nullable is False
    assert column.unique is True
    assert column.type.length == 120


def test_tenant_slug_is_unique_and_not_null() -> None:
    column = Tenant.__table__.c["slug"]
    assert column.nullable is False
    assert column.unique is True
    assert column.type.length == 64


def test_tenant_status_check_constraint_present() -> None:
    constraints = [c for c in Tenant.__table__.constraints if isinstance(c, CheckConstraint)]
    names = {c.name for c in constraints}
    assert "ck_tenant_status_allowed" in names


def test_tenant_lifecycle_columns_are_timezone_aware() -> None:
    for name, expect_nullable in (
        ("applied_at", False),
        ("activated_at", True),
        ("deactivated_at", True),
    ):
        column = Tenant.__table__.c[name]
        assert column.nullable is expect_nullable
        assert column.type.timezone is True


def test_tenant_applied_at_default_is_utc_now() -> None:
    column = Tenant.__table__.c["applied_at"]
    default_callable = column.default.arg
    assert callable(default_callable)
    now = default_callable(None) if default_callable.__code__.co_argcount else default_callable()
    assert isinstance(now, datetime)
    assert now.tzinfo is UTC


def test_tenant_status_constants_match_allowed_set() -> None:
    assert (
        frozenset({TENANT_STATUS_APPLIED, TENANT_STATUS_ACTIVE, TENANT_STATUS_DEACTIVATED})
        == ALLOWED_TENANT_STATUS
    )
    assert TENANT_STATUS_APPLIED == "applied"
    assert TENANT_STATUS_ACTIVE == "active"
    assert TENANT_STATUS_DEACTIVATED == "deactivated"


def test_tenant_naming_convention_applied() -> None:
    assert Tenant.__table__.primary_key.name == "pk_tenant"
    constraint_names = {c.name for c in Tenant.__table__.constraints}
    assert "ck_tenant_status_allowed" in constraint_names


# ---- OperationTenantParticipation -----------------------------------------


def test_participation_table_registered() -> None:
    assert "operation_tenant_participation" in Base.metadata.tables


def test_participation_uses_composite_primary_key() -> None:
    pk_columns = [c.name for c in OperationTenantParticipation.__table__.primary_key.columns]
    assert pk_columns == ["operation_id", "tenant_id"]


def test_participation_role_check_constraint_present() -> None:
    constraints = [
        c
        for c in OperationTenantParticipation.__table__.constraints
        if isinstance(c, CheckConstraint)
    ]
    names = {c.name for c in constraints}
    assert "ck_operation_tenant_participation_role_allowed" in names


def test_participation_owner_partial_unique_index_present() -> None:
    """Partial-Unique-Index erzwingt Phase-1-Invariante I1: max ein Owner pro Operation."""
    indexes = {idx.name: idx for idx in OperationTenantParticipation.__table__.indexes}
    assert "ix_operation_tenant_participation_owner_unique" in indexes
    index = indexes["ix_operation_tenant_participation_owner_unique"]
    assert index.unique is True
    # Filter prüft auf owner-Rolle.
    where_clause = index.dialect_options.get("postgresql", {}).get("where")
    assert where_clause is not None
    assert "owner" in str(where_clause)


def test_participation_role_constants_match_allowed_set() -> None:
    assert (
        frozenset({PARTICIPATION_ROLE_OWNER, PARTICIPATION_ROLE_PARTICIPANT})
        == ALLOWED_PARTICIPATION_ROLES
    )
    assert PARTICIPATION_ROLE_OWNER == "owner"
    assert PARTICIPATION_ROLE_PARTICIPANT == "participant"


def test_participation_foreign_keys_have_expected_ondelete() -> None:
    """Operation-Löschung kaskadiert die Verknüpfung; Mandanten-Löschung wird gebremst."""
    fks: dict[str, ForeignKeyConstraint] = {
        fk.column_keys[0]: fk
        for fk in OperationTenantParticipation.__table__.constraints
        if isinstance(fk, ForeignKeyConstraint)
    }
    assert fks["operation_id"].ondelete == "CASCADE"
    assert fks["tenant_id"].ondelete == "RESTRICT"


def test_participation_joined_at_is_timezone_aware_utc_default() -> None:
    column = OperationTenantParticipation.__table__.c["joined_at"]
    assert column.nullable is False
    assert column.type.timezone is True
    default_callable = column.default.arg
    assert callable(default_callable)
    now = default_callable(None) if default_callable.__code__.co_argcount else default_callable()
    assert now.tzinfo is UTC
