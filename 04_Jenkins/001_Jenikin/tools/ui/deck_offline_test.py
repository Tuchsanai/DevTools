#!/usr/bin/env python3
"""Executable U7 acceptance test for the single-file offline slide deck."""

from __future__ import annotations

import sys
import time
from pathlib import Path

from playwright.sync_api import ConsoleMessage, Page, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
DECK = ROOT / "Jenkins_CICD_Docker_Slides.html"
LOGS = ROOT / "logs"
EXPECTED_PAGES = 80
EXPECTED_COMPOSITIONS = {
    "mo-intro",
    "mo-manual-vs-ci",
    "mo-dood-socket",
    "mo-polling-vs-webhook",
    "mo-pipeline-flow",
}
EXPECTED_EMBEDDED_ASSETS = [
    "slides_assets/motion/mo_intro.mp4",
    "slides_assets/motion/mo_manual_vs_ci.mp4",
    "slides_assets/lab1_unlock.png",
    "slides_assets/lab1_plugins.png",
    "slides_assets/lab1_dashboard.png",
    "slides_assets/lab1_first_build.png",
    "slides_assets/lab2_params.png",
    "slides_assets/lab2_pipeline_graph.png",
    "slides_assets/motion/mo_dood_socket.mp4",
    "slides_assets/lab3_pipeline_docker.png",
    "slides_assets/lab3_push_log.png",
    "slides_assets/lab3_hub_tags.png",
    "slides_assets/lab4_s03_github_repo_files.png",
    "slides_assets/lab4_s05_jenkins_scm_config.png",
    "slides_assets/lab4_s08_git_polling_log.png",
    "slides_assets/motion/mo_polling_vs_webhook.mp4",
    "slides_assets/lab5_s04c_gwt_token_cause.png",
    "slides_assets/lab5_s05_gwt_filter.png",
    "slides_assets/lab5_s08_smee_push.png",
    "slides_assets/lab5_s09_github_push_build.png",
    "slides_assets/motion/mo_pipeline_flow.mp4",
    "slides_assets/lab6_pipeline_full.png",
    "slides_assets/lab6_app_v1.png",
    "slides_assets/lab6_app_v2.png",
    "slides_assets/lab6_hub_tags.png",
]
LEGACY_SCREENSHOT_ASSETS = {
    "slides_assets/lab4_gitea_repo.png",
    "slides_assets/lab4_jenkins_scm.png",
    "slides_assets/lab5_webhook_config.png",
    "slides_assets/lab5_delivery.png",
    "slides_assets/lab4_poll_build.png",
    "slides_assets/lab5_auto_build.png",
}


def check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[deck][PASS] {message}", flush=True)


def capture(page: Page, name: str) -> None:
    target = LOGS / name
    page.screenshot(path=str(target))
    print(f"[deck] screenshot: {target.relative_to(ROOT)}", flush=True)


