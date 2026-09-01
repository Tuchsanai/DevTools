#!/usr/bin/env python3
"""d36 — Annotated Cumulative Flow Diagram (Excalidraw scene, uses diagrams.py helpers).

Three stacked bands (To do / In Progress / Done) over 14 days; the In Progress band widens after day 8 (bottleneck).
Annotations: vertical gap = WIP, horizontal gap ≈ lead time, slope of Done = throughput, widening middle band = bottleneck.
"""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d36-cfd-annotated"
GRID = "#dee2e6"

# ---- plot geometry: days 0..14 (50 px/day), 0..64 work items (6.5 px/item)
PX, PY, PW, PH = 100, 100, 700, 416
DX, DY, YMAX = 50, 6.5, 64


def X(d):
    return d * DX


def Y(v):
    return (YMAX - v) * DY


def band(pts, bg):
    """closed polygon (first point repeated) with a solid fill and no visible stroke."""
    e = line(PX, PY, pts + [pts[0]], "transparent", 1)
    e["backgroundColor"] = bg
    e["fillStyle"] = "solid"
    return e


def dbl_arrow(x, y, dx, dy, color):
    return {"type": "arrow", "x": x, "y": y, "width": dx, "height": dy, "points": [[0, 0], [dx, dy]],
            "strokeColor": color, "strokeWidth": 2, "roughness": 0,
            "startArrowhead": "arrow", "endArrowhead": "arrow"}


# ---- cumulative data per day: arrivals (created), started (entered In Progress), done
days = list(range(15))
A = [0] + [4 * d + 4 for d in days[1:]]                    # 0, 8, 12, ... 60   (+4/day)
S = [0, 0] + [4 * d - 4 for d in days[2:]]                 # 0, 0, 4, ... 52    (+4/day)
D = [0 if d <= 2 else (4 * d - 10 if d <= 8 else 22 + 2 * (d - 8)) for d in days]  # 4/day until day 8, then 2/day

pa = [[X(d), Y(A[d])] for d in days]
ps = [[X(d), Y(S[d])] for d in days]
pd = [[X(d), Y(D[d])] for d in days]

els = [title("Cumulative Flow Diagram (CFD) : อ่าน WIP · lead time · throughput · คอขวด จากรูปเดียว"),
       txt(40, 70, "จำนวนงานสะสม (ใบ)", 14, MUTED),
       box(None, PX, PY, PW, PH, "", "#adb5bd", "#ffffff")]

# grid (under the bands)
for v in range(10, YMAX, 10):
    els.append(line(PX, PY + Y(v), [[0, 0], [PW, 0]], GRID, 1))

# stacked bands: To do (A..S), In Progress (S..D), Done (D..axis)
els += [
    band(pa + ps[::-1], SKYBG),
    band(ps + pd[::-1], ORANGEBG),
    band(pd + [[X(14), Y(0)], [X(0), Y(0)]], GREENBG),
    line(PX, PY, pa, BLUE, 3),
    line(PX, PY, ps, ORANGE, 3),
    line(PX, PY, pd, GREEN, 3),
    line(PX, PY, [[0, 0], [0, PH]], INK, 2),          # y axis
    line(PX, PY + PH, [[0, 0], [PW, 0]], INK, 2),     # x axis
]
for d in days:
    els.append(line(PX + X(d), PY + PH, [[0, 0], [0, 5]], INK, 1))
    els.append(txt(PX + X(d) - (8 if d >= 10 else 4), PY + PH + 8, str(d), 13, MUTED))
for v in range(0, YMAX, 10):
    els.append(txt(PX - (26 if v >= 10 else 18), PY + Y(v) - 8, str(v), 13, MUTED))
