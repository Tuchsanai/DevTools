import os

import psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tickets WHERE title = %s", ("[LAB001-COMMIT]",))
        deleted = cur.rowcount
    conn.commit()
    print(f"cleanup_deleted={deleted}")
