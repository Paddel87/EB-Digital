// Vite-Konfig für frontend-disponent (Phase 2, Schritt 2.5).
// Disponent läuft im stationären Lagezentrum mit stabiler Verbindung —
// keine PWA-Aktivierung in Phase 1 (project-context.md Abschnitt 2 +
// fahrplan.md Schritt 1.7 Notiz). Spike L (Tile-Caching-Strategie) und
// optionale Disponent-PWA werden in Phase 6 evaluiert.
//
// Dev-Proxy (2.5): `/api`-Pfade gehen auf das Backend (Compose-Stack auf
// localhost:8000), damit Cookies same-origin laufen. In Production
// übernehmen Caddy + nginx das Path-Routing. Ziel ist über die
// Environment-Variable VITE_BACKEND_URL überschreibbar — Default deckt
// den Standard-Compose-Stack ab.

import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendUrl = env.VITE_BACKEND_URL ?? "http://localhost:8000";

  return {
    plugins: [sveltekit()],
    define: {
      __APP_NAME__: JSON.stringify("frontend-disponent"),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },
    server: {
      port: 5173,
      proxy: {
        "/api": {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
        },
      },
    },
  };
});
