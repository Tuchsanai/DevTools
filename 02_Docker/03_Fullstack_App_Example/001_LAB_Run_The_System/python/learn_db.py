#!/usr/bin/env python3
"""สนามทดลอง PostgreSQL ของ LAB 001 — ใช้ psycopg 3 โดยไม่ใช้ ORM."""

from __future__ import annotations

import argparse
import os
import sys
import time
from collections.abc import Iterable
from typing import Any

import psycopg
from psycopg.rows import dict_row


EXPECTED_TABLES = ("assets", "tickets", "loans", "parts", "stock_moves")
MARKER_TITLE = "[LAB001-PERSISTENCE]"

SAMPLE_QUERIES = {
    "assets": "SELECT id, code, name, location FROM assets ORDER BY id LIMIT 2",
    "tickets": (
        "SELECT id, asset_id, title, priority, status, assignee "
        "FROM tickets ORDER BY id LIMIT 2"
    ),
    "loans": (
        "SELECT id, asset_id, borrower, borrowed_at, returned_at "
        "FROM loans ORDER BY id LIMIT 2"
    ),
    "parts": (
        "SELECT id, sku, name, qty_on_hand, reorder_point, "
        "(qty_on_hand < reorder_point) AS below_reorder "
        "FROM parts ORDER BY id LIMIT 2"
    ),
    "stock_moves": (
        "SELECT id, part_id, ticket_id, delta, reason "
        "FROM stock_moves ORDER BY id LIMIT 2"
    ),
}

REQUEST_MAP = (
    ("GET /health", "SELECT 1", "ตรวจว่า PostgreSQL ตอบสนอง"),
    (
        "GET /api/assets",
        "SELECT assets + EXISTS tickets + EXISTS loans",
        "assets, tickets, loans",
    ),
    ("GET /api/tickets", "SELECT tickets (+ WHERE status/assignee)", "tickets"),
    (
        "POST /api/tickets",
        "SELECT assets; INSERT tickets; COMMIT",
        "assets, tickets",
    ),
    (
        "PATCH /api/tickets/{ticket_id}/status",
        "SELECT tickets; UPDATE tickets; COMMIT",
        "tickets",
    ),
    (
        "POST /api/tickets/{ticket_id}/close",
        "SELECT tickets/parts FOR UPDATE; UPDATE parts; INSERT stock_moves; "
        "UPDATE tickets; COMMIT ทั้งหมดพร้อมกัน",
        "tickets, parts, stock_moves",
    ),
    ("GET /api/loans", "SELECT loans JOIN assets", "loans, assets"),
    (
        "POST /api/loans",
        "SELECT assets/loans/tickets; INSERT loans; COMMIT",
        "assets, loans, tickets",
    ),
    (
        "POST /api/loans/{loan_id}/return",
        "UPDATE loans SET returned_at = now(); COMMIT",
        "loans",
    ),
    ("GET /api/parts", "SELECT parts + คำนวณ below_reorder", "parts"),
    (
        "GET /api/parts/{part_id}/moves",
        "SELECT parts; SELECT stock_moves",
        "parts, stock_moves",
    ),
    (
        "POST /api/parts/{part_id}/move",
        "SELECT parts FOR UPDATE; UPDATE parts; INSERT stock_moves; COMMIT",
        "parts, stock_moves",
    ),
    (
        "GET /api/dashboard",
        "SELECT/GROUP BY tickets; COUNT loans; SELECT parts ต่ำกว่าจุดสั่งซื้อ",
        "tickets, loans, parts",
    ),
)


def database_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit(
            "ไม่พบ DATABASE_URL — ดูคำสั่งหา DB_IP และ export DATABASE_URL ใน readme.md"
        )
    return url


def connect() -> psycopg.Connection[dict[str, Any]]:
    for attempt in range(1, 31):
        try:
            return psycopg.connect(
                database_url(), row_factory=dict_row, connect_timeout=2
            )
        except psycopg.OperationalError:
            if attempt == 30:
                raise
            time.sleep(1)
    raise RuntimeError("unreachable")


def print_rows(rows: Iterable[dict[str, Any]]) -> None:
    rows = list(rows)
    if not rows:
        print("  (ไม่พบข้อมูล)")
        return
    for row in rows:
        print("  " + " | ".join(f"{key}={value}" for key, value in row.items()))


