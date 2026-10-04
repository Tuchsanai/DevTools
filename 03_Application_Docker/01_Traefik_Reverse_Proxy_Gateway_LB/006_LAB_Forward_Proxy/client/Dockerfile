FROM python:3.12-slim

# เครื่องพนักงานในออฟฟิศจำลอง — ต้องการแค่ curl ไว้ยิง request และพิสูจน์เรื่อง proxy
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

CMD ["sleep", "infinity"]
