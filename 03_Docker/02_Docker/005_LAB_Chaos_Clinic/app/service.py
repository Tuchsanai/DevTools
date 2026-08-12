import json
import os
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PORT = int(os.getenv("PORT", "8080"))
MODE = os.getenv("HEALTH_MODE", "broken")
RELEASE = os.getenv("RELEASE", "canary")


def event(kind, **data):
    print(json.dumps({"timestamp": time.time(), "event": kind, "mode": MODE, **data}), flush=True)


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type="application/json"):
        if not isinstance(body, str):
            body = json.dumps(body)
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        event("request", path=self.path, client=self.client_address[0])
        if self.path == "/health":
            ready = MODE == "ready"
            self.send(200 if ready else 503, {"status": "healthy" if ready else "unhealthy", "reason": None if ready else "HEALTH_MODE must be ready"})
            return
        if self.path == "/crash":
            self.send(202, {"status": "crashing", "exit_code": 17})
            threading.Timer(0.2, lambda: os._exit(17)).start()
            return
        if self.path != "/":
            self.send(404, {"status": "not-found"})
            return
        ready = MODE == "ready"
        color = "#22c55e" if ready else "#fb7185"
        label = "HEALTHY" if ready else "UNHEALTHY"
        host = socket.gethostname()[:12]
        body = f"""<!doctype html><html lang='th'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Chaos Clinic</title><style>*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#0b0c13;color:#f8fafc;font-family:Inter,system-ui,sans-serif}}main{{width:min(960px,92vw);padding:46px;border-radius:30px;border:1px solid #303341;background:radial-gradient(circle at 80% 16%,#3f1d2b 0,transparent 37%),#141622;box-shadow:0 34px 100px #000b}}.kicker{{color:#fda4af;font-weight:900;letter-spacing:.15em}}h1{{font-size:clamp(48px,7vw,82px);line-height:.96;letter-spacing:-.06em;margin:20px 0}}p{{font-size:20px;color:#b5bac8;max-width:700px;line-height:1.6}}.status{{display:flex;align-items:center;gap:18px;margin:30px 0;padding:22px;border-radius:20px;background:#ffffff09;border:1px solid #ffffff15}}.lamp{{width:58px;height:58px;border-radius:50%;background:var(--signal);box-shadow:0 0 42px var(--signal)}}.status b{{display:block;font-size:30px;color:var(--signal)}}.status small{{color:#9ca3af}}.grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}}.card{{padding:18px;border-radius:16px;background:#ffffff08}}.card span{{display:block;color:#7f8797;font-size:12px;text-transform:uppercase;letter-spacing:.1em}}.card b{{display:block;margin-top:8px}}@media(max-width:650px){{main{{padding:28px}}.grid{{grid-template-columns:1fr}}}}</style></head><body style='--signal:{color}'><main><div class='kicker'>LAB 05 · OBSERVABILITY</div><h1>Chaos Clinic</h1><p>Container ที่ <b>running</b> อาจยังไม่ <b>ready</b> — อ่าน healthcheck, structured logs และ restart count เพื่อรักษาจากหลักฐาน ไม่ใช่เดา</p><div class='status'><div class='lamp'></div><div><b>{label}</b><small>health endpoint reports mode={MODE}</small></div></div><div class='grid'><div class='card'><span>release</span><b>{RELEASE}</b></div><div class='card'><span>container</span><b>{host}</b></div><div class='card'><span>runtime user</span><b>uid {os.getuid()}</b></div></div></main></body></html>"""
        self.send(200, body, "text/html")

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    event("startup", port=PORT, uid=os.getuid(), release=RELEASE)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
