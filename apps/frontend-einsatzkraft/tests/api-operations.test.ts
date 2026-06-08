// Unit-Tests für das Order-API-Binding (S2c) in src/lib/api/operations.ts.

import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import {
  placeOrder,
  type AnonymousOrderOut,
  type PlaceOrderRequest,
} from "../src/lib/api/operations";

function setFetchMock(impl: (input: string, init?: RequestInit) => Promise<Response>) {
  const mock = vi.fn(impl);
  vi.stubGlobal("fetch", mock);
  return mock;
}

const exampleOrder: AnonymousOrderOut = {
  id: "order-uuid",
  status: "pending",
  plausibility_outcome: "ACCEPTED",
  placed_at: "2026-06-08T10:00:00+00:00",
};

const gpsRequest: PlaceOrderRequest = {
  items: [{ base_item_id: "base-1", quantity: 2 }],
  location_lat: 53.07,
  location_lng: 8.8,
  location_accuracy_m: 12,
};

describe("operations binding", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("placeOrder POSTs /api/anon/{token}/order with the request body", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify(exampleOrder), {
          status: 201,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const result = await placeOrder("abc-token", gpsRequest);
    expect(result).toEqual(exampleOrder);
    const [path, init] = mock.mock.calls[0]!;
    expect(path).toBe("/api/anon/abc-token/order");
    expect((init as RequestInit).method).toBe("POST");
    expect((init as RequestInit).body).toBe(JSON.stringify(gpsRequest));
  });

  test("placeOrder returns the moderation outcome unchanged", async () => {
    setFetchMock(
      async () =>
        new Response(
          JSON.stringify({
            ...exampleOrder,
            status: "needs_moderation",
            plausibility_outcome: "MODERATION_NO_GPS",
          }),
          { status: 201, headers: { "Content-Type": "application/json" } },
        ),
    );
    const result = await placeOrder("abc-token", {
      items: [{ tenant_extension_id: "ext-1", quantity: 1 }],
      location_text: "Marktplatz",
    });
    expect(result.status).toBe("needs_moderation");
    expect(result.plausibility_outcome).toBe("MODERATION_NO_GPS");
  });

  test("placeOrder throws if the response body is empty (204)", async () => {
    setFetchMock(async () => new Response(null, { status: 204 }));
    await expect(placeOrder("abc-token", gpsRequest)).rejects.toThrow(/empty/i);
  });
});
