"""
LAB 4 — ตัวยิงโหลด (load generator) แบบ stdlib ล้วน ไม่ต้องลง dependency

หลักการ: ไม่สุ่มว่าจะยิง endpoint ไหน แต่สร้าง "ตารางเวร" (pattern) ยาว 20 ช่อง
จากสัดส่วนที่ตั้งไว้ แล้ววนใช้ตารางนั้นซ้ำไปเรื่อย ๆ
  -> ทุกเครื่องได้สัดส่วนเท่ากันเป๊ะ ไม่ใช่ "แล้วแต่ดวง"
  -> คำนวณล่วงหน้าได้ว่า error ratio จะเป็นเท่าไร ก่อนจะไปดูใน Prometheus

ส่วนที่ยังสุ่ม (ใช้ SEED คงที่) คือ jitter ของ "จังหวะเวลา" เท่านั้น เพื่อให้กราฟ
ดูเป็นธรรมชาติ ไม่ใช่ฟันเลื่อยตรงเป๊ะ — แต่ไม่กระทบสัดส่วน endpoint หรือ error ratio
"""

import itertools
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

TARGET = os.environ.get("TARGET", "http://app:8000")
RPS = float(os.environ.get("RPS", "10"))
ERROR_MIX = float(os.environ.get("ERROR_MIX", "0.20"))  # สัดส่วน request ที่ไป /api/error
SLOW_MIX = float(os.environ.get("SLOW_MIX", "0.10"))    # สัดส่วน request ที่ไป /api/slow
ITEM_IDS = int(os.environ.get("ITEM_IDS", "200"))       # ช่วง id ของ /api/items/<id>
SEED = int(os.environ.get("SEED", "2569"))
JITTER = float(os.environ.get("JITTER", "0.10"))        # ความคลาดเคลื่อนของจังหวะยิง +-10%
SLOTS = int(os.environ.get("SLOTS", "20"))              # ความยาวของตารางเวร
REPORT_EVERY = float(os.environ.get("REPORT_EVERY", "30"))

random.seed(SEED)

# ---------------------------------------------------------- สร้างตารางเวร
rest = max(0.0, 1.0 - ERROR_MIX - SLOW_MIX)
WEIGHTS = {
    "/": rest * 0.35,
    "/api/items": rest * 0.45,
    "__item_id__": rest * 0.20,
    "/api/slow": SLOW_MIX,
    "/api/error": ERROR_MIX,
}


def build_pattern(weights: dict, slots: int):
    """กระจายช่องตามน้ำหนักแบบ smooth weighted round-robin (ไม่สุ่ม)

    ทุกก้าวจะบวก 'เครดิต' ให้ทุก route ตามน้ำหนัก แล้วเลือกตัวที่เครดิตมากสุด
    จากนั้นหักเครดิตตัวที่ถูกเลือกไป 1 -> ได้ผลลัพธ์ที่สัดส่วนตรงและกระจายสม่ำเสมอ
    """
    credit = {key: 0.0 for key in weights}
    pattern = []
    for _ in range(slots):
        for key, weight in weights.items():
            credit[key] += weight
        pick = max(credit, key=credit.get)
        credit[pick] -= 1.0
        pattern.append(pick)
    return pattern


PATTERN = build_pattern(WEIGHTS, SLOTS)
_pattern_cycle = itertools.cycle(PATTERN)
_id_cycle = itertools.cycle(range(1, ITEM_IDS + 1))  # id เดินหน้าเรียงลำดับ ไม่สุ่ม

_lock = threading.Lock()
_stats = {"sent": 0, "ok": 0, "err5xx": 0, "fail": 0}


def next_path() -> str:
    with _lock:
        choice = next(_pattern_cycle)
        item_id = next(_id_cycle) if choice == "__item_id__" else None
    if item_id is not None:
        return f"/api/items/{item_id}"
    return choice


def fire(path: str):
    url = TARGET + path
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            resp.read()
            code = resp.status
    except urllib.error.HTTPError as exc:  # 500 ของ /api/error มาทางนี้
        exc.read()
        code = exc.code
    except Exception:
        code = 0
    with _lock:
        _stats["sent"] += 1
        if code == 0:
            _stats["fail"] += 1
        elif code >= 500:
            _stats["err5xx"] += 1
        else:
            _stats["ok"] += 1


def main():
    print(f"loadgen -> {TARGET}  RPS={RPS}  ERROR_MIX={ERROR_MIX}  SLOW_MIX={SLOW_MIX}  SEED={SEED}", flush=True)
    counts = {key: PATTERN.count(key) for key in WEIGHTS}
    print(f"pattern({SLOTS} ช่อง) = {counts}", flush=True)
    print(f"  -> คาดว่า error ratio = {ERROR_MIX} x ERROR_RATE ของแอป", flush=True)

    # รอให้แอปตื่นก่อน (bounded ไม่วนไม่รู้จบ)
    for _ in range(60):
        try:
            with urllib.request.urlopen(TARGET + "/healthz", timeout=2) as resp:
                resp.read()
            break
        except Exception:
            time.sleep(1)
    else:
        print("target ไม่ตอบ /healthz ภายใน 60 วินาที — ออก", flush=True)
        sys.exit(1)

    interval = 1.0 / RPS
    started = time.monotonic()
    last_report = started
    sent = 0
    # ThreadPool ทำให้ request ที่ช้า (เช่น /api/slow) ไม่ไปหน่วงจังหวะการยิงตัวถัดไป
    with ThreadPoolExecutor(max_workers=64) as pool:
        while True:
            pool.submit(fire, next_path())
            sent += 1
            # จับเวลายิงครั้งถัดไปจาก "เวลาเริ่ม + ลำดับที่" เพื่อไม่ให้ rate ไหลช้าลงเรื่อย ๆ
            target_time = started + sent * interval
            target_time += random.uniform(-JITTER, JITTER) * interval
            nap = target_time - time.monotonic()
            if nap > 0:
                time.sleep(nap)
            now = time.monotonic()
            if now - last_report >= REPORT_EVERY:
                with _lock:
                    snap = dict(_stats)
                elapsed = now - started
                ratio = snap["err5xx"] / snap["sent"] if snap["sent"] else 0.0
                print(
                    f"[{elapsed:6.0f}s] sent={snap['sent']} ok={snap['ok']} "
                    f"5xx={snap['err5xx']} fail={snap['fail']} "
                    f"avg_rps={snap['sent'] / elapsed:.2f} err_ratio={ratio:.3f}",
                    flush=True,
                )
                last_report = now


if __name__ == "__main__":
    main()
