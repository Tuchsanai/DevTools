# LAB 1 — ยกฐานข้อมูลของลูกค้าขึ้นมา แล้วทำให้ข้อมูลไม่หาย

> โฟลเดอร์ `001_LAB_Run_The_System` · ไฟล์ของแล็บ : `db/initdb/01-schema.sql` · `db/initdb/02-seed.sql` · `.env.db` · `verify.sh`

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | ทำอย่างไรให้ฐานข้อมูลของลูกค้าขึ้นมาพร้อมข้อมูลจริง และ **ข้อมูลไม่หาย** แม้ลบกล่องทิ้งแล้วสร้างใหม่ (NFR-2) |
| **ต้องผ่านอะไรมาก่อน** | ชุด `01_Docker_Basics_Run_Port_Volume_Build` — แล็บนี้ใช้ของเดิมล้วน ๆ : `docker run` · `ps` · `logs` · `exec` · `rm` · `-e` · `-v` |
| **เวลา** | ~40 นาที · การทดลอง **9 อัน** อันละ 3–5 นาที |
| **จบแล้วต้องทำได้เอง** | ยก `postgres:17-alpine` ขึ้นพร้อม schema + ข้อมูลตั้งต้น · อ่าน log ตอนบูตเป็น · ชี้ได้ว่าข้อมูลหายตอนไหนและ named volume แก้อย่างไร |
| **แล็บนี้ยัง *ไม่* สอน** | ต่อกล่องเข้าหากันด้วย network → **LAB 4** · `compose.yaml` → **LAB 5** (ดูแผนทั้งชุดที่ [`docs/01_requirements.md`](../docs/01_requirements.md)) · ไม่มี ORM / migration tool · ยังไม่ publish พอร์ตฐานข้อมูลออกเครื่องเลย (NFR-3) |

---

## ทฤษฎีก่อนลงมือ

### ระบบของลูกค้ามี 3 กล่อง — แล็บนี้ทำกล่องเดียว

![แผนภาพระบบ CampusOps สามกล่อง เบราว์เซอร์เรียก web ซึ่งเรียก api และ api เรียก db โดยกล่อง db เป็นกล่องที่แล็บนี้ทำและผูกกับ named volume ชื่อ ops-pgdata](./images/theory-three-boxes.svg)

> 🖼 **วิธีอ่านรูปนี้:** กล่องขวาสุดที่ตีกรอบหนาคือขอบเขตของแล็บนี้ · กล่อง `web` กับ `api` ยังไม่ต้องมีตัวตนวันนี้ · ลูกศรสีเขียวที่ลงล่างคือที่ที่ข้อมูลไปนอนจริง ซึ่งเป็นหัวใจของ NFR-2

ลูกค้าพูดไว้ในบทสัมภาษณ์ว่า **"ข้อมูลยืม-คืนย้อนหลังห้ามหาย แม้ต้องย้ายเครื่องหรือ restart"** — ประโยคเดียวนี้กลายเป็น `NFR-2`
และเป็นเหตุผลทั้งหมดที่แล็บนี้มีอยู่

### 5 ตารางที่ต้องมี

| ตาราง | เก็บอะไร | รับผิดชอบ REQ |
|---|---|---|
| `assets` | ครุภัณฑ์ 180 ชิ้นของคณะ (แล็บใช้ 12 ชิ้น) | REQ-01, REQ-10, REQ-11 |
| `tickets` | ใบแจ้งซ่อม + สถานะ `NEW → ASSIGNED → IN_PROGRESS → DONE` | REQ-01 … REQ-04, REQ-08 |
| `loans` | สัญญายืม-คืน (`returned_at IS NULL` = ยังไม่คืน) | REQ-10 |
| `parts` | อะไหล่และจุดสั่งซื้อ | REQ-06, REQ-12 |
| `stock_moves` | ประวัติเบิก/รับเข้าอะไหล่ | REQ-05, REQ-07 |

ทั้งหมดอยู่ในไฟล์ `db/initdb/01-schema.sql` และข้อมูลตั้งต้นอยู่ใน `db/initdb/02-seed.sql`
**เราไม่แก้สองไฟล์นี้ในแล็บ** — หน้าที่ของเราคือทำให้มันถูกรันถูกที่ถูกเวลา

