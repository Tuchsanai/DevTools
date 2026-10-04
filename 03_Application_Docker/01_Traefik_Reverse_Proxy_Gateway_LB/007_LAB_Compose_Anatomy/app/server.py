"""แอปตัวอย่างของ LAB 7 — ตั้งใจให้ฟัง 2 port พร้อมกัน

    :8080  API ของแอปจริง   (สิ่งที่เราอยากให้ผู้ใช้เข้าถึงผ่าน Traefik)
    :9090  metrics ภายใน    (สิ่งที่ไม่ควรเปิดออกไป — มีไว้ให้เห็นว่า "เลือก port ผิด" หน้าตาเป็นยังไง)

ทั้งสอง port ตอบด้วยเนื้อหาที่บอกตัวเองชัดเจน จึงพิสูจน์ได้ทันทีว่า Traefik
ส่ง request ไปที่ port ไหน ซึ่งเป็นหัวใจของ label
`traefik.http.services.<ชื่อ>.loadbalancer.server.port`
"""

import json
import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOSTNAME = socket.gethostname()
APP_PORT = int(os.environ.get("APP_PORT", "8080"))
METRICS_PORT = int(os.environ.get("METRICS_PORT", "9090"))
STATE = {"app": 0, "metrics": 0}
LOCK = threading.Lock()

PAGE = r"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>LAB 7 — พอร์ต __PORT__</title>
<style>
  body{margin:0;min-height:100vh;display:grid;place-items:center;color:#eaf0ff;font-family:Inter,system-ui,"Segoe UI",sans-serif;
    background:radial-gradient(circle at 20% 10%,rgba(94,132,255,.30),transparent 40%),linear-gradient(150deg,#080c1b,#131a36 60%,#0a1024)}
  .card{width:min(720px,92vw);padding:40px;border-radius:26px;border:1px solid rgba(255,255,255,.12);
    background:rgba(15,21,44,.76);text-align:center}
  .eyebrow{font:800 12px/1 system-ui;letter-spacing:.2em;text-transform:uppercase;color:#93a6ff}
  .port{font:900 clamp(70px,16vw,140px)/1 ui-monospace,Menlo,monospace;letter-spacing:-.05em;margin:14px 0 6px;color:__COLOR__}
  h1{margin:0 0 12px;font-size:26px;letter-spacing:-.02em}
  p{color:#b7c2e6;line-height:1.7;font-size:16px;margin:0}
  code{font-family:ui-monospace,Menlo,monospace;background:rgba(255,255,255,.08);padding:2px 7px;border-radius:6px}
</style>
</head>
<body><main class="card">
  <div class="eyebrow">LAB 7 · Compose Anatomy</div>
  <div class="port">:__PORT__</div>
  <h1>__ROLE__ · container __HOSTNAME__</h1>
  <p>__NOTE__</p>
  <p style="margin-top:14px">เสิร์ฟไปแล้ว __COUNT__ ครั้ง · ตรวจแบบเครื่องอ่านได้ที่ <code>/api/info</code></p>
</main></body></html>
"""


def make_handler(role, port, color, note):
    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"
        server_version = "Lab7App/1.0"
        sys_version = ""

        def log_message(self, fmt, *args):
            return

        def do_GET(self):
            with LOCK:
                STATE[role] += 1
                count = STATE[role]

            print(
                f"[{role}:{port}] {self.command} {self.path} "
                f"host={self.headers.get('Host', '-')} from={self.client_address[0]}",
                flush=True,
            )

            # ใช้ "ลงท้ายด้วย" เพื่อให้เรียกได้ทั้ง /api/info และ /app/api/info
            # (Traefik ในแล็บนี้ส่ง path เดิมต่อไปให้ backend ไม่ได้ตัด prefix ทิ้ง)
            if self.path.rstrip("/").endswith("/api/info"):
                body = json.dumps(
                    {
                        "role": role,
                        "port": port,
                        "hostname": HOSTNAME,
                        "path": self.path,
                        "host_header": self.headers.get("Host", ""),
                        "served": count,
                    },
                    ensure_ascii=False,
                ).encode()
                ctype = "application/json; charset=utf-8"
            elif self.path.rstrip("/").endswith("/health"):
                body, ctype = b"ok\n", "text/plain; charset=utf-8"
            elif role == "metrics":
                body = (
                    f"# HELP lab7_requests_total requests served on the internal metrics port\n"
                    f"lab7_requests_total{{port=\"{port}\"}} {count}\n"
                ).encode()
                ctype = "text/plain; charset=utf-8"
            else:
                body = (
                    PAGE.replace("__PORT__", str(port))
                    .replace("__ROLE__", "API ของแอป" if role == "app" else "metrics ภายใน")
                    .replace("__HOSTNAME__", HOSTNAME)
                    .replace("__COLOR__", color)
                    .replace("__NOTE__", note)
                    .replace("__COUNT__", str(count))
                ).encode()
                ctype = "text/html; charset=utf-8"

            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-Lab-Port", str(port))
            self.send_header("X-Lab-Role", role)
            self.end_headers()
            self.wfile.write(body)

    return Handler


def serve(role, port, color, note):
    ThreadingHTTPServer(("0.0.0.0", port), make_handler(role, port, color, note)).serve_forever()


def main():
    threading.Thread(
        target=serve,
        args=(
            "metrics",
            METRICS_PORT,
            "#ffb84d",
            "ถ้าเห็นหน้านี้ผ่าน Traefik แปลว่า route ไปผิด port — พอร์ตนี้เป็นของทีมระบบ ไม่ใช่ของผู้ใช้",
        ),
        daemon=True,
    ).start()
    print(f"[app] listening on {APP_PORT} (app) and {METRICS_PORT} (metrics)", flush=True)
    serve(
        "app",
        APP_PORT,
        "#7ee7a8",
        "นี่คือพอร์ตที่ผู้ใช้ควรเข้าถึง — Traefik จะรู้จักพอร์ตนี้ก็ต่อเมื่อเราบอกมันด้วย label หรือด้วย EXPOSE ใน image",
    )


if __name__ == "__main__":
    main()
