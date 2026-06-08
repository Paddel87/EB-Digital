// Unit-Tests für die Warenkorb-Logik in src/lib/stores/cart.ts.

import { describe, expect, test } from "vitest";
import {
  decrementQuantity,
  incrementQuantity,
  isEmpty,
  setQuantity,
  toOrderItems,
  totalQuantity,
  type CartQuantities,
} from "../src/lib/stores/cart";
import type { ResolvedCatalogItem } from "../src/lib/api/catalog";

function item(id: string, source: "base" | "tenant_own"): ResolvedCatalogItem {
  return {
    id,
    base_item_id: source === "base" ? null : null,
    source,
    name: id,
    unit: "x",
    default_unit_label: "Stück",
    description: null,
    category_id: "cat",
    category_name: "Cat",
  };
}

describe("cart quantities", () => {
  test("setQuantity stores a clamped, floored value", () => {
    expect(setQuantity({}, "a", 3)).toEqual({ a: 3 });
    expect(setQuantity({}, "a", 2.9)).toEqual({ a: 2 });
    expect(setQuantity({}, "a", 20_000)).toEqual({ a: 10_000 });
  });

  test("setQuantity to 0 or negative removes the entry", () => {
    expect(setQuantity({ a: 5 }, "a", 0)).toEqual({});
    expect(setQuantity({ a: 5 }, "a", -1)).toEqual({});
  });

  test("setQuantity does not mutate the input", () => {
    const cart: CartQuantities = { a: 1 };
    setQuantity(cart, "b", 2);
    expect(cart).toEqual({ a: 1 });
  });

  test("increment and decrement step by one and clamp at zero", () => {
    let cart: CartQuantities = {};
    cart = incrementQuantity(cart, "a");
    cart = incrementQuantity(cart, "a");
    expect(cart).toEqual({ a: 2 });
    cart = decrementQuantity(cart, "a");
    expect(cart).toEqual({ a: 1 });
    cart = decrementQuantity(cart, "a");
    expect(cart).toEqual({});
  });

  test("totalQuantity and isEmpty reflect the cart", () => {
    expect(isEmpty({})).toBe(true);
    expect(totalQuantity({ a: 2, b: 3 })).toBe(5);
    expect(isEmpty({ a: 1 })).toBe(false);
  });
});

describe("toOrderItems mapping", () => {
  const items = [item("base-1", "base"), item("ext-1", "tenant_own")];

  test("maps base source to base_item_id and tenant_own to tenant_extension_id", () => {
    const result = toOrderItems({ "base-1": 2, "ext-1": 1 }, items);
    expect(result).toContainEqual({ base_item_id: "base-1", quantity: 2 });
    expect(result).toContainEqual({ tenant_extension_id: "ext-1", quantity: 1 });
    expect(result).toHaveLength(2);
  });

  test("skips entries without a matching catalog item", () => {
    const result = toOrderItems({ unknown: 5 }, items);
    expect(result).toEqual([]);
  });

  test("skips zero quantities defensively", () => {
    const result = toOrderItems({ "base-1": 0 }, items);
    expect(result).toEqual([]);
  });
});
