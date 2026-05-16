# Regelwerks-Patches — konkrete Diffs für CLAUDE.md und die Pflicht-Dokument-Vorlagen

> **Begleit-Dokument zu [`issue-onboarding-luecke.md`](issue-onboarding-luecke.md).**
>
> Acht Patches, unabhängig voneinander annehmbar. Pro Patch: **Eingriffs-Stelle**, **Vorher** (Status quo), **Nachher** (Vorschlag), **Begründung** (Kurzform, Detail im Issue), **Auswirkung auf laufende Projekte**.
>
> Reihenfolge im Dokument folgt der numerischen Reihenfolge in CLAUDE.md (nicht der Wirkungs-Priorität — siehe Issue Abschnitt 7 für die).
>
> **Hinweis zur Anwendung:** Die Patches sind als formaler Vorschlag formuliert. Vor Übernahme ins separate Regelwerks-Repo sind sie gegen die dortige Vorlagen-Version zu validieren — die hier verwendete Referenz ist der CLAUDE.md-Stand am 2026-05-16 (im EB-Digital-Repo verfügbar). Abweichungen sind möglich, falls die separate Vorlage zwischenzeitlich weiterentwickelt wurde.

---

## P1 — §9 DoD: Onboarding-Pfad-Verifikation als DoD-Punkt

**Eingriffs-Stelle:** CLAUDE.md Abschnitt 9 „Definition of Done", Checkliste der DoD-Punkte.

**Vorher:**

```markdown
- [ ] Bei nutzerrelevanten Änderungen: `README.md` ist aktualisiert (siehe Abschnitt 16, Trigger 1).
- [ ] Keine offenen `TODO`-Kommentare ohne Fahrplan-Referenz.
- [ ] Keine ungebridgten Lint-/Type-Suppressions ohne Begründungs-Kommentar.
- [ ] **CI-Pipeline** läuft grün – Lint, Format-Check, Type-Check, Security-Scan, Tests sind Pflicht-Gates.
- [ ] Commit ist erstellt (Konvention Abschnitt 11).
```

**Nachher:**

```markdown
- [ ] Bei nutzerrelevanten Änderungen: `README.md` ist aktualisiert (siehe Abschnitt 16, Trigger 1).
- [ ] **Bei Quick-Start-relevanten Änderungen (siehe Abschnitt 17): Onboarding-Pfad wurde gegen frischen Klon/Worktree validiert** oder explizit als nicht-validierungsrelevant markiert mit Begründung im Schritt-Logbuch.
- [ ] Keine offenen `TODO`-Kommentare ohne Fahrplan-Referenz.
- [ ] Keine ungebridgten Lint-/Type-Suppressions ohne Begründungs-Kommentar.
- [ ] **CI-Pipeline** läuft grün – Lint, Format-Check, Type-Check, Security-Scan, Tests sind Pflicht-Gates.
- [ ] Commit ist erstellt (Konvention Abschnitt 11).
```

