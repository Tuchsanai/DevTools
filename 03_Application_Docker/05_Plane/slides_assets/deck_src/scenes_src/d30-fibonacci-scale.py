#!/usr/bin/env python3
"""d30-fibonacci-scale : Modified Fibonacci scale as cards growing in size (Plane deck diagram)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

HERE = os.path.dirname(os.path.abspath(__file__))
NAME = "d30-fibonacci-scale"

# ---------------------------------------------------------------- cards
vals = [1, 2, 3, 5, 8, 13, 20, 40, 100]
widths = [50, 58, 66, 78, 92, 108, 128, 160, 205]          # grow with size
gaps = [8, 10, 14, 18, 24, 30, 40, 55]                      # gap widens too
heights = [62, 66, 72, 80, 92, 108, 128, 152, 180]   # convex growth -> curve bends up
fsz = [18, 19, 20, 21, 22, 24, 26, 28, 30]
cols = [(GREEN, GREENBG)] * 3 + [(BLUE, BLUEBG)] * 2 + [(ORANGE, ORANGEBG)] * 2 + [(RED, REDBG)] * 2
BOTTOM = 355
X0 = 35

els = [title("สเกล Modified Fibonacci : ยิ่งงานใหญ่ ยิ่งไม่แน่นอน ตัวเลขจึงห่างกันมากขึ้น")]

xs, tops, centers = [], [], []
x = X0
for i, v in enumerate(vals):
    w, h = widths[i], heights[i]
    top = BOTTOM - h
    c, bg = cols[i]
    els.append(box(f"f{i}", x, top, w, h, str(v), c, bg, fsz[i]))
    xs.append(x); tops.append(top); centers.append(x + w / 2)
    x += w + (gaps[i] if i < len(gaps) else 0)
X_END = x  # right edge of the last card

# numeric differences shown under each gap (1 1 2 3 5 7 20 60)
for i in range(len(vals) - 1):
    d = vals[i + 1] - vals[i]
    gx = (xs[i] + widths[i] + xs[i + 1]) / 2
    label = f"+{d}"
    els.append(txt(gx - len(label) * 4, BOTTOM + 6, label, 13, MUTED))

# ---------------------------------------------------------------- uncertainty curve (free-form curved arrow)
cx0, cy0 = centers[0], tops[0] - 22
pts = [[centers[i] - cx0, (tops[i] - 22) - cy0] for i in range(len(vals))]
pts.append([X_END - 10 - cx0, (tops[-1] - 48) - cy0])
els.append({"type": "arrow", "id": "curve", "x": cx0, "y": cy0,
            "width": pts[-1][0], "height": abs(pts[-1][1]), "points": pts,
            "roundness": {"type": 2}, "strokeColor": ORANGE, "strokeWidth": 3, "roughness": 0,
            "endArrowhead": "arrow"})
els.append(txt(60, 148, "ความไม่แน่นอนโตตามขนาด → ช่องห่างจึงกว้างขึ้น", 19, ORANGE))
els.append(txt(60, 180, "1 กับ 2 ต่างกันชัด แต่ 40 กับ 41 แยกไม่ออก → ใช้เลขห่าง ๆ ก็พอ", 15, MUTED))

# ---------------------------------------------------------------- brackets under the cards
BY = BOTTOM + 34
g_x0, g_x1 = xs[0], xs[4] + widths[4]          # 1 .. 8
r_x0, r_x1 = xs[5], X_END                       # 13 .. 100
els.append(line(g_x0, BY, [[0, -8], [0, 0], [g_x1 - g_x0, 0], [g_x1 - g_x0, -8]], GREEN, 2))
els.append(line(r_x0, BY, [[0, -8], [0, 0], [r_x1 - r_x0, 0], [r_x1 - r_x0, -8]], RED, 2))
els.append(txt((g_x0 + g_x1) / 2 - 95, BY + 8, "ขนาดที่พอดีกับ 1 sprint", 16, GREEN))
els.append(txt((r_x0 + r_x1) / 2 - 130, BY + 8, "≥ 13 → แตกงานก่อนเข้า sprint", 17, RED))

# ---------------------------------------------------------------- alternatives + note
els.append(zone(30, 445, 1150, 160, MUTED, GREYBG))
els.append(txt(50, 455, "สเกลทางเลือก (ใช้แบบเดียวทั้งทีมแล้วใช้ให้สม่ำเสมอ)", 17, MUTED))
els.append(box("alt1", 50, 488, 340, 70, "T-shirt sizes (categories)\nXS · S · M · L · XL", TEAL, TEALBG, 16))
els.append(box("alt2", 415, 488, 320, 70, "กำลังของสอง (powers of 2)\n1 · 2 · 4 · 8 · 16", PURPLE, PURPLEBG, 16))
els.append(box("note", 765, 488, 395, 70, "เถียงเรื่อง 13 กับ 14 ไม่มีประโยชน์\nเลือกเลขที่ใกล้ที่สุดในสเกลแล้วไปต่อ", ORANGE, YELBG, 15))
els.append(txt(50, 570, "ใน Plane : Project settings › Estimates — Points (Fibonacci · Linear · Squares · Custom) หรือ Categories (T-shirt)", 14, MUTED))

with open(os.path.join(HERE, NAME + ".json"), "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print(f"wrote {NAME}.json with {len(els)} elements; cards end at x={X_END}")
