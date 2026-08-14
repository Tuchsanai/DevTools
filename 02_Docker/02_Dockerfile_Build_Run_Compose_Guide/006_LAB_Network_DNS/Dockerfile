# ใช้ nginx Alpine แบบ pin เวอร์ชันเพื่อให้ผลลัพธ์ของ LAB ทำซ้ำได้
FROM nginx:1.27-alpine

# ระบุข้อมูลกำกับ image สำหรับ LAB Docker Network และ DNS
LABEL org.opencontainers.image.title="Container Network Console" \
      org.opencontainers.image.description="Docker Network and DNS teaching lab" \
      org.opencontainers.image.version="1.0"

# คัดลอกหน้า template ซึ่งจะถูก render ใหม่ทุกครั้งที่ container เริ่มทำงาน
COPY site/index.html.tpl /usr/share/nginx/html/index.html.tpl

# ใช้ server config ของ LAB แทนค่าเริ่มต้นของ nginx
COPY docker/netlab.conf /etc/nginx/conf.d/default.conf

# ติดตั้ง entrypoint hook สำหรับอ่านข้อมูล network จริงจากใน container
COPY docker/40-render-console.sh /docker-entrypoint.d/40-render-console.sh

# ทำให้ entrypoint hook สามารถรันได้บน Alpine
RUN chmod +x /docker-entrypoint.d/40-render-console.sh

# ประกาศทั้งพอร์ต HTTP มาตรฐานและพอร์ตสำรองของ LAB
EXPOSE 80 8186
