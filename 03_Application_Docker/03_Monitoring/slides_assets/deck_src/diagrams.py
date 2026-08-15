#!/usr/bin/env python3
"""Build every conceptual diagram for the Monitoring deck on the isolated Excalidraw canvas (port 3311)."""
import json, os, subprocess, sys, time

OUT = "/home/workspace/DevTools/03_Application_Docker/03_Monitoring/slides_assets"
TMP = "/tmp/claude-0/-home-workspace-DevTools-03-Application-Docker/1d810596-9f3a-4bb6-9707-090635d8d448/scratchpad/diagjson"
ENV = dict(os.environ, EXPRESS_SERVER_URL="http://127.0.0.1:3311")

BLUE, BLUEBG = "#1864ab", "#d0ebff"
ORANGE, ORANGEBG = "#e8590c", "#ffe8cc"
GREEN, GREENBG = "#2f9e44", "#ebfbee"
RED, REDBG = "#c92a2a", "#ffe3e3"
PURPLE, PURPLEBG = "#6741d9", "#f3f0ff"
INK, MUTED = "#16212f", "#5b6b7f"
SKYBG, YELBG = "#e7f5ff", "#fff9db"


def box(id, x, y, w, h, text, stroke=BLUE, bg=BLUEBG, fs=19, dashed=False):
    e = {"id": id, "type": "rectangle", "x": x, "y": y, "width": w, "height": h,
         "backgroundColor": bg, "strokeColor": stroke, "fillStyle": "solid",
         "strokeWidth": 2, "roughness": 0, "fontFamily": "helvetica", "fontSize": fs}
    if text:
        e["text"] = text
    if dashed:
        e["strokeStyle"] = "dashed"
    return e


def zone(x, y, w, h, stroke=BLUE, bg=SKYBG):
    return {"type": "rectangle", "x": x, "y": y, "width": w, "height": h, "backgroundColor": bg,
            "strokeColor": stroke, "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed",
            "roughness": 0}


def txt(x, y, text, fs=18, color=INK, font="helvetica"):
    return {"type": "text", "x": x, "y": y, "text": text, "fontSize": fs,
            "fontFamily": font, "strokeColor": color}


def title(text):
    return txt(30, 18, text, 28, "#0b2545")


def arrow(a, b, color=BLUE, dashed=False, x=0, y=0, w=60, h=0):
    e = {"type": "arrow", "x": x, "y": y, "width": w, "height": h, "startElementId": a,
         "endElementId": b, "strokeColor": color, "strokeWidth": 2, "roughness": 0}
    if dashed:
        e["strokeStyle"] = "dashed"
    return e


def line(x, y, pts, color=BLUE, width=3):
    return {"type": "line", "x": x, "y": y, "points": pts, "strokeColor": color,
            "strokeWidth": width, "roughness": 0}


D = {}

# ---------------------------------------------------------------- d01
D["d01-why-monitoring"] = [
    title('ทำไมต้องมี Monitoring — ต่างกันที่ "รู้ก่อน" หรือ "รู้ตอนสาย"'),
    zone(20, 80, 540, 440, RED, "#fff5f5"),
    zone(580, 80, 560, 440, GREEN, "#f4fce3"),
    txt(45, 95, "ไม่มี Monitoring", 24, RED),
    txt(605, 95, "มี Monitoring", 24, GREEN),
    box("prod1", 50, 150, 230, 75, "ระบบ Production", BLUE, BLUEBG, 20),
    box("boom1", 50, 270, 230, 75, "ล่มตอนตี 2", RED, REDBG, 20),
    box("user1", 50, 390, 230, 75, "ลูกค้าโทรมาแจ้ง", RED, REDBG, 20),
    arrow("prod1", "boom1", RED, x=165, y=230, w=0, h=35),
    arrow("boom1", "user1", RED, x=165, y=350, w=0, h=35),
    txt(310, 165, "• รู้ตอนเสียหายไปแล้ว\n\n• ไม่รู้ว่าเริ่มพังเมื่อไร\n\n• ไม่รู้ว่าพังตรงไหน\n\n• เดาสาเหตุ ลองแก้มั่ว\n\n• กู้คืนช้า (MTTR ยาว)", 18, "#a02020"),
    box("prod2", 610, 150, 220, 75, "ระบบ Production", BLUE, BLUEBG, 20),
    box("prom2", 610, 270, 220, 75, "เก็บตัวเลขทุก 15 วิ", ORANGE, ORANGEBG, 20),
    box("alert2", 610, 390, 220, 75, "Alert ปลุกทีม", GREEN, GREENBG, 20),
    arrow("prod2", "prom2", ORANGE, x=720, y=230, w=0, h=35),
    arrow("prom2", "alert2", GREEN, x=720, y=350, w=0, h=35),
    txt(860, 165, "• เห็นแนวโน้มก่อนพัง\n\n• รู้เวลาเริ่มผิดปกติ\n\n• ชี้ได้ว่า service ไหน\n\n• มีหลักฐานย้อนหลัง\n\n• แก้ตรงจุด กู้คืนเร็ว", 18, "#2b8a3e"),
]

