# Logbuch

<!-- Chronologischer Flugschreiber des Projekts. Ereignisbasierte Einträge, neueste oben.
     Zweck:
       1. Nahtlose Fortsetzung in neuer Session: was war zuletzt los, womit ging es zu Ende?
       2. Wiederfindbarkeit kleiner Lösungen: was war das nochmal mit dem Migrations-Bug?
       3. Selbst-Beobachtung des Projekts: was hat länger gedauert, was war überraschend?

     Abgrenzung zu anderen Dokumenten:
       - fahrplan.md: Was tun wir? (Plan)
       - decisions.md: Warum so? (Begründung)
       - architecture.md: Wie ist es gebaut? (Zustand)
       - blockers.md: Was hindert uns aktuell? (offene Probleme)
       - CHANGELOG.md: Was hat sich für Nutzer geändert? (extern, versionsorientiert)
       - logbuch.md: Was ist während der Arbeit passiert? (intern, chronologisch)

     Das Logbuch ist die einzige chronologisch durchlaufende Erzählung.
     Es darf detailreich sein und kleine Reibungen festhalten – das ist sein Wert. -->

## Aktueller Stand

[Die letzten Einträge geben den aktuellen Stand wieder. Bei Sessionbeginn liest die KI
mindestens den letzten SESSIONENDE-Eintrag und alle Einträge danach, um den Faden aufzunehmen.]

---

## Einträge (neueste oben)

### 2026-05-07 23:55 – [BEOBACHTUNG]

- **Modus-2-Schritt 10 abgeschlossen, CI-Workflow- und Pre-Commit-Skelett angelegt.**
- **Plan vorab vorgelegt und bestätigt** mit fünf zu klärenden Punkten: Action-Patch-Pins (`v5.0.0`/`v4.0.0` als Annahme), Pre-Commit-Hook-Patches (`.0`-Patches der Minor-Linien), initial rote Runs OK, security.yml beschränkt auf Dep-Audits + bandit (kein Duplikat-eslint-security), `release.yml` nicht jetzt.
- **`.github/workflows/ci.yml`** mit 7 Jobs angelegt:
  - Backend (3 Jobs): `lint-backend` (ruff check + format), `typecheck-backend` (mypy --strict), `test-backend` (pytest + Coverage 80 %).
  - Frontend (4 Jobs): `lint-frontend` (eslint + prettier --check), `typecheck-frontend` (svelte-check + tsc), `test-frontend` (vitest, Matrix über drei Frontend-Pakete), `build-frontend` (pnpm -r build).
  - Trigger: `push` (alle Branches) plus `pull_request` (main).
  - Tooling: uv für Python (statt pip aus dem Template), pnpm für TypeScript.
- **`.github/workflows/security.yml`** mit 3 Jobs angelegt:
  - `dep-audit-backend` (pip-audit `--strict --vulnerability-service=osv`).
  - `dep-audit-frontend` (pnpm audit `--audit-level=high`).
  - `static-security-backend` (bandit `-c pyproject.toml`).
  - Trigger: `schedule` (cron `0 6 * * 0`) plus `workflow_dispatch`.
  - Bewusst weggelassen: separater eslint-plugin-security-Lauf (läuft im regulären lint-frontend-Job mit).
- **`.pre-commit-config.yaml`** mit Hooks für beide Sprachen plus generelle Hygiene-Hooks angelegt:
  - General: trailing-whitespace, end-of-file, check-yaml/toml/json, check-added-large-files, check-merge-conflict, detect-private-key.
  - Python: ruff (lint+format, `files: ^backend/`), mypy --strict, bandit.
  - TypeScript/Frontend: prettier (mit `prettier-plugin-svelte`), eslint, svelte-check, tsc --noEmit – die letzten drei als lokale Hooks via pnpm-Workspace-Scripts (weil sie installierte Frontend-Dependencies brauchen).
- **TBD-Ersetzungen** alle aus `project-context.md` Abschnitt 3+7 abgeleitet: Python 3.13, Node 24, pnpm 11, uv 0.11.0, ruff 0.15.0, mypy 1.20.2 (exakt), bandit 1.9.0, prettier 3.8.0, prettier-plugin-svelte 3.5.0, GitHub-Actions checkout/setup-python/setup-node @v6, astral-sh/setup-uv@v5.0.0, pnpm/action-setup@v4.0.0.
- **Nicht angelegt:** `.github/workflows/release.yml` – `project-context.md` Abschnitt 7+8 verschiebt das explizit auf eine spätere Phase (Phase 7: Roll-out-Vorbereitung).
- **Coverage-Modul-Schwellen:** Globaler 80 %-Wert ist im Workflow als `--cov-fail-under=80` gesetzt; modul-spezifische strengere Schwellen (Auth ≥ 95 %, Operations ≥ 90 %, Retention ≥ 95 %, Resilience ≥ 90 % aus `project-context.md` Abschnitt 7) werden in Phase 1 Schritt 1.3 in `pyproject.toml` `[tool.coverage.report]` mit per-Modul-Konfigurationen ergänzt.
- **Initial rote Runs erwartet** – kein Code/keine `pyproject.toml`/keine `package.json` im Repo. Phase 1 Schritte 1.1 + 1.2 stellen die Skelette her, dann werden Workflows grün. Branch-Protection auf `main` wird in Phase 1 Schritt 1.2 aktiviert; bis dahin direkter Push erlaubt (`project-context.md` Abschnitt 10).
- **Methoden-Hinweis:** Die `# TBD:`-Platzhalter aus den Templates wurden alle aufgelöst, aber zwei Action-Patches (`astral-sh/setup-uv`, `pnpm/action-setup`) sind als Annahme gepinnt (`v5.0.0`/`v4.0.0`) und beim ersten Lauf in Phase 1 Schritt 1.2 zu verifizieren. Falls die Tags nicht existieren: konservativ höchsten existierenden Patch der Major-Linie wählen, kein ADR nötig (Patch-Anpassung freigabefrei nach Regel-001).

### 2026-05-07 23:35 – [BEOBACHTUNG]

