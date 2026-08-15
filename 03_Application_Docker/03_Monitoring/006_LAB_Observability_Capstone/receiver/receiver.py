#!/usr/bin/env python3
"""
LAB 6 — Alert receiver + Status Wall

หน้าที่ 3 อย่าง:
  POST /webhook      รับ payload จาก Alertmanager (เก็บไว้ในหน่วยความจำ)
  GET  /api/alerts   คืน alert ที่เคยได้รับเป็น JSON  (check.sh ข้อ 5 ใช้ตัวนี้)
  GET  /api/status   ถาม Prometheus/Grafana/Alertmanager แล้วสรุปสถานะ 5 ข้อ
  GET  /             หน้า Status Wall (HTML/CSS/JS inline ทั้งหมด ไม่มี CDN)

⚠️ เกณฑ์ของ /api/status ต้องเป็น "ชุดเดียวกับ check.sh" เสมอ ถ้าแก้ที่ใดที่หนึ่งต้องแก้อีกที่ให้ตรงกัน
   ไม่งั้นหน้าเว็บจะบอกว่าผ่าน แต่ผู้ตัดสินจริงบอกว่าตก (หรือกลับกัน) ซึ่งแย่กว่าไม่มีหน้าเว็บเลย

ใช้ไลบรารีมาตรฐานของ Python ล้วน ๆ ไม่ต้อง pip install
"""
import base64
import json
import math
import os
import re
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.environ.get("RECEIVER_PORT", "5001"))
PROM_URL = os.environ.get("PROM_URL", "http://prometheus:9090")
GRAFANA_URL = os.environ.get("GRAFANA_URL", "http://grafana:3000")
GRAFANA_USER = os.environ.get("GRAFANA_USER", "admin")
GRAFANA_PASSWORD = os.environ.get("GRAFANA_PASSWORD", "admin")
AM_URL = os.environ.get("AM_URL", "http://alertmanager:9093")
DASH_UID = os.environ.get("DASH_UID", "monlab6")
ALERT_NAME = os.environ.get("ALERT_NAME", "HighErrorRate")
EXPECTED_JOBS = {j.strip() for j in os.environ.get(
    "EXPECTED_JOBS", "alertmanager,app,cadvisor,node,prometheus").split(",") if j.strip()}

DS_SKIP = {"grafana", "-- Grafana --", "-- Mixed --", "-- Dashboard --"}
FAMILIES = [("app_", "แอป"), ("node_", "node-exporter"), ("container_", "cAdvisor")]
RANGE_FN = re.compile(r"\b(rate|irate|increase)\s*\(")
CMP_OP = re.compile(r"(>=|<=|==|!=|>|<)")
GROUND_TRUTH = 'sum(rate(app_requests_total{status=~"5.."}[1m])) / sum(rate(app_requests_total[1m]))'

ALERTS = deque(maxlen=300)
_lock = threading.Lock()
_status_cache = {"at": 0.0, "data": None}
_started = time.time()


# ---------------------------------------------------------------- helpers
def http_json(url, auth=None, timeout=3.0):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    if auth:
        token = base64.b64encode(auth.encode()).decode()
        req.add_header("Authorization", "Basic " + token)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def http_text(url, timeout=3.0):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read().decode("utf-8", "replace").strip()


def prom_samples(expr):
    """ยิง query จริง คืน (samples, err) โดย samples = [(labels, float), ...]"""
    url = PROM_URL + "/api/v1/query?" + urllib.parse.urlencode({"query": expr})
    try:
        data = http_json(url)
    except urllib.error.HTTPError as e:
        try:
            data = json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            return None, "HTTP %s" % e.code
    except Exception as e:
        return None, str(e)[:120]
    if data.get("status") != "success":
        return None, str(data.get("error", "query ไม่สำเร็จ"))[:120]
    out = []
    for s in data.get("data", {}).get("result", []):
        try:
            v = float(s.get("value", [0, "nan"])[1])
        except Exception:
            v = float("nan")
        out.append((s.get("metric", {}), v))
    return out, ""


def has_data(samples):
    return bool(samples) and any(not math.isnan(v) for _lbl, v in samples)


def first_value(samples):
    for _lbl, v in samples or []:
        if not math.isnan(v):
            return v
    return None


def prom_query(expr):
    """ค่าตัวแรกของ expr (None เมื่อไม่มีข้อมูล) — ใช้กับ query ที่คืนเลขตัวเดียว"""
    samples, _err = prom_samples(expr)
    return first_value(samples)


