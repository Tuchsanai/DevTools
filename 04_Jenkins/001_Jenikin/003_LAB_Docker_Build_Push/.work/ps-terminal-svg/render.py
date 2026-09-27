from playwright.sync_api import sync_playwright
from pathlib import Path
import base64
here = Path(__file__).resolve().parent
img = here.parents[1] / "images"
with sync_playwright() as p:
    b = p.chromium.launch()
    for n in ["lab3_powershell_terminal_network_create_pending", "lab3_powershell_terminal_devtools_run_pending"]:
        pg = b.new_page(viewport={"width": 1600, "height": 500})
        pg.set_content(f'<html><body style="margin:0;background:#fff"><img id="i" src="data:image/svg+xml;base64,{base64.b64encode((img / (n + '.svg')).read_bytes()).decode()}"></body></html>')
        pg.wait_for_timeout(800)
        pg.locator("#i").screenshot(path=str(here / f"{n}.png"), animations="disabled", timeout=60000)
    b.close()
