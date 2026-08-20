# แผนงาน — ยกระดับ UI/Docker Hub/GitHub ของชุด 03_Fullstack_App_Example

สถานะ: FROZEN v2 (ผ่าน critique จาก Codex แล้ว — ดูคำตัดสินข้อ 7)
วันที่: 2026-08-20

## 1. ช่องว่างที่ตรวจพบ (gap)

| # | ข้อกำหนด | สถานะปัจจุบัน | ต้องแก้ |
|---|---|---|---|
| G1 | ทุกขั้น UI ต้องมี ลำดับคลิก + screenshot จริง + marker (กรอบแดง+เลขลำดับ+ป้ายไทย) + caption | มีภาพนิ่งแล็บละ 1 ภาพ ไม่มี marker ไม่มีลำดับคลิก | สร้าง walkthrough ครบทุกแล็บที่มี UI |
| G2 | ใช้ Docker Hub จริง ไม่ใช้ registry ในเครื่อง | LAB 5 การทดลองที่ 8–9 เคยใช้ endpoint และ image ของ registry ในเครื่อง | เขียนใหม่เป็น `docker login` + push/pull บน Docker Hub จริง |
| G3 | Apply with GitHub จริง + capture หน้าเป็นหลักฐาน | มีแค่คำสั่ง `git clone` ไม่มีภาพ | เพิ่ม walkthrough หน้า GitHub (LAB 1) |
| G4 | ตัดคำสั่งตรวจสอบที่ยาว/ซับซ้อนเกินจำเป็น | รูปแบบตารางกำหนด field เอง 12 จุด + awk/sed/jq 15 จุด | กวาดทั้ง 5 แล็บ |
| G5 | Update รูป + Slide | deck 56 สไลด์ยังอ้างภาพเดิม + สไลด์ registry ในเครื่อง | rebuild deck |

## 2. เครื่องมือกลาง (U0 — ต้องเสร็จก่อน)

สร้าง `tools/` ในชุดนี้ (พอร์ตมาจากชุด `02_Dockerfile_Build_Run_Compose_Guide` ที่พิสูจน์แล้ว)

```
tools/fonts/NotoSansThai-Variable.ttf      # คัดลอกมา
tools/ui/annotate_steps.py                 # คัดลอก + ปรับ path ให้เป็น project root ของชุดนี้
tools/ui/annotations/lab1..lab5.json       # สเปก marker ต่อภาพ (สร้างใหม่)
tools/ui/raw/                              # ภาพดิบก่อนใส่ marker
tools/ui/hub_capture.py                    # ปรับจากชุดเดิม -> repo campusops-api / campusops-web
tools/ui/github_capture.py                 # ใหม่ — หน้า GitHub repo -> โฟลเดอร์แล็บ -> ปุ่ม Code
tools/ui/app_capture.py                    # ใหม่ — Swagger UI + หน้าเว็บ CampusOps
```

**อินเทอร์เฟซที่ตกลงกันแล้ว (ห้ามแก้เอง)**
- annotation spec: **ใช้ schema จริงของ `annotate_steps.py` (`shapes` / `type` / `label_at`) เท่านั้น** — ห้ามคิด key ใหม่
  ให้เปิดไฟล์เครื่องมืออ่าน schema ก่อนเขียน spec ทุกครั้ง
- marker: กรอบสี `#e11d48` หนา 5px + ป้ายไทยพื้น `#1e293b` ตัวอักษรขาว 28px + เลขลำดับวงกลม ①②③…
- ชื่อไฟล์ภาพขั้นตอน: `ui-<หัวข้อ>-NN-<slug>.png` เช่น `ui-swagger-03-execute.png`
- ทุกภาพต้องผ่าน mask: ห้ามมีชื่อบัญชีจริง/อีเมล/token — แทนด้วย `<DOCKER_USER>` `<DOCKER_TOKEN>`
- viewport มาตรฐาน 1440x900 · ซ่อน cookie banner ก่อนถ่าย

## 3. หน่วยงาน (1 LAB = 1 agent, container ≤5 ตัวใหม่)

