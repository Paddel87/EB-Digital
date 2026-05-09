// Static-Adapter: alle Routen Build-Zeit prerendern. SSR aktiv lassen, damit
// die generierten HTML-Snapshots vollständig sind. Phase 2+ kann pro Route
// dynamisch SSR/CSR umschalten.

export const prerender = true;
export const ssr = true;
