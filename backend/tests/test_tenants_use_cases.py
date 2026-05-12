"""Tests für ``backend/eb_digital/tenants/use_cases``.

Strategie: Repository-Funktionen werden über ``monkeypatch`` ersetzt; die
Use-Case-Schicht selbst (Validierung, Status-Checks, Token-Generierung,
Mapping auf Domain-Exceptions) wird damit isoliert getestet. Echtes
Repository-Verhalten ist im Compose-Smoke abgedeckt.
"""

from __future__ import annotations

import uuid
from typing import Any

import pytest

from eb_digital.auth.models import Carer, Dispatcher
from eb_digital.auth.repositories import KIND_DISPATCHER
from eb_digital.tenants import use_cases
from eb_digital.tenants.models import (
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_APPLIED,
    TENANT_STATUS_DEACTIVATED,
    Tenant,
)
from eb_digital.tenants.slug import SlugValidationError
from eb_digital.tenants.username import UsernameValidationError

SECRET = "test-secret-not-for-production"


def _make_tenant(
    *,
    status: str = TENANT_STATUS_ACTIVE,
    name: str = "DPolG Bremen",
    slug: str = "dpolg-bremen",
) -> Tenant:
    return Tenant(
        id=uuid.uuid4(),
        name=name,
        slug=slug,
        status=status,
    )


# ─── apply_for_tenant ────────────────────────────────────────────────────────


async def test_apply_for_tenant_creates_application(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, Any] = {}

    async def _fake_create(
        _session: Any,
        *,
        name: str,
        slug: str,
    ) -> Tenant:
        captured["name"] = name
        captured["slug"] = slug
        return _make_tenant(name=name, slug=slug, status="applied")

    monkeypatch.setattr(use_cases.tenants_repo, "create_tenant_application", _fake_create)
    result = await use_cases.apply_for_tenant(None, name="DPolG Bremen", slug="dpolg-bremen")  # type: ignore[arg-type]
    assert result.tenant.slug == "dpolg-bremen"
    assert captured == {"name": "DPolG Bremen", "slug": "dpolg-bremen"}


async def test_apply_for_tenant_rejects_invalid_slug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_create(_session: Any, **_: Any) -> Tenant:  # pragma: no cover
        msg = "should not be called"
        raise AssertionError(msg)

    monkeypatch.setattr(use_cases.tenants_repo, "create_tenant_application", _fake_create)
    with pytest.raises(SlugValidationError):
        # Name >= 3 Zeichen, damit Name-Validierung passiert und Slug-Validierung greift.
        await use_cases.apply_for_tenant(None, name="DPolG", slug="DPolG")  # type: ignore[arg-type]


