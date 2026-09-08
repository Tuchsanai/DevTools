สร้างและตรวจเรียบร้อยแล้ว ขนาด SVG 1540×900 จำนวน 6 ไฟล์:

- [Session 1 — SVG](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets/d09-yaml-anatomy.svg)
- [Session 1 — Excalidraw](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets/scenes/d09-yaml-anatomy.excalidraw)
- [Session 2 — SVG](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/slides_assets/d09-yaml-anatomy.svg)
- [Session 2 — Excalidraw](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/slides_assets/scenes/d09-yaml-anatomy.excalidraw)
- [Session 3 — SVG](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/slides_assets/d09-yaml-anatomy.svg)
- [Session 3 — Excalidraw](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/slides_assets/scenes/d09-yaml-anatomy.excalidraw)

ผลตรวจด้วยตาจากภาพที่ render ด้วย `shot.js`:

- A: เส้นหลัก 2px ชัดและสีตัดพื้น — ผ่าน 5/5
- B: เส้นตรง/หักฉาก ผูกกับ element และแตะกึ่งกลางขอบ — ผ่าน 5/5
- C: ตัวอักษรไม่ทับกัน; YAML monospace 20px — ผ่าน 5/5
- D: การ์ดขนาดเท่ากัน มีช่องว่างรอบกล่องและช่องเดินเส้นเพียงพอ — ผ่าน 5/5
- ตรวจยืนยันว่า YAML ใน scene ตรงกับ `01-pod.yaml` และสำเนาทั้งสามชุดมี checksum ตรงกัน

ข้อจำกัด: `status` ไม่มีอยู่ใน manifest ต้นฉบับ จึงแยกเป็นส่วนสีเทาด้านล่าง พร้อมระบุว่า API server เติมหลังสร้าง object เพื่อไม่ให้เข้าใจว่าเป็นบรรทัดที่ผู้ใช้ต้องเขียนเอง

ปิด canvas ที่พอร์ต 8893 แล้วครับ