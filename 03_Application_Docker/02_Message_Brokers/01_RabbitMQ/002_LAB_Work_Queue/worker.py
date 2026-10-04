import pika
import sys
import time

def main():
    credentials = pika.PlainCredentials('student', 'student123')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    # ประกาศแบบ durable ให้ตรงกับฝั่งผู้ส่ง (ประกาศไม่ตรงกันจะ error ทันที)
    channel.queue_declare(queue='task_queue', durable=True)

    def callback(ch, method, properties, body):
        message = body.decode()
        redelivered = " [redelivered]" if method.redelivered else ""
        print(f" [x] Received {message}{redelivered}")
        # งานปลอม: นับเฉพาะจุดที่ต่อท้ายข้อความ 1 จุด = ทำงาน 1 วินาที
        duration = len(message) - len(message.rstrip('.'))
        time.sleep(duration)
        print(" [x] Done")
        # ตอบรับด้วยมือว่า "งานนี้เสร็จแล้ว" — broker เพิ่งลบข้อความทิ้งตรงนี้
        ch.basic_ack(delivery_tag=method.delivery_tag)

    # แจกงานทีละ 1: อย่าส่งงานใหม่มาจนกว่าฉันจะ ack งานเดิม (fair dispatch)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
