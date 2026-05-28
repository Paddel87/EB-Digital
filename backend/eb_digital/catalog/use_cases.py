"""Use-Case-Schicht für ``backend/catalog`` (Phase 4 Schritt 4.1).

Dünne Orchestrierungs-Schicht über den Repositories. Validierung von
Vorbedingungen (Tenant aktiv, Kategorie existiert, Base-Item aktiv),
Aufruf der Repository-Funktionen und Mapping auf domain-spezifische
Exceptions. Berechtigungs-Checks (Plattform-Admin / Disponent /
Carer / Anon) liegen in der API-Schicht (analog ``tenants.api``).

Der **Resolver** ``resolve_catalog_for_operation`` ist das Herzstück:
er produziert den effektiven Katalog einer Operation gemäß S10/Regel-014
mit Drei-Query-Pattern (Owner-Tenant-Lookup, Base-Items + Overrides
gemischt, eigenständige Tenant-Items). Drei Queries je mit JOIN auf
Category, keine N+1-Schleifen.
"""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.catalog import repositories as catalog_repo
from eb_digital.catalog.models import (
    CatalogCategory,
    CatalogItemBase,
    CatalogItemTenantExtension,
)
from eb_digital.catalog.schemas import ResolvedCatalogItem
from eb_digital.tenants.models import TENANT_STATUS_ACTIVE
from eb_digital.tenants.participation import owners_of_operation
from eb_digital.tenants.repositories import find_tenant_by_id
from eb_digital.tenants.use_cases import TenantNotActiveError, TenantNotFoundError

# ─── Domain-Exceptions ───────────────────────────────────────────────────────


class CategoryNotFoundError(Exception):
    """Kategorie mit angegebener ID existiert nicht."""

    def __init__(self, category_id: uuid.UUID) -> None:
        super().__init__(f"Category not found: {category_id}")
        self.category_id = category_id


class BaseItemNotFoundError(Exception):
    """Base-Item mit angegebener ID existiert nicht."""

    def __init__(self, base_item_id: uuid.UUID) -> None:
        super().__init__(f"Base item not found: {base_item_id}")
        self.base_item_id = base_item_id


class BaseItemNotActiveError(Exception):
    """Base-Item existiert, ist aber per Soft-Delete deaktiviert.

    Override auf inaktive Base-Items ist nicht erlaubt (würde im
    effektiven Katalog ohnehin nicht sichtbar werden).
    """

    def __init__(self, base_item_id: uuid.UUID) -> None:
        super().__init__(f"Base item is not active: {base_item_id}")
        self.base_item_id = base_item_id


class ExtensionNotFoundError(Exception):
    """Tenant-Extension mit angegebener ID existiert nicht."""

    def __init__(self, extension_id: uuid.UUID) -> None:
        super().__init__(f"Tenant extension not found: {extension_id}")
        self.extension_id = extension_id


class ExtensionModeError(Exception):
    """Update-Versuch im falschen Modus (Override-Felder vs. Eigenständig-Felder)."""

    def __init__(self, *, extension_id: uuid.UUID, expected_mode: str) -> None:
        super().__init__(
            f"Extension {extension_id} is not in {expected_mode!r} mode; "
            "cannot apply update for that mode.",
        )
        self.extension_id = extension_id
        self.expected_mode = expected_mode


# ─── Categories ──────────────────────────────────────────────────────────────


async def create_category(session: AsyncSession, *, name: str) -> CatalogCategory:
    """Legt eine Kategorie an. ``CategoryNameTakenError`` bei Kollision."""
    return await catalog_repo.create_category(session, name=name)


# ─── Base Items ──────────────────────────────────────────────────────────────


