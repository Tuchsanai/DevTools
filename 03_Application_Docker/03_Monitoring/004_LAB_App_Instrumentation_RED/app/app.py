"""
LAB 4 — แอปตัวอย่างที่ "ติดมิเตอร์" ไว้ในตัวเอง (application instrumentation)

ใช้ http.server ของ Python stdlib ล้วน ๆ เพื่อให้เห็นชัดว่า "จุดวัด" อยู่ตรงไหน
ของ request lifecycle — ไม่มี framework มาซ่อน middleware ให้

metric ที่ประกาศไว้ (ชื่อเหล่านี้ถูกใช้ต่อใน LAB 5 และ LAB 6 ด้วย):
  app_requests_total{method,endpoint,status}   Counter   -> R (Rate) และ E (Errors)
  app_request_duration_seconds{endpoint}       Histogram -> D (Duration)
  app_inflight_requests                        Gauge     -> งานที่กำลังค้างอยู่ในมือ
  app_build_info{version}                      Gauge     -> ค่าคงที่ 1 ไว้ผูกเวอร์ชัน

หมายเหตุสำคัญ: แอปนี้ "ไม่สุ่มเลย" — เวลาหน่วงของแต่ละ endpoint วนตามตารางคงที่
และ /api/error ตอบ 500 ตามสัดส่วนที่นับรอบได้ ดังนั้นตัวเลข RED ที่ทุกคนวัดได้
จะใกล้เคียงกันทั้งห้อง ไม่ใช่ "แล้วแต่ดวง"
"""

import os
import re
import threading
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from prometheus_client import CONTENT_TYPE_LATEST, REGISTRY, Counter, Gauge, Histogram, generate_latest

# ---------------------------------------------------------------- config (env)
PORT = int(os.environ.get("PORT", "8000"))
APP_VERSION = os.environ.get("APP_VERSION", "1.0.0")
# สัดส่วนที่ /api/error จะตอบ 500 (0.5 = ทุก ๆ 2 request จะพัง 1 ครั้ง "พอดี")
ERROR_RATE = float(os.environ.get("ERROR_RATE", "0.5"))
# 1 = ใช้ path ดิบเป็น label (ของเสีย! ใช้สาธิต cardinality ระเบิดเท่านั้น)
RAW_PATH_LABEL = os.environ.get("RAW_PATH_LABEL", "0") == "1"

# ------------------------------------------------------------------- metrics
# Counter = ตัวเลขที่ "ขึ้นอย่างเดียว" ตอบคำถาม "เกิดขึ้นไปแล้วกี่ครั้ง"
# หมายเหตุ: prometheus_client ตัด suffix _total ออกจากชื่อที่เราตั้ง แล้วเติมกลับให้เอง
REQUESTS = Counter(
    "app_requests_total",
    "จำนวน HTTP request ทั้งหมดที่แอปนี้ตอบไปแล้ว",
    ["method", "endpoint", "status"],
)

