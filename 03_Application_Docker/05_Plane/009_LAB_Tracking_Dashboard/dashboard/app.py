"""app.py — Mission Control: dashboard ติดตามผลิตภัณฑ์จาก Plane REST API (FastAPI + SSE + inline-SVG UI)

  GET  /               หน้า dashboard (static/index.html — ไฟล์เดียว ไม่มี CDN)
  GET  /api/metrics    metric ทั้งหมดของ project ปัจจุบัน (?project=PLAB เปลี่ยนได้)
  GET  /api/raw        snapshot ดิบที่ดึงมา (items/states/cycles/activities) สำหรับทำรายงานเอง
  GET  /api/health     งบ request, X-RateLimit-Remaining ล่าสุด, freshness, backoff
  GET  /events         SSE — แจ้ง "refreshed" ทุกครั้งที่ snapshot ใหม่พร้อม
  POST /hook           webhook จาก Plane → refresh ทันที (dashboard.lab ต้องอยู่ใน WEBHOOK_ALLOWED_HOSTS)

env: PLANE_BASE (http://proxy) · PLANE_API_TOKEN · WS (devtools-lab) · PROJECT (PLAB) · REFRESH (60 s) · BUDGET (40 req/min) · WIP_POLICY (wip_policy.json)
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import threading
import time
from collections import deque
from pathlib import Path

import requests
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

import metrics as M

BASE = os.environ.get("PLANE_BASE", "http://proxy").rstrip("/") + "/api/v1"
TOKEN = os.environ.get("PLANE_API_TOKEN", "")
WS = os.environ.get("WS", "devtools-lab")
DEFAULT_PROJECT = os.environ.get("PROJECT", "PLAB")
REFRESH = int(os.environ.get("REFRESH", "60"))
BUDGET = int(os.environ.get("BUDGET", "40"))
HERE = Path(__file__).resolve().parent
POLICY = json.loads(Path(os.environ.get("WIP_POLICY", HERE / "wip_policy.json")).read_text(encoding="utf-8"))

app = FastAPI(title="Mission Control")
STATE = {"snapshots": {}, "metrics": {}, "last": {}, "remaining": None, "reset": None, "backoff_until": 0, "calls": deque(maxlen=500), "errors": deque(maxlen=20), "hooks": 0}
SUBS: list[asyncio.Queue] = []
LOOP = None


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- Plane client with budget + backoff
def api(path, params=None):
    now = time.time()
    if now < STATE["backoff_until"]:
        raise RuntimeError(f"backoff until {STATE['backoff_until'] - now:.0f}s")
    recent = [t for t in STATE["calls"] if now - t < 60]
    if len(recent) >= BUDGET:
        raise RuntimeError(f"budget {BUDGET}/min reached")
    r = requests.get(f"{BASE}{path}", headers={"X-API-Key": TOKEN}, params=params, timeout=20)
    STATE["calls"].append(time.time())
    STATE["remaining"] = r.headers.get("X-RateLimit-Remaining")
    STATE["reset"] = r.headers.get("X-RateLimit-Reset")
    if r.status_code == 429:
        reset = int(STATE["reset"] or 0)
        STATE["backoff_until"] = max(reset, int(time.time()) + 30)
        raise RuntimeError(f"429 → backoff until reset ({STATE['backoff_until'] - int(time.time())}s)")
    r.raise_for_status()
    return r.json()


def paged(path, params=None):
    out, cursor = [], None
    while True:
        p = dict(params or {}, per_page=100)
        if cursor:
            p["cursor"] = cursor
        d = api(path, p)
        out.extend(d.get("results", []))
        if not d.get("next_page_results"):
            return out
        cursor = d["next_cursor"]


def collect(project_key):
    """ดึงข้อมูลที่ dashboard ต้องใช้ทั้งหมด (incremental: activities ดึงเฉพาะใบที่ updated_at เปลี่ยน · relations เฉพาะใบที่ยังไม่เสร็จ)"""
    t0 = time.time(); n0 = len(STATE["calls"])
    prev = STATE["snapshots"].get(project_key, {})
    projects = paged(f"/workspaces/{WS}/projects/")
    proj = next(p for p in projects if p["identifier"] == project_key)
    pid = proj["id"]
    states = {s["id"]: {"name": s["name"], "group": s["group"]} for s in paged(f"/workspaces/{WS}/projects/{pid}/states/")}
    items = [i for i in paged(f"/workspaces/{WS}/projects/{pid}/work-items/") if not i.get("parent")]
    points = {}
    try:
        for e in paged(f"/workspaces/{WS}/projects/{pid}/estimates/"):
            for p in e.get("points", []):
                try: points[p["id"]] = float(p["value"])
                except (TypeError, ValueError): pass
    except Exception:
        points = prev.get("points", {})
    cycles = []
    for c in paged(f"/workspaces/{WS}/projects/{pid}/cycles/"):
        ids = [ci["id"] for ci in paged(f"/workspaces/{WS}/projects/{pid}/cycles/{c['id']}/cycle-issues/")] if c.get("total_issues") else []
        today = dt.date.today()
        status = "draft"
        if c.get("start_date") and c.get("end_date"):
            s, e = dt.date.fromisoformat(c["start_date"][:10]), dt.date.fromisoformat(c["end_date"][:10])
            status = "completed" if e < today else ("current" if s <= today else "upcoming")
        cycles.append({"id": c["id"], "name": c["name"], "start_date": c.get("start_date"), "end_date": c.get("end_date"), "status": status, "issue_ids": ids})
    # activities: เฉพาะใบที่เปลี่ยนตั้งแต่ครั้งก่อน
    old_items = {i["id"]: i for i in prev.get("items", [])}
    acts = {a["issue_id"]: a for a in []}
    acts = dict(prev.get("acts_by_issue", {}))
    for it in items:
        if old_items.get(it["id"], {}).get("updated_at") == it.get("updated_at") and it["id"] in acts:
            continue
        rows = paged(f"/workspaces/{WS}/projects/{pid}/work-items/{it['id']}/activities/")
        acts[it["id"]] = [{"issue_id": it["id"], "field": a.get("field"), "old_value": a.get("old_value"), "new_value": a.get("new_value"), "created_at": a["created_at"]} for a in rows if a.get("field") == "state"]
    activities = [a for rows in acts.values() for a in rows]
    # relations: list ของ work item ไม่แนบ relation มาให้ → ถาม /relations/ เฉพาะใบที่ยังไม่เสร็จ (blocker ของใบที่ Done ไม่มีความหมายแล้ว)
    relations = []
    for it in items:
        if it.get("completed_at"):
            continue
        rel = api(f"/workspaces/{WS}/projects/{pid}/work-items/{it['id']}/relations/")
        for r in rel.get("blocked_by", []) or []:
            relations.append({"issue_id": it["id"], "related_issue_id": r.get("issue_id"), "relation_type": "blocked_by"})
    snap = {"project": proj["identifier"], "project_id": pid, "items": items, "states": states, "points": points, "cycles": cycles,
            "activities": activities, "acts_by_issue": acts, "relations": relations, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(),
            "requests_used": len(STATE["calls"]) - n0, "seconds": round(time.time() - t0, 1)}
    STATE["snapshots"][project_key] = snap
    return snap


def compute(snap):
    items, states, points, cycles = snap["items"], snap["states"], snap["points"], snap["cycles"]
    by_id = {i["id"]: i for i in items}
    current = next((c for c in cycles if c["status"] == "current"), None) or next((c for c in cycles if c["status"] == "upcoming"), None)
    bd = None
    if current and current["start_date"] and current["end_date"]:
        its = [by_id[i] for i in current["issue_ids"] if i in by_id]
        bd = {"cycle": current["name"], "items": M.burndown(its, current["start_date"], current["end_date"]),
              "points": M.burndown(its, current["start_date"], current["end_date"], points=points) if points else None}
    return {
        "project": snap["project"], "fetched_at": snap["fetched_at"], "counts": {"items": len(items), "cycles": len(cycles)},
        "burndown": bd,
        "velocity": M.velocity(cycles, by_id, points=points or None),
        "cfd": M.cfd(items, states, snap["activities"], days=14),
        "lead_cycle": M.lead_cycle(items, states, snap["activities"]),
        "wip": M.wip(items, states, POLICY),
        "blockers": M.blockers(by_id, snap["relations"], states),
        "aging": M.aging(items, states, snap["activities"]),
        "throughput_7d": sum(1 for i in items if i.get("completed_at") and M._ts(i["completed_at"]) >= dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=7)),
    }


def refresh(project_key, reason="poll"):
    try:
        snap = collect(project_key)
        STATE["metrics"][project_key] = compute(snap)
        STATE["last"][project_key] = time.time()
        log(f"refresh[{reason}] {project_key}: items={len(snap['items'])} cycles={len(snap['cycles'])} requests={snap['requests_used']} remaining={STATE['remaining']} in {snap['seconds']}s")
        notify({"type": "refreshed", "project": project_key, "reason": reason, "at": snap["fetched_at"]})
    except Exception as e:
        STATE["errors"].append({"at": time.strftime("%H:%M:%S"), "error": str(e)})
        log(f"refresh[{reason}] {project_key} failed: {e}")
        notify({"type": "error", "project": project_key, "error": str(e)})


def notify(msg):
    if LOOP is None:
        return
    for q in list(SUBS):
        LOOP.call_soon_threadsafe(q.put_nowait, msg)


def poller():
    while True:
        for key in list({DEFAULT_PROJECT, *STATE["metrics"].keys()}):
            refresh(key, "poll")
        time.sleep(REFRESH)


@app.on_event("startup")
async def _start():
    global LOOP
    LOOP = asyncio.get_running_loop()
    threading.Thread(target=poller, daemon=True).start()


@app.get("/", response_class=HTMLResponse)
def index():
    return (HERE / "static" / "index.html").read_text(encoding="utf-8")


@app.get("/api/metrics")
def api_metrics(project: str = DEFAULT_PROJECT):
    if project not in STATE["metrics"]:
        refresh(project, "first")
    m = STATE["metrics"].get(project)
    return JSONResponse(m if m else {"error": "no data yet", "errors": list(STATE["errors"])[-3:]}, status_code=200 if m else 503)


@app.get("/api/raw")
def api_raw(project: str = DEFAULT_PROJECT):
    s = STATE["snapshots"].get(project) or {}
    return {k: v for k, v in s.items() if k != "acts_by_issue"}


@app.get("/api/health")
def api_health():
    now = time.time()
    return {"status": "ok", "requests_last_minute": sum(1 for t in STATE["calls"] if now - t < 60), "budget_per_minute": BUDGET,
            "ratelimit_remaining": STATE["remaining"], "ratelimit_reset": STATE["reset"], "backoff_s": max(0, int(STATE["backoff_until"] - now)),
            "freshness_s": {k: int(now - v) for k, v in STATE["last"].items()}, "refresh_interval_s": REFRESH, "hooks_received": STATE["hooks"],
            "errors": list(STATE["errors"])[-3:]}


@app.post("/hook")
async def hook(request: Request):
    body = await request.body()
    STATE["hooks"] += 1
    try:
        ev = json.loads(body or b"{}")
    except Exception:
        ev = {}
    log("webhook:", ev.get("event"), ev.get("action"), "→ refresh now")
    threading.Thread(target=refresh, args=(DEFAULT_PROJECT, "webhook"), daemon=True).start()
    return {"status": "ok"}


@app.get("/events")
async def events():
    q: asyncio.Queue = asyncio.Queue()
    SUBS.append(q)

    async def gen():
        try:
            yield ": connected\n\n"
            while True:
                try:
                    msg = await asyncio.wait_for(q.get(), timeout=15)
                    yield f"data: {json.dumps(msg)}\n\n"
                except asyncio.TimeoutError:
                    yield ": ping\n\n"
        finally:
            if q in SUBS:
                SUBS.remove(q)
    return StreamingResponse(gen(), media_type="text/event-stream", headers={"Cache-Control": "no-cache"})
