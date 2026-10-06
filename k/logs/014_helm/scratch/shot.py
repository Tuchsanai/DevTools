import sys
from playwright.sync_api import sync_playwright
G="172.18.0.1"
rules=f"MAP shop.localhost:30081 {G}:30101, MAP admin.localhost:30081 {G}:30101, MAP *.localhost:30080 {G}:30100, MAP shop.localhost:30080 {G}:30100, MAP localhost:30082 {G}:30102"
S=sys.argv[1]; shots=sys.argv[2:]
with sync_playwright() as p:
    b=p.chromium.launch(args=[f"--host-resolver-rules={rules}"]); c=b.new_context(ignore_https_errors=True, viewport={"width":1366,"height":900}); pg=c.new_page()
    for s in shots:
        name,url=s.split("=",1); r=pg.goto(url); pg.wait_for_timeout(2000 if 'dashboard' in url else 500)
        print(name, r.status if r else '-', pg.url, pg.title()); pg.screenshot(path=S+name+".png")
    b.close()
