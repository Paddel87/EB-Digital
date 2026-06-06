"""Tests für ``backend/eb_digital/operations/audit`` — Whitelist-Disziplin."""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from eb_digital.operations.audit import (
    ACTION_OPERATION_OPENED,
    TARGET_OPERATION,
    AuditLogger,
)


class _StubSession:
    def __init__(self) -> None:
        self.added: list[Any] = []
        self.flushes = 0

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1


@pytest.mark.asyncio
async def test_audit_logger_writes_known_action() -> None:
    session = _StubSession()
    op_id = uuid.uuid4()
    entry = await AuditLogger().log(
        session=session,  # type: ignore[arg-type]
        operation_id=op_id,
        actor_dispatcher_id=uuid.uuid4(),
        action_type=ACTION_OPERATION_OPENED,
        target_kind=TARGET_OPERATION,
        target_id=op_id,
        payload={"k": "v"},
    )
    assert entry.action_type == ACTION_OPERATION_OPENED
    assert session.added == [entry]
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_audit_logger_rejects_unknown_action() -> None:
    with pytest.raises(ValueError, match="Unknown audit action_type"):
        await AuditLogger().log(
            session=_StubSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            actor_dispatcher_id=None,
            action_type="totally_unknown_action",
            target_kind=TARGET_OPERATION,
            target_id=uuid.uuid4(),
        )
