# LAB 001 — PostgreSQL: สร้างฐานข้อมูลและสำรวจข้อมูลด้วย Python

> LAB นี้ศึกษาชั้นฐานข้อมูลของสถาปัตยกรรม `Browser → Next.js web → FastAPI api → PostgreSQL db` โดยมีฐานข้อมูล PostgreSQL หนึ่งฐานชื่อ `skillspace` และห้าตาราง ได้แก่ `assets`, `tickets`, `loans`, `parts` และ `stock_moves`

## สิ่งที่จะได้เรียนรู้

- สร้าง PostgreSQL ด้วยคอนเทนเนอร์จาก schema และ seed
- ใช้ Python และ psycopg 3 เชื่อมต่อฐานข้อมูลโดยไม่ใช้ ORM
- ตรวจชื่อฐานข้อมูล รายชื่อตาราง ชื่อและชนิดคอลัมน์ จำนวนแถว และข้อมูลตัวอย่าง
- เข้าใจ `connection`, `cursor`, `execute()`, `fetchone()` และ `fetchall()`
- ทำความสะอาดคอนเทนเนอร์เมื่อจบการทดลอง

## ภาพรวมของแล็บนี้

![สถาปัตยกรรม SkillSpace และขอบเขต LAB 001](./images/theory-three-boxes.svg)

Python ภายในเครื่องปฏิบัติการเป็น database client เพียงช่องทางเดียวและเชื่อม PostgreSQL ผ่าน `localhost:5432` Browser ไม่เชื่อมต่อ PostgreSQL โดยตรง และ LAB นี้ไม่ใช้ `docker exec` หรือ `psql` เพื่อจัดการข้อมูล

## 0. เตรียมเครื่องปฏิบัติการ

### 0.1 ลบเครื่องปฏิบัติการเดิมและสร้างเครื่องใหม่

📝 **คำอธิบาย:** รันสองบรรทัดนี้บนเครื่องผู้ใช้ บรรทัดแรกลบชื่อเดิม บรรทัดที่สองสร้างเครื่องปฏิบัติการที่รองรับ Docker-in-Docker และเผยแพร่ SSH ที่พอร์ต `2222`

```bash
docker rm -f devtools-fullstack-lab001 2>/dev/null
docker run -dit --name devtools-fullstack-lab001 --privileged -p 2222:22 tuchsanai/devtools:2569_1
```

✅ **ผลลัพธ์ที่คาดหวัง:** Docker แสดง container ID ใหม่ และคอนเทนเนอร์ไม่หยุดทำงานทันที

### 0.2 ตรวจสถานะเครื่องปฏิบัติการ

📝 **คำอธิบาย:** ตรวจว่า process หลักยังทำงานและพอร์ต SSH ถูกเผยแพร่แล้ว

```bash
docker ps --filter name=devtools-fullstack-lab001
```

✅ **ผลลัพธ์ที่คาดหวัง:** `devtools-fullstack-lab001` มีสถานะ `Up` และ port mapping `2222->22`

### 0.3 เชื่อมต่อ SSH

📝 **คำอธิบาย:** image สำหรับ LAB ใช้บัญชี `root` และรหัสผ่าน LAB-only คือ `passwd`

```bash
ssh root@localhost -p 2222
```

✅ **ผลลัพธ์ที่คาดหวัง:** prompt เปลี่ยนเป็น `root@<container-id>:~#` โดย container ID แตกต่างกันได้

### 0.4 ตรวจ Docker และ Docker Compose

📝 **คำอธิบาย:** ตรวจว่า Docker Engine และ Compose ภายในเครื่องปฏิบัติการพร้อมใช้งาน

```bash
docker --version && docker compose version
```

✅ **ผลลัพธ์ที่คาดหวัง:** แสดงรุ่นของ Docker และ Docker Compose โดยไม่มีข้อความ `Cannot connect to the Docker daemon`

### 0.5 รับ source code

📝 **คำอธิบาย:** สร้างพื้นที่ทดลองและเปลี่ยน working directory เข้าไปในคำสั่งเดียว

```bash
mkdir -p /root/skillspace-lab && cd /root/skillspace-lab
```

✅ **ผลลัพธ์ที่คาดหวัง:** prompt อยู่ภายใต้ `/root/skillspace-lab`

