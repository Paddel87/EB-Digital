// Auth-Guard für alle Routen unter `(authed)/`. Lädt aktuelle Session über
// `GET /api/auth/me` und redirected unauthentifizierte Zugriffe nach /login
// (mit `next`-Query-Param für Post-Login-Rücksprung).
//
// Detail-Frage 3-A: Session-State ist In-Memory; bei Hard-Refresh wird hier
// re-hydriert. Detail-Frage 4-B: Route-Gruppen-Trennung — `(public)/`-Routen
// haben keinen Guard, `(authed)/`-Routen schon.

import { redirect } from "@sveltejs/kit";
import { ApiError } from "$lib/api/client";
import { me } from "$lib/api/auth";
import { setSession, clearSession } from "$lib/stores/session";
import type { LayoutLoad } from "./$types";

export const load: LayoutLoad = async ({ url }) => {
  try {
    const user = await me();
    setSession(user);
    return { user };
  } catch (cause) {
    clearSession();
    if (cause instanceof ApiError && cause.kind === "auth") {
      const next = url.pathname + url.search;
      const nextEncoded = encodeURIComponent(next);
      redirect(307, `/login?next=${nextEncoded}`);
    }
    throw cause;
  }
};
