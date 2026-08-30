# LAB 001 — PostgreSQL: จากแบบจำลองข้อมูลสู่คำสั่ง SQL

> LAB นี้ศึกษาชั้นฐานข้อมูลของสถาปัตยกรรม `Browser → Next.js web → FastAPI api → PostgreSQL db` ระบบมีฐานข้อมูล PostgreSQL **หนึ่งฐานชื่อ `skillspace`** และมีห้าตาราง ได้แก่ `assets`, `tickets`, `loans`, `parts` และ `stock_moves`

## สิ่งที่จะได้เรียนรู้

- เริ่ม PostgreSQL จาก schema และ seed แล้วตรวจข้อมูลผ่าน Python client
- ใช้ Python และ psycopg 3 เป็น database client เพียงช่องทางเดียว
- อ่าน metadata จาก `information_schema`, นับข้อมูล และใช้ parameterized query
- เชื่อมโยง `GET /api/tickets` กับ SQL template และ parameters จริง
- ทดลอง rollback, commit, constraint error และ cleanup
- พิสูจน์การคงอยู่ของข้อมูลด้วย Named Volume

## ภาพรวมของแล็บนี้

![สถาปัตยกรรม SkillSpace และขอบเขต LAB 001](./images/theory-three-boxes.svg)

ผู้เรียนทำงานหลัง SSH เข้า `devtools-fullstack-lab001` แล้ว คอนเทนเนอร์ `ops-db` publish PostgreSQL ที่ `localhost:5432` **ภายในเครื่องปฏิบัติการเท่านั้น** จึงไม่ได้เปิดฐานข้อมูลสู่เครื่องผู้ใช้ Python ทำหน้าที่แทน data-access layer ของ FastAPI ชั่วคราว Browser ไม่เชื่อม PostgreSQL โดยตรง

แต่ละ micro-step มีวัตถุประสงค์เดียว และเรียงเป็น **เหตุผล → คำสั่ง → ผลลัพธ์ที่คาดหวัง → ความหมายของผล**

---

## 0. เตรียมเครื่องปฏิบัติการ

### 0.1 ลบเครื่องปฏิบัติการชื่อเดิม

📝 **คำอธิบาย:** ขั้นนี้ทำให้รัน LAB ซ้ำได้โดยไม่เกิดชื่อคอนเทนเนอร์ซ้ำ รันบนเครื่องผู้ใช้

```bash
docker rm -f devtools-fullstack-lab001 2>/dev/null
```

✅ **ผลลัพธ์ที่คาดหวัง:** แสดง `devtools-fullstack-lab001` หากมีคอนเทนเนอร์เดิม หรือไม่แสดงข้อความหากไม่พบ

### 0.2 สร้างเครื่องปฏิบัติการ

📝 **คำอธิบาย:** `--privileged` อนุญาต Docker-in-Docker และ `-p 2222:22` ส่ง SSH จากเครื่องผู้ใช้ไปยังเครื่องปฏิบัติการ

```bash
docker run -dit --name devtools-fullstack-lab001 --privileged -p 2222:22 tuchsanai/devtools:2569_1
```

✅ **ผลลัพธ์ที่คาดหวัง:** Docker แสดง container ID หนึ่งบรรทัด

### 0.3 ตรวจสถานะเครื่องปฏิบัติการ

📝 **คำอธิบาย:** การสร้างสำเร็จยังไม่รับรองว่า process หลักทำงาน จึงตรวจสถานะแยกต่างหาก

```bash
docker ps --filter name=devtools-fullstack-lab001
```

✅ **ผลลัพธ์ที่คาดหวัง:** ชื่อ `devtools-fullstack-lab001` มีสถานะ `Up` และมี port mapping `2222->22`

### 0.4 เชื่อมต่อ SSH

📝 **คำอธิบาย:** image สำหรับ LAB ใช้บัญชี `root` และรหัสผ่าน LAB-only คือ `passwd`

```bash
ssh root@localhost -p 2222
```

✅ **ผลลัพธ์ที่คาดหวัง:** prompt เปลี่ยนเป็น `root@<container-id>:~#` โดย container ID แตกต่างกันได้

