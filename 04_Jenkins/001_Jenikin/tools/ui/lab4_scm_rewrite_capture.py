#!/usr/bin/env python3
"""Capture the complete LAB 4 Gitea and Jenkins SCM teaching flow."""

from __future__ import annotations

import argparse
import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from common import browser_page, gitea_login, jenkins_login, log, require, run_main, wait_visible


ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"
JOB = "hello-ci-pipeline"


def shot(page, filename: str, description: str) -> None:
    target = ASSETS / filename
    page.screenshot(path=str(target), full_page=False)
    log(f"screenshot: {description} -> {target}")


def fill_if_present(page, name: str, value: str) -> None:
    field = page.locator(f"[name='{name}']")
    if field.count() and field.first.is_visible():
        field.first.fill(value)


def install_gitea(page, base_url: str) -> None:
    page.goto(base_url, wait_until="domcontentloaded", timeout=60_000)
    form = wait_visible(page.locator("form"), "Gitea initial configuration form", 60_000)
    database = form.locator("select[name='db_type']")
    if database.count():
        database.select_option("SQLite3")
    fill_if_present(page, "db_path", "/data/gitea/gitea.db")
    fill_if_present(page, "domain", "localhost")
    fill_if_present(page, "http_port", "3000")
    fill_if_present(page, "app_url", "http://localhost:3000/")
    disable_ssh = page.locator("input[name='disable_ssh']")
    if disable_ssh.count() and disable_ssh.first.is_visible() and not disable_ssh.first.is_checked():
        disable_ssh.first.check()

    app_url = wait_visible(page.locator("input[name='app_url']"), "canonical Gitea Base URL")
    app_url.scroll_into_view_if_needed()
    page.evaluate("document.body.style.zoom='80%'")
    page.wait_for_timeout(300)
    shot(page, "lab4_s01_gitea_install_form.png", "Gitea installer with canonical server values")

    page.evaluate("document.body.style.zoom='100%'")
    page.get_by_role("button", name="Install Gitea").click()
    page.wait_for_url(lambda url: "/install" not in url, timeout=600_000)
    wait_visible(page.locator("body"), "Gitea after installation", 120_000)


def register_student(page, base_url: str) -> None:
    page.goto(f"{base_url}/user/sign_up", wait_until="domcontentloaded")
    wait_visible(page.locator("input[name='user_name']"), "Gitea registration form").fill("student")
    page.locator("input[name='email']").fill("student@example.com")
    page.locator("input[name='password']").fill("student2569")
    confirm = page.locator("input[name='retype']")
    if not confirm.count():
        confirm = page.locator("input[name='password2']")
    require(confirm.count() == 1, "registration password confirmation field exists")
    confirm.fill("student2569")
    shot(page, "lab4_s02_student_registration.png", "student registration form with canonical fixture values")
    page.get_by_role("button", name=re.compile(r"Register|Sign Up", re.I)).click()
    page.wait_for_url(lambda url: "/user/sign_up" not in url)
    require("/user/sign_up" not in page.url, "student account registered through the UI")


def create_repo(page, base_url: str, *, submit: bool = True) -> None:
    gitea_login(page, base_url)
    page.goto(f"{base_url}/repo/create", wait_until="domcontentloaded")
    wait_visible(page.locator("input[name='repo_name']"), "new repository form").fill("hello-ci")
    private = page.locator("input[name='private']")
    if private.count() and private.first.is_checked():
        private.first.uncheck()
    auto_init = page.locator("input[name='auto_init']")
    if auto_init.count() and auto_init.first.is_checked():
        auto_init.first.uncheck()
    page.evaluate("document.body.style.zoom='65%'")
    page.locator("input[name='repo_name']").scroll_into_view_if_needed()
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(300)
    shot(page, "lab4_s03_hello_repo_form.png", "public hello-ci repository creation form")
    if not submit:
        return
    page.evaluate("document.body.style.zoom='100%'")
    page.get_by_role("button", name="Create Repository").click()
    page.wait_for_url(lambda url: "/student/hello-ci" in url and "/repo/create" not in url)


def capture_repo(page, base_url: str) -> None:
    gitea_login(page, base_url)
    page.goto(f"{base_url}/student/hello-ci", wait_until="domcontentloaded")
    body = page.locator("body").inner_text()
    for filename in ("Jenkinsfile", "hello.sh", "expected.txt"):
        require(filename in body, f"repository page lists {filename}")
    require("main" in body, "repository page shows branch main")
    shot(page, "lab4_s04_repo_files.png", "hello-ci main branch with all project files")


