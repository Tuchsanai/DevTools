#!/bin/bash
# auth_rate_limit.sh — ยิง sign-in ผิดรหัส 11 ครั้งติดกัน เพื่อดู AUTHENTICATION_RATE_LIMIT (10/minute) ทำงาน
# Plane ตอบ endpoint นี้ด้วย 302 เสมอ (redirect กลับหน้า sign-in พร้อม error_message ใน URL) จึงต้องอ่าน redirect URL ไม่ใช่ status code
# ใช้: bash auth_rate_limit.sh [email]   (ค่าเริ่มต้น nobody@example.com — ไม่กระทบบัญชีจริง)
EMAIL=${1:-nobody@example.com}
B=http://localhost:8080
CJ=$(mktemp)
CSRF=$(curl -s -c "$CJ" "$B/auth/get-csrf-token/" | python3 -c 'import sys,json; print(json.load(sys.stdin)["csrf_token"])')
for i in $(seq 1 11); do
  out=$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' -b "$CJ" -H "Referer: $B/" -H "Origin: $B" \
    --data-urlencode "csrfmiddlewaretoken=$CSRF" --data-urlencode "email=$EMAIL" --data-urlencode "password=wrong-password-$i" \
    "$B/auth/sign-in/")
  code=${out%% *}; url=${out#* }
  msg=$(printf '%s' "$url" | sed -n 's/.*error_message=\([^&]*\).*/\1/p')
  printf 'attempt %2d → HTTP %s  %s\n' "$i" "$code" "${msg:-$url}"
done
rm -f "$CJ"
