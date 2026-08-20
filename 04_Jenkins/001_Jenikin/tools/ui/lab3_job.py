#!/usr/bin/env python3
"""Create, build, assert, and capture the LAB 3 Pipeline through Jenkins UI."""

from __future__ import annotations

import os
import time
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, screenshot, wait_visible


ROOT = Path(__file__).resolve().parents[2]
JENKINSFILE = ROOT / "003_LAB_Docker_Build_Push" / "Jenkinsfile"
PIPELINE_SHOT = ROOT / "slides_assets" / "lab3_pipeline_docker.png"
LOG_SHOT = ROOT / "slides_assets" / "lab3_push_log.png"


def main() -> None:
    base_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:13080").rstrip("/")
    name = "docker-build-push"
    script = JENKINSFILE.read_text(encoding="utf-8")

    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        response = page.goto(f"{base_url}/job/{name}/", wait_until="domcontentloaded")
        if response is not None and response.status == 200:
            page.goto(f"{base_url}/job/{name}/configure", wait_until="domcontentloaded")
        else:
            page.goto(f"{base_url}/view/all/newJob", wait_until="domcontentloaded")
            page.locator("input[name='name']").fill(name)
            page.get_by_text("Pipeline", exact=True).click()
            page.get_by_role("button", name="OK").click()
        editor = wait_visible(page.locator(".ace_editor").last, "Pipeline script editor")
        editor.evaluate("(el, value) => window.ace.edit(el).setValue(value, -1)", script)
        require(editor.evaluate("el => window.ace.edit(el).getValue()") == script, "UI script equals the saved Jenkinsfile byte-for-byte")
        page.locator("button[name='Submit']").click()
        page.wait_for_load_state("domcontentloaded")
        require(f"/job/{name}/" in page.url, "docker-build-push job was created")

        page.get_by_text("Build Now", exact=True).click()
        page.wait_for_timeout(3000)
        deadline = time.monotonic() + 600
        console = ""
        while time.monotonic() < deadline:
            page.goto(f"{base_url}/job/{name}/lastBuild/console", wait_until="domcontentloaded")
            console = page.locator("body").inner_text()
            if "Finished: SUCCESS" in console:
                break
            require("Finished: FAILURE" not in console, "docker-build-push has not failed")
            page.wait_for_timeout(2000)
        require("Finished: SUCCESS" in console, "Docker build and push finished successfully")
        require("Login Succeeded" in console, "console reports Docker Hub login success")
        require("Masking supported pattern matches of $DOCKER_TOKEN" in console, "Jenkins enabled masking for the token binding")
        require("Docker token in console: ****" in console, "console shows the documented masking marker")
        require("digest: sha256:" in console, "console contains pushed manifest digest")
        require("ci-demo is ready" in console, "smoke test received the app response")

        console_pre = page.locator("pre").last
        pre_text = console_pre.inner_text()
        lines = pre_text.splitlines()
        first_line = next(i for i, line in enumerate(lines) if "Docker token in console: ****" in line)
        last_line = max(i for i, line in enumerate(lines) if "digest: sha256:" in line)
        pre_box = console_pre.bounding_box()
        line_height = console_pre.evaluate(
            "el => parseFloat(getComputedStyle(el).lineHeight) || parseFloat(getComputedStyle(el).fontSize) * 1.2"
        )
        require(pre_box is not None and line_height > 0, "console evidence has measurable bounds")
        page.set_viewport_size({"width": 1440, "height": 4600})
        pre_box = console_pre.bounding_box()
        require(pre_box is not None, "console remains measurable in the capture viewport")
        page.screenshot(
            path=str(LOG_SHOT),
            clip={
                "x": max(0, pre_box["x"] - 12),
                "y": max(0, pre_box["y"] + (first_line - 2) * line_height),
                "width": min(1300, pre_box["width"] + 24),
                "height": max(240, (last_line - first_line + 5) * line_height),
            },
        )
        log(f"screenshot: cropped masked login/push/digest evidence -> {LOG_SHOT}")

        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(f"{base_url}/job/{name}/lastBuild/stages/", wait_until="networkidle")
        wait_visible(page.get_by_text("Build & Push", exact=True).first, "Build & Push stage")
        wait_visible(page.get_by_text("Smoke test", exact=True).first, "Smoke test stage")
        require(page.locator(".PWGx-pipeline-node--success").count() >= 3, "latest Pipeline graph has green successful nodes")
        page.screenshot(path=str(PIPELINE_SHOT), full_page=False)
        log(f"screenshot: green docker-build-push Stage View -> {PIPELINE_SHOT}")


if __name__ == "__main__":
    run_main(main)
