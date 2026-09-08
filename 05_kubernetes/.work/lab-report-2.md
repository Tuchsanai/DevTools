ทำ LAB 004–006 เสร็จสมบูรณ์แล้ว โดยไม่แก้โค้ดใน `app/`

- [LAB 004](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/004-declarative-yaml/README.md) — 393 บรรทัด  
  ผ่าน apply `created/unchanged`, diff และเปลี่ยน v1→v2, immutable-field error, YAML error สองชนิด, แก้กลับ และ Clean Re-run

- [LAB 005](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/005-labels-the-glue/README.md) — 370 บรรทัด  
  ผ่าน selector ทุกแบบ, เปลี่ยน label, ลบเป็นกลุ่ม, ทำ ingress controller `Pending`, อ่าน `FailedScheduling`, คืน label และ Clean Re-run

- [LAB 006](/root/workspace/DevTools/05_kubernetes/01_Session1_Kubernetes_Basics/006-desired-state-and-self-healing/README.md) — 387 บรรทัด  
  ผ่าน ReplicaSet 3/3/3, กระจายครบสาม Pod, self-healing, scale 3→5→1→3, ลบทั้งกลุ่ม, mixed v1/v2, แก้กลับ และ Clean Re-run

ผลตรวจเพิ่มเติม:

- Manifest ปกติผ่าน `kubeconform -strict` ทั้งหมด: 2/2, 3/3 และ 3/3 resources
- `03-pod-typo.yaml` ล้มตามตั้งใจ
- ทุก app image มี `imagePullPolicy: IfNotPresent`
- ทุก bash block มีคำอธิบายและ Expected output ครบ
- Screenshot ทั้ง 6 ภาพมาจากหน้าเว็บที่รันจริง
- Raw logs: [lab004.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab004.txt), [lab005.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab005.txt), [lab006.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab006.txt)

จุดที่เบี่ยงจาก outline:

- LAB 006 เปลี่ยนไป wait ที่ `ReplicaSet.status.readyReplicas` เพราะการ wait รายชื่อ Pod ระหว่าง scale-down พบ `NotFound` เมื่อ Pod ที่กำลัง `Terminating` หายไป
- การถ่ายภาพ Pod ใหม่และ v2 จำกัด Service selector ชั่วคราวเพื่อให้ request ตกถึงเป้าหมายแน่นอน แล้วคืน `app=web` ทันที เนื่องจาก ingress ใช้เวลาประมาณ 3–5 วินาทีในการ sync upstream
- หลัง scale-down คำสั่งลบกลุ่มพบ 5 Pod รวม Pod ที่กำลัง `Terminating`; สุดท้าย ReplicaSet กลับเป็น 3/3/3 ถูกต้อง
- LAB 005 พบ NGINX reload error ชั่วคราวตอน controller เริ่มใหม่ ก่อนตามด้วย `Backend successfully reloaded`

สิ่งที่ยังค้างเฉพาะภายนอกขอบเขตงาน: ไฟล์ไดอะแกรมที่อีกทีมกำลังจัดทำ โดย README อ้างชื่อ `lab004-architecture.svg` ถึง `lab006-architecture.svg` ไว้ถูกต้องแล้ว นอกจากนี้ remote repository ปัจจุบันยังไม่มีโฟลเดอร์ใหม่จนกว่างานชุดนี้จะถูก commit/push

ยืนยันว่า namespace `lab004`, `lab005`, `lab006` ว่างทั้งหมด ไม่มี port-forward ค้าง และลบ `devtools-k8s-lab-g2` แล้ว โดยผลตรวจ `container_matches=0`