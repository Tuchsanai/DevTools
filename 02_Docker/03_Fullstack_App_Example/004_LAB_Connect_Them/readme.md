# LAB 4 — ให้สามกล่องคุยกันด้วยชื่อ และปิดฐานข้อมูลจากโลกภายนอก

> โฟลเดอร์ `004_LAB_Connect_Them` · ไฟล์ของแล็บ : `api/` (ของ LAB 2) · `web/` (ของ LAB 3) · `db/initdb/` (ของ LAB 1) · `verify.sh`

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | ทำอย่างไรให้สามกล่องคุยกันด้วย **ชื่อ** แทนการจำ IP และให้ฐานข้อมูล **เข้าถึงจากภายนอกไม่ได้เลย** (NFR-3) |
| **ต้องผ่านอะไรมาก่อน** | **LAB 1** (`-e` · `-v` · อ่าน log ของ postgres) · **LAB 2** (build image ของ `api` · `EXPOSE` vs `-p` · หา IP ด้วย `docker inspect`) · **LAB 3** (build image ของ `web` · `API_BASE_URL` อ่านตอน run) |
| **เวลา** | ~45 นาที · การทดลอง **9 อัน** อันละ 3–5 นาที |
| **จบแล้วต้องทำได้เอง** | สร้าง user-defined network เอง · ยกสามกล่องขึ้นบน network เดียวกันแล้วเรียกกันด้วยชื่อ · พิสูจน์ได้ว่าฐานข้อมูลไม่มีประตูออกสู่ภายนอก · เพิ่ม network ให้กล่องที่รันอยู่แล้วด้วย `docker network connect` |
| **แล็บนี้ยัง *ไม่* สอน** | `compose.yaml` · `healthcheck` · `tag`/`push` ขึ้น registry → **LAB 5** (ดูแผนทั้งชุดที่ [`docs/01_requirements.md`](../docs/01_requirements.md)) · ไม่มี ORM / migration tool · ไม่ยุ่งกับ multi-stage อีก (LAB 3 จบไปแล้ว ใช้ image ที่ได้มาเฉย ๆ) |

---

## ทฤษฎีก่อนลงมือ

### ปัญหาที่ค้างมาจาก LAB 2 และ LAB 3 : เราต่อกล่องกันด้วย IP

สองแล็บที่ผ่านมาเราต้องทำท่านี้ทุกครั้งที่ยกระบบขึ้น

```
-e DATABASE_URL="postgresql://opsuser:labpass@$(docker inspect -f '...' ops-db):5432/campusops"
```

มันได้ผล แต่ IP เป็นเลขที่ Docker **แจกให้ตามลำดับที่กล่องเข้ามาอยู่บน network** ไม่ได้จองไว้ให้ใคร
พอฐานข้อมูลถูกสร้างใหม่ เลขก็เปลี่ยนได้ และคำสั่งที่จดไว้เมื่อวานก็ใช้ไม่ได้อีก

![แผนภาพเปรียบเทียบสองรอบการยกระบบ รอบแรก ops-db ได้ 172.19.0.2 รอบสองที่ยก api ก่อน ops-db กลายเป็น 172.19.0.3 พร้อมเทียบผลของการเขียน DATABASE_URL ด้วย IP กับด้วยชื่อกล่อง](./images/theory-name-not-ip.svg)

> 🖼 **วิธีอ่านรูปนี้:** ดูเลขในกล่อง `ops-db` สองรอบบนสุด — คำสั่งเหมือนกันทุกตัวอักษร ต่างแค่ลำดับที่ยกขึ้น · แถบล่างซ้าย/ขวาคือผลที่ตามมาของการเขียน `DATABASE_URL` สองแบบ

### user-defined network มี DNS ในตัว

`docker network create ops-net` ให้ network ชนิด **bridge** ที่มีบริการแปลชื่อกล่องเป็น IP ติดมาด้วย
กล่องที่อยู่บน network เดียวกันจึงเรียกกันด้วย **ชื่อ container** ได้ทันที ไม่ต้องรู้เลข IP ของใครเลย

![แผนภาพเทียบสองฝั่ง ฝั่งซ้าย default bridge เรียก ops-db ด้วยชื่อไม่สำเร็จ getent ตอบ exit 2 ฝั่งขวาบน ops-net getent ตอบ 172.19.0.3 และ health ตอบ db up](./images/theory-bridge-vs-usernet.svg)

> 🖼 **วิธีอ่านรูปนี้:** เทียบสองฝั่งที่ **บรรทัดคำสั่งบนสุด** — ต่างกันแค่ `--network ops-net` · แล้วเลื่อนลงมาดูกล่องผลลัพธ์ล่างสุดของแต่ละฝั่ง ซึ่งเป็นข้อความจริงที่เราจะได้เห็นเองในการทดลองที่ 1 และ 6 (ฝั่งขวาเป็นเคสที่ `ops-api` เข้ามาอยู่บน network ก่อน จึงได้ `.2` ไป และ `ops-db` ได้ `.3`)

