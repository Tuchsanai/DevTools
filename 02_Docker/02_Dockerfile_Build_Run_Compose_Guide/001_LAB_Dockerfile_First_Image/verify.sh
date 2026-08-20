#!/usr/bin/env bash
set -u

fail_count=0

pass() {
  echo "[PASS] $1"
}

fail() {
  echo "[FAIL] $1"
  fail_count=$((fail_count + 1))
}

check_file() {
  if [[ -f "$1" ]]; then
    pass "พบไฟล์ $1"
  else
    fail "ไม่พบไฟล์ $1"
  fi
}

check_dockerfile_line() {
  if [[ -f Dockerfile ]] && grep -Fqx -- "$1" Dockerfile; then
    pass "Dockerfile มีคำสั่ง: $1"
  else
    fail "Dockerfile ไม่มีคำสั่ง: $1"
  fi
}

cleanup() {
  docker rm -f dockerfile-lab-web dockerfile-lab-web2 >/dev/null 2>&1 || true
}

trap cleanup EXIT

check_file Dockerfile
check_file app.py
check_file requirements.txt
check_file .dockerignore

check_dockerfile_line 'FROM python:3.12-slim'
check_dockerfile_line 'WORKDIR /app'
check_dockerfile_line 'ENV APP_VERSION=1.0'
check_dockerfile_line 'EXPOSE 5000'
check_dockerfile_line 'CMD ["python", "app.py"]'

# ลบ container ของแล็บนี้ที่ค้างอยู่ก่อนเริ่มทดสอบ
# (dockerfile-lab-v2 จากทดลอง ค. จองพอร์ต 8181 อยู่ ถ้าไม่ลบจะ FAIL ด้วย port is already allocated)
docker rm -f dockerfile-lab-web dockerfile-lab-web2 dockerfile-lab-v2 dockerfile-lab-noport >/dev/null 2>&1 || true

build_log=$(mktemp)
if docker build -t dockerfile-lab:1.0 . >"$build_log" 2>&1; then
  pass "build image dockerfile-lab:1.0 สำเร็จ"
else
  fail "build image dockerfile-lab:1.0 ไม่สำเร็จ"
  tail -20 "$build_log"
fi
rm -f "$build_log"

if docker image ls --format '{{.Repository}}:{{.Tag}}' | grep -Fqx 'dockerfile-lab:1.0'; then
  pass "พบ image dockerfile-lab:1.0"
else
  fail "ไม่พบ image dockerfile-lab:1.0"
fi

image_cmd=$(docker image inspect --format '{{json .Config.Cmd}}' dockerfile-lab:1.0 2>/dev/null || true)
if [[ "$image_cmd" == '["python","app.py"]' ]]; then
  pass "Config.Cmd = [python app.py]"
else
  fail "Config.Cmd ไม่ใช่ [python app.py]"
fi

image_ports=$(docker image inspect --format '{{json .Config.ExposedPorts}}' dockerfile-lab:1.0 2>/dev/null || true)
if [[ "$image_ports" == *'"5000/tcp"'* ]]; then
  pass "Config.ExposedPorts มี 5000/tcp"
else
  fail "Config.ExposedPorts ไม่มี 5000/tcp"
fi

image_env=$(docker image inspect --format '{{range .Config.Env}}{{println .}}{{end}}' dockerfile-lab:1.0 2>/dev/null || true)
if grep -Fqx 'APP_VERSION=1.0' <<<"$image_env"; then
  pass "Config.Env มี APP_VERSION=1.0"
else
  fail "Config.Env ไม่มี APP_VERSION=1.0"
fi

if docker run -d --name dockerfile-lab-web -p 8181:5000 dockerfile-lab:1.0 >/dev/null; then
  pass "สร้าง container dockerfile-lab-web สำเร็จ"
else
  fail "สร้าง container dockerfile-lab-web ไม่สำเร็จ"
fi

body_file=$(mktemp)
health_file=$(mktemp)
body_file2=$(mktemp)
health_file2=$(mktemp)
trap 'rm -f "$body_file" "$health_file" "$body_file2" "$health_file2"; cleanup' EXIT

