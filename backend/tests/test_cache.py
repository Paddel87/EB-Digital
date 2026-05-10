"""Tests für ``backend/eb_digital/cache``."""

from __future__ import annotations

from typing import Any

import fakeredis.aioredis
import pytest
from redis.asyncio import Redis

from eb_digital.cache import _adapt_valkey_url, create_valkey_client, ping_valkey


class TestAdaptValkeyUrl:
    def test_valkey_scheme_is_replaced_with_redis(self) -> None:
        assert _adapt_valkey_url("valkey://cache:6379/0") == "redis://cache:6379/0"

    def test_valkeys_scheme_is_replaced_with_rediss(self) -> None:
        assert _adapt_valkey_url("valkeys://cache:6380/0") == "rediss://cache:6380/0"

    def test_redis_scheme_passes_through(self) -> None:
        assert _adapt_valkey_url("redis://localhost/1") == "redis://localhost/1"

    def test_rediss_scheme_passes_through(self) -> None:
        assert _adapt_valkey_url("rediss://localhost/1") == "rediss://localhost/1"

    def test_unknown_scheme_passes_through(self) -> None:
        # Defensive: unbekannte Schemata werden unverändert gereicht; ``redis-py``
        # entscheidet selbst, ob es damit umgehen kann (Klartext-Fehler).
        assert _adapt_valkey_url("unix:///tmp/valkey.sock") == "unix:///tmp/valkey.sock"


def test_create_valkey_client_returns_redis_instance() -> None:
    client = create_valkey_client("valkey://localhost:6379/0")
    assert isinstance(client, Redis)


@pytest.mark.asyncio
async def test_ping_valkey_returns_true_for_reachable_server() -> None:
    fake = fakeredis.aioredis.FakeRedis()
    try:
        assert await ping_valkey(fake) is True
    finally:
        await fake.aclose()


@pytest.mark.asyncio
async def test_ping_valkey_returns_false_when_client_raises() -> None:
    class _RaisingClient:
        async def ping(self) -> Any:
            raise ConnectionError("simulated")

    # ``ping_valkey`` darf jeden ``Exception``-Pfad fangen — duck-typing genügt,
    # weil der Helper nur ``await client.ping()`` aufruft.
    assert await ping_valkey(_RaisingClient()) is False  # type: ignore[arg-type]
