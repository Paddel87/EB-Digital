"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from starlette.middleware.sessions import SessionMiddleware

from eb_digital import __version__
from eb_digital.auth import api as auth_api
from eb_digital.auth_anonymous import api as auth_anonymous_api
from eb_digital.cache import create_valkey_client
from eb_digital.db import create_db_engine, create_session_factory
from eb_digital.logging import configure_logging, get_logger
from eb_digital.settings import get_settings
from eb_digital.tenants import api as tenants_api


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger("eb_digital.app")
    logger.info(
        "application_startup",
        extra={"environment": settings.environment, "version": __version__},
    )

    # Datenbank-Engine + Session-Factory für FastAPI-Dependencies.
    engine = create_db_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory

    # Valkey-Connection-Pool für Rate-Limit-Counter (ADR-013) und ab Phase 4
    # WebSocket-Pub/Sub.
    valkey = create_valkey_client(settings.valkey_url)
    app.state.valkey = valkey

    try:
        yield
    finally:
        await valkey.aclose()
        await engine.dispose()
        logger.info("application_shutdown")


def _health_payload() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="EB Digital", version=__version__, lifespan=lifespan)

    # SessionMiddleware (signiert, nicht verschlüsselt) — Cookie-Flags aus
    # ``project-context.md`` Abschnitt 6 Sicherheit.
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.secret_key.get_secret_value(),
        session_cookie=settings.session_cookie_name,
        same_site="strict",
        https_only=settings.environment != "dev",
    )

    api_router = APIRouter(prefix="/api")

    @api_router.get("/health")
    async def api_health() -> dict[str, str]:
        return _health_payload()

    api_router.include_router(auth_api.router)
    api_router.include_router(auth_anonymous_api.router)
    api_router.include_router(tenants_api.router)

    app.include_router(api_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return _health_payload()

    return app
