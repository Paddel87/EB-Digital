// In-Memory-Session-Cache. Detail-Frage 3-A aus 2.5: HttpOnly-Cookie ist die
// alleinige persistente Quelle der Wahrheit; localStorage/sessionStorage
// wird bewusst nicht genutzt, um XSS-Defense-in-depth nicht zu schwächen
// (project-context.md Abschnitt 6 „Privacy-by-Design").
//
// Reaktivität auf den Store-Wert ist nicht nötig — die Konsumenten lesen
// `data.user` aus dem LayoutData, das von `(authed)/+layout.ts` via
// `GET /api/auth/me` geliefert wird. Der Store dient nur als
// optionaler Cache-Hint und als Logout-Cleanup-Punkt.
//
// Daher reine TS-Datei ohne Svelte-Runes — testbar ohne Svelte-Compiler.

import type { SessionUser } from "$lib/api/auth";

let current: SessionUser | null = null;

export function setSession(user: SessionUser): void {
  current = user;
}

export function clearSession(): void {
  current = null;
}

export function getSession(): SessionUser | null {
  return current;
}

export function isAuthenticated(): boolean {
  return current !== null;
}
