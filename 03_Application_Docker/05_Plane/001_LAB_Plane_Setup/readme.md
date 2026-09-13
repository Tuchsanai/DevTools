# LAB 1 — ติดตั้ง Plane ด้วย Docker Compose (`setup.sh`) และเปิดเว็บผ่าน VS Code

> โฟลเดอร์ `001_LAB_Plane_Setup` = **LAB 1** ใน `Plane_Agile_Slides.html`
> (ไฟล์ของแล็บนี้ : `check_lab01.sh` · `images/`)
> (เวลาโดยประมาณ : 45 นาที)

## สิ่งที่จะได้เรียนรู้

- ติดตั้ง **Plane Community Edition** แบบ self-host ตาม[คู่มือ Docker Compose ของ Plane](https://developers.plane.so/self-hosting/methods/docker-compose) ด้วยสคริปต์ `setup.sh` ตัวเดียว ไม่ต้อง clone source หรือเขียน Compose เอง
- อ่านไฟล์ `plane.env` ให้เป็น: `LISTEN_HTTP_PORT` คือพอร์ตที่เครื่องเรียนฟัง ส่วน `WEB_URL` / `CORS_ALLOWED_ORIGINS` ต้องเท่ากับ URL ที่ **เบราว์เซอร์** ใช้จริง
- เปิดเว็บที่รันในเครื่องเรียนผ่าน **VS Code Remote-SSH → PORTS** โดย forward พอร์ตเดียว (**8089**) และรู้ว่าต้องทำอย่างไรเมื่อพอร์ตฝั่งผู้เรียนไม่ตรงกับพอร์ตในเครื่องเรียน
- แยก **Up** (container ยังไม่ตาย) ออกจาก **Ready** (เว็บและ API ตอบ `200`) แล้วทำ first-run: ตั้งผู้ดูแล instance → Workspace → Project **Plane Lab (`PLAB`)** → work items 3 ใบ

**กติกาข้อมูล:** ชื่อ อีเมล และรหัสผ่านในเอกสารนี้เป็น **placeholder สำหรับแล็บ** (`admin@example.com` / `Plane-Lab-2569` / workspace `DevTools Lab`) ห้ามใช้ข้อมูลจริงของตนเอง และปกปิดข้อมูลส่วนตัวก่อนจับภาพส่งงาน

## ทฤษฎีที่เกี่ยวข้อง

- **เว็บแอปสมัยใหม่ไม่ใช่โปรเซสเดียว** — Plane ประกอบจาก **13 container**: proxy (Caddy) · web · admin · space · live · api · worker · beat-worker · migrator · plane-db (PostgreSQL) · plane-redis (Valkey) · plane-mq (RabbitMQ) · plane-minio (object storage) `setup.sh` เป็นเพียงตัวห่อ `docker compose` ที่ดาวน์โหลด `docker-compose.yaml` + `plane.env` ของรุ่นล่าสุดมาให้ แล้วสั่ง `up -d` / `down` แทนเรา
- **Migration ก่อน แล้วค่อยเปิดบริการ** — `migrator` รัน `manage.py migrate` แล้วจบตัวเอง (`Exited (0)`) ส่วน `api`/`worker` รอจน schema พร้อมจึงเริ่มฟังพอร์ต ระหว่างนั้น `docker ps` ขึ้น `Up` ทั้งที่เว็บยังตอบ `502` — `setup.sh` จึงพิมพ์ *Waiting for Data Migration* และ *Waiting for API Service* ให้เห็น
- **URL ฝั่งเบราว์เซอร์ ≠ พอร์ตฝั่งเครื่องเรียน** — Remote-SSH สร้าง SSH tunnel: เบราว์เซอร์คุยกับ `localhost:<LOCAL_PORT>` บนเครื่องผู้เรียน แล้ว VS Code ส่งต่อไปยัง `8089` ในเครื่องเรียน หลัง login Plane จะ **redirect ไปที่ `WEB_URL`** ค่านี้จึงต้องเป็น URL ฝั่งเบราว์เซอร์ ไม่ใช่พอร์ตที่ proxy ฟัง

## ภาพรวมของแล็บนี้

เตรียมเครื่องเรียน → ดาวน์โหลด `setup.sh` → **1 Install** → แก้ `plane.env` (พอร์ต 8089 + URL) → **2 Start** → Forward 8089 ใน VS Code → เปิดเว็บ → ตั้งผู้ดูแล → Workspace → Project → Work items 3 ใบ → ตรวจสถานะและทดลอง stop/start

![ขั้นตอนติดตั้ง Plane ด้วย setup.sh และเปิดเว็บผ่าน VS Code (วาดด้วย Excalidraw MCP)](images/setup-flow.png)

[ไฟล์แก้ไข Excalidraw](images/setup-flow.excalidraw)

> **คำถามก่อนเริ่ม:** `setup.sh` บอกว่า *Plane Server started successfully* แล้ว — เราจะพิสูจน์จากเครื่องผู้เรียนได้อย่างไรว่าเว็บใช้งานได้จริง และถ้า login แล้วเบราว์เซอร์เด้งไปพอร์ตที่เปิดไม่ได้ ต้องแก้ค่าไหน?

## 0. เตรียมเครื่องสำหรับเรียน

**เตรียมเครื่องสำหรับเรียน** — บนเครื่องผู้เรียน เปิด classroom container เดิม หรือสร้างใหม่หากยังไม่มี:

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
```

จากนั้น remote เข้าเครื่องเรียน:

```bash
ssh root@localhost -p 2222   # password: passwd
```

📝 **คำอธิบาย:** `-p 2222:22` เปิดเฉพาะ SSH ส่วนเว็บของ Plane จะเปิดผ่าน **VS Code Remote-SSH → PORTS** (ข้อ 4) ไม่ต้องสร้าง container ใหม่เพื่อเพิ่ม port mapping · บัญชี `root`/`passwd` เป็นค่าเริ่มต้นของ classroom image ไม่ใช่บัญชี Plane

**เปิด VS Code Remote-SSH:** ติดตั้งส่วนขยาย **Remote - SSH** → Command Palette → **Remote-SSH: Connect to Host...** → เพิ่ม `ssh root@localhost -p 2222` → เปิดโฟลเดอร์ `/root` ในเครื่องเรียน จากนี้ **ทุกคำสั่งรันใน terminal ของ VS Code ที่อยู่ในเครื่องเรียน** ตรวจว่า Docker ภายในพร้อม:

```bash
docker --version && docker compose version
docker info --format '{{.ServerVersion}}'
```

✅ **Expected output** — แสดงเวอร์ชันทั้งสามบรรทัด ไม่มี error `Cannot connect to the Docker daemon` (ถ้ามี ให้รอ 10–20 วินาทีแล้วลองใหม่) เครื่องเรียนต้องมีอย่างน้อย **2 CPU / RAM 4 GB** และอินเทอร์เน็ต เพราะต้อง pull image รวมประมาณ 4–5 GB

## 1. ดาวน์โหลด `setup.sh` (ตามคู่มือ Plane)

```bash
mkdir plane-selfhost
cd plane-selfhost
curl -fsSL -o setup.sh https://github.com/makeplane/plane/releases/latest/download/setup.sh
chmod +x setup.sh
ls -la
```

✅ **Expected output** — มีไฟล์ `setup.sh` ขนาดประมาณ 22 KB สิทธิ์ `-rwxr-xr-x`

📝 **คำอธิบาย:** โฟลเดอร์ `plane-selfhost` เป็นที่เก็บทั้งสคริปต์และไฟล์ตั้งค่า — สคริปต์จะสร้างโฟลเดอร์ย่อย `plane-app/` ให้เองในข้อถัดไป และ **ทุกคำสั่ง `./setup.sh` ต้องรันจากโฟลเดอร์นี้**

## 2. `./setup.sh` → เลือก **1 Install**

```bash
./setup.sh
```

```
Select a Action you want to perform:
   1) Install
   2) Start
   3) Stop
   4) Restart
   5) Upgrade
   6) View Logs
   7) Backup Data
   8) Exit

