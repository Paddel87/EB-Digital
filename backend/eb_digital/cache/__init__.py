"""Valkey-Connection-Pool und Health-Helper.

Erste produktive Valkey-Nutzung des Backends (ab Schritt 2.2 für Auth-Rate-
Limit-Counter, ab Phase 4 zusätzlich für WebSocket-Pub/Sub). Wir nutzen
``redis-py`` als Client; die Marken-Distanzierung in ADR-002 betrifft den
Server, nicht den MIT-lizenzierten Client (siehe Sub-Wahl Schritt 2.2).

Settings nutzt das URL-Schema ``valkey://`` für Marken-Konsistenz mit
ADR-002. ``redis.asyncio.Redis.from_url`` versteht aber nur
``redis://`` / ``rediss://``; die Adaption erfolgt analog zur Postgres-URL-
Adaption in ``eb_digital.jobs._to_psycopg_conninfo``.
"""

from __future__ import annotations

from redis.asyncio import Redis


def _adapt_valkey_url(url: str) -> str:
    """Wandle ``valkey://``- und ``valkeys://``-URLs in das von ``redis-py``
    erwartete ``redis://``- bzw. ``rediss://``-Schema um."""
    if url.startswith("valkeys://"):
        return "rediss://" + url.removeprefix("valkeys://")
    if url.startswith("valkey://"):
        return "redis://" + url.removeprefix("valkey://")
    return url


def create_valkey_client(url: str) -> Redis:
    """Erzeuge einen ``redis-py`` Async-Client gegen ``url``.

    Der Client verwaltet einen internen Connection-Pool. ``decode_responses``
    bleibt ``False`` (Default) — wir arbeiten konsistent mit Bytes auf der
    Wire-Schnittstelle und entscheiden pro Aufruf, was zu dekodieren ist.
    """
    return Redis.from_url(_adapt_valkey_url(url))


async def ping_valkey(client: Redis) -> bool:
    """``True``, wenn der Server auf ``PING`` mit ``PONG`` antwortet.

    Wirft keine Exception, sondern liefert ``False`` bei Connection-Fehlern —
    bestimmt für Health-Endpunkte, die einen Boolean-Status erwarten.
    """
    try:
        # ``Redis.ping()`` is typed as ``Awaitable[bool] | bool`` in redis-py 7
        # because the same method exists in the sync facade; in the asyncio
        # facade it is always awaitable.
        result: object = await client.ping()  # type: ignore[misc]
    except Exception:
        return False
    return bool(result)


__all__ = [
    "create_valkey_client",
    "ping_valkey",
]
