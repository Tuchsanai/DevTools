#!/usr/bin/env python3
"""Build every conceptual diagram for the Plane deck on an isolated Excalidraw canvas.

Usage (needs the canvas server + one open browser tab):
  PORT=3311 EXPRESS_SERVER_URL=http://127.0.0.1:3311 npx -y mcp-excalidraw-server start &
  python3 tools/canvas_tab.py http://127.0.0.1:3311 &      # headless tab (or open the URL yourself)
  python3 diagrams.py                 # draw every diagram → ../<name>.svg + ../scenes/<name>.excalidraw
  python3 diagrams.py d03-lab-architecture   # only one
"""
import json, os, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.abspath(os.path.join(HERE, ".."))
TMP = os.path.join(HERE, ".tmp_json")
ENV = dict(os.environ, EXPRESS_SERVER_URL=os.environ.get("EXPRESS_SERVER_URL", "http://127.0.0.1:3311"))

BLUE, BLUEBG = "#1864ab", "#d0ebff"
ORANGE, ORANGEBG = "#e8590c", "#ffe8cc"
GREEN, GREENBG = "#2f9e44", "#ebfbee"
RED, REDBG = "#c92a2a", "#ffe3e3"
PURPLE, PURPLEBG = "#6741d9", "#f3f0ff"
TEAL, TEALBG = "#0b7285", "#e3fafc"
INK, MUTED = "#16212f", "#5b6b7f"
SKYBG, YELBG, GREYBG = "#e7f5ff", "#fff9db", "#f1f3f5"


def box(id, x, y, w, h, text, stroke=BLUE, bg=BLUEBG, fs=19, dashed=False):
    e = {"id": id, "type": "rectangle", "x": x, "y": y, "width": w, "height": h,
         "backgroundColor": bg, "strokeColor": stroke, "fillStyle": "solid",
         "strokeWidth": 2, "roughness": 0, "fontFamily": "helvetica", "fontSize": fs}
    if text:
        e["text"] = text
    if dashed:
        e["strokeStyle"] = "dashed"
    return e


def zone(x, y, w, h, stroke=BLUE, bg=SKYBG, id=None):
    e = {"type": "rectangle", "x": x, "y": y, "width": w, "height": h, "backgroundColor": bg,
         "strokeColor": stroke, "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "dashed",
         "roughness": 0}
    if id:
        e["id"] = id
    return e


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


def line(x, y, pts, color=BLUE, width=3, dashed=False):
    e = {"type": "line", "x": x, "y": y, "points": pts, "strokeColor": color,
         "strokeWidth": width, "roughness": 0}
    if dashed:
        e["strokeStyle"] = "dashed"
    return e


D = {}

# ---------------------------------------------------------------- d01  Scrum → Plane
rows = [
    ("Product Backlog", "Work items (state group: Backlog)", BLUE, BLUEBG),
    ("Sprint (1–4 สัปดาห์)", "Cycle (start date → end date)", ORANGE, ORANGEBG),
    ("Sprint Backlog", "Work items ที่ถูกเพิ่มเข้า Cycle", ORANGE, ORANGEBG),
    ("Epic / Feature", "Module (มี lead, members, status)", PURPLE, PURPLEBG),
    ("Story points", "Estimates (points / categories / time)", GREEN, GREENBG),
    ("Board columns", "States 5 กลุ่ม: backlog · unstarted · started · completed · cancelled", TEAL, TEALBG),
    ("Definition of Done / Sprint Goal", "Page (เอกสารในโปรเจกต์) + Cycle description", MUTED, GREYBG),
    ("Burndown / Velocity", "Cycle progress chart + Analytics", RED, REDBG),
]
els = [title("Scrum ↔ Plane : แนวคิดเดียวกัน เรียกคนละชื่อ"),
       txt(60, 70, "Scrum (Scrum Guide 2020)", 20, BLUE), txt(620, 70, "Plane (self-hosted)", 20, GREEN)]
y = 105
for i, (s, p, c, bg) in enumerate(rows):
    els.append(box(f"s{i}", 40, y, 400, 52, s, c, bg, 17))
    els.append(box(f"p{i}", 600, y, 580, 52, p, c, bg, 16))
    els.append(arrow(f"s{i}", f"p{i}", c, x=445, y=y + 26, w=150, h=0))
    y += 64
D["d01-scrum-to-plane"] = els

