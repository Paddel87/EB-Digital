#!/usr/bin/env bash
# EB Digital — dev-Profil-Smoke-Test (Phase 1 Schritt 1.8).
#
# Ablauf:
#   1. Prüft .env (kopiert aus .env.example, falls fehlend).
#   2. Baut Images falls nötig.
#   3. Startet `docker compose --profile dev` im Hintergrund.
#   4. Wartet bis alle Container `healthy` sind (Timeout 180 s).
#   5. Prüft: https://localhost/api/health → 200, JSON-Payload.
#      Prüft: https://localhost/health → 200, JSON-Payload.
#      Prüft: tile-proxy /tiles/12/3456/4321.pbf → 204 (intern via backend-exec).
#      Prüft: tile-proxy /health → 200 (intern via backend-exec).
#   6. Räumt am Ende `docker compose --profile dev down` ab,
#      es sei denn, --keep wird übergeben.
#
# Exit-Code 0 = alle Checks grün, !=0 = mindestens ein Check rot.

set -euo pipefail

usage() {
	cat <<USAGE
Usage: scripts/dev-smoke.sh [--keep]

Options:
  --keep   Stack nach erfolgreichem Smoke-Test laufen lassen
           (sonst: docker compose down).
  --help   Diese Hilfe anzeigen.
USAGE
}

KEEP_STACK=0
for arg in "$@"; do
	case "$arg" in
	--keep) KEEP_STACK=1 ;;
	--help | -h)
		usage
		exit 0
		;;
	*)
		echo "Unbekanntes Argument: $arg" >&2
		usage >&2
		exit 2
		;;
	esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

step() { printf '\n\033[1;36m▶ %s\033[0m\n' "$*"; }
ok() { printf '  \033[1;32m✓\033[0m %s\n' "$*"; }
fail() { printf '  \033[1;31m✗\033[0m %s\n' "$*" >&2; }

cleanup() {
	local exit_code=$?
	if [[ $KEEP_STACK -eq 0 || $exit_code -ne 0 ]]; then
		step "Compose-Stack herunterfahren"
		docker compose --profile dev --profile frontends down --remove-orphans >/dev/null 2>&1 || true
	else
		step "Compose-Stack bleibt mit --keep aktiv (manuell beenden mit \`docker compose --profile dev down\`)"
	fi
	if [[ $exit_code -ne 0 ]]; then
		fail "Smoke-Test fehlgeschlagen (Exit $exit_code)"
		echo "─── Letzte Compose-Logs ───" >&2
		docker compose --profile dev logs --tail 40 >&2 || true
	fi
}
trap cleanup EXIT

step ".env-Pflege prüfen"
if [[ ! -f .env ]]; then
	if [[ -f .env.example ]]; then
		cp .env.example .env
		ok ".env aus .env.example angelegt (Platzhalter müssen für echten Betrieb ersetzt werden)"
	else
		fail "Weder .env noch .env.example vorhanden"
		exit 1
	fi
else
	ok ".env vorhanden"
fi

step "Compose-Konfiguration validieren"
docker compose --profile dev config --quiet
ok "compose config syntaktisch valide"

step "Images bauen / aktualisieren"
docker compose --profile dev build --quiet
ok "Backend-Image gebaut"

step "Stack starten (--profile dev)"
docker compose --profile dev up -d
ok "compose up -d ausgelöst"

step "Auf healthy-Status aller Services warten (Timeout 180 s)"
SERVICES=("db" "cache" "backend" "worker" "tile-proxy" "reverse-proxy")
DEADLINE=$(($(date +%s) + 180))
while :; do
	all_healthy=1
	for svc in "${SERVICES[@]}"; do
		cid=$(docker compose --profile dev ps -q "$svc")
		if [[ -z "$cid" ]]; then
			all_healthy=0
			break
		fi
		status=$(docker inspect --format '{{.State.Health.Status}}' "$cid" 2>/dev/null || echo "missing")
		if [[ "$status" != "healthy" ]]; then
			all_healthy=0
			break
		fi
	done
	if [[ $all_healthy -eq 1 ]]; then
		ok "alle ${#SERVICES[@]} Services healthy"
		break
	fi
	if [[ $(date +%s) -gt $DEADLINE ]]; then
		fail "Timeout: nicht alle Services healthy"
		docker compose --profile dev ps >&2
		exit 1
	fi
	sleep 2
