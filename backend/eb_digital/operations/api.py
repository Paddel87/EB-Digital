"""FastAPI-Router für ``backend/operations`` (Phase 4 Schritt 4.3a).

Zwei Router:

  • ``router`` unter ``/operations`` — authentifizierte Sub-Surface S8e.
    Rollen-Matrix (Detail-Plan-Freigabe 9A):
      - Dispatcher R/W eigener Tenant (über S10 / Regel-014).
      - Plattform-Admin R-only via ``?tenant_id=<uuid>``.
      - Carer R + ``POST .../complete`` eigener Tenant.
      - Anon → 403 auf S8e.
  • ``anon_order_router`` unter ``/anon`` — anonyme Sub-Surface S2c.
    ``POST /api/anon/{operation_url}/order`` mit Anon-Cookie + Rate-Limit.
    Rate-Limit IP+URL-AND analog ADR-013 mit eigenem Schlüsselraum
    ``operations:ratelimit:anon_order``, 5/15 min — Bestellungen sind
    operativ kein Spamming-Vektor, aber strenger als Catalog-Read (60/15)
    weil sie persistente Effekte haben.
"""

from __future__ import annotations

import uuid
from typing import Annotated, Any, Literal, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request, Response, status
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.api import extract_client_ip, get_db_session, get_valkey_client
from eb_digital.auth.rate_limit import incr_and_check
from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
)
from eb_digital.auth.sessions import SessionUser, get_current_session_user
from eb_digital.auth_anonymous.sessions import get_current_anonymous_session
from eb_digital.fleet.use_cases import VehicleNotSupplyTransporterError
from eb_digital.operations import schemas, use_cases
from eb_digital.operations.audit import AuditLogger
from eb_digital.operations.exceptions import (
    AnonymousSessionInvalidError,
    AnonymousSessionOperationMismatchError,
    BundleNotActiveError,
    BundleNotFoundError,
    CatalogItemNotAvailableError,
    CrossTenantExtensionError,
    EmptyBundleError,
    EmptyOrderError,
    MinimumTwoOrdersError,
    NotParticipantError,
    OperationAlreadyClosedError,
    OperationNotActiveError,
    OperationNotFoundError,
    OrderAlreadyAssignedError,
    OrderAlreadyBundledError,
    OrderInActiveBundleError,
    OrderNotAssignedError,
    OrderNotFoundError,
    OrderNotInModerationError,
    OrderNotInOperationError,
    OrderNotPendingError,
    VehicleNotEligibleError,
    VehicleNotFoundError,
    VehicleNotInLargeOrderModeError,
)
from eb_digital.operations.models import CustomerOrder, Operation, OrderBundle
from eb_digital.operations.realtime_adapter import RealtimeAdapter
from eb_digital.operations.repository import (
    CustomerOrderRepository,
    OperationAreaRepository,
    OperationAuditLogRepository,
    OperationRepository,
    OrderBundleRepository,
)

# ─── Berechtigungs-Helper ───────────────────────────────────────────────────


def _require_session(request: Request) -> SessionUser:
    user = get_current_session_user(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return user


def _require_dispatcher_with_tenant(request: Request) -> tuple[SessionUser, uuid.UUID]:
    user = _require_session(request)
    if user.kind != KIND_DISPATCHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispatcher role required.",
        )
    if user.tenant_id is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Dispatcher session is missing tenant binding.",
        )
    return user, user.tenant_id


def _audit_logger() -> AuditLogger:
    return AuditLogger()


def _realtime() -> RealtimeAdapter:
    return RealtimeAdapter()


# ─── Response-Builder ───────────────────────────────────────────────────────


# Type-Aliases für die Literal-Listen, damit ``cast`` knapp bleibt. Die
# zugrundeliegenden CHECK-Constraints (Migration ``c5e8d2f4a173``) sind die
# DB-seitige Garantie; der ``cast`` markiert die App-Seite davon.
_OperationStatus = Literal["planned", "active", "closed"]
_OrderStatus = Literal[
    "pending",
    "needs_moderation",
    "assigned",
    "in_progress",
    "completed",
    "cancelled",
]
_PlausibilityOutcome = Literal[
    "ACCEPTED",
    "MODERATION_NO_GPS",
    "MODERATION_ACCURACY_TOO_LOW",
    "MODERATION_OUT_OF_RANGE",
]
_BundleStatus = Literal["active", "completed", "dissolved"]


