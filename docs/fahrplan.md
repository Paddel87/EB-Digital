# Fahrplan

<!-- Zentrales Arbeitsdokument. Wird vor jeder Änderung gelesen (CLAUDE.md Abschnitt 2)
     und nach jedem Arbeitsschritt sowie zu Sessionende aktualisiert (Abschnitt 12).
     Phasen sind nach Typ klassifiziert (Erkundung / Umsetzung / Stabilisierung),
     weil iterative Entwicklung unterschiedliche Erfolgskriterien pro Phasentyp braucht. -->

## Aktueller Stand

- **Stand vom:** 2026-05-09
- **Laufende Phase:** Phase 1 – Repository-Bootstrap & Tech-Foundations (UMSETZUNG).
- **Phasentyp:** UMSETZUNG (Phase-1-Sonderregel: Eingangsdisziplin abgemildert, Modul-Schnitt durch ADR-002/003/004 fixiert).
- **Aktiver Schritt:** keiner. **1.1 [ERLEDIGT]** 2026-05-08, **1.2 [ERLEDIGT]** 2026-05-08, **1.3 [ERLEDIGT]** 2026-05-09, **1.4 [ERLEDIGT]** 2026-05-09 (`backend/eb_digital/db/{__init__.py,models.py}` mit Async-Engine, Session-Factory, DeclarativeBase + Naming-Convention, TimestampMixin und HealthMarker-Sentinel; Alembic mit Async-Template + Baseline + Health-Marker-Migration; PostgreSQL-17.9-Service im Compose-`dev`-Profil mit Digest-Pin und Healthcheck; 19 neue Tests, Coverage 95 %; asyncpg 0.31.0 verifiziert und gepinnt).
- **Nächster Schritt:** **1.5 – Procrastinate-Setup + Worker** oder **1.7 – Frontend-Workspaces + PWA-Skelett** (laut Parallelisierungs-Notiz unabhängig voneinander). Eingangskriterien: 1.5 hängt an 1.4 ✓; 1.7 hängt an 1.1 ✓.
- **Offene STOPP-Situationen:** keine.

## Phasen-Typen

Jede Phase ist genau einem Typ zugeordnet. Der Typ bestimmt das Akzeptanzformat der Schritte.

### ERKUNDUNG

**Zweck:** Erkenntnis gewinnen. Klärung architektonischer Unsicherheiten, Validierung von Annahmen, Reduktion von Risiken vor Umsetzung.

**Charakteristika:**

- Akzeptanzkriterien sind **wissensbasiert**: „Wir verstehen X", „Wir können Y entscheiden", „Annahme Z ist validiert oder widerlegt".
- Output ist primär Erkenntnis, sekundär Code. Code in Erkundungsphasen ist explizit „Wegwerf-Code" oder Spike, sofern nicht anders gekennzeichnet.
- Architektur-Bestandteile werden während der Phase oft von `[OFFEN]` auf `[VORLÄUFIG]` befördert.
- Definition of Done ist reduziert: kein Coverage-Mindestwert, keine vollständige Testpyramide. Aber: Erkenntnisse müssen dokumentiert sein (in `decisions.md` oder `architecture.md`).
- Spike-Code, der weiterverwendet werden soll, durchläuft eine Stabilisierungsphase, bevor er als Produktivcode gilt.

**Typische Schritt-Arten:**

