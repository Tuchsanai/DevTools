FROM python:3.13-alpine

WORKDIR /srv
COPY gen.py ./

ENV PYTHONUNBUFFERED=1 \
    TARGET_URL=http://app:8000 \
    RPS=8 \
    ERROR_MIX=0 \
    SLOW_MIX=0 \
    SEED=2569

CMD ["python", "gen.py"]
