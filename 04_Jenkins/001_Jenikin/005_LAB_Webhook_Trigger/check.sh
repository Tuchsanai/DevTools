#!/usr/bin/env bash
set -uo pipefail

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH='admin:admin2569'
GITHUB_API='https://api.github.com'
JOB='hello-ci-pipeline'
TOKEN='cicd2569-hello'
RELAY='smee-hello'
TARGET="http://jenkins:8080/generic-webhook-trigger/invoke?token=$TOKEN"
RELAY_IMAGE='deltaprojects/smee-client@sha256:20ea24c8c81bb3f3aa332c8939503e3c5bee048bb5a98ba2249d73a41a556e33'
failures=0
GH_API_REQUEST_COUNT=0
GH_API_STATUS=''
GH_API_RETRY_AFTER=''

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

finish_early() {
  fail "$1"
  printf '[INFO] GitHub API requests ใน run นี้: %d\n' "$GH_API_REQUEST_COUNT"
  printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
  exit 1
}

if [ -z "${GITHUB_USER:-}" ] || [ -z "${GITHUB_TOKEN:-}" ]; then
  finish_early 'ต้องกำหนด GITHUB_USER และ GITHUB_TOKEN ก่อนรัน check.sh'
fi
if [[ ! "$GITHUB_USER" =~ ^[A-Za-z0-9][A-Za-z0-9-]{0,38}$ ]]; then
  finish_early 'GITHUB_USER มีรูปแบบไม่ถูกต้อง'
fi

tmp_dir="$(mktemp -d)" || finish_early 'สร้างพื้นที่ชั่วคราวไม่สำเร็จ'
chmod 700 "$tmp_dir"
trap 'rm -rf -- "$tmp_dir"' EXIT

# Usage: gh_api METHOD /path output-file
# ทุก response ถูก cache ใน tmp_dir และอ่านซ้ำจากไฟล์โดยไม่ยิง request ซ้ำ
gh_api() {
  local method="$1" path="$2" output_file="$3"
  local headers_file config_file status curl_rc tracing=0
  headers_file="$tmp_dir/gh-headers-$GH_API_REQUEST_COUNT"
  config_file="$tmp_dir/gh-curl-$GH_API_REQUEST_COUNT.conf"
  printf 'header = "Authorization: token %s"\n' "$GITHUB_TOKEN" >"$config_file"
  chmod 600 "$config_file"
  case $- in *x*) tracing=1; set +x ;; esac
  if status="$(curl --config "$config_file" --silent --show-error \
      --connect-timeout 15 --max-time 60 --request "$method" \
      --header 'Accept: application/vnd.github+json' \
      --header 'X-GitHub-Api-Version: 2022-11-28' \
      --dump-header "$headers_file" --output "$output_file" \
      --write-out '%{http_code}' "$GITHUB_API$path")"; then
    curl_rc=0
  else
    curl_rc=$?
  fi
  [ "$tracing" -eq 0 ] || set -x
  rm -f -- "$config_file"
  GH_API_REQUEST_COUNT=$((GH_API_REQUEST_COUNT + 1))
  GH_API_STATUS="$status"
  GH_API_RETRY_AFTER="$(awk '
    tolower($0) ~ /^retry-after:/ {
      sub(/^[^:]*:[[:space:]]*/, ""); sub(/\r$/, ""); print; exit
    }
  ' "$headers_file")"
  if [ "$GH_API_STATUS" = '403' ] || [ "$GH_API_STATUS" = '429' ]; then
    finish_early "GitHub API จำกัดคำขอ (HTTP $GH_API_STATUS, Retry-After: ${GH_API_RETRY_AFTER:-ไม่ระบุ})"
  fi
  [ "$curl_rc" -eq 0 ]
}

auth_json="$tmp_dir/github-user.json"
if ! gh_api GET '/user' "$auth_json"; then
  finish_early 'เชื่อมต่อ GitHub API ไม่สำเร็จ'
fi
case "$GH_API_STATUS" in
  200) ;;
  401) finish_early 'GITHUB_TOKEN ไม่ถูกต้องหรือหมดอายุ (GitHub API ตอบ HTTP 401)' ;;
  403|429) finish_early "GitHub API จำกัดคำขอ (HTTP $GH_API_STATUS, Retry-After: ${GH_API_RETRY_AFTER:-ไม่ระบุ})" ;;
  *) finish_early "ตรวจสอบ GITHUB_TOKEN ไม่สำเร็จ (GitHub API ตอบ HTTP $GH_API_STATUS)" ;;
