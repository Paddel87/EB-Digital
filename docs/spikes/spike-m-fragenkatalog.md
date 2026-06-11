# Spike M — Fahrzeugbezeichnungs-Schema: Fragenkatalog für die DPolG Bremen

- **Fahrplan-Referenz:** 5.5 (Phase 5, ERKUNDUNG — Vergleichsstudie + Stakeholder-Rückfrage)
- **Datum:** 2026-06-11
- **Status:** Vergleichsstudien-Teil erledigt, Fragenkatalog versandfertig — **wartet auf DPolG-Antworten** (Vorlage durch Patrick)
- **Verfahren:** Antworten unten im Antwortformat eintragen → daraus entsteht der Spike-M-ADR `[ERKENNTNIS] [DATENMODELL]` „Fahrzeug-Naming" (freigabepflichtig).

---

## Teil 1 — Anschreiben-Vorlage (für die DPolG, nicht-technisch)

> **Worum geht es?**
> In EB Digital bekommt jedes Betreuungsfahrzeug eine Bezeichnung, die überall dort angezeigt wird, wo mit dem Fahrzeug gearbeitet wird: der Disponent weist Aufträge einem Fahrzeug zu, das Betreuer-Team sieht „sein" Fahrzeug in der App, und Einsatzkräfte sehen perspektivisch eine Meldung wie „Fahrzeug _XY_ nähert sich". Damit das im Einsatz funktioniert, muss die Bezeichnung kurz, eindeutig und am Telefon/im Gespräch gut durchsagbar sein.
>
> Wir möchten **nicht** am grünen Tisch ein Schema erfinden, das eurer gelebten Praxis widerspricht. Deshalb vorab acht kurze Fragen — die meisten mit ja/nein oder einem Beispiel zu beantworten. Eine Rückmeldung pro Frage reicht; „wissen wir nicht / egal" ist eine zulässige Antwort.

## Teil 2 — Wo die Bezeichnung sichtbar wird (Entscheidungsgrundlage)

| Ort                        | Kontext                                     | Anforderung daraus                                                                               |
| -------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| Disponenten-UI             | Auftragszuweisung, Fahrzeugliste, Audit-Log | sortierbar, eindeutig auf einen Blick                                                            |
| Betreuer-PWA (Smartphone)  | „Dein Fahrzeug", Auftragsanzeige            | **kurz** (schmales Display)                                                                      |
| Einsatzkraft-PWA (Phase 6) | 150-m-Annäherungs-Hinweis                   | verständlich auch für Polizei-Bedienstete **anderer Verbände** (Cross-Berufsverbands-Versorgung) |
| Mündliche Kommunikation    | Telefon/Zuruf im Lagezentrum                | durchsagbar, verwechslungsarm                                                                    |
| Datenexport (DSGVO)        | Fahrzeug-Stammdaten                         | dauerhaft stabil                                                                                 |

