# Spike H — Resilience-Granularität: Messprotokoll

- **Fahrplan-Referenz:** 5.2 (Phase 5, ERKUNDUNG)
- **Datum:** 2026-06-11
- **Status:** Empirie vollständig — ADR-Entwurf unten, **wartet auf Freigabe**
- **Zeitverbrauch:** ~2 h (innerhalb Zeitbox 6–8 h)
- **Setup:** lokaler Compose-Stack (PostgreSQL 17.9, Valkey 8.1.7, Backend + Procrastinate-Worker 3.8.1), Apple Silicon. Mess-Volumen synthetisch geseedet: **100.000 `customer_order`** + 200.000 Audit-Log-Einträge + 50.000 anonyme Sessions an einer Operation → **DB 90 MB** (realistische Obergrenze einer einzelnen mehrwöchigen Großlage; Seed nach Abschluss rückstandsfrei entfernt).

## 1. Mess-Ergebnisse

### A/B — Backup-Pfade (90-MB-DB, lokale NVMe)

| Pfad         | Befehl                             | Dauer     | Artefakt-Größe                |
| ------------ | ---------------------------------- | --------- | ----------------------------- |
| **Logisch**  | `pg_dump -Fc`                      | **2,1 s** | 18 MB                         |
| **Physisch** | `pg_basebackup -Ft -z -Xs -c fast` | **1,5 s** | 29 MB (base + WAL + Manifest) |

Beide Pfade sind bei Großlagen-Volumen trivial schnell und klein. Auch bei 10-fachem Volumen bleiben beide im Minuten-/Sub-Minuten-Bereich (lineares Skalierungsverhalten; auf dem Hetzner-VPS konservativ ×2–3 gegenüber lokaler NVMe anzusetzen — finale Validierung im 6.4-Backup-Recovery-Test).

### C — Restore-RTO

| Pfad         | Verfahren                                                      | Dauer     | Verifikation          |
| ------------ | -------------------------------------------------------------- | --------- | --------------------- |
| **Logisch**  | `pg_restore -j 4` in frische DB                                | **0,5 s** | 100.012 Orders, 84 MB |
| **Physisch** | base.tar.gz + pg_wal entpacken → frischer Container → Recovery | **4,6 s** | 100.012 Orders        |

### D — Crash mitten im Auftragsstatus-Wechsel (`kill -9` auf PostgreSQL)

Aufbau: unkommittete Groß-Transaktion (Status-Wechsel auf 20.000 Orders, in `pg_sleep` gehalten) **plus** parallele Autocommit-Insert-Schleife; dann `docker kill -s KILL` auf den DB-Container.

| Messgröße                           | Ergebnis                                                                                 |
| ----------------------------------- | ---------------------------------------------------------------------------------------- |
| Recovery bis `pg_isready`           | **0,7 s** (WAL-Redo 0,13 s über 112 MB WAL-Distanz)                                      |
| Unkommittete 20k-Status-Transaktion | **vollständig zurückgerollt** (cancelled-/completed-Zähler exakt auf Vor-Crash-Stand) ✅ |
| Committete parallele Inserts        | **vollständig erhalten** ✅                                                              |
| Orders gesamt                       | 100.012 — kein Verlust, kein Teilzustand                                                 |

**Befund:** PostgreSQL-Transaktionsatomarität trägt das Szenario „Crash mitten im Auftragsstatus-Wechsel" ohne jede Anwendungs-Logik. Es gibt keinen halben Status-Wechsel. **Bekannte, akzeptierte Lücke:** ein Crash **zwischen** DB-Commit und Valkey-`PUBLISH` verliert genau ein WS-Event — Clients heilen das per Design über REST-Refetch beim Reconnect (4.4/4.5-Mechanik, siehe F).

### E — Procrastinate-Job-State über Worker-Ausfall

| Szenario                                                                                                                  | Ergebnis                                                                                                                                                                                                                           |
| ------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **E1:** 20 Jobs deferiert bei gestopptem Worker                                                                           | Jobs persistieren als `todo` in PostgreSQL; nach Worker-Start binnen Sekunden alle `succeeded` ✅                                                                                                                                  |
| **E2:** verwaister `doing`-Job (toter Worker, Heartbeat 10 min alt — simulierter Worker-Crash mitten in der Verarbeitung) | `job_manager.get_stalled_jobs()` erkennt ihn (Heartbeat-Schwelle Default 30 s), `retry_job()` setzt zurück auf `todo`, laufender Worker verarbeitet ihn → `succeeded`; `prune_stalled_workers()` räumt den toten Worker-Eintrag ✅ |

**Befund:** Procrastinate 3.8.1 bringt die komplette Crash-Recovery-Mechanik mit (Worker-Heartbeats in `procrastinate_workers`, Stalled-Job-Erkennung, Retry). **Konsequenz für 6.4/6.5/6.6:** (a) beim Backend-/Worker-Start eine Stalled-Job-Routine ausführen (`get_stalled_jobs` → `retry_job`, `prune_stalled_workers`); (b) alle produktiven Jobs (Retention, Export, Aggregat) müssen **idempotent** sein — Retry-Semantik ist at-least-once (Idempotenz-Pflicht steht bereits in `architecture.md` Modul `backend/retention`).

### F — Full-Stack-Neustart (Vision-Szenario „Server-Neustart")

| Messgröße                                     | Ergebnis                                                                                                                             |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `docker compose down` (ohne `-v`)             | 1,7 s                                                                                                                                |
| `up -d` bis `/api/health` = 200 (durch Caddy) | 13,4 s                                                                                                                               |
| **Gesamt-RTO Stack-Neustart**                 | **15,1 s**                                                                                                                           |
| Datenintegrität danach                        | 100.012 Orders + komplette Job-Historie intakt ✅                                                                                    |
| **Post-Recovery-E2E**                         | **voller `dev-smoke.sh` grün** (alle 23 Stufen inkl. Realtime-Stufe: WS-Auth, Subscribe/S10, Valkey-Pub/Sub-Fan-out, Anon-Filter) ✅ |

