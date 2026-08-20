#!/usr/bin/env bash

# LAB 1 acceptance check: run this file from inside the devtools container.
set -u

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_USER="${JENKINS_USER:-admin}"
JENKINS_PASSWORD="${JENKINS_PASSWORD:-admin2569}"
failures=0

pass() {
  printf 'PASS: %s\n' "$1"
}

fail() {
  printf 'FAIL: %s\n' "$1" >&2
  failures=$((failures + 1))
}

if [ "$(docker inspect -f '{{.State.Running}}' jenkins 2>/dev/null || true)" = "true" ]; then
  pass "container jenkins is Up"
else
  fail "container jenkins is not Up"
fi

if docker volume inspect jenkins_home >/dev/null 2>&1; then
  pass "volume jenkins_home exists"
else
  fail "volume jenkins_home is missing"
fi

job_json="$(curl -fsS -u "${JENKINS_USER}:${JENKINS_PASSWORD}" \
  "${JENKINS_URL}/job/first-freestyle/api/json?tree=name" 2>/dev/null || true)"
if printf '%s' "$job_json" | grep -q '"name":"first-freestyle"'; then
  pass "job first-freestyle exists"
else
  fail "job first-freestyle is missing or Jenkins API login failed"
fi

build_json="$(curl -fsS -u "${JENKINS_USER}:${JENKINS_PASSWORD}" \
  "${JENKINS_URL}/job/first-freestyle/lastBuild/api/json?tree=number,result" 2>/dev/null || true)"
if printf '%s' "$build_json" | grep -q '"result":"SUCCESS"'; then
  build_number="$(printf '%s' "$build_json" | sed -n 's/.*"number":\([0-9][0-9]*\).*/\1/p')"
  pass "latest build #${build_number} is SUCCESS"
else
  fail "latest build is not SUCCESS"
fi

if [ "$failures" -eq 0 ]; then
  printf 'LAB 1 CHECK: PASS\n'
  exit 0
fi

printf 'LAB 1 CHECK: FAIL (%d problem(s))\n' "$failures" >&2
exit 1
