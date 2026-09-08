ทำ LAB 010–012 เสร็จครบแล้ว พร้อม manifest, README, runlog และ screenshot จากระบบจริง

- [LAB 010](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/010-configmap-separate-config/README.md) — ผ่าน
  - blue → amber → rose
  - `CreateContainerConfigError` จากชื่อ ConfigMap ผิด
  - แก้กลับและ Clean Re-run ผ่าน

- [LAB 011](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/011-secret-and-why-not-configmap/README.md) — ผ่าน
  - ระบบ web/api/db พร้อมใช้งาน
  - ถอด base64 ได้ `labpass`
  - รหัสผิดทำให้ `/ready` ตอบ 503 และเกิด `password authentication failed`
  - แก้กลับและ Clean Re-run ผ่าน

- [LAB 012](/root/workspace/DevTools/05_kubernetes/02_Session2_Networking_Config_Storage/012-why-data-disappears/README.md) — ผ่าน
  - เพิ่ม ticket ผ่าน UI: 8 → 9
  - สร้าง db Pod ใหม่: กลับเป็น 8
  - ไฟล์ `/tmp` หายใน web Pod ใหม่
  - `emptyDir` รอด container restart แต่ไม่รอด Pod recreation
  - scale db 0 → 1 ทำข้อมูลกลับเป็น seed 8
  - Clean Re-run ผ่าน

จุดที่ปรับจาก outline ตามพฤติกรรมจริง:

- เพิ่ม `DB_PORT: "5432"` เพื่อป้องกันการชนกับ Service environment อัตโนมัติ `DB_PORT=tcp://...`
- เพิ่ม named port `postgres` ใน `02-db-emptydir.yaml` มิฉะนั้น EndpointSlice แสดง port `<unset>`
- เพิ่มคำสั่ง recreate web Pod เพื่อพิสูจน์ว่า `/tmp/note.txt` หายจริง
- ไม่ restart db ในช่วง Secret ผิด เพราะ LAB 011 ยังไม่มี volume; db ใหม่จะ init ด้วยรหัสใหม่และข้อมูล reset ซึ่งขัดกับผลที่ outline คาดไว้

ปัญหาที่พบและบันทึกไว้ตามจริง:

- Ingress ตอบ 503 ชั่วครู่หลัง rollout; รอบยืนยันใช้การรอจน `/info` เป็น JSON
- browser พบฟอร์ม offline ระหว่าง db rollout หนึ่งรอบ; รอ db `up` แล้วทดลองใหม่ผ่าน
- fresh clone จาก GitHub ณ เวลาทดสอบยังไม่มี path ของแล็บชุดใหม่นี้ จึงทดสอบคำสั่ง `cd` กับ repository ที่ mount อยู่ งานต้องถูก publish ก่อนผู้เรียน clone ได้

Runlogs: [lab010.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab010.txt), [lab011.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab011.txt), [lab012.txt](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab012.txt)

สิ่งที่ยังค้างในขอบเขตงานนี้: ไม่มี ไฟล์ไดอะแกรมที่ README อ้างอิงยังเป็นงานของทีมไดอะแกรมตามที่แจ้งไว้

ยืนยันว่า `devtools-k8s-lab-g4` ถูกลบแล้ว และ `docker ps -a --filter name=devtools-k8s-lab-g4` ไม่พบ container ค้างอยู่ครับ