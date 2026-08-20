#!/usr/bin/env python3
"""ถ่ายภาพหน้าเว็บของ image ที่กำลังรัน (พอร์ต 8185 บนเครื่องโฮสต์) เพื่อใช้เป็นหลักฐานในเอกสาร LAB"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "tools/ui/raw"

def main() -> int:
    if len(sys.argv) != 3:
        raise SystemExit("usage: site_capture.py <url> <name>")
    url, name = sys.argv[1], sys.argv[2]
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as play:
        browser = play.chromium.launch()
        page = browser.new_context(viewport={"width": 1280, "height": 760}).new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1200)
        page.screenshot(path=str(OUT / f"{name}.png"))
        browser.close()
    print(f"{OUT / name}.png")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
