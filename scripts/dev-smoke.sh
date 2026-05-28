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
	# Tempfiles aufräumen, die im Frontend-Smoke-Block gesetzt werden. Dürfen
	# NICHT über einen eigenen `trap … EXIT` gehen — das würde diesen globalen
	# cleanup()-Trap überschreiben (bash hält nur einen EXIT-Trap pro Scope)
	# und den Compose-Stack-Down-Schritt verschlucken.
	rm -f "${FE_COOKIE_JAR:-}" 2>/dev/null || true
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

step "Catalog-Smoke (Schritt 4.1): PA Category+Base → Disponent Override+Own → Carer-Read effektiv"

# Smoke-Hygiene: vor den Login-intensiven Stages (Catalog + Frontend) den
# Valkey-Rate-Limit-Counter resetten. Tenants-Smoke hat den 5/15-min-IP-Login-
# Counter bereits 4× aktiviert (Smoke-Admin, PA-relogin, Disp, Disp-blocked);
# Catalog-Dispatcher-Login + Frontend-Login würden den Counter ohne Reset auf
# 6 treiben → 429. Phase-1-Smoke nutzt Valkey ausschließlich für Rate-Limit-
# Counter (Pub/Sub ist Phase 4); FLUSHDB ist daher unkritisch.
docker exec eb-digital-cache-1 valkey-cli FLUSHDB > /dev/null 2>&1 || true

# Eigener Tenant + eigener Dispatcher, weil Tenants-Smoke seinen Tenant am Ende
# deaktiviert. Plattform-Admin-Cookie wird aus Tenants-Smoke wiederverwendet
# (TENANTS_COOKIE_JAR; PA-Timeout 8 h).
CATALOG_TENANT_SLUG="cat-smoke-$(date +%s)"
CATALOG_TENANT_NAME="Catalog Smoke Verein $(date +%H%M%S)"
CATALOG_DISP_USER="catdisp_$(date +%s)"
CATALOG_DISP_PW="catdispatcher-password-12345"
CATALOG_DISP_JAR=$(mktemp)
# shellcheck disable=SC2064
trap "rm -f $CATALOG_DISP_JAR" EXIT

# Tenant anlegen + approve + Dispatcher invite + reset + login.
# TENANTS_COOKIE_JAR ist die PA-Session aus Tenants-Smoke (PA-Timeout 8 h).
cat_reg=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /tmp/dev-smoke-catalog-reg.json \
	-H 'Content-Type: application/json' \
	-d "{\"name\":\"$CATALOG_TENANT_NAME\",\"slug\":\"$CATALOG_TENANT_SLUG\"}" \
	https://localhost/api/auth/register-tenant)
[[ "$cat_reg" == "201" ]] || { fail "Catalog: register-tenant Status $cat_reg"; exit 1; }
CATALOG_TENANT_ID=$(jq -r .tenant_id /tmp/dev-smoke-catalog-reg.json)

cat_appr=$(curl --silent --insecure --max-time 10 \
	-X POST -b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /dev/null \
	"https://localhost/api/tenants/$CATALOG_TENANT_ID/approve")
[[ "$cat_appr" == "200" ]] || { fail "Catalog: tenant approve Status $cat_appr"; exit 1; }

cat_inv=$(curl --silent --insecure --max-time 10 \
	-b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-catalog-invite.json \
	-H 'Content-Type: application/json' \
	-d "{\"username\":\"$CATALOG_DISP_USER\"}" \
	"https://localhost/api/tenants/$CATALOG_TENANT_ID/dispatchers")
[[ "$cat_inv" == "201" ]] || { fail "Catalog: dispatcher invite Status $cat_inv"; exit 1; }
CATALOG_RESET=$(jq -r .reset_token /tmp/dev-smoke-catalog-invite.json)

cat_reset=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d "{\"token\":\"$CATALOG_RESET\",\"new_password\":\"$CATALOG_DISP_PW\"}" \
	https://localhost/api/auth/reset-password)
[[ "$cat_reset" == "204" ]] || { fail "Catalog: reset-password Status $cat_reset"; exit 1; }

