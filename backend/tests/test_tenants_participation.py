"""Tests für ``backend/eb_digital/tenants/participation`` (S10).

Strategie: Statement-basierte Stub-Session (analog ``test_auth_repositories``),
die die SELECT-Statements abfängt und vor-konfigurierte Ergebnisse liefert.
Die Statement-Logik (JOIN über ``operation_tenant_participation``) wird im
Integration-Pfad über ``dev-smoke.sh`` gegen die echte Postgres-DB
validiert.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from typing import Any

import pytest

from eb_digital.tenants.participation import (
    list_operations_for_tenant,
    owners_of_operation,
    tenant_participates_in_operation,
)


class _Scalars:
    def __init__(self, values: Iterable[Any]) -> None:
        self._values = list(values)

    def all(self) -> list[Any]:
        return list(self._values)


class _StubResult:
    def __init__(self, *, scalars: Iterable[Any] = (), single: Any = None) -> None:
        self._scalars = list(scalars)
        self._single = single

    def scalars(self) -> _Scalars:
        return _Scalars(self._scalars)

    def scalar_one_or_none(self) -> Any:
        return self._single


class _StubSession:
    """Liefert für jeden ``execute()``-Aufruf das vor-konfigurierte Ergebnis."""

    def __init__(self, result: _StubResult) -> None:
        self._result = result

    async def execute(self, _stmt: Any) -> _StubResult:
        return self._result


@pytest.mark.asyncio
async def test_list_operations_for_tenant_returns_uuids() -> None:
    op_a = uuid.uuid4()
    op_b = uuid.uuid4()
    session = _StubSession(_StubResult(scalars=[op_a, op_b]))
    tenant_id = uuid.uuid4()

    result = await list_operations_for_tenant(session, tenant_id)  # type: ignore[arg-type]
    assert result == [op_a, op_b]


@pytest.mark.asyncio
async def test_list_operations_for_tenant_empty() -> None:
    session = _StubSession(_StubResult(scalars=[]))
    result = await list_operations_for_tenant(session, uuid.uuid4())  # type: ignore[arg-type]
    assert result == []


@pytest.mark.asyncio
async def test_tenant_participates_in_operation_true() -> None:
    op_id = uuid.uuid4()
    session = _StubSession(_StubResult(single=op_id))
    result = await tenant_participates_in_operation(
        session,  # type: ignore[arg-type]
        tenant_id=uuid.uuid4(),
        operation_id=op_id,
    )
    assert result is True


@pytest.mark.asyncio
async def test_tenant_participates_in_operation_false() -> None:
    session = _StubSession(_StubResult(single=None))
    result = await tenant_participates_in_operation(
        session,  # type: ignore[arg-type]
        tenant_id=uuid.uuid4(),
        operation_id=uuid.uuid4(),
    )
    assert result is False


@pytest.mark.asyncio
async def test_owners_of_operation_returns_single_tenant_in_phase_1() -> None:
    tenant_id = uuid.uuid4()
    session = _StubSession(_StubResult(scalars=[tenant_id]))
    result = await owners_of_operation(session, uuid.uuid4())  # type: ignore[arg-type]
    assert result == [tenant_id]


@pytest.mark.asyncio
async def test_owners_of_operation_empty_for_unknown_operation() -> None:
    session = _StubSession(_StubResult(scalars=[]))
    result = await owners_of_operation(session, uuid.uuid4())  # type: ignore[arg-type]
    assert result == []
