# RabbitMQ — Message Queue

ชุดเรียนรู้ RabbitMQ แบบลงมือทำด้วย Python เรียงจาก **ทำไมต้องมี Queue** ไปจนถึง
Work Queue, Publish/Subscribe และ Topic Routing ระหว่างทำให้ใช้วงจรนี้เป็นหลัก:

> **ทายผล → รัน → สังเกตหลักฐาน → อธิบายเหตุผล → ทดลองให้พัง → แก้กลับ**

## ผลลัพธ์การเรียนรู้

เมื่อจบชุดนี้ ผู้เรียนควรอธิบายและทดลองให้เห็นได้ว่า:

- Producer, Exchange, Binding, Queue และ Consumer ส่งต่อ message กันอย่างไร
- Work Queue ต่างจาก Publish/Subscribe อย่างไร
- `ack`, `prefetch`, durable queue และ persistent message แก้ความล้มเหลวคนละจุดอย่างไร
- `direct`, `fanout` และ `topic` exchange ควรเลือกใช้เมื่อใด
- เหตุใดระบบแบบ at-least-once ต้องรองรับข้อความซ้ำ และเหตุใด producer ต้องใช้ confirm/`mandatory`
- จะดู Ready, Unacked, Consumers และ Bindings ใน Management UI เพื่อ debug อย่างไร

## เปิดสไลด์

เปิด [`RabbitMQ_Slides.html`](./RabbitMQ_Slides.html) ในเบราว์เซอร์ได้โดยตรง ไม่ต้องใช้ web server
และไม่โหลด CDN:

- `←` / `→` หรือ `Space` — เปลี่ยนสไลด์
- `O` — overview และคลิกเพื่อกระโดดไปสไลด์ที่ต้องการ
- `F` — เต็มจอ
- `?` — ดูปุ่มลัด
- `Ctrl+P` — บันทึกเป็น PDF 16:9

## เตรียมเครื่องเรียนครั้งเดียว

คำสั่งชุดนี้รันบน **เครื่องของผู้เรียน** เพื่อเปิด container `devtools` แบบไม่ลบงานเก่า:

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged \
  -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd
```

> `docker start ... || docker run ...` หมายถึง “มีเครื่องเดิมให้เปิดต่อ; ยังไม่มีจึงค่อยสร้าง”
> ทำให้ clone และ venv จาก LAB ก่อนหน้าไม่หาย ส่วน `--privileged` ใช้เฉพาะ disposable classroom
> container เพื่อรัน Docker-in-Docker ไม่ใช่แนวทาง production

จากนั้นใช้ VS Code **Remote-SSH** ต่อ `root@localhost:2222` แล้วรันคำสั่งที่เหลือ
ข้างในเครื่องเรียน ตรวจว่า Docker พร้อม:

```bash
docker --version
docker info --format 'Docker daemon: {{.ServerVersion}}'
```

✅ ได้เลขเวอร์ชันทั้งสองบรรทัดและไม่มี `Cannot connect to the Docker daemon`

## Clone และเตรียม Python ครั้งเดียว

รันข้างในเครื่องเรียน:

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/test/02_RabbitMQxx

python3 -m venv ~/venv-mq
source ~/venv-mq/bin/activate
python -m pip install -r 001_LAB_RabbitMQ_Setup/requirements.txt
```

ถ้า clone ไว้แล้ว ให้ใช้ `cd ~/labwork/DevTools/test/02_RabbitMQxx` แทนการ clone ซ้ำ
และทุก terminal ใหม่ต้อง `source ~/venv-mq/bin/activate` ก่อนรัน Python

## เปิด Broker สำหรับแต่ละ LAB

คำสั่ง baseline ของ LAB 1, 3 และ 4 รันข้างในเครื่องเรียนจากโฟลเดอร์ชุด LAB:

```bash
docker rm -f rabbit 2>/dev/null || true
docker run -d --name rabbit --hostname rabbit-node1 \
  -p 5672:5672 -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=student \
  -e RABBITMQ_DEFAULT_PASS=student123 \
  rabbitmq:4.3.4-management

until docker exec --user rabbitmq rabbit rabbitmq-diagnostics -q check_running; do sleep 2; done
```

ใช้ `check_running` เพราะ `ping` อาจผ่านตั้งแต่ Erlang runtime ตื่นแต่แอป RabbitMQ ยัง boot ไม่ครบ
และใช้ `--user rabbitmq` เพื่อไม่ให้ CLI แย่งสร้าง Erlang cookie ด้วย owner ผิดคนระหว่างที่ broker กำลังเริ่มทำงาน

LAB 2 จะเพิ่ม named volume `rabbitmq-lab2-data` เพื่อพิสูจน์ทั้ง restart และการลบ/สร้าง
container ใหม่โดยกลับมาใช้ storage เดิม ให้ใช้คำสั่งใน README ของ LAB 2 ซึ่งเป็นแหล่งอ้างอิงหลัก
ของการทดลองนั้น

