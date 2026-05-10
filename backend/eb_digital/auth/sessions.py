"""Session-Helper rund um Starlette ``SessionMiddleware``.

Das Session-Cookie ist signiert (HMAC), nicht verschlüsselt — die Payload ist
deshalb bewusst datenarm: nur ``kind``, ``id``, ``tenant_id`` und ein
absolutes Ablaufdatum. Sensible Felder (Hash, Email) gehören niemals in die
Session-Payload.

**Timeouts** aus ``project-context.md`` Abschnitt 6 Sicherheit:
  • PlatformAdmin: 8 h
  • Dispatcher / Carer: 24 h
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any, Final

from starlette.requests import Request

from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    KIND_PLATFORM_ADMIN,
    AuthSubject,
    SubjectKind,
)

SESSION_KEY: Final[str] = "auth"

PLATFORM_ADMIN_TIMEOUT: Final[timedelta] = timedelta(hours=8)
DISPATCHER_TIMEOUT: Final[timedelta] = timedelta(hours=24)
CARER_TIMEOUT: Final[timedelta] = timedelta(hours=24)


@dataclass(frozen=True, slots=True)
class SessionUser:
    """Authentifiziertes Subjekt in der laufenden Request-Session."""

    kind: SubjectKind
    id: uuid.UUID
    username: str
    tenant_id: uuid.UUID | None
    expires_at: datetime


def _timeout_for(kind: SubjectKind) -> timedelta:
    if kind == KIND_PLATFORM_ADMIN:
        return PLATFORM_ADMIN_TIMEOUT
    if kind == KIND_DISPATCHER:
        return DISPATCHER_TIMEOUT
    if kind == KIND_CARER:
        return CARER_TIMEOUT
    msg = f"Unknown subject kind: {kind!r}"
    raise ValueError(msg)


def set_session(request: Request, subject: AuthSubject) -> SessionUser:
    """Setzt die Session-Payload für ``subject`` und liefert sie als ``SessionUser``."""
    expires_at = datetime.now(UTC) + _timeout_for(subject.kind)
    payload: dict[str, Any] = {
        "kind": subject.kind,
        "id": str(subject.id),
        "username": subject.username,
        "tenant_id": str(subject.tenant_id) if subject.tenant_id is not None else None,
        "expires_at": expires_at.isoformat(),
    }
    request.session[SESSION_KEY] = payload
    return SessionUser(
        kind=subject.kind,
        id=subject.id,
        username=subject.username,
        tenant_id=subject.tenant_id,
        expires_at=expires_at,
    )


def get_current_session_user(request: Request) -> SessionUser | None:
    """Liefert den aktuellen User oder ``None`` (Session fehlt / ungültig / abgelaufen).

    Bei abgelaufener Session wird die Payload sofort entfernt (cleanup beim Read).
    """
    payload = request.session.get(SESSION_KEY)
    if not isinstance(payload, dict):
        return None
    try:
        kind = payload["kind"]
        if kind not in (KIND_PLATFORM_ADMIN, KIND_DISPATCHER, KIND_CARER):
            clear_session(request)
            return None
        subject_id = uuid.UUID(payload["id"])
        username = str(payload["username"])
        tenant_raw = payload.get("tenant_id")
        tenant_id = uuid.UUID(tenant_raw) if tenant_raw else None
        expires_at = datetime.fromisoformat(payload["expires_at"])
    except (KeyError, ValueError, TypeError):
        clear_session(request)
        return None

    if expires_at <= datetime.now(UTC):
        clear_session(request)
        return None

    return SessionUser(
        kind=kind,
        id=subject_id,
        username=username,
        tenant_id=tenant_id,
        expires_at=expires_at,
    )


def clear_session(request: Request) -> None:
    """Entfernt die Session-Payload (Logout)."""
    request.session.pop(SESSION_KEY, None)


__all__ = [
    "CARER_TIMEOUT",
    "DISPATCHER_TIMEOUT",
    "PLATFORM_ADMIN_TIMEOUT",
    "SESSION_KEY",
    "SessionUser",
    "clear_session",
    "get_current_session_user",
    "set_session",
]