async def create_base_item(
    session: AsyncSession,
    *,
    name: str,
    unit: str,
    default_unit_label: str,
    category_id: uuid.UUID,
    description: str | None = None,
) -> CatalogItemBase:
    """Legt ein Base-Item an. Vorbedingung: Kategorie existiert."""
    category = await catalog_repo.find_category_by_id(session, category_id)
    if category is None:
        raise CategoryNotFoundError(category_id)
    return await catalog_repo.create_base_item(
        session,
        name=name,
        unit=unit,
        default_unit_label=default_unit_label,
        category_id=category_id,
        description=description,
    )


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
) -> CatalogItemBase:
    """Aktualisiert ein Base-Item per PATCH-Semantik.

    Bei ``category_id != None`` wird Existenz vorab geprüft, weil sonst
    die DB nur einen unspezifischen FK-Fehler liefert. ``None``-Felder
    werden nicht angefasst (PATCH).
    """
    if category_id is not None:
        category = await catalog_repo.find_category_by_id(session, category_id)
        if category is None:
            raise CategoryNotFoundError(category_id)
    item = await catalog_repo.update_base_item(
        session,
        base_item_id=base_item_id,
        name=name,
        unit=unit,
        default_unit_label=default_unit_label,
        category_id=category_id,
        description=description,
        is_active=is_active,
    )
    if item is None:
        raise BaseItemNotFoundError(base_item_id)
    return item


# ─── Tenant Extensions ───────────────────────────────────────────────────────


