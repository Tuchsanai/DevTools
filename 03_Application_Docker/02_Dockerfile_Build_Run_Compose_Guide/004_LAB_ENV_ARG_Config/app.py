import html
import os
import platform
import socket
from datetime import datetime, timezone

from flask import Flask, jsonify


app = Flask(__name__)

# These values intentionally match the ENV instructions in Dockerfile.
IMAGE_DEFAULTS = {
    "APP_ENV": "development",
    "APP_VERSION": "1.0.0",
    "GREETING": "Hello",
    "FEATURE_FLAGS": "beta-ui",
    "LOG_LEVEL": "info",
}

APP_FALLBACKS = {
    "APP_ENV": "development",
    "APP_VERSION": "dev",
    "FEATURE_FLAGS": "",
    "GREETING": "Hello",
}

VARIABLES = (
    "APP_ENV",
    "APP_VERSION",
    "FEATURE_FLAGS",
    "GREETING",
    "LOG_LEVEL",
    "DATABASE_HOST",
    "BUILD_TOOL",
    "FAKE_TOKEN",
)

THEMES = {
    "development": ("#3b82f6", "#8b5cf6"),
    "staging": ("#f59e0b", "#f97316"),
    "production": ("#10b981", "#064e3b"),
}


def read_config():
    return {
        name: os.environ.get(name, APP_FALLBACKS.get(name, ""))
        for name in VARIABLES
    }


def value_source(name, value):
    if name not in os.environ:
        return "(ไม่ได้ตั้งค่า)"
    if name in IMAGE_DEFAULTS and value == IMAGE_DEFAULTS[name]:
        return "ENV ใน Dockerfile (ค่า default)"
    return "ถูกทับจากภายนอก (--env-file / -e)"


