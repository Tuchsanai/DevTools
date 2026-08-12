import os

import pika

# 1) ข้อมูลล็อกอิน — ใช้ค่า LAB เป็น default และ override password เพื่อทดลอง error ได้
password = os.getenv('RABBITMQ_PASSWORD', 'student123')
credentials = pika.PlainCredentials('student', password)

# 2) เปิด connection (ท่อ TCP) ไปหา broker ที่ localhost port 5672 (AMQP)
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))

# 3) เปิด channel — ช่องสื่อสารย่อยภายใน connection ใช้ส่งคำสั่งทุกอย่าง
channel = connection.channel()

# 4) RabbitMQ 4.x ใช้ durable queue แทน transient non-exclusive queue รุ่นเก่า
channel.queue_declare(queue='hello', durable=True)

# 5) ส่งข้อความผ่าน default exchange ("") — routing_key = ชื่อ queue ปลายทาง
channel.basic_publish(exchange='', routing_key='hello', body='Hello RabbitMQ!')
print(" [x] Sent 'Hello RabbitMQ!'")

# 6) ปิด connection ให้เรียบร้อย (pika จะส่งข้อมูลที่ค้างอยู่ออกให้หมดก่อน)
connection.close()
