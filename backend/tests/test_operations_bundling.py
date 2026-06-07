"""Tests für die Bündelung in ``backend/operations`` (Schritt 4.3b, ADR-018).

Deckt den ADR-018-Test-Datensatz B1-B11 ab:
  • B1-B8: ``bundle_orders``-Use-Case (Happy-Path + alle Fehlerklassen).
  • B9:    ``dissolve_bundle``.
  • B10/B11: ``OrderBundleRepository.count_for_operation`` (Aggregat-
    Zähllogik, Detail-Plan 4.3b-6A — die produktive ``operation_aggregate``-
    Migration folgt erst Phase 6.5).
Plus: implizite Bündel-Vervollständigung in ``complete_order`` (2A) und
die Einzel-Order-Storno-Sperre in ``cancel_order`` (3A).

Strategie analog ``test_operations_use_cases``: Repositories + Cross-Modul-
Funktionen via ``AsyncMock`` gestubbt, ``_FakeSession`` deckt add/flush ab,
``AuditLogger``/``RealtimeAdapter`` real. Echte DB-Semantik (Partial-UNIQUE,
FK, Status-CHECK) wird im Compose-Smoke + Migration-Round-Trip geprüft.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from eb_digital.fleet import repositories as fleet_repo
from eb_digital.fleet.models import (
    SUPPLY_MODE_LARGE_ORDER,
    SUPPLY_MODE_OFF,
    VEHICLE_TYPE_REGULAR,
    VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    Vehicle,
)
from eb_digital.fleet.use_cases import VehicleNotSupplyTransporterError
from eb_digital.operations import models as ops_models
from eb_digital.operations import use_cases as uc
from eb_digital.operations.audit import (
    ACTION_BUNDLE_COMPLETED,
    ACTION_BUNDLE_DISSOLVED,
    ACTION_ORDERS_BUNDLED,
    AuditLogger,
)
from eb_digital.operations.exceptions import (
    BundleNotActiveError,
    BundleNotFoundError,
    EmptyBundleError,
    MinimumTwoOrdersError,
    NotParticipantError,
    OperationAlreadyClosedError,
    OperationNotFoundError,
    OrderAlreadyBundledError,
    OrderInActiveBundleError,
    OrderNotFoundError,
    OrderNotInOperationError,
    OrderNotPendingError,
    VehicleNotEligibleError,
    VehicleNotFoundError,
    VehicleNotInLargeOrderModeError,
)
from eb_digital.operations.realtime_adapter import RealtimeAdapter
from eb_digital.operations.repository import (
    CustomerOrderRepository,
    OperationRepository,
    OrderAssignmentRepository,
    OrderBundleRepository,
)

# ─── Fakes / Builders ────────────────────────────────────────────────────────


class _FakeSession:
    def __init__(self) -> None:
        self.added: list[Any] = []
        self.flushes = 0

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1


def _audit() -> AuditLogger:
    return AuditLogger()


def _realtime() -> RealtimeAdapter:
    return RealtimeAdapter()


def _operation(*, status: str = ops_models.OPERATION_STATUS_ACTIVE) -> ops_models.Operation:
    op = ops_models.Operation(
        id=uuid.uuid4(),
        status=status,
        city_label="Bremen",
        url_token="tok",
        access_code_active=False,
        plausibility_threshold_m=None,
    )
    op.created_at = datetime.now(UTC)
    op.updated_at = datetime.now(UTC)
    return op


def _order(
    *,
    operation_id: uuid.UUID,
    status: str = ops_models.ORDER_STATUS_PENDING,
    bundle_id: uuid.UUID | None = None,
) -> Any:
    return SimpleNamespace(
        id=uuid.uuid4(),
        operation_id=operation_id,
        status=status,
        bundle_id=bundle_id,
    )


def _vehicle(
    *,
    tenant_id: uuid.UUID,
    vtype: str = VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    mode: str | None = SUPPLY_MODE_LARGE_ORDER,
) -> Vehicle:
    v = Vehicle(tenant_id=tenant_id, type=vtype, mode=mode, name="VT", is_active=True)
    v.id = uuid.uuid4()
    v.created_at = datetime.now(UTC)
    v.updated_at = datetime.now(UTC)
    return v


def _bundle(
    *,
    operation_id: uuid.UUID,
    status: str = ops_models.BUNDLE_STATUS_ACTIVE,
) -> Any:
    return SimpleNamespace(
        id=uuid.uuid4(),
        operation_id=operation_id,
        vehicle_id=uuid.uuid4(),
        created_by_dispatcher_id=uuid.uuid4(),
        status=status,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def patch_participation(monkeypatch: pytest.MonkeyPatch) -> Any:
    def _set(*, participates: bool = True) -> None:
        monkeypatch.setattr(
            uc, "tenant_participates_in_operation", AsyncMock(return_value=participates)
        )

    _set()
    return _set


def _patch_bundle_create(monkeypatch: pytest.MonkeyPatch, bundle: Any) -> None:
    monkeypatch.setattr(OrderBundleRepository, "create", AsyncMock(return_value=bundle))


# ─── bundle_orders: B1 Happy-Path ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_bundle_orders_b1_standard(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    tenant_id = uuid.uuid4()
    orders = [_order(operation_id=op.id) for _ in range(3)]
    vehicle = _vehicle(tenant_id=tenant_id)
    bundle = _bundle(operation_id=op.id)

    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_ids", AsyncMock(return_value=orders))
    _patch_bundle_create(monkeypatch, bundle)
    create_assignment = AsyncMock()
    monkeypatch.setattr(OrderAssignmentRepository, "create", create_assignment)
    session = _FakeSession()

    result = await uc.bundle_orders(
        session=session,  # type: ignore[arg-type]
        operation_id=op.id,
        order_ids=[o.id for o in orders],
        vehicle_id=vehicle.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=tenant_id,
        audit_logger=_audit(),
        realtime=_realtime(),
    )

    assert result is bundle
    # Alle Orders zugeordnet + auf assigned.
    assert all(o.bundle_id == bundle.id for o in orders)
    assert all(o.status == ops_models.ORDER_STATUS_ASSIGNED for o in orders)
    # Ein Assignment pro Order, alle mit bundle_id + VT.
    assert create_assignment.await_count == 3
    for call in create_assignment.await_args_list:
        assert call.kwargs["bundle_id"] == bundle.id
        assert call.kwargs["vehicle_id"] == vehicle.id
    # Audit-Eintrag orders_bundled.
    assert any(getattr(o, "action_type", None) == ACTION_ORDERS_BUNDLED for o in session.added)


@pytest.mark.asyncio
async def test_bundle_orders_deduplicates_ids(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    """Doppelte IDs werden zusammengefasst — ein Assignment je eindeutiger Order."""
    op = _operation()
    tenant_id = uuid.uuid4()
    orders = [_order(operation_id=op.id) for _ in range(2)]
    vehicle = _vehicle(tenant_id=tenant_id)
    bundle = _bundle(operation_id=op.id)

    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_ids", AsyncMock(return_value=orders))
    _patch_bundle_create(monkeypatch, bundle)
    create_assignment = AsyncMock()
    monkeypatch.setattr(OrderAssignmentRepository, "create", create_assignment)

    await uc.bundle_orders(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        order_ids=[orders[0].id, orders[1].id, orders[0].id],  # Duplikat
        vehicle_id=vehicle.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=tenant_id,
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert create_assignment.await_count == 2


# ─── bundle_orders: Fehlerklassen ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_bundle_orders_operation_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=None))
    with pytest.raises(OperationNotFoundError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            order_ids=[uuid.uuid4(), uuid.uuid4()],
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_b8_not_participant(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    patch_participation(participates=False)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    with pytest.raises(NotParticipantError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[uuid.uuid4(), uuid.uuid4()],
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_operation_closed(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation(status=ops_models.OPERATION_STATUS_CLOSED)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    with pytest.raises(OperationAlreadyClosedError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[uuid.uuid4(), uuid.uuid4()],
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_b7_empty(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    with pytest.raises(EmptyBundleError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[],
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_b6_minimum_two(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    with pytest.raises(MinimumTwoOrdersError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[uuid.uuid4()],
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_vehicle_not_found(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=None))
    with pytest.raises(VehicleNotFoundError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[uuid.uuid4(), uuid.uuid4()],
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_b3_regular_vehicle(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    vehicle = _vehicle(tenant_id=uuid.uuid4(), vtype=VEHICLE_TYPE_REGULAR, mode=None)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    with pytest.raises(VehicleNotSupplyTransporterError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[uuid.uuid4(), uuid.uuid4()],
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_b2_wrong_mode(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    vehicle = _vehicle(tenant_id=uuid.uuid4(), mode=SUPPLY_MODE_OFF)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    with pytest.raises(VehicleNotInLargeOrderModeError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[uuid.uuid4(), uuid.uuid4()],
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_vehicle_tenant_not_participating(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    """I3: Vehicle-Tenant nimmt nicht am Einsatz teil → VehicleNotEligible."""
    op = _operation()
    vehicle = _vehicle(tenant_id=uuid.uuid4())
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    # Dispatcher-Tenant nimmt teil; Vehicle-Tenant nicht.
    monkeypatch.setattr(
        uc, "tenant_participates_in_operation", AsyncMock(side_effect=[True, False])
    )
    with pytest.raises(VehicleNotEligibleError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[uuid.uuid4(), uuid.uuid4()],
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_order_not_found(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    tenant_id = uuid.uuid4()
    vehicle = _vehicle(tenant_id=tenant_id)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    # find_by_ids liefert keine Treffer.
    monkeypatch.setattr(CustomerOrderRepository, "find_by_ids", AsyncMock(return_value=[]))
    with pytest.raises(OrderNotFoundError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[uuid.uuid4(), uuid.uuid4()],
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=tenant_id,
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_b5_order_other_operation(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    tenant_id = uuid.uuid4()
    vehicle = _vehicle(tenant_id=tenant_id)
    good = _order(operation_id=op.id)
    foreign = _order(operation_id=uuid.uuid4())  # andere Operation
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    monkeypatch.setattr(
        CustomerOrderRepository, "find_by_ids", AsyncMock(return_value=[good, foreign])
    )
    with pytest.raises(OrderNotInOperationError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[good.id, foreign.id],
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=tenant_id,
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_b4_already_bundled(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    tenant_id = uuid.uuid4()
    vehicle = _vehicle(tenant_id=tenant_id)
    good = _order(operation_id=op.id)
    bundled = _order(operation_id=op.id, bundle_id=uuid.uuid4())
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    monkeypatch.setattr(
        CustomerOrderRepository, "find_by_ids", AsyncMock(return_value=[good, bundled])
    )
    with pytest.raises(OrderAlreadyBundledError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[good.id, bundled.id],
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=tenant_id,
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_bundle_orders_order_not_pending(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    tenant_id = uuid.uuid4()
    vehicle = _vehicle(tenant_id=tenant_id)
    good = _order(operation_id=op.id)
    assigned = _order(operation_id=op.id, status=ops_models.ORDER_STATUS_ASSIGNED)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    monkeypatch.setattr(
        CustomerOrderRepository, "find_by_ids", AsyncMock(return_value=[good, assigned])
    )
    with pytest.raises(OrderNotPendingError):
        await uc.bundle_orders(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_ids=[good.id, assigned.id],
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=tenant_id,
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── dissolve_bundle: B9 + Fehlerklassen ───────────────────────────────────────


@pytest.mark.asyncio
async def test_dissolve_bundle_b9_happy(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    bundle = _bundle(operation_id=op.id)
    orders = [
        _order(operation_id=op.id, status=ops_models.ORDER_STATUS_ASSIGNED, bundle_id=bundle.id)
        for _ in range(3)
    ]
    assignments = [
        SimpleNamespace(id=uuid.uuid4(), status=ops_models.ASSIGNMENT_STATUS_ASSIGNED)
        for _ in range(3)
    ]
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", AsyncMock(return_value=bundle))
    monkeypatch.setattr(
        OrderAssignmentRepository, "list_for_bundle", AsyncMock(return_value=assignments)
    )
    monkeypatch.setattr(CustomerOrderRepository, "list_for_bundle", AsyncMock(return_value=orders))
    session = _FakeSession()

    result = await uc.dissolve_bundle(
        session=session,  # type: ignore[arg-type]
        operation_id=op.id,
        bundle_id=bundle.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )

    assert result.status == ops_models.BUNDLE_STATUS_DISSOLVED
    assert all(a.status == ops_models.ASSIGNMENT_STATUS_CANCELLED for a in assignments)
    assert all(o.bundle_id is None for o in orders)
    assert all(o.status == ops_models.ORDER_STATUS_PENDING for o in orders)
    assert any(getattr(o, "action_type", None) == ACTION_BUNDLE_DISSOLVED for o in session.added)


@pytest.mark.asyncio
async def test_dissolve_bundle_keeps_completed_orders(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    """Bereits abgeschlossene Order im Bündel wird beim Auflösen nicht resurrektiert."""
    op = _operation()
    bundle = _bundle(operation_id=op.id)
    done = _order(operation_id=op.id, status=ops_models.ORDER_STATUS_COMPLETED, bundle_id=bundle.id)
    active = _order(
        operation_id=op.id, status=ops_models.ORDER_STATUS_ASSIGNED, bundle_id=bundle.id
    )
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", AsyncMock(return_value=bundle))
    monkeypatch.setattr(OrderAssignmentRepository, "list_for_bundle", AsyncMock(return_value=[]))
    monkeypatch.setattr(
        CustomerOrderRepository, "list_for_bundle", AsyncMock(return_value=[done, active])
    )
    await uc.dissolve_bundle(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        bundle_id=bundle.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert done.status == ops_models.ORDER_STATUS_COMPLETED
    assert active.status == ops_models.ORDER_STATUS_PENDING
    assert done.bundle_id is None
    assert active.bundle_id is None


@pytest.mark.asyncio
async def test_dissolve_bundle_not_found(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", AsyncMock(return_value=None))
    with pytest.raises(BundleNotFoundError):
        await uc.dissolve_bundle(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            bundle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_dissolve_bundle_wrong_operation(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    bundle = _bundle(operation_id=uuid.uuid4())
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", AsyncMock(return_value=bundle))
    with pytest.raises(BundleNotFoundError):
        await uc.dissolve_bundle(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),  # passt nicht zu bundle.operation_id
            bundle_id=bundle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_dissolve_bundle_not_active(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    bundle = _bundle(operation_id=op.id, status=ops_models.BUNDLE_STATUS_COMPLETED)
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", AsyncMock(return_value=bundle))
    with pytest.raises(BundleNotActiveError):
        await uc.dissolve_bundle(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            bundle_id=bundle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── complete_order: implizite Bündel-Vervollständigung (2A) ───────────────────


def _patch_complete_order_common(
    monkeypatch: pytest.MonkeyPatch, *, order: Any, assignment: Any
) -> None:
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository, "find_active_for_order", AsyncMock(return_value=assignment)
    )


@pytest.mark.asyncio
async def test_complete_order_completes_bundle_when_all_done(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    bundle = _bundle(operation_id=op.id)
    order = _order(operation_id=op.id, status=ops_models.ORDER_STATUS_ASSIGNED, bundle_id=bundle.id)
    assignment = SimpleNamespace(
        id=uuid.uuid4(), status=ops_models.ASSIGNMENT_STATUS_ASSIGNED, completed_at=None
    )
    _patch_complete_order_common(monkeypatch, order=order, assignment=assignment)
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", AsyncMock(return_value=bundle))
    # Nach Abschluss: alle (eine) Bündel-Order completed.
    monkeypatch.setattr(CustomerOrderRepository, "list_for_bundle", AsyncMock(return_value=[order]))
    session = _FakeSession()

    await uc.complete_order(
        session=session,  # type: ignore[arg-type]
        operation_id=op.id,
        order_id=order.id,
        actor_dispatcher_id=uuid.uuid4(),
        actor_carer_tenant_id=None,
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )

    assert bundle.status == ops_models.BUNDLE_STATUS_COMPLETED
    assert any(getattr(o, "action_type", None) == ACTION_BUNDLE_COMPLETED for o in session.added)


@pytest.mark.asyncio
async def test_complete_order_bundle_stays_active_when_pending_remains(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    bundle = _bundle(operation_id=op.id)
    order = _order(operation_id=op.id, status=ops_models.ORDER_STATUS_ASSIGNED, bundle_id=bundle.id)
    sibling = _order(
        operation_id=op.id, status=ops_models.ORDER_STATUS_ASSIGNED, bundle_id=bundle.id
    )
    assignment = SimpleNamespace(
        id=uuid.uuid4(), status=ops_models.ASSIGNMENT_STATUS_ASSIGNED, completed_at=None
    )
    _patch_complete_order_common(monkeypatch, order=order, assignment=assignment)
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", AsyncMock(return_value=bundle))
    # sibling noch nicht completed.
    monkeypatch.setattr(
        CustomerOrderRepository, "list_for_bundle", AsyncMock(return_value=[order, sibling])
    )
    session = _FakeSession()

    await uc.complete_order(
        session=session,  # type: ignore[arg-type]
        operation_id=op.id,
        order_id=order.id,
        actor_dispatcher_id=None,
        actor_carer_tenant_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )

    assert bundle.status == ops_models.BUNDLE_STATUS_ACTIVE
    assert not any(
        getattr(o, "action_type", None) == ACTION_BUNDLE_COMPLETED for o in session.added
    )


@pytest.mark.asyncio
async def test_complete_order_without_bundle_skips_bundle_logic(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    order = _order(operation_id=op.id, status=ops_models.ORDER_STATUS_ASSIGNED, bundle_id=None)
    assignment = SimpleNamespace(
        id=uuid.uuid4(), status=ops_models.ASSIGNMENT_STATUS_ASSIGNED, completed_at=None
    )
    _patch_complete_order_common(monkeypatch, order=order, assignment=assignment)
    find_bundle = AsyncMock()
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", find_bundle)

    await uc.complete_order(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        order_id=order.id,
        actor_dispatcher_id=uuid.uuid4(),
        actor_carer_tenant_id=None,
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert order.status == ops_models.ORDER_STATUS_COMPLETED
    find_bundle.assert_not_awaited()


# ─── cancel_order: Einzel-Storno-Sperre im aktiven Bündel (3A) ─────────────────


@pytest.mark.asyncio
async def test_cancel_order_in_active_bundle_rejected(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    bundle = _bundle(operation_id=op.id)
    order = _order(operation_id=op.id, status=ops_models.ORDER_STATUS_ASSIGNED, bundle_id=bundle.id)
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(OrderBundleRepository, "find_by_id", AsyncMock(return_value=bundle))
    with pytest.raises(OrderInActiveBundleError):
        await uc.cancel_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            order_id=order.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_cancel_order_with_dissolved_bundle_allowed(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    """bundle_id None nach Auflösung → Storno wieder erlaubt (kein Block)."""
    op = _operation()
    order = _order(operation_id=op.id, status=ops_models.ORDER_STATUS_PENDING, bundle_id=None)
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository, "find_active_for_order", AsyncMock(return_value=None)
    )
    result = await uc.cancel_order(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        order_id=order.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result.status == ops_models.ORDER_STATUS_CANCELLED


# ─── OrderBundleRepository (B10/B11 + CRUD) ────────────────────────────────────


class _ScalarResult:
    def __init__(self, *, single: Any = None, many: list[Any] | None = None) -> None:
        self._single = single
        self._many = many or []

    def scalar_one(self) -> Any:
        return self._single

    def scalars(self) -> _ScalarResult:
        return self

    def all(self) -> list[Any]:
        return self._many


class _QueueSession:
    """Liefert ``execute``-Ergebnisse aus einer Queue (für mehrfache Calls)."""

    def __init__(self, results: list[_ScalarResult], *, get_obj: Any = None) -> None:
        self._results = list(results)
        self._get_obj = get_obj
        self.added: list[Any] = []
        self.flushes = 0

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1

    async def get(self, _model: Any, _pk: Any) -> Any:
        return self._get_obj

    async def execute(self, _stmt: Any) -> _ScalarResult:
        return self._results.pop(0)


@pytest.mark.asyncio
async def test_count_for_operation_b10_two_bundles_seven_orders() -> None:
    """B10: 2 gezählte Bündel (active+completed), 3+4 = 7 Orders."""
    session = _QueueSession([_ScalarResult(single=2), _ScalarResult(single=7)])
    bundling_count, bundled_order_count = await OrderBundleRepository.count_for_operation(
        session,  # type: ignore[arg-type]
        uuid.uuid4(),
    )
    assert bundling_count == 2
    assert bundled_order_count == 7


@pytest.mark.asyncio
async def test_count_for_operation_b11_dissolved_not_counted() -> None:
    """B11: 1 aktives + 1 aufgelöstes Bündel → bundling_count=1, nur aktive Orders."""
    session = _QueueSession([_ScalarResult(single=1), _ScalarResult(single=3)])
    bundling_count, bundled_order_count = await OrderBundleRepository.count_for_operation(
        session,  # type: ignore[arg-type]
        uuid.uuid4(),
    )
    assert bundling_count == 1
    assert bundled_order_count == 3


@pytest.mark.asyncio
async def test_bundle_repository_create_adds_and_flushes() -> None:
    session = _QueueSession([])
    bundle = await OrderBundleRepository.create(
        session,  # type: ignore[arg-type]
        operation_id=uuid.uuid4(),
        vehicle_id=uuid.uuid4(),
        created_by_dispatcher_id=uuid.uuid4(),
    )
    assert bundle.status == ops_models.BUNDLE_STATUS_ACTIVE
    assert session.added == [bundle]
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_bundle_repository_find_by_id() -> None:
    sentinel = object()
    session = _QueueSession([], get_obj=sentinel)
    assert await OrderBundleRepository.find_by_id(session, uuid.uuid4()) is sentinel  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_bundle_repository_list_for_operation() -> None:
    rows = [object(), object()]
    session = _QueueSession([_ScalarResult(many=rows)])
    assert await OrderBundleRepository.list_for_operation(session, uuid.uuid4()) == rows  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_order_repository_find_by_ids_empty_short_circuit() -> None:
    session = _QueueSession([])  # execute darf nicht aufgerufen werden
    assert await CustomerOrderRepository.find_by_ids(session, []) == []  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_order_repository_find_by_ids_nonempty() -> None:
    rows = [object()]
    session = _QueueSession([_ScalarResult(many=rows)])
    assert await CustomerOrderRepository.find_by_ids(session, [uuid.uuid4()]) == rows  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_order_repository_list_for_bundle() -> None:
    rows = [object()]
    session = _QueueSession([_ScalarResult(many=rows)])
    assert await CustomerOrderRepository.list_for_bundle(session, uuid.uuid4()) == rows  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_assignment_repository_create_with_bundle_id() -> None:
    session = _QueueSession([])
    bundle_id = uuid.uuid4()
    assignment = await OrderAssignmentRepository.create(
        session,  # type: ignore[arg-type]
        order_id=uuid.uuid4(),
        vehicle_id=uuid.uuid4(),
        dispatcher_id=uuid.uuid4(),
        bundle_id=bundle_id,
    )
    assert assignment.bundle_id == bundle_id
    assert assignment.status == "assigned"
    assert session.flushes == 1


@pytest.mark.asyncio
async def test_assignment_repository_list_for_bundle() -> None:
    rows = [object()]
    session = _QueueSession([_ScalarResult(many=rows)])
    assert await OrderAssignmentRepository.list_for_bundle(session, uuid.uuid4()) == rows  # type: ignore[arg-type]
