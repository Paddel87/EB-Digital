# Fahrplan

<!-- Zentrales Arbeitsdokument. Wird vor jeder Änderung gelesen (CLAUDE.md Abschnitt 2)
     und nach jedem Arbeitsschritt sowie zu Sessionende aktualisiert (Abschnitt 12).
     Phasen sind nach Typ klassifiziert (Erkundung / Umsetzung / Stabilisierung),
     weil iterative Entwicklung unterschiedliche Erfolgskriterien pro Phasentyp braucht. -->

## Aktueller Stand

- **Stand vom:** 2026-05-28
- **Laufende Phase:** **Phase 4 (UMSETZUNG)** läuft seit 2026-05-28. Schritt **4.2** (`backend/fleet`) **IN ARBEIT** seit 2026-05-28 — Detail-Plan freigegeben 0A/1A/2A/3B/4B/5B/6A/7A/8A (9 Designfragen analog 4.1-Disziplin). Schritt 4.1 (`backend/catalog`) **ERLEDIGT** am 2026-05-28 — drei Tabellen + Repository + Use-Cases + Resolver + vier Rollen-API; Migration `b3a9c7e1f205` mit `alembic check` deckungsgleich zum ORM verifiziert; 55 Catalog-Tests + 495 Gesamt-Tests grün; Coverage 88 %; dev-smoke.sh-Catalog-Stufe mit 9 Sub-Checks E2E grün. ADR-019 fixiert Phase-4-Sonderregel. Phase 3 (3.1 ERLEDIGT 2026-05-18 durch ADR-017; 3.2 ERLEDIGT 2026-05-28 durch ADR-018) **abgeschlossen**.
- **Phasentyp:** **Phase 4** (UMSETZUNG) laufend. **Phase 3** (ERKUNDUNG) abgeschlossen.
- **Erledigte Schritte Phase 2 (alle ERLEDIGT):** **2.7 [ERLEDIGT]** 2026-05-16 (Phase-2-Abschluss: Coverage-Frischlauf verifiziert die Modul-Schwellen aller belastbaren Module — Backend 95.84 % gesamt, `backend/auth` 96 %, `backend/auth_anonymous` 100 %, `backend/tenants` 95–100 %; Frontend-Disponent 96.61 % Lines / 93.33 % Branches, Frontend-Einsatzkraft 98.38 % Lines / 95.55 % Branches; GitHub-Issue `Paddel87/EB-Digital#26` für externe Security-Review Phase 7.2 mit Briefing-Form angelegt; keine Code-Änderung, keine ADR-Pflicht; Detail-Plan A/A/A/A/A freigegeben). **2.6 [ERLEDIGT]** 2026-05-16 (`frontend-einsatzkraft` AccessCode-Eingabe-UI produktiv gegen S2a; 47 Vitest-Tests grün). **2.5 [ERLEDIGT]** 2026-05-15 (`frontend-disponent` Login + Dashboard + Reset-Password-UI produktiv; 27 Vitest-Tests grün). **2.5b [ERLEDIGT]** 2026-05-16 (Hot-Stabilisierung `get_db_session()` als yield-Dependency mit Rollback, ADR-015, Regel-018). **2.4 [ERLEDIGT]** 2026-05-12 (`backend/tenants` produktiv mit S10). **2.3 [ERLEDIGT]** 2026-05-11 (`backend/auth_anonymous` produktiv). **2.2 [ERLEDIGT]** 2026-05-10 (Login + Cookie-Sessions + Rate-Limit produktiv, ADR-013). **2.1 [ERLEDIGT]** 2026-05-10 (Datenmodell-Skelett). Phase 1 vollständig **ERLEDIGT** (1.1–1.8).
- **Aktiver Schritt:** keiner. Schritt **4.1** `backend/catalog` ERLEDIGT 2026-05-28; **4.2** `backend/fleet` ist nächster.
- **Erledigte Schritte Phase 3 (alle ERLEDIGT):** **3.2 [ERLEDIGT]** 2026-05-28 — Spike J durch ADR-018 (manuell durch Disponent, eigene `order_bundle`-Entity + nullable FK-Spalten `order.bundle_id` und `order_assignment.bundle_id`, Versorgungs-Transporter `mode='large_order'` Pflicht, keine räumliche Backend-Validierung, Min-2-Orders-Constraint, `bundling_count` Aktion-Semantik plus additive ADR-006-Erweiterung `bundled_order_count`; Detail-Plan A/A/A/A/A freigegeben; 11-Eintrag-Test-Datensatz inline im ADR). **3.1 [ERLEDIGT]** 2026-05-18 — Spike I durch ADR-017 (Hülle-Distanz + dynamische GPS-Toleranz `2·accuracy_m`, 500-m-Moderationsfilter, Text-Standort als Moderation, dreistufige Konfigurations-Hierarchie). Reifegrad-Wirkung: zwei `[OFFEN]`-Bereiche in `backend/operations` und `backend/geo` (`PlausibilityChecker`) auf `[VORLÄUFIG]` befördert (3.1) plus `[OFFEN]`-Bereich „Bündelungs-Trigger" in `backend/operations` auf `[VORLÄUFIG]` (3.2). Reaktiv-Quote 1/10 = 10 % (jetzt ADR-009 bis ADR-018).
- **Nächster Schritt:** **4.2** `backend/fleet` (Fahrzeuge, Beladung, Versorgungs-Transporter-Modi). Detail-Plan-Vorlage analog zur 4.1-Disziplin (Designfragen mit Optionen + Patrick-Freigabe als Buchstaben-Kombi vor Code-Eingriff).
- **Phase-3-Bilanz (Reifegrad-Beförderungen):** PlausibilityChecker in `backend/geo` und `backend/operations` `[OFFEN]` → `[VORLÄUFIG]` (3.1, ADR-017). Bündelungs-Trigger-Bereich in `backend/operations` `[OFFEN]` → `[VORLÄUFIG]` (3.2, ADR-018). Schnittstelle S4 offene Frage „Bündel-Mapping" gelöst durch ADR-018. Verbleibender `[OFFEN]`-Bereich in `backend/operations` ist nur Spike K (Hilfe-Knopf-Semantik, Phase 5), blockiert den Hilfe-Knopf-Pfad in Phase 6 — nicht Phase 4. Reaktiv-Quote 1/10 = 10 % (beide ADRs `[ERKENNTNIS]`, kein `[REAKTIV]`). Beförderungs-Pflicht (`project-context.md` §6 Methodik-Schwellenwerte) erfüllt: zwei `[OFFEN]`-Bereiche der berührten Module auf `[VORLÄUFIG]` befördert.
- **Phase-2-Bilanz (Reifegrad-Beförderungen):** `backend/auth` → `[BELASTBAR]` (2.2), `backend/auth_anonymous` → `[BELASTBAR]` (2.3), `backend/tenants` → `[BELASTBAR]` (2.4), Request-Scoped DB-Session-Dependency → `[BELASTBAR]` (2.5b, cross-cutting). Schnittstellen: S2a, S8a, S8b → `[BELASTBAR]`; S10 → `[BELASTBAR]`. Datenmodelle: `anonymous_session` + `operation.url_token`-Widening → `[BELASTBAR]`. Invarianten I1, I2 → `[BELASTBAR]`. Frontends `frontend-disponent` und `frontend-einsatzkraft` funktional validiert (Reifegrad bleibt `[VORLÄUFIG]` bis Phase-6-Last-Test). Reaktiv-Quote 1 / 10 = 10 % (ADR-015 Hot-Stabilisierung 2.5b — unter 20 %-Schwellenwert Klasse G).
- **Offene STOPP-Situationen:** keine.
- **Aktive Blocker:** **0** (Blocker #001 am 2026-05-10 ursächlich aufgeklärt — siehe [`docs/blockers.md`](blockers.md) und [`scripts/fix-venv-flags.sh`](../scripts/fix-venv-flags.sh)).
- **CI-Hygiene-Sonderfall in Phase 1 (2026-05-10):** ADR-012 — `actions/upload-artifact@v4` → `@v7` als Major-Update gegen Node-20-Deprecation, analog zu ADR-010 in 1.2. Reaktiv-Quote bleibt 0 / 10.
- **Strategische Klarstellung zwischen 2.1 und 2.2 (2026-05-10):** ADR-014 — Anbieter-Austauschbarkeit für externe Geo-Services als Architektur-Prinzip + Regel-017. Außerhalb der Schritt-Sequenz, dokumentations-only (kein Code-Eingriff). Reaktiv-Quote bleibt 0 / 10. Keine Auswirkung auf Schritt-2.2-Plan; jedoch ursprünglich erweiterte Eingangsbedingung für Phase 6 (MapTiler-Sales-Approval für serverseitigen Cache). **Update 2026-05-17:** Eingangsbedingung obsolet durch **ADR-016 (Verzicht auf serverseitiges Caching)** — Patrick-Direktive 2026-05-17 zugunsten architektur-sauberer Lösung. Phase-7-Roadmap-Meilenstein „MapTiler-Sales-Anfrage" entfällt; Pfad bleibt nach ADR-014/Regel-017 als Eskalations-Option offen, falls Phase-7-Lasttest (7.1) das Budget reißt.

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

| Phase | Titel                                                                   | Typ                   | Spikes / Roadmap  | Status                                                                                                                                                  |
| ----- | ----------------------------------------------------------------------- | --------------------- | ----------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1     | Repository-Bootstrap & Tech-Foundations                                 | UMSETZUNG             | –                 | ERLEDIGT (1.1–1.8 erledigt 2026-05-10)                                                                                                                  |
| 2     | Auth + Tenants + Verbund-Tauglichkeit                                   | UMSETZUNG             | –                 | ERLEDIGT (2.1+2.2 ERLEDIGT 2026-05-10, 2.3 ERLEDIGT 2026-05-11, 2.4 ERLEDIGT 2026-05-12, 2.5 ERLEDIGT 2026-05-15, 2.5b + 2.6 + 2.7 ERLEDIGT 2026-05-16) |
| 3     | Spikes Wave 1 – Operations-Vorklärungen                                 | ERKUNDUNG             | I, J              | ERLEDIGT (3.1 ERLEDIGT 2026-05-18 / ADR-017, 3.2 ERLEDIGT 2026-05-28 / ADR-018)                                                                         |
| 4     | Operations Core + Realtime + Einsatzkraft-PWA                           | UMSETZUNG             | –                 | LÄUFT (4.1 IN ARBEIT seit 2026-05-28; Detail-Plan freigegeben; ADR-019 Sonderregel)                                                                     |
| 5     | Spikes Wave 2 – Geo, Frontends, Resilience, Roll-out                    | ERKUNDUNG             | G, H, K, L, M     | OFFEN                                                                                                                                                   |
| 6     | Geo + Disponent-/Betreuer-PWAs + Resilience + Retention + Export        | UMSETZUNG             | –                 | OFFEN                                                                                                                                                   |
| 7     | Stabilisierung, Roll-out-Vorbereitung, Validierung                      | STABILISIERUNG        | – (Roadmap N/O/P) | OFFEN                                                                                                                                                   |
| X     | Verbund-Modus für parallele Mandanten-Großlagen _(spätere Erweiterung)_ | ERKUNDUNG → UMSETZUNG | (eigener Spike)   | OFFEN                                                                                                                                                   |

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

#### 2.5b: Hot-Stabilisierung — `get_db_session()` Lifecycle-Bug (yield-Dependency + Rollback)

- **Status:** ERLEDIGT (2026-05-16; Freigabe Patrick 2026-05-15: Option A; **kein** Unit-of-Work-Wechsel; Endpoint-Commits bleiben erhalten).
- **Phasentyp-Kontext:** UMSETZUNG (außerplanmäßiger Hot-Stabilisierungs-Schritt zwischen 2.5 und 2.6, analog ADR-014-Einschub zwischen 2.1 und 2.2).
- **Abhängigkeiten:** keine (behebt einen latenten Cross-Cutting-Bug in `backend/auth.api.get_db_session`, der von `backend/auth`, `backend/auth_anonymous` und `backend/tenants` konsumiert wird).
- **Freigabepflichtig:** ja (Methodik-Regelergänzung Regel-018 + reaktiver ADR-015). Freigabe erfolgt 2026-05-15 mit dieser Session.
- **Eingangskriterien:** Bug-Diagnose und Optionswahl Patrick freigegeben (Option A); aktive `[BELASTBAR]`-Module bleiben funktional unverändert (öffentliche API-Verträge unberührt; nur Lifecycle-Semantik der Dependency).
- **Zu tun:**
  - **Code-Fix** in [backend/eb_digital/auth/api.py](backend/eb_digital/auth/api.py): `get_db_session(request)` von `async def → AsyncSession` auf `async def → AsyncIterator[AsyncSession]` umstellen mit Muster `async with factory() as session: try: yield session except Exception: await session.rollback(); raise`. Keine Änderung an Endpoints; bestehende explizite `await db.commit()`-Aufrufe in Endpoints bleiben erhalten (Patrick-Direktive: kein Unit-of-Work in 2.5b).
  - **Lifecycle-Tests** in [backend/tests/test_auth_login_api.py](backend/tests/test_auth_login_api.py):
    - bestehenden `test_get_db_session_invokes_factory_and_returns_session` zu echtem Lifecycle-Test umschreiben (Stub mit Counter für `__aenter__`/`__aexit__`/`rollback`/`close`; Verifikation: Enter vor Yield, Exit nach Consumer-Abschluss);
    - **neuer Exception-Pfad-Test:** Konsument wirft Exception nach Yield → Verifikation `rollback()` aufgerufen, `__aexit__` lief, Exception propagiert.
  - **`scripts/dev-smoke.sh`** um Exception-Fall-Probe ergänzen: `register-tenant` mit kollidierender Slug (existiert nach erstem Aufruf) → 409 + Folge-Request `/api/health` muss innerhalb 1 s antworten (kein Pool-Stall durch Connection-Leak im Exception-Pfad).
  - **ADR-015** `[REAKTIV] [STACK] [SECURITY]` in `decisions.md` Teil B + Eintrag in Teil A. **Reaktiv-Quote** auf 1/10 = 10 % aktualisieren (unter 20-%-Schwellenwert für Klasse G).
  - **Regel-018** in `decisions.md` Teil C ergänzen: „FastAPI-Resource-Dependencies mit Context-Manager nutzen `yield`, nicht `return`".
  - **`architecture.md`** Modul-Einträge `backend/auth`, `backend/auth_anonymous`, `backend/tenants` um Hinweis „Request-Scoped DB-Session (yield-Dependency, Rollback bei Exception)" als interne Garantie ergänzen; Reifegrade unverändert.
  - **`logbuch.md`**: `[PROBLEM-GELÖST]`-Eintrag (Bug-Diagnose + Fix-Verifikation), `[ADR-ANGELEGT]` (ADR-015 + Regel-018), `[SESSIONENDE]`.
- **Akzeptanzkriterien:**
  - **AC-1:** `get_db_session` ist als async-Generator (yield) implementiert mit explizitem Rollback im Exception-Pfad; mypy --strict grün.
  - **AC-2:** Lifecycle-Test verifiziert `__aenter__` vor Yield und `__aexit__` nach Consumer-Abschluss (nicht vorher).
  - **AC-3:** Exception-Pfad-Test verifiziert `rollback()` wird vor `__aexit__` aufgerufen, Exception propagiert unverändert.
  - **AC-4:** Bestehende Backend-Suite (439 + 1 skipped) bleibt grün; Coverage `backend/auth` ≥ 95 % Lines/Branches.
  - **AC-5:** dev-smoke.sh Exception-Fall-Probe (Slug-Kollision → 409 → Folge-`/api/health`) grün.
  - **AC-6:** ADR-015 + Regel-018 dokumentiert; Reaktiv-Quote auf 1/10 = 10 % aktualisiert (unter Schwellenwert).
  - **AC-7:** Pflicht-Pre-Commit-Hooks grün (ruff lint+format, ruff format-check, mypy --strict, bandit, pytest).
- **Betroffene Module:** `backend/auth` (Code-Fix in der Dependency-Definition); konsumierende Module `backend/auth_anonymous` und `backend/tenants` (keine Code-Änderung, aber Architektur-Spec-Hinweis).
- **Reifegrad-Wirkung:**
  - Modul-Reifegrade bleiben `[BELASTBAR]` (Lifecycle-Bug war bereits Bestandteil des Querschnitts — Fix bestätigt die request-scoped Architektur-Absicht, kippt sie nicht).
  - Neuer architektur-belastbarer Eintrag „Request-Scoped DB-Session-Dependency" als Modul-übergreifendes Muster (BELASTBAR seit Fix-Datum).
- **Artefakte:**
  - **Code:** `backend/eb_digital/auth/api.py` (Funktion `get_db_session`).
  - **Tests:** `backend/tests/test_auth_login_api.py` (umgeschriebener Lifecycle-Test + neuer Exception-Pfad-Test).
  - **Smoke:** `scripts/dev-smoke.sh` Exception-Fall-Probe.
  - **Doku:** `decisions.md` (ADR-015, Regel-018, Reaktiv-Quote in Teil A), `architecture.md` (drei Modul-Einträge), `fahrplan.md` (dieser Schritt), `logbuch.md`, `README.md` (nur falls Status-Block-Drift entsteht).
- **Notizen:**
  - **Keine Unit-of-Work-Umstellung** in diesem Schritt (Patrick-Direktive). Endpoint-`await db.commit()`-Calls bleiben unverändert. Eine spätere zentrale Commit-/Rollback-Strategie wäre eigener `[STRATEGISCH]`-ADR mit eigenem Schritt.
  - **Real-DB-Integrationstest:** Eine neue Top-Level-Test-Dep wie `aiosqlite` oder `testcontainers` wäre freigabepflichtig (Regel-001 + Regel-016) und nicht durch Option A gedeckt. Stattdessen: **dev-smoke.sh** liefert die Real-DB-Validierung gegen echtes PostgreSQL im Compose-Stack; Lifecycle-Stubs decken die FastAPI-yield-Semantik unit-test-seitig.

#### 2.6: frontend-einsatzkraft AccessCode-Eingabe-UI — Typ: UMSETZUNG

- **Status:** ERLEDIGT (2026-05-16; alle 16 Akzeptanzkriterien erfüllt; Detail-Plan-Freigabe Patrick 2026-05-16: alle fünf Detail-Fragen wie empfohlen).
- **Phasentyp-Kontext:** UMSETZUNG (Phase-2-Sonderregel: berührtes Modul bleibt `[VORLÄUFIG]`, Reifegrad-Beförderung des Architektur-Patterns folgt mit Phase-6-Last-Test analog 2.5).
- **Abhängigkeiten:** 2.3 ERLEDIGT (`backend/auth_anonymous` produktiv, S2a `[BELASTBAR]`); 2.5 ERLEDIGT (Frontend-Pattern aus `frontend-disponent`: `client.ts`, Rate-Limit-Countdown-UX, In-Memory-Session-Cache, Vite-Dev-Proxy); 2.5b ERLEDIGT (yield-Dependency stabilisiert die S2a-Endpunkte). `frontend-einsatzkraft`-Skelett aus Schritt 1.7 vorhanden (SvelteKit 2.59, Svelte 5.55, TS 6.0.3, adapter-static, vitest 4.1, vite-plugin-pwa 1.3).
- **Freigabepflichtig:** ja (Detail-Plan + Architektur-Wirkung Frontend-Auth-Integration). Detail-Plan-Freigabe Patrick 2026-05-16: 1-A / 2-A / 3-A / 4-B / 5-A.
- **Eingangskriterien:**
  - Schnittstelle S2a (`/api/anon/{operation_url}/info`, `/api/anon/{operation_url}/session`) `[BELASTBAR]` seit 2026-05-11 ✓
  - Request-Scoped DB-Session-Dependency `[BELASTBAR]` seit 2026-05-16 (Hot-Stab 2.5b) ✓ — sichert die S2a-Endpunkte gegen Connection-Leaks im Exception-Pfad.
  - `frontend-einsatzkraft`-Skelett aus Schritt 1.7 vorhanden ✓
  - Patrick-Freigabe Detail-Plan 2026-05-16: 1-A / 2-A / 3-A / 4-B / 5-A ✓
- **Zu tun:**
  - **Routing-Architektur (Detail-Frage 1-A):** Token als Pfad-Segment `/[token]/+page.svelte`. Bestehendes `/+page.svelte` wird zur Landing-Erklärungsseite (Detail-Frage 2-A: keine manuelle URL-Eingabe). Nach erfolgreichem `POST /session` redirect auf separate Route `/[token]/dashboard/+page.svelte` (Detail-Frage 4-B). Dashboard-Route hat eigenen Auth-Guard (`+layout.ts`): bei leerem Session-Store → redirect zu `/[token]`.
  - **SvelteKit-SPA-Mode:** globalen `src/routes/+layout.ts` von `prerender = true; ssr = true;` auf `prerender = false; ssr = false;` umstellen — `/[token]` ist dynamische Route mit unbekanntem Parameter, kann nicht prerendered werden. `svelte.config.js`-Fallback `index.html` ist aus 1.7 bereits gesetzt. Begründungs-Kommentar im File.
  - **Session-Store** (`src/lib/stores/session.ts`): reine TS-Datei (kein `$state`-Rune; analog 2.5-Disponent-Pattern), In-Memory-Cache für `AnonymousSessionState = {sessionId, areaLabel, accessCodeActive}`. Funktionen `setSession()`, `clearSession()`, `getSession()`, `isActiveForToken(token)`. **Detail-Frage 3-A aus 2.5 analog:** HttpOnly-Cookie ist die alleinige persistente Quelle der Wahrheit; kein `localStorage`/`sessionStorage` (Vision-PII-Constraint + XSS-Defense-in-depth).
  - **API-Client** (`src/lib/api/client.ts`): Wrapper-Modul **1:1 aus `frontend-disponent` portiert** (credentials:'include', `ApiError`-Klasse, Status→Kind-Mapping, Retry-After-Parsing, `apiFetch`/`apiGet`/`apiPost`). Begründung der Duplikation: pnpm-Workspace ohne shared-Lib in Phase 2 (gleiche Argumentation wie ESLint-Inline-Config); shared-Modul wäre eigene Refactoring-Phase mit ADR.
  - **Anonymous-API-Bindings** (`src/lib/api/anonymous.ts`): `fetchInfo(token)` → `OperationInfo {area_label, access_code_active, status}`, `createSession(token, accessCode?)` → `AnonymousSessionResponse {session_id}`. Pfad-Konstruktor `/api/anon/${token}/info` und `/api/anon/${token}/session`. Body `{access_code: string | null}` für POST.
  - **AccessCode-Modul** (`src/lib/access-code.ts`): Pattern `^[0-9A-HJ-KM-NP-TV-Z]{6}$` (ADR-005, Crockford-Base32 ohne `I/L/O/U`), `normalize(input)` (Uppercase + Strip-Whitespace + Strip-Hyphen), `isValid(input)`, ALPHABET-Konstante. Auto-Uppercase erfolgt im Form-Component via `bind:value`-Filter — Live-Pattern-Test deaktiviert Submit-Button, kein Backend-Roundtrip bei offensichtlichem Tippfehler.
  - **Landing-Route** (`/+page.svelte` Ersatz): statische Erklärungsseite „Du brauchst eine Einsatz-URL, die du vom Disponenten erhalten hast (Link oder QR-Code)." Kein Eingabefeld, kein Scanner. Verweis auf den Health-Check (vorhanden) für interessierte Nutzer. (Detail-Frage 2-A — Vision-Constraint „niederschwellig / Erstaufruf-Größe minimal" schlägt Komfort.)
  - **Token-Route** (`/[token]/+page.svelte` neu + `/[token]/+layout.ts` neu): `+layout.ts` ruft `fetchInfo(token)`; bei 200 übergibt `{area_label, access_code_active, status}` an die Page; bei 404 setzt Fehler-State. Page rendert:
    - **404-Fall:** einheitliche Meldung „Diese Einsatz-URL ist nicht (mehr) gültig. Bitte beim Disponenten eine aktuelle URL anfordern." Kein Code-Form. Kein Info-Leak über Grund (forged vs. `planned` vs. `closed` — analog Backend-Verhalten).
    - **`access_code_active = true`:** Stadt-Label sichtbar; Code-Form mit `<input>` (autocomplete=off, inputmode=text, maxlength=6, autocapitalize=characters); Auto-Uppercase via `bind:value` mit Normalize-Filter; Submit-Button disabled bis `isValid(code)`; Live-Hinweis „6 Zeichen ohne I/L/O/U" bei ungültigem Pattern.
    - **`access_code_active = false`:** Stadt-Label sichtbar; einzelner „Anmelden"-Button; ruft `createSession(token, null)`.
    - **Submit-Behandlung:** POST /session — 201 → `setSession(...)` + `goto(/[token]/dashboard)` mit `replaceState: true`; 401 → „AccessCode ungültig" + Form bleibt; 410 → wechselt auf 404-Pfad-Meldung; 422 → „Format des Codes ungültig" (Defensive für Backend-Pattern-Verstoß trotz Client-Validation); 429 → Rate-Limit-Hinweis mit Retry-After-Countdown und disabled Submit (Wiederverwendung des 2.5-Disponent-Countdown-Patterns).
  - **Dashboard-Route** (`/[token]/dashboard/+layout.ts` neu + `/[token]/dashboard/+page.svelte` neu): `+layout.ts` prüft `isActiveForToken(params.token)`; falls falsch → `redirect(307, /[token])`. Page rendert: „Anmeldung erfolgreich" + Stadt-Label + Phase-4-Platzhalter „Bestellpfad und Karten-Anzeige folgen in Phase 4 (Operations Core)." Kein Logout-Button (Detail-Frage 5-A: Cookie-TTL 24 h aus 2.3 reicht; Backend-Logout-Endpunkt wäre S2-Erweiterung in Phase 4).
  - **Vite-Dev-Proxy** in `apps/frontend-einsatzkraft/vite.config.ts` ergänzen (analog 2.5): `/api`-Pfade auf `http://localhost:8000` (Backend-Container im Compose-Stack) proxen, damit Cookies same-origin laufen. `VITE_BACKEND_URL`-Override-Möglichkeit beibehalten. Bestehende `VitePWA`-Konfig bleibt unverändert.
  - **Vitest-Konfig** (`vitest.config.ts`): `$lib`-Alias auf `src/lib/` ergänzen (analog 2.5-Disponent), damit Tests `import { ... } from "$lib/..."` auflösen.
  - **ESLint-Flat-Config** (`eslint.config.js`): `browserGlobals`-Block analog 2.5-Disponent ergänzen (fetch, Response, Headers, document, window, setTimeout, setInterval, SubmitEvent, …) — sobald die Routes-Pages DOM-APIs verwenden, sind die Globals Pflicht.
  - **Tests** (vitest, 4 neue Test-Dateien):
    - `tests/api-client.test.ts` — analog 2.5-Disponent: Status→Kind-Mapping (alle 9 Kinds), Retry-After-Parsing, JSON-Body, Network-Fehler.
    - `tests/api-anonymous.test.ts` — `fetchInfo`/`createSession`-Calls mit gemocktem `fetch`: Pfad-Konstruktion, Body-Serialisierung (`access_code: null` vs. Code), Response-Parsing.
    - `tests/access-code.test.ts` — `normalize`, `isValid`, ALPHABET; Edge-Cases (Whitespace, Hyphen, Kleinschreibung, ungültige Zeichen, falsche Länge).
    - `tests/session.test.ts` — `setSession`/`clearSession`/`getSession`/`isActiveForToken`; Token-Bindung (Store für falschen Token gibt `false`).
  - **`scripts/dev-smoke.sh`-Erweiterung:** Einsatzkraft-Build-Block am Ende (vor dem Frontend-Disponent-Block oder danach): `pnpm --filter frontend-einsatzkraft build` muss durchlaufen (Service-Worker-Generation + adapter-static-Build mit SPA-Fallback). Backend-API-Smoke der S2a-Endpunkte ist durch den 2.3-Anon-Block bereits abgedeckt — keine Duplikation.
