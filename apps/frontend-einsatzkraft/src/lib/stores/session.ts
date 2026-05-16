// In-Memory-Session-Cache für die anonyme Einsatzkraft-Session.
//
// Detail-Frage 3-A aus 2.5 analog: HttpOnly-Cookie ist die alleinige
// persistente Quelle der Wahrheit; localStorage/sessionStorage wird
// bewusst nicht genutzt, um XSS-Defense-in-depth nicht zu schwächen
// (Vision-PII-Constraint + project-context.md Abschnitt 6).
//
// Der Store dient als Token-Bindung zwischen `/[token]` und
// `/[token]/dashboard`: nach 201-Response auf POST /session wird er
// gefüllt; auf der Dashboard-Route prüft `+layout.ts`, ob der Store für
// genau den aktuellen Token einen Eintrag hat. Hard-Refresh leert den
// Store — Folge: redirect zurück zu `/[token]` für neue Code-Eingabe.
//
// Reaktivität auf den Store-Wert ist nicht nötig (keine UI-Komponente
// abonniert ihn). Daher reine TS-Datei ohne Svelte-Runes — testbar ohne
// Svelte-Compiler im vitest-Setup.

export interface AnonymousSessionState {
  token: string;
  sessionId: string;
  areaLabel: string;
  accessCodeActive: boolean;
}

let current: AnonymousSessionState | null = null;

export function setSession(state: AnonymousSessionState): void {
  current = state;
}

export function clearSession(): void {
  current = null;
}

export function getSession(): AnonymousSessionState | null {
  return current;
}

export function isActiveForToken(token: string): boolean {
  return current !== null && current.token === token;
}
