# U-D2 — บันทึกการตัด ย้าย และแตกสไลด์

ขอบเขต: ตอนที่ 4–5 (`s4_lab1.html`, `s5_lab2.html`) · เลขหน้าเดิมอ้างจากเด็ค 60 สไลด์

| หน้าเดิม | บล็อกเดิม | การเปลี่ยนบนสไลด์ | ปลายทางรายละเอียดเต็ม |
|---:|---|---|---|
| 24 | ตาราง “แล็บนี้ใน 30 วินาที” | คง 4 ประเด็นหลักไว้หน้าแรก และแตก “สิ่งที่มักเข้าใจผิด + เตรียมเครื่องเรียน” เป็นหน้าที่สอง | `001_LAB_Run_The_System/readme.md` → `### 🎯 แล็บนี้ใน 30 วินาที`, `### สิ่งที่มักเข้าใจผิด`, `## เตรียมเครื่องเรียน` |
| 24 | คำอธิบายยาวใน 4 แถว | ย่อถ้อยคำ แต่คงคำถาม · prerequisite · สิ่งที่ทำได้ · สิ่งที่ยังไม่สอน | `001_LAB_Run_The_System/readme.md` → `### 🎯 แล็บนี้ใน 30 วินาที` |
| 26 | กรณีไม่ส่ง `POSTGRES_PASSWORD` พร้อม error | แตกเป็นหน้า “กล่องไม่ขึ้น” และคงเฉพาะคำสั่งกับ error ที่ตอบคำถาม | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 2 — ต้องกำหนดค่าเพื่อยกฐานข้อมูลด้วย docker run อย่างไร` |
| 26 | คำสั่ง `docker run` ที่ถูก + ผล `docker ps` | แตกเป็นหน้า “ฐานข้อมูลขึ้นโดยไม่เปิดพอร์ต” และชี้คอลัมน์ `PORTS` | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 2 — ต้องกำหนดค่าเพื่อยกฐานข้อมูลด้วย docker run อย่างไร` |
| 26 | ผล `\dt` 5 ตาราง + จำนวน seed `12 · 8 · 3 · 6` | แตกเป็นหน้าหลักฐาน schema + seed; ตัดคำอธิบายประกอบที่ซ้ำกับ readme | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 5 — จะรัน schema และ seed ตอนเริ่มต้นอย่างไร`, `## การทดลองที่ 6 — จำนวนข้อมูลตั้งต้นตรงกับ requirements ไหม` |
| 27 | transcript ฝั่งไม่มี volume | ย่อเหลือคำตอบ `count 9 → docker rm -f → count 8` ภายใน 7 บรรทัด | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 7 — ข้อมูลที่เพิ่มเองรอดจากการสร้างกล่องใหม่ไหม` |
| 27 | transcript ฝั่ง named volume | ย่อเหลือบรรทัด `-v ops-pgdata…` และแถวใบที่ 9 ภายใน 7 บรรทัด | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 8 — Named volume ทำให้ข้อมูลคงอยู่ไหม` |
| 30 | `api/Dockerfile` + build transcript ในหน้าเดียว | แตกเป็นหน้า Dockerfile และหน้าผล build; คง Dockerfile ไม่เกิน 14 บรรทัด | `002_LAB_Build_The_API/api/Dockerfile`; `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 2 — จะ build image ครั้งแรกทีละขั้นอย่างไร` |
| 30 | build transcript รอบแรก | ย่อเหลือ `[1/6]`–`[6/6]`, context `28.54kB`, และ naming; ตัดเวลา/รายละเอียด BuildKit ที่ไม่ใช่คำตอบ | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 2 — จะ build image ครั้งแรกทีละขั้นอย่างไร` |
| 30 | คำอธิบาย metadata ที่ไม่สร้าง layer | ย้ายไปบันทึกสั้นใต้ Dockerfile/ผล build | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 2 — จะ build image ครั้งแรกทีละขั้นอย่างไร` |
| 33 | `.dockerignore` 17 บรรทัดรวม comment/บรรทัดว่าง | แสดงเฉพาะ 11 pattern และระบุชัดว่าไฟล์จริง 17 บรรทัด | `002_LAB_Build_The_API/api/.dockerignore`; `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 5 — จะกันไฟล์ออกจาก build context ด้วย .dockerignore อย่างไร` |
| 33 | คำสั่งและผล build อยู่คู่ `.dockerignore` | แตกเป็นหน้าหลักฐาน `4.9M → 66B` | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 5 — จะกันไฟล์ออกจาก build context ด้วย .dockerignore อย่างไร` |
| 33 | pipeline `docker build … 2>&1 \| grep -A2 …` | ตัด pipeline ออกจากสไลด์ ใช้ `docker build -t ops-api:1.0 .` และบอกให้ดูบรรทัด `transferring context` | คำสั่งฉบับเต็มยังอยู่ที่ `002_LAB_Build_The_API/readme.md` → การทดลองที่ 5 |
| 33 | คำอธิบาย BuildKit `66B` / `28.15kB` | ย่อเหลือหมายเหตุหนึ่งบรรทัด; รายละเอียดเต็มอยู่ใน readme | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 5 — จะกันไฟล์ออกจาก build context ด้วย .dockerignore อย่างไร` |
| 36 | REQ-01 และ REQ-02 อยู่หน้าเดียวกัน | แตกเป็นหน้าหลักฐาน REQ-01 `HTTP 201` และหน้า REQ-02 `HTTP 409` | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 10 — จะทดสอบข้อกำหนดจริงของลูกค้าด้วย curl อย่างไร` |
| 36 | response body REQ-01 แบบเต็ม | ย่อเหลือ `id`, `asset_id`, `priority`, `status`; body เต็มและวิธีเก็บ `TID` ย้ายไป readme | `002_LAB_Build_The_API/readme.md` → การทดลองที่ 10 |
| 36 | บล็อก `curl … \| python3 -c '…'` และรายการใบสถานะ `NEW` | ตัดทั้งบล็อกจากสไลด์ตามข้อกำหนด เหลือ pointer ไปขั้นยืนยันสถานะ | `002_LAB_Build_The_API/readme.md` → การทดลองที่ 10 → “ยืนยันว่าใบนั้นสถานะไม่เปลี่ยน” |
| 36 | หมายเหตุ IP ของฐานข้อมูล | ย่อเป็นสะพานไป LAB 4 ในหน้าหลักฐาน REQ-02 | `002_LAB_Build_The_API/readme.md` → การทดลองที่ 10 → “บทเรียน” |
| — | ไม่มีสไลด์ปิดตอนที่ 4 | เพิ่ม “ตอนนี้ได้อะไร → ทำต่อที่แล็บไหน” 4 บล็อก | ตัวเลข LAB 1 จาก `BRIEF_DECK.md` และ `001_LAB_Run_The_System/readme.md` |
| — | ไม่มีสไลด์ปิดตอนที่ 5 | เพิ่ม “ตอนนี้ได้อะไร → ทำต่อที่แล็บไหน” 4 บล็อก | ตัวเลข LAB 2 จาก `BRIEF_DECK.md` และ `002_LAB_Build_The_API/readme.md` |

Waiver: ไม่มี
