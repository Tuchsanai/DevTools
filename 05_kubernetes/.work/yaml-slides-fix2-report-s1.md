แก้ [Kubernetes_Session1_Slides.html](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/Kubernetes_Session1_Slides.html) เรียบร้อย

- หน้าที่แก้/ตรวจ: 25–26, 37–39, 60–61 และ 75–76
- หน้า 37 เพิ่มคำสั่ง `kubectl apply --dry-run=server -f FILE` และแยกความสามารถ client/server ชัดเจน
- หน้า 38–39 แยกหน้าการ์ดกับไดอะแกรมเต็มหน้า
- เติม default, rounding behavior, immutability และปรับสมดุลพื้นที่ตาม feedback ครบ
- ตรวจ footer anchor ทั้งหกค่าแล้ว มีหัวข้อตรงใน `YAML_Guide.md`
- ยืนยันข้อมูลด้วย manifest จริงและ `kubectl explain` จาก server v1.36.4
- เปิดตรวจภาพหลัง render ครบทุกหน้าข้างต้นแล้ว

ผล `check-slides.js`: ผ่าน — 90 หน้า, 5.7 MB, 44 images โหลดครบ, ไม่มี external refs/imports, ไม่มี page errors และ navigation ผ่านทั้งหมด

ข้อที่ไม่แก้: ไม่มี feedback ที่ข้าม; หน้า 38 เลือกแนวทางแยกไดอะแกรมไปหน้า 39 ตามตัวเลือกใน feedback เพื่อคงความอ่านง่ายและไม่เกินเพดาน 90 หน้า