Action [2]: 1
```

พิมพ์ `1` แล้ว Enter สคริปต์จะตรวจรุ่นล่าสุด (`v1.4.2` ณ วันที่ทดสอบ) ดาวน์โหลด `docker-compose.yaml` + `plane.env` ลง `plane-app/` แล้วเริ่ม pull image

✅ **Expected output** — เห็นบรรทัด `Plane supports amd64` และรายการ `Image ... Pulling/Pulled` จบด้วย `Most recent version of Plane is now available for you to use` แล้วกลับสู่ prompt (สคริปต์ออกเอง ไม่ต้องกด 8)

> ⚠️ **ถ้าเห็น `pull access denied for minio/minio ... Failed to pull the images. Exiting...`** ไม่ต้องรันใหม่ — ไฟล์ `plane-app/docker-compose.yaml` และ `plane-app/plane.env` ถูกสร้างเรียบร้อยแล้ว เพียงแต่ image MinIO บน Docker Hub (`minio/minio:latest`) ถูกถอดออกไป ให้ชี้ไปที่ registry ทางการของ MinIO แทน (พบตอนทดสอบ 13 ก.ย. 2569 ถ้า pull ผ่านก็รันคำสั่งนี้ได้เช่นกัน ไม่มีผลเสีย):
>
> ```bash
> sed -i 's|image: minio/minio:latest|image: quay.io/minio/minio:RELEASE.2025-04-22T22-12-26Z|' plane-app/docker-compose.yaml
> grep -n 'quay.io' plane-app/docker-compose.yaml
> ```
>
> image ที่เหลือจะถูก pull ต่อให้เองตอนกด **2 Start** ในข้อ 3

📝 **คำอธิบาย:** `ls plane-app/` ต้องเห็น `docker-compose.yaml`, `plane.env` และ `archive/` — สองไฟล์นี้คือทั้งหมดที่ Docker Compose ต้องใช้ · ไม่มี `-p` ในคำสั่งของสคริปต์ ดังนั้นชื่อ compose project = ชื่อโฟลเดอร์ **`plane-app`** → container ชื่อ `plane-app-<service>-1`, volume `plane-app_<name>`, network `plane-app_default`

## 3. ตั้งพอร์ต **8089** และ URL ใน `plane.env` แล้ว **2 Start**

### 3.1 พอร์ตที่กำหนดสำหรับแล็บนี้

| พอร์ต / บริการ | ต้อง forward ใน VS Code? | ใช้ทำอะไร |
| --- | --- | --- |
| **8089 — Plane proxy (HTTP)** | **ใช่ — พอร์ตเดียวที่ต้อง forward** | หน้าเว็บ, `/api/`, `/god-mode/`, `/spaces/`, `/live/` (WebSocket) และไฟล์แนบ ผ่าน proxy เดียว |
| SSH — host `2222` → container `22` | ไม่ต้อง (Remote-SSH ใช้อยู่แล้ว) | ท่อขนส่งของ PORTS ทุกแถว |
| 8443 — proxy HTTPS | ไม่ต้อง | ใช้เมื่อมีโดเมนและ TLS จริง แล็บนี้ใช้ HTTP |
| PostgreSQL 5432, Valkey 6379, RabbitMQ 5672/15672, MinIO 9000/9090 | ไม่ต้อง | บริการภายใน network `plane-app_default` เท่านั้น (LAB 2 จะเปิดดูผ่าน `docker exec`) |

📝 **คำอธิบาย:** ค่าตั้งต้นคือ `LISTEN_HTTP_PORT=80` / `LISTEN_HTTPS_PORT=443` ซึ่งชนกับงานอื่นในเครื่องเรียนได้ง่าย แล็บนี้กำหนด **8089** (และ 8443) ไว้ตายตัว จะได้ไม่ชนกับพอร์ต 8080–8088 ของแล็บอื่น

### 3.2 แก้ `plane.env` ด้วยคำสั่งเดียว

```bash
cd ~/plane-selfhost
sed -i 's|^LISTEN_HTTP_PORT=.*|LISTEN_HTTP_PORT=8089|; s|^LISTEN_HTTPS_PORT=.*|LISTEN_HTTPS_PORT=8443|; \
        s|^WEB_URL=.*|WEB_URL=http://localhost:8089|; s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost:8089|' plane-app/plane.env
