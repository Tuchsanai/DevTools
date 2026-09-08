ทำแล็บ 013–015 เสร็จสมบูรณ์และรันจริงครบแล้วครับ

- [LAB 013 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/013-persistent-storage-with-pvc/README.md) — 384 บรรทัด
  - PVC เปลี่ยน `Pending → Bound`
  - เพิ่ม ticket ผ่าน UI จริง จำนวนข้อมูล `8 → 9`
  - ลบ db Pod แล้ว ticket #9 ยังอยู่
  - ลบ PVC แล้วเห็น `Terminating`, db Pod `Pending` และข้อมูลกลับเป็น seed 8
  - Cleanup และ Clean Re-run ผ่าน

- [LAB 014 README](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/014-running-is-not-ready/README.md) — 352 บรรทัด
  - scale db เป็น 0 แล้ว API ยัง `Running` แต่ `READY 0/1`
  - Service endpoints ว่าง และกลับมาเองเมื่อ db ฟื้น
  - liveness restart API จริง โดย `RESTARTS` เพิ่มเป็น 1
  - readiness path ผิดให้ HTTP 404 และไม่มี endpoint
  - แก้กลับและ Clean Re-run ผ่าน

- [LAB 015 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/015-assembling-a-real-application/README.md) — 390 บรรทัด
  - web/API พร้อมอย่างละ 2 Pod บนหลาย node
  - หน้าเว็บเชื่อม API ได้ โดย db down เป็นสถานะที่ตั้งใจใน LAB 15
  - ลบ API Service แล้ว Pod ยัง Running แต่ web ติดต่อไม่ได้
  - ลบ Ingress แล้วเห็นการเปลี่ยน `200 → 404`
  - ลบ ConfigMap แล้ว Pod ใหม่เป็น `CreateContainerConfigError` ขณะที่ Pod เก่ายังตอบ 200
  - apply ทั้งโฟลเดอร์ซ่อมระบบและ Clean Re-run ผ่าน

จุดที่ปรับจาก outline ตามผลจริง:

- ระบุ `DB_PORT: "5432"` เพราะ env อัตโนมัติของ Kubernetes Service ชนกับชื่อ `DB_PORT` ของแอป
- เพิ่ม db readiness probe เพราะ Pod condition Ready เกิดก่อน PostgreSQL เปิด socket
- ไฟล์ bad readiness ใช้ `Recreate` เพื่อไม่ให้ Pod เก่าที่ยัง Ready ค้างเป็น endpoint
- ใช้ `kubectl rollout status` แทนการ wait ด้วย label ระหว่าง rollout เพราะอาจจับ Pod เก่าที่กำลัง terminate
- Clean Re-run ของ LAB 15 เพิ่มการ poll HTTP เพราะ ingress-nginx ต้องใช้เวลาสั้น ๆ ในการ sync rule

การตรวจรับ:

- kubeconform: Valid `27/27`, Invalid `0`
- Screenshot จริง 6 ภาพ ตรวจเห็นการ์ดสถานะและชื่อ Pod ครบ
- Raw transcripts: [lab013.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab013.txt), [lab014.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab014.txt), [lab015.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab015.txt)
- ไม่ได้แก้โค้ดใน `app/`
- ไม่มีงานแล็บค้าง และไดอะแกรมทั้งสามไฟล์มีอยู่แล้ว

ลบ container `devtools-k8s-lab-g5` แล้ว ไม่มี host port ที่ publish และ `docker ps -a --filter name=devtools-k8s-lab-g5` ไม่เหลือรายการครับ