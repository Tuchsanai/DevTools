แก้ไฟล์ [Kubernetes_Session2_Slides.html](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/Kubernetes_Session2_Slides.html) เรียบร้อย

- หน้า screenshot: 15–17, 27, 37–38, 48–49, 59–61, 71–72, 82–83
- หน้า topology: 13, 25, 35, 46, 57, 69, 80
- ครอปจากต้นฉบับด้วย Pillow ที่ `x=264` และตรวจตรงกันระดับพิกเซลครบ 15 ภาพ
- ปรับ viewBox เฉพาะ SVG ที่ฝังในสไลด์ครบ 7 ภาพ พร้อม padding 20 px; ไม่แก้ไฟล์ใน `slides_assets/`
- เปิดตรวจหน้าที่แก้ครบทั้งหมดแล้ว

ผล `check-slides.js` รอบสุดท้าย:

- 87 slides, 47 images
- ขนาด 5.3 MB
- `brokenImages: []`
- `externalRefs: []`
- navigation ผ่านครบ
- `labFoldersReferenced: 7`
- `pageErrors: []`

ข้อจำกัดที่เหลือ: หน้า 71–72 ต้องเก็บภาพต้นฉบับสูง 1614 px ทั้งภาพเพื่อไม่ตัด ticket #9 ทำให้รายละเอียดเล็กกว่าหน้าอื่น แต่มีการ์ด `#9` ขยายแยกด้านขวาให้อ่านหลักฐานสำคัญได้ชัดเจน ไม่มีข้อจำกัดเชิงเทคนิคที่เหลือครับ