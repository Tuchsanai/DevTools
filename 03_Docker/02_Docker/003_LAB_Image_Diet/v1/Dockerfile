# =============================================================
# v1 — "แบบที่ทำงานได้ แต่ไม่มีใครอยากดูแล"
# ปัญหา 4 ข้อที่ตั้งใจใส่ไว้ให้เห็นกับตาในแล็บ
#   1) ใช้ base image เต็มรูปแบบ (python:3.12 ~1 GB)
#   2) COPY ทุกอย่างเข้ามา "ก่อน" pip install  -> แก้โค้ด 1 บรรทัด = ลง lib ใหม่ทั้งชุด
#   3) ไม่มี .dockerignore -> ไฟล์ขยะ/dataset ถูกยัดเข้า image ด้วย
#   4) ไม่ pin เวอร์ชัน + รันด้วย root
# =============================================================
FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install flask gunicorn requests python-dotenv

ENV APP_VARIANT=v1 \
    BASE_IMAGE=python:3.12 \
    APP_PORT=8080

EXPOSE 8080

CMD ["python", "app/app.py"]
