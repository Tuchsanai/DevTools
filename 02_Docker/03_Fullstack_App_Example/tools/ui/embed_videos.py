#!/usr/bin/env python3
"""ฝังวิดีโอ Remotion และภาพ poster ลง deck_build/_tail.html เป็น data URI

ไฟล์ต้นทางอยู่ที่ tools/media/ · รันซ้ำได้ · หลังรันต้อง build_deck.py ใหม่
"""
from __future__ import annotations

import base64
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
TAIL = ROOT / "deck_build/_tail.html"
MEDIA = ROOT / "tools/media"
CLIPS = ["v_name", "v_ship"]
MAX_MP4 = 500_000
MAX_PNG = 200_000


def uri(path: Path, mime: str, cap: int) -> str:
    raw = path.read_bytes()
    if len(raw) > cap:
        raise SystemExit(f"[FAIL] {path.name} {len(raw)} bytes เกินเพดาน {cap}")
    return f"data:{mime};base64," + base64.b64encode(raw).decode("ascii")


def main() -> int:
    assets: dict[str, str] = {}
    for name in CLIPS:
        assets[name] = uri(MEDIA / f"{name}.mp4", "video/mp4", MAX_MP4)
        assets[f"{name}_poster"] = uri(MEDIA / f"{name}.png", "image/png", MAX_PNG)

    tag = ('<script id="video-assets">Object.assign(window.ASSETS,'
           + json.dumps(assets, ensure_ascii=True, separators=(",", ":")) + ");</script>")
    html = TAIL.read_text(encoding="utf-8")
    existing = re.compile(r'<script id="video-assets">.*?</script>', re.DOTALL)
    if existing.search(html):
        html = existing.sub(tag, html, count=1)
    else:
        anchor = re.compile(r'(<script id="ui-assets">.*?</script>)', re.DOTALL)
        if not anchor.search(html):
            raise SystemExit("[FAIL] ไม่พบ <script id=\"ui-assets\">")
        html = anchor.sub(lambda m: m.group(1) + "\n" + tag, html, count=1)
    TAIL.write_text(html, encoding="utf-8")

    total = sum(len(v) for v in assets.values())
    print(f"[OK] ฝังวิดีโอ {len(CLIPS)} คลิป + poster {len(CLIPS)} ภาพ · รวม {total/1024/1024:.2f} MB (base64)")
    for k, v in assets.items():
        print(f"     {k:<16} {len(v)/1024:>8.1f} KB")
    print("     รัน python3 deck_build/build_deck.py ต่อ")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
