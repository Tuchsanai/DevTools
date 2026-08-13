# LAB 2 — CMD vs ENTRYPOINT : พิสูจน์ด้วย ASCII Art (⏱ ~15 นาที)

> โฟลเดอร์ `002_LAB_CMD_vs_ENTRYPOINT` — คู่กับสไลด์ `new_Docker_Week11_Slides.html` Section 2
> ไฟล์ในแล็บ : `Dockerfile-CMD` · `Dockerfile-ENTRYPOINT` · `Dockerfile-BOTH` · `verify.sh`

**เป้าหมาย:** ตอบได้โดยไม่ต้องเดา — argument ท้าย `docker run` จะ**แทนที่** CMD ทั้งก้อน แต่ถูก**ต่อท้าย** ENTRYPOINT · แถมเห็น layer cache ทำงาน**ข้ามไฟล์** Dockerfile

> **ทายก่อนเริ่ม:** `docker run <image> date` จะได้วันเวลา หรือได้อย่างอื่น? … คำตอบคือ "แล้วแต่ image สร้างด้วย CMD หรือ ENTRYPOINT"

---

## 0. เตรียมเครื่องเรียน

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

## 1. Clone แล้วอ่าน Dockerfile ทั้ง 3 ไฟล์

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git 2>/dev/null
cd DevTools/03_Docker/04_Docker/002_LAB_CMD_vs_ENTRYPOINT
cat Dockerfile-CMD Dockerfile-ENTRYPOINT Dockerfile-BOTH
```

✅ สามไฟล์ **`FROM`+`RUN` เหมือนกันทุกตัวอักษร** (ติดตั้ง `figlet` = โปรแกรมวาดตัวอักษร ASCII ตัวใหญ่) ต่างกันแค่ท้ายไฟล์:

```dockerfile
CMD ["figlet", "Hello CMD"]              # ไฟล์ 1 : ค่าเริ่มต้น เปลี่ยนได้ทั้งก้อน
ENTRYPOINT ["figlet", "Hello"]           # ไฟล์ 2 : โปรแกรมหลัก args ถูกต่อท้าย
ENTRYPOINT ["figlet"]                    # ไฟล์ 3 : สูตรมาตรฐาน —
CMD ["Hello Docker"]                     #          โปรแกรมคงที่ + argument เริ่มต้น
```

## 2. Build ทีมแรก : `cmd-example`

```bash
docker build -t cmd-example -f Dockerfile-CMD .
```

> 📝 `-f` เลือกไฟล์ Dockerfile เอง (ปกติ Docker หาไฟล์ชื่อ `Dockerfile` เป๊ะ ๆ) · อย่าลืมจุด `.` ท้ายคำสั่ง · รอบนี้ช้าสุด (~15–30 วิ แล้วแต่เน็ต) เพราะ pull `ubuntu:24.04` + `apt-get install figlet` — **จำเวลาไว้เทียบข้อ 4**

## 3. นิสัยของ CMD — ถูก "แทนที่" ทั้งก้อน

```bash
docker run --rm cmd-example                  # (1) ไม่ใส่อะไร
docker run --rm cmd-example date             # (2) พิมพ์คำสั่งต่อท้าย
docker run --rm cmd-example figlet "Somchai" # (3) ใส่ชื่อตัวเอง
```

> 📝 `--rm` ลบ container ทิ้งทันทีที่จบ — ไม่เหลือซากใน `docker ps -a`

✅ (1) ASCII "Hello CMD" · (2) **วันเวลาบรรทัดเดียว ไม่มี ASCII เลย** — `date` แทนที่ CMD ทั้งก้อน · (3) ASCII ชื่อที่พิมพ์:

```
Wed Aug 12 11:50:49 UTC 2026
```

## 4. Build ทีมสอง — cache ทำงาน "ข้ามไฟล์"

```bash
docker build -t entrypoint-example -f Dockerfile-ENTRYPOINT .
docker build -t both-example -f Dockerfile-BOTH .
```

✅ ทั้งสองคำสั่งเห็น **`#5 CACHED`** ที่ขั้น apt-get และเสร็จใน ~1 วินาที — Docker เทียบ**เนื้อหาของแต่ละขั้น** ไม่ใช่ชื่อไฟล์ ขั้นต้นเหมือนกันจึงหยิบจาก cache:

