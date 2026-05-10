"""Tests für ``backend/eb_digital/auth/repositories.find_by_username``.

Die Routing-Logik (PlatformAdmin → Dispatcher → Carer) wird gegen einen
``_StubSession`` getestet, der das Statement nach Ziel-Entity unterscheidet
und das passende ORM-Objekt zurückgibt. Das Statement-Building selbst
(``where``, ``order_by``, ``limit``) wird im Integration-Pfad über
``dev-smoke.sh`` gegen die echte Postgres-DB validiert.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

import pytest

from eb_digital.auth.models import Carer, Dispatcher, PlatformAdmin
from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
    find_by_username,
)


class _StubResult:
    def __init__(self, value: Any) -> None:
        self._value = value

    def scalar_one_or_none(self) -> Any:
        return self._value


class _StubSession:
    """Minimaler ``AsyncSession``-Ersatz für Routing-Tests.

    Liefert pro ORM-Klasse genau einen vor-konfigurierten Match (oder None).
    """

    def __init__(
        self,
        *,
        admin: PlatformAdmin | None = None,
        dispatcher: Dispatcher | None = None,
        carer: Carer | None = None,
    ) -> None:
        self._admin = admin
        self._dispatcher = dispatcher
        self._carer = carer

    async def execute(self, stmt: Any) -> _StubResult:
        entity = stmt.column_descriptions[0]["entity"]
        if entity is PlatformAdmin:
            return _StubResult(self._admin)
        if entity is Dispatcher:
            return _StubResult(self._dispatcher)
        if entity is Carer:
            return _StubResult(self._carer)
        return _StubResult(None)


def _make_admin(username: str = "alice") -> PlatformAdmin:
    return PlatformAdmin(
        id=uuid.uuid4(),
        username=username,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$xxx$yyy",
        created_at=datetime.now(UTC),
        created_via="bootstrap_cli",
    )


def _make_dispatcher(username: str = "alice", *, is_active: bool = True) -> Dispatcher:
    d = Dispatcher(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        username=username,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$xxx$yyy",
        is_active=is_active,
    )
    # `created_at`/`updated_at` werden beim DB-Flush gesetzt; im Stub stub'en wir.
    now = datetime.now(UTC)
    d.created_at = now
    d.updated_at = now
    return d


def _make_carer(username: str = "alice", *, is_active: bool = True) -> Carer:
    c = Carer(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        username=username,
        password_hash="$argon2id$v=19$m=65536,t=3,p=4$xxx$yyy",
        is_active=is_active,
    )
    now = datetime.now(UTC)
    c.created_at = now
    c.updated_at = now
    return c


@pytest.mark.asyncio
async def test_find_returns_none_when_no_table_matches() -> None:
    session = _StubSession()
    assert await find_by_username(session, "ghost") is None  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_finds_platform_admin_first() -> None:
    admin = _make_admin("alice")
    session = _StubSession(admin=admin, dispatcher=_make_dispatcher("alice"))
    subject = await find_by_username(session, "alice")  # type: ignore[arg-type]
    assert subject is not None
    assert subject.kind == KIND_PLATFORM_ADMIN
    assert subject.id == admin.id
    assert subject.tenant_id is None
    assert subject.is_active is True  # PlatformAdmin hat kein is_active-Feld


@pytest.mark.asyncio
async def test_finds_dispatcher_when_no_admin_matches() -> None:
    dispatcher = _make_dispatcher("alice")
    session = _StubSession(dispatcher=dispatcher)
    subject = await find_by_username(session, "alice")  # type: ignore[arg-type]
    assert subject is not None
    assert subject.kind == KIND_DISPATCHER
    assert subject.id == dispatcher.id
    assert subject.tenant_id == dispatcher.tenant_id
    assert subject.is_active is True


@pytest.mark.asyncio
async def test_finds_carer_when_no_admin_or_dispatcher_matches() -> None:
    carer = _make_carer("alice")
    session = _StubSession(carer=carer)
    subject = await find_by_username(session, "alice")  # type: ignore[arg-type]
    assert subject is not None
    assert subject.kind == KIND_CARER
    assert subject.id == carer.id
    assert subject.tenant_id == carer.tenant_id


@pytest.mark.asyncio
async def test_carer_inactive_flag_propagates_to_subject() -> None:
    carer = _make_carer("alice", is_active=False)
    session = _StubSession(carer=carer)
    subject = await find_by_username(session, "alice")  # type: ignore[arg-type]
    assert subject is not None
    assert subject.is_active is False


@pytest.mark.asyncio
async def test_dispatcher_inactive_flag_propagates_to_subject() -> None:
    dispatcher = _make_dispatcher("alice", is_active=False)
    session = _StubSession(dispatcher=dispatcher)
    subject = await find_by_username(session, "alice")  # type: ignore[arg-type]
    assert subject is not None
    assert subject.is_active is False
