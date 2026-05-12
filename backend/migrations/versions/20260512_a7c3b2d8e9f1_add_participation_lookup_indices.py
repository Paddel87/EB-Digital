"""add participation lookup indices

Phase 2 Schritt 2.4: zwei zusätzliche Indizes auf
``operation_tenant_participation`` für die in
``architecture.md`` Abschnitt 4 (Schnittstelle S10) spezifizierten
Lookup-Pfade. Die 2.1-Migration ``c1465f544fd0`` hatte diese versehentlich
ausgelassen — der Composite-PK liefert nur ``(operation_id, tenant_id)``,
nicht aber die spiegelverkehrte Reihenfolge oder den ``(operation_id, role)``-
Pfad.

Indizes:
  • ``ix_operation_tenant_participation_tenant_id_operation_id`` — für
    ``list_operations_for_tenant(tenant_id)`` (alle Operations eines Mandanten).
  • ``ix_operation_tenant_participation_operation_id_role`` — für
    ``owners_of_operation(operation_id)`` (Owner-Lookup mit Role-Filter).

Diese Migration wurde hand-geschrieben (kein Autogenerate), weil im
sandbox-Worktree kein Docker für eine laufende Postgres-Instanz verfügbar
ist. Verifikation erfolgt im Compose-Smoke-Test (``scripts/dev-smoke.sh``)
über ``alembic upgrade head`` gegen die ``db-init``-Routine. Beide Indizes
sind additiv und nicht-disruptiv (kein Datenverlust beim Up- oder
Downgrade).

Revision ID: a7c3b2d8e9f1
Revises: f14e7ecace66
Create Date: 2026-05-12 22:30:00+00:00

"""

from __future__ import annotations

from collections.abc import Sequence

from alembic import op

revision: str = "a7c3b2d8e9f1"
down_revision: str | None = "f14e7ecace66"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "ix_operation_tenant_participation_tenant_id_operation_id",
        "operation_tenant_participation",
        ["tenant_id", "operation_id"],
        unique=False,
    )
    op.create_index(
        "ix_operation_tenant_participation_operation_id_role",
        "operation_tenant_participation",
        ["operation_id", "role"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_operation_tenant_participation_operation_id_role",
        table_name="operation_tenant_participation",
    )
    op.drop_index(
        "ix_operation_tenant_participation_tenant_id_operation_id",
        table_name="operation_tenant_participation",
    )
