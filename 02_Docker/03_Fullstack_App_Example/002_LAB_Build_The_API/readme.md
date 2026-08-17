# LAB 2 — สร้าง image ของบริการเบื้องหลัง

> โฟลเดอร์ `002_LAB_Build_The_API` · ไฟล์ของแล็บ : `api/Dockerfile` · `api/Dockerfile.bad` · `api/main.py` · `api/requirements.txt` · `api/.dockerignore` · `db/initdb/` · `.env.db` · `verify.sh`

---

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | โค้ด `api` ที่รันได้บนเครื่องคนเขียน จะกลายเป็น **image ที่ลูกค้าเอาไปรันเองได้** อย่างไร |
| **ต้องผ่านอะไรมาก่อน** | **LAB 1** (ยกฐานข้อมูลขึ้นด้วย `docker run` · `-v` · `-e`) และเรื่อง Dockerfile · layer cache · `.dockerignore` จากชุด `02_Dockerfile_Build_Run_Compose_Guide` |
| **เวลา** | ~45 นาที · การทดลอง **9 อัน** อันละ 3–5 นาที |
| **จบแล้วต้องทำได้เอง** | build image ของ `api` จาก Dockerfile จริง · ชี้จุดที่ cache แตกได้ · หา IP ของกล่องด้วย `docker inspect` · เปิดพอร์ตด้วย `-p` แล้วยิง REQ-01 · REQ-02 ผ่าน `curl` |
| **แล็บนี้ยัง *ไม่* สอน** | multi-stage ของ `web` → **LAB 3** · เรียกกันด้วย**ชื่อ**แทน IP → **LAB 4** · `compose.yaml` และการ push ขึ้น registry → **LAB 5** |

---

## ทฤษฎีก่อนลงมือ

### จุด `.` ท้ายคำสั่ง build ไม่ใช่ที่อยู่ของ Dockerfile

`docker build -t ops-api:1.0 .` — จุดตัวนั้นคือ **build context** : โฟลเดอร์ทั้งก้อนที่ถูกมัดส่งข้ามไปให้ dockerd ก่อน build จะเริ่มด้วยซ้ำ

![โฟลเดอร์ api ถูกมัดเป็น build context 28.54kB ส่งไปให้ dockerd โดยไฟล์ที่ตรงกับ .dockerignore ไม่ถูกส่ง และ COPY หยิบได้เฉพาะไฟล์ที่ส่งไปแล้วเท่านั้น](./images/theory-build-context.svg)

> 🖼 **วิธีอ่านรูปนี้:** กล่องซ้ายคือโฟลเดอร์ `api/` — กรอบเส้นประสีแดงคือไฟล์ที่ `.dockerignore` กันไว้ **ไม่ถูกส่ง** · ลูกศรกลางคือบรรทัด `transferring context` ที่เห็นใน log จริง · กล่องขวาคือ daemon ซึ่ง `COPY` หยิบได้เฉพาะของที่ส่งไปถึงมือแล้วเท่านั้น

### ลำดับบรรทัดใน Dockerfile คือเรื่องของเวลา

ทุกบรรทัดที่เปลี่ยนไฟล์กลายเป็น **layer** หนึ่งชั้น · กฎเดียวที่ต้องจำคือ **ขั้นไหนเปลี่ยน ขั้นนั้นและทุกขั้นใต้ลงไปต้องทำใหม่**

![เทียบ Dockerfile ที่เรียงถูกกับ Dockerfile.bad หลังแก้ main.py หนึ่งบรรทัด ฝั่งเรียงถูก pip install ยัง CACHED ใช้เวลา 2.035 วินาที ฝั่งเรียงผิดต้อง pip install ใหม่ 4.6 วินาที รวม 8.103 วินาที](./images/theory-layer-cache-api.svg)

> 🖼 **วิธีอ่านรูปนี้:** หา **แถวสีแรกที่ไม่ใช่ CACHED** ของแต่ละฝั่ง นั่นคือจุดที่ cache แตก · ฝั่งซ้ายจุดแตกอยู่ **ใต้** `RUN pip install` ขั้นแพงจึงรอด · ฝั่งขวาจุดแตกอยู่ **เหนือ** ขั้นนั้น ทุกอย่างใต้ลงไปจึงต้องทำใหม่

### `EXPOSE` เป็นป้าย ไม่ใช่ประตู