def choose_option_containing(select, text: str) -> None:
    options = select.locator("option")
    for index in range(options.count()):
        if text.lower() in options.nth(index).inner_text().lower():
            select.select_option(index=index)
            return
    raise AssertionError(f"select has no option containing {text!r}")


def select_with_exact_option(form, text: str):
    selects = form.locator("select")
    for index in range(selects.count()):
        select = selects.nth(index)
        options = select.locator("option")
        if any(options.nth(i).inner_text().strip() == text for i in range(options.count())):
            return select
    raise AssertionError(f"form has no select with exact option {text!r}")


def create_job_and_configure(page, base_url: str) -> None:
    jenkins_login(page, base_url)
    response = page.goto(f"{base_url}/job/{JOB}/configure", wait_until="domcontentloaded")
    if response is None or response.status != 200:
        page.goto(f"{base_url}/view/all/newJob", wait_until="domcontentloaded")
        wait_visible(page.locator("input[name='name']"), "Jenkins New Item form").fill(JOB)
        page.get_by_text("Pipeline", exact=True).click()
        shot(page, "lab4_s05_new_pipeline_item.png", "New Item form for hello-ci-pipeline")
        page.get_by_role("button", name="OK").click()
        page.wait_for_url(re.compile(rf"/job/{JOB}/configure"))

    form = wait_visible(page.locator("form[name='config']"), "hello-ci-pipeline configuration form")
    definition = form.locator("select").filter(has_text="Pipeline script from SCM").last
    wait_visible(definition, "Pipeline Definition selector")
    choose_option_containing(definition, "Pipeline script from SCM")
    scm = wait_visible(select_with_exact_option(form, "Git"), "SCM selector")
    choose_option_containing(scm, "Git")
    wait_visible(form.locator("input[name='_.url']").last, "Git repository URL").fill(
        "http://gitea:3000/student/hello-ci.git"
    )
    form.locator("input[name='_.name']").last.fill("*/main")
    form.locator("input[name='_.scriptPath']").fill("Jenkinsfile")
    browser = select_with_exact_option(form, "(Auto)")
    browser.select_option(label="(Auto)")
    pipeline = form.locator(".jenkins-section").filter(has_text="Pipeline").last
    page.evaluate("document.body.style.zoom='70%'")
    pipeline.evaluate("element => element.scrollIntoView({block: 'start'})")
    page.evaluate("window.scrollBy(0, -70)")
    page.wait_for_timeout(300)
    shot(page, "lab4_s06_pipeline_from_scm.png", "Pipeline script from SCM with canonical Gitea URL")
    page.locator("button[name='Submit']").click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/?$"))


def configure_poll(page, base_url: str) -> int:
    jenkins_login(page, base_url)
    response = page.request.get(f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number]")
    require(response.ok, "job API is readable before enabling Poll SCM")
    last = response.json().get("lastBuild")
    baseline = 0 if last is None else int(last["number"])
    page.goto(f"{base_url}/job/{JOB}/configure", wait_until="domcontentloaded")
    form = wait_visible(page.locator("form[name='config']"), "job configuration form")
    label = wait_visible(form.get_by_text("Poll SCM", exact=True), "Poll SCM trigger")
    item = label.locator("xpath=ancestor::*[contains(@class,'jenkins-form-item')][1]")
    checkbox = item.locator("input[type='checkbox']")
    if not checkbox.count():
        checkbox = form.locator("input[name='hudson-triggers-SCMTrigger']")
    if not checkbox.first.is_checked():
        label.click()
    spec = wait_visible(form.locator("textarea[name='_.scmpoll_spec']").first, "Poll SCM schedule")
    spec.fill("* * * * *")
    spec.blur()
    page.wait_for_timeout(700)
    item.scroll_into_view_if_needed()
    shot(page, "lab4_s08_poll_scm_trigger.png", "Build Triggers with Poll SCM and every-minute schedule")
    page.locator("button[name='Submit']").click()
    page.wait_for_url(re.compile(rf"/job/{JOB}/?$"))
    config = page.request.get(f"{base_url}/job/{JOB}/config.xml")
    root = ET.fromstring(config.text())
    trigger = root.find(".//hudson.triggers.SCMTrigger")
    require(trigger is not None and trigger.findtext("spec") == "* * * * *", "Poll SCM schedule is * * * * *")
    print(f"BASELINE={baseline}", flush=True)
    return baseline