# ---------------------------------------------------------------- d02  Kanban flow metrics
D["d02-kanban-metrics"] = [
    title("Kanban : วัด flow ด้วย Lead time · Cycle time · WIP · Throughput"),
    zone(30, 80, 1150, 210, TEAL, TEALBG),
    txt(50, 92, "เส้นเวลาของ work item หนึ่งใบ", 18, TEAL),
    box("c1", 60, 125, 220, 72, "สร้าง (Backlog)\n2026-08-03 09:00", BLUE, BLUEBG, 15),
    box("c2", 440, 125, 240, 72, "เริ่มทำ (In Progress)\n2026-08-05 10:00", ORANGE, ORANGEBG, 15),
    box("c3", 900, 125, 220, 72, "เสร็จ (Done)\n2026-08-07 16:00", GREEN, GREENBG, 15),
    arrow("c1", "c2", MUTED, x=285, y=161, w=150, h=0),
    arrow("c2", "c3", MUTED, x=685, y=161, w=210, h=0),
    line(60, 222, [[0, 0], [1060, 0]], BLUE, 3),
    txt(380, 228, "Lead time = เสร็จ − สร้าง = 4 วัน 7 ชม.", 17, BLUE),
    line(440, 258, [[0, 0], [680, 0]], ORANGE, 3, dashed=True),
    txt(600, 264, "Cycle time = เสร็จ − เริ่มทำ = 2 วัน 6 ชม.", 17, ORANGE),
    zone(30, 315, 560, 250, PURPLE, PURPLEBG),
    txt(50, 327, "Little's Law", 20, PURPLE),
    box("ll", 55, 365, 510, 70, "Lead time  ≈  WIP  ÷  Throughput", PURPLE, "#ffffff", 22),
    txt(55, 450, "WIP 12 ใบ ÷ ปิดได้ 3 ใบ/วัน  →  รอเฉลี่ย 4 วัน\nอยากให้งานออกเร็วขึ้น: ลด WIP ก่อน ไม่ใช่เพิ่มคน", 16, INK),
    zone(620, 315, 560, 250, GREEN, GREENBG),
    txt(640, 327, "WIP limit บนบอร์ด", 20, GREEN),
    box("w1", 640, 365, 160, 130, "To Do\n\n4 ใบ", BLUE, "#ffffff", 16),
    box("w2", 815, 365, 160, 130, "In Progress\n(WIP ≤ 3)\n3/3  เต็ม!", ORANGE, ORANGEBG, 16),
    box("w3", 990, 365, 170, 130, "Done\n\n9 ใบ", GREEN, "#ffffff", 16),
    txt(640, 510, "คอลัมน์เต็ม = หยุดดึงงานใหม่ ไปช่วยปิดงานที่ค้างก่อน (stop starting, start finishing)", 15, MUTED),
]

# ---------------------------------------------------------------- d03  LAB architecture
D["d03-lab-architecture"] = [
    title("สถาปัตยกรรม LAB : เครื่องเรา → devtools (Docker-in-Docker) → Plane 13 container"),
    zone(30, 80, 290, 500, MUTED, GREYBG),
    txt(50, 92, "เครื่องของผู้เรียน", 20, MUTED),
    box("vs", 55, 135, 240, 80, "VS Code\nRemote-SSH + PORTS tab", BLUE, BLUEBG, 16),
    box("br", 55, 260, 240, 80, "Browser\nhttp://localhost:8080", GREEN, GREENBG, 16),
    box("py", 55, 385, 240, 80, "Terminal\nssh root@localhost -p 2222", ORANGE, ORANGEBG, 16),
    zone(360, 80, 860, 500, BLUE, SKYBG),
    txt(380, 92, "container devtools (--privileged) : มี Docker daemon ของตัวเอง", 19, BLUE),
    box("ssh", 385, 135, 140, 56, "sshd :22", ORANGE, ORANGEBG, 16),
    zone(385, 215, 815, 350, TEAL, TEALBG, id="stack"),
    txt(400, 225, "docker compose -p plane  (image ทางการ makeplane/plane-*:stable)", 16, TEAL),
    box("px", 400, 270, 160, 64, "proxy (Caddy)\n:8080", BLUE, BLUEBG, 15),
    box("web", 600, 262, 130, 44, "web (app)", GREEN, GREENBG, 14),
    box("adm", 600, 318, 130, 44, "admin (god-mode)", GREEN, GREENBG, 13),
    box("spc", 600, 374, 130, 44, "space (public)", GREEN, GREENBG, 14),
    box("api", 770, 262, 150, 56, "api (Django)\n:8000", PURPLE, PURPLEBG, 15),
    box("live", 770, 332, 150, 44, "live (collab)", PURPLE, PURPLEBG, 14),
    box("wk", 770, 390, 150, 56, "worker + beat\n(celery)", PURPLE, PURPLEBG, 14),
    box("db", 970, 262, 210, 44, "postgres 15", TEAL, "#ffffff", 15),
    box("rd", 970, 318, 210, 44, "valkey (redis)", TEAL, "#ffffff", 15),
    box("mq", 970, 374, 210, 44, "rabbitmq (queue)", TEAL, "#ffffff", 15),
    box("mn", 970, 430, 210, 44, "minio (S3 files)", TEAL, "#ffffff", 15),
    box("mig", 400, 470, 160, 70, "migrator\n(รันครั้งเดียว\nแล้วจบ)", MUTED, GREYBG, 13),
    txt(600, 470, "สร้างตาราง/ย้ายข้อมูลใน DB ก่อน api เริ่ม", 13, MUTED),
    arrow("vs", "ssh", BLUE, x=300, y=170, w=85, h=-7),
    arrow("py", "ssh", ORANGE, x=300, y=425, w=85, h=-262),
    arrow("br", "px", GREEN, x=300, y=300, w=100, h=2),
    txt(305, 275, "forward 8080", 13, GREEN),
    arrow("px", "web", BLUE, x=565, y=290, w=35, h=-6),
    arrow("px", "adm", BLUE, x=565, y=302, w=35, h=38),
    arrow("px", "spc", BLUE, x=565, y=312, w=35, h=84),
    arrow("px", "api", BLUE, x=565, y=280, w=205, h=10),
    arrow("api", "db", PURPLE, x=925, y=284, w=45, h=0),
    arrow("api", "rd", PURPLE, x=925, y=295, w=45, h=45),
    arrow("api", "mq", PURPLE, x=925, y=305, w=45, h=91),
    arrow("mq", "wk", TEAL, x=970, y=405, w=-50, h=13),
    arrow("api", "mn", PURPLE, x=925, y=312, w=45, h=140),
    arrow("mig", "db", MUTED, dashed=True, x=565, y=505, w=405, h=-215),
]