@app.get("/")
def index():
    config = read_config()
    app_env = config["APP_ENV"]
    primary, secondary = THEMES.get(app_env.lower(), THEMES["development"])

    rows = "".join(
        "<tr>"
        f"<td><code>{html.escape(name)}</code></td>"
        f"<td>{html.escape(value) if value else '<span class=\"muted\">(ว่าง)</span>'}</td>"
        f"<td>{html.escape(value_source(name, value))}</td>"
        "</tr>"
        for name, value in config.items()
    )

    flags = [flag.strip() for flag in config["FEATURE_FLAGS"].split(",") if flag.strip()]
    flag_chips = "".join(
        f'<span class="chip">{html.escape(flag)}</span>' for flag in flags
    ) or '<span class="muted">ไม่มี feature flag</span>'

    safe_env = html.escape(app_env)
    safe_version = html.escape(config["APP_VERSION"])
    safe_greeting = html.escape(config["GREETING"])
    hostname = html.escape(socket.gethostname())
    now = html.escape(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
    python_version = html.escape(platform.python_version())

    return f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Configuration Console</title>
  <style>
    :root {{ --primary: {primary}; --secondary: {secondary}; }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; min-height: 100vh; color: #f8fafc;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background:
        radial-gradient(circle at 10% 10%, color-mix(in srgb, var(--primary) 55%, transparent), transparent 35%),
        radial-gradient(circle at 90% 15%, color-mix(in srgb, var(--secondary) 50%, transparent), transparent 32%),
        linear-gradient(145deg, #0f172a, #111827 52%, #020617);
      padding: 48px 20px;
    }}
    .shell {{ width: min(1120px, 100%); margin: 0 auto; position: relative; }}
    .hero {{ margin-bottom: 28px; }}
    h1 {{ font-size: clamp(2rem, 5vw, 3.7rem); margin: 0 0 8px; letter-spacing: -0.04em; }}
    .subtitle {{ color: #cbd5e1; margin: 0; font-size: 1.05rem; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 18px; }}
    .card {{
      position: relative; overflow: hidden; padding: 24px; border-radius: 22px;
      background: rgba(15, 23, 42, 0.66); backdrop-filter: blur(18px);
      border: 1px solid rgba(255,255,255,.14);
      box-shadow: 0 18px 50px rgba(0,0,0,.28);
    }}
    .wide {{ grid-column: 1 / -1; }}
    .label {{ text-transform: uppercase; letter-spacing: .14em; color: #94a3b8; font-size: .75rem; font-weight: 700; }}
    .version {{ font-size: clamp(2.4rem, 7vw, 4.7rem); font-weight: 800; line-height: 1; margin: 16px 0 6px; word-break: break-word; }}
    .env-badge {{
      display: inline-flex; margin-top: 18px; padding: 10px 18px; border-radius: 999px;
      background: linear-gradient(120deg, var(--primary), var(--secondary));
      font-size: 1.35rem; font-weight: 800; box-shadow: 0 8px 28px color-mix(in srgb, var(--primary) 40%, transparent);
    }}
    .ribbon {{
      position: absolute; right: -53px; top: 24px; width: 200px; padding: 7px 0;
      transform: rotate(42deg); text-align: center; text-transform: uppercase;
      font-size: .7rem; font-weight: 800; letter-spacing: .12em;
      background: linear-gradient(90deg, var(--primary), var(--secondary));
    }}
    .chips {{ display: flex; flex-wrap: wrap; gap: 9px; margin-top: 16px; }}
    .chip {{ padding: 7px 12px; border-radius: 999px; background: color-mix(in srgb, var(--primary) 28%, #1e293b); border: 1px solid color-mix(in srgb, var(--primary) 60%, transparent); }}
    .details {{ display: grid; gap: 13px; margin-top: 16px; }}
    .runtime {{ grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 13px 28px; }}
    .detail {{ display: flex; justify-content: space-between; gap: 18px; border-bottom: 1px solid rgba(255,255,255,.08); padding-bottom: 10px; }}
    .detail span:last-child {{ text-align: right; overflow-wrap: anywhere; }}
    .table-wrap {{ overflow-x: auto; margin-top: 16px; }}
    table {{ width: 100%; border-collapse: collapse; min-width: 650px; }}
    th, td {{ padding: 13px 14px; text-align: left; border-bottom: 1px solid rgba(255,255,255,.09); }}
    th {{ color: #cbd5e1; font-size: .82rem; }}
    td {{ overflow-wrap: anywhere; }}
    code {{ color: #bfdbfe; font-size: .9rem; }}
    .muted {{ color: #94a3b8; }}
    .greeting {{ margin: 13px 0 0; color: #e2e8f0; font-size: 1.1rem; }}
    @media (max-width: 600px) {{ body {{ padding: 28px 14px; }} .card {{ padding: 19px; }} .ribbon {{ right: -66px; }} }}
  </style>
</head>
<body>
  <main class="shell">
    <header class="hero">
      <h1>Configuration Console</h1>
      <p class="subtitle">Docker image เดียวสามารถตั้งค่าและรันได้ในหลายสภาพแวดล้อม</p>
    </header>
    <section class="grid">
      <article class="card">
        <div class="ribbon">{safe_env}</div>
        <div class="label">Environment</div>
        <div class="env-badge">{safe_env}</div>
        <p class="greeting">{safe_greeting}</p>
      </article>
      <article class="card">
        <div class="label">App version</div>
        <div class="version">{safe_version}</div>
      </article>
      <article class="card">
        <div class="label">Feature flags</div>
        <div class="chips">{flag_chips}</div>
      </article>
      <article class="card wide">
        <div class="label">Runtime</div>
        <div class="details runtime">
          <div class="detail"><span>Hostname</span><span>{hostname}</span></div>
          <div class="detail"><span>เวลาปัจจุบัน</span><span>{now}</span></div>
          <div class="detail"><span>Python</span><span>{python_version}</span></div>
        </div>
      </article>
      <article class="card wide">
        <div class="label">Environment variables</div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>ตัวแปร</th><th>ค่าที่อ่านได้</th><th>มาจากไหน</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </div>
      </article>
    </section>
  </main>
</body>
</html>"""


@app.get("/healthz")
def healthz():
    config = read_config()
    return jsonify(
        status="ok",
        app_env=config["APP_ENV"],
        app_version=config["APP_VERSION"],
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8184)