# ---------------------------------------------------------------- d02
D["d02-three-pillars"] = [
    title("สามเสาหลักของ Observability — คนละคำถาม คนละต้นทุน"),
    zone(40, 90, 340, 330, BLUE, BLUEBG),
    zone(410, 90, 340, 330, ORANGE, ORANGEBG),
    zone(780, 90, 340, 330, PURPLE, PURPLEBG),
    txt(65, 110, "METRICS — ตัวเลข", 24, BLUE),
    txt(435, 110, "LOGS — เหตุการณ์", 24, "#c2410c"),
    txt(805, 110, "TRACES — เส้นทาง", 24, PURPLE),
    txt(65, 155, 'ตอบคำถามว่า\n"ตอนนี้เป็นอย่างไร?"\n\n• ตัวเลขตามเวลา (time series)\n• เล็ก เก็บย้อนหลังได้นาน\n• เหมาะกับ dashboard + alert\n• ตอบไม่ได้ว่า "ทำไม"\n\nเครื่องมือ :\nPrometheus + Grafana\n\nชุดนี้เน้นเสานี้', 17),
    txt(435, 155, 'ตอบคำถามว่า\n"เกิดอะไรขึ้นกันแน่?"\n\n• ข้อความรายเหตุการณ์\n• มีรายละเอียด stack trace\n• กินที่เก็บมากกว่า\n• ค้นหาช้ากว่า metrics\n\nเครื่องมือ :\nLoki / ELK\n\n(นอกขอบเขตชุดนี้)', 17),
    txt(805, 155, 'ตอบคำถามว่า\n"request นี้ช้าตรงไหน?"\n\n• ตาม request ข้าม service\n• เห็นเวลาของแต่ละช่วง\n• จำเป็นเมื่อมี microservices\n• ต้องแก้โค้ดให้ส่ง context\n\nเครื่องมือ :\nTempo / Jaeger\n\n(นอกขอบเขตชุดนี้)', 17),
    box("sum2", 40, 445, 1080, 70, 'เริ่มจาก Metrics เสมอ : มันตอบได้ว่า "มีอะไรผิดปกติ ตั้งแต่เมื่อไร ที่ไหน" — แล้วค่อยขุดต่อด้วย Logs / Traces', GREEN, GREENBG, 20),
]

# ---------------------------------------------------------------- d03
D["d03-pull-vs-push"] = [
    title("Pull vs Push — ใครเป็นฝ่ายเริ่มติดต่อ?"),
    zone(20, 80, 545, 310, BLUE, SKYBG),
    zone(590, 80, 545, 310, ORANGE, YELBG),
    txt(45, 95, "PULL — Prometheus ไปดึงเอง", 21, BLUE),
    txt(45, 122, "(ชุดนี้ใช้แบบนี้)", 17, MUTED),
    txt(615, 95, "PUSH — แอปส่งออกเอง", 21, "#c2410c"),
    box("p1", 50, 170, 165, 75, "Prometheus", BLUE, BLUEBG, 19),
    box("a1", 360, 150, 175, 50, "app A  /metrics", GREEN, GREENBG, 16),
    box("a2", 360, 215, 175, 50, "app B  /metrics", GREEN, GREENBG, 16),
    box("a3", 360, 280, 175, 50, "app C  /metrics", GREEN, GREENBG, 16),
    arrow("p1", "a1", BLUE, x=220, y=190, w=135, h=-15),
    arrow("p1", "a2", BLUE, x=220, y=207, w=135, h=30),
    arrow("p1", "a3", BLUE, x=220, y=225, w=135, h=80),
    txt(232, 128, "HTTP GET ทุก 15 วิ", 15, BLUE),
    txt(45, 265, "✓ Prometheus คุมจังหวะเอง\n✓ รู้ทันทีว่า target ตาย (up=0)\n✓ แอปแค่เปิดหน้าเว็บไว้เฉย ๆ\n✓ ทดสอบด้วย curl ได้เลย", 16, BLUE),
    box("p2", 940, 170, 165, 75, "ตัวรับกลาง", ORANGE, ORANGEBG, 18),
    box("b1", 620, 150, 150, 50, "app A", GREEN, GREENBG, 16),
    box("b2", 620, 215, 150, 50, "app B", GREEN, GREENBG, 16),
    box("b3", 620, 280, 150, 50, "app C", GREEN, GREENBG, 16),
    arrow("b1", "p2", ORANGE, x=775, y=175, w=160, h=25),
    arrow("b2", "p2", ORANGE, x=775, y=240, w=160, h=-30),
    arrow("b3", "p2", ORANGE, x=775, y=305, w=160, h=-90),
    txt(615, 345, "✗ แอปเงียบไป = ตาย หรือแค่ไม่ส่ง? แยกไม่ออก\n✗ แอปต้องรู้จัก address ของเซิร์ฟเวอร์กลาง", 16, "#c2410c"),
    box("note3", 20, 415, 1115, 100, "ข้อยกเว้น : งานที่อยู่สั้น ๆ (batch job) จบไปก่อน Prometheus จะมาดึง — กรณีนี้ใช้ Pushgateway มาคั่น\nแต่อย่าใช้กับ service ที่รันค้าง เพราะจะเสียความสามารถสำคัญที่สุดของ pull ไป นั่นคือการรู้ว่า target ตาย (up = 0)", ORANGE, YELBG, 19),
]

