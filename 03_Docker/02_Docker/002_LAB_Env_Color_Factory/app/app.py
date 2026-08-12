"""Color Factory — แอป Flask ตัวเล็ก ๆ ที่ 'บุคลิก' ทั้งหมดมาจาก environment variable

อ่านค่า 3 ตัวจากข้างนอก:
  APP_COLOR  สีของหน้าเว็บ   (default ในโค้ด: blue)
  APP_NAME   ชื่อที่โชว์บนการ์ด (default ในโค้ด: Color Factory)
  APP_PORT   port ที่ Flask ฟัง (default ในโค้ด: 8081)

ไฟล์ build_defaults.json ถูกเขียนตอน docker build จากค่า ENV ใน Dockerfile
แอปจึงบอกได้ว่าค่าที่ใช้อยู่ตอนนี้ "มาจากไหน" — โค้ด / Dockerfile ENV / override ตอน run
"""

import json
import os
import socket

from flask import Flask, jsonify

app = Flask(__name__)

# ---- default ในโค้ด (ชั้นล่างสุดของลำดับความสำคัญ) -------------------------
CODE_DEFAULTS = {
    "APP_COLOR": "blue",
    "APP_NAME": "Color Factory",
    "APP_PORT": "8081",
}

# ---- ค่า ENV ที่ถูก 'อบ' ไว้ใน image ตอน docker build ----------------------
try:
    with open("/app/build_defaults.json", encoding="utf-8") as fh:
        BUILD_DEFAULTS = json.load(fh)
except OSError:
    BUILD_DEFAULTS = {}

PALETTE = {
    "red": ("#c0392b", "#7b1f16"),
    "green": ("#1e8449", "#0e4a29"),
    "blue": ("#2471a3", "#123c58"),
    "blue2": ("#1a5276", "#0d2b3d"),
    "pink": ("#c2185b", "#6d0e33"),
    "darkblue": ("#1b2a49", "#0b1424"),
    "orange": ("#ca6f1e", "#6f3c10"),
}


def resolve(key):
    """คืน (ค่าใช้จริง, แหล่งที่มา) ของ environment variable หนึ่งตัว"""
    runtime = os.environ.get(key)
    baked = BUILD_DEFAULTS.get(key)
    if runtime is None:
        return CODE_DEFAULTS[key], "code default"
    if baked is not None and runtime == baked:
        return runtime, "Dockerfile ENV"
    if baked is not None and runtime != baked:
        return runtime, "override at run (-e / --env-file)"
    return runtime, "runtime env"


def state():
    color, color_src = resolve("APP_COLOR")
    name, name_src = resolve("APP_NAME")
    port, port_src = resolve("APP_PORT")
    return {
        "app_color": color,
        "app_color_source": color_src,
        "app_name": name,
        "app_name_source": name_src,
        "app_port": port,
        "app_port_source": port_src,
        "hostname": socket.gethostname(),
        "image_env_defaults": BUILD_DEFAULTS,
        "known_colors": sorted(PALETTE),
    }


PAGE = """<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{name} — {color}</title>
<style>
  *{{box-sizing:border-box}}
  body{{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
       font-family:"DejaVu Sans","Noto Sans Thai",system-ui,sans-serif;
       background:linear-gradient(140deg,{c1} 0%,{c2} 100%);color:#fff}}
  .card{{width:min(680px,92vw);background:rgba(0,0,0,.28);border:1px solid rgba(255,255,255,.22);
        border-radius:18px;padding:28px 30px;backdrop-filter:blur(2px);
        box-shadow:0 18px 50px rgba(0,0,0,.35)}}
  .kicker{{letter-spacing:.22em;font-size:12px;opacity:.75;text-transform:uppercase}}
  h1{{margin:6px 0 2px;font-size:38px;line-height:1.15}}
  .swatch{{display:inline-block;padding:4px 14px;border-radius:999px;font-size:26px;font-weight:700;
          background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.35)}}
  table{{width:100%;border-collapse:collapse;margin-top:18px;font-size:14px}}
  th,td{{text-align:left;padding:9px 10px;border-bottom:1px solid rgba(255,255,255,.16)}}
  th{{font-size:11px;letter-spacing:.12em;text-transform:uppercase;opacity:.7}}
  td.k{{font-family:"DejaVu Sans Mono",monospace;font-weight:700}}
  td.v{{font-family:"DejaVu Sans Mono",monospace}}
  .src{{font-size:12px;padding:3px 9px;border-radius:6px;background:rgba(255,255,255,.14);
       border:1px solid rgba(255,255,255,.3);white-space:nowrap}}
  .foot{{margin-top:16px;font-size:12.5px;opacity:.8;line-height:1.65}}
  code{{background:rgba(0,0,0,.3);padding:1px 6px;border-radius:5px}}
</style></head>
<body><div class="card">
  <div class="kicker">Docker Week 9 &middot; LAB 2 &middot; Env Color Factory</div>
  <h1>{name}</h1>
  <div><span class="swatch">APP_COLOR = {color}</span></div>
  <table>
    <tr><th>ตัวแปร</th><th>ค่าที่ใช้จริง</th><th>มาจากไหน</th></tr>
    <tr><td class="k">APP_COLOR</td><td class="v">{color}</td><td><span class="src">{color_src}</span></td></tr>
    <tr><td class="k">APP_NAME</td><td class="v">{name}</td><td><span class="src">{name_src}</span></td></tr>
    <tr><td class="k">APP_PORT</td><td class="v">{port}</td><td><span class="src">{port_src}</span></td></tr>
    <tr><td class="k">hostname</td><td class="v">{host}</td><td><span class="src">container id</span></td></tr>
  </table>
  <div class="foot">
    image เดียวกันทุกหน้า — เปลี่ยนแค่ <code>-e APP_COLOR=...</code> ตอน <code>docker run</code><br>
    ตรวจแบบเครื่องอ่านได้ที่ <code>/healthz</code>
  </div>
</div></body></html>"""


@app.route("/")
def home():
    s = state()
    c1, c2 = PALETTE.get(s["app_color"], PALETTE["blue"])
    return PAGE.format(
        name=s["app_name"],
        color=s["app_color"],
        color_src=s["app_color_source"],
        name_src=s["app_name_source"],
        port=s["app_port"],
        port_src=s["app_port_source"],
        host=s["hostname"],
        c1=c1,
        c2=c2,
    )


@app.route("/healthz")
def healthz():
    payload = {"status": "ok"}
    payload.update(state())
    return jsonify(payload)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(resolve("APP_PORT")[0]))
