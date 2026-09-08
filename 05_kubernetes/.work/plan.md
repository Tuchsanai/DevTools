# แผนการผลิตฉบับสมบูรณ์ (yolo2 ร่าง · yolo1 ตรวจแก้ 2026-09-02)

ตัวย่อ: R = /root/workspace/DevTools/05_kubernetes · S1/S2/S3 = โฟลเดอร์ 3 ครั้ง · W = R/.work (ไม่ใช่ของส่งมอบ)

## สิ่งที่ yolo1 แก้จากร่างของ yolo2
| # | ร่างเดิม | แก้เป็น | เหตุผล |
|---|---|---|---|
| 1 | แอปอยู่ `R/00_app` | `R/app/` | ตามเอกสาร orchestration · ไม่ปนกับโฟลเดอร์ครั้งที่สอน (0N_) |
| 2 | ผลิตทีละครั้ง (S1 → QG → S2 → QG → S3) | ผลิตแล็บทั้ง 21 พร้อมกัน 7 job (job ละ 3 แล็บติดกัน) แล้วตรวจรับรวม | ตาม orchestration เฟส 5 · เร็วกว่า 3 เท่า · ความสม่ำเสมอคุมด้วย lab-outline + worker-env + เทมเพลตส่วนที่ 4 แทน |
| 3 | เปิดเว็บ: ครั้ง 1-2 port-forward, ครั้ง 3 Ingress | port-forward เฉพาะ "ดู Pod เดียว" (003-005, 009) · "ประตู" Service+Ingress ตั้งแต่ 006 | port-forward ปักที่ Pod เดียว มองไม่เห็น load balancing / self-healing / readiness ซึ่งเป็นหัวใจของแล็บ 006, 008, 014, 018 |
| 4 | ไดอะแกรมแยกตาม task ต่อครั้ง หลังแล็บเสร็จ | ไดอะแกรม 3 job ขนาน (ครั้งละ job) **เริ่มทันทีหลัง outline** คู่กับการสร้างแอป | ไม่พึ่งแล็บ · ใช้ canvas Excalidraw คนละ port (8893/8894/8895) |
| 5 | README ระดับชุด + ระดับครั้ง ไม่มีเจ้าของชัด | เพิ่ม job 6D (cyolo1) เขียน README 4 ไฟล์หลังแล็บเสร็จ | DoD บังคับ 4 ไฟล์ |
| 6 | สร้างโครงโฟลเดอร์เป็น task ถึก | parent สร้างด้วยสคริปต์ (deterministic) ก่อนเฟส 3 | ล็อกชื่อโฟลเดอร์ 21 แล็บให้ทุก job อ้างตรงกัน |
| 7 | ให้ worker บันทึก `.run-log.txt` ในโฟลเดอร์แล็บ | บันทึกที่ `W/runlogs/labNNN.txt` | ไม่ปนของส่งมอบ · ใช้สุ่มเทียบตอนตรวจรับ |
| 8 | spec ขัดกันเอง (7 แล็บ/001_LAB/LO8/8 แล็บต่อครั้ง) | ยึดส่วนที่ 2-4: 21 แล็บ · `00n-xxx` · LO1-LO7 · 7 แล็บต่อครั้ง | ส่วนหัวของ spec เป็นของเก่า |
| 9 | ตรวจ README ต่อครั้ง 3 รอบ (QG2 ×3) | yolo1 ตรวจรวมครั้งเดียวหลังเฟส 5 + สุ่มรันตามเอกสารบนเครื่องสะอาด | ลดคอขวด yolo1 · ตรวจรับตาม DoD ครบทุกข้ออยู่แล้ว |
| 10 | image gen สำหรับปก | ทำถ้าเครื่องมือมี ไม่งั้นใช้ SVG จาก Excalidraw | ไม่ใช่ข้อบังคับใน DoD |

