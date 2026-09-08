สรุปส่งงาน — ชุดเรียน Kubernetes Concept First (05_kubernetes) · 2026-09-02

1. สิ่งที่ส่งมอบ
```text
05_kubernetes/
├── README.md                                  # ภาพรวมชุด · เตรียมเครื่อง 5 ขั้น · เวอร์ชันที่ pin
├── 01_Session1_Kubernetes_Basics/             # LAB 001–007 · README.md · Kubernetes_Session1_Slides.html (81 หน้า) · slides_assets/
├── 02_Session2_Networking_Config_Storage/     # LAB 008–014 · README.md · Kubernetes_Session2_Slides.html (87 หน้า) · slides_assets/
├── 03_Session3_Application_Deployment/        # LAB 015–021 · README.md · Kubernetes_Session3_Slides.html (79 หน้า) · slides_assets/
│   └── 0NN-<ชื่อแล็บ>/  README.md · *.yaml · images/   (ทุกแล็บ)
├── app/                                       # SkillSpace: web(Next.js+Tailwind) · api · db(PostgreSQL) · build-images.sh · k8s-reference/
├── Fullstack_Slides.html                      # ต้นแบบรูปแบบสไลด์ (ไม่ใช่สไลด์ของชุด)
├── PROMPT_Kubernetes_Course_Spec.txt · PROMPT_Kubernetes_Orchestration.txt
├── backup/old_version/                        # เนื้อหาชุดเดิม (ถูก ignore ไม่ขึ้น git)
└── .work/                                     # runlog/รายงานตรวจ (ignore · 625 MB · ลบได้)
```

2. ตารางแล็บ 21 ตัว
```text
ครั้ง | แล็บ | โฟลเดอร์                              | แนวคิดหลัก
  1   | 001 | 001-kubernetes-introduction            | K8s คือผู้ดูแลที่ทำให้แอปตรงกับที่สั่งไว้เสมอ · control plane vs worker
  1   | 002 | 002-kubectl-and-namespace              | ทุกอย่างคือ object สั่งผ่าน kubectl และจัดกลุ่มด้วย namespace
  1   | 003 | 003-pod-the-smallest-unit              | หน่วยเล็กที่สุดคือ Pod ไม่ใช่ container
  1   | 004 | 004-declarative-yaml                   | บอก "สภาพที่อยากได้" ไม่ใช่ "ทำอะไร"
  1   | 005 | 005-labels-the-glue                    | label/selector คือกาวที่จับ object เป็นกลุ่ม
  1   | 006 | 006-desired-state-and-self-healing     | เทียบจำนวนที่อยากได้กับที่มีจริง → สร้างคืนเอง
  1   | 007 | 007-deployment-manages-change          | Deployment ดูแลการเปลี่ยนแปลง: scale · rollout · rollback
  2   | 008 | 008-why-we-need-service                | Pod IP เปลี่ยนได้ จึงต้องมีชื่อคงที่
  2   | 009 | 009-service-types-and-access           | ClusterIP/NodePort ต่างกันที่ "ใครเข้าถึงได้"
  2   | 010 | 010-configmap-separate-config          | config อยู่นอก image เปลี่ยนพฤติกรรมโดยไม่ build ใหม่
  2   | 011 | 011-secret-and-why-not-configmap       | แยกข้อมูลลับ และ base64 ไม่ใช่การเข้ารหัส
  2   | 012 | 012-why-data-disappears                | ข้อมูลใน container หายเมื่อ Pod เกิดใหม่
  2   | 013 | 013-persistent-storage-with-pvc        | เก็บข้อมูลนอก container ด้วย PVC
  2   | 014 | 014-running-is-not-ready               | Running ≠ พร้อมรับงาน · readiness probe
  3   | 015 | 015-assembling-a-real-application      | แอปจริงคือหลาย object ทำงานร่วมกัน
  3   | 016 | 016-adding-a-database                  | ชั้นข้อมูล scale เหมือน web ไม่ได้
  3   | 017 | 017-ingress-the-front-door             | Ingress = ประตูหน้าบ้าน แยกทางด้วย path
  3   | 018 | 018-updating-without-downtime          | rolling update v1→v2 โดยประตูไม่ปิด
  3   | 019 | 019-telling-kubernetes-what-you-need   | requests/limits จองให้พอ จำกัดไม่ให้กินหมด
  3   | 020 | 020-reading-the-symptoms               | อ่านอาการหา layer ที่พังก่อนแก้ (Pending/ImagePullBackOff/CrashLoop)
  3   | 021 | 021-the-big-picture                    | ตาม request จาก Browser ถึง PostgreSQL ต่อทุกเรื่องเป็นภาพเดียว
```

3. วิธีเริ่มใช้งาน
- สไลด์: ดับเบิลคลิก `0N_Session*/Kubernetes_SessionN_Slides.html` เปิดใน browser แบบ file:// ได้เลย ไม่ต้องใช้เน็ต (ปุ่ม ← → Space O F ? Esc · Ctrl+P พิมพ์ PDF)
- เปิดเครื่องเรียน: `docker run ... tuchsanai/devtools-k8s:2569_1` ตามคำสั่งใน README ราก แล้ว `docker exec -it devtools-k8s bash`
- ในเครื่องเรียน: `git clone https://github.com/Tuchsanai/DevTools.git` ที่ `~/labwork` → `k8s-bootstrap` (kind 1 control-plane + 2 worker + ingress + metrics)
- Build แอป: `cd app && ./build-images.sh` แล้ว `kind load docker-image k8s-lab-web:v1 k8s-lab-web:v2 k8s-lab-api:v1 k8s-lab-db:v1 --name devtools`
- เริ่มแล็บ: เปิด README ของครั้ง → README ของแล็บตามลำดับ · ทุกคำสั่งมี 📝 อธิบาย + ✅ ผลที่คาด · จบด้วย Cleanup

