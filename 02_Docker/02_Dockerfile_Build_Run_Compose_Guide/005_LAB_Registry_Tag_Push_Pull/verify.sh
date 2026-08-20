#!/usr/bin/env bash

# เปิดใช้การแจ้งเตือนเมื่อมีการอ้างถึงตัวแปรที่ยังไม่ได้กำหนด แต่ไม่หยุดเมื่อ check ใดล้มเหลว
set -u

fail_count=0
verify_container="regdemo-verify"
verify_tmp_tag="regdemo:verify-tmp"
hub_user="${DOCKER_USER:-}"
verify_image="${hub_user}/regdemo:1.0"

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

# ลบเฉพาะของชั่วคราวของสคริปต์เมื่อสคริปต์จบ โดยไม่แตะ image หรือ repository ของผู้เรียน
cleanup() {
  docker rm -f "$verify_container" >/dev/null 2>&1 || true
  docker rmi "$verify_tmp_tag" >/dev/null 2>&1 || true
}
trap cleanup EXIT

# ถาม Docker Hub ว่า tag ที่ระบุชี้ไป digest ไหน (repository ที่เป็น public ถามได้โดยไม่ต้องล็อกอิน)
hub_digest() {
  curl -fsS --max-time 20 \
    "https://hub.docker.com/v2/repositories/${hub_user}/regdemo/tags/1.0/" 2>/dev/null |
    python3 -c 'import sys, json; print(json.load(sys.stdin)["digest"])' 2>/dev/null
}

if test -z "$hub_user"; then
  printf '\n%s\n' "[HINT] ยังไม่ได้ตั้งตัวแปร DOCKER_USER"
  printf '%s\n\n' "       สั่ง  export DOCKER_USER=<ชื่อบัญชี Docker Hub ของคุณ>  ก่อนแล้วรันสคริปต์ใหม่"
fi

check "c1 พบไฟล์ Dockerfile" test -f Dockerfile
check "c2 พบไฟล์ site/index.html" test -f site/index.html
check "c3 พบไฟล์ site_v2/index.html" test -f site_v2/index.html
check "c4 ตั้งตัวแปร DOCKER_USER แล้ว" test -n "$hub_user"

check "c5 พบ image \$DOCKER_USER/regdemo:1.0 ในเครื่อง" image_exists "$verify_image"

# ถามครั้งเดียวแล้วเก็บผลไว้ใช้ทั้งสองข้อ เพื่อไม่ยิง API ซ้ำ
remote_digest="$(hub_digest)"
local_digests="$(docker image inspect --format '{{range .RepoDigests}}{{println .}}{{end}}' "$verify_image" 2>/dev/null)"

check "c6 repository \$DOCKER_USER/regdemo บน Docker Hub มี tag 1.0" \
  test -n "$remote_digest"

digest_match=false
if test -n "$remote_digest"; then
  case "$local_digests" in
    *"$remote_digest"*) digest_match=true ;;
  esac
fi
check "c7 digest บน Docker Hub ตรงกับ image ในเครื่อง" test "$digest_match" = true

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
check "c8 รัน image ชั่วคราวแล้วหน้าเว็บมีคำว่า RELEASE" test "$web_check_passed" = true

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
check "c9 docker tag เพิ่มชื่อใหม่โดยไม่สำเนา image (IMAGE ID ตรงกัน)" test "$tag_proof" = true

if test "$fail_count" -eq 0; then
  printf 'ALL CHECKS PASSED\n'
  exit 0
fi

printf 'FAILED: %d check(s)\n' "$fail_count"
exit 1