- **Akzeptanzkriterien (UMSETZUNG → funktionsbasiert, 16 Stück):**
  - **AC-1 bis AC-3 (Landing + Token-Route Initialization):**
    - AC-1: `GET /` rendert statische Erklärungsseite ohne Eingabefeld; öffentliche Route, kein Auth-Aufruf.
    - AC-2: `GET /[token]` ruft `GET /api/anon/{token}/info` beim Laden auf; bei 200 zeigt Stadt-Label und entscheidet anhand `access_code_active` Code-Form vs. direkter Submit.
    - AC-3: `GET /[token]` bei `/info`-404 einheitliche Meldung „Diese Einsatz-URL ist nicht (mehr) gültig." ohne Unterscheidung des Grunds.
  - **AC-4 bis AC-7 (AccessCode-Eingabe):**
    - AC-4: `access_code_active=true` zeigt Code-Form; Submit-Button disabled bis `isValid(code) == true` (Pattern `^[0-9A-HJ-KM-NP-TV-Z]{6}$`).
    - AC-5: Eingabe wird live auf Uppercase normalisiert; Live-Hinweis „6 Zeichen ohne I/L/O/U" bei ungültigem Pattern.
    - AC-6: `access_code_active=false` zeigt direkten „Anmelden"-Button ohne Code-Form; POST `/session` Body `{access_code: null}`.
    - AC-7: 422-Response zeigt „Format des Codes ungültig" als Defensive (Bypass durch Hand-crafted-Request).
  - **AC-8 bis AC-11 (Session + Fehlerpfade):**
    - AC-8: POST `/session` 201 → `setSession({session_id, area_label, access_code_active})` + `goto(/[token]/dashboard)` mit `replaceState: true`.
    - AC-9: POST `/session` 401 → „AccessCode ungültig" Fehlermeldung; Form bleibt offen, Counter +1 backend-seitig.
    - AC-10: POST `/session` 410 → einheitliche „URL nicht (mehr) gültig"-Meldung (Operation während Code-Eingabe geschlossen).
    - AC-11: POST `/session` 429 → Hinweis mit Retry-After-Countdown; Submit-Button disabled bis Ablauf.
  - **AC-12 bis AC-13 (Dashboard):**
    - AC-12: `GET /[token]/dashboard` ohne Session-Store-Eintrag (Hard-Refresh nach Tab-Verlust) → redirect 307 zu `/[token]`.
    - AC-13: `GET /[token]/dashboard` mit aktiver Session zeigt Stadt-Label und Phase-4-Platzhalter „Bestellpfad und Karten-Anzeige folgen in Phase 4 (Operations Core)."
  - **AC-14 bis AC-16 (Architektur & Qualität):**
    - AC-14: Coverage `frontend-einsatzkraft` ≥ 80 % Lines/Branches auf den getesteten `src/lib/`-Modulen (Standard-NFR aus `project-context.md` Abschnitt 7).
    - AC-15: CI-Pflicht-Gates grün: `pnpm --filter frontend-einsatzkraft lint`, `format:check`, `check` (svelte-check), `tsc`, `test`, `build`. Pre-Commit-Hooks (prettier, eslint, …) grün.
    - AC-16: `scripts/dev-smoke.sh` Einsatzkraft-Build-Block grün — `pnpm --filter frontend-einsatzkraft build` erfolgreich.
