# Dockerfile แบบ single-stage — ทุกขั้นอยู่ใน image เดียว อ่านจากบนลงล่างได้ทันที
FROM node:22-alpine
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

# ① ติดตั้ง dependency ก่อน: ถ้า package*.json ไม่เปลี่ยน ขั้นนี้ใช้ cache ได้เลย (ล้าง cache ของ npm ทิ้งในขั้นเดียวกัน)
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund && npm cache clean --force

# ② คัดลอกซอร์สแล้ว build (ลบ cache ของการ build ทิ้ง ไม่ต้องใช้ตอนรัน)
COPY . .
RUN npm run build && rm -rf .next/cache

# ③ ตั้งค่าตอนรัน
ENV NODE_ENV=production \
    PORT=3000

# ข้อมูล build ประกาศไว้ท้ายสุด: เปลี่ยนเลข build ได้โดยไม่ทำให้ cache ของ npm ci / next build หาย
ARG APP_VERSION=dev
ARG BUILD_NUMBER=local
ARG GIT_COMMIT=none
ARG BUILD_TIME=unknown
ENV APP_VERSION=$APP_VERSION \
    BUILD_NUMBER=$BUILD_NUMBER \
    GIT_COMMIT=$GIT_COMMIT \
    BUILD_TIME=$BUILD_TIME

EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --start-period=30s --start-interval=1s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/api/health || exit 1
CMD ["npm", "start"]
