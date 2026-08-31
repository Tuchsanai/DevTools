#!/bin/bash
# api_tour.sh — ทัวร์ REST API v1 ของ Plane 6 จุดใน 1 นาที (ใช้ curl + python3 เท่านั้น)
#   a) ไม่ส่ง key → 401          b) users/me + rate-limit headers
#   c) work item ด้วย human key   d) /projects/PLAB/ → 404 (path ต้องเป็น UUID)
#   e) แปลง identifier → UUID     f) เดิน cursor ด้วย ?per_page=5
set -u
BASE=${PLANE_BASE:-http://localhost:8080}/api/v1
WS=${PLANE_WS:-devtools-lab}
TOKEN=$(cat ~/.plane_token 2>/dev/null) || { echo "ไม่พบ ~/.plane_token (ทำ LAB 3 ข้อ 8 ก่อน)"; exit 1; }
H="X-API-Key: $TOKEN"
hr() { printf '\n\033[1;36m== %s\033[0m\n' "$*"; }
py() { python3 -c "$@"; }

hr "a) ไม่ส่ง X-API-Key → ต้องได้ 401"
curl -s -o /dev/null -w 'HTTP %{http_code}\n' "$BASE/users/me/"

hr "b) GET /users/me/ พร้อม header → ดู X-RateLimit-*"
curl -si -H "$H" "$BASE/users/me/" | grep -iE '^HTTP|^x-ratelimit'
curl -s -H "$H" "$BASE/users/me/" | py 'import sys,json; d=json.load(sys.stdin); print("user:", d["email"], "| id:", d["id"])'

hr "c) GET work item ด้วย human key PLAB-1 (path เดียวที่รับ identifier)"
curl -s -H "$H" "$BASE/workspaces/$WS/work-items/PLAB-1/" | py 'import sys,json; d=json.load(sys.stdin); print("PLAB-%s" % d["sequence_id"], "|", d["name"], "| priority:", d["priority"], "| state UUID:", d["state"])'

hr "d) ใช้ identifier แทน UUID ใน path โปรเจกต์ → 404"
curl -s -w '\nHTTP %{http_code}\n' -H "$H" "$BASE/workspaces/$WS/projects/PLAB/work-items/"

hr "e) แปลง identifier → UUID จาก list โปรเจกต์ (ทำครั้งเดียวแล้วจำไว้)"
PID=$(curl -s -H "$H" "$BASE/workspaces/$WS/projects/" | py 'import sys,json; print(next(p["id"] for p in json.load(sys.stdin)["results"] if p["identifier"]=="PLAB"))')
echo "PLAB → $PID"

hr "f) cursor pagination: ?per_page=5 แล้วเดินตาม next_cursor จนหมด"
CURSOR=""; PAGE=1
while :; do
  URL="$BASE/workspaces/$WS/projects/$PID/work-items/?per_page=5&order_by=sequence_id"
  [ -n "$CURSOR" ] && URL="$URL&cursor=$CURSOR"
  OUT=$(curl -s -H "$H" "$URL")
  echo "$OUT" | PAGE=$PAGE py 'import sys,json,os; d=json.load(sys.stdin); keys=",".join("PLAB-%d" % i["sequence_id"] for i in d["results"]); print("page %s: count=%s total_results=%s next_cursor=%s next_page_results=%s  -> %s" % (os.environ["PAGE"], d["count"], d["total_results"], d["next_cursor"], d["next_page_results"], keys))'
  MORE=$(echo "$OUT" | py 'import sys,json; d=json.load(sys.stdin); print("y" if d["next_page_results"] else "n")')
  [ "$MORE" = "y" ] || break
  CURSOR=$(echo "$OUT" | py 'import sys,json; print(json.load(sys.stdin)["next_cursor"])')
  PAGE=$((PAGE+1))
done
