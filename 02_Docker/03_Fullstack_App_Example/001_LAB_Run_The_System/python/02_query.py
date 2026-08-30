import json
import os
import time

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

TABLES = ("assets", "tickets", "loans", "parts", "stock_moves")

def connect_with_retry():
    for attempt in range(1, 31):
        try:
            return psycopg.connect(
                os.environ["DATABASE_URL"], connect_timeout=2, row_factory=dict_row
            )
        except psycopg.OperationalError:
            if attempt == 30:
                raise
            time.sleep(1)
    raise RuntimeError("unreachable")

def inspect_table(cur, table):
    if table not in TABLES:
        raise ValueError(f"ไม่อนุญาตให้สำรวจตาราง: {table}")
    cur.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
        ("public", table),
    )
    columns = cur.fetchall()
    count_query = sql.SQL("SELECT count(*) AS n FROM {}").format(sql.Identifier(table))
    cur.execute(count_query)
    count = cur.fetchone()["n"]
    sample_query = sql.SQL("SELECT * FROM {} ORDER BY id LIMIT %s").format(
        sql.Identifier(table)
    )
    cur.execute(sample_query, (3,))
    samples = cur.fetchall()
    print(f"\n=== {table} ({count} rows) ===")
    print("columns: " + " | ".join(
        f"{column['column_name']}:{column['data_type']}" for column in columns
    ))
    for index, row in enumerate(samples, start=1):
        print(f"sample[{index}]: " + json.dumps(
            dict(row), ensure_ascii=False, default=str
        ))

with connect_with_retry() as conn:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        tables = tuple(row["table_name"] for row in cur.fetchall())
        print("tables=" + ",".join(tables))
        if set(tables) != set(TABLES):
            raise RuntimeError("ชุดตารางไม่ตรงกับแบบจำลองข้อมูล LAB 001")
        for table in TABLES:
            inspect_table(cur, table)
