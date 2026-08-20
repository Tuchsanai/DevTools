#!/usr/bin/env python3
"""Replace Poll SCM with the LAB 5 GWT token, variables, cause, and filter."""

from __future__ import annotations

import argparse
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


JOB = "hello-ci-pipeline"
TOKEN = "cicd2569-hello"
ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"


def form_item(block, label: str):
    return block.get_by_text(label, exact=True).locator(
        "xpath=ancestor::div[contains(@class,'jenkins-form-item')][1]"
    )


def add_post_parameter(block) -> None:
    form_item(block, "Post content parameters").get_by_role("button", name="Add").last.click()


def assert_contract(config: str) -> None:
    root = ET.fromstring(config)
    require(not root.findall(".//hudson.triggers.SCMTrigger"), "saved config has Poll SCM disabled")
    triggers = root.findall(".//org.jenkinsci.plugins.gwt.GenericTrigger")
    require(len(triggers) == 1, "saved config contains exactly one GenericTrigger")
    trigger = triggers[0]
    variables = {
        item.findtext("key"): item.findtext("value")
        for item in trigger.findall("./genericVariables/*")
    }
    require(variables == {"ref": "$.ref", "after": "$.after"}, "saved post parameters are ref=$.ref and after=$.after")
    require(trigger.findtext("token") == TOKEN, "saved token is cicd2569-hello")
    require(trigger.findtext("causeString") == "GitHub push $after", "saved cause is GitHub push $after")
    require(trigger.findtext("regexpFilterText") == "$ref", "saved filter text is $ref")
    require(trigger.findtext("regexpFilterExpression") == "^refs/heads/main$", "saved filter accepts only main")


def flow(args: argparse.Namespace) -> None:
    base_url = args.base_url.rstrip("/")
    with browser_page(headless=not args.headed) as (_, _, _, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/job/{JOB}/configure", wait_until="domcontentloaded")

        form = wait_visible(page.locator("form[name='config']"), "hello-ci-pipeline configuration form")
        poll = form.locator("input[name='hudson-triggers-SCMTrigger']")
        wait_visible(poll, "Poll SCM checkbox")
        if poll.is_checked():
            poll.locator("xpath=following-sibling::label").click()
        require(not poll.is_checked(), "Poll SCM is disabled")

        generic = form.locator("input[name='org-jenkinsci-plugins-gwt-GenericTrigger']")
        wait_visible(generic, "Generic Webhook Trigger checkbox")
        if not generic.is_checked():
            generic.locator("xpath=following-sibling::label").click()
        require(generic.is_checked(), "Generic Webhook Trigger is enabled")

        trigger_block = generic.locator("xpath=ancestor::div[contains(@class,'optionalBlock-container')]")
        keys = trigger_block.locator("input[name='_.key']")
        while keys.count() < 2:
            add_post_parameter(trigger_block)
        while keys.count() > 2:
            trigger_block.locator("button.repeatable-delete").last.click()
        values = trigger_block.locator("input[name='_.value']")
        keys.nth(0).fill("ref")
        values.nth(0).fill("$.ref")
        keys.nth(1).fill("after")
        values.nth(1).fill("$.after")

        token = trigger_block.locator("input[name='_.token']")
        wait_visible(token, "Generic Webhook Trigger token field")
        token.fill(TOKEN)
        require(token.input_value() == TOKEN, "per-job token is cicd2569-hello")
        cause = trigger_block.locator("input[name='_.causeString']")
        cause.fill("GitHub push $after")
        keys.nth(0).evaluate("el => el.scrollIntoView({block: 'center'})")
        page.wait_for_timeout(500)
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s04_gwt_parameters.png"),
            full_page=False,
        )
        log("screenshot: GWT first post content parameter ref")
        keys.nth(1).evaluate("el => el.scrollIntoView({block: 'center'})")
        page.wait_for_timeout(500)
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s04b_gwt_after.png"),
            full_page=False,
        )
        log("screenshot: GWT second post content parameter after")
        cause.evaluate("el => el.scrollIntoView({block: 'center'})")
        page.wait_for_timeout(500)
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s04c_gwt_token_cause.png"),
            full_page=False,
        )
        log("screenshot: GWT per-job token and SHA-bearing cause")

        expression = trigger_block.locator("input[name='_.regexpFilterExpression']")
        filter_text = trigger_block.locator("input[name='_.regexpFilterText']")
        expression.fill("^refs/heads/main$")
        filter_text.fill("$ref")
        expression.evaluate("el => el.scrollIntoView({block: 'center'})")
        page.wait_for_timeout(500)
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s05_gwt_filter.png"),
            full_page=False,
        )
        log("screenshot: GWT main-branch optional filter")

        submit = form.locator("button[name='Submit']")
        submit.scroll_into_view_if_needed()
        page.wait_for_timeout(500)
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s05b_gwt_save.png"),
            full_page=False,
        )
        log("screenshot: GWT configuration Save action")
        submit.click()
        page.wait_for_url(re.compile(rf"/job/{JOB}/?$"), timeout=60_000)
        log("job configuration saved through UI")

        response = page.request.get(f"{base_url}/job/{JOB}/config.xml")
        require(response.ok, f"config.xml returned HTTP {response.status}")
        assert_contract(response.text())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:20080"))
    parser.add_argument("--screenshot-dir", default=str(ASSETS))
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_main(lambda: flow(parse_args()))
