import html
import os
import platform
import socket
import threading
import time
from datetime import datetime, timezone
from importlib.metadata import version

from flask import Flask, jsonify


# สร้าง Flask application และเก็บสถานะของ process
app = Flask(__name__)
START_TIME = time.monotonic()
REQUEST_LOCK = threading.Lock()
REQUEST_COUNT = 0


# Dockerfile จริงที่ใช้สร้าง image สำหรับแสดงบนหน้าเว็บ
DOCKERFILE_SOURCE = """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
ENV APP_VERSION=1.0
EXPOSE 5000
CMD [\"python\", \"app.py\"]"""


# อ่านข้อมูล runtime จริงทุกครั้งที่มี request
def runtime_info():
    return {
        "hostname": socket.gethostname(),
        "app_version": os.environ.get("APP_VERSION", "unset"),
        "python": platform.python_version(),
        "flask": version("flask"),
        "uptime_seconds": int(time.monotonic() - START_TIME),
    }


# หน้า dashboard หลักพร้อมตัวนับ request แบบ thread-safe
@app.route("/")
def dashboard():
    global REQUEST_COUNT
    with REQUEST_LOCK:
        REQUEST_COUNT += 1
        requests = REQUEST_COUNT

    info = runtime_info()
    current_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    values = {
        "hostname": html.escape(info["hostname"]),
        "app_version": html.escape(info["app_version"]),
        "python": html.escape(info["python"]),
        "flask": html.escape(info["flask"]),
        "current_utc": current_utc,
        "requests": requests,
        "uptime_seconds": info["uptime_seconds"],
        "dockerfile": html.escape(DOCKERFILE_SOURCE),
    }

    page = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dockerfile Lab</title>
  <style>
    :root {
      --bg-start: #eff6ff;
      --bg-mid: #eef2ff;
      --bg-end: #faf5ff;
      --orb-one: rgba(37, 99, 235, 0.22);
      --orb-two: rgba(124, 58, 237, 0.18);
      --surface: rgba(255, 255, 255, 0.66);
      --surface-strong: rgba(255, 255, 255, 0.82);
      --border: rgba(255, 255, 255, 0.78);
      --border-soft: rgba(99, 102, 241, 0.14);
      --text: #172033;
      --muted: #63708a;
      --accent: #4f46e5;
      --accent-soft: rgba(79, 70, 229, 0.1);
      --success: #16a34a;
      --success-ring: rgba(34, 197, 94, 0.3);
      --code-bg: #111827;
      --code-text: #dbeafe;
      --shadow: 0 24px 70px rgba(56, 70, 110, 0.16);
    }

    @media (prefers-color-scheme: dark) {
      :root {
        --bg-start: #07111f;
        --bg-mid: #11162b;
        --bg-end: #171025;
        --orb-one: rgba(59, 130, 246, 0.24);
        --orb-two: rgba(168, 85, 247, 0.2);
        --surface: rgba(17, 24, 39, 0.64);
        --surface-strong: rgba(24, 32, 52, 0.84);
        --border: rgba(255, 255, 255, 0.12);
        --border-soft: rgba(165, 180, 252, 0.14);
        --text: #f1f5f9;
        --muted: #aab6ca;
        --accent: #a5b4fc;
        --accent-soft: rgba(129, 140, 248, 0.14);
        --success: #4ade80;
        --success-ring: rgba(74, 222, 128, 0.3);
        --code-bg: #070b14;
        --code-text: #dbeafe;
        --shadow: 0 26px 80px rgba(0, 0, 0, 0.4);
      }
    }

    * { box-sizing: border-box; }

    body {
      min-height: 100vh;
      margin: 0;
      color: var(--text);
      font-family: -apple-system, "Segoe UI", system-ui, sans-serif;
      background:
        radial-gradient(circle at 12% 15%, var(--orb-one), transparent 34rem),
        radial-gradient(circle at 88% 86%, var(--orb-two), transparent 32rem),
        linear-gradient(135deg, var(--bg-start), var(--bg-mid) 52%, var(--bg-end));
    }

    .shell {
      width: min(1120px, calc(100% - 32px));
      margin: 0 auto;
      padding: 64px 0;
    }

    .glass {
      background: var(--surface);
      border: 1px solid var(--border);
      box-shadow: var(--shadow);
      backdrop-filter: blur(22px);
      -webkit-backdrop-filter: blur(22px);
    }

    .hero {
      position: relative;
      overflow: hidden;
      padding: clamp(28px, 5vw, 52px);
      border-radius: 28px;
    }

    .hero::after {
      content: "";
      position: absolute;
      width: 220px;
      height: 220px;
      right: -85px;
      top: -110px;
      border-radius: 50%;
      background: var(--accent-soft);
    }

    .badge {
      display: inline-flex;
      align-items: center;
      gap: 9px;
      padding: 8px 13px;
      color: var(--success);
      background: var(--surface-strong);
      border: 1px solid var(--border-soft);
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      text-transform: uppercase;
    }

    .pulse {
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: var(--success);
      box-shadow: 0 0 0 0 var(--success-ring);
      animation: pulse 1.8s infinite;
    }

    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 var(--success-ring); }
      70% { box-shadow: 0 0 0 9px transparent; }
      100% { box-shadow: 0 0 0 0 transparent; }
    }

    h1 {
      margin: 24px 0 10px;
      font-size: clamp(2.2rem, 7vw, 4.6rem);
      line-height: 0.98;
      letter-spacing: -0.055em;
    }

    .subtitle {
      max-width: 640px;
      margin: 0;
      color: var(--muted);
      font-size: clamp(1rem, 2.4vw, 1.18rem);
      line-height: 1.7;
    }

    .stats {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 16px;
      margin: 22px 0;
    }

    .stat {
      min-width: 0;
      padding: 22px;
      border-radius: 20px;
    }

    /* การ์ดใบสุดท้ายกินเต็มแถว เพื่อไม่ให้เหลือช่องว่างข้างขวา */
    .stats .stat:last-child { grid-column: 1 / -1; }

    .label {
      margin-bottom: 9px;
      color: var(--muted);
      font-size: 0.76rem;
      font-weight: 700;
      letter-spacing: 0.09em;
      text-transform: uppercase;
    }

    .value {
      overflow-wrap: anywhere;
      font-size: 1.08rem;
      font-weight: 720;
      font-variant-numeric: tabular-nums;
    }

    .code-panel {
      padding: 26px;
      border-radius: 24px;
    }

    .code-heading {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;
    }

    .code-heading h2 { margin: 0; font-size: 1.08rem; }
    .code-heading span { color: var(--muted); font-size: 0.8rem; }

    pre {
      overflow-x: auto;
      margin: 0;
      padding: 22px;
      color: var(--code-text);
      background: var(--code-bg);
      border: 1px solid var(--border-soft);
      border-radius: 16px;
      line-height: 1.72;
      tab-size: 2;
    }

    code { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }

    @media (max-width: 760px) {
      .shell { width: min(100% - 20px, 1120px); padding: 22px 0; }
      .hero { border-radius: 22px; }
      .stats { grid-template-columns: 1fr; }
      .code-panel { padding: 18px; border-radius: 20px; }
      .code-heading { align-items: flex-start; flex-direction: column; gap: 5px; }
      pre { padding: 17px; font-size: 0.76rem; }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero glass">
      <div class="badge"><span class="pulse"></span>served from container</div>
      <h1>Dockerfile Lab</h1>
      <p class="subtitle">Built from an 8-line Dockerfile. Every value below is read live from inside this running container &mdash; nothing here is hard-coded.</p>
    </section>

    <section class="stats" aria-label="Container runtime statistics">
      <article class="stat glass"><div class="label">Hostname · Container ID</div><div class="value">%(hostname)s</div></article>
      <article class="stat glass"><div class="label">App version</div><div class="value">%(app_version)s</div></article>
      <article class="stat glass"><div class="label">Python</div><div class="value">%(python)s</div></article>
      <article class="stat glass"><div class="label">Flask</div><div class="value">%(flask)s</div></article>
      <article class="stat glass"><div class="label">Current time</div><div class="value">%(current_utc)s</div></article>
      <article class="stat glass"><div class="label">Requests served</div><div class="value">%(requests)s</div></article>
      <article class="stat glass"><div class="label">Process uptime</div><div class="value">%(uptime_seconds)s seconds</div></article>
    </section>

    <section class="code-panel glass">
      <div class="code-heading"><h2>Dockerfile</h2><span>8 lines · Python 3.12 slim</span></div>
      <pre><code>%(dockerfile)s</code></pre>
    </section>
  </main>
</body>
</html>"""
    for key, value in values.items():
        page = page.replace("%(" + key + ")s", str(value))
    return page


# health endpoint สำหรับตรวจสถานะจากภายนอก container
@app.route("/health")
def health():
    info = runtime_info()
    with REQUEST_LOCK:
        requests = REQUEST_COUNT
    return jsonify(
        status="ok",
        hostname=info["hostname"],
        app_version=info["app_version"],
        python=info["python"],
        flask=info["flask"],
        requests=requests,
        uptime_seconds=info["uptime_seconds"],
    )


# เปิด web server ให้เข้าถึงได้จากภายนอก container
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