# ---------------------------------------------------------------- d04
D["d04-prometheus-architecture"] = [
    title("สถาปัตยกรรม Prometheus — ใครทำอะไรตรงไหน"),
    txt(45, 80, "แหล่งตัวเลข (Exporter / แอป)", 18, GREEN),
    box("ex1", 40, 115, 240, 65, "node-exporter  :9100\nตัวเลขของเครื่อง", GREEN, GREENBG, 16),
    box("ex2", 40, 200, 240, 65, "cAdvisor  :8080\nตัวเลขของ container", GREEN, GREENBG, 16),
    box("ex3", 40, 285, 240, 65, "แอปของเรา  /metrics\nตัวเลขของธุรกิจ", GREEN, GREENBG, 16),
    zone(380, 105, 300, 300, BLUE, SKYBG),
    txt(400, 118, "Prometheus  :9090", 20, BLUE),
    box("sc", 400, 155, 260, 60, "1. Scrape — ดึงตามรอบ", BLUE, BLUEBG, 17),
    box("db", 400, 230, 260, 60, "2. TSDB — เก็บ time series", BLUE, BLUEBG, 17),
    box("ru", 400, 305, 260, 60, "3. Rule engine — ประเมิน", BLUE, BLUEBG, 17),
    arrow("ex1", "sc", GREEN, x=285, y=147, w=110, h=40),
    arrow("ex2", "sc", GREEN, x=285, y=232, w=110, h=-45),
    arrow("ex3", "sc", GREEN, x=285, y=317, w=110, h=-130),
    txt(288, 92, "HTTP GET /metrics", 14, GREEN),
    box("gf", 790, 130, 250, 80, "Grafana  :3000\ndashboard / กราฟ", ORANGE, ORANGEBG, 18),
    box("am", 790, 290, 250, 80, "Alertmanager  :9093\nจัดกลุ่ม + ส่งแจ้งเตือน", RED, REDBG, 18),
    box("rc", 790, 420, 250, 65, "Webhook / Email / Chat", PURPLE, PURPLEBG, 17),
    arrow("db", "gf", ORANGE, x=665, y=245, w=120, h=-70),
    arrow("ru", "am", RED, x=665, y=335, w=120, h=-5),
    arrow("am", "rc", PURPLE, x=915, y=375, w=0, h=40),
    txt(672, 195, "PromQL", 15, ORANGE),
    txt(672, 300, "alert ที่ firing", 15, RED),
    box("note4", 40, 425, 700, 90, "จำง่าย ๆ : Prometheus ทำ 3 อย่าง — ไปดึงตัวเลขมา · เก็บไว้ตามเวลา · เอาไปคิดต่อ\nส่วน \"หน้าตา\" เป็นงานของ Grafana และ \"การแจ้งเตือน\" เป็นงานของ Alertmanager", BLUE, SKYBG, 18),
]

# ---------------------------------------------------------------- d05
D["d05-metric-anatomy"] = [
    title("หน้าตาของ metric หนึ่งบรรทัด — อ่านให้ออกทีละส่วน"),
    box("codebox", 40, 95, 1100, 90, "", "#0d1626", "#0d1626"),
    txt(70, 120, 'app_requests_total{method="GET", endpoint="/api/items", status="200"}   1234', 22, "#dbe6f5", "cascadia"),
    txt(70, 152, "└──── ชื่อ metric ────┘└─────────── labels (มิติ) ───────────┘   └ ค่า ┘", 15, "#7d8ea3", "cascadia"),
    box("n1", 40, 220, 250, 120, "ชื่อ metric\n\nบอกว่าวัดอะไร\nลงท้าย _total = counter\nตามธรรมเนียม", BLUE, BLUEBG, 16),
    box("n2", 310, 220, 380, 120, "labels — หัวใจของ Prometheus\n\nแยกมิติของตัวเลขเดียวกัน เช่น แยกตาม\nmethod / endpoint / status\n1 ชุด label = 1 time series แยกกัน", ORANGE, ORANGEBG, 16),
    box("n3", 710, 220, 200, 120, "ค่า (value)\n\nเป็นตัวเลข\nfloat64 เสมอ", GREEN, GREENBG, 16),
    box("n4", 930, 220, 210, 120, "เวลา (timestamp)\n\nPrometheus เติมให้\nตอน scrape", PURPLE, PURPLEBG, 16),
    box("ser", 40, 370, 1100, 145, "ทำไม labels ถึงสำคัญ : เมื่อรวมกันแล้ว metric ชื่อเดียวกลายเป็นหลายเส้น (series) ที่ query แยกหรือรวมก็ได้\n\napp_requests_total{endpoint=\"/api/items\", status=\"200\"}    ← เส้นที่ 1\napp_requests_total{endpoint=\"/api/items\", status=\"500\"}    ← เส้นที่ 2\napp_requests_total{endpoint=\"/api/slow\",  status=\"200\"}    ← เส้นที่ 3\n\nsum by (status) (rate(app_requests_total[1m]))  →  ยุบทุก endpoint เหลือมองแยกตาม status", ORANGE, YELBG, 17),
]

