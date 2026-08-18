#!/usr/bin/env bash
set -u -o pipefail

LAB_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
COMPOSE_FILE="$LAB_DIR/docker-compose.yml"
PROJECT=vcafe-lab001-u2
BASE_URL=http://localhost:8000
TMP_DIR=$(mktemp -d)
CURRENT_CHECK=BOOTSTRAP
DC=(docker compose -f "$COMPOSE_FILE" -p "$PROJECT")

cleanup() {
  "${DC[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT INT TERM

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
  local cid
  cid=$(service_cid "$1")
  [[ -n $cid ]] || return 1
  docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$cid" 2>/dev/null
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

wait_all() {
  local service
  for service in traefik db api web; do
    wait_healthy "$service" 120 || fail "$service did not become healthy within 120s"
  done
}

request() {
  local method=$1 path=$2 data=${3:-}
  local -a args=(--noproxy '*' -sS -D "$TMP_DIR/headers" -o "$TMP_DIR/body" -w '%{http_code}' -X "$method")
  [[ -n $data ]] && args+=(-H 'Content-Type: application/json' --data "$data")
  HTTP_STATUS=$(curl "${args[@]}" "$BASE_URL$path") || return 1
  HTTP_BODY=$(<"$TMP_DIR/body")
}

header_value() {
  local name=$1
  awk -v key="$name" 'BEGIN{key=tolower(key) ":"} {line=$0; if(index(tolower(line),key)==1){sub(/^[^:]*:[[:space:]]*/,"",line); sub(/\r$/, "", line); value=line}} END{print value}' "$TMP_DIR/headers"
}

json_assert() {
  local expression=$1
  python3 - "$TMP_DIR/body" "$expression" <<'PY'
import json, pathlib, sys
data = json.loads(pathlib.Path(sys.argv[1]).read_text())
assert eval(sys.argv[2], {"__builtins__": {"len": len}}, {"data": data})
PY
}

db_scalar() {
  dc exec -T db psql -U student -d cafedb -Atqc "$1"
}

CURRENT_CHECK=BOOTSTRAP
for cmd in docker curl python3 awk grep sort; do require "$cmd"; done
[[ -f $COMPOSE_FILE ]] || fail "docker-compose.yml not found"

# คืนพอร์ตของ LAB1 ก่อน แล้วใช้ project ชั่วคราวที่ขึ้นต้น vcafe- ตาม namespace กลาง
docker compose -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
dc down -v --remove-orphans >/dev/null 2>&1 || true
dc up -d --build || fail "compose up failed"
wait_all

CURRENT_CHECK=LAB1-V01
request GET / || fail "front door web request failed"
[[ $HTTP_STATUS == 200 ]] || fail "web returned HTTP $HTTP_STATUS"
request GET /api/menu || fail "front door API request failed"
[[ $HTTP_STATUS == 200 ]] || fail "menu returned HTTP $HTTP_STATUS"
sleep 1
dc logs --no-color traefik 2>&1 | grep -q 'GET /api/menu' || fail "Traefik access log lacks /api/menu"
for service in db api web; do
  [[ -z $(docker port "$(service_cid "$service")" 2>/dev/null) ]] || fail "$service publishes a host port"
done
pass "single front door works, access log records /api/menu, backend ports stay private"

CURRENT_CHECK=LAB1-V02
request POST /api/orders '{"menu_code":"latte","qty":2,"customer_name":"verify-u2"}' || fail "valid order request failed"
[[ $HTTP_STATUS == 201 ]] || fail "valid order returned HTTP $HTTP_STATUS: $HTTP_BODY"
json_assert 'data["status"] == "QUEUED" and data["qty"] == 2 and data["ready_at"] is None' || fail "valid order schema/status mismatch"
ORDER_ID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["id"])' "$TMP_DIR/body")
request POST /api/orders '{"menu_code":"unknown","qty":1,"customer_name":"bad-menu"}' || fail "unknown menu request failed"
[[ $HTTP_STATUS == 404 ]] && json_assert 'data["code"] == "MENU_NOT_FOUND"' || fail "unknown menu contract mismatch"
request POST /api/orders '{"menu_code":"latte","qty":4,"customer_name":"bad-qty"}' || fail "invalid qty request failed"
[[ $HTTP_STATUS == 422 ]] && json_assert 'data["code"] == "VALIDATION_ERROR"' || fail "qty validation contract mismatch"
[[ $(db_scalar "SELECT status FROM orders WHERE id=$ORDER_ID") == QUEUED ]] || fail "database status is not QUEUED"
pass "valid order is 201/QUEUED; invalid menu and qty return canonical 404/422"

