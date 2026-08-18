# จากเรื่องร้านกาแฟ → ข้อกำหนดที่ทดสอบได้

> ต้นน้ำ: [`00_story.md`](./00_story.md) · สัญญาระบบ: [`02_contract.md`](./02_contract.md)
> ทุกข้อมีเกณฑ์วัด แล็บเจ้าของ และ check owner; ไม่มีคำอ้าง HA ทั้งระบบ, zero-loss หรือ exact-count เมื่อมี failure

---

## 1. User stories

| ID | ในฐานะ… ฉันต้องการ… เพื่อ… |
|---|---|
| US-01 | ลูกค้า · สั่งล่วงหน้าผ่าน URL เดียว · ลดเวลายืนต่อแถวช่วงพักเที่ยง |
| US-02 | บาริสต้า · รับงานจากคิวและยืนยันหลังชง · ไม่ทิ้งงานก่อน ack |
| US-03 | เจ้าของร้าน · เพิ่ม/ถอน API replica ระหว่างเปิดร้าน · กระจายคำขอช่วงเร่งด่วน |
| US-04 | เจ้าของร้าน · เห็น cups/revenue แยกเมนูและ replay ได้ใน retention · วางแผนวัตถุดิบจากแนวโน้ม |
| US-05 | เจ้าของร้าน · ส่งแบนเนอร์ v2 ให้ลูกค้าส่วนน้อย · ทดลองก่อนปล่อยเต็ม |
| US-06 | เจ้าของร้าน · ใส่รหัสก่อนดูรายงานและจำกัดการกดออเดอร์รัว · ลดการเข้าถึงที่ไม่ตั้งใจ |

## 2. Functional requirements

| REQ | ข้อกำหนดแบบวัดได้ | เกณฑ์ผ่าน | จาก |
|---|---|---|---|
| REQ-01 | browser และ Next.js server action เรียก API ผ่าน Traefik ที่ `:8000`; API/DB ไม่ publish port | access log พบ request จากการกดเว็บและ `docker compose ps` ไม่มี host mapping ของ API/DB | US-01 |
| REQ-02 | หนึ่งออเดอร์มีเมนู seed 1 ค่า, `qty` 1–3 และชื่อผู้รับ; เมื่อสำเร็จคืน `201` สถานะ `QUEUED` | fixture ที่ถูกต้องสร้างหนึ่งแถว; เมนูไม่พบได้ `404`; qty นอกช่วงได้ `422` | US-01 |
| REQ-03 | เมื่อใช้ RabbitMQ หนึ่งออเดอร์สร้างหนึ่ง persistent message; worker ใช้ manual ack หลัง `READY` และ `prefetch=1` | หยุด worker ก่อน ack แล้วข้อความ requeue; เปิดกลับแล้ว order เดิมถึง `READY` ภายใน 30 วินาที | US-02 |
| REQ-04 | scale API จาก 1 เป็น 3 ได้โดยไม่หยุด Traefik; replica ที่ `/api/health` ตอบ `503` ถูกถอนและใส่กลับเมื่อ `200` | header เห็นอย่างน้อย 2 hostname; hostname ที่ fail ไม่ปรากฏหลัง active check และกลับมาหลัง `/ok` | US-03 |
| REQ-05 | analytics นับเฉพาะ `ORDER_PLACED` แล้ว `UPDATE sales_stats` แยก 6 menu code | fixture ปกติไม่มี failure สั่ง N รายการแล้ว cups/revenue ตรง fixture; คำอ้างธุรกิจคงเป็น trend-level | US-04 |
| REQ-06 | `audit.py` group `audit` อ่าน `cafe.events` ตั้งแต่ earliest แบบ read-only แล้วจบเอง | output มี event เก่าภายใน retention และค่า `sales_stats` ก่อน/หลัง audit เท่ากัน | US-04 |
| REQ-07 | LAB5 ส่ง API v1:v2 ที่ weight 9:1; contract เหมือนกัน ต่างเฉพาะ `tagline` และ version header | 200 requests มี v2 10–30 ครั้ง ติดต่อกัน 3 clean runs; POST fixture ผ่านทั้งสองเวอร์ชัน | US-05 |
| REQ-08 | หน้า `/dashboard` และ API `/api/report` ต้องผ่าน basicAuth บัญชีสอน | ไม่ส่ง credential ได้ `401`; `manager/manager123` ได้ `200` | US-06 |
| REQ-09 | rateLimit ติดเฉพาะ router `PathPrefix(/api/orders)` ที่ `average=2/1s`, `burst=5` | ยิงพร้อมกัน 20 POST พบทั้ง `201` และ `429`; `GET /api/menu` และ `GET /api/queue` ยัง `200` | US-06 |
| REQ-10 | ลูกค้าดูเมนู, คิว, order รายตัว, version และรายงานผ่าน endpoint ที่ contract กำหนด | schema/status/header ของทุก endpoint ตรงตัวอย่างใน contract และ unknown order ได้ `404` | US-01, US-04 |

