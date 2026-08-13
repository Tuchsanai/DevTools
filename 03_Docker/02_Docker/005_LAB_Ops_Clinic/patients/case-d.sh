#!/bin/sh
# คนไข้ D — "โดนฆ่าเงียบ ๆ"
# จำกัดแรม 64 MB แล้วสั่งให้แอปกินแรมเพิ่มทีละ 2 MB ทุก 1 วินาที
# → kernel OOM killer เก็บ → Exited (137) และ .State.OOMKilled = true
docker rm -f patient-d >/dev/null 2>&1
docker run -d --name patient-d --memory=64m --memory-swap=64m -p 8083:8080 ops-clinic:1.0
sleep 4
curl -s -X POST "http://localhost:8083/leak?mb=2&delay=1"
