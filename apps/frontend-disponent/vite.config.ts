// Vite-Konfig für frontend-disponent (Phase 1, Schritt 1.7).
// Disponent läuft im stationären Lagezentrum mit stabiler Verbindung —
// keine PWA-Aktivierung in Phase 1 (project-context.md Abschnitt 2 +
// fahrplan.md Schritt 1.7 Notiz). Spike L (Tile-Caching-Strategie) und
// optionale Disponent-PWA werden in Phase 6 evaluiert.

import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [sveltekit()],
  define: {
    __APP_NAME__: JSON.stringify("frontend-disponent"),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
});
