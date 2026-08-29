# LAB 1 — เริ่มระบบฐานข้อมูลและทำให้ข้อมูลคงอยู่

> โฟลเดอร์ `001_LAB_Run_The_System` · ไฟล์ของแล็บ : `db/initdb/01-schema.sql` · `db/initdb/02-seed.sql` · `.env.db` · `verify.sh`

## สาระสำคัญและผลลัพธ์การเรียนรู้

| | |
|---|---|
| **คำถามหลัก** | ทำอย่างไรให้ฐานข้อมูลเริ่มทำงานพร้อมข้อมูลตั้งต้น และยังเก็บข้อมูลไว้ได้หลังลบแล้วสร้าง Container ใหม่ |
| **ความรู้พื้นฐาน** | ชุด `01_Docker_Basics_Run_Port_Volume_Build` โดยใช้ `docker run` · `ps` · `logs` · `exec` · `rm` · `-e` · `-v` |
| **เวลา** | ประมาณ 40 นาที · การทดลอง **10 รายการ** รายการละ 3–5 นาที |
| **ผลลัพธ์ที่คาดหวัง** | เริ่ม `postgres:17-alpine` พร้อมโครงสร้างฐานข้อมูล (schema) และข้อมูลตั้งต้น (seed) · อ่าน log ระหว่างเริ่มระบบ · อธิบายได้ว่า Named Volume ช่วยให้ข้อมูลคงอยู่อย่างไร |
| **ขอบเขต** | การเชื่อม Container ด้วย Network อยู่ใน **LAB 4** และไฟล์ `compose.yaml` อยู่ใน **LAB 5** (ดู [`docs/01_requirements.md`](../docs/01_requirements.md)) · ยังไม่ใช้เครื่องมือ Object-Relational Mapping (ORM) สำหรับเชื่อมวัตถุในโปรแกรมกับตาราง และยังไม่ใช้เครื่องมือ Migration สำหรับควบคุมรุ่นของโครงสร้างฐานข้อมูล |

---

## คำศัพท์และที่มาของข้อกำหนด

- **User Story (US)** คือข้อความสั้นจากมุมมองผู้ใช้ที่ระบุว่าใครต้องการทำอะไรและเพื่อประโยชน์ใด
- **Functional Requirement (REQ)** หรือข้อกำหนดเชิงหน้าที่ ระบุว่า “ระบบต้องทำอะไร” เช่น ระบบต้องบันทึกใบแจ้งซ่อม
- **Acceptance Criteria** หรือเกณฑ์การผ่าน ระบุผลที่สังเกตและทดสอบได้ เพื่อยืนยันว่า Requirement ผ่าน
- **Non-Functional Requirement (NFR)** หรือข้อกำหนดที่ไม่ใช่เชิงหน้าที่ ระบุคุณภาพหรือข้อจำกัดของระบบ เช่น ความคงอยู่ของข้อมูลและการไม่เปิดพอร์ตฐานข้อมูลสู่ภายนอก
- **Image** คือแม่แบบแบบอ่านอย่างเดียวที่ใช้สร้าง Container ส่วน **Container** คือ Instance ที่กำลังทำงานจาก Image
- **Volume** คือพื้นที่เก็บข้อมูลที่มีอายุแยกจาก Container ส่วน **Bind Mount** คือการเชื่อมไฟล์หรือ Directory บนเครื่องเข้าไปใน Container
- **Initialization Script** คือไฟล์คำสั่งที่ใช้เตรียมฐานข้อมูลครั้งแรก และ **Entrypoint** คือโปรแกรมเริ่มต้นของ Image ที่เรียก Script เหล่านี้
- **SQL** คือภาษาสำหรับจัดการฐานข้อมูลเชิงสัมพันธ์ และ `psql` คือโปรแกรมบรรทัดคำสั่งสำหรับเชื่อมต่อ PostgreSQL
- **Repository** คือพื้นที่เก็บ Source Code และประวัติรุ่นบน Git ส่วน **Clone** คือการคัดลอก Repository มายังเครื่องผู้เรียน
- **URL** (Uniform Resource Locator) คือที่อยู่ของทรัพยากรบนเว็บ และ **HTTPS** คือ Protocol สำหรับรับส่งข้อมูลเว็บแบบเข้ารหัส

ลำดับการสืบโยงในชุดการสอนนี้คือ `User Story → Requirement → Acceptance Criteria → Non-Functional Requirement → Design/Architecture` รหัส เช่น `REQ-01` และ `NFR-2` ใช้สำหรับอ้างอิงกลับไปยังข้อกำหนดต้นทาง ไม่ใช่คำสั่งของ Docker

User Story ที่เกี่ยวข้องกับแล็บนี้คือ ผู้ดูแลระบบต้องการเก็บประวัติการยืม-คืนและใบแจ้งซ่อมไว้ เพื่อให้ตรวจสอบย้อนหลังได้ จึงนำไปสู่ข้อกำหนดให้ระบบบันทึกข้อมูล และข้อกำหนด `NFR-2` ที่ระบุว่าข้อมูลต้องคงอยู่แม้เปลี่ยน Container

