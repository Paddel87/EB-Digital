# Decisions

<!-- Begründete Entscheidungen und daraus abgeleitete Regeln.
     Drei Teile, in dieser Reihenfolge:
       Teil A: ADR-Übersicht (kompakte Tabelle, Reaktiv-Quote) – Pflichtlektüre bei Sessionstart
       Teil B: Architecture Decision Records (ADRs) – chronologisch, mit Tags – Detailteil
       Teil C: Entscheidungsregeln – wiederkehrende Muster, die aus ADRs hervorgehen
     Einträge werden nicht gelöscht oder verändert. Überholte ADRs werden durch
     neue ADRs ersetzt, die den alten Eintrag referenzieren.

     HINWEIS: Teil A steht bewusst zuerst. Bei Sessionstart liest Claude nur Teil A.
     Teil B (einzelne ADRs) wird nur bei konkretem Bedarf nachgelesen. -->

## Teil A: ADR-Übersicht

| ADR | Datum | Status | Klassifikation | Themen | Kategorie | Kurztitel |
|---|---|---|---|---|---|---|
| 001 | 2026-05-07 | Aktiv | STRATEGISCH | METHODIK | Methodik | Projektgrößen-Klassifikation Klasse G |
| 002 | 2026-05-07 | Aktiv | STRATEGISCH | STACK | Externe Abhängigkeiten | Stack-Wahl (FastAPI + SvelteKit + PostgreSQL + Valkey + Procrastinate) |
| 003 | 2026-05-07 | Aktiv | STRATEGISCH | METHODIK | Architekturänderungen | Architektur-Pattern Modular Monolith + drei SvelteKit-Frontends |
| 004 | 2026-05-07 | Aktiv | STRATEGISCH | SECURITY | Sicherheit und Datenschutz | Admin-Bootstrap-Flow als CLI-Befehl |
| 005 | 2026-05-07 | Aktiv | STRATEGISCH | SECURITY | Sicherheit und Datenschutz | AccessCode-Schema (6 Zeichen Crockford-Base32) |
| 006 | 2026-05-07 | Aktiv | STRATEGISCH | DATENMODELL | Datenmodelländerungen | Aggregations-Schema pro Operation, ohne Personen-Buckets |
| 007 | 2026-05-07 | Aktiv | STRATEGISCH | SCHNITTSTELLE | API-Vertragsänderungen | Datenexport asynchron via Procrastinate-Job-Tripel |
| 008 | 2026-05-07 | Aktiv | STRATEGISCH | MODUL | Architekturänderungen | Multi-Disponent ohne Lead, vollständiges Audit-Log |
| 009 | 2026-05-07 | Aktiv | STRATEGISCH | DATENMODELL | Datenmodelländerungen | Verbund-Reinterpretation V2 plus Phase-1-Invarianten I1–I5 |

### Reaktiv-Quote

- **Aktueller Wert:** 0 / 9 = 0 % `[REAKTIV]`-Anteil über die letzten 10 ADRs.
- **Schwellenwert (`project-context.md` Abschnitt 6, Klasse G):** 20 % `[REAKTIV]`-Anteil über die letzten 10 ADRs.
- **Bei Überschreitung:** STOPP, Reflexion in `fahrplan.md` ergänzen, prüfen ob Architektur-Refactoring nötig ist.

---

## Teil B: Architecture Decision Records

<!-- Detailteil. Einzelne ADRs werden nur bei konkretem Bedarf gelesen –
     z. B. wenn ein Schritt einen referenzierten ADR berührt. -->

### Format

Jeder ADR folgt diesem Schema. Keine Abweichung.

```
### ADR-NNN: [Kurztitel]

- **Datum:** YYYY-MM-DD
- **Status:** Aktiv | Überholt durch ADR-M | Verworfen
- **Tags:** [aus Tag-Liste unten]
- **Phasentyp-Kontext:** [ERKUNDUNG | UMSETZUNG | STABILISIERUNG | INITIALISIERUNG]
- **Reifegrad-Wirkung:** [welche Architektur-Bestandteile gehen durch diesen ADR auf welchen Reifegrad – falls zutreffend]
- **Kategorie:** [aus CLAUDE.md Abschnitt 4 oder "Methodik"]
- **Kontext:**
  [Problem, Rahmenbedingungen, was stand an, 2–5 Sätze]
- **Optionen:**
  - **A:** [Beschreibung] – Konsequenzen: [...]
  - **B:** [Beschreibung] – Konsequenzen: [...]
  - **C:** [falls relevant]
- **Entscheidung:** [Welche Option, warum]
- **Konsequenzen:**
  - [Welche Regeln folgen daraus]
  - [Welche Einschränkungen entstehen]
  - [Welche weiteren Entscheidungen werden dadurch nötig]
- **Abgeleitete Regel:** [Falls aus diesem ADR eine Regel für wiederkehrende Fälle entsteht, hier benennen und in Teil C aufnehmen]
```

### Tags

Jeder ADR trägt mindestens **einen Klassifikations-Tag** und beliebig viele Themen-Tags.

#### Klassifikations-Tags (genau einer pflichtig)

- `[STRATEGISCH]` – in der Konzeptphase oder Initialisierung getroffene Grundsatzentscheidung. Stack-Wahl, Architektur-Pattern, Modul-Schnitt.
- `[OPERATIV]` – während der Umsetzung getroffene Entscheidung im Rahmen geplanter Architektur. Bibliothekswahl innerhalb des Stacks, konkrete Schnittstellen-Spezifikation, Datenmodell-Detail.
- `[REAKTIV]` – Entscheidung, die nötig wurde, weil bei der Umsetzung etwas Unerwartetes auftrat. Workaround, Pivot, nachträgliche Architekturänderung. **Reaktive ADRs sind ein Indikator** – ihre Häufung in einem Modul deutet darauf hin, dass die Architektur dort nicht trägt.
- `[ERKENNTNIS]` – Entscheidung als Resultat einer Erkundungsphase oder eines Spikes. Validiert oder widerlegt eine vorherige Annahme.

#### Themen-Tags (optional, mehrere möglich)

- `[STACK]`, `[MODUL]`, `[SCHNITTSTELLE]`, `[DATENMODELL]`, `[SECURITY]`, `[PERFORMANCE]`, `[DEPLOYMENT]`, `[OBSERVABILITY]`, `[METHODIK]`

### Nummerierung

Durchgehend, keine Lücken. Auch verworfene oder überholte Einträge behalten ihre Nummer.

### Einträge

