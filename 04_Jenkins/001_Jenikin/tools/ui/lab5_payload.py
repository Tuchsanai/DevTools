#!/usr/bin/env python3
"""Open the latest Gitea delivery request and verify its pushed-commit payload."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import subprocess

from common import browser_page, gitea_login, log, require, run_main, wait_visible


HOOK_URL = "http://jenkins:8080/generic-webhook-trigger/invoke?token=cicd2569-hello"


def remote_head(devtools_name: str) -> str:
    output = subprocess.check_output(
        [
            "docker", "exec", devtools_name, "git", "ls-remote",
            "http://student:student2569@localhost:3000/student/hello-ci.git", "refs/heads/main",
        ],
        text=True,
    )
    return output.split()[0]


def flow(args: argparse.Namespace) -> None:
    base_url = args.base_url.rstrip("/")
    commit = remote_head(args.devtools_name)
    require(len(commit) == 40, "read current main commit from Gitea")

    with browser_page(headless=not args.headed) as (_, _, _, page):
        gitea_login(page, base_url)
        page.goto(f"{base_url}/student/hello-ci/settings/hooks", wait_until="domcontentloaded")
        require(HOOK_URL in page.locator("body").inner_text(), "canonical webhook is listed")
        page.locator("a[href*='/settings/hooks/']").filter(has_text="Unnamed Webhook").first.click()
        page.wait_for_load_state("domcontentloaded")

        delivery = page.get_by_text(
            re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
        ).first
        wait_visible(delivery, "latest push delivery UUID")
        delivery.click()
        page.wait_for_timeout(500)
        request_tab = page.locator("a.item[data-tab^='request-']:visible").first
        wait_visible(request_tab, "delivery Request tab")
        request_tab.click()
        page.wait_for_timeout(500)
        # Scope assertions to the expanded delivery. Other collapsed deliveries
        # remain in the DOM and must not satisfy evidence for the latest push.
        payload_source = page.locator("pre.webhook-info:visible").last.inner_text()
        payload = json.loads(payload_source)
        head_commit = payload.get("head_commit") or {}
        commits = payload.get("commits") or []
        require(head_commit.get("id") == commit, "payload head commit matches Gitea main")
        require(
            "Verify immediate webhook build" in str(head_commit.get("message", "")),
            "payload contains the pushed commit message",
        )
        require(
            any("webhook-proof.txt" in (item.get("added") or []) for item in commits),
            "payload commits[].added contains webhook-proof.txt",
        )
        log(f"payload head_commit={commit[:12]} message='Verify immediate webhook build'")
        request_tab.scroll_into_view_if_needed()
        page.mouse.wheel(0, 700)
        page.wait_for_timeout(300)
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s08_delivery_request.png"),
            full_page=False,
        )
        log("screenshot: latest delivery Request payload")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("GITEA_BASE_URL", "http://host.docker.internal:15300"))
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk5"))
    parser.add_argument("--screenshot-dir", default="slides_assets")
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_main(lambda: flow(parse_args()))
