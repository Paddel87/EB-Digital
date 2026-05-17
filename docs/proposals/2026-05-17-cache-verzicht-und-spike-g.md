# Vorschlags-Vorlagen: Cache-Verzicht-ADR + Spike-G-Neuzuschnitt

**Stand:** 2026-05-17
**Status:** WARTET AUF FREIGABE
**Auslöser:** Patrick-Direktiven in Session 2026-05-17:
1. „ich wäre bereit, auf Caching zu verzichten"
2. „Wichtig wäre es auch gesperrte Straßen trotzdem befahrbar zu machen"

**Zweck dieser Datei:** Beide Themen sind freigabepflichtige Architektur-Entscheidungen (CLAUDE.md §4 Punkt 1). Diese Datei sammelt die ausgearbeiteten Vorlagen, damit Patrick freigeben oder Anpassungen wünschen kann. Nach Freigabe wandert Vorlage 1 als ADR-016 in `decisions.md` (mit Folge-Edits in `architecture.md`, `project-context.md`, `fahrplan.md`), Vorlage 2 ersetzt den Schritt 5.1-Block in `fahrplan.md` (kein eigener ADR — Spike-Inhalts-Update ist Fahrplan-Pflege).

---

## Vorlage 1: ADR-016 (Entwurf) — Verzicht auf serverseitiges Caching vor externen Geo-Services

- **Datum:** 2026-05-17 (Entwurf)
- **Status:** Entwurf, wartet auf Freigabe
- **Tags-Vorschlag:** `[STRATEGISCH]` `[MODUL]` `[STACK]` `[PERFORMANCE]`
- **Phasentyp-Kontext:** UMSETZUNG (zwischen Schritt 2.7 ERLEDIGT und 3.1 OFFEN; strategische Klarstellung außerhalb der Schritt-Sequenz, ausgelöst durch Patrick-Direktive 2026-05-17).
- **Reifegrad-Wirkung:** Modul `infra/tile-proxy` Verantwortung ändert sich strukturell (Cache entfällt); Schnittstelle S7 (Geo → Tile-Proxy) bleibt `[VORLÄUFIG]` — wird in Phase 6 unter neuer Cache-freier Annahme zu `[BELASTBAR]` befördert. NFR-Eintrag „Tile-Caching ≥ 7 Tage TTL" wird ersetzt durch „Browser-/Service-Worker-Cache als alleinige Cache-Schicht".
- **Kategorie:** Architekturänderung (CLAUDE.md §4 Punkt 1) — strukturelle Aufgabe-Änderung des Moduls `infra/tile-proxy` plus Anpassung NFR Performance.
- **Kontext:**
  - **2026-05-10 (BEOBACHTUNG):** MapTiler Cloud Terms verbieten serverseitiges Caching ohne Sales-Approval. Geplanter 7-Tage-nginx-Cache wäre AGB-widrig. Triage: Sales-Anfrage als Phase-7-Roadmap-Meilenstein.
  - **2026-05-17 (Recherche):** TomTom ToS Clause 11.4 verbietet ebenfalls serverseitiges Multi-Client-Caching. Ein Provider-Wechsel löst das Cache-Problem **nicht** — beide Branchenführer haben dieselbe Constraint.
  - **2026-05-17 (Patrick-Direktive):** Bereitschaft, auf Caching zu verzichten. Damit ist eine architektur-saubere Lösung statt Sales-Verhandlungen wählbar.
  - Konsequenz: `infra/tile-proxy` muss neu definiert werden — entweder Cache mit Approval, oder kein Cache und vereinfachte Verantwortung.

