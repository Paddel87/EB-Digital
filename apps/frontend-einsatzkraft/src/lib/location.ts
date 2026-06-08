// Standorterfassung via Browser-Geolocation (Detail-Plan 4.5-4A).
//
// GPS wird ausschließlich auf explizite Nutzeraktion angefordert (kein
// Auto-Prompt beim Laden) — Niederschwelligkeit + DSGVO-Transparenz
// (Vision). Die Genauigkeit (`accuracy_m`) wird mitgeliefert, weil sie die
// Plausibilitätsprüfung steuert (ADR-017: fehlende/zu grobe Genauigkeit →
// Moderation). Text-Standort ist die Alternative ohne GPS.
//
// Reine TS-Datei ohne Svelte-Runes — testbar mit einem gemockten
// `navigator.geolocation`.

export type GeolocationErrorKind =
  | "unsupported" // navigator.geolocation nicht vorhanden
  | "permission" // Nutzer hat Freigabe verweigert
  | "unavailable" // Position nicht bestimmbar
  | "timeout"; // Zeitüberschreitung

export class GeolocationError extends Error {
  readonly kind: GeolocationErrorKind;

  constructor(kind: GeolocationErrorKind, message: string) {
    super(message);
    this.name = "GeolocationError";
    this.kind = kind;
  }
}

export interface GpsPosition {
  lat: number;
  lng: number;
  accuracyM: number;
}

const DEFAULT_TIMEOUT_MS = 10_000;

function mapPositionError(error: GeolocationPositionError): GeolocationError {
  if (error.code === error.PERMISSION_DENIED) {
    return new GeolocationError("permission", "Standortfreigabe verweigert.");
  }
  if (error.code === error.TIMEOUT) {
    return new GeolocationError("timeout", "Standortbestimmung hat zu lange gedauert.");
  }
  return new GeolocationError("unavailable", "Standort konnte nicht bestimmt werden.");
}

// `geolocation` ist injizierbar, damit Tests nicht das globale
// `navigator` mutieren müssen.
export function getCurrentPosition(
  geolocation: Geolocation | undefined = typeof navigator !== "undefined"
    ? navigator.geolocation
    : undefined,
): Promise<GpsPosition> {
  if (geolocation === undefined) {
    return Promise.reject(
      new GeolocationError("unsupported", "Geolocation wird nicht unterstützt."),
    );
  }
  return new Promise<GpsPosition>((resolve, reject) => {
    geolocation.getCurrentPosition(
      (position) => {
        resolve({
          lat: position.coords.latitude,
          lng: position.coords.longitude,
          accuracyM: position.coords.accuracy,
        });
      },
      (error) => reject(mapPositionError(error)),
      { enableHighAccuracy: true, timeout: DEFAULT_TIMEOUT_MS, maximumAge: 0 },
    );
  });
}
