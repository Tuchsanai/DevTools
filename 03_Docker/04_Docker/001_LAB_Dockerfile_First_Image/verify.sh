#!/bin/bash
# verify.sh — LAB 1 : รันจากโฟลเดอร์แล็บ ก่อนขั้น "ล้างกระดาน"
# exit 0 = ผ่านทุกข้อ
PASS=0; FAIL=0
ok()   { echo "PASS  $1"; PASS=$((PASS+1)); }
bad()  { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

# 1) image ครบสอง tag
docker image inspect myapp:1.0 >/dev/null 2>&1 && ok "image myapp:1.0 มีอยู่" || bad "ไม่พบ image myapp:1.0 (ข้อ 3)"
docker image inspect myapp:2.0 >/dev/null 2>&1 && ok "image myapp:2.0 มีอยู่" || bad "ไม่พบ image myapp:2.0 (ข้อ 6)"

# 2) container myapp รันอยู่ด้วย image 2.0
IMG=$(docker inspect -f '{{.Config.Image}}' myapp 2>/dev/null)
[ "$IMG" = "myapp:2.0" ] && ok "container myapp รันจาก myapp:2.0" || bad "container myapp ไม่ได้รันจาก myapp:2.0 (ข้อ 7) — พบ: ${IMG:-ไม่มี}"

# 3) เว็บตอบข้อความใหม่ + เวอร์ชัน 2.0 (จาก -e)
BODY=$(curl -s --max-time 5 http://localhost:8081)
echo "$BODY" | grep -q 'ไม่ต้องลง Python ใหม่' && ok "หน้าเว็บเสิร์ฟข้อความใหม่ (image 2.0)" || bad "หน้าเว็บไม่ใช่ข้อความใหม่ (ข้อ 6–7)"
echo "$BODY" | grep -q 'เวอร์ชัน&nbsp;<b>2.0' && ok "เวอร์ชัน 2.0 จาก -e APP_VERSION" || bad "เวอร์ชันบนหน้าเว็บไม่ใช่ 2.0 — ลืม -e ? (ข้อ 7)"

# 4) .dockerignore + COPY ระบุชื่อ → ใน /app มีแค่ 2 ไฟล์
FILES=$(docker exec myapp ls /app 2>/dev/null | sort | tr '\n' ' ')
[ "$FILES" = "app.py requirements.txt " ] && ok "/app มีเฉพาะ app.py + requirements.txt" || bad "/app มีไฟล์เกิน: $FILES (ข้อ 8)"

# 5) build ซ้ำต้องโดน cache (ต้องรันจากโฟลเดอร์แล็บ)
if [ -f Dockerfile ]; then
  N=$(docker build -t myapp:2.0 . 2>&1 | grep -c 'CACHED')
  [ "$N" -ge 2 ] && ok "build ซ้ำเจอ CACHED $N ครั้ง — layer cache ทำงาน" || bad "build ซ้ำไม่เจอ CACHED (ข้อ 6)"
else
  bad "ไม่พบ Dockerfile — ต้องรัน verify.sh จากโฟลเดอร์แล็บ"
fi

echo "-----------------------------"
if [ "$FAIL" -eq 0 ]; then echo "ALL CHECKS PASSED ($PASS/$((PASS+FAIL)))"; exit 0
else echo "FAILED $FAIL CHECK(S) — ดูเลขข้อในวงเล็บแล้วย้อนกลับไปทำ"; exit 1; fi
