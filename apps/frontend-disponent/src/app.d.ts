// SvelteKit-Typen-Augmentation. Konkrete App-Properties (Locals, PageData,
// PageState, Platform) folgen ab Phase 2.

declare global {
  namespace App {
    // interface Error {}
    // interface Locals {}
    // interface PageData {}
    // interface PageState {}
    // interface Platform {}
  }

  // Werte aus vite.config.ts `define` (Build-Zeit-Konstanten).
  const __APP_NAME__: string;
  const __BUILD_TIME__: string;
}

export {};
