# LAB 5 — รวมระบบด้วย Compose และส่งมอบผ่าน Docker Hub

> โฟลเดอร์ `005_LAB_Compose_And_Ship` · ใช้ `compose.yaml`, `api/`, `web/`, `db/initdb/` และ `verify.sh`

แล็บนี้ตอบ NFR-1–NFR-3 ของ CampusOps: ยกระบบสาม service ด้วยคำสั่งเดียว รักษาข้อมูลใน named volume ไม่เปิดพอร์ตฐานข้อมูล และส่ง image รุ่น `1.0` ให้เครื่องปลายทางโดยไม่ต้องมีซอร์สโค้ด

| ประเด็น | ผลลัพธ์ที่ต้องพิสูจน์ |
|---|---|
| Compose | `db` → `api` → `web` ขึ้นตาม healthcheck |
| Persistence | `down` รักษาข้อมูล แต่ `down -v` คืนฐานข้อมูลเป็น seed |
| Security | มีเพียง `web` ที่ publish port |
| Shipping | push/pull image สองก้อนผ่าน Docker Hub แบบ public |

## ทฤษฎีก่อนลงมือ

### `compose.yaml` แทนคำสั่งที่กระจายอยู่หลายบรรทัด

![แผนภาพจับคู่คำสั่ง docker run และ docker build กับ key ใน compose.yaml](./images/theory-run-to-compose.svg)

`build`, `environment`, `volumes`, `ports` และ `depends_on` ทำให้ข้อกำหนดการติดตั้งอยู่ในไฟล์ที่ตรวจทานและทำซ้ำได้ ส่วน `condition: service_healthy` ทำให้ service ถัดไปรอจน service ต้นทางพร้อมใช้งานจริง

![เส้นเวลา healthcheck แสดงลำดับ db api และ web](./images/theory-healthcheck-order.svg)

`docker compose down` ลบ container และ network แต่ไม่ลบ named volume; `docker compose down -v` ลบ volume และข้อมูลอย่างถาวร จึงใช้เฉพาะเมื่อต้องการ reset เป็น seed

### ส่งมอบ image ผ่าน Docker Hub

![แผนภาพทีมพัฒนา build tag และ push image ไปยัง Docker Hub แบบ public ก่อนเครื่องลูกค้า pull และรันด้วย compose โดยไม่มีซอร์สโค้ด](./images/theory-ship-registry.svg)

ชื่อ `<DOCKER_USER>/campusops-web:1.0` ประกอบด้วย namespace เจ้าของ, repository และ tag เวอร์ชัน Docker Hub สร้าง repository อัตโนมัติเมื่อ push ครั้งแรก แต่ต้องตรวจให้เป็น **Public** เพื่อให้เครื่องลูกค้า pull ได้โดยไม่ต้องรับ credential ของผู้พัฒนา

บัญชี Personal รองรับ private repository ได้หนึ่งแห่ง จึงกำหนด repository ของแล็บทั้งสองเป็น Public อัตรา pull ที่กำหนดในชุดสอนนี้คือ 100 ครั้งต่อ 6 ชั่วโมงต่อ IP เมื่อไม่ login และ 200 ครั้งต่อ 6 ชั่วโมงต่อบัญชีเมื่อ login หากพบ `429 Too Many Requests` ให้รอรอบโควตา, login ก่อน pull และหลีกเลี่ยงการ pull ซ้ำโดยไม่จำเป็น

## เตรียมเครื่องเรียน

รันบนเครื่องโฮสต์:

```bash
docker rm -f devtools-fs-lab5 2>/dev/null
docker run -dit --name devtools-fs-lab5 --privileged \
  -p 2255:22 -p 8255:3000 tuchsanai/devtools:2569_1
ssh root@localhost -p 2255        # password : passwd
```

คำสั่งทั้งหมดหลังจากนี้รันภายในกล่องเรียน:

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone --depth 1 https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/03_Fullstack_App_Example/005_LAB_Compose_And_Ship
ls
```

ผลรันต้องมีไฟล์และโฟลเดอร์ต่อไปนี้:

```text
api  compose.yaml  db  images  readme.md  verify.sh  web
```

> ทุกคำสั่ง Compose ในแล็บนี้ระบุ `-p campusops` เพื่อให้ชื่อ project คงที่

### Walkthrough เตรียมบัญชี Docker Hub และ Access Token

ใช้รหัสผ่านบัญชีเฉพาะหน้า Sign in ของเว็บ แต่ใช้ **Personal Access Token** แทนรหัสผ่านบัญชีเมื่อคำสั่ง `docker login` ถาม `Password:` ห้ามบันทึก token ลงเอกสารหรือไฟล์สคริปต์

#### ขั้นที่ ①–② — เปิด Docker Hub และเริ่ม Sign in

เปิด `https://hub.docker.com` แล้วคลิก **Sign in**

