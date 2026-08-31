# LAB 002 — Docker Compose: Web · API · Database

แล็บนี้นำระบบ **SkillSpace** ทั้งชุดขึ้นด้วย Docker Compose เพียงคำสั่งเดียว แล้วทดลอง User Flow ของระบบแจ้งซ่อมจากหน้า 20–25 ใน `Fullstack_Slides.html`

## เป้าหมาย

เมื่อจบแล็บ ผู้เรียนจะสามารถ:

1. อธิบายเส้นทาง `browser → web → api → db` ได้
2. อ่าน `compose.yaml` และเข้าใจ `build`, `environment`, `ports`, `volumes`, `healthcheck` และ `depends_on`
3. เปิดระบบ 3 Container ด้วยคำสั่งเดียว
4. ทดลองสร้าง มอบหมาย ดำเนินการ และปิดใบแจ้งซ่อม
5. ตรวจ Flow ยืม–คืนและคลังอะไหล่ รวมทั้งกรณีที่ระบบต้องปฏิเสธ
6. พิสูจน์ว่า database ไม่เปิดพอร์ตออกภายนอก และข้อมูลอยู่รอดเมื่อสร้าง Container ใหม่

## ภาพรวมระบบ

```text
Browser
  │ http://localhost:8252
  ▼
web (Next.js :3000)
  │ http://api:8000
  ▼
api (FastAPI :8000)
  │ postgresql://db:5432/skillspace
  ▼
db (PostgreSQL :5432) ── pgdata volume
```

มีเพียง `web` ที่ publish port ออกมาที่เครื่องผู้เรียน ส่วน `api` และ `db` อยู่ใน Compose network ภายใน

## ไฟล์สำคัญ

```text
002_LAB_Docker_Compose/
├── compose.yaml
├── verify.sh
├── api/
│   ├── Dockerfile
│   ├── main.py
│   ├── requirements.txt
│   └── smoke.sh
├── web/
│   ├── Dockerfile
│   ├── app/
│   └── package.json
└── db/
    ├── Dockerfile
    └── initdb/
        ├── 01-schema.sql
        └── 02-seed.sql
```

## เตรียมเครื่องเรียน

รันคำสั่งนี้จากเครื่องหลักเพื่อสร้าง Container สำหรับทำแล็บ:

```bash
docker rm -f devtools-fs-lab2 2>/dev/null || true
docker run -dit --name devtools-fs-lab2 --privileged \
  -p 2252:22 -p 8252:3000 <LAB_IMAGE>
ssh root@localhost -p 2252
```

ภายในเครื่องเรียน:

```bash
cd ~/labwork/DevTools/02_Docker/03_Fullstack_App_Example/002_LAB_Docker_Compose
docker version
docker compose version
```

> `--privileged` ใช้เฉพาะ Container สำหรับเรียนแบบใช้แล้วทิ้ง เพื่อให้รัน Docker ซ้อนข้างใน ไม่ใช่รูปแบบสำหรับ production

## การทดลองที่ 1 — อ่าน Compose ก่อนรัน

เปิด `compose.yaml` แล้วหาให้ครบ:

- `db` build จาก `postgres:17-alpine`, bake schema/seed เข้า image, มี healthcheck และ volume `pgdata`
- `api` build จาก `./api`, ติดต่อฐานข้อมูลด้วย hostname `db`
- `web` build จาก `./web`, ติดต่อ API ด้วย hostname `api`
- `depends_on: condition: service_healthy` ทำให้ service ถัดไปรอ service ก่อนหน้าพร้อม
- มีเพียง `web` ที่มี `ports`

ตรวจ syntax และค่าที่ Compose จะใช้จริง:

```bash
docker compose config --services
docker compose config
```

ผลที่คาดหวัง: เห็น service `db`, `api`, `web` และไม่มี error

## การทดลองที่ 2 — เปิดระบบด้วยคำสั่งเดียว

