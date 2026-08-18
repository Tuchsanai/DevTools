# Full-stack Gateway + Broker — ChongJai Café

ชุดแล็บ 5 ตอนที่นำระบบสั่งกาแฟของ **ChongJai Café** จาก URL เดียว ไปสู่การ scale API,
คิวชง RabbitMQ, ประวัติเหตุการณ์และแนวโน้มยอดขายด้วย Kafka แล้วปิดท้ายด้วย canary release
ผู้เรียนจะเห็น request และ order เดียวกันไหลผ่านของจริงทุกชั้น ไม่ใช่ตัวอย่างแยกส่วน

> วงจรของชุดนี้: **อ่านโจทย์ธุรกิจ → ทายผล → รัน → ดูหลักฐาน → อธิบายข้อจำกัด**

## ผลลัพธ์การเรียนรู้

เมื่อจบชุดนี้ ผู้เรียนควรทำได้ว่า:

- อธิบายเส้นทาง `browser → Next.js → Traefik → FastAPI` และพิสูจน์ว่า backend ไม่เปิด host port
- scale API, อ่าน `X-Served-By`, ถอน replica ที่ health ไม่ผ่าน และวาง basicAuth/rateLimit ที่ gateway
- อธิบาย RabbitMQ manual ack, redelivery และขอบเขต **at-least-once**
- bootstrap Kafka topic, อ่าน key/partition/group/lag และ replay ด้วย audit group แบบ read-only
- วัด canary 90/10, hot reload น้ำหนัก และตรวจ end-to-end ถึง analytics

## REQ → แล็บเจ้าของ

| REQ | สิ่งที่ต้องพิสูจน์ | แล็บเจ้าของ |
|---|---|---|
| REQ-01 | หน้าเว็บและ server action เข้า API ผ่าน Traefik `:8000`; API/DB ไม่ publish | LAB 1 |
| REQ-02 | order หนึ่งเมนู, `qty` 1–3, สำเร็จเป็น `201/QUEUED`; invalid เป็น `404/422` | LAB 1 |
| REQ-03 | persistent message, manual ack หลัง `READY`, requeue เมื่อ worker หยุดก่อน ack | LAB 3 |
| REQ-04 | scale API 1→3 และถอน/คืน replica ด้วย active health check | LAB 2 |
| REQ-05 | analytics นับเฉพาะ `ORDER_PLACED` และมียอดครบ 6 เมนู | LAB 4 |
| REQ-06 | audit group อ่านย้อนหลังจาก earliest โดยไม่เปลี่ยนฐานข้อมูล | LAB 4 |
| REQ-07 | v1:v2 = 9:1; 200 requests พบ v2 10–30 ครั้ง ติดต่อกัน 3 clean runs | LAB 5 |
| REQ-08 | `/dashboard` และ `/api/report` เป็น `401 → 200` ด้วยบัญชีผู้จัดการของแล็บ | LAB 2 |
| REQ-09 | rateLimit กระทบ `/api/orders` แต่ไม่ลามไป menu/queue | LAB 2 |
| REQ-10 | endpoint, schema, error และ application headers ตรง contract | LAB 1 + LAB 5 |

รายละเอียดเกณฑ์เต็มและ NFR อยู่ที่ [`docs/01_requirements.md`](./docs/01_requirements.md)
ส่วนชื่อ/ค่า canonical ทั้งหมดอยู่ที่ [`docs/02_contract.md`](./docs/02_contract.md)

## เส้นทางแล็บ — ทำเรียง LAB 1 → 5

เวลารันจริงด้านล่างวัดเมื่อ 17 ส.ค. 2026 ด้วย `tools/run_readme.sh` ในกล่อง
`tuchsanai/devtools:2569_1` กล่องเดียว มี cleanup คั่นทุกแล็บ; เป็นเวลา automation รวม cold pull
บาง image ไม่ใช่เวลาอ่านและทดลองของผู้เรียน

| LAB | การทดลอง | เวลาเรียนโดยประมาณ | เวลารันจริง | โฟลเดอร์ | คำถามหลัก |
|---|---:|---:|---:|---|---|
| 1 | 7 | 40 นาที | 2:38 | [`001_LAB_Gateway_Front_Door`](./001_LAB_Gateway_Front_Door/readme.md) | URL เดียวส่งเว็บ/API ถูก service อย่างไร |
| 2 | 8 | 50 นาที | 1:16 | [`002_LAB_Scale_Rush_Hour`](./002_LAB_Scale_Rush_Hour/readme.md) | เพิ่ม API, ถอนตัวป่วย และวาง policy โดยไม่เปลี่ยน URL อย่างไร |
| 3 | 7 | 55 นาที | 3:36 | [`003_LAB_Order_Queue_RabbitMQ`](./003_LAB_Order_Queue_RabbitMQ/readme.md) | ทำอย่างไรไม่ให้งานออกจากคิวก่อนชงเสร็จ |
| 4 | 8 | 55 นาที | 5:17 | [`004_LAB_Sales_Analytics_Kafka`](./004_LAB_Sales_Analytics_Kafka/readme.md) | event เดียวกันทำ analytics และ replay ได้อย่างไร |
| 5 | 8 | 50 นาที | 2:35 | [`005_LAB_Canary_Release_Capstone`](./005_LAB_Canary_Release_Capstone/readme.md) | ปล่อย v2 ทีละน้อยแล้วพิสูจน์ทั้งระบบอย่างไร |

