"""add 4.3b bundling table (order_bundle) + nullable bundle_id FK columns

Revision ID: d4f1a9b8c2e6
Revises: c5e8d2f4a173
Create Date: 2026-06-07 10:00:00.000000+00:00

Phase 4 Schritt 4.3b (UMSETZUNG). Erstellt das Bündelungs-Datenmodell
gemäß ADR-018 und Detail-Plan-Freigabe 1A:

  • ``order_bundle`` — eigene Entity (ADR-018 Datenstruktur-Option A).
    Status-Maschine ``('active','completed','dissolved')``. FK
    ``created_by_dispatcher_id → dispatcher.id`` (ADR-018-SQL nannte
    fälschlich ``dispatcher_user``; reale Tabelle ist ``dispatcher``).
  • Additive nullable Spalte ``customer_order.bundle_id`` (FK auf
    ``order_bundle.id``, **kein** ondelete-Cascade → NO ACTION: Bündel
    werden nie zeilenweise gelöscht; NO ACTION ist zugleich cascade-sicher,
    falls eine künftige Operation-Löschung beide Kinder kaskadiert).
  • Additive nullable Spalte ``order_assignment.bundle_id`` (dito).

Aggregat-Erweiterung (``operation_aggregate.bundled_order_count``) bleibt
Phase 6.5 vorbehalten (ADR-018 §710; retention-Modul existiert noch nicht).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "d4f1a9b8c2e6"
down_revision: str | None = "c5e8d2f4a173"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) order_bundle ----------------------------------------------------
    op.create_table(
        "order_bundle",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("operation_id", sa.UUID(), nullable=False),
        sa.Column("vehicle_id", sa.UUID(), nullable=False),
        sa.Column("created_by_dispatcher_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('active', 'completed', 'dissolved')",
            name=op.f("ck_order_bundle_status_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["operation_id"],
            ["operation.id"],
            name=op.f("fk_order_bundle_operation_id_operation"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicle.id"],
            name=op.f("fk_order_bundle_vehicle_id_vehicle"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["created_by_dispatcher_id"],
            ["dispatcher.id"],
            name=op.f("fk_order_bundle_created_by_dispatcher_id_dispatcher"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_bundle")),
    )
    op.create_index(
        "ix_order_bundle_operation_id",
        "order_bundle",
        ["operation_id"],
        unique=False,
    )

    # 2) customer_order.bundle_id (additiv, nullable) --------------------
    op.add_column(
        "customer_order",
        sa.Column("bundle_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_customer_order_bundle_id_order_bundle"),
        "customer_order",
        "order_bundle",
        ["bundle_id"],
        ["id"],
        # NO ACTION (kein ondelete) — Bündel werden nie gelöscht; cascade-sicher.
    )
    op.create_index(
        "ix_customer_order_bundle_id",
        "customer_order",
        ["bundle_id"],
        unique=False,
    )

    # 3) order_assignment.bundle_id (additiv, nullable) ------------------
    op.add_column(
        "order_assignment",
        sa.Column("bundle_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        op.f("fk_order_assignment_bundle_id_order_bundle"),
        "order_assignment",
        "order_bundle",
        ["bundle_id"],
        ["id"],
    )
    op.create_index(
        "ix_order_assignment_bundle_id",
        "order_assignment",
        ["bundle_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_order_assignment_bundle_id", table_name="order_assignment")
    op.drop_constraint(
        op.f("fk_order_assignment_bundle_id_order_bundle"),
        "order_assignment",
        type_="foreignkey",
    )
    op.drop_column("order_assignment", "bundle_id")
    op.drop_index("ix_customer_order_bundle_id", table_name="customer_order")
    op.drop_constraint(
        op.f("fk_customer_order_bundle_id_order_bundle"),
        "customer_order",
        type_="foreignkey",
    )
    op.drop_column("customer_order", "bundle_id")
    op.drop_index("ix_order_bundle_operation_id", table_name="order_bundle")
    op.drop_table("order_bundle")
