import os

import psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO assets (code, name, location) VALUES (%s, %s, %s)",
                ("A-001", "ข้อมูลซ้ำ", "LAB"),
            )
        conn.commit()
    except psycopg.errors.UniqueViolation as exc:
        conn.rollback()
        print(f"constraint={exc.diag.constraint_name} rollback=complete")