**Befund Reconnect nach State-Reload:** WS-Verbindungen brechen beim Neustart ab (by design, Vision: State-Erhaltung ≠ Connection-Erhaltung); der WS-Pfad steht nach dem Neustart vollständig (dev-smoke-Realtime-Stufe), Clients reconnecten mit der 4.5-getesteten Auto-Reconnect-Mechanik und laden den State per REST nach.

## 2. Recovery-Reihenfolge (empirisch begründet)

1. **PostgreSQL** — Single Source of Truth, enthält **auch den Procrastinate-Job-State** (ADR-002-Designziel bestätigt: ein Restore stellt Einsatz- UND Job-Zustand gemeinsam her, keine getrennte Job-Queue-Wiederherstellung nötig).
2. **Valkey** — **kein Restore**: reiner Cache + Pub/Sub. Rate-Limit-Counter starten leer (kurzzeitig großzügigeres Limit, sicherheitsunkritisch), Pub/Sub-Subscriptions bauen sich mit den WS-Reconnects neu auf.
3. **Backend + Worker** — Start-Routine: Stalled-Job-Behandlung (E2); Worker zieht `todo`-Jobs automatisch.
4. **Valhalla-Routing-Container** — kein Backup nötig: Routing-Graph ist aus Geofabrik-Extract + Build-Pipeline deterministisch **rebuildbar** (ADR-021); nur der Extract-Stand wird dokumentiert.
5. **Frontends** — statische Bundles, kein State; Clients reconnecten selbst.

## 3. ADR-Entwurf (wartet auf Freigabe)

**Backup-Strategie-Optionen:**

- **A — Nur nächtlicher `pg_dump`:** einfachster Betrieb, aber RPO bis 24 h — während einer laufenden Großlage wären bis zu einem Tag Bestellungen/Aufträge verloren. Kollidiert mit der Vision „nahtlose Fortsetzung nach Crash" für den Disaster-Fall.
- **B — `pg_basebackup` täglich + kontinuierliches WAL-Archiving** (`archive_command`/`archive_timeout` 60 s) auf Off-VPS-Ziel: **RPO ≤ 1 min** (PITR), Restore gemessen im Sekundenbereich. Nur PostgreSQL-Bordmittel, keine neue Abhängigkeit.
- **C — Hybrid (Empfehlung): B als Primärpfad + täglicher `pg_dump` zusätzlich.** Der logische Dump ist das portable Artefakt (versionsunabhängiger, taugt für Einzeltabellen-Restore, Migrations-Tests, Mandanten-Forensik) und kostet bei den gemessenen Volumina nichts (2 s / 18 MB). Externes Tooling (pgBackRest, wal-g) bewusst **nicht** in Phase 1 — bei den gemessenen Größen Over-Engineering; Re-Evaluation wenn DB > einige GB.

**Empfehlung: C.** Eckwerte für den ADR: Basebackup täglich, WAL-Archiving kontinuierlich (`archive_timeout` 60 s), `pg_dump` täglich, Aufbewahrung 14 Tage (DSGVO-konsistent: Backups enthalten Detail-Daten, die nach 30 Tagen anonymisiert werden — Aufbewahrung muss < 30-Tage-Karenz bleiben, sonst überleben anonymisierte Daten im Backup; 14 Tage lässt Puffer). **Backup-Ziel außerhalb des VPS** (Hetzner Storage Box per SSH/rsync naheliegend — Deployment-Detail im 6.4-Detail-Plan, kein Code-Dependency).

**RTO/RPO-Annahmen für `architecture.md` §6 (als `[VORLÄUFIG]` mit Messwert):**

| Szenario                                     | RTO (gemessen lokal)                                                  | RPO                         |
| -------------------------------------------- | --------------------------------------------------------------------- | --------------------------- |
| Prozess-/Container-Crash (Disk überlebt)     | **< 30 s** (gemessen 0,7 s DB-Recovery, 15,1 s Full-Stack)            | **0** (WAL)                 |
| Disaster (VPS-Verlust, Restore aus Off-Site) | Minuten (Restore selbst 4,6 s bei 90 MB; Host-Provisioning dominiert) | **≤ 1 min** (WAL-Archiving) |

Finale Validierung beider Werte: Backup-Recovery-Test in **6.4** (Stabilisierungs-Anker, auf VPS-Hardware statt lokaler NVMe).

**Folge-Pflichten bei Freigabe:** ADR `[ERKENNTNIS] [MODUL] [DEPLOYMENT]`; Reifegrad Spike-H-Bereich (`backend/resilience`) → `[VORLÄUFIG]`; 6.4-Scope ergänzt um Stalled-Job-Start-Routine, WAL-Archiving-Konfiguration, Off-Site-Ziel, Restore-Runbook (`docs/runbooks/restore.md`) mit der in Abschnitt 2 verifizierten Reihenfolge.

## 4. Artefakte

- Mess-Rohdaten: Terminal-Protokoll dieser Session (Kennzahlen vollständig oben); kein versionierter Wegwerf-Code.
- Seed-Daten + Backup-Artefakte + Restore-Container nach Abschluss vollständig entfernt (verbleibend: 16 reguläre Dev-Smoke-Orders; DB-Dateigröße bis `VACUUM FULL` bei 92 MB — lokal irrelevant).
- Stack lief während des Spikes bewusst **up** (Laufzeit-Resilienz-Messung); für Coverage-Läufe gilt weiterhin die Stack-down-Disziplin.
