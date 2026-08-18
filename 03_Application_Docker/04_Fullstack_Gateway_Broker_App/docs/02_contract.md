# สัญญากลางของ ChongJai Café

> **แหล่งความจริงเดียวของ U1–U8** · โค้ด, compose, แล็บ, verify, check และ deck ต้องใช้ชื่อ/ค่าในไฟล์นี้
> เปลี่ยน interface ที่นี่ก่อนเสมอ ห้ามแต่ละ unit ตั้ง endpoint, schema, port, env หรือ version เอง

## 1. Version pins

### Container images

| งาน | image pin |
|---|---|
| Gateway | `traefik:v3.7.4` |
| PostgreSQL | `postgres:17-alpine` |
| RabbitMQ | `rabbitmq:4.3.4-management` |
| Kafka | `apache/kafka:4.1.0` |
| Kafka UI | `kafbat/kafka-ui:v1.5.0` |
| Python build/runtime | `python:3.12-slim` |
| Web build/runtime | `node:22-alpine` |

`kafbat/kafka-ui:v1.5.0` ถูก pin หลัง U1 spike ยืนยันแล้ว (`/actuator/health` = UP และมี `wget` ใน image)
`traefik:v3.7.4` คงไว้ให้ตรงชุดต้นทางแม้มี advisory; ใช้ใน LAB เท่านั้น ไม่ใช่ production baseline

### Application libraries

`fastapi==0.121.2` · `uvicorn[standard]==0.42.0` · `psycopg[binary]==3.2.12` ·
`pydantic==2.13.4` · `pika==1.3.2` · `kafka-python==3.0.10` ·
`next@16.3.1` · `react@19.2.8`

## 2. Domain model และฐานข้อมูล

- หนึ่ง order มี `menu_code` เดียวและ `qty` 1–3
- สถานะเดินหน้า `QUEUED → BREWING → READY`; ไม่มี `PICKED_UP`
- `ready_at` เป็น `NULL` จนเป็น `READY`; ทุกเวลาเก็บเป็น UTC
- โค้ดเมนูเป็น ASCII ตัวพิมพ์เล็ก 6 ค่าเท่านั้นและห้ามเปลี่ยน เพราะเป็น Kafka key
- SQL ในบทเรียนใช้เพียง `CREATE`, `INSERT`, `SELECT`, `UPDATE`; ไม่มี ORM/migration/upsert

### SQL canonical (`db/initdb/01-schema.sql` = ส่วน CREATE · `db/initdb/02-seed.sql` = ส่วน INSERT)

```sql
CREATE TABLE menus (
    code VARCHAR(20) PRIMARY KEY,
    name_th VARCHAR(80) NOT NULL,
    price NUMERIC(10,2) NOT NULL CHECK (price > 0),
    CHECK (code IN ('latte','espresso','americano','mocha','matcha','cocoa'))
);

CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    menu_code VARCHAR(20) NOT NULL REFERENCES menus(code),
    qty INTEGER NOT NULL CHECK (qty BETWEEN 1 AND 3),
    customer_name VARCHAR(80) NOT NULL CHECK (length(trim(customer_name)) BETWEEN 1 AND 80),
    status VARCHAR(10) NOT NULL DEFAULT 'QUEUED'
        CHECK (status IN ('QUEUED','BREWING','READY')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ready_at TIMESTAMPTZ NULL
);

CREATE TABLE sales_stats (
    menu_code VARCHAR(20) PRIMARY KEY REFERENCES menus(code),
    cups INTEGER NOT NULL DEFAULT 0 CHECK (cups >= 0),
    revenue NUMERIC(12,2) NOT NULL DEFAULT 0 CHECK (revenue >= 0)
);

INSERT INTO menus (code, name_th, price) VALUES
('latte',     'ลาเต้',       65.00),
('espresso',  'เอสเปรสโซ',  55.00),
('americano', 'อเมริกาโน',  50.00),
('mocha',     'มอคค่า',      70.00),
('matcha',    'มัทฉะลาเต้',  75.00),
('cocoa',     'โกโก้',       60.00);

INSERT INTO sales_stats (menu_code, cups, revenue) VALUES
('latte',0,0),('espresso',0,0),('americano',0,0),
('mocha',0,0),('matcha',0,0),('cocoa',0,0);
```

