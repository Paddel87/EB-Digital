"""FastAPI-Router für die S2-Sub-Surface ``/api/anon`` (Schritt 2.3).

Zwei Endpunkte:
  • ``GET  /api/anon/{url_token}/info``    — Operation-Metadaten, keine Auth.
  • ``POST /api/anon/{url_token}/session`` — anonyme Session anlegen.

Rate-Limit (5/15 min) liegt auf zwei Keys:
  • ``auth_anonymous:ratelimit:session:ip:<ip>``
  • ``auth_anonymous:ratelimit:session:url:<sha256(url_token)>``

Beide werden AND-verknüpft; nur erfolgreiche Session-Anlagen löschen den
URL-Counter (IP-Counter bleibt — Disziplin aus 2.2). Der URL-Counter wird
über den SHA-256-Hash des Tokens geführt, damit der Klartext-Token nicht in
Valkey-Keys auftaucht.
"""

from __future__ import annotations

import hashlib
from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response, status
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.api import extract_client_ip, get_db_session, get_valkey_client
from eb_digital.auth.rate_limit import (
    LOGIN_LIMIT,
    LOGIN_WINDOW_SECONDS,
    incr_and_check,
    reset,
)
from eb_digital.auth_anonymous.access_code import (
    ACCESS_CODE_PATTERN,
    verify_access_code,
    verify_dummy_access_code,
)
from eb_digital.auth_anonymous.repositories import (
    create_anonymous_session,
    find_operation_by_id,
)
from eb_digital.auth_anonymous.sessions import set_anonymous_session
from eb_digital.auth_anonymous.tokens import verify_url_token
from eb_digital.operations.models import OPERATION_STATUS_ACTIVE, OPERATION_STATUS_CLOSED
from eb_digital.settings import get_settings

# Operation-Status-Verhalten:
#   • ``active``  → /info 200, /session 201 möglich.
#   • ``planned`` → 404 in /info (Disponenten-Vorbereitung, Einsatzkraft sieht
#                    nichts), 410 in /session (Operation noch nicht offen).
#   • ``closed``  → 404 in /info, 410 in /session.
# Begründung: Die Einsatzkraft-Sicht greift erst, wenn die Operation aktiv ist.

_RATELIMIT_KEY_PREFIX: Final[str] = "auth_anonymous:ratelimit:session"


def _session_ip_key(ip: str) -> str:
    return f"{_RATELIMIT_KEY_PREFIX}:ip:{ip}"


def _session_url_key(url_token: str) -> str:
    """Hashed Token-Key, damit der Klartext-Token nicht im Valkey-Key auftaucht."""
    digest = hashlib.sha256(url_token.encode("utf-8")).hexdigest()
    return f"{_RATELIMIT_KEY_PREFIX}:url:{digest}"


# ─── Pydantic-Modelle ────────────────────────────────────────────────────────


class OperationInfoResponse(BaseModel):
    """Bezieher-sichtbare Operation-Metadaten.

    Bewusst keine Anbieter-PII (kein Tenant-Slug, kein Mandantenname) — die
    anonyme Sicht ist mandantenneutral (`project-context.md` Glossar:
    Bezieherseite).
    """

    area_label: str
    access_code_active: bool
    status: str


class SessionRequest(BaseModel):
    """Body für ``POST /session``.

    ``access_code`` ist required, sobald die Operation ``access_code_active``
    ist; das wird in der Endpoint-Logik geprüft. Format wird per Pydantic-
    Pattern erzwungen, sobald ein Wert geliefert wird.
    """

    access_code: str | None = Field(
        default=None,
        pattern=ACCESS_CODE_PATTERN.pattern,
        description="Crockford-Base32 (6 Zeichen, ohne I/L/O/U).",
    )


class SessionResponse(BaseModel):
    """Antwort auf erfolgreichen ``POST /session``."""

    session_id: str


# ─── Router ──────────────────────────────────────────────────────────────────


router = APIRouter(prefix="/anon", tags=["auth_anonymous"])


@router.get(
    "/{url_token}/info",
    response_model=OperationInfoResponse,
    responses={status.HTTP_404_NOT_FOUND: {"description": "Operation nicht aktiv."}},
)
async def get_info(
    url_token: Annotated[str, Path(min_length=1)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> OperationInfoResponse:
    settings = get_settings()
    operation_id = verify_url_token(url_token, settings.secret_key.get_secret_value())
    if operation_id is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation nicht aktiv.")

    operation = await find_operation_by_id(db, operation_id)
    if operation is None or operation.status != OPERATION_STATUS_ACTIVE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operation nicht aktiv.")

    return OperationInfoResponse(
        area_label=operation.city_label,
        access_code_active=operation.access_code_active,
        status=operation.status,
    )


@router.post(
    "/{url_token}/session",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Falscher AccessCode."},
        status.HTTP_410_GONE: {"description": "Operation beendet oder Token ungültig."},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded."},
    },
)
async def create_session(
    payload: SessionRequest,
    url_token: Annotated[str, Path(min_length=1)],
    request: Request,
    response: Response,
    valkey: Annotated[Redis, Depends(get_valkey_client)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SessionResponse:
    # 1) Rate-Limit-Check vor jeder DB-/Crypto-Operation.
    ip = extract_client_ip(request)
    ip_key = _session_ip_key(ip)
    url_key = _session_url_key(url_token)
    ip_result = await incr_and_check(
        valkey, ip_key, limit=LOGIN_LIMIT, window_seconds=LOGIN_WINDOW_SECONDS
    )
    url_result = await incr_and_check(
        valkey, url_key, limit=LOGIN_LIMIT, window_seconds=LOGIN_WINDOW_SECONDS
    )
    if not (ip_result.allowed and url_result.allowed):
        retry_after = max(ip_result.retry_after_seconds, url_result.retry_after_seconds)
        response.headers["Retry-After"] = str(retry_after)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many session attempts. Try again later.",
            headers={"Retry-After": str(retry_after)},
        )

    # 2) Token-Signatur prüfen — gefälschte Tokens kommen nicht in die DB.
    settings = get_settings()
    secret = settings.secret_key.get_secret_value()
    operation_id = verify_url_token(url_token, secret)
    if operation_id is None:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Operation nicht erreichbar.")

    # 3) Operation laden und Status prüfen.
    operation = await find_operation_by_id(db, operation_id)
    if operation is None or operation.status == OPERATION_STATUS_CLOSED:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Operation nicht erreichbar.")
    if operation.status != OPERATION_STATUS_ACTIVE:
        # planned: Operation noch nicht für Einsatzkräfte offen.
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Operation nicht erreichbar.")

    # 4) AccessCode-Prüfung, falls aktiviert.
    if operation.access_code_active:
        if payload.access_code is None or operation.access_code_hash is None:
            # Body-Code fehlt oder Operation hat keinen Hash (Inkonsistenz):
            # verify_dummy_access_code-Pfad zwecks Timing-Schutz, dann 401.
            verify_dummy_access_code(payload.access_code or "")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access code.",
            )
        if not verify_access_code(operation.access_code_hash, payload.access_code):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid access code.",
            )

    # 5) Erfolgreich: URL-Counter zurücksetzen, IP-Counter bleibt (Disziplin
    #    aus 2.2: schützt vor URL-Variation-Sweep über dieselbe IP).
    await reset(valkey, url_key)
    record = await create_anonymous_session(db, operation_id=operation.id)
    await db.commit()
    user = set_anonymous_session(request, record)
    return SessionResponse(session_id=str(user.session_id))


__all__ = [
    "OperationInfoResponse",
    "SessionRequest",
    "SessionResponse",
    "router",
]
