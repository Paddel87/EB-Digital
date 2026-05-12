"""Tests für ``backend/eb_digital/tenants/repositories``.

Strategie: ``_StubSession`` analog zu ``test_auth_repositories``. Statement-
Logik wird im Compose-Smoke gegen die echte Postgres-DB validiert. Hier:
Idempotenz-Checks, IntegrityError-Mapping, Sentinel-Hash-Wahl,
``set_password_and_activate``-Replay-Schutz.
"""

from __future__ import annotations

import uuid
from collections.abc import Iterable
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import IntegrityError

from eb_digital.auth.models import Carer, Dispatcher
from eb_digital.auth.repositories import KIND_CARER, KIND_DISPATCHER
from eb_digital.tenants import repositories as tenants_repo
from eb_digital.tenants.models import (
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_APPLIED,
    TENANT_STATUS_DEACTIVATED,
    Tenant,
)


class _Scalars:
    def __init__(self, values: Iterable[Any]) -> None:
        self._values = list(values)

    def all(self) -> list[Any]:
        return list(self._values)


class _StubResult:
    def __init__(self, *, scalars: Iterable[Any] = (), single: Any = None) -> None:
        self._scalars = list(scalars)
        self._single = single

    def scalars(self) -> _Scalars:
        return _Scalars(self._scalars)

    def scalar_one_or_none(self) -> Any:
        return self._single

    def scalar_one(self) -> Any:
        return self._single


class _StubSession:
    """Konfigurierbares Stub für ``AsyncSession``-Funktionalität.

    ``add()`` zählt Aufrufe; ``flush()`` kann eine Exception werfen;
    ``execute()`` liefert das vor-konfigurierte ``_StubResult``;
    ``rollback()`` ist no-op.
    """

    def __init__(
        self,
        *,
        execute_result: _StubResult | None = None,
        flush_raises: Exception | None = None,
    ) -> None:
        self._execute_result = execute_result or _StubResult(single=None)
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

    async def execute(self, _stmt: Any) -> _StubResult:
        return self._execute_result


def _make_integrity_error(orig_message: str) -> IntegrityError:
    """Baut einen ``IntegrityError`` mit kontrollierter ``orig``-Repräsentation."""
    orig = MagicMock()
    orig.__str__ = lambda _self: orig_message
    return IntegrityError("statement", {}, orig)


def _make_tenant(
    *,
    status: str = TENANT_STATUS_APPLIED,
) -> Tenant:
    return Tenant(
        id=uuid.uuid4(),
        name="Test",
        slug="test",
        status=status,
        applied_at=datetime.now(UTC),
    )


# ─── create_tenant_application ───────────────────────────────────────────────


async def test_create_tenant_application_success() -> None:
    session = _StubSession()
    tenant = await tenants_repo.create_tenant_application(
        session,  # type: ignore[arg-type]
        name="DPolG Bremen",
        slug="dpolg-bremen",
    )
    assert tenant.name == "DPolG Bremen"
    assert tenant.slug == "dpolg-bremen"
    assert tenant.status == TENANT_STATUS_APPLIED
    assert session.added == [tenant]
    assert session.flushes == 1


async def test_create_tenant_application_slug_collision_raises() -> None:
    session = _StubSession(
        flush_raises=_make_integrity_error("uq_tenant_slug violation"),
    )
    with pytest.raises(tenants_repo.SlugAlreadyTakenError) as exc_info:
        await tenants_repo.create_tenant_application(
            session,  # type: ignore[arg-type]
            name="DPolG",
            slug="dpolg",
        )
    assert exc_info.value.slug == "dpolg"
    assert session.rollbacks == 1


async def test_create_tenant_application_unrelated_integrity_error_propagates() -> None:
    session = _StubSession(
        flush_raises=_make_integrity_error("some other constraint failed"),
    )
    with pytest.raises(IntegrityError):
        await tenants_repo.create_tenant_application(
            session,  # type: ignore[arg-type]
            name="X",
            slug="x",
        )


# ─── approve_tenant ──────────────────────────────────────────────────────────


async def test_approve_tenant_applied_to_active() -> None:
    tenant = _make_tenant(status=TENANT_STATUS_APPLIED)
    session = _StubSession(execute_result=_StubResult(single=tenant))
    result = await tenants_repo.approve_tenant(session, tenant.id)  # type: ignore[arg-type]
    assert result is tenant
    assert tenant.status == TENANT_STATUS_ACTIVE
    assert tenant.activated_at is not None


