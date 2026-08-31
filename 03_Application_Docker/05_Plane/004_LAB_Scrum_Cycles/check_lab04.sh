#!/bin/bash
# check_lab04.sh — evidence gate ของ LAB 4: ตรวจสภาพจริงใน Plane ผ่าน SQL + API แล้วพิมพ์ PASS บรรทัดเดียวเมื่อครบ
# ใช้:  bash check_lab04.sh     (ต้องมี pc, ~/.plane_token และ venv ที่ติดตั้ง requests)
set -u
fail=0
ok()   { echo "  ✔ $1"; }
bad()  { echo "  ✘ $1"; fail=1; }
sql()  { pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -tA -c "$1" 2>/dev/null | tr -d '[:space:]'; }

echo "== LAB 4 checks (project PLAB)"
est=$(sql "SELECT e.type || ':' || count(ep.id) FROM estimates e JOIN projects p ON p.estimate_id = e.id LEFT JOIN estimate_points ep ON ep.estimate_id = e.id WHERE p.identifier='PLAB' GROUP BY e.type;")
[ "$est" = "points:6" ] && ok "Estimates = points (6 ค่า Fibonacci)" || bad "Estimates ต้องเป็น points 6 ค่า (ได้ '$est')"

seeded=$(sql "SELECT count(*) FROM issues i JOIN projects p ON p.id=i.project_id WHERE p.identifier='PLAB' AND i.external_source='lab' AND i.deleted_at IS NULL;")
[ "${seeded:-0}" -ge 10 ] && ok "backlog seeded: $seeded ใบ (external_source=lab)" || bad "ต้องมี work item จาก seed_backlog.py ≥ 10 (ได้ '$seeded')"

noest=$(sql "SELECT count(*) FROM issues i JOIN projects p ON p.id=i.project_id WHERE p.identifier='PLAB' AND i.external_source='lab' AND i.deleted_at IS NULL AND i.estimate_point_id IS NULL;")
[ "${noest:-1}" = "0" ] && ok "ทุกใบที่ seed มี estimate point" || bad "มี $noest ใบที่ยังไม่มี estimate point"

s1=$(sql "SELECT (end_date < now())::int || ':' || (progress_snapshot IS NOT NULL AND progress_snapshot::text <> '{}')::int FROM cycles c JOIN projects p ON p.id=c.project_id WHERE p.identifier='PLAB' AND c.name='Sprint 1';")
[ "$s1" = "1:1" ] && ok "Sprint 1 Completed และมี progress_snapshot (ผ่านการ Transfer แล้ว)" || bad "Sprint 1 ต้อง Completed + มี snapshot (ได้ '$s1')"

s2=$(sql "SELECT count(ci.id) FROM cycles c JOIN projects p ON p.id=c.project_id LEFT JOIN cycle_issues ci ON ci.cycle_id=c.id AND ci.deleted_at IS NULL WHERE p.identifier='PLAB' AND c.name='Sprint 2';")
[ "${s2:-0}" -ge 1 ] && ok "Sprint 2 มีงานที่โอนมา $s2 ใบ" || bad "Sprint 2 ต้องมีงาน ≥ 1 ใบ (ได้ '$s2')"

spread=$(sql "SELECT count(DISTINCT completed_at::date) FROM issues i JOIN projects p ON p.id=i.project_id WHERE p.identifier='PLAB' AND i.completed_at IS NOT NULL AND i.deleted_at IS NULL;")
[ "${spread:-0}" -ge 3 ] && ok "งาน Done กระจายอยู่ $spread วัน (time machine ทำงาน)" || bad "completed_at ควรกระจาย ≥ 3 วัน (ได้ '$spread')"

page=$(sql "SELECT count(*) FROM pages pg JOIN project_pages pp ON pp.page_id=pg.id JOIN projects p ON p.id=pp.project_id WHERE p.identifier='PLAB' AND pg.name ILIKE '%retro%' AND pg.deleted_at IS NULL;")
[ "${page:-0}" -ge 1 ] && ok "มี Page Review & Retro" || bad "ต้องมี Page ที่ชื่อมีคำว่า Retro (ได้ '$page')"

action=$(sql "SELECT count(*) FROM issues i JOIN projects p ON p.id=i.project_id JOIN issue_labels il ON il.issue_id=i.id AND il.deleted_at IS NULL JOIN labels l ON l.id=il.label_id WHERE p.identifier='PLAB' AND l.name='tech-debt' AND i.external_source IS NULL AND i.deleted_at IS NULL;")
[ "${action:-0}" -ge 1 ] && ok "action item จาก retro เป็น work item (label tech-debt) แล้ว" || bad "ต้องมี work item ใหม่ label tech-debt ที่สร้างจาก retro (ได้ '$action')"

PY=~/venv-plane/bin/python; [ -x "$PY" ] || PY=python3          # ไม่พึ่ง `python` ของ shell (venv อาจยังไม่ activate)
if "$PY" velocity.py >/dev/null 2>&1; then ok "velocity.py รันผ่าน"; else bad "velocity.py รันไม่ผ่าน (token/venv?)"; fi

if [ "$fail" = 0 ]; then
  echo "PASS: LAB 4 — estimates=points · backlog $seeded ใบ · Sprint 1 completed+snapshot · Sprint 2 รับโอน $s2 ใบ · burndown $spread วัน · retro page + action item"
else
  echo "FAIL: ยังมีข้อที่ไม่ผ่าน — ดูเครื่องหมาย ✘ ด้านบน"; exit 1
fi