```bash
docker compose up -d --build
docker compose ps
```

รอจนทั้งสาม service เป็น `healthy` แล้วเปิด:

```text
http://localhost:8252
```

ถ้าทำแล็บโดยตรงบนเครื่องเดียวกับ Docker ให้ใช้ `http://localhost:3000`

ดูเหตุการณ์เริ่มระบบ:

```bash
docker compose logs --tail=80 db api web
```

สังเกตลำดับ `db → api → web` และแยกให้ออกว่า `running` หมายถึง process ทำงาน ส่วน `healthy` หมายถึงผ่าน healthcheck

## การทดลองที่ 3 — ตรวจขอบเขตเครือข่าย

```bash
docker compose ps
docker compose exec web wget -qO- http://api:8000/health
docker compose exec api python -c "import socket; print(socket.gethostbyname('db'))"
```

ผลที่คาดหวัง:

- web เรียก api ด้วยชื่อ `api`
- api resolve ชื่อ `db` ได้
- หน้าเว็บเปิดจากภายนอกได้ แต่ api และ db ไม่มี published port
- ไม่ต้องหา IP ของ Container และไม่ต้องเขียน `localhost` เพื่อให้ Container คุยกัน

## การทดลองที่ 4 — อ่านค่าเริ่มต้นบน Overview

เปิดหน้า `Overview` และบันทึกค่าก่อนทดลอง:

| ค่า | Seed เริ่มต้น |
|---|---:|
| งานที่ยังไม่เสร็จ | 6 |
| งานสถานะ ASSIGNED | 2 |
| งานของ TECH-04 | 0 |
| อะไหล่ต่ำกว่าจุดสั่งซื้อ | 2 รายการ |

จากนั้นเปิด `Tickets` และตรวจว่ากระดานมี 4 สถานะ:

```text
NEW → ASSIGNED → IN_PROGRESS → DONE
```

## การทดลองที่ 5 — สร้างใบแจ้งซ่อม

ที่หน้า `Tickets` กรอกฟอร์ม:

| ช่อง | ค่าทดลอง |
|---|---|
| ครุภัณฑ์ | `A-003` |
| หัวข้อ | `โปรเจกเตอร์ภาพกะพริบ` |
| รายละเอียด | `ภาพกะพริบหลังเปิดประมาณ 10 นาที` |
| ความเร่งด่วน | `HIGH` |

กดสร้าง แล้วตรวจหลักฐานสามจุด:

1. มีข้อความสำเร็จ
2. การ์ดใหม่อยู่ในคอลัมน์ `NEW`
3. จำนวน `NEW` เพิ่มหนึ่ง โดยการ์ดไม่หายหลัง refresh

กลับหน้า Overview: งานที่ยังไม่เสร็จควรเปลี่ยนจาก 6 เป็น 7

## การทดลองที่ 6 — มอบหมายงานให้ TECH-04

บนการ์ดใบเดิม เลือก `TECH-04` แล้วกดมอบหมาย

ตรวจว่า:

- ticket id เดิมย้ายจาก `NEW` ไป `ASSIGNED`
- การ์ดแสดง assignee เป็น `TECH-04`
- จำนวน `ASSIGNED` เปลี่ยนจาก 2 เป็น 3
- Overview แสดงงานของ `TECH-04` เป็น 1
- การกรองด้วย `TECH-04` แสดงใบนี้ และไม่ปนงานของช่างคนอื่น

## การทดลองที่ 7 — ดำเนินงานและปิดงาน

1. เลื่อนใบเดิมจาก `ASSIGNED` เป็น `IN_PROGRESS`
2. ปิดงานจาก `IN_PROGRESS` เป็น `DONE`
3. ถ้าต้องการทดลองอะไหล่ ให้เลือก `KBD-USB-01` จำนวน 1 ก่อนปิด

