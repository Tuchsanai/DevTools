#!/usr/bin/env bash
set -uo pipefail

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH='admin:admin2569'
GITHUB_API='https://api.github.com'
JOB='hello-ci-pipeline'
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
# ทุก response ถูกเก็บใน tmp_dir แล้วนำไฟล์เดิมไปใช้กับหลาย assertion
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

repo_json="$tmp_dir/repo.json"
if gh_api GET "/repos/$GITHUB_USER/hello-ci" "$repo_json" \
  && [ "$GH_API_STATUS" = '200' ] \
  && EXPECTED_OWNER="$GITHUB_USER" python3 - "$repo_json" <<'PY'
import json, os, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
owner = str((d.get("owner") or {}).get("login", ""))
ok = owner.casefold() == os.environ["EXPECTED_OWNER"].casefold()
ok = ok and d.get("name") == "hello-ci" and d.get("private") is False
raise SystemExit(0 if ok else 1)
PY
then
  pass "GitHub repo $GITHUB_USER/hello-ci เป็น public"
else
  fail "ไม่พบ public GitHub repo $GITHUB_USER/hello-ci (HTTP ${GH_API_STATUS:-ไม่ทราบ})"
fi

contents_json="$tmp_dir/main-contents.json"
if gh_api GET "/repos/$GITHUB_USER/hello-ci/contents?ref=main" "$contents_json" \
  && [ "$GH_API_STATUS" = '200' ] \
  && python3 - "$contents_json" <<'PY'
import json, sys
names = {item.get("name") for item in json.load(open(sys.argv[1], encoding="utf-8"))}
required = {".course-cicd2569", "Jenkinsfile", "hello.sh", "expected.txt"}
raise SystemExit(0 if required <= names else 1)
PY
then
  pass 'branch main มี .course-cicd2569, Jenkinsfile, hello.sh และ expected.txt ครบ'
else
  fail 'branch main ยังไม่มี .course-cicd2569/Jenkinsfile/hello.sh/expected.txt ครบ'
fi

marker_json="$tmp_dir/marker.json"
if gh_api GET "/repos/$GITHUB_USER/hello-ci/contents/.course-cicd2569?ref=main" "$marker_json" \
  && [ "$GH_API_STATUS" = '200' ] \
  && python3 - "$marker_json" <<'PY'
import base64, json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
content = base64.b64decode(data.get("content", "")).decode("utf-8")
raise SystemExit(0 if content == "course fixture — safe to delete" else 1)
PY
then
  pass 'ownership marker มีค่า canonical safe-to-delete'
else
  fail 'ownership marker ต้องมีค่า canonical safe-to-delete'
fi

config_xml="$tmp_dir/config.xml"
if curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/config.xml" \
    -o "$config_xml" 2>/dev/null; then
  if EXPECTED_URL="https://github.com/$GITHUB_USER/hello-ci.git" \
      python3 - "$config_xml" <<'PY'
import os, sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
definition = root.find("definition")
scm = None if definition is None else definition.find("scm")
url = None if scm is None else scm.findtext("./userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
branch = None if scm is None else scm.findtext("./branches/hudson.plugins.git.BranchSpec/name")
kind = "" if definition is None else definition.attrib.get("class", "")
ok = kind == "org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition"
ok = ok and url == os.environ["EXPECTED_URL"] and branch in {"main", "*/main"}
ok = ok and definition.findtext("scriptPath") == "Jenkinsfile"
raise SystemExit(0 if ok else 1)
PY
  then
    pass 'job hello-ci-pipeline ใช้ Pipeline from SCM, GitHub URL, main และ Jenkinsfile ตรง contract'
  else
    fail 'definition/SCM URL/branch/scriptPath ของ hello-ci-pipeline ไม่ตรง contract'
  fi
  if python3 - "$config_xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
raise SystemExit(0 if not root.findall(".//credentialsId") else 1)
PY
  then
    pass 'job hello-ci-pipeline ไม่มี credentialsId ใดๆ'
  else
    fail 'job hello-ci-pipeline ต้องไม่กำหนด credentialsId สำหรับ public repo'
  fi
  if python3 - "$config_xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
triggers = root.findall(".//hudson.triggers.SCMTrigger")
ok = len(triggers) == 1 and triggers[0].findtext("spec") == "* * * * *"
raise SystemExit(0 if ok else 1)
PY
  then
    pass 'Poll SCM มีหนึ่ง trigger และ schedule * * * * *'
  else
    fail 'Poll SCM ต้องมีหนึ่ง trigger และ schedule * * * * *'
  fi
else
  fail "อ่าน config.xml ของ job $JOB ไม่ได้"
fi

build_json="$tmp_dir/build.json"
build_number=''
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/$JOB/lastBuild/api/json?tree=number,result,building,actions[causes[shortDescription]]" \
    -o "$build_json" 2>/dev/null; then
  build_number="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("number", ""))' "$build_json")"
  if python3 - "$build_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
causes = [str(c.get("shortDescription", "")) for a in d.get("actions", []) for c in a.get("causes", [])]
ok = d.get("result") == "SUCCESS" and d.get("building") is False
ok = ok and any("scm change" in cause.casefold() for cause in causes)
raise SystemExit(0 if ok else 1)
PY
  then
    pass "build ล่าสุด #$build_number = SUCCESS, จบแล้ว และ cause เป็น SCM change"
  else
    fail 'build ล่าสุดต้องจบ SUCCESS และมี cause เป็น SCM change'
  fi
else
  fail "อ่าน build ล่าสุดของ $JOB ไม่ได้"
fi

repo_url="https://github.com/$GITHUB_USER/hello-ci.git"
origin_sha="$(timeout 60 git ls-remote "$repo_url" refs/heads/main 2>/dev/null | awk 'NR == 1 {print $1}')"
console="$tmp_dir/console.txt"
curl -fsS -u "$JENKINS_AUTH" \
  "$JENKINS_URL/job/$JOB/${build_number:-0}/consoleText" -o "$console" 2>/dev/null || :
if [[ "$origin_sha" =~ ^[0-9a-f]{40}$ ]] \
  && EXPECTED_SHA="$origin_sha" python3 - "$console" <<'PY'
import os, re, sys
text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
checkouts = re.findall(r"Checking out Revision ([0-9a-f]{40})", text, re.I)
raise SystemExit(0 if checkouts and checkouts[-1].lower() == os.environ["EXPECTED_SHA"].lower() else 1)
PY
then
  pass 'checkout SHA ของ build ล่าสุดตรงกับ origin/main'
else
  fail 'checkout SHA ของ build ล่าสุดไม่ตรงกับ origin/main หรืออ่าน SHA ไม่ได้'
fi

printf '[INFO] GitHub API requests ใน run นี้: %d\n' "$GH_API_REQUEST_COUNT"
if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS\n'
  exit 0
fi
printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
