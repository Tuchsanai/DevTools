FROM python:3.13-alpine

WORKDIR /app
COPY receiver.py ./

EXPOSE 5001
CMD ["python", "-u", "receiver.py"]
