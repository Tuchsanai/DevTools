# LAB 4 — Environment Variables · ARG vs ENV

> โฟลเดอร์ `004_LAB_ENV_ARG_Config` · ไฟล์ของแล็บ : `Dockerfile` · `app.py` · `requirements.txt` · `.env.lab` · `.dockerignore` · `Dockerfile.args` · `Dockerfile.argfrom` · `Dockerfile.leak` · `verify.sh`

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | ใส่ค่าเดียวกันไว้ทั้ง `ENV`, `--env-file` และ `-e` — **แอปจะเห็นค่าไหน** |
| **ต้องผ่านอะไรมาก่อน** | **LAB 1** (build/run และการใช้ `-e` ครั้งแรก) |
| **เวลา** | ~35 นาที · การทดลอง **11 อัน** อันละ 2–4 นาที |
| **จบแล้วต้องทำได้เอง** | รัน image **ตัวเดียว** เป็น dev/staging/production โดยไม่ build ใหม่ · แยก `ARG` ออกจาก `ENV` · รู้ว่า secret รั่วออกทางไหน |
| **แล็บนี้ยัง *ไม่* สอน** | การส่ง config ผ่าน Compose → **LAB 7** |

---

## ทฤษฎีก่อนลงมือ

### `ARG` กับ `ENV` อยู่คนละช่วงเวลา

![เส้นเวลาแสดงอายุของ ARG และ ENV ตั้งแต่ช่วง build ผ่าน image จนถึง container ตอน run](./images/theory-arg-env-timeline.svg)

> 🖼 **วิธีอ่านรูปนี้:** `ARG` สิ้นอายุเมื่อ build จบ (แต่ค่าอาจค้างใน `docker history`) ส่วน `ENV` เดินทางต่อไปกับ image จนถึง container

| | `ARG` | `ENV` |
|---|---|---|
| มีผลช่วงไหน | **เฉพาะตอน build** | **build และ run** |
| ตั้งค่าอย่างไร | `--build-arg` | `ENV` ใน Dockerfile หรือ `-e` ตอน run |
| ใครอ่านได้ | คำสั่ง `RUN` ระหว่าง build | `RUN` และ **แอปใน container ตอนรัน** |
| ใส่ secret ได้ไหม | **ไม่ได้** — เห็นใน `docker history` | **ไม่ได้** — เห็นใน image metadata |

### ค่ามาจาก 3 ชั้น ชั้นที่ใกล้เวลารันที่สุดชนะ

![ลำดับความสำคัญของ ENV ใน Dockerfile ไฟล์ environment และค่าแบบ -e ที่รวมเป็นค่าจริงของโปรเซส](./images/theory-env-precedence.svg)

> 🖼 **วิธีอ่านรูปนี้:** สามชั้นไหลลงมารวมเป็นกล่อง "ค่าที่โปรเซสเห็นจริง" · ชั้น `-e` ทับ **เฉพาะชื่อที่ซ้ำ** ไม่ได้ลบค่าอื่นทิ้ง

```
ENV ใน Dockerfile   <   --env-file   <   -e
   (ค่า default)        (หลายค่า)      (ทีละค่า)
```

### สิ่งที่มักเข้าใจผิด

- **คิดว่า** `-e` หนึ่งตัวทำให้ค่าจาก `--env-file` หายทั้งชุด → **จริง ๆ** ทับเฉพาะ key ชื่อเดียวกัน
- **คิดว่า** `ARG` หายหลัง build จึงใช้เก็บ token ได้ → **จริง ๆ** ค่าค้างใน history (การทดลองที่ 9)
- **คิดว่า** สลับตำแหน่ง `-e` กับ `--env-file` บนบรรทัดคำสั่งแล้วผลเปลี่ยน → **จริง ๆ** Docker อ่านไฟล์ให้จบก่อนแล้วค่อยวาง `-e` ทับเสมอ

---

## เตรียมเครื่องเรียน