#### ADR-001: Projektgrößen-Klassifikation Klasse G

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[METHODIK]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** keine direkten Reifegrad-Beförderungen; legt aber den Reaktiv-Schwellenwert (20 %) und die Strukturwahl der Vorlagen fest.
- **Kategorie:** Methodik
- **Kontext:** Modus-2-Schritt 1 verlangt eine Stufe-1-Hypothese zur Projektgröße auf Basis der Vision und eine Stufe-2-Bestätigung am Ende des Architektur-Grobschnitts (CLAUDE.md Abschnitt 1B). Stufe-1-Hypothese auf Basis der Vision: Klasse G (mehrere Module, mehrere Stakeholder-Gruppen, NFR-Cluster). Stufe-2-Bestätigung am Ende von Schritt 4: 16 Komponenten, 5 zentrale externe Abhängigkeiten, 2 Sprachen, 2 Persistenzschichten, eine Compose-Einheit – siehe `architecture.md` Abschnitt 10.
- **Optionen:**
  - **A: Klasse K (Klein)** – Indikatoren: 1 Modul, 0–1 externe Abhängigkeiten, eine Sprache, kein Persistenzlayer. – Konsequenzen: stark reduziertes Vorlagen-Set, flache Schrittliste, keine Phasenstruktur. **Nicht zutreffend** (16 Komponenten, 4 Nutzergruppen).
  - **B: Klasse M (Mittel)** – Indikatoren: 2–5 Module, 2–5 Abhängigkeiten, eine Persistenzschicht. – Konsequenzen: Phasenstruktur 3–5 Phasen. **Nicht zutreffend** (Modul-Anzahl überschritten, NFR-Komplexität durch DSGVO/API-Budget/PWA/Resilience ist klassen-G-typisch).
  - **C: Klasse G (Groß)** – Indikatoren: 6+ Module, 5+ externe Abhängigkeiten, mehrere Sprachen, mehrere Persistenzschichten, NFR-Komplexität. – Konsequenzen: voller Vorlagen-Satz, 5–7 Phasen, Reaktiv-Schwellenwert 20 %, Index-Auslagerung von ADRs/Architektur bei Wachstum.
  - **D: Klasse V (Verteilt-Groß)** – Indikatoren: mehrere unabhängig deploybare Services, asynchrone Inter-Service-Kommunikation, Multi-Repo möglich. – Konsequenzen: Pflicht-Index aller Master-Dokumente, Service-spezifische Teil-Dokumente. **Nicht zutreffend** (eine Compose-Einheit, kein verteilter Lebenszyklus).
- **Entscheidung:** **Option C – Klasse G**. Vision-Hypothese und Architektur-Grobschnitt stimmen überein. Klasse V ist explizit ausgeschlossen, weil das System als ein Compose-Stack auf einem VPS läuft.
- **Konsequenzen:**
  - Vorlagen-Set Klasse G: alle sieben Pflicht-Dokumente in voller Form; `architecture.md` als Einzeldatei mit Auslagerungspfad nach `architecture-<modul>.md` bei Wachstum >500 Zeilen oder >5 Module mit eigenen Schnittstellen; `decisions.md` als Einzeldatei zunächst, Auslagerung nach `decisions/ADR-NNN.md` ab zweistelliger ADR-Anzahl.
  - **Reaktiv-Schwellenwert: 20 %** über die letzten 10 ADRs (`project-context.md` Abschnitt 6). Bei Überschreitung Reflexions-Schritt vor weiteren UMSETZUNG-Phasen.
  - Vorläufig-zu-Belastbar-Verhältnis: nach jeder UMSETZUNG-Phase mindestens ein VORLÄUFIG-Bestandteil der berührten Module auf BELASTBAR befördern, sonst Reflexion.
  - **Pflicht-ADR-Themen für Klasse V** (Service-Grenzen-Definition, Versionierungs-Strategie zwischen Services, Failure-Mode-Handling, Datenkonsistenz-Strategie, Observability-Standard) gelten **nicht**, weil Klasse G.
  - Reklassifikation rückwärts ist nicht vorgesehen; Reklassifikation vorwärts (G→V) erfordert eigenen `[STRATEGISCH] [METHODIK]`-ADR plus STABILISIERUNGS-Migrationsphase.
- **Abgeleitete Regel:** keine eigene Regel (Klassifikation wirkt strukturell, nicht über Code-Muster).

#### ADR-002: Stack-Wahl

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[STACK]` `[DEPLOYMENT]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** Bestätigt die in `architecture.md` Abschnitt 9 als `[BELASTBAR]` markierten Stack-fixen Bestandteile (REST/JSON-Grundmodus, WebSocket-Grundmodus, HTTP-Tile-Proxy-Routing, Procrastinate-Job-Engine, Backend-Multi-Architektur ARM/x86, PWA-Service-Worker offline-fähig, Coverage-Mindestwerte, Datenschutz-Constraints). Module bleiben `[VORLÄUFIG]`, weil die Implementierung noch aussteht.
- **Kategorie:** Externe Abhängigkeiten
- **Kontext:** Vision-Constraints (EU-Hosting, AGPLv3, kein US-Cloud-Hauptbetrieb, kein Tracking, Privacy-by-Design, PWA-only, Self-Hosting) plus Lasterwartung (50 Disponenten + 500 Einsatzkräfte) plus Rollen-Profile (Disponent stationär, Betreuer mobil mit Funklöchern, Einsatzkraft niederschwellig anonym) sind in Modus-2-Schritt 2 erarbeitet und in Modus-2-Schritt 2a am 2026-05-07 vollständig auf offiziellen Quellen verifiziert worden (Verifikations-Stempel `Verifiziert: 2026-05-07` für jede Komponente in `project-context.md` Abschnitt 3).
- **Optionen:**
  - **A: Django + DRF + Channels + Celery + Redis-Broker, React-Frontend.** – Konsequenzen: bewährter Mainstream-Stack, viele Entwickler verfügbar; aber Async-Bruch zwischen DRF und Channels, Celery-Overkill für PostgreSQL-basierte Job-Anforderung, Redis ist seit RSALv2/SSPL-Lizenzwechsel ausgeschlossen, React-Bundle größer als für die schlanke Einsatzkraft-PWA nötig.
  - **B: Node-Backend (NestJS) + Prisma + BullMQ + Next.js.** – Konsequenzen: sprachhomogen Backend+Frontend, sehr gute PWA-Unterstützung; aber Prisma + Multi-Tenant-Patterns sind bei mandantenstarken Modellen aufwendig, BullMQ braucht Redis (siehe oben), Threat-Modell für Async-Node bei Long-Running-Connections (WebSocket + Procrastinate-Aufgaben) hat in vergleichbaren Projekten Reibung erzeugt.
  - **C: FastAPI + SQLAlchemy + Alembic + Pydantic + httpx + Procrastinate (Backend), Svelte 5/SvelteKit 2 + Vite 8 + Workbox + MapLibre GL JS (Frontends), PostgreSQL 17 + Valkey 8 (Datenhaltung), nginx (Tile-Proxy) + Caddy (Reverse-Proxy), Docker Compose v5 + Hetzner CCX-VPS in Deutschland (Infrastruktur), uv + pnpm (Package-Manager), AGPLv3 (Projektlizenz) – verifizierter Stand vom 2026-05-07.** – Konsequenzen: vollständig async-native im Backend, kompakte Frontend-Bibliothek mit klaren PWA-Pfaden, Procrastinate nutzt PostgreSQL als Backing (ACID-Job-State Teil der DB-Backups), Valkey als Linux-Foundation-Fork löst die Redis-Lizenzproblematik, MapLibre löst die Mapbox-Lizenzproblematik. Höhere Eigenleistung im Auth-Bereich (kein FastAPI-Users), kompensiert durch externe Security-Review vor Produktivstart.
