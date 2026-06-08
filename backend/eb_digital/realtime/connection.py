"""Pro-Verbindung-Zustand und Lebenszyklus-Schleifen des Realtime-Hubs.

Jede WebSocket-Verbindung hat genau **einen** Writer-Task, der die
Outbound-Queue leert — Starlette erlaubt kein nebenläufiges Senden auf
derselben WebSocket. Fan-out (Hub) und Heartbeat schreiben deshalb nur in
die Queue, niemals direkt auf die WebSocket.

Drei Schleifen je Verbindung (vom Endpoint orchestriert):

* ``writer_loop``    — Queue → WebSocket.
* ``heartbeat_loop`` — 30 s Ping, Drop bei Pong-Timeout (Detail-Plan 4.4-6A).
* ``receive_loop``   — WebSocket → Action-Handler (Subscribe etc.).
"""

from __future__ import annotations

import asyncio
import time
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any, Final

from starlette.websockets import WebSocket, WebSocketDisconnect

from eb_digital.logging import get_logger
from eb_digital.realtime import messages

logger = get_logger(__name__)

KIND_DISPATCHER: Final[str] = "dispatcher"
KIND_CARER: Final[str] = "carer"
KIND_ANON: Final[str] = "anon"

HEARTBEAT_INTERVAL_S: Final[float] = 30.0
HEARTBEAT_TIMEOUT_S: Final[float] = 10.0
OUTBOUND_QUEUE_MAXSIZE: Final[int] = 1000

# WebSocket-Close-Codes (anwendungsdefiniert, 4000—4999).
CLOSE_TIMEOUT: Final[int] = 4408  # Heartbeat-Pong-Timeout.

ActionHandler = Callable[["Connection", str, dict[str, Any]], Awaitable[None]]


@dataclass(slots=True, eq=False)
class Connection:
    """Eine aktive WebSocket-Verbindung am Hub.

    ``eq=False``: Verbindungen werden per Identität verglichen und gehasht
    (sie liegen in den Subscription-Sets des Hubs); zwei distinkte Sockets
    sind nie „gleich", auch bei identischen Feldwerten.
    """

    websocket: WebSocket
    kind: str
    subject_id: uuid.UUID
    tenant_id: uuid.UUID | None = None
    anon_session_id: uuid.UUID | None = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    topics: set[str] = field(default_factory=set)
    queue: asyncio.Queue[dict[str, Any]] = field(
        default_factory=lambda: asyncio.Queue(maxsize=OUTBOUND_QUEUE_MAXSIZE)
    )
    _last_activity: float = field(default_factory=time.monotonic)

    def touch(self) -> None:
        """Markiere Aktivität (jede Inbound-Nachricht inkl. Pong)."""
        self._last_activity = time.monotonic()

    def idle_seconds(self) -> float:
        return time.monotonic() - self._last_activity

    def enqueue(self, frame: dict[str, Any]) -> bool:
        """Best-Effort-Outbound. ``False`` wenn die Queue voll ist (Slow-Client).

        Ein verworfenes Frame ist kein Datenverlust: der State liegt in der
        DB, der Client refetcht beim Reconnect (S9, kein WS-Replay).
        """
        try:
            self.queue.put_nowait(frame)
        except asyncio.QueueFull:
            return False
        return True

    def accepts(self, message: dict[str, Any]) -> bool:
        """Verbindungs-spezifischer Frame-Filter.

        Anon-Einsatzkraft sieht ausschließlich Frames der **eigenen**
        anonymen Session (Vision-Constraint: keine fremden Bestellungen).
        Disponent/Carer sehen alle Frames ihrer abonnierten Topics.
        """
        if self.kind != KIND_ANON:
            return True
        payload = message.get("payload") or {}
        return payload.get("anonymous_session_id") == str(self.anon_session_id)


async def writer_loop(conn: Connection) -> None:
    """Leert die Outbound-Queue auf die WebSocket (einziger Sender)."""
    while True:
        frame = await conn.queue.get()
        await conn.websocket.send_json(frame)


async def heartbeat_loop(
    conn: Connection,
    *,
    interval: float = HEARTBEAT_INTERVAL_S,
    timeout: float = HEARTBEAT_TIMEOUT_S,
) -> None:
    """Sendet periodisch Ping; schließt bei ausbleibendem Pong.

    Schließen erfolgt über ``websocket.close`` — das beendet die parallel
    laufende ``receive_loop`` mit ``WebSocketDisconnect``, woraufhin der
    Endpoint aufräumt.
    """
    while True:
        await asyncio.sleep(interval)
        if conn.idle_seconds() > interval + timeout:
            logger.info(
                "realtime.heartbeat.timeout",
                extra={"realtime_connection_id": str(conn.id), "realtime_kind": conn.kind},
            )
            await conn.websocket.close(code=CLOSE_TIMEOUT)
            return
        conn.enqueue(messages.ping_frame())


async def receive_loop(conn: Connection, on_action: ActionHandler) -> None:
    """Liest Client-Nachrichten und delegiert Aktionen an ``on_action``.

    Beendet sich bei ``WebSocketDisconnect`` (Client-Trennung oder durch
    Heartbeat ausgelöstes Close). Unbekannte Aktionen und ungültiges JSON
    erzeugen ein Fehler-Frame, **keinen** Drop (Detail-Plan 4.4-8A).
    """
    while True:
        try:
            raw = await conn.websocket.receive_text()
        except WebSocketDisconnect:
            return
        conn.touch()
        parsed = messages.parse_wire_message(raw)
        if parsed is None or not isinstance(parsed.get("action"), str):
            conn.enqueue(messages.error_frame(messages.ERROR_BAD_REQUEST, "Invalid message."))
            continue
        action = parsed["action"]
        data = parsed.get("data")
        if not isinstance(data, dict):
            data = {}
        if action == messages.ACTION_PONG:
            continue  # Aktivität bereits via touch() registriert.
        await on_action(conn, action, data)


__all__ = [
    "CLOSE_TIMEOUT",
    "HEARTBEAT_INTERVAL_S",
    "HEARTBEAT_TIMEOUT_S",
    "KIND_ANON",
    "KIND_CARER",
    "KIND_DISPATCHER",
    "Connection",
    "heartbeat_loop",
    "receive_loop",
    "writer_loop",
]
