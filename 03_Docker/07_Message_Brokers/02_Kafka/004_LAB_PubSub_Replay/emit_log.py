import sys
from kafka import KafkaProducer

# 1) ต่อ broker
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# 2) เนื้อข้อความมาจาก argument เช่น `python emit_log.py "info: user login"`
#    (ไม่ใส่ = ข้อความตัวอย่าง)
message = ' '.join(sys.argv[1:]) or 'info: Hello logs!'

# 3) ส่งเข้า topic 'logs' — ผู้ส่งไม่รู้และไม่สนใจว่า "ใครสมัครอ่านอยู่บ้าง"
metadata = producer.send('logs', message.encode()).get(timeout=10)
print(f" [x] Sent '{message}'  ->  partition={metadata.partition} offset={metadata.offset}")

producer.close()
