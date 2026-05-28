"""Tests für ``backend/eb_digital/catalog/use_cases``.

Strategie: Repository-Funktionen via ``monkeypatch`` ersetzen, damit die
Validierungs-/Routing-Logik der Use-Cases isoliert geprüft werden kann.
Echte SQL-Pfade laufen im Compose-Smoke.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from eb_digital.catalog import use_cases as catalog_use_cases
from eb_digital.catalog.models import (
    CatalogCategory,
    CatalogItemBase,
    CatalogItemTenantExtension,
)
from eb_digital.tenants.models import (
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_DEACTIVATED,
    Tenant,
)
from eb_digital.tenants.use_cases import TenantNotActiveError, TenantNotFoundError


class _FakeSession:
    """Platzhalter — Use-Cases sehen Repository-Calls über monkeypatch."""


def _make_base_item(*, is_active: bool = True) -> CatalogItemBase:
    item = CatalogItemBase(
        name="Wasser",
        unit="liter",
        default_unit_label="Liter",
        category_id=uuid.uuid4(),
        is_active=is_active,
    )
    item.id = uuid.uuid4()
    return item


def _make_tenant(*, status: str = TENANT_STATUS_ACTIVE) -> Tenant:
    tenant = Tenant(name="DPolG Bremen", slug="dpolg-bremen", status=status)
    tenant.id = uuid.uuid4()
    return tenant


def _make_category() -> CatalogCategory:
    cat = CatalogCategory(name="Getränke")
    cat.id = uuid.uuid4()
    return cat


# ─── Base Items ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_base_item_unknown_category_raises_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _find(_session: Any, _cat_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_category_by_id", _find)
    with pytest.raises(catalog_use_cases.CategoryNotFoundError):
        await catalog_use_cases.create_base_item(
            _FakeSession(),  # type: ignore[arg-type]
            name="x",
            unit="u",
            default_unit_label="U",
            category_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_update_base_item_unknown_category_raises_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _find_cat(_session: Any, _cat_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_category_by_id", _find_cat)
    with pytest.raises(catalog_use_cases.CategoryNotFoundError):
        await catalog_use_cases.update_base_item(
            _FakeSession(),  # type: ignore[arg-type]
            base_item_id=uuid.uuid4(),
            category_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_update_base_item_unknown_id_raises_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _update(_session: Any, **_kw: Any) -> None:
        return None

    monkeypatch.setattr(catalog_use_cases.catalog_repo, "update_base_item", _update)
    with pytest.raises(catalog_use_cases.BaseItemNotFoundError):
        await catalog_use_cases.update_base_item(
            _FakeSession(),  # type: ignore[arg-type]
            base_item_id=uuid.uuid4(),
            name="changed",
        )


# ─── Tenant Override ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_override_inactive_tenant_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    deactivated = _make_tenant(status=TENANT_STATUS_DEACTIVATED)

    async def _find_tenant(_session: Any, _tenant_id: uuid.UUID) -> Tenant:
        return deactivated

    monkeypatch.setattr(catalog_use_cases, "find_tenant_by_id", _find_tenant)
    with pytest.raises(TenantNotActiveError):
        await catalog_use_cases.create_tenant_override(
            _FakeSession(),  # type: ignore[arg-type]
            tenant_id=deactivated.id,
            base_item_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_create_override_missing_tenant_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _find_tenant(_session: Any, _tenant_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(catalog_use_cases, "find_tenant_by_id", _find_tenant)
    with pytest.raises(TenantNotFoundError):
        await catalog_use_cases.create_tenant_override(
            _FakeSession(),  # type: ignore[arg-type]
            tenant_id=uuid.uuid4(),
            base_item_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_create_override_inactive_base_item_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant()
    inactive_base = _make_base_item(is_active=False)

    async def _find_tenant(_session: Any, _tenant_id: uuid.UUID) -> Tenant:
        return tenant

    async def _find_base(_session: Any, _base_id: uuid.UUID) -> CatalogItemBase:
        return inactive_base

    monkeypatch.setattr(catalog_use_cases, "find_tenant_by_id", _find_tenant)
    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_base_item_by_id", _find_base)
    with pytest.raises(catalog_use_cases.BaseItemNotActiveError):
        await catalog_use_cases.create_tenant_override(
            _FakeSession(),  # type: ignore[arg-type]
            tenant_id=tenant.id,
            base_item_id=inactive_base.id,
        )


@pytest.mark.asyncio
async def test_create_override_missing_base_item_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant()

    async def _find_tenant(_session: Any, _tenant_id: uuid.UUID) -> Tenant:
        return tenant

    async def _find_base(_session: Any, _base_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(catalog_use_cases, "find_tenant_by_id", _find_tenant)
    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_base_item_by_id", _find_base)
    with pytest.raises(catalog_use_cases.BaseItemNotFoundError):
        await catalog_use_cases.create_tenant_override(
            _FakeSession(),  # type: ignore[arg-type]
            tenant_id=tenant.id,
            base_item_id=uuid.uuid4(),
        )


# ─── Tenant Own Item ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_own_item_inactive_tenant_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    deactivated = _make_tenant(status=TENANT_STATUS_DEACTIVATED)

    async def _find_tenant(_session: Any, _tenant_id: uuid.UUID) -> Tenant:
        return deactivated

    monkeypatch.setattr(catalog_use_cases, "find_tenant_by_id", _find_tenant)
    with pytest.raises(TenantNotActiveError):
        await catalog_use_cases.create_tenant_own_item(
            _FakeSession(),  # type: ignore[arg-type]
            tenant_id=deactivated.id,
            name="x",
            unit="u",
            default_unit_label="U",
            category_id=uuid.uuid4(),
        )


@pytest.mark.asyncio
async def test_create_own_item_unknown_category_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant()

    async def _find_tenant(_session: Any, _tenant_id: uuid.UUID) -> Tenant:
        return tenant

    async def _find_cat(_session: Any, _cat_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(catalog_use_cases, "find_tenant_by_id", _find_tenant)
    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_category_by_id", _find_cat)
    with pytest.raises(catalog_use_cases.CategoryNotFoundError):
        await catalog_use_cases.create_tenant_own_item(
            _FakeSession(),  # type: ignore[arg-type]
            tenant_id=tenant.id,
            name="x",
            unit="u",
            default_unit_label="U",
            category_id=uuid.uuid4(),
        )


# ─── Update Tenant Extension ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_update_extension_unknown_id_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _find(_session: Any, _ext_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_extension_by_id", _find)
    with pytest.raises(catalog_use_cases.ExtensionNotFoundError):
        await catalog_use_cases.update_tenant_extension(
            _FakeSession(),  # type: ignore[arg-type]
            extension_id=uuid.uuid4(),
            override_name="x",
        )


@pytest.mark.asyncio
async def test_update_extension_own_mode_rejects_override_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Eigenständige Extension (base_item_id IS NULL) lehnt override_* ab."""
    own_ext = CatalogItemTenantExtension(
        tenant_id=uuid.uuid4(),
        base_item_id=None,
        name="Lokales",
        unit="piece",
        default_unit_label="Stück",
        category_id=uuid.uuid4(),
        is_disabled=False,
    )
    own_ext.id = uuid.uuid4()

    async def _find(_session: Any, _ext_id: uuid.UUID) -> CatalogItemTenantExtension:
        return own_ext

    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_extension_by_id", _find)
    with pytest.raises(catalog_use_cases.ExtensionModeError) as exc_info:
        await catalog_use_cases.update_tenant_extension(
            _FakeSession(),  # type: ignore[arg-type]
            extension_id=own_ext.id,
            override_name="X",
        )
    assert exc_info.value.expected_mode == "override"


