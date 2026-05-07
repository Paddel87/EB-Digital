# Vision

<!-- Eingangs-Dokument eines Projekts. Wird VOR der Erstellung der anderen Dokumente
     ausgefüllt und bleibt danach als historisches Artefakt im Repo erhalten.
     Zweck: rohe Idee strukturiert erfassen, bevor sie in Konzept und Architektur überführt wird.
     Diese Datei wird nach Initialisierung der anderen Dokumente NICHT mehr verändert –
     spätere Erkenntnisse landen in project-context.md, decisions.md, fahrplan.md.
     Die Vision bleibt als Referenz: „so haben wir es ursprünglich gewollt". -->

## 1. Kernidee

[1–3 Sätze, in eigenen Worten. Was soll dieses System grundsätzlich tun?
Hier noch keine Architektur, keine Technologie, keine Implementierungsdetails.]

## 2. Problem und Anlass

- **Welches Problem löst das System?** [konkret, nicht „macht alles besser"]
- **Wer hat dieses Problem heute?** [Zielgruppe, möglichst spezifisch]
- **Wie wird das Problem heute gelöst (oder nicht)?** [Status quo, bekannte Workarounds]
- **Warum reicht das nicht?** [was die heutigen Lösungen nicht leisten]

## 3. Zielbild

[Beschreibe in 3–7 Sätzen, wie ein Nutzer das System idealerweise erlebt.
Schreibe in der Gegenwart, als ob es bereits existiert. Keine Konjunktive.]

**Beispielszenario (User Story-Form, 1–3 Beispiele):**

- [Ein Nutzer mit Eigenschaft X öffnet das System und tut Y. Er erhält Z.]
- [...]

## 4. Erfolgskriterien

[Woran erkennen wir, dass das System sein Ziel erreicht hat?
Soweit möglich messbar formulieren – auch wenn die Zahlen anfangs grobe Schätzungen sind.]

- [z. B. „Ein Anwendungsfall, der heute 30 Minuten dauert, soll in unter 5 Minuten erledigbar sein"]
- [z. B. „System soll von einer Person mit Grundkenntnissen ohne Schulung bedienbar sein"]
- [z. B. „Mindestens 10 reguläre Nutzer aus der Zielgruppe innerhalb der ersten 3 Monate"]

## 5. Bewusste Abgrenzung

**Was das System ausdrücklich NICHT tun soll** – auch wenn es naheliegend wäre:

- [z. B. „Keine Integration mit fremden Kalendern – Fokus auf Eigenstand"]
- [z. B. „Kein Mehrmandantenbetrieb in Phase 1"]
- [z. B. „Keine Mobile-App, nur responsive Web"]

[Dieser Abschnitt ist wichtig: er schützt vor Scope-Creep und gibt der KI später
klare Grenzen, was nicht zur Diskussion steht.]

## 6. Harte Randbedingungen

[Was steht von Anfang an fest und ist nicht verhandelbar?
Falls keine harten Randbedingungen: Abschnitt mit „keine" füllen, nicht weglassen.]

- **Technologie (falls fixiert):** [z. B. „Muss Python sein, weil bestehende Skripte"; oder „offen"]
- **Hosting:** [z. B. „Self-Hosting Pflicht"; „Cloud erlaubt"; „offen"]
- **Datenschutz/Compliance:** [z. B. „DSGVO Pflicht"; „Daten dürfen Deutschland nicht verlassen"; „keine besonderen Anforderungen"]
- **Lizenzmodell:** [z. B. „Open Source unter MIT geplant"; „proprietär"; „offen"]
- **Zeitrahmen:** [z. B. „erste lauffähige Version in 8 Wochen"; „kein harter Termin"]
- **Budget für externe Dienste:** [z. B. „kein Budget, nur kostenlose Tier"; „bis 50 €/Monat"; „offen"]

## 7. Weiche Präferenzen

[Was wäre angenehm, ist aber verhandelbar? Hilft der KI später bei Vorschlägen,
ohne sie als harte Regel zu behandeln.]

- [z. B. „Bevorzuge bekannte Frameworks vor Eigenentwicklung"]
- [z. B. „Lieber wenige, gut integrierte Tools als viele Spezialwerkzeuge"]
- [z. B. „Stabilität vor Aktualität bei Bibliothekswahl"]

## 8. Inspirationen und Vorbilder

[Existierende Systeme, die in Teilen ähnlich sind – auch wenn sie nicht 1:1 übernommen werden.
Hilft, Kontext und Erwartung zu vermitteln.]

- **[System / Produkt]:** [was daran inspirierend ist, was nicht übernommen werden soll]
- [...]

## 9. Bekannte Risiken und offene Punkte

[Stellen, an denen die Vision selbst unsicher oder ambivalent ist.
Wichtig: hier ehrlich sein – die Konzeptphase greift genau diese Punkte auf.]

- **[Risiko/offener Punkt]:** [was ist unklar oder problematisch]
- [...]

## 10. Was diese Vision nicht ersetzt

Dieses Dokument ist Eingang in die Konzeptphase, nicht ihr Ergebnis.
Es ersetzt **nicht**:

- die Architekturentscheidung (kommt in `architecture.md`)
- die Stack-Entscheidung (kommt in `project-context.md` und `decisions.md`)
- die Roadmap (kommt in `fahrplan.md`)
- die Constraints in operationalisierter Form (kommt in `project-context.md`)

---

**Überführungs-Status:**

- [ ] Vision von Mensch ausgefüllt
- [ ] Konzeptphase abgeschlossen (Lücken geschlossen, Optionen entschieden)
- [ ] Härtungsphase abgeschlossen (Blocker und Inkonsistenzen geprüft)
- [ ] Vorlagen-Set initialisiert (project-context.md, architecture.md, fahrplan.md, decisions.md, blockers.md)
- [ ] ADR-001 angelegt: Anpassung des Vorlagen-Sets
- [ ] Datum der Initialisierungs-Abschluss: [YYYY-MM-DD]

**Nach abgeschlossener Initialisierung:** Diese Datei wird nicht mehr verändert.
Spätere Vision-Erweiterungen oder Pivots werden in einem ADR dokumentiert,
nicht in dieser Datei. Bei substantieller Vision-Änderung: neuer ADR mit Verweis hier.
