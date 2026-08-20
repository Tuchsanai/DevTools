#!/usr/bin/env python3
"""Enable Poll SCM through Jenkins UI and verify the resulting GitHub build."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, wait_visible
from lab4_capture import masked_screenshot


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"
JOB = "hello-ci-pipeline"


def api_json(page, url: str) -> dict:
    response = page.request.get(url)
    require(response.ok, f"API {url} returned HTTP {response.status}")
    return response.json()


def last_build_number(page, base_url: str) -> int:
    build = api_json(page, f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number]").get("lastBuild")
    return 0 if build is None else int(build["number"])


def state_path(devtools_name: str) -> Path:
    return Path("/tmp") / f"lab4_scm_poll_{re.sub(r'[^A-Za-z0-9_.-]', '_', devtools_name)}.json"


def assert_poll_config(page, base_url: str) -> None:
    response = page.request.get(f"{base_url}/job/{JOB}/config.xml")
    require(response.ok, "job config.xml is readable after saving Poll SCM")
    root = ET.fromstring(response.text())
    triggers = root.findall(".//hudson.triggers.SCMTrigger")
    require(len(triggers) == 1, "exactly one Poll SCM trigger is present in config.xml")
    require(triggers[0].findtext("spec") == "* * * * *", "Poll SCM schedule is * * * * *")


def enable_poll(page, base_url: str, devtools_name: str, user: str) -> None:
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
    spec.first.press("Tab")
    spec.first.evaluate("el => el.scrollIntoView({block: 'center'})")
    page.wait_for_timeout(2500)
    masked_screenshot(
        page,
        ASSETS / "lab4_s07_poll_scm_trigger.png",
        "Poll SCM selected with an every-minute schedule",
        mask_texts=(user,),
    )

    baseline = last_build_number(page, base_url)
    page.locator("button[name='Submit']").click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/?$"))
    assert_poll_config(page, base_url)
    state_path(devtools_name).write_text(json.dumps({"baseline": baseline, "enabled_at": time.time()}), encoding="utf-8")
    log(f"baseline: build #{baseline}; timer started for the next SCM change")


def origin_sha(user: str) -> str:
    result = subprocess.run(
        ["git", "ls-remote", f"https://github.com/{user}/hello-ci.git", "refs/heads/main"],
        check=True,
        text=True,
        capture_output=True,
        timeout=60,
    )
    sha = result.stdout.split()[0] if result.stdout.split() else ""
    require(bool(re.fullmatch(r"[0-9a-f]{40}", sha)), "origin/main resolves to a full Git SHA")
    return sha


def wait_for_poll_build(page, base_url: str, devtools_name: str, timeout_seconds: int, user: str) -> None:
    path = state_path(devtools_name)
    require(path.is_file(), f"poll baseline exists at {path}")
    state = json.loads(path.read_text(encoding="utf-8"))
    baseline = int(state["baseline"])
    enabled_at = float(state["enabled_at"])
    deadline = time.monotonic() + timeout_seconds
    number = baseline
    build: dict = {}
    while time.monotonic() < deadline:
        data = api_json(page, f"{base_url}/job/{JOB}/api/json?tree=builds[number,result,building,actions[causes[shortDescription]]]")
        candidates = []
        for item in data.get("builds", []):
            causes = [str(c.get("shortDescription", "")) for action in item.get("actions", []) for c in action.get("causes", [])]
            if int(item.get("number", 0)) > baseline and any("scm change" in cause.casefold() for cause in causes):
                candidates.append(item)
        if candidates:
            build = max(candidates, key=lambda item: int(item["number"]))
            number = int(build["number"])
            if not build.get("building", True):
                break
        page.wait_for_timeout(1000)
    else:
        raise AssertionError(f"timed out after {timeout_seconds}s waiting for Poll SCM build after #{baseline}")

    require(build.get("result") == "SUCCESS", f"SCM-caused build #{number} finished SUCCESS")
    causes = [str(c.get("shortDescription", "")) for action in build.get("actions", []) for c in action.get("causes", [])]
    require(any("started by an scm change" in cause.casefold() for cause in causes), "build cause is Started by an SCM change")
    console = page.request.get(f"{base_url}/job/{JOB}/{number}/consoleText")
    require(console.ok and "Finished: SUCCESS" in console.text(), "polled build console ended with SUCCESS")
    expected_sha = origin_sha(user)
    checkouts = re.findall(r"Checking out Revision ([0-9a-f]{40})", console.text(), re.I)
    require(bool(checkouts) and checkouts[-1].casefold() == expected_sha.casefold(), "checkout SHA equals the pushed origin/main SHA")

    page.goto(f"{base_url}/job/{JOB}/scmPollLog/", wait_until="domcontentloaded")
    poll_body = page.locator("body").inner_text()
    require("Changes found" in poll_body, "Git Polling Log contains Changes found")
    masked_screenshot(page, ASSETS / "lab4_s08_git_polling_log.png", "Git Polling Log with Changes found", mask_texts=(user,))

    page.goto(f"{base_url}/job/{JOB}/{number}/", wait_until="domcontentloaded")
    require("Started by an SCM change" in page.locator("body").inner_text(), "build detail page shows Started by an SCM change")
    masked_screenshot(page, ASSETS / "lab4_s09_scm_build_cause.png", "SCM-caused successful build detail", mask_texts=(user,))
    log(f"observed: Poll SCM created build #{number} after {time.time() - enabled_at:.1f} seconds from timer start")
    path.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("enable", "wait"), required=True)
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:20080"))
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk-lab"))
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    user = os.environ.get("GITHUB_USER", "")
    require(bool(user), "GITHUB_USER is set")
    base_url = args.base_url.rstrip("/")
    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        if args.action == "enable":
            enable_poll(page, base_url, args.devtools_name, user)
        else:
            wait_for_poll_build(page, base_url, args.devtools_name, args.timeout, user)


if __name__ == "__main__":
    run_main(main)
