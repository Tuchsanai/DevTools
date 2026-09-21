# Apache Kafka — Event Streaming

Software Development Tools and Environments

Apache Kafka is an open-source event streaming platform: programs append events to
topics stored as durable logs, and any number of consumer groups read the same
stream at their own pace — replayable history, not just a queue.
It is the backbone of data pipelines at LinkedIn, Netflix, Uber and countless others.

---

## สไลด์

เปิดไฟล์ [`Kafka_Slides.html`](./Kafka_Slides.html) ในเบราว์เซอร์
(ไฟล์เดียวจบ ไม่ต้องติดตั้งอะไร · กด `O` ดูสไลด์ทั้งหมด · `Ctrl+P` บันทึกเป็น PDF)

สไลด์เป็น **ทฤษฎีชุดเดียวที่ครอบคลุมทั้ง 4 แล็บ** (ไม่แยกหัวข้อตามแล็บ) เรียงตามคอนเซ็ปต์ :
ทำไมต้องมี Kafka → Log/offset/retention → Partition และ Key → Consumer Group / rebalance / LAG →
Pub/Sub · Replay · Pipeline → Broker · Compose · Listener · Port → เทียบกับ RabbitMQ และแผนที่แล็บ —
ป้าย `LAB n` มุมขวาบนของแต่ละสไลด์บอกว่าทฤษฎีข้อนั้นไปลงมือจริงในแล็บไหน ·
ผลการรันและภาพหน้าจอในสไลด์ **รันจริง** บนเครื่องเรียน `tuchsanai/devtools:2569_1` ·
รูปอธิบายคอนเซ็ปต์อยู่ใน [`slides_assets/`](./slides_assets) (สร้างไฟล์สไลด์ใหม่ด้วย `python3 slides_assets/build_slides.py`)

## เครื่องสำหรับทำแล็บ

ทำบนเครื่องเราเอง ผ่าน VS Code — **ไม่ใช้ cloud**

```bash
docker rm -f devtools
docker run -dit --name devtools --privileged -p 2222:22 -p 8411:8411 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> 📝 **คำอธิบาย:** บรรทัดแรกลบเครื่องเรียนตัวเดิมทิ้ง (ถ้าเคยสร้างไว้) เพื่อให้เริ่มจากของใหม่เสมอ ·
> บรรทัดที่สองสร้างเครื่องเรียนขึ้นมา โดย `-dit` ทำให้กล่องรันเบื้องหลังและไม่ดับทันที `--privileged`
> ให้สิทธิ์เต็มเพื่อ**รัน Docker ซ้อนอยู่ข้างในกล่อง** (Docker-in-Docker) — Kafka ของเราจะรันเป็น
> container ซ้อนอยู่ข้างในนั้น · `-p 2222:22` ส่ง port 2222 ของเครื่องเรา เข้า port 22 (SSH) ของกล่อง ·
> `-p 8411:8411` เปิดทางให้เบราว์เซอร์เห็น Kafka UI ของแล็บนั้น (เลขเปลี่ยนตามแล็บ : LAB 1 `8411` · LAB 2 `8412` · LAB 3 `8413` · LAB 4 `8414`) ·
> บรรทัดที่สาม ssh เข้าไปทำงานข้างใน — คำสั่ง `docker` ทุกคำสั่งในแล็บ **สั่งข้างในเครื่องเรียน** ไม่ใช่บนเครื่องเราโดยตรง

เข้าไปได้แล้วให้ตรวจก่อนว่า Docker ข้างในพร้อมใช้งาน :

```bash
docker --version
docker compose version
```

✅ **Expected output** — ได้เลขเวอร์ชันทั้งสองบรรทัด (เลขเวอร์ชันอาจต่างจากนี้เล็กน้อยตามรุ่นของ image) :

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

จากนั้นใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บข้างใน
(หน้าเว็บ Kafka UI เปิดได้ที่ `http://localhost:<port ของแล็บ>` โดยตรง ไม่ต้อง forward port)

## แล็บ

