# LAB 2 — CMD vs ENTRYPOINT : ใครกันแน่ที่รันตอน container start

> โฟลเดอร์ `002_LAB_CMD_vs_ENTRYPOINT` = **LAB 2** ในสไลด์ `Docker_Week11_Slides.html`
> (ไฟล์โค้ดของแล็บนี้ : `Dockerfile-CMD` · `Dockerfile-ENTRYPOINT` · `Dockerfile-BOTH`)

## สิ่งที่จะได้เรียนรู้

- **CMD** คือ "คำสั่งเริ่มต้น" ของ image — argument ที่พิมพ์ท้าย `docker run` จะเข้ามา **แทนที่ทั้งก้อน**
- **ENTRYPOINT** คือ "โปรแกรมหลัก" ที่รันเสมอ — argument จะถูก **ต่อท้าย** ไม่ใช่แทนที่
- สูตรมาตรฐานของ image ดี ๆ : **ENTRYPOINT + CMD** — ENTRYPOINT ล็อกโปรแกรม ส่วน CMD เป็น argument ตั้งต้นที่ผู้ใช้เปลี่ยนได้
- `docker build -f` เลือกไฟล์ Dockerfile เองได้ — โฟลเดอร์เดียว build ออกมาได้ 3 image
- **layer cache ทำงานข้ามไฟล์** : Dockerfile ที่ขึ้นต้นเหมือนกัน build ไฟล์ที่ 2–3 เสร็จใน ~1 วินาที
- `docker run --rm` รัน container แบบใช้แล้วทิ้ง — จบแล้วไม่เหลือซากใน `docker ps -a`
- อ่าน metadata ของ image ด้วย `docker inspect` เพื่อยืนยันว่า Entrypoint/Cmd ถูกเก็บไว้อย่างไร

## ภาพรวมของแล็บนี้

1. **อ่าน Dockerfile ทั้ง 3 ไฟล์** — สามไฟล์ต่างกันแค่ **บรรทัดสุดท้าย** (CMD / ENTRYPOINT / ทั้งคู่) จึงเทียบพฤติกรรมกันได้แบบตัวแปรเดียว
2. **Build image ทีมแรก `cmd-example`** — รอบนี้ช้าสุดเพราะต้อง pull `ubuntu:24.04` และติดตั้ง `figlet` (โปรแกรมวาดตัวอักษร ASCII)
3. **ทดลองกับ CMD** — รันเปล่า ๆ แล้วลองพิมพ์ argument ต่อท้าย เพื่อดูว่า "อะไรหายไป"
4. **Build `entrypoint-example`** — จะเสร็จเร็วผิดปกติ เพราะ Docker ใช้ layer cache ร่วมกันข้าม Dockerfile
5. **ทดลองกับ ENTRYPOINT** — จุด aha ของแล็บ : พิมพ์ `date` ต่อท้ายแล้ว figlet **วาดคำว่า date** แทนที่จะรันคำสั่ง
6. **Build + ทดลอง `both-example`** — สูตร ENTRYPOINT + CMD ที่ image ดัง ๆ (nginx, postgres, python) ใช้กันจริง
7. **ยืนยันด้วย `docker inspect`** — อ่าน metadata แล้วสรุปเป็นตารางพฤติกรรมครบทุกกรณี
8. **ล้างกระดาน** — ลบ image ทั้งสาม แล้วชี้ให้เห็นว่า `--rm` ทำให้ไม่มี container ค้างเลยสักตัว

> **คำถามก่อนเริ่ม:** ถ้าพิมพ์ `docker run <image> date` — คำว่า `date` จะ "แทนที่" คำสั่งเดิมของ image หรือถูก "ส่งเป็น argument" ให้โปรแกรมใน image? คำตอบคือ **แล้วแต่ image สร้างมาด้วย CMD หรือ ENTRYPOINT** — จบแล็บนี้จะตอบได้โดยไม่ต้องเดา

---

## 0. เตรียมเครื่องเรียน

ทำบนเครื่องของเราเอง (ไม่ใช้ cloud) — เปิด container ที่ติดตั้ง Docker มาให้แล้ว

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> 📝 **คำอธิบาย:** `docker start ... || docker run ...` เปิดเครื่องเรียนเดิมถ้ามี และสร้างใหม่เฉพาะเมื่อยังไม่มี จึงไม่ลบ clone จาก LAB ก่อนหน้า ·
> `-dit` คือ `-d` รันเบื้องหลัง + `-i` เปิด stdin ค้างไว้ + `-t` ให้มี terminal กล่องจะได้ไม่ดับทันที · `--privileged` ให้สิทธิ์เต็มเพื่อรัน **Docker ซ้อนข้างในกล่อง** (จำเป็น — แล็บนี้จะ build image และรัน container ข้างในเครื่องเรียนอีกชั้น) ·
> `-p 2222:22` ส่ง port 2222 ของเครื่องเรา เข้า port 22 (SSH) ของกล่อง

> ⚠️ `--privileged` ใช้เฉพาะ disposable classroom container นี้ ไม่ใช่ค่าที่ควรใช้กับ production workload

> ใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บทั้งหมดข้างใน

ตรวจว่าพร้อมใช้งาน :

```bash
docker --version
docker info --format 'Docker daemon: {{.ServerVersion}}'
```

