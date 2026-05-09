// SvelteKit-Konfiguration für frontend-disponent.
// adapter-static, weil das Frontend als statisches Bundle hinter Caddy
// ausgeliefert wird (architecture.md Abschnitt 2). Phase 1: keine
// dynamischen Routen — `prerender` per Default an, Fallback `index.html`
// für Client-Seitiges Routing.

import adapter from "@sveltejs/adapter-static";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";

/** @type {import("@sveltejs/kit").Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    adapter: adapter({
      pages: "build",
      assets: "build",
      fallback: "index.html",
      precompress: false,
      strict: true,
    }),
  },
};

export default config;