| สิ่งที่อยากได้ | default bridge | `ops-net` (user-defined) |
|---|---|---|
| กล่องคุยกันด้วย IP | ✅ ได้ | ✅ ได้ |
| กล่องคุยกันด้วยชื่อ (`ops-db`) | ❌ ไม่ได้ | ✅ ได้ |
| เพิ่ม/ถอด network ของกล่องที่รันอยู่ | ❌ ไม่ได้ | ✅ `docker network connect` / `disconnect` |
| แยกวงจากกล่องอื่นที่ไม่เกี่ยวข้อง | ❌ ทุกกล่องปนกันหมด | ✅ เห็นเฉพาะสมาชิกของ network |

### บริการที่ไม่ต้องเข้าถึงจากภายนอก ไม่ต้องใส่ `-p`

`-p` คือการเจาะประตูจาก network ของเครื่องเข้าไปในกล่อง (LAB 2) — ถ้าไม่เจาะ ก็ไม่มีทางเข้า
ในระบบของลูกค้า มีแค่ `web` เท่านั้นที่คนนอกต้องเปิดดู ส่วน `api` และ `db` คุยกันภายใน `ops-net` พอ

![แผนภาพแสดงว่าใครเข้าถึง db ได้บ้าง กล่อง ops-web ops-api ops-db อยู่ใน ops-net โดยมีเพียง ops-web ที่มี -p 3000:3000 ส่วนเชลล์ในกล่องเรียนยิง curl localhost:5432 แล้วถูกปิดกั้น](./images/theory-nfr3-closed-db.svg)

> 🖼 **วิธีอ่านรูปนี้:** ลูกศรเขียวคือเส้นทางที่ผ่านได้ · เส้นประแดงที่ชนแท่งหนาตรงขอบ `ops-net` คือคำขอจากภายนอกที่ไปไม่ถึง `db` · สังเกตว่ากล่อง `db` เขียนว่า `5432/tcp เท่านั้น` ไม่มี `0.0.0.0:...->`

### สิ่งที่มักเข้าใจผิด

- **คิดว่า** กล่องสองกล่องบนเครื่องเดียวกันย่อมเรียกกันด้วยชื่อได้ → **จริง ๆ** บน default bridge ไม่มี DNS ให้เลย (การทดลองที่ 1)
- **คิดว่า** ต้องตั้ง DNS หรือแก้ `/etc/hosts` เอง → **จริง ๆ** แค่ `docker network create` แล้วใส่ `--network` ก็ได้ DNS มาฟรี (การทดลองที่ 2 และ 5)
- **คิดว่า** ลบกล่องแล้วสร้างใหม่ IP เดิมย่อมกลับมา → **จริง ๆ** ได้เลขตามลำดับที่เข้ามาอยู่บน network ไม่ใช่ของที่จองไว้ (การทดลองที่ 6)
- **คิดว่า** `5432/tcp` ในคอลัมน์ `PORTS` แปลว่าฐานข้อมูลเปิดให้เข้าถึงแล้ว → **จริง ๆ** นั่นคือป้าย `EXPOSE` ประตูจริงต้องมี `0.0.0.0:...->` (การทดลองที่ 8)

---

## เตรียมเครื่องเรียน

### ขั้นที่ 1 — เปิดกล่องเรียน

รันบน **เครื่องของเราเอง** :

```bash
docker rm -f devtools-ops-lab4 2>/dev/null
docker run -dit --name devtools-ops-lab4 --privileged \
  -p 2241:22 -p 8190:3000 tuchsanai/devtools:2569_1
ssh root@localhost -p 2241        # password : passwd
```

> พอร์ต `8190` ของเครื่องเราต่อเข้ากับพอร์ต `3000` ของกล่องเรียน — พอถึงการทดลองที่ 7 กล่อง `ops-web` จะจองพอร์ต `3000` ในกล่องเรียน ทำให้เปิด `http://localhost:8190` บนเบราว์เซอร์ของเราได้

### ขั้นที่ 2 — โหลดโค้ดแล็บ

