#!/bin/bash
# Checks installation smoke only; does not assert completion of UI exercises.
set -euo pipefail
command -v prime-cli >/dev/null || { echo 'FAIL: prime-cli is not installed' >&2; exit 1; }
bash "$(dirname "$0")/wait_ready.sh"
echo 'PASS: Prime CLI installed and web/API reachable. Complete the UI checklist in readme.md separately.'
