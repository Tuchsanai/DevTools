#!/usr/bin/env python3
"""Assert the newly pushed tag on the real public Docker Hub page."""

from __future__ import annotations

import os
from pathlib import Path

from common import browser_page, require, run_main, screenshot, wait_visible


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "slides_assets" / "lab3_hub_tags.png"


def main() -> None:
    docker_user = os.environ.get("DOCKER_USER", "")
    build_number = os.environ.get("BUILD_NUMBER", "")
    require(bool(docker_user and build_number), "public username and current build number are present")
    url = f"https://hub.docker.com/r/{docker_user}/ci-demo/tags"

    with browser_page() as (_, _, context, page):
        context.clear_cookies()
        response = page.goto(url, wait_until="domcontentloaded", timeout=120000)
        require(response is not None and response.status == 200, "Docker Hub Tags page returns HTTP 200")
        wait_visible(page.get_by_text("ci-demo", exact=False).first, "ci-demo repository title", 120000)
        wait_visible(page.get_by_text(build_number, exact=True).first, f"new tag {build_number}", 120000)
        require("/ci-demo/tags" in page.url, "browser remains on the ci-demo Tags page")
        screenshot(page, TARGET, "real public Docker Hub tag created by this build")


if __name__ == "__main__":
    run_main(main)