📝 **คำอธิบาย:** clone repository จริงภายในพื้นที่ทดลอง

```bash
git clone https://github.com/Tuchsanai/DevTools.git
```

✅ **ผลลัพธ์ที่คาดหวัง:** แสดง `Cloning into 'DevTools'...` และดาวน์โหลดสำเร็จ

📝 **คำอธิบาย:** เข้าสู่ LAB 001 แล้วตรวจไฟล์ schema, seed และ Python client

```bash
cd DevTools/02_Docker/03_Fullstack_App_Example/001_LAB_Run_The_System
ls db/initdb python
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบ `01-schema.sql`, `02-seed.sql`, `01_connect.py`, `02_query.py` และ `requirements.txt`

## การทดลองที่ 1 — สร้าง PostgreSQL ด้วยคอนเทนเนอร์และตรวจสอบสถานะ

📝 **คำอธิบาย:** คำสั่งสามบรรทัดทำงานตามลำดับ ได้แก่ ลบ `ops-db` เดิม สร้าง PostgreSQL ใหม่ และตรวจสถานะ การ mount `01-schema.sql` และ `02-seed.sql` ไปยัง `/docker-entrypoint-initdb.d` ทำให้ PostgreSQL สร้างตารางก่อนเติมข้อมูลตั้งต้นในการเริ่มฐานข้อมูลครั้งแรก พอร์ตถูกผูกกับ `127.0.0.1` เพื่อให้ Python ภายในเครื่องปฏิบัติการเป็นช่องทางจัดการข้อมูล

```bash
docker rm -f ops-db 2>/dev/null
docker run -d --name ops-db -p 127.0.0.1:5432:5432 --env-file .env.db -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
docker ps --filter name=ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** Docker แสดง container ID ใหม่ และบรรทัดสุดท้ายแสดง `ops-db` ในสถานะ `Up` พร้อม mapping `127.0.0.1:5432->5432/tcp` เวลาสถานะและ container ID แตกต่างกันได้

## การทดลองที่ 2 — เตรียม Python client

📝 **คำอธิบาย:** สร้าง virtual environment เพื่อแยก dependency ของ LAB

```bash
python3 -m venv .venv
```

✅ **ผลลัพธ์ที่คาดหวัง:** มีไดเรกทอรี `.venv` โดยไม่มี error

📝 **คำอธิบาย:** activate environment แล้วติดตั้ง psycopg 3 รุ่นที่กำหนด

```bash
. .venv/bin/activate
pip install -r python/requirements.txt
```

✅ **ผลลัพธ์ที่คาดหวัง:** prompt อาจมี `(.venv)` และติดตั้ง `psycopg 3.2.12` สำเร็จ

📝 **คำอธิบาย:** connection string ระบุค่าที่ Python ใช้เชื่อมต่อฐานข้อมูล

```bash
export DATABASE_URL="postgresql://opsuser:labpass@localhost:5432/skillspace"
```

✅ **ผลลัพธ์ที่คาดหวัง:** คำสั่งไม่แสดงข้อความและตัวแปรพร้อมใช้ใน shell ปัจจุบัน

## การทดลองที่ 3 — เชื่อมต่อและตรวจชื่อฐานข้อมูล

📝 **คำอธิบาย:** สร้าง `python/01_connect.py` ด้วยโค้ดด้านล่าง `psycopg.connect()` เปิด connection, `cursor()` สร้างตัวส่ง SQL, `execute()` ส่ง query และ `fetchone()` อ่านผลหนึ่งแถว ฟังก์ชัน retry รองรับช่วงที่ PostgreSQL ยังเริ่มทำงานไม่เสร็จ

```python
import os
import sys
import time

import psycopg

def connect_with_retry():
    for attempt in range(1, 31):
        try:
            return psycopg.connect(os.environ["DATABASE_URL"], connect_timeout=2)
        except (KeyError, psycopg.OperationalError):
            if attempt == 30:
                raise
            time.sleep(1)
    raise RuntimeError("unreachable")

try:
    with connect_with_retry() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database()")
            print(f"database={cur.fetchone()[0]}")
except (KeyError, psycopg.Error) as exc:
    print(f"เชื่อมต่อ PostgreSQL ไม่สำเร็จ: {exc}", file=sys.stderr)
    raise SystemExit(1) from exc
```

