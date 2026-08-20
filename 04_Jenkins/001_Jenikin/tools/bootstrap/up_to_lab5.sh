#!/usr/bin/env bash
# เตรียมสถานะ LAB 1-5; ต้องมี GITHUB_USER/GITHUB_TOKEN และ DOCKER_USER/DOCKER_TOKEN
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
ensure_lab5_state
printf '\n[assert] LAB 5 พร้อม: GitHub push ผ่าน smee สร้าง exactly one green webhook build; Poll SCM ปิดแล้ว\n'