### ขั้นที่ 1 — เปิดกล่องเรียน

รันบน **เครื่องของเราเอง** :

```bash
docker rm -f devtools-df-lab4 2>/dev/null
docker run -dit --name devtools-df-lab4 --privileged \
  -p 2234:22 -p 8184:8184 tuchsanai/devtools:2569_1
ssh root@localhost -p 2234        # password : passwd
```

### ขั้นที่ 2 — โหลดโค้ดแล็บ

**คำสั่งทุกอันหลังจากนี้พิมพ์ข้างในกล่องเรียน**

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide/004_LAB_ENV_ARG_Config
ls -a
```

> 📝 ต้องใส่ `-a` เพราะไฟล์สำคัญของแล็บนี้ขึ้นต้นด้วยจุด (`.env.lab`, `.dockerignore`)

---

## การทดลองที่ 1 — build image ที่มี `ENV` ฝังอยู่

**คำถาม:** ค่า default ของแอปมาจากไหน

```bash
cat Dockerfile
```

✅ **สิ่งที่ต้องเห็น** — มี `ENV` **5 บรรทัด** ซึ่งคือ **ชั้นที่ 1** ของแล็บนี้ :

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .

ENV APP_ENV=development
ENV APP_VERSION=1.0.0
ENV GREETING="Hello"
ENV FEATURE_FLAGS="beta-ui"
ENV LOG_LEVEL=info

EXPOSE 8184
CMD ["python","app.py"]
```

```bash
docker build -t lab4-config:1.0 .
```

> 📝 สังเกตว่า **ไม่มี `COPY .env`** และไม่มี `COPY . .` — ตั้งใจให้เฉพาะ `requirements.txt` กับ `app.py` เข้า image เท่านั้น · ฝั่ง `app.py` อ่านค่าด้วย `os.environ.get(...)` ธรรมดา ไม่มีเวทมนตร์อะไรเลย

---

## การทดลองที่ 2 — ชั้นที่ 1 : `ENV` ใน Dockerfile

**คำถาม:** ไม่ส่งอะไรเลย container จะเห็นค่าอะไร

```bash
docker rm -f cfg-a 2>/dev/null
docker run -d --name cfg-a lab4-config:1.0
docker exec cfg-a env | grep -E "^(APP_|GREETING|LOG_LEVEL|DATABASE_HOST)" | sort
```

✅ **สิ่งที่ต้องเห็น** — ตรงกับบรรทัด `ENV` ใน Dockerfile เป๊ะ และ **ไม่มี `DATABASE_HOST`** :

```
APP_ENV=development
APP_VERSION=1.0.0
GREETING=Hello
LOG_LEVEL=info
```

> 📝 `docker exec cfg-a env` = ดู "ค่าที่ container เห็นจริง" ตรงที่สุด · **สิ่งที่เพิ่งพิสูจน์:** `ENV` = ค่า default ที่เดินทางไปกับ image ใครดึงไปรันที่ไหนก็ได้ชุดนี้

---

## การทดลองที่ 3 — ชั้นที่ 2 : `--env-file`

**คำถาม:** ค่าจากไฟล์ทับค่า default ได้ไหม

```bash
cat .env.lab
```

```
APP_ENV=staging
APP_VERSION=2.0.0-rc1
FEATURE_FLAGS=beta-ui,dark-mode,metrics
GREETING=สวัสดีจาก env-file
LOG_LEVEL=debug
DATABASE_HOST=db.staging.internal
```

```bash
docker rm -f cfg-b 2>/dev/null
docker run -d --name cfg-b --env-file .env.lab lab4-config:1.0
docker exec cfg-b env | grep -E "^(APP_|GREETING|LOG_LEVEL|DATABASE_HOST)" | sort
```

✅ **สิ่งที่ต้องเห็น** — ทุกค่าถูก **ทับ** และ `DATABASE_HOST` ที่ image ไม่มี **โผล่ขึ้นมาใหม่** :

