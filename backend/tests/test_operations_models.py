"""Tests for the operations ORM models (Phase 2 Schritt 2.1)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import CheckConstraint, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID

from eb_digital.db import Base, TimestampMixin
from eb_digital.operations.models import (
    ALLOWED_OPERATION_STATUS,
    OPERATION_STATUS_ACTIVE,
    OPERATION_STATUS_CLOSED,
    OPERATION_STATUS_PLANNED,
    Operation,
    OperationAuditLog,
)

# ---- Operation -------------------------------------------------------------


def test_operation_table_registered() -> None:
    assert "operation" in Base.metadata.tables


def test_operation_has_no_tenant_id_column() -> None:
    """Invariante I1 (ADR-009): Operation↔Tenant geht ausschließlich über
    operation_tenant_participation; ein direkter Foreign-Key wäre eine
    architektonische Regelverletzung.
    """
    assert "tenant_id" not in Operation.__table__.c


def test_operation_uses_timestamp_mixin() -> None:
    assert issubclass(Operation, TimestampMixin)
    assert "created_at" in Operation.__table__.c
    assert "updated_at" in Operation.__table__.c


def test_operation_id_is_uuid_primary_key_with_uuid4_default() -> None:
    pk_columns = list(Operation.__table__.primary_key.columns)
    assert len(pk_columns) == 1
    assert pk_columns[0].name == "id"
    assert isinstance(pk_columns[0].type, UUID)
    column = Operation.__table__.c["id"]
    value = column.default.arg(None) if callable(column.default.arg) else column.default.arg
    assert isinstance(value, uuid.UUID)
    assert value.version == 4


def test_operation_status_check_constraint_present() -> None:
    constraints = [c for c in Operation.__table__.constraints if isinstance(c, CheckConstraint)]
    names = {c.name for c in constraints}
    assert "ck_operation_status_allowed" in names


def test_operation_status_constants_match_allowed_set() -> None:
    assert (
        frozenset({OPERATION_STATUS_PLANNED, OPERATION_STATUS_ACTIVE, OPERATION_STATUS_CLOSED})
        == ALLOWED_OPERATION_STATUS
    )


def test_operation_url_token_unique_and_not_null() -> None:
    column = Operation.__table__.c["url_token"]
    assert column.nullable is False
    assert column.unique is True
    assert column.type.length == 64


def test_operation_access_code_hash_nullable_and_long_enough_for_argon2() -> None:
    column = Operation.__table__.c["access_code_hash"]
    assert column.nullable is True
    assert column.type.length is not None
    assert column.type.length >= 128


def test_operation_access_code_active_default_false() -> None:
    column = Operation.__table__.c["access_code_active"]
    assert column.nullable is False
    assert column.default.arg is False


def test_operation_lifecycle_timestamps_are_timezone_aware() -> None:
    for name in ("opened_at", "closed_at"):
        column = Operation.__table__.c[name]
        assert column.nullable is True
        assert column.type.timezone is True


def test_operation_city_label_required() -> None:
    column = Operation.__table__.c["city_label"]
    assert column.nullable is False
    assert column.type.length == 120


def test_operation_naming_convention_applied() -> None:
    assert Operation.__table__.primary_key.name == "pk_operation"


# ---- OperationAuditLog -----------------------------------------------------


def test_audit_log_table_registered() -> None:
    assert "operation_audit_log" in Base.metadata.tables


def test_audit_log_does_not_use_timestamp_mixin() -> None:
    """Audit-Log ist immutable — kein ``updated_at``-Konzept (ADR-008)."""
    assert not issubclass(OperationAuditLog, TimestampMixin)
    assert "updated_at" not in OperationAuditLog.__table__.c


def test_audit_log_id_is_uuid_primary_key() -> None:
    pk_columns = list(OperationAuditLog.__table__.primary_key.columns)
    assert len(pk_columns) == 1
    assert pk_columns[0].name == "id"
    assert isinstance(pk_columns[0].type, UUID)


def test_audit_log_operation_fk_cascades() -> None:
    """Operation-Löschung räumt das Audit-Log mit ab."""
    fks: dict[str, ForeignKeyConstraint] = {
        fk.column_keys[0]: fk
        for fk in OperationAuditLog.__table__.constraints
        if isinstance(fk, ForeignKeyConstraint)
    }
    assert fks["operation_id"].ondelete == "CASCADE"


def test_audit_log_actor_dispatcher_fk_set_null_for_dsgvo_anonymisation() -> None:
    """ADR-008-Konsequenz: Audit-Eintrag bleibt erhalten, Personenbezug
    wird durch ON DELETE SET NULL bei Disponenten-Löschung entfernt.
    """
    fks: dict[str, ForeignKeyConstraint] = {
        fk.column_keys[0]: fk
        for fk in OperationAuditLog.__table__.constraints
        if isinstance(fk, ForeignKeyConstraint)
    }
    assert fks["actor_dispatcher_id"].ondelete == "SET NULL"
    assert OperationAuditLog.__table__.c["actor_dispatcher_id"].nullable is True


def test_audit_log_at_is_timezone_aware_utc_default() -> None:
    column = OperationAuditLog.__table__.c["at"]
    assert column.nullable is False
    assert column.type.timezone is True
    default_callable = column.default.arg
    assert callable(default_callable)
    now = default_callable(None) if default_callable.__code__.co_argcount else default_callable()
    assert isinstance(now, datetime)
    assert now.tzinfo is UTC


def test_audit_log_action_type_no_db_check_yet() -> None:
    """Action-Vokabular wächst mit Phase 4. Phase 2.1 lässt action_type als
    String offen; ein CHECK-Constraint kann später additiv ergänzt werden.
    """
    constraints = [
        c for c in OperationAuditLog.__table__.constraints if isinstance(c, CheckConstraint)
    ]
    assert constraints == []
    column = OperationAuditLog.__table__.c["action_type"]
    assert column.nullable is False
    assert column.type.length == 64


def test_audit_log_target_id_not_null() -> None:
    """Convention: bei Operation-Level-Aktionen ``target_id = operation_id``,
    sonst die ID des spezifischen Ziel-Objekts.
    """
    column = OperationAuditLog.__table__.c["target_id"]
    assert column.nullable is False
    assert isinstance(column.type, UUID)


def test_audit_log_payload_is_jsonb_nullable() -> None:
    column = OperationAuditLog.__table__.c["payload"]
    assert column.nullable is True
    assert isinstance(column.type, JSONB)


def test_audit_log_index_on_operation_id_at_present() -> None:
    """Standard-Query „letzte Audit-Einträge einer Operation"."""
    indexes = {idx.name: idx for idx in OperationAuditLog.__table__.indexes}
    assert "ix_operation_audit_log_operation_id_at" in indexes
    index = indexes["ix_operation_audit_log_operation_id_at"]
    assert index.unique is False
    column_names = [c.name for c in index.columns]
    assert column_names == ["operation_id", "at"]
