#!/bin/bash
# Set the browser origin for a local VS Code / SSH forward.
set -euo pipefail
PLANE_HTTP_PORT=8089
if [[ -z ${PLANE_BROWSER_URL:-} ]]; then
  read -r -p 'Paste Forwarded Address from VS Code: ' PLANE_BROWSER_URL </dev/tty
fi
PLANE_BROWSER_URL=${PLANE_BROWSER_URL%/}
[[ $PLANE_BROWSER_URL == http://* ]] || PLANE_BROWSER_URL="http://$PLANE_BROWSER_URL"
if [[ ! $PLANE_BROWSER_URL =~ ^http://(localhost|127\.0\.0\.1)(:([0-9]{1,5}))?$ ]]; then
  echo 'Use the HTTP localhost or 127.0.0.1 Forwarded Address, without a path.' >&2
  exit 2
fi
LOCAL_PORT=${BASH_REMATCH[3]:-80}
LOCAL_PORT=$((10#$LOCAL_PORT))
(( LOCAL_PORT >= 1 && LOCAL_PORT <= 65535 )) || { echo 'Invalid port' >&2; exit 2; }
PLANE_BROWSER_URL="http://127.0.0.1:$LOCAL_PORT"
test -f /opt/plane/plane.env
CURRENT_HTTP_PORT=$(sed -n 's/^LISTEN_HTTP_PORT=//p' /opt/plane/plane.env)
if [[ $CURRENT_HTTP_PORT != "$PLANE_HTTP_PORT" ]]; then
  python3 - "$PLANE_HTTP_PORT" <<'PYPORT'
import socket, sys
port = int(sys.argv[1])
with socket.socket() as listener:
    try:
        listener.bind(('0.0.0.0', port))
    except OSError:
        sys.exit(f'Port {port} is busy. Choose another LAB port; do not stop other services.')
PYPORT
fi
cp -p /opt/plane/plane.env /opt/plane/plane.env.before-forward
chmod 600 /opt/plane/plane.env.before-forward
prime-cli stop
sed -i -E \
  -e "s|^LISTEN_HTTP_PORT=.*|LISTEN_HTTP_PORT=$PLANE_HTTP_PORT|" \
  -e "s|^WEB_URL=.*|WEB_URL=$PLANE_BROWSER_URL|" \
  -e "s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=$PLANE_BROWSER_URL|" \
  /opt/plane/plane.env
prime-cli start
printf '\nOpen in your browser: %s\n' "$PLANE_BROWSER_URL"
