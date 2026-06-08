// Präsentations-Helfer für Order-Status und Plausibilitäts-Outcome
// (Detail-Plan 4.5-6A). Bewusst von den API-Bindings getrennt und ohne
// Svelte-Runes — pure Funktionen, unit-testbar. Nach außen werden keine
// technischen Codes gezeigt (Einsatzkraft sieht nur Klartext).

import type { OrderStatus, PlausibilityOutcome } from "$lib/api/operations";

const STATUS_LABELS: Record<OrderStatus, string> = {
  pending: "Bestellung aufgenommen – wird zugewiesen …",
  needs_moderation: "Wird vom Disponenten geprüft.",
  assigned: "Einem Fahrzeug zugewiesen.",
  in_progress: "Fahrzeug ist unterwegs zu dir.",
  completed: "Übergabe abgeschlossen.",
  cancelled: "Bestellung storniert.",
};

export function statusLabel(status: string): string {
  return STATUS_LABELS[status as OrderStatus] ?? "Status wird aktualisiert …";
}

// Outcome-abhängige Rückmeldung direkt nach dem Absenden: ACCEPTED geht in
// die Auto-Verteilung, jedes MODERATION_* in die Disponenten-Queue.
export function outcomeMessage(outcome: PlausibilityOutcome): string {
  if (outcome === "ACCEPTED") {
    return "Bestellung aufgenommen.";
  }
  return "Deine Bestellung wurde aufgenommen und geht zur Prüfung an den Disponenten.";
}