- **Entscheidung:** **Option C**. Erfüllt alle harten Vision-Constraints, ist intern konsistent (async durchgängig), reduziert externe Bindungen (kein Redis, keine Mapbox, keine US-Cloud, keine SaaS-Auth), behält Lizenz-Disziplin (AGPLv3 + permissive Dependencies), und passt zur Lasterwartung ohne Skalierungs-Vorabwurf.
- **Konsequenzen:**
  - **Versionsdisziplin:** jede in `project-context.md` Abschnitt 3 gelistete Version trägt Pflicht-Vermerk `Verifiziert: YYYY-MM-DD`. Major-Updates erfordern erneute Verifikation und einen ADR. Minor- und Patch-Updates sind freigabefrei (CLAUDE.md Abschnitt 4 Punkt 3, Major-Vorbehalt explizit dort).
  - **Bewusste Versions-Zurückhaltung an zwei Stellen:** PostgreSQL **17.9 statt 18** und mypy **1.20.2 statt 2.0.x** – „Stabilität vor Aktualität". Beide Punkte sind in `project-context.md` Abschnitt 3 als solche dokumentiert.
  - **Eigener Auth-Code statt FastAPI-Users**, basierend auf argon2-cffi + itsdangerous + Starlette-SessionMiddleware. Begleitende Pflichten: Auth-Modul-Coverage ≥ 95 %, externe Security-Review vor Produktivstart (siehe `project-context.md` Abschnitt 7 plus folgende ADRs in einer späteren Phase).
  - **CI-Plattform GitHub Actions**, Workflow-Splitting `ci.yml` / `security.yml` / `release.yml` für Klasse G; Pflicht-Pinning auf Patch-Tag oder Commit-Hash für `pnpm/action-setup` und `astral-sh/setup-uv` (Immutable-Tag-Trend).
  - **Explizite Ausschlüsse** sind in `project-context.md` Abschnitt 3 „Explizit nicht erlaubt" geführt: keine US-Cloud als Hauptbetrieb, kein Redis, keine Mapbox, keine GPL/LGPL-Backend-Dependencies, keine native Mobile-Toolchains, keine SaaS-Auth-Provider, kein FastAPI-Users/passlib, kein Taskiq/ARQ/Celery, keine Google-Maps/-Routing/-Geocoding, keine ORM-Schnellschüsse, keine Behörden-IT-Anschlüsse, kein Tracking.
  - **Externe API-Budget-Disziplin:** ~50 €/Monat für MapTiler+TomTom über alle aktiven Einsatztage (`project-context.md` Abschnitt 6 Performance) – `backend/geo` führt Verbrauchszähler.
- **Abgeleitete Regel:** Regel-001 (Versionsdisziplin) und Regel-002 (Stack-Ausschlüsse beachten) – siehe Teil C.

#### ADR-003: Architektur-Pattern Modular Monolith + drei SvelteKit-Frontends

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[METHODIK]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** fixiert die Pattern-**Wahl** als strategische Entscheidung. Tragfähigkeit (Last, Modulgrenzen-Disziplin) bleibt `[VORLÄUFIG]` bis zur ersten UMSETZUNG-Phase mit bestandenem Funktions-/Last-Test (siehe `architecture.md` Abschnitt 9).
- **Kategorie:** Architekturänderungen
- **Kontext:** Aus Vision und Klärungs-Session ergeben sich vier Nutzergruppen (Plattform-Admin, Disponent, Betreuer, anonyme Einsatzkraft) mit deutlich unterschiedlichen Berechtigungs-Modellen, Last-Profilen und Service-Worker-Anforderungen. Backend-Module sind dagegen domänenintern (Mandant, Operation, Order, Fleet, Geo, Realtime, Retention, Export, Resilience) ohne erkennbar verteilten Lebenszyklus. Lasterwartung 50/500 trägt einen Monolithen.
- **Optionen:**
  - **A: Monolith Backend + Monolith Frontend.** – Konsequenzen: einfachster Schnitt, aber Service-Worker-Einsatz und mobile Last-Profile schwer auszubalancieren; Disponent-Tablet und Einsatzkraft-Smartphone müssten dasselbe Bundle laden.
  - **B: Modular Monolith Backend + drei SvelteKit-Frontends + 2 Proxies (Tile-Proxy, Reverse-Proxy).** – Konsequenzen: Backend bleibt schlank deploybar, Modulgrenzen sind Pflicht und Architekturbruch verboten (CLAUDE.md Abschnitt 6); Frontends können je nach Rolle ihre PWA-Strategie unabhängig wählen (Offline-Pufferung Betreuer vs. anonymer Single-Use Einsatzkraft).
  - **C: Microservices pro Domäne.** – Konsequenzen: hohe Betriebs- und Test-Komplexität, asynchrone Inter-Service-Kommunikation müsste neu gebaut werden, Multi-Repo-Pflege; **nicht gerechtfertigt** durch Last- oder Stakeholder-Profil. Würde auch der Klassifikation Klasse V entsprechen, was per ADR-001 bewusst ausgeschlossen ist.
- **Entscheidung:** **Option B – Modular Monolith Backend + drei SvelteKit-Frontends + Tile-Proxy + Reverse-Proxy**. Liefert klare Modul-Kommunikations-Disziplin (Modul-Karte in `architecture.md` Abschnitt 2 mit erlaubten Beziehungen) ohne Microservices-Overhead.
- **Konsequenzen:**
  - **Modulgrenzen sind verbindlich.** Aufrufe Modul A → Modul B nur über die in `architecture.md` Abschnitt 4 spezifizierten Schnittstellen. Direktzugriff auf interne Strukturen anderer Module ist Architekturbruch (CLAUDE.md Abschnitt 6).
  - **Frontend-Backend-Kommunikation ausschließlich** REST über `/api`-Präfix oder WebSocket über `/ws`-Präfix.
  - **Externe Karten-/Routing-Aufrufe** ausschließlich über `infra/tile-proxy` (API-Keys Backend-seitig, Budget-Disziplin zentral).
  - **Drei Frontend-Bundles** mit eigener `pnpm`-Workspace-Struktur (Frontend-Trio in `apps/`-Layout). `frontend-disponent`, `frontend-betreuer`, `frontend-einsatzkraft` sind verschiedene PWA-Profile mit unterschiedlichen Service-Worker-Strategien.
  - **Reklassifikation in Microservices** ist freigabepflichtig (Architekturänderung) und würde Reklassifikation auf Klasse V nach sich ziehen.
- **Abgeleitete Regel:** Regel-003 (Modulgrenzen-Pflicht) und Regel-004 (kein direkter Frontend↔Externer-Service-Aufruf) – siehe Teil C.

#### ADR-004: Admin-Bootstrap-Flow als CLI-Befehl

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[SECURITY]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt Schnittstelle S1 (Admin-Bootstrap-CLI in `architecture.md` Abschnitt 4) und Modul-Verantwortung `backend/auth` strategisch fest; Schnittstelle und Modul bleiben `[VORLÄUFIG]` bis zur UMSETZUNG.
- **Kategorie:** Sicherheit und Datenschutz
- **Kontext:** Der allererste Plattform-Administrator muss angelegt werden, ohne dass eine andere Plattform-Admin-Identität bereits existiert. Klassisches Henne-Ei-Problem. Geklärt am 2026-05-07 in der Klärungs-Session zu `project-context.md` Abschnitt 11 Frage A.
- **Optionen:**
  - **A: ENV-Variable-Bootstrap** (`EB_ADMIN_PASSWORD=…` beim Start des Containers). – Konsequenzen: Klartext-Passwort in `.env`-Datei, im `docker compose`-Output, in Backups und in Container-Logs. Verstößt gegen Datenschutz-Constraint „keine sensiblen Daten in Logs" (`project-context.md` Abschnitt 6).
  - **B: Web-Setup-Wizard** (erste UI-Seite legt Admin-Account an). – Konsequenzen: Race-Condition-Risiko (Angreifer könnte schneller sein als der Betreiber), zwingt sehr früh Web-Code mit Sonder-Endpunkt und ggf. Sonder-Schalter „bootstrap_done?".
  - **C: Hybrid-Setup-Link via Server-Log** (Server schreibt zur Boot-Zeit einmaligen Link in Container-Log). – Konsequenzen: Konflikt mit Datenschutz-Constraint „keine sensiblen Daten in Logs"; Logs werden ggf. zentral aggregiert oder eingesehen, der Link wäre dort als Sekundär-Faktor sichtbar.
  - **D: CLI-Befehl im Backend-Container** (`docker compose exec backend python -m eb_digital admin create`, Username als Argument, Passwort interaktiv via `getpass`). – Konsequenzen: kein Klartext-Passwort in ENV/Compose-File/Logs/Backups; jederzeit nutzbar (kein Single-Use-Bootstrap), legt auch nachträglich weitere Plattform-Admins an; Voraussetzung ist SSH-Zugriff auf den Host plus Docker-Rechte – gleiches Risikoniveau wie der Betrieb des Hosts an sich.