sed -i "s|^SECRET_KEY=.*|SECRET_KEY=$(openssl rand -hex 32)|; s|^LIVE_SERVER_SECRET_KEY=.*|LIVE_SERVER_SECRET_KEY=$(openssl rand -hex 32)|" plane-app/plane.env
grep -nE '^(APP_RELEASE|LISTEN_HTTP_PORT|LISTEN_HTTPS_PORT|WEB_URL|CORS_ALLOWED_ORIGINS)=' plane-app/plane.env
```

✅ **Expected output**

```
2:APP_RELEASE=v1.4.2
12:LISTEN_HTTP_PORT=8089
13:LISTEN_HTTPS_PORT=8443
15:WEB_URL=http://localhost:8089
17:CORS_ALLOWED_ORIGINS=http://localhost:8089
```

📝 **คำอธิบาย:** **(1)** `LISTEN_HTTP_PORT` = พอร์ตที่ proxy publish บนเครื่องเรียน (`8089->80/tcp`) **(2)** `WEB_URL` และ `CORS_ALLOWED_ORIGINS` = URL ที่ **เบราว์เซอร์** จะเปิด — ตอนนี้ตั้งเป็น `http://localhost:8089` เพราะปกติ VS Code จะให้ local port เท่ากับ remote port (ถ้าไม่เท่า ข้อ 4.3 จะแก้) **(3)** `SECRET_KEY` / `LIVE_SERVER_SECRET_KEY` มาเป็น `change-this-key-on-deployment` ซึ่ง api จะเตือนระดับ CRITICAL จึงสุ่มค่าใหม่ด้วย `openssl rand` (ค่าของแต่ละคนต่างกัน **ห้าม**คัดลอกลงเอกสาร) · ไม่ต้องแก้ `APP_DOMAIN`/`SITE_ADDRESS` — proxy ฟัง `:80` ภายใน container เหมือนเดิม

