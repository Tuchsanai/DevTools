import pika
import sys

def main():
    binding_keys = sys.argv[1:]
    if not binding_keys:
        sys.stderr.write(f"Usage: {sys.argv[0]} [binding_key]...\n")
        sys.exit(1)

    credentials = pika.PlainCredentials('student', 'student123')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    channel.exchange_declare(exchange='topic_logs', exchange_type='topic')

    result = channel.queue_declare(queue='', exclusive=True)
    queue_name = result.method.queue
    print(f" [*] My queue is {queue_name}")

    # bind ทีละ pattern — queue เดียว bind หลาย pattern ได้
    for binding_key in binding_keys:
        channel.queue_bind(exchange='topic_logs', queue=queue_name,
                           routing_key=binding_key)

    print(f" [*] Waiting for {binding_keys}. To exit press CTRL+C")

    def callback(ch, method, properties, body):
        # method.routing_key = routing key ของข้อความที่เข้ามา
        print(f" [x] {method.routing_key}: {body.decode()}")

    # live log demo: broker ถือว่า delivery เสร็จทันทีที่ส่ง (ไม่มี ACK frame)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
