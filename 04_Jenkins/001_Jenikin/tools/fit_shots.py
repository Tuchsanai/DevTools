#!/usr/bin/env python3
"""Size every screenshot panel to the picture it actually holds.

`.shot` uses object-fit:contain, so a box whose aspect ratio does not match the
capture letterboxes it: the slide looks empty and the UI text shrinks below
readability.  This computes, for each panel, the height at which the box exactly
hugs its image at that column's width, clamps it to what the slide can spare,
then converges with tools/check_deck_fit.py so nothing overflows or gets clipped.

Usage: python3 tools/fit_shots.py [--rounds 5] [--min 150]
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "tools" / "slides_src.html"
DECK = ROOT / "Jenkins_CICD_Docker_Slides.html"
US = "␟"
FOOT = 38

# usable widths inside .body (1280 - 2*58 padding = 1164)
BODY_W = 1164
COL_W = {
    "duo": (BODY_W - 18) / 2,          # .duo = two equal columns, gap 18
    "shotwrap": (BODY_W - 24) * 1.32 / 2,  # .shotwrap = 1.32fr .68fr, gap 24
    "plain": BODY_W,
}

SHOT_RE = re.compile(r'<div class="shot([^"]*)" style="height:(\d+)px">\s*<img[^>]*data-asset="([^"]+)"')

SLACK_JS = """
(() => {
  const slide = document.querySelector('.slot.active .slide');
  const body = slide.querySelector('.body');
  const r = slide.getBoundingClientRect();
  const scale = r.width / 1280;
  const limit = r.bottom - %d * scale;
  let lowest = -Infinity;
  body.querySelectorAll('*').forEach(el => {
    const b = el.getBoundingClientRect();
    if (b.width === 0 && b.height === 0) return;
    if (b.bottom > lowest) lowest = b.bottom;
  });
  return {slack: lowest === -Infinity ? 0 : Math.floor((limit - lowest) / scale)};
})()
""" % FOOT


def slides(text: str) -> list[str]:
    block = text.split('<script id="slideData" type="text/plain">')[1].split("</script>")[0].strip()
    return block.split("\n")


def put(text: str, lines: list[str]) -> str:
    old = text.split('<script id="slideData" type="text/plain">')[1].split("</script>")[0].strip()
    return text.replace(old, "\n".join(lines), 1)


def container(record: str) -> str:
    if 'class="duo"' in record:
        return "duo"
    if 'class="shotwrap"' in record:
        return "shotwrap"
    return "plain"


_aspect: dict[str, float] = {}


def aspect(rel: str) -> float:
    if rel not in _aspect:
        with Image.open(ROOT / rel) as im:
            _aspect[rel] = im.width / im.height
    return _aspect[rel]


def natural_heights(record: str) -> list[int]:
    """height at which each panel exactly hugs its picture, at this column width"""
    width = COL_W[container(record)]
    return [round(width / aspect(m.group(3))) for m in SHOT_RE.finditer(record)]


def set_heights(record: str, heights: list[int]) -> str:
    it = iter(heights)
    return SHOT_RE.sub(lambda m: m.group(0).replace(f'height:{m.group(2)}px', f'height:{next(it)}px', 1), record)


def current_heights(record: str) -> list[int]:
    return [int(m.group(2)) for m in SHOT_RE.finditer(record)]


def rebuild() -> None:
    subprocess.run([sys.executable, str(ROOT / "tools" / "embed_assets.py")], check=True, capture_output=True)


def measure(pages: list[int]) -> dict[int, int]:
    from playwright.sync_api import sync_playwright

    out: dict[int, int] = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(DECK.resolve().as_uri())
        page.wait_for_selector(".slot.active")
        for i in pages:
            page.evaluate("n => { location.hash = '#page-' + n; }", i)
            page.wait_for_timeout(40)
            out[i] = page.evaluate(SLACK_JS)["slack"]
        browser.close()
    return out


def failing() -> list[int]:
    proc = subprocess.run([sys.executable, str(ROOT / "tools" / "check_deck_fit.py")],
                          capture_output=True, text=True)
    return sorted({int(m.group(1)) for m in re.finditer(r"^\[FAIL\] slide (\d+)", proc.stdout, re.M)})


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--rounds", type=int, default=5)
    ap.add_argument("--min", type=int, default=150, help="ความสูงต่ำสุดของกล่องภาพ")
    args = ap.parse_args()

    # 1 · start every panel at the size that exactly fits its picture
    text = SRC.read_text(encoding="utf-8")
    lines = slides(text)
    pages = [i for i, l in enumerate(lines, 1) if SHOT_RE.search(l)]
    if not pages:
        print("ไม่มีสไลด์ที่มีภาพ")
        return 0
    for i in pages:
        lines[i - 1] = set_heights(lines[i - 1], natural_heights(lines[i - 1]))
    SRC.write_text(put(text, lines), encoding="utf-8")
    rebuild()
    print(f"ตั้งกล่องภาพตามสัดส่วนภาพจริง {len(pages)} สไลด์")

    # 2 · shrink whatever no longer fits, proportionally, until the deck is clean
    for rnd in range(1, args.rounds + 1):
        bad = failing()
        if not bad:
            break
        text = SRC.read_text(encoding="utf-8")
        lines = slides(text)
        touched = 0
        for i in bad:
            hs = current_heights(lines[i - 1])
            if not hs:
                continue
            slack_needed = 26 if rnd == 1 else 20
            new = [max(args.min, h - slack_needed) for h in hs]
            if new == hs:
                continue
            lines[i - 1] = set_heights(lines[i - 1], new)
            touched += 1
        if not touched:
            print(f"[FAIL] รอบ {rnd}: ยังมีสไลด์ล้นแต่ย่อกล่องภาพต่อไม่ได้: {bad}")
            return 1
        SRC.write_text(put(text, lines), encoding="utf-8")
        rebuild()
        print(f"รอบ {rnd}: ย่อกล่องภาพ {touched} สไลด์ ({bad})")

    # 3 · give leftover slack back to the panels, never past their natural size
    for rnd in range(1, args.rounds + 1):
        text = SRC.read_text(encoding="utf-8")
        lines = slides(text)
        pages = [i for i, l in enumerate(lines, 1) if SHOT_RE.search(l)]
        slack = measure(pages)
        grown = 0
        for i in pages:
            hs = current_heights(lines[i - 1])
            nat = natural_heights(lines[i - 1])
            room = min(nat[k] - hs[k] for k in range(len(hs)))
            gain = min(slack[i] * 2 - 6, room)
            if gain < 10:
                continue
            lines[i - 1] = set_heights(lines[i - 1], [h + gain for h in hs])
            grown += 1
        if not grown:
            print(f"รอบคืนพื้นที่ {rnd}: ไม่มีอะไรให้ขยายแล้ว")
            break
        SRC.write_text(put(text, lines), encoding="utf-8")
        rebuild()
        print(f"รอบคืนพื้นที่ {rnd}: ขยาย {grown} สไลด์")
        if failing():
            continue

    for attempt in range(6):
        bad = failing()
        if not bad:
            print("ทุกสไลด์อยู่ในกรอบและไม่มีเนื้อหาถูกตัด")
            return 0
        text = SRC.read_text(encoding="utf-8")
        lines = slides(text)
        for i in bad:
            hs = current_heights(lines[i - 1])
            if hs:
                lines[i - 1] = set_heights(lines[i - 1], [max(args.min, h - 20) for h in hs])
        SRC.write_text(put(text, lines), encoding="utf-8")
        rebuild()
        print(f"ปรับท้าย: ย่อ {len(bad)} สไลด์ {bad}")
    print("[FAIL] ยังมีสไลด์ล้นกรอบ")
    return 1


if __name__ == "__main__":
    sys.exit(main())
