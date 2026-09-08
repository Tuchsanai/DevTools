# ผลตรวจรับตาม DoD (spec ส่วนที่ 9) — yolo1 · 2026-09-02

| เกณฑ์ | ผ่าน/ไม่ผ่าน | หลักฐาน | สิ่งที่ต้องแก้ |
|---|---|---|---|
| โฟลเดอร์แล็บครบ 21 ชื่อ 3 หลัก+อังกฤษ เรียงต่อเนื่องข้ามครั้ง | ผ่าน | dod-check: 21 โฟลเดอร์ 001-021 ครั้งละ 7 | - |
| ทุก README มีหัวข้อครบตามเทมเพลตส่วนที่ 4 | ผ่าน | check-readme.py 21 แล็บ: 0 FAIL / 0 WARN (ลำดับ 15 หัวข้อ) | - |
| ทุกคำสั่งมี 3 ส่วน (คำสั่ง / 📝 / ✅) | ผ่าน | linter: ทุก bash block มี 📝+✅ · P6 บรรทัดว่างก่อน ✅ ครบ | - |
| Expected output มาจากการรันจริง | ผ่าน (หลังรอบ 2) | reviewer 5 สาย เทียบ runlog ทีละบล็อก → พบ 4 บล็อกแต่ง/ประกอบ (002, 004, 006, 014) แก้ด้วยผลจริงจาก runlog แล้ว; ยืนยันซ้ำ (002 ไม่มี `1m`, 014 ไม่มีบรรทัดปลอม, 006 ใช้ loop 15 รอบจริง) | - |
| ทุกแล็บมี "ทดลองให้พัง" + แก้กลับ | ผ่าน | dod-check + reviewer ยืนยันครบ 21 | - |
| ตารางแก้ปัญหา · สรุปคำสั่ง · เช็กลิสต์ | ผ่าน | linter (5-12 checkbox ทุกแล็บ) | - |
| Cleanup + Clean Re-run | ผ่าน | linter + reviewer | - |
| สไลด์ HTML 3 ไฟล์ เปิด file:// ไม่พึ่งเน็ต ไม่มีภาพหาย | ผ่าน | check-slides.js (offline context): S1 90 หน้า 6.1 MB · S2 88 หน้า 6.0 MB · S3 90 หน้า 5.5 MB (หลังเพิ่มหน้า YAML เฟส 9 + ภาพถ่าย v2) · brokenImages 0 · externalRefs 0 · alt ครบ | - |
| สไลด์แล็บอ้างโฟลเดอร์แล็บชัด | ผ่าน | labFoldersReferenced = 7/7 ทั้ง 3 ไฟล์ | - |
| ปุ่มลัดครบ (← → Space O F ? Esc Ctrl+P) | ผ่าน | check-slides.js: right/left/space/end/home/overview/help/hash + progress/counter/controls (F/Ctrl+P เป็น browser API ตรวจโดยการมีอยู่ของ handler ในโค้ดที่คัดลอกจากต้นแบบ) | - |
| README ระดับชุด + ระดับครั้ง 4 ไฟล์ | ผ่าน | 171/91/92/94 บรรทัด · ลิงก์ทุกอันมีจริง · ไม่มี path ข้ามครั้ง | - |
| ไดอะแกรม .excalidraw + .svg ครบ และถูกอ้าง | ผ่าน | 15+15 ต่อครั้ง · README ทุกแล็บอ้าง lab0NN-architecture.svg (linter) · สไลด์ฝัง d01-d08 | - |
| ผู้เรียนใหม่เดินตามได้โดยไม่ต้องถาม | ผ่าน (หลังรอบ 2) | reviewer พบ 2 จุดตายทั้งชุด (curl 8080 ใน container · ไม่มีขั้นเข้า container/k8s-bootstrap) → แก้ทั้ง 21 แล็บ (P1/P2) + เพิ่มคำสั่งรอ (P4) + วิธีเปิด terminal ที่สอง · smoke run แล็บ 003/006 ตามเอกสารบน cluster ของ yolo1 ผ่าน | - |
| ใช้แอปจริง Next.js+Tailwind+PostgreSQL แสดงชื่อ Pod | ผ่าน | app/ (SkillSpace) การ์ดสถานะ web/api/db ทุกหน้า · screenshot 36 ภาพจริง | - |
| image :v1 และ :v2 ต่างชัด | ผ่าน | v1 น้ำเงิน/ป้าย v1 · v2 มรกต/ป้าย v2 (ตรวจเฟส 4 + screenshot 004/007/018) | - |
| screenshot ทุกภาพจากการรันจริงตรงขั้นตอน | ผ่าน | cyolo1 ตรวจ 36 ภาพ (≥4 ทุกหมวด) · yolo1 ดู 8 ภาพ · 006 กำกับว่าภาพมาจากอีกรอบ | - |
| สไลด์ยึดรูปแบบ Fullstack_Slides.html | ผ่าน | คัดลอก CSS/JS/คลาส · ลำดับ ปก→agenda→loop→[คั่นบท→ทฤษฎี→คำถามก่อนเริ่ม→แล็บ]→สรุป→ปิด · ตรวจหน้าโดย cyolo1 + yolo1 3 รอบ (ขยายโค้ด/ไดอะแกรม แยกหน้า topology ครอป screenshot) | - |
| เวอร์ชัน tool/image ถูก pin ในเอกสาร | ผ่าน | root README ตาราง + footer ทุกแล็บ (kind v0.33.0 · K8s v1.36.4 · kubectl v1.37.0 · image 2569_1) | - |
| (เพิ่ม) ภาพถ่ายสมจริง ≥ 15/ครั้ง ใช้ในสไลด์ **และสื่อเนื้อหา Kubernetes ของ section (v2 · ผู้สอนสั่ง 2026-09-03)** | ผ่าน | 45 JPEG v2 (15/ครั้ง) lum 0.41-0.85 · คลังภาพ K8s (ตู้คอนเทนเนอร์/ท่าเรือ · แร็ค/LED · สาย/patch panel/กรง · ไดรฟ์/storage · การ์ดสี/security key · NOC) ตาม .work/photo-spec-v2.md · loop cyolo1 ตรวจ → yolo1 feedback → cyolo1 แก้ (S1 4 · S2 1+5 หน้าคั่น · S3 5 ภาพ) · alt/h2/"มองภาพนี้" เล่าภาพใหม่ · กรอบภาพแนวคิด 16:9 · จุดโฟกัสหน้าคั่นบทมองเห็น · ชุด v1 สำรอง .work/photos-v1-backup/ | - |
| (เพิ่ม) รูปทุกภาพผ่าน loop cyolo1 ตรวจ → yolo1 feedback → cyolo1 สร้างใหม่ | ผ่าน | ไดอะแกรม 2 รอบ+วาดใหม่ · ภาพจริง 1 รอบ+gen ใหม่ 4 ภาพ · screenshot 1 รอบ · หน้าสไลด์ 3 รอบ (รายงานใน .work/) | - |

