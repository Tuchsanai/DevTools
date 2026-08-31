#!/usr/bin/env python3
"""wip_guard.py — ยาม WIP limit ที่ Plane CE ไม่มีให้ (บอร์ดของ CE ลากการ์ดเข้าคอลัมน์ไหนก็ได้ไม่จำกัด)

อ่านนโยบายจาก wip_policy.json  {"In Progress": 3, "In Review": 2}  แล้วนับใบงานจริงในแต่ละ state ผ่าน REST API

  python wip_guard.py                 # ตรวจครั้งเดียว → ตาราง state|wip|limit|status · exit 1 ถ้ามีคอลัมน์เกิน (ใช้ใน CI ได้)
  python wip_guard.py --watch 15      # ตรวจซ้ำทุก 15 วินาที ตารางสดบนจอ กะพริบแดงเมื่อเกิน (Ctrl+C หยุด)
  python wip_guard.py --comment       # เมื่อเกิน: โพสต์ comment เตือนบนการ์ดใบล่าสุดของคอลัมน์นั้น (1 ครั้งต่อการละเมิด)

งบ request: เตรียมงานตอนเริ่ม 3 request (projects, states, ...) แล้วแต่ละรอบใช้ 1 request (list work items 1 หน้า)
→ --watch 15 ใช้ 4 request/นาที จาก 60 ที่ token มี · ถ้าโพสต์ comment จะ +1 ต่อการละเมิด
"""
import argparse
import datetime as dt
import json
import os
import sys
import time

from planeapi import Plane

RED, GREEN, YELLOW, DIM, BOLD, INV, RESET = "\033[31m", "\033[32m", "\033[33m", "\033[2m", "\033[1m", "\033[7m", "\033[0m"

ap = argparse.ArgumentParser()
ap.add_argument("--project", default="PLAB")
ap.add_argument("--policy", default="wip_policy.json")
ap.add_argument("--watch", type=int, metavar="SEC", help="ตรวจซ้ำทุก SEC วินาที")
ap.add_argument("--max-rounds", type=int, default=0, help="หยุดหลังตรวจครบ N รอบ (0 = ไม่หยุด) — ใช้ตอนทดสอบ/CI")
ap.add_argument("--comment", action="store_true", help="โพสต์ comment เตือนบนการ์ดล่าสุดของคอลัมน์ที่เกิน")
ap.add_argument("--no-color", action="store_true")
a = ap.parse_args()
if a.no_color or not sys.stdout.isatty() and not os.environ.get("FORCE_COLOR"):
    RED = GREEN = YELLOW = DIM = BOLD = INV = RESET = ""

with open(a.policy, encoding="utf-8") as f:
    policy: dict[str, int] = json.load(f)

p = Plane()
pid = p.project(a.project)["id"]                         # request 1: projects
states = p.states(pid)                                   # request 2: states  (ชื่อ → uuid)
missing = [s for s in policy if s not in states]
if missing:
    sys.exit(f"state ในนโยบายไม่มีในโปรเจกต์: {missing} (ข้อ 1 ของแล็บสร้าง In Review หรือยัง?)")
id2name = {v["id"]: k for k, v in states.items()}
warned: dict[str, str] = {}                              # state → issue id ที่เตือนไปแล้ว


def snapshot() -> tuple[list[dict], str]:
    """1 request: ใบงานทั้งโปรเจกต์ 1 หน้า (per_page=100) เอาเฉพาะ field ที่ต้องใช้"""
    r = p.get(f"projects/{pid}/work-items/", per_page=100, fields="id,sequence_id,name,state,updated_at,parent")
    if r.status_code != 200:
        sys.exit(f"list work items → {r.status_code}: {r.text[:200]}")
    return r.json()["results"], r.headers.get("X-RateLimit-Remaining", "?")


def check() -> tuple[list[tuple], bool, str]:
    items, remaining = snapshot()
    rows, violated = [], False
    for state, limit in policy.items():
        cards = [i for i in items if i["state"] == states[state]["id"]]
        wip = len(cards)
        bad = wip > limit
        violated |= bad
        status = f"{RED}{BOLD}VIOLATION ({wip} > {limit}){RESET}" if bad else f"{GREEN}OK{RESET}"
        rows.append((state, wip, limit, status, cards))
    return rows, violated, remaining


def maybe_comment(rows):
    for state, wip, limit, _, cards in rows:
        if wip <= limit or not cards:
            continue
        newest = max(cards, key=lambda c: c["updated_at"])          # การ์ดที่เพิ่งขยับล่าสุด = ตัวที่ทำให้เกิน
        if warned.get(state) == newest["id"]:
            continue
        html = (f"<p>⚠️ <strong>WIP limit exceeded</strong> — คอลัมน์ <em>{state}</em> มี {wip} ใบ "
                f"เกินนโยบาย {limit} (Kanban Policies) · โพสต์โดย wip_guard.py {dt.datetime.now():%Y-%m-%d %H:%M}</p>")
        r = p.post(f"projects/{pid}/work-items/{newest['id']}/comments/", {"comment_html": html})
        print(f"  {YELLOW}→ comment บน {a.project}-{newest['sequence_id']}: HTTP {r.status_code}{RESET}")
        warned[state] = newest["id"]


def render(rows, violated, remaining, round_no):
    if a.watch:
        print("\033[2J\033[H", end="")                              # clear screen + home
        print(f"{BOLD}wip_guard{RESET} · {a.project} · รอบ {round_no} · {dt.datetime.now():%H:%M:%S} · ทุก {a.watch}s "
              f"· {DIM}requests รวม {p.calls} · X-RateLimit-Remaining {remaining}{RESET}")
    print(f"{BOLD}{'state':<13}{'wip':>4}  {'limit':>5}  status{RESET}")
    for state, wip, limit, status, cards in rows:
        print(f"{state:<13}{wip:>4}  {limit:>5}  {status}")
        if wip > limit:
            for c in sorted(cards, key=lambda c: c["updated_at"], reverse=True)[:wip]:
                print(f"{DIM}   {a.project}-{c['sequence_id']:<4} {c['name'][:48]}{RESET}")
    if violated:
        print(f"\n{INV}{RED}{BOLD}  ⛔ WIP POLICY VIOLATED — หยุดรับงานใหม่ แล้วช่วยกันเคลียร์คอลัมน์ที่เกินก่อน  {RESET}")
    else:
        print(f"\n{GREEN}✓ ทุกคอลัมน์อยู่ในนโยบาย{RESET}")


round_no = 0
while True:
    round_no += 1
    rows, violated, remaining = check()
    render(rows, violated, remaining, round_no)
    if a.comment and violated:
        maybe_comment(rows)
    if not a.watch:
        print(f"{DIM}requests used: {p.calls} · X-RateLimit-Remaining: {remaining}{RESET}")
        sys.exit(1 if violated else 0)
    if a.max_rounds and round_no >= a.max_rounds:
        sys.exit(1 if violated else 0)
    try:
        time.sleep(a.watch)
    except KeyboardInterrupt:
        print("\nหยุดเฝ้าแล้ว"); sys.exit(0)
