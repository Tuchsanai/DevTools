#!/bin/bash
# Optional bounded web + API smoke check; browser/login verification is separate.
set -euo pipefail
: "${PLANE_URL:?Set PLANE_URL to the URL reachable from this terminal (remote or forwarded port)}"
LIMIT=${WAIT_TIMEOUT:-600}
[[ "$LIMIT" =~ ^[1-9][0-9]*$ ]] || { echo 'WAIT_TIMEOUT must be a positive integer' >&2; exit 2; }
T0=$SECONDS
while (( SECONDS-T0 < LIMIT )); do
  code=$(curl -sS -L -o /dev/null -w '%{http_code}' --max-time 5 "$PLANE_URL" 2>/dev/null || true)
  api_code=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 5 "${PLANE_URL%/}/api/instances/" 2>/dev/null || true)
  if [[ "$code" == 200 && "$api_code" == 200 ]]; then
    echo "READY: web and API HTTP 200 after $((SECONDS-T0))s; verify the Plane page in a browser next."; exit 0
  fi
  sleep 2
done
echo "TIMEOUT after ${LIMIT}s; inspect: sudo prime-cli monitor" >&2
exit 1