### ข้อมูลของ PostgreSQL ไปนอนอยู่ที่ไหน

![แผนภาพเปรียบเทียบสองแบบ ซ้ายคือกล่องที่ไม่ผูก volume ข้อมูลอยู่ใน writable layer และหายเมื่อ docker rm ขวาคือกล่องที่ผูก named volume ops-pgdata แล้วข้อมูลยังอยู่หลังลบกล่อง](./images/theory-where-is-data.svg)

> 🖼 **วิธีอ่านรูปนี้:** เทียบกล่องสองฝั่งที่ **จุดเดียวกัน** คือบรรทัด `docker rm -f ops-db` · ฝั่งซ้ายกล่องหายแล้วข้อมูลหายด้วยเพราะข้อมูลอยู่ในตัวกล่อง · ฝั่งขวาข้อมูลไม่เคยอยู่ในกล่องตั้งแต่แรก

### init script ทำงานตอนไหน

![ผังตัดสินใจของ entrypoint ของ postgres ถ้า data directory ว่างจะรันไฟล์ใน docker-entrypoint-initdb.d เรียงตามชื่อ ถ้ามีข้อมูลอยู่แล้วจะขึ้น Skipping initialization และข้ามไฟล์ทั้งหมด](./images/theory-initdb-when.svg)

> 🖼 **วิธีอ่านรูปนี้:** จุดตัดสินอยู่ที่สี่เหลี่ยมข้าวหลามตัดกลางรูป — คำถามคือ *"data directory ว่างไหม"* ไม่ใช่ *"กล่องนี้ใหม่หรือเก่า"* · สองกิ่งซ้าย-ขวาให้ log คนละบรรทัด ซึ่งเราจะเห็นทั้งคู่ในแล็บนี้

### สิ่งที่มักเข้าใจผิด

- **คิดว่า** ไม่ใส่ `POSTGRES_PASSWORD` ก็รันได้ เดี๋ยว image ตั้งค่า default ให้เอง → **จริง ๆ** กล่องหยุดทันทีตั้งแต่วินาทีแรก (การทดลองที่ 1)
- **คิดว่า** ลบกล่องแล้วข้อมูลยังอยู่ เพราะ image ยังอยู่ → **จริง ๆ** ข้อมูลอยู่ใน writable layer ที่ตายพร้อมกล่อง ส่วน image เป็นแค่แม่พิมพ์ (การทดลองที่ 6)
- **คิดว่า** แก้ไฟล์ใน `db/initdb/` แล้วสร้างกล่องใหม่ก็มีผลเสมอ → **จริง ๆ** ถูกข้ามทันทีที่ volume ไม่ว่าง (การทดลองที่ 9)
- **คิดว่า** `--env-file` ให้ผลต่างจาก `-e` → **จริง ๆ** ได้ตัวแปรชุดเดียวกันเป๊ะ ต่างแค่ที่เก็บค่า (การทดลองที่ 8)

---

## เตรียมเครื่องเรียน

### ขั้นที่ 1 — เปิดกล่องเรียน

รันบน **เครื่องของเราเอง** — แล็บนี้ไม่ต้องเปิดพอร์ตแอปเลย เพราะเราคุยกับฐานข้อมูลผ่าน `docker exec` :

```bash
docker rm -f devtools-ops-lab1 2>/dev/null
docker run -dit --name devtools-ops-lab1 --privileged -p 2238:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2238        # password : passwd
```

### ขั้นที่ 2 — โหลดโค้ดแล็บ

