#!/bin/bash
# plane_status.sh — LAB 1: live colour grid of the 13 compose services while Plane boots (Ctrl+C to stop).
# Data: `pc ps -a --format json` + HTTP code of /api/instances/ + the newest api log line. Refreshes every 2 s.
URL=${PLANE_URL:-http://localhost:8080}
T0=$(date +%s)
trap 'tput cnorm 2>/dev/null; echo; exit 0' INT TERM
tput civis 2>/dev/null
while true; do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 2 "$URL/api/instances/" 2>/dev/null || echo 000)
  ps_json=$(pc ps -a --format json 2>/dev/null)
  api_log=$(pc logs --tail 1 --no-log-prefix api 2>/dev/null | tail -1 | cut -c1-400)
  frame=$(PS_JSON="$ps_json" python3 - "$code" "$T0" "$api_log" "$URL" <<'PY'
import os, sys, json, time
code, t0, api_log, URL = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]
raw = os.environ.get("PS_JSON", "").strip()
rows = []
if raw:
    try:
        data = json.loads(raw)
        rows = data if isinstance(data, list) else [data]
    except json.JSONDecodeError:
        rows = [json.loads(l) for l in raw.splitlines() if l.strip()]
ORDER = ["plane-db", "plane-redis", "plane-mq", "plane-minio", "migrator", "api", "worker", "beat-worker",
         "web", "space", "admin", "live", "proxy"]
G, Y, R, B, D, N = "\033[42;30m", "\033[43;30m", "\033[41;97m", "\033[44;97m", "\033[100;97m", "\033[0m"
by = {r.get("Service"): r for r in rows}
# t+ = seconds since the oldest container of the project was created (= when you ran `pc up -d`)
from datetime import datetime
try:
    t0 = min(datetime.strptime(r["CreatedAt"][:25], "%Y-%m-%d %H:%M:%S %z").timestamp() for r in rows if r.get("CreatedAt"))
except Exception:
    pass
up = sum(1 for r in rows if r.get("State") == "running")
exited0 = sum(1 for r in rows if r.get("State") == "exited" and int(r.get("ExitCode", 1)) == 0)
out = []
out.append(f"\033[1m Plane v1.4.2 — compose project 'plane'   t+{max(0, time.time()-t0):4.0f}s since up   running {up:2d}/13   exited(0) {exited0}\033[0m")
out.append("")
cells = []
for svc in ORDER:
    r = by.get(svc)
    if not r:
        col, txt = D, "not created"
    else:
        st, health, ec = r.get("State"), r.get("Health", ""), int(r.get("ExitCode", 0))
        if st == "running":
            col = G if health in ("", "healthy") else Y
            txt = "Up" + (f" ({health})" if health else "")
        elif st == "exited":
            col, txt = (B, "Exited (0)") if ec == 0 else (R, f"Exited ({ec})")
        else:
            col, txt = Y, st
    cells.append(f"{col} {svc:<12}{txt:<15}{N}")
for i in range(0, len(cells), 3):
    out.append("  " + " ".join(cells[i:i+3]))
out.append("")
hc = G if code == "200" else (Y if code == "502" else R)
out.append(f"  {hc} GET {URL}/api/instances/  →  HTTP {code} {N}   "
           + ("READY" if code == "200" else "not ready (proxy answers, api still booting)" if code == "502" else "proxy not up"))
if api_log.startswith("{"):
    try:
        j = json.loads(api_log if api_log.endswith("}") else api_log + "}")
        api_log = j.get("message") or j.get("msg") or api_log
    except Exception:
        pass
out.append(f"  api log: {api_log[:90]}")
out.append("\n  green = running · yellow = starting/unhealthy · blue = one-shot job finished · red = crashed   (Ctrl+C to quit)")
print("\n".join(out))
PY
)
  clear; printf '%s\n' "$frame"
  sleep 2
done
