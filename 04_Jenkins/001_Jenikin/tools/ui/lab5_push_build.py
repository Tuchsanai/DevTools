#!/usr/bin/env python3
"""Push one hello.sh change and prove exactly one matching GWT build."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import time
import urllib.request
import urllib.error

from common import browser_page, jenkins_login, log, require, run_main
from lab5_capture import masked_screenshot


JOB = "hello-ci-pipeline"
ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"


def jenkins_json(base_url: str, path: str) -> dict:
    token = base64.b64encode(b"admin:admin2569").decode("ascii")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}{path}", headers={"Authorization": f"Basic {token}"}
    )
    for attempt in range(5):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return json.load(response)
        except urllib.error.URLError:
            if attempt == 4:
                raise
            time.sleep(1)
    raise AssertionError("unreachable")


def console_text(base_url: str, number: int) -> str:
    token = base64.b64encode(b"admin:admin2569").decode("ascii")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/job/{JOB}/{number}/consoleText",
        headers={"Authorization": f"Basic {token}"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode(errors="replace")


def push_commit(devtools_name: str, user: str, token: str) -> str:
    script = r'''
set -eu
askpass_dir=$(mktemp -d /tmp/lab5-askpass.XXXXXX)
trap 'rm -rf -- "$askpass_dir"' EXIT
printf '#!/bin/sh\ncase "$1" in *Username*) printf "%%s\\n" "$GITHUB_USER" ;; *) printf "%%s\\n" "$GITHUB_TOKEN" ;; esac\n' > "$askpass_dir/askpass.sh"
chmod 700 "$askpass_dir/askpass.sh"
cd /root/hello-ci
git pull --ff-only -q origin main
git config user.name Student
git config user.email student@example.invalid
printf '\n# Webhook probe %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> hello.sh
proof_file=webhook-proof.txt
if [ -e "$proof_file" ]; then proof_file="webhook-proof-$(date -u +%Y%m%dT%H%M%SZ).txt"; fi
printf 'GitHub webhook payload proof\n' > "$proof_file"
git add hello.sh
git add "$proof_file"
git commit -q -m 'Verify immediate GitHub webhook build'
commit=$(git rev-parse HEAD)
GIT_ASKPASS="$askpass_dir/askpass.sh" GIT_TERMINAL_PROMPT=0 git push -q origin main
printf '%s\n' "$commit"
'''
    env_args = ["-e", f"GITHUB_USER={user}", "-e", f"GITHUB_TOKEN={token}"]
    output = subprocess.check_output(
        ["docker", "exec", *env_args, devtools_name, "bash", "-lc", script], text=True
    )
    sha = output.strip().splitlines()[-1]
    require(bool(re.fullmatch(r"[0-9a-f]{40}", sha)), "one real commit modifying hello.sh was pushed")
    return sha


def wait_for_build(base_url: str, baseline: int, timeout_seconds: int) -> tuple[int, float]:
    started = time.monotonic()
    deadline = started + timeout_seconds
    detected = 0.0
    while time.monotonic() < deadline:
        payload = jenkins_json(base_url, f"/job/{JOB}/api/json?tree=lastBuild[number,building,result]")
        build = payload.get("lastBuild") or {}
        number = int(build.get("number", 0))
        if number == baseline + 1:
            if not detected:
                detected = time.monotonic() - started
                log(f"new build #{number} detected {detected:.2f}s after push")
            if not build.get("building", True):
                require(build.get("result") == "SUCCESS", f"webhook build #{number} finished SUCCESS")
                return number, detected
        require(number <= baseline + 1, "no more than one build appeared after this push")
        time.sleep(1)
    raise TimeoutError(f"no completed build appeared after #{baseline}")


def flow(args: argparse.Namespace) -> None:
    user = os.environ.get("GITHUB_USER", "")
    github_token = os.environ.get("GITHUB_TOKEN", "")
    require(bool(user) and bool(github_token), "GITHUB_USER and GITHUB_TOKEN are set")
    base_url = args.jenkins_base_url.rstrip("/")
    before = jenkins_json(base_url, f"/job/{JOB}/api/json?tree=lastBuild[number,result,building]")
    if args.verify_latest:
        number = int((before.get("lastBuild") or {}).get("number", 0))
        require(number > 0 and before["lastBuild"].get("result") == "SUCCESS", "latest build is already complete and SUCCESS")
        output = subprocess.check_output(
            ["git", "ls-remote", f"https://github.com/{user}/hello-ci.git", "refs/heads/main"],
            text=True,
            timeout=60,
        )
        commit = output.split()[0]
        require(bool(re.fullmatch(r"[0-9a-f]{40}", commit)), "latest origin/main SHA is readable")
        log(f"verify latest evidence for build #{number} and commit={commit[:12]}")
    else:
        baseline = int((before.get("lastBuild") or {}).get("number", 0))
        log(f"baseline build is #{baseline}")
        started = time.monotonic()
        commit = push_commit(args.devtools_name, user, github_token)
        log(f"push completed in {time.monotonic() - started:.2f}s; commit={commit[:12]}")
        number, detected = wait_for_build(base_url, baseline, args.build_timeout)
        require(detected < 30, "webhook build appeared without waiting for a polling minute")

    detail = jenkins_json(
        base_url, f"/job/{JOB}/{number}/api/json?tree=actions[causes[shortDescription]]"
    )
    causes = [
        str(cause.get("shortDescription", ""))
        for action in detail.get("actions", [])
        for cause in action.get("causes", [])
    ]
    require(any(cause == f"GitHub push {commit}" for cause in causes), "build cause contains the exact pushed SHA")
    console = console_text(base_url, number)
    checkouts = re.findall(r"Checking out Revision ([0-9a-f]{40})", console, re.I)
    require(bool(checkouts) and checkouts[-1] == commit, "Jenkins checkout SHA equals the pushed SHA")
    if not args.verify_latest:
        time.sleep(8)
        current = jenkins_json(base_url, f"/job/{JOB}/api/json?tree=lastBuild[number]")
        require(int(current["lastBuild"]["number"]) == baseline + 1, "the push produced exactly one build")

    with browser_page(headless=not args.headed) as (_, _, _, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/job/{JOB}/{number}/", wait_until="domcontentloaded")
        body = page.locator("body").inner_text()
        require(f"GitHub push {commit}" in body, "build page displays the SHA-bearing GitHub push cause")
        masked_screenshot(page, ASSETS / "lab5_s09_github_push_build.png", "successful GitHub push build", masks=((user, "<GITHUB_USER>"),))
        page.goto(f"{base_url}/job/{JOB}/{number}/console", wait_until="domcontentloaded")
        page.get_by_text("Checking out Revision", exact=False).last.scroll_into_view_if_needed()
        masked_screenshot(page, ASSETS / "lab5_s10_checkout_sha.png", "console checkout SHA", masks=((user, "<GITHUB_USER>"),))
    log(f"correlation: push={commit[:12]} build=#{number} cause=GitHub push SHA checkout={commit[:12]}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jenkins-base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:20080"))
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk-lab"))
    parser.add_argument("--build-timeout", type=int, default=240)
    parser.add_argument("--verify-latest", action="store_true")
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_main(lambda: flow(parse_args()))