### 0.5 ตรวจ Docker ภายในเครื่องปฏิบัติการ

📝 **คำอธิบาย:** ยืนยันว่า Docker CLI ติดต่อ daemon ที่ทำงานอยู่ภายในเครื่องปฏิบัติการได้

```bash
docker --version
```

✅ **ผลลัพธ์ที่คาดหวัง:** แสดง Docker version โดยไม่มี `Cannot connect to the Docker daemon`

📝 **คำอธิบาย:** ตรวจ Compose แยกอีกขั้นเพื่อเตรียมพื้นฐานสำหรับ LAB 005

```bash
docker compose version
```

✅ **ผลลัพธ์ที่คาดหวัง:** แสดง Docker Compose version เลขรุ่นอาจแตกต่างกัน

### 0.6 รับ source code

📝 **คำอธิบาย:** clone repository จริงภายในเครื่องปฏิบัติการ เพื่อให้ schema, seed และ Python examples อยู่ใน environment เดียวกับ database client

```bash
git clone https://github.com/Tuchsanai/DevTools.git
```

✅ **ผลลัพธ์ที่คาดหวัง:** แสดง `Cloning into 'DevTools'...` และดาวน์โหลดเสร็จสมบูรณ์

📝 **คำอธิบาย:** เปลี่ยนไดเรกทอรีเข้าสู่ LAB 001 ก่อนรันคำสั่งถัดไป

```bash
cd DevTools/02_Docker/03_Fullstack_App_Example/001_LAB_Run_The_System
```

✅ **ผลลัพธ์ที่คาดหวัง:** คำสั่งไม่แสดง error

📝 **คำอธิบาย:** ตรวจไฟล์ที่เป็น input ของ PostgreSQL ก่อนเริ่มคอนเทนเนอร์

```bash
ls db/initdb python
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบ `01-schema.sql`, `02-seed.sql` และไฟล์ Python ของ LAB

---

## การทดลองที่ 1 — อ่าน schema และ seed ก่อนรัน

📝 **คำอธิบาย:** schema สร้างแบบจำลองข้อมูล จึงต้องอ่านก่อน seed

```bash
grep '^CREATE TABLE' db/initdb/01-schema.sql
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบ `CREATE TABLE` สำหรับ `assets`, `tickets`, `loans`, `parts`, `stock_moves`

📝 **คำอธิบาย:** seed เติมข้อมูลตั้งต้นหลังโครงสร้างพร้อมแล้ว

```bash
grep '^INSERT INTO' db/initdb/02-seed.sql
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบ `INSERT INTO` สำหรับทั้งห้าตาราง

![ลำดับ initialization scripts](./images/theory-initdb-when.svg)

---

## การทดลองที่ 2 — เริ่ม PostgreSQL และ publish เฉพาะในเครื่องปฏิบัติการ

📝 **คำอธิบาย:** ลบ `ops-db` เดิมก่อนเพื่อให้ initialization เริ่มจากสถานะที่คาดเดาได้

```bash
docker rm -f ops-db 2>/dev/null
```

✅ **ผลลัพธ์ที่คาดหวัง:** แสดง `ops-db` หากมีของเดิม หรือไม่แสดงข้อความ

📝 **คำอธิบาย:** bind mount ส่ง schema/seed แบบ read-only และ `-p 127.0.0.1:5432:5432` ให้ Python เชื่อม `localhost:5432` ได้เฉพาะภายในเครื่องปฏิบัติการ

```bash
docker run -d --name ops-db -p 127.0.0.1:5432:5432 --env-file .env.db -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
```

✅ **ผลลัพธ์ที่คาดหวัง:** Docker แสดง container ID

📝 **คำอธิบาย:** ตรวจ lifecycle โดยไม่เข้าไปสั่งงานใน database container

```bash
docker ps --filter name=ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** `ops-db` มีสถานะ `Up` และ mapping `0.0.0.0:5432->5432/tcp` ภายในเครื่องปฏิบัติการ

