#!/bin/bash
# LAB 1 smoke check — run inside the classroom machine after ./setup.sh → 2 Start.
# Checks files, the published proxy port, and that web + API answer 200. It does not
# verify the UI exercises (workspace / project / work items) — use the checklist for those.
set -uo pipefail
APP_DIR="${PLANE_APP_DIR:-$HOME/plane-selfhost/plane-app}"
PORT="${PLANE_HTTP_PORT:-8089}"
fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "$APP_DIR/docker-compose.yaml" && -f "$APP_DIR/plane.env" ]] || fail "missing $APP_DIR/docker-compose.yaml or plane.env (run ./setup.sh → 1 Install)"
grep -q "^LISTEN_HTTP_PORT=$PORT$" "$APP_DIR/plane.env" || fail "LISTEN_HTTP_PORT in plane.env is not $PORT"
grep -qE "^WEB_URL=http://localhost:[0-9]+$" "$APP_DIR/plane.env" || fail "WEB_URL must be http://localhost:<LOCAL_PORT>"
[[ "$(sed -n 's/^WEB_URL=//p' "$APP_DIR/plane.env")" == "$(sed -n 's/^CORS_ALLOWED_ORIGINS=//p' "$APP_DIR/plane.env")" ]] || fail "CORS_ALLOWED_ORIGINS must equal WEB_URL"
grep -q "change-this-key-on-deployment" "$APP_DIR/plane.env" && fail "SECRET_KEY / LIVE_SERVER_SECRET_KEY still default"
docker ps --format '{{.Names}} {{.Ports}}' | grep -q "plane-app-proxy-1 .*:$PORT->80/tcp" || fail "proxy is not publishing port $PORT (run ./setup.sh → 2 Start)"
running=$(docker ps --format '{{.Names}}' | grep -c '^plane-app-')
(( running >= 12 )) || fail "only $running plane-app containers running (expected 12 + exited migrator)"

LIMIT=${WAIT_TIMEOUT:-300}; T0=$SECONDS
while (( SECONDS - T0 < LIMIT )); do
  web=$(curl -sS -L -o /dev/null -w '%{http_code}' --max-time 5 "http://localhost:$PORT/" 2>/dev/null || true)
  api=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 "http://localhost:$PORT/api/instances/" 2>/dev/null || true)
  if [[ "$web" == 200 && "$api" == 200 ]]; then
    setup=$(curl -sS "http://localhost:$PORT/api/instances/" | python3 -c 'import sys,json; print(json.load(sys.stdin)["instance"]["is_setup_done"])' 2>/dev/null || echo "?")
    echo "PASS: $running containers up, proxy on $PORT, web+API HTTP 200 after $((SECONDS-T0))s, is_setup_done=$setup"
    exit 0
  fi
  sleep 3
done
fail "web/API not ready within ${LIMIT}s (web=$web api=$api); check ./setup.sh → 6 View Logs"
