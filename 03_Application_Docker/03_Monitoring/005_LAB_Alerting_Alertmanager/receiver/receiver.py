#!/usr/bin/env python3
"""
LAB 5 — Alert Receiver

รับ webhook จาก Alertmanager แล้วโชว์เป็นหน้าเว็บให้เห็นด้วยตาว่า
"แจ้งเตือนออกจากระบบจริง" ไม่ใช่แค่ตัวอักษรในหน้า /alerts ของ Prometheus

  POST /webhook      รับ payload (Alertmanager webhook v4) เก็บไว้ในหน่วยความจำ
  GET  /             หน้า UI (inline CSS/JS ทั้งหมด — ไม่มี CDN ไม่มีไฟล์ภายนอก)
  GET  /api/alerts   JSON สำหรับตรวจอัตโนมัติ
  GET  /healthz      liveness

ข้อควรระวังที่ทำตามจริงในโค้ดนี้:
  * handler ต้องตอบ 2xx เร็ว ห้ามทำงานหนัก ไม่งั้น Alertmanager จะ retry ซ้ำ
  * เก็บ state ใน memory เท่านั้น — restart แล้วหาย (พอสำหรับห้องเรียน)
"""

import json
import os
import threading
import time
from collections import OrderedDict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = int(os.getenv("PORT", "5001"))
MAX_PAYLOADS = int(os.getenv("MAX_PAYLOADS", "200"))

_lock = threading.Lock()
_payloads = []          # ประวัติ payload ที่ได้รับ (ใหม่สุดอยู่ท้าย)
_alerts = OrderedDict()  # fingerprint -> สถานะล่าสุดของ alert ใบนั้น
_seq = 0


def record(payload: dict):
    """เก็บ payload หนึ่งใบ + อัปเดตสถานะ alert รายใบ (เร็ว ๆ ไม่บล็อก)"""
    global _seq
    now = time.time()
    with _lock:
        _seq += 1
        entry = {
            "seq": _seq,
            "received_at": now,
            "receiver": payload.get("receiver", "?"),
            "status": payload.get("status", "?"),
            "group_key": payload.get("groupKey", ""),
            "group_labels": payload.get("groupLabels", {}) or {},
            "num_alerts": len(payload.get("alerts", []) or []),
        }
        _payloads.append(entry)
        del _payloads[:-MAX_PAYLOADS]

        for alert in payload.get("alerts", []) or []:
            labels = alert.get("labels", {}) or {}
            fp = alert.get("fingerprint") or json.dumps(labels, sort_keys=True)
            _alerts[fp] = {
                "fingerprint": fp,
                "status": alert.get("status", payload.get("status", "?")),
                "labels": labels,
                "annotations": alert.get("annotations", {}) or {},
                "startsAt": alert.get("startsAt", ""),
                "endsAt": alert.get("endsAt", ""),
                "generatorURL": alert.get("generatorURL", ""),
                "receiver": entry["receiver"],
                "group_key": entry["group_key"],
                "received_at": now,
                "seq": _seq,
            }
            _alerts.move_to_end(fp)


def snapshot() -> dict:
    with _lock:
        alerts = list(_alerts.values())
        payloads = list(_payloads)
    firing = sum(1 for a in alerts if a["status"] == "firing")
    resolved = sum(1 for a in alerts if a["status"] == "resolved")
    return {
        "payloads_received": len(payloads),
        "alert_count": len(alerts),
        "firing": firing,
        "resolved": resolved,
        "server_time": time.time(),
        "alerts": sorted(alerts, key=lambda a: -a["seq"]),
        "feed": list(reversed(payloads))[:40],
    }