- **Optionen:**
  - **A: Vollständiger Verzicht auf serverseitiges Caching.** `infra/tile-proxy` wird zum reinen Reverse-Proxy mit API-Key-Inject und Rate-Limit-Schutz; kein `proxy_cache_path`-Block. Browser-Cache (Default-TTL je Provider) und PWA-Service-Worker-Cache (Spike L) bleiben einzige Cache-Schichten.
    - **Konsequenzen:**
      - AGB-konform für MapTiler und TomTom; keine Sales-Verhandlung nötig.
      - Architektur vereinfacht; weniger Operations-Aufwand (kein nginx-Cache-Volume, keine Cache-Invalidierung).
      - Phase-7-Roadmap-Meilenstein „MapTiler-Sales-Anfrage" entfällt.
      - **API-Budget-Druck steigt deutlich.** Bei Großlage 500 Einsatzkräfte ohne Server-Cache vermutlich jenseits MapTiler-Flex-Tier ($25), realistisch Unlimited-Tier ($295/Monat) oder TomTom-Pay-as-you-grow mit Overage. Constraint „~50 €/Monat" aus `project-context.md` Abschnitt 6 ist dann nicht haltbar — Anpassung Pflicht.
      - Spike L (Phase 5) wird kritischer Hebel: Service-Worker-Pre-Cache des Operations-Raums vor Schichtbeginn reduziert API-Hit-Rate erheblich.
      - PWA-Offline-Tauglichkeit profitiert (Client-Cache ist ohnehin im Service Worker).
      - Risiko: keine Glättung von Tile-Request-Spitzen, jeder Cold-Cache-Browser triggert vollen Tile-Request-Schwall.

  - **B: Sales-Approval-Pfad weiter verfolgen (Status quo).** MapTiler-Sales-Anfrage als Phase-7-Meilenstein behalten, mit Zusatz-Fee verhandeln; TomTom-Routing-Cache als Backend-Performance-Cache argumentieren (Graubereich).
    - **Konsequenzen:**
      - Cache erlaubt, ~50 €/Monat-Budget hält mit Flex-Tier + Cache-Hit-Rate.
      - Sales-Aufwand, mögliche Zusatz-Fees (Höhe unbekannt), erhöhte Provider-Bindung.
      - TomTom-Cache-Graubereich bleibt — separate Klärung mit TomTom-Support nötig.
      - Phase-6 ist eingangsblockiert, bis Sales-Antworten vorliegen.
      - Architektur bleibt komplex (nginx-Cache-Konfiguration, Cache-Invalidierung bei Provider-Updates).

  - **C: Self-Hosting-Schwenk (Pfad-C aus ADR-014).** Tiles selbst hosten (OpenMapTiles + tileserver-gl auf OSM-Extracts); Geocoding und Routing extern lassen.
    - **Konsequenzen:**
      - Keine API-Constraints mehr für Tiles; Tile-Volumen ist der Hauptbudget-Hebel.
      - Hoher operativer Aufwand: 10–30 GB Storage für DE-Vektor-Tiles, Update-Pipeline (monatliche Geofabrik-Extracts), Style-Pflege, Server-Last.
      - Daten-Qualität merklich unter MapTiler Cloud (POI-Dichte, Hausnummern-Vollständigkeit).
      - Adapter-Tausch ist nach ADR-014/Regel-017 strukturell möglich.
      - Modulgrößen-Schub: `infra/tile-proxy` wächst zur eigenständigen Tile-Server-Komponente — ggf. Reklassifikation `infra/tile-server`.

- **Empfehlung:** **Option A** — Verzicht auf serverseitiges Caching.
  - **Begründung:** Patrick hat Bereitschaft signalisiert, das Budget-Constraint anzupassen statt Architektur-/Vertrags-Komplexität aufzubauen. Option A ist die AGB-saubere Lösung mit der einfachsten Architektur. Service-Worker-Caching (Spike L) glättet einen Großteil der Last. Option C bleibt als Eskalation offen, falls die nachfolgende Budget-Messung im Phase-7-Lasttest zeigt, dass Unlimited-Tier nicht tragbar ist; Option C ist dann Adapter-Tausch ohne Architektur-Umbau (ADR-014 trägt).