### 3.3 `./setup.sh` → เลือก **2 Start**

```bash
./setup.sh
```

พิมพ์ `2` แล้ว Enter (หรือกด Enter เฉย ๆ ก็ได้เพราะค่า default คือ 2) สคริปต์จะ `docker compose up -d` แล้วรอ migration และ API ให้เอง ครั้งแรกใช้เวลา 2–5 นาทีขึ้นกับความเร็ว pull image

✅ **Expected output** (ตัดจากผลรันจริง)

```
   Data Migration completed successfully ✅
   Waiting for API Service to be ready...
   API Service started successfully ✅
   Plane Server started successfully ✅

   You can access the application at http://localhost:8089
```

ตรวจพอร์ตจริงที่ proxy publish และจำนวน container:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
docker ps -a --format '{{.Names}} {{.Status}}' | grep migrator
curl -s -o /dev/null -w 'web %{http_code}\n' http://localhost:8089/
curl -s -o /dev/null -w 'api %{http_code}\n' http://localhost:8089/api/instances/
```

✅ **Expected output** — 12 container `Up` (web/admin/space มี `(healthy)`) แถว `plane-app-proxy-1` มี `0.0.0.0:8089->80/tcp` · `plane-app-migrator-1 Exited (0)` · `web 200` และ `api 200`

📝 **คำอธิบาย:** ตอนนี้ Plane พร้อม *ในเครื่องเรียน* แล้ว แต่เบราว์เซอร์บนเครื่องผู้เรียนยังเข้าไม่ถึง เพราะ classroom container เปิดไว้แค่พอร์ต 22 — ข้อ 4 จะสร้างเส้นทางด้วย VS Code

## 4. Forward พอร์ตด้วย VS Code และตั้ง URL ให้ตรงกับเบราว์เซอร์

![เส้นทางเปิดเว็บผ่าน VS Code Remote-SSH: Browser → PORTS → SSH tunnel → proxy 8089 → บริการภายใน (วาดด้วย Excalidraw MCP)](images/ports-flow.png)

[ไฟล์แก้ไข Excalidraw](images/ports-flow.excalidraw)

### 4.1 เพิ่มพอร์ตผ่าน PORTS → Forward a Port

1. ในหน้าต่าง VS Code ที่เชื่อม Remote-SSH อยู่ เปิด panel ด้านล่าง → แท็บ **PORTS** (ถ้าไม่เห็น: Command Palette → **Ports: Focus on Ports View**)
2. กด **Forward a Port** → พิมพ์ **`8089`** → Enter
3. อ่านคอลัมน์ **Forwarded Address** ของแถวนั้น — ปกติจะเป็น `localhost:8089` (local port = remote port)

### 4.2 เปิดเว็บจาก Forwarded Address

คลิกไอคอน **Open in Browser** (ลูกโลก) ที่แถว 8089 หรือคัดลอก Forwarded Address แล้วเปิด **`http://localhost:8089`** ในเบราว์เซอร์บนเครื่องผู้เรียน ต้องเห็นหน้า **Welcome to Plane**

