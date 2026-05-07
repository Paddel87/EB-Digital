# Blockers

<!-- Ungelöste Probleme und gescheiterte Ansätze.
     Wird befüllt, wenn ein Arbeitsschritt nach drei Versuchen nicht gelöst werden konnte
     (CLAUDE.md Abschnitt 10). Gelöste Einträge wandern in den Archiv-Abschnitt. -->

## Blocker-Erkennung (vor dem Dreifach-Versuch)

Ein Problem ist **sofort** als Blocker zu behandeln, ohne drei Versuche abzuwarten, wenn eines dieser Muster zutrifft:

1. **Informationslücke:** Eine für die Lösung nötige Angabe fehlt in allen Pflicht-Dokumenten.
2. **Widerspruch:** Zwei Dokumente geben unvereinbare Vorgaben und kein ADR löst den Konflikt auf.
3. **Fremde Modulgrenze:** Die Lösung würde Änderungen in einem Modul erfordern, das nicht Teil des aktuellen Fahrplan-Schritts ist.
4. **Freigabebedarf:** Die Lösung fällt in eine Kategorie aus CLAUDE.md Abschnitt 4.
5. **Nicht-deterministisches Verhalten:** Das Problem tritt nicht reproduzierbar auf. Nicht-Reproduzierbarkeit ist selbst ein Blocker, keine akzeptierte Eigenschaft.

In diesen Fällen: direkt Eintrag hier anlegen, ohne Dreifach-Versuch.

Für alle anderen Fälle gilt die Dreifach-Regel aus CLAUDE.md Abschnitt 10.

---

## Aktive Blocker

### Blocker #NNN: [Titel]

- **Datum:** YYYY-MM-DD
- **Fahrplan-Referenz:** [Phase.Schritt-ID]
- **Modul:** [betroffenes Modul]
- **Blocker-Typ:** [Informationslücke | Widerspruch | Fremde Modulgrenze | Freigabebedarf | Nicht-deterministisch | Dreifach-Fehlschlag]
- **Beschreibung:**
  [Was funktioniert nicht, unter welchen Bedingungen tritt das Problem auf.
  Konkret, prüfbar. Keine Spekulation ohne Kennzeichnung.]
- **Reproduktion:**
  ```
  [Exakte Schritte zur Reproduktion, mit Kommandos/Inputs/erwarteter vs. tatsächlicher Ausgabe]
  ```
- **Versuchte Ansätze (bei Dreifach-Fehlschlag):**
  1. [Ansatz 1] – Ergebnis: [...] – Grund des Scheiterns: [...]
  2. [Ansatz 2] – Ergebnis: [...] – Grund des Scheiterns: [...]
  3. [Ansatz 3] – Ergebnis: [...] – Grund des Scheiterns: [...]
- **Offene Hypothesen:**
  - [Was könnte noch versucht werden, braucht aber eine Entscheidung/Information/Freigabe]
- **Benötigt zur Auflösung:**
  - [Konkrete Information, Freigabe, externe Klärung – ohne Auslassungen]
- **Vorgeschlagene Entscheidungsfrage:**
  [Die spezifische Frage, die der Mensch beantworten soll, in einer Form, aus der eine Antwort direkt abgeleitet werden kann]

### Blocker #NNN: [...]

[...]

---

## Gelöste Blocker

[Nach Auflösung hierher verschieben. Ergänzungen: "Lösungsdatum", "Lösung", "ADR-Referenz falls zutreffend".
Bei hoher Anzahl: nach `docs/archiv/blockers-YYYY-MM.md` auslagern.]

### Blocker #NNN: [Titel] – GELÖST YYYY-MM-DD

- **Ursprüngliche Beschreibung:** [gekürzt oder Referenz]
- **Lösung:** [was hat funktioniert, warum]
- **ADR:** [falls die Auflösung einen ADR erzeugt hat]
- **Abgeleitete Regel:** [falls eine wiederkehrende Lektion entstanden ist]

---

**Initialisierungshinweis (erste Session nach Projektanlage):**

- Beispiel-Blocker entfernen. Abschnitt „Aktive Blocker" startet leer mit Hinweis „Keine aktiven Blocker".
- Abschnitt „Blocker-Erkennung" ist **nicht optional** und bleibt projektübergreifend identisch – nicht anpassen.
- Datei wird erst befüllt, wenn ein echter Blocker auftritt (vorzeitige Erkennung nach Abschnitt oben oder Dreifach-Fehlschlag).
- Nummerierung durchgehend (keine Lücken, auch gelöste Blocker behalten ihre Nummer).
- Format des Eintrags (Felder und Struktur) ist **nicht optional**.