- **Folgeänderungen bei Freigabe (Diff-Skizze):**

  1. **`docs/decisions.md`:**
     - ADR-016 mit obigem Inhalt anlegen (Aktiv, Tags `[STRATEGISCH]`).
     - Teil A: ADR-Übersicht-Tabelle erweitern.
     - Teil A: Reaktiv-Quote-Block — neue Quote 1/10 = 10 % bleibt (ADR-007–ADR-016, neuer ADR ist `[STRATEGISCH]`, kein `[REAKTIV]`).
     - Teil C: ggf. Regel-019 „Externe-Service-Cache-Verzicht" — nicht zwingend, da Cache-Frage provider-spezifisch ist; aber Regel-016 (Sub-Dep-Lizenzprüfung) als Verwandt referenzieren.

  2. **`docs/architecture.md`:**
     - **Abschnitt 1 (Überblick) Kommunikations-Grundmodi:** Bullet „HTTP synchron Backend → externe Karten-/Routing-Services ausschließlich über `infra/tile-proxy`" um Klarstellung ergänzen: „... als API-Key-Inject und Rate-Limit-Schutz, **ohne serverseitiges Multi-Client-Cache** (ADR-016)".
     - **Abschnitt 3 Modul `infra/tile-proxy`:** Verantwortung umformulieren: kein Cache, nur API-Key-Inject + Rate-Limit + Reverse-Proxy-Routing. Reifegrad bleibt `[VORLÄUFIG]`; wird in Phase 6 erstmals umgesetzt.
     - **Abschnitt 4 Schnittstelle S7 (Geo → Tile-Proxy):** Antwort-Cache-Header-Behandlung dokumentieren — `infra/tile-proxy` reicht `Cache-Control`-Header vom Upstream-Provider 1:1 an den Client weiter, Browser-Cache greift damit gemäß Provider-Default.
     - **Abschnitt 6 NFRs:** Sub-Sektion „Performance" anpassen — Tile-Caching-Regel umformulieren: alleinige Cache-Schicht = Browser + Service Worker (Workbox in PWA, Spike L). Kein nginx-Cache.
     - **Abschnitt 8 Verworfene Alternativen:** „MapTiler-Sales-Approval mit Zusatz-Fee" und „Self-Hosting tileserver-gl in Phase 1" als bewusst verworfen (Pfad-B/C aus ADR-014) erwähnen; Pfade bleiben als Eskalations-Optionen offen.
     - **Abschnitt 9 Reifegrad-Übersicht:** Modul `infra/tile-proxy`-Zeile aktualisieren (neue Verantwortung); ADR-016-Verweis.

  3. **`docs/project-context.md`:**
     - **Abschnitt 6 Performance:**
       - Bullet „**Tile-Caching:** statische Tiles ≥ 7 Tage TTL, mandanten-/einsatz-übergreifend" → ersetzen durch: „**Tile-Caching:** kein serverseitiges Caching im Backend (AGB-Konform, ADR-016). Browser-Default-TTL gemäß Provider-`Cache-Control`-Header, plus PWA-Service-Worker-Pre-Cache des Operations-Raums (Spike L)."
       - Bullet „**Routing-Aufrufe:** maximal 1 pro Auftrag, frühestens 30 s erneut für dasselbe Fahrzeug; Cache von Routen für identische (Start, Ziel)-Paare im 60-s-Fenster." → 60-s-Cache streichen (gleicher AGB-Konflikt bei TomTom Clause 11.4). Stattdessen: „... — kein Backend-Cache; Wiederholungs-Schutz ausschließlich über das 30-s-Fahrzeug-Throttle im Adapter."
       - Bullet „**API-Budget Externdienste:** ~50 €/Monat" — als „**API-Budget Externdienste:** initial ~50 €/Monat, **vor Phase-7-Lasttest neu zu validieren** unter neuer Cache-freier Annahme (ADR-016). Verbrauchszähler im `backend/geo`-Modul Pflicht; Budget-Anhebung als ADR-pflichtige Entscheidung nach Messung."
     - **Abschnitt 11 (offene Grundsatzfragen):** TomTom-Provider-Strategie-Eintrag von 2026-05-17 ergänzen um Hinweis „MapTiler-AGB-Cache-Konflikt durch ADR-016 obsolet; Routing-Caching-Graubereich durch ADR-016 obsolet."

  4. **`docs/fahrplan.md`:**
     - **Phase 1 Schritt 1.8 (bereits ERLEDIGT) — `nginx.conf`-Stub:** kein Update nötig (Phase-1-Stub liefert ohnehin 204; Phase-6-Implementierung greift Cache-freie Definition).
     - **Phase 5 Schritt 5.4 (Spike L):** Klarstellung ergänzen — Service-Worker-Pre-Cache des Operations-Raums vor Schichtbeginn ist nun **die einzige cache-seitige Last-Glättung**, damit erhöhter Stellenwert. Zeitbox 6–8 h ggf. auf 8–10 h erweitern.
     - **Phase 6 Schritt 6.1 (`backend/geo`):** „Tile-Cache-Steuerung" streichen (entfällt mit ADR-016); ersetzen durch „Cache-Control-Header-Pass-Through".
     - **Phase 7 (Roadmap-Meilensteine):** „MapTiler-Sales-Anfrage"-Meilenstein streichen (mit Verweis auf ADR-016).
     - **Phase 7 Schritt 7.1 (Lasttest):** Erweitern um „API-Budget-Validierung unter Cache-freier Annahme — Verbrauchszähler-Messung über simulierte Großlagen-Last; Budget-Anhebungs-Vorschlag bei Bedarf als ADR".

  5. **`docs/logbuch.md`:**
     - BEOBACHTUNG-Eintrag 2026-05-17 mit dem Befund „TomTom-Recherche zeigt: gleiche Cache-AGB-Constraint bei MapTiler und TomTom" → bereits angelegt.
     - Nach ADR-Freigabe: neuer Eintrag mit ADR-016-Referenz und Folge-Edit-Auflistung.

