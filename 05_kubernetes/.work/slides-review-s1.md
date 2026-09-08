ตรวจและแก้ไฟล์ [Kubernetes_Session1_Slides.html](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/Kubernetes_Session1_Slides.html) เรียบร้อย ยืนยันว่า `cyolo1` เปิดดู PNG จริงครบ `s001.png–s065.png` และตรวจซ้ำทุกหน้าที่แก้หลัง render

| หน้า | ถูกต้อง/ตัวอักษร/เลย์เอาต์/สวยงาม/เทคนิค | ปัญหา | แก้แล้ว? |
|---:|---|---|:---:|
| 3 | 5/2/3/4/5 | ไดอะแกรมเล็กและซ้ำกับการ์ด | ✓ |
| 5 | 5/3/3/4/5 | ตารางและไดอะแกรมแย่งพื้นที่ | ✓ |
| 6 | 5/2/4/4/5 | คำสั่งมีขนาดเพียง 10.5px | ✓ |
| 10 | 5/3/3/4/5 | ไดอะแกรมสถาปัตยกรรมเล็ก | ✓ |
| 13–14 | 5/2/3/4/5 | Topology และ terminal เล็ก | ✓ |
| 18 | 5/3/3/4/5 | รายละเอียด Namespace เล็ก | ✓ |
| 21–22 | 5/2/3/4/5 | Expected output อ่านยาก | ✓ |
| 26 | 5/3/3/4/5 | ข้อความในไดอะแกรม Pod เล็ก | ✓ |
| 29–30 | 5/2/3/4/5 | Command/output และ screenshot เล็ก | ✓ |
| 34 | 5/3/3/4/5 | Reconciliation loop เล็ก | ✓ |
| 37–38 | 5/2/3/4/5 | Terminal และหลักฐานเล็ก | ✓ |
| 42 | 5/3/3/4/5 | ไดอะแกรม label/selector เล็ก | ✓ |
| 45–46 | 5/2/3/4/5 | ผลรันยาวและตัวเล็ก | ✓ |
| 50 | 5/3/3/4/5 | Deployment hierarchy เล็ก | ✓ |
| 53 | 5/2/3/4/5 | Topology และผลรันเล็ก | ✓ |
| 54 | 5/2/2/3/5 | ภาพหลักฐาน 4 ภาพเล็กและ output ล้น | ✓ |
| 58 | 5/3/3/4/5 | RollingUpdate diagram เล็ก | ✓ |
| 61–62 | 5/2/3/4/5 | Rollout output และ screenshots เล็ก | ✓ |

แก้ทั้งหมด: **24 หน้า** โดยขยาย command/expected output, เพิ่มพื้นที่ไดอะแกรม, ลดองค์ประกอบซ้ำ และปรับสัดส่วนภาพกับเนื้อหา ไม่พบคำสั่ง `curl` ที่ใช้ `localhost:8080` ผิดบริบท

ผล `check-slides.js` หลังแก้:

- Slides: **65**
- ขนาด: **4.5 MB**
- `brokenImages`: `[]`
- `imagesWithoutAlt`: `0`
- `externalRefs`: `[]`
- `externalImports`: `0`
- `pageErrors`: `[]`
- Navigation, overview, help, hash, progress bar, counter และ controls: **ครบ**
- `labFoldersReferenced`: **ครบทั้ง 7 แล็บ**

หน้าที่ยังมีข้อจำกัด: **ไม่มีหน้าที่มีคะแนนหมวดใดต่ำกว่า 4**