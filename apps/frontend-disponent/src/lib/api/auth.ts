// Auth-API-Bindings für die in 2.2/2.4 produktiven Endpunkte unter
// /api/auth. Schemas spiegeln SessionUserResponse aus
// backend/eb_digital/auth/api.py (Schritt 2.2) — bei Backend-Vertragsänderung
// hier nachziehen.

import { apiGet, apiPost } from "$lib/api/client";

export type SubjectKind = "platform_admin" | "dispatcher" | "carer";

export interface SessionUser {
  kind: SubjectKind;
  id: string;
  username: string;
  tenant_id: string | null;
  expires_at: string;
}

export async function login(username: string, password: string): Promise<SessionUser> {
  const result = await apiPost<SessionUser>("/api/auth/login", { username, password });
  if (result === null) {
    throw new Error("Login response unexpectedly empty.");
  }
  return result;
}

export async function logout(): Promise<void> {
  await apiPost<null>("/api/auth/logout");
}

export async function me(): Promise<SessionUser> {
  return apiGet<SessionUser>("/api/auth/me");
}

export async function resetPassword(token: string, newPassword: string): Promise<void> {
  await apiPost<null>("/api/auth/reset-password", {
    token,
    new_password: newPassword,
  });
}
