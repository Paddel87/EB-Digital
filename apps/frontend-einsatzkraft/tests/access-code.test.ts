// Unit-Tests für den AccessCode-Format-Helfer in src/lib/access-code.ts.
// ADR-005 fixiert das Pattern; diese Tests sichern die Client-Validation
// gegen Backend-Pattern-Drift.

import { describe, expect, test } from "vitest";
import {
  ACCESS_CODE_ALPHABET,
  ACCESS_CODE_LENGTH,
  ACCESS_CODE_PATTERN,
  isValid,
  normalize,
} from "../src/lib/access-code";

describe("access-code constants", () => {
  test("length is 6", () => {
    expect(ACCESS_CODE_LENGTH).toBe(6);
  });

  test("alphabet excludes I, L, O, U", () => {
    expect(ACCESS_CODE_ALPHABET).not.toContain("I");
    expect(ACCESS_CODE_ALPHABET).not.toContain("L");
    expect(ACCESS_CODE_ALPHABET).not.toContain("O");
    expect(ACCESS_CODE_ALPHABET).not.toContain("U");
  });

  test("alphabet matches the documented Crockford variant", () => {
    expect(ACCESS_CODE_ALPHABET).toBe("0123456789ABCDEFGHJKMNPQRSTVWXYZ");
  });

  test("pattern matches the alphabet (each character is accepted in single-char check)", () => {
    // Konstruiere einen gültigen 6er-Code aus den ersten 6 Alphabet-Zeichen.
    const sample = ACCESS_CODE_ALPHABET.slice(0, 6);
    expect(ACCESS_CODE_PATTERN.test(sample)).toBe(true);
  });
});

describe("normalize", () => {
  test("uppercases lowercase input", () => {
    expect(normalize("x7k3pq")).toBe("X7K3PQ");
  });

  test("strips whitespace", () => {
    expect(normalize("X7K 3PQ")).toBe("X7K3PQ");
    expect(normalize("  X7K3PQ  ")).toBe("X7K3PQ");
    expect(normalize("X 7 K 3 P Q")).toBe("X7K3PQ");
  });

  test("strips hyphens", () => {
    expect(normalize("X7K-3PQ")).toBe("X7K3PQ");
    expect(normalize("-X7K3PQ-")).toBe("X7K3PQ");
  });

  test("combined whitespace and hyphen", () => {
    expect(normalize("x7k - 3pq")).toBe("X7K3PQ");
  });

  test("leaves invalid characters intact (Backend rejects them)", () => {
    expect(normalize("xilou")).toBe("XILOU");
  });
});

describe("isValid", () => {
  test("accepts a canonical code", () => {
    expect(isValid("X7K3PQ")).toBe(true);
  });

  test("accepts all-digits", () => {
    expect(isValid("123456")).toBe(true);
  });

  test("rejects codes with I", () => {
    expect(isValid("X7K3PI")).toBe(false);
  });

  test("rejects codes with L", () => {
    expect(isValid("X7K3PL")).toBe(false);
  });

  test("rejects codes with O", () => {
    expect(isValid("X7K3PO")).toBe(false);
  });

  test("rejects codes with U", () => {
    expect(isValid("X7K3PU")).toBe(false);
  });

  test("rejects lowercase codes (normalize first)", () => {
    expect(isValid("x7k3pq")).toBe(false);
  });

  test("rejects codes shorter than 6", () => {
    expect(isValid("X7K3P")).toBe(false);
  });

  test("rejects codes longer than 6", () => {
    expect(isValid("X7K3PQR")).toBe(false);
  });

  test("rejects empty string", () => {
    expect(isValid("")).toBe(false);
  });

  test("rejects codes with whitespace (normalize first)", () => {
    expect(isValid("X7K 3PQ")).toBe(false);
  });
});
