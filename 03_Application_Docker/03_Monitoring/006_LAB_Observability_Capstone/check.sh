#!/usr/bin/env bash
#
# LAB 6 — Observability Capstone : acceptance check
#
# หลักการของ checker ตัวนี้: **ตัดสินที่พฤติกรรมจริงของระบบ ไม่ใช่ที่รูปแบบข้อความใน config**
# ทุกข้อจึงยิง HTTP API จริงและดูผลที่ได้กลับมา ไม่มีข้อไหนตัดสินด้วยการนับคำในไฟล์
#
#   1  target ทุกตัว health=up และ "ชุดชื่อ job" ตรงกับที่คาดไว้เป๊ะ (ขาดก็ไม่ผ่าน เกินก็ไม่ผ่าน)
#   2  app_requests_total มีข้อมูลจริงใน TSDB และ rate(...) > 0
#   3  dashboard uid=monlab6 มีอยู่จริงใน Grafana · datasource ที่มันอ้างต้องมีจริงและเป็นชนิด prometheus
#      · แล้ว **ยิง query ของทุก panel จริง** ต้องได้ข้อมูลกลับมาครบ (ครอบคลุม app_ / node_ / container_)
#   4  rule HighErrorRate ถูกโหลด และเมื่อ **ยิง expr ของมันจริง** ต้องได้ผลไม่ว่างและเป็นสัดส่วน (0-1]
#      (expr ที่คืน vector ว่างคือ expr ที่ไม่มีวันเป็น firing — ข้อนี้จับตรงนั้น)
#   5  rule HighErrorRate ต้อง firing อยู่ ณ ตอนนี้ **และ** event ล่าสุดของ HighErrorRate ที่ receiver
#      ได้รับต้องเป็น firing (ไม่ใช่ resolved และไม่ใช่แค่ "เคยเห็นชื่อนี้ผ่านมาในประวัติ")
#
# ทุก loop มีจุดจบเป็น **เวลาจริงบนนาฬิกา (wall clock)** ไม่ใช่การนับรอบ sleep
# ดังนั้นตัวเลขงบเวลาข้างล่างคือเพดานเวลาที่ใช้จริง รวมเวลาที่ค้างรอ HTTP ไปแล้ว
#
# ใช้แค่ bash + curl + python3 ที่มีอยู่แล้วในเครื่องเรียน (ไม่ต้องติดตั้ง jq)
# exit code : 0 = ผ่านครบ 5 ข้อ, 1 = มีข้อที่ไม่ผ่าน

set -u

PROM_URL="${PROM_URL:-http://localhost:9090}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"
GF_AUTH="${GF_AUTH:-admin:admin}"
RECEIVER_URL="${RECEIVER_URL:-http://localhost:5001}"

# ชุด job ที่ต้องมีครบพอดี (เทียบแบบ set: ขาดก็ไม่ผ่าน เกินมาก็ไม่ผ่าน)
EXPECTED_JOBS="${EXPECTED_JOBS:-alertmanager,app,cadvisor,node,prometheus}"
DASH_UID="${DASH_UID:-monlab6}"
ALERT_NAME="${ALERT_NAME:-HighErrorRate}"

# งบเวลา (วินาที) ของแต่ละข้อ — นับด้วยนาฬิกาจริง ครอบคลุมทั้ง sleep และเวลาที่ HTTP ค้าง
BUDGET_READY="${BUDGET_READY:-120}"    # รอทุกบริการพร้อมและ Prometheus ได้ลอง scrape ครบหนึ่งรอบ
BUDGET_TARGETS="${BUDGET_TARGETS:-30}" # รอ scrape รอบใหม่หลังแก้ config
BUDGET_METRICS="${BUDGET_METRICS:-30}" # รอ rate() มีค่า (ต้องมีอย่างน้อย 2 sample ในหน้าต่าง)
BUDGET_GRAFANA="${BUDGET_GRAFANA:-25}" # รอ dashboard provider อ่านไฟล์ใหม่ (ตั้งไว้ทุก 10 วินาที)
BUDGET_RULE="${BUDGET_RULE:-45}"       # รอ reload + rule ถูกประเมินด้วยข้อมูลที่มีจริง
BUDGET_ALERT="${BUDGET_ALERT:-150}"    # รอ for: 20s + group_wait + (กรณีแย่สุด) repeat_interval
HTTP_TIMEOUT="${HTTP_TIMEOUT:-5}"      # timeout ต่อหนึ่ง request
RETRY_SLEEP="${RETRY_SLEEP:-3}"