![หน้า Docker Hub พร้อม marker ที่โลโก้และปุ่ม Sign in](./images/ui-hub-01-home.png)

*ภาพที่ 1 — เปิด Docker Hub และเข้าสู่ขั้นตอน Sign in*

#### ขั้นที่ ③–④ — กรอกชื่อบัญชี

คลิกช่องชื่อบัญชี กรอก `<DOCKER_USER>` แล้วคลิก **Continue**

![หน้า Sign in พร้อม marker ที่ช่องชื่อบัญชีและปุ่ม Continue](./images/ui-hub-02-username.png)

*ภาพที่ 2 — ชื่อบัญชีถูกแทนด้วย `<DOCKER_USER>` ในสื่อการสอน*

#### ขั้นที่ ⑤–⑥ — กรอกรหัสผ่านบัญชี

คลิกช่องรหัสผ่าน กรอกรหัสผ่านบัญชี แล้วคลิก **Continue**

![หน้ารหัสผ่านพร้อม marker ที่ช่องรหัสผ่านและปุ่ม Continue](./images/ui-hub-03-password.png)

*ภาพที่ 3 — รหัสผ่านใช้สำหรับเว็บเท่านั้น ไม่ใช้กับคำสั่ง docker login*

#### ขั้นที่ ⑦ — เปิดเมนูบัญชี

คลิก avatar มุมขวาบน

![หน้า My Hub พร้อม marker ที่ avatar ซึ่งปิดอักษรย่อบัญชีแล้ว](./images/ui-hub-04-avatar.png)

*ภาพที่ 4 — avatar ถูกปิดข้อมูลระบุตัวบัญชี แต่ตำแหน่งคลิกยังชัดเจน*

#### ขั้นที่ ⑧ — เปิด Account settings

คลิก **Account settings**

![เมนูบัญชีพร้อม marker ที่ Account settings](./images/ui-hub-05-account-settings.png)

*ภาพที่ 5 — เปิดหน้าตั้งค่าบัญชีจากเมนู avatar*

#### ขั้นที่ ⑨–⑩ — เปิดรายการและเริ่มสร้าง token

คลิก **Personal access tokens** แล้วคลิก **Generate new token**

![หน้า Personal access tokens พร้อม marker ที่เมนูและปุ่มสร้าง token](./images/ui-hub-06-token-list.png)

*ภาพที่ 6 — เปิดรายการ token และเริ่มสร้าง token ใหม่*

#### ขั้นที่ ⑪ — กำหนด description

คลิกช่อง description แล้วกรอก `lab5-capture-20260820-083133`

![ฟอร์ม token พร้อม marker ที่ช่อง description](./images/ui-hub-07-description.png)

*ภาพที่ 7 — description ช่วยระบุ token ที่ต้อง revoke หลังจบแล็บ*

#### ขั้นที่ ⑫ — กำหนดวันหมดอายุ

คลิกรายการ Expiration แล้วเลือก **30 days**

![รายการ expiration พร้อม marker ที่ตัวเลือก 30 days](./images/ui-hub-08-expiration.png)

*ภาพที่ 8 — กำหนดอายุ token ให้สั้นตามระยะเวลาการใช้งาน*

#### ขั้นที่ ⑬ — กำหนด permission

คลิกรายการ permission แล้วเลือก **Read & Write**

![รายการ permission พร้อม marker ที่ Read and Write](./images/ui-hub-09-permission.png)

*ภาพที่ 9 — สิทธิ์ Write จำเป็นสำหรับ push และสิทธิ์ Read จำเป็นสำหรับ pull*

#### ขั้นที่ ⑭ — สร้าง token

คลิก **Generate**

![ฟอร์มพร้อม marker ที่ปุ่ม Generate](./images/ui-hub-10-generate.png)

*ภาพที่ 10 — สร้าง token หลังตรวจ description, expiration และ permission*

#### ขั้นที่ ⑮ — คัดลอก token

คลิก **Copy** และเก็บค่าเป็น `<DOCKER_TOKEN>` ใน password manager ชั่วคราว

![หน้าคัดลอก token พร้อม marker ที่ปุ่ม Copy และปิดค่าจริงแล้ว](./images/ui-hub-11-copy.png)

*ภาพที่ 11 — Docker Hub แสดง token ครั้งเดียว สื่อการสอนแทนค่าด้วย `<DOCKER_TOKEN>`*

## การทดลองที่ 1 — Compose ประกาศ service อะไร

**คำถาม:** `compose.yaml` อ่านได้และประกาศระบบครบสาม service หรือไม่

```bash
docker compose -p campusops config --services
```

✅ **สิ่งที่ต้องเห็น**

```text
db
api
web
```

> 📝 ผลลัพธ์ยืนยัน schema ขั้นต้นและชื่อ service ที่ Compose DNS ใช้ภายใน network เดียวกัน โดยยังไม่สร้าง container

