#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH='admin:admin2569'
GITHUB_API='https://api.github.com'
JOB_NAME='webapp-deploy'
TOKEN='cicd2569-webapp'
RELAY='smee-webapp'
TARGET="http://jenkins:8080/generic-webhook-trigger/invoke?token=$TOKEN"
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
if [ -z "${DOCKER_USER:-}" ]; then
  finish_early 'กรุณารันด้วย DOCKER_USER=<id> bash check.sh (ไม่ต้องส่ง DOCKER_TOKEN ให้ตัวตรวจ)'
fi

tmp_dir="$(mktemp -d)" || finish_early 'สร้างพื้นที่ชั่วคราวไม่สำเร็จ'
chmod 700 "$tmp_dir"
anonymous_config="$tmp_dir/anonymous-docker"
mkdir -p "$anonymous_config"
trap 'rm -rf -- "$tmp_dir"' EXIT
# ตัวตรวจ Docker Hub ใช้ public endpoints/anonymous client เท่านั้น
unset DOCKER_TOKEN

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

job_config="$tmp_dir/job-config.xml"
if curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB_NAME/config.xml" \
    -o "$job_config" 2>/dev/null \
  && EXPECTED_URL="https://github.com/$GITHUB_USER/webapp.git" EXPECTED_TOKEN="$TOKEN" \
    python3 - "$job_config" <<'PY'
import os, sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
definition = root.find("definition")
scm = None if definition is None else definition.find("scm")
url = None if scm is None else scm.findtext("./userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
branch = None if scm is None else scm.findtext("./branches/hudson.plugins.git.BranchSpec/name")
kind = "" if definition is None else definition.attrib.get("class", "")
items = root.findall(".//org.jenkinsci.plugins.gwt.GenericTrigger")
if len(items) != 1:
    raise SystemExit(1)
trigger = items[0]
variables = {v.findtext("key"): v.findtext("value") for v in trigger.findall("./genericVariables/*")}
ok = kind == "org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition"
ok = ok and url == os.environ["EXPECTED_URL"] and branch in {"main", "*/main"}
ok = ok and definition.findtext("scriptPath") == "Jenkinsfile"
ok = ok and not root.findall(".//credentialsId") and not root.findall(".//hudson.triggers.SCMTrigger")
ok = ok and trigger.findtext("token") == os.environ["EXPECTED_TOKEN"]
ok = ok and variables.get("ref") == "$.ref" and variables.get("after") == "$.after"
ok = ok and trigger.findtext("regexpFilterText") == "$ref"
ok = ok and trigger.findtext("regexpFilterExpression") == "^refs/heads/main$"
raise SystemExit(0 if ok else 1)
PY
then
  pass 'job ใช้ public GitHub SCM main ไม่มี credentials/Poll และ GWT filter ตรง contract'
else
  fail 'SCM URL/branch/Jenkinsfile/credentials/Poll/GWT ของ webapp-deploy ไม่ตรง contract'
fi

relay_json="$tmp_dir/relay.json"
relay_logs="$tmp_dir/relay.log"
channel=''
if docker inspect "$RELAY" >"$relay_json" 2>/dev/null; then
  channel="$(EXPECTED_TARGET="$TARGET" python3 - "$relay_json" <<'PY'
import json, os, sys
from urllib.parse import urlsplit
d = json.load(open(sys.argv[1], encoding="utf-8"))[0]
args = (d.get("Config") or {}).get("Cmd") or []
running = ((d.get("State") or {}).get("Running") is True)
try:
    url = args[args.index("--url") + 1]
    target = args[args.index("--target") + 1]
except (ValueError, IndexError):
    raise SystemExit(1)
parsed = urlsplit(url)
valid_url = parsed.scheme == "https" and parsed.hostname == "smee.io"
valid_url = valid_url and bool(parsed.path.strip("/")) and parsed.path.count("/") == 1
valid_url = valid_url and not parsed.query and not parsed.fragment
if running and args == ["--url", url, "--target", target] and valid_url and target == os.environ["EXPECTED_TARGET"]:
    print(url)
else:
    raise SystemExit(1)
PY
)"
fi
if [ -n "$channel" ]; then
  pass "$RELAY กำลังรัน และ url/target args ตรง canonical contract"
else
  fail "$RELAY ต้องกำลังรันด้วย smee URL และ canonical Jenkins target ที่ถูกต้อง"
