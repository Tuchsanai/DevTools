#!/usr/bin/env python3
"""Render the deck headlessly: catch JS errors, unresolved images, and slides whose content overflows the 1280x720 frame."""
import sys
from playwright.sync_api import sync_playwright

DECK = "/home/workspace/DevTools/03_Application_Docker/03_Monitoring/Monitoring_Prometheus_Grafana_Slides.html"
SHOTS = "/tmp/claude-0/-home-workspace-DevTools-03-Application-Docker/1d810596-9f3a-4bb6-9707-090635d8d448/scratchpad/deckshots"

import os
os.makedirs(SHOTS, exist_ok=True)
want = [int(x) for x in sys.argv[1:]] if len(sys.argv) > 1 else []

errors = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 760})
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
    pg.goto("file://" + DECK, wait_until="load", timeout=60000)
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

    # overflow check: does any slide's content exceed the fixed 1280x720 frame?
    overflow = []
    for i in range(n):
        pg.evaluate(f"location.hash = '#{i+1}'")
        pg.wait_for_timeout(120)
        # code blocks clip silently (overflow:hidden), so compare real geometry against the
        # usable frame: the slide is 1280x720 with a 42px footer at the bottom.
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

    for k in (want or [1]):
        pg.evaluate(f"location.hash = '#{k}'")
        pg.wait_for_timeout(500)
        pg.screenshot(path=f"{SHOTS}/slide-{k:02d}.png")
    print("js errors:", errors or "none")
    b.close()
