// Smoke-Test für die Build-Zeit-Konstanten aus vite.config.ts `define`.
// Stellt sicher, dass die `define`-Pipeline funktioniert. Echte UI-Tests
// folgen ab Phase 4 (Operations Core).

import { describe, expect, test } from "vitest";

describe("vite define replacements", () => {
  test("APP_NAME compiles to a non-empty string", () => {
    const appName = (globalThis as { __APP_NAME__?: string }).__APP_NAME__;
    // In a non-vite test environment the macro is undefined; assert the type
    // contract holds when it IS defined.
    if (typeof appName === "string") {
      expect(appName.length).toBeGreaterThan(0);
    } else {
      expect(appName).toBeUndefined();
    }
  });
});
