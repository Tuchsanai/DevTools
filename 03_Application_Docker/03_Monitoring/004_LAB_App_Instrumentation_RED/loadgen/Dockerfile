FROM python:3.13-alpine

WORKDIR /loadgen

# ตัวยิงโหลดใช้แต่ stdlib (urllib + threading) จึงไม่ต้อง pip install อะไรเลย
COPY gen.py .

ENV PYTHONUNBUFFERED=1

CMD ["python", "gen.py"]