## การทดลองที่ 2 — คำสั่งเดียวสร้างระบบครบไหม

**คำถาม:** Compose สามารถ build และยกทั้งระบบตาม NFR-1 ด้วยคำสั่งเดียวหรือไม่

```bash
docker compose -p campusops down -v
docker compose -p campusops up -d --build
```

✅ **สิ่งที่ต้องเห็น**

```text
Image campusops-api Built
Image campusops-web Built
Container campusops-db-1 Started
Container campusops-db-1 Healthy
Container campusops-api-1 Started
Container campusops-api-1 Healthy
Container campusops-web-1 Started
```

> 📝 ลำดับ Started และ Healthy เกิดจาก healthcheck กับ depends_on ไม่ใช่การกำหนดเวลารอแบบคงที่ จึงรองรับเครื่องที่มีความเร็วต่างกัน

## การทดลองที่ 3 — ฐานข้อมูลไม่เปิดพอร์ตออกนอกระบบจริงไหม

**คำถาม:** service ทั้งสาม healthy และมีเพียง web ที่ publish port หรือไม่

```bash
sleep 20
docker compose -p campusops ps
```

✅ **สิ่งที่ต้องเห็น**

```text
NAME              IMAGE                COMMAND                  SERVICE   CREATED          STATUS                    PORTS
campusops-api-1   campusops-api        "uvicorn main:app --…"   api       32 seconds ago   Up 25 seconds (healthy)   8000/tcp
campusops-db-1    postgres:17-alpine   "docker-entrypoint.s…"   db        32 seconds ago   Up 31 seconds (healthy)   5432/tcp
campusops-web-1   campusops-web        "docker-entrypoint.s…"   web       32 seconds ago   Up 20 seconds (healthy)   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
```

> 📝 `5432/tcp` เป็น metadata จาก EXPOSE ไม่ใช่ published port หลักฐานของ NFR-3 คือมี mapping `0.0.0.0:3000->3000/tcp` เฉพาะ web

## การทดลองที่ 4 — Service เริ่มตามลำดับที่กำหนดไหม

**คำถาม:** เวลาเริ่มของ container เรียงจาก db ไป api และ web หรือไม่

```bash
docker inspect -f '{{.Name}} start={{.State.StartedAt}} health={{.State.Health.Status}}' \
  campusops-db-1 campusops-api-1 campusops-web-1
```

คำสั่งนี้ยาวเพราะต้องอ่านเวลาและ health status ของ container ทั้งสามพร้อมกันเพื่อเปรียบเทียบลำดับโดยตรง

✅ **สิ่งที่ต้องเห็น**

```text
/campusops-db-1 start=2026-08-20T08:32:52.694233813Z health=healthy
/campusops-api-1 start=2026-08-20T08:32:58.374800112Z health=healthy
/campusops-web-1 start=2026-08-20T08:33:04.049456156Z health=healthy
```

> 📝 เวลา UTC จากรอบทดสอบเรียง db < api < web และทุกกล่อง healthy จึงยืนยันว่าลำดับรอพร้อมทำงานตามที่ compose.yaml กำหนด

## การทดลองที่ 5 — หน้าเว็บทั้งสี่ส่วนตอบสนองไหม

**คำถาม:** หน้า overview, tickets, loans และ parts ตอบ HTTP 200 ครบหรือไม่

```bash
curl -s -o /dev/null -w "GET / -> %{http_code}\n" http://localhost:3000/
curl -s -o /dev/null -w "GET /tickets -> %{http_code}\n" http://localhost:3000/tickets
```

```bash
curl -s -o /dev/null -w "GET /loans -> %{http_code}\n" http://localhost:3000/loans
curl -s -o /dev/null -w "GET /parts -> %{http_code}\n" http://localhost:3000/parts
```

✅ **สิ่งที่ต้องเห็น**

```text
GET / -> 200
GET /tickets -> 200
GET /loans -> 200
GET /parts -> 200
```

> 📝 จุดนี้ต้องตรวจรหัสสถานะจริงจึงคงรูปแบบ curl ที่มี `-w` ไว้ ส่วนการตรวจเนื้อหาและการเชื่อมฐานข้อมูลแสดงผ่าน walkthrough ถัดไป

### Walkthrough หน้า CampusOps ที่ Compose ยกขึ้น

เปิดเบราว์เซอร์บนเครื่องโฮสต์ที่ `http://localhost:8255` แล้วตรวจ UI ตามลำดับต่อไปนี้

#### ขั้นที่ ① — เปิดหน้า CampusOps

เปิดหน้า CampusOps ที่พอร์ต 8255

![หน้า CampusOps พร้อม marker ที่ชื่อระบบ](./images/ui-compose-01-overview.png)

*ภาพที่ 12 — หน้าแรกจากระบบที่ Compose ยกขึ้นจริงด้วยข้อมูล seed 8 ใบ*