- **Betroffene Module:** `frontend-einsatzkraft` (primär). Keine Backend-Änderung — produktive S2a aus 2.3 ist die einzige Schnittstelle. Keine Änderung an `backend/auth_anonymous`, `backend/auth`, `backend/tenants`, `infra/*`.
- **Reifegrad-Wirkung:**
  - `frontend-einsatzkraft` bleibt `[VORLÄUFIG]` (Funktions-Validierung erfolgt, Last-Validierung steht bis Phase 6 aus — analog 2.5-Detail-Frage 5-A).
  - Schnittstelle S2a bleibt unverändert `[BELASTBAR]` (keine Vertragsänderung; nur erste Konsumenten-Implementation).
  - Architektur-Pattern „Modular Monolith + 3 SvelteKit-Frontends + 2 Proxies" bleibt `[VORLÄUFIG]` (Beförderung erst nach Phase-6-Last-Test, analog 2.5).
  - Keine neue Schnittstelle, kein neuer Sub-Surface-Eintrag.
- **Artefakte:**
  - **Frontend Quellcode:** `src/lib/api/client.ts`, `src/lib/api/anonymous.ts`, `src/lib/access-code.ts`, `src/lib/stores/session.ts` (neu); `src/routes/+layout.ts` (Modifikation: prerender/ssr=false), `src/routes/+page.svelte` (Aktualisierung: Landing-Inhalt), `src/routes/[token]/+layout.ts`, `src/routes/[token]/+page.svelte`, `src/routes/[token]/dashboard/+layout.ts`, `src/routes/[token]/dashboard/+page.svelte` (neu).
  - **Konfig:** `apps/frontend-einsatzkraft/vite.config.ts` (Dev-Proxy ergänzt); `vitest.config.ts` (`$lib`-Alias); `eslint.config.js` (Browser-Globals).
  - **Tests:** `tests/api-client.test.ts`, `tests/api-anonymous.test.ts`, `tests/access-code.test.ts`, `tests/session.test.ts` (neu).
  - **Smoke:** `scripts/dev-smoke.sh` Einsatzkraft-Build-Block.
  - **Doku zu Sessionende:** `architecture.md` Modul-Eintrag `frontend-einsatzkraft` (Validierungs-Status präzisieren), `README.md` Status-Block + Nächste-Schritte + Versions-Block falls nötig, `logbuch.md` `[SESSIONENDE]`, `fahrplan.md` Schritt 2.6 auf `[ERLEDIGT]`, Aktueller-Stand nachziehen.
