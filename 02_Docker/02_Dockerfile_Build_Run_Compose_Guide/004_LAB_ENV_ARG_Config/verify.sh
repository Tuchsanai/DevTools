#!/usr/bin/env bash

set -uo pipefail

failures=0
created_containers=()

pass() { printf '[PASS] %s\n' "$1"; }
fail() { printf '[FAIL] %s\n' "$1"; failures=$((failures + 1)); }

cleanup() {
  local container
  # ${arr[@]+...} กันกรณี array ว่างชนกับ set -u (bash รุ่นเก่า)
  for container in ${created_containers[@]+"${created_containers[@]}"}; do
    docker rm -f "$container" >/dev/null 2>&1 || true
  done
}
trap cleanup EXIT INT TERM

check_contains() {
  local description=$1
  local content=$2
  local expected=$3
  if [[ "$content" == *"$expected"* ]]; then
    pass "$description"
  else
    fail "$description (ไม่พบ: $expected)"
  fi
}

required_files=(requirements.txt app.py Dockerfile Dockerfile.args Dockerfile.argfrom Dockerfile.leak .env.lab .dockerignore verify.sh)
missing=()
for file in "${required_files[@]}"; do
  [[ -f "$file" ]] || missing+=("$file")
done
if ((${#missing[@]} == 0)); then
  pass "มีไฟล์ LAB ครบ"
else
  fail "ไฟล์ไม่ครบ: ${missing[*]}"
fi

if grep -Fxq '.env' .dockerignore 2>/dev/null; then
  pass ".dockerignore มี .env"
else
  fail ".dockerignore ไม่มีบรรทัด .env"
fi

if ! command -v docker >/dev/null 2>&1; then
  fail "ไม่พบคำสั่ง docker"
  printf '%s\n' "CHECKS FAILED: $failures"
  exit 1
fi

if docker build -q -t lab4-config:1.0 -f Dockerfile . >/dev/null 2>&1; then
  pass "build lab4-config:1.0"
else
  fail "build lab4-config:1.0"
fi

docker rm -f lab4-check >/dev/null 2>&1 || true
# ไม่ publish port ออกมา (ตรวจหน้าเว็บผ่าน docker exec ข้างในอยู่แล้ว)
# กัน "port is already allocated" ชนกับ container `web` ที่ผู้เรียนรันค้างไว้ที่ 8184
if docker run -d --name lab4-check -e APP_ENV=production -e APP_VERSION=9.9.9 lab4-config:1.0 >/dev/null; then
  created_containers+=(lab4-check)
  pass "รัน lab4-check"
else
  fail "รัน lab4-check"
fi

page=""
for attempt in {1..30}; do
  if page=$(docker exec lab4-check python -c 'import urllib.request; print(urllib.request.urlopen("http://127.0.0.1:8184", timeout=2).read().decode())' 2>/dev/null); then
    break
  fi
  sleep 1
done
check_contains "หน้าเว็บแสดง production" "$page" "production"
check_contains "หน้าเว็บแสดง 9.9.9" "$page" "9.9.9"

container_env=$(docker exec lab4-check env 2>/dev/null || true)
check_contains "container มี APP_VERSION=9.9.9" "$container_env" "APP_VERSION=9.9.9"

if docker build -q -t demo-args -f Dockerfile.args . >/dev/null 2>&1; then
  pass "build demo-args"
else
  fail "build demo-args"
fi
args_default=$(docker run --rm demo-args 2>/dev/null || true)
check_contains "demo-args ใช้ APP_VERSION=dev" "$args_default" "APP_VERSION=dev"
if [[ "$args_default" == *"BUILD_TOOL="* && "$args_default" != *"BUILD_TOOL=manual"* ]]; then
  pass "BUILD_TOOL ว่างตอน runtime"
else
  fail "BUILD_TOOL ต้องว่างตอน runtime"
fi

if docker build -q --build-arg APP_VERSION=2.5 -t demo-args:2.5 -f Dockerfile.args . >/dev/null 2>&1; then
  pass "build demo-args:2.5 ด้วย build arg"
else
  fail "build demo-args:2.5 ด้วย build arg"
fi
args_25=$(docker run --rm demo-args:2.5 2>/dev/null || true)
check_contains "image เก็บ APP_VERSION=2.5" "$args_25" "APP_VERSION=2.5"
args_override=$(docker run --rm -e APP_VERSION=override demo-args:2.5 2>/dev/null || true)
check_contains "-e ทับ APP_VERSION ได้" "$args_override" "APP_VERSION=override"

history=$(docker history --no-trunc demo-args:2.5 2>/dev/null || true)
check_contains "docker history มี ARG" "$history" "ARG"
check_contains "docker history มี ENV" "$history" "ENV"

docker rm -f lab4-env-file >/dev/null 2>&1 || true
if docker run -d --name lab4-env-file --env-file .env.lab lab4-config:1.0 >/dev/null; then
  created_containers+=(lab4-env-file)
  env_file_output=$(docker exec lab4-env-file env 2>/dev/null || true)
  check_contains "--env-file ตั้ง APP_ENV=staging" "$env_file_output" "APP_ENV=staging"
else
  fail "รัน container ด้วย --env-file"
fi

docker rm -f lab4-env-override >/dev/null 2>&1 || true
if docker run -d --name lab4-env-override --env-file .env.lab -e APP_ENV=production lab4-config:1.0 >/dev/null; then
  created_containers+=(lab4-env-override)
  override_output=$(docker exec lab4-env-override env 2>/dev/null || true)
  check_contains "-e ทับ --env-file ได้" "$override_output" "APP_ENV=production"
else
  fail "รัน container เพื่อทดสอบ override"
fi

image_files=$(docker run --rm lab4-config:1.0 ls -a /app 2>/dev/null || true)
if [[ "$image_files" != *".env"* ]]; then
  pass "ไม่มีไฟล์ .env หลุดเข้า image"
else
  fail "พบไฟล์ .env ใน image (ต้องอยู่ใน .dockerignore)"
fi

if docker build -q -t demo-argfrom -f Dockerfile.argfrom . >/dev/null 2>&1; then
  pass "build demo-argfrom (ARG ก่อน FROM)"
else
  fail "build demo-argfrom (ARG ก่อน FROM)"
fi
argfrom_out=$(docker build --no-cache --progress=plain -t demo-argfrom -f Dockerfile.argfrom . 2>&1 || true)
check_contains "ก่อนประกาศซ้ำ ค่าว่าง" "$argfrom_out" "ALPINE_VERSION=[]"
check_contains "หลังประกาศซ้ำ มีค่า 3.20" "$argfrom_out" "ALPINE_VERSION=[3.20]"

if ((failures == 0)); then
  printf '%s\n' "ALL CHECKS PASSED"
  exit 0
fi

printf '%s\n' "CHECKS FAILED: $failures"
exit 1
