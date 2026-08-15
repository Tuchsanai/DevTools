FROM python:3.12-slim

WORKDIR /app

COPY server.py .

# ประกาศทั้งสอง port — Traefik ใช้ข้อมูลนี้ "เดา" port ปลายทางเมื่อเราไม่ได้บอกด้วย label
EXPOSE 8080 9090

CMD ["python", "-u", "server.py"]
