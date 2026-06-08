"""``backend/realtime`` — WebSocket-Hub + Valkey-Pub/Sub-Fan-out (Schritt 4.4).

Öffentliche Bausteine:

* ``WebSocketHub``      — worker-lokale Registry + Pub/Sub-Listener.
* ``RealtimePublisher`` — S3-Publisher (``backend/operations`` → Valkey).
* ``router``            — WebSocket-Endpunkte (S9), gemountet unter ``/api/ws``.

Topic-Schema und Nachrichten-Format siehe ``topics`` und ``messages``.
"""

from __future__ import annotations

from eb_digital.realtime.api import router
from eb_digital.realtime.hub import WebSocketHub
from eb_digital.realtime.publisher import RealtimePublisher

__all__ = ["RealtimePublisher", "WebSocketHub", "router"]