**คำสั่งทุกอันหลังจากนี้พิมพ์ข้างในกล่องเรียน**

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/03_Fullstack_App_Example/001_LAB_Run_The_System
ls db/initdb
```

✅ **สิ่งที่ต้องเห็น** — ไฟล์ SQL สองไฟล์ที่จะกลายเป็นฐานข้อมูลของลูกค้า :

```
01-schema.sql  02-seed.sql
```

> 📝 **ชื่อไฟล์ขึ้นต้นด้วยตัวเลขโดยตั้งใจ** — entrypoint ของ postgres รันไฟล์เรียงตามชื่อ ถ้า seed รันก่อน schema ตารางยังไม่มี งานพัง

---

## การทดลองที่ 1 — ยกฐานข้อมูลขึ้นด้วย `docker run`

**คำถาม:** ต้องบอกอะไร `postgres:17-alpine` บ้าง กล่องถึงจะยอมขึ้น

```bash
docker run -d --name ops-db-nopass postgres:17-alpine   # จงใจไม่ใส่ -e อะไรเลย
sleep 3
docker logs ops-db-nopass 2>&1 | head -3
```

✅ **สิ่งที่ต้องเห็น** — กล่อง **ไม่ขึ้น** เพราะ image ปฏิเสธที่จะสร้างฐานข้อมูลให้ พร้อมบอกวิธีแก้มาในข้อความเดียวกัน :

```
Error: Database is uninitialized and superuser password is not specified.
       You must specify POSTGRES_PASSWORD to a non-empty value for the
       superuser. For example, "-e POSTGRES_PASSWORD=password" on "docker run".
```

ใส่ค่าให้ครบตามที่ [`docs/02_contract.md`](../docs/02_contract.md) กำหนด แล้วรันใหม่ :

```bash
docker rm -f ops-db-nopass
docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass postgres:17-alpine
sleep 8
docker ps --filter name=ops-db --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
```

✅ **สิ่งที่ต้องเห็น** — คราวนี้กล่อง **ขึ้นแล้ว** : `STATUS` เป็น `Up ...` (เวลาที่ขึ้นของแต่ละคนต่างกัน · คอลัมน์ `PORTS` มีแค่ `5432/tcp` ไม่มี `0.0.0.0:...->` เพราะเราไม่ได้สั่ง `-p` เลย ตาม NFR-3) :

```
NAMES     IMAGE                STATUS         PORTS
ops-db    postgres:17-alpine   Up 8 seconds   5432/tcp
```

> 📝 **บทเรียน:** `-e` คือช่องทางเดียวที่เราตั้งค่า image สำเร็จรูปได้ · `docker logs` ของกล่องที่ดับต้องอ่านด้วย `2>&1` เพราะข้อความเตือนออกทาง stderr

---

## การทดลองที่ 2 — อ่าน log ตอนบูต

**คำถาม:** ระหว่างที่เรารอ 8 วินาที postgres ทำอะไรไปบ้าง

```bash
docker logs ops-db 2>&1 | grep -E 'init process complete|ready to accept connections'
```

✅ **สิ่งที่ต้องเห็น** — คำว่า `ready to accept connections` โผล่ **สองครั้ง** โดยมี `init process complete` คั่นกลาง (เวลาและเลข process ของแต่ละคนต่างกัน) :

```
2026-08-17 13:15:23.566 UTC [41] LOG:  database system is ready to accept connections
PostgreSQL init process complete; ready for start up.
2026-08-17 13:15:24.236 UTC [1] LOG:  database system is ready to accept connections
```

> 📝 **บทเรียน:** ครั้งแรกคือเซิร์ฟเวอร์ชั่วคราวที่เปิดไว้เพื่อสร้างฐานข้อมูล ครั้งที่สองคือของจริงที่เรารอ · ถ้าเห็นแค่ครั้งแรกแปลว่าตอน init มีอะไรพัง

---

## การทดลองที่ 3 — เข้าไปใช้ `psql` ในกล่อง

**คำถาม:** ฐานข้อมูล `campusops` ที่เพิ่งเกิด มีตารางของลูกค้าอยู่แล้วหรือยัง

```bash
docker exec -it ops-db psql -U opsuser -d campusops -c '\dt'
```

✅ **สิ่งที่ต้องเห็น** — ต่อติดแต่ **ว่างเปล่า** :

```
Did not find any relations.
```

> 📝 **บทเรียน:** `-e POSTGRES_DB` สร้างได้แค่ฐานข้อมูล**เปล่า** · ตารางกับข้อมูลเป็นหน้าที่ของเราที่ต้องหาทางส่งเข้าไป

---

## การทดลองที่ 4 — ส่ง schema + seed เข้าไปด้วย bind mount

**คำถาม:** ทำอย่างไรให้ไฟล์ `.sql` ของเราถูกรันตอนฐานข้อมูลเกิด

```bash
docker rm -f ops-db          # ต้องลบกล่องเก่าก่อน เพราะ initdb รันแค่ตอนฐานข้อมูลเกิดใหม่
docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
sleep 10        # รอ init script รันไฟล์ .sql ให้ครบก่อนถาม
```

```bash
docker exec ops-db psql -U opsuser -d campusops -c '\dt'
```

✅ **สิ่งที่ต้องเห็น** — ครบ **5 ตาราง** ตามสัญญาใน [`docs/02_contract.md`](../docs/02_contract.md) และเจ้าของคือ `opsuser` :

```
           List of relations
 Schema |    Name     | Type  |  Owner
