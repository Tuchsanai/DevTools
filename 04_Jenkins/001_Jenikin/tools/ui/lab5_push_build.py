#!/usr/bin/env python3
"""Push a real commit and prove the immediate webhook-caused Jenkins build."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import subprocess
import time
import urllib.request

from common import browser_page, jenkins_login, log, require, run_main, screenshot, wait_visible


JOB = "hello-ci-pipeline"


def jenkins_json(base_url: str, path: str) -> dict:
    token = base64.b64encode(b"admin:admin2569").decode("ascii")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}",
        headers={"Authorization": f"Basic {token}"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        return json.load(response)


def push_commit(devtools_name: str) -> str:
    script = r'''
set -eu
probe_dir=$(mktemp -d /tmp/lab5-push.XXXXXX)
trap 'rm -rf "$probe_dir"' EXIT
git clone -q http://student:student2569@localhost:3000/student/hello-ci.git "$probe_dir/repo"
git -C "$probe_dir/repo" config user.name student
git -C "$probe_dir/repo" config user.email student@example.com
date -u +"webhook proof %Y-%m-%dT%H:%M:%SZ" >> "$probe_dir/repo/webhook-proof.txt"
git -C "$probe_dir/repo" add webhook-proof.txt
git -C "$probe_dir/repo" commit -q -m "Verify immediate webhook build"
commit=$(git -C "$probe_dir/repo" rev-parse HEAD)
git -C "$probe_dir/repo" push -q origin main
printf '%s\n' "$commit"
'''
    return subprocess.check_output(
        ["docker", "exec", devtools_name, "bash", "-lc", script], text=True
    ).strip()


def wait_for_build(base_url: str, baseline: int, timeout_seconds: int) -> tuple[dict, float]:
    started = time.monotonic()
    deadline = started + timeout_seconds
    first_seen = None
    while time.monotonic() < deadline:
        payload = jenkins_json(
            base_url,
            f"/job/{JOB}/api/json?tree=lastBuild[number,building,result,url]",
        )
        build = payload.get("lastBuild") or {}
        if int(build.get("number", 0)) > baseline:
            if first_seen is None:
                first_seen = time.monotonic() - started
                log(f"new build #{build['number']} detected {first_seen:.2f}s after push")
            if not build.get("building"):
                return build, first_seen
        time.sleep(1)
    raise TimeoutError(f"no completed build appeared after #{baseline}")


def flow(args: argparse.Namespace) -> None:
    base_url = args.jenkins_base_url.rstrip("/")
    before = jenkins_json(base_url, f"/job/{JOB}/api/json?tree=lastBuild[number]")
    baseline = int((before.get("lastBuild") or {}).get("number", 0))
    log(f"baseline build is #{baseline}")

    push_started = time.monotonic()
    commit = push_commit(args.devtools_name)
    push_elapsed = time.monotonic() - push_started
    require(len(commit) == 40, "real Git commit was pushed to main")
    log(f"push completed in {push_elapsed:.2f}s; commit={commit[:12]}")

    build, detected_seconds = wait_for_build(base_url, baseline, args.build_timeout)
    number = int(build["number"])
    require(detected_seconds < 15, "webhook build was detected immediately (under 15 seconds)")
    require(build.get("result") == "SUCCESS", f"webhook build #{number} finished SUCCESS")

    detail = jenkins_json(
        base_url,
        f"/job/{JOB}/{number}/api/json?tree=number,result,actions[causes[shortDescription]]",
    )
    causes = [
        cause.get("shortDescription", "")
        for action in detail.get("actions", [])
        for cause in action.get("causes", [])
    ]
    require(any("generic" in cause.lower() for cause in causes), "build cause is Generic Webhook Trigger")
    log(f"build cause: {' | '.join(causes)}")

    token = base64.b64encode(b"admin:admin2569").decode("ascii")
    request = urllib.request.Request(
        f"{base_url}/job/{JOB}/{number}/consoleText",
        headers={"Authorization": f"Basic {token}"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        console = response.read().decode("utf-8", errors="replace")
    require(commit in console, "console checkout contains the pushed commit SHA")

    with browser_page(headless=not args.headed) as (_, _, _, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/job/{JOB}/{number}/", wait_until="domcontentloaded")
        body = wait_visible(page.locator("body"), "webhook-caused build page").inner_text()
        require(str(number) in body, f"build page shows #{number}")
        require("Generic" in body, "build page visibly identifies the Generic webhook cause")
        screenshot(page, Path(args.screenshot_dir) / "lab5_auto_build.png", "automatic build and cause after push")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jenkins-base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:15080"))
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk5"))
    parser.add_argument("--screenshot-dir", default="slides_assets")
    parser.add_argument("--build-timeout", type=int, default=240)
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_main(lambda: flow(parse_args()))
