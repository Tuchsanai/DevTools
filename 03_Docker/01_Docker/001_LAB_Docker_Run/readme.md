# LAB 1 — Docker Run พื้นฐาน

> โฟลเดอร์ `001_LAB_Docker_Run` = **LAB 1** ในสไลด์ `Docker_Week08_Slides.html`
> (แล็บนี้เป็นคำสั่งล้วน ไม่มีไฟล์โค้ด)

## สิ่งที่จะได้เรียนรู้

- `docker run` : ถ้าไม่มี image ในเครื่อง Docker จะ **pull ให้อัตโนมัติ** แล้วค่อยรัน
- อ่านผลลัพธ์ให้เป็น — image ถูกดึงมาเป็น **layer** และมี **digest** เป็นลายนิ้วมือ
- **วงจรชีวิตของ container** : run → stop → start → rm และกฎ **stop ≠ rm**
- `docker ps` vs `docker ps -a` · exit code `(0)` · ชื่อสุ่มที่ Docker ตั้งให้
- ต่อท้ายคำสั่งให้ container ทำ : `echo` · `sleep 5` · `sh -c "..."`
- `docker pull` vs `docker run` และการอ่านตาราง `docker images`

---

## 0. เตรียมเครื่องเรียน

ทำบนเครื่องของเราเอง (ไม่ใช้ cloud) — เปิด container ที่ติดตั้ง Docker มาให้แล้ว

```bash
docker rm -f devtools
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> ใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บทั้งหมดข้างใน

ตรวจว่าพร้อมใช้งาน :

```bash
docker --version
docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

ถ้าทั้งสองคำสั่งขึ้นเลขเวอร์ชัน = **พร้อมทำแล็บ** ไม่ต้องติดตั้งอะไรเพิ่ม

> **สังเกต :** เป็น `docker compose` (เว้นวรรค) ไม่ใช่ `docker-compose` (ขีดกลาง) — แบบขีดกลางคือรุ่นเก่าที่เลิกใช้แล้ว

---

## 1. `docker run nginx` — สร้างและเริ่ม container

```bash
docker run nginx
```

ครั้งแรกยังไม่มี image ในเครื่อง Docker จึง **pull ให้อัตโนมัติ** แล้วค่อยรัน :

```
Unable to find image 'nginx:latest' locally
latest: Pulling from library/nginx
5a4222b844e8: Pulling fs layer
f5de6e85ac74: Pulling fs layer
        ... (รวม 7 layer) ...
26c307b5e35a: Pull complete
d84ae7b21412: Pull complete
5a4222b844e8: Pull complete
Digest: sha256:8541484afbc9c8a5a8a99b379568ebbc957f658583ec9448fc43104229c03cf8
Status: Downloaded newer image for nginx:latest
/docker-entrypoint.sh: /docker-entrypoint.d/ is not empty, will attempt to perform configuration
/docker-entrypoint.sh: Looking for shell scripts in /docker-entrypoint.d/
/docker-entrypoint.sh: Launching /docker-entrypoint.d/10-listen-on-ipv6-by-default.sh
10-listen-on-ipv6-by-default.sh: info: Getting the checksum of /etc/nginx/conf.d/default.conf
10-listen-on-ipv6-by-default.sh: info: Enabled listen on IPv6 in /etc/nginx/conf.d/default.conf
/docker-entrypoint.sh: Sourcing /docker-entrypoint.d/15-local-resolvers.envsh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/20-envsubst-on-templates.sh
/docker-entrypoint.sh: Launching /docker-entrypoint.d/30-tune-worker-processes.sh
/docker-entrypoint.sh: Configuration complete; ready for start up
2026/08/10 16:15:56 [notice] 1#1: using the "epoll" event method
2026/08/10 16:15:56 [notice] 1#1: nginx/1.31.3
2026/08/10 16:15:56 [notice] 1#1: built by gcc 14.2.0 (Debian 14.2.0-19)
2026/08/10 16:15:56 [notice] 1#1: OS: Linux 6.6.87.2-microsoft-standard-WSL2
2026/08/10 16:15:56 [notice] 1#1: getrlimit(RLIMIT_NOFILE): 1048576:1048576
2026/08/10 16:15:56 [notice] 1#1: start worker processes
2026/08/10 16:15:56 [notice] 1#1: start worker process 29
2026/08/10 16:15:56 [notice] 1#1: start worker process 30
        ... (รวม 32 worker) ...
        ^ ค้างอยู่ตรงนี้ — container ยังทำงาน กด Ctrl+C เพื่อหยุด
```

