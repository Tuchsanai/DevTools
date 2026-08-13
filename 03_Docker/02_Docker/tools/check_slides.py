#!/usr/bin/env python3
"""Visual QA for Docker_Week09_Slides.html.

For every slide: force it active, measure whether any element overflows the
1280x720 frame, and shoot a PNG into tools/qa/.
Overflow is what kills a deck on a projector, so it is reported per slide with
the offending element so it can be fixed at the source.
"""
import json
import os
import sys

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DECK = "file://" + os.path.join(ROOT, "Docker_Week09_Slides.html")
QA = os.path.join(HERE, "qa")

MEASURE = """
(k) => {
  const slots = document.querySelectorAll('.slot');
  slots.forEach((s, x) => s.classList.toggle('active', x === k));
  document.documentElement.style.setProperty('--s', 1);
  const slide = slots[k].querySelector('.slide');
  const box = slide.getBoundingClientRect();
  const bad = [];
  slide.querySelectorAll('*').forEach(el => {
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0) return;
    const dx = Math.round(r.right - box.right);
    const dy = Math.round(r.bottom - box.bottom);
    const dl = Math.round(box.left - r.left);
    if (dx > 1 || dy > 1 || dl > 1) {
      bad.push({tag: el.tagName.toLowerCase(), cls: el.className || '',
                over_right: dx, over_bottom: dy, over_left: dl,
                text: (el.textContent || '').trim().slice(0, 60)});
    }
    if (el.scrollHeight - el.clientHeight > 2 && getComputedStyle(el).overflow !== 'visible') {
      bad.push({tag: el.tagName.toLowerCase(), cls: el.className || '',
                clipped: el.scrollHeight - el.clientHeight,
                text: (el.textContent || '').trim().slice(0, 60)});
    }
  });
  const foot = slide.querySelector('.s-foot span');
  return {bad: bad.slice(0, 6), title: (slide.querySelector('h1,h2') || {}).textContent || '',
          section: foot ? foot.textContent : ''};
}
"""


def main():
    shoot = "--shots" in sys.argv
    os.makedirs(QA, exist_ok=True)
    problems = []
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=1)
        pg.goto(DECK, wait_until="load")
        pg.wait_for_timeout(1200)
        pg.wait_for_function(
            "Array.from(document.querySelectorAll('img[data-a]')).every(i=>i.complete&&i.naturalWidth>0)",
            timeout=30000)
        n = pg.evaluate("document.querySelectorAll('.slot').length")
        print("slides:", n)
        for k in range(n):
            res = pg.evaluate(MEASURE, k)
            pg.wait_for_timeout(45)
            if res["bad"]:
                problems.append({"slide": k + 1, **res})
            if shoot:
                el = pg.query_selector(".slot.active .slide")
                el.screenshot(path=os.path.join(QA, "s%02d.png" % (k + 1)))
        b.close()

    if problems:
        print("\n%d slide(s) with overflow / clipping:" % len(problems))
        for pr in problems:
            print("\n--- slide %d : %s [%s]" % (pr["slide"], pr["title"][:60], pr["section"]))
            for x in pr["bad"]:
                print("    ", json.dumps(x, ensure_ascii=False))
    else:
        print("\nno overflow on any slide ✓")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