> 📝 **คำอธิบาย:** บรรทัดแรกเช็ก Docker CLI และบรรทัดที่สองถาม daemon โดยตรง จึงยืนยันได้ว่าคำสั่ง `docker` วิ่งถึง daemon ก่อนเริ่มแล็บ · สิ่งที่ต้องดูคือ "มีเลขเวอร์ชันขึ้นมาไหม" ไม่ใช่ "เลขตรงกับเอกสารไหม" ·
> ถ้าขึ้น `Cannot connect to the Docker daemon` แปลว่ายังอยู่นอกกล่องเรียนหรือ daemon ยังไม่ขึ้น ให้ย้อนทำข้อ 0 ใหม่

✅ **Expected output** — ขอแค่มี **เลขเวอร์ชัน** ขึ้นครบสองบรรทัด ไม่ใช่ error (เลขเวอร์ชันของแต่ละคนอาจไม่ตรงกับเอกสารนี้):

```
Docker version 29.6.2, build dfc4efb
Docker daemon: 29.6.2
```

---

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Docker/04_Docker/002_LAB_CMD_vs_ENTRYPOINT
ls -1
```

> 📝 **คำอธิบาย:** `mkdir -p ~/labwork` สร้างโฟลเดอร์เก็บงาน (`-p` = มีอยู่แล้วก็ไม่ error) · `git clone` ดึงรีโพของวิชาลงมา ทำครั้งเดียวใช้ได้ทุกแล็บของชุดนี้ · แล้ว `cd` เข้าโฟลเดอร์แล็บ ปิดท้ายด้วย `ls -1` ไล่ดูว่าไฟล์ครบ ·
> ถ้าเคย clone ไว้ git จะบอกว่าโฟลเดอร์ไม่ว่าง — ข้ามไป `cd` ได้เลย

✅ **Expected output** — เห็น Dockerfile ครบ 3 ไฟล์ ชื่อไม่เหมือน Dockerfile ปกติ (จงใจ — เดี๋ยวข้อ 3 จะได้หัดใช้ `-f`):

```
Dockerfile-BOTH
Dockerfile-CMD
Dockerfile-ENTRYPOINT
```

---

## 2. อ่าน Dockerfile ทั้ง 3 ไฟล์ — ต่างกันแค่บรรทัดสุดท้าย

พระเอกของแล็บนี้คือ **figlet** โปรแกรมเล็ก ๆ ที่วาดข้อความเป็นตัวอักษร ASCII ตัวใหญ่เต็มจอ — เหมาะมากสำหรับดูว่า "คำสั่งที่รันจริงคืออะไร" เพราะผลลัพธ์มองเห็นชัดด้วยตาเปล่า

```bash
cat Dockerfile-CMD
```

> 📝 **คำอธิบาย:** อ่านไฟล์แรกก่อนลงมือ build เสมอ — Dockerfile คือพิมพ์เขียวของ image · `FROM ubuntu:24.04` เริ่มจาก Ubuntu เปล่า ๆ · `RUN apt-get ...` ติดตั้ง figlet แล้วลบ package index ทิ้งเพื่อลดขนาด image · `CMD ["figlet", "Hello CMD"]` (รูปแบบ JSON array เรียกว่า **exec form**) กำหนด "คำสั่งเริ่มต้น" ที่จะรันเมื่อ start container

✅ **Expected output** :

```dockerfile
# ── CMD อย่างเดียว : กำหนด "คำสั่งเริ่มต้น" ที่ถูกแทนที่ได้ทั้งก้อน ──
# ทั้ง 3 Dockerfile ของแล็บนี้ใช้ FROM + RUN บรรทัดเดียวกันเป๊ะ
# → Docker ใช้ layer cache ร่วมกัน build ไฟล์ที่ 2-3 จะเร็วมาก