def find_rule(name=None):
    """หา alert rule ตามชื่อจาก /api/v1/rules (คืน None ถ้าไม่มี)"""
    data = http_json(PROM_URL + "/api/v1/rules")
    want = name or ALERT_NAME
    found = None
    for grp in data.get("data", {}).get("groups", []):
        for r in grp.get("rules", []):
            if r.get("name") == want:
                found = r
    return found


def collect_ds_uids(node, found):
    """เดินทั้ง JSON ของ dashboard เพื่อหา datasource uid ที่ถูกอ้างถึง"""
    if isinstance(node, dict):
        ds = node.get("datasource")
        if isinstance(ds, dict) and isinstance(ds.get("uid"), str):
            found.add(ds["uid"])
        elif isinstance(ds, str) and ds:
            found.add(ds)
        for v in node.values():
            collect_ds_uids(v, found)
    elif isinstance(node, list):
        for v in node:
            collect_ds_uids(v, found)


def collect_queries(panels, out):
    """ดึง expr ของทุก panel (รวม panel ที่ซ้อนอยู่ใน row)"""
    for p in panels or []:
        if not isinstance(p, dict):
            continue
        collect_queries(p.get("panels"), out)
        for t in p.get("targets") or []:
            if not isinstance(t, dict):
                continue
            expr = (t.get("expr") or "").strip()
            if not expr:
                continue
            ds = t.get("datasource") or p.get("datasource") or {}
            uid = ds.get("uid") if isinstance(ds, dict) else ds
            out.append((p.get("title") or "(ไม่มีชื่อ panel)", expr, uid))