- **Entscheidung:** **Option D – CLI-Befehl, jederzeit nutzbar**. Niedrigste Angriffsfläche, kein Web-Sonderfall, hält die offene Skalierungs-Frage „zentraler vs. mehrere Plattform-Admins" (`project-context.md` Abschnitt 11 Punkt „Administrator-Architektur") ohne Architekturzwang offen.
- **Konsequenzen:**
  - **CLI-Befehl** liegt in `backend/auth` als Untermodul `eb_digital.admin` mit Argumenten `--username` (positional/required) und Passwort-Eingabe via `getpass` (kein `--password` als Argument, kein Echo).
  - **Hashing** mit Argon2id über argon2-cffi mit Library-Default-Parametern (`project-context.md` Abschnitt 6 Sicherheit).
  - **Mehrfach-Nutzbarkeit:** kein „bootstrap_done"-Flag; weitere Admins können jederzeit per CLI angelegt werden, ohne dass eine bestehende Web-Auth-Identität nötig ist. Das ist als Komfort gewollt, **nicht** als Backdoor – Voraussetzung bleibt SSH+Docker-Zugriff.
  - **Audit:** jeder per CLI angelegte Admin-Account wird in einem Audit-Log-Eintrag (Tabelle dafür wird in einer späteren UMSETZUNG-Phase definiert) mit Zeitpunkt, Username und Erstellungs-Methode `bootstrap_cli` festgehalten – kein Klartext-Passwort.
  - **Kein Web-Endpunkt** für Admin-Erstellung in Phase 1.
- **Abgeleitete Regel:** Regel-005 (Sensible Bootstrap-Operationen über CLI, nicht Web) – siehe Teil C.

#### ADR-005: AccessCode-Schema für anonyme Einsatzkraft-Sessions

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[SECURITY]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt Schnittstelle S2 (Anonymous Session API) und Modul-Verantwortung `backend/auth_anonymous` strategisch fest; Schnittstelle und Modul bleiben `[VORLÄUFIG]` bis zur UMSETZUNG.
- **Kategorie:** Sicherheit und Datenschutz
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage B. Die Einsatzkraft-PWA wird primär über eine pro Operation neu erzeugte URL mit kryptographischem Token erreicht. Optional kann der Disponent zusätzlich einen AccessCode aktivieren – Format, Wiederverwendbarkeit und Toggle-Verhalten waren offen.
- **Optionen:**
  - **A: 4-stellige PIN.** – Konsequenzen: 10⁴ ≈ 10 000 Möglichkeiten – Brute-Force-Reserve zu gering, insbesondere bei verteilter Belastung über mehrere Sessions.
  - **B: Single-Use-Codes pro Einsatzkraft** (jeder Einsatzkraft wird ein eigener Code zugewiesen). – Konsequenzen: erfordert eine zentrale Verteilliste der Einsatzkräfte – widerspricht „kein Klarnamen, anonyme Sessions" und scheitert an der realen Verteilungslogistik im Einsatz (Code-Übergabe „außerhalb des Systems").
  - **C: 6 Zeichen Crockford-Base32** (Großbuchstaben + Ziffern, ohne O/0/I/1/L), ein Code pro Operation, von beliebig vielen Einsatzkräften nutzbar, läuft mit Operation-Ende ab. – Konsequenzen: 32⁶ ≈ 1 073 000 000 Möglichkeiten, gut sprech- und merkbar, niedrigschwellig verteilbar (Ansage, Aushang, QR), kein Personen-Tracking.
- **Entscheidung:** **Option C – 6 Zeichen Crockford-Base32**.
- **Konsequenzen:**
  - **Format:** 6 Zeichen, Crockford-Base32-Alphabet (Großbuchstaben + Ziffern, ohne O/0/I/1/L), z. B. `X7K3PQ`. Kein Padding, kein Mixed-Case.
  - **Wiederverwendbarkeit:** **ein** Code pro Operation, von beliebig vielen Einsatzkräften nutzbar, läuft mit Operation-Ende ab.
  - **Aktivierung während laufender Operation:** wirkt **nur auf neu startende Sessions / neue Bestellungen**. Bestehende anonyme Sessions, die vor Aktivierung gestartet sind, bestellen weiter ohne Code bis zum Session-Ablauf.
  - **Disponenten-UI:** Anzeige des Codes plus Copy-to-Clipboard plus QR-Code (rendert die kombinierte Einsatz-URL inklusive Code). Druck/PDF-Export ist **nicht** Phase 1.
  - **Rotation:** **keine** systemseitige Rotation in Phase 1. Bei Verdacht auf Kompromittierung beendet der Disponent die Operation und eröffnet eine neue – URL und Code werden gemeinsam erneuert. Eine spätere Rotate-Funktion (Stabilisierungs-Erweiterung) ist nachrüstbar.
  - **Backend-Verifikation:** AccessCode wird in der Operation-Tabelle als Hash + Salt gespeichert, **nicht** im Klartext. Bei Bestellung: Konstantzeit-Vergleich.
  - **Logging-Disziplin:** weder Klartext-Code noch Hash in Logs. In Logs erscheint nur das boolesche Ergebnis „validierung erfolgreich/fehlgeschlagen".
- **Abgeleitete Regel:** Regel-006 (AccessCode-Hashing-Pflicht) und Regel-007 (AccessCode-Toggle wirkt nur auf neue Sessions) – siehe Teil C.

