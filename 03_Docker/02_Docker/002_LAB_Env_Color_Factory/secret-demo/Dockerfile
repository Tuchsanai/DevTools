# ตัวอย่าง "วิธีที่ผิด" — ใช้สาธิตว่า ARG/ENV ไม่ใช่ที่เก็บความลับ
# ค่าทั้งสองบรรทัดนี้เป็นค่าสมมติสำหรับสอนเท่านั้น ห้ามใส่ค่าจริงลงใน Dockerfile
FROM alpine:3.21

ARG DB_PASSWORD=not-a-real-password-1234
ENV API_TOKEN=not-a-real-token-abcd

RUN echo "building with DB_PASSWORD=$DB_PASSWORD" > /build.log

CMD ["sh", "-c", "echo leaky image"]
