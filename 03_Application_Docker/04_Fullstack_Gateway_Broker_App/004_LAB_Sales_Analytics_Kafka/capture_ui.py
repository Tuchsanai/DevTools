#!/usr/bin/env python3
"""Host-side Playwright capture for LAB4; run while SSH tunnels are open."""

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

WEB = os.environ.get("LAB_WEB_URL", "http://127.0.0.1:18300")
ADMIN = os.environ.get("LAB_ADMIN_URL", "http://127.0.0.1:18301")
KAFKA_UI = os.environ.get("LAB_KAFKA_UI_URL", "http://127.0.0.1:18302")
OUT = Path(__file__).resolve().parent / "images"


def shot(page, url: str, name: str) -> None:
    page.goto(url, wait_until="networkidle", timeout=60_000)
    page.screenshot(path=str(OUT / name), full_page=False)
    print(f"CAPTURED {name} 1440x900")


OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    public = browser.new_context(viewport={"width": 1440, "height": 900})
    page = public.new_page()
    shot(page, f"{WEB}/", "01-cafe-home.png")
    shot(page, f"{KAFKA_UI}/ui/clusters/chongjai/all-topics/cafe.events/messages", "02-kafka-topic.png")
    shot(page, f"{KAFKA_UI}/ui/clusters/chongjai/consumer-groups/analytics", "03-analytics-group.png")

    owner = browser.new_context(
        viewport={"width": 1440, "height": 900},
        http_credentials={"username": "manager", "password": "manager123"},
    )
    owner_page = owner.new_page()
    shot(owner_page, f"{WEB}/dashboard", "04-owner-dashboard.png")
    shot(page, f"{ADMIN}/dashboard/#/http/routers", "05-traefik-routers.png")
    owner.close()
    public.close()
    browser.close()

print("PLAYWRIGHT CAPTURE PASSED")
