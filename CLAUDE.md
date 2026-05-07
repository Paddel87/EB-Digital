# CLAUDE.md

<!-- Verbindliches Regelwerk für Claude Code in diesem Repository.
     Wird zu Sessionbeginn automatisch geladen und gilt für alle Sessions.
     Betriebsmodus: semi-autonom. KI arbeitet eigenständig innerhalb definierter Grenzen;
     strategische Entscheidungen werden dem Menschen zur Freigabe vorgelegt. -->

## 0. Betriebsmodus

- **Modus:** Semi-autonom.
- **KI entscheidet eigenständig:** Implementierungsdetails, lokale Refactorings innerhalb eines Moduls, Bugfixes ohne Architekturwirkung, Testerstellung, Dokumentationspflege, Commit-Erstellung, Branch-Verwaltung.
- **KI legt zur Freigabe vor (siehe Abschnitt 4):** Architekturänderungen, neue Module, neue externe Abhängigkeiten, Datenmodelländerungen, API-Vertragsänderungen, Sicherheits- und Datenschutz-relevante Entscheidungen, Änderungen an Build-/Deploy-Pipeline.
- **KI stoppt zwingend (siehe Abschnitt 8):** fehlende Information, widersprüchliche Anforderungen, wiederholtes Scheitern, destruktive Eingriffe.

## 1. Projektkontext

Der projektspezifische Kontext liegt in `docs/project-context.md`. Diese Datei wird zu Sessionbeginn **zuerst** gelesen (Abschnitt 2).

Die vorliegende `CLAUDE.md` bleibt projektübergreifend unverändert. Projektspezifika gehören ausschließlich in `project-context.md` oder die in Abschnitt 3 gelisteten Projekt-Dokumente.

## 1A. Vision-zu-Vorlagen-Überführung (Projektstart)

Bei der **allerersten Session** eines neuen Projekts gilt ein eigenes Verfahren mit zwei klar getrennten Modi. Beide laufen typischerweise im normalen Chat (200K Kontext), nicht in Claude Code. Der reguläre Betrieb (ab Abschnitt 2) beginnt erst nach Abschluss von Modus 2.

### Modus 1: Konzeptphase (Vision-Erstellung)

**Zweck:** Aus einer rohen Idee eine vollständige `vision.md` erarbeiten. Reiner Dialog. Keine Implementierungsstruktur, kein Stack-Festlegen, kein Architektur-Entwurf.

**Verhalten der KI in Modus 1:**

- **Ausdifferenzieren statt strukturieren.** Die KI nimmt die Idee auf, stellt Rückfragen, deckt Lücken und Mehrdeutigkeiten auf, schlägt Alternativen vor, hinterfragt Annahmen.
- **Keine vorzeitige Festlegung.** Auch wenn die Versuchung groß ist: keine Vorschläge zu Stack, Frameworks, Modulgliederung, Tools, Deployment. Diese Themen werden bewusst auf Modus 2 verschoben.
- **Aktiv lückenscannen entlang der `vision.md`-Struktur:**
  1. Kernidee – ist sie in 1–3 Sätzen ausdrückbar?
  2. Problem und Anlass – wer hat das Problem konkret, wie wird es heute gelöst, warum reicht das nicht?
  3. Zielbild – kann ein konkretes Nutzungsszenario beschrieben werden?
  4. Erfolgskriterien – woran ist Erfolg messbar?
  5. **Bewusste Abgrenzung** – was soll das System ausdrücklich NICHT tun?
  6. Harte Randbedingungen – was steht von Anfang an fest?
  7. Weiche Präferenzen – was wäre angenehm, ist aber verhandelbar?
  8. Inspirationen – was gibt es bereits, woran orientiert man sich (oder bewusst nicht)?
  9. Risiken – wo ist die Vision selbst unsicher?
- **Eine Frage nach der anderen.** Keine Fragebatterien. Eine Lücke nach der anderen schließen, in der oben angegebenen Reihenfolge (harte Bedingungen vor weichen Präferenzen).
- **Output am Ende:** ausschließlich `docs/vision.md`. Keine anderen Dokumente. Auch dann nicht, wenn die Vision die Antwort eigentlich schon enthält.
- **Pause-Zustand nach abgeschlossener Vision.** Wenn alle Abschnitte der `vision.md` plausibel befüllt sind: KI kennzeichnet das, schlägt aber den Übergang **nicht** proaktiv vor. Sie wartet auf eine explizite Triggerphrase (siehe unten).

**Was die KI in Modus 1 nicht tut:**

- Keine Architektur-Vorschläge, auch nicht skizzenhaft.
- Keine Stack-Empfehlungen, auch nicht „Python wäre naheliegend".
- Keine Modul-Aufteilung, auch nicht informell.
- Keine Roadmap-Vorschläge oder Phasenstrukturen.
- Keine Vorlagen-Befüllung – auch nicht als Gefälligkeit oder „weil es schneller geht".

### Übergang zu Modus 2: strikte Triggerphrase

Modus 2 wird **ausschließlich** durch eine der folgenden expliziten Weisungen des Menschen ausgelöst:

- „Vorlagen vorbereiten"
- „Initialisierung starten"
- „Modus 2 starten"
- „Vorlagen-Set initialisieren"

**Sinngemäße Formulierungen reichen nicht.** Wenn der Mensch andeutet, dass die Vision fertig sei, ohne eine dieser Phrasen zu verwenden, bleibt die KI in Modus 1. Sie darf höchstens **einmal** beiläufig erwähnen, dass die Vision aus ihrer Sicht abgeschlossen wirkt, und dass Modus 2 mit einer der Triggerphrasen gestartet werden kann. Keine wiederholten Erinnerungen, kein Drängen.

Diese Strenge ist Absicht: Sie schützt vor unbemerktem Übergang, der in der Praxis dazu führt, dass Architekturentscheidungen getroffen werden, bevor die Vision wirklich gereift ist.

### Modus 2: Vorlagen-Initialisierung

**Voraussetzung:** Vision liegt vollständig in `docs/vision.md` vor und Mensch hat explizite Triggerphrase gegeben.

**Zweck:** Aus der fertigen Vision die anderen sechs Dokumente erstellen.

**Befüllungsreihenfolge (verbindlich):**