**Datenschutz-Leitplanke (steht fest, keine Frage):** Bezeichnungen dürfen **keine Personennamen** enthalten („Bus Müller" ist unzulässig) — Vision-Constraint „keine Klarnamen im System".

## Teil 3 — Optionsvergleich (Vergleichsstudien-Teil, systemseitig)

|                                                          | **A: Strukturiertes Schema** (z. B. `EB-HB-01`) | **B: Verbandseigene Funkrufnamen**                                                                                          | **C: Freitext mit Systemregeln**     |
| -------------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ |
| Beispiel                                                 | `EB-HB-01`, `EB-HB-VT1`                         | wie bei euch etabliert                                                                                                      | „Bus 1", „Sprinter Nord"             |
| Vertrautheit für Betreuer                                | gering (neu gelernt)                            | **hoch**                                                                                                                    | hoch (selbst gewählt)                |
| Eindeutigkeit                                            | systemseitig garantiert                         | nur wenn Konvention es hergibt                                                                                              | systemseitig erzwungen (pro Verband) |
| Verständlich für Dritte (andere Verbände, Einsatzkräfte) | **hoch** (selbsterklärend mit Präfix)           | gering bis mittel                                                                                                           | mittel                               |
| Verwechslungsrisiko mit BOS-/Polizei-Funkrufnamen        | keines                                          | **prüfbedürftig** (EB Digital ist kein BOS-System — Anlehnung an echte Polizei-Rufnamen könnte im Einsatzumfeld irritieren) | je nach Wahl                         |
| Pflegeaufwand für den Verband                            | minimal                                         | keiner (existiert schon)                                                                                                    | gering                               |

**Vorläufige technische Empfehlung** (final erst nach euren Antworten): **Modell C als Systemmechanik** — das System erzwingt nur Eindeutigkeit pro Verband, eine Maximallänge und einen sicheren Zeichensatz — **mit Schema A als empfohlener Vorbelegung** in der Dokumentation. So kann die DPolG ihre etablierten Namen 1:1 verwenden (falls vorhanden), und Verbände ohne Konvention bekommen einen sinnvollen Default.

## Teil 4 — Fragenkatalog (M1–M8)

**Antwortformat pro Zeile:** Frage-Nr. + Antwort (bei ja/nein-Fragen reicht das Wort; Freitext wo gefragt).

- **M1 — Bestehende Konvention:** Gibt es bei der DPolG Bremen bereits etablierte Bezeichnungen für die Betreuungsfahrzeuge? _(ja → bitte 2–3 Beispiele / nein)_
- **M2 — Übernahme:** Falls ja: Sollen diese Bezeichnungen 1:1 in EB Digital erscheinen, oder darf das System ein eigenes Schema vorgeben? _(1:1 übernehmen / System darf vorgeben / Mischform)_
- **M3 — Stabilität:** Soll eine Bezeichnung dauerhaft am Fahrzeug bleiben (Stammdaten, einsatzübergreifend) oder pro Einsatz neu vergeben werden? _(dauerhaft / pro Einsatz — Hinweis: dauerhaft ist technisch vorgesehen und empfohlen)_
- **M4 — Vergabe:** Wer soll Bezeichnungen vergeben bzw. ändern dürfen? _(Disponent bei Fahrzeug-Anlage / Vorgabe durch Landesvorstand / beides)_
- **M5 — Reichweite der Eindeutigkeit:** Reicht es, wenn Bezeichnungen innerhalb der DPolG Bremen eindeutig sind? Bei späterer verbandsübergreifender Zusammenarbeit würde das System automatisch das Verbands-Kürzel voranstellen. _(reicht / wir wünschen von Anfang an verbandsübergreifend eindeutige Namen)_
- **M6 — Länge:** Ist eine Obergrenze von **20 Zeichen** für die Anzeige praktikabel (Smartphone-Display, Durchsagen)? _(ja / nein, wir brauchen bis zu \_\_ Zeichen)_
- **M7 — BOS-Abgrenzung:** Bestehen aus eurer Sicht Bedenken, wenn Fahrzeugbezeichnungen an polizeiliche Funkrufnamen erinnern (Verwechslungsgefahr im Einsatzumfeld)? Sollen wir solche Muster bewusst vermeiden? _(vermeiden / unkritisch / Freitext)_
- **M8 — Zeichensatz:** Werden Umlaute oder Sonderzeichen benötigt (z. B. „Süd")? _(ja, nämlich: … / nein, A–Z, 0–9, Bindestrich und Leerzeichen reichen)_

## Teil 5 — Was aus den Antworten wird (technische Konsequenz, intern)

- **Ist-Stand im Schema:** `vehicle.name` ist heute `String(120)`, **ohne** Eindeutigkeits- und Format-Constraint (bewusst offen gelassen bis Spike M). Der ADR fixiert: Maximallänge (M6), Zeichensatz-CHECK (M8), Partial-UNIQUE-Index auf `(tenant_id, name)` für aktive Fahrzeuge (M5; Verbund-Anzeige mit Mandanten-Kürzel-Präfix als spätere Phase-X-Konsequenz), Vergabe-/Änderungs-Berechtigung (M4 — Änderungen laufen wie alle Fleet-Mutationen über das Audit-Log), ggf. Format-Empfehlung als UI-Vorbelegung (M1/M2).
- **Kein Migrations-Risiko:** Constraint-Verschärfung auf `String(120)` → kürzer ist additiv möglich, solange keine produktiven Fahrzeuge existieren (Status Konzeption — genau deshalb jetzt klären).
- **PII-Regel** (keine Personennamen) wird unabhängig von den Antworten als UI-Hinweis + Doku-Regel umgesetzt; eine technische Namens-Erkennung ist bewusst nicht vorgesehen (Scheingenauigkeit).