- **Modus-2-Schritt 9 abgeschlossen, `README.md` aus Vorlagen-Zustand auf vollständiges Statusbild gebracht.**
- **Plan vorab vorgelegt und bestätigt** mit fünf zu klärenden Punkten: Status-Badge-Schema (Konzeption statt Vorlage-Mapping alpha/beta/stable), Build-Badge zwischenzeitlich „no status", CHANGELOG.md weglassen (nicht existent), LICENSE-Datei in Phase 1 statt jetzt anlegen, Sprache Deutsch.
- **Inhalt der README:** 7 Badges in 2 Zeilen (Klasse G Maximum 10, sechs darunter wegen Konzeptionsphase); Einzeiler aus `vision.md` Abschnitt 1; „Über das Projekt"-Block aus `vision.md` 1+2+3+5; Status-Block synchronisiert mit `project-context.md`, `fahrplan.md`, `architecture.md` Abschnitt 9, `decisions.md` Teil A, `blockers.md`; Quick Start als „Heute lauffähig" mit Klon-Anleitung plus Phase-1-Hinweis (kein Aspirational-Inhalt); Architektur-Skizze als vereinfachte Mermaid plus 1-Satz-Modulliste; Verwendung explizit auf Phase 4 verschoben; Nächste Schritte mit drei konkreten Punkten (Modus-2-Restschritte, Phase 1, Phase 2); Mitwirken aus CLAUDE.md 11 + project-context.md 7+10; Doku-Tabelle ohne CHANGELOG.md; Lizenz mit Hinweis auf späteres LICENSE-File.
- **Entfernt:** Vorlage „Badge-Auswahl pro Klasse" (~58 Zeilen) und Initialisierungs-Hinweis am Dateiende (~10 Zeilen). Methodik-relevante HTML-Kommentare am Datei-Anfang plus im Status-Block-Bereich behalten – sie sind Pflege-Hinweise, keine Initialisierungs-Vorlage.
- **Beobachtung zur Vorlage:** Badge-Vorlage erwartet „alpha / beta / stable / maintenance / deprecated" als Status-Werte; `project-context.md` führt aber „Konzeption / Aufbau / aktive Entwicklung / Wartung / deprecated". Das ist eine Vorlagen-/Projekt-Diskrepanz, die ich zugunsten von `project-context.md` aufgelöst habe (CLAUDE.md Abschnitt 16 macht `project-context.md` zur Quelle für den Status-Block). Vermerk: falls die Vorlagen-CLAUDE.md projektübergreifend angepasst wird, sollten die beiden Status-Listen vereinheitlicht werden – aber das ist Methodik-Diskussion, nicht Schritt-9-Aufgabe.

### 2026-05-07 23:20 – [BEOBACHTUNG]

- **Modus-2-Schritt 8 abgeschlossen, `logbuch.md` Vorlagen-Cleanup durchgeführt.**
- **Entfernt:** sechs Beispiel-Einträge mit `YYYY-MM-DD HH:MM`-Platzhaltern (PROBLEM-GELÖST, PROBLEM-OFFEN→BLOCKER, SESSIONSTART, BEOBACHTUNG, REIFEGRAD-WECHSEL, ADR-ANGELEGT) sowie der Initialisierungshinweis am Dateiende.
- **Beibehalten:** chronologische Einträge ab 2026-05-07 14:00 (Klärungs-Session) bis aktuell, Eintragstypen-Übersicht mit Pflicht-/Empfehlungs-Markierung, Hinweise zur Pflege (neueste oben, Zeitstempel-Format, Detailtiefe lieber zu hoch, Verweise statt Duplikation, keine Secrets), Archivierungs-Block (>800 Zeilen).
- **Folgenüberlegung:** Logbuch hat aktuell ca. 200 Zeilen, weit unter der 800-Zeilen-Auslagerungsschwelle. Nächste Auslagerungs-Prüfung erst beim Wachstum oder nach mehreren Wochen aktiver Sessions.

### 2026-05-07 23:05 – [BEOBACHTUNG]

- **Modus-2-Schritt 7 abgeschlossen, `blockers.md` auf Startzustand gebracht.**
- **Aktive Blocker:** keine. Begründung im Dokument festgehalten: alle Schublade-1-Grundsatzfragen geklärt (Logbuch 14:25 bis 16:20), alle Schublade-2-Spikes G–M in Phasen 3 + 5 platziert, alle Schublade-3-Roadmap-Meilensteine N/O/P in Phase 7 platziert. Härtungs-Schritt (Modus-2-Schritt 3) hatte keine Blocker hinterlassen.
- **Beibehalten:** Blocker-Erkennungs-Heuristiken (5 Muster für Sofort-Eskalation ohne Dreifach-Versuch) plus Eintrags-Format-Vorlagen für aktive und gelöste Blocker. Initialisierungs-Hinweis am Dateiende entfernt.
- **Nummerierungs-Regel** explizit dokumentiert: durchgehend, keine Lücken, gelöste Blocker behalten ihre Nummer. Erster Eintrag wäre `#001`.

### 2026-05-07 22:50 – [BEOBACHTUNG]

- **Modus-2-Schritt 6 abgeschlossen, `fahrplan.md` mit 7 regulären Phasen + 1 späterer Erweiterungs-Phase X befüllt.**
- **Phasen-Struktur:**
  - **Phase 1** Repo-Bootstrap & Tech-Foundations (UMSETZUNG, voll detailliert mit 8 Schritten 1.1–1.8 im Schritt-Format).
  - **Phase 2** Auth + Tenants + Verbund-Tauglichkeit I1/I2 (UMSETZUNG, gröber, 7 Schritte).
  - **Phase 3** Spikes Wave 1 (ERKUNDUNG, Spikes I + J).
  - **Phase 4** Operations Core + Realtime + Einsatzkraft-PWA (UMSETZUNG, gröber, 6 Schritte).
  - **Phase 5** Spikes Wave 2 (ERKUNDUNG, Spikes G + H + K + L + M).
  - **Phase 6** Geo + Frontends + Resilience + Retention + Export (UMSETZUNG, gröber, 7 Schritte).
  - **Phase 7** Stabilisierung + Roll-out + Roadmap N/O/P (STABILISIERUNG, 8 Schritte).
  - **Phase X** Verbund-Modus später (ERKUNDUNG → UMSETZUNG, sehr grob, 6 Schritte).