`EXPOSE 8000` ใน Dockerfile บอกแค่ว่า "แอปในกล่องนี้ฟังพอร์ต 8000" — คนที่หยิบ image ไปใช้จะได้รู้ว่าต้อง map พอร์ตไหน แต่มัน **ไม่เปิดทางเข้า** ให้เลย

![กรณีไม่ใส่ -p curl จากกล่องเรียนได้ exit 7 เพราะไม่มีทางเข้า ส่วนกรณีใส่ -p 8088:8000 curl ได้ผลลัพธ์ health ok และ docker port แสดงบรรทัด mapping](./images/theory-expose-vs-p.svg)

> 🖼 **วิธีอ่านรูปนี้:** สองกรณีนี้ใช้ **image เดียวกันที่มี `EXPOSE 8000` เหมือนกัน** ต่างกันแค่มี `-p` หรือไม่ · แถบล่างสอนวิธีอ่านเลข `-p 8088:8000` : ซ้ายคือพอร์ตฝั่งเครื่องที่รัน ขวาคือพอร์ตในกล่อง

### บน default bridge กล่องเรียกกันด้วยชื่อไม่ได้

กล่องที่สร้างแบบไม่ระบุ network จะไปอยู่บน **default bridge** ซึ่งไม่มี DNS ให้ — `api` จึงหาที่อยู่ของ `db` จากชื่อ `ops-db` ไม่เจอ ต้องอ่าน **IP** ด้วย `docker inspect` มาใส่ `DATABASE_URL` เอง

| สิ่งที่อยากได้ | ทำได้บน default bridge ไหม |
|---|---|
| กล่องคุยกันด้วย IP | ✅ ได้ |
| กล่องคุยกันด้วยชื่อ (`ops-db`) | ❌ ไม่ได้ |
| IP คงเดิมเมื่อสร้างกล่องใหม่ | ❌ เปลี่ยนได้ทุกครั้ง |

### สิ่งที่มักเข้าใจผิด

- **คิดว่า** จุด `.` คือที่อยู่ของ Dockerfile → **จริง ๆ** คือโฟลเดอร์ทั้งก้อนที่ถูกส่งไปให้ daemon (การทดลองที่ 1)
- **คิดว่า** แก้โค้ดทีไรก็ต้อง `pip install` ใหม่ทุกครั้ง → **จริง ๆ** ถ้าเรียงถูก ขั้นนั้นขึ้น `CACHED` (การทดลองที่ 3)
- **คิดว่า** `.dockerignore` มีไว้ลดขนาด image → **จริง ๆ** มันตัดตั้งแต่ก่อนส่ง context ไฟล์ที่ถูกกันจึงไม่ทำให้ cache แตก (การทดลองที่ 5)
- **คิดว่า** `EXPOSE 8000` = เปิดพอร์ต 8000 ให้แล้ว → **จริง ๆ** ต้องใส่ `-p` ตอน `docker run` เท่านั้น (การทดลองที่ 8)

---

## เตรียมเครื่องเรียน

### ขั้นที่ 1 — เปิดกล่องเรียน

รันบน **เครื่องของเราเอง** :

```bash
docker rm -f devtools-ops-lab2 2>/dev/null
docker run -dit --name devtools-ops-lab2 --privileged \
  -p 2239:22 -p 8088:8088 tuchsanai/devtools:2569_1
ssh root@localhost -p 2239        # password : passwd
```

### ขั้นที่ 2 — โหลดโค้ดแล็บ

