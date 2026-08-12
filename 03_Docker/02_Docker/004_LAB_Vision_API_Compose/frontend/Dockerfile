FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .
COPY static/ ./static/

ENV BACKEND_URL=http://backend:8000 \
    APP_TITLE="Vision API" \
    APP_PORT=8501

EXPOSE 8501

CMD ["python", "app.py"]
