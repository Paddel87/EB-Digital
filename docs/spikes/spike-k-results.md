# Spike K — Hilfe-Knopf-Semantik: UX-Konzept + Datenmodell-Skizze

- **Fahrplan-Referenz:** 5.3 (Phase 5, ERKUNDUNG)
- **Datum:** 2026-06-10
- **Status:** Konzept vollständig, **wartet auf Freigabe** (ADR-Entwurf unten; ADR-Anlage ist freigabepflichtig, CLAUDE.md §4 Kategorie 4/5)
- **Zeitverbrauch:** ~1,5 h (innerhalb Zeitbox 2–3 h)

## 1. Vision-Anker (bindend)

- Hilfe-Knopf in der **Betreuer-PWA** für **Eigennot oder Pannen**, **einseitig zum Disponenten** (Vision Z. 101, Beispielszenario Reifenpanne Z. 53).
- **Keine Hilfe-Funktion für Einsatzkräfte** — Hilfsersuchen jenseits Verpflegung laufen über den polizeilichen Dienstweg; EB Digital ist **kein Notruf-Kanal** (Vision Z. 69, bewusste Abgrenzung).
- Offene Konzeptdetails laut Vision Z. 137: Pflichtfeld Beschreibung, automatische Priorisierung, Eskalations-Routing.

## 2. UX-Konzept (Betreuer-Seite)

1. **Auslösung:** dauerhaft sichtbarer Hilfe-Knopf in der Betreuer-PWA. Ein Tap öffnet eine Kategorie-Wahl mit genau zwei Optionen: **„Eigennot"** (persönliche Notlage) und **„Panne"** (Fahrzeug/Technik). Zweiter Tap löst aus. Kein Bestätigungs-Dialog im Eigennot-Pfad — Niederschwelligkeit schlägt Fehlauslösungs-Schutz, weil eine Rückzieh-Funktion existiert (Punkt 4).
2. **Beschreibung: optional, kein Pflichtfeld.** Begründung: Eigennot darf nicht an einer Tipp-Hürde scheitern (Stress, Handschuhe, Funkloch). Freitext kann beim Auslösen oder **nachträglich** ergänzt werden; ab Phase 6 kann der Disponent über den Chat nachfragen. UI-Hinweis am Freitextfeld: „Keine Namen Dritter eintragen" (PII-Disziplin).
3. **Standort-Mitgabe:** letzter bekannter GPS-Standort des Betreuer-Geräts wird automatisch angehängt (lat/lng + `accuracy_m`, nullable wenn nicht verfügbar) — der Disponent muss den Betreuer finden können, das ist der Kern-Nutzwert. Standortdaten unterliegen der 30-Tage-Anonymisierung (Vision Abschnitt 6).
4. **Rückziehen:** der Betreuer kann die eigene offene Meldung zurückziehen (Status `cancelled`) — Fehlauslösungs-Pfad statt Bestätigungs-Dialog.
5. **Quittungspfad zum Betreuer:** Statusanzeige in der PWA — „gesendet" → „**übernommen von <Disponent-Username>**" (WS-Event bei Acknowledge) → „erledigt". Bei fehlender Verbindung puffert die PWA die Meldung und sendet beim Reconnect (Offline-Detail in Phase 6 mit Spike-L-Service-Worker-Strategie).
6. **Kein-Notruf-Abgrenzung (Pflicht-UX):** statischer Hinweis im Hilfe-Dialog: „Bei akuter Gefahr: 110/112. Dieser Knopf erreicht nur den Disponenten." — operationalisiert die Vision-Abgrenzung.

## 3. UX-Konzept (Disponenten-Seite)

