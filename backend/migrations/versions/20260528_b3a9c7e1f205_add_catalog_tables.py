"""add catalog tables (catalog_category, catalog_item_base, catalog_item_tenant_extension)

Revision ID: b3a9c7e1f205
Revises: a7c3b2d8e9f1
Create Date: 2026-05-28 14:00:00.000000+00:00

Phase 4 Schritt 4.1 (UMSETZUNG). Erstellt das ``backend/catalog``-Datenmodell
gemäß Detail-Plan-Freigabe 1-D (Kategorien als separate Tabelle) und 2-B
(Tenant-Extension als Schalt-Tabelle für Override **oder** eigenständiges
Tenant-Item). Der CHECK-Constraint ``mode_constraint`` und der Partial-UNIQUE-
Index sichern die beiden Modi auf DB-Ebene; Use-Case-Code erzwingt die
zugehörige Berechtigungs-Disziplin (Regel-014).
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "b3a9c7e1f205"
down_revision: str | None = "a7c3b2d8e9f1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "catalog_category",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_catalog_category")),
        sa.UniqueConstraint("name", name=op.f("uq_catalog_category_name")),
    )
    op.create_table(
        "catalog_item_base",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("unit", sa.String(length=16), nullable=False),
        sa.Column("default_unit_label", sa.String(length=32), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.UUID(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["catalog_category.id"],
            name=op.f("fk_catalog_item_base_category_id_catalog_category"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_catalog_item_base")),
    )
    op.create_table(
        "catalog_item_tenant_extension",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("base_item_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("unit", sa.String(length=16), nullable=True),
        sa.Column("default_unit_label", sa.String(length=32), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category_id", sa.UUID(), nullable=True),
        sa.Column("override_name", sa.String(length=120), nullable=True),
        sa.Column("override_unit_label", sa.String(length=32), nullable=True),
        sa.Column("is_disabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "("
            "    base_item_id IS NOT NULL "
            "    AND name IS NULL AND unit IS NULL "
            "    AND default_unit_label IS NULL AND category_id IS NULL"
            ") OR ("
            "    base_item_id IS NULL "
            "    AND name IS NOT NULL AND unit IS NOT NULL "
            "    AND default_unit_label IS NOT NULL AND category_id IS NOT NULL "
            "    AND override_name IS NULL AND override_unit_label IS NULL"
            ")",
            name=op.f("ck_catalog_item_tenant_extension_mode_constraint"),
        ),
        sa.ForeignKeyConstraint(
            ["base_item_id"],
            ["catalog_item_base.id"],
            name=op.f("fk_catalog_item_tenant_extension_base_item_id_catalog_item_base"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["catalog_category.id"],
            name=op.f("fk_catalog_item_tenant_extension_category_id_catalog_category"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenant.id"],
            name=op.f("fk_catalog_item_tenant_extension_tenant_id_tenant"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_catalog_item_tenant_extension")),
    )
    op.create_index(
        "ix_catalog_item_tenant_extension_tenant_id",
        "catalog_item_tenant_extension",
        ["tenant_id"],
        unique=False,
    )
    op.create_index(
        "ix_catalog_item_tenant_extension_tenant_id_base_item_id_unique",
        "catalog_item_tenant_extension",
        ["tenant_id", "base_item_id"],
        unique=True,
        postgresql_where=sa.text("base_item_id IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index(
        "ix_catalog_item_tenant_extension_tenant_id_base_item_id_unique",
        table_name="catalog_item_tenant_extension",
        postgresql_where=sa.text("base_item_id IS NOT NULL"),
    )
    op.drop_index(
        "ix_catalog_item_tenant_extension_tenant_id",
        table_name="catalog_item_tenant_extension",
    )
    op.drop_table("catalog_item_tenant_extension")
    op.drop_table("catalog_item_base")
    op.drop_table("catalog_category")