fi
docker logs --timestamps "$RELAY" >"$relay_logs" 2>&1 || :
if grep -q 'Connected' "$relay_logs"; then
  pass "$RELAY log มีหลักฐาน Connected"
else
  fail "$RELAY log ไม่มีหลักฐาน Connected"
fi

repo_url="https://github.com/$GITHUB_USER/webapp.git"
origin_sha="$(timeout 60 git ls-remote "$repo_url" refs/heads/main 2>/dev/null | awk 'NR == 1 {print $1}')"
if [[ "$origin_sha" =~ ^[0-9a-f]{40}$ ]]; then
  pass 'อ่าน SHA ปัจจุบันของ webapp origin/main ได้'
else
  fail 'อ่าน SHA ปัจจุบันของ webapp origin/main ไม่ได้'
fi

hooks_json="$tmp_dir/hooks.json"
hook_id=''
if gh_api GET "/repos/$GITHUB_USER/webapp/hooks?per_page=100" "$hooks_json" \
  && [ "$GH_API_STATUS" = '200' ] && [ -n "$channel" ]; then
  hook_id="$(EXPECTED_URL="$channel" python3 - "$hooks_json" <<'PY'
import json, os, sys
for hook in json.load(open(sys.argv[1], encoding="utf-8")):
    config = hook.get("config") or {}
    ok = config.get("url") == os.environ["EXPECTED_URL"]
    ok = ok and config.get("content_type") == "json"
    ok = ok and str(config.get("insecure_ssl")) == "0"
    ok = ok and config.get("secret") in (None, "")
    ok = ok and hook.get("events") == ["push"] and hook.get("active") is True
    if ok:
        print(hook.get("id", ""))
        break
PY
)"
fi
if [[ "$hook_id" =~ ^[0-9]+$ ]]; then
  pass 'GitHub hook ตรง relay channel, json, push-only, active, SSL verify และ secret ว่าง'
else
  fail "ไม่พบ GitHub hook ของ webapp ที่ครบ contract (HTTP ${GH_API_STATUS:-ไม่ทราบ})"
fi

deliveries_json="$tmp_dir/deliveries.json"
delivery_json="$tmp_dir/delivery.json"
delivery_id=''
delivery_timestamp=''
delivery_after=''
delivery_status=''
if [[ "$hook_id" =~ ^[0-9]+$ ]] \
  && gh_api GET "/repos/$GITHUB_USER/webapp/hooks/$hook_id/deliveries?per_page=10" "$deliveries_json" \
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
  && gh_api GET "/repos/$GITHUB_USER/webapp/hooks/$hook_id/deliveries/$delivery_id" "$delivery_json" \
  && [ "$GH_API_STATUS" = '200' ]; then
  read -r delivery_timestamp delivery_after delivery_status < <(python3 - "$delivery_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
payload = ((d.get("request") or {}).get("payload") or {})
print(d.get("delivered_at", ""), payload.get("after", ""), d.get("status_code", ""))
PY
  )
fi
if [[ "$delivery_status" =~ ^2[0-9][0-9]$ ]] \
  && [ "$delivery_after" = "$origin_sha" ] && [ -n "$delivery_timestamp" ]; then
  pass "GitHub push delivery ล่าสุดตอบ $delivery_status และ payload.after ตรง origin/main"
else
  fail 'GitHub push delivery ล่าสุดต้องเป็น 2xx และ payload.after ต้องตรง origin/main'
fi

build_json="$tmp_dir/build.json"
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/$JOB_NAME/lastBuild/api/json?tree=number,result,building,timestamp,url,actions[causes[shortDescription]]" \
    -o "$build_json" 2>/dev/null; then
  read -r build_number build_result building build_started webhook_cause < <(python3 - "$build_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
causes = [str(c.get("shortDescription", "")) for a in d.get("actions", []) for c in a.get("causes", [])]
is_webhook = any("github push" in cause.casefold() for cause in causes)
print(d.get("number", ""), d.get("result", ""), str(d.get("building", True)).lower(), d.get("timestamp", 0), str(is_webhook).lower())
PY
  )
else
  build_number=''
  build_result=''
  building='true'
  build_started='0'
  webhook_cause='false'
