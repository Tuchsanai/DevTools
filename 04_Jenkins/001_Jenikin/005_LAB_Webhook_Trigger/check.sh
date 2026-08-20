#!/usr/bin/env bash
set -uo pipefail

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
GITEA_URL="${GITEA_URL:-http://localhost:3000}"
JENKINS_AUTH='admin:admin2569'
GITEA_AUTH='student:student2569'
JOB='hello-ci-pipeline'
TOKEN='cicd2569-hello'
HOOK_URL="http://jenkins:8080/generic-webhook-trigger/invoke?token=$TOKEN"
failures=0
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

plugin_json="$tmp_dir/plugins.json"
if curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/pluginManager/api/json?depth=1" \
    -o "$plugin_json" 2>/dev/null \
  && python3 - "$plugin_json" <<'PY'
import json, sys
plugins = json.load(open(sys.argv[1], encoding="utf-8")).get("plugins", [])
ok = any(p.get("shortName") == "generic-webhook-trigger"
         and p.get("version") == "2.4.2" and p.get("active") is True
         for p in plugins)
raise SystemExit(0 if ok else 1)
PY
then
  pass 'Generic Webhook Trigger 2.4.2 ติดตั้งและ active'
else
  fail 'ไม่พบ Generic Webhook Trigger 2.4.2 ที่ active'
fi

config_xml="$tmp_dir/config.xml"
if curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/config.xml" \
    -o "$config_xml" 2>/dev/null; then
  if grep -q 'org.jenkinsci.plugins.gwt.GenericTrigger' "$config_xml" \
    && grep -q "<token>$TOKEN</token>" "$config_xml"; then
    pass "job $JOB ใช้ GenericTrigger token แยกต่อ job ถูกต้อง"
  else
    fail "job $JOB ไม่มี GenericTrigger หรือ token ไม่ตรง"
  fi
  if grep -q '<hudson.triggers.SCMTrigger>' "$config_xml"; then
    fail "job $JOB ยังเปิด Poll SCM"
  else
    pass "job $JOB ปิด Poll SCM แล้ว"
  fi
else
  fail "อ่าน config.xml ของ job $JOB ไม่ได้"
fi

hooks_json="$tmp_dir/hooks.json"
if curl -fsS -u "$GITEA_AUTH" \
    "$GITEA_URL/api/v1/repos/student/hello-ci/hooks" -o "$hooks_json" 2>/dev/null \
  && python3 - "$hooks_json" "$HOOK_URL" <<'PY'
import json, sys
hooks = json.load(open(sys.argv[1], encoding="utf-8"))
url = sys.argv[2]
ok = any(hook.get("type") == "gitea"
         and hook.get("active") is True
         and "push" in hook.get("events", [])
         and hook.get("config", {}).get("url") == url
         and hook.get("config", {}).get("content_type") == "json"
         for hook in hooks)
raise SystemExit(0 if ok else 1)
PY
then
  pass 'Gitea มี active push webhook ไป canonical Jenkins URL'
else
  fail 'ไม่พบ active push webhook ที่ URL/content type ถูกต้อง'
fi

build_json="$tmp_dir/build.json"
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/$JOB/lastBuild/api/json?tree=number,building,result,actions[causes[shortDescription]]" \
    -o "$build_json" 2>/dev/null; then
  read -r build_number build_result building webhook_cause < <(python3 - "$build_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
causes = [c for action in d.get("actions", []) for c in action.get("causes", [])]
is_webhook = any(
    c.get("_class", "").endswith(".GenericCause")
    or "generic" in c.get("shortDescription", "").lower()
    or "gitea push" in c.get("shortDescription", "").lower()
    for c in causes
)
print(d.get("number", ""), d.get("result", ""),
      str(d.get("building", True)).lower(),
      "yes" if is_webhook else "no")
PY
  )
  if [ -n "$build_number" ] && [ "$building" = 'false' ] \
    && [ "$build_result" = 'SUCCESS' ]; then
    pass "build ล่าสุด #$build_number = SUCCESS"
  else
    fail "build ล่าสุดยังไม่จบ SUCCESS"
  fi
  if [ "$webhook_cause" = 'yes' ]; then
    pass "build ล่าสุด #$build_number มี cause จาก Generic Webhook Trigger"
  else
    fail "build ล่าสุดไม่มี cause จาก Generic Webhook Trigger"
  fi
else
  fail "อ่าน build ล่าสุดของ $JOB ไม่ได้"
fi

if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS — LAB 5 พร้อมใช้งาน\n'
  exit 0
fi

printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
