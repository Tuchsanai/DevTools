import os
import socket
import sys

from flask import Flask

app = Flask(__name__)

# ── ลองแก้ข้อความบรรทัดล่างนี้ แล้ว build image ใหม่ เพื่อดู layer cache ทำงาน ──
MESSAGE = "สวัสดีจาก Container! 🐳"

PAGE = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<title>My First Docker App</title>
<style>
  body {{
    margin: 0; min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #0b2545 0%, #134074 55%, #1864ab 100%);
    font-family: "Leelawadee UI", "Noto Sans Thai", "Segoe UI", sans-serif; color: #16212f;
  }}
  .card {{
    background: #fff; border-radius: 20px; padding: 48px 64px; text-align: center;
    box-shadow: 0 24px 70px rgba(0,0,0,.45); max-width: 640px;
  }}
  .whale {{ font-size: 84px; line-height: 1; }}
  h1 {{ font-size: 34px; margin: 18px 0 6px; color: #1864ab; }}
  p.sub {{ color: #5b6b7f; font-size: 18px; margin: 0 0 26px; }}
  .row {{ display: flex; gap: 14px; justify-content: center; flex-wrap: wrap; }}
  .chip {{
    background: #e7f5ff; border: 2px solid #1971c2; color: #1864ab;
    border-radius: 999px; padding: 10px 22px; font-size: 17px; font-weight: 700;
  }}
  .chip.orange {{ background: #fff4e6; border-color: #e8590c; color: #e8590c; }}
  .chip.green  {{ background: #ebfbee; border-color: #2f9e44; color: #2f9e44; }}
  .chip b {{ font-family: Consolas, monospace; }}
</style>
</head>
<body>
  <div class="card">
    <div class="whale">🐳</div>
    <h1>{message}</h1>
    <p class="sub">หน้าเว็บนี้ถูกเสิร์ฟจาก Docker image ที่คุณ build เอง</p>
    <div class="row">
      <span class="chip">Container ID&nbsp;<b>{hostname}</b></span>
      <span class="chip orange">เวอร์ชัน&nbsp;<b>{version}</b></span>
      <span class="chip green">Python&nbsp;<b>{py}</b></span>
    </div>
  </div>
</body>
</html>"""


@app.route("/")
def home():
    return PAGE.format(
        message=MESSAGE,
        hostname=socket.gethostname(),
        version=os.environ.get("APP_VERSION", "dev"),
        py="%d.%d.%d" % sys.version_info[:3],
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
