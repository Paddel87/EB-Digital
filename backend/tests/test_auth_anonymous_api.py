"""Tests für ``backend/eb_digital/auth_anonymous/api``.

S2-Sub-Surface: ``GET /api/anon/{url}/info`` und
``POST /api/anon/{url}/session``. Strategie analog
``test_auth_login_api.py``:

  • Echte ``SessionMiddleware`` für Cookie-Round-Trip.
  • ``valkey`` als ``fakeredis.aioredis.FakeRedis`` via dependency_overrides.
  • Repository-Aufrufe per ``monkeypatch``.

Die DB-Session selbst wird durch einen minimalen Stub ersetzt, weil die
Operations-Erzeugung erst in 4.x landet und die Lookup-/Insert-Pfade über
gepatchte ``find_operation_by_id`` / ``create_anonymous_session`` laufen.
"""

from __future__ import annotations

import hashlib
import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta
from typing import Any

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from eb_digital.auth.api import get_db_session, get_valkey_client
from eb_digital.auth.rate_limit import LOGIN_LIMIT, LOGIN_WINDOW_SECONDS
from eb_digital.auth_anonymous import api as anon_api
from eb_digital.auth_anonymous.access_code import hash_access_code
from eb_digital.auth_anonymous.models import AnonymousSession
from eb_digital.auth_anonymous.tokens import generate_url_token
from eb_digital.operations.models import (
    OPERATION_STATUS_ACTIVE,
    OPERATION_STATUS_CLOSED,
    OPERATION_STATUS_PLANNED,
    Operation,
)
from eb_digital.settings import get_settings


class _StubDbSession:
    """Wird durchgereicht; Repository-Aufrufe sind gepatcht.

    ``commit`` muss vorhanden sein, weil der Endpoint nach dem Insert
    explizit committet.
    """

    committed: bool = False

    async def commit(self) -> None:
        self.committed = True


def _make_operation(
    *,
    op_id: uuid.UUID | None = None,
    status: str = OPERATION_STATUS_ACTIVE,
    access_code_active: bool = False,
    access_code_hash: str | None = None,
    city_label: str = "Bremen Innenstadt",
) -> Operation:
    op = Operation(
        id=op_id or uuid.uuid4(),
        status=status,
        city_label=city_label,
        url_token="placeholder",
        access_code_hash=access_code_hash,
        access_code_active=access_code_active,
    )
    now = datetime.now(UTC)
    op.created_at = now
    op.updated_at = now
    return op


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
    """Factory: gibt einen ``TestClient`` mit gepatchten Repositories zurück.

    ``operation_by_id`` ist eine ``dict[UUID, Operation | None]``-Map; bei
    ``None`` antwortet ``find_operation_by_id`` mit ``None``.
    """

    def _make(operation_by_id: dict[uuid.UUID, Operation | None]) -> TestClient:
        from eb_digital.app import create_app

        app = create_app()
        stub_db = _StubDbSession()

        async def _override_valkey() -> fakeredis.aioredis.FakeRedis:
            return fake_valkey

        async def _override_db() -> _StubDbSession:
            return stub_db

        async def _override_find_op(_session: Any, op_id: uuid.UUID) -> Operation | None:
            return operation_by_id.get(op_id)

        async def _override_create_session(
            _session: Any, *, operation_id: uuid.UUID
        ) -> AnonymousSession:
            record = AnonymousSession(
                id=uuid.uuid4(),
                operation_id=operation_id,
            )
            now = datetime.now(UTC)
            record.created_at = now
            record.last_seen_at = now
            record.expires_at = now + timedelta(hours=24)
            return record

        app.dependency_overrides[get_valkey_client] = _override_valkey
        app.dependency_overrides[get_db_session] = _override_db
        monkeypatch.setattr(anon_api, "find_operation_by_id", _override_find_op)
        monkeypatch.setattr(anon_api, "create_anonymous_session", _override_create_session)

        return TestClient(app)

    return _make


def _token_for(operation_id: uuid.UUID) -> str:
    settings = get_settings()
    return generate_url_token(operation_id, settings.secret_key.get_secret_value())


