"""FastAPI application factory."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI

from eb_digital import __version__
from eb_digital.logging import configure_logging, get_logger
from eb_digital.settings import get_settings


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger("eb_digital.app")
    logger.info(
        "application_startup",
        extra={"environment": settings.environment, "version": __version__},
    )
    try:
        yield
    finally:
        logger.info("application_shutdown")


def _health_payload() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


def create_app() -> FastAPI:
    app = FastAPI(title="EB Digital", version=__version__, lifespan=lifespan)
    api_router = APIRouter(prefix="/api")

    @api_router.get("/health")
    async def api_health() -> dict[str, str]:
        return _health_payload()

    app.include_router(api_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return _health_payload()

    return app
