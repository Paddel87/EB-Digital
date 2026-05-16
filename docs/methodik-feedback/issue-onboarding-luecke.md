# Methodik-Lücke: Onboarding-Tauglichkeit & Tooling-Reifegrad sind keine Pflichtkategorien — und das ist ein systematisches Risiko

> **Adressat:** Pflegende und Anwender des CLAUDE.md-Regelwerks (das in einem separaten Repository als Vorlage für zukünftige Software-Projekte gehalten wird).
>
> **Anlass:** Funktionstest nach Abschluss von Phase 2 im Pilot-Projekt EB-Digital am 2026-05-16. Test alle fünf Stufen grün, **aber** vier strukturelle Onboarding-Schulden offengelegt.
>
> **Klassifikation:** Methodik-Defekt mit dokumentierter Fallstudie. Kein Code-Bug.
>
> **Status:** Vorschlag zur Diskussion.

---

## TL;DR

Das aktuelle CLAUDE.md-Regelwerk ist nachweislich exzellent bei drei Themen — Code-Qualität, Architektur-Disziplin und Status-Konsistenz — und nachweislich **leer** bei zwei weiteren Themen, die für jedes nicht-triviale Software-Projekt strukturell genauso wichtig sind: **Onboarding-Tauglichkeit** (kann ein neuer Anwender die Software starten?) und **Tooling-Reifegrad** (sind die Hilfsskripts qualitätsgepflegt?). Diese Asymmetrie produziert Schulden, die erst beim ersten externen Anwendungs- oder Übergabe-Versuch sichtbar werden — also typischerweise zu spät, um sie ohne ein groß-angelegtes Refactoring zu schließen. Das Risiko ist **generisch** (tritt in jedem mittel- bis großen Projekt auf), **systemisch** (folgt aus der Struktur des Regelwerks selbst, nicht aus Ausführungsfehlern) und **vermeidbar** durch acht klar abgegrenzte Patches im Regelwerk und zwei neue Pflicht-Abschnitte in den Vorlagen der Pflicht-Dokumente. Dieses Issue beschreibt die Diagnose, die generische These und den konkreten Vorschlag; die Patches selbst liegen in `regelwerks-patches.md`.

---

## 1. Kontext der Erkenntnis

### 1.1 Wie das Muster sichtbar wurde