รวมเวลาเรียนประมาณ **4 ชั่วโมง 10 นาที** · 38 การทดลอง · automation จริง **15:22 นาที**

## Prerequisite และดัชนีกันเรียนซ้ำ

ควรรู้ Docker image/container, port mapping, volume, network, Dockerfile และ Compose มาก่อน
หัวข้อต่อไปนี้เป็นพื้นฐานที่ชุดนี้นำมาใช้กับ business flow จึงไม่ย้อนสอนเต็มอีกครั้ง:

| หัวข้อที่เรียนมาแล้ว | ชุดเจ้าของ | ชุดนี้นำมาใช้ที่ |
|---|---|---|
| Compose, network DNS, healthcheck, named volume, `down` เทียบ `down -v` | [CampusOps](../../02_Docker/03_Fullstack_App_Example/readme.md) | sanity/cleanup ทุก LAB |
| PathPrefix, priority, load balancing, active health, basicAuth, rateLimit, weighted canary | [Traefik Reverse Proxy · Gateway · LB](../01_Traefik_Reverse_Proxy_Gateway_LB/readme.md) | LAB 1, 2, 5 |
| durable queue, persistent message, `prefetch=1`, manual ack และ requeue | [RabbitMQ — Message Queue](../02_Message_Brokers/01_RabbitMQ/readme.md) | LAB 3 |
| partition key, consumer group, lag, pub/sub และ replay | [Apache Kafka — Event Streaming](../02_Message_Brokers/02_Kafka/readme.md) | LAB 4 |

สิ่งใหม่ของชุดนี้คือการประกอบหัวข้อเหล่านั้นเป็นเส้นทางเดียวของร้านกาแฟ พร้อม contract และ acceptance
ที่ย้อนกลับไปหา [`docs/00_story.md`](./docs/00_story.md) ได้

## เตรียมเครื่องเรียนครั้งเดียว

รันบนเครื่องของเราเพื่อเปิดกล่อง Docker-in-Docker ที่ SSH port `2222`:

<!-- skip-auto คำสั่งบน host สำหรับสร้างกล่องเรียนภายนอก runner -->
```bash
docker start devtools-cafe 2>/dev/null || \
  docker run -dit --name devtools-cafe --privileged \
  -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222
# password: passwd
```

`--privileged` ใช้เฉพาะ disposable classroom container เพื่อรัน Docker ซ้อน ไม่ใช่ค่า production
บัญชีทั้งหมดในชุดเป็นบัญชีสอน ไม่มีข้อมูลจริงและไม่ต้องใช้ token จริง

จากนั้น clone ภายในกล่อง:

<!-- skip-auto ต้องใช้ network และตำแหน่ง clone ของผู้เรียน -->
```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Application_Docker/04_Fullstack_Gateway_Broker_App
```

ทุกแล็บใช้พอร์ตภายในกล่องชุดเดียวกัน จึงต้อง cleanup ท้ายแล็บก่อนขึ้นตอนถัดไป
เปิด terminal อีกหน้าบน host แล้วทำ SSH port forwarding เมื่อต้องดูเว็บ/UI:

<!-- skip-auto tunnel ต้องรันบน host และค้าง foreground ระหว่างเปิดเว็บ -->
```bash
ssh -N -p 2222 \
  -L 8000:127.0.0.1:8000 \
  -L 8080:127.0.0.1:8080 \
  -L 15672:127.0.0.1:15672 \
  -L 8085:127.0.0.1:8085 root@127.0.0.1
```

| พอร์ต | ใช้ดู | เริ่มมีใน |
|---:|---|---|
| 8000 | เว็บร้านและ `/api` ผ่าน Traefik | ทุก LAB |
| 8080 | Traefik dashboard สำหรับแล็บ | ทุก LAB |
| 15672 | RabbitMQ Management | LAB 3–5 |
| 8085 | Kafka UI | LAB 4–5 |

## แล็บและไฟล์สำคัญ

