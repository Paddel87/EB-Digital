# [Projektname]

<!-- Diese README spiegelt den aktuellen Umsetzungsstand des Projekts wider.
     Sie ist KEIN sporadisch gepflegtes Marketing-Dokument, sondern ein lebendes Statusbild.
     Aktualisierungs-Pflicht (CLAUDE.md Abschnitt 16):
       - bei jedem nutzerrelevanten Fahrplan-Schritt während der Bearbeitung
       - vor jedem Sessionende mit Synchronisations-Prüfung gegen Pflicht-Dokumente
     Inhalte stammen aus den Pflicht-Dokumenten und müssen mit ihnen konsistent sein.
     Drift zwischen README und Pflicht-Dokumenten ist ein Bug. -->

[Badge-Zeile – siehe Abschnitt „Badge-Auswahl pro Klasse" am Ende dieser Vorlage]

[Optional: zweite Badge-Zeile, falls thematisch sinnvoll gruppiert]

> [Einzeiler: was das Projekt ist und für wen, in einem Satz.
> Soll auch im sozialen Vorschau-Snippet (Open Graph) funktionieren.]

## Über das Projekt

[2–4 Absätze. Quelle: `vision.md` Abschnitte 1–3 (Kernidee, Problem, Zielbild),
in für Außenstehende verständliche Sprache übersetzt.]

**Was es löst:** [aus `vision.md` Abschnitt 2]

**Für wen:** [aus `vision.md` Abschnitt 2 und `project-context.md` Abschnitt 2]

**Was es bewusst nicht ist:** [aus `vision.md` Abschnitt 5 – die wichtigsten Abgrenzungen]

## Aktueller Status

<!-- Dieser Block wird vor jedem Sessionende synchronisiert mit:
     - project-context.md Abschnitt 1 (Status, Version)
     - fahrplan.md Abschnitt „Aktueller Stand"
     - architecture.md Abschnitt 9 (Reifegrad-Übersicht)
     - decisions.md Teil B (ADR-Übersicht, Reaktiv-Quote)
     Inkonsistenzen sind Bugs und werden vor Sessionende behoben. -->

- **Projektphase:** [aus `fahrplan.md` – z. B. „Phase 2: Auth-System (UMSETZUNG)"]
- **Version:** [aus `project-context.md` Abschnitt 1]
- **Status:** [aus `project-context.md` Abschnitt 1 – Konzeption / Aufbau / aktive Entwicklung / Wartung / deprecated]
- **Letzte Änderung:** [Datum des letzten Sessionende, automatisch aus Commit-Datum]
- **Architektur-Reife:** [Kurzfassung aus `architecture.md` Abschnitt 9 – z. B. „Module A, B BELASTBAR; Modul C VORLÄUFIG; Modul D OFFEN, wartet auf Spike S-3"]
- **Aktive Blocker:** [Anzahl aus `blockers.md`; bei >0 Verweis auf die Datei]

## Quick Start

[Schritte für jemanden, der das Projekt nach dem Klonen startet.
Konkret und kopierbar, keine Abstraktionen.
Quelle: `project-context.md` Abschnitt 8 (Betrieb und Deployment) plus eigenes Hands-on.]

### Voraussetzungen

- [Sprache und Mindestversion, z. B. Python 3.12+]
- [Werkzeuge, z. B. Docker, Make]
- [Optional: Hardware, z. B. GPU für ML-Workloads]

### Installation

```bash
# Repo klonen
git clone [URL]
cd [projektname]

# Abhängigkeiten installieren
[konkreter Befehl]

# Erstkonfiguration
[konkreter Befehl, z. B. `cp .env.example .env`]
```

### Erste Ausführung

```bash
[konkreter Befehl]
```

Erwartete Ausgabe: [...]

## Architektur (Überblick)

[Eine Skizze in 5–10 Zeilen, NICHT die volle Architektur. Quelle: `architecture.md` Abschnitt 1 + Modul-Karte in vereinfachter Form.
Verweis auf `architecture.md` für Details.]

```
[ASCII-Skizze oder Mermaid-Block, max. 10 Zeilen]
```

**Module:**

- **[Modul A]:** [1 Satz Verantwortung]
- **[Modul B]:** [1 Satz Verantwortung]

→ Vollständige Architektur: [`docs/architecture.md`](docs/architecture.md)

## Verwendung

[Häufigste Anwendungsfälle als kurze Beispiele.
Bei UI-basierten Systemen: Screenshots oder Beschreibung der Hauptansichten.
Bei CLI-Tools: typische Befehle.
Bei APIs: typische Requests.]

### Beispiel: [Anwendungsfall]

```
[konkretes Beispiel]
```

## Nächste Schritte

[Aus `fahrplan.md` – die nächsten 1–3 geplanten Schritte oder Phasen, in nutzerorientierter Sprache.
Nicht die vollständige Roadmap, nur was als nächstes in der Umsetzung kommt.]

- [Schritt 1, kurz]
- [Schritt 2, kurz]

→ Vollständiger Fahrplan: [`docs/fahrplan.md`](docs/fahrplan.md)

## Mitwirken

[Falls Open Source: Verweis auf CONTRIBUTING.md falls vorhanden, Issue-Tracker, Branch-Konventionen.
Bei privaten Projekten: kurzer Hinweis auf den Workflow.]

- **Branch-Konvention:** [aus `CLAUDE.md` Abschnitt 11]
- **Commit-Format:** [aus `CLAUDE.md` Abschnitt 11]
- **Code-Standards:** [aus `project-context.md` Abschnitt 7]

## Dokumentation

| Dokument | Inhalt |
|---|---|
| [`docs/vision.md`](docs/vision.md) | Ursprüngliche Projektvision (eingefroren) |
| [`docs/project-context.md`](docs/project-context.md) | Aktueller Stack, Constraints, Qualitätsziele |
| [`docs/architecture.md`](docs/architecture.md) | Systemarchitektur, Module, Schnittstellen |
| [`docs/fahrplan.md`](docs/fahrplan.md) | Entwicklungsplan und Fortschritt |
| [`docs/decisions.md`](docs/decisions.md) | Architekturentscheidungen (ADRs) |
| [`docs/blockers.md`](docs/blockers.md) | Aktive Blocker und gelöste Probleme |
| [`CHANGELOG.md`](CHANGELOG.md) | Versionshistorie |

## Lizenz

[aus `project-context.md` Abschnitt 6 – Compliance und Lizenz]

---

## Badge-Auswahl pro Klasse (Initialisierungshinweis)

<!-- Dieser Abschnitt wird beim Initialisieren entfernt.
     Er dokumentiert nur, welche Badges in welcher Klasse als Default gelten. -->

**Maximalwerte (CLAUDE.md Abschnitt 1B):**

- **Klasse K (Klein):** maximal **5** Badges
- **Klasse M (Mittel):** maximal **8** Badges
- **Klasse G (Groß):** maximal **10** Badges
- **Klasse V (Verteilt-Groß):** maximal **12** Badges

**Pflicht-Badges (alle Klassen):**

- **Status** – aus `project-context.md` Abschnitt 1: alpha / beta / stable / maintenance / deprecated
- **Version** – SemVer-Wert aus `project-context.md` Abschnitt 1
- **License** – aus `project-context.md` Abschnitt 6
- **Build** – CI-Status des Hauptbranches

**Empfohlene Zusatz-Badges nach Klasse:**

- **Klasse K (1 Slot):** Sprach-/Laufzeit-Mindestversion ODER Last Commit
- **Klasse M (4 Slots):** Sprach-/Laufzeit-Version, Coverage, Last Commit, Open Issues
- **Klasse G (6 Slots):** zusätzlich Type-Check-Status, Security-Scan-Status, Lint-Status, Lines-of-Code, Stack-Hauptkomponente, Aktivitätsindikator
- **Klasse V (8 Slots):** zusätzlich pro Service ein Build-/Status-Badge ODER Compliance-Badge (DSGVO, etc.) ODER Container-Image-Status

**Reihenfolge in der Badge-Zeile (verbindlich):**

1. Status (immer ganz links – wichtigste Information)
2. Version
3. Build
4. Coverage (falls vorhanden)
5. Type-Check / Lint / Security (technische Qualitätsbadges)
6. License
7. Sprach-/Laufzeit-Version
8. Aktivitätsindikatoren (Last Commit, Open Issues)

**Bei Klasse G und V mit zwei Zeilen:** Zeile 1 = Status- und Qualitätsbadges, Zeile 2 = technische und Aktivitäts-Badges.

**Regeln:**

- Badges spiegeln **reale** Zustände – kein „coming soon"-Coverage-Badge.
- Bei Statuswechsel oder Versionserhöhung: Badge-Update Pflicht im selben Commit.
- Maximalwerte sind Obergrenze, nicht Zielwert. Wenn ein Projekt mit weniger auskommt: weniger ist besser.
- Badge-Quellen bevorzugt: shields.io für statische und einfach abgeleitete Badges; offizielle Service-Badges (codecov, github actions) für dynamische.

**Beispielzeile (Klasse M, 6 Badges):**

```markdown
![Status](https://img.shields.io/badge/status-beta-yellow)
![Version](https://img.shields.io/badge/version-v0.4.1-blue)
![Build](https://img.shields.io/github/actions/workflow/status/USER/REPO/ci.yml)
![Coverage](https://img.shields.io/badge/coverage-82%25-green)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.12+-blue)
```

---

**Initialisierungshinweis (erste Session nach Projektanlage):**

- Dieser ganze Abschnitt „Badge-Auswahl pro Klasse" und der Initialisierungshinweis selbst werden nach der Initialisierung **entfernt**.
- Inhaltliche Befüllung der README erfolgt aus den anderen Pflicht-Dokumenten – siehe Quellenangaben in den HTML-Kommentaren oben.
- **Strukturwahl** richtet sich nach Klasse:
  - **Klasse K (Klein):** Abschnitte „Architektur (Überblick)", „Mitwirken", „Dokumentation"-Tabelle können entfallen oder verkürzt werden. „Über das Projekt" auf 1 Absatz reduzieren.
  - **Klasse M (Mittel):** Volle Form wie oben.
  - **Klasse G (Groß):** Volle Form, „Architektur (Überblick)" mit Mermaid-Diagramm und Verweisen auf Modul-spezifische Architektur-Dokumente.
  - **Klasse V (Verteilt-Groß):** Volle Form, zusätzlich Service-Übersicht in „Architektur (Überblick)" mit Verweisen auf `architecture-<service>.md` und `architecture-integration.md`. „Quick Start" ggf. um Multi-Service-Setup erweitern.
- README-Initialisierung ist Teil der Modus-2-Befüllungsreihenfolge (CLAUDE.md Abschnitt 1A, Schritt 8 nachgelagert) – sie wird nach allen anderen Dokumenten erstellt, weil sie aus diesen abgeleitet wird.