export PROM_URL GRAFANA_URL GF_AUTH RECEIVER_URL EXPECTED_JOBS DASH_UID ALERT_NAME HTTP_TIMEOUT RETRY_SLEEP

GREEN=$'\033[0;32m'; RED=$'\033[0;31m'; CYAN=$'\033[0;36m'; DIM=$'\033[2m'; RESET=$'\033[0m'
PASS=0; FAIL=0; TOTAL=5

ok()   { PASS=$((PASS+1)); printf "%sOK  %s  [%s/5] %s\n" "$GREEN" "$RESET" "$1" "$2"; }
bad()  { FAIL=$((FAIL+1)); printf "%sFAIL%s  [%s/5] %s\n" "$RED" "$RESET" "$1" "$2"; }
note() { printf "        %s%s%s\n" "$DIM" "$1" "$RESET"; }

cget() { curl -sS --max-time "$HTTP_TIMEOUT" "$@" 2>/dev/null; }

tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

printf "%sLAB6 acceptance check%s\n" "$CYAN" "$RESET"
printf "  Prometheus  %s\n  Grafana     %s\n  Receiver    %s\n\n" \
       "$PROM_URL" "$GRAFANA_URL" "$RECEIVER_URL"

# ---------------------------------------------------------------- ตัวตรวจฝั่ง python
# เขียนลงไฟล์ชั่วคราวแล้วเรียกทีละข้อ (python3 อ่าน JSON และยิง query ได้โดยไม่ต้องพึ่ง jq)
cat > "$tmp/checks.py" <<'PYEOF'
#!/usr/bin/env python3
"""ตัวตรวจของ LAB 6 — เรียกจาก check.sh ทีละข้อ: python3 checks.py <1..5>

ทุกข้อคืนผลออกทาง stdout บรรทัดแรกเป็น "PASS<TAB>ข้อความสรุป"
บรรทัดถัดไปคือหมายเหตุ (check.sh เอาไปพิมพ์เป็นบรรทัด note)
exit code 0 = ผ่าน, 1 = ไม่ผ่าน
"""
import base64
import json
import math
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

PROM = os.environ.get("PROM_URL", "http://localhost:9090")
GRAFANA = os.environ.get("GRAFANA_URL", "http://localhost:3000")
RECEIVER = os.environ.get("RECEIVER_URL", "http://localhost:5001")
GF_AUTH = os.environ.get("GF_AUTH", "admin:admin")
DASH_UID = os.environ.get("DASH_UID", "monlab6")
ALERTNAME = os.environ.get("ALERT_NAME", "HighErrorRate")
WANT_JOBS = {j.strip() for j in os.environ.get(
    "EXPECTED_JOBS", "alertmanager,app,cadvisor,node,prometheus").split(",") if j.strip()}
HTTP_TIMEOUT = float(os.environ.get("HTTP_TIMEOUT", "5"))
RETRY_SLEEP = float(os.environ.get("RETRY_SLEEP", "3"))
BUDGET = float(os.environ.get("CHECK_BUDGET", "30"))

# สัดส่วน error ที่ระบบมีอยู่จริง ใช้เป็น "ความจริงอ้างอิง" เวลาอธิบายว่าทำไม rule ถึงควรยิง
GROUND_TRUTH = 'sum(rate(app_requests_total{status=~"5.."}[1m])) / sum(rate(app_requests_total[1m]))'


# ---------------------------------------------------------------- HTTP helpers
def fetch(url, auth=None):
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    if auth:
        req.add_header("Authorization", "Basic " + base64.b64encode(auth.encode()).decode())
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:
        return 0, str(e)


def fetch_json(url, auth=None):
    code, body = fetch(url, auth)
    try:
        return code, json.loads(body)
    except Exception:
        return code, None


