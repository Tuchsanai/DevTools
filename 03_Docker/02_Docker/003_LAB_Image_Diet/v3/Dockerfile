# =============================================================
# v3 — multi-stage + non-root + healthcheck
#   stage 1 (builder) : ใช้ base ตัวหนัก 1 GB ได้เต็มที่ ติดตั้ง lib ลง venv
#                       และรันขั้นตอน build asset (minify CSS)
#   stage 2 (runtime) : เริ่มจาก base ผอม แล้วหยิบมาเฉพาะ "ผลลัพธ์"
#                       -> เครื่องมือ build ไม่ตามไปกับ image สุดท้าย
# =============================================================

# ---------------------- stage 1 : builder ----------------------
FROM python:3.12 AS builder

WORKDIR /build

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
RUN python app/build_assets.py

# ---------------------- stage 2 : runtime ----------------------
FROM python:3.12-slim

RUN useradd --create-home --uid 10001 appuser

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /build/app/ ./app/

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    APP_VARIANT=v3 \
    BASE_IMAGE=python:3.12-slim \
    APP_PORT=8080

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request as u; u.urlopen('http://127.0.0.1:8080/healthz')" || exit 1

CMD ["python", "app/app.py"]
