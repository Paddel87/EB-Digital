"""Repository-Layer für ``backend/operations`` (Schritt 4.3a).

Reine CRUD-Helfer auf den Operations-Tabellen plus Tenant-Scope-Queries
über die S10-Funktionen (Regel-013/014). Use-Case-Logik (Audit-Log,
Realtime-Publish, Status-Übergänge, Plausibility-Auflösung) liegt in
``use_cases.py``; das Repository bleibt agnostisch.
"""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.operations.models import (
    BUNDLE_STATUS_ACTIVE,
    BUNDLE_STATUS_COMPLETED,
    CustomerOrder,
    CustomerOrderItem,
    Operation,
    OperationArea,
    OperationAuditLog,
    OperationDispatcherParticipation,
    OrderAssignment,
    OrderBundle,
)
from eb_digital.tenants.models import (
    PARTICIPATION_ROLE_OWNER,
    OperationTenantParticipation,
)


class OperationRepository:
    """CRUD auf ``operation`` plus Owner-Lookup."""

    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        city_label: str,
        url_token: str,
        access_code_active: bool = False,
        access_code_hash: str | None = None,
        plausibility_threshold_m: int | None = None,
    ) -> Operation:
        operation = Operation(
            status="planned",
            city_label=city_label,
            url_token=url_token,
            access_code_active=access_code_active,
            access_code_hash=access_code_hash,
            plausibility_threshold_m=plausibility_threshold_m,
        )
        session.add(operation)
        await session.flush()
        return operation

    @staticmethod
    async def find_by_id(session: AsyncSession, operation_id: uuid.UUID) -> Operation | None:
        result = await session.execute(select(Operation).where(Operation.id == operation_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def find_by_url_token(session: AsyncSession, url_token: str) -> Operation | None:
        result = await session.execute(select(Operation).where(Operation.url_token == url_token))
        return result.scalar_one_or_none()

    @staticmethod
    async def owner_tenant_id(session: AsyncSession, operation_id: uuid.UUID) -> uuid.UUID | None:
        result = await session.execute(
            select(OperationTenantParticipation.tenant_id).where(
                OperationTenantParticipation.operation_id == operation_id,
                OperationTenantParticipation.role == PARTICIPATION_ROLE_OWNER,
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_for_tenant(session: AsyncSession, tenant_id: uuid.UUID) -> list[Operation]:
        # Über S10 hinweg: alle Operations, an denen der Mandant teilnimmt
        # (Phase 1 nur ``owner`` — verhaltensgleich zu „eigene Operations").
        result = await session.execute(
            select(Operation)
            .join(
                OperationTenantParticipation,
                OperationTenantParticipation.operation_id == Operation.id,
            )
            .where(OperationTenantParticipation.tenant_id == tenant_id)
            .order_by(Operation.opened_at.desc().nulls_last(), Operation.id)
        )
        return list(result.scalars().all())


class OperationAreaRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        operation_id: uuid.UUID,
        area_index: int,
        polygon: dict[str, Any],
        label: str | None = None,
    ) -> OperationArea:
        area = OperationArea(
            operation_id=operation_id,
            area_index=area_index,
            label=label,
            polygon=polygon,
        )
        session.add(area)
        await session.flush()
        return area

    @staticmethod
    async def list_for_operation(
        session: AsyncSession, operation_id: uuid.UUID
    ) -> list[OperationArea]:
        result = await session.execute(
            select(OperationArea)
            .where(OperationArea.operation_id == operation_id)
            .order_by(OperationArea.area_index)
        )
        return list(result.scalars().all())

    @staticmethod
    async def delete_all_for_operation(session: AsyncSession, operation_id: uuid.UUID) -> None:
        existing = await OperationAreaRepository.list_for_operation(session, operation_id)
        for area in existing:
            await session.delete(area)
        await session.flush()


class OperationDispatcherParticipationRepository:
    @staticmethod
    async def upsert(
        session: AsyncSession,
        *,
        operation_id: uuid.UUID,
        dispatcher_id: uuid.UUID,
    ) -> OperationDispatcherParticipation:
        existing = await session.get(
            OperationDispatcherParticipation, (operation_id, dispatcher_id)
        )
        if existing:
            # Wiedereintritt — ``left_at`` zurücksetzen.
            existing.left_at = None
            await session.flush()
            return existing
        participation = OperationDispatcherParticipation(
            operation_id=operation_id,
            dispatcher_id=dispatcher_id,
        )
        session.add(participation)
        await session.flush()
        return participation

    @staticmethod
    async def is_participant(
        session: AsyncSession,
        *,
        operation_id: uuid.UUID,
        dispatcher_id: uuid.UUID,
    ) -> bool:
        existing = await session.get(
            OperationDispatcherParticipation, (operation_id, dispatcher_id)
        )
        return existing is not None and existing.left_at is None


class CustomerOrderRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        operation_id: uuid.UUID,
        anonymous_session_id: uuid.UUID | None,
        status: str,
        location_lat: float | None,
        location_lng: float | None,
        location_accuracy_m: float | None,
        location_text: str | None,
        plausibility_outcome: str,
        plausibility_distance_m: float | None,
        plausibility_threshold_m: int,
        plausibility_variant: str,
    ) -> CustomerOrder:
        order = CustomerOrder(
            operation_id=operation_id,
            anonymous_session_id=anonymous_session_id,
            status=status,
            location_lat=location_lat,
            location_lng=location_lng,
            location_accuracy_m=location_accuracy_m,
            location_text=location_text,
            plausibility_outcome=plausibility_outcome,
            plausibility_distance_m=plausibility_distance_m,
            plausibility_threshold_m=plausibility_threshold_m,
            plausibility_variant=plausibility_variant,
        )
        session.add(order)
        await session.flush()
        return order

    @staticmethod
    async def find_by_id(session: AsyncSession, order_id: uuid.UUID) -> CustomerOrder | None:
        return await session.get(CustomerOrder, order_id)

    @staticmethod
    async def list_for_operation(
        session: AsyncSession, operation_id: uuid.UUID
    ) -> list[CustomerOrder]:
        result = await session.execute(
            select(CustomerOrder)
            .where(CustomerOrder.operation_id == operation_id)
            .order_by(CustomerOrder.placed_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def items_for_order(
        session: AsyncSession, order_id: uuid.UUID
    ) -> list[CustomerOrderItem]:
        result = await session.execute(
            select(CustomerOrderItem).where(CustomerOrderItem.order_id == order_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def find_by_ids(session: AsyncSession, order_ids: list[uuid.UUID]) -> list[CustomerOrder]:
        if not order_ids:
            return []
        result = await session.execute(select(CustomerOrder).where(CustomerOrder.id.in_(order_ids)))
        return list(result.scalars().all())

    @staticmethod
    async def list_for_bundle(session: AsyncSession, bundle_id: uuid.UUID) -> list[CustomerOrder]:
        result = await session.execute(
            select(CustomerOrder).where(CustomerOrder.bundle_id == bundle_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def add_item(
        session: AsyncSession,
        *,
        order_id: uuid.UUID,
        base_item_id: uuid.UUID | None,
        tenant_extension_id: uuid.UUID | None,
        quantity: int,
    ) -> CustomerOrderItem:
        item = CustomerOrderItem(
            order_id=order_id,
            base_item_id=base_item_id,
            tenant_extension_id=tenant_extension_id,
            quantity=quantity,
        )
        session.add(item)
        await session.flush()
        return item


class OrderAssignmentRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        order_id: uuid.UUID,
        vehicle_id: uuid.UUID,
        dispatcher_id: uuid.UUID,
        bundle_id: uuid.UUID | None = None,
    ) -> OrderAssignment:
        assignment = OrderAssignment(
            order_id=order_id,
            vehicle_id=vehicle_id,
            dispatcher_id=dispatcher_id,
            status="assigned",
            bundle_id=bundle_id,
        )
        session.add(assignment)
        await session.flush()
        return assignment

    @staticmethod
    async def list_for_bundle(session: AsyncSession, bundle_id: uuid.UUID) -> list[OrderAssignment]:
        result = await session.execute(
            select(OrderAssignment).where(OrderAssignment.bundle_id == bundle_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def find_active_for_order(
        session: AsyncSession, order_id: uuid.UUID
    ) -> OrderAssignment | None:
        result = await session.execute(
            select(OrderAssignment).where(
                OrderAssignment.order_id == order_id,
                OrderAssignment.status.in_(["assigned", "in_progress"]),
            )
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def list_for_operation(
        session: AsyncSession, operation_id: uuid.UUID
    ) -> list[OrderAssignment]:
        result = await session.execute(
            select(OrderAssignment)
            .join(CustomerOrder, CustomerOrder.id == OrderAssignment.order_id)
            .where(CustomerOrder.operation_id == operation_id)
        )
        return list(result.scalars().all())


class OrderBundleRepository:
    @staticmethod
    async def create(
        session: AsyncSession,
        *,
        operation_id: uuid.UUID,
        vehicle_id: uuid.UUID,
        created_by_dispatcher_id: uuid.UUID,
    ) -> OrderBundle:
        bundle = OrderBundle(
            operation_id=operation_id,
            vehicle_id=vehicle_id,
            created_by_dispatcher_id=created_by_dispatcher_id,
            status=BUNDLE_STATUS_ACTIVE,
        )
        session.add(bundle)
        await session.flush()
        return bundle

    @staticmethod
    async def find_by_id(session: AsyncSession, bundle_id: uuid.UUID) -> OrderBundle | None:
        return await session.get(OrderBundle, bundle_id)

    @staticmethod
    async def list_for_operation(
        session: AsyncSession, operation_id: uuid.UUID
    ) -> list[OrderBundle]:
        result = await session.execute(
            select(OrderBundle)
            .where(OrderBundle.operation_id == operation_id)
            .order_by(OrderBundle.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_for_operation(
        session: AsyncSession, operation_id: uuid.UUID
    ) -> tuple[int, int]:
        """Liefert ``(bundling_count, bundled_order_count)`` für das ADR-006-
        Aggregat (additive Spike-J-Erweiterung, ADR-018 §708).

        ``bundling_count`` = Anzahl ``order_bundle`` mit Status
        ``active``/``completed`` (``dissolved`` zählt nicht). ``bundled_order_count``
        = Summe der ``customer_order`` über diese gezählten Bündel.

        Die produktive Aggregat-Schema-Migration kommt erst in Phase 6.5;
        diese Funktion liefert die Zähl-Logik vorab (Detail-Plan 4.3b-6A)
        und wird durch B10/B11 verifiziert.
        """
        counted_statuses = (BUNDLE_STATUS_ACTIVE, BUNDLE_STATUS_COMPLETED)
        bundling_count_result = await session.execute(
            select(func.count(OrderBundle.id)).where(
                OrderBundle.operation_id == operation_id,
                OrderBundle.status.in_(counted_statuses),
            )
        )
        bundling_count = int(bundling_count_result.scalar_one())
        bundled_order_count_result = await session.execute(
            select(func.count(CustomerOrder.id))
            .join(OrderBundle, OrderBundle.id == CustomerOrder.bundle_id)
            .where(
                OrderBundle.operation_id == operation_id,
                OrderBundle.status.in_(counted_statuses),
            )
        )
        bundled_order_count = int(bundled_order_count_result.scalar_one())
        return bundling_count, bundled_order_count


class OperationAuditLogRepository:
    @staticmethod
    async def list_for_operation(
        session: AsyncSession,
        operation_id: uuid.UUID,
        *,
        limit: int = 200,
    ) -> list[OperationAuditLog]:
        result = await session.execute(
            select(OperationAuditLog)
            .where(OperationAuditLog.operation_id == operation_id)
            .order_by(OperationAuditLog.at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())


__all__ = [
    "CustomerOrderRepository",
    "OperationAreaRepository",
    "OperationAuditLogRepository",
    "OperationDispatcherParticipationRepository",
    "OperationRepository",
    "OrderAssignmentRepository",
    "OrderBundleRepository",
]
