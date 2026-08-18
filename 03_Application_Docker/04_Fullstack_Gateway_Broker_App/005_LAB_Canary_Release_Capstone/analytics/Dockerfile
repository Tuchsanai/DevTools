# syntax=docker/dockerfile:1
FROM python:3.12-slim
# (1) log consumer ต้องออกทันทีเพื่อสังเกต partition/offset
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
# (2) วาง dependency ก่อนโค้ดเพื่อใช้ cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY analytics.py audit.py .
# (3) ลดสิทธิ์ process เป็น uid 10001
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser
CMD ["python", "analytics.py"]
