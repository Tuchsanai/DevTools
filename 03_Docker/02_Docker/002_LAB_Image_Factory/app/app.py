import html
import json
import os
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PORT = int(os.getenv("PORT", "8080"))


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self.send(200, json.dumps({"status": "ok"}), "application/json")
            return
        if self.path != "/":
            self.send(404, "not found", "text/plain")
            return

        theme = os.getenv("APP_THEME", "ocean").lower()
        palette = {
            "ocean": ("#071a2c", "#22d3ee", "#0e7490"),
            "sunset": ("#2b1220", "#fb7185", "#be123c"),
            "violet": ("#17112c", "#c084fc", "#7e22ce"),
        }.get(theme, ("#071a2c", "#22d3ee", "#0e7490"))
        stage = html.escape(os.getenv("APP_STAGE", "development"))
        version = html.escape(os.getenv("APP_VERSION", "unknown"))
        hostname = html.escape(socket.gethostname()[:12])
        body = f"""<!doctype html><html lang='th'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Image Factory</title>
<style>*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:{palette[0]};color:#f8fafc;font-family:Inter,system-ui,sans-serif}}main{{width:min(940px,92vw);padding:48px;border-radius:30px;background:linear-gradient(145deg,#ffffff10,#ffffff05);border:1px solid #ffffff1c;box-shadow:0 36px 100px #0008}}.label{{color:{palette[1]};font-weight:800;letter-spacing:.15em}}h1{{font-size:clamp(46px,7vw,84px);line-height:.95;letter-spacing:-.06em;margin:22px 0}}h1 em{{color:{palette[1]};font-style:normal}}p{{font-size:20px;color:#cbd5e1;max-width:690px;line-height:1.6}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:15px;margin-top:34px}}.card{{padding:22px;border-radius:18px;background:#ffffff0b;border:1px solid #ffffff18}}.card span{{display:block;color:#94a3b8;font-size:13px;text-transform:uppercase;letter-spacing:.1em}}.card b{{display:block;margin-top:8px;font-size:22px;color:{palette[1]}}}.pill{{display:inline-block;margin-top:26px;padding:9px 15px;border-radius:999px;background:{palette[2]};font-weight:750}}@media(max-width:650px){{main{{padding:28px}}.grid{{grid-template-columns:1fr}}}}</style></head><body><main><div class='label'>LAB 02 · IMMUTABLE IMAGE</div><h1>Build once.<br><em>Configure at run.</em></h1><p>โค้ดชุดเดียวกันเปลี่ยนบุคลิกได้ด้วย environment variable โดยไม่ต้อง build image ใหม่</p><div class='pill'>healthy · uid 10001 · non-root</div><div class='grid'><div class='card'><span>theme</span><b>{html.escape(theme)}</b></div><div class='card'><span>stage</span><b>{stage}</b></div><div class='card'><span>version / container</span><b>{version} · {hostname}</b></div></div></main></body></html>"""
        self.send(200, body, "text/html")

    def log_message(self, fmt, *args):
        print(json.dumps({"service": "image-factory", "path": self.path, "message": fmt % args}), flush=True)


if __name__ == "__main__":
    print(json.dumps({"event": "startup", "port": PORT, "uid": os.getuid()}), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
