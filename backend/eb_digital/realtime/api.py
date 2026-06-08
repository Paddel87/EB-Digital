"""WebSocket-Endpunkte des Realtime-Hubs (Schnittstelle S9, Schritt 4.4).

Drei rollengebundene Endpunkte:

* ``/ws/dispatcher`` — Cookie-Auth (Disponent). Client sendet ``subscribe``
  mit Operations-Liste; Server prüft je Operation ``tenant_participates_in_
  operation`` (S10) und abonniert alle Topic-Arten teilnehmender Operationen.
* ``/ws/carer`` — Cookie-Auth (Betreuer). Server abonniert automatisch
  ``assignment``+``chat`` aller Operationen des Mandanten (S10).
* ``/ws/anon/{operation_url}`` — anonyme Session-Cookie. Server abonniert
  ``order_status`` der eigenen Operation; Fan-out zusätzlich nach
  ``session_id`` gefiltert (Vision-Constraint).

Auth-Reject vor ``accept``: Close-Code **4401** (nicht authentifiziert) bzw.
**4403** (Pfad-Token passt nicht zur Session).
"""

from __future__ import annotations

import asyncio
import contextlib
import uuid
from typing import Any

from fastapi import APIRouter
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.websockets import WebSocket

from eb_digital.auth.sessions import get_current_session_user
from eb_digital.auth_anonymous.sessions import get_current_anonymous_session
from eb_digital.auth_anonymous.tokens import verify_url_token
from eb_digital.logging import get_logger
from eb_digital.realtime import messages
from eb_digital.realtime.connection import (
    KIND_ANON,
    KIND_CARER,
    KIND_DISPATCHER,
    ActionHandler,
    Connection,
    heartbeat_loop,
    receive_loop,
    writer_loop,
)
from eb_digital.realtime.hub import WebSocketHub
from eb_digital.realtime.topics import (
    ANON_KINDS,
    CARER_KINDS,
    DISPATCHER_KINDS,
    KIND_ORDER_STATUS,
    topic_for,
    topics_for_kinds,
)
from eb_digital.settings import get_settings

logger = get_logger(__name__)

CLOSE_UNAUTHENTICATED = 4401
CLOSE_FORBIDDEN = 4403

router = APIRouter(prefix="/ws", tags=["realtime"])


def _hub(websocket: WebSocket) -> WebSocketHub:
    hub = websocket.app.state.realtime_hub
    if not isinstance(hub, WebSocketHub):  # pragma: no cover — Wiring-Garantie
        msg = "realtime_hub not configured on app.state"
        raise RuntimeError(msg)
    return hub


def _session_factory(websocket: WebSocket) -> async_sessionmaker[Any]:
    return websocket.app.state.db_session_factory  # type: ignore[no-any-return]


# ─── Action-Handler ──────────────────────────────────────────────────────────


async def _dispatcher_action(conn: Connection, action: str, data: dict[str, Any]) -> None:
    """Subscribe/Unsubscribe für Disponenten (mit S10-Berechtigungsprüfung)."""
    if action not in (messages.ACTION_SUBSCRIBE, messages.ACTION_UNSUBSCRIBE):
        conn.enqueue(
            messages.error_frame(messages.ERROR_UNSUPPORTED_ACTION, f"Unsupported action: {action}")
        )
        return

    operation_ids = _parse_operation_ids(data.get("operations"))
    if operation_ids is None:
        conn.enqueue(
            messages.error_frame(
                messages.ERROR_BAD_REQUEST, "Field 'operations' must be a list of UUIDs."
            )
        )
        return

    hub = _hub(conn.websocket)
    if action == messages.ACTION_UNSUBSCRIBE:
        for operation_id in operation_ids:
            for topic in topics_for_kinds(operation_id, DISPATCHER_KINDS):
                hub.unsubscribe(conn, topic)
        conn.enqueue(messages.subscribed_frame(sorted(conn.topics)))
        return

    # Subscribe: Berechtigung je Operation prüfen (S10).
    from eb_digital.tenants.participation import tenant_participates_in_operation

    if conn.tenant_id is None:  # pragma: no cover — durch Endpoint-Auth garantiert
        return
    factory = _session_factory(conn.websocket)
    async with factory() as session:
        for operation_id in operation_ids:
            allowed = await tenant_participates_in_operation(
                session, tenant_id=conn.tenant_id, operation_id=operation_id
            )
            if not allowed:
                conn.enqueue(
                    messages.error_frame(
                        messages.ERROR_FORBIDDEN,
                        f"Not participating in operation {operation_id}.",
                        topic=topic_for(operation_id, KIND_ORDER_STATUS),
                    )
                )
                continue
            for topic in topics_for_kinds(operation_id, DISPATCHER_KINDS):
                hub.subscribe(conn, topic)
    conn.enqueue(messages.subscribed_frame(sorted(conn.topics)))