```
APP_ENV=staging
APP_VERSION=2.0.0-rc1
DATABASE_HOST=db.staging.internal
GREETING=สวัสดีจาก env-file
LOG_LEVEL=debug
```

> 📝 รูปแบบไฟล์คือ `KEY=value` บรรทัดละตัว **ห้ามมีช่องว่างรอบ `=`** และ **ไม่ต้องใส่เครื่องหมายคำพูด** (ใส่แล้วจะกลายเป็นส่วนหนึ่งของค่าจริง ๆ) · `--env-file` อ่านไฟล์จาก **เครื่องที่พิมพ์คำสั่ง** ไม่ใช่จากใน image

---

## การทดลองที่ 4 — ชั้นที่ 3 : `-e` ใครชนะใคร

**คำถาม:** ใส่ทั้ง `--env-file` และ `-e` พร้อมกัน จะได้ค่าไหน

```bash
docker rm -f cfg-c 2>/dev/null
docker run -d --name cfg-c --env-file .env.lab \
  -e APP_ENV=production -e APP_VERSION=3.0.0 lab4-config:1.0
docker exec cfg-c env | grep -E "^(APP_|GREETING|LOG_LEVEL|DATABASE_HOST)" | sort
```

✅ **สิ่งที่ต้องเห็น** — `-e` ชนะทั้งคู่ แต่ตัวที่ `-e` **ไม่ได้แตะ** ยังเป็นค่าจากไฟล์ :

```
APP_ENV=production
APP_VERSION=3.0.0
DATABASE_HOST=db.staging.internal
GREETING=สวัสดีจาก env-file
LOG_LEVEL=debug
```

### ผลจริงจากทั้ง 3 กรณี

| ตัวแปร | `cfg-a` (ENV) | `cfg-b` (+ `--env-file`) | `cfg-c` (+ `-e`) | ผู้ชนะใน `cfg-c` |
|---|---|---|---|---|
| `APP_ENV` | `development` | `staging` | `production` | **`-e`** |
| `APP_VERSION` | `1.0.0` | `2.0.0-rc1` | `3.0.0` | **`-e`** |
| `GREETING` | `Hello` | `สวัสดีจาก env-file` | `สวัสดีจาก env-file` | **`--env-file`** |
| `DATABASE_HOST` | *(ไม่มี)* | `db.staging.internal` | `db.staging.internal` | **`--env-file`** |

> 📝 **กฎที่ได้:** `-e` ชนะ `--env-file` ชนะ `ENV` — จำง่าย ๆ ว่า **"ยิ่งใกล้เวลารัน ยิ่งมีอำนาจ"** · การทับเกิดขึ้น **ทีละตัวแปร** ไม่ใช่ทับทั้งไฟล์
>
> ⚠️ "ทีหลัง" หมายถึง **ลำดับของชั้น** ไม่ใช่ลำดับที่พิมพ์บนบรรทัดคำสั่ง — สลับที่ `-e` กับ `--env-file` ผลก็เหมือนเดิม

---

## การทดลองที่ 5 — Docker จดค่าซ้ำไว้อย่างไร

**คำถาม:** ค่าที่ถูกทับหายไปไหน

```bash
docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' cfg-c | grep APP_ENV
```

✅ **สิ่งที่ต้องเห็น** — `APP_ENV` โผล่ **สองครั้ง** :

```
APP_ENV=staging
APP_ENV=production
```

> 📝 นี่คือ **รายการดิบที่ Docker จดไว้** ยังไม่ได้ตัดตัวซ้ำ · ตอนจะสตาร์ตโปรเซสจริง Docker จะยุบชื่อที่ซ้ำโดย **เก็บตัวสุดท้าย** ค่าที่แอปเห็นจึงเป็น `production` — ตรงกับที่ `docker exec cfg-c env` เห็นแค่บรรทัดเดียวในการทดลองที่ 4

เก็บกวาดก่อนไปต่อ :

```bash
docker rm -f cfg-a cfg-b cfg-c
```

