#!/usr/bin/env python3
"""d32 — Velocity bars (18 · 22 · 20) → average 20 → forecast remaining 120 pt = 6 sprints (5.5–6.7)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

# ---- bar chart geometry (left zone) -----------------------------------------
BASE = 440            # y of the x-axis
SCALE = 10            # px per point
BAR_W = 80
sprints = [("Sprint 1", 18, 135), ("Sprint 2", 22, 245), ("Sprint 3", 20, 355)]
AVG = 20
avg_y = BASE - AVG * SCALE

els = [
    title("Velocity : ใช้ประวัติ 3 sprint ล่าสุด พยากรณ์ว่าเหลืออีกกี่ sprint"),

    # ---------------- left : velocity chart
    zone(30, 75, 560, 445, TEAL, TEALBG),
    txt(50, 87, "Velocity = Σ points ของงานที่ Done ในแต่ละ sprint", 18, TEAL),
    txt(48, 140, "points\nDone", 13, MUTED),
    line(110, 140, [[0, 0], [0, BASE - 140]], MUTED, 2),          # y axis
    line(110, BASE, [[0, 0], [455, 0]], MUTED, 2),                 # x axis
    line(112, avg_y, [[0, 0], [453, 0]], RED, 2, dashed=True),     # average line (behind the bars)
]
for i, (name, pts, x) in enumerate(sprints):
    h = pts * SCALE
    top = BASE - h
    cx = x + BAR_W // 2
    els.append(box(f"s{i+1}", x, top, BAR_W, h, "", BLUE, BLUEBG))
    els.append(txt(cx - 22, top + 8, f"{pts} pt", 17, BLUE))       # value at the top of each bar
    els.append(txt(cx - 29, BASE + 8, name, 15, INK))

els += [
    box("avg", 450, avg_y - 50, 125, 44, "เฉลี่ย 20 pt", RED, "#ffffff", 15, dashed=True),
    txt(60, 480, "เฉลี่ย = (18 + 22 + 20) ÷ 3 = 20 pt / sprint  → ไม้บรรทัดของทีมนี้เท่านั้น", 15, RED),

    # ---------------- right : forecast
    zone(620, 75, 560, 445, PURPLE, PURPLEBG),
    txt(640, 87, "พยากรณ์ (forecast) จาก velocity เฉลี่ย", 18, PURPLE),
    box("b1", 645, 125, 510, 80, "backlog ที่เหลือ 120 pt ÷ velocity เฉลี่ย 20\n= 6 sprints", BLUE, BLUEBG, 17),
    box("b2", 645, 235, 510, 80, "ช่วง (เร็วสุด … ช้าสุด)\n120 ÷ 22 … 120 ÷ 18 = 5.5 – 6.7 sprints", ORANGE, ORANGEBG, 17),
    box("b3", 645, 345, 510, 80, "sprint ละ 2 สัปดาห์\n≈ 11 – 14 สัปดาห์", GREEN, GREENBG, 17),
    arrow("b1", "b2", MUTED, x=900, y=210, w=0, h=20),
    arrow("b2", "b3", MUTED, x=900, y=320, w=0, h=20),
    arrow("avg", "b1", RED, dashed=True, x=580, y=avg_y - 28, w=60, h=-32),
    txt(645, 480, "บอกลูกค้าเป็นช่วง ไม่ใช่วันเดียว · คำนวณใหม่ทุกครั้งที่จบ sprint", 14, MUTED),

    # ---------------- footer
    box("warn", 30, 545, 1150, 60, "ใช้ประวัติพยากรณ์ ไม่ใช่ตั้งเป้า (Goodhart)  ·  ห้ามเทียบ velocity ข้ามทีม", RED, REDBG, 17),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "d32-velocity-forecast.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
