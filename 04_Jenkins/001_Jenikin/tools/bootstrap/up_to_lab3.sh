#!/usr/bin/env bash
set -euo pipefail
source "$(cd "$(dirname "$0")" && pwd)/common.sh"
ensure_lab3_state
printf '\n[assert] LAB 3 ready: Docker socket, dockerhub credential, green job, and Hub manifest verified\n'