CURRENT_CHECK=LAB1-V03
request GET /api/menu || fail "menu request failed"
[[ $HTTP_STATUS == 200 ]] && json_assert 'len(data["items"]) == 6 and data["items"][0]["code"] == "latte"' || fail "menu contract mismatch"
[[ -n $(header_value X-Served-By) && $(header_value X-Cafe-Api-Version) == 1 ]] || fail "success headers missing"
request GET /api/queue || fail "queue request failed"
[[ $HTTP_STATUS == 200 ]] && json_assert 'data["count"] == len(data["items"]) and data["items"][0]["status"] == "QUEUED"' || fail "queue contract mismatch"
request GET "/api/orders/$ORDER_ID" || fail "order detail request failed"
[[ $HTTP_STATUS == 200 ]] && json_assert 'data["id"] > 0 and data["status"] == "QUEUED"' || fail "order detail contract mismatch"
request GET /api/orders/999999999 || fail "unknown order request failed"
[[ $HTTP_STATUS == 404 ]] && json_assert 'data["code"] == "ORDER_NOT_FOUND"' || fail "unknown order contract mismatch"
[[ -n $(header_value X-Served-By) && $(header_value X-Cafe-Api-Version) == 1 ]] || fail "404 application headers missing"
request GET /api/version || fail "version request failed"
[[ $HTTP_STATUS == 200 ]] && json_assert 'data == {"version":"1", "tagline":"ชงใจทุกแก้ว"}' || fail "version contract mismatch"
pass "menu/queue/order/version schemas and application headers match the contract"

CURRENT_CHECK=LAB1-V04
for service in db api web; do
  [[ -z $(docker port "$(service_cid "$service")" 2>/dev/null) ]] || fail "$service unexpectedly publishes a port"
done
traefik_ports=$(docker port "$(service_cid traefik)")
grep -q ':8000$' <<<"$traefik_ports" || fail "Traefik web port 8000 is missing"
grep -q ':8080$' <<<"$traefik_ports" || fail "Traefik dashboard port 8080 is missing"
[[ $(grep -Ec -- '->' <<<"$traefik_ports") -eq 4 ]] || fail "Traefik has an unexpected published mapping"
pass "published-port allowlist is exactly Traefik 8000/8080"

CURRENT_CHECK=LAB1-V05
before=$(db_scalar 'SELECT count(*) FROM orders')
(( before >= 1 )) || fail "fixture order missing before volume test"
dc down || fail "compose down failed"
dc up -d || fail "compose up after down failed"
wait_all
after_down=$(db_scalar 'SELECT count(*) FROM orders')
[[ $after_down == "$before" ]] || fail "down lost order rows: before=$before after=$after_down"
dc down -v || fail "compose down -v failed"
dc up -d || fail "compose up after down -v failed"
wait_all
after_reset=$(db_scalar 'SELECT count(*) FROM orders')
menus_after_reset=$(db_scalar 'SELECT count(*) FROM menus')
[[ $after_reset == 0 && $menus_after_reset == 6 ]] || fail "volume reset mismatch: orders=$after_reset menus=$menus_after_reset"
pass "down preserved $before order(s); down -v reset orders to 0 and reseeded 6 menus"

CURRENT_CHECK=LAB1-V06
services=$(dc config --services | sort | tr '\n' ' ')
[[ $services == 'api db traefik web ' ]] || fail "unexpected service subset: $services"
api_env=$(docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' "$(service_cid api)")
grep -q '^ORDER_TRANSPORT=db-only$' <<<"$api_env" || fail "ORDER_TRANSPORT is not db-only"
grep -q '^EVENTS_ENABLED=0$' <<<"$api_env" || fail "EVENTS_ENABLED is not 0"
! grep -Eq '^(RABBIT_URL|KAFKA_BOOTSTRAP)=' <<<"$api_env" || fail "disabled broker URL leaked into API env"
dc exec -T api python -c "import main,sys; assert 'pika' not in sys.modules and 'kafka' not in sys.modules" || fail "disabled broker client was imported"
request POST /api/orders '{"menu_code":"cocoa","qty":1,"customer_name":"no-broker"}' || fail "db-only order request failed"
[[ $HTTP_STATUS == 201 ]] || fail "db-only API returned HTTP $HTTP_STATUS"
pass "API is healthy and accepts 201 without RabbitMQ/Kafka services, URLs, or imports"

CURRENT_CHECK=FINAL
echo "ALL CHECKS PASSED"
echo "VERIFY_EXIT_CODE=0"