📝 **คำอธิบาย:** รัน client เพื่อยืนยันการเชื่อมต่อจริง

```bash
python python/01_connect.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** `database=skillspace`

## การทดลองที่ 4 — สำรวจโครงสร้างและข้อมูลทั้งห้าตาราง

📝 **คำอธิบาย:** สร้าง `python/02_query.py` ด้วยโค้ดด้านล่าง โปรแกรมอ่านรายชื่อตารางและ metadata จาก `information_schema` แล้วแสดงจำนวนแถว ชื่อและชนิดคอลัมน์ และข้อมูลจริงสูงสุด 15 แถวต่อหนึ่งตาราง ตารางที่มีข้อมูลน้อยกว่า 15 แถวจะแสดงครบทั้งหมด `dict_row` ทำให้เข้าถึงค่าด้วยชื่อคอลัมน์ ส่วนชื่อตารางใช้ allowlist และ `sql.Identifier` แทนการต่อ input ลง SQL โดยตรง

```python
import json
import os
import time

import psycopg
from psycopg import sql
from psycopg.rows import dict_row

TABLES = ("assets", "tickets", "loans", "parts", "stock_moves")

def connect_with_retry():
    for attempt in range(1, 31):
        try:
            return psycopg.connect(
                os.environ["DATABASE_URL"], connect_timeout=2, row_factory=dict_row
            )
        except psycopg.OperationalError:
            if attempt == 30:
                raise
            time.sleep(1)
    raise RuntimeError("unreachable")

def inspect_table(cur, table):
    if table not in TABLES:
        raise ValueError(f"ไม่อนุญาตให้สำรวจตาราง: {table}")
    cur.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
        ("public", table),
    )
    columns = cur.fetchall()
    count_query = sql.SQL("SELECT count(*) AS n FROM {}").format(sql.Identifier(table))
    cur.execute(count_query)
    count = cur.fetchone()["n"]
    sample_query = sql.SQL("SELECT * FROM {} ORDER BY id LIMIT %s").format(
        sql.Identifier(table)
    )
    cur.execute(sample_query, (15,))
    rows = cur.fetchall()
    print(f"\n=== {table} ({count} rows) ===")
    print("columns: " + " | ".join(
        f"{column['column_name']}:{column['data_type']}" for column in columns
    ))
    for index, row in enumerate(rows, start=1):
        print(f"row[{index}]: " + json.dumps(
            dict(row), ensure_ascii=False, default=str
        ))

with connect_with_retry() as conn:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' ORDER BY table_name"
        )
        tables = tuple(row["table_name"] for row in cur.fetchall())
        print("tables=" + ",".join(tables))
        if set(tables) != set(TABLES):
            raise RuntimeError("ชุดตารางไม่ตรงกับแบบจำลองข้อมูล LAB 001")
        for table in TABLES:
            inspect_table(cur, table)
```

📝 **คำอธิบาย:** รัน query จริงจาก Python และตรวจผลของ seed

```bash
python python/02_query.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** `LIMIT 15` คือจำนวนสูงสุดต่อหนึ่งตาราง จึงเห็นข้อมูล seed ครบทุกแถวของ LAB นี้ ค่า timestamp เปลี่ยนตามเวลาที่ PostgreSQL initialize แต่ element อื่นควรตรงกับตัวอย่างต่อไปนี้

