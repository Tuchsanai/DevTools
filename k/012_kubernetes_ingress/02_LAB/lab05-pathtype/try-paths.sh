#!/usr/bin/env bash
# LAB 5: ยิงหลาย path ไปที่ชื่อเดียว แล้วพิมพ์ตาราง "path → status → ใครตอบ"
# ใช้:  ./try-paths.sh [HOST] [path ...]
#   HOST ค่าเริ่มต้น paths.localhost   (ส่งผ่าน header Host ไปที่ประตู Traefik http://localhost:30080)
HOST=${1:-paths.localhost}; shift
PATHS=("$@")
[ ${#PATHS[@]} -eq 0 ] && PATHS=(/api /api/ /api/x /apix /API /docs /docs/ /docs/a /docsx /menu /menu/ /menux /impl /impl/x /implx)
printf '%-10s %-6s %s\n' PATH STATUS "ใครตอบ"
for p in "${PATHS[@]}"; do
  # -w ต่อท้าย status ไว้บรรทัดสุดท้ายของ body (ไม่ต้องใช้ไฟล์ชั่วคราว)
  out=$(curl -s -m 3 -H "Host: $HOST" -w '\n%{http_code}' "http://localhost:30080$p")
  code=${out##*$'\n'}
  who=$(grep -m1 -o 'Name: .*' <<<"$out")
  # path /api ของ whoami ตอบเป็น JSON → ดึงค่า "name" มาแสดงแทน
  [ -z "$who" ] && who=$(grep -m1 -o '"name":"[^"]*"' <<<"$out" | sed 's/"name":"\(.*\)"/Name: \1 (JSON)/')
  [ -z "$who" ] && who=$(head -1 <<<"$out" | cut -c1-40)
  printf '%-10s %-6s %s\n' "$p" "$code" "$who"
done
