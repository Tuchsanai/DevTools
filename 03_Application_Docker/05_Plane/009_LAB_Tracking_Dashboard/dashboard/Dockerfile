# Mission Control — dashboard ติดตามผลิตภัณฑ์จาก Plane API (FastAPI + inline SVG)
FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py metrics.py wip_policy.json ./
COPY static ./static
ENV PORT=8090
EXPOSE 8090
CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT}"]
