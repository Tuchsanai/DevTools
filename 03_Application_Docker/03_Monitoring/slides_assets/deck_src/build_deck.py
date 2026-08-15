#!/usr/bin/env python3
"""Assemble the single-file Monitoring slide deck (CSS/JS inline, every image embedded as a data URI)."""
import base64, glob, json, mimetypes, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = "/home/workspace/DevTools/03_Application_Docker/03_Monitoring"
ASSETS = f"{ROOT}/slides_assets"
OUT = f"{ROOT}/Monitoring_Prometheus_Grafana_Slides.html"

# lab screenshots: data-a key -> list of candidate paths (first existing wins)
LAB_SHOTS = {
    "l1a": [f"{ROOT}/001_LAB_Prometheus_First_Scrape/images/*targets-up*.png",
            f"{ROOT}/001_LAB_Prometheus_First_Scrape/images/*target*.png"],
    "l1b": [f"{ROOT}/001_LAB_Prometheus_First_Scrape/images/*graph*.png",
            f"{ROOT}/001_LAB_Prometheus_First_Scrape/images/*cpu*.png",
            f"{ROOT}/001_LAB_Prometheus_First_Scrape/images/*query*.png"],
    "l2a": [f"{ROOT}/002_LAB_Container_Metrics_cAdvisor/images/*rate-burners*.png",
            f"{ROOT}/002_LAB_Container_Metrics_cAdvisor/images/*cadvisor*.png"],
    "l3a": [f"{ROOT}/003_LAB_Grafana_Dashboard_As_Code/images/*dashboard*.png"],
    "l4a": [f"{ROOT}/004_LAB_App_Instrumentation_RED/images/*red-dashboard*.png",
            f"{ROOT}/004_LAB_App_Instrumentation_RED/images/*dashboard*.png"],
    "l5a": [f"{ROOT}/005_LAB_Alerting_Alertmanager/images/*receiver-multi*.png",
            f"{ROOT}/005_LAB_Alerting_Alertmanager/images/*receiver*.png",
            f"{ROOT}/005_LAB_Alerting_Alertmanager/images/*alert*.png"],
    "l6a": [f"{ROOT}/006_LAB_Observability_Capstone/images/*status-wall-ok*.png",
            f"{ROOT}/006_LAB_Observability_Capstone/images/*status-wall*.png"],
}

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


def first_match(patterns):
    for pat in patterns:
        hits = sorted(glob.glob(pat))
        if hits:
            return hits[0]
    return None


def main():
    assets, missing = {}, []

    for svg in sorted(glob.glob(f"{ASSETS}/*.svg")):
        key = os.path.basename(svg).split("-")[0]          # d01-why-monitoring.svg -> d01
        assets[key] = data_uri(svg)

    for key, pats in LAB_SHOTS.items():
        hit = first_match(pats)
        if hit:
            assets[key] = data_uri(hit)
            print(f"  {key}  <- {os.path.relpath(hit, ROOT)}")
        else:
            assets[key] = "data:image/svg+xml;base64," + base64.b64encode(PLACEHOLDER.encode()).decode()
            missing.append(key)

    parts = [open(f"{HERE}/00_head.html", encoding="utf-8").read()]
    for f in ("10_slides_a.html", "20_slides_b.html", "30_slides_c.html"):
        parts.append(open(f"{HERE}/{f}", encoding="utf-8").read())
    parts.append("</div>\n")
    parts.append("<script>window.ASSETS=" + json.dumps(assets, ensure_ascii=False) + ";</script>\n")
    parts.append(open(f"{HERE}/90_tail.html", encoding="utf-8").read())
    html = "\n".join(parts)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)

    slides = html.count('<div class="slot">')
    used = set(re.findall(r'data-a="([^"]+)"', html))
    unresolved = sorted(k for k in used if k not in assets)

    print(f"\nwrote {OUT}")
    print(f"  slides       : {slides}")
    print(f"  assets       : {len(assets)}  ({sum(len(v) for v in assets.values())/1024/1024:.2f} MB base64)")
    print(f"  size         : {os.path.getsize(OUT)/1024/1024:.2f} MB")
    if missing:
        print(f"  MISSING SHOTS: {', '.join(missing)}")
    if unresolved:
        print(f"  UNRESOLVED   : {', '.join(unresolved)}")
    return 1 if unresolved else 0


if __name__ == "__main__":
    sys.exit(main())
