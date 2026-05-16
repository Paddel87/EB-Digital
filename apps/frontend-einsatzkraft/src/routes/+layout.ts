// Schritt 2.6: SPA-Modus für die anonyme Einsatzkraft-PWA.
// `prerender = false` + `ssr = false` + `fallback: "index.html"`
// (svelte.config.js) ergibt eine reine Single-Page-App. Die dynamische
// Route `/[token]` ist beim Build-Zeitpunkt nicht prerenderbar
// (Operation-Tokens werden zur Laufzeit erzeugt), daher SPA. Diese
// Umstellung ersetzt die in 1.7 gesetzten `prerender = true; ssr = true;`
// — sie war für ein reines Skelett angemessen, ist aber für die
// AccessCode-Eingabe gegen die produktive S2a-Schnittstelle ungeeignet.

export const prerender = false;
export const ssr = false;
