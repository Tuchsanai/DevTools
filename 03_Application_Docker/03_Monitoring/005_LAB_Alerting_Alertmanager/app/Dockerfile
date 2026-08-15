FROM python:3.13-alpine

WORKDIR /srv

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py ./

ENV PYTHONUNBUFFERED=1 \
    PORT=8000 \
    ERROR_RATE=1.0

EXPOSE 8000
CMD ["python", "app.py"]
