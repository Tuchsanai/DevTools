#!/usr/bin/env python3
"""ถ่าย walkthrough หน้า CampusOps ของ LAB 5 ด้วยข้อมูล seed คงที่"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import Locator, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "tools/ui/raw"
BOXES = RAW / "lab5-boxes.json"
VIEWPORT = {"width": 1440, "height": 900}
OUTER_CONTAINER = "devtools-fs-lab5"
LAB_DIR = "/root/lab5"
PUBLISHED_URL = "http://localhost:8255"


def run_in_lab(command: str) -> None:
    subprocess.run(
        ["docker", "exec", OUTER_CONTAINER, "bash", "-lc", f"cd {LAB_DIR} && {command}"],
        check=True,
    )


def reset_seed() -> None:
    run_in_lab("docker compose -p campusops down -v")
    run_in_lab("docker compose -p campusops up -d --no-build")
    for _ in range(60):
        result = subprocess.run(
            [
                "docker",
                "exec",
                OUTER_CONTAINER,
                "docker",
                "inspect",
                "-f",
                "{{.State.Health.Status}}",
                "campusops-db-1",
                "campusops-api-1",
                "campusops-web-1",
            ],
            text=True,
            capture_output=True,
        )
        if result.returncode == 0 and result.stdout.count("healthy") == 3:
            return
        time.sleep(2)
    raise RuntimeError("CampusOps ไม่ healthy ครบภายใน 120 วินาที")


def reachable_url() -> str:
    """ใช้พอร์ตที่ publish เป็นหลัก และใช้ IP ของกล่องเมื่อโฮสต์รัน Docker แบบรีโมต"""
    candidates = [PUBLISHED_URL]
    address = subprocess.run(
        [
            "docker",
            "inspect",
            "-f",
            "{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}",
            OUTER_CONTAINER,
        ],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    if address:
        candidates.append(f"http://{address}:3000")
    for _ in range(30):
        for candidate in candidates:
            try:
                with urllib.request.urlopen(candidate, timeout=2) as response:
                    if response.status == 200:
                        return candidate
            except OSError:
                pass
        time.sleep(2)
    raise RuntimeError("หน้า CampusOps ไม่ตอบผ่านพอร์ตที่ publish")


def box(locator: Locator, pad: int = 6) -> list[int]:
    locator.wait_for(state="visible", timeout=20_000)
    rect = locator.bounding_box()
    if not rect:
        raise RuntimeError("ไม่พบกรอบของ element ที่ต้องใส่ marker")
    return [
        max(0, int(rect["x"]) - pad),
        max(0, int(rect["y"]) - pad),
        min(VIEWPORT["width"], int(rect["x"] + rect["width"]) + pad),
        min(VIEWPORT["height"], int(rect["y"] + rect["height"]) + pad),
    ]


def main() -> int:
    RAW.mkdir(parents=True, exist_ok=True)
    reset_seed()
    app_url = reachable_url()
    shots: dict[str, list[dict[str, object]]] = {}

    with sync_playwright() as play:
        browser = play.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.goto(app_url, wait_until="networkidle", timeout=60_000)

        brand = page.get_by_text("CampusOps", exact=True).first
        overview = page.locator("a[href='/']", has_text="สรุปภาพรวม").first
        tickets = page.locator("a[href='/tickets']", has_text="กระดานงานซ่อม").first
        page.screenshot(path=str(RAW / "ui-compose-01-overview.png"))
        shots["ui-compose-01-overview"] = [
            {"label": "① เปิดหน้า CampusOps", "box": box(brand)},
        ]

        tickets.click()
        page.wait_for_url("**/tickets")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(RAW / "ui-compose-02-tickets.png"))
        shots["ui-compose-02-tickets"] = [
            {"label": "② เปิดกระดานงานซ่อม", "box": box(tickets)},
        ]

        overview.click()
        page.wait_for_url(app_url + "/")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=str(RAW / "ui-compose-03-back-overview.png"))
        shots["ui-compose-03-back-overview"] = [
            {"label": "③ กลับสรุปภาพรวม", "box": box(overview)},
        ]
        browser.close()

    BOXES.write_text(json.dumps(shots, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"บันทึกภาพ 3 ใบและพิกัดที่ {BOXES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
