#!/usr/bin/env python3
"""Host-side Playwright capture for LAB5; run while the four SSH tunnels are open."""

import os
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

SSH_PORT = os.environ.get("LAB_SSH_PORT", "2228")
WEB = os.environ.get("LAB_WEB_URL", "http://127.0.0.1:18320")
TRAEFIK = os.environ.get("LAB_ADMIN_URL", "http://127.0.0.1:18321")
RABBIT = os.environ.get("LAB_RABBIT_URL", "http://127.0.0.1:18322")
KAFKA_UI = os.environ.get("LAB_KAFKA_UI_URL", "http://127.0.0.1:18323")
LAB_DIR = os.environ.get("LAB_INNER_DIR", "/root/lab/005_LAB_Canary_Release_Capstone")
OUT = Path(__file__).resolve().parent / "images"


def inner(command: str) -> str:
    return subprocess.check_output(
        [
            "sshpass", "-p", "passwd", "ssh", "-p", SSH_PORT,
            "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
            "root@127.0.0.1", f"cd {LAB_DIR} && {command}",
        ],
        text=True,
        stderr=subprocess.DEVNULL,
    ).strip()


def shot(page, name: str) -> None:
    page.screenshot(path=str(OUT / name), full_page=False)
    print(f"CAPTURED {name} 1440x900")


OUT.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    public = browser.new_context(viewport={"width": 1440, "height": 900})
    page = public.new_page()

    refreshes = 0
    for refreshes in range(1, 81):
        page.goto(f"{WEB}/", wait_until="networkidle")
        if "ลองข้อความใหม่กับลูกค้ากลุ่มเล็ก" in page.locator("body").inner_text():
            break
    else:
        raise AssertionError("v2 tagline was not observed in 80 page loads")
    shot(page, "01-home-canary-v2.png")
    print(f"V2 BANNER OBSERVED after {refreshes} loads")

    page.locator('input[data-menu-name="matcha"]').fill("แคปสโตน")
    page.locator('article:has(input[data-menu-name="matcha"]) select[name="qty"]').select_option("3")
    page.locator('button[data-order-menu="matcha"]').click()
    page.wait_for_url("**/orders?**", wait_until="networkidle")
    shot(page, "02-order-live-board.png")

    barista = public.new_page()
    barista.goto(f"{WEB}/barista", wait_until="networkidle")
    shot(barista, "03-barista-station.png")

    owner = browser.new_context(
        viewport={"width": 1440, "height": 900},
        http_credentials={"username": "manager", "password": "manager123"},
    )
    dashboard = owner.new_page()
    time.sleep(10)
    dashboard.goto(f"{WEB}/dashboard", wait_until="networkidle")
    shot(dashboard, "04-owner-dashboard.png")

    topology = public.new_page()
    response = topology.goto(f"{TRAEFIK}/api/rawdata", wait_until="networkidle")
    assert response and response.ok, "Traefik rawdata is unavailable"
    response = topology.goto(RABBIT, wait_until="domcontentloaded")
    assert response and response.ok, "RabbitMQ Management UI is unavailable"
    response = topology.goto(KAFKA_UI, wait_until="domcontentloaded", timeout=30_000)
    assert response and response.ok, "Kafka UI is unavailable"
    print("PLAYWRIGHT UI CHECK: Traefik, RabbitMQ and Kafka UI reachable")

    owner.close()
    public.close()
    browser.close()

order_id = inner("docker compose exec -T db psql -U student -d cafedb -Atqc \"SELECT max(id) FROM orders WHERE customer_name='แคปสโตน'\"")
print(f"PLAYWRIGHT CAPTURE PASSED order={order_id}")
