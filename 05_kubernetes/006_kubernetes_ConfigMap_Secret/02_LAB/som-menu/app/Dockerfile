# ร้านอาหารแมวน้องส้ม (ConfigMap + Secret) — Node.js ล้วน ไม่มี dependency
# image นี้ไม่มีชื่อร้าน ประกาศ เมนู หรือรหัสผ่านฝังอยู่ ทุกอย่างมาจาก ConfigMap / Secret ตอนรัน
FROM node:22-alpine
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000
COPY server.js ./
COPY public ./public
USER node
EXPOSE 3000
CMD ["node", "server.js"]
