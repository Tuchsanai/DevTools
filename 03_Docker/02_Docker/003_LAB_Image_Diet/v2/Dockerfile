# =============================================================
# v2 — "เรียง layer ให้ cache ทำงาน + เปลี่ยนไปใช้ base ที่ผอมกว่า"
#   1) python:3.12-slim แทน python:3.12
#   2) COPY requirements.txt -> pip install -> ค่อย COPY โค้ด
#      แก้โค้ด 1 บรรทัด จะไม่ทำให้ layer ของ pip เสีย cache
#   3) pin เวอร์ชันไว้ใน requirements.txt ทุกตัว
# ยังเหลืออีก 2 เรื่องที่ v3 จะไปแก้ต่อ : ยังรันด้วย root และยังมี pip cache ติดอยู่
# =============================================================
FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY app/ ./app/

ENV APP_VARIANT=v2 \
    BASE_IMAGE=python:3.12-slim \
    APP_PORT=8080

EXPOSE 8080

CMD ["python", "app/app.py"]