# ---------------------------------------------------------------- d06
D["d06-counter-vs-gauge"] = [
    title("Counter vs Gauge — ต่างกันที่ทิศทางของตัวเลข"),
    zone(30, 80, 545, 320, BLUE, SKYBG),
    zone(605, 80, 545, 320, GREEN, GREENBG),
    txt(55, 95, "COUNTER — ขึ้นอย่างเดียว", 22, BLUE),
    txt(630, 95, "GAUGE — ขึ้นก็ได้ ลงก็ได้", 22, GREEN),
    line(70, 340, [[0, 0], [60, -20], [120, -45], [180, -60], [240, -95], [300, -125], [360, -150], [420, -190]], BLUE, 3),
    line(70, 350, [[0, 0], [430, 0]], MUTED, 2),
    line(70, 350, [[0, 0], [0, -220]], MUTED, 2),
    txt(60, 355, "เวลา →", 14, MUTED),
    txt(500, 140, "restart\n↓ กลับเป็น 0", 14, RED),
    line(505, 175, [[0, 0], [0, 45]], RED, 2),
    txt(55, 145, "ค่าสะสมตั้งแต่เริ่มโปรเซส\nถามว่า \"ตอนนี้เท่าไร\" ไม่มีความหมาย\nต้องดู \"เพิ่มเร็วแค่ไหน\" ด้วย rate()", 16, BLUE),
    line(645, 250, [[0, 0], [50, -55], [100, -20], [150, -80], [200, -35], [250, -95], [300, -50], [350, -70], [400, -25]], GREEN, 3),
    line(645, 350, [[0, 0], [430, 0]], MUTED, 2),
    line(645, 350, [[0, 0], [0, -220]], MUTED, 2),
    txt(635, 355, "เวลา →", 14, MUTED),
    txt(630, 145, "ค่า ณ ขณะนั้น อ่านตรง ๆ ได้เลย\nไม่ต้องใช้ rate()", 16, GREEN),
    box("cex", 30, 415, 545, 100, "ตัวอย่าง\nnode_cpu_seconds_total · container_cpu_usage_seconds_total\napp_requests_total · prometheus_http_requests_total", BLUE, BLUEBG, 16),
    box("gex", 605, 415, 545, 100, "ตัวอย่าง\nnode_memory_MemAvailable_bytes · node_load1\ncontainer_memory_working_set_bytes · app_inflight_requests", GREEN, GREENBG, 16),
]

# ---------------------------------------------------------------- d07
D["d07-histogram-buckets"] = [
    title("Histogram — เก็บ \"การกระจายตัว\" ไม่ใช่แค่ค่าเฉลี่ย"),
    txt(40, 80, "ทุก request ถูกหย่อนลงถังตามเวลาที่ใช้ แล้วนับสะสมขึ้นไปเรื่อย ๆ (cumulative)", 18, MUTED),
    txt(40, 120, "le = 0.1", 17, INK, "cascadia"),
    box("b1", 160, 112, 240, 34, "80", BLUE, BLUEBG, 15),
    txt(40, 165, "le = 0.25", 17, INK, "cascadia"),
    box("b2", 160, 157, 420, 34, "140", BLUE, BLUEBG, 15),
    txt(40, 210, "le = 0.5", 17, INK, "cascadia"),
    box("b3", 160, 202, 540, 34, "180", BLUE, BLUEBG, 15),
    txt(40, 255, "le = 1.0", 17, INK, "cascadia"),
    box("b4", 160, 247, 585, 34, "195", ORANGE, ORANGEBG, 15),
    txt(40, 300, "le = +Inf", 17, INK, "cascadia"),
    box("b5", 160, 292, 600, 34, "200", GREEN, GREENBG, 15),
    txt(790, 112, "\"ไม่เกิน 0.1 วิ มี 80 ครั้ง\"", 16, MUTED),
    txt(790, 157, "\"ไม่เกิน 0.25 วิ มี 140 ครั้ง\"  ← รวม 80 ข้างบนแล้ว", 16, MUTED),
    txt(790, 202, "\"ไม่เกิน 0.5 วิ มี 180 ครั้ง\"", 16, MUTED),
    txt(790, 247, "\"ไม่เกิน 1 วิ มี 195 ครั้ง\"", 16, ORANGE),
    txt(790, 292, "ทั้งหมด 200 ครั้ง (= _count)", 16, GREEN),
    box("q", 40, 350, 1100, 165, "p95 = ค่าที่ 95% ของ request เร็วกว่าหรือเท่ากับค่านี้ → 95% ของ 200 = 190 ครั้ง\n190 อยู่ระหว่างถัง 0.5 (180 ครั้ง) กับถัง 1.0 (195 ครั้ง)  →  Prometheus ประมาณค่าเชิงเส้นในช่วงนั้น\n\nhistogram_quantile(0.95, sum by (le) (rate(app_request_duration_seconds_bucket[5m])))\n\n⚠️ p95 เป็น \"ค่าประมาณ\" ที่ละเอียดเท่าที่ขอบถังจะบอกได้ — เลือกขอบถังให้คร่อมค่าที่เราสนใจ (เช่น SLO 1 วินาที) เสมอ", ORANGE, YELBG, 17),
]

