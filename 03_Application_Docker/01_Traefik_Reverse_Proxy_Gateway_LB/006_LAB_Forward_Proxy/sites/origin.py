"""เว็บไซต์จำลอง "ฝั่งอินเทอร์เน็ต" ของ LAB 6 — Python standard library ล้วน

ไซต์เดียวกันนี้ถูกใช้สามบทบาทในแล็บ โดยเปลี่ยนแค่ environment variable
    site-news    ไซต์ปกติที่พนักงานเข้าได้
    site-social  ไซต์ที่นโยบายองค์กรสั่งบล็อกที่ proxy
    site-secure  ไซต์ HTTPS (สร้าง self-signed cert เองตอนสตาร์ท) ไว้พิสูจน์เรื่อง CONNECT

หน้าเว็บจะสรุปให้เห็นว่า "เซิร์ฟเวอร์เห็นอะไร" ซึ่งเป็นหลักฐานสำคัญของแล็บ:
    - forward proxy จะประทับ header  Via: 1.1 <ชื่อ proxy>
    - reverse proxy (Traefik) จะประทับ header  X-Forwarded-For / X-Forwarded-Host
    - ต่อตรงจะไม่มีทั้งสองอย่าง
"""

import html
import json
import os
import socket
import ssl
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SITE_NAME = os.environ.get("SITE_NAME", "site.lab")
SITE_TITLE = os.environ.get("SITE_TITLE", SITE_NAME)
SITE_TAG = os.environ.get("SITE_TAG", "เว็บไซต์จำลองในแล็บ")
SITE_EMOJI = os.environ.get("SITE_EMOJI", "🌐")
SITE_ACCENT = os.environ.get("SITE_ACCENT", "#8ec5ff")
PORT = int(os.environ.get("PORT", "80"))
USE_TLS = os.environ.get("SITE_TLS", "0") == "1"

HOSTNAME = socket.gethostname()
STATE = {"hits": 0}
LOCK = threading.Lock()

