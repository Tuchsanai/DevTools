import json
import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


PORT = int(os.getenv("PORT", "8080"))
DATA_FILE = os.getenv("DATA_FILE", "/data/state.json")
LOCK = threading.Lock()


def load_state():
    try:
        with open(DATA_FILE, encoding="utf-8") as stream:
            return json.load(stream)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"count": 0, "generation": 0}


def save_state(state):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    temporary = DATA_FILE + ".tmp"
    with open(temporary, "w", encoding="utf-8") as stream:
        json.dump(state, stream)
    os.replace(temporary, DATA_FILE)


class Handler(BaseHTTPRequestHandler):
    def send(self, status, body, content_type="text/html"):
        payload = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", f"{content_type}; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path == "/health":
            self.send(200, '{"status":"ok"}', "application/json")
            return
        with LOCK:
            state = load_state()
            if self.path.startswith("/hit"):
                state["count"] += 1
                save_state(state)
            elif self.path.startswith("/new-generation"):
                state["generation"] += 1
                save_state(state)
            elif self.path.startswith("/reset"):
                state = {"count": 0, "generation": state.get("generation", 0)}
                save_state(state)
            elif self.path != "/":
                self.send(404, "not found", "text/plain")
                return
        host = socket.gethostname()[:12]
        body = f"""<!doctype html><html lang='th'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Volume Time Machine</title><style>*{{box-sizing:border-box}}body{{margin:0;min-height:100vh;display:grid;place-items:center;background:#090b18;color:#f8fafc;font-family:Inter,system-ui,sans-serif}}main{{width:min(940px,92vw);padding:46px;border-radius:30px;background:radial-gradient(circle at 75% 15%,#312e81 0,transparent 38%),#12162a;border:1px solid #33375b;box-shadow:0 32px 100px #0009}}.kicker{{color:#c4b5fd;font-weight:800;letter-spacing:.15em}}h1{{font-size:clamp(46px,7vw,80px);line-height:.95;letter-spacing:-.055em;margin:22px 0}}h1 span{{color:#a78bfa}}p{{font-size:20px;line-height:1.55;color:#b9c0d4;max-width:680px}}.counter{{display:flex;align-items:end;gap:25px;margin:30px 0}}.number{{font-size:100px;line-height:.85;font-weight:900;color:#facc15}}.meta{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}.card{{padding:18px;border-radius:16px;background:#ffffff0a;border:1px solid #ffffff16}}.card small{{display:block;color:#8b93aa;text-transform:uppercase}}.card b{{display:block;margin-top:7px;color:#ddd6fe}}a{{display:inline-block;margin-top:26px;padding:12px 18px;border-radius:12px;background:#7c3aed;color:white;text-decoration:none;font-weight:800}}@media(max-width:650px){{main{{padding:28px}}.meta{{grid-template-columns:1fr}}}}</style></head><body><main><div class='kicker'>LAB 03 · NAMED VOLUME</div><h1>Volume<br><span>Time Machine</span></h1><p>ลบ container ได้ แต่ความทรงจำยังอยู่ เพราะ state แยกออกมาเก็บใน Docker-managed volume</p><div class='counter'><div class='number'>{state['count']}</div><div>เหตุการณ์ที่บันทึกแล้ว<br><b>generation {state.get('generation', 0)}</b></div></div><div class='meta'><div class='card'><small>current container</small><b>{host}</b></div><div class='card'><small>persistent file</small><b>/data/state.json</b></div></div><a href='/hit'>+ บันทึกเหตุการณ์</a></main></body></html>"""
        self.send(200, body)

    def log_message(self, fmt, *args):
        print(json.dumps({"service": "time-machine", "path": self.path, "message": fmt % args}), flush=True)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
