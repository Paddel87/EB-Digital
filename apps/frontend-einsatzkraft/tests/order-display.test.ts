// Unit-Tests für die Präsentations-Helfer in src/lib/order-display.ts.

import { describe, expect, test } from "vitest";
import { outcomeMessage, statusLabel } from "../src/lib/order-display";

describe("statusLabel", () => {
  test("maps known statuses to German labels", () => {
    expect(statusLabel("pending")).toMatch(/aufgenommen/i);
    expect(statusLabel("needs_moderation")).toMatch(/geprüft/i);
    expect(statusLabel("assigned")).toMatch(/zugewiesen/i);
    expect(statusLabel("in_progress")).toMatch(/unterwegs/i);
    expect(statusLabel("completed")).toMatch(/abgeschlossen/i);
    expect(statusLabel("cancelled")).toMatch(/storniert/i);
  });

  test("falls back for unknown status", () => {
    expect(statusLabel("something_new")).toMatch(/aktualisiert/i);
  });
});

describe("outcomeMessage", () => {
  test("ACCEPTED is a plain confirmation", () => {
    expect(outcomeMessage("ACCEPTED")).toBe("Bestellung aufgenommen.");
  });

  test("every MODERATION_* points to the dispatcher review", () => {
    expect(outcomeMessage("MODERATION_NO_GPS")).toMatch(/Disponenten/i);
    expect(outcomeMessage("MODERATION_ACCURACY_TOO_LOW")).toMatch(/Disponenten/i);
    expect(outcomeMessage("MODERATION_OUT_OF_RANGE")).toMatch(/Disponenten/i);
  });
});
