# ร้านอาหารแมวน้องส้ม (Helm) — Node.js ล้วน ไม่มี dependency
# image เดียวใช้ได้ทั้งหน้าร้านและครัว (เลือกด้วย env APP_MODE) สมุดออเดอร์อยู่ที่ /data บน PVC
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000
COPY server.js ./
COPY public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
