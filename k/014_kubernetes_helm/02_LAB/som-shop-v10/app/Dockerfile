# ร้านอาหารแมวน้องส้ม — Next.js standalone (multi-stage build)

# ---------- 1) deps: ติดตั้ง dependency ตาม package-lock.json ----------
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# ---------- 2) build: คอมไพล์แอปเป็น .next/standalone ----------
FROM node:22-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---------- 3) runner: image สำหรับรันจริง (เล็ก ไม่มี source/devDependencies) ----------
FROM node:22-alpine AS runner
WORKDIR /app
# เวอร์ชันและธีมถูก "จำ" ไว้ใน image แต่ละ tag (build ด้วย --build-arg)
#   1.2: --build-arg APP_VERSION=1.2 --build-arg APP_THEME=harbor
#   1.3: --build-arg APP_VERSION=1.3 --build-arg APP_THEME=sunset
#   1.5: --build-arg APP_VERSION=1.5  (ชื่อร้าน/ธีม/โปรโมชันมาจาก env = ConfigMap, ประกาศจากไฟล์ /etc/som/announcement.txt)
#   1.7: --build-arg APP_VERSION=1.7  (เพิ่ม /api/work?ms=N หมุน CPU ให้ HPA เห็นโหลด — บท 013)
#   1.8: --build-arg APP_VERSION=1.8  (โค้ดเดิมทุกบรรทัด — บท 014 ใช้ทดสอบ helm upgrade/rollback)
ARG APP_VERSION=dev
ARG APP_THEME=harbor
ENV APP_VERSION=$APP_VERSION \
    APP_THEME=$APP_THEME \
    NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
COPY --from=build --chown=node:node /app/public ./public
# สคริปต์ seed ใช้ใน init container (ใช้ node_modules/pg ที่อยู่ใน standalone แล้ว)
COPY --from=build --chown=node:node /app/scripts ./scripts
USER node
EXPOSE 3000
CMD ["node", "server.js"]