def build_status():
    checks = []

    # 1) targets
    try:
        data = http_json(PROM_URL + "/api/v1/targets?state=any")
        active = data.get("data", {}).get("activeTargets", [])
        up = [t for t in active if t.get("health") == "up"]
        jobs = sorted({t.get("labels", {}).get("job", "?") for t in active})
        bad = [
            "%s (%s)" % (t.get("labels", {}).get("job", "?"), t.get("scrapeUrl", ""))
            for t in active
            if t.get("health") != "up"
        ]
        missing = sorted(EXPECTED_JOBS - set(jobs))
        extra = sorted(set(jobs) - EXPECTED_JOBS)
        ok = len(active) > 0 and len(up) == len(active) and not missing and not extra
        detail = "jobs: " + ", ".join(jobs)
        if missing:
            detail += " | ขาด: " + ", ".join(missing)
        if extra:
            detail += " | เกิน: " + ", ".join(extra)
        if bad:
            detail += " | ล้ม: " + ", ".join(bad)
        checks.append(
            {
                "id": 1,
                "title": "Prometheus targets",
                "state": "ok" if ok else "fail",
                "value": "%d/%d up" % (len(up), len(active)),
                "detail": detail,
            }
        )
    except Exception as e:
        checks.append({"id": 1, "title": "Prometheus targets", "state": "fail",
                       "value": "ถาม Prometheus ไม่ได้", "detail": str(e)[:120]})

    # 2) app metrics
    try:
        rate = prom_query("sum(rate(app_requests_total[30s]))")
        series = prom_query("count(app_requests_total)")
        ok = rate is not None and rate > 0
        checks.append(
            {
                "id": 2,
                "title": "เมตริกจากแอป",
                "state": "ok" if ok else "fail",
                "value": ("%.2f req/s" % rate) if rate is not None else "ไม่มีข้อมูล",
                "detail": "app_requests_total มี %s ชุด series" % (int(series) if series else 0),
            }
        )
    except Exception as e:
        checks.append({"id": 2, "title": "เมตริกจากแอป", "state": "fail",
                       "value": "query ไม่สำเร็จ", "detail": str(e)[:120]})

    # 3) dashboard ของแล็บใช้ได้จริงหรือไม่ (เกณฑ์เดียวกับ check.sh ข้อ 3)
    #    ไม่ใช่แค่ "uid ที่อ้างมีอยู่" แต่ต้องมี dashboard ใบนั้นจริง ชนิด datasource ถูก
    #    และทุก query ของ panel ยิงแล้วได้ข้อมูลกลับมา
    try:
        health = http_json(GRAFANA_URL + "/api/health")
        auth = "%s:%s" % (GRAFANA_USER, GRAFANA_PASSWORD)
        ds_list = http_json(GRAFANA_URL + "/api/datasources", auth=auth)
        ds_by_uid = {d.get("uid"): d for d in ds_list if isinstance(d, dict)}
        try:
            board = http_json(GRAFANA_URL + "/api/dashboards/uid/" + DASH_UID, auth=auth)
        except urllib.error.HTTPError as e:
            board = None if e.code == 404 else {}
        dash = (board or {}).get("dashboard")
        if not isinstance(dash, dict):
            checks.append({"id": 3, "title": "Grafana dashboard", "state": "fail",
                           "value": "ไม่พบ uid=%s" % DASH_UID,
                           "detail": "Grafana ยังไม่มี dashboard ใบนี้ (provider อ่านไฟล์ทุก 10 วินาที "
                                     "ถ้า JSON ผิดรูปจะไม่ถูกโหลด — ดู log ของ grafana)"})
        else:
            wanted = set()
            collect_ds_uids(dash, wanted)
            wanted = {u for u in wanted if isinstance(u, str) and u and not u.startswith("$") and u not in DS_SKIP}
            missing = sorted(u for u in wanted if u not in ds_by_uid)
            wrong = sorted("%s(type=%s)" % (u, ds_by_uid[u].get("type"))
                           for u in wanted if u in ds_by_uid and ds_by_uid[u].get("type") != "prometheus")
            queries = []
            collect_queries(dash.get("panels"), queries)
            queries = [q for q in queries if not (isinstance(q[2], str) and q[2] in DS_SKIP)]
            empty, errors, ok_exprs = [], [], []
            if not missing and not wrong:
                for title, expr, _uid in queries:
                    samples, err = prom_samples(expr)
                    if samples is None:
                        errors.append(title)
                    elif not has_data(samples):
                        empty.append(title)
                    else:
                        ok_exprs.append(expr)
            blob = " ".join(ok_exprs)
            lack = [label for prefix, label in FAMILIES if prefix not in blob]
            ok = (health.get("database") == "ok" and queries and not missing and not wrong
                  and not empty and not errors and not lack)
            detail = "uid ที่อ้าง: %s | datasource ที่มีจริง: %s | panel query %d รายการ" % (
                ", ".join(sorted(wanted)) or "-", ", ".join(sorted(ds_by_uid)) or "-", len(queries))
            if missing:
                detail += " | ไม่พบ uid: " + ", ".join(missing)
            if wrong:
                detail += " | ชนิดผิด: " + ", ".join(wrong)
            if errors:
                detail += " | query ไม่ผ่าน: " + ", ".join(errors[:3])
            if empty:
                detail += " | ไม่มีข้อมูล: " + ", ".join(empty[:3])
            if lack and not (missing or wrong or errors or empty):
                detail += " | ยังขาดแหล่งข้อมูล: " + ", ".join(lack)
            checks.append(
                {
                    "id": 3,
                    "title": "Grafana dashboard",
                    "state": "ok" if ok else "fail",
                    "value": "db=%s · %d/%d panel query มีข้อมูล" % (
                        health.get("database", "?"), len(ok_exprs), len(queries)),
                    "detail": detail,
                }
            )
    except Exception as e:
        checks.append({"id": 3, "title": "Grafana dashboard", "state": "fail",
                       "value": "ถาม Grafana ไม่ได้", "detail": str(e)[:120]})

    # 4) กฎ HighErrorRate — ตัดสินที่พฤติกรรม: เอา expr ไปยิงจริงแล้วต้องได้ผลไม่ว่างและเป็นสัดส่วน
    rule = None
    try:
        rule = find_rule()
        if rule is None:
            checks.append({"id": 4, "title": "กฎ %s" % ALERT_NAME, "state": "fail",
                           "value": "ไม่พบ rule", "detail": "Prometheus ไม่ได้โหลด rule ชื่อนี้"})
        else:
            expr = rule.get("query", "")
            samples, err = prom_samples(expr)
            gv = prom_query(GROUND_TRUTH)
            if samples is None:
                verdict, why = False, "ยิง expr เป็น query ไม่ผ่าน: %s" % err
            elif not has_data(samples):
                verdict, why = False, ("ยิง expr นี้ตรง ๆ แล้วได้ vector ว่าง = ไม่มีวันเป็น firing"
                                       + ("" if gv is None else " (สัดส่วน error จริงตอนนี้ = %.4f)" % gv))
            else:
                vals = [v for _lbl, v in samples if not math.isnan(v)]
                out_of_range = [v for v in vals if not (0 < v <= 1.0)]
                if out_of_range:
                    verdict, why = False, "ผลของ expr ต้องเป็นสัดส่วน (0,1] แต่ได้ %.4f" % out_of_range[0]
                elif not RANGE_FN.search(expr):
                    verdict, why = False, "ยังใช้ค่าดิบของ counter ต้องคิดจาก rate()/increase() ในช่วงเวลา"
                elif not CMP_OP.search(expr):
                    verdict, why = False, "ไม่มีเกณฑ์เปรียบเทียบ (เช่น > 0.05) จะยิงตลอดเวลา"
                else:
                    verdict, why = True, "ยิง expr แล้วได้ %.4f" % vals[0]
            checks.append(
                {
                    "id": 4,
                    "title": "กฎ %s" % ALERT_NAME,
                    "state": "ok" if verdict else "fail",
                    "value": "state=%s" % rule.get("state", "?"),
                    "detail": "%s | %s" % (why, expr),
                }
            )
    except Exception as e:
        checks.append({"id": 4, "title": "กฎ %s" % ALERT_NAME, "state": "fail",
                       "value": "ถาม rules ไม่ได้", "detail": str(e)[:120]})

    # 5) alert ต้อง firing "อยู่ตอนนี้" และ event ล่าสุดที่ receiver ได้รับต้องเป็น firing
    #    (ประวัติเก่าที่ resolved ไปแล้วไม่นับ — เกณฑ์เดียวกับ check.sh ข้อ 5)
    with _lock:
        items = list(ALERTS)
    names = sorted({a["labels"].get("alertname", "?") for a in items})
    mine = [a for a in items if a.get("labels", {}).get("alertname") == ALERT_NAME]
    last = mine[-1] if mine else None
    last_status = last.get("status", "?") if last else "-"
    state = rule.get("state", "?") if rule else "-"
    try:
        code, body = http_text(AM_URL + "/-/healthy")
        am = "Alertmanager healthy" if code == 200 else "Alertmanager ตอบ HTTP %s" % code
    except Exception as e:
        am = "ต่อ Alertmanager ไม่ได้ (%s)" % str(e)[:60]
    ok = state == "firing" and last is not None and last_status == "firing"
    detail = "rule state=%s | event ล่าสุดของ %s = %s%s | %s" % (
        state, ALERT_NAME, last_status,
        (" เมื่อ " + last.get("receivedAtHuman", "?")) if last else "",
        am)
    if names:
        detail += " | ชนิดที่เคยได้รับ: " + ", ".join(names)
    checks.append(
        {
            "id": 5,
            "title": "Alert ที่ส่งถึง receiver",
            "state": "ok" if ok else "fail",
            "value": "%d ใบ" % len(items),
            "detail": detail if items else "ยังไม่มี alert ใบไหนเดินทางมาถึงเลย | " + am,
        }
    )

    return {
        "generated": time.time(),
        "uptime": time.time() - _started,
        "checks": checks,
        "passed": sum(1 for c in checks if c["state"] == "ok"),
        "total": len(checks),
    }