esac
if ! EXPECTED_USER="$GITHUB_USER" python3 - "$auth_json" <<'PY'
import json, os, sys
actual = str(json.load(open(sys.argv[1], encoding="utf-8")).get("login", ""))
raise SystemExit(0 if actual.casefold() == os.environ["EXPECTED_USER"].casefold() else 1)
PY
then
  finish_early 'GITHUB_USER ไม่ตรงกับเจ้าของ GITHUB_TOKEN'
fi
pass 'ยืนยัน GITHUB_TOKEN และเจ้าของบัญชีตรงกับ GITHUB_USER'

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
  if EXPECTED_TOKEN="$TOKEN" python3 - "$config_xml" <<'PY'
import os, sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
items = root.findall(".//org.jenkinsci.plugins.gwt.GenericTrigger")
if len(items) != 1:
    raise SystemExit(1)
trigger = items[0]
variables = {v.findtext("key"): v.findtext("value") for v in trigger.findall("./genericVariables/*")}
ok = trigger.findtext("token") == os.environ["EXPECTED_TOKEN"]
ok = ok and variables.get("ref") == "$.ref" and variables.get("after") == "$.after"
ok = ok and trigger.findtext("regexpFilterText") == "$ref"
ok = ok and trigger.findtext("regexpFilterExpression") == "^refs/heads/main$"
ok = ok and trigger.findtext("causeString") == "GitHub push $after"
raise SystemExit(0 if ok else 1)
PY
  then
    pass 'GenericTrigger มี token, ref/after, filter และ causeString ตรง contract'
  else
    fail 'GenericTrigger token/genericVariables/regexp filter ไม่ตรง contract'
  fi
  if python3 - "$config_xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
raise SystemExit(0 if not root.findall(".//hudson.triggers.SCMTrigger") else 1)
PY
  then
    pass "job $JOB ปิด Poll SCM แล้ว"
  else
    fail "job $JOB ยังเปิด Poll SCM; fallback ชั่วคราวต้อง revert ก่อนส่งงาน"
  fi
else
  fail "อ่าน config.xml ของ job $JOB ไม่ได้"
fi

relay_json="$tmp_dir/relay.json"
relay_logs="$tmp_dir/relay.log"
channel=''
relay_started_at=''
if docker inspect "$RELAY" >"$relay_json" 2>/dev/null; then
  read -r channel relay_started_at < <(EXPECTED_TARGET="$TARGET" EXPECTED_IMAGE="$RELAY_IMAGE" python3 - "$relay_json" <<'PY'
import json, os, sys
from urllib.parse import urlsplit
d = json.load(open(sys.argv[1], encoding="utf-8"))[0]
args = (d.get("Config") or {}).get("Cmd") or []
running = ((d.get("State") or {}).get("Running") is True)
started_at = str((d.get("State") or {}).get("StartedAt") or "")
image = str((d.get("Config") or {}).get("Image") or "")
restart = str((((d.get("HostConfig") or {}).get("RestartPolicy") or {}).get("Name")) or "")
networks = (d.get("NetworkSettings") or {}).get("Networks") or {}
try:
    url = args[args.index("--url") + 1]
    target = args[args.index("--target") + 1]
except (ValueError, IndexError):
    raise SystemExit(1)
parsed = urlsplit(url)
valid_url = parsed.scheme == "https" and parsed.hostname == "smee.io"
valid_url = valid_url and bool(parsed.path.strip("/")) and parsed.path.count("/") == 1
valid_url = valid_url and not parsed.query and not parsed.fragment
valid = running and args == ["--url", url, "--target", target]
valid = valid and valid_url and target == os.environ["EXPECTED_TARGET"]
valid = valid and image == os.environ["EXPECTED_IMAGE"]
valid = valid and restart == "unless-stopped" and "cicd-net" in networks
if valid and started_at:
    print(url, started_at)
else:
    raise SystemExit(1)
PY
  )
fi
if [ -n "$channel" ]; then
  pass "$RELAY ตรง image digest/network/restart/url/target contract"
else
  fail "$RELAY ต้องตรง pinned image, cicd-net, unless-stopped และ canonical args"
