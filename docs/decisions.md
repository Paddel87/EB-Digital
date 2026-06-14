# Decisions

<!-- Begründete Entscheidungen und daraus abgeleitete Regeln.
     Drei Teile, in dieser Reihenfolge:
       Teil A: ADR-Übersicht (kompakte Tabelle, Reaktiv-Quote) – Pflichtlektüre bei Sessionstart
       Teil B: Architecture Decision Records (ADRs) – chronologisch, mit Tags – Detailteil
       Teil C: Entscheidungsregeln – wiederkehrende Muster, die aus ADRs hervorgehen
     Einträge werden nicht gelöscht oder verändert. Überholte ADRs werden durch
     neue ADRs ersetzt, die den alten Eintrag referenzieren.

     HINWEIS: Teil A steht bewusst zuerst. Bei Sessionstart liest Claude nur Teil A.
     Teil B (einzelne ADRs) wird nur bei konkretem Bedarf nachgelesen. -->

## Teil A: ADR-Übersicht

| ADR | Datum      | Status | Klassifikation | Themen                    | Kategorie                     | Kurztitel                                                                                                                  |
| --- | ---------- | ------ | -------------- | ------------------------- | ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| 001 | 2026-05-07 | Aktiv  | STRATEGISCH    | METHODIK                  | Methodik                      | Projektgrößen-Klassifikation Klasse G                                                                                      |
| 002 | 2026-05-07 | Aktiv  | STRATEGISCH    | STACK                     | Externe Abhängigkeiten        | Stack-Wahl (FastAPI + SvelteKit + PostgreSQL + Valkey + Procrastinate)                                                     |
| 003 | 2026-05-07 | Aktiv  | STRATEGISCH    | METHODIK                  | Architekturänderungen         | Architektur-Pattern Modular Monolith + drei SvelteKit-Frontends                                                            |
| 004 | 2026-05-07 | Aktiv  | STRATEGISCH    | SECURITY                  | Sicherheit und Datenschutz    | Admin-Bootstrap-Flow als CLI-Befehl                                                                                        |
| 005 | 2026-05-07 | Aktiv  | STRATEGISCH    | SECURITY                  | Sicherheit und Datenschutz    | AccessCode-Schema (6 Zeichen Crockford-Base32)                                                                             |
| 006 | 2026-05-07 | Aktiv  | STRATEGISCH    | DATENMODELL               | Datenmodelländerungen         | Aggregations-Schema pro Operation, ohne Personen-Buckets                                                                   |
| 007 | 2026-05-07 | Aktiv  | STRATEGISCH    | SCHNITTSTELLE             | API-Vertragsänderungen        | Datenexport asynchron via Procrastinate-Job-Tripel                                                                         |
| 008 | 2026-05-07 | Aktiv  | STRATEGISCH    | MODUL                     | Architekturänderungen         | Multi-Disponent ohne Lead, vollständiges Audit-Log                                                                         |
| 009 | 2026-05-07 | Aktiv  | STRATEGISCH    | DATENMODELL               | Datenmodelländerungen         | Verbund-Reinterpretation V2 plus Phase-1-Invarianten I1–I5                                                                 |
| 010 | 2026-05-08 | Aktiv  | OPERATIV       | STACK, DEPL.              | Externe Abhängigkeiten        | GitHub-Actions Major-Update + Verifikations-Regime                                                                         |
| 011 | 2026-05-09 | Aktiv  | OPERATIV       | STACK, METHODIK           | Lizenz und Compliance         | psycopg LGPL-3.0-only akzeptiert + Sub-Dep-Lizenz-Regime                                                                   |
| 012 | 2026-05-10 | Aktiv  | OPERATIV       | STACK, DEPL.              | Externe Abhängigkeiten        | actions/upload-artifact Major-Update v4 → v7 (Node-20-Deprecation)                                                         |
| 013 | 2026-05-10 | Aktiv  | OPERATIV       | STACK, SECURITY           | Externe Abhängigkeiten        | Rate-Limit als eigener Valkey-Counter (vor Schritt 2.2)                                                                    |
| 014 | 2026-05-10 | Aktiv  | STRATEGISCH    | METHODIK, MODUL           | Architekturänderungen         | Anbieter-Austauschbarkeit für externe Geo-Services als Architektur-Prinzip                                                 |
| 015 | 2026-05-15 | Aktiv  | REAKTIV        | STACK, SECURITY, METHODIK | Sicherheit und Datenschutz    | `get_db_session()` als FastAPI-yield-Dependency mit Rollback (Lifecycle-Bug-Fix Schritt 2.5b)                              |
| 016 | 2026-05-17 | Aktiv  | STRATEGISCH    | MODUL, STACK, PERFORMANCE | Architekturänderungen         | Verzicht auf serverseitiges Caching vor externen Geo-Services                                                              |
| 017 | 2026-05-18 | Aktiv  | ERKENNTNIS     | PERFORMANCE, MODUL        | Architekturänderungen         | Geo-Plausibilitäts-Algorithmus: Hülle-Distanz + dynamische GPS-Toleranz (2·accuracy)                                       |
| 018 | 2026-05-28 | Aktiv  | ERKENNTNIS     | MODUL, DATENMODELL        | Datenmodelländerungen         | Bündelungs-Trigger (Spike J): manuell durch Disponent, `order_bundle`-Entity, min. 2 Orders                                |
| 019 | 2026-05-28 | Aktiv  | STRATEGISCH    | METHODIK                  | Methodik                      | Phase-4-Sonderregel — UMSETZUNG-Eingangsdisziplin für Modul-Beförderungs-Phasen (Regel-019)                                |
| 020 | 2026-05-28 | Aktiv  | OPERATIV       | STACK, METHODIK           | Lizenz und Compliance         | Shapely 2.1.2 + GEOS LGPL-2.1 als Pflicht-Sub-Dep akzeptiert (Plausibility-/Geo-Pfad)                                      |
| 021 | 2026-06-10 | Aktiv  | ERKENNTNIS     | MODUL, STACK, PERFORMANCE | Externe Abhängigkeiten        | Spike G: Routing-Wechsel auf self-hosted Valhalla (TomTom-K.-o. für permanente Sperrungen)                                 |
| 022 | 2026-06-11 | Aktiv  | ERKENNTNIS     | MODUL, DEPLOYMENT         | Betrieb und Deployment        | Spike H: Backup-Strategie C (basebackup + WAL-Archiving + Dump), Recovery-Reihenfolge, RTO/RPO                             |
| 023 | 2026-06-11 | Aktiv  | ERKENNTNIS     | MODUL, DATENMODELL        | Datenmodell + API-Vertrag     | Spike K: Hilfe-Knopf-Semantik (2 Kategorien, optionale Beschreibung, Re-Notification statt Eskalation, help_alert)         |
| 024 | 2026-06-11 | Aktiv  | ERKENNTNIS     | MODUL, PERFORMANCE        | Performance (Frontend-Cache)  | Spike L: Tile-Caching CacheFirst + Operationsraum-Pre-Cache beim Schichtbeginn (4–12 MB), client-TTL 24 h                  |
| 025 | 2026-06-11 | Aktiv  | ERKENNTNIS     | MODUL, DATENMODELL        | Datenmodell (Fahrzeug-Naming) | Spike M: Fahrzeug-Naming Mischform (Default `EB-<Kürzel>-NN`, überschreibbar), max 20 Zeichen, Umlaute, UNIQUE pro Mandant |

### Reaktiv-Quote

- **Aktueller Wert:** 1 / 10 = 10 % `[REAKTIV]`-Anteil über die letzten 10 ADRs (ADR-016 bis ADR-025).
- **Schwellenwert (`project-context.md` Abschnitt 6, Klasse G):** 20 % `[REAKTIV]`-Anteil über die letzten 10 ADRs.
- **Bei Überschreitung:** STOPP, Reflexion in `fahrplan.md` ergänzen, prüfen ob Architektur-Refactoring nötig ist.
- **Aktuelle reaktive ADRs:** ADR-015 (Lifecycle-Bug in `get_db_session` durch `return` aus `async with`-Block — bei Schritt 2.5b extern gemeldeter Verdacht; Fix als Hot-Stabilisierung außerhalb der Schritt-Sequenz). Bleibt im Fenster bis ADR-025 (dann fällt ADR-015 aus dem 10er-Fenster).

---

## Teil B: Architecture Decision Records

<!-- Detailteil. Einzelne ADRs werden nur bei konkretem Bedarf gelesen –
     z. B. wenn ein Schritt einen referenzierten ADR berührt. -->

### Format

Jeder ADR folgt diesem Schema. Keine Abweichung.

```
### ADR-NNN: [Kurztitel]

- **Datum:** YYYY-MM-DD
- **Status:** Aktiv | Überholt durch ADR-M | Verworfen
- **Tags:** [aus Tag-Liste unten]
- **Phasentyp-Kontext:** [ERKUNDUNG | UMSETZUNG | STABILISIERUNG | INITIALISIERUNG]
- **Reifegrad-Wirkung:** [welche Architektur-Bestandteile gehen durch diesen ADR auf welchen Reifegrad – falls zutreffend]
- **Kategorie:** [aus CLAUDE.md Abschnitt 4 oder "Methodik"]
- **Kontext:**
  [Problem, Rahmenbedingungen, was stand an, 2–5 Sätze]
- **Optionen:**
  - **A:** [Beschreibung] – Konsequenzen: [...]
  - **B:** [Beschreibung] – Konsequenzen: [...]
  - **C:** [falls relevant]
- **Entscheidung:** [Welche Option, warum]
- **Konsequenzen:**
  - [Welche Regeln folgen daraus]
  - [Welche Einschränkungen entstehen]
  - [Welche weiteren Entscheidungen werden dadurch nötig]
- **Abgeleitete Regel:** [Falls aus diesem ADR eine Regel für wiederkehrende Fälle entsteht, hier benennen und in Teil C aufnehmen]
```

### Tags

Jeder ADR trägt mindestens **einen Klassifikations-Tag** und beliebig viele Themen-Tags.

#### Klassifikations-Tags (genau einer pflichtig)

- `[STRATEGISCH]` – in der Konzeptphase oder Initialisierung getroffene Grundsatzentscheidung. Stack-Wahl, Architektur-Pattern, Modul-Schnitt.
- `[OPERATIV]` – während der Umsetzung getroffene Entscheidung im Rahmen geplanter Architektur. Bibliothekswahl innerhalb des Stacks, konkrete Schnittstellen-Spezifikation, Datenmodell-Detail.
- `[REAKTIV]` – Entscheidung, die nötig wurde, weil bei der Umsetzung etwas Unerwartetes auftrat. Workaround, Pivot, nachträgliche Architekturänderung. **Reaktive ADRs sind ein Indikator** – ihre Häufung in einem Modul deutet darauf hin, dass die Architektur dort nicht trägt.
- `[ERKENNTNIS]` – Entscheidung als Resultat einer Erkundungsphase oder eines Spikes. Validiert oder widerlegt eine vorherige Annahme.

#### Themen-Tags (optional, mehrere möglich)

- `[STACK]`, `[MODUL]`, `[SCHNITTSTELLE]`, `[DATENMODELL]`, `[SECURITY]`, `[PERFORMANCE]`, `[DEPLOYMENT]`, `[OBSERVABILITY]`, `[METHODIK]`

### Nummerierung

Durchgehend, keine Lücken. Auch verworfene oder überholte Einträge behalten ihre Nummer.

### Einträge

#### ADR-001: Projektgrößen-Klassifikation Klasse G

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[METHODIK]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** keine direkten Reifegrad-Beförderungen; legt aber den Reaktiv-Schwellenwert (20 %) und die Strukturwahl der Vorlagen fest.
- **Kategorie:** Methodik
- **Kontext:** Modus-2-Schritt 1 verlangt eine Stufe-1-Hypothese zur Projektgröße auf Basis der Vision und eine Stufe-2-Bestätigung am Ende des Architektur-Grobschnitts (CLAUDE.md Abschnitt 1B). Stufe-1-Hypothese auf Basis der Vision: Klasse G (mehrere Module, mehrere Stakeholder-Gruppen, NFR-Cluster). Stufe-2-Bestätigung am Ende von Schritt 4: 16 Komponenten, 5 zentrale externe Abhängigkeiten, 2 Sprachen, 2 Persistenzschichten, eine Compose-Einheit – siehe `architecture.md` Abschnitt 10.
- **Optionen:**
  - **A: Klasse K (Klein)** – Indikatoren: 1 Modul, 0–1 externe Abhängigkeiten, eine Sprache, kein Persistenzlayer. – Konsequenzen: stark reduziertes Vorlagen-Set, flache Schrittliste, keine Phasenstruktur. **Nicht zutreffend** (16 Komponenten, 4 Nutzergruppen).
  - **B: Klasse M (Mittel)** – Indikatoren: 2–5 Module, 2–5 Abhängigkeiten, eine Persistenzschicht. – Konsequenzen: Phasenstruktur 3–5 Phasen. **Nicht zutreffend** (Modul-Anzahl überschritten, NFR-Komplexität durch DSGVO/API-Budget/PWA/Resilience ist klassen-G-typisch).
  - **C: Klasse G (Groß)** – Indikatoren: 6+ Module, 5+ externe Abhängigkeiten, mehrere Sprachen, mehrere Persistenzschichten, NFR-Komplexität. – Konsequenzen: voller Vorlagen-Satz, 5–7 Phasen, Reaktiv-Schwellenwert 20 %, Index-Auslagerung von ADRs/Architektur bei Wachstum.
  - **D: Klasse V (Verteilt-Groß)** – Indikatoren: mehrere unabhängig deploybare Services, asynchrone Inter-Service-Kommunikation, Multi-Repo möglich. – Konsequenzen: Pflicht-Index aller Master-Dokumente, Service-spezifische Teil-Dokumente. **Nicht zutreffend** (eine Compose-Einheit, kein verteilter Lebenszyklus).
- **Entscheidung:** **Option C – Klasse G**. Vision-Hypothese und Architektur-Grobschnitt stimmen überein. Klasse V ist explizit ausgeschlossen, weil das System als ein Compose-Stack auf einem VPS läuft.
- **Konsequenzen:**
  - Vorlagen-Set Klasse G: alle sieben Pflicht-Dokumente in voller Form; `architecture.md` als Einzeldatei mit Auslagerungspfad nach `architecture-<modul>.md` bei Wachstum >500 Zeilen oder >5 Module mit eigenen Schnittstellen; `decisions.md` als Einzeldatei zunächst, Auslagerung nach `decisions/ADR-NNN.md` ab zweistelliger ADR-Anzahl.
  - **Reaktiv-Schwellenwert: 20 %** über die letzten 10 ADRs (`project-context.md` Abschnitt 6). Bei Überschreitung Reflexions-Schritt vor weiteren UMSETZUNG-Phasen.
  - Vorläufig-zu-Belastbar-Verhältnis: nach jeder UMSETZUNG-Phase mindestens ein VORLÄUFIG-Bestandteil der berührten Module auf BELASTBAR befördern, sonst Reflexion.
  - **Pflicht-ADR-Themen für Klasse V** (Service-Grenzen-Definition, Versionierungs-Strategie zwischen Services, Failure-Mode-Handling, Datenkonsistenz-Strategie, Observability-Standard) gelten **nicht**, weil Klasse G.
  - Reklassifikation rückwärts ist nicht vorgesehen; Reklassifikation vorwärts (G→V) erfordert eigenen `[STRATEGISCH] [METHODIK]`-ADR plus STABILISIERUNGS-Migrationsphase.
- **Abgeleitete Regel:** keine eigene Regel (Klassifikation wirkt strukturell, nicht über Code-Muster).

#### ADR-002: Stack-Wahl

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[STACK]` `[DEPLOYMENT]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** Bestätigt die in `architecture.md` Abschnitt 9 als `[BELASTBAR]` markierten Stack-fixen Bestandteile (REST/JSON-Grundmodus, WebSocket-Grundmodus, HTTP-Tile-Proxy-Routing, Procrastinate-Job-Engine, Backend-Multi-Architektur ARM/x86, PWA-Service-Worker offline-fähig, Coverage-Mindestwerte, Datenschutz-Constraints). Module bleiben `[VORLÄUFIG]`, weil die Implementierung noch aussteht.
- **Kategorie:** Externe Abhängigkeiten
- **Kontext:** Vision-Constraints (EU-Hosting, AGPLv3, kein US-Cloud-Hauptbetrieb, kein Tracking, Privacy-by-Design, PWA-only, Self-Hosting) plus Lasterwartung (50 Disponenten + 500 Einsatzkräfte) plus Rollen-Profile (Disponent stationär, Betreuer mobil mit Funklöchern, Einsatzkraft niederschwellig anonym) sind in Modus-2-Schritt 2 erarbeitet und in Modus-2-Schritt 2a am 2026-05-07 vollständig auf offiziellen Quellen verifiziert worden (Verifikations-Stempel `Verifiziert: 2026-05-07` für jede Komponente in `project-context.md` Abschnitt 3).
- **Optionen:**
  - **A: Django + DRF + Channels + Celery + Redis-Broker, React-Frontend.** – Konsequenzen: bewährter Mainstream-Stack, viele Entwickler verfügbar; aber Async-Bruch zwischen DRF und Channels, Celery-Overkill für PostgreSQL-basierte Job-Anforderung, Redis ist seit RSALv2/SSPL-Lizenzwechsel ausgeschlossen, React-Bundle größer als für die schlanke Einsatzkraft-PWA nötig.
  - **B: Node-Backend (NestJS) + Prisma + BullMQ + Next.js.** – Konsequenzen: sprachhomogen Backend+Frontend, sehr gute PWA-Unterstützung; aber Prisma + Multi-Tenant-Patterns sind bei mandantenstarken Modellen aufwendig, BullMQ braucht Redis (siehe oben), Threat-Modell für Async-Node bei Long-Running-Connections (WebSocket + Procrastinate-Aufgaben) hat in vergleichbaren Projekten Reibung erzeugt.
  - **C: FastAPI + SQLAlchemy + Alembic + Pydantic + httpx + Procrastinate (Backend), Svelte 5/SvelteKit 2 + Vite 8 + Workbox + MapLibre GL JS (Frontends), PostgreSQL 17 + Valkey 8 (Datenhaltung), nginx (Tile-Proxy) + Caddy (Reverse-Proxy), Docker Compose v5 + Hetzner CCX-VPS in Deutschland (Infrastruktur), uv + pnpm (Package-Manager), AGPLv3 (Projektlizenz) – verifizierter Stand vom 2026-05-07.** – Konsequenzen: vollständig async-native im Backend, kompakte Frontend-Bibliothek mit klaren PWA-Pfaden, Procrastinate nutzt PostgreSQL als Backing (ACID-Job-State Teil der DB-Backups), Valkey als Linux-Foundation-Fork löst die Redis-Lizenzproblematik, MapLibre löst die Mapbox-Lizenzproblematik. Höhere Eigenleistung im Auth-Bereich (kein FastAPI-Users), kompensiert durch externe Security-Review vor Produktivstart.
- **Entscheidung:** **Option C**. Erfüllt alle harten Vision-Constraints, ist intern konsistent (async durchgängig), reduziert externe Bindungen (kein Redis, keine Mapbox, keine US-Cloud, keine SaaS-Auth), behält Lizenz-Disziplin (AGPLv3 + permissive Dependencies), und passt zur Lasterwartung ohne Skalierungs-Vorabwurf.
- **Konsequenzen:**
  - **Versionsdisziplin:** jede in `project-context.md` Abschnitt 3 gelistete Version trägt Pflicht-Vermerk `Verifiziert: YYYY-MM-DD`. Major-Updates erfordern erneute Verifikation und einen ADR. Minor- und Patch-Updates sind freigabefrei (CLAUDE.md Abschnitt 4 Punkt 3, Major-Vorbehalt explizit dort).
  - **Bewusste Versions-Zurückhaltung an zwei Stellen:** PostgreSQL **17.9 statt 18** und mypy **1.20.2 statt 2.0.x** – „Stabilität vor Aktualität". Beide Punkte sind in `project-context.md` Abschnitt 3 als solche dokumentiert.
  - **Eigener Auth-Code statt FastAPI-Users**, basierend auf argon2-cffi + itsdangerous + Starlette-SessionMiddleware. Begleitende Pflichten: Auth-Modul-Coverage ≥ 95 %, externe Security-Review vor Produktivstart (siehe `project-context.md` Abschnitt 7 plus folgende ADRs in einer späteren Phase).
  - **CI-Plattform GitHub Actions**, Workflow-Splitting `ci.yml` / `security.yml` / `release.yml` für Klasse G; Pflicht-Pinning auf Patch-Tag oder Commit-Hash für `pnpm/action-setup` und `astral-sh/setup-uv` (Immutable-Tag-Trend).
  - **Explizite Ausschlüsse** sind in `project-context.md` Abschnitt 3 „Explizit nicht erlaubt" geführt: keine US-Cloud als Hauptbetrieb, kein Redis, keine Mapbox, keine GPL/LGPL-Backend-Dependencies, keine native Mobile-Toolchains, keine SaaS-Auth-Provider, kein FastAPI-Users/passlib, kein Taskiq/ARQ/Celery, keine Google-Maps/-Routing/-Geocoding, keine ORM-Schnellschüsse, keine Behörden-IT-Anschlüsse, kein Tracking.
  - **Externe API-Budget-Disziplin:** ~50 €/Monat für MapTiler+TomTom über alle aktiven Einsatztage (`project-context.md` Abschnitt 6 Performance) – `backend/geo` führt Verbrauchszähler.
- **Abgeleitete Regel:** Regel-001 (Versionsdisziplin) und Regel-002 (Stack-Ausschlüsse beachten) – siehe Teil C.

#### ADR-003: Architektur-Pattern Modular Monolith + drei SvelteKit-Frontends

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[METHODIK]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** fixiert die Pattern-**Wahl** als strategische Entscheidung. Tragfähigkeit (Last, Modulgrenzen-Disziplin) bleibt `[VORLÄUFIG]` bis zur ersten UMSETZUNG-Phase mit bestandenem Funktions-/Last-Test (siehe `architecture.md` Abschnitt 9).
- **Kategorie:** Architekturänderungen
- **Kontext:** Aus Vision und Klärungs-Session ergeben sich vier Nutzergruppen (Plattform-Admin, Disponent, Betreuer, anonyme Einsatzkraft) mit deutlich unterschiedlichen Berechtigungs-Modellen, Last-Profilen und Service-Worker-Anforderungen. Backend-Module sind dagegen domänenintern (Mandant, Operation, Order, Fleet, Geo, Realtime, Retention, Export, Resilience) ohne erkennbar verteilten Lebenszyklus. Lasterwartung 50/500 trägt einen Monolithen.
- **Optionen:**
  - **A: Monolith Backend + Monolith Frontend.** – Konsequenzen: einfachster Schnitt, aber Service-Worker-Einsatz und mobile Last-Profile schwer auszubalancieren; Disponent-Tablet und Einsatzkraft-Smartphone müssten dasselbe Bundle laden.
  - **B: Modular Monolith Backend + drei SvelteKit-Frontends + 2 Proxies (Tile-Proxy, Reverse-Proxy).** – Konsequenzen: Backend bleibt schlank deploybar, Modulgrenzen sind Pflicht und Architekturbruch verboten (CLAUDE.md Abschnitt 6); Frontends können je nach Rolle ihre PWA-Strategie unabhängig wählen (Offline-Pufferung Betreuer vs. anonymer Single-Use Einsatzkraft).
  - **C: Microservices pro Domäne.** – Konsequenzen: hohe Betriebs- und Test-Komplexität, asynchrone Inter-Service-Kommunikation müsste neu gebaut werden, Multi-Repo-Pflege; **nicht gerechtfertigt** durch Last- oder Stakeholder-Profil. Würde auch der Klassifikation Klasse V entsprechen, was per ADR-001 bewusst ausgeschlossen ist.
- **Entscheidung:** **Option B – Modular Monolith Backend + drei SvelteKit-Frontends + Tile-Proxy + Reverse-Proxy**. Liefert klare Modul-Kommunikations-Disziplin (Modul-Karte in `architecture.md` Abschnitt 2 mit erlaubten Beziehungen) ohne Microservices-Overhead.
- **Konsequenzen:**
  - **Modulgrenzen sind verbindlich.** Aufrufe Modul A → Modul B nur über die in `architecture.md` Abschnitt 4 spezifizierten Schnittstellen. Direktzugriff auf interne Strukturen anderer Module ist Architekturbruch (CLAUDE.md Abschnitt 6).
  - **Frontend-Backend-Kommunikation ausschließlich** REST über `/api`-Präfix oder WebSocket über `/ws`-Präfix.
  - **Externe Karten-/Routing-Aufrufe** ausschließlich über `infra/tile-proxy` (API-Keys Backend-seitig, Budget-Disziplin zentral).
  - **Drei Frontend-Bundles** mit eigener `pnpm`-Workspace-Struktur (Frontend-Trio in `apps/`-Layout). `frontend-disponent`, `frontend-betreuer`, `frontend-einsatzkraft` sind verschiedene PWA-Profile mit unterschiedlichen Service-Worker-Strategien.
  - **Reklassifikation in Microservices** ist freigabepflichtig (Architekturänderung) und würde Reklassifikation auf Klasse V nach sich ziehen.