**คำสั่งทุกอันหลังจากนี้พิมพ์ข้างในกล่องเรียน**

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/03_Fullstack_App_Example/002_LAB_Build_The_API
```

---

## การทดลองที่ 1 — จุด `.` ท้ายคำสั่ง build คืออะไร

**คำถาม:** เวลาสั่ง `docker build -t ops-api:1.0 .` เราส่งอะไรไปให้ Docker บ้าง

```bash
cd api
ls -a
```

✅ **สิ่งที่ต้องเห็น** — ทุกไฟล์ในโฟลเดอร์นี้คือ **build context** ที่จะถูกส่งไปให้ daemon (ลำดับการเรียงไฟล์ของแต่ละเครื่องอาจสลับกันได้) :

```
.
..
.dockerignore
Dockerfile
Dockerfile.bad
main.py
requirements.txt
smoke.sh
```

อ่าน Dockerfile ทีละบรรทัด :

```bash
cat Dockerfile
```

✅ **สิ่งที่ต้องเห็น** — 7 คำสั่งเรียงจาก "เปลี่ยนน้อย" ไป "เปลี่ยนบ่อย" (คอมเมนต์ในไฟล์จริงยาวกว่านี้) :

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> 📝 **บทเรียน:** `.` คือโฟลเดอร์ที่ยกให้ daemon ทั้งก้อน ไม่ใช่ที่อยู่ของ Dockerfile · ไฟล์นอกโฟลเดอร์นี้ `COPY` ไม่ได้เลย ต่อให้เขียน `../` ก็ตาม

---

## การทดลองที่ 2 — build ครั้งแรก ทีละขั้น

**คำถาม:** log ที่ขึ้นเป็น `[N/M]` กำลังบอกอะไรเรา

```bash
time docker build -t ops-api:1.0 .
```

✅ **สิ่งที่ต้องเห็น** — 6 ขั้นตามบรรทัดใน Dockerfile ทุกขั้นขึ้น `DONE` ไม่มี `CACHED` เลย (เวลาของแต่ละคนต่างกันตามความเร็วเน็ต) :

```
#5 [internal] load .dockerignore
#5 transferring context: 521B done
#7 [internal] load build context
#7 transferring context: 28.54kB done
#6 [1/6] FROM docker.io/library/python:3.12-slim@sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a
#6 DONE 6.9s
#8 [2/6] WORKDIR /app
#8 DONE 0.1s
#9 [3/6] COPY requirements.txt .
#9 DONE 0.1s
#10 [4/6] RUN pip install --no-cache-dir -r requirements.txt
#10 DONE 4.8s
#11 [5/6] COPY main.py .
#11 DONE 0.1s
#12 [6/6] RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
#12 DONE 0.3s
#13 naming to docker.io/library/ops-api:1.0 done

real	0m21.885s
```

> 📝 **บทเรียน:** `[4/6]` = ขั้นที่ 4 จากทั้งหมด 6 ขั้นที่สร้าง layer · `transferring context: 28.54kB` คือขนาดที่ส่งไปให้ daemon จริง ๆ · รอบแรกไม่มีอะไรให้ใช้ซ้ำ ทุกขั้นจึงต้องทำเอง

---

## การทดลองที่ 3 — แก้โค้ด 1 บรรทัดแล้ว build ใหม่

**คำถาม:** แก้ `main.py` บรรทัดเดียว ต้องติดตั้ง dependency ใหม่ทั้งชุดไหม

```bash
sed -i 's/version="1.0.0"/version="1.0.1"/' main.py
time docker build -t ops-api:1.0 .
```

✅ **สิ่งที่ต้องเห็น** — ขั้น `RUN pip install` ขึ้น **`CACHED`** และมีแค่สองขั้นล่างสุดที่ทำใหม่ :

```
#8 [2/6] WORKDIR /app
#8 CACHED
#9 [3/6] COPY requirements.txt .
#9 CACHED
#10 [4/6] RUN pip install --no-cache-dir -r requirements.txt
#10 CACHED
#11 [5/6] COPY main.py .
#11 DONE 0.1s
#12 [6/6] RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
#12 DONE 0.5s

real	0m3.220s
```

> 📝 **บทเรียน:** จาก **21.885 s เหลือ 3.220 s** เพราะ `requirements.txt` ไม่เปลี่ยน checksum ของขั้น `COPY requirements.txt .` จึงเท่าเดิม ขั้น `pip install` ที่ต่อจากมันเลยใช้ของเก่าได้

---

## การทดลองที่ 4 — เทียบกับ `Dockerfile.bad` ที่เรียงสลับกัน

**คำถาม:** ถ้าย้าย `COPY . .` ขึ้นไปก่อน `pip install` จะเสียเวลาเพิ่มเท่าไร

`Dockerfile.bad` มีคำสั่งชุดเดียวกันเป๊ะ ต่างแค่ลำดับ — build ให้มันมี cache ตั้งต้นก่อน :

```bash
docker build -f Dockerfile.bad -t ops-api-bad:1.0 .
```

✅ **สิ่งที่ต้องเห็น** — build ผ่านและได้ image ชื่อ `ops-api-bad:1.0` :

```
#12 naming to docker.io/library/ops-api-bad:1.0 done
#12 DONE 2.0s
```

ทีนี้แก้ `main.py` อีกบรรทัดเดียว แล้ว build **ไฟล์ bad** :

```bash
sed -i 's/version="1.0.1"/version="1.0.2"/' main.py
time docker build -f Dockerfile.bad -t ops-api-bad:1.0 .
```

✅ **สิ่งที่ต้องเห็น** — cache แตกตั้งแต่ `COPY . .` ทำให้ `RUN pip install` ต้องติดตั้งใหม่ทั้งชุด :

```
#9 [3/5] COPY . .
#9 DONE 0.1s
#10 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#10 DONE 4.6s

