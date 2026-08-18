#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")"
base_url=${BASE_URL:-http://localhost:8000}
tmp_dir=$(mktemp -d /tmp/vcafe-lab5-check.XXXXXX)
trap 'rm -rf "$tmp_dir"' EXIT

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1" >&2; exit 1; }

clean_oracle() {
  local dirty=0
  for kind in container network volume; do
    case "$kind" in
      container) ids=$(docker ps -aq --filter label=com.docker.compose.project=lab005) ;;
      network) ids=$(docker network ls -q --filter label=com.docker.compose.project=lab005) ;;
      volume) ids=$(docker volume ls -q --filter label=com.docker.compose.project=lab005) ;;
    esac
    [[ -z "$ids" ]] || { printf '[DIRTY] lab005 %s: %s\n' "$kind" "$ids" >&2; dirty=1; }
  done
  leftovers=$(docker ps -a --format '{{.Names}}' | grep -E '^(vcafe-|devtools-cafe)' || true)
  [[ -z "$leftovers" ]] || { printf '[DIRTY] reserved names:\n%s\n' "$leftovers" >&2; dirty=1; }
  [[ $dirty -eq 0 ]] || fail 'INT-CLEAN-01: namespace is not clean'
  pass 'INT-CLEAN-01: lab005 and vcafe namespaces are clean'
}

if [[ ${1:-} == --clean-only ]]; then
  clean_oracle
  echo 'ALL CHECKS PASSED'
  exit 0
fi

request() {
  local method=$1 url=$2 data=${3:-} auth=${4:-}
  local -a args=(--noproxy '*' -sS -D "$tmp_dir/headers" -o "$tmp_dir/body" -w '%{http_code}' -X "$method")
  [[ -n $data ]] && args+=(-H 'Content-Type: application/json' --data "$data")
  [[ -n $auth ]] && args+=(-u "$auth")
  http_status=$(curl "${args[@]}" "$url")
}

header() {
  awk -v key="$1" 'BEGIN{key=tolower(key)":"} {line=$0;if(index(tolower(line),key)==1){sub(/^[^:]*:[[:space:]]*/,"",line);sub(/\r$/, "",line);v=line}} END{print v}' "$tmp_dir/headers"
}

field() {
  python3 - "$1" "$tmp_dir/body" <<'PY'
import json, pathlib, sys
value=json.loads(pathlib.Path(sys.argv[2]).read_text())
for part in sys.argv[1].split('.'):
    value=value[int(part)] if isinstance(value,list) else value[part]
print(value)
PY
}

db_scalar() {
  docker compose exec -T db psql -U student -d cafedb -Atqc "$1"
}

direct() {
  local service=$1 method=$2 path=$3 data=${4:-} cid ip
  cid=$(docker compose ps -q "$service")
  ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$cid")
  request "$method" "http://$ip:8000$path" "$data"
}

post_order() {
  local menu=$1 qty=$2 customer=$3
  for _ in $(seq 1 12); do
    request POST "$base_url/api/orders" "{\"menu_code\":\"$menu\",\"qty\":$qty,\"customer_name\":\"$customer\"}"
    if [[ $http_status == 201 ]]; then order_id=$(field id); return 0; fi
    [[ $http_status == 429 ]] || return 1
    sleep 1
  done
  return 1
}

while IFS= read -r path; do
  [[ -n $path ]] || continue
  cmp -s "$path" "../app/$path" || fail "SYNC: mismatch $path"
done < sync_manifest.txt
pass 'SYNC: manifest files are byte-identical to app/'