async def _operation_to_out(db: AsyncSession, operation: Operation) -> schemas.OperationOut:
    owner_tenant_id = await OperationRepository.owner_tenant_id(db, operation.id)
    areas = await OperationAreaRepository.list_for_operation(db, operation.id)
    return schemas.OperationOut(
        id=operation.id,
        tenant_id=owner_tenant_id or uuid.UUID(int=0),
        status=cast(_OperationStatus, operation.status),
        city_label=operation.city_label,
        url_token=operation.url_token,
        access_code_active=operation.access_code_active,
        opened_at=operation.opened_at,
        closed_at=operation.closed_at,
        plausibility_threshold_m=operation.plausibility_threshold_m,
        areas=[
            schemas.OperationAreaOut(
                id=a.id, area_index=a.area_index, label=a.label, polygon=a.polygon
            )
            for a in areas
        ],
    )


async def _order_to_out(db: AsyncSession, order: CustomerOrder) -> schemas.OrderOut:
    items = await CustomerOrderRepository.items_for_order(db, order.id)
    return schemas.OrderOut(
        id=order.id,
        operation_id=order.operation_id,
        anonymous_session_id=order.anonymous_session_id,
        placed_at=order.placed_at,
        status=cast(_OrderStatus, order.status),
        location_lat=order.location_lat,
        location_lng=order.location_lng,
        location_accuracy_m=order.location_accuracy_m,
        location_text=order.location_text,
        plausibility_outcome=cast(_PlausibilityOutcome, order.plausibility_outcome),
        plausibility_distance_m=order.plausibility_distance_m,
        plausibility_threshold_m=order.plausibility_threshold_m,
        plausibility_variant=order.plausibility_variant,
        moderation_actor_dispatcher_id=order.moderation_actor_dispatcher_id,
        moderation_at=order.moderation_at,
        items=[
            schemas.OrderItemOut(
                id=i.id,
                base_item_id=i.base_item_id,
                tenant_extension_id=i.tenant_extension_id,
                quantity=i.quantity,
            )
            for i in items
        ],
    )


async def _bundle_to_out(db: AsyncSession, bundle: OrderBundle) -> schemas.OrderBundleOut:
    orders = await CustomerOrderRepository.list_for_bundle(db, bundle.id)
    return schemas.OrderBundleOut(
        id=bundle.id,
        operation_id=bundle.operation_id,
        vehicle_id=bundle.vehicle_id,
        created_by_dispatcher_id=bundle.created_by_dispatcher_id,
        status=cast(_BundleStatus, bundle.status),
        created_at=bundle.created_at,
        order_ids=[o.id for o in orders],
    )


def _exc_to_http(exc: Exception) -> HTTPException:
    """Mapping Domain-Exception → HTTPException (Sub-Surface S8e + S2c)."""
    if isinstance(exc, NotParticipantError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(
        exc,
        (
            OperationNotFoundError,
            OrderNotFoundError,
            VehicleNotFoundError,
            BundleNotFoundError,
        ),
    ):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, OperationAlreadyClosedError):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(
        exc,
        (
            OrderNotPendingError,
            OrderNotInModerationError,
            OrderNotAssignedError,
            OrderAlreadyAssignedError,
            OrderInActiveBundleError,
            BundleNotActiveError,
        ),
    ):
        return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    if isinstance(
        exc,
        (
            OperationNotActiveError,
            CatalogItemNotAvailableError,
            CrossTenantExtensionError,
            EmptyOrderError,
            VehicleNotEligibleError,
            VehicleNotSupplyTransporterError,
            EmptyBundleError,
            MinimumTwoOrdersError,
            OrderAlreadyBundledError,
            OrderNotInOperationError,
            VehicleNotInLargeOrderModeError,
        ),
    ):
        return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    if isinstance(exc, (AnonymousSessionInvalidError, AnonymousSessionOperationMismatchError)):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unhandled error."
    )


# ─── Router (S8e) ───────────────────────────────────────────────────────────

router = APIRouter(prefix="/operations", tags=["operations"])


