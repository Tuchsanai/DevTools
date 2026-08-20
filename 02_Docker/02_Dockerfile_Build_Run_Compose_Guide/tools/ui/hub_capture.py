#!/usr/bin/env python3
"""เก็บภาพหน้าจอจริงของ Docker Hub สำหรับ LAB 5 พร้อมปิดบังชื่อบัญชี/อีเมล/token ก่อนถ่ายภาพ

ใช้กับบัญชีจริงเท่านั้นตอนผลิตสื่อ — ค่าที่เป็นความลับรับผ่าน environment variable
(HUB_USER / HUB_PASS / HUB_EMAIL) และไม่ถูกเขียนลงไฟล์ใด ๆ

    python3 tools/ui/hub_capture.py auth       # ขั้นตอนสร้าง Access Token
    python3 tools/ui/hub_capture.py push1      # หลัง push tag 1.0 ครั้งแรก
    python3 tools/ui/hub_capture.py push2      # หลัง push ทับ tag 1.0
    python3 tools/ui/hub_capture.py delete     # ขั้นตอนลบ repository ตอนเก็บกวาด
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "tools/ui/raw"
BOXES = ROOT / "tools/ui/raw/boxes.json"
STATE = RAW / ".hub_state.json"
VIEWPORT = {"width": 1440, "height": 900}
REPO = "regdemo"

# ซ่อนแบนเนอร์โฆษณา/คุกกี้ทุกหน้า เพื่อให้ภาพขั้นตอนของแต่ละรอบเหมือนกันเสมอ
HIDE_CHROME = """
#onetrust-consent-sdk, #onetrust-banner-sdk, .ot-sdk-row,
[class*='CookieBanner'], [id*='cookie-banner'],
[data-testid='gordon-drawer'], [aria-label='Close Gordon drawer'],
[class*='Announcement'], [class*='announcement'], [class*='PromoBanner'] { display: none !important; }
"""


def secrets() -> tuple[str, str, str]:
    try:
        return os.environ["HUB_USER"], os.environ["HUB_PASS"], os.environ.get("HUB_EMAIL", "")
    except KeyError as error:
        raise SystemExit(f"missing environment variable: {error}") from error


def mask(page: Page, user: str, email: str) -> None:
    """แทนที่ข้อความลับใน text node ก่อนถ่ายภาพ — ได้ภาพที่สะอาดกว่าการเอากล่องทึบไปปะทับ"""
    page.evaluate(
        """([user, email]) => {
            const pairs = [];
            if (email) pairs.push([email, '<EMAIL>']);
            pairs.push([user, '<DOCKER_USER>']);
            pairs.push([/dckr_pat_[A-Za-z0-9_\\-]+/g, '<DOCKER_TOKEN>']);
            const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
            const nodes = [];
            while (walker.nextNode()) nodes.push(walker.currentNode);
            for (const node of nodes) {
                let value = node.nodeValue;
                for (const [from, to] of pairs) {
                    value = typeof from === 'string' ? value.split(from).join(to) : value.replace(from, to);
                }
                if (value !== node.nodeValue) node.nodeValue = value;
            }
            for (const input of document.querySelectorAll('input,textarea')) {
                for (const [from, to] of pairs) {
                    if (typeof from === 'string' && input.value && input.value.includes(from)) {
                        input.value = input.value.split(from).join(to);
                    }
                }
            }
        }""",
        [user, email],
    )


class Session:
    def __init__(self, page: Page, user: str, email: str) -> None:
        self.page = page
        self.user = user
        self.email = email
        self.shots: dict[str, list[dict]] = {}

    def settle(self, wait: int = 1500) -> None:
        self.page.add_style_tag(content=HIDE_CHROME)
        self.page.wait_for_timeout(wait)
        mask(self.page, self.user, self.email)

    def box(self, locator, pad: int = 6) -> list[int] | None:
        try:
            rect = locator.bounding_box(timeout=6000)
        except Exception:
            rect = None
        if not rect:
            return None
        return [
            max(0, int(rect["x"]) - pad),
            max(0, int(rect["y"]) - pad),
            min(VIEWPORT["width"], int(rect["x"] + rect["width"]) + pad),
            min(VIEWPORT["height"], int(rect["y"] + rect["height"]) + pad),
        ]

    def shot(self, name: str, targets: list[tuple[str, object]], wait: int = 1500) -> None:
        """ถ่ายภาพหนึ่งขั้นตอน แล้วบันทึกกรอบของสิ่งที่ต้องคลิกไว้ให้ annotate_steps.py ใช้ต่อ"""
        self.settle(wait)
        boxes = []
        for label, locator in targets:
            box = self.box(locator) if locator is not None else None
            boxes.append({"label": label, "box": box})
            if box is None:
                print(f"  ! {name}: ไม่พบตำแหน่งของ {label!r}")
        RAW.mkdir(parents=True, exist_ok=True)
        self.page.screenshot(path=str(RAW / f"{name}.png"))
        self.shots[name] = boxes
        print(f"  + {name}.png " + ", ".join(f"{b['label']}={b['box']}" for b in boxes))

    def save(self, phase: str) -> None:
        data = json.loads(BOXES.read_text(encoding="utf-8")) if BOXES.is_file() else {}
        data[phase] = self.shots
        BOXES.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"boxes -> {BOXES}")


def login(page: Page, user: str, password: str) -> None:
    page.goto("https://login.docker.com/u/login/identifier?state=lab5", wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(2000)
    page.fill("input[name='username']", user)
    page.click("button[type='submit']")
    page.wait_for_timeout(3500)
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    page.wait_for_url("https://hub.docker.com/**", timeout=60000)
    page.wait_for_timeout(3000)


def phase_auth(session: Session, password: str) -> None:
    page = session.page
    page.goto("https://login.docker.com/u/login/identifier?state=lab5", wait_until="domcontentloaded", timeout=60000)
    session.shot(
        "hub-token-01-signin",
        [("① กรอกชื่อบัญชี Docker", page.locator("input[name='username']")),
         ("② กด Continue", page.locator("button[type='submit']").first)],
        wait=2500,
    )
    page.fill("input[name='username']", session.user)
    page.click("button[type='submit']")
    page.wait_for_timeout(3500)
    session.shot(
        "hub-token-02-password",
        [("③ กรอกรหัสผ่าน", page.locator("input[name='password']")),
         ("④ กด Continue", page.locator("button[type='submit']").first)],
        wait=1500,
    )
    page.fill("input[name='password']", password)
    page.click("button[type='submit']")
    page.wait_for_url("https://hub.docker.com/**", timeout=60000)
    page.wait_for_timeout(3500)

    avatar = page.locator("button[aria-label$='account menu']").first
    session.shot("hub-token-03-avatar", [("⑤ คลิกรูปโปรไฟล์", avatar)], wait=2500)
    avatar.click()
    page.wait_for_timeout(2000)
    account = page.locator("a:has-text('Account settings'), [role='menuitem']:has-text('Account settings')").first
    session.shot("hub-token-04-menu", [("⑥ เลือก Account settings", account)], wait=1200)

    page.goto("https://app.docker.com/settings/personal-access-tokens", wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(2500)
    generate = page.get_by_role("link", name="Generate new token").first
    session.shot(
        "hub-token-05-list",
        [("⑦ เมนู Personal access tokens", page.locator("a[href$='personal-access-tokens']").first),
         ("⑧ กด Generate new token", generate)],
        wait=1500,
    )
    generate.click()
    page.wait_for_timeout(3500)
    description = page.locator("input[name='description']").first
    description.fill("lab5-docker-hub")
    page.wait_for_timeout(400)
    expiry = page.get_by_role("combobox").nth(0)
    expiry.click()
    page.wait_for_timeout(900)
    page.get_by_role("option", name="30 days").first.click()
    page.wait_for_timeout(900)
    session.shot(
        "hub-token-06-form",
        [("⑨ ตั้งชื่อ token", description),
         ("⑩ ตั้งวันหมดอายุ", expiry)],
        wait=1200,
    )
    scope = page.get_by_role("combobox").nth(1)
    scope.click()
    page.wait_for_timeout(1200)
    session.shot(
        "hub-token-07-scope",
        [("⑪ เลือก Read & Write", page.get_by_role("option", name="Read & Write").first)],
        wait=800,
    )
    page.get_by_role("option", name="Read & Write").first.click()
    page.wait_for_timeout(900)
    submit = page.get_by_role("button", name="Generate").first
    session.shot("hub-token-08-generate", [("⑫ กด Generate", submit)], wait=800)
    submit.click()
    page.wait_for_timeout(5000)
    copy = page.locator("button:has-text('Copy')").last
    session.shot("hub-token-09-copy", [("⑬ คัดลอก token เก็บทันที", copy)], wait=1500)
    session.save("auth")


def repo_url(user: str, tail: str) -> str:
    return f"https://hub.docker.com/repository/docker/{user}/{REPO}/{tail}"


def phase_push1(session: Session) -> None:
    page = session.page
    page.goto(f"https://hub.docker.com/repositories/{session.user}", wait_until="networkidle", timeout=60000)
    link = page.get_by_role("link", name=f"{session.user}/{REPO}").first
    session.shot("hub-repo-01-list", [("① repository ที่ push สร้างให้เอง", link)], wait=3000)
    link.click()
    page.wait_for_timeout(3500)
    tab = page.locator("a[href$='/tags']").last
    session.shot("hub-repo-02-general", [("② เปิดแท็บ Tags", tab)], wait=2000)
    page.goto(repo_url(session.user, "tags"), wait_until="networkidle", timeout=60000)
    tag = page.get_by_role("link", name="1.0", exact=True).first
    digest = page.locator("table a[href*='/sha256'], a[href*='images/sha256']").first
    session.shot("hub-repo-03-tag", [("③ tag 1.0 ที่เพิ่ง push", tag),
                                    ("④ digest ตรงกับผล push", digest)], wait=2500)
    session.save("push1")


def phase_push2(session: Session) -> None:
    page = session.page
    page.goto(repo_url(session.user, "tags"), wait_until="networkidle", timeout=60000)
    digest = page.locator("table a[href*='/sha256'], a[href*='images/sha256']").first
    session.shot("hub-repo-04-overwrite", [("⑤ digest ใหม่แม้ tag ชื่อเดิม", digest)], wait=3000)
    session.save("push2")


def phase_delete(session: Session) -> None:
    page = session.page
    page.goto(repo_url(session.user, "settings"), wait_until="networkidle", timeout=60000)
    delete = page.get_by_role("button", name="Delete repository").first
    delete.scroll_into_view_if_needed()
    page.wait_for_timeout(1200)
    session.shot("hub-del-01-settings", [("① กด Delete repository", delete)], wait=2000)
    delete.click()
    page.wait_for_timeout(2500)
    confirm = page.locator("input[type='text']").last
    confirm.fill(REPO)
    page.wait_for_timeout(800)
    forever = page.get_by_role("button", name="Delete").last
    session.shot(
        "hub-del-02-confirm",
        [("① พิมพ์ชื่อ repository", confirm), ("② กดยืนยันการลบ", forever)],
        wait=1000,
    )
    if os.environ.get("HUB_CONFIRM_DELETE") == "1":
        forever.click()
        page.wait_for_timeout(6000)
        page.goto(f"https://hub.docker.com/repositories/{session.user}", wait_until="networkidle", timeout=60000)
        session.shot("hub-del-03-gone", [("① ไม่มี regdemo ในรายการแล้ว", page.locator("table").first)], wait=3000)
    session.save("delete")


def phase_gone(session: Session) -> None:
    page = session.page
    page.goto(f"https://hub.docker.com/repositories/{session.user}", wait_until="networkidle", timeout=60000)
    session.shot("hub-del-03-gone", [("① ไม่มี regdemo แล้ว", page.locator("table").first)], wait=3000)
    session.save("gone")


PHASES = {"auth": phase_auth, "push1": phase_push1, "push2": phase_push2,
          "delete": phase_delete, "gone": phase_gone}


def main() -> int:
    if len(sys.argv) != 2 or sys.argv[1] not in PHASES:
        raise SystemExit(f"usage: hub_capture.py [{'|'.join(PHASES)}]")
    phase = sys.argv[1]
    user, password, email = secrets()
    RAW.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as play:
        browser = play.chromium.launch()
        state = str(STATE) if STATE.is_file() and phase != "auth" else None
        context = browser.new_context(viewport=VIEWPORT, storage_state=state)
        page = context.new_page()
        session = Session(page, user, email)
        if phase == "auth":
            phase_auth(session, password)
        else:
            if state is None:
                login(page, user, password)
            PHASES[phase](session)
        context.storage_state(path=str(STATE))
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
