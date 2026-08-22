#!/usr/bin/env python3
"""ตรวจวงจรชีวิตวิดีโอในเด็ค — เล่นเฉพาะสไลด์ที่แสดง · หยุดและรีเซ็ตเมื่อออก · ตอนพิมพ์ต้องเป็นภาพนิ่ง"""
from __future__ import annotations

import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Fullstack_App_Example.html"
if "--deck" in sys.argv:
    DECK = Path(sys.argv[sys.argv.index("--deck") + 1]).resolve()


def main() -> int:
    fail: list[str] = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        pg = b.new_context(viewport={"width": 1440, "height": 900}).new_page()
        pg.goto(DECK.as_uri() + "#1", wait_until="load")
        pages = pg.evaluate("""() => Array.from(document.querySelectorAll('.slot'))
            .map((s, i) => s.querySelector('video[data-v]') ? i + 1 : 0).filter(Boolean)""")
        if not pages:
            print("[SKIP] เด็คนี้ไม่มีวิดีโอ")
            b.close()
            return 0
        def go(target: int) -> None:
            pg.keyboard.press("Home")
            pg.wait_for_timeout(120)
            for _ in range(target - 1):
                pg.keyboard.press("ArrowRight")
            pg.wait_for_timeout(200)

        for p in pages:
            go(p)
            key = pg.evaluate("() => { const v = document.querySelector('.slot.active video[data-v]');"
                              " return v ? v.getAttribute('data-v') : null; }")
            if key is None:
                fail.append(f"หน้า {p} ไม่พบ video[data-v] ในสไลด์ที่แสดงอยู่")
                continue
            try:
                pg.wait_for_function(
                    "() => { const v = document.querySelector('.slot.active video[data-v]');"
                    " return v && v.readyState >= 2; }", timeout=8000)
            except Exception:
                fail.append(f"หน้า {p} ({key}) โหลดวิดีโอไม่สำเร็จภายใน 8 วินาที")
                continue
            t0 = pg.evaluate("() => document.querySelector('.slot.active video[data-v]').currentTime")
            pg.wait_for_timeout(1200)
            st = pg.evaluate("""() => { const v = document.querySelector('.slot.active video[data-v]');
                return {t: v.currentTime, paused: v.paused, muted: v.muted, loop: v.loop}; }""")
            if st["t"] <= t0:
                fail.append(f"หน้า {p} ({key}) วิดีโอไม่เดิน (currentTime {t0} -> {st['t']})")
            if not st["muted"]:
                fail.append(f"หน้า {p} ({key}) วิดีโอไม่ได้ปิดเสียง")
            if not st["loop"]:
                fail.append(f"หน้า {p} ({key}) วิดีโอไม่ได้ตั้ง loop")
            pg.keyboard.press("ArrowRight")
            pg.wait_for_timeout(500)
            off = pg.evaluate(f"""() => {{ const v = document.querySelectorAll('.slot')[{p-1}].querySelector('video[data-v]');
                return {{t: v.currentTime, paused: v.paused}}; }}""")
            if not off["paused"]:
                fail.append(f"หน้า {p} ({key}) ออกจากสไลด์แล้ววิดีโอยังเล่นอยู่")
            if off["t"] > 0.3:
                fail.append(f"หน้า {p} ({key}) ออกจากสไลด์แล้ว currentTime ไม่ถูกรีเซ็ต ({off['t']})")

        # โหมดพิมพ์ : วิดีโอต้องถูกซ่อน และ poster ต้องแสดงแทน
        pg.goto(DECK.as_uri() + "#1", wait_until="load")
        pg.emulate_media(media="print")
        pg.wait_for_timeout(300)
        pr = pg.evaluate("""() => Array.from(document.querySelectorAll('video[data-v]')).map(v => ({
            vis: getComputedStyle(v).display,
            playing: !v.paused,
            poster: v.parentNode.querySelector('img.vposter')
                    ? getComputedStyle(v.parentNode.querySelector('img.vposter')).display : 'none',
        }))""")
        for i, m in enumerate(pr):
            if m["vis"] != "none":
                fail.append(f"โหมดพิมพ์: วิดีโอตัวที่ {i+1} ยังแสดงอยู่ ({m['vis']})")
            if m["playing"]:
                fail.append(f"โหมดพิมพ์: วิดีโอตัวที่ {i+1} ยังเล่นอยู่")
            if m["poster"] == "none":
                fail.append(f"โหมดพิมพ์: วิดีโอตัวที่ {i+1} ไม่มีภาพนิ่งแสดงแทน")
        pg.emulate_media(media="screen")
        b.close()

    if fail:
        print(f"[FAIL] {len(fail)} รายการ")
        for f in fail:
            print(f"  {f}")
        return 1
    print(f"[PASS] วิดีโอ {len(pages)} คลิป · เล่นเมื่อถึงสไลด์ · หยุดและรีเซ็ตเมื่อออก · ปิดเสียง · loop")
    print("[PASS] โหมดพิมพ์: วิดีโอถูกซ่อน แสดง poster แทน และไม่มีคลิปใดเล่น")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