- **Spike** – zeitbegrenzte Untersuchung („maximal 4h, dann Erkenntnisse zusammenfassen")
- **Prototyp** – funktionsfähige Skizze einer Lösung, nicht produktiv
- **Vergleichsstudie** – mehrere Optionen gegeneinander prüfen
- **Lasttest / Messung** – NFR-Annahmen validieren

### UMSETZUNG

**Zweck:** Geplante Funktionalität auf Basis belastbarer Architektur produktiv bauen.

**Charakteristika:**

- Akzeptanzkriterien sind **funktionsbasiert**: konkrete Eingabe → erwartete Ausgabe, Tests grün, Coverage erfüllt.
- Architektur-Bestandteile, die der Schritt berührt, müssen vor Schrittbeginn `[BELASTBAR]` sein – sonst Stopp.
- Volle Definition of Done (CLAUDE.md Abschnitt 9) gilt.
- Wenn während der Umsetzung Architektur-Lücken auftauchen: Schritt **stoppen**, Lücke als `[OFFEN]` in `architecture.md` markieren, neuen ERKUNDUNG-Schritt anlegen, dann zurück.

### STABILISIERUNG

**Zweck:** Härten, was in vorherigen Phasen entstanden ist – inklusive Spike-Code, der produktiv weiterverwendet werden soll.

**Charakteristika:**

- Akzeptanzkriterien sind **qualitätsbasiert**: Coverage angehoben, Edge Cases abgedeckt, Lasttest bestanden, Sicherheits-Review durchgeführt, Refactoring-Schulden abgebaut.
- Output ist meist kein neues Feature, sondern höhere Robustheit der bestehenden.
- Volle Definition of Done gilt; zusätzlich projektspezifische Stabilisierungs-Kriterien aus `project-context.md`.
- Eine Stabilisierungsphase nach jeder Erkundungsphase, deren Ergebnisse weiterverwendet werden, ist Pflicht.

## Schritt-Format

Jeder Schritt folgt diesem Schema. Abweichungen nur nach Freigabe.

```
### [Phase].[Nummer]: Kurztitel

- **Status:** [OFFEN | IN ARBEIT | WARTET-AUF-FREIGABE | BLOCKIERT | ERLEDIGT | VERWORFEN]
- **Phasentyp-Kontext:** [ERKUNDUNG | UMSETZUNG | STABILISIERUNG] – ergibt sich aus der Phase
- **Schritt-Art (nur ERKUNDUNG):** [Spike | Prototyp | Vergleichsstudie | Lasttest | sonstiges]
- **Zeitbox (nur ERKUNDUNG):** [z. B. „maximal 4h Arbeit, dann Zwischenstand"]
- **Abhängigkeiten:** [Schritt-IDs, die vorher abgeschlossen sein müssen, oder "keine"]
- **Freigabepflichtig:** [ja/nein – siehe CLAUDE.md Abschnitt 4]
- **Eingangskriterien:** [was muss gegeben sein, bevor der Schritt begonnen werden kann; bei UMSETZUNG: alle berührten Architektur-Bestandteile auf [BELASTBAR]]
- **Zu tun:** [konkrete Arbeitsanweisung; bei UMSETZUNG implementierungsnah, bei ERKUNDUNG: zu klärende Fragen]
- **Akzeptanzkriterien:** [phasentypabhängig – wissensbasiert / funktionsbasiert / qualitätsbasiert]
- **Betroffene Module:** [Modulnamen – wenn >1, ggf. aufsplitten]
- **Reifegrad-Wirkung:** [welche Architektur-Bestandteile werden durch diesen Schritt befördert oder zurückgestuft]
- **Artefakte:** [erwartete Dateien/Änderungen; bei ERKUNDUNG: ADRs, Architektur-Updates, Erkenntnisdokumente]
- **Notizen:** [optional: Hinweise, bekannte Fallstricke]
```

## Phasen-Übersicht

| Phase | Titel                                                                   | Typ                   | Spikes / Roadmap  | Status                                      |
| ----- | ----------------------------------------------------------------------- | --------------------- | ----------------- | ------------------------------------------- |
| 1     | Repository-Bootstrap & Tech-Foundations                                 | UMSETZUNG             | –                 | IN ARBEIT (1.1–1.4 erledigt; 1.5–1.8 offen) |
| 2     | Auth + Tenants + Verbund-Tauglichkeit                                   | UMSETZUNG             | –                 | OFFEN                                       |
| 3     | Spikes Wave 1 – Operations-Vorklärungen                                 | ERKUNDUNG             | I, J              | OFFEN                                       |
| 4     | Operations Core + Realtime + Einsatzkraft-PWA                           | UMSETZUNG             | –                 | OFFEN                                       |
| 5     | Spikes Wave 2 – Geo, Frontends, Resilience, Roll-out                    | ERKUNDUNG             | G, H, K, L, M     | OFFEN                                       |
| 6     | Geo + Disponent-/Betreuer-PWAs + Resilience + Retention + Export        | UMSETZUNG             | –                 | OFFEN                                       |
| 7     | Stabilisierung, Roll-out-Vorbereitung, Validierung                      | STABILISIERUNG        | – (Roadmap N/O/P) | OFFEN                                       |
| X     | Verbund-Modus für parallele Mandanten-Großlagen _(spätere Erweiterung)_ | ERKUNDUNG → UMSETZUNG | (eigener Spike)   | OFFEN                                       |

**Spikes-Zuordnung im Detail:**

- **Spike G** (Sperrungs-Override-Technik) → Phase 5, vor Phase-6-Schritt zu `backend/geo`
- **Spike H** (Resilience-Granularität / RTO/RPO) → Phase 5, vor Phase-6-Schritt zu `backend/resilience`
- **Spike I** (Geo-Plausibilitäts-Algorithmus) → Phase 3, vor Phase-4-Schritt zu Einsatzkraft-Bestellpfad
- **Spike J** (Bündelungs-Trigger) → Phase 3, vor Phase-4-Schritt zu Großbestellungs-Modus
- **Spike K** (Hilfe-Knopf-Semantik) → Phase 5, vor Phase-6-Schritt zu Hilfe-Knopf in `frontend-betreuer`
- **Spike L** (Tile-Caching-Strategie Frontend) → Phase 5, vor Phase-6-Schritt zu `frontend-betreuer`-Karten produktiv
- **Spike M** (Fahrzeugbezeichnungs-Schema) → Phase 5, Stakeholder-Rückfrage DPolG vor Phase-7-Roll-out

**Roadmap-Meilensteine (organisatorisch, ohne Code):**

- **N – Plattform-Betreiber-Governance** → Phase 7, vor Produktivstart
- **O – Test-Termin reale Großlage** → Phase 7, Validierungs-Anker
- **P – Schriftliche Onboarding-Unterlagen** → Phase 7, vor erster Mandanten-Freischaltung

## Aktuelle Phasen

### Phase 1: Repository-Bootstrap & Tech-Foundations – Typ: UMSETZUNG

**Ziel:** Produktiv lauffähiges Repository mit aktiven CI-Gates, Backend-Skelett (FastAPI + PostgreSQL + Alembic + Procrastinate), drei Frontend-Workspaces (SvelteKit) plus PWA-Skeletten, lauffähigem Docker-Compose-`dev`-Profil und funktionsfähigem Plattform-Admin-Bootstrap-CLI. Alle in dieser Phase berührten Module bleiben durch Skelett-Existenz `[VORLÄUFIG]`; produktive Funktionalität entsteht in späteren Phasen.

**Abschlusskriterium:** `docker compose --profile dev up` startet alle Container fehlerfrei, `/health` antwortet aus dem Backend, `python -m eb_digital admin create` legt einen Plattform-Admin an, alle drei Frontend-Workspaces bauen mit `pnpm -r build`, GitHub-Actions-Pipeline ist auf `main` als Pflicht-Gate aktiv.

**Reifegrad-Erwartung am Phasenende:**

- Schnittstelle S1 (Admin-Bootstrap-CLI): `[VORLÄUFIG]` → `[BELASTBAR]` durch funktionierende Implementierung (Beförderungsregel 1).
- `backend/auth` (Skelett-Subset für CLI): bleibt `[VORLÄUFIG]` (volle Auth-Logik kommt in Phase 2).
- Stack-Bestandteile (Procrastinate, REST-Grundmodus, Backend-Multi-Architektur, PWA-Service-Worker): bleiben unverändert `[BELASTBAR]`.
- Architektur-Pattern (Modular Monolith + 3 SvelteKit-Frontends): bleibt `[VORLÄUFIG]` (Last-/Funktionstest steht aus).
- Coverage-Mindestwerte aktiv und durchgesetzt; CI-Pipeline ist `[BELASTBAR]` durch ihre Existenz auf `main`.

**Hinweis Sonderregel:** Für Phase 1 gilt die UMSETZUNG-Eingangs-Disziplin (alle berührten Architektur-Bestandteile auf `[BELASTBAR]`) **abgemildert**, weil die Phase die initialen Skelette herstellt, ohne die produktive Tragfähigkeit der Module zu beanspruchen. Berührter _Modul-Schnitt_ ist durch ADR-002, ADR-003, ADR-004 strategisch fixiert; das genügt als Eingangsbedingung.

#### 1.1: Repository- und Workspace-Setup

- **Status:** ERLEDIGT (2026-05-08)
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** keine
- **Freigabepflichtig:** nein (`project-context.md` Abschnitt 7 + Abschnitt 10 sind durch ADR-002 fixiert)
- **Eingangskriterien:** Modus-2-Initialisierung abgeschlossen; `project-context.md` Abschnitt 7 gibt Tooling vor; `project-context.md` Abschnitt 10 gibt Repo-Regeln vor.
- **Zu tun:**
  - **Backend-Workspace:** `pyproject.toml` mit uv-basierter Konfiguration, Python 3.13 als Pin, Dependency-Pin auf die in `project-context.md` Abschnitt 3 verifizierten Versionen.
  - **Frontend-Workspace:** `pnpm-workspace.yaml` mit drei Paketen `apps/frontend-disponent`, `apps/frontend-betreuer`, `apps/frontend-einsatzkraft`. Root-`package.json` mit `pnpm` 11.x als Pin.
  - **EditorConfig:** `.editorconfig` mit LF, UTF-8, 4 Spaces für Python, 2 Spaces für TypeScript/Svelte/YAML/JSON.
  - **`.gitignore`:** Python (`__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `dist`, `*.egg-info`), Node (`node_modules`, `.svelte-kit`, `build`, `.vite`), generelle (`.env*`, `.DS_Store`, IDE-Verzeichnisse).
  - **Pre-Commit-Hooks:** `.pre-commit-config.yaml` mit ruff (lint+format), mypy (auf Backend-Workspace), commitlint (Conventional-Commits), prettier (TypeScript), eslint (TypeScript), svelte-check.
  - **Commit-Lint-Regeln:** `commitlint.config.cjs` mit erlaubten Typen `feat, fix, refactor, docs, test, chore, perf, build, ci, init` (`project-context.md` Abschnitt 7).
  - **Skelett-Verzeichnisstruktur:** `backend/`, `apps/`, `infra/`, `docs/` (existiert), `.github/workflows/`.
- **Akzeptanzkriterien:**
  - `pre-commit run --all-files` läuft auf einer leeren Repo-Datei-Sammlung ohne Fehler.
  - `uv sync` baut Lock-File ohne Konflikte.
  - `pnpm install` baut Lock-File ohne Konflikte.
  - `git commit` mit Test-Conventional-Message wird vom Hook nicht abgelehnt; mit Test-Non-Conventional-Message wird er abgelehnt.
- **Betroffene Module:** Repository-Root (kein produktives Modul); Vorbereitung für alle späteren Module.
- **Reifegrad-Wirkung:** keine direkte (Skelett ohne Modul-Implementation).
- **Artefakte:** `pyproject.toml`, `uv.lock`, `pnpm-workspace.yaml`, `package.json`, `pnpm-lock.yaml`, `.editorconfig`, `.gitignore`, `.pre-commit-config.yaml`, `commitlint.config.cjs`, `LICENSE` (AGPL-3.0), `.env.example`, `backend/eb_digital/__init__.py`.
- **Notizen:** Major-Versions-Pinning ist Pflicht. `pnpm/action-setup` und `astral-sh/setup-uv` werden später in CI auf Patch-Tag oder Commit-Hash gepinnt (Regel-001 aus ADR-002).
- **Verifikation am 2026-05-08 (alle Akzeptanzkriterien erfüllt):**
  1. ✅ `uv sync` lief konfliktfrei (81 Pakete inkl. `fastapi`, `sqlalchemy`, `alembic`, `pydantic`, `httpx`, `argon2-cffi`, `itsdangerous` plus Dev-Tooling). `uv.lock` committet (Commit `0a2257f`).
  2. ✅ `pnpm install` lief konfliktfrei (`@commitlint/cli@20.5.0`, `@commitlint/config-conventional@20.5.0`). `pnpm-lock.yaml` committet (Commit `0a2257f`).
  3. ✅ AGPL-3.0-Volltext byte-genau aus GitHub-Licenses-API in `LICENSE` (Commit `20e2e28`).
  4. ✅ `pre-commit install --hook-type pre-commit --hook-type commit-msg` erfolgreich.
  5. ✅ `pre-commit run --all-files` zweiter Lauf grün; alle Hooks (Hygiene, ruff lint+format, mypy `--strict`, bandit, prettier, commitlint, lokale Frontend-Hooks) passieren bzw. werden korrekt geskipt (kein Frontend-Code in 1.1).
  6. ✅ Conventional Test-Commit (`test: verify commitlint accepts conventional message`, `9eeadcc`) durchgegangen.
  7. ✅ Non-Conventional Test-Commit (`this is a bad non-conventional commit message`) korrekt vom commit-msg-Hook abgelehnt mit `subject-empty` + `type-empty`.
  8. ✅ `.prettierignore` ergänzt (Lock-Files, Build-Caches, kanonisches LICENSE-File ausgeschlossen).
  9. ✅ Bugfix in `.pre-commit-config.yaml`: prettier-Hook-Repo von archiviertem `pre-commit/mirrors-prettier` auf gepflegten `rbubley/mirrors-prettier`-Fork (gleiche v3.8.0).
- **Versions-Verifikation für nachgelagerte Schritte:** itsdangerous (`~=2.2.0`) wird in Schritt 1.6 mit dem ersten produktiven Auth-Code re-verifiziert; uvicorn, pydantic-settings, asyncpg, procrastinate werden in Schritten 1.3/1.4/1.5 nachgepinnt mit erneuter Verifikation.

#### 1.2: CI-Pipeline aktivieren (GitHub Actions)

- **Status:** ERLEDIGT (2026-05-08)
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 1.1
- **Freigabepflichtig:** nein – Konfigurationsdateien für Build-/Deploy-Pipeline sind in `project-context.md` Abschnitt 7 grob vorgegeben, ihre konkrete YAML-Form ist OPERATIV.
- **Eingangskriterien:** Schritt 1.1 abgeschlossen; Tooling-Konfigurationsdateien existieren; pre-commit-Hooks laufen lokal grün.
- **Zu tun:**
  - **`.github/workflows/ci.yml`:** Trigger `push` (alle Branches) und `pull_request` (Hauptbranch). Jobs: `lint-backend` (ruff lint + format check), `typecheck-backend` (mypy --strict), `test-backend` (pytest + Coverage-Mindestwerte aus `project-context.md` Abschnitt 7), `lint-frontend` (eslint + prettier --check), `typecheck-frontend` (svelte-check + tsc --noEmit), `test-frontend` (vitest + Coverage), `build-frontend` (pnpm -r build). Matrix-Build über die drei Frontend-Pakete.
  - **`.github/workflows/security.yml`:** Trigger `schedule` (wöchentlich, So) plus `workflow_dispatch`. Jobs: `dep-audit-backend` (pip-audit, Schwellenwert `high`), `dep-audit-frontend` (pnpm audit, Schwellenwert `high`), `static-security-backend` (bandit), `static-security-frontend` (eslint-plugin-security).
  - **Action-Pinning:** `actions/checkout@v6`, `actions/setup-python@v6`, `actions/setup-node@v6` per Major-Tag. `pnpm/action-setup` und `astral-sh/setup-uv` per Patch-Tag oder Commit-Hash (Immutable-Tag-Trend).
  - **Branch-Protection auf `main`:** alle Pflicht-Gates aus `ci.yml` als Required Status Checks; Force-Push gesperrt; `--no-verify`-Commits durch Server-Side-Hook nicht abdeckbar (manueller Audit-Verzicht akzeptiert).
- **Akzeptanzkriterien:**
  - Push auf einen Test-Branch löst `ci.yml` aus; alle Jobs laufen grün auf einer Skelett-Repo-Basis.
  - PR auf `main` zeigt Required Status Checks; ein Job auf `failed` blockiert den Merge.
  - `security.yml` lässt sich manuell auslösen und liefert ein Audit-Ergebnis (auch wenn leer).
  - Coverage-Mindestwert für Backend auf 80 % konfiguriert; Frontend dito.
- **Betroffene Module:** Repository-Root.
- **Reifegrad-Wirkung:** CI-Pipeline-Existenz ist `[BELASTBAR]`; geht nicht über die in der Reifegrad-Übersicht geführten Bestandteile hinaus.
- **Artefakte:** `.github/workflows/ci.yml`, `.github/workflows/security.yml`, dokumentierte Branch-Protection-Konfiguration in `project-context.md` Abschnitt 10 (sofern Detail-Anpassung nötig).
- **Notizen:** Status-Wechsel `Konzeption` → `Aufbau` ist nicht hier, sondern in Phase 7 vorgesehen. Branch-Protection darf Initialisierungs-Phase aber nicht blockieren – Patrick bleibt bis zum Status-Wechsel direkter-Push-berechtigt (`project-context.md` Abschnitt 10).
- **Verifikation am 2026-05-08 (alle Akzeptanzkriterien erfüllt):**
  1. ✅ Push auf `scp/dreamy-liskov-be0c78` löst `ci.yml` aus, alle Jobs `success` (Backend Lint+Type-Check, Detect-Vorschalt) oder `skipped` (Frontend-Jobs + test-backend, weil `apps/` und `backend/tests/` noch leer; Skip via `needs:`+`if:`-Output-Vergleich aus dem Vorschalt-Job `detect-presence`). Run: https://github.com/Paddel87/EB-Digital/actions/runs/25579380487
  2. ✅ Branch-Protection auf `main` aktiv mit 8 Required Status Checks (alle ci.yml-Jobs inkl. `Detect · Code-Präsenz prüfen`); `enforce_admins: false` (Patrick behält direkten Push laut `project-context.md` Abschnitt 10), `required_pull_request_reviews: null`, `allow_force_pushes: false`, `allow_deletions: false`. Geskipte Jobs zählen als erfolgreich für Required Checks.
  3. ✅ `gh workflow run security.yml` manuell ausgelöst, alle drei Audits (`pip-audit`, `pnpm audit`, `bandit`) `success`. Run: https://github.com/Paddel87/EB-Digital/actions/runs/25579458539
  4. ✅ Coverage-Mindestwert Backend 80 % via `--cov-fail-under=80` in `pyproject.toml`; Frontend-Coverage-Mindestwert wird in Schritt 1.7 mit `vitest.config.ts` pro Frontend-Paket aktiviert.
- **Während 1.2 behobene Reibungen** (alle dokumentiert im Logbuch-Eintrag des Sessionendes):
  - **`hashFiles()` auf Job-Ebene nicht erlaubt** (actionlint-Befund). Erster Fix-Versuch (`f94ee93`) führte zu „workflow file issue"-Validierungsfehler ohne Job-Start. Lösung: Vorschalt-Job `detect-presence` mit Step-Skript-Check und Outputs `has_frontend`/`has_backend_tests`; Frontend- und `test-backend`-Jobs nutzen `needs:`+`if:` mit Output-Vergleich (Commit `632cead`).
  - **pnpm-Multi-Version-Konflikt** (`pnpm/action-setup@v4.0.0` + `version`-Arg + `packageManager` in `package.json` = "Multiple versions of pnpm specified"). Lösung: `version`-Arg aus allen `pnpm/action-setup`-Steps entfernt; `packageManager: pnpm@11.0.0` ist Single Source of Truth. `PNPM_VERSION`-env-Variable in beiden Workflows entfernt.
- **Beobachtung zur Aktion-Versionierung (Folge-Entscheidung außerhalb 1.2):** Security-Run-Annotation flaggt **Node.js-20-Deprecation** für `astral-sh/setup-uv@v5.0.0` und `pnpm/action-setup@v4.0.0` ab 2026-06-02. In ~3 Wochen werden diese Action-Pins funktional eingeschränkt. Major-Update auf `astral-sh/setup-uv@v8` und `pnpm/action-setup@v6` ist freigabepflichtig (CLAUDE.md Abschnitt 4 Punkt 3, Major-Vorbehalt) – als separater Mini-ADR vor 2026-06-02 zu erledigen.

#### 1.3: Backend-Skelett (FastAPI + Settings + Logging)

- **Status:** ERLEDIGT (2026-05-09)
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 1.1, 1.2
- **Freigabepflichtig:** nein
- **Eingangskriterien:** uv-Workspace existiert; `project-context.md` Abschnitt 6 (Datenschutz) gibt Logging-Disziplin vor.
- **Zu tun:**
  - **Anwendungs-Einstiegspunkt:** `backend/eb_digital/__main__.py` mit Argparse-Subcommand-Skelett (`admin`, `serve`, `worker`).
  - **FastAPI-App:** `backend/eb_digital/app.py` mit Settings via Pydantic-Settings (ENV-basiert, kein Default-Geheimnis), Lifespan-Hook, Mount-Punkt `/api`, Healthcheck-Endpoint `/health` (200 OK, JSON `{status: "ok", version: "0.1.0"}`).
  - **Strukturiertes JSON-Logging:** `backend/eb_digital/logging.py` mit stdlib-`logging` plus JSON-Formatter; zentraler Logger-Wrapper mit Redaction-Liste für Felder `password`, `password_hash`, `access_code`, `access_code_hash`, `email` (im Anonymous-Kontext), `coordinate_lat`, `coordinate_lng` (durch Tile-Identifier-Hash zu ersetzen).
  - **Konfigurations-Schema:** `backend/eb_digital/settings.py` mit Feldern `database_url`, `valkey_url`, `secret_key`, `session_cookie_name`, `log_level` (default `INFO` in prod, `DEBUG` lokal), `tile_proxy_base`, `tomtom_api_key`, `maptiler_api_key`. Keine Default-Werte für Secrets.
- **Akzeptanzkriterien:**
  - `uv run python -m eb_digital serve` startet einen Uvicorn-Server auf Port 8000.
  - `curl http://localhost:8000/health` liefert `{status: "ok", version: "0.1.0"}`.
  - Log-Output ist valides JSON pro Zeile.
  - Versuch eines Logger-Aufrufs mit `password=…` im `extra` redacted das Feld zu `<redacted>`.
  - mypy --strict läuft fehlerfrei.
- **Betroffene Module:** Backend-Skelett (kein einzelnes Modul der Modul-Karte).
- **Reifegrad-Wirkung:** keine direkten Beförderungen.
- **Artefakte:** `backend/eb_digital/{__main__.py, app.py, logging.py, settings.py}`, Tests unter `backend/tests/`.
- **Notizen:** Sicherheits-Constraint „keine PII in Logs" (`project-context.md` Abschnitt 6) wird hier zentral umgesetzt – spätere Module nutzen den Wrapper, statt eigene Logger.
- **Versions-Verifikation für Schritt 1.3** (Modus-2-Schritt 2a, Sessionstart 2026-05-09):
  - **uvicorn[standard]~=0.46.0** — `Verifiziert: 2026-05-09` (PyPI-Stand: 0.46.0 vom 2026-04-23, normales Minor ohne Breaking Change; `[standard]` bringt uvloop/httptools/websockets/watchfiles für Production-Performance auf Linux).
  - **pydantic-settings~=2.13.1** — `Verifiziert: 2026-05-09` (2.14 bewusst zurückgehalten — 2.14.1 war am 2026-05-08 als Hotfix für 2.14.0 erschienen, „Stabilität vor Aktualität"-Linie analog zu Postgres 17 / mypy 1.20). Kompatibel mit `pydantic~=2.13.0` (Constraint im Paket: `pydantic>=2.7.0`).
  - In `project-context.md` Abschnitt 3 Sub-Block „Backend Frameworks und Bibliotheken" mit Stempel ergänzt.
- **Verifikation am 2026-05-09 (alle Akzeptanzkriterien erfüllt):**
  1. ✅ `uv run python -m eb_digital serve --host 127.0.0.1 --port 18001` startet Uvicorn (Direct-`.venv/bin/python`-Aufruf in Smoke-Test wegen einmaliger `_editable_impl_*.pth`-Reibung — siehe Logbuch). Standard-Bind ist Port 8000.
  2. ✅ `curl http://127.0.0.1:18001/health` liefert `{"status":"ok","version":"0.1.0"}` (Inhalt + `application/json`-Content-Type).
  3. ✅ Log-Output validiert: alle 6 Stdout-Zeilen aus dem Smoke-Test (`uvicorn.error`, `uvicorn.access`, `eb_digital.app` `application_startup`) sind valides JSON pro Zeile (per `json.loads` geparst). `uvicorn.run(log_config=None)` plus pre-startup `configure_logging`-Aufruf in `_cmd_serve` bewirkt, dass uvicorn-Loggers per Propagation an Root + JsonLogFormatter gehen.
  4. ✅ Logger-Redaction für 9 sensitive Felder (`password`, `password_hash`, `access_code`, `access_code_hash`, `secret_key`, `tomtom_api_key`, `maptiler_api_key`, `email`, `coordinate_lat`, `coordinate_lng`) inklusive rekursiver Redaction durch verschachtelte Dicts/Lists. 14 Tests in `test_logging.py` decken das ab.
  5. ✅ `mypy --strict` läuft fehlerfrei auf 5 source files (1 lokale `# type: ignore[call-arg]`-Suppression mit Begründungs-Kommentar in `settings.py:get_settings`, weil pydantic-settings die required-Felder zur Laufzeit aus ENV nachlädt — nicht für mypy sichtbar).
  6. ✅ pytest 26 Tests grün, Coverage **94 % gesamt** (settings.py, app.py, logging.py jeweils 100 %; `__main__.py` 79 % — Server-Start nicht im Unit-Test). Schwelle 80 % deutlich überschritten.
  7. ✅ pre-commit `run --all-files` grün auf allen Hooks (ruff lint+format, mypy --strict, bandit, prettier, actionlint, commitlint).
- **Reibungen während 1.3** (alle dokumentiert im Logbuch-Sessionende-Eintrag):
  - **uvicorn-Logger umgehen Custom-Formatter standardmäßig:** Uvicorn richtet seine Logger (`uvicorn`, `uvicorn.access`, `uvicorn.error`) per Default mit eigener `LOGGING_CONFIG` ein, die unsere Root-Konfiguration überschreibt. Lösung: `_cmd_serve` ruft `configure_logging` vor `uvicorn.run` auf und übergibt `log_config=None` — dann propagieren alle uvicorn-Logger an den Root mit unserem `JsonLogFormatter`. Test im Smoke-Lauf bestätigt: 6/6 Zeilen JSON.
  - **Einmalige `_editable_impl_*.pth`-Reibung:** Nach manuellem Re-Schreiben des `.pth`-Files schien Python den Eintrag nicht mehr zu prozessieren. `uv sync --reinstall-package eb-digital` hat das geheilt; danach funktionierten sowohl direkter `.venv/bin/python` als auch `uv run`. Kein dauerhaftes Problem, kein ADR nötig.
  - **mypy-`# type: ignore[call-arg]` in `get_settings`:** pydantic-settings deklariert required Felder, deren Werte aber zur Laufzeit aus ENV kommen — mypy sieht das nicht. Engster Scope (Zeilen-Suppression mit Begründungs-Kommentar). Konsistent mit CLAUDE.md Abschnitt 6.
  - **`# noqa: ANN401` in `_redact`:** typing.Any ist für Log-Extras die korrekte Wahl, weil sie inhaltlich unbeschränkt sind (Caller bestimmt). Suppression mit Begründungs-Kommentar.
  - **`# noqa: S104` für `0.0.0.0`-Bind-Default:** Bewusster Default für Container-internes Bind hinter Caddy-Reverse-Proxy (`project-context.md` Abschnitt 8). Begründungs-Kommentar in derselben/oberhalb der Zeile.

#### 1.4: Datenbank + Alembic + ORM-Konventionen

- **Status:** ERLEDIGT (2026-05-09)
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 1.3
- **Freigabepflichtig:** nein
- **Eingangskriterien:** Backend-Skelett mit Settings-Modul existiert; Stack-Pinning aus `project-context.md` Abschnitt 3.
- **Zu tun:**
  - **PostgreSQL-Container** im Compose-`dev`-Profil (Image `postgres:17.9` mit gepinntem Digest, Volume `eb-digital-pg`, Healthcheck via `pg_isready`).
  - **SQLAlchemy 2.0-Setup:** `backend/eb_digital/db/__init__.py` mit Async-Engine, Session-Factory, `DeclarativeBase` mit Naming-Convention (PEP-Style: snake_case Tabellennamen, ID-Spalten als `id` UUID-Pkv4 oder Integer-Auto, Audit-Spalten `created_at`, `updated_at` als UTC).
  - **Alembic-Init:** `alembic.ini` plus `migrations/` mit Async-Template; erste leere Migration als Baseline.
  - **Code-Bezeichner-Konvention** wie in `architecture.md` Abschnitt 0 niedergelegt; Pflicht für alle ORM-Modelle.
  - **Ein Test-ORM-Modell** (z. B. `_HealthMarker` als Sentinel) zur Validierung des Setups.
- **Akzeptanzkriterien:**
  - `alembic upgrade head` läuft ohne Fehler gegen leere Datenbank.
  - `alembic revision --autogenerate -m "test"` erkennt eine triviale ORM-Änderung und erzeugt ein Skript.
  - Async-Session-Lifecycle in Tests funktioniert (Setup/Teardown ohne Connection-Leaks).
- **Betroffene Module:** Backend-Datenbank-Layer (modul-übergreifend).
- **Reifegrad-Wirkung:** keine direkten Beförderungen; Datenmodell-Grobschnitt bleibt `[VORLÄUFIG]`.
- **Artefakte:** `backend/eb_digital/db/`, `migrations/`, `alembic.ini`, Compose-Snippet für PostgreSQL.
- **Notizen:** Mandanten-spezifische Tabellen werden in Phase 2 angelegt – hier nur die Plumbing-Schicht.
- **Versions-Verifikation für Schritt 1.4** (Modus-2-Schritt 2a, Sessionstart 2026-05-09):
  - **asyncpg 0.31.0** — `Verifiziert: 2026-05-09` (PyPI-Stand: 0.31.0 vom 2025-11-24, ~5,5 Monate alt; PostgreSQL-17-Support seit 0.30.0; einziger Breaking Change in 0.31.0 ist Drop von Python 3.8, irrelevant für unseren Stack 3.13). Patrick wählte **Option A** (`asyncpg~=0.31.0`).
  - In `project-context.md` Abschnitt 3 Sub-Block "Backend Frameworks und Bibliotheken" mit Stempel ergänzt.
- **Verifikation am 2026-05-09 (alle Akzeptanzkriterien erfüllt):**
  1. ✅ `docker compose --profile dev up -d` startet `postgres:17.9@sha256:347bc4e6…` (Digest am 2026-05-09 aus Docker Hub Registry geholt), Container `healthy` nach 11 Sekunden.
  2. ✅ `alembic upgrade head` läuft fehlerfrei zweistufig: `(empty) → 0bf0aa5ccee1 baseline → 660e1a12a41a add health marker`.
  3. ✅ `alembic revision --autogenerate -m "add health marker"` erkennt das `HealthMarker`-Modell und erzeugt eine Migration mit korrekt benannten Constraints (`pk_health_marker`, `uq_health_marker_label`) gemäß Naming-Convention.
  4. ✅ `alembic check` nach Anwendung der generierten Migration: `No new upgrade operations detected` (Idempotenz bestätigt — ORM und Migration in Sync).
  5. ✅ Async-Session-Lifecycle gegen reale Postgres: Insert/Select/Delete eines `HealthMarker` mit timezone-aware Audit-Timestamps, danach `engine.dispose()` mit Pool-Status `Checked out connections: 0` (keine Connection-Leaks).
  6. ✅ `uv run pytest` 45 Tests grün (Coverage **95 %**; `db/__init__.py` und `db/models.py` je 100 %; Schwelle 80 % weit überschritten).
  7. ✅ `uv run ruff check backend` + `ruff format --check backend` + `mypy --strict` (7 source files) alle grün.
  8. ✅ `uv run pre-commit run --all-files` grün auf allen Hooks.
- **Reibungen während 1.4** (alle dokumentiert im Logbuch-Sessionende-Eintrag):
  - **`alembic post_write_hooks` mit `console_scripts`-Type fand `ruff` nicht** — uv installiert ruff zwar in `.venv/bin/ruff`, aber nicht als `console_scripts`-Entry-Point. Lösung: Hook-Type auf `exec` umgestellt mit `executable = ruff`. Zusätzlich `ruff check --fix` als zweiter Hook ergänzt, damit auto-generierte Migrationen direkt lint-konform sind.
  - **Erneute `_editable_impl_*.pth`-Reibung** — Direkter Smoke-Test (`uv run python /tmp/script.py`) konnte das `eb_digital`-Modul nicht importieren, obwohl `pytest` (mit eigenem Discovery) es findet. `uv sync --reinstall-package eb-digital` half diesmal **nicht**; **`rm -rf .venv && uv sync`** war die wirksame Heilung. Phänomen identisch zu Schritt 1.3 — wenn es ein drittes Mal auftritt, lohnt ein Blocker-Eintrag mit Reproduktion.

#### 1.5: Procrastinate-Setup + Worker

- **Status:** OFFEN
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 1.4
- **Freigabepflichtig:** nein
- **Eingangskriterien:** PostgreSQL läuft; SQLAlchemy-Engine konfiguriert.
- **Zu tun:**
  - **Procrastinate-DB-Schema:** Eigene Migration nach Procrastinate-Doku (`procrastinate_jobs`, `procrastinate_periodic_defers`, …).
  - **Worker-Container** im Compose-`dev`-Profil (eigener Container `eb-worker` mit Subcommand `python -m eb_digital worker`).
  - **Test-Job:** `backend/eb_digital/jobs/test_job.py` mit einem trivialen Async-Task (`@app.task(name="ping")` → liefert „pong" in Worker-Log).
  - **Job-Modul-Konvention:** Jedes Backend-Modul mit Hintergrund-Jobs hat ein Submodul `jobs/` mit registrierten Tasks.
- **Akzeptanzkriterien:**
  - `docker compose exec backend python -m eb_digital admin create` (in 1.6 verfügbar) bzw. ein Skript-Aufruf kann den Test-Job einreihen; der Worker führt ihn aus und schreibt ein Log mit „pong".
  - Worker stoppt sauber bei `SIGTERM`.
- **Betroffene Module:** Backend-Job-Infrastruktur.
- **Reifegrad-Wirkung:** Procrastinate-Job-Engine ist bereits `[BELASTBAR]` (Stack-fix); diese Phase liefert die Compose-Realisierung.
- **Artefakte:** Migration für Procrastinate-Schema, `backend/eb_digital/jobs/`, Compose-Snippet `eb-worker`.
- **Notizen:** Procrastinate-Job-State liegt in PostgreSQL und ist Teil der Standard-Backups – konsistent mit Vision „nahtlose Fortsetzung nach Crash".

#### 1.6: backend/auth Admin-Bootstrap-CLI

- **Status:** OFFEN
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 1.4 (DB), 1.3 (Settings)
- **Freigabepflichtig:** nein – ADR-004 fixiert das Verfahren strategisch; konkrete Implementierung ist OPERATIV.
- **Eingangskriterien:** PostgreSQL läuft; Backend-Skelett startet; Modul-Schnitt `backend/auth` aus `architecture.md` Abschnitt 3.
- **Zu tun:**
  - **Datenmodell-Skelett** (vollständige Auth-Datenmodelle kommen in Phase 2): `platform_admin`-Tabelle mit `id`, `username` (unique), `password_hash`, `created_at`, `created_via` (`'bootstrap_cli' | 'admin_cli'`).
  - **CLI-Befehl** `python -m eb_digital admin create`:
    - Argument `--username` (positional, required).
    - Passwort interaktiv via `getpass.getpass()`, ohne Echo, **kein** `--password`-CLI-Argument.
    - Argon2id-Hashing mit Library-Default-Parametern (`argon2-cffi`).
    - Insert in `platform_admin`-Tabelle plus Audit-Eintrag (Tabellen-Definition in Phase 2 final, hier zunächst minimal).
    - Idempotenz-Hinweis: Aufruf mit existierendem Username liefert Fehlermeldung „Username existiert bereits", kein silent overwrite.
  - **Logging:** Bootstrap-Erfolg als `INFO`-Zeile mit `{username, created_via, at}`. **Kein** Klartext-Passwort, **kein** Hash, **kein** Salt im Log.
- **Akzeptanzkriterien:**
  - `docker compose exec backend python -m eb_digital admin create --username patrick` fragt interaktiv das Passwort ab und legt einen Eintrag in `platform_admin` an.
  - Erneuter Aufruf mit demselben Username scheitert mit Exit-Code != 0 und Fehlermeldung.
  - DB-Eintrag enthält `password_hash` mit Argon2id-Format-Marker (`$argon2id$…`).
  - Coverage `backend/auth` für die Bootstrap-Funktionalität ≥ 95 % (Anforderung aus `project-context.md` Abschnitt 7 für Auth-Modul).
- **Betroffene Module:** `backend/auth` (Subset).
- **Reifegrad-Wirkung:** Schnittstelle S1 (Admin-Bootstrap-CLI) wird durch funktionierende Implementierung von `[VORLÄUFIG]` auf `[BELASTBAR]` befördert (Beförderungsregel 1). Reifegrad-Wechsel wird in `architecture.md` Abschnitt 9 mit Datum nachgetragen und im Logbuch als `[REIFEGRAD-WECHSEL]` festgehalten.
- **Artefakte:** Migration mit `platform_admin`-Tabelle, `backend/eb_digital/auth/cli.py`, Tests.
- **Notizen:** Volle Auth-Logik (Login, Sessions, Rate-Limit) folgt in Phase 2. Hier nur Bootstrap.

#### 1.7: Frontend-Workspaces + PWA-Skelett

- **Status:** OFFEN
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 1.1
- **Freigabepflichtig:** nein
- **Eingangskriterien:** pnpm-Workspace existiert.
- **Zu tun:**
  - **Drei SvelteKit-Projekte** in `apps/frontend-disponent`, `apps/frontend-betreuer`, `apps/frontend-einsatzkraft` mit Svelte 5 + SvelteKit 2 + Vite 8 + TypeScript 6.
  - **Pro Frontend** eine `package.json` mit gepinnten Dependencies (`project-context.md` Abschnitt 3), `svelte.config.js`, `vite.config.ts`, `tsconfig.json` mit `strict + noUncheckedIndexedAccess + noImplicitReturns`.
  - **Service-Worker-Skelett** für Betreuer und Einsatzkraft (`vite-plugin-pwa` aktiviert, Workbox-Konfiguration leer plus „network-first" für API-Calls). Disponent-Frontend ohne PWA-Aktivierung in Phase 1 – wird in Phase 6 evaluiert.
  - **Health-Page** pro Frontend (`/health`-Route, zeigt App-Version, Build-Zeit), als Smoke-Indikator.
  - **Eslint + Prettier + svelte-check** Konfigurationen pro Paket plus shared Root-Config.
- **Akzeptanzkriterien:**
  - `pnpm -r build` baut alle drei Pakete erfolgreich.
  - `pnpm --filter frontend-disponent dev` startet einen Dev-Server.
  - `pnpm -r test` läuft (auch wenn keine echten Tests existieren – Setup OK).
  - Service-Worker registriert sich in Betreuer- und Einsatzkraft-Frontends; Disponent-Frontend ohne SW.
- **Betroffene Module:** `frontend-disponent`, `frontend-betreuer`, `frontend-einsatzkraft` (Skelette).
- **Reifegrad-Wirkung:** keine direkten Beförderungen; Frontends bleiben `[VORLÄUFIG]`.
- **Artefakte:** `apps/frontend-disponent/`, `apps/frontend-betreuer/`, `apps/frontend-einsatzkraft/`.
- **Notizen:** MapLibre GL JS und Workbox-Tile-Strategien werden in Phase 6 produktiv konfiguriert (Spike L als Vorlauf).

#### 1.8: Infrastruktur (Caddy + nginx) + Docker Compose dev-Profil

- **Status:** OFFEN
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 1.3, 1.4, 1.5, 1.6, 1.7
- **Freigabepflichtig:** nein – Compose-Profil-Wechsel ist Build-/Deploy-Pipeline (`project-context.md` Abschnitt 8) und wird durch ADR-002 fixiert.
- **Eingangskriterien:** alle vorherigen Skelette laufen einzeln.
- **Zu tun:**
  - **`infra/reverse-proxy/Caddyfile`:** lokale Domain `eb.local` (oder `localhost`), Routing `/api/*` → Backend `:8000`, `/disponent/*` → Disponent-Frontend `:5173`, `/betreuer/*` → Betreuer-Frontend `:5174`, `/einsatzkraft/*` → Einsatzkraft-Frontend `:5175`. TLS mit Caddy-internem CA für `dev`.
  - **`infra/tile-proxy/nginx.conf`:** Cache-Pfad `/var/cache/nginx/tiles`, `proxy_cache_path` mit 7 Tagen TTL für `*.pbf`-Tiles, statisches Stub-Routing zu `https://api.maptiler.com/maps/streets-v2/{z}/{x}/{y}.pbf?key=…` (Key aus ENV). Routing-Endpunkt zu TomTom als zweiter Block. **Keine echten API-Calls in Phase 1** – Stub-Antwort `204 No Content` für nicht-cached Tiles, konfigurierbar.
  - **`docker-compose.yml`** mit Profilen `dev`, `staging`, `production`. `dev`-Profil enthält: `backend` (Uvicorn), `worker` (Procrastinate), `db` (PostgreSQL), `cache` (Valkey, gepinnt 8.1.7), `tile-proxy` (nginx), `reverse-proxy` (Caddy), `frontend-*` (drei Vite-Dev-Server, optional). Healthchecks plus dependency-graph (`depends_on: condition: service_healthy`).
  - **Smoke-Test-Skript** `scripts/dev-smoke.sh`: startet Compose, wartet auf Healthchecks, ruft `/health` über Caddy-Proxy ab, beendet Compose.
- **Akzeptanzkriterien:**
  - `docker compose --profile dev up -d` bringt alle Container in Status `healthy`.
  - `curl -k https://eb.local/api/health` liefert `200` mit erwartetem JSON.
  - Tile-Proxy antwortet auf Anfrage `GET /tiles/12/3456/4321.pbf` mit `204` (oder echtem Tile, falls API-Key gesetzt).
  - `scripts/dev-smoke.sh` läuft grün durch.
  - Kein Container hat Volumes ohne Backup-Marker (Vorbereitung Phase 6 Resilience).
- **Betroffene Module:** `infra/reverse-proxy`, `infra/tile-proxy` (Skelette).
- **Reifegrad-Wirkung:** Smoke-Test-Existenz reicht für Beförderung der Infra-Module von `[VORLÄUFIG]` → `[BELASTBAR]` (Beförderungsregel 1) **noch nicht** – produktive Konfiguration (TLS, Production-Profil, Cache-Headers) folgt in Phase 7. Bleiben `[VORLÄUFIG]`.
- **Artefakte:** `infra/reverse-proxy/Caddyfile`, `infra/tile-proxy/nginx.conf`, `docker-compose.yml`, `scripts/dev-smoke.sh`.
- **Notizen:** API-Keys (MapTiler, TomTom) bleiben in `.env`-Datei lokal, niemals committed (`.gitignore` enthält `.env*`).

---

### Phase 2: Auth + Tenants + Verbund-Tauglichkeit (I1/I2) – Typ: UMSETZUNG

**Ziel:** Vollständige Auth-Schicht (Login, Sessions, Rate-Limit, anonyme einsatzgebundene Sessions, AccessCode), Mandanten-Onboarding (Self-Service-Antrag plus Plattform-Admin-Freischaltung), Operation↔Mandant-Verknüpfung über `operation_tenant_participation` (Invariante I1) plus abstrakter Berechtigungs-Filter (Invariante I2). Disponenten-Dashboard-Skelett mit Login-Flow.

**Abschlusskriterium:** Plattform-Admin freischaltet einen Mandanten; Mandant-Disponent loggt ein; Mandant-Disponent eröffnet eine leere Operation, die in `operation_tenant_participation` mit `role='owner'` verbunden ist; einsatzgebundene URL plus optionaler AccessCode generieren eine anonyme Session, deren Token validiert wird. Coverage `backend/auth` ≥ 95 %, `backend/auth_anonymous` ≥ 95 %, `backend/tenants` ≥ 80 %, externe Security-Review (folgt in Phase 7) ist als Issue/Auftrag verschriftlicht.

**Reifegrad-Erwartung am Phasenende:** `backend/auth`, `backend/auth_anonymous`, `backend/tenants` zu `[BELASTBAR]` durch Implementierung; Schnittstellen S2 (Anonymous Session API), S8 (Authentifizierte REST-API für Login/Tenants), S10 (Tenant Participation Lookup) zu `[BELASTBAR]`. Invarianten I1, I2 zu `[BELASTBAR]` durch funktionierende Implementierung.

**Schritte (gröber):**

- **2.1** Datenmodell: `tenant`, `dispatcher`, `carer`, `operation` (ohne Tenant-FK!), `operation_tenant_participation`, `operation_audit_log` (Strukturskelett). Alembic-Migration.
- **2.2** `backend/auth`: Login-Endpoint, Session-Cookie (Starlette-SessionMiddleware), Argon2id-Hash-Vergleich, Rate-Limit (`slowapi` oder ähnliches; OPERATIVE Bibliotheks-Wahl per kleinem ADR vor Schritt-Beginn).
- **2.3** `backend/auth_anonymous`: einsatzgebundene URL-Token (`itsdangerous`), AccessCode-Validierung (Konstantzeit-Vergleich + Hash-Speicherung gemäß Regel-006), Session-Lifecycle anonym.
- **2.4** `backend/tenants`: Self-Service-Antrag, Plattform-Admin-Freischaltung-Endpoint, Mandanten-CRUD, abstrakter Teilnahme-Filter (Invariante I2 + Regel-014).
- **2.5** `frontend-disponent`: Login-Flow + Dashboard-Skelett (zeigt Mandanten-Übersicht und „leere Operations" der eigenen Teilnahme).
- **2.6** `frontend-einsatzkraft`: AccessCode-Eingabe-UI (anonyme Session mit Code-Validierung).
- **2.7** Tests + Coverage; externe Security-Review als Issue erfasst (Phase 7).

---

### Phase 3: Spikes Wave 1 – Operations-Vorklärungen – Typ: ERKUNDUNG

**Ziel:** Klärung der zwei Architektur-Lücken, die `backend/operations` blockieren würden: Geo-Plausibilitäts-Algorithmus (Spike I) und Bündelungs-Trigger (Spike J). Ergebnisse als ADRs plus Architektur-Updates dokumentiert; betroffene `[OFFEN]`-Bereiche in `architecture.md` Abschnitt 9 zu `[VORLÄUFIG]` befördert.

**Abschlusskriterium:** ADR pro Spike mit Tag `[ERKENNTNIS]` plus Themen-Tag, fixierte Entscheidung; `architecture.md` Abschnitt 6 (NFR-/Algorithmus-Bereich) und Abschnitt 9 entsprechend aktualisiert; keine Implementation-Änderungen am Produktivcode.

**Reifegrad-Erwartung am Phasenende:** `[OFFEN]`-Bereich Spike I → `[VORLÄUFIG]`; `[OFFEN]`-Bereich Spike J → `[VORLÄUFIG]`.

**Schritte:**

- **3.1** Spike I (Geo-Plausibilitäts-Algorithmus) – Schritt-Art Spike, Zeitbox 4 h. Klärt Distanz-Metrik (Hülle/Mittelpunkt), GPS-Ungenauigkeit, Text-Standort-Behandlung, mandanten-konfigurierbarer Schwellenwert (Default 5 km). Ergebnis: ADR `[ERKENNTNIS] [PERFORMANCE]` plus Pseudocode plus Test-Datensatz.
- **3.2** Spike J (Bündelungs-Trigger) – Schritt-Art Vergleichsstudie, Zeitbox 4 h. Klärt Auslöser (System-Heuristik vs. Disponenten-manuell vs. Versorgungs-Transporter-Crew), UI-Auswirkung, Aggregat-Wirkung auf `bundling_count` (ADR-006). Ergebnis: ADR `[ERKENNTNIS] [MODUL]` mit Auslöser-Wahl Phase 1 (Vermutung: manuell durch Disponent).

---

### Phase 4: Operations Core + Realtime + Einsatzkraft-PWA – Typ: UMSETZUNG

**Ziel:** Operations-Hauptpfad (Operation eröffnen, Bestellung anlegen, Auftrag zuweisen, stornieren, bündeln), Audit-Log (ADR-008), Realtime-Hub (WebSocket), Einsatzkraft-Bestell-PWA (F2 Hard-Path aus `architecture.md` Abschnitt 5).

**Abschlusskriterium:** End-to-End-Test: Disponent eröffnet Operation → Einsatzkraft-PWA zeigt URL+Code → Einsatzkraft öffnet anonyme Session → bestellt einen Artikel → Backend prüft Geo-Plausibilität (Algorithmus aus Spike I) → Bestellung in Disponenten-UI sichtbar → Disponent weist Fahrzeug zu (I3) → Audit-Log-Eintrag → WebSocket aktualisiert Live-Standort.

**Reifegrad-Erwartung am Phasenende:** `backend/operations`, `backend/fleet`, `backend/catalog`, `backend/realtime`, `frontend-einsatzkraft` zu `[BELASTBAR]`. Schnittstellen S3 (Operations Event Bus), S4 (Vehicle Assignment), S9 (WebSocket-Topologie) zu `[BELASTBAR]`. Invariante I3 zu `[BELASTBAR]`.

**Schritte (gröber):**

- **4.1** `backend/catalog`: Basis-Artikelkatalog plus mandantenspezifische Erweiterung.
- **4.2** `backend/fleet`: Fahrzeuge, Beladung, Versorgungs-Transporter-Modi.
- **4.3** `backend/operations`: Operations + Orders + Vehicle-Assignment (über Operation-Kontext, I3) + Stornierung + Bündelung + Audit-Log (`operation_audit_log`).
- **4.4** `backend/realtime`: WebSocket-Hub, Pub/Sub via Valkey, Live-Standorte, Auftragsstatus, Disponent↔Betreuer-Chat-Skelett, Hilfe-Knopf-Routing.
- **4.5** `frontend-einsatzkraft`: anonyme Bestell-PWA (F2 Hard-Path), AccessCode-Eingabe, Bestell-Form, Status-Anzeige.
- **4.6** Tests + Coverage (Operations ≥ 90 %).

---

### Phase 5: Spikes Wave 2 – Geo, Frontends, Resilience, Roll-out – Typ: ERKUNDUNG

**Ziel:** Klärung der fünf verbleibenden Architektur-Lücken vor Phase 6 + 7: Sperrungs-Override (G), Resilience (H), Hilfe-Knopf-Semantik (K), Tile-Caching-Strategie Frontend (L), Fahrzeugbezeichnungs-Schema (M).

**Abschlusskriterium:** ADR pro Spike, alle `[OFFEN]`-Bereiche Spike G/H/K/L/M zu `[VORLÄUFIG]` befördert; Stakeholder-Rückfrage DPolG zu Spike M dokumentiert.

**Reifegrad-Erwartung am Phasenende:** alle `[OFFEN]`-Bereiche Spike G/H/K/L/M zu `[VORLÄUFIG]`.

**Schritte:**

- **5.1** Spike G (Sperrungs-Override-Technik) – Schritt-Art Spike, Zeitbox 4–8 h. Klärt TomTom-Custom-Areas vs. Route-Bias vs. Penalty-Map, Datenbedarf bei Override-Pflege, API-Budget-Folgen. Ergebnis: ADR `[ERKENNTNIS] [MODUL] [PERFORMANCE]` mit Technikwahl.
- **5.2** Spike H (Resilience-Granularität) – Schritt-Art Vergleichsstudie + Prototyp, Zeitbox 6–8 h. Klärt Backup-Strategie (logical/physical, RTO/RPO), Recovery-Reihenfolge (Procrastinate-Job-State + Detail-Daten), Verhalten bei Crash mitten im Auftragsstatus-Wechsel, Erfahrung Reconnect WebSocket nach State-Reload. Ergebnis: ADR `[ERKENNTNIS] [MODUL] [DEPLOYMENT]` mit Backup-Frequenz, Recovery-Reihenfolge, getesteter RTO.
- **5.3** Spike K (Hilfe-Knopf-Semantik) – Schritt-Art Spike, Zeitbox 2–3 h. Klärt Pflichtfeld-Beschreibung, Disponenten-Eskalations-Sichtbarkeit, Quittungspfad zum Betreuer, kein PII-Speicher. Ergebnis: UX-Konzept + Datenmodell-Skizze.
- **5.4** Spike L (Tile-Caching-Strategie Frontend) – Schritt-Art Prototyp, Zeitbox 6–8 h. Klärt Workbox-Strategie für Tile-Cache, Pre-Cache des Operations-Raums beim Schichtbeginn, Tile-Lebensdauer (≥ 7 Tage konsistent mit nginx-Cache), Speicher-Quota mobiler Browser. Ergebnis: Prototyp + ADR `[ERKENNTNIS] [MODUL] [PERFORMANCE]`.
- **5.5** Spike M (Fahrzeugbezeichnungs-Schema) – Schritt-Art Vergleichsstudie + Stakeholder-Rückfrage DPolG, Zeitbox 2 h netto. Klärt Naming-Konvention (z. B. „EB-Bremen-01" oder verbandseigene Funkrufnamen), Eindeutigkeit pro Mandant vs. global, Längen-Constraints. Ergebnis: ADR `[ERKENNTNIS] [DATENMODELL]` „Fahrzeug-Naming".

---

### Phase 6: Geo + Disponent-/Betreuer-PWAs + Resilience + Retention + Export – Typ: UMSETZUNG

**Ziel:** Produktive Karten-/Routing-Integration (`backend/geo`), produktive Disponenten- und Betreuer-Frontends inklusive Multi-Disponenten-UX-Schutz (Confirmation-Dialog, Regel-012), Hilfe-Knopf, Offline-Tile-Cache; Resilience-Stack (Backup/Recovery), 30-Tage-Anonymisierung mit Aggregat-Schreibung beim Operation-Ende (ADR-006), DSGVO-Datenexport via Procrastinate-Job-Tripel (ADR-007).

**Abschlusskriterium:** End-to-End: Operation-Ende → Aggregat geschrieben (Regel-008) → Anonymisierungs-Job 30 Tage später entkoppelt → Datenexport-Anforderung liefert ZIP-Download. Disponenten-UI mit Multi-Disponenten-Bestätigungs-Dialog (Regel-012). Betreuer-Mobile-PWA mit Offline-Tile-Cache (Spike L) und Hilfe-Knopf (Spike K). Backup-Recovery-Test bestanden (Spike H, RTO im definierten Bereich).

**Reifegrad-Erwartung am Phasenende:** `backend/geo`, `backend/resilience`, `backend/retention`, `backend/export`, `frontend-disponent`, `frontend-betreuer` zu `[BELASTBAR]`. Schnittstellen S5 (Retention-Trigger), S6 (Tenant Data Export), S7 (Geo→Tile-Proxy) zu `[BELASTBAR]`. Invarianten I4, I5 zu `[BELASTBAR]`.

**Schritte (gröber):**

- **6.1** `backend/geo`: Routing-Adapter (TomTom mit aktiver API-Version pinned, Migrations-Hinweise aus `project-context.md` Abschnitt 5 berücksichtigen), Tile-Cache-Steuerung, Sperrungs-Override (Spike-G-Technik), Geofencing.
- **6.2** `frontend-disponent`: produktives Lagezentrum mit MapLibre-Karte, Operation-Eröffnung, Multi-Disponenten-Confirmation-Dialog für destruktive Aktionen (Regel-012), Audit-Log-Anzeige.
- **6.3** `frontend-betreuer`: produktive Mobile-PWA mit Turn-by-Turn (TomTom-Routing über `backend/geo`), Hilfe-Knopf-UX (Spike-K-Konzept), Offline-Tile-Cache (Spike-L-Strategie).
- **6.4** `backend/resilience`: Backup-Strategie (Spike-H-Wahl), Recovery-Verfahren, Backup-Recovery-Test als Stabilisierungs-Anker.
- **6.5** `backend/retention`: Aggregat-Schreibung beim Operation-Ende (ADR-006, Regel-008), 30-Tage-Anonymisierungs-Job (entkoppelter Procrastinate-Job).
- **6.6** `backend/export`: API-Tripel POST/GET-Status/GET-Download (ADR-007), Cleanup-Job (zweiter Procrastinate-Job, täglich).
- **6.7** Tests + Coverage (`backend/retention` ≥ 95 %, `backend/resilience` ≥ 90 %).

---

### Phase 7: Stabilisierung, Roll-out-Vorbereitung, Validierung – Typ: STABILISIERUNG

**Ziel:** System lasttauglich für die Annahme 50 Disponenten + 500 Einsatzkräfte (`project-context.md` Abschnitt 2), p95 < 300 ms validiert, externe Security-Review Auth-Stack bestanden, organisatorische Voraussetzungen für ersten produktiven Mandanten erfüllt (Roadmap-Meilensteine N/O/P), Status-Wechsel `Konzeption` → `Aufbau` → `aktive Entwicklung`.

**Abschlusskriterium:** Lasttest grün gegen 50/500-Annahme; externer Auditor bestätigt Auth-Stack; DSGVO-Datenverarbeitungs-Vereinbarung, Nutzungsbedingungen, Haftungsklarheit als finalisierte Dokumente; Plattform-Betreiber-Entscheidung getroffen; Test-Termin reale Großlage festgelegt.

**Reifegrad-Erwartung am Phasenende:** Architektur-Pattern (Modular Monolith + 3 SvelteKit-Frontends) → `[BELASTBAR]` durch Lasttest. NFR Performance, NFR Skalierungs-Annahme 50/500 → `[BELASTBAR]` durch Messung. NFR Bedrohungsmodell → `[BELASTBAR]` durch externe Security-Review.

**Schritte (gröber):**

- **7.1** Lasttest gegen 50/500 (k6 oder Locust), Messung p95 Backend-API < 300 ms, Auswertung als ADR `[ERKENNTNIS] [PERFORMANCE]`.
- **7.2** Externe Security-Review Auth-Stack (`project-context.md` Abschnitt 3): Beauftragung, Durchführung, Findings-Auflösung, Bestätigung. Ergebnis als ADR `[ERKENNTNIS] [SECURITY]` plus geschlossene Findings im Logbuch.
- **7.3** Roadmap-Meilenstein O (Test-Termin reale Großlage) festsetzen mit DPolG-Bremen.
- **7.4** Roadmap-Meilenstein P (Onboarding-Unterlagen): DSGVO-Datenverarbeitungs-Vereinbarung, Nutzungsbedingungen, Haftungsklarheit als externe Dokumente erstellen (kein Code, nicht-technische Voraussetzung).
- **7.5** Roadmap-Meilenstein N (Plattform-Betreiber-Governance): Patrick persönlich vs. Trägerverein vs. Stiftung – Entscheidung dokumentieren als ADR `[STRATEGISCH] [METHODIK]`. Verknüpft mit der offenen Skalierungs-Frage „zentraler vs. mehrere Plattform-Admins" (`project-context.md` Abschnitt 11).
- **7.6** Reaktiv-Quote-Reflexion: prüfen, ob Schwellenwert 20 % überschritten wurde; falls ja, Architektur-Refactoring-Pfad festlegen.
- **7.7** Status-Wechsel `Konzeption` → `Aufbau`: README-Badge, `project-context.md` Abschnitt 1, CHANGELOG-Eintrag im selben Commit. Direkter-Push-auf-`main`-Privileg endet mit dem nächsten Wechsel auf `aktive Entwicklung`.
- **7.8** Erste produktive Mandanten-Freischaltung DPolG-Bremen.

---

### Phase X: Verbund-Modus für parallele Mandanten-Großlagen _(spätere Erweiterung)_ – Typ: ERKUNDUNG → UMSETZUNG

**Ziel:** Verbund-Modus produktiv (ADR-009 setzt das Fundament). Aktivierung erst nach Phase 7 plus konkretem Stakeholder-Bedarf von zwei Mandanten.

**Abschlusskriterium:** Zwei Mandanten können eine gemeinsame Operation eröffnen, beidseitige Vertragsannahme protokolliert, gemeinsame Operations-URL plus AccessCode, Cross-Mandanten-Disposition (Regel-014 abstrakter Filter wird produktiv ausgewertet), Datenexport mit Quell-Markierung (I5 erweitert), Aggregat-Migration (I4 erweitert).

**Reifegrad-Erwartung am Phasenende:** Erweiterte Verbund-Schnittstellen, neue Datenmodelle (Verbund-Verträge in `backend/tenants`), erweiterte Aggregat-Schemata in `backend/retention` und Export-Schemata in `backend/export` zu `[BELASTBAR]`.

**Schritte (sehr grob, Verfeinerung kurz vor Phase X):**

- **X.1** ERKUNDUNG: Stakeholder-Klärung mit zwei Mandanten – Berechtigungs-Modell-Verfeinerung, Statistik-Zuordnung, Vertrags-Modell. Ergebnis: ADR `[ERKENNTNIS] [DATENMODELL]`.
- **X.2** `backend/tenants`-Erweiterung: Verbund-Verträge (Initiative, Akzeptanz, Auflösung) mit Audit-Spur.
- **X.3** `backend/operations`-Erweiterung: Cross-Mandanten-Disposition, gemeinsame Operations-URL, neue Rolle `role='participant'` in `operation_tenant_participation`.
- **X.4** Schema-Migration `operation_aggregate` (I4 erweitern auf mehrere verarbeitende Mandanten oder Quell-Markierung).
- **X.5** `backend/export`-Erweiterung: geteilte Datensätze mit Quell-Markierung (I5 erweitert).
- **X.6** Tests + STABILISIERUNG-Phase im Anschluss.

**Hinweis:** Bei Bedarf im Projektverlauf wird Phase X aus dem späteren Bereich in die Hauptphasen-Liste eingegliedert; Replanning wird in der Replanning-Historie dokumentiert.

---

## Iterations-Reflexion

[Nach Abschluss jeder Phase wird hier ein kurzer Eintrag ergänzt: was wurde gelernt,
welche Annahmen kippten, welche Reifegrad-Änderungen folgen, welche neuen Phasen wurden ergänzt.
Verhindert, dass Erkenntnisse im Tagesgeschäft verloren gehen.]

### Reflexion nach Phase 1 ([Datum])

- **Gelernt:** [...]
- **Kippende Annahmen:** [...]
- **Reifegrad-Änderungen:** [Bestandteil X: VORLÄUFIG → BELASTBAR; Bestandteil Y: VORLÄUFIG → OFFEN]
- **Neu erkannte Erkundungsbedarfe:** [neue Phasen oder Schritte, die hinzugefügt wurden]
- **ADRs aus dieser Phase:** [Liste]

---

## Parallelisierbarkeit

Innerhalb der einzelnen Phasen sind die Schritte stark sequentiell, weil die Bootstrap-/Modul-Aufbau-Logik aufeinander aufbaut. Echte Parallelisierungs-Optionen:

- **Phase 1 Schritte 1.6 (Auth-CLI) und 1.7 (Frontend-Workspaces)** sind unabhängig voneinander, sobald 1.3 + 1.4 + 1.1 erledigt sind.
- **Phase 3 Spikes 3.1 (Geo-Plausibilität) und 3.2 (Bündelungs-Trigger)** sind komplett unabhängig.
- **Phase 5 Spikes 5.1–5.5** sind paarweise unabhängig; Spike H (Resilience) kann zeitlich parallel zu Spike G/K/L laufen.
- **Phase 6 Schritte 6.4 (Resilience), 6.5 (Retention), 6.6 (Export)** überlappen sich nur auf der Procrastinate-Schnittstelle, sind ansonsten unabhängig.

Schritte mit gemeinsamen Modulen (Konfliktgefahr): siehe `architecture.md` Abschnitt 3 Modul-Liste – jede Schritt-Spezifikation listet die berührten Module explizit auf, parallele Bearbeitung desselben Moduls ist zu vermeiden.

## Replanning-Historie

[Wenn der Fahrplan umstrukturiert wurde: kurzer Eintrag mit Datum und Grund.
Nicht die einzelnen Schrittänderungen, sondern strukturelle Replanning-Entscheidungen.
Diese sind freigabepflichtig.]

- **2026-05-07** – Initiale Phasen-Struktur in Modus-2-Schritt 6 festgelegt (7 reguläre Phasen + 1 spätere Erweiterungs-Phase X für Verbund-Modus).

## Archiv / abgeschlossene Phasen

[Ältere abgeschlossene Arbeit mit Abschlussdatum.
Bei >500 Zeilen nach `docs/archiv/fahrplan-YYYY-MM.md` auslagern.]
