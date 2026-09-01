#!/usr/bin/env python3
"""Hold one headless Chromium tab on the Excalidraw canvas so `mcp-excalidraw-server screenshot/export` can render.

  PORT=3311 EXPRESS_SERVER_URL=http://127.0.0.1:3311 npx -y mcp-excalidraw-server start &
  python3 tools/canvas_tab.py http://127.0.0.1:3311 &
"""
import sys, time
from playwright.sync_api import sync_playwright

url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:3311"
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1500, "height": 900})
    pg.goto(url, wait_until="load", timeout=60000)
    print("canvas tab open:", url, flush=True)
    while True:
        time.sleep(3600)