มี container ของ session อื่นค้างอยู่ 2 ตัว (`devtools-df-lab5`, `devtools-jk-lab`) — **ห้ามแตะ**
พอร์ตที่ห้ามชน: 2235, 12224, 8185, 20800, 20080

| unit | ขอบเขต | container | พอร์ต ssh | พอร์ตแอป |
|---|---|---|---|---|
| U0 | tooling + ภาพ GitHub + ภาพ Docker Hub (รันบนโฮสต์ ไม่ใช้ container) | — | — | — |
| U1 | LAB 1: G4 + ฝัง walkthrough GitHub | `devtools-fs-lab1` | 2251 | — |
| U2 | LAB 2: G1 (Swagger UI 6 ขั้น) + G4 | `devtools-fs-lab2` | 2252 | 8252 |
| U3 | LAB 3: G1 (หน้าเว็บ CampusOps 6 ขั้น) + G4 | `devtools-fs-lab3` | 2253 | 8253 |
| U4 | LAB 4: G1 (หน้าเว็บผ่านชื่อกล่อง 4 ขั้น) + G4 (`--format` 7 จุด) | `devtools-fs-lab4` | 2254 | 8254 |
| U5 | LAB 5: G2 (Docker Hub แทน registry) + G1 + G4 + verify.sh | `devtools-fs-lab5` | 2255 | 8255 |
| U6 | Integration: deck + root readme + ตรวจข้ามแล็บ | — | — | — |

ลำดับ: U0 → (U1–U5 ขนาน) → U6

## 4. รายละเอียด walkthrough ที่ต้องได้

### LAB 1 — GitHub (3 ขั้น, ใส่ในหัวข้อ "ขั้นที่ 2 — โหลดโค้ดแล็บ")
1. หน้า repo `github.com/Tuchsanai/DevTools` — กรอบที่ชื่อ repo + ป้าย "① เปิดหน้า repository"
2. คลิกเข้าโฟลเดอร์ `02_Docker/03_Fullstack_App_Example` — กรอบที่แถวโฟลเดอร์
3. ปุ่ม `Code` เขียว → แท็บ HTTPS → ไอคอนคัดลอก URL — กรอบสามจุด ③④⑤

### LAB 2 — Swagger UI (6 ขั้น)
เปิด `/docs` → คลิกแถว `GET /api/dashboard` → `Try it out` → `Execute` → อ่าน `Response body` 200 →
คลิก `POST /api/tickets` แล้ว Execute ได้ `201`

### LAB 3 — หน้าเว็บ CampusOps (6 ขั้น)
หน้าแรก → เมนูซ้าย "กระดานงานซ่อม" → กรอกฟอร์มแจ้งซ่อมใหม่ → กดบันทึก →
การ์ดใหม่โผล่ในคอลัมน์ "รอรับเรื่อง" → กดปุ่มเลื่อนสถานะเป็น "มอบหมายแล้ว"

### LAB 4 — หน้าเว็บที่ต่อกันด้วยชื่อกล่อง (4 ขั้น)
เปิดหน้าสรุป → คลิกเมนู "ครุภัณฑ์" → คลิกเมนู "อะไหล่" → กลับหน้าสรุปเห็นตัวเลขตรงกับ requirements

### LAB 5 — Docker Hub (9 ขั้น) + repo หลัง push (3 ขั้น) + ลบ repo (2 ขั้น)
สร้าง Access Token: `hub.docker.com` → Sign in → รหัสผ่าน → avatar → Account settings →
Personal access tokens → Generate new token → ตั้ง description/expiration/สิทธิ์ → คัดลอก token
หลัง push: Repositories → เปิด `<DOCKER_USER>/campusops-api` → แท็บ Tags เห็น `1.0` + digest
เก็บกวาด: Settings ของ repo → Delete repository

## 5. LAB 5 — สิ่งที่เปลี่ยนจาก registry ในเครื่อง เป็น Docker Hub

- การทดลองที่ 8: `docker login -u <DOCKER_USER>` (วาง token) → `docker tag campusops-api:latest <DOCKER_USER>/campusops-api:1.0`
  → `docker push` ทั้งสองก้อน → เปิดหน้า Hub ดูของจริง (screenshot + marker)
