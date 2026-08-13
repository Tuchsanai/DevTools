#!/usr/bin/env python3
"""Assemble Docker_Week09_Slides.html — a single self-contained file.

  tools/deck_template.html   shell : CSS + nav JS, with <!--SLIDES--> and window.ASSETS={}
  tools/slides_body.html     the slides themselves
  slides_assets/*.svg        Excalidraw figures      -> ASSETS key = file stem (f01…f13)
  0NN_LAB_*/images/*.png     real screenshots        -> ASSETS key = declared in ASSET_SHOTS

Everything is inlined as data: URIs, so the result works offline with no CDN.
"""
import base64
import html
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from lab_outputs import MARKERS  # noqa: E402  (needs HERE on sys.path)
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "Docker_Week09_Slides.html")

# screenshot key -> repo-relative path
ASSET_SHOTS = {
    "sh_control":   "001_LAB_Container_Control_Room/images/control-room-web.png",
    "sh_red":       "002_LAB_Env_Color_Factory/images/color-red.png",
    "sh_green":     "002_LAB_Env_Color_Factory/images/color-green.png",
    "sh_blue":      "002_LAB_Env_Color_Factory/images/color-blue.png",
    "sh_diet":      "003_LAB_Image_Diet/images/diet-report.png",
    "sh_vision":    "004_LAB_Vision_API_Compose/images/vision-ui.png",
    "sh_docs":      "004_LAB_Vision_API_Compose/images/vision-docs.png",
    "sh_ops":       "005_LAB_Ops_Clinic/images/ops-healthy.png",
}

MAX_SHOT_W = 1400
JPEG_Q = 86


def svg_assets():
    out = {}
    d = os.path.join(ROOT, "slides_assets")
    if not os.path.isdir(d):
        return out
    for name in sorted(os.listdir(d)):
        if not name.endswith(".svg"):
            continue
        key = name[:-4].split("-")[0]          # f01-week9-roadmap.svg -> f01
        raw = open(os.path.join(d, name), "rb").read()
        out[key] = "data:image/svg+xml;base64," + base64.b64encode(raw).decode()
    return out


def shot_assets():
    out, missing = {}, []
    try:
        from PIL import Image
    except ImportError:
        Image = None
    for key, rel in ASSET_SHOTS.items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            missing.append(rel)
            continue
        if Image is None:
            out[key] = "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
            continue
        im = Image.open(p).convert("RGB")
        if im.width > MAX_SHOT_W:
            im = im.resize((MAX_SHOT_W, round(im.height * MAX_SHOT_W / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=JPEG_Q, optimize=True, progressive=True)
        out[key] = "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()
    return out, missing


def main():
    tpl = open(os.path.join(HERE, "deck_template.html"), encoding="utf-8").read()
    body = open(os.path.join(HERE, "slides_body.html"), encoding="utf-8").read()

    assets = svg_assets()
    shots, missing = shot_assets()
    assets.update(shots)

    for key, value in MARKERS.items():
        body = body.replace("{{%s}}" % key, html.escape(value))

    doc = tpl.replace("<!--SLIDES-->", body)
    payload = "window.ASSETS={" + ",".join(
        '"%s":"%s"' % (k, v) for k, v in sorted(assets.items())) + "};"
    doc = doc.replace("window.ASSETS={};", payload)

    open(OUT, "w", encoding="utf-8").write(doc)

    leftover = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", body)))
    used = set(re.findall(r'data-a="([^"]+)"', body))
    print("slides      :", body.count('<div class="slot">'))
    print("assets      :", len(assets), "(" + ", ".join(sorted(assets)) + ")")
    print("size        : %.2f MB" % (os.path.getsize(OUT) / 1024 / 1024))
    if missing:
        print("MISSING shot files:", *missing, sep="\n  ")
    unresolved = sorted(used - set(assets))
    if unresolved:
        print("MISSING asset keys referenced by slides:", unresolved)
    unused = sorted(set(assets) - used)
    if unused:
        print("unused assets:", unused)
    if leftover:
        print("UNFILLED OUTPUT MARKERS (real captured output still missing):", *leftover, sep="\n  ")
    return 1 if (missing or unresolved or leftover) else 0


if __name__ == "__main__":
    sys.exit(main())
