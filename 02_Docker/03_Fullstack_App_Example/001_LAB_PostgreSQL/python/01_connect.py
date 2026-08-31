import os
import sys
import time

import psycopg

def connect_with_retry():
    for attempt in range(1, 31):
        try:
            return psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=2)
        except (KeyError, psycopg.OperationalError):
            if attempt == 30:
                raise
            time.sleep(1)
    raise RuntimeError("unreachable")

try:
    with connect_with_retry() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            print(f"database={cur.fetchone()[0]}")
except (KeyError, psycopg.Error) as exc:
    print(f"เชื่อมต่อ PostgreSQL ไม่สำเร็จ: {exc}", file=sys.stderr)
    raise SystemExit(1) from exc
