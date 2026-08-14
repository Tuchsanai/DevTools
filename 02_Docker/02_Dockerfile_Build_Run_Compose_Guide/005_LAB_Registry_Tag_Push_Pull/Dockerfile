# กำหนดอิมเมจพื้นฐาน nginx เวอร์ชัน 1.27 บน Alpine แบบระบุเวอร์ชันชัดเจน
FROM nginx:1.27-alpine
# กำหนดโฟลเดอร์เว็บไซต์ต้นทาง โดยเปลี่ยนค่าได้ตอนสั่ง docker build
ARG SITE_DIR=site
# กำหนดหมายเลขรีลีส โดยมีค่าเริ่มต้นเป็น 1.0
ARG RELEASE=1.0
# ระบุชื่ออิมเมจตามมาตรฐาน Open Container Initiative
LABEL org.opencontainers.image.title="regdemo"
# บันทึกหมายเลขรีลีสจาก build argument ลงใน metadata ของอิมเมจ
LABEL release="${RELEASE}"
# คัดลอกเว็บไซต์จากโฟลเดอร์ที่เลือกไปยัง document root ของ nginx
COPY ${SITE_DIR}/ /usr/share/nginx/html/
# ระบุว่าเว็บเซิร์ฟเวอร์ภายในคอนเทนเนอร์ให้บริการผ่านพอร์ต 80
EXPOSE 80