- การทดลองที่ 9: ลบ image ทุกก้อนในเครื่อง → `docker pull <DOCKER_USER>/campusops-api:1.0` และ `docker pull <DOCKER_USER>/campusops-web:1.0` (แยกคำสั่ง ห้ามใช้ wildcard) → tag กลับเป็นชื่อใน compose
  → `docker compose up -d --no-build` ต้องไม่มีบรรทัด `Building`
- เก็บกวาด: `docker logout` + ลบ repository บน Hub (UI 2 ขั้น)
- `verify.sh`: ตัดขั้นยก image ของ registry ในเครื่องออก · เพิ่มการตรวจว่าชื่อ `<DOCKER_USER>/campusops-*:1.0` มีในเครื่อง
  และ `docker compose up --no-build` ขึ้นได้ · ถ้าไม่ได้ `docker login` ให้รายงาน `[SKIP]` พร้อมเหตุผล ไม่ใช่ `[FAIL]`
- ตาราง "แก้ปัญหาที่พบบ่อย": `denied: requested access to the resource is denied`,
  `unauthorized: incorrect username or password`, `pull access denied`, `docker login` ผ่าน token ไม่ใช่รหัสผ่าน

## 6. เกณฑ์ตรวจรับ (DoD ต่อ unit)

1. รันจริงบน `tuchsanai/devtools:2569_1` — log ที่ `logs/<unit>.log`
2. expected output ในเอกสาร = ผลรันจริง (คัดลอกมา ไม่ใช่แต่งขึ้น)
3. ภาพขั้นตอนครบทุกขั้น ไม่ขาดช่วง · ทุกภาพมี marker + caption ภาษาไทยใต้ภาพ
4. ไม่มีชื่อบัญชี/อีเมล/token จริงในเอกสารและในภาพ
5. `verify.sh` ของแล็บนั้นผ่าน
6. ลบ container ของตัวเองก่อนส่งงาน · ไม่มี image/volume ทดสอบค้าง

---

## 7. คำตัดสินหลัง critique (Claude, 2026-08-20) — ACCEPT พร้อมแก้ 12 ข้อ

**รับทั้งหมด** ข้อวิจารณ์ต่อไปนี้ถือเป็นส่วนหนึ่งของแผนที่ freeze แล้ว

1. **schema ของ annotation** — แผนเดิมคิด key `markers`/`masks` ขึ้นเอง แต่เครื่องมือจริงใช้ `shapes`/`type`/`label_at`
   → ยึด schema ของเครื่องมือ ทุก unit ต้องอ่านไฟล์เครื่องมือก่อนเขียน spec
2. **LAB 2 ลำดับไม่ครบ** — ต้องมีขั้นกรอก JSON body ก่อน Execute ของ `POST /api/tickets` (บังคับ `asset_id`, `title`, `priority`) และคืน `201`
   ลำดับที่ถูก 9 ขั้น: เปิด `/docs` → กาง `GET /api/dashboard` → Try it out → Execute → อ่าน 200 →
   กาง `POST /api/tickets` → Try it out → แก้ JSON ใน Request body → Execute → อ่าน 201
3. **LAB 3 ลำดับผิด** — ไม่มีปุ่มชื่อ "มอบหมายแล้ว" (นั่นคือชื่อ *สถานะ*) ปุ่มจริงคือ **มอบหมาย** และต้องกรอก "ชื่อช่าง" บนการ์ดก่อน
   ลำดับที่ถูก: หน้าแรก → กระดานงานซ่อม → เลือกครุภัณฑ์/หัวข้อ/รายละเอียด/ความเร่งด่วน → กด **แจ้งซ่อม** →
   การ์ดโผล่ใน **รอรับเรื่อง** → กรอกชื่อช่างบนการ์ด → กด **มอบหมาย** → การ์ดย้ายไป **มอบหมายแล้ว**