--------+-------------+-------+---------
 public | assets      | table | opsuser
 public | loans       | table | opsuser
 public | parts       | table | opsuser
 public | stock_moves | table | opsuser
 public | tickets     | table | opsuser
(5 rows)
```

> 📝 **บทเรียน:** `/docker-entrypoint-initdb.d` คือ "ช่องรับไฟล์" ที่ image ของ postgres เตรียมไว้ให้ · `:ro` ทำให้กล่องเขียนทับไฟล์ต้นฉบับบนเครื่องไม่ได้

---

## การทดลองที่ 5 — ข้อมูลตั้งต้นตรงกับที่ requirements บอกไหม

**คำถาม:** seed ที่เพิ่งถูกรัน ให้จำนวนตรงกับที่เขียนไว้ใน [`docs/01_requirements.md`](../docs/01_requirements.md) หรือเปล่า

```bash
docker exec ops-db psql -U opsuser -d campusops -c \
"SELECT (SELECT count(*) FROM assets) AS assets, (SELECT count(*) FROM tickets) AS tickets, (SELECT count(*) FROM loans) AS loans, (SELECT count(*) FROM parts) AS parts;"
```

✅ **สิ่งที่ต้องเห็น** — ครุภัณฑ์ **12** · ใบแจ้งซ่อม **8** · สัญญายืม **3** · อะไหล่ **6** :

```
 assets | tickets | loans | parts
--------+---------+-------+-------
     12 |       8 |     3 |     6
(1 row)
```

> 📝 **บทเรียน:** ตัวเลขชุดนี้คือ "สัญญา" ระหว่างแล็บ — LAB 2 จะเอาไปทดสอบ API ต่อ ถ้าตัวเลขเพี้ยนตั้งแต่ตรงนี้ แล็บถัดไปจะพังทั้งชุด

---

## การทดลองที่ 6 — ลบกล่องแล้วสร้างใหม่ ข้อมูลที่เพิ่มเองยังอยู่ไหม

**คำถาม:** ใบแจ้งซ่อมที่ลูกค้าแจ้งเข้ามาหลังระบบขึ้นแล้ว รอดการสร้างกล่องใหม่ไหม

```bash
docker exec ops-db psql -U opsuser -d campusops -c \
"INSERT INTO tickets (asset_id, title, detail, priority) VALUES (4, 'ไมโครโฟนห้องประชุมใหญ่เสียงขาด', 'แจ้งเข้ามาหลังระบบขึ้นแล้ว', 'HIGH');"
docker exec ops-db psql -U opsuser -d campusops -c 'SELECT count(*) FROM tickets;'
```

✅ **สิ่งที่ต้องเห็น** — จาก 8 ใบเป็น **9 ใบ** :

```
INSERT 0 1
 count
-------
     9
(1 row)
```

ทีนี้ลบกล่องแล้วสร้างใหม่ด้วยคำสั่งเดิมทุกตัวอักษร :

```bash
docker rm -f ops-db
docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
sleep 10        # รอกล่องใหม่บูตและรัน init script ให้เสร็จก่อนถาม
```

```bash
docker exec ops-db psql -U opsuser -d campusops -c 'SELECT count(*) FROM tickets;'
```

✅ **สิ่งที่ต้องเห็น** — กลับมาเป็น **8 ใบ** · ใบที่ลูกค้าแจ้งเข้ามา **หายถาวร** :

```
 count