- **Was Option A NICHT betrifft:**
  - **`backend/geo`-Adapter-Struktur:** bleibt unverändert. Adapter ruft Provider, gibt Antwort an den Client zurück. Kein internes Caching.
  - **PWA-Service-Worker-Caching (Spike L):** bleibt unverändert geplant; ist Client-Cache, AGB-konform.
  - **`infra/tile-proxy` als Modul-Existenz:** bleibt erhalten. Es entfällt nur die Cache-Logik. API-Key-Inject und Rate-Limit-Schutz bleiben.
  - **Adapter-Pattern aus ADR-014/Regel-017:** unverändert. Provider-Wechselbarkeit ist orthogonal zur Cache-Frage.

- **Reaktiv-Quote-Wirkung:** ADR-016 ist `[STRATEGISCH]` (Patrick-Direktive, nicht Bug-getrieben). Quote bleibt 1/10 = 10 % (zählt jetzt ADR-007 bis ADR-016). Unter 20 %-Schwellenwert.

- **Abgeleitete Regel:** keine neue Regel — ADR-014/Regel-017 deckt die übergeordnete Wechselbarkeit ab; ADR-016 ist eine konkrete Cache-Architektur-Entscheidung.

---

## Vorlage 2: Spike-G-Neuzuschnitt — Schritt 5.1 in `fahrplan.md`

- **Bisherige Fassung (`fahrplan.md` Zeile 977):**

  > **5.1** Spike G (Sperrungs-Override-Technik) – Schritt-Art Spike, Zeitbox 4–8 h. Klärt TomTom-Custom-Areas vs. Route-Bias vs. Penalty-Map, Datenbedarf bei Override-Pflege, API-Budget-Folgen. Ergebnis: ADR `[ERKENNTNIS] [MODUL] [PERFORMANCE]` mit Technikwahl.

- **Auslöser für den Neuzuschnitt:** Patrick-Direktive 2026-05-17 „Wichtig wäre es auch gesperrte Straßen trotzdem befahrbar zu machen". Bisheriger Spike-G-Zuschnitt war auf „Sperrung **hinzufügen**" geframet (Disponent markiert eine Strecke als gesperrt). Die neue Anforderung ist die _Umkehrung_: eine vom Routing-Provider als gesperrt geführte Straße muss trotzdem befahren werden können (Sondergenehmigung für Versorgungsfahrzeuge, Polizei-Durchfahrtsfreigabe, Fußgängerzonen-Befahrung).