@router.post(
    "",
    response_model=schemas.OperationOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_403_FORBIDDEN: {"description": "Disponent-Role required."},
    },
)
async def open_operation(
    payload: schemas.OpenOperationRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OperationOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        operation, _plain_code = await use_cases.open_operation(
            session=db,
            tenant_id=tenant_id,
            dispatcher_id=user.id,
            city_label=payload.city_label,
            area_payloads=[(a.area_index, a.label, a.polygon.model_dump()) for a in payload.areas],
            access_code_active=payload.access_code_active,
            plausibility_threshold_m=payload.plausibility_threshold_m,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return await _operation_to_out(db, operation)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.get("", response_model=list[schemas.OperationOut])
async def list_operations(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    tenant_id: Annotated[uuid.UUID | None, Query()] = None,
) -> list[schemas.OperationOut]:
    user = _require_session(request)
    if user.kind == KIND_PLATFORM_ADMIN:
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Platform-Admin must specify ?tenant_id=...",
            )
        effective_tenant_id = tenant_id
    elif user.kind in (KIND_DISPATCHER, KIND_CARER):
        if user.tenant_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant binding.")
        effective_tenant_id = user.tenant_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    operations = await OperationRepository.list_for_tenant(db, effective_tenant_id)
    return [await _operation_to_out(db, op) for op in operations]


@router.get("/{operation_id}", response_model=schemas.OperationOut)
async def get_operation(
    operation_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OperationOut:
    user = _require_session(request)
    operation = await OperationRepository.find_by_id(db, operation_id)
    if operation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found.")
    owner_tenant_id = await OperationRepository.owner_tenant_id(db, operation_id)
    if user.kind != KIND_PLATFORM_ADMIN and user.tenant_id != owner_tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    return await _operation_to_out(db, operation)


@router.post("/{operation_id}/close", response_model=schemas.OperationOut)
async def close_operation_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OperationOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        operation = await use_cases.close_operation(
            session=db,
            operation_id=operation_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return await _operation_to_out(db, operation)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.post("/{operation_id}/areas", response_model=schemas.OperationOut)
async def change_operation_areas_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    payload: schemas.ChangeOperationAreasRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OperationOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        operation = await use_cases.change_operation_areas(
            session=db,
            operation_id=operation_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            area_payloads=[(a.area_index, a.label, a.polygon.model_dump()) for a in payload.areas],
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return await _operation_to_out(db, operation)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.post(
    "/{operation_id}/access-code",
    response_model=schemas.AccessCodeIssueOut,
)
async def toggle_access_code_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    payload: schemas.ToggleAccessCodeRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.AccessCodeIssueOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        operation, plain_code = await use_cases.toggle_access_code(
            session=db,
            operation_id=operation_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            activate=payload.activate,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return schemas.AccessCodeIssueOut(
            access_code_active=operation.access_code_active,
            access_code=plain_code,
        )
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.post(
    "/{operation_id}/supply-transporter-mode",
    response_model=dict[str, Any],
)
async def supply_transporter_mode_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    payload: schemas.SupplyTransporterModeRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        vehicle = await use_cases.switch_supply_transporter_mode(
            session=db,
            operation_id=operation_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            vehicle_id=payload.vehicle_id,
            mode=payload.mode,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return {"vehicle_id": str(vehicle.id), "mode": vehicle.mode}
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.get(
    "/{operation_id}/orders",
    response_model=list[schemas.OrderOut],
)
async def list_orders_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[schemas.OrderOut]:
    user = _require_session(request)
    operation = await OperationRepository.find_by_id(db, operation_id)
    if operation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found.")
    owner_tenant_id = await OperationRepository.owner_tenant_id(db, operation_id)
    if user.kind != KIND_PLATFORM_ADMIN and user.tenant_id != owner_tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    orders = await CustomerOrderRepository.list_for_operation(db, operation_id)
    return [await _order_to_out(db, o) for o in orders]


@router.get(
    "/{operation_id}/orders/{order_id}",
    response_model=schemas.OrderOut,
)
async def get_order_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    order_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OrderOut:
    user = _require_session(request)
    order = await CustomerOrderRepository.find_by_id(db, order_id)
    if order is None or order.operation_id != operation_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    owner_tenant_id = await OperationRepository.owner_tenant_id(db, operation_id)
    if user.kind != KIND_PLATFORM_ADMIN and user.tenant_id != owner_tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    return await _order_to_out(db, order)


@router.post(
    "/{operation_id}/orders/{order_id}/approve-moderated",
    response_model=schemas.OrderOut,
)
async def approve_moderated_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    order_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OrderOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        order = await use_cases.approve_low_plausibility_order(
            session=db,
            operation_id=operation_id,
            order_id=order_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return await _order_to_out(db, order)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.post(
    "/{operation_id}/orders/{order_id}/assignments",
    response_model=schemas.OrderAssignmentOut,
    status_code=status.HTTP_201_CREATED,
)
async def assign_vehicle_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    order_id: Annotated[uuid.UUID, Path()],
    payload: schemas.AssignVehicleRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OrderAssignmentOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        assignment = await use_cases.assign_vehicle(
            session=db,
            operation_id=operation_id,
            order_id=order_id,
            vehicle_id=payload.vehicle_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return schemas.OrderAssignmentOut.model_validate(assignment)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.post(
    "/{operation_id}/orders/{order_id}/cancel",
    response_model=schemas.OrderOut,
)
async def cancel_order_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    order_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OrderOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        order = await use_cases.cancel_order(
            session=db,
            operation_id=operation_id,
            order_id=order_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return await _order_to_out(db, order)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.post(
    "/{operation_id}/orders/{order_id}/complete",
    response_model=schemas.OrderOut,
)
async def complete_order_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    order_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OrderOut:
    user = _require_session(request)
    if user.kind == KIND_DISPATCHER:
        if user.tenant_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant binding.")
        actor_dispatcher_id: uuid.UUID | None = user.id
        actor_carer_tenant_id: uuid.UUID | None = None
        tenant_id = user.tenant_id
    elif user.kind == KIND_CARER:
        if user.tenant_id is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tenant binding.")
        actor_dispatcher_id = None
        actor_carer_tenant_id = user.tenant_id
        tenant_id = user.tenant_id
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    try:
        order = await use_cases.complete_order(
            session=db,
            operation_id=operation_id,
            order_id=order_id,
            actor_dispatcher_id=actor_dispatcher_id,
            actor_carer_tenant_id=actor_carer_tenant_id,
            tenant_id=tenant_id,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return await _order_to_out(db, order)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.get(
    "/{operation_id}/audit-log",
    response_model=list[schemas.AuditLogEntryOut],
)
async def audit_log_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[schemas.AuditLogEntryOut]:
    user = _require_session(request)
    operation = await OperationRepository.find_by_id(db, operation_id)
    if operation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found.")
    owner_tenant_id = await OperationRepository.owner_tenant_id(db, operation_id)
    if user.kind != KIND_PLATFORM_ADMIN and user.tenant_id != owner_tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    entries = await OperationAuditLogRepository.list_for_operation(db, operation_id)
    return [schemas.AuditLogEntryOut.model_validate(e) for e in entries]


# ─── Bündelung (S8e, Schritt 4.3b, ADR-018) ──────────────────────────────────


@router.post(
    "/{operation_id}/bundles",
    response_model=schemas.OrderBundleOut,
    status_code=status.HTTP_201_CREATED,
)
async def create_bundle_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    payload: schemas.BundleOrdersRequest,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OrderBundleOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        bundle = await use_cases.bundle_orders(
            session=db,
            operation_id=operation_id,
            order_ids=payload.order_ids,
            vehicle_id=payload.vehicle_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return await _bundle_to_out(db, bundle)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.post(
    "/{operation_id}/bundles/{bundle_id}/dissolve",
    response_model=schemas.OrderBundleOut,
)
async def dissolve_bundle_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    bundle_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OrderBundleOut:
    user, tenant_id = _require_dispatcher_with_tenant(request)
    try:
        bundle = await use_cases.dissolve_bundle(
            session=db,
            operation_id=operation_id,
            bundle_id=bundle_id,
            dispatcher_id=user.id,
            tenant_id=tenant_id,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
        return await _bundle_to_out(db, bundle)
    except Exception as exc:
        raise _exc_to_http(exc) from exc


@router.get(
    "/{operation_id}/bundles",
    response_model=list[schemas.OrderBundleOut],
)
async def list_bundles_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[schemas.OrderBundleOut]:
    user = _require_session(request)
    operation = await OperationRepository.find_by_id(db, operation_id)
    if operation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found.")
    owner_tenant_id = await OperationRepository.owner_tenant_id(db, operation_id)
    if user.kind != KIND_PLATFORM_ADMIN and user.tenant_id != owner_tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    bundles = await OrderBundleRepository.list_for_operation(db, operation_id)
    return [await _bundle_to_out(db, b) for b in bundles]


@router.get(
    "/{operation_id}/bundles/{bundle_id}",
    response_model=schemas.OrderBundleOut,
)
async def get_bundle_endpoint(
    operation_id: Annotated[uuid.UUID, Path()],
    bundle_id: Annotated[uuid.UUID, Path()],
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.OrderBundleOut:
    user = _require_session(request)
    bundle = await OrderBundleRepository.find_by_id(db, bundle_id)
    if bundle is None or bundle.operation_id != operation_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bundle not found.")
    owner_tenant_id = await OperationRepository.owner_tenant_id(db, operation_id)
    if user.kind != KIND_PLATFORM_ADMIN and user.tenant_id != owner_tenant_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.")
    return await _bundle_to_out(db, bundle)


# ─── Anon-Router (S2c) ──────────────────────────────────────────────────────

anon_order_router = APIRouter(prefix="/anon", tags=["operations_anon"])

# Rate-Limit-Konstanten (Detail-Plan 4.3a-Frage 8A).
_ORDER_RATE_LIMIT = 5
_ORDER_RATE_WINDOW_SECONDS = 15 * 60


def _anon_order_ip_key(ip: str) -> str:
    return f"operations:ratelimit:anon_order:ip:{ip}"


def _anon_order_url_key(url_token: str) -> str:
    return f"operations:ratelimit:anon_order:url:{url_token}"


@anon_order_router.post(
    "/{url_token}/order",
    response_model=schemas.AnonymousOrderOut,
    status_code=status.HTTP_201_CREATED,
)
async def place_anon_order(
    url_token: Annotated[str, Path(min_length=1)],
    payload: schemas.PlaceOrderRequest,
    request: Request,
    response: Response,
    valkey: Annotated[Redis, Depends(get_valkey_client)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> schemas.AnonymousOrderOut:
    """Anonyme Bestellung (Flow F2, ADR-017-Plausibility)."""
    # 1) Rate-Limit (analog ADR-013 IP + URL AND).
    ip = extract_client_ip(request)
    ip_key = _anon_order_ip_key(ip)
    url_key = _anon_order_url_key(url_token)
    ip_result = await incr_and_check(
        valkey, ip_key, limit=_ORDER_RATE_LIMIT, window_seconds=_ORDER_RATE_WINDOW_SECONDS
    )
    url_result = await incr_and_check(
        valkey, url_key, limit=_ORDER_RATE_LIMIT, window_seconds=_ORDER_RATE_WINDOW_SECONDS
    )
    if not (ip_result.allowed and url_result.allowed):
        retry_after = max(ip_result.retry_after_seconds, url_result.retry_after_seconds)
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many order attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    # 2) Operation aus URL-Token auflösen.
    operation = await OperationRepository.find_by_url_token(db, url_token)
    if operation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation not found.")

    # 3) Anon-Session aus Cookie holen + Match prüfen.
    anon = get_current_anonymous_session(request)
    if anon is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No anon session.")
    if anon.operation_id != operation.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session does not belong to this operation.",
        )

    # 4) Use-Case.
    try:
        order, _result = await use_cases.place_order(
            session=db,
            operation_id=operation.id,
            anonymous_session_id=anon.session_id,
            items=[(i.base_item_id, i.tenant_extension_id, i.quantity) for i in payload.items],
            location_lat=payload.location_lat,
            location_lng=payload.location_lng,
            location_accuracy_m=payload.location_accuracy_m,
            location_text=payload.location_text,
            audit_logger=_audit_logger(),
            realtime=_realtime(),
        )
        await db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        raise _exc_to_http(exc) from exc
    return schemas.AnonymousOrderOut(
        id=order.id,
        status=cast(_OrderStatus, order.status),
        plausibility_outcome=cast(_PlausibilityOutcome, order.plausibility_outcome),
        placed_at=order.placed_at,
    )


__all__ = ["anon_order_router", "router"]
