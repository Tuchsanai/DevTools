#!/usr/bin/env bash
# ยิง request ไปที่ร้านทีละครั้ง (curl ใหม่ทุกครั้ง = connection ใหม่ → Service สุ่ม Pod ใหม่ทุกครั้ง)
# ใช้:  ./hit.sh [-q] [URL] [N] [DELAY]
#   URL   ค่าเริ่มต้น http://localhost:30080/api/whoami  (ตอบ "<ชื่อ Pod> <เวอร์ชัน>")
#   N     จำนวนครั้ง (60)      DELAY  เว้นระหว่างครั้ง วินาที (0.1)
#   -q    โหมดเงียบ: พิมพ์ . (สำเร็จ) / x (ล้มเหลว) ระหว่างยิง แล้วสรุป ok/err — ใช้ตอนลบ Pod
QUIET=0
if [ "$1" = "-q" ]; then QUIET=1; shift; fi
URL=${1:-http://localhost:30080/api/whoami}
N=${2:-60}
DELAY=${3:-0.1}

ok=0; err=0; first_err=""; last_err=""
declare -a lines errs
start=$(date +%s.%N)
for i in $(seq "$N"); do
  # -f: HTTP 4xx/5xx นับเป็น err, -m 2: รอไม่เกิน 2 วินาที
  if body=$(curl -sS -f -m 2 "$URL" 2>&1); then
    ok=$((ok + 1)); lines+=("$body"); [ $QUIET = 1 ] && printf '.'
  else
    err=$((err + 1)); errs+=("${body%% after*}")
    now=$(date +%s.%N); [ -z "$first_err" ] && first_err=$now; last_err=$now
    [ $QUIET = 1 ] && printf 'x'
  fi
  sleep "$DELAY"
done
end=$(date +%s.%N)
[ $QUIET = 1 ] && echo

if [ $QUIET = 0 ] && [ $ok -gt 0 ]; then
  echo "จำนวน  Pod  เวอร์ชัน"
  printf '%s\n' "${lines[@]}" | sort | uniq -c
fi
if [ $err -gt 0 ]; then
  echo "ข้อความ error:"
  printf '%s\n' "${errs[@]}" | sort | uniq -c
  awk -v a="$first_err" -v b="$last_err" 'BEGIN { printf "ช่วงที่มี err: %.1f วินาที\n", b - a }'
fi
awk -v a="$start" -v b="$end" -v ok=$ok -v err=$err 'BEGIN { printf "ok=%d err=%d (ใช้เวลา %.1f วินาที)\n", ok, err, b - a }'
