#!/bin/bash
# verify.sh — LAB 3 : รันหลังจบข้อ 7 (ก่อนล้างกระดาน)
# ตรวจเฉพาะสิ่งที่พิสูจน์ได้ในเครื่อง — ผ่านได้แม้ยังไม่มีบัญชี Docker Hub
# exit 0 = ผ่านทุกข้อ
PASS=0; FAIL=0
ok()  { echo "PASS  $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

# 1) มี tag ตามกติกา <username>/docker-card:1.0 (ป้ายไหนก็ได้ที่มี "/")
NAMED=$(docker images --format '{{.Repository}}:{{.Tag}}' | grep -E '^[a-z0-9.:-]+/docker-card:1.0$' | grep -v '^localhost:5000/' | head -1)
if [ -n "$NAMED" ]; then ok "พบ tag ตามกติกา username/repo:tag → $NAMED"
else bad "ไม่พบ tag รูปแบบ <username>/docker-card:1.0 (ข้อ 5 หรือ 7)"; fi

# 2) container card รันอยู่ และเสิร์ฟหน้านามบัตร (h1 ไม่ใช่ค่าตั้งต้น YOUR NAME)
H1=$(curl -s --max-time 5 localhost:8083 | grep -o '<h1>[^<]*</h1>' | head -1)
if [ -z "$H1" ]; then bad "curl localhost:8083 ไม่ได้หน้านามบัตร — container card รันอยู่ไหม? (ข้อ 2/7)"
elif echo "$H1" | grep -q 'YOUR NAME'; then bad "ยังไม่ได้แก้ชื่อบนนามบัตร (ข้อ 1) — พบ $H1"
else ok "นามบัตรออนไลน์เสิร์ฟชื่อที่แก้แล้ว → $H1"; fi

# 3) tag ≠ copy : ทุกป้ายของ docker-card ต้องชี้ image ID เดียวกัน
IDS=$(docker images --format '{{.Repository}}:{{.Tag}} {{.ID}}' | awk '/docker-card:1.0/{print $2}' | sort -u | wc -l)
N=$(docker images --format '{{.Repository}}' | grep -c 'docker-card')
if [ "$N" -ge 1 ] && [ "$IDS" -eq 1 ]; then ok "ทุกป้าย docker-card:1.0 ชี้ IMAGE ID เดียวกัน (tag = ป้าย ไม่ใช่ copy)"
elif [ "$N" -eq 0 ]; then bad "ไม่พบ image docker-card ในเครื่อง (ข้อ 2)"
else bad "ป้าย docker-card:1.0 ชี้คนละ ID — build ซ้ำหลังแก้ไฟล์? tag ใหม่อีกรอบ (ข้อ 5)"; fi

# 4) self-host registry ทำงานและมี docker-card อยู่ข้างใน
CAT=$(curl -s --max-time 5 localhost:5000/v2/_catalog)
echo "$CAT" | grep -q '"docker-card"' && ok "registry ในเครื่อง (localhost:5000) มี docker-card แล้ว" \
  || bad "registry ในเครื่องไม่ตอบ หรือยังไม่มี docker-card (ข้อ 6) — ได้: ${CAT:-ไม่ตอบ}"

echo "-----------------------------"
if [ "$FAIL" -eq 0 ]; then echo "ALL CHECKS PASSED ($PASS/$((PASS+FAIL)))"; exit 0
else echo "FAILED $FAIL CHECK(S)"; exit 1; fi
