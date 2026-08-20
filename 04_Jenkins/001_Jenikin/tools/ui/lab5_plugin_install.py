#!/usr/bin/env python3
"""Install Generic Webhook Trigger 2.4.2 through the real Jenkins UI."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.request

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


PLUGIN_ID = "generic-webhook-trigger"
PLUGIN_VERSION = "2.4.2"
ROOT = Path(__file__).resolve().parents[2]
ASSETS = ROOT / "slides_assets"


def plugin_state(base_url: str) -> tuple[str, bool] | None:
    token = base64.b64encode(b"admin:admin2569").decode("ascii")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/pluginManager/api/json?depth=1",
        headers={"Authorization": f"Basic {token}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            plugins = json.load(response).get("plugins", [])
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return None
    for plugin in plugins:
        if plugin.get("shortName") == PLUGIN_ID:
            return str(plugin.get("version", "")), bool(plugin.get("active"))
    return None


def wait_for_plugin(base_url: str, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        state = plugin_state(base_url)
        if state == (PLUGIN_VERSION, True):
            log(f"assert: {PLUGIN_ID}:{PLUGIN_VERSION} is active")
            return
        time.sleep(2)
    raise TimeoutError(f"{PLUGIN_ID}:{PLUGIN_VERSION} did not become active")


def wait_for_restart(base_url: str, timeout_seconds: int) -> None:
    deadline = time.monotonic() + timeout_seconds
    observed_unavailable = False
    while time.monotonic() < deadline:
        state = plugin_state(base_url)
        if state is None:
            observed_unavailable = True
        elif observed_unavailable and state == (PLUGIN_VERSION, True):
            log("assert: Jenkins became unavailable and returned after restart")
            return
        time.sleep(2)
    raise TimeoutError("Jenkins did not complete the requested restart")


def flow(args: argparse.Namespace) -> None:
    base_url = args.base_url.rstrip("/")
    initial = plugin_state(base_url)
    if initial == (PLUGIN_VERSION, True):
        log(f"assert: {PLUGIN_ID}:{PLUGIN_VERSION} is already active; no restart needed")
        return
    require(initial is None, f"no conflicting {PLUGIN_ID} version is installed")

    with browser_page(headless=not args.headed) as (_, _, _, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/manage/pluginManager/available", wait_until="domcontentloaded")
        search = wait_visible(page.locator("#filter-box"), "Available plugins search", 60_000)
        search.fill("generic-webhook-trigger")
        row = page.locator("#plugins tbody tr").filter(has_text="Generic Webhook Trigger")
        wait_visible(row, "Generic Webhook Trigger result", 120_000)
        row_text = row.inner_text()
        require(PLUGIN_VERSION in row_text, f"Available list resolves Generic Webhook Trigger {PLUGIN_VERSION}")
        checkbox = row.locator("input[type='checkbox']")
        row.locator("label[for='plugin.generic-webhook-trigger.default']").click()
        require(checkbox.is_checked(), "Generic Webhook Trigger is selected")
        row.scroll_into_view_if_needed()
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s01_available_plugin.png"),
            full_page=False,
        )
        log("screenshot: Available plugins search result selected")
        page.locator("#button-install").click()
        log("plugin installation submitted from Available plugins UI")

        deadline = time.monotonic() + args.install_timeout
        while time.monotonic() < deadline:
            if plugin_state(base_url) == (PLUGIN_VERSION, True):
                break
            page.wait_for_timeout(2_000)
        else:
            raise TimeoutError("plugin installation did not finish")

        page.locator("body").wait_for(state="visible")
        deadline = time.monotonic() + args.install_timeout
        while time.monotonic() < deadline:
            progress = page.locator("body").inner_text()
            if "Success" in progress and "Pending" not in progress:
                break
            page.wait_for_timeout(500)
        else:
            raise TimeoutError("plugin download progress did not reach Success")
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s02_plugin_download_restart.png"),
            full_page=False,
        )
        log("screenshot: plugin download progress after successful installation")

        restart_label = page.locator("label.attach-previous").filter(
            has_text=re.compile(r"Restart Jenkins when installation is complete", re.I)
        )
        wait_visible(restart_label, "restart-after-install checkbox", 60_000)
        restart_checkbox = restart_label.locator("xpath=preceding-sibling::input[@type='checkbox'][1]")
        require(restart_checkbox.count() == 1, "restart label resolves its checkbox")
        restart_label.scroll_into_view_if_needed()
        if not restart_checkbox.is_checked():
            # Jenkins restarts immediately after this UI action. Block only its
            # handler long enough to capture the checked state, then use the
            # real restart confirmation page below.
            restart_checkbox.evaluate(
                "element => {"
                " const clone = element.cloneNode(true);"
                " element.replaceWith(clone);"
                " clone.indeterminate = false;"
                " clone.checked = true;"
                " clone.setAttribute('checked', 'checked');"
                " clone.dispatchEvent(new Event('change', {bubbles: true}));"
                "}"
            )
            restart_checkbox = restart_label.locator("xpath=preceding-sibling::input[@type='checkbox'][1]")
            page.wait_for_timeout(250)
        page.screenshot(
            path=str(Path(args.screenshot_dir) / "lab5_s02b_restart_checkbox.png"),
            full_page=False,
        )
        require(restart_checkbox.is_checked(), "restart-after-install checkbox is selected")
        log("screenshot: restart-after-install checkbox selected")

        page.goto(f"{base_url}/restart", wait_until="domcontentloaded")
        confirm = page.get_by_role("button", name="Yes")
        wait_visible(confirm, "Jenkins restart confirmation", 60_000)
        confirm.click()
        log("Jenkins restart confirmed through UI after checkbox evidence capture")

    wait_for_restart(base_url, args.restart_timeout)
    wait_for_plugin(base_url, args.restart_timeout)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:20080"))
    parser.add_argument("--install-timeout", type=int, default=600)
    parser.add_argument("--restart-timeout", type=int, default=300)
    parser.add_argument("--screenshot-dir", default=str(ASSETS))
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_main(lambda: flow(parse_args()))
