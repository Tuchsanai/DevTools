ดำเนินการ LAB 019–021 เสร็จครบแล้ว โดยใช้ `devtools-lab` กำกับการแยก environment, เก็บหลักฐาน และ cleanup

- [LAB 019 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/019-telling-kubernetes-what-you-need/README.md) — 386 บรรทัด
  - requests/limits และ UI/log: ผ่าน
  - `cpu: 64` ทำให้ Pending: ผ่าน
  - memory limit 32Mi ทำให้ `OOMKilled`, exit 137: ผ่าน
  - Clean Re-run และลบ namespace: ผ่าน
  - [Raw transcript](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab019.txt)

- [LAB 020 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/020-reading-the-symptoms/README.md) — 398 บรรทัด
  - Pending, ImagePullBackOff และ Service ไม่มี endpoint: ผ่าน
  - process crash: พบ `MODULE_NOT_FOUND`, RESTARTS เพิ่ม และ Event `BackOff`
  - Exercise targetPort ผิดได้ `Connection refused`: ผ่าน
  - แก้ทุกเคส, UI กลับมา และ Clean Re-run: ผ่าน
  - [Raw transcript](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab020.txt)

- [LAB 021 README](/root/workspace/DevTools/05_kubernetes/03_Session3_Application_Deployment/021-the-big-picture/README.md) — 380 บรรทัด
  - ระบบ web 2 + API 2 + PostgreSQL 1, PVC Bound และ Ingress: ผ่าน
  - สร้าง ticket #9 จาก browser จริง และ trace ถึง PostgreSQL: ผ่าน
  - ตัด db Service/API Service/Ingress/web แล้วได้อาการจริงและแก้คืนครบ
  - Clean Re-run ได้ seed 8 tickets และลบ namespace: ผ่าน
  - [Raw transcript](/root/workspace/DevTools/05_kubernetes/.work/runlogs/lab021.txt)

จุดที่ต่างจาก outline:

- LAB 019 รายงาน scheduler จริงเป็น `1 untolerated taint + 2 Insufficient cpu` เพราะ control-plane มี taint
- LAB 020 Kubernetes v1.36.4 แสดง STATUS เป็น `Error` ระหว่าง crash แม้สุ่มตรวจ 90 วินาที แต่ Events ยืนยัน `BackOff restarting failed container`
- LAB 021 เมื่อ dependency หายนานพอ readiness เกิด cascade จน web endpoints ว่างและหน้าเว็บเป็น 503
- Outline ระบุ `manifests/01..11` แต่รายการ object ที่กำหนดมี 10 ไฟล์พอดี จึงส่ง 10 manifest โดยไม่เพิ่ม object นอกบทเรียน
- ช่วงหลัง apply ใหม่ Ingress อาจตอบ 404/503 ก่อน sync จึงใช้ retry ตามผลรันจริง
- เคยใช้ path ฝั่ง host ในการตรวจ dry-run ทำให้หาไฟล์ไม่พบหนึ่งรอบ; เก็บ failure ตามจริงและรันแก้ด้วย path ภายใน container จนทุก manifest ผ่าน

ตรวจสุดท้ายแล้ว:

- README ทุก command block มีคำอธิบายและ Expected output ครบ
- screenshot ทั้ง 5 ภาพมาจากหน้าเว็บจริงและเห็นการ์ดสถานะ/ชื่อ Pod
- ไม่แก้โค้ดใน `app/`
- ไม่เหลือ namespace `lab019`, `lab020`, `lab021`
- ไม่เหลือ port-forward
- ลบ `devtools-k8s-lab-g7` แล้ว และ `docker ps -a --filter name=devtools-k8s-lab-g7` ว่าง
- ไม่มีงานค้างหรือขั้นที่ไม่ได้รันจริง