#!/bin/bash
# check_lab08.sh — ด่านหลักฐานของ LAB 8: webhook active · allowlist · event ที่ลายเซ็นถูกต้อง · การ์ดที่ถูกปฏิเสธ · rule ทำงาน
set -u
sql() { pc exec -T -e PGPASSWORD=plane plane-db psql -U plane -d plane -tA -c "$1" 2>/dev/null | tr -d '[:space:]'; }
fail=0; ok() { echo "  ✓ $1"; }; bad() { echo "  ✗ $1"; fail=1; }
cd "$(dirname "$0")"
n=$(sql "select count(*) from webhooks where url like '%hookwall.lab%' and is_active and deleted_at is null")
[ "${n:-0}" -ge 1 ] && ok "webhook ชี้ไป hookwall.lab และ active" || bad "ไม่มี webhook ที่ url มี hookwall.lab (หรือถูกปิด)"
grep -Eq '^WEBHOOK_ALLOWED_HOSTS=.*hookwall\.lab' ~/plane-selfhost/plane.env && ok "WEBHOOK_ALLOWED_HOSTS มี hookwall.lab" || bad "plane.env ยังไม่มี WEBHOOK_ALLOWED_HOSTS=hookwall.lab,dashboard.lab"
pc exec worker env 2>/dev/null | grep -q 'WEBHOOK_ALLOWED_HOSTS=.*hookwall\.lab' && ok "worker อ่าน allowlist แล้ว (recreate ผ่าน pc up -d)" || bad "worker ยังไม่เห็น WEBHOOK_ALLOWED_HOSTS — ต้อง pc up -d api worker beat-worker"
n=$(sql "select count(*) from webhook_logs where response_status = '200'")
[ "${n:-0}" -ge 3 ] && ok "webhook_logs ส่งสำเร็จ (200) $n ครั้ง" || bad "ส่งสำเร็จ (200) แค่ ${n:-0} ครั้ง (ต้องการ ≥ 3)"
F=hookwall/data/events.jsonl
if [ -f "$F" ]; then
  okn=$(grep -c '"status": "OK"' "$F"); rej=$(grep -c '"status": "REJECTED"' "$F")
  [ "$okn" -ge 3 ] && ok "hookwall รับ event ลายเซ็นถูกต้อง $okn ใบ" || bad "event ที่ลายเซ็นถูกต้องมี $okn (ต้องการ ≥ 3)"
  [ "$rej" -ge 1 ] && ok "มีการ์ด REJECTED $rej ใบ (replay --tamper)" || bad "ยังไม่มี REJECTED — รัน bash replay_event.sh --tamper"
  grep -q '"rule": "R1' "$F" && ok "rule R1 เคยทำงาน" || bad "rule R1 ยังไม่เคยทำงาน (ตั้ง work item เป็น Urgent โดยไม่มี assignee)"
else bad "ไม่พบ $F — hookwall ยังไม่เคยรับ event"; fi
n=$(sql "select count(*) from issue_comments c join users u on u.id=c.actor_id where u.email='automation@example.com' and c.deleted_at is null")
[ "${n:-0}" -ge 1 ] && ok "comment จาก bot user ปรากฏใน Plane $n รายการ" || bad "ยังไม่มี comment ที่ actor เป็น automation@example.com"
if [ "$fail" = 0 ]; then echo "PASS: LAB 8 — webhook active · allowlist in env+worker · signed events · rejected tamper · rule fired · bot comment"; else echo "FAIL: ยังมีข้อที่ไม่ผ่านด้านบน"; exit 1; fi
