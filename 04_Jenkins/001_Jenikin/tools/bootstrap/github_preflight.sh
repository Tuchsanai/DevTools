#!/usr/bin/env bash
set -uo pipefail

fail() {
  printf '[github-preflight][ไม่ผ่าน] %s\n' "$*" >&2
  exit 1
}

command -v curl >/dev/null 2>&1 || fail 'ไม่พบคำสั่ง curl'
command -v python3 >/dev/null 2>&1 || fail 'ไม่พบคำสั่ง python3'

[ -n "${GITHUB_USER:-}" ] || fail 'กรุณา export GITHUB_USER ก่อนรัน'
[ -n "${GITHUB_TOKEN:-}" ] || fail 'กรุณา export GITHUB_TOKEN ก่อนรัน'

umask 077
temporary_directory="$(mktemp -d)" || fail 'สร้างพื้นที่ชั่วคราวไม่สำเร็จ'
trap 'rm -rf -- "$temporary_directory"' EXIT HUP INT TERM
headers_file="$temporary_directory/headers"
body_file="$temporary_directory/body"

printf '[github-preflight] กำลังตรวจบัญชีและสิทธิ์ของ GitHub token...\n'
if ! http_status="$(
  curl --silent --show-error \
    --request GET \
    --header "Authorization: Bearer ${GITHUB_TOKEN}" \
    --header 'Accept: application/vnd.github+json' \
    --header 'X-GitHub-Api-Version: 2022-11-28' \
    --dump-header "$headers_file" \
    --output "$body_file" \
    --write-out '%{http_code}' \
    'https://api.github.com/user'
)"; then
  fail 'เชื่อมต่อ GitHub API ไม่สำเร็จ'
fi

[ "$http_status" = '200' ] || fail "GitHub API ตอบ HTTP $http_status (ควรเป็น 200)"

if ! actual_login="$(
  python3 - "$body_file" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    value = json.load(handle)
login = value.get("login")
if not isinstance(login, str):
    raise SystemExit(1)
print(login)
PY
)"; then
  fail 'อ่านชื่อ login จากคำตอบ GitHub ไม่สำเร็จ'
fi

[ "$actual_login" = "$GITHUB_USER" ] || \
  fail "login จาก token คือ '$actual_login' แต่ GITHUB_USER คือ '$GITHUB_USER'"

oauth_scopes="$(
  awk '
    tolower($0) ~ /^x-oauth-scopes:/ {
      sub(/^[^:]*:[[:space:]]*/, "")
      sub(/\r$/, "")
      print
      exit
    }
  ' "$headers_file"
)"
[ -n "$oauth_scopes" ] || fail 'ไม่พบ header X-OAuth-Scopes; token นี้ไม่ผ่านสัญญา PAT classic ของแล็บ'

has_scope() {
  local required="$1"
  printf '%s\n' "$oauth_scopes" \
    | tr ',' '\n' \
    | sed 's/^[[:space:]]*//; s/[[:space:]]*$//' \
    | grep -Fxq "$required"
}

if has_scope 'repo'; then
  scope_profile='repo'
elif has_scope 'public_repo' && has_scope 'admin:repo_hook'; then
  scope_profile='public_repo + admin:repo_hook'
else
  fail 'scope ไม่ครบ: ต้องมี public_repo และ admin:repo_hook หรือมี repo'
fi

printf '[github-preflight][ผ่าน] login ตรงกับ GITHUB_USER และ scope ผ่านชุด %s\n' "$scope_profile"
exit 0