**Begründung:** Schließt SE-2 („Ungeprüfter Onboarding-Pfad"). Macht die Validierung zur DoD-Pflicht, ohne sie zur CI-Pflicht zu eskalieren — die Verantwortung liegt beim Schritt-Verantwortlichen. Die Formulierung „explizit als nicht-validierungsrelevant markiert" verhindert Dogmatismus bei kleinen Änderungen (z. B. ein interner Refactor in einem Modul, der keinen Quick-Start-Effekt hat). Die Definition „Quick-Start-relevant" liegt in P4 (neuer §17).

**Auswirkung auf laufende Projekte:** Pro Schritt zusätzliche 5–15 Minuten Validierungs-Aufwand bei tatsächlich relevanten Schritten (etwa 10–20 % aller Schritte). Bei nicht-relevanten Schritten: 0 Aufwand außer der expliziten Markierung im Logbuch.

---

## P2 — §15 Code-Standards: neue Pflichtkategorie „Hilfsskripts"

**Eingriffs-Stelle:** CLAUDE.md Abschnitt 15 „Code-Standards (sprachneutrale Pflichtkategorien)", nach den bestehenden sechs Pflichtkategorien.

**Vorher:**

```markdown
### Pflichtkategorien

1. **Linter** – statische Codeanalyse für Stil- und Logikfehler. Pflicht für alle Sprachen mit etablierten Lintern.
2. **Formatter** – deterministische Code-Formatierung. Pflicht, wenn ein Formatter für die Sprache existiert. Manuelle Formatierung ist verboten, sobald ein Formatter konfiguriert ist.
3. **Type-Checker** – statische Typprüfung. Pflicht für statisch oder gradual typisierte Sprachen. Strict-Modus ist Default; Abweichungen erfordern ADR.
4. **Security-Scanner** – statische Sicherheitsanalyse. Pflicht, wenn ein Standard-Tool für die Sprache existiert.
5. **Dependency-Audit** – Prüfung auf bekannte Schwachstellen in Abhängigkeiten. Pflicht für alle Sprachen mit Paketmanager.
6. **Test-Runner mit Coverage** – Coverage-Messung Pflicht. Mindestwerte werden in `project-context.md` Abschnitt 7 festgelegt.

Sprachen ohne etablierte Tools in einer Kategorie sind explizit in `project-context.md` zu vermerken („Kategorie X: nicht anwendbar für Sprache Y, Begründung: …").
```

**Nachher:** Nach Kategorie 6 wird ein neuer Sub-Abschnitt eingefügt:

```markdown
### Pflichtkategorien für Hilfsskripts (`scripts/`)

Skripts im Verzeichnis `scripts/` (oder vergleichbar projektüblich, z. B. `bin/`, `tools/`) unterliegen einer **reduzierten, aber explizit benannten** Pflicht-Liste. Sie ist nicht identisch mit den Pflichtkategorien für Sprachen oben — Skripts sind häufig kleiner, weniger formalisiert und folgen anderen Lebenszyklen als Anwendungs-Code. Dennoch sind sie qualitätsrelevant, weil sie das Onboarding und den Betrieb tragen.

**Pflicht für jedes Skript** (unabhängig von Größe):

A. **Header mit Zweck-Aussage in 1–3 Zeilen.**
B. **Voraussetzungs-Deklaration im Header** — alle externen CLI-Tools (z. B. `jq`, `openssl`, `docker`), alle erwarteten ENV-Variablen, alle OS-Komponenten (z. B. `mktemp`, `getopts`-Variante). Form: `# Voraussetzungen: bash 4+, jq 1.6+, curl, docker compose v5+`.
C. **Plattform-Matrix-Aussage** — explizit benannt, welche Plattformen unterstützt werden. Form: `# Plattformen: Linux, macOS, Windows (Git Bash oder WSL2)`. Wenn eine Plattform nicht unterstützt wird: explizit benannt mit Begründung.
D. **Exit-Code-Disziplin** — Skript signalisiert Erfolg/Fehler über Exit-Code (Bash: `set -euo pipefail` als Default, oder begründete Abweichung).

**Pflicht zusätzlich für Skripts ab Komplexitäts-Schwelle** (Richtwert: >100 Zeilen, >1 Subkommando, >3 externe Tool-Voraussetzungen, oder Cleanup-/Trap-Logik):

E. **Idempotenz-Aussage** im Header — beschreibt, ob das Skript bei wiederholtem Aufruf denselben Effekt erzielt, oder welche Vor-/Nachbedingungen für Re-Run gelten.
F. **Reproduzierbarkeits-Aussage** im Header — beschreibt, ob aufeinanderfolgende Aufrufe (z. B. innerhalb 15 Minuten) zuverlässig dasselbe Ergebnis liefern, oder welche Zustände (Volumes, Caches, Counter) sich auswirken können.
G. **Shell-Linter im Pre-Commit** — für Bash-Skripts: `shellcheck` Pflicht. Für Python-Skripts: bestehende `ruff`-Konfiguration gilt (kein zusätzlicher Linter nötig).
H. **Architektur-Eintrag** — siehe Patch P6: Skripts ab dieser Schwelle sind in `architecture.md` mit Reifegrad-Marker zu führen.

**Nicht-anwendbar-Kennzeichnung:** Wenn eine der obigen Pflichten in einem konkreten Skript nicht sinnvoll ist (z. B. ein Trivial-Wrapper hat keine sinnvolle Idempotenz-Aussage), wird das im Header explizit vermerkt mit kurzer Begründung — analog zur Sprachen-Regel oben.
```

**Begründung:** Schließt SE-4 („Hilfsskripts ohne Reifegrad") strukturell. Die Pflichten A–D sind sehr leicht (10 Zeilen Header-Boilerplate), die Pflichten E–H greifen nur für die wenigen wirklich komplexen Skripts. Genau diese komplexen Skripts sind aber die, in denen Bugs wie der EB-Digital-`dev-smoke.sh`-Trap-Override entstehen.

**Auswirkung auf laufende Projekte:** Einmaliger Aufwand pro existierendem Skript (Header-Ergänzung) — in EB-Digital wären das 2 Skripts (`dev-smoke.sh`, `fix-venv-flags.sh`), Aufwand ca. 15 Minuten. Danach 0 zusätzlicher Aufwand pro neuem Skript, weil die Pflichten bekannt sind.

---

## P3 — §16 README-Pflege: zwei neue Trigger

**Eingriffs-Stelle:** CLAUDE.md Abschnitt 16 „README-Pflege", Trigger-Abschnitte.

**Vorher** (Strukturen-Auszug, Detail-Text gekürzt):

```markdown
### Trigger 1: Pro nutzerrelevantem Schritt

Während der Bearbeitung eines Fahrplan-Schritts mit nutzersichtbarer Wirkung wird die README aktualisiert. ...

Konkrete Aktualisierungen pro Schritt:

- **Quick Start ändert sich:** Setup-, Installations- oder Erstausführungs-Befehle ergänzen oder anpassen.
- **Verwendung ändert sich:** Beispiele aktualisieren, neue Anwendungsfälle ergänzen.
- **Architektur ändert sich:** Architektur-Skizze und Modul-Liste anpassen, Verweise auf `architecture.md` prüfen.
- **Phase abgeschlossen:** „Nächste Schritte" auf die folgende Phase umstellen.

### Trigger 2: Sessionende-Synchronisation

...
```

**Nachher:** Trigger 1 wird um eine ausdrückliche Klausel ergänzt; nach Trigger 2 wird ein neuer **Trigger 3** eingefügt:

```markdown
### Trigger 1: Pro nutzerrelevantem Schritt

... (unverändert) ...

Konkrete Aktualisierungen pro Schritt:

- **Quick Start ändert sich:** Setup-, Installations- oder Erstausführungs-Befehle ergänzen oder anpassen.
- **Verwendung ändert sich:** Beispiele aktualisieren, neue Anwendungsfälle ergänzen.
- **Architektur ändert sich:** Architektur-Skizze und Modul-Liste anpassen, Verweise auf `architecture.md` prüfen.
- **Phase abgeschlossen:** „Nächste Schritte" auf die folgende Phase umstellen.
- **Neue oder geänderte Voraussetzung / ENV-Variable / CLI-Tool / OS-Komponente:** Voraussetzungen-Block der README und `.env.example`-Kommentare im **selben Commit** aktualisieren. Gilt insbesondere bei jeder Erweiterung von Skripts in `scripts/`, die ein neues externes Tool oder eine neue ENV-Variable einführt — auch wenn die Skript-Änderung selbst klein erscheint.

### Trigger 2: Sessionende-Synchronisation

... (unverändert) ...

### Trigger 3: Phasen-Abschluss-Re-Validation

Bei jedem Schritt, der einen Phasen-Abschluss markiert (Phasen-Bilanz, Reifegrad-Beförderung mehrerer Bestandteile, oder explizit als „Phase-X-Abschluss" geführt), wird der vollständige Onboarding-Pfad gegen einen frischen Klon oder Worktree validiert.

Konkrete Form:

- **Klasse K (Klein):** README-Quick-Start in einem temporären Verzeichnis nachvollziehen (manuell oder per Skript).
- **Klasse M (Mittel):** Wie K, plus `scripts/`-Smoke-Test (sofern vorhanden) in einem frischen Worktree.
- **Klasse G (Groß):** Wie M, plus expliziter Test einer zweiten Plattform aus der `project-context.md`-Plattform-Matrix (siehe Patch P5), wenn das Team mehrere Plattformen unterstützt.
- **Klasse V (Verteilt-Groß):** Wie G, plus expliziter Test des Multi-Service-Hochfahrens (alle Compose-Profile / Service-Mesh).

Findings werden im Logbuch dokumentiert. Falls Findings auftreten, die nicht im Rahmen des Phasen-Abschluss-Schritts gefixt werden können, wird ein eigener Stabilisierungs-Schritt angelegt (analog Hot-Stabilisierungs-Pattern, vgl. ADR-015 / Regel-018 in EB-Digital).
```

**Begründung:** Trigger 1-Ergänzung schließt SE-1 punktuell (jeder Schritt aktualisiert die Voraussetzungen synchron). Trigger 3 schließt SE-2 systemisch (am Phasen-Übergang wird der Pfad geprüft, statt erst beim ersten externen Anwender). Die Differenzierung nach Projektgrößen-Klasse vermeidet, dass kleine Projekte Overhead tragen, der für sie nicht gerechtfertigt ist.

**Auswirkung auf laufende Projekte:** Pro Phasen-Abschluss zusätzliche 15–60 Minuten Validierungs-Aufwand (je nach Klasse). Pro Schritt mit Quick-Start-relevanter Änderung zusätzliche 5–10 Minuten Doku-Synchronisation. In EB-Digital wären das bei ca. 7 Phasen ~2–5 Stunden Gesamtmehraufwand über die Projektlaufzeit — gegenüber 6–12 Stunden Refactor-Phase, die in der aktuellen Methodik anfallen würde (siehe Issue Abschnitt 8).

---

## P4 — Neuer §17 „Onboarding-Pfad-Pflege"

**Eingriffs-Stelle:** CLAUDE.md, neuer Abschnitt 17 nach dem bestehenden Abschnitt 16. Die Hinweis-Sektion am Dateiende rückt entsprechend nach hinten.

**Vorher:** Abschnitt 17 existiert nicht.

**Nachher:**

```markdown
## 17. Onboarding-Pfad-Pflege

Der **Onboarding-Pfad** ist die dokumentierte Sequenz, die ein neuer Anwender vom ersten Kontakt mit dem Repository bis zum lauffähigen System durchläuft. Er ist im Projekt definiert durch:

- den **Quick-Start-Block** der `README.md` (Voraussetzungen + Sequenz der Setup-Befehle),
- die Inhalte von `.env.example` (Konfigurations-Voraussetzungen, mit Hinweisen zur Ersetzung),
- die Inhalte von `project-context.md` Abschnitt „Setup / Lokales Hochfahren" (sofern vorhanden) und die Plattform-Matrix (Abschnitt nach P5),
- ggf. das `docs/onboarding-runbook.md` (Pflicht ab Klasse M, siehe Patch P7 / Abschnitt 3),
- die Hilfsskripts in `scripts/`, die im Pfad referenziert sind.

### Was als „Quick-Start-relevante Änderung" zählt

Eine Änderung gilt als Quick-Start-relevant — und löst die DoD-Validierung nach §9 sowie die README-Synchronisation nach §16 Trigger 1 aus — wenn sie eines der folgenden Artefakte berührt:

- `README.md` (insbesondere Voraussetzungen, Quick Start, Verwendung)
- `.env.example` oder `.env.*.example`
- `scripts/` (jede Änderung an einem Skript, das im Quick-Start oder Onboarding-Runbook referenziert ist)
- `docker-compose.yml`, `docker-compose.*.yml`, `Dockerfile*` (sofern im Quick-Start referenziert)
- `pyproject.toml`, `package.json` (Top-Level-Abhängigkeiten, die im Quick-Start „pflichtig zu installieren" sind)
- `docs/onboarding-runbook.md` (falls vorhanden)
- jede Datei, die im Quick-Start namentlich genannt ist

**Nicht Quick-Start-relevant:** rein interne Code-Änderungen (Backend-Module-Refactor, Frontend-Komponenten-Anpassung), Test-Erweiterungen ohne neue Tool-Voraussetzungen, Doku-Pflege in `docs/` ohne Quick-Start-Bezug.

### Validierungs-Form

Eine Validierung ist eine **Klon-/Worktree-frische** Durchführung der dokumentierten Setup-Sequenz, mindestens bis zum ersten erfolgreichen Funktions-Test (z. B. `/api/health` antwortet, oder Smoke-Skript läuft grün).

Mindestform (für Klasse K und Klasse M):

1. `git worktree add` in ein temporäres Verzeichnis (oder `git clone` in ein temporäres Verzeichnis).
2. Quick-Start-Sequenz exakt wie dokumentiert ausführen, ohne Abkürzungen oder Workarounds aus dem Pflege-Worktree.
3. Beim ersten Bruch: Bug im Quick-Start-Pfad, fixen.
4. Nach jedem Fix: erneut von Schritt 1 starten.

Erweiterte Form (für Klasse G und Klasse V): zusätzlich Test einer zweiten Plattform (siehe §16 Trigger 3).

### Auslöser-Trigger (zur Erinnerung, siehe auch §9 und §16)

- DoD-Pflicht bei jedem Schritt mit Quick-Start-relevanter Änderung (§9).
- Trigger 1 in §16 ergänzt um Voraussetzungen-Synchronisations-Pflicht.
- Trigger 3 in §16 macht den Onboarding-Pfad-Re-Run am Phasen-Abschluss zur Pflicht.

### Verhältnis zu README, Runbook und Logbuch

- **README** trägt den Quick-Start als **Statusbild** — was funktioniert heute, mit welchen Voraussetzungen.
- **Runbook (`docs/onboarding-runbook.md`, Pflicht ab Klasse M, siehe §3 erweitert nach Patch P7)** trägt die **vollständige, getestete End-to-End-Anleitung** mit allen Pfaden (Dev / Reviewer / Operations), mit Troubleshooting-Sektion, mit Plattform-spezifischen Hinweisen.
- **Logbuch** dokumentiert pro Phasen-Abschluss die durchgeführte Validierung mit Datum und Ergebnis (`[ONBOARDING-VALIDATION]` als neuer Eintragstyp).
```

**Begründung:** Verankert Onboarding-Pflege als eigenständige Disziplin auf demselben Niveau wie README-Pflege (§16), Code-Standards (§15) und DoD (§9). Macht die Begriffe „Quick-Start-relevant" und „Validierung" präzise verwendbar in den anderen Abschnitten. Differenziert nach Projektgrößen-Klasse, um Overhead zu vermeiden.

**Auswirkung auf laufende Projekte:** Die methodische Verankerung selbst ist kostenlos (ein Doku-Abschnitt). Die Validierungs-Pflichten kommen über §9 und §16 ins Spiel und sind dort bilanziert.

---

## P5 — `project-context.md`-Vorlage: Abschnitt „Unterstützte Entwickler-Plattformen"

**Eingriffs-Stelle:** Vorlage für `project-context.md` (im Regelwerks-Repo). Neuer Abschnitt vor oder nach dem bestehenden „Setup / Lokales Hochfahren"-Abschnitt (Abschnitt 8 in EB-Digital).

**Vorher:** Kein Plattform-Matrix-Abschnitt.

**Nachher:** Neuer Abschnitt:

```markdown
## Unterstützte Entwickler-Plattformen

Diese Tabelle ist **explizit, nicht implizit**. Jede Plattform, die nicht hier steht, ist nicht unterstützt — auch wenn sie technisch funktionieren mag. Plattformen, die mit Einschränkungen unterstützt werden, tragen den Einschränkungs-Hinweis.

| Aspekt                        | Linux (Ubuntu 22.04+ / Debian 12+ / Fedora 40+) | macOS 14+ (Apple Silicon und Intel)                                | Windows 11 mit Git Bash         | Windows 11 mit WSL2                 |
| ----------------------------- | ----------------------------------------------- | ------------------------------------------------------------------ | ------------------------------- | ----------------------------------- |
| **Backend-Entwicklung**       | ✓                                               | ✓                                                                  | ✓                               | ✓                                   |
| **Frontend-Entwicklung**      | ✓                                               | ✓                                                                  | ✓                               | ✓                                   |
| **Hilfsskripts (`scripts/`)** | ✓                                               | ✓ (siehe `fix-venv-flags.sh` für `.claude/worktrees/`-Spezialfall) | ✓ (Git Bash + `jq` installiert) | ✓                                   |
| **Docker Compose lokal**      | ✓ (Docker Engine direkt)                        | ✓ (Docker Desktop)                                                 | ✓ (Docker Desktop)              | ✓ (Docker Desktop mit WSL2-Backend) |
| **CI-Pipeline**               | ✓ (GitHub-Hosted-Runner)                        | — (kein macOS-Runner in CI)                                        | —                               | —                                   |

**Pflicht-Voraussetzungen pro Plattform:** Siehe README „Voraussetzungen"-Block. Plattform-spezifische Zusatz-Voraussetzungen sind dort namentlich vermerkt (z. B. „Windows: Git Bash oder WSL2 für `scripts/`-Hilfsskripts; `jq` separat installieren").

**Pflege-Regel:** Diese Tabelle ist bei jedem Touch an `scripts/`, `docker-compose.yml`, `pyproject.toml` (Top-Level-Dependencies) oder bei jeder neuen Plattform-spezifischen Eskalation (z. B. neuer Blocker mit Plattform-Bezug, vgl. EB-Digital Blocker #001 für macOS) zu re-validieren. Verstöße sind im selben Commit zu korrigieren.

**Nicht-Unterstützung:** Wenn eine Plattform bewusst nicht unterstützt wird (z. B. Windows ohne Git Bash und ohne WSL2), wird die Spalte trotzdem gelistet, mit einem ✗ und kurzer Begründung. Stille Nicht-Unterstützung („wir testen halt nur Linux") ist unzulässig — sie wird explizit oder die Plattform wird zur Test-Matrix hinzugefügt.
```

**Begründung:** Schließt SE-3 („Implizite Plattform-Annahmen") strukturell. Macht die Plattform-Annahmen explizit und damit prüfbar. Tabelle ist erweiterbar (neue Plattform-Spalte hinzufügen) und differenziert nach Aspekten — was z. B. Frontend-Entwicklung auf Windows-mit-Git-Bash erlaubt, auch wenn manche Skripts dort nicht laufen.

**Auswirkung auf laufende Projekte:** Einmaliger Aufwand 30–60 Minuten zur initialen Befüllung (gegen die tatsächlich genutzten Plattformen). Danach 0 zusätzlicher Aufwand bei plattform-neutralen Änderungen, ca. 10 Minuten bei plattform-betreffenden Änderungen.

---

## P6 — `architecture.md`-Vorlage: Abschnitt „Tooling-Inventar mit Reifegrad"

**Eingriffs-Stelle:** Vorlage für `architecture.md` (im Regelwerks-Repo). Neuer Abschnitt nach dem bestehenden „Module"-Abschnitt (in EB-Digital: nach Abschnitt 3 „Module (detailliert)").

**Vorher:** Kein expliziter Tooling-Abschnitt. Hilfsskripts werden nirgends als Architektur-Bestandteile geführt.

**Nachher:** Neuer Abschnitt:

```markdown
## Tooling-Inventar

Hilfsskripts (`scripts/`), Build-Skripte (`Makefile`-Targets oder Äquivalent), Diagnose-Tools und Setup-Helfer sind Architektur-Bestandteile mit eigenem Reifegrad. Sie werden hier explizit geführt, weil sie das Onboarding und den Betrieb tragen und in der Code-Review (Pflichtkategorien §15) bisher nicht systematisch erfasst sind.

### Reifegrad-Skala für Tooling

In Anlehnung an die Architektur-Reifegrade (Abschnitt 0), aber mit eigenen Beförderungs-Kriterien:

- `[ROH]` — Skript existiert, wurde getestet, aber: Voraussetzungs-Header unvollständig, Plattform-Matrix fehlt, oder Idempotenz/Reproduzierbarkeit nicht ausdrücklich. Akzeptabel für Phase-1-Skripts.
- `[GEHÄRTET]` — Skript erfüllt die vollständige §15-Tooling-Pflichtliste (P2 in den Regelwerks-Patches): Voraussetzungs-Header, Plattform-Matrix, Idempotenz-Aussage, Reproduzierbarkeits-Aussage, shellcheck-grün (bei Bash). Wird gegen frischen Worktree validiert.
- `[KRITISCH]` — Skript ist Teil eines automatisierten Pfads (CI, Deploy, Rollback), darf nicht fehlschlagen ohne klare Diagnose. Zusätzlich zu `[GEHÄRTET]`: vollständige Unit-Tests (für Python-Skripts) oder bats-Tests (für Bash-Skripts), CI-Integration als eigenständiger Job.

### Inventar

| Skript                                | Zweck                                | Reifegrad    | Plattform-Matrix (siehe `project-context.md`)                      | Voraussetzungen                            | Idempotenz                                                                          |
| ------------------------------------- | ------------------------------------ | ------------ | ------------------------------------------------------------------ | ------------------------------------------ | ----------------------------------------------------------------------------------- |
| Beispielzeile: `scripts/dev-smoke.sh` | End-to-End-Smoke gegen Compose-Stack | `[GEHÄRTET]` | Linux ✓ / macOS ✓ / Windows-Git-Bash ✓ (mit `jq`) / Windows-WSL2 ✓ | bash 4+, jq 1.6+, curl, docker compose v5+ | nicht idempotent: erfordert Volume-Reset (`docker compose down -v`) zwischen Läufen |

### Beförderungsregel `[ROH]` → `[GEHÄRTET]`

Voraussetzungen:

1. Header-Aussagen vollständig (siehe §15-Pflichten für Tooling).
2. Mindestens eine erfolgreiche Ausführung auf jeder unterstützten Plattform (oder begründete Plattform-Exklusion).
3. Bei Bash: `shellcheck` ohne Warnings (oder explizit unterdrückte Warnings mit Begründungs-Kommentar).
4. Erfolgreicher Re-Run-Test (entweder idempotent oder Re-Run-Voraussetzungen klar dokumentiert).

Beförderung erfolgt mit Datum und Hinweis im Inventar-Eintrag. Rückstufung erfordert ADR (analog Modul-Reifegrad).
```

**Begründung:** Schließt SE-4 strukturell, vervollständigt die Schließung von SE-1 und SE-3 (weil Voraussetzungs- und Plattform-Aussagen jetzt im Architektur-Dokument geführt werden, nicht nur in der README). Macht Hilfsskripts zu Architektur-Bestandteilen mit Lebenszyklus.

**Auswirkung auf laufende Projekte:** Einmaliger Aufwand 30–60 Minuten zur initialen Inventarisierung. Danach pro neuem Skript ca. 5 Minuten Eintrag, pro Beförderung ca. 10 Minuten Validierungs-Doku.

---

## P7 — §3 Dokumenten-Index: optionales `docs/onboarding-runbook.md`

**Eingriffs-Stelle:** CLAUDE.md Abschnitt 3 „Dokumenten-Index", Tabelle.

**Vorher:**

```markdown
| Datei            | Zweck                                               | Aktualisierungstrigger                            |
| ---------------- | --------------------------------------------------- | ------------------------------------------------- |
| `docs/vision.md` | Eingangs-Idee, Ziel, Erfolgskriterien, Abgrenzungen | Einmalig zu Projektstart (siehe Abschnitt 1A) ... |
| ...              | ...                                                 | ...                                               |
| `CHANGELOG.md`   | Nutzerrelevante Änderungen, SemVer-Einträge         | Bei jedem Release, bei Breaking Changes           |
```

**Nachher:** Zusätzliche Tabellenzeile **vor** `CHANGELOG.md`:

```markdown
| `docs/onboarding-runbook.md` (**Pflicht ab Klasse M**, optional Klasse K, in Klasse G/V aufteilbar nach Rolle) | Vollständige, getestete End-to-End-Anleitung für den Anwender vom Repo-Klon bis zum lauffähigen System. Ergänzt die README: README ist Statusbild, Runbook ist Bedienungs-Anleitung. Enthält Plattform-spezifische Hinweise, Troubleshooting-Sektion, ggf. Rollen-Aufteilung (Dev-Runbook / Reviewer-Runbook / Operations-Runbook). | Bei jedem Phasen-Abschluss-Schritt mit Quick-Start-relevanter Änderung; bei jeder Änderung der `project-context.md`-Plattform-Matrix; bei jedem neuen Skript in `scripts/`, das im Onboarding-Pfad referenziert wird. |
```

**Begründung:** Die README hat per §16 die Rolle eines „Statusbilds" — kompakt, kein Roadmap-Vollersatz, keine vollständige Bedienungsanleitung. Für Projekte ab Klasse M reicht das nicht, weil die Setup-Sequenz zu komplex wird (zwei Sprachen, mehrere Services, Plattform-Spezifika). Das Runbook trägt die ausführliche Form. In Klasse G/V kann es nach Rolle aufgeteilt werden — Dev-Runbook (Setup für Entwickler), Reviewer-Runbook (Setup für Code-/Security-Reviewer), Operations-Runbook (Setup für Produktiv-Betrieb).

**Auswirkung auf laufende Projekte:** Einmaliger Aufwand 1–3 Stunden zur initialen Befüllung. Danach pro Phasen-Abschluss 15–30 Minuten Re-Validation und Anpassung.

**Implementierungs-Hinweis:** Die Runbook-Erstellung ist nicht Teil dieser Patch-Sequenz — sie wird in jedem konkreten Projekt als separater Schritt geführt (Empfehlung: erster Schritt einer STABILISIERUNG-Phase, sobald die Setup-Komplexität die Schwelle überschreitet).

---

## P8 — §5 Autonomiebereich: Skript-Erweiterungen mit neuen Voraussetzungen

**Eingriffs-Stelle:** CLAUDE.md Abschnitt 5 „Autonomiebereich (freigabefrei)".

**Vorher:**

```markdown
Innerhalb der folgenden Grenzen arbeitet Claude eigenständig, ohne Freigabe einzuholen:

- Implementierung von Fahrplan-Schritten, die klar spezifiziert sind (Eingabe, Ausgabe, Akzeptanzkriterien vorhanden).
- Bugfixes, die keine der Kategorien in Abschnitt 4 berühren.
- Test-Erstellung und Testwartung.
- Dokumentationspflege in `docs/`.
- Refactorings **innerhalb eines Moduls**, solange öffentliche Schnittstellen unverändert bleiben.
- Commits mit sprechender Message (Konvention siehe Abschnitt 11).
- Branch-Anlage und lokales Mergen nach erfolgreichen Tests.
- Formatierung, Linting, kleinere Performance-Optimierungen ohne Architekturwirkung.

Grenzfälle werden **wie Freigaben behandelt**: im Zweifel stoppen und fragen.
```

**Nachher:** Erweiterung der Auflistung um einen Grenzfall-Punkt:

```markdown
Innerhalb der folgenden Grenzen arbeitet Claude eigenständig, ohne Freigabe einzuholen:

- ... (unverändert) ...
- Formatierung, Linting, kleinere Performance-Optimierungen ohne Architekturwirkung.

**Nicht im Autonomiebereich, auch wenn der eigentliche Eingriff klein ist:**

- **Skript-Erweiterungen, die neue externe Voraussetzungen einführen** (ein neues CLI-Tool, eine neue ENV-Variable, eine neue OS-Komponente, eine neue Sprach-Version) — auch wenn die Skript-Änderung selbst nur wenige Zeilen umfasst. Solche Erweiterungen brauchen zwingend die Synchronisation mit `README.md` (Voraussetzungen), `.env.example` (für ENV-Variablen) und ggf. der `project-context.md`-Plattform-Matrix im **selben Commit**. Wird die Synchronisation in einem späteren Commit nachgeholt, ist das eine `[PROBLEM-OFFEN]`-Lücke und in `blockers.md` zu vermerken.
- **Skript-Erweiterungen, die das Re-Run-Verhalten oder die Idempotenz-Eigenschaften des Skripts ändern** — z. B. neue persistente Volumes, neue Rate-Limit-relevante Aufrufe, neue Counter-Mutationen — brauchen Aktualisierung der Idempotenz-/Reproduzierbarkeits-Aussage im Skript-Header (siehe §15 Tooling-Pflichten, Patch P2).

Grenzfälle werden **wie Freigaben behandelt**: im Zweifel stoppen und fragen.
```

**Begründung:** Schließt SE-1 an der Wurzel. Die ursprüngliche Formulierung „Test-Erstellung und Testwartung" deckt Skript-Erweiterungen implizit ab — das ist genau, wie der `jq`-Drift in EB-Digital entstanden ist (`dev-smoke.sh`-Erweiterungen in 1.8/2.2/2.3/2.4/2.5b/2.6 wurden alle als Test-Wartung autonom durchgeführt, ohne Voraussetzungs-Synchronisation). Die Präzisierung benennt den Grenzfall explizit.

**Auswirkung auf laufende Projekte:** Pro Skript-Erweiterung, die eine neue Voraussetzung einführt, zusätzliche 5–10 Minuten Synchronisations-Aufwand im selben Commit. Bei Skript-Erweiterungen ohne neue Voraussetzungen: 0 zusätzlicher Aufwand.

---

## Übersicht der Patches mit Wirkungs-Zuordnung

| Patch | Schließt Symptom-Klassen  | Eingriffs-Stelle                      | Aufwand pro Projekt (geschätzt)                                                 |
| ----- | ------------------------- | ------------------------------------- | ------------------------------------------------------------------------------- |
| P1    | SE-2                      | CLAUDE.md §9                          | 5–15 min pro Schritt × geschätzt 10–20 % aller Schritte                         |
| P2    | SE-4                      | CLAUDE.md §15                         | einmalig 15 min pro existierendem Skript, danach 0 zusätzlich                   |
| P3    | SE-1 + SE-2               | CLAUDE.md §16                         | 5–10 min pro Quick-Start-relevantem Schritt + 15–60 min pro Phasen-Abschluss    |
| P4    | alle vier                 | CLAUDE.md §17 (neu)                   | 0 zusätzlich (verankert Begriffe)                                               |
| P5    | SE-3                      | `project-context.md`-Vorlage          | einmalig 30–60 min Befüllung, danach 10 min pro plattform-betreffender Änderung |
| P6    | SE-4 (vertieft SE-1+SE-3) | `architecture.md`-Vorlage             | einmalig 30–60 min Inventarisierung, danach 5–10 min pro neuem Skript           |
| P7    | SE-2 (vertieft)           | CLAUDE.md §3 + neues Pflicht-Dokument | einmalig 1–3 h Initial-Befüllung, danach 15–30 min pro Phasen-Abschluss         |
| P8    | SE-1 (strukturell)        | CLAUDE.md §5                          | 5–10 min pro Skript-Erweiterung mit neuer Voraussetzung                         |

**Geschätzter Gesamtaufwand pro Projekt über die Laufzeit:**

- Ohne Patches: 6–12 h Refactor-Phase zum Roll-out-Zeitpunkt, plus ~4 h pro neuem externen Anwender Onboarding-Unterstützung
- Mit Patches: 3–6 h kontinuierlicher Pflege-Aufwand über alle Phasen, kein Refactor, ~0,5 h pro neuem externen Anwender

**Geschätzter Gesamtaufwand für die Übernahme aller acht Patches ins Regelwerks-Repo:**

- Patch-Text in CLAUDE.md übernehmen: 1–2 h (acht Eingriffe, davon vier kleine und vier mittlere)
- `project-context.md`- und `architecture.md`-Vorlagen erweitern: 1 h
- Migration der laufenden Projekte (z. B. EB-Digital): 2–4 h pro Projekt für initiale Aufholung (Skript-Header, Plattform-Matrix, Tooling-Inventar)
- **Gesamt für Regelwerks-Repo: ca. 4–7 h.** Amortisation: bei zwei laufenden Projekten der Klasse G nach ca. 1–2 Monaten.

---

## Reihenfolge der Übernahme — Empfehlung

Wenn nicht alle acht Patches gleichzeitig übernommen werden sollen, empfohlene Reihenfolge nach Wirkungs-Verhältnis:

1. **P1 + P3** (zusammen) — größter Sofort-Effekt, klärt DoD und README-Pflege synchron.
2. **P5** (alleine) — explizite Plattform-Matrix, niedriger Aufwand, hohe Wirkung gegen SE-3.
3. **P8** (alleine) — schließt die Autonomiebereich-Lücke, präventiv für künftige Skript-Erweiterungen.
4. **P2 + P6** (zusammen) — Tooling-Disziplin als Paket, weil §15-Erweiterung und Inventar-Abschnitt sich gegenseitig referenzieren.
5. **P4** (alleine) — methodische Verankerung als eigene Disziplin (kann nach 1–3 nachgezogen werden, ohne dass die anderen Patches deshalb scheitern).
6. **P7** (zuletzt) — Onboarding-Runbook als Pflicht-Dokument, höchster Initial-Aufwand, kann pro Projekt zeitversetzt eingeführt werden.

Diese Reihenfolge minimiert das Risiko, dass eine Teil-Annahme der Patches Lücken hinterlässt.