1. **Sichtbarkeit:** Hilfe-Meldungen erscheinen **top-priorisiert** im Disponenten-UI aller Disponenten des Einsatzes (gleichberechtigt, ADR-008 — kein Lead, kein Routing an Einzelpersonen), visuell hervorgehoben + akustisches Signal (UI-Detail Phase 6.2).
2. **Acknowledge:** ein Disponent drückt „Übernommen" → Status `acknowledged`, WS-Quittung an den Betreuer, Eintrag in `operation_audit_log`. Mehrere Disponenten sehen, wer übernommen hat (Audit-Transparenz statt Lock — konsistent mit ADR-008).
3. **Resolve:** „Erledigt" schließt die Meldung (`resolved`), Audit-Log-Eintrag.
4. **Eskalation: keine automatische Eskalation in Phase 1.** Es gibt niemanden, zu dem eskaliert werden könnte (einseitig zum Disponenten, kein Lead, Plattform-Admin nicht zuverlässig erreichbar). Stattdessen: **Re-Notification** — solange eine Meldung nach 2 Minuten un-acknowledged ist, wiederholt das Disponenten-UI das akustische/visuelle Signal (Client-seitig, kein Backend-Job). Intervall konfigurierbares UI-Detail Phase 6.
5. **Keine automatische Priorisierung** zwischen `eigennot`/`panne` über die Sortierung hinaus (Eigennot vor Panne, dann FIFO). Automatisches Priority-Scoring wäre Scheingenauigkeit bei zwei Kategorien.

## 4. Datenmodell-Skizze `help_alert` (Phase-6-Migration, ADR-pflichtig)

```
help_alert
- id                              UUID PK
- operation_id                    UUID FK → operation.id ON DELETE CASCADE
- carer_id                        UUID FK → carer.id (Username-Identität, kein Klarname — PII-Regel eingehalten)
- vehicle_id                      UUID FK → vehicle.id NULLABLE (Schicht-Kontext, falls zugeordnet)
- category                        TEXT CHECK ('emergency' | 'breakdown')
- description                     TEXT NULLABLE (Freitext, optional/nachreichbar; nie in Logs)
- location_lat / location_lng     NUMERIC NULLABLE   ┐ letzter bekannter Standort,
- location_accuracy_m             NUMERIC NULLABLE   ┘ unterliegt 30-Tage-Anonymisierung
- status                          TEXT CHECK ('open' | 'acknowledged' | 'resolved' | 'cancelled')
- acknowledged_by_dispatcher_id   UUID FK NULLABLE
- acknowledged_at / resolved_at / created_at  TIMESTAMPTZ
```

- **Persistenz vor Transport:** Meldung wird erst in PostgreSQL geschrieben, dann via S3-`RealtimePublisher` auf `operation.{operation_id}.help_alert` publiziert — Crash-/Reconnect-Fall verliert keine Meldung (Resilience-Vision: State-Erhaltung; Reconnect lädt offene Alerts per REST nach, Muster identisch zu `order_status` aus 4.4/4.5).
- **Retention:** `description` + `location_*` werden vom 30-Tage-Anonymisierungs-Job (Phase 6.5) genullt; Zähler `anzahl_hilfe_meldungen` im Aggregat (ADR-006) bleibt — keine ADR-006-Schema-Änderung nötig, Feld existiert bereits.
- **Audit:** `acknowledge`/`resolve` erzeugen `operation_audit_log`-Einträge (neue Action-Types `help_alert_acknowledged`, `help_alert_resolved`); das Auslösen selbst ist Betreuer-Aktion und wird über die Entity selbst nachvollziehbar (kein Doppel-Eintrag).

## 5. API- und WS-Skizze (Phase-6-Implementierung)

- `POST /api/operations/{id}/help-alerts` (Carer; REST statt WS-Client-Frame — konsistent mit Bestell-Pfad-Muster: schreiben via REST, Status via WS)
- `GET /api/operations/{id}/help-alerts?status=open` (Dispatcher; Reconnect-Nachladen)
- `POST /api/operations/{id}/help-alerts/{alert_id}/acknowledge` | `/resolve` (Dispatcher)
- `POST /api/operations/{id}/help-alerts/{alert_id}/cancel` (Carer, nur eigene offene Meldung)
- **WS-Payload `help_alert`** (S3-Schema, schließt die offene Frage aus Schritt 4.4): `{alert_id, operation_id, category, status, created_at, carer_username, vehicle_id?, has_description, location?{lat,lng,accuracy_m}, acknowledged_by_username?}` — kein Freitext im Push (PII-Disziplin im WS-Log-Pfad; Description holt das Disponenten-UI per REST).

## 6. Bewusste Nicht-Entscheidungen

- Kein externer Benachrichtigungskanal (SMS/Push außerhalb der PWA) — wäre neue externe Abhängigkeit, widerspricht „kein Notruf-Kanal".
- Keine Einsatzkraft-Hilfe-Funktion (Vision-Abgrenzung, unverändert).
- Kein automatisches Eskalations-Routing, keine Priorisierungs-Heuristik (Begründung Abschnitt 3.4/3.5).