## รายการที่ต้องแก้
ไม่มีรายการค้างที่ block การส่งมอบ

## ข้อสังเกต/ข้อจำกัดที่ผู้สอนควรรู้ (ไม่ใช่ข้อบกพร่อง)
1. ขั้น "Clone โค้ดแล็บ" ในทุก README จะใช้ได้เมื่อ commit + push โฟลเดอร์ 05_kubernetes ขึ้น GitHub แล้ว (ตอนนี้ยังเป็นไฟล์ untracked ในเครื่อง)
2. ภาพ screenshot ของแล็บ 006 (และ 018 บางภาพ) มาจากรอบรันต่างจากตารางในข้อความ ชื่อ Pod จึงไม่ตรงกัน — README กำกับไว้แล้วว่า "ค่าเหล่านี้ต่างกันได้/ภาพจากอีกรอบ"
3. image `k8s-lab-web` ตั้ง `HOSTNAME=0.0.0.0` (Next.js bind) ทำให้ `env | grep HOSTNAME` ไม่ใช่ชื่อ Pod และ `localhost` ใน alpine resolve เป็น IPv6 → README 003 อธิบายให้ใช้ `hostname`/`127.0.0.1` แล้ว
4. `~/.curlrc` ใน image มี retry=5 → curl ที่ล้มจะรอ ~15 วิ ก่อน error (README 017 อธิบาย `--retry 0`)
5. ไดอะแกรม lab021 กับ d07 ของครั้งที่ 3 เกือบเหมือนกัน (จงใจ: แล็บ 021 คือภาพใหญ่)
6. `.work/` (บันทึกกลางทาง runlog/รายงาน/prompt) อยู่ใน .gitignore ลบทิ้งได้เมื่อไม่ต้องการ