# ---------------------------------------------------------------- d08
D["d08-rate-window"] = [
    title("rate() — แปลง counter ที่ขึ้นเรื่อย ๆ ให้เป็น \"ต่อวินาที\""),
    txt(40, 80, "scrape ทุก 15 วินาที — แต่ละจุดคือค่าสะสมที่อ่านได้", 18, MUTED),
    line(60, 200, [[0, 0], [1040, 0]], MUTED, 2),
    box("t1", 60, 120, 110, 55, "t=0s\n1000", BLUE, BLUEBG, 15),
    box("t2", 210, 120, 110, 55, "t=15s\n1030", BLUE, BLUEBG, 15),
    box("t3", 360, 120, 110, 55, "t=30s\n1075", BLUE, BLUEBG, 15),
    box("t4", 510, 120, 110, 55, "t=45s\n1105", BLUE, BLUEBG, 15),
    box("t5", 660, 120, 110, 55, "t=60s\n1150", BLUE, BLUEBG, 15),
    line(60, 235, [[0, 0], [0, 30]], GREEN, 3),
    line(770, 235, [[0, 0], [0, 30]], GREEN, 3),
    line(60, 265, [[0, 0], [710, 0]], GREEN, 3),
    txt(300, 275, "หน้าต่าง [1m] — มี 5 จุด ใช้ได้", 18, GREEN),
    txt(60, 315, "rate = (1150 − 1000) ÷ 60 วินาที = 2.5 ครั้ง/วินาที", 20, GREEN, "cascadia"),
    box("bad", 40, 365, 545, 150, "❌ หน้าต่างสั้นเกินไป : rate(...[15s])\n\nในหน้าต่าง 15 วิ อาจมีแค่ 1 จุด — คำนวณอัตราไม่ได้\nผลลัพธ์จะว่างเปล่า (No data) หรือกระโดดไปมา\n\nนี่คือสาเหตุอันดับหนึ่งที่ \"กราฟว่าง\" ทั้งที่ metric มีอยู่", RED, REDBG, 16),
    box("good", 605, 365, 545, 150, "✅ กฎง่าย ๆ ที่ควรจำ\n\nหน้าต่าง rate ≥ 4 × scrape_interval\n\nscrape 15s → ใช้ [1m]     scrape 5s → ใช้ [30s]\n\nเผื่อไว้ให้ scrape หลุดไป 1-2 รอบแล้วยังคำนวณได้", GREEN, GREENBG, 16),
]

# ---------------------------------------------------------------- d09
D["d09-cardinality"] = [
    title("Cardinality — label ที่เลือกผิด ฆ่า Prometheus ได้"),
    zone(30, 80, 545, 250, GREEN, GREENBG),
    zone(605, 80, 545, 250, RED, "#fff5f5"),
    txt(55, 95, "✅ label ที่ดี — ค่าจำกัด", 21, GREEN),
    txt(630, 95, "❌ label ที่พัง — ค่าไม่จำกัด", 21, RED),
    txt(55, 140, 'endpoint="/api/items/:id"\n\nไม่ว่าจะมีสินค้ากี่ล้านชิ้น\nendpoint ก็ยังมีค่าเดียว\n\n5 endpoint × 4 status × 3 method\n= 60 series', 17, INK, "cascadia"),
    txt(630, 140, 'endpoint="/api/items/48213"\n\nสินค้าใหม่ 1 ชิ้น = series ใหม่ 1 เส้น\nและมันไม่มีวันหายไปเอง\n\n100,000 id × 4 status × 3 method\n= 1,200,000 series', 17, INK, "cascadia"),
    box("res", 30, 355, 1120, 160, "ผลที่ตามมาเมื่อ series ระเบิด : RAM ของ Prometheus พุ่ง → query ช้าลงทุกอัน → สุดท้าย OOM ตายทั้งตัว\n(กระทบ dashboard และ alert ทั้งระบบ ไม่ใช่แค่ metric ตัวที่ผิด)\n\nกฎ : label ต้องมีค่าที่ \"นับได้\" และ \"ไม่โตตามข้อมูล\"\nห้ามใส่เป็น label : user id · order id · email · request id · session id · timestamp · full URL ที่มีพารามิเตอร์\nตรวจได้ด้วย :  count(count by (endpoint) (app_requests_total))   และ   prometheus_tsdb_head_series", ORANGE, YELBG, 17),
]

