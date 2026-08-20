#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
GITEA_URL="${GITEA_URL:-http://localhost:3000}"
JENKINS_AUTH='admin:admin2569'
GITEA_AUTH='student:student2569'
JOB_NAME='webapp-deploy'
failures=0
tmp_dir="$(mktemp -d)"
anonymous_config="$tmp_dir/anonymous-docker"
mkdir -p "$anonymous_config"
trap 'rm -rf "$tmp_dir"' EXIT
unset DOCKER_TOKEN

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

if [ -z "${DOCKER_USER:-}" ]; then
  fail 'กรุณารันด้วย DOCKER_USER=<id> bash check.sh'
  printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
  exit 1
fi

job_config="$tmp_dir/job-config.xml"
if curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB_NAME/config.xml" \
    -o "$job_config" 2>/dev/null \
  && grep -Fq '<url>http://gitea:3000/student/webapp.git</url>' "$job_config" \
  && grep -Fq '<name>*/main</name>' "$job_config" \
  && grep -Fq '<scriptPath>Jenkinsfile</scriptPath>' "$job_config" \
  && grep -Fq '<token>cicd2569-webapp</token>' "$job_config" \
  && ! grep -Fq '<hudson.triggers.SCMTrigger>' "$job_config"; then
  pass 'job เป็น Pipeline from SCM main และใช้ GWT token cicd2569-webapp โดยไม่มี Poll SCM'
else
  fail 'SCM/branch/Jenkinsfile/GWT token ของ webapp-deploy ไม่ตรง contract'
fi

hooks_json="$tmp_dir/hooks.json"
hook_id=''
if curl -fsS -u "$GITEA_AUTH" \
    "$GITEA_URL/api/v1/repos/student/webapp/hooks" -o "$hooks_json" 2>/dev/null; then
  hook_id="$(python3 - "$hooks_json" <<'PY'
import json, sys
hooks = json.load(open(sys.argv[1], encoding="utf-8"))
target = "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-webapp"
for hook in hooks:
    if hook.get("active") and hook.get("config", {}).get("url") == target:
        print(hook.get("id", ""))
        break
PY
)"
fi
if [ -n "$hook_id" ]; then
  pass 'Gitea repo webapp มี active push webhook URL canonical'
else
  fail 'ไม่พบ active webhook จาก webapp ไป Jenkins token ที่ถูกต้อง'
fi

delivery_status=''
# Gitea 1.27.2 does not expose delivery history in its REST API. Its own
# SQLite hook_task record is the executable source for the real HTTP status.
if [[ "$hook_id" =~ ^[0-9]+$ ]]; then
  delivery_status="$(docker exec gitea sqlite3 /data/gitea/gitea.db \
    "select json_extract(response_content,'$.status') from hook_task where hook_id=$hook_id and event_type='push' and is_delivered=1 and is_succeed=1 order by id desc limit 1;" \
    2>/dev/null || true)"
fi
case "$delivery_status" in
  2??) pass "webhook delivery ล่าสุดตอบ HTTP $delivery_status" ;;
  *) fail "webhook delivery ล่าสุดไม่ใช่ 2xx (พบ: ${delivery_status:-ไม่มีข้อมูล})" ;;
esac

build_json="$tmp_dir/build.json"
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/$JOB_NAME/lastBuild/api/json?tree=number,result,building,timestamp,url,actions[causes[shortDescription]]" \
    -o "$build_json" 2>/dev/null; then
  read -r build_number build_result building build_started webhook_cause < <(python3 - "$build_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
causes = [str(c.get("shortDescription", "")) for a in d.get("actions", []) for c in a.get("causes", [])]
is_webhook = any(any(word in cause.lower() for word in ("webhook", "gitea", "generic")) for cause in causes)
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
  pass "build ล่าสุด #$build_number = SUCCESS และ cause เป็น webhook"
else
  fail 'build ล่าสุดต้องจบ SUCCESS และเกิดจาก webhook push'
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

if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS\n'
  exit 0
fi
printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
