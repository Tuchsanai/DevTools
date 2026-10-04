"""Mini Forward Proxy สำหรับ LAB 6 — เขียนด้วย Python standard library ล้วน

จุดประสงค์ของไฟล์นี้คือ "อ่านได้" ไม่ใช่ "ครบทุก feature":
ของจริงในองค์กรจะใช้ Squid / tinyproxy / Envoy แต่กลไกแกนกลางคือสิ่งเดียวกันสามข้อ

    1. client ตั้งค่าให้ส่ง request มาที่ proxy โดยตรง (curl -x, http_proxy, ตั้งใน browser)
    2. request แบบ HTTP ที่ส่งมาหา proxy ใช้ "absolute-form"  →  GET http://news.lab/ HTTP/1.1
       (ต่างจาก request ที่ยิงเข้าเว็บตรง ๆ ซึ่งเป็น origin-form  →  GET / HTTP/1.1 + Host:)
       ตาม RFC 9112 เซิร์ฟเวอร์ต้องรองรับ absolute-form ด้วย แต่ในทางปฏิบัติเราจะเห็นมันในบันทึกของ proxy
    3. request แบบ HTTPS ใช้เมธอด CONNECT ให้ proxy เปิด "ท่อ" TCP ให้ แล้ว TLS
       วิ่งผ่านท่อนั้นแบบ end-to-end  →  proxy เห็นแค่ host:port ไม่เห็น path/เนื้อหา

พอร์ตที่เปิด
    :8888  proxy port   — ปลายทางของ curl -x / http_proxy
    :8899  egress console — หน้าเว็บสรุป log ขาออกแบบ real-time (หน้า Wow ของแล็บนี้)

ตัวแปรสภาพแวดล้อม
    PROXY_NAME       ชื่อที่ประทับใน header Via และแสดงบน console
    PROXY_DENY       รายชื่อ host ที่ห้ามออก คั่นด้วย comma (เช่น "social.lab")
    PROXY_ALLOW      ถ้าตั้งไว้ = allowlist โหมด (อนุญาตเฉพาะที่ระบุ)
    PROXY_CACHE_TTL  วินาทีที่จะ cache คำตอบของ GET (0 = ปิด cache)
"""

import html
import json
import os
import select
import socket
import threading
import time
from collections import deque
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

PROXY_PORT = int(os.environ.get("PROXY_PORT", "8888"))
UI_PORT = int(os.environ.get("PROXY_UI_PORT", "8899"))
PROXY_NAME = os.environ.get("PROXY_NAME", "lab-forward-proxy")
CACHE_TTL = int(os.environ.get("PROXY_CACHE_TTL", "0"))
MAX_BODY = int(os.environ.get("PROXY_MAX_BODY", str(2 * 1024 * 1024)))   # กันคำขอ body ใหญ่เกินในแล็บ
MAX_CACHE_ENTRIES = 64
CONNECT_PORTS = {
    int(x) for x in os.environ.get("PROXY_CONNECT_PORTS", "443,8443").split(",") if x.strip().isdigit()
}


def _host_list(raw: str):
    return tuple(h.strip().lower() for h in raw.split(",") if h.strip())


DENY = _host_list(os.environ.get("PROXY_DENY", ""))
ALLOW = _host_list(os.environ.get("PROXY_ALLOW", ""))

# header ที่เป็นของ "ช่วงต่อเดียว" (hop-by-hop) ห้ามส่งต่อไปยัง hop ถัดไป — RFC 9110 §7.6.1
# ค่าคงที่ตาม RFC — แต่ "ชื่อจริง" ของ hop-by-hop ในแต่ละ request ยังต้องอ่านจาก Connection: ด้วย
HOP_BY_HOP = {
    "connection",
    "proxy-connection",
    "keep-alive",
    "transfer-encoding",
    "te",
    "trailer",
    "upgrade",
    "proxy-authenticate",
    "proxy-authorization",
}

def hop_by_hop(headers):
    """hop-by-hop มาตรฐาน + ทุกชื่อที่ถูกระบุไว้ใน header Connection: ของ hop นั้น (RFC 9110 §7.6.1)"""
    drop = set(HOP_BY_HOP)
    getter = getattr(headers, "get_all", None)
    values = getter("Connection", []) if getter else ([headers.get("Connection")] if headers.get("Connection") else [])
    for value in values:
        for token in (value or "").split(","):
            token = token.strip().lower()
            if token:
                drop.add(token)
    return drop


