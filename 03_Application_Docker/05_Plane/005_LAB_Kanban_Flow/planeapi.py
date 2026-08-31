#!/usr/bin/env python3
"""planeapi.py — client กลางสำหรับ Plane REST API v1 (ไฟล์เดียวกันนี้ใช้ร่วมกันใน LAB 3–7 — ทุกโฟลเดอร์ต้องเป็นสำเนาเดียวกัน)

สิ่งที่ client นี้จัดการให้ทุกสคริปต์ :
  * token อ่านจาก env PLANE_API_TOKEN หรือไฟล์ ~/.plane_token (สร้างใน LAB 3 ข้อ 8, chmod 600) → header X-API-Key ทุกคำขอ
  * base URL จาก env PLANE_BASE (ค่าปกติ http://localhost:8080) · workspace จาก env PLANE_WS (ค่าปกติ devtools-lab)
  * path สั้น เช่น "projects/<uuid>/states/" ถูกเติมเป็น /api/v1/workspaces/<ws>/... ให้ ·
    path ที่ขึ้นต้นด้วย users/ หรือ workspaces/ ต่อจาก /api/v1 ตรง ๆ · URL เต็ม (http…) ใช้ตามนั้น
  * get/post/patch/delete คืน requests.Response (ผู้เรียกดู .status_code / .json() เอง)
  * โดน 429 Too Many Requests → รอตาม Retry-After (หรือจน X-RateLimit-Reset) แล้วส่งซ้ำให้อัตโนมัติ
    และเก็บ calls / remaining / reset / waits ไว้ดู (stats())
  * paginate() เดิน cursor (next_cursor / next_page_results) จนครบทุกหน้า — endpoint ที่ตอบเป็น list ตรง ๆ ก็รับได้
  * helper แปลงชื่อ → UUID: project("PLAB"), states(), labels(), estimate_points(), cycles(), cycle_by_name(), members()

ใช้ในสคริปต์:  from planeapi import Plane, C ; p = Plane() ; pid = p.project("PLAB")["id"]
"""
import os
import subprocess
import sys
import time

import requests

BASE = os.environ.get("PLANE_BASE", "http://localhost:8080").rstrip("/")
API = BASE + "/api/v1"
TOKEN_FILE = os.path.expanduser("~/.plane_token")
WS = os.environ.get("PLANE_WS", "devtools-lab")


# สีสำหรับ terminal (ใช้ร่วมกันทุกสคริปต์ของชุด LAB)
class C:
    G = "\033[32m"; Y = "\033[33m"; R = "\033[31m"; B = "\033[36m"; D = "\033[2m"; X = "\033[0m"; W = "\033[1m"


def load_token():
    tok = os.environ.get("PLANE_API_TOKEN", "").strip()
    if not tok and os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            tok = f.read().strip()
    if not tok:
        sys.exit(f"ไม่พบ token: สร้าง Personal Access Token (LAB 3 ข้อ 8) แล้ว echo '<YOUR_API_TOKEN>' > {TOKEN_FILE} "
                 "(chmod 600) หรือ export PLANE_API_TOKEN=<YOUR_API_TOKEN>")
    if not tok.startswith("plane_api_"):
        sys.exit(f"{TOKEN_FILE} ไม่ใช่ token ของ Plane (ต้องขึ้นต้นด้วย plane_api_)")
    return tok


