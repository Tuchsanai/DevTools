#!/usr/bin/env python3
"""Create the public LAB 6 webapp repository through the Gitea UI."""

from __future__ import annotations

import os

from common import browser_page, gitea_login, require, run_main, wait_visible


def main() -> None:
    base_url = os.getenv("GITEA_BASE_URL", "http://host.docker.internal:16300").rstrip("/")
    repo_url = f"{base_url}/student/webapp"

    with browser_page() as (_, _, _, page):
        gitea_login(page, base_url)
        response = page.goto(repo_url, wait_until="domcontentloaded")
        if response is None or response.status == 404:
            page.goto(f"{base_url}/repo/create", wait_until="domcontentloaded")
            wait_visible(page.locator("input[name='repo_name']"), "repository name field").fill("webapp")
            default_branch = page.locator("input[name='default_branch']")
            if default_branch.count():
                default_branch.fill("main")
            private = page.locator("input[name='private']")
            if private.count() and private.is_checked():
                private.uncheck()
            page.get_by_role("button", name="Create Repository").click()
            page.wait_for_load_state("domcontentloaded")

        require("/student/webapp" in page.url, "student/webapp repository exists")
        body = page.locator("body").inner_text()
        require("Private" not in body, "student/webapp repository is public")


if __name__ == "__main__":
    run_main(main)
