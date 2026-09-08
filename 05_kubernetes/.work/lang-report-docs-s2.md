ปรับภาษาเอกสารครั้งที่ 2 ครบตามขอบเขตแล้ว โดยจำนวนบรรทัดทุกไฟล์คงเดิม และ `check-lang-diff.py` ยืนยันว่าโค้ด ผลลัพธ์ inline code ลิงก์ และรูปไม่เปลี่ยนแปลง

### สรุปไฟล์

| ไฟล์ | บรรทัดก่อน→หลัง | HARD ก่อน→หลัง | SOFT ที่เหลือและเหตุผล |
|---|---:|---:|---|
| [README ระดับครั้ง](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/README.md) | 94→94 | 13→0 | 0 |
| [YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/YAML_Guide.md) | 298→298 | 8→0 | `ลอง` 2 — อยู่ในคำวิชาการ “การทดลอง” |
| [LAB 008](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/008-why-we-need-service/README.md) | 436→436 | 28→0 | `ลอง` 4 — อยู่ใน “การทดลอง/จำลอง” |
| [LAB 009](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/009-service-types-and-access/README.md) | 432→432 | 27→0 | `ลอง` 4 — อยู่ใน “การทดลอง/จำลอง” |
| [LAB 010](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/010-configmap-separate-config/README.md) | 423→423 | 36→0 | `ลอง` 3 — อยู่ใน “การทดลอง/จำลอง” |
| [LAB 011](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/011-secret-and-why-not-configmap/README.md) | 441→441 | 35→0 | `ลอง` 4 — อยู่ใน “การทดลอง/จำลอง/ค่าทดลอง” |
| [LAB 012](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/012-why-data-disappears/README.md) | 438→438 | 27→0 | `ลอง` 5 — อยู่ใน “การทดลอง/จำลอง/รอบทดลอง” |
| [LAB 013](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/013-persistent-storage-with-pvc/README.md) | 437→437 | 22→0 | `ลอง` 4 — อยู่ใน “การทดลอง/จำลอง” |
| [LAB 014](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/014-running-is-not-ready/README.md) | 446→446 | 24→0 | `ลอง` 6 — อยู่ใน “ทดลอง/การทดลอง/จำลอง” |
| [photos.md](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/slides_assets/photos/photos.md) | 15→15 | 4→0 | 0 |
| [lab-outline.md](/root/workspace/DevTools/05_kubernetes/.work/lab-outline.md) | 447→447 | ทั้งไฟล์ 167→167* | ทั้งไฟล์ 116*; เฉพาะ 7 บรรทัดที่อนุญาตตรวจได้ `HARD=0, SOFT=0` |

`ลอง` เป็นผลจาก linter จับส่วนท้ายของคำว่า “ทดลอง” และ “จำลอง” ซึ่งเป็นการใช้ที่ถูกต้องตามบริบทและเป็นส่วนหนึ่งของหัวข้อบังคับ B1

\* `lab-outline.md` มีภาษาพูดเดิมอยู่นอกปฏิบัติการ 008–014 แต่โจทย์กำหนดให้แก้ “เฉพาะ” 7 บรรทัด `แนวคิดหลัก` จึงไม่ได้แก้ส่วนอื่นเพื่อรักษาขอบเขตที่กำหนด การตรวจทั้งไฟล์จึงไม่อาจเป็น `HARD=0` พร้อมกับข้อห้ามดังกล่าวได้

### ผลสคริปต์ตรวจ

- `check-lang-diff.py`: exit 0 — `OK` ทั้ง 10 ไฟล์ที่ต้องตรวจ
- `check-register.py`: exit 0 — เอกสารเนื้อหาทั้ง 10 ไฟล์มี `HARD=0`; 7 บรรทัดที่แก้ใน outline มี `HARD=0, SOFT=0`
- `check-readme.py`: exit 0 — `0 FAIL` ครบ LAB 008–014
  - มี WARN เรื่องความยาวเกิน 400 บรรทัดทั้ง 7 ไฟล์ แต่เป็นความยาวเดิมและจำนวนบรรทัดไม่เปลี่ยน
- `check-yaml-teaching.py`: exit 0 — `YAML-TEACHING FAILS = 0`

### ตัวอย่างก่อนและหลัง

1. ก่อน: “Pod เปลี่ยนได้ แล้วแอปจะคุยและจำได้อย่างไร?”  
   หลัง: “การสื่อสารและการคงอยู่ของข้อมูลเมื่อ Pod เปลี่ยนแปลง”

2. ก่อน: “ใน Compose เรา publish `ports:` เฉพาะ web”  
   หลัง: “ใน Compose มีการ publish `ports:` เฉพาะ web”

3. ก่อน: “ลองคิดถึง image เป็น ‘กล่องแอปที่ปิดผนึกแล้ว’”  
   หลัง: “image อาจเปรียบได้กับกล่องแอปพลิเคชันที่ปิดผนึกแล้ว”

4. ก่อน: “คนที่มีสิทธิ์อ่าน Secret หรือ exec เข้า Pod จึงอาจเห็นค่าจริง”  
   หลัง: “ผู้ที่มีสิทธิ์อ่าน Secret หรือ exec เข้าสู่ Pod จึงอาจเห็นค่าจริง”

5. ก่อน: “## 6. ลบ db Pod แล้วดูข้อมูลหาย”  
   หลัง: “## 6. การลบ db Pod และการตรวจสอบการสูญหายของข้อมูล”

6. ก่อน: “ทำไม `/ready` ต้อง query db จริง?”  
   หลัง: “เหตุใด `/ready` จึงต้อง query db จริง”

### สิ่งที่ไม่ได้แก้

- ไม่แก้ไฟล์ `.yaml`, `.sh`, images, สไลด์, app หรือโฟลเดอร์ครั้งอื่นตามข้อห้าม
- ไม่แก้ข้อความส่วนอื่นของ `lab-outline.md` เพราะกำหนดให้แก้เฉพาะ 7 บรรทัดแนวคิดหลัก
- ไม่แก้สไลด์ตามคำสั่งว่ามีผู้ดำเนินการรายอื่น
- ไม่มี README ที่อ้าง anchor เดิมของหัวข้อสรุป YAML จึงไม่มีลิงก์ที่ต้องแก้; หัวข้อในคู่มือเปลี่ยนเป็น `## 0. หลักการอ่าน YAML โดยสรุป` ตาม B2 แล้ว
- ไม่ได้สร้างไฟล์ใหม่หรือไฟล์รายงานเพิ่มเติม