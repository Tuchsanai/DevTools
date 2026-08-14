import pika
import sys

credentials = pika.PlainCredentials('student', 'student123')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
channel = connection.channel()

channel.exchange_declare(exchange='direct_logs', exchange_type='direct')

# argument แรก = severity (ใช้เป็น routing key) · ที่เหลือ = ตัวข้อความ
severity = sys.argv[1] if len(sys.argv) > 1 else 'info'
message = ' '.join(sys.argv[2:]) or 'Hello World!'

channel.basic_publish(exchange='direct_logs', routing_key=severity, body=message)
print(f" [x] Sent {severity}: {message}")
connection.close()
