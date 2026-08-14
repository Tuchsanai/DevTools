#!/usr/bin/env bash

# เปิดใช้การแจ้งเตือนเมื่อมีการอ้างถึงตัวแปรที่ยังไม่ได้กำหนด แต่ไม่หยุดเมื่อ check ใดล้มเหลว
set -u

fail_count=0
verify_container="regdemo-verify"
verify_image="localhost:5000/workshop/regdemo:1.0"
verify_tmp_tag="regdemo:verify-tmp"

# รันคำสั่งตรวจสอบที่รับเข้ามา แล้วสะสมจำนวนข้อที่ไม่ผ่านเพื่อรายงานพร้อมกันตอนจบ
check() {
  local description="$1"
  shift

  if "$@"; then
    printf '[PASS] %s\n' "$description"
  else
    printf '[FAIL] %s\n' "$description"
    fail_count=$((fail_count + 1))
  fi
}

# ตรวจว่ามี image อยู่ในเครื่องโดยไม่แสดงรายละเอียดจาก docker inspect
image_exists() {
  docker image inspect "$1" >/dev/null 2>&1
}

# ลบเฉพาะคอนเทนเนอร์ชั่วคราวของสคริปต์เมื่อสคริปต์จบ โดยไม่แตะ image หรือ registry
cleanup() {
  docker rm -f "$verify_container" >/dev/null 2>&1 || true
  docker rmi "$verify_tmp_tag" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# เตือนล่วงหน้าถ้ายังไม่ได้ทำแล็บถึงขั้น push — ไม่งั้นข้อ 4 เป็นต้นไปจะ FAIL แบบไม่บอกสาเหตุ
if ! docker ps --filter "name=^lab-registry$" --format '{{.Names}}' | grep -q .; then
  printf '\n%s\n' "[HINT] ยังไม่พบคอนเทนเนอร์ 'lab-registry' ที่กำลังทำงาน"
  printf '%s\n' "       สคริปต์นี้ต้องรัน **หลังทำแล็บถึงข้อ 9** (registry เปิดอยู่ + push tag 1.0 แล้ว)"
  printf '%s\n\n' "       ถ้าเก็บกวาดไปแล้ว ให้ย้อนทำข้อ 3 → 9 ใหม่ก่อนรัน verify.sh"
fi

check "พบไฟล์ Dockerfile" test -f Dockerfile
check "พบไฟล์ site/index.html" test -f site/index.html
check "พบไฟล์ site_v2/index.html" test -f site_v2/index.html

check "คอนเทนเนอร์ lab-registry กำลังทำงาน" \
  sh -c 'test "$(docker inspect -f "{{.State.Running}}" lab-registry 2>/dev/null)" = "true"'

check "registry catalog มี repository workshop/regdemo" \
  sh -c 'curl -fsS http://localhost:5000/v2/_catalog 2>/dev/null | grep -Fq '"'"'"workshop/regdemo"'"'"''

check "repository workshop/regdemo มี tag 1.0" \
  sh -c 'curl -fsS http://localhost:5000/v2/workshop/regdemo/tags/list 2>/dev/null | grep -Fq '"'"'"1.0"'"'"''

check "พบ image localhost:5000/workshop/regdemo:1.0 ในเครื่อง" \
  image_exists "$verify_image"

# ป้องกันชื่อคอนเทนเนอร์ชั่วคราวซ้ำจากการรันครั้งก่อน
docker rm -f "$verify_container" >/dev/null 2>&1 || true

web_check_passed=false
if docker image inspect "$verify_image" >/dev/null 2>&1; then
  if docker run -d --name "$verify_container" -P "$verify_image" >/dev/null 2>&1; then
    host_port="$(docker port "$verify_container" 80/tcp 2>/dev/null | head -n 1 | sed 's/.*://')"
    if test -n "$host_port"; then
      for attempt in 1 2 3 4 5; do
        if curl -fsS "http://localhost:${host_port}/" 2>/dev/null | grep -Fq 'RELEASE'; then
          web_check_passed=true
          break
        fi
        sleep 1
      done
    fi
  fi
fi
check "รัน image ชั่วคราวแล้วหน้าเว็บมีคำว่า RELEASE" test "$web_check_passed" = true

# พิสูจน์ว่า docker tag แค่ "เพิ่มชื่อ" ไม่ได้สำเนา layers
# ทำแบบ self-contained: ตั้งชื่อชั่วคราวเอง เทียบ IMAGE ID แล้วถอนชื่อชั่วคราวคืน (ไม่แตะของผู้เรียน)
tag_proof=false
if docker image inspect "$verify_image" >/dev/null 2>&1; then
  if docker tag "$verify_image" "$verify_tmp_tag" >/dev/null 2>&1; then
    src_id="$(docker image inspect --format '{{.Id}}' "$verify_image" 2>/dev/null || true)"
    tmp_id="$(docker image inspect --format '{{.Id}}' "$verify_tmp_tag" 2>/dev/null || true)"
    if test -n "$src_id" && test "$src_id" = "$tmp_id"; then
      tag_proof=true
    fi
    docker rmi "$verify_tmp_tag" >/dev/null 2>&1 || true
  fi
fi
check "docker tag เพิ่มชื่อใหม่โดยไม่สำเนา image (IMAGE ID ตรงกัน)" test "$tag_proof" = true

if test "$fail_count" -eq 0; then
  printf 'ALL CHECKS PASSED\n'
  exit 0
fi

printf 'FAILED: %d check(s)\n' "$fail_count"
exit 1
