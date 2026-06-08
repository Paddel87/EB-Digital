// Warenkorb-Logik (Detail-Plan 4.5-5A) als reine Funktionen über einem
// `{ resolverItemId: quantity }`-Record. Reaktivität hält die
// Dashboard-Komponente per `$state`; die Mapping-Logik bleibt hier
// Svelte-frei und damit ohne Compiler testbar (analog $lib/stores/session).

import type { OrderItemIn } from "$lib/api/operations";
import type { ResolvedCatalogItem } from "$lib/api/catalog";

// Schlüssel ist die Resolver-Eintrags-ID (`ResolvedCatalogItem.id`).
export type CartQuantities = Record<string, number>;

const MAX_QUANTITY = 10_000;

function clampQuantity(quantity: number): number {
  if (!Number.isFinite(quantity)) return 0;
  const floored = Math.floor(quantity);
  if (floored < 0) return 0;
  if (floored > MAX_QUANTITY) return MAX_QUANTITY;
  return floored;
}

// Liest die aktuelle Menge eines Eintrags. Map-basiert (statt dynamischem
// Record-Bracket-Zugriff), damit `eslint-plugin-security` keinen
// Object-Injection-Sink meldet.
function quantityOf(cart: CartQuantities, itemId: string): number {
  return new Map(Object.entries(cart)).get(itemId) ?? 0;
}

// Setzt die Menge für einen Eintrag und liefert einen neuen Record. Menge
// 0 (oder negativ) entfernt den Eintrag, damit `toOrderItems` keine
// Null-Mengen produziert.
export function setQuantity(
  cart: CartQuantities,
  itemId: string,
  quantity: number,
): CartQuantities {
  const next = new Map<string, number>(Object.entries(cart));
  const clamped = clampQuantity(quantity);
  if (clamped === 0) {
    next.delete(itemId);
  } else {
    next.set(itemId, clamped);
  }
  return Object.fromEntries(next);
}

export function incrementQuantity(cart: CartQuantities, itemId: string): CartQuantities {
  return setQuantity(cart, itemId, quantityOf(cart, itemId) + 1);
}

export function decrementQuantity(cart: CartQuantities, itemId: string): CartQuantities {
  return setQuantity(cart, itemId, quantityOf(cart, itemId) - 1);
}

export function totalQuantity(cart: CartQuantities): number {
  return Object.values(cart).reduce((sum, quantity) => sum + quantity, 0);
}

export function isEmpty(cart: CartQuantities): boolean {
  return totalQuantity(cart) === 0;
}

// Mappt den Warenkorb auf das Backend-Schema OrderItemIn[]. Die
// Katalog-Referenz ergibt sich aus `source`: `base` → `base_item_id`,
// `tenant_own` → `tenant_extension_id` (genau-eine-Referenz, CHECK
// `exactly_one_ref`). Einträge ohne passendes Katalog-Item oder mit Menge
// 0 werden ausgelassen.
export function toOrderItems(cart: CartQuantities, items: ResolvedCatalogItem[]): OrderItemIn[] {
  const byId = new Map(items.map((item) => [item.id, item]));
  const result: OrderItemIn[] = [];
  for (const [itemId, quantity] of Object.entries(cart)) {
    if (quantity <= 0) continue;
    const item = byId.get(itemId);
    if (item === undefined) continue;
    if (item.source === "base") {
      result.push({ base_item_id: item.id, quantity });
    } else {
      result.push({ tenant_extension_id: item.id, quantity });
    }
  }
  return result;
}