-------
     8
(1 row)
```

> 📝 **บทเรียน:** นี่คือปัญหาจริงข้อ NFR-2 ของลูกค้า · เลข 8 ที่กลับมาไม่ใช่ข้อมูลเดิม แต่เป็น seed ที่ init script ใส่ให้ใหม่ทั้งชุด

---

## การทดลองที่ 7 — ผูก named volume แล้วทำซ้ำ

**คำถาม:** ย้ายข้อมูลออกไปไว้นอกกล่อง แล้วผลจะต่างไหม

```bash
docker rm -f ops-db
docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
sleep 10
```

```bash
docker exec ops-db psql -U opsuser -d campusops -c \
"INSERT INTO tickets (asset_id, title, detail, priority) VALUES (4, 'ไมโครโฟนห้องประชุมใหญ่เสียงขาด', 'แจ้งเข้ามาหลังระบบขึ้นแล้ว', 'HIGH');"
```

ลบกล่องแล้วสร้างใหม่ **โดยผูก volume ก้อนเดิม** :

```bash
docker rm -f ops-db
docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
sleep 10
```

```bash
docker exec ops-db psql -U opsuser -d campusops -c 'SELECT id, title, status FROM tickets ORDER BY id DESC LIMIT 1;'
```

✅ **สิ่งที่ต้องเห็น** — ใบที่ 9 ที่เราเพิ่มเอง **ยังอยู่** (คอลัมน์ภาษาไทยจะเยื้องไม่ตรงกรอบ เป็นเรื่องปกติของ `psql`) :

```
 id |           title            | status
----+----------------------------+--------
  9 | ไมโครโฟนห้องประชุมใหญ่เสียงขาด | NEW
(1 row)
```

> 📝 **บทเรียน:** `-v ops-pgdata:/var/lib/postgresql/data` ต่างกับการทดลองที่ 6 แค่บรรทัดเดียว แต่เปลี่ยนคำตอบของ NFR-2 ทั้งข้อ

---

## การทดลองที่ 8 — เก็บค่า env ไว้ในไฟล์เดียว

**คำถาม:** `-e` สามตัวย้ายไปอยู่ในไฟล์แล้วได้ผลเหมือนกันไหม

ไฟล์ `.env.db` ของแล็บมีอยู่แล้ว — ใช้แทน `-e` ทั้งสามตัว :

```bash
docker rm -f ops-db
docker run -d --name ops-db --env-file .env.db \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
sleep 10
docker exec ops-db env | grep POSTGRES
```

✅ **สิ่งที่ต้องเห็น** — ตัวแปรครบ 3 ตัวเหมือนตอนพิมพ์ `-e` เอง :

```
POSTGRES_DB=campusops
POSTGRES_USER=opsuser
POSTGRES_PASSWORD=labpass
```

> 📝 **บทเรียน:** บรรทัดที่ขึ้นต้นด้วย `#` ใน `.env.db` ถูกข้าม และ **ห้ามใส่เครื่องหมายคำพูดรอบค่า** เพราะ Docker จะนับเป็นส่วนหนึ่งของค่า · ไฟล์แบบนี้ต้องอยู่ใน `.gitignore` เสมอในงานจริง

---

## การทดลองที่ 9 — init script รันซ้ำไหมเมื่อ volume ไม่ว่าง

**คำถาม:** กล่องล่าสุดเป็นกล่องใหม่เอี่ยม แล้ว `02-seed.sql` ถูกรันอีกรอบหรือเปล่า

```bash
docker logs ops-db 2>&1 | grep -E 'Skipping initialization|running /docker-entrypoint-initdb.d'
docker exec ops-db psql -U opsuser -d campusops -c 'SELECT count(*) FROM tickets;'
```

