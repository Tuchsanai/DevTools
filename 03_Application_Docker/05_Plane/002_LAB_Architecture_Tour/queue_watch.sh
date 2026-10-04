#!/bin/bash
# LAB 2 — watch the Celery queue inside RabbitMQ every 2 s (vhost is "plane", so -p plane is mandatory). Ctrl+C to stop.
while true; do
  printf "\033[H\033[2J"
  echo "== $(date +%T)  rabbitmqctl list_queues -p plane   (Ctrl+C to stop)"
  pc exec -T plane-mq rabbitmqctl list_queues -p plane name messages consumers 2>/dev/null | grep -vE '^(Timeout|Listing)'
  sleep 2
done
