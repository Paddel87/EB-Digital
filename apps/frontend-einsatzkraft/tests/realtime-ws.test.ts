// Unit-Tests für den WebSocket-Client (S9) in src/lib/realtime/ws.ts.
// Erster WS-Konsument im Projekt — getestet mit einem Fake-Socket
// (WebSocketLike) und Fake-Timern für das Reconnect-Backoff. Kein
// window/WebSocket nötig (Test-Env "node"): socketFactory + urlBuilder
// werden injiziert.

import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import {
  AnonymousRealtimeClient,
  nextBackoffMs,
  type OrderStatusEvent,
  type WebSocketLike,
} from "../src/lib/realtime/ws";

class FakeSocket implements WebSocketLike {
  sent: string[] = [];
  closed = false;
  onopen: (() => void) | null = null;
  onmessage: ((event: { data: unknown }) => void) | null = null;
  onclose: (() => void) | null = null;
  onerror: (() => void) | null = null;

  constructor(readonly url: string) {}

  send(data: string): void {
    this.sent.push(data);
  }
  close(): void {
    this.closed = true;
    this.onclose?.();
  }

  // Test-Helfer (simulieren Server-Seite):
  emitOpen(): void {
    this.onopen?.();
  }
  emitMessage(frame: unknown): void {
    this.onmessage?.({ data: JSON.stringify(frame) });
  }
  emitClose(): void {
    this.onclose?.();
  }
}

function harness() {
  const sockets: FakeSocket[] = [];
  const orderEvents: OrderStatusEvent[] = [];
  const errors: string[] = [];
  const connectionStates: boolean[] = [];
  const client = new AnonymousRealtimeClient("tok", {
    onOrderStatus: (event) => orderEvents.push(event),
    onError: (message) => errors.push(message),
    onConnectionChange: (connected) => connectionStates.push(connected),
    socketFactory: (url) => {
      const socket = new FakeSocket(url);
      sockets.push(socket);
      return socket;
    },
    urlBuilder: (token) => `ws://test/api/ws/anon/${token}`,
    reconnectBaseMs: 1000,
    reconnectMaxMs: 30_000,
  });
  return { client, sockets, orderEvents, errors, connectionStates };
}

describe("nextBackoffMs", () => {
  test("grows exponentially and caps at max", () => {
    expect(nextBackoffMs(0, 1000, 30_000)).toBe(1000);
    expect(nextBackoffMs(1, 1000, 30_000)).toBe(2000);
    expect(nextBackoffMs(2, 1000, 30_000)).toBe(4000);
    expect(nextBackoffMs(10, 1000, 30_000)).toBe(30_000);
  });
});

describe("AnonymousRealtimeClient", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
  });

  test("connect opens a socket against the built URL", () => {
    const { client, sockets } = harness();
    client.connect();
    expect(sockets).toHaveLength(1);
    expect(sockets[0]!.url).toBe("ws://test/api/ws/anon/tok");
  });

  test("reports connection state on open and close", () => {
    const { client, sockets, connectionStates } = harness();
    client.connect();
    sockets[0]!.emitOpen();
    expect(connectionStates).toEqual([true]);
    sockets[0]!.emitClose();
    expect(connectionStates).toEqual([true, false]);
  });

  test("replies to a ping frame with a pong action", () => {
    const { client, sockets } = harness();
    client.connect();
    sockets[0]!.emitMessage({ topic: null, event_type: "ping", payload: {}, ts: "t" });
    expect(sockets[0]!.sent).toEqual([JSON.stringify({ action: "pong" })]);
  });

  test("dispatches order_status frames with order_id and status", () => {
    const { client, sockets, orderEvents } = harness();
    client.connect();
    sockets[0]!.emitMessage({
      topic: "operation.op.order_status",
      event_type: "order_assigned",
      payload: { event_type: "order_assigned", order_id: "ord-1", status: "assigned" },
      ts: "t",
    });
    expect(orderEvents).toEqual([
      { eventType: "order_assigned", orderId: "ord-1", status: "assigned" },
    ]);
  });

  test("surfaces error frames via onError", () => {
    const { client, sockets, errors } = harness();
    client.connect();
    sockets[0]!.emitMessage({
      topic: null,
      event_type: "error",
      payload: { code: "forbidden", message: "Nope." },
      ts: "t",
    });
    expect(errors).toEqual(["Nope."]);
  });

  test("ignores frames without order_id and malformed payloads", () => {
    const { client, sockets, orderEvents } = harness();
    client.connect();
    sockets[0]!.emitMessage({ event_type: "subscribed", payload: { topics: [] }, ts: "t" });
    sockets[0]!.onmessage?.({ data: "not-json" });
    expect(orderEvents).toEqual([]);
  });

  test("reconnects after an unexpected close, with backoff", () => {
    const { client, sockets } = harness();
    client.connect();
    sockets[0]!.emitOpen();
    sockets[0]!.emitClose(); // unerwartet
    expect(sockets).toHaveLength(1);
    vi.advanceTimersByTime(1000);
    expect(sockets).toHaveLength(2); // neuer Socket nach Backoff
  });

  test("does not reconnect after caller close()", () => {
    const { client, sockets } = harness();
    client.connect();
    sockets[0]!.emitOpen();
    client.close();
    vi.advanceTimersByTime(60_000);
    expect(sockets).toHaveLength(1);
    expect(sockets[0]!.closed).toBe(true);
  });

  test("ignores non-object JSON and tolerates onerror", () => {
    const { client, sockets, orderEvents, errors } = harness();
    client.connect();
    // valides JSON, aber kein Objekt → kein Dispatch, kein Crash.
    sockets[0]!.onmessage?.({ data: "42" });
    // Frame mit nicht-objektartigem payload → payload-Default {}.
    sockets[0]!.emitMessage({ event_type: "order_placed", payload: "x", ts: "t" });
    // Frame ohne event_type und ohne order_id.
    sockets[0]!.emitMessage({ topic: null, payload: {}, ts: "t" });
    // onerror ist ein No-Op (Reconnect läuft über onclose) — darf nicht werfen.
    sockets[0]!.onerror?.();
    expect(orderEvents).toEqual([]);
    expect(errors).toEqual([]);
  });

  test("falls back to defaults when optional options are omitted", () => {
    // Deckt die `?? DEFAULT`-Zweige im Konstruktor ab; kein connect() (würde
    // den Browser-Default-Socket bauen, im Node-Env nicht verfügbar).
    const client = new AnonymousRealtimeClient("tok", { onOrderStatus: () => {} });
    expect(client).toBeInstanceOf(AnonymousRealtimeClient);
  });
});
