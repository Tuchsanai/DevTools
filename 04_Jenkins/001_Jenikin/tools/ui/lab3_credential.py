#!/usr/bin/env python3
"""Create the LAB 3 Docker Hub credential through the Jenkins UI."""

from __future__ import annotations

import os
import re

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


def main() -> None:
    base_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:13080").rstrip("/")
    docker_user = os.environ.get("DOCKER_USER", "")
    docker_token = os.environ.get("DOCKER_TOKEN", "")
    require(bool(docker_user and docker_token), "Docker Hub credential environment is present")

    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        credentials_url = f"{base_url}/manage/credentials/store/system/domain/_/"
        page.goto(credentials_url, wait_until="domcontentloaded")
        if page.get_by_text("dockerhub", exact=True).count():
            require(page.get_by_text("dockerhub", exact=True).is_visible(), "credential id dockerhub is listed")
            log("credential already exists; no secret value was read")
            return
        page.get_by_text("Add Credentials", exact=True).click()
        page.get_by_text("Username with password", exact=True).click()
        page.get_by_role("button", name="Next").click()
        wait_visible(page.locator("input[name='_.username']"), "Username with password form")
        page.locator("input[name='_.username']").fill(docker_user)
        page.locator("input[name='_.password']").fill(docker_token)
        page.locator("input[name='_.id']").fill("dockerhub")
        page.locator("input[name='_.description']").fill(
            "Docker Hub Read/Write access token for LAB 3"
        )
        page.get_by_role("button", name="Create").click()
        page.wait_for_url(
            re.compile(r"/manage/credentials/store/system/domain/_/?$"),
            wait_until="domcontentloaded",
        )
        credential_id = wait_visible(
            page.get_by_text("dockerhub", exact=True),
            "credential id dockerhub in credential list",
        )
        require(credential_id.is_visible(), "credential id dockerhub is listed")
        log("credential saved without printing username or token")


if __name__ == "__main__":
    run_main(main)
