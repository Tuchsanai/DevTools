แก้ไฟล์ [Kubernetes_Session1_Slides.html](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/Kubernetes_Session1_Slides.html) แล้ว

- หน้า diagram/topology: 10, 13, 19, 22, 28, 31, 38, 41, 48, 51, 58, 61, 71, 74
- หน้า screenshot: 33, 43, 53, 63–66, 76–77
- ครอป PNG ทั้ง 9 ภาพด้วย Pillow ตาม box `(264, 0, 1280, 300)` และฝังด้วย key เดิม
- ปรับ viewBox ของ SVG ที่ฝังจาก bbox + padding 20px โดยไม่แก้ไฟล์ต้นฉบับใน `slides_assets/`
- ตรวจภาพ render ทุกหน้าที่แก้แล้ว ไม่พบ sidebar หรือเนื้อหาถูกตัด

ผลตรวจรอบสุดท้าย:

- 81 slides, 42 images
- ขนาด 5.6 MB
- `brokenImages: []`
- `externalRefs: []`
- navigation ผ่านครบ
- `labFoldersReferenced: 7`
- `pageErrors: []`

ข้อจำกัดที่เหลือ: ไดอะแกรมหนาแน่นหน้า 10, 13 และ 74 ยังมีข้อความเล็กสุดประมาณ 12.6–13.3px แม้ครอปถึง bbox แล้ว การขยายต่อจำเป็นต้องตัดองค์ประกอบ topology หรือแยกเป็นหน้า zoom เพิ่มเติม.