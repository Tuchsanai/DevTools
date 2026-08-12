import os
import socket

import redis
from flask import Flask, redirect, request

app = Flask(__name__)

r = redis.Redis(
    host=os.environ.get("REDIS_HOST", "redis"),
    port=6379,
    decode_responses=True,
)

PAGE = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>Cats vs Dogs — Vote</title>
<style>
  body {{
    margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #0b2545 0%, #134074 55%, #1864ab 100%);
    font-family: "Leelawadee UI", "Noto Sans Thai", "Segoe UI", sans-serif;
  }}
  .card {{
    background: #fff; border-radius: 20px; padding: 42px 56px; text-align: center;
    box-shadow: 0 24px 70px rgba(0,0,0,.45);
  }}
  h1 {{ font-size: 32px; color: #16212f; margin: 0 0 6px; }}
  p.sub {{ color: #5b6b7f; margin: 0 0 28px; font-size: 17px; }}
  form {{ display: flex; gap: 20px; justify-content: center; }}
  button {{
    font-size: 26px; font-weight: 700; border: 0; border-radius: 16px;
    padding: 26px 44px; cursor: pointer; color: #fff; font-family: inherit;
    transition: transform .1s;
  }}
  button:hover {{ transform: scale(1.05); }}
  .cats {{ background: linear-gradient(135deg, #e8590c, #f76707); }}
  .dogs {{ background: linear-gradient(135deg, #1971c2, #22b8cf); }}
  .thanks {{ font-size: 19px; color: #2f9e44; font-weight: 700; margin: 22px 0 0; min-height: 26px; }}
  .host {{ margin-top: 18px; font-size: 14px; color: #68778a; }}
  .host b {{ font-family: Consolas, monospace; }}
</style>
</head>
<body>
  <div class="card">
    <h1>Cats 🐱 vs Dogs 🐶</h1>
    <p class="sub">โหวตทีมโปรดของคุณ — เปลี่ยนใจโหวตใหม่ได้เสมอ</p>
    <form method="POST">
      <button class="cats" name="vote" value="cats">CATS 🐱</button>
      <button class="dogs" name="vote" value="dogs">DOGS 🐶</button>
    </form>
    <p class="thanks">{thanks}</p>
    <p class="host">processed by container <b>{hostname}</b></p>
  </div>
</body>
</html>"""


@app.route("/", methods=["GET", "POST"])
def vote():
    thanks = ""
    if request.method == "POST":
        team = request.form.get("vote")
        if team in ("cats", "dogs"):
            r.incr(f"votes:{team}")
            thanks = f"บันทึกคะแนนให้ทีม {team.upper()} แล้ว ✅"
    return PAGE.format(thanks=thanks, hostname=socket.gethostname())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
