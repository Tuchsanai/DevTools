อัปเดตไฟล์ [Kubernetes_Session1_Slides.html](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/Kubernetes_Session1_Slides.html) แล้ว

หน้าที่เพิ่ม:

- 35 — YAML คืออะไร
- 36 — โครง object พร้อม `d09-yaml-anatomy.svg`
- 37–38 — Pod
- 59 — ReplicaSet + selector/labels
- 60 — Service + Ingress แบบทบทวน
- 74 — Deployment + strategy/change-cause
- 75 — Deployment + Downward API `fieldRef`

รวมทั้งหมด: 89 หน้า

ผล `check-slides.js`:

- Exit code: 0
- ขนาด: 5.7 MB
- `brokenImages`: ว่าง
- `externalRefs`: ว่าง
- `externalImports`: 0
- Navigation ครบถึงหน้า 89
- `labFoldersReferenced`: ครบ 7
- `pageErrors`: ว่าง
- ตรวจ PNG ของหน้าที่เพิ่มทั้ง 8 หน้าแล้ว: ไม่ล้น ไม่ทับ และ YAML ใช้ตัวอักษร 18px ขึ้นไป

ข้อจำกัด:

- Service/Ingress สอนไว้เพียงระดับ “ประตูสำเร็จรูป” ตามสเปก
- `strategy`, `minReadySeconds` และ `revisionHistoryLimit` ไม่มีใน manifest ต้นทาง จึงแสดงเฉพาะคำอธิบายค่า default ในการ์ด ไม่แต่ง YAML เพิ่ม
- สารบัญเดิมไม่มีเลขหน้าตายตัว และ navigation/overview คำนวณจาก DOM อัตโนมัติ จึงไม่ต้องแก้หน้าเดิมอื่น ๆ