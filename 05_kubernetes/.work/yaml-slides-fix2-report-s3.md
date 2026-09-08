แก้เสร็จแล้วใน [Kubernetes_Session3_Slides.html](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/Kubernetes_Session3_Slides.html:230)

หน้าที่แก้:

- หน้า 4: ขยายไดอะแกรมเป็นภาพหลักกว้าง 748px และย่อ YAML เหลือ 6 บรรทัด
- หน้า 6: ย่อ YAML เหลือ 16 บรรทัด และแก้หัวข้อไม่ให้ล้น
- หน้า 17, 29, 41, 63: ลดเหลือ 4 การ์ด จัดคอลัมน์สมดุล และปรับข้อความตาม feedback
- ตรวจ footer หน้า YAML ทั้งหมด 11 หน้าแล้ว ทุก anchor มีจริงใน `YAML_Guide.md`
- ตรวจข้อเท็จจริงกับ manifest และ `kubectl explain` ใน `devtools-k8s-verify`

ผล `check-slides.js`: ผ่าน

- 90 หน้า
- 47 ภาพ ไม่มีภาพเสียหรือภาพขาด alt
- ไม่มี external refs/imports
- Navigation และ hash ผ่านครบ
- ไม่มี page errors
- เปิดตรวจภาพทุกหน้าที่แก้แล้ว
- ภาพ render อยู่ที่ [.work/slide-shots-s3](/root/workspace/DevTools/05_kubernetes/.work/slide-shots-s3)

ข้อที่ไม่แก้: ไม่มี feedback ที่ค้างอยู่ ส่วนหน้า 5, 28, 40, 53 และ 73 คงเดิมเพราะรายงานรอบก่อนให้คะแนนครบ 5 ทุกหมวดแล้ว