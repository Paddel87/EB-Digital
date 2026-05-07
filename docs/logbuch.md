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

### YYYY-MM-DD HH:MM – [SESSIONENDE]

- **Session-Dauer:** [z. B. „2h 15min" oder „kurze Session"]
- **Bearbeitet:** [Welche Fahrplan-Schritte wurden in dieser Session berührt; Status-Änderungen]
- **Erreicht:** [Was ist am Ende der Session konkret fertig oder vorangeschritten]
- **Offen geblieben:** [Was war angefangen, ist aber nicht abgeschlossen; mit Stand]
- **Nächster Schritt:** [Was zu Beginn der nächsten Session aufgegriffen wird – konkret]
- **Stimmung / Beobachtung:** [optional: was lief gut, was zäh, woran erinnern für nächstes Mal]

### YYYY-MM-DD HH:MM – [PROBLEM-GELÖST]

- **Kontext:** [In welchem Schritt / Modul / Datei trat das Problem auf]
- **Symptom:** [Was war zu sehen, welche Fehlermeldung, welches Verhalten]
- **Ursache:** [Was war der eigentliche Grund]
- **Lösung:** [Was wurde geändert, um es zu beheben]
- **Aufwand:** [grobe Zeitangabe, z. B. „10 Min", „1h", „halber Tag"]
- **Lerneffekt:** [optional: was nehmen wir daraus mit, was würden wir nächstes Mal anders machen]
- **Wiederkehrgefahr:** [optional: kann das Problem in ähnlicher Form an anderer Stelle auftauchen?]

### YYYY-MM-DD HH:MM – [PROBLEM-OFFEN → BLOCKER]

- **Kontext:** [...]
- **Symptom:** [...]
- **Versuche bisher:** [...]
- **Eskaliert nach:** `blockers.md` Eintrag #NNN

[Eintrag wird ergänzt, sobald der Blocker gelöst ist – als „[BLOCKER-AUFGELÖST]"-Eintrag mit Verweis hierhin.]

### YYYY-MM-DD HH:MM – [SESSIONSTART]

- **Letzter Stand:** [aufgenommen aus letztem SESSIONENDE-Eintrag]
- **Geplant für diese Session:** [welche Schritte sollen bearbeitet werden]
- **Vorabprüfung:** [ist `[BELASTBAR]`-Architektur für die geplanten UMSETZUNG-Schritte gegeben? Sind Eingangskriterien erfüllt?]
- **Modus / Werkzeug:** [Claude Code / normaler Chat, falls relevant]

### YYYY-MM-DD HH:MM – [BEOBACHTUNG]

[Freie Notiz, wenn etwas auffällt, das kein Problem und keine Entscheidung ist, aber später nützlich sein könnte.
Z. B. „Build-Zeit hat sich seit letzter Woche verdreifacht, könnte später relevant werden",
„Bibliothek X hat ein neues Major-Release, prüfen ob Migration in nächster STABILISIERUNG nötig",
„Test-Suite läuft auf neuer Maschine 30 % schneller, eventuell Threshold-Werte überdenken"]

### YYYY-MM-DD HH:MM – [REIFEGRAD-WECHSEL]

- **Bestandteil:** [Modul / Schnittstelle / NFR aus `architecture.md`]
- **Wechsel:** [VORLÄUFIG → BELASTBAR | BELASTBAR → VORLÄUFIG | OFFEN → VORLÄUFIG | etc.]
- **Auslöser:** [welcher Schritt, welche Validierung, welcher ADR]
- **Datum in `architecture.md` Abschnitt 9 nachgetragen:** [ja/nein]

### YYYY-MM-DD HH:MM – [ADR-ANGELEGT]

- **ADR:** [Nummer und Kurztitel]
- **Tag:** [STRATEGISCH | OPERATIV | REAKTIV | ERKENNTNIS]
- **Auslöser:** [warum kam diese Entscheidung jetzt auf]

[Eintrag dient als chronologische Spur; der eigentliche Inhalt steht in `decisions.md`.]

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

---

**Initialisierungshinweis (erste Session nach Projektanlage):**

- Beispiel-Einträge oben sind Format-Demonstration und werden bei Initialisierung **entfernt**.
- Erster echter Eintrag entsteht zu Beginn der ersten regulären Session nach Modus-2-Abschluss: `[SESSIONSTART]` mit Verweis auf den Initialisierungs-Commit.
- **Strukturwahl** richtet sich nach Klasse (siehe `CLAUDE.md` Abschnitt 1B):
  - **Klasse K (Klein):** Reduzierte Form – `[SESSIONSTART]`/`[SESSIONENDE]` auf Pflicht reduziert, andere Typen optional. Archivierung selten nötig.
  - **Klasse M (Mittel) und G (Groß):** Volle Form wie oben.
  - **Klasse V (Verteilt-Groß):** Bei stark service-getrennter Arbeit ggf. service-spezifische Logbücher (`logbuch-<service>.md`) zusätzlich. `logbuch.md` bleibt als Master mit Sessionrahmen und service-übergreifenden Ereignissen.
- KI legt Einträge **proaktiv und ungefragt** an. „Empfohlen" in Frage 3 heißt nicht „selten oder nur bei Bedarf" – es heißt „ohne dass der Mensch jedes Mal auffordern muss".
