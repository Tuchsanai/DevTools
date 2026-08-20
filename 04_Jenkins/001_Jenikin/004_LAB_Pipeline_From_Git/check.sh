#!/usr/bin/env bash
set -uo pipefail

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
GITEA_URL="${GITEA_URL:-http://localhost:3000}"
JENKINS_AUTH='admin:admin2569'
GITEA_AUTH='student:student2569'
failures=0
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

gitea_state="$(docker inspect -f '{{.State.Status}}' gitea 2>/dev/null || true)"
if [ "$gitea_state" = 'running' ]; then
  pass 'container gitea กำลังทำงาน'
else
  fail "container gitea ไม่ได้ Up (พบ: ${gitea_state:-ไม่พบ})"
fi

repo_json="$tmp_dir/repo.json"
if curl -fsS -u "$GITEA_AUTH" \
    "$GITEA_URL/api/v1/repos/student/hello-ci" -o "$repo_json" 2>/dev/null \
  && python3 - "$repo_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
ok = d.get("full_name") == "student/hello-ci" and not d.get("private", True)
raise SystemExit(0 if ok else 1)
PY
then
  pass 'Gitea API พบ public repo student/hello-ci'
else
  fail 'Gitea API ไม่พบ public repo student/hello-ci'
fi

contents_json="$tmp_dir/contents.json"
if curl -fsS -u "$GITEA_AUTH" \
    "$GITEA_URL/api/v1/repos/student/hello-ci/contents?ref=main" \
    -o "$contents_json" 2>/dev/null \
  && python3 - "$contents_json" <<'PY'
import json, sys
names = {item.get("name") for item in json.load(open(sys.argv[1], encoding="utf-8"))}
raise SystemExit(0 if {"Jenkinsfile", "hello.sh", "expected.txt"} <= names else 1)
PY
then
  pass 'branch main มี Jenkinsfile และไฟล์โปรเจกต์ครบ'
else
  fail 'branch main ยังไม่มี Jenkinsfile/hello.sh/expected.txt ครบ'
fi

config_xml="$tmp_dir/config.xml"
if curl -fsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/hello-ci-pipeline/config.xml" -o "$config_xml" 2>/dev/null \
  && python3 - "$config_xml" <<'PY'
import sys
import xml.etree.ElementTree as ET

root = ET.parse(sys.argv[1]).getroot()
definition = root.find("definition")
scm = None if definition is None else definition.find("scm")
url = None if scm is None else scm.findtext("./userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
branch = None if scm is None else scm.findtext("./branches/hudson.plugins.git.BranchSpec/name")
script_path = None if definition is None else definition.findtext("scriptPath")
credentials = [] if scm is None else scm.findall(".//credentialsId")
definition_class = "" if definition is None else definition.attrib.get("class", "")
ok = (
    definition_class == "org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition"
    and url == "http://gitea:3000/student/hello-ci.git"
    and branch in {"main", "*/main"}
    and script_path == "Jenkinsfile"
    and not credentials
)
raise SystemExit(0 if ok else 1)
PY
then
  pass 'hello-ci-pipeline ใช้ Pipeline from SCM ตาม contract และไม่ใช้ credential'
else
  fail 'definition/SCM URL/branch/script path ของ hello-ci-pipeline ไม่ตรง contract'
fi

build_json="$tmp_dir/build.json"
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/hello-ci-pipeline/lastBuild/api/json?tree=number,result,building" \
    -o "$build_json" 2>/dev/null \
  && python3 - "$build_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
raise SystemExit(0 if d.get("result") == "SUCCESS" and not d.get("building", True) else 1)
PY
then
  build_number="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["number"])' "$build_json")"
  pass "build ล่าสุด #$build_number = SUCCESS"
else
  fail 'hello-ci-pipeline ยังไม่มี build ล่าสุดที่ SUCCESS'
fi

if [ -s "$config_xml" ] && python3 - "$config_xml" <<'PY'
import sys
import xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
triggers = root.findall(".//hudson.triggers.SCMTrigger")
ok = len(triggers) == 1 and triggers[0].findtext("spec") == "* * * * *"
raise SystemExit(0 if ok else 1)
PY
then
  pass 'Poll SCM เปิดด้วย schedule * * * * *'
else
  fail 'Poll SCM ยังไม่เปิดหรือ schedule ไม่ใช่ * * * * *'
fi

if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS\n'
  exit 0
fi
printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