fi
docker logs --timestamps --since "${relay_started_at:-1970-01-01T00:00:00Z}" "$RELAY" >"$relay_logs" 2>&1 || :
if grep -q 'Connected' "$relay_logs"; then
  pass "$RELAY log มี Connected หลัง StartedAt"
else
  fail "$RELAY log ไม่มี Connected หลัง StartedAt"
fi

repo_url="https://github.com/$GITHUB_USER/hello-ci.git"
origin_sha="$(timeout 60 git ls-remote "$repo_url" refs/heads/main 2>/dev/null | awk 'NR == 1 {print $1}')"
if [[ "$origin_sha" =~ ^[0-9a-f]{40}$ ]]; then
  pass 'อ่าน SHA ปัจจุบันของ origin/main ได้'
else
  fail 'อ่าน SHA ปัจจุบันของ origin/main ไม่ได้'
fi

hooks_json="$tmp_dir/hooks.json"
hook_id=''
if gh_api GET "/repos/$GITHUB_USER/hello-ci/hooks?per_page=100" "$hooks_json" \
  && [ "$GH_API_STATUS" = '200' ] && [ -n "$channel" ]; then
  hook_id="$(EXPECTED_URL="$channel" python3 - "$hooks_json" <<'PY'
import json, os, sys
for hook in json.load(open(sys.argv[1], encoding="utf-8")):
    config = hook.get("config") or {}
    ok = config.get("url") == os.environ["EXPECTED_URL"]
    ok = ok and config.get("content_type") == "json"
    ok = ok and str(config.get("insecure_ssl")) == "0"
    ok = ok and hook.get("events") == ["push"] and hook.get("active") is True
    if ok:
        print(hook.get("id", ""))
        break
PY
)"
fi
if [[ "$hook_id" =~ ^[0-9]+$ ]]; then
  pass 'GitHub hook ตรง relay channel, json, push-only, active และ SSL verify'
else
  fail "ไม่พบ GitHub hook ของ hello-ci ที่ครบ contract (HTTP ${GH_API_STATUS:-ไม่ทราบ})"
fi

deliveries_json="$tmp_dir/deliveries.json"
delivery_json="$tmp_dir/delivery.json"
delivery_id=''
delivery_timestamp=''
delivery_after=''
delivery_status=''
delivery_unsigned='false'
if [[ "$hook_id" =~ ^[0-9]+$ ]] \
  && gh_api GET "/repos/$GITHUB_USER/hello-ci/hooks/$hook_id/deliveries?per_page=10" "$deliveries_json" \
  && [ "$GH_API_STATUS" = '200' ]; then
  delivery_id="$(python3 - "$deliveries_json" <<'PY'
import json, sys
for item in json.load(open(sys.argv[1], encoding="utf-8")):
    if item.get("event") == "push":
        print(item.get("id", ""))
        break
PY
)"
fi
if [[ "$delivery_id" =~ ^[0-9]+$ ]] \
  && gh_api GET "/repos/$GITHUB_USER/hello-ci/hooks/$hook_id/deliveries/$delivery_id" "$delivery_json" \
  && [ "$GH_API_STATUS" = '200' ]; then
  read -r delivery_timestamp delivery_after delivery_status delivery_unsigned < <(python3 - "$delivery_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
request = d.get("request") or {}
payload = request.get("payload") or {}
headers = request.get("headers") or {}
unsigned = not any(str(key).casefold() == "x-hub-signature-256" for key in headers)
print(d.get("delivered_at", ""), payload.get("after", ""), d.get("status_code", ""), str(unsigned).lower())
PY
  )
fi
if [[ "$delivery_status" =~ ^2[0-9][0-9]$ ]] \
  && [ "$delivery_after" = "$origin_sha" ] && [ -n "$delivery_timestamp" ] \
  && [ "$delivery_unsigned" = 'true' ]; then
  pass "GitHub push delivery ตอบ $delivery_status, after ตรง origin และไม่มี X-Hub-Signature-256"
else
  fail 'GitHub push delivery ต้องเป็น 2xx, after ตรง origin และไม่มี X-Hub-Signature-256'
fi

build_json="$tmp_dir/build.json"
builds_json="$tmp_dir/builds.json"
console="$tmp_dir/console.txt"
build_number=''
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/$JOB/lastBuild/api/json?tree=number,result,building,actions[causes[shortDescription]]" \
    -o "$build_json" 2>/dev/null; then
  build_number="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("number", ""))' "$build_json")"
  if EXPECTED_SHA="$origin_sha" python3 - "$build_json" <<'PY'
