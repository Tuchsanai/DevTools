import html
import os
import socket

import flask
import matplotlib
import pandas
import requests
from flask import Flask, jsonify


app = Flask(__name__)


@app.route("/")
def index():
    details = {
        "BUILD_ID": os.environ.get("BUILD_ID", "dev"),
        "Flask": flask.__version__,
        "pandas": pandas.__version__,
        "requests": requests.__version__,
        "matplotlib": matplotlib.__version__,
        "Hostname": socket.gethostname(),
    }
    cards = "".join(
        f"""
        <div class="card">
          <span>{html.escape(label)}</span>
          <strong>{html.escape(value)}</strong>
        </div>
        """
        for label, value in details.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Layer Cache Lab</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      min-height: 100vh;
      margin: 0;
      display: grid;
      place-items: center;
      padding: 24px;
      color: #f8fafc;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: linear-gradient(135deg, #172554 0%, #4c1d95 48%, #0f766e 100%);
    }}
    main {{
      width: min(760px, 100%);
      padding: clamp(24px, 5vw, 48px);
      border: 1px solid rgba(255, 255, 255, .24);
      border-radius: 28px;
      background: rgba(255, 255, 255, .12);
      box-shadow: 0 24px 70px rgba(2, 6, 23, .35);
      backdrop-filter: blur(18px);
      -webkit-backdrop-filter: blur(18px);
    }}
    .eyebrow {{
      margin: 0 0 8px;
      color: #a5f3fc;
      font-size: .78rem;
      font-weight: 700;
      letter-spacing: .16em;
      text-transform: uppercase;
    }}
    h1 {{ margin: 0 0 10px; font-size: clamp(2rem, 7vw, 4rem); line-height: 1; }}
    .intro {{ margin: 0 0 30px; color: #dbeafe; line-height: 1.65; }}
    .grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14px; }}
    .card {{
      min-width: 0;
      padding: 18px;
      border: 1px solid rgba(255, 255, 255, .16);
      border-radius: 18px;
      background: rgba(15, 23, 42, .24);
    }}
    .card span {{ display: block; margin-bottom: 7px; color: #bae6fd; font-size: .78rem; }}
    .card strong {{ display: block; overflow-wrap: anywhere; font-size: 1.05rem; }}
    @media (max-width: 560px) {{
      body {{ padding: 14px; }}
      main {{ border-radius: 22px; }}
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <p class="eyebrow">Docker learning lab</p>
    <h1>Layer Cache Lab</h1>
    <p class="intro">Inspect the build metadata and dependency versions running inside this container.</p>
    <section class="grid">{cards}</section>
  </main>
</body>
</html>"""


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8182)

# APP_VERSION = 1