#### ขั้นที่ ② — เปิดกระดานงานซ่อม

คลิก **กระดานงานซ่อม** และตรวจงาน seed ในสี่คอลัมน์

![กระดานงานซ่อมพร้อม marker ที่เมนูซึ่งถูกคลิก](./images/ui-compose-02-tickets.png)

*ภาพที่ 13 — กระดานแสดงรอรับเรื่อง 3, มอบหมายแล้ว 2, กำลังซ่อม 1 และปิดงานแล้ว 2 รวม 8 ใบ*

#### ขั้นที่ ③ — กลับหน้าสรุปภาพรวม

คลิก **สรุปภาพรวม** เพื่อกลับหน้าแรกและตรวจตัวเลข requirements

![หน้าสรุปภาพรวมพร้อม marker ที่เมนูสรุปภาพรวม](./images/ui-compose-03-back-overview.png)

*ภาพที่ 14 — งานที่ยังไม่ปิด 6 ใบ, เกินกำหนด 2 ใบ, ครุภัณฑ์ถูกยืม 2 ชิ้น และอะไหล่ต้องสั่งเพิ่ม 2 รายการ*

## การทดลองที่ 6 — ข้อมูลคงอยู่หลัง down แต่ reset หลัง down -v ไหม

**คำถาม:** named volume รักษาใบแจ้งซ่อมหลังปิดระบบและคืน seed เมื่อสั่งลบ volume หรือไม่

```bash
docker compose -p campusops exec -T db psql -U opsuser -d campusops -c "INSERT INTO tickets (asset_id,title,detail,priority) VALUES (4,'ไมโครโฟนห้องประชุมใหญ่เสียงขาด','แจ้งหลังส่งมอบระบบ','HIGH');"
docker compose -p campusops exec -T db psql -U opsuser -d campusops -tAc "SELECT count(*) FROM tickets;"
```

✅ **สิ่งที่ต้องเห็น**

```text
INSERT 0 1
9
```

ปิดและเปิดระบบโดยไม่ลบ volume แล้วนับอีกครั้ง:

```bash
docker compose -p campusops down
docker compose -p campusops up -d --no-build
```

```bash
sleep 20
docker compose -p campusops exec -T db psql -U opsuser -d campusops -tAc "SELECT count(*) FROM tickets;"
```

✅ **สิ่งที่ต้องเห็น**

```text
9
```

ลบ volume เปิดระบบใหม่ และนับ seed:

```bash
docker compose -p campusops down -v
docker compose -p campusops up -d --no-build
```

```bash
sleep 20
docker compose -p campusops exec -T db psql -U opsuser -d campusops -tAc "SELECT count(*) FROM tickets;"
```

✅ **สิ่งที่ต้องเห็น**

```text
8
```

> 📝 จำนวน 9 หลัง down พิสูจน์ persistence ส่วนจำนวน 8 หลัง down -v เป็น seed ชุดใหม่ ไม่ใช่ข้อมูลเดิม จึงต้องระวัง -v ในระบบจริง

## การทดลองที่ 7 — จะตรวจหาต้นเหตุข้าม service อย่างไร

**คำถาม:** อ่าน log รวมและทดสอบ DNS จาก web ไป api ได้หรือไม่

```bash
docker compose -p campusops logs --tail=1
docker compose -p campusops exec -T web wget -qO- http://api:8000/health; echo
```

✅ **สิ่งที่ต้องเห็น**

```text
api-1  | INFO:     172.19.0.4:37254 - "GET /api/dashboard HTTP/1.1" 200 OK
web-1  | ✓ Running next.config took 0.8ms
db-1   | 2026-08-20 08:34:01.570 UTC [1] LOG:  database system is ready to accept connections
{"status":"ok","db":"up"}
```

> 📝 คำนำหน้า service ช่วยแยกแหล่ง log และชื่อ `api` ถูกแก้ผ่าน Compose DNS ภายใน จึงไม่ผูกระบบกับ IP ที่เปลี่ยนเมื่อสร้าง container ใหม่

## การทดลองที่ 8 — ติดเวอร์ชันและส่งขึ้น Docker Hub ได้ไหม

**คำถาม:** image ที่ build ในเครื่องพัฒนาสามารถติด tag `1.0` และ push ไปยัง repository แบบ public ได้หรือไม่

```bash
docker login -u <DOCKER_USER>            # วาง Access Token ตอนถาม Password
docker tag campusops-api:latest <DOCKER_USER>/campusops-api:1.0
```

แทน `<DOCKER_USER>` ด้วยชื่อบัญชีจริงเฉพาะใน terminal และวาง Access Token เมื่อคำสั่งถาม `Password:`

```bash
docker tag campusops-web:latest <DOCKER_USER>/campusops-web:1.0
docker images <DOCKER_USER>/campusops-api
```

