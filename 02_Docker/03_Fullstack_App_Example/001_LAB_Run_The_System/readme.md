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

📝 **คำอธิบาย:** สร้าง `python/02_query.py` ด้วยโค้ดด้านล่าง โปรแกรมอ่านรายชื่อตารางและ metadata จาก `information_schema` แล้วแสดงจำนวนแถว ชื่อและชนิดคอลัมน์ และข้อมูลจริงไม่เกินสามแถวต่อหนึ่งตาราง `dict_row` ทำให้เข้าถึงค่าด้วยชื่อคอลัมน์ ส่วนชื่อตารางใช้ allowlist และ `sql.Identifier` แทนการต่อ input ลง SQL โดยตรง

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
    cur.execute(sample_query, (3,))
    samples = cur.fetchall()
    print(f"\n=== {table} ({count} rows) ===")
    print("columns: " + " | ".join(
        f"{column['column_name']}:{column['data_type']}" for column in columns
    ))
    for index, row in enumerate(samples, start=1):
        print(f"sample[{index}]: " + json.dumps(
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

✅ **ผลลัพธ์ที่คาดหวัง:** แสดงตารางทั้งห้า แต่ละหัวข้อมี `columns:` และข้อมูล `sample[1]` ถึง `sample[3]` โดยจำนวนแถวคือ `assets=12`, `tickets=8`, `loans=3`, `parts=6` และ `stock_moves=6`

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
