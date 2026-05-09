// Vite-Konfig für frontend-betreuer (Phase 1, Schritt 1.7).
// PWA-Aktivierung Pflicht (Vision-Constraint Offline-Pufferung). Workbox-
// Konfiguration in Phase 1 minimal: NetworkFirst für `/api/*`-Calls. Der
// Service-Worker bereitet das Skelett für Spike L (Tile-Caching-Strategie)
// und Phase 6 (`backend/realtime`-Auftrags-Pufferung) vor.
//
// Wir nutzen `vite-plugin-pwa` direkt (verifiziert in `project-context.md`
// Abschnitt 3); SvelteKit-spezifische Wrapper bleiben optional und werden
// per ADR aufgenommen, falls die Direktnutzung in Phase 6 zu eng wird.

import { sveltekit } from "@sveltejs/kit/vite";
import { defineConfig } from "vite";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig({
  plugins: [
    sveltekit(),
    VitePWA({
      strategies: "generateSW",
      registerType: "prompt",
      manifest: {
        name: "EB Digital Betreuer",
        short_name: "EB Betreuer",
        description: "Mobile-PWA für Betreuungsfahrzeuge im Einsatz.",
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
            urlPattern: /\/api\/.*/i,
            handler: "NetworkFirst",
            options: {
              cacheName: "api-cache",
              networkTimeoutSeconds: 5,
              expiration: { maxEntries: 100, maxAgeSeconds: 24 * 60 * 60 },
              cacheableResponse: { statuses: [0, 200] },
            },
          },
        ],
      },
    }),
  ],
  define: {
    __APP_NAME__: JSON.stringify("frontend-betreuer"),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },
});