📝 **คำอธิบาย:** log ใช้ตรวจ initialization/readiness เท่านั้น ไม่ใช้บริหารข้อมูล

```bash
docker logs ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบ `01-schema.sql` ก่อน `02-seed.sql` และท้าย log มี `database system is ready to accept connections`

---

## การทดลองที่ 3 — เตรียม Python database client

📝 **คำอธิบาย:** สร้าง virtual environment เพื่อแยก dependency ของ LAB

```bash
python3 -m venv .venv
```

✅ **ผลลัพธ์ที่คาดหวัง:** สร้างโฟลเดอร์ `.venv` โดยไม่มี error

📝 **คำอธิบาย:** activate ทำให้ `python` และ `pip` ชี้เข้า environment ของ LAB

```bash
. .venv/bin/activate
```

✅ **ผลลัพธ์ที่คาดหวัง:** prompt อาจมี `(.venv)` นำหน้า

📝 **คำอธิบาย:** ติดตั้ง psycopg 3 รุ่นเดียวกับ LAB 002

```bash
python -m pip install -r python/requirements.txt
```

✅ **ผลลัพธ์ที่คาดหวัง:** ติดตั้ง `psycopg-3.2.12` สำเร็จ

📝 **คำอธิบาย:** connection string ชี้จาก Python บนเครื่องปฏิบัติการไปยังพอร์ตที่ `ops-db` publish

```bash
export DATABASE_URL="postgresql://opsuser:labpass@localhost:5432/skillspace"
```

✅ **ผลลัพธ์ที่คาดหวัง:** คำสั่งไม่แสดงข้อความและตัวแปรพร้อมใช้ใน process ถัดไป

---

## การทดลองที่ 4 — เขียน `01_connect.py`: connection, cursor และ fetchone

📝 **คำอธิบาย:** สร้างไฟล์ด้วยโค้ดเต็มด้านล่าง `with psycopg.connect` จัดการอายุ connection, cursor ส่ง SQL, `fetchone()` รับหนึ่งแถว และ `try/except` ทำให้ connection error สังเกตได้

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

✅ **ผลลัพธ์ที่คาดหวัง:** หลังบันทึกเป็น `python/01_connect.py` ไฟล์มีโค้ดครบและไม่มี indentation error

📝 **คำอธิบาย:** รัน client จากเครื่องปฏิบัติการ ฟังก์ชัน retry ลองได้สูงสุด 30 ครั้ง; `connect_timeout` จำกัดเวลาของแต่ละครั้งแต่ไม่ได้ retry เอง เมื่อ `with psycopg.connect` จบปกติ psycopg จะ commit transaction และปิด connection

```bash
python python/01_connect.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** `database=skillspace`

---

## การทดลองที่ 5 — เขียน `02_query.py`: โครงสร้างและข้อมูลตัวอย่างทั้งห้าตาราง

📝 **คำอธิบาย:** โค้ดนี้อ่านรายชื่อตารางและชนิดข้อมูลจาก `information_schema`, นับจำนวนแถว และแสดงข้อมูลจริงสามแถวแรกจากทุกตาราง จากนั้นจึงเรียก `get_tickets()` ตาม SQL behavior ของ `GET /api/tickets` จริง

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

def get_tickets(cur, status=None):
    sql = "SELECT id, status, assignee, title FROM tickets"
    params = ()
    if status is not None:
        sql += " WHERE status = %s"
        params = (status,)
    sql += " ORDER BY id"
    print(f"SQL={sql}")
    print(f"params={params}")
    cur.execute(sql, params)
    return cur.fetchall()