PAGE = r"""<!doctype html>
<html lang="th">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Alert Receiver — LAB 5</title>
<style>
  *,*::before,*::after{box-sizing:border-box}
  :root{
    --bg:#0b1020; --bg2:#111a33; --panel:#151f3a; --panel2:#1b2748;
    --line:#26325a; --txt:#e8ecf8; --muted:#93a0c4;
    --crit:#f43f5e; --warn:#f59e0b; --info:#38bdf8; --ok:#22c55e;
  }
  body{
    margin:0; min-height:100vh; color:var(--txt);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans Thai",Tahoma,sans-serif;
    background:
      radial-gradient(1100px 520px at 12% -10%, #1e2a55 0%, transparent 60%),
      radial-gradient(900px 480px at 92% 0%, #2a1740 0%, transparent 55%),
      linear-gradient(180deg,var(--bg) 0%,var(--bg2) 100%);
    background-attachment:fixed;
  }
  .wrap{max-width:1320px;margin:0 auto;padding:26px 22px 44px}
  header{display:flex;flex-wrap:wrap;gap:14px;align-items:center;justify-content:space-between;margin-bottom:20px}
  .brand{display:flex;align-items:center;gap:14px}
  .logo{
    width:48px;height:48px;border-radius:14px;display:grid;place-items:center;font-size:24px;
    background:linear-gradient(135deg,#f43f5e,#f59e0b);box-shadow:0 8px 26px rgba(244,63,94,.35)
  }
  h1{margin:0;font-size:21px;letter-spacing:.2px}
  .sub{margin:3px 0 0;color:var(--muted);font-size:12.5px}
  .live{display:flex;align-items:center;gap:8px;font-size:12.5px;color:var(--muted);
    background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:999px;padding:7px 14px}
  .dot{width:9px;height:9px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 0 rgba(34,197,94,.7);animation:pulse 2s infinite}
  @keyframes pulse{70%{box-shadow:0 0 0 9px rgba(34,197,94,0)}100%{box-shadow:0 0 0 0 rgba(34,197,94,0)}}

  .stats{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:14px;margin-bottom:22px}
  .stat{background:linear-gradient(180deg,var(--panel) 0%,var(--panel2) 100%);
    border:1px solid var(--line);border-radius:16px;padding:16px 18px;position:relative;overflow:hidden}
  .stat::after{content:"";position:absolute;inset:0 0 auto 0;height:3px;background:var(--info);opacity:.85}
  .stat.f::after{background:var(--crit)} .stat.r::after{background:var(--ok)} .stat.p::after{background:var(--warn)}
  .stat .k{color:var(--muted);font-size:11.5px;text-transform:uppercase;letter-spacing:1.1px}
  .stat .v{font-size:32px;font-weight:700;margin-top:6px;line-height:1;font-variant-numeric:tabular-nums}
  .stat .n{color:var(--muted);font-size:11.5px;margin-top:6px}

  .cols{display:grid;grid-template-columns:1fr 340px;gap:18px;align-items:start}
  .panel{background:rgba(21,31,58,.72);border:1px solid var(--line);border-radius:18px;padding:16px 18px}
  .panel h2{margin:0 0 12px;font-size:13px;letter-spacing:1.2px;text-transform:uppercase;color:var(--muted)}

  .cards{display:flex;flex-direction:column;gap:13px}
  .card{
    border:1px solid var(--line);border-left:5px solid var(--info);border-radius:14px;
    background:linear-gradient(180deg,rgba(27,39,72,.95) 0%,rgba(21,31,58,.95) 100%);
    padding:14px 16px;animation:in .25s ease
  }
  @keyframes in{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}
  .card.sev-critical{border-left-color:var(--crit)}
  .card.sev-warning{border-left-color:var(--warn)}
  .card.resolved{border-left-color:var(--ok);opacity:.82}
  .crow{display:flex;flex-wrap:wrap;gap:10px;align-items:center;justify-content:space-between}
  .name{font-size:16.5px;font-weight:700;letter-spacing:.2px}
  .pill{font-size:10.5px;font-weight:800;letter-spacing:1.3px;padding:5px 11px;border-radius:999px;text-transform:uppercase}
  .pill.firing{background:rgba(244,63,94,.16);color:#ff8ba0;border:1px solid rgba(244,63,94,.45)}
  .pill.resolved{background:rgba(34,197,94,.14);color:#7ee2a8;border:1px solid rgba(34,197,94,.45)}
  .sev{font-size:10.5px;font-weight:700;letter-spacing:1.1px;padding:5px 10px;border-radius:8px;text-transform:uppercase}
  .sev.critical{background:rgba(244,63,94,.16);color:#ff8ba0}
  .sev.warning{background:rgba(245,158,11,.16);color:#ffd08a}
  .sev.other{background:rgba(56,189,248,.14);color:#9adcff}
  .summary{margin:10px 0 0;font-size:14px;line-height:1.6}
  .desc{margin:5px 0 0;color:var(--muted);font-size:12.5px;line-height:1.65}
  .chips{display:flex;flex-wrap:wrap;gap:7px;margin-top:12px}
  .chip{font-size:11.5px;background:rgba(255,255,255,.05);border:1px solid var(--line);
    border-radius:8px;padding:4px 9px;color:#c7d2f0;font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
  .chip b{color:#8fa6df;font-weight:600}
  .meta{display:flex;flex-wrap:wrap;gap:16px;margin-top:12px;padding-top:11px;border-top:1px dashed var(--line);
    color:var(--muted);font-size:11.5px}
  .meta b{color:#cbd6f5;font-weight:600}

  .feed{display:flex;flex-direction:column;gap:9px;max-height:70vh;overflow:auto}
  .fitem{display:flex;gap:11px;align-items:flex-start;font-size:12px;padding:9px 10px;border-radius:11px;
    background:rgba(255,255,255,.035);border:1px solid var(--line)}
  .fdot{width:9px;height:9px;border-radius:50%;margin-top:5px;flex:0 0 9px;background:var(--crit)}
  .fitem.resolved .fdot{background:var(--ok)}
  .fmain{min-width:0}
  .fmain .t{color:#dbe3fb;font-weight:600}
  .fmain .s{color:var(--muted);margin-top:3px;word-break:break-word;font-family:ui-monospace,Menlo,monospace;font-size:11px}
  .empty{color:var(--muted);font-size:13px;text-align:center;padding:34px 10px;line-height:1.8;
    border:1px dashed var(--line);border-radius:14px}
  footer{margin-top:22px;color:var(--muted);font-size:11.5px;text-align:center}
  @media(max-width:960px){.cols{grid-template-columns:1fr}.stats{grid-template-columns:repeat(2,1fr)}}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div class="brand">
      <div class="logo">🔔</div>
      <div>
        <h1>Alert Receiver — LAB 5</h1>
        <p class="sub">webhook ปลายทางของ Alertmanager · เก็บใน memory · รีเฟรชเองทุก 2 วินาที</p>
      </div>
    </div>
    <div class="live"><span class="dot"></span><span id="clock">กำลังเชื่อมต่อ…</span></div>
  </header>

  <div class="stats">
    <div class="stat f"><div class="k">Firing ตอนนี้</div><div class="v" id="s-firing">–</div><div class="n">alert ที่ยังไม่คลี่คลาย</div></div>
    <div class="stat r"><div class="k">Resolved</div><div class="v" id="s-resolved">–</div><div class="n">กลับสู่ปกติแล้ว</div></div>
    <div class="stat p"><div class="k">Payload ที่รับ</div><div class="v" id="s-payloads">–</div><div class="n">จำนวนครั้งที่ POST /webhook</div></div>
    <div class="stat"><div class="k">รับล่าสุดเมื่อ</div><div class="v" id="s-last">–</div><div class="n">วินาทีที่แล้ว</div></div>
  </div>

  <div class="cols">
    <div class="panel">
      <h2>Alert ที่ได้รับ</h2>
      <div class="cards" id="cards"></div>
    </div>
    <div class="panel">
      <h2>Timeline ของ payload</h2>
      <div class="feed" id="feed"></div>
    </div>
  </div>

  <footer>monlab5 · POST /webhook · GET /api/alerts · หน้านี้ไม่เรียกไฟล์จากภายนอกเลย</footer>
</div>

<script>
const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, c => (
  {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

function hhmmss(iso){
  if(!iso) return "–";
  const d = new Date(iso);
  if(isNaN(d)) return "–";
  return d.toLocaleTimeString("th-TH", {hour12:false});
}
function ago(sec){
  if(sec == null) return "–";
  if(sec < 60) return Math.max(0, Math.round(sec)) + " วิ";
  return Math.round(sec/60) + " นาที";
}

function alertCard(a, now){
  const sev = (a.labels.severity || "other").toLowerCase();
  const sevClass = (sev === "critical" || sev === "warning") ? sev : "other";
  const resolved = a.status === "resolved";
  const chips = Object.keys(a.labels).sort()
    .filter(k => k !== "alertname")
    .map(k => `<span class="chip"><b>${esc(k)}</b>=${esc(a.labels[k])}</span>`).join("");
  const ann = a.annotations || {};
  return `
  <div class="card sev-${sevClass} ${resolved ? "resolved" : ""}">
    <div class="crow">
      <div class="name">${esc(a.labels.alertname || "(ไม่มี alertname)")}</div>
      <div style="display:flex;gap:8px;align-items:center">
        <span class="sev ${sevClass}">${esc(sev)}</span>
        <span class="pill ${resolved ? "resolved" : "firing"}">${resolved ? "resolved" : "firing"}</span>
      </div>
    </div>
    ${ann.summary ? `<p class="summary">${esc(ann.summary)}</p>` : ""}
    ${ann.description ? `<p class="desc">${esc(ann.description)}</p>` : ""}
    <div class="chips">${chips}</div>
    <div class="meta">
      <span>เริ่ม <b>${hhmmss(a.startsAt)}</b></span>
      ${resolved ? `<span>จบ <b>${hhmmss(a.endsAt)}</b></span>` : ""}
      <span>receiver <b>${esc(a.receiver)}</b></span>
      <span>ได้รับเมื่อ <b>${ago(now - a.received_at)}ที่แล้ว</b></span>
    </div>
  </div>`;
}

async function tick(){
  let d;
  try { d = await (await fetch("/api/alerts", {cache:"no-store"})).json(); }
  catch(e){ document.getElementById("clock").textContent = "เชื่อมต่อ receiver ไม่ได้"; return; }

  document.getElementById("s-firing").textContent   = d.firing;
  document.getElementById("s-resolved").textContent = d.resolved;
  document.getElementById("s-payloads").textContent = d.payloads_received;
  const last = d.feed.length ? Math.round(d.server_time - d.feed[0].received_at) : null;
  document.getElementById("s-last").textContent = last === null ? "–" : last;
  document.getElementById("clock").textContent =
    "อัปเดตล่าสุด " + new Date(d.server_time*1000).toLocaleTimeString("th-TH",{hour12:false});

  const cards = document.getElementById("cards");
  cards.innerHTML = d.alerts.length
    ? d.alerts.map(a => alertCard(a, d.server_time)).join("")
    : `<div class="empty">ยังไม่มี alert เข้ามา<br>ลองหยุด node-exporter หรือเปิดโหมดกวนโหลด แล้วรอ Alertmanager ส่ง webhook มา</div>`;

  const feed = document.getElementById("feed");
  feed.innerHTML = d.feed.length
    ? d.feed.map(f => `
      <div class="fitem ${f.status === "resolved" ? "resolved" : ""}">
        <div class="fdot"></div>
        <div class="fmain">
          <div class="t">#${f.seq} · ${esc(f.status)} · ${f.num_alerts} alert
            <span style="color:var(--muted);font-weight:400"> · ${new Date(f.received_at*1000).toLocaleTimeString("th-TH",{hour12:false})}</span></div>
          <div class="s">receiver=${esc(f.receiver)}<br>${esc(f.group_key)}</div>
        </div>
      </div>`).join("")
    : `<div class="empty">ยังไม่มี payload</div>`;
}
tick();
setInterval(tick, 2000);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    server_version = "monlab5-receiver"
    sys_version = ""

    def log_message(self, fmt, *args):
        pass

    def send_body(self, status: int, ctype: str, body: bytes):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/":
            self.send_body(200, "text/html; charset=utf-8", PAGE.encode("utf-8"))
        elif path == "/api/alerts":
            body = json.dumps(snapshot(), ensure_ascii=False).encode("utf-8")
            self.send_body(200, "application/json; charset=utf-8", body)
        elif path == "/healthz":
            self.send_body(200, "text/plain; charset=utf-8", b"ok")
        else:
            self.send_body(404, "text/plain; charset=utf-8", b"not found")

    def do_POST(self):
        path = self.path.split("?", 1)[0]
        if path != "/webhook":
            self.send_body(404, "text/plain; charset=utf-8", b"not found")
            return
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            print(f"[receiver] payload อ่านไม่ออก: {exc}", flush=True)
            self.send_body(400, "text/plain; charset=utf-8", b"bad json")
            return
        record(payload)
        names = ",".join(sorted({(a.get("labels") or {}).get("alertname", "?")
                                 for a in payload.get("alerts", []) or []}))
        print(f"[receiver] status={payload.get('status')} "
              f"receiver={payload.get('receiver')} "
              f"alerts={len(payload.get('alerts', []) or [])} [{names}]", flush=True)
        self.send_body(200, "text/plain; charset=utf-8", b"ok")


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    server.daemon_threads = True
    print(f"[receiver] listening on :{PORT}", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
