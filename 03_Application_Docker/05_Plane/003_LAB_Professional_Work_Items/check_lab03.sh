#!/bin/bash
# check_lab03.sh — evidence gate ของ LAB 3: ตรวจจากฐานข้อมูลจริง + API ว่าทำครบทุกข้อ แล้วพิมพ์ PASS บรรทัดเดียว
# ใช้: bash check_lab03.sh   (ต้องมี pc จาก LAB 1 และ ~/.plane_token จากข้อ 8)
# ใบดี ("นักศึกษาสมัครบัญชี…") ถูกค้นด้วย "ชื่อ" ไม่ใช่เลข PLAB-N — เพราะเลขจะต่างกันตามว่าทำ LAB 2 มาก่อนหรือไม่ (issue_sequences ไม่ใช้เลขซ้ำ)
set -u
SQL() { pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -tA -c "$1" 2>/dev/null | tr -d '[:space:]'; }
PID=$(SQL "select id from projects where identifier='PLAB' and deleted_at is null")
P4=$(SQL "select id from issues where project_id='$PID' and parent_id is null and deleted_at is null and name like 'นักศึกษาสมัครบัญชี%' order by created_at desc limit 1")
P4KEY=$(SQL "select 'PLAB-'||sequence_id from issues where id='$P4'")
fail=()
[ -n "$P4" ] || fail+=("ไม่พบ work item ใบดี 'นักศึกษาสมัครบัญชีและเข้าสู่ระบบด้วยอีเมล' ใน PLAB")
labels=$(SQL "select count(*) from labels where project_id='$PID' and deleted_at is null and name in ('bug','feature','docs','tech-debt')")
[ "$labels" = "4" ] || fail+=("labels=$labels (ต้องการ 4)")
subs=$(SQL "select count(*) from issues where parent_id='$P4' and deleted_at is null")
[ "${subs:-0}" -ge 3 ] || fail+=("sub-work items ของ $P4KEY=$subs (ต้องการ ≥3)")
rel=$(SQL "select count(*) from issue_relations where relation_type='blocked_by' and related_issue_id='$P4' and deleted_at is null")
[ "${rel:-0}" -ge 1 ] || fail+=("relation blocked_by → $P4KEY =$rel (ต้องการ ≥1)")
links=$(SQL "select count(*) from issue_links where issue_id='$P4' and deleted_at is null")
[ "${links:-0}" -ge 1 ] || fail+=("links ของ $P4KEY=$links (ต้องการ ≥1)")
acts=$(SQL "select count(*) from issue_activities where issue_id='$P4' and deleted_at is null")
[ "${acts:-0}" -ge 3 ] || fail+=("issue_activities ของ $P4KEY=$acts (ต้องการ ≥3)")
roles=$(SQL "select string_agg(distinct role::text, ',' order by role::text) from workspace_members wm join workspaces w on w.id=wm.workspace_id where w.slug='devtools-lab' and wm.is_active and wm.deleted_at is null")
case ",$roles," in *,20,*) ;; *) fail+=("ไม่มี role 20 (Admin) ใน workspace_members");; esac
case ",$roles," in *,15,*) ;; *) fail+=("ไม่มี role 15 (Member) ใน workspace_members — dev1 ยังไม่ join");; esac
page=$(SQL "select count(*) from pages where name like 'Code of Ethics Reflection%' and deleted_at is null")
[ "${page:-0}" -ge 1 ] || fail+=("ไม่พบ Page 'Code of Ethics Reflection — LAB 3'")
if [ -f ~/.plane_token ]; then
  code=$(curl -s -o /dev/null -w '%{http_code}' -H "X-API-Key: $(cat ~/.plane_token)" http://localhost:8080/api/v1/users/me/)
  [ "$code" = "200" ] || fail+=("token ใน ~/.plane_token ใช้ไม่ได้ (HTTP $code)")
else
  fail+=("ไม่มีไฟล์ ~/.plane_token")
fi
if [ ${#fail[@]} -eq 0 ]; then
  echo "PASS: LAB 3 — labels 4 · good item $P4KEY · sub-work items $subs · relation blocked_by $rel · links $links · activities $acts · roles {$roles} · ethics page $page · token OK"
else
  printf 'FAIL: %s\n' "${fail[@]}"; exit 1
fi
