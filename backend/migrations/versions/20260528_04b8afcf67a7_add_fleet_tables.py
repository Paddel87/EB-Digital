"""add fleet tables (vehicle, head_office, loadout, loadout_item, loadout_history)

Revision ID: 04b8afcf67a7
Revises: b3a9c7e1f205
Create Date: 2026-05-28 18:00:00.000000+00:00

Phase 4 Schritt 4.2 (UMSETZUNG). Erstellt das ``backend/fleet``-Datenmodell
gemäß Detail-Plan-Freigabe 1A (Single Table Inheritance über ``vehicle.type``),
2A (Modus-Spalte mit CHECK auf Typ-Kombi), 4B (relationale Beladung +
Append-Only-History), 5B (Item-Refs exklusiv Base ODER Tenant-Extension),
6A (HeadOffice in eigener Tabelle).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "04b8afcf67a7"
down_revision: str | None = "b3a9c7e1f205"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1) vehicle ---------------------------------------------------------
    op.create_table(
        "vehicle",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("license_plate", sa.String(length=32), nullable=True),
        sa.Column("capacity_label", sa.String(length=64), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "type IN ('regular', 'supply_transporter')",
            name=op.f("ck_vehicle_type_valid"),
        ),
        sa.CheckConstraint(
            "("
            "    type = 'supply_transporter' "
            "    AND mode IN ('off', 'mobile_supply', 'large_order')"
            ") OR ("
            "    type = 'regular' "
            "    AND mode IS NULL"
            ")",
            name=op.f("ck_vehicle_type_mode_constraint"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name=op.f("fk_vehicle_tenant_id_tenant"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vehicle")),
    )
    op.create_index(
        "ix_vehicle_tenant_id",
        "vehicle",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_vehicle_tenant_id_active",
        "vehicle",
        ["tenant_id"],
        unique=False,
        postgresql_where=sa.text("is_active = TRUE"),
    )

    # 2) tenant_head_office ---------------------------------------------
    op.create_table(
        "tenant_head_office",
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lng", sa.Float(), nullable=False),
        sa.Column("label", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "lat BETWEEN -90 AND 90",
            name=op.f("ck_tenant_head_office_lat_range"),
        ),
        sa.CheckConstraint(
            "lng BETWEEN -180 AND 180",
            name=op.f("ck_tenant_head_office_lng_range"),
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name=op.f("fk_tenant_head_office_tenant_id_tenant"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("tenant_id", name=op.f("pk_tenant_head_office")),
    )

    # 3) vehicle_loadout ------------------------------------------------
    op.create_table(
        "vehicle_loadout",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("vehicle_id", sa.UUID(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_by_dispatcher_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["recorded_by_dispatcher_id"],
            ["dispatcher.id"],
            name=op.f("fk_vehicle_loadout_recorded_by_dispatcher_id_dispatcher"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicle.id"],
            name=op.f("fk_vehicle_loadout_vehicle_id_vehicle"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vehicle_loadout")),
        sa.UniqueConstraint("vehicle_id", name=op.f("uq_vehicle_loadout_vehicle_id")),
    )

    # 4) vehicle_loadout_item -------------------------------------------
    op.create_table(
        "vehicle_loadout_item",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("loadout_id", sa.UUID(), nullable=False),
        sa.Column("base_item_id", sa.UUID(), nullable=True),
        sa.Column("tenant_extension_id", sa.UUID(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "("
            "    base_item_id IS NOT NULL AND tenant_extension_id IS NULL"
            ") OR ("
            "    base_item_id IS NULL AND tenant_extension_id IS NOT NULL"
            ")",
            name=op.f("ck_vehicle_loadout_item_exactly_one_ref"),
        ),
        sa.CheckConstraint(
            "quantity > 0",
            name=op.f("ck_vehicle_loadout_item_quantity_positive"),
        ),
        sa.ForeignKeyConstraint(
            ["base_item_id"],
            ["catalog_item_base.id"],
            name=op.f("fk_vehicle_loadout_item_base_item_id_catalog_item_base"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["loadout_id"],
            ["vehicle_loadout.id"],
            name=op.f("fk_vehicle_loadout_item_loadout_id_vehicle_loadout"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_extension_id"],
            ["catalog_item_tenant_extension.id"],
            name=op.f("fk_vehicle_loadout_item_tenant_extension_id_catalog_item_tenant_extension"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vehicle_loadout_item")),
    )
    op.create_index(
        "ix_vehicle_loadout_item_loadout_base_unique",
        "vehicle_loadout_item",
        ["loadout_id", "base_item_id"],
        unique=True,
        postgresql_where=sa.text("base_item_id IS NOT NULL"),
    )
    op.create_index(
        "ix_vehicle_loadout_item_loadout_extension_unique",
        "vehicle_loadout_item",
        ["loadout_id", "tenant_extension_id"],
        unique=True,
        postgresql_where=sa.text("tenant_extension_id IS NOT NULL"),
    )

    # 5) vehicle_loadout_history (append-only, Frozen JSONB items) ------
    op.create_table(
        "vehicle_loadout_history",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("vehicle_id", sa.UUID(), nullable=False),
        sa.Column("recorded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("recorded_by_dispatcher_id", sa.UUID(), nullable=False),
        sa.Column(
            "items",
            sa.dialects.postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["recorded_by_dispatcher_id"],
            ["dispatcher.id"],
            name=op.f("fk_vehicle_loadout_history_recorded_by_dispatcher_id_dispatcher"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["vehicle_id"],
            ["vehicle.id"],
            name=op.f("fk_vehicle_loadout_history_vehicle_id_vehicle"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_vehicle_loadout_history")),
    )
    op.create_index(
        "ix_vehicle_loadout_history_vehicle_id_recorded_at",
        "vehicle_loadout_history",
        ["vehicle_id", "recorded_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vehicle_loadout_history_vehicle_id_recorded_at",
        table_name="vehicle_loadout_history",
    )
    op.drop_table("vehicle_loadout_history")
    op.drop_index(
        "ix_vehicle_loadout_item_loadout_extension_unique",
        table_name="vehicle_loadout_item",
        postgresql_where=sa.text("tenant_extension_id IS NOT NULL"),
    )
    op.drop_index(
        "ix_vehicle_loadout_item_loadout_base_unique",
        table_name="vehicle_loadout_item",
        postgresql_where=sa.text("base_item_id IS NOT NULL"),
    )
    op.drop_table("vehicle_loadout_item")
    op.drop_table("vehicle_loadout")
    op.drop_table("tenant_head_office")
    op.drop_index(
        "ix_vehicle_tenant_id_active",
        table_name="vehicle",
        postgresql_where=sa.text("is_active = TRUE"),
    )
    op.drop_index(
        "ix_vehicle_tenant_id",
        table_name="vehicle",
    )
    op.drop_table("vehicle")
