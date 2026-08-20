#!/usr/bin/env python3
"""Create and test the hello-ci Gitea webhook, with delivery assertions."""

from __future__ import annotations

import argparse
import os
import re
from pathlib import Path

from common import browser_page, gitea_login, log, require, run_main, wait_visible


HOOK_URL = "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello"


def flow(args: argparse.Namespace) -> None:
    base_url = args.base_url.rstrip("/")
    with browser_page(headless=not args.headed) as (_, _, _, page):
        gitea_login(page, base_url)
        page.goto(f"{base_url}/student/hello-ci/settings/hooks", wait_until="domcontentloaded")
        if HOOK_URL not in page.locator("body").inner_text():
            page.goto(
                f"{base_url}/student/hello-ci/settings/hooks/gitea/new",
                wait_until="domcontentloaded",
            )
            require("/settings/hooks/gitea/new" in page.url, "Gitea Add Webhook page opened")
            target = wait_visible(page.locator("input[name='payload_url']"), "webhook Target URL")
            target.fill(HOOK_URL)
            push_only = page.locator("input[name='events'][value='push_only']")
            active = page.locator("input[name='active']")
            require(push_only.is_checked(), "Push Events is selected")
            require(active.is_checked(), "webhook is active")
            target.scroll_into_view_if_needed()
            page.screenshot(
                path=str(Path(args.screenshot_dir) / "lab5_s04_add_webhook_form.png"),
                full_page=False,
            )
            log("screenshot: Gitea Add Webhook form with canonical URL")
            page.get_by_role("button", name="Add Webhook", exact=True).click()
            page.wait_for_url(lambda url: "/settings/hooks" in url and "/new" not in url, timeout=60_000)
            log(f"webhook saved through UI at {page.url}")

        require(HOOK_URL in page.locator("body").inner_text(), "saved webhook URL is shown")
        page.goto(f"{base_url}/student/hello-ci/settings/hooks", wait_until="domcontentloaded")
        require(HOOK_URL in page.locator("body").inner_text(), "canonical webhook remains listed after save")
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s05_webhook_list.png"),
            full_page=False,
        )
        log("screenshot: saved webhook in repository webhook list")
        saved = page.locator("a[href*='/settings/hooks/']").filter(has_text="Unnamed Webhook").first
        require(saved.count() == 1, "saved Gitea webhook entry is present")
        saved.click()
        page.wait_for_load_state("domcontentloaded")
        require(page.locator("input[name='payload_url']").input_value() == HOOK_URL, "edit page has canonical internal URL")

        test_button = page.locator("button:visible").filter(has_text="Test Push Event").first
        wait_visible(test_button, "Test Push Event button")
        test_button.click()
        log("Test Push Event submitted")

        delivery = page.get_by_text(
            re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
        ).first
        wait_visible(delivery, "new delivery UUID", 60_000)
        delivery.click()
        response_tab = page.locator("a.item[data-tab^='response-']:visible").first
        if response_tab.count() and response_tab.is_visible():
            response_tab.click()
        page.wait_for_timeout(1_000)
        text = page.locator("body").inner_text()
        require("200" in text, "delivery details show HTTP 200")
        require("hello-ci-pipeline" in text and "Triggered jobs." in text, "response names the triggered Jenkins job")
        for line in text.splitlines():
            if "200" in line or "Triggered" in line or "hello-ci-pipeline" in line:
                log(f"delivery evidence: {line.strip()}")
        delivery.scroll_into_view_if_needed()
        page.mouse.wheel(0, 650)
        page.wait_for_timeout(300)
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s06_delivery_response.png"),
            full_page=False,
        )
        log("screenshot: expanded delivery with HTTP 200 and Jenkins response")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("GITEA_BASE_URL", "http://host.docker.internal:15300"))
    parser.add_argument("--screenshot-dir", default="slides_assets")
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_main(lambda: flow(parse_args()))