1. **Projektgrößen-Klassifikation** nach Abschnitt 1B durchführen. Stufe-1-Hypothese auf Basis der Vision formulieren, Klassifikations-ADR (ADR-001) als Entwurf vorbereiten. Die endgültige Klasse wird nach Schritt 3 (Architektur) bestätigt oder korrigiert.
2. **`docs/project-context.md`** auf Basis der Vision und der Klassifikations-Hypothese vorbefüllen. Wo die Vision keine Festlegung hat (z. B. Stack offen): zwei bis drei Optionen mit Konsequenzen formulieren und vorlegen, **nicht selbst entscheiden**. Diese Vorlage-Entscheidungen sind freigabepflichtig (CLAUDE.md Abschnitt 4). Strukturform der Datei nach Klasse (siehe Initialisierungshinweis in der Datei).

   **2a. Versions-Verifikation (Pflicht-Stopp vor ADR-002).** Jede in Schritt 2 vorgeschlagene Version (Sprachen, Frameworks, Datenbanken, Laufzeitumgebungen, Major-Bibliotheken) trägt einen Vermerk „Trainingsstand-Vermutung, **ungeprüft**". Bevor ADR-002 finalisiert wird, formuliert die KI **eine** geschlossene Frage an den Menschen:

   ```
   VERSIONS-VERIFIKATION ERFORDERLICH
   Mein Trainingsstand reicht bis [Monat Jahr]. Bitte prüfe heute auf den
   offiziellen Quellen, ob die folgenden Versionen aktuell, unterstützt
   und nicht durch Deprecations belastet sind:
     - [Komponente A]: vorgeschlagen [Version] – aktuell? EOL? Empfohlen?
     - [Komponente B]: vorgeschlagen [Version] – aktuell? EOL? Empfohlen?
   Antwortformat pro Zeile: „bestätigt" ODER „ersetzt durch <Version>".
   ```

   Erst nach Bestätigung oder Korrektur wird die Version in `project-context.md` Abschnitt 3 mit Pflicht-Vermerk `Verifiziert: YYYY-MM-DD` eingetragen und in ADR-002 gesperrt. Ohne Verifikation bleibt Modus 2 stehen — keine stillen Annahmen, keine Rate-Versionen.

3. **Härtungs-Schritt:** Konzept aus Entwicklersicht prüfen. Inkonsistenz-Suche zwischen Vision-Aussagen, Constraints und vorgeschlagenen Optionen. Gefundene Probleme entweder in Modus 2 auflösen oder als ersten Eintrag in `blockers.md` mit Status „Aktiv" anlegen.
4. **`docs/architecture.md`** mit dem Architektur-Grobschnitt befüllen, soweit aus Vision und Stack-Entscheidung ableitbar. Schnittstellenverträge so weit, wie sie aus dem Konzept ableitbar sind. Lücken explizit als „TBD nach Schritt X.Y" markieren mit Fahrplan-Referenz. **Stufe-2-Bestätigung der Klassifikation:** Architektur-Indikatoren mit Hypothese aus Schritt 1 abgleichen. Bei Abweichung: ADR-001 anpassen, betroffene Strukturentscheidungen korrigieren.
5. **`docs/decisions.md`** befüllen:
   - **ADR-001:** Projektgrößen-Klassifikation und Anpassung des Vorlagen-Sets.
   - **ADR-002:** Stack-Entscheidung mit Optionen aus Schritt 2 und Begründung.
   - **ADR-003:** Architektur-Pattern-Entscheidung.
   - Weitere ADRs für jede in der Konzeptphase getroffene Grundsatzentscheidung.
