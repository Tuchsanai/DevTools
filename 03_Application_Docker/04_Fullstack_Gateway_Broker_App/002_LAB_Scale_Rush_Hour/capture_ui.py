#!/usr/bin/env python3
"""Host-side Playwright capture for LAB2; run only while SSH tunnels are open."""

import os
import subprocess
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

SSH_PORT = os.environ.get("LAB_SSH_PORT", "2228")
WEB = os.environ.get("LAB_WEB_URL", "http://127.0.0.1:18320")
ADMIN = os.environ.get("LAB_ADMIN_URL", "http://127.0.0.1:18321")
LAB_DIR = os.environ.get("LAB_INNER_DIR", "/root/lab/002_LAB_Scale_Rush_Hour")
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


def shot(page, url: str, name: str) -> None:
    page.goto(url, wait_until="networkidle")
    page.screenshot(path=str(OUT / name), full_page=False)
    print(f"CAPTURED {name} 1440x900")


OUT.mkdir(parents=True, exist_ok=True)
target = inner("id=$(docker compose ps -q api | head -1); "
               "docker inspect --format '{{.Config.Hostname}}|{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $id")
target_name, target_ip = target.split("|", 1)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    public = browser.new_context(viewport={"width": 1440, "height": 900})
    page = public.new_page()
    shot(page, f"{WEB}/", "01-home-rush-hour.png")
    shot(page, f"{ADMIN}/dashboard/#/http/services/api@docker", "02-traefik-three-servers.png")

    inner(f"curl -fsS -X POST http://{target_ip}:8000/api/health/fail >/dev/null")
    time.sleep(5)
    page.reload(wait_until="networkidle")
    page.screenshot(path=str(OUT / "03-traefik-one-down.png"), full_page=False)
    print(f"CAPTURED 03-traefik-one-down.png 1440x900 target={target_name}")
    inner(f"curl -fsS -X POST http://{target_ip}:8000/api/health/ok >/dev/null")
    time.sleep(4)

    owner = browser.new_context(
        viewport={"width": 1440, "height": 900},
        http_credentials={"username": "manager", "password": "manager123"},
    )
    owner_page = owner.new_page()
    shot(owner_page, f"{WEB}/dashboard", "04-owner-dashboard.png")
    owner.close()
    public.close()
    browser.close()

print("PLAYWRIGHT CAPTURE PASSED")