def overview() -> None:
    with connect() as conn:
        db_name = conn.execute("SELECT current_database() AS name").fetchone()["name"]
        tables = tuple(
            row["tablename"]
            for row in conn.execute(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' ORDER BY tablename"
            ).fetchall()
        )
        if set(tables) != set(EXPECTED_TABLES):
            raise SystemExit(f"ตารางไม่ตรงกับ LAB 001: พบ {', '.join(tables) or '(ไม่มี)'}")

        print(f"ฐานข้อมูล: {db_name}")
        print("ตาราง: " + ", ".join(tables))
        print("\nจำนวนแถวและตัวอย่างข้อมูล")
        for table in EXPECTED_TABLES:
            count = conn.execute(f"SELECT count(*) AS n FROM {table}").fetchone()["n"]
            print(f"\n[{table}] {count} แถว")
            print(f"SQL: {SAMPLE_QUERIES[table]}")
            print_rows(conn.execute(SAMPLE_QUERIES[table]).fetchall())


def request_map() -> None:
    print("Browser ไม่เชื่อม PostgreSQL โดยตรง")
    print("Browser -> Next.js web -> FastAPI api -> PostgreSQL skillspace\n")
    for route, sql, tables in REQUEST_MAP:
        print(f"{route}\n  SQL: {sql}\n  ตาราง: {tables}\n")


def demo_rollback() -> None:
    """สาธิต POST /api/tickets แต่ rollback เพื่อรักษา seed เดิม."""
    with connect() as conn:
        before = conn.execute("SELECT count(*) AS n FROM tickets").fetchone()["n"]
        asset_id = conn.execute(
            "SELECT id FROM assets WHERE code = %s", ("A-004",)
        ).fetchone()["id"]
        print(f"ก่อนเริ่ม transaction: tickets={before}")
        print("SQL: INSERT INTO tickets (...) VALUES (...) RETURNING id")
        row = conn.execute(
            """
            INSERT INTO tickets (asset_id, title, detail, priority, status)
            VALUES (%s, %s, %s, %s, 'NEW')
            RETURNING id, asset_id, title, priority, status
            """,
            (asset_id, "[LAB001-ROLLBACK-DEMO]", "ข้อมูลสาธิตชั่วคราว", "LOW"),
        ).fetchone()
        print_rows([row])
        during = conn.execute("SELECT count(*) AS n FROM tickets").fetchone()["n"]
        print(f"ใน transaction ก่อน rollback: tickets={during}")
        conn.rollback()

    with connect() as conn:
        after = conn.execute("SELECT count(*) AS n FROM tickets").fetchone()["n"]
    print(f"หลัง rollback และเปิด connection ใหม่: tickets={after}")
    if before != after:
        raise SystemExit("rollback ไม่คืนจำนวนแถวเป็นค่าเดิม")


def persistence(action: str) -> None:
    with connect() as conn:
        existing = conn.execute(
            "SELECT id, title, status FROM tickets WHERE title = %s ORDER BY id LIMIT 1",
            (MARKER_TITLE,),
        ).fetchone()

        if action == "add":
            if existing is None:
                asset_id = conn.execute(
                    "SELECT id FROM assets WHERE code = %s", ("A-004",)
                ).fetchone()["id"]
                existing = conn.execute(
                    """
                    INSERT INTO tickets (asset_id, title, detail, priority, status)
                    VALUES (%s, %s, %s, %s, 'NEW')
                    RETURNING id, title, status
                    """,
                    (asset_id, MARKER_TITLE, "แถวสาธิตสำหรับพิสูจน์ Named Volume", "LOW"),
                ).fetchone()
                conn.commit()
                print("เพิ่ม marker และ COMMIT แล้ว")
            else:
                print("marker มีอยู่แล้ว จึงไม่เพิ่มซ้ำ")
            print_rows([existing])
            return

        if action == "check":
            print("พบ marker" if existing else "ไม่พบ marker")
            if existing:
                print_rows([existing])
            return

        deleted = conn.execute(
            "DELETE FROM tickets WHERE title = %s RETURNING id", (MARKER_TITLE,)
        ).fetchall()
        conn.commit()
        print(f"ลบ marker {len(deleted)} แถวและ COMMIT แล้ว")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("overview", help="ดู 1 database, 5 tables, counts และ sample rows")
    sub.add_parser("request-map", help="ดูความสัมพันธ์ route -> SQL -> table ของ LAB 002")
    sub.add_parser("demo-rollback", help="สาธิต INSERT + ROLLBACK โดยไม่เปลี่ยน seed")
    persist = sub.add_parser("persistence", help="เพิ่ม/หา/ลบ marker สำหรับทดลอง Volume")
    persist.add_argument("action", choices=("add", "check", "remove"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    try:
        if args.command == "overview":
            overview()
        elif args.command == "request-map":
            request_map()
        elif args.command == "demo-rollback":
            demo_rollback()
        else:
            persistence(args.action)
    except psycopg.Error as exc:
        print(f"เชื่อมต่อหรือสั่ง PostgreSQL ไม่สำเร็จ: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
