# สัญญาภายในระบบ (Contract)

> เอกสารสำหรับผู้สอน/ผู้ดูแลชุดแล็บ · ผู้เรียนไม่ต้องอ่านหน้านี้ก็ทำแล็บได้
> ทุกไฟล์ใน `app/` ต้องตรงกับหน้านี้เป๊ะ · แก้ที่นี่ที่เดียวแล้วค่อยแก้โค้ด

## 1. สามกล่องและพอร์ตภายใน

| service | image ที่ build | พอร์ตในกล่อง | เข้าถึงจากภายนอก |
|---|---|---|---|
| `web` | Next.js 16.3.1 standalone | 3000 | ✅ (ตามพอร์ตของแต่ละแล็บ) |
| `api` | FastAPI + uvicorn | 8000 | เฉพาะ LAB 2 (สาธิต `/docs`) |
| `db` | `postgres:17-alpine` | 5432 | ❌ ไม่เคย publish (NFR-3) |

**ทิศทางการเรียก:** browser → `web` → (Docker network) → `api` → `db`
`web` เป็น **server-rendered ทั้งหมด** ทุกการกดปุ่มคือ form POST ที่ประมวลผลฝั่ง server
→ browser ไม่เคยเรียก `api` ตรง ๆ จึงไม่ต้องเปิดพอร์ต `api` และไม่มีเรื่อง CORS

## 2. ตัวแปรสภาพแวดล้อม

| ชื่อ | ใช้ที่ | ค่าตัวอย่าง |
|---|---|---|
| `POSTGRES_DB` / `POSTGRES_USER` / `POSTGRES_PASSWORD` | db | `campusops` / `opsuser` / `labpass` |
| `DATABASE_URL` | api | `postgresql://opsuser:labpass@db:5432/campusops` |
| `API_BASE_URL` | web (server-side) | `http://api:8000` |
| `NEXT_PUBLIC_SITE_NAME` | web (ฝังตอน build) | `CampusOps` |

## 3. ตาราง (`db/initdb/01-schema.sql`)

```sql
assets(id, code UNIQUE, name, location, created_at)
tickets(id, asset_id→assets, title, detail, priority CHECK IN (LOW,NORMAL,HIGH),
        status CHECK IN (NEW,ASSIGNED,IN_PROGRESS,DONE) DEFAULT 'NEW',
        assignee NULL, created_at, closed_at NULL)
loans(id, asset_id→assets, borrower, borrowed_at, returned_at NULL)
parts(id, sku UNIQUE, name, qty_on_hand CHECK (qty_on_hand >= 0), reorder_point)
stock_moves(id, part_id→parts, ticket_id→tickets NULL, delta, reason, created_at)
```

**SLA ตามความเร่งด่วน** (ใช้คำนวณ `overdue` ของ REQ-09) : `HIGH` = 1 วัน · `NORMAL` = 3 วัน · `LOW` = 7 วัน

**สถานะครุภัณฑ์เป็นค่าที่คำนวณ ไม่ใช่คอลัมน์** : มี ticket ที่ยังไม่ `DONE` → `IN_REPAIR` ·
มี loan ที่ยังไม่คืน → `ON_LOAN` · นอกนั้น `AVAILABLE`

**seed** : ครุภัณฑ์ 12 ชิ้น · ใบแจ้งซ่อม 8 ใบ (คละสถานะ มีค้างเกินกำหนด 2 ใบ) · สัญญายืม 3 รายการ (ยังไม่คืน 2) ·
อะไหล่ 6 รายการ (ต่ำกว่าจุดสั่งซื้อ 2)

## 4. HTTP API