6. **`docs/fahrplan.md`** befüllen: Phasen aus dem Konzept ableiten, erste Phase mit konkreten Schritten füllen (jeder Schritt im vollen Format), spätere Phasen können gröber sein und werden im Verlauf verfeinert. Strukturform nach Klasse.
7. **`docs/blockers.md`** auf Startzustand setzen (entweder leer mit „Keine aktiven Blocker" oder mit den im Härtungs-Schritt identifizierten Blockern).
8. **`docs/logbuch.md`** auf Startzustand setzen: Beispiel-Einträge entfernen, Pflege-Hinweise behalten. Erster realer Eintrag entsteht beim Start der ersten regulären Session nach Modus-2-Abschluss.
9. **`README.md`** befüllen aus den jetzt vorliegenden Dokumenten. Badge-Auswahl und Strukturwahl nach Klasse (siehe README-Vorlage). Initialisierungshinweis am Dateiende entfernen.
10. **CI-Workflow- und Pre-Commit-Skelett** aus `templates/` in das Projekt kopieren und anpassen. Quelle pro Klasse und Sprache:
    - **Klasse K:** `templates/github-workflows/ci-minimal.yml` → `.github/workflows/ci.yml`.
    - **Klasse M/G:** `templates/github-workflows/ci-<sprache>.yml` → `.github/workflows/ci.yml` (bei mehreren Sprachen mehrere Workflow-Dateien oder Job-Komposition); bei G zusätzlich `security.yml` und `release.yml` ableiten.
    - **Klasse V:** `ci-<sprache>.yml` pro Service nach `.github/workflows/ci-<service>.yml` mit Path-Filtern, plus eigene `integration.yml`.
    - **Pre-Commit:** `templates/pre-commit/<sprache>.yaml` → `.pre-commit-config.yaml` im Repo-Root.
    Alle `# TBD:`-Platzhalter (Sprachversion, Pfade, Coverage-Schwellen, Tool-Versionen) durch konkrete Werte aus `project-context.md` Abschnitt 7 ersetzen. GitHub Actions ist **Diagnoseschicht zusätzlich zu lokalen Hooks**, kein Ersatz.
11. **`docs/vision.md` Überführungs-Status** am Dateiende abhaken.
12. **Initialisierungs-Commit** mit allen Dokumenten und der Workflow-/Hook-Konfiguration. Commit-Message: `init: Projekt initialisiert aus vision.md, Klasse [K/M/G/V], ADR-001 bis ADR-NNN`.

**Iterationsregel innerhalb von Modus 2:** Wenn ein späterer Schritt eine frühere Annahme kippt (z. B. die Architektur in Schritt 3 zeigt, dass eine Stack-Option aus Schritt 1 nicht trägt): zurückspringen, betroffene Abschnitte überarbeiten. Keine stillen Korrekturen.

**Was Modus 2 nicht tut:**

- Keine Erweiterung der Vision. `vision.md` wird nicht mehr inhaltlich verändert. Wenn neue Erkenntnisse die Vision sprengen würden: Modus 2 abbrechen, zurück zu Modus 1, Mensch entscheiden lassen.
- Keine Anwendungslogik. Modus 2 produziert Dokumente sowie das CI-/Hook-Skelett aus Schritt 10 – aber keinen Anwendungscode, keine Tests, keine Konfiguration über das Qualitätsgate-Setup hinaus.

### Übergang zu regulärem Betrieb

Nach dem Initialisierungs-Commit ist die Initialisierung abgeschlossen. Ab diesem Punkt:

- `vision.md` wird nicht mehr verändert. Substantielle Vision-Pivots erzeugen einen neuen ADR mit Verweis auf den ursprünglichen Vision-Abschnitt.
- Reguläres Regelwerk (Abschnitt 2 ff.) gilt.
- Weitere Sessions finden typischerweise in Claude Code statt (1M Kontext).

## 1B. Projektgrößen-Klassifikation

Vor der Befüllung der Vorlagen in Modus 2 wird das Projekt in eine von vier Größenklassen eingestuft. Die Klasse bestimmt die **Default-Struktur** des Vorlagen-Sets. Abweichungen sind möglich, aber begründungspflichtig per ADR.

### Zweistufige Ableitung

Die Klassifikation erfolgt in zwei Stufen, weil Vision allein häufig zu vorsichtig (oder zu ehrgeizig) schätzt und Architektur die Realität korrigiert:

**Stufe 1: Vision-basierte Schätzung** (zu Beginn von Modus 2, vor `project-context.md`-Befüllung)

Indikatoren aus `vision.md`:

- Anzahl der im Zielbild und in den Beispielszenarien ableitbaren Module
- Dichte und Schärfe der Constraints (z. B. DSGVO + Self-Hosting + Compliance = hohe Dichte)
- Anzahl externer Stakeholder oder Nutzergruppen
- Erwartete Last und Skalierungsanforderung
- Anzahl externer Abhängigkeiten und Integrationen

Diese Stufe erzeugt eine vorläufige Klassen-Hypothese.

**Stufe 2: Architektur-basierte Bestätigung** (nach `project-context.md` und vor `architecture.md`-Befüllung)

Indikatoren aus dem Architektur-Grobschnitt:

- Anzahl Services oder Deployment-Einheiten (1 / 2–3 / 4–7 / >7)
- Anzahl modulübergreifender Schnittstellen
- Synchron-Monolith vs. asynchron/verteilt
- Stateless vs. Stateful-Komponenten
- Persistenzschichten (eine Datenbank / mehrere / heterogen)

Wenn Stufe 2 die Hypothese bestätigt: weiter wie geplant. Wenn Stufe 2 abweicht: zurück zu Stufe 1, neue Klasse als ADR-001 dokumentieren mit Begründung.

### Die vier Klassen

#### Klasse K – Klein

**Indikatoren:** 1 Modul, 0–1 externe Abhängigkeiten, einzelne Sprache, kein Persistenzlayer oder triviale lokale Datei, kein verteilter Aspekt, einzelner Nutzer oder kleine homogene Nutzergruppe.

**Typische Vertreter:** CLI-Tool, einzelnes Skript, Library mit klar abgegrenztem Zweck, Automatisierung.

**Default-Struktur:**

- `vision.md` – wie immer, aber kann kürzer ausfallen
- `project-context.md` – nicht-relevante Abschnitte entfernen (z. B. Skalierung, Observability)
- `architecture.md` – Modul-Karte entfällt, Schnittstellenverträge nur wenn nicht-trivial, kein Datenfluss-Abschnitt
- `fahrplan.md` – flache Schrittliste ohne Phasenstruktur, Phasentyp pro Schritt
- `decisions.md` – als Einzeldatei, Teil C (Regeln) bleibt leer bis Bedarf entsteht
- `blockers.md` – wie immer
- **CI-Workflow** (`.github/workflows/ci.yml`) – minimal: ein Job mit Lint und Test auf Push und PR. Pre-Commit-Hooks tragen lokal die Hauptlast; Actions ist hier reine Diagnoseschicht.

#### Klasse M – Mittel

**Indikatoren:** 2–5 Module, 2–5 externe Abhängigkeiten, ein bis zwei Sprachen, eine Persistenzschicht, monolithisches Deployment oder eng gekoppeltes Frontend+Backend, eine Nutzergruppe mit Rollen.

**Typische Vertreter:** typische Web-Anwendung (Backend+Frontend mit Datenbank), interne Tools mit UI, einzelner Microservice mit eigener Persistenz, Daten-Pipeline mit ein bis zwei Stufen.

**Default-Struktur:**

- Alle sieben Dokumente in voller Form
- `architecture.md` – ein Dokument, alle Abschnitte
- `decisions.md` – als Einzeldatei
- `fahrplan.md` – Phasenstruktur mit 3–5 Phasen
- Ein gemeinsamer `docs/`-Ordner
- **CI-Workflow** (`.github/workflows/ci.yml`) – voller Satz an Gates pro Sprache: Lint, Format-Check, Type-Check, Security-Scan, Dependency-Audit, Tests mit Coverage. Matrix-Build, falls mehrere Sprachversionen unterstützt werden. Branch-Protection auf Hauptbranch verlangt grüne Pipeline.

#### Klasse G – Groß

**Indikatoren:** 6+ Module, 5+ externe Abhängigkeiten, oft mehrere Sprachen, mehrere Persistenzschichten oder gemischte Speichertechnologien, ein bis zwei Deployment-Einheiten aber nicht stark verteilt, mehrere Nutzergruppen mit unterschiedlichen Rollen, NFR-Komplexität (Performance, Skalierung, Compliance).

**Typische Vertreter:** komplexe Web-Anwendung mit Auth-System, Multi-Tenant-Plattform, Daten-Pipeline mit mehreren Stufen und Speichern, ML-System mit Trainings- und Inference-Pfad ohne starke Verteilung.

**Default-Struktur:**

- Alle sieben Dokumente, plus optional Modul-spezifische Architektur-Dokumente
- `architecture.md` – als Index mit Verweisen auf `architecture-<modul>.md`-Unterdokumente, sobald die zentrale Datei unübersichtlich wird (>500 Zeilen oder >5 Module mit eigenen Schnittstellen)
- `decisions.md` – als Index mit Teil B (Übersicht) und Teil C (Regeln) zentral; einzelne ADRs in `decisions/ADR-NNN.md`-Dateien sobald die ADR-Anzahl zweistellig wird
- `fahrplan.md` – Phasenstruktur mit 5–7 Phasen, ggf. Teil-Fahrpläne pro Modul unter `docs/fahrplan-<modul>.md`
- Reaktiv-ADR-Schwellenwert in `project-context.md` strenger fassen (z. B. 20 % statt 30 %), weil bei dieser Größe reaktive Architekturentscheidungen schneller eskalieren
- **CI-Workflow** – voller Gate-Satz wie Klasse M, zusätzlich aufgeteilt in mehrere Workflow-Dateien, sobald die Pipeline unübersichtlich wird (z. B. `ci.yml`, `security.yml`, `release.yml`). Pflicht-Job für modulübergreifende Integrationstests. Caching von Abhängigkeiten und Build-Artefakten ist Default.

#### Klasse V – Verteilt-Groß

**Indikatoren:** mehrere unabhängig deploybare Services (3+), asynchrone Kommunikation zwischen Services, mehrere heterogene Persistenzschichten, GPU- oder andere Spezial-Workloads, hohe Compliance-Anforderungen (DSGVO, regulatorisch), externe Drittsysteme mit eigenem Lifecycle, Multi-Repo möglich.

**Typische Vertreter:** ML-Plattform mit getrenntem Training/Inference/Serving, Multi-Service-Architektur mit Event-Bus, Compliance-pflichtige verteilte Systeme.

**Default-Struktur:**

- `vision.md` – wie immer, aber Stakeholder- und Compliance-Abschnitte besonders sorgfältig
- `project-context.md` – als Index mit `project-context-<service>.md` für service-spezifische Stack-Details, oder als ein Dokument mit klar getrennten Service-Abschnitten
- `architecture.md` – **immer** als Index, Pflicht-Splitting in `architecture-<service>.md`-Dateien, plus separates `architecture-integration.md` für service-übergreifende Verträge und Event-Definitionen
- `decisions.md` – als Index mit Teil B und Teil C zentral, einzelne ADRs in `decisions/ADR-NNN.md`-Dateien von Anfang an
- `fahrplan.md` – als Master-Index mit Teil-Fahrplänen pro Service unter `docs/fahrplan-<service>.md`
- Reaktiv-ADR-Schwellenwert besonders streng (z. B. 15 %), zusätzlich Service-spezifische Reaktiv-Quoten getrennt überwachen
- **Pflicht-ADR-Themen für Klasse V:** Service-Grenzen-Definition, Versionierungsstrategie zwischen Services, Failure-Mode-Handling, Datenkonsistenz-Strategie (eventual / strict), Observability-Standard
- **CI-Workflow** – pro Service eigener Workflow unter `.github/workflows/ci-<service>.yml` mit Path-Filtern, plus separater `integration.yml` für service-übergreifende End-to-End-Tests und Vertrags-Prüfungen (z. B. Pact, Schema-Kompatibilität). `release.yml` und `security.yml` zentral. Reusable Workflows zur Vermeidung von Duplikation sind Pflicht.

### Klassifikations-ADR

Die Klassifikation wird in **ADR-001 als `[STRATEGISCH] [METHODIK]`** dokumentiert mit:

- gewählte Klasse mit Begründung aus Vision- und Architektur-Indikatoren
- daraus folgende Strukturentscheidungen (welche Dateien einzeln, welche als Index, welche Teil-Dokumente)
- abweichende Entscheidungen vom Default mit Begründung

### Reklassifikation

Wenn ein Projekt im Verlauf wächst (typischerweise K→M oder M→G):

- **Trigger:** mindestens zwei Indikatoren der höheren Klasse erfüllt, oder die Dokumentstruktur wird spürbar unübersichtlich.
- **Vorgehen:** ADR mit `[STRATEGISCH] [METHODIK]` und Tag `Reklassifikation`, Plan zur Migration der Dokumentstruktur, Migration als eigene STABILISIERUNG-Phase im Fahrplan.
- **Keine Reklassifikation rückwärts** ohne starken Grund – wenn ein Projekt vereinfacht wurde, ist das eher Anlass für Refactoring als für Vorlagen-Schrumpfung.

## 2. Pflichtlektüre zu Sessionbeginn

**Vor jeder Änderung** liest Claude die Pflichtlektüre. Sie ist zweistufig: eine **strikte Mindest-Lektüre**, die immer geladen wird, und eine **Vertiefung auf Anforderung**, die nur bei konkretem Bedarf erfolgt. Diese Trennung schont das Kontextfenster und verhindert, dass irrelevantes Hintergrundmaterial die Aufmerksamkeit verwässert.

### Mindest-Lektüre (Pflicht, in dieser Reihenfolge)

1. **`docs/project-context.md`** – das gesamte Dokument. Es enthält Stack, Constraints und projektspezifische Regeln, die jede Änderung betreffen können. Vollständig.
2. **`docs/logbuch.md`** – nur den **letzten `[SESSIONENDE]`-Eintrag plus alle Einträge danach**. Diese Auswahl liefert den Wiedereinstiegspunkt. Frühere Sessions werden nicht gelesen.
3. **`docs/fahrplan.md`** – nur den Abschnitt **„Aktueller Stand"** plus die **aktuell laufende Phase mit ihren Schritten**. Andere Phasen, Replanning-Historie und Archiv werden nicht gelesen.
4. **`docs/architecture.md`** – nur die Abschnitte **„Überblick" (1)**, **„Modul-Karte" (2)** und **„Reifegrad-Übersicht" (9)**. Detailspezifikationen einzelner Module und Schnittstellen werden nicht gelesen.
5. **`docs/decisions.md`** – nur **Teil A (ADR-Übersicht und Reaktiv-Quote)**. Einzelne ADR-Einträge in Teil B werden nicht gelesen.
6. **`docs/blockers.md`** – nur den Abschnitt **„Aktive Blocker"**. Gelöste Blocker und Erkennungs-Heuristiken werden nicht gelesen (letztere sind in CLAUDE.md Abschnitt 8 verankert).

Direkt nach der Mindest-Lektüre, **vor jeder anderen Aktion**: `[SESSIONSTART]`-Eintrag im Logbuch anlegen.

### Vertiefung auf Anforderung

Während der Arbeit lädt Claude **gezielt zusätzliche Abschnitte** nach, sobald eine konkrete Anforderung das nötig macht. Faustregel: Jede Vertiefung muss durch eine konkrete Aufgabe begründet sein, nicht durch generelles Sicherheitsbedürfnis.

Auslöser-Beispiele:

- Ein Schritt berührt **Modul X** → vollständiger Modul-Eintrag in `architecture.md` Abschnitt 3 plus zugehörige Schnittstellenverträge in Abschnitt 4 werden gelesen.
- Ein Schritt referenziert **ADR-Y** → Volltext dieses ADR in `decisions.md` Teil B wird gelesen.
- Ein Schritt **berührt einen aktiven Blocker** → Volltext des betreffenden Blocker-Eintrags wird gelesen, andere Blocker bleiben unberührt.
- Eine **Architekturentscheidung** steht an → Abschnitt „Verworfene Alternativen" in `architecture.md` Abschnitt 8 wird zusätzlich gelesen, um keine bereits abgelehnten Optionen vorzuschlagen.
- **Ein offenes Problem ähnelt einem früheren** → relevante Logbuch-Einträge älterer Sessions werden gezielt gesucht (per Datum oder Stichwort), nicht das gesamte Logbuch durchgelesen.
- Eine **NFR-Frage taucht auf** → `architecture.md` Abschnitt 6 wird gelesen.
- **Compliance- oder Lizenzfrage** → `project-context.md` Abschnitt 6 ist bereits aus Mindest-Lektüre vorhanden, ggf. CHANGELOG für Versionsverlauf.

### Was nicht zur Pflichtlektüre gehört

- `docs/vision.md` wird **einmalig** zu Projektstart gelesen und danach nur referenziert, wenn ein ADR explizit darauf verweist. Im regulären Betrieb gehört Vision nicht zur Pflichtlektüre.
- `README.md` wird zu Sessionbeginn **nicht gelesen** (sie ist abgeleitet aus den Pflicht-Dokumenten und enthält keine zusätzliche Information). Sie wird zu Sessionende geprüft und synchronisiert (Abschnitt 16).
- `CHANGELOG.md` wird nur bei Releases oder Versions-Fragen gelesen.

### Kein Überspringen der Mindest-Lektüre

Auch bei kleinen Änderungen wird die Mindest-Lektüre vollständig durchlaufen. Der Aufwand dafür ist bewusst eingeplant und beträgt durch die selektive Auswahl pro Dokument nur einen Bruchteil dessen, was eine Volllektüre kosten würde. „Kleine Änderung, brauche ich nicht" ist keine zulässige Begründung.

## 3. Dokumenten-Index

| Datei | Zweck | Aktualisierungstrigger |
|---|---|---|
| `docs/vision.md` | Eingangs-Idee, Ziel, Erfolgskriterien, Abgrenzungen | Einmalig zu Projektstart (siehe Abschnitt 1A); danach unverändert |
| `docs/project-context.md` | Projektdefinition, Stack, Status, Constraints | Statuswechsel, Stack-Änderung, neue Constraints |
| `docs/fahrplan.md` | Arbeitsschritte, Fortschritt, Status | Nach jedem Schritt; zu Sessionende; bei Replanning |
| `docs/architecture.md` | Module, Schnittstellen, Datenflüsse, NFRs | Bei jeder Architekturänderung (freigabepflichtig) |
| `docs/decisions.md` | ADRs, Entscheidungsregeln | Bei jeder freigabepflichtigen Entscheidung |
| `docs/blockers.md` | Ungelöste Probleme, gescheiterte Ansätze | Bei jedem Blocker; bei Auflösung verschieben |
| `docs/logbuch.md` | Chronologische Ereignis-Aufzeichnung: Sessionrahmen, Problemlösungen, Reifegrad-Wechsel, ADRs, Beobachtungen | Bei Sessionstart, bei jedem nennenswerten Ereignis während der Session, bei Sessionende |
| `README.md` | Aktuelles Statusbild des Projekts: Vision-Auszug, Status-Block aus Pflicht-Dokumenten, Quick Start, Badge-Zone, Architektur-Skizze, nächste Schritte | Bei jedem nutzerrelevanten `[ERLEDIGT]`-Schritt; vor jedem Sessionende mit Synchronisations-Prüfung; bei Statuswechsel und Versionserhöhung |
| `CHANGELOG.md` | Nutzerrelevante Änderungen, SemVer-Einträge | Bei jedem Release, bei Breaking Changes |

Struktur und Umfang der Dokumente ergeben sich aus dem Projektkontext (CLI bis verteiltes System). Alle Dokumente existieren als Vorlagen mit Initialisierungshinweisen. Bei der **ersten Session nach Projektanlage** passt Claude jede Vorlage an die Projektkomplexität an und hält die Anpassung als **ADR-001** in `decisions.md` fest.

## 4. Freigabepflichtige Entscheidungen

Die folgenden Kategorien werden **niemals** eigenständig umgesetzt. Claude formuliert einen konkreten Vorschlag mit Alternativen und Konsequenzen und wartet auf Freigabe, bevor Code verändert wird.

1. **Architekturänderungen:** neue Schichten, Änderung von Modulgrenzen, Änderung der Kommunikationsmuster zwischen Modulen, Wechsel synchron↔asynchron.
2. **Neue Module oder Komponenten:** jede Einheit, die eine neue Verantwortung im System übernimmt.
3. **Externe Abhängigkeiten:** neue Bibliotheken, SaaS-Dienste, APIs, CLI-Tools, Container-Images. Versions-*Updates* bestehender Abhängigkeiten sind nur dann freigabepflichtig, wenn sie Major-Versionen sind oder Breaking Changes enthalten.
4. **Datenmodelländerungen:** neue Entitäten, Schema-Migrationen, Änderungen an Primär-/Fremdschlüsseln, Änderungen an Indexstrategien.
5. **API-Vertragsänderungen:** jede Änderung an öffentlichen Schnittstellen (HTTP-Routes, CLI-Flags, Bibliotheks-Exporte), die nicht rein additiv und rückwärtskompatibel ist.
6. **Sicherheit und Datenschutz:** Authentifizierungs-/Autorisierungslogik, Umgang mit Geheimnissen, personenbezogenen Daten, Kryptographie, Logging sensibler Informationen.
7. **Build- und Deploy-Pipeline:** CI/CD-Änderungen, Container-Orchestrierung, Deployment-Ziele, Infrastructure-as-Code.
8. **Lizenz- und Compliance-relevante Änderungen:** neue Abhängigkeiten mit restriktiven Lizenzen, Änderungen an der Projektlizenz selbst.

**Form des Vorschlags:**

```
ENTSCHEIDUNG ERFORDERLICH
Kategorie: [aus Liste oben]
Kontext: [warum die Frage jetzt aufkommt, 1–3 Sätze]
Optionen:
  A: [Option mit Konsequenzen]
  B: [Option mit Konsequenzen]
  C: [ggf. weitere]
Empfehlung: [A/B/C] – Begründung [1–2 Sätze]
Blockiert Arbeit an: [Fahrplan-Einträge, die ohne Entscheidung nicht fortgeführt werden können]
```

Nach Freigabe: ADR in `decisions.md` anlegen, **erst dann** implementieren.

## 5. Autonomiebereich (freigabefrei)

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

## 6. Harte Regeln

- **Keine Implementierung ohne Fahrplan-Referenz.** Jede Codeänderung zeigt auf einen `[IN ARBEIT]`-Eintrag. Existiert keiner: Eintrag anlegen und als solchen kennzeichnen, oder bei freigabepflichtigen Themen nach Abschnitt 4 verfahren.
- **Keine stillen Annahmen.** Fehlt eine für die Implementierung nötige Information (API-Vertrag, Datentyp, Fehlerbehandlung, erwarteter Zustandsübergang): stoppen und gezielt nachfragen. Rate-Implementierungen sind verboten, auch wenn sie „naheliegend" wirken.
- **Keine Erfolgsmeldungen ohne Verifikation.** „Implementiert" ist nicht „fertig". Fertig ist, was die Definition of Done (Abschnitt 9) erfüllt. Formulierungen wie „sollte funktionieren", „müsste durchlaufen" sind unzulässig – entweder ausgeführt und verifiziert oder als offen markiert.
- **Keine Platzhalter-Implementierungen ohne Kennzeichnung.** Stubs, Mocks, Dummy-Returns werden im Code mit `TODO(fahrplan-ref: X)` markiert und in `fahrplan.md` als `[OFFEN]`-Schritt geführt.
- **Modulgrenzen respektieren.** Kein Zugriff aus Modul A auf interne Strukturen von Modul B. Kommunikation ausschließlich über definierte Schnittstellen. Verletzung dieser Regel ist eine Architekturänderung nach Abschnitt 4.
- **Keine heimlichen Scope-Erweiterungen.** Entdeckte Verbesserungspotenziale werden im Fahrplan als Vorschlag notiert und warten auf Freigabe. Gleichzeitige „ich habe das auch noch schnell gemacht"-Änderungen sind verboten.
- **Determinismus vor Kreativität.** Bei mehreren validen Implementierungsoptionen: die wählen, die bestehenden Mustern im Repo folgt. Neue Muster einzuführen ist eine Architekturentscheidung.
- **Secrets niemals im Code oder Log.** Nie Zugangsdaten, Tokens, private Schlüssel, PII in Code, Tests, Logs, Commit-Messages oder Dokumentation einfügen. Platzhalter-Environment-Variablen sind zu verwenden.
- **Reproduzierbarkeit vor Performance.** Abhängigkeiten werden pinned, Umgebungen sind deterministisch. Nicht-deterministische Tests sind Blocker, keine akzeptierte Flakiness.
- **Code-Standards sind verbindlich.** Die in Abschnitt 15 definierten Pflicht-Tool-Kategorien müssen für die jeweils verwendete Sprache aktiv und in der Pipeline durchgesetzt sein. Konfiguration und Toolwahl pro Sprache erfolgt in `project-context.md` Abschnitt 7. Keine Codeänderung darf Standards umgehen, deaktivieren oder lokal überschreiben (`# noqa`, `eslint-disable`, `@ts-ignore`, `# type: ignore` etc.) ohne expliziten Kommentar mit Begründung und Fahrplan-Referenz.
- **Architektur-Reifegrad respektieren.** Vor jeder UMSETZUNG-Phase müssen die berührten Architektur-Bestandteile in `architecture.md` den Reifegrad `[BELASTBAR]` haben. Bestandteile mit `[VORLÄUFIG]` oder `[OFFEN]` sind kein Implementierungsgrund, sondern ein Erkundungsgrund: ERKUNDUNG-Schritt anlegen, nicht raten. Stille Beförderung von `[VORLÄUFIG]` auf `[BELASTBAR]` ohne Validierung oder ADR ist verboten.
- **Phasentyp-Disziplin.** Schritte werden im Akzeptanzformat ihres Phasentyps geprüft (ERKUNDUNG: wissensbasiert, UMSETZUNG: funktionsbasiert, STABILISIERUNG: qualitätsbasiert). Vermischung („wir bauen mal schnell ein Feature in der Erkundungsphase") ist verboten – wenn das Bedürfnis aufkommt, ist es ein Signal, dass ein neuer UMSETZUNG-Schritt anzulegen ist.
- **Reaktiv-ADR-Disziplin.** Wenn während einer UMSETZUNG-Phase eine Architekturentscheidung nötig wird, die nicht in der Phasenplanung vorgesehen war: STOPP. Ein `[REAKTIV]`-ADR ist die Ausnahme, nicht der Normalfall. Häufung deutet auf zu schwache Architektur hin – siehe Reaktiv-Schwellenwert in `project-context.md`.
- **Logbuch-Einträge sind proaktiv.** Sessionstart, Sessionende, gelöste Probleme (auch kleine, mehrminütige Reibungen), Reifegrad-Wechsel, neue ADRs und nennenswerte Beobachtungen werden im Logbuch festgehalten, **ohne dass der Mensch dazu auffordert**. Bei Unsicherheit, ob ein Eintrag Wert hat: eintragen. Lieber ein zu detailreiches Logbuch als ein lückenhaftes – das Logbuch lebt davon, dass Mini-Reibungen festgehalten werden, weil ihr Wert oft erst Wochen später sichtbar wird.

## 7. Status-Marker

Einheitlich in `fahrplan.md` und `blockers.md`:

- `[OFFEN]` – definiert, noch nicht begonnen
- `[IN ARBEIT]` – aktuell in Bearbeitung (maximal ein Eintrag gleichzeitig pro Session)
- `[WARTET-AUF-FREIGABE]` – Vorschlag formuliert, wartet auf Entscheidung
- `[BLOCKIERT]` – nicht fortsetzbar, siehe `blockers.md`
- `[ERLEDIGT]` – Definition of Done erfüllt, verifiziert, mit Datum
- `[VERWORFEN]` – bewusst nicht umgesetzt, mit ADR-Referenz

## 8. Stopp-Kriterien

Claude stoppt die aktuelle Arbeit **zwingend und sofort** in folgenden Situationen:

1. **Informationslücke:** Für die Umsetzung nötige Information fehlt in allen Pflicht-Dokumenten.
2. **Widerspruch:** Zwei Dokumente widersprechen sich, ohne dass ein ADR den Konflikt auflöst.
3. **Freigabebedarf:** Eine der Kategorien aus Abschnitt 4 wird berührt.
4. **Dreifach-Fehlschlag:** Derselbe Ansatz ist dreimal gescheitert (siehe Abschnitt 10).
5. **Fremde Modulgrenze:** Die nötige Änderung reicht in ein Modul hinein, das nicht Teil des aktuellen Fahrplan-Schritts ist.
6. **Destruktiver Eingriff:** Löschung von Daten, Drop von Tabellen, `git push --force`, Änderung an Historie – auch wenn Tests es verlangen.
7. **Unklare Testlage:** Tests, die die Änderung absichern sollen, fehlen oder sind nicht eindeutig. Keine Implementierung ohne Absicherungsstrategie.

Form des Stopps:

```
STOPP
Grund: [aus Kategorien oben]
Kontext: [was war in Arbeit]
Benötigt: [was zur Fortsetzung nötig ist]
Vorgeschlagene Auflösung: [falls möglich]
```

Kein Umgehen durch „ich versuche es mal ohne".

## 9. Definition of Done

Ein Arbeitsschritt ist **nur dann** `[ERLEDIGT]`, wenn **alle** folgenden Punkte erfüllt sind:

- [ ] Code ist geschrieben, syntaktisch korrekt.
- [ ] **Linter** läuft ohne Fehler (Konfiguration: `project-context.md` Abschnitt 7).
- [ ] **Formatter** wurde ausgeführt; Code entspricht dem definierten Stil.
- [ ] **Type-Checker** läuft grün, sofern für die Sprache anwendbar.
- [ ] **Security-Scanner** läuft ohne neue Findings, sofern für die Sprache anwendbar.
- [ ] Tests auf Funktionsebene existieren und laufen grün.
- [ ] Testabdeckung der geänderten Einheit ist dokumentiert (konkrete Zahl, nicht „ausreichend").
- [ ] Integrationstests oder End-to-End-Tests laufen grün, sofern für die geänderte Funktionalität relevant.
- [ ] **Pre-Commit-Hook** war aktiv und erfolgreich (kein `--no-verify`).
- [ ] Inline-Dokumentation (Docstrings/JSDoc/o. Ä.) ist vorhanden und aktuell.
- [ ] Betroffene Dokumente in `docs/` sind aktualisiert.
- [ ] Bei nutzerrelevanten Änderungen: `CHANGELOG.md` ist ergänzt.
- [ ] Bei nutzerrelevanten Änderungen: `README.md` ist aktualisiert (siehe Abschnitt 16, Trigger 1).
- [ ] Keine offenen `TODO`-Kommentare ohne Fahrplan-Referenz.
- [ ] Keine ungebridgten Lint-/Type-Suppressions ohne Begründungs-Kommentar.
- [ ] **CI-Pipeline** läuft grün – Lint, Format-Check, Type-Check, Security-Scan, Tests sind Pflicht-Gates.
- [ ] Commit ist erstellt (Konvention Abschnitt 11).

Unvollständige DoD = Status bleibt `[IN ARBEIT]`. Keine Ausnahme, keine „fast fertig"-Kennzeichnung.

## 10. Blocker-Protokoll

Bei **dreifachem Scheitern** am selben Problem:

1. **Nicht** einen vierten Versuch mit kleiner Variation starten.
2. Eintrag in `docs/blockers.md` erstellen mit: Beschreibung, Reproduktion, drei versuchte Ansätze mit je Grund des Scheiterns, offene Hypothesen, konkrete Freigabe-/Klärungsfrage.
3. Fahrplan-Eintrag auf `[BLOCKIERT]` setzen.
4. Falls möglich: anderen Fahrplan-Eintrag wählen, der nicht vom Blocker abhängt. Falls alles davon abhängt: Session sauber abschließen (Abschnitt 12).

Was als „derselbe Ansatz" zählt: gleiche Grundidee mit Variation in Details (Bibliothek, Parameter, Reihenfolge). Drei syntaktische Varianten desselben Konzepts sind ein Ansatz, kein Dreifach-Versuch.

## 11. Commit- und Branch-Konvention

**Commit-Format:**
```
<bereich>: <kurze beschreibung im imperativ>

[optional: längere erklärung, fahrplan-ref, breaking changes]

Fahrplan: [eintrags-id oder phase/schritt-nummer]
```

**Regeln:**
- Atomare Commits: eine logische Änderung pro Commit.
- Imperativ, Präsens: „füge X hinzu", nicht „hinzugefügt" oder „adds X".
- Keine `WIP`-Commits auf Hauptbranches.
- Keine Mix-Commits (Feature + Refactoring + Format) – aufsplitten.
- Bei freigabepflichtigen Änderungen: ADR-Nummer im Commit-Body referenzieren.

**Branches:**
- Hauptbranch: wie im Repo konfiguriert. Umbenennung ist freigabepflichtig.
- Feature-Branches: `feat/<kurztitel>`, Bugfix: `fix/<kurztitel>`, Refactor: `refactor/<kurztitel>`.
- Push-Regeln auf Hauptbranch werden in `project-context.md` festgelegt.

## 12. Sessionende-Disziplin

Vor Abschluss jeder Session, auch bei Unterbrechung mitten in einer Aufgabe:

1. `docs/fahrplan.md` aktualisieren: aktueller Stand, nächster konkreter Schritt.
2. **`README.md` synchronisieren** (siehe Abschnitt 16): Status-Block, Badges, „Nächste Schritte" gegen Pflicht-Dokumente abgleichen. Drift = Bug = vor Sessionende beheben.
3. **`docs/logbuch.md` `[SESSIONENDE]`-Eintrag** anlegen mit Session-Dauer, bearbeiteten Schritten, erreichtem Stand, offen Gebliebenem, nächstem Schritt.
4. Alle Änderungen committen oder explizit als uncommitted markieren mit Begründung.
5. Offene Gedanken in Fahrplan oder als Kommentar im betroffenen Schritt festhalten.
6. Bei offenen Stopp-Situationen: entsprechenden STOPP-Block im Fahrplan hinterlegen.

**Kein** Abschluss mit offenem `[IN ARBEIT]`-Eintrag ohne Statushinweis. Die nächste Session muss in unter fünf Minuten den Kontext rekonstruieren können – das Logbuch ist dafür das primäre Werkzeug.

## 13. Kommunikationsstil

- **Ehrlich statt gefällig.** Scheitern wird gemeldet, nicht überspielt.
- **Konkret statt vage.** Zahlen, Dateinamen, Zeilen, Testnamen – nicht „es läuft".
- **Vollständigkeit vor Knappheit.** Wenn Zusatzinformation den Menschen zur schnelleren Entscheidung befähigt: mitliefern.
- **Keine Sycophancy.** Keine Zustimmungsfloskeln. Keine Lobhudelei. Reine Arbeitskommunikation.
- **Rückfragen sind erwünscht** bei echten Lücken. Sie sind verboten bei Informationen, die in den Pflicht-Dokumenten stehen – dort nachlesen.

## 14. Archivierung

Wenn ein Dokument unübersichtlich wird (Richtwert: >500 Zeilen, oder spürbare Suchzeit):

- Erledigte Einträge nach `docs/archiv/<dokument>-YYYY-MM.md` auslagern.
- Im aktiven Dokument bleibt: aktueller Stand, offene Punkte, Referenzen auf Archiv.
- Auslagerung selbst ist keine freigabepflichtige Entscheidung, aber Sessionende-Aktion.

## 15. Code-Standards (sprachneutrale Pflichtkategorien)

Für jede im Projekt verwendete Sprache müssen die folgenden Tool-Kategorien aktiv und in der CI-Pipeline als Gate konfiguriert sein, **sofern sie für die Sprache anwendbar sind**. Die konkrete Toolwahl pro Sprache erfolgt in `project-context.md` Abschnitt 7.

### Pflichtkategorien

1. **Linter** – statische Codeanalyse für Stil- und Logikfehler. Pflicht für alle Sprachen mit etablierten Lintern.
2. **Formatter** – deterministische Code-Formatierung. Pflicht, wenn ein Formatter für die Sprache existiert. Manuelle Formatierung ist verboten, sobald ein Formatter konfiguriert ist.
3. **Type-Checker** – statische Typprüfung. Pflicht für statisch oder gradual typisierte Sprachen. Strict-Modus ist Default; Abweichungen erfordern ADR.
4. **Security-Scanner** – statische Sicherheitsanalyse. Pflicht, wenn ein Standard-Tool für die Sprache existiert.
5. **Dependency-Audit** – Prüfung auf bekannte Schwachstellen in Abhängigkeiten. Pflicht für alle Sprachen mit Paketmanager.
6. **Test-Runner mit Coverage** – Coverage-Messung Pflicht. Mindestwerte werden in `project-context.md` Abschnitt 7 festgelegt.

Sprachen ohne etablierte Tools in einer Kategorie sind explizit in `project-context.md` zu vermerken („Kategorie X: nicht anwendbar für Sprache Y, Begründung: …").

### Durchsetzungsmechanismen (Pflicht)

- **Pre-Commit-Hook:** Lint, Format-Check, Type-Check, schnelle Security-Checks. Lokale Durchsetzung vor jedem Commit. Konfiguration im Repo (z. B. `pre-commit`-Framework, `husky`, `lefthook`).
- **CI-Pipeline-Gates:** Vollständige Ausführung aller Pflichtkategorien plus Tests bei jedem Push und PR. Rote Gates blockieren Merge.
- **Bypass verboten:** `git commit --no-verify`, `git push --no-verify`, manuelles Deaktivieren von CI-Checks sind nur mit expliziter Freigabe erlaubt (CLAUDE.md Abschnitt 4) und werden im Fahrplan vermerkt.

### Lokale Suppressions

Ein lokales Deaktivieren einer Regel (`# noqa`, `eslint-disable-next-line`, `@ts-ignore`, `# type: ignore`, `// nolint`, etc.) ist nur zulässig mit:

- Begründungs-Kommentar in derselben Zeile oder direkt darüber.
- Verweis auf Fahrplan-Eintrag oder ADR, falls der Grund eine Entscheidung ist.
- Möglichst engster Scope (`disable-next-line` statt `disable-file`).

Pauschale Suppressions auf Datei- oder Modulebene sind freigabepflichtig.

### Naming und Stil

- Naming Conventions folgen den sprachüblichen Standards (PEP 8 für Python, Standard-Style-Guides der Sprache, etc.).
- Bei mehreren validen Konventionen: einmalige Festlegung in `project-context.md`. Inkonsistenzen im Repo sind als Bug zu behandeln, nicht als Stilfrage.

## 16. README-Pflege

`README.md` ist das öffentliche Statusbild des Projekts und Pflichtbestandteil des Vorlagen-Sets. Sie wird **niemals sporadisch** aktualisiert, sondern folgt zwei festen Triggern.

### Trigger 1: Pro nutzerrelevantem Schritt

Während der Bearbeitung eines Fahrplan-Schritts mit nutzersichtbarer Wirkung wird die README aktualisiert. „Nutzersichtbar" heißt: der Schritt ändert Verhalten, Setup, Konfiguration, Architektur, abgeschlossene Phasen oder den Status des Projekts. Reine interne Refactorings, Test-Erweiterungen und Doku-Pflege in `docs/` lösen den Trigger nicht aus.

Konkrete Aktualisierungen pro Schritt:

- **Quick Start ändert sich:** Setup-, Installations- oder Erstausführungs-Befehle ergänzen oder anpassen.
- **Verwendung ändert sich:** Beispiele aktualisieren, neue Anwendungsfälle ergänzen.
- **Architektur ändert sich:** Architektur-Skizze und Modul-Liste anpassen, Verweise auf `architecture.md` prüfen.
- **Phase abgeschlossen:** „Nächste Schritte" auf die folgende Phase umstellen.

### Trigger 2: Sessionende-Synchronisation

Vor jedem Sessionende läuft eine Synchronisations-Prüfung gegen die Pflicht-Dokumente. Diese Prüfung ist **nicht optional** und Teil der Sessionende-Disziplin (Abschnitt 12).

Synchronisations-Quellen und -Ziele:

| README-Block | Quelle | Bei Drift |
|---|---|---|
| Status-Block: Projektphase | `fahrplan.md` „Aktueller Stand" + Phasentyp | README anpassen |
| Status-Block: Version | `project-context.md` Abschnitt 1 | README anpassen |
| Status-Block: Status | `project-context.md` Abschnitt 1 | README anpassen + Status-Badge |
| Status-Block: Architektur-Reife | `architecture.md` Abschnitt 9 (Reifegrad-Übersicht) | README-Kurzfassung anpassen |
| Status-Block: Aktive Blocker | `blockers.md` (Anzahl aus „Aktive Blocker") | README-Zähler anpassen |
| Über das Projekt | `vision.md` Abschnitte 1–3 | nur bei Vision-Pivot anpassen |
| Quick Start | `project-context.md` Abschnitt 8 + Stack | bei Stack- oder Setup-Änderungen |
| Architektur-Skizze | `architecture.md` Abschnitt 1 + 2 | bei Architektur-Änderungen |
| Nächste Schritte | `fahrplan.md` (nächste 1–3 Schritte/Phasen) | nach jedem `[ERLEDIGT]` |
| Badges | wie in der Tabelle pro Badge | bei Quell-Änderung |

**Drift zwischen README und Pflicht-Dokumenten ist ein Bug**, kein Stilfehler. Wird er bei der Sessionende-Prüfung gefunden, wird er vor dem Sessionende-Commit behoben.

### Badge-Disziplin

- **Maximalwerte pro Klasse** (siehe Abschnitt 1B): K=5, M=8, G=10, V=12.
- **Pflicht-Badges in jeder Klasse:** Status, Version, Build, License.
- **Erweiterungen pro Klasse** und **Reihenfolge in der Badge-Zeile** sind in der README-Vorlage verbindlich definiert.
- **Badges spiegeln reale Zustände.** Manuell gepflegte Fantasie-Badges („Coverage 95 %" ohne Test-Suite) sind verboten.
- **Badge-Update Pflicht im selben Commit** wie die zugrunde liegende Änderung. Beispiel: Versions-Bump in `project-context.md` und Versions-Badge in `README.md` gehören in einen Commit.

### Was die README NICHT ist

- **Kein Marketing-Dokument.** Inhalte stammen aus Pflicht-Dokumenten, nicht aus freier Hand.
- **Kein Roadmap-Vollersatz.** „Nächste Schritte" zeigt 1–3 Punkte, der vollständige Plan bleibt in `fahrplan.md`.
- **Keine vollständige Architektur-Spezifikation.** Architektur-Skizze ist Überblick, Details bleiben in `architecture.md`.
- **Keine Sammlung von Aspirationen.** Was geplant ist, aber nicht abgeschlossen, gehört in „Nächste Schritte" oder in `fahrplan.md`, nicht in „Verwendung" oder „Architektur".

---

**Hinweis für den Projektstart:** Diese Datei ist eine generische Vorlage und wird projektübergreifend unverändert übernommen. Änderungen hier betreffen die Arbeitsmethodik, nicht das einzelne Projekt. Projektspezifika gehören in `docs/project-context.md` und die weiteren Dokumente in `docs/`.
