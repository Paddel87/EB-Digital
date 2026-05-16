// Token-Route-Loader: ruft `GET /api/anon/{token}/info` beim Laden und
// reicht das Ergebnis (oder einen 404-Marker) an die Page weiter.
//
// Detail-Plan 2.6 Frage 1-A: Token als Pfad-Segment. Frage 2-A: keine
// manuelle URL-Eingabe — wenn der Token in der URL ungültig ist, zeigt
// die Page eine einheitliche Fehlermeldung ohne Info-Leak über den Grund
// (analog Backend-Verhalten: 404 für planned/closed/forged identisch).
//
// Andere Backend-Fehler (Network, 5xx) propagieren als SvelteKit-Error
// und werden vom Default-Error-Renderer behandelt.

import { ApiError } from "$lib/api/client";
import { fetchInfo, type OperationInfo } from "$lib/api/anonymous";
import type { LayoutLoad } from "./$types";

export interface TokenLayoutData {
  token: string;
  info: OperationInfo | null;
}

export const load: LayoutLoad = async ({ params }): Promise<TokenLayoutData> => {
  const token = params.token;
  try {
    const info = await fetchInfo(token);
    return { token, info };
  } catch (cause) {
    if (cause instanceof ApiError && cause.kind === "not-found") {
      return { token, info: null };
    }
    throw cause;
  }
};
