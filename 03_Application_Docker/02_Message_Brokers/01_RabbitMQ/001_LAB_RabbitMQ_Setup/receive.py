import pika
import sys

def main():
    # ต่อ broker ด้วยวิธีเดียวกับ send.py
    credentials = pika.PlainCredentials('student', 'student123')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    # ประกาศ attributes ให้ตรงฝั่งส่ง — จะรัน send หรือ receive ก่อนก็ได้
    channel.queue_declare(queue='hello', durable=True)

    # callback: ถูกเรียกอัตโนมัติทุกครั้งที่มีข้อความส่งมาถึง queue นี้
    def callback(ch, method, properties, body):
        print(f" [x] Received {body.decode()}")

    # auto_ack=True: broker ถือว่าส่งสำเร็จทันที (ไม่มี ACK frame จาก consumer)
    # เหมาะกับ demo ที่ยอมเสียข้อความได้; LAB 2 จะใช้ manual ack หลังทำงานเสร็จ
    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()   # วนรอรับข้อความไปเรื่อย ๆ จนกด Ctrl+C

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
