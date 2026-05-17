# Spike I — Geo-Plausibilitäts-Algorithmus (Ergebnisse)

- **Datum:** 2026-05-18
- **Fahrplan-Referenz:** Schritt 3.1
- **Phasentyp:** ERKUNDUNG (Schritt-Art: Spike + Vergleichsstudie)
- **Zeitbox:** 4 h
- **Patrick-Direktive:** A-vs-B-Vergleich + 500-m-Moderationsfilter; Kalman-Filter ausdrücklich nicht im Scope
- **Test-Datensatz:** Bremen Innenstadt (mehrere Polygone) + Osterdeich/Weserstadion-Bereich (Werder-Heimspiel-Szenario)
- **ADR-Ergebnis:** ADR-017 `[ERKENNTNIS] [PERFORMANCE]` (siehe `decisions.md`)

Dieser Spike ist eine Reißbrett-Übung. Es wurde kein Produktivcode geändert; alle Test-Punkte sind synthetisch mit realistischen `accuracy`-Werten aus der Geolocation-API-Praxis konstruiert. Reale GPS-Feldmessung folgt in Phase 4 / Phase 6.

---

## 1. Problemzuschnitt

`project-context.md` Abschnitt 6 (Sicherheit) verlangt:

> Geografische Plausibilitätsprüfung auf Einsatzkraft-Bestellungen — Regel: Distanz vom GPS-Standort zum nächstgelegenen aktiven Einsatzraum > Schwellenwert (initial 5 km, anpassbar pro Einsatz) wirft Bestellung in Disponenten-Moderation, nicht in Auto-Verteilung.

Daraus die sechs offenen Detail-Fragen, die der Spike klärt:

1. **Distanz-Metrik:** Hülle vs. Centroid.
2. **GPS-Ungenauigkeit:** pauschaler Aufschlag (A) vs. `2·accuracy`-dynamisch (B).
3. **Moderations-Filter:** accuracy > 500 m → moderieren.
4. **Text-Standort:** Bestellung ohne GPS-Position.
5. **Konfigurations-Verankerung:** pro Mandant, pro Einsatz, pro Plattform.
6. **Performance:** Bounding-Box-Pre-Filter notwendig?

---

## 2. Test-Datensatz

### 2.1 Polygone (vereinfachte Geometrien für Spike-Zwecke)

| ID  | Beschreibung                                    | Form                  | Ungefähre Maße   | Centroid-Lage            | Charakter                        |
| --- | ----------------------------------------------- | --------------------- | ---------------- | ------------------------ | -------------------------------- |
| P1  | Marktplatz / Domshof                            | annähernd quadratisch | 150 m × 100 m    | mittig                   | kompakt                          |
| P2  | Schlachte (Weseruferpromenade)                  | länglich, am Ufer     | 400 m × 60 m     | längs in der Mitte       | sehr länglich                    |
| P3  | Sögestraße / Liebfrauenkirche                   | unregelmäßig kompakt  | 100 m × 80 m     | mittig                   | kompakt                          |
| P4  | Hauptbahnhof-Vorplatz                           | annähernd quadratisch | 150 m × 150 m    | mittig                   | kompakt                          |
| P5  | Bürgerpark (Großlagen-Zonen-Beispiel)           | unregelmäßig groß     | 800 m × 400 m    | mittig im Wiesenbereich  | groß, unregelmäßig               |
| P6  | Weserstadion + Osterdeich-Fanmeile bis Sielwall | sehr länglich         | ~1 500 m × 200 m | mittig (Stadion-Vorfeld) | extrem länglich, Werder-Szenario |

P6 ist der entscheidende Stresstest für die Hülle-vs-Centroid-Frage: Eine Einsatzkraft am Sielwall (Ostende) ist 0 m von der Hülle entfernt, aber ~750 m vom Centroid (Stadion-Vorfeld).

### 2.2 GPS-Testpunkte

Notation: `(distance_zu_huelle_m | distance_zu_centroid_m | accuracy_m)`. Die Distanzen sind aus der Polygon-Geometrie hergeleitet; die `accuracy_m`-Werte sind realistisch gewählt nach Geolocation-API-Praxis (Smartphone-GPS draußen 5–20 m, Stadtkanyon 20–80 m, indoor 30–200 m, Cell-Tower-only 500–3 000 m).

**Szenario S1 — Hülle vs. Centroid (P6, längliches Polygon):**