async def _reserved_action(conn: Connection, action: str, data: dict[str, Any]) -> None:
    """Carer/Anon: Subscriptions sind server-verwaltet; alle Client-Aktionen
    (inkl. der reservierten ``chat``/``gps_push``) sind in Phase 4 nicht
    unterstützt (Detail-Plan 4.4-8A)."""
    conn.enqueue(
        messages.error_frame(messages.ERROR_UNSUPPORTED_ACTION, f"Unsupported action: {action}")
    )


def _parse_operation_ids(raw: object) -> list[uuid.UUID] | None:
    if not isinstance(raw, list):
        return None
    result: list[uuid.UUID] = []
    for item in raw:
        if not isinstance(item, str):
            return None
        try:
            result.append(uuid.UUID(item))
        except ValueError:
            return None
    return result


# ─── Verbindungs-Orchestrierung ──────────────────────────────────────────────


async def _serve(conn: Connection, on_action: ActionHandler) -> None:
    """Registriert die Verbindung und fährt Writer-/Heartbeat-/Receive-Loop."""
    hub = _hub(conn.websocket)
    hub.register(conn)
    writer = asyncio.create_task(writer_loop(conn))
    heartbeat = asyncio.create_task(heartbeat_loop(conn))
    try:
        await receive_loop(conn, on_action)
    finally:
        writer.cancel()
        heartbeat.cancel()
        await asyncio.gather(writer, heartbeat, return_exceptions=True)
        hub.unregister(conn)
        with contextlib.suppress(RuntimeError):
            await conn.websocket.close()


# ─── Endpunkte ───────────────────────────────────────────────────────────────


@router.websocket("/dispatcher")
async def ws_dispatcher(websocket: WebSocket) -> None:
    user = get_current_session_user(websocket)
    if user is None or user.kind != KIND_DISPATCHER or user.tenant_id is None:
        await websocket.close(code=CLOSE_UNAUTHENTICATED)
        return
    await websocket.accept()
    conn = Connection(
        websocket=websocket,
        kind=KIND_DISPATCHER,
        subject_id=user.id,
        tenant_id=user.tenant_id,
    )
    await _serve(conn, _dispatcher_action)


@router.websocket("/carer")
async def ws_carer(websocket: WebSocket) -> None:
    user = get_current_session_user(websocket)
    if user is None or user.kind != KIND_CARER or user.tenant_id is None:
        await websocket.close(code=CLOSE_UNAUTHENTICATED)
        return
    await websocket.accept()
    conn = Connection(
        websocket=websocket,
        kind=KIND_CARER,
        subject_id=user.id,
        tenant_id=user.tenant_id,
    )
    hub = _hub(websocket)
    from eb_digital.tenants.participation import list_operations_for_tenant

    factory = _session_factory(websocket)
    async with factory() as session:
        operation_ids = await list_operations_for_tenant(session, user.tenant_id)
    for operation_id in operation_ids:
        for topic in topics_for_kinds(operation_id, CARER_KINDS):
            hub.subscribe(conn, topic)
    await _serve(conn, _reserved_action)


@router.websocket("/anon/{operation_url}")
async def ws_anon(websocket: WebSocket, operation_url: str) -> None:
    anon = get_current_anonymous_session(websocket)
    if anon is None:
        await websocket.close(code=CLOSE_UNAUTHENTICATED)
        return
    settings = get_settings()
    token_operation_id = verify_url_token(operation_url, settings.secret_key.get_secret_value())
    if token_operation_id is None or token_operation_id != anon.operation_id:
        await websocket.close(code=CLOSE_FORBIDDEN)
        return
    await websocket.accept()
    conn = Connection(
        websocket=websocket,
        kind=KIND_ANON,
        subject_id=anon.session_id,
        anon_session_id=anon.session_id,
    )
    hub = _hub(websocket)
    for topic in topics_for_kinds(anon.operation_id, ANON_KINDS):
        hub.subscribe(conn, topic)
    await _serve(conn, _reserved_action)


__all__ = ["CLOSE_FORBIDDEN", "CLOSE_UNAUTHENTICATED", "router"]
