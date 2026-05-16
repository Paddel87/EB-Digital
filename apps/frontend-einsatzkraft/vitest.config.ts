// Vitest-Konfig für frontend-einsatzkraft.
// Wir laden hier bewusst NICHT den vollen SvelteKit-Plugin — er würde
// jsdom + Svelte-Compiler-Setup verlangen (neue Top-Level-Deps,
// freigabepflichtig). Stattdessen testen wir die TypeScript-Module
// direkt und mocken `fetch` per `vi.stubGlobal`. Komponenten-Tests
// folgen mit Playwright in Phase 7 (project-context.md Abschnitt 7).
//
// Der `$lib`-Alias entspricht der SvelteKit-Konvention: `src/lib/...`.

import path from "node:path";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: {
      $lib: path.resolve(__dirname, "src/lib"),
    },
  },
  test: {
    include: ["tests/**/*.test.ts"],
    environment: "node",
    coverage: {
      provider: "v8",
      reporter: ["text"],
    },
  },
});
