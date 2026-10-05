# งาน: แปลง "ป้ายในภาพ" ของ prompt ภาพให้คำอธิบายเป็นภาษาไทย

อินพุต: `<CH>-items.json` (list ของ {id, file, section, caption_th, scene, labels, extra})
- `labels` = ป้ายข้อความ verbatim ในภาพ (ลำดับมีความหมาย; ป้ายซ้ำ = ปรากฏซ้ำตามจำนวน)
- `extra` = ส่วนท้ายของ Constraints ที่บอกตำแหน่งป้าย (อ้างถึงป้ายด้วย 'ป้าย' ในเครื่องหมาย ' ')
ส่วนอื่นของ prompt (Use case/Style/BASE constraints) สคริปต์ผู้ประสานงานเติมเอง ไม่ต้องยุ่ง และจะเติมประโยค
"Thai text must be rendered exactly as given, correct Thai spelling, clear Thai font, no garbled glyphs" ให้อัตโนมัติ

เอาต์พุต: เขียน `<CH>-patch.json` = object {id: {"labels": [...], "extra": "..."}} ให้ **ครบทุก id** (แม้ไม่เปลี่ยนก็ใส่ค่าเดิม)
ใส่ "caption_th"/"scene" เฉพาะกรณีที่ต้องแก้ (ปกติไม่ต้อง ยกเว้นบท 005 ตามข้อแก้ที่ระบุ)

## กติกาป้าย
1. ป้ายที่เป็นคำอธิบาย/หัวข้อ/สถานะเชิงบรรยาย/คำเปรียบ/ชื่อแผง/ชื่อขั้นตอน → ภาษาไทยสั้น อ่านง่าย (≤ ~20 ตัวอักษรถ้าเป็นไปได้) สะกดถูก
   ตัวอย่าง: "desired: 3"→"ต้องการ 3", "actual: 2"→"มีจริง 2", observe/diff/act→"สังเกต"/"เทียบ"/"ลงมือ",
   "controller" (เป็นคำอธิบาย)→"ตัวควบคุม (controller)", "Problem"→"ปัญหา", "Solution"→"ทางแก้",
   "level-triggered"→"ดูสถานะปัจจุบันเสมอ (level-triggered)" (คำศัพท์เทคนิคใส่วงเล็บได้ถ้าช่วยผูกกับเนื้อหา),
   "before"/"after"→"ก่อน"/"หลัง", "old"/"new"→"เก่า"/"ใหม่", "watch" (ข่าวที่พลาด)→"แจ้งเตือน (watch)" เป็นต้น
2. คงภาษาอังกฤษไว้เฉพาะ: ชื่อ resource/kind (Pod, ReplicaSet, Service, Deployment, EndpointSlice, NodePort, ClusterIP ...),
   ชื่อ field YAML (replicas, selector, template, ownerReferences, maxSurge, targetPort ...), คำสั่ง (kubectl ..., --replicas=5),
   ชื่อ object/ชื่อ Pod/ชื่อ node/ชื่อ component (kube-apiserver, kube-proxy)/IP/port/เวอร์ชัน/image tag,
   และข้อความ error/สถานะจริงของ Kubernetes (Running, Pending, Terminating, NotReady, CrashLoopBackOff, exceeded quota, field is immutable ...)
   — ถ้าข้อความเหล่านี้เป็นหัวใจของภาพ เพิ่มป้ายไทยสั้นอธิบายกำกับได้ 1 ป้าย
3. ทุกภาพต้องมีป้ายภาษาไทยอย่างน้อย 1 ป้ายที่อธิบายใจความหลัก (ถ้าป้ายเดิมเป็นเทคนิคล้วน ให้เพิ่มหัวเรื่องไทยสั้น ๆ เช่น
   หัวป้ายบนสุด "ลบแล้วสร้างแทนเอง") รวมทั้งหมด ≤ 7 ป้ายต่อภาพ, ห้ามป้ายว่าง, ห้ามมี " ในป้าย
4. ป้ายที่ซ้ำกัน (เช่น "1.1" ×3) ให้ใส่ซ้ำใน list ตามจำนวนครั้งที่ปรากฏ
5. ต้องแก้ `extra` ให้อ้างป้ายใหม่ตรงตัวอักษร (ทุกครั้งที่ extra กล่าวถึงป้ายใน ' ' ต้องตรงกับ labels) และบอกตำแหน่งป้ายไทยที่เพิ่ม
   (เช่น "'ลบแล้วสร้างแทนเอง' is a title banner at the top"). เขียน extra เป็นภาษาอังกฤษเหมือนเดิม
   ถ้าใน extra มีข้อความ "no other text" / "N labels" / "exactly five rows" ฯลฯ ให้ปรับจำนวนให้ตรง
6. ห้ามเปลี่ยนฉาก/ความหมายทางเทคนิค/ลำดับ/id/ชื่อไฟล์ (ยกเว้นข้อแก้เฉพาะบท 005 ที่ผู้ประสานงานระบุ)
7. ตัวเลขที่อยู่ในป้ายไทยต้องตรงกับฉากเดิม (BASE constraint บอก "numbers appear only where listed")
8. ป้ายไทยที่เป็นเลข+หน่วย ใช้รูปแบบสั้น เช่น "~45 วิ", "ต้องการ 3"

เมื่อเสร็จ รัน `python3 check.py <CH>` (ถ้ามี) หรืออย่างน้อยตรวจด้วย python ว่า JSON parse ได้ ครบทุก id, ทุกภาพมีป้ายไทย ≥1,
1–7 ป้าย, ทุกชื่อป้ายใน ' ' ของ extra อยู่ใน labels. รายงานสั้น ๆ: จำนวนภาพที่เปลี่ยน + ตัวอย่าง 3 ภาพก่อน/หลัง
ห้ามเขียนไฟล์อื่นนอกจาก `<CH>-patch.json` และไฟล์ชั่วคราวในโฟลเดอร์นี้ (ห้ามใช้ /tmp)
