"""Tests für ``backend/eb_digital/auth_anonymous/sessions``.

Cookie-Layer für anonyme Einsatzkraft-Sessions. Strategie analog
``test_auth_sessions.py``: Mini-FastAPI-App mit echtem
``SessionMiddleware`` plus Direkt-Aufrufe gegen Stub-Requests.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request

from eb_digital.auth_anonymous.models import AnonymousSession
from eb_digital.auth_anonymous.sessions import (
    ANON_SESSION_KEY,
    AnonymousSessionUser,
    clear_anonymous_session,
    get_current_anonymous_session,
    set_anonymous_session,
)


def _build_record() -> AnonymousSession:
    record = AnonymousSession(
        id=uuid.uuid4(),
        operation_id=uuid.uuid4(),
    )
    now = datetime.now(UTC)
    record.created_at = now
    record.last_seen_at = now
    record.expires_at = now + timedelta(hours=24)
    return record


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key="test-secret-key-for-anon-sessions")

    record = _build_record()

    @app.post("/login-anon")
    async def login_anon(request: Request) -> dict[str, Any]:
        user = set_anonymous_session(request, record)
        return {
            "session_id": str(user.session_id),
            "operation_id": str(user.operation_id),
            "expires_at": user.expires_at.isoformat(),
        }

    @app.get("/whoami")
    async def whoami(request: Request) -> dict[str, Any]:
        user = get_current_anonymous_session(request)
        if user is None:
            return {"authenticated": False}
        return {
            "authenticated": True,
            "session_id": str(user.session_id),
            "operation_id": str(user.operation_id),
        }

    @app.post("/clear-anon")
    async def clear(request: Request) -> dict[str, bool]:
        clear_anonymous_session(request)
        return {"cleared": True}

    @app.get("/inject-bad-payload")
    async def bad_payload(request: Request) -> dict[str, bool]:
        request.session[ANON_SESSION_KEY] = "not-a-dict"
        user = get_current_anonymous_session(request)
        return {"got_user": user is not None}

    @app.get("/inject-malformed-uuid")
    async def malformed_uuid(request: Request) -> dict[str, Any]:
        request.session[ANON_SESSION_KEY] = {
            "session_id": "not-a-uuid",
            "operation_id": "also-not",
            "expires_at": "garbage",
        }
        user = get_current_anonymous_session(request)
        # Cleanup-Pfad muss die Payload entfernt haben.
        return {
            "got_user": user is not None,
            "session_still_present": ANON_SESSION_KEY in request.session,
        }

    @app.get("/inject-expired")
    async def expired(request: Request) -> dict[str, Any]:
        past = (datetime.now(UTC) - timedelta(seconds=1)).isoformat()
        request.session[ANON_SESSION_KEY] = {
            "session_id": str(uuid.uuid4()),
            "operation_id": str(uuid.uuid4()),
            "expires_at": past,
        }
        user = get_current_anonymous_session(request)
        return {
            "got_user": user is not None,
            "session_still_present": ANON_SESSION_KEY in request.session,
        }

    return app


def test_set_session_persists_payload_across_requests() -> None:
    client = TestClient(_build_app())
    client.post("/login-anon")
    me = client.get("/whoami").json()
    assert me["authenticated"] is True
    assert uuid.UUID(me["session_id"]).version == 4


def test_whoami_returns_unauthenticated_without_session() -> None:
    client = TestClient(_build_app())
    assert client.get("/whoami").json() == {"authenticated": False}


def test_clear_invalidates_subsequent_requests() -> None:
    client = TestClient(_build_app())
    client.post("/login-anon")
    assert client.get("/whoami").json()["authenticated"] is True
    client.post("/clear-anon")
    assert client.get("/whoami").json()["authenticated"] is False


def test_non_dict_payload_is_rejected() -> None:
    client = TestClient(_build_app())
    response = client.get("/inject-bad-payload")
    assert response.json() == {"got_user": False}


def test_malformed_uuid_payload_is_rejected_and_cleaned() -> None:
    client = TestClient(_build_app())
    response = client.get("/inject-malformed-uuid")
    body = response.json()
    assert body["got_user"] is False
    assert body["session_still_present"] is False


def test_expired_session_is_rejected_and_cleaned() -> None:
    client = TestClient(_build_app())
    response = client.get("/inject-expired")
    body = response.json()
    assert body["got_user"] is False
    assert body["session_still_present"] is False


def test_set_session_returns_anonymous_session_user_container() -> None:
    """Direkter Aufruf gegen Stub-Request — Container-Form prüfen."""

    class _StubRequest:
        def __init__(self) -> None:
            self.session: dict[str, Any] = {}

    request = _StubRequest()
    record = _build_record()
    user = set_anonymous_session(request, record)  # type: ignore[arg-type]
    assert isinstance(user, AnonymousSessionUser)
    assert user.session_id == record.id
    assert user.operation_id == record.operation_id
    assert user.expires_at == record.expires_at
    # Payload wurde gesetzt und enthält keine Identitäts-PII.
    payload = request.session[ANON_SESSION_KEY]
    assert set(payload.keys()) == {"session_id", "operation_id", "expires_at"}


def test_clear_anonymous_session_direct_call_is_idempotent() -> None:
    """``clear_anonymous_session`` darf auch ohne vorherige Session aufgerufen
    werden (defensiver Cleanup-Pfad)."""

    class _StubRequest:
        def __init__(self) -> None:
            self.session: dict[str, Any] = {}

    request = _StubRequest()
    clear_anonymous_session(request)  # type: ignore[arg-type]
    assert request.session == {}