START_TIME = time.time()
EVENTS = deque(maxlen=300)
STATS = {"allow": 0, "deny": 0, "connect": 0, "error": 0, "cache_hit": 0, "bytes": 0}
CACHE = {}
LOCK = threading.Lock()
SEQ = {"n": 0}


def record(**event):
    """เก็บเหตุการณ์ลง ring buffer + พิมพ์ log หนึ่งบรรทัดให้ `docker compose logs` อ่านง่าย"""
    with LOCK:
        SEQ["n"] += 1
        event["id"] = SEQ["n"]
        event.setdefault("time", time.strftime("%H:%M:%S"))
        EVENTS.appendleft(event)
        decision = event.get("decision", "ERROR").lower()
        if decision in ("allow", "deny", "error"):
            STATS[decision] += 1
        if event.get("method") == "CONNECT" and decision == "allow":
            STATS["connect"] += 1
        if event.get("cache") == "HIT":
            STATS["cache_hit"] += 1
        STATS["bytes"] += int(event.get("bytes") or 0)

    target = event.get("target", "-")
    extra = ""
    if event.get("method") == "CONNECT" and event.get("decision") == "ALLOW":
        extra = "  (encrypted tunnel — proxy sees host:port only)"
    elif event.get("decision") == "DENY":
        extra = f"  [{event.get('reason', 'policy')}]"
    elif event.get("cache") and event["cache"] != "OFF":
        extra = f"  cache={event['cache']}"
    print(
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} client={event.get('client', '-'):<15} "
        f"{event.get('decision', 'ERROR'):<5} {event.get('method', '-'):<7} {target:<42} "
        f"-> {event.get('status', '-')} ({event.get('bytes', 0)} bytes){extra}",
        flush=True,
    )


def policy_verdict(host: str):
    """คืน (allowed, reason) — allowlist ชนะ denylist เมื่อถูกตั้งพร้อมกัน

    ข้อความ reason เป็นภาษาอังกฤษล้วนเพราะถูกใส่ลงใน HTTP header ด้วย
    (header ตาม RFC เป็น ASCII — ภาษาไทยจะกลายเป็น ??? )
    """
    host = (host or "").lower()
    if ALLOW:
        if host in ALLOW:
            return True, f"allowlist: {', '.join(ALLOW)}"
        return False, f"not in allowlist: {', '.join(ALLOW)}"
    if host in DENY:
        return False, f"denylist: {', '.join(DENY)}"
    return True, "no policy rule matched"


def cacheable(status, headers):
    """เก็บเฉพาะคำตอบที่ไม่ผูกกับผู้ใช้คนใดคนหนึ่ง (ของจริงมีเงื่อนไขมากกว่านี้อีกเยอะ)"""
    if status != 200:
        return False
    for key, value in headers:
        low = key.lower()
        if low in ("set-cookie", "vary", "www-authenticate"):
            return False
        if low == "cache-control" and any(
            token.strip().lower() in ("no-store", "no-cache", "private") for token in value.split(",")
        ):
            return False
    return True


def tunnel(client_sock, upstream_sock):
    """คัดลอกไบต์สองทางจนกว่าฝั่งใดฝั่งหนึ่งจะปิด — นี่คือทั้งหมดที่ proxy ทำได้กับ HTTPS"""
    total = 0
    socks = [client_sock, upstream_sock]
    try:
        while True:
            readable, _, broken = select.select(socks, [], socks, 60)
            if broken or not readable:
                break
            for sock in readable:
                data = sock.recv(65536)
                if not data:
                    return total
                target = upstream_sock if sock is client_sock else client_sock
                target.sendall(data)
                total += len(data)
    except OSError:
        pass
    return total


class ForwardProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "LabForwardProxy/1.0"
    sys_version = ""

    # ปิด log มาตรฐานของ http.server เพราะเราพิมพ์บรรทัดของเราเองใน record()
    def log_message(self, fmt, *args):
        return

    def log_request(self, code="-", size="-"):
        return

    # ---------- HTTP ธรรมดา ----------
    def do_GET(self):
        self.proxy_plain("GET")

    def do_HEAD(self):
        self.proxy_plain("HEAD")

    def do_POST(self):
        self.proxy_plain("POST")

    def do_PUT(self):
        self.proxy_plain("PUT")

    def do_DELETE(self):
        self.proxy_plain("DELETE")

    def send_page(self, status, title, detail, target="-", method="-", decision="ERROR", reason=""):
        body = (
            "<!doctype html><html lang='th'><meta charset='utf-8'>"
            "<title>{t}</title>"
            "<body style=\"margin:0;min-height:100vh;display:grid;place-items:center;"
            "font-family:system-ui,'Segoe UI',sans-serif;background:#0b1020;color:#e7ecff\">"
            "<div style='max-width:640px;padding:38px;border:1px solid #2a3557;border-radius:20px;"
            "background:#131a33'>"
            "<div style='font:800 13px/1 system-ui;letter-spacing:.16em;color:#8ea3ff'>"
            "LAB 6 · FORWARD PROXY</div>"
            "<h1 style='margin:14px 0 10px;font-size:30px'>{t}</h1>"
            "<p style='color:#b9c5e8;line-height:1.7;font-size:17px'>{d}</p>"
            "<code style='display:block;margin-top:16px;padding:12px 14px;border-radius:10px;"
            "background:#0a0f22;color:#9fe6b5;font-size:15px'>{c}</code>"
            "</div></body></html>"
        ).format(t=title, d=detail, c=html.escape(f"{method} {target}")).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Lab-Proxy", PROXY_NAME)
        if reason:
            self.send_header("X-Lab-Proxy-Reason", reason)
        self.end_headers()
        self.wfile.write(body)
        record(
            client=self.client_address[0],
            method=method,
            target=target,
            status=status,
            bytes=len(body),
            decision=decision,
            reason=reason,
            cache="OFF",
        )

    def proxy_plain(self, method):
        # chunked request ต้องแยก frame เอง — แล็บนี้ไม่รองรับ และการปล่อยผ่านแบบครึ่ง ๆ กลาง ๆ
        # คือที่มาของช่องโหว่ request smuggling จึงปฏิเสธไปเลยแล้วปิด connection
        if self.headers.get("Transfer-Encoding"):
            self.close_connection = True
            self.send_page(
                501,
                "แล็บนี้ไม่รองรับ chunked request",
                "proxy ตัวอย่างนี้อ่าน body จาก <b>Content-Length</b> อย่างเดียว — "
                "ของจริงต้องรองรับ <code>Transfer-Encoding: chunked</code> ให้ถูกต้อง "
                "ไม่งั้นจะเกิดปัญหา request smuggling ได้",
                target=self.path, method=method, decision="ERROR",
                reason="transfer-encoding not supported",
            )
            return

        # request ที่ผ่าน forward proxy ต้องเป็น absolute-URI เสมอ
        if not self.path.startswith("http://"):
            self.send_page(
                400,
                "นี่คือ forward proxy ไม่ใช่เว็บไซต์",
                "proxy ตัวนี้รอรับ request แบบ absolute-URI เช่น <b>GET http://news.lab/ HTTP/1.1</b> "
                "ซึ่งเกิดขึ้นเมื่อ client ตั้งค่า proxy ไว้ (curl -x … หรือ http_proxy=…) "
                "การเปิด IP:8888 ตรง ๆ จะส่ง origin-form (GET / HTTP/1.1) มาแทน จึงไม่มีปลายทางให้ส่งต่อ",
                target=self.path,
                method=method,
                decision="ERROR",
                reason="origin-form request",
            )
            return

        try:
            parts = urlsplit(self.path)
            host = parts.hostname or ""
            port = parts.port or 80
        except ValueError as exc:      # เช่น port ไม่ใช่ตัวเลข หรือ URL เพี้ยน
            self.close_connection = True
            self.send_page(400, "URL ปลายทางอ่านไม่ออก", f"proxy แยกส่วนของ URL นี้ไม่ได้ ({exc})",
                           target=self.path, method=method, decision="ERROR", reason="bad request-target")
            return
        if not host:
            self.close_connection = True
            self.send_page(400, "URL ปลายทางไม่มีชื่อโฮสต์", "absolute-URI ต้องมีโฮสต์เสมอ เช่น <code>http://news.lab/</code>",
                           target=self.path, method=method, decision="ERROR", reason="missing host")
            return
        path = parts.path or "/"
        if parts.query:
            path = f"{path}?{parts.query}"
        target = f"http://{parts.netloc}{path}"

        allowed, reason = policy_verdict(host)
        if not allowed:
            self.send_page(
                403,
                "ถูกบล็อกที่ประตูขาออก",
                f"นโยบายของ proxy ไม่อนุญาตให้ออกไปยัง <b>{host}</b> ({reason}) — "
                "request ไม่เคยเดินทางไปถึงปลายทาง และเหตุการณ์นี้ถูกบันทึกไว้ที่ egress console แล้ว",
                target=target,
                method=method,
                decision="DENY",
                reason=reason,
            )
            return

        # cache ได้เฉพาะ request ที่ไม่มีข้อมูลผู้ใช้ติดมา ไม่งั้นจะจ่ายคำตอบของคนหนึ่งให้อีกคน
        private_request = bool(self.headers.get("Authorization") or self.headers.get("Cookie"))
        cache_key = f"{method} {target}"
        if CACHE_TTL > 0 and method == "GET" and not private_request:
            with LOCK:
                hit = CACHE.get(cache_key)
                if hit and hit[0] > time.time():
                    status, headers, payload = hit[1], hit[2], hit[3]
                else:
                    hit = None
            if hit:
                self.relay_response(status, headers, payload, method, target, "HIT", reason)
                return

        raw_length = self.headers.get("Content-Length")
        try:
            length = int(raw_length) if raw_length else 0
            if length < 0 or length > MAX_BODY:
                raise ValueError("body too large or negative")
        except ValueError:
            self.close_connection = True
            self.send_page(400, "Content-Length ใช้ไม่ได้",
                           f"ค่าที่ส่งมาคือ <code>{html.escape(str(raw_length))}</code> "
                           f"(แล็บนี้จำกัด body ไม่เกิน {MAX_BODY} ไบต์)",
                           target=target, method=method, decision="ERROR", reason="bad content-length")
            return
        body = self.rfile.read(length) if length else None

        drop = hop_by_hop(self.headers)
        forward_headers = {
            key: value for key, value in self.headers.items() if key.lower() not in drop
        }
        forward_headers["Host"] = parts.netloc
        # Via คือ "ลายเซ็น" ประจำตัวของ HTTP intermediary — ต้อง "ต่อท้าย" ของเดิม ไม่ใช่เขียนทับ
        existing_via = self.headers.get("Via")
        forward_headers["Via"] = f"{existing_via}, 1.1 {PROXY_NAME}" if existing_via else f"1.1 {PROXY_NAME}"

        try:
            conn = HTTPConnection(host, port, timeout=10)
            conn.request(method, path, body=body, headers=forward_headers)
            response = conn.getresponse()
            payload = response.read()
            drop_resp = hop_by_hop(response.headers)
            headers = [
                (key, value)
                for key, value in response.getheaders()
                if key.lower() not in drop_resp and key.lower() != "content-length"
            ]
            status = response.status
            conn.close()
        except OSError as exc:
            self.send_page(
                502,
                "proxy ต่อปลายทางไม่ได้",
                f"proxy ออกไปหา <b>{host}:{port}</b> แล้วไม่สำเร็จ ({exc}) — "
                "แปลว่าปัญหาอยู่ฝั่ง proxy→ปลายทาง ไม่ใช่ฝั่ง client→proxy",
                target=target,
                method=method,
                decision="ERROR",
                reason=str(exc),
            )
            return

        if CACHE_TTL > 0 and method == "GET" and not private_request and cacheable(status, headers):
            with LOCK:
                if len(CACHE) >= MAX_CACHE_ENTRIES:
                    CACHE.clear()           # แล็บ: ล้างทั้งก้อนง่ายกว่า และกันหน่วยความจำบวม
                CACHE[cache_key] = (time.time() + CACHE_TTL, status, headers, payload)

        self.relay_response(
            status, headers, payload, method, target, "MISS" if CACHE_TTL > 0 else "OFF", reason
        )

    def relay_response(self, status, headers, payload, method, target, cache_state, reason):
        self.send_response(status)
        for key, value in headers:
            self.send_header(key, value)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Via", f"1.1 {PROXY_NAME}")
        self.send_header("X-Lab-Proxy", PROXY_NAME)
        self.send_header("X-Lab-Cache", cache_state)
        self.end_headers()
        if method != "HEAD":
            self.wfile.write(payload)
        record(
            client=self.client_address[0],
            method=method,
            target=target,
            status=status,
            bytes=len(payload),
            decision="ALLOW",
            reason=reason,
            cache=cache_state,
        )

    # ---------- HTTPS ผ่าน CONNECT ----------
    def do_CONNECT(self):
        self.close_connection = True
        host, _, raw_port = self.path.rpartition(":")
        target = self.path
        if not host or host.startswith("[") or not raw_port.isdigit():
            # authority-form ที่ถูกต้องคือ host:port — แล็บนี้ไม่รองรับ IPv6 ในวงเล็บ
            body = b"bad CONNECT authority (expected host:port, IPv6 not supported in this lab)\n"
            self.send_response(400)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            record(client=self.client_address[0], method="CONNECT", target=self.path, status=400,
                   bytes=0, decision="ERROR", reason="bad authority", cache="OFF")
            return
        port = int(raw_port)
        target = f"{host}:{port}"

        if port not in CONNECT_PORTS:
            # ของจริงต้องจำกัด port ที่ tunnel ได้ ไม่งั้น proxy กลายเป็นทางลัดเข้าทุกบริการภายใน
            body = f"CONNECT to port {port} is not allowed (allowed: {sorted(CONNECT_PORTS)})\n".encode()
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            record(client=self.client_address[0], method="CONNECT", target=target, status=403,
                   bytes=0, decision="DENY", reason=f"port {port} not in allowed CONNECT ports", cache="OFF")
            return

        allowed, reason = policy_verdict(host)
        if not allowed:
            body = b"blocked by proxy policy\n"
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            record(
                client=self.client_address[0],
                method="CONNECT",
                target=target,
                status=403,
                bytes=0,
                decision="DENY",
                reason=reason,
                cache="OFF",
            )
            return

        try:
            upstream = socket.create_connection((host, port), timeout=10)
        except OSError as exc:
            body = f"proxy cannot reach {target}: {exc}\n".encode()
            self.send_response(502)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            record(
                client=self.client_address[0],
                method="CONNECT",
                target=target,
                status=502,
                bytes=0,
                decision="ERROR",
                reason=str(exc),
                cache="OFF",
            )
            return

        # ตอบ 200 แล้ว "ถอยออก" — ตั้งแต่บรรทัดนี้ไปคือ TLS ระหว่าง client กับปลายทางล้วน ๆ
        self.wfile.write(b"HTTP/1.1 200 Connection Established\r\n")
        self.wfile.write(f"Proxy-Agent: {PROXY_NAME}\r\n\r\n".encode())
        self.wfile.flush()

        try:
            moved = tunnel(self.connection, upstream)
        finally:
            try:
                upstream.close()
            except OSError:
                pass
        record(
            client=self.client_address[0],
            method="CONNECT",
            target=target,
            status="200 tunnel",
            bytes=moved,
            decision="ALLOW",
            reason=reason,
            cache="OFF",
        )


