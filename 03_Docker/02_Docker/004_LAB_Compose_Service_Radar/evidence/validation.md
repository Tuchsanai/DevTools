# Validation evidence

ทดสอบจริงวันที่ 2026-08-12 ด้วย Docker Compose v5, Redis 8.2 Alpine และ Playwright CLI

```text
redis → healthy
api   → healthy after redis health gate
web   → healthy after api health gate
api -> 172.20.0.3
redis -> 172.20.0.2
visits before docker compose down = 4
volume after down = devtools-compose-radar_radar-data
visits after docker compose up = 5
```

พิสูจน์ว่า service-name DNS ใช้งานได้ และ `down` ที่ไม่ใส่ `-v` รักษา named volume

ภาพ: `images/actual-compose-radar.png`

