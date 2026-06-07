"""Use-Case-Schicht für ``backend/operations`` (Phase 4 Schritt 4.3a).

Dünne Orchestrierungs-Schicht über den Repositories und Helpern. Audit-
Log-Schreibung läuft explizit am Ende jedes destruktiven oder
konfigurierenden Use-Cases (Detail-Plan 4.3a-Frage 7A). Berechtigungs-
Checks (Disponent eigener Tenant, S10-Teilnahme, Plattform-Admin, Carer)
liegen in der API-Schicht; die Use-Cases bekommen die bereits aufgelösten
``dispatcher_id`` / ``tenant_id`` / ``actor_*`` als Pflicht-Parameter.

Realtime-Publish erfolgt über ``RealtimeAdapter`` (Stub in 4.3a; Valkey-
Pub/Sub in 4.4 — Aufrufstellen bleiben unverändert).

Plausibility-Check (ADR-017) wird im ``place_order``-Use-Case aufgerufen;
``backend/geo.plausibility.check_plausibility`` ist der reine Algorithmus,
``resolve_threshold`` löst die dreistufige Konfigurations-Hierarchie auf.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth_anonymous.access_code import generate_access_code, hash_access_code
from eb_digital.auth_anonymous.tokens import generate_url_token
from eb_digital.catalog import repositories as catalog_repo
from eb_digital.fleet import repositories as fleet_repo
from eb_digital.fleet.models import (
    SUPPLY_MODE_LARGE_ORDER,
    VEHICLE_TYPE_SUPPLY_TRANSPORTER,
    Vehicle,
)
from eb_digital.fleet.use_cases import (
    VehicleNotFoundError as FleetVehicleNotFoundError,
)
from eb_digital.fleet.use_cases import (
    VehicleNotSupplyTransporterError,
)
from eb_digital.fleet.use_cases import (
    update_supply_transporter_mode as fleet_update_supply_transporter_mode,
)
from eb_digital.geo.plausibility import (
    OrderLocation,
    PlausibilityResult,
    PlausibilityThresholds,
    check_plausibility,
    resolve_threshold,
)
from eb_digital.operations import models as ops_models
from eb_digital.operations.audit import (
    ACTION_ACCESS_CODE_TOGGLED,
    ACTION_BUNDLE_COMPLETED,
    ACTION_BUNDLE_DISSOLVED,
    ACTION_OPERATION_AREA_CHANGED,
    ACTION_OPERATION_CLOSED,
    ACTION_OPERATION_OPENED,
    ACTION_ORDER_ASSIGNED,
    ACTION_ORDER_CANCELLED,
    ACTION_ORDER_COMPLETED,
    ACTION_ORDER_MODERATION_APPROVED,
    ACTION_ORDER_PLACED,
    ACTION_ORDERS_BUNDLED,
    ACTION_SUPPLY_TRANSPORTER_MODE_CHANGED,
    TARGET_BUNDLE,
    TARGET_OPERATION,
    TARGET_OPERATION_AREA,
    TARGET_ORDER,
    TARGET_VEHICLE,
    AuditLogger,
)
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
from eb_digital.operations.realtime_adapter import RealtimeAdapter
from eb_digital.operations.repository import (
    CustomerOrderRepository,
    OperationAreaRepository,
    OperationDispatcherParticipationRepository,
    OperationRepository,
    OrderAssignmentRepository,
    OrderBundleRepository,
)
from eb_digital.settings import get_settings
from eb_digital.tenants.models import (
    PARTICIPATION_ROLE_OWNER,
    OperationTenantParticipation,
)
from eb_digital.tenants.participation import tenant_participates_in_operation
from eb_digital.tenants.repositories import find_tenant_by_id


def _topic_lifecycle(operation_id: uuid.UUID) -> str:
    return f"operation.{operation_id}.lifecycle"


def _topic_order_status(operation_id: uuid.UUID) -> str:
    return f"operation.{operation_id}.order_status"


def _topic_assignment(operation_id: uuid.UUID) -> str:
    return f"operation.{operation_id}.assignment"


def _topic_audit_log(operation_id: uuid.UUID) -> str:
    return f"operation.{operation_id}.audit_log"


def _topic_bundle(operation_id: uuid.UUID) -> str:
    return f"operation.{operation_id}.bundle"


async def _require_tenant_participates(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    operation_id: uuid.UUID,
) -> None:
    is_participant = await tenant_participates_in_operation(
        session, tenant_id=tenant_id, operation_id=operation_id
    )
    if not is_participant:
        raise NotParticipantError(
            f"Tenant {tenant_id} does not participate in operation {operation_id}"
        )


async def _resolve_thresholds(
    session: AsyncSession,
    *,
    operation: ops_models.Operation,
    tenant_id: uuid.UUID,
) -> int:
    """Liest Tenant-Default + Operation-Override und gibt den effektiven Wert zurück."""
    tenant = await find_tenant_by_id(session, tenant_id)
    if tenant is None:
        # Sollte nicht passieren — Operation hat Owner.
        raise NotParticipantError(f"Tenant {tenant_id} not found")
    return resolve_threshold(
        tenant_default_m=tenant.plausibility_default_threshold_m,
        operation_override_m=operation.plausibility_threshold_m,
    ).effective_threshold_m


# ─── OpenOperation ──────────────────────────────────────────────────────


async def open_operation(
    *,
    session: AsyncSession,
    tenant_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    city_label: str,
    area_payloads: list[tuple[int, str | None, dict[str, Any]]],
    access_code_active: bool,
    plausibility_threshold_m: int | None,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> tuple[ops_models.Operation, str | None]:
    """Eröffnet einen Einsatz, legt OperationArea(s) + Owner-Participation
    + Dispatcher-Participation an und schreibt Audit-Log.

    Liefert die Operation und (falls AccessCode aktiviert) den Klartext-
    Code, der **einmal** an den Disponenten zurückgegeben wird (UI-
    Anzeige + QR-Render). Der Code wird im DB-Eintrag nur als Hash
    persistiert (ADR-005).
    """
    settings = get_settings()
    operation_uuid = uuid.uuid4()
    url_token = generate_url_token(operation_uuid, settings.secret_key.get_secret_value())
    plain_code: str | None = None
    access_code_hash: str | None = None
    if access_code_active:
        plain_code = generate_access_code()
        access_code_hash = hash_access_code(plain_code)

    # Operation einfügen (Status ``planned`` — Disponent muss noch
    # explizit „aktivieren"; der Übergang ``planned → active`` ist eine
    # additive Konfigurations-Aktion). Phase-1-Pragmatismus: gleich
    # ``active`` setzen, weil planned/active keine harte UX-Trennung
    # haben — eine spätere Phase kann ``planned`` als „in Vorbereitung"
    # reaktivieren.
    operation = ops_models.Operation(
        id=operation_uuid,
        status=ops_models.OPERATION_STATUS_ACTIVE,
        city_label=city_label,
        url_token=url_token,
        access_code_active=access_code_active,
        access_code_hash=access_code_hash,
        plausibility_threshold_m=plausibility_threshold_m,
        opened_at=ops_models._utcnow(),  # noqa: SLF001 — Modul-Helper, kein API-Bruch
    )
    session.add(operation)
    await session.flush()

    # Tenant↔Operation als ``owner`` (Invariante I1 / Regel-013).
    participation = OperationTenantParticipation(
        operation_id=operation.id,
        tenant_id=tenant_id,
        role=PARTICIPATION_ROLE_OWNER,
    )
    session.add(participation)
    await session.flush()

    # Dispatcher als Teilnehmer einbuchen.
    await OperationDispatcherParticipationRepository.upsert(
        session, operation_id=operation.id, dispatcher_id=dispatcher_id
    )

    # Areas anlegen.
    for area_index, label, polygon in area_payloads:
        await OperationAreaRepository.create(
            session,
            operation_id=operation.id,
            area_index=area_index,
            polygon=polygon,
            label=label,
        )

    await audit_logger.log(
        session=session,
        operation_id=operation.id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_OPERATION_OPENED,
        target_kind=TARGET_OPERATION,
        target_id=operation.id,
        payload={
            "city_label": city_label,
            "area_count": len(area_payloads),
            "access_code_active": access_code_active,
            "plausibility_threshold_m": plausibility_threshold_m,
        },
    )
    await realtime.publish(
        topic=_topic_lifecycle(operation.id),
        payload={"event_type": "operation_opened", "operation_id": str(operation.id)},
        tenant_scope=tenant_id,
    )
    return operation, plain_code


# ─── CloseOperation ──────────────────────────────────────────────────────


async def close_operation(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> ops_models.Operation:
    operation = await OperationRepository.find_by_id(session, operation_id)
    if operation is None:
        raise OperationNotFoundError(str(operation_id))
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    if operation.status == ops_models.OPERATION_STATUS_CLOSED:
        raise OperationAlreadyClosedError(str(operation_id))

    operation.status = ops_models.OPERATION_STATUS_CLOSED
    operation.closed_at = ops_models._utcnow()  # noqa: SLF001
    await session.flush()

    await audit_logger.log(
        session=session,
        operation_id=operation.id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_OPERATION_CLOSED,
        target_kind=TARGET_OPERATION,
        target_id=operation.id,
        payload={"closed_at": operation.closed_at.isoformat()},
    )
    await realtime.publish(
        topic=_topic_lifecycle(operation.id),
        payload={"event_type": "operation_closed", "operation_id": str(operation.id)},
        tenant_scope=tenant_id,
    )
    return operation


# ─── ChangeOperationAreas ────────────────────────────────────────────────


async def change_operation_areas(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    area_payloads: list[tuple[int, str | None, dict[str, Any]]],
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> ops_models.Operation:
    operation = await OperationRepository.find_by_id(session, operation_id)
    if operation is None:
        raise OperationNotFoundError(str(operation_id))
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    if operation.status == ops_models.OPERATION_STATUS_CLOSED:
        raise OperationAlreadyClosedError(str(operation_id))

    await OperationAreaRepository.delete_all_for_operation(session, operation_id)
    for area_index, label, polygon in area_payloads:
        await OperationAreaRepository.create(
            session,
            operation_id=operation_id,
            area_index=area_index,
            polygon=polygon,
            label=label,
        )
    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_OPERATION_AREA_CHANGED,
        target_kind=TARGET_OPERATION_AREA,
        target_id=operation_id,
        payload={"area_count": len(area_payloads)},
    )
    await realtime.publish(
        topic=_topic_lifecycle(operation_id),
        payload={"event_type": "operation_area_changed", "operation_id": str(operation_id)},
        tenant_scope=tenant_id,
    )
    return operation


# ─── ToggleAccessCode ────────────────────────────────────────────────────


async def toggle_access_code(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    activate: bool,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> tuple[ops_models.Operation, str | None]:
    operation = await OperationRepository.find_by_id(session, operation_id)
    if operation is None:
        raise OperationNotFoundError(str(operation_id))
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    if operation.status == ops_models.OPERATION_STATUS_CLOSED:
        raise OperationAlreadyClosedError(str(operation_id))

    plain_code: str | None = None
    if activate:
        plain_code = generate_access_code()
        operation.access_code_hash = hash_access_code(plain_code)
        operation.access_code_active = True
    else:
        operation.access_code_hash = None
        operation.access_code_active = False
    await session.flush()

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_ACCESS_CODE_TOGGLED,
        target_kind=TARGET_OPERATION,
        target_id=operation_id,
        payload={"access_code_active": operation.access_code_active},
    )
    await realtime.publish(
        topic=_topic_lifecycle(operation_id),
        payload={
            "event_type": "access_code_toggled",
            "operation_id": str(operation_id),
            "access_code_active": operation.access_code_active,
        },
        tenant_scope=tenant_id,
    )
    return operation, plain_code


# ─── SwitchSupplyTransporterMode (umhüllt Fleet + Audit) ─────────────────


async def switch_supply_transporter_mode(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    mode: str,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> Vehicle:
    """Wechselt den Modus eines Versorgungs-Transporters mit Audit-Log.

    Erfüllt ADR-008/Regel-011 für ``supply_transporter_mode_changed`` —
    in 4.2 hatte ``backend/fleet.update_supply_transporter_mode`` bewusst
    **kein** Audit geschrieben (Detail-Plan 3B). Hier wird der Fleet-
    Use-Case aufgerufen und das Audit dazu geschrieben.
    """
    operation = await OperationRepository.find_by_id(session, operation_id)
    if operation is None:
        raise OperationNotFoundError(str(operation_id))
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    if operation.status == ops_models.OPERATION_STATUS_CLOSED:
        raise OperationAlreadyClosedError(str(operation_id))

    # Vehicle muss zum participating Tenant gehören (I3 für Mode-
    # Wechsel: Fahrzeug eines fremden Tenants ist nicht erreichbar).
    vehicle = await fleet_repo.find_vehicle_by_id(session, vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(str(vehicle_id))
    if vehicle.tenant_id != tenant_id:
        raise VehicleNotEligibleError(str(vehicle_id))

    previous_mode = vehicle.mode
    try:
        vehicle = await fleet_update_supply_transporter_mode(
            session,
            vehicle_id=vehicle_id,
            mode=mode,
        )
    except FleetVehicleNotFoundError as e:
        raise VehicleNotFoundError(str(vehicle_id)) from e
    # ``VehicleNotSupplyTransporterError`` aus dem Fleet-Modul lassen wir
    # 1:1 nach oben durch — die API-Schicht mappt das auf 422.

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_SUPPLY_TRANSPORTER_MODE_CHANGED,
        target_kind=TARGET_VEHICLE,
        target_id=vehicle_id,
        payload={"previous_mode": previous_mode, "new_mode": mode},
    )
    await realtime.publish(
        topic=_topic_lifecycle(operation_id),
        payload={
            "event_type": "supply_transporter_mode_changed",
            "vehicle_id": str(vehicle_id),
            "mode": mode,
        },
        tenant_scope=tenant_id,
    )
    return vehicle


# ─── PlaceOrder (anonym) ─────────────────────────────────────────────────


async def place_order(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    anonymous_session_id: uuid.UUID,
    items: list[tuple[uuid.UUID | None, uuid.UUID | None, int]],
    location_lat: float | None,
    location_lng: float | None,
    location_accuracy_m: float | None,
    location_text: str | None,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> tuple[ops_models.CustomerOrder, PlausibilityResult]:
    """Anonyme Bestellung mit Plausibility-Check (ADR-017).

    Validiert:
      • Operation existiert und ist ``active``.
      • Anon-Session gehört zur Operation (Sicherheit gegen Cookie-Swap).
      • Mindestens ein Item.
      • Catalog-Refs gültig (Base aktiv, Extension nicht-disabled).
      • Tenant-Extension gehört zum Owner-Tenant der Operation.
    Schreibt: ``CustomerOrder`` mit Plausibility-Outcome, ``CustomerOrderItem``s,
    Audit-Log, Realtime-Publish.
    """
    operation = await OperationRepository.find_by_id(session, operation_id)
    if operation is None:
        raise OperationNotFoundError(str(operation_id))
    if operation.status != ops_models.OPERATION_STATUS_ACTIVE:
        raise OperationNotActiveError(str(operation_id))

    # Anon-Session muss zur Operation gehören.
    from eb_digital.auth_anonymous.repositories import find_anonymous_session_by_id

    anon_session = await find_anonymous_session_by_id(session, anonymous_session_id)
    if anon_session is None:
        raise AnonymousSessionInvalidError(str(anonymous_session_id))
    if anon_session.operation_id != operation_id:
        raise AnonymousSessionOperationMismatchError(str(anonymous_session_id))

    if not items:
        raise EmptyOrderError("Order needs at least one item")

    # Tenant-Owner (Phase 1: genau einer; I1).
    owner_tenant_id = await OperationRepository.owner_tenant_id(session, operation_id)
    if owner_tenant_id is None:
        # Datenintegritäts-Bug — Operation ohne Owner.
        raise OperationNotFoundError(str(operation_id))

    # Catalog-Refs validieren.
    for base_id, ext_id, qty in items:
        if qty <= 0:  # Defense-in-Depth — Pydantic ist primär verantwortlich.
            raise EmptyOrderError("Item quantity must be > 0")
        if base_id is not None:
            base = await catalog_repo.find_base_item_by_id(session, base_id)
            if base is None or not base.is_active:
                raise CatalogItemNotAvailableError(f"Base item {base_id} not available")
        if ext_id is not None:
            ext = await catalog_repo.find_extension_by_id(session, ext_id)
            if ext is None or ext.is_disabled:
                raise CatalogItemNotAvailableError(f"Extension {ext_id} not available")
            if ext.tenant_id != owner_tenant_id:
                raise CrossTenantExtensionError(f"Extension {ext_id} belongs to a different tenant")

    # Plausibility-Check (ADR-017).
    threshold_m = await _resolve_thresholds(session, operation=operation, tenant_id=owner_tenant_id)
    areas = await OperationAreaRepository.list_for_operation(session, operation_id)
    polygons = [a.polygon for a in areas]
    location = OrderLocation(
        lat=location_lat,
        lng=location_lng,
        accuracy_m=location_accuracy_m,
        text=location_text,
    )
    result = check_plausibility(
        location=location,
        polygons_geojson=polygons,
        thresholds=ops_thresholds(threshold_m),
    )
    status_value = (
        ops_models.ORDER_STATUS_PENDING
        if result.accepted
        else ops_models.ORDER_STATUS_NEEDS_MODERATION
    )

    order = await CustomerOrderRepository.create(
        session,
        operation_id=operation_id,
        anonymous_session_id=anonymous_session_id,
        status=status_value,
        location_lat=location_lat,
        location_lng=location_lng,
        location_accuracy_m=location_accuracy_m,
        location_text=location_text,
        plausibility_outcome=result.outcome,
        plausibility_distance_m=result.distance_m,
        plausibility_threshold_m=result.threshold_m,
        plausibility_variant=result.variant,
    )
    for base_id, ext_id, qty in items:
        await CustomerOrderRepository.add_item(
            session,
            order_id=order.id,
            base_item_id=base_id,
            tenant_extension_id=ext_id,
            quantity=qty,
        )

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=None,  # anonyme Bestellung — kein Dispatcher
        action_type=ACTION_ORDER_PLACED,
        target_kind=TARGET_ORDER,
        target_id=order.id,
        payload={
            "outcome": result.outcome,
            "distance_m": result.distance_m,
            "threshold_m": result.threshold_m,
            "variant": result.variant,
            "item_count": len(items),
        },
    )
    await realtime.publish(
        topic=_topic_order_status(operation_id),
        payload={
            "event_type": "order_placed",
            "order_id": str(order.id),
            "status": status_value,
        },
        tenant_scope=owner_tenant_id,
    )
    return order, result


def ops_thresholds(value_m: int) -> PlausibilityThresholds:
    """Helper-Konstruktor (Import-Brücke zur ``geo``-Datenklasse)."""
    return PlausibilityThresholds(effective_threshold_m=value_m)


# ─── ApproveLowPlausibilityOrder ─────────────────────────────────────────


async def approve_low_plausibility_order(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    order_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> ops_models.CustomerOrder:
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    order = await CustomerOrderRepository.find_by_id(session, order_id)
    if order is None or order.operation_id != operation_id:
        raise OrderNotFoundError(str(order_id))
    if order.status != ops_models.ORDER_STATUS_NEEDS_MODERATION:
        raise OrderNotInModerationError(str(order_id))

    order.status = ops_models.ORDER_STATUS_PENDING
    order.moderation_actor_dispatcher_id = dispatcher_id
    order.moderation_at = ops_models._utcnow()  # noqa: SLF001
    await session.flush()

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_ORDER_MODERATION_APPROVED,
        target_kind=TARGET_ORDER,
        target_id=order.id,
        payload={"previous_outcome": order.plausibility_outcome},
    )
    await realtime.publish(
        topic=_topic_order_status(operation_id),
        payload={
            "event_type": "order_moderation_approved",
            "order_id": str(order.id),
            "status": ops_models.ORDER_STATUS_PENDING,
        },
        tenant_scope=tenant_id,
    )
    return order


# ─── AssignVehicle (S4 / I3) ─────────────────────────────────────────────


async def assign_vehicle(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    order_id: uuid.UUID,
    vehicle_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> ops_models.OrderAssignment:
    """Erfüllt S4 + Invariante I3.

    Berechtigungs-Check: I3 verlangt, dass der **Vehicle-Tenant** am
    Einsatz teilnimmt — nicht direkter Mandanten-ID-Match mit dem
    aufrufenden Disponenten (das käme der Verbund-Phase entgegen).
    """
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    order = await CustomerOrderRepository.find_by_id(session, order_id)
    if order is None or order.operation_id != operation_id:
        raise OrderNotFoundError(str(order_id))
    if order.status != ops_models.ORDER_STATUS_PENDING:
        raise OrderNotPendingError(str(order_id))
    existing_active = await OrderAssignmentRepository.find_active_for_order(session, order_id)
    if existing_active is not None:
        raise OrderAlreadyAssignedError(str(order_id))

    vehicle = await fleet_repo.find_vehicle_by_id(session, vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(str(vehicle_id))
    # I3: Vehicle-Tenant nimmt teil?
    vehicle_tenant_participates = await tenant_participates_in_operation(
        session, tenant_id=vehicle.tenant_id, operation_id=operation_id
    )
    if not vehicle_tenant_participates:
        raise VehicleNotEligibleError(str(vehicle_id))

    assignment = await OrderAssignmentRepository.create(
        session,
        order_id=order_id,
        vehicle_id=vehicle_id,
        dispatcher_id=dispatcher_id,
    )
    order.status = ops_models.ORDER_STATUS_ASSIGNED
    await session.flush()

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_ORDER_ASSIGNED,
        target_kind=TARGET_ORDER,
        target_id=order_id,
        payload={
            "vehicle_id": str(vehicle_id),
            "assignment_id": str(assignment.id),
            "vehicle_tenant_id": str(vehicle.tenant_id),
        },
    )
    await realtime.publish(
        topic=_topic_assignment(operation_id),
        payload={
            "event_type": "order_assigned",
            "order_id": str(order_id),
            "assignment_id": str(assignment.id),
            "vehicle_id": str(vehicle_id),
        },
        tenant_scope=tenant_id,
    )
    return assignment


# ─── CancelOrder ──────────────────────────────────────────────────────────


async def cancel_order(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    order_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> ops_models.CustomerOrder:
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    order = await CustomerOrderRepository.find_by_id(session, order_id)
    if order is None or order.operation_id != operation_id:
        raise OrderNotFoundError(str(order_id))
    # Einzel-Order-Storno in aktivem Bündel ist Phase 1 nicht erlaubt
    # (Detail-Plan 4.3b-3A / ADR-018 §705) — Bündel zuerst auflösen.
    if order.bundle_id is not None:
        bundle = await OrderBundleRepository.find_by_id(session, order.bundle_id)
        if bundle is not None and bundle.status == ops_models.BUNDLE_STATUS_ACTIVE:
            raise OrderInActiveBundleError(str(order_id))
    if order.status in (
        ops_models.ORDER_STATUS_COMPLETED,
        ops_models.ORDER_STATUS_CANCELLED,
    ):
        raise OrderNotPendingError(str(order_id))

    # Aktives Assignment mit-cancelln.
    active = await OrderAssignmentRepository.find_active_for_order(session, order_id)
    if active is not None:
        active.status = ops_models.ASSIGNMENT_STATUS_CANCELLED
    order.status = ops_models.ORDER_STATUS_CANCELLED
    await session.flush()

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_ORDER_CANCELLED,
        target_kind=TARGET_ORDER,
        target_id=order.id,
        payload={"had_active_assignment": active is not None},
    )
    await realtime.publish(
        topic=_topic_order_status(operation_id),
        payload={
            "event_type": "order_cancelled",
            "order_id": str(order.id),
        },
        tenant_scope=tenant_id,
    )
    return order


# ─── CompleteOrder (Disponent ODER Carer) ────────────────────────────────


async def complete_order(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    order_id: uuid.UUID,
    actor_dispatcher_id: uuid.UUID | None,
    actor_carer_tenant_id: uuid.UUID | None,
    tenant_id: uuid.UUID,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> ops_models.CustomerOrder:
    """Abschluss einer zugewiesenen Bestellung.

    ``actor_dispatcher_id`` ist gesetzt, wenn ein Disponent abschließt;
    ``actor_carer_tenant_id`` ist gesetzt, wenn ein Carer abschließt
    (Audit-Log-Spur — beide Felder schließen sich aus). ``tenant_id`` ist
    der zugehörige Mandant des Akteurs (für Berechtigungs-Check).
    """
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    order = await CustomerOrderRepository.find_by_id(session, order_id)
    if order is None or order.operation_id != operation_id:
        raise OrderNotFoundError(str(order_id))
    if order.status not in (
        ops_models.ORDER_STATUS_ASSIGNED,
        ops_models.ORDER_STATUS_IN_PROGRESS,
    ):
        raise OrderNotAssignedError(str(order_id))

    active = await OrderAssignmentRepository.find_active_for_order(session, order_id)
    if active is None:
        raise OrderNotAssignedError(str(order_id))
    active.status = ops_models.ASSIGNMENT_STATUS_COMPLETED
    active.completed_at = ops_models._utcnow()  # noqa: SLF001
    order.status = ops_models.ORDER_STATUS_COMPLETED
    await session.flush()

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=actor_dispatcher_id,
        action_type=ACTION_ORDER_COMPLETED,
        target_kind=TARGET_ORDER,
        target_id=order.id,
        payload={
            "completed_by_carer_tenant_id": (
                str(actor_carer_tenant_id) if actor_carer_tenant_id else None
            ),
            "assignment_id": str(active.id),
        },
    )
    await realtime.publish(
        topic=_topic_order_status(operation_id),
        payload={
            "event_type": "order_completed",
            "order_id": str(order.id),
        },
        tenant_scope=tenant_id,
    )

    # Implizite Bündel-Vervollständigung (Detail-Plan 4.3b-2A): wenn die
    # abgeschlossene Order Teil eines aktiven Bündels ist und nun alle
    # Geschwister-Orders abgeschlossen sind → Bündel auf ``completed``.
    if order.bundle_id is not None:
        await _maybe_complete_bundle(
            session=session,
            operation_id=operation_id,
            bundle_id=order.bundle_id,
            actor_dispatcher_id=actor_dispatcher_id,
            tenant_id=tenant_id,
            audit_logger=audit_logger,
            realtime=realtime,
        )
    return order


async def _maybe_complete_bundle(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    bundle_id: uuid.UUID,
    actor_dispatcher_id: uuid.UUID | None,
    tenant_id: uuid.UUID,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> None:
    bundle = await OrderBundleRepository.find_by_id(session, bundle_id)
    if bundle is None or bundle.status != ops_models.BUNDLE_STATUS_ACTIVE:
        return
    bundle_orders = await CustomerOrderRepository.list_for_bundle(session, bundle_id)
    if not bundle_orders or any(
        o.status != ops_models.ORDER_STATUS_COMPLETED for o in bundle_orders
    ):
        return

    bundle.status = ops_models.BUNDLE_STATUS_COMPLETED
    await session.flush()

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=actor_dispatcher_id,
        action_type=ACTION_BUNDLE_COMPLETED,
        target_kind=TARGET_BUNDLE,
        target_id=bundle.id,
        payload={"order_count": len(bundle_orders)},
    )
    await realtime.publish(
        topic=_topic_bundle(operation_id),
        payload={
            "event_type": "bundle_completed",
            "bundle_id": str(bundle.id),
        },
        tenant_scope=tenant_id,
    )


# ─── BundleOrders (ADR-018) ──────────────────────────────────────────────


async def bundle_orders(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    order_ids: list[uuid.UUID],
    vehicle_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> ops_models.OrderBundle:
    """Bündelt ≥ 2 ``pending``-Orders auf einen Versorgungs-Transporter im
    ``large_order``-Modus (ADR-018 Use-Case-Vertrag).

    Schritte (ADR-018 §662-688):
      (1) Berechtigung: Tenant nimmt am Einsatz teil (Regel-014).
      (2) Minimum-Constraint: ≥ 2 (eindeutige) Orders.
      (3) Vehicle-Validierung: Versorgungs-Transporter mit ``mode='large_order'``,
          dessen Tenant teilnimmt (I3).
      (4) Order-Validierung: alle gehören zur Operation, Status ``pending``,
          noch nicht gebündelt.
      (5) Erzeuge ``OrderBundle(active)``, setze ``bundle_id`` + Status
          ``assigned`` für alle Orders.
      (6) Erzeuge N ``OrderAssignment`` (eines pro Order) mit identischer
          ``bundle_id`` und identischem ``vehicle_id``.
      (7) Audit-Log ``orders_bundled``.
      (8) Realtime-Publish ``operation.{op}.bundle``.
    """
    operation = await OperationRepository.find_by_id(session, operation_id)
    if operation is None:
        raise OperationNotFoundError(str(operation_id))
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    if operation.status == ops_models.OPERATION_STATUS_CLOSED:
        raise OperationAlreadyClosedError(str(operation_id))

    # (2) Minimum-Constraint auf eindeutigen IDs.
    if not order_ids:
        raise EmptyBundleError("Bundle needs at least one order")
    unique_order_ids = list(dict.fromkeys(order_ids))
    if len(unique_order_ids) < 2:
        raise MinimumTwoOrdersError("Bundle needs at least 2 distinct orders")

    # (3) Vehicle-Validierung.
    vehicle = await fleet_repo.find_vehicle_by_id(session, vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(str(vehicle_id))
    if vehicle.type != VEHICLE_TYPE_SUPPLY_TRANSPORTER:
        raise VehicleNotSupplyTransporterError(vehicle_id)
    if vehicle.mode != SUPPLY_MODE_LARGE_ORDER:
        raise VehicleNotInLargeOrderModeError(str(vehicle_id))
    vehicle_tenant_participates = await tenant_participates_in_operation(
        session, tenant_id=vehicle.tenant_id, operation_id=operation_id
    )
    if not vehicle_tenant_participates:
        raise VehicleNotEligibleError(str(vehicle_id))

    # (4) Order-Validierung.
    orders = await CustomerOrderRepository.find_by_ids(session, unique_order_ids)
    orders_by_id = {o.id: o for o in orders}
    for oid in unique_order_ids:
        order = orders_by_id.get(oid)
        if order is None:
            raise OrderNotFoundError(str(oid))
        if order.operation_id != operation_id:
            raise OrderNotInOperationError(str(oid))
        if order.bundle_id is not None:
            raise OrderAlreadyBundledError(str(oid))
        if order.status != ops_models.ORDER_STATUS_PENDING:
            raise OrderNotPendingError(str(oid))

    # (5) Bündel anlegen, Orders zuordnen.
    bundle = await OrderBundleRepository.create(
        session,
        operation_id=operation_id,
        vehicle_id=vehicle_id,
        created_by_dispatcher_id=dispatcher_id,
    )
    for oid in unique_order_ids:
        order = orders_by_id[oid]
        order.bundle_id = bundle.id
        order.status = ops_models.ORDER_STATUS_ASSIGNED
        # (6) Ein Assignment pro Order mit gemeinsamer bundle_id + VT.
        await OrderAssignmentRepository.create(
            session,
            order_id=oid,
            vehicle_id=vehicle_id,
            dispatcher_id=dispatcher_id,
            bundle_id=bundle.id,
        )
    await session.flush()

    # (7) Audit-Log.
    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_ORDERS_BUNDLED,
        target_kind=TARGET_BUNDLE,
        target_id=bundle.id,
        payload={
            "bundle_id": str(bundle.id),
            "order_ids": [str(oid) for oid in unique_order_ids],
            "vehicle_id": str(vehicle_id),
        },
    )
    # (8) Realtime-Publish.
    await realtime.publish(
        topic=_topic_bundle(operation_id),
        payload={
            "event_type": "orders_bundled",
            "bundle_id": str(bundle.id),
            "order_count": len(unique_order_ids),
            "vehicle_id": str(vehicle_id),
        },
        tenant_scope=tenant_id,
    )
    return bundle


# ─── DissolveBundle (ADR-018) ────────────────────────────────────────────


async def dissolve_bundle(
    *,
    session: AsyncSession,
    operation_id: uuid.UUID,
    bundle_id: uuid.UUID,
    dispatcher_id: uuid.UUID,
    tenant_id: uuid.UUID,
    audit_logger: AuditLogger,
    realtime: RealtimeAdapter,
) -> ops_models.OrderBundle:
    """Löst ein aktives Bündel auf (ADR-018 §703).

    Aktive Assignments des Bündels → ``cancelled``; gebündelte Orders, die
    noch nicht abgeschlossen sind, → ``pending`` zurück; ``bundle_id`` aller
    Orders → ``NULL``; Bündel-Status → ``dissolved``.
    """
    await _require_tenant_participates(session, tenant_id=tenant_id, operation_id=operation_id)
    bundle = await OrderBundleRepository.find_by_id(session, bundle_id)
    if bundle is None or bundle.operation_id != operation_id:
        raise BundleNotFoundError(str(bundle_id))
    if bundle.status != ops_models.BUNDLE_STATUS_ACTIVE:
        raise BundleNotActiveError(str(bundle_id))

    assignments = await OrderAssignmentRepository.list_for_bundle(session, bundle_id)
    for assignment in assignments:
        if assignment.status in (
            ops_models.ASSIGNMENT_STATUS_ASSIGNED,
            ops_models.ASSIGNMENT_STATUS_IN_PROGRESS,
        ):
            assignment.status = ops_models.ASSIGNMENT_STATUS_CANCELLED

    bundle_order_list = await CustomerOrderRepository.list_for_bundle(session, bundle_id)
    for order in bundle_order_list:
        order.bundle_id = None
        if order.status in (
            ops_models.ORDER_STATUS_ASSIGNED,
            ops_models.ORDER_STATUS_IN_PROGRESS,
        ):
            order.status = ops_models.ORDER_STATUS_PENDING

    bundle.status = ops_models.BUNDLE_STATUS_DISSOLVED
    await session.flush()

    await audit_logger.log(
        session=session,
        operation_id=operation_id,
        actor_dispatcher_id=dispatcher_id,
        action_type=ACTION_BUNDLE_DISSOLVED,
        target_kind=TARGET_BUNDLE,
        target_id=bundle.id,
        payload={"order_count": len(bundle_order_list)},
    )
    await realtime.publish(
        topic=_topic_bundle(operation_id),
        payload={
            "event_type": "bundle_dissolved",
            "bundle_id": str(bundle.id),
        },
        tenant_scope=tenant_id,
    )
    return bundle


# Re-Exports zur API-Konsumierung.
__all__ = [
    "approve_low_plausibility_order",
    "assign_vehicle",
    "bundle_orders",
    "cancel_order",
    "change_operation_areas",
    "close_operation",
    "complete_order",
    "dissolve_bundle",
    "open_operation",
    "ops_thresholds",
    "place_order",
    "switch_supply_transporter_mode",
    "toggle_access_code",
]
