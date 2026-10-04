#!/usr/bin/env python3
"""Render one Excalidraw scene (JSON array of elements, same format as diagrams.py) to SVG + .excalidraw + PNG preview.

Parallel-safe: each caller picks its own canvas port (default 3311). The canvas server (mcp-excalidraw-server) and a
headless Chromium tab are started on that port if not running.

  python3 tools/render_scene.py --port 3401 scenes_src/d20-sdlc.json            # -> ../d20-sdlc.svg, ../scenes/d20-sdlc.excalidraw, .deckshots/d20-sdlc.png
  python3 tools/render_scene.py --port 3401 --preview-only scenes_src/d20-sdlc.json   # only the PNG preview (scratch)
"""
import argparse, json, os, subprocess, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))          # deck_src
OUT = os.path.abspath(os.path.join(HERE, ".."))                              # slides_assets
PREV = os.path.join(HERE, ".deckshots")


def sh(cmd, env, timeout=120):
    return subprocess.run(cmd, shell=True, env=env, capture_output=True, text=True, timeout=timeout)


def server_up(url):
    try:
        with urllib.request.urlopen(url + "/api/elements", timeout=3) as r:
            return r.status == 200
    except Exception:
        return False


def ensure_server(port):
    url = f"http://127.0.0.1:{port}"
    env = dict(os.environ, EXPRESS_SERVER_URL=url, PORT=str(port))
    if not server_up(url):
        subprocess.Popen(f"PORT={port} EXPRESS_SERVER_URL={url} npx -y mcp-excalidraw-server start", shell=True,
                         env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(40):
            time.sleep(1)
            if server_up(url):
                break
    st = sh("npx -y mcp-excalidraw-server status", env)
    try:
        clients = json.loads(st.stdout).get("browserClients", 0)
    except Exception:
        clients = 0
    if clients < 1:
        subprocess.Popen(f"python3 {os.path.join(HERE, 'tools', 'canvas_tab.py')} {url}", shell=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(30):
            time.sleep(1)
            st = sh("npx -y mcp-excalidraw-server status", env)
            try:
                if json.loads(st.stdout).get("browserClients", 0) >= 1:
                    break
            except Exception:
                pass
    return env


def svg_to_png(svg_path, png_path, scale=1.0):
    """Rasterise an Excalidraw SVG (embedded fonts) via an <img> wrapper — screenshotting the SVG document directly
    makes Chromium wait forever for the data-URI fonts."""
    from playwright.sync_api import sync_playwright
    html = os.path.join(PREV, os.path.basename(svg_path) + ".html")
    with open(html, "w", encoding="utf-8") as f:
        f.write('<!doctype html><html><body style="margin:0;background:#fff"><img id="im" src="file://%s"></body></html>' % os.path.abspath(svg_path))
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1400, "height": 800}, device_scale_factor=scale)
        pg.goto("file://" + os.path.abspath(html), wait_until="load", timeout=60000)
        pg.wait_for_function("() => { const i = document.getElementById('im'); return i.complete && i.naturalWidth > 0; }", timeout=60000)
        pg.wait_for_timeout(500)
        dims = pg.evaluate("() => { const i = document.getElementById('im'); return [i.naturalWidth, i.naturalHeight]; }")
        pg.set_viewport_size({"width": max(int(dims[0]), 10), "height": max(int(dims[1]), 10)})
        pg.wait_for_timeout(300)
        pg.locator("#im").screenshot(path=png_path, timeout=60000)
        b.close()
    os.remove(html)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scene", help="JSON file with an array of Excalidraw elements")
    ap.add_argument("--port", type=int, default=3311)
    ap.add_argument("--preview-only", action="store_true")
    ap.add_argument("--out-dir", default=OUT)
    args = ap.parse_args()
    name = os.path.splitext(os.path.basename(args.scene))[0]
    env = ensure_server(args.port)
    os.makedirs(PREV, exist_ok=True)
    os.makedirs(os.path.join(args.out_dir, "scenes"), exist_ok=True)
    sh("npx -y mcp-excalidraw-server clear --yes", env)
    r = sh(f"npx -y mcp-excalidraw-server add {os.path.abspath(args.scene)}", env)
    if r.returncode != 0:
        print(f"[{name}] ADD FAILED rc={r.returncode}: {r.stderr[:400] or r.stdout[:400]}")
        sys.exit(1)
    time.sleep(2.5)
    tmp_svg = os.path.join(PREV, f"{name}.svg") if args.preview_only else os.path.join(args.out_dir, f"{name}.svg")
    r = sh(f"npx -y mcp-excalidraw-server screenshot --format svg --out {tmp_svg}", env)
    ok = os.path.exists(tmp_svg) and os.path.getsize(tmp_svg) > 2000
    if not ok:
        print(f"[{name}] SCREENSHOT FAILED rc={r.returncode}: {r.stderr[:400] or r.stdout[:400]}")
        sys.exit(1)
    if not args.preview_only:
        sh(f"npx -y mcp-excalidraw-server export --out {os.path.join(args.out_dir, 'scenes', name + '.excalidraw')}", env)
    png = os.path.join(PREV, f"{name}.png")
    svg_to_png(tmp_svg, png)
    with open(tmp_svg, encoding="utf-8") as f:
        head = f.read(400)
    import re
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', head)
    print(f"[{name}] OK svg={tmp_svg} ({os.path.getsize(tmp_svg)} bytes, viewBox {m.group(1) if m else '?'}x{m.group(2) if m else '?'}) preview={png}")


if __name__ == "__main__":
    main()
