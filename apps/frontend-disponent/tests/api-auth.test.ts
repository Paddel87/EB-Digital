// Unit-Tests für die Auth-Bindings in src/lib/api/auth.ts.
// Es wird der globale fetch gemockt — die Tests prüfen Pfad, Methode,
// Body-Serialisierung und Response-Parsing.

import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { login, logout, me, resetPassword } from "../src/lib/api/auth";

function setFetchMock(impl: (input: string, init?: RequestInit) => Promise<Response>) {
  const mock = vi.fn(impl);
  vi.stubGlobal("fetch", mock);
  return mock;
}

const exampleUser = {
  kind: "platform_admin" as const,
  id: "11111111-1111-1111-1111-111111111111",
  username: "patrick",
  tenant_id: null,
  expires_at: "2026-05-15T00:00:00+00:00",
};

describe("auth bindings", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("login posts to /api/auth/login with username+password", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify(exampleUser), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const result = await login("patrick", "password-123!");
    expect(result).toEqual(exampleUser);
    expect(mock).toHaveBeenCalledOnce();
    const [path, init] = mock.mock.calls[0]!;
    expect(path).toBe("/api/auth/login");
    expect((init as RequestInit).method).toBe("POST");
    expect((init as RequestInit).body).toBe(
      JSON.stringify({ username: "patrick", password: "password-123!" }),
    );
  });

  test("logout posts to /api/auth/logout and ignores 204 body", async () => {
    const mock = setFetchMock(async () => new Response(null, { status: 204 }));
    await logout();
    expect(mock).toHaveBeenCalledOnce();
    const [path, init] = mock.mock.calls[0]!;
    expect(path).toBe("/api/auth/logout");
    expect((init as RequestInit).method).toBe("POST");
  });

  test("me gets /api/auth/me and parses SessionUser", async () => {
    setFetchMock(
      async () =>
        new Response(JSON.stringify(exampleUser), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const result = await me();
    expect(result).toEqual(exampleUser);
  });

  test("resetPassword posts to /api/auth/reset-password with token+new_password", async () => {
    const mock = setFetchMock(async () => new Response(null, { status: 204 }));
    await resetPassword("token-abc", "new-passphrase-1");
    const [path, init] = mock.mock.calls[0]!;
    expect(path).toBe("/api/auth/reset-password");
    expect((init as RequestInit).body).toBe(
      JSON.stringify({ token: "token-abc", new_password: "new-passphrase-1" }),
    );
  });
});
