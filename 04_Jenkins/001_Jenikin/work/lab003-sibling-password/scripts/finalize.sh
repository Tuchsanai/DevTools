#!/bin/bash
# Post-cleanup rebuild + verification. Owner: yolo3. Run resources are already removed (state.c23096.done.env,
# run-state.json); this re-integrates images, rebuilds the README from recorded evidence and runs every check.
set -euo pipefail
W=$(cd "$(dirname "$0")/.." && pwd); cd "$W"
python3 scripts/integrate.py
python3 scripts/build_readme.py
python3 scripts/verify_readme.py > out/verify-final.txt || { grep -v '^OK' out/verify-final.txt; exit 1; }
python3 scripts/secret_scan.py | tee out/secret-scan-final.txt
# whitespace check on the files this work owns (catfood-shop/app/globals.css has a pre-existing CRLF change, not ours)
(cd ../.. && git diff --check -- 003_LAB_Docker_Build_Push/README.md 003_LAB_Docker_Build_Push/Jenkinsfile && echo "git diff --check: clean")
! grep -nE '[[:space:]]+$' ../../003_LAB_Docker_Build_Push/LAB003_FINAL_REPORT.md REPORT.md README.tmpl.md captures.json scripts/*.py scripts/*.sh || { echo "trailing whitespace" >&2; exit 1; }
echo "leftovers (must be empty):"
docker ps -a --format '{{.Names}}' | grep -E 'lab003-(c23096|326752)' || true
docker network ls --format '{{.Name}}' | grep -E 'lab003-(c23096|326752)' || true
docker volume ls --format '{{.Name}}' | grep -E 'lab003-(c23096|326752)' || true
ls -A private
tail -1 out/verify-final.txt
