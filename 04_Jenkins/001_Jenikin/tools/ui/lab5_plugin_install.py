#!/usr/bin/env python3
"""Install Generic Webhook Trigger 2.4.2 through Jenkins UI and restart."""

from __future__ import annotations

import argparse
import base64
import json
import os
import time
import urllib.error
import urllib.request

from common import browser_page, jenkins_login, log, require, run_main, wait_visible


PLUGIN_ID = "generic-webhook-trigger"
PLUGIN_VERSION = "2.4.2"


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
    require(plugin_state(base_url) is None, f"{PLUGIN_ID} is absent before the UI experiment")

    with browser_page(headless=not args.headed) as (_, _, _, page):
        jenkins_login(page, base_url)
        page.goto(f"{base_url}/manage/pluginManager/available", wait_until="domcontentloaded")
        search = wait_visible(page.locator("#filter-box"), "Available plugins search", 60_000)
        search.fill("Generic Webhook Trigger")
        row = page.locator("#plugins tbody tr").filter(has_text="Generic Webhook Trigger")
        wait_visible(row, "Generic Webhook Trigger result", 120_000)
        row_text = row.inner_text()
        require(PLUGIN_VERSION in row_text, f"Available list resolves Generic Webhook Trigger {PLUGIN_VERSION}")
        checkbox = row.locator("input[type='checkbox']")
        row.locator("label[for='plugin.generic-webhook-trigger.default']").click()
        require(checkbox.is_checked(), "Generic Webhook Trigger is selected")
        page.locator("#button-install").click()
        log("plugin installation submitted from Available plugins UI")

        deadline = time.monotonic() + args.install_timeout
        while time.monotonic() < deadline:
            if plugin_state(base_url) == (PLUGIN_VERSION, True):
                break
            page.wait_for_timeout(2_000)
        else:
            raise TimeoutError("plugin installation did not finish")

        # Use Jenkins' own restart confirmation page so the restart is also a UI action.
        page.goto(f"{base_url}/restart", wait_until="domcontentloaded")
        confirm = page.get_by_role("button", name="Yes")
        wait_visible(confirm, "Jenkins restart confirmation", 60_000)
        confirm.click()
        log("Jenkins restart confirmed through UI")

    wait_for_restart(base_url, args.restart_timeout)
    wait_for_plugin(base_url, args.restart_timeout)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=os.getenv("JENKINS_BASE_URL", "http://host.docker.internal:15080"))
    parser.add_argument("--install-timeout", type=int, default=600)
    parser.add_argument("--restart-timeout", type=int, default=300)
    parser.add_argument("--headed", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    run_main(lambda: flow(parse_args()))