def inspect_table(cur, table):
    if table not in TABLES:
        raise ValueError(f"ไม่อนุญาตให้สำรวจตาราง: {table}")

    cur.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_schema = %s AND table_name = %s ORDER BY ordinal_position",
        ("public", table),
    )
    columns = cur.fetchall()

    count_query = sql.SQL("SELECT count(*) AS n FROM {}").format(
        sql.Identifier(table)
    )
    cur.execute(count_query)
    count = cur.fetchone()["n"]

    sample_query = sql.SQL("SELECT * FROM {} ORDER BY id LIMIT %s").format(
        sql.Identifier(table)
    )
    cur.execute(sample_query, (3,))
    samples = cur.fetchall()

    print(f"\n=== {table} ({count} rows) ===")
    print(
        "columns: "
        + " | ".join(
            f"{column['column_name']}:{column['data_type']}" for column in columns
        )
    )
    for index, row in enumerate(samples, start=1):
        print(
            f"sample[{index}]: "
            + json.dumps(dict(row), ensure_ascii=False, default=str)
        )

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

        assigned = get_tickets(cur, "ASSIGNED")
        for row in assigned:
            print(
                f"ticket id={row['id']} status={row['status']} "
                f"assignee={row['assignee']}"
            )
```

✅ **ผลลัพธ์ที่คาดหวัง:** หลังบันทึกเป็น `python/02_query.py` source แสดง metadata query, allowlist, `sql.Identifier`, parameter `(3,)` และ `get_tickets()` ครบ

> `dict_row` คืนแต่ละแถวเป็น mapping ตามชื่อคอลัมน์; `json.dumps(..., default=str)` จัดรูปแบบ timestamp ให้อ่านได้; `%s` รับค่าข้อมูลแยกจาก SQL; ชื่อตารางเป็น identifier จึงใช้ได้เฉพาะค่าจาก `TABLES` และส่งผ่าน `sql.Identifier` ห้ามนำ input มาต่อโดยตรง

📝 **คำอธิบาย:** รัน query จริงกับ PostgreSQL และตรวจผลของ seed

```bash
python python/02_query.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบหัวข้อ `assets (12 rows)`, `tickets (8 rows)`, `loans (3 rows)`, `parts (6 rows)`, `stock_moves (6 rows)` แต่ละหัวข้อมี `columns:` และ `sample[1]` ถึง `sample[3]` จาก seed จริง ตัวอย่างที่สังเกตได้ ได้แก่ asset `A-001`, ticket id 1, borrower `วิทยากรหลักสูตร Data 101`, part `LAMP-EPS-01` และ stock move เหตุผล `รับเข้าจากผู้ขาย` ตอนท้ายยังได้ ticket id 4/`TECH-01` และ id 5/`TECH-02` จาก parameter `('ASSIGNED',)`

---

## การทดลองที่ 6 — อ่าน Request → SQL → ผลลัพธ์จริง

📝 **คำอธิบาย:** เปิด route จริงของ LAB 002 เพื่อเปรียบเทียบ SQL template กับฟังก์ชัน `get_tickets()` โดยไม่รัน API ก่อนเวลา

```bash
sed -n '332,382p' ../002_LAB_Build_The_API/api/main.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** เห็น `GET /api/tickets`, optional filters, SQL และ params ที่ส่งแยกกัน

📝 **คำอธิบาย:** เรียก query จริงอีกครั้งเพื่อยืนยัน causal chain `request filter → SQL template → params → rows`

```bash
python python/02_query.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** ผล `ASSIGNED` มีสองแถวจาก `tickets`; นี่คือข้อมูลที่ FastAPI จะ serialize เป็น response ไม่ใช่ mapping คงที่ที่พิมพ์ไว้ล่วงหน้า

ตารางสรุป route อื่นอ่านได้จาก `REQUEST_MAP` ใน `python/learn_db.py` ซึ่งเป็น reference solution ท้ายบท แต่หลักฐานของการทดลองนี้มาจาก query ที่ execute จริง

---

## การทดลองที่ 7 — เขียน `03_rollback.py`: transaction ที่ยกเลิกได้

📝 **คำอธิบาย:** โค้ดทำ `INSERT`, อ่านจำนวนภายใน transaction แล้ว `rollback()` ก่อนเปิด connection ใหม่เพื่อตรวจผล หากเกิด SQL error จะ rollback ก่อนส่ง exception ต่อ

