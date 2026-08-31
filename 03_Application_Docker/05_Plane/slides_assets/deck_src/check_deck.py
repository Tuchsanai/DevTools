#!/usr/bin/env python3
"""Render the deck headlessly: catch JS errors, broken images, and slides whose content overflows the 1280x720 frame.

  python3 check_deck.py            # checks only
  python3 check_deck.py 1 5 12     # also screenshot those slide numbers into ./.deckshots/
  python3 check_deck.py all        # screenshot every slide
"""
import os, sys
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
DECK = os.path.abspath(os.path.join(HERE, "..", "..", "Plane_Agile_Slides.html"))
SHOTS = os.path.join(HERE, ".deckshots")
os.makedirs(SHOTS, exist_ok=True)
args = sys.argv[1:]
if "--deck" in args:
    i = args.index("--deck"); DECK = os.path.abspath(args[i + 1]); del args[i:i + 2]
if "--shots" in args:
    i = args.index("--shots"); SHOTS = os.path.abspath(args[i + 1]); del args[i:i + 2]
    os.makedirs(SHOTS, exist_ok=True)
want_all = args == ["all"]
want = [] if want_all else [int(x) for x in args]

errors = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 760})
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
    pg.goto("file://" + DECK, wait_until="load", timeout=120000)
    pg.wait_for_timeout(2500)

    n = pg.evaluate("document.querySelectorAll('.slot').length")
    print(f"slides: {n}")

    bad_img = pg.evaluate("""() => {
        const out = [];
        document.querySelectorAll('img').forEach((im, i) => {
            if (!im.src) out.push('no src: ' + (im.dataset.a || i));
            else if (im.complete && im.naturalWidth === 0) out.push('broken: ' + (im.dataset.a || i));
        });
        return out;
    }""")
    print("broken images:", bad_img or "none")

    overflow = []
    for i in range(n):
        pg.evaluate(f"location.hash = '#{i+1}'")
        pg.wait_for_timeout(150)
        active = pg.evaluate("Array.from(document.querySelectorAll('.slot')).findIndex(s => s.classList.contains('active'))")
        if active != i:
            errors.append(f"navigation: asked for slide {i+1} but active is {active+1}")
        o = pg.evaluate("""() => {
            const s = document.querySelector('.slot.active .slide');
            if (!s) return null;
            const body = s.querySelector('.s-body');
            if (!body) return null;
            const sb = s.getBoundingClientRect();
            const foot = s.querySelector('.s-foot');
            const limit = foot ? foot.getBoundingClientRect().top : sb.bottom;
            let over = 0, wide = 0;
            body.querySelectorAll('*').forEach(el => {
                if (!el.getClientRects().length) return;
                const r = el.getBoundingClientRect();
                over = Math.max(over, r.bottom - limit);
                wide = Math.max(wide, r.right - sb.right, sb.left - r.left);
            });
            over = Math.max(over, body.scrollHeight - body.clientHeight);
            return {over: Math.round(over), wide: Math.round(wide)};
        }""")
        if o and (o["over"] > 4 or o["wide"] > 4):
            overflow.append((i + 1, o))
    print("overflowing slides:", overflow or "none")

    targets = range(1, n + 1) if want_all else (want or [1])
    for k in targets:
        pg.evaluate(f"location.hash = '#{k}'")
        pg.wait_for_timeout(350)
        pg.screenshot(path=f"{SHOTS}/slide-{k:03d}.png")
    print("js errors:", errors or "none")
    b.close()
sys.exit(1 if (bad_img or overflow or errors) else 0)
