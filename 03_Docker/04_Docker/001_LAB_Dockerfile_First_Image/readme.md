# LAB 1 — สร้าง Docker Image แรกของคุณ (⏱ ~15–20 นาที)

> โฟลเดอร์ `001_LAB_Dockerfile_First_Image` — คู่กับสไลด์ `new_Docker_Week11_Slides.html` Section 1
> ไฟล์ในแล็บ : `Dockerfile` · `app.py` · `requirements.txt` · `.dockerignore` · `verify.sh`

**เป้าหมาย:** เขียน/อ่าน Dockerfile ได้ · `docker build` image ของตัวเอง · เห็น layer cache ทำงานจริง · ทับค่า `ENV` ตอนรันด้วย `-e`

---

## 0. เตรียมเครื่องเรียน

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> 📝 เปิดเครื่องเรียนเดิมถ้ามี สร้างใหม่เฉพาะเมื่อยังไม่มี · `--privileged` จำเป็นเพราะเราจะรัน Docker ซ้อนข้างในกล่องเรียน (ใช้เฉพาะกล่องเรียนแบบใช้แล้วทิ้งเท่านั้น) · ใน VS Code ใช้ **Remote-SSH** ต่อ `root@localhost:2222`

ตรวจว่า Docker พร้อม :

```bash
docker --version && docker info --format 'daemon: {{.ServerVersion}}'
```

✅ ขอแค่มีเลขเวอร์ชันครบสองบรรทัด ไม่ใช่ error (เลขไม่ต้องตรงกับเอกสาร):

```
Docker version 29.6.2, build dfc4efb
daemon: 29.6.2
```

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Docker/04_Docker/001_LAB_Dockerfile_First_Image
```

> เคย clone แล้ว git จะบอกว่าโฟลเดอร์ไม่ว่าง — ข้ามไป `cd` ได้เลย

## 2. อ่าน Dockerfile ให้ออกทุกบรรทัด

```bash
cat Dockerfile
```

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

ENV APP_VERSION=1.0

EXPOSE 5000

CMD ["python", "app.py"]
```

> 📝 อ่านจากบนลงล่าง : `FROM` เลือก base image (pin tag เสมอ) · `WORKDIR` ตั้งโฟลเดอร์ทำงาน · `COPY requirements.txt` แยกมาก่อน `COPY app.py` **เพื่อให้ layer `pip install` โดน cache** (ข้อ 6 พิสูจน์) · `RUN` ทำงาน**ตอน build** ผลถูกอบเก็บใน image · `ENV` ฝังค่า default (ข้อ 7 จะทับด้วย `-e`) · `EXPOSE` เป็นแค่ป้ายประกาศ **ไม่ได้เปิดพอร์ตจริง** · `CMD` คือคำสั่งที่รัน**ตอน container start**

`app.py` คือ Flask จิ๋วที่โชว์ข้อความ (ตัวแปร `MESSAGE` บรรทัด 10) + Container ID + ค่า `APP_VERSION` · `.dockerignore` กัน `readme/รูป/.git` ไม่ให้เข้า build context

## 3. Build image แรก

```bash
time docker build -t myapp:1.0 .
```

> 📝 `-t ชื่อ:tag` ตั้งชื่อ image · **จุด `.` ท้ายคำสั่งคือ build context** (โฟลเดอร์วัตถุดิบที่ส่งให้ Docker) — ลืมจุดคือ error อันดับหนึ่งของห้อง · `time` จับเวลาไว้เทียบข้อ 6

✅ ครั้งแรกมี pull base image แล้วไล่ step `[1/5]`–`[5/5]` จบด้วยชื่อ image (เวลาแต่ละคนไม่ตรงกัน — **จดเวลา `real` ไว้**):

```
#5 [1/5] FROM docker.io/library/python:3.12-slim@sha256:229a2c5...
#6 [2/5] WORKDIR /app
#7 [3/5] COPY requirements.txt .
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#9 [5/5] COPY app.py .
#10 naming to docker.io/library/myapp:1.0 done

real	0m7.924s
```

ส่อง layer — ทุกบรรทัดของ Dockerfile ทิ้งรอยไว้จริง :

```bash
docker history myapp:1.0
```

✅ อ่านจากล่างขึ้นบน : 7 แถวบนคือฝีมือเรา (แถว `RUN pip install` ~15MB คือ Flask) แถวล่างเป็นของ base image · แถว `0B` คือ metadata (`ENV`/`EXPOSE`/`CMD`)

## 4. รัน container จาก image ของเราเอง

```bash
docker rm -f myapp 2>/dev/null; docker run -d --name myapp -p 8081:5000 myapp:1.0
curl -s http://localhost:8081 | grep -o 'สวัสดีจาก Container! 🐳'
```

> 📝 `-p 8081:5000` **คือตัวเปิดพอร์ตจริง** (ซ้าย=เครื่องเรียน ขวา=ใน container) — `EXPOSE` ใน Dockerfile ไม่เคยเปิดอะไรให้

✅ ได้ container ID แล้ว `curl` เจอข้อความ:

```
สวัสดีจาก Container! 🐳
```