สำหรับข้อกำหนดด้านโครงสร้างข้อมูล ตารางถัดไปแสดงว่า `REQ` แต่ละกลุ่มนำไปสู่ตารางใดและตรวจผ่านอย่างไร ส่วน `NFR-2` ผ่านเมื่อข้อมูลที่เพิ่มยังอยู่หลังสร้าง Container ใหม่ และ `NFR-3` ผ่านเมื่อฐานข้อมูลไม่มี Host Port ซึ่งหมายถึงไม่มีการเผยแพร่พอร์ตฐานข้อมูลออกจาก Container สำหรับเรียน

## ทฤษฎีก่อนลงมือ

### ปลายทางของทั้งชุด — จบ LAB 5 จะได้ระบบแบบนี้

![หน้าสรุปภาพรวมของ CampusOps ที่เปิดจากเบราว์เซอร์จริง หัวข้อ ตอนนี้งานอะไรอยู่ในมือใคร แสดงงานที่ยังไม่ปิด 6 ใบ ค้างเกินกำหนด 2 ใบ ครุภัณฑ์ถูกยืมอยู่ 2 ชิ้น อะไหล่ต้องสั่งเพิ่ม 2 รายการ พร้อมแถบสัดส่วนใบแจ้งซ่อมตามขั้นของงาน รอรับเรื่อง 3 มอบหมายแล้ว 2 กำลังซ่อม 1 ปิดงานแล้ว 2](./images/app-target-system.png)

> 🖼 **วิธีอ่านรูปนี้:** ตัวเลขบนหน้าเว็บมีที่มาจากข้อมูลของแล็บนี้ · การ์ด "งานที่ยังไม่ปิด 6 ใบ · ทั้งหมด 8 ใบ" กับแถบ `รอรับเรื่อง 3 · มอบหมายแล้ว 2 · กำลังซ่อม 1 · ปิดงานแล้ว 2` มาจากแถวใน `02-seed.sql` ซึ่งจะถูกโหลดเข้า 5 ตารางในการทดลองที่ 5 และตรวจนับด้วย `psql` ในการทดลองที่ 6 · หากฐานข้อมูลว่าง หน้าเว็บจะแสดงค่า 0

### ระบบประกอบด้วย 3 Container — แล็บนี้พัฒนาเฉพาะฐานข้อมูล

![แผนภาพระบบ CampusOps สาม Container โดยเบราว์เซอร์เรียก web จากนั้น web เรียก api และ api เรียก db ส่วน Container db ผูกกับ Named Volume ชื่อ ops-pgdata](./images/theory-three-boxes.svg)

> 🖼 **วิธีอ่านรูปนี้:** Container `db` ด้านขวาที่มีกรอบหนาคือขอบเขตของแล็บนี้ ส่วน `web` และ `api` ยังไม่ต้องเริ่มทำงาน ลูกศรสีเขียวชี้ไปยัง Named Volume ซึ่งเป็นตำแหน่งเก็บข้อมูลตาม `NFR-2`

ข้อความจากการเก็บความต้องการว่า **“ข้อมูลยืม-คืนย้อนหลังต้องไม่สูญหาย แม้ต้องย้ายเครื่องหรือเริ่มระบบใหม่”** ถูกแปลงเป็น `NFR-2` และเป็นเหตุผลที่ต้องใช้ Named Volume ในแล็บนี้

### 5 ตารางที่ต้องมี

| ตาราง | ข้อมูลที่จัดเก็บ | Requirement ที่รองรับ | Acceptance Criteria ของแล็บนี้ |
|---|---|---|---|
| `assets` | ครุภัณฑ์ 180 ชิ้นของคณะ (ข้อมูลสาธิต 12 ชิ้น) | `REQ-01`, `REQ-10`, `REQ-11` | คำสั่งนับแถวคืนค่า `12` |
| `tickets` | ใบแจ้งซ่อมและสถานะ `NEW → ASSIGNED → IN_PROGRESS → DONE` | `REQ-01` ถึง `REQ-04`, `REQ-08` | คำสั่งนับแถวคืนค่า `8` ก่อนเพิ่มข้อมูล |
| `loans` | รายการยืม-คืน โดย `returned_at IS NULL` หมายถึงยังไม่คืน | `REQ-10` | คำสั่งนับแถวคืนค่า `3` |
| `parts` | อะไหล่และจุดสั่งซื้อ | `REQ-06`, `REQ-12` | คำสั่งนับแถวคืนค่า `6` และพบรายการต่ำกว่าจุดสั่งซื้อ `2` รายการ |
| `stock_moves` | ประวัติการเบิกและรับเข้าอะไหล่ | `REQ-05`, `REQ-07` | สคริปต์ `verify.sh` นับได้ `6` แถว |

