# LAB 3 — RUN vs CMD vs ENTRYPOINT

> โฟลเดอร์ `003_LAB_RUN_CMD_ENTRYPOINT` = **LAB 3** ของชุด "Dockerfile → Build → Run → Compose" (ตรงกับ **ตอนที่ 6** ของคู่มือ)
> คำถามเดียวที่แล็บนี้ตอบให้จบ : **คำสั่งไหนทำงานตอน build · คำสั่งไหนทำงานตอนเริ่ม container · และสิ่งที่เราพิมพ์ต่อท้ายชื่อ image ไป "แทนที่" หรือ "ต่อท้าย" อะไรกันแน่**
> ไฟล์ในโฟลเดอร์นี้ : `Dockerfile.run` · `Dockerfile.cmd` · `Dockerfile.entrypoint` · `Dockerfile.both` · `Dockerfile.multicmd` ·
> `Dockerfile.execform` · `Dockerfile.shellform` · `Dockerfile.sigexec` · `Dockerfile.sigshell` · `Dockerfile.nocmd` · `Dockerfile.nocmd_reset` ·
> `app.sh` · `verify.sh`

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | สิ่งที่พิมพ์ต่อท้ายชื่อ image ไป **แทนที่** หรือไป **ต่อท้าย** อะไรกันแน่ |
| **ต้องผ่านอะไรมาก่อน** | **LAB 1** (โดยเฉพาะ `-f` และการแทนคำสั่งตอน run ในทดลอง ก.) |
| **เวลา** | ~35 นาที (แกนหลัก ข้อ 0–10 ประมาณ 25 นาที · ทดลองเพิ่มเติม ~10 นาที) |
| **จบแล้วต้องทำได้เอง** | เลือก `CMD` / `ENTRYPOINT` / ทั้งคู่ ให้ตรงงาน · อ่าน `.Config.Cmd` กับ `.Config.Entrypoint` แทนการเดา · บอกได้ว่าทำไม `docker stop` บางตัวช้า 10 วินาที |
| **แล็บนี้ยัง *ไม่* สอน** | `ENV`/`ARG` → **LAB 4** · แล็บนี้ **ไม่มีหน้าเว็บและไม่ต้องเปิดพอร์ต** ใช้เทอร์มินัลเดียวจบ |

## สิ่งที่จะได้เรียนรู้

- **เส้นเวลาของ Dockerfile** : `RUN` เกิดตอน `docker build` (ผลถูกอบลง layer ถาวร) ส่วน `CMD`/`ENTRYPOINT` เป็นแค่ **metadata** ที่มีผลตอน `docker run`
- **CMD ถูกแทนที่** — พิมพ์อะไรต่อท้ายชื่อ image คำสั่งนั้น **ทับ CMD ทั้งชุด**
- **ENTRYPOINT ถูกต่อท้าย** — ค่าหลังชื่อ image กลายเป็น **argument** ของโปรแกรมหลัก และต้องใช้ `--entrypoint` ถ้าจะเปลี่ยนโปรแกรม
- **ENTRYPOINT + CMD** = โปรแกรมหลักตายตัว + argument เริ่มต้นที่ผู้ใช้ปรับได้ (รูปแบบยอดฮิตของ image ที่เป็นเครื่องมือ)
- อ่าน **metadata จริง** ด้วย `docker image inspect --format '{{.Config.Entrypoint}} | {{.Config.Cmd}}'` แทนการเดา · และรู้ว่า `CMD` หลายบรรทัด **มีผลแค่บรรทัดสุดท้าย**
- **exec form vs shell form** : ใครได้เป็น **PID 1** · ใครได้รับ **SIGTERM** · และทำไม `docker stop` บาง container ใช้เวลา **10 วินาที** ทุกครั้ง
- เทคนิคที่ใช้จริงตอน debug : `--entrypoint sh` และการอ่าน `ps -o pid,args` ข้างใน container

## ภาพรวมของแล็บนี้

แล็บนี้ไม่มีหน้าเว็บและไม่มี port ให้เปิด — เป็นแล็บ "ทายผลแล้วเปิดฝาดู" ล้วน ๆ ทำในหน้าต่างเดียวจบ
1. **เตรียมเครื่องเรียน + clone โค้ด** — เปิด container `devtools-df-lab3` แล้ว ssh เข้าไปทำงานข้างใน (โฟลเดอร์เดียวมี Dockerfile หลายไฟล์ จึงต้องใช้ `-f` เลือกทีละไฟล์)
2. **6.1 RUN** — สร้างไฟล์และติดตั้ง `curl` ตอน build แล้วพิสูจน์ว่าของยังอยู่แม้แทนที่คำสั่งตอน run
3. **6.2 CMD** — รันเปล่า ๆ vs รันพร้อมคำสั่งต่อท้าย เห็นว่า CMD **ถูกทับทั้งชุด**
4. **6.3 ENTRYPOINT** — คำเดียวกันเป๊ะ แต่คราวนี้ถูก **ต่อท้ายเป็น argument** ไม่ได้ทับ
5. **6.4 ENTRYPOINT + CMD** — `ping` + argument เริ่มต้น เปลี่ยนเฉพาะ argument ได้โดยไม่ต้องพิมพ์ชื่อโปรแกรมซ้ำ
6. **ส่อง metadata ทั้ง 4 image + CMD หลายบรรทัด** — ตารางเดียวจบ ว่าที่เห็นตอนรันมาจากช่องไหนของ image
7. **exec form vs shell form** — ดู PID 1 ด้วย `ps` (มีเซอร์ไพรส์ของ Alpine รออยู่) แล้ววัดเวลา `docker stop` จริง — รอบแรกใช้ `sleep` ซึ่ง **ช้าทั้งคู่ ~10 วินาที** · รอบสองใช้แอปที่ดัก SIGTERM จริงจึงเห็นความต่าง 223 ms vs 10,228 ms
8. **ตารางสรุป + เลือกใช้ให้ตรงงาน** แล้วปิดท้ายด้วย `verify.sh`

> **คำถามก่อนเริ่ม:** ถ้า Dockerfile ปิดท้ายด้วย `CMD ["python", "app.py"]` แล้วเราสั่ง `docker run image sh` เราจะได้ shell
> แต่ถ้าเปลี่ยนบรรทัดนั้นเป็น `ENTRYPOINT ["python", "app.py"]` แล้วสั่งคำสั่งเดิม **เราจะได้อะไร?**
> และถ้าเขียน `CMD sleep 300` (ไม่มีวงเล็บเหลี่ยม) แทน `CMD ["sleep","300"]` ตอนกด `docker stop` จะต่างกันไหม — ต่างกี่วินาที?
> ลองทายไว้ในใจก่อน แล้วค่อยรันทีละขั้น

---

## ทฤษฎีก่อนลงมือ

### ภาพจำหลัก

แก่นของแล็บ: `RUN` สร้าง layer ตอน build ส่วน `CMD` และ `ENTRYPOINT` รอประกอบเป็นคำสั่งตอน run

![ตารางเทียบ CMD เดี่ยว ENTRYPOINT เดี่ยว และทั้งคู่กับคำสั่งจริง](./images/theory-cmd-vs-entrypoint.svg)

> 🖼 **วิธีอ่านรูปนี้:** อ่านแต่ละแถวจาก metadata ผ่านค่าหลังชื่อ image ไปยังคำสั่งจริงทางขวา ค่านั้นแทน `CMD` ทั้งก้อน แต่ไม่แทน `ENTRYPOINT`; เมื่อมีทั้งคู่ Docker จึงคงโปรแกรมหลักแล้วต่อ argument ชุดใหม่ ทั้งสามแถวตรงกับการทดลองข้อ 3–5

### กลไกจริง

ตอน `docker build` Docker อ่าน Dockerfile ตามลำดับ เมื่อพบ `RUN` จะทำคำสั่งใน container ชั่วคราว แล้วบันทึก filesystem ที่เปลี่ยนเป็น layer ของ image ไฟล์และโปรแกรมจึงยังอยู่ แม้ข้อ 2 จะเปลี่ยนคำสั่งตอน run ส่วน `CMD` และ `ENTRYPOINT` ยังไม่ทำงาน แต่ถูกเก็บเป็น metadata คล้ายฉลากบนกล่องว่า “เมื่อเปิด ให้เริ่มด้วยอะไร”

เมื่อ `docker run` เริ่ม Docker นำ filesystem ของ image มาสร้าง container แล้วประกอบคำสั่งจาก `ENTRYPOINT` กับ `CMD` เพื่อสร้าง process หลัก หากไม่มีค่าหลังชื่อ image จะใช้ `CMD` เดิม แต่ถ้ามี ค่านั้นจะแทน `CMD` ทั้งชุด ไม่ได้ต่อท้ายของเดิม ดังข้อ 3

