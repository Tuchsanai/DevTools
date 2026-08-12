import pika
import sys

def main():
    credentials = pika.PlainCredentials('student', 'student123')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    # ประกาศ exchange ให้ตรงกับฝั่งผู้ส่ง (ฝั่งไหนรันก่อนก็ได้)
    channel.exchange_declare(exchange='logs', exchange_type='fanout')

    # queue ชั่วคราว: queue='' ให้ broker ตั้งชื่อให้ (amq.gen-…)
    # exclusive=True = เป็นของ connection นี้คนเดียว ปิดโปรแกรมปุ๊บ queue หายปั๊บ
    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    print(f" [*] My queue is {queue_name}")

    # bind: บอก exchange logs ว่า "ขอสำเนาทุกข้อความมาเข้า queue ของฉันด้วย"
    channel.queue_bind(exchange='logs', queue=queue_name)

    print(' [*] Waiting for logs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(f" [x] {body.decode()}")

    # auto_ack=True = broker ถือว่า delivery เสร็จทันทีที่ส่ง ไม่มี ACK frame จาก consumer
    # ใช้ได้กับ live log demo ที่ยอมเสียข้อความ; งานสำคัญดู receive_logs_durable.py
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
