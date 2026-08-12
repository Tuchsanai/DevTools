"""Publish a persistent event and wait for RabbitMQ's confirmation."""

import sys

import pika


credentials = pika.PlainCredentials("student", "student123")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672, credentials=credentials)
)
channel = connection.channel()

# แยกชื่อจาก exchange ชั่วคราวของแล็บหลัก เพื่อให้ attributes ไม่ชนกัน
channel.exchange_declare(
    exchange="durable_logs", exchange_type="fanout", durable=True
)
channel.confirm_delivery()  # producer รอ broker ACK/NACK ทุก message

message = " ".join(sys.argv[1:]) or "audit: durable event"
try:
    channel.basic_publish(
        exchange="durable_logs",
        routing_key="",
        body=message,
        mandatory=True,  # route ไม่ถึง queue ให้ Pika โยน UnroutableError
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent,
            content_type="text/plain",
        ),
    )
except (pika.exceptions.UnroutableError, pika.exceptions.NackError) as error:
    connection.close()
    raise SystemExit(f" [!] Publish failed: {type(error).__name__}") from error

print(f" [x] Broker confirmed: {message}")
connection.close()
