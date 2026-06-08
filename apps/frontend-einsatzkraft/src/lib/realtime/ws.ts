// WebSocket-Client für die anonyme Einsatzkraft (Detail-Plan 4.5-2A,
// Schnittstelle S9). Erster WS-Konsument im Projekt — bewusst gekapselt
// und unit-testbar (injizierbare Socket-Factory), damit spätere Frontends
// (Disponent/Betreuer, Phase 6) das Muster übernehmen können.
//
// Vertrag (backend/eb_digital/realtime):
//   • Server → Client: JSON-Frame `{ topic, event_type, payload, ts }`.
//     - event_type "ping"  → Client antwortet `{ action: "pong" }`
//       (Heartbeat 30 s/10 s; jede Inbound-Nachricht resettet den
//       Server-Idle-Timer, 40 s Budget).
//     - event_type "error" → Fehler-Frame (kein Drop) → onError.
//     - sonst: order_status-Event mit payload `{ order_id, status, ... }`.
//   • Anon-Filterung nach `session_id` ist serverseitig (Cookie) — der
//     Client subscribt nicht aktiv und empfängt nur eigene Bestellungen.
//   • Reconnect ist Client-Aufgabe; State-Reload via REST (hier: erneutes
//     Bestellen / In-Memory-Seed aus POST /order) — kein WS-Replay.

export interface OrderStatusEvent {
  eventType: string;
  orderId: string;
  status: string;
}

// Minimal-Schnittstelle, die der Browser-`WebSocket` strukturell erfüllt;
// Tests reichen einen Fake mit denselben Property-Handlern.
export interface WebSocketLike {
  send(data: string): void;
  close(): void;
  onopen: (() => void) | null;
  onmessage: ((event: { data: unknown }) => void) | null;
  onclose: (() => void) | null;
  onerror: (() => void) | null;
}

export interface RealtimeClientOptions {
  onOrderStatus: (event: OrderStatusEvent) => void;
  onError?: (message: string) => void;
  onConnectionChange?: (connected: boolean) => void;
  socketFactory?: (url: string) => WebSocketLike;
  urlBuilder?: (token: string) => string;
  reconnectBaseMs?: number;
  reconnectMaxMs?: number;
}

const DEFAULT_RECONNECT_BASE_MS = 1_000;
const DEFAULT_RECONNECT_MAX_MS = 30_000;

// Exponentielles Backoff mit Obergrenze: 1s, 2s, 4s, … bis max.
export function nextBackoffMs(attempt: number, baseMs: number, maxMs: number): number {
  const exponential = baseMs * 2 ** Math.max(0, attempt);
  return Math.min(exponential, maxMs);
}

function defaultUrl(token: string): string {
  const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${scheme}//${window.location.host}/api/ws/anon/${encodeURIComponent(token)}`;
}

function defaultSocketFactory(url: string): WebSocketLike {
  return new WebSocket(url) as unknown as WebSocketLike;
}

interface ParsedFrame {
  eventType: string | null;
  payload: Record<string, unknown>;
}

function parseFrame(raw: unknown): ParsedFrame | null {
  if (typeof raw !== "string") return null;
  let data: unknown;
  try {
    data = JSON.parse(raw);
  } catch {
    return null;
  }
  if (typeof data !== "object" || data === null) return null;
  const record = data as Record<string, unknown>;
  const eventType = typeof record.event_type === "string" ? record.event_type : null;
  const payload =
    typeof record.payload === "object" && record.payload !== null
      ? (record.payload as Record<string, unknown>)
      : {};
  return { eventType, payload };
}

export class AnonymousRealtimeClient {
  private readonly token: string;
  private readonly options: RealtimeClientOptions;
  private readonly reconnectBaseMs: number;
  private readonly reconnectMaxMs: number;
  private readonly socketFactory: (url: string) => WebSocketLike;
  private readonly buildUrl: (token: string) => string;

  private socket: WebSocketLike | null = null;
  private closedByCaller = false;
  private reconnectAttempt = 0;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;

  constructor(token: string, options: RealtimeClientOptions) {
    this.token = token;
    this.options = options;
    this.reconnectBaseMs = options.reconnectBaseMs ?? DEFAULT_RECONNECT_BASE_MS;
    this.reconnectMaxMs = options.reconnectMaxMs ?? DEFAULT_RECONNECT_MAX_MS;
    this.socketFactory = options.socketFactory ?? defaultSocketFactory;
    this.buildUrl = options.urlBuilder ?? defaultUrl;
  }

  connect(): void {
    this.closedByCaller = false;
    this.openSocket();
  }

  // Beendet die Verbindung endgültig (kein Reconnect mehr).
  close(): void {
    this.closedByCaller = true;
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    if (this.socket !== null) {
      const socket = this.socket;
      this.socket = null;
      socket.close();
    }
  }

  private openSocket(): void {
    const socket = this.socketFactory(this.buildUrl(this.token));
    this.socket = socket;
    socket.onopen = () => {
      this.reconnectAttempt = 0;
      this.options.onConnectionChange?.(true);
    };
    socket.onmessage = (event) => this.handleMessage(event.data);
    socket.onclose = () => this.handleClose(socket);
    socket.onerror = () => {
      // Fehler mündet zuverlässig in onclose — dort wird reconnected.
    };
  }

  private handleMessage(raw: unknown): void {
    const frame = parseFrame(raw);
    if (frame === null) return;

    if (frame.eventType === "ping") {
      this.send({ action: "pong" });
      return;
    }
    if (frame.eventType === "error") {
      const message =
        typeof frame.payload.message === "string" ? frame.payload.message : "Realtime-Fehler.";
      this.options.onError?.(message);
      return;
    }

    const orderId = frame.payload.order_id;
    const status = frame.payload.status;
    if (typeof orderId === "string" && typeof status === "string") {
      this.options.onOrderStatus({
        eventType: frame.eventType ?? "",
        orderId,
        status,
      });
    }
  }

  private handleClose(socket: WebSocketLike): void {
    // Ein Close eines bereits ersetzten Sockets ignorieren.
    if (socket !== this.socket) return;
    this.socket = null;
    this.options.onConnectionChange?.(false);
    if (this.closedByCaller) return;
    this.scheduleReconnect();
  }

  private scheduleReconnect(): void {
    const delay = nextBackoffMs(this.reconnectAttempt, this.reconnectBaseMs, this.reconnectMaxMs);
    this.reconnectAttempt += 1;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      if (!this.closedByCaller) {
        this.openSocket();
      }
    }, delay);
  }

  private send(message: unknown): void {
    if (this.socket === null) return;
    this.socket.send(JSON.stringify(message));
  }
}
