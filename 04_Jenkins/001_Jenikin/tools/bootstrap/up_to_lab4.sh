#!/usr/bin/env bash
# เตรียมสถานะ LAB 1-4; ต้องมี GITHUB_USER/GITHUB_TOKEN และ DOCKER_USER/DOCKER_TOKEN
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
ensure_lab4_state
printf '\n[assert] LAB 4 พร้อม: public GitHub hello-ci/main, ownership marker, Poll SCM และ green SCM build ผ่าน\n'