**คำสั่งทุกอันหลังจากนี้พิมพ์ข้างในกล่องเรียน**

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone --depth 1 https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/03_Fullstack_App_Example/004_LAB_Connect_Them
ls
```

✅ **สิ่งที่ต้องเห็น** — ของครบทั้งสามกล่อง พร้อมเอกสารและสคริปต์ตรวจงาน รวม 6 รายการ :

```
api
db
images
readme.md
verify.sh
web
```

แล็บนี้ไม่มีอะไรให้ build ใหม่ — `api/` กับ `web/` คือของเดิมจาก LAB 2 และ LAB 3 · ดึงและทำ image ทั้งสามให้พร้อมใช้ก่อน :

```bash
docker pull -q postgres:17-alpine
docker build -q -t campusops-api:lab4 ./api
docker build -q -t campusops-web:lab4 ./web
docker images --format 'table {{.Repository}}:{{.Tag}}\t{{.Size}}' | grep -E 'campusops|postgres'
```

✅ **สิ่งที่ต้องเห็น** — ครบสาม image ก่อนเริ่มการทดลอง (ครั้งแรกใช้เวลาหลายนาทีเพราะต้องดึง base image และ `npm ci` · ค่า `sha256:` และขนาดของแต่ละคนไม่ตรงกัน) :

```
docker.io/library/postgres:17-alpine
sha256:ac85caaba2697ff266cad559a962d7e5a6f7a7cd57ef0281c89f8c04b099e2ab
sha256:8b89e5a1325975105adc713e793d98077bef2b05f0411ebe3d0d7457df43ff58
campusops-web:lab4   298MB
campusops-api:lab4   251MB
postgres:17-alpine   424MB
```

> 📝 ถ้าเพิ่งทำ LAB 2/3 มาในกล่องเรียนใบเดียวกัน สอง `docker build` นี้จะจบใน ~4 วินาทีเพราะ layer cache ยังอยู่ครบ

---

## การทดลองที่ 1 — เรียก `ops-db` ด้วยชื่อบน default bridge

**คำถาม:** ถ้าเขียน `DATABASE_URL` ด้วยชื่อกล่องโดยไม่ระบุ network `api` จะหาฐานข้อมูลเจอไหม

```bash
docker run -d --name ops-db -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass postgres:17-alpine
docker run -d --name ops-api -e DATABASE_URL="postgresql://opsuser:labpass@ops-db:5432/campusops" campusops-api:lab4
sleep 70        # api มี retry รอฐานข้อมูล 60 วินาทีตอนบูต ต้องรอให้มันยอมแพ้ก่อน
docker logs ops-api 2>&1 | grep -v 'รออีก 2 วินาที' | head -4
```

✅ **สิ่งที่ต้องเห็น** — บรรทัดกลางบอกว่ารอจนหมดเวลาแล้วก็ยัง **แปลชื่อ `ops-db` ไม่ออก** (เลข process ของแต่ละคนไม่ตรงกัน) :

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
[api] รอฐานข้อมูลไม่สำเร็จ: [Errno -2] Name or service not known
INFO:     Application startup complete.
```

ถามที่ `/health` ให้เห็นกับตาว่าแอปขึ้นแล้วแต่ต่อฐานข้อมูลไม่ได้ :

```bash
curl -s -w '\nHTTP %{http_code}\n' "http://$(docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' ops-api):8000/health"
```

✅ **สิ่งที่ต้องเห็น** — บรรทัดล่างคือ `HTTP 503` ตามสัญญาใน [`docs/02_contract.md`](../docs/02_contract.md) และ body บอกสาเหตุจริงว่าเป็นเรื่องของ **ชื่อ** ไม่ใช่รหัสผ่าน :

```
{"detail":"ฐานข้อมูลไม่ตอบสนอง: [Errno -2] Name or service not known","code":"DB_DOWN"}
HTTP 503
```

> 📝 **บทเรียน:** ทั้งสองกล่องอยู่บนเครื่องเดียวกัน เห็น IP กันด้วยซ้ำ แต่ default bridge ไม่มีบริการ DNS ชื่อ `ops-db` จึงไม่มีความหมายกับใครเลย นี่คือเหตุผลที่ LAB 2/3 ต้องใช้ IP

---

## การทดลองที่ 2 — สร้าง network ของระบบด้วย `docker network create`

**คำถาม:** สั่งสร้าง network หนึ่งบรรทัดแล้วเราได้อะไรมาบ้าง

```bash
docker network create ops-net
docker network ls
docker network inspect ops-net --format '{{.Name}} · driver={{.Driver}} · scope={{.Scope}} · subnet={{(index .IPAM.Config 0).Subnet}} · gateway={{(index .IPAM.Config 0).Gateway}}'
```

✅ **สิ่งที่ต้องเห็น** — `ops-net` ต่อท้ายของที่ Docker มีมาแต่เดิมสามอัน เป็น `DRIVER` แบบ `bridge` เหมือน `bridge` ตัวแรก และได้ช่วง IP มาเองหนึ่งช่วงโดยเราไม่ต้องกรอกอะไรเลย (`NETWORK ID` และช่วง IP ของแต่ละคนไม่ตรงกัน ขึ้นกับว่ามี network อยู่ก่อนกี่วง) :

```
27bfbc9f460a1795e81133ccf38766643a0dcbc27dea79b5458408aed46cddf1
NETWORK ID     NAME      DRIVER    SCOPE
4aeff02c8b64   bridge    bridge    local
4aed08682b4f   host      host      local
2fa1a3f5ffe4   none      null      local
27bfbc9f460a   ops-net   bridge    local
ops-net · driver=bridge · scope=local · subnet=172.19.0.0/16 · gateway=172.19.0.1
```