พอกด **Ctrl+C** nginx จะรับสัญญาณ SIGINT แล้วปิดตัวเองอย่างเรียบร้อย :

```
^C2026/08/10 16:16:29 [notice] 1#1: signal 2 (SIGINT) received, exiting
2026/08/10 16:16:29 [notice] 30#30: exiting
2026/08/10 16:16:29 [notice] 31#31: exiting
        ... (worker ทุกตัวทยอย exiting / exit) ...
2026/08/10 16:16:29 [notice] 1#1: worker process 60 exited with code 0
2026/08/10 16:16:29 [notice] 1#1: exit
```

> ถ้า **ไม่มี image ในเครื่อง** Docker จะ **pull ให้อัตโนมัติ** จาก registry แล้วค่อยรัน — ไม่ต้องสั่ง pull เองก่อน

> **ระวัง :** รันแบบนี้เป็น **foreground** — terminal จะค้างและพ่น log ออกมาเรื่อย ๆ ถ้าอยากได้ prompt คืน ให้เติม `-d` (จะได้ลองในข้อถัดไป)

### อ่านผลลัพธ์ให้เป็น

| สิ่งที่เห็น | ความหมาย |
|---|---|
| `5a4222b844e8`, `f5de6e85ac74`, … | **layer** ย่อยของ image (nginx มี 7 layer) |
| `Pull complete` | layer นั้นถูกโหลดใหม่ |
| `Already exists` | layer นั้นมีอยู่แล้ว ไม่ต้องโหลดซ้ำ |
| `Digest: sha256:8541484afbc9...` | **ลายนิ้วมือ** ของ image เวอร์ชันนั้นเป๊ะ ๆ ใช้ยืนยันว่าที่โหลดมาคือของชิ้นเดียวกับต้นทางจริง ไม่ถูกแก้ระหว่างทาง |

> **ประโยชน์ของ layer :** หลาย image ที่สร้างจากฐานเดียวกันจะ **ใช้ layer ร่วมกัน** — ประหยัดพื้นที่ดิสก์และเวลาดาวน์โหลดมาก

> **ตัวเลข digest ของแต่ละคนอาจไม่ตรงกับเอกสารนี้** เพราะ `nginx:latest` ถูกอัปเดตอยู่เรื่อย ๆ — ค่าที่เห็นคือของวันที่รันจริง

กด Ctrl+C แล้ว container แค่ **หยุด** ยังไม่หายไปไหน — ลบทิ้งก่อนไปข้อถัดไป :

```bash
docker rm -f $(docker ps -aq)
```

```
8c6b91861917
```

---

## 2. วงจรชีวิตของ Container — ลองสั่งจริงทีละขั้น

stop → start → rm ดูค่า **STATUS** เปลี่ยนไปทีละขั้น

เริ่มจากรันเบื้องหลัง (`-d`) พร้อมตั้งชื่อว่า `c1` :

```bash
docker run -d --name c1 nginx
```

```
c34b83fe3a48fd7c0d9cad8917f31bbb6c7b30354748cdcb175ca4d38a3b78b2
```

คราวนี้ได้ prompt คืนทันที — Docker พิมพ์ container ID ยาว ๆ ให้แล้วรันต่อเบื้องหลัง

```bash
docker ps
```

```
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS         PORTS     NAMES
c34b83fe3a48   nginx     "/docker-entrypoint.…"   10 seconds ago   Up 9 seconds   80/tcp    c1
```

**หยุด** container :

```bash
docker stop c1
docker ps -a
```

```
c1
```

```
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS                     PORTS     NAMES
c34b83fe3a48   nginx     "/docker-entrypoint.…"   16 seconds ago   Exited (0) 2 seconds ago             c1
```

หยุดแล้ว แต่ **ยังอยู่** — STATUS เปลี่ยนเป็น `Exited (0)`

**เริ่มต่อ** จากตัวเดิมได้ :

```bash
docker start c1
docker ps
```

```
c1
```

```
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS         PORTS     NAMES
c34b83fe3a48   nginx     "/docker-entrypoint.…"   22 seconds ago   Up 2 seconds   80/tcp    c1
```

สังเกตว่าเป็น **container ID เดิม** (`c34b83fe3a48`) — กลับมาทำงานต่อได้ ไม่ได้สร้างใหม่

**ลบทิ้ง** ถาวร :

```bash
docker rm -f c1
docker ps -a
```