async def test_approve_tenant_idempotent_for_already_active() -> None:
    tenant = _make_tenant(status=TENANT_STATUS_ACTIVE)
    activated_before = tenant.activated_at
    session = _StubSession(execute_result=_StubResult(single=tenant))
    result = await tenants_repo.approve_tenant(session, tenant.id)  # type: ignore[arg-type]
    assert result is tenant
    assert tenant.status == TENANT_STATUS_ACTIVE
    # Idempotenz: ``activated_at`` wird nicht überschrieben.
    assert tenant.activated_at == activated_before


async def test_approve_tenant_returns_none_for_unknown() -> None:
    session = _StubSession(execute_result=_StubResult(single=None))
    result = await tenants_repo.approve_tenant(session, uuid.uuid4())  # type: ignore[arg-type]
    assert result is None


async def test_approve_tenant_does_not_reactivate_deactivated() -> None:
    tenant = _make_tenant(status=TENANT_STATUS_DEACTIVATED)
    session = _StubSession(execute_result=_StubResult(single=tenant))
    result = await tenants_repo.approve_tenant(session, tenant.id)  # type: ignore[arg-type]
    assert result is tenant
    # Status bleibt deaktiviert.
    assert tenant.status == TENANT_STATUS_DEACTIVATED


# ─── deactivate_tenant ───────────────────────────────────────────────────────


async def test_deactivate_tenant_active_to_deactivated() -> None:
    tenant = _make_tenant(status=TENANT_STATUS_ACTIVE)
    session = _StubSession(execute_result=_StubResult(single=tenant))
    result = await tenants_repo.deactivate_tenant(session, tenant.id)  # type: ignore[arg-type]
    assert result is tenant
    assert tenant.status == TENANT_STATUS_DEACTIVATED
    assert tenant.deactivated_at is not None


async def test_deactivate_tenant_idempotent() -> None:
    tenant = _make_tenant(status=TENANT_STATUS_DEACTIVATED)
    deactivated_before = tenant.deactivated_at
    session = _StubSession(execute_result=_StubResult(single=tenant))
    result = await tenants_repo.deactivate_tenant(session, tenant.id)  # type: ignore[arg-type]
    assert result is tenant
    assert tenant.deactivated_at == deactivated_before


# ─── invite_dispatcher / invite_carer ────────────────────────────────────────


async def test_invite_dispatcher_uses_pending_sentinel() -> None:
    session = _StubSession()
    tenant_id = uuid.uuid4()
    dispatcher = await tenants_repo.invite_dispatcher(
        session,  # type: ignore[arg-type]
        tenant_id=tenant_id,
        username="alice",
        email="alice@example.org",
    )
    assert dispatcher.tenant_id == tenant_id
    assert dispatcher.username == "alice"
    assert dispatcher.email == "alice@example.org"
    assert dispatcher.is_active is False
    assert dispatcher.password_hash == ""  # Sentinel


async def test_invite_carer_uses_pending_sentinel() -> None:
    session = _StubSession()
    carer = await tenants_repo.invite_carer(
        session,  # type: ignore[arg-type]
        tenant_id=uuid.uuid4(),
        username="bob",
        email=None,
    )
    assert carer.is_active is False
    assert carer.password_hash == ""


async def test_invite_dispatcher_username_collision_maps_to_domain_exception() -> None:
    session = _StubSession(
        flush_raises=_make_integrity_error("uq_dispatcher_tenant_id_username failed"),
    )
    tenant_id = uuid.uuid4()
    with pytest.raises(tenants_repo.UsernameTakenInTenantError) as exc_info:
        await tenants_repo.invite_dispatcher(
            session,  # type: ignore[arg-type]
            tenant_id=tenant_id,
            username="alice",
            email=None,
        )
    assert exc_info.value.tenant_id == tenant_id
    assert exc_info.value.username == "alice"
    assert exc_info.value.kind == KIND_DISPATCHER


async def test_invite_carer_username_collision_maps_to_domain_exception() -> None:
    session = _StubSession(
        flush_raises=_make_integrity_error("uq_carer_tenant_id_username collision"),
    )
    with pytest.raises(tenants_repo.UsernameTakenInTenantError) as exc_info:
        await tenants_repo.invite_carer(
            session,  # type: ignore[arg-type]
            tenant_id=uuid.uuid4(),
            username="bob",
            email=None,
        )
    assert exc_info.value.kind == KIND_CARER