---

## การทดลองที่ 6 — image เดียว รัน 3 สภาพแวดล้อม

**คำถาม:** เปลี่ยน environment ต้อง build ใหม่ไหม

**รอบที่ 1 — development (ค่า default ล้วน ๆ)** แล้วเปิด `http://localhost:8184` :

```bash
docker rm -f web 2>/dev/null
docker run -d --name web -p 8184:8184 lab4-config:1.0
```

![หน้า Configuration Console ธีม development สีฟ้า-ม่วง](./images/env-development.png)

*ภาพ 6.1 — รอบที่ 1 ไม่ส่ง env ใด ๆ · หน้าเว็บใช้ค่า `ENV` ที่อบไว้ใน image จึงได้ธีม development*

**รอบที่ 2 — staging** แล้วรีเฟรชหน้าเดิม :

```bash
docker rm -f web
docker run -d --name web -p 8184:8184 --env-file .env.lab lab4-config:1.0
```

![หน้า Configuration Console ธีม staging สีส้ม-เหลือง](./images/env-staging.png)

*ภาพ 6.2 — รอบที่ 2 เพิ่ม `--env-file .env.lab` · image ตัวเดิมกลายเป็นธีม staging ทันทีโดยไม่ build ใหม่*

**รอบที่ 3 — production** :

```bash
docker rm -f web
docker run -d --name web -p 8184:8184 --env-file .env.lab \
  -e APP_ENV=production -e APP_VERSION=3.0.0 lab4-config:1.0
sleep 2
curl -s http://localhost:8184/healthz; echo
```

![หน้า Configuration Console ธีม production สีเขียวเข้ม](./images/env-production.png)

*ภาพ 6.3 — รอบที่ 3 เพิ่ม `-e` ทับ `--env-file` · ค่าที่ชนะคือค่าจาก `-e` จึงได้ธีม production*

✅ **สิ่งที่ต้องเห็น** — JSON สะท้อนค่าที่ส่งเข้าไปด้วย `-e` :

```
{"app_env":"production","app_version":"3.0.0","status":"ok"}
```

> 📝 **ไม่มีการ build ใหม่แม้แต่ครั้งเดียว** — image เดิม tag เดิม แต่หน้าเว็บเปลี่ยนทั้งธีม · นี่คือหัวใจของการแยก **"โค้ด"** ออกจาก **"config"** : ของที่ทดสอบผ่านบน staging คือ **binary ตัวเดียวกัน** กับที่ขึ้น production

---

## การทดลองที่ 7 — `ARG` หายไปไหนตอน run

**คำถาม:** ค่าที่ประกาศเป็น `ARG` แอปเห็นไหม

`Dockerfile.args` :

```dockerfile
FROM alpine:3.20
ARG APP_VERSION=dev
ARG BUILD_TOOL=manual
ENV APP_VERSION=$APP_VERSION
RUN echo "build เห็น: APP_VERSION=$APP_VERSION BUILD_TOOL=$BUILD_TOOL"
CMD ["sh","-c","echo run เห็น: APP_VERSION=$APP_VERSION BUILD_TOOL=$BUILD_TOOL"]
```

```bash
docker build --progress=plain --no-cache -f Dockerfile.args -t demo-args . 2>&1 | grep "build เห็น"
docker run --rm demo-args
```

✅ **สิ่งที่ต้องเห็น** — ตอน build เห็น `BUILD_TOOL=manual` แต่ตอน run **`BUILD_TOOL=` ว่างเปล่า** :

```
#5 0.227 build เห็น: APP_VERSION=dev BUILD_TOOL=manual
run เห็น: APP_VERSION=dev BUILD_TOOL=
```