# ---------------------------------------------------------------- d10
D["d10-red-use"] = [
    title("จะวัดอะไรดี? — RED สำหรับบริการ · USE สำหรับทรัพยากร"),
    zone(30, 80, 545, 400, BLUE, SKYBG),
    zone(605, 80, 545, 400, ORANGE, YELBG),
    txt(55, 95, "RED — สำหรับสิ่งที่ \"รับ request\"", 21, BLUE),
    txt(630, 95, "USE — สำหรับ \"ทรัพยากร\"", 21, "#c2410c"),
    box("r1", 55, 140, 495, 95, "R — Rate : รับงานเข้ามาเท่าไร\nsum(rate(app_requests_total[1m]))", BLUE, BLUEBG, 16),
    box("r2", 55, 250, 495, 95, "E — Errors : พังกี่เปอร์เซ็นต์\nsum(rate(app_requests_total{status=~\"5..\"}[1m]))\n  / sum(rate(app_requests_total[1m]))", BLUE, BLUEBG, 16),
    box("r3", 55, 360, 495, 100, "D — Duration : ช้าแค่ไหน (ดู p95 ไม่ใช่ค่าเฉลี่ย)\nhistogram_quantile(0.95, sum by (le)\n  (rate(app_request_duration_seconds_bucket[5m])))", BLUE, BLUEBG, 16),
    box("u1", 630, 140, 495, 95, "U — Utilization : ใช้ไปกี่ % ของที่มี\nrate(container_cpu_usage_seconds_total[1m])", ORANGE, ORANGEBG, 16),
    box("u2", 630, 250, 495, 95, "S — Saturation : คิวล้นแค่ไหน รอคิวเท่าไร\nnode_load1 · app_inflight_requests", ORANGE, ORANGEBG, 16),
    box("u3", 630, 360, 495, 100, "E — Errors : ตัวทรัพยากรเองพังกี่ครั้ง\nnode_network_receive_errs_total\ncontainer OOM kill", ORANGE, ORANGEBG, 16),
    txt(30, 495, "ใช้คู่กัน : RED บอกว่า \"ผู้ใช้เจ็บไหม\" (อาการ) · USE บอกว่า \"เพราะทรัพยากรตัวไหน\" (สาเหตุ) — ตั้ง alert ที่อาการ แล้วใช้ USE หาสาเหตุ", 18, GREEN),
]

# ---------------------------------------------------------------- d11
D["d11-alert-lifecycle"] = [
    title("วงจรชีวิตของ Alert — ทำไมต้องมี for:"),
    box("s1", 40, 130, 230, 90, "Inactive\nเงื่อนไขยังไม่จริง", MUTED, "#f1f3f5", 18),
    box("s2", 340, 130, 230, 90, "Pending\nจริงแล้ว แต่ยังไม่ครบเวลา", ORANGE, ORANGEBG, 18),
    box("s3", 640, 130, 230, 90, "Firing\nส่งให้ Alertmanager", RED, REDBG, 18),
    box("s4", 940, 130, 200, 90, "Resolved\nกลับมาปกติ", GREEN, GREENBG, 18),
    arrow("s1", "s2", ORANGE, x=275, y=175, w=60, h=0),
    arrow("s2", "s3", RED, x=575, y=175, w=60, h=0),
    arrow("s3", "s4", GREEN, x=875, y=175, w=60, h=0),
    txt(272, 100, "expr เป็นจริง", 15, ORANGE),
    txt(575, 100, "ครบ for:", 15, RED),
    txt(878, 100, "expr เท็จ", 15, GREEN),
    txt(40, 265, "ตัวอย่าง :  expr: error_ratio > 0.05   for: 1m", 20, INK, "cascadia"),
    line(60, 340, [[0, 0], [1060, 0]], MUTED, 2),
    line(260, 330, [[0, 0], [0, 20]], ORANGE, 3),
    line(660, 330, [[0, 0], [0, 20]], RED, 3),
    txt(180, 355, "10:00:00\nerror พุ่งเกิน 5%\n→ Pending", 15, ORANGE),
    txt(590, 355, "10:01:00\nยังเกินอยู่ครบ 1 นาที\n→ Firing (แจ้งเตือนออก)", 15, RED),
    box("why", 40, 435, 1100, 105, "ทำไมต้องรอ for: — เพราะ error กระตุกวินาทีเดียวไม่ควรปลุกใครตอนตี 3\nfor: คือตัวกรอง \"เสียงรบกวน\" ออกจาก \"ปัญหาจริง\" · ตั้งสั้นไป = เตือนพร่ำเพรื่อ · ตั้งยาวไป = รู้ช้าเกินแก้\n\n⏱ การเปลี่ยนสถานะเกิดเฉพาะ \"รอบประเมิน\" (evaluation_interval) เท่านั้น — จึง firing ช้ากว่า for: ที่ตั้งไว้ได้เล็กน้อย", BLUE, SKYBG, 17),
]

