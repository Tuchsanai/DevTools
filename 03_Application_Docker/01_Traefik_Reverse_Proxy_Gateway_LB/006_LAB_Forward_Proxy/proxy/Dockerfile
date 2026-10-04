FROM python:3.12-slim

WORKDIR /app

COPY forward_proxy.py .

EXPOSE 8888 8899

CMD ["python", "-u", "forward_proxy.py"]