ทั้งหมดอยู่ในไฟล์ `db/initdb/01-schema.sql` และข้อมูลตั้งต้นอยู่ใน `db/initdb/02-seed.sql`
**แล็บนี้ไม่แก้ไขสองไฟล์ดังกล่าว** — เป้าหมายคือทำให้ไฟล์ถูกรันในตำแหน่งและเวลาที่ถูกต้อง

### PostgreSQL จัดเก็บข้อมูลไว้ที่ใด

![แผนภาพเปรียบเทียบ Container ที่ไม่ผูก Volume ซึ่งข้อมูลอยู่ใน writable layer กับ Container ที่ผูก Named Volume ops-pgdata ซึ่งข้อมูลยังอยู่หลังลบ Container](./images/theory-where-is-data.svg)

> 🖼 **วิธีอ่านรูปนี้:** ทั้งสองฝั่งลบ Container ด้วย `docker rm -f ops-db` เหมือนกัน ฝั่งซ้ายข้อมูลใน writable layer ถูกลบพร้อม Container ส่วนฝั่งขวาข้อมูลอยู่ใน Named Volume จึงยังคงอยู่

### Initialization Script ทำงานเมื่อใด

![ผังตัดสินใจของ PostgreSQL Entrypoint โดยรันไฟล์ใน docker-entrypoint-initdb.d ตามลำดับชื่อเมื่อ Data Directory ว่าง และข้ามไฟล์ทั้งหมดเมื่อมีข้อมูลอยู่แล้ว](./images/theory-initdb-when.svg)

> 🖼 **วิธีอ่านรูปนี้:** จุดตัดสินอยู่ที่สี่เหลี่ยมข้าวหลามตัดกลางรูป โดยตรวจว่า *Data Directory ว่างหรือไม่* ไม่ได้ตรวจว่า Container ใหม่หรือเก่า แต่ละกิ่งจึงให้ข้อความ Log ต่างกัน

### สิ่งที่มักเข้าใจผิด

- **ความเข้าใจคลาดเคลื่อน:** Image จะกำหนด `POSTGRES_PASSWORD` ให้โดยอัตโนมัติ → **ข้อเท็จจริง:** ต้องกำหนดค่านี้ก่อนเริ่ม Container (ดูตารางแก้ปัญหาที่พบบ่อย)
- **ความเข้าใจคลาดเคลื่อน:** ข้อมูลยังอยู่หลังลบ Container เพราะ Image ยังอยู่ → **ข้อเท็จจริง:** ข้อมูลใน writable layer จะหายไปพร้อม Container ส่วน Image เป็นแม่แบบ (การทดลองที่ 7)
- **ความเข้าใจคลาดเคลื่อน:** การแก้ไฟล์ใน `db/initdb/` มีผลทุกครั้งที่สร้าง Container ใหม่ → **ข้อเท็จจริง:** Initialization Script ถูกข้ามเมื่อ Volume ไม่ว่าง (การทดลองที่ 10)
- **ความเข้าใจคลาดเคลื่อน:** `--env-file` ให้ผลต่างจาก `-e` → **ข้อเท็จจริง:** ทั้งสองวิธีส่งตัวแปรชุดเดียวกัน แต่จัดเก็บค่าคนละตำแหน่ง (การทดลองที่ 9)

---

## เตรียมเครื่องเรียน

### ขั้นที่ 1 — เปิด Container สำหรับเรียน

รันบน **เครื่องของผู้เรียน** โดยแทน `<DOCKER_USER>` ด้วยชื่อบัญชี Docker Hub ที่ได้รับ แล็บนี้ไม่เปิดพอร์ตฐานข้อมูล เพราะเข้าถึงผ่าน `docker exec` ภายใน Container สำหรับเรียน

```bash
docker rm -f devtools-lab001 2>/dev/null
docker run -dit --name devtools-lab001 --privileged -p 2222:22 <DOCKER_USER>/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd
```

ภายใน Container สำหรับเรียน ให้เตรียม Directory สำหรับ Source Code ก่อนเริ่มขั้นตอนบนหน้าเว็บ

```bash
mkdir -p ~/labwork
cd ~/labwork
```

---

## การทดลองที่ 1 — เปิด Repository และคัดลอก URL จาก GitHub อย่างไร

**คำถาม:** จะเข้าถึง Source Code ผ่านหน้า GitHub และคัดลอก URL แบบ HTTPS อย่างไร

### Walkthrough หน้า GitHub

#### ขั้นที่ ① — เปิดหน้า Repository

เปิด `https://github.com/<GITHUB_USER>/DevTools` โดยแทน `<GITHUB_USER>` ด้วยชื่อบัญชีที่ผู้สอนกำหนด แล้วตรวจว่าชื่อ Repository คือ `DevTools`

![หน้า Repository DevTools บน GitHub พร้อมกรอบสีแดง หมายเลข 1 และป้ายกำกับตำแหน่งชื่อ Repository](./images/ui-github-01-repo.png)