```text
tables=assets,loans,parts,stock_moves,tickets

=== assets (12 rows) ===
columns: id:integer | code:text | name:text | location:text | created_at:timestamp with time zone
row[1]: {"id": 1, "code": "A-001", "name": "โน้ตบุ๊ก Dell Latitude", "location": "ห้องพัสดุ ชั้น 1", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[2]: {"id": 2, "code": "A-002", "name": "โปรเจกเตอร์ Epson EB-X51", "location": "ห้องอบรม 301", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[3]: {"id": 3, "code": "A-003", "name": "กล้อง Sony ZV-1", "location": "ห้องพัสดุ ชั้น 1", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[4]: {"id": 4, "code": "A-004", "name": "ไมโครโฟนไร้สาย Shure", "location": "ห้องประชุมใหญ่", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[5]: {"id": 5, "code": "A-005", "name": "โปรเจกเตอร์ BenQ MW550", "location": "ห้องอบรม 205", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[6]: {"id": 6, "code": "A-006", "name": "เครื่องปรับอากาศ ห้องแล็บ 2", "location": "ห้องแล็บคอมพิวเตอร์ 2", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[7]: {"id": 7, "code": "A-007", "name": "เครื่องพิมพ์ HP LaserJet", "location": "สำนักงาน ชั้น 2", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[8]: {"id": 8, "code": "A-008", "name": "สวิตช์เครือข่าย 24 พอร์ต", "location": "ห้องเซิร์ฟเวอร์", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[9]: {"id": 9, "code": "A-009", "name": "โน้ตบุ๊ก Lenovo ThinkPad", "location": "ห้องแล็บคอมพิวเตอร์ 4", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[10]: {"id": 10, "code": "A-010", "name": "จอแสดงผล LG 27 นิ้ว", "location": "ห้องแล็บคอมพิวเตอร์ 1", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[11]: {"id": 11, "code": "A-011", "name": "เครื่องสแกนเอกสาร Canon", "location": "สำนักงาน ชั้น 2", "created_at": "2026-08-30 16:30:15.979128+00:00"}
row[12]: {"id": 12, "code": "A-012", "name": "ลำโพงห้องอบรม 402", "location": "ห้องอบรม 402", "created_at": "2026-08-30 16:30:15.979128+00:00"}

=== tickets (8 rows) ===
columns: id:integer | asset_id:integer | title:text | detail:text | priority:text | status:text | assignee:text | created_at:timestamp with time zone | closed_at:timestamp with time zone
row[1]: {"id": 1, "asset_id": 5, "title": "โปรเจกเตอร์ห้อง 205 ภาพวูบดับ", "detail": "เปิดไปสักพักภาพดับเอง ต้องถอดปลั๊กแล้วเสียบใหม่", "priority": "HIGH", "status": "NEW", "assignee": null, "created_at": "2026-08-25 16:30:15.986529+00:00", "closed_at": null}
row[2]: {"id": 2, "asset_id": 6, "title": "แอร์ห้องแล็บ 2 ไม่เย็น", "detail": "ลมออกแต่ไม่เย็น อาจต้องเติมน้ำยา", "priority": "NORMAL", "status": "NEW", "assignee": null, "created_at": "2026-08-30 14:30:15.986529+00:00", "closed_at": null}
row[3]: {"id": 3, "asset_id": 7, "title": "เครื่องพิมพ์ป้อนกระดาษซ้อน", "detail": "ดึงกระดาษทีละ 2 แผ่น", "priority": "LOW", "status": "NEW", "assignee": null, "created_at": "2026-08-28 16:30:15.986529+00:00", "closed_at": null}
row[4]: {"id": 4, "asset_id": 8, "title": "สวิตช์เครือข่ายพอร์ต 12 ไฟไม่ติด", "detail": "เสียบสายแล้วไม่มีลิงก์ ย้ายไปพอร์ตอื่นใช้ได้", "priority": "NORMAL", "status": "ASSIGNED", "assignee": "TECH-01", "created_at": "2026-08-21 16:30:15.986529+00:00", "closed_at": null}
row[5]: {"id": 5, "asset_id": 9, "title": "โน้ตบุ๊กแล็บ 4 เปิดไม่ติด", "detail": "กดปุ่มแล้วไฟไม่ขึ้นเลย", "priority": "HIGH", "status": "ASSIGNED", "assignee": "TECH-02", "created_at": "2026-08-30 13:30:15.986529+00:00", "closed_at": null}
row[6]: {"id": 6, "asset_id": 10, "title": "จอแล็บ 1 มีเส้นแนวตั้ง", "detail": "เส้นสีชมพูกลางจอ", "priority": "NORMAL", "status": "IN_PROGRESS", "assignee": "TECH-01", "created_at": "2026-08-29 16:30:15.986529+00:00", "closed_at": null}
row[7]: {"id": 7, "asset_id": 11, "title": "สแกนเนอร์สแกนแล้วมีเส้นดำ", "detail": "ทำความสะอาดกระจกแล้วยังเป็น", "priority": "LOW", "status": "DONE", "assignee": "TECH-03", "created_at": "2026-08-18 16:30:15.986529+00:00", "closed_at": "2026-08-21 16:30:15.986529+00:00"}
row[8]: {"id": 8, "asset_id": 12, "title": "ลำโพงห้อง 402 ไม่มีเสียง", "detail": "สายชำรุด เปลี่ยนสายใหม่", "priority": "HIGH", "status": "DONE", "assignee": "TECH-01", "created_at": "2026-08-23 16:30:15.986529+00:00", "closed_at": "2026-08-24 16:30:15.986529+00:00"}

=== loans (3 rows) ===
columns: id:integer | asset_id:integer | borrower:text | borrowed_at:timestamp with time zone | returned_at:timestamp with time zone
row[1]: {"id": 1, "asset_id": 1, "borrower": "วิทยากรหลักสูตร Data 101", "borrowed_at": "2026-08-26 16:30:15.982696+00:00", "returned_at": null}
row[2]: {"id": 2, "asset_id": 2, "borrower": "เจ้าหน้าที่ธุรการ", "borrowed_at": "2026-08-29 16:30:15.982696+00:00", "returned_at": null}
row[3]: {"id": 3, "asset_id": 3, "borrower": "วิทยากรหลักสูตร UX 204", "borrowed_at": "2026-08-20 16:30:15.982696+00:00", "returned_at": "2026-08-24 16:30:15.982696+00:00"}

=== parts (6 rows) ===
columns: id:integer | sku:text | name:text | qty_on_hand:integer | reorder_point:integer
row[1]: {"id": 1, "sku": "LAMP-EPS-01", "name": "หลอดโปรเจกเตอร์ Epson", "qty_on_hand": 2, "reorder_point": 5}
row[2]: {"id": 2, "sku": "FAN-NB-14", "name": "พัดลมระบายความร้อนโน้ตบุ๊ก", "qty_on_hand": 12, "reorder_point": 4}
row[3]: {"id": 3, "sku": "KBD-USB-01", "name": "คีย์บอร์ด USB", "qty_on_hand": 8, "reorder_point": 3}
row[4]: {"id": 4, "sku": "CBL-HDMI-3M", "name": "สาย HDMI ยาว 3 เมตร", "qty_on_hand": 1, "reorder_point": 6}
row[5]: {"id": 5, "sku": "SSD-256", "name": "SSD 256GB", "qty_on_hand": 20, "reorder_point": 5}
row[6]: {"id": 6, "sku": "MIC-CAP-01", "name": "หัวไมโครโฟนสำรอง", "qty_on_hand": 9, "reorder_point": 2}

=== stock_moves (6 rows) ===
columns: id:integer | part_id:integer | ticket_id:integer | delta:integer | reason:text | created_at:timestamp with time zone
row[1]: {"id": 1, "part_id": 1, "ticket_id": null, "delta": 5, "reason": "รับเข้าจากผู้ขาย", "created_at": "2026-07-31 16:30:15.994952+00:00"}
row[2]: {"id": 2, "part_id": 1, "ticket_id": null, "delta": -3, "reason": "เบิกใช้เตรียมห้องอบรมประจำเดือน", "created_at": "2026-08-10 16:30:15.994952+00:00"}
row[3]: {"id": 3, "part_id": 4, "ticket_id": null, "delta": 6, "reason": "รับเข้าจากผู้ขาย", "created_at": "2026-08-05 16:30:15.994952+00:00"}
row[4]: {"id": 4, "part_id": 4, "ticket_id": 8, "delta": -5, "reason": "ใช้ในงานซ่อม", "created_at": "2026-08-24 16:30:15.994952+00:00"}
row[5]: {"id": 5, "part_id": 3, "ticket_id": null, "delta": 9, "reason": "รับเข้าจากผู้ขาย", "created_at": "2026-08-02 16:30:15.994952+00:00"}
row[6]: {"id": 6, "part_id": 3, "ticket_id": 7, "delta": -1, "reason": "ใช้ในงานซ่อม", "created_at": "2026-08-21 16:30:15.994952+00:00"}
```