async def test_invite_dispatcher_unrelated_integrity_error_propagates() -> None:
    session = _StubSession(
        flush_raises=_make_integrity_error("foreign_key_violation"),
    )
    with pytest.raises(IntegrityError):
        await tenants_repo.invite_dispatcher(
            session,  # type: ignore[arg-type]
            tenant_id=uuid.uuid4(),
            username="alice",
            email=None,
        )


# ─── set_password_and_activate ───────────────────────────────────────────────


async def test_set_password_and_activate_dispatcher_success() -> None:
    dispatcher = Dispatcher(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        username="alice",
        password_hash="",
        is_active=False,
    )
    session = _StubSession(execute_result=_StubResult(single=dispatcher))
    ok = await tenants_repo.set_password_and_activate(
        session,  # type: ignore[arg-type]
        kind=KIND_DISPATCHER,
        subject_id=dispatcher.id,
        password_hash="$argon2id$NEW_HASH",
    )
    assert ok is True
    assert dispatcher.is_active is True
    assert dispatcher.password_hash == "$argon2id$NEW_HASH"


async def test_set_password_and_activate_replay_returns_false() -> None:
    dispatcher = Dispatcher(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        username="alice",
        password_hash="$argon2id$EXISTING",
        is_active=True,  # already active
    )
    session = _StubSession(execute_result=_StubResult(single=dispatcher))
    ok = await tenants_repo.set_password_and_activate(
        session,  # type: ignore[arg-type]
        kind=KIND_DISPATCHER,
        subject_id=dispatcher.id,
        password_hash="$argon2id$NEW",
    )
    assert ok is False
    # Hash wird nicht überschrieben.
    assert dispatcher.password_hash == "$argon2id$EXISTING"


async def test_set_password_and_activate_unknown_returns_false() -> None:
    session = _StubSession(execute_result=_StubResult(single=None))
    ok = await tenants_repo.set_password_and_activate(
        session,  # type: ignore[arg-type]
        kind=KIND_DISPATCHER,
        subject_id=uuid.uuid4(),
        password_hash="$argon2id$X",
    )
    assert ok is False


async def test_set_password_and_activate_carer_path() -> None:
    carer = Carer(
        id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
        username="bob",
        password_hash="",
        is_active=False,
    )
    session = _StubSession(execute_result=_StubResult(single=carer))
    ok = await tenants_repo.set_password_and_activate(
        session,  # type: ignore[arg-type]
        kind=KIND_CARER,
        subject_id=carer.id,
        password_hash="$argon2id$NEW",
    )
    assert ok is True
    assert carer.is_active is True


async def test_set_password_and_activate_unknown_kind_returns_false() -> None:
    session = _StubSession()
    ok = await tenants_repo.set_password_and_activate(
        session,  # type: ignore[arg-type]
        kind="platform_admin",  # nicht unterstützt für Reset-Token-Flow
        subject_id=uuid.uuid4(),
        password_hash="x",
    )
    assert ok is False


# ─── is_dispatcher_of_tenant ─────────────────────────────────────────────────


async def test_is_dispatcher_of_tenant_true() -> None:
    session = _StubSession(execute_result=_StubResult(single=1))
    ok = await tenants_repo.is_dispatcher_of_tenant(
        session,  # type: ignore[arg-type]
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
    )
    assert ok is True


async def test_is_dispatcher_of_tenant_false() -> None:
    session = _StubSession(execute_result=_StubResult(single=0))
    ok = await tenants_repo.is_dispatcher_of_tenant(
        session,  # type: ignore[arg-type]
        dispatcher_id=uuid.uuid4(),
        tenant_id=uuid.uuid4(),
    )
    assert ok is False


# ─── list_tenants ────────────────────────────────────────────────────────────


async def test_list_tenants_returns_scalars() -> None:
    tenants = [_make_tenant(), _make_tenant()]
    session = _StubSession(execute_result=_StubResult(scalars=tenants))
    result = await tenants_repo.list_tenants(session)  # type: ignore[arg-type]
    assert result == tenants


async def test_list_tenants_with_status_filter() -> None:
    tenants = [_make_tenant(status=TENANT_STATUS_APPLIED)]
    session = _StubSession(execute_result=_StubResult(scalars=tenants))
    result = await tenants_repo.list_tenants(
        session,  # type: ignore[arg-type]
        status_filter=TENANT_STATUS_APPLIED,
    )
    assert result == tenants
