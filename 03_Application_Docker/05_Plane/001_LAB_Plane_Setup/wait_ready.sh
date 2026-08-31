#!/bin/bash
# wait_ready.sh — LAB 1: block until Plane is really ready (not just "Up").
# Phase 1: migrator must finish with exit code 0 (api/worker wait for it).
# Phase 2: GET /api/instances/ must answer 200 (proxy → api → db all alive).
URL=${PLANE_URL:-http://localhost:8080}
T0=$(date +%s)
elapsed() { echo $(( $(date +%s) - T0 )); }
last=""
while true; do
  st=$(pc ps -a --format '{{.Service}} {{.State}} {{.ExitCode}}' 2>/dev/null | awk '$1=="migrator"{print $2" "$3}')
  case "$st" in
    "exited 0") echo "migrator: Exited (0) after $(elapsed)s — migrations applied"; break ;;
    exited*)    echo "migrator: $st — migrations FAILED, run: pc logs migrator"; exit 1 ;;
    "")         msg="migrator: not created yet (did you run: pc up -d ?)" ;;
    *)          msg="migrator: ${st%% *} (migrations in progress) … $(( $(elapsed) / 10 * 10 ))s" ;;
  esac
  [ "$msg" != "$last" ] && echo "$msg"; last=$msg
  sleep 2
done
while true; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 "$URL/api/instances/" || true)
  if [ "$code" = "200" ]; then echo "READY after $(elapsed)s  ($URL/api/instances/ = 200)"; exit 0; fi
  msg="api: $URL/api/instances/ = ${code:-000} (api still booting) … $(( $(elapsed) / 10 * 10 ))s"
  [ "$msg" != "$last" ] && echo "$msg"; last=$msg
  sleep 2
done