```
c1
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

เหลือแค่หัวตาราง — ถูกลบออกจริง

> **stop ≠ rm** — `stop` แค่หยุด container ยังอยู่และ `start` กลับมาได้ ส่วน `rm` คือลบทิ้งถาวร

> `docker ps` เห็นเฉพาะตัวที่ **กำลังทำงาน** — พอ `stop` แล้วต้องใช้ `docker ps -a` ถึงจะเห็น

---

## 3. `docker ps` vs `docker ps -a`

ลองรัน `ubuntu` ดูบ้าง — ubuntu ไม่มีคำสั่งค้างไว้ จึงจบทันที :

```bash
docker run ubuntu
```

```
Unable to find image 'ubuntu:latest' locally
latest: Pulling from library/ubuntu
a7fb98a8eddd: Pulling fs layer
617772c7d19b: Pulling fs layer
a7fb98a8eddd: Download complete
cc2ffdbc1bf7: Download complete
617772c7d19b: Download complete
a7fb98a8eddd: Pull complete
617772c7d19b: Pull complete
Digest: sha256:678c6550cc43645e08669028bc177f50be4e7c5b8cca677067b1914d4afc7a03
Status: Downloaded newer image for ubuntu:latest
```

```bash
docker ps             # แสดงเฉพาะที่ "กำลังทำงาน" → เหลือแค่หัวตาราง
```

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

```bash
docker ps -a          # แสดงทั้งหมด รวมที่หยุดไปแล้ว
```

```
CONTAINER ID   IMAGE     COMMAND       CREATED         STATUS                     PORTS     NAMES
19ebcf0dcac8   ubuntu    "/bin/bash"   8 seconds ago   Exited (0) 7 seconds ago             jovial_shamir
```

> **บทเรียนสำคัญ :** container มีชีวิตอยู่ตราบเท่าที่ **process หลักในนั้นยังทำงาน** — พอ `/bin/bash` จบ container ก็ `Exited (0)` ทันที ไม่ใช่ว่ามัน "พัง" แต่มัน "ทำงานเสร็จแล้ว"

> เลข `(0)` คือ exit code — **0 = จบปกติ** · ชื่อ `jovial_shamir` คือชื่อสุ่มที่ Docker ตั้งให้ เพราะเราไม่ได้ใส่ `--name`

---

## 4. ต่อท้ายคำสั่ง (Append a command)

รูปแบบ : `docker run <image> <command>` — คำสั่งที่ต่อท้ายจะไป **แทนที่คำสั่งเริ่มต้น** ของ image นั้น

### 4.1 `echo`

```bash
docker run busybox echo hi there
```

```
Unable to find image 'busybox:latest' locally
latest: Pulling from library/busybox
b05093807bb0: Pulling fs layer
b05093807bb0: Download complete
b05093807bb0: Pull complete
7270b3e1860c: Download complete
Digest: sha256:dc2d74b28e4cf8984fa52af1f39bc7c3d9c73760b41a74d629f5d11b1ab28616
Status: Downloaded newer image for busybox:latest
hi there
```

บรรทัดสุดท้าย `hi there` คือผลของคำสั่ง `echo` ที่เราต่อท้าย

> **busybox** เป็น image จิ๋วมาก — วัดจริงด้วย `docker images` ได้ **2.23 MB** (เทียบกับ nginx 66 MB, ubuntu 45.3 MB) จึงนิยมใช้ทดสอบเพราะโหลดเร็ว

### 4.2 `sleep 5` — container มีชีวิตอยู่นานเท่าคำสั่ง

```bash
time docker run ubuntu sleep 5
```

```
real	0m5.520s
user	0m0.008s
sys	0m0.020s
```

ไม่มี output แต่ terminal ค้างไปประมาณ 5 วินาทีแล้วค่อยได้ prompt คืน (จับเวลาจริงได้ `0m5.520s`) — **container มีชีวิตอยู่ตอนนั้น** พอ `sleep 5` จบ container ก็จบตาม

### 4.3 หลายคำสั่งด้วย `sh -c`

```bash
docker run ubuntu sh -c "echo Hello && echo World && ls && pwd && date"
```

```
Hello
World
bin
boot
dev
etc
home
lib
lib64
media
mnt
opt
proc
root
run
sbin
srv
sys
tmp
usr
var
/
Mon Aug 10 16:17:56 UTC 2026
```

> ผลลัพธ์ของ `ls` คือ **ไฟล์ระบบของ Ubuntu ที่อยู่ในกล่อง** ไม่ใช่ของเครื่องเรา — นี่คือ **Mount Namespace** ที่แยกกันตามที่เรียนในสไลด์ช่วงต้น

> ใช้ `sh -c "..."` เมื่อต้องการรันหลายคำสั่งต่อกัน เพราะ `&&` เป็นไวยากรณ์ของ shell ไม่ใช่ของ docker

---

## 5. `docker pull` — ดาวน์โหลดอย่างเดียว

เราเคย pull `nginx` ไปแล้วตอน `docker run nginx` ในข้อ 1 — ลอง pull ซ้ำอีกครั้ง :

```bash
docker pull nginx
```

```
Using default tag: latest
latest: Pulling from library/nginx
Digest: sha256:8541484afbc9c8a5a8a99b379568ebbc957f658583ec9448fc43104229c03cf8
Status: Image is up to date for nginx:latest
docker.io/library/nginx:latest
```

`Status: Image is up to date` และ **ไม่มีบรรทัด layer เลย** — image ตรงกับต้นทางอยู่แล้ว ไม่โหลดซ้ำ

| `docker pull` | `docker run` |
|---|---|
| โหลด image มาเก็บไว้ในเครื่องเฉย ๆ **ไม่รัน** | โหลด (ถ้ายังไม่มี) **แล้วรันต่อทันที** |

> **Using default tag: latest** — ถ้าไม่ระบุ tag Docker เติม `:latest` ให้เสมอ ในงานจริงควรระบุเวอร์ชันชัดเจน เช่น `nginx:1.31`

---

## 6. `docker images` — ดูของที่มีในเครื่อง

หลังทำแล็บมาถึงตรงนี้ เครื่องเรามี image อยู่ 3 ตัว :

```bash
docker images
```

```
IMAGE            ID             DISK USAGE   CONTENT SIZE   EXTRA
busybox:latest   dc2d74b28e4c       6.81MB         2.23MB   U
nginx:latest     8541484afbc9        241MB           66MB
ubuntu:latest    678c6550cc43        160MB         45.3MB   U
```

### อ่านคอลัมน์ให้เป็น

| คอลัมน์ | ความหมาย |
|---|---|
| **CONTENT SIZE** | ขนาดที่ **ดาวน์โหลดมาจริง** (ถูกบีบอัดไว้) — nginx ทั้งตัวแค่ **66 MB** |
| **DISK USAGE** | ขนาดที่ **กินพื้นที่จริงบนดิสก์** หลังแตกไฟล์ออกมาแล้ว |
| **EXTRA = U** | **U = in Use** มี container ใช้ image นี้อยู่ (ลบ container หมดเมื่อไร ตัว U ก็หายไป) |

> **หมายเหตุ :** ตารางหน้าตาแบบนี้ (`IMAGE / ID / DISK USAGE / CONTENT SIZE / EXTRA`) เป็นรูปแบบใหม่ของ Docker รุ่นใหม่ ๆ (ในเครื่องเรียนคือ 29.6.2) — Docker รุ่นเก่าจะแสดงคอลัมน์ `REPOSITORY / TAG / IMAGE ID / CREATED / SIZE` แทน ข้อมูลเดียวกัน แค่จัดหน้าคนละแบบ

> **เทียบกับ VM :** Ubuntu Server เต็มตัวเป็น image ขนาดหลาย **GB** แต่ `ubuntu` ใน Docker แค่ **45.3 MB** — เพราะไม่มี kernel และ service ของ OS ติดมาด้วย

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker run nginx` | โหลด image ให้ถ้ายังไม่มี แล้วรันเลย (foreground — terminal ค้าง) |
| `docker run -d --name c1 nginx` | รันเบื้องหลัง พร้อมตั้งชื่อเอง (ไม่ตั้งจะได้ชื่อสุ่ม) |
| `docker run ubuntu sleep 5` | รันพร้อมสั่งคำสั่งให้ทำ — container อยู่นานเท่าที่คำสั่งยังทำงาน |
| `docker run ubuntu sh -c "..."` | รันหลายคำสั่งต่อกันผ่าน shell |
| `docker pull nginx` | โหลดอย่างเดียว ยังไม่รัน |
| `docker ps` / `docker ps -a` | ดู container ที่กำลังทำงาน / ทั้งหมดรวมที่หยุดแล้ว |
| `docker stop` / `docker start` / `docker rm -f` | หยุด (ยังอยู่) / เริ่มต่อจากตัวเดิม / ลบทิ้งถาวร |
| `docker images` | ดู image ที่มีในเครื่อง |

> **stop ≠ rm** — หยุดแล้วกลับมาได้ · ลบแล้วหายถาวร

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` เมื่อ 10 ส.ค. 2026*
