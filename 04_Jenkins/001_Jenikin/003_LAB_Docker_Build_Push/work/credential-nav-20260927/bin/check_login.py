#!/usr/bin/env python3
"""Headless check that the real form login works (no screenshots kept)."""
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto('http://127.0.0.1:8080/login')
    pg.fill('input[name=j_username]', 'admin'); pg.fill('input[name=j_password]', 'admin2569')
    pg.click('button[type=submit], input[type=submit]'); pg.wait_for_load_state()
    print('after login:', pg.url)
    for path in ['/manage/', '/manage/credentials/', '/manage/credentials/store/system/']:
        r = pg.goto('http://127.0.0.1:8080' + path); print(path, r.status, pg.title())
    b.close()