## ลำดับงานจริง (ตาม orchestration 8 เฟส)
| เฟส | ผู้ทำ | งาน | สถานะ |
|---|---|---|---|
| 0 | parent | เช็คโควตา 3 บัญชี · ตรวจ toolchain (Playwright host, Excalidraw headless, image, ports) | ✅ ผ่าน (yolo1 5-8%, yolo2 0%, cyolo1 17%) |
| 1 | yolo2 | ร่างแผน | ✅ |
| 2 | yolo1 | ตรวจแผน + `W/lab-outline.md` + `W/app-requirements.md` + `W/worker-env.md` + โครงโฟลเดอร์ | ✅ |
| 3 | cyolo1 (JOB=app) | สร้างแอปที่ `R/app/` ตาม app-requirements · ทดสอบบน kind จริง | ✅ รายงานผ่าน 10/10 |
| 6A | cyolo1 ×3 ขนาน (canvas 8893/8894/8895) | ไดอะแกรมครั้งละ job: d01-d08 + lab0NN-architecture ×7 → .excalidraw + .svg | ✅ 45 ภาพ (yolo1 สุ่มดู 12 ผ่าน) |
| 6E | cyolo1 ×3 ขนาน | ภาพถ่ายสมจริง ≥ 15 ภาพต่อครั้ง (imagegen) → slides_assets/photos/ + photos.md · **ผู้ใช้กำหนด 2026-09-02** | ✅ 45 ภาพ JPEG ผ่าน loop ตรวจ (17:20) |
| 4 | yolo1 | ตรวจแอป 8 ข้อ (รันจริง) → `W/app-fixes.md` · วนแก้จนผ่าน = **ล็อกแอป** | ✅ ผ่าน 8/8 + 10/10 (16:27) แอปล็อกแล้ว |
| 6A-R | cyolo1 ×3 → yolo1 → cyolo1 | **loop ตรวจรูป (ผู้ใช้กำหนด 2026-09-02):** cyolo1 ตรวจภาพ 5 หมวด (ถูกต้อง·สวยงาม·ตัวอักษร·ตำแหน่ง·อื่น ๆ) → yolo1 ดูภาพ+รายงานแล้วเขียน feedback `W/diagram-feedback-sN.md` → cyolo1 สร้างใหม่ตาม feedback → ตรวจซ้ำ · ใช้ loop เดียวกันกับ screenshot แล็บและหน้าสไลด์ในเฟส 7 | |
| 5 | cyolo1 ×7 ขนาน (JOB=lab-g1..g7 บน k8s-course-net) | job g ทำแล็บ 3g-2..3g: manifest → รันจริง → Expected output → screenshot → README | ✅ 21 แล็บเสร็จ 17:40 · p5-fixes เสร็จ 17:58 (linter 0 FAIL/WARN · ไม่มีชื่อ/IP เครื่องผลิต · .gitignore) · screenshot review ผ่านทั้ง 3 ครั้ง (36 ภาพ) · yolo1 reviewer ×5 กำลังอ่านเนื้อหาเชิงลึก |
| 6B/6C/6D | cyolo1 ×4 ขนาน | สไลด์ครั้งละ job (p6-slides-sN) · 6D README ระดับชุด + 3 ครั้ง | ✅ สไลด์ 3 ไฟล์ (81/87/79 หน้า · 5.1-5.6 MB · check-slides ผ่าน · ผ่าน loop ตรวจหน้า 3 รอบ) + README 4 ไฟล์ · README แล็บผ่านรอบ 2 (reviewer 5 สาย + cyolo1 แก้) |
| 7 | yolo1 | ตรวจรับตาม DoD ส่วนที่ 9 → `W/final-fixes.md` · งานแก้: ถึก→cyolo1 คิด→yolo1 | ✅ dod-check 18/18 · smoke run 003/006 ผ่าน · ส่งงานได้ (19:45) |
| 8 | yolo2 | สรุปส่งงาน + รายการที่ค้าง | |

กฎเพิ่มจากผู้ใช้ (2026-09-02): yolo1 รันขนานได้ 2-5 งาน · รูปทุกชนิดผ่าน loop 6R · ภาพจริง ≥ 15/ครั้ง

