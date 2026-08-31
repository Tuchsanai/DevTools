"""pytest -q test_metrics.py — ทดสอบสูตรทั้ง 6 ด้วย fixture เล็กที่รู้คำตอบ (ก่อนต่อข้อมูลจริงจาก Plane)"""
import datetime as dt
import json
import pathlib

import metrics as m

FX = json.loads((pathlib.Path(__file__).parent / "fixtures" / "snapshot_small.json").read_text(encoding="utf-8"))
ITEMS, STATES, POINTS, CYCLES, ACTS, RELS = FX["items"], FX["states"], FX["points"], FX["cycles"], FX["activities"], FX["relations"]
BY_ID = {i["id"]: i for i in ITEMS}
TODAY = dt.date(2026, 8, 31)


def test_burndown_items_shape_and_values():
    b = m.burndown([BY_ID[i] for i in CYCLES[1]["issue_ids"]], "2026-08-25", "2026-08-31", today=TODAY)
    assert b["dates"][0] == "2026-08-25" and len(b["dates"]) == 7
    assert b["total"] == 4
    assert b["actual"] == [4, 4, 3, 3, 2, 2, 2]          # 2 ใบเสร็จวันที่ 27 และ 29
    assert b["ideal"][0] == 4 and b["ideal"][-1] == 0


def test_burndown_future_days_are_none():
    b = m.burndown(ITEMS, "2026-08-30", "2026-09-03", today=TODAY)
    assert b["actual"][2:] == [None, None, None]


def test_burndown_points_uses_estimate():
    b = m.burndown([BY_ID[i] for i in CYCLES[1]["issue_ids"]], "2026-08-25", "2026-08-31", points=POINTS, today=TODAY)
    assert b["unit"] == "points" and b["total"] == 13   # 5+3+3+2
    assert b["actual"][-1] == 5                          # เหลืองาน 3+2 ที่ยังไม่เสร็จ


def test_velocity_completed_cycles_only():
    v = m.velocity(CYCLES, BY_ID, points=POINTS)
    assert [r["cycle"] for r in v["rows"]] == ["Sprint 0"]
    assert v["rows"][0]["committed"] == 8 and v["rows"][0]["done"] == 8
    assert v["average"] == 8


def test_cfd_sum_equals_items_existing_that_day():
    c = m.cfd(ITEMS, STATES, ACTS, days=7, today=TODAY)
    for i, d in enumerate(c["dates"]):
        total = sum(c["series"][g][i] for g in c["series"])
        existing = sum(1 for it in ITEMS if it["created_at"][:10] <= d)
        assert total == existing


def test_cfd_history_replays_state_changes():
    c = m.cfd(ITEMS, STATES, ACTS, days=7, today=TODAY)
    # A-1 เข้า started วันที่ 26 และ completed วันที่ 27
    d26, d27 = c["dates"].index("2026-08-26"), c["dates"].index("2026-08-27")
    assert c["series"]["started"][d26] >= 1
    assert c["series"]["completed"][d27] >= 1


def test_lead_cycle_hours():
    lc = m.lead_cycle(ITEMS, STATES, ACTS)
    row = next(r for r in lc["rows"] if r["key"] == 1)
    assert row["lead_h"] == 48.0 and row["cycle_h"] == 24.0
    assert lc["lead_p50"] is not None and lc["cycle_p85"] is not None


def test_wip_policy_violation():
    w = m.wip(ITEMS, STATES, {"In Progress": 1, "In Review": 2})
    ip = next(r for r in w["rows"] if r["state"] == "In Progress")
    assert ip["wip"] == 2 and ip["ok"] is False
    assert w["violations"] == ["In Progress"]


def test_wip_within_policy():
    w = m.wip(ITEMS, STATES, {"In Progress": 3, "In Review": 2})
    assert w["violations"] == [] and w["total_wip"] == 2


def test_blockers_only_open_pairs():
    b = m.blockers(BY_ID, RELS, STATES)
    assert b == [{"blocked": 5, "by": 4, "by_state": "In Progress"}]


def test_aging_sorted_desc():
    a = m.aging(ITEMS, STATES, ACTS, now=dt.datetime(2026, 8, 31, 12, tzinfo=dt.timezone.utc))
    assert [r["key"] for r in a] == [4, 6]
    assert a[0]["age_d"] > a[1]["age_d"]


def test_ideal_line_formula():
    b = m.burndown(ITEMS[:3], "2026-09-01", "2026-09-10", today=TODAY)
    n = 10
    for i, v in enumerate(b["ideal"]):
        assert abs(v - 3 * (1 - i / (n - 1))) < 0.01
