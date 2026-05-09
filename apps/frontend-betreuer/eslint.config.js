// ESLint Flat-Config für frontend-betreuer.
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

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  ...sveltePlugin.configs["flat/recommended"],
  securityPlugin.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
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
