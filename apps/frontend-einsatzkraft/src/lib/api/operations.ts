// Order-API-Binding für die in 4.3a produktive S2c unter
// /api/anon/{operation_url}/order. Spiegelt die Pydantic-Schemas
// PlaceOrderRequest / AnonymousOrderOut aus
// backend/eb_digital/operations/schemas.py — bei Backend-Vertragsänderung
// hier nachziehen.

import { apiPost } from "$lib/api/client";

// Order-Status (Literal aus AnonymousOrderOut.status). Übergänge werden
// nach dem Absenden live via WS (S9 order_status-Events) nachgezogen.
export type OrderStatus =
  | "pending"
  | "needs_moderation"
  | "assigned"
  | "in_progress"
  | "completed"
  | "cancelled";

// Plausibilitäts-Outcome (ADR-017). ACCEPTED → Auto-Verteilung; jedes
// MODERATION_* → Disponenten-Queue.
export type PlausibilityOutcome =
  | "ACCEPTED"
  | "MODERATION_NO_GPS"
  | "MODERATION_ACCURACY_TOO_LOW"
  | "MODERATION_OUT_OF_RANGE";

// Order-Item mit genau einer Katalog-Referenz: Base-Items über
// `base_item_id`, eigenständige Mandanten-Items über `tenant_extension_id`
// (CHECK `exactly_one_ref` im Backend).
export interface OrderItemIn {
  base_item_id?: string;
  tenant_extension_id?: string;
  quantity: number;
}

export interface PlaceOrderRequest {
  items: OrderItemIn[];
  location_lat?: number | null;
  location_lng?: number | null;
  location_accuracy_m?: number | null;
  location_text?: string | null;
}

export interface AnonymousOrderOut {
  id: string;
  status: OrderStatus;
  plausibility_outcome: PlausibilityOutcome;
  placed_at: string;
}

function orderPath(token: string): string {
  return `/api/anon/${encodeURIComponent(token)}/order`;
}

export async function placeOrder(
  token: string,
  request: PlaceOrderRequest,
): Promise<AnonymousOrderOut> {
  const result = await apiPost<AnonymousOrderOut>(orderPath(token), request);
  if (result === null) {
    throw new Error("Order response unexpectedly empty.");
  }
  return result;
}
