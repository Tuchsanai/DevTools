#!/usr/bin/env python3
"""Create the public LAB 6 webapp repository through the Gitea UI."""

from __future__ import annotations

import os
from pathlib import Path

from common import browser_page, gitea_login, log, require, run_main, wait_visible


def main() -> None:
    base_url = os.getenv("GITEA_BASE_URL", "http://host.docker.internal:16300").rstrip("/")
    repo_url = f"{base_url}/student/webapp"
    form_target = Path(os.environ.get("FORM_SCREENSHOT", "slides_assets/lab6_s01_gitea_repo_form.png"))
    repo_target = Path(os.environ.get("REPO_SCREENSHOT", "slides_assets/lab6_s02_gitea_repo_after_push.png"))

    with browser_page() as (_, _, _, page):
        gitea_login(page, base_url)
        if os.getenv("CAPTURE_FORM_ONLY") == "1":
            page.goto(f"{base_url}/repo/create", wait_until="domcontentloaded")
            wait_visible(page.locator("input[name='repo_name']"), "repository name field").fill("webapp")
            default_branch = page.locator("input[name='default_branch']")
            if default_branch.count():
                default_branch.fill("main")
            private = page.locator("input[name='private']")
            if private.count() and private.is_checked():
                private.uncheck()
            form_target.parent.mkdir(parents=True, exist_ok=True)
            page.locator("input[name='repo_name']").evaluate("el => el.scrollIntoView({block: 'center'})")
            page.screenshot(path=str(form_target), full_page=False)
            log(f"screenshot: public webapp repository creation form -> {form_target}")
            return
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
            form_target.parent.mkdir(parents=True, exist_ok=True)
            page.locator("input[name='repo_name']").evaluate("el => el.scrollIntoView({block: 'center'})")
            page.screenshot(path=str(form_target), full_page=False)
            log(f"screenshot: public webapp repository creation form -> {form_target}")
            page.get_by_role("button", name="Create Repository").click()
            page.wait_for_load_state("domcontentloaded")

        require("/student/webapp" in page.url, "student/webapp repository exists")
        body = page.locator("body").inner_text()
        require("Private" not in body, "student/webapp repository is public")
        if page.get_by_text("Jenkinsfile", exact=True).count():
            repo_target.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(repo_target), full_page=False)
            log(f"screenshot: webapp repository after push with required files -> {repo_target}")


if __name__ == "__main__":
    run_main(main)