def poll_evidence(page, base_url: str, baseline: int, timeout: int) -> None:
    jenkins_login(page, base_url)
    deadline = time.monotonic() + timeout
    number = 0
    while time.monotonic() < deadline:
        response = page.request.get(
            f"{base_url}/job/{JOB}/api/json?tree=builds[number,result,building,actions[causes[shortDescription]]]"
        )
        require(response.ok, "job build history API is readable")
        for build in response.json().get("builds", []):
            causes = [
                str(cause.get("shortDescription", ""))
                for action in build.get("actions", [])
                for cause in action.get("causes", [])
            ]
            if int(build.get("number", 0)) > baseline and any("SCM" in cause for cause in causes):
                if not build.get("building", True) and build.get("result") == "SUCCESS":
                    number = int(build["number"])
                    break
        if number:
            break
        page.wait_for_timeout(1000)
    require(number > baseline, f"SCM-caused build after #{baseline} finished SUCCESS")

    page.goto(f"{base_url}/job/{JOB}/scmPollLog/", wait_until="domcontentloaded")
    body = page.locator("body").inner_text()
    require("Polling Log" in body or "Polling log" in body, "Git Polling Log page is open")
    require("Changes found" in body or "Done. Took" in body, "Git Polling Log contains a polling decision")
    shot(page, "lab4_s09_git_polling_log.png", "Git Polling Log after detecting the new revision")

    page.goto(f"{base_url}/job/{JOB}/{number}/", wait_until="domcontentloaded")
    body = page.locator("body").inner_text()
    require("Started by an SCM change" in body, "build page reports Started by an SCM change")
    shot(page, "lab4_s10_scm_build_history.png", "successful build with Started by an SCM change cause")


def manual_build_evidence(page, base_url: str, timeout: int) -> None:
    jenkins_login(page, base_url)
    response = page.request.get(f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number]")
    last = response.json().get("lastBuild")
    baseline = 0 if last is None else int(last["number"])
    page.goto(f"{base_url}/job/{JOB}/", wait_until="domcontentloaded")
    page.get_by_role("link", name=re.compile(r"Build Now", re.I)).click()
    deadline = time.monotonic() + timeout
    number = baseline
    while time.monotonic() < deadline:
        response = page.request.get(f"{base_url}/job/{JOB}/api/json?tree=lastBuild[number,building,result]")
        build = response.json().get("lastBuild") or {}
        number = int(build.get("number", 0))
        if number > baseline and not build.get("building", True):
            require(build.get("result") == "SUCCESS", f"manual build #{number} finished SUCCESS")
            break
        page.wait_for_timeout(1000)
    require(number > baseline, f"manual build after #{baseline} completed")
    page.goto(f"{base_url}/job/{JOB}/{number}/console", wait_until="domcontentloaded")
    console = page.locator("body").inner_text()
    require("Hello from Gitea" in console, "manual build console contains repository output")
    require("Finished: SUCCESS" in console, "manual build console ends with SUCCESS")
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(300)
    shot(page, "lab4_s07_manual_build_console.png", "manual SCM build console with test output and SUCCESS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--action",
        required=True,
        choices=("install", "register", "repo-create", "repo-form", "repo-files", "job-config", "manual-build", "poll-config", "poll-evidence"),
    )
    parser.add_argument("--gitea-url", default=os.getenv("GITEA_BASE_URL", "http://host.docker.internal:14300"))
    parser.add_argument("--jenkins-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:14080"))
    parser.add_argument("--baseline", type=int, default=0)
    parser.add_argument("--timeout", type=int, default=180)
    args = parser.parse_args()
    ASSETS.mkdir(parents=True, exist_ok=True)
    with browser_page() as (_, _, _, page):
        if args.action == "install":
            install_gitea(page, args.gitea_url.rstrip("/"))
        elif args.action == "register":
            register_student(page, args.gitea_url.rstrip("/"))
        elif args.action == "repo-create":
            create_repo(page, args.gitea_url.rstrip("/"))
        elif args.action == "repo-form":
            create_repo(page, args.gitea_url.rstrip("/"), submit=False)
        elif args.action == "repo-files":
            capture_repo(page, args.gitea_url.rstrip("/"))
        elif args.action == "job-config":
            create_job_and_configure(page, args.jenkins_url.rstrip("/"))
        elif args.action == "manual-build":
            manual_build_evidence(page, args.jenkins_url.rstrip("/"), args.timeout)
        elif args.action == "poll-config":
            configure_poll(page, args.jenkins_url.rstrip("/"))
        else:
            poll_evidence(page, args.jenkins_url.rstrip("/"), args.baseline, args.timeout)


if __name__ == "__main__":
    run_main(main)