def main() -> int:
    LOGS.mkdir(exist_ok=True)
    uri = DECK.resolve().as_uri()
    external_requests: list[str] = []
    console_errors: list[str] = []
    page_errors: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=["--autoplay-policy=no-user-gesture-required"],
        )
        context = browser.new_context(viewport={"width": 1280, "height": 720})

        def abort_external(route) -> None:
            url = route.request.url
            if url.startswith(("http://", "https://")):
                external_requests.append(url)
                route.abort()
            else:
                route.continue_()

        context.route("**/*", abort_external)
        page = context.new_page()

        def on_console(message: ConsoleMessage) -> None:
            if message.type == "error":
                console_errors.append(message.text)

        page.on("console", on_console)
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.goto(uri, wait_until="load")

        count = page.locator(".slot").count()
        check(count == EXPECTED_PAGES, f"page count = {EXPECTED_PAGES}")
        check(page.locator("#counter").inner_text() == "1/80", "initial counter is 1/80")
        check(page.url.endswith("#page-1"), "initial URL hash is #page-1")
        check(page.locator(".diagram svg").count() == 8, "8 inline SVG diagrams")
        check(page.locator("img[data-embedded-from]").count() == 20, "20 embedded lab screenshots")
        check(page.locator("video").count() == 5, "5 embedded videos")
        check(page.locator('video[src^="data:video/mp4;base64,"]').count() == 5, "all videos use data URIs")
        embedded_assets = page.locator("[data-embedded-from]").evaluate_all(
            "els => els.map(el => el.dataset.embeddedFrom)"
        )
        check(embedded_assets == EXPECTED_EMBEDDED_ASSETS, "data-embedded-from asset list matches exactly")
        check(
            not (set(embedded_assets) & LEGACY_SCREENSHOT_ASSETS),
            "0 legacy SCM/webhook screenshot assets embedded",
        )
        check(
            not any("gitea" in asset.lower() for asset in embedded_assets),
            "0 embedded asset names contain gitea",
        )
        capture(page, "U7_cover.png")

        # Walk every page using the public keyboard control and verify counter/hash.
        for page_number in range(2, EXPECTED_PAGES + 1):
            page.keyboard.press("ArrowRight")
            actual = page.locator("#counter").inner_text()
            check(actual == f"{page_number}/{EXPECTED_PAGES}", f"ArrowRight updates counter to {actual}")
            check(page.url.endswith(f"#page-{page_number}"), f"hash updates to #page-{page_number}")

        page.keyboard.press("Home")
        check(page.locator("#counter").inner_text() == "1/80", "Home returns to cover")
        page.keyboard.press("End")
        check(page.locator("#counter").inner_text() == "80/80", "End jumps to last page")

        # Overview button opens the thumbnail grid; clicking a thumbnail exits and jumps.
        page.locator("#overview").click()
        check("overview" in (page.locator("body").get_attribute("class") or ""), "overview button opens grid")
        capture(page, "U7_overview.png")
        page.locator(".slot").nth(12).click()
        check("overview" not in (page.locator("body").get_attribute("class") or ""), "thumbnail click closes overview")
        check(page.locator("#counter").inner_text() == "13/80", "thumbnail click jumps to selected page")

        # The course-map cards are independently clickable.
        page.goto(f"{uri}#page-2", wait_until="load")
        page.locator('[data-goto="70"]').click()
        check(page.locator("#counter").inner_text() == "70/80", "course-map card jumps to episode 6")

        # Refresh must preserve the exact page through #page-N.
        page.goto(f"{uri}#page-72", wait_until="load")
        check(page.locator("#counter").inner_text() == "72/80", "direct #page-N navigation works")
        page.reload(wait_until="load")
        check(page.locator("#counter").inner_text() == "72/80", "refresh preserves current page")
        capture(page, "U7_diagram.png")

        # Each manifest composition must advance only while its own slide is active.
        videos = page.locator("video")
        compositions = set(videos.evaluate_all("els => els.map(v => v.dataset.composition)"))
        check(compositions == EXPECTED_COMPOSITIONS, "video compositionIds match motion manifest")
        for composition in sorted(EXPECTED_COMPOSITIONS):
            video = page.locator(f'video[data-composition="{composition}"]')
            slide_number = video.evaluate(
                "v => Array.from(document.querySelectorAll('.slot')).indexOf(v.closest('.slot')) + 1"
            )
            page.goto(f"{uri}#page-{slide_number}", wait_until="load")
            page.wait_for_function(
                "id => { const v=document.querySelector(`video[data-composition=\"${id}\"]`); return v && !v.paused && v.currentTime > 0.18; }",
                arg=composition,
                timeout=5000,
            )
            before = video.evaluate("v => v.currentTime")
            page.wait_for_timeout(450)
            after = video.evaluate("v => v.currentTime")
            check(after - before > 0.18, f"{composition} currentTime advances on its slide")
            if composition == "mo-dood-socket":
                capture(page, "U7_video.png")
            page.keyboard.press("ArrowRight")
            paused_at = video.evaluate("v => v.currentTime")
            page.wait_for_timeout(450)
            paused_after = video.evaluate("v => v.currentTime")
            check(video.evaluate("v => v.paused"), f"{composition} is paused after leaving")
            check(abs(paused_after - paused_at) < 0.08, f"{composition} currentTime stops after leaving")

        # Give late console/page errors a chance to arrive.
        page.wait_for_timeout(250)
        check(not external_requests, "0 external http(s) requests")
        check(not console_errors, "0 console errors")
        check(not page_errors, "0 uncaught page errors")
        browser.close()

    print("[deck] RESULT: PASS", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[deck][FAIL] {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc
