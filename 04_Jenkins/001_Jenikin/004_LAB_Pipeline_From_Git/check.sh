#!/usr/bin/env bash
set -uo pipefail

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH="${JENKINS_AUTH:-admin:admin2569}"
JOB='hello-ci-pipeline'
failures=0

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmp_dir="$(mktemp -d)" || exit 1
chmod 700 "$tmp_dir"
trap 'rm -rf -- "$tmp_dir"' EXIT

for file in .course-cicd2569 .dockerignore Dockerfile Jenkinsfile app/index.html expected.txt hello.sh; do
  if [ -s "$root/$file" ]; then pass "artifact $file พร้อม"; else fail "artifact $file หายหรือว่าง"; fi
done

if [ "$(cat "$root/.course-cicd2569" 2>/dev/null)" = 'course fixture — safe to delete' ]; then
  pass 'ownership marker มีค่า canonical safe-to-delete'
else
  fail 'ownership marker ไม่ตรง contract'
fi

if grep -Fq 'org.opencontainers.image.source' "$root/Dockerfile" \
  && grep -Fq 'org.opencontainers.image.revision' "$root/Dockerfile"; then
  pass 'Dockerfile มี OCI source และ revision labels'
else
  fail 'Dockerfile ขาด OCI source/revision labels'
fi

for contract in \
  "git rev-parse HEAD" \
  "git remote get-url origin" \
  "diff -u expected.txt actual.txt" \
  'usernamePassword(credentialsId: env.DOCKER_CREDENTIALS' \
  'LOCAL_IMAGE="hello-ci-local:$FULL_SHA"' \
  'docker login --username "$DOCKER_USER" --password-stdin' \
  'docker push "$IMAGE:$FULL_SHA"' \
  'docker push "$IMAGE:$SHORT_SHA"' \
  'IMAGE="$(cat image-name.txt)"' \
  'DOCKER_CONFIG="$(mktemp -d)"' \
  'test -z "$(find "$DOCKER_CONFIG" -mindepth 1 -print -quit)"' \
  "anonymous Docker config: empty temporary directory" \
  'docker pull "$IMAGE@$DIGEST"' \
  'docker run --rm --entrypoint /usr/local/bin/hello-ci-test'; do
  if grep -Fq "$contract" "$root/Jenkinsfile"; then
    pass "Jenkinsfile contract: $contract"
  else
    fail "Jenkinsfile ขาด contract: $contract"
  fi
done

if python3 - "$root/Jenkinsfile" <<'PY'
from pathlib import Path
import sys
text = Path(sys.argv[1]).read_text(encoding="utf-8")
build = text.index("stage('Build OCI image')")
publish = text.index("stage('Publish image')")
binding = text.index("withCredentials([")
verify = text.index("stage('Verify public digest')")
assert text.count("withCredentials([") == 1
assert build < publish < binding < verify
assert "DOCKER_TOKEN" not in text[verify:]
verify_text = text[verify:]
assert 'DOCKER_CONFIG="$(mktemp -d)"' in verify_text
assert "trap 'rm -rf \"$DOCKER_CONFIG\"' EXIT" in verify_text
assert 'test -z "$(find "$DOCKER_CONFIG" -mindepth 1 -print -quit)"' in verify_text
assert verify_text.index('DOCKER_CONFIG="$(mktemp -d)"') < verify_text.index('docker pull "$IMAGE@$DIGEST"')
PY
then
  pass 'Docker credential binding มีครั้งเดียวและอยู่ใน Publish stage'
else
  fail 'Docker credential ต้อง bind เฉพาะ Publish stage หนึ่งครั้ง'
fi

if grep -Eq '<(GITHUB|DOCKER)_(TOKEN|PASSWORD)>|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}' "$root/Jenkinsfile" "$root/Dockerfile" "$root/app/index.html"; then
  fail 'พบรูปแบบ secret ใน implementation'
else
  pass 'implementation ไม่มี token/password literal'
fi

if [ -z "${GITHUB_USER:-}" ] || [ -z "${DOCKER_USER:-}" ]; then
  fail 'ต้องกำหนด GITHUB_USER และ DOCKER_USER จาก runtime environment'
  origin_sha=''
else
  repo_url="https://github.com/$GITHUB_USER/hello-ci.git"
  origin_sha="$(timeout 60 git ls-remote "$repo_url" refs/heads/main 2>/dev/null | awk 'NR == 1 {print $1}')"
  if [[ "$origin_sha" =~ ^[0-9a-f]{40}$ ]]; then
    pass 'anonymous GitHub origin/main คืน full SHA'
  else
    fail 'anonymous GitHub origin/main ไม่พร้อม'
  fi
  marker_url="https://raw.githubusercontent.com/$GITHUB_USER/hello-ci/main/.course-cicd2569"
  if [ "$(curl -fsS --max-time 30 "$marker_url" 2>/dev/null)" = 'course fixture — safe to delete' ]; then
    pass 'GitHub main มี ownership marker canonical'
  else
    fail 'GitHub main ไม่มี ownership marker canonical'
  fi