CONSOLE_HTML = r"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Egress Console — Forward Proxy</title>
<style>
  *{box-sizing:border-box}
  body{margin:0;min-height:100vh;color:#e9eeff;padding:30px 26px 46px;
    font-family:Inter,ui-sans-serif,system-ui,"Segoe UI",sans-serif;
    background:radial-gradient(circle at 12% 6%,rgba(94,132,255,.28),transparent 38%),
               radial-gradient(circle at 88% 92%,rgba(255,122,90,.20),transparent 40%),
               linear-gradient(150deg,#070a17,#111834 55%,#0a0f21)}
  .shell{width:min(1220px,100%);margin:0 auto}
  .eyebrow{font-size:12.5px;font-weight:800;letter-spacing:.2em;text-transform:uppercase;color:#93a6ff}
  h1{margin:12px 0 6px;font-size:clamp(30px,4.4vw,50px);letter-spacing:-.03em;line-height:1.05}
  h1 em{font-style:normal;color:#7ee7a8;text-shadow:0 0 40px rgba(126,231,168,.45)}
  .lead{color:#b6c1e4;font-size:17px;line-height:1.65;max-width:760px}
  .flow{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:12px;align-items:center;
    margin:26px 0 20px;padding:20px;border:1px solid rgba(255,255,255,.11);border-radius:20px;
    background:rgba(16,22,46,.66);backdrop-filter:blur(14px)}
  .node{text-align:center;padding:14px 10px;border-radius:16px;background:rgba(255,255,255,.05);
    border:1px solid rgba(255,255,255,.09)}
  .node .ico{font-size:30px;line-height:1}
  .node b{display:block;margin-top:8px;font-size:16px}
  .node s{display:block;text-decoration:none;color:#8fa0cd;font-size:12.5px;margin-top:3px;
    font-family:ui-monospace,Menlo,monospace}
  .node.proxy{border-color:rgba(126,231,168,.55);background:rgba(126,231,168,.09)}
  .node.proxy.deny{border-color:rgba(255,120,120,.7);background:rgba(255,90,90,.14)}
  .arrow{position:relative;height:4px;border-radius:3px;background:rgba(255,255,255,.13);min-width:52px}
  .arrow i{position:absolute;top:-3px;left:0;width:10px;height:10px;border-radius:50%;
    background:#7ee7a8;box-shadow:0 0 14px #7ee7a8;opacity:0}
  .arrow.run i{animation:slide .85s linear}
  .arrow.blocked{background:rgba(255,110,110,.4)}
  @keyframes slide{0%{left:0;opacity:1}100%{left:calc(100% - 10px);opacity:.15}}
  .tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:14px;margin-bottom:18px}
  .tile{padding:16px 18px;border-radius:16px;border:1px solid rgba(255,255,255,.1);
    background:rgba(16,22,46,.66)}
  .tile span{font-size:11.5px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:#8fa0cd}
  .tile b{display:block;margin-top:7px;font-size:28px;letter-spacing:-.02em}
  .tile.ok b{color:#7ee7a8} .tile.no b{color:#ff8a8a} .tile.lock b{color:#ffd479} .tile.hit b{color:#8ec5ff}
  .panel{border:1px solid rgba(255,255,255,.1);border-radius:20px;background:rgba(13,18,38,.74);overflow:hidden}
  .panel header{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between;
    padding:15px 20px;border-bottom:1px solid rgba(255,255,255,.09)}
  .panel h2{font-size:17px;margin:0}
  .chips{display:flex;flex-wrap:wrap;gap:7px}
  .chip{font:700 12px/1 ui-monospace,Menlo,monospace;padding:6px 10px;border-radius:999px;
    background:rgba(255,255,255,.07);color:#c6d1f2;border:1px solid rgba(255,255,255,.1)}
  .chip.deny{background:rgba(255,90,90,.16);color:#ffb3b3;border-color:rgba(255,90,90,.35)}
  .chip.on{background:rgba(126,231,168,.15);color:#9ff0c0;border-color:rgba(126,231,168,.35)}
  button{border:0;border-radius:12px;padding:10px 16px;font-size:13.5px;font-weight:800;cursor:pointer;
    color:#08122a;background:linear-gradient(120deg,#7ee7a8,#8ec5ff)}
  table{width:100%;border-collapse:collapse;font-size:14px}
  th{position:sticky;top:0;background:#101733;text-align:left;padding:11px 14px;font-size:11.5px;
    letter-spacing:.12em;text-transform:uppercase;color:#8fa0cd;border-bottom:1px solid rgba(255,255,255,.09)}
  td{padding:10px 14px;border-bottom:1px solid rgba(255,255,255,.05);vertical-align:middle}
  tbody tr:hover{background:rgba(255,255,255,.035)}
  .wrap{max-height:430px;overflow:auto}
  .tag{display:inline-block;font:800 11.5px/1 ui-monospace,Menlo,monospace;padding:5px 9px;border-radius:7px}
  .tag.allow{background:rgba(126,231,168,.16);color:#9ff0c0}
  .tag.deny{background:rgba(255,90,90,.18);color:#ffb0b0}
  .tag.error{background:rgba(255,212,121,.16);color:#ffd479}
  .mono{font-family:ui-monospace,Menlo,monospace;color:#cfd8f6}
  .muted{color:#8fa0cd}
  .empty{padding:38px;text-align:center;color:#8fa0cd}
  .foot{margin-top:16px;color:#8695c0;font-size:13.5px;line-height:1.7}
  @media(max-width:820px){.flow{grid-template-columns:1fr;}.arrow{height:22px;width:4px;margin:0 auto}}
</style>
</head>
<body>
<main class="shell">
  <div class="eyebrow">LAB 6 · Forward Proxy · Egress Console</div>
  <h1>ทุก request ที่ออกจากออฟฟิศ <em>ผ่านตรงนี้</em></h1>
  <p class="lead">นี่คือมุมมองของ <b>ผู้ดูแลเครือข่าย</b> ไม่ใช่ของเจ้าของเว็บ — forward proxy ยืนอยู่ข้าง client
     จึงเห็นว่าใครจะออกไปที่ไหน อนุญาตหรือบล็อกได้ที่จุดเดียว และเห็นว่า HTTPS นั้นเห็นได้แค่ชื่อโฮสต์</p>

  <section class="flow">
    <div class="node"><div class="ico">💻</div><b>client</b><s id="clientNet">officenet</s></div>
    <div class="arrow" id="arrowA"><i></i></div>
    <div class="node proxy" id="proxyNode"><div class="ico">🛡️</div><b id="proxyName">forward proxy</b><s>:8888</s></div>
    <div class="arrow" id="arrowB"><i></i></div>
    <div class="node"><div class="ico">🌐</div><b>อินเทอร์เน็ต</b><s id="lastTarget">รอ request แรก…</s></div>
  </section>

  <section class="tiles">
    <div class="tile ok"><span>ผ่าน (ALLOW)</span><b id="sAllow">0</b></div>
    <div class="tile no"><span>ถูกบล็อก (DENY)</span><b id="sDeny">0</b></div>
    <div class="tile lock"><span>อุโมงค์ CONNECT</span><b id="sConnect">0</b></div>
    <div class="tile hit"><span>Cache HIT</span><b id="sHit">0</b></div>
    <div class="tile"><span>ไบต์ที่ผ่าน proxy</span><b id="sBytes">0</b></div>
  </section>

  <section class="panel">
    <header>
      <h2>Egress log — ล่าสุดอยู่บนสุด</h2>
      <div class="chips" id="policy"></div>
      <button id="toggle">⏸ หยุด auto-refresh</button>
    </header>
    <div class="wrap">
      <table>
        <thead><tr><th>เวลา</th><th>client</th><th>เมธอด</th><th>ปลายทาง</th><th>ผล</th><th>สถานะ</th><th>ไบต์</th></tr></thead>
        <tbody id="rows"><tr><td colspan="7" class="empty">ยังไม่มี request — ลองรัน <span class="mono">curl -x http://proxy:8888 http://news.lab/</span> จากเครื่อง client</td></tr></tbody>
      </table>
    </div>
  </section>

  <p class="foot">🔒 แถวที่เป็น <b>CONNECT</b> คือ HTTPS — proxy เห็นแค่ <span class="mono">host:443</span>
     ไม่เห็น path ไม่เห็นเนื้อหา เพราะ TLS ถูกเข้ารหัสตั้งแต่ client ถึงปลายทาง ·
     เทียบกับ reverse proxy ที่ยืนฝั่งเซิร์ฟเวอร์: มันถอด TLS เองจึงเห็นทุกอย่าง</p>
</main>
<script>
  let auto = true, lastId = 0;
  const $ = (id) => document.getElementById(id);
  const fmt = (n) => n.toLocaleString('en-US');
  // ค่าทุกตัวในตารางมาจาก request ของผู้ใช้ จึงต้อง escape ก่อนเสมอ (กัน XSS)
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) =>
    ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

  function pulse(deny) {
    const a = $('arrowA'), b = $('arrowB'), p = $('proxyNode');
    a.classList.remove('run'); b.classList.remove('run'); void a.offsetWidth;
    a.classList.add('run');
    b.classList.toggle('blocked', deny);
    p.classList.toggle('deny', deny);
    if (!deny) { void b.offsetWidth; b.classList.add('run'); }
    setTimeout(() => p.classList.remove('deny'), 900);
  }

  async function tick() {
    try {
      const res = await fetch('/api/log', { cache: 'no-store' });
      const data = await res.json();
      $('proxyName').textContent = data.policy.name;   // textContent ปลอดภัยอยู่แล้ว
      $('sAllow').textContent = fmt(data.stats.allow);
      $('sDeny').textContent = fmt(data.stats.deny);
      $('sConnect').textContent = fmt(data.stats.connect);
      $('sHit').textContent = fmt(data.stats.cache_hit);
      $('sBytes').textContent = fmt(data.stats.bytes);

      const chips = [];
      chips.push(`<span class="chip ${data.policy.cache_ttl > 0 ? 'on' : ''}">cache ttl: ${data.policy.cache_ttl}s</span>`);
      if (data.policy.allow.length) chips.push(`<span class="chip on">allowlist: ${esc(data.policy.allow.join(' '))}</span>`);
      if (data.policy.deny.length) data.policy.deny.forEach(h => chips.push(`<span class="chip deny">blocked: ${esc(h)}</span>`));
      if (!data.policy.deny.length && !data.policy.allow.length) chips.push('<span class="chip">ยังไม่มีนโยบายบล็อก</span>');
      $('policy').innerHTML = chips.join('');

      const rows = data.events.map(e => {
        const cls = e.decision === 'ALLOW' ? 'allow' : (e.decision === 'DENY' ? 'deny' : 'error');
        const lock = e.method === 'CONNECT' ? '🔒 ' : '';
        const cache = e.cache && e.cache !== 'OFF' ? ` <span class="muted">· cache ${esc(e.cache)}</span>` : '';
        return `<tr><td class="mono">${esc(e.time)}</td><td class="mono">${esc(e.client)}</td>` +
               `<td class="mono">${esc(e.method)}</td><td class="mono">${lock}${esc(e.target)}${cache}</td>` +
               `<td><span class="tag ${cls}">${esc(e.decision)}</span></td>` +
               `<td class="mono">${esc(e.status)}</td><td class="mono">${fmt(e.bytes || 0)}</td></tr>`;
      }).join('');
      $('rows').innerHTML = rows || '<tr><td colspan="7" class="empty">ยังไม่มี request</td></tr>';

      if (data.events.length && data.events[0].id !== lastId) {
        if (lastId !== 0) pulse(data.events[0].decision === 'DENY');
        lastId = data.events[0].id;
        $('lastTarget').textContent = data.events[0].target;   // textContent ไม่ต้อง escape
      }
    } catch (err) { /* console ยังไม่พร้อม — รอบหน้าลองใหม่ */ }
  }

  $('toggle').addEventListener('click', () => {
    auto = !auto;
    $('toggle').textContent = auto ? '⏸ หยุด auto-refresh' : '▶ เล่น auto-refresh';
  });
  setInterval(() => { if (auto) tick(); }, 1000);
  tick();
</script>
</body>
</html>
"""


class ConsoleHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "LabProxyConsole/1.0"
    sys_version = ""

    def log_message(self, fmt, *args):
        return

    def _send(self, status, content_type, payload):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        if self.path.startswith("/api/log"):
            with LOCK:
                payload = json.dumps(
                    {
                        "policy": {
                            "name": PROXY_NAME,
                            "deny": list(DENY),
                            "allow": list(ALLOW),
                            "cache_ttl": CACHE_TTL,
                            "uptime": int(time.time() - START_TIME),
                        },
                        "stats": dict(STATS),
                        "events": list(EVENTS)[:120],
                    },
                    ensure_ascii=False,
                ).encode("utf-8")
            self._send(200, "application/json; charset=utf-8", payload)
            return
        if self.path in ("/", "/index.html"):
            self._send(200, "text/html; charset=utf-8", CONSOLE_HTML.encode("utf-8"))
            return
        self._send(404, "text/plain; charset=utf-8", b"not found\n")


def main():
    console = ThreadingHTTPServer(("0.0.0.0", UI_PORT), ConsoleHandler)
    threading.Thread(target=console.serve_forever, daemon=True).start()

    proxy = ThreadingHTTPServer(("0.0.0.0", PROXY_PORT), ForwardProxyHandler)
    print(
        f"[{PROXY_NAME}] forward proxy listening on :{PROXY_PORT} · "
        f"egress console on :{UI_PORT} · deny={list(DENY) or '-'} "
        f"allow={list(ALLOW) or '-'} cache_ttl={CACHE_TTL}s",
        flush=True,
    )
    try:
        proxy.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
