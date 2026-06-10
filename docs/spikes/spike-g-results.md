# Spike G — Sperrungs-Override-Technik: Messprotokoll (Teilstand)

- **Fahrplan-Referenz:** 5.1 (Phase 5, ERKUNDUNG)
- **Datum:** 2026-06-10
- **Status:** **TEILSTAND** — Valhalla-Vergleichsteil vollständig; TomTom-Empirie (T1/T2/T3) blockiert durch fehlenden API-Key (**Blocker #002**). ADR-Entwurf erst nach TomTom-Befunden finalisierbar.
- **Zeitverbrauch:** ~2 h (innerhalb Zeitbox 8–12 h)

## 1. Aufgabenstellung (Kurzfassung)

Patrick-Direktive 2026-05-17: Das System muss vom Routing-Provider als gesperrt geführte Straßen auf Disponenten-Freigabe **befahrbar machen** (Reverse-Override), nicht nur Straßen sperren (Override). Zwei Sperrungsarten:

- **(a) Traffic-basierte temporäre Sperrungen** (Echtzeit-Verkehrslage, `ROAD_CLOSURE`-Incidents).
- **(b) Permanente Sperrungen im Kartenmaterial** (Fußgängerzonen, Einbahnstraßen, bauliche Sperren).

## 2. TomTom-Empirie — BLOCKIERT

Probe-Requests am 2026-06-10 gegen Orbis Routing v2 (`apiVersion=2`) und Legacy Routing v1: beide `401 Unauthorized`. `.env` ist byte-identisch mit `.env.example` — kein echter `TOMTOM_API_KEY` im Arbeitsverzeichnis. Details und Klärungsfrage: `docs/blockers.md` Blocker #002. Die Szenarien T1/T2/T3 gegen TomTom stehen aus, sobald der Key vorliegt (geschätzter Bedarf: 30–60 Calls, Freemium-Tageslimit 2.500 reicht).

**Wissensstand TomTom (aus Recherche 2026-05-17, `project-context.md` §11, unverändert gültig, empirisch unbestätigt):**

- `avoidAreas`: nur Rechtecke, keine Polygone → für linienförmige Sperren nur als Approximation über multiple schmale Rechtecke.
- `supportingPoints`: Route-Rekonstruktion entlang Polyline — Kandidat für Reverse-Override, funktioniert mutmaßlich nur, wenn die Straße im Routing-Graph als prinzipiell befahrbar existiert. **Genau das ist bei Fußgängerzonen fraglich → empirischer Test zwingend.**
- `traffic=false`-Äquivalent für (a): Incidents ignorieren — global, nicht pro Strecke.

## 3. Valhalla-Vergleichstest — vollständig durchgeführt

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

- Valhalla **3.7.0** (`ghcr.io/valhalla/valhalla-scripted:latest`), OSM-Extract Bremen (Geofabrik, 20 MB), Tile-Build ~2 min auf Apple Silicon. Tiles + PBF liegen für Re-Runs unter `/tmp/spike-g/valhalla/custom_files`.

### 3.2 Szenario T2 — Fußgängerzone befahrbar machen (Reverse-Override, Sperrungsart b)

Testobjekt: Obernstraße/Unser Lieben Frauen Kirchhof, Bremen Innenstadt. Graph-Check via `/locate`: Edges tragen `car access: False`, `use: footway` — echte Fußgängerzone im Auto-Graph vorhanden, aber gesperrt.

| Lauf                                                               | Technik                                             | Ergebnis                                                                               |
| ------------------------------------------------------------------ | --------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Kurzstrecke auf der Zone (53.077349,8.804923 → 53.078478,8.802793) | Baseline (auto)                                     | 0,637 km Umfahrung via Martinistraße                                                   |
| dito                                                               | `costing_options.auto.ignore_access=true`           | **0,192 km direkt über Obernstraße — Befahrung erzwungen** ✅                          |
| Stadtquerung Domsheide → Ansgaritor                                | Baseline (auto)                                     | 2,133 km Umfahrung (südlich via Tiefer)                                                |
| dito                                                               | `ignore_access=true`, Endpunkte ohne `radius`       | **`442 No path`** — Snapping-Artefakt: Endpunkt rastet auf isoliertes Footway-Fragment |
| dito                                                               | `ignore_access=true` + `radius:30` an den Locations | **0,938 km direkt durch die Fußgängerzone** ✅                                         |

**Lehre Snapping-Disziplin:** Mit `ignore_access` werden auch Nicht-Auto-Kanten Snapping-Kandidaten. Der Adapter muss Location-`radius` (und ggf. `search_filter`) setzen, sonst sporadische 442-Fehler.

### 3.3 Szenario T3 — Einbahnstraße entgegen Fahrtrichtung (Reverse-Override, Sperrungsart b)

Testobjekt: Langenstraße (Einbahn-Asymmetrie empirisch verifiziert: hin 0,416 km / rück 0,106 km).

| Lauf                     | Technik               | Ergebnis                                                          |
| ------------------------ | --------------------- | ----------------------------------------------------------------- |
| Entgegen Einbahnrichtung | Baseline (auto)       | 0,416 km Umweg via Stintbrücke/Bredenstraße/Martinistraße         |
| Entgegen Einbahnrichtung | `ignore_oneways=true` | **0,106 km direkt entgegen der Einbahn — Befahrung erzwungen** ✅ |

### 3.4 Override — Straße sperren (Disponenten-Sperre)

Testobjekt: Martinistraße-Segment (Baseline 0,248 km direkt).

| Technik                                                  | Ergebnis                                                                                               |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `exclude_polygons` (Polygon **neben** der Kante)         | Route unverändert — **Sperre greift nur bei tatsächlichem Kanten-Schnitt** (Geometrie-Disziplin nötig) |
| `exclude_polygons` (30×30-m-Polygon **auf** Shape-Punkt) | **2,951 km Umweg via Wilhelm-Kaisen-Brücke — Sperre wirkt** ✅                                         |
| `exclude_locations` (Punkt auf Kante)                    | identisch 2,951 km — **Punkt-Sperre als leichtgewichtige Alternative zum Polygon** ✅                  |

**Lehre Geometrie-Disziplin:** Disponenten-Klick muss erst auf die Kante gematcht werden (`/locate`), bevor die Sperre gesetzt wird — sonst wirkungslose Sperren ohne Fehlermeldung. Valhalla akzeptiert beliebige Polygone (TomTom: nur Rechtecke).

### 3.5 Scoping-Risiko `ignore_*` und Gegenmittel (3-Call-Komposition)

`ignore_access`/`ignore_oneways` wirken **global pro Request** — die Route darf dann ÜBERALL beschränkte Segmente nutzen, nicht nur die freigegebene Strecke. Empirisch gezeigt: Stadtquerung mit globalem `ignore_access` wählte einen anderen, kürzeren Pfad über nicht freigegebene Bereiche (2,371 km statt Baseline 2,569 km, abweichender Straßenzug).

**Gegenmittel (getestet):** Komposition aus 3 Routing-Calls — Leg 1 normal bis Einfahrt der freigegebenen Strecke, Leg 2 mit `ignore_access` nur Einfahrt→Ausfahrt, Leg 3 normal ab Ausfahrt. Ergebnis: Override wirkt ausschließlich auf dem freigegebenen Segment (Gesamt 3,13 km, Leg 2 nutzt die Zone). Kosten: 3 interne Calls statt 1 — bei selbst gehostetem Valhalla **budget-irrelevant**, bei TomTom 3× API-Budget.

### 3.6 Sperrungsart (a) — Traffic-Sperrungen bei Valhalla

Selbst gehostetes Valhalla hat **per Default keinen Live-Traffic-Feed**: traffic-basierte Sperrungen existieren im Graph nicht. Konsequenz beidseitig: (a)-Reverse-Override ist trivial erfüllt (nichts zu überschreiben), aber die ETA kennt keine Verkehrslage, und disponenten-bekannte Real-Sperrungen MÜSSEN als `exclude_polygons`/`exclude_locations` eingespeist werden (funktioniert, 3.4). Die Disponenten-Sperrliste wird zur alleinigen Quelle der Wahrheit.

## 4. Zwischenstand Bewertungsmatrix (Stand: Valhalla empirisch, TomTom Rechercheständ)

| Kriterium                                     | TomTom (unbestätigt)                      | Valhalla (empirisch 2026-06-10)                                       |
| --------------------------------------------- | ----------------------------------------- | --------------------------------------------------------------------- |
| Reverse-Override Fußgängerzone (b)            | fraglich (`supportingPoints`, Test offen) | ✅ `ignore_access` (+ `radius`-Snapping)                              |
| Reverse-Override Einbahnstraße (b)            | fraglich (Test offen)                     | ✅ `ignore_oneways`                                                   |
| Sperre beliebiger Geometrie (Override)        | ⚠️ nur Rechtecke (`avoidAreas`)           | ✅ Polygone + Punkt-Sperren                                           |
| Scoping des Reverse-Override auf eine Strecke | unklar                                    | ⚠️ global pro Request; 3-Call-Komposition als Gegenmittel ✅          |
| Traffic-Sperrungen (a) ignorieren             | `traffic`-Parameter (Test offen)          | n/a (kein Traffic-Feed) — Disponenten-Sperrliste ersetzt              |
| Live-Verkehrslage für ETA                     | ✅ (Kern-Stärke)                          | ❌ ohne Zusatz-Feed                                                   |
| API-Budget pro Override                       | 1–3 Calls × Budget (ADR-016: kein Cache)  | 0 € (self-hosted); Betriebskosten: Container + monatliche OSM-Updates |
| Lizenz                                        | proprietär, ToS Clause 11.4               | MIT, OSM-Daten ODbL                                                   |
| Betriebsaufwand                               | 0 (SaaS)                                  | Container (~500 MB RAM Bremen), Geofabrik-Update-Pipeline             |

## 5. Offene Punkte bis ADR-Reife

1. **TomTom T1/T2/T3** nach Key-Eingang (Blocker #002): kann `supportingPoints` eine Fußgängerzone/Einbahnstraße wirklich erzwingen? Misserfolg wäre das K.-o.-Kriterium für „TomTom-only".
2. **Datenmodell-Skizze `route_override`** (Vorschlag, im ADR zu fixieren): `id`, `operation_id` (FK, CASCADE), `kind` (`block` | `allow`), `geometry` (Polyline/Punkt-Liste als JSONB, WGS84), `matched_edge_refs` (JSONB, provider-neutral), `created_by_dispatcher_id`, `created_at`, `expires_with_operation` (immer true in Phase 1), Audit-Log-Pflicht (Regel-012).
3. **Budget-Schätzung TomTom-Pfad:** Re-Routing pro Override ≈ 1–3 Calls; bei N aktiven Fahrzeugen im Einsatzraum multipliziert sich das pro Sperr-Änderung (jedes betroffene Fahrzeug ein Re-Route, 30-s-Throttle greift). Konkrete Zahl nach T-Tests.
4. **Hybrid-Option** für den ADR-Entwurf: TomTom für Normal-Routing + ETA (Verkehrslage), Valhalla-Container nur für Override-Routen (wo TomTom versagt) — erhöht Betriebskomplexität, umgeht aber das (b)-Risiko. Bewertung nach TomTom-Empirie.

## 6. Artefakte

- Mess-JSONs: `/tmp/spike-g/` (Wegwerf-Artefakte, nicht versioniert)
- Valhalla-Tiles für Re-Runs: `/tmp/spike-g/valhalla/custom_files/` (nach Reboot ggf. neu bauen, Setup 3.1)
- Kein produktiver Code entstanden (reine curl/python3-Wegwerf-Skripte, ERKUNDUNG-konform)
