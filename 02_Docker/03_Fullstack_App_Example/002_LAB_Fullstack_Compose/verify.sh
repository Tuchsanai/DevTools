#!/usr/bin/env bash
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="skillspace-lab002-verify"
PORT="13252"
FAILED=0

dc() {
  docker compose -p "$PROJECT" -f "$ROOT/compose.yaml" "$@"
}

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; FAILED=$((FAILED + 1)); }
check() {
  local label="$1"
  shift
  if "$@"; then pass "$label"; else fail "$label"; fi
}

cleanup() {
  WEB_PORT="$PORT" dc down -v --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT

cd "$ROOT"
cleanup

check "compose.yaml syntax is valid" env WEB_PORT="$PORT" docker compose -p "$PROJECT" config -q

services="$(docker compose config --services | sort | tr '\n' ' ')"
[ "$services" = "api db web " ] && pass "services are api, db and web" || fail "services are api, db and web"

if docker compose config | sed -n '/^  db:/,/^  [a-z]/p' | grep -q 'published:'; then
  fail "db has no published port"
else
  pass "db has no published port"
fi

if docker compose config | sed -n '/^  api:/,/^  [a-z]/p' | grep -q 'published:'; then
  fail "api has no published port"
else
  pass "api has no published port"
fi

WEB_PORT="$PORT" dc up -d --build

for _ in $(seq 1 90); do
  states="$(WEB_PORT="$PORT" dc ps --format json 2>/dev/null || true)"
  healthy="$(printf '%s' "$states" | grep -o '"Health":"healthy"' | wc -l | tr -d ' ')"
  [ "$healthy" = "3" ] && break
  sleep 2
done

states="$(WEB_PORT="$PORT" dc ps --format json)"
healthy="$(printf '%s' "$states" | grep -o '"Health":"healthy"' | wc -l | tr -d ' ')"
[ "$healthy" = "3" ] && pass "db, api and web are healthy" || fail "db, api and web are healthy"

check "web page returns HTTP 200" dc exec -T web wget -q -O /dev/null http://127.0.0.1:3000/
check "tickets page returns HTTP 200" dc exec -T web wget -q -O /dev/null http://127.0.0.1:3000/tickets
check "loans page returns HTTP 200" dc exec -T web wget -q -O /dev/null http://127.0.0.1:3000/loans
check "parts page returns HTTP 200" dc exec -T web wget -q -O /dev/null http://127.0.0.1:3000/parts

health="$(WEB_PORT="$PORT" dc exec -T web wget -qO- http://api:8000/health)"
printf '%s' "$health" | grep -q '"status":"ok"' && pass "web reaches api by service name" || fail "web reaches api by service name"

dbhost="$(WEB_PORT="$PORT" dc exec -T api python -c "import socket; print(socket.gethostbyname('db'))")"
[ -n "$dbhost" ] && pass "api resolves db by service name" || fail "api resolves db by service name"

before="$(WEB_PORT="$PORT" dc exec -T db psql -U opsuser -d skillspace -Atc 'select count(*) from tickets;')"
WEB_PORT="$PORT" dc exec -T db psql -U opsuser -d skillspace -c "insert into tickets(asset_id,title,detail,priority,status) values (3,'verify persistence','LAB 002','HIGH','NEW');" >/dev/null
WEB_PORT="$PORT" dc down >/dev/null
WEB_PORT="$PORT" dc up -d >/dev/null
for _ in $(seq 1 60); do
  after="$(WEB_PORT="$PORT" dc exec -T db psql -U opsuser -d skillspace -Atc 'select count(*) from tickets;' 2>/dev/null || true)"
  [ "$after" = "$((before + 1))" ] && break
  sleep 2
done
[ "${after:-}" = "$((before + 1))" ] && pass "ticket survives compose down and up" || fail "ticket survives compose down and up"

WEB_PORT="$PORT" dc down -v >/dev/null
WEB_PORT="$PORT" dc up -d >/dev/null
for _ in $(seq 1 60); do
  reset="$(WEB_PORT="$PORT" dc exec -T db psql -U opsuser -d skillspace -Atc 'select count(*) from tickets;' 2>/dev/null || true)"
  [ "$reset" = "$before" ] && break
  sleep 2
done
[ "${reset:-}" = "$before" ] && pass "down -v resets database to seed" || fail "down -v resets database to seed"

if [ "$FAILED" -eq 0 ]; then
  echo "ALL CHECKS PASSED"
else
  echo "$FAILED CHECK(S) FAILED"
  exit 1
fi
