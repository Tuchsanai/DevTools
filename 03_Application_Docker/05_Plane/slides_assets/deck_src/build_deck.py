#!/usr/bin/env python3
"""Assemble the single-file Plane slide deck (CSS/JS inline, every image embedded as a data URI).

Assets are picked up automatically:
  slides_assets/*.svg                 -> key = name prefix before the first '-'   (d01-scrum-to-plane.svg -> "d01")
  slides_assets/illustrations/*.svg   -> key = file stem                          (scrum_cycle.svg -> "scrum_cycle")
  slides_assets/screenshots/*.png     -> key = file stem                          (l1-setup-form.png -> "l1-setup-form")
  00N_LAB_*/images/*.png              -> key = "lab<N>:" + file stem              (001_LAB_x/images/ui-home.png -> "lab1:ui-home")
Slides reference assets with <img data-a="key">. Missing keys get a visible placeholder and are reported.
"""
import base64, glob, json, mimetypes, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ASSETS = os.path.join(ROOT, "slides_assets")
OUT = os.path.join(ROOT, "Plane_Agile_Slides.html")

PLACEHOLDER = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 675"><rect width="1200" height="675" '
               'fill="#f1f3f5" stroke="#adb5bd" stroke-width="3" stroke-dasharray="12 8"/><text x="600" y="330" '
               'text-anchor="middle" font-family="sans-serif" font-size="34" fill="#868e96">ยังไม่มีภาพจากการรันจริง</text>'
               '<text x="600" y="380" text-anchor="middle" font-family="sans-serif" font-size="22" fill="#adb5bd">'
               'MISSING SCREENSHOT</text></svg>')


def data_uri(path):
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    if path.endswith(".svg"):
        mime = "image/svg+xml"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def collect_assets():
    assets = {}
    for svg in sorted(glob.glob(f"{ASSETS}/*.svg")):
        assets[os.path.basename(svg).split("-")[0]] = data_uri(svg)
    for svg in sorted(glob.glob(f"{ASSETS}/illustrations/*.svg")):
        assets[os.path.splitext(os.path.basename(svg))[0]] = data_uri(svg)
    for png in sorted(glob.glob(f"{ASSETS}/screenshots/*.png")):
        assets[os.path.splitext(os.path.basename(png))[0]] = data_uri(png)
    for lab in sorted(glob.glob(f"{ROOT}/0*_LAB_*")):
        n = int(os.path.basename(lab)[:3])
        for png in sorted(glob.glob(f"{lab}/images/*.png")):
            assets[f"lab{n}:{os.path.splitext(os.path.basename(png))[0]}"] = data_uri(png)
    return assets


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", nargs="*", default=None, help="build only these fragment files (default: all [1-8]?_*.html)")
    ap.add_argument("--out", default=OUT)
    args = ap.parse_args()
    out_path = args.out
    assets = collect_assets()
    parts = [open(f"{HERE}/00_head.html", encoding="utf-8").read()]
    slide_files = sorted(f for f in os.listdir(HERE) if re.match(r"^[1-8]\d_.*\.html$", f))
    if args.only:
        slide_files = [f for f in slide_files if f in args.only or os.path.basename(f) in [os.path.basename(x) for x in args.only]]
    for f in slide_files:
        parts.append(open(f"{HERE}/{f}", encoding="utf-8").read())
    parts.append("</div>\n")
    html_body = "\n".join(parts)
    used = sorted(set(re.findall(r'data-a="([^"]+)"', html_body)))
    missing = [k for k in used if k not in assets]
    for k in missing:
        assets[k] = "data:image/svg+xml;base64," + base64.b64encode(PLACEHOLDER.encode()).decode()
    embedded = {k: v for k, v in assets.items() if k in used}
    parts.append("<script id=\"assets\">window.ASSETS=" + json.dumps(embedded, ensure_ascii=False) + ";</script>\n")
    parts.append(open(f"{HERE}/90_tail.html", encoding="utf-8").read())
    html = "\n".join(parts)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"wrote {out_path}")
    print(f"  slide files  : {', '.join(slide_files)}")
    print(f"  slides       : {html.count('<div class=\"slot\"')}")
    print(f"  assets used  : {len(embedded)} of {len(assets)} available ({sum(len(v) for v in embedded.values())/1024/1024:.2f} MB base64)")
    print(f"  size         : {os.path.getsize(out_path)/1024/1024:.2f} MB")
    ext = re.findall(r'(?:src|href)="(https?://[^"]+)"', html)
    if ext:
        print(f"  EXTERNAL REFS: {ext[:5]}")
    if missing:
        print(f"  MISSING      : {', '.join(missing)}")
    return 1 if (missing or ext) else 0


if __name__ == "__main__":
    sys.exit(main())
