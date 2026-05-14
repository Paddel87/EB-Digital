// Schritt 2.5: SPA-Modus für die Auth-pflichtige App.
// `prerender = false` + `ssr = false` + `fallback: "index.html"`
// (svelte.config.js) ergibt eine reine Single-Page-App, in der Auth-State
// clientseitig in `src/routes/(authed)/+layout.ts` geladen wird. Diese
// Umstellung ersetzt die in 1.7 gesetzten `prerender = true; ssr = true;`
// — sie war für ein reines Skelett angemessen, ist aber für Login-Flows
// und Cookie-Round-Trip ungeeignet.

export const prerender = false;
export const ssr = false;
