#!/usr/bin/env python3
"""Create and verify the public hello-ci repository through the Gitea UI."""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from common import browser_page, gitea_login, log, require, run_main, screenshot, wait_visible


ROOT = Path(__file__).resolve().parents[2]
REPO_SHOT = ROOT / "slides_assets" / "lab4_gitea_repo.png"


def create_repo(page, base_url: str) -> None:
    response = page.goto(f"{base_url}/student/hello-ci", wait_until="domcontentloaded")
    if response is not None and response.status == 200:
        log("student/hello-ci already exists; keeping the current repository")
        return

    page.goto(f"{base_url}/repo/create", wait_until="domcontentloaded")
    repo_name = wait_visible(page.locator("input[name='repo_name']"), "repository name field")
    repo_name.fill("hello-ci")

    private = page.locator("input[name='private']")
    if private.count() and private.first.is_checked():
        private.first.uncheck()
    auto_init = page.locator("input[name='auto_init']")
    if auto_init.count() and auto_init.first.is_checked():
        auto_init.first.uncheck()

    page.get_by_role("button", name="Create Repository").click()
    page.wait_for_url(lambda url: "/student/hello-ci" in url and "/repo/create" not in url)
    require(page.url.rstrip("/").endswith("/student/hello-ci"), "public hello-ci repository was created")


def assert_public_repo(page, base_url: str, require_files: bool) -> None:
    response = page.request.get(f"{base_url}/api/v1/repos/student/hello-ci")
    require(response.ok, f"Gitea repository API returned HTTP {response.status}")
    data = response.json()
    require(data.get("full_name") == "student/hello-ci", "repository full name is student/hello-ci")
    require(data.get("private") is False, "hello-ci is public")

    page.goto(f"{base_url}/student/hello-ci", wait_until="domcontentloaded")
    wait_visible(page.locator("body"), "hello-ci repository page")
    if require_files:
        body = page.locator("body").inner_text()
        for filename in ("Jenkinsfile", "hello.sh", "expected.txt"):
            require(filename in body, f"repository page lists {filename}")
        require("main" in body, "repository page shows branch main")
        screenshot(page, REPO_SHOT, "Gitea hello-ci main branch with project files and Jenkinsfile")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("GITEA_BASE_URL", "http://host.docker.internal:14300"))
    parser.add_argument("--action", choices=("create", "verify"), required=True)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    with browser_page() as (_, _, _, page):
        gitea_login(page, base_url)
        if args.action == "create":
            create_repo(page, base_url)
        assert_public_repo(page, base_url, require_files=args.action == "verify")


if __name__ == "__main__":
    run_main(main)
