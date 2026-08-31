# syntax=docker/dockerfile:1

# SkillSpace Web — Dockerfile แบบพื้นฐานสำหรับ Next.js
FROM node:22-alpine

WORKDIR /app

# ติดตั้ง dependency ก่อน เพื่อให้ Docker ใช้ layer cache ได้เมื่อ source เปลี่ยน
COPY package.json package-lock.json ./
RUN npm ci

# คัดลอก source แล้ว build Next.js
COPY . .
RUN npm run build

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

EXPOSE 3000

# เริ่ม Next.js production server
CMD ["npm", "start"]