ตรวจว่า ticket id ยังเป็นใบเดิม, `closed_at` มีค่า, งานออกจากยอดงานค้าง และจำนวนอะไหล่ลดลงหนึ่งพร้อมมีประวัติการเบิกที่อ้างถึง ticket นี้

> ระบบไม่อนุญาตให้ข้าม `NEW → DONE` เพราะ State ต้องเดินทีละขั้น

## การทดลองที่ 8 — ทดลอง Flow ที่ระบบต้องปฏิเสธ

### 8.1 ยืมของที่ยังไม่ถูกคืน

เปิด `Loans` แล้วลองยืม `A-001` หรือ `A-002` ซึ่งมีรายการยืมค้างอยู่

ผลที่คาดหวัง: ระบบปฏิเสธด้วย `ASSET_ON_LOAN` และบอกผู้ยืมปัจจุบัน

### 8.2 ยืมของที่กำลังซ่อม

สร้างใบซ่อมใหม่ให้ครุภัณฑ์ที่ว่าง แล้วลองยืมครุภัณฑ์ชิ้นนั้นก่อนปิดงาน

ผลที่คาดหวัง: ระบบปฏิเสธด้วย `ASSET_IN_REPAIR`

### 8.3 ตรวจอะไหล่ต่ำกว่าจุดสั่งซื้อ

เปิด `Parts` แล้วตรวจว่ามีสองรายการติดป้าย `ต้องสั่งเพิ่ม` จากเงื่อนไข:

```text
qty_on_hand < reorder_point
```

## การทดลองที่ 9 — พิสูจน์ Persistence

ก่อนหยุดระบบ ให้จำ ticket ที่เพิ่งสร้างไว้ แล้วรัน:

```bash
docker compose down
docker compose up -d
docker compose ps
```

เปิดหน้าเว็บอีกครั้ง: ticket ต้องยังอยู่ เพราะ `docker compose down` ไม่ลบ named volume

จากนั้นทดลอง reset ข้อมูล:

```bash
docker compose down -v
docker compose up -d
```

ข้อมูลต้องกลับเป็น seed เริ่มต้น เพราะ volume ใหม่ทำให้ `db/initdb/` รันอีกครั้ง

## การทดลองที่ 10 — ตรวจงานอัตโนมัติ

```bash
bash verify.sh
echo "exit code = $?"
```

เมื่อผ่านจะเห็น `ALL CHECKS PASSED` และ exit code `0` สคริปต์ใช้ Compose project สำหรับตรวจสอบแยกจากระบบที่ผู้เรียนเปิดอยู่

## แก้ปัญหาที่พบบ่อย

| อาการ | ตรวจ | วิธีแก้ |
|---|---|---|
| service ไม่ healthy | `docker compose ps` | `docker compose logs <service>` |
| web เรียก api ไม่ได้ | `docker compose exec web wget -qO- http://api:8000/health` | ตรวจ `API_BASE_URL` และชื่อ service `api` |
| api ต่อ db ไม่ได้ | `docker compose logs api db` | ตรวจ `DATABASE_URL` และ healthcheck ของ db |
| พอร์ต 3000 ถูกใช้ | `docker compose down` | ปิดระบบเดิมหรือเปลี่ยนพอร์ตด้านซ้ายใน `compose.yaml` |
| ข้อมูลไม่กลับเป็น seed | `docker volume ls` | ใช้ `docker compose down -v` แล้วเปิดใหม่ |

## เก็บกวาด

เก็บข้อมูลไว้ใช้ต่อ:

```bash
docker compose down
```

ลบทั้ง Container, network และข้อมูลของแล็บ:

```bash
docker compose down -v --remove-orphans
```

## สรุป

LAB 001 แยกให้เห็นว่า PostgreSQL เก็บข้อมูลอย่างไร ส่วน LAB 002 นำ `web`, `api` และ `db` มาประกอบเป็นระบบเดียว ทดลอง User Flow จริง และพิสูจน์ NFR ด้วย Docker Compose
