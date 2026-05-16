// Dünner Wrapper um `fetch()` mit einheitlichem Error-Mapping. Default
// `credentials: "include"`, weil die anonyme Session über ein HttpOnly-
// Cookie läuft (S2a, gesetzt durch POST /api/anon/{token}/session).
// Baseurl ist leer (relative Pfade) — funktioniert mit Vite-Dev-Proxy und
// mit Caddy/nginx in Production gleichermaßen.
//
// Die Klasse ist eine 1:1-Portierung aus frontend-disponent (Schritt 2.5).
// Eine gemeinsame Workspace-Library wäre eigenes Refactoring (ADR-pflichtig,
// pnpm-Workspace-Hygiene); Inline-Duplikation analog ESLint-Flat-Config.

export type ApiErrorKind =
  | "auth" // 401 — Code falsch / Session ungültig
  | "forbidden" // 403 — kein Phase-2-Pfad in S2a, defensiv gemappt
  | "not-found" // 404 — URL ungültig / Operation in planned/closed
  | "gone" // 410 — Token-Signatur abgelehnt / Operation geschlossen
  | "conflict" // 409 — kein Phase-2-Pfad in S2a, defensiv gemappt
  | "validation" // 422 — Pattern-Verstoß auf AccessCode
  | "rate-limit" // 429 — 5 Fehlversuche/15 min/IP oder Token
  | "server" // 5xx
  | "network"; // Netzwerk- oder CORS-Fehler

export class ApiError extends Error {
  readonly kind: ApiErrorKind;
  readonly status: number;
  readonly retryAfter: number | null;

  constructor(kind: ApiErrorKind, status: number, message: string, retryAfter: number | null) {
    super(message);
    this.name = "ApiError";
    this.kind = kind;
    this.status = status;
    this.retryAfter = retryAfter;
  }
}

function parseRetryAfter(header: string | null): number | null {
  if (header === null) return null;
  const seconds = Number.parseInt(header, 10);
  if (Number.isFinite(seconds) && seconds >= 0) {
    return seconds;
  }
  return null;
}

function mapStatusToKind(status: number): ApiErrorKind {
  if (status === 401) return "auth";
  if (status === 403) return "forbidden";
  if (status === 404) return "not-found";
  if (status === 409) return "conflict";
  if (status === 410) return "gone";
  if (status === 422) return "validation";
  if (status === 429) return "rate-limit";
  if (status >= 500) return "server";
  // Andere 4xx-Status werden als "validation" eingeordnet — defensiver Default.
  return "validation";
}

async function readDetail(response: Response): Promise<string> {
  try {
    const payload = (await response.clone().json()) as unknown;
    if (
      typeof payload === "object" &&
      payload !== null &&
      "detail" in payload &&
      typeof (payload as { detail: unknown }).detail === "string"
    ) {
      return (payload as { detail: string }).detail;
    }
  } catch {
    // Nicht-JSON-Antwort — Status-Text als Fallback.
  }
  return response.statusText || `HTTP ${response.status}`;
}

export interface ApiRequestInit extends Omit<RequestInit, "body"> {
  json?: unknown;
}

export async function apiFetch(path: string, init: ApiRequestInit = {}): Promise<Response> {
  const { json, headers, ...rest } = init;
  const finalHeaders = new Headers(headers ?? {});
  const finalInit: RequestInit = {
    credentials: "include",
    ...rest,
    headers: finalHeaders,
  };
  if (json !== undefined) {
    finalHeaders.set("Content-Type", "application/json");
    finalInit.body = JSON.stringify(json);
  }

  let response: Response;
  try {
    response = await fetch(path, finalInit);
  } catch (cause) {
    const message = cause instanceof Error ? cause.message : "Network request failed";
    throw new ApiError("network", 0, message, null);
  }

  if (!response.ok) {
    const detail = await readDetail(response);
    const retryAfter = parseRetryAfter(response.headers.get("retry-after"));
    throw new ApiError(mapStatusToKind(response.status), response.status, detail, retryAfter);
  }

  return response;
}

export async function apiGet<T>(path: string): Promise<T> {
  const response = await apiFetch(path, { method: "GET" });
  return (await response.json()) as T;
}

export async function apiPost<T>(path: string, body?: unknown): Promise<T | null> {
  const response = await apiFetch(path, {
    method: "POST",
    json: body,
  });
  if (response.status === 204) {
    return null;
  }
  return (await response.json()) as T;
}
