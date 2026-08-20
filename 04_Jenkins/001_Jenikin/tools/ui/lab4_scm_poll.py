#!/usr/bin/env python3
"""Enable Poll SCM through Jenkins UI, then verify an SCM-caused build."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, screenshot, wait_visible


ROOT = Path(__file__).resolve().parents[2]
POLL_SHOT = ROOT / "slides_assets" / "lab4_poll_build.png"
JOB = "hello-ci-pipeline"


def api_json(page, url: str) -> dict:
    response = page.request.get(url)
    require(response.ok, f"API {url} returned HTTP {response.status}")
    return response.json()


def last_build_number(page, base_url: str) -> int:
    data = api_json(page, f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number]")
    build = data.get("lastBuild")
    return 0 if build is None else int(build["number"])


def state_path(devtools_name: str) -> Path:
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", devtools_name)
    return Path("/tmp") / f"lab4_scm_poll_{safe_name}.json"


def assert_poll_config(page, base_url: str) -> None:
    response = page.request.get(f"{base_url}/job/{JOB}/config.xml")
    require(response.ok, "job config.xml is readable after saving Poll SCM")
    root = ET.fromstring(response.text())
    trigger = root.find(".//hudson.triggers.SCMTrigger")
    require(trigger is not None, "Poll SCM trigger is present in config.xml")
    require(trigger.findtext("spec") == "* * * * *", "Poll SCM schedule is * * * * *")


def enable_poll(page, base_url: str, devtools_name: str) -> None:
    page.goto(f"{base_url}/job/{JOB}/configure", wait_until="domcontentloaded")
    form = wait_visible(page.locator("form[name='config']"), "hello-ci-pipeline configuration form")
    poll_text = wait_visible(form.get_by_text("Poll SCM", exact=True), "Poll SCM trigger")

    item = poll_text.locator("xpath=ancestor::*[contains(@class,'jenkins-form-item')][1]")
    checkbox = item.locator("input[type='checkbox']")
    if not checkbox.count():
        checkbox = form.locator("input[name='hudson-triggers-SCMTrigger']")
    require(checkbox.count() >= 1, "Poll SCM checkbox exists")
    if not checkbox.first.is_checked():
        poll_text.click()
    require(checkbox.first.is_checked(), "Poll SCM checkbox is selected through its UI label")

    spec = form.locator("textarea[name='_.scmpoll_spec']")
    require(spec.count() >= 1, "Poll SCM schedule field exists")
    spec.first.fill("* * * * *")

    baseline = last_build_number(page, base_url)
    page.locator("button[name='Submit']").click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/?$"))
    assert_poll_config(page, base_url)

    state = {"baseline": baseline, "enabled_at": time.time()}
    state_path(devtools_name).write_text(json.dumps(state), encoding="utf-8")
    log(f"baseline: build #{baseline}; timer started for the next SCM change")


def wait_for_poll_build(page, base_url: str, devtools_name: str, timeout_seconds: int) -> None:
    path = state_path(devtools_name)
    require(path.is_file(), f"poll baseline exists at {path}")
    state = json.loads(path.read_text(encoding="utf-8"))
    baseline = int(state["baseline"])
    enabled_at = float(state["enabled_at"])

    deadline = time.monotonic() + timeout_seconds
    number = baseline
    data: dict = {}
    while time.monotonic() < deadline:
        data = api_json(
            page,
            f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number,building,result,actions[causes[shortDescription]]],builds[number,result,building,actions[causes[shortDescription]]]",
        )
        candidates = [b for b in data.get("builds", []) if int(b.get("number", 0)) > baseline]
        scm_builds = [
            b
            for b in candidates
            if any("SCM" in str(c.get("shortDescription", "")) for a in b.get("actions", []) for c in a.get("causes", []))
        ]
        if scm_builds:
            build = max(scm_builds, key=lambda item: int(item["number"]))
            number = int(build["number"])
            if not build.get("building", True):
                require(build.get("result") == "SUCCESS", f"SCM-caused build #{number} finished SUCCESS")
                break
        page.wait_for_timeout(1000)
    else:
        raise AssertionError(f"timed out after {timeout_seconds}s waiting for Poll SCM build after #{baseline}")

    elapsed = time.time() - enabled_at
    log(f"observed: Poll SCM created build #{number} after {elapsed:.1f} seconds from timer start")

    console = page.request.get(f"{base_url}/job/{JOB}/{number}/consoleText")
    require(console.ok and "Finished: SUCCESS" in console.text(), "polled build console ended with SUCCESS")

    page.goto(f"{base_url}/job/{JOB}/scmPollLog/", wait_until="domcontentloaded")
    body = page.locator("body").inner_text()
    require("Polling Log" in body or "Polling log" in body, "Git Polling Log page is open")
    require(
        "Changes found" in body or "Done. Took" in body or "Using strategy" in body,
        "Git Polling Log contains a completed polling decision",
    )
    screenshot(page, POLL_SHOT, "Build History and Git Polling Log after SCM-caused build")
    path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("enable", "wait"), required=True)
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:14080"))
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk4"))
    parser.add_argument("--timeout", type=int, default=3700)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        if args.action == "enable":
            enable_poll(page, base_url, args.devtools_name)
        else:
            wait_for_poll_build(page, base_url, args.devtools_name, args.timeout)


if __name__ == "__main__":
    run_main(main)
