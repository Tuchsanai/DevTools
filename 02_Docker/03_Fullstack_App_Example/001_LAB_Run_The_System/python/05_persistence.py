import argparse
import os

import psycopg

TITLE = "[LAB001-PERSISTENCE]"

parser = argparse.ArgumentParser()
parser.add_argument("action", choices=("add", "check", "remove"))
action = parser.parse_args().action

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        if action == "add":
            cur.execute("SELECT id FROM assets WHERE code = %s", ("A-004",))
            asset_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO tickets (asset_id, title, detail, priority, status) "
                "VALUES (%s, %s, %s, %s, 'NEW')",
                (asset_id, TITLE, "ข้อมูลพิสูจน์ persistence", "LOW"),
            )
            conn.commit()
            print("marker=committed")
        elif action == "check":
            cur.execute("SELECT count(*) FROM tickets WHERE title = %s", (TITLE,))
            print(f"marker_count={cur.fetchone()[0]}")
        else:
            cur.execute("DELETE FROM tickets WHERE title = %s", (TITLE,))
            deleted = cur.rowcount
            conn.commit()
            print(f"marker_deleted={deleted}")