- **Disziplin-Wahl:** Spikes wurden gebündelt in eigene ERKUNDUNG-Phasen 3 und 5 vor den jeweiligen UMSETZUNG-Phasen 4 und 6, statt sie innerhalb von UMSETZUNG-Phasen einzuschieben. Begründung: `CLAUDE.md` Abschnitt 6 Phasentyp-Disziplin verbietet Vermischung. Kosten: 7 Phasen sind das Maximum für Klasse G – Verbund-Modus läuft als Phase X außerhalb der Hauptliste, bis er aktiv wird.
- **Phase-1-Sonderregel** bewusst dokumentiert: Eingangs-Disziplin „alle berührten Bestandteile auf [BELASTBAR]" abgemildert, weil Bootstrap-Phase die initialen Skelette herstellt und nur strategische Modul-Schnitt-Fixierung (durch ADR-002, ADR-003, ADR-004) als Eingangsbedingung verlangt. Vermerkt direkt in der Phasen-Beschreibung, damit es bei späteren Sessions nicht als versehentliche Aufweichung gelesen wird.
- **Spike-Zuordnung im Detail** in der Phasen-Übersichts-Tabelle festgehalten, plus Roadmap-Meilensteine N/O/P explizit Phase 7 zugeordnet. Damit ist die Brücke zwischen Schubladen-Triage (Logbuch 2026-05-07 16:35) und konkretem Fahrplan vollständig.
- **Replanning-Historie** mit dem Initial-Eintrag 2026-05-07 versehen.
- **Iterations-Reflexion-Vorlage** für Phase 1 belassen; wird beim Phase-1-Abschluss befüllt.
- **Beobachtung zur Vorlage:** Phase-1-Schritt-Format mit 13 Pflichtfeldern pro Schritt × 8 Schritte ist sehr lang (~330 Zeilen für Phase 1). Lesbar, aber an der Grenze. Falls Phase 2+ vergleichbar voll dokumentiert würden, wäre Auslagerung in `fahrplan-<modul>.md`-Teil-Dokumente nötig. Spätere Phasen sind hier bewusst grob gehalten, Verfeinerung kurz vor Phasen-Beginn.

### 2026-05-07 22:10 – [ADR-ANGELEGT]

- **Block-Anlage Modus-2-Schritt 5:** ADR-001 bis ADR-009 in einem Zug in `decisions.md` befüllt.
  - **ADR-001** [STRATEGISCH] [METHODIK] – Projektgrößen-Klassifikation Klasse G. **Auslöser:** Stufe-2-Bestätigung am Ende des Architektur-Grobschnitts (`architecture.md` Abschnitt 10) deckt sich mit Stufe-1-Hypothese aus Modus-2-Schritt 1.
  - **ADR-002** [STRATEGISCH] [STACK] [DEPLOYMENT] – Stack-Wahl FastAPI + SvelteKit + PostgreSQL + Valkey + Procrastinate. **Auslöser:** Verifikations-Stempel `Verifiziert: 2026-05-07` für alle gelisteten Komponenten in `project-context.md` Abschnitt 3.
  - **ADR-003** [STRATEGISCH] [METHODIK] – Architektur-Pattern Modular Monolith Backend + 3 SvelteKit-Frontends + Tile-Proxy + Reverse-Proxy. **Auslöser:** Modul-Karte und Architektur-Pattern in `architecture.md` Abschnitt 1+2.
  - **ADR-004** [STRATEGISCH] [SECURITY] – Admin-Bootstrap-Flow als CLI-Befehl. **Auslöser:** Klärung Frage A am 2026-05-07 14:25.
  - **ADR-005** [STRATEGISCH] [SECURITY] – AccessCode-Schema 6 Zeichen Crockford-Base32. **Auslöser:** Klärung Frage B am 2026-05-07 14:45.
  - **ADR-006** [STRATEGISCH] [DATENMODELL] – Aggregations-Schema pro Operation, ohne Personen-Buckets. **Auslöser:** Klärung Frage C am 2026-05-07 15:05.
  - **ADR-007** [STRATEGISCH] [SCHNITTSTELLE] [DATENMODELL] – Datenexport asynchron via Procrastinate-Job-Tripel. **Auslöser:** Klärung Frage D am 2026-05-07 15:25.
  - **ADR-008** [STRATEGISCH] [MODUL] [DATENMODELL] – Multi-Disponent ohne Lead, vollständiges `operation_audit_log`. **Auslöser:** Klärung Frage E am 2026-05-07 15:50.
  - **ADR-009** [STRATEGISCH] [DATENMODELL] – Verbund-Reinterpretation V2 plus Phase-1-Invarianten I1–I5. **Auslöser:** Klärung Frage F am 2026-05-07 16:20.
- **Reaktiv-Quote initialisiert:** 0/9 = 0 % `[REAKTIV]`-Anteil. Schwellenwert Klasse G: 20 %. Keine Reflexion nötig.
- **Aus den ADRs abgeleitete 14 Regeln** in Teil C eingetragen (Versionsdisziplin, Stack-Ausschlüsse, Modulgrenzen-Pflicht, Frontend↔Externer-Service-Verbot, CLI-Bootstrap, AccessCode-Hashing/-Toggle-Verhalten, Aggregat-Schreibung, Personen-Bucket-Verbot, Async-Mandanten-Operationen, Audit-Log-Pflicht/Confirmation-Dialog, Tenant-Participation als alleinige Verknüpfung, Teilnahme-Filter-Formulierung).

### 2026-05-07 21:39 – [SESSIONSTART]

