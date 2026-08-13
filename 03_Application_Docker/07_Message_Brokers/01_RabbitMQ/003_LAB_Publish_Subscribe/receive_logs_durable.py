"""Consume from a named durable subscription with manual acknowledgements."""

import sys

import pika


def main():
    credentials = pika.PlainCredentials("student", "student123")
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="localhost", port=5672, credentials=credentials)
    )
    channel = connection.channel()

    channel.exchange_declare(
        exchange="durable_logs", exchange_type="fanout", durable=True
    )
    channel.queue_declare(queue="audit_logs", durable=True)
    channel.queue_bind(exchange="durable_logs", queue="audit_logs")
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        print(f" [x] {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue="audit_logs", on_message_callback=callback)
    print(" [*] Durable subscription audit_logs is ready. Press CTRL+C to exit")
    channel.start_consuming()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Interrupted")
        sys.exit(0)