http_code=""
for ((attempt = 1; attempt <= 30; attempt++)); do
  http_code=$(curl -fsS -o "$body_file" -w '%{http_code}' http://localhost:8181/ 2>/dev/null || true)
  if [[ "$http_code" == "200" ]]; then
    break
  fi
  sleep 1
done

if [[ "$http_code" == "200" ]]; then
  pass "หน้าแรกตอบ HTTP 200"
else
  fail "หน้าแรกไม่ตอบ HTTP 200 ภายใน 30 วินาที"
fi

if grep -Fq 'served from container' "$body_file"; then
  pass "หน้าแรกมีคำว่า served from container"
else
  fail "หน้าแรกไม่มีคำว่า served from container"
fi

if grep -Fq '1.0' "$body_file"; then
  pass "หน้าแรกแสดง version 1.0"
else
  fail "หน้าแรกไม่แสดง version 1.0"
fi

if curl -fsS http://localhost:8181/health -o "$health_file" 2>/dev/null \
  && python3 -c 'import json, sys; data = json.load(open(sys.argv[1])); raise SystemExit(0 if data.get("status") == "ok" else 1)' "$health_file"; then
  pass "/health คืน JSON ที่มี status ok"
else
  fail "/health ไม่คืน JSON ที่มี status ok"
fi

container_id=$(docker container inspect --format '{{.Id}}' dockerfile-lab-web 2>/dev/null | cut -c1-12 || true)
if [[ -n "$container_id" ]] && grep -Fq "$container_id" "$body_file"; then
  pass "hostname บนหน้าเว็บตรงกับ container ID 12 ตัวแรก"
else
  fail "hostname บนหน้าเว็บไม่ตรงกับ container ID 12 ตัวแรก"
fi

container_status=$(docker container inspect --format '{{.State.Status}}' dockerfile-lab-web 2>/dev/null || true)
if [[ "$container_status" == "running" ]]; then
  pass "container dockerfile-lab-web มีสถานะ running"
else
  fail "container dockerfile-lab-web ไม่มีสถานะ running"
fi

if docker run -d --name dockerfile-lab-web2 -p 8281:5000 dockerfile-lab:1.0 >/dev/null; then
  pass "สร้าง container ตัวที่ 2 จาก image เดิมสำเร็จ"
else
  fail "สร้าง container ตัวที่ 2 จาก image เดิมไม่สำเร็จ"
fi

http_code2=""
for ((attempt = 1; attempt <= 30; attempt++)); do
  http_code2=$(curl -fsS -o "$body_file2" -w '%{http_code}' http://localhost:8281/ 2>/dev/null || true)
  if [[ "$http_code2" == "200" ]]; then
    break
  fi
  sleep 1
done

if curl -fsS http://localhost:8281/health -o "$health_file2" 2>/dev/null; then
  hostname_one=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["hostname"])' "$health_file" 2>/dev/null || true)
  hostname_two=$(python3 -c 'import json, sys; print(json.load(open(sys.argv[1]))["hostname"])' "$health_file2" 2>/dev/null || true)
  if [[ -n "$hostname_one" && -n "$hostname_two" && "$hostname_one" != "$hostname_two" ]]; then
    pass "container ทั้งสองมี hostname ต่างกัน"
  else
    fail "container ทั้งสองมี hostname ไม่ต่างกัน"
  fi
else
  fail "อ่าน /health ของ container ตัวที่ 2 ไม่สำเร็จ"
fi

python_output=$(docker run --rm dockerfile-lab:1.0 python -V 2>&1 || true)
if [[ "$python_output" == Python\ 3.12* ]]; then
  pass "image ใช้ Python 3.12"
else
  fail "image ไม่ได้ใช้ Python 3.12"
fi

cleanup
trap - EXIT
rm -f "$body_file" "$health_file" "$body_file2" "$health_file2"

if ((fail_count == 0)); then
  echo 'ALL CHECKS PASSED'
  exit 0
else
  echo 'SOME CHECKS FAILED'
  exit 1
fi