| ID  | Lage                                      | Hülle-Distanz | Centroid-Distanz | accuracy |
| --- | ----------------------------------------- | ------------- | ---------------- | -------- |
| T1  | drinnen am östlichen Ende (Sielwall)      | 0 m           | ~750 m           | 15 m     |
| T2  | drinnen am westlichen Ende (Stadion-Tor)  | 0 m           | ~700 m           | 25 m     |
| T3  | 50 m außerhalb am Südrand (Weseruferpfad) | 50 m          | ~200 m           | 10 m     |
| T4  | 200 m außerhalb (St.-Pauli-Friedhof)      | 200 m         | ~600 m           | 20 m     |

**Szenario S2 — A vs. B Vergleich (P1 Marktplatz, kompakt; Schwellenwert hier ausnahmsweise eng auf 100 m gesetzt, um die Varianten-Unterschiede sichtbar zu machen):**

| ID  | Lage            | Hülle-Distanz | accuracy | Kontext                     |
| --- | --------------- | ------------- | -------- | --------------------------- |
| T5  | drinnen Mitte   | 0 m           | 10 m     | gutes GPS                   |
| T6  | 50 m außerhalb  | 50 m          | 5 m      | sehr gutes GPS              |
| T7  | 50 m außerhalb  | 50 m          | 80 m     | Stadtkern, GPS schlecht     |
| T8  | 80 m außerhalb  | 80 m          | 5 m      | sehr gutes GPS, knapp außen |
| T9  | 200 m außerhalb | 200 m         | 10 m     | klar außen, GPS gut         |

**Szenario S3 — Moderations-Filter accuracy > 500 m (P1):**

| ID  | Lage                          | Hülle-Distanz | accuracy | Kontext                   |
| --- | ----------------------------- | ------------- | -------- | ------------------------- |
| T10 | drinnen Mitte                 | 0 m           | 800 m    | Cell-Tower-only           |
| T11 | drinnen Mitte P6 (Osterdeich) | 0 m           | 1 500 m  | Funkloch + Mobilfunk-only |
| T12 | 100 m außerhalb P1            | 100 m         | 800 m    | Cell-Tower, knapper Fall  |

**Szenario S4 — Text-Standort (kein GPS):**

| ID  | Lage                       | Hülle-Distanz | accuracy | Kontext               |
| --- | -------------------------- | ------------- | -------- | --------------------- |
| T13 | keine Geolocation gemeldet | —             | —        | Permission verweigert |

**Szenario S5 — Mandanten-/Einsatz-Schwellenwert (P6, Werder-Heimspiel-Großlage):**

| ID   | Lage                                 | Hülle-Distanz | accuracy | Schwellenwert                      |
| ---- | ------------------------------------ | ------------- | -------- | ---------------------------------- |
| T14  | 4 km außerhalb P6                    | 4 000 m       | 15 m     | 5 000 m (Default)                  |
| T14' | 4 km außerhalb P6 (gleiche Position) | 4 000 m       | 15 m     | 500 m (eng konfigurierter Einsatz) |

---

## 3. Algorithmus-Pseudocode

### 3.1 Datenmodell-Skizze

```
PlausibilityConfig:
  tenant_default_threshold_m: int = 5000  # mandantenweiter Default
  moderation_accuracy_threshold_m: int = 500  # Plattform-Konstante (nicht mandanten-konfigurierbar in Phase 1)
  min_threshold_m: int = 50    # Sinnigkeits-Untergrenze
  max_threshold_m: int = 50000 # Bundesland-Obergrenze

Operation:
  active_rooms: list[OperationRoom]   # mind. 1 in Phase aktiv
  plausibility_threshold_m: Optional[int] = None  # überschreibt Mandanten-Default

GPSReading:
  point: Point  # (lat, lon)
  accuracy_m: float | None  # 1-Sigma-Radius, aus position.coords.accuracy

PlausibilityResult (enum):
  ACCEPTED
  MODERATION_NO_GPS                # kein Standort gemeldet (S4)
  MODERATION_ACCURACY_UNKNOWN      # accuracy ist None
  MODERATION_ACCURACY_TOO_LOW      # accuracy > Moderations-Schwelle (S3)
  MODERATION_OUT_OF_RANGE          # effective_distance > Einsatz-Schwelle
```

### 3.2 Hauptfunktion