Analytics ใช้รูปแบบ `UPDATE sales_stats SET cups=cups+qty, revenue=revenue+price_total WHERE menu_code=...`
เท่านั้น แถวทั้ง 6 ต้องมีจาก initdb ก่อน consumer เริ่ม และ `audit.py` ห้ามเขียน DB

## 3. HTTP API

Base path ภายนอกคือ `http://localhost:8000/api`; web เรียกภายในผ่าน `API_BASE_URL=http://traefik`
ทุก timestamp ใน JSON เป็น RFC 3339 UTC ลงท้าย `Z`; เงินเป็น JSON number ที่มีความหมายสองตำแหน่ง

| method | path | request JSON | success response ตัวอย่าง | application errors | ผู้เรียก |
|---|---|---|---|---|---|
| GET | `/api/ping` | — | `200 {"status":"ok"}` | — | Docker healthcheck |
| GET | `/api/health` | — | `200 {"status":"ok","accepting":true}` | `503 HEALTH_FORCED` | Traefik active health |
| POST | `/api/health/fail` | — | `200 {"status":"fail","accepting":false}` | — | แล็บ ยิงตรง replica IP |
| POST | `/api/health/ok` | — | `200 {"status":"ok","accepting":true}` | — | แล็บ ยิงตรง replica IP |
| GET | `/api/menu` | — | `200 {"items":[{"code":"latte","name_th":"ลาเต้","price":65.00}]}` | — | web/ลูกค้า |
| POST | `/api/orders` | `{"menu_code":"latte","qty":2,"customer_name":"ลูกค้า A"}` | `201` order object ด้านล่าง | `404 MENU_NOT_FOUND`, `422 VALIDATION_ERROR`, `503 BROKER_UNAVAILABLE`, `503 EVENT_PUBLISH_FAILED` | web server action |
| GET | `/api/queue` | — | `200 {"items":[...],"count":1}` | — | web จอคิว/บาริสต้า |
| GET | `/api/orders/{id}` | — | `200` order object | `404 ORDER_NOT_FOUND` | web หน้าสถานะ |
| GET | `/api/report/sales` | — | `200` sales report ด้านล่าง | — | web dashboard หลัง basicAuth |
| GET | `/api/version` | — | `200 {"version":"1","tagline":"ชงใจทุกแก้ว"}` | — | web/banner/canary check |

`GET /api/queue` คืนเฉพาะ `QUEUED` และ `BREWING` เรียง `created_at,id` จากเก่าไปใหม่
`GET /api/orders/{id}` คืนได้ทั้งสามสถานะ; health toggle เก็บแยกใน memory ของแต่ละ replica

### Golden application responses

Menu response (ครบ 6 ค่า):

```json
{"items":[{"code":"latte","name_th":"ลาเต้","price":65.00},{"code":"espresso","name_th":"เอสเปรสโซ","price":55.00},{"code":"americano","name_th":"อเมริกาโน","price":50.00},{"code":"mocha","name_th":"มอคค่า","price":70.00},{"code":"matcha","name_th":"มัทฉะลาเต้","price":75.00},{"code":"cocoa","name_th":"โกโก้","price":60.00}]}
```

Order object:

```json
{"id":101,"menu_code":"latte","menu_name_th":"ลาเต้","qty":2,"customer_name":"ลูกค้า A","status":"QUEUED","price_total":130.00,"created_at":"2026-08-17T12:00:00Z","ready_at":null}
```

Queue response: `{"items":[{"id":101,"menu_code":"latte","menu_name_th":"ลาเต้","qty":2,"customer_name":"ลูกค้า A","status":"QUEUED","price_total":130.00,"created_at":"2026-08-17T12:00:00Z","ready_at":null}],"count":1}`

Sales report ต้องมีครบ 6 items แม้ค่าเป็นศูนย์:

