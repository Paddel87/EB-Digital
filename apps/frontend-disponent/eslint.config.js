// ESLint Flat-Config für frontend-disponent.
// Pinning entspricht project-context.md Abschnitt 3+7 (eslint 10.3.x,
// typescript-eslint 8.59.x, eslint-plugin-svelte 3.17.x, eslint-plugin-
// security 4.0.x — Flat-Config-Linie).
// Identische Struktur in den drei Frontends — Inline statt shared-Import,
// weil shared-Imports aus dem Repo-Root die Plugin-Resolution zerschießen
// (jeder Workspace hat seinen eigenen node_modules-Pfad).

import js from "@eslint/js";
import tseslint from "typescript-eslint";
import sveltePlugin from "eslint-plugin-svelte";
import securityPlugin from "eslint-plugin-security";
import svelteParser from "svelte-eslint-parser";

// Browser-Globals inline (statt `globals`-Paket, das transitiv vorhanden,
// aber nicht direkt deklariert ist — pnpm-Workspace-Hygiene). Liste auf
// die in Phase 2 tatsächlich genutzten APIs beschränkt.
const browserGlobals = {
  fetch: "readonly",
  Response: "readonly",
  Request: "readonly",
  Headers: "readonly",
  URL: "readonly",
  URLSearchParams: "readonly",
  setTimeout: "readonly",
  clearTimeout: "readonly",
  setInterval: "readonly",
  clearInterval: "readonly",
  console: "readonly",
  document: "readonly",
  window: "readonly",
  SubmitEvent: "readonly",
  Event: "readonly",
  HTMLElement: "readonly",
  TypeError: "readonly",
};

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...sveltePlugin.configs["flat/recommended"],
  securityPlugin.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: browserGlobals,
    },
  },
  {
    files: ["**/*.svelte"],
    languageOptions: {
      parser: svelteParser,
      parserOptions: {
        parser: tseslint.parser,
      },
    },
  },
  {
    ignores: [
      "build/",
      ".svelte-kit/",
      "dist/",
      "node_modules/",
      "*.cjs",
      "vite.config.ts.timestamp-*",
    ],
  },
];
