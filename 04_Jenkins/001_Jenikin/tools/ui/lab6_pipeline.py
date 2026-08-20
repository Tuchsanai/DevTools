#!/usr/bin/env python3
"""Wait for the webhook build, assert its stages/console, and capture Pipeline Graph."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "slides_assets" / "lab6_pipeline_full.png"


def main() -> None:
    base_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:16080").rstrip("/")
    minimum = int(os.getenv("EXPECTED_MIN_BUILD", "1"))

    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        deadline = time.monotonic() + 900
        build = None
        while time.monotonic() < deadline:
            response = page.goto(
                f"{base_url}/job/webapp-deploy/lastBuild/api/json?tree=number,result,building,actions[causes[shortDescription]]",
                wait_until="domcontentloaded",
            )
            if response is not None and response.status == 200:
                try:
                    build = json.loads(page.locator("body").inner_text())
                except json.JSONDecodeError:
                    build = None
                if build:
                    causes = [
                        cause.get("shortDescription", "")
                        for action in build.get("actions", [])
                        for cause in action.get("causes", [])
                    ]
                    webhook = any(any(word in cause.lower() for word in ("webhook", "gitea", "generic")) for cause in causes)
                    if build.get("number", 0) >= minimum and webhook and not build.get("building"):
                        break
            page.wait_for_timeout(2000)

        require(bool(build), "a webapp-deploy build exists")
        require(build.get("result") == "SUCCESS", "latest webhook build finished SUCCESS")
        number = build["number"]

        page.goto(f"{base_url}/job/webapp-deploy/{number}/console", wait_until="domcontentloaded")
        console = page.locator("body").inner_text()
        require("3 passed" in console, "pytest passed all three tests")
        require(console.index("3 passed") < console.index("The push refers to repository"), "tests ran before the first image push")
        require(f"{number}: digest: sha256:" in console, "BUILD_NUMBER tag push emitted a digest")
        require("latest: digest: sha256:" in console, "latest tag push emitted a digest")
        require("http://webapp:8000/health" in console, "Verify used Docker DNS instead of localhost")

        page.goto(f"{base_url}/job/webapp-deploy/{number}/stages/", wait_until="networkidle")
        for stage in ("Build-Test-Push", "Deploy", "Verify"):
            wait_visible(page.get_by_text(stage, exact=True).first, f"{stage} stage")
        require(page.locator(".PWGx-pipeline-node--success").count() >= 3, "full Pipeline graph has green successful nodes")
        page.screenshot(path=str(TARGET), full_page=False)
        log(f"screenshot: full green capstone Pipeline graph -> {TARGET}")


if __name__ == "__main__":
    run_main(main)
