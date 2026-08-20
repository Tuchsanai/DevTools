#!/usr/bin/env python3
"""Create and assert the LAB 6 Gitea webhook through the web UI."""

from __future__ import annotations

import os
from pathlib import Path

from common import browser_page, gitea_login, log, require, run_main, wait_visible


TARGET_URL = "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-webapp"


def main() -> None:
    base_url = os.getenv("GITEA_BASE_URL", "http://host.docker.internal:16300").rstrip("/")
    hooks_url = f"{base_url}/student/webapp/settings/hooks"
    target = Path(os.environ.get("SCREENSHOT", "slides_assets/lab6_s05_gitea_webhook.png"))

    with browser_page() as (_, _, _, page):
        gitea_login(page, base_url)
        page.goto(hooks_url, wait_until="domcontentloaded")
        if TARGET_URL not in page.locator("body").inner_text():
            page.goto(f"{hooks_url}/gitea/new", wait_until="domcontentloaded")
            payload = wait_visible(page.locator("input[name='payload_url']"), "webhook target URL")
            payload.fill(TARGET_URL)
            content_type = page.locator("select[name='content_type']")
            if content_type.count():
                try:
                    content_type.select_option(label="application/json")
                except Exception:
                    content_type.select_option("2")
            push_only = page.locator("input[name='events'][value='push_only']")
            if push_only.count():
                push_only.check()
            active = page.locator("input[name='active']")
            if active.count() and not active.is_checked():
                active.check()
            page.get_by_role("button", name="Add Webhook").click()
            page.wait_for_load_state("domcontentloaded")
            page.goto(hooks_url, wait_until="domcontentloaded")

        require(TARGET_URL in page.locator("body").inner_text(), "active webapp webhook uses the canonical Jenkins URL")
        target.parent.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(target), full_page=False)
        log(f"screenshot: active canonical webapp webhook -> {target}")


if __name__ == "__main__":
    run_main(main)
