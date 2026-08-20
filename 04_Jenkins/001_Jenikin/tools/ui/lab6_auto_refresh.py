#!/usr/bin/env python3
"""Keep v1 open and prove its 5-second poll reloads the same page to v2."""

from __future__ import annotations

import os
from pathlib import Path

from common import browser_page, log, require, run_main, screenshot, wait_visible


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "slides_assets" / "lab6_s11_dashboard_v2.png"


def main() -> None:
    base_url = os.getenv("WEBAPP_BASE_URL", "http://host.docker.internal:20800").rstrip("/")

    with browser_page() as (_, _, _, page):
        response = page.goto(base_url, wait_until="networkidle")
        require(response is not None and response.status == 200, "v1 dashboard is reachable before the second push")
        require(page.locator("body").get_attribute("data-version") == "1.0.0", "the same browser page starts on version 1.0.0")
        old_build = page.locator("body").get_attribute("data-build") or ""
        log(f"ready: waiting on the existing v1 page (build={old_build})")

        page.wait_for_function(
            "document.body.dataset.version === '2.0.0' && document.body.dataset.theme === 'green'",
            timeout=900000,
        )
        wait_visible(page.get_by_text("v2.0.0", exact=True), "auto-refreshed dashboard version 2.0.0")
        new_build = page.locator("body").get_attribute("data-build") or ""
        require(new_build.isdigit() and new_build != old_build, "auto-refresh shows a newer Jenkins BUILD_NUMBER")
        require(page.locator("body").get_attribute("data-theme") == "green", "auto-refresh applies the green palette")
        screenshot(page, TARGET, f"same browser page after automatic v1-to-v2 refresh, build={new_build}")


if __name__ == "__main__":
    run_main(main)
