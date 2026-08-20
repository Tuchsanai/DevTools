#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH='admin:admin2569'
failures=0
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
unset DOCKER_TOKEN

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

if [ -z "${DOCKER_USER:-}" ]; then
  fail 'กรุณารันด้วย DOCKER_USER=<id> bash check.sh'
  printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
  exit 1
fi

image="$(docker inspect -f '{{.Config.Image}}' jenkins 2>/dev/null || true)"
if [ "$image" = 'jenkins-docker:2569' ]; then
  pass 'jenkins ใช้ image jenkins-docker:2569'
else
  fail "jenkins ใช้ image ไม่ตรง (พบ: ${image:-ไม่พบ container})"
fi

socket_mount="$(docker inspect -f '{{range .Mounts}}{{if eq .Destination "/var/run/docker.sock"}}{{.Source}}:{{.Destination}}{{end}}{{end}}' jenkins 2>/dev/null || true)"
if [ "$socket_mount" = '/var/run/docker.sock:/var/run/docker.sock' ]; then
  pass 'jenkins mount Docker socket ถูกต้อง'
else
  fail 'jenkins ยังไม่ได้ mount /var/run/docker.sock'
fi

credential_json="$tmp_dir/credentials.json"
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/credentials/store/system/domain/_/api/json?tree=credentials[id]" \
    -o "$credential_json" 2>/dev/null \
  && python3 - "$credential_json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
raise SystemExit(0 if any(c.get("id") == "dockerhub" for c in data.get("credentials", [])) else 1)
PY
then
  pass 'Jenkins Credentials API พบ id dockerhub'
else
  fail 'Jenkins Credentials API ไม่พบ id dockerhub'
fi

build_json="$tmp_dir/build.json"
if curl -gfsS -u "$JENKINS_AUTH" \
    "$JENKINS_URL/job/docker-build-push/lastBuild/api/json?tree=number,result,timestamp,url" \
    -o "$build_json" 2>/dev/null; then
  read -r build_number build_result build_started < <(python3 - "$build_json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
print(d.get("number", ""), d.get("result", ""), d.get("timestamp", 0))
PY
  )
else
  build_number=''
  build_result=''
  build_started='0'
fi

if [ -n "$build_number" ] && [ "$build_result" = 'SUCCESS' ]; then
  pass "docker-build-push build #$build_number = SUCCESS"
else
  fail 'docker-build-push ยังไม่มี build ล่าสุดที่ SUCCESS'
fi

console_url="$JENKINS_URL/job/docker-build-push/${build_number:-0}/consoleText"
jenkins_digest="$(curl -fsS -u "$JENKINS_AUTH" "$console_url" 2>/dev/null \
  | sed -n 's/.*digest: \(sha256:[0-9a-f]\{64\}\).*/\1/p' | tail -1)"
if [ -n "$jenkins_digest" ]; then
  pass 'อ่าน digest ของ push จาก Jenkins console ได้'
else
  fail 'ไม่พบ push digest ใน Jenkins console ของ build ล่าสุด'
fi

hub_json="$tmp_dir/hub-tag.json"
hub_url="https://hub.docker.com/v2/namespaces/$DOCKER_USER/repositories/ci-demo/tags/${build_number:-0}"
if DOCKER_CONFIG="$tmp_dir/anonymous-docker" docker manifest inspect \
    "docker.io/$DOCKER_USER/ci-demo:${build_number:-0}" >/dev/null 2>&1 \
  && curl -fsS "$hub_url" -o "$hub_json" 2>/dev/null; then
  pass 'anonymous client อ่าน manifest และ Hub tag API ได้'
else
  fail 'anonymous client อ่าน tag ปัจจุบันไม่ได้ (ตรวจ public repo/username/tag)'
fi

if [ -s "$hub_json" ] && [ -n "$jenkins_digest" ] \
  && python3 - "$hub_json" "$jenkins_digest" "$build_started" <<'PY'
from datetime import datetime
import json, sys
d = json.load(open(sys.argv[1], encoding="utf-8"))
remote_digest = d.get("digest", "")
updated = datetime.fromisoformat(d["last_updated"].replace("Z", "+00:00")).timestamp()
started = int(sys.argv[3]) / 1000
raise SystemExit(0 if remote_digest == sys.argv[2] and updated >= started else 1)
PY
then
  pass 'Hub digest ตรงกับ build นี้ และ last_updated ใหม่กว่าเวลาเริ่ม build'
else
  fail 'Hub digest/last_updated ไม่ผูกกับ build ล่าสุด'
fi

file_pattern_count="$(python3 - "$SCRIPT_DIR" <<'PY'
from pathlib import Path
import sys
count = 0
for path in Path(sys.argv[1]).rglob("*"):
    if path.is_file():
        try:
            count += path.read_bytes().count(b"dckr_" + b"pat_")
        except OSError:
            pass
print(count)
PY
)"
console_pattern_count="$(curl -fsS -u "$JENKINS_AUTH" "$console_url" 2>/dev/null \
  | python3 -c 'import sys; print(sys.stdin.buffer.read().count(b"dckr_" + b"pat_"))')"
printf '[INFO] Docker token pattern count: lab_files=%s console=%s\n' \
  "$file_pattern_count" "$console_pattern_count"
if [ "$file_pattern_count" = '0' ] && [ "$console_pattern_count" = '0' ]; then
  pass 'ไม่พบรูปแบบ Docker Hub token ในไฟล์แล็บหรือ console'
else
  fail 'พบรูปแบบ Docker Hub token; ต้อง revoke และล้างก่อนส่งงาน'
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