services=(traefik db rabbit kafka api-v1 api-v2 worker analytics web kafka-ui)
deadline=$((SECONDS + 120))
for service in "${services[@]}"; do
  while :; do
    cid=$(docker compose ps -q "$service")
    health=$([[ -n $cid ]] && docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$cid" 2>/dev/null || true)
    [[ $health == healthy ]] && break
    (( SECONDS < deadline )) || fail "INT-READY-01: $service not healthy within 120s"
    sleep 2
  done
done
for service in db api-v1 api-v2 worker analytics; do
  [[ -z $(docker port "$(docker compose ps -q "$service")" 2>/dev/null) ]] || fail "INT-READY-01: $service publishes a host port"
done
pass 'INT-READY-01: 10 services healthy; DB/API/workers publish no host ports'

request GET "$base_url/api/menu"
[[ $http_status == 200 && $(field items.0.code) == latte && $(field items.5.code) == cocoa ]] || fail 'INT-API-01: menu contract mismatch'
request GET "$base_url/api/queue"
[[ $http_status == 200 ]] || fail "INT-API-01: queue HTTP $http_status"
request GET "$base_url/api/orders/999999999"
[[ $http_status == 404 && $(field code) == ORDER_NOT_FOUND ]] || fail 'INT-API-01: order 404 mismatch'
request GET "$base_url/api/report/sales"
[[ $http_status == 401 ]] || fail 'INT-API-01: anonymous report was not 401'
request GET "$base_url/api/report/sales" '' manager:manager123
[[ $http_status == 200 && $(field items.5.menu_code) == cocoa && $(field claim) == trend-level ]] || fail 'INT-API-01: authenticated report mismatch'
pass 'INT-API-01: menu/queue/order/report schemas and basicAuth pass'

request GET "$base_url/api/menu"
[[ -n $(header X-Served-By) && $(header X-Cafe-Api-Version) =~ ^[12]$ ]] || fail 'INT-HEADERS-01: success headers missing'
request POST "$base_url/api/orders" '{"menu_code":"latte","qty":4,"customer_name":"bad"}'
[[ $http_status == 422 && $(field code) == VALIDATION_ERROR && -n $(header X-Served-By) && $(header X-Cafe-Api-Version) =~ ^[12]$ ]] || fail 'INT-HEADERS-01: 422 headers/body mismatch'
direct api-v1 POST /api/health/fail
direct api-v1 GET /api/health
[[ $http_status == 503 && $(field code) == HEALTH_FORCED && $(header X-Cafe-Api-Version) == 1 && -n $(header X-Served-By) ]] || fail 'INT-HEADERS-01: application 503 headers/body mismatch'
direct api-v1 POST /api/health/ok
sleep 5
request GET "$base_url/api/report/sales"
[[ $http_status == 401 && -z $(header X-Served-By) && -z $(header X-Cafe-Api-Version) ]] || fail 'INT-HEADERS-01: gateway 401 leaked application headers'
pass 'INT-HEADERS-01: success/422/503 have app headers; gateway 401 does not'

grep -q 'weight: 9' dynamic/routes.yml && grep -q 'weight: 1' dynamic/routes.yml || fail 'INT-CANARY-01: routes.yml is not 9:1'
for service in api-v1 api-v2; do
  direct "$service" GET /api/menu
  expected=${service#api-v}
  [[ $http_status == 200 && $(field items.5.code) == cocoa && $(header X-Cafe-Api-Version) == "$expected" ]] || fail "INT-CANARY-01: $service contract mismatch"
done
for run in 1 2 3; do
  v2=0
  for _ in $(seq 1 200); do
    request GET "$base_url/api/version"
    [[ $(header X-Cafe-Api-Version) == 2 ]] && ((v2+=1))
  done
  (( v2 >= 10 && v2 <= 30 )) || fail "INT-CANARY-01: run $run v2=$v2 outside [10,30]"
  printf '[PASS] INT-CANARY-01 run %d: v2=%d/200\n' "$run" "$v2"
done
pass 'INT-CANARY-01: v1/v2 parity and 90:10 tolerance passed 3 clean runs'

before=$(db_scalar "SELECT cups FROM sales_stats WHERE menu_code='matcha'")
start=$(date +%s)
post_order matcha 2 capstone-e2e || fail "INT-E2E-01: order rejected HTTP $http_status"
while :; do
  state=$(db_scalar "SELECT status FROM orders WHERE id=$order_id")
  cups=$(db_scalar "SELECT cups FROM sales_stats WHERE menu_code='matcha'")
  [[ $state == READY && $cups -ge $((before + 2)) ]] && break
  (( $(date +%s) - start <= 30 )) || fail "INT-E2E-01: order $order_id not READY with analytics within 30s"
  sleep 1
done
elapsed=$(( $(date +%s) - start ))
pass "INT-E2E-01: order $order_id crossed Traefik→RabbitMQ→worker→Kafka→analytics in ${elapsed}s"

leftovers=$(docker ps -a --format '{{.Names}}' | grep '^vcafe-' || true)
[[ -z $leftovers ]] || fail "INT-CLEAN-01: vcafe leftovers: $leftovers"
pass 'INT-CLEAN-01: no vcafe-* temporary resources leaked during acceptance'

echo 'ALL CHECKS PASSED'