*ภาพที่ 1 — หน้าแรกของ Repository `DevTools`; กรอบหมายเลข 1 ระบุตำแหน่งชื่อ Repository ที่ต้องตรวจสอบ*

#### ขั้นที่ ② — เข้าโฟลเดอร์ `02_Docker`

ในรายการไฟล์หน้าแรกของ Repository คลิกแถว `02_Docker`

![หน้าแรกของ repository DevTools พร้อมกรอบหมายเลข 2 ล้อมแถวโฟลเดอร์ 02 Docker ที่ต้องคลิก](./images/ui-github-02-folder.png)

*ภาพที่ 2 — คลิกแถว `02_Docker` ตามกรอบหมายเลข 2 ในรายการไฟล์*

#### ขั้นที่ ③ — เข้าโฟลเดอร์ชุดสอน

ในรายการไฟล์ของ `02_Docker` คลิกแถว `03_Fullstack_App_Example`

![หน้าโฟลเดอร์ 02 Docker พร้อมกรอบหมายเลข 3 ล้อมแถว 03 Fullstack App Example ที่ต้องคลิก](./images/ui-github-03-project.png)

*ภาพที่ 3 — คลิกแถว `03_Fullstack_App_Example` ตามกรอบหมายเลข 3*

#### ขั้นที่ ④–⑥ — คัดลอก URL แบบ HTTPS

คลิก `Code` เลือกแท็บ `HTTPS` แล้วคลิกไอคอนคัดลอก URL

![เมนู Code บน GitHub พร้อมกรอบหมายเลข 4 ที่ปุ่ม Code หมายเลข 5 ที่แท็บ HTTPS และหมายเลข 6 ที่ปุ่มคัดลอก](./images/ui-github-04-code.png)

*ภาพที่ 4 — ทำตามกรอบหมายเลข 4–6 เพื่อเปิดเมนู `Code` เลือก `HTTPS` และคัดลอก URL สำหรับ Clone Repository*

> ภาพที่ 1–4 เป็น Screenshot จากหน้า GitHub จริง โดยใส่ Marker หลังบันทึกภาพ ปกปิดข้อมูลบัญชีในภาพ และใช้ Placeholder ในข้อความประกอบเพื่อไม่เปิดเผยชื่อผู้ใช้จริง

จากนั้นโหลดโค้ดแล็บด้วย URL ที่คัดลอก โดยรันไม่เกินสองคำสั่งต่อไปนี้ **ภายใน Container สำหรับเรียน** และแทน `<HTTPS_URL>` ด้วย URL จากขั้นที่ ⑥

```bash
git clone "<HTTPS_URL>"
cd DevTools/02_Docker/03_Fullstack_App_Example/001_LAB_Run_The_System && ls db/initdb
```

✅ **สิ่งที่ต้องสังเกต** — พบไฟล์ SQL สองไฟล์สำหรับสร้างโครงสร้างและข้อมูลตั้งต้น

```
01-schema.sql  02-seed.sql
```

> 📝 **ชื่อไฟล์ขึ้นต้นด้วยตัวเลขโดยตั้งใจ** — Entrypoint ของ PostgreSQL รันไฟล์ตามลำดับชื่อ จึงต้องสร้าง Schema ก่อนเพิ่ม Seed

---

## การทดลองที่ 2 — ต้องกำหนดค่าเพื่อเริ่มฐานข้อมูลด้วย `docker run` อย่างไร

**คำถาม:** ต้องกำหนดค่าใดให้ `postgres:17-alpine` เพื่อให้ Container เริ่มทำงาน

```bash
docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass postgres:17-alpine
sleep 8 && docker ps
```

✅ **สิ่งที่ต้องสังเกต** — Container มี `STATUS` เป็น `Up ...` และ `PORTS` แสดงเพียง `5432/tcp` โดยไม่มี Host Port ตาม `NFR-3` (Container ID และเวลาอาจต่างกัน)

```
5dc9a1257a393844341ed8058d064845569e74c58af0556ebca395fed1115550
CONTAINER ID   IMAGE                COMMAND                  CREATED         STATUS         PORTS      NAMES
5dc9a1257a39   postgres:17-alpine   "docker-entrypoint.s…"   9 seconds ago   Up 8 seconds   5432/tcp   ops-db
```

> 📝 **สรุป:** PostgreSQL ต้องได้รับชื่อฐานข้อมูล ชื่อผู้ใช้ และรหัสผ่านผ่าน `-e` ก่อนเริ่มทำงาน ส่วนการไม่ใช้ `-p` ทำให้ฐานข้อมูลไม่เปิดพอร์ตสู่ภายนอก

---

## การทดลองที่ 3 — กระบวนการเริ่มต้นของ PostgreSQL มีลำดับอย่างไร

**คำถาม:** ระหว่างเริ่ม Container PostgreSQL มีกระบวนการใดเกิดขึ้นบ้าง

```bash
docker logs ops-db 2>&1 | grep -E 'init process complete|ready to accept connections'
```