![เส้นเวลาแสดงว่า RUN ทำงานตอน build ส่วน CMD และ ENTRYPOINT ถูกจดเป็น metadata ไว้ใช้ตอน run](./images/theory-build-vs-run-timeline.svg)

> 🖼 **วิธีอ่านรูปนี้:** อ่านจากซ้ายไปขวาตามหมายเลข ① → ② โดยมี **image เป็นตัวคั่นกลาง** · ฝั่ง ① มีแค่ `RUN` เท่านั้นที่ทำงานจริงและทิ้งผลไว้เป็น layer ส่วน `CMD`/`ENTRYPOINT` แค่ถูกจดลงช่อง metadata (สองช่องนี้คือสิ่งที่ข้อ 6 จะเปิดดูด้วย `docker image inspect`) · ฝั่ง ② Docker หยิบสองช่องนั้นมาประกอบกับค่าที่เราพิมพ์ต่อท้ายชื่อ image จนได้คำสั่งจริงที่กลายเป็น **PID 1** ตามที่ข้อ 5 และข้อ 7 จะพิสูจน์

สำหรับ `ENTRYPOINT` แบบ exec form ที่แล็บนี้ใช้ `ENTRYPOINT` คือส่วนหัวที่คงอยู่ ส่วน `CMD` คือ argument เริ่มต้น (ถ้าเขียน `ENTRYPOINT` แบบ shell form `CMD` และค่าหลังชื่อ image จะถูกเมินทั้งหมด) ลองนึกถึงหัวรถจักรกับตู้โดยสาร: `ENTRYPOINT` เป็นหัวรถจักร ส่วนค่าหลังชื่อ image เป็นตู้ชุดใหม่ที่แทน `CMD` เดิม ภาพนี้อธิบายว่าทำไมข้อ 4 ส่ง `sh` แล้วไม่ได้ shell และข้อ 5 เปลี่ยนปลายทางได้โดยไม่พิมพ์ `ping` ซ้ำ

process หลักจะเป็น PID 1 และกำหนดอายุ container: เมื่อมันจบ container ก็จบ PID 1 บน Linux พิเศษตรงที่ kernel อาจไม่ใช้ default action ของสัญญาณ หากโปรแกรมไม่ได้ติดตั้ง signal handler จึงเห็นข้อ 7 ใช้ `sleep` แล้วช้าทั้ง exec form และ shell form แม้ `sleep` เป็น PID 1

`docker stop` ส่ง `SIGTERM` ให้ PID 1 เท่านั้น แล้วรอค่าเริ่มต้น 10 วินาที ถ้ายังอยู่จึงส่ง `SIGKILL` ในข้อ 8 exec form ทำให้ `app.sh` เป็น PID 1 รับสัญญาณ เข้า `trap` และจบด้วย code 0 แต่ shell form ที่มี `&& echo` ทำให้ `sh` เป็น PID 1 Docker ไม่ได้ส่งสัญญาณตรงถึงแอปลูก และ `sh` ไม่มี trap เพื่อส่งต่อ จึงรอครบเวลาและจบด้วย code 137

ข้อยกเว้นคือ shell form แบบคำสั่งเดี่ยวบน Alpine: BusyBox `ash` อาจ `exec` โปรแกรมแทนตัวเอง โปรแกรมจึงเป็น PID 1 เหมือน exec form แล็บใช้ `&& echo` ในข้อ 8 เพื่อบังคับให้ `sh` อยู่ต่อและเผยเส้นทางสัญญาณจริง

### กฎที่ต้องจำ

| กฎ | ผลที่ใช้ทำนายการทดลอง |
|---|---|
| `RUN` เกิดตอน build | ผลอยู่ใน layer แม้เปลี่ยนคำสั่งตอน run |
| ค่าหลัง image แทน `CMD` ทั้งชุด | โปรแกรมและ argument เดิมถูกเปลี่ยนพร้อมกัน |
| exec-form `ENTRYPOINT` อยู่หน้า `CMD` | เปลี่ยน argument ได้ แต่โปรแกรมหลักยังเดิม |
| container ผูกกับ PID 1 | PID 1 จบเมื่อใด container จบเมื่อนั้น |
| `docker stop` ส่งถึง PID 1 | แอปต้องจัดการ `SIGTERM` เพื่อปิดอย่างสุภาพ |

### สิ่งที่มักเข้าใจผิด

- คิดว่า `CMD` ทำงานตอน build แต่จริง ๆ มันเป็น metadata สำหรับ run; คำสั่งที่สร้าง layer คือ `RUN`
- คิดว่าค่าหลัง image ต่อท้ายเสมอ แต่จริง ๆ มันแทน `CMD` ทั้งก้อน แล้วจึงต่อท้าย `ENTRYPOINT`
- คิดว่า exec form หยุดเร็วเสมอ แต่จริง ๆ PID 1 ต้องมี signal handler; ส่วนคำสั่งเดี่ยวบน Alpine อาจถูก `ash` ทำ `exec`

### ทายผลก่อนทดลอง

1. ก่อนข้อ 2–3 ทายว่าเมื่อแทนคำสั่งตอน run ไฟล์จาก `RUN` กับข้อความจาก `CMD` สิ่งใดยังอยู่ และสิ่งใดไม่ถูกเรียก
2. ก่อนข้อ 7–8 ทายว่า container ใดมีแอปเป็น PID 1 ตัวใดมี `sh` คั่น และสิ่งนี้สัมพันธ์กับเวลา stop กับ ExitCode อย่างไร

## 0. เตรียมเครื่องเรียน

ทำบนเครื่องของเราเอง — เปิด container ที่ติดตั้ง Docker มาให้แล้ว (Docker-in-Docker) :

```bash
docker rm -f devtools-df-lab3 2>/dev/null
docker run -dit --name devtools-df-lab3 --privileged \
  -p 2233:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2233        # password : passwd
```

> 📝 **คำอธิบาย:** บรรทัดแรกลบกล่องเก่าทิ้งก่อนถ้ามีค้างอยู่ (`2>/dev/null` ซ่อนข้อความตอนที่ยังไม่มี) · `-dit` = `-d` รันเบื้องหลัง + `-i` เปิด stdin ค้าง +
> `-t` ให้มี terminal รวมกันแล้วกล่องไม่ดับทันที · `--privileged` ให้สิทธิ์เต็มเพื่อรัน **Docker ซ้อนข้างในกล่อง** (แล็บนี้จะ `docker build` ข้างในอีกชั้นหนึ่ง) ·
> `-p 2233:22` ส่ง port 2233 ของเครื่องเรา เข้า port 22 (SSH) ของกล่อง — **แล็บนี้ไม่มี app port อื่น** เพราะไม่มีหน้าเว็บให้เปิด ·
> บรรทัดสาม ssh เข้าไปทำงานข้างใน (พิมพ์ `passwd` แล้ว prompt จะเปลี่ยนเป็นของเครื่องเรียน) — **คำสั่งทุกคำสั่งในแล็บนี้สั่งข้างในเครื่องเรียนทั้งหมด** ·
> ใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2233` ได้เหมือนกัน

ตรวจว่าพร้อมใช้งาน — สองบรรทัดนี้ต้องขึ้น **เลขเวอร์ชัน** ไม่ใช่ error :

```bash
docker --version
docker info --format 'Docker daemon: {{.ServerVersion}}'
```

> 📝 **คำอธิบาย:** บรรทัดแรกเช็ก Docker CLI บรรทัดที่สองถาม daemon โดยตรง เพื่อยืนยันว่า Docker ข้างในกล่องตื่นแล้ว · สิ่งที่ต้องดูคือ "มีเลขเวอร์ชันขึ้นไหม"
> ไม่ใช่ "เลขตรงกับเอกสารไหม" · ถ้าขึ้น `Cannot connect to the Docker daemon` แปลว่า daemon ข้างในยังไม่ตื่น รอสัก 10–20 วินาทีแล้วลองใหม่

✅ **Expected output** — เลขเวอร์ชันของแต่ละคนอาจไม่ตรงกับเอกสารนี้:

```
Docker version 29.6.2, build dfc4efb
Docker daemon: 29.6.2
```

---

## 1. Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide/003_LAB_RUN_CMD_ENTRYPOINT
ls
```

> 📝 **คำอธิบาย:** `mkdir -p` สร้างโฟลเดอร์เก็บงาน (`-p` = มีอยู่แล้วก็ไม่ error) · ถ้าเคย clone จากแล็บก่อนแล้ว git จะบอกว่าโฟลเดอร์ไม่ว่าง — ข้ามไป `cd` ได้เลย ·
> **จุดสำคัญของแล็บนี้** : ในโฟลเดอร์เดียวมี Dockerfile **หลายไฟล์** ซึ่ง `docker build` จะหาไฟล์ชื่อ `Dockerfile` เป็นค่าเริ่มต้นเสมอ เราจึงต้องใช้ `-f <ชื่อไฟล์>` ทุกครั้ง (ทบทวนจากตอนที่ 4)

