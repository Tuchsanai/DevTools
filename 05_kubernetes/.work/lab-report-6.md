ทำ LAB 016–018 เสร็จสมบูรณ์และรันจริงตามลำดับแล้ว

- [LAB 016 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/016-adding-a-database/README.md) — 398 บรรทัด  
  ระบบสามชั้น, UI, persistence หลังลบ DB Pod, stateless scaling, ลบ Secret/แก้กลับ และ Clean Re-run ผ่านครบ  
  [Runlog 016](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab016.txt)

- [LAB 017 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/017-ingress-the-front-door/README.md) — 370 บรรทัด  
  `/` → web, `/api` → api, access log, backend name/port ผิดจนได้ 503, แก้กลับ และ Clean Re-run ผ่านครบ  
  [Runlog 017](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab017.txt)

- [LAB 018 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/018-updating-without-downtime/README.md) — 400 บรรทัด  
  RollingUpdate v1→v2 และ undo ไม่มี `FAIL`; Recreate เกิด `FAIL` 17 ครั้ง; ถอด readiness เกิด `FAIL` 5 ครั้ง; screenshot และ Clean Re-run ผ่านครบ  
  [Runlog 018](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab018.txt)

จุดที่เบี่ยงจาก outline:

- LAB 016: DB replica ตัวที่สองไม่เป็น `CrashLoopBackOff/Pending` แต่ขึ้น Ready บน node เดียวกัน ก่อน logs แสดง automatic recovery และ DB Pod เดิม restart จึงบันทึกอาการจริงและอธิบายความเสี่ยงไว้แล้ว
- LAB 018: forward rollout request loop ถูก Ingress ส่งไป v1 ตลอด mixed phase ก่อนสลับเป็น v2 แต่ Pod monitor ยืนยันว่ามี v1/v2 พร้อมกัน ส่วน undo loop เห็น v1/v2 สลับจริง โดยไม่มี `FAIL`

ปัญหาที่พบและแก้แล้ว:

- ต้องกำหนด `DB_PORT: "5432"` เพราะ Kubernetes Service env ชื่อ `DB_PORT` ชนกับค่าที่ API ต้องการ
- curl ใน image มี retry configuration ทำให้ 503 แสดงซ้ำ; ใน README ใช้ `--retry 0` เพื่ออ่านอาการตรง ๆ

YAML ทุกไฟล์ผ่าน client dry-run, image ทุกจุดมี `imagePullPolicy: IfNotPresent`, screenshot มาจากระบบจริง และไม่มีงานค้าง

ลบ `devtools-k8s-lab-g6` แล้ว และ `docker ps -a --filter name=devtools-k8s-lab-g6` เหลือเฉพาะหัวตาราง ยืนยันว่า container ไม่เหลือครับ