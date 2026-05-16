"""FastAPI-Router für Login / Logout / Me / Register-Tenant / Reset-Password.

Endpunkte unter ``/api/auth``:

Login-Pfad (siehe 2.2):
  1. Rate-Limit-Check (IP+User AND, ADR-013) **vor** DB-Lookup.
  2. ``find_by_username`` über die drei Auth-Tabellen.
  3. Hash-Verifikation: ``verify_password`` bei Treffer, ``verify_dummy`` ohne
     Treffer (Timing-Attack-Schutz).
  4. Tenant-Status-Check für Dispatcher/Carer: nur ``status='active'`` erlaubt
     Login (ergänzt in 2.4).
  5. Bei Erfolg: User-Counter-Reset, Session setzen, 200 mit Subject-Info.
  6. Bei Fehlschlag: 401 mit konstanter Antwortzeit.
  7. Bei Rate-Limit-Überschreitung: 429 mit ``Retry-After``-Header.

Inaktive User (``is_active=False``) und Dispatcher/Carer in nicht-aktiven
Mandanten werden wie wrong-password behandelt (401), um Info-Leak zu
vermeiden.

Register-Tenant-Pfad (2.4): Public, 3/24h/IP-Rate-Limit, Slug-Validierung,
Antrag mit ``status='applied'``.

Reset-Password-Pfad (2.4): Public, 5/15min/IP-Rate-Limit, Token-Validierung
über ``auth.reset_token``, Setzen des Hashs + Aktivierung über
``tenants.use_cases.complete_password_reset``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, Final

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel, Field
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from eb_digital.auth.hashing import PASSWORD_MIN_LENGTH, verify_dummy, verify_password
from eb_digital.auth.rate_limit import check_login, incr_and_check, reset_user
from eb_digital.auth.repositories import (
    KIND_CARER,
    KIND_DISPATCHER,
    AuthSubject,
    find_by_username,
)
from eb_digital.auth.sessions import (
    SessionUser,
    clear_session,
    get_current_session_user,
    set_session,
)
from eb_digital.settings import Settings, get_settings
from eb_digital.tenants import repositories as tenants_repo
from eb_digital.tenants import use_cases as tenants_use_cases
from eb_digital.tenants.models import TENANT_STATUS_ACTIVE
from eb_digital.tenants.slug import SlugValidationError, validate_slug

UNKNOWN_IP: Final[str] = "unknown"

# Rate-Limit-Konfigurationen für die in 2.4 ergänzten Public-Endpunkte.
# Alle Schlüsselräume folgen der Convention ``auth:ratelimit:<endpoint>:<dim>:<key>``
# (analog zu Login aus 2.2 und Anon-Session aus 2.3).
REGISTER_TENANT_LIMIT: Final[int] = 3
REGISTER_TENANT_WINDOW_SECONDS: Final[int] = 24 * 60 * 60  # 24 h

RESET_PASSWORD_LIMIT: Final[int] = 5
RESET_PASSWORD_WINDOW_SECONDS: Final[int] = 15 * 60  # 15 min


def _register_tenant_ip_key(ip: str) -> str:
    return f"auth:ratelimit:register_tenant:ip:{ip}"


def _reset_password_ip_key(ip: str) -> str:
    return f"auth:ratelimit:reset_password:ip:{ip}"


def extract_client_ip(request: Request) -> str:
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


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    # FastAPI yield-Dependency (ADR-015, Regel-018): das `yield` hält den
    # Context-Manager über die Endpoint-Ausführung offen. `return session`
    # innerhalb des `async with` würde `__aexit__` vor Endpoint-Nutzung
    # auslösen und die Session bereits geschlossen ausliefern.
    factory = getattr(request.app.state, "db_session_factory", None)
    if factory is None:
        msg = "DB-Session-Factory wurde nicht im app.state initialisiert."
        raise RuntimeError(msg)
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


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
    ip = extract_client_ip(request)
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

    if not await _tenant_login_allowed(db, subject):
        # Tenant nicht aktiv (z. B. ``applied`` vor Approve oder
        # ``deactivated`` nach DSGVO-Stop) — identische Antwort wie
        # wrong-password, kein Info-Leak über Tenant-Status.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    # Erfolgreicher Login: User-Counter-Reset (IP-Counter bleibt — siehe ADR-013).
    await reset_user(valkey, payload.username)
    user = set_session(request, subject)
    return SessionUserResponse.from_user(user)


async def _tenant_login_allowed(
    db: AsyncSession,
    subject: AuthSubject,
) -> bool:
    """Tenant-Status-Check für Dispatcher/Carer (2.4).

    PlatformAdmin hat keine Tenant-Bindung und ist immer erlaubt.
    Dispatcher/Carer müssen zu einem Tenant im Status ``active`` gehören —
    Anträge im Status ``applied`` (Self-Service-Antrag, noch nicht
    freigeschaltet) und ``deactivated`` (DSGVO-Art.-17-Stop) blocken Login.
    """
    if subject.kind not in (KIND_DISPATCHER, KIND_CARER):
        return True
    if subject.tenant_id is None:
        # Datenintegritäts-Bug: Dispatcher/Carer ohne Tenant-FK. Defensiv
        # blocken statt durchlassen.
        return False
    tenant = await tenants_repo.find_tenant_by_id(db, subject.tenant_id)
    if tenant is None:
        return False
    return tenant.status == TENANT_STATUS_ACTIVE


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


# ─── 2.4: Self-Service-Antrag und Reset-Password ─────────────────────────────


class RegisterTenantRequest(BaseModel):
    name: str = Field(min_length=3, max_length=120)
    slug: str = Field(min_length=3, max_length=64)


class RegisterTenantResponse(BaseModel):
    tenant_id: str
    status: str


@router.post(
    "/register-tenant",
    response_model=RegisterTenantResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_409_CONFLICT: {"description": "Slug already taken."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Invalid input."},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded."},
    },
)
async def register_tenant(
    payload: RegisterTenantRequest,
    request: Request,
    valkey: Annotated[Redis, Depends(get_valkey_client)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> RegisterTenantResponse:
    """Public Self-Service-Antrag.

    Rate-Limit 3/24h pro IP. Slug-Validierung greift vor Repository-Aufruf;
    Slug-Kollision wirft 409.
    """
    ip = extract_client_ip(request)
    rate_check = await incr_and_check(
        valkey,
        _register_tenant_ip_key(ip),
        limit=REGISTER_TENANT_LIMIT,
        window_seconds=REGISTER_TENANT_WINDOW_SECONDS,
    )
    if not rate_check.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many tenant applications. Try again later.",
            headers={"Retry-After": str(rate_check.retry_after_seconds)},
        )

    # Vor-Validierung im Endpoint: liefert spezifisches 422 statt 409 bei
    # Format-Verstoß. Repository-Aufruf wirft danach nur noch
    # ``SlugAlreadyTakenError`` für DB-Unique-Verstoß.
    try:
        validate_slug(payload.slug)
    except SlugValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    try:
        result = await tenants_use_cases.apply_for_tenant(
            db,
            name=payload.name,
            slug=payload.slug,
        )
    except tenants_repo.SlugAlreadyTakenError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Slug already taken.",
        ) from exc
    except SlugValidationError as exc:
        # Falls Use-Case zusätzlich validiert (defensiv).
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    await db.commit()
    return RegisterTenantResponse(
        tenant_id=str(result.tenant.id),
        status=result.tenant.status,
    )


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=1, max_length=2048)
    new_password: str = Field(min_length=PASSWORD_MIN_LENGTH)


@router.post(
    "/reset-password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_410_GONE: {"description": "Token invalid, expired, or already used."},
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Password too short."},
        status.HTTP_429_TOO_MANY_REQUESTS: {"description": "Rate limit exceeded."},
    },
)
async def reset_password(
    payload: ResetPasswordRequest,
    request: Request,
    valkey: Annotated[Redis, Depends(get_valkey_client)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> Response:
    """Public Password-Reset via signiertem Token.

    Rate-Limit 5/15min pro IP (analog Login). Mindest-Passwort-Länge per
    Pydantic-Validator (Field min_length). Replay-Schutz via
    ``set_password_and_activate`` — schlägt fehl, wenn der User schon
    aktiv ist (Token-Replay).
    """
    ip = extract_client_ip(request)
    rate_check = await incr_and_check(
        valkey,
        _reset_password_ip_key(ip),
        limit=RESET_PASSWORD_LIMIT,
        window_seconds=RESET_PASSWORD_WINDOW_SECONDS,
    )
    if not rate_check.allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many reset attempts. Try again later.",
            headers={"Retry-After": str(rate_check.retry_after_seconds)},
        )

    try:
        await tenants_use_cases.complete_password_reset(
            db,
            token=payload.token,
            new_password=payload.new_password,
            secret=settings.secret_key.get_secret_value(),
        )
    except tenants_use_cases.PasswordTooShortError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Password must be at least {PASSWORD_MIN_LENGTH} characters.",
        ) from exc
    except (
        tenants_use_cases.InvalidResetTokenError,
        tenants_use_cases.UserAlreadyActiveError,
    ) as exc:
        # Identische Antwort für „Token ungültig/abgelaufen" und „bereits
        # eingelöst" — kein Info-Leak über Token-Replay-Status.
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Reset token invalid, expired, or already used.",
        ) from exc
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


__all__ = [
    "LoginRequest",
    "RegisterTenantRequest",
    "RegisterTenantResponse",
    "ResetPasswordRequest",
    "SessionUserResponse",
    "extract_client_ip",
    "get_db_session",
    "get_valkey_client",
    "router",
]
