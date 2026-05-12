"""Tests für die 2.4-Erweiterung: Tenant-Status-Check im Login-Pfad.

Dispatcher/Carer in einem nicht-aktiven Tenant (``applied`` vor Approve
oder ``deactivated`` nach DSGVO-Stop) sollen mit 401 abgewiesen werden —
identische Antwort wie wrong-password (kein Info-Leak).
"""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from eb_digital.auth import api as auth_api
from eb_digital.auth.api import get_db_session, get_valkey_client
from eb_digital.auth.hashing import hash_password
from eb_digital.auth.repositories import (
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
    AuthSubject,
)
from eb_digital.tenants.models import (
    TENANT_STATUS_ACTIVE,
    TENANT_STATUS_APPLIED,
    TENANT_STATUS_DEACTIVATED,
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


def _build_subject(
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
    def _make(
        subjects: dict[str, AuthSubject | None],
        tenants_by_id: dict[uuid.UUID, Tenant | None],
    ) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return _StubDbSession()

        async def _fake_find_subject(_session: Any, username: str) -> AuthSubject | None:
            return subjects.get(username)

        async def _fake_find_tenant(_session: Any, tid: uuid.UUID) -> Tenant | None:
            return tenants_by_id.get(tid)

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(auth_api, "find_by_username", _fake_find_subject)
        monkeypatch.setattr(
            auth_api.tenants_repo,
            "find_tenant_by_id",
            _fake_find_tenant,
        )
        return TestClient(app)

    return _make


def _make_tenant(*, status: str) -> Tenant:
    return Tenant(
        id=uuid.uuid4(),
        name="Test",
        slug="test",
        status=status,
    )


def test_dispatcher_in_active_tenant_can_login(make_client: Any) -> None:
    tenant = _make_tenant(status=TENANT_STATUS_ACTIVE)
    subject = _build_subject(tenant_id=tenant.id)
    with make_client({"alice": subject}, {tenant.id: tenant}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
    assert response.status_code == 200


def test_dispatcher_in_applied_tenant_returns_401(make_client: Any) -> None:
    tenant = _make_tenant(status=TENANT_STATUS_APPLIED)
    subject = _build_subject(tenant_id=tenant.id)
    with make_client({"alice": subject}, {tenant.id: tenant}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


def test_dispatcher_in_deactivated_tenant_returns_401(make_client: Any) -> None:
    tenant = _make_tenant(status=TENANT_STATUS_DEACTIVATED)
    subject = _build_subject(tenant_id=tenant.id)
    with make_client({"alice": subject}, {tenant.id: tenant}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
    assert response.status_code == 401


def test_dispatcher_with_missing_tenant_record_returns_401(make_client: Any) -> None:
    """Defensive: Datenintegritäts-Bug (Dispatcher zeigt auf nicht existierenden Tenant)."""
    tenant_id = uuid.uuid4()
    subject = _build_subject(tenant_id=tenant_id)
    with make_client({"alice": subject}, {}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
    assert response.status_code == 401


def test_platform_admin_login_does_not_check_tenant(make_client: Any) -> None:
    """PlatformAdmin hat keine Tenant-Bindung — Login muss erlaubt sein."""
    admin = _build_subject(kind=KIND_PLATFORM_ADMIN, username="patrick", tenant_id=None)
    with make_client({"patrick": admin}, {}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "patrick", "password": "correcthorsebattery"},
        )
    assert response.status_code == 200
