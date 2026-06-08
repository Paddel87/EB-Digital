// Unit-Tests für das Catalog-API-Binding (S2b) in src/lib/api/catalog.ts.
// Der globale fetch wird gemockt — geprüft werden Pfad, Methode,
// URL-Encoding und Response-Parsing.

import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { fetchCatalog, type ResolvedCatalogItem } from "../src/lib/api/catalog";

function setFetchMock(impl: (input: string, init?: RequestInit) => Promise<Response>) {
  const mock = vi.fn(impl);
  vi.stubGlobal("fetch", mock);
  return mock;
}

const exampleItems: ResolvedCatalogItem[] = [
  {
    id: "base-1",
    base_item_id: null,
    source: "base",
    name: "Wasser",
    unit: "bottle",
    default_unit_label: "Flasche",
    description: null,
    category_id: "cat-1",
    category_name: "Getränke",
  },
];

describe("catalog binding", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("fetchCatalog GETs /api/anon/{token}/catalog and parses items", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify(exampleItems), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const result = await fetchCatalog("abc-token");
    expect(result).toEqual(exampleItems);
    const [path, init] = mock.mock.calls[0]!;
    expect(path).toBe("/api/anon/abc-token/catalog");
    expect((init as RequestInit).method).toBe("GET");
  });

  test("fetchCatalog URL-encodes the token segment", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify([]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    await fetchCatalog("a/b c+d");
    const [path] = mock.mock.calls[0]!;
    expect(path).toBe(`/api/anon/${encodeURIComponent("a/b c+d")}/catalog`);
  });
});
