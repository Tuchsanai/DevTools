#!/usr/bin/env bash
# LAB 9: ยิง HTTPS ผ่านประตู Traefik วนหลายครั้ง แล้วนับว่าใครตอบ / error กี่ครั้ง (status อะไร)
# ใช้:  ./loop.sh [URL] [N] [DELAY]
#   URL   ค่าเริ่มต้น https://shop.localhost:30081/   (curl ใน k8s-lab แปลง *.localhost เป็น 127.0.0.1 เอง)
#   N     จำนวนครั้ง (300)     DELAY เว้นระหว่างครั้ง วินาที (0.05)
# -k = ข้ามการตรวจใบรับรอง self-signed (หรือ CURL_OPTS="--cacert ../lab07-tls/tls.crt" ./loop.sh)
URL=${1:-https://shop.localhost:30081/}
N=${2:-300}
DELAY=${3:-0.05}
OPTS=${CURL_OPTS:--k}
ok=0; err=0
declare -A who codes
start=$(date +%s.%N)
for i in $(seq "$N"); do
  # body + status บรรทัดสุดท้าย, -m 2 = รอไม่เกิน 2 วินาที (curl ต่อไม่ได้ = status 000)
  out=$(curl -s -m 2 $OPTS -w '\n%{http_code}' "$URL")
  code=${out##*$'\n'}
  if [ "$code" = 200 ]; then
    ok=$((ok + 1)); name=$(grep -m1 -o 'Name: .*' <<<"$out"); name=${name#Name: }
    who[${name:-?}]=$(( ${who[${name:-?}]:-0} + 1 ))
  else
    err=$((err + 1)); codes[$code]=$(( ${codes[$code]:-0} + 1 ))
  fi
  sleep "$DELAY"
done
end=$(date +%s.%N)
for k in "${!who[@]}"; do echo "  $k ${who[$k]}"; done | sort
for k in "${!codes[@]}"; do echo "  error $k × ${codes[$k]}"; done | sort
awk -v a="$start" -v b="$end" -v ok=$ok -v err=$err 'BEGIN { printf "ok=%d err=%d (ใช้เวลา %.1f วินาที)\n", ok, err, b - a }'
