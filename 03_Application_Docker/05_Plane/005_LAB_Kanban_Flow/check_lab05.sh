#!/bin/bash
# check_lab05.sh — ด่านหลักฐานของ LAB 5: ตรวจสิ่งที่ผู้เรียนต้องทำครบ แล้วพิมพ์ PASS บรรทัดเดียว
# ต้องรันในเครื่องเรียน (มี pc + ~/.plane_token + venv ~/venv-plane) จากโฟลเดอร์แล็บ
set -u
sql() { pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -tA -c "$1" 2>/dev/null | tr -d '[:space:]'; }
PID_SQL="(SELECT id FROM projects WHERE identifier='PLAB' AND deleted_at IS NULL)"
fail=0; ok() { echo "  ✓ $1"; }; bad() { echo "  ✗ $1"; fail=1; }

n=$(sql "SELECT count(*) FROM states WHERE project_id=$PID_SQL AND deleted_at IS NULL AND ((name='Ready' AND \"group\"='unstarted') OR (name='In Review' AND \"group\"='started'))")
[ "$n" = "2" ] && ok "states Ready(unstarted) + In Review(started)" || bad "states Ready/In Review ยังไม่ครบ (พบ $n)"

# นับรวมแถวที่ flow_time_machine.sql สำรองไว้ใน lab5_backup_activities ด้วย (ถ้าใบที่ลากถูก time machine เขียนทับ)
n=$(sql "SELECT count(*) FROM (SELECT id FROM issue_activities WHERE project_id=$PID_SQL AND field='state' AND new_value IN ('Ready','In Review') UNION SELECT id FROM lab5_backup_activities WHERE project_id=$PID_SQL AND field='state' AND new_value IN ('Ready','In Review')) x")
[ -n "$n" ] || n=$(sql "SELECT count(*) FROM issue_activities WHERE project_id=$PID_SQL AND field='state' AND new_value IN ('Ready','In Review')")
[ "${n:-0}" -ge 2 ] && ok "activity ย้ายการ์ดเข้า Ready/In Review ≥ 2 (พบ $n)" || bad "ยังไม่มี activity ลากการ์ดเข้า Ready/In Review"

n=$(sql "SELECT count(*) FROM issue_views WHERE project_id=$PID_SQL AND name='Expedite lane' AND deleted_at IS NULL")
[ "$n" = "1" ] && ok "view 'Expedite lane'" || bad "ไม่พบ view 'Expedite lane'"

n=$(sql "SELECT count(*) FROM pages p WHERE p.name ILIKE 'Kanban Policies%' AND p.deleted_at IS NULL")
[ "${n:-0}" -ge 1 ] && ok "page 'Kanban Policies'" || bad "ไม่พบ page 'Kanban Policies'"

st=$(sql "SELECT string_agg(DISTINCT status::text, ',' ORDER BY status::text) FROM intake_issues WHERE project_id=$PID_SQL AND deleted_at IS NULL")
miss=""; for want in -1 0 1; do case ",$st," in *",$want,"*) ;; *) miss="$miss $want";; esac; done
[ -z "$miss" ] && ok "intake_issues มีสถานะ Declined(-1) / Snoozed(0) / Accepted(1) (พบ $st)" || bad "intake_issues ยังไม่ครบ -1/0/1 (พบ '${st:-ว่าง}' ขาด$miss)"

n=$(sql "SELECT count(*) FROM issues WHERE project_id=$PID_SQL AND deleted_at IS NULL AND completed_at >= now() - interval '7 days'")
[ "${n:-0}" -ge 6 ] && ok "งานเสร็จใน 7 วัน ≥ 6 ใบ (พบ $n) — time machine ทำงานแล้ว" || bad "งานเสร็จใน 7 วันมีแค่ ${n:-0} ใบ — รัน flow_time_machine.sql หรือยัง?"

if [ -f flow_metrics.csv ]; then
  rows=$(($(wc -l < flow_metrics.csv) - 1)); [ "$rows" -ge 6 ] && ok "flow_metrics.csv มี $rows แถว" || bad "flow_metrics.csv มีแค่ $rows แถว"
else bad "ไม่พบ flow_metrics.csv (รัน python flow_metrics.py)"; fi

PY=~/venv-plane/bin/python; [ -x "$PY" ] || PY=python3
if "$PY" wip_guard.py --no-color >/tmp/wip_guard.out 2>&1; then ok "wip_guard.py exit 0 — ทุกคอลัมน์อยู่ในนโยบาย"; else bad "wip_guard.py exit $? — ยังมีคอลัมน์เกิน WIP (ดู /tmp/wip_guard.out)"; fi

if [ "$fail" = 0 ]; then echo "PASS: LAB 5 Kanban Flow — states · board activity · view · policy page · intake triage · flow metrics · WIP ok"; exit 0
else echo "FAIL: ยังมีข้อที่ไม่ผ่านด้านบน"; exit 1; fi