> 📝 **บทเรียน:** `bridge` ตัวแรกในตารางคือ default bridge ที่กล่องในการทดลองที่ 1 ไปอยู่ · `ops-net` เป็น driver เดียวกันแต่เป็นของที่ **เราสร้างเอง** จึงได้ DNS ในตัวมาด้วย

---

## การทดลองที่ 3 — ยกฐานข้อมูลขึ้นบน `ops-net` โดยไม่ใส่ `-p`

**คำถาม:** ฐานข้อมูลที่ไม่เปิดพอร์ตออกมาเลย จะยังขึ้นและทำงานได้ไหม

```bash
docker rm -f ops-db ops-api
docker run -d --name ops-db --network ops-net -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
sleep 12
docker ps --filter name=ops-db --format 'table {{.Names}}\t{{.Networks}}\t{{.Status}}\t{{.Ports}}'
```

✅ **สิ่งที่ต้องเห็น** — กล่องขึ้นปกติ · `NETWORKS` เป็น `ops-net` · `PORTS` มีแค่ `5432/tcp` **ไม่มี** `0.0.0.0:...->` (เวลาที่ขึ้นของแต่ละคนต่างกัน) :

```
NAMES     NETWORKS   STATUS          PORTS
ops-db    ops-net    Up 12 seconds   5432/tcp
```

> 📝 **บทเรียน:** `-v ops-pgdata:...` และ `-v "$PWD/db/initdb:..."` คือของที่ LAB 1 สอนไว้ทั้งคู่ ของใหม่ในบรรทัดนี้มีแค่ `--network ops-net` เท่านั้น · NFR-3 ได้มาจากการ **ไม่พิมพ์** `-p` ไม่ใช่จากการตั้งค่าอะไรเพิ่ม

---

## การทดลองที่ 4 — ให้ `api` ต่อฐานข้อมูลด้วยชื่อกล่อง

**คำถาม:** `DATABASE_URL` ที่ไม่มีเลข IP อยู่เลย ใช้งานได้จริงไหม

```bash
docker run -d --name ops-api --network ops-net -e DATABASE_URL="postgresql://opsuser:labpass@ops-db:5432/campusops" campusops-api:lab4
sleep 8
API_IP=$(docker inspect -f '{{index .NetworkSettings.Networks "ops-net" "IPAddress"}}' ops-api)
curl -s "http://$API_IP:8000/health"; echo
```

✅ **สิ่งที่ต้องเห็น** — คำสั่งเดียวกับการทดลองที่ 1 เป๊ะ ต่างแค่ `--network ops-net` แล้วคราวนี้ `db` **ขึ้น** :

```
{"status":"ok","db":"up"}
```

> 📝 **บทเรียน:** `ops-api` ยังไม่ต้องมี `-p` เพราะเราถามผ่าน IP ภายใน network · ค่า `DATABASE_URL` ก้อนนี้คือค่าที่จะยกไปเขียนใน `compose.yaml` ของ LAB 5 ได้ตรง ๆ โดยไม่ต้องแก้

---

## การทดลองที่ 5 — ใครเป็นคนแปลชื่อเป็น IP

**คำถาม:** ในกล่อง `ops-api` ชื่อ `ops-db` ถูกแปลเป็นเลขอะไร และตรงกับของจริงไหม

```bash
docker exec ops-api getent hosts ops-db
docker inspect -f '{{index .NetworkSettings.Networks "ops-net" "IPAddress"}}' ops-db
```

✅ **สิ่งที่ต้องเห็น** — สองบรรทัดให้เลข **เดียวกัน** (เลขของแต่ละคนไม่ตรงกัน ขึ้นกับช่วง IP ที่ network ได้มา) :

```
172.19.0.2      ops-db
172.19.0.2
```

> 📝 **บทเรียน:** `getent hosts` คือการถาม DNS จากในกล่อง — คำตอบมาจากบริการแปลชื่อของ `ops-net` เอง ไม่ใช่ไฟล์ `/etc/hosts` ที่เราไปแก้ และไม่ใช่ DNS ของอินเทอร์เน็ต

---

## การทดลองที่ 6 — สร้างฐานข้อมูลใหม่แล้ว IP เปลี่ยน

**คำถาม:** ยกระบบขึ้นใหม่โดยสลับลำดับ (api ก่อน db) แล้ว `api` ที่ยังใช้คำสั่งเดิมจะหาฐานข้อมูลเจอไหม

```bash
docker rm -f ops-api ops-db && docker run -d --name ops-api --network ops-net -e DATABASE_URL="postgresql://opsuser:labpass@ops-db:5432/campusops" campusops-api:lab4
docker run -d --name ops-db --network ops-net -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine
sleep 15
docker exec ops-api getent hosts ops-db
```

