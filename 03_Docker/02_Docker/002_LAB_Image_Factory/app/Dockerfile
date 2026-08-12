# syntax=docker/dockerfile:1
FROM python:3.13-alpine

ARG APP_VERSION=1.0.0
LABEL org.opencontainers.image.title="Docker Image Factory Lab" \
      org.opencontainers.image.version="${APP_VERSION}" \
      org.opencontainers.image.description="A dependency-free teaching app"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_THEME=ocean \
    APP_STAGE=development \
    APP_VERSION=${APP_VERSION} \
    PORT=8080

WORKDIR /app
RUN addgroup -S app && adduser -S -D -H -u 10001 -G app app
COPY --chown=app:app app.py ./app.py

USER app
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s --start-period=3s --retries=5 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=1)"]
CMD ["python", "app.py"]
