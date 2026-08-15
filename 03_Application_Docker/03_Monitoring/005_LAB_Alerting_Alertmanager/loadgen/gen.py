#!/usr/bin/env python3
"""
LAB 5 — ตัวยิงโหลด (load generator)

หน้าที่: ยิง request เข้าแอปด้วยอัตราคงที่ เพื่อให้ metric ขยับตลอดเวลา
และ "กระตุ้น" ให้ alert ยิงได้ภายในไม่กี่สิบวินาที

env ที่ปรับได้:
  TARGET_URL  ปลายทาง (default http://app:8000)
  RPS         request ต่อวินาที (default 8)
  ERROR_MIX   สัดส่วน request ที่ยิงไป /api/error   (0.0-1.0)
  SLOW_MIX    สัดส่วน request ที่ยิงไป /api/slow    (0.0-1.0)
  SEED        seed ของลำดับสุ่ม (ค่าเดียวกัน = ผลใกล้เคียงกันทุกเครื่อง)

การเลือก endpoint ใช้ "ตารางรอบละ 100 ครั้ง" (deterministic) ไม่ใช่สุ่มล้วน
→ error ratio ที่ Prometheus เห็นจะเท่ากับ ERROR_MIX จริง ๆ ไม่แกว่งตามดวง
"""

import os
import random
import threading
import time
import urllib.error
import urllib.request

TARGET_URL = os.getenv("TARGET_URL", "http://app:8000").rstrip("/")
RPS = float(os.getenv("RPS", "8"))
ERROR_MIX = float(os.getenv("ERROR_MIX", "0"))
SLOW_MIX = float(os.getenv("SLOW_MIX", "0"))
SEED = int(os.getenv("SEED", "2569"))
MAX_INFLIGHT = int(os.getenv("MAX_INFLIGHT", "64"))

CYCLE = 100
_sent = 0
_ok = 0
_err = 0
_stats_lock = threading.Lock()
_inflight = threading.Semaphore(MAX_INFLIGHT)


def build_plan():
    """สร้างตารางปลายทาง 100 ช่อง แล้วสับด้วย seed คงที่ → สัดส่วนแม่นยำ ลำดับคงที่"""
    n_err = int(round(ERROR_MIX * CYCLE))
    n_slow = int(round(SLOW_MIX * CYCLE))
    n_fast = CYCLE - n_err - n_slow
    if n_fast < 0:
        raise SystemExit("ERROR_MIX + SLOW_MIX ต้องไม่เกิน 1.0")
    plan = ["/api/error"] * n_err + ["/api/slow"] * n_slow
    for i in range(n_fast):
        plan.append("/" if i % 2 == 0 else "/api/items")
    random.Random(SEED).shuffle(plan)
    return plan


PLAN = build_plan()


def fire(path: str):
    global _ok, _err
    url = TARGET_URL + path
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            resp.read()
            code = resp.status
    except urllib.error.HTTPError as exc:
        code = exc.code
    except Exception:
        code = 0
    with _stats_lock:
        if 200 <= code < 400:
            _ok += 1
        else:
            _err += 1
    _inflight.release()


def reporter():
    while True:
        time.sleep(15)
        with _stats_lock:
            print(f"[loadgen] sent={_sent} ok={_ok} non2xx={_err} "
                  f"RPS={RPS} ERROR_MIX={ERROR_MIX} SLOW_MIX={SLOW_MIX}", flush=True)


def main():
    global _sent
    print(f"[loadgen] target={TARGET_URL} RPS={RPS} ERROR_MIX={ERROR_MIX} "
          f"SLOW_MIX={SLOW_MIX} SEED={SEED}", flush=True)
    threading.Thread(target=reporter, daemon=True).start()

    interval = 1.0 / RPS if RPS > 0 else 1.0
    idx = 0
    next_at = time.monotonic()
    while True:
        path = PLAN[idx % CYCLE]
        idx += 1
        _inflight.acquire()
        threading.Thread(target=fire, args=(path,), daemon=True).start()
        with _stats_lock:
            _sent += 1
        next_at += interval
        delay = next_at - time.monotonic()
        if delay > 0:
            time.sleep(delay)
        else:
            next_at = time.monotonic()


if __name__ == "__main__":
    main()
