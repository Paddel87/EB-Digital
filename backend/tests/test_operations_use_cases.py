"""Tests für ``backend/eb_digital/operations/use_cases`` (Schritt 4.3a).

Strategie: Repository-Klassenmethoden + Cross-Modul-Funktionen werden via
``AsyncMock`` gestubbt; eine minimale ``_FakeSession`` deckt die direkten
``add``/``flush``/``delete``-Aufrufe der Use-Cases ab. ``AuditLogger`` und
``RealtimeAdapter`` werden **real** verwendet (deckt ``audit.py`` +
``realtime_adapter.py`` mit ab). DB-SELECT-Semantik wird separat im
Compose-Smoke und in ``test_operations_repository`` geprüft.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import Any
from unittest.mock import AsyncMock

import pytest

from eb_digital.auth_anonymous import repositories as anon_repo
from eb_digital.catalog import repositories as catalog_repo
from eb_digital.fleet import repositories as fleet_repo
from eb_digital.fleet.models import (
    SUPPLY_MODE_LARGE_ORDER,
    SUPPLY_MODE_OFF,
    VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    Vehicle,
)
from eb_digital.fleet.use_cases import VehicleNotSupplyTransporterError
from eb_digital.operations import models as ops_models
from eb_digital.operations import use_cases as uc
from eb_digital.operations.audit import (
    ACTION_OPERATION_OPENED,
    AuditLogger,
)
from eb_digital.operations.exceptions import (
    AnonymousSessionInvalidError,
    AnonymousSessionOperationMismatchError,
    CatalogItemNotAvailableError,
    CrossTenantExtensionError,
    EmptyOrderError,
    NotParticipantError,
    OperationAlreadyClosedError,
    OperationNotActiveError,
    OperationNotFoundError,
    OrderAlreadyAssignedError,
    OrderNotAssignedError,
    OrderNotFoundError,
    OrderNotInModerationError,
    OrderNotPendingError,
    VehicleNotEligibleError,
    VehicleNotFoundError,
)
from eb_digital.operations.realtime_adapter import RealtimeAdapter
from eb_digital.operations.repository import (
    CustomerOrderRepository,
    OperationAreaRepository,
    OperationDispatcherParticipationRepository,
    OperationRepository,
    OrderAssignmentRepository,
)

_GEOMETRY: dict[str, Any] = {
    "type": "Polygon",
    "coordinates": [[[8.80, 53.07], [8.81, 53.07], [8.81, 53.08], [8.80, 53.07]]],
}


# ─── Fakes ───────────────────────────────────────────────────────────────────


class _FakeSession:
    """Deckt die direkten Session-Operationen der Use-Cases ab."""

    def __init__(self) -> None:
        self.added: list[Any] = []
        self.flushes = 0
        self.deleted: list[Any] = []

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1

    async def delete(self, obj: Any) -> None:
        self.deleted.append(obj)


def _audit() -> AuditLogger:
    return AuditLogger()


def _realtime() -> RealtimeAdapter:
    return RealtimeAdapter()


# ─── Builders ────────────────────────────────────────────────────────────────


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


def _order(*, status: str = ops_models.ORDER_STATUS_PENDING, operation_id: uuid.UUID) -> Any:
    return SimpleNamespace(
        id=uuid.uuid4(),
        operation_id=operation_id,
        status=status,
        plausibility_outcome=ops_models.PLAUSIBILITY_MODERATION_NO_GPS,
        moderation_actor_dispatcher_id=None,
        moderation_at=None,
        bundle_id=None,
        anonymous_session_id=None,
    )


def _vehicle(*, tenant_id: uuid.UUID, mode: str | None = SUPPLY_MODE_OFF) -> Vehicle:
    v = Vehicle(
        tenant_id=tenant_id,
        type=VEHICLE_TYPE_SUPPLY_TRANSPORTER,
        mode=mode,
        name="VT",
        is_active=True,
    )
    v.id = uuid.uuid4()
    v.created_at = datetime.now(UTC)
    v.updated_at = datetime.now(UTC)
    return v


@pytest.fixture
def patch_participation(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Setzt ``tenant_participates_in_operation`` (Default: True)."""

    def _set(*, participates: bool = True) -> None:
        monkeypatch.setattr(
            uc, "tenant_participates_in_operation", AsyncMock(return_value=participates)
        )

    _set()
    return _set


