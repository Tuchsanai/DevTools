#!/usr/bin/env python3
"""hookwall — กำแพง event สำหรับ webhook ของ Plane (stdlib เท่านั้น ไม่ต้อง pip)

  POST /hook        รับ webhook จาก Plane → ตรวจ X-Plane-Signature (HMAC-SHA256 ของ raw body ด้วย secret)
                    → กันซ้ำด้วย X-Plane-Delivery → เก็บลง /data/events.jsonl → ส่งขึ้นจอผ่าน SSE → รัน rules
  GET  /            หน้ากำแพง (static/index.html — ไฟล์เดียว CSS/JS/SVG inline)
  GET  /events      Server-Sent Events: event ใหม่ทุกใบแบบสด
  GET  /api/events  event ล่าสุด (JSON) สำหรับโหลดครั้งแรก
  GET  /health      {"status":"ok","events":N,"rejected":M,"rules_fired":K}

env: PLANE_WEBHOOK_SECRET (plane_wh_…) · PLANE_API_TOKEN (token ของ bot user) · PLANE_BASE (http://proxy)
     WS (devtools-lab) · PORT (9000) · DATA_DIR (/data) · RULES (rules.json)
"""
import base64
import hashlib
import hmac
import json
import os
import queue
import threading
import time
import urllib.error
import urllib.request
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

SECRET = os.environ.get("PLANE_WEBHOOK_SECRET", "").encode()
TOKEN = os.environ.get("PLANE_API_TOKEN", "")
BASE = os.environ.get("PLANE_BASE", "http://proxy").rstrip("/")
WS = os.environ.get("WS", "devtools-lab")
PORT = int(os.environ.get("PORT", "9000"))
DATA = Path(os.environ.get("DATA_DIR", "/data"))
DATA.mkdir(parents=True, exist_ok=True)
HERE = Path(__file__).resolve().parent
RULES_FILE = Path(os.environ.get("RULES", HERE / "rules.json"))

EVENTS = deque(maxlen=500)          # event ล่าสุดสำหรับ /api/events
SEEN = deque(maxlen=5000)           # X-Plane-Delivery ที่รับแล้ว (dedup)
SUBS = []                           # SSE subscribers (queue ต่อ client)
LOCK = threading.Lock()
STATS = {"events": 0, "rejected": 0, "duplicates": 0, "rules_fired": 0, "started": time.time()}
BOT = {"id": None, "email": None}
STATE_NAMES = {}                    # state uuid → {name, group}


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- Plane API (bot token)
def api(method, path, body=None):
    if not TOKEN:
        raise RuntimeError("PLANE_API_TOKEN ว่าง — rules ทำงานไม่ได้")
    req = urllib.request.Request(f"{BASE}/api/v1{path}", method=method,
                                 headers={"X-API-Key": TOKEN, "Content-Type": "application/json", "Accept": "application/json"},
                                 data=json.dumps(body).encode() if body is not None else None)
    with urllib.request.urlopen(req, timeout=15) as r:
        raw = r.read()
        return r.status, (json.loads(raw) if raw else {})


def bot_identity():
    try:
        _, me = api("GET", "/users/me/")
        BOT["id"], BOT["email"] = me.get("id"), me.get("email")
        log("bot user:", BOT["email"], BOT["id"])
    except Exception as e:
        log("bot identity failed:", e)


def states_for(project_id):
    if project_id in STATE_NAMES:
        return STATE_NAMES[project_id]
    try:
        _, d = api("GET", f"/workspaces/{WS}/projects/{project_id}/states/")
        rows = d.get("results", d) if isinstance(d, dict) else d
        STATE_NAMES[project_id] = {s["id"]: {"name": s["name"], "group": s["group"]} for s in rows}
    except Exception as e:
        log("states fetch failed:", e)
        STATE_NAMES[project_id] = {}
    return STATE_NAMES[project_id]


def label_id(project_id, name):
    _, d = api("GET", f"/workspaces/{WS}/projects/{project_id}/labels/")
    rows = d.get("results", d) if isinstance(d, dict) else d
    for l in rows:
        if l["name"] == name:
            return l["id"]
    _, created = api("POST", f"/workspaces/{WS}/projects/{project_id}/labels/", {"name": name, "color": "#a32222"})
    return created["id"]