async def test_apply_for_tenant_rejects_short_name(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_create(_session: Any, **_: Any) -> Tenant:  # pragma: no cover
        msg = "should not be called"
        raise AssertionError(msg)

    monkeypatch.setattr(use_cases.tenants_repo, "create_tenant_application", _fake_create)
    with pytest.raises(ValueError, match=r"3-120"):
        await use_cases.apply_for_tenant(None, name="ab", slug="abc")  # type: ignore[arg-type]


async def test_apply_for_tenant_strips_name_whitespace(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    async def _fake_create(
        _session: Any,
        *,
        name: str,
        slug: str,
    ) -> Tenant:
        captured["name"] = name
        return _make_tenant(name=name, slug=slug)

    monkeypatch.setattr(use_cases.tenants_repo, "create_tenant_application", _fake_create)
    await use_cases.apply_for_tenant(None, name="  DPolG  ", slug="dpolg")  # type: ignore[arg-type]
    assert captured["name"] == "DPolG"


# ─── approve_tenant / deactivate_tenant ──────────────────────────────────────


async def test_approve_tenant_returns_repository_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant(status=TENANT_STATUS_ACTIVE)

    async def _fake_approve(_session: Any, _tid: uuid.UUID) -> Tenant:
        return tenant

    monkeypatch.setattr(use_cases.tenants_repo, "approve_tenant", _fake_approve)
    result = await use_cases.approve_tenant(None, uuid.uuid4())  # type: ignore[arg-type]
    assert result is tenant


async def test_approve_tenant_raises_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_approve(_session: Any, _tid: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(use_cases.tenants_repo, "approve_tenant", _fake_approve)
    with pytest.raises(use_cases.TenantNotFoundError):
        await use_cases.approve_tenant(None, uuid.uuid4())  # type: ignore[arg-type]


async def test_deactivate_tenant_raises_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_deactivate(_session: Any, _tid: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(use_cases.tenants_repo, "deactivate_tenant", _fake_deactivate)
    with pytest.raises(use_cases.TenantNotFoundError):
        await use_cases.deactivate_tenant(None, uuid.uuid4())  # type: ignore[arg-type]


# ─── invite_dispatcher / invite_carer ────────────────────────────────────────


async def test_invite_dispatcher_blocks_inactive_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant(status=TENANT_STATUS_APPLIED)

    async def _fake_find(_session: Any, _tid: uuid.UUID) -> Tenant:
        return tenant

    monkeypatch.setattr(use_cases.tenants_repo, "find_tenant_by_id", _fake_find)
    with pytest.raises(use_cases.TenantNotActiveError) as exc_info:
        await use_cases.invite_dispatcher(
            None,  # type: ignore[arg-type]
            tenant_id=tenant.id,
            username="alice",
            email=None,
            secret=SECRET,
        )
    assert exc_info.value.status == TENANT_STATUS_APPLIED


async def test_invite_dispatcher_blocks_deactivated_tenant(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant(status=TENANT_STATUS_DEACTIVATED)

    async def _fake_find(_session: Any, _tid: uuid.UUID) -> Tenant:
        return tenant

    monkeypatch.setattr(use_cases.tenants_repo, "find_tenant_by_id", _fake_find)
    with pytest.raises(use_cases.TenantNotActiveError):
        await use_cases.invite_dispatcher(
            None,  # type: ignore[arg-type]
            tenant_id=tenant.id,
            username="alice",
            email=None,
            secret=SECRET,
        )


async def test_invite_dispatcher_raises_tenant_not_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_find(_session: Any, _tid: uuid.UUID) -> None:
        return None

    monkeypatch.setattr(use_cases.tenants_repo, "find_tenant_by_id", _fake_find)
    with pytest.raises(use_cases.TenantNotFoundError):
        await use_cases.invite_dispatcher(
            None,  # type: ignore[arg-type]
            tenant_id=uuid.uuid4(),
            username="alice",
            email=None,
            secret=SECRET,
        )


async def test_invite_dispatcher_validates_username(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant()

    async def _fake_find(_session: Any, _tid: uuid.UUID) -> Tenant:
        return tenant

    monkeypatch.setattr(use_cases.tenants_repo, "find_tenant_by_id", _fake_find)
    with pytest.raises(UsernameValidationError):
        await use_cases.invite_dispatcher(
            None,  # type: ignore[arg-type]
            tenant_id=tenant.id,
            username="ab",  # zu kurz
            email=None,
            secret=SECRET,
        )


async def test_invite_dispatcher_returns_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant()
    dispatcher = Dispatcher(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        username="alice",
        password_hash="",
        is_active=False,
    )

    async def _fake_find(_session: Any, _tid: uuid.UUID) -> Tenant:
        return tenant

    async def _fake_invite(
        _session: Any,
        **_: Any,
    ) -> Dispatcher:
        return dispatcher

    monkeypatch.setattr(use_cases.tenants_repo, "find_tenant_by_id", _fake_find)
    monkeypatch.setattr(use_cases.tenants_repo, "invite_dispatcher", _fake_invite)
    result = await use_cases.invite_dispatcher(
        None,  # type: ignore[arg-type]
        tenant_id=tenant.id,
        username="alice",
        email="alice@example.org",
        secret=SECRET,
    )
    assert result.user_id == dispatcher.id
    assert result.expires_in_seconds == 24 * 60 * 60
    assert result.reset_token  # non-empty


async def test_invite_carer_returns_token(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    tenant = _make_tenant()
    carer = Carer(
        id=uuid.uuid4(),
        tenant_id=tenant.id,
        username="bob",
        password_hash="",
        is_active=False,
    )

    async def _fake_find(_session: Any, _tid: uuid.UUID) -> Tenant:
        return tenant

    async def _fake_invite(
        _session: Any,
        **_: Any,
    ) -> Carer:
        return carer

    monkeypatch.setattr(use_cases.tenants_repo, "find_tenant_by_id", _fake_find)
    monkeypatch.setattr(use_cases.tenants_repo, "invite_carer", _fake_invite)
    result = await use_cases.invite_carer(
        None,  # type: ignore[arg-type]
        tenant_id=tenant.id,
        username="bob",
        email=None,
        secret=SECRET,
    )
    assert result.user_id == carer.id


# ─── complete_password_reset ─────────────────────────────────────────────────


async def test_complete_password_reset_short_password_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(use_cases.PasswordTooShortError):
        await use_cases.complete_password_reset(
            None,  # type: ignore[arg-type]
            token="any",
            new_password="short",
            secret=SECRET,
        )


async def test_complete_password_reset_invalid_token_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with pytest.raises(use_cases.InvalidResetTokenError):
        await use_cases.complete_password_reset(
            None,  # type: ignore[arg-type]
            token="garbage-token",
            new_password="long-enough-password",
            secret=SECRET,
        )


async def test_complete_password_reset_replay_raises_user_already_active(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from eb_digital.auth.reset_token import generate_reset_token

    subject_id = uuid.uuid4()
    token = generate_reset_token("dispatcher", subject_id, SECRET)

    async def _fake_set(
        *, kind: str, subject_id: uuid.UUID, password_hash: str, _session: Any = None
    ) -> bool:
        return False  # User already active

    async def _fake_set_wrapper(_session: Any, **kwargs: Any) -> bool:
        return await _fake_set(**kwargs)

    monkeypatch.setattr(
        use_cases.tenants_repo,
        "set_password_and_activate",
        _fake_set_wrapper,
    )
    with pytest.raises(use_cases.UserAlreadyActiveError):
        await use_cases.complete_password_reset(
            None,  # type: ignore[arg-type]
            token=token,
            new_password="long-enough-password",
            secret=SECRET,
        )


async def test_complete_password_reset_success_returns_kind(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from eb_digital.auth.reset_token import generate_reset_token

    subject_id = uuid.uuid4()
    token = generate_reset_token("dispatcher", subject_id, SECRET)
    captured: dict[str, Any] = {}

    async def _fake_set(_session: Any, **kwargs: Any) -> bool:
        captured.update(kwargs)
        return True

    monkeypatch.setattr(
        use_cases.tenants_repo,
        "set_password_and_activate",
        _fake_set,
    )
    result = await use_cases.complete_password_reset(
        None,  # type: ignore[arg-type]
        token=token,
        new_password="long-enough-password",
        secret=SECRET,
    )
    assert result == KIND_DISPATCHER
    # Hash wurde mit der Library gehasht (Argon2id-PHC).
    assert captured["password_hash"].startswith("$argon2")
    assert captured["subject_id"] == subject_id
