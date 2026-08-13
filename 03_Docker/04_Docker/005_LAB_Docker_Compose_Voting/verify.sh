#!/bin/bash
# verify.sh — LAB 5 : รันจากโฟลเดอร์แล็บ ตอนระบบเปิดอยู่และโหวตแล้ว (ข้อ 5)
# exit 0 = ผ่านทุกข้อ
PASS=0; FAIL=0
ok()  { echo "PASS  $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

[ -f docker-compose.yml ] || { echo "FAIL  ไม่พบ docker-compose.yml — ต้องรันจากโฟลเดอร์แล็บ"; exit 1; }

# 1) 3 services รันครบ
UP=$(docker compose ps --services --status running 2>/dev/null | sort | tr '\n' ' ')
[ "$UP" = "redis result vote " ] && ok "3 services รันครบ (redis result vote)" || bad "services ที่รันอยู่: ${UP:-ไม่มี} (ข้อ 2)"

# 2) redis ต้อง healthy (ผลของ healthcheck)
HS=$(docker inspect -f '{{.State.Health.Status}}' "$(docker compose ps -q redis 2>/dev/null)" 2>/dev/null)
[ "$HS" = "healthy" ] && ok "redis สถานะ healthy" || bad "redis ไม่ healthy: ${HS:-ไม่พบ} (ข้อ 2)"

# 3) หน้าเว็บตอบทั้งสอง port
curl -s --max-time 5 localhost:8085 | grep -q 'CATS' && ok "หน้าโหวต (8085) ตอบ" || bad "หน้าโหวต 8085 ไม่ตอบ (ข้อ 2)"
curl -s --max-time 5 localhost:8086 | grep -qi 'result\|คะแนน' && ok "หน้าผลคะแนน (8086) ตอบ" || bad "หน้าผล 8086 ไม่ตอบ (ข้อ 2)"

# 4) มีคะแนนแล้ว และ /data ตรงกับค่าใน redis (เว็บ = หน้ากากของ redis)
DATA=$(curl -s --max-time 5 localhost:8086/data)
CATS_WEB=$(echo "$DATA" | grep -o '"cats": *[0-9]*' | grep -o '[0-9]*')
CATS_DB=$(docker compose exec -T redis redis-cli GET votes:cats 2>/dev/null | tr -d '\r')
if [ -z "$CATS_WEB" ]; then bad "/data ไม่ตอบ JSON: $DATA (ข้อ 3)"
elif [ "$CATS_WEB" = "0" ] || [ -z "$CATS_DB" ]; then bad "ยังไม่มีคะแนนโหวต — กดโหวตก่อนแล้วรันใหม่ (ข้อ 3)"
elif [ "$CATS_WEB" = "$CATS_DB" ]; then ok "คะแนนบนเว็บ ($CATS_WEB) ตรงกับใน redis ($CATS_DB)"
else bad "คะแนนเว็บ ($CATS_WEB) ไม่ตรง redis ($CATS_DB)"; fi

# 5) named volume ของโปรเจกต์มีจริง
docker volume ls --format '{{.Name}}' | grep -q '_vote-data$' && ok "named volume vote-data ถูกสร้าง" || bad "ไม่พบ volume vote-data (ข้อ 1–2)"

# 6) DNS ชื่อ service ใช้งานได้จริงจากใน vote
IP=$(docker compose exec -T vote python -c "import socket;print(socket.gethostbyname('redis'))" 2>/dev/null | tr -d '\r')
case "$IP" in
  *.*.*.*) ok "ใน container vote ชื่อ 'redis' แปลเป็น IP ได้ ($IP)";;
  *) bad "แปลชื่อ redis ใน vote ไม่ได้ (Embedded DNS) (ข้อ 1)";;
esac

# 7) redis ไม่ถูก publish port สู่โลกภายนอก (อยู่ back-tier เท่านั้น)
PB=$(docker inspect -f '{{json .HostConfig.PortBindings}}' "$(docker compose ps -q redis 2>/dev/null)" 2>/dev/null)
{ [ "$PB" = "{}" ] || [ "$PB" = "null" ]; } && ok "redis ไม่ map port ออกนอก (หลังบ้านจริง)" || bad "redis ถูก publish port: $PB"

echo "-----------------------------"
if [ "$FAIL" -eq 0 ]; then echo "ALL CHECKS PASSED ($PASS/$((PASS+FAIL)))"; exit 0
else echo "FAILED $FAIL CHECK(S)"; exit 1; fi