| แล็บในสไลด์ | โฟลเดอร์ | หัวข้อ | Port |
|---|---|---|---|
| **LAB 1** | [`001_LAB_Kafka_Setup`](./001_LAB_Kafka_Setup) | รัน broker ด้วย docker · Kafka UI · Hello World (`send.py`/`receive.py`) · อ่านแล้วไม่หาย | 9092 · **8411** |
| **LAB 2** | [`002_LAB_Partitions_Keys`](./002_LAB_Partitions_Keys) | สร้าง topic 3 partitions · ส่งแบบมี/ไม่มี key · ลำดับการันตีต่อ partition | 9092 · **8412** |
| **LAB 3** | [`003_LAB_Consumer_Groups`](./003_LAB_Consumer_Groups) | ทีมช่วยกันอ่าน · rebalance · อ่านค่า LAG · เพดานของ parallelism | 9092 · **8413** |
| **LAB 4** | [`004_LAB_Event_Pipeline`](./004_LAB_Event_Pipeline) | pipeline JSON สามทอด : sensor → processor → alert center · สอง group สอง topic · replay ด้วย group ใหม่ | 9092 · **8414** |

> **เลขโฟลเดอร์ตรงกับเลขแล็บ** (`001`–`004` = LAB 1–4) — ทุกแล็บมี `docker-compose.yml` ของตัวเอง
> เปิด broker `kafka` (image `apache/kafka:4.1.0` — โหมด KRaft ไม่ต้องมี ZooKeeper · ไม่มี user/password ในโหมดแล็บ)
> คู่กับหน้าเว็บ `kafka-ui` (image `kafbat/kafka-ui:latest`) ด้วย `docker compose up -d`
> ทำทีละแล็บ จบแล้ว **`docker compose down -v`** แล้วเริ่มแล็บถัดไปจากของสะอาด ๆ
> port `9092` คือประตูของโปรแกรม (Kafka protocol) · **port ของ Kafka UI ต่างกันทุกแล็บ** (`8411`–`8414`) เลี่ยง `8080`/`80`/`8888`
> และต้องเปิดด้วย `-p <port>:<port>` ตอนสร้างเครื่องเรียน (ดูข้อ 1 ของแต่ละแล็บ)

## Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Application_Docker/02_Message_Brokers/02_Kafka
```

> 📝 **คำอธิบาย:** สั่ง **ข้างในเครื่องเรียน** (หลัง ssh เข้าไปแล้ว) — สร้างโฟลเดอร์ที่ทำงาน `~/labwork`
> แล้วดึงโค้ดของทุกแล็บลงมาครั้งเดียว ใช้ได้ทั้ง LAB 1–4 ไม่ต้อง clone ซ้ำในแต่ละแล็บ
> เสร็จแล้วจะอยู่ในโฟลเดอร์ที่มีโฟลเดอร์ `001_LAB_Kafka_Setup` … `004_LAB_Event_Pipeline` อยู่ข้างใน

## อ่านเอกสารแล็บอย่างไร

เอกสารของทุกแล็บใช้รูปแบบเดียวกัน :

| สัญลักษณ์ | ความหมาย |
|---|---|
| ` ```bash ` | คำสั่งที่ต้อง **พิมพ์เอง** ในเครื่องเรียน |
| 📝 **คำอธิบาย** | คำสั่งนั้นทำอะไร แต่ละ flag แปลว่าอะไร และให้สังเกตอะไร |
| ✅ **Expected output** | ผลลัพธ์ที่ควรได้ **ถ้าทำถูก** — ถ้าได้ไม่ตรง แปลว่าพลาดบางขั้น ให้ย้อนกลับไปดู |

> **ตัวเลขที่ไม่ต้องตรงกันก็ได้** — CONTAINER ID, TopicId, CONSUMER-ID, วันเวลา และ partition
> ของข้อความที่ส่งแบบไม่มี key ของแต่ละคนจะไม่เหมือนในเอกสาร ให้ดูที่ **รูปแบบและสถานะ**
> (เช่น `Up`, `Kafka Server started`, ค่า LAG, จำนวนข้อความรวม) เป็นหลัก ·
> ข้อยกเว้นสนุก ๆ : ค่าอุณหภูมิใน LAB 4 **ตรงกับเอกสารเป๊ะทุกคน** เพราะโค้ดล็อก `random.seed(2569)` ไว้

---

Happy Learning!
