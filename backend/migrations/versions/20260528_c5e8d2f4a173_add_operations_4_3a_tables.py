"""add 4.3a operations tables (areas, dispatcher_participation, customer_order, order_assignment)

Revision ID: c5e8d2f4a173
Revises: 04b8afcf67a7
Create Date: 2026-05-28 22:00:00.000000+00:00

Phase 4 Schritt 4.3a (UMSETZUNG). Erstellt das Datenmodell für die
Operations-Domäne ohne Bündelung gemäß Detail-Plan-Freigabe 1A:

  • Additive Spalte ``tenant.plausibility_default_threshold_m`` (Default
    5000 m) — ADR-017 zweite Stufe der Konfigurations-Hierarchie.
  • Additive Spalte ``operation.plausibility_threshold_m`` (nullable) —
    ADR-017 dritte Stufe (Operation-Override).
  • ``operation_area`` (Polygon-Geometrie als JSONB-GeoJSON, Frage 2A).
  • ``operation_dispatcher_participation`` (Teilnehmer-Tabelle, Frage 1A).
  • ``customer_order`` + ``customer_order_item`` (Frage 1A). Tabellenname
    ``customer_order`` statt ``order`` (SQL-reserved).
  • ``order_assignment`` (S4/I3, Frage 5A — Disponent-Manual).

Spike-J-Bündelungs-Tabelle ``order_bundle`` plus nullable FK-Spalten
``customer_order.bundle_id`` und ``order_assignment.bundle_id`` bleiben
Schritt 4.3b vorbehalten (eigene Migration).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c5e8d2f4a173"
down_revision: str | None = "04b8afcf67a7"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) tenant — additive Spalte ----------------------------------------
    op.add_column(
        "tenant",
        sa.Column(
            "plausibility_default_threshold_m",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("5000"),
        ),
    )
    op.create_check_constraint(
        op.f("ck_tenant_plausibility_default_threshold_m_range"),
        "tenant",
        "plausibility_default_threshold_m BETWEEN 50 AND 50000",
    )

    # 2) operation — additive Spalte -------------------------------------
    op.add_column(
        "operation",
        sa.Column("plausibility_threshold_m", sa.Integer(), nullable=True),
    )
    op.create_check_constraint(
        op.f("ck_operation_plausibility_threshold_m_range"),
        "operation",
        "plausibility_threshold_m IS NULL OR plausibility_threshold_m BETWEEN 50 AND 50000",
    )

    # 3) operation_area --------------------------------------------------
    op.create_table(
        "operation_area",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("operation_id", sa.UUID(), nullable=False),
        sa.Column("area_index", sa.Integer(), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column(
            "polygon",
            sa.dialects.postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "polygon ? 'type' AND polygon ? 'coordinates'",
            name=op.f("ck_operation_area_polygon_geojson_keys"),
        ),
        sa.ForeignKeyConstraint(
            ["operation_id"],
            ["operation.id"],
            name=op.f("fk_operation_area_operation_id_operation"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_operation_area")),
        sa.UniqueConstraint(
            "operation_id",
            "area_index",
            name="uq_operation_area_operation_id_area_index",
        ),
    )
    op.create_index(
        "ix_operation_area_operation_id",
        "operation_area",
        ["operation_id"],
        unique=False,
    )

    # 4) operation_dispatcher_participation ------------------------------
    op.create_table(
        "operation_dispatcher_participation",
        sa.Column("operation_id", sa.UUID(), nullable=False),
        sa.Column("dispatcher_id", sa.UUID(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["operation_id"],
            ["operation.id"],
            name=op.f("fk_operation_dispatcher_participation_operation_id_operation"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["dispatcher_id"],
            ["dispatcher.id"],
            name=op.f("fk_operation_dispatcher_participation_dispatcher_id_dispatcher"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "operation_id",
            "dispatcher_id",
            name=op.f("pk_operation_dispatcher_participation"),
        ),
    )

    # 5) customer_order --------------------------------------------------
    op.create_table(
        "customer_order",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("operation_id", sa.UUID(), nullable=False),
        sa.Column("anonymous_session_id", sa.UUID(), nullable=True),
        sa.Column("placed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("location_lat", sa.Float(), nullable=True),
        sa.Column("location_lng", sa.Float(), nullable=True),
        sa.Column("location_accuracy_m", sa.Float(), nullable=True),
        sa.Column("location_text", sa.String(length=255), nullable=True),
        sa.Column("plausibility_outcome", sa.String(length=40), nullable=False),
        sa.Column("plausibility_distance_m", sa.Float(), nullable=True),
        sa.Column("plausibility_threshold_m", sa.Integer(), nullable=False),
        sa.Column("plausibility_variant", sa.String(length=40), nullable=False),
        sa.Column("moderation_actor_dispatcher_id", sa.UUID(), nullable=True),
        sa.Column("moderation_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'needs_moderation', 'assigned', "
            "'in_progress', 'completed', 'cancelled')",
            name=op.f("ck_customer_order_status_allowed"),
        ),
        sa.CheckConstraint(
            "plausibility_outcome IN ('ACCEPTED', 'MODERATION_NO_GPS', "
            "'MODERATION_ACCURACY_TOO_LOW', 'MODERATION_OUT_OF_RANGE')",
            name=op.f("ck_customer_order_plausibility_outcome_allowed"),
        ),
        sa.CheckConstraint(
            "(location_lat IS NULL) = (location_lng IS NULL)",
            name=op.f("ck_customer_order_location_lat_lng_both_or_none"),
        ),
        sa.CheckConstraint(
            "location_lat IS NULL OR location_lat BETWEEN -90 AND 90",
            name=op.f("ck_customer_order_location_lat_range"),
        ),
        sa.CheckConstraint(
            "location_lng IS NULL OR location_lng BETWEEN -180 AND 180",
            name=op.f("ck_customer_order_location_lng_range"),
        ),
        sa.CheckConstraint(
            "location_accuracy_m IS NULL OR location_accuracy_m > 0",
            name=op.f("ck_customer_order_location_accuracy_m_positive"),
        ),
        sa.CheckConstraint(
            "location_lat IS NOT NULL OR location_text IS NOT NULL",
            name=op.f("ck_customer_order_location_gps_or_text_required"),
        ),
        sa.CheckConstraint(
            "plausibility_threshold_m BETWEEN 50 AND 50000",
            name=op.f("ck_customer_order_plausibility_threshold_m_range"),
        ),
        sa.ForeignKeyConstraint(
            ["operation_id"],
            ["operation.id"],
            name=op.f("fk_customer_order_operation_id_operation"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["anonymous_session_id"],
            ["anonymous_session.id"],
            name=op.f("fk_customer_order_anonymous_session_id_anonymous_session"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["moderation_actor_dispatcher_id"],
            ["dispatcher.id"],
            name=op.f("fk_customer_order_moderation_actor_dispatcher_id_dispatcher"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_customer_order")),
    )
    op.create_index(
        "ix_customer_order_operation_id_status",
        "customer_order",
        ["operation_id", "status"],
        unique=False,
    )
    op.create_index(
        "ix_customer_order_operation_id_placed_at",
        "customer_order",
        ["operation_id", "placed_at"],
        unique=False,
    )

    # 6) customer_order_item ---------------------------------------------
    op.create_table(
        "customer_order_item",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("base_item_id", sa.UUID(), nullable=True),
        sa.Column("tenant_extension_id", sa.UUID(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(base_item_id IS NOT NULL AND tenant_extension_id IS NULL) "
            "OR (base_item_id IS NULL AND tenant_extension_id IS NOT NULL)",
            name=op.f("ck_customer_order_item_exactly_one_ref"),
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name=op.f("ck_customer_order_item_quantity_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["customer_order.id"],
            name=op.f("fk_customer_order_item_order_id_customer_order"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["base_item_id"],
            ["catalog_item_base.id"],
            name=op.f("fk_customer_order_item_base_item_id_catalog_item_base"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_extension_id"],
            ["catalog_item_tenant_extension.id"],
            name=op.f("fk_customer_order_item_tenant_extension_id_catalog_item_tenant_extension"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_customer_order_item")),
    )
    op.create_index(
        "ix_customer_order_item_order_id",
        "customer_order_item",
        ["order_id"],
        unique=False,
    )

    # 7) order_assignment ------------------------------------------------
    op.create_table(
        "order_assignment",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("vehicle_id", sa.UUID(), nullable=False),
        sa.Column("dispatcher_id", sa.UUID(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('assigned', 'in_progress', 'completed', 'cancelled')",
            name=op.f("ck_order_assignment_status_allowed"),
        ),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["customer_order.id"],
            name=op.f("fk_order_assignment_order_id_customer_order"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicle.id"],
            name=op.f("fk_order_assignment_vehicle_id_vehicle"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["dispatcher_id"],
            ["dispatcher.id"],
            name=op.f("fk_order_assignment_dispatcher_id_dispatcher"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_assignment")),
    )
    op.create_index(
        "ix_order_assignment_order_id_active_unique",
        "order_assignment",
        ["order_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('assigned', 'in_progress')"),
    )
    op.create_index(
        "ix_order_assignment_vehicle_id",
        "order_assignment",
        ["vehicle_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_order_assignment_vehicle_id", table_name="order_assignment")
    op.drop_index(
        "ix_order_assignment_order_id_active_unique",
        table_name="order_assignment",
        postgresql_where=sa.text("status IN ('assigned', 'in_progress')"),
    )
    op.drop_table("order_assignment")
    op.drop_index("ix_customer_order_item_order_id", table_name="customer_order_item")
    op.drop_table("customer_order_item")
    op.drop_index("ix_customer_order_operation_id_placed_at", table_name="customer_order")
    op.drop_index("ix_customer_order_operation_id_status", table_name="customer_order")
    op.drop_table("customer_order")
    op.drop_table("operation_dispatcher_participation")
    op.drop_index("ix_operation_area_operation_id", table_name="operation_area")
    op.drop_table("operation_area")
    op.drop_constraint(
        op.f("ck_operation_plausibility_threshold_m_range"),
        "operation",
        type_="check",
    )
    op.drop_column("operation", "plausibility_threshold_m")
    op.drop_constraint(
        op.f("ck_tenant_plausibility_default_threshold_m_range"),
        "tenant",
        type_="check",
    )
    op.drop_column("tenant", "plausibility_default_threshold_m")