def promq(expr):
    """ยิง query จริงไปที่ Prometheus — คืน (samples, err) โดย samples = [(labels, float), ...]"""
    url = PROM + "/api/v1/query?" + urllib.parse.urlencode({"query": expr})
    code, data = fetch_json(url)
    if data is None:
        return None, "ติดต่อ Prometheus ไม่ได้ (HTTP %s)" % code
    if data.get("status") != "success":
        return None, str(data.get("error", "query ไม่สำเร็จ"))[:150]
    out = []
    for s in data.get("data", {}).get("result", []):
        try:
            v = float(s.get("value", [0, "nan"])[1])
        except Exception:
            v = float("nan")
        out.append((s.get("metric", {}), v))
    return out, ""


def has_data(samples):
    """ผลที่ใช้งานได้จริง = ต้องมี series และต้องมีค่าที่ไม่ใช่ NaN อย่างน้อยหนึ่งค่า"""
    return bool(samples) and any(not math.isnan(v) for _, v in samples)


def first_value(samples):
    for _, v in samples or []:
        if not math.isnan(v):
            return v
    return None


# ---------------------------------------------------------------- 1. targets
def check1():
    code, d = fetch_json(PROM + "/api/v1/targets?state=any")
    if d is None:
        return False, "อ่าน /api/v1/targets ไม่ได้ (HTTP %s)" % code, []
    active = d.get("data", {}).get("activeTargets", [])
    jobs = {t.get("labels", {}).get("job", "?") for t in active}
    up = [t for t in active if t.get("health") == "up"]
    missing = sorted(WANT_JOBS - jobs)
    extra = sorted(jobs - WANT_JOBS)
    down = ["job %s -> %s : %s" % (t.get("labels", {}).get("job", "?"), t.get("scrapeUrl", ""),
                                   (t.get("lastError") or "no error")[:70])
            for t in active if t.get("health") != "up"]
    good = bool(active) and not missing and not extra and len(up) == len(active)
    joblist = ",".join(sorted(jobs)) or "-"
    if good:
        return True, "targets ทุกตัว health=up : %d/%d target และชุด job ตรงกับที่คาดไว้ครบ" % (
            len(up), len(active)), ["job: " + joblist]
    notes = ["job ที่เห็นตอนนี้: " + joblist]
    if missing:
        notes.append("job ที่ขาดไป: " + ",".join(missing))
    if extra:
        notes.append("job ที่เกินมา: " + ",".join(extra))
    notes.extend("ตัวที่ล้ม: " + b for b in down)
    return False, "targets: expected job = {%s} และ up ครบทุกตัว, got %d/%d up จาก job {%s}" % (
        ",".join(sorted(WANT_JOBS)), len(up), len(active), joblist), notes


# ---------------------------------------------------------------- 2. app metrics
def check2():
    rate, err = promq("sum(rate(app_requests_total[30s]))")
    series, _ = promq("count(app_requests_total)")
    n = first_value(series)
    n = int(n) if n is not None else 0
    v = first_value(rate)
    if err:
        return False, "app_requests_total: query ไม่สำเร็จ (%s)" % err, []
    if v is None or v <= 0:
        return False, "app_requests_total: expected rate > 0, got %s (จำนวน series = %d)" % (
            "'none'" if v is None else "%.4f" % v, n), [
            "ถ้าเป็น none แปลว่า Prometheus ไม่มีข้อมูลของเมตริกนี้เลย ให้ย้อนไปดูข้อ 1 ก่อน"]
    return True, "app_requests_total มีข้อมูลจริง : rate = %.2f req/s (%d series)" % (v, n), []


# ---------------------------------------------------------------- 3. grafana dashboard
DS_SKIP = {"grafana", "-- Grafana --", "-- Mixed --", "-- Dashboard --"}
FAMILIES = [("app_", "แอป (app)"), ("node_", "node-exporter"), ("container_", "cAdvisor")]


def walk_ds(node, found):
    """เดินทั้ง JSON ของ dashboard เก็บ datasource uid ที่ถูกอ้างถึง"""
    if isinstance(node, dict):
        ds = node.get("datasource")
        if isinstance(ds, dict) and isinstance(ds.get("uid"), str):
            found.add(ds["uid"])
        elif isinstance(ds, str) and ds:
            found.add(ds)
        for v in node.values():
            walk_ds(v, found)
    elif isinstance(node, list):
        for v in node:
            walk_ds(v, found)


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