✅ **สิ่งที่ต้องเห็น** — เลขของ `ops-db` **ไม่ใช่ `172.19.0.2` อีกแล้ว** เพราะรอบนี้ `ops-api` เข้ามาอยู่บน network ก่อนจึงได้เลขนั้นไป :

```
172.19.0.3      ops-db
```

```bash
curl -s "http://$(docker inspect -f '{{index .NetworkSettings.Networks "ops-net" "IPAddress"}}' ops-api):8000/health"; echo
```

✅ **สิ่งที่ต้องเห็น** — ระบบยังทำงานได้ทั้งที่เลขเปลี่ยน เพราะไม่มีใครจดเลขไว้เลย :

```
{"status":"ok","db":"up"}
```

> 📝 **บทเรียน:** นี่คือคุณค่าจริงของ user-defined network — ถ้าเขียน `DATABASE_URL` ด้วย IP แบบ LAB 2 รอบนี้จะชี้ไปที่ `ops-api` เอง และต้องสร้างกล่อง `api` ใหม่ทุกครั้งที่ `db` เกิดใหม่

---

## การทดลองที่ 7 — ยกหน้าเว็บขึ้นแล้วเปิดดูของจริง

**คำถาม:** `web` ที่ชี้ `API_BASE_URL` ไปที่ชื่อ `ops-api` เรนเดอร์ข้อมูลจากฐานข้อมูลได้ครบไหม

```bash
docker run -d --name ops-web --network ops-net -p 3000:3000 -e API_BASE_URL="http://ops-api:8000" campusops-web:lab4
sleep 8
for p in / /tickets /loans /parts; do curl -s -o /dev/null -w "GET $p -> HTTP %{http_code} · %{size_download} ไบต์\n" "http://localhost:3000$p"; done
```

✅ **สิ่งที่ต้องเห็น** — ทั้งสี่หน้าตอบ `200` และมีเนื้อหาจริงหลักหมื่นไบต์ (ตัวเลขไบต์จะตรงกันทุกคนตราบใดที่ยังใช้ seed เดิม · จะขยับทันทีที่แก้ข้อมูลในฐานข้อมูล) :

```
GET / -> HTTP 200 · 31260 ไบต์
GET /tickets -> HTTP 200 · 71881 ไบต์
GET /loans -> HTTP 200 · 46734 ไบต์
GET /parts -> HTTP 200 · 70876 ไบต์
```

เปิดในเบราว์เซอร์บนเครื่องเราที่ **`http://localhost:8190`** ได้เลย :

![หน้าสรุปของ CampusOps ที่เปิดจากเบราว์เซอร์จริง แสดงการ์ดจำนวนใบแจ้งซ่อมตามสถานะ รอรับเรื่อง 3 มอบหมายแล้ว 2 กำลังซ่อม 1 ปิดงานแล้ว 2 ครุภัณฑ์ถูกยืมอยู่ 2 พร้อมบล็อกงานค้างเกินกำหนดและอะไหล่ต่ำกว่าจุดสั่งซื้อ](./images/app-via-service-name.png)

> 🖼 **วิธีอ่านรูปนี้:** ตัวเลขบนการ์ดทั้งห้าใบมาจากฐานข้อมูลจริงผ่านสาย `web → ops-api → ops-db` ที่เป็น **ชื่อล้วน ๆ** · ถ้า DNS ของ `ops-net` ไม่ทำงาน หน้านี้จะขึ้น error ทันทีเพราะทุกหน้าเรนเดอร์ฝั่ง server · บรรทัดล่างสุดของหน้าย้ำว่าหน้าเว็บคุยกับบริการเบื้องหลังผ่านเครือข่ายภายในของ Docker เท่านั้น

> 📝 **บทเรียน:** `-p 3000:3000` มีอยู่ที่กล่องเดียวคือ `web` · เบราว์เซอร์ไม่เคยเรียก `api` ตรง ๆ (ทุกหน้าเป็น server component ตาม [`docs/02_contract.md`](../docs/02_contract.md)) จึงไม่ต้องเปิดพอร์ตให้ `api` เลย

---

## การทดลองที่ 8 — ฐานข้อมูลถูกปิดจากภายนอกจริงไหม

**คำถาม:** มีทางไหนที่คนนอก `ops-net` จะยิงเข้าพอร์ต 5432 ได้บ้าง

```bash
docker port ops-db; echo "(ว่างเปล่า = ไม่มีพอร์ตถูก publish)"
curl -sS -m 5 http://localhost:5432; echo "curl exit = $?"
docker ps --filter name=ops- --format 'table {{.Names}}\t{{.Ports}}'
```

