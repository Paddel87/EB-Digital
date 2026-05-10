"""Tests für ``backend/eb_digital/auth_anonymous/repositories``.

Repository-Aufrufe gegen einen Stub-Session — analog zu
``test_auth_repositories.py``. Echte DB-Round-Trips werden im Compose-Smoke
abgedeckt.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest

from eb_digital.auth_anonymous.models import AnonymousSession
from eb_digital.auth_anonymous.repositories import (
    create_anonymous_session,
    find_anonymous_session_by_id,
    find_operation_by_id,
    is_session_still_valid,
)
from eb_digital.operations.models import OPERATION_STATUS_ACTIVE, Operation


class _StubResult:
    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one_or_none(self) -> Any:
        return self._value


class _StubSession:
    """Minimal ``AsyncSession``-Ersatz mit Match-Dispatch nach Entity-Typ."""

    def __init__(
        self,
        *,
        operation: Operation | None = None,
        anonymous_session: AnonymousSession | None = None,
    ) -> None:
        self._operation = operation
        self._anonymous_session = anonymous_session
        self.added: list[Any] = []
        self.flushed = False

    async def execute(self, stmt: Any) -> _StubResult:
        entity = stmt.column_descriptions[0]["entity"]
        if entity is Operation:
            return _StubResult(self._operation)
        if entity is AnonymousSession:
            return _StubResult(self._anonymous_session)
        return _StubResult(None)

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushed = True


def _make_operation(op_id: uuid.UUID | None = None) -> Operation:
    op = Operation(
        id=op_id or uuid.uuid4(),
        status=OPERATION_STATUS_ACTIVE,
        city_label="Bremen Innenstadt",
        url_token="signed.token.value",
        access_code_hash=None,
        access_code_active=False,
    )
    now = datetime.now(UTC)
    op.created_at = now
    op.updated_at = now
    return op


@pytest.mark.asyncio
async def test_find_operation_returns_match() -> None:
    op = _make_operation()
    session = _StubSession(operation=op)
    found = await find_operation_by_id(session, op.id)  # type: ignore[arg-type]
    assert found is op


@pytest.mark.asyncio
async def test_find_operation_returns_none_when_missing() -> None:
    session = _StubSession()
    found = await find_operation_by_id(session, uuid.uuid4())  # type: ignore[arg-type]
    assert found is None


@pytest.mark.asyncio
async def test_create_anonymous_session_adds_and_flushes() -> None:
    op = _make_operation()
    session = _StubSession()
    record = await create_anonymous_session(session, operation_id=op.id)  # type: ignore[arg-type]
    assert record.operation_id == op.id
    assert session.added == [record]
    assert session.flushed is True
    assert isinstance(record, AnonymousSession)


@pytest.mark.asyncio
async def test_find_anonymous_session_returns_match() -> None:
    op = _make_operation()
    record = AnonymousSession(operation_id=op.id)
    session = _StubSession(anonymous_session=record)
    found = await find_anonymous_session_by_id(session, uuid.uuid4())  # type: ignore[arg-type]
    assert found is record


@pytest.mark.asyncio
async def test_find_anonymous_session_returns_none_when_missing() -> None:
    session = _StubSession()
    found = await find_anonymous_session_by_id(session, uuid.uuid4())  # type: ignore[arg-type]
    assert found is None


def test_is_session_still_valid_returns_true_when_expires_at_in_future() -> None:
    record = AnonymousSession(operation_id=uuid.uuid4())
    record.expires_at = datetime.now(UTC) + timedelta(hours=1)
    assert is_session_still_valid(record) is True


def test_is_session_still_valid_returns_false_when_expired() -> None:
    record = AnonymousSession(operation_id=uuid.uuid4())
    record.expires_at = datetime.now(UTC) - timedelta(seconds=1)
    assert is_session_still_valid(record) is False


def test_is_session_still_valid_accepts_explicit_now() -> None:
    record = AnonymousSession(operation_id=uuid.uuid4())
    record.expires_at = datetime(2026, 1, 1, tzinfo=UTC)
    # ``now`` vor Ablauf → noch gültig.
    assert is_session_still_valid(record, datetime(2025, 12, 31, tzinfo=UTC)) is True
    # ``now`` nach Ablauf → invalide.
    assert is_session_still_valid(record, datetime(2026, 1, 2, tzinfo=UTC)) is False
