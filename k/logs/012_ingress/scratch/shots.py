# Real screenshots for chapter 012 — Chromium uses the same URLs students use (shop.localhost:30080/30081),
# resolver maps them to the test container's host ports 30090-30092 on the gateway.
import sys
from playwright.sync_api import sync_playwright
G="172.18.0.1"; m={30080:30090,30081:30091,30082:30092}
rules=", ".join(f"MAP {h}:{p} {G}:{hp}" for h in ("shop.localhost","admin.localhost","other.localhost","localhost") for p,hp in m.items())
S="/root/workspace/DevTools/k/screenshots/20261005_2035_lab10ing_"
with sync_playwright() as p:
    b=p.chromium.launch(args=[f"--host-resolver-rules={rules}"])
    # 1) self-signed warning (no ignore_https_errors)
    c0=b.new_context(viewport={"width":1366,"height":900}); p0=c0.new_page()
    try: p0.goto("https://shop.localhost:30081/")
    except Exception as e: print("warn page:", str(e).splitlines()[0])
    p0.screenshot(path=S+"01-https-selfsigned-warning.png"); c0.close()
    c=b.new_context(ignore_https_errors=True, viewport={"width":1366,"height":900}); pg=c.new_page()
    # 2) http -> redirect -> https shop
    r=pg.goto("http://shop.localhost:30080/"); req=r.request; chain=[]
    while req: chain.append(req.url); req=req.redirected_from
    print("shop", r.status, pg.url, chain[::-1]); pg.screenshot(path=S+"02-shop-via-ingress-https.png")
    # 3) admin without login -> 401
    r=pg.goto("https://admin.localhost:30081/"); print("admin no auth", r.status); pg.screenshot(path=S+"03-admin-401-no-login.png")
    # 4) admin with login
    c2=b.new_context(ignore_https_errors=True, viewport={"width":1366,"height":900}, http_credentials={"username":"som","password":"meow-admin-123"})
    p2=c2.new_page(); r=p2.goto("https://admin.localhost:30081/"); print("admin auth", r.status, p2.url); p2.screenshot(path=S+"04-admin-200-after-login.png")
    # 5) unknown host -> 404
    r=pg.goto("http://other.localhost:30080/"); print("other", r.status); pg.screenshot(path=S+"05-unknown-host-404.png")
    # 6) Traefik dashboard
    r=pg.goto("http://localhost:30082/dashboard/"); pg.wait_for_timeout(2500); print("dashboard", r.status, pg.title()); pg.screenshot(path=S+"06-traefik-dashboard.png")
    b.close()