import json, os, re, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
causes = [str(c.get("shortDescription", "")) for a in d.get("actions", []) for c in a.get("causes", [])]
ok = d.get("result") == "SUCCESS" and d.get("building") is False
expected = "GitHub push " + os.environ["EXPECTED_SHA"]
ok = ok and causes.count(expected) == 1
ok = ok and bool(re.fullmatch(r"GitHub push [0-9a-f]{40}", expected))
raise SystemExit(0 if ok else 1)
PY
  then
    pass "build ล่าสุด #$build_number = SUCCESS และ cause ตรง GitHub push <SHA>"
  else
    fail 'build ล่าสุดต้องจบ SUCCESS และ cause ต้องเท่ากับ GitHub push <origin SHA>'
  fi
else
  fail "อ่าน build ล่าสุดของ $JOB ไม่ได้"
fi

if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/$JOB/api/json?tree=builds[number,actions[causes[shortDescription]]]" \
    -o "$builds_json" 2>/dev/null \
  && EXPECTED_SHA="$origin_sha" python3 - "$builds_json" <<'PY'
import json, os, re, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
causes = [
    str(c.get("shortDescription", ""))
    for build in d.get("builds", [])
    for action in build.get("actions", [])
    for c in action.get("causes", [])
]
gwt = [cause for cause in causes if cause.startswith("GitHub push")]
valid = all(re.fullmatch(r"GitHub push [0-9a-f]{40}", cause) for cause in gwt)
expected = "GitHub push " + os.environ["EXPECTED_SHA"]
raise SystemExit(0 if valid and causes.count(expected) == 1 else 1)
PY
then
  pass 'ทุก GWT build มี exact SHA cause และ build ที่ตรง delivery/origin SHA มี exactly 1'
else
  fail 'GWT cause ต้องตรง regex และจำนวน build ของ delivery/origin SHA ต้องเท่ากับ 1'
fi
curl -fsS -u "$JENKINS_AUTH" \
  "$JENKINS_URL/job/$JOB/${build_number:-0}/consoleText" -o "$console" 2>/dev/null || :
if [[ "$origin_sha" =~ ^[0-9a-f]{40}$ ]] && [ "$delivery_after" = "$origin_sha" ] \
  && EXPECTED_SHA="$origin_sha" python3 - "$console" <<'PY'
import os, re, sys
text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
checkouts = re.findall(r"Checking out Revision ([0-9a-f]{40})", text, re.I)
raise SystemExit(0 if checkouts and checkouts[-1].lower() == os.environ["EXPECTED_SHA"].lower() else 1)
PY
then
  pass 'delivery SHA, origin/main และ checkout SHA ของ build ล่าสุดตรงกัน'
else
  fail 'delivery SHA, origin/main และ checkout SHA ของ build ล่าสุดไม่ตรงกัน'
fi

if [ -n "$delivery_timestamp" ] && EXPECTED_TARGET="$TARGET" DELIVERY_AT="$delivery_timestamp" \
    python3 - "$relay_logs" <<'PY'
from datetime import datetime
import os, re, sys

def parse_timestamp(value):
    value = value.strip()
    value = re.sub(r"(\.\d{6})\d+Z$", r"\1Z", value)
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

try:
    delivered = parse_timestamp(os.environ["DELIVERY_AT"])
except ValueError:
    raise SystemExit(1)
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    fields = line.split(None, 1)
    if len(fields) != 2:
        continue
    try:
        logged = parse_timestamp(fields[0])
    except ValueError:
        continue
    message = fields[1]
    if logged >= delivered and "POST " in message and os.environ["EXPECTED_TARGET"] in message \
            and re.search(r"(?:-|\s) 200(?:\s|$)", message):
        raise SystemExit(0)
raise SystemExit(1)
PY
then
  pass "$RELAY log มี POST canonical target ได้ 200 หลังเวลา delivery"
else
  fail "$RELAY log ไม่มี POST canonical target ได้ 200 หลังเวลา delivery"
fi

printf '[INFO] GitHub API requests ใน run นี้: %d\n' "$GH_API_REQUEST_COUNT"
if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS — LAB 5 พร้อมใช้งาน\n'
  exit 0
fi
printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