@pytest.mark.asyncio
async def test_update_extension_override_mode_rejects_own_fields(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Override-Extension (base_item_id IS NOT NULL) lehnt name/unit/etc. ab."""
    override_ext = CatalogItemTenantExtension(
        tenant_id=uuid.uuid4(),
        base_item_id=uuid.uuid4(),
        override_name="X",
        is_disabled=False,
    )
    override_ext.id = uuid.uuid4()

    async def _find(_session: Any, _ext_id: uuid.UUID) -> CatalogItemTenantExtension:
        return override_ext

    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_extension_by_id", _find)
    with pytest.raises(catalog_use_cases.ExtensionModeError) as exc_info:
        await catalog_use_cases.update_tenant_extension(
            _FakeSession(),  # type: ignore[arg-type]
            extension_id=override_ext.id,
            name="Anderer Name",
        )
    assert exc_info.value.expected_mode == "own"


@pytest.mark.asyncio
async def test_update_extension_own_mode_unknown_category_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    own_ext = CatalogItemTenantExtension(
        tenant_id=uuid.uuid4(),
        base_item_id=None,
        name="x",
        unit="u",
        default_unit_label="U",
        category_id=uuid.uuid4(),
        is_disabled=False,
    )
    own_ext.id = uuid.uuid4()

    async def _find_ext(_session: Any, _ext_id: uuid.UUID) -> CatalogItemTenantExtension:
        return own_ext

    async def _find_cat(_session: Any, _cat_id: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_extension_by_id", _find_ext)
    monkeypatch.setattr(catalog_use_cases.catalog_repo, "find_category_by_id", _find_cat)
    with pytest.raises(catalog_use_cases.CategoryNotFoundError):
        await catalog_use_cases.update_tenant_extension(
            _FakeSession(),  # type: ignore[arg-type]
            extension_id=own_ext.id,
            category_id=uuid.uuid4(),
        )


# ─── Defense-in-depth Helper ─────────────────────────────────────────────────


def test_expect_own_fields_raises_on_inconsistency() -> None:
    """Wenn die DB einen Bug hat und name/unit/etc. NULL sind trotz base_item_id IS NULL.

    Defense-in-depth-Pfad: ``_expect_own_fields`` muss RuntimeError werfen.
    """
    bad_ext = CatalogItemTenantExtension(
        tenant_id=uuid.uuid4(),
        base_item_id=None,
        name=None,  # mode_constraint sollte das verhindern; defensiver Check.
        unit=None,
        default_unit_label=None,
        category_id=None,
        is_disabled=False,
    )
    bad_ext.id = uuid.uuid4()
    with pytest.raises(RuntimeError):
        catalog_use_cases._expect_own_fields(bad_ext)  # type: ignore[reportPrivateUsage]


def test_expect_own_fields_returns_tuple_when_complete() -> None:
    cat_id = uuid.uuid4()
    ext = CatalogItemTenantExtension(
        tenant_id=uuid.uuid4(),
        base_item_id=None,
        name="Sandwich",
        unit="piece",
        default_unit_label="Stück",
        category_id=cat_id,
        is_disabled=False,
    )
    ext.id = uuid.uuid4()
    name, unit, label, returned_cat_id = catalog_use_cases._expect_own_fields(ext)  # type: ignore[reportPrivateUsage]
    assert name == "Sandwich"
    assert unit == "piece"
    assert label == "Stück"
    assert returned_cat_id == cat_id


# ─── Domain-Exception-Identitätstests ────────────────────────────────────────


def test_category_not_found_error_carries_id() -> None:
    cat_id = uuid.uuid4()
    exc = catalog_use_cases.CategoryNotFoundError(cat_id)
    assert exc.category_id == cat_id
    assert str(cat_id) in str(exc)


def test_base_item_not_active_error_carries_id() -> None:
    base_id = uuid.uuid4()
    exc = catalog_use_cases.BaseItemNotActiveError(base_id)
    assert exc.base_item_id == base_id
    assert str(base_id) in str(exc)


def test_extension_mode_error_carries_mode() -> None:
    ext_id = uuid.uuid4()
    exc = catalog_use_cases.ExtensionModeError(extension_id=ext_id, expected_mode="override")
    assert exc.expected_mode == "override"
    assert exc.extension_id == ext_id