```
def check_plausibility(
    operation: Operation,
    gps: Optional[GPSReading],
    config: PlausibilityConfig,
) -> tuple[PlausibilityResult, PlausibilityAuditFields]:

    # S4: Text-Standort / kein GPS-Fix → moderieren, nicht ablehnen
    if gps is None:
        return (
            PlausibilityResult.MODERATION_NO_GPS,
            PlausibilityAuditFields(distance_m=None, accuracy_m=None, threshold_m=None),
        )

    # accuracy fehlt (manche Browser/Apps liefern keinen Wert)
    if gps.accuracy_m is None:
        return (
            PlausibilityResult.MODERATION_ACCURACY_UNKNOWN,
            PlausibilityAuditFields(distance_m=None, accuracy_m=None, threshold_m=None),
        )

    # S3: schlechte GPS-Qualität → moderieren
    if gps.accuracy_m > config.moderation_accuracy_threshold_m:
        return (
            PlausibilityResult.MODERATION_ACCURACY_TOO_LOW,
            PlausibilityAuditFields(distance_m=None, accuracy_m=gps.accuracy_m, threshold_m=None),
        )

    # Edge-Case: unrealistisch niedrige accuracy → Untergrenze 5 m
    effective_accuracy_m = max(gps.accuracy_m, 5.0)

    # Schwellenwert: einsatz-spezifisch, sonst mandanten-Default
    threshold_m = (
        operation.plausibility_threshold_m
        if operation.plausibility_threshold_m is not None
        else config.tenant_default_threshold_m
    )
    # Min/Max-Validierung sollte bereits an der Eingangs-Schnittstelle (Mandant/Einsatz)
    # erfolgt sein. Hier defensiv clampen:
    threshold_m = max(config.min_threshold_m, min(threshold_m, config.max_threshold_m))

    # Distanz zur Hülle des nächstgelegenen aktiven Einsatzraums
    # distance_point_to_polygon_boundary liefert 0, wenn der Punkt im Polygon liegt
    distance_m = min(
        distance_point_to_polygon_boundary(gps.point, room.geometry)
        for room in operation.active_rooms
    )

    # Variante B: dynamische GPS-Toleranz (95-%-Konfidenz)
    effective_distance_m = distance_m - (2 * effective_accuracy_m)

    fields = PlausibilityAuditFields(
        distance_m=distance_m,
        accuracy_m=gps.accuracy_m,
        threshold_m=threshold_m,
    )

    if effective_distance_m <= threshold_m:
        return (PlausibilityResult.ACCEPTED, fields)
    return (PlausibilityResult.MODERATION_OUT_OF_RANGE, fields)
```

### 3.3 Vergleich der Varianten

- **Variante A (pauschal):** `effective_distance_m = distance_m - 30` (fester Aufschlag, unabhängig von `accuracy_m`).
- **Variante B (dynamisch):** `effective_distance_m = distance_m - (2 * effective_accuracy_m)` (entspricht 95-%-Konfidenz unter Annahme, dass `accuracy` der 1-Sigma-Radius ist).

Beide Varianten verwenden die gleiche Hülle-Distanz, nur die Tolerance-Berechnung unterscheidet sich.

---

## 4. Durchrechnen pro Test-Punkt

### 4.1 S1 — Hülle vs. Centroid (P6, Schwellenwert 5 000 m / Default)

| ID  | Hülle | Centroid | accuracy | Hülle-basiert (B)        | Centroid-basiert (B)       |
| --- | ----- | -------- | -------- | ------------------------ | -------------------------- |
| T1  | 0     | 750      | 15       | ACCEPTED (0 + 30 < 5000) | ACCEPTED (750 + 30 < 5000) |
| T2  | 0     | 700      | 25       | ACCEPTED                 | ACCEPTED                   |
| T3  | 50    | 200      | 10       | ACCEPTED                 | ACCEPTED                   |
| T4  | 200   | 600      | 20       | ACCEPTED                 | ACCEPTED                   |

Bei großzügigem Schwellenwert (5 km) wirken beide Metriken oberflächlich gleich. **Aber:** stellt man den Schwellenwert eng (z. B. 500 m für eine kleinere Mahnwache auf nur einem Teil-Areal), kippt das Bild:

| ID  | Hülle | Centroid | accuracy | Hülle-basiert (B), Schwellenwert 500 | Centroid-basiert (B), Schwellenwert 500 |
| --- | ----- | -------- | -------- | ------------------------------------ | --------------------------------------- |
| T1  | 0     | 750      | 15       | ACCEPTED (0 + 30 < 500)              | **MODERATION** (750 + 30 > 500)         |
| T2  | 0     | 700      | 25       | ACCEPTED                             | **MODERATION**                          |
| T3  | 50    | 200      | 10       | ACCEPTED                             | ACCEPTED                                |
| T4  | 200   | 600      | 20       | ACCEPTED                             | **MODERATION**                          |

→ **Hülle ist die korrekte Metrik.** Centroid bricht bei länglichen Polygonen und engen Schwellenwerten zusammen.

### 4.2 S2 — A vs. B (P1, Schwellenwert 100 m, Hülle-basiert)

| ID  | Hülle | accuracy | Variante A: `dist + 30 ≤ 100`?    | Variante B: `dist + 2·accuracy ≤ 100`? | Beobachtung                                                                                                                                           |
| --- | ----- | -------- | --------------------------------- | -------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| T5  | 0     | 10       | A: ACCEPTED (0 + 30 = 30)         | B: ACCEPTED (0 + 20 = 20)              | beide ok                                                                                                                                              |
| T6  | 50    | 5        | A: ACCEPTED (50 + 30 = 80)        | B: ACCEPTED (50 + 10 = 60)             | beide ok                                                                                                                                              |
| T7  | 50    | 80       | A: ACCEPTED (50 + 30 = 80)        | **B: MODERATION (50 + 160 = 210)**     | **B konservativer** bei schlechtem GPS — richtig im Stadtkern, wo die Person evtl. 200 m weiter steht als gemeldet                                    |
| T8  | 80    | 5        | **A: MODERATION (80 + 30 = 110)** | B: ACCEPTED (80 + 10 = 90)             | **B präziser** bei gutem GPS — wer scharfen 5-m-Fix hat und 80 m außen ist, ist real außen, aber innerhalb der 100-m-Toleranz mit `2·accuracy`-Modell |
| T9  | 200   | 10       | A: MODERATION (200 + 30 = 230)    | B: MODERATION (200 + 20 = 220)         | beide moderieren                                                                                                                                      |

**T7 und T8 sind die entscheidenden Unterscheidungs-Fälle.** Variante B passt sich der GPS-Qualität an: konservativ bei schlechtem GPS (verhindert falsche Akzeptanz aus dem Stadtkern-Echo), präziser bei gutem GPS (vermeidet unnötige Disponenten-Last bei klar geo-konformen Bestellungen).

### 4.3 S3 — Moderations-Filter

| ID  | Hülle | accuracy | Ergebnis                        |
| --- | ----- | -------- | ------------------------------- |
| T10 | 0     | 800      | **MODERATION_ACCURACY_TOO_LOW** |
| T11 | 0     | 1 500    | **MODERATION_ACCURACY_TOO_LOW** |
| T12 | 100   | 800      | **MODERATION_ACCURACY_TOO_LOW** |

Greift bevor die Distanz-Berechnung läuft. Konsequenz: Bestellungen mit Cell-Tower-only-Locating (typisch bei Funklöchern oder ausgeschaltetem GPS) landen immer beim Disponenten. Vorteil: Algorithmus trifft keine Entscheidung auf Basis einer ±1-km-GPS-Schätzung.

Wenn nötig, kann diese Schwelle pro Mandant überschreibbar werden (Phase 1: nicht). Eine Ländliche Großlage könnte z. B. eine höhere Toleranz vertreten — das wäre ein eigener ADR.

### 4.4 S4 — Text-Standort

| ID  | Eingabe                     | Ergebnis              |
| --- | --------------------------- | --------------------- |
| T13 | keine GPS-Position gemeldet | **MODERATION_NO_GPS** |

Bewusste Entscheidung gegen hartes Ablehnen: in Funklöchern, in Einsatzfahrzeugen mit Metalldach, oder bei verweigerter Browser-Permission gibt es legitime Gründe, ohne GPS zu bestellen. Disponent sieht die Bestellung mit Hinweis „kein Standort" und kann sie nach Sichtprüfung freigeben.

### 4.5 S5 — Schwellenwert-Konfiguration

