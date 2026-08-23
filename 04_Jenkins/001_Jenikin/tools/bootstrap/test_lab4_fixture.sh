#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=common.sh
source "$HERE/common.sh"

temporary_directory="$(mktemp -d)"
trap 'rm -rf -- "$temporary_directory"' EXIT
git init -q --bare "$temporary_directory/origin.git"
git init -q -b main "$temporary_directory/seed"
stage_hello_ci_fixture "$temporary_directory/seed"
git -C "$temporary_directory/seed" add --pathspec-from-file="$HERE/fixtures/hello-ci.files"
git -C "$temporary_directory/seed" \
  -c user.name=Student -c user.email=student@example.invalid \
  commit -q -m 'Clean isolated LAB 4 fixture'
git -C "$temporary_directory/seed" remote add origin "$temporary_directory/origin.git"
git -C "$temporary_directory/seed" push -q -u origin main
git -C "$temporary_directory/origin.git" symbolic-ref HEAD refs/heads/main
git clone -q "$temporary_directory/origin.git" "$temporary_directory/assert"

while IFS= read -r relative || [ -n "$relative" ]; do
  [ -s "$temporary_directory/assert/$relative" ] || {
    printf '[fixture][FAIL] missing or empty: %s\n' "$relative" >&2
    exit 1
  }
  printf '[fixture][PASS] %s\n' "$relative"
done <"$HERE/fixtures/hello-ci.files"
test -x "$temporary_directory/assert/hello.sh"
test "$(git -C "$temporary_directory/assert" rev-list --count HEAD)" -eq 1
printf '[fixture] RESULT: PASS (isolated local bare origin; public repo untouched)\n'