real	0m8.103s
```

แก้ไฟล์เดียวกันนี้แล้ว build **ไฟล์ที่เรียงถูก** เทียบในนาทีเดียวกัน :

```bash
time docker build -t ops-api:1.0 .
```

✅ **สิ่งที่ต้องเห็น** — ขั้นเดียวกันขึ้น `CACHED` และเวลารวมน้อยกว่าเกือบ 4 เท่า :

```
#10 [4/6] RUN pip install --no-cache-dir -r requirements.txt
#10 CACHED

real	0m2.035s
```

| Dockerfile | ขั้น `pip install` หลังแก้ `main.py` | เวลารวม (`real`) |
|---|---|---|
| `api/Dockerfile` | `CACHED` — ไม่ทำอะไรเลย | **2.035 s** |
| `api/Dockerfile.bad` | ติดตั้งใหม่ 4.6 s | **8.103 s** |

คืน `main.py` กลับเป็นของเดิมก่อนไปต่อ :

```bash
sed -i 's/version="1.0.2"/version="1.0.0"/' main.py
grep -n 'app = FastAPI' main.py
```

✅ **สิ่งที่ต้องเห็น** — บรรทัดกลับมาเป็น `1.0.0` เหมือนตอนโคลนมา :

```
94:app = FastAPI(title="CampusOps API", version="1.0.0", lifespan=lifespan)
```

> 📝 **บทเรียน:** ในแล็บนี้ต่างกัน ~4 เท่า เพราะ dependency มีแค่ 4 ตัว · ของจริงที่มี package หนัก ๆ ต่างกันหลายสิบเท่า และเราจ่ายค่านี้ **ทุกครั้งที่แก้โค้ด**

---

## การทดลองที่ 5 — `.dockerignore` กันอะไรออกจาก build context

**คำถาม:** ไฟล์ที่อยู่ในโฟลเดอร์เดียวกันแต่ไม่เกี่ยวกับแอป ถูกส่งไปด้วยไหม

```bash
cat .dockerignore
```

✅ **สิ่งที่ต้องเห็น** — รายการนี้ตัดทั้งของที่ Python สร้างเอง ของลับ และสคริปต์ทดสอบ :

```
__pycache__/
*.pyc
.venv/
.env
*.log
.git/

# สคริปต์ทดสอบไม่ต้องอยู่ใน image ของ production
smoke.sh
```

ลองสร้างไฟล์ log ขนาด 5MB ในโฟลเดอร์นี้แล้ว build ดู :

```bash
head -c 5000000 /dev/urandom > api-debug.log
du -sh .
docker build -t ops-api:1.0 . 2>&1 | grep -A2 "load build context"
```

✅ **สิ่งที่ต้องเห็น** — โฟลเดอร์โต 4.9M แต่ context ที่ส่งจริงยังเป็นหลัก **kB** :

```
4.9M	.
#7 [internal] load build context
#7 transferring context: 28.15kB done
#7 DONE 0.0s
```

```bash
rm -f api-debug.log
```

> 📝 **บทเรียน:** `.dockerignore` ทำงาน **ก่อน** context ถูกส่ง ไฟล์ที่ถูกกันจึงไม่กินเวลาส่ง ไม่หลุดเข้า image และไม่ทำให้ `COPY` แตก cache ตอนมันเปลี่ยน

---

## การทดลองที่ 6 — ยกฐานข้อมูลขึ้นแล้วหา IP ของมัน

**คำถาม:** `api` จะบอกที่อยู่ของฐานข้อมูลได้อย่างไร ในเมื่อยังไม่มี network ของเราเอง

```bash
cd ~/labwork/DevTools/02_Docker/03_Fullstack_App_Example/002_LAB_Build_The_API
docker run -d --name ops-db --env-file .env.db \
  -v ops-pgdata:/var/lib/postgresql/data \
  -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" \
  postgres:17-alpine
