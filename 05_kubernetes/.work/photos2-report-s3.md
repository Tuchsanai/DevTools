สร้างและฝังภาพใหม่ครบ 15 ภาพแล้ว โดยใช้ built-in `image_gen` ตาม prompt set ใน `photo-spec-v2.md` และปรับรอบใหม่เมื่อภาพมืดหรือมีองค์ประกอบไม่ผ่านเกณฑ์

| ไฟล์ | KB | ความสว่าง | รอบที่ gen | สื่อหัวข้อ |
|---|---:|---:|---:|---|
| cover-s3.jpg | 223.3 | 0.6476 | 2 | ท่าเรือและลานคอนเทนเนอร์ที่รวมถนนสู่ประตูเดียว สื่อระบบครบวงจรผ่าน Ingress |
| lab015-scene.jpg | 199.7 | 0.7156 | 2 | แร็คสองชุดเชื่อมผ่านสวิตช์ สื่อหลาย object ที่ประกอบเป็นแอปเดียว |
| lab016-scene.jpg | 144.8 | 0.7883 | 3 | เซิร์ฟเวอร์ช่องว่างเทียบกับฐานข้อมูลและ disk shelf สื่อ stateless กับ stateful |
| lab017-scene.jpg | 210.5 | 0.4141 | 1 | ไฟเบอร์เข้าจุดเดียวแล้วแตกไปหลายแร็ค สื่อ Ingress และ backend routing |
| lab018-scene.jpg | 174.6 | 0.7618 | 2 | เครื่องหนึ่งกำลังถูกเปลี่ยนขณะที่อีกสองเครื่องทำงาน สื่อ rolling update |
| lab019-scene.jpg | 173.7 | 0.5016 | 1 | สล็อต blade ที่จองไว้กับมิเตอร์ใกล้เพดาน สื่อ requests และ limits |
| lab020-scene.jpg | 105.8 | 0.8147 | 2 | จอแสดงบล็อกแดง เหลือง และเขียว สื่ออาการ crash, pending และปกติ |
| lab021-scene.jpg | 127.1 | 0.6369 | 3 | สายเชื่อมผนัง สวิตช์ เว็บ API และ storage สื่อเส้นทาง request ทั้งระบบ |
| concept-s3-1.jpg | 204.7 | 0.7910 | 2 | แร็คสี่หน้าที่เชื่อมกัน สื่อหลาย object ที่ร่วมเป็นระบบเดียว |
| concept-s3-2.jpg | 122.6 | 0.7960 | 2 | เซิร์ฟเวอร์ช่องว่างเทียบ storage ไดรฟ์เต็ม สื่อ stateless กับ stateful |
| concept-s3-3.jpg | 186.2 | 0.4815 | 1 | ตู้สีน้ำเงินและเขียวอยู่ร่วมกันระหว่างเปลี่ยน สื่อ rolling update |
| concept-s3-4.jpg | 89.3 | 0.8541 | 2 | พื้นที่สีน้ำเงินกับเส้นเพดานแดงบนมิเตอร์ สื่อ requests กับ limits |
| concept-s3-5.jpg | 253.1 | 0.7541 | 2 | ไฟหน้าเซิร์ฟเวอร์เขียว เหลือง แดง และดับ สื่อการอ่านอาการ |
| concept-s3-6.jpg | 162.7 | 0.7640 | 3 | วิศวกรดูเส้น กราฟแท่ง และ heatmap สื่อ observability หลายมิติ |
| concept-s3-7.jpg | 90.8 | 0.6917 | 3 | สายจากพอร์ตผนังผ่านสวิตช์ถึงเซิร์ฟเวอร์ สื่อ request path |

ทุกไฟล์เป็น JPEG quality 88 ขนาด 1280×720 และไม่เกิน 350 KB

ผล `check-slides`:

- หน้า: 90 เท่าเดิม
- brokenImages: 0
- externalRefs: 0
- pageErrors: 0
- imagesWithoutAlt: 0
- ตรวจ hash แล้ว base64 ทั้ง 15 KEY ตรงกับ JPEG ส่งมอบทุกไฟล์
- เปิดตรวจ PNG ของหน้าปก หน้าคั่น และหน้าแนวคิดที่ใช้ภาพใหม่แล้ว ภาพแสดงครบและข้อความไม่ล้น

หน้าที่แก้ `<h2>` และ “มองภาพนี้”: 9, 20, 32, 44, 56, 66 และ 76  
แก้ alt ของภาพทั้งหมด 16 ตำแหน่ง รวมภาพปกที่ถูกใช้สองหน้า

ไฟล์หลัก:

- [สไลด์ HTML](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/Kubernetes_Session3_Slides.html)
- [photos.md](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/slides_assets/photos/photos.md)
- [ต้นฉบับ PNG](/root/workspace/DevTools/05_kubernetes/.work/photos-src2-s3)
- [ภาพเดิมที่สำรอง](/root/workspace/DevTools/05_kubernetes/.work/photos-v1-backup/s3)

ปัญหาที่แก้ไม่ได้: ไม่มี