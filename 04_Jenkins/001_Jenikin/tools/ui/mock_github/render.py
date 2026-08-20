#!/usr/bin/env python3
"""Render deterministic GitHub UI mocks with Playwright Chromium."""

from pathlib import Path

from playwright.sync_api import Page, sync_playwright


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[2]
OUTPUT_DIR = PROJECT_ROOT / "slides_assets" / "mock"
VIEWPORT = {"width": 1600, "height": 1100}

PAGES = (
    ("new_repo_hello.html", "github_new_repo_hello.png", "repo", "hello-ci"),
    ("new_repo_webapp.html", "github_new_repo_webapp.png", "repo", "webapp"),
    (
        "add_webhook_hello.html",
        "github_add_webhook_hello.png",
        "webhook",
        "<SMEE_HELLO_URL>",
    ),
    (
        "add_webhook_webapp.html",
        "github_add_webhook_webapp.png",
        "webhook",
        "<SMEE_WEBAPP_URL>",
    ),
)


def checked(page: Page, selector: str, expected: bool = True) -> None:
    actual = page.locator(selector).is_checked()
    if actual is not expected:
        raise AssertionError(f"{selector}: checked={actual}, expected={expected}")


def value(page: Page, selector: str, expected: str) -> None:
    actual = page.locator(selector).input_value()
    if actual != expected:
        raise AssertionError(f"{selector}: value={actual!r}, expected={expected!r}")


def text_value(page: Page, selector: str, expected: str) -> None:
    actual = page.locator(selector).inner_text().strip()
    if actual != expected:
        raise AssertionError(f"{selector}: text={actual!r}, expected={expected!r}")


def verify_contract(page: Page, kind: str, expected: str) -> None:
    text_value(page, "[data-contract='mock-badge']", "ภาพจำลอง UI")

    if kind == "repo":
        value(page, "#owner", "<GITHUB_USER>")
        value(page, "#repo-name", expected)
        checked(page, "#visibility-public")
        checked(page, "#visibility-private", False)
        checked(page, "#add-readme", False)
        text_value(page, "#create-repository", "Create repository")
        return

    value(page, "#payload-url", expected)
    value(page, "#content-type", "application/json")
    value(page, "#secret", "")
    checked(page, "#ssl-enable")
    checked(page, "#ssl-disable", False)
    checked(page, "#event-push")
    checked(page, "#event-all", False)
    checked(page, "#event-select", False)
    checked(page, "#active")
    text_value(page, "#add-webhook", "Add webhook")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        for html_name, png_name, kind, expected in PAGES:
            source = HERE / html_name
            output = OUTPUT_DIR / png_name
            page.goto(source.as_uri(), wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            verify_contract(page, kind, expected)
            page.screenshot(path=str(output), full_page=True)
            print(f"rendered {output.relative_to(PROJECT_ROOT)}")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
