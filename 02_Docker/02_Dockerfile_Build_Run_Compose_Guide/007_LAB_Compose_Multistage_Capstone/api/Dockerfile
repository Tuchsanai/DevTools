# ใช้อิมเมจ Python 3.12 รุ่นเล็กเป็นฐาน
FROM python:3.12-slim
# กำหนดโฟลเดอร์ทำงานภายในคอนเทนเนอร์
WORKDIR /app
# ปิดไฟล์ bytecode และแสดง log แบบไม่ buffer
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# คัดลอกรายการแพ็กเกจก่อนเพื่อใช้ประโยชน์จาก layer cache
COPY requirements.txt .
# ติดตั้ง dependency โดยไม่เก็บ pip cache
RUN pip install --no-cache-dir -r requirements.txt
# คัดลอกซอร์ส API ทั้งหมดเข้าอิมเมจ
COPY . .
# บันทึกเวลาที่ build image ลงไฟล์ ให้แอปอ่านไปแสดงบน dashboard ตอนรัน
RUN date -u +'%Y-%m-%d %H:%M:%S UTC' > /app/BUILD_TIME
# ระบุพอร์ตที่ Flask รับคำขอ
EXPOSE 5000
# เริ่ม Flask API ด้วย Python
CMD ["python", "app.py"]