# ---------------------------------------------------------------- d04  Waterfall vs Agile
D["d04-waterfall-vs-agile"] = [
    title("Waterfall vs Agile : เมื่อไรที่ลูกค้าได้เห็นของจริง"),
    zone(30, 75, 1150, 190, RED, "#fff5f5"),
    txt(50, 85, "Waterfall — ส่งต่อทีละขั้น ได้ feedback เมื่อจบทั้งสาย (หลายเดือน)", 18, RED),
    box("w1", 55, 125, 200, 60, "Requirements", BLUE, BLUEBG, 16),
    box("w2", 280, 140, 200, 60, "Design", BLUE, BLUEBG, 16),
    box("w3", 505, 155, 200, 60, "Implement", BLUE, BLUEBG, 16),
    box("w4", 730, 170, 200, 60, "Test", BLUE, BLUEBG, 16),
    box("w5", 955, 185, 200, 60, "Release", RED, REDBG, 16),
    arrow("w1", "w2", MUTED, x=255, y=160, w=25, h=10),
    arrow("w2", "w3", MUTED, x=480, y=175, w=25, h=10),
    arrow("w3", "w4", MUTED, x=705, y=190, w=25, h=10),
    arrow("w4", "w5", MUTED, x=930, y=205, w=25, h=10),
    txt(560, 232, "ความเสี่ยง: รู้ว่าผิดโจทย์ตอนท้ายสุด แก้แพงที่สุด", 15, RED),
    zone(30, 290, 1150, 280, GREEN, GREENBG),
    txt(50, 300, "Agile — ทำเป็นรอบสั้น (Sprint/Cycle 1–4 สัปดาห์) ส่ง increment ที่ใช้ได้จริงทุกรอบ", 18, GREEN),
    box("a1", 55, 345, 340, 170, "Sprint 1\n\nวางแผน → ทำ → ทดสอบ → รีวิว\n↓\nIncrement 1 + feedback", ORANGE, ORANGEBG, 16),
    box("a2", 430, 345, 340, 170, "Sprint 2\n\nวางแผน → ทำ → ทดสอบ → รีวิว\n↓\nIncrement 2 + feedback", ORANGE, ORANGEBG, 16),
    box("a3", 805, 345, 340, 170, "Sprint 3 …\n\nปรับลำดับ backlog จาก feedback\n↓\nIncrement 3 …", ORANGE, ORANGEBG, 16),
    arrow("a1", "a2", GREEN, x=400, y=430, w=25, h=0),
    arrow("a2", "a3", GREEN, x=775, y=430, w=25, h=0),
    txt(55, 530, "ใน Plane: Sprint = Cycle · Increment = work items ที่อยู่ในกลุ่ม completed · feedback = comment/activity บน work item", 15, MUTED),
]

# ---------------------------------------------------------------- d05  Code of ethics
eth = [
    ("1. PUBLIC", "ทำเพื่อประโยชน์สาธารณะ\nปลอดภัย · ไม่หลอกลวง", RED, REDBG),
    ("2. CLIENT & EMPLOYER", "ซื่อสัตย์ต่อลูกค้า/นายจ้าง\nโดยไม่ขัดประโยชน์สาธารณะ", ORANGE, ORANGEBG),
    ("3. PRODUCT", "ส่งมอบตามมาตรฐานสูงสุด\nเท่าที่ทำได้ · ทดสอบ · เอกสาร", BLUE, BLUEBG),
    ("4. JUDGMENT", "ตัดสินใจอย่างเป็นอิสระ\nด้วยหลักวิชาชีพ", PURPLE, PURPLEBG),
    ("5. MANAGEMENT", "บริหารด้วยจริยธรรม\nประเมินเวลา/ต้นทุนตามจริง", TEAL, TEALBG),
    ("6. PROFESSION", "รักษาชื่อเสียงวิชาชีพ\nรายงานข้อผิดพลาด", GREEN, GREENBG),
    ("7. COLLEAGUES", "ยุติธรรมและสนับสนุน\nเพื่อนร่วมงาน · รีวิวกันอย่างสร้างสรรค์", MUTED, GREYBG),
    ("8. SELF", "เรียนรู้ตลอดชีวิต\nและยึดจริยธรรมในทุกงาน", "#a61e4d", "#ffdeeb"),
]
els = [title("ACM/IEEE-CS Software Engineering Code of Ethics — 8 หลักการ")]
for i, (h, b, c, bg) in enumerate(eth):
    col, row = i % 4, i // 4
    x, y = 40 + col * 290, 90 + row * 215
    els.append(box(f"e{i}", x, y, 265, 185, f"{h}\n\n{b}", c, bg, 15))
els.append(txt(40, 525, "ใน tracker: ประเมินตามจริง (5) · บันทึกการตัดสินใจไว้ใน work item (4) · รายงาน bug ทันที (6) · review อย่างสุภาพใน comment (7)", 15, MUTED))
D["d05-code-of-ethics"] = els