> 📝 **จุดสำคัญอยู่ที่บรรทัด `ENV APP_VERSION=$APP_VERSION`** — มันคัดลอกค่าจาก `ARG` ไปเป็น `ENV` ให้เฉพาะ `APP_VERSION` · ส่วน `BUILD_TOOL` ไม่มีใครคัดลอกให้ จึง **ตายเมื่อ build จบ**
>
> ต้องใส่ `--progress=plain` ถึงจะเห็นข้อความจาก `RUN echo` และ `--no-cache` ถึงจะรัน `RUN` ใหม่จริง — **ไม่ใส่สองตัวนี้จะไม่เห็นอะไรเลย**

---

## การทดลองที่ 8 — ส่งค่าเข้าไปตอน build ด้วย `--build-arg`

**คำถาม:** ส่งค่าจากภายนอกเข้า `ARG` ได้อย่างไร

```bash
docker build --progress=plain --no-cache --build-arg APP_VERSION=2.5 \
  -f Dockerfile.args -t demo-args:2.5 . 2>&1 | grep "build เห็น"
docker run --rm demo-args:2.5
```

✅ **สิ่งที่ต้องเห็น** — `APP_VERSION` เปลี่ยนเป็น `2.5` ทั้งตอน build และตอน run (เพราะถูกคัดลอกเข้า `ENV`) :

```
#5 0.199 build เห็น: APP_VERSION=2.5 BUILD_TOOL=manual
run เห็น: APP_VERSION=2.5 BUILD_TOOL=
```

> ⚠️ **กับดักเงียบ:** ถ้าพิมพ์ชื่อ build arg ผิด (เช่น `--build-arg APP_VERISON=2.5`) BuildKit ที่มากับ Docker 29 **ไม่เตือนอะไรเลย** — build ผ่านฉลุยแล้วได้ค่า default แทน (ต่างจากตำราเก่าที่บอกว่าจะขึ้น `build-args were not consumed`) · จึงต้อง **ตรวจผลเสมอ** หลัง build

---

## การทดลองที่ 9 — secret รั่วออกทาง `docker history` ได้จริงไหม

**คำถาม:** ค่าที่ส่งผ่าน `--build-arg` หายไปจริงหรือแค่มองไม่เห็น

`Dockerfile.leak` คือตัวอย่าง **"วิธีที่ผิด"** ที่เขียนไว้ให้ดูโดยเฉพาะ (`ARG FAKE_TOKEN` แล้ว `ENV FAKE_TOKEN=$FAKE_TOKEN` ต่อ) :

```bash
docker build --no-cache --build-arg FAKE_TOKEN=PLACEHOLDER_NOT_A_REAL_TOKEN \
  -f Dockerfile.leak -t demo-leak .
docker history --no-trunc --format "{{.CreatedBy}}" demo-leak | grep -i token
```

✅ **สิ่งที่ต้องเห็น** — Docker เตือนเองตั้งแต่ตอน build และค่าที่ควรเป็นความลับ **โผล่ครบใน history** :

```
 2 warnings found:
 - SecretsUsedInArgOrEnv: Do not use ARG or ENV instructions for sensitive data (ARG "FAKE_TOKEN")

ENV FAKE_TOKEN=PLACEHOLDER_NOT_A_REAL_TOKEN
ARG FAKE_TOKEN=PLACEHOLDER_NOT_A_REAL_TOKEN
```

> 📝 ค่า `PLACEHOLDER_NOT_A_REAL_TOKEN` เป็นข้อความปลอมล้วน ๆ — **ห้ามลองด้วย token จริงเด็ดขาด** เพราะมันจะฝังอยู่ใน image อย่างถาวร

> 🔐 **บทเรียนความปลอดภัย:** ค่าที่ผ่าน `ARG` และ `ENV` **มองเห็นได้จาก history และ metadata** และการ "ลบไฟล์ทีหลัง" ก็ไม่ช่วย เพราะประวัติยังอยู่ · ทางแก้ที่ถูกมี 3 ทาง :
> 1. **ตอนรัน** — ส่งด้วย `-e` / `--env-file` / secret manager (ค่าอยู่แค่ในตัว container)
> 2. **ตอน build ที่จำเป็นต้องใช้ secret** — ใช้ BuildKit secret mount : `RUN --mount=type=secret,id=tok cat /run/secrets/tok` แล้วสั่ง `docker build --secret id=tok,src=./token.txt .` — **ไม่ตกลง layer และไม่โผล่ใน history**
> 3. **multi-stage build** — ใช้ secret เฉพาะ stage แรก แล้ว `COPY --from=builder` เอาเฉพาะผลลัพธ์ (LAB 7)

