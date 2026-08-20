#!/usr/bin/env python3
"""Capture real Docker Hub walkthroughs for LAB 5.

Credentials are read only from HUB_USER, HUB_PASS, and HUB_EMAIL. The script
never writes credentials, tokens, or browser storage to disk. Visible account,
email, and token text is replaced in the DOM before every screenshot.

    python3 tools/ui/hub_capture.py auth
    python3 tools/ui/hub_capture.py push
    HUB_CONFIRM_DELETE=1 python3 tools/ui/hub_capture.py delete
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "tools/ui/raw"
BOXES = RAW / "boxes.json"
VIEWPORT = {"width": 1440, "height": 900}
REPOSITORIES = ("campusops-api", "campusops-web")
TOKEN_DESCRIPTION = "lab5-capture-20260820-083133"

HIDE_CHROME = """
#onetrust-consent-sdk, #onetrust-banner-sdk, .ot-sdk-row,
[class*='CookieBanner'], [id*='cookie-banner'], [data-testid*='cookie'],
[data-testid='gordon-drawer'], [aria-label='Close Gordon drawer'],
[class*='Announcement'], [class*='announcement'], [class*='PromoBanner'],
#docker-announcement-bar, [id^='dkr_global_banner_'] {
  display: none !important;
}
"""


def secrets() -> tuple[str, str, str]:
    missing = [name for name in ("HUB_USER", "HUB_PASS", "HUB_EMAIL") if not os.getenv(name)]
    if missing:
        raise SystemExit("missing environment variable(s): " + ", ".join(missing))
    return os.environ["HUB_USER"], os.environ["HUB_PASS"], os.environ["HUB_EMAIL"]


def mask(page: Page, user: str, email: str) -> None:
    """Replace secrets in rendered text and form values before capture."""
    page.evaluate(
        r"""([user, email, repositories]) => {
          const tokenPrefix = ['dckr', 'pat'].join('_') + '_';
          const tokenPattern = new RegExp(tokenPrefix + '[A-Za-z0-9_-]+', 'g');
          const replace = (value) => value
            .split(email).join('<EMAIL>')
            .split(user).join('<DOCKER_USER>')
            .replace(tokenPattern, '<DOCKER_TOKEN>');
          const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
          const nodes = [];
          while (walker.nextNode()) nodes.push(walker.currentNode);
          for (const node of nodes) node.nodeValue = replace(node.nodeValue || '');
          for (const input of document.querySelectorAll('input, textarea')) {
            if (input.type !== 'password' && input.value) input.value = replace(input.value);
          }
          for (const avatar of document.querySelectorAll("button[aria-label$='account menu']")) {
            avatar.textContent = '';
            avatar.style.background = '#475569';
          }
          for (const link of document.querySelectorAll("a[href*='/repository/docker/']")) {
            const match = (link.getAttribute('href') || '').match(
              /\/repository\/docker\/[^/]+\/([^/?#]+)/
            );
            const repository = match ? match[1] : '';
            if (repository && !repositories.includes(repository)) {
              link.textContent = '<DOCKER_USER>/repository อื่น';
            }
          }
        }""",
        [user, email, list(REPOSITORIES)],
    )


class Session:
    def __init__(self, page: Page, user: str, email: str) -> None:
        self.page = page
        self.user = user
        self.email = email
        self.shots: dict[str, list[dict]] = {}

    def settle(self, wait: int = 1_000) -> None:
        self.page.add_style_tag(content=HIDE_CHROME)
        self.page.wait_for_timeout(wait)

    def box(self, locator: Locator, pad: int = 6) -> list[int]:
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

    def shot(self, name: str, targets: list[tuple[str, Locator]], wait: int = 800) -> None:
        self.settle(wait)
        rows = [{"label": label, "box": self.box(locator)} for label, locator in targets]
        mask(self.page, self.user, self.email)
        self.page.screenshot(path=str(RAW / f"{name}.png"), full_page=False)
        self.shots[name] = rows
        print(f"+ {name}.png " + ", ".join(f"{row['label']}={row['box']}" for row in rows))

    def save(self, phase: str) -> None:
        current = json.loads(BOXES.read_text(encoding="utf-8")) if BOXES.is_file() else {}
        current[f"hub-{phase}"] = self.shots
        BOXES.write_text(json.dumps(current, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"boxes -> {BOXES}")


def sign_in(page: Page, user: str, password: str) -> None:
    page.goto("https://hub.docker.com/login", wait_until="domcontentloaded", timeout=60_000)
    page.locator("input[name='username']:visible").fill(user)
    page.get_by_role("button", name="Continue", exact=True).click()
    page.locator("input[name='password']:visible").fill(password)
    page.get_by_role("button", name="Continue", exact=True).click()
    page.wait_for_url("https://hub.docker.com/**", timeout=60_000)
    page.wait_for_timeout(1_500)


def token_settings_url() -> str:
    return "https://app.docker.com/settings/personal-access-tokens"


def cleanup_token(session: Session, description: str) -> None:
    """Delete exactly the token created by this run."""
    page = session.page
    page.goto(token_settings_url(), wait_until="domcontentloaded", timeout=60_000)
    page.wait_for_timeout(1_500)
    token_text = page.get_by_text(description, exact=True).first
    token_text.wait_for(state="visible", timeout=20_000)
    row = token_text.locator("xpath=ancestor::tr[1]")
    menu = row.locator("button[data-testid^='pat-menu-button']")
    session.shot("hub-auth-12-revoke-menu", [("⑯ เปิดเมนู token", menu)])
    menu.click()
    delete_link = page.locator("a[role='menuitem'][href$='/delete']:visible").first
    session.shot("hub-auth-13-revoke-delete", [("⑰ เลือก Delete", delete_link)])
    delete_link.click()
    page.wait_for_url("**/delete", timeout=20_000)
    delete_button = page.get_by_role("button", name="Delete token", exact=True)
    session.shot("hub-auth-14-revoke-confirm", [("⑱ ยืนยัน Delete token", delete_button)])
    delete_button.click()
    page.wait_for_url("**/personal-access-tokens", timeout=20_000)
    page.wait_for_timeout(1_000)
    if page.get_by_text(description, exact=True).count():
        raise RuntimeError("created token still appears after deletion")
    print("- created walkthrough token deleted")


def phase_auth(session: Session, password: str) -> None:
    page = session.page
    created = False
    try:
        page.goto("https://hub.docker.com", wait_until="domcontentloaded", timeout=60_000)
        logo = page.locator("a[href='/']").filter(has=page.locator("svg")).first
        sign_in_link = page.get_by_role("link", name="Sign in", exact=True)
        session.shot(
            "hub-auth-01-home",
            [("① เปิด hub.docker.com", logo), ("② กด Sign in", sign_in_link)],
            wait=2_000,
        )
        sign_in_link.click()
        page.locator("input[name='username']:visible").wait_for(timeout=30_000)

        username = page.locator("input[name='username']:visible")
        username.fill(session.user)
        continue_button = page.get_by_role("button", name="Continue", exact=True)
        session.shot(
            "hub-auth-02-username",
            [("③ กรอกชื่อบัญชี", username), ("④ กด Continue", continue_button)],
        )
        username.fill(session.user)
        continue_button.click()
        password_input = page.locator("input[name='password']:visible")
        password_input.wait_for(timeout=30_000)
        password_input.fill(password)
        continue_button = page.get_by_role("button", name="Continue", exact=True)
        session.shot(
            "hub-auth-03-password",
            [("⑤ กรอกรหัสผ่าน", password_input), ("⑥ กด Continue", continue_button)],
        )
        continue_button.click()
        page.wait_for_url("https://hub.docker.com/**", timeout=60_000)

        avatar = page.locator("button[aria-label$='account menu']").first
        session.shot("hub-auth-04-avatar", [("⑦ คลิก avatar", avatar)], wait=2_000)
        avatar.click()
        account = page.locator("a[href='https://app.docker.com/settings']:visible").first
        session.shot("hub-auth-05-account-settings", [("⑧ เลือก Account settings", account)])
        # The current Hub opens Account settings in a new tab. Navigate the
        # capture tab to the measured link target so the sequence stays linear.
        page.goto(account.get_attribute("href"), wait_until="domcontentloaded", timeout=60_000)

        page.goto(token_settings_url(), wait_until="domcontentloaded", timeout=60_000)
        personal_tokens = page.locator("a[href$='/personal-access-tokens']:visible").first
        generate_link = page.get_by_role("link", name="Generate new token", exact=True)
        session.shot(
            "hub-auth-06-token-list",
            [
                ("⑨ เปิด Personal access tokens", personal_tokens),
                ("⑩ กด Generate new token", generate_link),
            ],
            wait=2_000,
        )
        generate_link.click()
        page.wait_for_url("**/create", timeout=20_000)

        description = page.locator("input[name='description']")
        description.fill(TOKEN_DESCRIPTION)
        session.shot("hub-auth-07-description", [("⑪ ตั้ง description", description)])

        expiry = page.get_by_role("combobox").nth(0)
        expiry.click()
        expiry_option = page.get_by_role("option", name="30 days", exact=True)
        session.shot("hub-auth-08-expiration", [("⑫ เลือกหมดอายุ 30 วัน", expiry_option)])
        expiry_option.click()

        scope = page.get_by_role("combobox").nth(1)
        scope.click()
        scope_option = page.get_by_role("option", name="Read & Write", exact=True)
        session.shot("hub-auth-09-permission", [("⑬ เลือก Read & Write", scope_option)])
        scope_option.click()

        generate_button = page.get_by_role("button", name="Generate", exact=True)
        session.shot("hub-auth-10-generate", [("⑭ กด Generate", generate_button)])
        generate_button.click()
        created = True
        page.get_by_text("Copy access token", exact=True).wait_for(timeout=30_000)
        copy_token = page.get_by_role("button", name="Copy", exact=True).last
        session.shot("hub-auth-11-copy", [("⑮ คัดลอก token", copy_token)], wait=1_500)
    finally:
        if created:
            cleanup_token(session, TOKEN_DESCRIPTION)
        session.save("auth")


def repository_url(user: str, repository: str, tail: str = "") -> str:
    suffix = f"/{tail}" if tail else ""
    return f"https://hub.docker.com/repository/docker/{user}/{repository}{suffix}"


def phase_push(session: Session) -> None:
    page = session.page
    page.goto(f"https://hub.docker.com/repositories/{session.user}", wait_until="domcontentloaded", timeout=60_000)
    links = [page.locator(f"a[href$='/{repo}']:visible").first for repo in REPOSITORIES]
    session.shot(
        "hub-push-01-repositories",
        [
            (f"{chr(0x2460 + index)} เปิด {repo}", link)
            for index, (repo, link) in enumerate(zip(REPOSITORIES, links))
        ],
        wait=2_000,
    )
    step = 3
    file_index = 2
    for repository in REPOSITORIES:
        page.goto(repository_url(session.user, repository), wait_until="domcontentloaded", timeout=60_000)
        tags_tab = page.locator("a[href$='/tags']:visible").first
        session.shot(
            f"hub-push-{file_index:02d}-{repository}",
            [(f"{chr(0x245f + step)} เปิดแท็บ Tags", tags_tab)],
            wait=1_500,
        )
        file_index += 1
        tags_tab.click()
        page.wait_for_url("**/tags", timeout=20_000)
        tag = page.get_by_role("link", name="1.0", exact=True).first
        digest = page.locator("table a[href*='sha256']:visible").first
        session.shot(
            f"hub-push-{file_index:02d}-{repository}-tags",
            [
                (f"{chr(0x245f + step + 1)} ตรวจ tag 1.0", tag),
                (f"{chr(0x245f + step + 2)} ตรวจ digest", digest),
            ],
            wait=2_000,
        )
        file_index += 1
        step += 3
    session.save("push")


def phase_delete(session: Session) -> None:
    page = session.page
    step = 1
    for index, repository in enumerate(REPOSITORIES, start=1):
        page.goto(
            f"https://hub.docker.com/repositories/{session.user}",
            wait_until="domcontentloaded",
            timeout=60_000,
        )
        my_hub = page.locator("a", has_text="My Hub").first
        repositories = page.locator("a", has_text="Repositories").first
        repository_link = page.locator(f"a[href$='/{repository}']:visible").first
        session.shot(
            f"hub-delete-{index:02d}-01-{repository}-list",
            [
                (f"{chr(0x245f + step)} เปิด My Hub", my_hub),
                (f"{chr(0x245f + step + 1)} เปิด Repositories", repositories),
                (f"{chr(0x245f + step + 2)} เลือก {repository}", repository_link),
            ],
            wait=1_500,
        )
        repository_link.click()
        page.wait_for_url(f"**/{repository}", timeout=20_000)

        settings = page.locator("a[href$='/settings']:visible").first
        session.shot(
            f"hub-delete-{index:02d}-02-{repository}-repository",
            [(f"{chr(0x245f + step + 3)} เปิด Settings", settings)],
            wait=1_500,
        )
        settings.click()
        page.wait_for_url("**/settings", timeout=20_000)

        delete_button = page.get_by_role("button", name="Delete repository", exact=True)
        delete_button.scroll_into_view_if_needed()
        session.shot(
            f"hub-delete-{index:02d}-03-{repository}-settings",
            [(f"{chr(0x245f + step + 4)} กด Delete repository", delete_button)],
            wait=1_500,
        )
        delete_button.click()
        confirm = page.locator("input[type='text']:visible").last
        confirm.fill(repository)
        final_delete = page.get_by_role("button", name="Delete repository forever", exact=True)
        session.shot(
            f"hub-delete-{index:02d}-04-{repository}-confirm",
            [
                (f"{chr(0x245f + step + 5)} พิมพ์ชื่อ repository", confirm),
                (f"{chr(0x245f + step + 6)} ยืนยันลบถาวร", final_delete),
            ],
        )
        if os.getenv("HUB_CONFIRM_DELETE") == "1":
            final_delete.click()
            page.wait_for_timeout(3_000)
        step += 7
    session.save("delete")


PHASES = {"auth": phase_auth, "push": phase_push, "delete": phase_delete}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in PHASES:
        raise SystemExit("usage: hub_capture.py [auth|push|delete]")
    phase = sys.argv[1]
    user, password, email = secrets()
    RAW.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as play:
        browser = play.chromium.launch()
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = context.new_page()
        session = Session(page, user, email)
        if phase == "auth":
            phase_auth(session, password)
        else:
            sign_in(page, user, password)
            PHASES[phase](session)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