# ---------------------------------------------------------------- d06  Work item anatomy
D["d06-work-item-anatomy"] = [
    title("กายวิภาคของ Work item ที่ดี : สื่อสารครบในใบเดียว"),
    box("card", 40, 80, 620, 480, "", BLUE, "#ffffff", 16),
    txt(60, 95, "PLAB-12  ·  ผู้ใช้ต้องรีเซ็ตรหัสผ่านได้เองผ่านอีเมล", 20, INK),
    txt(60, 135, "State: In Progress    Priority: High    Assignee: <YOUR_NAME>", 15, MUTED),
    txt(60, 160, "Labels: backend, security    Estimate: 5 pts    Cycle: Sprint 2    Module: Auth", 15, MUTED),
    box("desc", 60, 195, 580, 150, "คำอธิบาย (Why + What)\nในฐานะผู้ใช้ ฉันต้องการรีเซ็ตรหัสผ่านเอง เพื่อไม่ต้องรอแอดมิน\n\nAcceptance criteria\n[ ] ขอลิงก์รีเซ็ตทางอีเมลได้   [ ] ลิงก์หมดอายุใน 15 นาที\n[ ] รหัสใหม่ต้องยาว ≥ 8 ตัว    [ ] มี test ครอบทั้ง 3 ข้อ", GREEN, GREENBG, 14),
    box("sub", 60, 360, 280, 80, "Sub-work items\n· สร้าง endpoint /reset\n· เทมเพลตอีเมล", PURPLE, PURPLEBG, 14),
    box("rel", 360, 360, 280, 80, "Relations / Links\nblocked by PLAB-9\nPR #42 · design doc", ORANGE, ORANGEBG, 14),
    box("act", 60, 455, 580, 90, "Activity (อัตโนมัติ)\n<YOUR_NAME> เปลี่ยน state Todo → In Progress · เมื่อ 2 ชม. ก่อน\n<TEAMMATE> comment: \"ใช้ token แบบ one-time ดีกว่า\"", MUTED, GREYBG, 13),
    zone(700, 80, 480, 480, TEAL, TEALBG),
    txt(720, 92, "ทำไมมืออาชีพต้องเขียนแบบนี้", 19, TEAL),
    box("r1", 720, 130, 440, 70, "Title = ผลลัพธ์ที่ผู้ใช้ได้ ไม่ใช่งานที่ทำ\n(ทดสอบได้ · จบได้)", TEAL, "#ffffff", 14),
    box("r2", 720, 215, 440, 70, "Acceptance criteria = Definition of Done\nระดับใบงาน → ลดการตีความคนละแบบ", TEAL, "#ffffff", 14),
    box("r3", 720, 300, 440, 70, "Estimate + Priority = ความซื่อสัตย์ต่อแผน\n(หลักการ Management ในจรรยาบรรณ)", TEAL, "#ffffff", 14),
    box("r4", 720, 385, 440, 70, "Links/Relations = traceability\nโจทย์ ↔ โค้ด ↔ รีวิว ↔ release", TEAL, "#ffffff", 14),
    box("r5", 720, 470, 440, 70, "Activity log = ความโปร่งใส\nใครตัดสินใจอะไร เมื่อไร ทำไม", TEAL, "#ffffff", 14),
]

# ---------------------------------------------------------------- d09  LAB4 import + webhook flow
D["d09-api-import-flow"] = [
    title("LAB 4 : ย้ายบอร์ดจาก Trello/Jira เข้า Plane ด้วย REST API แล้วฟัง Webhook"),
    box("csv", 40, 110, 220, 90, "trello_export.csv\n(หรือ Jira CSV)\nlist,card,label,due", ORANGE, ORANGEBG, 15),
    box("py", 330, 100, 260, 110, "import_board.py\nrequests + X-API-Key\nidempotent (ตรวจซ้ำก่อนสร้าง)", PURPLE, PURPLEBG, 15),
    box("api", 660, 100, 240, 110, "Plane REST API v1\n/api/v1/workspaces/<slug>/\nprojects/<id>/work-items/", BLUE, BLUEBG, 14),
    box("db", 970, 110, 190, 90, "Plane DB\nstates · labels\nwork items · cycle", TEAL, TEALBG, 15),
    arrow("csv", "py", ORANGE, x=265, y=155, w=60, h=0),
    arrow("py", "api", PURPLE, x=595, y=155, w=60, h=0),
    arrow("api", "db", BLUE, x=905, y=155, w=60, h=0),
    txt(600, 128, "POST/GET", 13, PURPLE),
    zone(40, 260, 1120, 300, GREEN, GREENBG),
    txt(60, 272, "ขาออก : Plane แจ้งเหตุการณ์กลับมาหาเรา (Webhook)", 19, GREEN),
    box("ev", 60, 320, 260, 90, "เหตุการณ์ใน Plane\nสร้าง/แก้ work item\nเปลี่ยน state · comment", BLUE, BLUEBG, 15),
    box("wk", 380, 320, 240, 90, "worker (celery)\nส่ง HTTP POST\nพร้อม X-Plane-Signature", PURPLE, PURPLEBG, 14),
    box("rx", 680, 320, 240, 90, "webhook_receiver.py\n(Flask :9000)\nตรวจลายเซ็น HMAC", GREEN, "#ffffff", 14),
    box("out", 980, 320, 170, 90, "console / log\nหรือส่งต่อ\nSlack · CI", MUTED, GREYBG, 14),
    arrow("ev", "wk", BLUE, x=325, y=365, w=50, h=0),
    arrow("wk", "rx", PURPLE, x=625, y=365, w=50, h=0),
    arrow("rx", "out", GREEN, x=925, y=365, w=50, h=0),
    txt(60, 440, "สิ่งที่พิสูจน์ : เครื่องมือ tracking ไม่ใช่เกาะเดี่ยว — API ใช้ป้อนข้อมูลเข้า (import/automation) และ webhook ใช้ผูกกับระบบอื่น (CI, chat, dashboard)\nแบบเดียวกับ Jira REST API + Jira webhooks และ Trello REST API + Butler", 15, INK),
]

