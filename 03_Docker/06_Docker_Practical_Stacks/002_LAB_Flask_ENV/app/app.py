import os
import re
from flask import Flask, jsonify, request


app = Flask(__name__)


def setting(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def app_color() -> str:
    value = setting("APP_COLOR", "#1971c2")
    return value if re.fullmatch(r"#[0-9a-fA-F]{6}", value) else "#1971c2"


@app.get("/")
def index():
    name = setting("APP_NAME", "Flask ENV Demo")
    color = app_color()
    instance = setting("APP_INSTANCE", "default")
    return f"""<!doctype html>
<html lang=\"th\">
<head>
  <meta charset=\"utf-8\">
  <meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
  <title>{name}</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; display: grid; place-items: center;
      font-family: \"Noto Sans Thai\", \"Leelawadee UI\", system-ui, sans-serif;
      color: white; background: {color}; }}
    main {{ width: min(850px, 90vw); padding: 4rem; border-radius: 28px;
      background: rgba(0,0,0,.22); box-shadow: 0 24px 70px rgba(0,0,0,.25); }}
    .tag {{ display: inline-block; padding: .45rem .8rem; border: 1px solid rgba(255,255,255,.5);
      border-radius: 999px; letter-spacing: .11em; text-transform: uppercase; font-weight: 800; }}
    h1 {{ font-size: clamp(3rem, 8vw, 6.5rem); line-height: 1; margin: 1.2rem 0; }}
    p {{ font-size: 1.25rem; line-height: 1.65; opacity: .92; }}
    code {{ background: rgba(0,0,0,.22); padding: .18rem .45rem; border-radius: .35rem; }}
  </style>
</head>
<body data-instance=\"{instance}\" data-color=\"{color}\">
  <main>
    <div class=\"tag\">LAB 2 · instance {instance}</div>
    <h1>{name}</h1>
    <p>ทั้งสามกล่องสร้างจาก image เดียวกัน แต่หน้าเว็บต่างกันเพราะ
      <code>APP_COLOR={color}</code> และ environment variables ของแต่ละ container</p>
  </main>
</body>
</html>"""


@app.get("/health")
def health():
    return jsonify(
        status="ok",
        instance=setting("APP_INSTANCE", "default"),
        color=app_color(),
        request_host=request.host,
    )
