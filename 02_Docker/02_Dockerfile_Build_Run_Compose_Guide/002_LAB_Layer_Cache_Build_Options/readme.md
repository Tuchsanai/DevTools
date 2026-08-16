# LAB 2 — Layer Cache และ Options ของ `docker build`

> โฟลเดอร์ `002_LAB_Layer_Cache_Build_Options` = **LAB 2** ของชุด "Dockerfile → Build → Run → Compose" (ตอนที่ 5 และ 4.1 ของคู่มือ) ต่อจาก LAB 1 ที่เขียน Dockerfile ตัวแรกและ build image ได้สำเร็จ
> ไฟล์ในโฟลเดอร์นี้ : `Dockerfile.good` (ลำดับที่ดี) · `Dockerfile.bad` (ลำดับที่ควรเลี่ยง) · `app.py` (Flask หน้าเดียว) · `requirements.txt` · `.dockerignore` · `verify.sh` (ตัวตรวจอัตโนมัติ) · `images/`

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | Dockerfile สองไฟล์ที่ต่างกันแค่ **ลำดับ 2 บรรทัด** ทำให้ build ต่างกันกี่เท่า และต่างตอนไหน |
| **ต้องผ่านอะไรมาก่อน** | **LAB 1** (build · run · build context) |
| **เวลา** | ~35 นาที (แกนหลัก ข้อ 0–10 ประมาณ 27 นาที · ทดลองเพิ่มเติม ~8 นาที) |
| **จบแล้วต้องทำได้เอง** | ชี้ได้ว่า cache แตกที่ขั้นไหนและเพราะอะไร · เรียง Dockerfile จาก "เปลี่ยนน้อย → เปลี่ยนบ่อย" · คืนพื้นที่โดยรู้ว่ากำลังลบอะไร |
| **แล็บนี้ยัง *ไม่* สอน** | `--build-arg` เต็มรูปแบบ → **LAB 4** · `--target` และ multi-stage → **LAB 7** · `.dockerignore` มุมกัน secret หลุด → **LAB 1** ข้อ 6 (ที่นี่ดูเฉพาะมุม cache) |

## สิ่งที่จะได้เรียนรู้

- **Docker build ทำงานจากบนลงล่าง** และเก็บผลแต่ละขั้นเป็น **layer** — ขั้นไหนเปลี่ยน ขั้นนั้น**และทุกขั้นถัดไป**ต้อง build ใหม่
- พิสูจน์ด้วย **เวลาจริงที่จับด้วย `time`** ว่าการสลับแค่ 2 บรรทัดทำให้ build ต่างกันจาก **18.4 วินาที เหลือ 0.8 วินาที**
- อ่าน log ของ build ให้เป็น : คำว่า **`CACHED`** อยู่ตรงไหน แปลว่าอะไร และขั้นไหนที่ cache แตก
- Options ที่ใช้จริงทุกวัน : `-t` (ติดหลาย tag ครั้งเดียว) · `-f` · `--no-cache` · `--pull` · `--progress=plain` · `--build-arg` · `--target`
- ทำไม `--no-cache` **ไม่ได้**ดึง base image ใหม่ และเมื่อไหร่ต้องใช้ `--pull --no-cache`
- คืนพื้นที่อย่างเข้าใจ : **`docker history`** (layer `RUN pip install` = **269MB**) · image `<untagged>` · `docker image prune` · `docker system df` · `docker builder prune` (คืนได้จริง **1.391GB**)
- `.dockerignore` ไม่ได้แค่ลดขนาด context แต่ **กันไม่ให้ cache แตกโดยไม่จำเป็น**

## ภาพรวมของแล็บนี้

1. **เตรียมเครื่องเรียน + clone โค้ด** — อ่าน `Dockerfile.good` กับ `Dockerfile.bad` เทียบกัน ต่างกันแค่ **ลำดับ 2 บรรทัด**
2. **ทำให้เงื่อนไขเท่ากันก่อนจับเวลา** — pull base image ล่วงหน้าและล้าง build cache
3. **รอบที่ 1 (cold)** — build ทั้งสองไฟล์ จับเวลาด้วย `time`
4. **รอบที่ 2** — แก้ `app.py` แค่ **1 บรรทัด** แล้ว build ใหม่ทั้งสอง จับเวลาอีกครั้ง แล้วทำ**ตารางเทียบเวลาจริง**
5. **Options ของ `docker build`** — `-t` หลาย tag · `-f` · `--no-cache` · `--pull` · `--progress=plain` · `--build-arg` · `--target` พร้อมกับดักที่มักพลาด
6. **`docker history` แล้วต่อด้วยการคืนพื้นที่** — layer ไหนใหญ่ · image `<untagged>` + `docker image prune` · `docker system df` + `docker builder prune`
7. **`.dockerignore` กับ cache** — พิสูจน์ว่าแก้ไฟล์ที่ถูก ignore แล้ว cache **ไม่แตก**
8. **รันแอปจริงบนพอร์ต 8182** แล้วปิดท้ายด้วย **`./verify.sh`** ตรวจซ้ำทั้งแล็บอัตโนมัติ

> **คำถามก่อนเริ่ม:** ถ้า Dockerfile สองไฟล์ติดตั้ง package ชุดเดียวกันเป๊ะ ใช้ base image เดียวกัน ได้ image ที่ทำงานเหมือนกันทุกอย่าง — แค่**สลับลำดับ 2 บรรทัด** จะทำให้เวลา build ต่างกันจริงหรือ? ต่างกันกี่เท่า? และ "ตอนไหน" ที่ความต่างนั้นจะโผล่มา?

### Terminal Map

แล็บนี้ใช้ **terminal เดียวก็พอ** (ไม่มีคำสั่งที่บล็อกค้าง ทุกคำสั่งรันจบแล้วคืน prompt)

| หน้าต่าง | หน้าที่ |
|---|---|
| **T1** | ทุกคำสั่งของแล็บ : build, จับเวลา, ตรวจ image, cleanup |
| **เบราว์เซอร์** | เปิด `http://localhost:8182` ดูหน้าเว็บของแอปในข้อ 9 |

## ทฤษฎีก่อนลงมือ

### ภาพจำหลัก

image คือกอง layer แบบอ่านอย่างเดียวที่ต่อกันตาม Dockerfile และ cache ใช้กองเดิมได้เมื่อเหตุผลตั้งแต่ฐานขึ้นมายังเหมือนเดิม

![ภาพกอง layer ของ Dockerfile.good แสดงขนาดแต่ละชั้นและผลของการแก้ชั้นหนึ่งต่อชั้นถัดลงไป](./images/theory-layer-cache.svg)

> 🖼 **วิธีอ่านรูปนี้:** ไล่จาก base image ราว 129MB ผ่าน `WORKDIR`, `COPY requirements.txt`, `RUN pip install` ราว 269MB ถึง `COPY . .` ราว 16.4kB มองทั้งขนาดและเส้นที่บอกว่าเมื่อชั้นหนึ่งเปลี่ยน ชั้นถัดไปต้องสร้างใหม่ แล้วเทียบกับ `CACHED` และเวลาในข้อ 4

### กลไกจริง

BuildKit อ่าน Dockerfile จากบนลงล่างและแปลงแต่ละขั้นเป็นงานที่มี input ชัดเจน `FROM` กำหนด snapshot ตั้งต้น ส่วน `WORKDIR`, `ENV`, `COPY` และ `RUN` ต่อสถานะบนผลก่อนหน้า บางคำสั่งเพิ่มไฟล์ บางคำสั่งเปลี่ยนเพียง metadata แต่ทุกขั้นอยู่ในสายเดียวกัน

ก่อนทำแต่ละขั้น BuildKit สร้าง cache key จากคำสั่งและสถานะ parent สำหรับ `COPY` ยังนำไฟล์ในขอบเขตมาคำนวณ checksum จากเนื้อหาและ metadata ที่เกี่ยวข้อง ไม่ได้ตัดสินด้วยเวลาแก้ไฟล์อย่างเดียว การแก้ `app.py` เพียงข้อความสั้น ๆ จึงเปลี่ยน key ของ `COPY . .` แต่แตะ timestamp โดยเนื้อหาเดิมไม่ควรทำให้ cache แตก

ลองนึกว่า layer เป็นชั้นตึก และ digest ของชั้นล่างคือเลขฐานรากในแบบของชั้นบน แม้คำสั่งชั้นบนเหมือนเดิม เมื่อเลขฐานรากเปลี่ยน แบบเดิมก็ใช้อ้างไม่ได้ cache miss จึงลามไปทุกขั้นถัดไป เพราะ parent digest ซึ่งเป็น input เปลี่ยน ไม่ใช่เพราะ Docker เดาว่าคำสั่งผิด

ลำดับ `COPY` จึงชี้ชะตาเวลา build ใน `Dockerfile.good` dependency ถูกคัดลอกและติดตั้งก่อน source code เมื่อแก้ `app.py`, checksum ของ `requirements.txt` ยังเดิม จึงเก็บ layer แพงจาก `RUN pip install` ได้ ส่วน `Dockerfile.bad` คัดลอกทั้ง context ก่อน ขั้นติดตั้งจึงอยู่ใต้จุดเปลี่ยนบ่อยและต้องทำใหม่ทั้งที่ package เดิม

build context ไม่ใช่การเททุกไฟล์ให้ทุกขั้น BuildKit ใช้ Dockerfile และ `.dockerignore` กรองสิ่งที่ส่ง เลือกข้อมูลที่ `COPY` ต้องใช้ และส่งเฉพาะส่วนที่เปลี่ยนใน build ถัดไป ไฟล์ที่ ignore จึงไม่อยู่ใน checksum ของ `COPY . .`; การแก้ไฟล์นั้นในข้อ 8 ไม่ควรเปลี่ยน key

