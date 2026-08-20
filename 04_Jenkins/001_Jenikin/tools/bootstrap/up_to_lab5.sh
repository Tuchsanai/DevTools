#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
ensure_lab5_state
printf '\n[assert] LAB 5 ready: real push produced a new green webhook build; Poll SCM is off\n'
