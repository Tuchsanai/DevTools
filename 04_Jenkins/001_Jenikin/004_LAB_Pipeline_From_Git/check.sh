#!/usr/bin/env bash
set -uo pipefail

JENKINS_URL="${JENKINS_URL:-http://localhost:8080}"
JENKINS_AUTH="${JENKINS_AUTH:-admin:admin2569}"
PROJECT_DIR="${PROJECT_DIR:-$HOME/hello-ci}"
JOB='hello-ci-pipeline'
failures=0

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmp_dir="$(mktemp -d)" || exit 1
chmod 700 "$tmp_dir"
trap 'rm -rf -- "$tmp_dir"' EXIT

manifest="$root/project-files.txt"
if [ -s "$manifest" ]; then
  pass 'project-files.txt พร้อม'
  while IFS= read -r file || [ -n "$file" ]; do
    [ -n "$file" ] || continue
    if [ -s "$root/$file" ]; then pass "artifact $file พร้อม"; else fail "artifact $file หายหรือว่าง"; fi
  done < "$manifest"
else
  fail 'project-files.txt หายหรือว่าง'
fi

if [ "$(cat "$root/.course-cicd2569" 2>/dev/null)" = 'course fixture — safe to delete' ]; then
  pass 'ownership marker มีค่า canonical safe-to-delete'
else
  fail 'ownership marker ไม่ตรง contract'
fi

project_ready=false
project_top=''
project_origin=''
if git -C "$PROJECT_DIR" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  project_ready=true
  project_top="$(git -C "$PROJECT_DIR" rev-parse --show-toplevel 2>/dev/null || true)"
  pass 'student project เป็น Git worktree'
else
  fail "student project ไม่ใช่ Git worktree: $PROJECT_DIR"
fi

