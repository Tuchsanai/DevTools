# Plane × Agile — เครื่องมือวิศวกรรมซอฟต์แวร์ที่รันเองได้จริง

ชุดการสอนที่ใช้ **Plane** (open-source project management, AGPL-3.0, self-hosted ด้วย Docker) เป็นเครื่องมือลงมือทำ
สำหรับ 4 หัวข้อของวิชา:

| หัวข้อ | สิ่งที่เรียน | พิสูจน์ใน LAB |
|---|---|---|
| **1. หลักการเพื่อเป็นผู้เชี่ยวชาญด้านซอฟต์แวร์** (Principles to Software Professionals) | วิชาชีพ · SWEBOK · จรรยาบรรณ ACM/IEEE-CS · หลักการ SE · การสื่อสาร/traceability | LAB 3 |
| **2. บทบาทของแอปพลิเคชันในงานวิศวกรรมซอฟต์แวร์** (Roles of Applications in SE Tasks) | เครื่องมือตลอด SDLC · single source of truth · กายวิภาคของเว็บแอป 13 container | LAB 1–2 |
| **3. เครื่องมือพัฒนาแบบ Agile** (Scrum & Kanban) | Manifesto · Scrum 3-5-3 · story points · burndown · Kanban · WIP · Little's Law | LAB 4–5 |
| **4. การติดตามการพัฒนาผลิตภัณฑ์** (Jira & Trello) | Jira/Trello concepts · เปรียบเทียบกับ Plane · metrics · dashboards · API/webhooks/import | LAB 6–9 |

ทุก LAB ใช้วงจรเดียวกับชุด RabbitMQ:

> **ทายผล → รัน → สังเกตหลักฐาน → อธิบายเหตุผล → ทดลองให้พัง → แก้กลับ**

## ผลลัพธ์การเรียนรู้

เมื่อจบชุดนี้ ผู้เรียนควรอธิบายและทดลองให้เห็นได้ว่า:

- มืออาชีพด้านซอฟต์แวร์ต่างจาก "คนเขียนโค้ดได้" อย่างไร และจรรยาบรรณ 8 ข้อปรากฏในงานประจำวันบน tracker ตรงไหน
- แอปพลิเคชันจัดการโครงการทำหน้าที่อะไรใน SDLC และเว็บแอปสมัยใหม่ประกอบด้วยส่วนใดบ้าง (proxy · web · api · worker · queue · db · cache · object storage)
- Scrum และ Kanban ต่างกันอย่างไร ทำไม Cycle = Sprint, Module = Epic, State group = คอลัมน์บอร์ด และ burndown คำนวณจากอะไร
- Jira, Trello และ Plane ใช้ศัพท์ต่างกันแต่โมเดลเดียวกันอย่างไร และจะติดตามผลิตภัณฑ์ด้วย metric ใด (velocity · lead/cycle time · CFD)
- จะป้อนข้อมูลเข้า/ออกจากเครื่องมือด้วย REST API, webhook และ CSV ได้อย่างไร แบบ idempotent และมี rate limit

## เปิดสไลด์

เปิด [`Plane_Agile_Slides.html`](./Plane_Agile_Slides.html) ในเบราว์เซอร์ได้โดยตรง ไม่ต้องใช้ web server และไม่โหลด CDN:

- `←` / `→` หรือ `Space` — เปลี่ยนสไลด์ · `#เลข` ท้าย URL กระโดดไปสไลด์นั้น
- `O` — overview และคลิกเพื่อกระโดดไปตอนที่ต้องการ
- `F` — เต็มจอ · `?` — ดูปุ่มลัด · `Ctrl+P` — บันทึกเป็น PDF 16:9

ไดอะแกรมในสไลด์วาดด้วย Excalidraw (ต้นฉบับแก้ได้ที่ `slides_assets/scenes/*.excalidraw`) ภาพประกอบแนวคิดเป็น SVG ใน
`slides_assets/illustrations/` และ **ภาพหน้าจอทุกภาพมาจากการรันจริง** ใน LAB (`00N_LAB_*/images/`)

## เตรียมเครื่องเรียนครั้งเดียว

คำสั่งชุดนี้รันบน **เครื่องของผู้เรียน** เพื่อเปิด container `devtools` แบบไม่ลบงานเก่า:

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged \
  -p 2222:22 -p 8080:8080 -p 9000:9000 -p 8090:8090 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password: passwd
