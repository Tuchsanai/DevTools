FROM python:3.12-slim

WORKDIR /app

# requirements ก่อน แล้วค่อย COPY โค้ด — layer ของ pip จะได้ถูก cache ไว้
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# ค่า default ของ image (บุคลิกเริ่มต้นของโรงงาน)
ENV APP_COLOR=blue \
    APP_NAME="Color Factory" \
    APP_PORT=8081

# อบค่า ENV ตอน build ลงไฟล์ เพื่อให้แอปบอกได้ว่าค่าที่ใช้อยู่ถูก override หรือยัง
RUN python -c "import json,os;json.dump({k:os.environ[k] for k in ('APP_COLOR','APP_NAME','APP_PORT')},open('/app/build_defaults.json','w'))"

EXPOSE 8081

CMD ["python", "app.py"]
