#!/usr/bin/env bash
set -euo pipefail

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH="${JENKINS_AUTH:-admin:admin2569}"
JOB_NAME='first-pipeline'

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

job_json="$(curl -gfsS -u "$JENKINS_AUTH" \
  "$JENKINS_URL/job/$JOB_NAME/api/json?tree=name,lastBuild[number,building,result]")" \
  || fail "ไม่พบ job $JOB_NAME ที่ $JENKINS_URL"

build_number="$(printf '%s' "$job_json" | python3 -c \
  'import json,sys; d=json.load(sys.stdin); b=d.get("lastBuild") or {}; print(b.get("number", ""))')"
build_result="$(printf '%s' "$job_json" | python3 -c \
  'import json,sys; d=json.load(sys.stdin); b=d.get("lastBuild") or {}; print(b.get("result", ""))')"
building="$(printf '%s' "$job_json" | python3 -c \
  'import json,sys; d=json.load(sys.stdin); b=d.get("lastBuild") or {}; print(str(b.get("building", True)).lower())')"

[ -n "$build_number" ] || fail 'job ยังไม่มี build'
[ "$building" = 'false' ] || fail "build #$build_number ยังทำงานอยู่"
[ "$build_result" = 'SUCCESS' ] || fail "build #$build_number มีผลเป็น $build_result"

# LAB 1's frozen suggested-plugin set includes pipeline-graph-view but not the
# Pipeline REST API plugin. Therefore this check uses the real /stages/tree
# endpoint from the installed pipeline-graph-view plugin.
graph_json="$(curl -gfsS -u "$JENKINS_AUTH" \
  "$JENKINS_URL/job/$JOB_NAME/$build_number/stages/tree")" \
  || fail "อ่าน stage ของ build #$build_number ผ่าน Pipeline Graph API ไม่ได้"

stage_summary="$(printf '%s' "$graph_json" | python3 -c '
import json, sys
data = json.load(sys.stdin).get("data", {})
required = ["Checkout", "Build", "Test", "Deploy"]
actual = {stage.get("name"): str(stage.get("state", "")).upper()
          for stage in data.get("stages", [])}
missing = [name for name in required if name not in actual]
not_green = [f"{name}={actual.get(name)}" for name in required if actual.get(name) != "SUCCESS"]
if missing or not_green:
    print("missing=" + ",".join(missing) + "; statuses=" + ",".join(not_green), file=sys.stderr)
    raise SystemExit(1)
print(", ".join(f"{name}={actual[name]}" for name in required))
')" || fail "stage ไม่ครบหรือไม่ได้ SUCCESS ทั้งหมด"

printf 'PASS: job=%s build=#%s result=%s\n' "$JOB_NAME" "$build_number" "$build_result"
printf 'PASS: stages: %s\n' "$stage_summary"
