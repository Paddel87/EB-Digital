"""Tests für ``backend/eb_digital/operations/repository`` (Schritt 4.3a).

Stub-Session-Strategie analog ``test_fleet_repositories``: add/flush/delete/
get/execute werden gestubbt. Die SELECT-Semantik (Filter, Sortierung,
Partial-UNIQUE) wird im Compose-Smoke gegen Postgres validiert.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from eb_digital.operations.repository import (
    CustomerOrderRepository,
    OperationAreaRepository,
    OperationAuditLogRepository,
    OperationDispatcherParticipationRepository,
    OperationRepository,
    OrderAssignmentRepository,
)

_GEOMETRY: dict[str, Any] = {
    "type": "Polygon",
    "coordinates": [[[8.80, 53.07], [8.81, 53.07], [8.81, 53.08], [8.80, 53.07]]],
}


class _Result:
    def __init__(self, *, single: Any = None, many: list[Any] | None = None) -> None:
        self._single = single
        self._many = many or []

    def scalar_one_or_none(self) -> Any:
        return self._single

    def scalars(self) -> _Result:
        return self

    def all(self) -> list[Any]:
        return self._many


class _StubSession:
    def __init__(
        self, *, single: Any = None, many: list[Any] | None = None, get_obj: Any = None
    ) -> None:
        self._single = single
        self._many = many
        self._get_obj = get_obj
        self.added: list[Any] = []
        self.deleted: list[Any] = []
        self.flushes = 0

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1

    async def delete(self, obj: Any) -> None:
        self.deleted.append(obj)

    async def get(self, _model: Any, _pk: Any) -> Any:
        return self._get_obj

    async def execute(self, _stmt: Any) -> _Result:
        return _Result(single=self._single, many=self._many)


# ─── OperationRepository ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_operation_create_adds_and_flushes() -> None:
    session = _StubSession()
    op = await OperationRepository.create(session, city_label="Bremen", url_token="tok")  # type: ignore[arg-type]
    assert op.status == "planned"
    assert session.added == [op]
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_operation_find_by_id() -> None:
    sentinel = object()
    session = _StubSession(single=sentinel)
    assert await OperationRepository.find_by_id(session, uuid.uuid4()) is sentinel  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_operation_find_by_url_token() -> None:
    sentinel = object()
    session = _StubSession(single=sentinel)
    assert await OperationRepository.find_by_url_token(session, "tok") is sentinel  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_operation_owner_tenant_id() -> None:
    tid = uuid.uuid4()
    session = _StubSession(single=tid)
    assert await OperationRepository.owner_tenant_id(session, uuid.uuid4()) == tid  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_operation_list_for_tenant() -> None:
    rows = [object(), object()]
    session = _StubSession(many=rows)
    assert await OperationRepository.list_for_tenant(session, uuid.uuid4()) == rows  # type: ignore[arg-type]


# ─── OperationAreaRepository ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_area_create() -> None:
    session = _StubSession()
    area = await OperationAreaRepository.create(
        session,  # type: ignore[arg-type]
        operation_id=uuid.uuid4(),
        area_index=1,
        polygon=_GEOMETRY,
        label="A",
    )
    assert area.area_index == 1
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_area_list_for_operation() -> None:
    rows = [object()]
    session = _StubSession(many=rows)
    assert await OperationAreaRepository.list_for_operation(session, uuid.uuid4()) == rows  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_area_delete_all_for_operation() -> None:
    existing = [object(), object()]
    session = _StubSession(many=existing)
    await OperationAreaRepository.delete_all_for_operation(session, uuid.uuid4())  # type: ignore[arg-type]
    assert session.deleted == existing
    assert session.flushes == 1


# ─── OperationDispatcherParticipationRepository ───────────────────────────────


@pytest.mark.asyncio
async def test_dispatcher_participation_upsert_new() -> None:
    session = _StubSession(get_obj=None)
    p = await OperationDispatcherParticipationRepository.upsert(
        session,
        operation_id=uuid.uuid4(),
        dispatcher_id=uuid.uuid4(),  # type: ignore[arg-type]
    )
    assert p in session.added
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_dispatcher_participation_upsert_existing_resets_left_at() -> None:
    from types import SimpleNamespace

    existing = SimpleNamespace(left_at="2026-01-01")
    session = _StubSession(get_obj=existing)
    p = await OperationDispatcherParticipationRepository.upsert(
        session,
        operation_id=uuid.uuid4(),
        dispatcher_id=uuid.uuid4(),  # type: ignore[arg-type]
    )
    assert p is existing
    assert existing.left_at is None


@pytest.mark.asyncio
async def test_dispatcher_participation_is_participant() -> None:
    from types import SimpleNamespace

    session = _StubSession(get_obj=SimpleNamespace(left_at=None))
    assert await OperationDispatcherParticipationRepository.is_participant(
        session,
        operation_id=uuid.uuid4(),
        dispatcher_id=uuid.uuid4(),  # type: ignore[arg-type]
    )
    session_gone = _StubSession(get_obj=None)
    assert not await OperationDispatcherParticipationRepository.is_participant(
        session_gone,
        operation_id=uuid.uuid4(),
        dispatcher_id=uuid.uuid4(),  # type: ignore[arg-type]
    )


# ─── CustomerOrderRepository ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_order_create_and_add_item() -> None:
    session = _StubSession()
    order = await CustomerOrderRepository.create(
        session,  # type: ignore[arg-type]
        operation_id=uuid.uuid4(),
        anonymous_session_id=uuid.uuid4(),
        status="pending",
        location_lat=53.0,
        location_lng=8.0,
        location_accuracy_m=10.0,
        location_text=None,
        plausibility_outcome="ACCEPTED",
        plausibility_distance_m=5.0,
        plausibility_threshold_m=5000,
        plausibility_variant="dynamic_2_accuracy",
    )
    assert order.status == "pending"
    item = await CustomerOrderRepository.add_item(
        session,  # type: ignore[arg-type]
        order_id=order.id,
        base_item_id=uuid.uuid4(),
        tenant_extension_id=None,
        quantity=3,
    )
    assert item.quantity == 3
    assert session.flushes == 2


@pytest.mark.asyncio
async def test_order_find_by_id_uses_get() -> None:
    sentinel = object()
    session = _StubSession(get_obj=sentinel)
    assert await CustomerOrderRepository.find_by_id(session, uuid.uuid4()) is sentinel  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_order_list_and_items() -> None:
    rows = [object()]
    session = _StubSession(many=rows)
    assert await CustomerOrderRepository.list_for_operation(session, uuid.uuid4()) == rows  # type: ignore[arg-type]
    assert await CustomerOrderRepository.items_for_order(session, uuid.uuid4()) == rows  # type: ignore[arg-type]


# ─── OrderAssignmentRepository ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_assignment_create() -> None:
    session = _StubSession()
    a = await OrderAssignmentRepository.create(
        session,
        order_id=uuid.uuid4(),
        vehicle_id=uuid.uuid4(),
        dispatcher_id=uuid.uuid4(),  # type: ignore[arg-type]
    )
    assert a.status == "assigned"
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_assignment_find_active_and_list() -> None:
    sentinel = object()
    session = _StubSession(single=sentinel, many=[sentinel])
    assert await OrderAssignmentRepository.find_active_for_order(session, uuid.uuid4()) is sentinel  # type: ignore[arg-type]
    assert await OrderAssignmentRepository.list_for_operation(session, uuid.uuid4()) == [sentinel]  # type: ignore[arg-type]


# ─── OperationAuditLogRepository ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_audit_log_list_for_operation() -> None:
    rows = [object(), object()]
    session = _StubSession(many=rows)
    assert await OperationAuditLogRepository.list_for_operation(session, uuid.uuid4()) == rows  # type: ignore[arg-type]
