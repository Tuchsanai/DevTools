เสร็จครบแล้ว ใช้ built-in `image_gen` สร้างทีละภาพตาม skill `imagegen` และนับรอบ cleanup เป็นรอบ gen ด้วย

| ไฟล์ | KB | ความสว่าง | รอบ gen | สื่อหัวข้อ |
|---|---:|---:|---:|---|
| cover-s1.jpg | 159.8 | 0.5474 | 3 | เครนจัดตู้สีน้ำเงินบนเรือ สื่อ Kubernetes ที่ orchestrate container |
| lab001-scene.jpg | 192.1 | 0.4110 | 1 | เซิร์ฟเวอร์ไฟแดงและสายหลุด สื่อเหตุขัดข้องที่ต้องกู้คืน |
| lab002-scene.jpg | 146.2 | 0.7641 | 2 | มือใช้จอหน้ากรงสามโซน สื่อ kubectl และ namespace |
| lab003-scene.jpg | 126.5 | 0.5649 | 2 | ตู้หลักกับ sidecar ถูกยกบนแท่นเดียวกัน สื่อ Pod |
| lab004-scene.jpg | 119.7 | 0.4586 | 2 | กริดสามช่องตรงกับตู้จริงสามตู้ สื่อ declarative desired state |
| lab005-scene.jpg | 152.4 | 0.4887 | 1 | เครนเลือกตู้จากแถบสี สื่อ labels และ selectors |
| lab006-scene.jpg | 171.8 | 0.5219 | 2 | เครนเติมตู้ลงช่องว่าง สื่อ self-healing |
| lab007-scene.jpg | 175.9 | 0.4896 | 2 | ตู้สีน้ำเงินและเขียวถูกเปลี่ยนทีละใบ สื่อ rolling update |
| concept-s1-1.jpg | 145.5 | 0.7566 | 2 | กราฟตกและไฟแดงใน NOC ไร้คน สื่อการ restart อัตโนมัติ |
| concept-s1-2.jpg | 134.1 | 0.8120 | 3 | แร็คสี่ตู้ต่อสวิตช์เดียว สื่อหลาย Node ใน cluster |
| concept-s1-3.jpg | 144.7 | 0.5097 | 3 | หอควบคุมดูแลเครนหลายตัว สื่อ control plane และ worker |
| concept-s1-4.jpg | 115.9 | 0.6663 | 2 | ตู้สองใบแชร์แท่น สาย และท่อ สื่อ container ใน Pod |
| concept-s1-5.jpg | 129.5 | 0.4780 | 1 | จอมีสามช่องแต่ลานมีสองตู้ สื่อ desired เทียบ actual |
| concept-s1-6.jpg | 110.9 | 0.4626 | 1 | spreader จับเฉพาะตู้แถบน้ำเงิน สื่อ selector จับคู่ label |
| concept-s1-7.jpg | 138.1 | 0.4894 | 2 | ตู้เดิมกลับเข้าช่องและตู้ใหม่ที่บุบถูกแยกออก สื่อ rollback |

ผลตรวจ:

- จำนวนหน้า: `90 → 90`
- `brokenImages: 0`
- `externalRefs: 0`
- `externalImports: 0`
- `pageErrors: 0`
- ตรวจภาพหน้าปก หน้าคั่นทั้ง 7 แล็บ หน้า concept ทั้ง 7 หน้า หน้า 4 และหน้าปิดแล้ว ไม่พบภาพหายหรือข้อความล้น
- ฝัง base64 ครบ 15 KEY และตรวจว่า binary ตรงกับ JPG ส่งมอบทุกไฟล์
- ไฟล์ส่งมอบมีเฉพาะ JPG 15 ไฟล์กับ `photos.md`

แก้ข้อความหน้า concept: `9, 18, 29, 42, 52, 64, 79`

ไฟล์สำคัญ:

- [สไลด์ที่แก้แล้ว](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/Kubernetes_Session1_Slides.html)
- [photos.md](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets/photos/photos.md)
- [ต้นฉบับ PNG](/root/workspace/DevTools/05_kubernetes/.work/photos-src2-s1/)
- [สำรองภาพชุดเดิม](/root/workspace/DevTools/05_kubernetes/.work/photos-v1-backup/s1/)

ปัญหาที่แก้ไม่ได้: ไม่มี