sleep 12 && docker exec ops-db pg_isready -U opsuser -d campusops
```

✅ **สิ่งที่ต้องเห็น** — ฐานข้อมูลพร้อมรับ connection (ครั้งแรกต้องรอโหลด image ก่อน) :

```
/var/run/postgresql:5432 - accepting connections
```

ลองให้กล่องหนึ่งเรียกอีกกล่องด้วย **ชื่อ** ดูก่อน แล้วค่อยอ่าน IP :

```bash
docker run --rm ops-api:1.0 python -c 'import socket; print(socket.gethostbyname("ops-db"))'
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ops-db
```

✅ **สิ่งที่ต้องเห็น** — ชื่อ `ops-db` แปลไม่ออก แต่ `inspect` ให้ IP มาได้ (ตัวเลข IP ของแต่ละเครื่องไม่ตรงกัน) :

```
socket.gaierror: [Errno -2] Name or service not known
172.18.0.2
```

> 📝 **บทเรียน:** บน default bridge ไม่มี DNS ให้ ชื่อกล่องจึงใช้เรียกกันไม่ได้ · ตอนนี้ต้องพึ่ง IP จาก `docker inspect` ไปก่อน — **LAB 4** จะแก้เรื่องนี้ให้จบ

---

## การทดลองที่ 7 — รัน `api` แล้วให้มันต่อฐานข้อมูลติด

**คำถาม:** ใส่ `DATABASE_URL` เป็น IP ที่เพิ่งได้มา แล้ว `/health` จะเขียวไหม

```bash
DB_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ops-db)
docker run -d --name ops-api \
  -e DATABASE_URL="postgresql://opsuser:labpass@${DB_IP}:5432/campusops" ops-api:1.0
```

✅ **สิ่งที่ต้องเห็น** — id ของกล่องที่เพิ่งสร้าง (ของแต่ละคนคนละค่า) :

```
59b0fd78de9185480ba57f5b688820dd9a483ec01b2716ab2fca9339929f0070
```

ยังไม่ได้ใส่ `-p` จึงต้องเรียกผ่าน IP ของกล่อง `api` เอง :

```bash
API_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' ops-api)
sleep 6 && curl -s http://$API_IP:8000/health; echo
```

✅ **สิ่งที่ต้องเห็น** — `/health` ยิง `SELECT 1` ไปที่ฐานข้อมูลจริงแล้วตอบกลับมา :

```
{"status":"ok","db":"up"}
```

> 📝 **บทเรียน:** `-e` ตอน `docker run` คือช่องที่ทำให้ image ก้อนเดิมชี้ไปฐานข้อมูลคนละตัวได้ · `db":"up"` แปลว่าต่อฐานข้อมูลติดจริง ไม่ใช่แค่แอปเปิดขึ้น

---

## การทดลองที่ 8 — `EXPOSE` ไม่ได้เปิดพอร์ตให้

**คำถาม:** image มี `EXPOSE 8000` อยู่แล้ว ทำไมยังเข้าจาก `localhost` ไม่ได้

```bash
docker image inspect ops-api:1.0 --format '{{json .Config.ExposedPorts}}'
docker port ops-api
curl -s -m 3 http://localhost:8088/health; echo "curl exit=$?"
```

✅ **สิ่งที่ต้องเห็น** — image ประกาศ `8000/tcp` ไว้จริง แต่ `docker port` ว่างเปล่า และ `curl` ต่อไม่ติด :

```
{"8000/tcp":{}}
curl exit=7
```

สร้างกล่องใหม่โดยเพิ่ม `-p 8088:8000` :

```bash
docker rm -f ops-api
docker run -d --name ops-api -p 8088:8000 \
  -e DATABASE_URL="postgresql://opsuser:labpass@${DB_IP}:5432/campusops" ops-api:1.0
sleep 6 && docker port ops-api && curl -s http://localhost:8088/health; echo
```

✅ **สิ่งที่ต้องเห็น** — คราวนี้มีบรรทัด mapping และเข้าถึงได้จาก `localhost` :

```
8000/tcp -> 0.0.0.0:8088
8000/tcp -> [::]:8088
{"status":"ok","db":"up"}
```

เปิดหน้าเอกสารของ API ที่ **`http://localhost:8088/docs`** ในเบราว์เซอร์บนเครื่องเราได้เลย :

