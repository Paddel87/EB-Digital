"""FastAPI-Router für Login / Logout / Me unter ``/api/auth``.

Login-Pfad:
  1. Rate-Limit-Check (IP+User AND, ADR-013) **vor** DB-Lookup.
  2. ``find_by_username`` über die drei Auth-Tabellen.
  3. Hash-Verifikation: ``verify_password`` bei Treffer, ``verify_dummy`` ohne
     Treffer (Timing-Attack-Schutz).
  4. Bei Erfolg: User-Counter-Reset, Session setzen, 200 mit Subject-Info.
  5. Bei Fehlschlag: 401 mit konstanter Antwortzeit.
  6. Bei Rate-Limit-Überschreitung: 429 mit ``Retry-After``-Header.

Inaktive User (``is_active=False``) werden behandelt wie wrong-password (401),
um Info-Leak über aktive vs. inaktive Accounts zu vermeiden.
"""

from __future__ import annotations

from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.hashing import PASSWORD_MIN_LENGTH, verify_dummy, verify_password
from eb_digital.auth.rate_limit import check_login, reset_user
from eb_digital.auth.repositories import find_by_username
from eb_digital.auth.sessions import (
    SessionUser,
    clear_session,
    get_current_session_user,
    set_session,
)

UNKNOWN_IP: Final[str] = "unknown"


def _extract_client_ip(request: Request) -> str:
    """Liefert die Client-IP unter Berücksichtigung des Caddy-Reverse-Proxy.

    ``X-Forwarded-For`` wird vom unmittelbaren Reverse-Proxy gesetzt; wir
    nehmen den **ersten** Eintrag (die ursprüngliche Client-IP). In Dev ohne
    Proxy fällt der Pfad auf ``request.client.host`` zurück.
    """
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client is not None:
        return request.client.host
    return UNKNOWN_IP


# ─── FastAPI-Dependencies (read from app.state) ───────────────────────────────


async def get_valkey_client(request: Request) -> Redis:
    client = getattr(request.app.state, "valkey", None)
    if client is None:
        msg = "Valkey-Client wurde nicht im app.state initialisiert."
        raise RuntimeError(msg)
    return client  # type: ignore[no-any-return]


async def get_db_session(request: Request) -> AsyncSession:
    factory = getattr(request.app.state, "db_session_factory", None)
    if factory is None:
        msg = "DB-Session-Factory wurde nicht im app.state initialisiert."
        raise RuntimeError(msg)
    async with factory() as session:
        return session  # type: ignore[no-any-return]


# ─── Pydantic-Modelle ────────────────────────────────────────────────────────


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=PASSWORD_MIN_LENGTH)


class SessionUserResponse(BaseModel):
    kind: str
    id: str
    username: str
    tenant_id: str | None
    expires_at: str

    @classmethod
    def from_user(cls, user: SessionUser) -> SessionUserResponse:
        return cls(
            kind=user.kind,
            id=str(user.id),
            username=user.username,
            tenant_id=str(user.tenant_id) if user.tenant_id else None,
            expires_at=user.expires_at.isoformat(),
        )


# ─── Router ──────────────────────────────────────────────────────────────────


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/login",
    response_model=SessionUserResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid credentials."},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded."},
    },
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    valkey: Annotated[Redis, Depends(get_valkey_client)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> SessionUserResponse:
    ip = _extract_client_ip(request)
    rate_check = await check_login(valkey, ip=ip, username=payload.username)
    if not rate_check.allowed:
        response.headers["Retry-After"] = str(rate_check.retry_after_seconds)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
            headers={"Retry-After": str(rate_check.retry_after_seconds)},
        )

    subject = await find_by_username(db, payload.username)
    if subject is None:
        # Timing-Attack-Schutz: gleicher CPU-Aufwand wie echte Verifikation.
        verify_dummy(payload.password)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    if not verify_password(subject.password_hash, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    if not subject.is_active:
        # Identische Antwort wie wrong-password: kein Info-Leak.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    # Erfolgreicher Login: User-Counter-Reset (IP-Counter bleibt — siehe ADR-013).
    await reset_user(valkey, payload.username)
    user = set_session(request, subject)
    return SessionUserResponse.from_user(user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request) -> Response:
    clear_session(request)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me",
    response_model=SessionUserResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "No active session."}},
)
async def me(request: Request) -> SessionUserResponse:
    user = get_current_session_user(request)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return SessionUserResponse.from_user(user)


__all__ = [
    "LoginRequest",
    "SessionUserResponse",
    "get_db_session",
    "get_valkey_client",
    "router",
]