def check3():
    code, health = fetch_json(GRAFANA + "/api/health")
    db = (health or {}).get("database", "?") if isinstance(health, dict) else "unreachable"
    if db != "ok":
        return False, "Grafana /api/health: expected database=ok, got '%s'" % db, []

    code, ds_list = fetch_json(GRAFANA + "/api/datasources", GF_AUTH)
    if not isinstance(ds_list, list):
        return False, "อ่าน /api/datasources ไม่ได้ (HTTP %s)" % code, [
            "endpoint นี้ต้องสิทธิ์ admin — ตรวจค่า GF_AUTH (ค่าเริ่มต้นคือ admin:admin)"]
    ds_by_uid = {d.get("uid"): d for d in ds_list if isinstance(d, dict)}

    code, board = fetch_json(GRAFANA + "/api/dashboards/uid/" + DASH_UID, GF_AUTH)
    if code != 200 or not isinstance(board, dict) or not isinstance(board.get("dashboard"), dict):
        return False, "ไม่พบ dashboard uid '%s' ใน Grafana (HTTP %s)" % (DASH_UID, code), [
            "dashboard ของแล็บนี้ต้องมี uid = %s (ดูคีย์ \"uid\" ท้ายไฟล์ grafana/dashboards/overview.json)" % DASH_UID,
            "provider อ่านไฟล์ใหม่ทุก 10 วินาที ถ้า JSON ผิดรูปจะไม่ถูกโหลด — ดู docker compose logs --tail 20 grafana"]
    dash = board["dashboard"]

    want = set()
    walk_ds(dash, want)
    want = {u for u in want if isinstance(u, str) and u and not u.startswith("$") and u not in DS_SKIP}
    missing = sorted(u for u in want if u not in ds_by_uid)
    wrong = sorted("%s (type=%s)" % (u, ds_by_uid[u].get("type"))
                   for u in want if u in ds_by_uid and ds_by_uid[u].get("type") != "prometheus")
    have = ",".join(sorted(ds_by_uid)) or "-"
    if missing:
        return False, "dashboard '%s' อ้าง datasource uid ที่ไม่มีอยู่จริง: %s" % (DASH_UID, ",".join(missing)), [
            "dashboard อ้าง uid : " + (",".join(sorted(want)) or "-"),
            "datasource ที่มีจริง: " + have]
    if wrong:
        return False, "datasource ที่ dashboard อ้างไม่ใช่ชนิด prometheus: %s" % ",".join(wrong), [
            "datasource ที่มีจริง: " + have]

    queries = []
    collect_queries(dash.get("panels"), queries)
    queries = [(t, e, u) for (t, e, u) in queries if not (isinstance(u, str) and u in DS_SKIP)]
    if not queries:
        return False, "dashboard '%s' ไม่มี panel ที่ query อะไรเลย" % DASH_UID, []

    empty, errors, ok_exprs = [], [], []
    for title, expr, _uid in queries:
        samples, err = promq(expr)
        if samples is None:
            errors.append("%s -> %s" % (title, err))
        elif not has_data(samples):
            empty.append("%s -> %s" % (title, expr[:80]))
        else:
            ok_exprs.append(expr)
    if errors:
        return False, "query ของ panel ยิงไม่ผ่าน %d รายการ (Prometheus ปฏิเสธ expr)" % len(errors), \
            ["ยิงไม่ผ่าน: " + e for e in errors[:4]]
    if empty:
        return False, "panel %d/%d รายการ query แล้วไม่ได้ข้อมูลกลับมา (dashboard จะขึ้น No data)" % (
            len(empty), len(queries)), ["ไม่มีข้อมูล: " + e for e in empty[:4]] + [
            "ตรวจว่าชื่อเมตริกใน expr สะกดถูกและมีอยู่จริงใน Prometheus"]
    blob = " ".join(ok_exprs)
    lack = [label for prefix, label in FAMILIES if prefix not in blob]
    if lack:
        return False, "dashboard ยังไม่ครอบคลุมแหล่งข้อมูลครบ: ขาด %s" % ", ".join(lack), [
            "capstone ต้องมี panel ที่ใช้ทั้ง app_* (แอป), node_* (node-exporter) และ container_* (cAdvisor)"]
    return True, "dashboard '%s' ใช้ datasource ชนิด prometheus (%s) และ query ของ panel ทั้ง %d รายการได้ข้อมูลจริง" % (
        DASH_UID, ",".join(sorted(want)) or "-", len(queries)), [
        "ครอบคลุม: " + ", ".join(label for _p, label in FAMILIES)]


