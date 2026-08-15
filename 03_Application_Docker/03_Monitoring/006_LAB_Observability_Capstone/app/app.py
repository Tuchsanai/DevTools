#!/usr/bin/env python3
"""
LAB 6 — แอปตัวอย่างที่ติดเครื่องมือวัด (instrumented app)

ออกแบบให้ "ผลลัพธ์เดาได้" เพื่อให้ check.sh ไม่ flaky:
  - หนึ่ง process เท่านั้น (ThreadingHTTPServer) → prometheus_client นับได้ตรง
  - /api/error ตอบ 500 แบบนับรอบ (ทุก ๆ ERROR_EVERY ครั้ง) ไม่ใช่สุ่ม
  - หน่วงเวลาแต่ละ endpoint วนตามลิสต์คงที่ ไม่ใช่สุ่ม

metric ที่ปล่อยออกมา (RED):
  app_requests_total{method,endpoint,status}   Counter  → Rate / Errors
  app_request_duration_seconds{endpoint}       Histogram → Duration
  app_inflight_requests                        Gauge
  app_build_info{version}                      Gauge (ค่า 1 เสมอ ใช้พก label)
"""
import itertools
import os
import re
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

PORT = int(os.environ.get("APP_PORT", "8000"))
VERSION = os.environ.get("APP_VERSION", "1.0.0")
# ทุก ๆ ERROR_EVERY ครั้งที่มีคนเรียก /api/error จะตอบ 500 หนึ่งครั้ง (2 = ครึ่งหนึ่ง)
ERROR_EVERY = max(1, int(os.environ.get("ERROR_EVERY", "2")))

REQUESTS = Counter(
    "app_requests_total",
    "จำนวน request ที่แอปตอบไปแล้วทั้งหมด แยกตาม method/endpoint/status",
    ["method", "endpoint", "status"],
)
LATENCY = Histogram(
    "app_request_duration_seconds",
    "เวลาที่ใช้ตอบแต่ละ request (วินาที)",
    ["endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)
INFLIGHT = Gauge("app_inflight_requests", "จำนวน request ที่กำลังประมวลผลอยู่ ณ ขณะนี้")
BUILD = Gauge("app_build_info", "ข้อมูลเวอร์ชันของแอป (ค่าเป็น 1 เสมอ)", ["version"])
BUILD.labels(version=VERSION).set(1)

# path ดิบ -> ชื่อ endpoint แบบ template  (กัน cardinality ระเบิด)
ITEM_ID_RE = re.compile(r"^/api/items/[^/]+$")

# หน่วงเวลาแบบวนลิสต์ = deterministic
DELAYS = {
    "/": itertools.cycle([0.002]),
    "/api/items": itertools.cycle([0.03, 0.06, 0.09, 0.12, 0.05]),
    "/api/items/:id": itertools.cycle([0.02, 0.04]),
    "/api/error": itertools.cycle([0.01]),
    "/api/slow": itertools.cycle([0.8, 1.6]),
}

_lock = threading.Lock()
_error_hits = 0
_started = time.time()


def endpoint_of(path: str) -> str:
    if path == "/":
        return "/"
    if path == "/api/items":
        return "/api/items"
    if path == "/api/slow":
        return "/api/slow"
    if path == "/api/error":
        return "/api/error"
    if ITEM_ID_RE.match(path):
        return "/api/items/:id"
    return "unknown"


def next_delay(endpoint: str) -> float:
    cyc = DELAYS.get(endpoint)
    if cyc is None:
        return 0.001
    with _lock:
        return next(cyc)


def handle(endpoint: str):
    """คืน (status_code, body_bytes)"""
    global _error_hits
    time.sleep(next_delay(endpoint))

    if endpoint == "unknown":
        return 404, b'{"error":"not found"}'

    if endpoint == "/api/error":
        with _lock:
            _error_hits += 1
            hit = _error_hits
        if hit % ERROR_EVERY == 0:
            return 500, b'{"error":"upstream exploded","simulated":true}'
        return 200, b'{"ok":true,"note":"this call got lucky"}'

    if endpoint == "/":
        body = (
            '{"app":"monlab6-app","version":"%s","uptime_seconds":%.1f,'
            '"endpoints":["/","/api/items","/api/items/:id","/api/slow","/api/error","/metrics"]}'
            % (VERSION, time.time() - _started)
        )
        return 200, body.encode()

    if endpoint == "/api/items":
        return 200, b'{"items":[{"id":1,"name":"cpu"},{"id":2,"name":"ram"},{"id":3,"name":"disk"}]}'

    if endpoint == "/api/items/:id":
        return 200, b'{"item":{"id":"<templated>","name":"one item"}}'

    if endpoint == "/api/slow":
        return 200, b'{"ok":true,"note":"slow report generated"}'

    return 200, b"{}"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "monlab6-app"

    def log_message(self, *args):  # เงียบไว้ ไม่งั้น log ท่วมจาก loadgen
        pass

    def _send(self, status, body, ctype="application/json; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]

        # /metrics และ /healthz ไม่ถูกนับเป็น traffic ของแอป (ไม่งั้น RED เพี้ยนเพราะ Prometheus เอง)
        if path == "/metrics":
            payload = generate_latest()
            self._send(200, payload, CONTENT_TYPE_LATEST)
            return
        if path == "/healthz":
            self._send(200, b'{"status":"ok"}')
            return

        endpoint = endpoint_of(path)
        INFLIGHT.inc()
        start = time.perf_counter()
        # ตั้งผลลัพธ์ตั้งต้นเป็น 500 ไว้ก่อน ถ้า handle() ระเบิดกลางทางเราจะยัง "ตอบ" และ "นับ" ครบ
        status = 500
        body = b'{"error":"internal error"}'
        try:
            status, body = handle(endpoint)
        except Exception:
            # การนับต้องเกิดกับ *ทุก* request ไม่ใช่เฉพาะ request ที่รอด
            # ถ้านับไว้นอก finally แล้วเกิด exception ตัว error จะหายไปทั้งจากตัวตั้งและตัวหาร
            # ทำให้ error ratio ที่เห็นบน dashboard ต่ำกว่าความจริง (ยิ่งพังยิ่งดูดี)
            traceback.print_exc()
        finally:
            elapsed = time.perf_counter() - start
            LATENCY.labels(endpoint=endpoint).observe(elapsed)
            REQUESTS.labels(method="GET", endpoint=endpoint, status=str(status)).inc()
            INFLIGHT.dec()
        self._send(status, body)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"monlab6-app {VERSION} listening on 0.0.0.0:{PORT} (ERROR_EVERY={ERROR_EVERY})", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
