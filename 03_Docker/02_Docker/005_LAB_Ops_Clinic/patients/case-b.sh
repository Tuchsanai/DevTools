#!/bin/sh
# คนไข้ B — "Up แต่เว็บเปิดไม่ได้"
# ลืมใส่ -p → แอปฟังอยู่ใน container จริง แต่ไม่มีประตูจากเครื่อง host เข้าไป
docker rm -f patient-b >/dev/null 2>&1
docker run -d --name patient-b ops-clinic:1.0