เมื่อใช้ `--no-cache`, ขั้นที่รันงานจริงอย่าง `RUN` ต้องไม่หยิบผลเก่า แต่ Docker 29 อาจยังแสดง `WORKDIR` เป็น `CACHED` เพราะเป็นขั้นเบา ๆ ที่ BuildKit จัดการเองได้โดยไม่ต้องรัน process ใน container (ถึงจะสร้างโฟลเดอร์ `/app` เป็น layer เล็ก ๆ 8.19kB ก็ตาม) จึงต้องดู `RUN pip install` ในข้อ 5.2 ส่วน `--pull` มีหน้าที่เช็ก base image บน registry แยกกัน

layer เป็น immutable และแชร์กันได้ การ build โดยไม่มี `-t` บน Docker 29 ได้ image ชื่อ `<untagged>` แต่ลบแล้วอาจคืนพื้นที่น้อยเมื่อ layer ยังถูกอ้าง `docker system df` แยกพื้นที่ Images, Containers, Volumes และ Build Cache ส่วน `docker builder prune` เก็บเฉพาะ cache ของ builder ไม่ลบ image ที่มี tag และทำให้ build ถัดไปช้าลง

### กฎที่ต้องจำ

| กฎ | เหตุผล |
|---|---|
| เรียงขั้นจากเปลี่ยนน้อยไปเปลี่ยนบ่อย | รักษา cache ของงานแพงให้นานที่สุด |
| แยก `COPY` ไฟล์ dependency ออกจาก source code | การแก้โค้ดไม่ควรลากการติดตั้ง dependency ให้ทำใหม่ |
| cache key ผูกกับคำสั่ง, input และ parent | แตกหนึ่งชั้นแล้วชั้นถัดไปย่อมได้รับฐานคนละชุด |
| ดูพื้นที่ตามชนิดก่อน prune | image layer กับ Build Cache อาจใช้พื้นที่ร่วมกันแต่มีวงจรลบคนละแบบ |

### สิ่งที่มักเข้าใจผิด

- คิดว่า image เป็นไฟล์ก้อนเดียว แต่จริง ๆ เป็น manifest ที่ชี้ไปยังกอง layer ซึ่งแชร์ข้าม image ได้
- คิดว่า `--no-cache` ต้องทำให้ทุกบรรทัดห้ามแสดง `CACHED` แต่จริง ๆ ขั้นเบา ๆ ที่ไม่ต้องรัน process อย่าง `WORKDIR` อาจยังแสดงเช่นนั้นได้ ให้ตรวจขั้น `RUN` ที่มีงานจริง
- คิดว่าลบ image ขนาดใหญ่แล้วต้องได้พื้นที่คืนเท่ากัน แต่จริง ๆ layer ที่ image อื่นหรือ cache ยังอ้างอยู่จะยังถูกเก็บไว้

### ทายผลก่อนทดลอง

1. ในข้อ 4 หลังแก้เพียง `app.py`, log ของ `Dockerfile.good` กับ `Dockerfile.bad` จะเริ่มต่างกันที่ขั้นใด และขั้นติดตั้ง dependency ของแต่ละไฟล์จะมีสถานะอะไร?
2. ก่อนทำข้อ 8 ลองทายว่า checksum ของ `COPY . .` จะเปลี่ยนหรือไม่เมื่อแก้ไฟล์ที่ `.dockerignore` กันไว้ แล้วผลจะต่างอย่างไรหลังเอาชื่อไฟล์นั้นออกจากรายการ ignore?

## 0. เตรียมเครื่องเรียน

ทำบนเครื่องของเราเอง (ไม่ใช้ cloud) — เปิด container ที่ติดตั้ง Docker มาให้แล้ว :

```bash
docker rm -f devtools-df-lab2 2>/dev/null
docker run -dit --name devtools-df-lab2 --privileged \
  -p 2232:22 -p 8182:8182 tuchsanai/devtools:2569_1
ssh root@localhost -p 2232        # password : passwd

# --- สองบรรทัดนี้พิมพ์ "ข้างในเครื่องเรียน" หลัง ssh เข้าไปแล้ว ---
docker --version
docker info --format 'Docker daemon: {{.ServerVersion}}'
```

