# ร้านอาหารแมวน้องส้ม (PersistentVolume) — Node.js ล้วน ไม่มี dependency
# สมุดออเดอร์ไม่ได้อยู่ใน image แต่อยู่ที่ /data ซึ่ง Kubernetes ต่อ PVC เข้ามาให้
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000
COPY server.js ./
COPY public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