def cached_status():
    now = time.time()
    if _status_cache["data"] is None or now - _status_cache["at"] > 3:
        try:
            _status_cache["data"] = build_status()
        except Exception as e:  # กันหน้าเว็บพังทั้งหน้า
            _status_cache["data"] = {"generated": now, "checks": [], "passed": 0,
                                     "total": 5, "error": str(e)[:200]}
        _status_cache["at"] = now
    return _status_cache["data"]


# ---------------------------------------------------------------- หน้าเว็บ
PAGE = """<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LAB6 Status Wall</title>
<style>
  :root{
    --bg:#0b1020; --card:#151b31; --card2:#1b2340; --line:#2a3358;
    --text:#e8ecf8; --muted:#94a0c4; --ok:#2ecc8f; --fail:#ff5f6d;
    --warn:#ffb020; --crit:#ff5f6d; --info:#5aa9ff;
  }
  *{box-sizing:border-box}
  body{margin:0;background:radial-gradient(1200px 600px at 20% -10%,#1c2748 0%,var(--bg) 60%);
       color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans Thai",sans-serif}
  header{padding:22px 28px 10px;display:flex;flex-wrap:wrap;gap:16px;align-items:center;justify-content:space-between}
  h1{font-size:22px;margin:0;letter-spacing:.3px}
  h1 span{color:var(--muted);font-weight:400;font-size:14px;display:block;margin-top:4px}
  .pill{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:8px 16px;font-size:13px;color:var(--muted)}
  .pill b{color:var(--text)}
  .score{font-size:15px}
  .score.ok b{color:var(--ok)} .score.fail b{color:var(--fail)}
  main{padding:8px 28px 40px;max-width:1400px;margin:0 auto}
  .grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px;margin-bottom:26px}
  .card{background:linear-gradient(180deg,var(--card2),var(--card));border:1px solid var(--line);
        border-radius:14px;padding:16px 18px;position:relative;overflow:hidden}
  .card:before{content:"";position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--muted)}
  .card.ok:before{background:var(--ok)} .card.fail:before{background:var(--fail)}
  .card .n{font-size:12px;color:var(--muted);letter-spacing:1px}
  .card .t{font-size:15px;font-weight:600;margin:4px 0 10px}
  .card .v{font-size:24px;font-weight:700;margin-bottom:8px}
  .card.ok .v{color:var(--ok)} .card.fail .v{color:var(--fail)}
  .card .d{font-size:12px;color:var(--muted);line-height:1.55;word-break:break-word}
  .badge{position:absolute;right:14px;top:14px;font-size:11px;font-weight:700;letter-spacing:1px;
         padding:3px 9px;border-radius:999px}
  .ok .badge{background:rgba(46,204,143,.15);color:var(--ok);border:1px solid rgba(46,204,143,.4)}
  .fail .badge{background:rgba(255,95,109,.15);color:var(--fail);border:1px solid rgba(255,95,109,.4)}
  h2{font-size:16px;margin:0 0 12px;color:var(--muted);font-weight:600;letter-spacing:.4px}
  .feed{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
  .alert{background:var(--card);border:1px solid var(--line);border-left:5px solid var(--info);
         border-radius:12px;padding:13px 15px}
  .alert.firing.critical{border-left-color:var(--crit)}
  .alert.firing.warning{border-left-color:var(--warn)}
  .alert.resolved{border-left-color:var(--ok);opacity:.82}
  .alert .row{display:flex;gap:8px;align-items:center;justify-content:space-between;margin-bottom:6px}
  .alert .name{font-weight:700;font-size:15px}
  .st{font-size:11px;font-weight:700;letter-spacing:1px;padding:3px 9px;border-radius:999px}
  .st.firing{background:rgba(255,95,109,.16);color:var(--fail)}
  .st.resolved{background:rgba(46,204,143,.16);color:var(--ok)}
  .sum{font-size:13px;color:var(--text);margin-bottom:8px;line-height:1.5}
  .chips{display:flex;flex-wrap:wrap;gap:6px}
  .chip{font-size:11px;background:#0f1730;border:1px solid var(--line);color:var(--muted);
        padding:2px 8px;border-radius:6px;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
  .when{font-size:11px;color:var(--muted);margin-top:8px}
  .empty{border:1px dashed var(--line);border-radius:12px;padding:26px;text-align:center;color:var(--muted);font-size:14px}
  footer{color:var(--muted);font-size:12px;padding:0 28px 30px;max-width:1400px;margin:0 auto}
  .dot{display:inline-block;width:8px;height:8px;border-radius:50%;background:var(--ok);margin-right:6px;
       animation:blink 2s infinite}
  @keyframes blink{0%,100%{opacity:1}50%{opacity:.25}}
</style>
</head>
<body>
<header>
  <h1>LAB 6 — Observability Status Wall
    <span>receiver อ่านสถานะจาก Prometheus / Grafana / Alertmanager แล้ววาดสด ๆ ทุก 3 วินาที</span></h1>
  <div style="display:flex;gap:10px;flex-wrap:wrap">
    <div class="pill"><span class="dot"></span>อัปเดตล่าสุด <b id="ts">-</b></div>
    <div class="pill score" id="score">ผ่าน <b>-</b></div>
  </div>
</header>
<main>
  <div class="grid" id="cards"></div>
  <h2>ALERT ที่เดินทางมาถึง receiver (ล่าสุดอยู่บนสุด)</h2>
  <div class="feed" id="feed"></div>
</main>
<footer>POST /webhook = ปลายทางของ Alertmanager · GET /api/alerts = JSON ที่ check.sh ใช้ · GET /api/status = ผลตรวจ 5 ข้อฝั่ง server</footer>
<script>
function esc(s){return String(s==null?"":s).replace(/[&<>"]/g,function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;"}[c];});}

function drawStatus(d){
  document.getElementById("ts").textContent = new Date(d.generated*1000).toLocaleTimeString();
  var sc = document.getElementById("score");
  sc.className = "pill score " + (d.passed === d.total ? "ok" : "fail");
  sc.innerHTML = "ผ่าน <b>" + d.passed + "/" + d.total + "</b>";
  document.getElementById("cards").innerHTML = (d.checks||[]).map(function(c){
    return '<div class="card '+c.state+'">'+
      '<div class="badge">'+(c.state==="ok"?"OK":"FAIL")+'</div>'+
      '<div class="n">CHECK '+c.id+'</div>'+
      '<div class="t">'+esc(c.title)+'</div>'+
      '<div class="v">'+esc(c.value)+'</div>'+
      '<div class="d">'+esc(c.detail)+'</div></div>';
  }).join("");
}

function drawAlerts(d){
  var items = (d.alerts||[]).slice().reverse();
  var el = document.getElementById("feed");
  if(!items.length){ el.innerHTML = '<div class="empty">ยังไม่มี alert ใบไหนถูกส่งมาที่ /webhook</div>'; return; }
  el.innerHTML = items.map(function(a){
    var sev = (a.labels && a.labels.severity) || "info";
    var chips = Object.keys(a.labels||{}).map(function(k){
      return '<span class="chip">'+esc(k)+'='+esc(a.labels[k])+'</span>';}).join("");
    var summary = (a.annotations && (a.annotations.summary||a.annotations.description)) || "";
    return '<div class="alert '+esc(a.status)+' '+esc(sev)+'">'+
      '<div class="row"><span class="name">'+esc((a.labels||{}).alertname)+'</span>'+
      '<span class="st '+esc(a.status)+'">'+esc(a.status).toUpperCase()+'</span></div>'+
      (summary?'<div class="sum">'+esc(summary)+'</div>':'')+
      '<div class="chips">'+chips+'</div>'+
      '<div class="when">ถึง receiver เมื่อ '+esc(a.receivedAtHuman)+'</div></div>';
  }).join("");
}

function tick(){
  fetch("/api/status").then(function(r){return r.json();}).then(drawStatus).catch(function(){});
  fetch("/api/alerts").then(function(r){return r.json();}).then(drawAlerts).catch(function(){});
}
tick(); setInterval(tick, 3000);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "monlab6-receiver"

    def log_message(self, *args):
        pass

    def _send(self, status, body, ctype="application/json; charset=utf-8"):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self._send(200, PAGE, "text/html; charset=utf-8")
        elif path == "/api/alerts":
            with _lock:
                items = list(ALERTS)
            self._send(200, json.dumps({"count": len(items), "alerts": items}, ensure_ascii=False))
        elif path == "/api/status":
            self._send(200, json.dumps(cached_status(), ensure_ascii=False))
        elif path == "/healthz":
            self._send(200, '{"status":"ok"}')
        else:
            self._send(404, '{"error":"not found"}')

    def do_POST(self):
        if self.path.split("?", 1)[0] != "/webhook":
            self._send(404, '{"error":"not found"}')
            return
        length = int(self.headers.get("Content-Length", "0") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8", "replace"))
        except Exception:
            self._send(400, '{"error":"bad json"}')
            return

        now = time.time()
        stored = 0
        for a in payload.get("alerts", []):
            item = {
                "status": a.get("status", payload.get("status", "firing")),
                "labels": a.get("labels", {}),
                "annotations": a.get("annotations", {}),
                "startsAt": a.get("startsAt", ""),
                "endsAt": a.get("endsAt", ""),
                "receivedAt": now,
                "receivedAtHuman": time.strftime("%H:%M:%S", time.localtime(now)),
            }
            with _lock:
                ALERTS.append(item)
            stored += 1
            print(
                "[%s] %s %s severity=%s"
                % (item["receivedAtHuman"], item["status"].upper(),
                   item["labels"].get("alertname", "?"), item["labels"].get("severity", "-")),
                flush=True,
            )
        self._send(200, json.dumps({"received": stored}))


def main():
    print(f"monlab6-receiver listening on 0.0.0.0:{PORT}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