```json
{"items":[{"menu_code":"latte","name_th":"ลาเต้","cups":2,"revenue":130.00},{"menu_code":"espresso","name_th":"เอสเปรสโซ","cups":0,"revenue":0.00},{"menu_code":"americano","name_th":"อเมริกาโน","cups":0,"revenue":0.00},{"menu_code":"mocha","name_th":"มอคค่า","cups":0,"revenue":0.00},{"menu_code":"matcha","name_th":"มัทฉะลาเต้","cups":0,"revenue":0.00},{"menu_code":"cocoa","name_th":"โกโก้","cups":0,"revenue":0.00}],"totals":{"cups":2,"revenue":130.00},"claim":"trend-level"}
```

v2 คืน schema เดียวกับ v1 ทุก endpoint เมนู 6 รายการเดิม และเปลี่ยนเพียง
`tagline="ลองข้อความใหม่กับลูกค้ากลุ่มเล็ก"` กับ header `X-Cafe-Api-Version: 2`

### Error contract

Application error ทุกตัวใช้ `{"detail":"<ข้อความไทย>","code":"<UPPER_SNAKE>"}` รวม FastAPI validation handler
ตัวอย่างจริง: `{"detail":"ไม่พบเมนูรหัส unknown","code":"MENU_NOT_FOUND"}`

| HTTP | code | เมื่อใด |
|---|---|---|
| 404 | `MENU_NOT_FOUND` | `menu_code` ไม่อยู่ใน seed 6 ค่า |
| 404 | `ORDER_NOT_FOUND` | ไม่พบ id |
| 422 | `VALIDATION_ERROR` | JSON ผิดรูป, ชื่อว่าง/ยาวเกิน, qty นอก 1–3 |
| 503 | `HEALTH_FORCED` | replica ถูก toggle fail |
| 503 | `BROKER_UNAVAILABLE` | `ORDER_TRANSPORT=rabbit` แต่ publish ไม่สำเร็จ |
| 503 | `EVENT_PUBLISH_FAILED` | `EVENTS_ENABLED=1` แต่ส่ง event ไม่สำเร็จ |

`401` จาก basicAuth และ `429` จาก rateLimit เป็น gateway error จึงไม่ใช้ JSON body ของ FastAPI
แต่ยังต้องมี header ตามตารางถัดไป; ห้ามอ้างสองสถานะนี้ว่าเป็น application error contract

## 4. Header matrix

ขอบเขตคือ Cafe API ที่ entrypoint web `:8000`; ทุก application response รวม `404/422/503` ต้องมี:

| response source | `X-Served-By` | `X-Cafe-Api-Version` |
|---|---|---|
| API v1 success/error | hostname ของ API replica | `"1"` |
| API v2 success/error | hostname ของ API replica | `"2"` |
| Traefik สร้าง `401/429` ก่อนถึง backend | **ไม่มี header** | **ไม่มี header** |

การ**ไม่มี** header คู่นี้บน `401/429` คือหลักฐานการสอนว่า response ถูกสร้างที่ประตู ไม่ถึงบาริสต้า
(ห้ามใช้ headers middleware เติม `X-Served-By` ที่ gateway — จะทับค่า hostname ของ replica ทุก response ทำให้นับ LB ไม่ได้)
application header ทั้งสองต้องอยู่บน `/api/ping`, health toggle และ unknown `/api/...` (404 จาก FastAPI) ด้วย

## 5. RabbitMQ contract

| รายการ | ค่าคงที่ |
|---|---|
| queue | `order_queue`, `durable=True` |
| encoding | UTF-8 JSON object, 1 message ต่อ 1 order |
| publish | default exchange, routing key `order_queue`, `pika.DeliveryMode.Persistent` |
| consume | manual ack หลัง DB เป็น `READY`; `auto_ack=False`; `prefetch_count=1` |
| payload fields | `order_id` integer, `menu_code` string, `qty` integer, `ts` RFC 3339 UTC |

Golden message (canonical แบบ compact; ลำดับ key นี้ใช้ใน fixture):

