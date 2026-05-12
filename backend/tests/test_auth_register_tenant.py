"""Tests für ``POST /api/auth/register-tenant`` (2.4)."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from typing import Any

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from eb_digital.auth import api as auth_api
from eb_digital.auth.api import (
    REGISTER_TENANT_LIMIT,
    get_db_session,
    get_valkey_client,
)
from eb_digital.tenants import repositories as tenants_repo
from eb_digital.tenants import use_cases as tenants_use_cases
from eb_digital.tenants.models import TENANT_STATUS_APPLIED, Tenant


class _StubDbSession:
    """Stub-Session mit ``commit()``-Stub (Endpoint ruft commit() auf)."""

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


@pytest.fixture
def make_client(
    monkeypatch: pytest.MonkeyPatch,
    fake_valkey: fakeredis.aioredis.FakeRedis,
) -> Any:
    """Liefert ``make_client(behavior)``-Factory.

    ``behavior`` ist ein Dict mit:
      • ``apply_returns``: Tenant, der von ``apply_for_tenant`` zurückgegeben wird
      • ``apply_raises``: Exception, die statt der Erfolgs-Antwort geworfen wird
    """

    def _make(behavior: dict[str, Any]) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return _StubDbSession()

        async def _fake_apply(_session: Any, *, name: str, slug: str) -> Any:
            if "apply_raises" in behavior:
                raise behavior["apply_raises"]
            tenant = behavior.get("apply_returns") or Tenant(
                id=uuid.uuid4(),
                name=name,
                slug=slug,
                status=TENANT_STATUS_APPLIED,
            )
            return tenants_use_cases.TenantApplicationCreated(tenant=tenant)

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(auth_api.tenants_use_cases, "apply_for_tenant", _fake_apply)

        return TestClient(app)

    return _make


def test_register_tenant_success_returns_201(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.post(
            "/api/auth/register-tenant",
            json={"name": "DPolG Bremen", "slug": "dpolg-bremen"},
        )
    assert response.status_code == 201
    body = response.json()
    assert "tenant_id" in body
    assert body["status"] == TENANT_STATUS_APPLIED
    uuid.UUID(body["tenant_id"])  # gültige UUID


def test_register_tenant_invalid_slug_format_returns_422(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.post(
            "/api/auth/register-tenant",
            json={"name": "DPolG", "slug": "DPolG-Bremen"},  # Großbuchstaben
        )
    assert response.status_code == 422


def test_register_tenant_reserved_slug_returns_422(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.post(
            "/api/auth/register-tenant",
            json={"name": "Admin Verein", "slug": "admin"},
        )
    assert response.status_code == 422


def test_register_tenant_slug_collision_returns_409(make_client: Any) -> None:
    with make_client(
        {"apply_raises": tenants_repo.SlugAlreadyTakenError("dpolg-bremen")},
    ) as client:
        response = client.post(
            "/api/auth/register-tenant",
            json={"name": "DPolG", "slug": "dpolg-bremen"},
        )
    assert response.status_code == 409


def test_register_tenant_short_name_rejected_by_pydantic(make_client: Any) -> None:
    """Pydantic min_length=3 lehnt zu kurzen Namen mit 422 ab."""
    with make_client({}) as client:
        response = client.post(
            "/api/auth/register-tenant",
            json={"name": "ab", "slug": "abc"},
        )
    assert response.status_code == 422


def test_register_tenant_rate_limit_kicks_in_after_3_attempts(make_client: Any) -> None:
    with make_client({}) as client:
        for n in range(REGISTER_TENANT_LIMIT):
            response = client.post(
                "/api/auth/register-tenant",
                json={"name": f"Verein {n}", "slug": f"verein-{n}"},
            )
            assert response.status_code == 201
        response = client.post(
            "/api/auth/register-tenant",
            json={"name": "Late", "slug": "late"},
        )
        assert response.status_code == 429
        assert "Retry-After" in response.headers


def test_register_tenant_does_not_require_auth(make_client: Any) -> None:
    """Public-Endpoint — kein Cookie nötig."""
    with make_client({}) as client:
        # ohne Login direkt aufrufen
        response = client.post(
            "/api/auth/register-tenant",
            json={"name": "Public Verein", "slug": "public-verein"},
        )
    assert response.status_code == 201