# ---------------------------------------------------------------- rules (Butler-like)
def load_rules():
    try:
        return json.loads(RULES_FILE.read_text(encoding="utf-8"))["rules"]
    except Exception as e:
        log("rules load failed:", e)
        return []


def matches(rule, ev):
    w = rule.get("when", {})
    if w.get("event") and w["event"] != ev["event"]:
        return False
    if w.get("action") and w["action"] not in (ev["action"], "*"):
        return False
    data = ev.get("data") or {}
    if "priority" in w and data.get("priority") != w["priority"]:
        return False
    if w.get("no_assignee") and data.get("assignees"):
        return False
    if "state_group" in w:
        st = data.get("state")
        if isinstance(st, dict):                       # payload ของ Plane ส่ง state เป็น object {id,name,color,group}
            group = st.get("group")
        else:                                          # เผื่อรุ่นที่ส่งเป็น uuid
            group = states_for(data.get("project", "")).get(st or "", {}).get("group")
        if group != w["state_group"]:
            return False
    if "field" in w and (ev.get("activity") or {}).get("field") != w["field"]:
        return False
    if "comment_contains" in w:
        text = strip_tags(data.get("comment_stripped") or data.get("comment_html") or "")
        if w["comment_contains"] not in text:
            return False
    return True


def strip_tags(html):
    import re
    return re.sub(r"<[^>]+>", " ", html or "")


def ids_of(values):
    return [v.get("id") if isinstance(v, dict) else v for v in (values or [])]


def run_rules(ev):
    data = ev.get("data") or {}
    actor = (ev.get("activity") or {}).get("actor") or {}
    actor_id = actor.get("id") if isinstance(actor, dict) else actor
    if BOT["id"] and actor_id == BOT["id"]:
        return [{"rule": "-", "result": "skipped: loop guard (actor = bot)"}]
    fired = []
    project = data.get("project")
    issue_id = data.get("issue") if ev["event"] == "issue_comment" else data.get("id")
    for rule in load_rules():
        if not matches(rule, ev):
            continue
        try:
            for act in rule.get("then", []):
                if act["do"] == "comment":
                    st, _ = api("POST", f"/workspaces/{WS}/projects/{project}/work-items/{issue_id}/comments/",
                                {"comment_html": f"<p>{act['text']}</p>"})
                elif act["do"] == "add_label":
                    lid = label_id(project, act["label"])
                    cur = [x for x in ids_of(data.get("labels")) if x != lid]
                    st, _ = api("PATCH", f"/workspaces/{WS}/projects/{project}/work-items/{issue_id}/", {"labels": cur + [lid]})
                elif act["do"] == "set_target_date":
                    import datetime as dt
                    day = (dt.date.today() + dt.timedelta(days=int(act.get("days", 3)))).isoformat()
                    st, _ = api("PATCH", f"/workspaces/{WS}/projects/{project}/work-items/{issue_id}/", {"target_date": day})
                else:
                    st = "?"
                fired.append({"rule": rule["name"], "result": f"{act['do']} → HTTP {st}"})
            STATS["rules_fired"] += 1
        except urllib.error.HTTPError as e:
            fired.append({"rule": rule["name"], "result": f"HTTP {e.code}: {e.read()[:120].decode(errors='replace')}"})
        except Exception as e:
            fired.append({"rule": rule["name"], "result": f"error: {e}"})
    return fired


