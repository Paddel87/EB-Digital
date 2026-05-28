"""Tests für ``backend/eb_digital/catalog/repositories``.

Strategie analog ``test_tenants_repositories``: ``_StubSession`` für Add/
Flush-Pfade, ``IntegrityError``-Mapping auf Domain-Exceptions. SELECT-
Logik wird im Compose-Smoke gegen die echte Postgres-DB validiert.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest
from sqlalchemy.exc import IntegrityError

from eb_digital.catalog import repositories as catalog_repo
from eb_digital.catalog.models import (
    CatalogCategory,
    CatalogItemBase,
    CatalogItemTenantExtension,
)


class _StubResult:
    def __init__(self, *, single: Any = None) -> None:
        self._single = single

    def scalar_one_or_none(self) -> Any:
        return self._single


class _StubSession:
    def __init__(self, *, flush_raises: Exception | None = None) -> None:
        self._flush_raises = flush_raises
        self.added: list[Any] = []
        self.rollbacks = 0
        self.flushes = 0

    def add(self, obj: Any) -> None:
        self.added.append(obj)

    async def flush(self) -> None:
        self.flushes += 1
        if self._flush_raises is not None:
            raise self._flush_raises

    async def rollback(self) -> None:
        self.rollbacks += 1


def _integrity_error(orig_msg: str) -> IntegrityError:
    """Bauen einer ``IntegrityError`` mit ``orig``-String-Match."""

    class _Orig:
        def __str__(self) -> str:
            return orig_msg

    err = IntegrityError("statement", {}, Exception(orig_msg))
    err.orig = _Orig()  # type: ignore[assignment]
    return err


# ─── Category-Repository ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_category_adds_and_flushes() -> None:
    session = _StubSession()
    result = await catalog_repo.create_category(session, name="Getränke")  # type: ignore[arg-type]
    assert len(session.added) == 1
    assert isinstance(session.added[0], CatalogCategory)
    assert session.added[0].name == "Getränke"
    assert session.flushes == 1
    assert result is session.added[0]


@pytest.mark.asyncio
async def test_create_category_duplicate_name_raises_taken_error() -> None:
    session = _StubSession(
        flush_raises=_integrity_error("uq_catalog_category_name"),
    )
    with pytest.raises(catalog_repo.CategoryNameTakenError) as exc_info:
        await catalog_repo.create_category(session, name="Getränke")  # type: ignore[arg-type]
    assert exc_info.value.name == "Getränke"
    assert session.rollbacks == 1


@pytest.mark.asyncio
async def test_create_category_other_integrity_error_propagates() -> None:
    session = _StubSession(flush_raises=_integrity_error("some other constraint"))
    with pytest.raises(IntegrityError):
        await catalog_repo.create_category(session, name="Snacks")  # type: ignore[arg-type]
    assert session.rollbacks == 1


# ─── BaseItem-Repository ─────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_base_item_default_active_true() -> None:
    session = _StubSession()
    cat_id = uuid.uuid4()
    result = await catalog_repo.create_base_item(
        session,  # type: ignore[arg-type]
        name="Wasser",
        unit="liter",
        default_unit_label="Liter",
        category_id=cat_id,
    )
    assert isinstance(result, CatalogItemBase)
    assert result.is_active is True
    assert result.category_id == cat_id


# ─── TenantExtension-Repository ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_create_override_default_is_disabled_false() -> None:
    session = _StubSession()
    tenant_id = uuid.uuid4()
    base_id = uuid.uuid4()
    result = await catalog_repo.create_override(
        session,  # type: ignore[arg-type]
        tenant_id=tenant_id,
        base_item_id=base_id,
        override_name="Wasser still",
    )
    assert isinstance(result, CatalogItemTenantExtension)
    assert result.is_disabled is False
    assert result.tenant_id == tenant_id
    assert result.base_item_id == base_id
    assert result.override_name == "Wasser still"


@pytest.mark.asyncio
async def test_create_override_duplicate_raises_duplicate_override() -> None:
    session = _StubSession(
        flush_raises=_integrity_error(
            "ix_catalog_item_tenant_extension_tenant_id_base_item_id_unique"
        ),
    )
    tenant_id = uuid.uuid4()
    base_id = uuid.uuid4()
    with pytest.raises(catalog_repo.DuplicateOverrideError) as exc_info:
        await catalog_repo.create_override(
            session,  # type: ignore[arg-type]
            tenant_id=tenant_id,
            base_item_id=base_id,
        )
    assert exc_info.value.tenant_id == tenant_id
    assert exc_info.value.base_item_id == base_id
    assert session.rollbacks == 1


@pytest.mark.asyncio
async def test_create_own_item_sets_base_id_null() -> None:
    session = _StubSession()
    tenant_id = uuid.uuid4()
    cat_id = uuid.uuid4()
    result = await catalog_repo.create_own_item(
        session,  # type: ignore[arg-type]
        tenant_id=tenant_id,
        name="Lokales Spezial",
        unit="piece",
        default_unit_label="Stück",
        category_id=cat_id,
    )
    assert isinstance(result, CatalogItemTenantExtension)
    assert result.base_item_id is None
    assert result.name == "Lokales Spezial"
    assert result.unit == "piece"
    assert result.category_id == cat_id
    assert result.is_disabled is False


@pytest.mark.asyncio
async def test_create_own_item_other_integrity_error_propagates() -> None:
    session = _StubSession(flush_raises=_integrity_error("fk_violation"))
    with pytest.raises(IntegrityError):
        await catalog_repo.create_own_item(
            session,  # type: ignore[arg-type]
            tenant_id=uuid.uuid4(),
            name="x",
            unit="u",
            default_unit_label="U",
            category_id=uuid.uuid4(),
        )
    # create_own_item ruft kein rollback — IntegrityError propagiert direkt.
    assert session.rollbacks == 0


# ─── Domain-Exception-Repr ───────────────────────────────────────────────────


def test_category_name_taken_error_carries_name() -> None:
    exc = catalog_repo.CategoryNameTakenError("Getränke")
    assert exc.name == "Getränke"
    assert "Getränke" in str(exc)


def test_duplicate_override_error_carries_ids() -> None:
    tenant_id = uuid.uuid4()
    base_id = uuid.uuid4()
    exc = catalog_repo.DuplicateOverrideError(tenant_id=tenant_id, base_item_id=base_id)
    assert exc.tenant_id == tenant_id
    assert exc.base_item_id == base_id
    assert str(base_id) in str(exc)
    assert str(tenant_id) in str(exc)
