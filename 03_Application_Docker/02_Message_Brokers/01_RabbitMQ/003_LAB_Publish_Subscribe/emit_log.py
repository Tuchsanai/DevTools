import pika
import sys

credentials = pika.PlainCredentials('student', 'student123')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

# ประกาศ exchange ชนิด fanout ชื่อ logs — ตัวกระจายข้อความให้ทุกคนที่ bind ไว้
channel.exchange_declare(exchange='logs', exchange_type='fanout')

message = ' '.join(sys.argv[1:]) or "info: Hello subscribers!"

# ส่งเข้า exchange ตรง ๆ — fanout ไม่สน routing_key จึงปล่อยเป็นค่าว่าง
channel.basic_publish(exchange='logs', routing_key='', body=message)
print(f" [x] Sent {message}")
connection.close()