| ส่วน | ไฟล์สำคัญ |
|---|---|
| LAB 1 | [`docker-compose.yml`](./001_LAB_Gateway_Front_Door/docker-compose.yml) · [`verify.sh`](./001_LAB_Gateway_Front_Door/verify.sh) |
| LAB 2 | [`docker-compose.yml`](./002_LAB_Scale_Rush_Hour/docker-compose.yml) · [`verify.sh`](./002_LAB_Scale_Rush_Hour/verify.sh) |
| LAB 3 | [`docker-compose.yml`](./003_LAB_Order_Queue_RabbitMQ/docker-compose.yml) · [`worker.py`](./003_LAB_Order_Queue_RabbitMQ/worker/worker.py) · [`verify.sh`](./003_LAB_Order_Queue_RabbitMQ/verify.sh) |
| LAB 4 | [`docker-compose.yml`](./004_LAB_Sales_Analytics_Kafka/docker-compose.yml) · [`analytics.py`](./004_LAB_Sales_Analytics_Kafka/analytics/analytics.py) · [`audit.py`](./004_LAB_Sales_Analytics_Kafka/analytics/audit.py) · [`verify.sh`](./004_LAB_Sales_Analytics_Kafka/verify.sh) |
| LAB 5 | [`docker-compose.yml`](./005_LAB_Canary_Release_Capstone/docker-compose.yml) · [`dynamic/routes.yml`](./005_LAB_Canary_Release_Capstone/dynamic/routes.yml) · [`check.sh`](./005_LAB_Canary_Release_Capstone/check.sh) |
| ระบบอ้างอิง | [`app/compose.yaml`](./app/compose.yaml) · [`app/smoke.sh`](./app/smoke.sh) |
| เอกสาร/เครื่องมือ | [`docs/`](./docs/) · [`tools/run_readme.sh`](./tools/run_readme.sh) · [`สไลด์`](./Fullstack_Gateway_Broker_Slides.html) |

## เวอร์ชันที่ใช้

Container images pin เป็น `traefik:v3.7.4`, `postgres:17-alpine`,
`rabbitmq:4.3.4-management`, `apache/kafka:4.1.0`, `kafbat/kafka-ui:v1.5.0`,
`python:3.12-slim` และ `node:22-alpine` ส่วนไลบรารีหลัก pin FastAPI `0.121.2`,
Pika `1.3.2`, kafka-python `3.0.10`, Next.js `16.3.1` และ React `19.2.8`

> ⚠️ **คำเตือน Traefik:** ชุดนี้คง `v3.7.4` เพื่อให้ผลตรงกับแล็บต้นทาง แต่รุ่นนี้อยู่ในช่วงที่
> ได้รับผลกระทบจาก advisory เรื่อง underscore-header spoofing (CVE-2026-54763; แก้ใน `v3.7.6`)
> และรายการนี้ไม่จำเป็นต้องครบทุก advisory ใช้เฉพาะกล่องเรียนที่แยกไว้เท่านั้น งานจริงให้ตรวจ
> [Traefik security advisories](https://github.com/traefik/traefik/security/advisories) และใช้รุ่นที่ patch แล้ว

## ตรวจงาน

ทำการทดลองตาม README ของแต่ละ LAB ก่อน แล้วรันตัวตรวจในโฟลเดอร์นั้น:

<!-- skip-auto รันทีละคำสั่งหลังทำการทดลองของแล็บนั้นและก่อน cleanup -->
```bash
cd 001_LAB_Gateway_Front_Door && bash verify.sh
cd ../002_LAB_Scale_Rush_Hour && bash verify.sh
cd ../003_LAB_Order_Queue_RabbitMQ && bash verify.sh
cd ../004_LAB_Sales_Analytics_Kafka && bash verify.sh
cd ../005_LAB_Canary_Release_Capstone && bash check.sh
```

LAB 1–4 ต้องจบด้วย `ALL CHECKS PASSED` จาก `verify.sh`; LAB 5 ใช้ `check.sh` ตรวจ readiness,
API/header parity, canary 3 clean runs, end-to-end และ cleanup โดยทุกคำสั่งต้องคืน exit code `0`

## เก็บกวาด

ภายในกล่องเรียน รันจาก root ของชุดเพื่อลบ state ของทั้งห้า project แบบระบุเป้าหมายชัดเจน:

<!-- skip-auto down -v จะลบข้อมูลแล็บทั้งหมดใน named volumes ที่ระบุ -->
```bash
for lab in \
  001_LAB_Gateway_Front_Door \
  002_LAB_Scale_Rush_Hour \
  003_LAB_Order_Queue_RabbitMQ \
  004_LAB_Sales_Analytics_Kafka \
  005_LAB_Canary_Release_Capstone; do
  docker compose -f "$lab/docker-compose.yml" down -v --remove-orphans
done
```

บน host เลือกเก็บกล่องไว้ใช้ต่อด้วย `docker stop devtools-cafe` หรือลบกล่องเรียนที่ระบุชื่อนี้ด้วย
`docker rm -f devtools-cafe`

## ขอบเขตการรับประกัน

- RabbitMQ manual ack ให้ขอบเขต **at-least-once**: งานที่ยังไม่ ack กลับเข้าคิวได้ แต่จังหวะผิดพลาดอาจชงซ้ำ
- ไม่มี outbox หรือ publisher confirm จึงไม่รับประกัน zero-loss ระหว่างฐานข้อมูลกับ broker
- analytics ใช้ auto-commit และ `UPDATE` สะสม จึงอาจนับซ้ำเมื่อมี failure; รายงานเป็น **trend-level** ไม่ใช่ยอดปิดบัญชี
- replay เห็นเฉพาะ event ที่ยังอยู่ใน Kafka retention และ audit เป็น read-only one-shot
- ชุดนี้ไม่อ้าง HA ทั้งระบบ, capacity benchmark, exactly-once หรือ production security baseline