✅ **Expected output** — `ls` ต้องเห็น Dockerfile **11 ไฟล์** (`.run` `.cmd` `.entrypoint` `.both` `.multicmd` `.execform` `.shellform` `.sigexec` `.sigshell` `.nocmd` `.nocmd_reset`) พร้อม `app.sh` และ `verify.sh`

---

## 2. 6.1 `RUN` — ทำงานตอน `docker build`

`RUN` ใช้ติดตั้งโปรแกรม สร้างไฟล์ หรือ compile source **ผลลัพธ์ถูกบันทึกเป็น layer ของ image** ไม่ต้องทำซ้ำทุกครั้งที่ container เริ่ม
```dockerfile
# Dockerfile.run
FROM alpine:3.20
RUN echo "สร้างไฟล์ในขั้น Build" > /message.txt
RUN apk add --no-cache curl
CMD ["cat", "/message.txt"]
```

```bash
docker build -f Dockerfile.run -t demo-run .
```

> 📝 **คำอธิบาย:** `-f Dockerfile.run` เลือกไฟล์ Dockerfile (ถ้าไม่ใส่ Docker จะหาไฟล์ชื่อ `Dockerfile` เฉย ๆ แล้วพัง) · `-t demo-run` ตั้งชื่อ image ·
> **จุดที่มักพลาด** : `.` ท้ายคำสั่งคือ **build context** (โฟลเดอร์ที่ส่งให้ daemon) ไม่ใช่ชื่อไฟล์ Dockerfile · `apk add --no-cache curl` เป็นวิธีติดตั้งของ Alpine (`apk` ไม่ใช่ `apt`) และ `--no-cache` ทำให้ไม่มี package index ค้างใน layer