4. **LAB 4 ต้องระบุตัวเลขจริงจาก seed** ที่คาดว่าจะเห็น ไม่ใช่คำว่า "ตรงกับ requirements"
5. **ข้อมูลตอนถ่ายภาพต้องนิ่ง** — reset ฐานข้อมูลให้เป็น seed ก่อน capture ทุกครั้ง และกรอกข้อความเดิมทุกรอบ
   ไม่งั้นตัวเลขบน dashboard กับตำแหน่งการ์ดจะไม่ตรงกับ caption
6. **Docker Hub** — repository ถูกสร้างอัตโนมัติตอน push แต่ต้องกำหนดให้ **public** ให้ชัด
   (บัญชี Personal มี private repo ได้แห่งเดียว) และเอกสารต้องเตือนเรื่อง pull rate limit
   (ไม่ล็อกอิน 100 ครั้ง/6 ชม./IP · ล็อกอินแล้ว 200 ครั้ง/6 ชม./บัญชี) พร้อมวิธีรับมือเมื่อเจอ `429`
7. **`docker logout` ไม่ได้ทำให้ token หมดอายุ** — เอกสารต้องบอกให้ revoke Personal Access Token บนหน้า Hub ด้วย
   และเตือนว่า credential ถูกเขียนไว้ที่ `/root/.docker/config.json` ในกล่องเรียน
8. **ขั้นลบ repository ไม่ใช่ 2 คลิก** — ของจริงคือ My Hub → Repositories → เปิด repo → Settings → Delete →
   พิมพ์ชื่อ repo ยืนยัน → Delete Repository Forever · ต้องเก็บภาพครบทุกขั้น
9. **ช่องโหว่ความลับใน `hub_capture.py` ต้นแบบ** — mask ทำเฉพาะ text node ไม่ครอบคลุมค่าใน `<input>`
   จึงอาจถ่ายติด PAT จริงในหน้า "คัดลอก token" · และเขียน storage state ลง `.hub_state.json`
   → U0 ต้อง mask ค่าของ input ด้วย · เพิ่ม `.gitignore` ปิด `tools/ui/raw/.hub_state.json` · ลบ state หลัง capture
   → ก่อนส่งงานต้องตรวจภาพทุกใบว่าไม่มี prefix ของ token จริง อีเมล หรือชื่อบัญชีจริง
10. **`hub_capture.py` ต้องรองรับสอง repository** (`campusops-api`, `campusops-web`) ไม่ใช่ค่าคงที่ตัวเดียว
    และต้องตรวจ Tags ของทั้งสองก้อน · cleanup ทั้งสองก้อน
11. **`verify.sh` ของ LAB 5 — ห้าม push หรือลบ repository จริง**
    ส่วนที่บังคับตรวจได้โดยไม่ต้องมีบัญชี Hub: compose schema · healthcheck/ลำดับ depends_on · up ครบ ·
    db ไม่ publish port · HTTP 4 หน้า · DNS web→api · persistence · reset seed ·
    **พิสูจน์การส่งมอบแบบออฟไลน์**: tag ด้วย namespace ทดสอบในเครื่อง → ตรวจว่า IMAGE ID เดิม →
    `docker save` → ลบ → `docker load` → tag กลับ → `compose up -d --no-build` → healthy + HTTP + log ไม่มี `Building`
    ส่วน remote (pull จาก Hub จริง) เป็น **opt-in ด้วย env `HUB_USER`** ถ้าไม่มีให้ `[SKIP]` และยัง exit 0
    ต้องอัปเดตจำนวน `[PASS]` ในเอกสารให้ตรงกับของจริง (เดิมเขียนไว้ 22)
12. **เกณฑ์ตรวจรับเพิ่ม** — ภาพทุกใบขนาด 1440×900 · spec parse ได้ · caption/ลิงก์ภาพไม่เสีย ·
    ไม่มี PAT/อีเมล/ชื่อบัญชี/cookie state หลุด · cleanup ตรวจเฉพาะ prefix ของ unit ตัวเอง
    (ห้ามใช้เกณฑ์ "ไม่มี container/image ค้างทั้งเครื่อง" เพราะมี session อื่นทำงานอยู่) ·
    หลัง U6 ต้องไม่เหลือ endpoint, image, ชื่อ container และพอร์ตของ registry ในเครื่องชุดเดิมที่ใดในชุด