| ID   | Hülle | accuracy | Schwellenwert     | Variante B Ergebnis                       |
| ---- | ----- | -------- | ----------------- | ----------------------------------------- |
| T14  | 4 000 | 15       | 5 000 (Default)   | ACCEPTED (4 000 + 30 = 4 030 ≤ 5 000)     |
| T14' | 4 000 | 15       | 500 (eng konfig.) | **MODERATION** (4 000 + 30 = 4 030 > 500) |

Begründet die Notwendigkeit pro-Einsatz-Konfiguration: Werder-Heimspiel (P6) mit ausgedehntem Fanstrom-Bereich erlaubt 5 km Toleranz, eine Mahnwache mit klar definierter Position rechtfertigt 200–500 m.

---

## 5. Konfigurations-Verankerung

Drei Ebenen, hierarchisch:

1. **Plattform-Konstante** (`PlausibilityConfig.moderation_accuracy_threshold_m`, `min_threshold_m`, `max_threshold_m`) — fest in Code/ENV, keine UI-Konfiguration in Phase 1. Änderung nur per ADR.
2. **Mandanten-Default** (`tenant.plausibility_default_threshold_m`) — pro Mandant einstellbar in Mandanten-Stammdaten. Default 5 000 m bei Mandanten-Anlage. Validierung gegen `min_threshold_m` / `max_threshold_m`.
3. **Einsatz-Override** (`operation.plausibility_threshold_m`) — optional, vom Disponenten beim Eröffnen oder im laufenden Einsatz änderbar. Validierung wie oben. Audit-Log-Eintrag bei Änderung (Regel-012: routing-/sichtbarkeits-beeinflussende Disponenten-Aktion).

**Datenmodell-Erweiterungen (für Phase 4 / Phase 2-Schema-Anpassung):**

- `tenant.plausibility_default_threshold_m INTEGER NOT NULL DEFAULT 5000` mit `CHECK (50 <= plausibility_default_threshold_m <= 50000)`.
- `operation.plausibility_threshold_m INTEGER NULL` mit `CHECK (plausibility_threshold_m IS NULL OR (50 <= plausibility_threshold_m <= 50000))`.

Migration ist additiv und nicht-breakend. Wird mit Phase 4 (`backend/operations` produktiv) ausgerollt, nicht früher.

---

## 6. Performance-Betrachtung

Aufwand pro Plausibilitäts-Check: O(N · K) mit

- N = aktive Räume der konkreten Operation (Phase 1: typisch 1–5, Worst Case Phase 7: 10),
- K = Polygon-Kanten pro Raum (typisch 10–50, Worst Case 100).

Bei p95-Annahme 300 ms für die gesamte Order-Endpunkt-Bearbeitung (DB-Insert, Audit-Log, WebSocket-Notify) liegt der reine Geometrie-Anteil unter 1 ms — die teuren `point-to-polygon-boundary`-Berechnungen sind in C-optimierten Geometrie-Bibliotheken (Shapely, GEOS) im Mikrosekunden-Bereich.

**Bounding-Box-Pre-Filter:** nicht erforderlich für Phase 1 und Phase 4. Aufnehmen, wenn Mandanten >50 parallele aktive Räume betreiben (unrealistisch in Phase 7-Annahme 50/500). Reserviert als Performance-Reserve für spätere Phasen ohne ADR-Folge.

**Konsequenz für Phase 4:** die Plausibilitäts-Check-Logik darf synchron im Order-Endpunkt laufen, kein Procrastinate-Job nötig.

---

## 7. Edge Cases

| Fall                                           | Behandlung                                                                                                                                                               |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| GPS-Punkt liegt im Polygon                     | `distance_m = 0` per Konvention → ACCEPTED                                                                                                                               |
| GPS-Punkt liegt exakt auf Polygon-Rand         | `distance_m = 0` → ACCEPTED                                                                                                                                              |
| Operation hat keine aktiven Räume              | Programmier-Fehler — Plausibilitäts-Check sollte vorher gar nicht aufgerufen werden. Empfehlung: `raise OperationHasNoActiveRoomsError` (defensiv, Bug-Indikator)        |
| `gps.accuracy_m = None`                        | MODERATION_ACCURACY_UNKNOWN — Disponent entscheidet                                                                                                                      |
| `gps.accuracy_m <= 0` (unrealistisch)          | mit `max(accuracy, 5.0)` auf 5-m-Untergrenze gehoben                                                                                                                     |
| Mehrere parallele Einsätze desselben Mandanten | Plausibilitäts-Check operiert pro **konkreter** Operation (via URL-Token aus anonymer Session), nicht über alle Mandanten-Einsätze hinweg. Kein Cross-Operation-Leakage. |
| Polygon hat Löcher (Inseln, Sperrzonen)        | Phase 1 nicht unterstützt — Einsatzraum ist ein einfaches Polygon. Wenn später nötig: separater ADR, `point-in-polygon-with-holes` ist Standard in Shapely.              |