```python
import os
import psycopg

COUNT_SQL = "SELECT count(*) FROM tickets"
INSERT_SQL = """
INSERT INTO tickets (asset_id, title, detail, priority, status)
VALUES (%s, %s, %s, %s, 'NEW')
RETURNING id
"""

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    try:
        with conn.cursor() as cur:
            cur.execute(COUNT_SQL)
            before = cur.fetchone()[0]
            cur.execute("SELECT id FROM assets WHERE code = %s", ("A-004",))
            asset_id = cur.fetchone()[0]
            cur.execute(
                INSERT_SQL,
                (asset_id, "[LAB001-ROLLBACK]", "ข้อมูลชั่วคราว", "LOW"),
            )
            new_id = cur.fetchone()[0]
            cur.execute(COUNT_SQL)
            during = cur.fetchone()[0]
            print(f"before={before} during={during} new_id={new_id}")
        conn.rollback()
    except psycopg.Error:
        conn.rollback()
        raise

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute(COUNT_SQL)
        after = cur.fetchone()[0]
        print(f"after={after}")
```

✅ **ผลลัพธ์ที่คาดหวัง:** หลังบันทึกเป็น `python/03_rollback.py` เห็น `rollback()` ทั้ง success path และ exception path

📝 **คำอธิบาย:** รัน transaction และสังเกตจำนวนก่อน ระหว่าง และหลัง rollback

```bash
python python/03_rollback.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** `before=8`, `during=9`, `after=8`; ค่า `new_id` ไม่จำเป็นต้องเป็น 9 เพราะ PostgreSQL sequence ไม่ rollback

---

## การทดลองที่ 8 — แยก commit, constraint/rollback และ cleanup

### 8.1 `04_commit.py`

📝 **คำอธิบาย:** lookup asset ด้วย code `A-004` แทนการผูกกับ id แล้ว insert ticket และ commit อย่างชัดเจน

```python
import os
import psycopg

TITLE = "[LAB001-COMMIT]"
with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM assets WHERE code = %s", ("A-004",))
        asset_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO tickets (asset_id, title, detail, priority, status) "
            "VALUES (%s, %s, %s, %s, 'NEW') RETURNING id",
            (asset_id, TITLE, "ข้อมูลสำหรับสาธิต commit", "LOW"),
        )
        committed_id = cur.fetchone()[0]
    conn.commit()
    print(f"committed_id={committed_id}")
```

✅ **ผลลัพธ์ที่คาดหวัง:** source แสดง lookup → insert → commit เป็นลำดับเดียว

📝 **คำอธิบาย:** รัน write path และให้โปรแกรมคืน seed state ด้วยตนเอง

```bash
python python/04_commit.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** `committed_id=<ตัวเลข>` โดยค่า id เปลี่ยนได้

### 8.2 `04_constraint.py`

📝 **คำอธิบาย:** ไฟล์นี้มีวัตถุประสงค์เดียว คือทำให้ UNIQUE constraint ปฏิเสธ code ซ้ำและ rollback transaction ที่ผิดพลาด

```python
import os
import psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO assets (code, name, location) VALUES (%s, %s, %s)",
                ("A-001", "ข้อมูลซ้ำ", "LAB"),
            )
        conn.commit()
    except psycopg.errors.UniqueViolation as exc:
        conn.rollback()
        print(f"constraint={exc.diag.constraint_name} rollback=complete")
```

✅ **ผลลัพธ์ที่คาดหวัง:** source แสดง `except UniqueViolation` และ `rollback()`

```bash
python python/04_constraint.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** `constraint=assets_code_key rollback=complete`

### 8.3 `04_cleanup.py`

📝 **คำอธิบาย:** แยก cleanup ออกจาก commit เพื่อให้ตรวจผลของแต่ละ state change ได้

```python
import os
import psycopg

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        cur.execute("DELETE FROM tickets WHERE title = %s", ("[LAB001-COMMIT]",))
        deleted = cur.rowcount
    conn.commit()
    print(f"cleanup_deleted={deleted}")
