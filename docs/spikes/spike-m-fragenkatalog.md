# Spike M — Fahrzeugbezeichnungs-Schema: Fragenkatalog für die DPolG Bremen

- **Fahrplan-Referenz:** 5.5 (Phase 5, ERKUNDUNG — Vergleichsstudie + Stakeholder-Rückfrage)
- **Datum:** 2026-06-11
- **Status:** **ABGESCHLOSSEN** — Antworten am 2026-06-11 von Patrick (Plattform-Betreiber mit DPolG-Bezug) direkt im Chat gegeben (Teil 4); fixiert als **ADR-025** in `docs/decisions.md`. Schließt Phase 5 ab (5/5 Spikes).
- **Verfahren:** Antworten unten eingetragen → ADR-025 `[ERKENNTNIS] [MODUL] [DATENMODELL]` „Fahrzeug-Naming".

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

## Teil 4 — Fragenkatalog (M1–M8) mit Antworten (2026-06-11)

| Nr.       | Frage (Kurzform)                  | **Antwort**                                                                                                                  |
| --------- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **M1/M2** | Bestehende Konvention + Übernahme | **Mischform** — System schlägt Default-Bezeichnung vor (`EB-<Mandanten-Kürzel>-NN`), Disponent kann überschreiben (Freitext) |
| **M3**    | Stabilität                        | **dauerhaft** (Stammdaten; folgt aus `vehicle`-Tabelle 4.2)                                                                  |
| **M4**    | Vergabe-Berechtigung              | **Disponent/Plattform-Admin** bei Fahrzeug-Anlage (folgt aus Fleet-Rollen-Matrix S8d 4.2)                                    |
| **M5**    | Reichweite Eindeutigkeit          | **pro Mandant** (Verbund-Präfix automatisch in Phase X)                                                                      |
| **M6**    | Länge                             | **max 20 Zeichen**                                                                                                           |
| **M7**    | BOS-Abgrenzung                    | **UI-Hinweis, keine harte Sperre** (keine technische Erkennung)                                                              |
| **M8**    | Zeichensatz                       | **Umlaute erlaubt** (ä ö ü Ä Ö Ü ß + A–Z, 0–9, Bindestrich, Leerzeichen)                                                     |

## Teil 5 — Ergebnis (fixiert in ADR-025)

Die Antworten sind als **ADR-025** `[ERKENNTNIS] [MODUL] [DATENMODELL]` festgehalten. Datenmodell-Konsequenzen auf `vehicle.name` (Implementierung als Phase-6.2-Migration, da `vehicle`-Tabelle seit 4.2 `[BELASTBAR]`, im Status Konzeption ohne Produktivdaten — additiv und risikofrei):

- **Länge:** `String(120)` → `String(20)` (M6).
- **Zeichensatz-CHECK** `ck_vehicle_name_charset`: Regex `^[A-Za-zÄÖÜäöüß0-9 -]+$` plus Nicht-Leer (`length(btrim(name)) >= 1`) (M8).
- **Eindeutigkeit:** Partial-UNIQUE `uq_vehicle_tenant_name_active` auf `(tenant_id, name)` `WHERE is_active = TRUE` (M5) — wiederverwendet das Soft-Delete-Prädikat des bestehenden `ix_vehicle_tenant_id_active`.
- **Default-Vorbelegung (UI, kein DB-Constraint):** `frontend-disponent` schlägt `EB-<Mandanten-Kürzel>-NN` vor, überschreibbar (M1/M2).
- **UI-Hinweise (keine technische Durchsetzung):** „keine Personennamen" (PII-Leitplanke, Vision) + „keine echten Funkrufnamen" (M7).
