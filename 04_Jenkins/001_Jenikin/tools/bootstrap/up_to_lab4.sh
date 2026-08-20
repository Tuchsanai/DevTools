#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
ensure_lab4_state
printf '\n[assert] LAB 4 ready: public hello-ci/main, canonical Gitea, Poll SCM, and green SCM job verified\n'