### อ่านผลลัพธ์เดียวกันแบบตาราง

บล็อกด้านบนคือ output จริงที่ Python พิมพ์จาก PostgreSQL ส่วนตารางต่อไปนี้จัดข้อมูลชุดเดียวกันให้อ่านความหมายทางธุรกิจและเทียบกับสไลด์ได้ง่ายขึ้น โดยใช้ค่าจาก `02-seed.sql` และเชื่อม `asset_id`, `part_id` และ `ticket_id` กลับเป็นรหัสหรือชื่อที่มนุษย์อ่านได้

เวลาใน seed เขียนเป็น `now() - interval ...` จึงแสดงเป็นช่วงเวลาสัมพัทธ์ เช่น “4 วันที่แล้ว” แทน timestamp ตายตัว ค่า timestamp จริงให้ตรวจจาก raw output ของเครื่องผู้เรียน

#### ภาพรวม: หนึ่ง database · ห้า tables

| Table | หนึ่งแถวหมายถึง | จำนวนแถว | ตัวอย่างที่ควรหาเจอใน Python output |
|---|---|---:|---|
| `assets` | ครุภัณฑ์หนึ่งชิ้น | 12 | `A-001` · โน้ตบุ๊ก Dell Latitude |
| `tickets` | ปัญหาหรืองานซ่อมหนึ่งเหตุการณ์ | 8 | `A-005` · HIGH · NEW |
| `loans` | การยืมหนึ่งครั้ง | 3 | วิทยากรหลักสูตร Data 101 · ยังไม่คืน |
| `parts` | อะไหล่หนึ่งชนิดและยอดคงเหลือปัจจุบัน | 6 | `LAMP-EPS-01` · คงเหลือ 2 |
| `stock_moves` | เหตุการณ์ที่ทำให้ยอดอะไหล่เปลี่ยนหนึ่งครั้ง | 6 | `LAMP-EPS-01` · `+5` · รับเข้าจากผู้ขาย |