# ---------------------------------------------------------------- d12
D["d12-alertmanager-pipeline"] = [
    title("Alertmanager — ทำไมไม่ให้ Prometheus ส่งอีเมลเองเลย?"),
    box("pr", 30, 150, 175, 110, "Prometheus\n\nประเมิน rule\nแล้วส่ง alert ที่\nfiring ออกมา", BLUE, BLUEBG, 16),
    zone(240, 110, 640, 200, RED, "#fff5f5"),
    txt(258, 122, "Alertmanager — งานทั้งหมดอยู่ที่นี่", 19, RED),
    box("d1", 258, 160, 140, 130, "1. Dedup\n\nalert เดียวกัน\nจากหลาย\nPrometheus\nรวมเป็นใบเดียว", RED, REDBG, 14),
    box("d2", 410, 160, 140, 130, "2. Group\n\n50 container\nล่มพร้อมกัน\n= แจ้ง 1 ใบ\nไม่ใช่ 50 ใบ", RED, REDBG, 14),
    box("d3", 562, 160, 140, 130, "3. Inhibit\n\nถ้าทั้งเครื่องล่ม\nแล้ว ก็ไม่ต้อง\nเตือนว่าแอป\nบนเครื่องช้า", RED, REDBG, 14),
    box("d4", 714, 160, 150, 130, "4. Silence\n\nช่วง maintenance\nปิดเสียงชั่วคราว\nโดยไม่ต้องแก้\n rule", RED, REDBG, 14),
    box("rt", 915, 130, 225, 75, "5. Route\nเลือกปลายทางตาม label\nเช่น severity", PURPLE, PURPLEBG, 16),
    box("rv", 915, 230, 225, 80, "6. ส่งจริง\nWebhook / Email / Chat", GREEN, GREENBG, 16),
    arrow("pr", "d1", BLUE, x=210, y=205, w=42, h=0),
    arrow("d4", "rt", PURPLE, x=870, y=205, w=40, h=-35),
    arrow("rt", "rv", GREEN, x=1027, y=210, w=0, h=15),
    box("why12", 30, 340, 1110, 175, "ถ้า Prometheus ส่งเองตรง ๆ จะเจอปัญหานี้ทันที :\n\n• Node ล่ม 1 เครื่องที่มี 40 container → อีเมล 41 ฉบับใน 5 วินาที (คนอ่านไม่ไหว แล้วจะเริ่มเมินทุกฉบับ)\n• ช่วง deploy ตั้งใจให้ล่ม → ไม่มีทางปิดเสียงชั่วคราวโดยไม่แก้ rule\n• อยากให้ critical เข้าโทรศัพท์ แต่ warning เข้าแชท → ต้องเขียน logic เองในทุก rule\n\nแยกหน้าที่กันชัด : Prometheus = \"ตัดสินว่าผิดปกติไหม\" · Alertmanager = \"จะบอกใคร อย่างไร เมื่อไร\"", ORANGE, YELBG, 17),
]

# ---------------------------------------------------------------- d13
D["d13-lab-stack"] = [
    title("ภาพรวม stack ที่จะประกอบขึ้นมาเองใน 6 แล็บ"),
    zone(30, 75, 1110, 390, BLUE, SKYBG),
    txt(50, 86, "ทุกอย่างรันด้วย Docker Compose ในเครื่องเรียนเดียว (network: monnet)", 17, MUTED),
    txt(50, 120, "แหล่งตัวเลข", 16, GREEN),
    box("ne", 55, 145, 205, 78, "node-exporter\n:9100  ·  LAB 1", GREEN, GREENBG, 16),
    box("ca", 285, 145, 205, 78, "cAdvisor\n:8080  ·  LAB 2", GREEN, GREENBG, 16),
    box("ap", 515, 145, 205, 78, "แอปของเรา\n:8000  ·  LAB 4", GREEN, GREENBG, 16),
    box("lg", 800, 145, 200, 78, "load generator\nยิง request  ·  LAB 4", MUTED, "#f1f3f5", 16),
    arrow("lg", "ap", MUTED, x=795, y=184, w=-70, h=0),
    box("pm", 430, 285, 280, 90, "Prometheus  :9090\nLAB 1", BLUE, BLUEBG, 18),
    box("gr", 60, 285, 250, 90, "Grafana  :3000\nLAB 3", ORANGE, ORANGEBG, 18),
    box("al", 830, 285, 250, 90, "Alertmanager  :9093\nLAB 5", RED, REDBG, 18),
    box("rc13", 830, 395, 250, 55, "receiver :5001  ·  LAB 5", PURPLE, PURPLEBG, 16),
    arrow("ne", "pm", GREEN, x=160, y=228, w=280, h=50),
    arrow("ca", "pm", GREEN, x=390, y=228, w=150, h=50),
    arrow("ap", "pm", GREEN, x=618, y=228, w=-40, h=50),
    arrow("pm", "gr", ORANGE, x=425, y=330, w=-108, h=0),
    arrow("pm", "al", RED, x=715, y=330, w=108, h=0),
    arrow("al", "rc13", PURPLE, x=955, y=380, w=0, h=10),
    txt(330, 302, "PromQL", 14, ORANGE),
    txt(725, 302, "alert", 14, RED),
    box("cap", 30, 485, 1110, 115, "LAB 6 (Capstone) = ทุกกล่องข้างบนพร้อมกัน + บั๊กซ่อน 3 จุดให้ตามหา + check.sh ตรวจให้ครบ 5 ข้อ\n\nทุกแล็บใช้ port ชุดเดียวกัน → ต้อง  docker compose down  ก่อนย้ายไปแล็บถัดไปเสมอ\nเปิดหน้าเว็บผ่าน VS Code Remote-SSH port forwarding", GREEN, GREENBG, 18),
]