fi
if [ -n "$build_number" ] && [ "$build_result" = 'SUCCESS' ] \
  && [ "$building" = 'false' ] && [ "$webhook_cause" = 'true' ]; then
  pass "build ล่าสุด #$build_number = SUCCESS และ cause มี GitHub push"
else
  fail 'build ล่าสุดต้องจบ SUCCESS และ cause ต้องมี GitHub push'
fi

stages_json="$tmp_dir/stages.json"
if [ -n "$build_number" ] && curl -fsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/$JOB_NAME/$build_number/stages/tree" -o "$stages_json" 2>/dev/null \
  && python3 - "$stages_json" <<'PY'
import json, sys
stages = json.load(open(sys.argv[1], encoding="utf-8")).get("data", {}).get("stages", [])
actual = {s.get("name"): str(s.get("state", "")).upper() for s in stages}
required = ("Build-Test-Push", "Deploy", "Verify")
raise SystemExit(0 if all(actual.get(name) == "SUCCESS" for name in required) else 1)
PY
then
  pass 'Build-Test-Push, Deploy และ Verify เป็น SUCCESS ครบ'
else
  fail 'stage หลักไม่ครบหรือมี stage ที่ไม่ SUCCESS'
fi

console="$tmp_dir/console.txt"
console_url="$JENKINS_URL/job/$JOB_NAME/${build_number:-0}/consoleText"
curl -fsS -u "$JENKINS_AUTH" "$console_url" -o "$console" 2>/dev/null || :
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

test_line="$(grep -nE '3 passed( in [0-9.]+s)?' "$console" | tail -1 | cut -d: -f1)"
first_push_line="$(grep -nE '^The push refers to repository|^Pushing ' "$console" | head -1 | cut -d: -f1)"
if [ -n "$test_line" ] && [ -n "$first_push_line" ] && [ "$test_line" -lt "$first_push_line" ]; then
  pass 'pytest ผ่าน 3 เคสก่อนเริ่ม push image'
else
  fail 'ไม่พบหลักฐาน 3 tests passed ก่อน push ใน console'
fi

jenkins_digest="$(sed -n "s/^${build_number:-0}: digest: \(sha256:[0-9a-f]\{64\}\).*/\1/p" "$console" | tail -1)"
latest_console_digest="$(sed -n 's/^latest: digest: \(sha256:[0-9a-f]\{64\}\).*/\1/p' "$console" | tail -1)"
if [ -n "$jenkins_digest" ]; then
  pass 'อ่าน build digest จาก Jenkins console ได้'
else
  fail 'อ่าน build digest จาก Jenkins console ไม่ได้'
fi
if [ -n "$jenkins_digest" ] && [ "$jenkins_digest" = "$latest_console_digest" ]; then
  pass 'console ยืนยัน BUILD_NUMBER และ latest push digest เดียวกัน'
else
  fail 'digest ของ BUILD_NUMBER กับ latest ใน console ไม่ตรงกัน'
fi

build_tag_json="$tmp_dir/hub-build-tag.json"
latest_tag_json="$tmp_dir/hub-latest-tag.json"
hub_build_url="https://hub.docker.com/v2/namespaces/$DOCKER_USER/repositories/cicd-webapp/tags/${build_number:-0}"
hub_latest_url="https://hub.docker.com/v2/namespaces/$DOCKER_USER/repositories/cicd-webapp/tags/latest"
if DOCKER_CONFIG="$anonymous_config" docker manifest inspect \
    "docker.io/$DOCKER_USER/cicd-webapp:${build_number:-0}" >/dev/null 2>&1 \
  && DOCKER_CONFIG="$anonymous_config" docker manifest inspect \
    "docker.io/$DOCKER_USER/cicd-webapp:latest" >/dev/null 2>&1 \
  && curl -fsS "$hub_build_url" -o "$build_tag_json" 2>/dev/null \
  && curl -fsS "$hub_latest_url" -o "$latest_tag_json" 2>/dev/null; then
  pass 'anonymous client อ่าน BUILD_NUMBER และ latest จาก public Hub repo ได้'
else
  fail 'anonymous client อ่าน Hub tags ไม่ได้ (repo ต้องเป็น public)'
fi

if [ -s "$build_tag_json" ] && [ -s "$latest_tag_json" ] && [ -n "$jenkins_digest" ] \
  && python3 - "$build_tag_json" "$latest_tag_json" "$jenkins_digest" "$build_started" <<'PY'