---

## 8. Sicherheits-/Datenschutz-Hinweise

### 8.1 Sicherheit: Manipulationsschutz

Der GPS-Punkt wird vom Client gemeldet und kann manipuliert sein. Das ist akzeptiert: der Plausibilitäts-Check ist Filter gegen versehentliche oder verwirrte Bestellungen, nicht gegen vorsätzliche Manipulation. Vorsätzliche Angreifer können auch GPS-Spoofing betreiben — die Hürde dafür ist niedriger als die Hürde, eine plausible Bestellung im Disponenten-Moderationsfeld zu rechtfertigen. Daher gilt:

- **Plausibilitäts-Check ist NICHT als Sicherheitsmaßnahme zu verstehen.** Er reduziert Disponenten-Last bei gutwilligen, aber falsch positionierten Bestellern.
- **Hinweis im ADR-017:** das gehört explizit ins Threat-Model. Auth-Schicht (anonyme Session + optionaler AccessCode) bleibt die einzige Schutzschicht gegen Drittparteien.

### 8.2 Datenschutz: Logging

Roh-Koordinaten sind PII (Standort-Daten). `project-context.md` Abschnitt 6 verlangt: „Standortdaten in Logs nur als gehashter Tile-Identifier, nie als Roh-Koordinate."

**Spike-Konsequenz für Phase 4:**

- Audit-Log (`operation_audit_log`-Eintrag bei jeder Bestellung mit Plausibility-Ergebnis): speichert `outcome`, `distance_m`, `accuracy_m`, `threshold_m`, `variant`. Nicht die Koordinaten.
- Operativ-Log (strukturierte JSON-Logs): wenn überhaupt Standort-Bezug nötig, dann nur als gehashter Tile-Identifier (z. B. Web-Mercator-Tile `z14/8567/5436`). Standard-Praxis ist: gar kein Log-Eintrag mit Standort-Bezug, nur bei expliziter Debug-Notwendigkeit.
- Persistenz der Roh-Koordinaten: in `order.client_location` (oder analog) gemäß `backend/operations`-Datenmodell. Unterliegt der 30-Tage-Anonymisierung wie alle individuellen Bestelldaten.

### 8.3 Aggregat-Wirkung (Bezug ADR-006)

ADR-006 listet Aggregat-Felder pro Einsatz. Folgende Plausibility-Felder wären sinnvoll und sollen in Phase 4-Implementation des Aggregats geprüft werden:

- `count_orders_accepted` (bereits vorgesehen als `anzahl_bestellungen`)
- `count_orders_moderated` (Erweiterung — heute nicht in ADR-006 listed)

**Empfehlung:** kein neuer ADR jetzt. Phase-4-Implementation des Aggregat-Felds kann die neuen Counts additiv ergänzen, falls als Stakeholder-Nutzen bestätigt. Vorerst nur als Notiz.

---

## 9. Entscheidungs-Tabelle Zusammenfassung