✅ **สิ่งที่ต้องสังเกต** — พบ `ready to accept connections` **สองครั้ง** โดยมี `init process complete` คั่นกลาง (เวลาและ Process ID อาจต่างกัน)

```
2026-08-20 08:09:35.055 UTC [41] LOG:  database system is ready to accept connections
PostgreSQL init process complete; ready for start up.
2026-08-20 08:09:35.731 UTC [1] LOG:  database system is ready to accept connections
```

> 📝 **สรุป:** ครั้งแรกคือ Server ชั่วคราวสำหรับสร้างฐานข้อมูล ส่วนครั้งที่สองคือ Server หลัก หากพบเพียงครั้งแรกให้ตรวจ Log ในตารางแก้ปัญหาที่พบบ่อย

---

## การทดลองที่ 4 — ฐานข้อมูลเริ่มต้นมีตารางแล้วหรือไม่

**คำถาม:** ฐานข้อมูล `campusops` ที่เพิ่งสร้างมีตารางของระบบแล้วหรือไม่

```bash
docker exec -it ops-db psql -U opsuser -d campusops -c '\dt'
```

✅ **สิ่งที่ต้องสังเกต** — เชื่อมต่อได้ แต่ยังไม่มีตาราง

```
Did not find any relations.
```

> 📝 **สรุป:** `-e POSTGRES_DB` สร้างเฉพาะฐานข้อมูลเปล่า ส่วนตารางและข้อมูลต้องส่งผ่าน Initialization Script

---

## การทดลองที่ 5 — เรียก Schema และ Seed ระหว่างเริ่มต้นอย่างไร

**คำถาม:** ทำอย่างไรให้ PostgreSQL รันไฟล์ `.sql` เมื่อสร้างฐานข้อมูลครั้งแรก

```bash
docker rm -f ops-db
docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine \
  && sleep 10 && docker exec ops-db psql -U opsuser -d campusops -c '\dt'
```

✅ **สิ่งที่ต้องสังเกต** — พบ **5 ตาราง** ตามสัญญาข้อมูลใน [`docs/02_contract.md`](../docs/02_contract.md) และเจ้าของคือ `opsuser`

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

> 📝 **สรุป:** `/docker-entrypoint-initdb.d` คือ Directory ที่ PostgreSQL Image ใช้รับ Initialization Script และ `:ro` กำหนดให้ Container อ่านไฟล์ได้อย่างเดียว

---

## การทดลองที่ 6 — จำนวนข้อมูลตั้งต้นตรงตาม Requirement หรือไม่

**คำถาม:** Seed ที่เพิ่งทำงานมีจำนวนตรงกับ [`docs/01_requirements.md`](../docs/01_requirements.md) หรือไม่

คำสั่ง `SELECT` รวมการนับ 4 ตารางไว้ในผลลัพธ์เดียว จึงยาวกว่าคำสั่งตรวจสอบทั่วไป แต่จำเป็นต่อการเปรียบเทียบสัญญาข้อมูลระหว่างแล็บ

```bash
docker exec ops-db psql -U opsuser -d campusops -c \
"SELECT (SELECT count(*) FROM assets) AS assets, (SELECT count(*) FROM tickets) AS tickets, (SELECT count(*) FROM loans) AS loans, (SELECT count(*) FROM parts) AS parts;"
```

✅ **สิ่งที่ต้องสังเกต** — ครุภัณฑ์ **12** · ใบแจ้งซ่อม **8** · รายการยืม **3** · อะไหล่ **6**

```
 assets | tickets | loans | parts
--------+---------+-------+-------
     12 |       8 |     3 |     6
(1 row)
```

> 📝 **สรุป:** จำนวนแถวเป็น Acceptance Criteria ของข้อมูลตั้งต้น และ LAB 2 จะใช้ค่าเดียวกันทดสอบ Application Programming Interface (API) ซึ่งเป็นช่องทางที่โปรแกรมใช้สื่อสารกัน

---

## การทดลองที่ 7 — ข้อมูลคงอยู่เมื่อสร้าง Container ใหม่โดยไม่มี Volume หรือไม่

**คำถาม:** ใบแจ้งซ่อมที่เพิ่มหลังระบบเริ่มทำงานยังคงอยู่หลังสร้าง Container ใหม่โดยไม่ใช้ Volume หรือไม่

```bash
docker exec ops-db psql -U opsuser -d campusops -c \
"INSERT INTO tickets (asset_id, title, detail, priority) VALUES (4, 'ไมโครโฟนห้องประชุมใหญ่เสียงขาด', 'แจ้งเข้ามาหลังระบบขึ้นแล้ว', 'HIGH'); SELECT count(*) FROM tickets;"
docker rm -f ops-db && docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine \
  && sleep 10 && docker exec ops-db psql -U opsuser -d campusops -c 'SELECT count(*) FROM tickets;'
```