✅ **สิ่งที่ต้องเห็น** — `docker port ops-db` **ไม่คืนบรรทัดใดเลย** · ยิงจากเชลล์ของกล่องเรียนซึ่งอยู่นอก `ops-net` ก็ต่อไม่ติด (`exit 7`) · และในตารางมีแค่ `ops-web` ที่มี `0.0.0.0:...->` :

```
(ว่างเปล่า = ไม่มีพอร์ตถูก publish)
curl: (7) Failed to connect to localhost port 5432 after 0 ms: Couldn't connect to server
curl exit = 7
NAMES     PORTS
ops-web   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
ops-db    5432/tcp
ops-api   8000/tcp
```

> 📝 **บทเรียน:** NFR-3 ผ่านโดยไม่ต้องตั้ง firewall หรือแก้ `pg_hba.conf` เลย — แค่ไม่ publish พอร์ต · `5432/tcp` ที่เห็นในตารางคือป้าย `EXPOSE` ของ image ไม่ใช่ประตูที่เปิดจริง

---

## การทดลองที่ 9 — ดูสมาชิกของ network และเพิ่มกล่องเข้าทีหลัง

**คำถาม:** ตอนนี้มีใครอยู่บน `ops-net` บ้าง และกล่องที่รันไปแล้วยังเข้ามาร่วมวงได้ไหม

```bash
docker network inspect ops-net --format '{{range .Containers}}{{.Name}} → {{.IPv4Address}}
{{end}}'
```

✅ **สิ่งที่ต้องเห็น** — ครบสามกล่องของระบบพร้อมเลขที่แต่ละกล่องได้รับ (ลำดับและเลขของแต่ละคนไม่ตรงกัน) :

```
ops-db → 172.19.0.3/16
ops-web → 172.19.0.4/16
ops-api → 172.19.0.2/16
```

ทีนี้สร้างกล่องเครื่องมือไว้บน default bridge ก่อน แล้วค่อยพามันเข้า `ops-net` ทีหลัง :

```bash
docker run -d --name ops-tools postgres:17-alpine sleep 600
docker exec ops-tools getent hosts ops-db; echo "ก่อน connect : exit = $?"
docker network connect ops-net ops-tools
docker exec ops-tools psql "postgresql://opsuser:labpass@ops-db:5432/campusops" -c 'SELECT count(*) FROM tickets;'
```

✅ **สิ่งที่ต้องเห็น** — ก่อน connect แปลชื่อไม่ได้ (`exit = 2`) · หลัง connect ต่อฐานข้อมูลด้วย **ชื่อ** ได้ทันทีโดยไม่ต้องสร้างกล่องใหม่ :

```
ก่อน connect : exit = 2
 count
-------
     8
(1 row)
```

> 📝 **บทเรียน:** `docker network connect` แก้ network ของกล่องที่กำลังรันได้ (default bridge ทำแบบนี้ไม่ได้) · กล่องหนึ่งอยู่ได้หลาย network พร้อมกัน ซึ่งเป็นวิธีเปิดวงเฉพาะกิจให้เครื่องมือดูแลระบบ

---

## ตรวจงานด้วย `verify.sh`

สคริปต์ **build image ของตัวเอง** (`vops4-api:verify` · `vops4-web:verify`) แล้วยกฐานข้อมูลขึ้นสองรอบ จึงเงียบไปพักหนึ่งระหว่างทาง — ถ้าเพิ่งทำการทดลองจบใหม่ ๆ layer cache ยังอยู่ครบจะใช้เวลา ~30 วินาที · ถ้า cache ว่างจะนานหลายนาที

```bash
bash verify.sh ; echo "exit code = $?"
```

✅ **สิ่งที่ต้องเห็น** — แบนเนอร์สามบรรทัด แล้ว `[PASS]` ครบ **19 บรรทัด** ปิดท้ายด้วย `ALL CHECKS PASSED` และ `exit code = 0` (เลข IP ของแต่ละคนไม่ตรงกัน) :

