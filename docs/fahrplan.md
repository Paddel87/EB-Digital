# Fahrplan

<!-- Zentrales Arbeitsdokument. Wird vor jeder Änderung gelesen (CLAUDE.md Abschnitt 2)
     und nach jedem Arbeitsschritt sowie zu Sessionende aktualisiert (Abschnitt 12).
     Phasen sind nach Typ klassifiziert (Erkundung / Umsetzung / Stabilisierung),
     weil iterative Entwicklung unterschiedliche Erfolgskriterien pro Phasentyp braucht. -->

## Aktueller Stand

- **Stand vom:** 2026-05-07
- **Laufende Phase:** Modus 2 – Initialisierung (Vorlagen-Befüllung gemäß `CLAUDE.md` Abschnitt 1A)
- **Phasentyp:** INITIALISIERUNG
- **Aktiver Schritt:** keiner – Klärungs-Session der offenen Grundsatzfragen aus `project-context.md` Abschnitt 11 abgeschlossen
- **Nächster Schritt:** Modus-2-Schritt 4 – `architecture.md` mit den in Schublade 1 geklärten Entscheidungen (Fragen A–F, Stand 2026-05-07) als Reifegrad-Hypothesen befüllen. Klassifikations-Bestätigung (Stufe 2) anhand des Architektur-Grobschnitts; bei Abweichung von Klasse G zurück zu Stufe 1.
- **Offene STOPP-Situationen:** keine.

**Hinweis:** Die regulären Phasenfelder dieses Dokuments (Phasen 1, 2, …) sind noch Vorlagen-Platzhalter. Sie werden in Modus-2-Schritt 6 mit den Phasen aus dem geklärten Konzept befüllt, einschließlich der Schublade-2-ERKUNDUNG-Spikes (G–M) und Schublade-3-Roadmap-Meilensteine (N/O/P) – Detail-Skizzen siehe Logbuch-Eintrag 2026-05-07 16:35.

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

## Aktuelle Phasen

### Phase 1: [Phasenname] – Typ: [ERKUNDUNG | UMSETZUNG | STABILISIERUNG]

**Ziel:** [was am Ende dieser Phase erreicht ist – messbar, phasentyp-passend]

**Abschlusskriterium:** [woran die Phase als abgeschlossen erkannt wird]

**Reifegrad-Erwartung am Phasenende:** [welche Architektur-Bestandteile sollen welchen Reifegrad erreicht haben]

#### 1.1: [Kurztitel]

- **Status:** [...]
- **Phasentyp-Kontext:** [...]
- **Schritt-Art (nur ERKUNDUNG):** [...]
- **Zeitbox (nur ERKUNDUNG):** [...]
- **Abhängigkeiten:** [...]
- **Freigabepflichtig:** [...]
- **Eingangskriterien:** [...]
- **Zu tun:** [...]
- **Akzeptanzkriterien:** [...]
- **Betroffene Module:** [...]
- **Reifegrad-Wirkung:** [...]
- **Artefakte:** [...]
- **Notizen:** [...]

#### 1.2: [...]

[...]

### Phase 2: [Phasenname] – Typ: [...]

[...]

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

[Wenn Schritte unabhängig voneinander sind und parallel bearbeitbar wären,
hier notieren. Hilft bei Session-Planung.]

- Schritte **ohne Abhängigkeiten zueinander**: [Liste]
- Schritte **mit gemeinsamen Modulen** (Konfliktgefahr): [Liste]

## Replanning-Historie

[Wenn der Fahrplan umstrukturiert wurde: kurzer Eintrag mit Datum und Grund.
Nicht die einzelnen Schrittänderungen, sondern strukturelle Replanning-Entscheidungen.
Diese sind freigabepflichtig.]

- [YYYY-MM-DD] – [Kurze Beschreibung des Replanning, ADR-Referenz]

## Archiv / abgeschlossene Phasen

[Ältere abgeschlossene Arbeit mit Abschlussdatum.
Bei >500 Zeilen nach `docs/archiv/fahrplan-YYYY-MM.md` auslagern.]

---

**Initialisierungshinweis (erste Session nach Projektanlage):**

- Phasen aus dem Projektvorhaben ableiten und benennen.
- **Phasentyp je Phase festlegen.** Typische Sequenz: ERKUNDUNG (Architektur klären) → UMSETZUNG (Features bauen) → STABILISIERUNG (härten) → UMSETZUNG (nächste Features) → STABILISIERUNG → … Reine UMSETZUNG-Sequenzen sind erlaubt, wenn die Architektur am Phasenstart `[BELASTBAR]` ist; reine ERKUNDUNG-Sequenzen sind selten und sollten begründet werden.
- Erste Phase mit konkreten Schritten füllen; spätere Phasen können gröber sein und werden im Verlauf verfeinert.
- **Strukturwahl** (flach vs. mit Phasen, ein Dokument vs. Master-Index mit Teil-Fahrplänen) richtet sich nach der Projektgrößen-Klassifikation in `CLAUDE.md` Abschnitt 1B. Default pro Klasse:
  - **Klasse K (Klein):** Phasenstruktur entfällt, flache Schrittliste, Phasentyp pro Schritt notieren.
  - **Klasse M (Mittel):** Phasenstruktur, 3–5 Phasen.
  - **Klasse G (Groß):** Phasenstruktur, 5–7 Phasen, ggf. Teil-Fahrpläne pro Modul unter `docs/fahrplan-<modul>.md`.
  - **Klasse V (Verteilt-Groß):** Master-Fahrplan als Index, Pflicht-Teil-Fahrpläne pro Service unter `docs/fahrplan-<service>.md`.
- Das Schritt-Format ist **nicht optional** – jeder Schritt enthält alle Felder.
- Klassifikations- und Anpassungsentscheidung in `decisions.md` als ADR-001 festhalten.