class Plane:
    def __init__(self, token=None, workspace=WS, base=API):
        self.api = base.rstrip("/")
        self.ws = workspace
        self.s = requests.Session()
        self.s.headers.update({"X-API-Key": token or load_token(), "Content-Type": "application/json"})
        self.calls = 0          # จำนวนคำขอที่ส่งไปทั้งหมด
        self.remaining = None   # X-RateLimit-Remaining ล่าสุด
        self.reset = None       # X-RateLimit-Reset ล่าสุด (unix timestamp)
        self.waits = 0          # โดน 429 แล้วต้องรอกี่ครั้ง

    # ---------- HTTP ----------
    def url(self, path):
        if path.startswith("http"):
            return path
        path = path.lstrip("/")
        if path.startswith(("workspaces/", "users/")):
            return f"{self.api}/{path}"
        return f"{self.api}/workspaces/{self.ws}/{path}"

    def req(self, method, path, **kw):
        url = self.url(path)
        while True:
            r = self.s.request(method, url, timeout=30, **kw)
            self.calls += 1
            if r.headers.get("X-RateLimit-Remaining") is not None:      # เก็บ header ล่าสุดไว้ดู
                self.remaining = int(r.headers["X-RateLimit-Remaining"])
                self.reset = int(r.headers.get("X-RateLimit-Reset") or 0) or self.reset
            if r.status_code != 429:
                return r
            # ---- backoff: server บอกมาเองว่าต้องรอกี่วินาที ----
            wait = int(r.headers.get("Retry-After") or 0)
            if not wait:
                now = int(time.time())
                wait = self.reset - now if self.reset and self.reset > now else 5
            wait = max(1, min(wait, 60))
            self.waits += 1
            print(f"{C.Y}⏳ 429 Too Many Requests — client รอ {wait}s (Retry-After) แล้วยิงซ้ำเอง{C.X}",
                  file=sys.stderr, flush=True)
            time.sleep(wait + 1)

    request = req   # ชื่อเดิม

    def get(self, path, params=None, **query):
        return self.req("GET", path, params={**(params or {}), **query})

    def post(self, path, body=None, **kw):
        return self.req("POST", path, json=body, **kw)

    def patch(self, path, body=None, **kw):
        return self.req("PATCH", path, json=body, **kw)

    def delete(self, path, **kw):
        return self.req("DELETE", path, **kw)

    def paginate(self, path, per_page=100, **params):
        """เดินทุกหน้าด้วย cursor: ส่ง cursor=next_cursor ไปเรื่อย ๆ จน next_page_results เป็น false"""
        cursor = None
        while True:
            q = dict(params, per_page=per_page)
            if cursor:
                q["cursor"] = cursor
            r = self.get(path, params=q)
            if r.status_code != 200:
                sys.exit(f"GET {path} → {r.status_code}: {r.text[:200]}")
            page = r.json()
            if isinstance(page, list):          # บาง endpoint (members/, cycle_view=current) ตอบเป็น list ตรง ๆ
                yield from page
                return
            yield from page.get("results", [])
            if not page.get("next_page_results"):
                return
            cursor = page["next_cursor"]

    # ---------- lookups (ชื่อ → UUID) ----------
    def project(self, identifier="PLAB", required=True):
        """identifier (เช่น PLAB) → project dict (มี id เป็น UUID) — ไม่พบ: จบโปรแกรม หรือคืน None ถ้า required=False"""
        for p in self.paginate("projects/"):
            if p["identifier"].upper() == identifier.upper() or p["id"] == identifier:
                return p
        if required:
            sys.exit(f"ไม่พบโปรเจกต์ {identifier} ใน workspace {self.ws}")
        return None

    def states(self, pid):
        """{ชื่อ state: {id, group, ...}} — ต้องใช้ UUID ของ state ตอนสร้าง/ย้าย work item"""
        return {s["name"]: s for s in self.paginate(f"projects/{pid}/states/")}

    def labels(self, pid):
        return {l["name"]: l for l in self.paginate(f"projects/{pid}/labels/")}

    def members(self):
        """สมาชิก workspace (endpoint นี้คืน list ตรง ๆ ไม่มี envelope)"""
        return list(self.paginate("members/"))

    def work_item(self, key):
        """GET ด้วย human key เช่น PLAB-1 (path เดียวใน v1 ที่ไม่ต้องใช้ UUID) → Response"""
        return self.get(f"work-items/{key.upper()}/")

    def work_items(self, pid, **params):
        return list(self.paginate(f"projects/{pid}/work-items/", **params))

    def cycles(self, pid, view="all"):
        return list(self.paginate(f"projects/{pid}/cycles/", cycle_view=view))

    def cycle_by_name(self, pid, name):
        for c in self.cycles(pid):
            if c["name"] == name:
                return c
        return None

    def estimate(self, pid):
        r = self.get(f"projects/{pid}/estimates/")
        return r.json() if r.status_code == 200 else None

    def estimate_points(self, pid):
        """คืน (by_value, by_id): {'5': uuid} และ {uuid: 5.0} — value ถูกเก็บเป็น string ใน DB

        Plane v1.4.2 มีไฟล์ api/urls/estimate.py แต่ยังไม่ได้ mount เข้า /api/v1 (GET .../estimates/ → 404)
        จึงลองผ่าน API ก่อน ถ้าไม่มีให้ถอยไปอ่านตาราง estimate_points ผ่าน `pc exec ... psql` โดยตรง
        """
        est = self.estimate(pid)
        if est:
            r = self.get(f"projects/{pid}/estimates/{est['id']}/estimate-points/")
            pts = r.json() if r.status_code == 200 else []
            return {str(x["value"]): x["id"] for x in pts}, {x["id"]: float(x["value"]) for x in pts}
        sql = ("SELECT ep.id, ep.value FROM estimate_points ep JOIN projects p ON p.estimate_id = ep.estimate_id "
               f"WHERE p.id = '{pid}' AND ep.deleted_at IS NULL ORDER BY ep.key")
        try:
            out = subprocess.run(["pc", "exec", "-T", "-e", "PGPASSWORD=plane", "plane-db", "psql", "-U", "plane",
                                  "-d", "plane", "-tA", "-c", sql], capture_output=True, text=True, timeout=60).stdout
        except (OSError, subprocess.SubprocessError):
            out = ""
        rows = [ln.split("|") for ln in out.splitlines() if "|" in ln]
        return {v: i for i, v in rows}, {i: float(v) for i, v in rows}

    def stats(self):
        return (f"API calls: {self.calls} · X-RateLimit-Remaining: {self.remaining}"
                f" · โดน 429 แล้วรอ: {self.waits} ครั้ง")


if __name__ == "__main__":
    # smoke test: token ใช้ได้ไหม + หา UUID ของ PLAB (ห้าม print token)
    p = Plane()
    r = p.get("users/me/")
    who = r.json().get("email") if r.status_code == 200 else r.text[:80]
    print(f"users/me → {r.status_code} {who} | {p.stats()}")
    proj = p.project("PLAB", required=False)
    print("project PLAB:", proj["id"] if proj else "ไม่พบ (ยังไม่ได้สร้างใน LAB 1?)")
