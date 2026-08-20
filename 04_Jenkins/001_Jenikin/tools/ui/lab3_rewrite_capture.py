#!/usr/bin/env python3
"""Capture the expanded LAB 3 Jenkins flow and its public Hub proof."""

from __future__ import annotations

import os
import time
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"
JENKINSFILE = ROOT / "003_LAB_Docker_Build_Push" / "Jenkinsfile"


def shot(page, name: str, description: str) -> None:
    target = ASSETS / name
    page.screenshot(path=str(target), full_page=False)
    log(f"screenshot: {description} -> {target}")


def wait_for_success(page, base_url: str, name: str) -> str:
    deadline = time.monotonic() + 600
    console = ""
    while time.monotonic() < deadline:
        page.goto(f"{base_url}/job/{name}/lastBuild/console", wait_until="domcontentloaded")
        console = page.locator("body").inner_text()
        if "Finished: SUCCESS" in console:
            return console
        require("Finished: FAILURE" not in console, f"{name} has not failed")
        page.wait_for_timeout(2000)
    raise AssertionError(f"timeout waiting for {name}")


def main() -> None:
    base_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:13080").rstrip("/")
    docker_user = os.environ.get("DOCKER_USER", "")
    docker_token = os.environ.get("DOCKER_TOKEN", "")
    require(bool(docker_user and docker_token), "Docker Hub credential environment is present")
    script = JENKINSFILE.read_text(encoding="utf-8")

    with browser_page() as (_, _, _, page):
        page.set_viewport_size({"width": 1440, "height": 1000})
        jenkins_login(page, base_url)

        page.goto(f"{base_url}/", wait_until="domcontentloaded")
        page.get_by_text("Manage Jenkins", exact=True).click()
        wait_visible(page.get_by_text("Credentials", exact=True).first, "Credentials entry in Manage Jenkins")
        shot(page, "lab3_s01_manage_jenkins.png", "Manage Jenkins menu with Credentials entry")

        page.get_by_text("Credentials", exact=True).first.click()
        wait_visible(page.get_by_text("System", exact=True).first, "System credentials store")
        page.goto(
            f"{base_url}/manage/credentials/store/system/domain/_/",
            wait_until="domcontentloaded",
        )
        wait_visible(page.get_by_text("Add Credentials", exact=True), "Add Credentials action")
        shot(page, "lab3_s02_global_credentials.png", "Global credentials page before adding dockerhub")

        page.get_by_text("Add Credentials", exact=True).click()
        page.get_by_text("Username with password", exact=True).click()
        page.get_by_role("button", name="Next").click()
        username = wait_visible(page.locator("input[name='_.username']"), "Username with password form")
        password = page.locator("input[name='_.password']")
        username.fill("<DOCKER_USER>")
        password.fill("<DOCKER_TOKEN>")
        page.locator("input[name='_.id']").fill("dockerhub")
        page.locator("input[name='_.description']").fill("Docker Hub Read/Write access token for LAB 3")
        shot(page, "lab3_s03_add_credential_form.png", "completed credential form containing placeholders only")
        require(username.input_value() == "<DOCKER_USER>", "captured username is the literal placeholder")

        # Replace placeholders only after capture; actual values are never logged or persisted in an image.
        username.fill(docker_user)
        password.fill(docker_token)
        page.get_by_role("button", name="Create").click()
        wait_visible(page.get_by_text("dockerhub", exact=True), "dockerhub credential in Global credentials")
        log("credential submitted without printing its username or token")

        page.goto(f"{base_url}/view/all/newJob", wait_until="domcontentloaded")
        item_name = wait_visible(page.locator("input[name='name']"), "New Item name")
        item_name.fill("docker-build-push")
        page.get_by_text("Pipeline", exact=True).click()
        shot(page, "lab3_s04_new_item_pipeline.png", "New Item with docker-build-push and Pipeline selected")
        page.get_by_role("button", name="OK").click()

        editor = wait_visible(page.locator(".ace_editor").last, "Pipeline script editor")
        editor.evaluate("(el, value) => window.ace.edit(el).setValue(value, -1)", script)
        require(editor.evaluate("el => window.ace.edit(el).getValue()") == script, "Pipeline script equals Jenkinsfile")
        editor.scroll_into_view_if_needed()
        shot(page, "lab3_s05_pipeline_script.png", "Pipeline script filled in the Jenkins editor")
        page.locator("button[name='Submit']").click()
        page.wait_for_load_state("domcontentloaded")
        page.get_by_text("Build Now", exact=True).click()

        console = wait_for_success(page, base_url, "docker-build-push")
        require("Login Succeeded" in console, "console reports Docker Hub login success")
        require("digest: sha256:" in console, "console reports the pushed digest")
        require("Masking supported pattern matches of $DOCKER_TOKEN" in console, "credential masking is active")

        log("build proof is ready for the privacy-focused evidence capture")


if __name__ == "__main__":
    run_main(main)
