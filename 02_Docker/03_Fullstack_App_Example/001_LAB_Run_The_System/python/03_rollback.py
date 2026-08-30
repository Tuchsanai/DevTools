import os

import psycopg

COUNT_SQL = "SELECT count(*) FROM tickets"
INSERT_SQL = """
INSERT INTO tickets (asset_id, title, detail, priority, status)
VALUES (%s, %s, %s, %s, 'NEW')
RETURNING id
"""

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    try:
        with conn.cursor() as cur:
            cur.execute(COUNT_SQL)
            before = cur.fetchone()[0]
            cur.execute("SELECT id FROM assets WHERE code = %s", ("A-004",))
            asset_id = cur.fetchone()[0]
            cur.execute(
                INSERT_SQL,
                (asset_id, "[LAB001-ROLLBACK]", "ข้อมูลชั่วคราว", "LOW"),
            )
            new_id = cur.fetchone()[0]
            cur.execute(COUNT_SQL)
            during = cur.fetchone()[0]
            print(f"before={before} during={during} new_id={new_id}")
        conn.rollback()
    except psycopg.Error:
        conn.rollback()
        raise

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute(COUNT_SQL)
        after = cur.fetchone()[0]
        print(f"after={after}")