# ---------------------------------------------------------------- d10  LAB5 dashboard flow
D["d10-dashboard-flow"] = [
    title("LAB 5 : Product Tracking Dashboard — คำนวณ metric เองจากข้อมูลจริงใน Plane"),
    box("pl", 40, 110, 230, 100, "Plane API\nwork items · states\ncycles · activities", BLUE, BLUEBG, 15),
    box("col", 340, 100, 260, 120, "collector.py\nดึงทุก N วินาที\nแปลงเป็น metric", PURPLE, PURPLEBG, 15),
    box("m", 670, 80, 230, 160, "metrics.json\n· burndown (คงเหลือ/วัน)\n· CFD (ใบต่อ state/วัน)\n· velocity ต่อ cycle\n· lead / cycle time", TEAL, TEALBG, 14),
    box("srv", 970, 100, 190, 120, "dashboard app\n(FastAPI :8050)\nHTML+SVG inline\nไม่ใช้ CDN", GREEN, GREENBG, 14),
    arrow("pl", "col", BLUE, x=275, y=160, w=60, h=0),
    arrow("col", "m", PURPLE, x=605, y=160, w=60, h=0),
    arrow("m", "srv", TEAL, x=905, y=160, w=60, h=0),
    txt(285, 135, "X-API-Key", 13, BLUE),
    box("br", 970, 300, 190, 80, "Browser\nlocalhost:8050", ORANGE, ORANGEBG, 15),
    arrow("br", "srv", ORANGE, x=1065, y=295, w=0, h=-70),
    zone(40, 280, 860, 280, MUTED, GREYBG),
    txt(60, 292, "สูตรที่ dashboard ใช้ (เหมือน Jira reports)", 18, MUTED),
    box("f1", 60, 330, 400, 60, "Burndown(d) = Σ estimate ของใบที่ยังไม่ completed ณ วัน d", BLUE, "#ffffff", 14),
    box("f2", 480, 330, 400, 60, "Velocity(cycle) = Σ estimate ของใบที่ completed ใน cycle", GREEN, "#ffffff", 14),
    box("f3", 60, 410, 400, 60, "Lead time = completed_at − created_at", TEAL, "#ffffff", 14),
    box("f4", 480, 410, 400, 60, "Cycle time = completed_at − started_at (จาก activity)", ORANGE, "#ffffff", 14),
    box("f5", 60, 490, 820, 55, "CFD(d, state) = จำนวนใบที่อยู่ใน state นั้น ณ สิ้นวัน d  (สร้างจาก activity log ย้อนหลัง)", PURPLE, "#ffffff", 14),
]

# ---------------------------------------------------------------- d11  Jira / Trello / Plane concept map
cm = [
    ("Board", "Project + Board", "Project"),
    ("List", "Column (workflow status)", "State (5 groups)"),
    ("Card", "Issue (Story/Task/Bug)", "Work item"),
    ("Checklist", "Sub-task", "Sub-work item"),
    ("Label", "Label / Component", "Label"),
    ("Due date", "Due date", "Start · Target date"),
    ("—", "Sprint", "Cycle"),
    ("—", "Epic", "Module"),
    ("—", "Story points", "Estimate"),
    ("Butler rules", "Automation + JQL", "Views + Webhooks + API"),
    ("Power-Ups", "Marketplace apps", "Integrations / self-host"),
]
els = [title("ศัพท์เดียวกันคนละชื่อ : Trello · Jira · Plane"),
       box("h1", 40, 70, 300, 46, "Trello", BLUE, BLUEBG, 19),
       box("h2", 380, 70, 380, 46, "Jira Software", BLUE, BLUEBG, 19),
       box("h3", 800, 70, 380, 46, "Plane", GREEN, GREENBG, 19)]
y = 126
for i, (t, j, p) in enumerate(cm):
    bg = "#ffffff" if i % 2 == 0 else GREYBG
    els.append(box(f"t{i}", 40, y, 300, 38, t, MUTED, bg, 15))
    els.append(box(f"j{i}", 380, y, 380, 38, j, MUTED, bg, 15))
    els.append(box(f"p{i}", 800, y, 380, 38, p, GREEN, bg, 15))
    y += 40
els.append(txt(40, y + 8, "“—” = Trello ไม่มีแนวคิดนี้ในตัว (ต้องใช้ Power-Up)  ·  Plane และ Jira รองรับทั้ง Scrum และ Kanban ในเครื่องมือเดียว", 15, MUTED))
D["d11-jira-trello-plane-terms"] = els

