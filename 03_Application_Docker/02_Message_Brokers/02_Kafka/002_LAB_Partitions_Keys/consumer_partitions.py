from kafka import KafkaConsumer

# 1) อ่าน topic 'orders' ตั้งแต่ข้อความแรกสุด (ไม่ใส่ group_id -> รันซ้ำกี่รอบก็ได้ครบเหมือนเดิม)
#    consumer_timeout_ms=5000 : ถ้าไม่มีข้อความใหม่มา 5 วินาที ให้จบเอง ไม่ต้องกด Ctrl+C
consumer = KafkaConsumer('orders',
                         bootstrap_servers='localhost:9092',
                         auto_offset_reset='earliest',
                         consumer_timeout_ms=5000)

count = 0
try:
    # 2) พิมพ์ "ที่อยู่" ของทุกข้อความ : partition / offset / key / เนื้อข้อความ
    #    (key ของข้อความที่ส่งแบบไม่ใส่ key จะเป็น None)
    for message in consumer:
        key = message.key.decode() if message.key else None
        print(f" [x] partition={message.partition} offset={message.offset} "
              f"key={key}  value={message.value.decode()}")
        count += 1
finally:
    consumer.close()

print(f" [*] Done - read {count} messages")