```

> `-p 8080:8080` เปิดทางให้เบราว์เซอร์บนเครื่องเราเห็น Plane ที่รันข้างในเครื่องเรียนโดยตรง ส่วน `-p 9000:9000` / `-p 8090:8090` เผื่อไว้ให้เว็บแอปของเราเองใน LAB 8–9 ·
> **`docker run` ทำงานเฉพาะครั้งแรกที่ยังไม่มี container** — ถ้า `devtools` ถูกสร้างไว้ก่อนแล้ว (เช่น จากชุด RabbitMQ) จะเพิ่ม `-p` ทีหลังไม่ได้ ให้ใช้แท็บ **PORTS** ของ VS Code forward `8080`, `9000`, `8090` แทน · `--privileged` ใช้เฉพาะ disposable classroom container เพื่อรัน Docker-in-Docker ไม่ใช่แนวทาง production ·
> ถ้า `docker run` ฟ้องว่า port `2222` ใช้ไม่ได้ (พบบน Windows/WSL2 บางเครื่อง: *"forbidden by its access permissions"*) ให้เปลี่ยนเป็น
> `-p 2280:22` แล้ว ssh ด้วย `-p 2280` — ดู `netsh interface ipv4 show excludedportrange protocol=tcp`

จากนั้นใช้ VS Code **Remote-SSH** ต่อ `root@localhost:2222` แล้วรันคำสั่งที่เหลือข้างในเครื่องเรียน ตรวจว่า Docker พร้อม:

```bash
docker --version
docker compose version
```

Clone ชุด LAB ไว้ครั้งเดียว:

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Application_Docker/Plane
```

## ติดตั้ง Plane ครั้งเดียว ใช้ต่อทุก LAB

LAB 1 พาทำทีละขั้นพร้อมคำอธิบาย สรุปคำสั่งทั้งหมดคือ (รันข้างในเครื่องเรียน):

```bash
mkdir -p ~/plane-selfhost && cd ~/plane-selfhost
TAG=v1.4.2      # release ที่ชุดนี้ทดสอบ (31 ส.ค. 2026) — ดูรุ่นล่าสุดที่ https://github.com/makeplane/plane/releases
curl -sSL -o docker-compose.yml "https://github.com/makeplane/plane/releases/download/$TAG/docker-compose.yml"
curl -sSL -o plane.env          "https://github.com/makeplane/plane/releases/download/$TAG/variables.env"
sed -i "s|^APP_DOMAIN=.*|APP_DOMAIN=localhost:8080|; s|^APP_RELEASE=.*|APP_RELEASE=$TAG|; \
        s|^LISTEN_HTTP_PORT=.*|LISTEN_HTTP_PORT=8080|; s|^LISTEN_HTTPS_PORT=.*|LISTEN_HTTPS_PORT=8443|; \
        s|^WEB_URL=.*|WEB_URL=http://localhost:8080|; s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost:8080|" plane.env
sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 32)|; s|^LIVE_SERVER_SECRET_KEY=.*|LIVE_SERVER_SECRET_KEY=$(openssl rand -hex 32)|" plane.env
docker compose -f docker-compose.yml --env-file plane.env -p plane up -d
until [ "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/instances/)" = "200" ]; do sleep 5; done; echo READY
```

> `WEB_URL`/`CORS_ALLOWED_ORIGINS` ต้องมี **port เดียวกับที่เบราว์เซอร์ใช้** เพราะ Plane สร้าง redirect หลัง login จากค่านี้ ·
> ครั้งแรกจะ pull image รวม ~4.7 GB · `docker compose ps` ขึ้น `Up` ไม่ได้แปลว่าพร้อม — ให้รอ `/api/instances/` ตอบ `200` (ราว 2 นาที) ·
> บัญชีในเอกสารทั้งหมดเป็น **placeholder สำหรับ LAB**: `admin@example.com` / `Plane-Lab-2569`, `dev1@example.com` / `Member-Lab-2569`, bot `automation@example.com` / `Bot-Lab-2569`,
> workspace `DevTools Lab` (`devtools-lab`), โปรเจกต์ `Plane Lab` (`PLAB`) · งานจริงต้องใช้ secret, TLS และสิทธิ์เท่าที่จำเป็น

เปิด `http://localhost:8080` ในเบราว์เซอร์ → หน้า **Welcome to Plane** → ตั้งค่า instance admin ที่ `/god-mode/` (LAB 1 ข้อ 6)

## เส้นทาง LAB

