#!/usr/bin/env bash

set -u

BASE_URL="${BASE_URL:-http://localhost:8000}"
AUTH="student:student123"
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
RESET='\033[0m'
PASS_COUNT=0
FAIL_COUNT=0

pass() {
  PASS_COUNT=$((PASS_COUNT + 1))
  printf "${GREEN}PASS${RESET}  %s\n" "$1"
}

fail() {
  FAIL_COUNT=$((FAIL_COUNT + 1))
  printf "${RED}FAIL${RESET}  %s\n" "$1"
}

printf "${CYAN}LAB005 acceptance check${RESET}  %s\n\n" "$BASE_URL"

tmp_body="$(mktemp)"
trap 'rm -f "$tmp_body"' EXIT

root_code="$(curl --max-time 4 -sS -o "$tmp_body" -w '%{http_code}' "$BASE_URL/" 2>/dev/null || true)"
if [[ "$root_code" == "200" ]] && grep -q "DevTools Mini Shop" "$tmp_body"; then
  pass "AC1  GET / returns the shop-ui (HTTP 200)"
else
  fail "AC1  GET / expected shop-ui HTTP 200, got HTTP $root_code"
fi

no_auth_code="$(curl --max-time 4 -sS -o /dev/null -w '%{http_code}' "$BASE_URL/api/users" 2>/dev/null || true)"
with_auth_code="$(curl --max-time 4 -sS -u "$AUTH" -o /dev/null -w '%{http_code}' "$BASE_URL/api/users" 2>/dev/null || true)"
if [[ "$no_auth_code" == "401" && "$with_auth_code" == "200" ]]; then
  pass "AC2  /api/users requires basicAuth (401 -> 200)"
else
  fail "AC2  /api/users expected 401 -> 200, got $no_auth_code -> $with_auth_code"
fi

declare -A HOSTS=()
orders_ok=1
for request_no in {1..12}; do
  response="$(curl --max-time 4 -fsS "$BASE_URL/api/orders?check=$request_no" 2>/dev/null || true)"
  hostname="$(printf '%s' "$response" | sed -n 's/.*"hostname":"\([^"]*\)".*/\1/p')"
  if [[ -n "$hostname" ]]; then
    HOSTS["$hostname"]=1
  else
    orders_ok=0
  fi
done
if [[ "$orders_ok" -eq 1 && "${#HOSTS[@]}" -ge 2 ]]; then
  pass "AC3  /api/orders reached ${#HOSTS[@]} hostnames in 12 requests: ${!HOSTS[*]}"
else
  fail "AC3  /api/orders expected >=2 hostnames, found ${#HOSTS[@]}"
fi

sleep 2
rate_limited=0
for request_no in {1..10}; do
  code="$(curl --max-time 4 -sS -u "$AUTH" -o /dev/null -w '%{http_code}' "$BASE_URL/api/users?burst=$request_no" 2>/dev/null || true)"
  if [[ "$code" == "429" ]]; then
    rate_limited=$((rate_limited + 1))
  fi
done
if [[ "$rate_limited" -ge 1 ]]; then
  pass "AC4  /api/users returned HTTP 429 ($rate_limited of 10 requests)"
else
  fail "AC4  /api/users expected at least one HTTP 429, found 0 of 10"
fi

printf '\nResult: %d PASS, %d FAIL\n' "$PASS_COUNT" "$FAIL_COUNT"
[[ "$FAIL_COUNT" -eq 0 ]]
