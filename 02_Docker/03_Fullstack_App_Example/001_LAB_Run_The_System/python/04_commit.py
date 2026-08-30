import os

import psycopg

TITLE = "[LAB001-COMMIT]"

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM assets WHERE code = %s", ("A-004",))
        asset_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO tickets (asset_id, title, detail, priority, status) "
            "VALUES (%s, %s, %s, %s, 'NEW') RETURNING id",
            (asset_id, TITLE, "ข้อมูลสำหรับสาธิต commit", "LOW"),
        )
        committed_id = cur.fetchone()[0]
    conn.commit()
    print(f"committed_id={committed_id}")