els.append(txt(PX + PW // 2 - 30, PY + PH + 28, "วัน (day)", 14, MUTED))

# legend (top-left, empty area above the arrivals line)
for i, (name, c, bg) in enumerate([("To do", BLUE, SKYBG), ("In Progress", ORANGE, ORANGEBG), ("Done", GREEN, GREENBG)]):
    yy = PY + 14 + i * 22
    els.append(box(None, PX + 16, yy, 22, 14, "", c, bg))
    els.append(txt(PX + 46, yy - 3, name, 14, c))

# band labels at the right end (bands are widest there)
els += [
    txt(750, 158, "To do", 14, BLUE),
    txt(722, 226, "In Progress", 14, ORANGE),
    txt(735, 430, "Done", 15, GREEN),
]

# ---- annotations -------------------------------------------------------------
# 1) WIP : vertical gap inside the middle band at day 11 (S=40, D=28)
els += [
    dbl_arrow(PX + X(11), PY + Y(D[11]), 0, Y(S[11]) - Y(D[11]), ORANGE),
    txt(610, 285, "WIP", 16, ORANGE),
]
# 2) lead time : horizontal gap at 20 items — arrivals reach 20 on day 4, done reaches 20 on day 7.5
els += [
    dbl_arrow(PX + X(4), PY + Y(20), X(7.5) - X(4), 0, BLUE),
    txt(483, 392, "≈ lead time (3.5 วัน)", 14, BLUE),
]
# 3) throughput : slope triangle on the Done line between day 4 (6) and day 6 (14)
els += [
    line(PX + X(4), PY + Y(D[4]), [[0, 0], [X(6) - X(4), 0]], GREEN, 2, dashed=True),
    line(PX + X(6), PY + Y(D[4]), [[0, 0], [0, Y(D[6]) - Y(D[4])]], GREEN, 2, dashed=True),
    txt(333, 481, "2 วัน", 12, GREEN),
    txt(412, 436, "throughput = ความชันของเส้น Done\n8 ใบ ÷ 2 วัน = 4 ใบ/วัน", 14, GREEN),
]
# 4) bottleneck : callout above the chart with an arrow into the widening middle band
els += [
    box("bn", 395, 110, 280, 58, "แถบกลางอ้วนขึ้น = คอขวด\nงานเข้าเร็วกว่าที่ปิดได้", RED, REDBG, 13),
    {"id": "mk", "type": "ellipse", "x": 695, "y": 264, "width": 10, "height": 10, "backgroundColor": RED,
     "strokeColor": RED, "fillStyle": "solid", "strokeWidth": 1, "roughness": 0},
    arrow("bn", "mk", RED, x=650, y=168, w=45, h=96),
]

# ---- right panel : how to read a CFD ------------------------------------------
els += [
    zone(825, 66, 355, 480, TEAL, TEALBG),
    txt(840, 76, "วิธีอ่าน CFD ในรูปเดียว", 18, TEAL),
    box("r1", 840, 108, 325, 74, "ช่องว่างแนวตั้ง = WIP\nงานค้างใน In Progress วันนั้น", ORANGE, "#ffffff", 13),
    box("r2", 840, 196, 325, 74, "ช่องว่างแนวนอน ≈ Lead time\nเข้า To do → ออก Done", BLUE, "#ffffff", 13),
    box("r3", 840, 284, 325, 74, "ความชัน Done = Throughput\nปิดงานได้กี่ใบต่อวัน", GREEN, "#ffffff", 13),
    box("r4", 840, 372, 325, 74, "แถบกลางอ้วนขึ้น = คอขวด\nเข้า In Progress เร็วกว่าที่ปิดได้", RED, "#ffffff", 13),
    box("r5", 840, 460, 325, 74, "Plane CE ไม่มี CFD ในตัว\nLAB 9: นับใบต่อ state ณ สิ้นวัน\nจาก activity log แล้ววาดเอง", MUTED, GREYBG, 12),
    txt(40, 570, "หลังวัน 8 งานเข้าเท่าเดิม แต่ปิดได้ช้าลง → แถบ In Progress อ้วนขึ้น และ lead time ยาวขึ้น  (Little's Law: lead time ≈ WIP ÷ throughput)", 14, MUTED),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
