#!/usr/bin/env bash
# Private Excalidraw canvas per job — does NOT touch the shared canvas on 8892.
#   source excalidraw-canvas.sh <port>            -> exports env vars for the mcp-excalidraw-server CLI
#   bash   excalidraw-canvas.sh <port> start|stop|status
PORT=${1:-8893}; CMD=${2:-}
T=/root/workspace/DevTools/05_kubernetes/.work/tools
export EXPRESS_SERVER_URL=http://127.0.0.1:$PORT
export XDG_STATE_HOME=$T/excali-state-$PORT
export EXCALIDRAW_EXPORT_DIR=$T/excali-state-$PORT/diagrams
export LOG_FILE_PATH=$T/excali-state-$PORT/excalidraw-mcp.log
export EXCALIDRAW_NO_AUTOSTART=1
mkdir -p "$XDG_STATE_HOME" "$EXCALIDRAW_EXPORT_DIR"
case "$CMD" in
  start)
    mcp-excalidraw-server start >/dev/null 2>&1; sleep 3
    nohup node "$T/excalidraw-tab.js" > "$XDG_STATE_HOME/tab.log" 2>&1 &
    echo $! > "$XDG_STATE_HOME/tab.pid"; sleep 6
    mcp-excalidraw-server status ;;
  stop)
    kill "$(cat "$XDG_STATE_HOME/tab.pid" 2>/dev/null)" 2>/dev/null
    mcp-excalidraw-server stop ;;
  status) mcp-excalidraw-server status ;;
  *) : ;;
esac
