# Spike G — Sperrungs-Override-Technik: Messprotokoll

- **Fahrplan-Referenz:** 5.1 (Phase 5, ERKUNDUNG)
- **Datum:** 2026-06-10 (Valhalla-Teil vormittags; TomTom-Teil nach Key-Eingang, Blocker #002 aufgelöst)
- **Status:** **Empirie vollständig** (T1/T2/T3 gegen TomTom Orbis v2 + Valhalla-Vergleich). ADR-Entwurf liegt unten vor — **wartet auf Freigabe**.
- **Zeitverbrauch:** ~3,5 h gesamt (innerhalb Zeitbox 8–12 h)
- **Key-Hinweis:** TomTom-Tests liefen mit einem temporären, von Patrick bereitgestellten API-Key (nach Spike-Abschluss gesperrt; `.env` zurück auf Platzhalter).

## 1. Aufgabenstellung (Kurzfassung)

Patrick-Direktive 2026-05-17: Das System muss vom Routing-Provider als gesperrt geführte Straßen auf Disponenten-Freigabe **befahrbar machen** (Reverse-Override), nicht nur Straßen sperren (Override). Zwei Sperrungsarten:

- **(a) Traffic-basierte temporäre Sperrungen** (Echtzeit-Verkehrslage, `ROAD_CLOSURE`-Incidents).
- **(b) Permanente Sperrungen im Kartenmaterial** (Fußgängerzonen, Einbahnstraßen, bauliche Sperren).

## 2. TomTom-Empirie (Orbis Routing API v2, `apiVersion=2`)

Smoke: Orbis v2 **und** Legacy v1 antworteten 200 — keine Orbis-Freischaltungs-Hürde. Alle Tests auf Orbis v2 (gepinnte Zielversion, `project-context.md` Abschnitt 5). API-Verbrauch des gesamten TomTom-Teils: **12 Routing-Calls + 1 Traffic-Call** (weit unter Freemium-Tageslimit 2.500).

### 2.1 Szenario T1 — Traffic-Sperrung befahrbar machen (Sperrungsart a) ✅

Testobjekt: realer `ROAD_CLOSURE`-Incident (iconCategory 8, „Gesperrt") auf der K347 Lange Straße bei Ganderkesee, gefunden via Traffic API `incidentDetails` (Bremen-Region: 154 Incidents, davon 96 Closures — Testlage am 2026-06-10).

| Lauf                 | Ergebnis                                                                     |
| -------------------- | ---------------------------------------------------------------------------- |
| `traffic=live`       | 2.321 m, 282 s — Routing **umfährt** die Live-Sperrung                       |
| `traffic=historical` | **204 m, 27 s — Routing ignoriert den Live-Incident, fährt direkt durch** ✅ |

**Aber:** `traffic` wirkt **global pro Request** — mit `historical` werden ALLE Live-Incidents ignoriert (auch Staus für die ETA), nicht nur die freigegebene Sperrung. Scoping nur über Leg-Komposition möglich (analog Abschnitt 3.5): Override-Segment mit `traffic=historical`, Rest mit `traffic=live` → 3 Calls statt 1.

### 2.2 Szenario T2 — Fußgängerzone befahrbar machen (Sperrungsart b) ❌ K.-o.-Befund

Testobjekt: Fußgängerzone Obernstraße/Unser Lieben Frauen Kirchhof, Bremen. Baseline Domsheide → Ansgaritor: **2.136 m** Umfahrung (Valhalla-Baseline: 2.133 m — deckungsgleiches Vermeidungsverhalten).

| Lauf                                                                  | Ergebnis                                                                                    |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `supportingPoints` (6 Punkte: Start, 4 auf der Zone, Ziel)            | 2.536 m — Map-Matching weicht auf befahrbare Parallelstraßen aus, **Zone nicht durchquert** |
| `supportingPoints` **dicht** (19 Punkte exakt auf der Zonen-Polyline) | 2.536 m — identisch, **Zone nicht durchquert** ❌                                           |

**Befund:** Die Route-Rekonstruktion via `supportingPoints` kann Kanten, die im TomTom-Routing-Graph für `travelMode=car` gesperrt sind, **nicht** erzwingen — auch nicht mit beliebig dichter Punktfolge. Es existiert kein öffentlicher API-Parameter, der Zufahrtsbeschränkungen aufhebt (kein Äquivalent zu Valhallas `ignore_access`).

### 2.3 Szenario T3 — Einbahnstraße entgegen Fahrtrichtung (Sperrungsart b) ❌

Testobjekt: Langenstraße Bremen (Einbahn). Baseline entgegen der Fahrtrichtung: 463 m Umweg (Valhalla: 416 m).

| Lauf                                                    | Ergebnis                                                   |
| ------------------------------------------------------- | ---------------------------------------------------------- |
| `supportingPoints` (5 Punkte entlang der Gegenrichtung) | 463 m — Umweg bleibt, **Gegenrichtung nicht erzwungen** ❌ |

### 2.4 Override — Straße sperren via `avoidAreas` ✅

Testobjekt: Martinistraße-Segment, Baseline 224 m direkt.

| Lauf                                                    | Ergebnis                                                        |
| ------------------------------------------------------- | --------------------------------------------------------------- |
| `avoidAreas`-Rechteck (~30×30 m) auf Routen-Mittelpunkt | **2.941 m Umweg — Sperre wirkt** ✅ (Valhalla-Pendant: 2.951 m) |

Einschränkung bleibt: nur Rechtecke — linienförmige/diagonale Sperren erfordern Multi-Rechteck-Approximation mit Präzisionsrisiko (Recherche-Befund 2026-05-17, durch die Rechteck-Mechanik bestätigt).

## 3. Valhalla-Vergleichstest (3.7.0, lokal, OSM Bremen)

### 3.1 Setup (reproduzierbar, ~5 min)

```bash
mkdir -p /tmp/spike-g/valhalla/custom_files
curl -sL -o /tmp/spike-g/valhalla/custom_files/bremen-latest.osm.pbf \
  https://download.geofabrik.de/europe/germany/bremen-latest.osm.pbf   # 20 MB
docker run -d --name spike-g-valhalla -p 8002:8002 \
  -v /tmp/spike-g/valhalla/custom_files:/custom_files \
  -e serve_tiles=True ghcr.io/valhalla/valhalla-scripted:latest
# Tile-Build Bremen: ~2 min; ready wenn GET :8002/status == 200
```

### 3.2 Szenario T2 — Fußgängerzone (Reverse-Override) ✅

Graph-Check via `/locate`: Obernstraße-Edges tragen `car access: False`, `use: footway`.

| Lauf                                | Technik                                             | Ergebnis                                                                               |
| ----------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Kurzstrecke auf der Zone            | Baseline (auto)                                     | 0,637 km Umfahrung via Martinistraße                                                   |
| dito                                | `costing_options.auto.ignore_access=true`           | **0,192 km direkt über Obernstraße** ✅                                                |
| Stadtquerung Domsheide → Ansgaritor | Baseline (auto)                                     | 2,133 km Umfahrung                                                                     |
| dito                                | `ignore_access=true`, Endpunkte ohne `radius`       | **`442 No path`** — Snapping-Artefakt: Endpunkt rastet auf isoliertes Footway-Fragment |
| dito                                | `ignore_access=true` + `radius:30` an den Locations | **0,938 km direkt durch die Fußgängerzone** ✅                                         |

**Lehre Snapping-Disziplin:** Mit `ignore_access` werden auch Nicht-Auto-Kanten Snapping-Kandidaten. Der Adapter muss Location-`radius` (und ggf. `search_filter`) setzen, sonst sporadische 442-Fehler.

### 3.3 Szenario T3 — Einbahnstraße (Reverse-Override) ✅

| Lauf                     | Technik               | Ergebnis                                                  |
| ------------------------ | --------------------- | --------------------------------------------------------- |
| Entgegen Einbahnrichtung | Baseline (auto)       | 0,416 km Umweg via Stintbrücke/Bredenstraße/Martinistraße |
| Entgegen Einbahnrichtung | `ignore_oneways=true` | **0,106 km direkt entgegen der Einbahn** ✅               |

### 3.4 Override — Straße sperren ✅

| Technik                                                  | Ergebnis                                                                                               |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `exclude_polygons` (Polygon **neben** der Kante)         | Route unverändert — **Sperre greift nur bei tatsächlichem Kanten-Schnitt** (Geometrie-Disziplin nötig) |
| `exclude_polygons` (30×30-m-Polygon **auf** Shape-Punkt) | **2,951 km Umweg — Sperre wirkt** ✅                                                                   |
| `exclude_locations` (Punkt auf Kante)                    | identisch — **Punkt-Sperre als leichtgewichtige Alternative** ✅                                       |

**Lehre Geometrie-Disziplin:** Disponenten-Klick muss erst auf die Kante gematcht werden (`/locate`), bevor die Sperre gesetzt wird. Valhalla akzeptiert beliebige Polygone (TomTom: nur Rechtecke).

### 3.5 Scoping-Risiko `ignore_*` und Gegenmittel (3-Call-Komposition)

`ignore_access`/`ignore_oneways` wirken **global pro Request**. Empirisch: Stadtquerung mit globalem `ignore_access` wählte einen kürzeren Pfad über nicht freigegebene beschränkte Segmente (2,371 km statt 2,569 km Baseline, abweichender Straßenzug). **Gegenmittel (getestet):** 3-Call-Komposition — Leg 1 normal bis Einfahrt, Leg 2 mit `ignore_access` Einfahrt→Ausfahrt, Leg 3 normal. Override wirkt dann ausschließlich auf dem freigegebenen Segment. Identische Mechanik funktioniert bei TomTom für (a) mit `traffic=historical` auf dem Override-Leg.

### 3.6 Sperrungsart (a) bei Valhalla

Selbst gehostetes Valhalla hat per Default **keinen Live-Traffic-Feed**: traffic-basierte Sperrungen existieren im Graph nicht. (a)-Reverse-Override ist trivial erfüllt (nichts zu überschreiben); Kehrseite: ETA ohne Verkehrslage, und real existierende Sperrungen muss der Disponent als `exclude_polygons`/`exclude_locations` pflegen (funktioniert, 3.4). Die Disponenten-Sperrliste wird zur alleinigen Quelle der Wahrheit — was dem Domänen-Modell entspricht: bei Großlagen kennt der Disponent die Absperrlage verlässlicher und früher als der Provider-Traffic-Feed.

## 4. Finale Bewertungsmatrix (alles empirisch, 2026-06-10)

| Kriterium                              | TomTom Orbis v2                                       | Valhalla 3.7.0 (self-hosted)                                                  |
| -------------------------------------- | ----------------------------------------------------- | ----------------------------------------------------------------------------- |
| Reverse-Override Traffic-Sperrung (a)  | ✅ `traffic=historical` (global → Komposition)        | n/a — kein Traffic-Feed, Anforderung entfällt strukturell                     |
| Reverse-Override Fußgängerzone (b)     | ❌ **nicht möglich** (supportingPoints verweigert)    | ✅ `ignore_access` (+ `radius`-Snapping)                                      |
| Reverse-Override Einbahnstraße (b)     | ❌ **nicht möglich**                                  | ✅ `ignore_oneways`                                                           |
| Sperre beliebiger Geometrie (Override) | ⚠️ nur Rechtecke (`avoidAreas`)                       | ✅ Polygone + Punkt-Sperren                                                   |
| Scoping des Override auf eine Strecke  | ⚠️ global; 3-Call-Komposition nötig                   | ⚠️ global; 3-Call-Komposition nötig (getestet)                                |
| Live-Verkehrslage für ETA              | ✅ (Kern-Stärke)                                      | ❌ ohne Zusatz-Feed                                                           |
| API-Budget pro Override-Re-Route       | 1–3 Calls × Budget (ADR-016: kein Cache)              | 0 € (self-hosted)                                                             |
| Lizenz                                 | proprietär; ToS Clause 11.4; Preisänderung 2026-07-01 | MIT; Daten OSM/ODbL (Attribution-Pflicht)                                     |
| Betriebsaufwand                        | 0 (SaaS)                                              | Container (~500 MB RAM/Bremen; DE gesamt mehr) + monatliche Geofabrik-Updates |
| Provider-Wechsel-Aufwand               | Adapter-Tausch (ADR-014/Regel-017)                    | Adapter-Tausch (ADR-014/Regel-017)                                            |

## 5. ADR-Entwurf (wartet auf Freigabe)

**Kernbefund:** Die Anforderung „permanente Sperrungen auf Disponenten-Freigabe befahrbar machen" (Sperrungsart b — Fußgängerzonen, Einbahnstraßen; bei Großlagen-Einsätzen in Innenstädten der Regelfall) ist mit TomTom **nicht erfüllbar**. Damit zerfällt die Technik-Wahl in drei Optionen:

- **Option A — TomTom-only, Anforderung (b) streichen:** Reverse-Override nur für Traffic-Sperrungen (`traffic=historical`-Komposition); permanente Sperren bleiben unbefahrbar, Vision-Klarstellung nötig. Geringster Aufwand, aber Kern-Use-Case (Polizei-Freigabe durch Absperrung/Fußgängerzone) entfällt.
- **Option B — Routing-Wechsel auf Valhalla (self-hosted):** erfüllt (a) strukturell und (b) empirisch; Routing-Budget entfällt komplett (entlastet ADR-016-Folgen); TomTom-Vertrag, ToS-Clause-11.4-Restriktion und Preisänderungs-Risiko 2026-07-01 entfallen; passt zu Self-Hosting-Vision und ADR-014. Kosten: ETA ohne Live-Verkehrslage, Betrieb Container + monatlicher OSM-Update-Job, neue Abhängigkeit (Valhalla MIT, OSM-Daten ODbL — Lizenz-Prüfung nach Regel-016 nötig, Attribution-Pflicht). MapTiler (Tiles/Geocoding) bleibt unberührt.
- **Option C — Hybrid:** TomTom für Normal-Routing/ETA, Valhalla nur für Override-Routen. Erfüllt alles inkl. Live-ETA, aber zwei Engines parallel (Konsistenz-, Betriebs- und Test-Aufwand am höchsten).

**Empfehlung: B.** Begründung: (b) ist Kern-Use-Case und hart; der Live-Traffic-Verlust wiegt im Einsatz-Kontext wenig (der Disponent kennt die Absperrlage früher und verlässlicher als der Provider-Feed, Abschnitt 3.6); Budget-, Lizenz- und Souveränitäts-Effekte zahlen alle in bestehende Constraints ein (ADR-016, Vision Self-Hosting, ADR-014). Datenmodell-Skizze `route_override` (`kind`: `block` | `allow`, Geometrie + gematchte Kanten-Referenzen, einsatzgebunden, Audit-Pflicht Regel-012) siehe Abschnitt 6.

Freigabepflichtig nach CLAUDE.md §4 (Kategorien 3 + 7, Stack-Änderung ADR-002): Entscheidung liegt bei Patrick. Bei Freigabe B folgen: ADR `[ERKENNTNIS] [MODUL] [STACK] [PERFORMANCE]`, Folge-ADR Daten-Update-Pipeline (Geofabrik), Regel-016-Lizenzprüfung, Architektur-Update `backend/geo` + `infra/tile-proxy` (Routing-Pfad wird container-intern statt extern).

## 6. Datenmodell-Skizze `route_override` (für den ADR)

```
route_override
- id                          UUID PK
- operation_id                UUID FK → operation.id ON DELETE CASCADE  (einsatzgebunden, verfällt mit Einsatz-Ende)
- kind                        TEXT CHECK ('block' | 'allow')
- geometry                    JSONB  (Polyline bzw. Punkt-Liste, WGS84, vom Disponenten-Klickpfad)
- matched_refs                JSONB  (provider-neutral: gematchte Kanten-/Standort-Referenzen nach /locate-Disziplin, Abschnitt 3.4)
- created_by_dispatcher_id    UUID FK → dispatcher.id
- created_at                  TIMESTAMPTZ
```

Audit-Log-Pflicht (Regel-012): Anlage und Löschung eines Overrides sind routing-beeinflussende Disponenten-Aktionen → `operation_audit_log`-Action-Types `route_override_created` / `route_override_removed`. Budget-Hinweis: Bei Option B sind Override-Re-Routes budget-frei; die `geo_usage_daily`-Zählung (Abschnitt 6 `project-context.md`) reduziert sich auf MapTiler-Tiles/Geocoding.

## 7. Artefakte

- Mess-JSONs: `/tmp/spike-g/` (Wegwerf-Artefakte, nicht versioniert)
- Valhalla-Tiles für Re-Runs: `/tmp/spike-g/valhalla/custom_files/` (nach Reboot neu bauen, Setup 3.1)
- Kein produktiver Code entstanden (reine curl/python3-Wegwerf-Skripte, ERKUNDUNG-konform)
- TomTom-Key: temporär, nach Abschluss von Patrick gesperrt; `.env` wieder auf Platzhalter