```json
{"order_id":101,"menu_code":"latte","qty":2,"ts":"2026-08-17T12:00:00Z"}
```

Worker ทำ idempotent `UPDATE orders ... WHERE id=order_id`: ตั้ง `BREWING`, รอ `BREW_SECONDS*qty`,
ตั้ง `READY`/`ready_at` แล้วจึง ack; redelivery ของ order ที่ `READY` แล้วต้อง ack โดยไม่ชง/เพิ่ม event ซ้ำ

## 6. Kafka event contract

| รายการ | ค่าคงที่ |
|---|---|
| topic | `cafe.events`, 3 partitions, replication factor 1 ใน LAB |
| retention | default 7 วัน; replay รับประกันเพียงข้อมูลที่ยังไม่พ้น retention |
| key | `menu_code.encode('utf-8')` |
| value | UTF-8 compact JSON |
| event types | `ORDER_PLACED`, `ORDER_READY` |
| analytics group | `analytics`, `auto_offset_reset='earliest'`, auto-commit เปิด |
| audit group | `audit`, earliest, `enable_auto_commit=False`, read-only, one-shot |

Golden events:

```json
{"event":"ORDER_PLACED","order_id":101,"menu_code":"latte","qty":2,"price_total":130.00,"ts":"2026-08-17T12:00:00Z"}
{"event":"ORDER_READY","order_id":101,"menu_code":"latte","qty":2,"price_total":130.00,"ts":"2026-08-17T12:00:06Z"}
```

Analytics parse ทั้งคู่แต่ `UPDATE sales_stats` เฉพาะ `ORDER_PLACED`; `ORDER_READY` ใช้สังเกต pipeline เท่านั้น
`audit.py` รันด้วย `docker compose exec analytics python audit.py`, ใช้ `consumer_timeout_ms`, พิมพ์แล้วจบ และไม่แตะ DB

### Key → partition ที่พิสูจน์แล้ว

สูตรเดียวกับ kafka-python: `(murmur2(key_bytes) & 0x7fffffff) % 3`

| key | partition |
|---|---:|
| `mocha` | 0 |
| `matcha` | 1 |
| `cocoa` | 1 |
| `latte` | 2 |
| `espresso` | 2 |
| `americano` | 2 |

ห้ามเปลี่ยนตัวพิมพ์/encoding/รหัสเมนู เพราะ partition จะเปลี่ยน; 6 keys นี้จงใจครอบครบ 3 partitions

## 7. Feature และ environment matrix

| LAB | `ORDER_TRANSPORT` | `EVENTS_ENABLED` | API version | broker ที่ต้องมี |
|---|---|---:|---|---|
| LAB1 | `db-only` | `0` | `1` | ไม่มี; order ค้าง `QUEUED` เป็น teaching hook |
| LAB2 | `db-only` | `0` | `1` | ไม่มี; scale API ได้ 3 replicas |
| LAB3 | `rabbit` | `0` | `1` | RabbitMQ; worker ห้ามต่อ Kafka |
| LAB4 | `rabbit` | `1` | `1` | RabbitMQ + Kafka + analytics |
| LAB5 | `rabbit` | `1` | v1=`1`, v2=`2` | ระบบเต็ม |

เมื่อ `ORDER_TRANSPORT=db-only` API ต้องไม่ import `pika`, ไม่ resolve `rabbit`, ไม่เปิด connection และคืน `201`
เมื่อ `EVENTS_ENABLED=0` API/worker ต้องไม่ import Kafka client, ไม่ resolve `kafka`, ไม่เปิด connection และไม่ส่ง event

| env | canonical value | ใช้ที่ |
|---|---|---|
| `API_BASE_URL` | `http://traefik` | web server-side ทุก request |
| `DATABASE_URL` | `postgresql://student:student123@db:5432/cafedb` | api, worker, analytics |
| `RABBIT_URL` | `amqp://student:student123@rabbit:5672/%2F` | api, worker เมื่อเปิด |
| `KAFKA_BOOTSTRAP` | `kafka:9092` | api, worker, analytics เมื่อเปิด |
| `API_VERSION` | `1` หรือ `2` ตาม matrix | api |
| `BREW_SECONDS` | `3` | worker |
| `POSTGRES_DB` | `cafedb` | db |
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | `student` / `student123` | db |
| `RABBITMQ_DEFAULT_USER` / `RABBITMQ_DEFAULT_PASS` | `student` / `student123` | rabbit |

