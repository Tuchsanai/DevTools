#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")"
project=${VERIFY_PROJECT:-vcafe-lab3}
compose=(docker compose -p "$project" -f docker-compose.yml)
base=http://127.0.0.1:8000
passed=0

cleanup() {
  "${compose[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT INT TERM

pass() {
  echo "[PASS] $1"
  passed=$((passed + 1))
}

die() {
  echo "[FAIL] $1" >&2
  "${compose[@]}" ps >&2 || true
  "${compose[@]}" logs --tail 80 >&2 || true
  exit 1
}

wait_healthy() {
  local service=$1 limit=${2:-120} cid status elapsed=0
  while (( elapsed < limit )); do
    cid=$("${compose[@]}" ps -q "$service" | head -n 1)
    if [[ -n "$cid" ]]; then
      status=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$cid" 2>/dev/null || true)
      [[ "$status" == healthy || "$status" == running ]] && return 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
  return 1
}

queue_value() {
  local column=$1
  "${compose[@]}" exec -T rabbit rabbitmqctl -q list_queues name "$column" |
    awk -v column="$column" '$1=="order_queue" {print $2}'
}

post_order() {
  local menu=$1 qty=$2 name=$3 response
  response=$(curl -fsS -X POST "$base/api/orders" -H 'Content-Type: application/json' \
    -d "{\"menu_code\":\"$menu\",\"qty\":$qty,\"customer_name\":\"$name\"}")
  python3 -c 'import json,sys; print(json.load(sys.stdin)["id"])' <<<"$response"
}

db_status() {
  "${compose[@]}" exec -T db psql -U student -d cafedb -Atc "SELECT status FROM orders WHERE id=$1"
}

wait_status() {
  local id=$1 wanted=$2 limit=${3:-30} elapsed=0 actual
  while (( elapsed < limit )); do
    actual=$(db_status "$id")
    [[ "$actual" == "$wanted" ]] && return 0
    sleep 1
    elapsed=$((elapsed + 1))
  done
  return 1
}

echo "== LAB3 verify: project $project =="
cleanup
"${compose[@]}" config --quiet || die "compose syntax"
"${compose[@]}" up -d --build --scale worker=0
for service in traefik db rabbit api web; do
  wait_healthy "$service" 120 || die "$service ไม่ healthy ภายใน 120 วินาที"
done
pass "COMMON-READY services ที่ใช้ healthy ภายใน 120 วินาที"

ids=()
for fixture in 'latte 1 verify-a' 'mocha 1 verify-b' 'matcha 1 verify-c'; do
  read -r menu qty name <<<"$fixture"
  ids+=("$(post_order "$menu" "$qty" "$name")")
  sleep 1
done
[[ $(queue_value messages_ready) == 3 ]] || die "LAB3-V01 ต้องมี 3 messages_ready จาก 3 orders"
"${compose[@]}" restart rabbit >/dev/null
wait_healthy rabbit 120 || die "rabbit ไม่กลับมา healthy หลัง restart"
[[ $(queue_value messages_ready) == 3 ]] || die "LAB3-V01 persistent messages ไม่รอด rabbit restart"
pass "LAB3-V01 หนึ่ง order ต่อหนึ่ง persistent message และ durable queue รอด restart"

"${compose[@]}" up -d --scale worker=1 worker >/dev/null
wait_healthy worker 120 || die "worker ไม่ healthy"
deadline=$((SECONDS + 30))
while (( SECONDS < deadline )); do
  ready=$("${compose[@]}" exec -T db psql -U student -d cafedb -Atc "SELECT count(*) FROM orders WHERE id IN (${ids[0]},${ids[1]},${ids[2]}) AND status='READY'")
  [[ "$ready" == 3 ]] && break
  sleep 1
done
[[ ${ready:-0} == 3 ]] || die "LAB3-V01 orders ไม่ READY ภายใน 30 วินาที"
[[ $(queue_value messages_ready) == 0 ]] || die "LAB3-V01 queue ยังมีงานค้างหลัง READY"
pass "LAB3-V01 worker ack หลังทั้ง 3 orders เป็น READY ภายใน 30 วินาที"

crash_id=$(post_order cocoa 3 verify-redelivery)
wait_status "$crash_id" BREWING 12 || die "LAB3-V02 ไม่เห็นสถานะ BREWING"
[[ $(queue_value messages_unacknowledged) == 1 ]] || die "LAB3-V02 งาน BREWING ต้องยัง unacknowledged"
"${compose[@]}" stop -t 1 worker >/dev/null
[[ $(queue_value messages_ready) == 1 ]] || die "LAB3-V02 งานไม่ถูก requeue หลัง worker หยุด"
started=$SECONDS
"${compose[@]}" start worker >/dev/null
wait_healthy worker 120 || die "worker ไม่ healthy หลัง start"
wait_status "$crash_id" READY 30 || die "LAB3-V02 order เดิมไม่ READY หลัง redelivery"
(( SECONDS - started <= 30 )) || die "LAB3-V02 READY เกิน 30 วินาที"
pass "LAB3-V02 manual ack ทำให้งาน requeue และ order เดิม READY หลัง redelivery"

"${compose[@]}" up -d --scale worker=2 worker >/dev/null
deadline=$((SECONDS + 120))
while (( SECONDS < deadline )); do
  [[ $("${compose[@]}" ps -q worker | wc -l) -eq 2 ]] && break
  sleep 2
done
[[ $("${compose[@]}" ps -q worker | wc -l) -eq 2 ]] || die "scale worker=2 ไม่สำเร็จ"
consumer_prefetch=$("${compose[@]}" exec -T rabbit rabbitmqctl -q list_consumers queue_name prefetch_count | awk '$1=="order_queue" {print $2}' | sort -u)
[[ "$consumer_prefetch" == 1 ]] || die "LAB3-V02 consumer ไม่ได้ prefetch_count=1"
fair_ids=()
for n in 1 2 3 4; do
  fair_ids+=("$(post_order espresso 1 "fair-$n")")
  sleep 1
done
deadline=$((SECONDS + 30))
while (( SECONDS < deadline )); do
  fair_ready=$("${compose[@]}" exec -T db psql -U student -d cafedb -Atc "SELECT count(*) FROM orders WHERE id IN ($(IFS=,; echo "${fair_ids[*]}")) AND status='READY'")
  [[ "$fair_ready" == 4 ]] && break
  sleep 1
done
[[ ${fair_ready:-0} == 4 ]] || die "LAB3-V02 fair-dispatch fixture ไม่ READY"
workers_with_jobs=0
while read -r cid; do
  docker logs "$cid" 2>&1 | grep -q 'กำลังชง' && workers_with_jobs=$((workers_with_jobs + 1))
done < <("${compose[@]}" ps -q worker)
[[ $workers_with_jobs -eq 2 ]] || die "LAB3-V02 งานไม่ได้กระจายถึง worker ทั้ง 2"
pass "LAB3-V02 prefetch=1 และ fair dispatch กระจายงานถึง worker ทั้งสอง"

services=$("${compose[@]}" config --services)
! grep -qx kafka <<<"$services" || die "LAB3-V03 ต้องไม่มี Kafka service"
"${compose[@]}" exec -T api python -c "import sys,main; assert main.EVENTS_ENABLED is False; assert 'kafka' not in sys.modules"
first_worker=$("${compose[@]}" ps -q worker | head -n 1)
docker exec "$first_worker" python -c "import sys,worker; assert worker.EVENTS_ENABLED is False; assert 'kafka' not in sys.modules"
! "${compose[@]}" config | awk '/^  web:/{p=1;next} /^  [a-z].*:/{p=0} p' | grep -q RABBIT_URL || die "web ต้องไม่รู้ RABBIT_URL"
pass "LAB3-V03 EVENTS_ENABLED=0 ไม่ import/connect Kafka และ web ไม่ถือ broker credential"

code=$(curl -sS -o /tmp/vcafe-lab3-error.json -w '%{http_code}' "$base/api/orders/999999")
headers=$(curl -sSI "$base/api/ping" | tr -d '\r')
[[ "$code" == 404 ]] || die "interface unknown order ต้องเป็น 404"
grep -qi '^x-served-by:' <<<"$headers" || die "interface ขาด X-Served-By"
grep -qi '^x-cafe-api-version: 1$' <<<"$headers" || die "interface ขาด API version 1"
pass "COMMON-INTERFACE API error และ application headers ตรง contract"

echo "ALL CHECKS PASSED ($passed checks)"
