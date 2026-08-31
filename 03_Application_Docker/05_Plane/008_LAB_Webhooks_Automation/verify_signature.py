#!/usr/bin/env python3
"""verify_signature.py — คำนวณ HMAC-SHA256 ของ raw body ทุก event ใน events.jsonl ด้วย secret แล้วเทียบกับ X-Plane-Signature ที่ Plane ส่งมา
ใช้: python verify_signature.py hookwall/data/events.jsonl   (secret อ่านจาก ~/.plane_wh_secret หรือ env PLANE_WEBHOOK_SECRET)
"""
import base64, hashlib, hmac, json, os, sys
from pathlib import Path
secret = os.environ.get("PLANE_WEBHOOK_SECRET") or Path("~/.plane_wh_secret").expanduser().read_text().strip()
path = sys.argv[1] if len(sys.argv) > 1 else "hookwall/data/events.jsonl"
match = mismatch = 0
for line in open(path, encoding="utf-8"):
    r = json.loads(line)
    raw = base64.b64decode(r["raw_b64"])
    calc = hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest()
    sent = r["headers"].get("X-Plane-Signature", "")
    ok = hmac.compare_digest(calc, sent)
    match += ok; mismatch += (not ok)
    s = r.get("summary") or {}
    print(f"{'MATCH   ' if ok else 'MISMATCH'}  {r.get('event')}.{r.get('action')}  {s.get('key','')}  delivery {r.get('delivery','')[:8]}  sig {sent[:12]}…")
print(f"\n{match} match · {mismatch} mismatch  (สูตร: hmac.new(secret, raw_body, sha256).hexdigest())")
sys.exit(0 if mismatch == 0 else 1)