cat_disp_login=$(curl --silent --insecure --max-time 10 \
	-c "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d "{\"username\":\"$CATALOG_DISP_USER\",\"password\":\"$CATALOG_DISP_PW\"}" \
	https://localhost/api/auth/login)
[[ "$cat_disp_login" == "200" ]] || { fail "Catalog: dispatcher login Status $cat_disp_login"; exit 1; }

ok "Catalog: Tenant + Dispatcher vorbereitet (tenant_id=$CATALOG_TENANT_ID, PA-Cookie aus Tenants-Smoke wiederverwendet)"

# 1. Plattform-Admin: Kategorie anlegen.
CATALOG_CAT_NAME="Smoke-Kategorie-$(date +%s)"
cat_cat=$(curl --silent --insecure --max-time 10 \
	-b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-catalog-category.json \
	-H 'Content-Type: application/json' \
	-d "{\"name\":\"$CATALOG_CAT_NAME\"}" \
	https://localhost/api/catalog/categories)
if [[ "$cat_cat" == "201" ]]; then
	CATALOG_CAT_ID=$(jq -r .id /tmp/dev-smoke-catalog-category.json)
	ok "POST /api/catalog/categories 201 — category_id=$CATALOG_CAT_ID"
else
	fail "POST /api/catalog/categories Status $cat_cat (body: $(cat /tmp/dev-smoke-catalog-category.json))"
	exit 1
fi

# 2. Plattform-Admin: Base-Item anlegen.
cat_base=$(curl --silent --insecure --max-time 10 \
	-b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-catalog-base.json \
	-H 'Content-Type: application/json' \
	-d "{\"name\":\"Wasser still\",\"unit\":\"liter\",\"default_unit_label\":\"Liter\",\"category_id\":\"$CATALOG_CAT_ID\"}" \
	https://localhost/api/catalog/base)
if [[ "$cat_base" == "201" ]]; then
	CATALOG_BASE_ID=$(jq -r .id /tmp/dev-smoke-catalog-base.json)
	ok "POST /api/catalog/base 201 — base_item_id=$CATALOG_BASE_ID"
else
	fail "POST /api/catalog/base Status $cat_base (body: $(cat /tmp/dev-smoke-catalog-base.json))"
	exit 1
fi

# 3. Dispatcher: Override des Base-Items für eigenen Tenant.
cat_ovr=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-catalog-override.json \
	-H 'Content-Type: application/json' \
	-d "{\"base_item_id\":\"$CATALOG_BASE_ID\",\"override_name\":\"Wasser regional\"}" \
	https://localhost/api/catalog/tenant/override)
if [[ "$cat_ovr" == "201" ]]; then
	ok "POST /api/catalog/tenant/override 201 — Disponent legt Override an"
else
	fail "POST /api/catalog/tenant/override Status $cat_ovr (body: $(cat /tmp/dev-smoke-catalog-override.json))"
	exit 1
fi

# 4. Dispatcher: eigenständiges Tenant-Item.
cat_own=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-catalog-own.json \
	-H 'Content-Type: application/json' \
	-d "{\"name\":\"Lokales Brot\",\"unit\":\"piece\",\"default_unit_label\":\"Stück\",\"category_id\":\"$CATALOG_CAT_ID\"}" \
	https://localhost/api/catalog/tenant/own)
if [[ "$cat_own" == "201" ]]; then
	ok "POST /api/catalog/tenant/own 201 — Disponent legt eigenständiges Item an"
else
	fail "POST /api/catalog/tenant/own Status $cat_own (body: $(cat /tmp/dev-smoke-catalog-own.json))"
	exit 1
fi

# 5. Dispatcher: GET /api/catalog/tenant liefert die beiden Extensions.
cat_list=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-catalog-tenant-list.json \
	https://localhost/api/catalog/tenant)
if [[ "$cat_list" == "200" ]]; then
	ext_count=$(jq 'length' /tmp/dev-smoke-catalog-tenant-list.json)
	if [[ "$ext_count" -ge 2 ]]; then
		ok "GET /api/catalog/tenant 200 — $ext_count Extensions (Override + Own)"
	else
		fail "GET /api/catalog/tenant lieferte nur $ext_count Extensions (erwartet ≥ 2)"
		exit 1
	fi
else
	fail "GET /api/catalog/tenant Status $cat_list"
	exit 1
fi

# 6. Dispatcher: GET /api/catalog liefert effektiven Resolver-Output mit
#    Override-Name und eigenständigem Item (Dispatcher konsumiert über den
#    Carer-Pfad — _require_carer_or_dispatcher erlaubt beide).
cat_resolve=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-catalog-resolved.json \
	https://localhost/api/catalog)
if [[ "$cat_resolve" == "200" ]]; then
	override_visible=$(jq '[.[] | select(.name == "Wasser regional")] | length' /tmp/dev-smoke-catalog-resolved.json)
	own_visible=$(jq '[.[] | select(.name == "Lokales Brot")] | length' /tmp/dev-smoke-catalog-resolved.json)
	if [[ "$override_visible" == "1" && "$own_visible" == "1" ]]; then
		ok "GET /api/catalog 200 — Override-Name aktiv (\"Wasser regional\"), eigenständiges Item sichtbar (\"Lokales Brot\")"
	else
		fail "GET /api/catalog: Override sichtbar=$override_visible (erwartet 1), Own sichtbar=$own_visible (erwartet 1)"
		exit 1
	fi
else
	fail "GET /api/catalog Status $cat_resolve"
	exit 1
fi

# 7. Berechtigungs-Check: GET /api/catalog ohne Auth → 401.
cat_unauth=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /dev/null \
	https://localhost/api/catalog)
if [[ "$cat_unauth" == "401" ]]; then
	ok "GET /api/catalog ohne Auth 401 — Carer/Dispatcher-Pflicht durchgesetzt"
else
	fail "GET /api/catalog ohne Auth Status $cat_unauth (erwartet 401)"
	exit 1
fi

# 8. Berechtigungs-Check: POST /api/catalog/categories als Dispatcher → 403.
cat_forbidden=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d "{\"name\":\"Forbidden Kat\"}" \
	https://localhost/api/catalog/categories)
if [[ "$cat_forbidden" == "403" ]]; then
	ok "POST /api/catalog/categories als Dispatcher 403 — Plattform-Admin-Pflicht durchgesetzt"
else
	fail "POST /api/catalog/categories als Dispatcher Status $cat_forbidden (erwartet 403)"
	exit 1
fi

step "Fleet-Smoke (Schritt 4.2): Vehicle CRUD + Mode + Loadout + History + HeadOffice"

# Wir bleiben im Catalog-Tenant-/Dispatcher-Kontext — derselbe Verein, dieselbe
# Login-Session. CATALOG_DISP_JAR (Disponent) + TENANTS_COOKIE_JAR (PA) gelten
# weiter; CATALOG_BASE_ID + CATALOG_TENANT_OVERRIDE_… stehen ebenfalls bereits.

# Tenant-Extension-ID für Loadout-Items aus dem Catalog-Tenant-Listing extrahieren
# (eigenständiges „Lokales Brot" — base_item_id IS NULL).
CATALOG_OWN_EXT_ID=$(jq -r '.[] | select(.name == "Lokales Brot") | .id' /tmp/dev-smoke-catalog-tenant-list.json)
if [[ -z "$CATALOG_OWN_EXT_ID" || "$CATALOG_OWN_EXT_ID" == "null" ]]; then
	fail "Fleet: Tenant-Extension für 'Lokales Brot' konnte nicht ermittelt werden"
	exit 1
fi
ok "Fleet: nutze Catalog-Tenant ($CATALOG_TENANT_ID), Base $CATALOG_BASE_ID, Extension $CATALOG_OWN_EXT_ID"

# 1. Disponent legt reguläres Fahrzeug an.
fleet_v1=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-vehicle1.json \
	-H 'Content-Type: application/json' \
	-d '{"type":"regular","name":"ELW-Smoke-01","license_plate":"HB-EB 1"}' \
	https://localhost/api/fleet/vehicles)
if [[ "$fleet_v1" == "201" ]]; then
	FLEET_REGULAR_ID=$(jq -r .id /tmp/dev-smoke-fleet-vehicle1.json)
	ok "POST /api/fleet/vehicles regular 201 — vehicle_id=$FLEET_REGULAR_ID"
else
	fail "POST /api/fleet/vehicles regular Status $fleet_v1 (body: $(cat /tmp/dev-smoke-fleet-vehicle1.json))"
	exit 1
fi

# 2. Disponent legt Versorgungs-Transporter an (mode-Default 'off').
fleet_v2=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-vehicle2.json \
	-H 'Content-Type: application/json' \
	-d '{"type":"supply_transporter","name":"VT-Smoke-01","capacity_label":"3.5t"}' \
	https://localhost/api/fleet/vehicles)
if [[ "$fleet_v2" == "201" ]]; then
	FLEET_TRANSPORTER_ID=$(jq -r .id /tmp/dev-smoke-fleet-vehicle2.json)
	fleet_v2_mode=$(jq -r .mode /tmp/dev-smoke-fleet-vehicle2.json)
	[[ "$fleet_v2_mode" == "off" ]] || { fail "Fleet: Supply-Transporter Default-Mode '$fleet_v2_mode' (erwartet 'off')"; exit 1; }
	ok "POST /api/fleet/vehicles supply_transporter 201 — vehicle_id=$FLEET_TRANSPORTER_ID, mode='off' (Default)"
else
	fail "POST /api/fleet/vehicles supply_transporter Status $fleet_v2 (body: $(cat /tmp/dev-smoke-fleet-vehicle2.json))"
	exit 1
fi

# 3. Mode-Wechsel auf Versorgungs-Transporter.
fleet_mode=$(curl --silent --insecure --max-time 10 \
	-X POST -b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-mode.json \
	-H 'Content-Type: application/json' \
	-d '{"mode":"large_order"}' \
	"https://localhost/api/fleet/vehicles/$FLEET_TRANSPORTER_ID/mode")
if [[ "$fleet_mode" == "200" ]]; then
	fleet_mode_new=$(jq -r .mode /tmp/dev-smoke-fleet-mode.json)
	[[ "$fleet_mode_new" == "large_order" ]] || { fail "Fleet: Mode-Wechsel-Antwort '$fleet_mode_new' (erwartet 'large_order')"; exit 1; }
	ok "POST /api/fleet/vehicles/{id}/mode 200 — mode='large_order' aktiv"
else
	fail "POST /api/fleet/vehicles/{id}/mode Status $fleet_mode (body: $(cat /tmp/dev-smoke-fleet-mode.json))"
	exit 1
fi

# 4. Mode-Wechsel auf reguläres Fahrzeug → 422.
fleet_mode_bad=$(curl --silent --insecure --max-time 10 \
	-X POST -b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d '{"mode":"large_order"}' \
	"https://localhost/api/fleet/vehicles/$FLEET_REGULAR_ID/mode")
if [[ "$fleet_mode_bad" == "422" ]]; then
	ok "POST /api/fleet/vehicles/{regular_id}/mode 422 — Supply-Transporter-Pflicht durchgesetzt"
else
	fail "Fleet: Mode-Wechsel auf reguläres Fahrzeug Status $fleet_mode_bad (erwartet 422)"
	exit 1
fi

# 5. Loadout setzen mit Base + Tenant-Extension.
fleet_loadout=$(curl --silent --insecure --max-time 10 \
	-X PUT -b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-loadout.json \
	-H 'Content-Type: application/json' \
	-d "{\"items\":[{\"base_item_id\":\"$CATALOG_BASE_ID\",\"quantity\":24},{\"tenant_extension_id\":\"$CATALOG_OWN_EXT_ID\",\"quantity\":12}]}" \
	"https://localhost/api/fleet/vehicles/$FLEET_TRANSPORTER_ID/loadout")
if [[ "$fleet_loadout" == "200" ]]; then
	loadout_items=$(jq '.items | length' /tmp/dev-smoke-fleet-loadout.json)
	[[ "$loadout_items" == "2" ]] || { fail "Fleet: Loadout-Items=$loadout_items (erwartet 2)"; exit 1; }
	ok "PUT /api/fleet/vehicles/{id}/loadout 200 — 2 Items (Base + Tenant-Extension)"
else
	fail "PUT /api/fleet/vehicles/{id}/loadout Status $fleet_loadout (body: $(cat /tmp/dev-smoke-fleet-loadout.json))"
	exit 1
fi

# 6. Loadout neu setzen — vorheriger Stand muss in History landen.
fleet_loadout2=$(curl --silent --insecure --max-time 10 \
	-X PUT -b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-loadout2.json \
	-H 'Content-Type: application/json' \
	-d "{\"items\":[{\"base_item_id\":\"$CATALOG_BASE_ID\",\"quantity\":36}]}" \
	"https://localhost/api/fleet/vehicles/$FLEET_TRANSPORTER_ID/loadout")
[[ "$fleet_loadout2" == "200" ]] || { fail "Fleet: 2. Loadout-Set Status $fleet_loadout2"; exit 1; }
ok "PUT /api/fleet/vehicles/{id}/loadout (2. Set) 200 — vorheriger Snapshot in History"

# 7. History prüfen — muss 1 Eintrag haben (der erste Snapshot).
fleet_history=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-history.json \
	"https://localhost/api/fleet/vehicles/$FLEET_TRANSPORTER_ID/loadout/history")
if [[ "$fleet_history" == "200" ]]; then
	history_count=$(jq '.entries | length' /tmp/dev-smoke-fleet-history.json)
	[[ "$history_count" -ge 1 ]] || { fail "Fleet: History-Count=$history_count (erwartet ≥ 1)"; exit 1; }
	ok "GET /api/fleet/vehicles/{id}/loadout/history 200 — $history_count Eintrag/Einträge"
else
	fail "GET /api/fleet/vehicles/{id}/loadout/history Status $fleet_history"
	exit 1
fi

# 8. HeadOffice setzen + lesen.
fleet_ho_put=$(curl --silent --insecure --max-time 10 \
	-X PUT -b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-ho.json \
	-H 'Content-Type: application/json' \
	-d '{"lat":53.0793,"lng":8.8017,"label":"DPolG Bremen Lagezentrum"}' \
	https://localhost/api/fleet/head-office)
if [[ "$fleet_ho_put" == "200" ]]; then
	ok "PUT /api/fleet/head-office 200 — Geschäftsstelle gesetzt (lat=53.0793, lng=8.8017)"
else
	fail "PUT /api/fleet/head-office Status $fleet_ho_put (body: $(cat /tmp/dev-smoke-fleet-ho.json))"
	exit 1
fi

fleet_ho_get=$(curl --silent --insecure --max-time 10 \
	-b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-ho-get.json \
	https://localhost/api/fleet/head-office)
if [[ "$fleet_ho_get" == "200" ]]; then
	ho_label=$(jq -r .label /tmp/dev-smoke-fleet-ho-get.json)
	[[ "$ho_label" == "DPolG Bremen Lagezentrum" ]] || { fail "Fleet: HeadOffice-Label '$ho_label' (erwartet 'DPolG Bremen Lagezentrum')"; exit 1; }
	ok "GET /api/fleet/head-office 200 — Label-Round-Trip"
else
	fail "GET /api/fleet/head-office Status $fleet_ho_get"
	exit 1
fi

# 9. Berechtigungs-Verweigerungen: ohne Auth 401, HeadOffice mit lat=91 → 422.
fleet_unauth=$(curl --silent --insecure --max-time 10 \
	-w '%{http_code}' -o /dev/null \
	"https://localhost/api/fleet/vehicles?tenant_id=$CATALOG_TENANT_ID")
if [[ "$fleet_unauth" == "401" ]]; then
	ok "GET /api/fleet/vehicles ohne Auth 401 — Session-Pflicht durchgesetzt"
else
	fail "GET /api/fleet/vehicles ohne Auth Status $fleet_unauth (erwartet 401)"
	exit 1
fi

fleet_lat_oor=$(curl --silent --insecure --max-time 10 \
	-X PUT -b "$CATALOG_DISP_JAR" \
	-w '%{http_code}' -o /dev/null \
	-H 'Content-Type: application/json' \
	-d '{"lat":91.0,"lng":0.0}' \
	https://localhost/api/fleet/head-office)
if [[ "$fleet_lat_oor" == "422" ]]; then
	ok "PUT /api/fleet/head-office mit lat=91 422 — Pydantic-Range-Check greift"
else
	fail "PUT /api/fleet/head-office mit lat=91 Status $fleet_lat_oor (erwartet 422)"
	exit 1
fi

# 10. PA-Read mit ?tenant_id= über alle Vehicles des Catalog-Tenants.
fleet_pa_list=$(curl --silent --insecure --max-time 10 \
	-b "$TENANTS_COOKIE_JAR" \
	-w '%{http_code}' -o /tmp/dev-smoke-fleet-pa-list.json \
	"https://localhost/api/fleet/vehicles?tenant_id=$CATALOG_TENANT_ID")
if [[ "$fleet_pa_list" == "200" ]]; then
	pa_count=$(jq 'length' /tmp/dev-smoke-fleet-pa-list.json)
	[[ "$pa_count" -ge 2 ]] || { fail "Fleet: PA-Read-Count=$pa_count (erwartet ≥ 2)"; exit 1; }
	ok "GET /api/fleet/vehicles?tenant_id=… als PA 200 — $pa_count Vehicles sichtbar"
else
	fail "GET /api/fleet/vehicles?tenant_id=… als PA Status $fleet_pa_list"
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
# Kein eigener `trap … EXIT` hier — würde den globalen cleanup()-Trap (Zeile 68)
# überschreiben und den Compose-Stack-Down-Schritt verschlucken.
# FE_COOKIE_JAR wird in cleanup() aufgeräumt.

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
