#!/usr/bin/env bash
set -u -o pipefail

APP_DIR=${APP_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}
BASE_URL=${BASE_URL:-http://localhost:8000}
COMPOSE_FILE=${COMPOSE_FILE:-$APP_DIR/compose.yaml}
DC=(docker compose -f "$COMPOSE_FILE")
CURRENT_CHECK=BOOTSTRAP
TMP_DIR=$(mktemp -d)

cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

fail() {
  echo "CHECK $CURRENT_CHECK FAIL: $*" >&2
  echo "CHECK SUMMARY FAIL" >&2
  exit 1
}

pass() {
  echo "CHECK $CURRENT_CHECK PASS: $*"
}

require() {
  command -v "$1" >/dev/null 2>&1 || fail "missing command: $1"
}

dc() {
  "${DC[@]}" "$@"
}

service_cid() {
  dc ps -q "$1"
}

service_health() {
  docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$(service_cid "$1")" 2>/dev/null
}

wait_healthy() {
  local service=$1 timeout=${2:-120} start now
  start=$(date +%s)
  while [[ $(service_health "$service" || true) != healthy ]]; do
    now=$(date +%s)
    (( now - start < timeout )) || return 1
    sleep 1
  done
}

db_scalar() {
  dc exec -T db psql -U student -d cafedb -Atqc "$1"
}

wait_db_value() {
  local sql=$1 expected=$2 timeout=${3:-30} start now actual
  start=$(date +%s)
  while :; do
    actual=$(db_scalar "$sql" 2>/dev/null || true)
    [[ $actual == "$expected" ]] && return 0
    now=$(date +%s)
    (( now - start < timeout )) || return 1
    sleep 1
  done
}

request() {
  local method=$1 url=$2 data=${3:-} auth=${4:-}
  local -a args=(--noproxy '*' -sS -D "$TMP_DIR/headers" -o "$TMP_DIR/body" -w '%{http_code}' -X "$method")
  [[ -n $data ]] && args+=(-H 'Content-Type: application/json' --data "$data")
  [[ -n $auth ]] && args+=(-u "$auth")
  HTTP_STATUS=$(curl "${args[@]}" "$url") || return 1
  HTTP_BODY=$(cat "$TMP_DIR/body")
}

header_value() {
  local name=$1
  awk -v key="$name" 'BEGIN{key=tolower(key) ":"} {line=$0; if(index(tolower(line),key)==1){sub(/^[^:]*:[[:space:]]*/,"",line); sub(/\r$/, "", line); value=line}} END{print value}' "$TMP_DIR/headers"
}

json_field() {
  local path=$1
  python3 - "$path" "$TMP_DIR/body" <<'PY'
import json, pathlib, sys
value = json.loads(pathlib.Path(sys.argv[2]).read_text())
for part in sys.argv[1].split('.'):
    value = value[int(part)] if isinstance(value, list) else value[part]
print(value)
PY
}

post_order() {
  local menu=$1 qty=$2 customer=$3 attempts=${4:-12}
  local payload i
  payload=$(printf '{"menu_code":"%s","qty":%s,"customer_name":"%s"}' "$menu" "$qty" "$customer")
  for ((i=1; i<=attempts; i++)); do
    request POST "$BASE_URL/api/orders" "$payload" || return 1
    if [[ $HTTP_STATUS == 201 ]]; then
      ORDER_ID=$(json_field id)
      return 0
    fi
    [[ $HTTP_STATUS == 429 ]] || return 1
    sleep 1
  done
  return 1
}

direct_request() {
  local service=$1 method=$2 path=$3 data=${4:-}
  local cid ip
  cid=$(service_cid "$service")
  ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$cid")
  request "$method" "http://$ip:8000$path" "$data"
}

wait_analytics_lag_zero() {
  local timeout=${1:-60} start now output lag
  start=$(date +%s)
  while :; do
    output=$(dc exec -T kafka /opt/kafka/bin/kafka-consumer-groups.sh --bootstrap-server kafka:9092 --describe --group analytics 2>/dev/null || true)
    lag=$(awk '$1=="analytics" && $6 ~ /^[0-9]+$/ {sum+=$6; seen=1} END{if(seen) print sum}' <<<"$output")
    [[ $lag == 0 ]] && return 0
    now=$(date +%s)
    (( now - start < timeout )) || return 1
    sleep 2
  done
}

CURRENT_CHECK=BOOTSTRAP
for cmd in docker curl python3 awk; do require "$cmd"; done
[[ -f $COMPOSE_FILE ]] || fail "compose file not found"

CURRENT_CHECK=INT-READY-00
services=(traefik db rabbit kafka api-v1 api-v2 worker analytics web kafka-ui)
for service in "${services[@]}"; do
  wait_healthy "$service" 120 || fail "$service did not become healthy"
done
pass "all ${#services[@]} services healthy"

CURRENT_CHECK=REQ-01
request GET "$BASE_URL/" || fail "web front door unreachable"
[[ $HTTP_STATUS == 200 ]] || fail "web returned HTTP $HTTP_STATUS"
request GET "$BASE_URL/api/menu" || fail "API front door unreachable"
[[ $HTTP_STATUS == 200 ]] || fail "menu returned HTTP $HTTP_STATUS"
for service in db api-v1 api-v2; do
  [[ -z $(docker port "$(service_cid "$service")" 2>/dev/null) ]] || fail "$service publishes a host port"
done
dc logs --no-color traefik 2>&1 | grep 'GET /api/menu' >/dev/null || fail "Traefik access log lacks /api/menu"
pass "web/API use Traefik and DB/API publish no host ports"

CURRENT_CHECK=REQ-02
post_order latte 1 req02 || fail "valid order was not accepted: HTTP ${HTTP_STATUS:-none} ${HTTP_BODY:-}"
[[ $(json_field status) == QUEUED ]] || fail "new order response was not QUEUED"
request POST "$BASE_URL/api/orders" '{"menu_code":"unknown","qty":1,"customer_name":"bad-menu"}' || fail "unknown-menu request failed"
[[ $HTTP_STATUS == 404 && $(json_field code) == MENU_NOT_FOUND ]] || fail "unknown menu contract mismatch"
sleep 1
request POST "$BASE_URL/api/orders" '{"menu_code":"latte","qty":4,"customer_name":"bad-qty"}' || fail "invalid-qty request failed"
[[ $HTTP_STATUS == 422 && $(json_field code) == VALIDATION_ERROR ]] || fail "qty validation contract mismatch"
pass "valid 201/QUEUED and invalid 404/422 contracts"

CURRENT_CHECK=REQ-10
request GET "$BASE_URL/api/menu" || fail "menu request failed"
[[ $HTTP_STATUS == 200 && $(json_field items.0.code) == latte ]] || fail "menu schema/order mismatch"
[[ -n $(header_value X-Served-By) && $(header_value X-Cafe-Api-Version) =~ ^[12]$ ]] || fail "application headers missing on success"
request GET "$BASE_URL/api/queue" || fail "queue request failed"
[[ $HTTP_STATUS == 200 ]] || fail "queue returned HTTP $HTTP_STATUS"
python3 - "$TMP_DIR/body" <<'PY' || fail "queue schema mismatch"
import json, pathlib, sys
x=json.loads(pathlib.Path(sys.argv[1]).read_text()); assert isinstance(x["items"],list) and x["count"]==len(x["items"])
PY
request GET "$BASE_URL/api/orders/999999999" || fail "unknown order request failed"
[[ $HTTP_STATUS == 404 && $(json_field code) == ORDER_NOT_FOUND ]] || fail "unknown order contract mismatch"
[[ -n $(header_value X-Served-By) && $(header_value X-Cafe-Api-Version) =~ ^[12]$ ]] || fail "application headers missing on 404"
request GET "$BASE_URL/api/version" || fail "version request failed"
[[ $HTTP_STATUS == 200 && $(json_field version) =~ ^[12]$ ]] || fail "version schema mismatch"
pass "menu/queue/order/version schemas, errors, and headers"

CURRENT_CHECK=REQ-03A-WORKER-REQUEUE
post_order matcha 3 fault-worker || fail "could not create worker fault order"
fault_order=$ORDER_ID
wait_db_value "SELECT status FROM orders WHERE id=$fault_order" BREWING 10 || fail "order never entered BREWING"
worker_cid=$(service_cid worker)
docker kill --signal KILL "$worker_cid" >/dev/null || fail "could not kill worker"
docker start "$worker_cid" >/dev/null || fail "could not restart killed worker"
wait_healthy worker 30 || fail "worker did not restart healthy"
wait_db_value "SELECT status FROM orders WHERE id=$fault_order" READY 30 || fail "requeued order did not reach READY"
[[ $(docker inspect -f '{{.State.Running}}' "$worker_cid") == true ]] || fail "worker is not running after fault recovery"
pass "killed during BREWING; Rabbit redelivery completed same order READY"

CURRENT_CHECK=REQ-03B-RABBIT-DURABLE
dc stop worker >/dev/null || fail "could not stop worker"
post_order espresso 1 fault-rabbit || fail "could not enqueue durable order"
durable_order=$ORDER_ID
wait_db_value "SELECT status FROM orders WHERE id=$durable_order" QUEUED 5 || fail "order was not queued while worker stopped"
dc restart rabbit >/dev/null || fail "Rabbit restart failed"
wait_healthy rabbit 90 || fail "Rabbit did not recover healthy"
ready_messages=$(dc exec -T rabbit rabbitmqctl -q list_queues name messages_ready | awk '$1=="order_queue"{print $2}')
[[ ${ready_messages:-0} -ge 1 ]] || fail "durable message missing after Rabbit restart"
dc start worker >/dev/null || fail "worker start failed"
wait_healthy worker 30 || fail "worker did not return healthy"
wait_db_value "SELECT status FROM orders WHERE id=$durable_order" READY 30 || fail "durable order did not reach READY"
pass "persistent message survived Rabbit restart and completed"

CURRENT_CHECK=REQ-04
v1_cid=$(service_cid api-v1)
v1_host=$(docker inspect -f '{{.Config.Hostname}}' "$v1_cid")
direct_request api-v1 POST /api/health/fail || fail "could not toggle v1 fail"
[[ $HTTP_STATUS == 200 ]] || fail "health fail returned HTTP $HTTP_STATUS"
sleep 5
direct_request api-v1 GET /api/health || fail "direct health request transport failed"
[[ $HTTP_STATUS == 503 && $(json_field code) == HEALTH_FORCED ]] || fail "forced health did not return application 503"
[[ $(header_value X-Served-By) == "$v1_host" && $(header_value X-Cafe-Api-Version) == 1 ]] || fail "503 application headers mismatch"
for _ in $(seq 1 30); do
  request GET "$BASE_URL/api/version" || fail "gateway failed during withdrawal"
  [[ $(header_value X-Served-By) != "$v1_host" ]] || fail "unhealthy v1 still received traffic"
done
direct_request api-v1 POST /api/health/ok || fail "could not restore v1"
[[ $HTTP_STATUS == 200 ]] || fail "health ok returned HTTP $HTTP_STATUS"
sleep 5
seen_v1=0
for _ in $(seq 1 60); do
  request GET "$BASE_URL/api/version" || fail "gateway failed after restore"
  [[ $(header_value X-Served-By) == "$v1_host" ]] && seen_v1=1
done
[[ $seen_v1 == 1 ]] || fail "restored v1 did not return to rotation"
pass "active health withdrew and restored v1 replica"

CURRENT_CHECK=REQ-08
request GET "$BASE_URL/api/report/sales" || fail "unauthenticated report request failed"
[[ $HTTP_STATUS == 401 && -z $(header_value X-Served-By) && -z $(header_value X-Cafe-Api-Version) ]] || fail "report 401/gateway headers mismatch"
request GET "$BASE_URL/api/report/sales" '' manager:manager123 || fail "authenticated report request failed"
[[ $HTTP_STATUS == 200 && $(json_field claim) == trend-level ]] || fail "authenticated report contract mismatch"
request GET "$BASE_URL/dashboard" || fail "unauthenticated dashboard request failed"
[[ $HTTP_STATUS == 401 ]] || fail "dashboard without auth returned HTTP $HTTP_STATUS"
request GET "$BASE_URL/dashboard" '' manager:manager123 || fail "authenticated dashboard request failed"
[[ $HTTP_STATUS == 200 ]] || fail "dashboard with auth returned HTTP $HTTP_STATUS"
pass "report and dashboard enforce manager basicAuth"

CURRENT_CHECK=REQ-09
sleep 3
rate_dir="$TMP_DIR/rate"
mkdir -p "$rate_dir"
for i in $(seq 1 20); do
  curl --noproxy '*' -sS -o "$rate_dir/body-$i" -w '%{http_code}' -H 'Content-Type: application/json' --data "{\"menu_code\":\"cocoa\",\"qty\":1,\"customer_name\":\"rate-$i\"}" "$BASE_URL/api/orders" >"$rate_dir/code-$i" &
done
wait
count_201=$(grep -l '^201$' "$rate_dir"/code-* | wc -l)
count_429=$(grep -l '^429$' "$rate_dir"/code-* | wc -l)
(( count_201 > 0 && count_429 > 0 && count_201 + count_429 == 20 )) || fail "expected 201+429, got 201=$count_201 429=$count_429"
request GET "$BASE_URL/api/menu" || fail "menu request after rate test failed"
[[ $HTTP_STATUS == 200 ]] || fail "menu was rate limited"
request GET "$BASE_URL/api/queue" || fail "queue request after rate test failed"
[[ $HTTP_STATUS == 200 ]] || fail "queue was rate limited"
pass "20 concurrent POST: 201=$count_201 429=$count_429; menu/queue remain 200"

CURRENT_CHECK=REQ-07
for service in api-v1 api-v2; do
  direct_request "$service" GET /api/menu || fail "$service menu failed"
  [[ $HTTP_STATUS == 200 && $(json_field items.5.code) == cocoa ]] || fail "$service menu contract mismatch"
  direct_request "$service" POST /api/orders "{\"menu_code\":\"americano\",\"qty\":1,\"customer_name\":\"direct-$service\"}" || fail "$service direct POST failed"
  expected_version=${service#api-v}
  [[ $HTTP_STATUS == 201 && $(header_value X-Cafe-Api-Version) == "$expected_version" ]] || fail "$service POST/version contract mismatch"
done
for run in 1 2 3; do
  v2_count=0
  for _ in $(seq 1 200); do
    request GET "$BASE_URL/api/version" || fail "canary request failed"
    [[ $(header_value X-Cafe-Api-Version) == 2 ]] && ((v2_count+=1))
  done
  (( v2_count >= 10 && v2_count <= 30 )) || fail "run $run v2=$v2_count outside [10,30]"
  echo "CHECK REQ-07 RUN-$run PASS: v2=$v2_count/200"
done
pass "v1/v2 parity and three clean 200-request canary runs"

CURRENT_CHECK=REQ-05-KAFKA-RECOVERY
dc restart kafka >/dev/null || fail "Kafka restart failed"
wait_healthy kafka 90 || fail "Kafka did not recover healthy"
wait_analytics_lag_zero 90 || fail "analytics did not catch up after Kafka restart"
before_mocha=$(db_scalar "SELECT cups||':'||revenue FROM sales_stats WHERE menu_code='mocha'")
before_cups=${before_mocha%%:*}
before_revenue=${before_mocha#*:}
post_order mocha 2 fault-kafka || fail "post-restart Kafka order failed"
expected_cups=$((before_cups + 2))
expected_revenue=$(python3 - "$before_revenue" <<'PY'
from decimal import Decimal
import sys
print(f"{Decimal(sys.argv[1])+Decimal('140'):.2f}")
PY
)
wait_db_value "SELECT cups||':'||revenue FROM sales_stats WHERE menu_code='mocha'" "$expected_cups:$expected_revenue" 45 || fail "analytics did not follow Kafka recovery"
pass "Kafka restarted; analytics consumed the next ORDER_PLACED"

CURRENT_CHECK=REQ-05-FIXTURE
topic_desc=$(dc exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 --describe --topic cafe.events) || fail "topic describe failed"
grep -q 'PartitionCount: 3' <<<"$topic_desc" || fail "cafe.events does not have 3 partitions"
wait_analytics_lag_zero 90 || fail "analytics lag was not zero before fixture"
db_scalar "UPDATE sales_stats SET cups=0,revenue=0" >/dev/null || fail "could not reset controlled fixture"
fixture=(latte:1 espresso:2 americano:3 mocha:1 matcha:2 cocoa:3)
for item in "${fixture[@]}"; do
  menu=${item%%:*}; qty=${item#*:}
  post_order "$menu" "$qty" "fixture-$menu" || fail "fixture POST failed for $menu"
  sleep 1
done
expected_rows='latte:1:65.00,espresso:2:110.00,americano:3:150.00,mocha:1:70.00,matcha:2:150.00,cocoa:3:180.00'
wait_db_value "SELECT string_agg(menu_code||':'||cups||':'||revenue,',' ORDER BY CASE menu_code WHEN 'latte' THEN 1 WHEN 'espresso' THEN 2 WHEN 'americano' THEN 3 WHEN 'mocha' THEN 4 WHEN 'matcha' THEN 5 ELSE 6 END) FROM sales_stats" "$expected_rows" 60 || fail "sales_stats fixture was not exact"
request GET "$BASE_URL/api/report/sales" '' manager:manager123 || fail "fixture report failed"
[[ $(json_field totals.cups) == 12 && $(json_field totals.revenue) == 725.0 && $(json_field claim) == trend-level ]] || fail "fixture totals/report claim mismatch"
pass "3 partitions and exact six-menu fixture cups=12 revenue=725.00"

CURRENT_CHECK=REQ-06
before_hash=$(db_scalar "SELECT md5(string_agg(menu_code||':'||cups||':'||revenue,',' ORDER BY menu_code)) FROM sales_stats")
audit_output=$(dc exec -T analytics python audit.py 2>&1) || fail "audit replay exited non-zero"
grep -q 'ORDER_PLACED' <<<"$audit_output" || fail "audit output lacked retained ORDER_PLACED events"
after_hash=$(db_scalar "SELECT md5(string_agg(menu_code||':'||cups||':'||revenue,',' ORDER BY menu_code)) FROM sales_stats")
[[ $before_hash == "$after_hash" ]] || fail "audit modified sales_stats"
pass "earliest replay produced old events and left DB hash unchanged"

CURRENT_CHECK=FINAL
echo "ALL CHECKS PASSED"
echo "SMOKE_EXIT_CODE=0"
exit 0