อยากดูในเบราว์เซอร์ : VS Code แท็บ **PORTS** → **Forward a Port** → `8081` → เปิด `http://localhost:8081` — เห็นการ์ดขาวบนพื้นน้ำเงิน ชิป Container ID ตรงกับ `docker ps`

## 5. 1 image → หลาย container

```bash
docker run -d --name myapp2 -p 8082:5000 myapp:1.0
curl -s localhost:8081 | grep -oE '[0-9a-f]{12}'; curl -s localhost:8082 | grep -oE '[0-9a-f]{12}'
docker rm -f myapp2
```

✅ สองบรรทัดแรกคือ Container ID จากหน้าเว็บ — **คนละค่า** ทั้งที่มาจาก image เดียวกัน (image = พิมพ์เขียว · container = บ้าน) แล้วลบบ้านหลังที่สองทิ้ง

## 6. แก้โค้ด → build ใหม่ → ดู cache ทำงาน

```bash
sed -i 's/สวัสดีจาก Container! 🐳/Docker เปลี่ยนข้อความได้ ไม่ต้องลง Python ใหม่! 🚀/' app.py
time docker build -t myapp:2.0 .
```

✅ สาม step แรกขึ้น **`CACHED`** — Docker ทำงานจริงแค่ `COPY app.py` · เวลาเหลือ ~2 วินาที จาก ~8 วินาที:

```
#6 [2/5] WORKDIR /app
#6 CACHED
#7 [3/5] COPY requirements.txt .
#7 CACHED
#8 [4/5] RUN pip install --no-cache-dir -r requirements.txt
#8 CACHED          ← ไม่ติดตั้ง Flask ซ้ำ ไม่แตะเน็ตเลย
#9 [5/5] COPY app.py .
#9 DONE 0.0s

real	0m1.922s
```

> 📝 **กติกา cache:** Docker เทียบทีละ layer จากบนลงล่าง — layer ไหนเปลี่ยน ทุก layer ใต้มันต้องทำใหม่หมด · นี่คือเหตุผลที่ `COPY requirements.txt` (นาน ๆ เปลี่ยนที) ต้องมาก่อน `COPY app.py` (เปลี่ยนทุกวัน)

## 7. รันเวอร์ชันใหม่ + ทับ ENV ด้วย `-e`

```bash
docker rm -f myapp
docker run -d --name myapp -p 8081:5000 -e APP_VERSION=2.0 myapp:2.0
curl -s localhost:8081 | grep -o '<h1>.*</h1>'
curl -s localhost:8081 | grep -o 'เวอร์ชัน&nbsp;<b>[0-9.]*'
```

✅ ข้อความใหม่มาจาก image `2.0` ส่วนเลขเวอร์ชันมาจาก `-e` ล้วน ๆ (Dockerfile ยังเขียน `1.0` อยู่!):

```
<h1>Docker เปลี่ยนข้อความได้ ไม่ต้องลง Python ใหม่! 🚀</h1>
เวอร์ชัน&nbsp;<b>2.0
```

> 📝 ลำดับความสำคัญ : `-e` ตอน run > `ENV` ตอน build > default ในโค้ด — build ครั้งเดียว รันเป็น dev/staging/prod ด้วย config ต่างกันได้

## 8. พิสูจน์ `.dockerignore`

```bash
docker exec myapp ls /app
```

✅ ใน image มีแค่ **2 ไฟล์** ที่ `COPY` ระบุชื่อ — readme/รูป/.git ไม่หลุดเข้ามา:

```
app.py
requirements.txt
```

## 9. ตรวจงานด้วย verify.sh

รันจากโฟลเดอร์แล็บ **ก่อน** ล้างกระดาน :

```bash
bash verify.sh
```

✅ ทุกข้อขึ้น `PASS` และจบด้วย `ALL CHECKS PASSED` (exit code 0)

## 10. ล้างกระดาน

```bash
docker rm -f myapp
docker rmi myapp:1.0 myapp:2.0
docker ps -a && docker images
```

✅ สองตารางเหลือแค่หัว ไม่มีแถวข้อมูล (build cache ตั้งใจเก็บไว้ให้แล็บถัดไปเร็ว) · ถ้า forward port ไว้ อย่าลืม **Stop Forwarding Port**

---

## ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `"docker buildx build" requires exactly 1 argument` | ลืมจุด `.` (build context) ท้ายคำสั่ง | เติม `.` — `docker build -t myapp:1.0 .` |
| แก้ `app.py` แล้วรีเฟรชเบราว์เซอร์ — ไม่เปลี่ยน | โค้ดถูก "อบ" ไว้ใน image ตอน build แล้ว | build tag ใหม่ (ข้อ 6) แล้ว `rm -f` + `run` ใหม่ (ข้อ 7) |
| หน้าเว็บขึ้น "เวอร์ชัน 1.0" ทั้งที่รัน `myapp:2.0` | ลืม `-e APP_VERSION=2.0` — จึงใช้ค่า `ENV` เดิม | ใส่ `-e APP_VERSION=2.0` ตอน `docker run` |

*ผลลัพธ์ทั้งหมดมาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