# ---------------------------------------------------------------- d14
D["d14-slo-error-budget"] = [
    title("SLI / SLO / Error Budget — ตั้งเป้าเป็นตัวเลขที่เถียงกันไม่ได้"),
    box("sli", 30, 100, 355, 130, "SLI — ตัววัด\n\n\"สัดส่วน request ที่สำเร็จ\nและเร็วกว่า 1 วินาที\"\n\nคือ PromQL หนึ่งบรรทัด", BLUE, BLUEBG, 17),
    box("slo", 405, 100, 355, 130, "SLO — เป้าหมาย\n\n\"SLI ต้อง ≥ 99.9%\nวัดต่อเนื่อง 30 วัน\"\n\nคือสัญญาที่ทีมให้ไว้", ORANGE, ORANGEBG, 17),
    box("eb", 780, 100, 360, 130, "Error Budget — โควตาพัง\n\n100% − 99.9% = 0.1%\nของ 30 วัน = 43 นาที\n\nคือ \"งบ\" ที่ใช้ได้ต่อเดือน", RED, REDBG, 17),
    txt(30, 265, "งบพังของเดือนนี้ (43 นาที)", 19, INK),
    box("used", 30, 300, 420, 55, "ใช้ไปแล้ว 28 นาที", RED, REDBG, 17),
    box("left", 450, 300, 690, 55, "เหลือ 15 นาที", GREEN, GREENBG, 17),
    box("use14", 30, 390, 1110, 125, "ทำไมต้องมีงบ : ระบบที่ไม่เคยพังเลย = ลงทุนเกินจำเป็น (99.99% แพงกว่า 99.9% หลายเท่า)\nError budget เปลี่ยนคำถามจาก \"ห้ามพัง\" เป็น \"พังได้เท่าไร แล้วเราจะใช้โควตานั้นทำอะไร\"\n\nงบเหลือเยอะ → ปล่อยฟีเจอร์ใหม่ได้เร็ว กล้าทดลอง       งบใกล้หมด → หยุดปล่อยของ หันมาแก้ความเสถียรก่อน\nและมันคือเหตุผลว่าทำไม alert ควรผูกกับ \"อาการที่ผู้ใช้เจอ\" ไม่ใช่ \"CPU สูง\" ที่ผู้ใช้อาจไม่รู้สึกอะไรเลย", BLUE, SKYBG, 17),
]


def run(cmd):
    return subprocess.run(cmd, shell=True, env=ENV, capture_output=True, text=True)


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[1:] or sorted(D)
    for name in names:
        els = D[name]
        jf = f"{TMP}/{name}.json"
        with open(jf, "w") as f:
            json.dump(els, f, ensure_ascii=False)
        run("npx -y mcp-excalidraw-server clear --yes")
        r = run(f"npx -y mcp-excalidraw-server add {jf}")
        if r.returncode != 0:
            print(f"[{name}] ADD FAILED: {r.stderr[:300]}")
            continue
        time.sleep(2.5)
        svg = f"{OUT}/{name}.svg"
        r = run(f"npx -y mcp-excalidraw-server screenshot --format svg --out {svg}")
        ok = os.path.exists(svg) and os.path.getsize(svg) > 2000
        # keep the editable scene alongside the SVG
        run(f"npx -y mcp-excalidraw-server export --out {OUT}/scenes/{name}.excalidraw")
        print(f"[{name}] {'OK' if ok else 'FAIL'} size={os.path.getsize(svg) if os.path.exists(svg) else 0} rc={r.returncode}")


if __name__ == "__main__":
    main()