📝 **คำอธิบาย:** `localhost` ในเบราว์เซอร์คือ **เครื่องผู้เรียน** ส่วน `localhost` ใน terminal ของ VS Code คือ **เครื่องเรียน** — VS Code เชื่อมสองฝั่งด้วย SSH tunnel ผ่านพอร์ต 2222 ที่มีอยู่แล้ว จึงไม่ต้องแก้ `docker run`

### 4.3 ถ้าพอร์ตฝั่งผู้เรียนต่างจากพอร์ตในเครื่องเรียน

ถ้าพอร์ต 8089 บนเครื่องผู้เรียนไม่ว่าง VS Code จะเลือกเลขอื่นให้ เช่น Forwarded Address = `localhost:8090` → **ต้องใช้ URL ฝั่งผู้เรียน** `http://localhost:8090` ในเบราว์เซอร์ และแก้ `WEB_URL`/`CORS_ALLOWED_ORIGINS` ให้เท่ากับ URL นั้น แล้ว Restart:

```bash
cd ~/plane-selfhost
sed -i 's|^WEB_URL=.*|WEB_URL=http://localhost:8090|; s|^CORS_ALLOWED_ORIGINS=.*|CORS_ALLOWED_ORIGINS=http://localhost:8090|' plane-app/plane.env
./setup.sh      # เลือก 4 Restart
```

`LISTEN_HTTP_PORT` **คง 8089** และแถวใน PORTS ยังเป็น 8089 เหมือนเดิม — เปลี่ยนเฉพาะ URL ฝั่งเบราว์เซอร์ (ทางเลือก: คลิกขวาที่แถว → **Change Local Address Port** → `8089` เมื่อพอร์ตนั้นว่างแล้ว)

📝 **คำอธิบาย (หลักฐานจากการทดสอบ):** เมื่อเปิดเว็บผ่าน local port `18089` ทั้งที่ `WEB_URL=http://localhost:8089` การ login ยังตอบ `302` ตามปกติ แต่เบราว์เซอร์ถูกส่งไปที่ **`http://localhost:8089/onboarding/`** — คือกลับไปพอร์ตของ `WEB_URL` ถ้าพอร์ตนั้นไม่ได้ forward ไว้จะเจอหน้าเปล่า/เชื่อมต่อไม่ได้ · เช่นเดียวกัน หลังตั้งผู้ดูแลใน god-mode ระบบ redirect ไป `WEB_URL + /god-mode/general/` ดังนั้น **URL ที่เบราว์เซอร์ใช้ = `WEB_URL` = `CORS_ALLOWED_ORIGINS`** เสมอ

## 5. เปิดเว็บ → ตั้งผู้ดูแล → Workspace → Project → Work items

### 5.1 Welcome → god-mode

![หน้า Welcome to Plane ผ่านพอร์ตที่ forward (Playwright)](images/welcome.png)

กด **Get started** → ไปที่ `http://localhost:8089/god-mode/` หน้า **Setup your Plane Instance** กรอกด้วยค่า placeholder ของแล็บ:

| ช่อง | ค่าที่กรอก |
| --- | --- |
| First name / Last name | `Lab` / `Admin` |
| Email | `admin@example.com` |
| Company name | `DevTools Lab` |
| Set a password / Confirm password | `Plane-Lab-2569` |

![ฟอร์ม Setup your Plane Instance กรอกครบก่อนกด Continue](images/godmode-setup.png)

กด **Continue** → เบราว์เซอร์ถูกส่งไป **`http://localhost:8089/god-mode/general/`** พร้อมป๊อปอัป *Create workspace — Instance setup done!* (กด **Close** ได้ เราจะสร้าง workspace ผ่าน onboarding)

![god-mode › General หลังตั้งค่า: Name of instance = DevTools Lab](images/godmode-general.png)

✅ **Expected output** — URL ลงท้าย `/god-mode/general/` **บน host และพอร์ตเดียวกับที่เปิดมา** (นี่คือหลักฐานว่า `WEB_URL` ถูกต้อง) ตรวจซ้ำจาก terminal เครื่องเรียน:

