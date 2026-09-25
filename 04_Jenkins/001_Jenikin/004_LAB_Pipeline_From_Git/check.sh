#!/usr/bin/env bash
# ตรวจสถานะจบ LAB 4 — รันใน devtools:
#   GITHUB_USER=<github id> DOCKER_USER=<docker id> bash check.sh
set -uo pipefail

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH='admin:admin2569'
JOB='hello-ci-pipeline'
PROJECT_DIR="${PROJECT_DIR:-$HOME/hello-ci}"
failures=0
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
unset DOCKER_TOKEN GITHUB_TOKEN

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }
info() { printf '[INFO] %s\n' "$1"; }
json() { python3 -c "import json,sys; d=json.load(sys.stdin); print($1)" 2>/dev/null; }

if [ -z "${GITHUB_USER:-}" ] || [ -z "${DOCKER_USER:-}" ]; then
  fail 'กรุณารันด้วย GITHUB_USER=<id> DOCKER_USER=<id> bash check.sh'
  printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"; exit 1
fi

# 1) GitHub repository เป็น Public และอ่าน HEAD ของ main ได้โดยไม่ใช้ token
repo_json="$(curl -fsS "https://api.github.com/repos/$GITHUB_USER/hello-ci" 2>/dev/null || true)"
if [ "$(printf '%s' "$repo_json" | json 'd.get("private")')" = 'False' ]; then
  pass "GitHub repository $GITHUB_USER/hello-ci เป็น Public"
else
  fail 'ไม่พบ GitHub repository hello-ci แบบ Public'
fi
head_sha="$(git ls-remote "https://github.com/$GITHUB_USER/hello-ci.git" refs/heads/main 2>/dev/null | cut -c1-40)"
[ -n "$head_sha" ] && info "GitHub main = ${head_sha:0:7}" || fail 'อ่าน refs/heads/main จาก GitHub ไม่ได้'

# 2) job ตั้งเป็น Pipeline script from SCM + Poll SCM
config="$tmp_dir/config.xml"
curl -fsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/config.xml" -o "$config" 2>/dev/null
if grep -qi "<url>https://github.com/$GITHUB_USER/hello-ci" "$config" \
  && grep -q '<name>\*/main</name>' "$config" \
  && grep -q '<scriptPath>Jenkinsfile</scriptPath>' "$config"; then
  pass 'job อ่าน Jenkinsfile จาก GitHub branch */main'
else
  fail 'job ยังไม่ได้ตั้ง Pipeline script from SCM (URL / */main / Jenkinsfile)'
fi
grep -q '<spec>\* \* \* \* \*</spec>' "$config" && pass 'เปิด Poll SCM ทุกนาที (* * * * *)' \
  || fail 'ยังไม่ได้เปิด Poll SCM * * * * *'

# 3) build ล่าสุดสำเร็จ และตรงกับ HEAD ของ GitHub
build_json="$(curl -gfsS -u "$JENKINS_AUTH" \
  "$JENKINS_URL/job/$JOB/lastBuild/api/json?tree=number,result,actions[lastBuiltRevision[SHA1]]" 2>/dev/null)"
build_number="$(printf '%s' "$build_json" | json 'd["number"]')"
build_result="$(printf '%s' "$build_json" | json 'd["result"]')"
built_sha="$(printf '%s' "$build_json" | json '[a["lastBuiltRevision"]["SHA1"] for a in d["actions"] if a and "lastBuiltRevision" in a][0]')"
[ "$build_result" = 'SUCCESS' ] && pass "$JOB build #$build_number = SUCCESS" \
  || fail "$JOB build ล่าสุดยังไม่ SUCCESS (พบ: ${build_result:-ไม่มี build})"
if [ -n "$head_sha" ] && [ "$built_sha" = "$head_sha" ]; then
  pass "build #$build_number checkout commit ${head_sha:0:7} = HEAD ของ GitHub"
else
  fail "build ล่าสุด checkout ${built_sha:0:7} แต่ GitHub main คือ ${head_sha:0:7}"
fi

# 4) มี build ที่เกิดจาก Poll SCM
if curl -gfsS -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/api/json?tree=builds[actions[causes[shortDescription]]]" 2>/dev/null \
    | grep -q 'Started by an SCM change'; then
  pass 'พบ build ที่เริ่มจาก "Started by an SCM change"'
else
  fail 'ยังไม่มี build ที่เกิดจาก Poll SCM — push commit ใหม่แล้วรอ 1–2 นาที'
fi

# 5) Docker Hub มี tag ของ build นี้ และ latest ชี้ digest เดียวกัน
hub_digest() {
  curl -fsS "https://hub.docker.com/v2/namespaces/$DOCKER_USER/repositories/hello-ci/tags/$1" 2>/dev/null | json 'd.get("digest","")'
}
tag_digest="$(hub_digest "${build_number:-0}")"
latest_digest="$(hub_digest latest)"
if [ -n "$tag_digest" ] && [ "$tag_digest" = "$latest_digest" ]; then
  pass "Docker Hub hello-ci:$build_number และ latest = ${tag_digest:0:19}..."
else
  fail "Docker Hub ยังไม่มี hello-ci:${build_number:-?} หรือ latest ยังชี้ digest อื่น"
fi

# 6) เว็บที่ deploy แล้วบอก build และ commit เดียวกับ GitHub
health="$(curl -fsS http://localhost:3000/api/health 2>/dev/null || true)"
info "health: ${health:-ไม่มีการตอบกลับ}"
if printf '%s' "$health" | grep -q "\"build\":\"$build_number\"" \
  && printf '%s' "$health" | grep -q "\"commit\":\"${head_sha:0:7}\""; then
  pass "http://localhost:3000 = build #$build_number / commit ${head_sha:0:7}"
else
  fail 'เว็บที่ port 3000 ยังไม่ใช่ build/commit ล่าสุด'
fi

# 7) ไม่มี token หลุดเข้า repository
if [ -d "$PROJECT_DIR/.git" ]; then
  leaks="$(git -C "$PROJECT_DIR" grep -I -c -E 'gh[pous]_[A-Za-z0-9]{20,}|github_pat_|dckr_pat_' $(git -C "$PROJECT_DIR" rev-list --all) 2>/dev/null | wc -l)"
  info "token pattern hits in git history: $leaks"
  [ "$leaks" = '0' ] && pass 'ไม่พบรูปแบบ token ใน git history ของ hello-ci' \
    || fail 'พบรูปแบบ token ใน git history — revoke token ทันที'
else
  fail "ไม่พบ Student Project ที่ $PROJECT_DIR"
fi

if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS\n'; exit 0
fi
printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
