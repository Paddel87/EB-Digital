# Project Context

<!-- Projektspezifischer Kontext. Wird zu Sessionbeginn als erste Datei gelesen.
     Dient als Entscheidungsgrundlage für alle autonomen Schritte der KI.
     Jede Angabe muss so konkret sein, dass daraus maschinell eindeutig Regeln ableitbar sind. -->

## 1. Kerndaten

- **Projektname:** EB Digital
- **Kurzbeschreibung:** Multi-Tenant-Plattform zur Echtzeit-Koordination ehrenamtlicher Einsatzbetreuung bei polizeilichen Großlagen (initial DPolG, perspektivisch weitere Berufsverbände).
- **Status:** Konzeption
- **Version (SemVer):** v0.1.0
- **Dokumentationssprache:** Deutsch
- **Codesprache (Kommentare, Variablennamen, Bezeichner):** Englisch
- **Projekttyp:** Full-Stack (Python-Backend + drei TypeScript-PWAs auf SvelteKit-Basis)

## 2. Zielgruppe und Nutzungskontext

- **Primäre Nutzer:**
  - **Disponent** – ehrenamtlich, technisch grundversiert, Browser auf Desktop/Tablet, oft im stationären Lagezentrum.
  - **Betreuer** – ehrenamtlich, im Einsatz mobil im Fahrzeug, PWA auf Smartphone/Tablet, Funklöcher müssen abgefedert werden.
  - **Einsatzkraft** – Polizeibedienstete im Außendienst, anonyme PWA-Session, oft auf schlechtem Funknetz, niederschwellig.
- **Sekundäre Nutzer / Betreiber:**
  - **Plattform-Administrator** – betreibt Server, schaltet Mandanten frei, legt Disponent-Accounts an. Initial: Patrick (Plattform-Betreiber).
  - **Mandanten-Antragsteller** – Berufsverband-Vertretung (Landesvorstand o. ä.), Self-Service-Registrierung plus Vertragsbeilage.
- **Erwartete Last:** Großlagen mit potenziell mehreren hundert parallelen Einsatzkräften, mehrere parallele Einsätze pro Mandant, einzelne Großlagen über Wochen. Konkrete Zielgrößen sind in Phase STABILISIERUNG zu validieren – Annahme bis Validierung: 50 concurrent Disponenten + 500 concurrent Einsatzkräfte pro Plattform-Instanz.
- **Nutzungsumgebung:**
  - Disponent: Browser Desktop/Tablet, stabile Verbindung.
  - Betreuer: PWA Mobile, intermittierende Verbindung, lokal gepufferte Karten und Auftragsdaten.
  - Einsatzkraft: PWA Mobile, oft schlechtes Netz, einmaliger oder seltener Aufruf pro Einsatz.

## 3. Technischer Stack

### Fixiert

Pflicht: jede Version trägt einen Vermerk `Verifiziert: YYYY-MM-DD` (Datum, an dem auf der offiziellen Quelle bestätigt wurde, dass die Version aktuell, unterstützt und nicht durch Deprecations belastet ist). Verifikation wird in Modus 2 Schritt 2a ausgelöst (siehe `CLAUDE.md` Abschnitt 1A). Major-Updates erfordern eine erneute Verifikation und einen ADR.

**Stand der Verifikation:** Recherche am 2026-05-07 durch delegierten KI-Recherche-Agenten auf offiziellen Quellen (PyPI, GitHub Releases, endoflife.date, postgresql.org, nginx.org, vite.dev), Ergebnis durch Patrick Schulz freigegeben. Verifikations-Stempel `Verifiziert: 2026-05-07` gilt entsprechend.

**Sprachen und Laufzeit**

- Python 3.13 (Patch-Linie aktuell, EOL 2029-10) — `Verifiziert: 2026-05-07`
- TypeScript 6.0.3 (Major 6 stabil seit 2024-04-16) — `Verifiziert: 2026-05-07`
- Node.js 24 LTS (Active LTS bis 2026-10, Security bis 2028-04) — `Verifiziert: 2026-05-07`

**Backend Frameworks und Bibliotheken**

- FastAPI 0.136.x — `Verifiziert: 2026-05-07`
- uvicorn 0.46.x mit `[standard]`-Extra (uvloop, httptools, websockets, watchfiles, PyYAML, python-dotenv) — `Verifiziert: 2026-05-09` (Schritt 1.3)
- SQLAlchemy 2.0.49 — `Verifiziert: 2026-05-07`
- asyncpg 0.31.x (Async PostgreSQL-Driver für SQLAlchemy 2.0; v0.31.0 released 2025-11-24, droppt nur EOL Python 3.8, PostgreSQL-17-Support seit 0.30.0) — `Verifiziert: 2026-05-09` (Schritt 1.4)
- Alembic 1.18.x — `Verifiziert: 2026-05-07`
- Pydantic 2.13.x — `Verifiziert: 2026-05-07`
- pydantic-settings 2.13.1 (NICHT 2.14 – „Stabilität vor Aktualität": 2.14.1 erst am 2026-05-08 released, Hotfix auf 2.14.0; 2.13.1 hat seit Februar Praxisreife. Migration auf 2.14.x per ADR, sobald die 2.14-Linie stabilisiert ist) — `Verifiziert: 2026-05-09` (Schritt 1.3)
- httpx 0.28.x (1.0 noch in dev) — `Verifiziert: 2026-05-07`

**Auth-Bausteine (kein Auth-Framework, eigene dünne Schicht)**

- argon2-cffi 25.1.x – Argon2id-Hashing direkt — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-09 Schritt 1.6: Python 3.13/3.14 als Trove-Classifier offiziell aufgeführt, MIT, kein neuer Hotfix seit 2025-06-03)
- itsdangerous 2.2.x – signierte Tokens für Reset-Flows und Einsatz-URLs — `Verifiziert: 2026-05-09` (Schritt 1.6); BSD-3-Clause; einzige stabile 2.x-Linie seit 2024-04-16, langsame Pallets-Cadence, kein 2.3 in Sicht
- Starlette `SessionMiddleware` – Cookie-basierte Sessions (Bestandteil von FastAPI-Stack)
- redis 7.4.x – async Valkey-Client für Rate-Limit-Counter (ADR-013) und ab Phase 4 WebSocket-Pub/Sub. Wire-protokoll-kompatibel mit Valkey 8.1.7. — `Verifiziert: 2026-05-10` (Schritt 2.2); MIT; reguläre Cadence (7.2.1, 7.3.0, 7.4.0 vom 2026-03-24); gewählt gegenüber `valkey-py 6.1.1` (9 Monate Stable-Cadence-Pause, Beta-Linie 6.2.0rc), weil operative Reife schlägt Marken-Konsistenz im Client (siehe Sub-Entscheidung Schritt 2.2). Lizenzproblem ADR-002 betrifft den Server, nicht den MIT-lizenzierten Client.

Begründung: FastAPI-Users im Maintenance-Mode (kein Feature-Wachstum), passlib seit 2020-10 ohne Release. Eigener Auth-Code basiert auf etablierten Bausteinen, keine eigene Krypto-Implementierung. Begleitende Pflichten: Auth-Modul-Coverage ≥ 95 %, externe Security-Review vor Produktivstart, ADR mit Threat-Model.

