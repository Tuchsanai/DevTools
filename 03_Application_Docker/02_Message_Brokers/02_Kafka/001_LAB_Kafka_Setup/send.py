from kafka import KafkaProducer

# 1) ต่อไปหา broker ที่ localhost port 9092 (port ที่ map ไว้ตอน docker run)
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# 2) ส่งข้อความเข้า topic 'hello' — Kafka รับ-ส่งเป็น bytes เสมอ จึงต้อง .encode()
#    (ไม่ต้องสร้าง topic ก่อน — ส่งครั้งแรก broker จะสร้าง topic ให้อัตโนมัติ)
future = producer.send('hello', 'Hello Kafka!'.encode())

# 3) .get() รอจน broker ตอบรับ แล้วคืน "ใบเสร็จ" ว่าข้อความไปลงตรงไหนของ log
metadata = future.get(timeout=10)
print(f" [x] Sent 'Hello Kafka!'  ->  topic={metadata.topic} "
      f"partition={metadata.partition} offset={metadata.offset}")

# 4) ปิด connection ให้เรียบร้อย (producer จะส่งข้อมูลที่ค้างอยู่ออกให้หมดก่อน)
producer.close()
