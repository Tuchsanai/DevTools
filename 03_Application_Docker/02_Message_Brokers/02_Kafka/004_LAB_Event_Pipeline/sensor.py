import json
import random
import sys
import time
from kafka import KafkaProducer

# ล็อกผลการสุ่มให้ตรงกับเอกสารแล็บ — อยากได้ค่าสุ่มจริง ให้ลบบรรทัดนี้ทิ้ง
random.seed(2569)

# 1) ต่อ broker
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# 2) จำนวนรอบที่จะวัด — ใส่เป็น argument ได้ เช่น `python sensor.py 15` (ไม่ใส่ = 15)
rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 15

# 3) จำลอง sensor วัดอุณหภูมิ 3 ตัว ส่งค่าเป็น JSON เข้า topic 'sensor.readings'
#    ใช้ key = ชื่อ sensor → ค่าของ sensor ตัวเดิมเรียงลำดับกันเสมอ (บทเรียน LAB 2)
sensors = ['sensor-1', 'sensor-2', 'sensor-3']
for i in range(rounds):
    sensor = sensors[i % 3]
    reading = {
        'sensor': sensor,
        'temp': round(random.uniform(20.0, 45.0), 1),   # อุณหภูมิ 20.0–45.0 °C
        'round': i // 3 + 1,
    }
    # 4) dict → ข้อความ JSON → bytes แล้วค่อยส่ง (ผู้รับจะแปลงกลับด้วย json.loads)
    producer.send('sensor.readings',
                  key=sensor.encode(),
                  value=json.dumps(reading).encode()).get(timeout=10)
    print(f" [x] Sent {reading}")
    time.sleep(0.5)   # เว้นจังหวะเหมือน sensor วัดค่าเป็นระยะ

producer.close()
