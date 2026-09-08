# ผลตรวจความถูกต้อง YAML teaching ครั้งที่ 1 (yolo1 reviewer · kube-apiserver v1.36.4 + runlog)
## YAML_Guide.md — ต้องแก้
- L46,49,61,237 FAIL: มี backslash จริงในโค้ดสแปน (`\"5432\"`, `\"release v1\"`, `unknown field \"containers\"`, `\"lab007\"`) → ลบ backslash ทั้งหมด ใช้ "..." ตรง ๆ (grep -n '\\"' ทั้งไฟล์)
- L87 FAIL: บล็อก Pod (อ้าง 003/02-pod-with-sidecar.yaml) เขียน `command: [\"sh\", \"-c\"]` ไม่ตรงไฟล์จริง L20 `command: ["sh", "-c"]` → คัดจากไฟล์จริง
- L167 FAIL: `kubernetes.io/change-cause: \"release v1\"` ไม่ตรง 007/01-deployment.yaml L7 → แก้ให้ตรง
- L51-59 FAIL: สอนว่า `--dry-run=client` ตรวจ schema ได้ แต่ error ที่ยก (L61 `strict decoding error: unknown field "containers"`) จับได้เฉพาะ `--dry-run=server` (ทดสอบ: ย่อหน้าผิด/field ไม่รู้จัก/`value: 5432` ผ่าน client ทั้งหมด; runlog lab004:316 ใช้ server) → เพิ่ม `kubectl apply --dry-run=server -f` เป็นชั้นตรวจ schema และระบุว่า client ตรวจแค่ syntax + kind
- L46 NIT: `"5432"` ไม่มีในไฟล์ของครั้งนี้ → กำกับ "(ตัวอย่างเพิ่มเติม ไม่อยู่ในไฟล์ของแล็บ)" + error จริง `json: cannot unmarshal number into Go struct field EnvVar.spec.containers.env.value of type string`
- L102 WARN: ports[].containerPort ไม่ใช่ optional — list ports optional แต่ containerPort required ในแต่ละสมาชิก (explain: -required-)
- L109 WARN: ระบุรายการ field ของ Pod ที่แก้ได้ตามข้อความจริง runlog lab004:266: image / initContainers image / activeDeadlineSeconds / tolerations (เพิ่มได้อย่างเดียว) / terminationGracePeriodSeconds กรณีพิเศษ
- L150 WARN: "RS อาจรับ Pod ที่สร้างแยกมานับเหมือนการทดลอง 006" ไม่ตรงแล็บ 006 (§7 = เปลี่ยน template แล้ว Pod เก่าไม่ถูกแทน · §8 = relabel เป็น orphan) → อธิบายอาการจริงหรือตัดคำอ้าง · ข้อความจริง: The ReplicaSet "web" is invalid: spec.template.metadata.labels: Invalid value: {"app":"webx"}: `selector` does not match template `labels`
- L197 NIT: ข้อความจริง `spec.selector: Invalid value: {...}: field is immutable` · L220 NIT: แก้เป็น "API ปฏิเสธตอน create" ให้สอดคล้อง L223 · L223 NIT: ข้อความเต็ม `...fieldRef.fieldPath: Invalid value: "metadata.whoops": error converting fieldPath: field label not supported: metadata.whoops`
- L6,63,113 NIT: หัวข้อไม่มีเลข — ปล่อยได้ (ถ้าใส่เลขต้องแก้ anchor ทุก README)
## README
- 004 L130 FAIL: สั่ง `--dry-run=client` ทันทีหลังยก error strict decoding (client ไม่จับ; §7 ของ README เองใช้ server) → เปลี่ยนเป็น `kubectl apply --dry-run=server -f 01-pod.yaml` หรืออธิบายว่า client ตรวจเฉพาะ syntax/kind · L126 NIT: "annotations เป็น metadata ที่ selector ไม่ใช้เลือกสมาชิก" · L126 NIT: กำกับว่า "5432" เป็นตัวอย่างเพิ่มเติม
- 006 L123 FAIL: "ผิดบ่อย" อ้าง RS นับ Pod ที่สร้างเอง + "controller สุ่ม image" (ไม่ใช่สิ่งที่แล็บทำ) → "RS ไม่ทำ rolling update — แก้ image ใน template แล้ว Pod เดิมยังเป็น v1 จนกว่าจะถูกลบ จึงเห็น v1/v2 ปน" · L123 WARN: ข้อความ selector/labels ให้ตรงของจริง (มี backtick)
- 005 L119 NIT: `No resources found in lab005 namespace.` เต็ม · 007 L132 NIT: เพิ่มข้อความ error `selector` does not match template `labels`
- 001, 002, 003: ผ่าน
## ยืนยันถูกต้อง: apiVersion ทุก kind · imagePullPolicy default (Always สำหรับ :latest/ไม่มี tag · IfNotPresent อื่น ๆ) · restartPolicy Always · replicas default 1 · selector immutable · strategy 25%/25% ปัดขึ้น/ลง ห้าม 0/0 · minReadySeconds 0 · revisionHistoryLimit 10 · fieldRef.apiVersion v1 · namespace conflict message · anchor ครบ · ลำดับหัวข้อถูก
