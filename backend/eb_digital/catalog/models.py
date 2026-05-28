"""ORM-Modelle für ``backend/catalog`` (Phase 4 Schritt 4.1).

Drei Tabellen:

  • ``catalog_category`` — Kategorien-Stammdaten, Plattform-Admin-gepflegt,
    Name UNIQUE.
  • ``catalog_item_base`` — zentraler Basis-Artikelkatalog, jedes Item
    trägt eine Kategorie (NOT NULL FK), ``is_active``-Flag für Soft-Delete.
  • ``catalog_item_tenant_extension`` — Schalt-Tabelle mit zwei Modi:

    * **Override-Modus** (``base_item_id IS NOT NULL``): überschreibt ein
      Base-Item für genau einen Mandanten. Felder ``override_name`` und
      ``override_unit_label`` sind optional (nur das, was abweichen soll);
      ``is_disabled=TRUE`` blendet das Base-Item für den Mandanten aus.
    * **Eigenständiges-Tenant-Item-Modus** (``base_item_id IS NULL``):
      mandanten-eigenes Item mit allen Pflichtfeldern (Name, Unit,
      Default-Unit-Label, Category).

    Die Modi sind über eine CHECK-Constraint abgesichert. Ein
    Partial-UNIQUE-Index verhindert mehrere Overrides desselben
    Base-Items für denselben Mandanten.

Reifegrad-Wirkung mit Schrittabschluss: VORLÄUFIG → BELASTBAR.
"""

from __future__ import annotations

import uuid

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    Index,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from eb_digital.db import Base, TimestampMixin


class CatalogCategory(Base, TimestampMixin):
    """Kategorie eines Catalog-Items (z. B. ``Getränke``, ``Snacks``).

    Plattform-Admin-gepflegt. ``name`` ist UNIQUE und dient zugleich als
    Anzeigetext. Eine Hierarchie (Eltern-Kategorien) ist in Phase 1 bewusst
    nicht modelliert — additive Erweiterung später möglich.
    """

    __tablename__ = "catalog_category"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)


class CatalogItemBase(Base, TimestampMixin):
    """Basis-Artikelkatalog-Eintrag (plattformweit, Plattform-Admin-gepflegt).

    ``unit`` ist der Maschinen-Bezeichner (``piece``, ``liter`` etc.);
    ``default_unit_label`` ist der deutsche Anzeigetext. Trennung erlaubt
    spätere Lokalisierung ohne Schema-Änderung.

    ``is_active=FALSE`` ist Soft-Delete — Eintrag erscheint nicht mehr im
    effektiven Katalog (cross-tenant), bleibt aber für referenzierende
    Orders auswertbar.
    """

    __tablename__ = "catalog_item_base"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    unit: Mapped[str] = mapped_column(String(16), nullable=False)
    default_unit_label: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_category.id", ondelete="RESTRICT"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class CatalogItemTenantExtension(Base, TimestampMixin):
    """Mandantenspezifische Catalog-Erweiterung.

    Zwei Modi (siehe Modul-Docstring):

      • **Override** — ``base_item_id`` gesetzt; ``name``, ``unit``,
        ``default_unit_label``, ``category_id`` müssen NULL sein.
      • **Eigenständig** — ``base_item_id`` NULL; ``name``, ``unit``,
        ``default_unit_label``, ``category_id`` müssen NOT NULL sein.

    ``is_disabled=TRUE`` blendet ein Override für den Mandanten aus
    (gilt nur im Override-Modus; bei eigenständigen Items wirkt
    ``is_disabled`` analog — eigenes Tenant-Item versteckt).
    """

    __tablename__ = "catalog_item_tenant_extension"
    __table_args__ = (
        # CHECK: entweder Override-Modus (mit base_item_id) oder
        # Eigenständig-Modus (mit allen vier Pflichtfeldern).
        CheckConstraint(
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
            name="mode_constraint",
        ),
        # Höchstens ein Override pro Base-Item pro Tenant. Partial-Index,
        # weil eigenständige Items (base_item_id IS NULL) beliebig
        # mehrfach pro Tenant existieren dürfen.
        Index(
            "ix_catalog_item_tenant_extension_tenant_id_base_item_id_unique",
            "tenant_id",
            "base_item_id",
            unique=True,
            postgresql_where=text("base_item_id IS NOT NULL"),
        ),
        # Lookup-Pfad für den Resolver: alle Extensions eines Tenants.
        Index(
            "ix_catalog_item_tenant_extension_tenant_id",
            "tenant_id",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenant.id", ondelete="CASCADE"),
        nullable=False,
    )
    base_item_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_item_base.id", ondelete="CASCADE"),
        nullable=True,
    )
    # Felder für den Eigenständig-Modus.
    name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(16), nullable=True)
    default_unit_label: Mapped[str | None] = mapped_column(String(32), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("catalog_category.id", ondelete="RESTRICT"),
        nullable=True,
    )
    # Felder für den Override-Modus.
    override_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    override_unit_label: Mapped[str | None] = mapped_column(String(32), nullable=True)
    is_disabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


__all__ = [
    "CatalogCategory",
    "CatalogItemBase",
    "CatalogItemTenantExtension",
]