✅ **Expected output** — ดูว่า **`RUN` ทั้งสองบรรทัดถูกรันตอนนี้** (ตอน build ไม่ใช่ตอน run) แล้วปิดท้ายด้วย `naming to docker.io/library/demo-run` (เลข sha256 · เวลา · เวอร์ชัน package ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
#5 [2/3] RUN echo "สร้างไฟล์ในขั้น Build" > /message.txt
#5 DONE 0.3s
#6 [3/3] RUN apk add --no-cache curl
#6 0.338 fetch https://dl-cdn.alpinelinux.org/alpine/v3.20/main/x86_64/APKINDEX.tar.gz
        ... (ตัดท่อนกลาง — ติดตั้งครบ 10 package) ...
#6 1.245 (10/10) Installing curl (8.14.1-r2)
#6 DONE 1.4s
#7 exporting to image
#7 naming to docker.io/library/demo-run:latest done
```

ทีนี้ลองรันสองแบบ :
```bash
docker run --rm demo-run
docker run --rm demo-run curl --version
```

> 📝 **คำอธิบาย:** `--rm` ลบ container ทิ้งทันทีที่มันจบ (ไม่งั้นจะมีซาก `Exited` ค้างเต็มไปหมด — แล็บนี้รัน container สิบกว่ารอบ) · คำสั่งแรกไม่ได้ใส่อะไรต่อท้าย
> จึงใช้ `CMD` เดิมคือ `cat /message.txt` · คำสั่งที่สองใส่ `curl --version` ต่อท้าย = **แทนที่ CMD** · **สิ่งที่ต้องสังเกต** : ถึง CMD จะถูกแทนที่ แต่ `curl` ยังใช้ได้ เพราะถูกติดตั้ง **ถาวรอยู่ใน image** ตั้งแต่ตอน build

✅ **Expected output** — บรรทัดแรกคือไฟล์ที่ `RUN` สร้างไว้ · ท่อนที่สองพิสูจน์ว่า `curl` ที่ `RUN` ติดตั้งยังอยู่ (เลขเวอร์ชัน curl ของแต่ละคนอาจไม่ตรงกับเอกสารนี้):

```
สร้างไฟล์ในขั้น Build
curl 8.14.1 (x86_64-alpine-linux-musl) libcurl/8.14.1 OpenSSL/3.3.7 zlib/1.3.2 brotli/1.1.0 ...
Release-Date: 2025-06-04
        ... (ตัดท่อนกลาง — บรรทัด Protocols / Features) ...
```

> **สรุปข้อ 6.1 :** `RUN` = "อบเข้า image" · `CMD` = "คำสั่งเริ่มต้นตอนเปิดกล่อง" · เปลี่ยนคำสั่งตอน run ได้ แต่ **ของที่ `RUN` ติดตั้งไว้ไม่หายไปไหน**

## 3. 6.2 `CMD` — ค่าเริ่มต้นที่ **ถูกแทนที่**

```dockerfile
# Dockerfile.cmd
FROM alpine:3.20
CMD ["echo", "ข้อความเริ่มต้นจาก CMD"]
```

```bash
docker build -f Dockerfile.cmd -t demo-cmd .
docker run --rm demo-cmd
docker run --rm demo-cmd echo "แทนที่ CMD แล้ว"
```

> 📝 **คำอธิบาย:** `CMD` เขียนเป็น **exec form** (JSON array — วงเล็บเหลี่ยม + double quote เท่านั้น ใช้ single quote ไม่ได้) · รอบแรกไม่ใส่อะไรต่อท้ายจึงใช้ค่าใน image ·
> รอบสองใส่ `echo "แทนที่ CMD แล้ว"` ต่อท้ายชื่อ image → **ทับ CMD ทั้งชุด** · **จุดที่มักพลาด** : หลายคนคิดว่าจะได้สองข้อความ แต่ได้แค่ข้อความใหม่ เพราะของเดิมหายไปทั้งบรรทัด

✅ **Expected output** — สองบรรทัด และ **ข้อความเดิมไม่โผล่ในรอบที่สอง**:

```
ข้อความเริ่มต้นจาก CMD
แทนที่ CMD แล้ว
```

| `docker run` | คำสั่งจริงที่ถูกเรียก | เหตุผล |
|---|---|---|
| `docker run demo-cmd` | `echo "ข้อความเริ่มต้นจาก CMD"` | ไม่ได้ส่งคำสั่งใหม่ จึงใช้ `CMD` ใน image |
| `docker run demo-cmd echo "แทนที่ CMD แล้ว"` | `echo "แทนที่ CMD แล้ว"` | ค่าหลังชื่อ image **แทน `CMD` ทั้งชุด** |
| `docker run demo-cmd cat /etc/alpine-release` | `cat /etc/alpine-release` | เปลี่ยนได้แม้กระทั่ง **โปรแกรม** ไม่ใช่แค่ argument |

ลองข้อสามด้วยตัวเอง : `docker run --rm demo-cmd cat /etc/alpine-release` → ได้ `3.20.10` (เลข patch ของแต่ละคนอาจต่างกัน) ไม่ใช่ข้อความเดิมของ `CMD`

---

## 4. 6.3 `ENTRYPOINT` — โปรแกรมหลักที่ **ต่อท้าย** argument

```dockerfile
# Dockerfile.entrypoint
FROM alpine:3.20
ENTRYPOINT ["echo", "ข้อความจาก ENTRYPOINT:"]
```

```bash
docker build -f Dockerfile.entrypoint -t demo-entrypoint .
docker run --rm demo-entrypoint
docker run --rm demo-entrypoint สวัสดี Docker
```

> 📝 **คำอธิบาย:** Dockerfile นี้ต่างจากข้อ 6.2 แค่คำเดียว — เปลี่ยน `CMD` เป็น `ENTRYPOINT` · รอบแรกได้ผลเหมือนกันเป๊ะ (ดูไม่ออกว่าต่างกัน!) · **ความต่างโผล่ตอนใส่ค่าต่อท้าย** :
> `สวัสดี Docker` ไม่ได้ทับอะไรเลย แต่ถูกประกอบเป็น `echo "ข้อความจาก ENTRYPOINT:" "สวัสดี" "Docker"` · **จุดที่มักพลาด** : เขียน `ENTRYPOINT` ไว้แล้วสั่ง `docker run image sh` หวังจะได้ shell — จะไม่ได้ (ดู "ทดลองเพิ่มเติม" ข้อ 1)

✅ **Expected output** — รอบแรกได้ข้อความเปล่า ๆ · รอบสอง **ข้อความเดิมยังอยู่** แล้วมีคำที่เราพิมพ์ต่อท้ายมาด้วย:

```
ข้อความจาก ENTRYPOINT:
ข้อความจาก ENTRYPOINT: สวัสดี Docker
```

ถ้าอยากเปลี่ยน **โปรแกรมหลัก** ต้องใช้ option `--entrypoint` :

```bash
docker run --rm --entrypoint sh demo-entrypoint -c "echo เปลี่ยนโปรแกรมหลัก"
```

> 📝 **คำอธิบาย:** `--entrypoint sh` เขียน **ก่อนชื่อ image** เสมอ (เป็น option ของ `docker run` ไม่ใช่ของ image) และรับได้แค่ **ชื่อโปรแกรมตัวเดียว** · ส่วนที่อยู่หลังชื่อ image
> (`-c "echo ..."`) กลายเป็น argument ของ `sh` · **ของแถมที่ต้องรู้** : พอใส่ `--entrypoint` ค่า `CMD` เดิมที่ติดมากับ image จะถูก **ล้างทิ้ง** ไปด้วย ถ้าอยากได้ argument ต้องพิมพ์ต่อท้ายชื่อ image เอง ·
> นี่คือท่าที่ใช้จริงทุกครั้งที่ต้องเข้าไปส่องข้างใน image ที่มี ENTRYPOINT

✅ **Expected output** — ได้เฉพาะ `เปลี่ยนโปรแกรมหลัก` ไม่มี `ข้อความจาก ENTRYPOINT:` เหลืออยู่เลย

### ภาพเทียบ : ค่าหลังชื่อ image ไปไหน?

```
  CMD อย่างเดียว  ──  ค่าหลังชื่อ image "แทนที่" ทั้งชุด
  ======================================================================
    $ docker run demo-cmd  echo "แทนที่ CMD แล้ว"
                           +------------+------------+
      ENTRYPOINT : (ว่าง)               |  ทับทิ้งทั้งชุด
      CMD        : [ echo , "ข้อความเริ่มต้นจาก CMD" ]  x  ถูกทิ้ง
      ----------------------------------------------------------------
      คำสั่งจริง  :  echo "แทนที่ CMD แล้ว"

  ENTRYPOINT อย่างเดียว  ──  ค่าหลังชื่อ image "ต่อท้าย" เป็น argument
  ======================================================================
    $ docker run demo-entrypoint  สวัสดี Docker
                                  +------+------+  ต่อท้าย ไม่ทับ
      ENTRYPOINT : [ echo , "ข้อความจาก ENTRYPOINT:" ]  |
      argument   :                               [ สวัสดี , Docker ]
      ----------------------------------------------------------------
      คำสั่งจริง  :  echo "ข้อความจาก ENTRYPOINT:" "สวัสดี" "Docker"
      * จะเปลี่ยนโปรแกรมหลักต้องใช้ --entrypoint เท่านั้น *
```

---

## 5. 6.4 `ENTRYPOINT` + `CMD` — โปรแกรมหลัก + argument เริ่มต้น

```dockerfile
# Dockerfile.both
FROM alpine:3.20
ENTRYPOINT ["ping"]
CMD ["-c", "2", "127.0.0.1"]
```

```bash
docker build -f Dockerfile.both -t demo-both .
docker run --rm demo-both
docker run --rm demo-both -c 1 localhost
```

> 📝 **คำอธิบาย:** เมื่อใช้ **exec form ทั้งคู่** Docker จะเอา `ENTRYPOINT` มาต่อหน้า `CMD` เป็นคำสั่งเดียว = `ping -c 2 127.0.0.1` · พอผู้ใช้ใส่ `-c 1 localhost`
> ต่อท้ายชื่อ image ค่านั้นไป **แทน `CMD`** แต่ `ENTRYPOINT` (`ping`) ยังอยู่ → ได้ `ping -c 1 localhost` · **จุดที่มักพลาด** : ไม่ต้องพิมพ์คำว่า `ping` ซ้ำ — พิมพ์ไปจะกลายเป็น `ping ping ...` แล้วพัง ·
> **เงื่อนไขสำคัญ** : การรวมร่างนี้เกิดขึ้น **เฉพาะเมื่อ `ENTRYPOINT` เขียนเป็น exec form** เท่านั้น — ถ้าเขียน `ENTRYPOINT ping` (shell form) Docker จะห่อเป็น `/bin/sh -c "ping"` แล้ว **ละเลย `CMD` และค่าที่พิมพ์ต่อท้ายชื่อ image ทั้งหมด**

✅ **Expected output** — รอบแรก **2 packets** (มาจาก CMD) · รอบสอง **1 packet** และปลายทางเปลี่ยนเป็น `localhost` (`::1` = IPv6 loopback · ค่า time ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
PING 127.0.0.1 (127.0.0.1): 56 data bytes        PING localhost (::1): 56 data bytes
64 bytes from 127.0.0.1: seq=0 time=0.035 ms     64 bytes from ::1: seq=0 time=0.037 ms
64 bytes from 127.0.0.1: seq=1 time=0.042 ms     --- localhost ping statistics ---
--- 127.0.0.1 ping statistics ---                1 packets transmitted, 1 received, 0% loss
2 packets transmitted, 2 received, 0% loss
```

| การรัน | ENTRYPOINT | CMD / argument | คำสั่งจริง |
|---|---|---|---|
| `docker run demo-both` | `ping` | `-c 2 127.0.0.1` (ค่าใน image) | `ping -c 2 127.0.0.1` |
| `docker run demo-both -c 1 localhost` | `ping` | CMD เดิม **ถูกแทน** | `ping -c 1 localhost` |

---

## 6. เปิดฝาดู metadata ของทั้ง 4 image

ทุกอย่างที่เห็นมา **ไม่ใช่เวทมนตร์** — มันคือสองช่องใน metadata ของ image เท่านั้น :

```bash
for i in run cmd entrypoint both; do
  printf "%-16s %s\n" "demo-$i" \
    "$(docker image inspect --format '{{.Config.Entrypoint}} | {{.Config.Cmd}}' demo-$i)"
done
```

> 📝 **คำอธิบาย:** `docker image inspect` อ่าน metadata ของ image เป็น JSON · `--format` ใช้ **Go template** ดึงเฉพาะสองช่องที่เราสนใจคือ `.Config.Entrypoint`
> และ `.Config.Cmd` · วงเล็บปีกกาสองชั้น `{{ }}` เป็นไวยากรณ์ของ template ไม่ใช่ของ shell — ต้องครอบด้วย **single quote** ไม่งั้น shell จะแปลงเอง · `for i in ...` แค่วนพิมพ์ให้อ่านง่าย

✅ **Expected output** — ช่องว่าง `[]` คือ "ไม่ได้ตั้งไว้" · สังเกตว่า `demo-cmd` กับ `demo-entrypoint` เก็บข้อความไว้ **คนละช่อง** ทั้งที่ผลตอนรันเปล่า ๆ เหมือนกัน:

```
demo-run         [] | [cat /message.txt]
demo-cmd         [] | [echo ข้อความเริ่มต้นจาก CMD]
demo-entrypoint  [echo ข้อความจาก ENTRYPOINT:] | []
demo-both        [ping] | [-c 2 127.0.0.1]
```

> **นี่คือหลักฐานชิ้นสำคัญของแล็บ :** พฤติกรรม "แทนที่ vs ต่อท้าย" ไม่ได้ขึ้นกับคำที่เราพิมพ์ตอน `docker run` แต่ขึ้นกับว่าข้อความนั้น
> ถูกเก็บไว้ในช่อง **Cmd** (ทับได้) หรือช่อง **Entrypoint** (ทับไม่ได้ ต้องใช้ `--entrypoint`)

### `CMD` หลายบรรทัด — มีผลแค่บรรทัดสุดท้าย

`Dockerfile.multicmd` จงใจเขียน `CMD` **สองบรรทัด** : `CMD ["echo","CMD ตัวแรก - จะไม่ถูกใช้"]` แล้วตามด้วย `CMD ["echo","CMD ตัวสุดท้าย - ตัวนี้เท่านั้นที่มีผล"]`

```bash
docker build -f Dockerfile.multicmd -t demo-multicmd .
docker image inspect --format '{{.Config.Cmd}}' demo-multicmd
docker run --rm demo-multicmd
```

> 📝 **คำอธิบาย:** `CMD` (และ `ENTRYPOINT`) ไม่ได้ "สะสม" แบบ `RUN` — มันคือการ **เขียนทับค่าเดียวในช่อง metadata** บรรทัดหลังจึงทับบรรทัดก่อนเสมอ ·
> **จุดที่มักพลาด** : เขียน `CMD` ไว้กลางไฟล์แล้วเผลอเขียนอีกตัวตอนท้าย — ตัวแรกหายเงียบ ๆ ไม่มี warning · วิธีตรวจที่เร็วที่สุดคืออ่าน `.Config.Cmd`

✅ **Expected output** — ทั้ง metadata และผลรัน **ไม่มีคำว่า "ตัวแรก" หลงเหลืออยู่เลย**:

```
[echo CMD ตัวสุดท้าย - ตัวนี้เท่านั้นที่มีผล]
CMD ตัวสุดท้าย - ตัวนี้เท่านั้นที่มีผล
```

---

## 7. exec form vs shell form — ใครได้เป็น PID 1?

Dockerfile เขียน `CMD` ได้สองแบบ และมันไม่ได้ต่างกันแค่หน้าตา :

| แบบ | หน้าตา | Docker ทำอะไร |
|---|---|---|
| **exec form** | `CMD ["sleep", "300"]` | เรียกโปรแกรมตรง ๆ ไม่ผ่าน shell |
| **shell form** | `CMD sleep 300` | ห่อเป็น `/bin/sh -c "sleep 300"` ให้อัตโนมัติ |

```bash
docker build -f Dockerfile.execform  -t demo-execform .
docker build -f Dockerfile.shellform -t demo-shellform .
docker image inspect --format '{{.Config.Cmd}}' demo-execform     # -> [sleep 300]
docker image inspect --format '{{.Config.Cmd}}' demo-shellform    # -> [/bin/sh -c sleep 300]

docker rm -f c-exec c-shell 2>/dev/null
docker run -d --name c-exec  demo-execform
docker run -d --name c-shell demo-shellform
sleep 2
docker exec c-exec  ps -o pid,args
docker exec c-shell ps -o pid,args
```

> 📝 **คำอธิบาย:** metadata ต่างกันชัดเจนตั้งแต่ตอน build — shell form ถูก Docker **ห่อด้วย `/bin/sh -c` ให้อัตโนมัติ** ·
> `docker rm -f ... 2>/dev/null` บรรทัดแรกกันไว้ก่อน เผื่อรันบล็อกนี้ซ้ำแล้วชนกับชื่อเดิม (`Conflict. The container name "/c-exec" is already in use`) ·
> `-d` รันเบื้องหลัง (ทั้งคู่จะนอน `sleep` อยู่ 300 วินาที) · `docker exec <container> ps -o pid,args` สั่ง `ps` **ข้างใน** container
> โดยขอแค่สองคอลัมน์คือ PID กับคำสั่งเต็ม · **สิ่งที่ต้องดูคือแถว PID 1** เพราะ process ตัวนั้นคือ "หัวใจ" ของ container —
> Docker ส่งสัญญาณให้มันโดยตรง และ container จะดับทันทีที่มันจบ

✅ **Expected output** — **เซอร์ไพรส์ : `ps` เหมือนกันทั้งสองตัว!** ไม่มี `/bin/sh -c` โผล่เลย (เลข PID ของ `ps` เองจะไม่ตรงกับเอกสารนี้):

```
$ docker exec c-exec ps -o pid,args        $ docker exec c-shell ps -o pid,args
PID   COMMAND                              PID   COMMAND
    1 sleep 300                                1 sleep 300
    7 ps -o pid,args                           7 ps -o pid,args
```

> 📝 **ทำไมถึงเป็นแบบนี้:** `/bin/sh` ของ Alpine คือ **BusyBox `ash`** ซึ่งมี optimization ว่า ถ้าคำสั่งใน `-c` เป็น **คำสั่งเดี่ยว ๆ ตัวสุดท้าย**
> มันจะ `exec` แทนที่ตัวเองด้วยโปรแกรมนั้นเลย แทนที่จะ fork ลูกแล้วนั่งรอ → shell จึง "หายตัว" ไป และ `sleep` ได้เป็น PID 1
> **นี่ไม่ได้แปลว่า shell form ปลอดภัย** — พอคำสั่งมีมากกว่าหนึ่งท่อน (`&&`, `|`, `;`, ตัวแปร) shell **ต้องอยู่ต่อ** และปัญหาจริงจะโผล่ทันที (ดูข้อ 8)

วัดเวลา `docker stop` ของทั้งสองตัวก่อนไปต่อ (`date +%s%N` = เวลาเป็นนาโนวินาที หารล้านได้มิลลิวินาที) :

```bash
for c in c-exec c-shell; do
  s=$(date +%s%N); docker stop $c >/dev/null; e=$(date +%s%N)
  echo "docker stop $c  ->  $(( (e-s)/1000000 )) ms"
done
docker rm c-exec c-shell
```

> 📝 **คำอธิบาย:** `docker stop` ส่ง **SIGTERM** ให้ PID 1 ก่อน แล้วรอ **10 วินาที** (ค่าเริ่มต้น ปรับได้ด้วย `-t`) ถ้ายังไม่ดับจึงส่ง **SIGKILL** ที่ห้ามปฏิเสธ

✅ **Expected output** — **ช้าทั้งคู่ ~10 วินาที** (ตัวเลขมิลลิวินาทีของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
docker stop c-exec  ->  10362 ms
docker stop c-shell  ->  10264 ms
```

> 📝 **ทำไม exec form ก็ยังช้า:** เพราะ **PID 1 บน Linux พิเศษ** — kernel ไม่ใช้ default action ของสัญญาณกับ PID 1 ที่ไม่ได้เขียน handler ดักไว้เอง
> จึง **เพิกเฉยต่อ SIGTERM** · `sleep` ไม่ได้ดัก SIGTERM จึงนอนต่อจนโดน SIGKILL ครบ 10 วินาที · **บทเรียน :** "exec form ทำให้ `docker stop` เร็ว"
> เป็นจริงเฉพาะเมื่อ **แอปข้างในดัก SIGTERM เอง** — ซึ่งแอปจริง (nginx, postgres, gunicorn) ทำกันหมด ข้อถัดไปจะพิสูจน์ด้วยแอปแบบนั้น

---

## 8. exec form vs shell form — ใครได้รับ SIGTERM (ของแถมที่สำคัญที่สุด)

คราวนี้ใช้ **แอปที่ดัก SIGTERM จริง** เหมือนแอป production :
```sh
# app.sh
#!/bin/sh
trap 'echo "[app] ได้รับ SIGTERM แล้ว - ปิดตัวเองอย่างสุภาพ"; exit 0' TERM
echo "[app] เริ่มทำงานแล้ว PID=$$"
while true; do
    sleep 1 & wait $!
done
```

```dockerfile
# Dockerfile.sigexec            |   # Dockerfile.sigshell
FROM alpine:3.20                |   FROM alpine:3.20
COPY app.sh /app.sh             |   COPY app.sh /app.sh
CMD ["/app.sh"]                 |   CMD /app.sh && echo "app.sh จบแล้ว"
```

> 📝 **คำอธิบาย:** `trap '...' TERM` = ถ้าได้รับ SIGTERM ให้พิมพ์ข้อความแล้ว `exit 0` ทันที (graceful shutdown แบบย่อส่วน) · `$$` คือ PID ของตัวเอง — ใช้ดูว่าแอปได้เป็น PID 1 หรือไม่ ·
> `sleep 1 & wait $!` ทำให้ shell ตื่นมารับ trap ได้ทันที · ฝั่ง `sigshell` จงใจใส่ `&& echo ...` เพื่อให้ **shell ต้องอยู่ต่อ** (ไม่โดน optimization ในข้อ 7) — เหมือนที่ Dockerfile จริงชอบเขียน `CMD npm run build && npm start`

```bash
docker build -f Dockerfile.sigexec  -t demo-sigexec .
docker build -f Dockerfile.sigshell -t demo-sigshell .
docker rm -f c-sigexec c-sigshell 2>/dev/null
docker run -d --name c-sigexec  demo-sigexec
docker run -d --name c-sigshell demo-sigshell
sleep 2
docker exec c-sigexec  ps -o pid,args
docker exec c-sigshell ps -o pid,args
```

✅ **Expected output** — **คนละเรื่องเลย** : ฝั่ง exec form แอปเป็น PID 1 · ฝั่ง shell form มี `/bin/sh -c` คั่นกลางเป็น PID 1 แล้วแอปถูกผลักไปเป็นลูก:

```
$ docker exec c-sigexec ps -o pid,args     $ docker exec c-sigshell ps -o pid,args
PID   COMMAND                              PID   COMMAND
    1 {app.sh} /bin/sh /app.sh                 1 /bin/sh -c /app.sh && echo "..."
    9 sleep 1                                  8 {app.sh} /bin/sh /app.sh
                                              11 sleep 1
```

จับเวลา `docker stop` ทั้งสองตัว :

```bash
for c in c-sigexec c-sigshell; do
  s=$(date +%s%N); docker stop $c >/dev/null; e=$(date +%s%N)
  echo "docker stop $c  ->  $(( (e-s)/1000000 )) ms"
done
docker logs c-sigexec ; docker logs c-sigshell
docker inspect --format '{{.State.ExitCode}}' c-sigexec c-sigshell
```

> 📝 **คำอธิบาย:** `docker logs` อ่าน stdout ที่ container พิมพ์ไว้ (ยังอ่านได้แม้ container ดับแล้ว ตราบใดที่ยังไม่ `docker rm`) · `.State.ExitCode` คือรหัสจบของ PID 1 :
> **0 = จบเองอย่างสงบ** · **137 = 128 + 9 คือโดน SIGKILL** ซึ่งเป็นหลักฐานว่า `docker stop` ต้องใช้ไม้แข็ง

✅ **Expected output** — **ต่างกันเกือบ 40 เท่า** และ log ฝั่ง shell form **ไม่มีบรรทัด "ได้รับ SIGTERM" เลย** (ตัวเลขมิลลิวินาทีของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
docker stop c-sigexec  ->  223 ms          <-- exit code 0
docker stop c-sigshell  ->  10228 ms       <-- exit code 137 (โดน SIGKILL)

$ docker logs c-sigexec                    $ docker logs c-sigshell
[app] เริ่มทำงานแล้ว PID=1                  [app] เริ่มทำงานแล้ว PID=8
[app] ได้รับ SIGTERM แล้ว - ปิดตัวเองอย่างสุภาพ   (ไม่มีบรรทัดที่สอง — ไม่เคยได้รับ SIGTERM)
```

![แผนภาพเส้นทาง SIGTERM เมื่อแอปหรือ sh เป็น PID 1](./images/theory-shell-vs-exec-signal.svg)

> 🖼 **วิธีอ่านรูปนี้:** ตามลูกศร `docker stop` ว่า `SIGTERM` ถึง PID 1 ตัวใด ฝั่ง exec form ถึง `trap` จึงจบราว 0.3 วินาทีด้วย ExitCode 0 ส่วน shell form มี `sh` คั่น จึงรอ 10 วินาทีจนถูก `SIGKILL` และจบด้วย ExitCode 137 สังเกต `&& echo` ซึ่งบังคับ BusyBox `ash` ให้อยู่ต่อ ไม่เหมือนคำสั่งเดี่ยวในข้อ 7

```
   exec form :  CMD ["/app.sh"]
   -----------------------------------------------------------------------
     docker stop --SIGTERM--> PID 1 = /app.sh  -->  trap ทำงาน · exit 0
                                                    ==> 223 ms · code 0

   shell form :  CMD /app.sh && echo "..."
   -----------------------------------------------------------------------
     docker stop --SIGTERM--> PID 1 = /bin/sh -c ...
                                X   sh ไม่ส่งต่อให้ลูก (และเองก็เมิน)
                              PID 8 = /app.sh  -->  ไม่เคยรู้เรื่อง
                   (ครบ 10 วิ) --SIGKILL--> ตายยกกระบวน
                                                    ==> 10228 ms · code 137
```

> **บทเรียนที่ต้องจำติดตัว :** ใช้ **exec form เสมอ** สำหรับ process หลักของ container ไม่งั้นแอปจะไม่มีโอกาสปิด connection / flush ข้อมูล
> และทุก ๆ การ deploy จะเสียเวลา 10 วินาทีต่อ container ฟรี ๆ · ถ้าจำเป็นต้องใช้ shell form จริง ๆ ให้เขียน `exec` นำหน้า
> (เช่น `CMD exec /app.sh`) เพื่อให้ shell **แทนที่ตัวเอง** ด้วยแอป แอปจึงได้เป็น PID 1 · ส่วน `--init` ตอนรันช่วยแค่ **เก็บ zombie process** และทำให้ container ดับเร็วขึ้น
> (เพราะ `sh` ไม่ได้เป็น PID 1 แล้ว จึงไม่เมิน SIGTERM) แต่ **ไม่ได้ทำให้แอปลูกได้รับ SIGTERM** — trap ในแอปก็ยังไม่ทำงานอยู่ดี ทางแก้ที่ถูกต้องคือ exec form หรือ `exec` นำหน้าเท่านั้น

เก็บกวาด container ทดลอง :

```bash
docker rm c-sigexec c-sigshell
```

---

## 9. ตารางสรุป และเลือกใช้ให้ตรงงาน

| คำสั่ง | เกิดเมื่อใด | หน้าที่หลัก | เมื่อใส่ค่าหลังชื่อ image |
|---|---|---|---|
| `RUN` | ตอน **build** | ติดตั้ง/สร้างสิ่งที่จะเก็บถาวรใน image | **ไม่เกี่ยวข้อง** (ทำไปแล้วตั้งแต่ build) |
| `CMD` | ตอน **run** | คำสั่งหรือ argument เริ่มต้น | **ถูกแทนที่ทั้งชุด** |
| `ENTRYPOINT` | ตอน **run** | โปรแกรมหลักของ container | ถูก **ต่อท้ายเป็น argument** |
| `ENTRYPOINT` + `CMD` | ตอน **run** | โปรแกรมหลัก + argument เริ่มต้น | **แทน CMD แต่คง ENTRYPOINT** |

**เลือกใช้ให้ตรงงาน :** `CMD` เดี่ยว = แอปทั่วไปที่อยากให้ผู้ใช้แทนคำสั่งได้ง่าย (เปิด `sh` เข้าไปดูได้ทันที ไม่ต้องจำ `--entrypoint`) ·
`ENTRYPOINT` เดี่ยว = image ที่ทำตัวเป็นโปรแกรม CLI หนึ่งตัว (เช่น `ffmpeg` ใน container) ผู้ใช้พิมพ์แค่ option ·
`ENTRYPOINT` + `CMD` = โปรแกรมหลักตายตัวแต่มี option เริ่มต้นที่ปรับได้

รูปแบบที่เจอในแอปจริง :

```dockerfile
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "5000"]
```

- `docker run image` → `python app.py --port 5000` (ใช้ค่าเริ่มต้น)
- `docker run image --port 8000` → `python app.py --port 8000` (CMD เดิมถูกแทน ENTRYPOINT ยังอยู่)
- `docker run --entrypoint sh image` → เข้า shell ไป debug (ต้องใช้ `--entrypoint` เพราะ ENTRYPOINT ทับไม่ได้)

> Dockerfile ของ Flask ในตอนที่ 3 เลือกใช้ `CMD ["python", "app.py"]` เดี่ยว ๆ เพราะอยากให้ **แทนคำสั่งได้ง่ายตอนพัฒนา**
> ส่วน image ที่เป็นเครื่องมือสำเร็จรูปนิยม `ENTRYPOINT` + `CMD` แบบข้างบน

---

## 10. ตรวจงานอัตโนมัติด้วย `verify.sh`

```bash
bash verify.sh
```

> 📝 **คำอธิบาย:** สคริปต์ build image ทั้ง 11 ตัวเงียบ ๆ แล้วตรวจข้อสรุปของแล็บครบ 18 ข้อ ตั้งแต่ RUN/CMD/ENTRYPOINT ไปจนถึงการวัดเวลา `docker stop` จริง ·
> **ใช้เวลาราว 40–60 วินาที** เพราะมีขั้นที่ต้องรอ `docker stop` แบบ shell form จนครบ 10 วินาที (บวกเวลารอ container สตาร์ตอีกไม่กี่วินาที) · ลบเฉพาะ container ทดสอบที่มันสร้างเอง (`v-*`) ไม่แตะของผู้เรียน

✅ **Expected output** — ต้องขึ้น `[PASS]` ครบทุกข้อ และปิดท้าย `ALL CHECKS PASSED` (ตัวเลขมิลลิวินาทีในข้อ 13 ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
[PASS] 1. RUN สร้าง /message.txt ไว้ตอน build และ CMD อ่านออกมาได้
        ... (ตัดท่อนกลาง — ข้อ 2 ถึง 12) ...
[PASS] 13. docker stop: exec form 269 ms (<3s) · shell form 10246 ms (รอ SIGKILL ครบ 10s)
[PASS] 14. exec form เท่านั้นที่แอปได้รับ SIGTERM (shell form ไม่ส่งต่อให้ลูก)
        ... (ตัดท่อนกลาง — ข้อ 15 ถึง 18 : busybox exec optimization · CMD ที่สืบทอดมา · no command specified · ping -c abc) ...

ALL CHECKS PASSED
```

---

## ทดลองเพิ่มเติม (~10 นาที)

> แกนหลักของแล็บจบแล้ว — หัวข้อต่อจากนี้เลือกทำตามเวลาที่มี แต่ข้อ 💥 **ทำให้พัง** อยู่ในเช็กลิสต์ท้ายแล็บ เพราะการอ่าน error ให้ออกคือทักษะที่ใช้จริงมากที่สุด

### 1. ทำไม image ที่มี ENTRYPOINT ถึง debug ยากกว่า

ท่ามาตรฐานเวลาอยากส่องข้างใน container คือต่อท้ายด้วย `sh` — ลองกับ image ที่มี ENTRYPOINT ดู :
```bash
docker run --rm demo-entrypoint sh                                        # ไม่ได้ shell
docker run --rm --entrypoint sh demo-entrypoint -c "echo ได้ shell แล้ว; id -u"   # วิธีแก้
```

> 📝 **คำอธิบาย:** บรรทัดแรกเราคาดว่าจะได้ shell แต่ `sh` ไม่ได้ไปแทนโปรแกรมหลัก มันแค่กลายเป็น **argument ตัวหนึ่งของ `echo`** — คำสั่งจริงคือ
> `echo "ข้อความจาก ENTRYPOINT:" "sh"` (ใส่ `-it` ด้วยก็ได้ผลเหมือนเดิม ปัญหาไม่ได้อยู่ที่ terminal) · บรรทัดสองใช้ `--entrypoint sh` ทับโปรแกรมหลัก แล้วส่ง `-c "..."` เป็น argument ของ `sh`

✅ **Expected output** — บรรทัดแรกได้แค่คำว่า `sh` ถูกพิมพ์ออกมาแล้วจบ · บรรทัดสองได้ shell จริง (`id -u` = 0 คือ root):

```
ข้อความจาก ENTRYPOINT: sh
ได้ shell แล้ว
0
```

เทียบกับ image ที่ใช้ `CMD` เดี่ยว ซึ่งไม่ต้องใช้ option พิเศษเลย : `docker run --rm demo-cmd sh -c "echo demo-cmd เข้า shell ได้ทันที"` → ได้ `demo-cmd เข้า shell ได้ทันที`

> **นี่คือคำตอบของ "คำถามก่อนเริ่ม" ข้อแรก** — เปลี่ยน `CMD ["python","app.py"]` เป็น `ENTRYPOINT ["python","app.py"]` แล้วสั่ง `docker run -it image sh`
> จะไม่ได้ shell แต่จะได้ `python app.py sh` — คือ `app.py` ตัวเดิมถูกรันตามปกติ โดยมีคำว่า `sh` ไหลไปเป็น argument ตัวหนึ่งใน `sys.argv` (แอปส่วนใหญ่จะเมินทิ้งหรือฟ้องว่า argument ไม่ถูกต้อง) ·
> ตอน dev จึงสะดวกกว่าถ้าใช้ `CMD` แต่ production ที่อยากล็อกโปรแกรมหลักไว้ `ENTRYPOINT` ปลอดภัยกว่า

### 2. 💥 ทำให้พัง — Dockerfile ที่ไม่มี `CMD` และไม่มี `ENTRYPOINT` เลย

**ทายก่อนรัน :** image ที่ไม่ได้บอกว่าจะรันอะไร ควรจะ error ตั้งแต่ `docker run` ใช่ไหม?
`Dockerfile.nocmd` มีแค่ `FROM alpine:3.20` + `RUN echo "no default command" > /note.txt` — ไม่มี `CMD` ไม่มี `ENTRYPOINT` สักบรรทัด

```bash
docker build -f Dockerfile.nocmd -t demo-nocmd .
docker image inspect --format '{{.Config.Entrypoint}} | {{.Config.Cmd}}' demo-nocmd
docker run --rm demo-nocmd
echo "exit code = $?"
docker image inspect --format '{{.Config.Cmd}}' alpine:3.20
```

> 📝 **คำอธิบาย:** `echo "exit code = $?"` พิมพ์รหัสจบของคำสั่งก่อนหน้า — เครื่องมือชิ้นสำคัญเวลาสิ่งที่พังไม่พิมพ์ error ให้เห็น · บรรทัดสุดท้ายเปิดดู metadata ของ **base image** เพื่อหาคำตอบว่าค่ามันโผล่มาจากไหน

✅ **Expected output** — **ไม่พัง!** และ `Cmd` ดันมีค่า `[/bin/sh]` ทั้งที่ Dockerfile ไม่ได้เขียนไว้:

```
[] | [/bin/sh]          <-- ของ demo-nocmd
exit code = 0           <-- docker run ไม่ error เลย
[/bin/sh]               <-- ของ alpine:3.20 : ต้นตออยู่ตรงนี้
```

> 📝 **เฉลย:** `CMD`/`ENTRYPOINT` เป็น metadata ที่ **สืบทอดจาก base image** — `alpine:3.20` ตั้ง `CMD ["/bin/sh"]` มาให้แล้ว พอ `docker run`
> โดยไม่มี terminal (`-it`) `sh` ก็อ่าน stdin ที่ว่างเปล่าแล้วจบทันทีด้วย exit code 0 · **บทเรียน :** อย่าเชื่อสายตาว่า Dockerfile เขียนอะไรไว้ — ให้เชื่อ `docker image inspect`

ทีนี้ล้างค่าที่สืบทอดมาให้ว่างจริง ๆ ด้วย `Dockerfile.nocmd_reset` (เหมือนเดิมแต่เติม `ENTRYPOINT []` และ `CMD []` ท้ายไฟล์) :

```bash
docker build -f Dockerfile.nocmd_reset -t demo-nocmd-reset .
docker image inspect --format '{{.Config.Entrypoint}} | {{.Config.Cmd}}' demo-nocmd-reset
docker run --rm demo-nocmd-reset ; echo "exit code = $?"
```

> 📝 **คำอธิบาย:** `ENTRYPOINT []` และ `CMD []` (array ว่าง) เป็นวิธีมาตรฐานในการ **ล้างค่าที่สืบทอดมา** — ใช้จริงเวลาสร้าง base image ให้ทีมอื่นต่อยอด แล้วอยากบังคับว่าห้ามรันโดยไม่ระบุคำสั่ง

✅ **Expected output** — คราวนี้ **พังจริง** ตั้งแต่ยังไม่ทันสร้าง container (สังเกต exit code `125` = Docker daemon ปฏิเสธคำสั่ง ไม่ใช่แอปข้างในพัง):

```
[] | []
docker: Error response from daemon: no command specified

Run 'docker run --help' for more information
exit code = 125
```

### 3. 💥 ทำให้พัง — ส่ง argument ผิดให้ `ENTRYPOINT`

`demo-both` ล็อกโปรแกรมหลักไว้เป็น `ping` แล้วให้ผู้ใช้ใส่ argument เอง — ถ้าใส่มั่วจะเป็นอย่างไร?
```bash
docker run --rm demo-both -c abc                    ; echo "exit code = $?"
docker run --rm demo-both -c 1 no-such-host.invalid ; echo "exit code = $?"
```

> 📝 **คำอธิบาย:** `-c abc` ผิดเพราะ `-c` ต้องการ **จำนวนครั้ง** เป็นตัวเลข · กรณีที่สองใส่ชื่อโฮสต์ที่ไม่มีจริง · **จุดที่ต้องอ่านให้เป็น** : error ขึ้นต้นด้วย
> `ping:` ไม่ใช่ `docker:` แปลว่า container **เริ่มได้สำเร็จ** แล้วโปรแกรมข้างในเป็นฝ่ายบ่นเอง คนละเรื่องกับข้อ 2 ที่ container ไม่ได้เกิดด้วยซ้ำ

✅ **Expected output** — error มาจาก `ping` โดยตรง และ exit code เป็น `1` (ไม่ใช่ 125):

```
ping: invalid number 'abc'
exit code = 1
ping: bad address 'no-such-host.invalid'
exit code = 1
```

> **สรุปวิธีอ่าน error 3 ระดับ :** `docker: Error response from daemon: ...` = daemon ปฏิเสธ (exit 125) · `docker: ... executable file not found` = หาโปรแกรมไม่เจอ (exit 127) · `<ชื่อโปรแกรม>: ...` = แอปข้างในบ่นเอง

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ERROR: failed to build: failed to solve: failed to read dockerfile: open Dockerfile: no such file or directory` | ลืมใส่ `-f` ทั้งที่โฟลเดอร์นี้ไม่มีไฟล์ชื่อ `Dockerfile` เฉย ๆ | ใส่ `-f <ชื่อไฟล์>` ทุกครั้ง เช่น `docker build -f Dockerfile.cmd -t demo-cmd .` |
| `docker run image sh` แล้วไม่ได้ shell แต่ได้คำว่า `sh` ถูกพิมพ์ออกมา | image นั้นมี `ENTRYPOINT` — ค่าหลังชื่อ image กลายเป็น argument ไม่ได้แทนโปรแกรม | ใช้ `docker run -it --entrypoint sh <image>` (เขียน `--entrypoint` **ก่อน** ชื่อ image เสมอ) |
| แก้ `CMD` ใน Dockerfile แล้ว แต่รันได้ผลเดิม | ยังไม่ได้ build ใหม่ หรือ build คนละไฟล์กับที่แก้ (`-f` ชี้ผิดตัว) | build ใหม่ แล้วยืนยันด้วย `docker image inspect --format '{{.Config.Cmd}}' <image>` ว่าค่าเปลี่ยนจริง |
| เขียน `CMD` ไว้สองที่ แล้วตัวแรกไม่ทำงาน ไม่มี warning ใด ๆ | `CMD`/`ENTRYPOINT` เขียนทับกัน **มีผลแค่บรรทัดสุดท้าย** (ไม่สะสมแบบ `RUN`) | เหลือ `CMD` ไว้ตัวเดียวท้ายไฟล์ · ตรวจด้วย `docker image inspect` ไม่ใช่ไล่อ่าน Dockerfile |
| `docker stop` ช้า 10 วินาทีทุกครั้ง และ exit code เป็น `137` | PID 1 ไม่ได้รับ/ไม่ได้ดัก SIGTERM (ใช้ shell form หรือแอปไม่มี signal handler) จึงต้องรอ SIGKILL | เปลี่ยนเป็น **exec form** `CMD ["app"]` · เลี่ยง shell form ไม่ได้ให้ใส่ `exec` นำหน้า (`CMD exec /app.sh`) — `--init` ช่วยให้ดับเร็วขึ้นแต่แอปลูกก็ยังไม่ได้รับ SIGTERM |
| `docker: Error response from daemon: no command specified` | image ไม่มีทั้ง `CMD` และ `ENTRYPOINT` (โดนล้างด้วย `[]` หรือมาจาก `FROM scratch`) | ใส่ `CMD`/`ENTRYPOINT` ใน Dockerfile หรือระบุคำสั่งต่อท้ายตอนรัน เช่น `docker run <image> sh` |
| `docker: Error response from daemon: ... exec: "app.sh": executable file not found in $PATH` (exit `127`) | เรียกไฟล์โดยไม่ใส่ path เต็ม (`CMD ["app.sh"]`) หรือลืม `chmod +x` | ใช้ path เต็ม `CMD ["/app.sh"]` และ `RUN chmod +x /app.sh` หลัง `COPY` (หรือ `COPY --chmod=755`) |
| เขียน `CMD ['echo', 'hello']` แล้วรันได้ `/bin/sh: [echo,: not found` | exec form เป็น **JSON array** ต้องใช้ **double quote** เท่านั้น · ใช้ single quote จะถูกตีเป็น **shell form** (ตรวจได้จาก `.Config.Cmd` = `[/bin/sh -c ['echo', 'hello']]`) | เขียนเป็น `CMD ["echo", "hello"]` |

> ข้อความ error ในตารางมาจากการทำผิดจริงบนเครื่องเรียน (บรรทัดยาวตัดให้สั้นด้วย `...`)

---

## เก็บกวาด (Cleanup)

ลบของที่สร้างในแล็บนี้ก่อน (ทำ **ข้างในเครื่องเรียน**) :
```bash
docker rm -f c-exec c-shell c-sigexec c-sigshell 2>/dev/null
docker rmi demo-run demo-cmd demo-entrypoint demo-both demo-multicmd \
           demo-execform demo-shellform demo-sigexec demo-sigshell \
           demo-nocmd demo-nocmd-reset
docker images --filter "reference=demo-*"
```

> 📝 **คำอธิบาย:** `docker rm -f` ลบ container ทดลองที่อาจค้างอยู่ (`-f` เพราะบางตัวอาจยังรัน) · `docker rmi` ลบ image ของแล็บทั้ง 11 ตัว · **image `alpine:3.20`
> เก็บไว้ได้** ไม่ต้องลบ — LAB ถัดไปใช้ต่อ ไม่ต้อง pull ใหม่ · `docker images --filter "reference=demo-*"` ตรวจซ้ำว่าเหลือแค่หัวตาราง

จากนั้นออกจาก ssh (`exit`) แล้วลบเครื่องเรียนบนเครื่องเราเอง :

```bash
docker rm -f devtools-df-lab3
docker ps -a --filter "name=^devtools-"
```

✅ **Expected output** — ได้ชื่อ `devtools-df-lab3` คืนมา แล้วตารางเหลือแต่หัว (`CONTAINER ID   IMAGE   COMMAND ...`) ไม่มีแถวข้อมูล

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker build -f Dockerfile.cmd -t demo-cmd .` | build โดยเลือกไฟล์ Dockerfile ด้วย `-f` (จำเป็นเมื่อมีหลายไฟล์ในโฟลเดอร์เดียว) |
| `docker run --rm <image>` | รันแล้วลบ container ทิ้งทันทีที่จบ — ใช้ `CMD`/`ENTRYPOINT` ที่ image กำหนดไว้ |
| `docker run --rm <image> <คำสั่ง>` | ค่าหลังชื่อ image : **แทน `CMD`** หรือ **ต่อท้าย `ENTRYPOINT`** แล้วแต่ image |
| `docker run --rm --entrypoint sh <image> -c "..."` | เปลี่ยนโปรแกรมหลัก — ทางเดียวที่จะทับ `ENTRYPOINT` ได้ |
| `docker image inspect --format '{{.Config.Entrypoint}} \| {{.Config.Cmd}}' <image>` | อ่าน metadata สองช่องที่ตัดสินพฤติกรรมทั้งหมดของแล็บนี้ |
| `docker exec <container> ps -o pid,args` | ดูว่า process ไหนได้เป็น **PID 1** ข้างใน container |
| `docker logs <container>` | อ่าน stdout ย้อนหลัง — ใช้ดูว่าแอปได้รับ SIGTERM หรือไม่ |
| `docker inspect --format '{{.State.ExitCode}}' <container>` | รหัสจบของ PID 1 : `0` = จบเอง · `137` = โดน SIGKILL |
| `docker stop -t <วินาที> <container>` · `docker rmi <image>...` | ปรับเวลารอ SIGTERM ก่อน SIGKILL (เริ่มต้น 10 วินาที) · ลบ image ของแล็บ |

> **RUN = ตอน build · CMD/ENTRYPOINT = metadata ที่มีผลตอน run · CMD ถูกทับ · ENTRYPOINT ถูกต่อท้าย · exec form ให้แอปเป็น PID 1 และปิดตัวเองได้ทัน**

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `docker run --rm demo-run curl --version` ใช้ได้ และอธิบายได้ว่าทำไม `curl` ยังอยู่ทั้งที่ `CMD` ถูกแทนที่
- [ ] `docker run --rm demo-cmd echo "..."` แล้ว **ไม่เห็น** ข้อความเดิมของ `CMD` · `docker run --rm demo-entrypoint สวัสดี Docker` แล้ว **เห็นทั้งสองส่วน**
- [ ] อธิบายได้ว่าทำไมต้องใช้ `--entrypoint` และเขียนไว้ตำแหน่งไหนของคำสั่ง
- [ ] `docker run --rm demo-both -c 1 localhost` ได้ `1 packets transmitted` โดยไม่ต้องพิมพ์คำว่า `ping`
- [ ] `docker image inspect` เห็นว่า `demo-cmd` กับ `demo-entrypoint` เก็บข้อความไว้ **คนละช่อง** · `demo-multicmd` เหลือแค่ `CMD` บรรทัดสุดท้าย
- [ ] `ps -o pid,args` ของ `c-sigexec` เห็น `app.sh` เป็น **PID 1** ส่วน `c-sigshell` เห็น `/bin/sh -c` เป็น PID 1
- [ ] วัดเวลา `docker stop` ได้จริง : exec form หลักร้อย ms · shell form ~10,000 ms และอธิบาย exit code `137` ได้
- [ ] อธิบายได้ว่าทำไม `CMD sleep 300` บน Alpine ถึงยังได้ PID 1 เป็น `sleep` (BusyBox `ash` exec optimization)
- [ ] ทำให้พังครบ : `demo-nocmd` **ไม่พัง** เพราะสืบทอด `CMD [/bin/sh]` · `demo-nocmd-reset` พังด้วย `no command specified` (exit 125) · `demo-both -c abc` พังที่ `ping` เอง (exit 1)
- [ ] `bash verify.sh` ขึ้น `ALL CHECKS PASSED`
- [ ] เก็บกวาดครบ : `docker images --filter "reference=demo-*"` เหลือแค่หัวตาราง และ `docker ps -a --filter "name=^devtools-"` ไม่มี `devtools-df-lab3` แล้ว

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` เมื่อ 14 ส.ค. 2026*
