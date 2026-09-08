ดำเนินการครบและฝังกลับใน [Kubernetes_Session3_Slides.html](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/Kubernetes_Session3_Slides.html) แล้ว โดยใช้ built-in `imagegen`

| ภาพที่สร้างใหม่ | ขนาด | ความสว่าง | รอบ | องค์ประกอบที่เปลี่ยน |
|---|---:|---:|---:|---|
| `cover-s3.jpg` | 227.8 KB | 0.5574 | 3 | ท่าเรือมุมสูง ถนนบรรจบประตูเดียวทางขวา ผิวเรือ/ตู้/เครนไม่มี stencil |
| `lab017-scene.jpg` | 163.2 KB | 0.5093 | 3 | ไฟเบอร์น้ำเงินเข้าผนังจุดเดียว → patch panel เดียว → แตกไปหลายแร็ค |
| `lab019-scene.jpg` | 162.1 KB | 0.6361 | 2 | blade สลับฝาปิดน้ำเงิน มิเตอร์เดียวใกล้เส้นแดง ลบ glyph บนอุปกรณ์ |
| `concept-s3-2.jpg` | 121.5 KB | 0.6621 | 1 | ซ้ายสามเครื่องช่องไดรฟ์ว่าง ขวา storage ไดรฟ์เต็มพร้อมไฟเขียว |
| `concept-s3-3.jpg` | 205.0 KB | 0.4348 | 2 | มุมดาดฟ้าเรือ ตู้ฟ้า/เขียวปนครึ่งทาง เครนยกตู้เขียว ผิวเรียบไร้ stencil |

ทุกไฟล์เป็น JPEG quality 88, 1280×720 และต่ำกว่า 350 KB ต้นฉบับ PNG ถูกทับเฉพาะห้าชื่อที่กำหนดใน `.work/photos-src2-s3/`

ข้อความที่แก้:

- alt หน้า 1/32, 20, 30, 44 และ 54
- `<em>` และ “มองภาพนี้:” หน้า 20, 32 และ 44
- อัปเดตห้าแถวใน [photos.md](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/slides_assets/photos/photos.md) ให้ตรงกับ alt

ผลกรอบและการจัดภาพ:

- แก้กรอบ `concept_s3_K` หน้า 9, 20, 44, 56, 66 และ 76 เป็น 16:9 พร้อม `object-fit:cover`
- ตรวจ PNG หน้าแนวคิดครบทั้ง 7 หน้า: 9, 20, 32, 44, 56, 66, 76 — ภาพหกกรอบที่อยู่ในขอบเขตเต็มกรอบ ไม่ล้น และข้อความขวาครบ
- เพิ่ม `object-position:right center` ให้หน้าคั่น 015–021
- เลื่อนจุดโฟกัสหน้า 7, 18, 42, 64 และ 74 ไปทางขวา โดย PNG ยืนยันว่ามือเสียบสาย, storage, เครื่องที่กำลังเปลี่ยน, บล็อกแดง และ request path มองเห็นชัดขึ้น
- หน้า 30 และ 54 มีจุดโฟกัสอยู่ขวาแล้ว จึงไม่เพิ่มการเลื่อน
- กรอบหน้า 32 ไม่เปลี่ยน เพราะห่อ `cover_s3` ไม่ใช่ `concept_s3_K` ตามขอบเขตที่ระบุ

ผล `check-slides`:

- slides: 90 เท่าเดิม
- images: 47
- brokenImages: 0
- externalRefs/imports: 0
- imagesWithoutAlt: 0
- pageErrors: 0

ไม่มี feedback ข้อใดถูกละไว้ ภาพอีก 10 ใบ, CSS กลาง, screenshot/diagram และโฟลเดอร์ครั้งอื่นไม่ได้แก้ไขครับ