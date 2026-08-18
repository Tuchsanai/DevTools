# syntax=docker/dockerfile:1
# (1) ชั้น dependency ใช้ npm ci และ lock file เพื่อ build ซ้ำได้ผลเดิม
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# (2) ชั้น build สร้าง Next.js standalone; ไม่มี font หรือ asset จาก CDN
FROM node:22-alpine AS builder
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# (3) ชั้น runtime มีเฉพาะ server, public และ .next/static ทั้งก้อน
FROM node:22-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000 HOSTNAME=0.0.0.0
RUN addgroup -g 10001 -S webapp && adduser -u 10001 -S webapp -G webapp
COPY --from=builder --chown=webapp:webapp /app/.next/standalone ./
COPY --from=builder --chown=webapp:webapp /app/.next/static ./.next/static
USER webapp
EXPOSE 3000
CMD ["node", "server.js"]
