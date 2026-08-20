#!/usr/bin/env python3
"""Assert and capture a real LAB 6 Deploy Dashboard."""

from __future__ import annotations

import os
from pathlib import Path

from common import browser_page, require, run_main, screenshot, wait_visible


def main() -> None:
    base_url = os.getenv("WEBAPP_BASE_URL", "http://host.docker.internal:16800").rstrip("/")
    version = os.environ.get("EXPECTED_VERSION", "1.0.0")
    theme = os.environ.get("EXPECTED_THEME", "blue")
    target = Path(os.environ.get("SCREENSHOT", f"slides_assets/lab6_app_{'v2' if version.startswith('2') else 'v1'}.png"))

    with browser_page() as (_, _, _, page):
        response = page.goto(base_url, wait_until="networkidle")
        require(response is not None and response.status == 200, "Deploy Dashboard returns HTTP 200")
        wait_visible(page.get_by_text(f"v{version}", exact=True), f"dashboard version {version}")
        require(page.locator("body").get_attribute("data-theme") == theme, f"dashboard shows version {version} and {theme} theme")
        build = page.locator("body").get_attribute("data-build") or ""
        require(build.isdigit(), "dashboard displays a numeric Jenkins BUILD_NUMBER")
        require("Container hostname" in page.locator(".label").all_text_contents(), "dashboard displays the container hostname")
        screenshot(page, target, f"real deployed dashboard v{version}, theme={theme}, build={build}")


if __name__ == "__main__":
    run_main(main)