```bash
curl -s http://localhost:8089/api/instances/ | python3 -c '
import sys, json; d = json.load(sys.stdin)["instance"]
print("is_setup_done:", d["is_setup_done"], "| instance_name:", d["instance_name"])'
```

```
is_setup_done: True | instance_name: DevTools Lab
```

📝 **คำอธิบาย:** รหัสผ่านถูกตรวจฝั่ง server ด้วย zxcvbn — รหัสง่าย ๆ อย่าง `Password123!` จะถูกปฏิเสธ (`PASSWORD_TOO_WEAK`) แม้ผ่านกฎบนหน้าจอ · ไม่มี SMTP ในแล็บนี้ จึง login ด้วยรหัสผ่านเท่านั้น

### 5.2 Sign in → onboarding

กลับไปที่ `http://localhost:8089/` → กรอก **Email** `admin@example.com` → **Continue** → **Password** `Plane-Lab-2569` → **Go to workspace**

![หน้า sign-in หลังตั้ง instance แล้ว](images/signin.png)

1. **Create your profile** — ช่อง Name ถูกเติม `Lab` ไว้แล้ว ปล่อยไว้ กด **Continue**
2. **Create your workspace** — Name `DevTools Lab` (slug จะเป็น `devtools-lab` อัตโนมัติ) → เลือก **2-10** → **Create workspace**
3. **Invite your teammates** — กด **I'll do it later** (ไม่มี SMTP อีเมลส่งไม่ออกอยู่แล้ว)
4. ถึง Home `http://localhost:8089/devtools-lab/` — ถ้ามีป๊อปอัป Product Tour กด **No thanks, I will explore it myself**

![onboarding: Create your workspace — DevTools Lab / devtools-lab / 2-10](images/onboarding-workspace.png)

### 5.3 Project `Plane Lab` (`PLAB`) และ work items 3 ใบ

แถบซ้าย **Projects** → **Add Project** → Project name `Plane Lab` → แก้ Project ID เป็น **`PLAB`** → **Create project** → ป๊อปอัป *Projects and work items* กด **Open project**

![Project Plane Lab ถูกสร้าง — ป๊อปอัปเปิด/ปิดฟีเจอร์ของโปรเจกต์](images/project-created.png)

ในหน้า **Work items** กด **New work item** → พิมพ์ Title → **Save** ทำ 3 ครั้ง:

| # | Title |
| --- | --- |
| PLAB-1 | ออกแบบหน้ารายการอาหาร |
| PLAB-2 | เพิ่มตะกร้าสินค้า |
| PLAB-3 | แสดงสถานะคำสั่งซื้อ |

![work items 3 ใบใน Plane Lab (PLAB-1..3) จากการทดลองจริง](images/work-items.png)

✅ **Expected output** — รายการ **All work items 3** สถานะ `Backlog` เลข `PLAB-1`…`PLAB-3` ตามลำดับที่สร้าง (โปรเจกต์ `DevTools Lab` อีกอันคือตัวอย่างที่ระบบ seed ให้ตอนสร้าง workspace ไม่ต้องลบ)

## 6. ตรวจสถานะและเตรียมคำสั่งลัดสำหรับแล็บถัดไป

`setup.sh` มีเมนู **6 View Logs** ให้เลือกดู log ของแต่ละ service (กด `0` กลับเมนูหลัก, `8` ออก):

```bash
./setup.sh      # เลือก 6 → เลือก 3 (API) → Ctrl+C เพื่อหยุดดู
```

สร้าง helper **`pc`** = `docker compose` พร้อมไฟล์ของ Plane ใช้ได้จากทุกโฟลเดอร์ (LAB 2–9 ใช้คำสั่งนี้ตลอด):

```bash
cat > /usr/local/bin/pc <<'EOF'
#!/bin/bash
exec docker compose -f "$HOME/plane-selfhost/plane-app/docker-compose.yaml" --env-file "$HOME/plane-selfhost/plane-app/plane.env" "$@"
EOF
chmod +x /usr/local/bin/pc
pc ps --format 'table {{.Service}}\t{{.Status}}\t{{.Ports}}'
```

