// Auth-Guard für die Dashboard-Route nach erfolgreicher anonymer
// Anmeldung. Detail-Plan 2.6 Frage 4-B: separate Route, eigener Guard.
//
// Der Guard prüft, ob der In-Memory-Session-Store einen Eintrag für genau
// den aktuellen Token hat. Falls nicht (Hard-Refresh nach Tab-Verlust,
// Direkt-Aufruf der URL ohne vorherige Code-Eingabe), redirect zurück zur
// Token-Route für eine neue Anmeldung.

import { redirect } from "@sveltejs/kit";
import { getSession, isActiveForToken } from "$lib/stores/session";
import type { LayoutLoad } from "./$types";

export interface DashboardLayoutData {
  token: string;
  areaLabel: string;
}

export const load: LayoutLoad = async ({ params }): Promise<DashboardLayoutData> => {
  const token = params.token;
  if (!isActiveForToken(token)) {
    redirect(307, `/${token}`);
  }
  const session = getSession();
  // `isActiveForToken` garantiert non-null, aber TypeScript braucht den
  // expliziten Check.
  if (session === null) {
    redirect(307, `/${token}`);
  }
  return { token, areaLabel: session.areaLabel };
};