4. สิ่งที่ยังค้าง / ข้อจำกัด
- (แก้แล้ว 19:55) README ราก/ครั้งเคยเขียนว่ายังไม่มีไฟล์สไลด์ — ตอนนี้ลิงก์ไปยัง Kubernetes_SessionN_Slides.html จริงแล้ว
- ยังไม่ commit/push: โฟลเดอร์ทั้งหมดเป็น untracked และเนื้อหาชุดเดิม (01_setup… 04_…, basic_k8s.pdf) ถูกย้ายไป backup/ แสดงเป็น deleted ใน git status → ขั้น "Clone โค้ดแล็บ" ในทุก README จะใช้ได้หลัง push เท่านั้น
- Screenshot แล็บ 006 และบางภาพของ 018 มาจากรอบรันต่างจากตารางข้อความ ชื่อ Pod ไม่ตรงกัน (README กำกับไว้แล้ว)
- image web ตั้ง HOSTNAME=0.0.0.0 ทำให้ `env | grep HOSTNAME` ไม่ใช่ชื่อ Pod และ `localhost` ใน alpine เป็น IPv6 (003 ให้ใช้ `hostname` / `127.0.0.1`)
- `~/.curlrc` ใน image มี retry=5 → curl ที่ล้มจะรอราว 15 วิ (017 ให้ใช้ `--retry 0`)
- ไดอะแกรม lab021 กับ d07 ของครั้งที่ 3 เกือบเหมือนกัน (จงใจ) · เครื่อง RAM น้อยใช้ `k8s-bootstrap --single-node` ได้แต่ผลชื่อ node จะต่างจากตัวอย่าง

5. ข้อเสนอแนะสำหรับการสอนครั้งแรก
- ให้ผู้เรียน pull image `tuchsanai/devtools-k8s:2569_1` และ build+kind load แอปทั้ง 4 tag ล่วงหน้าก่อนเข้าห้อง เพราะเป็นขั้นที่กินเวลาและเน็ตมากที่สุด และเป็นเงื่อนไขของทุกแล็บ
- แล็บ 001 บังคับให้ทุกคนทำ `docker stop devtools-worker2` แล้วดู NotReady ด้วยตา เพื่อตั้งวงจร "ทายผล → รัน → สังเกต → อธิบาย → ทำให้พัง → แก้กลับ" ตั้งแต่ชั่วโมงแรก
- เปิด k9s ค้างไว้จอที่สองตลอดครั้ง และเน้นย้ำว่าชื่อ Pod/IP/AGE ที่ต่างจาก Expected output เป็นเรื่องปกติ เพื่อลดคำถาม "ทำไมของผมไม่เหมือน" ซึ่งเป็นจุดสะดุดที่พบบ่อยสุดใน README ทุกแล็บ

6. ส่วนเพิ่ม (เฟส 9 · ผู้สอนสั่ง): การสอน YAML ของทุก object
- ทุกแล็บที่มี manifest (19 แล็บ) มีหัวข้อ "อ่าน YAML ของแล็บนี้": ตารางทุกไฟล์ .yaml · YAML จริงพร้อมอธิบาย field ที่ใช้ครั้งแรก · "ผิดบ่อย" พร้อม error จริง · kubectl explain
- คู่มือ YAML ต่อครั้ง: 01_.../YAML_Guide.md (โครง object + syntax + Pod/RS/Deployment/Downward API) · 02_.../YAML_Guide.md (Service/ConfigMap/Secret/Volume-PVC/Probes + ทบทวน) · 03_.../YAML_Guide.md (Ingress/resources/strategy/manifests/broken + ทบทวน)
- สไลด์ทั้ง 3 ไฟล์มีหน้า "กายวิภาค YAML" ครบทุก object ที่ใช้ในครั้งนั้น (S1 8 · S2 9 · S3 11 หน้า · ไฟล์ 90/88/90 หน้า) + ไดอะแกรม d09-yaml-anatomy.svg
- ความถูกต้องตรวจกับ kubectl explain บน v1.36.4 โดย reviewer 3 สาย และหน้าสไลด์ผ่าน cyolo1 ตรวจ+feedback → แก้

7. ส่วนเพิ่ม (ผู้สอนสั่ง 2026-09-03): ภาพถ่ายสมจริง v2 สื่อเนื้อหา Kubernetes ของแต่ละ section
- แทนภาพชุดเดิม (อุปมาสำนักงาน/พัสดุ) ทั้ง 45 ภาพด้วยภาพจากคลังภาพโลก Kubernetes: ตู้คอนเทนเนอร์/ท่าเรือ/เครน (Pod · self-healing · rolling update: ตู้น้ำเงิน = v1 · เขียวมรกต = v2) · data center/แร็ค/ไฟสถานะ · สาย/patch panel/กรงล็อก · ถาดไดรฟ์/storage array · การ์ดสี/security key · ห้อง NOC
- องค์ประกอบทุกภาพระบุใน .work/photo-spec-v2.md · ผ่าน loop cyolo1 ตรวจ (เกณฑ์แรก: รู้หัวข้อใน 3 วินาที) → yolo1 feedback → cyolo1 สร้างใหม่ 10 ภาพ + จัดหน้าคั่นบท S2 5 ภาพ
- คำบรรยายในสไลด์ (alt · "ใช้ภาพจริงเป็นอุปมา — …" · "มองภาพนี้:") และ photos.md เล่าภาพใหม่ทั้งหมด · กรอบภาพหน้าแนวคิดพอดี 16:9 · ชุดเดิมสำรองที่ .work/photos-v1-backup/