- **Notizen:**
  - **`adapter-static`-SPA-Mode:** wie bei 2.5-Disponent. `/[token]` und `/[token]/dashboard` sind dynamische Routen ohne Vorab-Entries — `prerender = false; ssr = false;` global + `fallback: "index.html"` (vorhanden) reicht. Alternativ wäre eine `entries()`-Export, aber das ist für unbekannte Operation-Tokens nicht möglich (sie werden zur Laufzeit erzeugt).
  - **PWA-Service-Worker bleibt aktiv:** `vite-plugin-pwa` aus 1.7 unverändert. Runtime-Cache `/api/anon/*` mit NetworkFirst (4 h TTL) ist bereits in `vite.config.ts` konfiguriert — passt zur 2.6-Architektur (offline-fähige Nach-Anmelde-Ansichten in Phase 4 möglich).
  - **CSRF-Schutz:** Cookies sind `SameSite=Strict; HttpOnly; Secure` (aus 2.3 produktiv); Anti-CSRF-Token via Synchronizer-Pattern ist Phase-7-Stabilisierungs-Aufgabe (analog 2.5).
  - **Hard-Refresh-Verhalten auf `/[token]/dashboard`:** In-Memory-Store leer → redirect zu `/[token]`. User gibt Code neu ein → POST `/session` 201 (nicht idempotent laut S2-Spec, neue Session). Akzeptabler UX-Trade-Off: PWA-Tab bleibt typischerweise offen; Hard-Refresh-Recovery braucht 5-Sekunden Code-Wiederholung.
  - **AccessCode-Auto-Uppercase:** wirkt sowohl auf manuelle Eingabe (z. B. „x7k3pq" → „X7K3PQ") als auch auf Paste (z. B. „X7K-3PQ" → „X7K3PQ" durch Strip-Hyphen). Disziplin: Backend ist die Autorität; clientseitige Normalisierung dient UX, nicht Sicherheit.
  - **`access_code_active=false` und 422-Defensive:** Backend liefert 422 nur bei Pattern-Verstoß mit Pflicht-Code. Bei `access_code_active=false` wird Body `{access_code: null}` gesendet — wenn der Backend-Status zwischen `/info`-Antwort und `/session`-Submit auf `access_code_active=true` wechselt (Disponent-Toggle), könnten wir theoretisch 422 sehen. UX-Defensive: 422-Meldung weist auf Toggle hin („Format des Codes ungültig — bitte Seite neu laden und Code eingeben").
  - **Build-Smoke vs. Backend-API-Smoke:** Detail-Plan-Entscheidung — der Backend-API-Smoke der S2a-Endpunkte ist im 2.3-Anon-Block bereits vollständig (200/401/410). Eine UI-basierte E2E-Probe wäre Browser-Automatisierung (Playwright) und gehört zu Phase 7 (`project-context.md` Abschnitt 7: Playwright als STABILISIERUNG-Coverage).

#### 2.7: Tests + Coverage + Security-Review-Issue (Phase-2-Abschluss) — Typ: UMSETZUNG

- **Status:** ERLEDIGT (2026-05-16; Detail-Plan-Freigabe Patrick 2026-05-16: A/A/A/A/A für alle fünf Detail-Fragen).
- **Phasentyp-Kontext:** UMSETZUNG (Phase-2-Abschluss-Schritt; keine Code-Änderungen, reine Verifikation + Dokumentation + Issue-Erfassung).
- **Abhängigkeiten:** 2.1 + 2.2 + 2.3 + 2.4 + 2.5 + 2.5b + 2.6 ERLEDIGT; Phase-2-Coverage-Schwellen bereits durch die jeweiligen Schritte etabliert.
- **Freigabepflichtig:** ja — der Schritt war im Fahrplan nur als „2.7 Tests + Coverage; externe Security-Review als Issue erfasst (Phase 7)" angerissen und musste in dieser Session in volles Schritt-Format überführt werden. Detail-Plan mit fünf Fragen (Form der Issue, Coverage-Scope, Verifikation des Operation-Eröffnungs-Kriteriums, PR-Strategie, ADR-Bedarf) Patrick 2026-05-16 vorgelegt — Freigabe „A/A/A/A/A" (alle Empfehlungen).
- **Eingangskriterien:**
  - 2.1–2.6 (inkl. 2.5b) ERLEDIGT ✓
  - Backend-Suite 440 + 1 skipped grün (Stand 2.5b ✓, in 2.7 re-verifiziert)
  - Frontend-Suites 27/27 (Disponent) + 47/47 (Einsatzkraft) grün (Stand 2.5/2.6 ✓, in 2.7 re-verifiziert)
  - Detail-Plan-Freigabe Patrick 2026-05-16 ✓
- **Zu tun:**
  1. **Coverage-Frischlauf** gegen aktuelle `main` (HEAD `f7cd481`):
     - Backend: `uv run pytest backend/tests --cov=backend/eb_digital --cov-report=term-missing -q`
     - Frontend-Disponent: `pnpm --filter frontend-disponent exec vitest run --coverage`
     - Frontend-Einsatzkraft: `pnpm --filter frontend-einsatzkraft exec vitest run --coverage`
     - Snapshot der Ergebnisse in `logbuch.md` `[SESSIONENDE]`-Eintrag.
  2. **GitHub-Issue für externe Security-Review (Phase 7.2)** anlegen mit Briefing-Form gemäß Detail-Plan-Frage-1-A:
     - Scope: `backend/auth` + `backend/auth_anonymous` + `backend/tenants` + Rate-Limit-Schicht + Session-Handling + Regel-018-Pattern
     - Artefakt-Verweise: relevante Module/Dateien, ADR-004/005/007/008/009/013/015, Regel-005/006/007/010/011/013/014/018
     - Bedrohungsmodell-Anker zur Bestätigung oder Widerlegung
     - Erfolgskriterien: Findings-Klassifikation (CVSS o. ä.), Auflösungs-Pfad pro Severity, Abschluss-ADR-Pflicht in Phase 7.2
     - Out-of-Scope-Klärung (`backend/operations`, Frontends, Infra)
  3. **Fahrplan-Updates:**
     - Schritt 2.7 in volles Schritt-Format überführen (dieser Block).
     - Aktueller Stand: Phase 2 ERLEDIGT; nächste Phase: Phase 3 (Spikes Wave 1).
     - Phasen-Übersicht: Phase 2-Zeile auf ERLEDIGT.
     - Phase-2-Reflexions-Eintrag im Abschnitt „Iterations-Reflexion" mit Beobachtungen zu Reaktiv-Quote, Coverage-Trajektorie, Phase-2-Sonderregel-Wirkung.
  4. **README-Sync:**
     - Status-Block: Letzte Änderung, Phase-Status, „Nächste Schritte" auf Phase 3 (Spike I + Spike J) umstellen.
  5. **Logbuch-Sessionende-Eintrag** mit Coverage-Snapshot, Issue-Verweis, Phase-2-Abschluss-Beobachtung.
  6. **Commit + PR** (Detail-Plan-Frage-4-A): eigene PR aus Worktree-Branch `claude/nice-neumann-35648e` gegen `main`.
- **Akzeptanzkriterien (UMSETZUNG → funktionsbasiert, 7 Stück):**
  - **AC-1:** Backend-Coverage-Frischlauf grün, 440 passed + 1 skipped, gesamt ≥ 95 %; Modul-Schwellen `backend/auth` ≥ 95 % Lines / ≥ 90 % Branches, `backend/auth_anonymous` ≥ 95 % / ≥ 90 %, `backend/tenants` ≥ 80 % erfüllt (jeweils gewichtet auf Modul-Aggregat).
  - **AC-2:** Frontend-Disponent-Coverage-Frischlauf grün, 27/27 Tests, ≥ 80 % Lines auf getesteten Modulen.
  - **AC-3:** Frontend-Einsatzkraft-Coverage-Frischlauf grün, 47/47 Tests, ≥ 80 % Lines auf getesteten Modulen.
  - **AC-4:** GitHub-Issue „Phase 7.2 — Externe Security-Review Auth-Stack beauftragen" im Repo `Paddel87/EB-Digital` angelegt mit vollständigem Briefing (Scope, Artefakt-Verweise, Bedrohungsmodell-Anker, Erfolgskriterien, Out-of-Scope, Referenzen).
  - **AC-5:** `docs/fahrplan.md` Schritt 2.7 in vollem Schritt-Format; „Aktueller Stand" auf Phase 2 ERLEDIGT, Phase 3 als nächste laufende Phase nominiert; Phasen-Übersicht entsprechend; Reflexions-Eintrag für Phase 2.
  - **AC-6:** `README.md` Status-Block und „Nächste Schritte" synchronisiert (Phase 2 abgeschlossen, Phase 3 / Spike I + J als nächste Schritte).
  - **AC-7:** `docs/logbuch.md` `[SESSIONENDE]`-Eintrag mit Coverage-Snapshot, Issue-Verweis, Phase-2-Abschluss-Beobachtung.
- **Betroffene Module:** keine Code-Änderung. Reine Doku-Pflege in `docs/fahrplan.md`, `docs/logbuch.md`, `README.md`. Neuer GitHub-Issue.
- **Reifegrad-Wirkung:**
  - **Keine Beförderung in 2.7.** Modul-Reifegrade bleiben unverändert: `backend/auth`, `backend/auth_anonymous`, `backend/tenants` bleiben `[BELASTBAR]` (mit der Phase-2-Sonderregel-Einschränkung). Architektur-Pattern (Modular Monolith + 3 SvelteKit-Frontends) bleibt `[VORLÄUFIG]` bis Phase-6-Last-Test (analog Detail-Frage 5-A aus 2.5/2.6).
  - **Phase-2-Reifegrad-Bilanz** (Beförderungen durch Phase 2 insgesamt): `backend/auth` → `[BELASTBAR]` (2.2), `backend/auth_anonymous` → `[BELASTBAR]` (2.3), `backend/tenants` → `[BELASTBAR]` (2.4), Request-Scoped DB-Session-Dependency → `[BELASTBAR]` (2.5b). Schnittstellen S1 (in 1.6 schon belastbar) + S2a, S8a, S8b, S10 zu `[BELASTBAR]`. Datenmodelle `anonymous_session`, `operation.url_token`-Widening zu `[BELASTBAR]`. Invarianten I1, I2 zu `[BELASTBAR]`. Frontends `frontend-disponent` und `frontend-einsatzkraft` funktional validiert, Reifegrad bleibt `[VORLÄUFIG]` bis Last-Test.
- **Artefakte:**
  - **Doku:** `docs/fahrplan.md` (dieser Schritt + Aktueller-Stand-Update + Phasen-Übersicht + Reflexion), `docs/logbuch.md` (`[SESSIONENDE]`-Eintrag), `README.md` (Status-Block + Nächste-Schritte).
  - **GitHub-Issue:** `Paddel87/EB-Digital#26` (Phase 7.2 — Externe Security-Review Auth-Stack beauftragen).
  - **Keine Code-Änderung.** Keine Tests neu, keine Migrations, keine Artefakte in `backend/` oder `apps/`.
- **Notizen:**
  - **Phase-2-Sonderregel** (Eingangsdisziplin abgemildert, alle berührten Module starten als `[VORLÄUFIG]` und werden mit dem jeweiligen funktionalen Schritt befördert) hat in der Praxis getragen: alle vier befördernden Schritte (2.2, 2.3, 2.4, 2.5b) lieferten den Reifegrad-Wechsel verifiziert über Coverage + dev-smoke.sh. Keine spätere `[REAKTIV]`-Korrektur aufgrund verfrühter Beförderung.
  - **Operation-Eröffnung in Phase 2** (Detail-Plan-Frage-3-A): Phase-2-Abschluss-Kriterium fordert „Mandant-Disponent eröffnet eine leere Operation, die in `operation_tenant_participation` mit `role='owner'` verbunden ist". `backend/operations`-Use-Cases existieren in Phase 2 nicht (per Plan Phase 4). Der bestehende Direkt-INSERT-Pfad in `scripts/dev-smoke.sh` (seit 2.3 für Anon-Smoke aktiv, in 2.4 um `operation_tenant_participation`-Setup mit `role='owner'` erweitert) ist die korrekte Phase-2-API zur Operation-Anlage. Dev-smoke-Lauf gegen Compose-Stack (zuletzt 2.4-Sessionende) belegt die Kette End-to-End.
  - **Issue als Briefing-Anker, nicht als Vergabe-Dokument:** Detail-Plan-Frage-1-A bewusst gewählt, weil eine externe Vergabe-Anbahnung erst sinnvoll ist, wenn der Status `Konzeption → Aufbau` gewechselt hat (Phase 7.7). Vergabe-Modalitäten (Pricing, Zeitrahmen, Vertrag) werden in Phase 7.2 bei Issue-Aktivierung ergänzt.
  - **Coverage-Lücken-Behandlung** (Detail-Plan-Frage-2-A): keine aktive Suche nach uncovered Branches. Phase-Schwellen sind übererfüllt; externe Security-Review prüft Logik und Threat-Model, nicht Coverage-Branches. Eine spätere Coverage-Härtung (z. B. `backend/auth/reset_token.py` 80 % → 95 %, `backend/tenants/api.py` 89 % → 95 %) wäre Phase-7-Stabilisierungs-Pfad.
  - **`HTTP_422_UNPROCESSABLE_ENTITY` Deprecation-Warning** im Backend-Coverage-Lauf: Starlette 1.0.0 / FastAPI 0.136.x liefert Backwards-compat-Alias für `HTTP_422_UNPROCESSABLE_CONTENT`. Kein Phase-2-Blocker; im `logbuch.md` als `[BEOBACHTUNG]` notiert, um in Phase 4 oder Phase 7 mit dem nächsten Stack-Refresh entschuldet zu werden.
  - **Kein ADR in 2.7** (Detail-Plan-Frage-5-A): Phase-Abschluss ist Status-Update / Buchhaltung, keine Entscheidung. Reaktiv-Quote bleibt 1 / 10 = 10 %.

---

### Phase 3: Spikes Wave 1 – Operations-Vorklärungen – Typ: ERKUNDUNG

**Ziel:** Klärung der zwei Architektur-Lücken, die `backend/operations` blockieren würden: Geo-Plausibilitäts-Algorithmus (Spike I) und Bündelungs-Trigger (Spike J). Ergebnisse als ADRs plus Architektur-Updates dokumentiert; betroffene `[OFFEN]`-Bereiche in `architecture.md` Abschnitt 9 zu `[VORLÄUFIG]` befördert.

**Abschlusskriterium:** ADR pro Spike mit Tag `[ERKENNTNIS]` plus Themen-Tag, fixierte Entscheidung; `architecture.md` Abschnitt 6 (NFR-/Algorithmus-Bereich) und Abschnitt 9 entsprechend aktualisiert; keine Implementation-Änderungen am Produktivcode.

**Reifegrad-Erwartung am Phasenende:** `[OFFEN]`-Bereich Spike I → `[VORLÄUFIG]`; `[OFFEN]`-Bereich Spike J → `[VORLÄUFIG]`.

**Schritte:**

#### 3.1: Spike I — Geo-Plausibilitäts-Algorithmus

- **Status:** ERLEDIGT (2026-05-18)
- **Phasentyp-Kontext:** ERKUNDUNG
- **Schritt-Art:** Spike + Vergleichsstudie (zwei Algorithmus-Varianten)
- **Zeitbox:** 4 h
- **Abhängigkeiten:** Phase 2 ERLEDIGT (Operations-Hülle steht noch nicht produktiv, aber `backend/auth_anonymous` produktiv — der Algorithmus wird beim Anonymen-Bestell-Pfad gegriffen).
- **Freigabepflichtig:** nein (Spike-Schritt). Resultierender ADR-017 ist freigabepflichtig.
- **Eingangskriterien:** Patrick-Direktive 2026-05-18 zum Spike-Inhalt liegt vor (A vs. B-Vergleich, 500-m-Moderationsfilter, kein Kalman-Filter, Test-Datensatz Bremen Innenstadt + Osterdeich-/Weserstadion-Bereich). Constraint aus `project-context.md` Abschnitt 6 Sicherheit ist die Wurzel: „Distanz vom GPS-Standort zum nächstgelegenen aktiven Einsatzraum > Schwellenwert (initial 5 km, anpassbar pro Einsatz) wirft Bestellung in Disponenten-Moderation, nicht in Auto-Verteilung."
- **Zu klärende Fragen:**
  1. **Distanz-Metrik:** Hülle (nächster Punkt auf Polygon-Rand) vs. Centroid (Mittelpunkt). Welche ist für längliche Einsatzräume wie Osterdeich/Fanmeile angemessen?
  2. **GPS-Ungenauigkeit:**
     - **Variante A (pauschal):** fester Aufschlag (z. B. +30 m), unabhängig vom client-gemeldeten `accuracy`-Wert.
     - **Variante B (dynamisch):** `2·accuracy`-Aufschlag (95-%-Konfidenz, aus `position.coords.accuracy` der Geolocation API).
       Vergleich an Test-Punkten mit unterschiedlicher GPS-Qualität.
  3. **Moderations-Filter:** `accuracy > 500 m` (deutliches Indiz für reines WLAN-/Cell-Tower-Locating) → automatisch in Disponenten-Moderation. Schwellenwert variieren?
  4. **Text-Standort-Behandlung:** Bestellungen ohne GPS-Standort (Permission verweigert, kein GPS-Fix) — Moderation, hart ablehnen oder auto-akzeptieren?
  5. **Mandanten-konfigurierbarer Schwellenwert:** wie ist die Konfiguration verankert — pro Mandant, pro Einsatz, oder beides? Default 5 km. Min/Max-Grenzen?
  6. **Algorithmus-Performance:** bei mehreren parallelen Einsatzräumen pro Mandant — Bounding-Box-Vorsortierung notwendig für p95 < 300 ms?
- **Akzeptanzkriterien (wissensbasiert, ERKUNDUNG):**
  - Test-Datensatz konstruiert: GeoJSON-Polygone Bremen Innenstadt (mehrere) + Osterdeich/Fanmeile; GPS-Testpunkte mit variabler accuracy (klar drinnen, am Rand, drinnen mit großer Streuung, klar draußen, Mobilfunk-only).
  - Pseudocode der Algorithmus-Varianten A und B liegt vor, formal nachvollziehbar.
  - Entscheidungs-Tabelle pro Testpunkt mit Ergebnis aus Variante A und B vorhanden (akzeptieren / moderieren / ablehnen).
  - ADR-017 mit klarer Entscheidung Distanz-Metrik, A vs. B, Moderations-Schwelle, Text-Standort-Behandlung, Konfigurations-Verankerung.
  - `architecture.md` Modul `backend/operations` und `backend/geo` aktualisiert; Reifegrad-Übersicht (Abschnitt 9) zeigt den `[OFFEN]`-Bereich „Geo-Plausibilitäts-Algorithmus" als `[VORLÄUFIG]`.
- **Betroffene Module:** `backend/operations` (ruft den Plausibility-Check beim Anlegen einer Order auf), `backend/geo` (Heimat der `PlausibilityChecker`-Logik, siehe `architecture.md` Zeile 185). Keine produktive Implementation in diesem Schritt — Spike ist „Wegwerf"-Algorithmus auf dem Reißbrett, ohne Code-Änderung am Produktivpfad.
- **Reifegrad-Wirkung am Schritt-Ende:**
  - `[OFFEN]`-Bereich „Geo-Plausibilitäts-Algorithmus" in `backend/operations` → `[VORLÄUFIG]`.
  - `[OFFEN]`-Bereich „Geo-Plausibilitäts-Algorithmus" in `backend/geo` (Komponente `PlausibilityChecker`) → `[VORLÄUFIG]`.
  - Modul-Reifegrade selbst bleiben `[VORLÄUFIG]` (volle Beförderung erst nach Phase 4 Implementation).
- **Artefakte:**
  - `docs/spikes/spike-i-results.md` — Test-Datensatz, Pseudocode, Durchrechnen, Diskussion.
  - `docs/decisions.md` — neuer ADR-017 `[ERKENNTNIS] [PERFORMANCE]` plus Reaktiv-Quoten-Update in Teil A.
  - `docs/architecture.md` — Updates in Modulen `backend/operations`, `backend/geo`, Abschnitt 9 Reifegrad-Übersicht.
- **Notizen:**
  - Spike ist Schreibtisch-Übung — keine reale GPS-Messung im Feld. Test-Punkte sind synthetisch, aber mit realistischen accuracy-Werten aus der Geolocation-API-Praxis (Smartphone-GPS draußen: 5–20 m, Stadtkanyon: 20–80 m, indoor/WLAN: 30–200 m, Cell-Tower-only: 500–3000 m).
  - Algorithmus berechnet **immer** auf dem Server, nie auf dem Client (manipulationsgeschützt).
  - Konsistenz mit Vision-Constraint „keine PII in Logs": GPS-Roh-Koordinaten dürfen nur als gehashter Tile-Identifier ins Log, nicht als Klartext (`project-context.md` Abschnitt 6 Datenschutz).
- **Verifikation am 2026-05-18 (alle Akzeptanzkriterien erfüllt):**
  1. ✅ Test-Datensatz konstruiert: 6 Polygone (Bremen Innenstadt P1–P5 + Osterdeich/Weserstadion P6) plus 14 GPS-Testpunkte über fünf Szenarien S1–S5 (Hülle-vs-Centroid, A-vs-B-GPS-Toleranz, 500-m-Moderationsfilter, Text-Standort, Mandanten-/Einsatz-Schwellenwert). Siehe `docs/spikes/spike-i-results.md` Abschnitt 2.
  2. ✅ Pseudocode der Algorithmus-Varianten A (pauschal +30 m) und B (`2·accuracy`-dynamisch) liegt vor, plus Moderations-Filter, plus dreistufige Konfigurations-Hierarchie. `docs/spikes/spike-i-results.md` Abschnitt 3.
  3. ✅ Entscheidungs-Tabellen pro Testpunkt: S1 zeigt Hülle ≫ Centroid bei länglichen Polygonen; S2 zeigt B reagiert auf GPS-Qualität (T7 konservativ bei accuracy 80 m, T8 präziser bei accuracy 5 m); S3 Moderations-Filter greift ohne Distanz-Berechnung; S4 Text-Standort → Moderation; S5 Konfigurations-Notwendigkeit am Werder-Heimspiel demonstriert. `docs/spikes/spike-i-results.md` Abschnitt 4.
  4. ✅ ADR-017 in [docs/decisions.md](decisions.md) `[ERKENNTNIS] [PERFORMANCE] [MODUL]` mit klarer Entscheidung Option C (Hülle + dynamische Toleranz), Konsequenzen, Wirkung auf bestehende ADRs, Folge-Edits.
  5. ✅ `architecture.md` Module `backend/operations` und `backend/geo` aktualisiert (Spike-I-Bereiche von `[OFFEN]` auf `[VORLÄUFIG]` mit ADR-017-Verweis); Abschnitt 9 Reifegrad-Übersicht entsprechend; Datenfluss F2 Schritt 6 mit konkreten Outcome-Werten ersetzt.
- **Zeitbox-Bilanz:** Spike ist Reißbrett-Übung, kein Feld-Test. Effektiver Aufwand: Algorithmus-Definition + Test-Datensatz-Konstruktion + Durchrechnen + ADR + architecture/fahrplan-Sync deutlich innerhalb 4-h-Zeitbox.

- **3.2 [ERLEDIGT]** 2026-05-28 — Spike J (Bündelungs-Trigger). Schritt-Art Vergleichsstudie, Zeitbox 4 h. Klärt Auslöser (manuell durch Disponent, Designfrage 1.A), Datenstruktur (eigene `order_bundle`-Entity, Designfrage 2.A), Versorgungs-Transporter-Zwang (ja, `mode='large_order'` Pflicht, Designfrage 3.A), räumliche Voraussetzung (keine harte Backend-Validierung in Phase 1, Designfrage 4.A) und Aggregat-Semantik (`bundling_count` = Aktionsanzahl plus neu `bundled_order_count` als additive ADR-006-Erweiterung, Designfrage 5.A). Zusatz-Constraint aus Spike-Analyse: Minimum 2 Orders pro Bündel. **Ergebnis:** [ADR-018](decisions.md) mit Tags `[ERKENNTNIS] [MODUL] [DATENMODELL]`; `BundleOrders`-Use-Case-Vertrag + 8 Fehlerklassen + 11-Eintrag-Test-Datensatz inline im ADR. **Reifegrad-Wirkung:** `[OFFEN]`-Bereich Spike J in `backend/operations` auf `[VORLÄUFIG]` befördert; S4-Schnittstelle offene Frage „Bündel-Mapping" gelöst (N Assignments mit identischer `bundle_id`). **Phase-4.3-Vorgaben:** Migration ergänzt Entity `order_bundle` (id, operation_id, vehicle_id, created_by_dispatcher_id, status active/completed/dissolved) plus zwei nullable FK-Spalten `order.bundle_id` und `order_assignment.bundle_id`. **Phase-6.5-Vorgabe:** `operation_aggregate`-Schema-Migration nimmt `bundled_order_count` (de: `anzahl_gebuendelte_bestellungen`) mit auf.

---

### Phase 4: Operations Core + Realtime + Einsatzkraft-PWA – Typ: UMSETZUNG

**Ziel:** Operations-Hauptpfad (Operation eröffnen, Bestellung anlegen, Auftrag zuweisen, stornieren, bündeln), Audit-Log (ADR-008), Realtime-Hub (WebSocket), Einsatzkraft-Bestell-PWA (F2 Hard-Path aus `architecture.md` Abschnitt 5).

**Abschlusskriterium:** End-to-End-Test: Disponent eröffnet Operation → Einsatzkraft-PWA zeigt URL+Code → Einsatzkraft öffnet anonyme Session → bestellt einen Artikel → Backend prüft Geo-Plausibilität (Algorithmus aus Spike I) → Bestellung in Disponenten-UI sichtbar → Disponent weist Fahrzeug zu (I3) → Audit-Log-Eintrag → WebSocket aktualisiert Live-Standort.

**Reifegrad-Erwartung am Phasenende:** `backend/operations`, `backend/fleet`, `backend/catalog`, `backend/realtime`, `frontend-einsatzkraft` zu `[BELASTBAR]`. Schnittstellen S3 (Operations Event Bus), S4 (Vehicle Assignment), S9 (WebSocket-Topologie) zu `[BELASTBAR]`. Invariante I3 zu `[BELASTBAR]`.

**Hinweis Sonderregel:** Die UMSETZUNG-Eingangs-Disziplin (Schritt-Format: „alle berührten Architektur-Bestandteile vor Schrittbeginn `[BELASTBAR]`") gilt für Phase 4 **abgemildert** gemäß **ADR-019 / Regel-019**. Die Module `backend/catalog`, `backend/fleet`, `backend/operations`, `backend/realtime`, `frontend-einsatzkraft` sind zum Phasenstart `[VORLÄUFIG]` und werden **durch** die Phase-4-Schritte erst zu `[BELASTBAR]` befördert. Voraussetzung: (a) Modul-Schnitt strategisch fixiert (ADR-002/003/009), (b) konsumierte Bestandteile (Plumbing, `backend/auth`, `backend/auth_anonymous`, `backend/tenants`, S10, Regel-013/014, `get_db_session`) tatsächlich `[BELASTBAR]`, (c) Detail-Plan vor Code-Eingriff jeden berührten Bestandteil benennt.

**Schritte:**

#### 4.1: backend/catalog — Basis-Artikelkatalog + mandantenspezifische Erweiterung

- **Status:** ERLEDIGT (2026-05-28; Detail-Plan freigegeben 0B/1D/2B/3A/4A/5A/6A/7A; ADR-019 fixiert Eingangs-Sonderregel)
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** Phase 2 ERLEDIGT (S10, Regel-013/014, `get_db_session`); Plumbing aus Schritt 1.4; ADR-019 angelegt
- **Freigabepflichtig:** ja — Datenmodelländerungen (drei neue Tabellen `catalog_category`, `catalog_item_base`, `catalog_item_tenant_extension`); Detail-Plan vom 2026-05-28 freigegeben (0B/1D/2B/3A/4A/5A/6A/7A); ADR-019 fixiert die Methodik-Voraussetzung
- **Eingangskriterien:**
  - Konsumierte `[BELASTBAR]`-Bestandteile: `backend/auth` (2.2), `backend/auth_anonymous` (2.3), `backend/tenants` + S10 (2.4), Regel-013/014, `get_db_session` (2.5b), Plumbing (1.4)
  - ADR-019 / Regel-019 (Phase-4-Sonderregel) gilt — `backend/catalog` darf trotz `[VORLÄUFIG]`-Reifegrad starten
- **Zu tun:**
  - **Alembic-Migration** mit drei Tabellen:
    - `catalog_category(id UUID PK, name string UNIQUE, created_at, updated_at)` — Kategorien-Tabelle aus Frage 1-D
    - `catalog_item_base(id UUID PK, name string, unit string, default_unit_label string, description text NULL, category_id FK→catalog_category NOT NULL, is_active bool default TRUE, created_at, updated_at)` — Felder aus Frage 1-D
    - `catalog_item_tenant_extension(id UUID PK, tenant_id FK→tenant NOT NULL, base_item_id FK→catalog_item_base NULL, name string NULL, unit string NULL, default_unit_label string NULL, override_name string NULL, override_unit_label string NULL, description text NULL, category_id FK→catalog_category NULL, is_disabled bool default FALSE, created_at, updated_at)` — Frage 2-B
      - **CHECK-Constraint:** `(base_item_id IS NOT NULL) OR (name IS NOT NULL AND unit IS NOT NULL)` — entweder Override eines Base-Items oder eigenständiges Tenant-Item
      - **Partial-UNIQUE-Index:** `UNIQUE(tenant_id, base_item_id) WHERE base_item_id IS NOT NULL` — höchstens ein Override pro Base-Item pro Tenant
  - **SQLAlchemy-Modelle:** `backend/eb_digital/catalog/models.py` mit `CatalogCategory`, `CatalogItemBase`, `CatalogItemTenantExtension`, Pydantic-Schemas in `schemas.py`
  - **Repository-Layer:** `repository.py` mit `CatalogCategoryRepository`, `CatalogItemBaseRepository`, `CatalogItemTenantExtensionRepository`; Resolver-Query in `services.py::resolve_catalog_for_operation(operation_id)` (Frage 3-A: SQL-LEFT-JOIN über S10/Regel-014, Filter `is_active=TRUE` und `(extension IS NULL OR is_disabled=FALSE)`, Override-Felder priorisiert)
  - **Use-Cases:** `CreateCategory` (Plattform-Admin), `CreateBaseItem` (Plattform-Admin), `DeactivateBaseItem` (Plattform-Admin Soft-Delete, Frage 5-A), `CreateTenantExtension` (Disponent eigener Tenant, Frage 6-A), `UpdateTenantExtension` (Disponent), `DisableTenantExtension` (Disponent Soft-Delete), `ResolveCatalogForOperation` (intern, Frage 3-A)
  - **API-Endpunkte in** `backend/eb_digital/catalog/api.py`:
    - Plattform-Admin: `POST/GET/PATCH /api/catalog/base`, `POST/GET /api/catalog/categories`
    - Disponent (eigener Tenant über `current_user.tenant_id`): `POST/GET/PATCH /api/catalog/tenant`
    - Carer: `GET /api/catalog` (effektiver Katalog des eigenen Tenants)
    - Anon (Frage 4-A — Session-Pflicht, Rate-Limit IP+URL AND analog ADR-013, separater Schlüsselraum): `GET /api/anon/{operation_url}/catalog`
  - **Tests:**
    - Unit-Tests pro Use-Case und Repository in `backend/tests/catalog/`
    - Integration mit echtem PostgreSQL-Fixture (Migration-Round-Trip + Resolver-Korrektheit)
    - Coverage-Ziel: ≥ 80 % Lines / 70 % Branches (Standard, Frage 7-A)
  - **dev-smoke.sh-Erweiterung:** neue Stufe „Catalog-Smoke" (Plattform-Admin legt Base-Item via API an → Disponent legt Tenant-Extension via API → Carer-Read `/api/catalog` zeigt effektiven Katalog → Anon-Read `/api/anon/{url}/catalog` zeigt effektiven Katalog der Operation)
  - **Doku-Updates** beim Schrittabschluss: `architecture.md` §3 (Modul-Eintrag → `[BELASTBAR]` + Use-Case-Liste), §4 (S8 + S2 Sub-Surfaces zu `[BELASTBAR]`), §7 (drei neue Entitäten), §9 (Reifegrad-Tabelle); `fahrplan.md` (Status ERLEDIGT mit Verifikations-Block)
- **Akzeptanzkriterien:**
  - `alembic upgrade head` und `alembic downgrade -1` laufen ohne Datenverlust auf Phase-2-Daten
  - Plattform-Admin kann via `POST /api/catalog/base` ein Item anlegen; Versuch durch Disponent → 403
  - Disponent kann via `POST /api/catalog/tenant` eine Extension anlegen, **nur** für eigenen Tenant; Cross-Tenant-Versuch → 403
  - Carer-Read-Pfad `GET /api/catalog` liefert effektiven Katalog gemäß S10-Filter (Regel-014)
  - Anon-Pfad `GET /api/anon/{url}/catalog` liefert effektiven Katalog der Operation; ohne aktive Session → 401; bei aktivem AccessCode → 401 ohne Code
  - **Override-Verhalten:** Tenant-Extension mit `override_name="X"` über `base_item_id` führt im effektiven Katalog dieses Tenants zu Name="X"; in anderen Tenants weiterhin Base-Name
  - **Soft-Delete-Verhalten:** Base-Item mit `is_active=FALSE` erscheint cross-tenant nicht mehr; Tenant-Extension mit `is_disabled=TRUE` (über Base) erscheint im effektiven Katalog dieses Tenants nicht mehr
  - Coverage `backend/catalog` ≥ 80 % Lines / 70 % Branches
  - `dev-smoke.sh` Catalog-Stufe grün gegen Compose-Stack
  - `mypy --strict`, `ruff check`, `ruff format --check`, `bandit`, `pre-commit run --all-files` alle grün
- **Betroffene Module:** `backend/catalog` (zu befördern). Konsumenten in 4.1: `backend/auth` (Session-Validierung), `backend/auth_anonymous` (für `/api/anon/.../catalog`-Pfad), `backend/tenants` (S10).
- **Reifegrad-Wirkung:**
  - `backend/catalog`: `[VORLÄUFIG]` → `[BELASTBAR]`
  - Schnittstelle S8-Sub-Surface `/api/catalog/*`: `[VORLÄUFIG]` → `[BELASTBAR]`
  - Schnittstelle S2-Sub-Surface `/api/anon/{url}/catalog`: `[VORLÄUFIG]` → `[BELASTBAR]`
  - Datenmodelle `catalog_category` + `catalog_item_base` + `catalog_item_tenant_extension`: neu, `[BELASTBAR]`
- **Artefakte:**
  - `backend/eb_digital/catalog/` (`__init__.py`, `models.py`, `schemas.py`, `repository.py`, `services.py`, `api.py`)
  - `backend/migrations/versions/{hash}_add_catalog_tables.py`
  - `backend/tests/catalog/...`
  - `scripts/dev-smoke.sh` Erweiterung
  - `docs/architecture.md` Updates (§3 / §4 / §7 / §9)
  - `docs/fahrplan.md` Schritt-Status ERLEDIGT mit Verifikations-Block
  - `docs/logbuch.md` (`[SCHRITT-START]`, `[REIFEGRAD-WECHSEL]`, `[SCHRITT-ABSCHLUSS]`)
- **Notizen:**
  - **Detail-Plan-Disziplin:** 7 Designfragen wurden am Sessionstart 2026-05-28 vorgelegt (siehe Logbuch-Eintrag 2026-05-28 `[BEOBACHTUNG]`); Patrick freigab als `0B/1D/2B/3A/4A/5A/6A/7A`.
  - **ADR-019 / Regel-019** fixiert die Sonderregel — Modul darf trotz `[VORLÄUFIG]` starten, weil die Beförderung Output des Schritts ist.
  - `catalog_category` ist neu (Frage 1-D) — Datenmodelländerung, freigabepflichtig nach CLAUDE.md §4, durch 1-D bereits freigegeben.
  - `is_active`-Default `TRUE` und `is_disabled`-Default `FALSE`, damit neue Items per Default sichtbar sind.
- **Verifikation am 2026-05-28 (alle Akzeptanzkriterien erfüllt):**
  1. ✅ Migration `b3a9c7e1f205` gegen `postgres:17.9@sha256:347bc4e6…` im Compose-Stack: `alembic upgrade head` fehlerfrei, `alembic check` → „No new upgrade operations detected" (Migration deckungsgleich mit ORM-Modell), `alembic downgrade -1` + `upgrade head` Round-Trip sauber.
  2. ✅ DB-Struktur via `psql \d catalog_item_tenant_extension`: drei Indizes (PK + `ix_*_tenant_id` + Partial-UNIQUE `WHERE base_item_id IS NOT NULL`), CHECK-Constraint `ck_*_mode_constraint` mit zweiseitiger Bedingung, drei FK-Constraints (`base_item_id` CASCADE, `category_id` RESTRICT, `tenant_id` CASCADE) exakt wie spezifiziert.
  3. ✅ Backend-Tests: 55 grüne Catalog-Tests (10 `test_catalog_repositories` + 18 `test_catalog_use_cases` + 27 `test_catalog_api`); Gesamt-Suite **495 passed, 1 skipped**; Coverage gesamt **88 %** (CI-Gate 80 % bestanden); per-File Catalog: models 100 %, schemas 100 %, api 77 %, use_cases 68 %, repositories 39 % (die unter 80 %-Werte sind SELECT-/Resolver-Pfade, die in dev-smoke.sh gegen echtes Postgres gedeckt sind).
  4. ✅ Lint-/Type-/Security-Gates: `ruff check`, `ruff format --check`, `mypy --strict` (7 Catalog source files), `bandit`, `pre-commit run --all-files` alle grün; null `assert # noqa: S101`-Stellen im Modul-Endzustand (Helper-Tuple-Rückgabe statt asserts).
  5. ✅ `dev-smoke.sh`-Catalog-Stufe gegen den vollen Compose-Stack: **9 Sub-Checks grün** — Tenant + Dispatcher Setup (PA-Cookie aus Tenants-Smoke wiederverwendet), `POST /api/catalog/categories` als PA → 201, `POST /api/catalog/base` als PA → 201, `POST /api/catalog/tenant/override` als Disponent → 201, `POST /api/catalog/tenant/own` als Disponent → 201, `GET /api/catalog/tenant` → 2 Extensions (Override + Own), `GET /api/catalog` → Override-Name aktiv (`Wasser regional`) + eigenständiges Item sichtbar (`Lokales Brot`), `GET /api/catalog` ohne Auth → 401, `POST /api/catalog/categories` als Dispatcher → 403.
  6. ✅ Reifegrad-Wirkung **realisiert**: Modul `backend/catalog` `[VORLÄUFIG]` → `[BELASTBAR]` mit Datum 2026-05-28 (`architecture.md` §3 + §9). Schnittstellen S8c (`/api/catalog/*`) und S2b (`/api/anon/{url}/catalog`) als neue belastbare Sub-Surfaces in §4 + §9 ergänzt. Drei Datenmodelle (`catalog_category`, `catalog_item_base`, `catalog_item_tenant_extension`) als belastbar geführt.
- **Reibungen / Verifikations-Erweiterungen:**
  - **Docker daemon initial nicht verfügbar** — Migration manuell ohne `--autogenerate` geschrieben; Round-Trip-Verifikation gegen `postgres:17.9` nach Docker-Verfügbarkeit nachgezogen, `alembic check` bestätigt Deckungsgleichheit mit ORM-Modell (kein Drift).
  - **Login-Rate-Limit 5/15 min/IP** hat dev-smoke.sh-Catalog-Stufe initial gerissen (Tenants-Smoke 4 + Catalog 1 = 5, Frontend +1 → 429). Auflösung: PA-Cookie aus Tenants-Smoke wiederverwendet (1 Login statt 2) plus `valkey-cli FLUSHDB` vor Catalog-Smoke als Smoke-Hygiene-Reset (Valkey trägt in Phase 1 nur Rate-Limit-Counter; Pub/Sub erst Phase 4).
  - **Test-Bug** in `test_update_base_item_unknown_id_raises_not_found`: Stub-Funktion hatte `**_kw` aber Use-Case ruft positional `session` — sofort gefixed.

#### 4.2: backend/fleet — Fahrzeuge, Beladung, Versorgungs-Transporter-Modi

- **Status:** IN ARBEIT (seit 2026-05-28; Detail-Plan freigegeben 0A/1A/2A/3B/4B/5B/6A/7A/8A)
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 4.1; Phase 2; ADR-019 / Regel-019 (Phase-4-Sonderregel); ADR-008 + ADR-018 (Modus-Wechsel-Audit-Pflicht erst in 4.3 zu erfüllen)
- **Freigabepflichtig:** ja — Datenmodelländerungen (fünf neue Tabellen `vehicle`, `tenant_head_office`, `vehicle_loadout`, `vehicle_loadout_item`, `vehicle_loadout_history`); Detail-Plan vom 2026-05-28 freigegeben (0A/1A/2A/3B/4B/5B/6A/7A/8A); ADR-019 trägt den Eingang trotz `[VORLÄUFIG]`-Modul-Reifegrad
- **Eingangskriterien:**
  - Konsumierte `[BELASTBAR]`-Bestandteile: Plumbing (1.4), `backend/auth` (2.2), `backend/tenants` + S10 (2.4), `backend/catalog` (4.1 — für Beladungs-Item-Referenzen), Regel-013/014, `get_db_session` (2.5b / ADR-015)
  - Detail-Plan-Freigabe 2026-05-28: **0A** (Scope: 4.2 ohne S4 und ohne Verbrauchsbuchung — beides in 4.3), **1A** (Fahrzeug-Typ-Trennung über `vehicle.type` mit CHECK), **2A** (Versorgungs-Transporter-Modus als `vehicle.mode` mit CHECK auf Typ-Kombi, Default `'off'`), **3B** (Mode-Wechsel-Use-Case in 4.2 ohne Audit-Log; Audit-Pflicht erst in 4.3 durch `backend/operations.SwitchSupplyTransporterMode`), **4B** (relationales Beladungsmodell mit separater `vehicle_loadout_history`-Append-Only-Tabelle), **5B** (Beladung referenziert Base- ODER Tenant-Extension via CHECK-exklusiv), **6A** (HeadOffice als eigene `tenant_head_office`-Tabelle, modul-sauber), **7A** (Disponent R/W eigener Tenant + PA R-only + Carer R eigener Tenant + Anon 403), **8A** (Standard-Coverage 80 % / 70 %)
- **Zu tun:**
  - **Alembic-Migration** mit fünf Tabellen:
    - `vehicle(id UUID PK, tenant_id FK→tenant CASCADE NOT NULL, type text NOT NULL, mode text NULL, name text NOT NULL, license_plate text NULL, capacity_label text NULL, is_active bool default TRUE, created_at, updated_at)`
      - **CHECK** `ck_vehicle_type_mode_constraint`: `(type='supply_transporter' AND mode IN ('off','mobile_supply','large_order')) OR (type='regular' AND mode IS NULL)`
      - **CHECK** `ck_vehicle_type_valid`: `type IN ('regular','supply_transporter')`
      - **Index** `ix_vehicle_tenant_id` für Tenant-Scope-Queries
      - **Partial-Index** `ix_vehicle_tenant_id_active WHERE is_active=TRUE` für Default-Listing
    - `tenant_head_office(tenant_id UUID PK FK→tenant CASCADE, lat double precision NOT NULL, lng double precision NOT NULL, label text NULL, created_at, updated_at)`
      - 1:1 zu Tenant; PK ist `tenant_id` (kein eigener Surrogat-Key)
      - **CHECK** `ck_tenant_head_office_lat_range`: `lat BETWEEN -90 AND 90`
      - **CHECK** `ck_tenant_head_office_lng_range`: `lng BETWEEN -180 AND 180`
    - `vehicle_loadout(id UUID PK, vehicle_id FK→vehicle CASCADE NOT NULL UNIQUE, recorded_at TIMESTAMPTZ NOT NULL, recorded_by_dispatcher_id FK→user CASCADE NOT NULL, created_at, updated_at)`
      - Aktueller Snapshot pro Vehicle (UNIQUE auf `vehicle_id`)
    - `vehicle_loadout_item(id UUID PK, loadout_id FK→vehicle_loadout CASCADE NOT NULL, base_item_id UUID NULL FK→catalog_item_base RESTRICT, tenant_extension_id UUID NULL FK→catalog_item_tenant_extension RESTRICT, quantity int NOT NULL, created_at)`
      - **CHECK** `ck_vlitem_exactly_one_ref`: `(base_item_id IS NOT NULL AND tenant_extension_id IS NULL) OR (base_item_id IS NULL AND tenant_extension_id IS NOT NULL)`
      - **CHECK** `ck_vlitem_quantity_positive`: `quantity > 0`
      - Zwei Partial-UNIQUE-Indizes gegen Doppel-Item pro Loadout: `UNIQUE(loadout_id, base_item_id) WHERE base_item_id IS NOT NULL` und `UNIQUE(loadout_id, tenant_extension_id) WHERE tenant_extension_id IS NOT NULL`
    - `vehicle_loadout_history(id UUID PK, vehicle_id FK→vehicle CASCADE NOT NULL, recorded_at TIMESTAMPTZ NOT NULL, recorded_by_dispatcher_id FK→user CASCADE NOT NULL, items JSONB NOT NULL, created_at)`
      - **Append-only** — wird bei jedem Loadout-Update aus dem alten Stand befüllt
      - **JSONB** für History-Items, weil Catalog-Items deaktiviert/umbenannt sein könnten — History muss historisch unveränderlich bleiben (Frozen Snapshot mit Klartext-Item-Daten plus Referenz-IDs)
      - **Index** `ix_vlh_vehicle_id_recorded_at` (DESC) für „letzte N Snapshots"-Queries
  - **SQLAlchemy-Modelle:** `backend/eb_digital/fleet/models.py` mit `Vehicle`, `TenantHeadOffice`, `VehicleLoadout`, `VehicleLoadoutItem`, `VehicleLoadoutHistory`; Pydantic-Schemas in `schemas.py`
  - **Repository-Layer:** `repository.py` mit `VehicleRepository`, `TenantHeadOfficeRepository`, `VehicleLoadoutRepository`, `VehicleLoadoutHistoryRepository`
  - **Use-Cases:**
    - `CreateVehicle` (Disponent eigener Tenant) — `type` (regular/supply_transporter), `name`, optional `license_plate` + `capacity_label`; bei `type='supply_transporter'` wird `mode='off'` als Default gesetzt
    - `UpdateVehicle` (Disponent eigener Tenant) — Stammdaten ändern; Typ-Wechsel verboten (`VehicleTypeChangeNotAllowed`)
    - `DeactivateVehicle` (Disponent eigener Tenant) — Soft-Delete via `is_active=FALSE`
    - `UpdateSupplyTransporterMode` (Disponent eigener Tenant) — nur für `type='supply_transporter'`; akzeptierte Werte `{'off','mobile_supply','large_order'}`; **kein Audit-Log in 4.2** (3B: Audit-Pflicht in 4.3 über `backend/operations.SwitchSupplyTransporterMode`-Umhüllung); Fehler `VehicleNotSupplyTransporter` bei `type='regular'`
    - `SetLoadout` (Disponent eigener Tenant) — Items-Liste atomar setzen; vor Replace wird der aktuelle Snapshot in `vehicle_loadout_history` als Frozen JSONB kopiert (mit Item-Names + Refs eingefroren); Items validieren gegen `(base_item_id IS NOT NULL XOR tenant_extension_id IS NOT NULL)` und Catalog-Items müssen `is_active=TRUE` bzw. `is_disabled=FALSE` sein; Tenant-Extension-Items müssen zum selben Tenant gehören wie das Vehicle (Cross-Tenant-Check)
    - `GetLoadoutHistory` (Disponent eigener Tenant, PA alle) — paginierte Liste, neueste zuerst
    - `SetHeadOffice` (Disponent eigener Tenant) — Upsert auf `tenant_head_office`; `lat`/`lng`-Range-Check redundant zur DB
  - **API-Endpunkte in** `backend/eb_digital/fleet/api.py`:
    - Disponent eigener Tenant: `POST/GET/PATCH/DELETE /api/fleet/vehicles`, `POST /api/fleet/vehicles/{id}/mode`, `GET/PUT /api/fleet/vehicles/{id}/loadout`, `GET /api/fleet/vehicles/{id}/loadout/history`, `GET/PUT /api/fleet/head-office`
    - Plattform-Admin (R-only über alle Tenants via Query-Param `?tenant_id=<uuid>`): `GET /api/fleet/vehicles`, `GET /api/fleet/vehicles/{id}/loadout`, `GET /api/fleet/vehicles/{id}/loadout/history`, `GET /api/fleet/head-office?tenant_id=<uuid>`
    - Carer (eigener Tenant R-only über S10): `GET /api/fleet/vehicles`, `GET /api/fleet/vehicles/{id}/loadout`
    - Anon: 403 auf allen Pfaden
  - **Tests:**
    - Unit-Tests pro Use-Case und Repository in `backend/tests/fleet/`
    - Integration mit echtem PostgreSQL-Fixture (Migration-Round-Trip + Loadout-History-Korrektheit)
    - Coverage-Ziel: ≥ 80 % Lines / 70 % Branches (8A)
  - **dev-smoke.sh-Erweiterung:** neue Stufe „Fleet-Smoke" (Disponent legt Vehicle via API an → setzt Mode → setzt Loadout mit Base+Tenant-Ref → liest Loadout zurück → setzt Loadout erneut → History zeigt 1 Eintrag → HeadOffice anlegen+lesen → Carer-Read zeigt eigene Tenant-Vehicles → Plattform-Admin-Read über `?tenant_id=` → Berechtigungs-Verweigerungen 401/403)
  - **Doku-Updates** beim Schrittabschluss: `architecture.md` §3 (Modul-Eintrag → `[BELASTBAR]` + Use-Case-Liste), §4 (neue Sub-Surface S8d ergänzt), §7 (fünf neue Entitäten), §9 (Reifegrad-Tabelle); `fahrplan.md` (Status ERLEDIGT mit Verifikations-Block); `README.md` Status-Block + Nächste-Schritte
- **Akzeptanzkriterien:**
  - `alembic upgrade head` und `alembic downgrade -1` laufen ohne Datenverlust auf Phase-4.1-Daten; `alembic check` ergibt „No new upgrade operations detected"
  - Disponent kann via `POST /api/fleet/vehicles` ein reguläres Fahrzeug + einen Versorgungs-Transporter anlegen; Cross-Tenant-Versuch → 403; Anon → 403; Carer-Schreibversuch → 403
  - `POST /api/fleet/vehicles/{id}/mode` mit `mode='large_order'` für reguläres Fahrzeug → 422 `VehicleNotSupplyTransporter`
  - `PUT /api/fleet/vehicles/{id}/loadout` mit Items aus Base + Tenant-Extension setzt Loadout; vorherigen Snapshot in History sichtbar
  - `PUT /api/fleet/vehicles/{id}/loadout` mit deaktiviertem Base-Item → 422 `CatalogItemNotAvailable`
  - `PUT /api/fleet/vehicles/{id}/loadout` mit Tenant-Extension eines fremden Tenants → 422 `CrossTenantExtension`
  - `GET /api/fleet/vehicles/{id}/loadout/history` als Disponent eigener Tenant zeigt History; Cross-Tenant-Versuch → 403
  - `GET/PUT /api/fleet/head-office` upsertet HeadOffice; `lat=91` → 422; HeadOffice anderer Tenants → 403 (Disponent) / 200 (PA mit `?tenant_id=`)
  - Coverage `backend/fleet` ≥ 80 % Lines / 70 % Branches
  - `dev-smoke.sh` Fleet-Stufe grün gegen Compose-Stack
  - `mypy --strict`, `ruff check`, `ruff format --check`, `bandit`, `pre-commit run --all-files` alle grün
- **Betroffene Module:** `backend/fleet` (zu befördern). Konsumenten in 4.2: `backend/auth` (Session-Validierung), `backend/tenants` (S10 für Tenant-Scope), `backend/catalog` (Item-Referenz-Validierung bei Loadout).
- **Reifegrad-Wirkung:**
  - `backend/fleet`: `[VORLÄUFIG]` → `[BELASTBAR]`
  - Schnittstelle S8d (Sub-Surface `/api/fleet/*`): neu, `[BELASTBAR]`
  - Datenmodelle `vehicle`, `tenant_head_office`, `vehicle_loadout`, `vehicle_loadout_item`, `vehicle_loadout_history`: neu, `[BELASTBAR]`
  - S4 (Operations → Fleet Vehicle Assignment): bleibt `[VORLÄUFIG]` (Beförderung in 4.3 mit Konsumenten-Implementierung in `backend/operations`)
  - I3: bleibt `[VORLÄUFIG]` (Beförderung in 4.3 zusammen mit S4)
- **Artefakte:**
  - `backend/eb_digital/fleet/` (`__init__.py`, `models.py`, `schemas.py`, `repository.py`, `services.py`, `api.py`)
  - `backend/migrations/versions/{hash}_add_fleet_tables.py`
  - `backend/tests/fleet/...`
  - `scripts/dev-smoke.sh` Erweiterung
  - `docs/architecture.md` Updates (§3 / §4 / §7 / §9)
  - `docs/fahrplan.md` Schritt-Status ERLEDIGT mit Verifikations-Block
  - `docs/logbuch.md` (`[SCHRITT-START]`, `[REIFEGRAD-WECHSEL]`, `[SCHRITT-ABSCHLUSS]`)
  - `README.md` Status-Block + Nächste-Schritte
- **Notizen:**
  - **Detail-Plan-Disziplin:** 9 Designfragen (0–8) wurden am Sessionstart 2026-05-28 vorgelegt (siehe Logbuch-Eintrag 2026-05-28 `[BEOBACHTUNG]`); Patrick freigegeben als `0A/1A/2A/3B/4B/5B/6A/7A/8A`.
  - **ADR-019 / Regel-019** trägt die Sonderregel — `backend/fleet` darf trotz `[VORLÄUFIG]` starten, weil Beförderung Output ist.
  - **3B-Konsequenz:** `UpdateSupplyTransporterMode` ist in 4.2 ein einfacher Konfigurationswert-Setter. Audit-Log-Pflicht aus ADR-008 / Regel-011 (`'supply_transporter_mode_changed'`) wird in 4.3 erfüllt, wenn `backend/operations.SwitchSupplyTransporterMode` den fleet-Use-Case umhüllt und das Audit-Log schreibt. Keine TODOs im Code; die Schichten-Trennung ist sauber dokumentiert.
  - **5B-Konsequenz:** Loadout-Item kann entweder Base-Item ODER Tenant-Extension referenzieren. Tenant-Extension-Refs müssen zum Vehicle-Tenant gehören (Catalog-Architektur erlaubt cross-tenant nicht).
  - **Spike M** (Fahrzeugbezeichnungs-Schema, Phase 5) bleibt offen — in 4.2 reicht ein freies `name`-Textfeld. Vor Roll-out (Phase 7) wird das Schema final geklärt.
  - **`vehicle_realtime_position`** gehört zu `backend/realtime` (Schritt 4.4) — wird **nicht** in 4.2 angelegt.

#### 4.3: backend/operations — Operations + Orders + Audit-Log + Bündelung + Plausibilität

- **Status:** OFFEN
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 4.1, 4.2; ADR-006, ADR-008, ADR-009, ADR-017, ADR-018

#### 4.4: backend/realtime — WebSocket-Hub + Pub/Sub via Valkey

- **Status:** OFFEN
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 4.3

#### 4.5: frontend-einsatzkraft — anonyme Bestell-PWA (F2 Hard-Path)

- **Status:** OFFEN
- **Phasentyp-Kontext:** UMSETZUNG
- **Abhängigkeiten:** 4.1, 4.3, 4.4; 2.6 (AccessCode-UI bereits gebaut)

#### 4.6: Tests + Coverage-Anker

- **Status:** OFFEN
- **Phasentyp-Kontext:** UMSETZUNG (Phase-2-Pattern: Coverage-Frischlauf für alle in Phase 4 belastbaren Module; `backend/operations` ≥ 90 %)

---

### Phase 5: Spikes Wave 2 – Geo, Frontends, Resilience, Roll-out – Typ: ERKUNDUNG

**Ziel:** Klärung der fünf verbleibenden Architektur-Lücken vor Phase 6 + 7: Sperrungs-Override (G), Resilience (H), Hilfe-Knopf-Semantik (K), Tile-Caching-Strategie Frontend (L), Fahrzeugbezeichnungs-Schema (M).

**Abschlusskriterium:** ADR pro Spike, alle `[OFFEN]`-Bereiche Spike G/H/K/L/M zu `[VORLÄUFIG]` befördert; Stakeholder-Rückfrage DPolG zu Spike M dokumentiert.

**Reifegrad-Erwartung am Phasenende:** alle `[OFFEN]`-Bereiche Spike G/H/K/L/M zu `[VORLÄUFIG]`.

**Schritte:**

#### 5.1: Spike G — Sperrungs-Override-Technik (Override + Reverse-Override)

- **Status:** OFFEN
- **Phasentyp-Kontext:** ERKUNDUNG
- **Schritt-Art:** Spike + Vergleichsstudie
- **Zeitbox:** 8–12 h (erweitert gegenüber bisherigen 4–8 h wegen Reverse-Override-Anforderung und Provider-Vergleich)
- **Abhängigkeiten:** Phase 2 ERLEDIGT (Auth-Stack zur Adapter-Authentifizierung); ADR-014/Regel-017 (Provider-Neutralität).
- **Freigabepflichtig:** nein (Spike-Schritt). ADR im Anschluss freigabepflichtig.
- **Eingangskriterien:** TomTom-Recherche-Befunde aus `project-context.md` Abschnitt 11 (Eintrag 2026-05-17) gelesen; `avoidAreas`-Rechteck-Limit und `supportingPoints`-Mechanik verstanden; ADR-016 (Cache-Verzicht) berücksichtigt — beeinflusst die API-Budget-Folgen pro Override-Technik, weil ohne Server-Cache jeder Override-Versuch direkt aufs Provider-Budget durchschlägt.
- **Zu klärende Fragen:**
  1. **Anforderungs-Präzisierung „Override":** Patrick-Direktive 2026-05-17 verlangt _Befahrbarkeit_ vom Routing-Provider als gesperrt geführter Straßen, nicht nur _Markierung_ als gesperrt. Spike trennt zwei Sperrungsarten:
     - **(a) Traffic-basierte temporäre Sperrungen** (Echtzeit-Verkehrslage, Baustellen, Polizei-Absperrungen) — über TomTom Traffic API als `ROAD_CLOSURE`-Incidents gemeldet.
     - **(b) Permanente Sperrungen im Kartenmaterial** (Fußgängerzonen, Einbahnstraßen entgegen Fahrtrichtung, bauliche Sperren) — fest im Routing-Graph des Providers.
  2. **TomTom-Techniken im konkreten Test (Provider-Eignung):**
     - `traffic=false` / `considerTraffic=false` für (a) — Traffic-Incidents ignorieren.
     - `avoidAreas` mit Rechteck-Liste für „großflächige Sperre" (z. B. Innenstadtblock) — Eignung für (a) und (b) prüfen. Achtung: TomTom unterstützt nur Rechtecke, keine Polygone.
     - `supportingPoints` mit Disponent-gesetzten Wegpunkten direkt auf der gesperrten Straße — Route-Rekonstruktion erzwingt Befahrung. Funktioniert nur, wenn die Straße im Routing-Graph als befahrbar existiert (mit oder ohne Restriktion).
     - **Empirischer Test:** drei Test-Szenarien gegen TomTom mit den drei Techniken kombinieren:
       - **Szenario T1:** Echtzeit-Stau / Traffic-Incident auf Hauptstraße → Befahrung erzwingen.
       - **Szenario T2:** Fußgängerzone Bremen-Innenstadt (Beispiel) → Befahrung erzwingen.
       - **Szenario T3:** Einbahnstraße entgegen Fahrtrichtung → Befahrung erzwingen.
  3. **Alternative Routing-Engines als Vergleichs-Kandidaten:**
     - **Valhalla** (OSS, MIT/BSD-lizenziert, OSM-basiert): `exclude_polygons`, dynamische Edge-Penalties, Costing-Funktionen mit Konfiguration zur Befahrung restriktiver Wege. Erwarteter Vorteil bei (b).
     - **OSRM** (OSS, OSM-basiert): weniger flexibel als Valhalla, aber bewährt — als sekundäre Vergleichsoption.
     - **Test der gleichen drei Szenarien T1/T2/T3** gegen Valhalla (lokales Demo-Setup mit OSM-Extract Bremen oder Bayern).
  4. **API-Budget-Folgen pro Technik:** jeder Override-Versuch ist ggf. ein zusätzlicher API-Call (Re-Routing). Mit ADR-016 (Cache-Verzicht) wird das budget-relevanter. Messung pro Szenario.
  5. **Datenbedarf bei Override-Pflege:** wie speichert das System eine „trotzdem befahrbare Strecke"? Polylinie, Wegpunkt-Liste, Edge-Identifier? Wie ist die Disponent-UX (Klick auf Karte vs. Strecken-Editor)?
  6. **Persistenz des Datenmodells `route_override`:** Felder, Lebensdauer (einsatzgebunden), Audit-Log-Eintrag-Pflicht (Regel-012 — destruktive bzw. routing-beeinflussende Disponenten-Aktion).
- **Akzeptanzkriterien (wissensbasiert, ERKUNDUNG):**
  - Für jedes der drei Szenarien T1/T2/T3 ist dokumentiert, welche TomTom-Technik welches Ergebnis liefert (Erfolg/Misserfolg, mit gemessener API-Aufruf-Zahl).
  - Für (mindestens) Szenario T2 (permanente Sperrung) ist dokumentiert, ob TomTom hinreichend ist; falls nein, ist eine Alternative (Valhalla mit OSM-Extract) prototypisch getestet.
  - ADR-Entwurf liegt vor mit:
    - gewählter Override-Technik je Sperrungsart (a)/(b);
    - falls TomTom nicht hinreichend für (b): Empfehlung „Routing-Provider wechseln zu Valhalla" oder „Anforderung (b) als nicht erfüllbar streichen mit Vision-Klarstellung";
    - Datenmodell-Skizze `route_override`;
    - geschätzte API-Budget-Folgen.
- **Betroffene Module:** `backend/geo` (Adapter; im Spike-Stadium als Wegwerf-Code), keine produktive Implementierung. Bei provider-relevanter Empfehlung sind außerdem `infra/tile-proxy` (Routing-Endpunkt-Pfad) und ADR-002 (Stack-Wahl) berührt — dann eigener Folge-ADR.
- **Reifegrad-Wirkung am Schritt-Ende:**
  - `[OFFEN]`-Bereich „Sperrungs-Override-Technik" in `architecture.md` Modul `backend/geo` → `[VORLÄUFIG]` mit ADR-Verweis.
  - Schnittstelle S7 (Geo → Tile-Proxy) `[OFFEN]`-Anteil „Sperrungs-Override-Aufrufschema" → `[VORLÄUFIG]`.
  - Falls Provider-Wechsel als ADR-Konsequenz: Modul `backend/geo` Adapter-Spec aktualisiert; ADR-014/Regel-017 trägt die Wechselbarkeit.
- **Artefakte:**
  - `docs/decisions.md` neuer ADR `[ERKENNTNIS] [MODUL] [PERFORMANCE]` (ggf. zusätzlich `[STACK]`, falls Provider-Wechsel empfohlen).
  - `docs/architecture.md` Update Modul `backend/geo` und ggf. `infra/tile-proxy`.
  - `docs/spikes/spike-g-results.md` (optional, falls Detail-Messprotokoll nicht in den ADR passt) — Test-Szenarien T1/T2/T3 mit Antworten/Routen/Counts.
- **Notizen:**
  - Test gegen TomTom kann mit dem entwickler-eigenen API-Key des Plattform-Betreibers laufen (kein produktiver Mandanten-Bezug nötig).
  - Valhalla-Test kann mit Docker (`valhalla/valhalla:latest` plus DE-OSM-Extract) lokal aufgesetzt werden — Datenmenge für nur Bremen oder Bayern ist <2 GB.
  - Bei Wahl Valhalla als produktive Routing-Engine: Folge-ADR zu Daten-Update-Pipeline (Geofabrik-Extracts, monatliche Frequenz) — nicht Teil von Spike G.
  - Bisheriger Spike-G-Zuschnitt („TomTom-Custom-Areas vs. Route-Bias vs. Penalty-Map") ist in dieser Fassung in den Techniken-Punkten 2 und 3 enthalten und um die Reverse-Override-Anforderung sowie den Valhalla-Vergleich erweitert.

- **5.2** Spike H (Resilience-Granularität) – Schritt-Art Vergleichsstudie + Prototyp, Zeitbox 6–8 h. Klärt Backup-Strategie (logical/physical, RTO/RPO), Recovery-Reihenfolge (Procrastinate-Job-State + Detail-Daten), Verhalten bei Crash mitten im Auftragsstatus-Wechsel, Erfahrung Reconnect WebSocket nach State-Reload. Ergebnis: ADR `[ERKENNTNIS] [MODUL] [DEPLOYMENT]` mit Backup-Frequenz, Recovery-Reihenfolge, getesteter RTO.
- **5.3** Spike K (Hilfe-Knopf-Semantik) – Schritt-Art Spike, Zeitbox 2–3 h. Klärt Pflichtfeld-Beschreibung, Disponenten-Eskalations-Sichtbarkeit, Quittungspfad zum Betreuer, kein PII-Speicher. Ergebnis: UX-Konzept + Datenmodell-Skizze.
- **5.4** Spike L (Tile-Caching-Strategie Frontend) – Schritt-Art Prototyp, Zeitbox **8–10 h** (erhöht gegenüber bisher 6–8 h durch ADR-016: PWA-Service-Worker ist jetzt **alleinige Cache-Schicht für Tile-Last-Glättung** neben Browser-Default-Cache, kein nginx-Cache mehr im Backend). Klärt Workbox-Strategie für Tile-Cache, Pre-Cache des Operations-Raums beim Schichtbeginn (kritischer Hebel), Tile-Lebensdauer (gemäß Provider-`Cache-Control`, MapTiler default 4 h), Speicher-Quota mobiler Browser, Hit-Rate-Schätzung gegen realistische Großlagen-Last. Ergebnis: Prototyp + ADR `[ERKENNTNIS] [MODUL] [PERFORMANCE]`.
- **5.5** Spike M (Fahrzeugbezeichnungs-Schema) – Schritt-Art Vergleichsstudie + Stakeholder-Rückfrage DPolG, Zeitbox 2 h netto. Klärt Naming-Konvention (z. B. „EB-Bremen-01" oder verbandseigene Funkrufnamen), Eindeutigkeit pro Mandant vs. global, Längen-Constraints. Ergebnis: ADR `[ERKENNTNIS] [DATENMODELL]` „Fahrzeug-Naming".

---

### Phase 6: Geo + Disponent-/Betreuer-PWAs + Resilience + Retention + Export – Typ: UMSETZUNG

**Ziel:** Produktive Karten-/Routing-Integration (`backend/geo`), produktive Disponenten- und Betreuer-Frontends inklusive Multi-Disponenten-UX-Schutz (Confirmation-Dialog, Regel-012), Hilfe-Knopf, Offline-Tile-Cache; Resilience-Stack (Backup/Recovery), 30-Tage-Anonymisierung mit Aggregat-Schreibung beim Operation-Ende (ADR-006), DSGVO-Datenexport via Procrastinate-Job-Tripel (ADR-007).

**Abschlusskriterium:** End-to-End: Operation-Ende → Aggregat geschrieben (Regel-008) → Anonymisierungs-Job 30 Tage später entkoppelt → Datenexport-Anforderung liefert ZIP-Download. Disponenten-UI mit Multi-Disponenten-Bestätigungs-Dialog (Regel-012). Betreuer-Mobile-PWA mit Offline-Tile-Cache (Spike L) und Hilfe-Knopf (Spike K). Backup-Recovery-Test bestanden (Spike H, RTO im definierten Bereich).

**Reifegrad-Erwartung am Phasenende:** `backend/geo`, `backend/resilience`, `backend/retention`, `backend/export`, `frontend-disponent`, `frontend-betreuer` zu `[BELASTBAR]`. Schnittstellen S5 (Retention-Trigger), S6 (Tenant Data Export), S7 (Geo→Tile-Proxy) zu `[BELASTBAR]`. Invarianten I4, I5 zu `[BELASTBAR]`.

**Schritte (gröber):**

- **6.1** `backend/geo`: Routing-Adapter (TomTom mit aktiver API-Version pinned, Migrations-Hinweise aus `project-context.md` Abschnitt 5 berücksichtigen), **`Cache-Control`-Header-Pass-Through** an `infra/tile-proxy` (ADR-016 — kein serverseitiges Caching), Sperrungs-Override (Spike-G-Technik), Geofencing, Verbrauchszähler `geo_usage_daily`.
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

- **7.1** Lasttest gegen 50/500 (k6 oder Locust), Messung p95 Backend-API < 300 ms, **plus API-Budget-Validierung externer Geo-Services unter Cache-freier Annahme (ADR-016)**: simulierte Großlage misst Verbrauchszähler `geo_usage_daily` über alle drei Provider-Pfade (MapTiler-Tiles, MapTiler-Geocoding, TomTom-Routing). Bei Budget-Überschreitung der ~50 €/Monat-Annahme aus `project-context.md` Abschnitt 6: Folge-ADR mit Optionen (Budget-Anhebung / Eskalation auf Self-Hosting Pfad-C aus ADR-014 / Mandanten-Vertragsdetail). Auswertung als ADR `[ERKENNTNIS] [PERFORMANCE]`.
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

### Reflexion nach Phase 2 (2026-05-16)

- **Gelernt:**
  - **Phase-2-Sonderregel** (Eingangsdisziplin abgemildert; alle berührten Module starten als `[VORLÄUFIG]` und werden mit dem funktionalen Schritt befördert, nicht mit dem Datenmodell-Skelett) **hat getragen**: alle vier befördernden Schritte (2.2, 2.3, 2.4, 2.5b) lieferten den Reifegrad-Wechsel verifiziert über Coverage + dev-smoke.sh gegen den echten Compose-Stack. Keine spätere `[REAKTIV]`-Korrektur aufgrund verfrühter Beförderung — die einzige `[REAKTIV]`-Adresse (ADR-015) betraf einen Cross-Cutting-Lifecycle-Bug, nicht das Modul-Schnitt-Modell.
  - **Detail-Plan-vor-Code-Disziplin** (etabliert in 2.1, durchgehalten in 2.2/2.3/2.4/2.5/2.5b/2.6/2.7): jeder freigabepflichtige Schritt wurde mit einer Liste klar formulierter Detail-Fragen (3–7 Stück) vor dem Code-Eingriff vorgelegt; Patrick freigab jeweils mit Buchstaben-Kombination (B/B/A/A, A/B/B/A, B/B/A/A/A, A/A/A/A/A). Das verkürzt die Reibungs-Anteile in der Implementation deutlich gegenüber „erst implementieren, dann freigeben lassen".
  - **Test-Maskierung als wiederkehrendes Risiko bei Dependency-Mocks** (ADR-015-Lehre): API-Tests, die `dependency_overrides` mit Stubs nutzen, prüfen die Dependency selbst nicht. Regel-018 fixiert die Lifecycle-Counter-Stub + Real-Smoke-Pflicht für künftige Resource-Dependencies — gilt antizipativ für Procrastinate-Connection-Wrapper (Phase 4), Valkey-Pipelines (Phase 4 Pub/Sub), externe HTTP-Client-Pools (Phase 6 `backend/geo`).
  - **Frontend-Pattern aus 2.5 trug für 2.6** (1:1-Portierung des `api/client.ts`-Wrappers, Route-Gruppen-Idee, In-Memory-Session-Store): pnpm-Workspace ohne shared-Lib in Phase 2 ist akzeptable Duplikation. Ein gemeinsamer `@eb/api-client`-Workspace-Package wäre eigene Refactoring-Phase mit ADR (Architektur-Änderung).
- **Kippende Annahmen:** keine. Annahmen aus ADR-002 bis ADR-014 (Stack, Modul-Schnitt, Auth-Strategie, Verbund-Invarianten) blieben in Phase 2 stabil. ADR-015 (`[REAKTIV]`) korrigierte ein Lifecycle-Detail, kippte aber nicht die strategische Linie.
- **Reifegrad-Änderungen Phase 2 (Bilanz):**
  - `backend/auth`: VORLÄUFIG → BELASTBAR (Schritt 2.2)
  - `backend/auth_anonymous`: VORLÄUFIG → BELASTBAR (Schritt 2.3)
  - `backend/tenants`: VORLÄUFIG → BELASTBAR (Schritt 2.4)
  - Request-Scoped DB-Session-Dependency (cross-cutting): neu eingeführt als BELASTBAR (Schritt 2.5b, ADR-015)
  - Schnittstelle S2a (Anonymous Session API Sub-Surface `/info` + `/session`): VORLÄUFIG → BELASTBAR (Schritt 2.3); S2 insgesamt bleibt VORLÄUFIG bis Order-Endpoints in Phase 4
  - Schnittstellen S8a + S8b (Authentifizierte REST-API Sub-Surfaces für `/auth/login|logout|me` und `/auth/register-tenant|reset-password|/tenants/*`): VORLÄUFIG → BELASTBAR (Schritte 2.2 + 2.4); S8 insgesamt bleibt VORLÄUFIG
  - Schnittstelle S10 (Tenant Participation Lookup): VORLÄUFIG → BELASTBAR (Schritt 2.4)
  - Valkey-Connection-Pool für Backend: VORLÄUFIG → BELASTBAR (Schritt 2.2, ADR-013); Pub/Sub-Pfad bleibt VORLÄUFIG
  - Datenmodell `anonymous_session` + `operation.url_token`-Spalten-Widening: neu eingeführt bzw. BELASTBAR (Schritt 2.3)
  - Invarianten I1 (`operation_tenant_participation` als einzige Mandanten-Verknüpfung) + I2 (abstrakter Berechtigungs-Filter): VORLÄUFIG → BELASTBAR (Schritt 2.4)
  - **Bleibend VORLÄUFIG:** `frontend-disponent` und `frontend-einsatzkraft` (funktional validiert, Last-Validierung steht bis Phase-6-Last-Test aus, analog Detail-Frage 5-A aus 2.5/2.6). Architektur-Pattern (Modular Monolith + 3 SvelteKit-Frontends + 2 Proxies) bleibt VORLÄUFIG bis Phase-6-Last-Test.
- **Neu erkannte Erkundungsbedarfe:** keine zusätzlichen Spikes / Phasen außerhalb des bereits geplanten Fahrplans. Phase 3 (Spike I + Spike J) ist die unmittelbar nächste laufende Phase. Die in Phase 2 entstandenen Folge-Themen (CSRF-Synchronizer-Pattern, externe Security-Review, Coverage-Härtung in `backend/auth/reset_token.py` + `backend/tenants/api.py`, Stack-Refresh `HTTP_422_UNPROCESSABLE_ENTITY` → `_CONTENT`) sind alle Phase-7-Stabilisierungs-Themen und ohne eigene Spike-Phase adressierbar.
- **ADRs aus dieser Phase:** ADR-013 (Rate-Limit als eigener Valkey-Counter, OPERATIV, vor 2.2), ADR-014 (Anbieter-Austauschbarkeit für externe Geo-Services, STRATEGISCH, zwischen 2.1 und 2.2; Doku-only), ADR-015 (yield-Dependency + Rollback, REAKTIV, Hot-Stab 2.5b). Reaktiv-Quote 1 / 10 = 10 %, deutlich unter 20 %-Schwellenwert Klasse G. Regel-017 (Anbieter-Austauschbarkeit) + Regel-018 (yield-Dependency-Pflicht) sind die Phase-2-Regelergänzungen.
- **Issues:** [`Paddel87/EB-Digital#26`](https://github.com/Paddel87/EB-Digital/issues/26) — Phase 7.2 Externe Security-Review Auth-Stack beauftragen (Briefing-Anker, aktiv ab Phase 7.2).

### Reflexion nach Phase 3 (2026-05-28)

- **Gelernt:**
  - **Detail-Plan-vor-ADR-Disziplin trägt auch für ERKUNDUNG-Spikes.** Beide Spike-Sessions (3.1 am 2026-05-18, 3.2 am 2026-05-28) liefen im selben Muster wie die Phase-2-UMSETZUNG-Schritte: Designfragen mit A/B/C-Optionen plus Empfehlungs-Zeile, Patrick-Freigabe als Buchstaben-Kombination, dann ADR-Volltext mit Pseudocode/Use-Case-Vertrag/Test-Datensatz zur Bestätigung. 3.1 wurde mit Option-C-Variante (`2·accuracy`) entschieden, 3.2 mit A/A/A/A/A — beide Male war die Empfehlungs-Linie kein Empfehlungs-Bias zugunsten der einfachsten Lösung.
  - **Spike-J-Befund: ADR-006 musste additiv erweitert werden.** Designfrage 5 (Aggregat-Semantik) hat aufgedeckt, dass ADR-006-Feld `bundling_count` ohne Semantik-Festlegung steht — Aktion-Anzahl vs. Order-Anzahl waren beide plausibel. Erweiterung um zweites Feld `bundled_order_count` ist sauberer als Re-Open von ADR-006. **Lehre:** beim ADR-Schreiben zukünftig prüfen, ob Aggregat-Felder-Semantik explizit ist (Zähl-Einheit konkretisieren), nicht nur Feld-Name.
  - **Phase-1-Scope-Disziplin in Spike-J:** zwei „naheliegende" Erweiterungen bewusst auf spätere Phase verschoben — System-Heuristik für Bündelung (Designfrage 1.B/D, braucht Pilot-Daten) und Stornierung einzelner Orders innerhalb aktivem Bündel (braucht eigenes Lebenszyklus-Modell). Beide sind in ADR-018-Konsequenzen mit Re-Evaluation-Klausel verankert.
  - **Methodik-Lehre aus 2026-05-28 (Stale-Base-Vorfall):** Sessionstart hat den lokalen Stand nur gegen `docs/`-Dateien geprüft, nicht gegen `origin/main`. Lokaler `main` war 11 Tage hinter Remote, der ADR-017-Inhalt war auf Remote bereits anders entschieden als in meinem Lokal-Spike. Aufgedeckt durch `push`-Reject. **Lehre:** der Sessionstart-Pflichtlektüre-Block (CLAUDE.md §2) sollte einen impliziten `git fetch origin && git log <last-known>..origin/<main>`-Schritt enthalten, wenn der lokale `main` potenziell stale ist. Ein Issue an die Dev-Templates-Vorlage analog zu [Paddel87/Dev-Templates#6](https://github.com/Paddel87/Dev-Templates/issues/6) (Dokument-Hygiene) ist als Phase-7-Stabilisierungs-Kandidat vorzumerken.
  - **Datenmodell-Vorgaben aus Spikes konsolidieren sich auf Phase 4.3.** ADR-017 + ADR-018 ergeben gemeinsam mehrere neue Datenmodell-Elemente: zwei Schwellenwert-Spalten (`tenant.plausibility_default_threshold_m`, `operation.plausibility_threshold_m`) plus Audit-Spalten für Plausibilitäts-Outcome (ADR-017), neue Entity `order_bundle` + zwei FK-Spalten `order.bundle_id` und `order_assignment.bundle_id` (ADR-018). Plus eine spätere Aggregat-Spalte in Phase 6.5. Phase 4.3 wird damit die schemataktisch dichteste UMSETZUNG-Phase — Detail-Plan dort entsprechend ausführlich vorlegen.
- **Kippende Annahmen:** keine in den ADR-Entscheidungen selbst. Aber: der 2026-05-28-Sessionstart-Annahme „lokal-stand-ist-aktuell" wurde durch Push-Reject widerlegt; daraus die Methodik-Lehre oben.
- **Reifegrad-Änderungen Phase 3 (Bilanz):**
  - PlausibilityChecker-Bereich in `backend/geo` und `backend/operations`: OFFEN → VORLÄUFIG (3.1, ADR-017)
  - Bündelungs-Trigger-Bereich in `backend/operations`: OFFEN → VORLÄUFIG (3.2, ADR-018)
  - Schnittstelle S4 (Vehicle Assignment) offene Frage „Bündel-Mapping": gelöst (3.2)
  - Mehrere Datenmodell-Vorgaben für Phase 4.3, eine für Phase 6.5
- **Neu erkannte Erkundungsbedarfe:** keine zusätzlichen Spikes/Phasen außerhalb des bereits geplanten Fahrplans. Phase 4 (UMSETZUNG `backend/catalog` → `backend/fleet` → `backend/operations` → `backend/realtime` → `frontend-einsatzkraft` → Tests) ist die unmittelbar nächste laufende Phase. Spike K (Hilfe-Knopf-Semantik) bleibt in Phase 5 (Wave 2); blockiert nur den Hilfe-Knopf-Pfad in Phase 6, nicht Phase 4.
- **ADRs aus dieser Phase:** ADR-017 (Geo-Plausibilitäts-Algorithmus, ERKENNTNIS, Schritt 3.1, 2026-05-18), ADR-018 (Bündelungs-Trigger, ERKENNTNIS, Schritt 3.2, 2026-05-28). Reaktiv-Quote 1/10 = 10 %, unverändert (beide ADRs `[ERKENNTNIS]`, kein `[REAKTIV]`). Keine neuen allgemeinen Regeln aus dieser Phase — ADR-017 und ADR-018 sind beide konkrete Algorithmus-/Use-Case-Entscheidungen ohne wiederkehrendes Muster, das eine Regel rechtfertigen würde.

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