✅ **สิ่งที่ต้องเห็น** — มีแต่บรรทัด `Skipping initialization` · **ไม่มีบรรทัด `running /docker-entrypoint-initdb.d/...` เลย** และจำนวนยังเป็น 9 ใบ ไม่ใช่ 17 ใบ :

```
PostgreSQL Database directory appears to contain a database; Skipping initialization

 count
-------
     9
(1 row)
```

> 📝 **บทเรียน:** ตัวตัดสินคือ **data directory ว่างหรือไม่** ไม่ใช่กล่องใหม่หรือเก่า · แปลว่าแก้ `db/initdb/*.sql` ทีหลังจะไม่มีผล จนกว่าจะลบ volume ทิ้ง (ซึ่งข้อมูลจริงจะหายไปด้วย)

---

## ตรวจงานด้วย `verify.sh`

```bash
bash verify.sh ; echo "exit code = $?"
```

✅ **สิ่งที่ต้องเห็น** — `[PASS]` ทุกบรรทัด ปิดท้ายด้วย `ALL CHECKS PASSED` และ `exit code = 0`

> 📝 สคริปต์สร้างกล่องของตัวเองชื่อขึ้นต้น `vops-` และ volume `vops1-pgdata` แล้วลบทิ้งเองเมื่อจบ — กล่อง `ops-db` กับ volume `ops-pgdata` ของเราจะไม่ถูกแตะ

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `Error: Database is uninitialized and superuser password is not specified.` | ไม่ได้ส่ง `POSTGRES_PASSWORD` เข้ากล่อง | เพิ่ม `-e POSTGRES_PASSWORD=labpass` หรือใช้ `--env-file .env.db` |
| `docker: Error response from daemon: Conflict. The container name "/ops-db" is already in use by container ...` | ยังมีกล่องชื่อเดิมค้างอยู่ | `docker rm -f ops-db` ก่อนแล้วค่อย `docker run` ใหม่ |
| `Did not find any relations.` ทั้งที่ผูก initdb แล้ว | ไม่ได้ `cd` อยู่ในโฟลเดอร์แล็บ `$PWD` จึงชี้ผิดที่ | `cd` เข้าโฟลเดอร์ `001_LAB_Run_The_System` แล้วลบกล่อง+`docker volume rm ops-pgdata` ก่อนรันใหม่ |
| `psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL:  role "opsuser" does not exist` | volume เดิมถูกสร้างด้วย `POSTGRES_USER` คนละชื่อ และ init ไม่รันซ้ำ | `docker rm -f ops-db && docker volume rm ops-pgdata` แล้วสร้างใหม่ให้ชื่อ user ตรงกัน |
| `ERROR:  relation "tickets" does not exist` | ต่อผิดฐานข้อมูล (ลืม `-d campusops` จึงไปโดน `postgres`) | ใส่ `-d campusops` ทุกครั้งที่เรียก `psql` |
| `Error response from daemon: container ... is not running` | `docker exec` ใส่กล่องที่หยุดไปแล้ว | `docker ps -a` ดูสถานะ แล้วอ่านเหตุผลจาก `docker logs <ชื่อกล่อง>` |
| `Error response from daemon: remove ops-pgdata: volume is in use - [...]` | ยังมีกล่องผูก volume ก้อนนั้นอยู่ | `docker rm -f ops-db` ก่อน แล้วค่อย `docker volume rm ops-pgdata` |
| `PostgreSQL Database directory appears to contain a database; Skipping initialization` ทั้งที่อยากให้ seed ใหม่ | volume ไม่ว่าง init script จึงถูกข้าม | ลบ volume ด้วย `docker volume rm ops-pgdata` แล้วสร้างกล่องใหม่ (**ข้อมูลเดิมหายหมด**) |

---

## เก็บกวาด

**ในกล่องเรียน:**

```bash
docker rm -f ops-db
docker volume rm ops-pgdata
docker ps -a
docker volume ls --filter name=ops-pgdata
```

> 📝 ต้องลบกล่องก่อนเสมอ ไม่งั้น `docker volume rm` จะฟ้อง `volume is in use` · `docker volume ls` เปล่า ๆ จะเห็น volume ชื่อเป็นรหัสยาวอีกหลายก้อน — เป็น volume นิรนามที่ postgres สร้างให้ทุกครั้งที่รันโดยไม่ระบุ `-v` และหายไปพร้อมกล่องเรียน