- **Vorgeschlagene neue Fassung:**

  ### 5.1 Spike G — Sperrungs-Override-Technik (Override + Reverse-Override)

  - **Status:** OFFEN
  - **Phasentyp-Kontext:** ERKUNDUNG
  - **Schritt-Art:** Spike + Vergleichsstudie
  - **Zeitbox:** 8–12 h (erweitert gegenüber 4–8 h wegen Reverse-Override-Anforderung und Provider-Vergleich)
  - **Abhängigkeiten:** Phase 2 ERLEDIGT (Auth-Stack zur Adapter-Authentifizierung); ADR-014/Regel-017 (Provider-Neutralität).
  - **Freigabepflichtig:** nein (Spike-Schritt, ADR im Anschluss freigabepflichtig)
  - **Eingangskriterien:** TomTom-Recherche-Befunde aus `project-context.md` Abschnitt 11 (2026-05-17) gelesen; `avoidAreas`-Rechteck-Limit und `supportingPoints`-Mechanik verstanden; ADR-016 (falls vorher freigegeben) eingebunden — Cache-Verzicht beeinflusst API-Budget-Folgen pro Override-Technik.
  - **Zu klärende Fragen:**
    1. **Anforderungs-Präzisierung „Override":** Patrick-Direktive 2026-05-17 verlangt _Befahrbarkeit_ vom Routing-Provider als gesperrt geführter Straßen, nicht nur _Markierung_ als gesperrt. Spike trennt zwei Sperrungsarten:
       - **(a) Traffic-basierte temporäre Sperrungen** (Echtzeit-Verkehrslage, Baustellen, Polizei-Absperrungen) — über TomTom Traffic API als ROAD_CLOSURE-Incidents gemeldet.
       - **(b) Permanente Sperrungen im Kartenmaterial** (Fußgängerzonen, Einbahnstraßen entgegen Fahrtrichtung, bauliche Sperren) — fest im Routing-Graph.
    2. **TomTom-Techniken im konkreten Test (Provider-Eignung):**
       - `traffic=false` / `considerTraffic=false` für (a) — Traffic-Incidents ignorieren.
       - `avoidAreas` mit Rechteck-Liste für „großflächige Sperre" (z. B. Innenstadtblock) — Eignung für (a) und (b) prüfen.
       - `supportingPoints` mit Disponent-gesetzten Wegpunkten direkt auf der gesperrten Straße — Route-Rekonstruktion erzwingt Befahrung. Funktioniert nur, wenn Straße im Routing-Graph als befahrbar existiert (mit oder ohne Restriktion).
       - **Empirischer Test:** drei Test-Szenarien gegen TomTom mit den vier Techniken kombinieren:
         - Szenario T1: Echtzeit-Stau auf Hauptstraße → Befahrung erzwingen.
         - Szenario T2: Fußgängerzone Bremen-Innenstadt (Beispiel) → Befahrung erzwingen.
         - Szenario T3: Einbahnstraße entgegen Fahrtrichtung → Befahrung erzwingen.
    3. **Alternative Routing-Engines als Vergleichs-Kandidaten (NEU, durch Patrick-Direktive ausgelöst):**
       - **Valhalla** (Mapbox-Spin-off, OSS unter MIT/BSD, OSM-basiert): `exclude_polygons`, dynamische Edge-Penalties, Costing-Funktionen mit Konfiguration zur Befahrung restriktiver Wege. Erwarteter Vorteil bei (b).
       - **OSRM** (OSS, OSM-basiert): weniger flexibel als Valhalla, aber bewährt.
       - **Test der gleichen drei Szenarien T1/T2/T3** gegen Valhalla (lokales Demo-Setup mit OSM-Extract Bremen oder Bayern).
    4. **API-Budget-Folgen pro Technik:** jeder Override-Versuch ist ggf. ein zusätzlicher API-Call (Re-Routing). Mit ADR-016 (Cache-Verzicht) wird das relevanter. Messung pro Szenario.
    5. **Datenbedarf bei Override-Pflege:** wie speichert das System eine „trotzdem befahrbare Strecke"? Polylinie, Wegpunkt-Liste, Edge-Identifier? Wie ist die Disponent-UX (Klick auf Karte vs. Strecken-Editor)?
    6. **Persistenz des Datenmodells `route_override`:** Felder, Lebensdauer (einsatzgebunden), Audit-Log-Eintrag-Pflicht.
  - **Akzeptanzkriterien (wissensbasiert, ERKUNDUNG):**
    - Für jedes der drei Szenarien T1/T2/T3 ist dokumentiert, welche TomTom-Technik welches Ergebnis liefert (Erfolg/Misserfolg, mit gemessener API-Aufruf-Zahl).
    - Für (mindestens) Szenario T2 (permanente Sperrung) ist dokumentiert, ob TomTom hinreichend ist; falls nein, ist eine Alternative (Valhalla mit OSM-Extract) prototypisch getestet.
    - ADR-Entwurf liegt vor mit:
      - gewählter Override-Technik je Sperrungsart (a)/(b);
      - falls TomTom nicht hinreichend für (b): Empfehlung „Routing-Provider wechseln zu Valhalla" oder „Anforderung (b) als nicht erfüllbar streichen mit Vision-Klarstellung";
      - Datenmodell-Skizze `route_override`;
      - geschätzte API-Budget-Folgen.
  - **Betroffene Module:** `backend/geo` (Adapter; im Spike-Stadium als Wegwerf-Code), keine produktive Implementierung.
  - **Reifegrad-Wirkung am Phasen-Ende:**
    - `[OFFEN]`-Bereich „Sperrungs-Override-Technik" in `architecture.md` Modul `backend/geo` → `[VORLÄUFIG]` mit ADR-Verweis.
    - Schnittstelle S7 (Geo → Tile-Proxy) `[OFFEN]`-Anteil → `[VORLÄUFIG]`.
    - Falls Provider-Wechsel als ADR-Konsequenz: Modul `backend/geo` Adapter-Spec aktualisiert; ADR-014/Regel-017 trägt die Wechselbarkeit.
  - **Artefakte:**
    - `docs/decisions.md` neuer ADR `[ERKENNTNIS] [MODUL] [PERFORMANCE]` (ggf. zusätzlich `[STACK]`, falls Provider-Wechsel empfohlen).
    - `docs/architecture.md` Update `backend/geo` und ggf. `infra/tile-proxy`.
    - `docs/spikes/spike-g-results.md` (optional, falls Detail-Messprotokoll nicht in den ADR passt) — Test-Szenarien T1/T2/T3 mit Antworten/Routen/Counts.
  - **Notizen:**
    - Test gegen TomTom kann mit dem entwickler-eigenen API-Key des Plattform-Betreibers laufen (kein produktiver Mandanten-Bezug nötig).
    - Valhalla-Test kann mit Docker (`valhalla/valhalla:latest` plus DE-OSM-Extract) lokal aufgesetzt werden — Datenmenge für nur Bremen oder Bayern ist <2 GB.
    - Bei Wahl Valhalla: Folge-ADR zu Daten-Update-Pipeline (Geofabrik-Extracts, monatliche Frequenz) — nicht Teil von Spike G.

