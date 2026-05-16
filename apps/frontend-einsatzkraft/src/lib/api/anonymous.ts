// Anonymous-Session-API-Bindings für die in 2.3 produktive S2a unter
// /api/anon. Spiegelt die Pydantic-Schemas aus
// backend/eb_digital/auth_anonymous/api.py — bei Backend-Vertragsänderung
// hier nachziehen.

import { apiGet, apiPost } from "$lib/api/client";

export type OperationStatus = "planned" | "active" | "closed";

export interface OperationInfo {
  area_label: string;
  access_code_active: boolean;
  status: OperationStatus;
}

export interface AnonymousSessionResponse {
  session_id: string;
}

function infoPath(token: string): string {
  return `/api/anon/${encodeURIComponent(token)}/info`;
}

function sessionPath(token: string): string {
  return `/api/anon/${encodeURIComponent(token)}/session`;
}

export async function fetchInfo(token: string): Promise<OperationInfo> {
  return apiGet<OperationInfo>(infoPath(token));
}

export async function createSession(
  token: string,
  accessCode: string | null,
): Promise<AnonymousSessionResponse> {
  const result = await apiPost<AnonymousSessionResponse>(sessionPath(token), {
    access_code: accessCode,
  });
  if (result === null) {
    throw new Error("Session response unexpectedly empty.");
  }
  return result;
}