# ---------------------------------------------------------------- 4. alert rule
RANGE_FN = re.compile(r"\b(rate|irate|increase)\s*\(")
CMP_OP = re.compile(r"(>=|<=|==|!=|>|<)")


def find_rule():
    code, d = fetch_json(PROM + "/api/v1/rules")
    if d is None:
        return None, "อ่าน /api/v1/rules ไม่ได้ (HTTP %s)" % code
    for g in d.get("data", {}).get("groups", []):
        for r in g.get("rules", []):
            if r.get("name") == ALERTNAME:
                return r, ""
    return None, "ไม่พบ rule ชื่อ %s ใน /api/v1/rules" % ALERTNAME


def check4():
    rule, err = find_rule()
    if rule is None:
        return False, "rule %s: %s" % (ALERTNAME, err), []
    expr = rule.get("query", "")
    state = rule.get("state", "?")
    notes = ["expr: " + expr]

    samples, qerr = promq(expr)
    if samples is None:
        return False, "rule %s: เอา expr ไปยิงเป็น query แล้วไม่ผ่าน (%s)" % (ALERTNAME, qerr), notes
    if not has_data(samples):
        notes.append("ยิง expr นี้ตรง ๆ ที่ /api/v1/query แล้วได้ result ว่าง")
        notes.append("expr ที่คืน vector ว่างจะไม่มีวันเปลี่ยนเป็น firing ได้เลย")
        g, _ = promq(GROUND_TRUTH)
        gv = first_value(g)
        if gv is None:
            notes.append("ตอนนี้ Prometheus ยังไม่มีเมตริกของแอปให้ประเมินเลย ให้ย้อนไปดูข้อ 1 และ 2 ก่อน")
        else:
            notes.append("สัดส่วน error จริงของระบบตอนนี้ = %.4f — ข้อมูลมีให้ประเมิน แต่ expr ของ rule กลับคืนค่าว่าง" % gv)
        return False, "rule %s: expected expr ที่ประเมินแล้วได้ผลจริง, got vector ว่าง (state=%s)" % (
            ALERTNAME, state), notes

    vals = [v for _lbl, v in samples if not math.isnan(v)]
    out_of_range = [v for v in vals if not (0 < v <= 1.0)]
    if out_of_range:
        notes.append("ค่าที่ควรได้คือ 'สัดส่วน' เช่น 0.10 = 10% ไม่ใช่จำนวน error ต่อวินาที และไม่ใช่หน่วยเปอร์เซ็นต์")
        return False, "rule %s: expected ผลของ expr เป็นสัดส่วนในช่วง (0,1], got %s" % (
            ALERTNAME, ", ".join("%.4f" % v for v in out_of_range[:3])), notes
    if not RANGE_FN.search(expr):
        notes.append("counter ดิบบอกได้แค่ 'รวมทั้งชีวิตของโปรเซส' ไม่ได้บอกว่า 'ตอนนี้แย่แค่ไหน'")
        return False, "rule %s: expected คิดจากอัตราในช่วงเวลา (rate/irate/increase), got expr ที่ใช้ค่าดิบของ counter" % ALERTNAME, notes
    if not CMP_OP.search(expr):
        notes.append("expr ที่ไม่มีเกณฑ์เปรียบเทียบจะคืนค่าตลอดเวลา = alert ยิงตลอดเวลา")
        return False, "rule %s: expected มีเกณฑ์เปรียบเทียบ (เช่น > 0.05), got expr ที่ไม่มีเกณฑ์" % ALERTNAME, notes

    g, _ = promq(GROUND_TRUTH)
    gv = first_value(g)
    if gv is not None:
        notes.append("เทียบกับความจริง: สัดส่วน error ของระบบตอนนี้ = %.4f" % gv)
    return True, "rule %s ประเมินได้จริง : ยิง expr แล้วได้ค่า %.4f (state=%s)" % (
        ALERTNAME, vals[0], state), notes


