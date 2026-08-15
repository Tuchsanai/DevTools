FROM python:3.13-alpine

WORKDIR /srv
COPY receiver.py ./

ENV PYTHONUNBUFFERED=1 \
    PORT=5001

EXPOSE 5001
CMD ["python", "receiver.py"]
