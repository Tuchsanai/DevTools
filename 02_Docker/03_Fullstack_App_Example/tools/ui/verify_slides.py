#!/usr/bin/env python3
"""ตรวจโครงสร้างการนำทางของเด็ค — จำนวนหน้า เลขหน้า สารบัญตอน ภาพ UI และการเป็นไฟล์เดียว

ทุกค่าที่คาดหวังอ่านจาก DOM ไม่ hardcode เลขหน้า เพราะเด็คแตกสไลด์เพิ่มได้
ใช้: python3 tools/ui/verify_slides.py [--deck <path>] [--shots <dir>]
"""
from __future__ import annotations

import sys
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import ConsoleMessage, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Fullstack_App_Example.html"
if "--deck" in sys.argv:
    DECK = Path(sys.argv[sys.argv.index("--deck") + 1]).resolve()


def main() -> int:
    shot_dir = None
    if "--shots" in sys.argv:
        shot_dir = Path(sys.argv[sys.argv.index("--shots") + 1]).resolve()
        shot_dir.mkdir(parents=True, exist_ok=True)

    failures: list[str] = []
    console_errors: list[str] = []
    page_errors: list[str] = []
    requests: list[str] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_context(viewport={"width": 1440, "height": 900}).new_page()
        page.on("console", lambda m: console_errors.append(m.text) if m.type == "error" else None)
        page.on("pageerror", lambda e: page_errors.append(str(e)))
        page.on("request", lambda r: requests.append(r.url))
        page.goto(DECK.as_uri() + "#1", wait_until="load")
        page.wait_for_function(
            "Array.from(document.querySelectorAll('img[data-a]')).every(i => i.complete && i.naturalWidth > 0)"
        )

        s = page.evaluate(r"""() => {
          const slots = Array.from(document.querySelectorAll('.slot'));
          const secStarts = slots.map((s, i) => [s.getAttribute('data-sec'), i]).filter(x => x[0]);
          return {
            slots: slots.length,
            total: document.getElementById('tot').textContent,
            lastPage: Array.from(document.querySelectorAll('.pg')).at(-1).textContent,
            missingPg: slots.filter(s => !s.querySelector('.pg')).length,
            overviewCards: document.querySelectorAll('#ov .oc').length,
            overviewLast: Array.from(document.querySelectorAll('#ov .oc .r')).at(-1).textContent,
            sections: secStarts.length,
            lastSectionStart: secStarts.length ? secStarts.at(-1)[1] + 1 : 0,
            brokenImages: Array.from(document.images).filter(i => !i.complete || !i.naturalWidth).length,
            assetKeys: Object.keys(window.ASSETS || {}),
            usedKeys: Array.from(document.querySelectorAll('img[data-a]')).map(i => i.getAttribute('data-a'))
              .concat(Array.from(document.querySelectorAll('video[data-v]')).flatMap(v => {
                const k = v.getAttribute('data-v');
                return [k, k + '_poster'];
              })),
            nonDataAssets: Object.entries(window.ASSETS || {})
              .filter(([, v]) => typeof v !== 'string'
                              || !(v.startsWith('data:image/') || v.startsWith('data:video/')))
              .map(([k]) => k),
            external: Array.from(document.querySelectorAll(
                'script[src],link[href],iframe[src],img[src],video[src],source[src],audio[src]'))
              .map(e => e.getAttribute('src') || e.getAttribute('href'))
              .filter(v => v && /^(?:https?:)?\/\//i.test(v)),
            shotPages: Array.from(document.querySelectorAll('img[data-a]'))
              .map(i => slots.indexOf(i.closest('.slot')) + 1),
          };
        }""")

        n = s["slots"]
        if s["total"] != str(n):
            failures.append(f"ตัวนับจำนวนหน้ารวม {s['total']} ไม่ตรงกับ {n} สไลด์")
        if s["lastPage"] != f"{n} / {n}":
            failures.append(f"เลขหน้าสุดท้าย {s['lastPage']} ไม่ตรงกับ {n}")
        if s["missingPg"]:
            failures.append(f"สไลด์ที่ไม่มีช่องเลขหน้า {s['missingPg']} แผ่น")
        if s["overviewCards"] != s["sections"] + 1:
            failures.append(f"สารบัญมี {s['overviewCards']} การ์ด แต่มี {s['sections']} ตอน (+ เปิดเรื่อง)")
        want_last = f"สไลด์ {s['lastSectionStart']}–{n} · {n - s['lastSectionStart'] + 1} แผ่น"
        if s["overviewLast"].strip() != want_last:
            failures.append(f"สารบัญตอนสุดท้ายเขียน \"{s['overviewLast'].strip()}\" ควรเป็น \"{want_last}\"")
        if s["brokenImages"]:
            failures.append(f"ภาพ render ไม่สำเร็จ {s['brokenImages']} ใบ")
        if s["nonDataAssets"]:
            failures.append(f"ASSETS ที่ไม่ใช่ data URI: {s['nonDataAssets']}")
        missing = sorted(set(s["usedKeys"]) - set(s["assetKeys"]))
        if missing:
            failures.append(f"สไลด์อ้าง ASSETS ที่ไม่มี: {missing}")
        unused = sorted(set(s["assetKeys"]) - set(s["usedKeys"]))
        if unused:
            failures.append(f"ASSETS ที่ไม่มีสไลด์ไหนใช้: {unused}")
        if s["external"]:
            failures.append(f"attribute ที่ชี้ออกนอกไฟล์: {s['external'][:3]}")

        page.keyboard.press("Home")
        for i in range(1, n + 1):
            if i > 1:
                page.keyboard.press("ArrowRight")
            st = page.evaluate("""() => {
              const a = Array.from(document.querySelectorAll('.slot.active'));
              const slide = a[0] && a[0].querySelector('.slide');
              return {n: a.length, cur: document.getElementById('cur').textContent,
                      w: slide ? slide.offsetWidth : 0, h: slide ? slide.offsetHeight : 0,
                      len: slide ? slide.innerText.trim().length : 0};
            }""")
            if st["n"] != 1 or st["cur"] != str(i) or st["w"] != 1280 or st["h"] != 720 or st["len"] == 0:
                failures.append(f"หน้า {i} render/state ไม่ครบ: {st}")
            if shot_dir and i in s["shotPages"]:
                page.locator(".slot.active .slide").screenshot(path=str(shot_dir / f"{i:03d}.png"))
        browser.close()

    ext = [u for u in requests
           if urlparse(u).scheme not in {"file", "data", "blob", "about"}
           and urlparse(u).hostname not in {"localhost", "127.0.0.1", "::1"}]
    if ext:
        failures.append(f"request ออกนอกเครื่อง {len(ext)} รายการ")
    if console_errors:
        failures.append(f"console error {len(console_errors)}: {console_errors[:3]}")
    if page_errors:
        failures.append(f"page error {len(page_errors)}: {page_errors[:3]}")

    if failures:
        print(f"[FAIL] {len(failures)} รายการ")
        for f in failures:
            print(f"  {f}")
        return 1
    print(f"[PASS] render ครบ {n} หน้า · เลขหน้าและสารบัญ {s['sections']} ตอนตรงกัน")
    print(f"[PASS] ภาพ data URI {len(s['assetKeys'])} ก้อน ใช้ครบ · request ภายนอก 0 · console error 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
