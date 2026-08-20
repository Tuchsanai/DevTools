#!/usr/bin/env python3
"""ถ่าย walkthrough หน้าเว็บ CampusOps สำหรับ LAB 3 จากข้อมูล seed ชุดคงที่."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright


PROJECT = Path(__file__).resolve().parents[2]
RAW = PROJECT / "tools/ui/raw"
LAB_DIR = "/root/labwork/DevTools/02_Docker/03_Fullstack_App_Example/003_LAB_Build_The_Web"
OUTER_CONTAINER = "devtools-fs-lab3"
BASE_URL = os.environ.get("CAMPUSOPS_URL", "http://localhost:8253")

TITLE = "กล้องถ่ายวิดีโอเปิดไม่ติด"
DETAIL = "กดปุ่มเปิดแล้วไฟสถานะไม่ทำงาน"
ASSIGNEE = "TECH-04"


def reset_seed() -> None:
    command = (
        f"cd {LAB_DIR} && "
        "docker exec ops-db psql -U opsuser -d campusops -v ON_ERROR_STOP=1 "
        "-c 'TRUNCATE stock_moves, loans, tickets, parts, assets RESTART IDENTITY CASCADE' && "
        "docker exec -i ops-db psql -U opsuser -d campusops -v ON_ERROR_STOP=1 "
        "< db/initdb/02-seed.sql"
    )
    subprocess.run(
        ["docker", "exec", OUTER_CONTAINER, "bash", "-lc", command],
        check=True,
        stdout=subprocess.DEVNULL,
    )


def box(locator: Locator) -> list[int]:
    bounds = locator.bounding_box()
    if bounds is None:
        raise RuntimeError(f"ไม่พบ bounding box ของ {locator}")
    return [
        round(bounds["x"]),
        round(bounds["y"]),
        round(bounds["x"] + bounds["width"]),
        round(bounds["y"] + bounds["height"]),
    ]


def capture(page: Page, name: str, targets: dict[str, Locator], boxes: dict[str, object]) -> None:
    page.screenshot(path=RAW / name)
    boxes[name] = {label: box(locator) for label, locator in targets.items()}


def align_column(page: Page, header: Locator) -> None:
    """เลื่อนหัวคอลัมน์มาไว้ใกล้ขอบบน โดยยังเห็นการ์ดล่างในเฟรมเดียวกัน."""
    bounds = header.bounding_box()
    if bounds is None:
        raise RuntimeError("ไม่พบหัวคอลัมน์")
    page.evaluate("delta => window.scrollBy(0, delta)", bounds["y"] - 24)


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    reset_seed()
    boxes: dict[str, object] = {}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900}, device_scale_factor=1)

        page.goto(BASE_URL, wait_until="networkidle")
        overview_link = page.get_by_role("link", name="สรุปภาพรวม ตัวเลขวันนี้")
        capture(page, "ui-web-01-overview.png", {"overview": overview_link}, boxes)

        tickets_link = page.get_by_role("link", name="กระดานงานซ่อม งานอยู่ในมือใคร")
        tickets_link.click()
        page.wait_for_load_state("networkidle")
        tickets_link = page.get_by_role("link", name="กระดานงานซ่อม งานอยู่ในมือใคร")
        capture(page, "ui-web-02-tickets.png", {"tickets": tickets_link}, boxes)

        asset = page.locator("#asset_id")
        asset.select_option("3")
        capture(page, "ui-web-03-asset.png", {"asset": asset}, boxes)

        title = page.locator("#title")
        detail = page.locator("#detail")
        title.fill(TITLE)
        detail.fill(DETAIL)
        capture(
            page,
            "ui-web-04-details.png",
            {"title": title, "detail": detail},
            boxes,
        )

        priority = page.locator("#priority")
        priority.select_option("HIGH")
        capture(page, "ui-web-05-priority.png", {"priority": priority}, boxes)

        submit = page.get_by_role("button", name="แจ้งซ่อม")
        capture(page, "ui-web-06-submit.png", {"submit": submit}, boxes)
        with page.expect_navigation(wait_until="networkidle"):
            submit.click()

        # การ์ดใบที่ 4 กับหัวคอลัมน์สูงเกินหนึ่ง viewport ที่ 100% จึงใช้ browser zoom 65%
        # เพื่อเก็บหลักฐานทั้งเลขจำนวนและการ์ดใหม่ในภาพ 1440x900 ใบเดียว
        page.evaluate("document.body.style.zoom = '0.65'")

        new_card = page.locator("article").filter(has_text=TITLE)
        new_column = page.locator("section").filter(has=page.get_by_role("heading", name="รอรับเรื่อง"))
        align_column(page, new_column.locator("header"))
        capture(
            page,
            "ui-web-07-new-card.png",
            {"new_header": new_column.locator("header"), "new_card": new_card},
            boxes,
        )

        assignee = new_card.get_by_label("ชื่อช่างสำหรับใบ #9")
        assignee.fill(ASSIGNEE)
        capture(page, "ui-web-08-assignee.png", {"assignee": assignee}, boxes)

        assign = new_card.get_by_role("button", name="มอบหมาย")
        capture(page, "ui-web-09-assign.png", {"assign": assign}, boxes)
        with page.expect_navigation(wait_until="networkidle"):
            assign.click()

        page.evaluate("document.body.style.zoom = '0.65'")

        assigned_column = page.locator("section").filter(
            has=page.get_by_role("heading", name="มอบหมายแล้ว")
        )
        assigned_card = assigned_column.locator("article").filter(has_text=TITLE)
        assigned_card.wait_for(state="visible")
        align_column(page, assigned_column.locator("header"))
        capture(
            page,
            "ui-web-10-assigned.png",
            {"assigned_header": assigned_column.locator("header"), "assigned_card": assigned_card},
            boxes,
        )

        browser.close()

    print(json.dumps(boxes, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
