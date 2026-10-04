#!/bin/bash
# LAB 2 — expose the RabbitMQ Management UI (plane-mq:15672, NOT published by Plane's compose) through a tiny socat bridge.
# Then forward port 15672 in VS Code PORTS and open http://localhost:15672 (user plane / password plane).
docker rm -f mq-ui >/dev/null 2>&1
docker run -d --name mq-ui --network plane_default -p 15672:15672 alpine/socat:1.8.0.0 \
  TCP-LISTEN:15672,fork,reuseaddr TCP:plane-mq:15672
echo "mq-ui bridge up → forward 15672 and open http://localhost:15672  (plane / plane)"
