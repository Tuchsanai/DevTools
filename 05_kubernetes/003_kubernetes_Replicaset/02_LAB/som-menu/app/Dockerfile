# ร้านอาหารแมวน้องส้ม (หลายสาขา) — Node.js ล้วน ไม่มี dependency
FROM node:22-alpine
WORKDIR /app

# เวอร์ชันของร้าน เปลี่ยนตอน build ได้ เช่น --build-arg APP_VERSION=2.0
ARG APP_VERSION=1.0
ENV APP_VERSION=$APP_VERSION \
    NODE_ENV=production \
    PORT=3000

COPY server.js ./
COPY public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
