#!/bin/bash
# LAB 2 — expose the MinIO console (plane-minio:9090) through a socat bridge.
# Then forward port 9090 in VS Code PORTS and open http://localhost:9090 (access-key / secret-key = LAB defaults).
docker rm -f minio-ui >/dev/null 2>&1
docker run -d --name minio-ui --network plane_default -p 9090:9090 alpine/socat:1.8.0.0 \
  TCP-LISTEN:9090,fork,reuseaddr TCP:plane-minio:9090
echo "minio-ui bridge up → forward 9090 and open http://localhost:9090  (access-key / secret-key)"