✅ **สิ่งที่ต้องเห็น**

```text
Login Succeeded

WARNING! Your credentials are stored unencrypted in '/root/.docker/config.json'.
IMAGE                              ID             DISK USAGE   CONTENT SIZE   EXTRA
<DOCKER_USER>/campusops-api:1.0   2c737965a208        251MB         60.3MB   U
```

push แยกสองคำสั่งเพื่อให้ระบุ image ที่ล้มเหลวได้ชัดเจน:

```bash
docker push <DOCKER_USER>/campusops-api:1.0
docker push <DOCKER_USER>/campusops-web:1.0
```

✅ **สิ่งที่ต้องเห็น** — ส่วนท้ายของผลรันจริงรอบนี้

```text
1.0: digest: sha256:2c737965a208b50cf56f68da0e03933af5d1fdc33dbe5721b6921f54c55279ae size: 856
1.0: digest: sha256:ceb28834907df500a84ac02e1432f9b2d9b0df3cb55b864fe0fbc73a387be481 size: 856
```

> 📝 tag ไม่ได้คัดลอก image แต่เพิ่มชื่อให้ IMAGE ID เดิม ส่วน push ครั้งแรกสร้าง repository อัตโนมัติ ต้องตรวจ Visibility เป็น Public ทั้งสองก้อน

### Walkthrough ยืนยัน image บนหน้า Docker Hub

#### ขั้นที่ ①–② — เปิด repository ทั้งสองจาก My Hub

คลิก **My Hub → Repositories** ตรวจค่า **Public** ของทั้งสองรายการ แล้วคลิก `campusops-api` ก่อน `campusops-web` ตาม marker

![รายการ Docker Hub พร้อม marker ที่ repository ทั้งสอง](./images/ui-hub-push-01-repositories.png)

*ภาพที่ 15 — repository ทั้งสองถูกสร้างจาก push และแสดง Visibility เป็น Public*

#### ขั้นที่ ③ — เปิดแท็บ Tags ของ API

ในหน้า `campusops-api` คลิกแท็บ **Tags**

![หน้า repository API พร้อม marker ที่แท็บ Tags](./images/ui-hub-push-02-api.png)

*ภาพที่ 16 — เปิดแท็บ Tags ของ `<DOCKER_USER>/campusops-api`*

#### ขั้นที่ ④–⑤ — อ่าน tag และ digest ของ API

ตรวจ tag `1.0`, digest, เวลาที่ push และขนาด

![แท็บ API Tags พร้อม marker ที่ tag และ digest](./images/ui-hub-push-03-api-tags.png)

*ภาพที่ 17 — API แสดง Last pushed 6 minutes ago, repository size 57.5 MB และ compressed size 57.49 MB*

#### ขั้นที่ ⑥ — เปิดแท็บ Tags ของ Web

กลับ Repositories คลิก `campusops-web` แล้วคลิกแท็บ **Tags**

![หน้า repository Web พร้อม marker ที่แท็บ Tags](./images/ui-hub-push-04-web.png)

*ภาพที่ 18 — เปิดแท็บ Tags ของ `<DOCKER_USER>/campusops-web`*

#### ขั้นที่ ⑦–⑧ — อ่าน tag และ digest ของ Web

ตรวจ tag `1.0`, digest, เวลาที่ push และขนาด

![แท็บ Web Tags พร้อม marker ที่ tag และ digest](./images/ui-hub-push-05-web-tags.png)

*ภาพที่ 19 — Web แสดง Last pushed 6 minutes ago, repository size 69.9 MB และ compressed size 69.87 MB*

## การทดลองที่ 9 — เครื่องลูกค้าที่ไม่มีซอร์สโค้ดยกระบบได้ไหม

**คำถาม:** หลังลบ image แอปทั้งหมด เครื่องปลายทางสามารถ pull แล้ว `up --no-build` โดยไม่มีขั้น build หรือไม่

```bash
docker compose -p campusops down
docker image rm campusops-api:latest campusops-web:latest <DOCKER_USER>/campusops-api:1.0 <DOCKER_USER>/campusops-web:1.0
```

```bash
docker images <DOCKER_USER>/campusops-api
```

✅ **สิ่งที่ต้องเห็น**

```text
Untagged: campusops-api:latest
Untagged: campusops-web:latest
Untagged: <DOCKER_USER>/campusops-api:1.0
Deleted: sha256:2c737965a208b50cf56f68da0e03933af5d1fdc33dbe5721b6921f54c55279ae
Untagged: <DOCKER_USER>/campusops-web:1.0
Deleted: sha256:ceb28834907df500a84ac02e1432f9b2d9b0df3cb55b864fe0fbc73a387be481
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
```

pull ต้องเขียนแยกสองคำสั่ง ห้ามใช้ wildcard:

