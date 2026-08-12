# syntax=docker/dockerfile:1
FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080 DATA_FILE=/data/state.json
WORKDIR /app
RUN addgroup -S app && adduser -S -D -H -u 10001 -G app app \
    && mkdir -p /data && chown app:app /data
COPY --chown=app:app app.py ./app.py

USER app
VOLUME ["/data"]
EXPOSE 8080
HEALTHCHECK --interval=5s --timeout=2s --start-period=3s --retries=5 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=1)"]
CMD ["python", "app.py"]
