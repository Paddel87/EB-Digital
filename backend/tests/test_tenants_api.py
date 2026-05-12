"""Tests für ``backend/eb_digital/tenants/api`` (Tenants-CRUD + Invites).

Berechtigungs-Modell:
  • Plattform-Admin: alles
  • Dispatcher des Mandanten: alles auf eigenem Tenant + Invites
  • Dispatcher anderen Mandanten: 403
  • Carer: 403 (keine Verwaltungs-Rechte)
  • Ohne Auth: 401

Strategie analog ``test_auth_login_api`` — echtes ``SessionMiddleware``
(Cookie-Round-Trip), ``fakeredis`` als Valkey-Stub, DB-Session als Stub,
Repository-Funktionen via ``monkeypatch`` ersetzt.

Sessions werden direkt über den Login-Endpoint mit ``find_by_username``-Stub
gesetzt (vermeidet das manuelle Cookie-Bauen).
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from typing import Any

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from eb_digital.auth import api as auth_api
from eb_digital.auth.api import get_db_session, get_valkey_client
from eb_digital.auth.hashing import hash_password
from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
    AuthSubject,
)
from eb_digital.tenants import api as tenants_api
from eb_digital.tenants import repositories as tenants_repo
from eb_digital.tenants import use_cases as tenants_use_cases
from eb_digital.tenants.models import (
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_APPLIED,
    Tenant,
)


class _StubDbSession:
    async def commit(self) -> None:
        return None


@pytest.fixture
async def fake_valkey() -> AsyncIterator[fakeredis.aioredis.FakeRedis]:
    client = fakeredis.aioredis.FakeRedis()
    try:
        yield client
    finally:
        await client.flushall()
        await client.aclose()


def _make_tenant(
    *,
    status: str = TENANT_STATUS_ACTIVE,
    name: str = "DPolG Bremen",
    slug: str = "dpolg-bremen",
    tenant_id: uuid.UUID | None = None,
) -> Tenant:
    now = datetime.now(UTC)
    return Tenant(
        id=tenant_id or uuid.uuid4(),
        name=name,
        slug=slug,
        status=status,
        applied_at=now,
        # ``activated_at``/``deactivated_at`` bleiben None — vom API-Mapper
        # defensiv gehandhabt.
    )


def _make_subject(
    *,
    kind: str = KIND_DISPATCHER,
    username: str = "alice",
    password: str = "correcthorsebattery",
    tenant_id: uuid.UUID | None = None,
) -> AuthSubject:
    return AuthSubject(
        kind=kind,  # type: ignore[arg-type]
        id=uuid.uuid4(),
        username=username,
        password_hash=hash_password(password),
        is_active=True,
        tenant_id=tenant_id
        if tenant_id is not None
        else (None if kind == KIND_PLATFORM_ADMIN else uuid.uuid4()),
    )


@pytest.fixture
def make_client(
    monkeypatch: pytest.MonkeyPatch,
    fake_valkey: fakeredis.aioredis.FakeRedis,
) -> Any:
    """Liefert ``make_client(behavior)`` mit umfassend konfigurierbarem Stub.

    ``behavior`` kann enthalten:
      • ``subjects``: ``{username: AuthSubject | None}`` für Login.
      • ``tenants_by_id``: ``{tenant_id: Tenant | None}`` für find/list.
      • ``approve_returns``, ``deactivate_returns``: Tenant-Override.
      • ``invite_dispatcher_result``, ``invite_carer_result``:
        ``ResetTokenIssued`` oder ``Exception``.
      • ``is_dispatcher_of_tenant``: ``bool`` (Default ``True``, wenn der
        Dispatcher-Subject auf den Ziel-Tenant passt).
      • ``tenant_login_active``: ``bool`` für ``_tenant_login_allowed``-Override
        (default: True).
    """

    def _make(behavior: dict[str, Any]) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()

        subjects: dict[str, AuthSubject | None] = behavior.get("subjects", {})
        tenants_by_id: dict[uuid.UUID, Tenant | None] = behavior.get("tenants_by_id", {})

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return _StubDbSession()

        async def _fake_find_by_username(_session: Any, username: str) -> AuthSubject | None:
            return subjects.get(username)

        async def _fake_find_tenant_by_id(_session: Any, tid: uuid.UUID) -> Tenant | None:
            return tenants_by_id.get(tid)

        async def _fake_list_tenants(
            _session: Any,
            *,
            status_filter: str | None = None,
        ) -> list[Tenant]:
            tenants = [t for t in tenants_by_id.values() if t is not None]
            if status_filter is not None:
                tenants = [t for t in tenants if t.status == status_filter]
            return tenants

        async def _fake_approve(_session: Any, tid: uuid.UUID) -> Tenant:
            tenant = behavior.get("approve_returns")
            if tenant is None:
                raise tenants_use_cases.TenantNotFoundError(tid)
            return tenant

        async def _fake_deactivate(_session: Any, tid: uuid.UUID) -> Tenant:
            tenant = behavior.get("deactivate_returns")
            if tenant is None:
                raise tenants_use_cases.TenantNotFoundError(tid)
            return tenant

        async def _fake_invite_dispatcher(
            _session: Any,
            **_: Any,
        ) -> tenants_use_cases.ResetTokenIssued:
            v = behavior.get("invite_dispatcher_result")
            if isinstance(v, Exception):
                raise v
            return v or tenants_use_cases.ResetTokenIssued(
                user_id=uuid.uuid4(),
                reset_token="dummy-reset-token",
                expires_in_seconds=24 * 60 * 60,
            )

        async def _fake_invite_carer(
            _session: Any,
            **_: Any,
        ) -> tenants_use_cases.ResetTokenIssued:
            v = behavior.get("invite_carer_result")
            if isinstance(v, Exception):
                raise v
            return v or tenants_use_cases.ResetTokenIssued(
                user_id=uuid.uuid4(),
                reset_token="dummy-carer-token",
                expires_in_seconds=24 * 60 * 60,
            )

        async def _fake_is_dispatcher_of_tenant(
            _session: Any,
            *,
            dispatcher_id: uuid.UUID,
            tenant_id: uuid.UUID,
        ) -> bool:
            override = behavior.get("is_dispatcher_of_tenant")
            if override is not None:
                return bool(override)
            # Default: True, wenn der Test-Subject ein Dispatcher mit
            # passender tenant_id ist.
            for subject in subjects.values():
                if (
                    subject is not None
                    and subject.kind == KIND_DISPATCHER
                    and subject.id == dispatcher_id
                    and subject.tenant_id == tenant_id
                ):
                    return True
            return False

        async def _fake_tenant_login_allowed(
            _db: Any,
            _subject: AuthSubject,
        ) -> bool:
            return bool(behavior.get("tenant_login_active", True))

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(auth_api, "find_by_username", _fake_find_by_username)
        monkeypatch.setattr(
            auth_api,
            "_tenant_login_allowed",
            _fake_tenant_login_allowed,
        )
        monkeypatch.setattr(
            tenants_api.tenants_repo,
            "find_tenant_by_id",
            _fake_find_tenant_by_id,
        )
        monkeypatch.setattr(
            tenants_api.tenants_repo,
            "list_tenants",
            _fake_list_tenants,
        )
        monkeypatch.setattr(
            tenants_api.tenants_repo,
            "is_dispatcher_of_tenant",
            _fake_is_dispatcher_of_tenant,
        )
        monkeypatch.setattr(
            tenants_api.tenants_use_cases,
            "approve_tenant",
            _fake_approve,
        )
        monkeypatch.setattr(
            tenants_api.tenants_use_cases,
            "deactivate_tenant",
            _fake_deactivate,
        )
        monkeypatch.setattr(
            tenants_api.tenants_use_cases,
            "invite_dispatcher",
            _fake_invite_dispatcher,
        )
        monkeypatch.setattr(
            tenants_api.tenants_use_cases,
            "invite_carer",
            _fake_invite_carer,
        )

        return TestClient(app)

    return _make


def _login(client: TestClient, *, username: str, password: str = "correcthorsebattery") -> None:
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
    )
    assert response.status_code == 200, response.text


# ─── GET /api/tenants ────────────────────────────────────────────────────────


def test_get_tenants_without_auth_returns_401(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.get("/api/tenants")
    assert response.status_code == 401


def test_get_tenants_as_platform_admin_lists_all(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant_a = _make_tenant(slug="dpolg-bremen")
    tenant_b = _make_tenant(slug="dpolg-niedersachsen", status=TENANT_STATUS_APPLIED)
    with make_client(
        {
            "subjects": {"patrick": admin},
            "tenants_by_id": {tenant_a.id: tenant_a, tenant_b.id: tenant_b},
        },
    ) as client:
        _login(client, username="patrick")
        response = client.get("/api/tenants")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2


def test_get_tenants_as_dispatcher_returns_only_own(make_client: Any) -> None:
    own_tenant = _make_tenant(slug="dpolg-bremen")
    other_tenant = _make_tenant(slug="dpolg-niedersachsen")
    dispatcher = _make_subject(
        kind=KIND_DISPATCHER,
        username="alice",
        tenant_id=own_tenant.id,
    )
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "tenants_by_id": {
                own_tenant.id: own_tenant,
                other_tenant.id: other_tenant,
            },
        },
    ) as client:
        _login(client, username="alice")
        response = client.get("/api/tenants")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["slug"] == "dpolg-bremen"


def test_get_tenants_as_carer_returns_403(make_client: Any) -> None:
    own_tenant = _make_tenant()
    carer = _make_subject(
        kind=KIND_CARER,
        username="bob",
        tenant_id=own_tenant.id,
    )
    with make_client(
        {
            "subjects": {"bob": carer},
            "tenants_by_id": {own_tenant.id: own_tenant},
        },
    ) as client:
        _login(client, username="bob")
        response = client.get("/api/tenants")
    assert response.status_code == 403


def test_get_tenants_with_invalid_status_filter_returns_422(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client({"subjects": {"patrick": admin}}) as client:
        _login(client, username="patrick")
        response = client.get("/api/tenants?status=bogus")
    assert response.status_code == 422


def test_get_tenants_with_status_filter_works(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant_a = _make_tenant(status=TENANT_STATUS_ACTIVE, slug="active")
    tenant_b = _make_tenant(status=TENANT_STATUS_APPLIED, slug="applied")
    with make_client(
        {
            "subjects": {"patrick": admin},
            "tenants_by_id": {tenant_a.id: tenant_a, tenant_b.id: tenant_b},
        },
    ) as client:
        _login(client, username="patrick")
        response = client.get("/api/tenants?status=applied")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["slug"] == "applied"


# ─── GET /api/tenants/{id} ───────────────────────────────────────────────────


def test_get_tenant_by_id_as_admin_returns_200(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant = _make_tenant()
    with make_client(
        {
            "subjects": {"patrick": admin},
            "tenants_by_id": {tenant.id: tenant},
        },
    ) as client:
        _login(client, username="patrick")
        response = client.get(f"/api/tenants/{tenant.id}")
    assert response.status_code == 200


def test_get_tenant_by_id_unknown_returns_404(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client({"subjects": {"patrick": admin}, "tenants_by_id": {}}) as client:
        _login(client, username="patrick")
        response = client.get(f"/api/tenants/{uuid.uuid4()}")
    assert response.status_code == 404


def test_get_tenant_by_id_as_dispatcher_of_other_tenant_returns_403(
    make_client: Any,
) -> None:
    own_tenant = _make_tenant()
    other_tenant = _make_tenant(slug="other")
    dispatcher = _make_subject(
        kind=KIND_DISPATCHER,
        username="alice",
        tenant_id=own_tenant.id,
    )
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "tenants_by_id": {
                own_tenant.id: own_tenant,
                other_tenant.id: other_tenant,
            },
        },
    ) as client:
        _login(client, username="alice")
        response = client.get(f"/api/tenants/{other_tenant.id}")
    assert response.status_code == 403


def test_get_tenant_by_id_as_dispatcher_of_own_tenant_works(make_client: Any) -> None:
    own_tenant = _make_tenant()
    dispatcher = _make_subject(
        kind=KIND_DISPATCHER,
        username="alice",
        tenant_id=own_tenant.id,
    )
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "tenants_by_id": {own_tenant.id: own_tenant},
        },
    ) as client:
        _login(client, username="alice")
        response = client.get(f"/api/tenants/{own_tenant.id}")
    assert response.status_code == 200


# ─── POST /api/tenants/{id}/approve ──────────────────────────────────────────


def test_approve_as_admin_returns_200(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant = _make_tenant(status=TENANT_STATUS_ACTIVE)
    with make_client(
        {
            "subjects": {"patrick": admin},
            "approve_returns": tenant,
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(f"/api/tenants/{tenant.id}/approve")
    assert response.status_code == 200
    assert response.json()["status"] == TENANT_STATUS_ACTIVE


def test_approve_as_dispatcher_returns_403(make_client: Any) -> None:
    own_tenant = _make_tenant()
    dispatcher = _make_subject(
        kind=KIND_DISPATCHER,
        username="alice",
        tenant_id=own_tenant.id,
    )
    with make_client({"subjects": {"alice": dispatcher}}) as client:
        _login(client, username="alice")
        response = client.post(f"/api/tenants/{own_tenant.id}/approve")
    assert response.status_code == 403


def test_approve_unknown_tenant_returns_404(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    # ``approve_returns`` ist None — Use-Case wirft TenantNotFoundError.
    with make_client({"subjects": {"patrick": admin}}) as client:
        _login(client, username="patrick")
        response = client.post(f"/api/tenants/{uuid.uuid4()}/approve")
    assert response.status_code == 404


# ─── POST /api/tenants/{id}/deactivate ───────────────────────────────────────


def test_deactivate_as_admin_returns_200(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant = _make_tenant()
    with make_client(
        {
            "subjects": {"patrick": admin},
            "deactivate_returns": tenant,
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(f"/api/tenants/{tenant.id}/deactivate")
    assert response.status_code == 200


def test_deactivate_as_dispatcher_returns_403(make_client: Any) -> None:
    own_tenant = _make_tenant()
    dispatcher = _make_subject(
        kind=KIND_DISPATCHER,
        username="alice",
        tenant_id=own_tenant.id,
    )
    with make_client({"subjects": {"alice": dispatcher}}) as client:
        _login(client, username="alice")
        response = client.post(f"/api/tenants/{own_tenant.id}/deactivate")
    assert response.status_code == 403


# ─── POST /api/tenants/{id}/dispatchers ──────────────────────────────────────


def test_invite_dispatcher_as_admin_returns_201_with_token(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant = _make_tenant()
    with make_client(
        {
            "subjects": {"patrick": admin},
            "tenants_by_id": {tenant.id: tenant},
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(
            f"/api/tenants/{tenant.id}/dispatchers",
            json={"username": "newdisp", "email": None},
        )
    assert response.status_code == 201
    body = response.json()
    assert "user_id" in body
    assert "reset_token" in body
    assert body["expires_in_seconds"] == 24 * 60 * 60


def test_invite_dispatcher_as_dispatcher_of_tenant_works(make_client: Any) -> None:
    own_tenant = _make_tenant()
    dispatcher = _make_subject(
        kind=KIND_DISPATCHER,
        username="alice",
        tenant_id=own_tenant.id,
    )
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "tenants_by_id": {own_tenant.id: own_tenant},
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            f"/api/tenants/{own_tenant.id}/dispatchers",
            json={"username": "newdisp"},
        )
    assert response.status_code == 201


def test_invite_dispatcher_as_dispatcher_of_other_tenant_returns_403(
    make_client: Any,
) -> None:
    own_tenant = _make_tenant()
    other_tenant = _make_tenant(slug="other")
    dispatcher = _make_subject(
        kind=KIND_DISPATCHER,
        username="alice",
        tenant_id=own_tenant.id,
    )
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "tenants_by_id": {own_tenant.id: own_tenant, other_tenant.id: other_tenant},
            "is_dispatcher_of_tenant": False,
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            f"/api/tenants/{other_tenant.id}/dispatchers",
            json={"username": "newdisp"},
        )
    assert response.status_code == 403


def test_invite_dispatcher_as_carer_returns_403(make_client: Any) -> None:
    own_tenant = _make_tenant()
    carer = _make_subject(kind=KIND_CARER, username="bob", tenant_id=own_tenant.id)
    with make_client(
        {
            "subjects": {"bob": carer},
            "tenants_by_id": {own_tenant.id: own_tenant},
        },
    ) as client:
        _login(client, username="bob")
        response = client.post(
            f"/api/tenants/{own_tenant.id}/dispatchers",
            json={"username": "newdisp"},
        )
    assert response.status_code == 403


def test_invite_dispatcher_username_collision_returns_409(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant = _make_tenant()
    with make_client(
        {
            "subjects": {"patrick": admin},
            "tenants_by_id": {tenant.id: tenant},
            "invite_dispatcher_result": tenants_repo.UsernameTakenInTenantError(
                tenant_id=tenant.id,
                username="alice",
                kind=KIND_DISPATCHER,
            ),
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(
            f"/api/tenants/{tenant.id}/dispatchers",
            json={"username": "alice"},
        )
    assert response.status_code == 409


def test_invite_dispatcher_inactive_tenant_returns_409(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant = _make_tenant(status=TENANT_STATUS_APPLIED)
    with make_client(
        {
            "subjects": {"patrick": admin},
            "tenants_by_id": {tenant.id: tenant},
            "invite_dispatcher_result": tenants_use_cases.TenantNotActiveError(
                tenant_id=tenant.id,
                status=TENANT_STATUS_APPLIED,
            ),
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(
            f"/api/tenants/{tenant.id}/dispatchers",
            json={"username": "alice"},
        )
    assert response.status_code == 409


def test_invite_dispatcher_invalid_username_returns_422(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant = _make_tenant()
    with make_client(
        {
            "subjects": {"patrick": admin},
            "tenants_by_id": {tenant.id: tenant},
        },
    ) as client:
        _login(client, username="patrick")
        # Username < 3 Zeichen → Pydantic 422
        response = client.post(
            f"/api/tenants/{tenant.id}/dispatchers",
            json={"username": "ab"},
        )
    assert response.status_code == 422


def test_invite_dispatcher_unknown_tenant_returns_404(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    with make_client(
        {
            "subjects": {"patrick": admin},
            "invite_dispatcher_result": tenants_use_cases.TenantNotFoundError(uuid.uuid4()),
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(
            f"/api/tenants/{uuid.uuid4()}/dispatchers",
            json={"username": "newdisp"},
        )
    assert response.status_code == 404


# ─── POST /api/tenants/{id}/carers ───────────────────────────────────────────


def test_invite_carer_as_admin_returns_201(make_client: Any) -> None:
    admin = _make_subject(kind=KIND_PLATFORM_ADMIN, username="patrick")
    tenant = _make_tenant()
    with make_client(
        {
            "subjects": {"patrick": admin},
            "tenants_by_id": {tenant.id: tenant},
        },
    ) as client:
        _login(client, username="patrick")
        response = client.post(
            f"/api/tenants/{tenant.id}/carers",
            json={"username": "newcarer"},
        )
    assert response.status_code == 201
    body = response.json()
    assert "user_id" in body
    assert "reset_token" in body


def test_invite_carer_as_dispatcher_of_tenant_works(make_client: Any) -> None:
    own_tenant = _make_tenant()
    dispatcher = _make_subject(
        kind=KIND_DISPATCHER,
        username="alice",
        tenant_id=own_tenant.id,
    )
    with make_client(
        {
            "subjects": {"alice": dispatcher},
            "tenants_by_id": {own_tenant.id: own_tenant},
        },
    ) as client:
        _login(client, username="alice")
        response = client.post(
            f"/api/tenants/{own_tenant.id}/carers",
            json={"username": "newcarer"},
        )
    assert response.status_code == 201
