// Unit-Tests für den In-Memory-Session-Cache in src/lib/stores/session.ts.

import { beforeEach, describe, expect, test } from "vitest";
import { clearSession, getSession, isAuthenticated, setSession } from "../src/lib/stores/session";

const exampleUser = {
  kind: "dispatcher" as const,
  id: "abc",
  username: "alice",
  tenant_id: "t1",
  expires_at: "2026-05-15T00:00:00+00:00",
};

describe("session store", () => {
  beforeEach(() => {
    clearSession();
  });

  test("starts unauthenticated", () => {
    expect(getSession()).toBeNull();
    expect(isAuthenticated()).toBe(false);
  });

  test("setSession stores the user", () => {
    setSession(exampleUser);
    expect(getSession()).toEqual(exampleUser);
    expect(isAuthenticated()).toBe(true);
  });

  test("setSession overrides previous user", () => {
    setSession(exampleUser);
    const other = { ...exampleUser, id: "def", username: "bob" };
    setSession(other);
    expect(getSession()?.username).toBe("bob");
  });

  test("clearSession resets the store", () => {
    setSession(exampleUser);
    clearSession();
    expect(getSession()).toBeNull();
    expect(isAuthenticated()).toBe(false);
  });
});
