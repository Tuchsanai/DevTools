#!/bin/bash
# run_dashboard.sh — build + รัน dashboard ใน network ของ Plane (alias dashboard.lab) และเปิด port 8090
# ใช้: bash run_dashboard.sh [PROJECT=PLAB] [REFRESH=60]     (token จาก ~/.plane_token · เรียก Plane ผ่าน http://proxy)
set -euo pipefail
cd "$(dirname "$0")"
: "${PROJECT:=PLAB}"; : "${REFRESH:=60}"; : "${WS:=devtools-lab}"
[ -f ~/.plane_token ] || { echo "ไม่พบ ~/.plane_token (LAB 3)"; exit 1; }
docker build -q -t dashboard:lab dashboard/ >/dev/null && echo "image dashboard:lab พร้อม"
docker rm -f dashboard >/dev/null 2>&1 || true
docker run -d --name dashboard --network plane_default --network-alias dashboard.lab -p 8090:8090 \
  -e PLANE_BASE=http://proxy -e PLANE_API_TOKEN="$(cat ~/.plane_token)" -e WS="$WS" -e PROJECT="$PROJECT" -e REFRESH="$REFRESH" \
  dashboard:lab >/dev/null
for i in $(seq 1 30); do curl -s -o /dev/null --max-time 2 http://localhost:8090/api/health && break; sleep 1; done
curl -s http://localhost:8090/api/health && echo
echo "เปิด http://localhost:8090 (forward port 8090) · log: docker logs -f dashboard"
