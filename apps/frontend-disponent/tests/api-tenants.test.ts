// Unit-Tests für die Tenants-Bindings in src/lib/api/tenants.ts.

import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { listTenants } from "../src/lib/api/tenants";

function setFetchMock(impl: (input: string, init?: RequestInit) => Promise<Response>) {
  const mock = vi.fn(impl);
  vi.stubGlobal("fetch", mock);
  return mock;
}

const exampleTenant = {
  id: "abc",
  name: "DPolG Bayern",
  slug: "dpolg-bayern",
  status: "active",
  applied_at: "2026-05-10T08:30:00+00:00",
  activated_at: "2026-05-10T10:15:00+00:00",
  deactivated_at: null,
};

describe("listTenants", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
  });
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("gets /api/tenants without query when no status filter", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify([exampleTenant]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    const result = await listTenants();
    expect(result).toEqual([exampleTenant]);
    const [path] = mock.mock.calls[0]!;
    expect(path).toBe("/api/tenants");
  });

  test("appends ?status=active when filter is set", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify([exampleTenant]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    await listTenants("active");
    const [path] = mock.mock.calls[0]!;
    expect(path).toBe("/api/tenants?status=active");
  });

  test("url-encodes the status filter", async () => {
    const mock = setFetchMock(
      async () =>
        new Response(JSON.stringify([]), {
          status: 200,
          headers: { "Content-Type": "application/json" },
        }),
    );
    await listTenants("deactivated");
    const [path] = mock.mock.calls[0]!;
    expect(path).toBe("/api/tenants?status=deactivated");
  });
});
