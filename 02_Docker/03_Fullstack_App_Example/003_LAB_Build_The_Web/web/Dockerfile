# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------
# SkillSpace Web image  (LAB 3) — Next.js standalone แบบ multi-stage
#
# แนวคิด : เครื่องมือที่ใช้ "ตอน build" (โค้ด TypeScript, devDependencies, ตัว compiler)
# ไม่จำเป็นต้องติดไปกับ image ที่เอาไป "รัน" เลยแม้แต่นิดเดียว
# จึงแยกเป็น 3 ชั้น แล้วชั้นสุดท้ายหยิบไปเฉพาะผลลัพธ์ที่ต้องใช้จริง
# ---------------------------------------------------------------------

# ---------- ชั้นที่ 1 : ติดตั้ง dependency ----------
FROM node:22-alpine AS deps
WORKDIR /app

# คัดลอกเฉพาะไฟล์รายการ dependency ก่อน แล้วค่อย npm ci
# โค้ดเปลี่ยนทุกวันแต่ dependency แทบไม่เปลี่ยน → layer นี้ถูก cache ไว้ใช้ซ้ำได้เกือบตลอด
# ใช้ npm ci ไม่ใช่ npm install เพราะ ci ยึดตาม package-lock.json เป๊ะ ๆ (build ซ้ำได้ผลเดิม)
COPY package.json package-lock.json ./
RUN npm ci

# ---------- ชั้นที่ 2 : build ----------
FROM node:22-alpine AS builder
WORKDIR /app

# ARG อ่านได้เฉพาะตอน build · ENV ติดไปกับ image ตอนรันด้วย
# ค่า NEXT_PUBLIC_* ถูก "ฝัง" ลงไฟล์ผลลัพธ์ตอน build จึงต้องมาถึงตรงนี้ก่อน npm run build
ARG NEXT_PUBLIC_SITE_NAME=SkillSpace
ENV NEXT_PUBLIC_SITE_NAME=$NEXT_PUBLIC_SITE_NAME
ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---------- ชั้นที่ 3 : runtime ----------
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

# รันด้วยผู้ใช้ธรรมดา ไม่ใช่ root (node:22-alpine มี user 'node' อยู่แล้ว แต่ตั้งเองให้เห็นชัดว่าเป็นของแอปนี้)
RUN addgroup -g 10001 -S webapp && adduser -u 10001 -S webapp -G webapp

# output:"standalone" ทำให้ .next/standalone มี server.js + node_modules เท่าที่ใช้จริงมาให้แล้ว
COPY --from=builder --chown=webapp:webapp /app/.next/standalone ./

# !! กับดักที่เจอมาแล้วกับ Next.js 16 !!
# ไฟล์ CSS ถูกวางไว้ที่ .next/static/chunks/*.css ไม่ใช่ .next/static/css/
# ถ้าเจาะ COPY เฉพาะโฟลเดอร์ย่อย (เช่น .next/static/css) จะได้หน้าเว็บที่ไม่มี CSS เลย
# → ต้องคัดลอก .next/static ทั้งก้อนเท่านั้น
COPY --from=builder --chown=webapp:webapp /app/.next/static ./.next/static

USER webapp

# EXPOSE เป็นเอกสารบอกว่าแอปฟังพอร์ตไหน ไม่ได้เปิดพอร์ตให้เอง
EXPOSE 3000

# exec form → node เป็น PID 1 ได้รับ SIGTERM ตรง ๆ ตอน docker stop (ไม่ต้องรอ timeout 10 วินาที)
CMD ["node", "server.js"]
