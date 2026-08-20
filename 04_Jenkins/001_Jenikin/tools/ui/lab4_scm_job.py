#!/usr/bin/env python3
"""Configure Pipeline from GitHub SCM through Jenkins UI and run a manual build."""

from __future__ import annotations

import argparse
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from common import browser_page, jenkins_login, require, run_main, wait_visible
from lab4_capture import masked_screenshot


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"
JOB = "hello-ci-pipeline"


def api_json(page, url: str) -> dict:
    response = page.request.get(url)
    require(response.ok, f"API {url} returned HTTP {response.status}")
    return response.json()


def last_build_number(page, base_url: str) -> int:
    build = api_json(page, f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number]").get("lastBuild")
    return 0 if build is None else int(build["number"])


def choose_option_containing(select, text: str) -> None:
    options = select.locator("option")
    for index in range(options.count()):
        if text.casefold() in options.nth(index).inner_text().casefold():
            select.select_option(index=index)
            return
    raise AssertionError(f"select has no option containing {text!r}")


def select_with_exact_option(form, text: str):
    selects = form.locator("select")
    for index in range(selects.count()):
        select = selects.nth(index)
        values = [select.locator("option").nth(i).inner_text().strip() for i in range(select.locator("option").count())]
        if text in values:
            return select
    raise AssertionError(f"form has no select with exact option {text!r}")


def open_configuration(page, base_url: str, user: str) -> None:
    response = page.goto(f"{base_url}/job/{JOB}/configure", wait_until="domcontentloaded")
    if response is not None and response.status == 200:
        return
    page.goto(f"{base_url}/view/all/newJob", wait_until="domcontentloaded")
    name = wait_visible(page.locator("input[name='name']"), "New Item name")
    name.fill(JOB)
    page.get_by_text("Pipeline", exact=True).click()
    masked_screenshot(
        page,
        ASSETS / "lab4_s04_jenkins_new_item.png",
        "New Item with hello-ci-pipeline and Pipeline selected",
        mask_texts=(user,),
    )
    page.get_by_role("button", name="OK").click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/configure"))


def configure_scm(page, base_url: str, user: str) -> None:
    open_configuration(page, base_url, user)
    form = wait_visible(page.locator("form[name='config']"), "hello-ci-pipeline configuration form")
    definition = form.locator("select").filter(has_text="Pipeline script from SCM").last
    choose_option_containing(wait_visible(definition, "Pipeline Definition selector"), "Pipeline script from SCM")
    git_option = form.locator("select option").filter(has_text=re.compile(r"^\s*Git\s*$")).first
    git_option.wait_for(state="attached", timeout=10000)
    scm = select_with_exact_option(form, "Git")
    choose_option_containing(wait_visible(scm, "SCM selector"), "Git")

    url = wait_visible(form.locator("input[name='_.url']").last, "Git repository URL")
    url.fill(f"https://github.com/{user}/hello-ci.git")
    url.press("Tab")
    branch = form.locator("input[name='_.name']").last
    branch.fill("*/main")
    script_path = form.locator("input[name='_.scriptPath']")
    require(script_path.count() == 1, "Script Path field exists")
    script_path.fill("Jenkinsfile")

    page.set_viewport_size({"width": 1440, "height": 1200})
    definition.evaluate("el => el.scrollIntoView({block: 'start'})")
    page.wait_for_timeout(3000)
    masked_screenshot(
        page,
        ASSETS / "lab4_s05_jenkins_scm_config.png",
        "Pipeline script from GitHub SCM configuration",
        mask_texts=(user,),
        mask_locators=((url, "https://github.com/<GITHUB_USER>/hello-ci.git"),),
    )
    submit = page.locator("button[name='Submit']")
    submit.scroll_into_view_if_needed()
    page.wait_for_timeout(500)
    masked_screenshot(
        page,
        ASSETS / "lab4_s05b_scm_save.png",
        "SCM configuration ready to save",
        mask_texts=(user,),
    )
    submit.click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/?$"))
    require(page.url.rstrip("/").endswith(f"/job/{JOB}"), "SCM job configuration saved through UI")


def assert_saved_contract(page, base_url: str, user: str) -> None:
    response = page.request.get(f"{base_url}/job/{JOB}/config.xml")
    require(response.ok, "hello-ci-pipeline config.xml is readable")
    root = ET.fromstring(response.text())
    definition = root.find("definition")
    require(definition is not None and definition.attrib.get("class") == "org.jenkinsci.plugins.workflow.cps.CpsScmFlowDefinition", "job definition is Pipeline script from SCM")
    assert definition is not None
    require(definition.findtext("./scm/userRemoteConfigs/hudson.plugins.git.UserRemoteConfig/url") == f"https://github.com/{user}/hello-ci.git", "saved SCM URL is the anonymous GitHub HTTPS URL")
    require(definition.findtext("./scm/branches/hudson.plugins.git.BranchSpec/name") in {"main", "*/main"}, "saved branch is main")
    require(definition.findtext("scriptPath") == "Jenkinsfile", "saved Script Path is Jenkinsfile")
    require(not definition.findall(".//credentialsId"), "public repository checkout has no credentialsId")


def build_and_assert(page, base_url: str, user: str) -> None:
    baseline = last_build_number(page, base_url)
    page.goto(f"{base_url}/job/{JOB}/", wait_until="domcontentloaded")
    build_now = page.get_by_role("link", name=re.compile(r"Build Now", re.I))
    build_now.scroll_into_view_if_needed()
    masked_screenshot(page, ASSETS / "lab4_s06a_build_now.png", "Build Now action", mask_texts=(user,))
    build_now.click()
    deadline = time.monotonic() + 300
    number = baseline
    result = None
    while time.monotonic() < deadline:
        build = api_json(page, f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number,building,result]").get("lastBuild") or {}
        number = int(build.get("number", 0))
        if number > baseline and not build.get("building", True):
            result = build.get("result")
            break
        page.wait_for_timeout(1000)
    require(number > baseline and result == "SUCCESS", f"manual build #{number} finished SUCCESS")
    console = page.request.get(f"{base_url}/job/{JOB}/{number}/consoleText")
    require(console.ok and "Checking out Revision" in console.text(), "console proves a real Git checkout")
    require("Hello from GitHub" in console.text(), "repository test script printed Hello from GitHub")
    require("Finished: SUCCESS" in console.text(), "console ended with SUCCESS")
    page.goto(f"{base_url}/job/{JOB}/{number}/", wait_until="domcontentloaded")
    console_link = page.get_by_role("link", name=re.compile(r"Console Output", re.I))
    console_link.scroll_into_view_if_needed()
    masked_screenshot(page, ASSETS / "lab4_s06b_open_console.png", "open Console Output action", mask_texts=(user,))
    console_link.click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/{number}/console"))
    evidence = page.get_by_text("Hello from GitHub", exact=False).last
    evidence.scroll_into_view_if_needed()
    masked_screenshot(page, ASSETS / "lab4_s06_manual_build_console.png", "manual SCM build console", mask_texts=(user,))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", choices=("configure", "build"), required=True)
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:20080"))
    args = parser.parse_args()
    user = os.environ.get("GITHUB_USER", "")
    require(bool(user), "GITHUB_USER is set")
    base_url = args.base_url.rstrip("/")
    with browser_page() as (_, _, _, page):
        jenkins_login(page, base_url)
        if args.action == "configure":
            configure_scm(page, base_url, user)
            assert_saved_contract(page, base_url, user)
        else:
            assert_saved_contract(page, base_url, user)
            build_and_assert(page, base_url, user)


if __name__ == "__main__":
    run_main(main)
