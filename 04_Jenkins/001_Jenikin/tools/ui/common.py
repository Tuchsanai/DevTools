#!/usr/bin/env python3
"""Small Playwright helpers shared by the Jenkins/Gitea teaching flows."""

from __future__ import annotations

import contextlib
import os
import sys
import time
from pathlib import Path
from typing import Iterator

from playwright.sync_api import Browser, BrowserContext, Locator, Page, Playwright, sync_playwright


DEFAULT_TIMEOUT_MS = int(os.getenv("UI_TIMEOUT_MS", "30000"))


def log(message: str) -> None:
    print(f"[ui][{time.strftime('%H:%M:%S')}] {message}", flush=True)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    log(f"assert: {message}")


def wait_visible(locator: Locator, description: str, timeout_ms: int = DEFAULT_TIMEOUT_MS) -> Locator:
    log(f"wait: {description}")
    locator.wait_for(state="visible", timeout=timeout_ms)
    return locator


def screenshot(page: Page, target: str | Path, description: str) -> None:
    path = Path(target)
    path.parent.mkdir(parents=True, exist_ok=True)
    page.screenshot(path=str(path), full_page=True)
    log(f"screenshot: {description} -> {path}")


@contextlib.contextmanager
def browser_page(*, headless: bool = True) -> Iterator[tuple[Playwright, Browser, BrowserContext, Page]]:
    """Open Chromium with stable lab defaults and always close it."""

    playwright = sync_playwright().start()
    # Chromium otherwise blocks PLAN §7's shifted 10080 port as an unsafe port.
    browser = playwright.chromium.launch(
        headless=headless,
        args=["--explicitly-allowed-ports=10080,10300,10800"],
    )
    context = browser.new_context(ignore_https_errors=True, viewport={"width": 1440, "height": 1000})
    context.set_default_timeout(DEFAULT_TIMEOUT_MS)
    page = context.new_page()
    try:
        yield playwright, browser, context, page
    finally:
        context.close()
        browser.close()
        playwright.stop()


def jenkins_login(page: Page, base_url: str, username: str = "admin", password: str = "admin2569") -> None:
    page.goto(f"{base_url.rstrip('/')}/login", wait_until="domcontentloaded")
    user = page.locator("input[name='j_username']")
    if user.is_visible():
        user.fill(username)
        page.locator("input[name='j_password']").fill(password)
        page.get_by_role("button", name="Sign in").click()
    wait_visible(page.locator("#jenkins-head-icon"), "Jenkins authenticated header")
    require("login" not in page.url.lower(), "Jenkins login reached an authenticated page")


def gitea_login(page: Page, base_url: str, username: str = "student", password: str = "student2569") -> None:
    page.goto(f"{base_url.rstrip('/')}/user/login", wait_until="domcontentloaded")
    user = page.locator("input[name='user_name']")
    if user.is_visible():
        user.fill(username)
        page.locator("input[name='password']").fill(password)
        page.get_by_role("button", name="Sign In").click()
    wait_visible(page.locator("body"), "Gitea page after login")
    require("/user/login" not in page.url, "Gitea login reached an authenticated page")


def run_main(function) -> None:
    """Turn every UI failure into a clear non-zero process exit."""

    try:
        function()
    except Exception as exc:  # assertions and Playwright errors both belong in the log
        print(f"[ui][FAIL] {type(exc).__name__}: {exc}", file=sys.stderr, flush=True)
        raise SystemExit(1) from exc
    log("PASS")