```
==============================================
 LAB 4 — Connect Them (network + ชื่อ) : verify
==============================================
[PASS] ต่อกับ Docker daemon ได้
[PASS] ไฟล์ของแล็บครบ (api/ · web/ · db/initdb/)
[PASS] docker network create ได้ network ชนิด bridge (vops4-net)
[PASS] ยกกล่องฐานข้อมูล vops4-db ขึ้นบน vops4-net ได้ (ไม่ใส่ -p)
[PASS] ฐานข้อมูลรัน init script เสร็จและพร้อมรับ connection แล้ว
[PASS] docker port vops4-db ไม่คืนบรรทัดใดเลย — ไม่มีพอร์ตถูก publish (NFR-3)
[PASS] NetworkSettings.Ports ของ vops4-db ไม่มี HostPort ผูกไว้เลย
[PASS] ยิง curl http://localhost:5432 จากกล่องเรียนแล้วต่อไม่ติด (ตามที่ NFR-3 ต้องการ)
[PASS] ยกกล่อง vops4-api ขึ้นบน vops4-net โดยใส่ชื่อกล่อง vops4-db ใน DATABASE_URL
[PASS] /health ตอบ db up ทั้งที่ DATABASE_URL ไม่มีเลข IP อยู่เลย
[PASS] getent hosts vops4-db ในกล่อง api ได้ 172.20.0.2 ตรงกับ IP จริงของ vops4-db
[PASS] กล่องบน default bridge แปลชื่อ vops4-db ไม่ได้ (ยืนยันว่า default bridge ไม่มี DNS)
[PASS] docker network connect กับกล่องที่รันอยู่แล้ว ทำให้แปลชื่อ vops4-db ได้ทันที
[PASS] สร้าง vops4-db ใหม่แล้ว ชื่อเดิมยังชี้ไปที่กล่องใหม่ได้ถูกต้อง (172.20.0.2)
[PASS] api กล่องเดิม (ไม่ได้สร้างใหม่ ไม่ได้แก้ค่าใด ๆ) ต่อ db ตัวใหม่ได้เอง
[PASS] หน้าเว็บตอบ 200 โดยตั้ง API_BASE_URL=http://vops4-api:8000 (ชื่อล้วน ๆ)
[PASS] หน้าแรกมีเนื้อหาที่วิ่งครบสายจริง : เบราว์เซอร์ → web → api → db
[PASS] หน้า /tickets · /loans · /parts ตอบ 200 ครบ
[PASS] docker network inspect เห็นครบทั้ง vops4-db · vops4-api · vops4-web
----------------------------------------------
ALL CHECKS PASSED
exit code = 0
```

> 📝 สคริปต์สร้างของของตัวเองด้วย prefix `vops4-` ทั้งหมด (network `vops4-net` · กล่อง `vops4-db` · `vops4-api` · `vops4-web` · `vops4-probe`) แล้วลบทิ้งเมื่อจบ — กล่อง `ops-` และ network `ops-net` ของเราจะไม่ถูกแตะ

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `[api] รอฐานข้อมูลไม่สำเร็จ: [Errno -2] Name or service not known` | `api` กับ `db` ไม่ได้อยู่บน network เดียวกัน (กล่องใดกล่องหนึ่งลืม `--network ops-net`) | `docker rm -f ops-api` แล้ว `docker run` ใหม่พร้อม `--network ops-net` · ตรวจสมาชิกด้วย `docker network inspect ops-net` |
| `Error response from daemon: network with name ops-net already exists` | สั่ง `docker network create ops-net` ซ้ำ | ใช้ของเดิมต่อได้เลย หรือลบก่อนด้วย `docker network rm ops-net` แล้วค่อยสร้างใหม่ |
| `docker: Error response from daemon: failed to set up container networking: network ops-network not found` | พิมพ์ชื่อ network ผิด (`ops-network` ไม่ใช่ `ops-net`) | `docker network ls` ดูชื่อจริง แล้วแก้ค่าหลัง `--network` ให้ตรง |
| `Error response from daemon: error while removing network: network ops-net has active endpoints (name:"ops-db" id:"a2106b852805", name:"ops-web" id:"8ef74b558ace", ...)` | ยังมีกล่องต่ออยู่บน network นั้น | `docker rm -f ops-web ops-api ops-db ops-tools` ให้หมดก่อน แล้วค่อย `docker network rm ops-net` |
| `Error response from daemon: endpoint with name ops-tools already exists in network ops-net` | สั่ง `docker network connect` กล่องเดิมเข้า network เดิมซ้ำ | ข้ามได้เลย ไม่ต้องแก้ · ตรวจว่าอยู่แล้วจริงด้วย `docker network inspect ops-net` |
| `psql: error: could not translate host name "ops-db" to address: Try again` | กล่องที่ยิง `psql` ไม่ได้อยู่บน `ops-net` | ตอนสร้างใส่ `--network ops-net` หรือกล่องที่รันอยู่แล้วใช้ `docker network connect ops-net <ชื่อกล่อง>` |
| `⨯ TypeError: fetch failed` ตามด้วย `[cause]: Error: getaddrinfo EAI_AGAIN api` ใน `docker logs ops-web` | `API_BASE_URL` ชี้ไปชื่อที่ไม่มีอยู่บน network (เช่น `http://api:8000` ตามชื่อ service ใน contract แต่กล่องจริงชื่อ `ops-api`) | สร้าง `ops-web` ใหม่โดยตั้ง `-e API_BASE_URL="http://ops-api:8000"` ให้ตรงกับ **ชื่อกล่อง** จริง |
| `docker: Error response from daemon: failed to set up container networking: driver failed programming external connectivity on endpoint ops-web (...): Bind for 0.0.0.0:3000 failed: port is already allocated` | มีกล่องอื่นในกล่องเรียนจองพอร์ต 3000 อยู่แล้ว | `docker ps --filter publish=3000` หาตัวที่จองอยู่ แล้ว `docker rm -f` หรือเปลี่ยนเลขฝั่งซ้ายของ `-p` |

