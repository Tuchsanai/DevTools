#!/usr/bin/env bash
set -Eeuo pipefail

cd "$(dirname "$0")"
base_url=${BASE_URL:-http://localhost:8000}
tmp_dir=$(mktemp -d /tmp/vcafe-lab2-verify.XXXXXX)
trap 'rm -rf "$tmp_dir"' EXIT

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1" >&2; exit 1; }
status() { curl -sS -o /dev/null -w '%{http_code}' "$@"; }

# Verify source synchronization before exercising runtime behavior.
while IFS= read -r path; do
  [[ -n "$path" ]] || continue
  cmp -s "$path" "../app/$path" || fail "sync manifest mismatch: $path"
done < sync_manifest.txt
pass 'SYNC: every manifest file is byte-identical to app/'

docker compose up -d --build --scale api=3 >/dev/null
deadline=$((SECONDS + 120))
while (( SECONDS < deadline )); do
  unhealthy=$(docker compose ps --format json | grep -vc '"Health":"healthy"' || true)
  running=$(docker compose ps --status running -q | wc -l)
  [[ "$unhealthy" -eq 0 && "$running" -eq 6 ]] && break
  sleep 2
done
[[ $(docker compose ps --status running -q | wc -l) -eq 6 ]] || fail 'LAB2-V01: services did not become healthy within 120s'
provider_ready=0
for _ in $(seq 1 30); do
  server_count=$(curl -fsS http://localhost:8080/api/rawdata 2>/dev/null | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["services"]["api@docker"]["loadBalancer"]["servers"]))' 2>/dev/null || echo 0)
  if [[ "$server_count" -eq 3 ]]; then provider_ready=1; break; fi
  sleep 1
done
[[ "$provider_ready" -eq 1 ]] || fail 'LAB2-V01: Docker provider did not expose 3 servers'

mapfile -t served < <(for _ in $(seq 1 36); do curl -fsS -D - -o /dev/null "$base_url/api/menu" | awk -F': ' 'tolower($1)=="x-served-by"{gsub("\r",""); print $2}'; done | sort -u)
[[ ${#served[@]} -eq 3 ]] || fail "LAB2-V01: expected 3 API hostnames, got ${#served[@]}"
pass "LAB2-V01: scale api=3 distributed requests to ${#served[@]} hostnames (${served[*]})"

mapfile -t api_ids < <(docker compose ps -q api)
target_id=${api_ids[0]}
target_name=$(docker inspect --format '{{.Config.Hostname}}' "$target_id")
target_ip=$(docker inspect --format '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$target_id")
curl -fsS -X POST "http://$target_ip:8000/api/health/fail" >/dev/null
sleep 5
[[ $(docker inspect --format '{{.State.Running}}' "$target_id") == true ]] || fail 'LAB2-V02: failed replica stopped running'
if for _ in $(seq 1 40); do curl -fsS -D - -o /dev/null "$base_url/api/menu"; done | grep -qi "^X-Served-By: $target_name"; then
  fail "LAB2-V02: unhealthy replica $target_name was still served"
fi
curl -fsS -X POST "http://$target_ip:8000/api/health/ok" >/dev/null
restored=0
for _ in $(seq 1 15); do
  sleep 1
  if for _ in $(seq 1 18); do curl -fsS -D - -o /dev/null "$base_url/api/menu"; done | grep -qi "^X-Served-By: $target_name"; then restored=1; break; fi
done
[[ "$restored" -eq 1 ]] || fail "LAB2-V02: replica $target_name did not return"
pass "LAB2-V02: active health withdrew and restored $target_name while container stayed Running"

report_anon=$(status "$base_url/api/report/sales")
report_auth=$(status -u manager:manager123 "$base_url/api/report/sales")
dashboard_anon=$(status "$base_url/dashboard")
dashboard_auth=$(status -u manager:manager123 "$base_url/dashboard")
[[ "$report_anon/$report_auth/$dashboard_anon/$dashboard_auth" == '401/200/401/200' ]] || fail "LAB2-V03: got $report_anon/$report_auth/$dashboard_anon/$dashboard_auth"
pass 'LAB2-V03: report and dashboard enforce manager basicAuth (401 -> 200)'

export tmp_dir base_url
seq 1 20 | xargs -P20 -I{} sh -c \
  'curl -sS -D "$tmp_dir/h-{}" -o "$tmp_dir/b-{}" -w "%{http_code}\n" -X POST "$base_url/api/orders" -H "Content-Type: application/json" -d "{\"menu_code\":\"latte\",\"qty\":1,\"customer_name\":\"rush-{}\"}" > "$tmp_dir/s-{}"'
created=$(grep -l '^201$' "$tmp_dir"/s-* | wc -l)
limited=$(grep -l '^429$' "$tmp_dir"/s-* | wc -l)
[[ "$created" -gt 0 && "$limited" -gt 0 ]] || fail "LAB2-V04: expected mixed 201/429, got 201=$created 429=$limited"
for header in "$tmp_dir"/h-*; do
  grep -q '^HTTP/.* 429' "$header" || continue
  ! grep -qiE '^X-(Served-By|Cafe-Api-Version):' "$header" || fail 'LAB2-V04: gateway 429 leaked application headers'
done
sleep 2
menu_code=$(status "$base_url/api/menu")
queue_code=$(status "$base_url/api/queue")
[[ "$menu_code/$queue_code" == '200/200' ]] || fail "LAB2-V04: menu/queue were limited ($menu_code/$queue_code)"
pass "LAB2-V04: 20 concurrent POST mixed 201=$created and 429=$limited; 429 had no app headers; menu/queue stayed 200"

echo 'ALL CHECKS PASSED'