✅ **สิ่งที่ต้องสังเกต** — หลังเพิ่มข้อมูลมี **9 ใบ** แต่หลังสร้าง Container ใหม่โดยไม่มี Volume จะกลับมาเป็น **8 ใบ**

```
INSERT 0 1
 count
-------
    9
(1 row)

 count
-------
    8
(1 row)
```

> 📝 **สรุป:** ผลลัพธ์นี้ยังไม่ผ่าน `NFR-2` เลข 8 ที่ปรากฏหลังสร้างใหม่คือ Seed ที่ Initialization Script เพิ่มอีกครั้ง ไม่ใช่ข้อมูลชุดเดิม

---

## การทดลองที่ 8 — Named Volume ทำให้ข้อมูลคงอยู่หรือไม่

**คำถาม:** Named Volume ทำให้ข้อมูลยังคงอยู่หลังสร้าง Container ใหม่หรือไม่

```bash
docker rm -f ops-db && docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine \
  && sleep 10 && docker exec ops-db psql -U opsuser -d campusops -c \
  "INSERT INTO tickets (asset_id, title, detail, priority) VALUES (4, 'ไมโครโฟนห้องประชุมใหญ่เสียงขาด', 'แจ้งเข้ามาหลังระบบขึ้นแล้ว', 'HIGH');"
docker rm -f ops-db && docker run -d --name ops-db \
  -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine \
  && sleep 10 && docker exec ops-db psql -U opsuser -d campusops -c 'SELECT id, title, status FROM tickets ORDER BY id DESC LIMIT 1;'
```

✅ **สิ่งที่ต้องสังเกต** — ใบแจ้งซ่อม `id = 9` ที่เพิ่มไว้ **ยังอยู่** (ความกว้างตัวอักษรไทยอาจทำให้แนวคอลัมน์ของ `psql` คลาดเคลื่อน)

```
 id |           title            | status
----+----------------------------+--------
  9 | ไมโครโฟนห้องประชุมใหญ่เสียงขาด | NEW
(1 row)
```

> 📝 **สรุป:** `-v ops-pgdata:/var/lib/postgresql/data` ทำให้ข้อมูลอยู่นอก Writable Layer ของ Container จึงผ่าน Acceptance Criteria ของ `NFR-2`

---

## การทดลองที่ 9 — Environment File ให้ผลเทียบเท่าการกำหนด `-e` หรือไม่

**คำถาม:** การย้ายค่า `-e` สามตัวไปไว้ในไฟล์ให้ผลเหมือนเดิมหรือไม่

ไฟล์ `.env.db` ของแล็บมีอยู่แล้ว — ใช้แทน `-e` ทั้งสามตัว :

```bash
docker rm -f ops-db
docker run -d --name ops-db --env-file .env.db \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine \
  && sleep 10 && docker exec ops-db env | grep POSTGRES
```

✅ **สิ่งที่ต้องสังเกต** — พบตัวแปรครบ 3 ตัวเช่นเดียวกับการกำหนด `-e`

```
POSTGRES_DB=campusops
POSTGRES_USER=opsuser
POSTGRES_PASSWORD=labpass
```

> 📝 **สรุป:** Docker ข้ามบรรทัดที่ขึ้นต้นด้วย `#` ใน `.env.db` และนับเครื่องหมายคำพูดเป็นส่วนหนึ่งของค่า ในระบบจริงต้องเก็บไฟล์ที่มีข้อมูลลับไว้นอก Git และใช้ Placeholder ในเอกสารเสมอ

---

## การทดลองที่ 10 — เมื่อ Volume ไม่ว่าง Initialization Script รันซ้ำหรือไม่

**คำถาม:** เมื่อสร้าง Container ใหม่โดยใช้ Volume เดิม `02-seed.sql` จะถูกรันซ้ำหรือไม่

```bash
docker logs ops-db 2>&1 | grep -E 'Skipping initialization|running /docker-entrypoint-initdb.d'
docker exec ops-db psql -U opsuser -d campusops -c 'SELECT count(*) FROM tickets;'
```

✅ **สิ่งที่ต้องสังเกต** — พบ `Skipping initialization` โดยไม่พบ `running /docker-entrypoint-initdb.d/...` และจำนวนใบแจ้งซ่อมยังเป็น 9 ใบ ไม่ใช่ 17 ใบ

```
PostgreSQL Database directory appears to contain a database; Skipping initialization

 count
-------
     9
(1 row)
```

> 📝 **สรุป:** PostgreSQL ตรวจว่า **Data Directory ว่างหรือไม่** ไม่ได้ตรวจอายุของ Container ดังนั้นการแก้ `db/initdb/*.sql` ภายหลังจะไม่มีผลกับ Volume เดิม

---

## ตรวจงานด้วย `verify.sh`

```bash
bash verify.sh ; echo "exit code = $?"
```

✅ **สิ่งที่ต้องสังเกต** — `[PASS]` ทุกบรรทัด ปิดท้ายด้วย `ALL CHECKS PASSED` และ `exit code = 0`

