"""Tests für ``backend/eb_digital/auth/sessions``.

Wir nutzen Starlettes echtes ``SessionMiddleware`` über einen Mini-FastAPI-
App; das schützt vor Drift zwischen unserer Session-Helper-Logik und der
realen Cookie-Round-Trip-Semantik.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
    AuthSubject,
)
from eb_digital.auth.sessions import (
    CARER_TIMEOUT,
    DISPATCHER_TIMEOUT,
    PLATFORM_ADMIN_TIMEOUT,
    SESSION_KEY,
    SessionUser,
    clear_session,
    get_current_session_user,
    set_session,
)


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-secret-key-for-sessions-only")

    @app.post("/login/{kind}")
    async def login_route(
        kind: str,
        request: Request,
    ) -> dict[str, Any]:
        subject = AuthSubject(
            kind=kind,  # type: ignore[arg-type]
            id=uuid.uuid4(),
            username=f"user-{kind}",
            password_hash="$argon2id$…",
            is_active=True,
            tenant_id=uuid.uuid4() if kind != KIND_PLATFORM_ADMIN else None,
        )
        user = set_session(request, subject)
        return {"username": user.username, "expires_at": user.expires_at.isoformat()}

    @app.get("/me")
    async def me_route(request: Request) -> dict[str, Any]:
        user = get_current_session_user(request)
        if user is None:
            return {"authenticated": False}
        return {
            "authenticated": True,
            "kind": user.kind,
            "username": user.username,
            "tenant_id": str(user.tenant_id) if user.tenant_id else None,
        }

    @app.post("/logout")
    async def logout_route(request: Request) -> dict[str, bool]:
        clear_session(request)
        return {"ok": True}

    @app.get("/inject-bad-payload")
    async def bad_payload(request: Request) -> dict[str, Any]:
        request.session[SESSION_KEY] = {"kind": "alien", "id": "x"}
        user = get_current_session_user(request)
        return {"user": user is not None}

    return app


def test_set_session_persists_payload_across_requests() -> None:
    client = TestClient(_build_app())
    client.post(f"/login/{KIND_DISPATCHER}")
    me = client.get("/me").json()
    assert me["authenticated"] is True
    assert me["kind"] == KIND_DISPATCHER
    assert me["username"] == f"user-{KIND_DISPATCHER}"
    assert me["tenant_id"] is not None


def test_platform_admin_session_has_no_tenant_id() -> None:
    client = TestClient(_build_app())
    client.post(f"/login/{KIND_PLATFORM_ADMIN}")
    me = client.get("/me").json()
    assert me["kind"] == KIND_PLATFORM_ADMIN
    assert me["tenant_id"] is None


def test_get_current_session_user_returns_none_without_session() -> None:
    client = TestClient(_build_app())
    me = client.get("/me").json()
    assert me["authenticated"] is False


def test_clear_session_invalidates_subsequent_requests() -> None:
    client = TestClient(_build_app())
    client.post(f"/login/{KIND_CARER}")
    assert client.get("/me").json()["authenticated"] is True
    client.post("/logout")
    assert client.get("/me").json()["authenticated"] is False


def test_unknown_kind_in_payload_is_rejected_and_session_cleared() -> None:
    client = TestClient(_build_app())
    response = client.get("/inject-bad-payload")
    assert response.json()["user"] is False
    # Folge-/me/ findet keine Session, weil bad-payload Cleanup gemacht hat.
    assert client.get("/me").json()["authenticated"] is False


def test_malformed_uuid_in_payload_is_rejected() -> None:
    """Direktes Stub-Payload-Manipulation schlägt sauber fehl."""

    class _StubRequest:
        def __init__(self) -> None:
            self.session: dict[str, Any] = {
                SESSION_KEY: {"kind": KIND_DISPATCHER, "id": "not-a-uuid"},
            }

    user = get_current_session_user(_StubRequest())  # type: ignore[arg-type]
    assert user is None


def test_expired_session_is_cleared_and_returns_none() -> None:
    past = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
    payload = {
        "kind": KIND_DISPATCHER,
        "id": str(uuid.uuid4()),
        "username": "alice",
        "tenant_id": str(uuid.uuid4()),
        "expires_at": past,
    }

    class _StubRequest:
        def __init__(self) -> None:
            self.session: dict[str, Any] = {SESSION_KEY: payload}

    request = _StubRequest()
    user = get_current_session_user(request)  # type: ignore[arg-type]
    assert user is None
    # Cleanup: Session wurde geleert.
    assert SESSION_KEY not in request.session


def test_set_session_returns_session_user_with_correct_timeout() -> None:
    """Direkter Aufruf — keine Cookie-Round-Trip nötig für die Timeout-Prüfung."""

    class _StubRequest:
        def __init__(self) -> None:
            self.session: dict[str, Any] = {}

    request = _StubRequest()
    before = datetime.now(UTC)
    subject = AuthSubject(
        kind=KIND_PLATFORM_ADMIN,
        id=uuid.uuid4(),
        username="admin",
        password_hash="$argon2id$…",
        is_active=True,
        tenant_id=None,
    )
    user = set_session(request, subject)  # type: ignore[arg-type]
    after = datetime.now(UTC)
    elapsed = user.expires_at - before
    span = after - before
    assert PLATFORM_ADMIN_TIMEOUT <= elapsed <= PLATFORM_ADMIN_TIMEOUT + span
    assert isinstance(user, SessionUser)


@pytest.mark.parametrize(
    ("kind", "expected_timeout"),
    [
        (KIND_PLATFORM_ADMIN, PLATFORM_ADMIN_TIMEOUT),
        (KIND_DISPATCHER, DISPATCHER_TIMEOUT),
        (KIND_CARER, CARER_TIMEOUT),
    ],
)
def test_set_session_uses_role_specific_timeout(
    kind: str,
    expected_timeout: timedelta,
) -> None:
    class _StubRequest:
        def __init__(self) -> None:
            self.session: dict[str, Any] = {}

    subject = AuthSubject(
        kind=kind,  # type: ignore[arg-type]
        id=uuid.uuid4(),
        username="x",
        password_hash="$argon2id$…",
        is_active=True,
        tenant_id=None if kind == KIND_PLATFORM_ADMIN else uuid.uuid4(),
    )
    before = datetime.now(UTC)
    user = set_session(_StubRequest(), subject)  # type: ignore[arg-type]
    elapsed = user.expires_at - before
    # ±1 s Schlupf für die Wall-Clock zwischen Aufruf und Auswertung.
    assert (
        expected_timeout - timedelta(seconds=1)
        <= elapsed
        <= expected_timeout + timedelta(seconds=1)
    )


def test_unknown_kind_raises_value_error_in_set_session() -> None:
    class _StubRequest:
        def __init__(self) -> None:
            self.session: dict[str, Any] = {}

    subject = AuthSubject(
        kind="alien",  # type: ignore[arg-type]
        id=uuid.uuid4(),
        username="x",
        password_hash="$argon2id$…",
        is_active=True,
        tenant_id=None,
    )
    with pytest.raises(ValueError, match="Unknown subject kind"):
        set_session(_StubRequest(), subject)  # type: ignore[arg-type]