- **Abgeleitete Regel:** Regel-003 (Modulgrenzen-Pflicht) und Regel-004 (kein direkter Frontend↔Externer-Service-Aufruf) – siehe Teil C.

#### ADR-004: Admin-Bootstrap-Flow als CLI-Befehl

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[SECURITY]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt Schnittstelle S1 (Admin-Bootstrap-CLI in `architecture.md` Abschnitt 4) und Modul-Verantwortung `backend/auth` strategisch fest; Schnittstelle und Modul bleiben `[VORLÄUFIG]` bis zur UMSETZUNG.
- **Kategorie:** Sicherheit und Datenschutz
- **Kontext:** Der allererste Plattform-Administrator muss angelegt werden, ohne dass eine andere Plattform-Admin-Identität bereits existiert. Klassisches Henne-Ei-Problem. Geklärt am 2026-05-07 in der Klärungs-Session zu `project-context.md` Abschnitt 11 Frage A.
- **Optionen:**
  - **A: ENV-Variable-Bootstrap** (`EB_ADMIN_PASSWORD=…` beim Start des Containers). – Konsequenzen: Klartext-Passwort in `.env`-Datei, im `docker compose`-Output, in Backups und in Container-Logs. Verstößt gegen Datenschutz-Constraint „keine sensiblen Daten in Logs" (`project-context.md` Abschnitt 6).
  - **B: Web-Setup-Wizard** (erste UI-Seite legt Admin-Account an). – Konsequenzen: Race-Condition-Risiko (Angreifer könnte schneller sein als der Betreiber), zwingt sehr früh Web-Code mit Sonder-Endpunkt und ggf. Sonder-Schalter „bootstrap_done?".
  - **C: Hybrid-Setup-Link via Server-Log** (Server schreibt zur Boot-Zeit einmaligen Link in Container-Log). – Konsequenzen: Konflikt mit Datenschutz-Constraint „keine sensiblen Daten in Logs"; Logs werden ggf. zentral aggregiert oder eingesehen, der Link wäre dort als Sekundär-Faktor sichtbar.
  - **D: CLI-Befehl im Backend-Container** (`docker compose exec backend python -m eb_digital admin create`, Username als Argument, Passwort interaktiv via `getpass`). – Konsequenzen: kein Klartext-Passwort in ENV/Compose-File/Logs/Backups; jederzeit nutzbar (kein Single-Use-Bootstrap), legt auch nachträglich weitere Plattform-Admins an; Voraussetzung ist SSH-Zugriff auf den Host plus Docker-Rechte – gleiches Risikoniveau wie der Betrieb des Hosts an sich.
- **Entscheidung:** **Option D – CLI-Befehl, jederzeit nutzbar**. Niedrigste Angriffsfläche, kein Web-Sonderfall, hält die offene Skalierungs-Frage „zentraler vs. mehrere Plattform-Admins" (`project-context.md` Abschnitt 11 Punkt „Administrator-Architektur") ohne Architekturzwang offen.
- **Konsequenzen:**
  - **CLI-Befehl** liegt in `backend/auth` als Untermodul `eb_digital.admin` mit Argumenten `--username` (positional/required) und Passwort-Eingabe via `getpass` (kein `--password` als Argument, kein Echo).
  - **Hashing** mit Argon2id über argon2-cffi mit Library-Default-Parametern (`project-context.md` Abschnitt 6 Sicherheit).
  - **Mehrfach-Nutzbarkeit:** kein „bootstrap_done"-Flag; weitere Admins können jederzeit per CLI angelegt werden, ohne dass eine bestehende Web-Auth-Identität nötig ist. Das ist als Komfort gewollt, **nicht** als Backdoor – Voraussetzung bleibt SSH+Docker-Zugriff.
  - **Audit:** jeder per CLI angelegte Admin-Account wird in einem Audit-Log-Eintrag (Tabelle dafür wird in einer späteren UMSETZUNG-Phase definiert) mit Zeitpunkt, Username und Erstellungs-Methode `bootstrap_cli` festgehalten – kein Klartext-Passwort.
  - **Kein Web-Endpunkt** für Admin-Erstellung in Phase 1.
- **Abgeleitete Regel:** Regel-005 (Sensible Bootstrap-Operationen über CLI, nicht Web) – siehe Teil C.

#### ADR-005: AccessCode-Schema für anonyme Einsatzkraft-Sessions

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[SECURITY]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt Schnittstelle S2 (Anonymous Session API) und Modul-Verantwortung `backend/auth_anonymous` strategisch fest; Schnittstelle und Modul bleiben `[VORLÄUFIG]` bis zur UMSETZUNG.
- **Kategorie:** Sicherheit und Datenschutz
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage B. Die Einsatzkraft-PWA wird primär über eine pro Operation neu erzeugte URL mit kryptographischem Token erreicht. Optional kann der Disponent zusätzlich einen AccessCode aktivieren – Format, Wiederverwendbarkeit und Toggle-Verhalten waren offen.
- **Optionen:**
  - **A: 4-stellige PIN.** – Konsequenzen: 10⁴ ≈ 10 000 Möglichkeiten – Brute-Force-Reserve zu gering, insbesondere bei verteilter Belastung über mehrere Sessions.
  - **B: Single-Use-Codes pro Einsatzkraft** (jeder Einsatzkraft wird ein eigener Code zugewiesen). – Konsequenzen: erfordert eine zentrale Verteilliste der Einsatzkräfte – widerspricht „kein Klarnamen, anonyme Sessions" und scheitert an der realen Verteilungslogistik im Einsatz (Code-Übergabe „außerhalb des Systems").
  - **C: 6 Zeichen Crockford-Base32** (Großbuchstaben + Ziffern, ohne O/0/I/1/L), ein Code pro Operation, von beliebig vielen Einsatzkräften nutzbar, läuft mit Operation-Ende ab. – Konsequenzen: 32⁶ ≈ 1 073 000 000 Möglichkeiten, gut sprech- und merkbar, niedrigschwellig verteilbar (Ansage, Aushang, QR), kein Personen-Tracking.
- **Entscheidung:** **Option C – 6 Zeichen Crockford-Base32**.
- **Konsequenzen:**
  - **Format:** 6 Zeichen, Crockford-Base32-Alphabet (Großbuchstaben + Ziffern, ohne O/0/I/1/L), z. B. `X7K3PQ`. Kein Padding, kein Mixed-Case.
  - **Wiederverwendbarkeit:** **ein** Code pro Operation, von beliebig vielen Einsatzkräften nutzbar, läuft mit Operation-Ende ab.
  - **Aktivierung während laufender Operation:** wirkt **nur auf neu startende Sessions / neue Bestellungen**. Bestehende anonyme Sessions, die vor Aktivierung gestartet sind, bestellen weiter ohne Code bis zum Session-Ablauf.
  - **Disponenten-UI:** Anzeige des Codes plus Copy-to-Clipboard plus QR-Code (rendert die kombinierte Einsatz-URL inklusive Code). Druck/PDF-Export ist **nicht** Phase 1.
  - **Rotation:** **keine** systemseitige Rotation in Phase 1. Bei Verdacht auf Kompromittierung beendet der Disponent die Operation und eröffnet eine neue – URL und Code werden gemeinsam erneuert. Eine spätere Rotate-Funktion (Stabilisierungs-Erweiterung) ist nachrüstbar.
  - **Backend-Verifikation:** AccessCode wird in der Operation-Tabelle als Hash + Salt gespeichert, **nicht** im Klartext. Bei Bestellung: Konstantzeit-Vergleich.
  - **Logging-Disziplin:** weder Klartext-Code noch Hash in Logs. In Logs erscheint nur das boolesche Ergebnis „validierung erfolgreich/fehlgeschlagen".
- **Abgeleitete Regel:** Regel-006 (AccessCode-Hashing-Pflicht) und Regel-007 (AccessCode-Toggle wirkt nur auf neue Sessions) – siehe Teil C.

