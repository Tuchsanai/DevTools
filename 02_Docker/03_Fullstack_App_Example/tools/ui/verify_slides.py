#!/usr/bin/env python3
"""เปิด deck ด้วย Playwright และตรวจทุกสไลด์โดยไม่อนุญาต request ภายนอก."""

from __future__ import annotations

import os
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import ConsoleMessage, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Fullstack_App_Example.html"
EXPECTED_SLIDES = 60
UI_KEYS = (
    "ui_github_code",
    "ui_swagger_created",
    "ui_web_new_card",
    "ui_hub_api_tags",
)


def main() -> int:
    console_errors: list[str] = []
    page_errors: list[str] = []
    requests: list[str] = []
    failures: list[str] = []
    shot_dir_value = os.environ.get("SLIDE_SHOT_DIR")
    shot_dir = Path(shot_dir_value).resolve() if shot_dir_value else None
    if shot_dir:
        shot_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        def on_console(message: ConsoleMessage) -> None:
            if message.type == "error":
                console_errors.append(message.text)

        page.on("console", on_console)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on("request", lambda request: requests.append(request.url))
        page.goto(DECK.as_uri() + "#1", wait_until="load")
        page.wait_for_function(
            "Array.from(document.querySelectorAll('img[data-a]')).every(i => i.complete && i.naturalWidth > 0)"
        )

        summary = page.evaluate(
            r"""([expected, keys]) => ({
              slots: document.querySelectorAll('.slot').length,
              total: document.getElementById('tot').textContent,
              lastPage: Array.from(document.querySelectorAll('.pg')).at(-1).textContent,
              overviewCards: document.querySelectorAll('#ov .oc').length,
              overviewLast: Array.from(document.querySelectorAll('#ov .oc .r')).at(-1).textContent,
              brokenImages: Array.from(document.images).filter(i => !i.complete || !i.naturalWidth).length,
              uiAssets: keys.map(k => typeof window.ASSETS[k] === 'string' && window.ASSETS[k].startsWith('data:image/png;base64,')),
              externalAttrs: Array.from(document.querySelectorAll('script[src],link[href],iframe[src],img[src]'))
                .map(e => e.getAttribute('src') || e.getAttribute('href'))
                .filter(v => v && /^(?:https?:)?\/\//i.test(v))
            })""",
            [EXPECTED_SLIDES, list(UI_KEYS)],
        )
        if summary["slots"] != EXPECTED_SLIDES:
            failures.append(f"จำนวนสไลด์ {summary['slots']} ไม่ใช่ {EXPECTED_SLIDES}")
        if summary["total"] != str(EXPECTED_SLIDES):
            failures.append("ตัวนับจำนวนหน้ารวมไม่ตรง")
        if summary["lastPage"] != f"{EXPECTED_SLIDES} / {EXPECTED_SLIDES}":
            failures.append("เลขหน้าสุดท้ายไม่ตรง")
        if summary["overviewCards"] != 10 or not summary["overviewLast"].endswith(f"–{EXPECTED_SLIDES} · 4 แผ่น"):
            failures.append(f"overview ไม่ครอบคลุมหน้าสุดท้าย: {summary['overviewLast']}")
        if summary["brokenImages"]:
            failures.append(f"มีภาพ render ไม่สำเร็จ {summary['brokenImages']} ใบ")
        if not all(summary["uiAssets"]):
            failures.append("UI asset ใหม่ไม่ได้เป็น PNG data URI ครบ")
        if summary["externalAttrs"]:
            failures.append(f"พบ attribute ภายนอก: {summary['externalAttrs']}")

        screenshot_pages = {23: "github", 36: "swagger", 43: "web", 55: "ship", 56: "hub"}
        page.keyboard.press("Home")
        for index in range(1, EXPECTED_SLIDES + 1):
            if index > 1:
                page.keyboard.press("ArrowRight")
            state = page.evaluate(
                """expected => {
                  const active = Array.from(document.querySelectorAll('.slot.active'));
                  const slot = active[0];
                  const slide = slot && slot.querySelector('.slide');
                  return {
                    active: active.length,
                    counter: document.getElementById('cur').textContent,
                    page: slot && slot.querySelector('.pg') ? slot.querySelector('.pg').textContent : '',
                    width: slide ? slide.offsetWidth : 0,
                    height: slide ? slide.offsetHeight : 0,
                    visibleText: slide ? slide.innerText.trim().length : 0
                  };
                }""",
                index,
            )
            if (
                state["active"] != 1
                or state["counter"] != str(index)
                or state["page"] != f"{index} / {EXPECTED_SLIDES}"
                or state["width"] != 1280
                or state["height"] != 720
                or state["visibleText"] == 0
            ):
                failures.append(f"หน้า {index} render/state ไม่ครบ: {state}")
            if shot_dir and index in screenshot_pages:
                page.locator(".slot.active .slide").screenshot(
                    path=str(shot_dir / f"{index:02d}-{screenshot_pages[index]}.png")
                )

        external_requests = []
        for url in requests:
            parsed = urlparse(url)
            if parsed.scheme in {"file", "data", "blob", "about"}:
                continue
            if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
                continue
            external_requests.append(url)
        if external_requests:
            failures.append(f"พบ request ออกนอกเครื่อง {len(external_requests)} รายการ")
        if console_errors:
            failures.append(f"console error {len(console_errors)} รายการ: {console_errors}")
        if page_errors:
            failures.append(f"page error {len(page_errors)} รายการ: {page_errors}")
        browser.close()

    if failures:
        for failure in failures:
            print(f"[FAIL] {failure}")
        return 1
    print(f"[PASS] render ครบ {EXPECTED_SLIDES} หน้า")
    print(f"[PASS] เลขหน้าและ overview สิ้นสุดที่ {EXPECTED_SLIDES}")
    print(f"[PASS] UI data URI ใหม่ {len(UI_KEYS)} ภาพโหลดครบ")
    print(f"[PASS] request ภายนอก 0 · console error 0 · page error 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
