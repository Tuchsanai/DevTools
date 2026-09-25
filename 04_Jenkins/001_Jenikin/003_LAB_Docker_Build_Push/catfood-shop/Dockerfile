# ---------- Stage 1: deps — ติดตั้ง dependency ตาม package-lock.json ----------
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund

# ---------- Stage 2: build — คอมไพล์ Next.js เป็น standalone server ----------
FROM node:22-alpine AS build
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# ---------- Stage 3: runtime — เก็บเฉพาะไฟล์ที่ต้องใช้ตอนรัน ----------
FROM node:22-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

COPY --from=build --chown=node:node /app/public ./public
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static

# ข้อมูล build ประกาศไว้ท้ายสุด: เปลี่ยนเลข build ได้โดยไม่ทำให้ cache ของ npm ci / next build หาย
ARG APP_VERSION=dev
ARG BUILD_NUMBER=local
ARG GIT_COMMIT=none
ARG BUILD_TIME=unknown
ENV APP_VERSION=$APP_VERSION \
    BUILD_NUMBER=$BUILD_NUMBER \
    GIT_COMMIT=$GIT_COMMIT \
    BUILD_TIME=$BUILD_TIME

USER node
EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/api/health || exit 1
CMD ["node", "server.js"]