```bash
docker pull <DOCKER_USER>/campusops-api:1.0
docker pull <DOCKER_USER>/campusops-web:1.0
```

```bash
docker tag <DOCKER_USER>/campusops-api:1.0 campusops-api:latest
docker tag <DOCKER_USER>/campusops-web:1.0 campusops-web:latest
```

```bash
docker compose -p campusops up -d --no-build
sleep 20
```

ตรวจสถานะและรหัส HTTP:

```bash
docker compose -p campusops ps
curl -s -o /dev/null -w "GET / -> %{http_code}\n" http://localhost:3000/
```

✅ **สิ่งที่ต้องเห็น** — log ของ `up` ไม่มีบรรทัด `Building`

```text
NAME              IMAGE                COMMAND                  SERVICE   CREATED          STATUS                    PORTS
campusops-api-1   campusops-api        "uvicorn main:app --…"   api       32 seconds ago   Up 25 seconds (healthy)   8000/tcp
campusops-db-1    postgres:17-alpine   "docker-entrypoint.s…"   db        32 seconds ago   Up 31 seconds (healthy)   5432/tcp
campusops-web-1   campusops-web        "docker-entrypoint.s…"   web       32 seconds ago   Up 20 seconds (healthy)   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
GET / -> 200
```

> 📝 --no-build พิสูจน์ว่าเครื่องปลายทางใช้ image ที่ pull มาโดยไม่อ่าน Dockerfile หรือ build source แต่ยังต้องมี compose.yaml และ db/initdb สำหรับระบบนี้

## ตรวจงานด้วย `verify.sh`

สคริปต์ไม่ push และไม่ลบ repository จริง การส่งมอบส่วนบังคับใช้ namespace ทดสอบในเครื่อง, `docker save`, ลบ image, `docker load` และ `up --no-build`; การตรวจ Docker Hub จริงเป็น opt-in ด้วย `HUB_USER`

```bash
bash verify.sh
echo "exit code = $?"
```

✅ **สิ่งที่ต้องเห็น** — `[PASS]` 26 บรรทัด, `[SKIP]` 1 บรรทัด และ exit code 0

```text
==============================================
 LAB 5 — Compose And Ship : verify
==============================================
[PASS] ต่อกับ Docker daemon ได้
[PASS] ไฟล์ของแล็บครบ (compose.yaml · api/ · web/ · db/initdb/)
[PASS] compose.yaml ประกาศครบ 3 service : api db web
[PASS] ไม่มี container_name ในไฟล์ — ปล่อยให้ compose ตั้งชื่อเป็น <project>-<service>-<n>
[PASS] มี healthcheck ครบทั้ง 3 service
[PASS] depends_on ใช้ condition: service_healthy 2 จุด (api รอ db · web รอ api)
[PASS] NFR-3 : service db ไม่มี published port ในไฟล์
[PASS] NFR-2 : ประกาศ named volume ชื่อ pgdata ไว้แล้ว
[PASS] NFR-1 : docker compose up -d --build ขึ้นครบด้วยคำสั่งเดียว
[PASS] ทั้ง 3 service ขึ้นสถานะ healthy
[PASS] ลำดับการสตาร์ตเป็น db -> api -> web ตาม depends_on: service_healthy
[PASS] NFR-3 : กล่อง db ที่รันอยู่ไม่มี port mapping ออกนอกเครื่อง
[PASS] หน้าเว็บตอบ 200 ที่ http://localhost:13191/
[PASS] หน้า /tickets · /loans · /parts ตอบ 200 ครบทั้ง 3 โมดูล
[PASS] web เรียก http://api:8000/health ด้วยชื่อ service แล้วได้ db up
[PASS] NFR-2 : down แล้ว up ข้อมูลยังอยู่ครบ (9 ใบเท่าเดิม)
[PASS] down -v แล้ว up ข้อมูลกลับไปเป็น seed ตั้งต้น (8 ใบ)
[PASS] tag repository ให้ api แล้ว IMAGE ID ยังเป็นก้อนเดิม
[PASS] tag repository ให้ web แล้ว IMAGE ID ยังเป็นก้อนเดิม
[PASS] docker save รวม image ทั้งสองก้อนเป็นไฟล์ส่งมอบได้
[PASS] ลบ image ต้นทางและชื่อสำหรับส่งมอบออกจากเครื่องแล้ว
[PASS] docker load คืน image ทั้งสองก้อนจากไฟล์ส่งมอบได้
[PASS] docker compose up -d --no-build ขึ้นครบจาก image ที่ load กลับมา
[PASS] ระบบที่ load กลับมามีสถานะ healthy ครบ 3 service
[PASS] ระบบที่ส่งมอบแบบออฟไลน์ตอบ HTTP 200
[PASS] log ของ --no-build ไม่มีบรรทัด Building
[SKIP] ไม่ตรวจ Docker Hub จริง — ตั้ง HUB_USER แล้ว tag/push ตามการทดลองที่ 8 เพื่อเปิดการตรวจ
----------------------------------------------
ALL CHECKS PASSED
exit code = 0
```

