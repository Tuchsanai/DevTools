# ผลตรวจแอป (เฟส 4 · yolo1 ตรวจเองบน cluster ของตัวเอง devtools-k8s-verify · 2026-09-02)

| # | เกณฑ์ (orchestration เฟส 4) | ผล | หลักฐาน |
|---|---|---|---|
| 1 | หน้าเว็บแสดงชื่อ Pod/hostname ที่ตอบ | ผ่าน | `/info` ผ่าน Ingress 24 ครั้ง กระจาย 3 Pod (8/11/5) · การ์ดสถานะใน screenshot แสดง Pod + Node + เวลา |
| 2 | /health กับ /ready แยกกัน และ /ready ล้มเมื่อ db ล่ม | ผ่าน | scale db=0 → api READY 0/1, endpoints ว่าง, /api/ready 503 · db กลับ → 1/1 โดยไม่ restart · POST /debug/health → liveness restart (RESTARTS 0→1) |
| 3 | เปลี่ยน env แล้วหน้าเว็บเปลี่ยน | ผ่าน | patch ConfigMap SITE_NAME/THEME=amber + rollout restart → `/info` = amber/ชื่อใหม่ (screenshot yolo1-amber.png) |
| 4 | v1 กับ v2 ต่างกันชัด | ผ่าน | set image v2 → theme emerald + ป้าย v2 โดยไม่ตั้ง env · screenshot v1 น้ำเงิน / v2 เขียวมรกต ต่างกันทั้งแถบข้าง แถบสถานะ กราฟ |
| 5 | ข้อมูล PostgreSQL แสดงบนหน้าเว็บ | ผ่าน | dashboard tickets จาก seed แสดงบนหน้าเว็บ · `/api/dashboard` ผ่าน Ingress คืน JSON |
| 6 | UI สวยพอขึ้นสไลด์ | ผ่าน | UI ของต้นแบบ SkillSpace + การ์ดสถานะ 3 แถวบนสุดทุกหน้า · โหมดเดี่ยว/API ล่ม แสดงสถานะสวยงาม ไม่ error |
| 7 | build ซ้ำจากสภาพสะอาดผ่าน | ผ่าน | dockerd เปล่า → `./build-images.sh` 4 image ผ่านใน 73 วินาที (มี cache ของ base image) |
| 8 | ไม่มี container/volume ค้าง | ผ่าน | `devtools-k8s-app` ของผู้สร้างถูกลบแล้ว · เหลือเฉพาะ `devtools-k8s-verify` ของ yolo1 (ลบตอนจบเฟส 7) |

ข้อทดสอบ 10 ข้อใน app-requirements §5: ผ่าน 10/10 (รอบแรก 7 ข้อล้มเพราะสคริปต์ตรวจอยู่คนละ docker network — ไม่ใช่แอป · รอบสองบน k8s-course-net ผ่านหมด · ข้อ 2 ที่ล้มในรอบสองเป็น race หลัง apply 0-3 วินาที ยืนยันด้วยมือแล้วว่า /api/whoami และ /api/dashboard ผ่าน Ingress คืน JSON + X-Pod-Name)

## สิ่งที่ต้องแก้
ไม่มี — **แอปผ่าน gate และถูกล็อก** ห้ามแก้พฤติกรรมหลังจากนี้ (ถ้าจำเป็นต้องออก tag ใหม่และรันแล็บที่กระทบซ้ำ)

## หมายเหตุสำหรับผู้ทำแล็บ (ไม่ใช่ข้อบกพร่อง)
- หลัง `kubectl apply` ทั้งชุด ให้รอ api Ready + ingress sync ~5 วินาทีก่อน curl `/api/*` ผ่าน Ingress ไม่งั้นเจอ 503 ชั่วครู่ (ใช้เป็นตัวอย่างสอนได้ในแล็บ 014/017)
- `kubectl rollout undo` หลัง `set image` จะเตือนเรื่อง last-applied-configuration — ในแล็บให้ใช้แก้ไฟล์แล้ว apply แทน set image (ตาม outline)
