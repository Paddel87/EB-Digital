"""Async-Repositories für ``backend/catalog`` (Phase 4 Schritt 4.1).

Drei Repository-Bereiche analog zu den drei ORM-Tabellen:

  • ``CatalogCategory`` — CRUD plus Lookup nach Name (UNIQUE).
  • ``CatalogItemBase`` — CRUD plus Soft-Delete-Toggle ``set_base_item_active``.
  • ``CatalogItemTenantExtension`` — zwei Anlage-Pfade (Override-Modus
    vs. Eigenständig-Modus, getrennte Funktionen, weil sich die
    Pflicht-Felder unterscheiden) plus Update.

DB-Constraint-Verstöße werden hier abgefangen und auf eigene Domain-
Exceptions gemappt; die Use-Case-Schicht fängt diese und mappt sie auf
API-Status-Codes (analog ``tenants.repositories``).
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.catalog.models import (
    CatalogCategory,
    CatalogItemBase,
    CatalogItemTenantExtension,
)

# ─── Domain-Exceptions ───────────────────────────────────────────────────────


class CategoryNameTakenError(Exception):
    """Kategorie-Name existiert bereits (UNIQUE-Verletzung)."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Category name already taken: {name!r}")
        self.name = name


class DuplicateOverrideError(Exception):
    """Override desselben Base-Items für denselben Tenant existiert bereits.

    Folgt aus dem Partial-UNIQUE-Index
    ``ix_catalog_item_tenant_extension_tenant_id_base_item_id_unique``.
    """

    def __init__(self, *, tenant_id: uuid.UUID, base_item_id: uuid.UUID) -> None:
        super().__init__(
            f"Override for base_item {base_item_id} already exists for tenant {tenant_id}.",
        )
        self.tenant_id = tenant_id
        self.base_item_id = base_item_id


# ─── Category-Repository ─────────────────────────────────────────────────────


async def create_category(
    session: AsyncSession,
    *,
    name: str,
) -> CatalogCategory:
    """Legt eine Kategorie an. Bei Namens-Kollision: ``CategoryNameTakenError``."""
    category = CatalogCategory(name=name)
    session.add(category)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        msg = str(exc.orig) if exc.orig is not None else ""
        if "uq_catalog_category_name" in msg:
            raise CategoryNameTakenError(name) from exc
        raise
    return category


async def find_category_by_id(
    session: AsyncSession,
    category_id: uuid.UUID,
) -> CatalogCategory | None:
    return (
        await session.execute(select(CatalogCategory).where(CatalogCategory.id == category_id))
    ).scalar_one_or_none()


async def list_categories(session: AsyncSession) -> list[CatalogCategory]:
    """Alle Kategorien, alphabetisch sortiert nach Name."""
    stmt = select(CatalogCategory).order_by(CatalogCategory.name.asc())
    return list((await session.execute(stmt)).scalars().all())


# ─── BaseItem-Repository ─────────────────────────────────────────────────────


async def create_base_item(
    session: AsyncSession,
    *,
    name: str,
    unit: str,
    default_unit_label: str,
    category_id: uuid.UUID,
    description: str | None = None,
) -> CatalogItemBase:
    """Legt ein Base-Item an. Kategorie muss existieren (FK)."""
    item = CatalogItemBase(
        name=name,
        unit=unit,
        default_unit_label=default_unit_label,
        category_id=category_id,
        description=description,
        is_active=True,
    )
    session.add(item)
    await session.flush()
    return item


async def find_base_item_by_id(
    session: AsyncSession,
    base_item_id: uuid.UUID,
) -> CatalogItemBase | None:
    return (
        await session.execute(select(CatalogItemBase).where(CatalogItemBase.id == base_item_id))
    ).scalar_one_or_none()


async def list_base_items(
    session: AsyncSession,
    *,
    include_inactive: bool = False,
) -> list[CatalogItemBase]:
    """Alle Base-Items, alphabetisch sortiert.

    ``include_inactive=False`` (Default) versteckt Soft-Delete-Einträge.
    Plattform-Admin sieht mit ``include_inactive=True`` auch deaktivierte
    Items (für Reaktivierung).
    """
    stmt = select(CatalogItemBase).order_by(CatalogItemBase.name.asc())
    if not include_inactive:
        stmt = stmt.where(CatalogItemBase.is_active.is_(True))
    return list((await session.execute(stmt)).scalars().all())


async def update_base_item(
    session: AsyncSession,
    *,
    base_item_id: uuid.UUID,
    name: str | None = None,
    unit: str | None = None,
    default_unit_label: str | None = None,
    category_id: uuid.UUID | None = None,
    description: str | None = None,
    is_active: bool | None = None,
) -> CatalogItemBase | None:
    """Aktualisiert ein Base-Item per PATCH-Semantik.

    ``None`` heißt „nicht ändern". Liefert das aktualisierte Item zurück,
    oder ``None`` wenn die ID nicht existiert.
    """
    item = await find_base_item_by_id(session, base_item_id)
    if item is None:
        return None
    if name is not None:
        item.name = name
    if unit is not None:
        item.unit = unit
    if default_unit_label is not None:
        item.default_unit_label = default_unit_label
    if category_id is not None:
        item.category_id = category_id
    if description is not None:
        item.description = description
    if is_active is not None:
        item.is_active = is_active
    await session.flush()
    return item