---

## การทดลองที่ 10 — `ARG` ก่อน `FROM` ต้องประกาศซ้ำ

**คำถาม:** ประกาศ `ARG` ไว้ก่อน `FROM` แล้วใช้ต่อได้เลยไหม

`Dockerfile.argfrom` :

```dockerfile
ARG ALPINE_VERSION=3.20
FROM alpine:$ALPINE_VERSION
RUN echo "ยังไม่ประกาศซ้ำ ALPINE_VERSION=[$ALPINE_VERSION]"
ARG ALPINE_VERSION
RUN echo "ประกาศซ้ำแล้ว ALPINE_VERSION=[$ALPINE_VERSION]"
```

```bash
docker build --progress=plain --no-cache -f Dockerfile.argfrom -t demo-argfrom . 2>&1 | grep ALPINE_VERSION=
```

✅ **สิ่งที่ต้องเห็น** — ก่อนประกาศซ้ำได้ **ค่าว่าง** หลังประกาศซ้ำได้ค่าจริง :

```
#5 0.229 ยังไม่ประกาศซ้ำ ALPINE_VERSION=[]
#6 0.268 ประกาศซ้ำแล้ว ALPINE_VERSION=[3.20]
```

> 📝 บรรทัด `ARG ALPINE_VERSION` (เปล่า ๆ ไม่มี `=`) หลัง `FROM` คือการบอกว่า **"ขอค่าเดิมที่ประกาศไว้ข้างนอกเข้ามาใช้ใน stage นี้ด้วย"** · ถ้าลืมบรรทัดนี้ ตัวแปรจะเป็นค่าว่างทันที **ไม่มี error ไม่มี warning** ซึ่งอันตรายกว่า error เสียอีก
>
> เหตุผลหลักที่มี `ARG` ก่อน `FROM` คือใช้ **เลือกเวอร์ชันของ base image** จากภายนอก : `docker build --build-arg ALPINE_VERSION=3.19 ...`

---

## การทดลองที่ 11 — ทำไมไฟล์ config ไม่ต้องอยู่ใน image

**คำถาม:** `.env.lab` ถูก `.dockerignore` กันไว้ แล้วแอปยังทำงานได้อย่างไร

```bash
cat .dockerignore
```

```
.env
.env.*
__pycache__/
*.pyc
test_logs/
images/
readme.md
```

พิสูจน์ว่ากติกา `.env.*` ทำงานจริง แม้เขียน `COPY . .` :

```bash
cat > Dockerfile.copyall <<'EOF'
FROM alpine:3.20
WORKDIR /ctx
COPY . .
CMD ["ls","-a","/ctx"]
EOF
docker build -q -f Dockerfile.copyall -t demo-copyall . >/dev/null && docker run --rm demo-copyall
```

✅ **สิ่งที่ต้องเห็น** — **ไม่มี `.env.lab`** ทั้งที่ไฟล์นี้อยู่ในโฟลเดอร์จริง :

```
.
..
.dockerignore
Dockerfile
Dockerfile.argfrom
Dockerfile.args
Dockerfile.copyall
Dockerfile.leak
app.py
requirements.txt
verify.sh
```

> 📝 **นี่คือประเด็นของข้อนี้:** `--env-file` อ่านไฟล์จาก **เครื่องที่พิมพ์คำสั่ง** ไม่ใช่จากในกล่อง image — ไฟล์ config ที่ใช้ตอนรันจึง **ไม่ต้องอยู่ใน image** ตั้งแต่แรก · ของจริงต้องใส่ `.env` ทั้งใน `.dockerignore` **และ** `.gitignore`

