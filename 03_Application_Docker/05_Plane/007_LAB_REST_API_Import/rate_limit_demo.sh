#!/bin/bash
# rate_limit_demo.sh — ยิง GET /users/me/ รัว ๆ 62 ครั้ง เพื่อดู 60 × 200 → 429 แล้ว "รอให้ถูกวิธี" ตาม Retry-After
set -u
BASE=${PLANE_BASE:-http://localhost:8080}/api/v1
TOKEN=$(cat ~/.plane_token 2>/dev/null) || { echo "ไม่พบ ~/.plane_token"; exit 1; }
URL="$BASE/users/me/"
N=${1:-62}
hdr() { curl -s -o /dev/null -D - -H "X-API-Key: $TOKEN" "$URL"; }   # -D - = พิมพ์เฉพาะ response headers
field() { echo "$1" | tr -d '\r' | awk -v k="$2" 'tolower($1)==tolower(k)":" {print $2}'; }

# --- หน้าต่างต้องสะอาดก่อน ไม่งั้นจะโดน 429 เร็วกว่าที่คาด (limit นับย้อนหลัง 60 วินาที) ---
H=$(hdr); REM=$(field "$H" X-RateLimit-Remaining)
if [ "${REM:-0}" -lt 59 ]; then
  echo "Remaining ตอนนี้ = $REM (ไม่ใช่หน้าต่างสด) → รอ 61 วินาทีให้ history 60 วินาทีก่อนหน้าหลุดออกไปก่อน…"
  sleep 61
fi

echo "== ยิง $N ครั้งติดกัน (limit = API_KEY_RATE_LIMIT ใน plane.env)"
T0=$(date +%s)
for i in $(seq 1 $N); do
  H=$(hdr)
  CODE=$(echo "$H" | head -1 | awk '{print $2}')
  REM=$(field "$H" X-RateLimit-Remaining); RESET=$(field "$H" X-RateLimit-Reset); RETRY=$(field "$H" Retry-After)
  if [ "$CODE" = "429" ]; then
    printf '\033[31mcall %2d → HTTP 429 Too Many Requests\033[0m  Retry-After=%ss  (ไม่มี X-RateLimit-* ในคำตอบ 429)\n' "$i" "$RETRY"
    echo "   X-RateLimit-Reset ล่าสุดที่เห็น = $LAST_RESET ($(date -d @"$LAST_RESET" +%H:%M:%S)) · ตอนนี้ $(date +%H:%M:%S)"
    echo "   client ที่ดีต้อง sleep ${RETRY}s แล้วค่อยยิงใหม่ (ไม่ใช่วนยิงซ้ำถี่ ๆ)…"
    sleep $((RETRY + 1))
    H=$(hdr); CODE=$(echo "$H" | head -1 | awk '{print $2}'); REM=$(field "$H" X-RateLimit-Remaining)
    printf '\033[32mหลังรอ → HTTP %s  X-RateLimit-Remaining=%s\033[0m\n' "$CODE" "$REM"
    break
  fi
  LAST_RESET=$RESET
  if [ "$i" -le 3 ] || [ "$i" -ge 58 ]; then
    printf 'call %2d → HTTP %s  X-RateLimit-Remaining=%-2s  X-RateLimit-Reset=%s\n' "$i" "$CODE" "$REM" "$RESET"
  elif [ "$i" -eq 4 ]; then
    echo "   …"
  fi
done
echo "== ใช้เวลา $(( $(date +%s) - T0 )) วินาที (รวมเวลารอ)"
