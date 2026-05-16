// Unit-Tests für den fetch-Wrapper in src/lib/api/client.ts.
// Fokus: Status-Code → ApiErrorKind-Mapping, Retry-After-Parsing,
// JSON-Body-Serialisierung, Network-Fehler. Spiegelt die analoge
// Suite aus frontend-disponent — der Client ist 1:1 portiert.

import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { apiFetch, apiGet, apiPost, ApiError } from "../src/lib/api/client";

type FetchMock = ReturnType<typeof vi.fn>;

function setFetchMock(impl: (input: string, init?: RequestInit) => Promise<Response>): FetchMock {
  const mock = vi.fn(impl);
  vi.stubGlobal("fetch", mock);
  return mock;
}

function jsonResponse(body: unknown, init: ResponseInit = {}): Response {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { "Content-Type": "application/json" },
    ...init,
  });
}

describe("apiFetch", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("sends GET with credentials: 'include' by default", async () => {
    const mock = setFetchMock(async () => jsonResponse({ ok: true }));
    await apiFetch("/api/test");
    expect(mock).toHaveBeenCalledOnce();
    const [, init] = mock.mock.calls[0]!;
    expect((init as RequestInit).credentials).toBe("include");
  });

  test("serializes json body and sets Content-Type", async () => {
    const mock = setFetchMock(async () => new Response(null, { status: 204 }));
    await apiFetch("/api/test", { method: "POST", json: { a: 1 } });
    const [, init] = mock.mock.calls[0]!;
    const headers = new Headers((init as RequestInit).headers);
    expect(headers.get("Content-Type")).toBe("application/json");
    expect((init as RequestInit).body).toBe(JSON.stringify({ a: 1 }));
  });

  test("maps 401 to ApiError(kind='auth')", async () => {
    setFetchMock(async () => jsonResponse({ detail: "Not authenticated." }, { status: 401 }));
    await expect(apiFetch("/api/anon/x/session")).rejects.toMatchObject({
      name: "ApiError",
      kind: "auth",
      status: 401,
    });
  });

  test("maps 403 to ApiError(kind='forbidden')", async () => {
    setFetchMock(async () => jsonResponse({ detail: "Forbidden." }, { status: 403 }));
    await expect(apiFetch("/api/test")).rejects.toMatchObject({ kind: "forbidden" });
  });

  test("maps 404 to ApiError(kind='not-found')", async () => {
    setFetchMock(async () => jsonResponse({ detail: "Not found." }, { status: 404 }));
    await expect(apiFetch("/api/anon/x/info")).rejects.toMatchObject({ kind: "not-found" });
  });

  test("maps 409 to ApiError(kind='conflict')", async () => {
    setFetchMock(async () => jsonResponse({ detail: "Conflict." }, { status: 409 }));
    await expect(apiFetch("/api/test")).rejects.toMatchObject({ kind: "conflict" });
  });

  test("maps 410 to ApiError(kind='gone')", async () => {
    setFetchMock(async () => jsonResponse({ detail: "Gone." }, { status: 410 }));
    await expect(apiFetch("/api/anon/x/session")).rejects.toMatchObject({ kind: "gone" });
  });

  test("maps 422 to ApiError(kind='validation')", async () => {
    setFetchMock(async () => jsonResponse({ detail: "Invalid." }, { status: 422 }));
    await expect(apiFetch("/api/anon/x/session")).rejects.toMatchObject({
      kind: "validation",
    });
  });

  test("maps 429 with Retry-After to ApiError(kind='rate-limit', retryAfter set)", async () => {
    setFetchMock(
      async () =>
        new Response(JSON.stringify({ detail: "Too many." }), {
          status: 429,
          headers: { "Content-Type": "application/json", "Retry-After": "42" },
        }),
    );
    const error = await apiFetch("/api/anon/x/session").catch((cause) => cause);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).kind).toBe("rate-limit");
    expect((error as ApiError).retryAfter).toBe(42);
  });

  test("ignores non-numeric Retry-After header", async () => {
    setFetchMock(
      async () =>
        new Response(JSON.stringify({}), {
          status: 429,
          headers: { "Content-Type": "application/json", "Retry-After": "not-a-number" },
        }),
    );
    const error = await apiFetch("/api/test").catch((cause) => cause);
    expect((error as ApiError).retryAfter).toBeNull();
  });

  test("maps 5xx to ApiError(kind='server')", async () => {
    setFetchMock(async () => new Response("boom", { status: 503 }));
    await expect(apiFetch("/api/test")).rejects.toMatchObject({ kind: "server" });
  });

  test("maps thrown fetch errors to ApiError(kind='network')", async () => {
    setFetchMock(async () => {
      throw new TypeError("Failed to fetch");
    });
    const error = await apiFetch("/api/test").catch((cause) => cause);
    expect(error).toBeInstanceOf(ApiError);
    expect((error as ApiError).kind).toBe("network");
    expect((error as ApiError).status).toBe(0);
  });

  test("falls back to statusText when body is not JSON", async () => {
    setFetchMock(
      async () =>
        new Response("plain text", {
          status: 503,
          statusText: "Service Unavailable",
        }),
    );
    const error = await apiFetch("/api/test").catch((cause) => cause);
    expect((error as ApiError).message).toBe("Service Unavailable");
  });
});

describe("apiGet / apiPost", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("apiGet returns parsed JSON", async () => {
    setFetchMock(async () => jsonResponse({ foo: "bar" }));
    const result = await apiGet<{ foo: string }>("/api/test");
    expect(result).toEqual({ foo: "bar" });
  });

  test("apiPost returns parsed JSON on 201", async () => {
    setFetchMock(async () => jsonResponse({ id: "x" }, { status: 201 }));
    const result = await apiPost<{ id: string }>("/api/test", {});
    expect(result).toEqual({ id: "x" });
  });

  test("apiPost returns null on 204", async () => {
    setFetchMock(async () => new Response(null, { status: 204 }));
    const result = await apiPost<unknown>("/api/test", {});
    expect(result).toBeNull();
  });
});