- **Letzter Stand:** Modus-2-Schritt 4 abgeschlossen. PR #2 (`init(modus-2): Schritt 4 abgeschlossen, architecture.md befüllt`, Commit `d2c910f`) am 2026-05-07 in `main` gemerged (Merge-Commit `5a5f21e`). Architektur-Grobschnitt mit 14 Modulen, 10 Schnittstellen S1–S10, 5 Datenflüssen F1–F5, ER-Datenmodell, NFRs und Reifegrad-Übersicht steht. Stufe-2-Klassifikation Klasse G bestätigt.
- **Geplant für diese Session:** Modus-2-Schritt 5 – `decisions.md` von Vorlagen-Zustand auf vollständigen ADR-Satz befüllen. ADR-001 Klassifikation (G), ADR-002 Stack-Wahl, ADR-003 Architektur-Pattern, ADR-004 bis ADR-009 für die in Schublade 1 geklärten Fragen A–F. Teil A (Übersicht) und Teil C (Regeln) entsprechend pflegen. Reaktiv-Quote initialisieren.
- **Vorabprüfung:** Modus 2 weiterhin INITIALISIERUNG. Eingangskriterien für Schritt 5: Klärungs-Session Schublade 1 vollständig (erfüllt, Logbuch-Einträge 14:25 bis 16:20), Architektur-Grobschnitt vorhanden mit Verworfenen-Alternativen-Liste in `architecture.md` Abschnitt 8 (erfüllt), Verifikations-Stempel Stack 2026-05-07 (erfüllt, `project-context.md` Abschnitt 3). `decisions.md` ist Vorlagen-Zustand. Keine offenen STOPPs.
- **Methoden-Korrektur aus Sessionstart:** Bei der Pflichtlektüre habe ich zunächst nicht erkannt, dass Schritt 4 auf einem parallelen Worktree-Branch (`scp/trusting-tereshkova-b09abc-step-4`) bereits durchgeführt war. Nach `git fetch --all` plus User-Hinweis fand ich den Commit `d2c910f`. PR #2 wurde noch während meiner Klärung gemerged, mein Worktree-Branch via Fast-Forward auf `5a5f21e` gebracht. Lerneffekt: Pflichtlektüre nach CLAUDE.md Abschnitt 2 sollte um einen Branch-Awareness-Check ergänzt werden – Vorschlag wandert in eine spätere CLAUDE.md-Diskussion.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus.

### 2026-05-07 19:30 – [SESSIONENDE]

- **Session-Dauer:** ca. 2 h (17:30–19:30).
- **Bearbeitet:** Modus-2-Schritt 4 abgeschlossen – `architecture.md` von Vorlagen-Zustand auf vollständigen Architektur-Grobschnitt befüllt. Architektur-Plan vorab abgestimmt und bestätigt; Stufe-2-Klassifikations-Bestätigung am Dokumentende.
- **Erreicht:**
  - Abschnitt 0 Reifegrad-System um Code-Bezeichner-Konvention ergänzt (Domänen-Übersetzungstabelle Deutsch→Englisch); Klärungs-Session-Tabellennamen `einsatz_mandant_teilnahme`/`einsatz_audit_log` werden im Code als `operation_tenant_participation`/`operation_audit_log` umgesetzt.
  - Abschnitt 1 Überblick + Architektur-Pattern „Modular Monolith Backend + 3 SvelteKit-Frontends + nginx-Tile-Proxy + Caddy-Reverse-Proxy" formuliert.
  - Abschnitt 2 Modul-Karte als Mermaid-Top-Level (Frontends → Reverse-Proxy → Backend → Tile-Proxy → MapTiler/TomTom; PostgreSQL/Valkey/File-Volume).
  - Abschnitt 3 alle 14 Module detailliert (Reifegrad, Verantwortung, Nicht-Verantwortung, Schnittstellen-Verweis, interne Struktur, Abhängigkeiten, NFRs, offene Fragen).
  - Abschnitt 4 zehn Schnittstellenverträge S1–S10 (CLI-Bootstrap, Anonymous Session API, Operations Event Bus, Vehicle Assignment, Retention-Trigger, Tenant Data Export Tripel, Geo→Tile-Proxy, Auth-REST-API, WebSocket-Topologie, Tenant Participation Lookup).
  - Abschnitt 5 fünf Datenflüsse F1–F5 (Mandanten-Onboarding, Einsatzkraft-Bestellung Hard-Path, Disponenten-Aktion mit Audit-Log, Operation-Ende→Aggregat→Anonymisierung, asynchroner Datenexport).
  - Abschnitt 6 NFRs (Performance, Skalierung, Security, Observability, Datenschutz) mit Reifegrad-Verteilung.
  - Abschnitt 7 Datenmodell-Grobübersicht als Mermaid-ER mit zentralen Entitäten und Erläuterung der Phase-1-Invarianten I1/I4 + Lebensdauer-Felder.
  - Abschnitt 8 Verworfene Alternativen aus den Klärungen (Lead-Modell, synchroner Export, ENV-Bootstrap, Web-Setup-Wizard, Hybrid-Setup-Link, Verbund-Phase-1, Cross-Anzeige, Pseudonyme-Hashes, Karten-Snapshots, Single-Use-Codes, 4-stellige PIN); ADR-Nummern folgen in Schritt 5.
  - Abschnitt 9 Reifegrad-Übersicht: ~50 Bestandteile als Tabelle (1 BELASTBAR Kommunikations-Grundmodus + 1 BELASTBAR Procrastinate + diverse VORLÄUFIG-Module/Schnittstellen/NFRs + sieben OFFEN-Bereiche für die Spikes G–M plus NFR Bedrohungsmodell und Tracing).
  - Abschnitt 10 Stufe-2-Klassifikations-Bestätigung: Klasse G **bestätigt** (16 Komponenten, 5 zentrale externe Abhängigkeiten, 2 Sprachen, 2 Persistenzschichten, eine Compose-Einheit – nicht Klasse V, weil kein verteilter Lebenszyklus). Keine Anpassung der Hypothese aus Schritt 1 nötig.
  - `fahrplan.md` „Aktueller Stand"-Block aktualisiert auf Schritt 5.
