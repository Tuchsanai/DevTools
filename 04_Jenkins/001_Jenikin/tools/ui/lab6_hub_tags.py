#!/usr/bin/env python3
"""Capture the real public Hub page showing BUILD_NUMBER and latest."""

from __future__ import annotations

import base64
import json
import os
import urllib.request
from pathlib import Path

from common import browser_page, require, run_main, screenshot, wait_visible


ROOT = Path(__file__).resolve().parents[2]
TARGET = ROOT / "slides_assets" / "lab6_hub_tags.png"


def latest_build_number(jenkins_url: str) -> str:
    request = urllib.request.Request(f"{jenkins_url}/job/webapp-deploy/lastBuild/api/json?tree=number")
    encoded = base64.b64encode(b"admin:admin2569").decode("ascii")
    request.add_header("Authorization", f"Basic {encoded}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return str(json.load(response)["number"])


def main() -> None:
    docker_user = os.environ.get("DOCKER_USER", "")
    jenkins_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:16080").rstrip("/")
    require(bool(docker_user), "public Docker Hub username is present")
    build_number = latest_build_number(jenkins_url)
    url = f"https://hub.docker.com/r/{docker_user}/cicd-webapp/tags"

    with browser_page() as (_, _, context, page):
        context.clear_cookies()
        response = page.goto(url, wait_until="domcontentloaded", timeout=120000)
        require(response is not None and response.status == 200, "Docker Hub Tags page returns HTTP 200 anonymously")
        wait_visible(page.get_by_text("cicd-webapp", exact=False).first, "cicd-webapp repository title", 120000)
        wait_visible(page.get_by_text(build_number, exact=True).first, f"new build tag {build_number}", 120000)
        wait_visible(page.get_by_text("latest", exact=True).first, "latest tag", 120000)
        require("/cicd-webapp/tags" in page.url, "browser remains on the public cicd-webapp Tags page")
        screenshot(page, TARGET, "real public Hub page with current build and latest tags")


if __name__ == "__main__":
    run_main(main)