async def _require_tenant_active(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    tenant = await find_tenant_by_id(session, tenant_id)
    if tenant is None:
        raise TenantNotFoundError(tenant_id)
    if tenant.status != TENANT_STATUS_ACTIVE:
        raise TenantNotActiveError(tenant_id=tenant_id, status=tenant.status)


async def create_tenant_override(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    base_item_id: uuid.UUID,
    override_name: str | None = None,
    override_unit_label: str | None = None,
) -> CatalogItemTenantExtension:
    """Legt einen Override eines Base-Items für einen Tenant an.

    Vorbedingungen: Tenant aktiv, Base-Item existiert und ``is_active=True``.
    ``DuplicateOverrideError`` bei Doppelung wird vom Repository geworfen.
    """
    await _require_tenant_active(session, tenant_id)
    base_item = await catalog_repo.find_base_item_by_id(session, base_item_id)
    if base_item is None:
        raise BaseItemNotFoundError(base_item_id)
    if not base_item.is_active:
        raise BaseItemNotActiveError(base_item_id)
    return await catalog_repo.create_override(
        session,
        tenant_id=tenant_id,
        base_item_id=base_item_id,
        override_name=override_name,
        override_unit_label=override_unit_label,
    )


async def create_tenant_own_item(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    name: str,
    unit: str,
    default_unit_label: str,
    category_id: uuid.UUID,
    description: str | None = None,
) -> CatalogItemTenantExtension:
    """Legt ein eigenständiges Tenant-Item an. Vorbedingungen: Tenant aktiv,
    Kategorie existiert."""
    await _require_tenant_active(session, tenant_id)
    category = await catalog_repo.find_category_by_id(session, category_id)
    if category is None:
        raise CategoryNotFoundError(category_id)
    return await catalog_repo.create_own_item(
        session,
        tenant_id=tenant_id,
        name=name,
        unit=unit,
        default_unit_label=default_unit_label,
        category_id=category_id,
        description=description,
    )


async def update_tenant_extension(
    session: AsyncSession,
    *,
    extension_id: uuid.UUID,
    override_name: str | None = None,
    override_unit_label: str | None = None,
    name: str | None = None,
    unit: str | None = None,
    default_unit_label: str | None = None,
    category_id: uuid.UUID | None = None,
    description: str | None = None,
    is_disabled: bool | None = None,
) -> CatalogItemTenantExtension:
    """PATCH-Update einer Tenant-Extension; routet nach Modus.

    Im Override-Modus dürfen nur ``override_name``, ``override_unit_label``,
    ``is_disabled`` gesetzt werden — alle anderen Felder werden ignoriert
    (Pydantic-Validierung im API-Layer würde sie ebenfalls fangen, hier
    Doppel-Sicherung).

    Im Eigenständig-Modus dürfen nur ``name``, ``unit``, ``default_unit_label``,
    ``category_id``, ``description``, ``is_disabled`` gesetzt werden.

    ``ExtensionModeError`` wird geworfen, wenn versucht wird, Override-Felder
    auf einer eigenständigen Extension zu setzen oder umgekehrt.
    """
    ext = await catalog_repo.find_extension_by_id(session, extension_id)
    if ext is None:
        raise ExtensionNotFoundError(extension_id)

    if ext.base_item_id is not None:
        # Override-Modus
        if any(v is not None for v in (name, unit, default_unit_label, category_id)):
            raise ExtensionModeError(extension_id=extension_id, expected_mode="own")
        updated = await catalog_repo.update_override(
            session,
            extension_id=extension_id,
            override_name=override_name,
            override_unit_label=override_unit_label,
            is_disabled=is_disabled,
        )
    else:
        # Eigenständig-Modus
        if any(v is not None for v in (override_name, override_unit_label)):
            raise ExtensionModeError(extension_id=extension_id, expected_mode="override")
        if category_id is not None:
            category = await catalog_repo.find_category_by_id(session, category_id)
            if category is None:
                raise CategoryNotFoundError(category_id)
        updated = await catalog_repo.update_own_item(
            session,
            extension_id=extension_id,
            name=name,
            unit=unit,
            default_unit_label=default_unit_label,
            category_id=category_id,
            description=description,
            is_disabled=is_disabled,
        )

    if updated is None:
        raise ExtensionNotFoundError(extension_id)
    return updated


# ─── Helper ──────────────────────────────────────────────────────────────────


def _expect_own_fields(
    ext: CatalogItemTenantExtension,
) -> tuple[str, str, str, uuid.UUID]:
    """Erzwingt die Pflicht-Felder eines Eigenständig-Modus-Eintrags.

    Garantiert durch DB-CHECK ``mode_constraint``: bei ``base_item_id IS
    NULL`` sind ``name``, ``unit``, ``default_unit_label`` und
    ``category_id`` NOT NULL. Diese Hilfsfunktion ist defensiver
    Runtime-Check (deckt etwaige Constraint-Verletzungen durch Daten-Bug
    oder Migration-Drift auf) und gleichzeitig mypy-Narrowing.
    """
    if (
        ext.name is None
        or ext.unit is None
        or ext.default_unit_label is None
        or ext.category_id is None
    ):
        msg = (
            f"Data integrity violation: own-mode tenant extension {ext.id} "
            "has NULL pflicht field(s) despite mode_constraint."
        )
        raise RuntimeError(msg)
    return ext.name, ext.unit, ext.default_unit_label, ext.category_id


# ─── Resolver ────────────────────────────────────────────────────────────────


async def resolve_catalog_for_tenant(
    session: AsyncSession,
    tenant_id: uuid.UUID,
) -> list[ResolvedCatalogItem]:
    """Effektiver Katalog für einen Tenant (Carer-Read-Pfad).

    Drei-Query-Pattern:

      1. Base-Items mit ``is_active=TRUE`` + Category-Name (JOIN).
      2. Overrides für ``tenant_id`` (only Override-Modus).
      3. Eigenständige Tenant-Items für ``tenant_id`` mit ``is_disabled=FALSE``
         + Category-Name (JOIN).

    Pro Base-Item wird der ggf. existierende Override eingekomponiert
    (``override_name`` / ``override_unit_label`` ersetzen das Base-Feld);
    ``is_disabled=TRUE`` schließt das Base-Item für den Tenant aus.
    Sortierung am Ende nach Name (alphabetisch, case-insensitive).
    """
    # Query 1: aktive Base-Items mit Category-Name.
    base_stmt = (
        select(CatalogItemBase, CatalogCategory.name)
        .join(CatalogCategory, CatalogCategory.id == CatalogItemBase.category_id)
        .where(CatalogItemBase.is_active.is_(True))
    )
    base_rows = list((await session.execute(base_stmt)).all())

    # Query 2: Overrides für diesen Tenant (only Override-Modus).
    override_stmt = select(CatalogItemTenantExtension).where(
        CatalogItemTenantExtension.tenant_id == tenant_id,
        CatalogItemTenantExtension.base_item_id.is_not(None),
    )
    overrides = list((await session.execute(override_stmt)).scalars().all())
    overrides_by_base_id: dict[uuid.UUID, CatalogItemTenantExtension] = {
        # Cast ist sicher: WHERE-Clause filtert auf base_item_id IS NOT NULL.
        ov.base_item_id: ov  # type: ignore[misc]
        for ov in overrides
    }

    # Query 3: eigenständige Tenant-Items mit Category-Name.
    own_stmt = (
        select(CatalogItemTenantExtension, CatalogCategory.name)
        .join(CatalogCategory, CatalogCategory.id == CatalogItemTenantExtension.category_id)
        .where(
            CatalogItemTenantExtension.tenant_id == tenant_id,
            CatalogItemTenantExtension.base_item_id.is_(None),
            CatalogItemTenantExtension.is_disabled.is_(False),
        )
    )
    own_rows = list((await session.execute(own_stmt)).all())

    result: list[ResolvedCatalogItem] = []

    # Base-Items zusammenstellen, Overrides anwenden.
    for base_item, base_category_name in base_rows:
        override = overrides_by_base_id.get(base_item.id)
        if override is not None and override.is_disabled:
            # Tenant hat das Base-Item explizit für sich deaktiviert.
            continue
        effective_name = (
            override.override_name
            if override is not None and override.override_name is not None
            else base_item.name
        )
        effective_unit_label = (
            override.override_unit_label
            if override is not None and override.override_unit_label is not None
            else base_item.default_unit_label
        )
        result.append(
            ResolvedCatalogItem(
                id=str(base_item.id),
                base_item_id=str(base_item.id),
                source="base",
                name=effective_name,
                unit=base_item.unit,
                default_unit_label=effective_unit_label,
                description=base_item.description,
                category_id=str(base_item.category_id),
                category_name=base_category_name,
            ),
        )

    # Eigenständige Tenant-Items. Die mode_constraint garantiert, dass
    # name/unit/default_unit_label/category_id für base_item_id IS NULL
    # gesetzt sind; ``_expect_own_fields`` ist defensiver Runtime-Check
    # plus mypy-Narrowing.
    for own_item, own_category_name in own_rows:
        own_name, own_unit, own_label, own_category_id = _expect_own_fields(own_item)
        result.append(
            ResolvedCatalogItem(
                id=str(own_item.id),
                base_item_id=None,
                source="tenant_own",
                name=own_name,
                unit=own_unit,
                default_unit_label=own_label,
                description=own_item.description,
                category_id=str(own_category_id),
                category_name=own_category_name,
            ),
        )

    result.sort(key=lambda r: r.name.casefold())
    return result


async def resolve_catalog_for_operation(
    session: AsyncSession,
    operation_id: uuid.UUID,
) -> list[ResolvedCatalogItem]:
    """Effektiver Katalog einer Operation (Anon-Read-Pfad).

    Phase 1: genau ein Owner-Tenant pro Operation (Invariante I1). Wenn
    keine Owner gefunden werden, liefert die Funktion eine leere Liste —
    Aufrufer entscheidet, ob das ein 404 (Operation existiert nicht) oder
    ein leerer Catalog ist.

    Phase X (Verbund-Modus, ADR-009): bei mehreren Owner-Tenants würden
    die Tenant-spezifischen Overrides und eigenständigen Items
    kombiniert. Phase 1 ist verhaltensgleich zu „Catalog des einzigen
    Owners".
    """
    owner_tenant_ids = await owners_of_operation(session, operation_id)
    if not owner_tenant_ids:
        return []
    # Phase 1: ein Owner. Direkter Aufruf der Tenant-Variante.
    return await resolve_catalog_for_tenant(session, owner_tenant_ids[0])


__all__ = [
    "BaseItemNotActiveError",
    "BaseItemNotFoundError",
    "CategoryNotFoundError",
    "ExtensionModeError",
    "ExtensionNotFoundError",
    "create_base_item",
    "create_category",
    "create_tenant_override",
    "create_tenant_own_item",
    "resolve_catalog_for_operation",
    "resolve_catalog_for_tenant",
    "update_base_item",
    "update_tenant_extension",
]