- **Folgeänderungen bei Freigabe:**
  1. **`docs/fahrplan.md` Zeile 977** durch obigen Schritt-Block ersetzen (im vollen Schritt-Format gemäß Schema in fahrplan.md Zeile 71–87).
  2. **`docs/fahrplan.md` Phasen-Übersicht-Tabelle** für Phase 5: Spike-Aufzählung „G, H, K, L, M" unverändert; falls Spike G provider-relevante Empfehlung produziert, wird er spätere Phase-6-Schritte beeinflussen (separater Folge-ADR).
  3. **`docs/architecture.md` Modul `backend/geo` Abschnitt „Offene Fragen":** Klarstellung „Sperrungs-Override umfasst (a) Traffic-Override + (b) Permanent-Override — siehe Spike G".
  4. **Reaktiv-Quote:** kein ADR jetzt; Spike-G-ADR später ist `[ERKENNTNIS]` (nicht `[REAKTIV]`).

---

## Reihenfolge der Bearbeitung

Falls beide Vorlagen freigegeben werden:

1. **Erst Vorlage 2 (Spike-G-Neuzuschnitt)** in `fahrplan.md` übernehmen. Kein ADR nötig, Fahrplan-Pflege.
2. **Dann Vorlage 1 (ADR-016)** als ADR in `decisions.md` anlegen + Folge-Edits in `architecture.md`, `project-context.md`, `fahrplan.md`. Reihenfolge: ADR zuerst, dann abgeleitete Doku-Edits in einem zweiten Commit (saubere History).

Patrick kann jede Vorlage einzeln freigeben oder ablehnen. Anpassungswünsche bitte konkret formulieren (welcher Abschnitt, welche Änderung).
