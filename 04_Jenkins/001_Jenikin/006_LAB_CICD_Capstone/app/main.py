import os
import socket
from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.responses import HTMLResponse


VERSION = "1.0.0"
THEME = "blue"

PALETTES = {
    "blue": {
        "primary": "#2563eb",
        "secondary": "#06b6d4",
        "glow": "#60a5fa",
        "surface": "rgba(15, 23, 42, 0.74)",
    },
    "green": {
        "primary": "#16a34a",
        "secondary": "#14b8a6",
        "glow": "#4ade80",
        "surface": "rgba(6, 38, 28, 0.76)",
    },
    "orange": {
        "primary": "#ea580c",
        "secondary": "#f59e0b",
        "glow": "#fb923c",
        "surface": "rgba(49, 24, 8, 0.76)",
    },
}

app = FastAPI(title="CI/CD Deploy Dashboard")
DEPLOYED_AT = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def app_info() -> dict[str, str]:
    return {
        "version": VERSION,
        "build_number": os.getenv("BUILD_NUMBER", "local"),
        "theme": THEME,
        "hostname": socket.gethostname(),
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/info")
def info() -> dict[str, str]:
    return app_info()


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    details = app_info()
    palette = PALETTES.get(THEME, PALETTES["blue"])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Deploy Dashboard · v{VERSION}</title>
  <style>
    * {{ box-sizing: border-box; }}
    :root {{ color-scheme: dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
    body {{
      margin: 0; min-height: 100vh; color: #f8fafc; overflow: hidden;
      background:
        radial-gradient(circle at 18% 18%, {palette['primary']}88 0, transparent 32%),
        radial-gradient(circle at 84% 76%, {palette['secondary']}66 0, transparent 36%),
        linear-gradient(135deg, #020617 0%, #0f172a 48%, #020617 100%);
    }}
    body::before {{
      content: ""; position: fixed; inset: 0; opacity: .18;
      background-image: linear-gradient(#fff 1px, transparent 1px), linear-gradient(90deg, #fff 1px, transparent 1px);
      background-size: 46px 46px; mask-image: linear-gradient(to bottom, #000, transparent 82%);
    }}
    main {{ position: relative; min-height: 100vh; display: grid; place-items: center; padding: 42px; }}
    .shell {{ width: min(1100px, 100%); }}
    .eyebrow {{ display: flex; align-items: center; gap: 12px; letter-spacing: .18em; text-transform: uppercase; color: #cbd5e1; font-size: 13px; }}
    .pulse {{ width: 11px; height: 11px; border-radius: 99px; background: {palette['glow']}; box-shadow: 0 0 0 0 {palette['glow']}99; animation: pulse 2s infinite; }}
    h1 {{ margin: 22px 0 6px; font-size: clamp(68px, 12vw, 148px); line-height: .9; letter-spacing: -.065em; text-shadow: 0 18px 70px {palette['primary']}88; }}
    .build {{ margin: 0 0 36px; font-size: clamp(24px, 4vw, 42px); font-weight: 650; color: {palette['glow']}; }}
    .grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }}
    .card {{ background: {palette['surface']}; border: 1px solid #ffffff22; border-radius: 22px; padding: 22px; box-shadow: 0 24px 80px #0007; backdrop-filter: blur(18px); }}
    .label {{ color: #94a3b8; font-size: 12px; letter-spacing: .14em; text-transform: uppercase; }}
    .value {{ margin-top: 9px; font-size: 18px; font-weight: 650; overflow-wrap: anywhere; }}
    footer {{ margin-top: 20px; color: #94a3b8; font-size: 13px; display: flex; justify-content: space-between; }}
    @keyframes pulse {{ 70% {{ box-shadow: 0 0 0 13px transparent; }} 100% {{ box-shadow: 0 0 0 0 transparent; }} }}
    @media (max-width: 760px) {{ main {{ padding: 24px; }} .grid {{ grid-template-columns: 1fr; }} body {{ overflow: auto; }} }}
  </style>
</head>
<body data-version="{VERSION}" data-build="{details['build_number']}" data-theme="{THEME}">
  <main>
    <section class="shell">
      <div class="eyebrow"><span class="pulse"></span> live deployment · auto-refresh 5s</div>
      <h1>v{VERSION}</h1>
      <p class="build">BUILD #{details['build_number']}</p>
      <div class="grid">
        <article class="card"><div class="label">Theme</div><div class="value">{THEME}</div></article>
        <article class="card"><div class="label">Container hostname</div><div class="value">{details['hostname']}</div></article>
        <article class="card"><div class="label">Deployed at</div><div class="value">{DEPLOYED_AT}</div></article>
      </div>
      <footer><span>Jenkins CI/CD Capstone</span><span id="sync">checking deployment…</span></footer>
    </section>
  </main>
  <script>
    const current = {{version: document.body.dataset.version, build_number: document.body.dataset.build, theme: document.body.dataset.theme}};
    async function refreshDeployment() {{
      const sync = document.getElementById('sync');
      try {{
        const response = await fetch('/api/info', {{cache: 'no-store'}});
        const next = await response.json();
        if (next.version !== current.version || next.build_number !== current.build_number || next.theme !== current.theme) {{
          location.reload();
          return;
        }}
        sync.textContent = 'deployment is current · ' + new Date().toLocaleTimeString();
      }} catch (_) {{ sync.textContent = 'waiting for deployment…'; }}
    }}
    refreshDeployment();
    setInterval(refreshDeployment, 5000);
  </script>
</body>
</html>"""