เก็บกวาดของทดลองข้อนี้ :

```bash
rm -f Dockerfile.copyall && docker rmi -f demo-copyall
```

---

## ตรวจงานด้วย `verify.sh`

```bash
bash verify.sh ; echo "exit code = $?"
```

✅ **สิ่งที่ต้องเห็น** — `ALL CHECKS PASSED` และ exit code `0` :

```
[PASS] มีไฟล์ LAB ครบ
[PASS] .dockerignore มี .env
        ... (รวม 21 ข้อ ต้องเป็น [PASS] ทุกข้อ) ...
[PASS] หลังประกาศซ้ำ มีค่า 3.20
ALL CHECKS PASSED
exit code = 0
```

> 📝 สคริปต์ใช้ชื่อ container ของตัวเอง (`lab4-check`, `lab4-env-file`, `lab4-env-override`) และลบเฉพาะของตัวเอง ไม่ยุ่งกับ `web`/`cfg-*` ของเรา · ต้องรันจาก **ในโฟลเดอร์แล็บ** เพราะอ่าน `.env.lab` แบบ relative path

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `--env-file: open .env.lab: no such file or directory` (exit `125`) | อยู่ผิดโฟลเดอร์ (path เป็น relative) หรือพิมพ์ชื่อผิด | `cd` เข้าโฟลเดอร์แล็บแล้ว `ls -a` ให้เห็น `.env.lab` ก่อน |
| `invalid env file: variable ... contains whitespaces` | ไฟล์ `.env` มีบรรทัดที่ไม่ใช่รูปแบบ `KEY=value` | แก้ให้เป็น `KEY=value` บรรทัดละตัว ไม่มีช่องว่างรอบ `=` |
| ตั้ง `-e` แล้วแอปยัง**ไม่เปลี่ยนค่า** | ยังเป็น container ตัวเก่า — ค่า ENV **ตั้งได้ตอนสร้างเท่านั้น** `docker restart` ไม่เปลี่ยนให้ | `docker rm -f <ชื่อ>` แล้ว `docker run` ใหม่พร้อม `-e` ชุดใหม่ |
| `docker build` ไม่พิมพ์ข้อความจาก `RUN echo` | ไม่ได้ใส่ `--progress=plain` หรือ layer นั้นโดน cache | ใส่ทั้ง `--progress=plain` และ `--no-cache` |
| ส่ง `--build-arg X=1` แล้วค่าไม่เข้า และ**ไม่มี warning** | ไม่ได้ประกาศ `ARG X` ใน Dockerfile หรือสะกดชื่อผิด — BuildKit รุ่นใหม่ไม่เตือน | เพิ่ม `ARG X` ใน Dockerfile แล้วตรวจผลด้วย `docker history` ทุกครั้ง |
| ค่า `ARG` ใช้ได้ใน `RUN` แต่แอปมองไม่เห็น | `ARG` มีชีวิตแค่ตอน build | เพิ่มบรรทัด `ENV X=$X` หลัง `ARG X` |
| ตัวแปรที่ประกาศ `ARG` **ก่อน `FROM`** กลายเป็นค่าว่างใน `RUN` | `ARG` ก่อน `FROM` มี scope เฉพาะบรรทัด `FROM` | ประกาศ `ARG <ชื่อ>` ซ้ำอีกครั้ง **หลัง** `FROM` |
| `.env` หลุดเข้า image / `docker history` เห็น token | ใช้ `COPY . .` โดยไม่มี `.dockerignore` หรือส่ง secret ผ่าน `--build-arg` | ใส่ `.env` และ `.env.*` ใน `.dockerignore` · ส่ง secret ตอน run เท่านั้น |
| เปิด `http://localhost:8184` ไม่ขึ้น | ลืม `-p 8184:8184` ที่ชั้นใดชั้นหนึ่ง | ตรวจ `docker ps` ให้เห็น `0.0.0.0:8184->8184/tcp` |

