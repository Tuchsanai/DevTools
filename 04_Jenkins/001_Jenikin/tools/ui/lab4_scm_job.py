#!/usr/bin/env python3
"""Configure Pipeline from SCM, build it, assert checkout, and capture Jenkins UI."""

from __future__ import annotations

import argparse
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


ROOT = Path(__file__).resolve().parents[2]
SCM_SHOT = ROOT / "slides_assets" / "lab4_jenkins_scm.png"
JOB = "hello-ci-pipeline"


def api_json(page, url: str) -> dict:
    response = page.request.get(url)
    require(response.ok, f"API {url} returned HTTP {response.status}")
    return response.json()


def last_build_number(page, base_url: str) -> int:
    data = api_json(page, f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number]")
    build = data.get("lastBuild")
    return 0 if build is None else int(build["number"])


def choose_option_containing(select, text: str) -> None:
    options = select.locator("option")
    for index in range(options.count()):
        option = options.nth(index)
        if text.lower() in option.inner_text().lower():
            select.select_option(index=index)
            return
    raise AssertionError(f"select has no option containing {text!r}")


def open_configuration(page, base_url: str) -> None:
    response = page.goto(f"{base_url}/job/{JOB}/configure", wait_until="domcontentloaded")
    if response is not None and response.status == 200:
        return
    page.goto(f"{base_url}/view/all/newJob", wait_until="domcontentloaded")
    page.locator("input[name='name']").fill(JOB)
    page.get_by_text("Pipeline", exact=True).click()
    page.get_by_role("button", name="OK").click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/configure"))


def configure_scm(page, base_url: str) -> None:
    open_configuration(page, base_url)
    form = wait_visible(page.locator("form[name='config']"), "hello-ci-pipeline configuration form")

    definition = form.locator("select").filter(has_text="Pipeline script from SCM").last
    wait_visible(definition, "Pipeline Definition selector")
    choose_option_containing(definition, "Pipeline script from SCM")

    scm = wait_visible(form.locator("select").filter(has_text="None").filter(has_text="Git").last, "SCM selector")
    choose_option_containing(scm, "Git")

    url = wait_visible(form.locator("input[name='_.url']").last, "Git repository URL")
    url.fill("http://gitea:3000/student/hello-ci.git")

    branch_fields = form.locator("input[name='_.name']")
    require(branch_fields.count() >= 1, "branch specifier field exists")
    branch_fields.last.fill("*/main")

    script_path = form.locator("input[name='_.scriptPath']")
    require(script_path.count() == 1, "Script Path field exists")
    script_path.fill("Jenkinsfile")

    pipeline_section = form.locator(".jenkins-section").filter(has_text="Pipeline").last
    wait_visible(pipeline_section, "Pipeline from SCM section")
    pipeline_section.scroll_into_view_if_needed()
    pipeline_section.screenshot(path=str(SCM_SHOT))
    log(f"screenshot: Pipeline from SCM configuration -> {SCM_SHOT}")

    page.locator("button[name='Submit']").click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/?$"))
    require(page.url.rstrip("/").endswith(f"/job/{JOB}"), "SCM job configuration saved through UI")


def assert_saved_contract(page, base_url: str) -> None:
    response = page.request.get(f"{base_url}/job/{JOB}/config.xml")
    require(response.ok, "hello-ci-pipeline config.xml is readable")
    root = ET.fromstring(response.text())
    definition = root.find("definition")
    require(
        definition is not None
        and definition.attrib.get("class") == "org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition",
        "job definition is Pipeline script from SCM",
    )
    require(
        definition.findtext("./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url")
        == "http://gitea:3000/student/hello-ci.git",
        "saved SCM URL uses the gitea container DNS name",
    )
    require(
        definition.findtext("./scm/branches/hudson.plugins.git.BranchSpec/name") in {"main", "*/main"},
        "saved branch is main",
    )
    require(definition.findtext("scriptPath") == "Jenkinsfile", "saved Script Path is Jenkinsfile")
    require(not definition.findall(".//credentialsId"), "public repository checkout has no credential")


def build_and_assert(page, base_url: str) -> None:
    baseline = last_build_number(page, base_url)
    page.goto(f"{base_url}/job/{JOB}/", wait_until="domcontentloaded")
    page.get_by_role("link", name=re.compile(r"Build Now", re.I)).click()

    deadline = time.monotonic() + 180
    number = baseline
    result = None
    while time.monotonic() < deadline:
        data = api_json(page, f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number,building,result]")
        build = data.get("lastBuild") or {}
        number = int(build.get("number", 0))
        if number > baseline and not build.get("building", True):
            result = build.get("result")
            break
        page.wait_for_timeout(1000)
    require(number > baseline and result == "SUCCESS", f"manual build #{number} finished SUCCESS")

    console_response = page.request.get(f"{base_url}/job/{JOB}/{number}/consoleText")
    require(console_response.ok, f"console for build #{number} is readable")
    console = console_response.text()
    require(
        "Checking out Revision" in console or "Cloning the remote Git repository" in console,
        "console proves a real Git checkout",
    )
    require("Hello from Gitea" in console, "repository test script ran")
    require("Finished: SUCCESS" in console, "console ended with SUCCESS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("configure", "build"), required=True)
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:14080"))
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")
    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        if args.action == "configure":
            configure_scm(page, base_url)
            assert_saved_contract(page, base_url)
        else:
            assert_saved_contract(page, base_url)
            build_and_assert(page, base_url)


if __name__ == "__main__":
    run_main(main)
