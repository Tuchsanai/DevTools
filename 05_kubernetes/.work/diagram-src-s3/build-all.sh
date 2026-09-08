#!/usr/bin/env bash
set -euo pipefail

ROOT=/root/workspace/DevTools/05_kubernetes
SRC=$ROOT/.work/diagram-src-s3
ASSETS=$ROOT/03_Session3_Application_Deployment/slides_assets
SCENES=$ASSETS/scenes

source "$ROOT/.work/tools/excalidraw-canvas.sh" 8895
mkdir -p "$ASSETS" "$SCENES" "$SRC/previews"

names=(
  d01-compose-to-objects
  d02-stateless-vs-stateful
  d03-ingress-vs-nodeport
  d04-rolling-update-timeline
  d05-requests-limits-scheduling
  d06-troubleshooting-ladder
  d07-request-path-browser-to-postgres
  d08-learning-loop
  lab015-architecture
  lab016-architecture
  lab017-architecture
  lab018-architecture
  lab019-architecture
  lab020-architecture
  lab021-architecture
)

for name in "${names[@]}"; do
  echo "BUILD $name"
  mcp-excalidraw-server clear --yes >/dev/null
  mcp-excalidraw-server add "$SRC/$name.json" >/dev/null

  node "$ROOT/.work/tools/excalidraw-tab.js" > "$SRC/previews/$name-tab.log" 2>&1 &
  tab_pid=$!
  sleep 4

  mcp-excalidraw-server screenshot --out "$SRC/previews/$name.png" >/dev/null
  mcp-excalidraw-server screenshot --format svg --out "$ASSETS/$name.svg" >/dev/null
  mcp-excalidraw-server export --out "$SCENES/$name.excalidraw" >/dev/null

  kill "$tab_pid" 2>/dev/null || true
done

echo "BUILT ${#names[@]} diagrams"