```bash
curl -s -o /dev/null -w 'GET /docs -> %{http_code}\n' http://localhost:8088/docs
```

✅ **สิ่งที่ต้องเห็น** — หน้า Swagger UI ของ FastAPI ตอบ 200 :

```
GET /docs -> 200
```

> 📝 **บทเรียน:** `EXPOSE` = เอกสารในตัว image · `-p 8088:8000` = ประตูจริง (ซ้ายพอร์ตเครื่อง ขวาพอร์ตในกล่อง) · นี่คือเหตุผลที่ `db` ไม่มี `-p` ตาม NFR-3 ทั้งที่ image ของมันก็มี `EXPOSE 5432`

---

## การทดลองที่ 9 — ยิงข้อกำหนดจริงของลูกค้าด้วย `curl`

**คำถาม:** REQ-01 กับ REQ-02 ที่เขียนไว้ในเอกสาร ทำงานจริงในกล่องนี้ไหม

```bash
curl -s -w '\nHTTP %{http_code}\n' -X POST http://localhost:8088/api/tickets \
  -H 'Content-Type: application/json' \
  -d '{"asset_id":1,"title":"แอร์ห้อง 301 ไม่เย็น","detail":"เปิดแล้วมีแต่ลมร้อน","priority":"HIGH"}'
```

✅ **สิ่งที่ต้องเห็น** — **REQ-01** : ได้ `201` และใบใหม่มีสถานะ `NEW` (หมายเลข `id` และเวลาของแต่ละคนไม่ตรงกัน) :

```
{"id":9,"asset_id":1,"title":"แอร์ห้อง 301 ไม่เย็น","detail":"เปิดแล้วมีแต่ลมร้อน","priority":"HIGH","status":"NEW","assignee":null,"created_at":"2026-08-17T12:48:42.312171+00:00","closed_at":null}
HTTP 201
```

ลองข้ามลำดับสถานะจาก `NEW` ไป `DONE` ตรง ๆ :

```bash
curl -s -w '\nHTTP %{http_code}\n' -X PATCH http://localhost:8088/api/tickets/9/status \
  -H 'Content-Type: application/json' -d '{"status":"DONE"}'
```

✅ **สิ่งที่ต้องเห็น** — **REQ-02** : ถูกปฏิเสธด้วย `409` และ `code` เป็น `INVALID_TRANSITION` :

```
{"detail":"เปลี่ยนสถานะจาก NEW ไป DONE ไม่ได้","code":"INVALID_TRANSITION"}
HTTP 409
```

ยืนยันว่าใบนั้น **สถานะไม่เปลี่ยน** :

```bash
curl -s "http://localhost:8088/api/tickets?status=NEW" | python3 -c 'import sys,json
for t in json.load(sys.stdin): print(t["id"], t["status"], t["title"])'
```

✅ **สิ่งที่ต้องเห็น** — ใบหมายเลข 9 ยังอยู่ในกลุ่ม `NEW` ร่วมกับใบจาก seed :

```
1 NEW โปรเจกเตอร์ห้อง 205 ภาพวูบดับ
2 NEW แอร์ห้องแล็บ 2 ไม่เย็น
3 NEW เครื่องพิมพ์ป้อนกระดาษซ้อน
9 NEW แอร์ห้อง 301 ไม่เย็น
```

> 📝 **บทเรียน:** กฎธุรกิจของลูกค้าอยู่ใน image ไปแล้ว · แต่ที่อยู่ของฐานข้อมูลยังเป็น IP ที่เราจำเองและ **เปลี่ยนทุกครั้งที่สร้างกล่องใหม่** — **LAB 4** จะเปลี่ยนไปเรียกด้วยชื่อแทน

---

## ตรวจงานด้วย `verify.sh`

```bash
cd ~/labwork/DevTools/02_Docker/03_Fullstack_App_Example/002_LAB_Build_The_API
bash verify.sh ; echo "exit code = $?"
```

✅ **สิ่งที่ต้องเห็น** — `[PASS]` ทุกบรรทัด ปิดท้ายด้วย `ALL CHECKS PASSED` :

