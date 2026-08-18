# syntax=docker/dockerfile:1
FROM python:3.12-slim

# (1) ให้ log ภาษาไทยออกทันทีและไม่สร้างไฟล์ bytecode ที่ไม่จำเป็น
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# (2) แยกชั้น dependency เพื่อให้ Docker ใช้ cache ได้
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .

# (3) ลดสิทธิ์ process ตามรูปแบบ CampusOps
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
