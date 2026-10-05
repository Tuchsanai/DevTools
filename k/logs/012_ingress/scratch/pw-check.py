# ตรวจฉาก screenshot: Chromium + host-resolver-rules map *.localhost:3008x → gateway:3009x (ไม่แตะพอร์ตของ k8s-lab ผู้เรียน)
import base64, sys
from playwright.sync_api import sync_playwright
G = sys.argv[1]; NP0 = int(sys.argv[2])
m = {30080: NP0, 30081: NP0 + 1, 30082: NP0 + 2}
rules = ", ".join(f"MAP {h}:{p} {G}:{hp}" for h in ("shop.localhost", "admin.localhost", "other.localhost", "localhost") for p, hp in m.items())
out = []
with sync_playwright() as p:
    b = p.chromium.launch(args=[f"--host-resolver-rules={rules}"])
    ctx = b.new_context(ignore_https_errors=True)
    pg = ctx.new_page()
    r = pg.goto("http://shop.localhost:30080/")
    out.append(f"shop: final url={pg.url} status={r.status} title={pg.title()} chain={[x.url for x in (lambda q: [q] + ([] if not q.redirected_from else []))(r.request)]}")
    req = r.request; chain = []
    while req: chain.append(req.url); req = req.redirected_from
    out.append(f"shop redirect chain (ล่าสุดก่อน): {chain}")
    out.append("footer: " + pg.locator("footer").inner_text().replace("\n", " | "))
    pg.screenshot(path="pw-012-shop.png")
    r = pg.goto("https://admin.localhost:30081/"); out.append(f"admin no auth: {r.status}")
    ctx2 = b.new_context(ignore_https_errors=True, http_credentials={"username": "som", "password": "meow-admin-123"})
    p2 = ctx2.new_page(); r = p2.goto("http://admin.localhost:30080/"); out.append(f"admin with auth: {p2.url} {r.status} h1={p2.locator('h1').inner_text()}")
    r = p2.goto("https://admin.localhost:30081/stats"); out.append(f"admin /stats: {r.status} {p2.locator('body').inner_text().strip()}")
    r = pg.goto("http://other.localhost:30080/"); out.append(f"other: {r.status} {pg.locator('body').inner_text().strip()}")
    r = pg.goto("http://localhost:30082/dashboard/"); pg.wait_for_timeout(1500); out.append(f"dashboard: {r.status} title={pg.title()}")
    pg.screenshot(path="pw-012-dashboard.png")
    b.close()
print("\n".join(out))
