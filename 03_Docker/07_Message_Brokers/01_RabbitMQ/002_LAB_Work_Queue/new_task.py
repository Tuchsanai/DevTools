import pika
import sys

credentials = pika.PlainCredentials('student', 'student123')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

# durable=True: นิยาม queue อยู่รอดเมื่อ broker restart โดยยังใช้ storage เดิม
channel.queue_declare(queue='task_queue', durable=True)

# ข้อความ = argument ทั้งหมดต่อกัน (จำนวนจุด . ท้ายข้อความ = วินาทีที่งานนี้ใช้)
message = ' '.join(sys.argv[1:]) or "Hello World!"

channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=pika.DeliveryMode.Persistent,  # ขอให้ broker เก็บข้อความแบบ persistent
    ))
print(f" [x] Sent {message}")
connection.close()
