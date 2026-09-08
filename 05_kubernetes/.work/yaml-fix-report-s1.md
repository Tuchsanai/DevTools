แก้ครบตาม reviewer และตรวจด้วย Kubernetes v1.36.4 แล้ว

| ไฟล์ | รายการที่แก้ (บรรทัด) | ยังไม่แก้และเหตุผล |
|---|---|---|
| [YAML_Guide.md](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/YAML_Guide.md) | quote/error จริงและ client/server dry-run (46–62), YAML Pod ให้ตรงไฟล์ (88), `containerPort` required (103), Pod immutable fields (110), ReplicaSet/error LAB 006 (151), Deployment/change-cause/immutable selector (168, 198), fieldRef error (221–224), namespace error (238) | ไม่เติมเลขหัวข้อที่บรรทัด 6, 64, 114 เพราะ reviewer อนุญาตและจะทำให้ anchor ทุก README เปลี่ยน |
| [LAB 003 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/003-pod-the-smallest-unit/README.md) | ระบุชื่อไฟล์ต้นทางของ YAML block (232) | — |
| [LAB 004 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/004-declarative-yaml/README.md) | กำกับตัวอย่าง `"5432"`, แก้คำอธิบาย annotation (126), แยก client/server dry-run (130) | — |
| [LAB 005 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/005-labels-the-glue/README.md) | เติมข้อความ `No resources found in lab005 namespace.` ให้ครบ (119) | — |
| [LAB 006 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/006-desired-state-and-self-healing/README.md) | ใช้ selector error จริงและอธิบายอาการ v1/v2 ปนตามการทดลอง (123) | — |
| [LAB 007 README](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/007-deployment-manages-change/README.md) | เติม error `` `selector` does not match template `labels` `` (132) | — |
| LAB 001–002 README | ไม่เปลี่ยน | Reviewer ระบุว่าผ่านแล้ว |

หัวข้อทบทวนที่เพิ่ม: ไม่มี ตามข้อกำหนดว่าครั้งที่ 1 ไม่ต้องมีหัวข้อทบทวน

ผลตรวจ:

- `check-yaml-teaching.py`: **0 FAIL**
- `check-readme.py`: **0 FAIL**, 6 WARN เรื่องเป้าหมายแนะนำ 200–400 บรรทัด
- README ทุกไฟล์ไม่เกินข้อกำหนด 450 บรรทัด; สูงสุด LAB 007 เท่ากับ 450 บรรทัด
- ตรวจ field/default ด้วย `kubectl explain` บน server v1.36.4
- `devtools-k8s-verify` ยัง healthy และไม่ได้สร้างหรือลบ container
- ไม่ได้สร้างไฟล์รายงานเพิ่ม