#### ADR-006: Aggregations-Schema pro Operation

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[DATENMODELL]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt das Aggregat-Datenmodell `operation_aggregate` (`architecture.md` Abschnitt 7) sowie Schnittstelle S5 (Operations → Retention Aggregat-Trigger, `architecture.md` Abschnitt 4) strategisch fest; Datenmodell und Schnittstelle bleiben `[VORLÄUFIG]` bis zur UMSETZUNG `backend/retention`.
- **Kategorie:** Datenmodelländerungen
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage C. Vision Abschnitt 6 verlangt: aggregierte Statistiken bleiben dauerhaft, individuelle Bestell- und Standortdaten 30 Tage nach Operation-Ende. Offen war, welche Felder vor Anonymisierung in welche Aggregat-Form überführt werden, ob Geometrien gespeichert werden, ob Personen-Buckets erlaubt sind.
- **Optionen:**
  - **A: Pseudonyme Personen-Hashes im Aggregat** (Hash pro Disponent, Betreuer, Einsatzkraft mit Aktivitäts-Zähler). – Konsequenzen: Re-Identifikations-Risiko bei kleinen Mandanten (DPolG Bremen ist klein); selbst bei Salz-Hash mit langer Lebensdauer entstehen Quasi-Identifikatoren über Aktivitätsmuster. Verstößt gegen den Geist des Datenschutz-Constraints.
  - **B: Festes Metriken-Set ohne Personen-Buckets**, Aggregation pro Operation, ein finaler Snapshot beim Operation-Ende. – Konsequenzen: keine Re-Identifikation möglich; Aggregat ist ein einfacher Zähler-Datensatz.
  - **C: Dauerhafte Geometrie der Einsatzräume** (Polygon plus Mittelpunkt). – Konsequenzen: visuell wertvoll, aber Geometrie bei wenigen Operationen pro Mandant ist über die Zeit ein Quasi-Identifikator, und MapTiler-Lizenzfragen für persistente Geometrie-Snapshots wären zusätzlich zu klären.
  - **D: Stadt-/Region-Label als String** (vom Disponenten beim Eröffnen gesetzt, z. B. „Bremen Innenstadt"). – Konsequenzen: ausreichend für Rückblicke und Reports, kein Geometrie-Persistenz-Aufwand, kein Re-Identifikations-Vektor.
- **Entscheidung:** **Kombination B + D**. Aggregat pro Operation als finaler Snapshot beim Operation-Ende, festes Metriken-Set ohne Personen-Buckets, Stadt-Label statt Geometrie.
- **Konsequenzen:**
  - **Aggregations-Einheit:** ein Eintrag in `operation_aggregate` pro Operation, geschrieben **beim Operation-Ende** als finaler Snapshot. Übergreifende Roll-ups (pro Mandant, pro Tag/Monat) per SQL-Sum aus dieser Tabelle ableitbar.
  - **Metriken-Set pro Eintrag** (finale Liste, in dieser Reihenfolge im Schema):
    - `tenant_id` (in Phase 1 genau eine, siehe Invariante I4 in ADR-009)
    - `operation_id`
    - `start_at`, `end_at` (UTC, mit `zoneinfo`)
    - `area_count` (Anzahl Einsatzräume)
    - `order_count`, `order_assignment_count`, `cancellation_count`, `bundling_count`
    - `supply_transporter_mode_changes` als JSON-Map mit Counter pro Modus
    - `access_code_activated` (boolean)
    - `route_override_count`
    - `help_request_count`
    - `total_drive_distance_km` (gerundet auf 1 km)
    - `peak_active_vehicles`, `peak_active_dispatchers`
    - `area_label` (String, vom Disponenten gesetzt, z. B. „Bremen Innenstadt")
  - **Keine Personen-Buckets** (kein Pseudonym-Hash für Disponenten/Betreuer/Einsatzkräfte). Datenbasis für die `peak_*`- und `count_*`-Felder ist die Audit-Log-Tabelle aus ADR-008 plus die Operations-/Order-Tabellen.
  - **Zugriff:** Mandanten-Disponenten sehen Aggregate **ihres eigenen Mandanten**; Plattform-Administrator sieht alle. Keine Cross-Mandanten-Veröffentlichung in Phase 1.
  - **Anonymisierungs-Reihenfolge:** Aggregat-Schreibung **beim Operation-Ende** (sofort, synchron im Operation-Ende-Workflow). Anonymisierungs-Job läuft entkoppelt 30 Tage später und löscht nur noch Detail-Daten. Damit besteht keine Race-Bedingung zwischen Anonymisierung und Aggregat-Berechnung.
  - **Phase-1-Invariante I4** (siehe ADR-009): `operation_aggregate.tenant_id` ist in Phase 1 genau eine Mandanten-ID. Spätere Verbund-Phase erweitert das Schema additiv (mehrere verarbeitende Mandanten pro Aggregat oder Quell-Markierung).
- **Abgeleitete Regel:** Regel-008 (Aggregat-Schreibung sofort beim Operation-Ende) und Regel-009 (kein Personen-Bucket im Aggregat) – siehe Teil C.

#### ADR-007: Datenexport asynchron via Procrastinate

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[SCHNITTSTELLE]` `[DATENMODELL]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt Schnittstelle S6 (Tenant Data Export, `architecture.md` Abschnitt 4) und das Datenmodell des `export_job`-Eintrags strategisch fest; Schnittstelle bleibt `[VORLÄUFIG]` bis zur UMSETZUNG `backend/export`.
- **Kategorie:** API-Vertragsänderungen
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage D. DSGVO Art. 20 (Datenübertragbarkeit) und Vision-Constraint „Mandanten-Datenexport" verlangen einen Self-Service-Export. Offen war Verfahren (synchron/asynchron), Format, Inhalt, Auslöser, Lebensdauer.
- **Optionen:**
  - **A: Synchron-Einzelendpunkt** (`GET /api/tenants/{id}/export` als Single-Request mit ZIP-Stream). – Konsequenzen: bei großen Mandanten Worker-Block-Risiko (Procrastinate-Worker oder API-Worker), Kollision mit p95 < 300 ms-Ziel, Timeouts auf Reverse-Proxy- oder Browser-Seite.
  - **B: Asynchron via Procrastinate-Job-Tripel.** – Konsequenzen: Job-Erzeugung antwortet sofort mit Job-ID, Status-Polling über separaten Endpunkt, Download-Endpunkt liefert das fertige ZIP. Nutzt vorhandenen Procrastinate-Stack ohne Zusatz-Komponente.
  - **C: Mit Karten-Snapshots im Export** (Tile-Captures der Operation-Räume). – Konsequenzen: erhöht Datenvolumen, MapTiler-Lizenz-Klärungsbedarf für persistente Tile-Speicherung, Phase-1-Komplexität nicht gerechtfertigt.
- **Entscheidung:** **Option B**, **ohne** Karten-Snapshots (Option C verworfen).
- **Konsequenzen:**
  - **API-Tripel:**
    - `POST /api/tenants/{id}/export` startet Procrastinate-Job, liefert `{job_id, status: "queued"}`.
    - `GET /api/tenants/{id}/export/{job_id}` liefert Job-Status (`queued`, `running`, `done`, `failed`).
    - `GET /api/tenants/{id}/export/{job_id}/download` liefert das fertige ZIP, sobald `status = "done"`.
  - **Format:** ZIP mit JSON-Datei pro Tabelle plus `manifest.json` (Schema-Version, Export-Datum UTC, Mandanten-ID, Tabellen-Liste mit Datensatzzahl).
  - **Inhalt:** vollständige Mandanten-Daten – Stammdaten, Disponenten-/Betreuer-Accounts ohne Passwort-Hashes, Fahrzeug-Stammdaten plus Beladungs-Historie, mandantenspezifischer Artikelkatalog, Operations, Bestellungen plus Fahraufträge der letzten 30 Tage detailliert (danach anonymisiert), Aggregations-Tabelle. Keine Karten-Snapshots, keine externen Anhänge, keine Klartext-AccessCodes.
  - **Auslöser:** Self-Service durch Disponent / Mandanten-Admin-Disponent im **eigenen** Mandanten; Plattform-Administrator kann jeden Mandanten exportieren (Override-Pfad).
  - **Lebensdauer:** fertiges ZIP unter `/var/eb-digital/exports/{tenant_id}/{job_id}.zip`, **7 Tage** abrufbar (mehrfacher Download), danach Cleanup-Job (zweiter Procrastinate-Job, läuft täglich).
  - **Phase-1-Invariante I5** (siehe ADR-009): Datenexport ist in Phase 1 auf `role='owner'` reduziert; spätere Verbund-Aufträge werden als geteilte Datensätze mit Quell-Markierung ergänzt.
  - **Authentifizierung:** alle drei Endpunkte verlangen Disponenten-Session (Self-Service) oder Plattform-Admin-Session (Override). Anonyme Sessions haben keinen Zugriff.
- **Abgeleitete Regel:** Regel-010 (Mandanten-übergreifende Datenoperationen ausschließlich asynchron via Procrastinate) – siehe Teil C.

#### ADR-008: Multi-Disponent ohne Lead, vollständiges Audit-Log

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[MODUL]` `[DATENMODELL]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt das Verhaltens-Modell von `backend/operations` und das Datenmodell `operation_audit_log` (`architecture.md` Abschnitt 7) strategisch fest; Modul und Schnittstellen bleiben `[VORLÄUFIG]` bis zur UMSETZUNG.
- **Kategorie:** Architekturänderungen
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage E. Mehrere Disponenten können gleichzeitig an einer Operation arbeiten. Frage war: gibt es einen Lead-Disponenten mit Sonderrechten für destruktive Aktionen, oder sind alle gleichberechtigt?
- **Optionen:**
  - **A: Lead-Modell mit Eröffner-Default.** Der Disponent, der die Operation eröffnet, ist Lead; nur er darf die Operation beenden, AccessCode toggeln, Operation-Räume umgestalten, Versorgungs-Transporter-Modi wechseln. – Konsequenzen: Schutz gegen versehentliche destruktive Aktionen; aber: Eskalations-Pfad nötig, falls Lead-Disponent nicht erreichbar (Schicht-Ende, Funkloch). Plattform-Administrator als Eskalations-Pfad ist laut Klärungs-Session nicht zuverlässig erreichbar.
  - **B: Kein Lead-Modell, alle Disponenten am Operation gleichberechtigt**, einschließlich destruktiver Aktionen. UX-Bestätigungs-Dialog plus vollständiges Audit-Log ersetzen den Lead-Schutz durch retrospektive Nachvollziehbarkeit. – Konsequenzen: Disponenten bleiben jederzeit handlungsfähig; Schaden durch versehentliche Aktion wird durch Bestätigungs-Dialog minimiert; Verantwortlichkeit über Audit-Log auflösbar.
- **Entscheidung:** **Option B – kein Lead-Modell**. Begründung Patrick: Plattform-Administrator nicht zuverlässig erreichbar, Disponenten haben den operativen Überblick und sollen ohne Eskalations-Hürde handlungsfähig sein. Schutz gegen Großschäden trägt der Bestätigungs-Dialog plus retrospektive Nachvollziehbarkeit über das Audit-Log.
- **Konsequenzen:**
  - **Berechtigungs-Modell `backend/operations`:** alle Disponenten, die laut `operation_tenant_participation` (siehe ADR-009) am Operation teilnehmen, dürfen **alle** Aktionen ausführen, einschließlich der destruktiven (Operation beenden, AccessCode toggeln, Operation-Raum-Geometrie ändern, Versorgungs-Transporter-Modus wechseln).
  - **`operation_audit_log`-Tabelle:** jede destruktive oder konfigurierende Aktion erzeugt einen Eintrag mit `actor_dispatcher_id`, `action_type`, `at` (UTC), `target_kind` und `target_id` (z. B. `operation`, `operation_area`, `vehicle`), plus `payload` (JSON, Aktion-spezifische Detail-Daten ohne PII).
  - **UX-Schutz:** Bestätigungs-Dialog im `frontend-disponent` vor jeder destruktiven Aktion. Implementierungs-Detail im Frontend, kein Architektur-Block.
  - **Sichtbarkeit Audit-Log:** im Disponenten-UI für **alle** Disponenten am Operation und für den Plattform-Administrator. Kein Aggregations-Zugriff durch andere Mandanten.
  - **Audit-Log liefert Datenbasis** für die `peak_active_*`- und `*_count`-Felder im Aggregat (siehe ADR-006).
  - **Retention Audit-Log:** unterliegt der 30-Tage-Anonymisierung wie andere Detail-Daten der Operation; nach Anonymisierung bleibt nur die Aggregat-Spur (siehe ADR-006).
- **Abgeleitete Regel:** Regel-011 (Audit-Log-Pflicht bei destruktiven/konfigurierenden Operations-Aktionen) und Regel-012 (Confirmation-Dialog vor destruktiven Aktionen im Frontend) – siehe Teil C.

#### ADR-009: Verbund-Reinterpretation V2 plus Phase-1-Invarianten I1–I5

- **Datum:** 2026-05-07
- **Status:** Aktiv
- **Tags:** `[STRATEGISCH]` `[DATENMODELL]`
- **Phasentyp-Kontext:** INITIALISIERUNG
- **Reifegrad-Wirkung:** legt fünf Datenmodell-Invarianten I1–I5 (`architecture.md` Abschnitt 9) strategisch fest, die Phase 1 architektonisch verbund-tauglich halten. Invarianten bleiben `[VORLÄUFIG]` bis zur UMSETZUNG der jeweiligen Module.
- **Kategorie:** Datenmodelländerungen
- **Kontext:** Geklärt am 2026-05-07 zu `project-context.md` Abschnitt 11 Frage F. Vision postuliert die strikte Trennung der Anbieterseiten (jeder Mandant verwaltet eigene Disponenten, Betreuer, Fahrzeuge, Aufträge). Solidarische Praxis (ein Mandant versorgt auch fremde Einsatzkräfte) ist über die anonyme Bezieherseite gelöst. Realer Bedarf (zwei Mandanten an derselben Großlage mit gemeinsamem Auftragspool) widerspricht der Default-Trennung. Frage: Vision-Pivot oder Reinterpretation, sofortige Implementierung oder Phase-1-Vorbereitung?
- **Optionen:**
  - **V1: Echter Konflikt mit der Vision** (Verbund-Modus ist nicht mit Anbieterseiten-Trennung vereinbar; Vision müsste angepasst werden, oder Verbund-Modus muss verworfen werden). – Konsequenzen: zwingt Vision-Pivot-Diskussion oder verschließt einen real geforderten Anwendungsfall.
  - **V2: Reinterpretation als opt-in-Erweiterung** mit beidseitigem Konsens. Solange beide Mandanten ausdrücklich zustimmen, ist die Default-Trennung nicht verletzt, sondern bewusst delegiert. – Konsequenzen: Vision bleibt unangetastet, Anwendungsfall wird ermöglicht.
  - **V3: Vision-Pivot** (Anbieterseiten-Trennung wird als Default abgeschafft). – Konsequenzen: tiefer Architektur-Eingriff, Constraint-Bruch, nicht gerechtfertigt durch den realen Bedarf eines opt-in-Falls.
  - **P1: Sofort implementieren in Phase 1.** – Konsequenzen: erhebliche Phase-1-Komplexität (Cross-Mandanten-UI, Vertrags-Akzeptanz, Auflösung, Statistik-Zuordnung); verzögert die DPolG-Bremen-Solo-Phase ohne Mehrwert für den Initial-Mandanten.
  - **P2: Phase 1 architektonisch verbund-tauglich vorbereiten**, eigentliche Verbund-Funktionalität in späterer UMSETZUNG-Phase mit ERKUNDUNG-Vorlauf. – Konsequenzen: Phase 1 bleibt klein, spätere Erweiterung ohne Tabellen-Refactoring möglich, wenn die Datenmodell-Invarianten konsequent eingehalten werden.
  - **P3: Verbund-Modus gar nicht implementieren.** – Konsequenzen: schließt einen real geforderten Anwendungsfall aus.
- **Entscheidung:** **V2 + P2 – Reinterpretation als opt-in-Erweiterung mit beidseitigem Konsens, in Phase 1 architektonisch vorbereitet, eigentliche Funktionalität in späterer UMSETZUNG-Phase**.
- **Konsequenzen – fünf Phase-1-Invarianten** (additive Einführbarkeit ohne Tabellen-Refactoring):
  - **I1:** Operation↔Mandant über die Verknüpfungstabelle `operation_tenant_participation(operation_id, tenant_id, role)`. In Phase 1 genau ein Eintrag pro Operation mit `role='owner'`. **Kein direkter `operation.tenant_id`-Foreign-Key.**
  - **I2:** Berechtigungs-Filter formuliert als „Operations, an denen mein Mandant teilnimmt" statt „Operations meines Mandanten". In Phase 1 verhaltensgleich, in späterer Verbund-Phase additiv erweiterbar.
  - **I3:** Fahrzeug-Zuweisung in `backend/operations.assign_vehicle()` prüft **Operations-Kontext** (Teilnahme über `operation_tenant_participation`), **nicht** Mandanten-ID-Match.
  - **I4:** `operation_aggregate` (siehe ADR-006) bleibt in Phase 1 mit genau **einer** `tenant_id` pro Eintrag. Spätere Schema-Migration auf „verarbeitende Mandanten" ist im Architektur-Dokument als bekannte spätere Aufgabe vermerkt – keine versteckte technische Schuld.
  - **I5:** Datenexport (siehe ADR-007) bleibt in Phase 1 auf `role='owner'` reduziert. Spätere Verbund-Aufträge werden als geteilte Datensätze mit Quell-Markierung ergänzt.
- **Konsequenzen – Modul-Zuordnung der späteren Verbund-Erweiterung:**
  - **Kein eigenes `backend/verbund`-Modul in Phase 1.** Spätere Funktionalität als Erweiterung von `backend/tenants` (Verbund-Verträge: Initiative, Akzeptanz, Auflösung) und `backend/operations` (Cross-Mandanten-Disposition, gemeinsame Operations-URL).
  - Falls bei der späteren Implementierung Modulgrenzen unscharf werden, wird per ADR ein eigenes Modul ausgegliedert.
- **Konsequenzen – Fahrplan:**
  - Spätere UMSETZUNG-Phase „Verbund-Modus für parallele Mandanten-Großlagen" mit ERKUNDUNG-Vorlauf (Stakeholder-Klärung mit zwei Mandanten, Berechtigungs-Modell-Verfeinerung, Statistik-Zuordnung) wird in Modus-2-Schritt 6 in `fahrplan.md` als spätere Phase aufgenommen.
- **Abgeleitete Regel:** Regel-013 (Operation↔Mandant ausschließlich über `operation_tenant_participation`) und Regel-014 (Berechtigungs-Filter als Teilnahme-Filter formulieren) – siehe Teil C.

---

## Teil C: Entscheidungsregeln

<!-- Regeln für wiederkehrende Fälle, damit die KI in ähnlichen Situationen
     konsistent und ohne Rückfrage handeln kann.
     Jede Regel verweist auf den ADR, aus dem sie entstanden ist. -->

### Format

```
### Regel-NNN: [Kurztitel]

- **Herkunft:** ADR-[Nr.]
- **Gilt für:** [wann ist diese Regel anzuwenden]
- **Regel:** [was ist zu tun]
- **Ausnahmen:** [wann gilt die Regel nicht; leer lassen, wenn keine]
- **Gegenbeispiel:** [was wäre falsch]
```

### Regeln

#### Regel-001: Versionsdisziplin Stack-Komponenten

- **Herkunft:** ADR-002
- **Gilt für:** jede Änderung an in `project-context.md` Abschnitt 3 gelisteten Versionen.
- **Regel:** Patch- und Minor-Updates sind freigabefrei und werden ohne ADR übernommen, sofern Verifikations-Stempel `Verifiziert: YYYY-MM-DD` aktualisiert wird. **Major-Updates** erfordern erneute Verifikation auf der offiziellen Quelle plus einen ADR mit Begründung und Auswirkungen.
- **Ausnahmen:** Sicherheits-Patches dürfen ohne ADR sofort übernommen werden, müssen aber im Logbuch als `[BEOBACHTUNG]` plus `[ADR-ANGELEGT]` (Folge-ADR mit `[OPERATIV] [STACK]`) nachgezogen werden.
- **Gegenbeispiel:** PostgreSQL silent von 17.9 auf 18 ohne ADR – verboten.

#### Regel-002: Stack-Ausschlüsse beachten

- **Herkunft:** ADR-002
- **Gilt für:** jede Bibliotheks-, Tool- oder Service-Wahl.
- **Regel:** Vor Aufnahme einer neuen Abhängigkeit zuerst `project-context.md` Abschnitt 3 „Explizit nicht erlaubt" prüfen. Treffer dort = sofortiger Verzicht, keine Diskussion. Auch indirekte Treffer (eine Bibliothek, die intern auf Redis basiert, ist faktisch ein Redis-Treffer).
- **Ausnahmen:** Ausnahmen sind freigabepflichtig und werden mit eigenem ADR (`[STRATEGISCH] [STACK]`) dokumentiert.
- **Gegenbeispiel:** Auswahl einer Bibliothek mit GPL-Lizenz für ein Backend-Modul, weil sie funktional besser passt – verboten ohne expliziten ADR.

#### Regel-003: Modulgrenzen-Pflicht

- **Herkunft:** ADR-003
- **Gilt für:** jeden Funktions-/Methodenaufruf zwischen Backend-Modulen.
- **Regel:** Aufrufe von Modul A nach Modul B nur über die in `architecture.md` Abschnitt 4 spezifizierten öffentlichen Schnittstellen. Direktzugriff auf interne Strukturen anderer Module (Funktionen, Klassen, ORM-Modelle) ist Architekturbruch.
- **Ausnahmen:** keine. Eine Schnittstellen-Erweiterung ist freigabepflichtig (CLAUDE.md Abschnitt 4 Punkt 5).
- **Gegenbeispiel:** `from backend.fleet.models import Vehicle` aus `backend/operations` – verboten. Stattdessen Schnittstelle S4 nutzen.

#### Regel-004: Frontend ↔ Externer Service nur über Backend

- **Herkunft:** ADR-003
- **Gilt für:** alle drei Frontends.
- **Regel:** Frontends rufen niemals direkt MapTiler, TomTom oder andere externe HTTP-APIs auf. Alle externen Calls gehen über das Backend, das sie über `infra/tile-proxy` sendet. API-Keys leben Backend-seitig.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Direkter `fetch('https://api.maptiler.com/...')`-Call aus dem Svelte-Code – verboten.

#### Regel-005: Sensible Bootstrap-Operationen über CLI

- **Herkunft:** ADR-004
- **Gilt für:** jede Operation, die ohne bestehende Web-Auth-Identität ausgeführt werden muss.
- **Regel:** Bootstrap-Operationen werden als CLI-Subcommand in `python -m eb_digital …` realisiert, mit interaktiver Passwort-Eingabe via `getpass` und ohne Klartext-Argument. Kein Web-Endpunkt für Bootstrap-Aktionen in Phase 1.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** `POST /api/admin/bootstrap` – verboten. ENV-basiertes Bootstrap-Passwort – verboten.

#### Regel-006: AccessCode-Hashing-Pflicht

- **Herkunft:** ADR-005
- **Gilt für:** jede Speicherung und jeden Vergleich eines AccessCodes.
- **Regel:** AccessCodes werden gehashed (mit Salt) gespeichert. Vergleiche per Konstantzeit-Vergleich. Klartext-Codes erscheinen weder in der Datenbank noch in Logs noch in Fehlermeldungen.
- **Ausnahmen:** Disponenten-UI darf den Klartext-Code anzeigen, weil der Disponent ihn aktiv erzeugt und verteilt – aber nur im UI-Antwort-Flow direkt nach Erzeugung, nicht aus der Datenbank rekonstruiert.
- **Gegenbeispiel:** `WHERE access_code = $1` mit Klartext – verboten. `logger.info(f"AccessCode für Operation {id} ist {code}")` – verboten.

#### Regel-007: AccessCode-Toggle wirkt nur auf neue Sessions

- **Herkunft:** ADR-005
- **Gilt für:** Aktivierung oder Deaktivierung eines AccessCodes für eine laufende Operation.
- **Regel:** Bestehende anonyme Sessions, die vor der Toggle-Aktion gestartet sind, behalten ihren Bestell-Pfad bis zum Session-Ablauf. Nur **neu** startende Sessions ab dem Zeitpunkt der Toggle-Aktion müssen den (de)aktivierten Code-Status erfüllen.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Aktivierung des Codes mitten in laufender Operation invalidiert sofort alle bestehenden Einsatzkraft-Sessions – verboten (UX-Bruch im Einsatz).

#### Regel-008: Aggregat-Schreibung sofort beim Operation-Ende

- **Herkunft:** ADR-006
- **Gilt für:** Operation-Ende-Workflow.
- **Regel:** Beim Operation-Ende wird der `operation_aggregate`-Eintrag **synchron** geschrieben, bevor der Operation-Ende-Workflow als abgeschlossen gilt. Die 30-Tage-Anonymisierung läuft entkoppelt als separater Procrastinate-Job und greift nur auf Detail-Daten zu, nicht auf das bereits geschriebene Aggregat.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Aggregat-Schreibung als Procrastinate-Job, der parallel zur Anonymisierung läuft – verboten (Race-Bedingung).

#### Regel-009: Kein Personen-Bucket im Aggregat

- **Herkunft:** ADR-006
- **Gilt für:** jede Erweiterung von `operation_aggregate`.
- **Regel:** Keine Felder, die einzelne Personen identifizieren oder pseudonymisieren – auch nicht über Hashes, Counter pro Person oder ähnliche Konstrukte. Aggregat enthält nur summarische Werte ohne Personen-Bezug.
- **Ausnahmen:** keine. Eine Aufweichung wäre freigabepflichtig (CLAUDE.md Abschnitt 4 Punkt 6) und müsste ein neues ADR mit DSGVO-Re-Identifikations-Analyse vorlegen.
- **Gegenbeispiel:** Hinzufügen eines Felds `dispatcher_activity_hash_counts` (Map Pseudonym→Anzahl Aktionen) – verboten.

#### Regel-010: Mandanten-übergreifende Datenoperationen ausschließlich asynchron

- **Herkunft:** ADR-007
- **Gilt für:** jede Operation, die mehr als triviale Mengen Mandanten-Daten anfasst (Datenexport, Bulk-Anonymisierung, große Aggregations-Migrationen).
- **Regel:** Solche Operationen werden als Procrastinate-Job gestartet. API-Endpunkte liefern nur Job-ID/Status, nie das Ergebnis im selben Request.
- **Ausnahmen:** Lese-Anfragen mit klar begrenzter Größe (Listen unter ~100 Datensätzen, paginiert) bleiben synchron.
- **Gegenbeispiel:** `GET /api/tenants/{id}/export` als Single-Request mit ZIP-Stream – verboten.

#### Regel-011: Audit-Log-Pflicht bei destruktiven oder konfigurierenden Operations-Aktionen

- **Herkunft:** ADR-008
- **Gilt für:** jede Aktion in `backend/operations`, die Operation-Zustand ändert (Operation beenden, AccessCode toggeln, Operation-Raum-Geometrie ändern, Versorgungs-Transporter-Modus wechseln, Strecke freigeben, Bündelung auslösen, Stornierung ausführen).
- **Regel:** Vor oder im selben DB-Transaktions-Schritt wird ein `operation_audit_log`-Eintrag mit `actor_dispatcher_id`, `action_type`, `at`, `target_kind`, `target_id`, `payload` (ohne PII) geschrieben.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Operation beenden ohne Audit-Log-Eintrag – verboten. Audit-Log-Eintrag erst nach erfolgreichem Commit der Aktion (außerhalb der Transaktion) – verboten (Atomicity-Bruch).

#### Regel-012: Confirmation-Dialog vor destruktiven Aktionen im Disponenten-Frontend

- **Herkunft:** ADR-008
- **Gilt für:** alle in Regel-011 gelisteten Aktionen, soweit sie aus dem `frontend-disponent` initiiert werden.
- **Regel:** Vor Auslösung der Aktion zeigt das Frontend einen modalen Bestätigungs-Dialog mit klarer Bezeichnung der Aktion und ihrer Wirkung („Operation 'X' beenden – nicht rückgängig machbar."). Bestätigung erst nach explizitem Klick.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** Single-Click-Button für „Operation beenden" ohne Modal – verboten.

#### Regel-013: Operation↔Mandant ausschließlich über `operation_tenant_participation`

- **Herkunft:** ADR-009
- **Gilt für:** jede Datenmodell-Erweiterung oder -Abfrage, die Operation und Mandant in Beziehung setzt.
- **Regel:** Kein direkter `operation.tenant_id`-Foreign-Key. Verknüpfung ausschließlich über `operation_tenant_participation(operation_id, tenant_id, role)`. In Phase 1 genau ein Eintrag pro Operation mit `role='owner'`.
- **Ausnahmen:** keine. Eine Direkt-FK-Variante wäre eine Aufhebung der Verbund-Tauglichkeit und freigabepflichtig.
- **Gegenbeispiel:** `ALTER TABLE operation ADD COLUMN tenant_id …` – verboten.

#### Regel-014: Berechtigungs-Filter als Teilnahme-Filter formulieren

- **Herkunft:** ADR-009
- **Gilt für:** alle Backend-Abfragen, die Mandanten-Sichtbarkeit auf Operations und davon abhängige Entitäten (Orders, Vehicles im Operations-Kontext, Audit-Log-Einträge) prüfen.
- **Regel:** Filter werden als „Operations, an denen Mandant X teilnimmt" formuliert (`JOIN operation_tenant_participation … WHERE tenant_id = …`), **nicht** als „Operations, deren `tenant_id` X ist". In Phase 1 verhaltensgleich, in späterer Verbund-Phase additiv erweiterbar ohne Refactoring der Filter.
- **Ausnahmen:** keine.
- **Gegenbeispiel:** `SELECT * FROM operation WHERE tenant_id = $1` – verboten.
