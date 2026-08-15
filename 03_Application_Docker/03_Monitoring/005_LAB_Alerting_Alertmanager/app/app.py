#!/usr/bin/env python3
"""
LAB 5 — แอปตัวอย่างที่ติด metric แบบ RED (สำเนาในตัวเองของแล็บนี้)

ชื่อ metric ต้องตรงกับ LAB 4 เพื่อให้ alert rule ใช้ query ชุดเดียวกันได้:
  - app_requests_total{method,endpoint,status}     Counter
  - app_request_duration_seconds{endpoint}         Histogram
  - app_inflight_requests                          Gauge

หมายเหตุการออกแบบ:
  * ใช้ http.server ของ stdlib เพื่อให้เห็น "จุดวัด" ชัด ๆ ในโค้ด ไม่ถูกซ่อนใน framework
  * เป็น process เดียว (registry เดียว) ตัวเลข metric จึงไม่แตกตาม worker
    แต่ใช้ ThreadingHTTPServer เพราะ /api/slow หน่วงได้ถึง 2 วินาที
    ถ้าเป็น single thread ล้วน การ scrape /metrics จะถูกบล็อกจน scrape timeout
  * /api/error ตอบ 500 แบบ "นับรอบ" ไม่ใช่สุ่ม เพื่อให้ error ratio คาดเดาได้
    และ alert ยิงตรงเวลาในคาบเรียน
"""

import json
import os
import random
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

PORT = int(os.getenv("PORT", "8000"))
# สัดส่วนของ request ที่เข้า /api/error แล้วได้ 500 (0.0-1.0) — ทำงานแบบนับรอบ ไม่สุ่ม
ERROR_RATE = float(os.getenv("ERROR_RATE", "1.0"))
SEED = int(os.getenv("SEED", "2569"))

BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)

REQUESTS = Counter(
    "app_requests_total",
    "Total HTTP requests handled by the app",
    ["method", "endpoint", "status"],
)
DURATION = Histogram(
    "app_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"],
    buckets=BUCKETS,
)
INFLIGHT = Gauge(
    "app_inflight_requests",
    "Number of requests currently being processed",
)

_rng = random.Random(SEED)
_rng_lock = threading.Lock()
_error_counter = 0
_error_lock = threading.Lock()


def jitter(low: float, high: float) -> float:
    """สุ่มเวลาหน่วงแบบ thread-safe ด้วย seed คงที่ ผลจึงใกล้เคียงกันทุกเครื่อง"""
    with _rng_lock:
        return _rng.uniform(low, high)


def should_fail() -> bool:
    """ตอบ 500 แบบนับรอบ: ทุก 10 request จะ fail จำนวน round(ERROR_RATE*10) ครั้ง"""
    global _error_counter
    fail_per_10 = int(round(max(0.0, min(1.0, ERROR_RATE)) * 10))
    with _error_lock:
        slot = _error_counter % 10
        _error_counter += 1
    return slot < fail_per_10


def route_template(path: str) -> str:
    """แปลง path ดิบเป็น template — กัน cardinality ระเบิดจาก id ที่ไม่ซ้ำ"""
    if path in ("/", "/api/items", "/api/slow", "/api/error", "/healthz", "/metrics"):
        return path
    if path.startswith("/api/items/"):
        return "/api/items/:id"
    return "/404"


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "monlab5-app"
    sys_version = ""

    def log_message(self, fmt, *args):  # ปิด access log ให้ log ของแล็บอ่านง่าย
        pass

    # ---------- ตัวแอปจริง ----------
    def business_logic(self, endpoint: str):
        # /healthz ถูกนับเข้า RED เหมือน endpoint อื่น ๆ (สัญญาเดียวกับ LAB 4)
        if endpoint == "/healthz":
            return 200, {"status": "ok"}
        if endpoint == "/":
            return 200, {"service": "monlab5-app", "hint": "ลอง /api/items /api/slow /api/error"}
        if endpoint == "/api/items":
            time.sleep(jitter(0.02, 0.12))
            return 200, {"items": [{"id": i, "name": f"item-{i}"} for i in range(1, 6)]}
        if endpoint == "/api/slow":
            time.sleep(jitter(0.6, 2.0))
            return 200, {"result": "งานหนักเสร็จแล้ว"}
        if endpoint == "/api/error":
            time.sleep(jitter(0.01, 0.05))
            if should_fail():
                return 500, {"error": "upstream dependency failed"}
            return 200, {"result": "รอดไปได้"}
        if endpoint == "/api/items/:id":
            time.sleep(jitter(0.01, 0.06))
            return 200, {"id": self.path.rsplit("/", 1)[-1]}
        return 404, {"error": "not found"}

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        endpoint = route_template(path)

        # มีแค่ /metrics ที่ไม่นับเข้า RED — ไม่งั้นตัว scraper เองจะไปเจือจางตัวเลข
        # (สัญญาข้อนี้ต้องตรงกับ LAB 4 เป๊ะ ๆ เพราะสองแล็บใช้ชื่อ metric ชุดเดียวกัน:
        #  นับทุก request ยกเว้น /metrics · จับเวลาครอบถึงตอนเขียน response เสร็จ)
        if endpoint == "/metrics":
            body = generate_latest()
            self.send_response(200)
            self.send_header("Content-Type", CONTENT_TYPE_LATEST)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        INFLIGHT.inc()                       # Gauge: ขึ้นตอนเริ่ม ลงตอนจบ
        started = time.perf_counter()
        status = 500  # กันเหนียว เผื่อหลุดถึง finally โดยยังไม่ได้ค่า
        try:
            try:
                status, payload = self.business_logic(endpoint)
            except Exception:
                # งานพังกลางทาง -> ต้องตอบ 500 กลับไปให้ client จริง ๆ ไม่ใช่แค่นับเป็น 500
                traceback.print_exc()
                status, payload = 500, {"error": "internal error"}
            self.write_json(status, payload)
        finally:
            # ทั้งสามมิเตอร์อยู่ใน finally ด้วยกัน: request ที่พังกลางทางก็ยังถูกนับครบ
            # ถ้า REQUESTS.inc() หลุดออกไปอยู่นอก try/finally แล้ว business_logic โยน exception
            # เราจะได้ duration กับ inflight ที่ถูก แต่ "จำนวน request" หายไปเงียบ ๆ -> error ratio ต่ำกว่าจริง
            elapsed = time.perf_counter() - started
            DURATION.labels(endpoint=endpoint).observe(elapsed)   # Histogram: .observe()
            REQUESTS.labels(method="GET", endpoint=endpoint, status=str(status)).inc()  # Counter: .inc()
            INFLIGHT.dec()

    def write_json(self, status: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True
    print(f"[app] listening on :{PORT} ERROR_RATE={ERROR_RATE} SEED={SEED}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
