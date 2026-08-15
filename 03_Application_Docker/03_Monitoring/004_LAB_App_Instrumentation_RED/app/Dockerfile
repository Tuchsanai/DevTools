FROM python:3.13-alpine

WORKDIR /app

# ติดตั้ง dependency ก่อน copy โค้ด เพื่อให้ layer cache ของ pip ไม่โดนล้างทุกครั้งที่แก้ app.py
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# ไม่ buffer stdout เพื่อให้ print() โผล่ใน docker compose logs ทันที
ENV PYTHONUNBUFFERED=1
# ไม่ต้องสร้าง series *_created ที่พ่วงมากับ Counter (ค่าเป็น unix timestamp ตอนสร้าง)
# ปิดไว้เพื่อให้หน้า /metrics อ่านง่ายและนับ series ในแล็บได้ตรงไปตรงมา
ENV PROMETHEUS_DISABLE_CREATED_SERIES=true

EXPOSE 8000
CMD ["python", "app.py"]
