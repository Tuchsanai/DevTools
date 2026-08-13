"""OPS CLINIC — คนไข้ตัวอย่างสำหรับฝึกวินิจฉัยอาการของ container

endpoint ที่มีให้:
  GET  /          หน้าเว็บสถานะ (auto refresh)
  GET  /healthz   200 = ok, 500 = sick   (HEALTHCHECK ใน Dockerfile เรียกอันนี้)
  POST /break     ทำให้ /healthz ตอบ 500 (จำลองอาการ "Up แต่ป่วย")
  POST /fix       กลับมาปกติ
  POST /leak      เริ่ม thread ที่กินแรมเรื่อย ๆ (ใช้ทดสอบ --memory / OOMKilled)
"""

import os
import socket
import threading
import time

from flask import Flask, jsonify, request, Response

app = Flask(__name__)

APP_NAME = os.environ.get("APP_NAME", "ops-clinic")
APP_PORT = int(os.environ.get("APP_PORT", "8080"))
STARTED = time.time()
STATE = {"healthy": True, "reason": "", "leaking": False, "leaked_mb": 0}
_BUCKET = []


def mem_limit_mb():
    """อ่าน memory limit ที่ cgroup ของ container กำหนดไว้ (หน่วย MB)"""
    try:
        with open("/sys/fs/cgroup/memory.max") as fh:
            raw = fh.read().strip()
        if raw == "max":
            return None
        return int(raw) // (1024 * 1024)
    except OSError:
        return None


def rss_mb():
    """แรมที่ process นี้ใช้อยู่จริง (RSS) หน่วย MB"""
    try:
        with open("/proc/self/statm") as fh:
            pages = int(fh.read().split()[1])
        return round(pages * os.sysconf("SC_PAGE_SIZE") / (1024 * 1024), 1)
    except OSError:
        return -1


def _leak_worker(chunk_mb, delay):
    while True:
        _BUCKET.append(b"x" * (chunk_mb * 1024 * 1024))
        STATE["leaked_mb"] += chunk_mb
        time.sleep(delay)


@app.get("/healthz")
def healthz():
    body = {
        "status": "ok" if STATE["healthy"] else "sick",
        "app": APP_NAME,
        "host": socket.gethostname(),
        "uptime_sec": round(time.time() - STARTED, 1),
        "rss_mb": rss_mb(),
    }
    if STATE["healthy"]:
        return jsonify(body), 200
    body["reason"] = STATE["reason"]
    return jsonify(body), 500


@app.post("/break")
def do_break():
    STATE["healthy"] = False
    STATE["reason"] = "database connection lost (simulated by POST /break)"
    return jsonify(ok=True, healthy=False, reason=STATE["reason"])


@app.post("/fix")
def do_fix():
    STATE["healthy"] = True
    STATE["reason"] = ""
    return jsonify(ok=True, healthy=True)


@app.post("/leak")
def do_leak():
    # ปรับความแรงได้ เช่น  /leak?mb=2&delay=1  = กินเพิ่มทีละ 2 MB ทุก 1 วินาที
    chunk_mb = int(request.args.get("mb", 8))
    delay = float(request.args.get("delay", 0.25))
    if not STATE["leaking"]:
        STATE["leaking"] = True
        threading.Thread(target=_leak_worker, args=(chunk_mb, delay), daemon=True).start()
    return jsonify(ok=True, leaking=True, chunk_mb=chunk_mb, delay_sec=delay,
                   limit_mb=mem_limit_mb(), rss_mb=rss_mb())