if [ "$project_ready" = true ]; then
  course_top="$(git -C "$root" rev-parse --show-toplevel 2>/dev/null || true)"
  if [ -n "$course_top" ] && [ "$project_top" = "$course_top" ]; then
    fail 'ยังทำงานอยู่ใน course repository; ให้สร้าง $HOME/hello-ci เป็น repository ของตนเองก่อน'
  else
    pass 'student project แยกจาก course repository'
  fi

  project_origin="$(git -C "$PROJECT_DIR" remote get-url origin 2>/dev/null || true)"
  if [ -n "${GITHUB_USER:-}" ] && [[ "$project_origin" =~ ^https://github[.]com/${GITHUB_USER}/hello-ci([.]git)?$ ]]; then
    pass 'origin ชี้ GitHub hello-ci ของนักศึกษา'
  else
    fail 'origin ต้องเป็น https://github.com/<GITHUB_USER>/hello-ci.git ของนักศึกษา'
  fi
  if [[ "$project_origin" =~ [Tt][Uu][Cc][Hh][Ss][Aa][Nn][Aa][Ii]/[Dd][Ee][Vv][Tt][Oo][Oo][Ll][Ss] ]]; then
    fail 'origin ยังชี้ course repository'
  else
    pass 'origin ไม่ชี้ course repository'
  fi

  if [ -s "$manifest" ]; then
    while IFS= read -r file || [ -n "$file" ]; do
      [ -n "$file" ] || continue
      if [ "$file" = 'app/index.html' ] \
        && grep -Fq 'Pipeline จาก GitHub' "$PROJECT_DIR/app/index.html"; then
        pass 'student app/index.html มีข้อความตาม contract (แก้ไขเพื่อทดสอบ Poll SCM ได้)'
      elif cmp -s "$root/$file" "$PROJECT_DIR/$file"; then
        pass "student copy ตรง course source: $file"
      else
        fail "student copy ไม่ตรง course source: $file"
      fi
    done < "$manifest"
  fi
  if [ ! -e "$PROJECT_DIR/hello.sh" ] && [ ! -e "$PROJECT_DIR/expected.txt" ]; then
    pass 'student project ไม่มี helper/result files จาก contract เดิม'
  else
    fail 'ให้ลบ hello.sh และ expected.txt; LAB 4 ใหม่ใช้ app/index.html โดยตรง'
  fi

  scan_input="$tmp_dir/project-secret-scan.txt"
  {
    printf '%s\n' "$project_origin"
    git -C "$PROJECT_DIR" config --local --list 2>/dev/null || true
    git -C "$PROJECT_DIR" log -p --all 2>/dev/null || true
  } > "$scan_input"
  secret_found=false
  if grep -Eq 'ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|https://[^/@:]+:[^/@]+@' "$scan_input"; then
    secret_found=true
  fi
  if [ -n "${GITHUB_TOKEN:-}" ]; then
    token_pattern="$tmp_dir/runtime-token.txt"
    umask 077
    printf '%s\n' "$GITHUB_TOKEN" > "$token_pattern"
    if grep -Fq -f "$token_pattern" "$scan_input"; then secret_found=true; fi
  fi
  if [ "$secret_found" = true ]; then
    fail 'student remote/config/history มีรูปแบบ credential หรือ runtime token'
  else
    pass 'student remote/config/history ไม่มี credential หรือ runtime token'
  fi
fi

for docker_contract in \
  'FROM nginx:1.29-alpine' \
  'COPY app/index.html /usr/share/nginx/html/index.html' \
  'EXPOSE 80'; do
  if grep -Fq "$docker_contract" "$root/Dockerfile"; then
    pass "Dockerfile contract: $docker_contract"
  else
    fail "Dockerfile ขาด contract: $docker_contract"
  fi
done
if grep -Eq 'hello[.]sh|ARG |LABEL |HEALTHCHECK' "$root/Dockerfile"; then
  fail 'Dockerfile ยังมี logic ขั้นสูงหรือ helper script'
else
  pass 'Dockerfile เหลือเฉพาะ nginx, COPY และ EXPOSE'
fi

for pipeline_contract in \
  "stage('Check source')" \
  'git log -1 --oneline' \
  'test -f Dockerfile' \
  'test -f app/index.html' \
  "stage('Build image')" \
  'docker build -t "$IMAGE:$BUILD_NUMBER" .' \
  "stage('Run container')" \
  'docker run --rm "$IMAGE:$BUILD_NUMBER"' \
  "stage('Push image')" \
  "credentialsId: 'dockerhub'" \
  'docker push "$DOCKER_USER/hello-ci:$BUILD_NUMBER"' \
  'docker logout'; do
  if grep -Fq "$pipeline_contract" "$root/Jenkinsfile"; then
    pass "Jenkinsfile contract: $pipeline_contract"
  else
    fail "Jenkinsfile ขาด contract: $pipeline_contract"
  fi
done

if python3 - "$root/Jenkinsfile" <<'PY'
from pathlib import Path
import sys

text = Path(sys.argv[1]).read_text(encoding="utf-8")
check = text.index("stage('Check source')")
build = text.index("stage('Build image')")
run = text.index("stage('Run container')")
push = text.index("stage('Push image')")
binding = text.index("withCredentials([")
assert check < build < run < push < binding
assert text.count("withCredentials([") == 1
assert all(term not in text for term in (
    "archiveArtifacts", "readFile(", "full-sha.txt", "short-sha.txt",
    "image-digest.txt", "build-evidence.env", "hello.sh", "expected.txt",
))
PY
then
  pass 'Stage เรียง Check source → Build → Run → Push และไม่สร้างไฟล์หลักฐาน'
else
  fail 'ลำดับ Stage หรือ simple-pipeline contract ไม่ตรง'
fi

if grep -Eq '<(GITHUB|DOCKER)_(TOKEN|PASSWORD)>|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}' "$root/Jenkinsfile" "$root/Dockerfile" "$root/app/index.html"; then
  fail 'พบรูปแบบ secret ใน implementation'
else
  pass 'implementation ไม่มี token/password literal'
fi

origin_sha=''
if [ -z "${GITHUB_USER:-}" ] || [ -z "${DOCKER_USER:-}" ]; then
  fail 'ต้องกำหนด GITHUB_USER และ DOCKER_USER จาก runtime environment'
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

  completed_json="$tmp_dir/last-completed.json"
  successful_json="$tmp_dir/last-successful.json"
  completed_url="$JENKINS_URL/job/$JOB/lastCompletedBuild/api/json?tree=number,result,actions[causes[shortDescription]]"
  if curl --globoff -fsS --max-time 30 -u "$JENKINS_AUTH" "$completed_url" -o "$completed_json" \
    && curl -fsS --max-time 30 -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/lastSuccessfulBuild/api/json?tree=number" -o "$successful_json"; then
    read -r completed_number completed_result scm_cause < <(python3 - "$completed_json" <<'PY'
import json, sys
data = json.load(open(sys.argv[1], encoding="utf-8"))
causes = [c.get("shortDescription", "") for a in data.get("actions", []) for c in a.get("causes", [])]
print(data.get("number", ""), data.get("result", ""), int(any("Started by an SCM change" in c for c in causes)))
PY
    )
    successful_number="$(python3 - "$successful_json" <<'PY'
import json, sys
print(json.load(open(sys.argv[1], encoding="utf-8")).get("number", ""))
PY
    )"
    if [ "$scm_cause" = 1 ]; then pass 'newest completed build เกิดจาก SCM change'; else fail 'newest completed build ไม่ได้เกิดจาก SCM change'; fi
    if [ "$completed_result" = 'SUCCESS' ] && [ "$completed_number" = "$successful_number" ]; then
      pass 'newest completed build เป็น last successful build'
    else
      fail 'newest completed build ต้อง SUCCESS และตรง lastSuccessfulBuild'
    fi
  else
    completed_number=''
    fail 'อ่าน newest completed/last successful build API ไม่สำเร็จ'
  fi

  console="$tmp_dir/console.txt"
  build_ref="${completed_number:-lastSuccessfulBuild}"
  if curl -fsS --max-time 30 -u "$JENKINS_AUTH" "$JENKINS_URL/job/$JOB/$build_ref/consoleText" -o "$console"; then
    if grep -Fq 'Finished: SUCCESS' "$console" \
      && grep -Fq 'Check source' "$console" \
      && grep -Fq 'Build image' "$console" \
      && grep -Fq 'Run container' "$console" \
      && grep -Fq 'Push image' "$console"; then
      pass 'Console แสดง simple pipeline ครบ 4 Stage และ SUCCESS'
    else
      fail 'Console ไม่มี 4 Stage หรือ SUCCESS ตาม contract'
    fi
    if [ -n "$origin_sha" ] && grep -Fq "$origin_sha" "$console"; then
      pass 'Jenkins checkout revision ตรง origin/main'
    else
      fail 'Console ไม่มี checkout revision ที่ตรง origin/main'
    fi
    image="${DOCKER_USER:-<DOCKER_USER>}/hello-ci:${completed_number:-0}"
    if docker pull "$image" >/dev/null 2>&1 \
      && docker run --rm "$image" sh -c "grep -Fq 'Pipeline จาก GitHub' /usr/share/nginx/html/index.html"; then
      pass 'pull/run image ด้วย Jenkins BUILD_NUMBER tag สำเร็จ'
    else
      fail 'pull/run image ด้วย Jenkins BUILD_NUMBER tag ไม่สำเร็จ'
    fi
  else
    fail 'อ่าน completed build console ไม่สำเร็จ'
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