fi

config="$tmp_dir/config.xml"
if curl -fsS --max-time 20 -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/config.xml" -o "$config"; then
  if EXPECTED_URL="https://github.com/${GITHUB_USER:-<GITHUB_USER>}/hello-ci.git" python3 - "$config" <<'PY'
import os, sys, xml.etree.ElementTree as ET
root = ET.parse(sys.argv[1]).getroot()
definition = root.find("definition")
remote = definition.findtext(".//hudson.plugins.git.UserRemoteConfig/url") if definition is not None else None
branch = definition.findtext(".//hudson.plugins.git.BranchSpec/name") if definition is not None else None
script = definition.findtext("scriptPath") if definition is not None else None
creds = definition.findall(".//credentialsId") if definition is not None else [1]
ok = remote == os.environ["EXPECTED_URL"] and branch in ("*/main", "main") and script == "Jenkinsfile" and not creds
raise SystemExit(0 if ok else 1)
PY
  then pass 'Jenkins job ใช้ anonymous GitHub SCM/main/Jenkinsfile'; else fail 'Jenkins SCM contract ไม่ตรง'; fi

  if grep -Fq '<spec>* * * * *</spec>' "$config"; then pass 'Poll SCM schedule เป็น * * * * *'; else fail 'Poll SCM schedule ไม่ตรง'; fi

  console="$tmp_dir/console.txt"
  evidence="$tmp_dir/build-evidence.env"
  if curl -fsS --max-time 30 -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/lastSuccessfulBuild/consoleText" -o "$console" \
    && curl -fsS --max-time 30 -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/lastSuccessfulBuild/artifact/build-evidence.env" -o "$evidence"; then
    full_sha="$(sed -n 's/^FULL_SHA=//p' "$evidence")"
    short_sha="$(sed -n 's/^SHORT_SHA=//p' "$evidence")"
    digest="$(sed -n 's/^DIGEST=//p' "$evidence")"
    image="$(sed -n 's/^IMAGE=//p' "$evidence")"
    if [[ "$full_sha" =~ ^[0-9a-f]{40}$ ]] && [ "$short_sha" = "${full_sha:0:12}" ]; then pass 'build artifact มี full/short SHA ที่สัมพันธ์กัน'; else fail 'full/short SHA ไม่สัมพันธ์กัน'; fi
    if [ -n "$origin_sha" ] && [ "$full_sha" = "$origin_sha" ]; then pass 'build SHA ตรง origin/main'; else fail 'build SHA ไม่ตรง origin/main'; fi
    if [[ "$digest" =~ ^sha256:[0-9a-f]{64}$ ]]; then pass 'build artifact มี immutable digest'; else fail 'digest ไม่ถูกต้อง'; fi
    if grep -Fq 'Finished: SUCCESS' "$console" && grep -Fq 'Verify public digest' "$console" \
      && grep -Fq 'anonymous Docker config: empty temporary directory' "$console"; then pass 'Jenkins build จบ SUCCESS หลัง anonymous verify ด้วย empty DOCKER_CONFIG'; else fail 'console ไม่มี SUCCESS/anonymous verify contract'; fi
    if [[ "$image" == "${DOCKER_USER:-<DOCKER_USER>}/hello-ci" ]] && docker pull "$image@$digest" >/dev/null 2>&1; then
      pulled_revision="$(docker inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}' "$image@$digest" 2>/dev/null)"
      pulled_output="$(docker run --rm --entrypoint /usr/local/bin/hello-ci-test "$image@$digest" 2>/dev/null)"
      [ "$pulled_revision" = "$full_sha" ] && pass 'OCI revision label ตรง build SHA' || fail 'OCI revision label ไม่ตรง build SHA'
      [ "$pulled_output" = 'Hello from GitHub' ] && pass 'pull-run by digest ให้ผล deterministic' || fail 'pull-run by digest ให้ผลไม่ตรง'
    else
      fail 'pull image by digest ไม่สำเร็จ'
    fi
  else
    fail 'อ่าน last successful console/build-evidence.env ไม่สำเร็จ'
  fi
else
  fail "เชื่อม Jenkins job $JOB ไม่สำเร็จที่ $JENKINS_URL"
fi

if [ "$failures" -eq 0 ]; then
  printf 'ผลรวม: PASS\n'
  exit 0
fi
printf 'ผลรวม: FAIL (%d จุด)\n' "$failures"
exit 1
