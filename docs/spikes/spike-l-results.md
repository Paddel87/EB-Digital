# Spike L — Tile-Caching-Strategie Frontend: Messprotokoll + Prototyp-Konzept

- **Fahrplan-Referenz:** 5.4 (Phase 5, ERKUNDUNG — Prototyp)
- **Datum:** 2026-06-11
- **Status:** **ABGESCHLOSSEN** — Empirie vollständig; **Patrick-Freigabe am 2026-06-11**, fixiert als **ADR-024** in `docs/decisions.md`. Der ADR-Entwurf in Abschnitt 5 ist durch ADR-024 abgelöst und bleibt als Spike-Artefakt erhalten.
- **Zeitverbrauch:** ~1,5 h (innerhalb Zeitbox 8–10 h; die Messung war schneller als veranschlagt, weil MapTiler die offenen Fragen mit echten Headern direkt beantwortet)
- **Key-Hinweis:** Tests liefen mit einem temporären, von Patrick bereitgestellten MapTiler-API-Key (nach Spike-Abschluss rotiert; `.env` zurück auf Platzhalter, verifiziert byte-identisch mit `.env.example`).
- **Architektur-Kontext:** ADR-016 macht den **PWA-Service-Worker zur alleinigen Cache-Schicht** für Tile-Last-Glättung (kein serverseitiges Caching, kein nginx-Cache). MapLibre GL JS rendert Vektor-Tiles (ADR-014/Regel-017). Dieser Spike klärt die Workbox-Strategie und das Pre-Cache-Budget.

## 1. Gemessene MapTiler-Fakten (echte Header, streets-v2 / tiles v3)

| Fakt                                   | Messung                                                                      | Konsequenz                                                                                                       |
| -------------------------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| **Vektor-Tile-TTL**                    | `cache-control: public, max-age=14400` = **exakt 4 h**                       | bestätigt die `project-context.md`-Annahme empirisch                                                             |
| **Vektor-Tileset maxzoom**             | **15** (`tiles/v3/tiles.json`)                                               | z16+ wird von MapLibre **clientseitig overzoomt** — Pre-Cache-Budget ist bei z15 gedeckelt, keine z16/17-Fetches |
| **Tile-Format**                        | `application/x-protobuf`, gzip on-the-wire                                   | Service-Worker cacht die komprimierte Response 1:1                                                               |
| **Tile-Größe z14 (dichte Innenstadt)** | ~120 KB ø                                                                    | dichtester Zoom, Hauptbudget-Posten                                                                              |
| **Tile-Größe z15**                     | ~62 KB ø                                                                     | Detail-/Navigations-Zoom                                                                                         |
| **Tile-Größe z12/z13 (Übersicht)**     | ~56 / ~64 KB ø                                                               | klein, wenige Tiles                                                                                              |
| **Style-JSON**                         | 63 KB, 90 Layer, 4 statische Fontstacks                                      | einmalig pro Style                                                                                               |
| **Sprite @2x**                         | 94 KB                                                                        | einmalig                                                                                                         |
| **Glyph-Range 0-255 (Latin)**          | 83 KB                                                                        | deckt deutsche Umlaute/ß ab (Latin-1 Supplement); einmalig pro Fontstack/Range                                   |
| **Quelle der Tiles**                   | `https://api.maptiler.com/tiles/v3/{z}/{x}/{y}.pbf` (vom Style referenziert) | das ist der zu cachende Endpoint, **nicht** der `.png`-Raster-Pfad                                               |

## 2. Pre-Cache-Budget (gemessen + hochgerechnet)

Operationsraum = Bounding Box, die der Disponent beim Einsatz-Eröffnen aufspannt. Pre-Cache der Zoomstufen **z12–z15** (Übersicht bis Straßendetail; darüber overzoomt MapLibre aus z15).

| Operationsraum       | Fläche       | Tiles z12–15 | Vektor-Tiles | + statische Assets | **Pre-Cache gesamt** |
| -------------------- | ------------ | ------------ | ------------ | ------------------ | -------------------- |
| Innenstadt-Kern      | 2,8 × 3,3 km | 52           | 3,8 MB       | 0,4 MB             | **~4,2 MB**          |
| Großlage Stadtgebiet | 6,7 × 7,3 km | 159          | 11,7 MB      | 0,4 MB             | **~12,1 MB**         |

