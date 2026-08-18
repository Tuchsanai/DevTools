"""Audit replay — อ่านเหตุการณ์เก่าหนึ่งรอบและไม่แตะฐานข้อมูล"""

# (1) group audit ไม่ commit และเริ่ม earliest เมื่อไม่มี offset
import json
import os
from collections import Counter

from kafka import KafkaConsumer

consumer = KafkaConsumer("cafe.events", bootstrap_servers=os.environ["KAFKA_BOOTSTRAP"], group_id="audit", auto_offset_reset="earliest", enable_auto_commit=False, consumer_timeout_ms=5000)

# (2) พิมพ์ timeline ที่อ่านง่าย พร้อม partition และ offset
counts: Counter[str] = Counter()
print("☕ ประวัติเหตุการณ์ ChongJai Café", flush=True)
for record in consumer:
    event = json.loads(record.value.decode("utf-8"))
    counts[event.get("event", "UNKNOWN")] += 1
    print(f"  p{record.partition} · offset {record.offset:>3} · {event.get('ts')} · {event.get('event')} · order #{event.get('order_id')} · {event.get('menu_code')} x{event.get('qty')}", flush=True)

# (3) จบเองหลัง timeout โดยไม่มี SQL หรือ DB connection
consumer.close()
print(f"สรุป ORDER_PLACED={counts['ORDER_PLACED']} · ORDER_READY={counts['ORDER_READY']} · รวม={sum(counts.values())}", flush=True)
