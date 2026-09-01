#!/usr/bin/env python3
"""d33 — Burndown vs Burn-up side by side (Excalidraw scene, uses diagrams.py helpers)."""
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from diagrams import *

NAME = "d33-burndown-burnup"
GRID = "#dee2e6"

# plot geometry (shared by both charts): 10 days x 50 pt
PY, PW, PH = 138, 430, 300
DX, DY, YMAX = 43, 6, 50           # px per day, px per pt


def X(d):
    return d * DX


def Y(v):
    return (YMAX - v) * DY


def axes(px, y_title, pid):
    """white plot box + axes + ticks + labels + light grid."""
    els = [box(pid, px, PY, PW, PH, "", "#adb5bd", "#ffffff")]
    for v in range(10, YMAX, 10):
        els.append(line(px, PY + Y(v), [[0, 0], [PW, 0]], GRID, 1))
    els.append(line(px, PY, [[0, 0], [0, PH]], INK, 2))          # y axis
    els.append(line(px, PY + PH, [[0, 0], [PW, 0]], INK, 2))     # x axis
    for d in range(11):
        els.append(line(px + X(d), PY + PH, [[0, 0], [0, 5]], INK, 1))
        els.append(txt(px + X(d) - (8 if d >= 10 else 4), PY + PH + 8, str(d), 13, MUTED))
    for v in range(0, YMAX + 1, 10):
        els.append(txt(px - (26 if v >= 10 else 18), PY + Y(v) - 8, str(v), 13, MUTED))
    els.append(txt(px + PW // 2 - 30, PY + PH + 28, "วัน (day)", 14, MUTED))
    els.append(txt(px - 62, PY - 28, y_title, 14, MUTED))
    return els


# ---- data (same sprint in both charts): 40 pt planned, +8 pt scope added on day 5
remaining = [40, 40, 40, 34, 30, 36, 29, 21, 13, 6, 0]
scope = [40] * 5 + [48] * 6
done = [s - r for s, r in zip(scope, remaining)]     # 0 0 0 6 10 12 19 27 35 42 48

# ---- LEFT : burndown ------------------------------------------------------
L = 110
stairs = [[X(0), Y(remaining[0])]]
for d in range(1, 11):
    stairs.append([X(d), Y(remaining[d - 1])])
    stairs.append([X(d), Y(remaining[d])])

els = [title("Burndown vs Burn-up : ดูงานคงเหลือ หรือดูงานเสร็จสะสมพร้อม scope")]
els += [zone(30, 72, 560, 495, RED, "#fff5f5"),
        txt(50, 82, "Burndown — งานคงเหลือ (pt) ต่อวัน", 20, RED)]
els += axes(L, "งานคงเหลือ (pt)", "plotL")
els += [
    line(L, PY, [[X(0), Y(40)], [X(10), Y(0)]], MUTED, 2, dashed=True),   # ideal
    line(L, PY, stairs, RED, 3),                                          # actual staircase
    # annotations
    txt(L + 6, PY + Y(40) - 24, "ราบ = งานติดค้าง (ไม่มีใบไหนปิด)", 14, RED),
    txt(L + X(5) - 30, PY + Y(36) - 26, "กระโดดขึ้น = scope เพิ่ม (+8 pt)", 14, RED),
    # legend (bottom-left, empty area)
    line(L + 12, PY + Y(9), [[0, 0], [30, 0]], MUTED, 2, dashed=True),
    txt(L + 50, PY + Y(9) - 9, "ideal — งานคงเหลือตามแผน", 13, MUTED),
    line(L + 12, PY + Y(5), [[0, 0], [30, 0]], RED, 3),
    txt(L + 50, PY + Y(5) - 9, "actual — งานคงเหลือจริง", 13, RED),
    txt(50, 500, "เหนือเส้น ideal = ช้ากว่าแผน · ใต้เส้น = เร็วกว่าแผน\nแต่บอกไม่ได้ว่า \"ช้า\" เพราะทีมทำช้า หรือเพราะ scope เพิ่ม", 14, INK),
]

# ---- RIGHT : burn-up --------------------------------------------------------
R = 700
scope_pts = [[X(0), Y(40)], [X(5), Y(40)], [X(5), Y(48)], [X(10), Y(48)]]
done_pts = [[X(d), Y(done[d])] for d in range(11)]

els += [zone(620, 72, 560, 495, GREEN, GREENBG),
        txt(640, 82, "Burn-up — Done สะสม + Scope รวม (pt)", 20, GREEN)]
els += axes(R, "งาน (pt)", "plotR")
els += [
    line(R, PY, scope_pts, PURPLE, 3),      # scope line (steps up on day 5)
    line(R, PY, done_pts, GREEN, 3),        # cumulative done
    txt(R + 8, PY + Y(40) + 6, "Scope รวม = 40 pt", 14, PURPLE),                 # just under the 40-pt level
    # step label sits inside the 40–48 band, left of the day-5 step (keeps clear of the day-7 marker)
    txt(R + X(5) - 138, PY + Y(48) + 12, "วันที่ 5: scope +8 pt", 14, PURPLE),
    txt(R + X(6) + 30, PY + Y(19) + 8, "Done สะสม", 14, GREEN),
    # gap marker at day 7
    line(R + X(7), PY + Y(48), [[0, 0], [0, Y(27) - Y(48)]], MUTED, 2, dashed=True),
    txt(R + X(7) + 6, PY + Y(48) + 34, "งานที่เหลือ", 12, MUTED),
    txt(R + 12, PY + Y(34) + 2, "เห็น scope creep แยกจากความคืบหน้า:\nเส้น Scope ขยับขึ้น ≠ เส้น Done ช้าลง", 14, INK),
    # legend (bottom-right, empty area)
    line(R + X(7) + 15, PY + Y(9), [[0, 0], [30, 0]], PURPLE, 3),
    txt(R + X(7) + 53, PY + Y(9) - 9, "Scope รวม", 13, PURPLE),
    line(R + X(7) + 15, PY + Y(5), [[0, 0], [30, 0]], GREEN, 3),
    txt(R + X(7) + 53, PY + Y(5) - 9, "Done สะสม", 13, GREEN),
    txt(640, 500, "Burndown ซ่อน scope ที่เพิ่ม (ดูเหมือนทีมช้า)\nBurn-up แยก 2 เส้น → รู้ทันทีว่า scope creep หรือทีมช้า", 14, INK),
]

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), NAME + ".json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(els, f, ensure_ascii=False)
print("wrote", out, len(els), "elements")