# Histogram = แจกแจงค่าที่วัดได้ลงถัง (bucket) ตอบคำถาม "ช้าแค่ไหน" แบบมี percentile
# ขอบถังต้องเลือกให้ครอบเวลาจริงของแอป ไม่งั้น p95 จะเพี้ยน
DURATION = Histogram(
    "app_request_duration_seconds",
    "เวลาที่ใช้ตอบ 1 request (วินาที)",
    ["endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# Gauge = ตัวเลขที่ "ขึ้นลงได้" ตอบคำถาม "ตอนนี้เป็นเท่าไร"
INFLIGHT = Gauge(
    "app_inflight_requests",
    "จำนวน request ที่กำลังประมวลผลอยู่ ณ ขณะนี้",
)

# Gauge ค่าคงที่ 1 ที่มี label เป็นเวอร์ชัน — สูตรมาตรฐานสำหรับ "ข้อมูลที่ไม่ใช่ตัวเลข"
BUILD_INFO = Gauge(
    "app_build_info",
    "ข้อมูลบิลด์ของแอป (ค่าเป็น 1 เสมอ ความหมายอยู่ที่ label)",
    ["version"],
)
BUILD_INFO.labels(version=APP_VERSION).set(1)

# ------------------------------------------------- ตารางหน่วงเวลาแบบไม่สุ่ม
# แต่ละ endpoint วนใช้ค่าในตารางตามลำดับ -> รันกี่รอบก็ได้ผลเหมือนเดิม
LATENCY_TABLE = {
    "/api/items": (0.020, 0.045, 0.070, 0.095, 0.120),      # งานปกติ 20-120 ms
    "/api/items/:id": (0.010, 0.030, 0.050),                 # อ่านรายตัว เร็วกว่า list
    "/api/error": (0.010, 0.020, 0.030),                     # พังเร็ว ไม่หน่วง
    "/api/slow": (0.7, 1.1, 1.5, 1.9),                       # งานหนัก 0.6-2.0 s
}
_state_lock = threading.Lock()
_cursor = {key: 0 for key in LATENCY_TABLE}
_error_budget = 0.0  # ตัวสะสมสำหรับตัดสินใจว่า request นี้ต้องพังหรือไม่


def next_delay(key: str) -> float:
    """ดึงค่าหน่วงถัดไปของ endpoint นั้นแบบวนลูป (thread-safe)"""
    table = LATENCY_TABLE[key]
    with _state_lock:
        idx = _cursor[key]
        _cursor[key] = (idx + 1) % len(table)
    return table[idx]


def should_fail() -> bool:
    """คืน True ตามสัดส่วน ERROR_RATE แบบ "นับรอบ" ไม่ใช่โยนเหรียญ

    บวก ERROR_RATE เข้าไปในกระปุกทุกครั้งที่มีคนเรียก พอครบ 1 ก็จ่าย error 1 ใบ
    ผลคือได้สัดส่วนตรงเป๊ะ: ERROR_RATE=0.5 -> พัง 1 ใน 2 ครั้ง สลับกันเป๊ะ ๆ
    """
    global _error_budget
    with _state_lock:
        _error_budget += ERROR_RATE
        if _error_budget >= 1.0:
            _error_budget -= 1.0
            return True
    return False


# ------------------------------------------------------------ endpoint label
ITEM_ID_PATH = re.compile(r"^/api/items/[^/]+$")
KNOWN_PATHS = {"/", "/api/items", "/api/slow", "/api/error", "/healthz"}


def endpoint_label(path: str) -> str:
    """แปลง path จริงให้เป็น 'ชื่อ route' ที่มีจำนวนจำกัด

    หัวใจของแล็บนี้: label ต้องมีค่าที่เป็นไปได้ "นับได้" ไม่ใช่ไม่จำกัด
    /api/items/1, /api/items/2, ... ต้องยุบเป็น /api/items/:id ตัวเดียว
    """
    if RAW_PATH_LABEL:
        return path  # โหมดของเสีย: label = path ดิบ -> 1 id = 1 series
    if path in KNOWN_PATHS:
        return path
    if ITEM_ID_PATH.match(path):
        return "/api/items/:id"
    return "/other"  # path ที่ไม่รู้จักยุบรวมเป็นถังเดียว กัน 404 flood สร้าง series


# -------------------------------------------------------------------- routes
def route(path: str):
    """คืน (status_code, body) พร้อมจำลองพฤติกรรมของแต่ละ endpoint"""
    if path == "/":
        return 200, b'{"service":"monlab4-app","hint":"try /api/items"}\n'

    if path == "/healthz":
        return 200, b'{"status":"ok"}\n'

    if path == "/api/items":
        time.sleep(next_delay("/api/items"))
        return 200, b'{"items":["cpu","ram","disk"],"count":3}\n'

    if path == "/api/slow":
        time.sleep(next_delay("/api/slow"))
        return 200, b'{"report":"generated","rows":10000}\n'

    if path == "/api/error":
        time.sleep(next_delay("/api/error"))
        if should_fail():
            return 500, b'{"error":"upstream exploded"}\n'
        return 200, b'{"error":null}\n'

    if ITEM_ID_PATH.match(path):
        time.sleep(next_delay("/api/items/:id"))
        item_id = path.rsplit("/", 1)[-1]
        return 200, ('{"id":"%s","name":"item-%s"}\n' % (item_id, item_id)).encode()

    return 404, b'{"error":"not found"}\n'


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "monlab4app/1.0"

    def log_message(self, fmt, *args):  # ปิด access log ไม่ให้ท่วม terminal ตอนยิงโหลด
        pass

    def _send(self, status: int, body: bytes, ctype: str = "application/json"):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path

        # /metrics ไม่นับเป็น traffic ของแอป จึงไม่วัดตัวเอง (กัน Prometheus ปั่นตัวเลข RED)
        if path == "/metrics":
            self._send(200, generate_latest(REGISTRY), CONTENT_TYPE_LATEST)
            return

        endpoint = endpoint_label(path)

        # ---- จุดวัดที่ 1: ก่อนเริ่มงาน -> gauge +1 และเริ่มจับเวลา
        INFLIGHT.inc()
        started = time.perf_counter()
        status = 500  # กันเหนียวกรณีสุดวิสัยที่หลุดมาถึง finally โดยยังไม่ได้ค่า
        try:
            try:
                status, body = route(path)
            except Exception:
                # งานพังกลางทาง -> ต้อง "ตอบ 500 กลับไปให้ client จริง ๆ" ไม่ใช่แค่นับเป็น 500
                # ถ้าปล่อยให้ exception หลุดขึ้นไป client จะได้แค่ connection ที่ถูกปิดเปล่า ๆ
                # แล้วตัวเลขใน metric จะไม่ตรงกับสิ่งที่ผู้ใช้เจอจริง — ซึ่งอันตรายกว่าไม่มี metric
                traceback.print_exc()
                status, body = 500, b'{"error":"internal error"}\n'
            self._send(status, body)
        finally:
            # ---- จุดวัดที่ 2: หลังงานจบ (แม้จะ exception) -> observe / inc / dec
            elapsed = time.perf_counter() - started
            DURATION.labels(endpoint=endpoint).observe(elapsed)
            REQUESTS.labels(method="GET", endpoint=endpoint, status=str(status)).inc()
            INFLIGHT.dec()


def main():
    mode = "RAW PATH (cardinality demo)" if RAW_PATH_LABEL else "TEMPLATE (/api/items/:id)"
    print(f"monlab4-app v{APP_VERSION} listening on :{PORT}", flush=True)
    print(f"  endpoint label mode = {mode}", flush=True)
    print(f"  ERROR_RATE = {ERROR_RATE}", flush=True)
    # process เดียว เธรดหลายเส้น: registry ของ prometheus_client จึงมีชุดเดียว
    # (ถ้าแตกเป็นหลาย worker process counter จะกระโดดไปมาเพราะแต่ละ process นับของตัวเอง)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