เวอร์ชัน image ถูก pin เพื่อให้ผลในห้องเรียนทำซ้ำได้ ส่วน `student/student123`, port ที่เปิดโล่ง
และบัญชี administrator เป็นค่า **สำหรับ LAB เท่านั้น** งานจริงต้องใช้ secret, TLS และสิทธิ์เท่าที่จำเป็น

เปิด Management UI ด้วยแท็บ **PORTS** ของ VS Code: forward `15672` แล้วไปที่
`http://localhost:15672` (user `student`, password `student123`)

## เส้นทาง LAB

| LAB | เวลาโดยประมาณ | โฟลเดอร์ | คำถามที่ทดลองตอบ |
|---|---:|---|---|
| **1** | 35 นาที | [`001_LAB_RabbitMQ_Setup`](./001_LAB_RabbitMQ_Setup) | ส่งก่อนมีผู้รับได้หรือไม่ และ message รออยู่ตรงไหน |
| **2** | 55 นาที | [`002_LAB_Work_Queue`](./002_LAB_Work_Queue) | หลาย worker แบ่งงานอย่างไร และ durable message รอด restart/recreate บน storage เดิมหรือไม่ |
| **3** | 35 นาที | [`003_LAB_Publish_Subscribe`](./003_LAB_Publish_Subscribe) | ประกาศครั้งเดียวให้หลาย subscriber ได้อย่างไร; temporary กับ durable subscription ต่างกันอย่างไร |
| **4** | 55 นาที | [`004_LAB_Topic_Routing`](./004_LAB_Topic_Routing) | จะคัดข้อความด้วย key/wildcard และตรวจ message ที่ route ไม่ถึง queue อย่างไร |

ทุก LAB มี Expected output, จุดสังเกตใน CLI/UI, แบบทดลองเพิ่มเติม, Troubleshooting,
Cleanup และ Checklist; ขั้นตอนที่ใช้หลาย terminal จะระบุหน้าที่ของแต่ละจอไว้ใกล้คำสั่ง
ควรทำตามลำดับ LAB 1 → 4

## ขอบเขตของสิ่งที่ LAB พิสูจน์

- Manual ack ให้พฤติกรรมแบบ **at-least-once**: ข้อความไม่ถูกลบก่อนเสร็จ แต่อาจส่งซ้ำได้
- durable + persistent + named volume ใน LAB 2 พิสูจน์การรอดจาก restart และ recreate
  เมื่อ broker กลับมาใช้ storage เดิม แต่ไม่ได้พิสูจน์ zero-loss หรือความทนทานต่อ disk/node failure
- Publisher confirm ยืนยันว่า broker รับผิดชอบ message แล้ว และ `mandatory=True` ช่วยตรวจ message ที่ route ไม่ถึง queue
- ระบบ production ยังต้องมี volume/replication, retry จำกัด + DLQ, idempotency, monitoring,
  reconnect, TLS และ secret management ซึ่งสไลด์มี “Production bridge” สรุปไว้

## ตรวจไฟล์หลังแก้ไข

จากโฟลเดอร์นี้:

```bash
python3 scripts/check_materials.py
```

สคริปต์นี้เป็น **static check**: ตรวจโครงสร้าง HTML, จำนวนสไลด์/ภาพฝัง, ลิงก์ไฟล์ภายใน,
โครงสร้าง LAB, syntax ของ Python และป้องกัน image tag/คำสั่ง/path ที่เคยทำให้ LAB ใช้งานไม่ได้
โดยไม่เปิด Docker หรือเชื่อมต่อ RabbitMQ

## Cleanup

จบแต่ละ LAB ให้เก็บกวาดเฉพาะทรัพยากรของ LAB ด้านในเครื่องเรียน คำสั่งพื้นฐานคือ:

```bash
docker rm -f rabbit
docker ps -a --filter name=^/rabbit$
```

LAB 2 มี named volume สำหรับการทดลองโดยเฉพาะ หลังจบและไม่ต้องการข้อมูลแล้วให้ลบตาม
ขั้นตอน Cleanup ของ LAB 2 ด้วย `docker volume rm rabbitmq-lab2-data`

ถ้า forward Management UI ผ่าน VS Code ไว้ ให้กด **Stop Forwarding Port** ที่ port `15672`
ด้วย

อย่าลบ `devtools` ระหว่าง LAB เพราะ clone และ venv อยู่ในนั้น หากต้องการ reset เครื่องเรียนจริง ๆ
ให้คัดลอกงานออกมาก่อน แล้วจึงลบจากเครื่องของผู้เรียนด้วย `docker rm -f devtools`
