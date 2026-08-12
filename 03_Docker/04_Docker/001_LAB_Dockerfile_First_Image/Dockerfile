# ── Image แรกของคุณ : Flask web app ขนาดเล็ก ──────────────────────────
# ลำดับบรรทัดมีความหมาย! คัดลอก requirements.txt ก่อน source code
# เพื่อให้ layer "pip install" ถูก cache ไว้ แม้เราแก้ app.py กี่ครั้งก็ตาม

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV APP_VERSION=1.0

EXPOSE 5000

CMD ["python", "app.py"]