# ---------------------------------------------------------------- 5. alert ถึง receiver
def check5():
    rule, rerr = find_rule()
    state = rule.get("state", "?") if rule else "-"
    code, d = fetch_json(RECEIVER + "/api/alerts")
    if not isinstance(d, dict):
        return False, "อ่าน /api/alerts ของ receiver ไม่ได้ (HTTP %s)" % code, []
    items = d.get("alerts", [])
    names = sorted({a.get("labels", {}).get("alertname", "?") for a in items})
    mine = [a for a in items if a.get("labels", {}).get("alertname") == ALERTNAME]
    last = mine[-1] if mine else None
    last_status = last.get("status", "?") if last else "-"

    notes = ["alert ที่ receiver ได้รับทั้งหมด %d ใบ (ชนิด: %s)" % (len(items), ",".join(names) or "-"),
             "สถานะ rule ตอนนี้: %s%s" % (state, "" if rule else " (%s)" % rerr)]
    if rule is not None and state == "firing" and last is not None and last_status == "firing":
        return True, "%s กำลัง firing และ event ล่าสุดที่ receiver ได้รับเป็น firing (เมื่อ %s)" % (
            ALERTNAME, last.get("receivedAtHuman", "?")), notes

    if rule is None or state != "firing":
        notes.append("ข้อนี้ต้องการ rule ที่ firing 'อยู่ตอนนี้' ไม่ใช่แค่เคยยิงแล้วหายไป")
        return False, "%s: expected rule state=firing, got '%s'" % (ALERTNAME, state), notes
    if last is None:
        notes.append("rule firing แล้วแต่ยังไม่มี event เดินทางมาถึง — ดู docker compose logs alertmanager receiver")
        return False, "%s: rule firing แล้วแต่ receiver ยังไม่ได้รับ alert ชนิดนี้เลย" % ALERTNAME, notes
    notes.append("event ล่าสุดของ %s เป็น '%s' เมื่อ %s — ประวัติเก่าที่ resolved ไปแล้วไม่นับว่าผ่าน" % (
        ALERTNAME, last_status, last.get("receivedAtHuman", "?")))
    return False, "%s: expected event ล่าสุดที่ receiver ได้รับเป็น firing, got '%s'" % (
        ALERTNAME, last_status), notes


# ---------------------------------------------------------------- main
CHECKS = {"1": check1, "2": check2, "3": check3, "4": check4, "5": check5}


def main():
    fn = CHECKS[sys.argv[1]]
    started = time.time()
    end = started + BUDGET
    tries = 0
    while True:
        tries += 1
        try:
            good, headline, notes = fn()
        except Exception as e:  # ตัวตรวจต้องไม่ระเบิดใส่ผู้เรียน
            good, headline, notes = False, "ตัวตรวจข้อนี้มีข้อผิดพลาด: %s" % str(e)[:150], []
        if good or time.time() >= end:
            break
        time.sleep(RETRY_SLEEP)
    notes = list(notes)
    if not good and tries > 1:
        notes.append("ลองซ้ำ %d ครั้งในเวลา %d วินาที (นับด้วยนาฬิกาจริง) แล้วยังไม่ผ่าน" % (
            tries, int(time.time() - started)))
    sys.stdout.write(("PASS" if good else "FAIL") + "\t" + headline + "\n")
    for n in notes:
        sys.stdout.write(str(n) + "\n")
    sys.exit(0 if good else 1)


main()
PYEOF

