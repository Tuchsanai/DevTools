#!/bin/sh
# คนไข้ D — "โดนฆ่าเงียบ ๆ"
# จำกัดแรม 64 MB แล้วสั่งให้แอปกินแรมเรื่อย ๆ → kernel OOM killer เก็บ → Exited (137)
docker rm -f patient-d >/dev/null 2>&1
docker run -d --name patient-d --memory=64m --memory-swap=64m -p 8082:8080 ops-clinic:1.0
sleep 3
curl -s -X POST http://localhost:8082/leak
