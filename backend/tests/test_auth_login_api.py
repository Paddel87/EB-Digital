"""Tests für ``backend/eb_digital/auth/api`` — Login / Logout / Me.

Strategie:
  • Echtes ``SessionMiddleware`` (Cookie-Round-Trip wird mit-getestet).
  • ``valkey``-Client als ``fakeredis.aioredis.FakeRedis`` über
    ``dependency_overrides``.
  • DB-Session als minimaler Stub, der ``find_by_username``-Aufruf abfängt.
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
from eb_digital.auth.rate_limit import (
    LOGIN_LIMIT,
    LOGIN_WINDOW_SECONDS,
    login_ip_key,
    login_user_key,
)
from eb_digital.auth.repositories import (
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
    AuthSubject,
)

# ─── Stubs für DB-Session und Repository-Lookup ───────────────────────────────


class _StubDbSession:
    """Wird als Substitut für ``AsyncSession`` durchgereicht; ``find_by_username``
    wird über Monkeypatch vollständig abgefangen, also sind hier keine echten
    Methoden nötig."""


def _build_subject(
    *,
    kind: str = KIND_DISPATCHER,
    username: str = "alice",
    password: str = "correcthorsebattery",
    is_active: bool = True,
    tenant_id: uuid.UUID | None = None,
) -> AuthSubject:
    return AuthSubject(
        kind=kind,  # type: ignore[arg-type]
        id=uuid.uuid4(),
        username=username,
        password_hash=hash_password(password),
        is_active=is_active,
        tenant_id=tenant_id
        if tenant_id is not None
        else (None if kind == KIND_PLATFORM_ADMIN else uuid.uuid4()),
    )


# ─── Test-App-Fabrik mit dependency_overrides ────────────────────────────────


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
    """Liefert eine Factory ``make_client(subjects)`` für jeweilige Test-Szenarien.

    ``subjects`` ist eine ``dict[username, AuthSubject | None]``-Map; bei
    ``None`` antwortet ``find_by_username`` mit ``None`` (User existiert nicht).
    """

    def _make(subjects: dict[str, AuthSubject | None]) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return _StubDbSession()

        async def _override_find(_session: Any, username: str) -> AuthSubject | None:
            return subjects.get(username)

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(auth_api, "find_by_username", _override_find)

        # 2.4: Login-Pfad fragt Tenant-Status ab; ohne echte DB einfach
        # durchlassen (Tenant-Status-Check wird in
        # ``test_auth_login_tenant_status.py`` separat geprüft).
        async def _allow_tenant_login(_db: Any, _subject: Any) -> bool:
            return True

        monkeypatch.setattr(auth_api, "_tenant_login_allowed", _allow_tenant_login)

        return TestClient(app)

    return _make


# ─── Login-Tests ─────────────────────────────────────────────────────────────


def test_login_success_for_dispatcher_returns_session_user(make_client: Any) -> None:
    subject = _build_subject(kind=KIND_DISPATCHER, username="alice")
    with make_client({"alice": subject}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
    assert response.status_code == 200
    body = response.json()
    assert body["kind"] == KIND_DISPATCHER
    assert body["username"] == "alice"
    assert body["tenant_id"] is not None
    # Session-Cookie wird gesetzt.
    assert any(c.name == "eb_session" for c in client.cookies.jar)


def test_login_success_for_platform_admin_has_no_tenant_id(make_client: Any) -> None:
    subject = _build_subject(
        kind=KIND_PLATFORM_ADMIN,
        username="patrick",
        tenant_id=None,
    )
    with make_client({"patrick": subject}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "patrick", "password": "correcthorsebattery"},
        )
    assert response.status_code == 200
    assert response.json()["tenant_id"] is None


def test_login_with_wrong_password_returns_401(make_client: Any) -> None:
    subject = _build_subject(username="alice", password="correcthorsebattery")
    with make_client({"alice": subject}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "wrong-password!!"},
        )
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


def test_login_with_unknown_username_returns_401(make_client: Any) -> None:
    with make_client({"alice": None}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "ghost", "password": "correcthorsebattery"},
        )
    assert response.status_code == 401


def test_login_for_inactive_dispatcher_returns_401(make_client: Any) -> None:
    subject = _build_subject(username="alice", is_active=False)
    with make_client({"alice": subject}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
    assert response.status_code == 401
    # Identische Antwort wie wrong-password — kein Info-Leak.
    assert response.json() == {"detail": "Invalid credentials."}


def test_login_short_password_is_rejected_before_hash_check(make_client: Any) -> None:
    """Pydantic-Validierung lehnt zu kurze Passwörter mit 422 ab."""
    with make_client({"alice": None}) as client:
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "short"},
        )
    assert response.status_code == 422


# ─── Rate-Limit-Tests ────────────────────────────────────────────────────────


def test_six_failed_attempts_for_same_user_trip_user_counter(
    make_client: Any,
) -> None:
    subject = _build_subject(username="alice")
    with make_client({"alice": subject}) as client:
        for _ in range(LOGIN_LIMIT):
            response = client.post(
                "/api/auth/login",
                json={"username": "alice", "password": "wrong-password!!"},
            )
            assert response.status_code == 401

        # 6. Versuch — User-Counter ist über 5.
        response = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "wrong-password!!"},
        )
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert int(response.headers["Retry-After"]) <= LOGIN_WINDOW_SECONDS


def test_brute_force_sweep_across_usernames_trips_ip_counter(
    make_client: Any,
) -> None:
    # 5 verschiedene Username, alle nicht existent — IP-Counter zieht.
    with make_client({}) as client:
        for n in range(LOGIN_LIMIT):
            response = client.post(
                "/api/auth/login",
                json={"username": f"u{n}", "password": "correcthorsebattery"},
            )
            assert response.status_code == 401

        # 6. Versuch gegen 6. Username → IP-Counter ist über 5.
        response = client.post(
            "/api/auth/login",
            json={"username": "u-fresh", "password": "correcthorsebattery"},
        )
        assert response.status_code == 429


def test_successful_login_resets_user_counter(
    make_client: Any,
    fake_valkey: fakeredis.aioredis.FakeRedis,
) -> None:
    subject = _build_subject(username="alice", password="correcthorsebattery")
    with make_client({"alice": subject}) as client:
        # 4 Fehlversuche, dann Erfolg.
        for _ in range(4):
            client.post(
                "/api/auth/login",
                json={"username": "alice", "password": "wrong-password!!"},
            )
        success = client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
        assert success.status_code == 200

    # User-Counter wurde gelöscht; IP-Counter steht weiterhin (4 Fehler + 1 Erfolg = 5).
    import asyncio

    async def _fetch() -> tuple[Any, Any]:
        u = await fake_valkey.get(login_user_key("alice"))
        i = await fake_valkey.get(login_ip_key("testclient"))
        return u, i

    user_count, ip_count = asyncio.get_event_loop().run_until_complete(_fetch())
    assert user_count is None  # User-Counter gelöscht.
    assert ip_count is not None
    assert int(ip_count) == LOGIN_LIMIT


# ─── /me und Logout ──────────────────────────────────────────────────────────


def test_me_returns_401_without_session(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_session_user_after_login(make_client: Any) -> None:
    subject = _build_subject(username="alice")
    with make_client({"alice": subject}) as client:
        client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
        response = client.get("/api/auth/me")
    assert response.status_code == 200
    body = response.json()
    assert body["username"] == "alice"
    assert body["kind"] == KIND_DISPATCHER


def test_logout_returns_204_and_clears_session(make_client: Any) -> None:
    subject = _build_subject(username="alice")
    with make_client({"alice": subject}) as client:
        client.post(
            "/api/auth/login",
            json={"username": "alice", "password": "correcthorsebattery"},
        )
        assert client.get("/api/auth/me").status_code == 200
        logout = client.post("/api/auth/logout")
        assert logout.status_code == 204
        assert client.get("/api/auth/me").status_code == 401


# ─── Hilfsfunktionen-Tests ───────────────────────────────────────────────────


def test_extract_client_ip_prefers_x_forwarded_for() -> None:
    from starlette.requests import Request

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [(b"x-forwarded-for", b"203.0.113.45, 198.51.100.7")],
        "client": ("127.0.0.1", 5000),
    }
    request = Request(scope)
    assert auth_api.extract_client_ip(request) == "203.0.113.45"


def test_extract_client_ip_falls_back_to_request_client() -> None:
    from starlette.requests import Request

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "client": ("198.51.100.7", 5000),
    }
    request = Request(scope)
    assert auth_api.extract_client_ip(request) == "198.51.100.7"


def test_extract_client_ip_returns_unknown_when_no_client_info() -> None:
    from starlette.requests import Request

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": [],
        "client": None,
    }
    request = Request(scope)
    assert auth_api.extract_client_ip(request) == auth_api.UNKNOWN_IP


@pytest.mark.asyncio
async def test_get_valkey_client_raises_without_app_state() -> None:
    from starlette.requests import Request

    class _AppNoState:
        class state:  # noqa: N801
            pass

    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "app": _AppNoState(),
        }
    )
    with pytest.raises(RuntimeError, match="Valkey-Client"):
        await auth_api.get_valkey_client(request)


@pytest.mark.asyncio
async def test_get_db_session_raises_without_app_state() -> None:
    from starlette.requests import Request

    class _AppNoState:
        class state:  # noqa: N801
            pass

    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "app": _AppNoState(),
        }
    )
    with pytest.raises(RuntimeError, match="DB-Session-Factory"):
        await auth_api.get_db_session(request)


@pytest.mark.asyncio
async def test_get_valkey_client_returns_state_value(
    fake_valkey: fakeredis.aioredis.FakeRedis,
) -> None:
    from starlette.requests import Request

    class _StateBag:
        valkey = fake_valkey

    class _AppWithState:
        state = _StateBag()

    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "app": _AppWithState(),
        }
    )
    client = await auth_api.get_valkey_client(request)
    assert client is fake_valkey


@pytest.mark.asyncio
async def test_get_db_session_invokes_factory_and_returns_session() -> None:
    from starlette.requests import Request

    class _StubSession:
        async def __aenter__(self) -> _StubSession:
            return self

        async def __aexit__(self, *args: object) -> None:
            return None

    def _factory() -> _StubSession:
        return _StubSession()

    class _StateBag:
        pass

    state = _StateBag()
    state.db_session_factory = _factory  # type: ignore[attr-defined]

    class _AppWithState:
        pass

    app = _AppWithState()
    app.state = state  # type: ignore[attr-defined]

    request = Request(
        scope={
            "type": "http",
            "method": "GET",
            "path": "/",
            "headers": [],
            "app": app,
        }
    )
    session = await auth_api.get_db_session(request)
    assert isinstance(session, _StubSession)
