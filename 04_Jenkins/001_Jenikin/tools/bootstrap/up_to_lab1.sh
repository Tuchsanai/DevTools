#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
ensure_lab1_state
printf '\n[assert] LAB 1 ready: Jenkins authenticated and first-freestyle exists\n'
