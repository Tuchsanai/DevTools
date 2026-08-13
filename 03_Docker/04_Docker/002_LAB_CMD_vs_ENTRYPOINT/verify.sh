#!/bin/bash
# verify.sh — LAB 2 : รันจากที่ไหนก็ได้ หลังจบข้อ 7 (ก่อนล้างกระดาน)
# exit 0 = ผ่านทุกข้อ
PASS=0; FAIL=0
ok()  { echo "PASS  $1"; PASS=$((PASS+1)); }
bad() { echo "FAIL  $1"; FAIL=$((FAIL+1)); }

# 1) image ครบ 3 ตัว
for img in cmd-example entrypoint-example both-example; do
  docker image inspect "$img" >/dev/null 2>&1 && ok "image $img มีอยู่" || bad "ไม่พบ image $img (ข้อ 2/4)"
done

# 2) metadata ตรงตาม Dockerfile
M1=$(docker inspect --format '{{json .Config.Entrypoint}}|{{json .Config.Cmd}}' cmd-example 2>/dev/null)
[ "$M1" = 'null|["figlet","Hello CMD"]' ] && ok "cmd-example: CMD ถูกต้อง ไม่มี ENTRYPOINT" || bad "metadata cmd-example ผิด: $M1"
M2=$(docker inspect --format '{{json .Config.Entrypoint}}|{{json .Config.Cmd}}' entrypoint-example 2>/dev/null)
[ "$M2" = '["figlet","Hello"]|null' ] && ok "entrypoint-example: ENTRYPOINT ถูกต้อง" || bad "metadata entrypoint-example ผิด: $M2"
M3=$(docker inspect --format '{{json .Config.Entrypoint}}|{{json .Config.Cmd}}' both-example 2>/dev/null)
[ "$M3" = '["figlet"]|["Hello Docker"]' ] && ok "both-example: ENTRYPOINT+CMD ถูกต้อง" || bad "metadata both-example ผิด: $M3"

# 3) พฤติกรรมจริง : CMD ถูกแทนที่ → date รันจริง (ขึ้น UTC/เลขปี)
OUT=$(docker run --rm cmd-example date 2>/dev/null)
echo "$OUT" | grep -qE 'UTC|20[0-9]{2}' && ok "cmd-example date → รัน date จริง" || bad "cmd-example date ไม่ได้วันเวลา: $OUT"

# 4) พฤติกรรมจริง : ENTRYPOINT ต่อท้าย → ได้ ASCII ไม่ใช่วันเวลา
OUT=$(docker run --rm entrypoint-example date 2>/dev/null)
if echo "$OUT" | grep -qE 'UTC'; then bad "entrypoint-example date ได้วันเวลา — ไม่ควรเกิด"
elif [ "$(echo "$OUT" | wc -l)" -ge 4 ]; then ok "entrypoint-example date → figlet วาดคำว่า date (ต่อท้าย)"
else bad "entrypoint-example date ผลผิดปกติ: $OUT"; fi

# 5) both-example : args แทนเฉพาะ CMD, figlet ยังทำงาน
OUT=$(docker run --rm both-example "VERIFY" 2>/dev/null)
[ "$(echo "$OUT" | wc -l)" -ge 4 ] && ok "both-example \"VERIFY\" → figlet ยังเป็นโปรแกรมหลัก" || bad "both-example ไม่วาด ASCII: $OUT"

echo "-----------------------------"
if [ "$FAIL" -eq 0 ]; then echo "ALL CHECKS PASSED ($PASS/$((PASS+FAIL)))"; exit 0
else echo "FAILED $FAIL CHECK(S)"; exit 1; fi
