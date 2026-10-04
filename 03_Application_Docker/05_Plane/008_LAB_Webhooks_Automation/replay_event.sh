#!/bin/bash
# replay_event.sh — ส่ง event ล่าสุดจาก events.jsonl กลับเข้า hookwall อีกครั้ง (raw body + header เดิม)
#   bash replay_event.sh            → delivery id เดิม ⇒ hookwall ตอบ "duplicate ignored"
#   bash replay_event.sh --tamper   → แก้ body 1 ตัวอักษรแต่ใช้ลายเซ็นเดิม ⇒ 401 REJECTED (การ์ดแดงบนกำแพง)
set -euo pipefail
F=${EVENTS_FILE:-hookwall/data/events.jsonl}
LAST=$(grep '"status": "OK"' "$F" | tail -1 || true); [ -n "$LAST" ] || LAST=$(tail -1 "$F")
python3 - "${1:-}" "$LAST" <<'PY'
import base64, json, sys, urllib.request
mode, rec = sys.argv[1] if len(sys.argv) > 1 else "", json.loads(sys.argv[2])
raw = base64.b64decode(rec["raw_b64"])
if mode == "--tamper":
    raw = raw.replace(b'"action"', b'"actioN"', 1)   # แก้ 1 ตัวอักษร ลายเซ็นเดิมจึงไม่ตรง
h = {k: v for k, v in rec["headers"].items() if v}; h["Content-Type"] = "application/json"
req = urllib.request.Request("http://localhost:9000/hook", data=raw, headers=h, method="POST")
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        print("HTTP", r.status, r.read().decode())
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode())
PY