- **Offen geblieben:** Modus-2-Schritte 5 (decisions.md mit ADRs A–F + ADR-001/002/003 + Vision-V2-Reinterpretation), 6 (fahrplan.md mit Phasen + Schubladen 2/3), 7 (blockers.md), 8 (logbuch Vorlagen-Cleanup), 9 (README.md), 10 (CI-/Hook-Skelett), 11 (vision Überführungsstatus), 12 (Init-Commit).
- **Nächster Schritt:** Modus-2-Schritt 5 – `decisions.md` befüllen. ADR-Reihenfolge:
  - ADR-001 [STRATEGISCH] [METHODIK]: Projektgrößen-Klassifikation Klasse G (Bestätigung Stufe 2).
  - ADR-002 [STRATEGISCH] [STACK]: Stack-Wahl (Backend + Frontend + Datenbanken + Infra, Verifikations-Stempel 2026-05-07).
  - ADR-003 [STRATEGISCH] [METHODIK]: Architektur-Pattern Modular Monolith + drei SvelteKit-Frontends.
  - ADR-004 [STRATEGISCH] [SECURITY]: Admin-Bootstrap-Flow (Frage A).
  - ADR-005 [STRATEGISCH] [SECURITY]: Zugangscode-Schema (Frage B).
  - ADR-006 [STRATEGISCH] [DATENMODELL]: Aggregations-Schema (Frage C).
  - ADR-007 [STRATEGISCH] [SCHNITTSTELLE]: Datenexport asynchron via Procrastinate (Frage D).
  - ADR-008 [STRATEGISCH] [MODUL]: Multi-Disponent ohne Lead (Frage E).
  - ADR-009 [STRATEGISCH] [DATENMODELL]: Verbund-Reinterpretation V2 + Phase-1-Invarianten I1–I5 (Frage F).
  - Teil A (Übersicht) und Teil C (Regeln) entsprechend pflegen.
- **Stimmung / Beobachtung:**
  - Vorab-Plan war wirkungsvoll – das Dokument ließ sich in einem Wurf sauber durchschreiben, ohne dass mitten im Schreiben Detail-Klärungen offen blieben. Die Klärungs-Session der vorigen Session hat sich hier ausgezahlt.
  - Code-Bezeichner-Konvention (Englisch im Code, Domänenbegriffe übersetzt) habe ich proaktiv eingeführt, weil `project-context.md` Codesprache Englisch verlangt, aber Klärungs-Session deutsche Tabellennamen produziert hatte. Inkonsistenz war im Hintergrund; jetzt sauber dokumentiert mit Übersetzungstabelle. Das ist keine Vision-Änderung, sondern Code-Konvention.
  - `[OFFEN]`-Bereiche sind klar von Spikes G–M referenziert – die Verbindung Architektur→Fahrplan-Spike ist jetzt ein-zu-eins. Das hilft beim Befüllen von Schritt 6.
  - Stufe-2-Klassifikations-Bestätigung hatte keine Überraschung; Klasse G war von Anfang an plausibel und wird jetzt durch den konkreten Architektur-Grobschnitt validiert.
  - Datei umfangreich (~700 Zeilen). Falls sie bei späterem Wachstum unübersichtlich wird, ist der Auslagerungspfad nach `architecture-<modul>.md` für besonders komplexe Module bereits in `CLAUDE.md` Abschnitt 1B Klasse G vorgesehen.

### 2026-05-07 19:25 – [REIFEGRAD-WECHSEL]

- **Bestandteile:** alle in `architecture.md` Abschnitt 9 gelisteten Bestandteile (Architektur-Pattern, Kommunikations-Modi, 14 Module, 10 Schnittstellen, 9 NFRs, 6 Datenmodell-Invarianten, 7 Spike-OFFEN-Bereiche, Datenmodell-Grobschnitt).
- **Wechsel:** Initial-Vergabe (Vorlagen-Zustand → konkreter Reifegrad). Verteilung:
  - `[BELASTBAR]`: 9 (Vision-/Stack-fixierte Bestandteile – REST/JSON, WebSocket-Grundmodus, HTTP-Tile-Proxy-Routing, Procrastinate, Datenschutz-Constraints, NFRs Tile-Cache-TTL, Routing-Disziplin, Backend-Multi-Architektur, PWA-Offline-Pflicht, Coverage-Mindestwerte).
  - `[VORLÄUFIG]`: ca. 35 (Module, Schnittstellen, Datenmodell-Invarianten, Skalierungs-/Performance-Annahmen, weitere NFRs).
  - `[OFFEN]`: 9 (Spike G/H/I/J/K/L/M plus NFR Bedrohungsmodell, NFR Tracing).
- **Auslöser:** Modus-2-Schritt 4, befüllt aus Klärungs-Ergebnissen Schublade 1 + Vision-Stack + Klassifikations-Bestätigung.
- **Datum in `architecture.md` Abschnitt 9 nachgetragen:** ja, 2026-05-07.

### 2026-05-07 17:30 – [SESSIONSTART]

- **Letzter Stand:** PR #1 erstellt (`init(modus-2): offene Grundsatzfragen vor Schritt 4 geklärt`, Commit `4853e0c`), Klärungs-Session abgeschlossen, Schublade 1 (Fragen A–F) durchgearbeitet, Schubladen 2/3 als Fahrplan-Skizzen für Schritt 6 abgelegt.
- **Geplant für diese Session:** Modus-2-Schritt 4 – `architecture.md` befüllen. Modul-Karte aus `project-context.md` Abschnitt 4 in Mermaid übertragen; Reifegrade hypothesengetreu setzen (`[VORLÄUFIG]` als Default, `[BELASTBAR]` nur bei harten Vision-Konstraints, `[OFFEN]` für Schublade-2-Punkte mit Verweis auf Spike); Schnittstellenverträge skizzieren für die durch Schublade 1 jetzt klar gewordenen Kontaktstellen; Stufe-2-Klassifikations-Bestätigung am Ende.
- **Vorabprüfung:** Modus 2 weiterhin INITIALISIERUNG. `architecture.md` ist Vorlagen-Zustand (kein Reifegrad vergeben). Eingangskriterien für Schritt 4: Schublade 1 vollständig geklärt (erfüllt), Stack fixiert (erfüllt, `project-context.md` Abschnitt 3 + Verifikation 2026-05-07), Modul-Liste in `project-context.md` Abschnitt 4 vorhanden (erfüllt). Keine offenen STOPPs.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus.

### 2026-05-07 16:35 – [BEOBACHTUNG]

