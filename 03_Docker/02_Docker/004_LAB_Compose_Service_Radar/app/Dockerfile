# syntax=docker/dockerfile:1
FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PORT=8080 ROLE=web
WORKDIR /app
RUN addgroup -S app && adduser -S -D -H -u 10001 -G app app
COPY --chown=app:app service.py ./service.py

USER app
EXPOSE 8080
CMD ["python", "service.py"]
