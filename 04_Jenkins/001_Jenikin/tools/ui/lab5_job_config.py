#!/usr/bin/env python3
"""Replace Poll SCM with the per-job Generic Webhook Trigger token via UI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


JOB = "hello-ci-pipeline"
TOKEN = "cicd2569-hello"


def flow(args: argparse.Namespace) -> None:
    base_url = args.base_url.rstrip("/")
    with browser_page(headless=not args.headed) as (_, _, _, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/job/{JOB}/configure", wait_until="domcontentloaded")

        poll = page.locator("input[name='hudson-triggers-SCMTrigger']")
        wait_visible(poll, "Poll SCM checkbox")
        require(poll.is_checked(), "Poll SCM starts enabled from LAB 4")
        poll.locator("xpath=following-sibling::label").click()
        require(not poll.is_checked(), "Poll SCM is disabled")

        generic = page.locator("input[name='org-jenkinsci-plugins-gwt-GenericTrigger']")
        wait_visible(generic, "Generic Webhook Trigger checkbox")
        require(not generic.is_checked(), "Generic Webhook Trigger starts disabled")
        generic.locator("xpath=following-sibling::label").click()
        require(generic.is_checked(), "Generic Webhook Trigger is enabled")

        trigger_block = generic.locator("xpath=ancestor::div[contains(@class,'optionalBlock-container')]")
        token = trigger_block.locator("input[name='_.token']")
        wait_visible(token, "Generic Webhook Trigger token field")
        token.fill(TOKEN)
        require(token.input_value() == TOKEN, "per-job token is cicd2569-hello")
        trigger_block.scroll_into_view_if_needed()
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s03_build_trigger_token.png"),
            full_page=False,
        )
        log("screenshot: Build Triggers with Generic Webhook Trigger token")

        page.get_by_role("button", name="Save", exact=True).click()
        page.wait_for_url(lambda url: f"/job/{JOB}/" in url and "configure" not in url, timeout=60_000)
        log("job configuration saved through UI")

        response = page.request.get(f"{base_url}/job/{JOB}/config.xml")
        require(response.ok, f"config.xml returned HTTP {response.status}")
        config = response.text()
        require("<hudson.triggers.SCMTrigger>" not in config, "saved config has Poll SCM disabled")
        require("org.jenkinsci.plugins.gwt.GenericTrigger" in config, "saved config contains GenericTrigger")
        require(f"<token>{TOKEN}</token>" in config, "saved config contains the per-job token")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:15080"))
    parser.add_argument("--screenshot-dir", default="slides_assets")
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_main(lambda: flow(parse_args()))