done

step "Reverse-Proxy: GET https://localhost/api/health"
api_health=$(curl --silent --insecure --max-time 10 https://localhost/api/health)
if echo "$api_health" | grep -q '"status":"ok"'; then
	ok "/api/health 200, Payload status=ok ($api_health)"
else
	fail "/api/health unerwartete Antwort: $api_health"
	exit 1
fi

step "Reverse-Proxy: GET https://localhost/health"
root_health=$(curl --silent --insecure --max-time 10 https://localhost/health)
if echo "$root_health" | grep -q '"status":"ok"'; then
	ok "/health 200, Payload status=ok ($root_health)"
else
	fail "/health unerwartete Antwort: $root_health"
	exit 1
fi

step "Tile-Proxy: GET tile-proxy/tiles/12/3456/4321.pbf via backend-exec"
tile_status=$(docker compose exec -T backend python -c "
import urllib.request, urllib.error
req = urllib.request.Request('http://tile-proxy/tiles/12/3456/4321.pbf')
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        print(resp.status)
except urllib.error.HTTPError as exc:
    print(exc.code)
")
if [[ "$tile_status" == "204" ]]; then
	ok "tile-proxy /tiles/.../12/3456/4321.pbf antwortet 204 (Phase-1-Stub)"
else
	fail "tile-proxy unerwarteter Status: $tile_status"
	exit 1
fi

step "Tile-Proxy: GET tile-proxy/health via backend-exec"
tile_health=$(docker compose exec -T backend python -c "
import urllib.request
with urllib.request.urlopen('http://tile-proxy/health', timeout=5) as resp:
    print(resp.read().decode())
")
if echo "$tile_health" | grep -q '"status":"ok"'; then
	ok "tile-proxy /health antwortet 200 mit JSON-Payload"
else
	fail "tile-proxy /health unerwartete Antwort: $tile_health"
	exit 1
fi

step "Auth-Smoke (Schritt 2.2): Admin anlegen → Login → /me → Logout"
SMOKE_USER="smoke_login_$(date +%s)"
SMOKE_PW="smoke-password-12345"
COOKIE_JAR=$(mktemp)
# shellcheck disable=SC2064 — cookie-jar variable is interpolated at trap-creation time.
trap "rm -f $COOKIE_JAR" RETURN

# Admin direkt über die Repository-Funktion anlegen — die Bootstrap-CLI
# nutzt getpass, das ohne TTY nicht aus stdin liest. Funktional äquivalent.
if docker compose exec -T \
	-e EB_SMOKE_USER="$SMOKE_USER" -e EB_SMOKE_PW="$SMOKE_PW" \
	backend python -c "
import asyncio, os
from eb_digital.auth.cli import create_platform_admin
from eb_digital.db import create_db_engine, create_session_factory
from eb_digital.settings import get_settings

async def main():
    s = get_settings()
    engine = create_db_engine(s.database_url)
    factory = create_session_factory(engine)
    try:
        async with factory() as session, session.begin():
            await create_platform_admin(
                session,
                username=os.environ['EB_SMOKE_USER'],
                password=os.environ['EB_SMOKE_PW'],
            )
    finally:
        await engine.dispose()

asyncio.run(main())
" >/dev/null 2>&1; then
	ok "Admin '$SMOKE_USER' angelegt"
else
	fail "Admin-Anlage fehlgeschlagen"
	exit 1
fi

# Login.
login_status=$(curl --silent --insecure --max-time 10 \
	-c "$COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-login.json \
	-H 'Content-Type: application/json' \
	-d "{\"username\":\"$SMOKE_USER\",\"password\":\"$SMOKE_PW\"}" \
	https://localhost/api/auth/login)
if [[ "$login_status" == "200" ]]; then
	ok "/api/auth/login 200 — Session-Cookie gesetzt ($(jq -r .kind /tmp/dev-smoke-login.json))"
else
	fail "/api/auth/login Status $login_status (body: $(cat /tmp/dev-smoke-login.json))"
	exit 1
fi

# /me mit Cookie.
me_status=$(curl --silent --insecure --max-time 10 \
	-b "$COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-me.json \
	https://localhost/api/auth/me)
if [[ "$me_status" == "200" ]]; then
	ok "/api/auth/me 200 — eingeloggt als $(jq -r .username /tmp/dev-smoke-me.json)"
else
	fail "/api/auth/me Status $me_status (body: $(cat /tmp/dev-smoke-me.json))"
	exit 1
fi

# Logout → 204.
logout_status=$(curl --silent --insecure --max-time 10 \
	-X POST -b "$COOKIE_JAR" -c "$COOKIE_JAR" \
	-w '%{http_code}' -o /dev/null \
	https://localhost/api/auth/logout)
if [[ "$logout_status" == "204" ]]; then
	ok "/api/auth/logout 204"
else
	fail "/api/auth/logout Status $logout_status"
	exit 1
fi

# /me nach Logout → 401.
me_after_logout=$(curl --silent --insecure --max-time 10 \
	-b "$COOKIE_JAR" \
	-w '%{http_code}' -o /dev/null \
	https://localhost/api/auth/me)
if [[ "$me_after_logout" == "401" ]]; then
	ok "/api/auth/me nach Logout 401 — Session abgelaufen"
else
	fail "/api/auth/me nach Logout Status $me_after_logout (erwartet 401)"
	exit 1
fi

step "Anon-Smoke (Schritt 2.3): Operation → /info → /session → 401/410-Pfade"
SMOKE_CODE="X7K3PQ"
ANON_COOKIE_JAR=$(mktemp)
# shellcheck disable=SC2064
trap "rm -f $ANON_COOKIE_JAR" RETURN

# Operation direkt via Python im Backend-Container anlegen (backend/operations-
# Use-Cases kommen erst in 4.x). Erzeugt eine aktive Operation mit
# AccessCode-Hash und gibt den signierten URL-Token auf stdout aus.
SMOKE_TOKEN=$(docker compose exec -T \
	-e EB_SMOKE_CODE="$SMOKE_CODE" \
	backend python -c "
import asyncio, os
from sqlalchemy import insert
from eb_digital.auth_anonymous.access_code import hash_access_code
from eb_digital.auth_anonymous.tokens import generate_url_token
from eb_digital.db import create_db_engine, create_session_factory
from eb_digital.operations.models import Operation, OPERATION_STATUS_ACTIVE
from eb_digital.settings import get_settings

async def main():
    s = get_settings()
    engine = create_db_engine(s.database_url)
    factory = create_session_factory(engine)
    try:
        async with factory() as session, session.begin():
            op = Operation(
                status=OPERATION_STATUS_ACTIVE,
                city_label='Bremen Innenstadt (Anon-Smoke)',
                url_token='placeholder',
                access_code_hash=hash_access_code(os.environ['EB_SMOKE_CODE']),
                access_code_active=True,
            )
            session.add(op)
            await session.flush()
            token = generate_url_token(op.id, s.secret_key.get_secret_value())
            op.url_token = token
            await session.flush()
            print(token)
    finally:
        await engine.dispose()

asyncio.run(main())
" 2>/dev/null | tr -d '\r\n')

if [[ -n "$SMOKE_TOKEN" ]]; then
	ok "Anon-Operation angelegt; Token-Länge: ${#SMOKE_TOKEN}"
else
	fail "Anon-Operation-Anlage fehlgeschlagen"
	exit 1
fi

# /info mit aktivem Code.
info_status=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /tmp/dev-smoke-anon-info.json \
	"https://localhost/api/anon/$SMOKE_TOKEN/info")
if [[ "$info_status" == "200" ]]; then
	ok "/api/anon/.../info 200 — access_code_active=$(jq -r .access_code_active /tmp/dev-smoke-anon-info.json)"
else
	fail "/api/anon/.../info Status $info_status (body: $(cat /tmp/dev-smoke-anon-info.json))"
	exit 1
fi

# /session mit falschem Code → 401.
wrong_status=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /tmp/dev-smoke-anon-wrong.json \
	-H 'Content-Type: application/json' \
	-d '{"access_code":"Z9X8Y7"}' \
	"https://localhost/api/anon/$SMOKE_TOKEN/session")
if [[ "$wrong_status" == "401" ]]; then
	ok "/api/anon/.../session mit falschem Code 401"
else
	fail "/api/anon/.../session mit falschem Code Status $wrong_status (body: $(cat /tmp/dev-smoke-anon-wrong.json))"
	exit 1
fi

# /session mit korrektem Code → 201 + Cookie.
session_status=$(curl --silent --insecure --max-time 10 \
	-c "$ANON_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-anon-session.json \
	-H 'Content-Type: application/json' \
	-d "{\"access_code\":\"$SMOKE_CODE\"}" \
	"https://localhost/api/anon/$SMOKE_TOKEN/session")
if [[ "$session_status" == "201" ]]; then
	ok "/api/anon/.../session mit Code 201 — session_id=$(jq -r .session_id /tmp/dev-smoke-anon-session.json)"
else
	fail "/api/anon/.../session mit Code Status $session_status (body: $(cat /tmp/dev-smoke-anon-session.json))"
	exit 1
fi

# /session gegen verfälschten Token → 410.
forged_status=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d '{}' \
	"https://localhost/api/anon/not-a-real-token/session")
if [[ "$forged_status" == "410" ]]; then
	ok "/api/anon/forged/session 410 — Token-Signatur abgelehnt"
else
	fail "/api/anon/forged/session Status $forged_status (erwartet 410)"
	exit 1
fi

step "Tenants-Smoke (Schritt 2.4): register-tenant → approve → invite → reset → login → deactivate"
TENANT_SLUG="smoke-tenant-$(date +%s)"
TENANT_NAME="Smoke Verein $(date +%H%M%S)"
NEW_DISP_USER="newdisp_$(date +%s)"
NEW_DISP_PW="dispatcher-password-12345"
TENANTS_COOKIE_JAR=$(mktemp)
DISP_COOKIE_JAR=$(mktemp)
# shellcheck disable=SC2064
trap "rm -f $TENANTS_COOKIE_JAR $DISP_COOKIE_JAR" RETURN

# 1. Self-Service-Antrag (public, kein Auth-Cookie).
register_status=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /tmp/dev-smoke-register-tenant.json \
	-H 'Content-Type: application/json' \
	-d "{\"name\":\"$TENANT_NAME\",\"slug\":\"$TENANT_SLUG\"}" \
	https://localhost/api/auth/register-tenant)
if [[ "$register_status" == "201" ]]; then
	TENANT_ID=$(jq -r .tenant_id /tmp/dev-smoke-register-tenant.json)
	ok "/api/auth/register-tenant 201 — tenant_id=$TENANT_ID, status=$(jq -r .status /tmp/dev-smoke-register-tenant.json)"
else
	fail "/api/auth/register-tenant Status $register_status (body: $(cat /tmp/dev-smoke-register-tenant.json))"
	exit 1
fi

# 2. Plattform-Admin neu einloggen (Smoke-Admin von oben wurde ausgeloggt).
admin_relogin=$(curl --silent --insecure --max-time 10 \
	-c "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-admin-relogin.json \
	-H 'Content-Type: application/json' \
	-d "{\"username\":\"$SMOKE_USER\",\"password\":\"$SMOKE_PW\"}" \
	https://localhost/api/auth/login)
if [[ "$admin_relogin" == "200" ]]; then
	ok "Plattform-Admin re-login (für Tenants-Aktionen) 200"
else
	fail "Plattform-Admin re-login Status $admin_relogin"
	exit 1
fi

# 3. GET /api/tenants als Plattform-Admin liefert mindestens unseren Antrag.
list_status=$(curl --silent --insecure --max-time 10 \
	-b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-tenants-list.json \
	"https://localhost/api/tenants?status=applied")
if [[ "$list_status" == "200" ]]; then
	count=$(jq 'length' /tmp/dev-smoke-tenants-list.json)
	ok "/api/tenants?status=applied 200 — $count applied-Tenants"
else
	fail "/api/tenants Status $list_status (body: $(cat /tmp/dev-smoke-tenants-list.json))"
	exit 1
fi

# 4. POST /api/tenants/{id}/approve.
approve_status=$(curl --silent --insecure --max-time 10 \
	-X POST -b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-tenant-approve.json \
	"https://localhost/api/tenants/$TENANT_ID/approve")
if [[ "$approve_status" == "200" ]]; then
	ok "/api/tenants/$TENANT_ID/approve 200 — status=$(jq -r .status /tmp/dev-smoke-tenant-approve.json)"
else
	fail "/api/tenants/.../approve Status $approve_status (body: $(cat /tmp/dev-smoke-tenant-approve.json))"
	exit 1
fi

# 5. POST /api/tenants/{id}/dispatchers liefert Reset-Token.
invite_status=$(curl --silent --insecure --max-time 10 \
	-b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-invite.json \
	-H 'Content-Type: application/json' \
	-d "{\"username\":\"$NEW_DISP_USER\"}" \
	"https://localhost/api/tenants/$TENANT_ID/dispatchers")
if [[ "$invite_status" == "201" ]]; then
	RESET_TOKEN=$(jq -r .reset_token /tmp/dev-smoke-invite.json)
	ok "/api/tenants/$TENANT_ID/dispatchers 201 — Reset-Token-Länge ${#RESET_TOKEN}, expires_in=$(jq -r .expires_in_seconds /tmp/dev-smoke-invite.json)s"
else
	fail "/api/tenants/.../dispatchers Status $invite_status (body: $(cat /tmp/dev-smoke-invite.json))"
	exit 1
fi

# 6. Reset-Password mit Token + neuem Passwort.
reset_status=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d "{\"token\":\"$RESET_TOKEN\",\"new_password\":\"$NEW_DISP_PW\"}" \
	https://localhost/api/auth/reset-password)
if [[ "$reset_status" == "204" ]]; then
	ok "/api/auth/reset-password 204 — Passwort gesetzt + User aktiviert"
else
	fail "/api/auth/reset-password Status $reset_status (erwartet 204)"
	exit 1
fi

# 7. Login als neuer Dispatcher → 200 mit tenant_id.
disp_login_status=$(curl --silent --insecure --max-time 10 \
	-c "$DISP_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-disp-login.json \
	-H 'Content-Type: application/json' \
	-d "{\"username\":\"$NEW_DISP_USER\",\"password\":\"$NEW_DISP_PW\"}" \
	https://localhost/api/auth/login)
if [[ "$disp_login_status" == "200" ]]; then
	disp_tenant=$(jq -r .tenant_id /tmp/dev-smoke-disp-login.json)
	if [[ "$disp_tenant" == "$TENANT_ID" ]]; then
		ok "Dispatcher-Login 200 — tenant_id matches ($disp_tenant)"
	else
		fail "Dispatcher-Login tenant_id mismatch: erwartet $TENANT_ID, gelesen $disp_tenant"
		exit 1
	fi
else
	fail "Dispatcher-Login Status $disp_login_status (body: $(cat /tmp/dev-smoke-disp-login.json))"
	exit 1
fi

# 8. Replay des Reset-Tokens → 410 (Replay-Schutz).
replay_status=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d "{\"token\":\"$RESET_TOKEN\",\"new_password\":\"another-password-1234\"}" \
	https://localhost/api/auth/reset-password)
if [[ "$replay_status" == "410" ]]; then
	ok "/api/auth/reset-password Replay 410 — User schon aktiv, Token verbraucht"
else
	fail "/api/auth/reset-password Replay Status $replay_status (erwartet 410)"
	exit 1
fi

# 9. POST /api/tenants/{id}/deactivate als Plattform-Admin.
deactivate_status=$(curl --silent --insecure --max-time 10 \
	-X POST -b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-deactivate.json \
	"https://localhost/api/tenants/$TENANT_ID/deactivate")
if [[ "$deactivate_status" == "200" ]]; then
	ok "/api/tenants/$TENANT_ID/deactivate 200 — status=$(jq -r .status /tmp/dev-smoke-deactivate.json)"
else
	fail "/api/tenants/.../deactivate Status $deactivate_status (body: $(cat /tmp/dev-smoke-deactivate.json))"
	exit 1
fi

# 10. Login als Dispatcher in deaktiviertem Tenant → 401.
disp_blocked_status=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d "{\"username\":\"$NEW_DISP_USER\",\"password\":\"$NEW_DISP_PW\"}" \
	https://localhost/api/auth/login)
if [[ "$disp_blocked_status" == "401" ]]; then
	ok "Dispatcher-Login in deaktiviertem Tenant 401 — Tenant-Status-Check greift"
else
	fail "Dispatcher-Login in deaktiviertem Tenant Status $disp_blocked_status (erwartet 401)"
	exit 1
fi

step "DB-Session-Lifecycle (Schritt 2.5b): Slug-Kollision → 409 → Folge-/health"

# ADR-015: Exception-Pfad-Probe für get_db_session(). Die Slug-Kollision auf
# /register-tenant löst eine HTTPException aus, *nachdem* die DB-Session
# vergeben wurde — also genau der Pfad, in dem der ehemalige
# `return session`-Bug eine geöffnete Connection im Pool hinterlassen hätte.
# Der Folge-Aufruf auf /api/health muss ohne Stall innerhalb 1 s antworten;
# bei einem Connection-Leak liefe der Pool unter wiederholten Aufrufen voll.
collision_status=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /tmp/dev-smoke-collision.json \
	-H 'Content-Type: application/json' \
	-d "{\"name\":\"$TENANT_NAME duplicate\",\"slug\":\"$TENANT_SLUG\"}" \
	https://localhost/api/auth/register-tenant)
if [[ "$collision_status" == "409" ]]; then
	ok "/api/auth/register-tenant Slug-Kollision 409 — DB-Exception nach Session-Vergabe geprüft"
else
	fail "/api/auth/register-tenant Slug-Kollision Status $collision_status (erwartet 409, body: $(cat /tmp/dev-smoke-collision.json))"
	exit 1
fi

# Folge-Request muss ohne Stall durchkommen — Connection wurde durch die
# yield-Dependency korrekt zurückgegeben (und Rollback ausgeführt).
followup_status=$(curl --silent --insecure --max-time 1 \
	-w '%{http_code}' -o /dev/null \
	https://localhost/api/health)
if [[ "$followup_status" == "200" ]]; then
	ok "/api/health nach Slug-Kollision 200 (innerhalb 1 s) — kein Connection-Stall"
else
	fail "/api/health nach Slug-Kollision Status $followup_status (erwartet 200 innerhalb 1 s — möglicher Connection-Leak)"
	exit 1
fi

step "Frontend-Disponent — statischer Build + Cookie-Round-Trip (Schritt 2.5)"

# 1. Statischer Build der frontend-disponent-App via pnpm. Build-Fehler fallen
#    hier auf (z. B. wenn adapter-static einen non-prerenderbaren Pfad findet).
if ! command -v pnpm >/dev/null 2>&1; then
	ok "pnpm nicht verfügbar — Frontend-Smoke übersprungen (akzeptiert: Backend-Smoke deckt die Pflicht-Pfade ab)"
else
	if pnpm --filter frontend-disponent build >/tmp/dev-smoke-frontend-build.log 2>&1; then
		ok "pnpm --filter frontend-disponent build erfolgreich"
	else
		fail "pnpm --filter frontend-disponent build (log: /tmp/dev-smoke-frontend-build.log)"
		exit 1
	fi
fi

# 2. Cookie-Round-Trip aus Frontend-Sicht: Login → /me → /tenants → Logout →
#    /me darf danach kein 200 mehr liefern. Wir nutzen Plattform-Admin aus
#    den vorhergehenden Smoke-Schritten.
FE_COOKIE_JAR=$(mktemp)
trap 'rm -f "$FE_COOKIE_JAR"' EXIT

fe_login_status=$(curl --silent --insecure --max-time 10 \
	-c "$FE_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fe-login.json \
	-H 'Content-Type: application/json' \
	-d "{\"username\":\"$SMOKE_USER\",\"password\":\"$SMOKE_PW\"}" \
	https://localhost/api/auth/login)
if [[ "$fe_login_status" == "200" ]]; then
	ok "Frontend-Smoke Login 200 — kind=$(jq -r .kind /tmp/dev-smoke-fe-login.json)"
else
	fail "Frontend-Smoke Login Status $fe_login_status (body: $(cat /tmp/dev-smoke-fe-login.json))"
	exit 1
fi

fe_me_status=$(curl --silent --insecure --max-time 10 \
	-b "$FE_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fe-me.json \
	https://localhost/api/auth/me)
if [[ "$fe_me_status" == "200" ]]; then
	ok "Frontend-Smoke /api/auth/me 200 — username=$(jq -r .username /tmp/dev-smoke-fe-me.json)"
else
	fail "Frontend-Smoke /api/auth/me Status $fe_me_status (body: $(cat /tmp/dev-smoke-fe-me.json))"
	exit 1
fi

fe_tenants_status=$(curl --silent --insecure --max-time 10 \
	-b "$FE_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fe-tenants.json \
	https://localhost/api/tenants)
if [[ "$fe_tenants_status" == "200" ]]; then
	ok "Frontend-Smoke /api/tenants 200 — count=$(jq 'length' /tmp/dev-smoke-fe-tenants.json)"
else
	fail "Frontend-Smoke /api/tenants Status $fe_tenants_status (body: $(cat /tmp/dev-smoke-fe-tenants.json))"
	exit 1
fi

fe_logout_status=$(curl --silent --insecure --max-time 10 \
	-X POST -b "$FE_COOKIE_JAR" -c "$FE_COOKIE_JAR" \
	-w '%{http_code}' -o /dev/null \
	https://localhost/api/auth/logout)
if [[ "$fe_logout_status" == "204" ]]; then
	ok "Frontend-Smoke Logout 204"
else
	fail "Frontend-Smoke Logout Status $fe_logout_status (erwartet 204)"
	exit 1
fi

fe_me_after_status=$(curl --silent --insecure --max-time 10 \
	-b "$FE_COOKIE_JAR" \
	-w '%{http_code}' -o /dev/null \
	https://localhost/api/auth/me)
if [[ "$fe_me_after_status" == "401" ]]; then
	ok "Frontend-Smoke /api/auth/me nach Logout 401 — Cookie ungültig"
else
	fail "Frontend-Smoke /api/auth/me nach Logout Status $fe_me_after_status (erwartet 401)"
	exit 1
fi

step "Frontend-Einsatzkraft — statischer Build (Schritt 2.6)"

# Backend-API-Smoke der S2a-Endpunkte ist im 2.3-Anon-Block bereits abgedeckt
# (Operation → /info → /session → 401/410-Pfade). Für 2.6 fügen wir nur den
# Build-Smoke hinzu — adapter-static mit fallback="index.html" + SPA-Mode
# (prerender=false, ssr=false) für die dynamische /[token]-Route. Build-
# Fehler hier (z. B. bei einer in 2.6 versehentlich wieder prerenderbaren
# Route) wären die einzige Klasse, die der vitest-Lauf nicht abdeckt.
if ! command -v pnpm >/dev/null 2>&1; then
	ok "pnpm nicht verfügbar — Einsatzkraft-Build-Smoke übersprungen (Backend-S2a-Smoke deckt die Pflicht-Pfade)"
else
	if pnpm --filter frontend-einsatzkraft build >/tmp/dev-smoke-einsatzkraft-build.log 2>&1; then
		ok "pnpm --filter frontend-einsatzkraft build erfolgreich"
	else
		fail "pnpm --filter frontend-einsatzkraft build (log: /tmp/dev-smoke-einsatzkraft-build.log)"
		exit 1
	fi
fi

step "Smoke-Test komplett grün"
exit 0