# ─── open_operation ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_open_operation_happy_without_access_code(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        uc,
        "get_settings",
        lambda: SimpleNamespace(secret_key=SimpleNamespace(get_secret_value=lambda: "s")),
    )
    monkeypatch.setattr(OperationDispatcherParticipationRepository, "upsert", AsyncMock())
    monkeypatch.setattr(OperationAreaRepository, "create", AsyncMock())
    session = _FakeSession()

    op, code = await uc.open_operation(
        session=session,  # type: ignore[arg-type]
        tenant_id=uuid.uuid4(),
        dispatcher_id=uuid.uuid4(),
        city_label="Bremen",
        area_payloads=[(1, "Osterdeich", _GEOMETRY)],
        access_code_active=False,
        plausibility_threshold_m=None,
        audit_logger=_audit(),
        realtime=_realtime(),
    )

    assert code is None
    assert op.status == ops_models.OPERATION_STATUS_ACTIVE
    assert op.access_code_hash is None
    OperationAreaRepository.create.assert_awaited_once()
    # Audit-Eintrag wurde an die Session gehängt.
    assert any(getattr(o, "action_type", None) == ACTION_OPERATION_OPENED for o in session.added)


@pytest.mark.asyncio
async def test_open_operation_with_access_code_returns_plaintext(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        uc,
        "get_settings",
        lambda: SimpleNamespace(secret_key=SimpleNamespace(get_secret_value=lambda: "s")),
    )
    monkeypatch.setattr(OperationDispatcherParticipationRepository, "upsert", AsyncMock())
    monkeypatch.setattr(OperationAreaRepository, "create", AsyncMock())

    op, code = await uc.open_operation(
        session=_FakeSession(),  # type: ignore[arg-type]
        tenant_id=uuid.uuid4(),
        dispatcher_id=uuid.uuid4(),
        city_label="Bremen",
        area_payloads=[(1, None, _GEOMETRY)],
        access_code_active=True,
        plausibility_threshold_m=5000,
        audit_logger=_audit(),
        realtime=_realtime(),
    )

    assert code is not None
    assert op.access_code_active is True
    assert op.access_code_hash is not None
    assert code not in op.access_code_hash


# ─── close_operation ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_close_operation_happy(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    result = await uc.close_operation(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result.status == ops_models.OPERATION_STATUS_CLOSED
    assert result.closed_at is not None


