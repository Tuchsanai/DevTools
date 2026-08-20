#!/usr/bin/env python3
"""Reset LAB 4 to its seed and capture the four-step network walkthrough."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from playwright.sync_api import Locator, Page, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "tools/ui/raw"
BOXES = RAW / "lab4-boxes.json"
VIEWPORT = {"width": 1440, "height": 900}
# Codex itself runs in a development container; this hostname reaches the
# Docker host where port 8254 is published.  Learners use localhost:8254.
BASE_URL = "http://host.docker.internal:8254"
LAB_CONTAINER = "devtools-fs-lab4"
LAB_DIR = "/root/labwork/DevTools/02_Docker/03_Fullstack_App_Example/004_LAB_Connect_Them"


def outer(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=check, text=True, capture_output=True)


def inner(script: str) -> str:
    result = outer("docker", "exec", LAB_CONTAINER, "bash", "-lc", script)
    return result.stdout.strip()


def reset_seed() -> None:
    """Replace the LAB database volume so initdb loads the fixed seed again."""
    inner(
        "docker rm -f ops-web ops-api ops-db ops-tools >/dev/null 2>&1 || true; "
        "docker volume rm ops-pgdata >/dev/null 2>&1 || true; "
        "docker network inspect ops-net >/dev/null 2>&1 || docker network create ops-net >/dev/null; "
        f"cd {LAB_DIR}; "
        "docker run -d --name ops-db --network ops-net "
        "-e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass "
        "-v ops-pgdata:/var/lib/postgresql/data "
        "-v \"$PWD/db/initdb:/docker-entrypoint-initdb.d:ro\" postgres:17-alpine >/dev/null"
    )
    for _ in range(90):
        initialized = outer(
            "docker",
            "exec",
            LAB_CONTAINER,
            "bash",
            "-lc",
            "docker logs ops-db 2>&1 | grep -q 'init process complete'",
            check=False,
        )
        ready = outer(
            "docker",
            "exec",
            LAB_CONTAINER,
            "docker",
            "exec",
            "ops-db",
            "pg_isready",
            "-U",
            "opsuser",
            "-d",
            "campusops",
            check=False,
        )
        if initialized.returncode == 0 and ready.returncode == 0:
            break
        time.sleep(1)
    else:
        raise RuntimeError("ops-db did not become ready after seed reset")

    inner(
        "docker run -d --name ops-api --network ops-net "
        "-e DATABASE_URL=postgresql://opsuser:labpass@ops-db:5432/campusops "
        "campusops-api:lab4 >/dev/null; "
        "docker run -d --name ops-web --network ops-net -p 3000:3000 "
        "-e API_BASE_URL=http://ops-api:8000 campusops-web:lab4 >/dev/null"
    )
    for _ in range(90):
        response = outer(
            "curl", "-fsS", "-o", "/dev/null", BASE_URL, check=False
        )
        if response.returncode == 0:
            return
        time.sleep(1)
    raise RuntimeError("LAB 4 web page did not become ready")


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


def nav_link(page: Page, label: str) -> Locator:
    return page.locator("aside nav").get_by_role("link", name=label, exact=False)


def assert_text(page: Page, required: list[str]) -> None:
    content = " ".join(page.locator("main").inner_text().split())
    missing = [text for text in required if " ".join(text.split()) not in content]
    if missing:
        raise RuntimeError(f"page is not at the fixed seed; missing text: {missing}")


def capture(page: Page, name: str, target: Locator) -> list[int]:
    page.wait_for_load_state("networkidle")
    box = measured_box(target)
    page.screenshot(path=str(RAW / f"{name}.png"), full_page=False)
    print(f"+ {name}.png target={box}")
    return box


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    reset_seed()
    boxes: dict[str, list[int]] = {}

    with sync_playwright() as play:
        browser = play.chromium.launch()
        context = browser.new_context(viewport=VIEWPORT, device_scale_factor=1)
        page = context.new_page()

        page.goto(BASE_URL, wait_until="networkidle", timeout=60_000)
        overview = nav_link(page, "สรุปภาพรวม")
        overview.click()
        page.wait_for_url(f"{BASE_URL}/")
        assert_text(
            page,
            [
                "งานที่ยังไม่ปิด 6 ใบ",
                "ค้างเกินกำหนด",
                "ครุภัณฑ์ถูกยืมอยู่",
                "อะไหล่ต้องสั่งเพิ่ม",
            ],
        )
        boxes["ui-net-01-overview"] = capture(page, "ui-net-01-overview", overview)

        loans = nav_link(page, "ยืม-คืนครุภัณฑ์")
        loans.click()
        page.wait_for_url(f"{BASE_URL}/loans")
        loans = nav_link(page, "ยืม-คืนครุภัณฑ์")
        assert_text(page, ["ครุภัณฑ์ที่ยังไม่คืน", "2 รายการ", "A-001", "A-002"])
        boxes["ui-net-02-loans"] = capture(page, "ui-net-02-loans", loans)

        parts = nav_link(page, "คลังอะไหล่")
        parts.click()
        page.wait_for_url(f"{BASE_URL}/parts")
        parts = nav_link(page, "คลังอะไหล่")
        assert_text(page, ["ต่ำกว่าจุดสั่งซื้อ 2 รายการ", "LAMP-EPS-01", "CBL-HDMI-3M"])
        boxes["ui-net-03-parts"] = capture(page, "ui-net-03-parts", parts)

        overview = nav_link(page, "สรุปภาพรวม")
        overview.click()
        page.wait_for_url(f"{BASE_URL}/")
        overview = nav_link(page, "สรุปภาพรวม")
        assert_text(page, ["งานที่ยังไม่ปิด 6 ใบ", "ค้างเกินกำหนด", "ครุภัณฑ์ถูกยืมอยู่"])
        boxes["ui-net-04-back"] = capture(page, "ui-net-04-back", overview)

        browser.close()

    BOXES.write_text(json.dumps(boxes, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"boxes -> {BOXES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
