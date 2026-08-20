#!/usr/bin/env python3
"""Create and run the small Pipeline used to prove Docker CLI access."""

from __future__ import annotations

import os
import time

from common import browser_page, jenkins_login, require, run_main, wait_visible


SCRIPT = """pipeline {
  agent any
  stages {
    stage('Docker ready') {
      steps { sh 'docker version' }
    }
  }
}
"""


def main() -> None:
    base_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:13080").rstrip("/")
    name = "docker-version-check"
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
        editor.evaluate("(el, value) => window.ace.edit(el).setValue(value, -1)", SCRIPT)
        require(editor.evaluate("el => window.ace.edit(el).getValue()") == SCRIPT, "Docker version Pipeline script is set")
        page.locator("button[name='Submit']").click()
        page.wait_for_load_state("domcontentloaded")
        page.get_by_text("Build Now", exact=True).click()
        page.wait_for_timeout(3000)
        deadline = time.monotonic() + 120
        body = ""
        while time.monotonic() < deadline:
            page.goto(f"{base_url}/job/{name}/lastBuild/console", wait_until="domcontentloaded")
            body = page.locator("body").inner_text()
            if "Finished: SUCCESS" in body:
                break
            require("Finished: FAILURE" not in body, "Docker version Pipeline has not failed")
            page.wait_for_timeout(2000)
        require("Finished: SUCCESS" in body, "Docker version Pipeline finished successfully")
        require("Client:" in body and "Server:" in body, "docker version reports both client and server")


if __name__ == "__main__":
    run_main(main)
