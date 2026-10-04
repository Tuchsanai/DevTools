#!/bin/bash
# LAB 2 — what does Plane keep in Valkey (Redis-compatible cache)?  usage: bash valkey_tour.sh
# NOTE: docker compose exec -T reads stdin, so every call gets </dev/null — otherwise a loop over keys eats its own input.
V() { pc exec -T plane-redis valkey-cli "$@" </dev/null | tr -d '\r'; }
echo "== server";  V INFO server | grep -E '^(redis_version|valkey_version|uptime_in_seconds)'
echo "== how many keys?"; V DBSIZE
echo "== every key: type · TTL (seconds, -1 = never expires) · size"
mapfile -t KEYS < <(V --scan)
for k in "${KEYS[@]}"; do
  printf '%-45s %-7s ttl=%-6s %s bytes\n' "$k" "$(V TYPE "$k")" "$(V TTL "$k")" "$(V MEMORY USAGE "$k")"
done
echo "== value of a UUID key (issue_activity stores the request origin for 600 s)"
for k in "${KEYS[@]}"; do case "$k" in *-*-*-*-*) V GET "$k"; break;; esac; done
echo "== magic-link codes? (need SMTP → expected 0)"; V --scan --pattern 'magic_*' | wc -l
