# syntax=docker/dockerfile:1
FROM python:3.12-slim
# (1) แสดง log ทันทีเพื่อดูการ ack/redelivery ในบทเรียน
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# (2) ติดตั้ง dependency ก่อนโค้ดเพื่อใช้ layer cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY worker.py .
# (3) รัน worker ด้วย uid 10001 ไม่ใช้ root
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python", "worker.py"]