# ---------------------------------------------------------------- d07  Request path through Caddy
D["d07-request-path"] = [
    title("เส้นทาง request : Caddy ตัดสินใจจาก prefix ของ URL แล้วส่งต่อให้ container ที่รับผิดชอบ"),
    box("brw", 40, 180, 230, 80, "Browser\nlocalhost:8080/...", GREEN, GREENBG, 15),
    box("cad", 330, 160, 220, 120, "proxy (Caddy)\n:80 ในเครือข่าย compose\nเปิดออกมาเป็น :8080", BLUE, BLUEBG, 14),
    arrow("brw", "cad", GREEN, x=275, y=220, w=50, h=0),
    box("r1", 640, 70, 400, 44, "/god-mode/*  →  admin:3000", PURPLE, PURPLEBG, 14),
    box("r2", 640, 134, 400, 44, "/spaces/*  →  space:3000", PURPLE, PURPLEBG, 14),
    box("r3", 640, 198, 400, 44, "/live/*  →  live:3000 (WebSocket)", PURPLE, PURPLEBG, 14),
    box("r4", 640, 262, 400, 44, "/api/*  /auth/*  /static/*  →  api:8000", ORANGE, ORANGEBG, 14),
    box("r5", 640, 326, 400, 44, "/uploads/*  →  plane-minio:9000", TEAL, TEALBG, 14),
    box("r6", 640, 390, 400, 44, "/*  (ที่เหลือทั้งหมด)  →  web:3000", GREEN, GREENBG, 14),
    arrow("cad", "r1", PURPLE, x=555, y=195, w=85, h=-103),
    arrow("cad", "r2", PURPLE, x=555, y=205, w=85, h=-49),
    arrow("cad", "r3", PURPLE, x=555, y=215, w=85, h=5),
    arrow("cad", "r4", ORANGE, x=555, y=225, w=85, h=59),
    arrow("cad", "r5", TEAL, x=555, y=235, w=85, h=113),
    arrow("cad", "r6", GREEN, x=555, y=245, w=85, h=167),
    zone(640, 460, 540, 110, ORANGE, "#fff4e6"),
    txt(655, 468, "หลังบ้านของ api (LAB 2 ส่องด้วย docker compose exec)", 14, ORANGE),
    box("db", 655, 498, 160, 50, "postgres :5432", TEAL, "#ffffff", 13),
    box("rd", 830, 498, 160, 50, "valkey :6379", TEAL, "#ffffff", 13),
    box("mq", 1005, 498, 160, 50, "rabbitmq :5672", TEAL, "#ffffff", 13),
    zone(40, 330, 560, 150, MUTED, GREYBG),
    txt(60, 340, "ลองเองใน LAB 2", 17, MUTED),
    txt(60, 372, "docker compose -p plane logs -f proxy\n   # ดู path ที่วิ่งผ่าน Caddy\ncurl -s localhost:8080/api/instances/ | head -c 200   # ตกที่ api\ncurl -sI localhost:8080/god-mode/ | head -3            # ตกที่ admin", 14, INK),
]

# ---------------------------------------------------------------- d08  ER model (core)
D["d08-er-model"] = [
    title("โมเดลข้อมูลของ Plane : Instance → Workspace → Project → Work item (+ ดาวบริวาร)"),
    zone(30, 75, 1150, 90, MUTED, GREYBG),
    txt(50, 82, "ระดับ instance", 15, MUTED),
    box("ins", 60, 105, 240, 46, "Instance (is_setup_done)", MUTED, "#ffffff", 14),
    box("adm", 350, 105, 250, 46, "InstanceAdmin (role 20)", MUTED, "#ffffff", 14),
    box("usr", 660, 105, 180, 46, "User (email)", BLUE, BLUEBG, 14),
    arrow("ins", "adm", MUTED, x=305, y=128, w=45, h=0),
    arrow("usr", "adm", BLUE, x=655, y=128, w=-55, h=0),
    zone(30, 180, 1150, 95, BLUE, SKYBG),
    txt(50, 187, "ระดับ workspace", 15, BLUE),
    box("ws", 60, 213, 200, 50, "Workspace (slug)", BLUE, BLUEBG, 14),
    box("wm", 300, 213, 330, 50, "WorkspaceMember · role 20 / 15 / 5", BLUE, "#ffffff", 13),
    box("lab", 660, 213, 110, 50, "Label", TEAL, TEALBG, 14),
    box("vw", 785, 213, 120, 50, "View", TEAL, TEALBG, 14),
    box("pg", 920, 213, 110, 50, "Page", TEAL, TEALBG, 14),
    box("wh", 1045, 213, 120, 50, "Webhook · Token", TEAL, TEALBG, 12),
    arrow("ws", "wm", BLUE, x=265, y=238, w=35, h=0),
    arrow("usr", "wm", BLUE, dashed=True, x=720, y=155, w=-270, h=58),
    zone(30, 290, 1150, 380, GREEN, GREENBG),
    txt(50, 297, "ระดับ project", 15, GREEN),
    box("pr", 60, 330, 220, 56, "Project (identifier PLAB)", GREEN, "#ffffff", 13),
    box("st", 60, 404, 220, 92, "State\ngroup: backlog · unstarted\nstarted · completed · cancelled", GREEN, "#ffffff", 11),
    box("est", 60, 516, 220, 50, "Estimate (points/categories)", TEAL, TEALBG, 12),
    box("ik", 60, 590, 220, 50, "Intake → Triage state", TEAL, TEALBG, 12),
    box("iss", 380, 330, 300, 170, "Work item (Issue)\nPLAB-<sequence_id>\npriority · state · estimate_point\nstart/target date · completed_at\nparent → sub-work items", ORANGE, ORANGEBG, 13),
    box("cy", 780, 330, 190, 56, "Cycle (start/end date)", PURPLE, PURPLEBG, 13),
    box("md", 780, 410, 190, 56, "Module (status · lead)", PURPLE, PURPLEBG, 13),
    box("cyi", 1000, 330, 165, 56, "CycleIssue (M:N)", PURPLE, "#ffffff", 12),
    box("mdi", 1000, 410, 165, 56, "ModuleIssue (M:N)", PURPLE, "#ffffff", 12),
    box("as", 380, 590, 150, 50, "Assignees", MUTED, "#ffffff", 12),
    box("lb", 545, 590, 150, 50, "Labels", MUTED, "#ffffff", 12),
    box("cm", 710, 590, 150, 50, "Comments", MUTED, "#ffffff", 12),
    box("ac", 875, 590, 150, 50, "Activity log", MUTED, "#ffffff", 12),
    box("ln", 1040, 590, 125, 50, "Links · Files", MUTED, "#ffffff", 12),
    arrow("ws", "pr", GREEN, x=160, y=268, w=0, h=62),
    arrow("pr", "st", GREEN, x=170, y=391, w=0, h=19),
    arrow("pr", "iss", GREEN, x=285, y=358, w=95, h=30),
    arrow("st", "iss", GREEN, dashed=True, x=285, y=448, w=95, h=-30),
    arrow("est", "iss", TEAL, dashed=True, x=285, y=535, w=95, h=-70),
    arrow("ik", "iss", TEAL, dashed=True, x=285, y=609, w=95, h=-120),
    arrow("iss", "cy", PURPLE, x=685, y=380, w=95, h=-22),
    arrow("iss", "md", PURPLE, x=685, y=430, w=95, h=8),
    arrow("cy", "cyi", PURPLE, x=975, y=358, w=25, h=0),
    arrow("md", "mdi", PURPLE, x=975, y=438, w=25, h=0),
    arrow("iss", "as", MUTED, x=455, y=505, w=0, h=85),
    arrow("iss", "lb", MUTED, x=560, y=505, w=60, h=85),
    arrow("iss", "cm", MUTED, x=620, y=505, w=165, h=85),
    arrow("iss", "ac", MUTED, x=660, y=505, w=290, h=85),
    arrow("iss", "ln", MUTED, x=680, y=490, w=420, h=100),
]

