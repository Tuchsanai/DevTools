# ผลตรวจความถูกต้อง YAML teaching ครั้งที่ 3 (yolo1 reviewer · ตรวจกับ kubectl explain/dry-run บน v1.36.4 + runlog)
## YAML_Guide.md — ต้องแก้
- L5-257 FAIL: ไม่มีหัวข้อ "ทบทวน" (spec 4b) สำหรับ Deployment/Service/ConfigMap/Secret/PVC/Probes → README 7 ไฟล์ต้องลิงก์ไป #0-สรุปโครง-object (22 ครั้ง) หรือ #4-โครงโฟลเดอร์ (9 ครั้ง) ที่ไม่อธิบาย field → เพิ่ม "## 6. ทบทวน object ที่เรียนแล้ว" (อย่างละ 10-20 บรรทัด ใช้ YAML จาก 021/manifests) แล้วแก้ลิงก์ใน README ทุกแล็บให้ชี้ anchor ทบทวนที่ตรง object (Service/Secret/PVC/ConfigMap/Deployment/Probes)
- L52 WARN: ingressClassName — API ไม่ตรวจว่า IngressClass มีจริง (dry-run=server ผ่านกับชื่อมั่ว) และถ้า cluster ตั้ง default class จะเติมให้เอง → "ไม่มี (เว้นแต่ cluster ตั้ง IngressClass default ไว้)" + "ชื่อใดก็ได้ แต่ถ้าไม่มี controller รับ class นั้น Ingress จะไม่มี Address และไม่ route"
- L57 NIT: backend.service.port ระบุได้ทั้ง number และ name (mutually exclusive) → เพิ่ม "หรือ port.name"
- L70 NIT: ใส่ข้อความจริง `The Ingress "x" is invalid: spec.rules[0].http.paths[0].pathType: Required value: pathType must be specified` และเตือนว่า --dry-run=client ไม่จับ (จับเฉพาะ server/apply จริง)
- L82-112 NIT: อ้าง 019/manifests/02-web-deployment.yaml แต่ตัด readinessProbe ออกโดยไม่บอก → เติม "(ตัดส่วน readinessProbe)" หรือใส่กลับ
- L179-180 WARN: caveat ของ Recreate ผิด (Pod bare ที่ label ตรงจะถูก RS adopt แล้ว scale-to-0) → แทนด้วย "ถ้าลบ Pod เองระหว่าง Recreate RS จะสร้างตัวแทนทันทีแม้ตัวเก่ายัง Terminating"
- L253 NIT: ข้อความจริง `wget: can't connect to remote host (10.96.178.73): Connection refused`
## README
- 015 L119-123 WARN: แถว ConfigMap/Deployment/Service ลิงก์ #4-โครงโฟลเดอร์ (ไม่ใช่ field) และ 016-021 ใช้ #0 → ชี้หัวข้อทบทวน
- 016 L105-113 · 017 L111-119 · 018 L102-108 · 021 L116-121 WARN: ลิงก์ #0 → ชี้หัวข้อทบทวน · 018 L101 NIT: Service "ส่งงานเฉพาะ Pod ที่ Ready" ลิงก์ #3-strategy → ชี้ทบทวน Service/Probes
- 019 L139 WARN: `kubectl get pod -o jsonpath='{.status.qosClass}'` ไม่ระบุชื่อ Pod → ผลว่าง → ใช้ `kubectl get pod -n lab019 -l app=web -o jsonpath='{.items[0].status.qosClass}'` (runlog lab019:915)
- 021 L118 NIT: Secret มีแค่ POSTGRES_PASSWORD (DB_HOST/PORT/NAME/USER ฝังใน 04-api-deployment.yaml) → "เก็บรหัสผ่าน db แยกจาก Deployment"
- 020: ผ่าน · 017: ผ่าน
## ยืนยันถูกต้อง: pathType enum/semantics · host/tls · requests/limits/QoS · หน่วย · strategy defaults 25%/ปัดขึ้น-ลง · minReadySeconds 0 · revisionHistoryLimit 10 · diff exit codes · apply -f dir ไม่ recurse · ข้อความ error ทั้งหมดมีใน runlog · broken/fixed/exercise ตรงไฟล์ · ไม่มี path ข้ามครั้ง