# รันตัวตรวจหนึ่งข้อ: run_check <หมายเลขข้อ> <งบเวลาวินาที>  → คืน 0 เมื่อผ่าน
run_check() {
  local n="$1" budget="$2" out="$tmp/out.$1" rc verdict headline
  CHECK_BUDGET="$budget" python3 "$tmp/checks.py" "$n" > "$out" 2>"$tmp/err.$1"
  rc=$?
  if [ ! -s "$out" ]; then
    bad "$n" "ตัวตรวจข้อนี้ไม่ตอบอะไรกลับมา (python3 exit=$rc)"
    note "$(tail -n 2 "$tmp/err.$1" | tr '\n' ' ')"
    return 1
  fi
  verdict=$(head -n 1 "$out" | cut -f1)
  headline=$(head -n 1 "$out" | cut -f2-)
  if [ "$verdict" = "PASS" ]; then ok "$n" "$headline"; else bad "$n" "$headline"; fi
  tail -n +2 "$out" | while IFS= read -r line; do note "$line"; done
  [ "$verdict" = "PASS" ]
}

# ---------------------------------------------------------------- readiness (bounded ด้วยนาฬิกาจริง)
ready=0
ready_start=$(date +%s)
ready_end=$(( ready_start + BUDGET_READY ))
while :; do
  p=$(cget -o /dev/null -w '%{http_code}' "$PROM_URL/-/ready")
  g=$(cget -o /dev/null -w '%{http_code}' "$GRAFANA_URL/api/health")
  r=$(cget -o /dev/null -w '%{http_code}' "$RECEIVER_URL/api/alerts")
  a=$(cget -o /dev/null -w '%{http_code}' "$PROM_URL/api/v1/alertmanagers")
  if [ "$p" = "200" ] && [ "$g" = "200" ] && [ "$r" = "200" ] && [ "$a" = "200" ]; then
    # รอจน Prometheus ได้ลอง scrape ทุก target อย่างน้อยหนึ่งรอบ (สำเร็จหรือล้มก็ได้)
    scraped=$(cget "$PROM_URL/api/v1/targets?state=any" | python3 -c '
import json,sys
try: d=json.load(sys.stdin)
except Exception: print("0 1"); raise SystemExit
a=d.get("data",{}).get("activeTargets",[])
done=[t for t in a if not str(t.get("lastScrape","")).startswith("0001")]
print("%d %d"%(len(done),max(len(a),1)))
')
    set -- $scraped
    if [ "${1:-0}" -ge "${2:-1}" ]; then ready=1; break; fi
  fi
  [ "$(date +%s)" -ge "$ready_end" ] && break
  sleep 2
done
if [ "$ready" -eq 1 ]; then
  printf "ระบบพร้อมตรวจแล้ว (ใช้เวลา ~%s วินาที)\n\n" "$(( $(date +%s) - ready_start ))"
else
  printf "%sWARN%s  ระบบยังไม่พร้อมครบภายใน %s วินาที — ตรวจต่อไปแต่ผลอาจเป็นแค่ startup noise\n\n" \
         "$RED" "$RESET" "$BUDGET_READY"
fi

# ---------------------------------------------------------------- ตรวจทีละข้อ
run_check 1 "$BUDGET_TARGETS"
run_check 2 "$BUDGET_METRICS"; metrics_ok=$?
run_check 3 "$BUDGET_GRAFANA"

# ถ้าไม่มีเมตริกของแอปเลย rule นี้ประเมินไม่ได้และ alert ไม่มีทางยิง — ไม่ต้องรอจนครบงบเวลา
b4="$BUDGET_RULE"; b5="$BUDGET_ALERT"
if [ "$metrics_ok" -ne 0 ]; then b4=5; b5=5; fi

run_check 4 "$b4"; rule_ok=$?
# rule ที่ยังประเมินไม่ได้ ก็ไม่มีวัน firing เช่นกัน
[ "$rule_ok" -ne 0 ] && b5=5
run_check 5 "$b5"

# ---------------------------------------------------------------- สรุป
printf "\n"
if [ "$FAIL" -eq 0 ]; then
  printf "%sResult: %d/%d OK%s\n" "$GREEN" "$PASS" "$TOTAL" "$RESET"
else
  printf "%sResult: expected %d/%d OK, got %d/%d%s\n" "$RED" "$TOTAL" "$TOTAL" "$PASS" "$TOTAL" "$RESET"
fi
[ "$FAIL" -eq 0 ]