# ─── TenantExtension-Repository ──────────────────────────────────────────────


async def create_override(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    base_item_id: uuid.UUID,
    override_name: str | None = None,
    override_unit_label: str | None = None,
) -> CatalogItemTenantExtension:
    """Legt einen Override eines Base-Items für einen Tenant an.

    Bei doppeltem Override (Partial-UNIQUE-Verletzung) wird
    ``DuplicateOverrideError`` geworfen.
    """
    ext = CatalogItemTenantExtension(
        tenant_id=tenant_id,
        base_item_id=base_item_id,
        override_name=override_name,
        override_unit_label=override_unit_label,
        is_disabled=False,
    )
    session.add(ext)
    try:
        await session.flush()
    except IntegrityError as exc:
        await session.rollback()
        msg = str(exc.orig) if exc.orig is not None else ""
        if "ix_catalog_item_tenant_extension_tenant_id_base_item_id_unique" in msg:
            raise DuplicateOverrideError(
                tenant_id=tenant_id,
                base_item_id=base_item_id,
            ) from exc
        raise
    return ext


async def create_own_item(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    name: str,
    unit: str,
    default_unit_label: str,
    category_id: uuid.UUID,
    description: str | None = None,
) -> CatalogItemTenantExtension:
    """Legt ein eigenständiges Tenant-Item an (kein Override).

    ``base_item_id`` bleibt NULL — die mode_constraint stellt sicher,
    dass alle Pflichtfelder gesetzt sind.
    """
    ext = CatalogItemTenantExtension(
        tenant_id=tenant_id,
        base_item_id=None,
        name=name,
        unit=unit,
        default_unit_label=default_unit_label,
        category_id=category_id,
        description=description,
        is_disabled=False,
    )
    session.add(ext)
    await session.flush()
    return ext


async def find_extension_by_id(
    session: AsyncSession,
    extension_id: uuid.UUID,
) -> CatalogItemTenantExtension | None:
    return (
        await session.execute(
            select(CatalogItemTenantExtension).where(CatalogItemTenantExtension.id == extension_id),
        )
    ).scalar_one_or_none()


async def list_extensions_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[CatalogItemTenantExtension]:
    """Alle Extensions eines Tenants (Override + eigenständig gemischt)."""
    stmt = (
        select(CatalogItemTenantExtension)
        .where(CatalogItemTenantExtension.tenant_id == tenant_id)
        .order_by(CatalogItemTenantExtension.created_at.asc())
    )
    return list((await session.execute(stmt)).scalars().all())


async def update_override(
    session: AsyncSession,
    *,
    extension_id: uuid.UUID,
    override_name: str | None = None,
    override_unit_label: str | None = None,
    is_disabled: bool | None = None,
) -> CatalogItemTenantExtension | None:
    """Aktualisiert einen Override (nur Override-Felder erlaubt).

    Liefert ``None`` wenn die ID nicht existiert oder die Extension
    kein Override ist (``base_item_id IS NULL``).
    """
    ext = await find_extension_by_id(session, extension_id)
    if ext is None or ext.base_item_id is None:
        return None
    if override_name is not None:
        ext.override_name = override_name
    if override_unit_label is not None:
        ext.override_unit_label = override_unit_label
    if is_disabled is not None:
        ext.is_disabled = is_disabled
    await session.flush()
    return ext


async def update_own_item(
    session: AsyncSession,
    *,
    extension_id: uuid.UUID,
    name: str | None = None,
    unit: str | None = None,
    default_unit_label: str | None = None,
    category_id: uuid.UUID | None = None,
    description: str | None = None,
    is_disabled: bool | None = None,
) -> CatalogItemTenantExtension | None:
    """Aktualisiert ein eigenständiges Tenant-Item (Override-Felder bleiben NULL).

    Liefert ``None`` wenn die ID nicht existiert oder die Extension
    ein Override ist (``base_item_id IS NOT NULL``).
    """
    ext = await find_extension_by_id(session, extension_id)
    if ext is None or ext.base_item_id is not None:
        return None
    if name is not None:
        ext.name = name
    if unit is not None:
        ext.unit = unit
    if default_unit_label is not None:
        ext.default_unit_label = default_unit_label
    if category_id is not None:
        ext.category_id = category_id
    if description is not None:
        ext.description = description
    if is_disabled is not None:
        ext.is_disabled = is_disabled
    await session.flush()
    return ext


__all__ = [
    "CategoryNameTakenError",
    "DuplicateOverrideError",
    "create_base_item",
    "create_category",
    "create_override",
    "create_own_item",
    "find_base_item_by_id",
    "find_category_by_id",
    "find_extension_by_id",
    "list_base_items",
    "list_categories",
    "list_extensions_for_tenant",
    "update_base_item",
    "update_override",
    "update_own_item",
]
