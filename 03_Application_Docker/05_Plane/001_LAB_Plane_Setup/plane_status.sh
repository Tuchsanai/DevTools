#!/bin/bash
# Optional shortcut to the official Prime monitor.
set -euo pipefail
exec sudo prime-cli monitor "$@"
