"""Tests for the Phase-1 sentinel ORM model (HealthMarker)."""

from __future__ import annotations

import uuid

from sqlalchemy.dialects.postgresql import UUID

from eb_digital.db import Base, TimestampMixin
from eb_digital.db.models import HealthMarker


def test_health_marker_table_registered_with_metadata() -> None:
    assert "health_marker" in Base.metadata.tables


def test_health_marker_inherits_audit_columns() -> None:
    assert issubclass(HealthMarker, TimestampMixin)
    assert "created_at" in HealthMarker.__table__.c
    assert "updated_at" in HealthMarker.__table__.c


def test_health_marker_id_is_uuid_primary_key() -> None:
    pk_columns = list(HealthMarker.__table__.primary_key.columns)
    assert len(pk_columns) == 1
    assert pk_columns[0].name == "id"
    assert isinstance(pk_columns[0].type, UUID)


def test_health_marker_id_default_is_uuid4_callable() -> None:
    column = HealthMarker.__table__.c["id"]
    assert column.default is not None
    value = column.default.arg(None) if callable(column.default.arg) else column.default.arg
    assert isinstance(value, uuid.UUID)
    assert value.version == 4


def test_health_marker_label_is_unique() -> None:
    label = HealthMarker.__table__.c["label"]
    assert label.unique is True
    assert label.nullable is False


def test_naming_convention_applied_to_primary_key_constraint() -> None:
    pk = HealthMarker.__table__.primary_key
    assert pk.name == "pk_health_marker"


def test_naming_convention_applied_to_unique_constraint() -> None:
    uniques = [
        c for c in HealthMarker.__table__.constraints if c.__class__.__name__ == "UniqueConstraint"
    ]
    inline_unique_indexes = [idx for idx in HealthMarker.__table__.indexes if idx.unique]
    names = {c.name for c in uniques} | {idx.name for idx in inline_unique_indexes}
    assert any(
        (name and name.startswith("uq_health_marker_")) or name == "ix_health_marker_label"
        for name in names
    )