**ออกจากกล่องแล้วลบกล่องบนเครื่องเรา:**

```bash
exit
docker rm -f devtools-ops-lab1
docker ps -a --filter "name=^devtools-"
```

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker run -d --name <ชื่อ> -e KEY=value <image>` | สร้างกล่องแบบเบื้องหลัง พร้อมส่งค่าตั้งต้นเข้าไป |
| `docker run --env-file .env.db ...` | ส่งค่าทั้งไฟล์แทนการพิมพ์ `-e` ทีละตัว |
| `docker run -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" ...` | bind mount โฟลเดอร์บนเครื่องเข้าไปแบบอ่านอย่างเดียว |
| `docker run -v ops-pgdata:/var/lib/postgresql/data ...` | ผูก named volume ให้ข้อมูลอยู่นอกกล่อง |
| `docker ps` / `docker ps -a` | ดูกล่องที่รันอยู่ / รวมกล่องที่หยุดแล้ว |
| `docker logs <ชื่อกล่อง>` | อ่านสิ่งที่โปรแกรมในกล่องพิมพ์ออกมา (ใช้หาสาเหตุตอนกล่องดับ) |
| `docker exec <ชื่อกล่อง> <คำสั่ง>` | สั่งงานข้างในกล่องที่กำลังรันอยู่ |
| `docker exec -it <ชื่อกล่อง> psql -U opsuser -d campusops` | เปิด psql แบบโต้ตอบ (ออกด้วย `\q`) |
| `docker rm -f <ชื่อกล่อง>` | ลบกล่องทิ้งทันทีแม้ยังรันอยู่ |
| `docker volume ls` / `docker volume rm <ชื่อ>` | ดู / ลบ named volume (ลบแล้วข้อมูลหายถาวร) |

> **จำ 3 อย่าง:** ไม่มี `POSTGRES_PASSWORD` = ไม่ขึ้น · ไม่มี volume = ข้อมูลตายพร้อมกล่อง · volume ไม่ว่าง = init script ถูกข้าม

---

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] ไม่ใส่ `-e` แล้ว `docker logs ops-db-nopass 2>&1 | head -3` เจอ `You must specify POSTGRES_PASSWORD` · ใส่ครบแล้ว `docker ps` เห็น `ops-db` เป็น `Up` และ `PORTS` มีแค่ `5432/tcp`
- [ ] `docker logs ops-db 2>&1` เจอ `ready to accept connections` สองครั้ง โดยมี `init process complete` คั่นกลาง
- [ ] ก่อนผูก initdb : `docker exec -it ops-db psql -U opsuser -d campusops -c '\dt'` ตอบ `Did not find any relations.`
- [ ] หลังผูก `-v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro"` : `\dt` เห็นครบ **5 ตาราง** เจ้าของ `opsuser`
- [ ] นับ seed ได้ `assets 12 · tickets 8 · loans 3 · parts 6` ตรงกับ [`docs/01_requirements.md`](../docs/01_requirements.md)
- [ ] เพิ่มใบแจ้งซ่อมเป็น 9 → `docker rm -f ops-db` + `docker run` ใหม่ **โดยไม่มี volume** แล้ว `SELECT count(*) FROM tickets;` เหลือ 8
- [ ] ทำซ้ำแบบมี `-v ops-pgdata:/var/lib/postgresql/data` แล้วใบที่ `id = 9` **ยังอยู่**
- [ ] `--env-file .env.db` แล้ว `docker exec ops-db env | grep POSTGRES` ได้ครบ 3 ตัว
- [ ] `docker logs ops-db 2>&1 | grep 'Skipping initialization'` เจอ 1 บรรทัด และ `SELECT count(*) FROM tickets;` ยังเป็น 9 ไม่ใช่ 17
- [ ] `bash verify.sh ; echo "exit code = $?"` ขึ้น `ALL CHECKS PASSED` และ `exit code = 0`

---

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
