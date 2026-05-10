"""Tests für ``backend/eb_digital/auth_anonymous/models.AnonymousSession``."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID

from eb_digital.auth_anonymous.models import (
    ANONYMOUS_SESSION_HARD_CAP,
    AnonymousSession,
)
from eb_digital.db import Base, TimestampMixin


def test_anonymous_session_table_registered() -> None:
    assert "anonymous_session" in Base.metadata.tables


def test_anonymous_session_does_not_use_timestamp_mixin() -> None:
    """Anonyme Session führt ``created_at`` + ``last_seen_at`` selbst — kein
    ``updated_at`` (kein generischer Audit-Pfad nötig)."""
    assert not issubclass(AnonymousSession, TimestampMixin)
    assert "updated_at" not in AnonymousSession.__table__.c
    assert "created_at" in AnonymousSession.__table__.c
    assert "last_seen_at" in AnonymousSession.__table__.c


def test_id_is_uuid_primary_key_with_uuid4_default() -> None:
    pk_columns = list(AnonymousSession.__table__.primary_key.columns)
    assert len(pk_columns) == 1
    assert pk_columns[0].name == "id"
    assert isinstance(pk_columns[0].type, UUID)
    column = AnonymousSession.__table__.c["id"]
    value = column.default.arg(None) if callable(column.default.arg) else column.default.arg
    assert isinstance(value, uuid.UUID)
    assert value.version == 4


def test_operation_fk_cascades_on_delete() -> None:
    """Operation-Löschung räumt Anon-Sessions mit ab — analog
    ``operation_audit_log``."""
    fks: dict[str, ForeignKeyConstraint] = {
        fk.column_keys[0]: fk
        for fk in AnonymousSession.__table__.constraints
        if isinstance(fk, ForeignKeyConstraint)
    }
    assert fks["operation_id"].ondelete == "CASCADE"
    assert AnonymousSession.__table__.c["operation_id"].nullable is False


def test_timestamps_are_timezone_aware_utc() -> None:
    for name in ("created_at", "last_seen_at", "expires_at"):
        column = AnonymousSession.__table__.c[name]
        assert column.nullable is False
        assert column.type.timezone is True


def test_expires_at_default_is_24h_in_the_future() -> None:
    """``expires_at`` ist 24-h-Hard-Cap auf dem aktuellen ``now()``-Wert.
    Patrick-Entscheidung 2026-05-11 (Frage 3 = Option B)."""
    column = AnonymousSession.__table__.c["expires_at"]
    callable_default = column.default.arg
    assert callable(callable_default)
    before = datetime.now(UTC)
    # SQLAlchemy umwickelt manche Default-Callables mit einem ``ctx``-Argument;
    # daher Fallback analog zum Pattern in ``test_operations_models``.
    result = callable_default(None) if callable_default.__code__.co_argcount else callable_default()
    after = datetime.now(UTC)
    expected_window = (after + ANONYMOUS_SESSION_HARD_CAP) - (before + ANONYMOUS_SESSION_HARD_CAP)
    expected_min = before + ANONYMOUS_SESSION_HARD_CAP - timedelta(seconds=1)
    expected_max = after + ANONYMOUS_SESSION_HARD_CAP + timedelta(seconds=1)
    assert expected_min <= result <= expected_max, (
        f"expires_at-Default außerhalb der erwarteten Spanne: {result} "
        f"vs. [{expected_min}, {expected_max}], Δ {expected_window}"
    )


def test_hard_cap_is_24_hours() -> None:
    assert timedelta(hours=24) == ANONYMOUS_SESSION_HARD_CAP


def test_no_client_ip_hash_column() -> None:
    """Vision-Constraint „keine PII": IP wird nicht persistiert. Frage-2-B
    Patrick-Entscheidung 2026-05-11. Forensik wäre additiv per ADR."""
    assert "client_ip_hash" not in AnonymousSession.__table__.c
    assert "client_ip" not in AnonymousSession.__table__.c


def test_naming_convention_applied() -> None:
    assert AnonymousSession.__table__.primary_key.name == "pk_anonymous_session"


def test_index_on_operation_id_present() -> None:
    """Standard-Query: „aktive Sessions einer Operation" + Cleanup-Job (4.x)."""
    indexes = {idx.name: idx for idx in AnonymousSession.__table__.indexes}
    assert "ix_anonymous_session_operation_id" in indexes
    index = indexes["ix_anonymous_session_operation_id"]
    assert index.unique is False
    column_names = [c.name for c in index.columns]
    assert column_names == ["operation_id"]
