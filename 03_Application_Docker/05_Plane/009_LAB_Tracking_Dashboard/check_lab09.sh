#!/bin/bash
# check_lab09.sh — ด่านหลักฐานของ LAB 9: pytest ผ่าน · dashboard ตอบ metric ครบ 6 ชุด · งบ API ไม่เกิน · webhook ไป dashboard.lab
set -u
cd "$(dirname "$0")"
fail=0; ok() { echo "  ✓ $1"; }; bad() { echo "  ✗ $1"; fail=1; }
PY=~/venv-plane/bin/python; [ -x "$PY" ] || PY=python3
if (cd dashboard && "$PY" -m pytest -q test_metrics.py >/tmp/lab09_pytest.out 2>&1); then ok "pytest: $(grep -oE '[0-9]+ passed' /tmp/lab09_pytest.out)"; else bad "pytest ไม่ผ่าน (ดู /tmp/lab09_pytest.out)"; fi
m=$(curl -s --max-time 10 http://localhost:8090/api/metrics 2>/dev/null)
for k in burndown velocity cfd lead_cycle wip blockers aging; do echo "$m" | grep -q "\"$k\"" && ok "/api/metrics มี $k" || bad "/api/metrics ไม่มี $k"; done
h=$(curl -s --max-time 5 http://localhost:8090/api/health 2>/dev/null)
rl=$(echo "$h" | python3 -c 'import sys,json; d=json.load(sys.stdin); print(d["requests_last_minute"], d["budget_per_minute"])' 2>/dev/null || echo "x x")
set -- $rl; [ "$1" != "x" ] && [ "$1" -le "$2" ] && ok "งบ API: $1/$2 request ต่อนาที" || bad "อ่าน /api/health ไม่ได้หรือเกินงบ"
sql() { pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -tA -c "$1" 2>/dev/null | tr -d '[:space:]'; }
n=$(sql "select count(*) from webhooks where url like '%dashboard.lab%' and is_active and deleted_at is null")
[ "${n:-0}" -ge 1 ] && ok "webhook ตัวที่ 2 ชี้ไป dashboard.lab" || echo "  · ยังไม่มี webhook ไป dashboard.lab (ทางเลือกในข้อ 5 — dashboard ยัง poll ทุก REFRESH วินาที)"
if [ "$fail" = 0 ]; then echo "PASS: LAB 9 — pytest · metrics 7 ชุด · budget ok"; else echo "FAIL: ยังมีข้อที่ไม่ผ่านด้านบน"; exit 1; fi