# ---------------------------------------------------------------- d12  Celery + webhook flow
D["d12-celery-webhook-flow"] = [
    title("เบื้องหลัง 1 คลิก : api ส่งงานเข้า RabbitMQ → worker ทำต่อ → webhook ยิงออกไปข้างนอก"),
    box("u", 40, 120, 190, 80, "ผู้ใช้เปลี่ยน state\nของ PLAB-12", GREEN, GREENBG, 15),
    box("api", 300, 110, 220, 100, "api\nบันทึกลง DB แล้วตอบ 200 ทันที\n+ publish task", ORANGE, ORANGEBG, 14),
    box("mq", 590, 120, 200, 80, "rabbitmq\nqueue: celery", TEAL, TEALBG, 15),
    box("wk", 860, 110, 220, 100, "worker (celery)\nissue_activity →\nnotifications · webhook", PURPLE, PURPLEBG, 14),
    arrow("u", "api", GREEN, x=235, y=160, w=60, h=0),
    arrow("api", "mq", ORANGE, x=525, y=160, w=60, h=0),
    arrow("mq", "wk", TEAL, x=795, y=160, w=60, h=0),
    txt(530, 135, "AMQP", 13, ORANGE), txt(800, 135, "consume", 13, TEAL),
    box("db", 300, 250, 220, 60, "postgres\nissue_activities", TEAL, "#ffffff", 14),
    arrow("wk", "db", PURPLE, x=860, y=215, w=-340, h=55),
    box("ntf", 640, 260, 190, 60, "in-app Notification\n(กระดิ่งใน UI)", BLUE, BLUEBG, 13),
    arrow("wk", "ntf", PURPLE, x=900, y=215, w=-70, h=60),
    box("hook", 880, 260, 240, 90, "HTTP POST → receiver\nX-Plane-Event\nX-Plane-Signature (HMAC-SHA256)", RED, REDBG, 13),
    arrow("wk", "hook", RED, x=990, y=215, w=5, h=45),
    box("rx", 880, 390, 240, 70, "event-wall (FastAPI)\nตรวจลายเซ็นด้วย secret แล้วโชว์สด", GREEN, "#ffffff", 13),
    arrow("hook", "rx", RED, x=1000, y=355, w=0, h=35),
    zone(40, 380, 800, 190, MUTED, GREYBG),
    txt(60, 392, "สิ่งที่ LAB 2 และ LAB 8 ให้เห็นจริง", 17, MUTED),
    txt(60, 425, "• docker compose -p plane stop worker → สร้าง/แก้ work item หลายใบ → rabbitmqctl list_queues เห็น celery กองสูงขึ้น\n• start worker → คิวถูกดูดจนเป็น 0 ภายในไม่กี่วินาที (backpressure แบบเดียวกับ LAB RabbitMQ)\n• receiver ล่ม → worker retry 5 ครั้ง (backoff 600 s) แล้วปิด webhook ให้อัตโนมัติ · ดูได้ที่ webhook_logs", 14, INK),
]

# ---------------------------------------------------------------- d13  Roles & permissions
D["d13-roles"] = [
    title("บทบาทในทีม = สิทธิ์ในเครื่องมือ : Instance admin · Workspace · Project"),
    box("ia", 40, 100, 300, 90, "Instance admin (god-mode)\nตั้งค่า SMTP · เปิด/ปิด sign-up\nสร้าง workspace", RED, REDBG, 14),
    box("wa", 40, 230, 300, 90, "Workspace Admin (20)\nเชิญสมาชิก · ตั้งค่า workspace\nสร้าง/ลบโปรเจกต์ · webhooks", ORANGE, ORANGEBG, 14),
    box("wmb", 40, 360, 300, 90, "Member (15)\nสร้าง/แก้ work item · cycles\nmodules · pages · views", BLUE, BLUEBG, 14),
    box("wg", 40, 490, 300, 70, "Guest (5)\nดูและ comment เท่านั้น\n(ไม่เห็นทุกอย่างถ้าไม่เปิด guest_view_all)", MUTED, GREYBG, 13),
    arrow("ia", "wa", MUTED, x=190, y=195, w=0, h=30),
    arrow("wa", "wmb", MUTED, x=190, y=325, w=0, h=30),
    arrow("wmb", "wg", MUTED, x=190, y=455, w=0, h=30),
    zone(400, 90, 780, 480, TEAL, TEALBG),
    txt(420, 100, "แมปกับบทบาทใน Scrum / ทีมจริง", 18, TEAL),
    box("po", 420, 140, 360, 80, "Product Owner → Admin หรือ Member\nดูแล backlog · ลำดับความสำคัญ · รับงานจาก Intake", ORANGE, "#ffffff", 13),
    box("sm", 420, 240, 360, 80, "Scrum Master → Admin\nตั้ง Cycle · states · estimates · เชิญคน", RED, "#ffffff", 13),
    box("dev", 420, 340, 360, 80, "Developers → Member\nขยับการ์ด · comment · ปิดงาน · sub-work items", BLUE, "#ffffff", 13),
    box("stk", 420, 440, 360, 80, "ผู้มีส่วนได้เสีย / ลูกค้า → Guest หรือ Sites\nดูบอร์ดสาธารณะ · โหวต · comment", MUTED, "#ffffff", 13),
    box("ethic", 800, 140, 360, 380, "มุมจรรยาบรรณ\n\n• สิทธิ์เท่าที่จำเป็น (least privilege)\n  → หลักการ Management/Product\n\n• Activity log บันทึกว่าใครแก้อะไร\n  → ความรับผิดชอบตรวจสอบได้\n\n• Guest เห็นเฉพาะที่ควรเห็น\n  → รักษาความลับของลูกค้า\n\n• API token ผูกกับคนและหมดอายุได้\n  → ไม่แชร์รหัสกัน ไม่ใส่ในโค้ด", PURPLE, PURPLEBG, 13),
]

