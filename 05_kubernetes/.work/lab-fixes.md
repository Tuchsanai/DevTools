# รายการแก้แล็บ (yolo1 สะสมจาก linter/การอ่าน · แก้หลังเฟส 5 จบ เพราะ job ยังเขียนไฟล์อยู่)

## FAIL (ต้องแก้)
- 004, 013, 014, 015: README มีชื่อ/IP เฉพาะเครื่องผลิต (172.30.* / devtools-k8s-lab-* / k8s-course-net) → แทนด้วยค่าที่นักศึกษาเห็น (localhost:8080 / localhost:3000 / devtools-k8s) และกำกับ "ค่าเหล่านี้ต่างกันได้" (ดูบรรทัดที่ระบุด้านล่าง)
- 014: อ้างโฟลเดอร์ครั้งที่ 3 ด้วย path (03_Session3_...) → เปลี่ยนเป็นข้อความ "แล็บ 0NN ของครั้งที่ 3"
## WARN (ควรแก้)
- 019 (468 บรรทัด) · 020 (475 บรรทัด) เกิน 400 → ตัดส่วนซ้ำ/ย่อ Expected output ที่ยาวเกินจำเป็น
- 003 ขั้น 4: อธิบาย HOSTNAME=0.0.0.0 / localhost (IPv6) vs 127.0.0.1 ให้เป็นบทเรียนเสริมที่อ่านลื่น
## ทำตอนปิดงาน
- ลบ .ipynb_checkpoints ทุกที่ใน 05_kubernetes (ยกเว้น backup/) + เพิ่ม .gitignore
- 004-declarative-yaml line 60:✅ **Expected output** — ได้ชื่อ container หรือ container ID (รอบตรวจ�
- 013-persistent-storage-with-pvc line 70:✅ **Expected output** — node ทั้ง 3 เป็น `Ready` และพบ image คร�
- 014-running-is-not-ready line 64:✅ **Expected output** — cluster พร้อมและ image ครบ (รอบทดสอบใ
- 014-running-is-not-ready line 333:🧭 ต่อยอด: [LAB 15 — Assembling a Real Application](../../03_Session3_Application_Deploy
- 015-assembling-a-real-application line 69:✅ **Expected output** — node และ ingress พร้อม พร้อม image แอ�
- 015-assembling-a-real-application line 92:cd ~/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/015-assembling-a-real-app
- 015-assembling-a-real-application line 98:/root/labwork/DevTools/05_kubernetes/03_Session3_Application_Deployment/015-assembling-a-real-ap
- 013, 014, 015 (job g5): บรรทัดแรกของ README เป็นบล็อก 💡 แนวคิดหลัก ไม่ใช่หัวเรื่อง `# LAB n — ...` → จัดลำดับหัวให้ตรงเทมเพลตส่วนที่ 4: `# LAB n — ชื่อ : ประโยคขยาย` → `> โฟลเดอร์ ... = LAB n ของชุด Kubernetes ครั้งที่ N` → `> (ไฟล์ของแล็บนี้: ...)` → `> 💡 แนวคิดหลัก`
- 016, 017, 018 (job g6): บรรทัดแรกเป็นบล็อก 💡 ก่อนหัวเรื่อง เช่นเดียวกับ 013-015 → จัดลำดับหัวใหม่
- 006 (job g2): worker "จำกัด Service selector ชั่วคราว" เพื่อให้ screenshot ตกที่ Pod เป้าหมาย (แล้วคืนค่า) — ภาพจริง แต่ README ต้องไม่บอกให้นักศึกษาทำเช่นนั้น (ตรวจว่าไม่มีขั้นตอนนี้ใน README; ถ้ามีให้ตัด)

## ผล linter เต็ม 21 แล็บ (17:18) — ให้แก้ทุก FAIL และ WARN ที่ทำได้
- FAIL 013-persistent-storage-with-pvc: title line: > 💡 **แนวคิดหลักของแล็บนี้:** ถ้าอยากให
- FAIL 013-persistent-storage-with-pvc: no worker-only names/IPs leaked
- FAIL 014-running-is-not-ready: title line: > 💡 **แนวคิดหลักของแล็บนี้:** "Pod Running" ไม่ได้�
- FAIL 014-running-is-not-ready: cross-session folder refs (other sessions): ['03_Session3_Application_Deployment']
- FAIL 014-running-is-not-ready: no worker-only names/IPs leaked
- FAIL 015-assembling-a-real-application: title line: > 💡 **แนวคิดหลักของแล็บนี้:** แอปจริงค�
- FAIL 015-assembling-a-real-application: no worker-only names/IPs leaked
- FAIL 016-adding-a-database: title line: > 💡 **แนวคิดหลักของแล็บนี้:** ส่วนที่มีข้อ�
- FAIL 017-ingress-the-front-door: title line: > 💡 **แนวคิดหลักของแล็บนี้:** Ingress คือประตู
- FAIL 018-updating-without-downtime: title line: > 💡 **แนวคิดหลักของแล็บนี้:** เปลี่ยนเว�
