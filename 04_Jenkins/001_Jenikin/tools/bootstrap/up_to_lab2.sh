#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
ensure_lab2_state
printf '\n[assert] LAB 2 ready: first-pipeline last build is SUCCESS\n'
