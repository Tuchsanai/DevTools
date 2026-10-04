# hookwall — receiver + กำแพง event สำหรับ webhook ของ Plane (stdlib ล้วน ไม่ต้อง pip install)
FROM python:3.12-alpine
WORKDIR /app
COPY app.py rules.json ./
COPY static ./static
ENV PORT=9000 DATA_DIR=/data
EXPOSE 9000
VOLUME ["/data"]
CMD ["python", "app.py"]