# ─── /info ───────────────────────────────────────────────────────────────────


def test_info_returns_200_for_active_operation(make_client: Any) -> None:
    op = _make_operation(access_code_active=False)
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.get(f"/api/anon/{token}/info")
    assert response.status_code == 200
    body = response.json()
    assert body == {
        "area_label": "Bremen Innenstadt",
        "access_code_active": False,
        "status": OPERATION_STATUS_ACTIVE,
    }


def test_info_includes_access_code_active_flag(make_client: Any) -> None:
    op = _make_operation(access_code_active=True)
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.get(f"/api/anon/{token}/info")
    assert response.status_code == 200
    assert response.json()["access_code_active"] is True


def test_info_returns_404_for_forged_token(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.get("/api/anon/not-a-real-token/info")
    assert response.status_code == 404


def test_info_returns_404_for_missing_operation(make_client: Any) -> None:
    # Token signed, but operation row not in DB.
    token = _token_for(uuid.uuid4())
    with make_client({}) as client:
        response = client.get(f"/api/anon/{token}/info")
    assert response.status_code == 404


def test_info_returns_404_for_closed_operation(make_client: Any) -> None:
    op = _make_operation(status=OPERATION_STATUS_CLOSED)
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.get(f"/api/anon/{token}/info")
    assert response.status_code == 404


def test_info_returns_404_for_planned_operation(make_client: Any) -> None:
    """Planned = Vorbereitung; Einsatzkraft sieht sie noch nicht."""
    op = _make_operation(status=OPERATION_STATUS_PLANNED)
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.get(f"/api/anon/{token}/info")
    assert response.status_code == 404


# ─── /session — happy paths ──────────────────────────────────────────────────


def test_session_without_code_for_open_operation_returns_201(make_client: Any) -> None:
    op = _make_operation(access_code_active=False)
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.post(f"/api/anon/{token}/session", json={})
    assert response.status_code == 201
    body = response.json()
    assert "session_id" in body
    # Session-Cookie wurde gesetzt (gleicher Cookie-Name wie Login, weil
    # Starlette-SessionMiddleware nur ein Cookie pro App führt — der Inhalt
    # trägt den separaten ``anon``-Subkey).
    assert any(c.name == "eb_session" for c in client.cookies.jar)


def test_session_with_correct_code_returns_201(make_client: Any) -> None:
    code = "X7K3PQ"
    op = _make_operation(access_code_active=True, access_code_hash=hash_access_code(code))
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.post(f"/api/anon/{token}/session", json={"access_code": code})
    assert response.status_code == 201


# ─── /session — error paths ──────────────────────────────────────────────────


def test_session_with_wrong_code_returns_401(make_client: Any) -> None:
    op = _make_operation(
        access_code_active=True,
        access_code_hash=hash_access_code("X7K3PQ"),
    )
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.post(f"/api/anon/{token}/session", json={"access_code": "Z9X8Y7"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid access code."}


def test_session_without_code_on_active_code_operation_returns_401(make_client: Any) -> None:
    op = _make_operation(
        access_code_active=True,
        access_code_hash=hash_access_code("X7K3PQ"),
    )
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.post(f"/api/anon/{token}/session", json={})
    assert response.status_code == 401


def test_session_with_invalid_pattern_code_returns_422(make_client: Any) -> None:
    """Pydantic-Pattern-Verstoß: Code mit verbotenen Zeichen → 422."""
    op = _make_operation(access_code_active=True, access_code_hash=hash_access_code("X7K3PQ"))
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        # Enthält ``I`` (verboten).
        response = client.post(f"/api/anon/{token}/session", json={"access_code": "X7IIIQ"})
    assert response.status_code == 422


def test_session_for_forged_token_returns_410(make_client: Any) -> None:
    with make_client({}) as client:
        response = client.post("/api/anon/not-a-real-token/session", json={})
    assert response.status_code == 410


def test_session_for_closed_operation_returns_410(make_client: Any) -> None:
    op = _make_operation(status=OPERATION_STATUS_CLOSED)
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.post(f"/api/anon/{token}/session", json={})
    assert response.status_code == 410


def test_session_for_planned_operation_returns_410(make_client: Any) -> None:
    op = _make_operation(status=OPERATION_STATUS_PLANNED)
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.post(f"/api/anon/{token}/session", json={})
    assert response.status_code == 410


# ─── Rate-Limit ──────────────────────────────────────────────────────────────


def test_six_failed_attempts_on_same_url_trip_url_counter(make_client: Any) -> None:
    op = _make_operation(access_code_active=True, access_code_hash=hash_access_code("X7K3PQ"))
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        for _ in range(LOGIN_LIMIT):
            response = client.post(f"/api/anon/{token}/session", json={"access_code": "Z9X8Y7"})
            assert response.status_code == 401

        # 6. Versuch — URL-Counter über 5.
        response = client.post(f"/api/anon/{token}/session", json={"access_code": "Z9X8Y7"})
        assert response.status_code == 429
        assert "Retry-After" in response.headers
        assert int(response.headers["Retry-After"]) <= LOGIN_WINDOW_SECONDS


def test_brute_force_sweep_across_urls_trips_ip_counter(make_client: Any) -> None:
    """5 verschiedene URLs (alle verfälscht/unbekannt) von derselben IP →
    IP-Counter zieht beim 6. Versuch."""
    with make_client({}) as client:
        for n in range(LOGIN_LIMIT):
            response = client.post(f"/api/anon/forged-token-{n}/session", json={})
            assert response.status_code == 410  # token signature fails before rate-limit return

        # 6. Versuch mit weiterem verfälschten Token: IP-Counter über 5 → 429.
        response = client.post("/api/anon/forged-token-fresh/session", json={})
        assert response.status_code == 429


def test_successful_session_resets_url_counter(
    make_client: Any,
    fake_valkey: fakeredis.aioredis.FakeRedis,
) -> None:
    code = "X7K3PQ"
    op = _make_operation(access_code_active=True, access_code_hash=hash_access_code(code))
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        for _ in range(4):
            client.post(f"/api/anon/{token}/session", json={"access_code": "Z9X8Y7"})
        success = client.post(f"/api/anon/{token}/session", json={"access_code": code})
        assert success.status_code == 201

    # URL-Counter wurde gelöscht; IP-Counter steht weiterhin bei 5.
    import asyncio

    digest = hashlib.sha256(token.encode("utf-8")).hexdigest()
    url_key = f"auth_anonymous:ratelimit:session:url:{digest}"
    ip_key = "auth_anonymous:ratelimit:session:ip:testclient"

    async def _fetch() -> tuple[Any, Any]:
        return await fake_valkey.get(url_key), await fake_valkey.get(ip_key)

    url_count, ip_count = asyncio.get_event_loop().run_until_complete(_fetch())
    assert url_count is None  # URL-Counter weggeräumt.
    assert ip_count is not None
    assert int(ip_count) == LOGIN_LIMIT


# ─── Klartext-Code-Leak-Defensive ────────────────────────────────────────────


def test_wrong_code_response_body_does_not_contain_code(make_client: Any) -> None:
    """Reine Defensive: 401-Body enthält keinen Code-Klartext."""
    submitted = "Z9X8Y7"
    op = _make_operation(access_code_active=True, access_code_hash=hash_access_code("X7K3PQ"))
    token = _token_for(op.id)
    with make_client({op.id: op}) as client:
        response = client.post(f"/api/anon/{token}/session", json={"access_code": submitted})
    assert response.status_code == 401
    assert submitted not in response.text


# ─── Key-Helper-Tests ────────────────────────────────────────────────────────


def test_session_url_key_uses_sha256_hash() -> None:
    token = "some-arbitrary-token"
    key = anon_api._session_url_key(token)
    assert key.startswith("auth_anonymous:ratelimit:session:url:")
    assert hashlib.sha256(token.encode()).hexdigest() in key
    # Klartext-Token darf nicht im Key auftauchen.
    assert token not in key


def test_session_ip_key_format() -> None:
    assert anon_api._session_ip_key("198.51.100.7") == (
        "auth_anonymous:ratelimit:session:ip:198.51.100.7"
    )