@pytest.mark.asyncio
async def test_close_operation_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=None))
    with pytest.raises(OperationNotFoundError):
        await uc.close_operation(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_close_operation_not_participant(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    patch_participation(participates=False)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=_operation()))
    with pytest.raises(NotParticipantError):
        await uc.close_operation(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_close_operation_already_closed(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation(status=ops_models.OPERATION_STATUS_CLOSED)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    with pytest.raises(OperationAlreadyClosedError):
        await uc.close_operation(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── change_operation_areas ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_change_areas_happy(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(OperationAreaRepository, "delete_all_for_operation", AsyncMock())
    monkeypatch.setattr(OperationAreaRepository, "create", AsyncMock())
    result = await uc.change_operation_areas(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        area_payloads=[(1, None, _GEOMETRY), (2, "B", _GEOMETRY)],
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result is op
    OperationAreaRepository.delete_all_for_operation.assert_awaited_once()
    assert OperationAreaRepository.create.await_count == 2


@pytest.mark.asyncio
async def test_change_areas_closed(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation(status=ops_models.OPERATION_STATUS_CLOSED)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    with pytest.raises(OperationAlreadyClosedError):
        await uc.change_operation_areas(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            area_payloads=[(1, None, _GEOMETRY)],
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_change_areas_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=None))
    with pytest.raises(OperationNotFoundError):
        await uc.change_operation_areas(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            area_payloads=[(1, None, _GEOMETRY)],
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── toggle_access_code ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_toggle_access_code_activate(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    result, code = await uc.toggle_access_code(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        activate=True,
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert code is not None
    assert result.access_code_active is True
    assert result.access_code_hash is not None


@pytest.mark.asyncio
async def test_toggle_access_code_deactivate(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    op.access_code_active = True
    op.access_code_hash = "h"
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    result, code = await uc.toggle_access_code(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        activate=False,
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert code is None
    assert result.access_code_active is False
    assert result.access_code_hash is None


# ─── switch_supply_transporter_mode ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_switch_mode_happy(monkeypatch: pytest.MonkeyPatch, patch_participation: Any) -> None:
    tenant_id = uuid.uuid4()
    op = _operation()
    vehicle = _vehicle(tenant_id=tenant_id, mode=SUPPLY_MODE_OFF)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))

    async def _fleet_switch(_s: Any, *, vehicle_id: uuid.UUID, mode: str) -> Vehicle:
        vehicle.mode = mode
        return vehicle

    monkeypatch.setattr(uc, "fleet_update_supply_transporter_mode", _fleet_switch)

    result = await uc.switch_supply_transporter_mode(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=tenant_id,
        vehicle_id=vehicle.id,
        mode=SUPPLY_MODE_LARGE_ORDER,
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result.mode == SUPPLY_MODE_LARGE_ORDER


@pytest.mark.asyncio
async def test_switch_mode_vehicle_not_found(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=None))
    with pytest.raises(VehicleNotFoundError):
        await uc.switch_supply_transporter_mode(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            vehicle_id=uuid.uuid4(),
            mode=SUPPLY_MODE_LARGE_ORDER,
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_switch_mode_vehicle_wrong_tenant(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation()
    vehicle = _vehicle(tenant_id=uuid.uuid4())
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    with pytest.raises(VehicleNotEligibleError):
        await uc.switch_supply_transporter_mode(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),  # ≠ vehicle.tenant_id
            vehicle_id=vehicle.id,
            mode=SUPPLY_MODE_LARGE_ORDER,
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_switch_mode_not_supply_transporter_passthrough(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    tenant_id = uuid.uuid4()
    op = _operation()
    vehicle = _vehicle(tenant_id=tenant_id)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    monkeypatch.setattr(
        uc,
        "fleet_update_supply_transporter_mode",
        AsyncMock(side_effect=VehicleNotSupplyTransporterError(vehicle.id)),
    )
    with pytest.raises(VehicleNotSupplyTransporterError):
        await uc.switch_supply_transporter_mode(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=tenant_id,
            vehicle_id=vehicle.id,
            mode=SUPPLY_MODE_LARGE_ORDER,
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_switch_mode_operation_closed(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op = _operation(status=ops_models.OPERATION_STATUS_CLOSED)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    with pytest.raises(OperationAlreadyClosedError):
        await uc.switch_supply_transporter_mode(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            vehicle_id=uuid.uuid4(),
            mode=SUPPLY_MODE_LARGE_ORDER,
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── place_order ─────────────────────────────────────────────────────────────


def _anon_session(*, operation_id: uuid.UUID) -> Any:
    return SimpleNamespace(id=uuid.uuid4(), operation_id=operation_id)


@pytest.mark.asyncio
async def test_place_order_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    op = _operation()
    tenant_id = uuid.uuid4()
    anon = _anon_session(operation_id=op.id)
    created_order = _order(status=ops_models.ORDER_STATUS_PENDING, operation_id=op.id)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(OperationRepository, "owner_tenant_id", AsyncMock(return_value=tenant_id))
    monkeypatch.setattr(anon_repo, "find_anonymous_session_by_id", AsyncMock(return_value=anon))
    monkeypatch.setattr(
        uc,
        "find_tenant_by_id",
        AsyncMock(return_value=SimpleNamespace(plausibility_default_threshold_m=5000)),
    )
    monkeypatch.setattr(OperationAreaRepository, "list_for_operation", AsyncMock(return_value=[]))
    monkeypatch.setattr(CustomerOrderRepository, "create", AsyncMock(return_value=created_order))
    monkeypatch.setattr(CustomerOrderRepository, "add_item", AsyncMock())
    monkeypatch.setattr(
        catalog_repo,
        "find_base_item_by_id",
        AsyncMock(return_value=SimpleNamespace(is_active=True)),
    )
    monkeypatch.setattr(
        uc,
        "check_plausibility",
        lambda **_kw: SimpleNamespace(
            accepted=True, outcome="ACCEPTED", distance_m=10.0, threshold_m=5000, variant="v"
        ),
    )

    order, result = await uc.place_order(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        anonymous_session_id=anon.id,
        items=[(uuid.uuid4(), None, 2)],
        location_lat=53.07,
        location_lng=8.80,
        location_accuracy_m=10.0,
        location_text=None,
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result.accepted is True
    assert order is created_order
    CustomerOrderRepository.add_item.assert_awaited_once()


@pytest.mark.asyncio
async def test_place_order_moderation(monkeypatch: pytest.MonkeyPatch) -> None:
    op = _operation()
    tenant_id = uuid.uuid4()
    anon = _anon_session(operation_id=op.id)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(OperationRepository, "owner_tenant_id", AsyncMock(return_value=tenant_id))
    monkeypatch.setattr(anon_repo, "find_anonymous_session_by_id", AsyncMock(return_value=anon))
    monkeypatch.setattr(
        uc,
        "find_tenant_by_id",
        AsyncMock(return_value=SimpleNamespace(plausibility_default_threshold_m=5000)),
    )
    monkeypatch.setattr(OperationAreaRepository, "list_for_operation", AsyncMock(return_value=[]))
    captured: dict[str, Any] = {}

    async def _create(_s: Any, **kw: Any) -> Any:
        captured.update(kw)
        return _order(status=kw["status"], operation_id=op.id)

    monkeypatch.setattr(CustomerOrderRepository, "create", _create)
    monkeypatch.setattr(CustomerOrderRepository, "add_item", AsyncMock())
    monkeypatch.setattr(
        catalog_repo,
        "find_extension_by_id",
        AsyncMock(return_value=SimpleNamespace(is_disabled=False, tenant_id=tenant_id)),
    )
    monkeypatch.setattr(
        uc,
        "check_plausibility",
        lambda **_kw: SimpleNamespace(
            accepted=False,
            outcome="MODERATION_NO_GPS",
            distance_m=None,
            threshold_m=5000,
            variant="v",
        ),
    )

    _order_obj, result = await uc.place_order(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op.id,
        anonymous_session_id=anon.id,
        items=[(None, uuid.uuid4(), 1)],
        location_lat=None,
        location_lng=None,
        location_accuracy_m=None,
        location_text="Marktplatz",
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result.accepted is False
    assert captured["status"] == ops_models.ORDER_STATUS_NEEDS_MODERATION


@pytest.mark.asyncio
async def test_place_order_operation_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=None))
    with pytest.raises(OperationNotFoundError):
        await uc.place_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            anonymous_session_id=uuid.uuid4(),
            items=[(uuid.uuid4(), None, 1)],
            location_lat=None,
            location_lng=None,
            location_accuracy_m=None,
            location_text="x",
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_place_order_operation_not_active(monkeypatch: pytest.MonkeyPatch) -> None:
    op = _operation(status=ops_models.OPERATION_STATUS_CLOSED)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    with pytest.raises(OperationNotActiveError):
        await uc.place_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            anonymous_session_id=uuid.uuid4(),
            items=[(uuid.uuid4(), None, 1)],
            location_lat=None,
            location_lng=None,
            location_accuracy_m=None,
            location_text="x",
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_place_order_anon_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    op = _operation()
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(anon_repo, "find_anonymous_session_by_id", AsyncMock(return_value=None))
    with pytest.raises(AnonymousSessionInvalidError):
        await uc.place_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            anonymous_session_id=uuid.uuid4(),
            items=[(uuid.uuid4(), None, 1)],
            location_lat=None,
            location_lng=None,
            location_accuracy_m=None,
            location_text="x",
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_place_order_anon_mismatch(monkeypatch: pytest.MonkeyPatch) -> None:
    op = _operation()
    anon = _anon_session(operation_id=uuid.uuid4())  # andere Operation
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(anon_repo, "find_anonymous_session_by_id", AsyncMock(return_value=anon))
    with pytest.raises(AnonymousSessionOperationMismatchError):
        await uc.place_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            anonymous_session_id=anon.id,
            items=[(uuid.uuid4(), None, 1)],
            location_lat=None,
            location_lng=None,
            location_accuracy_m=None,
            location_text="x",
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_place_order_empty_items(monkeypatch: pytest.MonkeyPatch) -> None:
    op = _operation()
    anon = _anon_session(operation_id=op.id)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(anon_repo, "find_anonymous_session_by_id", AsyncMock(return_value=anon))
    with pytest.raises(EmptyOrderError):
        await uc.place_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            anonymous_session_id=anon.id,
            items=[],
            location_lat=None,
            location_lng=None,
            location_accuracy_m=None,
            location_text="x",
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_place_order_base_item_unavailable(monkeypatch: pytest.MonkeyPatch) -> None:
    op = _operation()
    anon = _anon_session(operation_id=op.id)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(
        OperationRepository, "owner_tenant_id", AsyncMock(return_value=uuid.uuid4())
    )
    monkeypatch.setattr(anon_repo, "find_anonymous_session_by_id", AsyncMock(return_value=anon))
    monkeypatch.setattr(catalog_repo, "find_base_item_by_id", AsyncMock(return_value=None))
    with pytest.raises(CatalogItemNotAvailableError):
        await uc.place_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            anonymous_session_id=anon.id,
            items=[(uuid.uuid4(), None, 1)],
            location_lat=None,
            location_lng=None,
            location_accuracy_m=None,
            location_text="x",
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_place_order_cross_tenant_extension(monkeypatch: pytest.MonkeyPatch) -> None:
    op = _operation()
    anon = _anon_session(operation_id=op.id)
    monkeypatch.setattr(OperationRepository, "find_by_id", AsyncMock(return_value=op))
    monkeypatch.setattr(
        OperationRepository, "owner_tenant_id", AsyncMock(return_value=uuid.uuid4())
    )
    monkeypatch.setattr(anon_repo, "find_anonymous_session_by_id", AsyncMock(return_value=anon))
    monkeypatch.setattr(
        catalog_repo,
        "find_extension_by_id",
        AsyncMock(return_value=SimpleNamespace(is_disabled=False, tenant_id=uuid.uuid4())),
    )
    with pytest.raises(CrossTenantExtensionError):
        await uc.place_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op.id,
            anonymous_session_id=anon.id,
            items=[(None, uuid.uuid4(), 1)],
            location_lat=None,
            location_lng=None,
            location_accuracy_m=None,
            location_text="x",
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── approve_low_plausibility_order ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_approve_happy(monkeypatch: pytest.MonkeyPatch, patch_participation: Any) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_NEEDS_MODERATION, operation_id=op_id)
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    result = await uc.approve_low_plausibility_order(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op_id,
        order_id=order.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result.status == ops_models.ORDER_STATUS_PENDING
    assert result.moderation_actor_dispatcher_id is not None


@pytest.mark.asyncio
async def test_approve_order_not_found(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=None))
    with pytest.raises(OrderNotFoundError):
        await uc.approve_low_plausibility_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            order_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_approve_not_in_moderation(
    monkeypatch: pytest.MonkeyPatch, patch_participation: Any
) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_PENDING, operation_id=op_id)
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    with pytest.raises(OrderNotInModerationError):
        await uc.approve_low_plausibility_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op_id,
            order_id=order.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── assign_vehicle ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_assign_vehicle_happy(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    tenant_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_PENDING, operation_id=op_id)
    vehicle = _vehicle(tenant_id=tenant_id)
    assignment = SimpleNamespace(id=uuid.uuid4())
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository, "find_active_for_order", AsyncMock(return_value=None)
    )
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    monkeypatch.setattr(OrderAssignmentRepository, "create", AsyncMock(return_value=assignment))
    result = await uc.assign_vehicle(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op_id,
        order_id=order.id,
        vehicle_id=vehicle.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=tenant_id,
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result is assignment
    assert order.status == ops_models.ORDER_STATUS_ASSIGNED


@pytest.mark.asyncio
async def test_assign_vehicle_order_not_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_ASSIGNED, operation_id=op_id)
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    with pytest.raises(OrderNotPendingError):
        await uc.assign_vehicle(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op_id,
            order_id=order.id,
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_assign_vehicle_already_assigned(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_PENDING, operation_id=op_id)
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository,
        "find_active_for_order",
        AsyncMock(return_value=SimpleNamespace()),
    )
    with pytest.raises(OrderAlreadyAssignedError):
        await uc.assign_vehicle(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op_id,
            order_id=order.id,
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_assign_vehicle_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_PENDING, operation_id=op_id)
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository, "find_active_for_order", AsyncMock(return_value=None)
    )
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=None))
    with pytest.raises(VehicleNotFoundError):
        await uc.assign_vehicle(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op_id,
            order_id=order.id,
            vehicle_id=uuid.uuid4(),
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_assign_vehicle_not_eligible(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_PENDING, operation_id=op_id)
    vehicle = _vehicle(tenant_id=uuid.uuid4())
    # Order-Operation: teilnehmend; Vehicle-Tenant: nicht teilnehmend.
    monkeypatch.setattr(
        uc, "tenant_participates_in_operation", AsyncMock(side_effect=[True, False])
    )
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository, "find_active_for_order", AsyncMock(return_value=None)
    )
    monkeypatch.setattr(fleet_repo, "find_vehicle_by_id", AsyncMock(return_value=vehicle))
    with pytest.raises(VehicleNotEligibleError):
        await uc.assign_vehicle(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op_id,
            order_id=order.id,
            vehicle_id=vehicle.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── cancel_order ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cancel_order_happy_with_assignment(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_ASSIGNED, operation_id=op_id)
    active = SimpleNamespace(status=ops_models.ASSIGNMENT_STATUS_ASSIGNED)
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository, "find_active_for_order", AsyncMock(return_value=active)
    )
    result = await uc.cancel_order(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op_id,
        order_id=order.id,
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result.status == ops_models.ORDER_STATUS_CANCELLED
    assert active.status == ops_models.ASSIGNMENT_STATUS_CANCELLED


@pytest.mark.asyncio
async def test_cancel_order_terminal_status(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_COMPLETED, operation_id=op_id)
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    with pytest.raises(OrderNotPendingError):
        await uc.cancel_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op_id,
            order_id=order.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_cancel_order_wrong_operation(monkeypatch: pytest.MonkeyPatch) -> None:
    order = _order(status=ops_models.ORDER_STATUS_PENDING, operation_id=uuid.uuid4())
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    with pytest.raises(OrderNotFoundError):
        await uc.cancel_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=uuid.uuid4(),
            order_id=order.id,
            dispatcher_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


# ─── complete_order ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_complete_order_happy(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_ASSIGNED, operation_id=op_id)
    active = SimpleNamespace(
        id=uuid.uuid4(), status=ops_models.ASSIGNMENT_STATUS_ASSIGNED, completed_at=None
    )
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository, "find_active_for_order", AsyncMock(return_value=active)
    )
    result = await uc.complete_order(
        session=_FakeSession(),  # type: ignore[arg-type]
        operation_id=op_id,
        order_id=order.id,
        actor_dispatcher_id=None,
        actor_carer_tenant_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        audit_logger=_audit(),
        realtime=_realtime(),
    )
    assert result.status == ops_models.ORDER_STATUS_COMPLETED
    assert active.status == ops_models.ASSIGNMENT_STATUS_COMPLETED


@pytest.mark.asyncio
async def test_complete_order_not_assigned_status(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_PENDING, operation_id=op_id)
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    with pytest.raises(OrderNotAssignedError):
        await uc.complete_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op_id,
            order_id=order.id,
            actor_dispatcher_id=uuid.uuid4(),
            actor_carer_tenant_id=None,
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )


@pytest.mark.asyncio
async def test_complete_order_no_active_assignment(monkeypatch: pytest.MonkeyPatch) -> None:
    op_id = uuid.uuid4()
    order = _order(status=ops_models.ORDER_STATUS_ASSIGNED, operation_id=op_id)
    monkeypatch.setattr(uc, "tenant_participates_in_operation", AsyncMock(return_value=True))
    monkeypatch.setattr(CustomerOrderRepository, "find_by_id", AsyncMock(return_value=order))
    monkeypatch.setattr(
        OrderAssignmentRepository, "find_active_for_order", AsyncMock(return_value=None)
    )
    with pytest.raises(OrderNotAssignedError):
        await uc.complete_order(
            session=_FakeSession(),  # type: ignore[arg-type]
            operation_id=op_id,
            order_id=order.id,
            actor_dispatcher_id=uuid.uuid4(),
            actor_carer_tenant_id=None,
            tenant_id=uuid.uuid4(),
            audit_logger=_audit(),
            realtime=_realtime(),
        )