PAGE = r"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;display:grid;place-items:center;padding:34px;color:#eaf0ff;
    font-family:Inter,ui-sans-serif,system-ui,"Segoe UI",sans-serif;
    background:radial-gradient(circle at 18% 12%,color-mix(in srgb,__ACCENT__ 42%,transparent),transparent 38%),
               linear-gradient(150deg,#080c1b,#141b38 58%,#0a1024)}
  .card{width:min(860px,100%);border:1px solid rgba(255,255,255,.12);border-radius:26px;padding:34px;
    background:rgba(15,21,44,.74);backdrop-filter:blur(16px);box-shadow:0 26px 80px rgba(0,0,0,.35)}
  .eyebrow{font-size:12px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:#93a6ff}
  h1{margin:12px 0 8px;font-size:clamp(34px,6vw,58px);letter-spacing:-.04em;line-height:1}
  h1 span{color:__ACCENT__}
  .tag{color:#b7c2e6;font-size:18px;line-height:1.6}
  .scheme{display:inline-block;margin-top:16px;padding:7px 14px;border-radius:999px;font:800 13px/1 ui-monospace,Menlo,monospace;
    background:color-mix(in srgb,__ACCENT__ 20%,transparent);color:__ACCENT__;border:1px solid color-mix(in srgb,__ACCENT__ 45%,transparent)}
  table{width:100%;border-collapse:collapse;margin-top:24px;font-size:15px}
  th{text-align:left;padding:11px 12px;color:#93a6ff;font-size:11.5px;letter-spacing:.13em;text-transform:uppercase;
    border-bottom:1px solid rgba(255,255,255,.1);width:42%}
  td{padding:11px 12px;border-bottom:1px solid rgba(255,255,255,.06);font-family:ui-monospace,Menlo,monospace;
    color:#d6dffb;word-break:break-all}
  .yes{color:#7ee7a8} .no{color:#7d8bb5}
  .note{margin-top:22px;padding:15px 18px;border-left:4px solid __ACCENT__;border-radius:0 12px 12px 0;
    background:rgba(255,255,255,.05);color:#c2cdec;font-size:15px;line-height:1.65}
</style>
</head>
<body>
  <main class="card">
    <div class="eyebrow">LAB 6 · เว็บไซต์ฝั่งอินเทอร์เน็ต</div>
    <h1>__EMOJI__ <span>__SITE__</span></h1>
    <p class="tag">__TAG__</p>
    <div class="scheme">__SCHEME__ · เสิร์ฟโดย container __HOSTNAME__ · เข้าชมครั้งที่ __HITS__</div>
    <table>
      <tr><th>เซิร์ฟเวอร์เห็น IP ต้นทางเป็น</th><td>__REMOTE__</td></tr>
      <tr><th>Host ที่ขอมา</th><td>__HOST__</td></tr>
      <tr><th>Path</th><td>__PATH__</td></tr>
      <tr><th>Via (ลายเซ็นของ forward proxy)</th><td class="__VIACLS__">__VIA__</td></tr>
      <tr><th>X-Forwarded-For (ลายเซ็นของ reverse proxy)</th><td class="__XFFCLS__">__XFF__</td></tr>
      <tr><th>X-Forwarded-Host</th><td class="__XFFCLS__">__XFH__</td></tr>
      <tr><th>User-Agent</th><td>__UA__</td></tr>
    </table>
    <p class="note">__NOTE__</p>
  </main>
</body>
</html>
"""


class OriginHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "LabOrigin/1.0"
    sys_version = ""

    def log_message(self, fmt, *args):
        return

    def facts(self):
        via = self.headers.get("Via", "")
        xff = self.headers.get("X-Forwarded-For", "")
        with LOCK:
            hits = STATE["hits"]
        return {
            "site": SITE_NAME,
            "hostname": HOSTNAME,
            "scheme": "https" if USE_TLS else "http",
            "path": self.path,
            "host_header": self.headers.get("Host", ""),
            "remote_addr": self.client_address[0],
            "via": via,
            "x_forwarded_for": xff,
            "x_forwarded_host": self.headers.get("X-Forwarded-Host", ""),
            "user_agent": self.headers.get("User-Agent", ""),
            "hits": hits,
        }

    def note_for(self, facts):
        if facts["via"] and facts["x_forwarded_for"]:
            return (
                "request นี้ผ่าน <b>ทั้งสอง</b> ตัวกลาง — forward proxy ฝั่ง client ประทับ Via "
                "และ reverse proxy ฝั่งเซิร์ฟเวอร์ประทับ X-Forwarded-For"
            )
        if facts["via"]:
            return (
                "มี Via แต่ไม่มี X-Forwarded-For → request นี้ออกมาทาง <b>forward proxy</b> "
                "ที่ client เป็นคนตั้งค่าเอง เว็บนี้ไม่ได้ตั้งอะไรไว้เลย"
            )
        if facts["x_forwarded_for"]:
            return (
                "มี X-Forwarded-For แต่ไม่มี Via → request นี้เข้ามาทาง <b>reverse proxy</b> "
                "ที่เจ้าของเว็บตั้งไว้หน้าระบบ client ไม่ต้องรู้เรื่องเลย"
            )
        return "ไม่มีทั้ง Via และ X-Forwarded-For → request นี้ <b>ต่อตรง</b> ไม่ผ่านตัวกลางใด ๆ"

    def render(self, facts):
        # ทุกค่าที่มาจาก request ต้อง escape ก่อนใส่ลง HTML เสมอ
        safe = {k: html.escape(str(v)) for k, v in facts.items()}
        return (
            PAGE.replace("__TITLE__", SITE_TITLE)
            .replace("__ACCENT__", SITE_ACCENT)
            .replace("__EMOJI__", SITE_EMOJI)
            .replace("__SITE__", SITE_NAME)
            .replace("__TAG__", SITE_TAG)
            .replace("__SCHEME__", safe["scheme"].upper())
            .replace("__HOSTNAME__", safe["hostname"])
            .replace("__HITS__", safe["hits"])
            .replace("__REMOTE__", safe["remote_addr"])
            .replace("__HOST__", safe["host_header"] or "-")
            .replace("__PATH__", safe["path"])
            .replace("__VIA__", safe["via"] or "— ไม่มี —")
            .replace("__VIACLS__", "yes" if facts["via"] else "no")
            .replace("__XFF__", safe["x_forwarded_for"] or "— ไม่มี —")
            .replace("__XFH__", safe["x_forwarded_host"] or "— ไม่มี —")
            .replace("__XFFCLS__", "yes" if facts["x_forwarded_for"] else "no")
            .replace("__UA__", safe["user_agent"] or "-")
            .replace("__NOTE__", self.note_for(facts))
            .encode("utf-8")
        )

    def do_GET(self):
        with LOCK:
            STATE["hits"] += 1
        facts = self.facts()

        print(
            f"[{SITE_NAME}] {self.command} {self.path} from={facts['remote_addr']} "
            f"host={facts['host_header'] or '-'} via={facts['via'] or '-'} "
            f"xff={facts['x_forwarded_for'] or '-'} ua={facts['user_agent'] or '-'}",
            flush=True,
        )

        if self.path.startswith("/api/info"):
            payload = json.dumps(facts, ensure_ascii=False).encode("utf-8")
            content_type = "application/json; charset=utf-8"
        elif self.path.startswith("/health"):
            payload = b"ok\n"
            content_type = "text/plain; charset=utf-8"
        else:
            payload = self.render(facts)
            content_type = "text/html; charset=utf-8"

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Lab-Site", SITE_NAME)
        self.send_header("Cache-Control", "max-age=60")
        self.end_headers()
        self.wfile.write(payload)


def make_cert():
    """สร้าง self-signed certificate ตอนสตาร์ท — openssl ติดมากับ image python:3.12-slim อยู่แล้ว"""
    crt, key = "/tmp/site.crt", "/tmp/site.key"
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
            "-keyout", key, "-out", crt, "-days", "365",
            "-subj", f"/CN={SITE_NAME}",
            "-addext", f"subjectAltName=DNS:{SITE_NAME}",
        ],
        check=True,
        capture_output=True,
    )
    return crt, key


def main():
    httpd = ThreadingHTTPServer(("0.0.0.0", PORT), OriginHandler)
    if USE_TLS:
        crt, key = make_cert()
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(crt, key)
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
    print(
        f"[{SITE_NAME}] serving {'https' if USE_TLS else 'http'} on :{PORT} "
        f"(container {HOSTNAME}, started {time.strftime('%H:%M:%S')})",
        flush=True,
    )
    httpd.serve_forever()


if __name__ == "__main__":
    main()