```
#5 [2/2] RUN apt-get update && apt-get install -y figlet && rm -rf /var/lib/apt/lists/*
#5 CACHED
```

## 5. จุด aha! — `date` ที่ไม่ใช่ date

```bash
docker run --rm entrypoint-example date
```

✅ **ไม่มีวันเวลา!** `date` ถูก**ต่อท้าย** ENTRYPOINT กลายเป็น `figlet Hello date` — figlet วาดคำว่า date ให้ดูเฉย ๆ:

```
 _   _      _ _             _       _
| | | | ___| | | ___     __| | __ _| |_ ___
| |_| |/ _ \ | |/ _ \   / _` |/ _` | __/ _ \
|  _  |  __/ | | (_) | | (_| | (_| | ||  __/
|_| |_|\___|_|_|\___/   \__,_|\__,_|\__\___|
```

ทางหนีไฟเมื่อจำเป็นจริง ๆ — flag `--entrypoint` (ต้องวาง**ก่อน**ชื่อ image):

```bash
docker run --rm --entrypoint date entrypoint-example
```

✅ คราวนี้ได้วันเวลาจริง

## 6. สูตรมาตรฐาน : ENTRYPOINT + CMD

```bash
docker run --rm both-example                    # ENTRYPOINT+CMD ต่อกัน
docker run --rm both-example "DevOps 2569"      # args แทนที่เฉพาะ CMD — figlet ยังอยู่
```

✅ (1) ASCII "Hello Docker" · (2) ASCII "DevOps 2569" — โปรแกรมคงที่ + ค่าตั้งต้นที่เปลี่ยนง่าย คือสูตรของ image ดัง ๆ (`postgres`, `python`, CLI tools)

> ⚠️ figlet ไม่รู้จักอักษรไทย — ใช้อังกฤษ/ตัวเลขเท่านั้น

## 7. ยืนยันด้วย metadata

```bash
docker inspect --format 'ENTRYPOINT = {{json .Config.Entrypoint}}  |  CMD = {{json .Config.Cmd}}' \
  cmd-example entrypoint-example both-example
```

✅ ตรงกับ Dockerfile ทั้งสามไฟล์ (`null` = ไม่ได้กำหนด):

```
ENTRYPOINT = null  |  CMD = ["figlet","Hello CMD"]
ENTRYPOINT = ["figlet","Hello"]  |  CMD = null
ENTRYPOINT = ["figlet"]  |  CMD = ["Hello Docker"]
```

**ตารางสรุป** — เข้าใจพอ ไม่ต้องท่อง:

| image กำหนดอะไร | `run` เปล่า ๆ | `run … date` |
|---|---|---|
| CMD อย่างเดียว | รันตาม CMD | args **แทนที่ทั้งก้อน** → ได้วันเวลา |
| ENTRYPOINT อย่างเดียว | รันตาม ENTRYPOINT | args **ต่อท้าย** → figlet วาดคำว่า date |
| ทั้งคู่ | ENTRYPOINT+CMD ต่อกัน | args **แทนเฉพาะ CMD** → `figlet date` |

## 8. ตรวจงานด้วย verify.sh

```bash
bash verify.sh
```

✅ ทุกข้อ `PASS` จบด้วย `ALL CHECKS PASSED` (exit 0)

## 9. ล้างกระดาน

```bash
docker rmi cmd-example entrypoint-example both-example
docker images && docker ps -a
```

✅ สองตารางเหลือแค่หัว — ไม่มี container ให้ลบเลยเพราะเราใส่ `--rm` ทุกครั้ง

---

## ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `failed to read dockerfile: open Dockerfile: no such file` | ลืม `-f` — โฟลเดอร์นี้ไม่มีไฟล์ชื่อ `Dockerfile` ตรง ๆ | ใส่ `-f Dockerfile-CMD` (หรือไฟล์ที่ต้องการ) |
| พิมพ์ `date` แล้วได้ ASCII คำว่า date แทนวันเวลา | image นั้นใช้ ENTRYPOINT — args ถูกต่อท้าย | ถูกต้องแล้ว! นี่คือบทเรียน · อยากรันจริงใช้ `--entrypoint date` |
| `docker ps -a` มีซาก `Exited` กองอยู่ | รัน `docker run` โดยไม่ใส่ `--rm` | `docker container prune -f` แล้วติดนิสัย `--rm` |

*ผลลัพธ์ทั้งหมดมาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