```

✅ **ผลลัพธ์ที่คาดหวัง:** source มี parameterized DELETE และ explicit commit

```bash
python python/04_cleanup.py
```

✅ **ผลลัพธ์ที่คาดหวัง:** `cleanup_deleted=1`

---

## การทดลองที่ 9 — พิสูจน์ writable layer: ลบคอนเทนเนอร์แล้ว marker หาย

📝 **คำอธิบาย:** สร้าง `05_persistence.py` จาก source เต็มนี้ โปรแกรม lookup `A-004` และใช้ parameterized SQL สำหรับ add/check/remove marker

```python
import argparse
import os
import psycopg

TITLE = "[LAB001-PERSISTENCE]"
parser = argparse.ArgumentParser()
parser.add_argument("action", choices=("add", "check", "remove"))
action = parser.parse_args().action

with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
    with conn.cursor() as cur:
        if action == "add":
            cur.execute("SELECT id FROM assets WHERE code = %s", ("A-004",))
            asset_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO tickets (asset_id, title, detail, priority, status) "
                "VALUES (%s, %s, %s, %s, 'NEW')",
                (asset_id, TITLE, "ข้อมูลพิสูจน์ persistence", "LOW"),
            )
            conn.commit()
            print("marker=committed")
        elif action == "check":
            cur.execute("SELECT count(*) FROM tickets WHERE title = %s", (TITLE,))
            print(f"marker_count={cur.fetchone()[0]}")
        else:
            cur.execute("DELETE FROM tickets WHERE title = %s", (TITLE,))
            deleted = cur.rowcount
            conn.commit()
            print(f"marker_deleted={deleted}")
```

✅ **ผลลัพธ์ที่คาดหวัง:** source ใน README ตรงกับ `python/05_persistence.py` และเห็น params/commit ของ write paths

📝 **คำอธิบาย:** commit marker ลง writable layer ของ `ops-db`

```bash
python python/05_persistence.py add
```

✅ **ผลลัพธ์ที่คาดหวัง:** `marker=committed`

📝 **คำอธิบาย:** ลบคอนเทนเนอร์จึงลบ writable layer ไปพร้อมกัน

```bash
docker rm -f ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** `ops-db`

📝 **คำอธิบาย:** สร้าง PostgreSQL ใหม่โดยไม่มี Volume ทำให้ init scripts ทำงานกับ data directory ว่าง

```bash
docker run -d --name ops-db -p 127.0.0.1:5432:5432 --env-file .env.db -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
```

✅ **ผลลัพธ์ที่คาดหวัง:** Docker แสดง container ID ใหม่

📝 **คำอธิบาย:** Python connection มี retry ในระดับ driver เมื่อรันหลัง log พร้อม; ตรวจ readiness ด้วย log ก่อน query

```bash
docker logs ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบ `database system is ready to accept connections`

📝 **คำอธิบาย:** query marker จาก PostgreSQL ที่สร้างใหม่

```bash
python python/05_persistence.py check
```

✅ **ผลลัพธ์ที่คาดหวัง:** `marker_count=0`

![ตำแหน่งข้อมูลเมื่อไม่มีและมี Named Volume](./images/theory-where-is-data.svg)

---

## การทดลองที่ 10 — พิสูจน์ Named Volume และทำความสะอาด

📝 **คำอธิบาย:** ลบ `ops-db` เพื่อเตรียม mount Named Volume

```bash
docker rm -f ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** `ops-db`

📝 **คำอธิบาย:** สร้าง storage ที่มีอายุแยกจากคอนเทนเนอร์

```bash
docker volume create ops-pgdata
```

✅ **ผลลัพธ์ที่คาดหวัง:** `ops-pgdata`

📝 **คำอธิบาย:** เริ่ม PostgreSQL โดย mount Named Volume ที่ data directory

```bash
docker run -d --name ops-db -p 127.0.0.1:5432:5432 --env-file .env.db -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
```

✅ **ผลลัพธ์ที่คาดหวัง:** Docker แสดง container ID

📝 **คำอธิบาย:** ตรวจ readiness ก่อนให้ Python เชื่อมต่อ