Im Pilot-Projekt EB-Digital ist Phase 2 („Auth + Tenants + Verbund-Tauglichkeit", UMSETZUNG) am 2026-05-16 mit Schritt 2.7 abgeschlossen worden. Schritt 2.7 verifizierte alle Phase-2-Coverage-Schwellen (Backend 95.84 %, Frontend-Disponent 96.61 %, Frontend-Einsatzkraft 98.38 %), schloss eine Hot-Stabilisierung des DB-Session-Lifecycle (ADR-015, Regel-018) ab und führte eine externe Security-Review als Phase-7-Issue ein. Aus methodischer Sicht: textbuchmäßiger Phasen-Abschluss, keine offenen Punkte.

In der Folgesession beauftragte der Projekt-Inhaber einen **vollständigen Funktionstest** zur Aufdeckung „eingeschlichener Fehler und Probleme". Der Test umfasste fünf Stufen:

1. Workspace-Sync (`uv sync` + `pnpm install`)
2. Backend-Tests + Coverage-Frischlauf (`uv run pytest --cov`)
3. Frontend-Tests + Coverage in beiden Workspaces (`pnpm exec vitest run --coverage`)
4. Pre-Commit auf allen Dateien (18 Hooks)
5. End-to-End-Smoke gegen den echten Docker-Compose-Stack (`scripts/dev-smoke.sh`)

Alle fünf Stufen sind nach Diagnose und Behebung dreier Reibungspunkte grün. Phase-2-Code ist verifiziert produktiv. Im Verlauf des Tests sind aber **acht** Einzelpunkte aufgefallen, von denen **sechs** keine Code-Bugs sind, sondern unsichtbare Brüche zwischen dem dokumentierten Onboarding-Pfad (README + project-context.md + Quick Start) und der Realität, die ein neuer Anwender auf einer frischen Maschine antrifft.

### 1.2 Warum das jetzt sichtbar wird

Phase 1 (Repo-Bootstrap) und Phase 2 (Auth + Tenants) zusammen haben eine bestimmte Komplexitäts-Schwelle überschritten:

- Drei Sprachen (Python, TypeScript, Bash für Hilfsskripts)
- Sechs Container-Services (PostgreSQL, Valkey, Backend, Worker, Tile-Proxy, Reverse-Proxy)
- Drei Frontend-Workspaces mit unterschiedlichen Build-Pipelines
- Eine externe Voraussetzung pro Hilfsskript (jq, curl, bash)
- Zwei Geheimnis-Kategorien (SECRET_KEY, API-Keys MapTiler/TomTom)
- Eine Plattform-Asymmetrie (macOS-Sonderfall in fix-venv-flags.sh ist verankert, Windows-Sonderfälle sind unbenannt)

Bis Phase 1 reichte das einfache „klonen, `uv sync`, `pnpm install`, `docker compose up`"-Muster. Mit Phase 2 ist es nicht mehr ausreichend — aber das Regelwerk hat den Übergang nicht erkannt.

### 1.3 Die acht Einzelpunkte (verdichtet)

Eine vollständige Tabelle mit Schweregrad und Behandlung liegt im Anhang (Abschnitt 11). Hier nur die Klassifizierung nach struktureller Wurzel:

- **Strukturell, im Regelwerk verwurzelt:** sechs Punkte
- **Situativ, phasen-bedingt:** zwei Punkte

Die sechs strukturellen Punkte lassen sich auf **vier generische Symptom-Klassen** verdichten, die in jedem Projekt auftreten können, das den aktuellen Regelwerks-Stand verwendet. Diese vier Klassen sind das Thema dieses Issue.

---

## 2. Symptome verdichtet — vier generische Klassen

Die folgenden Symptom-Klassen sind aus EB-Digital konkret beobachtet, aber **bewusst projekt-agnostisch** formuliert, weil sie aus der Struktur des Regelwerks folgen, nicht aus Eigenheiten des Pilot-Projekts.

### SE-1: Stille Voraussetzungs-Drift

**Phänomen:** Ein Hilfsskript, eine ENV-Variable, ein CLI-Tool oder eine OS-Komponente wird im Verlauf der Entwicklung neu eingeführt — beim Schritt, der das Skript anlegt oder das Tool nutzt — und in der Onboarding-Doku (README „Voraussetzungen", `project-context.md` Setup-Block) **nicht** nachgepflegt. Die neue Voraussetzung ist im Repo wirksam, aber für den nächsten Anwender unsichtbar.

**Mechanismus:** Der Schritt-Verantwortliche denkt: „Ich nutze hier `jq`, das hat doch jeder" oder „Die ENV-Variable `EB_FOO_KEY` ist neu, aber sie steht ja in `.env.example`". Beides ist subjektiv plausibel, beides verletzt die externe Anwender-Perspektive.

**Sichtbarkeits-Latenz:** Tritt erst beim ersten Klon auf einer frischen Maschine auf. Im Worktree des Schritt-Verantwortlichen ist die Voraussetzung längst befriedigt.

**Konkretes Auftreten in EB-Digital:** `jq` wurde in Schritt 1.8 zusammen mit `dev-smoke.sh` eingeführt und in 2.2/2.3/2.4/2.5b/2.6 stillschweigend weiter genutzt. Nirgends als Voraussetzung dokumentiert. Standard-Git-Bash auf Windows liefert kein `jq`. Beim Funktionstest schlug `dev-smoke.sh` sofort beim ersten `jq`-Aufruf fehl — was wie ein Code-Bug aussieht, aber Tool-Drift ist.

### SE-2: Ungeprüfter Onboarding-Pfad

**Phänomen:** Die README beschreibt eine Quick-Start-Sequenz (klonen → Tooling installieren → Setup → Hochfahren → Verifikation). Die Sequenz wird **niemals als Ganzes** gegen einen frischen Klon oder Worktree validiert. Sie wächst stattdessen Schritt-für-Schritt mit, jedes Phase-Ergebnis ergänzt seinen Teil. Lücken, Reihenfolge-Fehler oder gelöschte Voraussetzungen bleiben unsichtbar.

**Mechanismus:** Die Pflege-Trigger der README (im aktuellen Regelwerk §16) reagieren auf **Status**, **Phase**, **Reifegrad**, **Blocker**, **ADRs**. Sie reagieren nicht auf **„kann ein Außenstehender das jetzt von Null bis Hochfahren durchziehen?"**. Niemand wird gezwungen, den Pfad zu prüfen, also prüft ihn niemand.

**Sichtbarkeits-Latenz:** Tritt beim ersten externen Klon auf — ein interner Entwickler, der seinen Worktree pflegt, merkt nichts.

**Konkretes Auftreten in EB-Digital:**

- Quick-Start-Zeile 94 sagt `cp .env.example .env` ohne Hinweis, dass `SECRET_KEY=GENERATE_ME_64_CHAR_RANDOM_TOKEN` und `CHANGE_ME` ersetzt werden müssen, bevor der Backend-Boot funktioniert.
- Quick-Start-Zeile 95 startet das Backend lokal (`uv run python -m eb_digital serve`), **vor** Zeile 99, die die DB im Compose-Container hochfährt. `DATABASE_URL` in `.env.example` zeigt aber auf den Compose-Service-Namen `db:5432`, nicht auf `localhost:5432`. Bei jedem `/api/`-Aufruf nach lokalem Backend-Start ohne vorher hochgefahrenes DB bricht die Verbindung.
- Quick-Start-Zeile 119 ruft `bash scripts/dev-smoke.sh` auf, ohne zu erwähnen, dass das Skript bei wiederholtem Aufruf innerhalb 15 Minuten am Rate-Limit-Counter scheitert (Valkey-Volume persistiert).

Keiner dieser drei Brüche ist absichtlich. Alle drei wären beim ersten realen Klon-Versuch sofort aufgefallen — und genau dieser Versuch ist methodisch nicht vorgesehen.

### SE-3: Implizite Plattform-Annahmen

**Phänomen:** Das Regelwerk und die Projekt-Dokumente nennen Sprachen, Frameworks und Versionen, aber **nicht** die unterstützten Entwickler-Plattformen (Linux/macOS/Windows in welchen Varianten). Plattform-Annahmen sind implizit — der Verantwortliche einer Skript-Änderung prüft seine eigene Plattform und stellt fest „läuft bei mir". Andere Plattformen sind nicht im Methodik-Blick.

**Mechanismus:** Die einzigen Plattform-Aussagen im Regelwerk entstehen reaktiv durch eskalierte Blocker (z. B. macOS-`UF_HIDDEN`-Fall in EB-Digital → `fix-venv-flags.sh` + Doku in `blockers.md`). Plattformen, die noch nicht zu einem Blocker geführt haben, sind in der Methodik unsichtbar. Auch wenn jemand auf Windows entwickelt, ist Windows nirgends ausdrücklich als unterstützte Plattform verankert.

**Sichtbarkeits-Latenz:** Tritt auf, sobald ein Anwender mit einer abweichenden Plattform die Software starten will. Häufig erst beim ersten externen Reviewer oder Teammitglied.

**Konkretes Auftreten in EB-Digital:**

- `scripts/dev-smoke.sh` und `scripts/fix-venv-flags.sh` sind reine Bash-Skripts. Auf Windows ohne Git Bash oder WSL2 läuft das nicht. Nirgends erwähnt.
- `curl` in PowerShell/cmd ist ein Alias auf `Invoke-WebRequest` mit anderer Flag-Konvention; `curl -k` (im Quick-Start) funktioniert dort nicht. Nirgends erwähnt.
- macOS hat einen Sonderfall-Hinweis (Blocker #001), Windows hat keinen.

### SE-4: Hilfsskripts ohne Reifegrad

**Phänomen:** Skripts im `scripts/`-Ordner (Smoke-Tests, Setup-Helfer, Diagnose-Tools) sind weder im Architektur-Dokument geführt noch in der Definition of Done verankert. Sie sind „einfach da" und wachsen ad-hoc — bekommen mit jedem Phase-Schritt neue Checks, neue Aufrufmuster, neue Tool-Abhängigkeiten — ohne dass jemand sie systematisch auf **Reproduzierbarkeit, Idempotenz, Plattform-Tauglichkeit oder Voraussetzungs-Deklaration** prüft.

**Mechanismus:** §15 des Regelwerks („Code-Standards") gilt für „Sprachen" — also Backend- und Frontend-Produktivcode. Bash- oder Python-Hilfsskripts in `scripts/` sind nicht im Standard-Adressat-Kreis. Sie werden weder im Architektur-Dokument als Bestandteile mit Reifegrad markiert noch in der Definition of Done geprüft. Reviewer beim Phase-Abschluss prüfen das Produktivcode-Modul, nicht das begleitende Tooling.

**Sichtbarkeits-Latenz:** Tritt auf, wenn das Skript in einer anderen Umgebung als der Schreib-Umgebung läuft (frischer Worktree, andere OS, mehrfacher Aufruf, paralleler Aufruf, ohne Internet, etc.).

**Konkretes Auftreten in EB-Digital:**

- `scripts/dev-smoke.sh` enthielt einen Bash-Trap-Override-Bug (Zeile 564 überschrieb den globalen Cleanup-EXIT-Trap), der den Compose-Stack nach jedem Lauf laufen ließ — direkt gegen die Header-Spezifikation des Skripts.
- Drei `trap "rm -f $..." RETURN`-Statements auf Top-Level sind **No-Ops** (RETURN feuert nur in Function-Scopes) und produzieren stillen Tempfile-Leak.
- Das Skript ist nicht reproduzierbar in schneller Folge (Valkey-Volume-Persistenz, siehe SE-2).
- Plattform-Tauglichkeit: braucht jq, curl, bash, mktemp, sleep, date, sha-Hash-Generierung — keine dieser Voraussetzungen ist im Skript-Header dokumentiert.

Würde `scripts/dev-smoke.sh` im Architektur-Dokument als `[VORLÄUFIG]`-Bestandteil geführt und bei jedem Touch durch eine reduzierte DoD geprüft (etwa: „Plattform-Matrix angegeben, Voraussetzungen im Header, idempotenter Re-Run getestet"), wären drei der oben genannten Bugs nie entstanden.

---

## 3. Strukturelle Diagnose im aktuellen Regelwerk

Die Wurzeln der vier Symptom-Klassen sind im Regelwerk **lokalisierbar** — sie sind keine generelle Schwäche der Methodik, sondern konkret-benannte Leerstellen.

| Symptom-Klasse                       | Schweigende Regelwerks-Stelle                 | Was dort heute steht                                                                                                                                       | Was dort fehlt                                                                                                                                                                                                                                |
| ------------------------------------ | --------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SE-1** Voraussetzungs-Drift        | §16 README-Pflege                             | Trigger: Status/Phase/Reifegrad/Blocker/ADR/Quick-Start, Verwendung, Architektur                                                                           | Trigger „neue Voraussetzung / neue ENV-Variable / neues CLI-Tool im Setup"                                                                                                                                                                    |
| **SE-2** Ungeprüfter Pfad            | §9 Definition of Done                         | 17 Punkte: Linter, Format, Type-Check, Security, Tests, Coverage, Inline-Doc, betroffene Doku, CHANGELOG, README, TODOs, Suppressions, CI-Pipeline, Commit | Kein Punkt „Onboarding-Pfad funktioniert auf frischem Klon/Worktree, sofern Quick-Start-relevante Änderung"                                                                                                                                   |
| **SE-3** Plattform-Annahmen          | CLAUDE.md gesamt + project-context.md-Vorlage | Keine Aussage zu unterstützten Entwickler-Plattformen                                                                                                      | Pflicht-Abschnitt „Unterstützte Plattformen" mit OS-Matrix (Linux/macOS/Windows-via-Git-Bash/Windows-via-WSL2) und Regel „Skript-Touch löst Plattform-Matrix-Prüfung aus"                                                                     |
| **SE-4** Hilfsskripts ohne Reifegrad | §15 Code-Standards + architecture.md-Vorlage  | §15 zählt Pflichtkategorien für „Sprachen". architecture.md hat Modul-Karte und Reifegrad nur für Backend-/Frontend-/Infra-Module.                         | §15 erweitert um Kategorie „Hilfsskripts/Tooling" mit reduzierten, aber benannten Pflichten (Voraussetzungen, Plattform, Idempotenz, Reproduzierbarkeit). architecture.md erweitert um Abschnitt „Tooling-Inventar" mit Reifegrad pro Skript. |

Daneben hat die Methodik einen weiteren strukturellen Schwachpunkt:

**§5 Autonomiebereich** erlaubt der KI (oder dem Schritt-Verantwortlichen) selbständige „Test-Erstellung und -wartung" und „Bugfixes ohne Architekturwirkung". Skript-Erweiterungen fallen darunter — auch dann, wenn sie neue externe Tool-Voraussetzungen einführen. Heute gibt es keinen Mechanismus, der bei einer solchen Skript-Erweiterung die Doku-Synchronisation erzwingt. Die Skript-Erweiterung kann passieren, ohne dass irgendein Trigger die Voraussetzungs-Liste aktualisiert. **Genau hier entsteht SE-1.**

---

## 4. Warum das ein generisches Risiko ist

Die folgenden vier Argumente sind nicht EB-Digital-spezifisch. Sie folgen aus dem Verhältnis zwischen einem methodisch geführten Entwicklungsprozess und dem realen Lebenszyklus von Software, die jemand zum Laufen bringen soll. Jedes Projekt, das mit dem aktuellen Regelwerks-Stand entwickelt wird, trägt das Risiko.

### 4.1 Asymmetrie zwischen messbar und nicht-messbar

Code-Qualität ist **messbar** — Coverage-Prozent, Linter-Findings, Type-Errors, Security-Treffer. Diese Messbarkeit verankert ihre Disziplin: ein Linter-Treffer bricht das CI-Gate, ein Coverage-Abfall ist im Diff sichtbar, ein Type-Error blockiert den Merge. Es gibt keinen Weg, Code-Qualität schleichend verfallen zu lassen.

Onboarding-Qualität ist **nicht messbar** in derselben Weise. Es gibt keine CI-Metrik „Time to first successful Quick-Start". Eine Voraussetzungs-Drift erzeugt kein rotes Gate. Eine README, die in der Reihenfolge falsch ist, kompiliert nicht und wirft keinen Type-Error. Selbst eine systematische Sammlung „Onboarding-Smell" gibt es nicht — analog zum „Code Smell" wäre es naheliegend, ist aber nirgends etabliert.

Konsequenz: **Ohne expliziten Pflege-Mechanismus drifted Onboarding-Qualität immer ab.** Der natürliche Zustand eines lebenden Projekts ohne Onboarding-DoD ist Drift, nicht Korrektheit.

### 4.2 Sichtbarkeits-Latenz

Code-Bugs zeigen sich beim nächsten Test-Lauf, spätestens beim nächsten CI-Run, in der Regel innerhalb eines Tages. Architektur-Brüche zeigen sich beim nächsten Modul-Touch, spätestens beim nächsten ADR-Review, in der Regel innerhalb von ein bis zwei Wochen.

Onboarding-Bugs zeigen sich **beim ersten externen Anwender**. In den meisten Projekten ist das:

- der zweite Entwickler im Team, der neu dazustößt — typischerweise Wochen oder Monate nach der Einführung des betreffenden Tools
- der Reviewer in einem Audit oder externem Review — typischerweise vor einem Roll-out, also nach Wochen oder Monaten
- der Operations-Verantwortliche, der das System produktiv stellt — typischerweise Monate nach Projektstart
- der erste echte Kunde / Pilot-Anwender in einem internen Tool

Diese Sichtbarkeits-Latenz hat zwei Konsequenzen:

**Erste Konsequenz:** Zum Zeitpunkt der Entdeckung ist die Onboarding-Schuld **dick**. Sie ist nicht einer von acht Punkten, sondern ein bis drei Dutzend kleine Brüche, die sich über alle Phasen verteilt aufaddiert haben. Jeder einzelne ist trivial; in Summe ergeben sie ein „kann nicht gestartet werden"-Erlebnis.

**Zweite Konsequenz:** Die Behebung ist **dis-incentiviert**. Sie ist mechanisch billig (Doku-Edits, Skript-Anpassung), aber strategisch teuer — sie verzögert das, was der Beobachter eigentlich tun wollte (das System nutzen, reviewen, betreiben). Sie wird häufig als „Setup-Friction" abgetan und mit lokalen Workarounds gelöst (Tool-Installation, manuelles Editieren der README, mündliche Onboarding-Tipps von Kollegen). Die strukturelle Wurzel bleibt unberührt.

### 4.3 Wachstumsdynamik: jede Phase ergänzt Schulden, ohne Rückkopplung

Software-Projekte sind monoton in der Voraussetzungs-Akkumulation: jede Phase fügt Tools, ENV-Variablen, Endpunkte, Migrations-Schritte und Setup-Befehle hinzu. Sie entfernt selten welche.

Ohne Pflege-Trigger im Regelwerk wird **jede dieser Hinzufügungen** zur potenziellen Onboarding-Schuld. Die Wachstumsrate skaliert mit der Phasen-Anzahl, nicht mit der Komplexitäts-Wahrnehmung. In einem Projekt mit sieben Phasen, das die ersten zwei sauber durchläuft, ist die Onboarding-Schuld am Ende von Phase 7 typischerweise **drei- bis fünfmal so groß** wie nach Phase 2 — selbst wenn jeder einzelne Schritt nur eine Mini-Schuld erzeugt.

Im Fall EB-Digital: Phase 2 hat **acht** Onboarding-Brüche produziert. Die geplanten Phasen 3–7 enthalten:

- neue ENV-Variablen (TomTom-API-Key, MapTiler-API-Key werden in Phase 6 aktiv)
- neue Hilfsskripts (Resilience-Backup-Restore in Phase 6, Lasttest-Tooling in Phase 7)
- neue Service-Worker-Caches (PWA-Strategie in Phase 6 mit `frontend-betreuer`)
- neuen Onboarding-Pfad für Mandanten (Plattform-Admin-Governance in Phase 7)
- neue Produktiv-Konfiguration (TLS-Zertifikate, Hetzner-VPS-Provisioning in Phase 7)

Eine konservative Hochrechnung: zusätzliche **15–25 Onboarding-Brüche** bis Phase 7, wenn die Methodik unverändert bleibt. Das entspricht einer **Refactor-Phase 7.5** mit geschätzten 6–12 Stunden reiner Doku-/Skript-Aufräum-Arbeit, plus dem indirekten Schaden in Form schlechter ersten Anwendungs-Erfahrungen vor und während dieser Aufräum-Phase.

### 4.4 Refactor-Asymmetrie: Symptom-Fix billig, Wurzel-Fix unattraktiv

Wenn die Schulden sichtbar werden, ist es psychologisch und organisatorisch **wesentlich** einfacher, sie als Symptome zu fixen als an der methodischen Wurzel anzusetzen.

**Symptom-Fix:** „Ich edit-iere die README, ergänze `jq` in den Voraussetzungen, korrigiere die Reihenfolge der Quick-Start-Schritte." Das ist in 15 Minuten gemacht, das CI-Gate bleibt grün, der Commit ist klein.

**Wurzel-Fix:** „Ich erweitere CLAUDE.md um eine neue Pflichtkategorie, ergänze §9 DoD um einen Onboarding-Pfad-Punkt, ergänze §16 README-Pflege um neue Trigger, ergänze die project-context.md-Vorlage um eine Plattform-Matrix, ergänze die architecture.md-Vorlage um ein Tooling-Inventar, und plane die Migration bestehender Projekte auf die erweiterte Methodik." Das ist Tage Arbeit, betrifft alle laufenden Projekte, erfordert Diskussion und Konsens, sieht aus wie „Meta-Arbeit ohne Produkt-Mehrwert".

Die natürliche Dynamik ist: **Symptome werden ein- bis zweimal pro Projekt gefixt, die Wurzel nie**. Das nächste Projekt startet mit demselben Regelwerk und erzeugt dieselben Symptome.

Daraus folgt der wichtigste Punkt dieses Issue:

> **Genau jetzt — wo die Symptome im Pilot-Projekt EB-Digital konkret beobachtet, dokumentiert und verstanden sind — ist der einmalige Zeitpunkt, die Wurzel zu fixen, ohne dass es als „abstrakte Meta-Arbeit" verkauft werden muss. Die nächste Gelegenheit kommt nicht von alleine — sie müsste durch denselben Schmerz im nächsten Projekt erkauft werden.**

---

## 5. Bezug zu etablierten Konzepten

Die in diesem Issue beschriebene Lücke ist nicht neu. Die Software-Engineering-Literatur hat dieselbe Klasse Probleme seit zwei Jahrzehnten unter verschiedenen Namen beschrieben. Das Regelwerk profitiert davon, wenn es seine eigene Erweiterung in dieser Tradition verankert — sowohl methodisch als auch sprachlich.

### 5.1 Walking Skeleton (Alistair Cockburn, „Crystal Clear", 2004)

Cockburn beschreibt das „Walking Skeleton" als „eine winzige End-to-End-Implementierung eines Systems, die zwar trivial ist, aber alle Schichten und Komponenten durchquert". Der Punkt ist nicht der Funktions-Umfang, sondern die **Existenz und Verifikation eines durchgängigen Pfades** — von der Eingabe bis zur Ausgabe, durch alle Build-/Deploy-/Konfigurations-Schichten.

**Bezug zur Lücke:** Ein lauffähiger Quick-Start-Pfad **ist** das Walking Skeleton aus Anwender-Sicht. Wenn ein neuer Anwender ihn nicht durchlaufen kann, existiert das Walking Skeleton aus seiner Sicht nicht — egal wie viel Backend-Code dahinter steckt. Cockburn argumentiert, dass das Walking Skeleton von Anfang an existieren und mit jeder Iteration **mit-validiert** werden muss, nicht erst „am Ende, wenn das System fertig ist". Das aktuelle Regelwerk hat diese Disziplin für die internen System-Schichten (Tests, CI, Smoke), aber nicht für den anwender-seitigen Onboarding-Pfad.

### 5.2 12-Factor App (Adam Wiggins, Heroku, 2011)

Faktor 3: „Store config in the environment." Faktor 5: „Strictly separate build, release, and run stages." Faktor 10: „Keep development, staging, and production as similar as possible."

**Bezug zur Lücke:** Faktor 10 ist die explizite Forderung, dass ein neuer Entwickler die Software in seiner Dev-Umgebung mit minimaler Friction starten können muss — als Vorbedingung für die Plausibilität jedes Produktiv-Deployments. Wenn die Dev-Umgebung nicht reproduzierbar startbar ist, ist die Produktiv-Umgebung es auch nicht (sondern hat zufällig anders konfiguriert, was nicht dasselbe ist wie „korrekt"). Die in EB-Digital beobachteten Onboarding-Brüche (SECRET_KEY-Platzhalter, DATABASE_URL-Pfad, jq-Voraussetzung, Smoke-Reproduzierbarkeit) sind alle direkte Verletzungen von Faktor 10.

### 5.3 Definition of Done (Scrum / Agile-Tradition)

Die Definition of Done ist im Scrum-Modell die **explizite, geteilte Liste der Kriterien, die jeder „fertige" Arbeitsgegenstand erfüllen muss**. Sie ist projekt-spezifisch, aber methodisch verankert: jedes Team formuliert sie, hält sie sichtbar und wendet sie konsequent an.

Etablierte DoD-Sammlungen umfassen typischerweise drei Klassen Kriterien:

1. **Funktional:** Code geschrieben, Tests grün, Reviewer-Freigabe
2. **Qualität:** Coverage, Lint, Security, Performance
3. **Operational:** Deploybar, Dokumentiert, **Für Stakeholder zugänglich**

Die dritte Klasse — operational — ist in vielen Scrum-Teams Standard. Sie umfasst typischerweise „Doku aktualisiert", „Demo-fähig", „Onboarding-Pfad durchläuft", „Operations-Runbook ergänzt", „Monitoring konfiguriert". Im aktuellen CLAUDE.md-§9 sind die Klassen 1 und 2 sehr detailliert (17 Punkte), Klasse 3 ist nur partiell vertreten (CHANGELOG, README-Sync, Inline-Doc) und enthält **keinen** „Onboarding-Pfad durchläuft"-Punkt.

**Bezug zur Lücke:** Die etablierte DoD-Tradition kennt den Punkt seit den späten 1990ern. Es ist nicht eine Innovation, ihn aufzunehmen — es ist die Schließung einer auffälligen Auslassung gegen den Stand der Praxis.

### 5.4 Time to Hello World (Developer-Experience-Metrik)

Die DX-Literatur (Forsgren/Humble/Kim, „Accelerate", 2018; Stripe/Twilio Developer-Experience-Studien 2019–2024) führt **„Time to Hello World"** als zentrale Metrik: wie lange braucht ein neuer Entwickler vom ersten Kontakt mit dem Repo bis zum ersten erfolgreichen Run? Werte unter 30 Minuten gelten als ausgezeichnet, über 4 Stunden als kritisch.

**Bezug zur Lücke:** Es gibt keinen direkten Mess-Mechanismus für TtHW, aber es gibt einen sehr guten Proxy: **kann jemand, der das Projekt zum ersten Mal sieht, dem Quick-Start in der README ohne Rückfragen folgen und am Ende ein laufendes System haben?** Wenn die Antwort „im Prinzip ja, aber..." lautet, ist die TtHW kritisch. Wenn die Antwort „ja, in 30 Minuten" lautet, ist sie ausgezeichnet. Das aktuelle CLAUDE.md hat keinen Mechanismus, diese Frage zu stellen, geschweige denn zu beantworten.

### 5.5 Tests-as-Documentation

Eine im Open-Source-Ökosystem etablierte Disziplin: **Smoke-Tests sind ausführbare Spezifikationen der Setup- und Betriebsanforderungen**. Wenn der Smoke-Test ohne `jq` nicht läuft, ist `jq` faktisch eine Setup-Voraussetzung — egal ob sie irgendwo dokumentiert ist. Wenn der Smoke-Test ohne Volume-Reset nicht reproduzierbar ist, ist Volume-Reset faktisch eine Re-Run-Voraussetzung — egal ob es im Header steht.

**Bezug zur Lücke:** Ein qualitäts-gepflegtes Smoke-Skript ist die **billigste** Form, Onboarding-Tauglichkeit zu prüfen — es prüft sich selbst, sobald es läuft. Aber das setzt voraus, dass das Skript **selbst** als qualitäts-relevantes Artefakt geführt wird, mit Reifegrad, Plattform-Matrix und expliziten Voraussetzungen. Genau das fehlt in der aktuellen Methodik (SE-4).

### 5.6 Test the Test — die exakte Parallele zu ADR-015

Im EB-Digital-Projekt wurde am 2026-05-15 in Schritt 2.5b ein reaktiver ADR (ADR-015) angelegt, weil ein Lifecycle-Bug in der `get_db_session()`-Dependency in den bestehenden Tests durch `dependency_overrides`-Stubs **maskiert** war. Die Tests waren grün, aber sie prüften die Dependency selbst nicht — sie prüften nur ihre Stub-Ersetzung. Die methodische Lehre (Regel-018): für jede Resource-Dependency braucht es einen Lifecycle-Test, der die echte Dependency-Funktion gegen einen Counter-Stub für die Ressource fährt, plus mindestens eine Real-Smoke-Probe gegen die echte Ressource.

**Die exakte Parallele:** Die README ist ein „Test" für den Onboarding-Pfad. Die Tests (Pre-Commit, Pytest, Vitest, CI-Pipeline) prüfen den Onboarding-Pfad nicht. Sie sind grün, aber sie prüfen ihren eigenen Code, nicht den Pfad, den ein Außenstehender durchläuft. Die README ist faktisch nicht getestet, sondern stub-ersetzt durch „im internen Worktree funktioniert es ja".

Die methodische Lehre für die Onboarding-Qualität ist analog: es braucht eine **Real-Smoke-Probe gegen die echte Anwender-Umgebung** — einen frischen Klon oder Worktree, der den dokumentierten Pfad durchläuft. Genau das schlägt dieses Issue als neue DoD-Bedingung vor.

Diese Parallele ist nicht zufällig. Die Klasse Bug („grüner Test, der Falsches prüft") ist dieselbe, ob das geprüfte Objekt eine Code-Dependency oder eine README ist.

---

## 6. Anti-Pattern: Symptom-Pflege ohne Wurzel-Pflege

Der häufigste Umgang mit den vier Symptom-Klassen in der Praxis lautet:

1. Symptom tritt auf (Anwender meldet „kann nicht starten").
2. Schmerz wird verortet als „Doku-Fehler" oder „Setup-Friction".
3. Eine README-Zeile wird ergänzt, ein Skript-Header wird klarer, ein Voraussetzungs-Eintrag wird hinzugefügt.
4. Symptom ist weg, Schmerz vergessen.
5. Sechs Monate später: dasselbe Symptom in einer neuen Form (anderes Tool, andere ENV, anderer Skript-Lauf) tritt auf.
6. → zurück zu Schritt 1.

Dieses Muster ist gut dokumentiert in der technischen Schulden-Literatur (Cunningham 1992, Fowler 2003, Sterling 2010 zur „Technical Debt Quadrant"-Klassifizierung). Es ist die **reaktive Variante** des Wartungs-Modus, im Gegensatz zur **antizipativen Variante**, in der die Wurzel adressiert wird.

Die antizipative Variante ist im aktuellen CLAUDE.md für **Code-Qualität** vollständig umgesetzt (DoD §9, Pflichtkategorien §15, Pre-Commit/CI-Gates) — sie ist methodisch verankert, nicht nur erinnert. Für **Onboarding-Qualität** ist sie nicht umgesetzt.

Die Empfehlung dieses Issue lautet: **Verankerung in der Methodik auf demselben Niveau, das Code-Qualität bereits hat.** Nicht „mehr Disziplin von den Anwendern fordern", sondern „Trigger und Pflichten so im Regelwerk verankern, dass die Disziplin entsteht, ohne dass jemand aktiv daran denken muss".

---

## 7. Konkrete Regelwerks-Empfehlungen (Übersicht)

Detail-Patches stehen im Begleit-Dokument [`regelwerks-patches.md`](regelwerks-patches.md). Diese Übersicht zeigt die strategische Auflage:

| #   | Patch                                                                                                                                                                                                                                                                                                                                                                                                                    | Adressiert                | Eingriff in                     |
| --- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------------- | ------------------------------- |
| P1  | **§9 DoD erweitern** um Punkt „Onboarding-Pfad-Verifikation: bei Quick-Start-relevanten Änderungen wurde der dokumentierte Pfad gegen frischen Klon/Worktree validiert (oder begründet als nicht-relevant markiert)"                                                                                                                                                                                                     | SE-2                      | CLAUDE.md                       |
| P2  | **§15 Code-Standards erweitern** um neue Pflichtkategorie „Hilfsskripts (`scripts/`)" mit reduzierten, aber explizit benannten Pflichten: Voraussetzungs-Header, Plattform-Matrix, Idempotenz-Aussage, Reproduzierbarkeit-Aussage. Für Skripts ab einer bestimmten Komplexitäts-Schwelle (z. B. >100 Zeilen oder zwei Subkommandos): zusätzlich Shell-Linter (`shellcheck`) im Pre-Commit.                               | SE-4                      | CLAUDE.md                       |
| P3  | **§16 README-Pflege erweitern** um zwei neue Trigger: (a) „neue oder geänderte Voraussetzung / ENV-Variable / Quick-Start-Schritt → README-Voraussetzungen-Block aktualisieren im selben Commit"; (b) „Phasenende → Onboarding-Pfad-Re-Validation pflichtig"                                                                                                                                                             | SE-1 + SE-2               | CLAUDE.md                       |
| P4  | **Neuer §17 „Onboarding-Pfad-Pflege"** als eigenständige Disziplin: was zählt als Onboarding-Pfad, was zählt als Quick-Start-relevante Änderung, wie wird validiert (frischer Klon, frischer Worktree, frischer Container, je nach Projekt-Klasse), wer ist Ziel-Anwender (Dev/Reviewer/Operations)                                                                                                                      | SE-1 + SE-2 + SE-3 + SE-4 | CLAUDE.md                       |
| P5  | **`project-context.md`-Vorlage erweitern** um Abschnitt „Unterstützte Entwickler-Plattformen" mit OS-Matrix-Tabelle (Linux-Distros / macOS / Windows-mit-Git-Bash / Windows-mit-WSL2) und Spalten je Aspekt (Backend, Frontend, Hilfsskripts, Dokumentations-Tools)                                                                                                                                                      | SE-3                      | CLAUDE.md §3 indirekt (Vorlage) |
| P6  | **`architecture.md`-Vorlage erweitern** um Abschnitt „Tooling-Inventar mit Reifegrad" — jedes Skript in `scripts/` ist ein Bestandteil mit `[VORLÄUFIG]/[BELASTBAR]`-Marker, einer Plattform-Matrix-Spalte und einer Liste der externen Voraussetzungen                                                                                                                                                                  | SE-4                      | CLAUDE.md §3 indirekt (Vorlage) |
| P7  | **§3 Dokumenten-Index erweitern** um optionales `docs/onboarding-runbook.md` als **Pflicht ab Klasse M**. Ab Klasse G aufteilbar nach Ziel-Rolle (Dev-Runbook / Reviewer-Runbook / Operations-Runbook). Das Runbook ist die ausführliche, getestete End-to-End-Anleitung — die README bleibt das **Statusbild**, das Runbook ist die **Bedienungs-Anleitung**                                                            | SE-2 (vertieft)           | CLAUDE.md                       |
| P8  | **§5 Autonomiebereich präzisieren**: Skript-Erweiterungen, die neue externe Voraussetzungen einführen (CLI-Tool, ENV-Variable, OS-Komponente), verlassen den Autonomiebereich und brauchen Doku-Update im selben Commit (Pflicht, nicht Wahl). Pre-Commit-Hook erkennt das Muster — wenn `scripts/*.sh` geändert UND README/.env.example nicht im selben Commit, dann Warning (nicht harter Block, weil False-Positives) | SE-1 (strukturell)        | CLAUDE.md                       |

Diese acht Patches sind **unabhängig** — jeder kann einzeln freigegeben, abgelehnt oder modifiziert werden. Eine teilweise Annahme (z. B. P1+P3+P5) wäre bereits eine signifikante Verbesserung gegenüber dem aktuellen Stand.

**Reihenfolge der Wirkung:** P1 und P3 sind die mit dem größten Sofort-Effekt (sie schließen SE-1 und einen Teil von SE-2 in jedem laufenden Projekt). P4 und P7 sind die mit der größten Tiefen-Wirkung (sie verankern die Disziplin als eigenständige Praxis). P2 und P6 sind die mit dem größten Folgen-Effekt (sie strukturieren das Tooling für die nächsten Jahre).

---

## 8. Erwartete Wirkung pro künftiges Projekt

Eine quantifizierte Schätzung pro mittelgroßes Projekt (Klasse G nach CLAUDE.md §1B), basierend auf der EB-Digital-Fallstudie:

| Zeitpunkt                                            | Status ohne Patches                                  | Status mit Patches                              | Differenz                                                    |
| ---------------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------ |
| Phasen-Übergang 2→3                                  | 6–10 Onboarding-Brüche kumuliert                     | 0–2 (Restquote durch nicht-erfasste Edge-Cases) | 4–10 vermieden                                               |
| Phasen-Übergang 4→5                                  | 12–20 Brüche kumuliert                               | 2–5                                             | 10–18 vermieden                                              |
| Vor Produktiv-Start                                  | 20–40 Brüche kumuliert, Refactor-Phase nötig         | 4–8 Brüche, einzelne Fixes ohne Phasen-Eingriff | Refactor-Phase entfällt (geschätzt 6–12 h gespart)           |
| Externe Übergabe (neuer Entwickler, Audit, Roll-out) | TtHW > 2 h, mündliche Onboarding-Unterstützung nötig | TtHW < 30 min, Self-Service-Onboarding          | Onboarding-Aufwand pro neuem Stakeholder von ~4 h auf ~0,5 h |

Diese Schätzung ist konservativ. In Projekten mit mehr Stakeholdern, mehr Plattformen oder höherer Compliance-Anforderung (Audit-Pflicht, Penetration-Test, Roll-out an mehrere Mandanten) sind die Einsparungen entsprechend höher, weil jeder zusätzliche externe Anwender den Schaden multipliziert.

**Indirekte Wirkungen, nicht in der Tabelle:**

- Bessere erste Anwender-Erfahrung → höhere Akzeptanz, niedrigere Eskalations-Quote
- Reproduzierbare Smoke-Läufe → CI-Tauglichkeit der Smoke-Tests (heute oft nicht in CI integriert, weil nicht idempotent)
- Plattform-Matrix-Bewusstsein → Frühe Aufdeckung von Plattform-spezifischen Bugs (vor Roll-out, nicht im Roll-out)
- Methodische Klarheit für Tooling → Skript-Wildwuchs wird vermieden, Hilfsskripts werden Architektur-Bestandteile mit Lebenszyklus

---

## 9. Out-of-Scope

Die folgenden Punkte sind **bewusst nicht** Teil der Empfehlung:

- **Marketing-Doku (Landing-Page, Produkt-Website):** außerhalb der Methodik-Reichweite, eigener Disziplin-Kreis.
- **Tutorial-Inhalte / Lerninhalte für Anwender:** README-Aufgabe ist Quick-Start, Architektur-Überblick, Status — nicht „lerne, wie das System funktioniert". Tutorials sind separate Artefakte.
- **API-Dokumentation (OpenAPI, JSDoc-Export):** technische Schnittstellen-Doku ist eigene Disziplin und im aktuellen Regelwerk durch Inline-Doc-Pflicht abgedeckt.
- **Internationalisierung der Doku (mehrsprachig):** nicht Teil des Methodik-Problems.
- **CI-Auto-Run-Setup für Quick-Start-Validation:** Vorschlag P4 verankert die Pflicht, ein konkreter CI-Auto-Run wäre eine Folge-Optimierung, die jedes Projekt individuell entscheiden kann. Es gibt nicht-CI-basierte Wege (lokales Re-Klonen, Worktree-basierte Validation), die manche Projekte bevorzugen werden.

---

## 10. Diskussions-Punkte für Methodik-Pflege

Folgende Punkte sind in der Patch-Ausarbeitung noch offen und benötigen eine Entscheidung des Methodik-Pflegers:

### D1 — Reichweite der „Quick-Start-relevanten Änderung"

P1 (DoD) sagt: „bei Quick-Start-relevanten Änderungen". Wer definiert „relevant"? Eine konservative Lesart: jede Änderung an README, `.env.example`, `scripts/`, `docker-compose.yml`, oder den Top-Level-Build-Files. Eine großzügige Lesart: jede Änderung am Backend-`/api/`-Pfad (potentiell neuer Endpunkt → Onboarding-Demo-Pfad könnte ihn nutzen). Empfehlung: konservative Lesart als Default mit der Option, in `project-context.md` projekt-spezifisch zu erweitern.

### D2 — Pflicht-Trigger für die Onboarding-Pfad-Re-Validation

P3 (README-Pflege) sagt: „Phasenende → Onboarding-Pfad-Re-Validation pflichtig". Wann genau? Vorschlag: bei jedem Phasen-Abschluss-Schritt (in EB-Digital wäre das z. B. der Schritt 2.7). Wer validiert? Vorschlag: derjenige, der den Phasen-Abschluss-Schritt durchführt — mit der reduzierten Form „neuer Worktree, dokumentierter Pfad ohne Abweichung durchlaufen" (eine harte Klon-auf-frischer-VM-Validation wäre Overhead).

### D3 — Tooling-Reifegrad-Skala

P6 (Tooling-Inventar) übernimmt die `[VORLÄUFIG]/[BELASTBAR]`-Skala aus dem Architektur-Reifegrad. Aber Hilfsskripts haben oft keinen klassischen „Validierungs-durch-Implementierung"-Pfad — sie sind klein, sie funktionieren oder funktionieren nicht. Vorschlag: vereinfachte Skala `[ROH]` (frisch geschrieben, keine systematische Prüfung) / `[GEHÄRTET]` (Plattform-Matrix angegeben, Voraussetzungen dokumentiert, Idempotenz bewiesen, ggf. shellcheck-grün). Alternative: dieselbe Skala wie Architektur, aber mit eigenen Beförderungskriterien.

### D4 — Onboarding-Runbook-Pflicht ab welcher Klasse

P7 (Onboarding-Runbook) schlägt „Pflicht ab Klasse M" vor. Eine Alternative wäre „Pflicht ab Klasse G, in Klasse M optional aber empfohlen". Diskussions-Punkt: ab welcher Komplexität ist ein separates Runbook nötig (vs. README reicht aus)? Empirisch in der Industrie: ab ca. 2 Sprachen + 3 Services + 1 externem API-Provider.

### D5 — Migration bestehender Projekte

Wenn die Patches angenommen werden, wie wird ein laufendes Projekt (wie EB-Digital) migriert? Vorschlag: keine retroaktive Validations-Pflicht für vergangene Phasen, aber eine **einmalige Migrations-Phase** „Onboarding-Pfad-Stabilisierung", in der die akkumulierten Schulden gesammelt geschlossen werden. Danach gelten die neuen Trigger ab nächstem Phasen-Schritt. Diese Migrations-Phase ist in EB-Digital faktisch die aktuelle Aktivität, in deren Verlauf dieses Issue entstanden ist.

### D6 — CI-Integration der Validation

P1 macht Onboarding-Validation zur DoD-Pflicht, aber nicht zur CI-Pflicht (kein automatisierter Gate). Diskussions-Punkt: soll es einen optionalen CI-Job geben („Onboarding-Smoke" — frischer Container, klonen, Quick-Start durchlaufen)? Vorteil: Drift wird sichtbar zwischen den Phasen, nicht erst beim Phasen-Abschluss. Nachteil: technisch nicht-trivial (frischer Container mit allen OS-Voraussetzungen pro CI-Run), kostet CI-Minuten. Empfehlung: nicht Pflicht, aber als Vorlagen-Snippet in der `.github/workflows/`-Vorlage verfügbar.

---

## 11. Anhang: Fallstudie EB-Digital — alle acht Symptome mit Regelwerks-Wurzel

| #     | Symptom (konkret)                                                                                       | Symptom-Klasse                                      | Regelwerks-Wurzel                                                    | Patch der schließt                         | Status in EB-Digital                                          |
| ----- | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------- | -------------------------------------------------------------------- | ------------------------------------------ | ------------------------------------------------------------- |
| 1     | `jq` fehlt in Voraussetzungen — `dev-smoke.sh` läuft nicht                                              | SE-1 (Voraussetzungs-Drift)                         | §16 ohne Trigger für neue Tool-Voraussetzung                         | P3 + P5                                    | Tool installiert (winget), Doku-Fix offen                     |
| 2     | `SECRET_KEY` / `CHANGE_ME` Platzhalter im `.env.example`, README sagt nicht „ersetzen"                  | SE-2 (Ungeprüfter Pfad)                             | §9 DoD ohne Onboarding-Pfad-Punkt                                    | P1 + P7                                    | Doku-Fix offen                                                |
| 3     | `DATABASE_URL=...@db:5432/...` zeigt auf Compose-Service, README startet aber Backend lokal vor Compose | SE-2 (Ungeprüfter Pfad)                             | §9 DoD ohne Onboarding-Pfad-Punkt                                    | P1 + P7                                    | Doku-Fix offen                                                |
| 4     | Bash auf Windows nicht erwähnt — `bash scripts/...` schlägt in cmd/PowerShell fehl                      | SE-3 (Plattform-Annahmen)                           | Kein Plattform-Matrix-Abschnitt in project-context.md-Vorlage        | P5                                         | Doku-Fix offen                                                |
| 5     | Compose-Volumes persistieren, Re-Run von `dev-smoke.sh` schlägt am Rate-Limit-Counter fehl              | SE-4 (Hilfsskripts ohne Reifegrad)                  | §15 ohne Pflichten für Hilfsskripts (Idempotenz, Reproduzierbarkeit) | P2 + P6                                    | Skript-Fix optional, Doku-Hinweis offen                       |
| 6     | `pnpm exec vitest` ohne vorheriges `svelte-kit sync` schlägt im frischen Worktree fehl                  | situativ — README sagt korrekten Pfad (`pnpm test`) | —                                                                    | —                                          | nicht zu fixen                                                |
| 7     | Pre-Commit-Erstlauf dauert mehrere Minuten — nicht in README erwähnt                                    | situativ — universell                               | —                                                                    | —                                          | optional Doku-Hinweis                                         |
| 8     | `curl` in PowerShell ist Alias auf `Invoke-WebRequest` mit anderer Flag-Konvention                      | SE-3 (Plattform-Annahmen)                           | wie #4                                                               | P5                                         | Doku-Fix offen                                                |
| extra | **scripts/dev-smoke.sh EXIT-Trap-Override-Bug** (Zeile 564 überschrieb cleanup)                         | SE-4 (Hilfsskripts ohne Reifegrad)                  | §15 ohne Lint-/Review-Pflicht für scripts/                           | P2 (shellcheck-Pflicht hätte ihn gefunden) | gefixt in Commit 8ac20ea                                      |
| extra | **scripts/dev-smoke.sh: drei `trap … RETURN`-No-Ops auf Top-Level** (Tempfile-Leak)                     | SE-4 (Hilfsskripts ohne Reifegrad)                  | wie oben                                                             | P2                                         | offen — orthogonaler Bug, nicht im Funktionstest-Scope gefixt |

---

## Schlussbemerkung

Die Methodik-Lücke, die dieses Issue beschreibt, ist nicht auf irgendeine Weise „neu entdeckt" — sie ist im Software-Engineering-Diskurs seit zwei Jahrzehnten bekannt und unter mehreren Begriffen (Walking Skeleton, 12-Factor, DoD, TtHW, Tests-as-Documentation, Test-the-Test) ausführlich behandelt. Was neu ist, ist die konkrete Lokalisierung im CLAUDE.md-Regelwerk und der präzise Vorschlag, wie sie geschlossen werden kann, ohne die bestehende Struktur zu beschädigen.

Die Patches sind **inkrementell** — sie ergänzen, sie löschen nicht. Bestehende Projekte können sie schrittweise übernehmen. Die Beförderung der Methodik kostet einmalig Doku-Arbeit, danach amortisiert sie sich pro Projekt mehrfach.

Das **eigentliche Risiko** dieses Issue ist nicht, dass die Patches abgelehnt werden. Es ist, dass die Diskussion endet mit „spannend, lass uns das im nächsten Projekt mal prüfen" — und das nächste Projekt dieselben acht Symptome reproduziert, weil die Regelwerks-Stellen unverändert bleiben. Der Zeitpunkt, an dem diese Diskussion mit konkretem Anker geführt werden kann, ist **jetzt**.
