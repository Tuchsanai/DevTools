#!/usr/bin/env python3
"""Capture the public DevTools repository walkthrough for LAB 1.

The script uses the live GitHub UI at 1440x900, hides cookie/marketing chrome,
masks account names, and records measured element bounding boxes in
tools/ui/raw/boxes.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "tools/ui/raw"
BOXES = RAW / "boxes.json"
VIEWPORT = {"width": 1440, "height": 900}
GITHUB_OWNER = "Tuchsanai"
GITHUB_REPOSITORY = "DevTools"
REPOSITORY = f"https://github.com/{GITHUB_OWNER}/{GITHUB_REPOSITORY}"

HIDE_CHROME = """
#onetrust-consent-sdk, #onetrust-banner-sdk, .js-cookie-consent-banner,
[class*='CookieBanner'], [id*='cookie-banner'], [data-testid*='cookie'],
.js-notice, .flash-banner, [class*='marketing-banner'] {
  display: none !important;
}
img.avatar, img.Avatar {
  visibility: hidden !important;
}
"""

MASK_ACCOUNTS = """
() => {
  const replacements = [
    [/Tuchsanai/gi, '<DOCKER_USER>'],
    [/Claude/gi, '<DOCKER_USER>']
  ];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const nodes = [];
  while (walker.nextNode()) nodes.push(walker.currentNode);
  for (const node of nodes) {
    let value = node.nodeValue;
    for (const [pattern, replacement] of replacements) {
      value = value.replace(pattern, replacement);
    }
    node.nodeValue = value;
  }
}
"""


def measured_box(locator: Locator, pad: int = 6) -> list[int]:
    locator.wait_for(state="visible", timeout=20_000)
    rect = locator.bounding_box(timeout=10_000)
    if not rect:
        raise RuntimeError(f"element has no bounding box: {locator}")
    return [
        max(0, int(rect["x"]) - pad),
        max(0, int(rect["y"]) - pad),
        min(VIEWPORT["width"], int(rect["x"] + rect["width"]) + pad),
        min(VIEWPORT["height"], int(rect["y"] + rect["height"]) + pad),
    ]


def settle(page: Page, wait: int = 1_000) -> None:
    page.add_style_tag(content=HIDE_CHROME)
    page.wait_for_timeout(wait)
    page.evaluate(MASK_ACCOUNTS)


def shot(page: Page, name: str, targets: list[tuple[str, Locator]]) -> list[dict]:
    settle(page)
    rows = [{"label": label, "box": measured_box(locator)} for label, locator in targets]
    page.screenshot(path=str(RAW / f"{name}.png"), full_page=False)
    print(f"+ {name}.png " + ", ".join(f"{row['label']}={row['box']}" for row in rows))
    return rows


def save_boxes(captures: dict[str, list[dict]], clicks: list[dict]) -> None:
    current = json.loads(BOXES.read_text(encoding="utf-8")) if BOXES.is_file() else {}
    current["github"] = captures
    current["github-clicks"] = clicks
    BOXES.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"boxes -> {BOXES}")


def first_visible(page: Page, selectors: list[str]) -> Locator:
    for selector in selectors:
        locator = page.locator(selector).first
        try:
            if locator.is_visible(timeout=2_000):
                return locator
        except Exception:
            pass
    raise RuntimeError(f"no visible locator matched: {selectors}")


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    captures: dict[str, list[dict]] = {}
    clicks: list[dict] = []

    with sync_playwright() as play:
        browser = play.chromium.launch()
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = context.new_page()

        page.goto(REPOSITORY, wait_until="domcontentloaded", timeout=60_000)
        settle(page, 2_000)
        repo_name = first_visible(
            page,
            [
                "strong[itemprop='name'] a",
                "[data-testid='breadcrumbs-filename']",
                "main h1 strong a",
            ],
        )
        docker_folder = page.locator(
            f"a[href*='/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/tree/']"
            "[href$='/02_Docker']:visible"
        ).first
        captures["gh-01-repo"] = shot(
            page, "gh-01-repo", [("① เปิดหน้า repository", repo_name)]
        )
        captures["gh-02-folder"] = shot(
            page,
            "gh-02-folder",
            [("② คลิกโฟลเดอร์ 02_Docker", docker_folder)],
        )
        clicks.append({"action": "click 02_Docker", "box": measured_box(docker_folder)})
        docker_folder.click()
        page.wait_for_url("**/02_Docker", timeout=30_000)
        settle(page, 1_500)

        project_folder = page.locator(
            f"a[href*='/{GITHUB_OWNER}/{GITHUB_REPOSITORY}/tree/']"
            "[href$='/02_Docker/03_Fullstack_App_Example']:visible"
        ).first
        clicks.append(
            {"action": "click 03_Fullstack_App_Example", "box": measured_box(project_folder)}
        )
        captures["gh-03-project"] = shot(
            page,
            "gh-03-project",
            [("③ คลิก 03_Fullstack_App_Example", project_folder)],
        )
        project_folder.click()
        page.wait_for_url("**/02_Docker/03_Fullstack_App_Example", timeout=30_000)
        settle(page, 1_500)

        for lab in range(1, 6):
            page.locator(f"a[title^='00{lab}_LAB_']:visible").first.wait_for(
                state="visible", timeout=15_000
            )
        # GitHub's current public folder view uses the new Files layout and no
        # longer displays the green repository-level Code button. Return to the
        # repository root to capture the real clone menu.
        page.goto(REPOSITORY, wait_until="domcontentloaded", timeout=60_000)
        settle(page, 1_500)
        code_button = first_visible(
            page,
            [
                "button:has-text('Code')",
                "summary:has-text('Code')",
                "[data-testid='code-button']",
            ],
        )
        clicks.append({"action": "click Code", "box": measured_box(code_button)})
        code_button.click()
        page.wait_for_timeout(800)

        https_tab = first_visible(
            page,
            [
                "button:has-text('HTTPS')",
                "[role='tab']:has-text('HTTPS')",
                "a:has-text('HTTPS')",
            ],
        )
        clicks.append({"action": "click HTTPS", "box": measured_box(https_tab)})
        https_tab.click()
        page.wait_for_timeout(500)
        copy_button = first_visible(
            page,
            [
                "button[aria-label*='Copy']",
                "button:has(svg.octicon-copy)",
                "button[data-copy-feedback]",
                "clipboard-copy button",
                "clipboard-copy",
            ],
        )
        clicks.append({"action": "click copy URL", "box": measured_box(copy_button)})
        captures["gh-04-code"] = shot(
            page,
            "gh-04-code",
            [
                ("④ กดปุ่ม Code", code_button),
                ("⑤ เลือกแท็บ HTTPS", https_tab),
                ("⑥ คัดลอก URL", copy_button),
            ],
        )

        save_boxes(captures, clicks)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
