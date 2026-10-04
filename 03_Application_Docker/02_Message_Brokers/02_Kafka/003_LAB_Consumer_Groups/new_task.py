import sys
from kafka import KafkaProducer

# 1) ต่อ broker
producer = KafkaProducer(bootstrap_servers='localhost:9092')

# 2) จำนวนงานที่จะส่ง — ใส่เป็น argument ได้ เช่น `python new_task.py 12` (ไม่ใส่ = 12)
count = int(sys.argv[1]) if len(sys.argv) > 1 else 12

# 3) ส่งงานเข้า topic 'tasks' โดยใช้ key = ชื่อสาขา (วนครบ 3 สาขา)
#    key เดิม → partition เดิมเสมอ (บทเรียนจาก LAB 2) — งานจึงกระจายครบทุก partition
branches = ['bangkok', 'chiangmai', 'hatyai']
for i in range(1, count + 1):
    branch = branches[(i - 1) % 3]
    message = f'task-{i} ({branch})'
    metadata = producer.send('tasks',
                             key=branch.encode(),
                             value=message.encode()).get(timeout=10)
    print(f" [x] Sent '{message}' -> partition={metadata.partition}")

producer.close()
