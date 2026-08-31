#!/bin/bash
# check_lab07.sh — evidence gate ของ LAB 7: ตรวจจาก DB โดยตรง (ไม่กิน rate limit) แล้วพิมพ์ PASS บรรทัดเดียว
set -u
PSQL="pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -At"
q() { $PSQL -c "$1" 2>/dev/null | tr -d '\r'; }
fail() { echo "FAIL: $*"; exit 1; }

[ -s ~/.plane_token ] || fail "ไม่มี ~/.plane_token"
COUNTS=$(q "select external_source||'='||count(*) from issues where external_source in ('trello','jira') and deleted_at is null group by external_source order by external_source" | paste -sd, -)
[ "$COUNTS" = "jira=13,trello=20" ] || fail "จำนวน work items: $COUNTS (ต้องเป็น jira=13,trello=20)"
SUB=$(q "select count(*) from issues where external_source='trello' and parent_id is not null and deleted_at is null")
[ "$SUB" = "8" ] || fail "sub-work items จาก checklist = $SUB (ต้องเป็น 8)"
STATES=$(q "select string_agg(s.name, ',' order by s.name) from states s join projects p on p.id=s.project_id where p.identifier='TRL' and p.deleted_at is null and s.\"group\"<>'triage' and s.deleted_at is null")
[ "$STATES" = "Doing,Done,Review,To Do" ] || fail "states ของ TRL = $STATES"
MOD=$(q "select count(*) from modules m join projects p on p.id=m.project_id where p.identifier='JRA' and p.deleted_at is null and m.deleted_at is null")
CYC=$(q "select count(*) from cycles c join projects p on p.id=c.project_id where p.identifier='JRA' and p.deleted_at is null and c.deleted_at is null")
[ "$MOD" = "2" ] && [ "$CYC" = "2" ] || fail "JRA modules=$MOD cycles=$CYC (ต้องเป็น 2/2)"
EST=$(q "select count(*) from issues i join projects p on p.id=i.project_id where p.identifier='JRA' and p.deleted_at is null and i.estimate_point_id is not null and i.deleted_at is null")
[ "$EST" = "13" ] || fail "JRA work items ที่มี estimate = $EST (ต้องเป็น 13)"
PTS=$(q "select count(*) from estimate_points ep join projects p on p.id=ep.project_id where p.identifier='JRA' and p.deleted_at is null and ep.deleted_at is null")
[ "$PTS" = "6" ] || fail "estimate points ของ JRA = $PTS (ต้องเป็น 6)"
DONE_S1=$(q "select count(*) from cycle_issues ci join cycles c on c.id=ci.cycle_id join issues i on i.id=ci.issue_id where c.name='Sprint 1' and i.completed_at is not null and ci.deleted_at is null")
[ "$DONE_S1" = "5" ] || fail "Sprint 1 completed items = $DONE_S1 (ต้องเป็น 5)"
LOG429=$(q "select count(*) from api_activity_logs where response_code=429")
[ "${LOG429:-0}" -ge 1 ] || fail "ยังไม่มี 429 ใน api_activity_logs (รัน bash rate_limit_demo.sh ก่อน)"
RATE=$(grep -E '^API_KEY_RATE_LIMIT=' ~/plane-selfhost/plane.env | cut -d= -f2)
[ "$RATE" = "60/minute" ] || fail "API_KEY_RATE_LIMIT=$RATE (ต้อง restore เป็น 60/minute)"
echo "PASS: LAB 7 — TRL 20 (12 cards + 8 checklist) · JRA 13 (2 modules · 2 cycles · 6 estimate points · Sprint 1 done 5) · 429 logged ${LOG429}× · rate limit $RATE"
