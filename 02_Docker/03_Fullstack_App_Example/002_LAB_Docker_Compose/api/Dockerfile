# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------
# SkillSpace API image  (LAB 002)
# ---------------------------------------------------------------------
FROM python:3.12-slim

# ไม่เขียนไฟล์ .pyc และไม่กัก stdout ไว้ใน buffer
# ถ้าไม่ตั้ง PYTHONUNBUFFERED บรรทัด print จะไม่โผล่ใน docker logs ทันที (ดีบักยากมาก)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# --- จุดสำคัญของ layer cache ---
# คัดลอก requirements.txt มา "ก่อน" แล้ว pip install แล้วค่อยคัดลอกโค้ด
# เพราะโค้ดเปลี่ยนทุกวัน แต่รายการ dependency แทบไม่เปลี่ยน
# ถ้าสลับลำดับ (COPY . . ก่อน) แก้โค้ดบรรทัดเดียวก็ต้อง pip install ใหม่ทั้งหมดทุกครั้ง
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# โค้ดมาทีหลังสุด — layer ที่เปลี่ยนบ่อยที่สุดต้องอยู่ล่างสุดเสมอ
COPY main.py .

# รันด้วยผู้ใช้ธรรมดา ไม่ใช่ root
# ถ้ามีช่องโหว่ในแอป ผู้บุกรุกจะได้สิทธิ์แค่ appuser ไม่ใช่ root ของคอนเทนเนอร์
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

# EXPOSE เป็นแค่ "เอกสาร" บอกว่าแอปฟังพอร์ตไหน — ไม่ได้เปิดพอร์ตให้เอง
# จะเข้าถึงจากนอกเครื่องได้ต้อง -p ตอน docker run เท่านั้น
EXPOSE 8000

# exec form (JSON array) → uvicorn เป็น PID 1 และได้รับ SIGTERM ตรง ๆ ตอน docker stop
# ถ้าใช้ shell form จะมี /bin/sh คั่นกลาง แล้วสัญญาณไปไม่ถึง ต้องรอ timeout 10 วินาทีทุกครั้ง
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