## 3. Non-functional requirements

| NFR | ข้อกำหนดแบบวัดได้ | เกณฑ์ผ่าน |
|---|---|---|
| NFR-01 | warm start หลัง image พร้อม ทุก service ที่แล็บใช้ต้อง healthy ภายใน 120 วินาที | readiness oracle ใน service matrix ผ่านครบก่อน 120 วินาที |
| NFR-02 | จุดเข้า host มีเฉพาะ `8000`, `8080`, และ UI ของ broker ตามแล็บ; DB/API ไม่ publish | ตรวจ `docker compose ps` และ socket host ไม่พบ `5432`/API `8000` โดยตรง |
| NFR-03 | `down` รักษา named volumes; `down -v` ลบ state เพื่อเริ่มแล็บสะอาด | seed/fixture รอด `down`+`up`; หายและ seed ใหม่หลัง `down -v` |
| NFR-04 | เมื่อ feature flag ปิด API/worker ต้องไม่ import หรือพยายามต่อ broker นั้น | LAB1–2 ไม่มี Rabbit/Kafka แต่ API healthy; LAB3 ไม่มี Kafka แต่ API/worker healthy |
| NFR-05 | ทุก response ที่ออกจาก application ใต้ `/api` รวม application error มีสอง header ตาม contract | success, `404`, `422`, `503` แสดง `X-Served-By` และ `X-Cafe-Api-Version` |
| NFR-06 | ชื่อ project/test/verify และ cleanup อยู่ใน namespace ที่ contract กำหนด | หลัง cleanup ไม่เหลือ container/network/volume กลุ่ม `lab00*`, `devtools-cafe*`, `vcafe-*` |

## 4. Trace: REQ → เทคนิคเดิม → แล็บเจ้าของ

Path ต่อไปนี้ตรวจแล้วว่ามี heading ตามที่อ้าง โดยนับจากราก `DevTools/`:

| ข้อ | เทคนิคเดิม | path + section จริง | แล็บเจ้าของ |
|---|---|---|---|
| REQ-01, REQ-10 | entrypoint, PathPrefix, forwarded headers | `03_Application_Docker/01_Traefik_Reverse_Proxy_Gateway_LB/001_LAB_Traefik_Reverse_Proxy/readme.md` §3 “เพิ่ม Traefik” และ §4 “เรียกผ่าน Proxy” | LAB1 |
| REQ-02 | Compose services/network + DB init scaffold | `02_Docker/02_Dockerfile_Build_Run_Compose_Guide/007_LAB_Compose_Multistage_Capstone/readme.md` §การทดลองที่ 1 และ 3 | LAB1 |
| REQ-04 | scale, load distribution, active health toggle | `03_Application_Docker/01_Traefik_Reverse_Proxy_Gateway_LB/002_LAB_Load_Balancing/readme.md` §2, §3 และ §6 | LAB2 |
| REQ-08, REQ-09 | basicAuth, rateLimit, access log | `03_Application_Docker/01_Traefik_Reverse_Proxy_Gateway_LB/003_LAB_API_Gateway_Middlewares/readme.md` §2, §5, §8 และ §9 | LAB2 |
| REQ-03 | durable/persistent, prefetch, ack/requeue | `03_Application_Docker/02_Message_Brokers/01_RabbitMQ/002_LAB_Work_Queue/readme.md` §6, §7 และ §8 | LAB3 |
| REQ-05 | JSON event pipeline | `03_Application_Docker/02_Message_Brokers/02_Kafka/005_LAB_Event_Pipeline/readme.md` §5–§8 | LAB4 |
| REQ-05 | key เดิมลง partition เดิม | `03_Application_Docker/02_Message_Brokers/02_Kafka/002_LAB_Partitions_Keys/readme.md` §4, §6 และ §7 | LAB4 |
| REQ-05 | consumer group, rebalance, lag | `03_Application_Docker/02_Message_Brokers/02_Kafka/003_LAB_Consumer_Groups/readme.md` §6–§9 | LAB4 |
| REQ-06 | group ใหม่ replay จาก earliest | `03_Application_Docker/02_Message_Brokers/02_Kafka/004_LAB_PubSub_Replay/readme.md` §9 และ §10 | LAB4 |
| REQ-07 | weighted service + file-provider reload | `03_Application_Docker/01_Traefik_Reverse_Proxy_Gateway_LB/004_LAB_Canary_Mirroring/readme.md` §2, §4 และ §5 | LAB5 |
| NFR-01, NFR-03 | healthcheck/depends_on, down เทียบ down -v | `02_Docker/02_Dockerfile_Build_Run_Compose_Guide/007_LAB_Compose_Multistage_Capstone/readme.md` §การทดลองที่ 7, 10 และ 11 | LAB1–5 |
| NFR-02, NFR-04 | user-defined network, backend ไม่ต้อง publish | `02_Docker/02_Dockerfile_Build_Run_Compose_Guide/006_LAB_Network_DNS/readme.md` §การทดลองที่ 4 และ 7 | LAB1–5 |
| NFR-05 | response headers ผ่าน API gateway | `03_Application_Docker/01_Traefik_Reverse_Proxy_Gateway_LB/003_LAB_API_Gateway_Middlewares/readme.md` §6 | LAB1–5 |
| NFR-06 | Compose project/name และ cleanup | `02_Docker/02_Dockerfile_Build_Run_Compose_Guide/007_LAB_Compose_Multistage_Capstone/readme.md` §การทดลองที่ 4 และ §เก็บกวาด | LAB1–5 |

