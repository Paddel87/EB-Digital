// Tenants-API-Bindings für die in 2.4 produktiven Endpunkte unter
// /api/tenants. Schemas spiegeln TenantResponse aus
// backend/eb_digital/tenants/api.py — bei Backend-Vertragsänderung hier
// nachziehen.

import { apiGet } from "$lib/api/client";

export type TenantStatus = "applied" | "active" | "deactivated";

export interface Tenant {
  id: string;
  name: string;
  slug: string;
  status: TenantStatus;
  applied_at: string;
  activated_at: string | null;
  deactivated_at: string | null;
}

export async function listTenants(status?: TenantStatus): Promise<Tenant[]> {
  const query = status === undefined ? "" : `?status=${encodeURIComponent(status)}`;
  return apiGet<Tenant[]>(`/api/tenants${query}`);
}
