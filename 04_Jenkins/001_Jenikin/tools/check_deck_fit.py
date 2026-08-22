#!/usr/bin/env python3
"""Gate: no slide may push content outside its 1280x720 frame.

Loads the built deck with a headless browser, walks every page, and measures the
bounding box of every element inside the slide.  Anything that reaches past the
footer line (or off the left/right edge) is content the projector will cut off.

Usage: python3 tools/check_deck_fit.py [--shots DIR] [--deck FILE]
Exit 0 = PASS.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DECK = ROOT / "Jenkins_CICD_Docker_Slides.html"
FOOT = 38          # footer strip height, px
TOLERANCE = 4      # sub-pixel rounding slack, px

MEASURE = """
(() => {
  const slot = document.querySelector('.slot.active');
  if (!slot) return {error: 'no active slot'};
  const slide = slot.querySelector('.slide');
  const r = slide.getBoundingClientRect();
  const scale = r.width / 1280;
  const limitBottom = r.bottom - FOOT_PX * scale;
  const bad = [];
  slide.querySelectorAll('.body *').forEach(el => {
    const b = el.getBoundingClientRect();
    if (b.width === 0 && b.height === 0) return;
    const over = (b.bottom - limitBottom) / scale;
    const left = (r.left - b.left) / scale;
    const right = (b.right - r.right) / scale;
    // A box with overflow:hidden that is shorter than its own content shows no
    // overflow at all — it just silently eats the rest of the text.  That is the
    // failure this deck is most exposed to (code blocks under a tall screenshot),
    // so measure it directly rather than trusting the outer geometry.
    // Only a box that actually clips can hide text; an element with visible
    // overflow just spills, and a tight line-height makes scrollHeight exceed
    // clientHeight on perfectly fine headings.
    const cs = getComputedStyle(el);
    const clipped = cs.overflowY !== 'visible' ? Math.round((el.scrollHeight - el.clientHeight) / scale) : 0;
    const clipX = cs.overflowX !== 'visible' ? Math.round((el.scrollWidth - el.clientWidth) / scale) : 0;
    if (over > TOL || left > TOL || right > TOL || clipped > TOL || clipX > TOL) {
      bad.push({
        tag: el.tagName.toLowerCase(),
        cls: (el.className || '').toString().slice(0, 40),
        overBottom: Math.round(over), overLeft: Math.round(left), overRight: Math.round(right),
        clipped: clipped > TOL ? clipped : 0, clipX: clipX > TOL ? clipX : 0,
        text: (el.textContent || '').trim().slice(0, 60),
      });
    }
  });
  return {kind: slide.className.replace('slide', '').trim(), bad};
})()
""".replace("FOOT_PX", str(FOOT)).replace("TOL", str(TOLERANCE))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--deck", type=Path, default=DEFAULT_DECK)
    ap.add_argument("--shots", type=Path, default=None, help="save a PNG per slide into this directory")
    ap.add_argument("--only", type=str, default=None, help="page numbers to check, e.g. 25-40,55")
    args = ap.parse_args()

    from playwright.sync_api import sync_playwright

    wanted: set[int] | None = None
    if args.only:
        wanted = set()
        for part in args.only.split(","):
            if "-" in part:
                a, b = part.split("-")
                wanted.update(range(int(a), int(b) + 1))
            else:
                wanted.add(int(part))

    if args.shots:
        args.shots.mkdir(parents=True, exist_ok=True)

    problems: list[str] = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(args.deck.resolve().as_uri())
        page.wait_for_selector(".slot.active")
        total = page.evaluate("document.querySelectorAll('.slot').length")
        print(f"deck: {args.deck.name} · {total} slides")
        for i in range(1, total + 1):
            if wanted and i not in wanted:
                continue
            page.evaluate("n => { location.hash = '#page-' + n; }", i)
            page.wait_for_timeout(45)
            res = page.evaluate(MEASURE)
            if res.get("error"):
                problems.append(f"slide {i}: {res['error']}")
                continue
            for b in res["bad"]:
                where = []
                if b["overBottom"] > TOLERANCE:
                    where.append(f"ล้นล่าง {b['overBottom']}px")
                if b["overLeft"] > TOLERANCE:
                    where.append(f"ล้นซ้าย {b['overLeft']}px")
                if b["overRight"] > TOLERANCE:
                    where.append(f"ล้นขวา {b['overRight']}px")
                if b.get("clipped"):
                    where.append(f"เนื้อหาถูกตัดหาย {b['clipped']}px")
                if b.get("clipX"):
                    where.append(f"เนื้อหาถูกตัดด้านข้าง {b['clipX']}px")
                problems.append(
                    f"slide {i} ({res['kind']}): <{b['tag']} class=\"{b['cls']}\"> "
                    f"{', '.join(where)} — {b['text']!r}"
                )
            if args.shots:
                page.locator(".slot.active").screenshot(path=str(args.shots / f"page-{i:03d}.png"))
        browser.close()

    if problems:
        seen: set[str] = set()
        for p in problems:
            head = p.split(":")[0]
            if head in seen:
                continue
            seen.add(head)
            print(f"[FAIL] {p}")
        print(f"\nDECK FIT CHECK: FAIL ({len(seen)} slide(s) มีเนื้อหาล้นกรอบ)")
        return 1
    print("\nDECK FIT CHECK: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