> 📝 verify ใช้ project vops5 และพอร์ต 13191 แยกจากงานของผู้เรียน ลบเฉพาะทรัพยากรของตนเอง และถือ SKIP ของ Docker Hub เป็นผลปกติ

## แก้ปัญหาที่พบบ่อย

| ข้อความจริง | สาเหตุ | วิธีแก้ |
|---|---|---|
| `no configuration file provided: not found` | รันจากโฟลเดอร์ที่ไม่มี `compose.yaml` | เข้า `005_LAB_Compose_And_Ship` แล้วสั่งใหม่ |
| `Bind for 0.0.0.0:3000 failed: port is already allocated` | มี project อื่นใช้พอร์ต 3000 | ตรวจด้วย `docker ps` แล้วหยุดเฉพาะ project ที่ตนสร้าง |
| `dependency failed to start: container campusops-db-1 is unhealthy` | healthcheck ของ db ไม่ผ่าน | อ่าน `docker compose -p campusops logs db`; หากเป็น volume ฝึกที่สร้างผิด ให้ reset ด้วย `down -v` |
| `denied: requested access to the resource is denied` | tag ไม่มีชื่อบัญชีนำหน้า หรือยังไม่ได้ login | tag เป็น `<DOCKER_USER>/campusops-api:1.0` และ login ด้วย token |
| `unauthorized: incorrect username or password` | ใช้รหัสผ่านบัญชีแทน Access Token หรือ token หมดอายุ | สร้าง token ใหม่แบบ Read & Write แล้ว login ใหม่ |
| `pull access denied for <DOCKER_USER>/campusops-api, repository does not exist or may require 'docker login'` | repository เป็น Private หรือพิมพ์ชื่อผิด | ตรวจชื่อและ Visibility; login หากตั้งใจใช้ Private |
| `429 Too Many Requests` | เกิน pull rate limit | รอรอบโควตา, login ก่อน pull และใช้ image cache ที่มีอยู่ |
| `Error response from daemon: No such image: campusops-api:latest` | สั่ง `up --no-build` ก่อน pull/tag | pull ให้ครบสองก้อนแล้ว tag กลับเป็นชื่อที่ compose.yaml ใช้ |

## เก็บกวาด

ภายในกล่องเรียน ลบ project, volume, image และ credential ที่ Docker CLI เขียนไว้ใน `/root/.docker/config.json`:

```bash
docker compose -p campusops down -v
docker image rm -f campusops-api:latest campusops-web:latest <DOCKER_USER>/campusops-api:1.0 <DOCKER_USER>/campusops-web:1.0
```

```bash
docker logout
```

`docker logout` ลบ credential ออกจากกล่องเรียน แต่ **ไม่ทำให้ Access Token หมดอายุ** จึงต้อง revoke token บน Docker Hub ด้วย หากต้องการเก็บ repository เป็นผลงาน สามารถข้ามเฉพาะขั้นลบ repository แต่ยังต้อง logout และ revoke token

### Revoke Personal Access Token

ใช้เส้นทาง avatar → Account settings → Personal access tokens ตามภาพที่ 4–6 แล้วดำเนินการต่อ:

#### ขั้นที่ ⑯ — เปิดเมนูของ token

คลิกเมนูของ token ที่สร้างสำหรับแล็บ

![รายการ token พร้อม marker ที่ปุ่มเมนู](./images/ui-hub-12-revoke-menu.png)

*ภาพที่ 20 — เลือกเฉพาะ token จาก description ของแล็บ*

#### ขั้นที่ ⑰ — เปิดหน้ายืนยันการลบ

คลิก **Delete**

![เมนู token พร้อม marker ที่ Delete](./images/ui-hub-13-revoke-delete.png)

*ภาพที่ 21 — เปิดหน้าลบ token ที่เลือก*

#### ขั้นที่ ⑱ — ยืนยันการลบ token

คลิก **Delete token** เพื่อยืนยัน

![หน้ายืนยันพร้อม marker ที่ Delete token](./images/ui-hub-14-revoke-confirm.png)

*ภาพที่ 22 — token ชั่วคราวของรอบถ่ายภาพถูก revoke จริงหลังคลิก*

### ลบ repository ทั้งสองบน Docker Hub

ทำลำดับต่อไปนี้กับ `campusops-api`:

#### ขั้นที่ ①–③ — เปิด repository API

คลิก **My Hub → Repositories → campusops-api**

![หน้า Repositories พร้อม marker สามขั้นสำหรับ API](./images/ui-hub-delete-01-api-list.png)

*ภาพที่ 23 — เปิด repository API จาก My Hub ตามลำดับไม่ข้ามขั้น*

#### ขั้นที่ ④ — เปิด Settings ของ API