**Background-Jobs**

- procrastinate 3.8.1 (PostgreSQL-basiert, async-native, ACID-Job-State; PsycopgConnector als Default — psycopg3-Pool transitiv neben unserem asyncpg-Pool, by-design getrennte Connection-Pools für Job-Engine und ORM) — `Verifiziert: 2026-05-09` (Schritt 1.5)
- psycopg 3.3.4 (`psycopg[binary,pool]`-Extra) — Pflicht-Sub-Dependency von procrastinate. Lizenz LGPL-3.0-only — explizit per ADR-011 als einzige LGPL-Ausnahme zur Lizenz-Restriktion in Abschnitt 6 akzeptiert; Geltungsbereich auf den Persistenz-/Job-Engine-Pfad beschränkt. `binary`-Extra gewählt, weil macOS-Entwicklung ohne System-libpq und Docker-Container ohne `apt-get install libpq5`-Schritt beide nur mit dem Binary-Wheel reproduzierbar laufen; `pool`-Extra ist von procrastinate gefordert. — `Verifiziert: 2026-05-09` (Schritt 1.5, Lizenz-Quelle: PyPI License-Expression + Upstream-`LICENSE.txt`)

Begründung: PostgreSQL als Backing nutzt vorhandene Infrastruktur und macht Job-State Teil der DB-Backups – passt direkt zur Vision-Anforderung „nahtlose Fortsetzung nach Crash". Gewählt anstelle von Taskiq (Velocity-Risiko) und SAQ (zusätzlicher Druck auf Valkey-Persistenz-Konfiguration). Connector-Wahl: `PsycopgConnector` (Procrastinate-Default-Pfad in der Doku, ACID-Garantien klar dokumentiert) statt `SQLAlchemyConnector` (Sekundärpfad mit weniger Praxisbeispielen).

**Datenbank, Cache, Realtime**

- PostgreSQL 17.9 (NICHT 18 – „Stabilität vor Aktualität", 7 Monate Praxisreife mehr; EOL 2029-11) — `Verifiziert: 2026-05-07`
- Valkey 8.1.7 (NICHT 9 – Linux-Foundation-Fork, gewählt wegen Lizenzwechsel von Redis zu RSALv2/SSPL; Rolle reduziert auf Cache und WebSocket-Pub/Sub, Jobs gehen in PostgreSQL) — `Verifiziert: 2026-05-07`

**Frontend Frameworks und Bibliotheken**

- Svelte 5.55.x (Svelte 5 ist stabile Default-Linie) — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-10 Schritt 1.7)
- SvelteKit 2.59.x — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-10 Schritt 1.7)
- @sveltejs/adapter-static 3.0.x — `Verifiziert: 2026-05-10` (Schritt 1.7); MIT; gewählt statt `@sveltejs/adapter-auto`/`adapter-node`, weil Frontends als statische Bundles hinter Caddy serviert werden (architecture.md Abschnitt 2)
- @sveltejs/vite-plugin-svelte 7.1.x — `Verifiziert: 2026-05-10` (Schritt 1.7); MIT; transitiv über `@sveltejs/kit`, expliziter Pin macht Major-Updates ADR-pflichtig
- TypeScript 6.0.3 (Re-Bestätigung 2026-05-10 Schritt 1.7) — siehe Sprachen-Block oben
- Vite 8.0.x (Rolldown-basiert, stable seit 2026-03-12) — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-10 Schritt 1.7)
- vite-plugin-pwa 1.3.x (peer-dep auf Vite 8) — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-10 Schritt 1.7)
- MapLibre GL JS 5.24.x (BSD-3) — `Verifiziert: 2026-05-07` (Aktivierung in Phase 6 nach Spike L)
- Workbox 7.4.x — `Verifiziert: 2026-05-07` (transitiv via vite-plugin-pwa in Phase 1; expliziter Import in Phase 6)

**Infrastruktur**

