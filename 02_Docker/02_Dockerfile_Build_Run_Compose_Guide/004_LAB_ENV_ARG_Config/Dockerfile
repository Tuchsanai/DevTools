FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV APP_ENV=development
ENV APP_VERSION=1.0.0
ENV GREETING="Hello"
ENV FEATURE_FLAGS="beta-ui"
ENV LOG_LEVEL=info

EXPOSE 8184

CMD ["python","app.py"]