✅ **Expected output** — 12 service `running` (migrator `exited (0)`) แถว `proxy` มี `0.0.0.0:8089->80/tcp`

📝 **คำอธิบาย:** `pc` ชี้ไปที่ไฟล์ชุดเดียวกับที่ `setup.sh` ใช้ จึงเห็น project `plane-app` เดียวกัน (`pc logs -f api`, `pc exec plane-db psql ...`, `pc stop worker`) · `setup.sh` ใช้เมื่อต้องการ Start/Stop/Upgrade/Backup ทั้งชุด ส่วน `pc` ใช้เจาะราย service

ตัวตรวจอัตโนมัติของแล็บ (รันในเครื่องเรียน หลัง clone ชุด LAB):

```bash
bash check_lab01.sh
```

✅ **Expected output** — บรรทัดเดียวขึ้นต้นด้วย `PASS:` เช่น `PASS: 12 containers up, proxy on 8089, web+API HTTP 200 after 0s, is_setup_done=True` (ตรวจไฟล์/พอร์ต/HTTP เท่านั้น ไม่ตรวจ workspace หรือ work items)

## ทดลองเพิ่มเติม

**หยุดแล้วเปิดใหม่ — ข้อมูลยังอยู่ไหม?** ใน `~/plane-selfhost` รัน `./setup.sh` → **3 Stop** แล้วดู `docker ps` (ต้องไม่มี `plane-app-*` เหลือ เพราะ Stop = `docker compose down` ลบ container แต่ **ไม่ลบ volume**) จากนั้น `./setup.sh` → **2 Start** รอจน *Plane Server started successfully* แล้วรีเฟรชหน้า Work items:

![หน้า Work items หลัง Stop แล้ว Start ใหม่ — PLAB-1..3 ยังอยู่](images/after-restart.png)

✅ **Expected output** — login ด้วยบัญชีเดิมได้ และ PLAB-1..3 ยังอยู่ครบ เพราะข้อมูลอยู่ใน volume `plane-app_pgdata` (PostgreSQL) และ `plane-app_uploads` (MinIO): `docker volume ls | grep plane-app`

**ดูว่า Plane ตอบอะไรก่อน API พร้อม** — สั่ง `pc restart api` แล้วยิง `curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8089/api/instances/` ซ้ำทุกวินาที จะเห็น `502` ราว 10–20 วินาทีก่อนกลับเป็น `200` — นี่คือช่องว่างระหว่าง *Up* กับ *Ready*

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ / สิ่งที่ตรวจ |
| --- | --- |
| `Failed to pull the images` และมี `pull access denied for minio/minio` | image บน Docker Hub ถูกถอด → รัน `sed` ในข้อ 2 ให้ใช้ `quay.io/minio/minio` แล้วกด **2 Start** ไม่ต้อง Install ใหม่ |
| Install ค้างที่ `Checking for the latest release` หรือ curl ล้มเหลว | เครื่องเรียนออกอินเทอร์เน็ตไม่ได้ (`api.github.com`, `registry-1.docker.io`, `quay.io`) ตรวจ DNS/proxy แล้วรันใหม่ |
| `Bind for 0.0.0.0:8089 failed: port is already allocated` | มีงานอื่นใช้ 8089 ในเครื่องเรียน → `docker ps --format '{{.Names}} {{.Ports}}' \| grep 8089` แล้วเปลี่ยน `LISTEN_HTTP_PORT` เป็นพอร์ตว่าง (เช่น 8088) และ forward เลขนั้นแทน **อย่าหยุดงานของคนอื่น** |
| เปิด `http://localhost:8089` ไม่ได้จากเครื่องผู้เรียน แต่ `curl` ในเครื่องเรียนได้ `200` | ยังไม่ได้ forward พอร์ตใน PORTS หรือ Forwarded Address เป็นเลขอื่น → ใช้เลขที่ VS Code แสดง (ข้อ 4.3) |
| login แล้วเด้งไปพอร์ตอื่น / หน้าเปล่า | `WEB_URL` ไม่ตรงกับ URL ฝั่งเบราว์เซอร์ → แก้ `WEB_URL`/`CORS_ALLOWED_ORIGINS` แล้ว `./setup.sh` → 4 Restart |
| เว็บตอบ `502` หรือ `Waiting for API Service` นาน | migration ยังไม่จบ / api ยังบูต → `pc logs -f migrator api` รอจน `migrator Exited (0)`; ถ้า `Plane Server failed to start ❌` ให้อ่าน log ของ migrator |
| `PASSWORD_TOO_WEAK` ใน god-mode | server ตรวจด้วย zxcvbn → ใช้รหัสยาวและไม่ใช่รูปแบบทั่วไป เช่น `Plane-Lab-2569` |
| แก้ `plane.env` แล้วค่าไม่เปลี่ยน | ค่าถูกอ่านตอนสร้าง container → ต้อง **4 Restart** (หรือ `pc up -d <service>`) ไม่ใช่ `docker restart` |

