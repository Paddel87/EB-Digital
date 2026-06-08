// Unit-Tests für die Standorterfassung in src/lib/location.ts. Das
// `geolocation`-Objekt wird injiziert (kein globales navigator-Mutieren).

import { describe, expect, test } from "vitest";
import { getCurrentPosition, GeolocationError } from "../src/lib/location";

interface FakeError {
  code: number;
  PERMISSION_DENIED: number;
  POSITION_UNAVAILABLE: number;
  TIMEOUT: number;
}

function fakeError(code: number): FakeError {
  return { code, PERMISSION_DENIED: 1, POSITION_UNAVAILABLE: 2, TIMEOUT: 3 };
}

function geoWithSuccess(lat: number, lng: number, accuracy: number): Geolocation {
  return {
    getCurrentPosition: (success: PositionCallback) => {
      success({ coords: { latitude: lat, longitude: lng, accuracy } } as GeolocationPosition);
    },
    watchPosition: () => 0,
    clearWatch: () => {},
  } as unknown as Geolocation;
}

function geoWithError(code: number): Geolocation {
  return {
    getCurrentPosition: (_success: PositionCallback, error?: PositionErrorCallback) => {
      error?.(fakeError(code) as unknown as GeolocationPositionError);
    },
    watchPosition: () => 0,
    clearWatch: () => {},
  } as unknown as Geolocation;
}

describe("getCurrentPosition", () => {
  test("resolves with lat/lng/accuracy on success", async () => {
    const result = await getCurrentPosition(geoWithSuccess(53.07, 8.8, 14.2));
    expect(result).toEqual({ lat: 53.07, lng: 8.8, accuracyM: 14.2 });
  });

  test("rejects with 'unsupported' when geolocation is missing", async () => {
    await expect(getCurrentPosition(undefined)).rejects.toMatchObject({ kind: "unsupported" });
  });

  test("maps PERMISSION_DENIED to 'permission'", async () => {
    await expect(getCurrentPosition(geoWithError(1))).rejects.toMatchObject({ kind: "permission" });
  });

  test("maps TIMEOUT to 'timeout'", async () => {
    await expect(getCurrentPosition(geoWithError(3))).rejects.toMatchObject({ kind: "timeout" });
  });

  test("maps POSITION_UNAVAILABLE to 'unavailable'", async () => {
    const error = await getCurrentPosition(geoWithError(2)).catch((cause: unknown) => cause);
    expect(error).toBeInstanceOf(GeolocationError);
    expect((error as GeolocationError).kind).toBe("unavailable");
  });
});
