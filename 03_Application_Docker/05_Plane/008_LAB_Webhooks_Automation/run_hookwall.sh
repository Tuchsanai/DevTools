#!/bin/bash
# run_hookwall.sh — build + รัน hookwall ใน network เดียวกับ Plane (plane_default) ให้ Plane เรียกถึงด้วยชื่อ "hookwall.lab" (ต้องมีจุด — URL validator ของ Django ไม่รับ hostname คำเดียว)
# ต้องมี: ~/.plane_wh_secret (secret จากหน้า Webhooks) และ ~/.plane_bot_token (Personal Access Token ของ automation@example.com)
set -euo pipefail
cd "$(dirname "$0")"
: "${WS:=devtools-lab}"
[ -f ~/.plane_wh_secret ] || { echo "ไม่พบ ~/.plane_wh_secret — สร้าง webhook ใน Workspace settings → Webhooks ก่อน"; exit 1; }
[ -f ~/.plane_bot_token ] || { echo "ไม่พบ ~/.plane_bot_token — สร้าง Personal Access Token ของ bot user ก่อน"; exit 1; }
docker build -q -t hookwall:lab hookwall/ >/dev/null && echo "image hookwall:lab พร้อม"
docker rm -f hookwall >/dev/null 2>&1 || true
mkdir -p hookwall/data
docker run -d --name hookwall --network plane_default --network-alias hookwall.lab -p 9000:9000 \
  -e PLANE_WEBHOOK_SECRET="$(cat ~/.plane_wh_secret)" -e PLANE_API_TOKEN="$(cat ~/.plane_bot_token)" \
  -e PLANE_BASE=http://proxy -e WS="$WS" -v "$PWD/hookwall/data:/data" hookwall:lab >/dev/null
sleep 2
curl -s http://localhost:9000/health && echo
echo "เปิด http://localhost:9000 (forward port 9000) · log: docker logs -f hookwall"
