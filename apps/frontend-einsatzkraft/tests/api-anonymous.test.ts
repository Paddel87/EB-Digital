// Unit-Tests für die Anonymous-API-Bindings in src/lib/api/anonymous.ts.
// Es wird der globale fetch gemockt — die Tests prüfen Pfad, Methode,
// Body-Serialisierung und Response-Parsing der S2a-Endpunkte.

import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fetchInfo, createSession } from "../src/lib/api/anonymous";

function setFetchMock(impl: (input: string, init?: RequestInit) => Promise<Response>) {
  const mock = vi.fn(impl);
  vi.stubGlobal("fetch", mock);
  return mock;
}

const exampleInfo = {
  area_label: "Bremen Innenstadt",
  access_code_active: true,
  status: "active" as const,
};

describe("anonymous bindings", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("fetchInfo GETs /api/anon/{token}/info and parses OperationInfo", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify(exampleInfo), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const result = await fetchInfo("abc-token");
    expect(result).toEqual(exampleInfo);
    expect(mock).toHaveBeenCalledOnce();
    const [path, init] = mock.mock.calls[0]!;
    expect(path).toBe("/api/anon/abc-token/info");
    expect((init as RequestInit).method).toBe("GET");
  });

  test("fetchInfo URL-encodes the token segment", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify(exampleInfo), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    await fetchInfo("a/b c+d");
    const [path] = mock.mock.calls[0]!;
    expect(path).toBe(`/api/anon/${encodeURIComponent("a/b c+d")}/info`);
  });

  test("createSession POSTs /api/anon/{token}/session with access_code", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify({ session_id: "session-uuid" }), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const result = await createSession("abc-token", "X7K3PQ");
    expect(result).toEqual({ session_id: "session-uuid" });
    const [path, init] = mock.mock.calls[0]!;
    expect(path).toBe("/api/anon/abc-token/session");
    expect((init as RequestInit).method).toBe("POST");
    expect((init as RequestInit).body).toBe(JSON.stringify({ access_code: "X7K3PQ" }));
  });

  test("createSession POSTs with access_code=null when no code", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify({ session_id: "sess" }), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
    );
    await createSession("abc-token", null);
    const [, init] = mock.mock.calls[0]!;
    expect((init as RequestInit).body).toBe(JSON.stringify({ access_code: null }));
  });

  test("createSession throws if response body is empty (204)", async () => {
    setFetchMock(async () => new Response(null, { status: 204 }));
    await expect(createSession("abc-token", null)).rejects.toThrow(/empty/i);
  });
});