---

## เก็บกวาด

**ในกล่องเรียน:**

```bash
docker rm -f ops-web ops-api ops-db ops-tools
docker network rm ops-net
docker volume rm ops-pgdata
docker network ls
```

> 📝 ต้องลบกล่องให้หมดก่อนเสมอ ไม่งั้น `docker network rm` จะฟ้อง `has active endpoints` · ในตารางสุดท้ายต้องเหลือแค่ `bridge` · `host` · `none` ซึ่งเป็นของที่ Docker มีมาแต่แรกและลบไม่ได้

**ออกจากกล่องแล้วลบกล่องบนเครื่องเรา:**

```bash
exit
docker rm -f devtools-ops-lab4
docker ps -a --filter "name=^devtools-"
```

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker network create ops-net` | สร้าง user-defined network ชนิด bridge ที่มี DNS ในตัว |
| `docker network ls` | ดู network ทั้งหมด (`bridge` · `host` · `none` คือของที่มีมาแต่แรก) |
| `docker network inspect ops-net` | ดูรายละเอียด network : ช่วง IP · gateway · รายชื่อกล่องที่อยู่ในวง |
| `docker run --network ops-net ...` | สร้างกล่องให้เข้าไปอยู่บน network ที่เราสร้างไว้ตั้งแต่แรก |
| `docker network connect ops-net <ชื่อกล่อง>` | พากล่องที่ **รันอยู่แล้ว** เข้ามาร่วมวง (กล่องเดียวอยู่ได้หลาย network) |
| `docker network disconnect ops-net <ชื่อกล่อง>` | ถอดกล่องออกจากวง |
| `docker network rm ops-net` | ลบ network (ต้องไม่มีกล่องต่ออยู่) |
| `docker exec <กล่อง> getent hosts <ชื่อกล่อง>` | ถาม DNS จากในกล่องว่าชื่อนี้แปลเป็น IP อะไร |
| `docker port <กล่อง>` | ดูว่ากล่องนี้ publish พอร์ตอะไรออกมาบ้าง (ว่าง = ไม่มีทางเข้าจากภายนอก) |
| `docker ps --format 'table {{.Names}}\t{{.Networks}}\t{{.Ports}}'` | ดูพร้อมกันว่ากล่องไหนอยู่ network ไหน และเปิดพอร์ตอะไรจริง |

> **จำ 3 อย่าง:** default bridge ไม่มี DNS · บน network ที่เราสร้างเองให้เรียกกันด้วย **ชื่อกล่อง** เสมอ · ไม่มี `-p` = ไม่มีประตูจากภายนอก

---

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] บน default bridge : `docker logs ops-api 2>&1 | grep -v 'รออีก 2 วินาที' | head -4` เจอ `[api] รอฐานข้อมูลไม่สำเร็จ: [Errno -2] Name or service not known`
- [ ] `curl .../health` ของกล่องเดียวกันตอบ `{"detail":"ฐานข้อมูลไม่ตอบสนอง: ...","code":"DB_DOWN"}`
- [ ] `docker network create ops-net` แล้ว `docker network ls` เห็น `ops-net` เป็น `DRIVER` แบบ `bridge`
- [ ] `docker ps --filter name=ops-db --format 'table {{.Names}}\t{{.Networks}}\t{{.Status}}\t{{.Ports}}'` แสดง `NETWORKS` = `ops-net` และ `PORTS` มีแค่ `5432/tcp` (คอลัมน์ `NETWORKS` ไม่มีในรูปแบบ default ของ `docker ps` ต้องใส่ `--format` เอง)
- [ ] ตั้ง `DATABASE_URL=...@ops-db:5432/...` (ไม่มีเลข IP) แล้ว `/health` ตอบ `{"status":"ok","db":"up"}`
- [ ] `docker exec ops-api getent hosts ops-db` ได้เลขตรงกับ `docker inspect` ของ `ops-db`
- [ ] ยกใหม่โดยสลับลำดับ (api ก่อน db) แล้ว `getent hosts ops-db` ได้ **เลขใหม่** แต่ `/health` ยังตอบ `db up`
- [ ] `-e API_BASE_URL="http://ops-api:8000"` แล้วทั้ง 4 หน้าตอบ `200` และเปิด `http://localhost:8190` เห็นการ์ดสรุปจริง
- [ ] `docker port ops-db` ไม่มีบรรทัดใดเลย · `curl -sS -m 5 http://localhost:5432` ได้ `curl exit = 7` · แต่ `/health` ยัง `db up`
- [ ] `bash verify.sh ; echo "exit code = $?"` ขึ้น `ALL CHECKS PASSED` และ `exit code = 0`

---

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