```
[PASS] api/Dockerfile เรียงถูก : COPY requirements.txt -> RUN pip install -> COPY main.py
[PASS] api/Dockerfile : แก้ main.py แล้วขั้น RUN pip install ยังเป็น CACHED
[PASS] api/Dockerfile.bad : ขั้น RUN pip install ถูกทำใหม่ (cache แตกจริงเพราะเรียงผิดลำดับ)
[PASS] ไฟล์ 3MB ที่ตรงกับ *.log ไม่ถูกส่งเข้า build context (transferring context: 66B done)
[PASS] รันโดยไม่ใส่ -p แล้ว docker port ไม่มีรายการ — EXPOSE ไม่ได้เปิดพอร์ตให้
[PASS] GET /health ตอบ {"status":"ok","db":"up"} ผ่านพอร์ต 18088
[PASS] REQ-01 : POST /api/tickets ได้ 201 และใบใหม่มีสถานะ NEW
[PASS] REQ-02 : สั่ง NEW -> DONE ได้ 409 INVALID_TRANSITION
----------------------------------------------
ALL CHECKS PASSED
exit code = 0
```

> 📝 ใช้เวลาราว 30 วินาที เพราะต้องยกฐานข้อมูลของตัวเองขึ้นมาทดสอบจริง · สคริปต์สร้างของด้วย prefix `vops-` และพอร์ต `18088` แล้วลบทิ้งเอง — ของที่ชื่อ `ops-` ของเราไม่ถูกแตะ

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `failed to read dockerfile: open Dockerfile: no such file or directory` | สั่ง build จากโฟลเดอร์แล็บ ไม่ใช่จาก `api/` | `cd api` ก่อน แล้วค่อย `docker build -t ops-api:1.0 .` |
| `failed to compute cache key: ... "/db/initdb": not found` | เขียน `COPY ../db/initdb` ซึ่งอยู่ **นอก** build context | ย้ายไฟล์เข้ามาในโฟลเดอร์ context หรือเปลี่ยน context ให้ครอบไฟล์นั้น |
| `Conflict. The container name "/ops-api" is already in use` | กล่องชื่อเดิมยังอยู่ | `docker rm -f ops-api` แล้วรันใหม่ |
| `Bind for 0.0.0.0:8088 failed: port is already allocated` | มีกล่องอื่นจอง 8088 อยู่แล้ว | `docker rm -f ops-api` หรือเปลี่ยนเลขซ้ายของ `-p` |
| `curl: (7) Failed to connect to localhost port 8088` | รันกล่องโดยไม่ใส่ `-p` (มีแต่ `EXPOSE`) | สร้างกล่องใหม่พร้อม `-p 8088:8000` |
| `docker logs ops-api` วน `[api] ฐานข้อมูลยังไม่พร้อม รออีก 2 วินาที...` ไม่หยุด | `DATABASE_URL` ชี้ IP ผิด หรือ `ops-db` ถูกสร้างใหม่จน IP เปลี่ยน | อ่าน IP ใหม่ด้วย `docker inspect` แล้วสร้างกล่อง `api` ใหม่ |
| `{"detail":"ข้อมูลที่ส่งมาไม่ถูกต้อง: ฟิลด์ 'body' ...","code":"VALIDATION_ERROR"}` | ลืม `-H 'Content-Type: application/json'` ตอน `curl` | ใส่ header ให้ครบทุกครั้งที่ส่ง JSON |
| ทำการทดลองที่ 4 ซ้ำ แล้วฝั่ง `bad` กลับขึ้น `CACHED` | เคย build เนื้อหาชุดนี้ไปแล้ว BuildKit จึงหยิบ cache เก่ามาใช้ | แก้ด้วยค่าที่ไม่เคยใช้ : `sed -i -E "s/version=\"[^\"]+\"/version=\"1.0.$(date +%s)\"/" main.py` แล้วคืนกลับเป็น `1.0.0` ทีหลัง |

---

## เก็บกวาด

**ในกล่องเรียน:**

```bash
docker rm -f ops-api ops-db
docker volume rm ops-pgdata
docker image rm ops-api:1.0 ops-api-bad:1.0
docker ps -a
```

✅ **สิ่งที่ต้องเห็น** — ไม่เหลือกล่องของแล็บนี้ เหลือแค่หัวตาราง :