```text
==============================================
 LAB 1 — Run The System (CampusOps db) : verify
==============================================
[PASS] ต่อ Docker daemon ได้
[PASS] ไฟล์ของแล็บครบ (db/initdb/01-schema.sql, db/initdb/02-seed.sql, .env.db, readme.md)
[PASS] ไม่ใส่ POSTGRES_PASSWORD แล้ว Container หยุดพร้อมข้อความเตือน (state=exited:1)
[PASS] Container devtools-lab001-verify-db1 ขึ้นและรับ connection ได้
[PASS] initdb สร้างตารางครบ 5 ตาราง : assets,loans,parts,stock_moves,tickets
[PASS] log บอกว่ารันไฟล์ /docker-entrypoint-initdb.d/01-schema.sql จริง
[PASS] จำนวน seed ตรงตามข้อกำหนด (assets 12 · tickets 8 · loans 3 · parts 6 · stock_moves 6)
[PASS] อะไหล่ต่ำกว่าจุดสั่งซื้อ 2 รายการตามสัญญาข้อมูล (REQ-12)
[PASS] เพิ่มใบแจ้งซ่อม 1 ใบแล้วนับได้ 9 ใบ
[PASS] ไม่มี Volume : ลบ Container แล้วสร้างใหม่ ข้อมูลที่เพิ่มเองหายจริง (กลับเป็น 8 ใบตาม Seed)
[PASS] Container ที่ผูก Volume lab001-verify-pgdata เพิ่มข้อมูลแล้วนับได้ 9 ใบ
[PASS] ลบ Container แล้ว Volume lab001-verify-pgdata ยังอยู่ (อายุ Volume ไม่ผูกกับอายุ Container)
[PASS] มี Volume : สร้าง Container ใหม่แล้วข้อมูลยังอยู่ครบ 9 ใบ (NFR-2 ผ่าน)
[PASS] Volume ไม่ว่าง : Log ขึ้น 'Skipping initialization' — Initialization Script ถูกข้าม
[PASS] devtools-lab001-verify-db4 ไม่ได้รัน 02-seed.sql ซ้ำ ข้อมูลจึงไม่ถูกเติมซ้ำซ้อน
[PASS] --env-file .env.db ส่งค่าเข้า Container ครบ 3 ตัว และเข้าฐานข้อมูลเดิมได้ (9 ใบ)
----------------------------------------------
ALL CHECKS PASSED
exit code = 0
```

> 📝 สคริปต์สร้าง Container ชื่อขึ้นต้น `devtools-lab001-verify-` และ Volume `lab001-verify-pgdata` แล้วลบเมื่อทำงานเสร็จ โดยไม่แตะต้อง `ops-db` และ `ops-pgdata`

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `Error: Database is uninitialized and superuser password is not specified.` | ไม่ได้ส่ง `POSTGRES_PASSWORD` เข้า Container | เพิ่ม `-e POSTGRES_PASSWORD=labpass` หรือใช้ `--env-file .env.db` |
| ต้องการอ่านข้อความเตือนของ Container ที่หยุดทำงาน | ข้อความเตือนของ PostgreSQL ส่งออกทาง Standard Error (stderr) | ใช้ `docker logs <CONTAINER_NAME> 2>&1` เพื่อรวม Standard Output (stdout) และ stderr ก่อนอ่านผล |
| `docker: Error response from daemon: Conflict. The container name "/ops-db" is already in use by container ...` | ยังมี Container ชื่อเดิมค้างอยู่ | `docker rm -f ops-db` ก่อนแล้วค่อย `docker run` ใหม่ |
| `Did not find any relations.` ทั้งที่ผูก Initialization Script แล้ว | ไม่ได้ `cd` อยู่ใน Directory ของแล็บ ค่า `$PWD` จึงชี้ผิดที่ | `cd` เข้า `001_LAB_Run_The_System` แล้วลบ Container และ Volume ก่อนรันใหม่ |
| `psql: error: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432" failed: FATAL: role "opsuser" does not exist` | Volume เดิมสร้างด้วย `POSTGRES_USER` คนละชื่อ และ Initialization Script ไม่รันซ้ำ | รัน `docker rm -f ops-db` แล้วรัน `docker volume rm ops-pgdata` ก่อนสร้างใหม่ให้ชื่อผู้ใช้ตรงกัน |
| `ERROR:  relation "tickets" does not exist` | ต่อผิดฐานข้อมูล (ลืม `-d campusops` จึงไปโดน `postgres`) | ใส่ `-d campusops` ทุกครั้งที่เรียก `psql` |
| `Error response from daemon: container ... is not running` | `docker exec` อ้างถึง Container ที่หยุดแล้ว | `docker ps -a` ดูสถานะ แล้วอ่านเหตุผลจาก `docker logs <CONTAINER_NAME>` |
| `Error response from daemon: remove ops-pgdata: volume is in use - [...]` | ยังมี Container ผูก Volume นั้นอยู่ | `docker rm -f ops-db` ก่อน แล้วค่อย `docker volume rm ops-pgdata` |
| `PostgreSQL Database directory appears to contain a database; Skipping initialization` เมื่อต้องการใช้ Seed ใหม่ | Volume ไม่ว่าง Initialization Script จึงถูกข้าม | ลบ Volume ด้วย `docker volume rm ops-pgdata` แล้วสร้าง Container ใหม่ (**ข้อมูลเดิมหายทั้งหมด**) |

