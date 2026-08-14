# Dockerfile.cmd
# ใช้ Alpine Linux เวอร์ชัน 3.20 เป็น base image
FROM alpine:3.20
# กำหนดคำสั่งเริ่มต้นที่สามารถแทนที่ตอน docker run ได้
CMD ["echo", "ข้อความเริ่มต้นจาก CMD"]