- nginx 1.30.0 stable (Hinweis zur Konvention: gerade Minor = stable, ungerade = mainline; GA des stable 1.30-Branches am 2026-04-15, kein 1.30.1 in Sicht) — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-10 Schritt 1.8); im Compose als `nginx:1.30.0-alpine` gepinnt (Manifest-List-Digest in `docker-compose.yml`)
- Caddy 2.11.2 (released 2026-04-17, Bug-Fix-Release auf 2.11-Linie) — `Verifiziert: 2026-05-10` (Schritt 1.8); im Compose als `caddy:2.11.2` gepinnt (Manifest-List-Digest)
- Docker Engine 29.4.2 (released 2026-05-01, CVE-Fix-Patch innerhalb 29.4.x-Pin; Hostsystem-Erwartungswert) — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-10 Schritt 1.8: lokal `docker version` gegen die laufende Engine geprüft)
- Docker Compose v5.1.3 („Mont Blanc"; Major-Sprung über v3/v4 zur Vermeidung von Verwechslung mit alten YAML-Schemas; v5.1.3 released 2026-04-15 innerhalb 5.1.x-Pin) — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-10 Schritt 1.8: lokal `docker compose version` geprüft)
- docker buildx 0.33.x — `Verifiziert: 2026-05-07`
- Valkey 8.1.7 (Re-Bestätigung 2026-05-10 Schritt 1.8) — siehe „Datenbank, Cache, Realtime"-Block oben; im Compose als `valkey/valkey:8.1.7-alpine` gepinnt (Manifest-List-Digest)

**Laufzeitumgebung**

Hetzner CCX-VPS in Deutschland; Docker Compose mit Profilen für lokal, staging, production.

**Package Manager**

- uv 0.11.x (Python) — `Verifiziert: 2026-05-07`
- pnpm 11.x (TypeScript, Workspaces für drei Frontends) — `Verifiziert: 2026-05-07`

### Empfohlen (freigabefrei nutzbar)

Bibliotheken und Tools, die ohne separate Freigabe eingesetzt werden dürfen, solange Lizenz und Wartungslage passen. Versionen sind als Pinning-Empfehlung verstanden – Patch-Updates frei, Minor-Updates ohne ADR möglich, Major-Updates ADR-pflichtig.

**Backend Test- und Qualitäts-Tooling**

- pytest 9.0.x — `Verifiziert: 2026-05-07`
- pytest-asyncio 1.3.x — `Verifiziert: 2026-05-07`
- pytest-cov 7.1.x — `Verifiziert: 2026-05-07`
- fakeredis 2.35.x – In-Process-Fake für `redis-py` in Unit-Tests — `Verifiziert: 2026-05-10` (Schritt 2.2); BSD-3-Clause; reguläre Cadence (last release 2026-04-12); Integration-Test gegen den echten Valkey-Container im Compose-Stack via `dev-smoke.sh`.
- ruff 0.15.x (Linter und Formatter, Konfiguration in `pyproject.toml`, Zeilenlänge 100) — `Verifiziert: 2026-05-07`
- mypy 1.20.2 (`--strict`; **bewusst nicht 2.0.x** – mypy 2.0.0 wurde 2026-05-06 released, „Stabilität vor Aktualität": Migration auf 2.x per ADR, sobald 2.0.x-Patches stabilisiert sind) — `Verifiziert: 2026-05-07`
- bandit 1.9.x — `Verifiziert: 2026-05-07`
- pip-audit 2.10.x (Schwellenwert `high`) — `Verifiziert: 2026-05-07`
- httpx 0.28.x – auch als Backend-HTTP-Client für externe APIs (Connection-Pool) — siehe „Fixiert"

**Backend Logging**

- strukturiertes JSON-Logging via stdlib `logging` + JSON-Formatter; zentraler Logger-Wrapper mit Redaction-Liste für PII (Pflicht aus Constraint Datenschutz).

**Frontend Test- und Qualitäts-Tooling**

- vitest 4.1.x mit Coverage — `Verifiziert: 2026-05-07` (Re-Bestätigung 2026-05-10 Schritt 1.7)
- @vitest/coverage-v8 4.1.x — `Verifiziert: 2026-05-10` (Schritt 1.7); MIT; vitest-Coverage-Reporter analog `pytest-cov`
- @types/node 24.12.x — `Verifiziert: 2026-05-10` (Schritt 1.7); MIT; Type-Stubs für Node 24 LTS, Pflicht für vite/svelte-kit-tsconfig (`types: ["node"]`)
- Playwright 1.59.x (E2E-Smoke-Tests pro Frontend, ausgeweitet in STABILISIERUNG) — `Verifiziert: 2026-05-07`
- ESLint 10.3.x — `Verifiziert: 2026-05-07`
- @typescript-eslint 8.59.x — `Verifiziert: 2026-05-07`
- eslint-plugin-svelte 3.17.x — `Verifiziert: 2026-05-07`
- eslint-plugin-security 4.0.x (Flat-Config) — `Verifiziert: 2026-05-07`
- prettier 3.8.x — `Verifiziert: 2026-05-07`
- prettier-plugin-svelte 3.5.x — `Verifiziert: 2026-05-07`
- svelte-check 4.4.x — `Verifiziert: 2026-05-07`
- `tsc --noEmit --strict --noUncheckedIndexedAccess --noImplicitReturns` (kommt mit TypeScript 6.0.3)

**Repository-Tooling**

- pre-commit 4.6.x — `Verifiziert: 2026-05-07`
- commitlint 20.5.x mit Conventional-Commits — `Verifiziert: 2026-05-07`
- actionlint 1.7.x als pre-commit-Hook (rhysd/actionlint) — `Verifiziert: 2026-05-08`

**GitHub Actions**

Pin-Form je nach Maintainer-Praxis: **Major-Tag** für Actions aus der `actions/`-Org (dort pflegen die Maintainer Major-Tag-Stabilität); **Patch-Tag** für Actions außerhalb der `actions/`-Org (Immutable-Tag-Trend, kein floating major). Major-Updates sind ADR-pflichtig (Regel-001 + Regel-015). Verifikation in derselben Disziplin wie die übrigen Stack-Komponenten.

- `actions/checkout@v6` — `Verifiziert: 2026-05-08`
- `actions/setup-python@v6` — `Verifiziert: 2026-05-08`
- `actions/setup-node@v6` — `Verifiziert: 2026-05-08`
- `actions/upload-artifact@v7` — `Verifiziert: 2026-05-10` (Major-Update v4→v7 in ADR-012 dokumentiert; Auslöser: Node-20-Deprecation-Annotation auf v4)
- `astral-sh/setup-uv@v8.1.0` — `Verifiziert: 2026-05-08` (Major-Update v5→v8 in ADR-010 dokumentiert)
- `pnpm/action-setup@v6.0.5` — `Verifiziert: 2026-05-08` (Major-Update v4→v6 in ADR-010 dokumentiert)

**Container-Build**

- docker buildx mit Multi-Stage-Build — siehe „Fixiert"

**Datums-/Zeit-Handling**

- stdlib `datetime` + `zoneinfo`. Keine pendulum/arrow ohne ADR-Begründung.

### Explizit nicht erlaubt

Was bewusst ausgeschlossen ist, mit Begründung. Verhindert, dass die KI naheliegende, aber unerwünschte Lösungen wählt.

- **Keine US-Cloud-Anbieter (AWS, GCP, Azure) als Hauptbetrieb** — Vision-Constraint EU-Hosting.
- **Kein Redis** (statt Valkey) — Lizenzwechsel zu RSALv2/SSPL, nicht mehr OSI-Open-Source.
- **Keine Mapbox GL JS** (proprietäre Lizenz seit v2) — MapLibre GL JS ist die OSS-Fork.
- **Keine GPL/LGPL-Bibliotheken als Backend-Dependency** ohne ADR — das Projekt ist AGPLv3, Abhängigkeiten sollen permissiv lizenziert sein, um Re-Use durch andere Komponenten ohne Lizenz-Abklärung zu erlauben.
- **Keine native Mobile-App-Toolchains** (React Native, Flutter, Capacitor, Expo) — Vision-Constraint nur PWA in Phase 1.
- **Keine SaaS-Auth-Provider** (Auth0, Clerk, Supabase-Auth, WorkOS) — Self-Hosting + Privacy-by-Design.
- **Kein FastAPI-Users, kein passlib** — FastAPI-Users im Maintenance-Mode (kein Feature-Wachstum), passlib seit 2020-10 ohne Release. Auth wird auf etablierten Bausteinen (argon2-cffi, itsdangerous, Starlette-Sessions) selbst geschrieben, siehe Abschnitt 3 „Fixiert".
- **Kein Taskiq, kein ARQ, kein Celery** — Taskiq mit Velocity-Risiko, ARQ-Maintenance verlangsamt, Celery Overkill. Procrastinate als alleinige Job-Engine.
- **Keine Google Maps / Google Routing / Google Geocoding** — externe Dienste sind ausschließlich MapTiler (Karten/Geocoding) und TomTom (Routing).
- **Keine ORM-Schnellschüsse** (SQLModel als Hauptweg, Tortoise-ORM, Peewee) — SQLAlchemy 2.0 als alleiniges Backend-ORM, um Multi-Tenant-Patterns konsistent zu halten.
- **Keine Behörden-IT-Anschlüsse** — Vision-Constraint, technisch durchgesetzt durch fehlende externe Schnittstellen Richtung polizeiliche/behördliche Systeme.
- **Kein Tracking** (Google Analytics, Plausible-Cloud, Matomo-Cloud) — Privacy-by-Design.

## 4. Architektur-Grobstruktur

[Details in `architecture.md`. Hier nur Grobübersicht. Reifegrade aller Bestandteile starten als `[VORLÄUFIG]`, sofern nicht durch eine harte Vision-Vorgabe `[BELASTBAR]`.]

**Module (Kurzübersicht):**

- **backend/auth** – Account-Hierarchie, Session-Handling für angemeldete Rollen.
- **backend/auth_anonymous** – einsatzspezifische URL, optionale Zugangscodes, anonyme Temporär-Sessions; bewusst getrennt vom Login-basierten `auth`-Modul.
- **backend/tenants** – Mandanten-Verwaltung, Self-Service-Onboarding, Admin-Freischaltung.
- **backend/catalog** – zentraler Basis-Artikelkatalog plus mandantenspezifische Erweiterungen.
- **backend/operations** – Einsätze, Aufträge, automatische Fahrzeugzuweisung, Stornierung, Bündelung, Versorgungs-Transporter-Modus-Steuerung.
- **backend/fleet** – Fahrzeuge, Beladung, Verbrauchsbuchung.
- **backend/geo** – Routing-Adapter (TomTom), Tile-Caching-Steuerung (MapTiler über nginx-Proxy), Geofencing (150 m), Sperrungs-Override.
- **backend/realtime** – WebSocket-Hub für Live-Standorte, Auftragsstatus, Disponent↔Betreuer-Chat, Hilfe-Knopf.
- **backend/resilience** – Backup und Wiederherstellung des persistenten Einsatzzustands aus PostgreSQL (inklusive offener Aufträge und in-flight Procrastinate-Jobs); WebSocket-Verbindungen brechen bei Server-Neustart ab, Clients reconnecten automatisch und bekommen den persistenten State neu geladen. „Nahtlos" im Sinne der Vision bezieht sich auf State-Erhaltung, nicht auf Connection-Erhaltung.
- **backend/export** – Mandanten-Datenexport (DSGVO-Recht).
- **backend/retention** – automatische 30-Tage-Anonymisierung individueller Bestell- und Standortdaten, Aggregations-Pflege.
- **frontend-disponent** (SvelteKit) – Disponenten-Web-UI für PC/Tablet.
- **frontend-betreuer** (SvelteKit, PWA) – Mobile-PWA mit Offline-Pufferung und Turn-by-Turn-Navigation.
- **frontend-einsatzkraft** (SvelteKit, PWA) – schlanke anonyme Bestell-PWA.
- **infra/tile-proxy** – nginx-Cache vor MapTiler-Tiles und TomTom-Routing.
- **infra/reverse-proxy** – Caddy mit automatischem TLS, Routing zu Backend und drei Frontend-Buckets.

**Kommunikationsmuster:** REST/JSON synchron Frontend ↔ Backend; WebSocket für Live-Updates und Chat; HTTP synchron Backend → externe Karten- und Routing-Services über den `infra/tile-proxy`-Cache.

## 5. Externe Abhängigkeiten

### Services

| Service      | Zweck                       | Authentifizierung                          | Ausfallverhalten                                                                                                                    |
| ------------ | --------------------------- | ------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **MapTiler** | Vektor-Tiles, Geocoding     | API-Key (Backend-Seite, niemals im Client) | Fallback: Tiles aus nginx-Cache; Geocoding-Ausfall → Disponent setzt Position manuell auf Karte                                     |
| **TomTom**   | Routing inkl. Verkehrsdaten | API-Key (Backend-Seite, niemals im Client) | Fallback: ohne Verkehrslage routen (Static-Routing aus letzter Antwort); bei vollständigem Ausfall → Disponent koordiniert per Chat |

### APIs

API-Verträge werden in `architecture.md` Abschnitt 4 detailliert. Hier nur Kategorien:

- **Tile-API (MapTiler):** GET-Tiles, aggressiv gecacht (≥ 7 Tage TTL für statische Tiles).
- **Geocoding-API (MapTiler):** sparsam, mit Backend-Cache von Adresse → Koordinate.
- **Routing-API (TomTom):** maximal 1 Aufruf pro Auftrag, frühestens nach 30 s erneut für dasselbe Fahrzeug. Detaillierte Budget-Disziplin siehe Abschnitt 6 (Performance).
- **Bekannte Migrations-Hinweise TomTom (Stand 2026-05-07):**
  - Section-Type `tollRoad` wurde am 2025-03-15 entfernt – stattdessen `toll` und `tollVignette` verwenden.
  - Orbis Maps v1 wurde am 2025-02-19 dekommissioniert – Adapter im `backend/geo`-Modul muss die aktive Routing-API-Version explizit pinnen, kein implizites `latest`.

## 6. Constraints (operationalisierbar)

**Regel: Jeder Constraint muss in eine prüfbare Regel übersetzt sein. Schwammige Angaben wie „sicher" oder „schnell" gehören hier nicht hin.**

### Datenschutz

- **Keine Klarnamen** im System – Regel: Schemas für Einsatzkraft enthalten keine Identitäts-PII (kein Name, keine Mail, keine Telefonnummer); Disponenten-/Betreuer-Schemas enthalten Username, optional Email für Reset-Flow.
- **Anonyme Sessions für Einsatzkräfte** – Regel: Session-Datensatz hat ausschließlich `session_id`, `einsatz_id`, ggf. letzten Standort (mit Lebensdauer-Limit), keine User-Referenz.
- **Aggregierte Statistiken bleiben dauerhaft, individuelle Bestell- und Standortdaten 30 Tage nach Einsatzende** – Regel: `backend/retention` läuft als zeitgesteuerter Procrastinate-Job, ausgelöst durch das Ereignis „Einsatz beendet" plus 30-Tage-Karenz; während eines laufenden Einsatzes wird nichts anonymisiert. Vor dem Löschen werden Aggregations-Tabellen gepflegt. Vision Abschnitt 6 ist hier maßgeblich.
- **Keine PII in Logs** – Regel: zentraler Logger-Wrapper mit Redaction-Liste; Standortdaten in Logs nur als gehashter Tile-Identifier, nie als Roh-Koordinate.
- **DSGVO-Datenexport** – Regel: asynchroner Procrastinate-Job, exponiert über das API-Tripel `POST /api/tenants/{id}/export` (startet Job), `GET /api/tenants/{id}/export/{job_id}` (Status), `GET /api/tenants/{id}/export/{job_id}/download` (ZIP-Download). Format: ZIP mit JSON pro Tabelle plus `manifest.json`. Detail siehe Abschnitt 11 (Grundsatzfrage „Datenexport-Format und Granularität").
- **DSGVO-Art. 17 Löschung** – greift implizit über die 30-Tage-Auto-Anonymisierung; mandantenseitige Stamm- und Aggregations-Daten haben gesonderte Löschpfade über Mandanten-Deaktivierung.

### Sicherheit

- **Authentifizierung Pflicht** auf allen API-Endpoints außer `/health`, `/api/auth/login`, `/api/auth/register-tenant` (Antrag), `/api/anon/{einsatz_url}/*` (mit URL-Validierung und optionalem Zugangscode).
- **Passwort-Hashing:** Argon2id direkt über `argon2-cffi` mit Library-Default-Parametern; minimum 12 Zeichen, kein Maximum, keine künstlichen Komplexitätsregeln (Länge schlägt Klasse).
- **Sessions:** Cookie-basiert, `Secure` + `HttpOnly` + `SameSite=Strict`, signiert; Session-Timeout 24 h für Disponent/Betreuer, 8 h für Administrator, einsatzgebunden für anonyme Einsatzkraft.
- **Rate-Limit auf Login:** maximal 5 Fehlversuche pro 15 min pro IP-Adresse plus pro User getrennt.
- **Anonyme Einsatz-Session:** pro Einsatz neu erzeugte URL mit kryptographisch zufälligem Token, alte URLs verfallen mit Einsatzende; optional Zugangscode obendrauf.
- **Geografische Plausibilitätsprüfung** auf Einsatzkraft-Bestellungen – Regel: Distanz vom GPS-Standort zum nächstgelegenen aktiven Einsatzraum > Schwellenwert (initial 5 km, anpassbar pro Einsatz) wirft Bestellung in Disponenten-Moderation, nicht in Auto-Verteilung.
- **API-Keys (MapTiler, TomTom)** ausschließlich Backend-seitig; nie im Client-Bundle, nie in Logs.

### Performance

- **Tile-Caching:** statische Tiles ≥ 7 Tage TTL, mandanten-/einsatz-übergreifend (Tiles sind nicht personenbezogen).
- **Routing-Aufrufe:** maximal 1 pro Auftrag, frühestens 30 s erneut für dasselbe Fahrzeug; Cache von Routen für identische (Start, Ziel)-Paare im 60-s-Fenster.
- **API-Budget Externdienste:** ~50 €/Monat über alle aktiven Einsatztage – Verbrauchszähler im `backend/geo`-Modul Pflicht; Überschreitung erzeugt Disponenten-Warnung und ggf. automatischen Fallback auf rein lokale Tile-Wiedergabe.
- **p95-Antwortzeit Backend-API:** < 300 ms bei der unter Abschnitt 2 angenommenen Last (Annahme, in STABILISIERUNG zu validieren).
- **Datenbankabfragen:** keine N+1-Muster, kein `SELECT *`; Linter-/Review-Regel.

### Plattform und Kompatibilität

- Backend lauffähig auf x86_64 und arm64 (Hetzner CCX-Reihe).
- Frontend-Targets: jeweils aktuelle Major minus eine Major (Chrome, Safari, Firefox, Edge), in jedem Fall mit Service-Worker-Support.
- PWA-Service-Worker müssen offline-fähig sein für Karten-Tiles im aktuellen Einsatzraum und für die letzten Auftragsdaten des angemeldeten Betreuers.

### Compliance und Lizenz

- **Projektlizenz:** AGPLv3.
- **Erlaubte Abhängigkeitslizenzen:** MIT, BSD-2/BSD-3, Apache-2.0, MPL-2.0, ISC.
- **Ausgeschlossene Lizenzen:** GPL/LGPL als Backend-Dependency (außer per ADR ausdrücklich freigegeben), proprietäre/commercial-only, RSALv2, SSPL, Confluent-Community-License, Elastic-License.
- **Begründung der GPL/LGPL-Restriktion trotz AGPLv3-Hauptlizenz:** Technisch wäre AGPLv3 mit GPL/LGPL-Dependencies kompatibel. Die Restriktion auf permissive Lizenzen ist eine bewusste strategische Wahl, um einzelne Module später ohne Lizenz-Reibung als eigenständige Bibliotheken extrahieren zu können (z. B. die Tile-Cache-Logik oder den Routing-Adapter), falls sie über EB Digital hinaus nutzbar werden. Abweichung im Einzelfall via ADR möglich.
- **Aktive Ausnahmen** (im Einzelfall via ADR freigegeben):
  - **psycopg 3 (LGPL-3.0-only)** als Pflicht-Sub-Dependency von `procrastinate` — siehe **ADR-011**. Verschmutzung beschränkt auf den Persistenz-/Job-Engine-Pfad; Module ohne Job-Engine-Bezug (`infra/tile-proxy`, Routing-Adapter in `backend/geo` u. ä.) bleiben extraktions-fähig.
- **Sub-Dependency-Lizenz-Prüfung:** Pflicht-Sub-Dependencies neuer Top-Level-Komponenten werden **vor** Aufnahme gegen die Erlaubt-/Ausschluss-Liste geprüft (Regel-016). Treffer auf eine ausgeschlossene Lizenz erzwingt entweder einen ADR (analog zu ADR-011) oder Verzicht auf die Top-Level-Komponente.
- **DSGVO** gilt; Operationalisierung siehe Abschnitt „Datenschutz" oben.

### Methodik-Schwellenwerte

- **Reaktiv-ADR-Schwellenwert:** maximal 20 % `[REAKTIV]`-Anteil über die letzten 10 ADRs (Klasse G). Bei Überschreitung Hinweis in `decisions.md` Teil A und Reflexions-Schritt im Fahrplan vor weiteren UMSETZUNG-Schritten.
- **Vorläufig-zu-Belastbar-Verhältnis:** nach jeder UMSETZUNG-Phase mindestens ein `[VORLÄUFIG]`-Bestandteil der berührten Module auf `[BELASTBAR]` befördert, sonst Reflexion in `fahrplan.md`.

## 7. Code-Standards und Qualitätsziele

Pflichtkategorien sind in `CLAUDE.md` Abschnitt 15 definiert. Tool-Wahl pro Sprache hier verbindlich; Abweichung erfordert ADR.

### Tool-Festlegung pro Sprache

#### Python

- **Linter:** ruff mit Konfiguration in `pyproject.toml` (Regelset `E,F,I,B,UP,SIM,RUF,N,S,A,C4,T20,PT,RET,SLF,ANN`).
- **Formatter:** ruff format, Zeilenlänge 100.
- **Type-Checker:** mypy mit `--strict` (alle Optionen aktiv).
- **Security-Scanner:** bandit.
- **Dependency-Audit:** pip-audit; Schwellenwert `high`.
- **Test-Runner:** pytest mit pytest-asyncio und pytest-cov.
- **Naming-Konvention:** PEP 8; snake_case für Funktionen/Variablen, PascalCase für Klassen, SCREAMING_SNAKE_CASE für Konstanten.

#### TypeScript

- **Linter:** eslint mit `@typescript-eslint`, `eslint-plugin-svelte`, `eslint-plugin-security`.
- **Formatter:** prettier mit `prettier-plugin-svelte`.
- **Type-Checker:** `svelte-check` und `tsc --strict --noUncheckedIndexedAccess --noImplicitReturns --noEmit`.
- **Security-Scanner:** `eslint-plugin-security` (statische Analyse) plus `pnpm audit` als Zusatz.
- **Dependency-Audit:** `pnpm audit` mit Schwellenwert `high`.
- **Test-Runner:** vitest mit Coverage; E2E: Playwright.
- **Naming-Konvention:** camelCase für Variablen/Funktionen, PascalCase für Typen/Klassen/Komponenten, kebab-case für Dateinamen außer Komponenten.

### Durchsetzungsmechanismen

- **Pre-Commit-Hook-Framework:** `pre-commit` (Python-basiert, multi-language).
- **Konfigurationsdatei:** `.pre-commit-config.yaml` im Repo-Root.
- **CI-Plattform:** GitHub Actions.
- **Workflow-Dateien (Klasse G):**
  - `.github/workflows/ci.yml` – alle Pflicht-Gates für Backend und Frontends, Matrix für die drei Frontend-Pakete.
  - `.github/workflows/security.yml` – Dependency-Audit + Security-Scan, separat aufrufbar (z. B. wöchentlicher Cron + on-demand).
  - `.github/workflows/release.yml` – wird in späterer Phase angelegt (zunächst manuelles Deployment).
- **Trigger:** mindestens `push` (alle Branches) und `pull_request` (Hauptbranch).
- **Verpflichtende CI-Gates (Merge-Block bei Rot):**
  - Lint (ruff, eslint).
  - Format-Check (ruff format --check, prettier --check). Kein Auto-Fix in CI.
  - Type-Check (mypy --strict, svelte-check, tsc --noEmit).
  - Security-Scan (bandit, eslint-plugin-security).
  - Dependency-Audit (pip-audit, pnpm audit; Schwellenwert `high`).
  - Tests inklusive Coverage-Mindestwert.
- **Branch-Protection auf Hauptbranch:** alle Pflicht-Gates grün; Force-Push gesperrt; Approvals siehe Abschnitt 10.

### Coverage-Mindestwerte

- **Globaler Mindestwert:** 80 % Lines, 70 % Branches.
- **Kritische Pfade (höhere Anforderung):**
  - `backend/auth` und `backend/auth_anonymous`: ≥ 95 % Lines, ≥ 90 % Branches.
  - `backend/operations` (Auftragszuweisung, Stornierung, Bündelung): ≥ 90 % Lines.
  - `backend/retention` (DSGVO-Auto-Löschung): ≥ 95 % Lines.
  - `backend/resilience` (Backup/Wiederherstellung): ≥ 90 % Lines.
- **Ausnahmen:**
  - `infra/tile-proxy`: nicht durch Coverage messbar (nginx-Konfiguration); stattdessen Smoke-Test über curl + Snapshot-Diff.
  - `infra/reverse-proxy`: dito (Caddy-Konfiguration).

### Commit-Lint

- **Tool:** commitlint mit Conventional-Commits-Konfiguration.
- **Erlaubte Typen:** feat, fix, refactor, docs, test, chore, perf, build, ci, init.

### Editor-Integration (empfohlen, nicht erzwungen)

- **EditorConfig:** `.editorconfig` im Repo-Root – LF-Zeilenenden, UTF-8, 4 Spaces für Python, 2 Spaces für TypeScript/Svelte/YAML/JSON.

## 8. Betrieb und Deployment

- **Deployment-Ziel:** Hetzner CCX-VPS in Deutschland; Docker Compose mit Profilen für lokal, staging, production.
- **CI/CD:** GitHub Actions als Pflicht-Gates (siehe Abschnitt 7). Deployment-Workflow `release.yml` wird in späterer Phase aktiviert; initial: manuelles Deployment per SSH und `docker compose up -d` aus aktualisiertem Compose-File.
- **Umgebungen:**
  - **lokal:** `docker compose --profile dev up`.
  - **staging:** kleinerer VPS oder gleicher Host mit eigenem Compose-Profil; nicht öffentlich, ohne echte Mandantendaten.
  - **production:** dedizierter Hetzner-VPS in DE.
- **Monitoring:** initial nur strukturierte JSON-Logs plus Caddy-Access-Logs; Erweiterung um Healthcheck-Dashboard und Verbrauchszähler externer Dienste in STABILISIERUNG-Phase.
- **Logging-Level Default:** `INFO` in Prod, `DEBUG` nur lokal.

## 9. Entscheidungsbefugnisse

- **Freigabe-Entscheidungen trifft:** Patrick Schulz (Repo-Eigentümer und initialer Plattform-Betreiber).
- **Kommunikationskanal für Freigaben:** direkt im Chat oder als Kommentar im Pull Request.
- **Reaktionszeit-Erwartung:** asynchron, keine harte Antwortzeit.

## 10. Repository-Regeln

- **Hauptbranch:** `main`.
- **Push-Regel:** Vor erstem Produktiv-Deploy direkter Push auf `main` erlaubt (Initialisierungsphase). Ab erstem Produktiv-Deploy (Status `Aufbau` → `aktive Entwicklung`): nur über PR mit grünen Pflicht-Gates.
- **Schutzregeln:** keine Force-Pushes auf `main`, keine `--no-verify`-Commits ohne ADR-Begründung, gelöschte Branches nur nach Merge.

## 11. Offene Grundsatzfragen

Punkte, die zu Projektstart bewusst offen sind. Claude arbeitet nicht an Bereichen, die von einer offenen Grundsatzfrage abhängen, ohne vorher eine Klärung anzustoßen.

**Aus Vision Abschnitt 9 übernommen:**

- **Plattform-Betreiber-Governance** – wer betreibt die zentrale Multi-Tenant-Instanz nach der Initialphase: Patrick persönlich, gewerkschaftlicher Trägerverein, neutrale Stiftung? Klärung vor Produktivbetrieb.
- **Test-Termin (reale Großlage)** – konkretes Anker-Datum im 3–6-Monats-Fenster festzulegen.
- **Parallele Mandanten an derselben Großlage** – ~~Verbund-Modus oder Out-of-Band-Absprache~~ **GEKLÄRT 2026-05-07:** Verbund-Modus mit gemeinsamem Auftragspool ist Ziel, wird aber nicht in Phase 1 implementiert. Stattdessen Phase 1 architektonisch verbund-tauglich vorbereiten; eigene UMSETZUNG-Phase mit ERKUNDUNG-Vorlauf später im Fahrplan.
  - **Vision-Verhältnis:** Reinterpretation – Verbund ist opt-in-Erweiterung der Anbieterseiten-Trennung, keine Aufhebung. Solange beide Mandanten ausdrücklich zustimmen, ist die Default-Trennung nicht verletzt, sondern bewusst delegiert.
  - **Phase-1-Architektur-Invarianten** (für spätere additive Einführbarkeit ohne Tabellen-Refactoring):
    - **I1:** Einsatz↔Mandant über Verknüpfungstabelle `einsatz_mandant_teilnahme(einsatz_id, mandant_id, rolle)`; Phase 1 genau ein Eintrag mit `rolle='eigentümer'`. Kein direkter `einsatz.mandant_id`-Foreign-Key.
    - **I2:** Berechtigungs-Filter „Einsätze, an denen mein Mandant teilnimmt" statt „Einsätze meines Mandanten". Phase 1 verhaltensgleich.
    - **I3:** Fahrzeug-Zuweisung in `backend/operations.assign_vehicle()` prüft Einsatz-Kontext (Teilnahme), nicht Mandanten-ID-Match.
    - **I4:** Aggregat (Frage C) bleibt Phase 1 mit einer `mandant_id` pro Eintrag; spätere Schema-Migration auf „verarbeitende Mandanten" wird im Architektur-Dokument als bekannte spätere Aufgabe vermerkt (keine versteckte technische Schuld).
    - **I5:** Datenexport (Frage D) bleibt Phase 1 auf `rolle='eigentümer'` reduziert; spätere Verbund-Aufträge werden als geteilte Datensätze mit Quell-Markierung ergänzt.
  - **Modul-Zuordnung der späteren Verbund-Erweiterung:** kein eigenes `backend/verbund`-Modul in Phase 1. Spätere Funktionalität als Erweiterung von `backend/tenants` (Verbund-Verträge: Initiative, Akzeptanz, Auflösung) und `backend/operations` (Cross-Mandanten-Disposition, gemeinsame Einsatz-URL). Falls bei der späteren Implementierung Modulgrenzen unscharf werden, wird per ADR ein eigenes Modul ausgegliedert.
  - **Fahrplan-Konsequenz:** spätere UMSETZUNG-Phase „Verbund-Modus für parallele Mandanten-Großlagen" mit ERKUNDUNG-Vorlauf (Stakeholder-Klärung mit zwei Mandanten, Berechtigungs-Modell, Statistik-Zuordnung) wird in Modus-2-Schritt 6 als spätere Phase in den Fahrplan aufgenommen.
  - **Begründung:** Solo-Mandant-Phase 1 bleibt klein und testbar; Verbund-Modus wird ohne spätere Tabellen-Refactor-Schulden möglich. Vision-Constraint der Anbieterseiten-Trennung bleibt als Default unangetastet. ADR folgt in Modus-2-Schritt 5.
- **Multi-Disponent-Hierarchie pro Einsatz** – ~~Lead vs. Gleichberechtigung~~ **GEKLÄRT 2026-05-07:**
  - **Modell:** kein Lead. Alle Disponenten am Einsatz sind voll gleichberechtigt – auch für destruktive Aktionen („Einsatz beenden", Zugangscode-Toggle, Einsatzraum-Geometrie ändern, Versorgungs-Transporter-Modus wechseln).
  - **Audit-Log:** alle kritischen Aktionen werden in der Tabelle `einsatz_audit_log` mit Akteur (Disponenten-ID), Aktionstyp, Zeitstempel und Zielobjekt-Referenz erfasst. Sichtbar im Disponenten-UI für alle Disponenten am Einsatz und für Plattform-Administrator. Liefert gleichzeitig die Datengrundlage für die `anzahl_disponierungs…`-Felder im Aggregat (Frage C).
  - **UX-Schutz vor versehentlichen destruktiven Aktionen:** Bestätigungs-Dialog im Disponenten-Frontend vor dem Auslösen (Implementierungs-Detail im `frontend-disponent`, kein Architektur-Block).
  - **Begründung:** Plattform-Administrator nicht zuverlässig erreichbar; Disponenten haben den operativen Überblick und sollen ohne Eskalations-Hürde handlungsfähig sein. Schutz gegen Großschäden trägt der Bestätigungs-Dialog plus retrospektive Nachvollziehbarkeit über Audit-Log. ADR folgt in Modus-2-Schritt 5.
- **Administrator-Architektur bei Multi-Tenancy** – ein zentraler Plattform-Administrator vs. ein Administrator pro Mandant; in der Anfangsphase ein zentraler Administrator (Patrick), Skalierungs-Frage offen.
- **Zugangscode-Erzeugung und -Verteilung** – ~~Code-Format, Wiederverwendung, UI-Unterstützung~~ **GEKLÄRT 2026-05-07:**
  - **Format:** 6 Zeichen Crockford-Base32 (Großbuchstaben + Ziffern, ohne O/0/I/1/L) – z. B. „X7K3PQ".
  - **Wiederverwendung:** ein Code pro Einsatz, von beliebig vielen Einsatzkräften nutzbar, läuft mit Einsatz-Ende ab.
  - **Aktivierung während laufendem Einsatz:** wirkt nur auf neu startende Sessions / neue Bestellungen; bestehende anonyme Sessions bestellen weiter ohne Code bis Session-Ablauf.
  - **Disponenten-UI:** Anzeige + Copy-to-Clipboard + QR-Code (rendert kombinierte Einsatz-URL inkl. Code). Druck/PDF-Export nicht in Phase 1.
  - **Rotation:** keine systemseitige Rotation in Phase 1; bei Kompromittierungsverdacht beendet der Disponent den Einsatz und eröffnet einen neuen (URL + Code werden gemeinsam erneuert). 5.B (Rotate-Button) als Stabilisierungs-Erweiterung später nachrüstbar.
  - **Begründung:** Vision-treu (URL bleibt Hauptfaktor, Code opt-in, niedrigschwellig), DSGVO-konsistent (kein PII-Touch), kleinster sinnvoller Funktionsumfang mit klarem Erweiterungspfad. ADR folgt in Modus-2-Schritt 5.
- **Sperrungs-Override-Technik im Routing** – wie eine vom Disponenten freigeschaltete Strecke technisch in die TomTom-Routing-Anfragen einfließt (Custom-Areas, Route-Bias, Penalty-Map); Erkundungs-Spike vor erster Implementierung des `backend/geo`-Moduls. **Risiko-Hinweis:** jeder Override löst potenziell Re-Routing aus und belastet das API-Budget – die gewählte Technik muss das budgetschonend lösen.

**Im Härtungs-Schritt zusätzlich identifiziert:**

- **Schriftliche Onboarding-Unterlagen für Mandanten** (DSGVO-Vereinbarung, Nutzungsbedingungen, Haftungsklarheit) – nicht-technische Voraussetzung für die erste Mandanten-Freischaltung. Ohne diese Templates kann Self-Service-Onboarding zwar technisch laufen, aber kein Mandant produktiv freigeschaltet werden. Erstellung ist ein Asset außerhalb des Codes, muss aber im Fahrplan vor erstem Produktiv-Mandant terminiert sein.
- **Admin-Bootstrap-Flow** – ~~wie der allererste Plattform-Administrator angelegt wird~~ **GEKLÄRT 2026-05-07:** CLI-Befehl im Backend-Container (`docker compose exec backend python -m eb_digital admin create`, Username als Argument, Passwort interaktiv via getpass). Jederzeit nutzbar (kein Single-Use-Bootstrap), legt auch nachträglich weitere Plattform-Admins an. Begründung: niedrigste Angriffsfläche, kein Klartext-Passwort in ENV/Compose-File/Logs, kein frühes Web-Setup-UI nötig, hält die offene Skalierungsfrage „zentraler vs. mehrere Admins" ohne Architekturzwang offen. ADR folgt in Modus-2-Schritt 5.
- **Aggregations-Schema für dauerhafte Statistiken** – ~~welche Felder vor 30-Tage-Anonymisierung in Aggregations-Tabellen~~ **GEKLÄRT 2026-05-07:**
  - **Aggregations-Einheit:** pro Einsatz – ein finaler Aggregat-Eintrag beim Einsatz-Ende. Übergreifende Roll-ups (pro Mandant, pro Tag/Monat) per SQL-Sum ableitbar.
  - **Metriken-Set pro Eintrag:** mandant_id, einsatz_id, zeitraum_start, zeitraum_ende, anzahl_einsatzraeume, anzahl_bestellungen, anzahl_fahrauftraege, anzahl_stornierungen, anzahl_buendelungen, anzahl_versorgungs_transporter_aktivierungen je Modus, anzahl_zugangscode_aktiviert, anzahl_strecken_freigaben (Sperrungs-Override), anzahl_hilfe_meldungen, gesamt_fahrdistanz_km (gerundet auf 1 km), aktive_fahrzeuge_max, aktive_disponenten_max. Keine Personen-Buckets (kein Pseudonym-Hash für Betreuer/Disponent).
  - **Geo-Information:** Stadt-/Region-Label als String (vom Disponenten beim Einsatz-Eröffnen gesetzt, z. B. „Bremen Innenstadt"). Keine Geometrie-Persistenz in Phase 1.
  - **Zugriff:** Mandanten-Disponenten sehen Aggregate ihres eigenen Mandanten; Plattform-Administrator sieht alle. Keine Cross-Mandanten-Veröffentlichung in Phase 1.
  - **Anonymisierungs-Reihenfolge:** Aggregat wird sofort beim Einsatz-Ende geschrieben (Snapshot). Anonymisierungs-Job läuft 30 Tage später entkoppelt und löscht nur noch Detail-Daten.
  - **Begründung:** balanciert DSGVO-Anspruch mit operativer Nutzbarkeit, hält Großlagen-Identität für Rückblicke ohne Re-Identifikations-Risiko, idempotente Reihenfolge ohne Race-Bedingungen. ADR folgt in Modus-2-Schritt 5.
- **Datenexport-Format und Granularität** – ~~synchron/asynchron, Format, Anhänge~~ **GEKLÄRT 2026-05-07:**
  - **Verfahren:** asynchron via Procrastinate-Job. API-Tripel `POST /api/tenants/{id}/export` (startet Job, liefert Job-ID), `GET /api/tenants/{id}/export/{job_id}` (Status), `GET /api/tenants/{id}/export/{job_id}/download` (ZIP-Download).
  - **Format:** ZIP mit JSON-Datei pro Tabelle plus `manifest.json` (Schema-Version, Export-Datum, Mandanten-ID, Tabellen-Liste mit Datensatzzahl).
  - **Inhalt:** vollständige Mandanten-Daten (Stammdaten, Disponenten-/Betreuer-Accounts ohne Passwort-Hashes, Fahrzeug-Stammdaten + Beladungs-Historie, mandantenspezifischer Artikelkatalog, Einsätze, Bestellungen + Fahraufträge der letzten 30 Tage detailliert, danach anonymisiert, Aggregations-Tabelle). Keine Karten-Snapshots, keine externen Anhänge.
  - **Auslöser:** Self-Service durch Disponent / Mandanten-Admin-Disponent im eigenen Mandanten; Plattform-Administrator kann jeden Mandanten exportieren.
  - **Lebensdauer:** fertiges ZIP unter `/var/eb-digital/exports/{tenant_id}/{job_id}.zip`, 7 Tage abrufbar (mehrfacher Download), danach Cleanup-Job (zweiter Procrastinate-Job).
  - **Begründung:** asynchron nutzt vorhandenen Procrastinate-Stack und löst Worker-Block-Risiko bei großen Mandanten; ZIP+JSON+manifest ist migrations-tauglich und versioniert; vollständige Daten erfüllen DSGVO-Anspruch ohne Phase-1-Komplexität von Karten-Anhängen. ADR folgt in Modus-2-Schritt 5. **Hinweis:** Endpunkt-Skizze in Abschnitt 6 unten ist mit angepasst.

### Triage-Stand 2026-05-07 (Klärungs-Session vor Modus-2-Schritt 4)

Die obigen sechs „GEKLÄRT 2026-05-07"-Einträge bilden Schublade 1 der Triage. Die übrigen Punkte werden in Modus-2-Schritt 6 (Fahrplan-Befüllung) wie folgt eingearbeitet:

- **Schublade 2 – ERKUNDUNG-Spikes vor jeweiliger UMSETZUNG-Phase:**
  - Sperrungs-Override-Technik im Routing (oben gelistet, **G**)
  - Resilience-Granularität (Vision Abschnitt 9, **H**)
  - Geografischer Plausibilitäts-Algorithmus (Vision Abschnitt 9, **I**)
  - Bündelungs-Trigger (Vision Abschnitt 9, **J**)
  - Hilfe-Knopf-Semantik (Vision Abschnitt 9, **K**)
  - Kartenmaterial-Offline-Caching-Technik (Vision Abschnitt 9, **L**)
  - Fahrzeugbezeichnungs-Schema (Vision Abschnitt 9, **M**)
    Detail-Skizzen pro Spike (Phasentyp ERKUNDUNG, Schritt-Art, Zeitbox, zu klärende Fragen, erwartetes Ergebnis) liegen im `[BEOBACHTUNG]`-Eintrag vom 2026-05-07 16:35 im Logbuch und werden in Modus-2-Schritt 6 in `fahrplan.md` aufgenommen.

- **Schublade 3 – organisatorische Roadmap-Meilensteine ohne Code:**
  - Plattform-Betreiber-Governance (oben gelistet, **N**) – auch Verbindung zu „Administrator-Architektur bei Multi-Tenancy" (oben gelistet), weil die Wahl der Trägerstruktur die Skalierungsfrage zentraler vs. mehrere Plattform-Admins beeinflusst.
  - Test-Termin reale Großlage (oben gelistet, **O**)
  - Schriftliche Onboarding-Unterlagen für Mandanten (oben gelistet, **P**)
    Wird in Modus-2-Schritt 6 als Roadmap-Meilensteine im Fahrplan platziert (vor produktivem Mandanten-Onboarding bzw. in der STABILISIERUNG-Phase).

## 12. Glossar (projektspezifische Begriffe)

- **Mandant:** Berufsverband (Landesverband), der EB Digital für seine Einsatzbetreuung nutzt; initial DPolG Bremen.
- **Anbieterseite:** Disponent, Betreuer, Fahrzeuge eines Mandanten – also alle authentifizierten, dem Mandanten zugeordneten Akteure.
- **Bezieherseite:** Einsatzkraft, anonym und mandantenneutral.
- **Cross-Berufsverbands-Versorgung:** ein Mandant versorgt während einer Großlage auch Einsatzkräfte aus anderen Berufsverbänden – gelebte solidarische Praxis und Selbstverständnis des Systems.
- **Einsatz:** zeitlich begrenzte Großlage mit ein oder mehreren Einsatzräumen, von einem Disponenten eröffnet und beendet.
- **Einsatzraum:** geographische Fläche auf der Karte, innerhalb derer Einsatzkräfte als legitim plausibilisiert werden.
- **Einsatzkraft-URL:** pro Einsatz neu erzeugte URL mit zufälligem Token, über die anonyme Sessions starten.
- **Zugangscode:** optional pro Einsatz vom Disponenten aktivierbarer Zusatzfaktor; Default: aus.
- **Reguläres Betreuungsfahrzeug:** Fahrzeug, das Einzelaufträge im Einsatzraum fährt.
- **Versorgungs-Transporter:** zweite Fahrzeugrolle in Transportergröße mit drei vom Disponenten festgelegten Betriebszuständen (außer Betrieb / mobile Nachschubstelle / Großbestellungs-Modus).
- **Geschäftsstelle:** stationäre Hauptversorgungsstelle des Mandanten, von der Schichten starten.

---

**Pflegehinweis:** Änderungen an Status, Stack oder Constraints sind freigabepflichtig (siehe `CLAUDE.md` Abschnitt 4) und erzeugen einen ADR-Eintrag. Statuswechsel (z. B. `Konzeption` → `Aufbau`) ziehen außerdem README-Badge- und CHANGELOG-Updates nach sich.