```bash
docker logs ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบ `database system is ready to accept connections`

📝 **คำอธิบาย:** commit marker ลงฐานข้อมูลที่เก็บใน Volume

```bash
python python/05_persistence.py add
```

✅ **ผลลัพธ์ที่คาดหวัง:** `marker=committed`

📝 **คำอธิบาย:** ลบเฉพาะคอนเทนเนอร์ โดย Volume ยังคงอยู่

```bash
docker rm -f ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** `ops-db`

📝 **คำอธิบาย:** สร้างคอนเทนเนอร์ใหม่และ mount Volume เดิม

```bash
docker run -d --name ops-db -p 127.0.0.1:5432:5432 --env-file .env.db -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
```

✅ **ผลลัพธ์ที่คาดหวัง:** Docker แสดง container ID ใหม่

📝 **คำอธิบาย:** log ต้องแสดงว่า data directory มีข้อมูลอยู่แล้ว จึงไม่รัน seed ซ้ำ

```bash
docker logs ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** พบ `Skipping initialization` และ `ready to accept connections`

📝 **คำอธิบาย:** query marker จาก Volume เดิมด้วย Python

```bash
python python/05_persistence.py check
```

✅ **ผลลัพธ์ที่คาดหวัง:** `marker_count=1`

### Cleanup ภายในเครื่องปฏิบัติการ

📝 **คำอธิบาย:** ลบ marker ก่อนทำลาย storage เพื่อให้เห็น cleanup ผ่าน SQL client

```bash
python python/05_persistence.py remove
```

✅ **ผลลัพธ์ที่คาดหวัง:** `marker_deleted=1`

📝 **คำอธิบาย:** ลบ database container ตามชื่อเฉพาะของ LAB

```bash
docker rm -f ops-db
```

✅ **ผลลัพธ์ที่คาดหวัง:** `ops-db`

📝 **คำอธิบาย:** ลบ Named Volume หลังไม่มีคอนเทนเนอร์ใช้งานแล้ว

```bash
docker volume rm ops-pgdata
```

✅ **ผลลัพธ์ที่คาดหวัง:** `ops-pgdata`

📝 **คำอธิบาย:** ปิด virtual environment

```bash
deactivate
```

✅ **ผลลัพธ์ที่คาดหวัง:** `(.venv)` หายจาก prompt

📝 **คำอธิบาย:** ออกจาก SSH กลับสู่เครื่องผู้ใช้

```bash
exit
```

✅ **ผลลัพธ์ที่คาดหวัง:** prompt กลับเป็นของเครื่องผู้ใช้

### Cleanup บนเครื่องผู้ใช้

📝 **คำอธิบาย:** ลบเครื่องปฏิบัติการตามชื่อเฉพาะของ LAB

```bash
docker rm -f devtools-fullstack-lab001
```

✅ **ผลลัพธ์ที่คาดหวัง:** `devtools-fullstack-lab001`

📝 **คำอธิบาย:** ตรวจยืนยันว่าไม่เหลือเครื่องปฏิบัติการของ LAB

```bash
docker ps -a --filter name=devtools-fullstack-lab001
```

✅ **ผลลัพธ์ที่คาดหวัง:** เหลือเฉพาะหัวตาราง ไม่มีแถวคอนเทนเนอร์

---

## Reference solution ท้ายบท

`python/learn_db.py` รวม overview, route map, rollback และ persistence สำหรับทบทวนหลังทำไฟล์สั้นครบแล้ว ไม่ใช่ flow หลักของผู้เรียน

## หลักฐานที่ต้องอธิบายได้

- Python เชื่อม `skillspace` ผ่าน `localhost:5432` จากเครื่องปฏิบัติการ
- `information_schema` ยืนยันห้าตารางและ counts เท่ากับ 12, 8, 3, 6, 6
- `GET /api/tickets?status=ASSIGNED` สัมพันธ์กับ SQL template, params `('ASSIGNED',)` และ rows id 4/5
- rollback ให้ผล `8 → 9 → 8`; commit ทำให้ข้อมูลคงอยู่จน cleanup
- `UNIQUE` constraint ปฏิเสธ asset code ซ้ำและ transaction ต้อง rollback
- marker หายเมื่อไม่มี Volume แต่คงอยู่เมื่อ mount `ops-pgdata`
