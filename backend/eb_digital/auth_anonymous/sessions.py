"""Cookie-Session-Helper für anonyme Einsatzkraft-Sessions.

Eigener Session-Key ``anon`` in der Starlette-Session-Payload, damit eine
laufende Anonymous-Session koexistieren kann mit einer Login-Session
(theoretisch: Disponent öffnet im selben Browser die anonyme PWA — Phase 1
nicht produktiver Use-Case, aber bewusste Strukturierung gegen Kollisionen).

**Payload-Schema** (datenarm, kein PII):
  • ``session_id``: UUID der ``anonymous_session``-Zeile (String).
  • ``operation_id``: UUID der zugehörigen Operation (String).
  • ``expires_at``: ISO-8601 UTC-Datetime (24-h-Hard-Cap aus dem DB-Record).
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Final

from starlette.requests import HTTPConnection, Request

from eb_digital.auth_anonymous.models import AnonymousSession

ANON_SESSION_KEY: Final[str] = "anon"


@dataclass(frozen=True, slots=True)
class AnonymousSessionUser:
    """Anonyme Session aus Cookie-Sicht (kein DB-Roundtrip)."""

    session_id: uuid.UUID
    operation_id: uuid.UUID
    expires_at: datetime


def set_anonymous_session(request: Request, record: AnonymousSession) -> AnonymousSessionUser:
    """Setzt die Session-Payload für ``record`` und liefert sie als Container.

    Beachte: die DB-Zeile ist die maßgebliche Quelle (Cleanup-Job in Phase 4
    löscht abgelaufene Records). Die Cookie-Payload ist eine Komfort-Kopie
    der wichtigsten Felder.
    """
    payload: dict[str, Any] = {
        "session_id": str(record.id),
        "operation_id": str(record.operation_id),
        "expires_at": record.expires_at.isoformat(),
    }
    request.session[ANON_SESSION_KEY] = payload
    return AnonymousSessionUser(
        session_id=record.id,
        operation_id=record.operation_id,
        expires_at=record.expires_at,
    )


def get_current_anonymous_session(request: HTTPConnection) -> AnonymousSessionUser | None:
    """Liefert die aktive anonyme Session aus dem Cookie, oder ``None``.

    ``None`` bei: fehlender Payload, Schema-Verstoß, abgelaufenem
    ``expires_at`` (zusätzlich zum DB-seitigen Hard-Cap aus Defense-in-
    depth). Bei Ablauf wird die Payload aus der Session entfernt.
    """
    payload = request.session.get(ANON_SESSION_KEY)
    if not isinstance(payload, dict):
        return None
    try:
        session_id = uuid.UUID(payload["session_id"])
        operation_id = uuid.UUID(payload["operation_id"])
        expires_at = datetime.fromisoformat(payload["expires_at"])
    except (KeyError, ValueError, TypeError):
        clear_anonymous_session(request)
        return None

    if expires_at <= datetime.now(UTC):
        clear_anonymous_session(request)
        return None

    return AnonymousSessionUser(
        session_id=session_id,
        operation_id=operation_id,
        expires_at=expires_at,
    )


def clear_anonymous_session(request: HTTPConnection) -> None:
    """Entfernt die Anon-Session-Payload (kein Logout-Endpoint in 2.3, aber
    für Cleanup-Pfad in den Repository-Helpern nutzbar)."""
    request.session.pop(ANON_SESSION_KEY, None)


__all__ = [
    "ANON_SESSION_KEY",
    "AnonymousSessionUser",
    "clear_anonymous_session",
    "get_current_anonymous_session",
    "set_anonymous_session",
]
