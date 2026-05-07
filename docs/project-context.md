# Project Context

<!-- Projektspezifischer Kontext. Wird zu Sessionbeginn als erste Datei gelesen.
     Dient als Entscheidungsgrundlage für alle autonomen Schritte der KI.
     Jede Angabe muss so konkret sein, dass daraus maschinell eindeutig Regeln ableitbar sind. -->

## 1. Kerndaten

- **Projektname:** [ausfüllen]
- **Kurzbeschreibung:** [1–2 Sätze: was das System tut und für wen]
- **Status:** [Konzeption | Aufbau | aktive Entwicklung | Wartung | deprecated]
- **Version (SemVer):** [z. B. v0.1.0]
- **Dokumentationssprache:** [z. B. Deutsch]
- **Codesprache (Kommentare, Variablennamen):** [z. B. Englisch]
- **Projekttyp:** [CLI | Web-Backend | Web-Frontend | Full-Stack | Daten-Pipeline | ML-System | Library | Mixed]

## 2. Zielgruppe und Nutzungskontext

- **Primäre Nutzer:** [wer verwendet das System, technisches Level]
- **Sekundäre Nutzer / Betreiber:** [wer installiert, konfiguriert, wartet]
- **Erwartete Last:** [z. B. „10 concurrent users", „1M Requests/Tag", „Batch-Jobs wöchentlich"]
- **Nutzungsumgebung:** [z. B. „Browser Desktop + Mobile", „CLI auf Linux/macOS", „Kubernetes-Cluster"]

## 3. Technischer Stack

### Fixiert

Pflicht: jede Version trägt einen Vermerk `Verifiziert: YYYY-MM-DD` (Datum, an dem der Mensch auf der offiziellen Quelle bestätigt hat, dass die Version aktuell, unterstützt und nicht durch Deprecations belastet ist). Verifikation wird in Modus 2 Schritt 2a ausgelöst (siehe `CLAUDE.md` Abschnitt 1A). Major-Updates erfordern eine erneute Verifikation und einen ADR.

- **Sprachen und Versionen:** [z. B. Python 3.12 — Verifiziert: 2026-05-02; TypeScript 5.3 — Verifiziert: 2026-05-02]
- **Frameworks:** [z. B. FastAPI 0.115 — Verifiziert: 2026-05-02; Next.js 15 — Verifiziert: 2026-05-02]
- **Datenbank:** [z. B. PostgreSQL 16 — Verifiziert: 2026-05-02]
- **Laufzeitumgebung:** [z. B. Docker Compose lokal, K8s in Prod — Verifiziert: 2026-05-02]
- **Package Manager:** [z. B. uv, pnpm — Verifiziert: 2026-05-02]

### Empfohlen (freigabefrei nutzbar)

[Bibliotheken, die bei Bedarf ohne separate Freigabe eingesetzt werden dürfen.
Beispiele: Standard-Test-Runner, Logging-Bibliothek, ORM, Linter.]

- [Bibliothek 1 – Einsatzzweck]
- [Bibliothek 2 – Einsatzzweck]

### Explizit nicht erlaubt

[Was bewusst ausgeschlossen ist, mit Begründung.
Verhindert, dass die KI naheliegende, aber unerwünschte Lösungen wählt.]

- [z. B. „Keine externen Cloud-Services (Self-Hosting-Prinzip)"]
- [z. B. „Keine GPL-lizenzierten Abhängigkeiten"]

## 4. Architektur-Grobstruktur

[2–5 Sätze. Details gehören in `architecture.md`.
Hier nur das, was für die Gesamtorientierung nötig ist.]

**Module (Kurzübersicht):**

- [Modul A] – [Kurzbeschreibung der Verantwortung]
- [Modul B] – [...]

**Kommunikationsmuster:** [z. B. „REST synchron intern, Events über Queue zwischen Backend und Worker"]

## 5. Externe Abhängigkeiten

### Services

| Service | Zweck | Authentifizierung | Ausfallverhalten |
|---|---|---|---|
| [Name] | [wofür] | [wie] | [Fallback bei Nichterreichbarkeit] |

### APIs

[Externe APIs mit Version, Rate Limits, Failure Modes.]

## 6. Constraints (operationalisierbar)

**Regel: Jeder Constraint muss in eine prüfbare Regel übersetzt sein. Schwammige Angaben wie „sicher" oder „schnell" gehören hier nicht hin.**

### Datenschutz

- [z. B. „Keine personenbezogenen Daten in Logs" → Regel: Logger-Wrapper mit Redaction-Liste verwenden]
- [z. B. „DSGVO-Art. 17: Löschfunktion für Nutzerdaten" → Regel: API-Endpunkt `DELETE /users/{id}` kaskadiert auf verknüpfte Tabellen]

### Sicherheit

- [z. B. „Alle Endpoints erfordern Authentifizierung außer `/health` und `/login`"]
- [z. B. „Passwörter werden mit argon2id gehasht, minimum 12 Zeichen, kein Maximum"]

### Performance

- [z. B. „p95-Antwortzeit < 200 ms bei bis zu 100 concurrent users"]
- [z. B. „Datenbankabfragen dürfen keine `SELECT *` verwenden"]

### Plattform und Kompatibilität

- [z. B. „Lauffähig auf x86_64 und arm64"]
- [z. B. „Minimum Node 20 LTS"]

### Compliance und Lizenz

- **Projektlizenz:** [z. B. MIT, AGPLv3, proprietär]
- **Erlaubte Abhängigkeitslizenzen:** [z. B. MIT, BSD, Apache-2.0, MPL-2.0]
- **Ausgeschlossene Lizenzen:** [z. B. GPL außer explizit freigegeben]

### Methodik-Schwellenwerte

- **Reaktiv-ADR-Schwellenwert:** [z. B. „maximal 30 % `[REAKTIV]`-Anteil über die letzten 10 ADRs"] – bei Überschreitung wird in `decisions.md` Teil B (Reaktiv-Quote) ein Hinweis ausgelöst, und Claude legt einen Reflexions-Schritt im Fahrplan an, bevor weitere Umsetzungsschritte beginnen.
- **Vorläufig-zu-Belastbar-Verhältnis:** [optional, z. B. „spätestens nach jeder UMSETZUNG-Phase soll mindestens ein `[VORLÄUFIG]`-Bestandteil der berührten Module auf `[BELASTBAR]` befördert sein, sonst Reflexion"]

## 7. Code-Standards und Qualitätsziele

Pflichtkategorien sind in `CLAUDE.md` Abschnitt 15 definiert. Hier wird pro im Projekt verwendeter Sprache die konkrete Toolwahl festgelegt. Nicht anwendbare Kategorien sind mit Begründung zu vermerken, nicht wegzulassen.

### Tool-Festlegung pro Sprache

#### [Sprache, z. B. Python]

- **Linter:** [z. B. `ruff` mit Konfiguration `pyproject.toml`]
- **Formatter:** [z. B. `ruff format` oder `black`, Zeilenlänge: 100]
- **Type-Checker:** [z. B. `mypy --strict`]
- **Security-Scanner:** [z. B. `bandit`]
- **Dependency-Audit:** [z. B. `pip-audit`, `safety`]
- **Test-Runner:** [z. B. `pytest` mit `pytest-cov`]
- **Naming-Konvention:** [z. B. PEP 8, snake_case für Funktionen/Variablen, PascalCase für Klassen]

#### [Sprache, z. B. TypeScript]

- **Linter:** [z. B. `eslint` mit `@typescript-eslint`]
- **Formatter:** [z. B. `prettier`]
- **Type-Checker:** [z. B. `tsc --strict --noUncheckedIndexedAccess`]
- **Security-Scanner:** [z. B. `eslint-plugin-security`]
- **Dependency-Audit:** [z. B. `npm audit` oder `pnpm audit` mit Schwellenwert `high`]
- **Test-Runner:** [z. B. `vitest` mit `--coverage`]
- **Naming-Konvention:** [z. B. camelCase für Variablen/Funktionen, PascalCase für Typen/Klassen]

[Weitere Sprachen analog. Sprachen ohne etabliertes Tool in einer Kategorie:
„nicht anwendbar, Begründung: …"]

### Durchsetzungsmechanismen

Zwei Schichten, die identische Checks ausführen: lokale Pre-Commit-Hooks als erste Verteidigung, GitHub Actions als unabhängige Diagnoseschicht auf Push/PR. Beide Schichten sind Pflicht – die CI ersetzt die Hooks nicht und umgekehrt. Skelette für beide Schichten liegen unter `templates/` (siehe `templates/README.md`) und werden in Modus 2 Schritt 10 kopiert und angepasst.

- **Pre-Commit-Hook-Framework:** [z. B. `pre-commit`, `husky`, `lefthook`]
- **Konfigurationsdatei:** [z. B. `.pre-commit-config.yaml`, `.husky/`]
- **CI-Plattform:** GitHub Actions (Default; Abweichung erfordert ADR).
- **Workflow-Dateien:** Scope und Aufteilung nach Projektgrößen-Klasse (siehe `CLAUDE.md` Abschnitt 1B):
  - **Klasse K:** `.github/workflows/ci.yml` mit einem Job (Lint + Test).
  - **Klasse M/G:** `.github/workflows/ci.yml` mit allen Pflicht-Gates; bei G zusätzlich Aufteilung in `security.yml` / `release.yml`, sobald die Pipeline unübersichtlich wird.
  - **Klasse V:** je Service ein `.github/workflows/ci-<service>.yml` mit Path-Filtern, plus `integration.yml` für service-übergreifende Tests; `release.yml` und `security.yml` zentral.
- **Trigger:** mindestens `push` auf alle Branches und `pull_request` auf Hauptbranch.
- **Verpflichtende CI-Gates (Merge-Block bei Rot):**
  - Lint
  - Format-Check (kein Auto-Fix in CI)
  - Type-Check
  - Security-Scan
  - Dependency-Audit (Schwellenwert: [z. B. high oder critical])
  - Tests inklusive Coverage-Mindestwert
- **Branch-Protection auf Hauptbranch:** alle Pflicht-Gates müssen grün sein; Force-Push gesperrt; siehe Abschnitt 10.

### Coverage-Mindestwerte

- **Globaler Mindestwert:** [z. B. 80 % Lines, 70 % Branches]
- **Kritische Pfade (höhere Anforderung):** [Liste der Module/Pfade mit ihrem jeweiligen Mindestwert]
- **Ausnahmen:** [Module, für die Coverage nicht messbar ist, mit Begründung]

### Commit-Lint

- **Tool:** [z. B. `commitlint` mit Conventional-Commits-Konfiguration; falls nicht verwendet: „nicht aktiv, Begründung: …"]
- **Erlaubte Typen:** [z. B. feat, fix, refactor, docs, test, chore, perf, build, ci]

### Editor-Integration (empfohlen, nicht erzwungen)

- **EditorConfig:** `.editorconfig` im Repo-Root (Zeilenenden, Einrückung, Encoding)
- **Editor-Snippets oder Linter-Plugins:** [optional auflisten]

## 8. Betrieb und Deployment

- **Deployment-Ziel:** [z. B. „eigener VPS via Ansible", „Kubernetes via Helm"]
- **CI/CD:** GitHub Actions (Default, siehe Abschnitt 7 für Workflow-Dateien). Deployment-Workflow: [z. B. `.github/workflows/release.yml` – Trigger und Ziel beschreiben, oder „kein Deploy-Workflow, manuelles Deployment"]
- **Umgebungen:** [z. B. lokal → staging → production]
- **Monitoring:** [falls vorhanden: was wird erfasst, wo]
- **Logging-Level Default:** [z. B. `INFO` in Prod, `DEBUG` nur lokal]

## 9. Entscheidungsbefugnisse

- **Freigabe-Entscheidungen trifft:** [Name/Rolle – normalerweise der Repo-Eigentümer]
- **Kommunikationskanal für Freigaben:** [z. B. „direkt im Chat / im Pull Request / im Fahrplan als Kommentar"]
- **Reaktionszeit-Erwartung:** [z. B. „asynchron, keine harte Antwortzeit"]

## 10. Repository-Regeln

- **Hauptbranch:** [z. B. `main`]
- **Push-Regel:** [z. B. „direkter Push erlaubt", „nur über PR", „PR + grüne CI + ein Approval"]
- **Schutzregeln:** [z. B. „keine Force-Pushes auf main", „gelöschte Branches nur nach Merge"]

## 11. Offene Grundsatzfragen

[Wenn zu Projektstart Punkte noch ungeklärt sind, hier notieren.
Claude arbeitet nicht an Bereichen, die von offenen Grundsatzfragen abhängen,
ohne vorher eine Klärung anzustoßen.]

- [z. B. „Hosting-Modell (Self-Hosting vs. Managed) – offen bis Phase 2"]
- [z. B. „Auth-Provider (Keycloak vs. Better-Auth) – pending Spike"]

## 12. Glossar (projektspezifische Begriffe)

[Begriffe, die im Projekt eine definierte Bedeutung haben und sonst mehrdeutig wären.
Verhindert, dass die KI Begriffe nach allgemeiner Lesart interpretiert.]

- **[Begriff]:** [Definition im Projektkontext]

---

**Pflegehinweis:** Änderungen an Status, Stack oder Constraints sind freigabepflichtig (siehe `CLAUDE.md` Abschnitt 4) und erzeugen einen ADR-Eintrag. Statuswechsel (z. B. `alpha` → `beta`) ziehen außerdem README-Badge- und CHANGELOG-Updates nach sich.

**Initialisierungshinweis (erste Session nach Projektanlage):**
- Alle Platzhalter in eckigen Klammern durch konkrete Werte ersetzen.
- Abschnitte, die für den Projekttyp nicht relevant sind (z. B. „Performance" bei einem einmaligen Skript), entfernen statt leer zu lassen.
- Abschnitt 11 (Offene Grundsatzfragen) darf nur Punkte enthalten, die echte Blocker sind – sonst entfernen.
- **Strukturwahl** richtet sich nach der Projektgrößen-Klassifikation in `CLAUDE.md` Abschnitt 1B. Default pro Klasse:
  - **Klasse K (Klein):** Reduzierte Form – nicht relevante Abschnitte (Skalierung, Observability, Stakeholder) entfernen.
  - **Klasse M (Mittel) und G (Groß):** Ein Dokument, alle Abschnitte ausfüllen, Tiefe an Komplexität anpassen.
  - **Klasse V (Verteilt-Groß):** Ein Hauptdokument mit klar getrennten Service-Abschnitten, oder Index-Pattern mit `project-context-<service>.md` für Service-spezifische Stack-Details.
- Reaktiv-ADR-Schwellenwert in „Methodik-Schwellenwerte" klassen-abhängig setzen: K/M ≤ 30 %, G ≤ 20 %, V ≤ 15 %.
- Die Anpassung selbst als ADR-001 in `decisions.md` festhalten.
