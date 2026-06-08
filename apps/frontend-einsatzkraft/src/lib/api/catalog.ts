// Catalog-API-Binding für die in 4.1 produktive S2b unter
// /api/anon/{operation_url}/catalog. Spiegelt das Pydantic-Schema
// ResolvedCatalogItem aus backend/eb_digital/catalog/schemas.py — bei
// Backend-Vertragsänderung hier nachziehen.
//
// Der Resolver liefert den effektiven Katalog der Operation, die zur
// aktiven anonymen Session gehört (Override-Items bereits einkomponiert).

import { apiGet } from "$lib/api/client";

// Eintrags-Herkunft: `base` (Basis- oder Override-Item) vs. `tenant_own`
// (eigenständiges Mandanten-Item). Steuert das Order-Item-Mapping
// (genau-eine-Referenz, siehe $lib/api/operations.ts).
export type CatalogItemSource = "base" | "tenant_own";

export interface ResolvedCatalogItem {
  id: string;
  base_item_id: string | null;
  source: CatalogItemSource;
  name: string;
  unit: string;
  default_unit_label: string;
  description: string | null;
  category_id: string;
  category_name: string;
}

function catalogPath(token: string): string {
  return `/api/anon/${encodeURIComponent(token)}/catalog`;
}

export async function fetchCatalog(token: string): Promise<ResolvedCatalogItem[]> {
  return apiGet<ResolvedCatalogItem[]>(catalogPath(token));
}
