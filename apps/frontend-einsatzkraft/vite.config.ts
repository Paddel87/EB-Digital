// Vite-Konfig für frontend-einsatzkraft.
//
// Phase 1 (Schritt 1.7): Schlanke anonyme PWA — Erstaufruf-Größe minimal
// (mobile, oft schlechtes Netz). Service-Worker ist Pflicht
// (Vision-Constraint Offline-Pufferung für Tiles im Sichtbereich), bleibt
// aber kleiner als bei Betreuer (kein Tile-Pre-Cache des gesamten
// Einsatzraums).
//
// Phase 2 (Schritt 2.6): Dev-Proxy für `/api`-Pfade auf das Backend
// (Compose-Stack auf localhost:8000), damit Cookies same-origin laufen
// (analog frontend-disponent in 2.5). In Production übernehmen
// Caddy + nginx das Path-Routing. Ziel über VITE_BACKEND_URL
// überschreibbar — Default deckt den Standard-Compose-Stack ab.

import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig, loadEnv } from "vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");
  const backendUrl = env.VITE_BACKEND_URL ?? "http://localhost:8000";

  return {
    plugins: [
      sveltekit(),
      VitePWA({
        strategies: "generateSW",
        registerType: "prompt",
        manifest: {
          name: "EB Digital Einsatzkraft",
          short_name: "EB Einsatz",
          description: "Anonyme Bestell-PWA für Einsatzkräfte im Außendienst.",
          lang: "de",
          start_url: "/",
          display: "standalone",
          background_color: "#ffffff",
          theme_color: "#1f2937",
          icons: [],
        },
        workbox: {
          navigateFallback: "/",
          runtimeCaching: [
            {
              urlPattern: /\/api\/anon\/.*/i,
              handler: "NetworkFirst",
              options: {
                cacheName: "anon-api-cache",
                networkTimeoutSeconds: 5,
                expiration: { maxEntries: 50, maxAgeSeconds: 4 * 60 * 60 },
                cacheableResponse: { statuses: [0, 200] },
              },
            },
          ],
        },
      }),
    ],
    define: {
      __APP_NAME__: JSON.stringify("frontend-einsatzkraft"),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },
    server: {
      port: 5175,
      proxy: {
        // `ws: true` proxyt auch den WebSocket-Pfad /api/ws/anon/{token}
        // (S9, Schritt 4.5) same-origin auf das Backend; ohne das Flag
        // leitet Vite nur HTTP weiter. In Production routet Caddy/nginx.
        "/api": {
          target: backendUrl,
          changeOrigin: true,
          secure: false,
          ws: true,
        },
      },
    },
  };
});
