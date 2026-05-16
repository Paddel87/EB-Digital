// Unit-Tests für den In-Memory-Anonymous-Session-Cache in
// src/lib/stores/session.ts.

import { beforeEach, describe, expect, test } from "vitest";
import {
  clearSession,
  getSession,
  isActiveForToken,
  setSession,
  type AnonymousSessionState,
} from "../src/lib/stores/session";

const exampleSession: AnonymousSessionState = {
  token: "abc-token",
  sessionId: "11111111-1111-1111-1111-111111111111",
  areaLabel: "Bremen Innenstadt",
  accessCodeActive: true,
};

describe("anonymous session store", () => {
  beforeEach(() => {
    clearSession();
  });

  test("starts empty", () => {
    expect(getSession()).toBeNull();
    expect(isActiveForToken("any-token")).toBe(false);
  });

  test("setSession stores the state", () => {
    setSession(exampleSession);
    expect(getSession()).toEqual(exampleSession);
  });

  test("isActiveForToken returns true only for the matching token", () => {
    setSession(exampleSession);
    expect(isActiveForToken("abc-token")).toBe(true);
    expect(isActiveForToken("other-token")).toBe(false);
    expect(isActiveForToken("")).toBe(false);
  });

  test("setSession overrides previous state", () => {
    setSession(exampleSession);
    const other: AnonymousSessionState = {
      ...exampleSession,
      token: "other-token",
      sessionId: "22222222-2222-2222-2222-222222222222",
    };
    setSession(other);
    expect(getSession()?.token).toBe("other-token");
    expect(isActiveForToken("abc-token")).toBe(false);
    expect(isActiveForToken("other-token")).toBe(true);
  });

  test("clearSession resets the store", () => {
    setSession(exampleSession);
    clearSession();
    expect(getSession()).toBeNull();
    expect(isActiveForToken("abc-token")).toBe(false);
  });
});