> 📝 **คำอธิบาย:** `docker rm -f ... 2>/dev/null` ลบ container ชื่อเดิมที่อาจค้างอยู่ (ถ้าไม่มีก็ไม่ต้องบ่น) · `--privileged` จำเป็นเพราะเราจะ **รัน Docker ข้างใน container อีกที** (Docker-in-Docker) ใช้เฉพาะ container สำหรับเรียนที่ทิ้งได้ **ไม่ใช่ค่าที่ใช้ใน production** · `-p 2232:22` เปิด SSH · `-p 8182:8182` เตรียมให้หน้าเว็บของข้อ 9 ทะลุออกมาถึงเบราว์เซอร์ · **ทุกคำสั่งหลังจากนี้พิมพ์ข้างในเครื่องเรียน** (ใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2232` ได้เลย) · สองบรรทัดสุดท้ายยืนยันว่า `docker` ข้างในวิ่งถึง daemon ได้จริง สิ่งที่ต้องดูคือ "มีเลขเวอร์ชันขึ้นไหม" ไม่ใช่ "เลขตรงกับเอกสารไหม" — ถ้าขึ้น `Cannot connect to the Docker daemon` แปลว่า daemon ข้างในยังตื่นไม่เสร็จ รอ 10–20 วินาทีแล้วลองใหม่

✅ **Expected output** — ขอแค่มีเลขเวอร์ชันครบสองบรรทัด ไม่ใช่ error (เลขเวอร์ชันของแต่ละคนอาจไม่ตรงกับเอกสารนี้):

```
Docker version 29.6.2, build dfc4efb
Docker daemon: 29.6.2
```

## 1. Clone โค้ดแล็บ แล้วอ่าน Dockerfile สองไฟล์เทียบกัน

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide/002_LAB_Layer_Cache_Build_Options
ls -a
diff Dockerfile.good Dockerfile.bad
```

> 📝 **คำอธิบาย:** ถ้าเคย clone ไว้แล้วจาก LAB 1 ให้ข้ามบรรทัด `git clone` แล้ว `cd` เข้ามาได้เลย · `ls -a` ต้องใส่ `-a` เพราะ `.dockerignore` เป็นไฟล์ซ่อน (ขึ้นต้นด้วยจุด) ซึ่งเป็นพระเอกของข้อ 8 · `diff` เทียบไฟล์ทีละบรรทัด : `<` คือของไฟล์แรก (`good`) และ `>` คือของไฟล์ที่สอง (`bad`)

✅ **Expected output** — จุดที่ต้องเห็นคือ **คำสั่งชุดเดียวกันเป๊ะ ต่างกันแค่ลำดับ** — บรรทัด `RUN pip install` ย้ายไปอยู่ **หลัง** `COPY . .` ในไฟล์ `bad`:

```
5,9c5
< COPY requirements.txt .
        ... (ตัดท่อนกลาง) ...
11,12c7,10
> RUN pip install --no-cache-dir -r requirements.txt
> ENV BUILD_ID=bad-1
```

**`Dockerfile.good` — ลำดับที่ดี** (ซ้าย) เทียบกับ **`Dockerfile.bad` — ลำดับที่ควรเลี่ยง** (ขวา) :

```dockerfile
# ---------- Dockerfile.good ----------              # ---------- Dockerfile.bad ----------
FROM python:3.12-slim                                FROM python:3.12-slim
WORKDIR /app                                         WORKDIR /app
COPY requirements.txt .                              COPY . .                    # ← ทุกไฟล์เข้ามาก่อน
RUN pip install --no-cache-dir -r requirements.txt   RUN pip install --no-cache-dir -r requirements.txt
COPY . .                                             ENV BUILD_ID=bad-1
ENV BUILD_ID=good-1                                  EXPOSE 8182
EXPOSE 8182                                          CMD ["python","app.py"]
CMD ["python","app.py"]
```

> 📝 **คำอธิบาย:** (บรรทัด comment ภาษาไทยในไฟล์จริงถูกตัดออกจากตารางเทียบนี้ให้อ่านง่าย — เปิดไฟล์จริงดูได้) · `--no-cache-dir` เป็น option ของ **pip** (ไม่ให้ pip เก็บ wheel cache ไว้ใน image เพื่อให้ image เล็กลง) — **คนละเรื่องกับ** `--no-cache` ของ `docker build` ในข้อ 5 อย่าสับสน · `ENV BUILD_ID=...` ตั้งไว้ให้หน้าเว็บในข้อ 9 บอกได้ว่า image มาจาก Dockerfile ไหน · `EXPOSE 8182` เป็นเพียง **เอกสารกำกับ image** ไม่ได้เปิดพอร์ตให้เอง ต้องใช้ `-p` ตอน `docker run` เสมอ

ดูไฟล์ที่เหลือด้วย `cat requirements.txt` และ `tail -1 app.py`

> 📝 **คำอธิบาย:** `requirements.txt` **pin เวอร์ชันทุกตัว** เพื่อให้ทั้งห้องได้ผลเหมือนกันและให้ cache เสถียร (ถ้าเขียนลอย ๆ ว่า `flask` เฉย ๆ วันดีคืนดี pip จะหยิบเวอร์ชันใหม่มาโดยที่ layer cache ยังบอกว่า "เหมือนเดิม") · บรรทัดสุดท้ายของ `app.py` คือ `# APP_VERSION = 1` เราจะใช้เป็น "การแก้โค้ด 1 บรรทัด" ในข้อ 4

✅ **Expected output** — เวอร์ชันที่ pin ไว้เป็นชุดที่ผ่านการทดสอบจริงในเอกสารนี้:

```
flask==3.1.2
requests==2.32.3
pandas==2.2.3
matplotlib==3.9.2
# APP_VERSION = 1
```

## 2. ทำให้เงื่อนไขเท่ากันก่อนจับเวลา

การจับเวลาเชื่อถือไม่ได้เลยถ้าไฟล์หนึ่งต้องโหลด base image ก่อนแต่อีกไฟล์ไม่ต้อง — ล้างสนามให้เท่ากันก่อน :

```bash
docker pull python:3.12-slim
docker builder prune -af
docker image ls
```

> 📝 **คำอธิบาย:** `docker pull` ดึง base image มาก่อน ทั้งสอง Dockerfile จะได้เริ่มจากจุดเดียวกัน · `docker builder prune -af` ล้าง **build cache ทั้งหมด** (`-a` = ลบทุกอันไม่ใช่แค่ที่ไม่ได้ใช้, `-f` = ไม่ถามยืนยัน) — ใช้ `-f` ตรงนี้เพราะจงใจล้างให้เกลี้ยงเพื่อการทดลอง แต่**ตอนใช้งานจริงอย่าเพิ่งเติม `-f`** ให้ Docker แสดงรายการและถามก่อน · `builder prune` ไม่ได้ลบ image แต่ build ครั้งถัดไปจะช้าลงเพราะต้องสร้าง cache ใหม่

✅ **Expected output** — เหลือแค่ base image ตัวเดียว (digest ของแต่ละคนจะไม่ตรงกับเอกสารนี้ · Docker 29 แสดงคอลัมน์ `DISK USAGE`/`CONTENT SIZE` แทน `SIZE` แบบเดิม):

```
3.12-slim: Pulling from library/python
        ... (ทยอย Download / Pull complete รวม 4 layer) ...
Status: Downloaded newer image for python:3.12-slim
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
python:3.12-slim   dd29372629ee        179MB         45.4MB
```

## 3. รอบที่ 1 (cold) — build ทั้งสองไฟล์แล้วจับเวลา

> **ทายก่อนรัน :** ตอนนี้ยังไม่มี cache เลย คิดว่าเวลา build ของ `good` กับ `bad` จะต่างกันไหม?

```bash
time docker build -f Dockerfile.good -t cachelab-good:1.0 .
```

> 📝 **คำอธิบาย:** `time` เป็นคำสั่งของ shell วัดเวลาที่คำสั่งข้างหลังใช้ไป ผลโผล่ 3 บรรทัดท้าย ให้ดูบรรทัด **`real`** (เวลานาฬิกาจริง) ส่วน `user`/`sys` คือเวลา CPU ของตัว client ซึ่งน้อยมากเพราะงานหนักไปเกิดที่ daemon · `-f Dockerfile.good` เลือกไฟล์ Dockerfile (ถ้าไม่ใส่ Docker จะหาไฟล์ชื่อ `Dockerfile` เฉย ๆ ซึ่งโฟลเดอร์นี้ไม่มี) · `-t cachelab-good:1.0` ตั้งชื่อ:tag · **จุด `.` ท้ายสุดคือ build context ห้ามลืมเด็ดขาด** (หัวข้อ "ทดลองเพิ่มเติม" จะให้ลองลืมดูว่าพังยังไง)

✅ **Expected output** — ทุกขั้นขึ้น `DONE` ไม่มีคำว่า `CACHED` เลยเพราะยังไม่มี cache; จุดที่ต้องดูคือ **`#8 RUN pip install ... DONE 11.5s`** กับบรรทัด **`real`** (เวลาของแต่ละคนขึ้นกับเน็ตและ CPU จะไม่ตรงกับเอกสารนี้):

```
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 0.979 Collecting flask==3.1.2 (from -r requirements.txt (line 1))
        ... (ตัดท่อนกลาง : ดาวน์โหลด pandas 12.7 MB · numpy 16.7 MB · matplotlib ฯลฯ) ...
#8 11.22 Successfully installed blinker-1.9.0 ... pandas-2.2.3 ... werkzeug-3.1.8
#8 DONE 11.5s
#9 [5/5] COPY . .
#9 DONE 0.1s
real	0m19.158s
user	0m0.103s
sys	0m0.086s
```

ทีนี้ไฟล์ที่ลำดับไม่ดี :

```bash
time docker build -f Dockerfile.bad -t cachelab-bad:1.0 .
```

> 📝 **คำอธิบาย:** คำสั่งเดียวกันเป๊ะ เปลี่ยนแค่ `-f` กับชื่อ tag · รอบนี้ยังไม่มีอะไรน่าตื่นเต้น — ประเด็นทั้งหมดจะไปโผล่ในข้อ 4

✅ **Expected output** — เวลาพอ ๆ กับ `good` (ต่างกันไม่ถึงครึ่งวินาที) เพราะทั้งคู่ต้องติดตั้ง package ใหม่หมดเหมือนกัน:

```
#8 [4/4] RUN pip install --no-cache-dir -r requirements.txt
#8 DONE 11.5s

real	0m18.929s
```

> **สรุปรอบที่ 1 :** ลำดับคำสั่ง **ไม่มีผลเลย** ตอน build ครั้งแรก — ซึ่งเป็นเหตุผลที่คนส่วนใหญ่เขียน Dockerfile ผิดลำดับแล้วไม่รู้ตัว เพราะตอนทดสอบครั้งแรกมันเหมือนกันทุกประการ

## 4. รอบที่ 2 — แก้ `app.py` แค่ 1 บรรทัด แล้ว build ใหม่ทั้งสอง

นี่คือการทดลองแกนกลางของแล็บ จำลองสิ่งที่เกิดขึ้น **ทุกวันในชีวิตจริง** : แก้โค้ดแอปนิดเดียวแล้ว build image ใหม่

```bash
sed -i 's/# APP_VERSION = 1/# APP_VERSION = 2/' app.py
tail -1 app.py
time docker build -f Dockerfile.good -t cachelab-good:1.0 .
```

> 📝 **คำอธิบาย:** `sed -i` แก้ไฟล์ตรงที่ (in-place) เปลี่ยนเลข 1 เป็น 2 ในบรรทัด comment สุดท้ายของ `app.py` — เป็นการแก้ที่ **ไม่แตะ `requirements.txt` เลยแม้แต่นิดเดียว** · `tail -1` ยืนยันว่าแก้ถูกจุด · จะเปิด editor แก้เองก็ได้ ขอแค่แก้เฉพาะ `app.py`

✅ **Expected output** — จุดชี้ขาดคือคำว่า **`CACHED`** ที่ขั้น `#8 RUN pip install` และบรรทัด `real` ที่เหลือไม่ถึง 1 วินาที:

```
# APP_VERSION = 2

#7 [3/5] COPY requirements.txt .
#7 CACHED
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 CACHED
#9 [5/5] COPY . .
#9 DONE 0.0s

real	0m0.765s
user	0m0.043s
sys	0m0.079s
```

> 📝 **คำอธิบาย:** อ่าน log จากบนลงล่างแล้วจะเห็นเรื่องราวทั้งหมด — `WORKDIR`, `COPY requirements.txt .`, `RUN pip install` **ไม่มีอะไรเปลี่ยน** Docker จึงหยิบ layer เดิมมาใช้ (`CACHED`) · พอถึง `COPY . .` ไฟล์ในโฟลเดอร์เปลี่ยนไปแล้ว (เราแก้ `app.py`) มันจึงต้องทำใหม่ (`DONE`) และทุกขั้นถัดจากนั้นทำใหม่ตามไปด้วย · เพราะขั้นที่แพงที่สุดอยู่**ก่อน**จุดที่แตก เราจึงจ่ายแค่ 0.7 วินาที · **Docker ตัดสินว่าขั้น `COPY` แตกหรือไม่จาก checksum ของ "เนื้อไฟล์" ที่คัดลอกเข้าไป ไม่ใช่จากเวลาแก้ไขไฟล์ (timestamp)** — ถ้าสั่ง `touch app.py` เฉย ๆ โดยเนื้อหาไม่เปลี่ยน cache จะ**ไม่**แตก แต่พอแก้เนื้อหาแม้แต่ตัวอักษรเดียว checksum เปลี่ยนทันที cache จึงแตก

ทีนี้ build `bad` ด้วยการแก้ **ไฟล์เดียวกัน บรรทัดเดียวกัน** :

```bash
time docker build -f Dockerfile.bad -t cachelab-bad:1.0 .
```

✅ **Expected output** — ไม่มีคำว่า `CACHED` ที่ขั้น `pip install` เลย มันติดตั้ง package ใหม่ทั้งหมดอีกรอบ:

```
#7 [3/4] COPY . .
#7 DONE 0.0s
#8 [4/4] RUN pip install --no-cache-dir -r requirements.txt
#8 11.02 Successfully installed blinker-1.9.0 ... matplotlib-3.9.2 numpy-2.5.2 pandas-2.2.3 ... werkzeug-3.1.8
#8 DONE 11.2s
real	0m18.442s
```

> 📝 **คำอธิบาย:** ใน `Dockerfile.bad` ขั้น `COPY . .` อยู่ **ก่อน** `RUN pip install` — พอ `app.py` เปลี่ยน ขั้น `COPY . .` ก็แตก และตามกฎ "ขั้นใดเปลี่ยน ทุกขั้นถัดไปต้อง build ใหม่" ขั้น `pip install` ที่แพงที่สุดจึงต้องวิ่งใหม่ทั้งดุ้น **ทั้งที่ `requirements.txt` ไม่ได้ถูกแตะเลย**

![เทียบทีละขั้นว่า cache แตกจุดไหนใน Dockerfile.good กับ Dockerfile.bad หลังแก้ app.py หนึ่งบรรทัด](./images/theory-cache-break-point.svg)

> 🖼 **วิธีอ่านรูปนี้:** อ่านทีละคอลัมน์จากบนลงล่างแล้วมองหา **แถวสีแดงแถวแรก** ของแต่ละฝั่ง — นั่นคือจุดที่ cache แตก · ฝั่ง `good` จุดแตกอยู่ **ล่าง** ขั้น `RUN pip install` ขั้นแพงจึงยัง `CACHED` · ฝั่ง `bad` จุดแตกอยู่ **เหนือ** ขั้นนั้น ทุกอย่างใต้ลงไปจึงต้องสร้างใหม่หมด · ตัวเลขในรูปคือผลรันจริงชุดเดียวกับตารางข้างล่าง

### ตารางเทียบเวลาจริง (วัดในเครื่องเรียนของเอกสารนี้)

| Dockerfile | รอบที่ 1 — cold (ไม่มี cache) | รอบที่ 2 — หลังแก้ `app.py` 1 บรรทัด | ขั้น `RUN pip install` ในรอบที่ 2 |
|---|---|---|---|
| `Dockerfile.good` | **19.158 s** | **0.765 s** | `CACHED` |
| `Dockerfile.bad` | **18.929 s** | **18.442 s** | ทำใหม่ 11.2 s |

> **อ่านตารางให้เป็น :** คอลัมน์แรกเกือบเท่ากัน (ต่าง 0.2 วินาที) — ลำดับไม่มีผลตอน build ครั้งแรก · คอลัมน์ที่สองต่างกัน **~24 เท่า** และนี่คือคอลัมน์ที่เราจ่ายจริง **ทุกครั้งที่แก้โค้ด** วันหนึ่งอาจ build 20–50 รอบ · เวลาของแต่ละคนจะไม่ตรงกับตัวเลขนี้ (ขึ้นกับเน็ต/CPU) แต่ **อัตราส่วนต้องต่างกันชัดเจนแบบนี้**

> **กฎที่ต้องจำ :** เรียง Dockerfile จาก **"สิ่งที่เปลี่ยนน้อยที่สุด" ไปหา "สิ่งที่เปลี่ยนบ่อยที่สุด"** เสมอ — base image → system package → รายการ dependency → ติดตั้ง dependency → source code

## 5. Options ของ `docker build` ที่ต้องใช้เป็น

รูปแบบหลักของคำสั่งคือ `docker build [OPTIONS] PATH | URL | -`

> 📝 **คำอธิบาย:** เครื่องหมาย `|` ในบรรทัดบนแปลว่า "เลือกอย่างใดอย่างหนึ่ง" ระหว่าง path (`.`), URL หรือ `-` (อ่าน Dockerfile จาก stdin) — **ไม่ใช่ท่อของ shell** และไม่ใช่บรรทัดที่พิมพ์ตามได้ · ค่าที่เลือก **มีได้ตัวเดียวเท่านั้น** (ใส่เกินหนึ่งตัวเมื่อไร Docker ฟ้อง `requires 1 argument` ทันที) และตามรูปแบบมาตรฐานให้วางไว้ **ท้ายสุดเสมอ**

### 5.1 `-t` — ติดหลาย tag จากการ build ครั้งเดียว

```bash
docker build -f Dockerfile.good -t cachelab-good:1.1 -t cachelab-good:latest .
docker image ls cachelab-good
```

> 📝 **คำอธิบาย:** ใส่ `-t` ซ้ำได้กี่ครั้งก็ได้ เหมาะกับการติดทั้งเลขเวอร์ชันและ `latest` พร้อมกันโดยไม่ต้อง build สองรอบ · รูปแบบของ tag คือ `[registry/]repository[:tag]` ถ้าไม่ใส่ `:tag` Docker จะเติม `:latest` ให้เอง

✅ **Expected output** — จุดที่ต้องดูคือ **`1.1` กับ `latest` มี `ID` เดียวกัน** = มี image จริงตัวเดียว แค่มีสองชื่อ (ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้ · `1.0` เป็นคนละ ID เพราะ build คนละครั้ง):

```
#10 naming to docker.io/library/cachelab-good:1.1 done
#10 naming to docker.io/library/cachelab-good:latest done
IMAGE                  ID             DISK USAGE   CONTENT SIZE
cachelab-good:1.0      060290589b07        524MB          121MB
cachelab-good:1.1      6df39de8d09d        524MB          121MB
cachelab-good:latest   6df39de8d09d        524MB          121MB
```

### 5.2 `--no-cache` + `--pull` — บังคับสร้างใหม่ และดึง base image ใหม่

```bash
time docker build --no-cache -f Dockerfile.good -t cachelab-good:1.0 .
time docker build --pull -f Dockerfile.good -t cachelab-good:1.0 .
```

> 📝 **คำอธิบาย:** `--no-cache` ใช้เมื่อสงสัยว่า cache "โกหก" เช่น `RUN apt-get update` ที่ค้าง index เก่า หรือ dependency ที่ pin เวอร์ชันไม่ครบแล้วอยากบังคับไปหยิบของใหม่ ราคาที่จ่ายคือเวลาที่กลับไปเท่ารอบ cold · `--pull` เป็นคนละเรื่อง : ปกติถ้ามี `python:3.12-slim` ในเครื่องแล้ว Docker จะใช้ตัวในเครื่องเลยโดยไม่ถาม registry ส่วน `--pull` สั่งให้ไปเช็กก่อนว่ามี image ใหม่กว่าภายใต้ tag เดิมหรือเปล่า (tag อย่าง `3.12-slim` ถูกขยับไปชี้ image ใหม่ได้ทุกเดือน — เป็นเหตุผลที่ image ที่ pin tag ไว้ก็ยังเปลี่ยนได้)

✅ **Expected output** — คำสั่งแรก : ขั้น `RUN pip install` ทำใหม่จริง 10.8 วินาที · คำสั่งที่สอง : ขั้น `#2 load metadata` กลายเป็น **1.4s** (เวลาที่วิ่งไปถาม registry) ส่วนขั้นอื่นยัง `CACHED` เพราะ base image ไม่ได้เปลี่ยนจริง:

```
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 DONE 10.8s
real	0m18.018s

#2 [internal] load metadata for docker.io/library/python:3.12-slim
#2 DONE 1.4s
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 CACHED
real	0m1.876s
```

> ⚠️ **จุดที่คนพลาดบ่อยที่สุด :** `--no-cache` **ไม่ได้**ดึง base image ใหม่ให้ มันแค่ไม่ใช้ cache ของขั้นต่าง ๆ ส่วน `FROM` ยังใช้ image เดิมในเครื่อง · ถ้าต้องการ "ของใหม่หมดจริง ๆ" ต้องสั่งคู่กัน : `docker build --pull --no-cache -f Dockerfile.good -t cachelab-good:1.0 .`
> **ของแปลกที่จะเห็นจริงบน Docker 29 :** ขั้น `#6 WORKDIR /app` ยังขึ้น `CACHED` แม้สั่ง `--no-cache` เพราะ BuildKit จัดการขั้นที่เป็น metadata เบา ๆ ต่างจากขั้นที่รันจริง — **จุดที่ใช้ตัดสินว่า `--no-cache` ทำงานหรือไม่คือขั้น `RUN` ต่างหาก**

### 5.3 `--progress=plain` — เปิด log แบบเต็มไว้ไล่ปัญหา

```bash
docker build --progress=plain -f Dockerfile.good -t cachelab-good:1.0 .
```

> 📝 **คำอธิบาย:** เวลารันในหน้าจอปกติ Docker จะย่อ log ให้สั้น (บรรทัดยุบรวมกัน มีแถบความคืบหน้า) ซึ่งอ่านสบายแต่**กลืนบรรทัด error ของคำสั่งข้างใน `RUN`** · `--progress=plain` พิมพ์ทุกบรรทัดเรียงตรง ๆ พร้อมเลขวินาทีนำหน้า (`#8 0.979 Collecting flask...`) เหมาะกับตอนดีบัก build ที่พังและตอนเก็บ log ลงไฟล์ · ถ้าเอา output ไปเข้า pipe หรือเขียนลงไฟล์อยู่แล้ว Docker จะใช้รูปแบบ plain ให้เองอัตโนมัติ · `verify.sh` ของแล็บนี้ก็ใช้ option นี้เพื่ออ่านคำว่า `CACHED` จาก log

✅ **Expected output** — เห็นเลขขั้น `#N` และสถานะของทุกขั้นครบ:

```
#6 [2/5] WORKDIR /app
#6 CACHED
#7 [3/5] COPY requirements.txt .
#7 CACHED
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 CACHED
```

### 5.4 `--build-arg` และ `--target` — รู้จักรูปแบบไว้ก่อน

สอง option นี้ต้องมี Dockerfile ที่รองรับก่อนถึงจะใช้ได้ (จะลงมือทำเต็ม ๆ ใน **LAB 4** และ **LAB 7**) ตอนนี้จำรูปแบบไว้ :

```bash
# ---- สองบรรทัดนี้เป็น "รูปแบบให้อ่าน" ยังไม่ต้องพิมพ์ตามในโฟลเดอร์นี้ ----
# (ไม่มีไฟล์ชื่อ Dockerfile เฉย ๆ และไม่มี ARG/stage รองรับ สั่งไปก็ได้ error)

# ส่งค่าเข้าไปตอน build — Dockerfile ต้องประกาศ ARG APP_ENV ไว้ก่อน
docker build --build-arg APP_ENV=production -t myapp:1.0 .

# เลือก build ถึงแค่ stage ที่ต้องการ — Dockerfile ต้องเขียน FROM ... AS test ไว้
docker build --target test -t myapp:test .
```

> 📝 **คำอธิบาย:** ถ้า Dockerfile ไม่ได้ประกาศ `ARG APP_ENV` ค่าที่ส่งไปจะถูกทิ้งพร้อมคำเตือน ไม่ใช่ error — เป็นกับดักที่ทำให้คนงงว่า "ส่งค่าไปแล้วทำไมไม่มีผล" · **ห้ามส่ง password หรือ token ผ่าน `--build-arg`** เพราะค่าจะไปโผล่ในประวัติของ image (`docker history`) ที่ใครก็อ่านได้

## 6. `docker history` — layer ไหนกินพื้นที่เท่าไร

ให้นึกถึงภาพกอง layer ในส่วนทฤษฎี: `docker history` กำลังคลี่กองนั้นจากบนลงล่าง เพื่อดูต้นทุนของชั้นที่ cache รักษาไว้ในข้อ 4

```bash
docker history cachelab-good:1.0
docker history --no-trunc --format 'table {{.Size}}\t{{.CreatedBy}}' cachelab-good:1.0
```

> 📝 **คำอธิบาย:** แสดงทุก layer เรียง **จากบนสุด (ใหม่สุด) ลงไปหาล่างสุด (base image)** · คอลัมน์ `SIZE` คือขนาดที่ layer นั้น **เพิ่มเข้ามา** ไม่ใช่ขนาดสะสม · คำว่า `<missing>` ในคอลัมน์ IMAGE ไม่ใช่ error — เป็นเรื่องปกติของ layer ที่**ไม่มี image ID ของตัวเองให้อ้างถึง** (มีแต่ layer บนสุดเท่านั้นที่ได้ ID/tag) · บรรทัดที่สองคือเวอร์ชันที่ไม่ตัดข้อความท้ายด้วย `…` : `--no-trunc` เลิกตัดข้อความ ส่วน `--format` เลือกเฉพาะคอลัมน์ที่อยากดู (`table` ข้างหน้าทำให้ยังมีหัวตาราง) · **นี่คือเครื่องมือหาว่า image อ้วนเพราะอะไร**

✅ **Expected output** — จุดที่ต้องชี้ให้เห็นคือ layer **`RUN ... pip install ...` = 269MB** ตัวเดียวใหญ่กว่าทุก layer ที่เหลือของเรารวมกัน ส่วน `COPY . .` ที่เราแก้บ่อย ๆ มีแค่ 16.4kB (IMAGE ID และเวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
IMAGE          CREATED          CREATED BY                                      SIZE      COMMENT
cd37a50f03d4   32 seconds ago   CMD ["python" "app.py"]                         0B        buildkit.dockerfile.v0
<missing>      32 seconds ago   EXPOSE [8182/tcp]                               0B        buildkit.dockerfile.v0
<missing>      32 seconds ago   ENV BUILD_ID=good-1                             0B        buildkit.dockerfile.v0
<missing>      32 seconds ago   COPY . . # buildkit                             16.4kB    buildkit.dockerfile.v0
<missing>      32 seconds ago   RUN /bin/sh -c pip install --no-cache-dir -r…   269MB     buildkit.dockerfile.v0
<missing>      43 seconds ago   COPY requirements.txt . # buildkit              12.3kB    buildkit.dockerfile.v0
<missing>      2 minutes ago    WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
        ... (ตัดท่อนล่าง : layer ของ base image python:3.12-slim รวม 41.4MB + 87.4MB) ...
```

> **เชื่อมกับข้อ 4 :** layer 269MB ตัวนี้แหละคือสิ่งที่ `Dockerfile.bad` สร้างใหม่ทุกครั้งที่เราแก้โค้ดแม้แต่ตัวอักษรเดียว ส่วน `Dockerfile.good` หยิบของเดิมมาใช้

## 7. คืนพื้นที่ : dangling image, `docker system df` และ `builder prune`

```bash
sed -i 's/# APP_VERSION = 2/# APP_VERSION = 3/' app.py
docker build -f Dockerfile.good .
docker image ls -a
docker image ls -f dangling=true
```

> 📝 **คำอธิบาย:** สังเกตว่าคำสั่ง build บรรทัดนี้ **ไม่มี `-t` เลย** — image ที่ได้จึงไม่มีชื่อ กลายเป็น **dangling image** (image ที่ไม่มี tag ชี้ถึง) · `docker image ls -a` แสดง image ทั้งหมดรวมตัวที่ไม่มี tag · `-f dangling=true` กรองเฉพาะตัวที่ไม่มี tag = รายการที่ `docker image prune` จะลบ **ควรดูก่อนลบทุกครั้ง** · **หมายเหตุ:** ตารางของคุณจะมีแถวมากกว่าในตัวอย่างข้างล่าง เพราะยังมี `cachelab-bad:1.0`, `cachelab-good:1.1` และ `cachelab-good:latest` ที่สร้างไว้ในข้อ 3 กับ 5.1 อยู่ด้วย (ผลตัวอย่างนี้เก็บจากเครื่องที่เหลือ image น้อยกว่า) — **ให้ดูเฉพาะแถว `<untagged>`** ว่ามีโผล่ขึ้นมาจริงไหม

✅ **Expected output** — บรรทัด `naming to moby-dangling@sha256:...` บอกตรง ๆ ว่ามันไม่มีชื่อ และในตารางโผล่แถว `<untagged>`:

```
#10 naming to moby-dangling@sha256:df7d12bbb34cbe2c5e477887e6deb67e0c27b57af0c9d0ab6fc6ab44740e4bd3 done
IMAGE               ID             DISK USAGE   CONTENT SIZE
cachelab-good:1.0   9017cf37fb1d        524MB          121MB
python:3.12-slim    dd29372629ee        179MB         45.4MB
<untagged>          df7d12bbb34c        524MB          121MB
IMAGE        ID             DISK USAGE   CONTENT SIZE
<untagged>   df7d12bbb34c        524MB          121MB
```

ลบทิ้งด้วย `docker image prune` แล้วพิมพ์ `y` เมื่อมันถาม

> 📝 **คำอธิบาย:** **อย่าเพิ่งเติม `-f` ตอนเรียน** ให้ Docker แสดงคำเตือนและถามยืนยันก่อนเสมอ · `docker image prune` ลบเฉพาะ **dangling** · ส่วน `docker image prune -a` ขยายขอบเขตเป็น "image ทุกตัวที่ไม่มี container ใช้อยู่" ซึ่งกินขาดกว่ามาก ใช้เมื่อรู้ตัวจริง ๆ ว่าทำอะไรอยู่

✅ **Expected output** — ดูบรรทัด `Total reclaimed space` (ตัวเลขและ sha256 ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
WARNING! This will remove all dangling images.
Are you sure you want to continue? [y/N] Deleted Images:
untagged: sha256:df7d12bbb34cbe2c5e477887e6deb67e0c27b57af0c9d0ab6fc6ab44740e4bd3
        ... (ตัดท่อนกลาง) ...
Total reclaimed space: 27.76kB
```

> 📝 **ทำไมลบ image 524MB แล้วคืนมาแค่ 27.76kB?** เพราะ layer เกือบทั้งหมดของมัน (รวม layer `pip install` 269MB) ยัง**ใช้ร่วมกัน**กับ `cachelab-good:1.0` ที่ยังมี tag อยู่ — Docker ลบได้เฉพาะส่วนที่ไม่มีใครใช้แล้ว

> ⚠️ **จุดที่เปลี่ยนไปใน Docker 29 :** เอกสารเก่า ๆ บอกว่า "build ทับ tag เดิมแล้วจะเหลือ image `<none>` ค้างเต็มเครื่อง" — **บน Docker 29 ที่ใช้ containerd image store ไม่เป็นแบบนั้นแล้ว** ลอง build ทับ `-t cachelab-good:1.0` ซ้ำกี่รอบก็ไม่มี `<untagged>` งอกออกมา (ลองเองได้: build ซ้ำแล้วสั่ง `docker image ls -f dangling=true` จะว่าง) · วิธีทำให้เกิด dangling image บนเวอร์ชันนี้คือ **build โดยไม่ใส่ `-t`** อย่างที่เราเพิ่งทำ · ถ้าเครื่องของคุณ Docker เก่ากว่านี้จะเห็น `<none>` งอกจากการ build ทับ tag เดิมตามคู่มือเก่า — ทั้งสองแบบใช้ `docker image prune` เก็บกวาดเหมือนกัน

คืนไฟล์กลับก่อนไปตอนถัดไป : `sed -i 's/# APP_VERSION = 3/# APP_VERSION = 1/' app.py`

### พื้นที่หายไปไหน — `docker system df`

```bash
docker system df
```

> 📝 **คำอธิบาย:** คำสั่งนี้ **อ่านอย่างเดียว ไม่ลบอะไร** ปลอดภัย 100% · `SIZE` = พื้นที่ที่ใช้จริง · `RECLAIMABLE` = ส่วนที่ลบแล้วได้คืน · `ACTIVE` = จำนวนที่ยังมีคนใช้อยู่ · แถว **Build Cache** คือของที่ BuildKit เก็บไว้ให้ build ครั้งหน้าเร็ว — มันโตเงียบ ๆ และมักเป็นตัวกินพื้นที่อันดับหนึ่งบนเครื่อง dev · ตัวเลขทุกช่องในตัวอย่างข้างล่างขึ้นกับสภาพเครื่องตอนเก็บผล (เช่นคอลัมน์ `ACTIVE` ของแถว Images เป็น 1 เพราะตอนนั้นมี container รันอยู่ ส่วนของคุณตอนนี้ยังไม่มี container จึงเป็น 0) — **ให้ดูที่ "แถว Build Cache ใหญ่แค่ไหน" ไม่ใช่ตัวเลขตรงกันเป๊ะ**

✅ **Expected output** — จุดที่ต้องดูคือแถว `Build Cache` : **1.781GB** โดยคืนได้ **1.391GB** (ตัวเลขของแต่ละคนขึ้นกับว่า build ไปกี่รอบ):

```
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
Images          4         1         873.8MB   349.5MB (39%)
        ... (ตัดแถว Containers และ Local Volumes) ...
Build Cache     24        0         1.781GB   1.391GB
```

ล้าง build cache แล้วดูซ้ำ :

```bash
docker builder prune
docker system df
```

> 📝 **คำอธิบาย:** ตอบ `y` เมื่อถาม · `docker builder prune` **ไม่ได้ลบ image** แค่ลบ cache ที่ BuildKit ใช้เร่ง build — ผลข้างเคียงคือ **build ครั้งถัดไปจะช้าเท่ารอบ cold** · แบบไม่ใส่ `-a` จะเก็บ cache ที่ยังถูกใช้อยู่ไว้

✅ **Expected output** — พิมพ์ตารางก้อน cache ที่ลบ ปิดท้ายด้วย `Total: 1.391GB` แล้ว Build Cache ลดจาก **1.781GB → 390.8MB** และ RECLAIMABLE เหลือ `0B` (ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
WARNING! This will remove all dangling build cache. Are you sure you want to continue? [y/N] ID			RECLAIMABLE	SIZE		LAST ACCESSED
kobpmczrkrovkc8ityabmlt3o               	true 	347.6MB   	3 minutes ago
        ... (ตัดท่อนกลาง รวม 17 ก้อน) ...
Total:	1.391GB
TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE
        ... (ตัดแถว Images, Containers และ Local Volumes ซึ่งไม่เปลี่ยน) ...
Build Cache     7         0         390.8MB   0B
```

ราคาที่ต้องจ่าย — ลอง `time docker build -f Dockerfile.good -t cachelab-good:1.0 .` ใหม่ทันที

✅ **Expected output** — **ไม่มีคำว่า `CACHED` เหลือแม้แต่ขั้นเดียว** ทุกอย่างกลับไปเริ่มใหม่:

```
#6 [2/5] WORKDIR /app
#6 DONE 0.0s
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 DONE 11.1s
real	0m18.625s
```

> **สรุปข้อนี้ :** `builder prune` คือการแลก **พื้นที่ดิสก์** กับ **เวลา build ครั้งหน้า** ไม่มีอะไรฟรี — สั่งเมื่อดิสก์ใกล้เต็มจริง ๆ ไม่ใช่สั่งเป็นนิสัยทุกวัน

## 8. `.dockerignore` กับ layer cache

`.dockerignore` มักถูกสอนว่า "ไว้ลดขนาด build context" ซึ่งจริงแต่ไม่ครบ — ผลที่สำคัญกว่าคือ **มันกันไม่ให้ cache แตกโดยไม่จำเป็น** พิสูจน์กัน :

```bash
grep -n 'notes.md' .dockerignore
echo "note v1" > notes.md
docker build -f Dockerfile.good -t cachelab-good:1.0 .      # build ให้ cache นิ่งก่อน
echo "note v2 — แก้แล้ว" > notes.md
time docker build -f Dockerfile.good -t cachelab-good:1.0 .
```

> 📝 **คำอธิบาย:** `notes.md` ถูกระบุไว้ใน `.dockerignore` แล้ว (บรรทัดที่ 6) · build รอบแรกเพื่อให้ cache นิ่ง จากนั้นแก้เนื้อหา `notes.md` แล้ว build ใหม่ · **ทายก่อนดูผล :** `COPY . .` จะแตกไหม ในเมื่อไฟล์ในโฟลเดอร์เปลี่ยนไปจริง ๆ?

✅ **Expected output** — ทุกขั้นยัง `CACHED` **รวมถึง `COPY . .`** และบรรทัด `transferring context: 95B` บอกว่า `notes.md` ไม่เคยเดินทางเข้า build context เลยด้วยซ้ำ:

```
#4 transferring context: 95B done
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 CACHED
#9 [5/5] COPY . .
#9 CACHED
real	0m0.553s
```

ทีนี้เอา `notes.md` ออกจาก `.dockerignore` แล้วทำแบบเดิมซ้ำ เพื่อดูความต่าง :

```bash
sed -i '/^notes.md$/d' .dockerignore
echo "note v3 — ไม่ถูก ignore แล้ว" > notes.md
docker build -f Dockerfile.good -t cachelab-good:1.0 .
```

✅ **Expected output** — คราวนี้ `transferring context` โตขึ้นเป็น **270B** และ **`COPY . .` เปลี่ยนจาก `CACHED` เป็น `DONE`** = cache แตกเพราะไฟล์ที่ไม่เกี่ยวกับแอปเลย:

```
#4 transferring context: 270B done
#9 [5/5] COPY . .
#9 DONE 0.0s
```

คืน `.dockerignore` กลับแล้วลบไฟล์ทดลองทิ้ง : `sed -i 's|^images/$|images/\nnotes.md|' .dockerignore && rm -f notes.md`

> **บทเรียนสำคัญ :** ไฟล์อย่าง `.git/`, `node_modules/`, `test_logs/`, ไฟล์ log, ไฟล์ note ส่วนตัว ล้วนเปลี่ยนบ่อยมากแต่ไม่มีผลกับแอปเลย — ถ้าไม่ใส่ใน `.dockerignore` มันจะไปทำให้ `COPY . .` แตกทุกครั้ง แล้วลากทุกขั้นถัดไป build ใหม่ตามไปด้วย · `.dockerignore` จึงเป็น **เครื่องมือเร่ง build** ไม่ใช่แค่เครื่องมือลดขนาด

## 9. รันแอปจริงบนพอร์ต 8182

```bash
docker build -f Dockerfile.good -t cachelab-good:1.0 .
docker rm -f cachelab-web 2>/dev/null
docker run -d --name cachelab-web -p 8182:8182 cachelab-good:1.0
sleep 3
docker ps --filter name=cachelab-web
curl -s http://localhost:8182/health
docker image inspect cachelab-good:1.0 --format '{{json .Config.Env}}'
```

> 📝 **คำอธิบาย:** `-d` รันเบื้องหลังแล้วคืน prompt ทันที (ต่างจาก `-it` ที่ยึดหน้าจอไว้) · `--name cachelab-web` ตั้งชื่อเพื่ออ้างถึงง่าย · `-p 8182:8182` = `พอร์ตของเครื่องเรียน : พอร์ตข้างใน container` ต้องใส่เอง `EXPOSE` ใน Dockerfile ไม่ได้เปิดให้ · `sleep 3` รอ Flask boot ก่อนยิง curl ไม่งั้นจะเจอ `Connection refused` · `image inspect --format '{{json .Config.Env}}'` ดึงเฉพาะ ENV ที่ฝังอยู่ใน image ออกมา

✅ **Expected output** — `STATUS` เป็น `Up ...` · `/health` ตอบ JSON · ท้ายรายการ ENV มี **`BUILD_ID=good-1`** (ถ้า build จาก `Dockerfile.bad` จะเป็น `bad-1`) — container ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้:

```
CONTAINER ID   IMAGE               COMMAND           CREATED         STATUS         PORTS                                         NAMES
67c5c2f52503   cachelab-good:1.0   "python app.py"   4 seconds ago   Up 4 seconds   0.0.0.0:8182->8182/tcp, [::]:8182->8182/tcp   cachelab-web

{"status":"ok"}
["PATH=/usr/local/bin:...","LANG=C.UTF-8","PYTHON_VERSION=3.12.14",...,"BUILD_ID=good-1"]
```

เปิดดูหน้าเว็บ — ถ้าตอน `docker run` ของข้อ 0 ใส่ `-p 8182:8182` ไว้แล้ว เปิด `http://localhost:8182` ได้เลย · ถ้าใช้ VS Code จะ forward เพิ่มก็ได้ที่แท็บ **PORTS** → **Forward a Port** → พิมพ์ `8182`

![หน้าเว็บของแอปแสดง BUILD_ID กับเวอร์ชันของ dependency ที่ติดตั้งอยู่ใน layer](./images/app-8182.png)

> 📝 **จุดที่ต้องดูในหน้านี้:** `BUILD_ID = good-1` ยืนยันว่า image นี้มาจาก `Dockerfile.good` · เวอร์ชัน **Flask 3.1.2 · pandas 2.2.3 · requests 2.32.3 · matplotlib 3.9.2** ตรงกับที่ pin ไว้ใน `requirements.txt` เป๊ะ — ทั้งหมดนี้คือเนื้อหาของ layer 269MB ที่เห็นใน `docker history` · `Hostname` คือ container ID สั้น (ของแต่ละคนจะไม่ตรงกับภาพนี้)

เสร็จแล้วเก็บ container ทิ้ง : `docker rm -f cachelab-web`

## 10. ตรวจงานอัตโนมัติด้วย `verify.sh`

```bash
./verify.sh
```

> 📝 **คำอธิบาย:** สคริปต์จะ build ทั้งสอง Dockerfile, แก้ `app.py` ให้เอง แล้วตรวจว่า `good` ได้ `CACHED` ที่ขั้น `pip install` จริงและ `bad` ต้อง build ใหม่จริง, ทดสอบ `.dockerignore`, แล้วรัน container ยิง `/health` — จบแล้ว **คืนไฟล์ `app.py` กลับให้เองและลบ container ชั่วคราวทิ้ง** แต่ **ไม่ลบ image ของเรา** · ถ้าขึ้น `Permission denied` ให้สั่ง `chmod +x verify.sh` ก่อน · ใช้เวลาราว 1 นาที (ต้องรอ `Dockerfile.bad` ติดตั้ง package ใหม่จริงเพื่อพิสูจน์)

✅ **Expected output** — ต้องได้ `[PASS]` ครบทุกบรรทัดและปิดท้ายด้วย `ALL CHECKS PASSED`:

```
 LAB 2 — Layer Cache & Build Options : verify
==============================================
[PASS] ไฟล์ของแล็บครบ (app.py, requirements.txt, Dockerfile.good, Dockerfile.bad, .dockerignore)
        ... (ตัดท่อนกลาง 4 บรรทัด : build ทั้งสอง image, docker image ls, แก้ app.py) ...
[PASS] Dockerfile.good : ขั้น RUN pip install เป็น CACHED หลังแก้ app.py
[PASS] Dockerfile.bad : ขั้น RUN pip install ถูก build ใหม่ (cache แตก) — ลำดับคำสั่งมีผลจริง
        ... (ตัดท่อนกลาง 2 บรรทัด : คืนไฟล์ app.py, .dockerignore มี notes.md) ...
[PASS] แก้ไฟล์ที่ถูก .dockerignore แล้ว ขั้น COPY . . ยังเป็น CACHED
[PASS] docker history cachelab-good:1.0 เห็น layer ของ RUN pip install
[PASS] container cachelab-web ตอบ /health ว่า status ok บนพอร์ต 8182
        ... (ตัดท้าย 2 บรรทัด : หน้าเว็บ Layer Cache Lab, ลบ container — รวมทั้งหมด 14 บรรทัด) ...
----------------------------------------------
ALL CHECKS PASSED
```

## ทดลองเพิ่มเติม (~8 นาที)

> แกนหลักของแล็บจบแล้ว — หัวข้อต่อจากนี้เลือกทำตามเวลาที่มี แต่ข้อ 💥 **ทำให้พัง** อยู่ในเช็กลิสต์ท้ายแล็บ เพราะการอ่าน error ให้ออกคือทักษะที่ใช้จริงมากที่สุด

### 1) แก้ `requirements.txt` — cache แตกตั้งแต่ขั้นไหน?

ข้อ 4 พิสูจน์แล้วว่าแก้ `app.py` ไม่กระทบ cache ของ `Dockerfile.good` — แล้วถ้าแก้ **รายการ dependency** ล่ะ?

```bash
cp requirements.txt /tmp/req.bak
echo "python-dotenv==1.0.1" >> requirements.txt
time docker build -f Dockerfile.good -t cachelab-good:1.0 .
```

> 📝 **คำอธิบาย:** เพิ่ม package หนึ่งตัวต่อท้ายไฟล์ · `cp ... /tmp/req.bak` สำรองไว้คืนกลับทีหลัง · **ทายก่อนดูผล :** `Dockerfile.good` ที่เคยเร็ว 0.7 วินาที จะยังเร็วอยู่ไหม?

✅ **Expected output** — คราวนี้ `COPY requirements.txt .` แตก (`DONE` ไม่ใช่ `CACHED`) แล้วลาก `pip install` ให้ทำใหม่ตามไปด้วย เวลากลับไปเท่ารอบ cold:

```
#7 [3/5] COPY requirements.txt .
#7 DONE 0.0s
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 11.74 Successfully installed ... python-dotenv-1.0.1 ... werkzeug-3.1.8
#8 DONE 12.0s
real	0m19.240s
```

> **อ่านให้เป็น :** นี่ไม่ใช่ข้อเสียของ `Dockerfile.good` — **มันถูกต้องแล้ว** เพราะรายการ dependency เปลี่ยนจริง จึงต้องติดตั้งใหม่จริง · ประเด็นคือ dependency เปลี่ยน **เดือนละครั้ง** ส่วน source code เปลี่ยน **วันละสิบครั้ง** เราจึงวางสิ่งที่เปลี่ยนน้อยไว้ก่อน เพื่อจ่ายค่าติดตั้งใหม่ให้น้อยที่สุด

คืนไฟล์กลับ : `cp /tmp/req.bak requirements.txt`

### 2) ทำให้พัง — สั่ง `docker build` แบบผิด ๆ แล้วอ่าน error จริง

> เคส "ลืมจุด `.` ท้ายคำสั่ง" ทำไปแล้วใน **LAB 1 ทดลอง ง.** — ที่นี่ต่อยอดเป็นอีกสองเคสที่ทำให้ error หน้าตาเดียวกันโผล่มาได้

```bash
docker build . -t myapp:1.0 extra                # มี argument เกินมา (context ต้องมีตัวเดียว)
docker build -f Dockerfile.prod -t myapp:1.0 .   # -f ชี้ไฟล์ที่ไม่มีอยู่
```

> 📝 **คำอธิบาย:** บรรทัดแรกให้ error **ตัวเดียวกับตอนลืมจุด** ทั้งที่เราใส่จุดครบ — เพราะกติกาคือ **context มีได้ตัวเดียวและต้องอยู่ท้ายสุด** พอมี `extra` ต่อท้าย Docker จึงนับว่าได้ argument มา 2 ตัว · บรรทัดที่สองคือเคสที่เจอบ่อยพอกัน คือพิมพ์ชื่อไฟล์ผิดตัวอักษรเดียว หรือสั่ง build จากคนละโฟลเดอร์กับที่คิด (ในโฟลเดอร์นี้มีแต่ `Dockerfile.good` กับ `Dockerfile.bad`)

✅ **Expected output** — บรรทัดแรกยังไม่ทันเริ่ม build เลย ส่วนบรรทัดที่สอง **เริ่ม build ไปแล้ว** (มีขั้น `#1`) ก่อนจะพังตอนอ่านไฟล์ · ทั้งคู่คืน exit code 1:

```
ERROR: docker: 'docker buildx build' requires 1 argument

Usage:  docker buildx build [OPTIONS] PATH | URL | -

Run 'docker buildx build --help' for more information
exit code = 1

#1 [internal] load build definition from Dockerfile.prod
#1 transferring dockerfile: 2B done
#1 DONE 0.0s
ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile.prod: no such file or directory
exit code = 1
```

> 📝 **แปล error ให้เป็น:** `requires 1 argument` = "ต้องมี argument **1 ตัวพอดี**" — จึงฟ้องทั้งตอน **ขาด** (ลืมจุด ตามที่เจอใน LAB 1) และตอน **เกิน** (มี `extra` ต่อท้ายอย่างในบรรทัดแรก) และบรรทัด `Usage:` ที่ตามมาคือคำใบ้ว่า `PATH | URL | -` ต้องอยู่**ท้ายสุดตัวเดียว** → **แก้โดยลบ argument ส่วนเกินออก** · ส่วน `transferring dockerfile: 2B` แปลว่า "ไฟล์เปล่า" เป็นสัญญาณแรกว่าผิดปกติ แล้ว `open Dockerfile.prod: no such file or directory` ก็บอกชัดว่าหาไฟล์ไม่เจอ → **แก้โดย `ls Dockerfile*` แล้วสะกดให้ตรง** · ระวังว่า path ของ `-f` อ้างอิงจาก**โฟลเดอร์ที่เรายืนอยู่** ไม่ใช่จาก build context

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ERROR: docker: 'docker buildx build' requires 1 argument` | ลืมใส่ build context (จุด `.`) ท้ายคำสั่ง หรือใส่ argument เกิน 1 ตัว | เติม `.` เป็น**ตัวสุดท้าย**ของคำสั่งเสมอ : `docker build -t myapp:1.0 .` |
| `failed to read dockerfile: open Dockerfile.xxx: no such file or directory` | `-f` ชี้ไฟล์ที่ไม่มีอยู่ / สะกดผิด / ยืนอยู่คนละโฟลเดอร์ | `ls Dockerfile*` แล้วสะกดชื่อให้ตรง · `pwd` เช็กว่ายืนในโฟลเดอร์แล็บจริง |
| แก้โค้ดนิดเดียวแต่ build ใหม่ทีไรก็นานเป็นนาทีทุกครั้ง | Dockerfile เรียงผิดลำดับแบบ `Dockerfile.bad` (`COPY . .` อยู่ก่อน `RUN` ติดตั้ง) | ย้าย `COPY requirements.txt .` + `RUN pip install` ขึ้นไปไว้**ก่อน** `COPY . .` แล้ว build ใหม่ · ดูใน log ว่าขั้น `pip install` ขึ้น `CACHED` แล้วหรือยัง |
| ทำข้อ 4 ซ้ำรอบสอง แล้ว `Dockerfile.bad` กลับขึ้น `CACHED` ที่ขั้น `pip install` | เคย build เนื้อหาชุด **เดียวกันเป๊ะ** นี้ไปแล้วรอบก่อน BuildKit จึงหยิบ cache เก่ามาใช้ได้ (ไม่ใช่ว่าลำดับดีขึ้น) | ตั้งค่าใหม่ที่ไม่เคยใช้ เช่น `sed -i "s/^# APP_VERSION = .*/# APP_VERSION = $(date +%s)/" app.py` แล้วลองใหม่ · หรือล้างด้วย `docker builder prune -af` ก่อน (`verify.sh` ของแล็บนี้ใส่ timestamp ให้อัตโนมัติด้วยเหตุผลนี้) |
| build แล้วได้ของเก่า ทั้งที่แก้ไฟล์ไปแล้ว | Docker ใช้ cache ของขั้นนั้นอยู่ (มักเกิดกับ `RUN apt-get update` หรือ dependency ที่ไม่ได้ pin เวอร์ชัน) | สั่ง `docker build --no-cache ...` ครั้งเดียวเพื่อบังคับทำใหม่ · ระยะยาวให้ **pin เวอร์ชันทุกตัว** ใน `requirements.txt` |
| สั่ง `--no-cache` แล้ว base image ยังเป็นตัวเก่าอยู่ | `--no-cache` ไม่แตะ `FROM` — ไม่ได้ไปถาม registry ว่ามี image ใหม่ไหม | ใช้คู่กัน : `docker build --pull --no-cache -f Dockerfile.good -t cachelab-good:1.0 .` |
| ดิสก์เต็มทั้งที่ลบ image ไปหมดแล้ว | **Build cache** ของ BuildKit ยังอยู่ — `docker image rm` ไม่แตะมันเลย | `docker system df` ดูแถว Build Cache ก่อน แล้ว `docker builder prune` (build ครั้งหน้าจะช้าลง เป็นเรื่องปกติ) |
| ลบ image ตัวใหญ่ทิ้งแล้ว แต่ `Total reclaimed space` ได้คืนแค่ไม่กี่ kB | layer ส่วนใหญ่ยัง**ใช้ร่วมกัน**กับ image ตัวอื่นที่ยังอยู่ | เป็นพฤติกรรมปกติของ layer ที่ share กัน ไม่ใช่ bug · ถ้าอยากได้พื้นที่คืนจริงต้องลบ image ทุกตัวที่ใช้ layer ชุดนั้น |
| หา image `<none>` ไม่เจอทั้งที่ build ทับ tag เดิมหลายรอบ | Docker 29 (containerd image store) ไม่ทิ้ง dangling image จากการ build ทับ tag เดิมแล้ว | ไม่ต้องแก้อะไร — ถ้าอยากเห็นตัวอย่าง dangling image ให้ build โดย**ไม่ใส่ `-t`** แล้วดูด้วย `docker image ls -f dangling=true` |
| `docker run -p 8182:8182 ...` ขึ้น `port is already allocated` หรือ `curl .../health` ขึ้น `Connection refused` | มี container เก่าจองพอร์ตอยู่ / ยิง curl เร็วเกินไป Flask ยัง boot ไม่เสร็จ หรือ container ตายไปแล้ว | `docker rm -f cachelab-web` แล้วรันใหม่ · รอ 2–3 วินาทีก่อน curl · ถ้ายังไม่ได้ให้ดู `docker logs cachelab-web` และ `docker ps -a` ว่า STATUS เป็น `Exited` หรือเปล่า |

## เก็บกวาด (Cleanup)

ลบของที่สร้างในแล็บนี้ **ข้างในเครื่องเรียน** ก่อน :

```bash
docker rm -f cachelab-web 2>/dev/null
docker image rm cachelab-good:1.0 cachelab-good:1.1 cachelab-good:latest cachelab-bad:1.0
docker container prune
docker image ls
```

> 📝 **คำอธิบาย:** `docker image rm` ระบุเป้าหมายชัดเจนกว่า `prune` มาก จึงปลอดภัยกว่าเมื่อรู้ว่าจะลบอะไร · `docker container prune` เก็บ container ที่หยุดแล้วทุกตัว (**ไม่**ลบตัวที่กำลังรัน และ**ไม่**ลบ volume) ตอบ `y` เมื่อถาม · เก็บ `python:3.12-slim` ไว้ใช้ต่อใน LAB ถัดไปได้ ไม่ต้องลบ

✅ **Expected output** — เหลือแค่ base image และไม่มี container ค้าง (sha256 ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
Untagged: cachelab-good:1.0
Deleted: sha256:52268e56ba6fe79311fc8dc48a2d2b840bf8bf0be9b74c85b6bdb6ffb3a36e8a
        ... (ตัดท่อนกลาง : Untagged ของ 1.1, latest และ cachelab-bad:1.0) ...
WARNING! This will remove all stopped containers.
Are you sure you want to continue? [y/N] Total reclaimed space: 0B
IMAGE              ID             DISK USAGE   CONTENT SIZE   EXTRA
python:3.12-slim   dd29372629ee        179MB         45.4MB
```

จากนั้น **ออกจาก SSH** (พิมพ์ `exit`) แล้วลบเครื่องเรียนบนเครื่องของเราเอง :

```bash
docker rm -f devtools-df-lab2
docker ps -a --filter "name=^devtools-"
```

> 📝 **คำอธิบาย:** `docker rm -f` ลบ container ที่ยังรันอยู่ได้เลย (บังคับหยุดก่อน) · `--filter "name=^devtools-"` กรองเฉพาะ container ของชุด LAB นี้ (`^` คือจุดเริ่มต้นของชื่อ) · ถ้าจะทำ LAB อื่นต่อ ให้เช็กว่าไม่ได้ลบเครื่องเรียนของ LAB นั้นไปด้วย

✅ **Expected output** — ได้ชื่อ container ที่ลบสำเร็จ แล้วตารางเหลือแค่หัวตาราง ไม่มีแถวข้อมูล:

```
devtools-df-lab2
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker build [OPTIONS] PATH` | รูปแบบหลัก — **build context เป็น argument สุดท้ายเสมอ** |
| `docker build -f Dockerfile.good -t cachelab-good:1.0 .` | เลือกไฟล์ Dockerfile ด้วย `-f` และตั้งชื่อ:tag ด้วย `-t` |
| `docker build -t app:1.0 -t app:latest .` | ใส่ `-t` ซ้ำได้ — ติดหลาย tag จากการ build ครั้งเดียว ได้ image ตัวเดียวสองชื่อ |
| `docker build --no-cache ...` / `--pull ...` / `--pull --no-cache ...` | ไม่ใช้ cache ของขั้นต่าง ๆ (แต่ **ไม่** ดึง base image ใหม่) / ไปถาม registry ว่า base image มีรุ่นใหม่กว่าไหม / "ใหม่หมดจริง ๆ" ต้องใช้คู่กันเท่านั้น |
| `docker build --progress=plain ...` | พิมพ์ log ทุกบรรทัดแบบไม่ย่อ ใช้ตอนไล่ปัญหา build |
| `docker build --build-arg APP_ENV=production ...` / `--target test ...` | ส่งค่าเข้าตอน build (Dockerfile ต้องมี `ARG`) · **ห้ามใส่ password/token** / build ถึงแค่ stage ที่ระบุใน multi-stage (`FROM ... AS test`) |
| `time docker build ...` | จับเวลาจริงของการ build — ดูบรรทัด `real` |
| `docker history <image>` | ดูทุก layer พร้อมขนาดที่แต่ละ layer เพิ่มเข้ามา (`--no-trunc` ไม่ตัดข้อความ) |
| `docker image ls -a` / `docker image ls -f dangling=true` | ดู image ทั้งหมดรวมตัวไม่มี tag / กรองเฉพาะตัวไม่มี tag |
| `docker image prune` / `docker container prune` | ลบ dangling image / ลบ container ที่หยุดแล้วทุกตัว (ไม่แตะตัวที่รันอยู่ ไม่แตะ volume) — ไม่ใส่ `-f` เพื่อให้ Docker ถามยืนยันก่อน |
| `docker system df` | อ่านอย่างเดียว — ดูพื้นที่ของ images / containers / volumes / **build cache** |
| `docker builder prune` | ล้าง build cache ของ BuildKit — คืนดิสก์แลกกับ build ครั้งหน้าที่ช้าลง |
| `.dockerignore` | กันไฟล์ไม่ให้เข้า build context → context เล็กลง **และ cache ไม่แตกมั่ว** |

> **จำให้ครบ:** เรียง Dockerfile จาก **เปลี่ยนน้อย → เปลี่ยนบ่อย** · ขั้นที่แพงที่สุดต้องอยู่**ก่อน**ไฟล์ที่แก้บ่อย · `CACHED` ใน log คือหลักฐานว่าเรียงถูก · `--no-cache` ≠ `--pull` · `builder prune` คือการแลกดิสก์กับเวลา

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] อ่าน `diff Dockerfile.good Dockerfile.bad` แล้วบอกได้ว่าต่างกันแค่ **ลำดับ** ไม่ใช่เนื้อหา
- [ ] รอบที่ 1 (cold) เวลาของ `good` กับ `bad` **ใกล้เคียงกัน** และไม่มีคำว่า `CACHED` ใน log เลย
- [ ] แก้ `app.py` 1 บรรทัดแล้ว build `good` ใหม่ → เห็น **`CACHED` ที่ขั้น `RUN pip install`** และ `real` ไม่ถึง 1 วินาที · ส่วน `bad` **ไม่มี `CACHED`** และเวลากลับไปเท่ารอบ cold
- [ ] ทำตารางเทียบเวลาของเครื่องตัวเองได้ครบ 4 ช่อง
- [ ] ลองครบทุก option : `-t` หลาย tag · `-f` · `--no-cache` · `--pull` · `--progress=plain` และอธิบายได้ว่าทำไม `--no-cache` ไม่พอเมื่ออยากได้ base image ใหม่
- [ ] `docker history` ชี้ได้ว่า layer ไหนใหญ่ที่สุด (คำใบ้ : `RUN pip install` = 269MB)
- [ ] build โดยไม่ใส่ `-t` แล้วเห็น image `<untagged>` จากนั้น `docker image prune` เก็บทิ้ง และอธิบายได้ว่าทำไมคืนพื้นที่ได้น้อย
- [ ] `docker system df` ก่อน/หลัง `docker builder prune` แล้วจดตัวเลข Build Cache ที่ลดลงได้
- [ ] แก้ไฟล์ที่อยู่ใน `.dockerignore` แล้ว build ใหม่ → `COPY . .` **ยัง `CACHED`** และเอาออกจาก `.dockerignore` แล้ว **cache แตกจริง**
- [ ] ทำให้พังครบ 2 แบบ (argument เกิน · `-f` ชี้ไฟล์ที่ไม่มี) แล้วอ่าน error ออกว่าต้องแก้ตรงไหน
- [ ] `./verify.sh` ขึ้น `ALL CHECKS PASSED` และเก็บกวาดจน `docker ps -a --filter "name=^devtools-"` เหลือแค่หัวตาราง

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` เมื่อ 14 ส.ค. 2026*
