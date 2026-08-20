#!/usr/bin/env python3
"""Create and build LAB 1's first Freestyle job through the Jenkins UI."""

from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from common import jenkins_login, log, require, run_main, wait_visible


def job_api(page, base_url: str) -> dict | None:
    response = page.request.get(
        f"{base_url.rstrip('/')}/job/first-freestyle/api/json?tree=name,lastBuild[number,url]"
    )
    if response.status == 404:
        return None
    require(response.ok, f"first-freestyle API returned HTTP {response.status}")
    return response.json()


def configure_job(page, base_url: str, *, create: bool) -> None:
    if not create:
        page.goto(
            f"{base_url.rstrip('/')}/job/first-freestyle/configure",
            wait_until="domcontentloaded",
        )
        page.wait_for_timeout(2_000)

    command = page.locator("textarea[name='command']")
    if not command.count():
        add_build_step = page.get_by_role("button", name="Add build step")
        wait_visible(add_build_step, "Add build step").click()
        execute_shell = page.get_by_text("Execute shell", exact=True)
        wait_visible(execute_shell, "Execute shell build step").click()
        command = page.locator("textarea[name='command']")
        command.wait_for(state="attached")

    # Jenkins 2.568 wraps this hidden textarea with CodeMirror. Updating both the
    # backing field and editor keeps the flow stable across headed/headless runs.
    shell = 'echo "Hello from Jenkins!"; date; hostname'
    command.last.evaluate(
        """(element, value) => {
          element.value = value;
          element.dispatchEvent(new Event('input', {bubbles: true}));
          element.dispatchEvent(new Event('change', {bubbles: true}));
          const editor = element.nextElementSibling && element.nextElementSibling.CodeMirror;
          if (editor) editor.setValue(value);
        }""",
        shell,
    )
    wait_visible(page.locator(".CodeMirror").last, "shell command editor")
    page.get_by_role("button", name="Save").click()
    page.wait_for_url("**/job/first-freestyle/**")
    wait_visible(page.locator("#main-panel"), "saved first-freestyle job page")
    log("configured first-freestyle with echo, date, and hostname")


def create_job(page, base_url: str) -> None:
    page.goto(f"{base_url.rstrip('/')}/newJob", wait_until="domcontentloaded")
    name = wait_visible(page.locator("input[name='name']"), "new item name")
    name.fill("first-freestyle")
    project_type = page.get_by_text("Freestyle project", exact=True)
    wait_visible(project_type, "Freestyle project type").click()
    ok = page.get_by_role("button", name="OK")
    wait_visible(ok, "create item OK button").click()

    configure_job(page, base_url, create=True)


def start_build(page, base_url: str) -> tuple[int, str]:
    page.goto(f"{base_url.rstrip('/')}/job/first-freestyle/", wait_until="domcontentloaded")
    current = job_api(page, base_url) or {}
    current_build = current.get("lastBuild") or {}
    current_number = int(current_build.get("number") or 0)
    if current_number:
        current_url = f"{base_url.rstrip('/')}/job/first-freestyle/{current_number}/"
        current_response = page.request.get(
            f"{current_url}api/json?tree=number,building,result"
        )
        if current_response.ok and current_response.json().get("result") == "SUCCESS":
            require(True, f"existing build #{current_number} is SUCCESS")
            log("reusing the successful build created by the prior Build Now action")
            return current_number, current_url

    build_now = wait_visible(page.get_by_text("Build Now", exact=True), "Build Now")
    build_now.click()
    log("requested a new build")

    deadline = time.monotonic() + 180
    build_number = 0
    build_url = ""
    while time.monotonic() < deadline:
        payload = job_api(page, base_url) or {}
        last_build = payload.get("lastBuild") or {}
        build_number = int(last_build.get("number") or 0)
        api_url = str(last_build.get("url") or "")
        if build_number and api_url:
            # The API intentionally returns the canonical student-facing URL
            # (localhost:8080). The agent must keep browsing via PLAN §7's
            # shifted host.docker.internal URL.
            build_url = (
                f"{base_url.rstrip('/')}/job/first-freestyle/{build_number}/"
            )
            break
        page.wait_for_timeout(1_000)
    require(build_number > 0 and bool(build_url), "Jenkins API reported a latest build")

    result = None
    while time.monotonic() < deadline:
        response = page.request.get(f"{build_url}api/json?tree=number,building,result")
        require(response.ok, f"build API returned HTTP {response.status}")
        payload = response.json()
        result = payload.get("result")
        if not payload.get("building") and result:
            break
        page.wait_for_timeout(1_000)
    require(result == "SUCCESS", f"first-freestyle build #{build_number} completed SUCCESS")
    return build_number, build_url


def capture_console(page, build_number: int, build_url: str, screenshot_path: Path) -> None:
    page.goto(f"{build_url}console", wait_until="domcontentloaded")
    console = wait_visible(page.locator("#main-panel"), "Console Output")
    wait_visible(page.get_by_text("Finished: SUCCESS", exact=False), "successful console footer")
    text = console.inner_text()
    require("Hello from Jenkins!" in text, "console contains the echo output")
    require("Finished: SUCCESS" in text, "console contains Finished: SUCCESS")
    require(len([line for line in text.splitlines() if line.strip()]) >= 5, "console contains command output")
    page.set_viewport_size({"width": 1280, "height": 900})
    screenshot_path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(screenshot_path), full_page=False)
    log(f"screenshot: first build #{build_number} console -> {screenshot_path}")


def flow(args: argparse.Namespace) -> None:
    # Import here so an unavailable browser produces a clear non-zero run_main exit.
    from common import browser_page

    with browser_page(headless=not args.headed) as (_, _, _, page):
        page.set_viewport_size({"width": 1280, "height": 900})
        jenkins_login(page, args.base_url)
        payload = job_api(page, args.base_url)
        if payload is None:
            create_job(page, args.base_url)
        else:
            require(payload.get("name") == "first-freestyle", "existing job has the canonical name")
            configure_job(page, args.base_url, create=False)
            log("first-freestyle already exists; canonical shell step was refreshed")
        build_number, build_url = start_build(page, args.base_url)
        capture_console(page, build_number, build_url, Path(args.screenshot))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:11080"),
    )
    parser.add_argument(
        "--screenshot",
        default="slides_assets/lab1_first_build.png",
    )
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_main(lambda: flow(arguments))
