// Build-Zeit-Konstanten aus vite.config.ts (`define`).
// Werden in der `/health`-Route angezeigt.

export const APP_NAME: string = __APP_NAME__;
export const BUILD_TIME: string = __BUILD_TIME__;
export const APP_VERSION = "0.1.0";
