ปรับภาษาวิชาการครบทุกไฟล์ตามขอบเขต พร้อมคงโค้ด ผลลัพธ์ ลิงก์ รูปภาพ และจำนวนบรรทัดเดิม

| ไฟล์ | บรรทัดก่อน→หลัง | HARD ก่อน→หลัง | SOFT ที่เหลือ + เหตุผล |
|---|---:|---:|---|
| [README ระดับครั้ง](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/README.md) | 97→97 | 12→0 | 2 — อยู่ในคำทางการ “ทดลอง/จำลอง” |
| [YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/YAML_Guide.md) | 374→374 | 16→0 | 1 — “ไฟล์ทดลอง” |
| [LAB 015](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/015-assembling-a-real-application/README.md) | 422→422 | 34→0 | 6 — อยู่ใน “ทดลอง/จำลอง” |
| [LAB 016](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/016-adding-a-database/README.md) | 401→401 | 36→0 | 8 — อยู่ใน “ทดลอง/จำลอง” |
| [LAB 017](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/017-ingress-the-front-door/README.md) | 410→410 | 30→0 | 6 — อยู่ใน “ทดลอง/จำลอง” |
| [LAB 018](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/018-updating-without-downtime/README.md) | 425→425 | 30→0 | 7 — อยู่ใน “ทดลอง/จำลอง” |
| [LAB 019](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/019-telling-kubernetes-what-you-need/README.md) | 437→437 | 36→0 | 5 — อยู่ใน “ทดลอง/จำลอง” |
| [LAB 020](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/020-reading-the-symptoms/README.md) | 434→434 | 67→0 | 4 — อยู่ใน “ทดลอง/จำลอง” |
| [LAB 021](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/021-the-big-picture/README.md) | 424→424 | 33→0 | 5 — อยู่ใน “ทดลอง/จำลอง” |
| [photos.md](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/slides_assets/photos/photos.md) | 15→15 | 7→0 | 0 |
| [lab-outline.md](/root/workspace/DevTools/05_kubernetes/.work/lab-outline.md) | 447→447 | 171→165 | 116 — เป็นข้อความเดิมนอก 7 บรรทัดที่อนุญาตให้แก้; 7 บรรทัดของ LAB 015–021 ตรวจแยกได้ HARD=0, SOFT=0 |

ผลการตรวจ:

- `check-lang-diff.py`: OK ทั้ง 10 ไฟล์, exit 0
- `check-register.py`: เอกสารทั้ง 10 ไฟล์ HARD=0; เมื่อรวม `lab-outline.md` exit 99 เพราะข้อความเดิมนอกขอบเขตยังมี HARD=165
- `check-readme.py`: 0 FAIL, exit 0
- `check-yaml-teaching.py`: `YAML-TEACHING FAILS = 0`, exit 0
- Anchor ใหม่ `#5-manifest-ที่มีข้อผิดพลาดโดยเจตนาของปฏิบัติการ-020` ผ่านการตรวจทุกลิงก์

ตัวอย่างก่อน/หลัง:

1. “จะเปิดประตูเดียว อัปเดตโดยผู้ใช้ไม่สะดุด…” → “การกำหนดทางเข้าเพียงจุดเดียว การอัปเดตโดยไม่กระทบผู้ใช้…”
2. `## 5. manifest ที่พังโดยตั้งใจของแล็บ 020` → `## 5. manifest ที่มีข้อผิดพลาดโดยเจตนาของปฏิบัติการ 020`
3. “ต่อ object ให้กลายเป็นระบบ” → “การประกอบ object ให้เป็นระบบแอปพลิเคชัน”
4. “ส่วนที่มีข้อมูลต้องการการดูแลต่างจากส่วนที่ไม่มีข้อมูล” → “องค์ประกอบที่บันทึกข้อมูลต้องใช้แนวทางการดูแลแตกต่างจากองค์ประกอบที่ไม่บันทึกข้อมูล”
5. “Ingress คือประตูหน้าบ้าน…” → “Ingress ทำหน้าที่เป็นทางเข้าหลัก…”
6. “หา layer ที่พังก่อนรีบแก้” → “การวิเคราะห์อาการเพื่อระบุ layer ที่ขัดข้อง”

ไม่ได้แก้ไฟล์ `.yaml`, `.sh`, รูปภาพ, สไลด์, `app/` หรือโฟลเดอร์ครั้งอื่นตามข้อห้าม และไม่ได้แก้ข้อความอื่นใน `lab-outline.md` นอก LAB 015–021 ทั้งนี้ตรวจพบการเปลี่ยนแปลง LAB 001–014 ในไฟล์ดังกล่าวจากงานอื่นระหว่างดำเนินการ จึงเก็บรักษาไว้โดยไม่ย้อนทับ หากต้องการให้ `check-register.py` ผ่านทั้ง `lab-outline.md` จำเป็นต้องอนุญาตให้ปรับร้อยแก้วนอก 7 บรรทัดเพิ่มเติมก่อนครับ