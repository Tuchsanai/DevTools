#!/usr/bin/env python3
"""Create/configure LAB 6 Pipeline from SCM and GWT through Jenkins UI."""

from __future__ import annotations

import os
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


JOB_NAME = "webapp-deploy"
SCM_URL = "http://gitea:3000/student/webapp.git"
TOKEN = "cicd2569-webapp"


def select_option_by_text(locator, text: str) -> None:
    locator.select_option(label=text)


def assert_and_capture(page, scm_target: Path, trigger_target: Path) -> None:
    token_input = wait_visible(page.locator("input[name='_.token']"), "GWT token field")
    definition = page.locator("select").filter(has=page.locator("option", has_text="Pipeline script from SCM")).last
    wait_visible(definition, "Pipeline definition selector")
    require(token_input.input_value() == TOKEN, "Generic Webhook Trigger token is cicd2569-webapp")
    require(page.locator("input[name='_.url']").last.input_value() == SCM_URL, "Pipeline from SCM uses the canonical Gitea URL and main branch")
    require(page.locator("input[name='_.name']").last.input_value() == "*/main", "SCM branch is main")
    require(page.locator("input[name='_.scriptPath']").input_value() == "Jenkinsfile", "SCM script path is Jenkinsfile")

    trigger_target.parent.mkdir(parents=True, exist_ok=True)
    definition.evaluate("el => el.scrollIntoView({block: 'start'})")
    page.evaluate("window.scrollBy(0, -100)")
    page.screenshot(path=str(scm_target), full_page=False)
    log(f"screenshot: Pipeline from SCM configuration section -> {scm_target}")

    token_input.evaluate("el => el.scrollIntoView({block: 'center'})")
    page.screenshot(path=str(trigger_target), full_page=False)
    log(f"screenshot: Generic Webhook Trigger token section -> {trigger_target}")


def main() -> None:
    base_url = os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:16080").rstrip("/")
    scm_target = Path(os.environ.get("SCM_SCREENSHOT", "slides_assets/lab6_s03_job_scm.png"))
    trigger_target = Path(os.environ.get("TRIGGER_SCREENSHOT", "slides_assets/lab6_s04_job_trigger.png"))

    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        response = page.goto(f"{base_url}/job/{JOB_NAME}/", wait_until="domcontentloaded")
        if response is not None and response.status == 200:
            page.goto(f"{base_url}/job/{JOB_NAME}/configure", wait_until="domcontentloaded")
            assert_and_capture(page, scm_target, trigger_target)
            return
        else:
            page.goto(f"{base_url}/view/all/newJob", wait_until="domcontentloaded")
            wait_visible(page.locator("input[name='name']"), "new item name").fill(JOB_NAME)
            page.get_by_text("Pipeline", exact=True).click()
            page.get_by_role("button", name="OK").click()
            page.wait_for_load_state("domcontentloaded")

        trigger_text = page.get_by_text("Generic Webhook Trigger", exact=True).first
        wait_visible(trigger_text, "Generic Webhook Trigger option")
        trigger_checkbox = trigger_text.locator("xpath=ancestor::label[1]//input[@type='checkbox']")
        if trigger_checkbox.count() == 0:
            trigger_checkbox = trigger_text.locator("xpath=preceding::input[@type='checkbox'][1]")
        if not trigger_checkbox.is_checked():
            trigger_text.click()

        token_input = wait_visible(page.locator("input[name='_.token']"), "GWT token field")
        token_input.fill(TOKEN)

        # Jenkins 2.568 renders this hetero-list selector without a name.
        definition = page.locator("select").filter(has=page.locator("option", has_text="Pipeline script from SCM")).last
        wait_visible(definition, "Pipeline definition selector")
        select_option_by_text(definition, "Pipeline script from SCM")

        scm = page.locator("select").filter(has=page.locator("option", has_text="Git")).last
        wait_visible(scm, "SCM selector")
        select_option_by_text(scm, "Git")
        url_input = wait_visible(page.locator("input[name='_.url']"), "Git repository URL").last
        url_input.fill(SCM_URL)

        branch_inputs = page.locator("input[name='_.name']")
        branch_input = branch_inputs.last
        wait_visible(branch_input, "Git branch field").fill("*/main")
        script_path = wait_visible(page.locator("input[name='_.scriptPath']"), "Jenkinsfile path")
        script_path.fill("Jenkinsfile")

        page.locator("button[name='Submit']").click()
        page.wait_for_load_state("domcontentloaded")
        require(f"/job/{JOB_NAME}/" in page.url, "webapp-deploy job was saved")

        page.goto(f"{base_url}/job/{JOB_NAME}/configure", wait_until="domcontentloaded")
        assert_and_capture(page, scm_target, trigger_target)


if __name__ == "__main__":
    run_main(main)