| 9 | yolo1 สเปก → cyolo1 ×3 + ไดอะแกรม → yolo1 reviewer ×3 → cyolo1 แก้ → cyolo1 สไลด์ ×3 → loop ตรวจหน้า | **การสอน YAML ของทุก object** (ผู้ใช้สั่ง 20:05): หัวข้อ "อ่าน YAML ของแล็บนี้" ทุกแล็บ · YAML_Guide.md ต่อครั้ง · หน้ากายวิภาค YAML ในสไลด์ · d09-yaml-anatomy.svg | เริ่ม 20:10 |

## quality gate
| gate | หลัง | เกณฑ์ผ่าน |
|---|---|---|
| QG-app (เฟส 4) | เฟส 3 | 8 ข้อใน orchestration เฟส 4 + 10 ข้อทดสอบใน app-requirements §5 · ผ่านแล้ว **ห้ามแก้พฤติกรรมแอป** (ถ้าจำเป็นให้ tag ใหม่และรันแล็บที่กระทบซ้ำ) |
| QG-final (เฟส 7) | เฟส 6 | DoD 18 ข้อ · สุ่ม README ≥ 6 ไฟล์เทียบกับ runlog · เปิดสไลด์ 3 ไฟล์ด้วย Playwright (offline, ปุ่มลัด, ไม่มีภาพหาย) · grep ข้อมูลจริง/ path ข้ามครั้ง |

## จุดเสี่ยงที่ยังต้องเฝ้า (จากร่าง yolo2 ที่ยังใช้ได้)
- R4 แรม: 7 kind cluster + app job ≈ 25 GB จาก 61 GB → พอ · ถ้า bootstrap ล้มให้ job นั้น retry เองครั้งเดียว
- R5 แอปเปลี่ยนหลังล็อก → ต้องรันแล็บที่กระทบซ้ำ · หลีกเลี่ยงด้วยการทดสอบ §5 ให้ครบก่อนล็อก
- R7 สไลด์บวม: screenshot กว้าง 1280 · ไดอะแกรม SVG · เพดาน 15 MB/ไฟล์
- R8/R9 ผลรันแต่ง/ภาพไม่ตรงขั้น: บังคับ runlog + ชื่อไฟล์ภาพระบุขั้นตอน + ตรวจรับสุ่มเทียบ
- R10 ข้อมูลจริงหลุด: ตรวจรับ grep `@`, `ghp_`, `sk-`, `tuchsanai` (ยกเว้นชื่อ image/repo) ทั้ง R
- R12 แล็บ 018 ภาพระหว่าง rollout: minReadySeconds 5 + maxSurge 1 + shot.js วนถ่าย
- R15 แล็บ 008/009/015 ซ้ำกัน: outline กำหนดมุมมองต่างกันแล้ว (IP เปลี่ยน / ใครเข้าถึง / ภาพรวม object)

## เฟส 9 (ผู้สอนสั่งเพิ่ม 2026-09-02) — เสร็จ 2026-09-03
สอน YAML ของทุก object: README ทุกแล็บมี "อ่าน YAML ของแล็บนี้" · YAML_Guide.md ต่อครั้ง (297/298/374 บรรทัด) · หน้า "กายวิภาค YAML" ในสไลด์ S1 8 / S2 9 / S3 11 หน้า · d09-yaml-anatomy ×3 · ตรวจกับ kubectl explain · loop cyolo1 ตรวจ+feedback → yolo1 feedback → cyolo1 แก้ ครบ 3 ไฟล์ · dod-check 24/24 · บันทึก .work/final-fixes.md ภาคผนวก

## ภาพถ่าย v2 (ผู้สอนสั่ง 2026-09-03) — เสร็จ 2026-09-03
ภาพจริงต้องสื่อเนื้อหา Kubernetes: spec .work/photo-spec-v2.md · gen p6e2-photos-s* → review p6e2-review-s* → feedback .work/photos2-feedback-s* → fix p6e2-fix-s* (+ fix2-s2 หน้าคั่นบท) · ตรวจรับ: 45 ภาพผ่านเกณฑ์อัตโนมัติ · สไลด์ 90/88/90 หน้า · dod-check 24/24