| LAB | เวลาโดยประมาณ | โฟลเดอร์ | คำถามที่ทดลองตอบ | หัวข้อ |
|---|---:|---|---|---|
| **1** | 45 นาที | [`001_LAB_Plane_Setup`](./001_LAB_Plane_Setup) | ติดตั้งแอป 13 container ด้วยคำสั่งเดียวได้อย่างไร และ "พร้อม" วัดจากอะไร | 2 |
| **2** | 50 นาที | [`002_LAB_Architecture_Tour`](./002_LAB_Architecture_Tour) | request วิ่งผ่าน proxy → api → db/queue อย่างไร และเกิดอะไรเมื่อ worker หยุด | 2 |
| **3** | 50 นาที | [`003_LAB_Professional_Work_Items`](./003_LAB_Professional_Work_Items) | work item ที่มืออาชีพเขียนต่างจากโน้ตสั้น ๆ อย่างไร และเพิ่มเพื่อนร่วมทีมโดยไม่มี SMTP ได้ไหม | 1 |
| **4** | 60 นาที | [`004_LAB_Scrum_Cycles`](./004_LAB_Scrum_Cycles) | Sprint = Cycle ทำงานอย่างไร burndown มาจากไหน และงานที่ไม่เสร็จไปไหน | 3 |
| **5** | 55 นาที | [`005_LAB_Kanban_Flow`](./005_LAB_Kanban_Flow) | บอร์ด swimlane · state ใหม่ · WIP policy · Intake triage และวัด cycle time จาก activity ได้อย่างไร | 3 |
| **6** | 55 นาที | [`006_LAB_Modules_Pages_Analytics`](./006_LAB_Modules_Pages_Analytics) | จะติดตาม roadmap ด้วย Modules, เก็บ PRD ไว้กับงาน, อ่าน Analytics, export CSV และเผยแพร่บอร์ดสาธารณะได้อย่างไร และ CE นำเข้าจาก Jira/Trello ได้ไหม | 4 |
| **7** | 60 นาที | [`007_LAB_REST_API_Import`](./007_LAB_REST_API_Import) | ย้ายบอร์ด Trello/Jira เข้า Plane ด้วย REST API แบบ idempotent ภายใต้ rate limit ได้อย่างไร | 4 |
| **8** | 55 นาที | [`008_LAB_Webhooks_Automation`](./008_LAB_Webhooks_Automation) | Plane แจ้งเหตุการณ์ออกมาอย่างไร ตรวจลายเซ็น HMAC และทำ automation แบบ Butler ได้อย่างไร | 4 |
| **9** | 60 นาที | [`009_LAB_Tracking_Dashboard`](./009_LAB_Tracking_Dashboard) | จะสร้าง dashboard ติดตามผลิตภัณฑ์ (burndown · CFD · velocity · lead time) จากข้อมูลจริงใน Plane ภายใต้ rate limit ได้อย่างไร | 4 |

ทุก LAB มีหัวข้อเดียวกัน: สิ่งที่จะได้เรียนรู้ · ทฤษฎีที่เกี่ยวข้อง · ภาพรวมของแล็บนี้ (พร้อมคำถามก่อนเริ่ม) · ขั้นตอนพร้อม 📝 คำอธิบาย และ ✅ Expected output · ทดลองเพิ่มเติม · แก้ปัญหาที่พบบ่อย · เก็บกวาด (Cleanup) · สรุปคำสั่งของแล็บนี้ · เช็กลิสต์ก่อนจบแล็บ
ควรทำตามลำดับ LAB 1 → 9 เพราะ Plane และข้อมูลใน workspace ถูกใช้ต่อเนื่อง (ลบทั้งหมดตอนจบ LAB 9)

## ขอบเขตของสิ่งที่ LAB พิสูจน์

- ทุกอย่างรันใน classroom container แบบ Docker-in-Docker ด้วย image ทางการ `makeplane/plane-*:v1.4.2` — ไม่ใช่การตั้งค่าสำหรับ production
  (ไม่มี TLS, secret เป็นค่า LAB, ไม่มี SMTP, ไม่มี backup อัตโนมัติ)
- Plane Community Edition **ไม่มี** WIP limit, workflow rule, bulk edit, velocity chart และ importer — LAB จะเขียนสคริปต์ทดแทนผ่าน REST API
  เพื่อให้เห็นว่า "เครื่องมือขาดอะไร วิศวกรเติมเองได้อย่างไร"
- ข้อมูลตัวเลขในเอกสาร (เวลาบูต, จำนวน queue, ค่า metric) มาจากการรันจริงในวันที่ระบุ ของแต่ละคนอาจต่างกันเล็กน้อย

## ตรวจไฟล์หลังแก้ไข

```bash
python3 scripts/check_materials.py
```

สคริปต์เป็น **static check**: โครงสร้างสไลด์ (ไฟล์เดียว ไม่มี CDN, asset ครบ), หัวข้อบังคับใน readme ของทุก LAB, ลิงก์/รูปที่อ้างถึงมีจริง,
ไม่มี token/email จริงหลุด, syntax ของ Python และ tag `:latest`/`version:` ใน compose

สร้างสไลด์ใหม่จากต้นฉบับ (แก้ HTML fragment ใน `slides_assets/deck_src/` แล้ว):

```bash
cd slides_assets/deck_src
python3 build_deck.py && python3 check_deck.py       # ต้องได้ overflowing slides / broken images / js errors = none
python3 diagrams.py                                   # วาดไดอะแกรม Excalidraw ใหม่ (ต้องมี canvas server — ดูหัวไฟล์)
```

## เก็บกวาด (Cleanup)

จบแต่ละ LAB ให้ทำตาม **เก็บกวาด** ของ LAB นั้น (ส่วนใหญ่ปล่อย Plane ไว้ใช้ต่อ) · จบ LAB 9 ลบทั้งหมดข้างในเครื่องเรียน:

```bash
cd ~/plane-selfhost && docker compose -f docker-compose.yml --env-file plane.env -p plane down -v
docker ps -a
```

อย่าลบ `devtools` ระหว่างชุด LAB เพราะ clone และ Plane อยู่ในนั้น หากต้องการ reset จริง ๆ ให้ `docker rm -f devtools` จากเครื่องของผู้เรียน