`assets` และ `parts` บอกว่า “เรามีอะไร” · `tickets` และ `loans` บอกว่า “เกิดอะไรขึ้น” · `stock_moves` บอกว่า “ยอดเปลี่ยนเพราะอะไร”

#### `assets` — ตัวอย่าง 6 จาก 12 แถว

| code | name | location | นำไปเชื่อมกับ |
|---|---|---|---|
| `A-001` | โน้ตบุ๊ก Dell Latitude | ห้องพัสดุ ชั้น 1 | `loans` |
| `A-002` | โปรเจกเตอร์ Epson EB-X51 | ห้องอบรม 301 | `loans` |
| `A-003` | กล้อง Sony ZV-1 | ห้องพัสดุ ชั้น 1 | `loans` |
| `A-004` | ไมโครโฟนไร้สาย Shure | ห้องประชุมใหญ่ | พร้อมใช้งาน |
| `A-005` | โปรเจกเตอร์ BenQ MW550 | ห้องอบรม 205 | `tickets` |
| `A-006` | เครื่องปรับอากาศ ห้องแล็บ 2 | ห้องแล็บคอมพิวเตอร์ 2 | `tickets` |

`assets.id` คือ parent key ที่ `tickets.asset_id` และ `loans.asset_id` ใช้อ้างอิง ดังนั้น `asset_id: 5` ใน raw output ของ `tickets` จึงหมายถึง `A-005`

#### `tickets` — ตัวอย่าง 6 จาก 8 แถว

| asset | title | priority | status | assignee |
|---|---|---|---|---|
| `A-005` | โปรเจกเตอร์ห้อง 205 ภาพวูบดับ | HIGH | NEW | — |
| `A-006` | แอร์ห้องแล็บ 2 ไม่เย็น | NORMAL | NEW | — |
| `A-007` | เครื่องพิมพ์ป้อนกระดาษซ้อน | LOW | NEW | — |
| `A-008` | สวิตช์เครือข่ายพอร์ต 12 ไฟไม่ติด | NORMAL | ASSIGNED | `TECH-01` |
| `A-009` | โน้ตบุ๊กแล็บ 4 เปิดไม่ติด | HIGH | ASSIGNED | `TECH-02` |
| `A-010` | จอแล็บ 1 มีเส้นแนวตั้ง | NORMAL | IN_PROGRESS | `TECH-01` |

