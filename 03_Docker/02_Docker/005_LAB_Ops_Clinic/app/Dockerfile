FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV APP_NAME=ops-clinic \
    APP_PORT=8080

EXPOSE 8080

# หมอประจำตัวของ container : เรียก /healthz ทุก 5 วินาที
# ถ้า exit code != 0 ติดกัน 3 ครั้ง STATUS จะกลายเป็น (unhealthy)
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8080/healthz',timeout=2)"

CMD ["python", "app.py"]