# ---------------------------------------------------------------- event store + SSE
def publish(rec):
    with LOCK:
        EVENTS.append(rec)
        dead = []
        for q in SUBS:
            try:
                q.put_nowait(rec)
            except Exception:
                dead.append(q)
        for q in dead:
            SUBS.remove(q)
    with (DATA / "events.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def summarize(ev):
    d = ev.get("data") or {}
    a = ev.get("activity") or {}
    key = f"{d.get('sequence_id') or ''}".strip()
    if ev["event"] == "issue" and key:
        key = f"#{key}"
    field = a.get("field")
    names = states_for(d.get("project", "")) if field == "state" else {}
    def short(v):
        if isinstance(v, list): return ",".join(short(x) for x in v)[:40] or "∅"
        if isinstance(v, dict): return v.get("name") or v.get("id", "")[:8]
        if isinstance(v, str) and v in names: return names[v]["name"]
        return str(v)[:40] if v not in (None, "") else "∅"
    change = f"{field}: {short(a.get('old_value'))} → {short(a.get('new_value'))}" if field else ""
    return {"key": key, "name": (d.get("name") or strip_tags(d.get("comment_html")).strip() or "")[:80], "change": change,
            "actor": (a.get("actor") or {}).get("display_name") if isinstance(a.get("actor"), dict) else a.get("actor")}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):  # เงียบ log มาตรฐาน ใช้ log() ของเราแทน
        pass

    def _send(self, code, body, ctype="application/json"):
        raw = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text") else ""))
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index.html"):
            self._send(200, (HERE / "static" / "index.html").read_bytes(), "text/html")
        elif self.path.startswith("/api/events"):
            with LOCK:
                self._send(200, list(EVENTS)[-200:])
        elif self.path.startswith("/health"):
            self._send(200, {"status": "ok", "uptime_s": int(time.time() - STATS["started"]), **{k: v for k, v in STATS.items() if k != "started"},
                             "bot": BOT["email"], "secret_set": bool(SECRET)})
        elif self.path.startswith("/events"):
            q = queue.Queue(maxsize=200)
            with LOCK:
                SUBS.append(q)
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            try:
                self.wfile.write(b": connected\n\n"); self.wfile.flush()
                while True:
                    try:
                        rec = q.get(timeout=15)
                        self.wfile.write(f"data: {json.dumps(rec, ensure_ascii=False)}\n\n".encode()); self.wfile.flush()
                    except queue.Empty:
                        self.wfile.write(b": ping\n\n"); self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                with LOCK:
                    if q in SUBS:
                        SUBS.remove(q)
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        if not self.path.startswith("/hook"):
            return self._send(404, {"error": "not found"})
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n)
        sig = self.headers.get("X-Plane-Signature", "")
        delivery = self.headers.get("X-Plane-Delivery", "")
        event_hdr = self.headers.get("X-Plane-Event", "")
        expected = hmac.new(SECRET, raw, hashlib.sha256).hexdigest() if SECRET else ""
        ok = bool(SECRET) and hmac.compare_digest(expected, sig)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception:
            payload = {}
        rec = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "delivery": delivery, "event": payload.get("event") or event_hdr,
               "action": payload.get("action"), "signature_ok": ok, "signature": sig[:12] + "…" if sig else "",
               "raw_b64": base64.b64encode(raw).decode(), "headers": {"X-Plane-Event": event_hdr, "X-Plane-Delivery": delivery, "X-Plane-Signature": sig}}
        if not ok:
            STATS["rejected"] += 1
            rec.update({"status": "REJECTED", "summary": {"key": "", "name": "signature mismatch", "change": "", "actor": ""}})
            publish(rec)
            log("REJECTED", delivery, event_hdr)
            return self._send(401, {"error": "signature mismatch"})
        if delivery and delivery in SEEN:
            STATS["duplicates"] += 1
            log("duplicate ignored", delivery)
            return self._send(200, {"status": "duplicate ignored"})
        if delivery:
            SEEN.append(delivery)
        STATS["events"] += 1
        ev = {"event": rec["event"], "action": rec["action"], "data": payload.get("data") or {}, "activity": payload.get("activity") or {}}
        rec.update({"status": "OK", "summary": summarize(ev)})
        self._send(200, {"status": "ok"})           # ตอบ Plane ก่อน แล้วค่อยรัน rules (กัน timeout 30 s)
        fired = run_rules(ev) if TOKEN else []
        rec["rules"] = fired
        publish(rec)
        log("OK", rec["event"], rec["action"], rec["summary"]["key"], rec["summary"]["change"], "| rules:", fired or "-")


if __name__ == "__main__":
    log(f"hookwall on :{PORT} · base {BASE} · ws {WS} · secret {'set' if SECRET else 'MISSING'} · rules {RULES_FILE}")
    bot_identity()
    # โหลด event เดิมจากดิสก์ให้กำแพงไม่ว่างหลัง restart
    try:
        for line in (DATA / "events.jsonl").read_text(encoding="utf-8").splitlines()[-200:]:
            rec = json.loads(line); EVENTS.append(rec)
            if rec.get("delivery"):
                SEEN.append(rec["delivery"])
    except FileNotFoundError:
        pass
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
