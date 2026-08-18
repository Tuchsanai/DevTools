"""บาริสต้า worker — RabbitMQ manual ack + DB idempotent"""

# (1) Kafka ถูก import เฉพาะเมื่อเปิด event ตาม feature matrix
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import pika
import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ["DATABASE_URL"]
RABBIT_URL = os.environ["RABBIT_URL"]
BREW_SECONDS = int(os.environ.get("BREW_SECONDS", "3"))
EVENTS_ENABLED = os.environ.get("EVENTS_ENABLED", "0") == "1"
KAFKA_BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092")

if EVENTS_ENABLED:
    from kafka import KafkaProducer


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def make_producer():
    if not EVENTS_ENABLED:
        return None
    return KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP, key_serializer=lambda value: value.encode("utf-8"), value_serializer=lambda value: json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


# (2) callback เดินสถานะไปข้างหน้าและ ack หลัง READY เท่านั้น
def main() -> None:
    rabbit = pika.BlockingConnection(pika.URLParameters(RABBIT_URL))
    channel = rabbit.channel()
    channel.queue_declare(queue="order_queue", durable=True)
    channel.basic_qos(prefetch_count=1)
    producer = make_producer()

    def brew(ch, method, properties, body):
        message = json.loads(body.decode("utf-8"))
        order_id = int(message["order_id"])
        try:
            with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
                order = conn.execute("SELECT o.id,o.status,o.menu_code,o.qty,(m.price*o.qty)::numeric(12,2) AS price_total FROM orders o JOIN menus m ON m.code=o.menu_code WHERE o.id=%s", (order_id,)).fetchone()
                if order is None or order["status"] == "READY":
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print(f"[worker] #{order_id} พร้อมอยู่แล้ว/ไม่พบ — ack โดยไม่ชงซ้ำ", flush=True)
                    return
                conn.execute("UPDATE orders SET status='BREWING' WHERE id=%s AND status='QUEUED'", (order_id,))
                conn.commit()
            print(f"[worker] กำลังชง #{order_id} จำนวน {message['qty']} แก้ว", flush=True)
            time.sleep(BREW_SECONDS * int(message["qty"]))
            with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
                ready = conn.execute("UPDATE orders SET status='READY',ready_at=CURRENT_TIMESTAMP WHERE id=%s AND status<>'READY' RETURNING ready_at", (order_id,)).fetchone()
                conn.commit()
            if ready is not None and producer is not None:
                event = {"event": "ORDER_READY", "order_id": order_id, "menu_code": order["menu_code"], "qty": order["qty"], "price_total": float(order["price_total"]), "ts": utc_now()}
                producer.send("cafe.events", key=order["menu_code"], value=event).get(timeout=10)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[worker] #{order_id} READY — ack แล้ว", flush=True)
        except Exception:
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
            raise

    # (3) ready file เกิดหลังต่อ DB/Rabbit/Kafka และประกาศ consumer ครบ
    with psycopg.connect(DATABASE_URL) as conn:
        conn.execute("SELECT 1")
    channel.basic_consume(queue="order_queue", on_message_callback=brew, auto_ack=False)
    Path("/tmp/worker.ready").write_text("ready\n", encoding="utf-8")
    print("[worker] พร้อมรับ order_queue", flush=True)
    try:
        channel.start_consuming()
    finally:
        Path("/tmp/worker.ready").unlink(missing_ok=True)
        if producer is not None:
            producer.close(timeout=5)
        rabbit.close()


if __name__ == "__main__":
    main()
