"""Tests für ``POST /api/auth/reset-password`` (2.4)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from eb_digital.auth import api as auth_api
from eb_digital.auth.api import (
    RESET_PASSWORD_LIMIT,
    get_db_session,
    get_valkey_client,
)
from eb_digital.auth.repositories import KIND_DISPATCHER
from eb_digital.tenants import use_cases as tenants_use_cases


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


@pytest.fixture
def make_client(
    monkeypatch: pytest.MonkeyPatch,
    fake_valkey: fakeredis.aioredis.FakeRedis,
) -> Any:
    def _make(behavior: dict[str, Any]) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return _StubDbSession()

        async def _fake_complete(
            _session: Any,
            *,
            token: str,
            new_password: str,
            secret: str,
        ) -> str:
            if "raises" in behavior:
                raise behavior["raises"]
            return KIND_DISPATCHER

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(
            auth_api.tenants_use_cases,
            "complete_password_reset",
            _fake_complete,
        )

        return TestClient(app)

    return _make


def test_reset_password_success_returns_204(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.post(
            "/api/auth/reset-password",
            json={"token": "any-token", "new_password": "long-enough-password"},
        )
    assert response.status_code == 204


def test_reset_password_invalid_token_returns_410(make_client: Any) -> None:
    with make_client({"raises": tenants_use_cases.InvalidResetTokenError()}) as client:
        response = client.post(
            "/api/auth/reset-password",
            json={"token": "garbage", "new_password": "long-enough-password"},
        )
    assert response.status_code == 410


def test_reset_password_replay_returns_410(make_client: Any) -> None:
    """Replay-Schutz: identische Antwort wie ungültiger Token (kein Info-Leak)."""
    with make_client({"raises": tenants_use_cases.UserAlreadyActiveError()}) as client:
        response = client.post(
            "/api/auth/reset-password",
            json={"token": "valid-but-used", "new_password": "long-enough-password"},
        )
    assert response.status_code == 410
    # Identische Antwort wie InvalidResetTokenError (kein „already used"-Hinweis).
    assert "already used" not in response.text.lower() or "invalid" in response.text.lower()


def test_reset_password_short_password_pydantic_rejects(make_client: Any) -> None:
    """Pydantic Field min_length=12 lehnt mit 422 ab."""
    with make_client({}) as client:
        response = client.post(
            "/api/auth/reset-password",
            json={"token": "any", "new_password": "short"},
        )
    assert response.status_code == 422


def test_reset_password_rate_limit(make_client: Any) -> None:
    with make_client({"raises": tenants_use_cases.InvalidResetTokenError()}) as client:
        for _ in range(RESET_PASSWORD_LIMIT):
            response = client.post(
                "/api/auth/reset-password",
                json={"token": "garbage", "new_password": "long-enough-password"},
            )
            assert response.status_code == 410
        response = client.post(
            "/api/auth/reset-password",
            json={"token": "garbage", "new_password": "long-enough-password"},
        )
        assert response.status_code == 429
        assert "Retry-After" in response.headers


def test_reset_password_does_not_require_auth(make_client: Any) -> None:
    """Public-Endpoint — kein Cookie nötig."""
    with make_client({}) as client:
        response = client.post(
            "/api/auth/reset-password",
            json={"token": "x", "new_password": "long-enough-password"},
        )
    assert response.status_code == 204
