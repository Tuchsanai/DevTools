import hashlib
import json
import os
import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


HOSTNAME = socket.gethostname()
HOST_HASH = int(hashlib.sha256(HOSTNAME.encode()).hexdigest(), 16)
# 360 possible hues make an accidental same-color collision between three
# replicas very unlikely, while saturation/lightness keep every color legible.
HUE = HOST_HASH % 360
COLOR = f"hsl({HUE} 78% 60%)"
ACCENT = f"hsl({(HUE + 52) % 360} 82% 64%)"
STATE = {"served_count": 0, "healthy": True}
LOCK = threading.Lock()


def page() -> bytes:
    html = r"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Wow! Traefik Load Balancer</title>
  <style>
    :root { --replica: __COLOR__; --accent: __ACCENT__; }
    * { box-sizing: border-box; }
    body {
      margin: 0; min-height: 100vh; color: #f8fafc;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: radial-gradient(circle at 15% 10%, color-mix(in srgb, var(--replica) 45%, transparent), transparent 35%),
                  radial-gradient(circle at 85% 90%, color-mix(in srgb, var(--accent) 35%, transparent), transparent 36%),
                  linear-gradient(145deg, #090b18, #151934 58%, #0b1023);
      display: grid; place-items: center; padding: 38px;
    }
    .shell { width: min(1120px, 100%); }
    .eyebrow { color: #b9c0dc; font-size: 13px; font-weight: 800; letter-spacing: .18em; text-transform: uppercase; }
    h1 { font-size: clamp(54px, 8vw, 104px); line-height: .9; margin: 18px 0 12px; letter-spacing: -.065em; }
    h1 span { color: var(--replica); text-shadow: 0 0 44px color-mix(in srgb, var(--replica) 65%, transparent); }
    .lead { color: #c8cee6; max-width: 720px; font-size: 19px; line-height: 1.65; }
    .grid { display: grid; grid-template-columns: 1.1fr .9fr; gap: 20px; margin-top: 34px; }
    .card { background: rgba(18, 23, 48, .72); border: 1px solid rgba(255,255,255,.12); border-radius: 24px; padding: 26px; box-shadow: 0 22px 70px rgba(0,0,0,.28); backdrop-filter: blur(16px); }
    .label { color: #8f98ba; font-size: 12px; font-weight: 800; letter-spacing: .13em; text-transform: uppercase; }
    .hostname { margin-top: 10px; font: 800 clamp(27px, 4vw, 45px)/1.1 ui-monospace, SFMono-Regular, Menlo, monospace; word-break: break-all; color: var(--replica); }
    .stats { display: flex; gap: 14px; margin-top: 22px; }
    .stat { flex: 1; padding: 15px; background: rgba(255,255,255,.055); border-radius: 15px; }
    .stat b { display: block; font-size: 25px; margin-top: 5px; }
    button { width: 100%; border: 0; border-radius: 15px; padding: 16px 18px; margin: 18px 0; color: #fff; font-size: 16px; font-weight: 850; cursor: pointer; background: linear-gradient(120deg, var(--replica), var(--accent)); box-shadow: 0 12px 32px color-mix(in srgb, var(--replica) 30%, transparent); }
    button:disabled { cursor: wait; opacity: .65; }
    .bars { display: grid; grid-template-columns: repeat(20, 1fr); gap: 5px; height: 122px; align-items: end; }
    .bar { min-width: 4px; height: 0; border-radius: 6px 6px 2px 2px; transition: height .35s ease; box-shadow: 0 0 15px currentColor; }
    .legend { min-height: 47px; display: flex; flex-wrap: wrap; gap: 8px 15px; margin-top: 14px; color: #cbd2ea; font: 12px ui-monospace, monospace; }
    .dot { width: 9px; height: 9px; display: inline-block; margin-right: 6px; border-radius: 50%; }
    .hint { color: #8992b4; font-size: 13px; line-height: 1.5; }
    @media (max-width: 780px) { body { padding: 22px; } .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <main class="shell">
    <div class="eyebrow">LAB 002 · Traefik as a Load Balancer</div>
    <h1>Wow! <span>__HOSTNAME__</span></h1>
    <p class="lead">หน้าเดียว แต่มีแอปอยู่ข้างหลัง 3 replicas — ให้ Traefik เลือกปลายทาง แล้วดูการกระจาย request เปลี่ยนเป็นสีตรงหน้า</p>
    <section class="grid">
      <article class="card">
        <div class="label">Replica ที่สร้าง HTML หน้านี้</div>
        <div class="hostname">__HOSTNAME__</div>
        <div class="stats">
          <div class="stat"><span class="label">สีประจำตัว</span><b style="color:var(--replica)">__COLOR__</b></div>
          <div class="stat"><span class="label">Request count</span><b id="count">__COUNT__</b></div>
        </div>
      </article>
      <article class="card">
        <div class="label">20 requests ผ่าน Traefik</div>
        <button id="fire">ยิง 20 requests</button>
        <div id="bars" class="bars" aria-label="ผลการกระจาย request"></div>
        <div id="legend" class="legend"></div>
        <div class="hint">แต่ละแท่ง = 1 response · สีและชื่อบอก replica ที่ตอบกลับ</div>
      </article>
    </section>
  </main>
  <script>
    const button = document.querySelector('#fire');
    const bars = document.querySelector('#bars');
    const legend = document.querySelector('#legend');
    const count = document.querySelector('#count');

    async function fire() {
      button.disabled = true;
      button.textContent = 'กำลังยิง request…';
      bars.innerHTML = '';
      legend.innerHTML = '';
      const seen = new Map();
      for (let i = 0; i < 20; i++) {
        const response = await fetch('/api/whoami', { cache: 'no-store' });
        const data = await response.json();
        const bar = document.createElement('div');
        bar.className = 'bar';
        bar.style.background = data.color;
        bar.style.color = data.color;
        bar.title = `${i + 1}: ${data.hostname} (#${data.served_count})`;
        bars.appendChild(bar);
        requestAnimationFrame(() => bar.style.height = `${48 + (i % 5) * 15}px`);
        seen.set(data.hostname, { color: data.color, count: (seen.get(data.hostname)?.count || 0) + 1 });
        count.textContent = data.served_count;
      }
      legend.innerHTML = [...seen].map(([host, info]) =>
        `<span><i class="dot" style="background:${info.color}"></i>${host} × ${info.count}</span>`).join('');
      button.disabled = false;
      button.textContent = 'ยิงอีก 20 requests';
      document.body.dataset.burstComplete = 'true';
    }
    button.addEventListener('click', fire);
  </script>
</body>
</html>"""
    return (
        html.replace("__HOSTNAME__", HOSTNAME)
        .replace("__COLOR__", COLOR)
        .replace("__ACCENT__", ACCENT)
        .replace("__COUNT__", str(STATE["served_count"]))
        .encode()
    )


class Handler(BaseHTTPRequestHandler):
    server_version = "Lab002/1.0"

    def send_body(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path.split("?", 1)[0] == "/health":
            healthy = STATE["healthy"]
            self.send_body(200 if healthy else 500, b"OK\n" if healthy else b"FAILED\n", "text/plain; charset=utf-8")
            return

        with LOCK:
            STATE["served_count"] += 1
            served_count = STATE["served_count"]

        path = self.path.split("?", 1)[0]
        if path == "/api/whoami":
            body = json.dumps(
                {"hostname": HOSTNAME, "color": COLOR, "served_count": served_count},
                separators=(",", ":"),
            ).encode()
            self.send_body(200, body, "application/json")
        elif path == "/":
            self.send_body(200, page(), "text/html; charset=utf-8")
        else:
            self.send_body(404, b"Not Found\n", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        if self.path == "/health/fail":
            STATE["healthy"] = False
            self.send_body(200, b"health=FAILED\n", "text/plain; charset=utf-8")
        elif self.path == "/health/ok":
            STATE["healthy"] = True
            self.send_body(200, b"health=OK\n", "text/plain; charset=utf-8")
        else:
            self.send_body(404, b"Not Found\n", "text/plain; charset=utf-8")

    def log_message(self, fmt: str, *args: object) -> None:
        print(f"{self.address_string()} - {fmt % args}", flush=True)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    print(f"LAB002 app listening on :{port} hostname={HOSTNAME} color={COLOR}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