## 5. REQ → check matrix

| ข้อ | check owner | สิ่งที่ check ตัดสิน |
|---|---|---|
| REQ-01 | `LAB1 verify.sh / LAB1-V01` | front door + access log + no API/DB port |
| REQ-02 | `LAB1 verify.sh / LAB1-V02` | valid/invalid order และสถานะเริ่มต้น |
| REQ-03 | `LAB3 verify.sh / LAB3-V01,V02` | message ต่อ order, requeue, READY ≤30s |
| REQ-04 | `LAB2 verify.sh / LAB2-V01,V02` | หลาย hostname และถอน/คืน unhealthy replica |
| REQ-05 | `LAB4 verify.sh / LAB4-V01` | normal fixture cups/revenue และ 6 seed rows |
| REQ-06 | `LAB4 verify.sh / LAB4-V02` | replay output โดย DB hash ไม่เปลี่ยน |
| REQ-07 | `LAB5 check.sh / INT-CANARY-01` | 200 requests, tolerance, 3 clean runs, contract parity |
| REQ-08 | `LAB2 verify.sh / LAB2-V03` | dashboard/report 401→200 |
| REQ-09 | `LAB2 verify.sh / LAB2-V04` | POST มี 429 แต่ menu/queue ไม่ถูกจำกัด |
| REQ-10 | `LAB1 verify.sh / LAB1-V03` + `LAB5 check.sh / INT-API-01` | endpoint/schema/error/header ครบ |
| NFR-01 | `LAB5 check.sh / INT-READY-01` | warm healthy ≤120s |
| NFR-02 | `LAB1 verify.sh / LAB1-V04` | published-port allowlist |
| NFR-03 | `LAB1 verify.sh / LAB1-V05` | down คง state, down -v reset |
| NFR-04 | `LAB1 verify.sh / LAB1-V06` + `LAB3 verify.sh / LAB3-V03` | broker ที่ปิดไม่ถูก import/connect |
| NFR-05 | `LAB5 check.sh / INT-HEADERS-01` | header บน success และ application errors |
| NFR-06 | `LAB5 check.sh / INT-CLEAN-01` | namespace สะอาดหลัง cleanup |

## 6. แผนที่ 5 แล็บ

| แล็บ | ธีม | REQ/NFR หลัก | ผลที่เห็น |
|---|---|---|---|
| LAB1 | ประตูหน้าร้าน | REQ-01,02,10 · NFR-02–05 | กดเว็บแล้ว request ผ่าน Traefik; order ค้าง `QUEUED` โดยตั้งใจ |
| LAB2 | รับศึกพักเที่ยง | REQ-04,08,09 | scale/LB, active health, basicAuth และ rateLimit |
| LAB3 | ออเดอร์เข้าคิว RabbitMQ | REQ-03 · NFR-04 | manual ack/requeue, fair dispatch, durable/persistent |
| LAB4 | แนวโน้มยอดขาย Kafka | REQ-05,06 | key→partition, group analytics, lag และ audit replay |
| LAB5 | Canary capstone | REQ-07 และ integration ทุกข้อ | v1/v2 contract เดียว, 9:1, end-to-end และ cleanup |

## 7. ขอบเขต

ไม่ทำระบบชำระเงิน · ไม่ทำ login ลูกค้า · ไม่ใช้ WebSocket · ไม่ทำ outbox/publisher confirm ·
ไม่อ้าง exactly-once, zero-loss, capacity benchmark หรือ HA ทั้งระบบ · รายงานไม่ใช้ปิดบัญชี
