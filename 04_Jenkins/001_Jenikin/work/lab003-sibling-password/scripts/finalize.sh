#!/bin/bash
# Run after the coordinator creates CAPTURE_DONE. Owner: yolo3.
# 1) bring captures/diagrams into images/  2) build+verify README while the admin password file still exists (leak check)
# 3) run the README cleanup block and remove every run resource  4) rebuild+verify with cleanup evidence  5) prove nothing is left
set -euo pipefail
W=$(cd "$(dirname "$0")/.." && pwd); cd "$W"
[ -f CAPTURE_DONE ] || { echo "CAPTURE_DONE not found: captures still pending" >&2; exit 3; }
. state.env
python3 scripts/integrate.py
python3 scripts/build_readme.py
python3 scripts/verify_readme.py > out/verify-before-cleanup.txt || { cat out/verify-before-cleanup.txt; exit 1; }
./scripts/lab.sh cleanup
python3 scripts/build_readme.py
python3 scripts/verify_readme.py > out/verify-final.txt || { cat out/verify-final.txt; exit 1; }
(cd ../.. && git diff --check -- 003_LAB_Docker_Build_Push/README.md 003_LAB_Docker_Build_Push/Jenkinsfile)
echo "leftovers (must be empty):"
docker ps -a --format '{{.Names}}' | grep -E "lab003-$H" || true
docker network ls --format '{{.Name}}' | grep -E "lab003-$H" || true
docker volume ls --format '{{.Name}}' | grep -E "lab003-$H" || true
ls private
tail -3 out/verify-final.txt