## คำตัดสิน
**ส่งงานได้** — รวมเฟส 9 + ภาพถ่าย v2 แล้ว (dod-check 24/24 · 2026-09-03 · container ตรวจสอบ devtools-k8s-verify ลบแล้ว)

# ภาคผนวก — เฟส 9: การสอน YAML ของทุก object (ผู้ใช้สั่งเพิ่ม 2026-09-02 20:05)
| เกณฑ์ | ผ่าน/ไม่ผ่าน | หลักฐาน |
|---|---|---|
| ทุกแล็บมีหัวข้อ "อ่าน YAML ของแล็บนี้" ครอบทุกไฟล์ .yaml (รวม manifests/ broken/ fixed/ exercise/) | ผ่าน | check-yaml-teaching.py 3 ครั้ง: 0 FAIL · 19 แล็บที่มี manifest ครอบครบ (001/002 ไม่มี manifest) · README 401-450 บรรทัด (เพดาน 450 สำหรับส่วนเพิ่มนี้) |
| YAML_Guide.md ต่อครั้ง (จบในตัว มีบททบทวน object ที่เรียนแล้ว) | ผ่าน | 297 / 298 / 374 บรรทัด · anchor ที่ README ลิงก์มีจริงทั้งหมด · README ระดับชุด/ครั้ง ลิงก์คู่มือ |
| ความถูกต้องของคำอธิบาย field/default | ผ่าน (หลังแก้) | yolo1 reviewer ×3 ตรวจกับ `kubectl explain`/`--dry-run=server` บน v1.36.4 → พบ FAIL 8 ข้อ (backslash ในโค้ด · snippet ไม่ตรงไฟล์ 2 · dry-run=client สอนผิด · error ระบุขั้นผิด · YAML แบนสอน parent ผิด · accessModes/storage ไม่ใช่ optional · ขาดบททบทวน) → cyolo1 แก้ครบ ยืนยันซ้ำแล้ว |
| สไลด์มีหน้า "กายวิภาค YAML" ครบทุก object ที่ใช้ในครั้งนั้น (ใหม่ = เต็ม · เคยเรียน = ทบทวน) | ผ่าน | S1 8 หน้า (+d09 เต็มหน้า) · S2 9 หน้า (Deployment+Ingress ทบทวนรวม 1 หน้า) · S3 11 หน้า · วางก่อนแล็บแรกที่ใช้ · ไฟล์ 90/88/90 หน้า check-slides ผ่าน · footer ทุกหน้าชี้ anchor ที่มีจริงใน YAML_Guide.md |
| หน้า YAML ผ่าน loop ตรวจ (cyolo1 ตรวจ+ส่ง feedback → yolo1 feedback → cyolo1 แก้) | ผ่าน | รายงาน .work/yaml-slides-review-s{1,2,3}.md + feedback yolo1 .work/yaml-slides-feedback-s{1,2,3}.md + fix2 (รายงาน .work/yaml-slides-fix2-report-s*.md) · yolo1 เปิดดูทุกหน้า YAML ทั้ง 3 ไฟล์แล้ว |
| ไดอะแกรม d09-yaml-anatomy (.svg+.excalidraw ×3 ครั้ง) | ผ่าน | yolo1 ดู: YAML จริงไฮไลต์ 4 key เส้นหักฉากไปการ์ด status สีเทา |