---

## เก็บกวาด

**ภายใน Container สำหรับเรียน:**

```bash
docker rm -f ops-db
docker volume rm ops-pgdata
docker ps -a
docker volume ls --filter name=ops-pgdata
```

> 📝 ต้องลบ Container ก่อนลบ Volume มิฉะนั้น `docker volume rm` จะแสดง `volume is in use` ส่วน Volume ที่มีชื่อเป็นรหัสยาวคือ Anonymous Volume ที่ PostgreSQL สร้างเมื่อไม่ระบุ `-v`

**ออกจาก Container แล้วลบ Container สำหรับเรียนบนเครื่องผู้เรียน:**

```bash
exit
docker rm -f devtools-lab001
docker ps -a --filter name=devtools-lab001
```

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker run -d --name <CONTAINER_NAME> -e KEY=value <IMAGE>` | สร้าง Container แบบเบื้องหลังและส่งค่าตั้งต้นเข้าไป |
| `docker run --env-file .env.db ...` | ส่งค่าทั้งไฟล์แทนการพิมพ์ `-e` ทีละตัว |
| `docker run -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" ...` | bind mount โฟลเดอร์บนเครื่องเข้าไปแบบอ่านอย่างเดียว |
| `docker run -v ops-pgdata:/var/lib/postgresql/data ...` | ผูก Named Volume เพื่อเก็บข้อมูลนอก Writable Layer ของ Container |
| `docker ps` / `docker ps -a` | แสดง Container ที่กำลังทำงาน / แสดงรวม Container ที่หยุดแล้ว |
| `docker logs <CONTAINER_NAME>` | อ่าน Log ที่โปรแกรมใน Container ส่งออกมา |
| `docker exec <CONTAINER_NAME> <COMMAND>` | รันคำสั่งภายใน Container ที่กำลังทำงาน |
| `docker exec -it <CONTAINER_NAME> psql -U opsuser -d campusops` | เปิด `psql` แบบโต้ตอบและออกด้วย `\q` |
| `docker rm -f <CONTAINER_NAME>` | ลบ Container ทันทีแม้กำลังทำงาน |
| `docker volume ls` / `docker volume rm <VOLUME_NAME>` | แสดง / ลบ Named Volume โดยการลบทำให้ข้อมูลสูญหายถาวร |

> **หลักสำคัญ 3 ประการ:** ไม่มี `POSTGRES_PASSWORD` = Container ไม่เริ่มทำงาน · ไม่มี Volume = ข้อมูลถูกลบพร้อม Container · Volume ไม่ว่าง = Initialization Script ถูกข้าม

---

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `docker ps` เห็น `ops-db` เป็น `Up` และ `PORTS` มีเพียง `5432/tcp`
- [ ] `docker logs ops-db 2>&1` เจอ `ready to accept connections` สองครั้ง โดยมี `init process complete` คั่นกลาง
- [ ] ก่อนผูก initdb : `docker exec -it ops-db psql -U opsuser -d campusops -c '\dt'` ตอบ `Did not find any relations.`
- [ ] หลังผูก `-v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro"` : `\dt` เห็นครบ **5 ตาราง** เจ้าของ `opsuser`
- [ ] นับ seed ได้ `assets 12 · tickets 8 · loans 3 · parts 6` ตรงกับ [`docs/01_requirements.md`](../docs/01_requirements.md)
- [ ] เพิ่มใบแจ้งซ่อมเป็น 9 → `docker rm -f ops-db` + `docker run` ใหม่ **โดยไม่มี Volume** แล้ว `SELECT count(*) FROM tickets;` เหลือ 8
- [ ] ทำซ้ำแบบมี `-v ops-pgdata:/var/lib/postgresql/data` แล้วใบที่ `id = 9` **ยังอยู่**
- [ ] `--env-file .env.db` แล้ว `docker exec ops-db env | grep POSTGRES` ได้ครบ 3 ตัว
- [ ] `docker logs ops-db 2>&1 | grep 'Skipping initialization'` เจอ 1 บรรทัด และ `SELECT count(*) FROM tickets;` ยังเป็น 9 ไม่ใช่ 17
- [ ] `bash verify.sh ; echo "exit code = $?"` ขึ้น `ALL CHECKS PASSED` และ `exit code = 0`

---

*ผลลัพธ์ในเอกสารผ่านการรันจริงด้วย Image `<DOCKER_USER>/devtools:2569_1`; ใช้ Placeholder เพื่อไม่เปิดเผยชื่อบัญชีจริง*