คลิกแท็บ **Settings**

![หน้า API พร้อม marker ที่ Settings](./images/ui-hub-delete-02-api-repository.png)

*ภาพที่ 24 — เปิด Settings ของ campusops-api*

#### ขั้นที่ ⑤ — เริ่มลบ repository API

คลิก **Delete repository**

![หน้า Settings API พร้อม marker ที่ Delete repository](./images/ui-hub-delete-03-api-settings.png)

*ภาพที่ 25 — เริ่มขั้นลบ campusops-api*

#### ขั้นที่ ⑥–⑦ — ยืนยันชื่อและลบ repository API

พิมพ์ `campusops-api` แล้วคลิก **Delete repository forever**

![กล่องยืนยัน API พร้อม marker ที่ช่องชื่อและปุ่มลบถาวร](./images/ui-hub-delete-04-api-confirm.png)

*ภาพที่ 26 — ยืนยันชื่อให้ตรงก่อนลบ campusops-api อย่างถาวร*

ทำลำดับเดียวกันกับ `campusops-web`:

#### ขั้นที่ ⑧–⑩ — เปิด repository Web

คลิก **My Hub → Repositories → campusops-web**

![หน้า Repositories พร้อม marker สามขั้นสำหรับ Web](./images/ui-hub-delete-05-web-list.png)

*ภาพที่ 27 — เปิด repository Web จาก My Hub*

#### ขั้นที่ ⑪ — เปิด Settings ของ Web

คลิกแท็บ **Settings**

![หน้า Web พร้อม marker ที่ Settings](./images/ui-hub-delete-06-web-repository.png)

*ภาพที่ 28 — เปิด Settings ของ campusops-web*

#### ขั้นที่ ⑫ — เริ่มลบ repository Web

คลิก **Delete repository**

![หน้า Settings Web พร้อม marker ที่ Delete repository](./images/ui-hub-delete-07-web-settings.png)

*ภาพที่ 29 — เริ่มขั้นลบ campusops-web*

#### ขั้นที่ ⑬–⑭ — ยืนยันชื่อและลบ repository Web

พิมพ์ `campusops-web` แล้วคลิก **Delete repository forever**

![กล่องยืนยัน Web พร้อม marker ที่ช่องชื่อและปุ่มลบถาวร](./images/ui-hub-delete-08-web-confirm.png)

*ภาพที่ 30 — ยืนยันชื่อให้ตรงก่อนลบ campusops-web อย่างถาวร*

ออกจากกล่องเรียนและลบเฉพาะ container ของ LAB 5:

```bash
exit
docker rm -f devtools-fs-lab5
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | หน้าที่ |
|---|---|
| `docker compose -p campusops up -d --build` | build และยกระบบจาก source |
| `docker compose -p campusops up -d --no-build` | ยกระบบจาก image ที่มีอยู่โดยห้าม build |
| `docker compose -p campusops ps` | แสดงสถานะ health และ port ของทุก service |
| `docker compose -p campusops down` | ลบ container กับ network แต่รักษา volume |
| `docker compose -p campusops down -v` | ลบ volume และข้อมูล |
| `docker login -u <DOCKER_USER>` | login ด้วย Access Token |
| `docker tag <image> <DOCKER_USER>/<repository>:1.0` | เพิ่มชื่อสำหรับ Docker Hub ให้ image เดิม |
| `docker push <DOCKER_USER>/<repository>:1.0` | ส่ง image ไป Docker Hub |
| `docker pull <DOCKER_USER>/<repository>:1.0` | รับ image ลงเครื่องปลายทาง |
| `docker logout` | ลบ credential ในกล่อง แต่ไม่ revoke token |

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `docker compose -p campusops ps` แสดง healthy ครบ 3 service และ publish port เฉพาะ web
- [ ] หน้า `/`, `/tickets`, `/loans` และ `/parts` ตอบ 200
- [ ] `down` แล้วยังมี 9 ใบ แต่ `down -v` แล้วกลับเป็น seed 8 ใบ
- [ ] push `campusops-api:1.0` และ `campusops-web:1.0` สำเร็จ และทั้งสอง repository เป็น Public
- [ ] ลบ image แล้ว pull แยกสองคำสั่ง ก่อน `up -d --no-build` โดยไม่มี `Building`
- [ ] `verify.sh` แสดง `[PASS]` 26 บรรทัด, `[SKIP]` สำหรับ Hub เมื่อไม่ตั้ง `HUB_USER`, `ALL CHECKS PASSED` และ exit code 0
- [ ] logout, revoke token และตัดสินใจว่าจะเก็บหรือลบ repository เป็นผลงาน

*ผลลัพธ์ในเอกสารนี้มาจากการรันจริงวันที่ 20 สิงหาคม 2026 ภายในเครื่องเรียน `tuchsanai/devtools:2569_1`*
