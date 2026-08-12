import html
import json
import os
import socket
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


ROLE = os.getenv("ROLE", "web")
PORT = int(os.getenv("PORT", "8080"))
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
API_URL = os.getenv("API_URL", "http://api:8000")


def redis_command(*parts):
    request = f"*{len(parts)}\r\n".encode()
    for part in parts:
        encoded = str(part).encode()
        request += f"${len(encoded)}\r\n".encode() + encoded + b"\r\n"
    with socket.create_connection((REDIS_HOST, 6379), timeout=2) as connection:
        connection.sendall(request)
        stream = connection.makefile("rb")
        prefix = stream.read(1)
        line = stream.readline().rstrip(b"\r\n")
        if prefix == b"+":
            return line.decode()
        if prefix == b":":
            return int(line)
        if prefix == b"$":
            size = int(line)
            return stream.read(size).decode() if size >= 0 else None
        raise RuntimeError(line.decode(errors="replace"))


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=2) as response:
        return json.loads(response.read())


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
        try:
            if ROLE == "api":
                self.handle_api()
            else:
                self.handle_web()
        except Exception as error:
            self.send(503, {"status": "error", "detail": str(error), "service": ROLE})

    def handle_api(self):
        if self.path == "/health":
            self.send(200, {"status": "ok", "redis": redis_command("PING")})
        elif self.path == "/stats":
            visits = redis_command("INCR", "radar:visits")
            self.send(200, {"status": "online", "visits": visits, "redis": "PONG", "api": socket.gethostname()[:12]})
        else:
            self.send(404, {"status": "not-found"})

    def handle_web(self):
        if self.path == "/health":
            data = fetch_json(API_URL + "/health")
            self.send(200, {"status": "ok", "api": data["status"]})
        elif self.path == "/data":
            self.send(200, fetch_json(API_URL + "/stats"))
        elif self.path == "/":
            title = html.escape(os.getenv("DASHBOARD_TITLE", "Compose Service Radar"))
            body = f"""<!doctype html><html lang='th'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title><style>*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#07111f;color:#edf6ff;font-family:Inter,system-ui,sans-serif}}main{{width:min(1040px,94vw);padding:42px;border:1px solid #203b55;border-radius:30px;background:linear-gradient(135deg,#0b1b2c,#101832);box-shadow:0 32px 100px #0009}}.top{{display:flex;justify-content:space-between;align-items:start;gap:20px}}.kicker{{color:#67e8f9;font-weight:900;letter-spacing:.14em}}h1{{font-size:clamp(42px,6vw,72px);letter-spacing:-.055em;line-height:1;margin:18px 0}}p{{font-size:19px;color:#9fb5ca}}.live{{padding:9px 14px;border-radius:999px;background:#123629;color:#86efac;font-weight:800}}.live:before{{content:'';display:inline-block;width:8px;height:8px;border-radius:50%;background:#22c55e;margin-right:8px;box-shadow:0 0 15px #22c55e}}.flow{{display:grid;grid-template-columns:1fr 60px 1fr 60px 1fr;align-items:center;margin:36px 0 24px}}.node{{height:150px;padding:22px;border-radius:20px;border:1px solid #ffffff1b;background:#ffffff0b}}.node b{{font-size:25px}}.node small{{display:block;color:#849ab0;margin-top:10px;line-height:1.5}}.arrow{{text-align:center;color:#22d3ee;font-size:32px}}.metric{{display:flex;align-items:end;gap:18px;padding:22px;border-radius:18px;background:#0b2941;border:1px solid #155e75}}#visits{{font-size:70px;font-weight:950;line-height:.8;color:#facc15}}#detail{{color:#9fb5ca}}@media(max-width:760px){{.flow{{grid-template-columns:1fr;gap:10px}}.arrow{{transform:rotate(90deg)}}.top{{display:block}}}}</style></head><body><main><div class='top'><div><div class='kicker'>LAB 04 · COMPOSE</div><h1>{title}</h1><p>หนึ่งคำสั่ง ปลุกทั้ง web, API และ Redis บนเครือข่ายที่แยกชั้น</p></div><div class='live' id='status'>checking</div></div><div class='flow'><div class='node'><b>WEB</b><small>public :8080<br>frontend + proxy</small></div><div class='arrow'>→</div><div class='node'><b>API</b><small>private :8000<br>service-name DNS</small></div><div class='arrow'>→</div><div class='node'><b>REDIS</b><small>private :6379<br>named volume</small></div></div><div class='metric'><div id='visits'>—</div><div><b>requests crossed the stack</b><br><span id='detail'>waiting for health gates…</span></div></div></main><script>fetch('/data').then(r=>r.json()).then(d=>{{document.querySelector('#visits').textContent=d.visits;document.querySelector('#detail').textContent='web → '+d.api+' → '+d.redis;document.querySelector('#status').textContent='all services healthy'}}).catch(e=>{{document.querySelector('#status').textContent='degraded';document.querySelector('#detail').textContent=e}})</script></body></html>"""
            self.send(200, body, "text/html")
        else:
            self.send(404, {"status": "not-found"})

    def log_message(self, fmt, *args):
        print(json.dumps({"service": ROLE, "path": self.path, "message": fmt % args}), flush=True)


if __name__ == "__main__":
    print(json.dumps({"event": "startup", "role": ROLE, "port": PORT, "uid": os.getuid()}), flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
