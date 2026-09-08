ดำเนินการครบแล้ว: สร้างภาพใหม่ด้วย built-in imagegen ทั้ง 15 ภาพ ฝังลง [สไลด์ครั้งที่ 2](</root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/Kubernetes_Session2_Slides.html>) และตรวจภาพจริงทุกหน้าเป้าหมายแล้ว

| ไฟล์ | KB | ความสว่าง | รอบที่ gen | สื่อหัวข้อ |
|---|---:|---:|---:|---|
| cover-s2.jpg | 167.8 | 0.4410 | 2 | แร็คเซิร์ฟเวอร์ สวิตช์เครือข่าย และดิสก์ สื่อ Networking, Config และ Storage |
| lab008-scene.jpg | 116.7 | 0.7309 | 2 | สายเครือข่ายเดิมหลุดเมื่อเปลี่ยนเซิร์ฟเวอร์ สื่อเหตุผลที่ต้องมี Service |
| lab009-scene.jpg | 177.3 | 0.8183 | 2 | สายภายในกรงกับสายที่ออกสู่ทางเดิน สื่อ ClusterIP เทียบ NodePort |
| lab010-scene.jpg | 119.4 | 0.8079 | 2 | เปลี่ยนการ์ดตั้งค่าบนเครื่องเดิม สื่อ ConfigMap ที่แยก config ออกจาก workload |
| lab011-scene.jpg | 109.8 | 0.7423 | 2 | กุญแจฮาร์ดแวร์กับกรงล็อก สื่อ Secret และการควบคุมสิทธิ์ |
| lab012-scene.jpg | 123.3 | 0.8284 | 2 | เซิร์ฟเวอร์ใหม่ไม่มีไดรฟ์ของเครื่องเดิม สื่อข้อมูลที่หายเมื่อ Pod ถูกแทนที่ |
| lab013-scene.jpg | 138.9 | 0.7441 | 2 | แร็ค storage ภายนอกเชื่อมกับ compute สื่อ Persistent Storage ผ่าน PVC |
| lab014-scene.jpg | 80.5 | 0.7853 | 3 | เซิร์ฟเวอร์เปิดอยู่แต่พอร์ตหนึ่งไม่พร้อม สื่อ Running ไม่เท่ากับ Ready |
| concept-s2-1.jpg | 146.5 | 0.5142 | 1 | พอร์ตเดียวกระจายสายไปหลายเซิร์ฟเวอร์ สื่อ Service endpoint ที่คงที่ |
| concept-s2-2.jpg | 139.2 | 0.8052 | 2 | สายภายในกับทางเชื่อมภายนอก สื่อขอบเขต ClusterIP และ NodePort |
| concept-s2-3.jpg | 141.0 | 0.4514 | 1 | สลับการ์ด config ขณะเครื่องเดิมยังทำงาน สื่อการเปลี่ยน ConfigMap |
| concept-s2-4.jpg | 140.8 | 0.7336 | 2 | บัตรผ่านกับประตูกรงล็อก สื่อการจำกัดสิทธิ์เข้าถึง Secret |
| concept-s2-5.jpg | 77.0 | 0.8166 | 2 | ดึงไดรฟ์ออกจากเซิร์ฟเวอร์เก่า สื่อ ephemeral container storage |
| concept-s2-6.jpg | 118.9 | 0.8189 | 3 | แร็ค storage แยกจากเครื่องคำนวณ สื่อ PVC ที่อยู่นอก Pod |
| concept-s2-7.jpg | 114.3 | 0.8040 | 2 | สวิตช์ปิดพอร์ตของเครื่องที่ไม่พร้อม สื่อ readiness ตัด Pod ออกจากทราฟฟิก |

ผลตรวจ `check-slides`:

- จำนวนหน้า: **88 เท่าเดิม**
- `brokenImages`: **0**
- `externalRefs`: **0**
- `pageErrors`: **0**
- `imagesWithoutAlt`: **0**
- เปิดผ่าน `file://` ได้ครบ และ base64 ทั้ง 15 รายการตรงกับ JPEG แบบ byte-for-byte

หน้าที่แก้ข้อความอุปมา: **12, 23, 33, 44, 55, 67 และ 78** ครอบคลุม LAB 008–014 โดยแก้เฉพาะหัวข้ออุปมาและประโยค “มองภาพนี้”

ไฟล์ประกอบ:

- [photos.md](</root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/slides_assets/photos/photos.md>)
- [PNG ต้นฉบับ](</root/workspace/DevTools/05_kubernetes/.work/photos-src2-s2/>)
- [ภาพเดิมที่สำรองไว้](</root/workspace/DevTools/05_kubernetes/.work/photos-v1-backup/s2/>)
- [ภาพตรวจหน้าสไลด์](</root/workspace/DevTools/05_kubernetes/.work/slide-shots2-s2/>)

ปัญหาที่แก้ไม่ได้: **ไม่มี**