```
ops-api
ops-db
ops-pgdata
Untagged: ops-api:1.0
Deleted: sha256:e65518f9e0f71fca7e25c74e0e90bd0dc96c42aa4f933cd8e81d5c32275a0029
Untagged: ops-api-bad:1.0
Deleted: sha256:ba0e2a6adcf945a020d38a7549ed138d5e070c48fd1e13f563150783818ad3a3
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

> 📝 เก็บ `postgres:17-alpine` กับ `python:3.12-slim` ไว้ใช้ต่อใน LAB ถัดไปได้ ไม่ต้องลบ

**ออกจากกล่องแล้วลบกล่องบนเครื่องเรา:**

```bash
exit
docker rm -f devtools-ops-lab2
docker ps -a --filter "name=^devtools-"
```

✅ ตารางสุดท้ายต้องเหลือแค่หัวตาราง

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker build -t ops-api:1.0 .` | build image จาก `Dockerfile` โดยใช้โฟลเดอร์ปัจจุบันเป็น build context |
| `docker build -f Dockerfile.bad -t ops-api-bad:1.0 .` | เลือกไฟล์ Dockerfile ด้วย `-f` เมื่อชื่อไฟล์ไม่ใช่ `Dockerfile` |
| `time docker build ...` | จับเวลา build จริง — ดูบรรทัด `real` |
| `cat .dockerignore` | ดูรายการไฟล์ที่จะ **ไม่** ถูกส่งเข้า build context |
| `docker image inspect <image> --format '{{json .Config.ExposedPorts}}'` | ดูว่า image ประกาศ `EXPOSE` พอร์ตอะไรไว้ |
| `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <กล่อง>` | อ่าน IP ของกล่องบน default bridge |
| `docker run -d --name ops-api -e DATABASE_URL=... ops-api:1.0` | ส่งค่าตั้งค่าตอนรันด้วย `-e` |
| `docker run -d --name ops-api -p 8088:8000 ops-api:1.0` | เปิดประตูจริง : พอร์ต 8088 ของเครื่อง → 8000 ในกล่อง |
| `docker port ops-api` | ดูว่ากล่องนี้ถูก map พอร์ตอะไรไว้บ้าง (ว่าง = ไม่ได้ใส่ `-p`) |
| `curl -s http://localhost:8088/health` | เช็กว่าแอปขึ้นและต่อฐานข้อมูลติดจริง |
| `docker volume rm ops-pgdata` | ลบ volume ของฐานข้อมูล (ข้อมูลหายถาวร) |

> **จำให้ครบ:** `.` = build context ทั้งก้อน · เรียง Dockerfile จาก **เปลี่ยนน้อย → เปลี่ยนบ่อย** · `.dockerignore` ตัดตั้งแต่ก่อนส่ง · `EXPOSE` เป็นป้าย `-p` เป็นประตู · default bridge เรียกด้วยชื่อไม่ได้

---

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] อธิบายได้ว่าจุด `.` ใน `docker build -t ops-api:1.0 .` คือ build context ไม่ใช่ที่อยู่ของ Dockerfile
- [ ] อ่าน log รอบแรกแล้วชี้ได้ว่า `[4/6]` คือขั้นไหนใน `api/Dockerfile`
- [ ] แก้ `main.py` 1 บรรทัด แล้วเห็นขั้น `RUN pip install` ขึ้น `CACHED` (เวลาลดจาก 21.885 s เหลือ 3.220 s)
- [ ] build `Dockerfile.bad` หลังแก้ไฟล์เดียวกัน แล้วเห็น `pip install` ทำใหม่ (8.103 s เทียบกับ 2.035 s)
- [ ] คืน `main.py` กลับเป็น `version="1.0.0"` แล้วด้วย `grep -n 'app = FastAPI' main.py`
- [ ] สร้างไฟล์ `.log` 5MB แล้ว `transferring context` ยังเป็นหลัก kB
- [ ] ยก `ops-db` ขึ้นได้ · `pg_isready` ตอบ `accepting connections` · อ่าน IP ด้วย `docker inspect` ได้
- [ ] `curl` `/health` ได้ `{"status":"ok","db":"up"}` จาก IP ของกล่อง `api` ตอนที่ยังไม่ใส่ `-p`
- [ ] รันใหม่พร้อม `-p 8088:8000` แล้ว `docker port` มีบรรทัด mapping และเปิด `http://localhost:8088/docs` ได้
- [ ] REQ-01 ได้ `201` · REQ-02 ได้ `409 INVALID_TRANSITION` · `bash verify.sh` ขึ้น `ALL CHECKS PASSED` และเก็บกวาดจนไม่เหลือกล่องของแล็บ

---

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
