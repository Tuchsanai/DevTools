# COVERAGE — รายละเอียดที่ย้ายออกจากเด็ค ไปอยู่ที่ไหน

รวมจาก `deck_build/changes/U-D*.md` · เด็ครุ่น 60 สไลด์ → 83 สไลด์ (21 ส.ค. 2026)

ทุกบล็อกที่ถูก **ตัด** หรือ **ย่อ** ออกจากสไลด์ต้องมีแถวที่นี่ พร้อมปลายทางที่มีอยู่จริง

| unit | เดิม | บล็อก | การจัดการ | ปลายทาง |
|---|---|---|---|---|
| U-D1 | 2 | คง 1 หน้า | ย่อ `.sub` และคำบรรยายการ์ดทั้ง 10 ใบให้เหลือหัวใจของแต่ละตอน | การ์ดยังคง `data-go`; ตอน 1 → `s1_customer.html`, ตอน 2 → `s2_require.html`, ตอน 3 → `s3_design.html`, LAB 1–5 → `s4_lab1.html`…`s8_lab5.html`, สรุป → `s9_summary.html` |
| U-D1 | 2 | แก้ข้อเท็จจริง | `45 การทดลอง · แล็บละ 9 อัน` → `48 · 10 · 11 · 9 · 9 · 9`; เวลารวม → `4:15` | ตารางความจริงใน `deck_build/BRIEF_DECK.md` |
| U-D1 | 10 | แตก 2 หน้า | US-1…US-4 แยกจาก US-5…US-7; ไม่มีแถวใดถูกทิ้ง | ทั้งสองหน้าคง pointer `docs/01_requirements.md` · หัวข้อ 1 “แปลงคำบ่นเป็น User Story” |
| U-D1 | 10 | ย้ายประโยคปิด | “ทุกแถวมีคอลัมน์ขวาสุดเสมอ…” ย้ายไปหน้าครึ่งหลัง เพื่อปิดชุด US-5…US-7 | หน้าใหม่ US-5…US-7 และ `docs/01_requirements.md` |
| U-D1 | 11 | แตก 2 หน้า | REQ-01…06 แยกจาก REQ-07…12; คงข้อกำหนด เกณฑ์ผ่าน และคอลัมน์ที่มาเดิมครบ | ทั้งสองหน้าคง pointer `docs/01_requirements.md` · หัวข้อ 2 “ข้อกำหนดที่ทดสอบได้” |
| U-D1 | 11 | แก้การอ่าน | ตาราง `tbl xs` ถูกแยกเป็น `tbl sm`; ไม่ลดฟอนต์ | รายละเอียดเดิมอยู่ครบในสองหน้าใหม่ |
| U-D1 | 12 | แตก 2 หน้า | การ์ด NFR-1…3 แยกจากตาราง “ลูกค้าพูดว่า → NFR → เทคนิค Docker” | หน้าแรกชี้ `docs/01_requirements.md`; หน้าหลังชี้ `readme.md` |
| U-D1 | 16 | แตก 2 หน้า | schema 5 ตารางแยกจากตารางส่วนงาน, seed `12 · 8 · 3 · 6` และ SLA | ทั้งสองหน้าชี้ `docs/02_contract.md` · หัวข้อ 3 |
| U-D1 | 16 | ย่อ code | ใช้ `…` แทนคอลัมน์รอง: `created_at`, `DEFAULT 'NEW'`, `assignee`, `closed_at`, `returned_at`, `reorder_point` และรายละเอียดท้าย `stock_moves` | schema ครบอยู่ที่ `docs/02_contract.md` · หัวข้อ 3 และ `001_LAB_Run_The_System/db/initdb/01-schema.sql` |
| U-D1 | 16 | ย้ายคำอธิบาย | รายละเอียดว่า SLA ใช้คำนวณ `overdue` ของ REQ-09 และนิยามสถานะครุภัณฑ์ฉบับเต็มออกจากสไลด์ | `docs/02_contract.md` · หัวข้อ 3 |
| U-D1 | 17 | แตก 2 หน้า | flow `browser → web → api → db` + ผลที่ตามมา 3 ข้อ แยกจากตารางตัวแปร 4 แถว + server-rendered | หน้า flow ชี้ `docs/02_contract.md` หัวข้อ 1; หน้าตัวแปรชี้หัวข้อ 2 |
| U-D1 | 1–21 | ติดป้าย | eyebrow ของทุกสไลด์ปกติใน part U-D1 เปลี่ยนให้ขึ้นต้น `ตอนที่ N ·` และมี `ทฤษฎี` หรือ `หลักฐาน` | ปฏิบัติตาม N2; cover/section คงข้อยกเว้นเดิม |
| U-D2 | 24 | ตาราง “แล็บนี้ใน 30 วินาที” | คง 4 ประเด็นหลักไว้หน้าแรก และแตก “สิ่งที่มักเข้าใจผิด + เตรียมเครื่องเรียน” เป็นหน้าที่สอง | `001_LAB_Run_The_System/readme.md` → `### 🎯 แล็บนี้ใน 30 วินาที`, `### สิ่งที่มักเข้าใจผิด`, `## เตรียมเครื่องเรียน` |
| U-D2 | 24 | คำอธิบายยาวใน 4 แถว | ย่อถ้อยคำ แต่คงคำถาม · prerequisite · สิ่งที่ทำได้ · สิ่งที่ยังไม่สอน | `001_LAB_Run_The_System/readme.md` → `### 🎯 แล็บนี้ใน 30 วินาที` |
| U-D2 | 26 | กรณีไม่ส่ง `POSTGRES_PASSWORD` พร้อม error | แตกเป็นหน้า “กล่องไม่ขึ้น” และคงเฉพาะคำสั่งกับ error ที่ตอบคำถาม | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 2 — ต้องกำหนดค่าเพื่อยกฐานข้อมูลด้วย docker run อย่างไร` |
| U-D2 | 26 | คำสั่ง `docker run` ที่ถูก + ผล `docker ps` | แตกเป็นหน้า “ฐานข้อมูลขึ้นโดยไม่เปิดพอร์ต” และชี้คอลัมน์ `PORTS` | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 2 — ต้องกำหนดค่าเพื่อยกฐานข้อมูลด้วย docker run อย่างไร` |
| U-D2 | 26 | ผล `\dt` 5 ตาราง + จำนวน seed `12 · 8 · 3 · 6` | แตกเป็นหน้าหลักฐาน schema + seed; ตัดคำอธิบายประกอบที่ซ้ำกับ readme | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 5 — จะรัน schema และ seed ตอนเริ่มต้นอย่างไร`, `## การทดลองที่ 6 — จำนวนข้อมูลตั้งต้นตรงกับ requirements ไหม` |
| U-D2 | 27 | transcript ฝั่งไม่มี volume | ย่อเหลือคำตอบ `count 9 → docker rm -f → count 8` ภายใน 7 บรรทัด | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 7 — ข้อมูลที่เพิ่มเองรอดจากการสร้างกล่องใหม่ไหม` |
| U-D2 | 27 | transcript ฝั่ง named volume | ย่อเหลือบรรทัด `-v ops-pgdata…` และแถวใบที่ 9 ภายใน 7 บรรทัด | `001_LAB_Run_The_System/readme.md` → `## การทดลองที่ 8 — Named volume ทำให้ข้อมูลคงอยู่ไหม` |
| U-D2 | 30 | `api/Dockerfile` + build transcript ในหน้าเดียว | แตกเป็นหน้า Dockerfile และหน้าผล build; คง Dockerfile ไม่เกิน 14 บรรทัด | `002_LAB_Build_The_API/api/Dockerfile`; `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 2 — จะ build image ครั้งแรกทีละขั้นอย่างไร` |
| U-D2 | 30 | build transcript รอบแรก | ย่อเหลือ `[1/6]`–`[6/6]`, context `28.54kB`, และ naming; ตัดเวลา/รายละเอียด BuildKit ที่ไม่ใช่คำตอบ | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 2 — จะ build image ครั้งแรกทีละขั้นอย่างไร` |
| U-D2 | 30 | คำอธิบาย metadata ที่ไม่สร้าง layer | ย้ายไปบันทึกสั้นใต้ Dockerfile/ผล build | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 2 — จะ build image ครั้งแรกทีละขั้นอย่างไร` |
| U-D2 | 33 | `.dockerignore` 17 บรรทัดรวม comment/บรรทัดว่าง | แสดงเฉพาะ 11 pattern และระบุชัดว่าไฟล์จริง 17 บรรทัด | `002_LAB_Build_The_API/api/.dockerignore`; `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 5 — จะกันไฟล์ออกจาก build context ด้วย .dockerignore อย่างไร` |
| U-D2 | 33 | คำสั่งและผล build อยู่คู่ `.dockerignore` | แตกเป็นหน้าหลักฐาน `4.9M → 66B` | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 5 — จะกันไฟล์ออกจาก build context ด้วย .dockerignore อย่างไร` |
| U-D2 | 33 | pipeline `docker build … 2>&1 \ | grep -A2 …` | ตัด pipeline ออกจากสไลด์ ใช้ `docker build -t ops-api:1.0 .` และบอกให้ดูบรรทัด `transferring context` |
| U-D2 | 33 | คำอธิบาย BuildKit `66B` / `28.15kB` | ย่อเหลือหมายเหตุหนึ่งบรรทัด; รายละเอียดเต็มอยู่ใน readme | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 5 — จะกันไฟล์ออกจาก build context ด้วย .dockerignore อย่างไร` |
| U-D2 | 36 | REQ-01 และ REQ-02 อยู่หน้าเดียวกัน | แตกเป็นหน้าหลักฐาน REQ-01 `HTTP 201` และหน้า REQ-02 `HTTP 409` | `002_LAB_Build_The_API/readme.md` → `## การทดลองที่ 10 — จะทดสอบข้อกำหนดจริงของลูกค้าด้วย curl อย่างไร` |
| U-D2 | 36 | response body REQ-01 แบบเต็ม | ย่อเหลือ `id`, `asset_id`, `priority`, `status`; body เต็มและวิธีเก็บ `TID` ย้ายไป readme | `002_LAB_Build_The_API/readme.md` → การทดลองที่ 10 |
| U-D2 | 36 | บล็อก `curl … \ | python3 -c '…'` และรายการใบสถานะ `NEW` | ตัดทั้งบล็อกจากสไลด์ตามข้อกำหนด เหลือ pointer ไปขั้นยืนยันสถานะ |
| U-D2 | 36 | หมายเหตุ IP ของฐานข้อมูล | ย่อเป็นสะพานไป LAB 4 ในหน้าหลักฐาน REQ-02 | `002_LAB_Build_The_API/readme.md` → การทดลองที่ 10 → “บทเรียน” |
| U-D2 | — | ไม่มีสไลด์ปิดตอนที่ 4 | เพิ่ม “ตอนนี้ได้อะไร → ทำต่อที่แล็บไหน” 4 บล็อก | ตัวเลข LAB 1 จาก `BRIEF_DECK.md` และ `001_LAB_Run_The_System/readme.md` |
| U-D2 | — | ไม่มีสไลด์ปิดตอนที่ 5 | เพิ่ม “ตอนนี้ได้อะไร → ทำต่อที่แล็บไหน” 4 บล็อก | ตัวเลข LAB 2 จาก `BRIEF_DECK.md` และ `002_LAB_Build_The_API/readme.md` |
| U-D3 | หน้า 38 · ตัวเลข `.next/standalone`, `.next/static` และ content size |  | แก้ `49.7 MB → 49.9 MB`, `680 kB → 668 kB`, `73.2MB → 73.3MB`, `310MB → 314MB` | `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 3–4 |
| U-D3 | หน้า 39 · `docker history` + การตรวจ `node_modules` สอง image |  | แตกเป็น 2 สไลด์: (ก) history ไม่มีบรรทัด `npm` (ข) `12` เทียบ `35` และไม่มี `typescript` | เนื้อหาทั้งสองแผ่นชี้ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 4 |
| U-D3 | หน้า 39 · transcript ของ base `node:22-alpine` ที่ไม่ใช่คำตอบหลัก |  | ย่อเป็นบรรทัด `ต่อจากนี้คือ base node:22-alpine 9 บรรทัด` | transcript เต็มอยู่ที่ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 4 |
| U-D3 | หน้า 39 · รายละเอียด exit code และคำอธิบาย toolchain |  | ย่อเหลือข้อสรุปว่าคำสั่งแรกออก exit code 1 เป็นคำตอบที่ถูก และ image ไม่มี compiler/devDependencies | คำอธิบายเต็มอยู่ที่ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 4 |
| U-D3 | หน้า 41 · transcript `ps` ของ exec/shell form |  | คงเฉพาะ PID 1, process ลูกที่จำเป็น และเวลา `0m0.244s` เทียบ `0m10.281s`; ตัดแถว process ของคำสั่ง `ps` | transcript เต็มอยู่ที่ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 7 |
| U-D3 | หน้า 41 · note ผลต่อ LAB 5 |  | ย่อกลไก `SIGTERM → SIGKILL` ให้เหลือข้อสรุปเดียว และเพิ่ม pointer | คำอธิบายเต็มอยู่ที่ `003_LAB_Build_The_Web/readme.md` · การทดลองที่ 7 |
| U-D3 | หน้า 42 · ขนาด CSS สองจุด |  | แก้ `35 kB → 21048 ไบต์` และ `35235 ไบต์ → 21048 ไบต์` | `003_LAB_Build_The_Web/readme.md` · กับดักของ Next.js 16 / การทดลองที่ 9 |
| U-D3 | ท้ายตอนที่ 6 · เดิมไม่มีสไลด์ปิดตอน |  | เพิ่ม 4 บล็อก: ทฤษฎี 3 บรรทัด, REQ-08/09/12, LAB 3 = 9 การทดลอง · 45 นาที · 22 PASS, คำสั่งไป LAB 4 | `003_LAB_Build_The_Web/readme.md` · แล็บนี้ใน 30 วินาที / ตรวจงานด้วย `verify.sh`; คำสั่งจาก `004_LAB_Connect_Them/readme.md` · เตรียมเครื่องเรียน |
| U-D3 | ท้ายตอนที่ 7 · เดิมไม่มีสไลด์ปิดตอน |  | เพิ่ม 4 บล็อก: ทฤษฎี 3 บรรทัด, NFR-3, LAB 4 = 9 การทดลอง · 45 นาที · 19 PASS, คำสั่งไป LAB 5 | `004_LAB_Connect_Them/readme.md` · แล็บนี้ใน 30 วินาที / ตรวจงานด้วย `verify.sh`; คำสั่งจาก `005_LAB_Compose_And_Ship/readme.md` · เตรียมเครื่องเรียน |
| U-D4 | 51 | `db:` + `api:` + `web:` อยู่หน้าเดียวและมีโค้ด 45 บรรทัด | แตกเป็น 2 หน้า: (ก) `db` เน้น volume, healthcheck, ไม่มี `ports:` (ข) `api`/`web` เน้น `service_healthy` และ `ports:` บรรทัดเดียว | `005_LAB_Compose_And_Ship/readme.md` → `## การทดลองที่ 1 — Compose ประกาศ service อะไร`; ไฟล์จริง `005_LAB_Compose_And_Ship/compose.yaml` |
| U-D4 | 51 | environment ของ db, build args, healthcheck ของ web, `restart` และประกาศ volume ท้ายไฟล์ | ย่อด้วย `…` ให้เหลือ key ที่ตอบ NFR โดยมี pointer บนทั้งสองหน้า | `005_LAB_Compose_And_Ship/readme.md` → การทดลองที่ 1; `005_LAB_Compose_And_Ship/compose.yaml` |
| U-D4 | 51 | กฎทุกคำสั่งต้องมี `-p campusops` | ย้ายไปบล็อก “เปิดแล็บ” ของสไลด์ปิดตอน 8 | `005_LAB_Compose_And_Ship/readme.md` → `## เตรียมเครื่องเรียน` |
| U-D4 | 51 | เหตุผลที่ไม่ตั้ง `container_name` | ตัดจากสไลด์และให้ pointer ไปหลักฐานตรวจไฟล์ | `005_LAB_Compose_And_Ship/readme.md` → `## ตรวจงานด้วย verify.sh` (`[PASS] ไม่มี container_name…`); `005_LAB_Compose_And_Ship/compose.yaml` comment บรรทัด 11 |
| U-D4 | 52 | คำสั่ง `up -d --build`, ลำดับ Starting→Healthy, `ps`, HTTP 200 สี่หน้า และหมายเหตุ `start_period` อยู่หน้าเดียว | แตกเป็น 2 หน้า: (ก) ลำดับขึ้นระบบ + `real 1m10.147s` (ข) `ps`/PORTS + GET สี่หน้า + `start_period: 20s` | `005_LAB_Compose_And_Ship/readme.md` → การทดลองที่ 2, 3 และ 5 |
| U-D4 | 52 | คำอธิบายเวลารอบแรกและขั้นตรวจหน้าเว็บแบบเต็ม | ย่อเป็นข้อสรุปและ pointer ตามการทดลอง | `005_LAB_Compose_And_Ship/readme.md` → `## การทดลองที่ 2 — คำสั่งเดียวสร้างระบบครบไหม`, `## การทดลองที่ 5 — หน้าเว็บทั้งสี่ส่วนตอบสนองไหม` |
| U-D4 | 54 | transcript `down` เทียบ `down -v` ฝั่งละ 9 บรรทัด พร้อมหัวคอลัมน์ซ้ำ | คงหน้าเปรียบเทียบ `.cmp` และย่อเหลือฝั่งละ 6 บรรทัด: volume ยังอยู่/ถูกลบ และผล `9`/`8` | `005_LAB_Compose_And_Ship/readme.md` → `## การทดลองที่ 6 — ข้อมูลคงอยู่หลัง down แต่ reset หลัง down -v ไหม` |
| U-D4 | 54 | ตาราง “ของที่ compose สร้าง” ซ้อนอยู่ใต้ transcript | แตกเป็นหน้าใหม่ 5 แถว ฟอนต์มาตรฐาน พร้อมข้อสรุปว่า `-v` เปลี่ยน named volume เท่านั้น | `005_LAB_Compose_And_Ship/readme.md` → การทดลองที่ 6 และ `## สรุปคำสั่งของแล็บนี้` |
| U-D4 | 58 | ตาราง NFR-1…3 + REQ-01…12 ห้าแถวในหน้าเดียว | แตกเป็น 2 หน้า: (ก) NFR-1 สองแถว + NFR-2 (ข) NFR-3 + REQ-01…12 และคงประโยค “คำถามเดียว…” | `readme.md` → `## ตารางแกน : ข้อจำกัดของลูกค้า → เทคนิค Docker → แล็บ` |
| U-D4 | 58 | รายละเอียดจุดพิสูจน์และถ้อยคำอธิบายยาวในแต่ละแถว | ย่อให้เหลือข้อจำกัด → เทคนิค → แล็บ โดยมี pointer ไปตารางเต็ม | `readme.md` → `## ตารางแกน : ข้อจำกัดของลูกค้า → เทคนิค Docker → แล็บ` |
| U-D4 | 59 | ดัชนี 26 แถวใน 2 ตารางข้างกัน | แตกเป็น 2 หน้า หน้าละ 13 แถวรวม header: (ก) `run` ถึง `.dockerignore` (ข) `-f` ถึง Docker Hub | `readme.md` → `## หัวข้อนี้เรียนเต็มมาจากไหน — ดัชนีกันเรียนซ้ำ (ข้ามชุด)` |
| U-D4 | 59 | หมายเหตุข้อยกเว้น `USER` และ `restart: unless-stopped` | ย้ายไปใต้ตารางหน้าที่สองและย่อถ้อยคำ ไม่ตัดสาระ | `readme.md` → `## หัวข้อนี้เรียนเต็มมาจากไหน — ดัชนีกันเรียนซ้ำ (ข้ามชุด)` |
| U-D4 | 60 | ผลลัพธ์การเรียนรู้ 7 ข้อ + สถิติ + verify + คำถามปิดอยู่หน้าเดียว | แตกเป็น 2 หน้า: (ก) ผลลัพธ์ 7 ข้อ (ข) สถิติจริง + verify + คำถามปิด | `readme.md` → `## ผลลัพธ์การเรียนรู้`, `## เวลาที่ใช้`, `## ตรวจงานอัตโนมัติ` |
| U-D4 | 60 | สถิติเก่า `45`, “แล็บละ 9 อัน”, `3:45`, `96 [PASS]` | แก้เป็น `48`, `10 · 11 · 9 · 9 · 9`, `4:15`, `100 [PASS]` ตามตารางความจริง | `deck_build/BRIEF_DECK.md` → “ตัวเลขที่เป็นความจริงของชุดนี้”; `readme.md` → `## เส้นทางแล็บ`, `## เวลาที่ใช้` |
| U-D4 | 60 | รายละเอียด safety ของ prefix `vops` | ย้ายออกจากสไลด์ เหลือ pointer “ตรวจงานอัตโนมัติ” | `readme.md` → `## ตรวจงานอัตโนมัติ` |
| U-D4 | ท้ายตอน 8 | เดิมไม่มีสไลด์ปิดตอน | เพิ่ม 4 บล็อก: ทฤษฎี 3 บรรทัด, NFR-1…3, LAB 5 = 9 การทดลอง · 50 นาที · 26 PASS + 1 SKIP, คำสั่งเปิดแล็บหนึ่งบรรทัด | `005_LAB_Compose_And_Ship/readme.md` → `### 🎯 แล็บนี้ใน 30 วินาที`, `## เตรียมเครื่องเรียน`, `## ตรวจงานด้วย verify.sh`; ตัวเลขจาก `deck_build/BRIEF_DECK.md` |

รวม **57** รายการ

## ทะเบียน waiver

ไม่มีสไลด์ใดใช้ `data-waiver` — ทุกหน้าผ่านงบโดยไม่ต้องขอยกเว้น
(ยืนยันด้วย `python3 tools/ui/check_deck.py` = `[PASS] สไลด์ 83 หน้า · ทุกหน้าอยู่ในงบ`)
