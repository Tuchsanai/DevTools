"""IMAGE DIET REPORT
เว็บเล็ก ๆ ที่ "รายงานตัวเอง" ว่า image ที่มันอาศัยอยู่นั้นผอมแค่ไหน
และรันด้วย user อะไร  ใช้ใน LAB 3 (003_LAB_Image_Diet)
"""

import json
import os
import platform
import re
import socket
from pathlib import Path

from flask import Flask, Response, jsonify

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "static"

app = Flask(__name__)


def human(nbytes):
    """1234567 -> '1.23 MB'"""
    try:
        n = float(nbytes)
    except (TypeError, ValueError):
        return None
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.2f} {unit}" if unit != "B" else f"{int(n)} B"
        n /= 1024
    return f"{n:.2f} GB"


def whoami():
    uid = os.getuid()
    try:
        import pwd

        name = pwd.getpwuid(uid).pw_name
    except Exception:  # pragma: no cover
        name = "unknown"
    return name, uid


def css():
    """ใช้ไฟล์ที่ถูก minify ใน builder stage ถ้ามี  ไม่มีก็ใช้ต้นฉบับ"""
    minified = STATIC_DIR / "style.min.css"
    raw = APP_DIR / "style.css"
    if minified.exists():
        return minified.read_text(encoding="utf-8"), "style.min.css (builder stage)"
    if raw.exists():
        return raw.read_text(encoding="utf-8"), "style.css (ต้นฉบับ ไม่ผ่าน build)"
    return "", "ไม่มีไฟล์ CSS"


def build_info():
    f = STATIC_DIR / "build_info.json"
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


UNITS = {"B": 1, "KB": 1024, "MB": 1024 ** 2, "GB": 1024 ** 3, "TB": 1024 ** 4}


def to_bytes(text):
    """รับค่าที่ได้จาก docker images (เช่น '1.62GB' หรือ '179MB') หรือเลขไบต์ล้วน"""
    text = (text or "").strip()
    if not text:
        return None
    m = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)\s*([KMGT]?B)?", text, flags=re.I)
    if not m:
        return None
    return int(float(m.group(1)) * UNITS.get((m.group(2) or "B").upper(), 1))


def sizes():
    """อ่านขนาด image ของแต่ละรุ่นจาก environment (ส่งเข้ามาตอน docker run)"""
    out = []
    for key, base in (
        ("SIZE_V1", "python:3.12"),
        ("SIZE_V2", "python:3.12-slim"),
        ("SIZE_V3", "python:3.12-slim (multi-stage)"),
    ):
        tag = key.replace("SIZE_", "").lower()
        raw = os.environ.get(key, "").strip()
        value = to_bytes(raw)
        out.append({"tag": tag, "base": base, "bytes": value,
                    "human": raw if value else None,
                    "rebuild": os.environ.get("REBUILD_" + tag.upper(), "").strip() or "—"})
    return out


def facts():
    user, uid = whoami()
    info = build_info()
    return {
        "image_tag": os.environ.get("IMAGE_TAG", "unknown"),
        "variant": os.environ.get("APP_VARIANT", "unknown"),
        "base_image": os.environ.get("BASE_IMAGE", "unknown"),
        "python": platform.python_version(),
        "user": user,
        "uid": uid,
        "is_root": uid == 0,
        "hostname": socket.gethostname(),
        "assets_built_at": info.get("built_at"),
        "css_raw_bytes": info.get("raw_bytes"),
        "css_min_bytes": info.get("min_bytes"),
    }


@app.get("/healthz")
def healthz():
    return jsonify(status="ok", variant=os.environ.get("APP_VARIANT", "unknown"))


@app.get("/facts")
def facts_json():
    return jsonify(facts=facts(), sizes=sizes())


