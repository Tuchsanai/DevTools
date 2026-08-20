#!/usr/bin/env python3
"""Walk the real Jenkins setup wizard and freeze its resolved plugin set."""

from __future__ import annotations

import argparse
import os
import subprocess
import time
from pathlib import Path

from common import browser_page, log, require, run_main, screenshot, wait_visible


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PLUGINS = ROOT / "tools" / "bootstrap" / "plugins.txt"


def initial_password(devtools_name: str, jenkins_name: str) -> str:
    command = [
        "docker",
        "exec",
        devtools_name,
        "docker",
        "exec",
        jenkins_name,
        "cat",
        "/var/jenkins_home/secrets/initialAdminPassword",
    ]
    password = subprocess.check_output(command, text=True).strip()
    require(bool(password), "initialAdminPassword was read from the Jenkins container")
    return password


def click_install_suggested(page) -> None:
    button = page.get_by_text("Install suggested plugins", exact=False)
    wait_visible(button, "Install suggested plugins", timeout_ms=60_000)
    button.click()
    log("suggested plugin installation started")


def wait_for_setup_state(page, timeout_seconds: int = 180) -> str:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if page.locator("#jenkins-head-icon").is_visible():
            return "dashboard"
        admin_frame = page.frame(name="setup-first-user")
        if admin_frame and admin_frame.locator("input[name='username']").is_visible():
            return "admin"
        config_frame = page.frame(name="setup-configure-instance")
        if config_frame and config_frame.locator("input[name='rootUrl']").is_visible():
            return "configure"
        if page.get_by_role("button", name="Start using Jenkins").is_visible():
            return "ready"
        if page.get_by_text("Install suggested plugins", exact=False).is_visible():
            return "plugins"
        page.wait_for_timeout(2_000)
    raise TimeoutError("Jenkins setup did not reach plugins, admin, or dashboard state")


def wait_for_admin_form(page, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    last_progress = ""
    while time.monotonic() < deadline:
        admin_frame = page.frame(name="setup-first-user")
        if admin_frame and admin_frame.locator("input[name='username']").is_visible():
            log("suggested plugin installation completed")
            return
        progress_bar = page.locator(".progress-bar")
        progress = progress_bar.get_attribute("style", timeout=1_000) if progress_bar.count() else ""
        status_locator = page.locator(".install-text")
        status = status_locator.all_inner_texts() if status_locator.count() else []
        summary = f"{progress} {' | '.join(status[-3:])}"
        if summary != last_progress:
            log(f"plugin progress: {summary.strip() or 'waiting'}")
            last_progress = summary
        page.wait_for_timeout(5_000)
    raise TimeoutError(f"plugin installation did not finish within {timeout_seconds}s")


def create_admin(page) -> None:
    frame = page.frame(name="setup-first-user")
    require(frame is not None, "Create First Admin User iframe is present")
    fields = {
        "username": "admin",
        "password1": "admin2569",
        "password2": "admin2569",
        "fullname": "Admin",
        "email": "student@example.com",
    }
    for name, value in fields.items():
        locator = frame.locator(f"input[name='{name}']")
        if locator.count():
            locator.fill(value)
    page.get_by_role("button", name="Save and Continue").click()
    log("created Jenkins admin/admin2569")


def finish_instance_configuration(page, canonical_url: str) -> None:
    config_frame = page.frame(name="setup-configure-instance")
    if not config_frame:
        page.wait_for_timeout(2_000)
        config_frame = page.frame(name="setup-configure-instance")
    if config_frame:
        url_field = config_frame.locator("input[name='rootUrl']")
        wait_visible(url_field, "canonical Jenkins URL field", timeout_ms=60_000)
        url_field.fill(canonical_url)
        page.get_by_role("button", name="Save and Finish").click()
        log(f"saved canonical Jenkins URL {canonical_url}")
    ready = page.get_by_role("button", name="Start using Jenkins")
    wait_visible(ready, "Start using Jenkins", timeout_ms=120_000)
    ready.click()
    wait_visible(page.locator("#jenkins-head-icon"), "Jenkins dashboard", timeout_ms=120_000)


def freeze_plugins(page, base_url: str, output: Path) -> list[str]:
    response = page.request.get(f"{base_url.rstrip('/')}/pluginManager/api/json?depth=1")
    require(response.ok, f"pluginManager API returned HTTP {response.status}")
    payload = response.json()
    resolved = sorted(
        f"{item['shortName']}:{item['version']}"
        for item in payload.get("plugins", [])
        if item.get("shortName") and item.get("version") and item.get("active", True)
    )
    require(bool(resolved), "pluginManager API returned at least one active plugin")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(resolved) + "\n", encoding="utf-8")
    log(f"froze {len(resolved)} plugins -> {output}")
    return resolved


def flow(args: argparse.Namespace) -> None:
    shot_dir = Path(args.screenshot_dir)
    with browser_page(headless=not args.headed) as (_, _, _, page):
        page.goto(f"{args.base_url.rstrip('/')}/login", wait_until="domcontentloaded", timeout=60_000)
        regular_user = page.locator("input[name='j_username']")
        if regular_user.is_visible():
            log("resuming wizard through the configured admin account")
            regular_user.fill("admin")
            page.locator("input[name='j_password']").fill("admin2569")
            page.get_by_role("button", name="Sign in").click()
        else:
            password = initial_password(args.devtools_name, args.jenkins_name)
            unlock = wait_visible(page.locator("input[name='j_password']"), "Unlock Jenkins password field", 60_000)
            screenshot(page, shot_dir / "lab1_unlock.png", "Jenkins unlock page")
            unlock.fill(password)
            page.get_by_role("button", name="Continue").click()
        setup_state = wait_for_setup_state(page)
        log(f"wizard state: {setup_state}")
        if setup_state == "admin":
            log("resuming wizard at Create First Admin User")
            create_admin(page)
            finish_instance_configuration(page, args.canonical_url)
        elif setup_state == "dashboard":
            log("wizard is already complete; continuing at dashboard")
        elif setup_state == "configure":
            log("resuming wizard at Instance Configuration")
            finish_instance_configuration(page, args.canonical_url)
        elif setup_state == "ready":
            page.get_by_role("button", name="Start using Jenkins").click()
            wait_visible(page.locator("#jenkins-head-icon"), "Jenkins dashboard", timeout_ms=120_000)
        else:
            click_install_suggested(page)
            screenshot(page, shot_dir / "lab1_plugins.png", "suggested plugins installing")
            wait_for_admin_form(page, args.plugin_timeout)
            create_admin(page)
            finish_instance_configuration(page, args.canonical_url)
        screenshot(page, shot_dir / "lab1_dashboard.png", "Jenkins dashboard")
        plugins = freeze_plugins(page, args.base_url, args.plugins_output)
        require(any(item.startswith("workflow-aggregator:") for item in plugins), "suggested plugins include Pipeline")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:10080"))
    parser.add_argument("--canonical-url", default="http://localhost:8080/")
    parser.add_argument("--devtools-name", default=os.getenv("DT_NAME", "devtools-jk0"))
    parser.add_argument("--jenkins-name", default="jenkins")
    parser.add_argument("--plugins-output", type=Path, default=DEFAULT_PLUGINS)
    parser.add_argument("--screenshot-dir", default="/tmp/u0-lab1-wizard")
    parser.add_argument("--plugin-timeout", type=int, default=1800)
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    run_main(lambda: flow(arguments))
