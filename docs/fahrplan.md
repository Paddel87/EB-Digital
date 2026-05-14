# Fahrplan

<!-- Zentrales Arbeitsdokument. Wird vor jeder Änderung gelesen (CLAUDE.md Abschnitt 2)
     und nach jedem Arbeitsschritt sowie zu Sessionende aktualisiert (Abschnitt 12).
     Phasen sind nach Typ klassifiziert (Erkundung / Umsetzung / Stabilisierung),
     weil iterative Entwicklung unterschiedliche Erfolgskriterien pro Phasentyp braucht. -->

## Aktueller Stand

- **Stand vom:** 2026-05-15
- **Laufende Phase:** Phase 2 – Auth + Tenants + Verbund-Tauglichkeit (I1/I2) (UMSETZUNG).
- **Phasentyp:** UMSETZUNG (**Phase-2-Sonderregel:** Eingangsdisziplin analog Phase 1 abgemildert — alle berührten Module bleiben durch Skelett-Existenz `[VORLÄUFIG]`; Modul-Schnitt durch ADR-002/003/004/008/009 fixiert, Datenmodell-Grundzüge durch ADR-006/007 fixiert. Reifegrad-Beförderung `[VORLÄUFIG]` → `[BELASTBAR]` erfolgt mit dem jeweiligen funktionalen Schritt, nicht mit dem Datenmodell-Skelett. Patrick freigegeben 2026-05-10.).
- **Erledigte Schritte Phase 2:** **2.5 [ERLEDIGT]** 2026-05-15 (`frontend-disponent` Login + Dashboard + Reset-Password-UI produktiv: Route-Gruppen `(public)/`/`(authed)/`, In-Memory-Session-Cache, API-Client-Wrapper mit Error-Mapping für 7 Statuscodes + Retry-After-Parsing, Login-Form mit Rate-Limit-Countdown, Dashboard mit Mandanten-Tabelle und Status-Badges, Carer-Hinweisseite, Operations-Platzhalter, Reset-Password-Form mit Client-Side-Validierung, Vite-Dev-Proxy, Browser-Globals in ESLint-Flat-Config, `.gitattributes` mit `eol=lf` als Plattform-Hygiene-Fix gegen CRLF-Drift unter Windows; 27 Vitest-Tests grün, Coverage ≥ 96 % auf den getesteten Auth-/API-Modulen; svelte-check + tsc + eslint + prettier + build + alle Pre-Commit-Hooks grün; `dev-smoke.sh` um Frontend-Smoke-Block erweitert; Backend-Suite weiterhin 439/1 grün mit 95.82 % Coverage). **2.4 [ERLEDIGT]** 2026-05-12 (`backend/tenants` produktiv: 6 neue Module unter `backend/eb_digital/tenants/{slug,username,repositories,use_cases,participation,api}.py` + `auth/reset_token.py`; Tenant-Modell um zwei Lookup-Indizes erweitert + Migration `a7c3b2d8e9f1` (S10-Pflicht-Indizes, in 2.1 versehentlich ausgelassen); Erweiterung `auth/api.py` um `register-tenant`, `reset-password` und Tenant-Status-Check im Login-Pfad; 7 neue Domain-Exception-Klassen; 10 neue Test-Dateien mit 153 neuen Tests bringen Backend von 286 auf 439 / 95.82 % Coverage gesamt, `backend/tenants` 95–100 %; alle Pflicht-Hooks pre-commit grün; `dev-smoke.sh` um Tenants-Block (10 Schritte) erweitert; Compose-Smoke + Alembic-Round-Trip live im Stack verifiziert; Detail-Plan mit 4 Detail-Entscheidungen Patrick am 2026-05-12 mit B/B/A/A freigegeben). **2.3 [ERLEDIGT]** 2026-05-11 (`backend/auth_anonymous` produktiv). **2.2 [ERLEDIGT]** 2026-05-10 (Login + Cookie-Sessions + Rate-Limit produktiv, ADR-013 + redis-py-Sub-Wahl). **2.1 [ERLEDIGT]** 2026-05-10 (Datenmodell-Skelett). Phase 1 vollständig **ERLEDIGT** (1.1–1.8).
- **Aktiver Schritt:** keiner.
- **Nächster Schritt:** **2.6** `frontend-einsatzkraft` AccessCode-Eingabe-UI (anonyme Session mit Code-Validierung gegen S2a).
- **Offene STOPP-Situationen:** keine.
- **Aktive Blocker:** **0** (Blocker #001 am 2026-05-10 ursächlich aufgeklärt — siehe [`docs/blockers.md`](blockers.md) und [`scripts/fix-venv-flags.sh`](../scripts/fix-venv-flags.sh)).
- **CI-Hygiene-Sonderfall in Phase 1 (2026-05-10):** ADR-012 — `actions/upload-artifact@v4` → `@v7` als Major-Update gegen Node-20-Deprecation, analog zu ADR-010 in 1.2. Reaktiv-Quote bleibt 0 / 10.
- **Strategische Klarstellung zwischen 2.1 und 2.2 (2026-05-10):** ADR-014 — Anbieter-Austauschbarkeit für externe Geo-Services als Architektur-Prinzip + Regel-017. Außerhalb der Schritt-Sequenz, dokumentations-only (kein Code-Eingriff). Reaktiv-Quote bleibt 0 / 10. Keine Auswirkung auf Schritt-2.2-Plan; jedoch erweiterte Eingangsbedingung für Phase 6 (`backend/geo` + `infra/tile-proxy`-Implementierung): MapTiler-Sales-Approval für serverseitigen Cache vor erster Tile-Proxy-Implementierung zu klären, oder Pfad-B/C/D-Wechsel — siehe `project-context.md` Abschnitt 11. Wird in Phase-7-Roadmap-Meilenstein „MapTiler-Sales-Anfrage" gespiegelt.

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

| Phase | Titel                                                                   | Typ                   | Spikes / Roadmap  | Status                                                                                                             |
| ----- | ----------------------------------------------------------------------- | --------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------ |
| 1     | Repository-Bootstrap & Tech-Foundations                                 | UMSETZUNG             | –                 | ERLEDIGT (1.1–1.8 erledigt 2026-05-10)                                                                             |
| 2     | Auth + Tenants + Verbund-Tauglichkeit                                   | UMSETZUNG             | –                 | IN ARBEIT (2.1+2.2 ERLEDIGT 2026-05-10, 2.3 ERLEDIGT 2026-05-11, 2.4 ERLEDIGT 2026-05-12, 2.5 ERLEDIGT 2026-05-15) |
| 3     | Spikes Wave 1 – Operations-Vorklärungen                                 | ERKUNDUNG             | I, J              | OFFEN                                                                                                              |
| 4     | Operations Core + Realtime + Einsatzkraft-PWA                           | UMSETZUNG             | –                 | OFFEN                                                                                                              |
| 5     | Spikes Wave 2 – Geo, Frontends, Resilience, Roll-out                    | ERKUNDUNG             | G, H, K, L, M     | OFFEN                                                                                                              |
| 6     | Geo + Disponent-/Betreuer-PWAs + Resilience + Retention + Export        | UMSETZUNG             | –                 | OFFEN                                                                                                              |
| 7     | Stabilisierung, Roll-out-Vorbereitung, Validierung                      | STABILISIERUNG        | – (Roadmap N/O/P) | OFFEN                                                                                                              |
| X     | Verbund-Modus für parallele Mandanten-Großlagen _(spätere Erweiterung)_ | ERKUNDUNG → UMSETZUNG | (eigener Spike)   | OFFEN                                                                                                              |

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

- **Status:** ERLEDIGT (2026-05-09)
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 1.4
- **Freigabepflichtig:** nein (operative Setzungen; ADR-011 nachgezogen für die LGPL-Sub-Dep `psycopg`)
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
- **Versions-Verifikation für Schritt 1.5** (Modus-2-Schritt 2a, Sessionstart 2026-05-09):
  - **procrastinate~=3.8.1** — `Verifiziert: 2026-05-09` (PyPI-Stand: 3.8.1 vom 2026-04-08, ~1 Monat Praxisreife; Production/Stable-Classifier; 3.8.1 ist Type-Hint-Refinement gegenüber 3.8.0, kein Hotfix-Pattern wie pydantic-settings 2.14.0/2.14.1; Lizenz MIT).
  - **psycopg[binary,pool]~=3.3.4** — `Verifiziert: 2026-05-09` (Pflicht-Sub-Dep zu procrastinate, Lizenz **LGPL-3.0-only**, explizit per **ADR-011** als einzige LGPL-Ausnahme zur Lizenz-Restriktion in `project-context.md` Abschnitt 6 akzeptiert; `binary`-Extra macht das Image auf macOS und in Debian-basierten Containern reproduzierbar ohne System-libpq).
- **Verifikation am 2026-05-09 (alle Akzeptanzkriterien aus Fahrplan 1.5 erfüllt):**
  1. ✅ **Lokaler Smoke-Test:** `python -m eb_digital worker` startet (JSON-Logs zeigen `Starting worker on all queues`, `Installing signal handler`, `tasks: [..., 'ping']`); ein-Skript-Defer (`ping.defer_async()`) erzeugt Job-ID 1; Worker pickt nach <1 s auf, Log zeigt `Starting job ping[1]()`, `eb_digital.jobs.ping ping_task_executed`, `Result: pong`.
  2. ✅ **Lokaler SIGTERM-Test:** `kill -TERM <pid>` → Worker stoppt nach 2 s mit Log `Stop requested` → `Cancelled task deferrer` → `Unregistered finished worker` → `Stopped worker on all queues`.
  3. ✅ **Container-Smoke-Test:** `docker compose --profile dev build worker` baut `eb-digital-backend:dev` aus `docker/Dockerfile.backend`. `docker compose --profile dev up -d worker` startet den Worker im Container, der gegen den `db`-Service connected (`Registered worker 2 in the database`). Defer via `docker compose run --rm --no-deps worker python -c "..."` erzeugt Job-ID 2, Worker-Container loggt `Starting job ping[2]()` + `Result: pong`.
  4. ✅ **Container-SIGTERM-Test:** `docker compose --profile dev stop worker` bringt den Container in <1 s mit identischer Stopp-Sequenz herunter.
  5. ✅ `alembic upgrade head` läuft inkl. der neuen `add procrastinate schema`-Migration. `alembic check` meldet nach erfolgtem Upgrade „No new upgrade operations detected" — der `include_object`/`include_name`-Filter im env.py blendet die `procrastinate_*`-Objekte für Autogenerate aus, sodass die externe Schemen-Verwaltung (Procrastinate verwaltet seine Tabellen selber bei zukünftigen Major-Updates) und Alembic koexistieren.
  6. ✅ `alembic downgrade 660e1a12a41a && alembic upgrade head` als Roundtrip — alle 4 Tabellen, 18 Funktionen und 3 Enum-Typen sauber gedroppt und neu erzeugt.
  7. ✅ `uv run ruff check backend` + `ruff format --check backend` + `uv run mypy --strict` (9 source files) alle grün.
  8. ✅ `uv run pytest` 66 Tests grün, **Coverage 92 %** gesamt (settings/app/logging/db/jobs/ping je 100 %, `__main__.py` 81 %; Schwelle 80 % deutlich überschritten).
  9. ✅ `uv run pre-commit run --all-files` grün — alle Hooks (Hygiene, ruff lint+format, mypy, bandit, prettier, actionlint, commitlint). Mypy-Hook-`additional_dependencies` um `procrastinate~=3.8.1` und `psycopg[binary,pool]~=3.3.4` erweitert.
- **Reibungen während 1.5** (alle dokumentiert im Logbuch-Sessionende-Eintrag):
  - **psycopg LGPL-3.0-only-Reibung mit Lizenz-Constraint:** procrastinate ist MIT, zieht aber psycopg als Pflicht-Sub-Dep — und psycopg ist LGPL-3.0-only. `project-context.md` Abschnitt 6 schließt LGPL ohne ADR aus. STOPP-Situation während Schritt 1.5; Patrick wählte Option C: ADR-Akzeptanz **plus** Methodik-Regel. ADR-011 + Regel-016 angelegt. Geltungsbereich der LGPL-Verschmutzung auf Persistenz-/Job-Engine-Pfad beschränkt; Module ohne Job-Engine bleiben extraktionsfähig. Reaktiv-Quote bleibt 0/10 (klar `[OPERATIV]`, kein Pivot).
  - **asyncpg-Multi-Statement-Limit bei Procrastinate-Schema-Apply:** Procrastinate's `SchemaManager.get_schema()` liefert ~20 KB SQL mit mehreren Statements und `$$`-Function-Bodies. asyncpg's prepared-statement-Pfad lehnt Multi-Statement ab (`cannot insert multiple commands into a prepared statement`). Lösung: Statement-Splitter direkt in der Migration, der Top-Level-Semikolons trennt und PostgreSQL-Dollar-Quoting (`$$`, `$tag$`) respektiert. Splitter ist mit 11 Tests (`test_migration_splitter.py`) abgesichert; Roundtrip `upgrade → downgrade → upgrade` validiert.
  - **`alembic check` will Procrastinate-Tabellen droppen:** Das von der Migration erzeugte Schema ist nicht in `Base.metadata` registriert, daher schlägt Autogenerate vor, die Tabellen zu droppen. Lösung: `include_object`- und `include_name`-Callbacks in `env.py`, die alle Objekte mit Präfix `procrastinate_` ausblenden. Damit kann Procrastinate seine Tabellen via eigenem Migrations-System pflegen, ohne dass Alembic-Autogenerate das stört.
  - **Procrastinate-Worker und uvicorn-Logger-Pattern:** wie schon in 1.3 für uvicorn musste `configure_logging` vor `procrastinate_app.run_worker_async` aufgerufen werden, damit Procrastinate's Logger via Root-Propagation auf den `JsonLogFormatter` gehen. Bestätigt: alle Worker-Container-Log-Zeilen sind valides JSON.
  - **Coverage-Source-Pfad:** Der bisherige Pfad `--cov=backend/eb_digital` schlug fehl, weil die neue conftest.py-Top-Level-`os.environ.setdefault`-Setup-Logik das Modul erstmalig vor Coverage-Initialisierung importiert (`No data was collected`). Wechsel auf den **Modul-Namen** `--cov=eb_digital` — Coverage findet das Modul jetzt über den Editable-Install-Pfad zuverlässig. Dauerhafte Verbesserung über Schritt 1.5 hinaus.
  - **`_editable_impl_*.pth`-Reibung dritte Iteration:** trat erneut nach `uv sync --reinstall-package eb-digital` auf. Heilung 1.4 (`rm -rf .venv && uv sync`) wirkte sofort. Hypothese aus 1.4 (uv-Cache-Zustand bei Re-Install vs. Wheel-Build) bestätigt sich; Drittauftritt rechtfertigt das Anlegen eines Blocker-Stub-Eintrags noch nicht (Heilung ist deterministisch und einzeilig).
  - **mypy-Hook-Reinstall-Korruption:** Während der Verifikations-Sequenz brach mypy mit `ModuleNotFoundError: No module named '0aca9ce3d91742c5b361__mypyc'` ab. `uv sync --reinstall` heilte. Vermutlich Reibung mit dem `pre-commit`-Hook-venv-Cache; beim nächsten `uv sync --reinstall-package mypy` ohne nukleare Reset trat es nicht erneut auf.

#### 1.6: backend/auth Admin-Bootstrap-CLI

- **Status:** ERLEDIGT (2026-05-10)
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

- **Status:** ERLEDIGT (2026-05-10)
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

- **Status:** ERLEDIGT (2026-05-10)
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

#### 2.1: Datenmodell-Skelett (Tenant + Dispatcher + Carer + Operation + Participation + AuditLog) – Typ: UMSETZUNG

- **Status:** ERLEDIGT 2026-05-10 (begonnen 2026-05-10 nach Patrick-Freigabe Detail-Plan + Phase-2-Sonderregel)
- **Phasentyp-Kontext:** UMSETZUNG (Phase 2, Phase-2-Sonderregel: Eingangsdisziplin abgemildert; siehe „Aktueller Stand")
- **Abhängigkeiten:** Phase 1 vollständig ERLEDIGT (`db.Base`, `TimestampMixin`, Naming-Convention, Alembic-Setup, Procrastinate-Schema-Migration aktiv).
- **Freigabepflichtig:** ja (Datenmodelländerung CLAUDE.md Abschnitt 4 Punkt 4) — Detail-Plan im Chat 2026-05-10 vorgelegt, Patrick freigegeben („geht davon aus, dass die Tabellen richtig in Bezug auf Vision und Projekt-Kontext erstellt sind"). Kein neuer ADR; die Grobstruktur liegt durch ADR-006/007/008/009 fest.
- **Eingangskriterien:** Phase 1 ERLEDIGT ✓; Phase-2-Sonderregel akzeptiert ✓; alle benötigten Bibliotheken (SQLAlchemy 2.0.49, Alembic 1.18.x, asyncpg 0.31.x, psycopg 3.3.4) bereits in Phase 1 verifiziert und produktiv.
- **Zu tun:**
  1. **Modul-Skelette:**
     - `backend/eb_digital/tenants/__init__.py` + `tenants/models.py` (neu): `Tenant`, `OperationTenantParticipation`.
     - `backend/eb_digital/operations/__init__.py` + `operations/models.py` (neu): `Operation`, `OperationAuditLog`.
     - `backend/eb_digital/auth/models.py` (Erweiterung): `DispatcherUser`, `CarerUser` parallel zu bestehender `PlatformAdmin`-Klasse.
  2. **`backend/migrations/env.py`**: Imports der drei neuen Module ergänzen, damit Alembic-Autogenerate alle Tabellen sieht.
  3. **Alembic-Migration**: `alembic revision --autogenerate -m "add tenant dispatcher carer operation participation auditlog"`. Nach Autogenerate-Lauf manuell prüfen, dass:
     - Naming-Convention auf alle PK/FK/UQ/CK/IX angewendet ist (Stichprobe `pk_…`, `fk_…`, `uq_…`, `ck_…`, `ix_…`).
     - Partial-Unique-Index `ix_operation_tenant_participation_owner_unique` mit `postgresql_where=sa.text("role = 'owner'")` enthalten ist; falls Autogenerate den Partial-Filter ausgelassen hat, manuell ergänzen.
     - JSONB-Spalte `operation_audit_log.payload` als `postgresql.JSONB` typisiert ist.
  4. **Tests** (neu/erweitert): siehe Akzeptanzkriterien.
- **Akzeptanzkriterien (UMSETZUNG → funktionsbasiert):**
  1. `alembic upgrade head` läuft fehlerfrei gegen die Compose-DB; alle sechs neuen Tabellen werden erzeugt.
  2. `alembic check` nach Upgrade: „No new upgrade operations detected".
  3. `alembic downgrade -1` rollt sauber zurück auf Pre-2.1-Stand und `upgrade head` wieder hoch.
  4. **Constraint-Tests grün:**
     - `tenant.status` CHECK lehnt unbekannte Werte ab.
     - `operation.status` CHECK lehnt unbekannte Werte ab.
     - `(dispatcher.tenant_id, dispatcher.username)` UNIQUE; selbe Username-/Tenant-Kombination scheitert mit IntegrityError; gleicher Username für anderen Tenant ist erlaubt.
     - `(carer.tenant_id, carer.username)` analog.
     - `operation_tenant_participation.role` CHECK auf `('owner','participant')`.
     - **Partial-Unique-Index**: zwei Inserts mit `role='owner'` für dieselbe Operation scheitern mit IntegrityError; ein zweiter Eintrag mit `role='participant'` für dieselbe Operation ist erlaubt.
     - `operation_audit_log` Insert mit JSONB-Payload und Lookup über `(operation_id, at)`-Index.
  5. `uv run pytest` grün; neue `models.py`-Dateien bei 100 % Coverage; Backend-Coverage gesamt ≥ 80 %.
  6. `uv run ruff check backend` + `ruff format --check backend` + `uv run mypy --strict` + `uv run pre-commit run --all-files` grün.
  7. Compose-Smoke: `docker compose --profile dev up -d` führt `db-init` mit der neuen Migration aus; `docker compose exec db psql -U eb_digital -c "\dt"` zeigt die sechs neuen Tabellen.
- **Betroffene Module:** `backend/auth`, `backend/auth_anonymous` (nur indirekt — kein Modul-Code in 2.1, aber `operation.access_code_hash` und `operation.url_token` legen die Felder vor, die 2.3 nutzt), `backend/tenants`, `backend/operations`.
- **Reifegrad-Wirkung:** Keine Beförderung in 2.1. Module bleiben `[VORLÄUFIG]` (Skelett ohne funktionale Belastbarkeit, analog zur Phase-1-Sonderregel).
- **Artefakte:**
  - `backend/eb_digital/tenants/__init__.py`, `tenants/models.py` (neu)
  - `backend/eb_digital/operations/__init__.py`, `operations/models.py` (neu)
  - `backend/eb_digital/auth/models.py` (Erweiterung)
  - `backend/migrations/env.py` (Import-Erweiterung)
  - `backend/migrations/versions/<timestamp>_<rev>_add_tenant_dispatcher_carer_operation_participation_auditlog.py` (neu)
  - `backend/tests/test_tenants_models.py`, `test_operations_models.py`, `test_operation_tenant_participation.py`, `test_operation_audit_log.py` (neu)
  - `backend/tests/test_auth_models.py` (Erweiterung um `DispatcherUser`/`CarerUser`)
- **Notizen:**
  - **Partial-Unique-Index** schützt Phase-1-Invariante I1 („genau ein Owner pro Operation") auf DB-Ebene; bleibt in Phase X gültig, weil dort nur `role='participant'` additiv hinzukommt.
  - **`access_code_hash` (Argon2id) statt Klartext**: Konstantzeit-Vergleich (Regel-006); kein Klartext im DB-Dump.
  - **`actor_dispatcher_id` ON DELETE SET NULL** statt CASCADE: Audit-Log-Erhalt vor FK-Konsistenz priorisiert (DSGVO-Anonymisierung erhält Audit-Spur, entfernt Personenbezug).
  - **`target_id` NOT NULL**: bei Operation-Level-Aktionen Convention `target_id = operation_id`.
  - Kein neuer ADR; Architektur-Spec-Update in `architecture.md` Abschnitt 7 nur falls beim Implementieren Detail-Drift sichtbar wird.

#### 2.2: backend/auth Login + Session + Rate-Limit – Typ: UMSETZUNG

- **Status:** ERLEDIGT 2026-05-10 (begonnen 2026-05-10 nach Patrick-Freigabe Detail-Plan + ADR-013 + redis-py-Sub-Wahl).
- **Phasentyp-Kontext:** UMSETZUNG (Phase 2, Phase-2-Sonderregel: Eingangsdisziplin abgemildert)
- **Abhängigkeiten:** 2.1 ERLEDIGT (Tabellen `dispatcher`, `carer` mit `password_hash`, `is_active`, `username` unique pro Tenant); PlatformAdmin aus 1.6; **ADR-013** (Rate-Limit-Strategie als eigener Valkey-Counter).
- **Freigabepflichtig:** ja — neue Top-Level-Dependency `redis~=7.4.0` plus Test-Dep `fakeredis~=2.35.1` (CLAUDE.md Abschnitt 4 Punkt 3). Login-Endpoint-Spec ist durch `project-context.md` Abschnitt 6 + Abschnitt 3 fixiert, daher selbst nicht zusätzlich freigabepflichtig.
- **Eingangskriterien:** 2.1 ERLEDIGT ✓; ADR-013 entschieden ✓; Compose-Stack bringt Valkey hoch (1.8 `cache`-Service) ✓; Phase-2-Sonderregel akzeptiert ✓.
- **Zu tun:**
  1. **Dependencies pinnen** in `pyproject.toml`: `redis~=7.4.0` (runtime), `fakeredis~=2.35.1` (dev). PyPI-Verifikation am 2026-05-10 dokumentiert; `project-context.md` Abschnitt 3 entsprechend ergänzen.
  2. **`backend/eb_digital/cache/__init__.py`** (neu): async Connection-Pool gegen `settings.valkey_url` (Schema `valkey://` → `redis://` adaptieren analog `_to_psycopg_conninfo`); App-Lifespan-Wiring (Startup öffnet Pool, Shutdown schließt); Health-Helper `await ping_valkey(client)`.
  3. **`backend/eb_digital/auth/hashing.py`** (Erweiterung): `verify_dummy()`-Helper für Timing-Attack-Schutz bei nicht existierenden Usern (Aufwand identisch zu echter Verifikation).
  4. **`backend/eb_digital/auth/rate_limit.py`** (neu): `incr_and_check(client, key, *, limit, window_seconds) -> RateLimitResult` (`{allowed: bool, retry_after_seconds: int, current: int}`) per `INCR` + `EXPIRE`; `reset(client, key)` per `DELETE`; Multi-Key-AND-Helper `check_login(client, ip, username) -> RateLimitResult` (5/15min auf beiden Keys, AND-Logik). Key-Konvention: `auth:ratelimit:login:ip:<ip>` und `auth:ratelimit:login:user:<username>`.
  5. **`backend/eb_digital/auth/repositories.py`** (neu): `find_by_username(session, username) -> AuthSubject | None` (Union-Suchstrategie über `PlatformAdmin`, `Dispatcher`, `Carer`); deterministische Suchreihenfolge dokumentiert; bei Konflikten (gleiches Username in mehreren Tabellen) hat PlatformAdmin Vorrang. `AuthSubject` als typisierte Container-Klasse mit `kind`, `id`, `username`, `password_hash`, `is_active`, `tenant_id`.
  6. **`backend/eb_digital/auth/sessions.py`** (neu): `set_session(request, subject)`, `get_current_subject(request) -> AuthSubject | None` (Session-Payload-Validierung inkl. `expires_at`-Check), `clear_session(request)`. Session-Payload: `{kind, id (str), tenant_id (str|null), expires_at (iso8601)}`. Timeouts: 8 h für `platform_admin`, 24 h für `dispatcher`/`carer`.
  7. **`backend/eb_digital/auth/api.py`** (neu): drei FastAPI-Endpunkte unter `/api/auth/`:
     - `POST /api/auth/login` — Body `{username, password}`. Rate-Limit-Check (IP+User AND) **vor** DB-Lookup; danach `find_by_username`, `verify_password` oder `verify_dummy` (Timing-Attack-Schutz), bei Erfolg User-Counter-Reset + `set_session` + 200 mit `{kind, id, username, tenant_id}`; bei Misserfolg 401 mit konstanter Antwortzeit; bei Rate-Limit 429 mit `Retry-After`-Header.
     - `POST /api/auth/logout` — `clear_session`, 204.
     - `GET /api/auth/me` — 200 mit aktueller Subject-Info, 401 ohne/abgelaufene Session.
  8. **App-Wiring** (`backend/eb_digital/app.py`): `SessionMiddleware` mit `secret_key` aus Settings, `https_only` an Production gebunden, `same_site='strict'`, `session_cookie=settings.session_cookie_name`; Valkey-Pool im `lifespan`-Context; Session-Provider und Valkey-Client als FastAPI-Dependencies; `auth.api.router` an `api_router` hängen.
  9. **`scripts/dev-smoke.sh`-Erweiterung**: nach den bestehenden Health-Checks ein Login-Smoke-Block — Admin via `docker compose exec backend python -m eb_digital admin create` anlegen, danach `curl -k -c /tmp/cookies https://localhost/api/auth/login -d {…}` 200 mit Cookie, `curl -k -b /tmp/cookies https://localhost/api/auth/me` 200, `curl -k -X POST -b /tmp/cookies https://localhost/api/auth/logout` 204.
  10. **Tests** (neu): `test_cache.py`, `test_auth_hashing.py`-Erweiterung (`verify_dummy`), `test_auth_rate_limit.py`, `test_auth_repositories.py`, `test_auth_sessions.py`, `test_auth_login_api.py`. Coverage `backend/auth` ≥ 95 % Lines / ≥ 90 % Branches.
- **Akzeptanzkriterien (UMSETZUNG → funktionsbasiert):**
  1. PlatformAdmin loggt erfolgreich ein → 200, Session-Cookie mit Flags `Secure; HttpOnly; SameSite=Strict; Path=/` (Test gegen ASGI-Client).
  2. Dispatcher (Test-DB) loggt erfolgreich ein → 200, Response enthält `tenant_id`.
  3. Login mit falschem Passwort → 401; konstante Antwortzeit (`verify_dummy()` deckt non-existing-user-Pfad).
  4. Login mit nicht-existentem Username → 401, Counter (User-Key UND IP-Key) erhöht.
  5. 5 falsche Login-Versuche desselben Users innerhalb 15 min → 6. Versuch 429 mit `Retry-After`-Header.
  6. 5 falsche Versuche von derselben IP gegen 5 verschiedene Usernames → 6. Versuch 429 (IP-Counter zieht).
  7. Erfolgreicher Login löscht User-Counter, IP-Counter bleibt bestehen.
  8. Login auf User mit `is_active=False` → 401 (identisch zu wrong-password, kein Info-Leak).
  9. `GET /api/auth/me` ohne Cookie → 401; mit gültiger Session → 200; mit abgelaufener Session → 401 + Session-Clear.
  10. `POST /api/auth/logout` → 204; Folge-`/me` → 401.
  11. Session-Timeout: PlatformAdmin nach 8 h, Dispatcher/Carer nach 24 h (Test über manipulierten `expires_at`, kein Sleep).
  12. Coverage `backend/auth` ≥ 95 % Lines / ≥ 90 % Branches; Coverage `backend/eb_digital/cache` ≥ 90 %.
  13. `uv run pre-commit run --all-files` grün auf allen Hooks.
  14. `alembic check` „No new upgrade operations detected" (kein Schema-Update in 2.2).
  15. `bash scripts/dev-smoke.sh` grün — inklusive neuem Login-Smoke-Block (Admin-CLI → Login → /me → logout).
- **Betroffene Module:** `backend/auth` (Hauptarbeit), neuer Querschnitts-Bestandteil `backend/eb_digital/cache` (Valkey-Pool), `backend/eb_digital/app.py` (Wiring), `backend/eb_digital/settings.py` (gegebenenfalls Erweiterung um `session_cookie_secure: bool`). Keine Berührung von `backend/tenants`, `backend/operations`.
- **Reifegrad-Wirkung:**
  - `backend/auth` `[VORLÄUFIG]` → `[BELASTBAR]` (Login + Sessions + Rate-Limit produktiv, Timing-/Hash-Disziplin etabliert).
  - Schnittstelle S8 (Authentifizierte REST-API): bleibt insgesamt `[VORLÄUFIG]`, aber Sub-Surface `/api/auth/login`, `/api/auth/logout`, `/api/auth/me` als spezifischer Sub-Eintrag in Architektur-Reifegrad-Tabelle auf `[BELASTBAR]` (analog S1-Spec-Korrektur in 1.6).
  - Pub/Sub via Valkey bleibt `[VORLÄUFIG]` (in 2.2 nur Counter, kein Pub/Sub).
  - Connection-Pool-Pfad zu Valkey de-facto belastbar; ergänzender Architektur-Eintrag in Abschnitt 9.
- **Artefakte:** 5 neue Backend-Module (`cache/__init__.py`, `auth/rate_limit.py`, `auth/repositories.py`, `auth/sessions.py`, `auth/api.py`); Erweiterung `auth/hashing.py`, `app.py`, `settings.py`, `pyproject.toml`, `uv.lock`, `.env.example`, `scripts/dev-smoke.sh`; 5+ neue/erweiterte Test-Dateien; Logbuch- und Architektur-Updates zu Sessionende.
- **Notizen:**
  - **Counter-Reset-Disziplin:** Erfolgreicher Login löscht **nur** den User-Counter, nicht den IP-Counter (sonst Brute-Force-Sweep „1 falsches Passwort × 5 Usernames + 1 richtiges = neuer IP-Slot" möglich). Dokumentiert in `rate_limit.py`-Modul-Docstring.
  - **Test-Strategie für Valkey:** Unit-Tests gegen `fakeredis` (In-Process-Fake, kompatibel mit `redis-py`). Integration-Test gegen echten Valkey-Container im Compose-Stack via `dev-smoke.sh`-Login-Smoke. Vermeidet Container-Pflicht für Unit-Tests.
  - **Carer-Login** strukturell mit-eingebaut, aber Akzeptanztest auf PlatformAdmin + Dispatcher fokussiert; Carer-Coverage zählt mit zur 95 %-Schwelle.
  - **Coverage-Risiko:** `verify_dummy()` erzeugt einen Code-Pfad, der in der Coverage-Messung sichtbar sein muss → expliziter Test.
  - **URL-Schema-Adaption:** Settings nutzt `valkey://` als URL-Schema (Marken-Konsistenz mit ADR-002), `redis-py.from_url()` erwartet `redis://` oder `rediss://`. Cache-Modul macht das gleiche Schema-Replace wie `_to_psycopg_conninfo` für Postgres-URL.

#### 2.3: backend/auth_anonymous Anonymous-Session + URL-Token + AccessCode-Validierung – Typ: UMSETZUNG

- **Status:** ERLEDIGT 2026-05-11 (alle 18 Akzeptanzkriterien erfüllt, inkl. Compose-Smoke und Alembic-Round-Trip live im Stack verifiziert: 286 Tests grün / 97.93 % Coverage, `backend/auth_anonymous` 100 %; Stack-Smoke alle 6 Services healthy, Migration `f14e7ecace66` durch db-init auf frischer DB angewandt, Auth- und Anon-Smoke grün, Alembic-Round-Trip auf leerer Operation-Tabelle sauber, `alembic check` ohne Drift).
- **Phasentyp-Kontext:** UMSETZUNG (Phase 2, Phase-2-Sonderregel: Eingangsdisziplin abgemildert).
- **Abhängigkeiten:** 2.1 ERLEDIGT (`operation.url_token`, `access_code_hash`, `access_code_active`, `status`); 2.2 ERLEDIGT (Rate-Limit-Schicht, `verify_dummy()`, Cache/Valkey-Pool, SessionMiddleware-Wiring, fakeredis-Test-Setup); ADR-005 (AccessCode-Schema), Regel-006 (Hashing-Pflicht), Regel-007 (Toggle wirkt nur auf neue Sessions).
- **Freigabepflichtig:** ja — neue Tabelle `anonymous_session` (CLAUDE.md Abschnitt 4 Punkt 4), Spalten-Widening `operation.url_token` von `String(64)` auf `String(255)` (additive Schema-Anpassung, weil itsdangerous-signierte Token > 64 Zeichen). Detail-Plan + vier Detail-Entscheidungen (URL-Token via `itsdangerous.URLSafeSerializer`, kein `client_ip_hash`, 24h-Hard-Cap-`expires_at`, gemeinsames Secret) Patrick am 2026-05-11 vorgelegt und mit „A/B/B/A" freigegeben.
- **Eingangskriterien:** 2.1 + 2.2 ERLEDIGT ✓; ADR-005/Regel-006/007 ✓; Phase-2-Sonderregel akzeptiert ✓; keine neue Top-Level-Dependency erwartet (`itsdangerous 2.2.x` aus 1.6, `argon2-cffi 25.1.x` aus 2.2).
- **Zu tun:**
  1. **Architektur-Spec-Cleanup vorab:** [architecture.md:129](../docs/architecture.md:129) und [architecture.md:614](../docs/architecture.md:614) — Modul-Abhängigkeit (`access_code` → `access_code_hash`) und Sensitive-Datenflüsse-Eintrag (von „kein Hash" auf Argon2id-PHC) korrigieren. Bringt die Architektur-Spec mit ADR-005 + 2.1-Implementation in Übereinstimmung (war in 2.1-SESSIONENDE als „Abgleich mit 2.2–2.6" zurückgestellt).
  2. **Neues Modul `backend/eb_digital/auth_anonymous/`** mit sieben Dateien:
     - `__init__.py` — Modul-Docstring.
     - `tokens.py` — `URLSafeSerializer` aus `itsdangerous` mit Salt `"eb-digital.operation-url-token"`. Funktionen `generate_url_token(operation_id: UUID, secret: str) -> str` und `verify_url_token(token: str, secret: str) -> UUID | None`. Bei `BadSignature`/`BadPayload` → `None` (kein Throw nach außen).
     - `access_code.py` — Crockford-Base32-Generator (Alphabet `0-9` + `A-Z` ohne `I/L/O/U`, 32 Zeichen, gemäß architecture.md S2-Pattern `^[0-9A-HJ-KM-NP-TV-Z]{6}$`) via `secrets.choice`. Argon2-Wrapper `hash_access_code()`, `verify_access_code()`, `verify_dummy()` analog `auth/hashing.py`.
     - `models.py` — `AnonymousSession`-ORM.
     - `repositories.py` — `find_operation_by_id`, `create_anonymous_session`, `find_anonymous_session_by_id`, `is_session_valid`. (Read- und Insert-Pfade — Cleanup-Job ist Phase 4.)
     - `sessions.py` — `set_anonymous_session(request, session_record)`, `get_current_anonymous_session(request) -> AnonymousSessionUser | None`, `clear_anonymous_session(request)`. Cookie-Key separat (`request.session['anon']` statt der bestehenden Login-Keys), damit Login-/Anon-Sessions parallel koexistieren können.
     - `api.py` — FastAPI-Router unter `/anon` mit zwei Endpunkten.
  3. **Neue Tabelle `anonymous_session`** (Alembic-Autogenerate):

     | Spalte         | Typ         | Constraints / Notiz                                 |
     | -------------- | ----------- | --------------------------------------------------- |
     | `id`           | UUID PK     | `default uuid.uuid4`                                |
     | `operation_id` | UUID FK     | → `operation.id` `ON DELETE CASCADE`, NOT NULL      |
     | `created_at`   | TIMESTAMPTZ | NOT NULL, default `_utcnow`                         |
     | `last_seen_at` | TIMESTAMPTZ | NOT NULL, default `_utcnow` (Cleanup-Anker Phase 4) |
     | `expires_at`   | TIMESTAMPTZ | NOT NULL, default `_utcnow + 24h` (Frage-3-B)       |

     Indizes: `pk_anonymous_session`, `fk_anonymous_session_operation_id_operation`, `ix_anonymous_session_operation_id`. Kein Tenant-FK (Bezieher-Seite ist mandantenneutral, ADR-005-konsistent). Kein `client_ip_hash` (Frage-2-B: Vision-Constraint „keine PII" strikt; Rate-Limit-Counter im Valkey-TTL ist die einzige IP-Berührung).

  4. **Spalten-Widening `operation.url_token`** von `String(64)` auf `String(255)` in derselben Migration (signierte itsdangerous-Tokens sind ~80+ Zeichen). Additive Änderung, kein Datenverlust.
  5. **Endpunkte (S2 Sub-Surface):**
     - `GET /api/anon/{url_token}/info` → Token signaturprüfen → 404 bei Mismatch oder `status='closed'`/`'planned'` mit Operation-nicht-bereit-Semantik. Bei `status='active'`: 200 mit `{area_label, access_code_active, status}`. Keine Auth, kein Rate-Limit, kein Cookie. **Wahl `planned`-Behandlung:** für `status='planned'` ebenfalls 404, damit die Einsatzkraft-Sicht erst bei aktiver Operation greift (`access_code_active` aus DB; `planned`-State ist Disponenten-Vorbereitung).
     - `POST /api/anon/{url_token}/session` → Rate-Limit-Check (IP UND URL-Hash AND, 5/15 min) **vor** DB-Lookup. Token signaturprüfen → 410 bei Mismatch (Operation-Token ungültig). SELECT operation → 410 bei `status='closed'`. Bei `access_code_active=True`: Pydantic-Pattern-Check `^[0-9A-HJ-KM-NP-TV-Z]{6}$` → 422 bei Format-Verstoß; Argon2-Verify gegen `access_code_hash`; bei Mismatch → 401, beide Counter +1, identische Antwortzeit (`verify_dummy()`-Pfad bei NULL-Hash). Bei `access_code_active=False`: Body `access_code` optional/ignoriert. Bei Erfolg: URL-Counter-Reset (IP-Counter bleibt — Disziplin aus 2.2), INSERT `anonymous_session` (24h-`expires_at`), Cookie via `set_anonymous_session()`. Antwort 201 mit `{session_id}`.
  6. **App-Wiring** (`backend/eb_digital/app.py`): `auth_anonymous.api.router` an `api_router` unter `/anon` hängen.
  7. **`pyproject.toml` / Dependencies:** keine neue Top-Level-Dependency. `itsdangerous 2.2.x` und `argon2-cffi 25.1.x` aus 1.6+2.2 wiederverwendet.
  8. **`scripts/dev-smoke.sh`-Erweiterung:** Operation per Python-Direktaufruf erzeugen (analog 2.2-Admin-Pattern, weil `backend/operations` erst in 4.x kommt) — direkt INSERT mit `url_token = generate_url_token(op.id, settings.secret_key)`, `access_code_hash = hash_access_code("X7K3PQ")`, `access_code_active=True`, `status='active'`. Smoke-Pfad: `/info` → `/session` mit Code → 201; `/session` mit falschem Code → 401; `/session` auf gefälschtem Token → 410.
  9. **Tests (5 neue Dateien)** + 1 Erweiterung von `test_auth_models.py` für anonymous_session:
     - `test_auth_anonymous_tokens.py` — Roundtrip, falsches Secret, verfälschter Token.
     - `test_auth_anonymous_access_code.py` — Generator-Alphabet, Hash-Roundtrip, Konstantzeit-Heuristik.
     - `test_auth_anonymous_models.py` — anonymous_session ORM-Eigenschaften (FK CASCADE, Indizes, Default-Werte).
     - `test_auth_anonymous_repositories.py` — find/create/expire.
     - `test_auth_anonymous_api.py` — alle Endpunkte, alle Status-Codes, Rate-Limit-Counter-Disziplin.
  10. **Reifegrad-Updates zu Sessionende:** `backend/auth_anonymous` `[VORLÄUFIG]` → `[BELASTBAR]`; S2 Sub-Surface (`/info`, `/session`) als spezifischer Sub-Eintrag `[BELASTBAR]` (S2 insgesamt bleibt `[VORLÄUFIG]` bis 4.x-`POST /order`); Datenmodell `anonymous_session` `[BELASTBAR]`; `architecture.md` Sensitive-Datenflüsse-Eintrag AccessCode auf `[BELASTBAR]`.

- **Akzeptanzkriterien (UMSETZUNG → funktionsbasiert, 18 Stück):**
  1. `GET /api/anon/{valid_url_token}/info` mit aktiver Operation → 200 mit `{area_label, access_code_active, status}`.
  2. `GET /api/anon/{invalid_url_token}/info` → 404.
  3. `GET /api/anon/{closed_operation_url_token}/info` → 404.
  4. `POST /session` ohne Code bei `access_code_active=False` → 201 mit Session-Cookie.
  5. `POST /session` mit korrektem Code bei `access_code_active=True` → 201 mit Cookie.
  6. `POST /session` mit falschem Code → 401, IP- und URL-Counter +1.
  7. `POST /session` ohne Code bei `access_code_active=True` → 422 (Pydantic-Pattern-Verstoß, weil Body `access_code` Pflicht-Feld bei aktivem Code).
  8. 5 Fehlversuche/15 min/IP gegen verschiedene URLs → 6. Versuch 429 mit `Retry-After`.
  9. 5 Fehlversuche/15 min auf demselben URL-Token → 6. Versuch 429.
  10. Erfolgreicher POST /session löscht URL-Counter, IP-Counter bleibt.
  11. `POST /session` auf `status='closed'`-Operation → 410.
  12. AccessCode-Format-Pattern `^[0-9A-HJ-KM-NP-TV-Z]{6}$` durchgesetzt — ungültige Zeichen → 422.
  13. Coverage `backend/auth_anonymous` ≥ 95 % Lines / ≥ 90 % Branches.
  14. Alembic-Round-Trip `upgrade head` → `downgrade -1` → `upgrade head` grün; `alembic check` „No new upgrade operations".
  15. `uv run pre-commit run --all-files` grün auf allen Hooks (inkl. mypy --strict).
  16. `uv run pytest` grün, gesamtes Backend ≥ 80 % Coverage (globale Schwelle), kritischer Pfad ≥ 95 %.
  17. `bash scripts/dev-smoke.sh` grün, Anon-Smoke-Block durchläuft.
  18. Kein AccessCode-Klartext in Logs, Fehlermeldungen oder DB-Antworten — verifiziert per Grep-Test über `caplog` (Pytest).
- **Betroffene Module:** `backend/auth_anonymous` (Hauptarbeit, neu); `backend/eb_digital/app.py` (Router-Wiring); `backend/migrations/env.py` (Model-Registrierung); `backend/eb_digital/operations/models.py` (Spalten-Längenänderung `url_token`). **Nicht** berührt: `backend/auth`, `backend/tenants`, `backend/operations`-Use-Cases.
- **Reifegrad-Wirkung:**
  - `backend/auth_anonymous` `[VORLÄUFIG]` → `[BELASTBAR]`.
  - Schnittstelle S2 Sub-Surface (`/info`, `/session`) `[BELASTBAR]` (S2 insgesamt bleibt `[VORLÄUFIG]` bis Order-Endpoints in 4.x).
  - Datenmodell `anonymous_session` neu `[BELASTBAR]`.
  - Datenmodell `operation.url_token` (Spalten-Widening) bleibt `[BELASTBAR]` durch Migration.
  - Architektur-Spec Abschnitt 6 AccessCode-Eintrag von `[VORLÄUFIG]` (mit „kein Hash"-Notiz) auf `[BELASTBAR]` (Argon2id-PHC produktiv).
- **Artefakte:** 7 neue Backend-Module (`auth_anonymous/__init__.py`, `tokens.py`, `access_code.py`, `models.py`, `repositories.py`, `sessions.py`, `api.py`); 1 Erweiterung `app.py` + `env.py`; 1 neue Alembic-Migration; 5 neue Test-Dateien; 1 Erweiterung `scripts/dev-smoke.sh`; Logbuch- und Architektur-Updates zu Sessionende.
- **Notizen:**
  - **Counter-Reset-Disziplin:** Erfolgreiche Session-Anlage löscht URL-Counter, NICHT IP-Counter. Begründung analog 2.2: schützt vor Brute-Force-Sweep „1 falscher Code × 5 URLs + 1 richtiger = neuer IP-Slot".
  - **`itsdangerous`-Salt:** `"eb-digital.operation-url-token"` — Context-Separation gegen Token-Replay aus anderen Verwendungen desselben Secrets (z. B. Disponent-Email-Reset in Phase 7).
  - **Crockford-Base32-Diskrepanz** (Methoden-Notiz): ADR-005 sagt „ohne O/0/I/1/L"; architecture.md S2 zeigt das **kanonische** Crockford-Alphabet (ohne I/L/O/U; 0 und 1 sind valide Zeichen). Implementierung folgt architecture.md S2 (kanonische Spec); ADR-005-Wortlaut ist eine ungenaue Glosse, keine Spec-Abweichung — der ADR-Name „Crockford-Base32" ist die maßgebliche Festlegung. Hinweis in `access_code.py`-Modul-Docstring.
  - **Test-Strategie für Operation-Erzeugung:** Unit-Tests bauen `Operation`-Instanzen via Direkt-INSERT in Test-DB-Fixtures (kein `backend/operations`-Use-Case nötig). Integration-Test in `dev-smoke.sh` via Python-Direktaufruf in Backend-Container.
  - **Regel-007** (Toggle wirkt nur auf neue Sessions): in 2.3 nur indirekt umgesetzt (Code-Validierung passiert ausschließlich im `POST /session`; bestehende `anonymous_session`-Records werden bei Toggle nicht invalidiert). Expliziter Test zur Toggle-Semantik kommt mit der Toggle-Action in 4.x (`backend/operations.ToggleAccessCode`).
  - **`status='planned'`-Verhalten in `/info`:** 404 statt 200, damit die Einsatzkraft-PWA erst dann die Operation „sieht", wenn sie aktiv ist. `planned` ist Disponenten-Vorbereitungsphase. Begründung in `tokens.py` und `api.py` als Doc-Kommentar.

#### 2.4: backend/tenants Self-Service-Antrag + Approve + CRUD + Reset-Token + S10 – Typ: UMSETZUNG

- **Status:** ERLEDIGT 2026-05-12 (alle 22 Akzeptanzkriterien erfüllt, inkl. Compose-Smoke und Alembic-Round-Trip live im Stack: 439 Tests grün / 95.82 % Coverage gesamt, `backend/tenants` 95–100 %; Stack-Smoke alle 6 Services healthy, Migration `a7c3b2d8e9f1` durch db-init auf frischer DB angewandt, alle 10 Tenants-Smoke-Schritte grün, Alembic downgrade/upgrade Round-Trip auf der neuen Index-Migration sauber, `alembic check` ohne Drift).
- **Phasentyp-Kontext:** UMSETZUNG (Phase 2, Phase-2-Sonderregel: Eingangsdisziplin abgemildert; `backend/tenants`-Skelett aus 2.1 vorhanden, Modul-Reifegrad-Beförderung mit diesem Schritt).
- **Abhängigkeiten:** 2.1 ERLEDIGT (`Tenant`, `OperationTenantParticipation`, `Dispatcher`, `Carer`, `Operation` als Skelett); 2.2 ERLEDIGT (Cookie-Sessions, Rate-Limit-Schicht, `AuthSubject`, `find_by_username`, Argon2-Hashing, `verify_dummy`); 2.3 ERLEDIGT (`itsdangerous`-Token-Pattern als Vorlage für Reset-Token-Modul); ADR-008 (Multi-Disponent ohne Lead), ADR-009 (Verbund-Reinterpretation V2 + Invarianten I1/I5), Regel-013 (Operation↔Mandant ausschließlich über Participation), Regel-014 (Berechtigungs-Filter als Teilnahme-Filter).
- **Freigabepflichtig:** ja — neue API-Verträge (Self-Service-Antrag, Approve, Tenant-CRUD, Dispatcher-/Carer-Anlage mit Reset-Token, Reset-Password, Mandanten-Deaktivierung) gemäß CLAUDE.md Abschnitt 4 Punkt 5. Detail-Plan + 4 Detail-Entscheidungen (Slug-Eingabe vs. Auto-Sluggify, Initial-Disponent-Anlage Atomar vs. separater Reset-Token-Endpoint, Wer-darf-Dispatcher-anlegen, Rate-Limit-Strenge) Patrick am 2026-05-12 vorgelegt und mit **B/B/A/A** freigegeben. Keine neue Top-Level-Dependency; keine Migration nötig (Schema steht aus 2.1).
- **Eingangskriterien:** 2.1 + 2.2 + 2.3 ERLEDIGT ✓; ADR-008/009 + Regel-013/014 ✓; Phase-2-Sonderregel akzeptiert ✓; keine neue Top-Level-Dependency erwartet (`itsdangerous` aus 1.6, `argon2-cffi` aus 2.2, `redis-py` aus 2.2).
- **Zu tun:**
  1. **Slug-Validierung `backend/eb_digital/tenants/slug.py`** (neu): `validate_slug(value: str) -> None` (raises `SlugValidationError`), `RESERVED_SLUGS`-Frozenset (`{'admin', 'api', 'auth', 'anon', 'health', 'static', 'assets'}`); Pattern `^[a-z0-9](?:[a-z0-9-]{1,62}[a-z0-9])?$` (3–64 Zeichen, beginnt/endet mit Alphanum, dazwischen `-` erlaubt, kein Doppel-`-`).
  2. **Reset-Token-Modul `backend/eb_digital/auth/reset_token.py`** (neu): `URLSafeTimedSerializer` aus `itsdangerous` mit Salt `"eb-digital.user-password-reset"` (Context-Separation gegen `auth_anonymous`-URL-Token); Funktionen `generate_reset_token(subject_kind, subject_id) -> str` und `verify_reset_token(token: str, *, max_age_seconds: int) -> tuple[Literal['platform_admin','dispatcher','carer'], UUID] | None` (24-h-Default-TTL, bei `BadSignature`/`SignatureExpired`/`BadPayload` → `None`, kein Throw).
  3. **Tenant-Repository `backend/eb_digital/tenants/repositories.py`** (neu):
     - `create_tenant_application(session, *, name, slug) -> Tenant` — Insert mit `status='applied'`.
     - `find_tenant_by_id(session, tenant_id) -> Tenant | None`.
     - `find_tenant_by_slug(session, slug) -> Tenant | None`.
     - `list_tenants(session, *, status_filter=None) -> list[Tenant]` — Plattform-Admin-Sicht, optionaler Status-Filter.
     - `approve_tenant(session, tenant_id) -> Tenant | None` — `status='active'`, `activated_at=now`. Idempotent-Check: bereits aktiver Tenant → unverändert zurückgeben.
     - `deactivate_tenant(session, tenant_id) -> Tenant | None` — `status='deactivated'`, `deactivated_at=now`.
     - **Dispatcher/Carer-Repository-Funktionen** (parallel im selben Modul oder Sub-File): `create_dispatcher_invite(session, *, tenant_id, username, email)`, `create_carer_invite(session, *, tenant_id, username, email)` — legen User mit `password_hash=NULL_SENTINEL` (oder `pending_password_hash`-Marker; siehe Detail-Plan), `is_active=False` an. Wir lösen das per **`is_active=False` + `password_hash=''`** (leerer String, Argon2-Verify schlägt strukturell fehl, Login-Pfad blockiert ohnehin durch `is_active=False`). Sauberer wäre eine `pending=True`-Spalte, die spar' ich für Phase 7-Stabilisierung.
     - `set_password_and_activate(session, *, kind, subject_id, password_hash) -> bool` — setzt Hash + `is_active=True` atomar. Liefert `False`, wenn der User schon aktiv ist (Reset-Token-Replay-Schutz).
     - **Helper `is_dispatcher_of_tenant(session, dispatcher_id, tenant_id) -> bool`** für die Berechtigungs-Prüfung „Dispatcher legt Carer im eigenen Mandanten an".
  4. **Tenant-Use-Cases `backend/eb_digital/tenants/use_cases.py`** (neu, dünne Schicht über Repository): `apply_for_tenant`, `approve_tenant`, `deactivate_tenant`, `invite_dispatcher`, `invite_carer`, `complete_password_reset`. Use-Case-Schicht orchestriert Slug-Validierung, Username-Validierung (analog Slug-Pattern, mit eigenem Pattern), Tenant-Status-Check (`status='active'` für Invites Pflicht), Reset-Token-Generierung. **Keine HTTP-Wirkung** — Use-Cases liefern Domain-Objekte oder werfen domain-spezifische Exceptions (`SlugAlreadyTaken`, `TenantNotFound`, `TenantNotActive`, `UsernameTakenInTenant`, `UserAlreadyActive`, `InvalidResetToken`).
  5. **S10-Funktions-Exporte `backend/eb_digital/tenants/participation.py`** (neu) gemäß ADR-009 + Regel-013/014:
     - `list_operations_for_tenant(session, tenant_id) -> list[UUID]` — Filter über `JOIN operation_tenant_participation … WHERE tenant_id = $1` (Regel-014: Teilnahme-Filter, kein Direkt-FK).
     - `tenant_participates_in_operation(session, tenant_id, operation_id) -> bool`.
     - `owners_of_operation(session, operation_id) -> list[UUID]` — Phase 1 stets Liste mit einem Eintrag.
     - **Hinweis:** Die DB-Indizes `(tenant_id, operation_id)` und `(operation_id, role)` erfordert die S10-Spec — wenn nach 2.1-Migration nicht vorhanden, in derselben Migration in 2.4 nachziehen (Pflicht-Check vor API-Implementation).
  6. **Tenant-API `backend/eb_digital/tenants/api.py`** (neu): FastAPI-Router unter `/api/tenants` mit Cookie-Session-Auth (Plattform-Admin oder Dispatcher des Mandanten):
     - `GET /api/tenants` — Plattform-Admin: alle Tenants (optional `?status=` Filter); Dispatcher: nur eigener Tenant (Liste mit 1 Eintrag). 401 ohne Auth.
     - `GET /api/tenants/{tenant_id}` — Plattform-Admin: jeder Tenant. Dispatcher: nur eigener Tenant (sonst 403).
     - `POST /api/tenants/{tenant_id}/approve` — nur Plattform-Admin. Idempotent. 200 mit aktualisiertem Tenant. 403 ohne Plattform-Admin-Rolle.
     - `POST /api/tenants/{tenant_id}/deactivate` — nur Plattform-Admin. 200 mit aktualisiertem Tenant. **Hinweis:** Die kaskadierende Stammdaten-Löschung (DSGVO-Art. 17) ist explizit **NICHT** in 2.4 implementiert — das ist Procrastinate-Job-Pattern und gehört zu `backend/retention` in Phase 6. 2.4 setzt nur `status='deactivated'` + `deactivated_at`; sofortige Folgewirkung ist Login-Block via Tenant-Status-Check im Login-Pfad.
     - `POST /api/tenants/{tenant_id}/dispatchers` — Plattform-Admin oder bestehender Dispatcher des Mandanten. Body `{username, email | null}`. Antwort 201 mit `{dispatcher_id, reset_token}` (Reset-Token in der Response, weil Email-Versand in Phase 1 nicht produktiv ist; Plattform-Admin/Dispatcher übermittelt manuell).
     - `POST /api/tenants/{tenant_id}/carers` — analog für Carer-Anlage.
  7. **Self-Service-Antrag `POST /api/auth/register-tenant`** in `backend/eb_digital/auth/api.py` (Erweiterung):
     - Public-Endpoint, kein Auth-Header.
     - Rate-Limit: 3 Anträge / 24 h / IP via Valkey-Counter, neuer Schlüsselraum `auth:ratelimit:register_tenant:ip:<ip>`. Bei Überschreitung 429 mit `Retry-After`.
     - Body `{name, slug}` (beide Pflicht). Slug-Validierung via `slug.py` (422 bei Format-/Reserved-Verstoß, 409 bei Slug-Kollision).
     - Antwort 201 mit `{tenant_id, status: 'applied'}`. Kein Login-Cookie, keine PII-Echo.
  8. **Reset-Password-Endpoint `POST /api/auth/reset-password`** in `backend/eb_digital/auth/api.py` (Erweiterung):
     - Public-Endpoint.
     - Rate-Limit: 5 Versuche / 15 min / IP (analog Login).
     - Body `{token, new_password}`. Mindest-Länge 12 Zeichen (analog `project-context.md` Abschnitt 6).
     - Token verifizieren (`verify_reset_token`), bei `None` → 410 (Token ungültig/abgelaufen).
     - Bei gültigem Token: `set_password_and_activate(kind, subject_id, hash_password(new_password))`. Bei `False` (User bereits aktiv) → 410 (Replay-Schutz). Bei Erfolg 204.
  9. **Login-Pfad-Erweiterung in `backend/eb_digital/auth/api.py`** (kleine Änderung): Login-Pfad prüft beim Dispatcher/Carer-Login zusätzlich `Tenant.status='active'`. Bei `applied`/`deactivated` → 401 (identische Antwort zu wrong-password, kein Info-Leak). Plattform-Admin-Login bleibt unangetastet.
  10. **App-Wiring** (`backend/eb_digital/app.py`): `tenants.api.router` an `api_router` unter `/tenants` hängen.
  11. **`scripts/dev-smoke.sh`-Erweiterung** (Tenants-Block, nach Auth-Smoke und vor Anon-Smoke):
      - `register-tenant` → 201 mit `{tenant_id}`.
      - Plattform-Admin-Login (existiert aus Auth-Smoke).
      - `GET /api/tenants` → liefert eingegangenen Antrag.
      - `POST /api/tenants/{id}/approve` → 200, `status='active'`.
      - `POST /api/tenants/{id}/dispatchers` → 201 mit Reset-Token.
      - `POST /api/auth/reset-password` mit Token + neuem Passwort → 204.
      - Login als neuer Dispatcher → 200 mit Cookie + `tenant_id` im Body.
      - `GET /api/tenants/{id}` als Dispatcher → 200 (eigener Tenant).
      - `POST /api/tenants/{id}/deactivate` als Plattform-Admin → 200, `status='deactivated'`.
      - Folge-Login als Dispatcher → 401.
  12. **Tests** (neu, ~9 Dateien):
      - `test_tenants_slug.py` — Pattern, Reserved, Trim, Edge-Cases.
      - `test_auth_reset_token.py` — Roundtrip, Expired (max_age=0), falsches Secret/Salt, Bad-Payload.
      - `test_tenants_repositories.py` — alle CRUD-Funktionen, Slug-Kollision (`IntegrityError`), Idempotenz von approve/deactivate.
      - `test_tenants_use_cases.py` — Domain-Exceptions, Status-Checks, Username-Validierung, Reset-Token-Erzeugung.
      - `test_tenants_participation.py` — S10-Funktionen mit Test-Daten (1 Owner, perspektivisch 0 Owner = leere Liste).
      - `test_tenants_api.py` — alle Endpunkte, alle Status-Codes, Rollen-Checks (Plattform-Admin vs. Dispatcher vs. cross-Tenant-Dispatcher).
      - `test_auth_register_tenant.py` — Self-Service-Antrag, Rate-Limit, Slug-Kollision, ungültiger Slug.
      - `test_auth_reset_password.py` — Token-Validierung, Mindest-Länge, Replay-Schutz, Rate-Limit.
      - `test_auth_login_api.py` — Erweiterung um Tenant-Status-Check (Dispatcher in `applied`/`deactivated`-Tenant → 401).
- **Akzeptanzkriterien (UMSETZUNG → funktionsbasiert, 22 Stück):**
  1. `POST /api/auth/register-tenant` mit gültigen Daten → 201 mit `{tenant_id, status: 'applied'}`.
  2. Self-Service-Antrag mit Slug-Kollision → 409.
  3. Self-Service-Antrag mit reservierten Slug (`admin`, `api`, …) → 422.
  4. Self-Service-Antrag mit Slug-Format-Verstoß (Großbuchstaben, Doppel-`-`, Sonderzeichen) → 422.
  5. 4. Antrag von derselben IP innerhalb 24 h → 429 mit `Retry-After`.
  6. `GET /api/tenants` als Plattform-Admin → 200, alle Tenants.
  7. `GET /api/tenants` als Dispatcher → 200, nur eigener Tenant.
  8. `GET /api/tenants/{id}` als Dispatcher mit fremder Tenant-ID → 403.
  9. `POST /api/tenants/{id}/approve` als Plattform-Admin → 200, `status='active'`.
  10. `POST /api/tenants/{id}/approve` zweimal hintereinander → idempotent, beide 200.
  11. `POST /api/tenants/{id}/approve` als Dispatcher → 403.
  12. `POST /api/tenants/{id}/dispatchers` als Plattform-Admin → 201 mit `{dispatcher_id, reset_token}`.
  13. `POST /api/tenants/{id}/dispatchers` als Dispatcher des Mandanten → 201.
  14. `POST /api/tenants/{id}/dispatchers` als Dispatcher eines anderen Mandanten → 403.
  15. `POST /api/tenants/{id}/dispatchers` mit Username-Kollision im selben Tenant → 409.
  16. `POST /api/auth/reset-password` mit gültigem Token + Passwort ≥ 12 Zeichen → 204; Folge-Login mit neuem Passwort → 200.
  17. `POST /api/auth/reset-password` mit demselben Token zum zweiten Mal → 410 (Replay-Schutz, weil User schon aktiv).
  18. `POST /api/auth/reset-password` mit verfälschtem/abgelaufenem Token → 410.
  19. `POST /api/auth/reset-password` mit Passwort < 12 Zeichen → 422.
  20. Login als Dispatcher in `applied`-Tenant → 401 (identische Antwort zu wrong-password).
  21. S10-Funktionen liefern korrekte Werte (Test mit 1 Owner-Operation, Test mit 0-Owner-Edge-Case).
  22. Coverage `backend/tenants` ≥ 80 % Lines (Standard-NFR); kein Hash-/Token-Klartext in Logs (caplog-Test).
- **Pflicht-Hooks:** `uv run pre-commit run --all-files` grün; `uv run pytest` grün (Backend gesamt ≥ 80 % Coverage); `alembic check` „No new upgrade operations detected" (kein neues Schema in 2.4); `bash scripts/dev-smoke.sh` grün inkl. Tenants-Block.
- **Betroffene Module:** `backend/tenants` (Hauptarbeit); `backend/auth` (Erweiterung um `register-tenant`, `reset-password`, Reset-Token-Modul, Tenant-Status-Check im Login-Pfad); `backend/eb_digital/app.py` (Router-Wiring). **Nicht** berührt: `backend/auth_anonymous`, `backend/operations`, `backend/fleet`, Frontends.
- **Reifegrad-Wirkung:**
  - `backend/tenants` `[VORLÄUFIG]` → `[BELASTBAR]`.
  - Schnittstelle S8 Sub-Surfaces (`/api/auth/register-tenant`, `/api/auth/reset-password`, `/api/tenants/*`) als Sub-Eintrag `[BELASTBAR]` (S8 insgesamt bleibt `[VORLÄUFIG]` bis Operations-Endpunkte in 4.x).
  - Schnittstelle **S10 (Tenant Participation Lookup)** `[VORLÄUFIG]` → `[BELASTBAR]`.
  - Invarianten **I1** und **I2** `[VORLÄUFIG]` → `[BELASTBAR]` durch funktionierende S10-Implementation und Berechtigungs-Filter im Tenant-API.
- **Artefakte:** ~7 neue Backend-Module (`tenants/slug.py`, `tenants/repositories.py`, `tenants/use_cases.py`, `tenants/participation.py`, `tenants/api.py`, `auth/reset_token.py`, evtl. `auth/passwords.py` für die Mindest-Länge-Validierung); ~2 Erweiterungen (`auth/api.py`, `app.py`); ~9 neue Test-Dateien; 1 Erweiterung `scripts/dev-smoke.sh`; Logbuch-, Architektur- und README-Updates zu Sessionende.
- **Notizen:**
  - **Initial-Reset-Token in API-Response**: Phase 1 hat keinen Email-Versand. Token wird im Response-Body zurückgegeben — Plattform-Admin/Dispatcher übermittelt ihn manuell an den neuen Dispatcher/Carer (Slack, persönlich, andere Out-of-Band-Kanäle). Phase 7 ergänzt Email-Versand und entfernt Token aus Response.
  - **Reset-Token-Salt-Separation**: `"eb-digital.user-password-reset"` ist bewusst ein anderer Salt als `"eb-digital.operation-url-token"` aus 2.3 — Token-Replay zwischen den Kontexten ist damit ausgeschlossen, auch bei gemeinsamem `secret_key` (Detail-Plan-Frage 4-A aus 2.3).
  - **`is_active=False` + leerer Hash für Pending-User**: Pragmatisch in Phase 1. Sauberer wäre eine `pending=True`-Spalte, aber das wäre eine Schema-Migration zusätzlich zum 2.4-Scope. Login-Pfad blockiert über `is_active=False` ohnehin korrekt; Argon2-Verify schlägt bei leerem Hash strukturell fehl (defensive Doppel-Sicherung).
  - **Tenant-Status-Check im Login-Pfad**: Notwendig, weil `register-tenant` vor Approve einen `applied`-Tenant erzeugt — eingeladene Dispatcher sollen erst nach Approve einloggen können. Edge-Case: Wenn ein Tenant deaktiviert wird, blockiert das **sofort** alle Dispatcher/Carer-Logins, auch wenn die Stammdaten noch nicht gelöscht sind (DSGVO-konformer Zugriffs-Stop).
  - **Audit-Log für Tenant-/User-Aktionen**: Regel-011 (Audit-Log-Pflicht) bezieht sich explizit auf **Operations**-Aktionen, nicht auf Tenants. Audit-Log für Tenant-Aktionen (Approve/Deactivate, Dispatcher-/Carer-Anlage) wäre ein methodisch sinnvoller Add-on, ist aber nicht 2.4-Pflicht. Für später (Phase 7-Stabilisierung) als Roadmap-Punkt notiert, hier nicht implementiert.
  - **DSGVO-Cascade-Löschung**: Dispatcher/Carer-FK auf Tenant ist `RESTRICT`. Beim Tenant-Deactivate werden in 2.4 keine Stammdaten gelöscht — die kaskadierende Anonymisierung läuft als Procrastinate-Job in `backend/retention` (Phase 6). Phase-1-`deactivated`-Status ist ausreichend für Login-Block.
  - **Username-Validierung**: analog zur Slug-Validierung, aber lockerer (3–32 Zeichen, `^[a-zA-Z0-9_.-]+$`, keine Reserved-Liste — Username ist Tenant-scoped, also kein globaler Konflikt-Vektor).
  - **Reset-Token-TTL 24 h**: Pragmatisch. Plattform-Admin oder Dispatcher hat einen Tag, den Token weiterzugeben. Bei Ablauf: Re-Invite (Endpoint nochmal aufrufen, neuer Token).

#### 2.5: frontend-disponent Login-Flow + Dashboard-Skelett

- **Status:** ERLEDIGT (2026-05-15; Detail-Plan-Freigabe Patrick 2026-05-14: alle fünf Detail-Fragen wie empfohlen).
- **Phasentyp-Kontext:** UMSETZUNG (Phase-2-Sonderregel: berührte Module bleiben `[VORLÄUFIG]`, Reifegrad-Beförderung des Architektur-Patterns folgt in Phase 6 nach Last-Test — Detail-Frage 5-A).
- **Abhängigkeiten:** 2.1, 2.2, 2.4 (alle ERLEDIGT).
- **Freigabepflichtig:** ja (Detail-Plan + Architektur-Wirkung Frontend-Auth-Integration). Detail-Plan-Freigabe Patrick 2026-05-14: Frage 1-B / 2-A / 3-A / 4-B / 5-A.
- **Eingangskriterien:**
  - Schnittstelle S8a (`/api/auth/login`, `/api/auth/me`, `/api/auth/logout`) `[BELASTBAR]` seit 2026-05-10 ✓
  - Schnittstelle S8b (`/api/tenants`, `/api/auth/register-tenant`, `/api/auth/reset-password`) `[BELASTBAR]` seit 2026-05-12 ✓
  - `frontend-disponent`-Skelett aus Schritt 1.7 vorhanden (SvelteKit 2.59, Svelte 5.55, TypeScript 6.0.3, adapter-static, vitest 4.1) ✓
- **Zu tun:**
  - **Routing-Architektur:** Route-Gruppen `(public)/` und `(authed)/` in `apps/frontend-disponent/src/routes/`. `(public)/login/+page.svelte`, `(public)/reset-password/+page.svelte` ohne Auth-Guard; `(authed)/+layout.ts` als zentraler Guard via `fetch('/api/auth/me')`, redirect auf `/login?next=<aktueller-Pfad>` bei 401; `(authed)/dashboard/+page.svelte` als Tenant-Übersicht.
  - **Session-Store** (`src/lib/stores/session.ts`): reine TS-Datei (kein `$state`-Rune, weil Reaktivität von außen via `LayoutData` bereits getragen wird und der Store dann ohne Svelte-Compiler im vitest-Setup testbar bleibt). Funktionen `setSession()`, `clearSession()`, `getSession()`, `isAuthenticated()`. In-Memory only (Detail-Frage 3-A): kein localStorage/sessionStorage. HttpOnly-Cookie ist die alleinige persistente Quelle der Wahrheit; Hard-Refresh re-hydriert über `/api/auth/me`.
  - **API-Client** (`src/lib/api/client.ts`): Wrapper um `fetch()` mit `credentials: 'include'`-Default, einheitlichem Error-Mapping (`{ kind: 'auth' | 'rate-limit' | 'forbidden' | 'not-found' | 'gone' | 'validation' | 'network', message, retryAfter? }`). Baseurl `''` (relativer Pfad) — funktioniert mit Vite-Dev-Proxy und Caddy-Production gleichermaßen. Helpers: `apiGet`, `apiPost`.
  - **Auth-API-Bindings** (`src/lib/api/auth.ts`): `login(username, password)`, `logout()`, `me()`, `resetPassword(token, newPassword)`. Typ-Definitionen für `SessionUserResponse` analog Backend.
  - **Tenants-API-Bindings** (`src/lib/api/tenants.ts`): `listTenants(status?: 'applied' | 'active' | 'deactivated')` mit Response-Typ `TenantResponse`.
  - **Login-Route** (`(public)/login/+page.svelte`): Formular mit Username + Password + Submit. Submit ruft `auth.login()`, bei Erfolg: Store setzen, redirect zum `next`-Query-Param oder `/dashboard`. Bei 401: generische Fehlermeldung „Ungültige Anmeldedaten oder Mandant nicht aktiv". Bei 429: Hinweis mit `Retry-After` (sofern Header verfügbar), Submit-Button disabled mit Countdown. Bei Network-Fehler: „Server nicht erreichbar".
  - **Reset-Password-Route** (`(public)/reset-password/+page.svelte`): Token aus `?token=...`-Query-Param; Formular „Neues Passwort + Bestätigung". Mindest-Länge 12 Zeichen (clientseitig validiert, Backend ist die Autorität). Submit ruft `auth.resetPassword(token, newPassword)`. Bei 204: Erfolgs-Meldung + Link zu `/login`. Bei 410: „Token ungültig, abgelaufen oder bereits verwendet — bitte Plattform-Admin oder Dispatcher um neuen Token bitten".
  - **Dashboard-Route** (`(authed)/dashboard/+page.svelte`): zwei Sektionen.
    - **Mandanten-Übersicht:** Tabelle aus `listTenants()` (für PlatformAdmin: alle Tenants mit `?status=active` als Default; für Dispatcher: eigener Tenant). Spalten Name / Slug / Status-Badge / Aktivierungs-Datum. Status-Badge farblich codiert (applied=gelb, active=grün, deactivated=grau).
    - **Aktive Einsätze:** Platzhalter-Text „Keine aktiven Einsätze" mit Sub-Hinweis „Operations-Funktionalität folgt in Phase 4" (Detail-Frage 2-A).
    - **Carer-Sicht:** falls `session.kind === 'carer'`, statt Dashboard ein Hinweistext „Phase 2 stellt für die Carer-Rolle noch keinen Dashboard-Zugriff bereit" + Logout-Button.
  - **`(authed)/+layout.svelte`:** Top-Bar mit Username + Rolle + Logout-Button. Logout ruft `auth.logout()` + `clearSession()` + redirect `/login`.
  - **`(authed)/+layout.ts`:** ruft beim Mount `auth.me()`; bei Erfolg setzt Session-Store; bei 401 redirect `/login?next=<aktueller-Pfad>`. Bei Network-Fehler: Fehler-Seite mit Retry-Button (kein automatischer Redirect, weil Cookie eventuell gültig ist).
  - **Vite-Dev-Proxy** in `apps/frontend-disponent/vite.config.ts`: `/api`-Pfade auf `http://localhost:8000` (Backend-Container im Compose-Stack) proxen, damit Cookies same-origin laufen. `changeOrigin: true`, `secure: false` (lokales Dev-Setup).
  - **Tests** (vitest + @testing-library/svelte als Devdependency hinzufügen, falls noch nicht): Unit-Tests für `session.ts` Store (set/get/clear), `client.ts` Error-Mapping, `auth.ts`/`tenants.ts` mit gemocktem `fetch`. Route-Component-Tests sind in Phase 2 optional, weil Playwright-E2E in Phase 7 die Integration-Coverage erbringt.
  - **Frontend-Smoke-Block** in `scripts/dev-smoke.sh`: nach Backend-Tenants-Block neue Sektion mit `pnpm --filter frontend-disponent build` (statischer Build muss durchlaufen) + curl-basiertem Cookie-Round-Trip (Login als Plattform-Admin → `/api/auth/me` → `/api/tenants` → Logout → erneuter `/api/auth/me` muss 401 liefern). Keine Browser-Automatisierung; reine Backend-API-Smoke aus Frontend-Sicht.
- **Akzeptanzkriterien:**
  - **AC-1 bis AC-6 (Login-Pfad):**
    - AC-1: `GET /login` rendert Formular clientseitig, öffentliche Route.
    - AC-2: Erfolgreicher `POST /api/auth/login` setzt Cookie, navigiert nach `/dashboard` (oder `next`-Query-Param).
    - AC-3: Fehlgeschlagener Login (401) zeigt generische Fehlermeldung, keine Unterscheidung wrong-username/-password/disabled-tenant.
    - AC-4: Rate-Limit-Erreichen (429) zeigt Hinweis mit `Retry-After`-Auswertung, Submit-Button disabled.
    - AC-5: Bereits authentifizierter Aufruf von `/login` redirected nach `/dashboard`.
    - AC-6: Hard-Refresh innerhalb der Session lädt User über `/api/auth/me`; bei 401 redirect `/login`.
  - **AC-7 bis AC-12 (Dashboard / Mandanten-Übersicht):**
    - AC-7: `GET /dashboard` Login-pflichtig; unauthentifiziert → redirect `/login?next=/dashboard`.
    - AC-8: `GET /api/tenants` wird geladen; PlatformAdmin sieht alle, Dispatcher sieht eigenen Tenant.
    - AC-9: Mandanten-Tabelle mit Name/Slug/Status-Badge/Aktivierungs-Datum gerendert.
    - AC-10: Carer-Login auf `/dashboard` zeigt Hinweisseite ohne Tenant-Liste, mit Logout-Button.
    - AC-11: Platzhalter „Keine aktiven Einsätze" + Phase-4-Sub-Hinweis sichtbar.
    - AC-12: Logout-Button ruft `POST /api/auth/logout`, leert Store, redirect `/login`.
  - **AC-13 bis AC-15 (Reset-Password-Flow):**
    - AC-13: `/reset-password?token=...` rendert Formular; ohne Token-Query: Hinweistext „Token fehlt".
    - AC-14: Submit mit gültigem Token + 12-Zeichen-Passwort → 204 → Erfolgsmeldung + Link `/login`.
    - AC-15: Submit mit abgelaufenem/ungültigem/Replay-Token → 410 → einheitliche Fehlermeldung ohne Info-Leak.
  - **AC-16 bis AC-17 (Architektur & Qualität):**
    - AC-16: Route-Gruppen `(public)/`/`(authed)/` strukturieren Routing; `(authed)/+layout.ts` ist zentraler Auth-Guard.
    - AC-17: Coverage `frontend-disponent` ≥ 80 % Lines/Branches (Standard); CI-Pipeline grün (lint + format-check + svelte-check + tsc + vitest + build); `scripts/dev-smoke.sh` Frontend-Block läuft erfolgreich gegen den Compose-Stack.
- **Betroffene Module:** `frontend-disponent` (primär). Keine Backend-Änderung (Detail-Frage 2-A).
- **Reifegrad-Wirkung:**
  - `frontend-disponent` bleibt `[VORLÄUFIG]` (Skelett-Erweiterung; Funktions-Validierung erfolgt, Last-Validierung steht aus — Phase-2-Sonderregel).
  - Architektur-Pattern „Modular Monolith + 3 SvelteKit-Frontends + 2 Proxies" bleibt `[VORLÄUFIG]` (Detail-Frage 5-A: Beförderung erst nach Phase-6-Last-Test).
  - Keine neue Schnittstelle, keine neue Sub-Surface (Detail-Frage 2-A).
- **Artefakte:**
  - **Frontend:** `src/lib/stores/session.ts`, `src/lib/api/{client.ts, auth.ts, tenants.ts}`, `src/routes/(public)/login/+page.svelte`, `src/routes/(public)/reset-password/+page.svelte`, `src/routes/(authed)/+layout.{ts,svelte}`, `src/routes/(authed)/dashboard/+page.svelte`, ggf. `src/routes/+page.svelte`-Anpassung (Redirect von `/` nach `/login` oder `/dashboard`), `vite.config.ts`-Erweiterung mit Dev-Proxy.
  - **Tests:** `tests/session.test.ts`, `tests/api-client.test.ts`, `tests/api-auth.test.ts`, `tests/api-tenants.test.ts`.
  - **Smoke:** `scripts/dev-smoke.sh`-Erweiterung mit Frontend-Smoke-Block.
  - **Doku-Updates zu Sessionende:** `architecture.md` Abschnitt 9 + ggf. Modul-Eintrag, `README.md` Status-Block + Nächste-Schritte, `logbuch.md` `[SESSIONENDE]`, `fahrplan.md` Aktueller-Stand + Schritt-Status.
- **Notizen:**
  - **`adapter-static`-Implikation:** Keine SvelteKit-Server-Routes, keine `+page.server.ts`, keine Form-Actions. Alle Auth-Operationen sind clientseitige `fetch()`-Aufrufe gegen `/api/...`. In Production proxen Caddy + nginx; in Dev kümmert sich der Vite-Proxy.
  - **CSRF-Schutz:** Cookies sind `SameSite=Strict` + `HttpOnly` + `Secure` (aus 2.2 produktiv). Das reicht in Phase 2; Anti-CSRF-Token via Synchronizer-Pattern ist Phase-7-Stabilisierungs-Aufgabe (externe Security-Review).
  - **Coverage-Pflicht-Schwelle Frontend:** Standard 80 % laut `project-context.md` Abschnitt 7. Keine speziellen Auth-Frontend-Schwellen (Backend-Auth ≥ 95 % bleibt eigene Sache des Backend-Modul). Selbst-Auferlegung von 95 % für `session.ts` und `client.ts` wäre verlockend, ist aber nicht Pflicht — angestrebt wird hohe Coverage durch klein gehaltene Module.
  - **Operations-Platzhalter:** Detail-Frage 2-A → kein Backend-Call für Operations. Phase 4 erweitert `backend/operations` + Frontend-Verdrahtung gemeinsam.
  - **Self-Service-Antrag + Admin-Approve-/Invite-UI:** bewusst draußen (Detail-Frage 1-B). Self-Service ist Public-Landing-Asset und gehört zu Roadmap-Meilenstein P (schriftliche Onboarding-Unterlagen, Phase 7); Admin-Approve-/Invite-UI folgt sobald `frontend-einsatzkraft` (2.6) den AccessCode-Eingabe-Flow trägt — vorher fehlt operative Notwendigkeit.

#### 2.6–2.7: Folgeschritte (gröber)

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