FROM ubuntu:24.04
RUN apt-get update && apt-get install -y figlet && rm -rf /var/lib/apt/lists/*

CMD ["figlet", "Hello CMD"]
```

ดูอีกสองไฟล์เทียบกัน :

```bash
cat Dockerfile-ENTRYPOINT
cat Dockerfile-BOTH
```

> 📝 **คำอธิบาย:** สังเกตให้ดี — **`FROM` กับ `RUN` ของทั้งสามไฟล์เหมือนกันทุกตัวอักษร** ต่างกันเฉพาะบรรทัดสุดท้าย : ไฟล์ที่สองใช้ `ENTRYPOINT ["figlet", "Hello"]` ส่วนไฟล์ที่สามใช้ `ENTRYPOINT ["figlet"]` คู่กับ `CMD ["Hello Docker"]` ·
> การที่บรรทัดต้นเหมือนกันเป๊ะไม่ใช่ความบังเอิญ — ข้อ 5 จะได้เห็นผลของมันต่อความเร็วในการ build

✅ **Expected output** :

```dockerfile
# ── ENTRYPOINT อย่างเดียว : กำหนด "โปรแกรมหลัก" ที่รันเสมอ ──
# argument ที่พิมพ์ท้าย docker run จะถูก "ต่อท้าย" ไม่ใช่แทนที่

FROM ubuntu:24.04
RUN apt-get update && apt-get install -y figlet && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["figlet", "Hello"]
```

```dockerfile
# ── ENTRYPOINT + CMD ใช้ร่วมกัน : สูตรมาตรฐานของ image ดี ๆ ──
# ENTRYPOINT = โปรแกรมหลัก (คงที่)   CMD = argument เริ่มต้น (เปลี่ยนได้)

FROM ubuntu:24.04
RUN apt-get update && apt-get install -y figlet && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["figlet"]
CMD ["Hello Docker"]
```

---

## 3. Build image ทีมแรก : `cmd-example`

```bash
docker build -t cmd-example -f Dockerfile-CMD .
```

> 📝 **คำอธิบาย:** `-t cmd-example` ตั้งชื่อ (tag) ให้ image เรียกใช้ง่าย · `-f Dockerfile-CMD` **เลือกไฟล์ Dockerfile เอง** — ปกติ Docker มองหาไฟล์ชื่อ `Dockerfile` เป๊ะ ๆ แต่โฟลเดอร์นี้มี 3 ไฟล์ชื่อไม่ตรง จึงต้องชี้เอง · `.` (จุด) ท้ายคำสั่งคือ **build context** = ส่งไฟล์ในโฟลเดอร์ปัจจุบันให้ daemon ใช้ตอน build — **ลืมจุดบ่อยที่สุดในห้อง** ·
> รอบแรกช้าสุดของแล็บ (~10–15 วินาที ขึ้นกับเน็ต) เพราะต้องทำครบทุกขั้น : pull base image + `apt-get update` + ติดตั้ง figlet

✅ **Expected output** — ไล่ดู 3 ช่วง : `#4` pull base image → `#5` รัน apt-get ติดตั้ง figlet → `#6` ปิดท้ายด้วย `naming to docker.io/library/cmd-example` = สำเร็จ (digest · ตัวเลขเวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
#0 building with "default" instance using docker driver

#1 [internal] load build definition from Dockerfile-CMD
#1 transferring dockerfile: 605B done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/ubuntu:24.04
#2 DONE 1.8s

#4 [1/2] FROM docker.io/library/ubuntu:24.04@sha256:561618e2c15bf2397621dd04f96926663a3b5616c189cf7e38db7e82f5c538ea
#4 sha256:966c395d29cb... 2.10MB / 29.75MB 0.5s
        ... (ดาวน์โหลด + extract layer ของ ubuntu:24.04 ราว 30MB) ...
#4 DONE 2.6s

#5 [2/2] RUN apt-get update && apt-get install -y figlet && rm -rf /var/lib/apt/lists/*
#5 0.679 Get:2 http://archive.ubuntu.com/ubuntu noble InRelease [256 kB]
        ... (apt-get update ดึง package index อีก ~17 บรรทัด) ...
#5 6.126 The following NEW packages will be installed:
#5 6.127   figlet
#5 7.409 Unpacking figlet (2.2.5-3) ...
#5 7.467 Setting up figlet (2.2.5-3) ...
#5 DONE 7.6s

#6 exporting to image
#6 naming to docker.io/library/cmd-example:latest done
#6 DONE 0.4s
```

> ⚠️ ขั้น `[1/2]` `[2/2]` คือ **layer** ของ image — Docker จำผลของแต่ละขั้นไว้ใน **build cache** ถ้าขั้นไหนไม่เปลี่ยนจะไม่ทำซ้ำ · จำเวลารวมรอบนี้ไว้ (~12 วินาที) แล้วไปเทียบกับข้อ 5

---

## 4. CMD = ค่าเริ่มต้นที่ถูก "แทนที่" ได้ทั้งก้อน

### 4.1 รันแบบไม่ใส่อะไรเลย → ได้คำสั่งเริ่มต้น

```bash
docker run --rm cmd-example
```

> 📝 **คำอธิบาย:** ไม่มี argument ต่อท้าย → Docker รันตาม `CMD ["figlet", "Hello CMD"]` ที่ฝังไว้ใน image · `--rm` สั่งให้ **ลบ container ทิ้งทันทีที่โปรแกรมจบ** — container แบบนี้รันเสร็จใน 1 วินาทีแล้วไม่มีประโยชน์ต่อ เหมาะกับ `--rm` มาก (ถ้าไม่ใส่ ซาก Exited จะกองใน `docker ps -a` — ทดลองท้ายแล็บมีให้ดู)

✅ **Expected output** — figlet วาด "Hello CMD" ตัวใหญ่เต็มจอ:

```
 _   _      _ _          ____ __  __ ____
| | | | ___| | | ___    / ___|  \/  |  _ \
| |_| |/ _ \ | |/ _ \  | |   | |\/| | | | |
|  _  |  __/ | | (_) | | |___| |  | | |_| |
|_| |_|\___|_|_|\___/   \____|_|  |_|____/
```

### 4.2 พิมพ์คำสั่งอื่นต่อท้าย → CMD หายไปทั้งก้อน

```bash
docker run --rm cmd-example date
```

> 📝 **คำอธิบาย:** argument ท้าย `docker run` เข้ามา **แทนที่ CMD ทั้งก้อน** — `figlet "Hello CMD"` ถูกเขี่ยทิ้ง เหลือแค่ `date` · นี่คือนิสัยของ CMD : เป็นเพียง "ค่าเริ่มต้นเผื่อผู้ใช้ไม่บอกอะไรมา"

✅ **Expected output** — ได้วันเวลาบรรทัดเดียว **ไม่มี ASCII art เลย** (วันเวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
Wed Aug 12 11:50:49 UTC 2026
```

### 4.3 ใส่ชื่อตัวเองดูหน่อย

```bash
docker run --rm cmd-example figlet "Somchai"
```

> 📝 **คำอธิบาย:** คราวนี้แทนที่ CMD ด้วยคำสั่งเต็ม `figlet "Somchai"` ของเราเอง — figlet กลับมาเพราะ **เราพิมพ์เอง** ไม่ใช่เพราะ image · **เปลี่ยน `Somchai` เป็นชื่อตัวเองแล้วรันดู** — ข้อความในเครื่องหมายคำพูดคือ argument ที่ส่งให้ figlet

✅ **Expected output** — ASCII art ตามข้อความที่พิมพ์:

```
 ____                       _           _
/ ___|  ___  _ __ ___   ___| |__   __ _(_)
\___ \ / _ \| '_ ` _ \ / __| '_ \ / _` | |
 ___) | (_) | | | | | | (__| | | | (_| | |
|____/ \___/|_| |_| |_|\___|_| |_|\__,_|_|
```

> **สรุปนิสัยของ CMD :** `docker run cmd-example <อะไรก็ตาม>` — สิ่งที่พิมพ์ต่อท้ายจะ **กลายเป็นคำสั่งแทน CMD ทันที** · CMD จึงเหมาะกับ image ที่อยากให้ผู้ใช้สลับคำสั่งได้อิสระ

---

## 5. Build ทีมสอง : เห็น layer cache ทำงาน "ข้ามไฟล์"

```bash
docker build -t entrypoint-example -f Dockerfile-ENTRYPOINT .
```

> 📝 **คำอธิบาย:** คำสั่งหน้าตาเดิม เปลี่ยนแค่ชื่อ tag กับไฟล์ · ก่อนกด Enter ให้ทายก่อน — รอบนี้จะใช้เวลากี่วินาที? ·
> เฉลย : Docker เทียบ **เนื้อหาของแต่ละขั้น** ไม่ได้เทียบชื่อไฟล์ — `FROM` + `RUN` ของไฟล์นี้ตรงกับที่เพิ่ง build ไปเป๊ะ จึงหยิบผลจาก cache มาใช้เลย ไม่ pull ไม่ apt-get ซ้ำ

✅ **Expected output** — จุดชี้ขาดคือบรรทัด **`#5 CACHED`** : ขั้น apt-get ที่เคยกิน 7 วินาทีไม่ถูกรันซ้ำ ทั้งคำสั่งเสร็จใน ~1 วินาที:

```
#1 [internal] load build definition from Dockerfile-ENTRYPOINT
#1 transferring dockerfile: 459B done
#1 DONE 0.0s

#2 [internal] load metadata for docker.io/library/ubuntu:24.04
#2 DONE 0.8s

#4 [1/2] FROM docker.io/library/ubuntu:24.04@sha256:561618e2c15bf2397621dd04f96926663a3b5616c189cf7e38db7e82f5c538ea
#4 DONE 0.0s

#5 [2/2] RUN apt-get update && apt-get install -y figlet && rm -rf /var/lib/apt/lists/*
#5 CACHED

#6 exporting to image
#6 naming to docker.io/library/entrypoint-example:latest done
#6 DONE 0.2s
```

> **บทเรียนสำคัญ :** cache ผูกกับ "ลำดับขั้นที่เหมือนกัน" ไม่ใช่ชื่อไฟล์ — นี่คือเหตุผลที่ Dockerfile ควรวางบรรทัดที่เปลี่ยนบ่อย (เช่น COPY โค้ด) ไว้ **ล่างสุด** เพื่อให้ขั้นหนัก ๆ ข้างบนโดน cache ตลอด

---

## 6. ENTRYPOINT = โปรแกรมหลัก — argument ถูก "ต่อท้าย"

### 6.1 รันเปล่า ๆ

```bash
docker run --rm entrypoint-example
```

> 📝 **คำอธิบาย:** ไม่มี argument → รันตาม `ENTRYPOINT ["figlet", "Hello"]` ตรง ๆ · ถึงตรงนี้ยังดูไม่ต่างจาก CMD — ความต่างจะโผล่ตอนใส่ argument

✅ **Expected output** :

```
 _   _      _ _
| | | | ___| | | ___
| |_| |/ _ \ | |/ _ \
|  _  |  __/ | | (_) |
|_| |_|\___|_|_|\___/
```

### 6.2 ใส่ argument ต่อท้าย → ถูก "ต่อ" ไม่ใช่ "แทน"

```bash
docker run --rm entrypoint-example World
```

> 📝 **คำอธิบาย:** `World` ไม่ได้แทนที่อะไรเลย — มันถูก **ต่อท้าย** ENTRYPOINT กลายเป็น `figlet Hello World` · เทียบกับข้อ 4.2 : image CMD โดน `date` เขี่ยทิ้งทั้งก้อน แต่ image ENTRYPOINT ยังยืนหนึ่งเป็นโปรแกรมหลักเสมอ

✅ **Expected output** — figlet วาดสองคำ "Hello World":

```
 _   _      _ _        __        __         _     _
| | | | ___| | | ___   \ \      / /__  _ __| | __| |
| |_| |/ _ \ | |/ _ \   \ \ /\ / / _ \| '__| |/ _` |
|  _  |  __/ | | (_) |   \ V  V / (_) | |  | | (_| |
|_| |_|\___|_|_|\___/     \_/\_/ \___/|_|  |_|\__,_|
```

### 6.3 จุด aha! — ลองสั่ง `date` แบบเดียวกับข้อ 4.2

```bash
docker run --rm entrypoint-example date
```

> 📝 **คำอธิบาย:** คำสั่งหน้าตาเหมือนข้อ 4.2 เป๊ะ แต่ผลตรงข้ามโดยสิ้นเชิง — `date` **ไม่ได้ถูกรันเป็นคำสั่ง** มันถูกต่อท้ายกลายเป็น `figlet Hello date` · figlet เลยวาดคำว่า "date" ให้ดูเฉย ๆ — ความต่างระหว่าง CMD กับ ENTRYPOINT สรุปอยู่ในภาพนี้ภาพเดียว

✅ **Expected output** — ไม่มีวันเวลา มีแต่ ASCII คำว่า "Hello date":

```
 _   _      _ _             _       _
| | | | ___| | | ___     __| | __ _| |_ ___
| |_| |/ _ \ | |/ _ \   / _` |/ _` | __/ _ \
|  _  |  __/ | | (_) | | (_| | (_| | ||  __/
|_| |_|\___|_|_|\___/   \__,_|\__,_|\__\___|
```

### 6.4 ทางหนีไฟ : `--entrypoint`

```bash
docker run --rm --entrypoint date entrypoint-example
```

> 📝 **คำอธิบาย:** ถ้าจำเป็นต้องรันคำสั่งอื่นใน image ที่ล็อก ENTRYPOINT ไว้ ให้ใช้ flag `--entrypoint <คำสั่ง>` — **ต้องวางก่อนชื่อ image** เพราะเป็น option ของ `docker run` (ทุกอย่างหลังชื่อ image ถือเป็น argument ของ container) · ใช้บ่อยเวลา debug image คนอื่น เช่น `--entrypoint bash` เพื่อแอบเข้าไปดูข้างใน

✅ **Expected output** — คราวนี้ `date` ถูกรันเป็นคำสั่งจริง:

```
Wed Aug 12 11:51:23 UTC 2026
```

> **สรุปนิสัยของ ENTRYPOINT :** argument ท้าย `docker run` = **argument ของโปรแกรม** ไม่ใช่คำสั่งใหม่ · อยากเปลี่ยนโปรแกรมจริง ๆ ต้องใช้ `--entrypoint` เท่านั้น

---

## 7. ENTRYPOINT + CMD = สูตรมาตรฐานที่ image ดัง ๆ ใช้จริง

### 7.1 Build ไฟล์ที่สาม (cache อีกรอบ)

```bash
docker build -t both-example -f Dockerfile-BOTH .
```

> 📝 **คำอธิบาย:** ไฟล์ที่สามก็ขึ้นต้นด้วย `FROM` + `RUN` ชุดเดิม → `CACHED` เหมือนข้อ 5 เสร็จใน ~1 วินาที · ตอนนี้เรามี image ครบสามตัวจาก apt-get เพียง **ครั้งเดียว**

✅ **Expected output** — เห็น `#5 CACHED` เช่นเดิม ปิดท้ายด้วยชื่อ image ใหม่:

```
        ...
#5 [2/2] RUN apt-get update && apt-get install -y figlet && rm -rf /var/lib/apt/lists/*
#5 CACHED

#6 exporting to image
#6 naming to docker.io/library/both-example:latest done
#6 DONE 0.2s
```

### 7.2 รันเปล่า ๆ → ENTRYPOINT + CMD ต่อกัน

```bash
docker run --rm both-example
```

> 📝 **คำอธิบาย:** ไม่มี argument → Docker เอา `ENTRYPOINT ["figlet"]` ต่อกับ `CMD ["Hello Docker"]` ได้คำสั่งจริง `figlet "Hello Docker"` · CMD ในสูตรนี้ทำหน้าที่เป็น **"argument เริ่มต้น"** ของโปรแกรม

✅ **Expected output** :

```
 _   _      _ _         ____             _
| | | | ___| | | ___   |  _ \  ___   ___| | _____ _ __
| |_| |/ _ \ | |/ _ \  | | | |/ _ \ / __| |/ / _ \ '__|
|  _  |  __/ | | (_) | | |_| | (_) | (__|   <  __/ |
|_| |_|\___|_|_|\___/  |____/ \___/ \___|_|\_\___|_|
```

### 7.3 ใส่ argument → CMD ถูกแทน แต่ figlet ยังอยู่

```bash
docker run --rm both-example "I love Docker"
```

> 📝 **คำอธิบาย:** argument ของเราแทนที่ **เฉพาะ CMD** (`"Hello Docker"` หายไป) ส่วน ENTRYPOINT (`figlet`) ยังคงเป็นโปรแกรมหลัก — ได้คำสั่งจริง `figlet "I love Docker"` · นี่คือส่วนผสมที่ดีที่สุดของสองโลก : โปรแกรมคงที่ + ค่าตั้งต้นที่เปลี่ยนง่าย · เครื่องหมายคำพูดสำคัญ — ทำให้สามคำนี้เป็น argument เดียว

✅ **Expected output** :

```
 ___   _                  ____             _
|_ _| | | _____   _____  |  _ \  ___   ___| | _____ _ __
 | |  | |/ _ \ \ / / _ \ | | | |/ _ \ / __| |/ / _ \ '__|
 | |  | | (_) \ V /  __/ | |_| | (_) | (__|   <  __/ |
|___| |_|\___/ \_/ \___| |____/ \___/ \___|_|\_\___|_|
```

ลองข้อความของตัวเอง :

```bash
docker run --rm both-example "DevOps 2569"
```

✅ **Expected output** :

```
 ____              ___              ____  ____   __   ___
|  _ \  _____   __/ _ \ _ __  ___  |___ \| ___| / /_ / _ \
| | | |/ _ \ \ / / | | | '_ \/ __|   __) |___ \| '_ \ (_) |
| |_| |  __/\ V /| |_| | |_) \__ \  / __/ ___) | (_) \__, |
|____/ \___| \_/  \___/| .__/|___/ |_____|____/ \___/  /_/
                       |_|
```

> ⚠️ **figlet ไม่รู้จักอักษรไทย** — ลอง `docker run --rm both-example "สอบผ่านชัวร์"` จะได้ลายเส้นเพี้ยน ๆ อ่านไม่ออก (figlet มองข้อความ UTF-8 เป็น byte ทีละตัว):
>
> ```
>   __   __ _  __         __     __     __   _   __   ___  __     __     __
>   \_\_/ _` | \_\_       \_\_   \_\_   \_\_/ |  \_\_|_  ) \_\_   \_\_   \_\_
>         ... (ลายเส้นเพี้ยนต่ออีกหลายบรรทัด) ...
> ```
>
> ใช้ภาษาอังกฤษหรือตัวเลขแทน เช่น `"DevOps 2569"`

> **ภาพจำ :** image จริงในโลกใช้สูตรนี้ทั้งนั้น — `postgres` มี ENTRYPOINT เป็นสคริปต์เริ่ม database, `python` มี ENTRYPOINT/CMD ให้เปิด REPL ถ้าไม่บอกอะไร · เขียน image ของตัวเองเมื่อไร ให้เริ่มคิดจากสูตร **ENTRYPOINT = โปรแกรม · CMD = argument เริ่มต้น**

---

## 8. ยืนยันด้วย `docker inspect` + ตารางสรุปทุกกรณี

อย่าเชื่อแค่ตาเปล่า — ถาม metadata ของ image ตรง ๆ :

```bash
docker inspect --format 'ENTRYPOINT = {{json .Config.Entrypoint}}  |  CMD = {{json .Config.Cmd}}' \
  cmd-example entrypoint-example both-example
```

> 📝 **คำอธิบาย:** `docker inspect` อ่าน metadata ทั้งหมดของ image (ปกติได้ JSON ยาวหลายจอ) · `--format` เลือกพิมพ์เฉพาะ field ที่สนใจ — `{{json .Config.Entrypoint}}` กับ `{{json .Config.Cmd}}` คือค่าที่ Dockerfile ฝังไว้ · ใส่ชื่อ image ได้หลายตัวในคำสั่งเดียว ผลจะออกมาบรรทัดละ image ตามลำดับ

✅ **Expected output** — ค่า `null` = Dockerfile ไม่ได้กำหนด field นั้น สอดคล้องกับไฟล์ทั้งสามที่อ่านในข้อ 2 เป๊ะ:

```
ENTRYPOINT = null  |  CMD = ["figlet","Hello CMD"]
ENTRYPOINT = ["figlet","Hello"]  |  CMD = null
ENTRYPOINT = ["figlet"]  |  CMD = ["Hello Docker"]
```

ดูรายชื่อ image ทั้งสามที่ build มา :

```bash
docker images
```

> 📝 **คำอธิบาย:** ทั้งสาม image โชว์ขนาดเท่ากันเป๊ะ เพราะมันแชร์ layer `ubuntu + figlet` ชุดเดียวกันบนดิสก์ — ต่างกันจริง ๆ แค่ metadata (Entrypoint/Cmd) ไม่กี่ byte · นี่คืออีกผลพลอยได้ของ layer cache

✅ **Expected output** — ครบ 3 image ขนาดเท่ากัน (ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
IMAGE                       ID             DISK USAGE   CONTENT SIZE   EXTRA
both-example:latest         fc71b0a6f172        119MB           30MB
cmd-example:latest          adf5bfd664c8        119MB           30MB
entrypoint-example:latest   c003c08afc15        119MB           30MB
```

### ตารางสรุป — ท่องไม่ต้อง เข้าใจพอ

| image กำหนดอะไรไว้ | `docker run <image>` (ไม่มี args) | `docker run <image> date` (มี args) |
|---|---|---|
| **CMD อย่างเดียว** (`cmd-example`) | รันตาม CMD → `figlet "Hello CMD"` | args **แทนที่ CMD ทั้งก้อน** → รัน `date` ได้วันเวลาจริง |
| **ENTRYPOINT อย่างเดียว** (`entrypoint-example`) | รันตาม ENTRYPOINT → `figlet Hello` | args **ต่อท้าย** → `figlet Hello date` (คำว่า date ถูกวาด!) |
| **ทั้งคู่** (`both-example`) | ENTRYPOINT + CMD ต่อกัน → `figlet "Hello Docker"` | args **แทนที่เฉพาะ CMD** → `figlet date` (figlet ยังอยู่) |

> ข้อยกเว้นเดียวของตาราง : flag `--entrypoint` (ข้อ 6.4) เปลี่ยนตัว ENTRYPOINT เองได้ตอน run

---

## ทดลองเพิ่มเติม

### ก. ส่ง "option" ให้โปรแกรมผ่าน ENTRYPOINT — เหมือน CLI จริง ๆ

```bash
docker run --rm both-example -f slant "Docker"
```

> 📝 **คำอธิบาย:** ทุกอย่างหลังชื่อ image (`-f slant "Docker"`) ถูกต่อท้าย ENTRYPOINT กลายเป็น `figlet -f slant "Docker"` — `-f slant` ตรงนี้คือ option **ของ figlet** (เลือกฟอนต์เอียง) ไม่ใช่ของ docker เพราะ docker เลิกอ่าน option ตั้งแต่เจอชื่อ image แล้ว ·
> เพราะแบบนี้เอง image ประเภท CLI tool (เช่น `docker run aquasec/trivy image ...`) ถึงออกแบบด้วย ENTRYPOINT — ผู้ใช้ส่ง subcommand/option ได้เป็นธรรมชาติ

✅ **Expected output** — ฟอนต์เปลี่ยนเป็นตัวเอียง:

```
    ____             __
   / __ \____  _____/ /_____  _____
  / / / / __ \/ ___/ //_/ _ \/ ___/
 / /_/ / /_/ / /__/ ,< /  __/ /
/_____/\____/\___/_/|_|\___/_/
```

### ข. ลืม `--rm` แล้วเกิดอะไรขึ้น?

```bash
docker run cmd-example
docker ps -a
```

> 📝 **คำอธิบาย:** รอบนี้จงใจไม่ใส่ `--rm` — figlet วาดเสร็จ โปรแกรมจบ container กลายเป็นสถานะ `Exited` แต่ **ซากยังอยู่** · `docker ps -a` (มี `-a` ถึงจะเห็นตัวที่หยุดแล้ว) จะเจอ container ชื่อสุ่ม ๆ ที่ Docker ตั้งให้

✅ **Expected output** — มีซาก `Exited (0)` หนึ่งแถว (ID · ชื่อสุ่มของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
CONTAINER ID   IMAGE         COMMAND                CREATED        STATUS                              PORTS     NAMES
d22aeaa46b50   cmd-example   "figlet 'Hello CMD'"   1 second ago   Exited (0) Less than a second ago             distracted_noether
```

เก็บซากทิ้งด้วยคำสั่งเดียว :

```bash
docker container prune -f
```

> 📝 **คำอธิบาย:** `container prune` ลบ container ที่หยุดแล้ว **ทุกตัว** ในครั้งเดียว (`-f` = ไม่ต้องถามยืนยัน) · รันแล็บทั้งวันแล้วเจอซากกอง ๆ ให้นึกถึงคำสั่งนี้ — แต่ทางที่ดีคือติดนิสัยใส่ `--rm` กับ container ใช้แล้วทิ้งตั้งแต่แรก

✅ **Expected output** — รายงาน ID ที่ลบและพื้นที่ที่ได้คืน:

```
Deleted Containers:
d22aeaa46b50938582c4eb9cedd5d2a825afe8c06083b1296fd47e0f6d0ea463

Total reclaimed space: 4.096kB
```

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ERROR: failed to read dockerfile: open Dockerfile: no such file or directory` | ลืม `-f` — Docker มองหาไฟล์ชื่อ `Dockerfile` ซึ่งโฟลเดอร์นี้ไม่มี | ใส่ `-f Dockerfile-CMD` (หรือไฟล์ที่ต้องการ) ให้ครบ |
| `ERROR: docker: 'docker buildx build' requires 1 argument` | ลืม `.` (build context) ท้ายคำสั่ง build | เติม `.` ปิดท้ายเสมอ — จุดเดียวเปลี่ยนชีวิต |
| `pull access denied for cmd-example, repository does not exist` | พิมพ์ชื่อ image ผิด หรือยังไม่ได้ build / ลบไปแล้ว — Docker เลยพยายามไป pull จาก Hub | `docker images` เช็กชื่อที่มีจริง แล้ว build ใหม่ตามข้อ 3 |
| พิมพ์ `date` ต่อท้ายแล้วได้ ASCII คำว่า "date" แทนวันเวลา | image นั้นใช้ ENTRYPOINT — args ถูกต่อท้าย ไม่ใช่แทนที่ | ถูกต้องแล้ว! นี่คือบทเรียนของแล็บ · อยากรันคำสั่งจริงใช้ `--entrypoint date` (ข้อ 6.4) |
| figlet วาดข้อความไทยเป็นลายเส้นเพี้ยน | figlet ไม่รองรับ UTF-8/อักษรไทย | ใช้ข้อความอังกฤษหรือตัวเลข เช่น `"DevOps 2569"` |
| `docker ps -a` มี container `Exited` กองหลายตัว | รัน `docker run` โดยไม่ใส่ `--rm` | `docker container prune -f` เก็บกวาด แล้วติดนิสัย `--rm` |

---

## 9. ล้างกระดาน (cleanup)

แล็บนี้ใช้ `--rm` ทุกครั้ง จึง**ไม่มี container ให้ลบ** — เหลือแค่ image สามตัว :

```bash
docker rmi cmd-example entrypoint-example both-example
docker images
docker ps -a
```

> 📝 **คำอธิบาย:** `docker rmi` ลบ image ตามชื่อ ใส่หลายตัวได้ในคำสั่งเดียว · `docker images` ตรวจว่า image หมดเกลี้ยง · `docker ps -a` ปิดท้ายเพื่อชี้จุดที่ตั้งใจสอน — **ตารางว่างมาตั้งแต่ต้น** เพราะทุก `docker run` ของแล็บนี้ใส่ `--rm` (ยกเว้นทดลอง ข. ที่เราก็ prune ไปแล้ว) ·
> ถ้า `rmi` ฟ้องว่า image is being used ให้เช็กว่ามี container ค้างจาก `docker ps -a` แล้วลบ container ก่อน

✅ **Expected output** — `rmi` รายงาน Untagged/Deleted ครบสามตัว แล้วทั้งสองตารางเหลือแค่หัว ไม่มีแถวข้อมูล:

```
Untagged: cmd-example:latest
Deleted: sha256:adf5bfd664c8cd1df20c78e28979288976651fa8a9fddd75f72972708dc34a5e
Untagged: entrypoint-example:latest
Deleted: sha256:c003c08afc15269c444675888225fa44ff2e410088f3cb616cd78d1c79d8b3ee
Untagged: both-example:latest
Deleted: sha256:fc71b0a6f1720b032e20475548c297d3e09a49804bad6f80967d218626d52304
IMAGE   ID             DISK USAGE   CONTENT SIZE   EXTRA
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

---

## สรุปสิ่งที่ได้เรียนรู้

| สิ่งที่ทำ | คำสั่ง/แนวคิดหลัก | ทำไมสำคัญ |
|---|---|---|
| Build 3 image จากโฟลเดอร์เดียว | `docker build -t <ชื่อ> -f <ไฟล์> .` | เลือกไฟล์ Dockerfile เองได้ ไม่ต้องตั้งชื่อ `Dockerfile` เสมอไป |
| เห็น cache ทำงานข้ามไฟล์ | ขั้นต้นเหมือนกัน → `CACHED` เสร็จใน ~1 วิ | เข้าใจว่าทำไมต้องเรียงบรรทัดที่เปลี่ยนบ่อยไว้ล่างสุดของ Dockerfile |
| พิสูจน์นิสัย CMD | args ท้าย `docker run` **แทนที่ CMD ทั้งก้อน** | CMD = ค่าเริ่มต้น เหมาะกับ image ที่ให้ผู้ใช้สลับคำสั่งอิสระ |
| พิสูจน์นิสัย ENTRYPOINT | args ถูก **ต่อท้าย** — `date` กลายเป็นข้อความ | ENTRYPOINT = โปรแกรมหลักที่การันตีว่ารันเสมอ |
| ใช้สูตรมาตรฐาน | `ENTRYPOINT ["figlet"]` + `CMD ["Hello Docker"]` | โปรแกรมคงที่ + argument เริ่มต้นที่เปลี่ยนง่าย — สูตรของ image ดัง ๆ ทั่วโลก |
| หาทางหนีไฟ | `docker run --entrypoint <คำสั่ง> <image>` | เปลี่ยนโปรแกรมหลักตอน run ได้ เวลาต้อง debug image คนอื่น |
| อ่าน metadata ยืนยัน | `docker inspect --format '{{json .Config.Entrypoint}}'` | ตรวจ image ใด ๆ ได้โดยไม่ต้องเดาหรือแกะ Dockerfile |
| รันแบบใช้แล้วทิ้ง | `docker run --rm` | ไม่เหลือซาก `Exited` ให้ตามเก็บทีหลัง |

จบแล็บนี้ เราออกแบบ "ประตูทางเข้า" ของ image เป็นแล้ว — รู้ว่าเมื่อไรควรใช้ CMD, เมื่อไรควรล็อกด้วย ENTRYPOINT และทำไม image ดี ๆ ถึงใช้ทั้งคู่ · ใน **LAB 3** จะพา image ที่เรา build ออกเดินทางไกลขึ้น : ตั้งชื่อตามมาตรฐาน `<username>/<repo>:<tag>` แล้ว **push ขึ้น Docker Hub** ให้คนทั้งโลก pull ไปรันได้จริง

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `docker --version` และ `docker info --format ...` ขึ้นเลขเวอร์ชันทั้งคู่ ไม่มี error
- [ ] `ls -1` ในโฟลเดอร์แล็บเห็น Dockerfile ครบ 3 ไฟล์ และอธิบายได้ว่าสามไฟล์ต่างกันตรงไหน
- [ ] build `cmd-example` ผ่าน (รอบแรกช้า ~10–15 วิ เพราะ pull + apt-get)
- [ ] `docker run --rm cmd-example` ได้ ASCII "Hello CMD" · ต่อท้ายด้วย `date` แล้ว figlet **หายทั้งก้อน**
- [ ] ใส่ชื่อตัวเองด้วย `docker run --rm cmd-example figlet "<ชื่อ>"` สำเร็จ
- [ ] build `entrypoint-example` เห็น `#5 CACHED` และเสร็จใน ~1 วินาที
- [ ] `docker run --rm entrypoint-example date` วาด **คำว่า date** — และอธิบายได้ว่าทำไม
- [ ] `--entrypoint date` ได้วันเวลาจริง
- [ ] `both-example` : รันเปล่าได้ "Hello Docker" · ใส่ข้อความเองแล้ว figlet ยังอยู่
- [ ] `docker inspect --format ...` อ่านค่า ENTRYPOINT/CMD ตรงกับ Dockerfile ทั้งสามไฟล์
- [ ] เติมตาราง 3×2 (image × มี/ไม่มี args) ได้เองโดยไม่เปิดเอกสาร
- [ ] `docker rmi` ทั้งสาม image แล้ว `docker images` + `docker ps -a` เหลือแค่หัวตาราง

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` เมื่อ 12 ส.ค. 2026*