บัญชี basicAuth สำหรับ LAB เท่านั้น: `manager/manager123`
hash ที่ generate และ verify จริง: `manager:$apr1$d3IFwbOQ$khBdiU.59.9ljExK/4xAw0`
ใน Compose ต้อง escape เป็น `manager:$$apr1$$d3IFwbOQ$$khBdiU.59.9ljExK/4xAw0`

Kafka KRaft ใช้ `CLUSTER_ID=MkU3OEVBNTcwNTJENDM2Qk` คงที่, node `1`,
listeners `PLAINTEXT://:9092,CONTROLLER://:9093`, advertised `PLAINTEXT://kafka:9092`,
controller quorum `1@kafka:9093` และ `KAFKA_AUTO_CREATE_TOPICS_ENABLE=false`

## 8. Router map

entrypoint `web=:80` publish host `8000` · dashboard ใช้ entrypoint อัตโนมัติ `traefik=:8080`
ที่ `--api.insecure=true` สร้างให้ (ห้ามประกาศ entrypoint `:8080` ซ้ำ — bind ชนกัน) publish host `8080:8080`
Docker provider ใช้ `exposedByDefault=false`; file provider watch `dynamic/` ใน LAB5

| ใช้ใน | router name | rule | priority | entrypoint | middleware chain | service | provider |
|---|---|---|---:|---|---|---|---|
| LAB1 | `cafe-api` | `PathPrefix(`/api`)` | 200 | web | — | `api@docker` | docker |
| LAB2–4 | `cafe-orders` | `PathPrefix(`/api/orders`)` | 320 | web | `orders-rate@docker` | `api@docker` | docker |
| LAB2–4 | `cafe-report` | `PathPrefix(`/api/report`)` | 310 | web | `manager-auth@docker` | `api@docker` | docker |
| LAB2–4 | `cafe-api` | `PathPrefix(`/api`)` | 200 | web | — | `api@docker` | docker |
| LAB5 | `cafe-orders` | `PathPrefix(`/api/orders`)` | 320 | web | `orders-rate@docker` | `weighted@file` | docker |
| LAB5 | `cafe-report` | `PathPrefix(`/api/report`)` | 310 | web | `manager-auth@docker` | `weighted@file` | docker |
| LAB5 | `cafe-api` | `PathPrefix(`/api`)` | 200 | web | — | `weighted@file` | docker |
| LAB2–5 | `cafe-web-dashboard` | `PathPrefix(`/dashboard`)` | 300 | web | `manager-auth@docker` | `web@docker` | docker |
| ทุก LAB | `cafe-web` | `PathPrefix(`/`)` | 1 | web | — | `web@docker` | docker |

Traefik dashboard ใช้ `--api.insecure=true` เปิดที่ entrypoint `:8080` แบบเดียวกับชุด Traefik ต้นทาง
(ไม่มี router/basicAuth ครอบ — LAB เท่านั้น มีคำเตือนใน readme) — ห้ามสร้าง router `api@internal` เพิ่ม

หน้า web `/dashboard` ต้องมี router แยก `PathPrefix(`/dashboard`)`, priority `300`, basicAuth แล้วไป `web@docker`
จึงชนะ catch-all; Next.js ต้อง forward `Authorization` เมื่อ server-side fetch `/api/report/sales`

LAB5 file service `weighted@file` อ้าง `api-v1@docker` weight 9 และ `api-v2@docker` weight 1
ทั้งสองใช้ image/code/schema/menu เดียวกัน ต่างเฉพาะ env `API_VERSION` และ tagline