จากข้อมูลชุดนี้มองเห็นทั้งลำดับงานใน `status`, ผู้รับผิดชอบใน `assignee` และระดับความเร่งด่วนใน `priority`

#### `loans` — ครบทั้ง 3 แถว

| asset | borrower | borrowed_at | returned_at |
|---|---|---|---|
| `A-001` | วิทยากรหลักสูตร Data 101 | 4 วันที่แล้ว | **NULL · ยังไม่คืน** |
| `A-002` | เจ้าหน้าที่ธุรการ | 1 วันที่แล้ว | **NULL · ยังไม่คืน** |
| `A-003` | วิทยากรหลักสูตร UX 204 | 10 วันที่แล้ว | คืนแล้วเมื่อ 6 วันที่แล้ว |

เมื่อ `returned_at` เป็น `NULL` ครุภัณฑ์ชิ้นนั้นยังถูกยืมอยู่ จึงใช้ตัดสินเงื่อนไขห้ามยืมซ้ำได้

#### `parts` — ครบทั้ง 6 แถว

| sku | name | qty_on_hand | reorder_point | ผลจาก `qty_on_hand < reorder_point` |
|---|---|---:|---:|---|
| `LAMP-EPS-01` | หลอดโปรเจกเตอร์ Epson | **2** | 5 | **ต้องสั่งเพิ่ม** |
| `FAN-NB-14` | พัดลมระบายความร้อนโน้ตบุ๊ก | 12 | 4 | เพียงพอ |
| `KBD-USB-01` | คีย์บอร์ด USB | 8 | 3 | เพียงพอ |
| `CBL-HDMI-3M` | สาย HDMI ยาว 3 เมตร | **1** | 6 | **ต้องสั่งเพิ่ม** |
| `SSD-256` | SSD 256GB | 20 | 5 | เพียงพอ |
| `MIC-CAP-01` | หัวไมโครโฟนสำรอง | 9 | 2 | เพียงพอ |

#### `stock_moves` — ครบทั้ง 6 แถว

| part | delta | reason | ticket ที่เกี่ยวข้อง |
|---|---:|---|---|
| `LAMP-EPS-01` | **+5** | รับเข้าจากผู้ขาย | — |
| `LAMP-EPS-01` | **-3** | เบิกใช้เตรียมห้องอบรมประจำเดือน | — |
| `CBL-HDMI-3M` | **+6** | รับเข้าจากผู้ขาย | — |
| `CBL-HDMI-3M` | **-5** | ใช้ในงานซ่อม | ลำโพงห้อง 402 ไม่มีเสียง |
| `KBD-USB-01` | **+9** | รับเข้าจากผู้ขาย | — |
| `KBD-USB-01` | **-1** | ใช้ในงานซ่อม | สแกนเนอร์สแกนแล้วมีเส้นดำ |

ค่า `delta` บวกคือรับเข้าและค่าติดลบคือเบิกออก ผลรวมของประวัติในตัวอย่างตรงกับยอดปัจจุบัน ได้แก่ `5 - 3 = 2`, `6 - 5 = 1` และ `9 - 1 = 8`

## การทดลองที่ 5 — ทำความสะอาด

📝 **คำอธิบาย:** ลบคอนเทนเนอร์ฐานข้อมูลหลังสำรวจเสร็จ

```bash
docker rm -f ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** แสดง `ops-db`

📝 **คำอธิบาย:** ออกจาก SSH แล้วลบเครื่องปฏิบัติการจากเครื่องผู้ใช้

```bash
exit
docker rm -f devtools-fullstack-lab001
```

✅ **ผลลัพธ์ที่คาดหวัง:** กลับสู่ prompt ของเครื่องผู้ใช้และแสดง `devtools-fullstack-lab001`

## สรุปผลการเรียนรู้

ผู้เรียนควรอธิบายได้ว่า `skillspace` เป็นฐานข้อมูลหนึ่งฐานที่มีห้าตาราง schema ทำงานก่อน seed ในการเริ่มครั้งแรก และ Python ใช้ connection กับ cursor เพื่อส่ง query แล้วอ่านผลลัพธ์จาก PostgreSQL โดยตรง
