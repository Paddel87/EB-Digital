"""WebSocket-Hub: lokale Subscription-Registry + Valkey-Pub/Sub-Brücke.

Pro Backend-Worker läuft **ein** Listener-Task, der per
``PSUBSCRIBE operation.*`` alle Operations-Channels mitliest (eigene
Pub/Sub-Connection aus dem Pool, getrennt vom Command-Verkehr des Rate-Limit-
Clients) und eingehende Nachrichten an die lokal verbundenen WebSockets
fan-outet. Die Registry ``topic → {Connection}`` ist In-Memory und damit
worker-lokal; der Fan-out über mehrere Worker entsteht dadurch, dass jeder
Worker denselben Valkey abonniert (Detail-Plan 4.4-1A/7A).
"""

from __future__ import annotations

import asyncio
import contextlib
from typing import TYPE_CHECKING

from redis.asyncio import Redis

from eb_digital.logging import get_logger
from eb_digital.realtime import messages
from eb_digital.realtime.connection import Connection
from eb_digital.realtime.topics import TOPIC_PATTERN

if TYPE_CHECKING:
    from redis.asyncio.client import PubSub

logger = get_logger(__name__)


class WebSocketHub:
    """Worker-lokale Registry plus Valkey-Pub/Sub-Listener."""

    def __init__(self) -> None:
        self._by_topic: dict[str, set[Connection]] = {}
        self._pubsub: PubSub | None = None
        self._listener_task: asyncio.Task[None] | None = None

    # ─── Registry ────────────────────────────────────────────────────────

    def register(self, conn: Connection) -> None:
        logger.info(
            "realtime.connection.open",
            extra={"realtime_connection_id": str(conn.id), "realtime_kind": conn.kind},
        )

    def unregister(self, conn: Connection) -> None:
        for topic in list(conn.topics):
            self._remove_from_topic(conn, topic)
        conn.topics.clear()
        logger.info(
            "realtime.connection.close",
            extra={"realtime_connection_id": str(conn.id), "realtime_kind": conn.kind},
        )

    def subscribe(self, conn: Connection, topic: str) -> None:
        self._by_topic.setdefault(topic, set()).add(conn)
        conn.topics.add(topic)

    def unsubscribe(self, conn: Connection, topic: str) -> None:
        self._remove_from_topic(conn, topic)
        conn.topics.discard(topic)

    def _remove_from_topic(self, conn: Connection, topic: str) -> None:
        subscribers = self._by_topic.get(topic)
        if subscribers is None:
            return
        subscribers.discard(conn)
        if not subscribers:
            del self._by_topic[topic]

    def subscriber_count(self, topic: str) -> int:
        return len(self._by_topic.get(topic, ()))

    # ─── Fan-out ─────────────────────────────────────────────────────────

    def dispatch(self, channel: str, raw: bytes | str) -> int:
        """Verteile eine Wire-Nachricht an lokale Abonnenten von ``channel``.

        Liefert die Anzahl der Verbindungen, an die zugestellt wurde. Frames
        an überlaufende Slow-Client-Queues werden verworfen (siehe
        ``Connection.enqueue``).
        """
        subscribers = self._by_topic.get(channel)
        if not subscribers:
            return 0
        message = messages.parse_wire_message(raw)
        if message is None:
            return 0
        frame = messages.client_frame_from_wire(message)
        delivered = 0
        for conn in list(subscribers):
            if not conn.accepts(message):
                continue
            if conn.enqueue(frame):
                delivered += 1
            else:
                logger.warning(
                    "realtime.fanout.dropped",
                    extra={"realtime_connection_id": str(conn.id), "realtime_topic": channel},
                )
        return delivered

    # ─── Pub/Sub-Listener ────────────────────────────────────────────────

    async def start_listener(self, valkey: Redis) -> None:
        """Starte den ``PSUBSCRIBE operation.*``-Listener-Task.

        Ist Valkey beim App-Start nicht erreichbar (z. B. Unit-Tests, die die
        App-Lifespan ohne Valkey fahren), wird der Fehler geloggt und der
        Listener übersprungen — der App-Start bricht **nicht** ab. Pub/Sub ist
        dann inaktiv bis zum nächsten Start; Rate-Limit etc. bleiben unberührt
        (lazy-connectender Command-Client).
        """
        if self._listener_task is not None:
            return
        pubsub = valkey.pubsub()
        try:
            # Eager ``psubscribe`` macht die Subscription beim Rückgabezeitpunkt
            # garantiert aktiv (Readiness für direkt folgende PUBLISH-Aufrufe).
            await pubsub.psubscribe(TOPIC_PATTERN)
        except Exception:
            logger.exception("realtime.listener.subscribe_failed")
            with contextlib.suppress(Exception):
                await pubsub.aclose()  # type: ignore[no-untyped-call]
            return
        self._pubsub = pubsub
        self._listener_task = asyncio.create_task(self._listen(pubsub))
        logger.info("realtime.listener.started", extra={"realtime_pattern": TOPIC_PATTERN})

    async def _listen(self, pubsub: PubSub) -> None:
        try:
            async for message in pubsub.listen():
                if message.get("type") != "pmessage":
                    continue
                channel = message["channel"]
                if isinstance(channel, bytes):
                    channel = channel.decode()
                self.dispatch(channel, message["data"])
        except asyncio.CancelledError:
            raise
        except Exception:
            # Listener darf nie still sterben — Fehler wird geloggt, der Task
            # endet aber; ein Neustart erfolgt beim nächsten Lifespan-Zyklus.
            logger.exception("realtime.listener.error")

    async def stop_listener(self) -> None:
        """Beende den Listener-Task und schließe die Pub/Sub-Connection."""
        if self._listener_task is not None:
            self._listener_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._listener_task
            self._listener_task = None
        if self._pubsub is not None:
            # ``PubSub.aclose`` ist in redis-py 7 ungetypt (Stub-Lücke); der
            # Aufruf ist korrekt und schließt die dedizierte Pub/Sub-Connection.
            await self._pubsub.aclose()  # type: ignore[no-untyped-call]
            self._pubsub = None
        logger.info("realtime.listener.stopped")


__all__ = ["WebSocketHub"]