`orders-rate`: `average=2`, `period=1s`, `burst=5`; จงใจจำกัด `/api/orders` เท่านั้น
ดังนั้น `GET /api/orders/{id}` ถูกจำกัดด้วยเพราะใช้ PathPrefix แต่ `/api/queue`, `/api/menu` และหน้าเว็บปกติไม่ถูกจำกัด
limiter เห็น source เป็น web container เพราะ server action เรียก gateway; เป็น demo policy ไม่ใช่ per-customer production limit

Traefik active health ของ API ใช้ path `/api/health`, interval `3s`, timeout `1s`; Docker health ใช้ `/api/ping`

## 9. Service matrix

ทุก healthcheck ใช้ `interval=5s`; ค่า timeout/start/retry ด้านล่างต้องรวมแล้วไม่เกิน ready budget 120s

| service | image/build · listen | healthcheck command | timeout/start_period/retries | healthy dependencies | restart | volume | ready |
|---|---|---|---|---|---|---|---:|
| `traefik` | `traefik:v3.7.4` · 80,8080 | `traefik healthcheck --ping` (ต้องเปิด `--ping=true` ใน static config) | 3s/5s/20 | — | unless-stopped | docker socket RO, LAB5 dynamic RO | 120s |
| `db` | `postgres:17-alpine` · 5432 | `pg_isready -U student -d cafedb` | 3s/10s/20 | — | unless-stopped | `pgdata:/var/lib/postgresql/data`, initdb RO | 120s |
| `rabbit` | `rabbitmq:4.3.4-management` · 5672,15672 | `rabbitmq-diagnostics -q check_running` | 5s/20s/18 | — | unless-stopped | `rabbitdata:/var/lib/rabbitmq` | 120s |
| `kafka` | `apache/kafka:4.1.0` · 9092,9093 | `/opt/kafka/bin/kafka-broker-api-versions.sh --bootstrap-server 127.0.0.1:9092` | 10s/15s/12 | — | unless-stopped | `kafkadata:/var/lib/kafka/data` | 120s |
| `api`/`api-v1`/`api-v2` | Python build · 8000 | `python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/ping')"` | 3s/10s/22 | db; +rabbit เมื่อ rabbit; +kafka เมื่อ events | unless-stopped | — | 120s |
| `worker` | Python build · none | `python -c "from pathlib import Path; assert Path('/tmp/worker.ready').exists()"` | 3s/15s/20 | db+rabbit; +kafka เมื่อ events | unless-stopped | — | 120s |
| `analytics` | Python build · none | `python -c "from pathlib import Path; assert Path('/tmp/analytics.ready').exists()"` | 3s/15s/20 | db+kafka | unless-stopped | — | 120s |
| `web` | Node build · 3000 | `wget -qO- http://127.0.0.1:3000/` | 5s/20s/18 | traefik+API healthy | unless-stopped | — | 120s |
| `kafka-ui` | `kafbat/kafka-ui:v1.5.0` · 8080 | `wget -qO- http://127.0.0.1:8080/actuator/health` | 5s/30s/16 | kafka healthy | unless-stopped | — | 120s |

Python services fail-fast เมื่อ dependency ที่เปิดตาม feature matrix ต่อไม่ได้ แล้ว `restart: unless-stopped` ให้เริ่มใหม่
dependency ทุกตัวในคอลัมน์ healthy ใช้ `depends_on: condition: service_healthy`
ไฟล์ ready ของ worker/analytics สร้างหลังต่อ dependencies และประกาศ consumer สำเร็จ ไม่ใช่ทันทีที่ process เริ่ม
คำสั่ง Kafka ตรวจแล้วว่ามีและ executable ใน `apache/kafka:4.1.0`; U1 ต้องยืนยัน `wget` ใน Kafka UI tag ที่เลือก

## 10. Compose, network, volume และ bootstrap

- project ภายใน: `name: lab001` … `name: lab005`; แล็บหนึ่งไม่พึ่ง state ของอีกแล็บ
- logical network เดียวชื่อ `cafenet`; ทุก service อยู่ network นี้และเรียกกันด้วย service name
- logical named volumes: `pgdata`, `rabbitdata`, `kafkadata`; actual name มี project prefix
- `docker compose down` ลบ container/network แต่คง named volumes; `docker compose down -v` ลบ state ถาวรและ init seed ใหม่รอบหน้า
- Kafka ปิด auto-create; ห้าม producer เป็นผู้สร้าง `cafe.events`
- warm start gate วัดหลัง image พร้อม; cold build รายงานเวลา/ทรัพยากรแต่ไม่เป็น gate

