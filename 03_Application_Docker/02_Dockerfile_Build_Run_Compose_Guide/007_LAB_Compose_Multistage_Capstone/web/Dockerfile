# Stage 1: ใช้ Python image เป็น build environment ซึ่งจะไม่ติดไปกับ runtime image
FROM python:3.12-slim AS build
# กำหนดโฟลเดอร์ทำงานของขั้น build ให้ไฟล์ต้นทางอยู่รวมกันใน /src
WORKDIR /src
# คัดลอกเฉพาะ build tool และ template ที่จำเป็นต่อการสร้าง static artifact
COPY build_site.py template.html ./
# รับเวลาสร้างจาก Compose ตอน docker build และใช้ unknown เมื่อไม่ได้ระบุค่า
ARG BUILD_TIME=unknown
# ส่ง build argument เข้า environment เพื่อให้ build_site.py อ่านผ่าน os.environ
ENV BUILD_TIME=${BUILD_TIME}
# ติดตั้ง Jinja2 ที่ใช้ render จริงและ csscompressor เพื่อจำลอง build toolchain ที่หนักกว่า runtime
RUN pip install --no-cache-dir jinja2==3.1.4 csscompressor==0.9.5
# รัน build tool เพื่อรวม template, CSS และ JavaScript เป็น artifact ไฟล์เดียวใน /out
RUN python build_site.py /out/index.html

# Stage 2: ใช้ nginx Alpine ขนาดเล็กเป็น production runtime โดยไม่มี Python หรือ build toolchain
FROM nginx:1.27-alpine
# คัดเฉพาะ artifact ที่ build เสร็จแล้วจาก stage build ไม่คัด Python, source หรือแพ็กเกจ build มาด้วย
COPY --from=build /out/index.html /usr/share/nginx/html/index.html
# คัดลอก config สำหรับเสิร์ฟหน้าเว็บและ reverse proxy ไปยัง API service
COPY nginx.conf /etc/nginx/conf.d/default.conf
# ระบุว่า container ให้บริการเว็บผ่านพอร์ต 80
EXPOSE 80
# รัน nginx แบบ foreground เพื่อให้เป็น process หลักของ container
CMD ["nginx","-g","daemon off;"]
