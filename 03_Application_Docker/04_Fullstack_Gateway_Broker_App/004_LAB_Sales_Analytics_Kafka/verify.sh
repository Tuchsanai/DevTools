#!/usr/bin/env bash
set -Eeuo pipefail

LAB_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
COMPOSE_FILE="$LAB_DIR/docker-compose.yml"
PROJECT=vcafe-lab004-u5
BASE_URL=http://localhost:8000
TMP_DIR=$(mktemp -d /tmp/vcafe-lab4-verify.XXXXXX)
DC=(docker compose -f "$COMPOSE_FILE" -p "$PROJECT")

cleanup() {
  "${DC[@]}" down -v --remove-orphans >/dev/null 2>&1 || true
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT INT TERM

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1" >&2; exit 1; }
dc() { "${DC[@]}" "$@"; }

health() {
  local cid
  cid=$(dc ps -q "$1")
  [[ -n $cid ]] || return 1
  docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$cid" 2>/dev/null
}

wait_healthy() {
  local service=$1 deadline=$((SECONDS + ${2:-120}))
  until [[ $(health "$service" || true) == healthy ]]; do
    (( SECONDS < deadline )) || fail "$service did not become healthy within 120s"
    sleep 1
  done
}

db_scalar() {
  dc exec -T db psql -U student -d cafedb -Atqc "$1"
}

post_order() {
  local menu=$1 qty=$2 customer=$3 output=$4
  local code
  code=$(curl --noproxy '*' -sS -o "$output" -w '%{http_code}' -X POST "$BASE_URL/api/orders" \
    -H 'Content-Type: application/json' \
    --data "{\"menu_code\":\"$menu\",\"qty\":$qty,\"customer_name\":\"$customer\"}")
  [[ $code == 201 ]] || fail "order $menu returned HTTP $code: $(<"$output")"
}

for command in docker curl python3 grep cmp sha256sum; do
  command -v "$command" >/dev/null 2>&1 || fail "missing command: $command"
done

while IFS= read -r path; do
  [[ -n $path ]] || continue
  cmp -s "$LAB_DIR/$path" "$LAB_DIR/../app/$path" || fail "sync manifest mismatch: $path"
done < "$LAB_DIR/sync_manifest.txt"
pass 'SYNC: every manifest file is byte-identical to app/'

# คืน published ports ของ project สำหรับเรียน แล้วสร้าง verify project ที่ขึ้นต้น vcafe- ตาม namespace กลาง
docker compose -f "$COMPOSE_FILE" down -v --remove-orphans >/dev/null 2>&1 || true
dc down -v --remove-orphans >/dev/null 2>&1 || true
dc up -d kafka >/dev/null
wait_healthy kafka
dc exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 \
  --create --topic cafe.events --partitions 3 --replication-factor 1 >"$TMP_DIR/topic-create"
dc exec -T kafka /opt/kafka/bin/kafka-topics.sh --bootstrap-server kafka:9092 \
  --describe --topic cafe.events >"$TMP_DIR/topic-describe"
grep -q 'PartitionCount: 3' "$TMP_DIR/topic-describe" || fail 'cafe.events does not have 3 partitions'
grep -q 'ReplicationFactor: 1' "$TMP_DIR/topic-describe" || fail 'cafe.events replication factor is not 1'

dc up -d --build >/dev/null
for service in traefik db rabbit kafka api worker analytics web kafka-ui; do wait_healthy "$service"; done

post_order latte 2 verify-latte "$TMP_DIR/latte.json"
post_order mocha 1 verify-mocha "$TMP_DIR/mocha.json"
post_order matcha 3 verify-matcha "$TMP_DIR/matcha.json"
mapfile -t order_ids < <(python3 - "$TMP_DIR" <<'PY'
import json, pathlib, sys
root = pathlib.Path(sys.argv[1])
for name in ("latte", "mocha", "matcha"):
    print(json.loads((root / f"{name}.json").read_text())["id"])
PY
)

deadline=$((SECONDS + 30))
while (( SECONDS < deadline )); do
  stats=$(db_scalar "SELECT count(*)||':'||sum(cups)||':'||sum(revenue)::numeric(12,2) FROM sales_stats")
  ready=$(db_scalar "SELECT count(*) FROM orders WHERE id IN (${order_ids[0]},${order_ids[1]},${order_ids[2]}) AND status='READY'")
  [[ $stats == '6:6:425.00' && $ready == 3 ]] && break
  sleep 1
done

[[ $(db_scalar 'SELECT count(*) FROM sales_stats') == 6 ]] || fail 'LAB4-V01: sales_stats does not contain all 6 seed rows'
expected='americano:0:0.00,cocoa:0:0.00,espresso:0:0.00,latte:2:130.00,matcha:3:225.00,mocha:1:70.00'
actual=$(db_scalar "SELECT string_agg(menu_code||':'||cups||':'||revenue::numeric(12,2),',' ORDER BY menu_code) FROM sales_stats")
[[ $actual == "$expected" ]] || fail "LAB4-V01: sales totals mismatch: $actual"
[[ $(db_scalar "SELECT count(*) FROM orders WHERE id IN (${order_ids[0]},${order_ids[1]},${order_ids[2]}) AND status='READY'") == 3 ]] || fail 'LAB4-V01: fixture orders did not become READY within 30s'
pass 'LAB4-V01: ORDER_PLACED updated exactly 6 cups / 425.00 across all 6 seeded menu rows'

before=$(db_scalar "SELECT md5(string_agg(menu_code||':'||cups||':'||revenue::numeric(12,2),',' ORDER BY menu_code)) FROM sales_stats")
dc exec -T analytics python audit.py >"$TMP_DIR/audit.log"
after=$(db_scalar "SELECT md5(string_agg(menu_code||':'||cups||':'||revenue::numeric(12,2),',' ORDER BY menu_code)) FROM sales_stats")
[[ $before == "$after" ]] || fail 'LAB4-V02: audit changed sales_stats'
grep -q 'ORDER_PLACED=3' "$TMP_DIR/audit.log" || fail 'LAB4-V02: audit did not replay 3 ORDER_PLACED events'
grep -q 'ORDER_READY=3' "$TMP_DIR/audit.log" || fail 'LAB4-V02: audit did not replay 3 ORDER_READY events'
grep -Eq 'p0 .* ORDER_PLACED .* mocha' "$TMP_DIR/audit.log" || fail 'LAB4-V02: mocha was not observed on partition 0'
grep -Eq 'p1 .* ORDER_PLACED .* matcha' "$TMP_DIR/audit.log" || fail 'LAB4-V02: matcha was not observed on partition 1'
grep -Eq 'p2 .* ORDER_PLACED .* latte' "$TMP_DIR/audit.log" || fail 'LAB4-V02: latte was not observed on partition 2'
pass 'LAB4-V02: audit replayed earliest history on partitions 0/1/2 and left the database hash unchanged'

echo 'ALL CHECKS PASSED'
echo 'VERIFY_EXIT_CODE=0'
