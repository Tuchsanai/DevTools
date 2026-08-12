"""Show how publisher confirms + mandatory expose an unroutable message."""

import pika


credentials = pika.PlainCredentials("student", "student123")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost", port=5672, credentials=credentials)
)
channel = connection.channel()
channel.exchange_declare(exchange="direct_logs", exchange_type="direct")
channel.confirm_delivery()

try:
    # หลังปิด consumer ทั้งหมด ไม่มี temporary queue bind key "debug"
    channel.basic_publish(
        exchange="direct_logs",
        routing_key="debug",
        body="This message has no matching queue",
        mandatory=True,
    )
except pika.exceptions.UnroutableError:
    print(" [!] Unroutable: no queue is bound with routing key 'debug'")
else:
    print(" [x] Routed and confirmed by RabbitMQ")
finally:
    connection.close()
