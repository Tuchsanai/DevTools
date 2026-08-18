"""Analytics consumer — นับเฉพาะ ORDER_PLACED แบบ trend-level"""

# (1) ต่อ Kafka group analytics แบบ earliest และเปิด auto-commit
import json
import os
from pathlib import Path

import psycopg
from kafka import KafkaConsumer

DATABASE_URL = os.environ["DATABASE_URL"]
KAFKA_BOOTSTRAP = os.environ["KAFKA_BOOTSTRAP"]


def main() -> None:
    consumer = KafkaConsumer("cafe.events", bootstrap_servers=KAFKA_BOOTSTRAP, group_id="analytics", auto_offset_reset="earliest", enable_auto_commit=True)
    # (2) ตรวจ DB หลัง consumer ต่อสำเร็จ แล้วค่อยสร้าง readiness oracle
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("SELECT 1")
    Path("/tmp/analytics.ready").write_text("ready\n", encoding="utf-8")
    print("[analytics] พร้อมอ่าน cafe.events", flush=True)
    try:
        for message in consumer:
            event = json.loads(message.value.decode("utf-8"))
            print(f"[analytics] p{message.partition} offset={message.offset} {event['event']}", flush=True)
            # (3) ORDER_READY มีไว้สังเกต pipeline; UPDATE เฉพาะ ORDER_PLACED
            if event.get("event") == "ORDER_PLACED":
                with psycopg.connect(DATABASE_URL) as conn:
                    conn.execute("UPDATE sales_stats SET cups=cups+%s,revenue=revenue+%s WHERE menu_code=%s", (int(event["qty"]), event["price_total"], event["menu_code"]))
                    conn.commit()
    finally:
        Path("/tmp/analytics.ready").unlink(missing_ok=True)
        consumer.close()


if __name__ == "__main__":
    main()