---

## เก็บกวาด

**ในกล่องเรียน:**

```bash
docker rm -f web cfg-a cfg-b cfg-c 2>/dev/null
docker rmi -f lab4-config:1.0 demo-args demo-args:2.5 demo-argfrom demo-leak 2>/dev/null
docker ps -a
```

> 📝 ลบ **`demo-leak`** ให้แน่ใจ เพราะมีค่า token ปลอมฝังอยู่ · เก็บ base image `python:3.12-slim` กับ `alpine:3.20` ไว้ใช้ต่อได้

**ออกจากกล่องแล้วลบกล่องบนเครื่องเรา:**

```bash
exit
docker rm -f devtools-df-lab4
docker ps -a --filter "name=^devtools-"
```

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker run <image>` | ได้ค่า default จาก `ENV` (ชั้นที่ 1) |
| `docker run --env-file .env.lab <image>` | โหลดหลายค่าจากไฟล์ `KEY=value` (ชั้นที่ 2) |
| `docker run -e KEY=value <image>` | ตั้งทีละตัวตอนรัน **ชนะทุกชั้น** (ชั้นที่ 3) |
| `docker exec <c> env` | ดูค่าที่ container **เห็นจริง** ขณะกำลังรัน |
| `docker inspect -f '{{range .Config.Env}}{{println .}}{{end}}' <c>` | ดูรายการดิบที่ Docker จดไว้ (เห็นค่าซ้ำได้) |
| `docker build --build-arg KEY=value -f <ไฟล์> .` | ส่งค่าเข้า `ARG` ระหว่าง build — **ห้ามใส่ secret** |
| `docker build --progress=plain --no-cache ...` | บังคับให้เห็น log ดิบและรัน `RUN` ใหม่จริง |
| `docker history --no-trunc --format "{{.CreatedBy}}" <image>` | ดูว่าแต่ละ layer สร้างด้วยคำสั่งอะไร — **เห็นค่า `ARG`/`ENV` ที่ฝังไว้** |

> **จำสามชั้นให้ขึ้นใจ:** `ENV` (ฝังใน image) → `--env-file` (หลายค่าตอนรัน) → `-e` (ทีละค่าตอนรัน) · **ขวาชนะซ้ายเสมอ**

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `cfg-a` เห็น `development` · `cfg-b` เห็น `staging` · `cfg-c` เห็น `production` — และอธิบายได้ว่าทำไม
- [ ] อธิบายได้ว่าใน `cfg-c` ทำไม `GREETING`/`DATABASE_HOST` ยังเป็นค่าจาก `--env-file`
- [ ] `docker inspect` เห็น `APP_ENV` **สองบรรทัด** และรู้ว่าตัวหลังเป็นตัวที่มีผลจริง
- [ ] เปิด `http://localhost:8184` เห็นครบ 3 ธีม จาก **image เดียวกัน** โดยไม่ build ใหม่
- [ ] `Dockerfile.args` แสดงว่า `BUILD_TOOL` **ว่างเปล่าตอน run** พร้อมอธิบายเหตุผลได้
- [ ] `--build-arg APP_VERSION=2.5` เปลี่ยนค่าได้ทั้งตอน build และ run
- [ ] เห็นค่า `FAKE_TOKEN` ปลอมรั่วออกมาทาง `docker history` พร้อมคำเตือน `SecretsUsedInArgOrEnv`
- [ ] `Dockerfile.argfrom` แสดง `ALPINE_VERSION=[]` ก่อนประกาศซ้ำ และ `[3.20]` หลังประกาศซ้ำ
- [ ] `COPY . .` แล้ว `.env.lab` **ไม่หลุดเข้า image** เพราะกติกา `.env.*`
- [ ] `bash verify.sh` ขึ้น `ALL CHECKS PASSED` และเก็บกวาดจนไม่เหลือ container ของแล็บ

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