- **Schublade 2 + 3 für Modus-2-Schritt 6 vorbereitet, Klärungs-Session abgeschlossen.**
- **Schublade 2 (ERKUNDUNG-Spikes vor jeweiliger UMSETZUNG-Phase, in `fahrplan.md` aufzunehmen):**
  - **G — Sperrungs-Override-Technik:** ERKUNDUNG/Spike, 4–8 h, klärt TomTom-Custom-Areas vs. Route-Bias vs. Penalty-Map; Datenbedarf bei Override-Pflege; API-Budget-Folgen. Liegt vor erster UMSETZUNG-Phase mit `backend/geo`. Ergebnis: ADR mit Technikwahl.
  - **H — Resilience-Granularität:** ERKUNDUNG/Vergleichsstudie+Prototyp, 6–8 h, klärt Backup-Strategie (logical/physical, RTO/RPO), Recovery-Reihenfolge (Procrastinate-Job-State + Detail-Daten), Verhalten bei Crash mitten im Auftragsstatus-Wechsel, Erfahrung reconnect WebSocket nach State-Reload. Liegt vor UMSETZUNG `backend/resilience`. Ergebnis: ADR „Backup-Frequenz, Recovery-Reihenfolge, getestete RTO".
  - **I — Geografischer Plausibilitäts-Algorithmus:** ERKUNDUNG/Spike, 4 h, klärt Distanz-Metrik (Hülle vs. Mittelpunkt), GPS-Ungenauigkeit, Text-Standort-Behandlung, mandanten-konfigurierbarer Schwellenwert (Default 5 km). Liegt vor UMSETZUNG Einsatzkraft-Bestellpfad in `backend/operations`. Ergebnis: Pseudocode + Test-Datensatz.
  - **J — Bündelungs-Trigger:** ERKUNDUNG/Vergleichsstudie, 4 h, klärt Auslöser (System-Heuristik vs. Disponenten-manuell vs. Versorgungs-Transporter-Crew), UI-Auswirkung, Aggregat-Wirkung auf `anzahl_buendelungen`. Liegt vor UMSETZUNG Großbestellungs-Modus. Ergebnis: ADR Auslöser-Wahl Phase 1 (Vermutung: manuell durch Disponent).
  - **K — Hilfe-Knopf-Semantik:** ERKUNDUNG/Spike, 2–3 h, klärt Pflichtfeld-Beschreibung, Disponenten-Eskalations-Sichtbarkeit, Quittungspfad zum Betreuer, kein PII-Speicher. Liegt vor UMSETZUNG `frontend-betreuer`-Hilfe-Knopf. Ergebnis: UX-Konzept + Datenmodell-Skizze.
  - **L — Kartenmaterial-Offline-Caching-Technik:** ERKUNDUNG/Prototyp, 6–8 h, klärt Workbox-Strategie für Tile-Cache, Pre-Cache des Einsatzraums beim Schichtbeginn, Tile-Lebensdauer (≥ 7 Tage konsistent mit nginx-Cache), Speicher-Quota mobiler Browser. Liegt vor UMSETZUNG `frontend-betreuer`-Karten-Anzeige produktiv. Ergebnis: Prototyp + Konfigurations-ADR.
  - **M — Fahrzeugbezeichnungs-Schema:** ERKUNDUNG/Vergleichsstudie + Stakeholder-Rückfrage DPolG, 2 h netto, klärt Naming-Konvention (z. B. „EB-Bremen-01" oder verbandseigene Funkrufnamen), Eindeutigkeit pro Mandant vs. global, Längen-Constraints. Liegt vor erstem Roll-out, kein Architektur-Blocker. Ergebnis: ADR „Fahrzeug-Naming".
- **Schublade 3 (organisatorische Roadmap-Meilensteine ohne Code):**
  - **N — Plattform-Betreiber-Governance:** Klärung vor Produktivbetrieb (Patrick persönlich vs. Trägerverein vs. Stiftung). Berührt Haftung, DSGVO-Verantwortlichkeit, Mandanten-Vertragsgestaltung. Verknüpft mit „Administrator-Architektur bei Multi-Tenancy" (Skalierungsfrage zentraler vs. mehrere Plattform-Admins).
  - **O — Test-Termin reale Großlage:** konkretes Datum von DPolG + Patrick zu setzen, Anker im 3–6-Monats-Fenster. STABILISIERUNG-Phase als Validierungs-Anker.
  - **P — Schriftliche Onboarding-Unterlagen:** DSGVO-Datenverarbeitungs-Vereinbarung, Nutzungsbedingungen, Haftungsklarheit. Pflicht-Voraussetzung für Mandanten-Freischaltung. Verknüpft mit N (Trägerstruktur beeinflusst Vertragsgestaltung).
- **Bestätigung Patrick:** Triage geht so in Modus-2-Schritt 6 ein.

### 2026-05-07 16:20 – [BEOBACHTUNG]

- **Grundsatzfrage F (Parallele Mandanten an derselben Großlage) geklärt:** Verbund-Modus mit gemeinsamem Auftragspool ist Ziel, aber nicht Phase 1. Vision-Verhältnis: V2 (Reinterpretation – Verbund als opt-in-Erweiterung mit beidseitigem Konsens, Default-Trennung bleibt). Phase: P2 (Phase 1 architektonisch verbund-tauglich vorbereiten, eigentliche Verbund-Funktionalität in späterer UMSETZUNG-Phase). Fünf Phase-1-Invarianten festgelegt (I1 Verknüpfungstabelle `einsatz_mandant_teilnahme`, I2 abstrakter Berechtigungs-Filter, I3 Fahrzeug-Zuweisung über Einsatz-Kontext, I4 Aggregat einstweilen mit einer `mandant_id`, I5 Datenexport einstweilen auf Eigentümer-Rolle reduziert). Keine eigenes `backend/verbund`-Modul in Phase 1. Spätere Verbund-Phase wird in Modus-2-Schritt 6 in `fahrplan.md` als Phase mit ERKUNDUNG-Vorlauf aufgenommen. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 15:50 – [BEOBACHTUNG]

- **Grundsatzfrage E (Multi-Disponent-Hierarchie) geklärt:** Kein Lead-Modell. Alle Disponenten am Einsatz voll gleichberechtigt, einschließlich destruktiver Aktionen. Vollständiges Audit-Log (Tabelle `einsatz_audit_log`) ersetzt Lead-Schutz durch retrospektive Nachvollziehbarkeit. UX-Bestätigungs-Dialog vor destruktiven Aktionen im `frontend-disponent`. Begründung Patricks: Plattform-Administrator nicht zuverlässig erreichbar; Disponenten haben den operativen Überblick und müssen handlungsfähig bleiben. Audit-Log liefert zugleich Datenbasis für Aggregations-Felder aus Frage C. Abweichung von der ursprünglichen Empfehlung (Lead-Modell mit Eröffner-Default) – Begründung gilt als geklärt aufgenommen. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 15:25 – [BEOBACHTUNG]

- **Grundsatzfrage D (Datenexport-Format und Granularität) geklärt:** asynchron via Procrastinate-Job, API-Tripel POST/GET/GET-Download, ZIP mit JSON pro Tabelle plus manifest.json, vollständige Mandanten-Daten ohne externe Anhänge, Self-Service Mandant + Plattform-Admin-Override, 7 Tage Aufbewahrung mit Cleanup-Job. Endpunkt-Skizze in `project-context.md` Abschnitt 6 entsprechend angepasst. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 15:05 – [BEOBACHTUNG]

- **Grundsatzfrage C (Aggregations-Schema) geklärt:** Aggregation pro Einsatz, finaler Snapshot beim Einsatz-Ende; Metriken-Set ohne Personen-Buckets (Bestellungen, Fahraufträge, Stornos, Bündelungen, Versorgungs-Transporter-Modi, Zugangscode-Status, Strecken-Freigaben, Hilfe-Meldungen, Gesamt-Distanz gerundet, Spitzenwerte aktiver Fahrzeuge/Disponenten); Stadt-Label statt Geometrie in Phase 1; Mandanten-Trennung beim Zugriff; Aggregat-Schreibung entkoppelt vom 30-Tage-Anonymisierungs-Job. Begründung in `project-context.md` Abschnitt 11. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 14:45 – [BEOBACHTUNG]

- **Grundsatzfrage B (Zugangscode für Einsatzkraft-PWA) geklärt:** 6 Zeichen Crockford-Base32, ein Code pro Einsatz wiederverwendbar, Toggle wirkt nur auf neue Sessions, Disponenten-UI mit Anzeige+Copy+QR (kombinierte URL), keine Rotation in Phase 1. Begründung in `project-context.md` Abschnitt 11. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 14:25 – [BEOBACHTUNG]

- **Grundsatzfrage A (Admin-Bootstrap-Flow) geklärt:** CLI-Befehl `python -m eb_digital admin create`, jederzeit nutzbar, Passwort interaktiv. Verworfen: ENV-Bootstrap (Klartext-Risiko), Web-Setup-Wizard (Race + früher UI-Code), Hybrid-Setup-Link (Logs als Sekundär-Faktor problematisch). Eintrag in `project-context.md` Abschnitt 11 als geklärt markiert. ADR-Anlage erfolgt im Block in Modus-2-Schritt 5.

### 2026-05-07 14:00 – [SESSIONSTART]

- **Letzter Stand:** Initialisierungs-Commit `3b92368 init(modus-2): Schritte 1-3 abgeschlossen, project-context.md gehärtet`. Modus 2 Schritte 1 (Klassifikations-Hypothese), 2 (project-context vorbefüllt), 2a (Versions-Verifikation 2026-05-07) und 3 (Härtungs-Schritt) abgeschlossen. Schritte 4–12 (architecture, decisions, fahrplan, blockers, logbuch, README, CI-Skelett, Vision-Status, Init-Commit) stehen noch aus.
- **Geplant für diese Session:** Klärung der offenen Grundsatzfragen aus `project-context.md` Abschnitt 11 vor Befüllung von `architecture.md` (Modus-2-Schritt 4). Triage in „jetzt klären / als Erkundungs-Schritt einplanen / organisatorisch offen lassen" und anschließend Punkt für Punkt durchgehen.
- **Vorabprüfung:** Wir sind weiterhin in Modus 2 (Initialisierung), Phasentyp INITIALISIERUNG. Architektur-Reifegrade noch nicht vergeben. Pflichtlektüre vollständig gelesen plus Vertiefung `vision.md` (Auslöser: Grundsatzfragen verweisen direkt auf Vision Abschnitt 9).
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus.

### 2026-05-07 16:55 – [SESSIONENDE]

- **Session-Dauer:** ca. 3 h (14:00–16:55).
- **Bearbeitet:** Klärungs-Session der offenen Grundsatzfragen aus `project-context.md` Abschnitt 11; Triage in drei Schubladen; Schublade 1 (Fragen A–F) vollständig durchgearbeitet; Schublade 2 (G–M) und Schublade 3 (N/O/P) als Fahrplan-Skizzen für Modus-2-Schritt 6 vorbereitet und bestätigt.
- **Erreicht:**
  - **Frage A (Admin-Bootstrap-Flow) → CLI-Befehl, jederzeit nutzbar.**
  - **Frage B (Zugangscode) → 6 Zeichen Crockford-Base32, ein Code pro Einsatz, QR-Unterstützung, keine Rotation in Phase 1.**
  - **Frage C (Aggregations-Schema) → pro Einsatz, festes Metriken-Set, Stadt-Label statt Geometrie, Mandanten-Trennung beim Zugriff, Aggregat-Schreibung entkoppelt vom Anonymisierungs-Job.**
  - **Frage D (Datenexport) → asynchron via Procrastinate, ZIP+JSON pro Tabelle plus manifest.json, Self-Service Mandant + Plattform-Admin, 7 Tage Aufbewahrung.** Endpunkt-Skizze in `project-context.md` Abschnitt 6 entsprechend angepasst (Job-Tripel POST/GET/GET-Download).
  - **Frage E (Multi-Disponent) → kein Lead-Modell, alle gleichberechtigt, vollständiges Audit-Log (`einsatz_audit_log`).**
  - **Frage F (Parallele Mandanten) → Verbund-Modus als Ziel, Phase 1 nur architektonisch verbund-tauglich; fünf Phase-1-Invarianten festgelegt (I1 Verknüpfungstabelle `einsatz_mandant_teilnahme`, I2 abstrakter Filter, I3 Fahrzeug-Zuweisung über Einsatz-Kontext, I4 Aggregat einstweilen mit einer `mandant_id`, I5 Datenexport einstweilen auf Eigentümer-Rolle).**
  - `project-context.md` Abschnitt 11 mit allen sechs „GEKLÄRT 2026-05-07"-Einträgen und Triage-Vermerk konsolidiert.
  - `fahrplan.md` „Aktueller Stand"-Block aktualisiert (Modus-2-INITIALISIERUNG mit nächstem Schritt 4).
- **Offen geblieben:** Modus-2-Schritte 4 (architecture.md), 5 (decisions.md mit ADRs A–F + ggf. ADR für Vision-V2-Reinterpretation aus Frage F), 6 (fahrplan.md mit Schublade 2 + 3), 7 (blockers.md), 8 (logbuch Vorlagen-Cleanup), 9 (README.md), 10 (CI-/Hook-Skelett), 11 (vision Überführungsstatus), 12 (Init-Commit). Schubladen 2 und 3 als Skizzen im Logbuch-Eintrag 16:35 abgelegt – beim Befüllen von `fahrplan.md` direkt verwertbar.
- **Nächster Schritt:** Modus-2-Schritt 4 – `architecture.md` befüllen. Eingangsfragen: Modul-Karte aus `project-context.md` Abschnitt 4 in Mermaid übertragen; Reifegrade hypothesengetreu setzen (`[VORLÄUFIG]` als Default, `[BELASTBAR]` nur bei harten Vision-Konstraints); Schnittstellenverträge für die durch Schublade 1 jetzt klar gewordenen Kontaktstellen skizzieren (`backend/auth` CLI, `backend/auth_anonymous` Code-Validierung, `backend/operations` Lead-freie Auftragslogik plus Audit-Log, `backend/retention` Aggregat-Schreibung beim Einsatz-Ende, `backend/export` Job-Tripel, `einsatz_mandant_teilnahme`-Invarianten). Stufe-2-Klassifikations-Bestätigung am Ende des Architektur-Grobschnitts.
- **Stimmung / Beobachtung:**
  - Triage in Schubladen vor der eigentlichen Klärung war wirkungsvoll – sie hat verhindert, dass sekundäre Fragen mit den Architektur-blockierenden vermischt wurden.
  - Frage F war die einzige mit echtem Vision-Konflikt-Risiko. Nachfragen zu V1/V2/V3 plus P1/P2/P3 hat eine fast unbemerkte Vision-Aufweichung verhindert. Lerneffekt: bei freigabepflichtigen Architekturen mit Vision-Berührung lieber zwei Klärungs-Sätze als einen langen Architekturbau-Folgeaufwand.
  - Frage E zeigte die Pflicht zu „nicht stillschweigend interpretieren": die Begründung Patricks zu 4.B passte nicht zur Option, die er gewählt hatte – Nachfrage hat eine ganz andere Variante (Var.3 = kein Lead) zutage gefördert.
  - README ist noch im Vorlagen-Zustand und deshalb in dieser Session nicht synchronisiert worden – das ist kein Drift-Bug, sondern Modus-2-Schritt 9 nimmt sie in Betrieb. Vermerk hier, damit die Sessionende-Disziplin (CLAUDE.md Abschnitt 12 + 16) bewusst dokumentiert nicht erfüllt wurde, weil das Dokument zum Zeitpunkt des Sessionendes noch nicht aktiv ist.

---

## Eintragstypen (Übersicht)

Verbindliche Typen, andere nur in Ausnahmefällen:

| Typ | Wann | Pflicht? |
|---|---|---|
| `[SESSIONSTART]` | Zu Beginn jeder Session | Ja |
| `[SESSIONENDE]` | Vor Sessionabschluss | Ja |
| `[PROBLEM-GELÖST]` | Nach Behebung eines Problems, das Reibung war | Empfohlen, alle Mini-Probleme erfassen |
| `[PROBLEM-OFFEN → BLOCKER]` | Wenn ein Problem zum Blocker eskaliert | Ja, mit Verweis auf `blockers.md` |
| `[BLOCKER-AUFGELÖST]` | Wenn ein Blocker gelöst wurde | Ja, mit Verweis auf den ursprünglichen Logbuch- und Blocker-Eintrag |
| `[REIFEGRAD-WECHSEL]` | Bei jeder Reifegrad-Änderung in `architecture.md` | Ja |
| `[ADR-ANGELEGT]` | Bei Anlage eines neuen ADR | Ja |
| `[BEOBACHTUNG]` | Wenn etwas auffällt, das später nützlich sein könnte | Optional, KI proaktiv |

## Hinweise zur Pflege

- **Neueste Einträge oben.** Lesefluss bei Sessionbeginn ist „von oben nach unten bis zum letzten gelesenen Stand".
- **Zeitstempel ist Pflicht.** Format: `YYYY-MM-DD HH:MM` (24h, lokale Zeitzone). Bei Unsicherheit: das Datum ist Pflicht, die Uhrzeit kann grob sein.
- **Detailtiefe lieber zu hoch als zu niedrig.** Das Logbuch lebt davon, dass auch kleine Reibungen festgehalten werden – sie sind im Moment des Auftretens unscheinbar, aber später Goldwert. Wenn unsicher, ob etwas eingetragen werden soll: eintragen.
- **Verweise sind willkommen.** Wenn ein Logbuch-Eintrag mit einem ADR, einem Blocker oder einem Fahrplan-Schritt zusammenhängt: verweisen, statt zu duplizieren.
- **Keine sensiblen Daten.** Auch im Logbuch keine Secrets, keine echten PII, keine internen URLs aus Produktion. Platzhalter verwenden.

## Archivierung

Wenn das Logbuch unübersichtlich wird (Richtwert: >800 Zeilen, schneller wachsend als andere Dokumente):

- Alte Einträge nach `docs/archiv/logbuch-YYYY-MM.md` auslagern.
- Im aktiven Logbuch bleibt: die letzten 4–8 Wochen, plus alle Einträge, die mit aktuell offenen `blockers.md`-Einträgen verbunden sind.
- Auslagerung ist Sessionende-Aktion, keine freigabepflichtige Entscheidung.
