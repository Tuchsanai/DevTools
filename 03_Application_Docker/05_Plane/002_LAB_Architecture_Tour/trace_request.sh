#!/bin/bash
# LAB 2 — trace 6 URL prefixes through the Caddy proxy and print "signatures" of the upstream that answered.
# Caddy in the plane-proxy container has NO access log, so the response itself is our evidence:
#   status code · Content-Type · first 60 bytes of the body
# usage: bash trace_request.sh [base_url]   (default http://localhost:8080)
BASE=${1:-http://localhost:8080}
printf '%-26s %-5s %-32s %s\n' "PATH" "CODE" "CONTENT-TYPE" "FIRST 60 BYTES"
printf '%-26s %-5s %-32s %s\n' "----" "----" "------------" "--------------"
for p in / /god-mode/ /spaces/ /api/instances/ /uploads/does-not-exist /live/health; do
  tmp=$(mktemp)
  hdr=$(curl -s -o "$tmp" -D - "$BASE$p" --max-time 10)
  code=$(printf '%s' "$hdr" | head -1 | awk '{print $2}')
  ctype=$(printf '%s' "$hdr" | grep -i '^content-type:' | head -1 | cut -d' ' -f2- | tr -d '\r' | cut -c1-32)
  body=$(head -c 60 "$tmp" | tr '\n\r\t' '   ')
  printf '%-26s %-5s %-32s %s\n' "$p" "${code:-ERR}" "${ctype:--}" "$body"
  rm -f "$tmp"
done