| Frage                          | Entscheidung                                                 | Begründung (Kurz)                                                                    |
| ------------------------------ | ------------------------------------------------------------ | ------------------------------------------------------------------------------------ |
| Distanz-Metrik                 | **Hülle**                                                    | Längliche Polygone (P6 Osterdeich) brechen Centroid-Ansatz bei engen Schwellenwerten |
| GPS-Ungenauigkeit              | **Variante B (dynamisch, `2·accuracy`)**                     | Reagiert auf reale GPS-Qualität (konservativ in Funklöchern, präziser bei gutem Fix) |
| Untergrenze accuracy           | **5 m** (`max(accuracy, 5.0)`)                               | Unter 5 m unrealistisch, schützt vor 0-Werten                                        |
| Moderations-Filter             | **accuracy > 500 m** → MODERATION                            | Cell-Tower-only zu unsicher für Auto-Entscheidung                                    |
| Text-Standort / kein GPS       | **MODERATION**, nicht ablehnen                               | Legitime Gründe für GPS-Fehlen; Disponent ist im Loop                                |
| accuracy = None                | **MODERATION** (`MODERATION_ACCURACY_UNKNOWN`)               | Browser-Inkonsistenz; defensive Behandlung                                           |
| Konfigurations-Hierarchie      | **Plattform-Konstante → Mandant-Default → Einsatz-Override** | Werder-Stadion (5 km sinnvoll) vs. Marktplatz (300 m sinnvoll)                       |
| Schwellenwert-Default          | **5 000 m** (project-context.md unverändert)                 | bestätigt, kein ADR-Änderungs-Bedarf                                                 |
| Schwellenwert-Grenzen          | **50 m bis 50 000 m**                                        | unter 50 m wirkungslos, über 50 000 m außerhalb sinnvoller Großlagen-Geographie      |
| Bounding-Box-Pre-Filter        | **nicht in Phase 4**                                         | Aufwand < 1 ms bei realistischen N und K                                             |
| Synchrone vs. async Ausführung | **synchron im Order-Endpunkt**                               | <1 ms, kein Procrastinate-Job nötig                                                  |
| Sicherheits-Klassifizierung    | **kein Sicherheitsmechanismus**                              | Manipulationsschutz nicht beanspruchbar; explizit ins Threat-Model                   |

---

## 10. Offene Punkte für Phase 4 (Implementation)

Nicht im Scope dieses Spikes, aber als Erinnerung für die produktive Implementation:

1. **Schema-Migration:** Felder `tenant.plausibility_default_threshold_m` und `operation.plausibility_threshold_m` mit CHECK-Constraints (siehe Abschnitt 5).
2. **Disponenten-UI:** Eingabe-Feld für Einsatz-Schwellenwert (Default leer = Mandanten-Default verwenden). Mit Schiebe-Regler oder Eingabe-Feld plus Helper-Text „üblich 500 m für Mahnwachen, 5 000 m für Großlagen wie Werder-Heimspiele".
3. **Mandanten-Stammdaten-UI:** Default-Schwellenwert pro Mandant änderbar in Mandanten-Stammdaten (typisch durch Mandanten-Admin).
4. **Moderations-UI:** Disponent sieht moderierte Bestellungen mit Begründungs-Code (`MODERATION_NO_GPS`, `MODERATION_ACCURACY_TOO_LOW`, `MODERATION_OUT_OF_RANGE`) und kann „freigeben" / „ablehnen" — Audit-Log-Pflicht.
5. **Geometrie-Bibliothek:** Shapely 2.0+ als Backend-Dependency aufnehmen. Wird vermutlich ohnehin für andere Geo-Operationen gebraucht (Sperrungs-Override-Geometrien, Routing-Bounding-Boxen). Lizenz BSD-3, kompatibel mit `project-context.md` Abschnitt 6. Sub-Dependencies prüfen (GEOS dynamisch geladen, MIT-Lizenz).
6. **Coverage-Pflicht:** Plausibility-Logik liegt in `backend/operations` mit Bezug zu `backend/geo`. Coverage-Pflicht aus `project-context.md` Abschnitt 7: `backend/operations` ≥ 90 % Lines.

---

## 11. Reifegrad-Wirkung dieser Erkenntnis

- `architecture.md` Modul `backend/operations`: `[OFFEN]`-Bereich „Geo-Plausibilitäts-Algorithmus" → `[VORLÄUFIG]` mit ADR-017-Verweis.
- `architecture.md` Modul `backend/geo`: `[OFFEN]`-Bereich „Geo-Plausibilitäts-Algorithmus" (Komponente `PlausibilityChecker`) → `[VORLÄUFIG]` mit ADR-017-Verweis.
- Modul-Reifegrade selbst bleiben `[VORLÄUFIG]` — produktive Beförderung kommt mit Phase 4.

---

## 12. Begriffliche Klarstellung „Phase" (Spike-intern)

In diesem Dokument bezieht sich „Phase 1" auf die Vision-Phasenzählung (gesamte Initial-Architektur ohne Verbund-Modus, vor Phase X). Die `fahrplan.md`-Phasenzählung (Phase 1–7 plus X) ist die Implementierungsreihenfolge. Die Plausibility-Implementation gehört zu **Phase 4 der `fahrplan.md`-Zählung** = Operations Core + Realtime + Einsatzkraft-PWA.