LAB4/5 bootstrap ตามลำดับ: เปิด `kafka` → รอ healthy → สร้าง `cafe.events` แบบ 3 partitions
และ replication factor 1 → ตรวจ `--describe` → เปิด db/rabbit/api/worker/analytics/web/kafka-ui ที่เหลือ

## 11. Published ports

| host port | ปลายทาง | LAB |
|---:|---|---|
| `8000` | Traefik web entrypoint `:80` | ทุก LAB |
| `8080` | Traefik admin/dashboard entrypoint `:8080` | ทุก LAB |
| `15672` | RabbitMQ Management UI | LAB3–5 |
| `8085` | Kafka UI container `:8080` | LAB4–5 |

Rabbit AMQP `5672`, Kafka `9092`, PostgreSQL `5432`, API `8000`, web `3000`, worker และ analytics ห้าม publish

## 12. เวลาและขอบเขตการรับประกัน

เวลาชงจำลอง = `BREW_SECONDS * qty` = 3, 6 หรือ 9 วินาที; acceptance end-to-end ต้อง `READY ≤30s`
เมื่อ worker ตายก่อน ack RabbitMQ ส่งซ้ำได้: นี่คือ **at-least-once**, ไม่ใช่ exactly-once
การ `UPDATE ... WHERE id=...` และตรวจ order ที่ `READY` ทำให้ state transition idempotent แต่ไม่สร้าง zero-loss ระหว่าง DB/broker

ไม่มี outbox และ publisher confirm: failure ผิดจังหวะอาจทิ้งแถว `QUEUED`, ส่งซ้ำ หรือขาด event
Analytics ใช้ auto-commit และสะสมด้วย UPDATE จึงอาจนับซ้ำเมื่อ failure; claim คือ **trend-level**
เฉพาะ fixture ปกติที่ควบคุมและไม่มี failure เท่านั้นที่ cups/revenue ต้อง exact ตาม DoD-06

## 13. README runner tags และ namespace ทดสอบ

ทุก fenced block ภาษา bash ใน readme ต้องมี HTML comment ติดก่อน blockหนึ่งบรรทัด:

- `<!-- run -->` รันตามลำดับและคาด exit 0; เป็น default ที่ต้องเขียนให้เห็นชัด
- `<!-- bg -->` เปิดงาน background และ runner ต้องเก็บ PID/cleanup
- `<!-- expect-fail -->` คาด non-zero; ใช้ `<!-- expect-fail:1 -->` เมื่อล็อก exit code
- `<!-- skip-auto เหตุผล -->` ข้ามได้เฉพาะ interactive/Playwright/tunnel พร้อมเหตุผลจริง

namespace ภายนอกกล่องทดสอบ `devtools-cafe1..5`; verify สร้างของชั่วคราวด้วย prefix `vcafe-`
cleanup ต้องตรวจ container, network และ volume ของ `lab001..lab005`, `devtools-cafe*`, `vcafe-*`
ภาพเว็บทุกภาพต้องมาจาก Playwright capture จริงผ่าน tunnel; ห้าม mock ภาพ UI

## 14. Interface handoff

- U0 produce ไฟล์นี้; U1–U8 consume โดยตรง
- U1 ใช้สิทธิ์ pin `kafbat/kafka-ui:v1.5.0` แล้ว (spike ผ่าน — health UP, wget ใช้ได้)
- U2–U6 ต้องใส่ `sync_manifest.txt` และใช้ check IDs จาก requirements
- U7 ใช้ endpoint/schema/header/claim จากไฟล์นี้และคง 50–60 สไลด์
- U8 ตรวจ consistency ทุกชื่อ/พอร์ต/version และไล่ LAB1→5 โดย cleanup ระหว่างแล็บ