## เก็บกวาด (Cleanup)

ปล่อย Plane รันไว้ใช้ต่อใน LAB 2–9 ถ้าจะพักเครื่อง ให้ `./setup.sh` → **3 Stop** และกลับมา **2 Start** (ข้อมูลอยู่ใน volume)

ถ้าจะลบ Plane ทั้งชุด **รวมข้อมูล** (ทำตอนจบ LAB 9 เท่านั้น):

```bash
cd ~/plane-selfhost && pc down -v && cd ~ && rm -rf ~/plane-selfhost
docker ps -a | grep plane-app || echo "plane-app removed"
```

ถ้าใช้ classroom container ชั่วคราวและจบทุกการทดลองแล้ว ให้ลบเฉพาะของตนเองจากเครื่องผู้เรียน: `docker rm -f devtools`

## สรุปคำสั่งของแล็บนี้

| งาน | คำสั่ง (รันใน `~/plane-selfhost` ของเครื่องเรียน) |
| --- | --- |
| ดาวน์โหลดสคริปต์ | `curl -fsSL -o setup.sh https://github.com/makeplane/plane/releases/latest/download/setup.sh && chmod +x setup.sh` |
| ติดตั้ง / เริ่ม / หยุด / รีสตาร์ท | `./setup.sh` → `1` / `2` / `3` / `4` (หรือ `./setup.sh install|start|stop|restart`) |
| ดู log | `./setup.sh` → `6` หรือ `pc logs -f api` |
| ตั้งพอร์ตและ URL | `sed -i ... plane-app/plane.env` (ข้อ 3.2 / 4.3) แล้ว `./setup.sh` → `4` |
| ตรวจความพร้อม | `docker ps` · `curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8089/api/instances/` · `bash check_lab01.sh` |
| helper สำหรับแล็บถัดไป | `pc ps` · `pc logs -f <service>` · `pc exec <service> <cmd>` |

## เช็กลิสต์ก่อนจบแล็บ

- [ ] `~/plane-selfhost/plane-app/` มี `docker-compose.yaml` และ `plane.env`; `./setup.sh` → 2 Start จบด้วย *Plane Server started successfully*
- [ ] `docker ps` เห็น `plane-app-proxy-1` publish `8089->80/tcp` และ 12 container `Up`
- [ ] Forward 8089 ใน PORTS แล้วเปิด `http://localhost:<LOCAL_PORT>` เห็น Plane; `WEB_URL`/`CORS_ALLOWED_ORIGINS` ตรงกับ URL นั้น และหลัง login/setup ไม่เด้งไปพอร์ตอื่น
- [ ] ตั้งผู้ดูแล instance สำเร็จ (`is_setup_done: True`) และ sign in ด้วยรหัสผ่านได้
- [ ] มี workspace `DevTools Lab`, project `Plane Lab` (`PLAB`) และ work items PLAB-1..3
- [ ] Stop → Start แล้วข้อมูลยังอยู่; `bash check_lab01.sh` ได้ `PASS:`
- [ ] มีคำสั่ง `pc` ใช้ได้ (`pc ps`)
- [ ] ภาพส่งงานใช้ placeholder ไม่มีข้อมูลส่วนตัวหรือ secret จริง

อ้างอิง: [Docker Compose — Plane self-hosting](https://developers.plane.so/self-hosting/methods/docker-compose) · [makeplane/plane releases](https://github.com/makeplane/plane/releases)

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงใน classroom container (Plane v1.4.2, ทดสอบเว็บและจับภาพด้วย Playwright ผ่าน SSH tunnel พอร์ต 8089) เมื่อ 13-ก.ย.-2569*