@app.get("/")
def index():
    style, css_source = css()
    f = facts()
    rows = sizes()
    known = [r["bytes"] for r in rows if r["bytes"]]
    biggest = max(known) if known else 1

    bars = [
        '<div class="row chead"><div class="tag">รุ่น</div>'
        '<div class="base">base image</div>'
        '<div class="track"></div>'
        '<div class="num">ขนาดบนดิสก์</div>'
        '<div class="time">rebuild</div></div>'
    ]
    for r in rows:
        if not r["bytes"]:
            bars.append(
                f'<div class="row"><div class="tag">{r["tag"]}</div>'
                f'<div class="base">{r["base"]}</div>'
                f'<div class="track"><div class="bar unknown" style="width:6%"></div></div>'
                f'<div class="num">ไม่ได้ส่งค่ามา</div>'
                f'<div class="time">{r["rebuild"]}</div></div>'
            )
            continue
        pct = max(3.0, r["bytes"] / biggest * 100.0)
        cls = "fat" if r["tag"] == "v1" else ("mid" if r["tag"] == "v2" else "slim")
        saved = ""
        if r["tag"] != "v1" and rows[0]["bytes"]:
            saved = f' <span class="saved">−{100 - r["bytes"] / rows[0]["bytes"] * 100:.0f}%</span>'
        bars.append(
            f'<div class="row"><div class="tag">{r["tag"]}</div>'
            f'<div class="base">{r["base"]}</div>'
            f'<div class="track"><div class="bar {cls}" style="width:{pct:.1f}%"></div></div>'
            f'<div class="num">{r["human"]}{saved}</div>'
            f'<div class="time">{r["rebuild"]}</div></div>'
        )

    user_badge = (
        '<span class="badge bad">root — อันตราย</span>'
        if f["is_root"]
        else '<span class="badge good">non-root — ปลอดภัยกว่า</span>'
    )
    css_line = (
        f'{f["css_raw_bytes"]} B → {f["css_min_bytes"]} B'
        if f["css_min_bytes"]
        else "ไม่ผ่านขั้นตอน build asset"
    )
    built_at = f["assets_built_at"] or "—"

    html = f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>IMAGE DIET REPORT — {f["variant"]}</title>
<style>{style}</style></head>
<body>
<main>
  <header>
    <div class="logo">🥗</div>
    <div>
      <h1>IMAGE DIET REPORT</h1>
      <p class="sub">หน้าเว็บนี้ทำงานอยู่ใน image <code>{f["image_tag"]}</code></p>
    </div>
    <div class="stamp">{f["variant"].upper()}</div>
  </header>

  <section class="card">
    <h2>ขนาด image ของแต่ละรุ่น · เวลา rebuild หลังแก้โค้ด 1 บรรทัด</h2>
    <div class="chart">{''.join(bars)}</div>
    <p class="hint">ค่าเหล่านี้ไม่ได้ hard-code ไว้ในโค้ด แต่ส่งเข้ามาทาง environment variable ตอน
       <code>docker run</code> ด้วย <code>docker images --format '{{{{.Size}}}}'</code>
       จึงเป็นตัวเลขเดียวกับที่เห็นใน terminal เป๊ะ ๆ</p>
  </section>

  <section class="grid">
    <div class="card">
      <h2>ตัวตนของ container นี้</h2>
      <dl>
        <dt>base image</dt><dd><code>{f["base_image"]}</code></dd>
        <dt>python</dt><dd>{f["python"]}</dd>
        <dt>hostname</dt><dd><code>{f["hostname"]}</code></dd>
        <dt>รันด้วย user</dt><dd><code>{f["user"]}</code> (uid {f["uid"]}) {user_badge}</dd>
      </dl>
    </div>
    <div class="card">
      <h2>ของที่ได้จาก builder stage</h2>
      <dl>
        <dt>CSS</dt><dd>{css_line}</dd>
        <dt>ที่มาของ CSS</dt><dd>{css_source}</dd>
        <dt>build asset เมื่อ</dt><dd><code>{built_at}</code></dd>
      </dl>
      <p class="hint">ไฟล์ CSS ถูก minify ใน stage แรก (image ฐาน 1 GB)
         แล้ว <code>COPY --from=builder</code> เข้ามาเฉพาะผลลัพธ์</p>
    </div>
  </section>

  <footer>LAB 3 · 003_LAB_Image_Diet · <code>/healthz</code> · <code>/facts</code></footer>
</main>
</body></html>"""
    return Response(html, mimetype="text/html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("APP_PORT", "8080")))
