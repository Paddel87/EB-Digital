# EB Digital

<!-- Diese README spiegelt den aktuellen Umsetzungsstand des Projekts wider.
     Sie ist KEIN sporadisch gepflegtes Marketing-Dokument, sondern ein lebendes Statusbild.
     Aktualisierungs-Pflicht (CLAUDE.md Abschnitt 16):
       - bei jedem nutzerrelevanten Fahrplan-Schritt während der Bearbeitung
       - vor jedem Sessionende mit Synchronisations-Prüfung gegen Pflicht-Dokumente
     Inhalte stammen aus den Pflicht-Dokumenten und müssen mit ihnen konsistent sein.
     Drift zwischen README und Pflicht-Dokumenten ist ein Bug. -->

![Status](https://img.shields.io/badge/status-konzeption-lightgrey)
![Version](https://img.shields.io/badge/version-v0.1.0-blue)
![Build](https://img.shields.io/github/actions/workflow/status/Paddel87/EB-Digital/ci.yml?branch=main)
![License](https://img.shields.io/badge/license-AGPL--3.0-blue)

![Python](https://img.shields.io/badge/python-3.13-blue)
![Node](https://img.shields.io/badge/node-24--LTS-green)
![Last Commit](https://img.shields.io/github/last-commit/Paddel87/EB-Digital)

> Multi-Tenant-Plattform zur Echtzeit-Koordination ehrenamtlicher Einsatzbetreuung bei polizeilichen Großlagen.

## Über das Projekt

EB Digital ersetzt die heute übliche WhatsApp-Improvisation bei der ehrenamtlichen Einsatzbetreuung polizeilicher Großlagen durch ein strukturiertes, serviceorientiertes Auftragssystem. Disponenten, Betreuungsfahrzeuge und Einsatzkräfte arbeiten über rollenspezifische Oberflächen zusammen – mit Live-Karte, automatischer Fahrzeugzuweisung, anonymer Bestellfunktion für Einsatzkräfte und kollaborativer Multi-Disponenten-UX.

**Was es löst:** Fehlende Echtzeit-Koordination zwischen Disponenten, Betreuungsfahrzeugen und Einsatzkräften bei Großlagen – ohne Lagebild, ohne automatische Fahrzeugzuweisung, ohne Statusrückmeldung.

**Für wen:** Ehrenamtliche Strukturen polizeilicher Berufsverbände als Anbieter (initial DPolG, perspektivisch GdP und weitere). Polizeibedienstete im Außendienst als anonyme Bezieherseite. Cross-Berufsverbands-Versorgung ist gelebte solidarische Praxis und Teil des Selbstverständnisses des Systems.

**Was es bewusst nicht ist:**

- Kein Behörden-IT-Anschluss, kein operatives Lagebild im behördlichen Sinne, keine Einsatzversorgung im behördlichen Sinne.
- Keine Klarnamen-Verwaltung; Einsatzkräfte erhalten anonyme Temporär-Sessions.
- Keine Mitgliedschaftsprüfung der Einsatzkraft – verbandsoffener Zugriff über die Einsatz-URL.
- Keine Hilfe-Funktion für Einsatzkräfte (läuft über den polizeilichen Dienstweg).
- Keine native App in Phase 1 – ausschließlich PWA.
- Keine US-Cloud-Anbieter, kein Tracking, keine SaaS-Auth-Provider.

## Aktueller Status

<!-- Dieser Block wird vor jedem Sessionende synchronisiert mit:
     - project-context.md Abschnitt 1 (Status, Version)
     - fahrplan.md Abschnitt „Aktueller Stand"
     - architecture.md Abschnitt 9 (Reifegrad-Übersicht)
     - decisions.md Teil A (ADR-Übersicht, Reaktiv-Quote)
     - blockers.md (Aktive Blocker)
     Inkonsistenzen sind Bugs und werden vor Sessionende behoben. -->

- **Projektphase:** Phase 2 (Auth + Tenants + Verbund-Tauglichkeit, UMSETZUNG) **in Arbeit**: Schritt 2.1 (Datenmodell-Skelett), Schritt 2.2 (`backend/auth` Login + Cookie-Sessions + Valkey-Rate-Limit nach ADR-013), Schritt 2.3 (`backend/auth_anonymous` URL-Token + AccessCode-Validierung + Anonymous-Session-Cookie), Schritt 2.4 (`backend/tenants` Self-Service-Antrag + Approve + CRUD + Reset-Token-Flow + S10 Participation-Lookup), Schritt 2.5 (`frontend-disponent` Login + Dashboard-Skelett + Reset-Password-UI) und Schritt 2.6 (`frontend-einsatzkraft` AccessCode-Eingabe-UI gegen S2a) alle `[ERLEDIGT]` 2026-05-10 / 2026-05-11 / 2026-05-12 / 2026-05-15 / 2026-05-16. **Hot-Stabilisierung 2.5b** am 2026-05-16: `get_db_session()` Lifecycle-Bug-Fix (FastAPI-yield-Dependency mit Rollback im Exception-Pfad, ADR-015 / Regel-018) — `[ERLEDIGT]` 2026-05-16. Phase 1 (Repo-Bootstrap & Tech-Foundations) vollständig abgeschlossen — Schritte 1.1–1.8 zwischen 2026-05-08 und 2026-05-10.
- **Version:** v0.1.0
- **Status:** Konzeption
- **Letzte Änderung:** 2026-05-16
- **Architektur-Reife:** 24 Bestandteile `[BELASTBAR]` (Stack-/NFR-/Datenschutz-Constraints + Schnittstelle S1 Admin-Bootstrap-CLI + `backend/auth`-Modul + Schnittstelle S8a `/api/auth/{login,logout,me}` + Valkey-Connection-Pool + NFR Anbieter-Austauschbarkeit für externe Geo-Services via ADR-014/Regel-017 + `backend/auth_anonymous`-Modul, Schnittstelle S2a `/api/anon/{url}/info`+`/session`, Datenmodell `anonymous_session` und Spalten-Widening `operation.url_token` 64→255 + seit Schritt 2.4 zusätzlich `backend/tenants`-Modul, Schnittstelle S8b `/api/auth/{register-tenant,reset-password}`+`/api/tenants/*`, Schnittstelle S10 Participation-Lookup, Invariante I1 `operation_tenant_participation` und Invariante I2 abstrakter Berechtigungs-Filter + seit Schritt 2.5b zusätzlich Request-Scoped DB-Session-Dependency `get_db_session` via ADR-015/Regel-018), ca. 23 `[VORLÄUFIG]` (Module inkl. drei Frontend-Skelette + zwei Infra-Module mit Phase-1-Smoke, restliche Schnittstellen, Invarianten I3–I5 — Phase-2-Sonderregel: Beförderung erfolgt mit dem jeweiligen funktionalen Schritt; `frontend-disponent` ist mit 2.5 und `frontend-einsatzkraft` ist mit 2.6 funktional validiert, beide bleiben `[VORLÄUFIG]` bis zum Last-Test in Phase 6 — Detail-Frage 5-A aus 2.5), 9 `[OFFEN]` (Spikes G–M, Bedrohungsmodell, Tracing). Architektur-Pattern Modular Monolith + drei SvelteKit-Frontends bleibt bis zum Last-/Funktionstest in Phase 6 `[VORLÄUFIG]`.
- **Aktive Blocker:** 0 (Blocker #001 am 2026-05-10 ursächlich aufgeklärt — macOS `UF_HIDDEN`-File-Flag auf `.venv` lässt Python 3.13 die Editable-`.pth` skippen; Heilung als Skript [`scripts/fix-venv-flags.sh`](scripts/fix-venv-flags.sh), siehe [`docs/blockers.md`](docs/blockers.md)).
- **ADRs:** 15 (9 `[STRATEGISCH]` aus INITIALISIERUNG + 4 `[OPERATIV]`: ADR-010 GitHub-Actions Major-Update + Verifikations-Regime, ADR-011 psycopg-LGPL-Akzeptanz und Sub-Dep-Lizenz-Regime, ADR-012 actions/upload-artifact v4 → v7 gegen Node-20-Deprecation, ADR-013 Rate-Limit als eigener Valkey-Counter + ADR-014 `[STRATEGISCH]` zu Anbieter-Austauschbarkeit für externe Geo-Services als Architektur-Prinzip + ADR-015 `[REAKTIV]` zu `get_db_session()` yield-Dependency mit Rollback als Hot-Stabilisierungs-Schritt 2.5b); Reaktiv-Quote 1/10 = 10 % (Schwellenwert 20 % nicht überschritten; zählt jetzt ADR-006 bis ADR-015).
- **Klassifikation:** Klasse G (Groß) – ADR-001.

## Quick Start

> **Hinweis Konzeptionsphase:** Das Repository enthält die Pflicht-Dokumente, das Tooling-Skelett (uv-/pnpm-Workspace, Pre-Commit-Hooks, CI-Pipeline auf GitHub Actions), das Backend-Skelett (FastAPI + Settings + JSON-Logging mit PII-Redaction + `/health` und `/api/health`), die Datenbank-Plumbing-Schicht (SQLAlchemy 2.0 Async-Engine + asyncpg, Alembic mit Async-Template, PostgreSQL-17.9-Service mit Digest-Pin), die Procrastinate-Job-Engine (ping-Test-Job, Worker-Subcommand, Worker-Container), die `backend/auth`-Bootstrap-Schiene (`PlatformAdmin`-Tabelle, Argon2id-Hashing, CLI `python -m eb_digital admin create`), die drei SvelteKit-Frontend-Skelette (Disponent ohne PWA, Betreuer + Einsatzkraft mit `vite-plugin-pwa`-Service-Worker und `/api`-NetworkFirst-Cache), die komplette Compose-Infrastruktur (Caddy reverse-proxy mit `tls internal` für `eb.local`/`localhost`, nginx tile-proxy mit 7-Tage-Cache und Phase-1-Stub, `db-init`-Migration vor backend/worker, `scripts/dev-smoke.sh` als End-to-End-Smoke-Test inkl. Auth-Smoke), das Phase-2-Datenmodell-Skelett aus 2.1 (`Tenant`, `Dispatcher`, `Carer`, `Operation` ohne Tenant-FK [Invariante I1, ADR-009], `OperationTenantParticipation` mit Partial-Unique-Index auf `role='owner'`, `OperationAuditLog` mit JSONB-Payload nach ADR-008) und seit Schritt 2.2 die produktive Auth-Schicht (Login-Endpoint `POST /api/auth/login` mit Argon2id-Verify und Timing-Attack-Schutz, signierte Cookie-Sessions via Starlette `SessionMiddleware` mit Role-spezifischen Timeouts, `POST /api/auth/logout` und `GET /api/auth/me`, eigener Valkey-basierter Rate-Limit-Counter nach ADR-013 mit IP+User-AND-Logik). Seit Schritt 2.3 zusätzlich die produktive Anonymous-Bezieher-Schicht (`backend/auth_anonymous` mit `itsdangerous`-signiertem URL-Token, Crockford-Base32-AccessCode-Generator, Argon2id-Konstantzeit-Verify gemäß Regel-006, IP+URL-Rate-Limit, 24-h-Hard-Cap-Cookie-Session) und Schnittstelle S2a (`GET /api/anon/{url}/info`, `POST /api/anon/{url}/session`). Seit Schritt 2.4 die produktive Mandanten-Verwaltung (`backend/tenants` mit Self-Service-Antrag `POST /api/auth/register-tenant` mit 3/24 h/IP-Rate-Limit, Plattform-Admin-Approve/Deactivate, Tenant-CRUD mit Rollen-Filter, Dispatcher-/Carer-Invite mit signiertem `URLSafeTimedSerializer`-Reset-Token (24-h-TTL, Salt-Separation gegen URL-Token aus 2.3), Reset-Password-Flow `POST /api/auth/reset-password` mit Replay-Schutz, Tenant-Status-Check im Login-Pfad), Schnittstelle S10 (Tenant Participation Lookup mit drei Funktions-Exporten gemäß Regel-013/014) und Invarianten I1+I2 (`operation_tenant_participation` als alleinige Mandanten-Verknüpfung, abstrakter Teilnahme-Filter). Seit Schritt 2.5 das produktive `frontend-disponent` (Login + Dashboard + Reset-Password-UI gegen S8a/S8b) und seit Schritt 2.6 das produktive `frontend-einsatzkraft` (AccessCode-Eingabe-UI gegen S2a: Landing-Erklärungsseite, dynamische Route `/[token]` mit `/info`-Load und Code-Form, separate Erfolgs-Route `/[token]/dashboard` mit In-Memory-Session-Guard, SPA-Mode mit `prerender=false; ssr=false` für die dynamische Token-Route, strikte Crockford-Base32-Pattern-Validation mit Auto-Uppercase, 47 Vitest-Tests grün mit 98.59 %/95.55 % Coverage). Phase-1-Foundations abgeschlossen, Phase 2 bei den Folgeschritten 2.7 (Tests + externe-Security-Review-Issue) plus Hot-Stabilisierung 2.5b (`get_db_session()`-Lifecycle-Fix nach ADR-015 / Regel-018 am 2026-05-16). Detail in [`docs/fahrplan.md`](docs/fahrplan.md).

### Voraussetzungen

- Docker Engine 29.4+ und Docker Compose v5.1+ (für Phase 1.4 ff. – PostgreSQL/Valkey-Container)
- uv 0.11+ (Python-Package-Manager) und Python 3.13
- pnpm 11+ und Node.js 24 LTS
- Optional: GitHub-Account für CI-Auslösung; SSH-Zugriff auf Hetzner-VPS für Production-Deployment

### Heute lauffähig

```bash
# Repository klonen
git clone https://github.com/Paddel87/EB-Digital.git
cd EB-Digital

# Pflicht-Dokumente lesen (Pflichtlektüre nach CLAUDE.md Abschnitt 2)
cat docs/project-context.md
cat docs/architecture.md
cat docs/fahrplan.md

# Tooling installieren und Pre-Commit-Hooks aktivieren
uv sync                                              # Python-Dev-Tooling (ruff, mypy, pytest, bandit, …)
# macOS-Hinweis: Wenn der Checkout unter einem versteckten Parent-Verzeichnis liegt
# (z. B. ein Claude-Code-Worktree unter .claude/worktrees/), nach dem ersten `uv sync`
# einmalig ausführen — entfernt UF_HIDDEN von der frischen .venv, sonst skippt
# Python 3.13 die Editable-.pth (siehe docs/blockers.md → Blocker #001):
bash scripts/fix-venv-flags.sh
pnpm install                                         # Node-Dev-Tooling (commitlint, prettier, …)
uv run pre-commit install \
  --hook-type pre-commit --hook-type commit-msg      # Hooks lokal aktivieren
uv run pre-commit run --all-files                    # Alle Hooks einmalig durchlaufen

# Backend-Skelett lokal starten (ab Schritt 1.3)
cp .env.example .env                                 # Platzhalter ersetzen, .env ist gitignored
uv run python -m eb_digital serve                    # Uvicorn auf 0.0.0.0:8000
curl http://localhost:8000/health                    # → {"status":"ok","version":"0.1.0"}

# Datenbank lokal hochziehen (ab Schritt 1.4)
docker compose --profile dev up -d db                # PostgreSQL 17.9 mit Digest-Pin und Healthcheck
uv run alembic upgrade head                          # Schema auf den aktuellen Stand bringen

# Worker im Container starten (ab Schritt 1.5; baut docker/Dockerfile.backend beim ersten up)
docker compose --profile dev up -d worker            # eb-digital-backend:dev → python -m eb_digital worker
docker compose --profile dev logs -f worker          # JSON-Logs der Job-Engine

# Plattform-Administrator anlegen (ab Schritt 1.6)
uv run python -m eb_digital admin create --username patrick   # interaktive Passwort-Eingabe via getpass
# → "created admin user: patrick" plus JSON-Audit-Log {message: "platform_admin_created", …}

# Frontend-Workspaces (ab Schritt 1.7)
pnpm -r build                                        # baut alle drei SvelteKit-Frontends
pnpm --filter frontend-disponent dev                 # Disponent-Dev-Server auf Port 5173
pnpm --filter frontend-betreuer dev                  # Betreuer-Dev-Server auf Port 5174 (PWA)
pnpm --filter frontend-einsatzkraft dev              # Einsatzkraft-Dev-Server auf Port 5175 (PWA)

# Komplettes dev-Profil (Backend + Worker + DB + Cache + Tile-Proxy + Reverse-Proxy, ab Schritt 1.8)
docker compose --profile dev up -d                   # 6 Services + db-init alle healthy
curl -k https://localhost/api/health                 # → {"status":"ok","version":"0.1.0"} via Caddy
bash scripts/dev-smoke.sh                            # End-to-End-Smoke (Caddy + Tile-Proxy + Healthchecks)

# Optional: Frontends als zusätzliches Profil
docker compose --profile dev --profile frontends up -d   # erster Start: pnpm install im Volume-Cache (mehrere Minuten)

uv run pytest                                        # 103 Backend-Tests, Coverage ≥ 80 % (aktuell 94 %)
pnpm -r test                                         # 3 Frontend-Smoke-Tests
```

## Architektur (Überblick)

```mermaid
graph LR
  FD["frontend-disponent<br/>SvelteKit"]
  FB["frontend-betreuer<br/>SvelteKit PWA"]
  FE["frontend-einsatzkraft<br/>SvelteKit PWA"]
  RP["infra/reverse-proxy<br/>Caddy"]
  BE["Backend<br/>Modular Monolith<br/>(11 Module)"]
  TP["infra/tile-proxy<br/>nginx"]
  PG[("PostgreSQL 17.9")]
  VK[("Valkey 8.1.7")]
  MT[MapTiler]
  TT[TomTom]

  FD --> RP
  FB --> RP
  FE --> RP
  RP --> BE
  BE --> TP
  BE --> PG
  BE --> VK
  TP --> MT
  TP --> TT
```

**Backend-Module (11):** `auth` (Login + Sessions + CLI-Bootstrap) · `auth_anonymous` (einsatz-URL + AccessCode) · `tenants` (Mandanten-Onboarding) · `catalog` (Artikelkatalog) · `operations` (Operations + Orders + Audit-Log) · `fleet` (Fahrzeuge + Beladung) · `geo` (Routing + Tile-Cache + Sperrungs-Override) · `realtime` (WebSocket-Hub) · `resilience` (Backup/Recovery) · `export` (DSGVO-Datenexport) · `retention` (30-Tage-Anonymisierung + Aggregat).

**Frontends (3):** `frontend-disponent` (Browser, Lagezentrum) · `frontend-betreuer` (PWA Mobile, Turn-by-Turn) · `frontend-einsatzkraft` (anonyme PWA).

**Infrastruktur (2):** `infra/reverse-proxy` (Caddy mit automatischem TLS) · `infra/tile-proxy` (nginx-Cache vor MapTiler/TomTom).

→ Vollständige Architektur: [`docs/architecture.md`](docs/architecture.md) · Architektur-Entscheidungen: [`docs/decisions.md`](docs/decisions.md)

## Verwendung

> Verwendungs-Beispiele werden ergänzt, sobald Phase 4 (Operations Core + Realtime + Einsatzkraft-PWA) abgeschlossen ist und ein End-to-End-Pfad lauffähig ist. Bis dahin spiegelt [`docs/architecture.md`](docs/architecture.md) Abschnitt 5 die geplanten Datenflüsse F1–F5.

## Nächste Schritte

1. **Schritt 2.7 – Tests + Coverage + externe-Security-Review-Issue** (UMSETZUNG, Phase-2-Abschluss): Abschluss-Schritt mit Test-/Coverage-Audit und Anlage eines Issues für die externe Security-Review vor Produktivstart (Phase 7). Schritt 2.6 (`frontend-einsatzkraft` AccessCode-Eingabe-UI gegen S2a) ist am 2026-05-16 ERLEDIGT, Schritt 2.5 (`frontend-disponent` Login + Dashboard + Reset-Password-UI) am 2026-05-15, Hot-Stabilisierung 2.5b (`get_db_session()` yield-Dependency mit Rollback nach ADR-015 / Regel-018) am 2026-05-16.
2. **Phase 3 – Spikes Wave 1 (ERKUNDUNG)**: Geografischer Plausibilitäts-Algorithmus (Spike I) und Bündelungs-Trigger (Spike J) als Vorklärung für Phase 4.

→ Vollständiger Fahrplan mit 7 regulären Phasen plus späterer Verbund-Erweiterungs-Phase X: [`docs/fahrplan.md`](docs/fahrplan.md)

## Mitwirken

- **Branch-Konvention:** Hauptbranch `main`. Feature-Branches `feat/<kurztitel>`, Bugfixes `fix/<kurztitel>`, Refactor `refactor/<kurztitel>`. In der Initialisierungsphase ist direkter Push auf `main` zulässig (Status `Konzeption`); ab Statuswechsel nur über Pull Request mit grünen Pflicht-Gates.
- **Commit-Format:** Conventional Commits in deutscher Sprache, atomar pro Änderung, Imperativ-Präsens. Bei freigabepflichtigen Änderungen: ADR-Nummer im Commit-Body. Pre-Commit-Hooks und `commitlint` sind Pflicht-Gates.
- **Code-Standards:** Python via uv + ruff (Linter+Formatter) + mypy `--strict` + bandit + pip-audit. TypeScript via pnpm + eslint (`@typescript-eslint`, `eslint-plugin-svelte`, `eslint-plugin-security`) + prettier + svelte-check + `tsc --strict --noUncheckedIndexedAccess`. Tests: pytest+Coverage (Backend, kritische Pfade ≥ 95 %), vitest+Playwright (Frontends). CI: GitHub Actions, drei Workflows (`ci.yml`, `security.yml`, später `release.yml`).
- **Methodik:** semi-autonomer Modus mit Claude Code (siehe [`CLAUDE.md`](CLAUDE.md)). Architektur-Entscheidungen werden in [`docs/decisions.md`](docs/decisions.md) als ADRs festgehalten; Reaktiv-Quote ≤ 20 % über die letzten 10 ADRs.
- **Dokumentationssprache:** Deutsch. **Codesprache (Bezeichner, Kommentare):** Englisch (Domänen-Begriffe übersetzt – siehe [`docs/architecture.md`](docs/architecture.md) Abschnitt 0).

## Dokumentation

| Dokument                                             | Inhalt                                                                                                                                                                                      |
| ---------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [`docs/vision.md`](docs/vision.md)                   | Ursprüngliche Projektvision (eingefroren nach Modus-2-Abschluss)                                                                                                                            |
| [`docs/project-context.md`](docs/project-context.md) | Aktueller Stack, Constraints, Qualitätsziele, Code-Standards                                                                                                                                |
| [`docs/architecture.md`](docs/architecture.md)       | Systemarchitektur, 14 Module, 10 Schnittstellen, 5 Datenflüsse, Reifegrad-Übersicht                                                                                                         |
| [`docs/fahrplan.md`](docs/fahrplan.md)               | Entwicklungsplan: 7 reguläre Phasen + Phase X (Verbund), Phase 1 voll detailliert                                                                                                           |
| [`docs/decisions.md`](docs/decisions.md)             | 14 ADRs (Klassifikation, Stack, Pattern, Fragen A–F, Actions-Updates, psycopg-LGPL-Akzeptanz, Rate-Limit als eigener Valkey-Counter, Anbieter-Austauschbarkeit) plus 17 Entscheidungsregeln |
| [`docs/blockers.md`](docs/blockers.md)               | Aktive Blocker (aktuell keine; #001 am 2026-05-10 gelöst) und Erkennungs-Heuristiken                                                                                                        |
| [`docs/logbuch.md`](docs/logbuch.md)                 | Chronologischer Flugschreiber: Sessions, Beobachtungen, Reifegrad-Wechsel, ADR-Anlagen                                                                                                      |
| [`CLAUDE.md`](CLAUDE.md)                             | Projektübergreifende Arbeitsmethodik (semi-autonomer Modus)                                                                                                                                 |

## Lizenz

Dieses Projekt steht unter der **GNU Affero General Public License v3.0** (AGPL-3.0); der vollständige Lizenztext liegt im [`LICENSE`](LICENSE)-File im Repo-Root.

**Erlaubte Abhängigkeitslizenzen:** MIT, BSD-2/BSD-3, Apache-2.0, MPL-2.0, ISC. **Ausgeschlossen:** GPL/LGPL als Backend-Dependency (außer per ADR), proprietär, RSALv2, SSPL, Confluent-Community-License, Elastic-License. Begründung in [`docs/project-context.md`](docs/project-context.md) Abschnitt 6.