from datetime import datetime
import json, sys
build = json.load(open(sys.argv[1], encoding="utf-8"))
latest = json.load(open(sys.argv[2], encoding="utf-8"))
expected = sys.argv[3]
started = int(sys.argv[4]) / 1000
updated = datetime.fromisoformat(build["last_updated"].replace("Z", "+00:00")).timestamp()
ok = build.get("digest") == expected == latest.get("digest") and updated >= started
raise SystemExit(0 if ok else 1)
PY
then
  pass 'Hub build digest ตรง Jenkins, ใหม่กว่าเวลาเริ่ม build และ latest ชี้ digest เดียวกัน'
else
  fail 'Hub digest/last_updated/latest ไม่ผูกกับ Jenkins build ล่าสุด'
fi

container_image="$(docker inspect -f '{{.Config.Image}}' webapp 2>/dev/null || true)"
container_running="$(docker inspect -f '{{.State.Running}}' webapp 2>/dev/null || true)"
expected_image="docker.io/$DOCKER_USER/cicd-webapp:${build_number:-0}"
if [ "$container_running" = 'true' ] && [ "$container_image" = "$expected_image" ]; then
  pass "container webapp รัน image tag ของ build #$build_number"
else
  fail "container webapp ไม่ได้รัน image ปัจจุบัน (พบ: ${container_image:-ไม่พบ})"
fi

info_json="$tmp_dir/info.json"
if docker exec jenkins curl -fsS http://webapp:8000/health >/dev/null 2>&1 \
  && docker exec jenkins curl -fsS http://webapp:8000/api/info >"$info_json" 2>/dev/null \
  && python3 - "$info_json" "${build_number:-}" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
required = {"version", "build_number", "theme", "hostname"}
raise SystemExit(0 if set(d) == required and d.get("build_number") == sys.argv[2] else 1)
PY
then
  pass '/health ตอบและ /api/info แสดง build_number ตรง build ล่าสุดผ่าน DNS webapp'
else
  fail 'health/info ของ deployment ไม่ตรง Jenkins build ล่าสุด'
fi

file_pattern_count="$(python3 - "$SCRIPT_DIR" "$PROJECT_DIR/logs/U6.log" <<'PY'
from pathlib import Path
import sys
needle = b"dckr_" + b"pat_"
count = 0
targets = [Path(sys.argv[1])]
if Path(sys.argv[2]).exists():
    targets.append(Path(sys.argv[2]))
for target in targets:
    paths = target.rglob("*") if target.is_dir() else [target]
    for path in paths:
        if path.is_file():
            try:
                # Ignore this check's own numeric summary line; count every
                # other occurrence as a possible retained token.
                for line in path.read_bytes().splitlines():
                    if not line.startswith(b"[INFO] " + needle + b"="):
                        count += line.count(needle)
            except OSError:
                pass
print(count)
PY
)"
console_pattern_count="$(python3 - "$console" <<'PY'
from pathlib import Path
import sys
print(Path(sys.argv[1]).read_bytes().count(b"dckr_" + b"pat_"))
PY
)"
pattern_label="dckr_${PAT_LABEL:-pat_}"
printf '[INFO] %s=%s (lab/log) + %s (console)\n' "$pattern_label" "$file_pattern_count" "$console_pattern_count"
if [ "$file_pattern_count" = '0' ] && [ "$console_pattern_count" = '0' ]; then
  pass 'secret scan ไม่พบรูปแบบ Docker Hub access token'
else
  fail 'secret scan พบรูปแบบ access token; ต้อง revoke และล้างก่อนส่งงาน'
fi

retained_auth_count="$(docker exec jenkins sh -c \
  'find /root /var/jenkins_home /tmp -type f -name config.json -exec grep -hEc '"'"'"auth"[[:space:]]*:'"'"' {} \; 2>/dev/null | awk '"'"'{s+=$1} END {print s+0}'"'"'' \
  2>/dev/null || printf '0')"
printf '[INFO] retained Docker auth entry count: %s\n' "$retained_auth_count"
if [ "$retained_auth_count" = '0' ]; then
  pass 'ไม่พบ Docker auth entry ค้างใน jenkins container'
else
  fail 'พบ Docker auth entry ค้างใน jenkins container'
fi

printf '[INFO] GitHub API requests ใน run นี้: %d\n' "$GH_API_REQUEST_COUNT"
if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS\n'
  exit 0
fi
printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
