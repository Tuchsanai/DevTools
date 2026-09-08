ปรับเอกสารครั้งที่ 1 เป็นภาษาวิชาการแล้ว โดยรักษา code block, ผลลัพธ์, inline code, link target, รูปภาพ และจำนวนหัวข้อไว้ครบถ้วน

| ไฟล์ | บรรทัดก่อน→หลัง | HARD ก่อน→หลัง | SOFT ที่เหลือ |
|---|---:|---:|---|
| [README ระดับครั้ง](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/README.md) | 94→94 | 11→0 | `ลอง` 2: อยู่ภายในคำวิชาการ “ทดลอง” |
| [YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/YAML_Guide.md) | 297→297 | 13→0 | 0 |
| [LAB 001](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/001-kubernetes-introduction/README.md) | 414→414 | 40→0 | `ลอง` 6: อยู่ภายใน “ทดลอง/จำลอง” |
| [LAB 002](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/002-kubectl-and-namespace/README.md) | 399→399 | 39→0 | `ลอง` 5: อยู่ภายใน “ทดลอง/จำลอง” |
| [LAB 003](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit/README.md) | 442→442 | 34→0 | `ลอง` 5: อยู่ภายใน “ทดลอง/จำลอง” |
| [LAB 004](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/004-declarative-yaml/README.md) | 437→437 | 33→0 | `ลอง` 8: อยู่ภายใน “ทดลอง/จำลอง” |
| [LAB 005](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/005-labels-the-glue/README.md) | 418→418 | 30→0 | `ลอง` 3: อยู่ภายใน “ทดลอง/จำลอง” |
| [LAB 006](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/006-desired-state-and-self-healing/README.md) | 439→439 | 23→0 | `ลอง` 3: อยู่ภายใน “ทดลอง/จำลอง” |
| [LAB 007](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/007-deployment-manages-change/README.md) | 450→450 | 30→0 | `ลอง` 3: อยู่ภายใน “ทดลอง/จำลอง” |
| [photos.md](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/slides_assets/photos/photos.md) | 15→15 | 11→0 | 0 |
| [lab-outline.md](/root/workspace/DevTools/05_kubernetes/.work/lab-outline.md) | 447→447 | เฉพาะ 7 บรรทัดที่อนุญาต: 1→0 | เฉพาะ 7 บรรทัด: 0 |

ผลการตรวจ:

- `check-lang-diff.py`: OK ครบ 10/10 ไฟล์ที่กำหนด, exit 0
- `check-register.py`: เอกสารทั้ง 10 ไฟล์ HARD=0, exit 0; บรรทัดแนวคิดหลักทั้ง 7 บรรทัดใน `lab-outline.md` มี HARD=0 และ SOFT=0
- `check-readme.py`: exit 0, 0 FAIL
- `check-yaml-teaching.py`: exit 0, `YAML-TEACHING FAILS = 0`
- ตรวจ inline code เพิ่มเติมเทียบสำเนาก่อนแก้: ตรงกันครบ 10/10 ไฟล์
- จำนวนบรรทัดทุกไฟล์คงเดิม จึงอยู่ภายในเกณฑ์ ±10%

ตัวอย่างก่อนและหลัง:

1. “ใครคอยทำให้ระบบตรงกับที่เราสั่ง?” → “กลไกการรักษาสภาพของระบบให้สอดคล้องกับข้อกำหนด”
2. “Kubernetes คือผู้ดูแลที่คอยรันแอป...” → “Kubernetes คือระบบกำกับดูแลที่ทำให้การทำงานของแอปสอดคล้องกับสภาพที่กำหนดไว้...”
3. “Pod ไม่ได้หาย เราเพียงกำลังมองคนละห้อง” → “Pod ยังคงอยู่ แต่คำสั่งกำลังตรวจสอบคนละ namespace”
4. “เราไม่ได้สั่งว่า ‘ทำอะไร’...” → “ผู้ใช้กำหนดสภาพที่ต้องการแทนการระบุขั้นตอนดำเนินงาน...”
5. “label คือกาวที่ทำให้ object ต่าง ๆ รู้จักกัน” → “label เป็นกลไกเชื่อมโยง object โดยไม่ต้องอ้างอิงชื่อหรือ IP ... โดยตรง”
6. “ใครจะ restart ตอนตีสาม” → “กลไก restart อัตโนมัตินอกเวลาทำการ”

ข้อจำกัดที่รักษาไว้:

- ไม่แก้สไลด์ เนื่องจากระบุว่ามีผู้ดำเนินการส่วนนี้แล้ว
- ไม่แก้ไฟล์ `.yaml`, `.sh`, image, app หรือโฟลเดอร์ครั้งอื่น
- ใน `lab-outline.md` แก้เฉพาะ 7 บรรทัดแนวคิดหลักตามคำสั่ง โดยข้อความตรงกับบรรทัด 💡 ใน README แล้ว
- ด้วยเหตุนี้ หากเรียก `check-register.py` กับ `lab-outline.md` ทั้งไฟล์ จะยังพบ HARD=167 และ SOFT=116 จากอีก 440 บรรทัดที่ห้ามแก้ ข้อกำหนด “แก้เฉพาะ 7 บรรทัด” จึงขัดกับข้อกำหนด “HARD=0 ทั้งไฟล์”; ผล HARD=0/SOFT=0 ข้างต้นเป็นผลตรวจเฉพาะส่วนที่ได้รับอนุญาตให้แก้
- ไม่ได้สร้างไฟล์รายงานเพิ่มเติมครับ