| method + path | body | ผลสำเร็จ | ผลผิดพลาด |
|---|---|---|---|
| `GET /health` | — | `{"status":"ok","db":"up"}` | `503` ถ้า db ไม่ตอบ |
| `GET /api/assets` | — | `200` list (มี `status` ที่คำนวณแล้ว) | |
| `GET /api/tickets?status=&assignee=` | — | `200` list | |
| `POST /api/tickets` | `{asset_id,title,detail,priority}` | `201` ticket สถานะ `NEW` | `422 VALIDATION_ERROR` |
| `PATCH /api/tickets/{id}/status` | `{status,assignee?}` | `200` ticket | `409 INVALID_TRANSITION` · `400 ASSIGNEE_REQUIRED` · `404 NOT_FOUND` |
| `POST /api/tickets/{id}/close` | `{parts:[{part_id,qty}]}` (ว่างได้) | `200` ticket `DONE` + ตัดสต็อก | `409 INVALID_TRANSITION` · `409 INSUFFICIENT_STOCK` |
| `GET /api/loans` | — | `200` list | |
| `POST /api/loans` | `{asset_id,borrower}` | `201` loan | `409 ASSET_ON_LOAN` · `409 ASSET_IN_REPAIR` |
| `POST /api/loans/{id}/return` | — | `200` loan | `404 NOT_FOUND` |
| `GET /api/parts` | — | `200` list (มี `below_reorder` bool) | |
| `GET /api/parts/{id}/moves` | — | `200` list เรียงเวลาใหม่→เก่า | |
| `POST /api/parts/{id}/move` | `{delta,reason}` | `200` part | `409 INSUFFICIENT_STOCK` |
| `GET /api/dashboard` | — | `200` (ดูรูปข้างล่าง) | |

**รูปของ `/api/dashboard`**
```json
{"tickets":{"NEW":3,"ASSIGNED":2,"IN_PROGRESS":1,"DONE":2},
 "overdue":[{"id":4,"title":"...","days_open":9,"sla_days":3}],
 "loans_active":2,
 "parts_low":[{"id":2,"sku":"...","name":"...","qty_on_hand":1,"reorder_point":5}]}
```

**รูปของ error ทุกตัว** — `{"detail":"<ข้อความไทย>","code":"<UPPER_SNAKE>"}`
รวมถึง `422` ของ FastAPI ที่ต้องเขียน handler ครอบเอง ไม่งั้น `detail` จะเป็น array

| code | HTTP | เกิดเมื่อ | REQ |
|---|---|---|---|
| `INVALID_TRANSITION` | 409 | ข้ามลำดับสถานะ | REQ-02 |
| `ASSIGNEE_REQUIRED` | 400 | `ASSIGNED` โดยไม่ระบุช่าง | REQ-03 |
| `INSUFFICIENT_STOCK` | 409 | เบิกเกินยอดคงเหลือ | REQ-06 |
| `ASSET_ON_LOAN` | 409 | ยืมของที่ยังไม่ถูกคืน | REQ-10 |
| `ASSET_IN_REPAIR` | 409 | ยืมของที่มีใบซ่อมค้าง | REQ-11 |
| `NOT_FOUND` | 404 | ไม่พบรายการ | — |
| `VALIDATION_ERROR` | 422 | body ผิดรูป | — |

## 5. หน้าเว็บ

| path | แสดงอะไร | REQ |
|---|---|---|
| `/` | สรุป: การ์ดจำนวนตามสถานะ · งานค้างเกินกำหนด · อะไหล่ใกล้หมด · จำนวนที่ถูกยืมอยู่ | REQ-08, REQ-09, REQ-12 |
| `/tickets` | กระดานงาน 4 คอลัมน์ตามสถานะ · ฟอร์มแจ้งซ่อม · ปุ่มเลื่อนสถานะ/มอบหมาย/ปิดงาน · ตัวกรองตามช่าง | REQ-01…REQ-05 |
| `/loans` | รายการยืมที่ยังไม่คืน + ประวัติ · ฟอร์มยืม · ปุ่มคืน | REQ-10, REQ-11 |
| `/parts` | ตารางอะไหล่ + แถบเตือนใกล้หมด · ฟอร์มรับเข้า/เบิก · ประวัติการเคลื่อนไหว | REQ-06, REQ-07, REQ-12 |

ทุกหน้าเป็น server component · ทุกฟอร์มใช้ server action ที่เรียก `API_BASE_URL` ภายใน
`export const dynamic = "force-dynamic"` เพื่อไม่ให้ Next แคชหน้าไว้ตอน build

## 6. เวอร์ชันที่ล็อก (ยืนยันด้วยการรันจริง 17 ส.ค. 2026)

`next@16.3.1` · `react@19.2.8` · `tailwindcss@4` · `node:22-alpine` ·
`fastapi==0.121.2` · `uvicorn[standard]==0.42.0` · `psycopg[binary]==3.2.12` · `pydantic==2.13.4` ·
`python:3.12-slim` · `postgres:17-alpine`
