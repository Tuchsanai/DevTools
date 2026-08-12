"""Vision UI — หน้าเว็บอัปโหลดรูป แล้วส่งไปให้ backend ตรวจจับขอบ

ใช้แค่ flask + requests เท่านั้น (ไม่มี opencv/numpy) เพื่อให้ image ของ frontend เล็ก
งานหนักทั้งหมดอยู่ที่ service `backend`
"""

import base64
import os

import requests
from flask import Flask, render_template_string, request

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")
APP_TITLE = os.environ.get("APP_TITLE", "Vision API")
SAMPLE_PATH = os.path.join(os.path.dirname(__file__), "static", "sample.jpg")

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{ title }}</title>
<style>
  * { box-sizing: border-box; }
  body { margin:0; font-family: "Segoe UI", "Noto Sans Thai", system-ui, sans-serif;
         background:#0b1020; color:#e6ecff; }
  .wrap { max-width: 1120px; margin: 0 auto; padding: 28px 24px 48px; }
  header { display:flex; align-items:center; gap:14px; margin-bottom:6px; }
  .logo { width:42px; height:42px; border-radius:12px; background:linear-gradient(135deg,#38bdf8,#818cf8);
          display:flex; align-items:center; justify-content:center; font-size:22px; }
  h1 { font-size:26px; margin:0; letter-spacing:.3px; }
  .sub { color:#93a4c8; font-size:14px; margin:2px 0 22px 56px; }
  .card { background:#141b33; border:1px solid #24304f; border-radius:16px; padding:20px 22px; }
  form { display:flex; flex-wrap:wrap; gap:14px; align-items:flex-end; }
  label { display:block; font-size:12px; color:#93a4c8; margin-bottom:6px; }
  input[type=text], input[type=file] { background:#0b1020; color:#e6ecff; border:1px solid #2c3a5e;
        border-radius:10px; padding:10px 12px; font-size:14px; min-width:190px; }
  button { background:linear-gradient(135deg,#38bdf8,#6366f1); color:#08122b; font-weight:700;
        border:0; border-radius:10px; padding:12px 20px; font-size:14px; cursor:pointer; }
  button.ghost { background:#1d2745; color:#c9d6f5; font-weight:600; border:1px solid #2c3a5e; }
  .meta { display:flex; flex-wrap:wrap; gap:10px; margin:18px 0 0; }
  .chip { background:#101833; border:1px solid #24304f; border-radius:999px;
          padding:6px 14px; font-size:12.5px; color:#a9bce6; }
  .chip b { color:#7dd3fc; font-weight:700; }
  .grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; margin-top:20px; }
  .panel { background:#141b33; border:1px solid #24304f; border-radius:16px; overflow:hidden; }
  .panel h2 { margin:0; padding:12px 16px; font-size:14px; letter-spacing:.6px; text-transform:uppercase;
              color:#0b1020; background:linear-gradient(90deg,#38bdf8,#818cf8); }
  .panel.edges h2 { background:linear-gradient(90deg,#facc15,#fb923c); }
  .panel img { display:block; width:100%; height:auto; background:#000; }
  .err { margin-top:18px; background:#3b1220; border:1px solid #7f1d3a; color:#ffb4c8;
         border-radius:12px; padding:14px 16px; font-size:14px; }
  footer { margin-top:26px; color:#6d7fa6; font-size:12px; }
  code { color:#7dd3fc; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="logo">🛰️</div>
    <h1>{{ title }}</h1>
  </header>
  <div class="sub">frontend (Flask) → HTTP → backend (FastAPI + OpenCV Canny)</div>

  <div class="card">
    <form method="post" enctype="multipart/form-data">
      <div>
        <label>ชื่อ</label>
        <input type="text" name="name" value="{{ name }}" placeholder="Somchai">
      </div>
      <div>
        <label>นามสกุล</label>
        <input type="text" name="surname" value="{{ surname }}" placeholder="Jaidee">
      </div>
      <div>
        <label>เลือกไฟล์รูป (jpg / png)</label>
        <input type="file" name="image" accept="image/*">
      </div>
      <button type="submit">ตรวจจับขอบ</button>
      <button type="submit" class="ghost" name="use_sample" value="1">ใช้รูปตัวอย่าง</button>
    </form>

    <div class="meta">
      <span class="chip">BACKEND_URL = <b>{{ backend_url }}</b></span>
      <span class="chip">backend = <b>{{ health.status }}</b></span>
      <span class="chip">Canny threshold = <b>{{ health.canny_low }} / {{ health.canny_high }}</b></span>
      <span class="chip">OpenCV = <b>{{ health.cv2 }}</b></span>
    </div>
  </div>

  {% if error %}<div class="err">⚠️ {{ error }}</div>{% endif %}

  {% if edges %}
  <div class="meta">
    <span class="chip">name = <b>{{ result.name }}</b></span>
    <span class="chip">surname = <b>{{ result.surname }}</b></span>
    <span class="chip">numbers = <b>{{ result.numbers }}</b></span>
    <span class="chip">ไฟล์ = <b>{{ filename }}</b></span>
  </div>
  <div class="grid">
    <div class="panel"><h2>Original</h2><img src="{{ original }}" alt="original"></div>
    <div class="panel edges"><h2>Edges — cv2.Canny</h2><img src="{{ edges }}" alt="edges"></div>
  </div>
  {% endif %}

  <footer>LAB 4 · 004_LAB_Vision_API_Compose · frontend เรียก backend ด้วย <code>{{ backend_url }}</code>
  (ชื่อ service ไม่ใช่ IP)</footer>
</div>
</body>
</html>
"""


def backend_health():
    try:
        r = requests.get(f"{BACKEND_URL}/healthz", timeout=3)
        return r.json()
    except Exception as exc:  # backend ยังไม่ขึ้น / ชื่อ service ผิด
        return {"status": f"unreachable ({exc.__class__.__name__})",
                "canny_low": "-", "canny_high": "-", "cv2": "-"}


@app.route("/", methods=["GET", "POST"])
def index():
    ctx = {
        "title": APP_TITLE,
        "backend_url": BACKEND_URL,
        "health": backend_health(),
        "name": request.form.get("name", "") if request.method == "POST" else "",
        "surname": request.form.get("surname", "") if request.method == "POST" else "",
        "original": None, "edges": None, "error": None, "result": {}, "filename": "",
    }

    if request.method != "POST":
        return render_template_string(PAGE, **ctx)

    upload = request.files.get("image")
    if upload and upload.filename:
        raw = upload.read()
        ctx["filename"] = upload.filename
    elif request.form.get("use_sample"):
        with open(SAMPLE_PATH, "rb") as fh:
            raw = fh.read()
        ctx["filename"] = "sample.jpg"
    else:
        ctx["error"] = "ยังไม่ได้เลือกไฟล์ — กด 'ใช้รูปตัวอย่าง' ก็ได้"
        return render_template_string(PAGE, **ctx)

    data_url = "data:image/jpeg;base64," + base64.b64encode(raw).decode()
    payload = {
        "image": data_url,
        "name": ctx["name"] or "student",
        "surname": ctx["surname"] or "docker",
        "numbers": [1, 2, 3],
    }

    try:
        resp = requests.post(f"{BACKEND_URL}/process-image", json=payload, timeout=30)
    except Exception as exc:
        ctx["error"] = f"เรียก backend ไม่สำเร็จ: {exc}"
        return render_template_string(PAGE, **ctx)

    if resp.status_code != 200:
        ctx["error"] = f"backend ตอบ HTTP {resp.status_code}: {resp.text[:200]}"
        return render_template_string(PAGE, **ctx)

    data = resp.json()
    ctx["result"] = data
    ctx["original"] = data_url
    ctx["edges"] = data["processed_image"]
    return render_template_string(PAGE, **ctx)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "backend_url": BACKEND_URL}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("APP_PORT", "8501")))
