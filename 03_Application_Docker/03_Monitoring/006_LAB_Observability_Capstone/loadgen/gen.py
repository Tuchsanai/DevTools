#!/usr/bin/env python3
"""
LAB 6 — ตัวยิงโหลด (load generator)

ยิงตาม "รอบคงที่" ยาว 20 request แทนการสุ่ม เพื่อให้สัดส่วนที่ Prometheus เห็น
เท่ากันทุกเครื่องและทุกครั้งที่รัน:

    /               x7
    /api/items      x5
    /api/items/<id> x2
    /api/error      x4   -> แอปตอบ 500 ครึ่งหนึ่ง (ERROR_EVERY=2) = 2 error ต่อ 20 request = 10%
    /api/slow       x2   -> 10% ของ request ช้า 0.8/1.6 วินาที ทำให้ p95 อยู่ราว 1 วินาที
                            ซึ่งเกินเกณฑ์ของ alert HighLatencyP95 ที่ตั้งไว้ 0.75 วินาที

ตัวเลข 10% นี้คือเหตุผลที่ alert HighErrorRate (เกณฑ์ 5%) ต้องยิงเมื่อ expr ถูกต้อง

สถิติที่พิมพ์ออกมาแยก 2xx / 4xx / 5xx / ต่อไม่ติด ออกจากกัน เพราะ "ไม่ 5xx" ไม่ได้แปลว่า "สำเร็จ"
— 404 ที่นับรวมเป็นสำเร็จคือวิธีที่ทำให้ dashboard ดูดีกว่าความจริง
"""
import itertools
import os
import threading
import time
import urllib.error
import urllib.request

TARGET = os.environ.get("TARGET", "http://app:8000")
WORKERS = max(1, int(os.environ.get("WORKERS", "3")))
PACE = float(os.environ.get("PACE", "0.12"))  # หน่วงต่อ request ต่อ worker (วินาที)

CYCLE = (
    ["/"] * 7
    + ["/api/items"] * 5
    + ["/api/items/101", "/api/items/202"]
    + ["/api/error"] * 4
    + ["/api/slow"] * 2
)

_it = itertools.cycle(CYCLE)
_lock = threading.Lock()
_stats = {"sent": 0, "ok2xx": 0, "err4xx": 0, "err5xx": 0, "fail": 0}


def next_path() -> str:
    with _lock:
        return next(_it)


def bump(key: str) -> None:
    with _lock:
        _stats[key] += 1


def wait_for_app(timeout: int = 120) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{TARGET}/healthz", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(1)
    return False


def worker() -> None:
    while True:
        path = next_path()
        bump("sent")
        try:
            with urllib.request.urlopen(f"{TARGET}{path}", timeout=10) as r:
                r.read()
                bump("ok2xx" if r.status < 300 else "err4xx")
        except urllib.error.HTTPError as e:
            e.read()
            # แยก 4xx ออกจาก 5xx เสมอ — 404 ไม่ใช่ความสำเร็จ และไม่ใช่ปัญหาชนิดเดียวกับ 500
            bump("err5xx" if e.code >= 500 else "err4xx")
        except Exception:
            bump("fail")
        time.sleep(PACE)


def main() -> None:
    print(f"loadgen -> {TARGET} workers={WORKERS} pace={PACE}s", flush=True)
    if not wait_for_app():
        print("แอปยังไม่ตอบ /healthz ภายใน 120 วินาที — ยิงต่อไปแบบไม่รอ", flush=True)

    for _ in range(WORKERS):
        threading.Thread(target=worker, daemon=True).start()

    last = dict(_stats)
    while True:
        time.sleep(15)
        with _lock:
            now = dict(_stats)
        delta = now["sent"] - last["sent"]
        print(
            "15s ที่ผ่านมา: sent=%d (%.1f rps) 2xx=%d 4xx=%d 5xx=%d ต่อไม่ติด=%d | รวมทั้งหมด sent=%d"
            % (delta, delta / 15.0,
               now["ok2xx"] - last["ok2xx"], now["err4xx"] - last["err4xx"],
               now["err5xx"] - last["err5xx"], now["fail"] - last["fail"], now["sent"]),
            flush=True,
        )
        last = now


if __name__ == "__main__":
    main()
