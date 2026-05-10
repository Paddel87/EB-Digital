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

### 2026-05-10 – [SESSIONENDE]

- **Session-Dauer:** ca. 2 h 45 min (Sessionstart unmittelbar nach PR-#14-Merge bis Sessionende-Commit-Vorbereitung).
- **Bearbeitet:** Phase 1 Schritt 1.8 — **Infrastruktur (Caddy + nginx) + Docker Compose dev-Profil.** Status `[OFFEN]` → `[ERLEDIGT]`. **Phase 1 damit komplett abgeschlossen.**
- **Erreicht:**
  - **Versions-Re-Verifikation 1.8** (eigene Recherche → Patrick-Batch-Bestätigung — gleiches Pattern wie 1.3/1.5/1.6/1.7): nginx 1.30.0 unverändert (released 2026-04-15, GA des stable 1.30-Branches, kein 1.30.1), Caddy 2.11.2 (released 2026-04-17, Bug-Fix-Patch innerhalb 2.11-Linie), Valkey 8.1.7 unverändert (released 2026-05-06), Docker Engine 29.4.2 (CVE-Fix-Patch, lokal `docker version` bestätigt), Docker Compose v5.1.3 (lokal bestätigt). Patrick: „alle bestätigt". Stempel in `project-context.md` Abschnitt 3 nachgezogen.
  - **Image-Pinning mit Manifest-List-Digests** (multi-arch-tauglich, analog zur Postgres-Konvention) per `docker buildx imagetools inspect <tag> --format '{{.Manifest.Digest}}'`: `nginx:1.30.0-alpine` → `sha256:0272e460…`, `caddy:2.11.2` → `sha256:25cdc846…`, `valkey/valkey:8.1.7-alpine` → `sha256:b0272353…`, `node:24-alpine` → `sha256:d1b3b4da…`. Drei in `dev`-Profil-Services aktiv, der vierte für Frontend-`frontends`-Profil.
  - **`infra/reverse-proxy/Caddyfile`** (Caddy 2.11.2): `eb.local` + `localhost`-Site mit `tls internal` (Caddy-internem CA, browser zeigt Warnung, curl `-k`). Routing `/api/*` und `/health` → `backend:8000`; `handle_path /disponent/*`, `/betreuer/*`, `/einsatzkraft/*` → die drei Vite-Dev-Server mit URL-Präfix-Strip; Default-Handler liefert HTML-Landing als Lebenszeichen. Security-Header (HSTS, X-Content-Type-Options, X-Frame-Options, Referrer-Policy) global. JSON-Logging zu stdout für `docker compose logs`. Sub-Domain-Refactor und `paths.base`-Frontend-Konfiguration für Phase 7 STABILISIERUNG dokumentiert.
  - **`infra/tile-proxy/nginx.conf`** (nginx 1.30.0-alpine): `proxy_cache_path` für Tiles (7 Tage TTL, 1 GB) und Geocoding (30 Tage, 128 MB) eingerichtet — Phase-1-Stubs antworten 204 (kein API-Budget-Verbrauch in dev), Phase-6-Pass-through für MapTiler/TomTom als Inline-Kommentare an den Routen vorgemerkt. `/health`-Endpunkt für Compose-Healthcheck. Pfad-Regex `^/tiles/(\d+)/(\d+)/(\d+)\.pbf$` matcht Akzeptanzkriterium aus Fahrplan.
  - **`docker-compose.yml`** komplett überarbeitet:
    - Profile `dev`, `staging`, `production` für Core-Services (`db`, `cache`, `db-init`, `backend`, `worker`, `tile-proxy`, `reverse-proxy`); separates `frontends`-Profil für die drei Vite-Dev-Server. `--profile dev` bringt 6 healthy Services + 1 abgeschlossenen `db-init` hoch; `--profile dev --profile frontends` zusätzlich die Frontend-Dev-Server.
    - **Neuer `db-init`-Service:** läuft `alembic upgrade head` einmalig; backend und worker hängen mit `depends_on: condition: service_completed_successfully` an. Idempotent. **Notwendig** weil ein neues `eb-digital-pg`-Volume sonst kein procrastinate-Schema hat (Worker-Crash mit `function procrastinate_prune_stalled_workers_v1 does not exist`).
    - **Backend-Service** mit `serve --host 0.0.0.0 --port 8000`, Healthcheck via Python-`urllib.request` auf `/health`, `expose: 8000` (intern für Caddy).
    - **Worker-Healthcheck:** PID-1-Liveness (`os.path.exists('/proc/1/cmdline')`) — vollwertige Job-Engine-Health folgt in Phase 4. Bewusst Skelett.
    - **Cache (Valkey 8.1.7-alpine):** `valkey-server --appendonly yes --save 60 1000`, eigenes Volume `eb-digital-valkey` mit `eb-digital.backup: yes`-Label.
    - **Reverse-Proxy:** Ports `127.0.0.1:80` und `127.0.0.1:443` ans Loopback-Interface gebunden (kein öffentliches Binding in dev). Caddy admin-API auf `:2019` für Healthcheck.
    - **Volume-Backup-Marker** über Labels `eb-digital.backup: yes/no` und `eb-digital.purpose` — pg + valkey + caddy-data = backup-pflichtig, tile-cache + caddy-config + node_modules = regenerierbar. Erfüllt Akzeptanzkriterium „Kein Container hat Volumes ohne Backup-Marker".
    - **Frontend-Services:** node:24-alpine mit Bind-Mount des Workspaces + Named-Volumes für `node_modules` (vermeidet macOS-↔-Alpine-Inkompatibilität). Erster Start zieht pnpm-Dependencies in den Volume-Cache (mehrere Minuten Wartezeit). `corepack enable && pnpm install --frozen-lockfile && pnpm --filter <ws> exec vite dev --host 0.0.0.0`.
  - **Backend-Erweiterung:** `/api/health`-Endpunkt am `api_router` ergänzt (additiv, identische Payload zu `/health`). Neue gemeinsame `_health_payload()`-Helper-Funktion. Zwei neue Tests in `test_health.py` (Endpoint-Funktionalität + Payload-Identität). Coverage backend gesamt 94 % bei 103 Tests (zuvor 101).
  - **`scripts/dev-smoke.sh`** als robuster End-to-End-Smoke: prüft `.env` (kopiert aus `.env.example` falls fehlend), validiert Compose-Konfiguration, baut Images, fährt Stack hoch, wartet auf alle Healthchecks (180 s Timeout), testet `/api/health` + `/health` über Caddy mit JSON-Payload-Match, testet Tile-Proxy (`/tiles/12/3456/4321.pbf` → 204; `/health` → 200) via `docker compose exec backend` (testet die intern-only-Route). `--keep`-Flag für Stack-Persistenz nach grünem Lauf, sonst automatisches `compose down`. Trap mit Diagnose-Logs bei Fehler.
  - **Verifikations-Sequenz (alle Akzeptanzkriterien aus Fahrplan 1.8 erfüllt):**
    1. ✅ `docker compose --profile dev config --quiet` syntaktisch valide.
    2. ✅ `docker compose --profile dev build` bringt eb-digital-backend:dev.
    3. ✅ `docker compose --profile dev up -d` bringt nach `db-init`-Lauf alle 6 Services in Status `healthy` (Postgres, Valkey, Backend, Worker, Tile-Proxy, Reverse-Proxy).
    4. ✅ `curl -k https://localhost/api/health` → 200, `{"status":"ok","version":"0.1.0"}`.
    5. ✅ `curl -k https://localhost/health` → 200 (parallel-Pfad).
    6. ✅ Tile-Proxy `/tiles/12/3456/4321.pbf` → 204 (Phase-1-Stub).
    7. ✅ Tile-Proxy `/health` → 200, JSON-Payload.
    8. ✅ `bash scripts/dev-smoke.sh` läuft komplett grün durch.
    9. ✅ `uv run pytest` 103 Tests grün, Coverage 94 % gesamt (Backend-`/api/health`-Endpunkt-Coverage 100 %).
    10. ✅ `uv run pre-commit run --all-files` grün auf allen Hooks (prettier formatierte docker-compose.yml einmal um, danach stabil).
    11. ✅ Volume-Backup-Marker konsistent gepflegt — alle 11 Volumes haben `eb-digital.backup`-Label.
- **Reibungen während der Session:**
  - **Methoden-Erfolg — `db-init`-Service als saubere Lösung:** Erste compose-up-Iteration nach Postgres-Volume-Neuanlage scheiterte am Worker, weil das procrastinate-Schema fehlte. Statt Alembic im Smoke-Skript zu skripten, sauber als eigener Compose-Service mit `service_completed_successfully`-Dependency modelliert. Idempotent, repository-versioniert, in Production wieder­verwendbar.
  - **Stale Postgres-Container-Konflikt aus früherer Worktree-Session:** Erste Smoke-Iteration scheiterte mit „Bind for 127.0.0.1:5432 failed: port is already allocated". Ursache: `distracted-dirac-fbe89b-db-1` aus PR-#13-Worktree lief noch (Compose-Stack post-merge nicht abgeräumt). Nach Patrick-Freigabe per `docker stop && docker rm` entfernt. Lerneffekt: nach jedem PR-Merge sollten die Worktree-Compose-Stacks beendet werden — möglicher Cleanup-Hook für Worktree-Lifecycle in Phase 7.
  - **Prettier formatierte docker-compose.yml einmal um:** Healthcheck-Test-Arrays wurden von einzeiligem in mehrzeiligen Stil gebracht. Erwartete Reibung mit YAML-Formatter, Re-Run nach prettier-Auto-Fix grün.
  - **Architektur-Spec vs. Fahrplan-Dissonanz bei Frontend-Routing:** `architecture.md` Abschnitt 3 sieht Sub-Domains pro Frontend vor (`disponent.eb-digital.example` etc.), `fahrplan.md` 1.8 schreibt Path-Routing unter `eb.local` vor. Path-Routing in dev mit `handle_path` umgesetzt; Architektur-Wechsel auf Sub-Domains plus `kit.paths.base`-Frontend-Konfiguration als Phase-7-Aufgabe in den Caddyfile-Header dokumentiert. Kein ADR nötig — Fahrplan dokumentiert die Phase-1-Wahl, Architektur-Update kommt mit der Phase-7-Implementierung.
- **Reaktiv-Quote nach dieser Session:** **0/10 (0 %)**. Schwellenwert 20 % nicht erreicht. Diese Session hat keinen ADR erzeugt — alle Entscheidungen (Profil-Layout, Image-Tags, Healthcheck-Strategien, db-init-Service) sind operativ und im Rahmen von ADR-002 (Stack), ADR-003 (Architektur-Pattern) und ADR-008-Methodik abgedeckt.
- **Architektur-Spec-Anpassung:** keine Reifegrad-Wechsel. `infra/reverse-proxy` und `infra/tile-proxy` bleiben `[VORLÄUFIG]` per expliziter Fahrplan-Regel — produktive TLS, Sub-Domain-Routing und Cache-Pass-through sind Phase-7-Voraussetzung für `[BELASTBAR]`.
- **Phase-1-Reflexion (Anker für Reflexion-nach-Phase-1 in `fahrplan.md`):** 8 Schritte, alle ERLEDIGT, Zeitraum 2026-05-08 bis 2026-05-10 (3 Kalendertage). Versions-Verifikations-Disziplin (eigene Recherche → A/B-Frage → Patrick-Bestätigung) hat sich 5 Mal in Folge bewährt (1.3, 1.5, 1.6, 1.7, 1.8). Reaktiv-Quote 0 % über die gesamte Phase. Eine Reibungs-Welle (Blocker #001 uv-/venv-Korruption) durchgängig ab 1.4, mit Diagnose-Spike in PR #14 ursächlich aufgeklärt — Heilung als 14-Zeilen-Skript dauerhaft im Repo.
- **Bekannter Test-Daten-Stand in lokaler DB:** `platform_admin` enthält noch `smoke_test_user` und `smoke_v2` aus Schritt 1.6. Optional Aufräumen vor Phase 2.
- **Nächster Schritt:** **Phase 2 – Auth + Tenants + Verbund-Tauglichkeit (I1/I2)** (UMSETZUNG). Detail siehe `fahrplan.md` Phase 2.

### 2026-05-10 – [SESSIONSTART]

- **Letzter Stand:** Phase 1 Schritte 1.1–1.7 alle ERLEDIGT (PR #13 in `main`, PR #14 mit Blocker-#001-Ursachenaufklärung in `main`). Reaktiv-Quote 0/11. Keine aktiven Blocker. `scripts/fix-venv-flags.sh` als macOS-Worktree-Heilung etabliert.
- **Geplant für diese Session:** Phase 1 Schritt 1.8 — **Infrastruktur (Caddy + nginx) + Docker Compose dev-Profil.** Konkret laut `fahrplan.md` Zeilen 367–388: `infra/reverse-proxy/Caddyfile` (Routing `/api/*` → backend, je ein Pfad-Block für die drei Frontends, Caddy-internes TLS für `eb.local`); `infra/tile-proxy/nginx.conf` (proxy_cache 7-Tage-TTL, Stub-204 für nicht-gecachte Tiles, MapTiler/TomTom-Pass-through-Skelett mit ENV-Key-Inject); `docker-compose.yml` um Profile `dev`/`staging`/`production` plus Services `backend` (Uvicorn), `cache` (Valkey), `tile-proxy`, `reverse-proxy`, `frontend-*` (drei Vite-Dev-Server) erweitern (db + worker existieren bereits); `scripts/dev-smoke.sh` (Compose hochfahren, Healthchecks abwarten, `/api/health` über Caddy abrufen, runterfahren). Akzeptanzkriterien aus `fahrplan.md` Schritt 1.8: `docker compose --profile dev up -d` bringt alle Container `healthy`, `curl -k https://eb.local/api/health` 200, Tile-Proxy antwortet `204`/Tile, Smoke-Script grün, kein Volume ohne Backup-Marker.
- **Vorabprüfung:**
  - **Branch-Awareness korrekt verlaufen:** `git fetch --all --prune` zu Sessionstart; Worktree-Branch `scp/romantic-buck-1e64b2` lag 2 Commits hinter `origin/main`, per `git merge --ff-only origin/main` von `d31812f` auf `a3d6ef0` (PR #14) gehoben. Worktree-Stand entspricht Fahrplan-Stand 1.7 ERLEDIGT, 1.8 OFFEN.
  - **Versions-Re-Verifikation Pflicht für 1.8** (Modus-2-Schritt-2a-Disziplin): Recherche durchgeführt am 2026-05-10 auf nginx.org-CHANGES, GitHub-Releases und Docker-Hub. Ergebnis als Batch-Frage an Patrick — nginx 1.30.0 unverändert (released 2026-04-15), Caddy 2.11.2 (released 2026-04-17), Valkey 8.1.7 unverändert (released 2026-05-06), Docker Engine 29.4.2 (CVE-Fix, lokal `docker version` bestätigt 29.4.2), Docker Compose v5.1.3 (lokal bestätigt). Patrick hat alle bestätigt.
  - **Image-Digests** für reproduzierbares Pinning per `docker buildx imagetools inspect <tag> --format '{{.Manifest.Digest}}'` aufgelöst — Manifest-List-Digests (multi-arch-tauglich): `nginx:1.30.0` → `sha256:55d1fb09…`, `caddy:2.11.2` → `sha256:25cdc846…`, `valkey/valkey:8.1.7-alpine` → `sha256:b0272353…`. Konvention analog zum bestehenden Postgres-Eintrag (Tag + Digest).
  - **Backend-Health-Routing:** existierender `/health`-Endpoint ist auf App-Root, Caddy-Routing in 1.8 zielt aber auf `/api/*`. Lösung: zusätzlichen `/api/health`-Endpoint im FastAPI-Router ergänzen (additiv, nicht-brechend, deckt das Akzeptanzkriterium `curl https://eb.local/api/health`).
  - **macOS-Worktree-Vorsorge:** `.venv` existiert noch nicht. Plan: nach erstem `uv sync` in dieser Session einmalig `bash scripts/fix-venv-flags.sh` ausführen, um Hidden-Flag-Skip-Bug zu prä-empt-fixen (Erkenntnis aus PR #14).
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/romantic-buck-1e64b2` (Opus 4.7 1M-Kontext).

### 2026-05-10 – [PROBLEM-GELÖST]

- **Bezug:** Blocker #001 „uv-/venv-Korruption nach intensiven Reinstall-/Sync-Sequenzen" — vier Vorfälle in 1.4, 1.5, 1.6 (zweimal), 1.7. Aufforderung des Menschen am 2026-05-10: „ursache feststellen".
- **Methode:** Diagnose-Spike im Worktree `practical-tesla-baab22` auf grünem Boden (`.venv` existierte zu Sessionstart nicht). Systematische Verifikation der vier Hypothesen aus dem Blocker-Eintrag, jede mit eigenem reproduzierbaren Test, ohne vorab zu „heilen" (Beweise-Erhalt).
- **Ursache (zweifelsfrei nachgewiesen):**
  - macOS BSD-File-Flag **`UF_HIDDEN`** ist auf allen `.venv`-Dateien gesetzt (nachgewiesen mit `ls -lO`-Spalte `hidden` auf vier verschiedenen Worktrees).
  - **Python 3.13** hat in [`Lib/site.py`](https://github.com/python/cpython/blob/3.13/Lib/site.py) ein neues Sicherheits-Verhalten: `.pth`-Dateien mit `UF_HIDDEN` werden mit der expliziten Meldung `Skipping hidden .pth file: …` übersprungen. Verifiziert per `uv run --no-sync python -v` direkt im Worktree.
  - Das **Editable-Install** für `eb_digital` läuft über genau so eine `.pth` (`_editable_impl_eb_digital.pth`, Inhalt: `<projektroot>/backend`). Wird sie geskipt → `eb_digital`-Pfad nie in `sys.path` → `ModuleNotFoundError: No module named 'eb_digital'`.
- **Trigger:** Der Worktree-Stamm (`.../EB-Digital/.claude/worktrees/<name>/`) und das Eltern-Verzeichnis `.claude/worktrees/` tragen das `hidden`-Flag (mit hoher Wahrscheinlichkeit gesetzt vom Worktree-anlegenden Tooling). Beim **allerersten** `uv sync` in einem neuen Worktree übernimmt uv (oder das macOS-Filesystem beim `mkdir .venv` unter einem hidden Parent) das Flag auf die `.venv`-Inhalte. **Folge-Syncs in derselben venv erzeugen nicht-hidden Dateien** — daher ist die Heilung mit `chflags -R nohidden .venv` stabil, sobald sie einmal angewandt ist.
- **Verifikations-Sequenz:**
  1. ✅ `uv run --no-sync python -v -c "pass"` druckt sechsmal `Skipping hidden .pth file: …` (für `_editable_impl_eb_digital.pth`, `_virtualenv.pth`, `a1_coverage.pth`).
  2. ✅ `site.addpackage(sp, '_editable_impl_eb_digital.pth', set())` bei manuellem Aufruf fügt den Pfad **nicht** zu `sys.path` hinzu (Hidden-Skip in der internen Logik).
  3. ✅ Manueller `sys.path.insert(0, '<projektroot>/backend')` lässt `import eb_digital` sofort gelingen — Pfad und Modul-Existenz sind also korrekt.
  4. ✅ `chflags -R nohidden .venv` heilt alle Importe in einem Schritt (`eb_digital`, `pytest`, `pygments`, `pygments.plugin`, `annotated_types`, `argon2`, `_argon2_cffi_bindings`) — **kein** `--reinstall`, **kein** `rm -rf .venv` nötig.
  5. ✅ Cross-Check: Hauptcheckout `/Users/patrickschulz/Documents/GitHub/EB-Digital/` (außerhalb von `.claude/worktrees/`) hat **keine** Hidden-Flags auf seinen Dateien — der Bug ist worktree-spezifisch.
- **Erklärt damit alle bekannten Symptom-Varianten von Blocker #001:**
  - **`eb_digital`-Pattern (1.4, 1.6):** direkt — `.pth` skipped → Editable-Pfad nicht in `sys.path`.
  - **`pygments.plugin`, `BaseMetadata`, `_argon2_cffi_bindings`, `pytest` fehlt (1.6, 1.7):** Folgeschäden. Wenn `eb_digital` fehlt, hat der Mensch (oder ich) reaktiv mit `uv pip install --reinstall <pkg>` und `rm -rf .venv && uv sync` gegengearbeitet, was Cache-Inkonsistenzen / partielle Installationen produzieren kann. In der jetzt frisch geheilten venv funktionieren _alle_ diese Module ohne `--reinstall`.
  - **Heilungs-Mythos:** `rm -rf .venv && uv sync --reinstall` wirkte zuverlässig nicht weil `--reinstall` nötig war, sondern weil der **zweite** Sync auf eine bereits zur Hälfte aufgesetzte venv schreibt, deren neue Files nicht-hidden geschrieben werden.
- **Fix (eingeführt):** [`scripts/fix-venv-flags.sh`](scripts/fix-venv-flags.sh) — minimalistisches Bash-Skript, prüft `.venv` und entfernt rekursiv das Hidden-Flag mit `chflags -R nohidden .venv`. Idempotent, no-op außerhalb von macOS, klare Begründungs-Header. Manuell auszuführen nach jedem _ersten_ `uv sync` in einem neuen Worktree (also einmalig pro Worktree-Lebensdauer).
- **Hinweis im README:** Quick-Start-Sektion um eine kurze Notiz „macOS-Worktrees: nach erstem `uv sync` einmalig `bash scripts/fix-venv-flags.sh` ausführen" ergänzt.
- **Blocker-Bewegung:** Blocker #001 in `docs/blockers.md` von „Aktive Blocker" nach „Gelöste Blocker" verschoben mit Lösungs-Eintrag und Verweis auf diesen Logbuch-Eintrag. Aktive-Blocker-Anzahl: **0**.
- **Reaktiv-Quote nach diesem Eintrag:** **0 / 11 (0 %)**, unverändert. Es entstand kein ADR — die Diagnose ist reine Bug-Aufklärung mit Tooling-Fix, keine Architektur-Entscheidung. Eine als `ENTSCHEIDUNG ERFORDERLICH` vorgelegte strategische Folge-Frage (venv-Speicherort außerhalb von `.claude/worktrees/` per `UV_PROJECT_ENVIRONMENT`) wurde von Patrick am 2026-05-10 zugunsten **Option A (Status quo + Sofort-Fix-Skript)** entschieden — keine Build-Pipeline-Änderung, kein ADR. Begründung: Aufwand-Nutzen marginal gegenüber 14 Zeilen Bash, einmalig pro Worktree-Setup.
- **Lerneffekt (methodisch):** Die Heuristik im Logbuch 1.5 „Drittauftritt rechtfertigt einen Blocker-Stub-Eintrag noch nicht — Heilung ist deterministisch" war im Nachhinein zu zurückhaltend. Eine zuverlässige Workaround-Sequenz, die wiederholt nötig wird, ist **selbst** ein Indikator für eine offene Ursache und sollte spätestens beim **dritten** Vorfall einen Diagnose-Spike auslösen, nicht erst beim vierten oder fünften. Der Workaround maskiert den Bug, ohne ihn zu lösen.

### 2026-05-10 – [SESSIONSTART]

- **Letzter Stand:** 1.7 ERLEDIGT (PR #13 in `main`); Blocker #001 vom 2026-05-10 als „Aktiv" eingetragen aber ohne Schritt-Blockade. Worktree `practical-tesla-baab22` zu Sessionbeginn ohne `.venv`.
- **Auftrag:** Mensch fragt „Wieso taucht der vorfall in Blocker 001 immerwieder auf?" — Antwort liefert die Selbst-Erklärung des Blockers (symptomatische Heilung ohne Ursachenbehebung). Folgeauftrag: **„ursache feststellen"**.
- **Charakter:** Diagnose-Spike, kein Code-Schritt. Phasentyp-formal entspricht das einer ERKUNDUNG, läuft aber als Sonderfall innerhalb Phase 1 (UMSETZUNG) — kein neuer Fahrplan-Schritt nötig, weil die Aufgabe einen einzelnen Tag umfasst und ein bestehendes Blocker-Item auflöst.
- **Vorabprüfung:** `git fetch --all --prune` zeigt Worktree synchron mit `origin/main` (`d31812f`). Keine berührten Module, keine ADR-Pflicht antizipiert.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/practical-tesla-baab22` (Opus 4.7 1M-Kontext).

### 2026-05-10 – [SESSIONENDE]

- **Session-Dauer:** ca. 1 h 30 min (Sessionstart unmittelbar nach PR-#12-Merge bis Sessionende-Commit-Vorbereitung).
- **Bearbeitet:** Phase 1 Schritt 1.7 — **Frontend-Workspaces + PWA-Skelett.** Status `[OFFEN]` → `[ERLEDIGT]`. Plus erster Eintrag in `blockers.md` (#001 uv-/venv-Korruption — Pattern-Dokumentation, kein Schritt-Blocker).
- **Erreicht:**
  - **Versions-Verifikation 1.7** (Batch-Recherche auf npm + GitHub-Releases, Patrick entscheidet — gleiches Pattern wie 1.3/1.5/1.6): 13 bestehende Pins re-bestätigt (svelte 5.55, @sveltejs/kit 2.59, vite 8.0, typescript 6.0.3, vite-plugin-pwa 1.3, vitest 4.1, svelte-check 4.4, eslint 10.3, typescript-eslint 8.59, eslint-plugin-svelte 3.17, eslint-plugin-security 4.0, prettier 3.8, prettier-plugin-svelte 3.5), 3 neue Pakete erst-verifiziert (`@sveltejs/adapter-static` ~3.0.10, `@sveltejs/vite-plugin-svelte` ~7.1.0, `@vitest/coverage-v8` ~4.1.0). Patrick antwortete „alle bestätigt". Ein vierter neuer Pin (`@types/node` ~24.12.0) wurde mid-implementation pragmatisch ergänzt — als Standard-Tooling-Type-Stub für Node 24 LTS, transitiv über vite/svelte-kit `tsconfig types: ["node"]` Pflicht. Stempel in `project-context.md` Abschnitt 3 nachgezogen.
  - **Drei SvelteKit-Workspaces** unter `apps/frontend-{disponent,betreuer,einsatzkraft}` neu angelegt:
    - **Strukturidentisch:** `package.json` mit gepinnten Dev-Deps + scripts (`dev`, `build`, `preview`, `sync`, `check`, `tsc`, `lint`, `format`, `format:write`, `test`); `svelte.config.js` mit `@sveltejs/adapter-static` (Pages+Assets in `build/`, Fallback `index.html`, strict); `tsconfig.json` extends `./.svelte-kit/tsconfig.json` plus override für `strict + noUncheckedIndexedAccess + noImplicitReturns + isolatedModules`; `eslint.config.js` (Flat-Config, inline statt shared-Import — siehe Reibung); `.prettierrc.json` mit `prettier-plugin-svelte` (pro Frontend statt Root, weil prettier-Plugin-Resolution pro CWD läuft); `.prettierignore` (analog, weil prettier 3.x `.prettierignore` aus dem CWD relativ auflöst); `vitest.config.ts` mit v8-Coverage; `src/app.html`, `src/app.d.ts`, `src/lib/version.ts` (App-Name/Version/Build-Time aus `vite.config.ts` `define`); `src/routes/+layout.{ts,svelte}` (prerender + ssr); `src/routes/+page.svelte`; `src/routes/health/+page.svelte` mit dl/dt/dd-Listing; `tests/version.test.ts` als Smoke; `static/.gitkeep`.
    - **Spezifika:**
      - **disponent (Port 5173):** ohne PWA (Vision-Constraint stationär + stabile Verbindung).
      - **betreuer (Port 5174):** `vite-plugin-pwa` mit `generateSW` + Manifest „EB Digital Betreuer" + Workbox-NetworkFirst auf `/api/*` (cache-name `api-cache`, 24 h TTL, networkTimeoutSeconds 5). Skelett für Spike L (Tile-Caching).
      - **einsatzkraft (Port 5175):** dito mit Manifest „EB Digital Einsatzkraft" und schlankerem Workbox-NetworkFirst nur auf `/api/anon/*` (cache-name `anon-api-cache`, 4 h TTL, 50 entries).
  - **Shared-Root-Konfig:** `tsconfig.base.json` mit gemeinsamen strict-Optionen; `.prettierrc.json` im Root für md/yaml/json (ohne svelte-Plugin, das pro Frontend deklariert wird).
  - **Verifikations-Sequenz (alle Akzeptanzkriterien aus Fahrplan 1.7 erfüllt):**
    1. ✅ `pnpm install` zieht 482 Pakete für 4 Workspaces (root + 3 Frontends).
    2. ✅ `pnpm -r build` baut alle drei Frontends; SW + manifest.webmanifest in `apps/frontend-betreuer/build/` und `apps/frontend-einsatzkraft/build/`, **kein** sw.js in `apps/frontend-disponent/build/` — Differential korrekt.
    3. ✅ `pnpm --filter frontend-disponent dev` startet vite dev (Port 5173 belegt → automatisch 5174); curl `http://[::1]:5173/` und `http://[::1]:5173/health` liefern HTML mit App-Name + Version + Build-Time.
    4. ✅ `pnpm -r test` 3 Test-Files je 1 passed (Smoke für `vite define`-Replacement).
    5. ✅ `pnpm -r lint` (eslint Flat-Config) grün auf allen drei nach Fix von `svelte/no-navigation-without-resolve` (`<a href="/health">` → `<a href={resolve("/health")}>` aus `$app/paths`).
    6. ✅ `pnpm -r format` (prettier --check) grün nach Anlegen pro-Frontend-`.prettierrc.json` und `.prettierignore`.
    7. ✅ `pnpm -r check` (svelte-check) 0 Errors / 0 Warnings auf allen drei nach Aufnahme von `@types/node` als Dev-Dep (Pflicht für SvelteKit-generierte tsconfig `types: ["node"]`).
    8. ✅ `pnpm -r tsc` (svelte-kit sync && tsc --noEmit) grün auf allen drei.
    9. ✅ `uv run pre-commit run --all-files` grün — alle Hooks (Hygiene, ruff, mypy, bandit, prettier, actionlint) passieren. ESLint/svelte-check/tsc-Frontend-Hooks „skipped" weil noch keine git-changed-files (wirken erst beim echten Commit).
    10. ✅ `uv run pytest` Backend-Suite weiterhin 101/101 grün, Coverage 94 % gesamt — keine Regression durch Frontend-Arbeit.
- **Reibungen während der Session:**
  - **Methoden-Erfolg — Versions-Batch-Verifikation:** 16 Pakete in einem einzigen Verifikations-Block an Patrick statt 16 einzelne Fragen. Effizient (eine Antwort „alle bestätigt") und transparent. Ein Paket (`@types/node`) wurde mid-implementation nachgereicht, weil svelte-check eine entsprechende Warnung warf — als Tooling-Standard-Type-Stub von Patrick nicht als ADR-pflichtig zu betrachten, aber im Logbuch transparent.
  - **Shared-ESLint-Config-Pfad funktionierte nicht:** Erster Versuch war `eslint.config.shared.mjs` im Repo-Root, importiert von jeder Frontend-eslint.config.js. Ergebnis: `Cannot find package '@eslint/js' imported from /<root>/eslint.config.shared.mjs` — pnpm-Workspaces installieren die Pakete nur in den Workspace-`node_modules`, nicht im Root. Lösung: shared.mjs gelöscht, Inline-Config (~30 Zeilen) pro Frontend dupliziert. Lerneffekt: Cross-Workspace-Imports von Tooling-Configs sind in pnpm-Workspaces brüchig — Inline-Duplikation ist robuster als geschickter Import.
  - **Prettier-Plugin-Resolution scheitert in pre-commit-Hook:** Erster Wurf hatte `.prettierrc.json` im Root mit `"plugins": ["prettier-plugin-svelte"]`. Lokaler `pnpm -r format` (im Workspace-Verzeichnis) lief grün, aber `pre-commit run prettier --all-files` (vom Root aus) failte mit `Cannot find package 'prettier-plugin-svelte' imported from /noop.js`. Lösung: Root-`.prettierrc.json` ohne svelte-Plugin; pro Frontend eigene `.prettierrc.json` mit Plugin-Deklaration. Gleicher Pfad-Resolution-Effekt wie bei ESLint.
  - **Svelte-Hyper-Lint-Regel `no-navigation-without-resolve`:** Erste `+page.svelte`-Files hatten `<a href="/health">` — eslint-plugin-svelte's flat/recommended verlangt `resolve()` aus `$app/paths` für alle internen Links. Fix: `import { resolve } from "$app/paths"` plus `<a href={resolve("/health")}>`. Korrekt für SvelteKit mit `paths.base`-Konfiguration.
  - **Vite-Dev-Smoke zeigte Port-Konflikt:** `pnpm --filter frontend-disponent dev` versuchte Port 5173, fand ihn belegt (von vorigem Background-Task), wechselte automatisch auf 5174. Curl auf 5173 lieferte 000, Curl auf `[::1]:5173` (IPv6) jedoch 200 — der vorhandene vite-Server lauschte auf IPv6-only. Lerneffekt: für Smoke-Tests `[::1]` und `127.0.0.1` beide probieren oder explizit `--host 127.0.0.1` setzen. Background-vite-Server wurden mit `kill <pid>` beendet (pkill via Pattern-Match griff nicht zuverlässig).
  - **Vierter Fall der uv-venv-Reibung — Blocker #001 angelegt:** Nach intensiver Frontend-Arbeit zeigte `uv run pytest` `ModuleNotFoundError: No module named 'pytest'` direkt nach `uv sync` (das vorher grün war). Targeted `uv pip install --reinstall pytest pytest-cov pytest-asyncio` löste pytest, aber nicht `argon2-cffi` — `_argon2_cffi_bindings` fehlte. Heilung: nukleare `rm -rf .venv && uv sync --reinstall` (4. Mal in dieser Phase). Pattern jetzt klar: _jede_ intensive Sequenz aus `uv sync` + `uv pip install --reinstall` + `uv run` mit längerer Aktivität dazwischen kann eine partial-korrupte venv produzieren. Wie in CLAUDE.md-Lerneffekt 1.6 versprochen: Eintrag in [`docs/blockers.md`](docs/blockers.md) als **Blocker #001** angelegt mit fünf bekannten Symptom-Varianten, Reproduktions-Skizze und Eskalations-Hinweis bei fünftem Vorfall.
- **Reaktiv-Quote nach dieser Session:** **0/11 (0 %)**. Schwellenwert 20 % nicht erreicht. Diese Session hat keinen ADR erzeugt — alle Versions-Pin-Entscheidungen sind operativ und in `project-context.md` Abschnitt 3 abgehandelt (Regel-001 ADR-002).
- **Architektur-Spec-Anpassung:** keine direkten Modul-Reifegrad-Wechsel — die drei Frontend-Skelette bleiben `[VORLÄUFIG]`, weil außer Health-Page und Layout keine Domain-Logik existiert. Beförderung auf `[BELASTBAR]` folgt frühestens mit Phase 4 (Operations Core) für `frontend-einsatzkraft` und Phase 6 für die anderen.
- **Bekannter Test-Daten-Stand:** unverändert (`platform_admin` enthält noch `smoke_test_user` und `smoke_v2` aus Schritt 1.6).
- **Nächster Schritt:** **Phase 1 Schritt 1.8 — Infrastruktur (Caddy + nginx) + Docker Compose dev-Profil.** Eingangskriterien: 1.3 ✓, 1.4 ✓, 1.5 ✓, 1.6 ✓, 1.7 ✓ — alle Skelette laufen einzeln. Versions-Re-Verifikation für `nginx 1.30.0`, `Caddy 2.11.x`, `docker compose v5.1.x` zu Sessionstart 1.8.

### 2026-05-10 – [SESSIONSTART]

- **Letzter Stand:** Phase 1 Schritte 1.1–1.6 alle ERLEDIGT (PR #12 `f39bb15` in `main`). Reaktiv-Quote 0/11. Keine aktiven Blocker. Keine offenen STOPP-Situationen. Schnittstelle S1 (Admin-Bootstrap-CLI) auf `[BELASTBAR]`.
- **Geplant für diese Session:** Phase 1 Schritt 1.7 — **Frontend-Workspaces + PWA-Skelett.** Konkret: drei SvelteKit-Projekte unter `apps/frontend-{disponent,betreuer,einsatzkraft}` mit Svelte 5 + SvelteKit 2 + Vite 8 + TypeScript 6, jeweils mit `package.json`, `svelte.config.js`, `vite.config.ts`, `tsconfig.json` (`strict + noUncheckedIndexedAccess + noImplicitReturns`); `vite-plugin-pwa` mit Workbox-Konfig „network-first" für API-Calls für Betreuer + Einsatzkraft (Disponent ohne PWA in Phase 1); `/health`-Route pro Frontend mit App-Version + Build-Zeit; ESLint + Prettier + svelte-check Konfigurationen pro Paket plus shared Root-Config. Akzeptanzkriterien aus `fahrplan.md` Schritt 1.7: `pnpm -r build` baut alle drei, `pnpm --filter frontend-disponent dev` startet Dev-Server, `pnpm -r test` läuft (Setup OK), SW registriert sich für Betreuer + Einsatzkraft, nicht für Disponent.
- **Vorabprüfung:**
  - **Branch-Awareness korrekt verlaufen:** `git fetch --all --prune` zu Sessionstart; lokaler `scp/distracted-dirac-fbe89b` mit `git merge --ff-only origin/main` von `884a686` auf `f39bb15` (Merge-Commit von PR #12) gehoben. Worktree-Stand entspricht Fahrplan-Stand 1.6 ERLEDIGT, 1.7 OFFEN.
  - Phase 1 = UMSETZUNG. Schritt 1.7 Eingangskriterium: 1.1 ✓ (pnpm-Workspace existiert mit Workspace-Manifest auf `apps/frontend-*`). Nicht freigabepflichtig laut Fahrplan.
  - Sonderregel Phase 1 (Eingangsdisziplin abgemildert) gilt — Frontend-Module bleiben durch Skelett-Existenz `[VORLÄUFIG]`, keine direkte Reifegrad-Wirkung.
  - **Versions-Re-Verifikation Pflicht für 1.7** (Stand-Notiz im Fahrplan + Modus-2-Schritt-2a-Disziplin): mehrere npm-Pakete werden hier neu gepinnt. Re-Verifikation auf npm + GitHub-Releases zu Sessionbeginn, dann in `project-context.md` Abschnitt 3 mit `Verifiziert: 2026-05-10`-Stempel pro Paket ergänzen.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/distracted-dirac-fbe89b` (Opus 4.7 1M-Kontext) — selber Worktree wie 1.6 (PR #12 ist gemerged, kein neuer Worktree nötig).

### 2026-05-10 – [SESSIONENDE]

- **Session-Dauer:** ca. 2 h 30 min (Sessionstart 2026-05-09 spät bis Sessionende-Commit-Vorbereitung 2026-05-10 nach Mitternacht).
- **Bearbeitet:** Phase 1 Schritt 1.6 — **backend/auth Admin-Bootstrap-CLI.** Status `[OFFEN]` → `[ERLEDIGT]`. Reifegrad-Wechsel S1 (Admin-Bootstrap-CLI) `[VORLÄUFIG]` → `[BELASTBAR]`.
- **Erreicht:**
  - **Versions-Verifikation 1.6** (eigene Recherche, Patrick entscheidet — gleiches Pattern wie 1.3/1.5): `argon2-cffi 25.1.0` (released 2025-06-03, Python 3.13/3.14 als Trove-Classifier offiziell, MIT, kein Hotfix seit 2025-06-03 → Re-Bestätigung); `itsdangerous 2.2.0` (released 2024-04-16, BSD-3-Clause, einzige stabile 2.x-Linie, langsame Pallets-Cadence → Erst-Verifikation). Patrick antwortete „beide bestätigt". Stempel in `pyproject.toml` und `project-context.md` Abschnitt 3 nachgezogen.
  - **`backend/eb_digital/auth/`** komplett neu angelegt:
    - **`models.py`** (`PlatformAdmin` mit UUID-PK, `username` unique 64, `password_hash` String(255) für Argon2id-PHC mit Headroom, `created_at` timezone-aware, `created_via` String(32) plus `CHECK (created_via IN ('bootstrap_cli','admin_cli'))`-Constraint mit Naming-Convention-konformem Namen `ck_platform_admin_created_via_allowed`; `_utcnow`-Helper inline statt Import privater `db._utcnow`).
    - **`hashing.py`** (`hash_password`/`verify_password`/`needs_rehash` über `PasswordHasher()` mit Library-Defaults; `PASSWORD_MIN_LENGTH=12` aus `project-context.md` Abschnitt 6 Sicherheit; `verify_password` fängt `VerifyMismatchError` und `InvalidHash` ab → `False`, alle anderen argon2-Fehler propagieren).
    - **`cli.py`** (asynchrone `create_platform_admin`-Use-Case-Funktion mit Idempotenz-`SELECT … WHERE username=?` vor INSERT; `AdminCreationError` als gemeinsame Exception mit konkreten Messages; `_run_create` orchestriert Engine + Session + Dispose; `cmd_admin_create` ist der argparse-Handler; `_read_password_interactively` ist getpass-Wrapper für Tests). Username-Validierung: `strip` + nicht leer + mindestens 3 Zeichen + kein Whitespace. Erfolg: stdout `created admin user: <username>` plus JSON-Log `{"message": "platform_admin_created", "username": ..., "created_via": "bootstrap_cli", "at": <ISO8601>}`. **Kein Klartext-Passwort, kein Hash, kein Salt im Log oder stdout.**
  - **`__main__.py`-Erweiterung:** `admin`-Subparser mit `required=True` admin_command und `create`-Sub-Sub-Subcommand mit `--username` Pflichtargument; `_cmd_admin` ruft `cmd_admin_create` (Stub mit TODO 1.6 entfernt). JSON-Logging wird vor dem Handler-Aufruf konfiguriert, damit der Audit-Eintrag strukturiert geht.
  - **Migration `20260509_fa3aaa5f04a0_add_platform_admin.py`** per Autogenerate erzeugt; `alembic check` bestätigt Idempotenz. Alembic env.py um Import von `eb_digital.auth.models` erweitert (sonst sieht autogenerate die neue Tabelle nicht).
  - **30 neue Tests**: `test_auth_models.py` (10), `test_auth_hashing.py` (7), `test_auth_cli.py` (13). `test_main.py` aktualisiert (`test_admin_subcommand_is_a_stub_with_exit_code_two` ersetzt durch 4 Tests für die echte Subparser-Routine inkl. parse-error-Pfade). `_FakeSession`-Klasse simuliert SQLAlchemy-Defaults beim `flush`, sodass Tests ohne Live-DB UUID/created_at sehen.
  - **Verifikations-Sequenz (alle Akzeptanzkriterien aus Fahrplan 1.6 erfüllt):**
    1. ✅ `alembic upgrade head` zweistufig: 1.5-Stand → `add_platform_admin` läuft fehlerfrei.
    2. ✅ `alembic check` nach upgrade: „No new upgrade operations detected" — ORM und Schema in Sync.
    3. ✅ `uv run pytest` 101 Tests grün; Coverage `backend/eb_digital/auth/*` **100 %** (cli/hashing/models alle bei 100 %); gesamt 94 % (Schwelle 80 % weit überschritten); Auth-Modul-Anforderung ≥ 95 % aus `project-context.md` Abschnitt 7 erfüllt.
    4. ✅ `uv run ruff check backend` + `ruff format --check backend` + `uv run mypy --strict` alle grün (nach Erweiterung der per-file-ignores für Tests um `S105`/`S106`/`S107`/`SLF001`).
    5. ✅ `uv run pre-commit run --all-files` grün (mypy-Hook brauchte `argon2-cffi` und `itsdangerous` in `additional_dependencies`, sonst „Cannot find implementation or library stub for module argon2" — eingehängt).
    6. ✅ Smoke gegen reale Postgres: `echo '<pass>' | python -m eb_digital admin create --username smoke_v2` → stdout `created admin user: smoke_v2` plus JSON-Audit-Log; DB-Eintrag mit `$argon2id$v=19$m=65536,t=3,p=4`-Marker + `bootstrap_cli`. Doppel-Aufruf mit gleichem Username scheitert mit Exit 1 + Fehlermeldung „Username 'smoke_test_user' existiert bereits". Kürzerer Username (`pa`) scheitert mit Validierungsmeldung „mindestens 3 Zeichen".
- **Reifegrad-Wechsel:** Schnittstelle **S1 (Admin-Bootstrap-CLI)** `[VORLÄUFIG]` → `[BELASTBAR]` per Beförderungsregel 1 (funktionierende Implementierung + Tests + Smoke). Modul `backend/auth` bleibt `[VORLÄUFIG]`, weil die volle Auth-Logik (Login, Sessions, Rate-Limit, Multi-User) erst in Phase 2 kommt — Schritt 1.6 implementiert ausschließlich den Bootstrap-Pfad. Architektur-Spec S1 in `architecture.md` an die Implementierung angepasst (keine Confirm-Password-UX in Phase 1, gemeinsame `AdminCreationError`-Klasse statt drei benannten, konkrete Fehlermessages dokumentiert).
- **Reibungen während der Session:**
  - **Methoden-Erfolg — Versions-Verifikations-Disziplin hält:** drittes Mal in Folge (1.3, 1.5, 1.6) lief der Pattern „eigene Recherche → konkrete A/B-Frage an Patrick → er entscheidet → Stempel ins pyproject + project-context". Cost ~10 min Recherche, Antwort ein Wort. Kein Architektur-Drift durch Versions-Treiber.
  - **Architecture-Spec-Drift bei S1:** Beim Reifegrad-Update fiel auf, dass `architecture.md` für S1 eine Confirm-Password-Eingabe und drei separate Fehlerklassen (`UsernameAlreadyExists`, `PasswordTooShort`, `DatabaseUnavailable`) vorgegeben hatte — beides ohne Quellen-ADR und über Fahrplan-Schritt 1.6 hinaus. Auflösung: Implementierung minimal an Spec angeglichen (Username-Min-3, stdout-Print), Spec dort an Implementierung angepasst, wo sie über Phase-1-Scope hinausging (Confirm weg, AdminCreationError-Konsolidierung dokumentiert). Lerneffekt: Architektur-Spec-Details, die nicht durch ADR oder Fahrplan-Schritt gedeckt sind, sind „Architektur-Wunsch" und beim ersten Reifegrad-Wechsel mit der Realität abzugleichen.
  - **Drittes Mal `_editable_impl_*.pth`-Reibung — diesmal mit Bonus pygments-/annotated-types-Korruption:** `python -m eb_digital admin create` schlug nach einem Test-Lauf mit `No module named eb_digital` fehl (1.4-Pattern, drittes Mal). Heilung 1.4 (`uv sync --reinstall-package eb-digital`) wirkte einmal, dann erneut Fehler. Nukleare Variante (`rm -rf .venv && uv sync`) brachte ein neues Symptom: `pygments` und `annotated_types` waren korrupt installiert (`No module named 'pygments.plugin'`, `cannot import name 'BaseMetadata' from 'annotated_types'`), wahrscheinlich uv-Cache-Korruption. Wirksame Heilung: `rm -rf .venv && uv sync --reinstall` (cache-bypass per `--reinstall`). Lerneffekt: nach nuklearer Variante immer `--reinstall` mitnehmen, sonst greift uv auf einen potenziell beschädigten Cache zurück. Kein Blocker (reproduzierbar gemacht und geheilt), aber wenn ein viertes Mal: `docs/blockers.md`-Eintrag mit minimaler Repro pflicht.
  - **Pre-Commit-mypy-Lücke:** `uv run mypy` lief grün (lokale venv kennt argon2-cffi mit `py.typed`), aber `pre-commit run mypy` failte mit „Cannot find implementation or library stub for module argon2". Pre-Commit-mypy läuft in eigener venv und kennt nur, was in `additional_dependencies` steht. Lösung: `argon2-cffi~=25.1.0` und `itsdangerous~=2.2.0` zur `.pre-commit-config.yaml`-mypy-Hook-Liste ergänzt. Lerneffekt: Pflicht-Pin im pyproject **und** Spiegelung im Pre-Commit-mypy-Block sind beides notwendig — bei jeder neuen Runtime-Dep mit eigenen Type-Stubs muss beides ergänzt werden.
- **Reaktiv-Quote nach dieser Session:** **0/10 (0 %)**. Schwellenwert 20 % nicht erreicht. Diese Session hat keinen ADR erzeugt — die Versions-Pin-Entscheidungen sind operativ und in `project-context.md` Abschnitt 3 abgehandelt (entspricht Regel-001 ADR-002 „Patch frei, Minor ohne ADR, Major mit ADR").
- **Bekannter Test-Daten-Stand in lokaler DB:** `platform_admin` enthält zwei Smoke-Test-Einträge (`smoke_test_user`, `smoke_v2`). Lokales Volume `eb-digital-pg`; Aufräumen optional vor 1.7-Beginn (`docker exec ... psql -c "DELETE FROM platform_admin WHERE username LIKE 'smoke%'"` oder `docker compose down -v`).
- **Nächster Schritt:** **Phase 1 Schritt 1.7 — Frontend-Workspaces + PWA-Skelett.** Eingangskriterium 1.1 ✓ erfüllt (pnpm-Workspace existiert). Versions-Re-Verifikation für `svelte`/`@sveltejs/kit`/`vite`/`vite-plugin-pwa` zu Sessionstart 1.7 (Modus-2-Schritt-2a-Disziplin).

### 2026-05-09 – [SESSIONSTART]

- **Letzter Stand:** Phase 1 Schritte 1.1–1.5 alle ERLEDIGT (PR #11 `c09c2e1` in `main`, ADR-011 + Regel-016 als Folge der psycopg-LGPL-Reibung in 1.5). Reaktiv-Quote 0/10. Keine aktiven Blocker. Keine offenen STOPP-Situationen.
- **Geplant für diese Session:** Phase 1 Schritt 1.6 — **backend/auth Admin-Bootstrap-CLI.** Konkret: Migration mit Tabelle `platform_admin` (`id`, `username` unique, `password_hash`, `created_at`, `created_via ∈ {bootstrap_cli,admin_cli}`); CLI-Befehl `python -m eb_digital admin create --username <name>` mit interaktiver Passwortabfrage via `getpass`, Argon2id-Hashing per `argon2-cffi` mit Library-Defaults; Idempotenz (Doppel-Username → Exit ≠ 0); Bootstrap-Erfolg als JSON-`INFO`-Zeile mit `{username, created_via, at}`, **kein** Klartext-Passwort/Hash/Salt im Log. Akzeptanzkriterien aus `fahrplan.md` Schritt 1.6: CLI legt Eintrag an, Doppel-Aufruf scheitert, `password_hash` mit `$argon2id$…`-Marker, Coverage `backend/auth` ≥ 95 %. Reifegrad-Wirkung: S1 (Admin-Bootstrap-CLI) `[VORLÄUFIG]` → `[BELASTBAR]`.
- **Vorabprüfung:**
  - **Branch-Awareness korrekt verlaufen:** `git fetch --all --prune` zu Sessionstart; Worktree-Branch `scp/distracted-dirac-fbe89b` ist auf HEAD `c09c2e1` (PR #11 gemerged), tracked `origin/main`, keine Divergenz. Worktree-Stand entspricht Fahrplan-Stand 1.5 ERLEDIGT, 1.6 OFFEN.
  - Phase 1 = UMSETZUNG. Schritt 1.6 hat Eingangskriterien: 1.3 ✓ (Backend-Skelett), 1.4 ✓ (PostgreSQL + Alembic + ORM-Konventionen). Nicht freigabepflichtig laut Fahrplan — ADR-004 fixiert das Verfahren strategisch (CLI-Bootstrap statt Web-Setup-UI), die konkrete Implementierung ist OPERATIV.
  - Sonderregel Phase 1 (Eingangsdisziplin abgemildert) gilt — `backend/auth` bleibt durch das Bootstrap-Skelett `[VORLÄUFIG]`; nur die einzelne Schnittstelle S1 wird durch funktionierende CLI auf `[BELASTBAR]` befördert.
  - **Versions-Re-Verifikation Pflicht für 1.6** (Schritt-1.1-Notiz + Modus-2-Schritt-2a-Disziplin): zwei Pakete zu prüfen — `argon2-cffi` (bereits am 2026-05-07 verifiziert, Re-Bestätigung vor produktiver Nutzung) und `itsdangerous` (im pyproject mit Hinweis „Verifikation Schritt 1.6", noch ohne Stempel). Frage an Patrick wird im Modus-2-Schritt-2a-Format formuliert, **bevor** Code geschrieben wird.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/distracted-dirac-fbe89b` (Opus 4.7 1M-Kontext).

### 2026-05-09 – [SESSIONENDE]

- **Session-Dauer:** ca. 3 h (Sessionstart bis Sessionende-Commit-Vorbereitung).
- **Bearbeitet:** Phase 1 Schritt 1.5 — **Procrastinate-Setup + Worker.** Status `[OFFEN]` → `[ERLEDIGT]`. Plus eine ungeplante, mid-Session entstandene Methodik-/Lizenz-Entscheidung (ADR-011 + Regel-016).
- **Erreicht:**
  - **Versions-Verifikation 1.5** (delegiert an mich nach 1.3-Pattern): PyPI + GitHub-Releases + raw `pyproject.toml` für `procrastinate`. **3.8.1** (released 2026-04-08, ~1 Monat alt, Production/Stable, MIT). Kein Hotfix-Pattern wie 2.14.x bei pydantic-settings → Empfehlung A. **Patrick wählte Option A:** `procrastinate~=3.8.1` plus **PsycopgConnector** (Procrastinate-Default-Pfad).
  - **STOPP wegen Lizenz-Reibung:** Beim ersten `uv run python ...` mit procrastinate-Import fiel auf, dass psycopg (Pflicht-Sub-Dep von procrastinate) **LGPL-3.0-only** ist. `project-context.md` Abschnitt 6 schließt LGPL ohne ADR aus. STOPP-Block formuliert mit drei Optionen: (A) ADR-Akzeptanz, (B) Procrastinate kippen (effektiv unmöglich), (C) ADR-Akzeptanz **plus** Methodik-Regel für Sub-Dep-Lizenz-Prüfung. **Patrick wählte C.**
  - **ADR-011** `[OPERATIV] [STACK] [METHODIK]` — psycopg LGPL-3.0-only akzeptiert. Geltungsbereich der LGPL-Verschmutzung auf Persistenz-/Job-Engine-Pfad beschränkt; Module ohne Job-Engine (`infra/tile-proxy`, Routing-Adapter in `backend/geo`) bleiben extraktionsfähig. **Regel-016** abgeleitet — Sub-Dep-Lizenz-Prüfung im Verifikations-Regime, schließt die methodische Lücke aus Modus-2-Schritt-2a. Tabelle Teil A in `decisions.md` aktualisiert. `project-context.md` Abschnitt 6 um „Aktive Ausnahmen"-Sub-Block + Sub-Dep-Lizenz-Prüfung-Verweis erweitert. **Reaktiv-Quote bleibt 0/10.**
  - **`pyproject.toml`:** `procrastinate~=3.8.1` und `psycopg[binary,pool]~=3.3.4` als Runtime-Deps mit Verifiziert-Stempel. Kommentar im Datei-Kopf entfernt (procrastinate ist nicht mehr „kommend").
  - **`project-context.md`** Abschnitt 3 Sub-Block Background-Jobs überarbeitet — procrastinate jetzt mit Versions-Pin, Connector-Begründung; psycopg als eigene Stack-Zeile mit ADR-011-Verweis. Begründungs-Block aktualisiert.
  - **Procrastinate-DB-Schema-Migration** `add_procrastinate_schema` (Revision `1e343dae5fc4`):
    - `upgrade()` nutzt `procrastinate.schema.SchemaManager.get_schema()` als Quelle.
    - **Statement-Splitter** (`_split_postgres_statements`) inline in der Migration: respektiert Top-Level-Semikolons, schützt `$$`/`$tag$`-Dollar-Quoting für Function-Bodies und `DO`-Blöcke. Begründung: asyncpg's prepared-statement-Modus lehnt Multi-Statement ab (`cannot insert multiple commands into a prepared statement`).
    - `downgrade()` als Liste expliziter `DROP ... CASCADE`-Statements (Tabellen, Functions, Composite-Type, Enum-Types in der richtigen Reihenfolge). 4 Tabellen + 18 Functions + 3 Enum-Types sauber rekonstruierbar.
  - **`backend/migrations/env.py`:** `include_object` + `include_name` Callbacks blenden `procrastinate_*`-Objekte aus, damit `alembic check`/`alembic revision --autogenerate` keine Drop-Operationen für die externe Schema-Verwaltung vorschlagen.
  - **`backend/eb_digital/jobs/`:**
    - `__init__.py`: `_to_psycopg_conninfo()` (URL-Konvertierung `postgresql+asyncpg://` → `postgresql://`), `make_procrastinate_app()` Factory, Modul-Level `procrastinate_app: App` mit Side-Effekt-Import des `ping`-Sub-Moduls. **Job-Modul-Konvention** dokumentiert: jedes Backend-Modul mit Hintergrund-Jobs bekommt ein eigenes `jobs/`-Submodul.
    - `ping.py`: `@procrastinate_app.task(name="ping")` mit `INFO`-Logger-Eintrag `ping_task_executed` und Rückgabe `"pong"`. Phase-1-Sentinel; entfernt in Phase 2 sobald produktive Tasks existieren.
  - **`backend/eb_digital/__main__.py`** `worker`-Subcommand:
    - `--queue` (repeatable) + `--concurrency`-Args.
    - `_cmd_worker` ruft `configure_logging` vor dem `asyncio.run(_run_worker(...))` (analog zu `_cmd_serve` mit uvicorn — JSON-Logs propagieren via Root).
    - `_run_worker` öffnet `procrastinate_app.open_async()` und ruft `run_worker_async`. KeyboardInterrupt → exit 0 (Procrastinate behandelt SIGINT/SIGTERM intern und ruft sauberen Shutdown).
    - mypy-Reibung mit Procrastinate's `WorkerOptions`-TypedDict (deklariert `queues: Iterable[str]` ohne `Optional`, Doku sagt aber `None = alle queues`): umgangen durch konditionalen kwarg-Pass + `# type: ignore[arg-type]` mit Begründungs-Kommentar.
  - **`docker-compose.yml`** `worker`-Service im `dev`-Profil: `build: docker/Dockerfile.backend`, `image: eb-digital-backend:dev`, `depends_on: db (healthy)`, `command: ["python", "-m", "eb_digital", "worker"]`, `env_file: .env`, `restart: unless-stopped`. `DATABASE_URL` über Compose-Network `db:5432`.
  - **`docker/Dockerfile.backend`** multi-stage (builder/runtime), Python 3.13.13-slim, uv 0.11.0, copy von `pyproject.toml + uv.lock + README.md + LICENSE + backend/ + alembic.ini`, `uv sync --frozen --no-dev`. Default-CMD `python -m eb_digital serve` (für 1.8 Backend-Server-Service); worker-Service überschreibt CMD. UID/GID 1000 als non-root. **Wird in 1.8 wiederverwendet** für den `backend`-Service — kein zweites Image nötig.
  - **21 neue Tests** in `backend/tests/test_jobs.py` (7), `test_migration_splitter.py` (11), Erweiterung von `test_main.py` (3 zusätzliche Worker-CLI-Tests).
  - **`.pre-commit-config.yaml`** mypy-Hook `additional_dependencies` um `procrastinate~=3.8.1` und `psycopg[binary,pool]~=3.3.4` erweitert (analog zu 1.4 für sqlalchemy/asyncpg/alembic).
  - **`pyproject.toml`** Coverage-Source-Pfad von `backend/eb_digital` auf `eb_digital` (Modul-Name) gewechselt — der Editable-Install-Pfad wird korrekt erkannt, die `0%`-Coverage-Reibung mit der neuen conftest-Top-Level-Logik ist behoben.
  - **`backend/tests/conftest.py`:** ENV-Defaults werden jetzt **am Modul-Top-Level** via `os.environ.setdefault` gesetzt (für Test-Collection-Time, weil `eb_digital.jobs` die Settings beim Import lädt). Pro-Test-Override über Fixture bleibt erhalten. `from eb_digital.settings ...` bewusst nur in der Fixture (nicht Top-Level), damit Coverage das Modul beim ersten Test-Import sieht.
- **Verifikations-Sequenz (alle Akzeptanzkriterien aus Fahrplan 1.5 erfüllt):**
  1. ✅ Lokaler Smoke-Test: ping deferred → Worker-Pickup nach <1 s → `ping_task_executed` + `Result: pong` als JSON-Logs.
  2. ✅ Lokaler SIGTERM-Test: `kill -TERM <pid>` → Worker stoppt nach 2 s mit Stop-Sequenz.
  3. ✅ Container-Smoke-Test: Image gebaut, Worker im Container läuft, ping deferred, Job durchgeführt mit identischer Log-Sequenz.
  4. ✅ Container-SIGTERM-Test: `docker compose stop worker` → sauberer Shutdown in <1 s.
  5. ✅ `alembic upgrade head` + `alembic check` (No new upgrade operations) + `alembic downgrade 660e1a12a41a && upgrade head` Roundtrip.
  6. ✅ `uv run ruff check backend` + `ruff format --check backend` + `uv run mypy --strict` alle grün (9 source files).
  7. ✅ `uv run pytest` 66 Tests grün, Coverage **92 %** gesamt.
  8. ✅ `uv run pre-commit run --all-files` grün auf allen Hooks.
- **Reibungen während der Session:**
  - **Methoden-Erfolg — STOPP-Disziplin bei Lizenz-Reibung:** Vor jeder Code-Änderung mit psycopg habe ich die Lizenz-Reibung erkannt, einen STOPP-Block im CLAUDE.md-Format formuliert und Patrick zur Entscheidung vorgelegt. Disziplin gewahrt; ADR + Regel sind solide dokumentiert; methodische Lücke (Sub-Dep-Lizenz-Prüfung) ist dauerhaft geschlossen.
  - **asyncpg-Multi-Statement-Limit:** Schon vor dem ersten Migrations-Lauf erwartet (`cannot insert multiple commands into a prepared statement`); Splitter pragmatisch implementiert, mit 11 Tests abgesichert. Alternative (separate psycopg-Sync-Connection in der Migration) wäre transaktions-fragiler gewesen — der Splitter hält die DDL in der Alembic-Outer-Transaktion.
  - **`alembic check` mit externem Schema:** Procrastinate verwaltet seine Tabellen selbst (eigenes Migrations-System bei zukünftigen Major-Updates). Ohne `include_object`-Filter würden Autogenerate und `alembic check` Drop-Operationen für die `procrastinate_*`-Tabellen vorschlagen. Filter blendet sie aus — saubere Koexistenz.
  - **`_editable_impl_*.pth`-Reibung dritte Iteration:** trat erneut nach `uv sync --reinstall-package eb-digital` auf. Heilung 1.4 (`rm -rf .venv && uv sync`) wirkte. Drittauftritt rechtfertigt einen Blocker-Stub-Eintrag noch nicht — Heilung ist deterministisch und einzeilig. Sollte das viertes Mal kommen, lege ich einen formalen Blocker an.
  - **mypy-Hook-Korruption während Verifikation:** `ModuleNotFoundError: No module named '0aca9ce3d91742c5b361__mypyc'` nach einem mid-Session venv-Reinstall. `uv sync --reinstall-package mypy` heilte sofort. Vermutlich pre-commit-mypy-Hook-venv-Cache-Konflikt; Wiederholung nicht beobachtet.
  - **Coverage-Source-Pfad-Issue:** Mit der neuen conftest-Top-Level-`os.environ.setdefault`-Logik und der Beibehaltung des `--cov=backend/eb_digital`-Pfads (statt Modul-Name) zeigte coverage `0%` mit Warnung „Module backend/eb_digital was never imported". Wechsel auf `--cov=eb_digital` heilte. Dauerhafte Verbesserung — Modul-Name ist auch der robustere Pfad bei Editable-Installs. Diff in `pyproject.toml`.
  - **Methoden-Lerneffekt — Container-Smoke-Test ist Pflicht in 1.5, weil 1.8 erst kommt:** Akzeptanzkriterien aus dem Fahrplan-Schritt 1.5 verlangen explizit „Worker-Container im Compose-`dev`-Profil". Der lokale Smoke-Test allein hätte das `eb-worker`-Compose-Snippet nicht validiert. Image-Build + Container-Run + Container-SIGTERM ist der entscheidende Schritt — und hat den fehlenden `README.md`+`LICENSE`-Copy im Dockerfile vor dem Commit aufgedeckt (Bugfix in derselben Iteration).
- **Reaktiv-Quote nach dieser Session:** **0/11 (0 %)**. Schwellenwert 20 % nicht erreicht. ADR-011 ist klar `[OPERATIV]` (planmäßige Nachzieh-Festlegung im Rahmen einer strategisch fixierten Stack-Wahl, kein Pivot).
- **Nächster Schritt:** **Phase 1 Schritt 1.6 — backend/auth Admin-Bootstrap-CLI** _oder_ **1.7 — Frontend-Workspaces + PWA-Skelett** (parallelisierbar laut Fahrplan). Versions-Re-Verifikation für `argon2-cffi` (1.6) bzw. `svelte`/`@sveltejs/kit`/`vite` (1.7) zu Sessionstart.

### 2026-05-09 – [ADR-ANGELEGT]

- **ADR-011** `[OPERATIV] [STACK] [METHODIK]` – „psycopg LGPL-3.0-only akzeptiert plus Sub-Dependency-Lizenz-Regime". Auslöser: Aufnahme von `procrastinate~=3.8.1` für Schritt 1.5 deckte auf, dass die Pflicht-Sub-Dependency `psycopg` (psycopg3) LGPL-3.0-only ist und damit gegen die Lizenz-Restriktion in `project-context.md` Abschnitt 6 verstößt. ADR-002 (Stack-Wahl) hatte das nicht adressiert — methodische Lücke (Modus-2-Schritt-2a deckt nur Top-Level-Komponenten).
- **Entscheidung Patrick: Option C** (psycopg-Akzeptanz **plus** Methodik-Regel). Ich hatte A/B/C als Optionen vorgelegt, C empfohlen. Patrick bestätigte „c".
- **Konkrete Festlegungen:** Geltungsbereich der LGPL-Verschmutzung auf Persistenz-/Job-Engine-Pfad beschränkt; Module ohne Job-Engine (`infra/tile-proxy`, Routing-Adapter) bleiben extraktionsfähig. `psycopg[binary,pool]~=3.3.4` wird als **explizite** Runtime-Dep gepinnt (nicht nur transitiv), Begründung Build-Reproduzierbarkeit auf macOS und im Docker-Container ohne libpq-System-Package.
- **Regel-016** (Sub-Dependency-Lizenz-Prüfung im Verifikations-Regime) abgeleitet — schließt die methodische Lücke dauerhaft.
- **Reaktiv-Quote bleibt 0/10.** Klassifikation `[OPERATIV]`, weil planmäßige Nachzieh-Festlegung im Rahmen einer strategisch fixierten Stack-Wahl, kein Pivot.
- **Auswirkungen auf Schritt 1.5:** keine Verzögerung des Schritts selbst — nach ADR-Anlage geht es nahtlos mit Schema-Migration, Job-Modul und Worker weiter. Die Disziplin-Folge (Sub-Dep-Lizenz-Check für künftige Stack-Komponenten) ist methodisch ab sofort wirksam.

### 2026-05-09 – [SESSIONSTART]

- **Letzter Stand:** Phase 1 Schritt 1.4 am 2026-05-09 abgeschlossen (PR #10 `7dcc068` in `main`); 1.1–1.4 alle ERLEDIGT. Reaktiv-Quote 0/10. Keine aktiven Blocker. Keine offenen STOPP-Situationen.
- **Geplant für diese Session:** Phase 1 Schritt 1.5 — **Procrastinate-Setup + Worker.** Konkret: `procrastinate`-Pin nach Versions-Verifikation in `pyproject.toml` und `project-context.md` aufnehmen, eigene Migration für das Procrastinate-DB-Schema (`procrastinate apply-schema`-Output als Alembic-Migration), Modul `backend/eb_digital/jobs/` mit `ping`-Test-Job (`@app.task(name="ping")`), `__main__.py worker`-Subcommand durch echten Worker-Run ersetzen, `eb-worker`-Service im Compose-`dev`-Profil. Akzeptanzkriterien aus `fahrplan.md` Schritt 1.5: Job einreihen → Worker führt aus → „pong" im Log; Worker stoppt sauber bei `SIGTERM`.
- **Vorabprüfung:**
  - **Branch-Awareness:** `git fetch --all --prune` zu Sessionstart durchgeführt; Worktree-Branch `scp/romantic-shockley-190ddb` initial bei `a81e981` (PR #9), nach `git pull --ff-only` auf `7dcc068` synchron mit `origin/main` (PR #10 mit 1.4 wurde gemerged, der Worktree-SESSIONSTART zunächst „weiter mit 1.5" wurde durch Patrick mit Hinweis auf den letzten Commit korrigiert; Synchronisation nachgezogen). Worktree-Stand entspricht Fahrplan-Stand 1.4 ERLEDIGT, 1.5 OFFEN.
  - Phase 1 = UMSETZUNG. Schritt 1.5 hat Eingangskriterien: 1.4 ✓ (PostgreSQL läuft im Compose-`dev`-Profil, Async-Engine konfiguriert). Nicht freigabepflichtig laut Fahrplan.
  - Sonderregel Phase 1 (Eingangsdisziplin abgemildert) gilt weiter — Procrastinate-Job-Engine ist laut Reifegrad-Übersicht bereits `[BELASTBAR]` (Stack-fix), die Compose-Realisierung ist hier zu bauen.
  - **Versions-Re-Verifikation Pflicht für 1.5** (Notiz aus Schritt 1.1 + Modus-2-Schritt-2a): `procrastinate` wird hier neu gepinnt — Re-Verifikation auf offiziellen Quellen (PyPI + GitHub-Releases) zu Sessionbeginn, dann in `project-context.md` Abschnitt 3 mit `Verifiziert: 2026-05-09`-Stempel ergänzen. Ohne Verifikation keine Aufnahme ins Pinning-Set.
- **Reibung beim Sessionstart (gelöst):** Erster Sessionstart-Befund („1.4 OFFEN, weiter mit 1.5") basierte auf veraltetem Worktree-Stand (`a81e981`); ohne `git fetch --all` direkt nach Pflichtlektüre wurde der zwischenzeitlich gemergete PR #10 nicht gesehen. Patricks Hinweis „1.4 ist fertig, prüfe letzten Commit" hat das aufgedeckt. Wiederholung des **Lerneffekts vom 2026-05-08 22:22**: Branch-Awareness mit `git fetch --all --prune` gehört vor die Pflichtlektüre, nicht danach. Hier nochmal als Reibung dokumentiert; die fundamentale Methodik-Anpassung (`fetch` als Vor-Pflichtlektüre-Schritt in CLAUDE.md Abschnitt 2 verankern) bleibt projektmethodisch unerledigt.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/romantic-shockley-190ddb` (Opus 4.7 1M-Kontext).

### 2026-05-09 – [SESSIONENDE]

- **Session-Dauer:** ca. 1 h 45 min (Sessionstart bis Sessionende-Commit-Vorbereitung).
- **Bearbeitet:** Phase 1 Schritt 1.4 — **Datenbank + Alembic + ORM-Konventionen.** Status `[OFFEN]` → `[ERLEDIGT]`.
- **Erreicht:**
  - **Versions-Verifikation 1.4** (Modus-2-Schritt-2a-Disziplin): Recherche per `curl pypi.org/pypi/asyncpg/json` + GitHub-Releases → asyncpg 0.31.0 vom 2025-11-24 (~5,5 Monate alt), PostgreSQL-17-Support seit 0.30.0, einziger Breaking Change in 0.31.0 ist Drop Python 3.8 (irrelevant). Patrick wählte **Option A:** `asyncpg~=0.31.0`. In `pyproject.toml` und `project-context.md` Abschnitt 3 mit `Verifiziert: 2026-05-09`-Stempel ergänzt.
  - **DB-Plumbing-Schicht** (`backend/eb_digital/db/`):
    - **`__init__.py`** (40 Zeilen exec): `MetaData(naming_convention=…)` mit deterministischen Patterns für PK/FK/UQ/CK/IX (Voraussetzung für stabile Alembic-Autogenerate-Diffs); `Base(DeclarativeBase)` mit shared metadata; `TimestampMixin` mit `created_at`/`updated_at` als timezone-aware UTC und `onupdate=_utcnow` auf updated_at; `create_db_engine(database_url, echo=False) -> AsyncEngine`; `create_session_factory(engine) -> async_sessionmaker[AsyncSession]` mit `expire_on_commit=False` (FastAPI-Pattern). 100 % Coverage.
    - **`models.py`** (33 Zeilen exec): `HealthMarker(Base, TimestampMixin)` als Phase-1-Sentinel zur Setup-Validierung — UUID-PK mit `default=uuid.uuid4`, `label: str` mit `unique=True`, plus die zwei Audit-Spalten aus dem Mixin. Wird in Phase 2 entfernt, sobald echte Domain-Modelle existieren. 100 % Coverage.
  - **Alembic-Setup** mit Async-Template:
    - **`alembic.ini`** im Repo-Root: `script_location = backend/migrations`, `prepend_sys_path = backend`, `file_template = %(year)d%(month).2d%(day).2d_%(rev)s_%(slug)s` (sortierbares Datum-Präfix), `sqlalchemy.url =` leer (URL kommt zur Laufzeit aus Settings). `post_write_hooks` mit `exec`-Type für `ruff format` + `ruff check --fix`, sodass auto-generierte Migrationen direkt lint-konform sind.
    - **`backend/migrations/env.py`**: liest `Settings().database_url` zur Laufzeit (kein Hard-Coding), `async_engine_from_config` mit `NullPool` für Migrations-Runs, sync-Migration-Runner via `connection.run_sync(_run_sync_migrations)`, `compare_type=True` + `compare_server_default=True` für genaue Diff-Erkennung.
    - **`backend/migrations/script.py.mako`**: Standard-Alembic-Template, an PEP-8/Modern-Type-Style angepasst (`str | None` statt `Optional[str]`, `from __future__ import annotations`).
    - **`backend/migrations/versions/20260509_0bf0aa5ccee1_baseline.py`**: leere Baseline-Migration, manuell geschrieben (ohne autogenerate, weil DB-leer).
    - **`backend/migrations/versions/20260509_660e1a12a41a_add_health_marker.py`**: per autogenerate erzeugt — Tabelle `health_marker` mit korrekt benannten Constraints `pk_health_marker` und `uq_health_marker_label` (Naming-Convention angewandt).
  - **PostgreSQL-Service im Compose-`dev`-Profil** (`docker-compose.yml`): `postgres:17.9@sha256:347bc4e6…` (Digest am 2026-05-09 aus Docker Hub Registry-Manifest geholt mit Bearer-Token + `docker-content-digest`-Header), Volume `eb-digital-pg`, `pg_isready`-Healthcheck (5 s Interval, 10 retries, 10 s start_period), Port-Bind nur auf `127.0.0.1:5432` (kein public exposure). Schritt 1.5/1.6/1.8 erweitern dieses File später.
  - **19 neue Tests** in `backend/tests/test_db.py` (12 Tests) + `backend/tests/test_models.py` (7 Tests):
    - DB-Layer: Naming-Convention vollständigkeit, Base-Metadata-Sharing, Async-Engine-Konstruktion mit korrekten Dialekten (`postgresql+asyncpg`), `echo`-Default false + überschreibbar, Session-Factory mit `class_=AsyncSession` und `expire_on_commit=False`, async dispose-without-connect ist no-op, TimestampMixin-Audit-Spalten timezone-aware mit `onupdate`.
    - Models: Tabelle in metadata registriert, UUID-v4-PK-Default, `label`-Unique, Naming-Convention auf PK + Unique angewandt, TimestampMixin-Vererbung.
  - **Verifikations-Sequenz (alle Akzeptanzkriterien aus Fahrplan 1.4 erfüllt):**
    1. ✅ Postgres-Container `healthy` nach 11 Sekunden via `docker compose --profile dev up -d`.
    2. ✅ `alembic upgrade head` läuft zweistufig fehlerfrei (`(empty) → 0bf0aa5ccee1 → 660e1a12a41a`).
    3. ✅ `alembic revision --autogenerate -m "add health marker"` erkennt das HealthMarker-Modell, generiert die Migration, post-write-hook formatiert + lintet sie automatisch.
    4. ✅ `alembic check` (nach `alembic upgrade head`): „No new upgrade operations detected" — Idempotenz bestätigt, ORM-Modelle und Migrationen in Sync.
    5. ✅ Async-Session-Lifecycle gegen reale Postgres (`/tmp/eb_smoke_db.py`, später aufgeräumt): Insert mit auto-generierter UUID + timezone-aware Timestamps, Select mit `tzinfo`-Assertion, Delete in Transaction, `engine.dispose()` mit Pool-Status `Checked out connections: 0` → keine Connection-Leaks.
    6. ✅ `uv run pytest` 45 Tests grün (Coverage **95 %**: `db/__init__.py` 100 %, `db/models.py` 100 %, gesamt 95.03 %; Schwelle 80 % deutlich überschritten).
    7. ✅ `uv run ruff check backend` + `ruff format --check backend` + `uv run mypy --strict` (7 source files) alle grün.
    8. ✅ `uv run pre-commit run --all-files` grün — alle Hooks (Hygiene, ruff lint+format, mypy, bandit, prettier, actionlint) passieren.
- **Reibungen während der Session:**
  - **Methoden-Erfolg — Verifikations-Disziplin:** Versions-Frage an Patrick im Modus-2-Schritt-2a-Format formuliert (mit konkreter Recherche-Begründung und Optionen A/B). Patrick antwortete „a" → Pin in `pyproject.toml` und `project-context.md` mit Datum. Disziplin gewahrt.
  - **`alembic post_write_hooks` mit `console_scripts`-Type fand `ruff` nicht.** Erster autogenerate-Lauf produzierte zwar die Migration, der ruff-Hook scheiterte aber an `Could not find entrypoint console_scripts.ruff`. Ursache: uv installiert ruff zwar in `.venv/bin/ruff`, aber nicht als `console_scripts`-Entry-Point in der venv-Metadata. Lösung: Hook-Type auf `exec` umgestellt (`executable = ruff`). Zusätzlich `ruff check --fix` als zweiter Hook ergänzt, sodass autogenerate-Migrationen direkt sowohl formatiert als auch gelintet sind. Nach Korrektur lief der zweite autogenerate-Lauf sauber.
  - **Erneute `_editable_impl_*.pth`-Reibung** (zweites Mal nach 1.3): Direkter Smoke-Test (`uv run python /tmp/script.py`) konnte das `eb_digital`-Modul nicht importieren, obwohl `pytest` (mit eigenem Discovery) es findet. **Heilung 1.3** (`uv sync --reinstall-package eb-digital`) **wirkte diesmal nicht** — die `.pth`-Datei hatte den richtigen Pfad-Inhalt, aber `import _editable_impl_eb_digital` schlug fehl. **Wirksame Heilung:** `rm -rf .venv && uv sync` (komplette venv-Erneuerung) — danach lief der Smoke direkt durch. Lerneffekt: Wenn das ein drittes Mal auftritt, ist es ein Blocker mit Reproduktion (Datei kann unter `docs/blockers.md` als Stub angelegt werden, sobald reproduzierbar). Hypothese: Reihenfolge von uv-Operationen (sync → manueller Test → reinstall) erzeugt einen Cache-Zustand, den die nukleare Variante umgeht.
  - **Methoden-Lerneffekt — `alembic check` als Idempotenz-Bestätigung:** Nach `alembic upgrade head` zusätzlich `alembic check` aufgerufen, statt nur per Augenschein zu prüfen, ob ORM und Migration in Sync sind. „No new upgrade operations detected" ist die explizite Bestätigung. Sollte für jede Phase-1+-Schritt-Verifikation Standard werden, sobald die DB-Schicht aktiv ist.
- **Reaktiv-Quote nach dieser Session:** **0/10 (0 %)**. Schwellenwert 20 % nicht erreicht. Diese Session hat keinen ADR erzeugt — die asyncpg-Versions-Pin-Entscheidung ist operativ und in `project-context.md` Abschnitt 3 abgehandelt (Regel-001 ADR-002).
- **Nächster Schritt:** **Phase 1 Schritt 1.5 — Procrastinate-Setup + Worker** (Eingangskriterium 1.4 erfüllt) **oder** **Schritt 1.7 — Frontend-Workspaces + PWA-Skelett** (parallelisierbar, Eingangskriterium 1.1 erfüllt). Versions-Re-Verifikation für `procrastinate` zu Sessionstart 1.5 (Modus-2-Schritt-2a-Disziplin).

### 2026-05-09 – [SESSIONSTART]

- **Letzter Stand:** Phase 1 Schritt 1.3 am 2026-05-09 abgeschlossen (PR #9 `a81e981` in `main`). Reaktiv-Quote 0/10. Keine aktiven Blocker. Keine offenen STOPP-Situationen.
- **Geplant für diese Session:** Phase 1 Schritt 1.4 — **Datenbank + Alembic + ORM-Konventionen.** Konkret: PostgreSQL-Container im Compose-`dev`-Profil (Image-Stub, weil das Compose-File erst in Schritt 1.8 final entsteht — hier wird ein Snippet vorbereitet/dokumentiert), `backend/eb_digital/db/__init__.py` mit SQLAlchemy 2.0 Async-Engine + Session-Factory + `DeclarativeBase` mit Naming-Convention, Alembic-Init mit Async-Template, ein Test-ORM-Modell zur Validierung des Setups, Tests für Async-Session-Lifecycle. Akzeptanzkriterien aus `fahrplan.md` Schritt 1.4: `alembic upgrade head` läuft fehlerfrei, `alembic revision --autogenerate` erkennt Änderungen, Async-Session-Lifecycle in Tests funktioniert ohne Connection-Leaks.
- **Vorabprüfung:**
  - **Branch-Awareness korrekt verlaufen:** `git fetch --all --prune` zu Sessionstart durchgeführt. Worktree-Branch `scp/competent-sutherland-993194` ist auf HEAD `a81e981` (PR #9 gemerged), tracked `origin/main`, keine Divergenz. Worktree-Stand entspricht dem Fahrplan-Stand 1.3 ERLEDIGT, 1.4 OFFEN.
  - Phase 1 = UMSETZUNG. Schritt 1.4 hat Eingangskriterien: 1.3 ✓ (Backend-Skelett mit Settings-Modul existiert, `Settings.database_url` ist gepinnt). Nicht freigabepflichtig laut Fahrplan.
  - Sonderregel Phase 1 (Eingangsdisziplin abgemildert) gilt weiter — Datenbank-Layer wird hier als Plumbing aufgebaut, ohne produktive Tabellen (die kommen ab Phase 2).
  - **Versions-Re-Verifikation Pflicht für 1.4** (Notiz aus Schritt 1.1): `asyncpg` wird hier neu gepinnt — Re-Verifikation auf offiziellen Quellen zu Sessionbeginn, dann in `project-context.md` Abschnitt 3 mit `Verifiziert: 2026-05-09`-Stempel ergänzen. SQLAlchemy 2.0.49 + Alembic 1.18.x sind bereits in 1.1 verifiziert; Re-Bestätigung als Disziplin-Akt unmittelbar vor Aufnahme der DB-Schicht.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/competent-sutherland-993194` (Opus 4.7 1M-Kontext).

### 2026-05-09 – [SESSIONENDE]

- **Session-Dauer:** ca. 1 h 30 min (Sessionstart bis Sessionende-Commit-Vorbereitung).
- **Bearbeitet:** Phase 1 Schritt 1.3 — **Backend-Skelett (FastAPI + Settings + Logging)**. Status `[OFFEN]` → `[ERLEDIGT]`.
- **Erreicht:**
  - **Versions-Verifikation 1.3** (delegiert an Patrick auf Wunsch — er bat „du wirst im internet diese aufgabe selber erledigen und deine ergebniss mir vorlegen, ich entscheide"). Web-Recherche auf PyPI + GitHub Releases + raw pyproject.toml für beide neuen Pakete:
    - **uvicorn 0.46.0** (released 2026-04-23, 16 Tage alt): Python 3.13 voll unterstützt, keine EOL/Deprecation, letzter Breaking Change war 0.40.0 (Drop Python 3.9). `[standard]`-Extra bringt uvloop, httptools, websockets, watchfiles, PyYAML, python-dotenv. **Patrick wählte Option A:** `uvicorn[standard]~=0.46.0`.
    - **pydantic-settings 2.13.1** (released 2026-02-19, ~3 Monate alt): Python 3.13 voll unterstützt, `pydantic>=2.7.0` Constraint kompatibel mit unserem `pydantic~=2.13.0` Pin. **Patrick wählte Option B:** `~=2.13.1` statt der frischen 2.14.x-Linie (2.14.1 war erst am 2026-05-08 als Hotfix für 2.14.0 erschienen, „Stabilität vor Aktualität"-Linie analog zu Postgres 17 / mypy 1.20).
  - **`pyproject.toml`** Runtime-Dependencies um die zwei neuen Pakete erweitert; **`project-context.md`** Abschnitt 3 Sub-Block „Backend Frameworks und Bibliotheken" um beide Pakete mit `Verifiziert: 2026-05-09`-Stempel ergänzt; Begründung für 2.13.1 statt 2.14.x als Inline-Kommentar in beiden Dateien.
  - **Vier neue Backend-Dateien** unter `backend/eb_digital/`:
    - **`settings.py`** (20 Zeilen exec): `Settings(BaseSettings)` mit ENV-Loading, `Literal["dev","staging","production"]` für `environment`, `SecretStr` für `secret_key`/`tomtom_api_key`/`maptiler_api_key` (kein Default), `lru_cache`-gewrappter `get_settings()`. Eine eng begründete `# type: ignore[call-arg]`-Suppression, weil pydantic-settings die required Felder zur Laufzeit aus ENV nachlädt — mypy sieht das nicht.
    - **`logging.py`** (35 Zeilen exec): `JsonLogFormatter`, der Stdlib-LogRecords zu einem JSON-Objekt pro Zeile rendert. **9 sensitive Feld-Namen** in `REDACTED_FIELDS` aus `project-context.md` Abschnitt 6 (Datenschutz): `password`, `password_hash`, `access_code`, `access_code_hash`, `secret_key`, `session_cookie`, `tomtom_api_key`, `maptiler_api_key`, `email`, `coordinate_lat`, `coordinate_lng`. **Rekursive Redaction** durch verschachtelte Dicts und Lists (geht über das Fahrplan-Minimum hinaus — Lerneffekt aus dem Architektur-Constraint, dass Standortdaten oft als nested objects geliefert werden). `configure_logging` ist idempotent (clear handlers + add new). `_redact` hat eine `# noqa: ANN401`-Suppression mit Begründung („log extras are intentionally unbounded").
    - **`app.py`** (24 Zeilen exec): `create_app()`-Factory liefert FastAPI-Instanz mit Lifespan-Hook (ruft `configure_logging` + loggt `application_startup`/`application_shutdown`), `/api`-Router (leer, wird in Phase 2+ befüllt) und `/health`-Endpoint (200 OK, `{status: "ok", version: __version__}`).
    - **`__main__.py`** (37 Zeilen exec): Argparse mit Subcommands `serve`, `admin`, `worker`. `serve` ruft `uvicorn.run(..., factory=True, log_config=None)` und konfiguriert vorher `configure_logging` — dadurch propagieren uvicorn-eigene Logger (`uvicorn`, `uvicorn.access`, `uvicorn.error`) an Root mit unserem `JsonLogFormatter`. `admin` und `worker` sind explizite Stubs mit `TODO(fahrplan-ref: 1.6)` bzw. `1.5`-Kommentar und Exit-Code 2.
  - **5 Test-Dateien** unter `backend/tests/`:
    - `conftest.py` mit `_reset_env`-Autouse-Fixture (setzt alle ENV-Felder, leert `get_settings`-Cache).
    - `test_health.py` (2 Tests): TestClient gegen `create_app()`, `/health`-Inhalt + Content-Type.
    - `test_logging.py` (14 Tests): JSON-Format pro Zeile, Redaction für jeden der 9 sensitiven Felder einzeln (Parametrisiert), nested-Redaction durch dict/list, `configure_logging` ersetzt bestehende Handler, `exception` wird mit `exc_info` serialisiert.
    - `test_settings.py` (5 Tests): ENV-Loading, lru_cache, Required-Field-Validation, invalid environment, SecretStr-Repr-Schutz.
    - `test_main.py` (5 Tests): Subcommand-Required, Serve-Defaults, explizite Host/Port/Reload-Args, Admin-Stub-Exit-2, Worker-Stub-Exit-2.
  - **Verifikations-Sequenz (alle Akzeptanzkriterien aus Fahrplan 1.3 erfüllt):**
    1. ✅ `uv run ruff check backend` — All checks passed (nach 3 Initial-Befunden: UP037 in `__main__.py` fix + zwei ANN401 in `logging.py` mit `# noqa`+Begründung).
    2. ✅ `uv run ruff format --check backend` — 11 files already formatted.
    3. ✅ `uv run mypy` — Success: no issues found in 5 source files (mit `--strict`).
    4. ✅ `uv run pytest` — 26 passed in 0.28s; **Coverage 94 % gesamt** (settings/app/logging je 100 %, `__main__.py` 79 % weil `_cmd_serve` nicht im Unit-Test). Schwelle 80 % weit überschritten.
    5. ✅ `uv run pre-commit run --all-files` — alle Hooks grün (ruff, ruff format, mypy, bandit, prettier, actionlint).
    6. ✅ Smoke-Test mit echtem Server: `python -m eb_digital serve --host 127.0.0.1 --port 18001` → READY nach 12 × 0.25 s, `curl /health` → `{"status":"ok","version":"0.1.0"}`. Stdout-Log: alle 6 Zeilen valides JSON (4 × `uvicorn.error`, 1 × `uvicorn.access`, 1 × `eb_digital.app`).
- **Reibungen während der Session:**
  - **Methoden-Erfolg — Versions-Verifikations-Disziplin hat funktioniert:** Mein erster Versuch im Session-Verlauf war, eine VERIFIKATIONS-FRAGE an Patrick zu stellen (analog zum Modus-2-Schritt-2a-Format). Das war strikt korrekt nach `project-context.md` Abschnitt 3 („Pflicht-Vermerk `Verifiziert: YYYY-MM-DD`") und Schritt 1.1-Notiz. Patrick hat das delegiert („du wirst im internet diese aufgabe selber erledigen und deine ergebniss mir vorlegen, ich entscheide") — die Recherche kostete ~10 min, die Entscheidung „A/B" war eine Antwort. Disziplin gewahrt, Reibung minimal.
  - **uvicorn-Logger-Reibung schon spät im Loop entdeckt:** Erster Smoke-Test zeigte 4 plain-Text-Zeilen (`INFO: Started server process …`) plus 1 JSON-Zeile. Akzeptanzkriterium „valides JSON pro Zeile" verletzt. Ursache: uvicorn richtet `uvicorn`/`uvicorn.access`/`uvicorn.error`-Logger per Default mit eigener `LOGGING_CONFIG` ein, die unsere Root-Konfiguration überschreibt. Lösung: `_cmd_serve` ruft `configure_logging` vor `uvicorn.run` auf und übergibt `log_config=None` — dadurch propagieren uvicorn-Logger an Root mit `JsonLogFormatter`. Zweiter Smoke-Test: 6/6 Zeilen valides JSON. Lerneffekt: Akzeptanzkriterien beim Implementieren mitsehen, nicht nur als Endprüfung — der Bug wäre ohne expliziten JSON-Validator-Loop in der Smoke-Test-Sequenz unentdeckt geblieben.
  - **`_editable_impl_*.pth`-Reibung mit `uv run` (Einmal-Vorfall):** Zwischen pytest (grün) und Smoke-Test (`No module named eb_digital`) zeigte sich, dass das Editable-Install-`.pth`-File nach manuellem Re-Schreiben nicht mehr von Python's site.py prozessiert wurde, obwohl es identische Bytes hatte. Diagnose-Schleife: `xxd` der Datei, marker-`.pth` mit `print()` zum Beweis dass `_editable_impl_*` filename-Pattern gefiltert wird, während `zzz_marker.pth` läuft. **Heilung: `uv sync --reinstall-package eb-digital`** — danach funktionierten sowohl direkter `.venv/bin/python` als auch `uv run`. Kein dauerhaftes Problem, kein ADR. Sollte das wiederkommen, ist die einzeilige Heilung dokumentiert.
  - **Methoden-Lerneffekt — Smoke-Test als Akzeptanz-Pflicht-Schritt:** Die Akzeptanzkriterien aus dem Fahrplan-Schritt 1.3 ließen sich NUR durch echten Server-Start verifizieren — Tests allein hätten die uvicorn-Logger-Reibung nicht aufgedeckt (TestClient umgeht uvicorn vollständig). Lerneffekt: für jeden Phase-1-Schritt mit Akzeptanzkriterium „Tool X läuft" oder „Endpoint Y antwortet" ist der lokale Smoke-Test Pflicht, nicht optional.
- **Reaktiv-Quote nach dieser Session:** **0/10 (0 %)**. Schwellenwert 20 % nicht erreicht. Diese Session hat keinen ADR erzeugt — die Versions-Pin-Entscheidungen sind operativ und in `project-context.md` Abschnitt 3 abgehandelt (entspricht Regel-001 ADR-002 „Patch frei, Minor ohne ADR, Major mit ADR").
- **Nächster Schritt:** **Phase 1 Schritt 1.4 — Datenbank + Alembic + ORM-Konventionen.** Eingangskriterium erfüllt: Backend-Skelett mit Settings-Modul existiert (Settings.database_url ist gepinnt). Versions-Re-Verifikation für `asyncpg` zu Sessionstart 1.4 (Modus-2-Schritt-2a-Disziplin).

### 2026-05-09 – [SESSIONSTART]

- **Letzter Stand:** Phase 1 Schritt 1.2 am 2026-05-08 abgeschlossen (PR #5 `1cd72df` in `main`); ADR-010 + Verifikations-Lücke + actionlint-Hook im selben Tag als Folge-Aktion (PR #7 `22b6a0f` in `main`); Sessionende-Folge-Eintrag in `268f25e` plus PR #8 `3c4ce89`. Reaktiv-Quote 0/10. Keine aktiven Blocker. Keine offenen STOPP-Situationen.
- **Geplant für diese Session:** Phase 1 Schritt 1.3 — **Backend-Skelett (FastAPI + Settings + Logging)**. Konkret: `backend/eb_digital/{__main__.py, app.py, logging.py, settings.py}` plus `backend/tests/` mit ersten Tests (Health-Endpoint, Logger-Redaction, Settings-Loading). Akzeptanzkriterien aus `fahrplan.md` Schritt 1.3: `uv run python -m eb_digital serve` startet Uvicorn auf Port 8000, `curl http://localhost:8000/health` liefert `{status: "ok", version: "0.1.0"}`, Log-Output ist valides JSON pro Zeile, Redaction von `password`-Feldern wirkt, `mypy --strict` läuft fehlerfrei. Ab erstem Test wird der bisher geskipte CI-Job `Backend · Tests & Coverage` regulär ausgeführt.
- **Vorabprüfung:**
  - **Branch-Awareness korrekt verlaufen** (Lerneffekt aus 2026-05-08-Sessions umgesetzt): `git fetch --all --prune` zu Sessionstart durchgeführt. Worktree-Branch `scp/sweet-gates-d730ca` ist auf HEAD `3c4ce89` (PR #8 gemerged), tracked `origin/main`, keine Divergenz. Worktree-Stand entspricht dem Fahrplan-Stand 1.2 ERLEDIGT, 1.3 OFFEN.
  - Phase 1 = UMSETZUNG. Schritt 1.3 hat Eingangskriterien: 1.1 ✓, 1.2 ✓, uv-Workspace ✓, Logging-Disziplin in `project-context.md` Abschnitt 6 verankert ✓. Nicht freigabepflichtig laut Fahrplan.
  - Sonderregel Phase 1 (Eingangsdisziplin abgemildert) gilt weiter — `backend/auth` und Settings-Module sind `[VORLÄUFIG]`, das ist für Skelett-Aufbau in Phase 1 zulässig.
  - **Versions-Re-Verifikation Pflicht für 1.3** (Notiz aus Schritt 1.1, „Versions-Verifikation für nachgelagerte Schritte"): `uvicorn`, `pydantic-settings` werden hier neu gepinnt — Re-Verifikation auf offiziellen Quellen zu Sessionbeginn, dann in `project-context.md` Abschnitt 3 mit `Verifiziert: 2026-05-09`-Stempel ergänzen. Ohne Verifikation keine Aufnahme ins Pinning-Set (Modus-2-Schritt 2a-Disziplin gilt durchgehend).
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/sweet-gates-d730ca` (Opus 4.7 1M-Kontext).

### 2026-05-08 23:55 – [SESSIONENDE]

- **Session-Dauer (Folgeblock nach 23:25):** ca. 30 min (23:25 – 23:55).
- **Bearbeitet:** Folge-Aktion zu Schritt 1.2: **ADR-010 plus Verifikations-Lücke geschlossen**. Auslöser war Patricks direkte Reaktion auf das Sessionende-Bulletin („das scheint ernst zu sein, eigentlich wollte ich mit der versions verifikation genau sowas verhindern, veraltete software"). Mein Vorschlag A (drei Aktionen in einem PR) wurde freigegeben.
- **Erreicht:**
  - **ADR-010 `[OPERATIV] [STACK] [DEPLOYMENT]`** – Major-Update GitHub-Actions plus Aufnahme aller Actions ins Verifikations-Regime. Reaktiv-Quote bleibt **0/10** (planmäßiges Update gegen bekannte Deprecation-Frist, kein Pivot). Plus **Regel-015** (GitHub-Actions im Verifikations-Regime).
  - **`project-context.md` Abschnitt 3** um Sub-Block „GitHub Actions" erweitert. Sechs Actions tragen jetzt `Verifiziert: 2026-05-08`-Stempel: `actions/checkout@v6`, `actions/setup-python@v6`, `actions/setup-node@v6`, `actions/upload-artifact@v4`, `astral-sh/setup-uv@v8.1.0`, `pnpm/action-setup@v6.0.5`. Plus actionlint 1.7.x im Repository-Tooling-Block.
  - **Workflow-Pin-Updates:** `astral-sh/setup-uv@v5.0.0` → `@v8.1.0`, `pnpm/action-setup@v4.0.0` → `@v6.0.5` in `ci.yml` und `security.yml`.
  - **`actionlint`-Pre-Commit-Hook** (`rhysd/actionlint@v1.7.12`) in `.pre-commit-config.yaml`. Schließt die Reibung aus Lerneffekt 2 vom 23:25-Sessionende-Eintrag.
  - **PR #7** erstellt und als Merge-Commit `22b6a0f` in `main` gemerged. Erster Merge-Versuch lief in einen GitHub-API-Race („base branch policy prohibits the merge", obwohl `mergeStateStatus: CLEAN`); zweiter Versuch sofort erfolgreich. Keine Branch-Protection-Aufweichung nötig.
  - **Verifikation:** lokal `actionlint` 0 Findings; pre-commit-Run inkl. neuem actionlint-Hook grün; CI-Run https://github.com/Paddel87/EB-Digital/actions/runs/25580741945 alle Backend-Jobs `success`, Frontend-Jobs `skipped`; Security-Run https://github.com/Paddel87/EB-Digital/actions/runs/25580771681 alle drei Audits `success`. **Wichtig: keine Node-20-Deprecation-Annotations mehr** — Major-Update wirkt. Einzige Annotation jetzt: harmlose Cache-Race-Warning beim ersten Lauf mit der neuen setup-uv-Major-Version, beim nächsten Lauf weg.
- **Methoden-Lerneffekt — Verifikations-Lücke war strukturell, nicht ein einmaliger Übersehen-Fehler:**
  - Modus-2-Schritt 2a (Versions-Verifikation) deckte explizit nur Sprachen, Bibliotheken, Datenbanken, Infrastruktur, Package-Manager ab. GitHub-Actions waren in `project-context.md` Abschnitt 3 nur als Hinweis in Abschnitt 7 erwähnt, ohne Versionen und ohne Stempel.
  - In Modus-2-Schritt 10 wurden zwei Actions als Annahme gepinnt (`v5.0.0`/`v4.0.0`) mit Verschiebung der Verifikation auf 1.2.
  - Bei der 1.2-Verifikation habe ich gesehen, dass die Major-Linien aktuell v8/v6 sind, aber „bei der Annahme bleiben" empfohlen mit falscher Berufung auf „Stabilität vor Aktualität". Das Prinzip „Stabilität vor Aktualität" gilt für **bewusste Zurückhaltung mit Begründung** (Postgres 18 jung, mypy 2.0 frisch), nicht für **unverifizierte Annahmen aus Modus 2**.
  - Patricks Eskalation („das scheint ernst zu sein") hat den Fehler aufgedeckt. Ohne ihn wäre die Node-20-Deprecation am 2026-06-02 als CI-Reibung in einer späteren Phase aufgeschlagen.
  - Strukturkorrektur: ADR-010 + Regel-015 + Sub-Block in `project-context.md` Abschnitt 3 schließen die Lücke dauerhaft. Künftige Action-Updates folgen demselben Verifikations-Regime wie alles andere.
- **Methoden-Lerneffekt — actionlint-Hook gehört von Anfang an dazu, nicht erst nach erstem Bug:**
  - Die hashFiles-Job-Level-Reibung in 1.2 (Commit `f94ee93`) hat eine Push-Iteration gekostet plus Forensik via API. `actionlint` hätte das vor dem Push gefangen.
  - Hook ist jetzt im Pre-Commit-Repo verankert, künftige Workflow-Edits werden lokal validiert.
- **Reaktiv-Quote nach dieser Session:** **0/10 (0 %)**. Schwellenwert 20 % nicht erreicht. ADR-010 ist klar `[OPERATIV]`, kein `[REAKTIV]`-Pivot.
- **Nächster Schritt unverändert:** Phase 1 Schritt 1.3 (Backend-Skelett FastAPI + Settings + Logging).

### 2026-05-08 23:25 – [SESSIONENDE]

- **Session-Dauer:** ca. 1 h (22:22 – 23:25).
- **Bearbeitet:** Phase 1 Schritt 1.2 – CI-Pipeline aktivieren. Patrick gab beim Sessionstart drei A-Empfehlungen frei (Action-Pins v5.0.0/v4.0.0 beibehalten, Frontend-Jobs guarden, Branch-Protection via gh api).
- **Erreicht:**
  - **Workflow-Anpassungen `ci.yml` / `security.yml`:** zwei iterative Commits notwendig.
    - **Commit `f94ee93`** (erster Versuch, fehlerhaft): `if: hashFiles(...)` direkt auf Job-Ebene gesetzt. GitHub-Actions-Validator lehnte beide Workflows ab (0s-Run, „workflow file issue"). Lokal mit `actionlint` (frisch via `brew install actionlint` installiert) bestätigt: `hashFiles()` ist **nur in `steps.*`-Kontext** erlaubt.
    - **Commit `632cead`** (Bugfix): Vorschalt-Job `detect-presence` mit Step-Skript-Check (`find apps -name package.json …` und `find backend/tests -name '*.py' …`), liefert Outputs `has_frontend`/`has_backend_tests`. Frontend- und `test-backend`-Jobs nutzen `needs: detect-presence` plus `if: needs.detect-presence.outputs.* == 'true'` – auf Job-Ebene erlaubt. **Zusätzlich pnpm-Multi-Version-Konflikt entschärft:** `version`-Arg aus allen `pnpm/action-setup`-Steps entfernt, `packageManager: pnpm@11.0.0` in `package.json` ist jetzt Single Source of Truth. `PNPM_VERSION`-env-Variable in beiden Workflows entfernt. Lokal mit `actionlint` validiert (0 Findings).
  - **CI-Lauf:** alle 8 Jobs `success`/`skipped` wie erwartet. Run https://github.com/Paddel87/EB-Digital/actions/runs/25579380487
  - **Security-Lauf:** alle 3 Audits `success`. Run https://github.com/Paddel87/EB-Digital/actions/runs/25579458539. **Wichtige Annotation:** Node.js-20-Deprecation für `astral-sh/setup-uv@v5.0.0` und `pnpm/action-setup@v4.0.0` ab **2026-06-02** (in ~3 Wochen). Major-Update auf v8/v6 ist freigabepflichtig – als Folge-Mini-ADR vor 2026-06-02 zu erledigen, im Fahrplan-1.2-Block dokumentiert.
  - **PR #5** erstellt (`ci(phase-1): Schritt 1.2 — CI-Pipeline aktiviert`), via `gh pr merge 5 --merge` als Merge-Commit `1cd72df` in `main` gemerged (konsistent mit PR #1–#4).
  - **Branch-Protection** auf `main` aktiv via `gh api -X PUT repos/Paddel87/EB-Digital/branches/main/protection`. 8 Required Status Checks (`Backend · Lint & Format`, `Backend · Type-Check`, `Backend · Tests & Coverage`, `Detect · Code-Präsenz prüfen`, `Frontend · Lint & Format`, `Frontend · Type-Check`, `Frontend · Tests & Coverage`, `Frontend · Build`); `enforce_admins: false` (Patrick behält direkten Push), `required_pull_request_reviews: null`, `allow_force_pushes: false`, `allow_deletions: false`.
  - **Sessionende-Disziplin:** `fahrplan.md` Stand-Block + 1.2-Block aktualisiert (Status `[ERLEDIGT]`, Verifikations-Block, Reibungs-Dokumentation, Aktion-Versionierungs-Beobachtung); `README.md` Status-Block, Quick Start (jetzt mit `uv sync`/`pnpm install`/`pre-commit install`-Befehlen), „Nächste Schritte" auf 1.3 umgestellt, LICENSE-Hinweis korrigiert (Datei existiert seit 1.1).
- **Offen geblieben:**
  - **Schritt 1.3** (Backend-Skelett FastAPI + Settings + Logging) als nächster Phase-1-Schritt. Eingangsbedingungen: erfüllt – Settings-Felder-Liste in `.env.example` aus 1.1 vorhanden, Logging-Disziplin in `project-context.md` Abschnitt 6 verankert.
  - **Action-Major-Update auf `astral-sh/setup-uv@v8` und `pnpm/action-setup@v6`** als Mini-ADR vor 2026-06-02. Ohne Update verlieren die Actions Node-20-Support; ggf. funktional eingeschränkt.
  - **Reaktiv-Quote-Beobachtung:** Diese Session hat keinen ADR erzeugt. Reaktiv-Quote bleibt 0/9 (0 %). Der angekündigte Action-Major-Update-ADR wird in Folge-Session als `[STRATEGISCH] [STACK]` (nicht `[REAKTIV]`, weil planmäßige Antwort auf bekannte Deprecation-Frist, nicht auf einen Implementierungs-Bug).
- **Stimmung / Beobachtungen:**
  - **Methoden-Lerneffekt 1 — Branch-Awareness erneut verfehlt:** Pflichtlektüre nach CLAUDE.md Abschnitt 2 hat zu Sessionstart (22:22) keinen `git fetch --all`-Schritt, also zeigte mein Worktree den Stand vor PR #4 und ich interpretierte „1.2 starten" fälschlich als „1.1 fehlt noch". Patricks Hinweis „1.1 ist doch erledigt, prüfe die Dokumentation" hat das aufgedeckt. **Exakt der Lerneffekt 1 vom Sessionende 2026-05-08 00:30** — die CLAUDE.md-Methodik-Anpassung „parallele Worktree-Branches und offene PRs prüfen" ist überfällig. Bleibt aber außerhalb dieser Session zu klären (Methodik-Diskussion).
  - **Methoden-Lerneffekt 2 — actionlint früh einsetzen, nicht erst nach Validierungs-Fehlschlag:** Hätte ich `actionlint` direkt nach den Workflow-Edits laufen lassen, wäre der `hashFiles`-Job-Level-Bug sofort sichtbar gewesen. Stattdessen waren ein fehlgeschlagener Push, GitHub-Run-Forensik via API und manueller `brew install actionlint` nötig. Künftige Workflow-Änderungen: `actionlint` lokal vor jedem Commit. Empfehlung: in `.pre-commit-config.yaml` als Hook ergänzen (außerhalb dieser Session – verändert Tooling-Konfig, aber keine Methodik).
  - **Methoden-Lerneffekt 3 — pnpm-Multi-Version-Konflikt war als Bug schon im PR-#4-Run sichtbar (20:08), aber damals nicht als Schritt-1.2-Voraufgabe markiert.** Erst beim Forensik-Schritt der gescheiterten Validierung in dieser Session bin ich auf den Konflikt gestoßen. Künftige PR-Reviews: schon vor Branch-Protection prüfen, ob die existierenden CI-Jobs grün sind, und Reibungen früh dokumentieren statt sie kollektiv im nächsten Schritt aufzulösen.
  - **Beobachtung — Geskipte Jobs als Required Checks:** GitHub-Branch-Protection wertet `skipped` als „successful" für Required-Status-Checks. Damit kann das gesamte 8-Job-Set jetzt schon als Required konfiguriert werden, auch wenn die Frontend-Jobs erst ab 1.7 produktiv laufen. Saubere Lösung ohne Branch-Protection-Splitting in Phase-1-Schritten.
  - **Beobachtung — Iterativer Workflow-Bugfix:** Zwei Push-Iterationen für eine logische Aufgabe (1.2). Prä-Push-Validierung mit `actionlint` hätte den ersten Push komplett vermeiden können. Auf längere Sicht: lokale Tooling-Disziplin senkt PR-Lärm im Repo.
  - **Beobachtung — Node-20-Deprecation-Frist:** Drei Wochen ist eine kurze Frist für ein freigabepflichtiges Major-Update (CLAUDE.md Abschnitt 4 Punkt 3). Mini-ADR zum Update sollte spätestens in der nächsten Phase-1-Session vorgelegt werden, damit das Major-Update vor 2026-06-02 erfolgt ist – sonst gibt es ungeplante CI-Reibung in laufenden Schritten.

### 2026-05-08 22:22 – [SESSIONSTART]

- **Letzter Stand:** Phase 1 Schritt 1.1 am 2026-05-08 abgeschlossen (Status `[ERLEDIGT]` im Fahrplan), PR #4 `init(phase-1): Schritt 1.1 — Repository- und Workspace-Setup [ERLEDIGT]` am 2026-05-08 20:07 in `main` gemerged. Anschließend Bugfix-Commit `667377d fix(phase-1): LICENSE auf byte-Treue zur kanonischen AGPL-3.0 zurueckgesetzt` direkt auf `main`. Aktueller Stand `c47d293`. Reaktiv-Quote weiter 0/9, keine aktiven Blocker. CI-/Pre-Commit-Skelette aus Modus-2-Schritt 10 plus Phase-1-1.1-Anpassungen liegen lauffähig vor (lokale Pre-Commit-Verifikation in 1.1 erfolgt).
- **Geplant für diese Session:** Phase 1 Schritt 1.2 – CI-Pipeline aktivieren (`fahrplan.md` Phase 1 Schritt 1.2). Konkret: bestehende `.github/workflows/ci.yml` und `security.yml` gegen die 1.2-Akzeptanzkriterien abgleichen, Action-Pinning für `astral-sh/setup-uv` und `pnpm/action-setup` verifizieren (Annahme aus Modus-2-Schritt 10 war `v5.0.0`/`v4.0.0` — laut Logbuch beim ersten Run zu prüfen), Coverage-Mindestwert prüfen, Push auf Test-Branch zur Verifikation der Workflow-Auslösung, Branch-Protection auf `main` setzen (separater Schritt mit Patrick-Bestätigung wegen shared-state-Wirkung).
- **Vorabprüfung:**
  - **Methoden-Reibung beim Sessionstart:** Pflichtlektüre nach CLAUDE.md Abschnitt 2 erfolgte zunächst ohne `git fetch --all`. Der Worktree-Branch `scp/dreamy-liskov-be0c78` lag 6 Commits hinter `origin/main` (Stand vor PR #4). Folge: Schritt 1.1 wurde fälschlich als „noch offen" interpretiert und ein STOPP wegen Schritt-1.2-Eingabe vs. Fahrplan-Stand vorgeschlagen. Patricks Hinweis „1.1 ist doch erledigt, prüfe die Dokumentation" hat das aufgedeckt. **Exakt der Lerneffekt 1 vom 2026-05-08 00:30** (Branch-Awareness fehlt in Pflichtlektüre Abschnitt 2). Bestätigt damit erneut, dass die CLAUDE.md-Methodik-Anpassung „parallele Worktree-Branches und offene PRs prüfen" notwendig ist — bleibt aber außerhalb dieser Session zu klären (Methodik, nicht Projekt). Korrektur in dieser Session: `git fetch --all` + `git pull --ff-only` durchgeführt, falscher SESSIONSTART verworfen, dieser Eintrag ersetzt ihn.
  - Phase 1 = UMSETZUNG. Schritt 1.2 hat Eingangskriterien: Schritt 1.1 abgeschlossen ✓, Tooling-Konfigs existieren ✓, lokale Pre-Commit-Hooks laufen grün ✓. Nicht freigabepflichtig laut Fahrplan. Sonderregel Phase 1 (Eingangsdisziplin abgemildert) gilt weiter.
  - Keine aktiven Blocker, keine offenen STOPP-Situationen. Reaktiv-Quote 0/9.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/dreamy-liskov-be0c78` (1M-Kontext-Modell).

### 2026-05-08 22:10 – [BEOBACHTUNG]

- **Phase 1 Schritt 1.1 abgeschlossen — Status `[ERLEDIGT]`.** Auslöser: Patricks Bestätigung „grünes licht" zur lokalen Akzeptanz-Verifikation in der laufenden Session (uv und pnpm waren entgegen früherer Annahme installiert: `/opt/homebrew/bin/uv`, `~/.local/bin/pnpm`).
- **Verifikations-Sequenz (alle Akzeptanzkriterien erfüllt):**
  1. `uv sync` → `uv.lock` mit 81 Paketen erzeugt. ruff resolved auf `0.15.12`, pydantic auf `2.13.4`, sqlalchemy `2.0.49` exakt, mypy `1.20.2` exakt – alle Patches bleiben innerhalb der `~=`-Pin-Range.
  2. `pnpm install` → `pnpm-lock.yaml` mit `@commitlint/cli@20.5.0` und `@commitlint/config-conventional@20.5.0`.
  3. `uv run pre-commit install --hook-type pre-commit --hook-type commit-msg` → beide Hooks installiert.
  4. **Erster `pre-commit run --all-files`-Lauf:** `pre-commit/mirrors-prettier` v3.8.0-Tag existiert nicht mehr (Mirror archiviert, stoppt bei v4.0.0-alpha.x). Bugfix-Wechsel auf gepflegten Community-Fork `rbubley/mirrors-prettier` v3.8.0 (semantisch identisch, gleiche Prettier-Binary). Kein ADR nötig (Patch-Niveau-Repo-Wechsel ohne Architekturwirkung). Anschließend hat Prettier alle Markdown-/JSON-/YAML-/CJS-Dateien reformatiert (Tabellen-Padding, Quote-Style, Trailing-Komma) und `end-of-file-fixer` eine Final-Newline an `LICENSE` ergänzt.
  5. **Zweiter Versuch `git commit`:** Prettier wollte `pnpm-lock.yaml` reformatieren – `.prettierignore` neu angelegt mit Ausschluss für Lock-Files, Build-/Cache-Verzeichnisse und kanonisches LICENSE-File.
  6. **Dritter `pre-commit run --all-files`-Lauf:** alle Hooks grün. Commit `0a2257f` mit Lock-Files plus Auto-Fixer-Anpassungen.
  7. **Test-Commit Conventional:** `test: verify commitlint accepts conventional message` → commitlint-Hook akzeptiert, Commit `9eeadcc` angelegt. Bleibt als selbst-dokumentierender Verifikations-Beweis in der Branch-Historie.
  8. **Test-Commit Non-Conventional:** `this is a bad non-conventional commit message` → commitlint-Hook lehnt ab mit klaren Fehlermeldungen `subject may not be empty [subject-empty]` und `type may not be empty [type-empty]`. Kein Commit angelegt.
- **Beobachtungen für nachgelagerte Schritte:**
  - **Patch-Resolution unter `~=`-Range funktioniert wie erwartet:** ruff 0.15.0 → 0.15.12, pydantic 2.13.0 → 2.13.4. Keine Unannehmlichkeit, keine Breaking Changes – konsistent mit Regel-001 ADR-002.
  - **Prettier-Mirror-Diskontinuität:** das Risiko archivierter pre-commit-Mirrors ist real. Künftige Pin-Updates (Schritte 1.3 ff.) prüfen bei jedem Mirror, ob er noch lebendig ist. Falls weitere Mirrors archiviert werden, bewegt sich das Repo zu lokalen Hooks via pnpm/uv (wie es schon bei eslint/svelte-check/tsc-noemit der Fall ist).
  - **`commitlint`-Konfiguration als CJS-Datei:** funktioniert sauber mit pnpm und @commitlint/cli 20.5.0. Type-Enum-Liste auf die zehn project-context.md-Typen beschränkt; alle anderen Conventional-Defaults (subject-case, header-max-length 100) sind sinnvolle Zusatzregeln.
  - **`apps/`-Verzeichnis ist leer:** ESLint, svelte-check, tsc-noemit-Hooks zeigen „no files to check" und werden korrekt geskipt – Phase-1-Schritt-1.7 stellt die Frontend-Skelette her.
  - **Commit `9eeadcc` in der Branch-Historie:** ist ein Empty-Test-Commit ohne semantischen Wert für die Anwendung. Bewusste Entscheidung, ihn zu lassen, weil die Commit-Message selbst-dokumentierend ist und der Aufwand zur Entfernung (`git reset --soft HEAD~1`) eine History-Modifikation wäre. Im PR-Review-Vorgang kann er bei Bedarf zusammengefasst (Squash) werden.
  - **Verbliebene Test-Branch `test/precommit-verification`:** beim ersten Test-Versuch existierte sie schon (Reste eines früheren Versuchs), die Tests liefen trotzdem auf der Hauptarbeitsbranch (siehe Punkt 7+8). Branch hat keinen Wert und kann gelöscht werden – Patrick entscheidet bei nächster Repo-Aufräumung.
- **Methoden-Lerneffekt 1 — „installation in der repo wohl nicht vorhanden" ≠ „Tools fehlen":** ich hatte den User-Hinweis zu pessimistisch interpretiert (Tools nicht installiert) und Schritt 1.1 vorschnell als unvollständig ausgeflaggt. `which uv pnpm` hätte sofort Klarheit gebracht. Künftig: bei „Tool fehlt"-Annahmen erst `which`/`command -v` prüfen, dann verbalisieren.
- **Methoden-Lerneffekt 2 — Pre-commit-Auto-Fixer beim ersten Lauf sind erwartbar, kein Fehler:** wenn Prettier oder end-of-file-fixer beim Erstauf zuschlagen, ist das ein Sign für „Hooks arbeiten korrekt", nicht für Konfig-Bug. Erwartete Pattern: Erstauf rot mit Auto-Fix, Stage + Erneuter Lauf grün.
- **Methoden-Lerneffekt 3 — `.prettierignore` ist Pflicht von Anfang an:** ohne diese Datei formatiert Prettier alle YAML-Dateien einschließlich Lock-Files. Lock-Files dürfen aber nur vom Package-Manager geändert werden. Das war hier ein Lerneffekt, der jetzt im Vorlagen-Set vermerkt werden könnte (außerhalb dieser Session).

### 2026-05-08 14:50 – [BEOBACHTUNG]

- **Methodische Korrektur — Bash-Sandbox ohne Netz ≠ keine Web-Quelle erreichbar.** Im Eintrag 14:30 hatte ich nach dem fehlgeschlagenen `curl https://www.gnu.org/licenses/agpl-3.0.txt` (Verbindungs-Timeout aus der Bash-Sandbox) vorschnell geschlossen, der AGPL-3.0-Volltext sei in dieser Session prinzipiell nicht beschaffbar, und ihn als offenen Restpunkt im LICENSE-Stub belassen. Patricks Rückfrage hat das aufgedeckt.
- **Verfügbare alternative Routen für Web-Inhalte aus Claude-Code-Sessions** (für künftige Sessions zu merken):
  1. **`gh api`** für alles, was über die GitHub-API erreichbar ist – authentifiziert, sandbox-erlaubt, byte-genau (kein AI-Resümee dazwischen). Für Lizenztexte: `gh api licenses/<spdx-id>` liefert das `body`-Feld als kanonischen Text.
  2. **`WebFetch`** als deferred Tool – funktioniert auch ohne Bash-Netzwerkzugriff, schickt den Content aber durch ein kleines AI-Modell, das paraphrasieren oder summarisieren kann. **Nicht** geeignet für verbatim-pflichtige Texte (Lizenzen, Verträge, Standards), gut für „erkläre/extrahiere"-Anfragen.
  3. **`WebSearch`** als deferred Tool – für Discovery, nicht für Volltext.
  4. **`Bash` mit `curl`/`wget`** – in dieser Sandbox blockiert (Verbindungs-Timeout). Nicht zuverlässig.
- **Konkrete Auflösung:** AGPL-3.0-Text via `gh api licenses/agpl-3.0 --jq '.body' > /tmp/agpl-3.0.txt` geholt (662 Zeilen / 34 524 Bytes), in `LICENSE` unter dem Projekt-Header eingefügt. Kontroll-Daten: `head -3` zeigt „GNU AFFERO GENERAL PUBLIC LICENSE / Version 3, 19 November 2007", `tail -4` zeigt das kanonische FSF-Closing („For more information on this … <https://www.gnu.org/licenses/>"). Finale Datei 673 Zeilen / 35 035 Bytes. Restpunkt 2 in `fahrplan.md` Phase 1 Schritt 1.1 als gelöst markiert (Strikethrough plus „GELÖST 2026-05-08"-Vermerk im selben Listenpunkt, weil ein Logbuch-Eintrag das Detail trägt und der Fahrplan nur den aktuellen Zustand abbildet).
- **Festhalten als wiederkehrendes Muster:** Bei „Web-Quelle nötig, Sandbox blockt curl" zuerst prüfen, ob `gh api` (verbatim) oder `WebFetch` (paraphrasing-tolerant) die Aufgabe abdeckt – nicht direkt zu Stub + TODO greifen. Diese Lektion gehört in den projektübergreifenden CLAUDE-Methodik-Kanon, ist aber außerhalb dieser Session zu klären (vgl. ähnliche „Lerneffekt-für-CLAUDE.md"-Vermerke vom 2026-05-08 00:30).

### 2026-05-08 14:30 – [BEOBACHTUNG]

- **Phase 1 Schritt 1.1 begonnen, Konfig-Skelett angelegt; Schritt bleibt `[IN ARBEIT]`.** Umgesetzt:
  - `LICENSE` als AGPL-3.0-Header-Stub mit dokumentiertem TODO für den Volltext (Sandbox ohne Netzzugriff – Reproduktion des kanonischen FSF-Lizenztextes nicht zulässig). Volltext-Ergänzung als offener Akzeptanz-Restpunkt im Fahrplan.
  - `.gitignore` (Python: `__pycache__`, `.pytest_cache`, `.mypy_cache`, `.ruff_cache`, `dist`, `build`, `.venv`, `.uv-cache`; Node: `node_modules`, `.pnpm-store`; SvelteKit/Vite: `.svelte-kit`, `.vite`, `apps/*/build`, `.output`; Secrets: `.env*` außer `.env.example`; OS/IDE-Standard).
  - `.editorconfig` mit LF/UTF-8, 4-Spaces für Python (`max_line_length = 100`), 2-Spaces für TypeScript/Svelte/JSON/YAML, Markdown ohne `trim_trailing_whitespace`, Tab für Makefile.
  - `.env.example` mit allen Settings-Feldern aus Phase-1-Schritt-1.3 (`SECRET_KEY`, `SESSION_COOKIE_NAME`, `LOG_LEVEL`, `DATABASE_URL`, `VALKEY_URL`, `TOMTOM_API_KEY`, `MAPTILER_API_KEY`, `TILE_PROXY_BASE`, `PUBLIC_DOMAIN`) plus Postgres-Container-Init-Variablen für das spätere dev-Profil.
  - `pyproject.toml` mit uv-basierter Konfiguration, Python `>=3.13,<3.14`, License-Trove `AGPL-3.0-or-later`, Hatchling als Build-Backend mit `packages = ["backend/eb_digital"]`. Runtime-Deps mit Verifikations-Stempel 2026-05-07 gepinnt: fastapi `~=0.136.0`, sqlalchemy[asyncio] `~=2.0.49`, alembic `~=1.18.0`, pydantic `~=2.13.0`, httpx `~=0.28.0`, argon2-cffi `~=25.1.0`, itsdangerous `~=2.2.0` (Pin auf plausible Major, Verifikation in Schritt 1.6). uvicorn, pydantic-settings, asyncpg, procrastinate **bewusst nicht** in 1.1-pyproject.toml – werden in 1.3/1.4/1.5 mit erneuter Verifikation nachgepinnt. Dev-Group: pytest `~=9.0.0`, pytest-asyncio `~=1.3.0`, pytest-cov `~=7.1.0`, ruff `~=0.15.0`, mypy `==1.20.2` (exakt – „bewusst nicht 2.0.x"), bandit[toml] `~=1.9.0`, pip-audit `~=2.10.0`, pre-commit `~=4.6.0`. Tool-Konfigurationen für ruff (Regelset aus `project-context.md` Abschnitt 7), mypy `--strict`, pytest mit `asyncio_mode = "auto"` und `--cov-fail-under=80`, coverage mit Branch-Coverage, bandit-Test-Dir-Ausschluss.
  - `pnpm-workspace.yaml` mit drei Paketen `apps/frontend-{disponent,betreuer,einsatzkraft}` (Initialisierung in Schritt 1.7).
  - Root-`package.json` mit `packageManager: pnpm@11.0.0`, Engine-Constraints (`node >=24 <25`, `pnpm >=11 <12`), devDependencies `@commitlint/cli@20.5.0` und `@commitlint/config-conventional@20.5.0`. Workspace-Scripts (`lint`, `format`, `check`, `build`, `test`, `commitlint`).
  - `commitlint.config.cjs` extends `@commitlint/config-conventional`, Type-Enum auf zehn Typen aus `project-context.md` Abschnitt 7 beschränkt (`feat, fix, refactor, docs, test, chore, perf, build, ci, init`), Header-Max 100 Zeichen.
  - `.pre-commit-config.yaml` aus Modus-2-Schritt 10 um lokalen `commit-msg`-Hook für commitlint ergänzt; übrige Hooks (Hygiene, ruff, mypy, bandit, prettier, eslint/svelte-check/tsc-noemit) decken Phase-1-Anforderungen bereits ab und wurden unverändert gelassen.
  - `backend/eb_digital/__init__.py` mit `__version__ = "0.1.0"` als Backend-Package-Root angelegt (Hatchling-Wheel-Target verlangt das Paket-Verzeichnis).
- **Bewusst nicht angelegt in 1.1:**
  - `apps/frontend-*` – SvelteKit-Initialisierung erst in Schritt 1.7.
  - `infra/{tile-proxy,reverse-proxy}` – erst in Schritt 1.8.
  - Zusätzliche Module unter `backend/eb_digital/` (`app.py`, `settings.py`, `logging.py`, `db/`, `auth/`) – Schritt 1.3 ff.
- **Offene Akzeptanz-Restpunkte (Auflösung außerhalb dieser Session):**
  1. **`uv` und `pnpm` lokal installieren**, dann `uv sync` und `pnpm install` ausführen → Lock-Files committen. Bestätigung Patrick: Tools sind aktuell nicht im Repo-Worktree verfügbar.
  2. **AGPL-3.0-Volltext** ans `LICENSE`-File anhängen (von `https://www.gnu.org/licenses/agpl-3.0.txt`).
  3. **Pre-Commit-Hooks lokal validieren:** `pre-commit install`, `pre-commit run --all-files`, plus Test-Commits mit Conventional und Non-Conventional Message zur Verifikation des commitlint-Hooks.
- **Methoden-Notiz:** Phase-1-Schritt-1.1 ist nach CLAUDE.md Abschnitt 9 ohne Akzeptanzkriterien-Erfüllung (Lock-Files + Pre-Commit-Run + Commit-Lint-Test) **nicht `[ERLEDIGT]`-fähig**. Die Konfig-Dateien sind syntaktisch korrekt und intern konsistent, aber „grünes Pre-Commit-Run" lässt sich erst nach lokaler Tool-Installation verifizieren. Statt eines verfrühten `[ERLEDIGT]`-Markers bleibt der Status `[IN ARBEIT]` und die Restpunkte sind im Fahrplan-Eintrag konkret aufgeführt – konsistent mit CLAUDE.md Abschnitt 6 „Keine Erfolgsmeldungen ohne Verifikation".

### 2026-05-08 13:50 – [SESSIONSTART]

- **Letzter Stand:** Modus 2 (Initialisierung) am 2026-05-08 00:30 abgeschlossen, PR #3 gemerged auf `main` (Merge-Commit `5f5c7db`), zusätzlicher Sessionende-Commit `494a657 docs: Sessionende-Eintrag und Übergang Modus 2 -> Phase 1` ist bereits in `main`. Worktree `scp/competent-black-c11212` ist clean und auf Stand von `origin/main`. Repository enthält bislang: `CLAUDE.md`, `README.md`, `.pre-commit-config.yaml`, `.github/workflows/{ci,security}.yml`, `docs/` (vollständig), `templates/`. **Kein** `pyproject.toml`, `pnpm-workspace.yaml`, `package.json`, `.editorconfig`, `.gitignore`, `LICENSE`, `.env.example`, kein `backend/`, kein `apps/`, kein `infra/`.
- **Geplant für diese Session:** Phase 1 Schritt 1.1 – Repository- und Workspace-Setup (`fahrplan.md` Phase 1, Schritt 1.1). Erweitert um `LICENSE` (AGPL-3.0) und `.env.example` aus dem Sessionende-Vermerk vom 2026-05-08 00:30. Konkret: `pyproject.toml` (uv-basiert, Python 3.13, Dependencies aus `project-context.md` Abschnitt 3 verifiziert), `pnpm-workspace.yaml` mit drei Frontend-Paketen, Root-`package.json` (pnpm 11.x), `.editorconfig`, `.gitignore`, `commitlint.config.cjs`, Skelett-Verzeichnisse `backend/`, `apps/`, `infra/`. Ergänzend: `.pre-commit-config.yaml` aus Modus-2-Schritt 10 prüfen, ob es Schritt-1.1-Anforderungen vollständig deckt; nachsteuern statt Komplett-Überschreibung.
- **Vorabprüfung:** Phase 1 = UMSETZUNG. Sonderregel aus `fahrplan.md` Phase 1 abgemildert (Modul-Schnitt ist durch ADR-002, ADR-003, ADR-004 strategisch fixiert). Schritt 1.1 hat keine Abhängigkeiten und ist nicht freigabepflichtig (`project-context.md` Abschnitt 7 + 10 + ADR-002 fixieren das Tooling). Eingangskriterien erfüllt: Modus-2-Initialisierung abgeschlossen ✓, Tooling-Vorgaben in `project-context.md` Abschnitt 7 ✓, Repo-Regeln in `project-context.md` Abschnitt 10 ✓. Keine aktiven Blocker (`blockers.md`), keine offenen STOPP-Situationen (`fahrplan.md` Aktueller Stand). Reaktiv-Quote 0/9, weit unter 20 %-Schwellenwert.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus, Worktree `scp/competent-black-c11212` (1M-Kontext-Modell).

### 2026-05-08 00:30 – [SESSIONENDE]

- **Session-Dauer:** ca. 3 h (21:39 am 2026-05-07 – 00:30 am 2026-05-08).
- **Bearbeitet:** Modus-2-Schritte 5 bis 12 in einem Zug. Zu Sessionstart noch ein Branch-Sichtbarkeits-Problem behoben (Schritt 4 lag auf parallelem Worktree-Branch und war über `git log --all` sichtbar; PR #2 hat ihn während der Session in `main` gemerged).
- **Erreicht:**
  - **Schritt 5:** `decisions.md` mit ADR-001 bis ADR-009 plus 14 Entscheidungsregeln, Reaktiv-Quote 0/9 initialisiert. Konsistenz-Check `architecture.md` Abschnitt 8 auf konkrete ADR-Nummern. Commit `c0e89af`.
  - **Schritt 6:** `fahrplan.md` mit 7 regulären Phasen plus Phase X (Verbund später). Phase 1 voll detailliert in 8 Schritten 1.1–1.8 im vollen Schritt-Format. Spikes G–M in Phasen 3 + 5 platziert, Roadmap N/O/P in Phase 7. Commit `8cbccd6`.
  - **Schritt 7:** `blockers.md` auf Startzustand (Keine aktiven Blocker) plus Erkennungs-Heuristiken plus Eintrags-Format-Vorlagen. Commit `cc0f6a8`.
  - **Schritt 8:** `logbuch.md` Vorlagen-Cleanup (sechs Beispiel-Einträge plus Initialisierungs-Hinweis entfernt). Commit `3b782ec`.
  - **Schritt 9:** `README.md` aus Vorlagen-Zustand auf Statusbild gebracht. 7 Badges, Über-das-Projekt aus `vision.md`, Status-Block synchronisiert mit allen Pflicht-Dokumenten. Commit `857e55d`.
  - **Schritt 10:** CI- und Pre-Commit-Skelett (`.github/workflows/ci.yml`, `.github/workflows/security.yml`, `.pre-commit-config.yaml`). `release.yml` bewusst weggelassen (project-context.md: spätere Phase). Commit `44673af`.
  - **Schritt 11:** `vision.md` Überführungs-Status abgehakt. Vision eingefroren. Commit `b60d877`.
  - **Schritt 12:** Initialisierungs-Abschluss als PR #3 statt zusätzlichem Riesencommit (Methoden-Abweichung von CLAUDE.md Abschnitt 1A Schritt 12 dokumentiert). PR am 2026-05-08 gemerged, Merge-Commit `5f5c7db` auf `main`.
  - **Sessionende-Disziplin:** `fahrplan.md` Stand-Block aktualisiert auf „Modus 2 abgeschlossen, Phase 1 nächster Schritt"; `README.md` Status-Block (Projektphase, Letzte Änderung) und „Nächste Schritte" synchronisiert.
- **Offen geblieben:** Reguläre Phase 1 ist noch nicht begonnen. Erste Session der nächsten Phase startet mit Schritt 1.1 (Repository- und Workspace-Setup). Vor Phase-1-Beginn werden in Schritt 1.1 außerdem `LICENSE`-Datei (AGPL-3.0) und `.env.example` angelegt – das ist Teil von 1.1 „Repository-Setup".
- **Stimmung / Beobachtungen:**
  - **Methodischer Lerneffekt 1 – Branch-Awareness:** Pflichtlektüre nach CLAUDE.md Abschnitt 2 hat bei Sessionstart die Existenz des parallelen Worktree-Branches mit Schritt 4 nicht aufgezeigt. `git log` ohne `--all` zeigt nur den lokalen Branch-Stand. Vorschlag für CLAUDE.md-Update: in Abschnitt 2 Pflichtlektüre einen Punkt „parallele Worktree-Branches und offene PRs prüfen" ergänzen. Außerhalb dieser Session zu klären – nicht jetzt.
  - **Methodischer Lerneffekt 2 – Vorlage-Vorlage-Abstimmung:** Die README-Vorlage erwartet Status-Werte „alpha/beta/stable/maintenance/deprecated", `project-context.md` führt aber „Konzeption/Aufbau/aktive Entwicklung/Wartung/deprecated". Ich habe zugunsten von `project-context.md` (Quelle laut CLAUDE.md Abschnitt 16) entschieden, aber die Vorlagen-CLAUDE.md sollte projektübergreifend angeglichen werden. Ebenfalls außerhalb dieser Session.
  - **Methodischer Lerneffekt 3 – Phasen-Disziplin und Phasenanzahl:** Klasse G erlaubt 5–7 Phasen. Mit strikter Phasentyp-Trennung (CLAUDE.md Abschnitt 6: keine Spike+UMSETZUNG-Mischung) komme ich auf 7 Phasen ohne Verbund-Modus, der Phase X außerhalb der Hauptliste belegt. Falls der Verbund-Bedarf konkretisiert wird, muss die Hauptphasen-Liste neu strukturiert werden – damit dokumentiert in `Replanning-Historie`.
  - **Methodischer Lerneffekt 4 – Phase 1 Sonderregel:** UMSETZUNG-Eingangsdisziplin „alle berührten Bestandteile auf [BELASTBAR]" ist in einer Skelett-Phase nicht erfüllbar, weil die Module bis zur Implementierung VORLÄUFIG bleiben. Eingangsbedingung wurde abgemildert auf „Modul-Schnitt durch ADR strategisch fixiert". Bewusst dokumentiert, damit es in einer späteren Session nicht als versehentliche Aufweichung gelesen wird.
  - **Pragmatik der vielen Init-Commits vs. CLAUDE.md-Schritt-12-Vorgabe:** CLAUDE.md sieht einen einzigen Init-Commit vor; in der Praxis war es bei interaktiver Schritt-für-Schritt-Bearbeitung schöner, pro Schritt einen Commit zu machen. PR #3 hat das mit Sammeltitel zusammengeführt – funktioniert in der Praxis sauber und behält die Granularität für Nachvollziehbarkeit. Die CLAUDE.md-Formulierung könnte „eine Init-PR-Einheit" anstelle von „ein Init-Commit" sagen. Ebenfalls außerhalb dieser Session.
  - **Reaktiv-Quote:** 0/9 nach Init – sehr gute Ausgangslage. Erste reaktive Entscheidung wäre eine in Phase 1, die hoffentlich nicht eintritt. Beobachtung beim Phasen-Wechsel.

### 2026-05-08 00:10 – [BEOBACHTUNG]

- **Modus-2-Schritt 11 abgeschlossen, `vision.md` Überführungs-Status abgehakt und Vision eingefroren.**
- **Alle sechs Checkboxen** auf [x] gesetzt mit konkreten Verweisen auf die zugehörigen Modus-2-Schritte und Logbuch-Einträge:
  - Konzeptphase (Schritte 1+2+2a)
  - Härtungsphase (Schritt 3 plus Klärungs-Session Schublade 1)
  - Vorlagen-Set initialisiert (Schritte 4–10)
  - ADR-001 angelegt (plus Erwähnung von ADR-002 bis ADR-009)
  - Initialisierungs-Abschluss-Datum: 2026-05-07
- **Zusätzlich** am Block-Ende ein Hinweis ergänzt: Verbund-Modus-Reinterpretation V2 ist in ADR-009 dokumentiert und verändert die Vision **nicht**, sondern präzisiert die Anbieterseiten-Trennung als Default mit Delegations-Möglichkeit. Damit ist klargestellt, dass Frage F kein Vision-Pivot war.
- **Vision ist damit eingefroren.** Spätere substantielle Vision-Änderungen erfordern einen ADR mit Verweis auf den ursprünglichen Vision-Abschnitt; Vision-Datei wird inhaltlich nicht mehr verändert.
- **Nicht angefasst:** Vision-Abschnitte 1–10. Diese bleiben als historisches Eingangs-Dokument unverändert.

### 2026-05-07 23:55 – [BEOBACHTUNG]

- **Modus-2-Schritt 10 abgeschlossen, CI-Workflow- und Pre-Commit-Skelett angelegt.**
- **Plan vorab vorgelegt und bestätigt** mit fünf zu klärenden Punkten: Action-Patch-Pins (`v5.0.0`/`v4.0.0` als Annahme), Pre-Commit-Hook-Patches (`.0`-Patches der Minor-Linien), initial rote Runs OK, security.yml beschränkt auf Dep-Audits + bandit (kein Duplikat-eslint-security), `release.yml` nicht jetzt.
- **`.github/workflows/ci.yml`** mit 7 Jobs angelegt:
  - Backend (3 Jobs): `lint-backend` (ruff check + format), `typecheck-backend` (mypy --strict), `test-backend` (pytest + Coverage 80 %).
  - Frontend (4 Jobs): `lint-frontend` (eslint + prettier --check), `typecheck-frontend` (svelte-check + tsc), `test-frontend` (vitest, Matrix über drei Frontend-Pakete), `build-frontend` (pnpm -r build).
  - Trigger: `push` (alle Branches) plus `pull_request` (main).
  - Tooling: uv für Python (statt pip aus dem Template), pnpm für TypeScript.
- **`.github/workflows/security.yml`** mit 3 Jobs angelegt:
  - `dep-audit-backend` (pip-audit `--strict --vulnerability-service=osv`).
  - `dep-audit-frontend` (pnpm audit `--audit-level=high`).
  - `static-security-backend` (bandit `-c pyproject.toml`).
  - Trigger: `schedule` (cron `0 6 * * 0`) plus `workflow_dispatch`.
  - Bewusst weggelassen: separater eslint-plugin-security-Lauf (läuft im regulären lint-frontend-Job mit).
- **`.pre-commit-config.yaml`** mit Hooks für beide Sprachen plus generelle Hygiene-Hooks angelegt:
  - General: trailing-whitespace, end-of-file, check-yaml/toml/json, check-added-large-files, check-merge-conflict, detect-private-key.
  - Python: ruff (lint+format, `files: ^backend/`), mypy --strict, bandit.
  - TypeScript/Frontend: prettier (mit `prettier-plugin-svelte`), eslint, svelte-check, tsc --noEmit – die letzten drei als lokale Hooks via pnpm-Workspace-Scripts (weil sie installierte Frontend-Dependencies brauchen).
- **TBD-Ersetzungen** alle aus `project-context.md` Abschnitt 3+7 abgeleitet: Python 3.13, Node 24, pnpm 11, uv 0.11.0, ruff 0.15.0, mypy 1.20.2 (exakt), bandit 1.9.0, prettier 3.8.0, prettier-plugin-svelte 3.5.0, GitHub-Actions checkout/setup-python/setup-node @v6, astral-sh/setup-uv@v5.0.0, pnpm/action-setup@v4.0.0.
- **Nicht angelegt:** `.github/workflows/release.yml` – `project-context.md` Abschnitt 7+8 verschiebt das explizit auf eine spätere Phase (Phase 7: Roll-out-Vorbereitung).
- **Coverage-Modul-Schwellen:** Globaler 80 %-Wert ist im Workflow als `--cov-fail-under=80` gesetzt; modul-spezifische strengere Schwellen (Auth ≥ 95 %, Operations ≥ 90 %, Retention ≥ 95 %, Resilience ≥ 90 % aus `project-context.md` Abschnitt 7) werden in Phase 1 Schritt 1.3 in `pyproject.toml` `[tool.coverage.report]` mit per-Modul-Konfigurationen ergänzt.
- **Initial rote Runs erwartet** – kein Code/keine `pyproject.toml`/keine `package.json` im Repo. Phase 1 Schritte 1.1 + 1.2 stellen die Skelette her, dann werden Workflows grün. Branch-Protection auf `main` wird in Phase 1 Schritt 1.2 aktiviert; bis dahin direkter Push erlaubt (`project-context.md` Abschnitt 10).
- **Methoden-Hinweis:** Die `# TBD:`-Platzhalter aus den Templates wurden alle aufgelöst, aber zwei Action-Patches (`astral-sh/setup-uv`, `pnpm/action-setup`) sind als Annahme gepinnt (`v5.0.0`/`v4.0.0`) und beim ersten Lauf in Phase 1 Schritt 1.2 zu verifizieren. Falls die Tags nicht existieren: konservativ höchsten existierenden Patch der Major-Linie wählen, kein ADR nötig (Patch-Anpassung freigabefrei nach Regel-001).

### 2026-05-07 23:35 – [BEOBACHTUNG]

- **Modus-2-Schritt 9 abgeschlossen, `README.md` aus Vorlagen-Zustand auf vollständiges Statusbild gebracht.**
- **Plan vorab vorgelegt und bestätigt** mit fünf zu klärenden Punkten: Status-Badge-Schema (Konzeption statt Vorlage-Mapping alpha/beta/stable), Build-Badge zwischenzeitlich „no status", CHANGELOG.md weglassen (nicht existent), LICENSE-Datei in Phase 1 statt jetzt anlegen, Sprache Deutsch.
- **Inhalt der README:** 7 Badges in 2 Zeilen (Klasse G Maximum 10, sechs darunter wegen Konzeptionsphase); Einzeiler aus `vision.md` Abschnitt 1; „Über das Projekt"-Block aus `vision.md` 1+2+3+5; Status-Block synchronisiert mit `project-context.md`, `fahrplan.md`, `architecture.md` Abschnitt 9, `decisions.md` Teil A, `blockers.md`; Quick Start als „Heute lauffähig" mit Klon-Anleitung plus Phase-1-Hinweis (kein Aspirational-Inhalt); Architektur-Skizze als vereinfachte Mermaid plus 1-Satz-Modulliste; Verwendung explizit auf Phase 4 verschoben; Nächste Schritte mit drei konkreten Punkten (Modus-2-Restschritte, Phase 1, Phase 2); Mitwirken aus CLAUDE.md 11 + project-context.md 7+10; Doku-Tabelle ohne CHANGELOG.md; Lizenz mit Hinweis auf späteres LICENSE-File.
- **Entfernt:** Vorlage „Badge-Auswahl pro Klasse" (~58 Zeilen) und Initialisierungs-Hinweis am Dateiende (~10 Zeilen). Methodik-relevante HTML-Kommentare am Datei-Anfang plus im Status-Block-Bereich behalten – sie sind Pflege-Hinweise, keine Initialisierungs-Vorlage.
- **Beobachtung zur Vorlage:** Badge-Vorlage erwartet „alpha / beta / stable / maintenance / deprecated" als Status-Werte; `project-context.md` führt aber „Konzeption / Aufbau / aktive Entwicklung / Wartung / deprecated". Das ist eine Vorlagen-/Projekt-Diskrepanz, die ich zugunsten von `project-context.md` aufgelöst habe (CLAUDE.md Abschnitt 16 macht `project-context.md` zur Quelle für den Status-Block). Vermerk: falls die Vorlagen-CLAUDE.md projektübergreifend angepasst wird, sollten die beiden Status-Listen vereinheitlicht werden – aber das ist Methodik-Diskussion, nicht Schritt-9-Aufgabe.

### 2026-05-07 23:20 – [BEOBACHTUNG]

- **Modus-2-Schritt 8 abgeschlossen, `logbuch.md` Vorlagen-Cleanup durchgeführt.**
- **Entfernt:** sechs Beispiel-Einträge mit `YYYY-MM-DD HH:MM`-Platzhaltern (PROBLEM-GELÖST, PROBLEM-OFFEN→BLOCKER, SESSIONSTART, BEOBACHTUNG, REIFEGRAD-WECHSEL, ADR-ANGELEGT) sowie der Initialisierungshinweis am Dateiende.
- **Beibehalten:** chronologische Einträge ab 2026-05-07 14:00 (Klärungs-Session) bis aktuell, Eintragstypen-Übersicht mit Pflicht-/Empfehlungs-Markierung, Hinweise zur Pflege (neueste oben, Zeitstempel-Format, Detailtiefe lieber zu hoch, Verweise statt Duplikation, keine Secrets), Archivierungs-Block (>800 Zeilen).
- **Folgenüberlegung:** Logbuch hat aktuell ca. 200 Zeilen, weit unter der 800-Zeilen-Auslagerungsschwelle. Nächste Auslagerungs-Prüfung erst beim Wachstum oder nach mehreren Wochen aktiver Sessions.

### 2026-05-07 23:05 – [BEOBACHTUNG]

- **Modus-2-Schritt 7 abgeschlossen, `blockers.md` auf Startzustand gebracht.**
- **Aktive Blocker:** keine. Begründung im Dokument festgehalten: alle Schublade-1-Grundsatzfragen geklärt (Logbuch 14:25 bis 16:20), alle Schublade-2-Spikes G–M in Phasen 3 + 5 platziert, alle Schublade-3-Roadmap-Meilensteine N/O/P in Phase 7 platziert. Härtungs-Schritt (Modus-2-Schritt 3) hatte keine Blocker hinterlassen.
- **Beibehalten:** Blocker-Erkennungs-Heuristiken (5 Muster für Sofort-Eskalation ohne Dreifach-Versuch) plus Eintrags-Format-Vorlagen für aktive und gelöste Blocker. Initialisierungs-Hinweis am Dateiende entfernt.
- **Nummerierungs-Regel** explizit dokumentiert: durchgehend, keine Lücken, gelöste Blocker behalten ihre Nummer. Erster Eintrag wäre `#001`.

### 2026-05-07 22:50 – [BEOBACHTUNG]

- **Modus-2-Schritt 6 abgeschlossen, `fahrplan.md` mit 7 regulären Phasen + 1 späterer Erweiterungs-Phase X befüllt.**
- **Phasen-Struktur:**
  - **Phase 1** Repo-Bootstrap & Tech-Foundations (UMSETZUNG, voll detailliert mit 8 Schritten 1.1–1.8 im Schritt-Format).
  - **Phase 2** Auth + Tenants + Verbund-Tauglichkeit I1/I2 (UMSETZUNG, gröber, 7 Schritte).
  - **Phase 3** Spikes Wave 1 (ERKUNDUNG, Spikes I + J).
  - **Phase 4** Operations Core + Realtime + Einsatzkraft-PWA (UMSETZUNG, gröber, 6 Schritte).
  - **Phase 5** Spikes Wave 2 (ERKUNDUNG, Spikes G + H + K + L + M).
  - **Phase 6** Geo + Frontends + Resilience + Retention + Export (UMSETZUNG, gröber, 7 Schritte).
  - **Phase 7** Stabilisierung + Roll-out + Roadmap N/O/P (STABILISIERUNG, 8 Schritte).
  - **Phase X** Verbund-Modus später (ERKUNDUNG → UMSETZUNG, sehr grob, 6 Schritte).
- **Disziplin-Wahl:** Spikes wurden gebündelt in eigene ERKUNDUNG-Phasen 3 und 5 vor den jeweiligen UMSETZUNG-Phasen 4 und 6, statt sie innerhalb von UMSETZUNG-Phasen einzuschieben. Begründung: `CLAUDE.md` Abschnitt 6 Phasentyp-Disziplin verbietet Vermischung. Kosten: 7 Phasen sind das Maximum für Klasse G – Verbund-Modus läuft als Phase X außerhalb der Hauptliste, bis er aktiv wird.
- **Phase-1-Sonderregel** bewusst dokumentiert: Eingangs-Disziplin „alle berührten Bestandteile auf [BELASTBAR]" abgemildert, weil Bootstrap-Phase die initialen Skelette herstellt und nur strategische Modul-Schnitt-Fixierung (durch ADR-002, ADR-003, ADR-004) als Eingangsbedingung verlangt. Vermerkt direkt in der Phasen-Beschreibung, damit es bei späteren Sessions nicht als versehentliche Aufweichung gelesen wird.
- **Spike-Zuordnung im Detail** in der Phasen-Übersichts-Tabelle festgehalten, plus Roadmap-Meilensteine N/O/P explizit Phase 7 zugeordnet. Damit ist die Brücke zwischen Schubladen-Triage (Logbuch 2026-05-07 16:35) und konkretem Fahrplan vollständig.
- **Replanning-Historie** mit dem Initial-Eintrag 2026-05-07 versehen.
- **Iterations-Reflexion-Vorlage** für Phase 1 belassen; wird beim Phase-1-Abschluss befüllt.
- **Beobachtung zur Vorlage:** Phase-1-Schritt-Format mit 13 Pflichtfeldern pro Schritt × 8 Schritte ist sehr lang (~330 Zeilen für Phase 1). Lesbar, aber an der Grenze. Falls Phase 2+ vergleichbar voll dokumentiert würden, wäre Auslagerung in `fahrplan-<modul>.md`-Teil-Dokumente nötig. Spätere Phasen sind hier bewusst grob gehalten, Verfeinerung kurz vor Phasen-Beginn.

### 2026-05-07 22:10 – [ADR-ANGELEGT]

- **Block-Anlage Modus-2-Schritt 5:** ADR-001 bis ADR-009 in einem Zug in `decisions.md` befüllt.
  - **ADR-001** [STRATEGISCH] [METHODIK] – Projektgrößen-Klassifikation Klasse G. **Auslöser:** Stufe-2-Bestätigung am Ende des Architektur-Grobschnitts (`architecture.md` Abschnitt 10) deckt sich mit Stufe-1-Hypothese aus Modus-2-Schritt 1.
  - **ADR-002** [STRATEGISCH] [STACK] [DEPLOYMENT] – Stack-Wahl FastAPI + SvelteKit + PostgreSQL + Valkey + Procrastinate. **Auslöser:** Verifikations-Stempel `Verifiziert: 2026-05-07` für alle gelisteten Komponenten in `project-context.md` Abschnitt 3.
  - **ADR-003** [STRATEGISCH] [METHODIK] – Architektur-Pattern Modular Monolith Backend + 3 SvelteKit-Frontends + Tile-Proxy + Reverse-Proxy. **Auslöser:** Modul-Karte und Architektur-Pattern in `architecture.md` Abschnitt 1+2.
  - **ADR-004** [STRATEGISCH] [SECURITY] – Admin-Bootstrap-Flow als CLI-Befehl. **Auslöser:** Klärung Frage A am 2026-05-07 14:25.
  - **ADR-005** [STRATEGISCH] [SECURITY] – AccessCode-Schema 6 Zeichen Crockford-Base32. **Auslöser:** Klärung Frage B am 2026-05-07 14:45.
  - **ADR-006** [STRATEGISCH] [DATENMODELL] – Aggregations-Schema pro Operation, ohne Personen-Buckets. **Auslöser:** Klärung Frage C am 2026-05-07 15:05.
  - **ADR-007** [STRATEGISCH] [SCHNITTSTELLE] [DATENMODELL] – Datenexport asynchron via Procrastinate-Job-Tripel. **Auslöser:** Klärung Frage D am 2026-05-07 15:25.
  - **ADR-008** [STRATEGISCH] [MODUL] [DATENMODELL] – Multi-Disponent ohne Lead, vollständiges `operation_audit_log`. **Auslöser:** Klärung Frage E am 2026-05-07 15:50.
  - **ADR-009** [STRATEGISCH] [DATENMODELL] – Verbund-Reinterpretation V2 plus Phase-1-Invarianten I1–I5. **Auslöser:** Klärung Frage F am 2026-05-07 16:20.
- **Reaktiv-Quote initialisiert:** 0/9 = 0 % `[REAKTIV]`-Anteil. Schwellenwert Klasse G: 20 %. Keine Reflexion nötig.
- **Aus den ADRs abgeleitete 14 Regeln** in Teil C eingetragen (Versionsdisziplin, Stack-Ausschlüsse, Modulgrenzen-Pflicht, Frontend↔Externer-Service-Verbot, CLI-Bootstrap, AccessCode-Hashing/-Toggle-Verhalten, Aggregat-Schreibung, Personen-Bucket-Verbot, Async-Mandanten-Operationen, Audit-Log-Pflicht/Confirmation-Dialog, Tenant-Participation als alleinige Verknüpfung, Teilnahme-Filter-Formulierung).

### 2026-05-07 21:39 – [SESSIONSTART]

- **Letzter Stand:** Modus-2-Schritt 4 abgeschlossen. PR #2 (`init(modus-2): Schritt 4 abgeschlossen, architecture.md befüllt`, Commit `d2c910f`) am 2026-05-07 in `main` gemerged (Merge-Commit `5a5f21e`). Architektur-Grobschnitt mit 14 Modulen, 10 Schnittstellen S1–S10, 5 Datenflüssen F1–F5, ER-Datenmodell, NFRs und Reifegrad-Übersicht steht. Stufe-2-Klassifikation Klasse G bestätigt.
- **Geplant für diese Session:** Modus-2-Schritt 5 – `decisions.md` von Vorlagen-Zustand auf vollständigen ADR-Satz befüllen. ADR-001 Klassifikation (G), ADR-002 Stack-Wahl, ADR-003 Architektur-Pattern, ADR-004 bis ADR-009 für die in Schublade 1 geklärten Fragen A–F. Teil A (Übersicht) und Teil C (Regeln) entsprechend pflegen. Reaktiv-Quote initialisieren.
- **Vorabprüfung:** Modus 2 weiterhin INITIALISIERUNG. Eingangskriterien für Schritt 5: Klärungs-Session Schublade 1 vollständig (erfüllt, Logbuch-Einträge 14:25 bis 16:20), Architektur-Grobschnitt vorhanden mit Verworfenen-Alternativen-Liste in `architecture.md` Abschnitt 8 (erfüllt), Verifikations-Stempel Stack 2026-05-07 (erfüllt, `project-context.md` Abschnitt 3). `decisions.md` ist Vorlagen-Zustand. Keine offenen STOPPs.
- **Methoden-Korrektur aus Sessionstart:** Bei der Pflichtlektüre habe ich zunächst nicht erkannt, dass Schritt 4 auf einem parallelen Worktree-Branch (`scp/trusting-tereshkova-b09abc-step-4`) bereits durchgeführt war. Nach `git fetch --all` plus User-Hinweis fand ich den Commit `d2c910f`. PR #2 wurde noch während meiner Klärung gemerged, mein Worktree-Branch via Fast-Forward auf `5a5f21e` gebracht. Lerneffekt: Pflichtlektüre nach CLAUDE.md Abschnitt 2 sollte um einen Branch-Awareness-Check ergänzt werden – Vorschlag wandert in eine spätere CLAUDE.md-Diskussion.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus.

### 2026-05-07 19:30 – [SESSIONENDE]

- **Session-Dauer:** ca. 2 h (17:30–19:30).
- **Bearbeitet:** Modus-2-Schritt 4 abgeschlossen – `architecture.md` von Vorlagen-Zustand auf vollständigen Architektur-Grobschnitt befüllt. Architektur-Plan vorab abgestimmt und bestätigt; Stufe-2-Klassifikations-Bestätigung am Dokumentende.
- **Erreicht:**
  - Abschnitt 0 Reifegrad-System um Code-Bezeichner-Konvention ergänzt (Domänen-Übersetzungstabelle Deutsch→Englisch); Klärungs-Session-Tabellennamen `einsatz_mandant_teilnahme`/`einsatz_audit_log` werden im Code als `operation_tenant_participation`/`operation_audit_log` umgesetzt.
  - Abschnitt 1 Überblick + Architektur-Pattern „Modular Monolith Backend + 3 SvelteKit-Frontends + nginx-Tile-Proxy + Caddy-Reverse-Proxy" formuliert.
  - Abschnitt 2 Modul-Karte als Mermaid-Top-Level (Frontends → Reverse-Proxy → Backend → Tile-Proxy → MapTiler/TomTom; PostgreSQL/Valkey/File-Volume).
  - Abschnitt 3 alle 14 Module detailliert (Reifegrad, Verantwortung, Nicht-Verantwortung, Schnittstellen-Verweis, interne Struktur, Abhängigkeiten, NFRs, offene Fragen).
  - Abschnitt 4 zehn Schnittstellenverträge S1–S10 (CLI-Bootstrap, Anonymous Session API, Operations Event Bus, Vehicle Assignment, Retention-Trigger, Tenant Data Export Tripel, Geo→Tile-Proxy, Auth-REST-API, WebSocket-Topologie, Tenant Participation Lookup).
  - Abschnitt 5 fünf Datenflüsse F1–F5 (Mandanten-Onboarding, Einsatzkraft-Bestellung Hard-Path, Disponenten-Aktion mit Audit-Log, Operation-Ende→Aggregat→Anonymisierung, asynchroner Datenexport).
  - Abschnitt 6 NFRs (Performance, Skalierung, Security, Observability, Datenschutz) mit Reifegrad-Verteilung.
  - Abschnitt 7 Datenmodell-Grobübersicht als Mermaid-ER mit zentralen Entitäten und Erläuterung der Phase-1-Invarianten I1/I4 + Lebensdauer-Felder.
  - Abschnitt 8 Verworfene Alternativen aus den Klärungen (Lead-Modell, synchroner Export, ENV-Bootstrap, Web-Setup-Wizard, Hybrid-Setup-Link, Verbund-Phase-1, Cross-Anzeige, Pseudonyme-Hashes, Karten-Snapshots, Single-Use-Codes, 4-stellige PIN); ADR-Nummern folgen in Schritt 5.
  - Abschnitt 9 Reifegrad-Übersicht: ~50 Bestandteile als Tabelle (1 BELASTBAR Kommunikations-Grundmodus + 1 BELASTBAR Procrastinate + diverse VORLÄUFIG-Module/Schnittstellen/NFRs + sieben OFFEN-Bereiche für die Spikes G–M plus NFR Bedrohungsmodell und Tracing).
  - Abschnitt 10 Stufe-2-Klassifikations-Bestätigung: Klasse G **bestätigt** (16 Komponenten, 5 zentrale externe Abhängigkeiten, 2 Sprachen, 2 Persistenzschichten, eine Compose-Einheit – nicht Klasse V, weil kein verteilter Lebenszyklus). Keine Anpassung der Hypothese aus Schritt 1 nötig.
  - `fahrplan.md` „Aktueller Stand"-Block aktualisiert auf Schritt 5.
- **Offen geblieben:** Modus-2-Schritte 5 (decisions.md mit ADRs A–F + ADR-001/002/003 + Vision-V2-Reinterpretation), 6 (fahrplan.md mit Phasen + Schubladen 2/3), 7 (blockers.md), 8 (logbuch Vorlagen-Cleanup), 9 (README.md), 10 (CI-/Hook-Skelett), 11 (vision Überführungsstatus), 12 (Init-Commit).
- **Nächster Schritt:** Modus-2-Schritt 5 – `decisions.md` befüllen. ADR-Reihenfolge:
  - ADR-001 [STRATEGISCH] [METHODIK]: Projektgrößen-Klassifikation Klasse G (Bestätigung Stufe 2).
  - ADR-002 [STRATEGISCH] [STACK]: Stack-Wahl (Backend + Frontend + Datenbanken + Infra, Verifikations-Stempel 2026-05-07).
  - ADR-003 [STRATEGISCH] [METHODIK]: Architektur-Pattern Modular Monolith + drei SvelteKit-Frontends.
  - ADR-004 [STRATEGISCH] [SECURITY]: Admin-Bootstrap-Flow (Frage A).
  - ADR-005 [STRATEGISCH] [SECURITY]: Zugangscode-Schema (Frage B).
  - ADR-006 [STRATEGISCH] [DATENMODELL]: Aggregations-Schema (Frage C).
  - ADR-007 [STRATEGISCH] [SCHNITTSTELLE]: Datenexport asynchron via Procrastinate (Frage D).
  - ADR-008 [STRATEGISCH] [MODUL]: Multi-Disponent ohne Lead (Frage E).
  - ADR-009 [STRATEGISCH] [DATENMODELL]: Verbund-Reinterpretation V2 + Phase-1-Invarianten I1–I5 (Frage F).
  - Teil A (Übersicht) und Teil C (Regeln) entsprechend pflegen.
- **Stimmung / Beobachtung:**
  - Vorab-Plan war wirkungsvoll – das Dokument ließ sich in einem Wurf sauber durchschreiben, ohne dass mitten im Schreiben Detail-Klärungen offen blieben. Die Klärungs-Session der vorigen Session hat sich hier ausgezahlt.
  - Code-Bezeichner-Konvention (Englisch im Code, Domänenbegriffe übersetzt) habe ich proaktiv eingeführt, weil `project-context.md` Codesprache Englisch verlangt, aber Klärungs-Session deutsche Tabellennamen produziert hatte. Inkonsistenz war im Hintergrund; jetzt sauber dokumentiert mit Übersetzungstabelle. Das ist keine Vision-Änderung, sondern Code-Konvention.
  - `[OFFEN]`-Bereiche sind klar von Spikes G–M referenziert – die Verbindung Architektur→Fahrplan-Spike ist jetzt ein-zu-eins. Das hilft beim Befüllen von Schritt 6.
  - Stufe-2-Klassifikations-Bestätigung hatte keine Überraschung; Klasse G war von Anfang an plausibel und wird jetzt durch den konkreten Architektur-Grobschnitt validiert.
  - Datei umfangreich (~700 Zeilen). Falls sie bei späterem Wachstum unübersichtlich wird, ist der Auslagerungspfad nach `architecture-<modul>.md` für besonders komplexe Module bereits in `CLAUDE.md` Abschnitt 1B Klasse G vorgesehen.

### 2026-05-07 19:25 – [REIFEGRAD-WECHSEL]

- **Bestandteile:** alle in `architecture.md` Abschnitt 9 gelisteten Bestandteile (Architektur-Pattern, Kommunikations-Modi, 14 Module, 10 Schnittstellen, 9 NFRs, 6 Datenmodell-Invarianten, 7 Spike-OFFEN-Bereiche, Datenmodell-Grobschnitt).
- **Wechsel:** Initial-Vergabe (Vorlagen-Zustand → konkreter Reifegrad). Verteilung:
  - `[BELASTBAR]`: 9 (Vision-/Stack-fixierte Bestandteile – REST/JSON, WebSocket-Grundmodus, HTTP-Tile-Proxy-Routing, Procrastinate, Datenschutz-Constraints, NFRs Tile-Cache-TTL, Routing-Disziplin, Backend-Multi-Architektur, PWA-Offline-Pflicht, Coverage-Mindestwerte).
  - `[VORLÄUFIG]`: ca. 35 (Module, Schnittstellen, Datenmodell-Invarianten, Skalierungs-/Performance-Annahmen, weitere NFRs).
  - `[OFFEN]`: 9 (Spike G/H/I/J/K/L/M plus NFR Bedrohungsmodell, NFR Tracing).
- **Auslöser:** Modus-2-Schritt 4, befüllt aus Klärungs-Ergebnissen Schublade 1 + Vision-Stack + Klassifikations-Bestätigung.
- **Datum in `architecture.md` Abschnitt 9 nachgetragen:** ja, 2026-05-07.

### 2026-05-07 17:30 – [SESSIONSTART]

- **Letzter Stand:** PR #1 erstellt (`init(modus-2): offene Grundsatzfragen vor Schritt 4 geklärt`, Commit `4853e0c`), Klärungs-Session abgeschlossen, Schublade 1 (Fragen A–F) durchgearbeitet, Schubladen 2/3 als Fahrplan-Skizzen für Schritt 6 abgelegt.
- **Geplant für diese Session:** Modus-2-Schritt 4 – `architecture.md` befüllen. Modul-Karte aus `project-context.md` Abschnitt 4 in Mermaid übertragen; Reifegrade hypothesengetreu setzen (`[VORLÄUFIG]` als Default, `[BELASTBAR]` nur bei harten Vision-Konstraints, `[OFFEN]` für Schublade-2-Punkte mit Verweis auf Spike); Schnittstellenverträge skizzieren für die durch Schublade 1 jetzt klar gewordenen Kontaktstellen; Stufe-2-Klassifikations-Bestätigung am Ende.
- **Vorabprüfung:** Modus 2 weiterhin INITIALISIERUNG. `architecture.md` ist Vorlagen-Zustand (kein Reifegrad vergeben). Eingangskriterien für Schritt 4: Schublade 1 vollständig geklärt (erfüllt), Stack fixiert (erfüllt, `project-context.md` Abschnitt 3 + Verifikation 2026-05-07), Modul-Liste in `project-context.md` Abschnitt 4 vorhanden (erfüllt). Keine offenen STOPPs.
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus.

### 2026-05-07 16:35 – [BEOBACHTUNG]

- **Schublade 2 + 3 für Modus-2-Schritt 6 vorbereitet, Klärungs-Session abgeschlossen.**
- **Schublade 2 (ERKUNDUNG-Spikes vor jeweiliger UMSETZUNG-Phase, in `fahrplan.md` aufzunehmen):**
  - **G — Sperrungs-Override-Technik:** ERKUNDUNG/Spike, 4–8 h, klärt TomTom-Custom-Areas vs. Route-Bias vs. Penalty-Map; Datenbedarf bei Override-Pflege; API-Budget-Folgen. Liegt vor erster UMSETZUNG-Phase mit `backend/geo`. Ergebnis: ADR mit Technikwahl.
  - **H — Resilience-Granularität:** ERKUNDUNG/Vergleichsstudie+Prototyp, 6–8 h, klärt Backup-Strategie (logical/physical, RTO/RPO), Recovery-Reihenfolge (Procrastinate-Job-State + Detail-Daten), Verhalten bei Crash mitten im Auftragsstatus-Wechsel, Erfahrung reconnect WebSocket nach State-Reload. Liegt vor UMSETZUNG `backend/resilience`. Ergebnis: ADR „Backup-Frequenz, Recovery-Reihenfolge, getestete RTO".
  - **I — Geografischer Plausibilitäts-Algorithmus:** ERKUNDUNG/Spike, 4 h, klärt Distanz-Metrik (Hülle vs. Mittelpunkt), GPS-Ungenauigkeit, Text-Standort-Behandlung, mandanten-konfigurierbarer Schwellenwert (Default 5 km). Liegt vor UMSETZUNG Einsatzkraft-Bestellpfad in `backend/operations`. Ergebnis: Pseudocode + Test-Datensatz.
  - **J — Bündelungs-Trigger:** ERKUNDUNG/Vergleichsstudie, 4 h, klärt Auslöser (System-Heuristik vs. Disponenten-manuell vs. Versorgungs-Transporter-Crew), UI-Auswirkung, Aggregat-Wirkung auf `anzahl_buendelungen`. Liegt vor UMSETZUNG Großbestellungs-Modus. Ergebnis: ADR Auslöser-Wahl Phase 1 (Vermutung: manuell durch Disponent).
  - **K — Hilfe-Knopf-Semantik:** ERKUNDUNG/Spike, 2–3 h, klärt Pflichtfeld-Beschreibung, Disponenten-Eskalations-Sichtbarkeit, Quittungspfad zum Betreuer, kein PII-Speicher. Liegt vor UMSETZUNG `frontend-betreuer`-Hilfe-Knopf. Ergebnis: UX-Konzept + Datenmodell-Skizze.
  - **L — Kartenmaterial-Offline-Caching-Technik:** ERKUNDUNG/Prototyp, 6–8 h, klärt Workbox-Strategie für Tile-Cache, Pre-Cache des Einsatzraums beim Schichtbeginn, Tile-Lebensdauer (≥ 7 Tage konsistent mit nginx-Cache), Speicher-Quota mobiler Browser. Liegt vor UMSETZUNG `frontend-betreuer`-Karten-Anzeige produktiv. Ergebnis: Prototyp + Konfigurations-ADR.
  - **M — Fahrzeugbezeichnungs-Schema:** ERKUNDUNG/Vergleichsstudie + Stakeholder-Rückfrage DPolG, 2 h netto, klärt Naming-Konvention (z. B. „EB-Bremen-01" oder verbandseigene Funkrufnamen), Eindeutigkeit pro Mandant vs. global, Längen-Constraints. Liegt vor erstem Roll-out, kein Architektur-Blocker. Ergebnis: ADR „Fahrzeug-Naming".
- **Schublade 3 (organisatorische Roadmap-Meilensteine ohne Code):**
  - **N — Plattform-Betreiber-Governance:** Klärung vor Produktivbetrieb (Patrick persönlich vs. Trägerverein vs. Stiftung). Berührt Haftung, DSGVO-Verantwortlichkeit, Mandanten-Vertragsgestaltung. Verknüpft mit „Administrator-Architektur bei Multi-Tenancy" (Skalierungsfrage zentraler vs. mehrere Plattform-Admins).
  - **O — Test-Termin reale Großlage:** konkretes Datum von DPolG + Patrick zu setzen, Anker im 3–6-Monats-Fenster. STABILISIERUNG-Phase als Validierungs-Anker.
  - **P — Schriftliche Onboarding-Unterlagen:** DSGVO-Datenverarbeitungs-Vereinbarung, Nutzungsbedingungen, Haftungsklarheit. Pflicht-Voraussetzung für Mandanten-Freischaltung. Verknüpft mit N (Trägerstruktur beeinflusst Vertragsgestaltung).
- **Bestätigung Patrick:** Triage geht so in Modus-2-Schritt 6 ein.

### 2026-05-07 16:20 – [BEOBACHTUNG]

- **Grundsatzfrage F (Parallele Mandanten an derselben Großlage) geklärt:** Verbund-Modus mit gemeinsamem Auftragspool ist Ziel, aber nicht Phase 1. Vision-Verhältnis: V2 (Reinterpretation – Verbund als opt-in-Erweiterung mit beidseitigem Konsens, Default-Trennung bleibt). Phase: P2 (Phase 1 architektonisch verbund-tauglich vorbereiten, eigentliche Verbund-Funktionalität in späterer UMSETZUNG-Phase). Fünf Phase-1-Invarianten festgelegt (I1 Verknüpfungstabelle `einsatz_mandant_teilnahme`, I2 abstrakter Berechtigungs-Filter, I3 Fahrzeug-Zuweisung über Einsatz-Kontext, I4 Aggregat einstweilen mit einer `mandant_id`, I5 Datenexport einstweilen auf Eigentümer-Rolle reduziert). Keine eigenes `backend/verbund`-Modul in Phase 1. Spätere Verbund-Phase wird in Modus-2-Schritt 6 in `fahrplan.md` als Phase mit ERKUNDUNG-Vorlauf aufgenommen. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 15:50 – [BEOBACHTUNG]

- **Grundsatzfrage E (Multi-Disponent-Hierarchie) geklärt:** Kein Lead-Modell. Alle Disponenten am Einsatz voll gleichberechtigt, einschließlich destruktiver Aktionen. Vollständiges Audit-Log (Tabelle `einsatz_audit_log`) ersetzt Lead-Schutz durch retrospektive Nachvollziehbarkeit. UX-Bestätigungs-Dialog vor destruktiven Aktionen im `frontend-disponent`. Begründung Patricks: Plattform-Administrator nicht zuverlässig erreichbar; Disponenten haben den operativen Überblick und müssen handlungsfähig bleiben. Audit-Log liefert zugleich Datenbasis für Aggregations-Felder aus Frage C. Abweichung von der ursprünglichen Empfehlung (Lead-Modell mit Eröffner-Default) – Begründung gilt als geklärt aufgenommen. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 15:25 – [BEOBACHTUNG]

- **Grundsatzfrage D (Datenexport-Format und Granularität) geklärt:** asynchron via Procrastinate-Job, API-Tripel POST/GET/GET-Download, ZIP mit JSON pro Tabelle plus manifest.json, vollständige Mandanten-Daten ohne externe Anhänge, Self-Service Mandant + Plattform-Admin-Override, 7 Tage Aufbewahrung mit Cleanup-Job. Endpunkt-Skizze in `project-context.md` Abschnitt 6 entsprechend angepasst. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 15:05 – [BEOBACHTUNG]

- **Grundsatzfrage C (Aggregations-Schema) geklärt:** Aggregation pro Einsatz, finaler Snapshot beim Einsatz-Ende; Metriken-Set ohne Personen-Buckets (Bestellungen, Fahraufträge, Stornos, Bündelungen, Versorgungs-Transporter-Modi, Zugangscode-Status, Strecken-Freigaben, Hilfe-Meldungen, Gesamt-Distanz gerundet, Spitzenwerte aktiver Fahrzeuge/Disponenten); Stadt-Label statt Geometrie in Phase 1; Mandanten-Trennung beim Zugriff; Aggregat-Schreibung entkoppelt vom 30-Tage-Anonymisierungs-Job. Begründung in `project-context.md` Abschnitt 11. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 14:45 – [BEOBACHTUNG]

- **Grundsatzfrage B (Zugangscode für Einsatzkraft-PWA) geklärt:** 6 Zeichen Crockford-Base32, ein Code pro Einsatz wiederverwendbar, Toggle wirkt nur auf neue Sessions, Disponenten-UI mit Anzeige+Copy+QR (kombinierte URL), keine Rotation in Phase 1. Begründung in `project-context.md` Abschnitt 11. ADR-Anlage in Modus-2-Schritt 5.

### 2026-05-07 14:25 – [BEOBACHTUNG]

- **Grundsatzfrage A (Admin-Bootstrap-Flow) geklärt:** CLI-Befehl `python -m eb_digital admin create`, jederzeit nutzbar, Passwort interaktiv. Verworfen: ENV-Bootstrap (Klartext-Risiko), Web-Setup-Wizard (Race + früher UI-Code), Hybrid-Setup-Link (Logs als Sekundär-Faktor problematisch). Eintrag in `project-context.md` Abschnitt 11 als geklärt markiert. ADR-Anlage erfolgt im Block in Modus-2-Schritt 5.

### 2026-05-07 14:00 – [SESSIONSTART]

- **Letzter Stand:** Initialisierungs-Commit `3b92368 init(modus-2): Schritte 1-3 abgeschlossen, project-context.md gehärtet`. Modus 2 Schritte 1 (Klassifikations-Hypothese), 2 (project-context vorbefüllt), 2a (Versions-Verifikation 2026-05-07) und 3 (Härtungs-Schritt) abgeschlossen. Schritte 4–12 (architecture, decisions, fahrplan, blockers, logbuch, README, CI-Skelett, Vision-Status, Init-Commit) stehen noch aus.
- **Geplant für diese Session:** Klärung der offenen Grundsatzfragen aus `project-context.md` Abschnitt 11 vor Befüllung von `architecture.md` (Modus-2-Schritt 4). Triage in „jetzt klären / als Erkundungs-Schritt einplanen / organisatorisch offen lassen" und anschließend Punkt für Punkt durchgehen.
- **Vorabprüfung:** Wir sind weiterhin in Modus 2 (Initialisierung), Phasentyp INITIALISIERUNG. Architektur-Reifegrade noch nicht vergeben. Pflichtlektüre vollständig gelesen plus Vertiefung `vision.md` (Auslöser: Grundsatzfragen verweisen direkt auf Vision Abschnitt 9).
- **Modus / Werkzeug:** Claude Code, semi-autonomer Modus.

### 2026-05-07 16:55 – [SESSIONENDE]

- **Session-Dauer:** ca. 3 h (14:00–16:55).
- **Bearbeitet:** Klärungs-Session der offenen Grundsatzfragen aus `project-context.md` Abschnitt 11; Triage in drei Schubladen; Schublade 1 (Fragen A–F) vollständig durchgearbeitet; Schublade 2 (G–M) und Schublade 3 (N/O/P) als Fahrplan-Skizzen für Modus-2-Schritt 6 vorbereitet und bestätigt.
- **Erreicht:**
  - **Frage A (Admin-Bootstrap-Flow) → CLI-Befehl, jederzeit nutzbar.**
  - **Frage B (Zugangscode) → 6 Zeichen Crockford-Base32, ein Code pro Einsatz, QR-Unterstützung, keine Rotation in Phase 1.**
  - **Frage C (Aggregations-Schema) → pro Einsatz, festes Metriken-Set, Stadt-Label statt Geometrie, Mandanten-Trennung beim Zugriff, Aggregat-Schreibung entkoppelt vom Anonymisierungs-Job.**
  - **Frage D (Datenexport) → asynchron via Procrastinate, ZIP+JSON pro Tabelle plus manifest.json, Self-Service Mandant + Plattform-Admin, 7 Tage Aufbewahrung.** Endpunkt-Skizze in `project-context.md` Abschnitt 6 entsprechend angepasst (Job-Tripel POST/GET/GET-Download).
  - **Frage E (Multi-Disponent) → kein Lead-Modell, alle gleichberechtigt, vollständiges Audit-Log (`einsatz_audit_log`).**
  - **Frage F (Parallele Mandanten) → Verbund-Modus als Ziel, Phase 1 nur architektonisch verbund-tauglich; fünf Phase-1-Invarianten festgelegt (I1 Verknüpfungstabelle `einsatz_mandant_teilnahme`, I2 abstrakter Filter, I3 Fahrzeug-Zuweisung über Einsatz-Kontext, I4 Aggregat einstweilen mit einer `mandant_id`, I5 Datenexport einstweilen auf Eigentümer-Rolle).**
  - `project-context.md` Abschnitt 11 mit allen sechs „GEKLÄRT 2026-05-07"-Einträgen und Triage-Vermerk konsolidiert.
  - `fahrplan.md` „Aktueller Stand"-Block aktualisiert (Modus-2-INITIALISIERUNG mit nächstem Schritt 4).
- **Offen geblieben:** Modus-2-Schritte 4 (architecture.md), 5 (decisions.md mit ADRs A–F + ggf. ADR für Vision-V2-Reinterpretation aus Frage F), 6 (fahrplan.md mit Schublade 2 + 3), 7 (blockers.md), 8 (logbuch Vorlagen-Cleanup), 9 (README.md), 10 (CI-/Hook-Skelett), 11 (vision Überführungsstatus), 12 (Init-Commit). Schubladen 2 und 3 als Skizzen im Logbuch-Eintrag 16:35 abgelegt – beim Befüllen von `fahrplan.md` direkt verwertbar.
- **Nächster Schritt:** Modus-2-Schritt 4 – `architecture.md` befüllen. Eingangsfragen: Modul-Karte aus `project-context.md` Abschnitt 4 in Mermaid übertragen; Reifegrade hypothesengetreu setzen (`[VORLÄUFIG]` als Default, `[BELASTBAR]` nur bei harten Vision-Konstraints); Schnittstellenverträge für die durch Schublade 1 jetzt klar gewordenen Kontaktstellen skizzieren (`backend/auth` CLI, `backend/auth_anonymous` Code-Validierung, `backend/operations` Lead-freie Auftragslogik plus Audit-Log, `backend/retention` Aggregat-Schreibung beim Einsatz-Ende, `backend/export` Job-Tripel, `einsatz_mandant_teilnahme`-Invarianten). Stufe-2-Klassifikations-Bestätigung am Ende des Architektur-Grobschnitts.
- **Stimmung / Beobachtung:**
  - Triage in Schubladen vor der eigentlichen Klärung war wirkungsvoll – sie hat verhindert, dass sekundäre Fragen mit den Architektur-blockierenden vermischt wurden.
  - Frage F war die einzige mit echtem Vision-Konflikt-Risiko. Nachfragen zu V1/V2/V3 plus P1/P2/P3 hat eine fast unbemerkte Vision-Aufweichung verhindert. Lerneffekt: bei freigabepflichtigen Architekturen mit Vision-Berührung lieber zwei Klärungs-Sätze als einen langen Architekturbau-Folgeaufwand.
  - Frage E zeigte die Pflicht zu „nicht stillschweigend interpretieren": die Begründung Patricks zu 4.B passte nicht zur Option, die er gewählt hatte – Nachfrage hat eine ganz andere Variante (Var.3 = kein Lead) zutage gefördert.
  - README ist noch im Vorlagen-Zustand und deshalb in dieser Session nicht synchronisiert worden – das ist kein Drift-Bug, sondern Modus-2-Schritt 9 nimmt sie in Betrieb. Vermerk hier, damit die Sessionende-Disziplin (CLAUDE.md Abschnitt 12 + 16) bewusst dokumentiert nicht erfüllt wurde, weil das Dokument zum Zeitpunkt des Sessionendes noch nicht aktiv ist.

---

## Eintragstypen (Übersicht)

Verbindliche Typen, andere nur in Ausnahmefällen:

| Typ                         | Wann                                                 | Pflicht?                                                            |
| --------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------- |
| `[SESSIONSTART]`            | Zu Beginn jeder Session                              | Ja                                                                  |
| `[SESSIONENDE]`             | Vor Sessionabschluss                                 | Ja                                                                  |
| `[PROBLEM-GELÖST]`          | Nach Behebung eines Problems, das Reibung war        | Empfohlen, alle Mini-Probleme erfassen                              |
| `[PROBLEM-OFFEN → BLOCKER]` | Wenn ein Problem zum Blocker eskaliert               | Ja, mit Verweis auf `blockers.md`                                   |
| `[BLOCKER-AUFGELÖST]`       | Wenn ein Blocker gelöst wurde                        | Ja, mit Verweis auf den ursprünglichen Logbuch- und Blocker-Eintrag |
| `[REIFEGRAD-WECHSEL]`       | Bei jeder Reifegrad-Änderung in `architecture.md`    | Ja                                                                  |
| `[ADR-ANGELEGT]`            | Bei Anlage eines neuen ADR                           | Ja                                                                  |
| `[BEOBACHTUNG]`             | Wenn etwas auffällt, das später nützlich sein könnte | Optional, KI proaktiv                                               |

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