# ---------------------------------------------------------------- d14  First-run flow
D["d14-first-run"] = [
    title("ครั้งแรกที่เปิด Plane : จาก container ว่าง ๆ ถึง workspace แรก"),
    box("f1", 40, 110, 200, 90, "1. docker compose up -d\nmigrator → api\n(register + configure)", BLUE, BLUEBG, 13),
    box("f2", 280, 110, 200, 90, "2. เปิด localhost:8080\n\"Welcome to Plane\"\nGet started", GREEN, GREENBG, 13),
    box("f3", 520, 110, 200, 90, "3. /god-mode/\nSetup your Plane Instance\nสร้าง instance admin", RED, REDBG, 13),
    box("f4", 760, 110, 200, 90, "4. /god-mode/general/\nตั้งค่า instance\n(ยังไม่ต้องแตะ)", MUTED, GREYBG, 13),
    box("f5", 1000, 110, 170, 90, "5. กลับไป /\nsign in ด้วย email\n+ password", ORANGE, ORANGEBG, 13),
    arrow("f1", "f2", MUTED, x=245, y=155, w=30, h=0),
    arrow("f2", "f3", MUTED, x=485, y=155, w=30, h=0),
    arrow("f3", "f4", MUTED, x=725, y=155, w=30, h=0),
    arrow("f4", "f5", MUTED, x=965, y=155, w=30, h=0),
    box("f6", 1000, 260, 170, 90, "6. Onboarding\nCreate your profile", ORANGE, ORANGEBG, 13),
    box("f7", 760, 260, 200, 90, "7. Create your workspace\nname + slug\n(seed โปรเจกต์ตัวอย่างให้)", ORANGE, ORANGEBG, 13),
    box("f8", 520, 260, 200, 90, "8. Invite teammates\n→ \"I'll do it later\"", ORANGE, ORANGEBG, 13),
    box("f9", 280, 260, 200, 90, "9. Home ของ workspace\nProjects → Add Project", GREEN, GREENBG, 13),
    box("f10", 40, 260, 200, 90, "10. เปิดฟีเจอร์ Cycles\nModules · Views · Pages\n(Intake ปิดไว้ก่อน)", GREEN, GREENBG, 13),
    arrow("f5", "f6", MUTED, x=1085, y=205, w=0, h=55),
    arrow("f6", "f7", MUTED, x=995, y=305, w=-30, h=0),
    arrow("f7", "f8", MUTED, x=755, y=305, w=-30, h=0),
    arrow("f8", "f9", MUTED, x=515, y=305, w=-30, h=0),
    arrow("f9", "f10", MUTED, x=275, y=305, w=-30, h=0),
    zone(40, 400, 1130, 170, TEAL, TEALBG),
    txt(60, 412, "ค่าที่ต้องรู้ (placeholder สำหรับ LAB เท่านั้น)", 17, TEAL),
    txt(60, 445, "อีเมล admin@example.com · รหัสผ่าน Plane@Lab2026! (ต้องผ่าน zxcvbn ≥ 3: ยาว ≥ 8 มีตัวใหญ่ เล็ก ตัวเลข อักขระพิเศษ)\nworkspace slug devtools-lab · โปรเจกต์ Plane Lab / identifier PLAB\nไม่ต้องมี SMTP: sign-up เปิดอยู่โดยปริยาย และคำเชิญใช้ปุ่ม Copy link ได้", 14, INK),
    txt(60, 520, "curl -s http://localhost:8080/api/instances/ | python3 -m json.tool | grep -E 'is_setup_done|enable_signup'", 14, MUTED),
]


def run(cmd):
    return subprocess.run(cmd, shell=True, env=ENV, capture_output=True, text=True)


def main():
    os.makedirs(TMP, exist_ok=True)
    os.makedirs(os.path.join(OUT, "scenes"), exist_ok=True)
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
        run(f"npx -y mcp-excalidraw-server export --out {OUT}/scenes/{name}.excalidraw")
        print(f"[{name}] {'OK' if ok else 'FAIL'} size={os.path.getsize(svg) if os.path.exists(svg) else 0} rc={r.returncode}")


if __name__ == "__main__":
    main()
