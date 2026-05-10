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

step "Smoke-Test komplett grün"
exit 0
