"""S10 — Tenant Participation Lookup (ADR-009 Invarianten I1/I2).

Implementiert Regel-014 („Berechtigungs-Filter als Teilnahme-Filter
formulieren"): alle Filter werden als JOIN über
``operation_tenant_participation`` formuliert, **nie** als direkter
``WHERE operation.tenant_id = …``-Vergleich. In Phase 1 verhaltensgleich
zur direkten Variante (genau ein Owner-Eintrag pro Operation), in Phase X
(Verbund-Modus) additiv erweiterbar um ``role='participant'``-Pfade ohne
Refactoring der Filter.

Funktions-Signaturen folgen ``architecture.md`` Abschnitt 4 Schnittstelle
S10. Konsumenten in Phase 2: ``backend/tenants.api`` (Berechtigungs-Filter
für Tenant-Sichtbarkeit). Spätere Konsumenten: ``backend/operations``,
``backend/realtime``, ``backend/export`` (jeweils ab dem Phase-Schritt,
in dem sie Operations-Sichtbarkeit prüfen).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.tenants.models import (
    PARTICIPATION_ROLE_OWNER,
    OperationTenantParticipation,
)


async def list_operations_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[uuid.UUID]:
    """Liefert alle ``operation_id``s, an denen ``tenant_id`` teilnimmt.

    Phase 1: alle Einträge sind ``role='owner'`` — die zurückgegebene
    Liste entspricht „eigene Operations". Phase X: zusätzlich
    Participant-Operationen (gleicher Aufruf, additive Erweiterung).
    """
    stmt = select(OperationTenantParticipation.operation_id).where(
        OperationTenantParticipation.tenant_id == tenant_id,
    )
    return list((await session.execute(stmt)).scalars().all())


async def tenant_participates_in_operation(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    operation_id: uuid.UUID,
) -> bool:
    """``True`` wenn ``tenant_id`` an ``operation_id`` teilnimmt (jede Rolle)."""
    stmt = select(OperationTenantParticipation.operation_id).where(
        OperationTenantParticipation.tenant_id == tenant_id,
        OperationTenantParticipation.operation_id == operation_id,
    )
    result = (await session.execute(stmt)).scalar_one_or_none()
    return result is not None


async def owners_of_operation(
    session: AsyncSession,
    operation_id: uuid.UUID,
) -> list[uuid.UUID]:
    """Liefert alle Owner-``tenant_id``s einer Operation.

    Phase 1 immer Liste mit genau einem Eintrag (Partial-Unique-Index
    ``ix_operation_tenant_participation_owner_unique`` aus 2.1 erzwingt
    das auf DB-Ebene). Leere Liste = Operation existiert nicht oder hat
    keinen Owner — letzteres ist in Phase 1 ein Datenintegritäts-Bug,
    in Phase X potenziell ein Übergangszustand.
    """
    stmt = select(OperationTenantParticipation.tenant_id).where(
        OperationTenantParticipation.operation_id == operation_id,
        OperationTenantParticipation.role == PARTICIPATION_ROLE_OWNER,
    )
    return list((await session.execute(stmt)).scalars().all())


__all__ = [
    "list_operations_for_tenant",
    "owners_of_operation",
    "tenant_participates_in_operation",
]