#### ADR-006: Aggregations-Schema pro Operation

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[DATENMODELL]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt das Aggregat-Datenmodell `operation_aggregate` (`architecture.md` Abschnitt 7) sowie Schnittstelle S5 (Operations → Retention Aggregat-Trigger, `architecture.md` Abschnitt 4) strategisch fest; Datenmodell und Schnittstelle bleiben `[VORLÄUFIG]` bis zur UMSETZUNG `backend/retention`.
- **Kategorie:** Datenmodelländerungen
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage C. Vision Abschnitt 6 verlangt: aggregierte Statistiken bleiben dauerhaft, individuelle Bestell- und Standortdaten 30 Tage nach Operation-Ende. Offen war, welche Felder vor Anonymisierung in welche Aggregat-Form überführt werden, ob Geometrien gespeichert werden, ob Personen-Buckets erlaubt sind.
- **Optionen:**
  - **A: Pseudonyme Personen-Hashes im Aggregat** (Hash pro Disponent, Betreuer, Einsatzkraft mit Aktivitäts-Zähler). – Konsequenzen: Re-Identifikations-Risiko bei kleinen Mandanten (DPolG Bremen ist klein); selbst bei Salz-Hash mit langer Lebensdauer entstehen Quasi-Identifikatoren über Aktivitätsmuster. Verstößt gegen den Geist des Datenschutz-Constraints.
  - **B: Festes Metriken-Set ohne Personen-Buckets**, Aggregation pro Operation, ein finaler Snapshot beim Operation-Ende. – Konsequenzen: keine Re-Identifikation möglich; Aggregat ist ein einfacher Zähler-Datensatz.
  - **C: Dauerhafte Geometrie der Einsatzräume** (Polygon plus Mittelpunkt). – Konsequenzen: visuell wertvoll, aber Geometrie bei wenigen Operationen pro Mandant ist über die Zeit ein Quasi-Identifikator, und MapTiler-Lizenzfragen für persistente Geometrie-Snapshots wären zusätzlich zu klären.
  - **D: Stadt-/Region-Label als String** (vom Disponenten beim Eröffnen gesetzt, z. B. „Bremen Innenstadt"). – Konsequenzen: ausreichend für Rückblicke und Reports, kein Geometrie-Persistenz-Aufwand, kein Re-Identifikations-Vektor.
- **Entscheidung:** **Kombination B + D**. Aggregat pro Operation als finaler Snapshot beim Operation-Ende, festes Metriken-Set ohne Personen-Buckets, Stadt-Label statt Geometrie.
- **Konsequenzen:**
  - **Aggregations-Einheit:** ein Eintrag in `operation_aggregate` pro Operation, geschrieben **beim Operation-Ende** als finaler Snapshot. Übergreifende Roll-ups (pro Mandant, pro Tag/Monat) per SQL-Sum aus dieser Tabelle ableitbar.
  - **Metriken-Set pro Eintrag** (finale Liste, in dieser Reihenfolge im Schema):
    - `tenant_id` (in Phase 1 genau eine, siehe Invariante I4 in ADR-009)
    - `operation_id`
    - `start_at`, `end_at` (UTC, mit `zoneinfo`)
    - `area_count` (Anzahl Einsatzräume)
    - `order_count`, `order_assignment_count`, `cancellation_count`, `bundling_count`
    - `supply_transporter_mode_changes` als JSON-Map mit Counter pro Modus
    - `access_code_activated` (boolean)
    - `route_override_count`
    - `help_request_count`
    - `total_drive_distance_km` (gerundet auf 1 km)
    - `peak_active_vehicles`, `peak_active_dispatchers`
    - `area_label` (String, vom Disponenten gesetzt, z. B. „Bremen Innenstadt")
  - **Keine Personen-Buckets** (kein Pseudonym-Hash für Disponenten/Betreuer/Einsatzkräfte). Datenbasis für die `peak_*`- und `count_*`-Felder ist die Audit-Log-Tabelle aus ADR-008 plus die Operations-/Order-Tabellen.
  - **Zugriff:** Mandanten-Disponenten sehen Aggregate **ihres eigenen Mandanten**; Plattform-Administrator sieht alle. Keine Cross-Mandanten-Veröffentlichung in Phase 1.
  - **Anonymisierungs-Reihenfolge:** Aggregat-Schreibung **beim Operation-Ende** (sofort, synchron im Operation-Ende-Workflow). Anonymisierungs-Job läuft entkoppelt 30 Tage später und löscht nur noch Detail-Daten. Damit besteht keine Race-Bedingung zwischen Anonymisierung und Aggregat-Berechnung.
  - **Phase-1-Invariante I4** (siehe ADR-009): `operation_aggregate.tenant_id` ist in Phase 1 genau eine Mandanten-ID. Spätere Verbund-Phase erweitert das Schema additiv (mehrere verarbeitende Mandanten pro Aggregat oder Quell-Markierung).
- **Abgeleitete Regel:** Regel-008 (Aggregat-Schreibung sofort beim Operation-Ende) und Regel-009 (kein Personen-Bucket im Aggregat) – siehe Teil C.

#### ADR-007: Datenexport asynchron via Procrastinate

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[SCHNITTSTELLE]` `[DATENMODELL]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt Schnittstelle S6 (Tenant Data Export, `architecture.md` Abschnitt 4) und das Datenmodell des `export_job`-Eintrags strategisch fest; Schnittstelle bleibt `[VORLÄUFIG]` bis zur UMSETZUNG `backend/export`.
- **Kategorie:** API-Vertragsänderungen
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage D. DSGVO Art. 20 (Datenübertragbarkeit) und Vision-Constraint „Mandanten-Datenexport" verlangen einen Self-Service-Export. Offen war Verfahren (synchron/asynchron), Format, Inhalt, Auslöser, Lebensdauer.
- **Optionen:**
  - **A: Synchron-Einzelendpunkt** (`GET /api/tenants/{id}/export` als Single-Request mit ZIP-Stream). – Konsequenzen: bei großen Mandanten Worker-Block-Risiko (Procrastinate-Worker oder API-Worker), Kollision mit p95 < 300 ms-Ziel, Timeouts auf Reverse-Proxy- oder Browser-Seite.
  - **B: Asynchron via Procrastinate-Job-Tripel.** – Konsequenzen: Job-Erzeugung antwortet sofort mit Job-ID, Status-Polling über separaten Endpunkt, Download-Endpunkt liefert das fertige ZIP. Nutzt vorhandenen Procrastinate-Stack ohne Zusatz-Komponente.
  - **C: Mit Karten-Snapshots im Export** (Tile-Captures der Operation-Räume). – Konsequenzen: erhöht Datenvolumen, MapTiler-Lizenz-Klärungsbedarf für persistente Tile-Speicherung, Phase-1-Komplexität nicht gerechtfertigt.
- **Entscheidung:** **Option B**, **ohne** Karten-Snapshots (Option C verworfen).
- **Konsequenzen:**
  - **API-Tripel:**
    - `POST /api/tenants/{id}/export` startet Procrastinate-Job, liefert `{job_id, status: "queued"}`.
    - `GET /api/tenants/{id}/export/{job_id}` liefert Job-Status (`queued`, `running`, `done`, `failed`).
    - `GET /api/tenants/{id}/export/{job_id}/download` liefert das fertige ZIP, sobald `status = "done"`.
  - **Format:** ZIP mit JSON-Datei pro Tabelle plus `manifest.json` (Schema-Version, Export-Datum UTC, Mandanten-ID, Tabellen-Liste mit Datensatzzahl).
  - **Inhalt:** vollständige Mandanten-Daten – Stammdaten, Disponenten-/Betreuer-Accounts ohne Passwort-Hashes, Fahrzeug-Stammdaten plus Beladungs-Historie, mandantenspezifischer Artikelkatalog, Operations, Bestellungen plus Fahraufträge der letzten 30 Tage detailliert (danach anonymisiert), Aggregations-Tabelle. Keine Karten-Snapshots, keine externen Anhänge, keine Klartext-AccessCodes.
  - **Auslöser:** Self-Service durch Disponent / Mandanten-Admin-Disponent im **eigenen** Mandanten; Plattform-Administrator kann jeden Mandanten exportieren (Override-Pfad).
  - **Lebensdauer:** fertiges ZIP unter `/var/eb-digital/exports/{tenant_id}/{job_id}.zip`, **7 Tage** abrufbar (mehrfacher Download), danach Cleanup-Job (zweiter Procrastinate-Job, läuft täglich).
  - **Phase-1-Invariante I5** (siehe ADR-009): Datenexport ist in Phase 1 auf `role='owner'` reduziert; spätere Verbund-Aufträge werden als geteilte Datensätze mit Quell-Markierung ergänzt.
  - **Authentifizierung:** alle drei Endpunkte verlangen Disponenten-Session (Self-Service) oder Plattform-Admin-Session (Override). Anonyme Sessions haben keinen Zugriff.
- **Abgeleitete Regel:** Regel-010 (Mandanten-übergreifende Datenoperationen ausschließlich asynchron via Procrastinate) – siehe Teil C.

#### ADR-008: Multi-Disponent ohne Lead, vollständiges Audit-Log

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[MODUL]` `[DATENMODELL]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt das Verhaltens-Modell von `backend/operations` und das Datenmodell `operation_audit_log` (`architecture.md` Abschnitt 7) strategisch fest; Modul und Schnittstellen bleiben `[VORLÄUFIG]` bis zur UMSETZUNG.
- **Kategorie:** Architekturänderungen
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage E. Mehrere Disponenten können gleichzeitig an einer Operation arbeiten. Frage war: gibt es einen Lead-Disponenten mit Sonderrechten für destruktive Aktionen, oder sind alle gleichberechtigt?
- **Optionen:**
  - **A: Lead-Modell mit Eröffner-Default.** Der Disponent, der die Operation eröffnet, ist Lead; nur er darf die Operation beenden, AccessCode toggeln, Operation-Räume umgestalten, Versorgungs-Transporter-Modi wechseln. – Konsequenzen: Schutz gegen versehentliche destruktive Aktionen; aber: Eskalations-Pfad nötig, falls Lead-Disponent nicht erreichbar (Schicht-Ende, Funkloch). Plattform-Administrator als Eskalations-Pfad ist laut Klärungs-Session nicht zuverlässig erreichbar.
  - **B: Kein Lead-Modell, alle Disponenten am Operation gleichberechtigt**, einschließlich destruktiver Aktionen. UX-Bestätigungs-Dialog plus vollständiges Audit-Log ersetzen den Lead-Schutz durch retrospektive Nachvollziehbarkeit. – Konsequenzen: Disponenten bleiben jederzeit handlungsfähig; Schaden durch versehentliche Aktion wird durch Bestätigungs-Dialog minimiert; Verantwortlichkeit über Audit-Log auflösbar.
- **Entscheidung:** **Option B – kein Lead-Modell**. Begründung Patrick: Plattform-Administrator nicht zuverlässig erreichbar, Disponenten haben den operativen Überblick und sollen ohne Eskalations-Hürde handlungsfähig sein. Schutz gegen Großschäden trägt der Bestätigungs-Dialog plus retrospektive Nachvollziehbarkeit über das Audit-Log.
- **Konsequenzen:**
  - **Berechtigungs-Modell `backend/operations`:** alle Disponenten, die laut `operation_tenant_participation` (siehe ADR-009) am Operation teilnehmen, dürfen **alle** Aktionen ausführen, einschließlich der destruktiven (Operation beenden, AccessCode toggeln, Operation-Raum-Geometrie ändern, Versorgungs-Transporter-Modus wechseln).
  - **`operation_audit_log`-Tabelle:** jede destruktive oder konfigurierende Aktion erzeugt einen Eintrag mit `actor_dispatcher_id`, `action_type`, `at` (UTC), `target_kind` und `target_id` (z. B. `operation`, `operation_area`, `vehicle`), plus `payload` (JSON, Aktion-spezifische Detail-Daten ohne PII).
  - **UX-Schutz:** Bestätigungs-Dialog im `frontend-disponent` vor jeder destruktiven Aktion. Implementierungs-Detail im Frontend, kein Architektur-Block.
  - **Sichtbarkeit Audit-Log:** im Disponenten-UI für **alle** Disponenten am Operation und für den Plattform-Administrator. Kein Aggregations-Zugriff durch andere Mandanten.
  - **Audit-Log liefert Datenbasis** für die `peak_active_*`- und `*_count`-Felder im Aggregat (siehe ADR-006).
  - **Retention Audit-Log:** unterliegt der 30-Tage-Anonymisierung wie andere Detail-Daten der Operation; nach Anonymisierung bleibt nur die Aggregat-Spur (siehe ADR-006).
- **Abgeleitete Regel:** Regel-011 (Audit-Log-Pflicht bei destruktiven/konfigurierenden Operations-Aktionen) und Regel-012 (Confirmation-Dialog vor destruktiven Aktionen im Frontend) – siehe Teil C.

#### ADR-009: Verbund-Reinterpretation V2 plus Phase-1-Invarianten I1–I5

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[DATENMODELL]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt fünf Datenmodell-Invarianten I1–I5 (`architecture.md` Abschnitt 9) strategisch fest, die Phase 1 architektonisch verbund-tauglich halten. Invarianten bleiben `[VORLÄUFIG]` bis zur UMSETZUNG der jeweiligen Module.
- **Kategorie:** Datenmodelländerungen
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage F. Vision postuliert die strikte Trennung der Anbieterseiten (jeder Mandant verwaltet eigene Disponenten, Betreuer, Fahrzeuge, Aufträge). Solidarische Praxis (ein Mandant versorgt auch fremde Einsatzkräfte) ist über die anonyme Bezieherseite gelöst. Realer Bedarf (zwei Mandanten an derselben Großlage mit gemeinsamem Auftragspool) widerspricht der Default-Trennung. Frage: Vision-Pivot oder Reinterpretation, sofortige Implementierung oder Phase-1-Vorbereitung?
- **Optionen:**
  - **V1: Echter Konflikt mit der Vision** (Verbund-Modus ist nicht mit Anbieterseiten-Trennung vereinbar; Vision müsste angepasst werden, oder Verbund-Modus muss verworfen werden). – Konsequenzen: zwingt Vision-Pivot-Diskussion oder verschließt einen real geforderten Anwendungsfall.
  - **V2: Reinterpretation als opt-in-Erweiterung** mit beidseitigem Konsens. Solange beide Mandanten ausdrücklich zustimmen, ist die Default-Trennung nicht verletzt, sondern bewusst delegiert. – Konsequenzen: Vision bleibt unangetastet, Anwendungsfall wird ermöglicht.
  - **V3: Vision-Pivot** (Anbieterseiten-Trennung wird als Default abgeschafft). – Konsequenzen: tiefer Architektur-Eingriff, Constraint-Bruch, nicht gerechtfertigt durch den realen Bedarf eines opt-in-Falls.
  - **P1: Sofort implementieren in Phase 1.** – Konsequenzen: erhebliche Phase-1-Komplexität (Cross-Mandanten-UI, Vertrags-Akzeptanz, Auflösung, Statistik-Zuordnung); verzögert die DPolG-Bremen-Solo-Phase ohne Mehrwert für den Initial-Mandanten.
  - **P2: Phase 1 architektonisch verbund-tauglich vorbereiten**, eigentliche Verbund-Funktionalität in späterer UMSETZUNG-Phase mit ERKUNDUNG-Vorlauf. – Konsequenzen: Phase 1 bleibt klein, spätere Erweiterung ohne Tabellen-Refactoring möglich, wenn die Datenmodell-Invarianten konsequent eingehalten werden.
  - **P3: Verbund-Modus gar nicht implementieren.** – Konsequenzen: schließt einen real geforderten Anwendungsfall aus.
- **Entscheidung:** **V2 + P2 – Reinterpretation als opt-in-Erweiterung mit beidseitigem Konsens, in Phase 1 architektonisch vorbereitet, eigentliche Funktionalität in späterer UMSETZUNG-Phase**.
- **Konsequenzen – fünf Phase-1-Invarianten** (additive Einführbarkeit ohne Tabellen-Refactoring):
  - **I1:** Operation↔Mandant über die Verknüpfungstabelle `operation_tenant_participation(operation_id, tenant_id, role)`. In Phase 1 genau ein Eintrag pro Operation mit `role='owner'`. **Kein direkter `operation.tenant_id`-Foreign-Key.**
  - **I2:** Berechtigungs-Filter formuliert als „Operations, an denen mein Mandant teilnimmt" statt „Operations meines Mandanten". In Phase 1 verhaltensgleich, in späterer Verbund-Phase additiv erweiterbar.
  - **I3:** Fahrzeug-Zuweisung in `backend/operations.assign_vehicle()` prüft **Operations-Kontext** (Teilnahme über `operation_tenant_participation`), **nicht** Mandanten-ID-Match.
  - **I4:** `operation_aggregate` (siehe ADR-006) bleibt in Phase 1 mit genau **einer** `tenant_id` pro Eintrag. Spätere Schema-Migration auf „verarbeitende Mandanten" ist im Architektur-Dokument als bekannte spätere Aufgabe vermerkt – keine versteckte technische Schuld.
  - **I5:** Datenexport (siehe ADR-007) bleibt in Phase 1 auf `role='owner'` reduziert. Spätere Verbund-Aufträge werden als geteilte Datensätze mit Quell-Markierung ergänzt.
- **Konsequenzen – Modul-Zuordnung der späteren Verbund-Erweiterung:**
  - **Kein eigenes `backend/verbund`-Modul in Phase 1.** Spätere Funktionalität als Erweiterung von `backend/tenants` (Verbund-Verträge: Initiative, Akzeptanz, Auflösung) und `backend/operations` (Cross-Mandanten-Disposition, gemeinsame Operations-URL).
  - Falls bei der späteren Implementierung Modulgrenzen unscharf werden, wird per ADR ein eigenes Modul ausgegliedert.
- **Konsequenzen – Fahrplan:**
  - Spätere UMSETZUNG-Phase „Verbund-Modus für parallele Mandanten-Großlagen" mit ERKUNDUNG-Vorlauf (Stakeholder-Klärung mit zwei Mandanten, Berechtigungs-Modell-Verfeinerung, Statistik-Zuordnung) wird in Modus-2-Schritt 6 in `fahrplan.md` als spätere Phase aufgenommen.
- **Abgeleitete Regel:** Regel-013 (Operation↔Mandant ausschließlich über `operation_tenant_participation`) und Regel-014 (Berechtigungs-Filter als Teilnahme-Filter formulieren) – siehe Teil C.

#### ADR-010: GitHub-Actions Major-Update plus Verifikations-Regime

- **Datum:** 2026-05-08
- **Status:** Aktiv
- **Tags:** `[OPERATIV]` `[STACK]` `[DEPLOYMENT]`
- **Phasentyp-Kontext:** UMSETZUNG (Phase 1, im Anschluss an Schritt 1.2)
- **Reifegrad-Wirkung:** keine direkten Architektur-Reifegrad-Beförderungen; festigt aber den Status der CI-Pipeline (`[BELASTBAR]` durch Existenz auf `main`) gegen die kommende Node-20-Deprecation.
- **Kategorie:** Externe Abhängigkeiten (CLAUDE.md Abschnitt 4 Punkt 3 – Major-Update bestehender Abhängigkeiten ist freigabepflichtig).
- **Kontext:** In Modus-2-Schritt 10 (2026-05-07) wurden zwei GitHub-Actions als **Annahme** gepinnt (`astral-sh/setup-uv@v5.0.0`, `pnpm/action-setup@v4.0.0`) mit dem Vermerk „in Phase 1 Schritt 1.2 zu verifizieren". Bei der Verifikation in Schritt 1.2 (2026-05-08) wurde sichtbar, dass diese Pins **zwei Major-Versionen hinter dem aktuellen Stand** liegen (heute v8.1.0 und v6.0.5) und dass die GitHub-Annotations bereits **Node.js-20-Deprecation ab 2026-06-02** flaggen. Zusätzlich wurde aufgedeckt, dass das `Verifiziert: YYYY-MM-DD`-Regime aus `project-context.md` Abschnitt 3 GitHub-Actions bisher **nicht** umfasst – die Disziplin endete bei Sprachen, Bibliotheken, Datenbanken, Infrastruktur und Package-Managern. Das ist eine strukturelle Lücke, die diese Entscheidung mit schließt.
- **Optionen:**
  - **A:** Bei v5.0.0/v4.0.0 bleiben, Major-Update aufschieben. – Konsequenzen: Node-20-Deprecation ab 2026-06-02 erzwingt das Update später unter Zeitdruck, möglicherweise mitten in einer anderen UMSETZUNG-Phase. Verifikations-Lücke bliebe offen.
  - **B:** Sofort auf aktuelle Major-Linie aktualisieren (`astral-sh/setup-uv@v8.1.0`, `pnpm/action-setup@v6.0.5`) und Verifikations-Regime auf GitHub-Actions ausdehnen. – Konsequenzen: Major-Update ist ADR-pflichtig (CLAUDE.md Abschnitt 4 Punkt 3) und braucht einen Re-Test der CI-Pipeline. Schließt die strukturelle Lücke. Eliminiert die Deprecation-Frist.
  - **C:** Weg von externen Action-Wrappern (manuelles `pip install uv` und `corepack enable pnpm` in den Workflow-Steps). – Konsequenzen: weniger Abhängigkeiten, mehr Workflow-Code, schlechteres Caching. Kein Mehrwert gegenüber B.
- **Entscheidung:** **Option B – sofort updaten plus Verifikations-Regime erweitern**. Pin auf konkreten Patch-Tag (Immutable-Tag-Trend, vgl. Modus-2-Schritt 10): `astral-sh/setup-uv@v8.1.0` (released 2026-04-16), `pnpm/action-setup@v6.0.5` (released 2026-05-02). `actions/checkout@v6`, `actions/setup-python@v6`, `actions/setup-node@v6`, `actions/upload-artifact@v4` bleiben als Major-Tag-Pin (GitHub-Org-Maintainer-Praxis hat dort Tag-Stabilität).
- **Konsequenzen:**
  - **Workflow-Pins aktualisiert** in `.github/workflows/ci.yml` und `.github/workflows/security.yml`. Re-Test der gesamten Pipeline auf dem PR-Branch.
  - **`project-context.md` Abschnitt 3** um Sub-Block „GitHub Actions" erweitert mit Verifikations-Stempel `Verifiziert: 2026-05-08` für jede Action. Damit greift Regel-001 (Versionsdisziplin) automatisch auch für Actions.
  - **`actionlint` als Pre-Commit-Hook** in `.pre-commit-config.yaml` ergänzt. Dieser Hook hätte den `hashFiles`-Job-Level-Bug aus Schritt 1.2 (Commit `f94ee93`) vor dem Push gefangen. Lokale Tooling-Disziplin senkt CI-Reibung.
  - **Klassifikation `[OPERATIV]`, nicht `[REAKTIV]`:** planmäßige Antwort auf bekannte Deprecation-Frist mit Vorlauf, kein Pivot wegen Implementierungsbug. Reaktiv-Quote bleibt 0/10.
  - **Action-Verifikations-Termine:** alle GitHub-Actions tragen ab dieser Entscheidung dieselben `Verifiziert: YYYY-MM-DD`-Stempel wie andere Stack-Komponenten. Major-Updates erfordern ADR, Patch-/Minor-Updates sind freigabefrei mit Stempel-Refresh.
- **Abgeleitete Regel:** Regel-015 (GitHub-Actions im Verifikations-Regime) – siehe Teil C.

---

#### ADR-011: psycopg LGPL-3.0-only akzeptiert plus Sub-Dependency-Lizenz-Regime

- **Datum:** 2026-05-09
- **Status:** Aktiv
- **Tags:** `[OPERATIV]` `[STACK]` `[METHODIK]`
- **Phasentyp-Kontext:** UMSETZUNG (Phase 1, im Anschluss an Schritt 1.5-Start)
- **Reifegrad-Wirkung:** keine Architektur-Reifegrad-Beförderungen; festigt aber den Stack-Eintrag „Procrastinate" als belastbar in seiner praktischen Realisierbarkeit (vorher offene Lizenz-Frage bei der Pflicht-Sub-Dep psycopg).
- **Kategorie:** Lizenz- und Compliance-relevante Änderung (CLAUDE.md Abschnitt 4 Punkt 8).
- **Kontext:** Beim Aufnehmen von `procrastinate` (gemäß ADR-002 strategisch fixierte Job-Engine) für Schritt 1.5 wurde die Pflicht-Sub-Dependency `psycopg` (psycopg3) sichtbar. Auf PyPI und im Upstream-LICENSE.txt mit License-Expression **`LGPL-3.0-only`** markiert. `project-context.md` Abschnitt 6 schließt GPL/LGPL als Backend-Dependency ohne ADR aus, mit der Begründung, dass einzelne Module später ohne Lizenz-Reibung als eigenständige Bibliotheken extrahierbar bleiben sollen. ADR-002 (Stack-Wahl) hatte diese transitive Lizenz-Frage nicht adressiert – das ist eine methodische Lücke, weil Modus-2-Schritt-2a (Versions-Verifikation) systematisch nur Top-Level-Komponenten erfasst und Sub-Dependencies offen lässt. Die Frage stellt sich jetzt akut, weil ohne psycopg keine Procrastinate-Realisierung möglich ist (kein anderer First-Class-Connector, kein gangbarer Job-Engine-Ersatz im Rahmen der Constraints aus ADR-002 und `project-context.md` Abschnitt 3).
- **Optionen:**
  - **A:** psycopg LGPL-3.0-only als transitive Dep akzeptieren, ADR-Folgeeintrag mit Begründung. – Konsequenzen: pragmatisch, technisch ohne Reibung. Erste echte LGPL-Akzeptanz im Projekt.
  - **B:** Procrastinate-Wahl revidieren, andere Job-Engine wählen. – Konsequenzen: Kein gangbarer Ersatz im Rahmen unserer Constraints. Taskiq, ARQ, Celery sind in `project-context.md` Abschnitt 3 explizit ausgeschlossen, SAQ in ADR-002 verworfen. Effektiv kein gangbarer Pfad ohne ADR-002-Kippung.
  - **C:** A plus Methodik-Regel: bei jeder neuen Stack-Komponente werden Pflicht-transitive Dependencies auf Lizenz geprüft und im ADR adressiert (nicht nur Top-Level-Lizenz). – Konsequenzen: schließt die methodische Lücke, die hier sichtbar wurde, und verhindert die Wiederholung bei künftigen Stack-Komponenten.
- **Entscheidung:** **Option C – psycopg akzeptieren plus Methodik-Regel.** Die LGPL-Akzeptanz für psycopg ist die einzige praktikable Variante, sobald procrastinate gesetzt ist. Zusätzlich wird die Modus-2-Schritt-2a-Disziplin auf Pflicht-Sub-Dependencies ausgedehnt, damit die nächste Stack-Komponente nicht erneut diese Reibung erzeugt.
- **Konsequenzen:**
  - **psycopg-Akzeptanz konkret abgegrenzt:** LGPL-3-Lib-Linking aus Python ist dynamisches Linking, der Standard-LGPL-konforme Pfad. AGPLv3-Hauptlizenz vereinbart sich. Die Modul-Extraktions-Strategie aus `project-context.md` Abschnitt 6 bleibt für **andere** Module gewahrt: `infra/tile-proxy`, der Routing-Adapter in `backend/geo` und ähnliche sauber gegen Job-Engine getrennte Module verwenden psycopg **nicht** und sind weiterhin ohne LGPL-Verschmutzung extrahierbar. Verschmutzung ist auf den Persistenz-/Job-Engine-Pfad beschränkt.
  - **`pyproject.toml`** nimmt `psycopg[binary,pool]` als **explizite** Runtime-Dependency auf (statt nur transitiv über procrastinate). Begründung: macOS-Entwicklung ohne System-libpq und Docker-Container ohne `apt-get install libpq5`-Schritt sind beide nur mit dem Binary-Wheel reproduzierbar; das `pool`-Extra ist ohnehin von procrastinate gefordert. Pin: aktuelles Patch-Tag `~=3.3.4` (analog zu Stack-Komponenten-Verifikations-Regime).
  - **`project-context.md` Abschnitt 3** – neuer Sub-Block-Eintrag „psycopg 3.3.4 (LGPL-3.0-only, transitive Pflicht-Dep zu procrastinate)" mit `Verifiziert: 2026-05-09`-Stempel; Eintrag bei „Compliance und Lizenz" um expliziten Verweis auf ADR-011 als Ausnahme von der LGPL-Restriktion erweitert.
  - **Klassifikation `[OPERATIV]`, nicht `[REAKTIV]`:** Die LGPL-Frage war prinzipiell aus procrastinates `pyproject.toml` ableitbar. Sie wurde in ADR-002 nicht erfasst, weil die damalige Modus-2-Methodik keine Sub-Dependency-Lizenz-Prüfung vorgesehen hat. Es ist eine nachgezogene Festlegung im Rahmen einer strategisch gesetzten Stack-Wahl, kein unerwarteter Pivot. Reaktiv-Quote bleibt 0/10.
  - **Methodische Lehre:** Sub-Dep-Lizenz-Prüfung wird in das Verifikations-Regime aufgenommen (Regel-016), greift bei jeder neuen Top-Level-Stack-Komponente.
- **Abgeleitete Regel:** Regel-016 (Sub-Dependency-Lizenz-Prüfung im Verifikations-Regime) – siehe Teil C.

---

#### ADR-012: actions/upload-artifact Major-Update v4 → v7 (Node-20-Deprecation)

- **Datum:** 2026-05-10
- **Status:** Aktiv
- **Tags:** `[OPERATIV]` `[STACK]` `[DEPLOYMENT]`
- **Phasentyp-Kontext:** UMSETZUNG (Phase 1, vor Schritt 1.8 — CI-Hygiene-Sonderfall analog zu ADR-010 vor Schritt 1.3).
- **Reifegrad-Wirkung:** keine direkten Architektur-Reifegrad-Beförderungen; festigt den Status der CI-Pipeline (`[BELASTBAR]`) gegen die Node-20-Deprecation-Frist (forced default 2026-06-02, Removal 2026-09-16).
- **Kategorie:** Externe Abhängigkeiten (CLAUDE.md Abschnitt 4 Punkt 3 – Major-Update bestehender Abhängigkeiten ist freigabepflichtig). Zusätzlich greift Regel-015: „Bei Deprecation-Warnings in CI-Annotations: Mini-ADR vor Ablauf der Frist anlegen".
- **Kontext:** ADR-010 (2026-05-08) hat `actions/upload-artifact@v4` bewusst als Major-Tag-Pin belassen mit der Begründung „GitHub-Org-Maintainer pflegen Tag-Stabilität". Diese Begründung schützt vor Pin-Bruch, nicht aber vor der Node-Runtime-Deprecation: `upload-artifact@v4` läuft auf Node.js 20 und löst seit mindestens 2026-05-09 in jedem CI-Run die Annotation `Node.js 20 actions are deprecated` aus. Patrick fragte am 2026-05-10 nach (Vermutung: zieht sich schon länger durch). Untersuchung der CI-Logs bestätigte: einzige verbleibende Node-20-Action im Workflow-Set ist `upload-artifact@v4` (alle anderen sind durch ADR-010 oder durch Major-Tag-Stabilität bereits auf Node 24). Hard-Deadlines laut GitHub-Blog: 2026-06-02 forced default auf Node 24 (kann v4 brechen), 2026-09-16 Node-20-Removal.
- **Optionen:**
  - **A:** Bump auf `actions/upload-artifact@v7` (Major-Tag, latest). v7.0.0 (2026-02-26) addiert nur additive Erweiterungen (`archive: false`-Option für Direct-Uploads, ESM-intern); keine API-Brüche für unsere Nutzung (nur `name`, `path`, `retention-days`). – Konsequenzen: Warnung beseitigt, Node-24-Runtime, ~12+ Monate Ruhe vor nächster Major-Erwartung. Re-Test der CI-Pipeline nötig.
  - **B:** Bump auf `actions/upload-artifact@v6` (Major-Tag). v6.0.0 (2025-12-12) ist die erste Version, die Node 24 default macht. – Konsequenzen: Warnung beseitigt, aber nächstes Major-Update v7 steht früher an; wir laufen erneut in eine Mini-ADR-Pflicht.
  - **C:** Nichts tun, bis die Frist näher rückt. – Konsequenzen: CI-Reibung mitten in einer UMSETZUNG-Phase, Verstoß gegen Regel-015 (Mini-ADR-Pflicht bei Deprecation-Warnings).
- **Entscheidung:** **Option A** — Bump auf `actions/upload-artifact@v7` (Major-Tag, gemäß ADR-010-Pin-Form-Regel: `actions/`-Org → Major-Tag, nicht Patch-Tag). Patrick freigegeben am 2026-05-10.
- **Konsequenzen:**
  - **Workflow-Pin aktualisiert** in `.github/workflows/ci.yml` an zwei Stellen (`test-backend`-Job und `test-frontend`-Matrix-Job). `security.yml` nutzt `upload-artifact` nicht; keine Änderung dort.
  - **`project-context.md` Abschnitt 3** Sub-Block „GitHub Actions": Eintrag von `actions/upload-artifact@v4` (`Verifiziert: 2026-05-08`) auf `actions/upload-artifact@v7` (`Verifiziert: 2026-05-10`) aktualisiert mit Verweis auf diesen ADR.
  - **Klassifikation `[OPERATIV]`, nicht `[REAKTIV]`:** planmäßige Antwort auf bekannte Deprecation-Frist mit Vorlauf, ausdrücklich von Regel-015 vorgesehen. Reaktiv-Quote bleibt 0 / 10 (zählt jetzt ADR-003 bis ADR-012).
  - **Strukturelle Konsistenz mit ADR-010:** ADR-010 hatte `setup-uv` und `pnpm/action-setup` aktualisiert, `upload-artifact` aber bewusst belassen. Diese Lücke war bei der damaligen Verifikation nicht sichtbar, weil v4 zum 2026-05-08 noch keine Deprecation-Annotation auf Job-Ebene auslöste oder die Annotation in den damaligen Run-Logs noch nicht auftauchte. Sie wurde sichtbar, sobald Frontend-Coverage-Uploads (1.7) eingeführt waren und die Annotation pro Job-Abschluss erschien. Methodische Lehre: zukünftige Verifikations-Runden lesen CI-Run-Logs auf Annotations gegen, nicht nur Versions-Verfügbarkeit auf der Releases-Seite.
  - **Re-Test der Pipeline** auf dem PR-Branch dieser Session. Erwartung: keine Node-20-Deprecation-Annotations mehr in `test-backend` oder `test-frontend`-Matrix.
- **Abgeleitete Regel:** keine neue Regel — Regel-015 hat den Fall bereits abgedeckt, dieser ADR ist die regelkonforme Anwendung.

#### ADR-013: Rate-Limit als eigener Valkey-Counter (vor Schritt 2.2)

- **Datum:** 2026-05-10
- **Status:** Aktiv
- **Tags:** `[OPERATIV]` `[STACK]` `[SECURITY]`
- **Phasentyp-Kontext:** UMSETZUNG (Phase 2, vor Schritt 2.2 — explizit im Fahrplan-Schritt-Text als „OPERATIVE Bibliotheks-Wahl per kleinem ADR vor Schritt-Beginn" verlangt).
- **Reifegrad-Wirkung:** keine direkten Modul-Reifegrad-Beförderungen durch den ADR selbst. Wirkt vorbereitend auf Schritt 2.2 (`backend/auth` → `[BELASTBAR]`) und Schritt 2.3 (`backend/auth_anonymous` → `[BELASTBAR]`); Pub/Sub-Pfad via Valkey bleibt `[VORLÄUFIG]` bis Phase 4.
- **Kategorie:** Externe Abhängigkeiten (CLAUDE.md Abschnitt 4 Punkt 3 — die Wahl _vermeidet_ eine neue Top-Level-Dependency, dokumentiert das aber als bewusste Entscheidung) plus Sicherheit (Punkt 6 — Rate-Limit ist Bestandteil der Login-Hardening-Schicht).
- **Kontext:** Schritt 2.2 verlangt eine Rate-Limit-Implementierung für `POST /api/auth/login` mit der in `project-context.md` Abschnitt 6 fixierten Spec „5 Fehlversuche pro 15 min pro IP-Adresse plus pro User getrennt". Schritt 2.3 verlangt analog ein Rate-Limit auf der AccessCode-Validierung in `backend/auth_anonymous` (architecture.md Modul-Block: „analog zu Login: 5 Fehlversuche pro 15 min pro IP"). Die Wahl trägt also für beide Auth-Module und ist im Fahrplan explizit als „kleiner ADR vor Schritt-Beginn" markiert.
- **Optionen:**
  - **A: `slowapi`** (Flask-Limiter-Port für Starlette/FastAPI). – Lizenz MIT (✓), aktiv gepflegt, Decorator-API. Storage pluggable über `limits`-Library: in-memory Default, Valkey/Redis möglich (Valkey ist Redis-protokoll-kompatibel). Multi-Key (IP + User) realisierbar. – Konsequenzen: Drei neue transitive Dependencies (`slowapi`, `limits`, `redis-py`), die alle der Versions-Verifikations-Disziplin (Regel-001) unterworfen sind. Funktional vollwertig, aber zusätzliche Wartungs-Oberfläche.
  - **B: `fastapi-limiter`** (async-native, Redis-only). – Konsequenzen: Strukturell dieselbe Risikoklasse wie `FastAPI-Users` und `passlib`, die in `project-context.md` Abschnitt 3 explizit als Maintenance-Falle benannt und vermieden wurden. Kein in-memory-Fallback. Kleinere und unsichere Maintainer-Basis.
  - **C: Eigener Valkey-basierter Counter.** ~80 Zeilen in `backend/eb_digital/auth/rate_limit.py`: `INCR key` plus `EXPIRE key 900` (Valkey `INCR` und `EXPIRE` sind einzeln atomar; das race-window für „IncrOhneExpire" hat keinen Sicherheits-Effekt, weil ein Limit-Slot maximal 15 min lebt). Multi-Key (IP + User) durch zwei Counter, beide müssen unter dem Schwellwert liegen. – Konsequenzen: keine neue Top-Level-Dependency, keine Versions-Verifikations-Pflicht in Folgeversionen. Erste produktive Valkey-Nutzung des Backends — Connection-Pool wird in 2.2 etabliert. Eigener Test-Aufwand höher (6–10 Tests inkl. Edge-Cases: Window-Rollover, Multi-Key-AND, Counter-Reset nach Erfolg).
- **Entscheidung:** **Option C** — eigener Valkey-basierter Counter. Patrick freigegeben am 2026-05-10.
- **Konsequenzen:**
  - **Konsistenz mit Auth-Philosophie:** dieselbe Argumentation, die in `project-context.md` Abschnitt 3 zu „kein FastAPI-Users, kein passlib" geführt hat, gilt für Rate-Limit noch stärker — Rate-Limit ist Counter-Logik, keine Krypto, eigener Code daher unkritisch im Threat-Modell.
  - **Neuer Modul-Bestandteil** in `backend/eb_digital/auth/rate_limit.py` (~80 Zeilen Async-Code) plus Tests. Coverage muss das Auth-Modul-Niveau erreichen (≥ 95 % Lines, ≥ 90 % Branches).
  - **Erste produktive Valkey-Nutzung des Backends:** Connection-Pool-Wiring in App-Lifespan (`lifespan`-Context oder Startup-Event), Health-Check-Erweiterung um Valkey-Reachability optional (Entscheidung im Detail-Plan zu 2.2).
  - **Wiederverwendung in Schritt 2.3:** AccessCode-Validierung nutzt dieselbe Rate-Limit-Schicht. Modul-Schnitt: Rate-Limit liegt in `backend/auth/rate_limit.py` (Auth-Querschnittsfunktion) und wird von `backend/auth_anonymous` importiert; alternativ in `backend/common/`-Modul, falls Schritt 2.3 zeigt, dass auch nicht-auth-bezogene Endpunkte (z. B. `register-tenant`) profitieren — Entscheidung in 2.3.
  - **Counter-Reset bei Erfolg:** Nach erfolgreichem Login wird der User-Counter zurückgesetzt (`DEL` auf User-Key); IP-Counter bleibt bestehen (würde sonst Brute-Force gegen viele Usernames vom selben IP nicht abfangen). Dokumentiert in der `rate_limit.py`-Modul-Docstring.
  - **Key-Konvention:** `auth:ratelimit:login:ip:<ip>` und `auth:ratelimit:login:user:<username>`; analog für anonymen AccessCode-Pfad. Redis/Valkey-Namespacing macht künftige Cross-Modul-Konflikte sichtbar.
  - **Keine Versions-Verifikations-Pflicht:** Der ADR fügt keinen Pin in `pyproject.toml` hinzu. Die Valkey-Client-Bibliothek (vermutlich `valkey-py` oder `coredis`) **wird** mit Schritt 2.2 als neue Dep geprüft und verifiziert — diese Sub-Entscheidung ist im Detail-Plan zu 2.2 zu klären (zwei Kandidaten haben unterschiedliche Maintenance-Lage; im Detail-Plan vorzulegen, kein eigener ADR nötig solange MIT/BSD/Apache-2.0).
- **Abgeleitete Regel:** keine neue allgemeine Regel — der Fall „Auth-Querschnittsfunktion → eigener Code statt Bibliothek" ist bereits durch die Auth-Philosophie in `project-context.md` Abschnitt 3 verankert. Dieser ADR ist deren operative Anwendung auf Rate-Limit.

---

#### ADR-014: Anbieter-Austauschbarkeit für externe Geo-Services als Architektur-Prinzip

- **Datum:** 2026-05-10
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[METHODIK]` `[MODUL]`
- **Phasentyp-Kontext:** UMSETZUNG (Phase 2, zwischen Schritt 2.1 ERLEDIGT und 2.2 OFFEN; strategische Klarstellung außerhalb der Schritt-Sequenz, ausgelöst durch Patrick-Direktive am 2026-05-10).
- **Reifegrad-Wirkung:** neuer Architektur-Bestandteil „NFR Anbieter-Austauschbarkeit für externe Geo-Services" auf `[BELASTBAR]` (durch diesen ADR fixiert). Reifegrad-Übersicht in `architecture.md` Abschnitt 9 entsprechend ergänzt; Stand-Datum auf 2026-05-10 aktualisiert.
- **Kategorie:** Architekturänderung als Architektur-Prinzip (CLAUDE.md Abschnitt 4 Punkt 1) — fixiert eine bisher implizite Architektur-Eigenschaft als bewusst geschütztes Prinzip.
- **Kontext:** Echtdaten-Recherche zu MapTiler am 2026-05-10 (Logbuch-BEOBACHTUNG vom selben Tag) ergab vier Befunde, die die externe Service-Abhängigkeit mit strategischer Reibung belasten:
  1. **AGB-Cache-Konflikt:** [MapTiler Cloud Terms](https://www.maptiler.com/terms/cloud/) verbieten serverseitiges Caching ohne ausdrückliche Sales-Approval und Zusatzgebühr — der geplante 7-Tage-nginx-Cache vor MapTiler Cloud (`project-context.md` Abschnitt 6 Performance, `architecture.md` Modul `infra/tile-proxy`) ist ohne Approval AGB-widrig.
  2. **Pricing-Modell-Unterschiede pro Provider:** MapTiler Cloud rechnet Sessions vs. Tile-Requests ab. Sessions sind nur mit dem MapTiler-eigenen SDK technisch zählbar (Frontend-Lock-in). MapLibre GL JS als Renderer erzwingt Tile-Request-Abrechnung. Dieser Cost-Optimierungs-Hebel ist provider-spezifisch und damit kein Architektur-Argument, sondern ein Provider-Argument.
  3. **Lizenz-/Compliance-Profile unterscheiden sich:** MapTiler Cloud Free Tier ist auf non-commercial use beschränkt; Multi-Tenant-B2B-Produktivnutzung schließt Free Tier aus, unabhängig von der AGPLv3-Lizenz der eigenen Software. MapTiler Server Standard schließt B2B/Multi-Tenant explizit aus; einziger Self-Hosting-Pfad ist Custom (kein öffentlicher Preis).
  4. **Eigenbetriebs-Pfade unterscheiden sich qualitativ:** MapTiler Server vs. OpenMapTiles+tileserver-gl haben unterschiedliche Daten-Qualitäts- und Operations-Aufwand-Profile.
     Gleichzeitig sind die Architektur-Naht (`backend/geo`-Adapter, `infra/tile-proxy`-Modul, MapLibre GL JS als Renderer ohne Provider-Bindung) bereits provider-neutral angelegt — diese Eigenschaft war bisher _implizit_ und wäre durch eine vermeintlich pragmatische Wahl (z. B. „wir nutzen MapTiler SDK JS für die Cost-Optimierung") leise verloren gegangen. Patrick-Direktive 2026-05-10: „EB-Digital so konzeptionieren, dass die Anbieter bei Bedarf gewechselt werden können". Dieser ADR überführt die Direktive in ein bewusst geschütztes Architektur-Prinzip.
- **Optionen:**
  - **A:** Provider-Lock-in pragmatisch akzeptieren (z. B. MapTiler SDK JS für Sessions-Cost-Vorteil im Frontend, MapTiler-spezifische Aufrufe in Backend-Modulen jenseits von `backend/geo`). – Konsequenzen: Cost-Vorteil heute, aber Hand bei jedem Provider-Vertragswechsel oder AGB-Update gebunden; Vendor-Lock-in im Frontend; Pfad zu OSS-Stack nur mit Frontend-Refactoring möglich.
  - **B:** Provider-Neutralität als bewusst geschütztes Architektur-Prinzip fixieren. Externe Geo-Service-Integration läuft ausschließlich über Adapter-Module mit provider-neutralen Schnittstellen. Frontend-Renderer-Wahl: MapLibre GL JS als provider-neutraler Default. Wechsel zu provider-spezifischem SDK (MapTiler SDK JS) erfordert eigenen ADR mit expliziter Lock-in-Begründung. – Konsequenzen: Cost-Optimierung über Sessions im Frontend wird ADR-gesperrt (kein stilles Drift); Pfad zu OSS-Stack oder MapTiler Server Custom bleibt als Adapter-Tausch möglich; Pflicht zur Adapter-Schnittstellen-Dokumentation pro externer Service-Integration; Phase-1-Architektur ist für diesen Pfad bereits korrekt geschnitten — keine Code-Umstrukturierung nötig.
  - **C:** Multi-Provider-Aktivbetrieb von Tag 1 (zwei aktive Provider-Adapter mit Failover). – Konsequenzen: doppelter Implementations-/Verifikations-/Test-Aufwand; in Phase 1 ohne demonstrierten Bedarf Over-Engineering.
- **Entscheidung:** **Option B** — Anbieter-Austauschbarkeit als Architektur-Prinzip fixieren. Patrick freigegeben am 2026-05-10 mit Direktive „EB-Digital so konzeptionieren, dass die Anbieter bei Bedarf gewechselt werden können".
- **Konsequenzen:**
  - **Geltungsbereich:** Tile-Provider (heute MapTiler Cloud), Geocoding-Provider (heute MapTiler Cloud), Routing-Provider (heute TomTom), künftige externe Dienste mit Geo-/Karten-Bezug. Implizit auch alle externen HTTP-API-Abhängigkeiten mit erkennbarem Alternativanbieter (SaaS-Auth ist bereits durch `project-context.md` Abschnitt 3 „Explizit nicht erlaubt" ausgeschlossen).
  - **Adapter-Pflicht:** Jede externe Service-Integration läuft ausschließlich über `backend/geo`-Adapter-Klassen (oder analoge Adapter in anderen Backend-Modulen) mit provider-neutralen Schnittstellen-Definitionen (Methoden-Signaturen, Datentypen, Fehler-Verhalten). Provider-spezifische Aufrufe, Datenstrukturen oder Endpunkte leben **ausschließlich** im Adapter; aufrufende Module dürfen sie nicht kennen.
  - **Frontend-Renderer-Wahl ist Architektur-Entscheidung:** MapLibre GL JS bleibt provider-neutraler Default. Wechsel zu MapTiler SDK JS (oder einem analogen provider-spezifischen SDK) erfordert separaten ADR mit Begründung des akzeptierten Lock-ins, Bezifferung des Cost-/UX-Vorteils und Plan zum Rück-Wechsel-Aufwand.
  - **Pflichten beim Hinzufügen eines neuen externen Service:**
    1. Adapter-Modul mit provider-neutraler Schnittstelle vor erster produktiver Nutzung definiert und in `architecture.md` Abschnitt 4 als Schnittstelle dokumentiert.
    2. Mindestens ein Alternativanbieter im aufnehmenden ADR oder im `project-context.md` Abschnitt 5 dokumentiert.
    3. Wechselpfad als Adapter-Austausch beschrieben (welche Methoden-Signaturen müssen erfüllt sein, welche Datentypen sind kanonisch).
  - **Kein Multi-Provider-Aktivbetrieb in Phase 1:** Prinzip schützt die _Möglichkeit_ des Wechsels, nicht die laufende parallele Verfügbarkeit. Ein einzelner aktiver Adapter pro Service-Typ reicht.
  - **Wirkung auf bestehende Recherche-Befunde 2026-05-10:**
    - **AGB-Cache-Konflikt** wird als offene Klärung in `project-context.md` Abschnitt 11 geführt (vor Phase-6-Tile-Proxy-Implementierung zu klären); kein direkter Konflikt mit dem Prinzip, weil das Prinzip die Wechselbarkeit, nicht die Gegenwarts-Wahl betrifft.
    - **maptiler-sdk-js-Frontend-Lock-in** wird durch dieses Prinzip explizit ADR-pflichtig — wenn der Sessions-Cost-Vorteil nutzbar gemacht werden soll, muss ein eigener ADR die Akzeptanz begründen.
    - **MapTiler Server Custom als Self-Hosting-Pfad** bleibt offen; das Prinzip ändert nichts an der Phase-1-Wahl MapTiler Cloud, hält aber den Migrationspfad als reiner Adapter-Austausch sauber.
  - **Klassifikation `[STRATEGISCH]`, nicht `[REAKTIV]`:** strategische Architektur-Entscheidung aus Patrick-Direktive, kein nachgezogener Pivot. Reaktiv-Quote bleibt 0/10 (zählt jetzt ADR-005 bis ADR-014).
- **Verworfene Alternativen** (siehe Optionen A und C oben; werden in `architecture.md` Abschnitt 8 aufgenommen):
  - **A: Provider-Lock-in pragmatisch akzeptieren** – verworfen, weil strategische Flexibilität wichtiger als Cost-Optimierung in Phase 1; MapTiler-AGB-Risiken (Cache-Klausel, Free-Tier-Restriktion, Multi-Tenant-Restriktion bei Server Standard) zeigen, wie schnell sich Provider-Bedingungen ändern können; Patrick-Direktive 2026-05-10 fordert explizit Wechselbarkeit.
  - **C: Multi-Provider-Aktivbetrieb von Tag 1** – verworfen, weil Over-Engineering ohne demonstrierten Phase-1-Bedarf; doppelter Implementations-/Verifikations-/Test-Aufwand.
- **Wirkung auf bestehende Architektur und ADRs:**
  - **ADR-002 (Stack-Wahl)** bleibt gültig; konkrete Provider (MapTiler, TomTom) bleiben in Phase 1 fixiert. Dieser ADR fixiert nur, dass die Schnittstelle provider-neutral bleiben muss.
  - **ADR-003 (Architektur-Pattern)** bleibt gültig; das Prinzip ergänzt eine bisher implizite Eigenschaft des Modular-Monolith-Patterns ohne Modul-Schnitt-Änderung.
  - **`architecture.md` Abschnitt 1 Überblick** wird um die Prinzip-Aussage als zusätzlichen Kommunikations-Grundmodus-Bullet ergänzt (`[BELASTBAR]`).
  - **`architecture.md` Abschnitt 6 NFRs** wird um eine neue Sub-Sektion „Wartbarkeit / Portabilität" ergänzt mit dem Anbieter-Austauschbarkeits-Prinzip als belastbarer NFR.
  - **`architecture.md` Abschnitt 8 Verworfene Alternativen** wird um „Provider-Lock-in pragmatisch akzeptieren" und „Multi-Provider-Aktivbetrieb in Phase 1" ergänzt.
  - **`architecture.md` Abschnitt 9 Reifegrad-Übersicht** bekommt eine neue Zeile „NFR Anbieter-Austauschbarkeit für externe Geo-Services" als `[BELASTBAR]` mit Verweis auf diesen ADR.
  - **`project-context.md` Abschnitt 11 MapTiler-Eintrag** wird vollständig konsolidiert (Renderer/Provider-Trennung, AGB-Cache-Befund, Free-Tier-Restriktion, Sessions-vs-Requests-Detail, vier Migrationspfade A/B/C/D mit aktualisierter Trigger-Liste, Begriffsklärung MapTiler vs. MapLibre).
- **Abgeleitete Regel:** Regel-017 (Anbieter-Austauschbarkeit für externe Services) – siehe Teil C.

#### ADR-015: `get_db_session()` als FastAPI-yield-Dependency mit Rollback (Lifecycle-Bug-Fix Schritt 2.5b)

- **Datum:** 2026-05-15
- **Status:** Aktiv
- **Tags:** `[REAKTIV]` `[STACK]` `[SECURITY]` `[METHODIK]`
- **Phasentyp-Kontext:** UMSETZUNG (Hot-Stabilisierungs-Schritt 2.5b zwischen 2.5 und 2.6).
- **Reifegrad-Wirkung:** Modul-Reifegrade `backend/auth`, `backend/auth_anonymous`, `backend/tenants` bleiben `[BELASTBAR]` (Bug betraf den Querschnitts-Lifecycle, nicht die fachliche Funktionalität — der Fix bestätigt die request-scoped Architektur-Absicht). Die Dependency-Lifecycle-Garantie selbst wird im Architektur-Modul-Eintrag `backend/auth` als Modul-übergreifende Eigenschaft `[BELASTBAR]` aufgenommen.
- **Kategorie:** Sicherheit und Datenschutz (CLAUDE.md Abschnitt 4 Punkt 6 — Auth-Endpunkte hängen an dieser Dependency) + Methodik (neue Regel für Resource-Dependencies).
- **Kontext:** Externer Verdachtsbericht 2026-05-15 (Patrick) zu `backend/eb_digital/auth/api.py:103` `get_db_session()`. Implementierung war:

  ```python
  async def get_db_session(request: Request) -> AsyncSession:
      ...
      async with factory() as session:
          return session  # ← __aexit__ feuert HIER
  ```

  Das `return` innerhalb des `async with` löst `AsyncSession.__aexit__()` **vor** der Endpoint-Ausführung aus → SQLAlchemy schließt die Session und rollbackt offene Transaktionen. SQLAlchemy 2.0 `AsyncSession` ist lazy bei Connection-Acquisition, daher funktionieren die Endpoints oberflächlich (erste Operation erwirbt eine neue Connection), aber:
  1. **Die neue Connection liegt außerhalb des `async with`-Cleanup** — FastAPI hat keinen Finalizer für `return`-Dependencies. Cleanup hängt am unzuverlässigen `__del__` der Session.
  2. **Bei Exception vor `await db.commit()`** wird kein Rollback ausgelöst — die Connection bleibt potenziell ‚idle in transaction‘ im Pool.
  3. **Unter Last** (Vision-Annahme 50 Disponenten + 500 Einsatzkräfte, `project-context.md` Abschnitt 2) drohen Connection-Pool-Erschöpfung und steigende Latenzen.

  Die Dependency wird von 9 Endpoints aller drei `[BELASTBAR]`-Module konsumiert (`backend/auth`, `backend/auth_anonymous`, `backend/tenants`). Bestehende API-Tests überschreiben sie per `dependency_overrides` mit Stubs und maskieren den Lifecycle-Bug; der einzige direkte Lifecycle-Test prüfte nur `isinstance(...)`.

- **Optionen:**
  - **A: Minimaler Code-Fix als Hot-Stabilisierungs-Schritt 2.5b** — `return` durch `yield` ersetzen, expliziter `await session.rollback()` im Exception-Pfad. Lifecycle-Tests umgeschrieben (Counter-Stub für Enter/Exit/Rollback). Real-DB-Validierung über bestehenden `dev-smoke.sh` mit Slug-Kollision als Exception-Pfad-Probe. Bestehende explizite Endpoint-`await db.commit()` bleiben unverändert. ADR + neue Regel-018 dokumentieren das Muster für künftige Resource-Dependencies. — Konsequenzen: 3-Zeilen-Code-Change, niedriges Risiko (offizielles FastAPI-Muster), Methodik-Lerneffekt für künftige Connection-/Pipeline-Dependencies.
  - **B: Größere Unit-of-Work-Umstellung** — Dependency committet selbst bei Endpoint-Erfolg, rollbackt sonst. Endpoints verlieren ihre expliziten `await db.commit()`-Aufrufe. — Konsequenzen: Anpassung aller 9 Endpoints + Use-Cases, hoher Test-Refactor, eigener `[STRATEGISCH]`-ADR. Geht über das Bug-Fix-Bedürfnis hinaus, mischt zwei Themen.
  - **C: Fix-only ohne Methodik-Regel** — wie A, aber ohne Regel-018 und ohne Architektur-Spec-Anpassung. — Konsequenzen: Wiederholungs-Risiko in künftigen Modulen mit Resource-Dependencies (Procrastinate-Connection, Valkey-Pipelines), Vision-Driven-Development verliert die Lerngelegenheit.
- **Entscheidung:** **Option A**. Patrick-Freigabe 2026-05-15 nach Vorlage der drei Optionen mit Empfehlung A (Bug-Tiefe rechtfertigt Methodik-Regel; Unit-of-Work-Wechsel ist eigene Architekturfrage; Reaktiv-Quote bleibt mit 1/10 = 10 % unter Schwellenwert).
- **Konsequenzen:**
  - **Code:** [backend/eb_digital/auth/api.py](backend/eb_digital/auth/api.py) `get_db_session()` umgestellt auf `async def get_db_session(request) -> AsyncIterator[AsyncSession]` mit Muster `async with factory() as session: try: yield session except Exception: await session.rollback(); raise`. Type-Annotation auf `AsyncIterator[AsyncSession]` umgestellt; `# type: ignore[no-any-return]` nicht mehr nötig.
  - **Tests:** [backend/tests/test_auth_login_api.py](backend/tests/test_auth_login_api.py) — bestehender `test_get_db_session_invokes_factory_and_returns_session` zu `test_get_db_session_yields_session_within_open_context` umgeschrieben (echter Lifecycle mit Counter); neuer `test_get_db_session_rollbacks_and_propagates_on_exception` ergänzt (Exception-Pfad mit Rollback-Verifikation); bestehender `test_get_db_session_raises_without_app_state` an async-Generator-Semantik angepasst (`gen.__anext__()` statt direkter Aufruf).
  - **Smoke:** [scripts/dev-smoke.sh](scripts/dev-smoke.sh) erweitert um Exception-Fall-Probe (Slug-Kollision auf `/register-tenant` → 409 → Folge-`/api/health` muss innerhalb 1 s antworten — verifiziert Connection-Rückgabe im Exception-Pfad gegen echtes PostgreSQL im Compose-Stack).
  - **Architektur-Spec:** [architecture.md](docs/architecture.md) Modul-Einträge `backend/auth`, `backend/auth_anonymous`, `backend/tenants` ergänzt um Hinweis „Request-Scoped DB-Session via FastAPI-yield-Dependency mit explizitem Rollback im Exception-Pfad" als modul-übergreifende Eigenschaft.
  - **Reaktiv-Quote:** 0/10 → 1/10 = 10 % über die letzten 10 ADRs (ADR-006 bis ADR-015). Unter dem 20 %-Schwellenwert für Klasse G; keine Reflexion nötig, aber im nächsten Phasen-Anfang als Beobachtung führen.
  - **Endpoint-`await db.commit()` bleiben erhalten** (Patrick-Direktive: kein Unit-of-Work in 2.5b). Eine spätere zentrale Commit-/Rollback-Strategie wäre eigener `[STRATEGISCH]`-ADR.
  - **`auth_anonymous` und `tenants` benötigen keine Code-Änderung** — sie konsumieren `get_db_session` per `Depends(...)`, FastAPI erkennt automatisch yield-Generatoren. Auch die existierenden `dependency_overrides` in den Test-Suiten funktionieren unverändert (FastAPI erlaubt sowohl return- als auch yield-Override-Funktionen).
- **Verworfene Alternativen:**
  - **B (Unit-of-Work):** zu großer Scope, mischt zwei Architektur-Themen (Lifecycle-Bug + Commit-Strategie). Wird als spätere `[STRATEGISCH]`-Option offengehalten, falls Phase-7-Stabilisierung das Endpoint-Commit-Boilerplate als zu fehleranfällig markiert.
  - **C (kein Methodik-Regel):** verliert den Querschnitts-Lerneffekt. Procrastinate (PsycopgConnector als eigener Pool) und Valkey-Pipelines werden in Phase 4 ähnliche Resource-Dependency-Muster verlangen — Regel-018 schützt vor Wiederholung.
- **Wirkung auf bestehende ADRs:**
  - ADR-002 (Stack-Wahl) bleibt gültig; FastAPI-yield-Dependency ist offizielles Stack-Muster.
  - ADR-003 (Architektur-Pattern Modular Monolith) bleibt gültig; Request-Scoped-DB-Session ist Eigenschaft der Backend-Schicht, kein Modul-Schnitt.
  - ADR-013 (Rate-Limit als Valkey-Counter) bleibt gültig; betroffene `incr_and_check`-Calls sind eigenständige `redis.asyncio`-Operationen ohne Lifecycle-Wechselwirkung mit der DB-Session.
- **Abgeleitete Regel:** Regel-018 (FastAPI-Resource-Dependencies mit Context-Manager nutzen `yield`, nicht `return`) — siehe Teil C.

---

#### ADR-016: Verzicht auf serverseitiges Caching vor externen Geo-Services

- **Datum:** 2026-05-17
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[MODUL]` `[STACK]` `[PERFORMANCE]`
- **Phasentyp-Kontext:** UMSETZUNG (zwischen Schritt 2.7 ERLEDIGT und 3.1 OFFEN; strategische Klarstellung außerhalb der Schritt-Sequenz, ausgelöst durch Patrick-Direktive 2026-05-17).
- **Reifegrad-Wirkung:** Modul `infra/tile-proxy` Verantwortung ändert sich strukturell (Cache entfällt); Schnittstelle S7 (Geo → Tile-Proxy) bleibt `[VORLÄUFIG]` — wird in Phase 6 unter neuer Cache-freier Annahme zu `[BELASTBAR]` befördert. NFR-Eintrag „Tile-Caching ≥ 7 Tage TTL" wird ersetzt durch „Browser-/Service-Worker-Cache als alleinige Cache-Schicht". Eintrag „NFR Cache-Strategie für externe Geo-Services" in `architecture.md` Abschnitt 9 wird auf `[BELASTBAR]` (durch diesen ADR fixiert).
- **Kategorie:** Architekturänderung (CLAUDE.md §4 Punkt 1) — strukturelle Aufgabe-Änderung des Moduls `infra/tile-proxy` plus Anpassung NFR Performance.
- **Kontext:**
  - **2026-05-10 (BEOBACHTUNG):** MapTiler Cloud Terms verbieten serverseitiges Caching ohne Sales-Approval. Geplanter 7-Tage-nginx-Cache wäre AGB-widrig. Triage damals: Sales-Anfrage als Phase-7-Roadmap-Meilenstein.
  - **2026-05-17 (Recherche):** TomTom ToS Clause 11.4 verbietet ebenfalls serverseitiges Multi-Client-Caching. Ein Provider-Wechsel löst das Cache-Problem **nicht** — beide Branchenführer haben dieselbe Constraint. Detail in `project-context.md` Abschnitt 11 (Eintrag „TomTom-Provider-Strategie: konsolidierte Befunde (Recherche 2026-05-17)").
  - **2026-05-17 (Patrick-Direktive):** „ich wäre bereit, auf Caching zu verzichten." Damit ist eine architektur-saubere Lösung statt Sales-Verhandlungen wählbar.
  - Konsequenz: `infra/tile-proxy` muss neu definiert werden — entweder Cache mit Sales-Approval, oder kein Cache und vereinfachte Verantwortung.
- **Optionen:**
  - **A:** Vollständiger Verzicht auf serverseitiges Caching. `infra/tile-proxy` wird zum reinen Reverse-Proxy mit API-Key-Inject und Rate-Limit-Schutz; kein `proxy_cache_path`-Block. Browser-Cache (Default-TTL je Provider) und PWA-Service-Worker-Cache (Spike L) bleiben einzige Cache-Schichten. — Konsequenzen: AGB-konform für MapTiler und TomTom; keine Sales-Verhandlung nötig; Architektur vereinfacht; weniger Operations-Aufwand; Phase-7-Roadmap-Meilenstein „MapTiler-Sales-Anfrage" entfällt. API-Budget-Druck steigt deutlich — bei Großlage 500 Einsatzkräfte ohne Server-Cache vermutlich jenseits MapTiler-Flex-Tier ($25), realistisch Unlimited-Tier ($295/Monat) oder TomTom-Pay-as-you-grow mit Overage. Constraint „~50 €/Monat" aus `project-context.md` Abschnitt 6 ist dann nicht haltbar — Anpassung Pflicht. Spike L (Phase 5) wird kritischer Hebel: Service-Worker-Pre-Cache des Operations-Raums vor Schichtbeginn reduziert API-Hit-Rate erheblich. PWA-Offline-Tauglichkeit profitiert. Risiko: keine Glättung von Tile-Request-Spitzen, jeder Cold-Cache-Browser triggert vollen Tile-Request-Schwall.
  - **B:** Sales-Approval-Pfad weiter verfolgen (Status quo aus BEOBACHTUNG 2026-05-10). MapTiler-Sales-Anfrage als Phase-7-Meilenstein behalten, mit Zusatz-Fee verhandeln; TomTom-Routing-Cache als Backend-Performance-Cache argumentieren (Graubereich). — Konsequenzen: Cache erlaubt, ~50 €/Monat-Budget hält mit Flex-Tier + Cache-Hit-Rate; aber Sales-Aufwand, mögliche Zusatz-Fees (Höhe unbekannt), erhöhte Provider-Bindung; TomTom-Cache-Graubereich bleibt — separate Klärung mit TomTom-Support nötig; Phase 6 ist eingangsblockiert, bis Sales-Antworten vorliegen; Architektur bleibt komplex.
  - **C:** Self-Hosting-Schwenk (Pfad-C aus ADR-014). Tiles selbst hosten (OpenMapTiles + tileserver-gl auf OSM-Extracts); Geocoding und Routing extern lassen. — Konsequenzen: keine API-Constraints mehr für Tiles; Tile-Volumen ist der Hauptbudget-Hebel; hoher operativer Aufwand (10–30 GB Storage, Update-Pipeline, Style-Pflege); Daten-Qualität merklich unter MapTiler Cloud; Adapter-Tausch ist nach ADR-014/Regel-017 strukturell möglich; Modulgrößen-Schub für `infra/tile-proxy`.
- **Entscheidung:** **Option A** — Verzicht auf serverseitiges Caching. Patrick-Freigabe 2026-05-17 nach Vorlage der drei Optionen in `docs/proposals/2026-05-17-cache-verzicht-und-spike-g.md` und Empfehlung A (Patrick-Bereitschaft, Budget-Constraint anzupassen statt Architektur-/Vertrags-Komplexität aufzubauen).
- **Konsequenzen:**
  - **Geltungsbereich:** alle externen Geo-Service-Aufrufe (heute MapTiler-Tiles, MapTiler-Geocoding, TomTom-Routing). Implizit auch alle künftigen externen Geo-Service-Integrationen, sofern die Provider-ToS Multi-Client-Caching verbieten — was als Default angenommen wird, bis eine konkrete Lizenz Cache ausdrücklich erlaubt.
  - **`infra/tile-proxy` neue Verantwortung:** API-Key-Inject (Backend-seitige Geheimhaltung der Provider-Keys), Rate-Limit-Schutz (vor versehentlichem Budget-Verbrauch durch Programmfehler), Reverse-Proxy-Routing (Pfade `/tiles/maptiler/*`, `/geocoding/maptiler/*`, `/routing/tomtom/*`). **Kein** `proxy_cache_path`-Block, **kein** Tile-Cache-Volume.
  - **Cache-Control-Header-Pass-Through:** `infra/tile-proxy` reicht die `Cache-Control`-Header der Upstream-Provider 1:1 an den Client weiter. Browser-Cache greift damit gemäß Provider-Default (MapTiler 4 h dokumentiert; TomTom gemäß Tile-Response-Header).
  - **PWA-Service-Worker-Cache (Spike L) bleibt unverändert geplant** und wird kritischer Hebel zur Glättung der Last. Vor Schichtbeginn lädt der Service Worker den Operations-Raum proaktiv — das ist Client-Cache pro End-User, ToS-konform bei beiden Providern.
  - **Endpoint-Routing-Cache im `backend/geo`-Adapter (60 s für identische Start/Ziel-Paare) entfällt** — gleicher AGB-Konflikt bei TomTom Clause 11.4. Wiederholungs-Schutz ausschließlich über das 30-s-Fahrzeug-Throttle im Adapter (`project-context.md` Abschnitt 6 Performance).
  - **API-Budget-Constraint:** initiale ~50 €/Monat-Annahme bleibt vorerst stehen, ist aber **vor Phase-7-Lasttest neu zu validieren** unter neuer Cache-freier Annahme. Budget-Anhebung wird ADR-pflichtige Entscheidung nach der Messung (Schritt 7.1).
  - **Phase-7-Roadmap-Meilenstein „MapTiler-Sales-Anfrage" entfällt** durch diesen ADR. Pfad bleibt als Eskalations-Option offen (über ADR-014/Regel-017), falls die Phase-7-Messung das Budget reißt.
  - **Verworfene Alternativen** (siehe Optionen B und C oben; werden in `architecture.md` Abschnitt 8 aufgenommen):
    - **B: Sales-Approval-Pfad** – verworfen, weil Patrick architektur-saubere Lösung der Vertragslösung vorzieht; Sales-Zusatz-Fee unbekannt; Phase-6-Eingangsblockade durch externe Antwortzeiten unerwünscht.
    - **C: Self-Hosting tileserver-gl in Phase 1** – verworfen wegen Operations-Aufwand und Daten-Qualitäts-Verlust gegenüber MapTiler Cloud; bleibt als Eskalations-Pfad offen, falls Phase-7-Lasttest zeigt, dass Budget nicht tragbar ist.
  - **Klassifikation `[STRATEGISCH]`, nicht `[REAKTIV]`:** strategische Architektur-Entscheidung aus Patrick-Direktive, kein nachgezogener Pivot. Reaktiv-Quote bleibt 1/10 = 10 % (zählt jetzt ADR-007 bis ADR-016).
- **Wirkung auf bestehende ADRs:**
  - **ADR-002 (Stack-Wahl)** bleibt gültig; nginx als `infra/tile-proxy`-Basis bleibt unverändert, nur die Cache-Konfiguration entfällt.
  - **ADR-003 (Architektur-Pattern)** bleibt gültig; Modul-Schnitt unverändert.
  - **ADR-014 (Anbieter-Austauschbarkeit)** bleibt gültig; Cache-Verzicht ist orthogonal zur Provider-Wechselbarkeit. Pfade B/C/D aus ADR-014-Kontext bleiben als spätere Eskalations-Optionen offen.
- **Folge-Edits in diesem Commit:**
  - `architecture.md` Abschnitt 1 (Kommunikations-Grundmodi), Abschnitt 3 (Modul `infra/tile-proxy`), Abschnitt 4 (Schnittstelle S7), Abschnitt 6 (NFR Performance), Abschnitt 8 (Verworfene Alternativen), Abschnitt 9 (Reifegrad-Übersicht).
  - `project-context.md` Abschnitt 6 (Performance-Bullets Tile-Caching, Routing-Aufrufe, API-Budget), Abschnitt 11 (Hinweis ADR-016 → MapTiler-AGB-Cache-Konflikt obsolet, Routing-Caching-Graubereich obsolet).
  - `fahrplan.md` Zeile 20 (Hinweis zu Phase-7-Sales-Anfrage gestrichen), Schritt 5.4 (Spike L erhöhter Stellenwert), Schritt 6.1 (Tile-Cache-Steuerung gestrichen, Cache-Control-Pass-Through ergänzt), Schritt 7.1 (Lasttest erweitert um Budget-Validierung).
- **Abgeleitete Regel:** keine neue allgemeine Regel — ADR-014/Regel-017 deckt die übergeordnete Wechselbarkeit ab; ADR-016 ist eine konkrete Cache-Architektur-Entscheidung mit Geltungsbereich „externe Geo-Services unter Provider-ToS mit Cache-Restriktion".

---

#### ADR-017: Geo-Plausibilitäts-Algorithmus — Hülle-Distanz plus dynamische GPS-Toleranz

- **Datum:** 2026-05-18
- **Status:** Aktiv
- **Tags:** `[ERKENNTNIS]` `[PERFORMANCE]` `[MODUL]`
- **Phasentyp-Kontext:** ERKUNDUNG (Schritt 3.1 Spike I).
- **Reifegrad-Wirkung:** `[OFFEN]`-Bereich „Geo-Plausibilitäts-Algorithmus" in den Modulen `backend/operations` und `backend/geo` → `[VORLÄUFIG]`. Modul-Reifegrade selbst bleiben `[VORLÄUFIG]`.
- **Kategorie:** Architekturänderung — konkretisiert den `PlausibilityChecker` als `[VORLÄUFIG]`-Komponente in `backend/geo` und seine Aufruf-Schnittstelle zu `backend/operations`. Nicht produktiv-Code-veränderlich (Phase 4 implementiert).
- **Kontext:**
  - `project-context.md` Abschnitt 6 (Sicherheit) verlangt eine Plausibilitätsprüfung von Einsatzkraft-Bestellungen mit Disponenten-Moderation bei Schwellenwert-Überschreitung (Default 5 km, pro Einsatz anpassbar). Bisher waren Distanz-Metrik, GPS-Ungenauigkeits-Modellierung, Behandlung fehlender oder unsicherer GPS-Werte und Konfigurations-Verankerung als `[OFFEN]` markiert in `architecture.md` Modulen `backend/operations` und `backend/geo`.
  - Spike I (Zeitbox 4 h) sollte diese Lücken über einen Reißbrett-Vergleich zweier GPS-Toleranz-Varianten an einem synthetischen Test-Datensatz (Bremen Innenstadt + Osterdeich-/Weserstadion-Bereich) klären.
  - Patrick-Direktive vor Spike-Start: (1) Hülle-vs-Centroid-Frage am länglichen Osterdeich-Polygon klären; (2) zwei Varianten vergleichen — A pauschal vs. B dynamisch `2·accuracy`; (3) 500-m-Moderationsfilter für GPS-Ausreißer aufnehmen; (4) keine Kalman-Filter-Modellierung (Overkill für Einzelbestellungen ohne Zeitserie).
- **Optionen:**
  - **A — Centroid-Distanz + pauschaler 30-m-Aufschlag:** Distanz misst vom GPS-Punkt zum Polygon-Centroid (Mittelpunkt). GPS-Ungenauigkeit als feste Konstante. — Konsequenzen: Algorithmisch einfacher, aber bricht bei länglichen Polygonen (P6 Osterdeich, 1500 m × 200 m): eine Einsatzkraft am Rand ist 0 m von der Hülle entfernt, aber bis zu 750 m vom Centroid. Bei engen Einsatz-Schwellenwerten (z. B. 500 m für punktuelle Lagen) führt Centroid zu False-Moderation legitimer Bestellungen. **Nicht zutreffend** für unsere Polygon-Klassen.
  - **B — Hülle-Distanz + pauschaler 30-m-Aufschlag (Variante A im Spike):** Distanz misst zum nächsten Punkt auf der Polygon-Hülle. GPS-Ungenauigkeit als feste Konstante 30 m. — Konsequenzen: Distanz-Metrik korrekt; aber Tolerance-Modell ignoriert die vom Client gemeldete `accuracy`. Konkret problematisch bei T7 (50 m außen, accuracy 80 m im Stadtkern): Variante A akzeptiert (50+30=80<100), obwohl die Person realistisch bis zu 210 m außen stehen könnte. Auch problematisch bei T8 (80 m außen, accuracy 5 m gutes GPS): Variante A moderiert unnötig.
  - **C — Hülle-Distanz + dynamische GPS-Toleranz `2·accuracy` (Variante B im Spike):** Distanz zur Hülle; Tolerance ist `2·accuracy_m` (95-%-Konfidenz unter Annahme `accuracy` = 1-Sigma-Radius). Plus 500-m-Moderationsfilter für `accuracy_m > 500`, plus Text-Standort-Behandlung als `MODERATION_NO_GPS`. — Konsequenzen: Tolerance passt sich der realen GPS-Qualität an: konservativ in Funklöchern (T7), präziser bei gutem Fix (T8). Distanz-Metrik geometrisch korrekt für alle Polygon-Formen. Algorithmus weiterhin synchron in O(N·K) (<1 ms typisch), kein Bounding-Box-Pre-Filter nötig. Min/Max-Untergrenze auf accuracy (5 m) schützt vor unrealistischen 0-Werten. Audit-Log persistiert Distanz und accuracy, aber keine Roh-Koordinaten (DSGVO-konform, `project-context.md` Abschnitt 6 Datenschutz).
- **Entscheidung:** **Option C** — Hülle-Distanz plus dynamische GPS-Toleranz `2·accuracy_m`. Plus dreistufige Konfigurations-Hierarchie: Plattform-Konstante (Moderations-Schwelle, Min/Max-Grenzen) → Mandant-Default (`tenant.plausibility_default_threshold_m`, Default 5 000 m) → optionaler Einsatz-Override (`operation.plausibility_threshold_m`).
- **Konsequenzen:**
  - **Algorithmus-Spezifikation** liegt im Spike-Ergebnis-Dokument `docs/spikes/spike-i-results.md` mit Test-Datensatz, Pseudocode und Durchrechnen aller Test-Punkte. Phase-4-Implementation übernimmt diese Spezifikation 1:1.
  - **Reaktion auf GPS-Qualität:** Bestellungen mit `accuracy > 500 m` (Cell-Tower-only-Locating) landen automatisch in Moderation. Schwellenwert ist in Phase 1 Plattform-Konstante, nicht mandanten-konfigurierbar.
  - **Text-Standort / fehlendes GPS** wird **moderiert, nicht abgelehnt**: legitime Gründe für GPS-Fehlen sind Funklöcher, Permission-Verweigerung, Metalldach-Fahrzeuge. Disponent ist im Loop und entscheidet.
  - **Konfigurations-Hierarchie** mit additivem Schema-Migrations-Bedarf in Phase 4: zwei neue Felder mit CHECK-Constraints (50 ≤ Schwellenwert ≤ 50 000).
  - **Performance:** synchroner Aufruf im Order-Endpunkt, kein Procrastinate-Job. Bounding-Box-Pre-Filter nicht in Phase 4 nötig.
  - **Datenschutz / Logging:** Audit-Log speichert Plausibility-Outcome plus `distance_m`, `accuracy_m`, `threshold_m`, `variant`. Roh-Koordinaten gehen nicht ins Log; falls Standort-Bezug operativ nötig, nur als gehashter Tile-Identifier (Web-Mercator). Persistenz der Roh-Koordinaten in der Order-Tabelle unterliegt der 30-Tage-Anonymisierung.
  - **Sicherheits-Einordnung:** Der Plausibilitäts-Check ist **nicht** als Sicherheitsmechanismus zu verstehen. Client-gemeldete GPS-Punkte können manipuliert sein. Filter reduziert Disponenten-Last bei gutwilligen, aber fehl-positionierten Bestellern. Threat-Model-Notiz in der späteren Auth-Stack-Security-Review (Phase 7.2) aufnehmen.
  - **Geometrie-Bibliothek:** Phase 4 nimmt Shapely 2.0+ als Backend-Dependency auf (BSD-3, ADR-002-kompatibel; GEOS dynamisch geladen, MIT). Sub-Dependency-Lizenz-Prüfung gemäß Regel-016 in Phase 4 dokumentieren.
  - **Klassifikation `[ERKENNTNIS]`, nicht `[REAKTIV]`:** Ergebnis eines geplanten Spike-Schritts (3.1). Reaktiv-Quote bleibt 1/10 = 10 % (zählt jetzt ADR-008 bis ADR-017).
- **Wirkung auf bestehende ADRs:**
  - **ADR-006 (Aggregations-Schema):** Erweiterung um `count_orders_moderated*` Felder wäre nutzbringend, aber nicht zwingend für Phase 4. Bewertung beim Phase-4-Implementation des Aggregats; falls Stakeholder-Nutzen bestätigt, additive Erweiterung von ADR-006 oder Folge-ADR.
  - **ADR-008 (Audit-Log):** Plausibility-Outcome plus Distanz und accuracy wird Audit-Log-Bestandteil bei jeder Order-Anlage.
  - **ADR-002, ADR-003** bleiben unverändert.
- **Folge-Edits in diesem Commit:**
  - `architecture.md` Modul `backend/operations` (Plausibility-Check als `[VORLÄUFIG]` benennen, ADR-017-Verweis); Modul `backend/geo` (Komponente `PlausibilityChecker` als `[VORLÄUFIG]`); Abschnitt 9 Reifegrad-Übersicht (zwei `[OFFEN]`-Einträge → `[VORLÄUFIG]`).
  - `fahrplan.md` Schritt 3.1 auf `[ERLEDIGT]` plus Aktueller-Stand-Block.
  - `docs/spikes/spike-i-results.md` als Spike-Messprotokoll (neue Datei).
- **Abgeleitete Regel:** keine neue allgemeine Regel. ADR-017 ist eine konkrete Algorithmus-Entscheidung mit Geltungsbereich „Plausibilitätsprüfung Einsatzkraft-Bestellungen in `backend/operations`/`backend/geo`".

#### ADR-018: Bündelungs-Trigger (Spike J)

- **Datum:** 2026-05-28
- **Status:** Aktiv
- **Tags:** `[ERKENNTNIS]` `[MODUL]` `[DATENMODELL]`
- **Phasentyp-Kontext:** ERKUNDUNG (Spike J, Phase 3, Zeitbox 4 h)
- **Reifegrad-Wirkung:** `[OFFEN]`-Bereich „Bündelungs-Trigger" in Modul `backend/operations` → `[VORLÄUFIG]`. Schnittstelle S4 offene Frage „Verhalten bei Bündelung" gelöst. Datenmodell-Vorgabe für Phase 4.3: neue Entity `order_bundle`, neue nullable Spalte `order.bundle_id`, neue nullable Spalte `order_assignment.bundle_id`. ADR-006 wird additiv um Aggregat-Spalte `bundled_order_count` ergänzt (kein Re-Open von ADR-006, sondern dokumentierte Spike-J-Erweiterung; Schema-Migration `operation_aggregate` in Phase 6 Schritt 6.5 nimmt das mit auf). Mit dieser Beförderung ist Phase 3 (Spikes Wave 1) vollständig abgeschlossen.
- **Kategorie:** Datenmodelländerung (neue Entity + zwei neue FK-Spalten) + Methodik (Use-Case-Spec)
- **Kontext:**
  - Vision §3: Versorgungs-Transporter hat drei Modi inkl. „Großbestellungs-Modus = bedient gebündelte Bestellungen an grob gleicher Örtlichkeit".
  - Vision §9 offener Punkt: „Bündelungs-Trigger – durch wen (System / Disponent / Versorgungs-Transporter-Crew), bei welchem Schwellenwert."
  - `architecture.md` Modul `backend/operations` Use-Case `BundleOrders` (`[OFFEN]`).
  - Schnittstelle S4 offene Frage: „Verhalten bei Bündelung – ob ein Bündelungs-Auftrag eine Assignment-Aggregation braucht, hängt von Spike J ab."
  - ADR-006 Aggregat-Feld `bundling_count` ohne Semantik-Festlegung (Aktion-Anzahl vs. Order-Anzahl).
  - Fahrplan §944 Vermutung: Phase-1-Wahl = manuell durch Disponent.
  - Spike I (ADR-017, 2026-05-18) hatte die parallele `[OFFEN]`-Lücke in `backend/operations` geklärt. ADR-018 schließt die zweite Lücke und damit Phase 3.
- **Optionen (je Designfrage):**
  - **Auslöser-Initiative:**
    - A: Manuell durch Disponent (UI-Aktion „Bündeln"). Phase-1-robust, keine Schwellenwert-Kalibrierung nötig.
    - B: System-Heuristik (automatisch oder Vorschlag). Cluster-Algorithmus + Radius- + Zeitfenster-Schwelle erforderlich, ohne Pilot-Daten nicht sinnvoll kalibrierbar.
    - C: Carer-Crew-Eingabe vor Ort. Verlangt Carer-PWA-UI (Phase ≥ 6); verschiebt Initiative vom strategischen Disponenten zum operativen Carer.
    - D: Hybrid – System-Vorschlag + Disponent-Bestätigung.
  - **Datenstruktur:**
    - A: Eigene `order_bundle`-Entity + nullable `order.bundle_id` FK.
    - B: Bündel-Order als konsolidierte neue Order (Original-Orders → `bundled_into`). Bricht 1:1-Beziehung Order↔Einsatzkraft.
    - C: Implizit über gemeinsamen Versorgungs-Transporter-Assignment (keine Entity, Heuristik im Aggregat).
  - **Versorgungs-Transporter-Zwang:**
    - A: Ja – nur Versorgungs-Transporter mit `mode='large_order'`. Vision-konsistent.
    - B: Nein – jedes Fahrzeug mit ausreichender Beladung. Lockerer, Vision-Intent verletzt.
  - **Räumliche Voraussetzung backend-seitig:**
    - A: Keine harte Validierung in Phase 1. Disponent prüft visuell.
    - B: System-Validierung mit Radius-Constraint (z. B. `operation.bundle_radius_m`). Willkürlicher Default ohne Pilot-Daten.
  - **`bundling_count`-Semantik:**
    - A: Anzahl Bündel-Aktionen + zusätzliches Feld `bundled_order_count` (Summe Orders).
    - B: Anzahl gebündelte Orders (verschiebt ADR-006-Semantik).
    - C: Beides als zwei Felder, ohne Erweiterung von ADR-006 (nur `bundling_count` = Aktionen).
- **Entscheidung:** **A / A / A / A / A** — Empfehlungs-Kombination. Patrick-Freigabe 2026-05-28 nach Detail-Plan-Vorlage in der Spike-J-Session.
  1. **Auslöser:** Manuell durch Disponent. System-Heuristik und Carer-Crew-Eingabe explizit auf spätere Phase verschoben; Re-Evaluation per ADR, falls Pilot zeigt, dass manueller Workflow zu aufwändig wird.
  2. **Datenstruktur:** Eigene `order_bundle`-Entity + nullable `order.bundle_id` FK + nullable `order_assignment.bundle_id` FK.
  3. **Versorgungs-Transporter-Zwang:** Ja. `vehicle.mode='large_order'`-Pflichtprüfung im `BundleOrders`-Use-Case.
  4. **Räumliche Voraussetzung:** Keine harte Backend-Validierung in Phase 1. „Grob gleicher Örtlichkeit" ist UI-Empfehlung.
  5. **Aggregat-Semantik:** `bundling_count` = Bündel-Aktionsanzahl (ausgenommen `dissolved`). **Additive Erweiterung von ADR-006:** zusätzliches Feld `bundled_order_count` (Summe Orders).
  6. **Zusatz-Constraint aus Spike-Analyse:** Minimum **2 Orders** pro Bündel. Bündel mit 0 oder 1 Order ist Validierungsfehler (`MinimumTwoOrders`/`EmptyBundle`).
- **Konsequenzen:**
  - **Datenmodell-Migration Phase 4.3:**

    ```sql
    CREATE TABLE order_bundle (
        id UUID PRIMARY KEY,
        operation_id UUID NOT NULL REFERENCES operation(id),
        vehicle_id UUID NOT NULL REFERENCES vehicle(id),   -- Versorgungs-Transporter
        created_by_dispatcher_id UUID NOT NULL REFERENCES dispatcher_user(id),
        created_at TIMESTAMPTZ NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('active','completed','dissolved'))
    );
    ALTER TABLE "order" ADD COLUMN bundle_id UUID NULL REFERENCES order_bundle(id);
    ALTER TABLE order_assignment ADD COLUMN bundle_id UUID NULL REFERENCES order_bundle(id);
    ```

    Endgültiger Tabellenname für `order` (SQL-reserved Wort) wird in Phase 4.3 final festgelegt.

  - **`backend/operations.BundleOrders`-Use-Case-Vertrag:**

    ```python
    async def bundle_orders(
        *,
        order_ids: list[UUID],            # mindestens 2
        vehicle_id: UUID,                  # Versorgungs-Transporter im Großbestellungs-Modus
        dispatcher_id: UUID,               # Akteur, S10-Teilnahme geprüft
        operation_id: UUID,                # Defense-in-depth
        operation_repo: OperationRepository,
        vehicle_repo: VehicleRepository,
        order_repo: OrderRepository,
        bundle_repo: OrderBundleRepository,
        audit_logger: AuditLogger,
    ) -> OrderBundle:
        # (1) Berechtigung: dispatcher_id ist Teilnehmer der operation_id (Regel-014)
        # (2) Minimum-Constraint: len(order_ids) >= 2 -> sonst MinimumTwoOrders
        # (3) Vehicle-Validierung: Versorgungs-Transporter mit mode='large_order'
        # (4) Order-Validierung: alle order_ids gehören zu operation_id,
        #     Status 'pending', order.bundle_id IS NULL
        # (5) Erzeuge OrderBundle(status='active'), setze order.bundle_id für alle Orders
        # (6) Erzeuge N OrderAssignment-Einträge (eines pro Order) mit identischer bundle_id
        #     und identischem vehicle_id (= Versorgungs-Transporter)
        # (7) Audit-Log: action_type='orders_bundled',
        #     payload={'bundle_id': ..., 'order_ids': [...], 'vehicle_id': ...}
        # (8) Publish 'operation.{op}.orders_bundled' an backend/realtime
    ```

  - **Fehlerklassen:**
    - `MinimumTwoOrders` (422) — `len(order_ids) < 2` (Sonderfall: leere Liste behandelt als `EmptyBundle`)
    - `EmptyBundle` (422) — `order_ids == []`
    - `VehicleNotSupplyTransporter` (422) — Fahrzeug ist reguläres Betreuungsfahrzeug
    - `VehicleNotInLargeOrderMode` (422) — Versorgungs-Transporter, aber `mode != 'large_order'`
    - `OrderNotInOperation` (422) — Order gehört zu anderer Operation
    - `OrderNotPending` (422) — Order-Status ≠ pending
    - `OrderAlreadyBundled` (422) — `order.bundle_id IS NOT NULL`
    - `NotParticipant` (403) — Dispatcher nicht Teilnehmer (S10/Regel-014)

  - **S4 (Vehicle Assignment) — Bündel-Mapping:** N OrderAssignment-Einträge mit identischer `bundle_id` und identischem `vehicle_id` (= Versorgungs-Transporter). Kein NULL-Constraint auf `order_id` nötig, Aggregations-Joins bleiben einheitlich. Offene Frage in S4 ist damit aufgelöst.

  - **Lifecycle-Use-Cases in Phase 4.3 (skizziert):**
    - `DissolveBundle`: bundle.status='dissolved', alle `order.bundle_id=NULL`, Assignments des Bündels storniert, Orders zurück Status `pending`. Audit-Log `action_type='bundle_dissolved'`.
    - `CompleteBundle`: implizit, wenn alle gebündelten Orders Status `completed` erreichen → bundle.status='completed'.
    - **Stornierung einzelner Orders innerhalb aktivem Bündel in Phase 1 nicht erlaubt** — nur kompletter Bündel-Cancel oder Auflösung. Reduziert Phase-1-Komplexität.

  - **`operation_aggregate`-Erweiterung (additiv zu ADR-006):**
    - `bundling_count` (de: `anzahl_buendelungen`): Anzahl `order_bundle` mit `status IN ('active','completed')` pro Operation. `dissolved` zählt nicht (sonst verzerrt durch Storno-Wellen).
    - **Neu:** `bundled_order_count` (de: `anzahl_gebuendelte_bestellungen`): Summe Orders über alle gezählten Bündel.
    - **Klarstellung zu ADR-006:** ADR-006-Metriken-Set bleibt gültig; `bundled_order_count` ist Spike-J-Ergänzung. Schema-Migration `operation_aggregate` in Phase 6.5 nimmt das mit auf.

  - **Re-Evaluation per ADR**, falls Phase-7-Pilot zeigt: manueller Bündelungs-Workflow zu aufwändig → System-Heuristik (Option 1.B/1.D) nachziehen mit Pilot-Daten als Kalibrierungs-Basis.

- **Test-Datensatz (Operation O mit Fahrzeugen + 5 Orders im pending-Status):**

  Operation O:
  - Versorgungs-Transporter `VT1` mit `mode='large_order'`
  - Versorgungs-Transporter `VT2` mit `mode='off'`
  - Reguläres Betreuungsfahrzeug `F1`
  - Dispatchers `D1`, `D2` (Teilnehmer); `D_other` (Nicht-Teilnehmer)
  - Orders `O1..O5` (alle Status `pending`, alle in Operation O)
  - Order `OX` aus anderer Operation

  | #   | Szenario                                 | Eingabe                                          | Erwartetes Ergebnis                                                                                |
  | --- | ---------------------------------------- | ------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
  | B1  | Standard-Bündelung                       | order_ids=[O1,O2,O3], vehicle=VT1, dispatcher=D1 | OrderBundle(status=active), O1/O2/O3.bundle_id=B, 3 Assignments mit bundle_id=B, Audit-Log-Eintrag |
  | B2  | Versorgungs-Transporter falscher Modus   | vehicle=VT2 (mode='off')                         | 422 `VehicleNotInLargeOrderMode`                                                                   |
  | B3  | Reguläres Fahrzeug statt Transporter     | vehicle=F1                                       | 422 `VehicleNotSupplyTransporter`                                                                  |
  | B4  | Order bereits gebündelt                  | order_ids=[O1,O4] (O1 schon in B1)               | 422 `OrderAlreadyBundled`                                                                          |
  | B5  | Order aus anderer Operation              | order_ids=[O1, OX]                               | 422 `OrderNotInOperation`                                                                          |
  | B6  | Bündel mit 1 Order                       | order_ids=[O1]                                   | 422 `MinimumTwoOrders`                                                                             |
  | B7  | Leeres Bündel                            | order_ids=[]                                     | 422 `EmptyBundle`                                                                                  |
  | B8  | Dispatcher nicht Teilnehmer              | dispatcher=D_other                               | 403 `NotParticipant`                                                                               |
  | B9  | Bündel-Auflösung                         | DissolveBundle(bundle_id=B nach B1)              | bundle.status=dissolved, O1/O2/O3.bundle_id=NULL, Orders zurück pending, Audit-Log                 |
  | B10 | Aggregat: 2 Bündel mit 3+4 Orders        | nach Operation-Ende, 1 active, 1 completed       | operation_aggregate.bundling_count=2, bundled_order_count=7                                        |
  | B11 | Aggregat: aufgelöstes Bündel zählt nicht | nach Operation-Ende, 1 active + 1 dissolved      | operation_aggregate.bundling_count=1, bundled_order_count=(nur die aktiven)                        |

- **Wirkung auf bestehende ADRs:**
  - **ADR-006 (Aggregations-Schema):** additiv erweitert um `bundled_order_count`. Aggregat-Felder-Anzahl wächst von 16 auf 17. Klarstellung: `bundling_count` ist Bündel-Aktionsanzahl, ausgenommen `dissolved`.
  - **ADR-008 (Audit-Log):** Erweiterung um `action_type IN ('orders_bundled','bundle_dissolved','bundle_cancelled')`. Kein neuer ADR — Regel-011 deckt das Muster.
  - **ADR-017** (Geo-Plausibilität): unberührt; ADR-018 schließt die zweite `[OFFEN]`-Lücke in `backend/operations` und damit Phase 3.
  - **ADR-002, ADR-003, ADR-014, ADR-016:** unberührt.
- **Abgeleitete Regel:** keine neue allgemeine Regel — Bündelungs-Trigger ist ein konkreter Use-Case-Mechanismus, kein wiederkehrendes Muster. Existierende Regeln (Regel-011 Audit-Log, Regel-014 Teilnahme-Filter) greifen.

---

#### ADR-019: Phase-4-Sonderregel — UMSETZUNG-Eingangsdisziplin für Modul-Beförderungs-Phasen

- **Datum:** 2026-05-28
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[METHODIK]`
- **Phasentyp-Kontext:** UMSETZUNG (Phase 4, vor Schritt 4.1)
- **Reifegrad-Wirkung:** Keine direkten Architektur-Reifegrad-Beförderungen. Klärt die Eingangs-Disziplin für die UMSETZUNG-Schritte 4.1–4.6 als Voraussetzung dafür, dass diese Schritte ihre Module von `[VORLÄUFIG]` auf `[BELASTBAR]` befördern dürfen.
- **Kategorie:** Methodik.
- **Kontext:** Phase 4 (Operations Core + Realtime + Einsatzkraft-PWA, UMSETZUNG) berührt die Module `backend/catalog`, `backend/fleet`, `backend/operations`, `backend/realtime`, `frontend-einsatzkraft`. Alle fünf sind heute `[VORLÄUFIG]`; sie werden **durch** die Phase-4-Schritte erst zu `[BELASTBAR]` befördert (Phase-4-Reifegrad-Erwartung im Fahrplan-Kopf). Eine strikte Anwendung der UMSETZUNG-Eingangsdisziplin aus dem Schritt-Format (`fahrplan.md` „Schritt-Format": „bei UMSETZUNG: alle berührten Architektur-Bestandteile auf [BELASTBAR]") würde Phase 4 unmöglich machen, weil das Modul gleichzeitig Eingangsbedingung **und** Output des Schritts wäre. Phase 1 hatte für genau dieselbe Situation eine explizite Sonderregel im Phasen-Kopf (`fahrplan.md` Phase-1-Block, Zeile 136); Phase 2 hat dieselbe Sonderregel implizit in der Reflexion (2026-05-16) angewendet — aber nicht im Phasen-Kopf dokumentiert.
- **Optionen:**
  - **A:** Phase-2-Sonderregel sinngemäß übertragen + im `fahrplan.md` vor Phase 4 als „Hinweis Sonderregel" ergänzen (Schreibarbeit, kein ADR — analoge Anwendung eines etablierten Phasen-Patterns).
  - **B:** Eigener Mini-ADR `[STRATEGISCH] [METHODIK]` (Phase-4-Sonderregel formal als Entscheidung; eine Spur mehr Formalismus, dafür reproduzierbar für künftige UMSETZUNG-Phasen, im ADR-Index auffindbar).
  - **C:** Strikt anwenden, jeden berührten Bestandteil vor Schritt 4.1 separat per ADR auf `[BELASTBAR]` erklären — überdimensioniert, da kein Bestandteil ohne Funktion belastbar gemacht werden kann.
- **Entscheidung:** **Option B – Mini-ADR**. Begründung Patrick (Detail-Plan-Freigabe 2026-05-28): reproduzierbare Methodik-Setzung für alle künftigen UMSETZUNG-Phasen, die Module von `[VORLÄUFIG]` auf `[BELASTBAR]` heben sollen — die Sonderregel ist damit auffindbar im ADR-Index statt nur im `fahrplan.md`-Kontext einer Phase versteckt.
- **Konsequenzen:**
  - **Regel-Formulierung (siehe Abgeleitete Regel unten):** Eine UMSETZUNG-Phase, deren Hauptzweck die Beförderung berührter Module von `[VORLÄUFIG]` auf `[BELASTBAR]` ist, gilt diese Module **am Schrittbeginn als hinreichend belastbar, um den Schritt starten zu lassen**, sofern (a) der Modul-Schnitt durch einen ADR strategisch fixiert ist (heute: ADR-002, ADR-003, ADR-009), (b) die **konsumierten** Bestandteile außerhalb der zu befördernden Module (Plumbing, andere Module, Schnittstellen) tatsächlich `[BELASTBAR]` sind, und (c) der Detail-Plan vor Code-Eingriff jeden berührten Bestandteil benennt.
  - **Anwendung auf Phase 4:**
    - Konsumierte `[BELASTBAR]`-Bestandteile vor 4.1 (Catalog): Plumbing (Schritt 1.4), `backend/auth` (2.2), `backend/auth_anonymous` (2.3), `backend/tenants` + S10 (2.4), Request-Scoped DB-Session-Dependency (2.5b), Regel-013/014 (Operation↔Tenant-Filter).
    - Schrittweise Beförderung im Phasenverlauf: 4.1 → `backend/catalog` belastbar; 4.2 → `backend/fleet`; 4.3 → `backend/operations` + S3/S4 + I3 + ADR-017/ADR-018-Datenmodelle; 4.4 → `backend/realtime` + S9 + Pub/Sub via Valkey; 4.5 → `frontend-einsatzkraft` (funktional; Architektur-Pattern-Beförderung weiter ausstehend bis Phase 6); 4.6 → Tests/Coverage-Anker.
  - **`fahrplan.md`:** Hinweis vor Phase 4 als „Hinweis Sonderregel" mit Verweis auf diesen ADR (analog Phase-1-Hinweis-Block).
  - **Geltungsbereich über Phase 4 hinaus:** die abgeleitete Regel-019 gilt **generisch** für jede UMSETZUNG-Phase, die berührte Module von `[VORLÄUFIG]` auf `[BELASTBAR]` heben soll. Damit auch für Phase 6 (Geo + PWAs + Resilience + Retention + Export) anwendbar — keine erneute ADR-Pflicht in Phase 6.
  - **Klassifikation `[STRATEGISCH]`, nicht `[REAKTIV]`:** planmäßige Methodik-Setzung vor Phase-Start, keine Reaktion auf einen Implementierungsbug. Reaktiv-Quote bleibt 1 / 10 (Fenster wandert auf ADR-010 bis ADR-019; ADR-015 weiterhin einziger reaktiver Eintrag).
- **Abgeleitete Regel:** Regel-019 (UMSETZUNG-Sonderregel für Modul-Beförderungs-Phasen) – siehe Teil C.

---

#### ADR-020: Shapely 2.1.2 + GEOS LGPL-2.1 als Pflicht-Sub-Dep akzeptiert

- **Datum:** 2026-05-28
- **Status:** Aktiv
- **Tags:** `[OPERATIV]` `[STACK]` `[METHODIK]`
- **Phasentyp-Kontext:** UMSETZUNG (Phase 4, Schritt 4.3a, Sub-Dep-Lizenz-Prüfung gemäß Regel-016 vor Aufnahme der Top-Level-Dependency `shapely`).
- **Reifegrad-Wirkung:** Keine direkten Architektur-Beförderungen. Klärt die Lizenz-Zulässigkeit der Shapely-Aufnahme in `pyproject.toml` als Voraussetzung dafür, dass der ADR-017-Plausibility-Algorithmus mit Shapely implementiert werden kann (Schritt 4.3a).
- **Kategorie:** Lizenz und Compliance.
- **Kontext:**
  - ADR-017 (Spike I) schreibt **Shapely 2.0+** als Backend-Dependency vor („Phase 4 nimmt Shapely 2.0+ als Backend-Dependency auf (BSD-3, ADR-002-kompatibel; GEOS dynamisch geladen, MIT)"). Die Lizenz-Angabe „GEOS … MIT" war faktisch falsch — GEOS ist seit Beginn LGPL-2.1.
  - **Regel-016** (Herkunft ADR-011) fordert: Pflicht-Sub-Dependencies neuer Top-Level-Komponenten werden vor Aufnahme gegen die Erlaubt-/Ausschluss-Liste in `project-context.md` §6 geprüft.
  - `project-context.md` §6 listet **GPL/LGPL** als Backend-Dependency ausgeschlossen ohne ADR. Aktive Ausnahme bisher: **psycopg 3 LGPL-3.0-only** durch **ADR-011** (Pflicht-Sub-Dep von `procrastinate`).
  - Verifikation am **2026-05-28** auf offiziellen Quellen:
    - **Shapely 2.1.2** (released 2025-09-24): **BSD 3-Clause**, Quelle [pypi.org/project/shapely](https://pypi.org/project/shapely/).
    - **GEOS ≥ 3.9** (Pflicht-Runtime-Dep, im Binary-Wheel von Shapely mitgeliefert): **LGPL-2.1**, Quelle [libgeos.org](https://libgeos.org/) („GEOS is available under the terms of GNU Lesser General Public License (LGPL)" mit Link auf LGPL-2.1).
    - `numpy ≥ 1.21` (Pflicht-Runtime-Dep): **BSD 3-Clause**.
- **Optionen:**
  - **A: Shapely + GEOS-LGPL-Ausnahme akzeptieren** (analog ADR-011 für psycopg). Geltungsbereich beschränken auf den Plausibility-/Geo-Pfad. — Konsequenzen: ADR-017 ist 1:1 umsetzbar; präzise und reproduzierbare Geometrie-Operationen; LGPL-Lizenz „verschmutzt" den extrahierbaren Umfang von `backend/geo`. Strategische Wahl gegen Cost (Lizenz-Ausnahme) zugunsten Nutzen (etablierte, geprüfte Geometrie-Bibliothek).
  - **B: Eigenimplementierung point-to-polygon-distance in reinem Python** ohne Shapely (Closest-Point-on-Segment-Algorithmus pro Polygon-Kante, dann Minimum). — Konsequenzen: keine LGPL-Sub-Dep, keine zusätzliche externe Abhängigkeit; aber Eigenimplementierungs-Risiko bei Edge-Cases (degenerierte Polygone, exakte Vertex-Distanzen, numerische Stabilität bei sehr kleinen Polygonen). Würde ADR-017 widersprechen, das explizit Shapely vorsieht; bräuchte einen additiven ADR „Shapely-Verzicht zugunsten Eigenimplementierung".
  - **C: Andere Geometrie-Bibliothek mit permissiver Lizenz.** Realistische Kandidaten: keine ausgereifte BSD-/MIT-Alternative mit vergleichbarer Reife. PyGEOS wurde 2022 in Shapely 2.0 zurückfusioniert; turfpy hat begrenzten Reifegrad und nutzt selbst Shapely indirekt. — Konsequenzen: kein gangbarer Kandidat ohne Re-Evaluation.
- **Entscheidung:** **Option A** — Shapely 2.1.2 in `pyproject.toml` als Backend-Dependency aufnehmen; GEOS LGPL-2.1 ausnahmsweise akzeptiert.
- **Konsequenzen:**
  - **`pyproject.toml`-Eintrag:** `shapely>=2.1.2,<3` als Backend-Dep (`backend/pyproject.toml`), `Verifiziert: 2026-05-28` als Pflicht-Vermerk in `project-context.md` §3.
  - **Geltungsbereich der LGPL-Ausnahme:** beschränkt auf den **Plausibility-/Geo-Pfad** (`backend/eb_digital/geo/plausibility.py`, `backend/eb_digital/operations/use_cases.py::PlaceOrder` als Konsument). Module ohne Geometrie-Bezug (`backend/auth`, `backend/auth_anonymous`, `backend/tenants`, `backend/catalog`, `backend/fleet`, `backend/operations`-Use-Cases ohne Plausibility-Aufruf, `backend/realtime`, `backend/resilience`, `backend/retention`, `backend/export`, `infra/tile-proxy`, `infra/reverse-proxy`) bleiben extraktions-fähig ohne LGPL-Verschmutzung.
  - **Korrektur zu ADR-017:** Lizenz-Aussage „GEOS dynamisch geladen, MIT" wird durch ADR-020 als faktisch falsch markiert. GEOS ist LGPL-2.1 (verifiziert 2026-05-28 auf libgeos.org). Inhaltliche Spezifikation von ADR-017 (Algorithmus, Tolerance-Modell, dreistufige Konfigurations-Hierarchie) bleibt unverändert. **Folge-Edit in dieser Session:** ADR-017-Konsequenz „GEOS dynamisch geladen MIT" wird nicht inline gepatcht (ADRs sind chronologisch); ADR-020 fungiert als Lizenz-Korrektur.
  - **Reaktiv-Quote:** ADR-020 ist `[OPERATIV]` (planmäßige Sub-Dep-Prüfung im Rahmen von Schritt 4.3a, keine Reaktion auf einen Bug). Fenster wandert auf ADR-011 bis ADR-020; ADR-015 bleibt einziger `[REAKTIV]`-Eintrag. Reaktiv-Quote bleibt 1 / 10 = 10 % unter dem 20 %-Schwellenwert (Klasse G).
  - **Sub-Dependency-Disziplin:** Regel-016 wurde sauber durchlaufen (Top-Level-Komponente `shapely` mit ihren Pflicht-Sub-Dependencies `geos` + `numpy` gegen die Lizenz-Listen geprüft; ein Treffer auf eine ausgeschlossene Lizenz hat den ADR ausgelöst, keinen Verzicht).
- **Abgeleitete Regel:** keine neue allgemeine Regel — Regel-016 (Sub-Dep-Lizenz-Prüfung) ist die Quell-Regel; ADR-020 ist konkrete Anwendung. Liste der akzeptierten LGPL-Ausnahmen in `project-context.md` §6 wird um Shapely/GEOS ergänzt (Pflege-Hinweis im Folge-Commit).

---

#### ADR-021: Spike G — Routing-Wechsel auf self-hosted Valhalla (TomTom-K.-o. für permanente Sperrungen)

- **Datum:** 2026-06-10
- **Status:** Aktiv
- **Tags:** `[ERKENNTNIS]` `[MODUL]` `[STACK]` `[PERFORMANCE]`
- **Phasentyp-Kontext:** ERKUNDUNG (Phase 5, Schritt 5.1 / Spike G)
- **Reifegrad-Wirkung:** `[OFFEN]`-Bereich „Sperrungs-Override-Technik" in `backend/geo` → `[VORLÄUFIG]`; S7-`[OFFEN]`-Anteil „Sperrungs-Override-Aufrufschema" → `[VORLÄUFIG]`. Routing-Adapter-Spezifikation in `backend/geo` von TomTom auf Valhalla umgestellt (Beförderung auf `[BELASTBAR]` mit Phase-6-Implementierung 6.1).
- **Kategorie:** Externe Abhängigkeiten + Architekturänderungen (Adapter-Tausch nach ADR-014/Regel-017, kein Modul-Refactor).
- **Kontext:** Patrick-Direktive 2026-05-17 verlangt, dass vom Routing-Provider als gesperrt geführte Straßen auf Disponenten-Freigabe **befahrbar** gemacht werden (Reverse-Override) — bei Innenstadt-Großlagen (Fußgängerzonen, Absperrungen) der Kern-Use-Case. Spike-G-Empirie 2026-06-10 ([`docs/spikes/spike-g-results.md`](spikes/spike-g-results.md)): **TomTom Orbis v2 kann permanente Sperrungen nicht erzwingen** — `supportingPoints` weicht selbst bei 19 dichten Punkten exakt auf der Fußgängerzonen-Polyline aus (T2) und verweigert die Einbahn-Gegenrichtung (T3); es existiert kein öffentlicher Parameter zum Aufheben von Zufahrtsbeschränkungen. Traffic-Sperrungen sind ignorierbar (T1, `traffic=historical`), Sperren via `avoidAreas` möglich (nur Rechtecke). **Valhalla 3.7.0 erfüllt alle Szenarien** (`ignore_access`, `ignore_oneways`, `exclude_polygons`/`exclude_locations`, 3-Call-Komposition gegen globales Flag-Scoping).
- **Optionen:**
  - **A: TomTom-only, Anforderung (b) streichen** — Reverse-Override nur für Traffic-Sperrungen; Vision-Klarstellung nötig; Kern-Use-Case Innenstadt-Großlage entfällt.
  - **B: Routing-Wechsel auf self-hosted Valhalla** — erfüllt (a) strukturell (kein Traffic-Feed, Disponenten-Sperrliste als alleinige Quelle der Wahrheit) und (b) empirisch; Routing-API-Budget entfällt; TomTom-Vertrag, ToS Clause 11.4 und Preisänderungs-Risiko 2026-07-01 entfallen. Kosten: ETA ohne Live-Verkehrslage; Betrieb Container + monatliche OSM-Updates.
  - **C: Hybrid (TomTom-ETA + Valhalla für Overrides)** — maximale Fähigkeit, maximale Komplexität: Engine-Wahl-Heuristik, doppelte Sperren-Übersetzung, doppelte Test-/Fallback-/Audit-Last, alle B-Betriebskosten **plus** alle TomTom-Lasten; verhält sich bei aktiven Overrides ohnehin wie B.
- **Entscheidung:** **Option B** — Patrick-Freigabe 2026-06-10. Begründung: (b) ist hart und mit TomTom unerfüllbar; Live-Traffic-Verlust wiegt im Einsatz-Kontext wenig (Disponent kennt die Absperrlage früher und verlässlicher als der Provider-Feed); Budget-, Lizenz- und Souveränitäts-Effekte zahlen in bestehende Constraints ein (ADR-016, Vision Self-Hosting, ADR-014). C bleibt dank ADR-014-Adapter **additiv nachrüstbar**, falls der Phase-7-Lasttest ETA-Qualität ohne Verkehrslage als operatives Problem ausweist.
- **Konsequenzen:**
  - **Stack (`project-context.md` §3):** Valhalla 3.7.x (MIT) als self-hosted Routing-Engine, Container `ghcr.io/valhalla/valhalla-scripted` (`Verifiziert: 2026-06-10` — Version 3.7.0 empirisch im Spike-G-Lauf aus `/status`; Digest-Pin + Bild-Strategie-Detail im 6.1-Detail-Plan). Daten: OSM-Extracts via Geofabrik (ODbL). **TomTom entfällt vollständig** (einzige Rolle war Routing): Services-Tabelle §5, Budget-/Throttle-Constraints §6, Migrations-Hinweise §5 werden bereinigt; Recherche-Befunde §11 bleiben als Historie mit Obsolet-Vermerk.
  - **Override-Technik je Sperrungsart:** (a) entfällt strukturell — Live-Closures existieren im Graph nicht; real existierende Sperrungen pflegt der Disponent als `exclude_polygons`/`exclude_locations`. (b) `ignore_access`/`ignore_oneways` via 3-Call-Komposition (Leg-Scoping, empirisch verifiziert).
  - **Adapter-Disziplinen (`backend/geo`, Phase 6.1):** Location-`radius`/`search_filter` bei `ignore_*`-Requests (Snapping-442-Schutz); Disponenten-Klick → `/locate`-Kanten-Matching **vor** Sperren-Anlage (wirkungslose-Sperre-Schutz); Komposition kapselt der Adapter, nicht der Aufrufer.
  - **Datenmodell `route_override`** (Phase-6-Migration): `id`, `operation_id` (FK CASCADE, einsatzgebunden), `kind` (`block` | `allow`), `geometry` (JSONB, WGS84), `matched_refs` (JSONB, provider-neutral), `created_by_dispatcher_id`, `created_at`. Audit-Pflicht (Regel-012): Action-Types `route_override_created`/`route_override_removed`.
  - **Budget:** Routing-Re-Routes sind budget-frei; `geo_usage_daily` reduziert sich auf MapTiler-Pfade (`maptiler_geocoding_calls`, `maptiler_tile_proxy_hits`); die ~50-€/Monat-Annahme (§6) wird entlastet, Phase-7-Validierung (7.1) bleibt für MapTiler bestehen. Das 30-s-Fahrzeug-Throttle bleibt als **Last-Schutz** (nicht mehr Budget-Schutz).
  - **Lizenz (Regel-016-Prüfung, dokumentiert):**
    1. **Valhalla: MIT** ✓ (Erlaubt-Liste §6).
    2. **OSM-Daten: ODbL 1.0** — Attribution „© OpenStreetMap contributors" ist durch die ohnehin pflichtige MapTiler-Karten-Attribution („© MapTiler © OpenStreetMap contributors") abgedeckt und gilt ausdrücklich auch für Routing-Ergebnisse.
    3. **ODbL-Share-alike:** Pipeline enthält keine eigene Datenveränderung (unveränderter Geofabrik-Extract + Standard-Valhalla-Build); Compliance durch Dokumentation von Quelle (Extract-Datum) und Build-Weg.
    4. **Invariante (Collective Database):** `route_override`- und Einsatzdaten bleiben eigenständige Daten **neben** dem Routing-Graphen und werden nie in den Tile-Build eingearbeitet — sonst würden Einsatzdaten ODbL-share-alike-pflichtig.
    5. **Container-Scoping:** Container-Grenze = Lizenz-Grenze (→ **Regel-020**); Container-interne C++-Deps (z. B. libspatialite, libzmq — Lizenzstand Trainingsstand-Vermutung, **ungeprüft**) sind bei 6.1 zu verifizieren, erzeugen aber nach Regel-020 keine Pflichten für EB-Digital-Code.
  - **ADR-014/Regel-017-Konformität:** reiner Adapter-Tausch; `infra/tile-proxy` verliert den Routing-Pfad (`/routing/tomtom/*` entfällt — Valhalla ist Compose-intern, kein API-Key-Inject nötig), bleibt provider-neutral für Tiles/Geocoding. Rückweg zu TomTom oder Hybrid C bleibt per Adapter offen.
  - **Folge-Aufgaben (Phase 6.1, im Detail-Plan zu konkretisieren):** Geofabrik-Update-Pipeline (monatliche Extract-Erneuerung + Tile-Rebuild als Procrastinate- oder Cron-Job — eigener Folge-ADR im 6.1-Detail-Plan), RAM-/Storage-Dimensionierung für den Ziel-Extract (Bremen ~500 MB RAM; DE gesamt deutlich mehr — Extract-Zuschnitt nach Einsatzgebieten klären), Compose-Integration mit Digest-Pin, Container-Sub-Dep-Lizenz-Verifikation.
  - **Reaktiv-Quote:** `[ERKENNTNIS]` (planmäßiges Spike-Ergebnis, keine Reaktion auf Implementierungsbug). Fenster wandert auf ADR-012 bis ADR-021; ADR-015 bleibt einziger `[REAKTIV]`-Eintrag → 1 / 10 = 10 %.
- **Abgeleitete Regel:** Regel-020 (Container-Grenze = Lizenz-Grenze) — siehe Teil C.

---

#### ADR-022: Spike H — Backup-Strategie C, Recovery-Reihenfolge und RTO/RPO-Annahmen

- **Datum:** 2026-06-11
- **Status:** Aktiv
- **Tags:** `[ERKENNTNIS]` `[MODUL]` `[DEPLOYMENT]`
- **Phasentyp-Kontext:** ERKUNDUNG (Phase 5, Schritt 5.2 / Spike H)
- **Reifegrad-Wirkung:** `[OFFEN]`-Bereich „Backup-Granularität, Recovery-Reihenfolge, RTO/RPO-Annahme" in `backend/resilience` → `[VORLÄUFIG]`. RTO/RPO-Werte in `architecture.md` §6 als `[VORLÄUFIG]` mit Messwert eingetragen; Beförderung auf `[BELASTBAR]` durch den 6.4-Backup-Recovery-Test auf VPS-Hardware.
- **Kategorie:** Betrieb und Deployment (Backup-/Recovery-Verfahren; kein neuer Code, keine neue Abhängigkeit).
- **Kontext:** Vision verlangt „nahtlose Fortsetzung nach Crash" (State-Erhaltung). Spike-H-Empirie 2026-06-11 ([`docs/spikes/spike-h-results.md`](spikes/spike-h-results.md), 90-MB-Seed mit 100k Orders): Backup/Restore in Sekunden auf beiden Pfaden (pg_dump 2,1 s/18 MB; pg_basebackup 1,5 s/29 MB; Restore 0,5 s logisch / 4,6 s physisch); `kill -9` mitten im 20k-Status-Wechsel → Recovery 0,7 s mit vollständigem Rollback der offenen Transaktion bei Erhalt aller Commits; Procrastinate-Job-State überlebt Worker-Ausfälle (`todo`-Persistenz; verwaiste `doing`-Jobs via Heartbeat-Mechanik `get_stalled_jobs`/`retry_job`/`prune_stalled_workers` verifiziert); Full-Stack-Neustart-RTO 15,1 s mit anschließend vollem dev-smoke-E2E grün (inkl. WS-Realtime).
- **Optionen:**
  - **A: Nur nächtlicher `pg_dump`** — einfachster Betrieb, aber RPO bis 24 h; kollidiert im Disaster-Fall mit der Vision für laufende Großlagen.
  - **B: `pg_basebackup` täglich + kontinuierliches WAL-Archiving** (`archive_timeout` 60 s) auf Off-VPS-Ziel — RPO ≤ 1 min (PITR), nur PostgreSQL-Bordmittel.
  - **C: Hybrid — B als Primärpfad + täglicher `pg_dump` zusätzlich** als portables logisches Artefakt (Einzeltabellen-Restore, Migrations-Tests, Mandanten-Forensik); Mehrkosten bei gemessenen Volumina ~2 s/Tag.
- **Entscheidung:** **Option C** — Patrick-Freigabe 2026-06-11. Externes Backup-Tooling (pgBackRest, wal-g) bewusst nicht in Phase 1 (Over-Engineering bei den gemessenen Größen; Re-Evaluation, wenn die DB einige GB überschreitet).
- **Konsequenzen:**
  - **Eckwerte:** `pg_basebackup` täglich; WAL-Archiving kontinuierlich (`archive_timeout` 60 s); `pg_dump -Fc` täglich; **Aufbewahrung 14 Tage** — bewusst unter der 30-Tage-Anonymisierungs-Karenz (Regel: Backup-Aufbewahrung < Anonymisierungs-Karenz, sonst überleben anonymisierte Detail-Daten im Backup und unterlaufen ADR-006/`backend/retention`).
  - **Backup-Ziel außerhalb des VPS** (naheliegend: Hetzner Storage Box per SSH/rsync) — Deployment-Detail im 6.4-Detail-Plan, keine Code-Dependency.
  - **Recovery-Reihenfolge (verbindlich, empirisch begründet):** 1. PostgreSQL (Single Source of Truth **inklusive Procrastinate-Job-State** — ADR-002-Designziel empirisch bestätigt) → 2. Valkey (**kein Restore**: Cache + Pub/Sub; leere Rate-Limit-Counter sicherheitsunkritisch) → 3. Backend + Worker (**Stalled-Job-Start-Routine**: `get_stalled_jobs` → `retry_job`, `prune_stalled_workers` — neuer 6.4-Scope-Punkt) → 4. Valhalla-Container (kein Backup; Routing-Graph deterministisch rebuildbar aus Geofabrik-Extract, ADR-021) → 5. Frontends (statisch, kein State).
  - **RTO/RPO-Annahmen** (`architecture.md` §6, `[VORLÄUFIG]` mit Messwert): Prozess-/Container-Crash RTO < 30 s (gemessen 0,7 s DB / 15,1 s Full-Stack), RPO 0 (WAL); Disaster mit Off-Site-Restore RTO im Minuten-Bereich (Restore selbst 4,6 s bei 90 MB, Host-Provisioning dominiert), RPO ≤ 1 min (WAL-Archiving). Validierung auf VPS-Hardware im 6.4-Backup-Recovery-Test (Stabilisierungs-Anker).
  - **Idempotenz-Pflicht produktiver Jobs** (Retention, Export, Aggregat) ist hart: Retry-Semantik ist at-least-once (bestätigt bestehende NFR in `architecture.md` Modul `backend/retention`).
  - **Akzeptierte Lücke:** Crash zwischen DB-Commit und Valkey-`PUBLISH` verliert genau ein WS-Event; Clients heilen per REST-Refetch beim Reconnect (4.4/4.5-Design, empirisch konsistent).
  - **6.4-Scope ergänzt um:** WAL-Archiving-Konfiguration, Off-Site-Ziel, Stalled-Job-Start-Routine, Restore-Runbook (`docs/runbooks/restore.md`) mit obiger Reihenfolge, Backup-Recovery-Test auf VPS.
  - **Reaktiv-Quote:** `[ERKENNTNIS]` (planmäßiges Spike-Ergebnis). Fenster wandert auf ADR-013 bis ADR-022; ADR-015 bleibt einziger `[REAKTIV]`-Eintrag → 1 / 10 = 10 %.
- **Abgeleitete Regel:** keine neue Teil-C-Regel — die Kopplung „Backup-Aufbewahrung < Anonymisierungs-Karenz" ist als Konsequenz-Eckwert dokumentiert; sollte sie ein zweites Mal entscheidungsrelevant werden, wird sie zur Regel befördert.

---

#### ADR-023: Spike K — Hilfe-Knopf-Semantik (Kategorien, Quittungspfad, Re-Notification, `help_alert`-Datenmodell)

- **Datum:** 2026-06-11
- **Status:** Aktiv
- **Tags:** `[ERKENNTNIS]` `[MODUL]` `[DATENMODELL]`
- **Phasentyp-Kontext:** ERKUNDUNG (Phase 5, Schritt 5.3 / Spike K)
- **Reifegrad-Wirkung:** `[OFFEN]`-Bereich „Hilfe-Knopf-Semantik" in `backend/operations` → `[VORLÄUFIG]`; reservierter `help_alert`-Payload-Anteil in `backend/realtime`/S3 → `[VORLÄUFIG]` (Payload-Schema spezifiziert — schließt die offene 4.4-Frage); Hilfe-Knopf-UI-Anteil in `frontend-betreuer` konzeptionell fixiert. Beförderung auf `[BELASTBAR]` mit Phase-6-Implementierung (6.3 + Backend-Anteil).
- **Kategorie:** Datenmodelländerung + API-Vertrag (CLAUDE.md §4 Kategorien 4/5).
- **Kontext:** Vision verlangt einen Hilfe-Knopf in der Betreuer-PWA für Eigennot/Pannen, einseitig zum Disponenten, ausdrücklich **kein Notruf-Kanal** und keine Hilfe-Funktion für Einsatzkräfte. Offen waren Pflichtfeld-Beschreibung, automatische Priorisierung und Eskalations-Routing. Vollständiges Konzept in [`docs/spikes/spike-k-results.md`](spikes/spike-k-results.md).
- **Optionen:** A — Konzept wie vorgelegt; B — Konzept mit Änderungen (Pflichtfeld, anderes Re-Notification-Intervall, dritte Kategorie). **Entscheidung: Option A** — Patrick-Freigabe 2026-06-11.
- **Konsequenzen (Konzept-Eckpunkte, bindend für Phase 6):**
  - **Auslösung:** zwei Taps (Knopf → Kategorie-Wahl `eigennot`/`panne`); **kein Bestätigungs-Dialog**, stattdessen Rückzieh-Pfad (`cancelled`, nur eigene offene Meldung).
  - **Beschreibung optional** (keine Tipp-Hürde bei Eigennot), nachreichbar; UI-Hinweis „keine Namen Dritter"; **kein Freitext im WS-Push** (PII-Disziplin, Description per REST).
  - **Standort automatisch angehängt** (lat/lng + `accuracy_m`, nullable); unterliegt der 30-Tage-Anonymisierung (`description` + `location_*` werden vom 6.5-Job genullt; Aggregat-Zähler `anzahl_hilfe_meldungen` existiert bereits — keine ADR-006-Änderung).
  - **Quittungspfad:** `open` → `acknowledged` (WS-Quittung „übernommen von <Username>") → `resolved`; Acknowledge/Resolve erzeugen Audit-Log-Einträge (neue Action-Types `help_alert_acknowledged`/`help_alert_resolved`); alle Disponenten gleichberechtigt (ADR-008), Transparenz statt Lock.
  - **Keine automatische Eskalation** (kein Eskalations-Ziel vorhanden); stattdessen client-seitige **Re-Notification** nach 2 min un-acknowledged (Intervall = UI-Detail Phase 6). **Keine Priorisierungs-Heuristik** (Eigennot vor Panne, dann FIFO).
  - **Kein-Notruf-UX-Pflicht:** statischer Hinweis „Bei akuter Gefahr: 110/112" im Hilfe-Dialog.
  - **Datenmodell `help_alert`** (Phase-6-Migration) und **API-Tripel + WS-Payload** gemäß Spike-Protokoll Abschnitte 4/5; **Persistenz vor Transport** (erst PostgreSQL, dann `RealtimePublisher` auf `operation.{id}.help_alert`; Reconnect lädt offene Alerts per REST — Muster identisch `order_status`, konsistent mit ADR-022-Resilienz-Befund).
  - **Bewusste Nicht-Entscheidungen:** kein externer Benachrichtigungskanal (SMS/Push), keine Einsatzkraft-Hilfe-Funktion, kein Eskalations-Routing.
  - **Reaktiv-Quote:** `[ERKENNTNIS]` (planmäßiges Spike-Ergebnis). Fenster wandert auf ADR-014 bis ADR-023; ADR-015 bleibt einziger `[REAKTIV]`-Eintrag → 1 / 10 = 10 %.
- **Abgeleitete Regel:** keine.

---

#### ADR-024: Spike L — Tile-Caching-Strategie (CacheFirst + Operationsraum-Pre-Cache beim Schichtbeginn)

- **Datum:** 2026-06-11
- **Status:** Aktiv
- **Tags:** `[ERKENNTNIS]` `[MODUL]` `[PERFORMANCE]`
- **Phasentyp-Kontext:** ERKUNDUNG (Phase 5, Schritt 5.4 / Spike L)
- **Reifegrad-Wirkung:** `[OFFEN]`-Bereich „Tile-Caching-Strategie / Service-Worker" in `frontend-betreuer` → `[VORLÄUFIG]`. Beförderung auf `[BELASTBAR]` mit Phase-6.3-Implementierung (produktive Karten + Offline-Cache) plus Playwright-Service-Worker-Offline-Smoke.
- **Kategorie:** Performance (Frontend-Cache-Strategie; kein neuer Stack, Workbox bereits in `project-context.md` §3).
- **Kontext:** ADR-016 macht den PWA-Service-Worker zur **alleinigen** Cache-Schicht für Tile-Last-Glättung (kein serverseitiges Caching). Spike L klärt mit echten MapTiler-Headern ([`docs/spikes/spike-l-results.md`](spikes/spike-l-results.md)): Vektor-Tile-TTL `max-age=14400` (exakt 4 h, bestätigt Annahme), Vektor-Tileset **maxzoom 15** (z16+ overzoomt MapLibre clientseitig → Pre-Cache gedeckelt), Tile-Größen z14 ~120 KB / z15 ~62 KB, Pre-Cache-Budget Operationsraum **4,2 MB (Innenstadt) bis 12,1 MB (Stadtgebiets-Großlage)** — trivial gegen mobile Quota.
- **Optionen (Runtime-Strategie):** `StaleWhileRevalidate` (immer frisch, aber jeder Tile-View triggert Background-Fetch → im Funkloch nutzlos, ohne Server-Cache budget-teuer) vs. **`CacheFirst` + ExpirationPlugin** (liefert offline ohne Netz, Fetch nur bei Miss/Ablauf). **Entscheidung: CacheFirst** — Patrick-Freigabe 2026-06-11.
- **Konsequenzen (bindend für Phase 6.3):**
  - **Pre-Cache (kritischer Hebel):** beim Schichtbeginn / Operationsraum-Beitritt lädt die Betreuer-PWA die Tile-Liste des Operationsraums (z12–15, aus Operations-Bounding-Box clientseitig berechnet) plus die statischen Style-Assets (Style-JSON, Sprite, Glyph-Ranges) per `cache.addAll()` — ausgelöst durch **bewusste Nutzeraktion** („Einsatzraum offline laden") mit Fortschrittsanzeige. Ergebnis: near-100 % Hit-Rate offline (Vision-Anforderung „offline-fähig für Karten-Tiles im aktuellen Einsatzraum").
  - **Runtime-Strategie:** `CacheFirst` + ExpirationPlugin für `api.maptiler.com/tiles/v3/*`; Glyphs/Sprite/Style als separater CacheFirst-Eintrag (selten, lange TTL).
  - **Client-TTL:** `maxAgeSeconds` auf Operationsdauer-Größenordnung (~24 h) statt der Provider-4 h — ein Betreuer im Funkloch muss ein vor 5 h pre-gecachtes Tile trotzdem sehen. **ADR-016-konform:** die AGB-Restriktion betraf ausschließlich serverseitiges Multi-Client-Caching; per-End-User-Browser-/PWA-Cache ist erlaubt, eine längere clientseitige Haltedauer davon gedeckt. `maxEntries`-LRU-Cap (~4.000 Tiles > jede Großlage) als Wachstumssicherung.
  - **Kein Pre-Cache über z15:** maxzoom 15, MapLibre overzoomt — wäre wirkungslos.
  - **Quota:** unkritisch (12 MB ≪ Quota); `navigator.storage.estimate()`-Pre-Check vor dem Pre-Cache; iOS-7-Tage-PWA-Eviction durch Re-Pre-Cache beim Schichtbeginn abgefedert.
  - **Abgrenzung Einsatzkraft-PWA:** dünnerer Cache (seltener Aufruf, kein Schicht-Pre-Cache) — nur Runtime-CacheFirst, kein proaktiver Operationsraum-Pre-Cache.
  - **Tooling:** Workbox 7.4.x via `vite-plugin-pwa` (bereits im Stack).
  - **6.3-Scope ergänzt um:** Pre-Cache-UX (Nutzeraktion + Fortschritt), Tile-Listen-Berechnung aus Operations-BBox, Workbox-`runtimeCaching`-Konfiguration, Playwright-Offline-Service-Worker-Smoke.
  - **Reaktiv-Quote:** `[ERKENNTNIS]` (planmäßiges Spike-Ergebnis). Fenster wandert auf ADR-015 bis ADR-024; ADR-015 bleibt einziger `[REAKTIV]`-Eintrag → 1 / 10 = 10 %.
- **Abgeleitete Regel:** keine.

---

#### ADR-025: Spike M — Fahrzeugbezeichnungs-Schema (Mischform mit Default-Vorbelegung, pro Mandant eindeutig)

- **Datum:** 2026-06-11
- **Status:** Aktiv
- **Tags:** `[ERKENNTNIS]` `[MODUL]` `[DATENMODELL]`
- **Phasentyp-Kontext:** ERKUNDUNG (Phase 5, Schritt 5.5 / Spike M)
- **Reifegrad-Wirkung:** `[OFFEN]`-Bereich „Fahrzeugbezeichnungs-Schema" in `backend/fleet` → `[VORLÄUFIG]`. Die implementierende Constraint-Migration + Disponenten-UI-Vorbelegung sind Phase-6.2-Aufgabe (Beförderung der Naming-Constraints auf `[BELASTBAR]` mit der Implementierung).
- **Kategorie:** Datenmodelländerung (Constraints auf `vehicle.name`; kein neues Modul, keine neue Abhängigkeit).
- **Kontext:** `vehicle.name` ist seit Schritt 4.2 `String(120)` **ohne** Eindeutigkeits- oder Format-Constraint — bewusst offen gehalten bis Spike M (`docs/architecture.md` Modul `backend/fleet`, „Offene Fragen"). Der Fragenkatalog ([`docs/spikes/spike-m-fragenkatalog.md`](spikes/spike-m-fragenkatalog.md)) wurde am 2026-06-11 von Patrick (Plattform-Betreiber mit DPolG-Bezug) direkt im Chat beantwortet. Die `vehicle`-Tabelle enthält im Status Konzeption keine Produktivdaten — Constraint-Verschärfung ist additiv und risikofrei.
- **Antworten (M1–M8):**
  - **M1/M2 — Vergabe-Modell: Mischform.** System schlägt eine Default-Bezeichnung vor (Schema `EB-<Mandanten-Kürzel>-NN`, z. B. `EB-HB-01`), die der Disponent **überschreiben** kann (Freitext). Etablierte DPolG-Namen sind damit 1:1 nutzbar, Verbände ohne Konvention bekommen einen sinnvollen Default.
  - **M3 — Stabilität: dauerhaft** (Stammdaten, einsatzübergreifend) — folgt bereits aus der `vehicle`-Tabelle (4.2).
  - **M4 — Vergabe: Disponent/Plattform-Admin** bei Fahrzeug-Anlage; Änderungen über die Fleet-API (S8d) — folgt aus der bestehenden Rollen-Matrix (4.2).
  - **M5 — Eindeutigkeit: pro Mandant.** Bezeichnungen müssen je Mandant eindeutig sein; bei späterem Verbund stellt das System ein Mandanten-Kürzel voran (Phase-X-Konsequenz, kein Phase-1-Aufwand).
  - **M6 — Länge: max 20 Zeichen.**
  - **M7 — BOS-Abgrenzung: UI-Hinweis, keine harte Sperre.** Beim Anlegen ein dezenter Hinweis („keine echten Funkrufnamen verwenden"); keine technische Erkennung (Scheingenauigkeit). Der `EB-`-Präfix der Default-Vorbelegung grenzt ohnehin ab.
  - **M8 — Zeichensatz: Umlaute erlaubt** (ä ö ü Ä Ö Ü ß plus A–Z, 0–9, Bindestrich, Leerzeichen).
- **Datenmodell-Konsequenzen (Phase-6.2-Migration auf `vehicle`):**
  - **Länge:** `vehicle.name` `String(120)` → `String(20)` (M6).
  - **Zeichensatz-CHECK:** `ck_vehicle_name_charset` — Regex `^[A-Za-zÄÖÜäöüß0-9 -]+$` (M8), plus Nicht-Leer/Nicht-nur-Whitespace (`length(btrim(name)) >= 1`).
  - **Eindeutigkeit:** Partial-UNIQUE-Index `uq_vehicle_tenant_name_active` auf `(tenant_id, name)` `WHERE is_active = TRUE` (M5) — verwendet dasselbe Soft-Delete-Prädikat wie der bestehende `ix_vehicle_tenant_id_active`; deaktivierte Fahrzeuge belegen den Namen nicht.
  - **Default-Vorbelegung (UI, kein DB-Constraint):** `frontend-disponent` schlägt `EB-<Mandanten-Kürzel>-<laufende NN>` vor (Kürzel aus Tenant-Stammdaten), überschreibbar (M1/M2).
  - **UI-Hinweise:** „keine Personennamen" (PII-Leitplanke, Vision-Constraint) + „keine echten Funkrufnamen" (M7) am Eingabefeld; keine technische Durchsetzung.
- **Bewusste Nicht-Entscheidungen:** keine technische Personennamen-/BOS-Erkennung; keine globale Eindeutigkeit in Phase 1; keine Pro-Einsatz-Namen.
- **Reaktiv-Quote:** `[ERKENNTNIS]` (planmäßiges Spike-Ergebnis). Fenster wandert auf ADR-016 bis ADR-025; ADR-015 bleibt einziger `[REAKTIV]`-Eintrag → 1 / 10 = 10 %.
- **Abgeleitete Regel:** keine.

---

## Teil C: Entscheidungsregeln

<!-- Regeln für wiederkehrende Fälle, damit die KI in ähnlichen Situationen
     konsistent und ohne Rückfrage handeln kann.
     Jede Regel verweist auf den ADR, aus dem sie entstanden ist. -->

### Format

```
### Regel-NNN: [Kurztitel]

- **Herkunft:** ADR-[Nr.]
- **Gilt für:** [wann ist diese Regel anzuwenden]
- **Regel:** [was ist zu tun]
- **Ausnahmen:** [wann gilt die Regel nicht; leer lassen, wenn keine]
- **Gegenbeispiel:** [was wäre falsch]
```

### Regeln

#### Regel-001: Versionsdisziplin Stack-Komponenten

- **Herkunft:** ADR-002
- **Gilt für:** jede Änderung an in `project-context.md` Abschnitt 3 gelisteten Versionen.
- **Regel:** Patch- und Minor-Updates sind freigabefrei und werden ohne ADR übernommen, sofern Verifikations-Stempel `Verifiziert: YYYY-MM-DD` aktualisiert wird. **Major-Updates** erfordern erneute Verifikation auf der offiziellen Quelle plus einen ADR mit Begründung und Auswirkungen.
- **Ausnahmen:** Sicherheits-Patches dürfen ohne ADR sofort übernommen werden, müssen aber im Logbuch als `[BEOBACHTUNG]` plus `[ADR-ANGELEGT]` (Folge-ADR mit `[OPERATIV] [STACK]`) nachgezogen werden.
- **Gegenbeispiel:** PostgreSQL silent von 17.9 auf 18 ohne ADR – verboten.

#### Regel-002: Stack-Ausschlüsse beachten

- **Herkunft:** ADR-002
- **Gilt für:** jede Bibliotheks-, Tool- oder Service-Wahl.
- **Regel:** Vor Aufnahme einer neuen Abhängigkeit zuerst `project-context.md` Abschnitt 3 „Explizit nicht erlaubt" prüfen. Treffer dort = sofortiger Verzicht, keine Diskussion. Auch indirekte Treffer (eine Bibliothek, die intern auf Redis basiert, ist faktisch ein Redis-Treffer).
- **Ausnahmen:** Ausnahmen sind freigabepflichtig und werden mit eigenem ADR (`[STRATEGISCH] [STACK]`) dokumentiert.
- **Gegenbeispiel:** Auswahl einer Bibliothek mit GPL-Lizenz für ein Backend-Modul, weil sie funktional besser passt – verboten ohne expliziten ADR.

#### Regel-003: Modulgrenzen-Pflicht

- **Herkunft:** ADR-003
- **Gilt für:** jeden Funktions-/Methodenaufruf zwischen Backend-Modulen.
- **Regel:** Aufrufe von Modul A nach Modul B nur über die in `architecture.md` Abschnitt 4 spezifizierten öffentlichen Schnittstellen. Direktzugriff auf interne Strukturen anderer Module (Funktionen, Klassen, ORM-Modelle) ist Architekturbruch.
- **Ausnahmen:** keine. Eine Schnittstellen-Erweiterung ist freigabepflichtig (CLAUDE.md Abschnitt 4 Punkt 5).
- **Gegenbeispiel:** `from backend.fleet.models import Vehicle` aus `backend/operations` – verboten. Stattdessen Schnittstelle S4 nutzen.

#### Regel-004: Frontend ↔ Externer Service nur über Backend

- **Herkunft:** ADR-003
- **Gilt für:** alle drei Frontends.
- **Regel:** Frontends rufen niemals direkt MapTiler, TomTom oder andere externe HTTP-APIs auf. Alle externen Calls gehen über das Backend, das sie über `infra/tile-proxy` sendet. API-Keys leben Backend-seitig.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Direkter `fetch('https://api.maptiler.com/...')`-Call aus dem Svelte-Code – verboten.

#### Regel-005: Sensible Bootstrap-Operationen über CLI

- **Herkunft:** ADR-004
- **Gilt für:** jede Operation, die ohne bestehende Web-Auth-Identität ausgeführt werden muss.
- **Regel:** Bootstrap-Operationen werden als CLI-Subcommand in `python -m eb_digital …` realisiert, mit interaktiver Passwort-Eingabe via `getpass` und ohne Klartext-Argument. Kein Web-Endpunkt für Bootstrap-Aktionen in Phase 1.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** `POST /api/admin/bootstrap` – verboten. ENV-basiertes Bootstrap-Passwort – verboten.

#### Regel-006: AccessCode-Hashing-Pflicht

- **Herkunft:** ADR-005
- **Gilt für:** jede Speicherung und jeden Vergleich eines AccessCodes.
- **Regel:** AccessCodes werden gehashed (mit Salt) gespeichert. Vergleiche per Konstantzeit-Vergleich. Klartext-Codes erscheinen weder in der Datenbank noch in Logs noch in Fehlermeldungen.
- **Ausnahmen:** Disponenten-UI darf den Klartext-Code anzeigen, weil der Disponent ihn aktiv erzeugt und verteilt – aber nur im UI-Antwort-Flow direkt nach Erzeugung, nicht aus der Datenbank rekonstruiert.
- **Gegenbeispiel:** `WHERE access_code = $1` mit Klartext – verboten. `logger.info(f"AccessCode für Operation {id} ist {code}")` – verboten.

#### Regel-007: AccessCode-Toggle wirkt nur auf neue Sessions

- **Herkunft:** ADR-005
- **Gilt für:** Aktivierung oder Deaktivierung eines AccessCodes für eine laufende Operation.
- **Regel:** Bestehende anonyme Sessions, die vor der Toggle-Aktion gestartet sind, behalten ihren Bestell-Pfad bis zum Session-Ablauf. Nur **neu** startende Sessions ab dem Zeitpunkt der Toggle-Aktion müssen den (de)aktivierten Code-Status erfüllen.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Aktivierung des Codes mitten in laufender Operation invalidiert sofort alle bestehenden Einsatzkraft-Sessions – verboten (UX-Bruch im Einsatz).

#### Regel-008: Aggregat-Schreibung sofort beim Operation-Ende

- **Herkunft:** ADR-006
- **Gilt für:** Operation-Ende-Workflow.
- **Regel:** Beim Operation-Ende wird der `operation_aggregate`-Eintrag **synchron** geschrieben, bevor der Operation-Ende-Workflow als abgeschlossen gilt. Die 30-Tage-Anonymisierung läuft entkoppelt als separater Procrastinate-Job und greift nur auf Detail-Daten zu, nicht auf das bereits geschriebene Aggregat.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Aggregat-Schreibung als Procrastinate-Job, der parallel zur Anonymisierung läuft – verboten (Race-Bedingung).

#### Regel-009: Kein Personen-Bucket im Aggregat

- **Herkunft:** ADR-006
- **Gilt für:** jede Erweiterung von `operation_aggregate`.
- **Regel:** Keine Felder, die einzelne Personen identifizieren oder pseudonymisieren – auch nicht über Hashes, Counter pro Person oder ähnliche Konstrukte. Aggregat enthält nur summarische Werte ohne Personen-Bezug.
- **Ausnahmen:** keine. Eine Aufweichung wäre freigabepflichtig (CLAUDE.md Abschnitt 4 Punkt 6) und müsste ein neues ADR mit DSGVO-Re-Identifikations-Analyse vorlegen.
- **Gegenbeispiel:** Hinzufügen eines Felds `dispatcher_activity_hash_counts` (Map Pseudonym→Anzahl Aktionen) – verboten.

#### Regel-010: Mandanten-übergreifende Datenoperationen ausschließlich asynchron

- **Herkunft:** ADR-007
- **Gilt für:** jede Operation, die mehr als triviale Mengen Mandanten-Daten anfasst (Datenexport, Bulk-Anonymisierung, große Aggregations-Migrationen).
- **Regel:** Solche Operationen werden als Procrastinate-Job gestartet. API-Endpunkte liefern nur Job-ID/Status, nie das Ergebnis im selben Request.
- **Ausnahmen:** Lese-Anfragen mit klar begrenzter Größe (Listen unter ~100 Datensätzen, paginiert) bleiben synchron.
- **Gegenbeispiel:** `GET /api/tenants/{id}/export` als Single-Request mit ZIP-Stream – verboten.

#### Regel-011: Audit-Log-Pflicht bei destruktiven oder konfigurierenden Operations-Aktionen

- **Herkunft:** ADR-008
- **Gilt für:** jede Aktion in `backend/operations`, die Operation-Zustand ändert (Operation beenden, AccessCode toggeln, Operation-Raum-Geometrie ändern, Versorgungs-Transporter-Modus wechseln, Strecke freigeben, Bündelung auslösen, Stornierung ausführen).
- **Regel:** Vor oder im selben DB-Transaktions-Schritt wird ein `operation_audit_log`-Eintrag mit `actor_dispatcher_id`, `action_type`, `at`, `target_kind`, `target_id`, `payload` (ohne PII) geschrieben.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Operation beenden ohne Audit-Log-Eintrag – verboten. Audit-Log-Eintrag erst nach erfolgreichem Commit der Aktion (außerhalb der Transaktion) – verboten (Atomicity-Bruch).

#### Regel-012: Confirmation-Dialog vor destruktiven Aktionen im Disponenten-Frontend

- **Herkunft:** ADR-008
- **Gilt für:** alle in Regel-011 gelisteten Aktionen, soweit sie aus dem `frontend-disponent` initiiert werden.
- **Regel:** Vor Auslösung der Aktion zeigt das Frontend einen modalen Bestätigungs-Dialog mit klarer Bezeichnung der Aktion und ihrer Wirkung („Operation 'X' beenden – nicht rückgängig machbar."). Bestätigung erst nach explizitem Klick.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Single-Click-Button für „Operation beenden" ohne Modal – verboten.

#### Regel-013: Operation↔Mandant ausschließlich über `operation_tenant_participation`

- **Herkunft:** ADR-009
- **Gilt für:** jede Datenmodell-Erweiterung oder -Abfrage, die Operation und Mandant in Beziehung setzt.
- **Regel:** Kein direkter `operation.tenant_id`-Foreign-Key. Verknüpfung ausschließlich über `operation_tenant_participation(operation_id, tenant_id, role)`. In Phase 1 genau ein Eintrag pro Operation mit `role='owner'`.
- **Ausnahmen:** keine. Eine Direkt-FK-Variante wäre eine Aufhebung der Verbund-Tauglichkeit und freigabepflichtig.
- **Gegenbeispiel:** `ALTER TABLE operation ADD COLUMN tenant_id …` – verboten.

#### Regel-014: Berechtigungs-Filter als Teilnahme-Filter formulieren

- **Herkunft:** ADR-009
- **Gilt für:** alle Backend-Abfragen, die Mandanten-Sichtbarkeit auf Operations und davon abhängige Entitäten (Orders, Vehicles im Operations-Kontext, Audit-Log-Einträge) prüfen.
- **Regel:** Filter werden als „Operations, an denen Mandant X teilnimmt" formuliert (`JOIN operation_tenant_participation … WHERE tenant_id = …`), **nicht** als „Operations, deren `tenant_id` X ist". In Phase 1 verhaltensgleich, in späterer Verbund-Phase additiv erweiterbar ohne Refactoring der Filter.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** `SELECT * FROM operation WHERE tenant_id = $1` – verboten.

#### Regel-015: GitHub-Actions im Verifikations-Regime

- **Herkunft:** ADR-010
- **Gilt für:** jede Action, die in `.github/workflows/*.yml` per `uses:` eingebunden ist.
- **Regel:** Alle GitHub-Actions stehen unter demselben Verifikations-Regime wie die anderen Stack-Komponenten (`project-context.md` Abschnitt 3): jede Action trägt einen `Verifiziert: YYYY-MM-DD`-Stempel im Sub-Block „GitHub Actions". Pin-Form je nach Maintainer-Praxis: **Patch-Tag** (z. B. `@v8.1.0`) für Repos außerhalb der `actions/`-Org (Immutable-Tag-Trend); **Major-Tag** (z. B. `@v6`) für Actions aus der `actions/`-Org (dort pflegen die Maintainer Major-Tag-Stabilität). Patch- und Minor-Updates sind freigabefrei mit Stempel-Refresh; Major-Updates erfordern ADR mit Begründung (Regel-001 analog für Sprachen/Bibliotheken). Bei Deprecation-Warnings in CI-Annotations: Mini-ADR vor Ablauf der Frist anlegen.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Eine Action ohne `Verifiziert`-Stempel im `project-context.md`-Block aufnehmen – verboten. Major-Sprung (z. B. `actions/checkout@v6` → `@v7`) ohne ADR – verboten.

#### Regel-016: Sub-Dependency-Lizenz-Prüfung im Verifikations-Regime

- **Herkunft:** ADR-011
- **Gilt für:** jede neue **Top-Level**-Backend- oder Frontend-Komponente, die in `pyproject.toml` (oder dem entsprechenden Frontend-Manifest) als Runtime-Dependency aufgenommen wird, sowie jeder Major-Update-Schritt einer bestehenden Top-Level-Komponente.
- **Regel:** Vor Aufnahme bzw. Major-Update wird **zusätzlich zur eigenen Lizenz** auch die Lizenz aller **Pflicht**-Sub-Dependencies (`dependencies = […]` ohne `optional-dependencies` / `extras`) gegen die Liste „Erlaubte Abhängigkeitslizenzen" in `project-context.md` Abschnitt 6 geprüft. Quelle: PyPI-Metadaten der Sub-Dep (License-Expression oder Classifier) plus Upstream-`LICENSE`-Datei zur Bestätigung. Ergebnis wird im Verifikations-Block notiert. Treffer auf eine ausgeschlossene Lizenz (GPL/LGPL als Backend-Dep, RSALv2/SSPL u. a.) erzwingt **vor** dem Pinning eine Entscheidung: entweder eigener ADR (`[STACK] [METHODIK]` oder strenger) mit Begründung der Akzeptanz und konkretem Geltungsbereich der Verschmutzung, oder Verzicht auf die Top-Level-Komponente.
- **Ausnahmen:** Optionale Extras (`optional-dependencies`, `extras`), die wir nicht installieren, müssen nicht geprüft werden. Test- und Dev-Dependencies (`[dependency-groups].dev`) sind außerhalb des Backend-Lizenz-Restriktions-Geltungsbereichs (`project-context.md` Abschnitt 6 „als Backend-Dependency"); werden trotzdem im Verifikations-Block notiert, ohne ADR-Pflicht.
- **Gegenbeispiel:** Eine Bibliothek `foo` (MIT) in `pyproject.toml` aufnehmen, weil ihre Top-Level-Lizenz passt, ohne zu prüfen, dass `foo` zwingend `bar` (GPLv3) zieht – verboten. Die Verschmutzung ist real, auch wenn die direkte Top-Level-Lizenz „sauber" wirkt.

#### Regel-017: Anbieter-Austauschbarkeit für externe Services

- **Herkunft:** ADR-014
- **Gilt für:** jede externe HTTP-API-Abhängigkeit eines Backend-Moduls (heute: MapTiler Cloud für Tiles + Geocoding via `infra/tile-proxy`, TomTom für Routing via `backend/geo`); jede künftige externe Service-Integration mit erkennbarem Alternativanbieter.
- **Regel:** Externe Services werden ausschließlich über Adapter-Module angesprochen, die eine provider-neutrale Schnittstelle definieren (Methoden-Signaturen, Datentypen, Fehler-Verhalten). Provider-spezifische Aufrufe, Datenstrukturen oder Endpunkte leben **ausschließlich** im Adapter. Aufrufende Module außerhalb des Adapter-Moduls dürfen Provider-Identität nicht kennen — sie sehen nur die provider-neutrale Schnittstelle. Wechsel des Providers erfolgt als Adapter-Austausch ohne Modul-Refactor außerhalb des Adapters. Frontend-Renderer-Wahl pro Frontend folgt demselben Prinzip: **MapLibre GL JS als provider-neutraler Default**. Wechsel zu provider-spezifischem SDK (MapTiler SDK JS, Mapbox GL JS, etc.) ist möglich, erfordert aber **eigenen ADR** mit expliziter Begründung des akzeptierten Frontend-Lock-ins, Bezifferung des Cost-/UX-Vorteils und Plan zum Rück-Wechsel-Aufwand.
- **Pflichten beim Hinzufügen eines neuen externen Service:**
  1. Adapter-Modul mit provider-neutraler Schnittstelle vor erster produktiver Nutzung definiert und in `architecture.md` Abschnitt 4 als Schnittstelle dokumentiert.
  2. Mindestens ein Alternativanbieter im aufnehmenden ADR oder im `project-context.md` Abschnitt 5 dokumentiert.
  3. Wechselpfad als Adapter-Austausch beschrieben (welche Methoden-Signaturen müssen erfüllt sein, welche Datentypen sind kanonisch).
- **Ausnahmen:** keine. Eine pragmatische Provider-Lock-in-Abweichung erfordert eigenen ADR mit expliziter Begründung (z. B. Frontend-Lock-in mit MapTiler SDK JS für Sessions-Cost-Vorteil) und greift nur für die spezifisch begründete Komponente, nicht generisch.
- **Gegenbeispiel:**
  - `from backend.geo.maptiler import geocode_address` direkt aus `backend/operations` aufgerufen (Provider-Identität sickert in den Aufrufer) — verboten. Stattdessen `backend.geo.geocode(address)` als provider-neutrale Schnittstelle.
  - `import maptilersdk` im Svelte-Frontend ohne separaten ADR — verboten. Stattdessen MapLibre GL JS, oder ADR mit Lock-in-Begründung.
  - Direkter provider-spezifischer Endpunkt-Aufruf in einem Backend-Modul außerhalb von `backend/geo` (z. B. `httpx.get("https://api.maptiler.com/...")` aus `backend/realtime`) — verboten. Stattdessen Adapter-Aufruf über `backend/geo`.

#### Regel-018: FastAPI-Resource-Dependencies mit Context-Manager nutzen `yield`, nicht `return`

- **Herkunft:** ADR-015
- **Gilt für:** jede FastAPI-Dependency, die eine Ressource mit Lifecycle (Context-Manager, `with`/`async with`) erzeugt und an Endpoints durchreicht. Aktuelle Treffer: `get_db_session` (SQLAlchemy `AsyncSession`); künftige Treffer: Procrastinate-Connection-Wrapper, Valkey-Pipeline-Scopes, file-handle-haltende Helfer, externe HTTP-Client-Sessions mit dediziertem Connection-Pool, etc.
- **Regel:** Eine Dependency, die intern `with` oder `async with` öffnet, gibt die geschützte Ressource ausschließlich per `yield` weiter — niemals per `return` aus dem `with`-Block heraus. Korrektes Muster:
  ```python
  async def get_resource(...) -> AsyncIterator[Resource]:
      async with factory() as resource:
          try:
              yield resource
          except Exception:
              await resource.rollback()  # oder analoger Fehler-Cleanup
              raise
  ```
  Die Type-Annotation lautet `AsyncIterator[Resource]` (oder `Iterator[Resource]` für sync). Der Exception-Pfad führt einen expliziten Fehler-Cleanup-Aufruf aus (z. B. `rollback()` für DB-Sessions, `discard()` für Pipelines), bevor die Exception propagiert. FastAPI erkennt yield-Generatoren automatisch und führt den Code nach `yield` als Cleanup-Phase aus, auch wenn der Endpoint eine Exception wirft. Der Code vor `yield` läuft vor dem Endpoint, der yield-Wert wird injiziert, der Code nach `yield` läuft nach dem Endpoint.
- **Begründung:** `return resource` innerhalb eines `with`-Blocks löst sofort `__exit__` / `__aexit__` aus — die Ressource ist beim Endpoint-Aufruf bereits geschlossen oder im Cleanup-Modus. SQLAlchemy-`AsyncSession` ist lazy bei Connection-Acquisition, daher funktioniert der Code oberflächlich (neue Connection wird stillschweigend erworben), aber **diese Connection liegt außerhalb des `with`-Cleanup**, und Exceptions vor explizitem Commit lösen keinen Rollback aus. Symptome: Connection-Pool-Erschöpfung unter Last, ‚idle in transaction‘-Zustände, schwer reproduzierbare Fehler in Integrationstests.
- **Tests:** Jede neue Resource-Dependency braucht einen Lifecycle-Test mit Counter-Stub (Verifikation: Enter vor Yield, Exit nach Konsum, Rollback bei Exception) sowie mindestens eine Smoke-/Integration-Probe gegen die echte Ressource (z. B. dev-smoke.sh-Eintrag mit Exception-Pfad → Folge-Request darf nicht stallen).
- **Ausnahmen:** Dependencies, die keine Lifecycle-Ressource verwalten (reine Settings-Lookups, statische Header-Reader, in-memory-Object-Lookups), dürfen `return` verwenden — sie öffnen keinen `with`-Block und haben keinen Cleanup-Bedarf.
- **Gegenbeispiel:**
  ```python
  # ❌ Verboten — return aus async with löst __aexit__ vor Endpoint aus:
  async def get_db_session(request: Request) -> AsyncSession:
      async with factory() as session:
          return session  # ← Bug: Session ist beim Endpoint bereits geschlossen
  ```
  Genau diese Form war der Lifecycle-Bug aus Schritt 2.5b (ADR-015).

#### Regel-019: UMSETZUNG-Sonderregel für Modul-Beförderungs-Phasen

- **Herkunft:** ADR-019
- **Gilt für:** jede UMSETZUNG-Phase, deren Hauptzweck die Beförderung berührter Module von `[VORLÄUFIG]` auf `[BELASTBAR]` ist (Phase 1, Phase 2, Phase 4, Phase 6 sowie alle künftigen ähnlich gelagerten UMSETZUNG-Phasen, inkl. Phase X Verbund-Modus).
- **Regel:** Die zu befördernden Module gelten **am Schrittbeginn als hinreichend belastbar, um den Schritt starten zu lassen**, wenn (a) der Modul-Schnitt durch einen ADR strategisch fixiert ist (Stack/Architektur-ADRs wie ADR-002/003/009), (b) alle **konsumierten** Bestandteile außerhalb der zu befördernden Module tatsächlich `[BELASTBAR]` sind, und (c) der Detail-Plan vor Code-Eingriff jeden berührten Bestandteil benennt. Die tatsächliche Beförderung des Moduls von `[VORLÄUFIG]` auf `[BELASTBAR]` erfolgt erst mit funktional erfülltem Schritt (Definition of Done aus CLAUDE.md §9 plus Coverage-Anker plus Smoke-Probe).
- **Ausnahmen:** keine. UMSETZUNG-Phasen, die **nicht** primär Module befördern, sondern bereits belastbare Module erweitern (z. B. Phase 7 Stabilisierung — die ist allerdings STABILISIERUNG, kein UMSETZUNG, daher außerhalb des Geltungsbereichs), fallen unter die strikte Original-Eingangs-Disziplin.
- **Gegenbeispiel:** Schritt 4.1 `backend/catalog` **nicht starten**, weil das Modul heute `[VORLÄUFIG]` ist und die strikte Eingangs-Disziplin „[BELASTBAR] vor Schrittbeginn" fordert — verboten, weil das das Schritt-Format-Patterndokument durch wörtliche Lektüre über den Phasen-Zweck stellt und Phase 4 unmöglich machen würde. Korrekt: Detail-Plan vorlegen (siehe Regel oben Punkt c), Patrick-Freigabe, Schritt starten.

#### Regel-020: Container-Grenze = Lizenz-Grenze für Infrastruktur-Komponenten

- **Herkunft:** ADR-021
- **Gilt für:** die Lizenz-Bewertung von Komponenten, die als eigenständige Container/Prozesse betrieben und ausschließlich über Netzwerk-Schnittstellen (HTTP, SQL-Protokoll, Redis-Protokoll o. ä.) angesprochen werden — z. B. PostgreSQL, Valkey, nginx, Caddy, Valhalla.
- **Regel:** Gegen die Erlaubt-/Ausschluss-Listen in `project-context.md` §6 wird die **Lizenz der Komponente selbst** geprüft (plus die Lizenz der von ihr konsumierten **Daten**, falls vorhanden — z. B. OSM/ODbL). Container-intern gelinkte Sub-Dependencies erzeugen **keine** Pflichten für den EB-Digital-Code und keine ADR-Pflicht, solange (a) kein Code-Linking zwischen EB-Digital-Prozessen und der Komponente stattfindet, (b) das Image vom Upstream-Registry bezogen und nicht selbst distribuiert wird, und (c) die Kommunikation ausschließlich über Netzwerk-Schnittstellen läuft. Beginnt das Projekt, eigene Images mit der Komponente zu **distribuieren** (Registry-Push an Dritte), ist die Bewertung per ADR zu erneuern.
- **Ausnahmen:** Prozess-interne Abhängigkeiten (Python-Pakete in `pyproject.toml`, npm-Pakete in `package.json`) — dort gilt Regel-016 in voller Schärfe inklusive Sub-Dependency-Prüfung (Präzedenzfälle ADR-011 psycopg, ADR-020 GEOS).
- **Gegenbeispiel:** Eine LGPL-Python-Bibliothek mit dem Argument „läuft ja im Docker-Container" ohne ADR aufnehmen — verboten: das Deployment-Vehikel ändert nichts daran, dass die Bibliothek in den EB-Digital-Prozess gelinkt wird.