PAGE = """<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>OPS CLINIC</title>
<style>
 *{box-sizing:border-box;margin:0;padding:0}
 body{min-height:100vh;background:#0b1120;color:#e2e8f0;
      font-family:"DejaVu Sans",system-ui,sans-serif;
      display:flex;align-items:center;justify-content:center;padding:32px}
 .card{width:760px;background:#131c31;border:1px solid #24304d;border-radius:16px;
       padding:32px 36px;box-shadow:0 18px 50px rgba(0,0,0,.45)}
 .top{display:flex;align-items:center;justify-content:space-between;margin-bottom:22px}
 h1{font-size:26px;letter-spacing:2px;color:#7dd3fc}
 .sub{font-size:13px;color:#94a3b8;margin-top:4px}
 .pill{padding:9px 20px;border-radius:999px;font-size:15px;font-weight:700;letter-spacing:1px}
 .ok{background:#052e1a;color:#4ade80;border:1px solid #16a34a}
 .bad{background:#3b0d0d;color:#f87171;border:1px solid #dc2626}
 table{width:100%;border-collapse:collapse;margin-top:6px}
 td{padding:11px 8px;border-bottom:1px solid #1e293b;font-size:15px}
 td.k{color:#94a3b8;width:230px}
 td.v{color:#f1f5f9;font-family:"DejaVu Sans Mono",monospace}
 .bar{height:9px;background:#1e293b;border-radius:6px;overflow:hidden;margin-top:8px}
 .bar i{display:block;height:100%;background:linear-gradient(90deg,#38bdf8,#22d3ee)}
 .foot{margin-top:22px;font-size:12.5px;color:#64748b;line-height:1.9}
 code{background:#0b1120;border:1px solid #24304d;border-radius:5px;padding:1px 7px;color:#7dd3fc}
</style></head><body>
<div class="card">
  <div class="top">
    <div><h1>OPS CLINIC</h1><div class="sub">Week 9 &middot; LAB 5 &middot; container ที่หายดีแล้ว</div></div>
    <div id="pill" class="pill ok">HEALTHY</div>
  </div>
  <table>
    <tr><td class="k">APP_NAME</td><td class="v" id="app">-</td></tr>
    <tr><td class="k">hostname (container ID)</td><td class="v" id="host">-</td></tr>
    <tr><td class="k">/healthz</td><td class="v" id="code">-</td></tr>
    <tr><td class="k">uptime</td><td class="v" id="up">-</td></tr>
    <tr><td class="k">memory limit (cgroup)</td><td class="v" id="lim">-</td></tr>
    <tr><td class="k">memory used (RSS)</td><td class="v" id="rss">-</td>
    </tr>
  </table>
  <div class="bar"><i id="fill" style="width:0%"></i></div>
  <div class="foot">
    <code>POST /break</code> &rarr; /healthz ตอบ 500 &rarr; STATUS กลายเป็น <b>unhealthy</b><br>
    <code>POST /fix</code> &rarr; กลับมา healthy &nbsp;&middot;&nbsp;
    <code>POST /leak</code> &rarr; กินแรมจนโดน OOM kill (exit 137)
  </div>
</div>
<script>
const LIMIT = __LIMIT__;
document.getElementById('lim').textContent = LIMIT ? LIMIT + ' MB' : 'unlimited';
async function tick(){
  let r, j;
  try { r = await fetch('/healthz'); j = await r.json(); }
  catch(e){ return; }
  const ok = r.status === 200;
  const p = document.getElementById('pill');
  p.textContent = ok ? 'HEALTHY' : 'UNHEALTHY';
  p.className = 'pill ' + (ok ? 'ok' : 'bad');
  document.getElementById('app').textContent  = j.app;
  document.getElementById('host').textContent = j.host;
  document.getElementById('code').textContent = r.status + ' ' + j.status;
  document.getElementById('up').textContent   = j.uptime_sec + ' s';
  document.getElementById('rss').textContent  = j.rss_mb + ' MB';
  if (LIMIT) document.getElementById('fill').style.width =
      Math.min(100, j.rss_mb / LIMIT * 100) + '%';
}
tick(); setInterval(tick, 2000);
</script>
</body></html>"""


@app.get("/")
def index():
    limit = mem_limit_mb()
    html = PAGE.replace("__LIMIT__", str(limit) if limit else "null")
    return Response(html, mimetype="text/html")


if __name__ == "__main__":
    print(f"[{APP_NAME}] starting on 0.0.0.0:{APP_PORT} "
          f"(memory limit = {mem_limit_mb()} MB)", flush=True)
    app.run(host="0.0.0.0", port=APP_PORT)
