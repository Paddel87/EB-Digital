// Vite-Konfig für frontend-einsatzkraft (Phase 1, Schritt 1.7).
// Schlanke anonyme PWA — Erstaufruf-Größe minimal (mobile, oft schlechtes
// Netz). Service-Worker ist Pflicht (Vision-Constraint Offline-Pufferung
// für Tiles im Sichtbereich), bleibt aber kleiner als bei Betreuer
// (kein Tile-Pre-Cache des gesamten Einsatzraums).

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
});
