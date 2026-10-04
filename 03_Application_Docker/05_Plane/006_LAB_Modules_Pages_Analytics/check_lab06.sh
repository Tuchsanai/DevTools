#!/bin/bash
# check_lab06.sh — evidence gate ของ LAB 6: ตรวจสภาพจริงใน Plane ผ่าน SQL แล้วพิมพ์ PASS บรรทัดเดียวเมื่อครบ
# ใช้:  bash check_lab06.sh     (ต้องมี pc จาก LAB 1)
set -u
fail=0
ok()   { echo "  ✔ $1"; }
bad()  { echo "  ✘ $1"; fail=1; }
sql()  { pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -tA -c "$1" 2>/dev/null | tr -d '[:space:]'; }
PJ="JOIN projects p ON p.id=x.project_id AND p.identifier='PLAB'"

echo "== LAB 6 checks (project PLAB)"
mods=$(sql "SELECT count(*) FROM modules x $PJ WHERE x.deleted_at IS NULL;")
[ "${mods:-0}" -ge 3 ] && ok "modules: $mods (Ordering / Payments / Notifications)" || bad "ต้องมี module ≥ 3 (ได้ '$mods')"

mi=$(sql "SELECT count(*) FROM module_issues x $PJ WHERE x.deleted_at IS NULL;")
[ "${mi:-0}" -ge 5 ] && ok "module_issues: $mi ใบถูกผูกเข้า module" || bad "ต้องมี work item ใน module ≥ 5 (ได้ '$mi')"

prd=$(sql "SELECT count(*) FROM pages pg JOIN project_pages pp ON pp.page_id=pg.id JOIN projects p ON p.id=pp.project_id WHERE p.identifier='PLAB' AND pg.name ILIKE 'PRD%' AND pg.is_locked AND pg.deleted_at IS NULL;")
[ "${prd:-0}" -ge 1 ] && ok "Page PRD มีอยู่และถูก Lock แล้ว" || bad "ต้องมี Page ชื่อขึ้นต้น PRD ที่ is_locked=true (ได้ '$prd')"

child=$(sql "SELECT count(*) FROM pages pg JOIN project_pages pp ON pp.page_id=pg.id JOIN projects p ON p.id=pp.project_id WHERE p.identifier='PLAB' AND pg.name ILIKE '%API design%' AND pg.deleted_at IS NULL;")
[ "${child:-0}" -ge 1 ] && ok "มี page ออกแบบ API ประกอบ PRD: $child หน้า" || bad "ต้องมี page 'Ordering — API design' ≥ 1 (ได้ '$child')"

exp=$(sql "SELECT string_agg(provider, ',' ORDER BY provider) FROM (SELECT DISTINCT provider FROM exporters WHERE status='completed' AND deleted_at IS NULL) s;")
[ "$exp" = "csv,json,xlsx" ] && ok "exporters: completed ครบ csv, json, xlsx" || bad "ต้อง export สำเร็จครบ 3 แบบ (ได้ '$exp')"

board=$(sql "SELECT count(*) FROM deploy_boards x $PJ WHERE x.entity_name='project' AND x.deleted_at IS NULL;")
[ "${board:-0}" -ge 1 ] && ok "deploy_boards: โปรเจกต์ถูก Publish เป็น Sites แล้ว" || bad "ต้อง Publish โปรเจกต์ (deploy_boards) (ได้ '$board')"

votes=$(sql "SELECT count(*) FROM issue_votes x $PJ WHERE x.deleted_at IS NULL;")
[ "${votes:-0}" -ge 1 ] && ok "issue_votes: มีการโหวตจากหน้า public $votes ครั้ง" || echo "  · ยังไม่มีโหวตจาก Sites (ทางเลือก — ต้อง sign in ใน Sites ก่อนโหวต)"

if [ "$fail" = 0 ]; then
  echo "PASS: LAB 6 — modules $mods · module_issues $mi · PRD locked + API-design page $child · exports csv,json,xlsx · Sites published · votes ${votes:-0}"
else
  echo "FAIL: ยังมีข้อที่ไม่ผ่าน — ดูเครื่องหมาย ✘ ด้านบน"; exit 1
fi
