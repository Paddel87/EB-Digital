// AccessCode-Format-Helfer für die anonyme Einsatzkraft-Session.
//
// ADR-005 fixiert das Schema: Crockford-Base32-Variante mit 6 Zeichen,
// Alphabet `0-9 A-H J-K M-N P-T V-Z` (ohne `I/L/O/U` — Verwechslungs-
// Vermeidung beim manuellen Tippen). Backend-Pydantic-Pattern in
// backend/eb_digital/auth_anonymous/access_code.py ist identisch.
//
// Detail-Frage 3-A aus 2.6: strikte Client-Validation, weil das Pattern
// ADR-fest ist und ein Backend-Roundtrip + Rate-Limit-Counter-Risiko bei
// offensichtlichen Tippfehlern vermieden werden soll. Backend bleibt die
// Autorität — Client-Normalisierung ist UX-Hilfe, nicht Sicherheit.

export const ACCESS_CODE_PATTERN = /^[0-9A-HJ-KM-NP-TV-Z]{6}$/;
export const ACCESS_CODE_LENGTH = 6;
export const ACCESS_CODE_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";

// Erlaubt Whitespace und Bindestriche beim Tippen/Paste (z. B. "x7k 3pq"
// oder "X7K-3PQ" → "X7K3PQ"). Aggressivere Filter-Politik als Backend,
// das nur das Pattern matched — Backend ist Autorität, Client normalisiert
// für UX.
export function normalize(input: string): string {
  return input.replace(/[\s-]/g, "").toUpperCase();
}

export function isValid(code: string): boolean {
  return ACCESS_CODE_PATTERN.test(code);
}
