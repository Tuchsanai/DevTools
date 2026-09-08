อัปเดต [Kubernetes_Session2_Slides.html](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/Kubernetes_Session2_Slides.html) แล้ว

หน้าที่เพิ่ม:

- 3 · โครง object — ทบทวน พร้อม `d09-yaml-anatomy.svg` แบบ base64
- 8 · Deployment — ทบทวน
- 9 · Ingress — ทบทวน path-only
- 10 · Service — ClusterIP/NodePort, ports และ DNS
- 33 · ConfigMap — `data`, `envFrom`, `configMapKeyRef`, volume
- 45 · Secret — `stringData`, `data`, `secretKeyRef`
- 57 · Volume/PVC — `emptyDir`, `volumeMounts`, `PGDATA`
- 70 · Volume/PVC — PVC, access modes, storage และ claim
- 82 · Probes — readiness/liveness/startup/exec
- 83 · Probes — ค่าเวลา 5 ตัว

จำนวนรวม: **97 หน้า**

ผล `check-slides.js`:

- `brokenImages: []`
- `externalRefs: []`
- Navigation ครบทุกปุ่ม
- `labFoldersReferenced`: ครบ 7 แล็บ
- ขนาด 5.4 MB
- ไม่มี page error
- ตรวจ PNG ของหน้าที่เพิ่มครบทั้ง 10 หน้าแล้ว: ไม่ล้น ไม่ทับ และ YAML 18px จำนวน 6–16 บรรทัด

ข้อจำกัด: เพดาน 90 หน้าไม่สามารถทำพร้อมเงื่อนไข “ครบทุก object”, PVC/Probes อย่างละ 2 หน้า และ “ห้ามแตะหน้าอื่น” ได้ เพราะไฟล์เดิมมี 87 หน้า จึงต้องใช้ขั้นต่ำ 97 หน้า ส่วน agenda/เลขหน้าอัปเดตอัตโนมัติจากระบบนำทางของไฟล์เดิมแล้ว