**Befund:** Selbst eine große Stadtgebiets-Großlage liegt bei ~12 MB. Das ist gegen mobile Storage-Quotas vernachlässigbar (Abschnitt 4). Der Pre-Cache des Operationsraums beim Schichtbeginn — der laut Fahrplan „kritische Hebel" — ist damit **uneingeschränkt machbar**.

## 3. Workbox-Strategie (zwei getrennte Entscheidungen)

### 3.1 Pre-Cache (der kritische Hebel)

Beim Schichtbeginn / Operationsraum-Beitritt lädt die Betreuer-PWA die Tile-Liste des Operationsraums (z12–15) plus die statischen Style-Assets explizit in den Cache (`cache.addAll(tileURLs)`), ausgelöst durch eine **bewusste Nutzeraktion** („Einsatzraum offline laden") mit Fortschrittsanzeige. Tile-Liste wird aus der Operations-Bounding-Box clientseitig berechnet (Slippy-Map-Formel, wie im Spike). Ergebnis: **near-100 % Hit-Rate** für jede Navigation im Operationsraum, auch im Funkloch — genau die Vision-Anforderung „offline-fähig für Karten-Tiles im aktuellen Einsatzraum".

### 3.2 Runtime-Strategie für Tiles außerhalb des Pre-Cache / nach Ablauf

Vergleich der beiden Workbox-Kandidaten unter den EB-Digital-Constraints (Funkloch = intermittierende Verbindung; ADR-016 = jeder Fetch trifft direkt MapTiler, kein Server-Cache davor; API-Budget):

|                   | `StaleWhileRevalidate`                                                                            | **`CacheFirst` + ExpirationPlugin**                       |
| ----------------- | ------------------------------------------------------------------------------------------------- | --------------------------------------------------------- |
| Offline-Verhalten | liefert Cache, **triggert aber immer einen Background-Fetch** → im Funkloch nutzlose Fehlversuche | liefert Cache **ohne Netz**, Fetch nur bei Miss/Ablauf ✅ |
| MapTiler-Budget   | jeder Tile-View = 1 Request (Revalidate) → teuer ohne Server-Cache                                | nur Cache-Misses erzeugen Requests ✅                     |
| Aktualität        | immer frisch                                                                                      | Tiles ändern sich selten (Straßennetz) — 4 h+ unkritisch  |

**Wahl: `CacheFirst` + ExpirationPlugin** für den Tile-Pfad. Begründung: Im Einsatz-Kontext zählt Offline-Robustheit und Budget-Schonung mehr als minutenaktuelle Tiles; das Straßennetz ändert sich über eine Schicht nicht.

### 3.3 TTL-Override (bewusste Abweichung vom Provider-`max-age`)

Der Provider-Header sagt 4 h — das ist eine generische Web-Caching-Vorgabe. Eine Schicht dauert länger; ein Betreuer im Funkloch muss ein vor 5 h pre-gecachtes Tile **trotzdem** sehen. Daher setzt der ExpirationPlugin `maxAgeSeconds` auf **Operationsdauer-Größenordnung (z. B. 24 h)** statt der 4 h zu folgen. **ADR-016-konform:** Die AGB-Restriktion betraf ausschließlich serverseitiges Multi-Client-Caching; per-End-User-Browser-/PWA-Caching ist ausdrücklich erlaubt — eine längere clientseitige Haltedauer ist davon gedeckt. `maxEntries`-Cap (z. B. 4.000 Tiles ≈ größer als jede Großlage) als LRU-Sicherung gegen unbegrenztes Wachstum bei langem Pannen-Umherfahren.

## 4. Mobile Storage-Quota (Referenz, nicht im Spike gemessen)

- **Chrome/Android (Chromium):** Cache Storage darf bis ~60 % des freien Geräte-Speichers nutzen, LRU-Eviction unter Druck pro Origin. 12 MB ist trivial.
- **Safari/iOS:** historisch restriktiver; aktuelle WebKit-Versionen erlauben mehrere hundert MB bis ~GB pro Origin, **aber 7-Tage-Eviction für PWAs, die 7 Tage nicht genutzt werden**. 12 MB passt; das Eviction-Risiko ist akzeptabel, weil Operationen zeitlich begrenzt sind und der Pre-Cache beim Schichtbeginn **ohnehin neu ausgelöst** wird.
- **Konsequenz:** Quota ist kein limitierender Faktor. Die Strategie muss nur den iOS-7-Tage-Eviction-Fall handhaben — was der Re-Pre-Cache beim Schichtbeginn automatisch tut. `navigator.storage.estimate()` wird vor dem Pre-Cache abgefragt, um bei absurd vollem Gerät eine Warnung statt eines stillen Fehlschlags zu zeigen.

## 5. ADR-Entwurf (wartet auf Freigabe)

**Tag:** `[ERKENNTNIS] [MODUL] [PERFORMANCE]`

- **Pre-Cache (kritischer Hebel):** explizit per Nutzeraktion beim Schichtbeginn, Tile-Liste z12–15 aus Operations-Bounding-Box, `cache.addAll()` + Fortschrittsanzeige; Budget gemessen 4–12 MB. Garantiert Offline-Tiles im Operationsraum (Vision-Anforderung).
- **Runtime-Strategie:** `CacheFirst` + ExpirationPlugin (statt `StaleWhileRevalidate`) — Offline-Robustheit + MapTiler-Budget schlagen Tile-Aktualität.
- **TTL:** clientseitige Haltedauer auf Operationsdauer (~24 h) statt Provider-4 h, ADR-016-konform (per-User-Cache erlaubt); `maxEntries`-LRU-Cap als Wachstumssicherung.
- **Quota:** unkritisch (12 MB ≪ Quota); `navigator.storage.estimate()`-Pre-Check; iOS-7-Tage-Eviction durch Re-Pre-Cache beim Schichtbeginn abgefedert.
- **Tooling:** Workbox 7.4.x via `vite-plugin-pwa` (bereits im Stack, `project-context.md` §3), `runtimeCaching`-Regel auf `api.maptiler.com/tiles/v3/.*`; Glyphs/Sprite/Style separater CacheFirst-Eintrag (selten, lange TTL).
- **Abgrenzung Einsatzkraft-PWA:** dünnerer Cache (seltener Aufruf, kein Schicht-Pre-Cache) — nur Runtime-CacheFirst, kein proaktiver Operationsraum-Pre-Cache.

**Reifegrad-Wirkung bei Freigabe:** `[OFFEN]`-Bereich „Tile-Caching-Strategie / Service-Worker" in `frontend-betreuer` → `[VORLÄUFIG]`; Implementierung in Phase 6.3 (produktive Karten + Offline-Cache), Beförderung auf `[BELASTBAR]` mit Playwright-Service-Worker-Smoke-Test.

**Folge-Pflichten bei Freigabe:** ADR `[ERKENNTNIS] [MODUL] [PERFORMANCE]`; 6.3-Scope um Pre-Cache-UX (Nutzeraktion + Fortschritt), Tile-Listen-Berechnung aus Operations-BBox, Workbox-`runtimeCaching`-Konfiguration und Playwright-Offline-Smoke ergänzen.

## 6. Bewusste Nicht-Entscheidungen

- **Kein Raster-Tile-Pfad** (`.png`): MapLibre rendert Vektor-Tiles; der Raster-Endpoint ist nicht relevant.
- **Kein eigener IndexedDB-Tile-Store:** Workbox + Cache Storage API decken den Bedarf; eigene Persistenz wäre Over-Engineering.
- **Kein Pre-Cache über z15 hinaus:** maxzoom 15, MapLibre overzoomt — z16+-Pre-Cache wäre wirkungslos.
- **Keine Hintergrund-Synchronisation der Tiles** (Background Sync API): widerspräche dem Funkloch-/Budget-Ziel; Tiles werden bewusst beim Schichtbeginn geladen, nicht kontinuierlich aufgefrischt.

## 7. Artefakte

- Mess-Rohdaten: `/tmp/spike-l/` (Wegwerf: style.json, Sample-Tiles) — nicht versioniert.
- Kein produktiver Code (reine curl/python3-Wegwerf-Messung, ERKUNDUNG-konform).
- MapTiler-Key: temporär, nach Abschluss rotiert; `.env` zurück auf Platzhalter.
