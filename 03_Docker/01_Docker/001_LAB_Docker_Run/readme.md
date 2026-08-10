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

## ภาพรวมของแล็บนี้

1. **เปิดเครื่องเรียนแล้วเช็กว่า Docker พร้อม** — พิมพ์ `docker --version` กับ `docker compose version` ให้ขึ้นเลขเวอร์ชัน
   พิสูจน์ว่าเราสั่ง Docker จากข้างในกล่องเรียนได้จริง ก่อนจะลงมือทำอะไรต่อ
2. **รัน container ตัวแรกด้วย `docker run nginx`** — จะได้เห็นว่า Docker ไป **pull image ให้เอง** ทีละ layer
   แล้วจึงเริ่มรัน พิสูจน์ว่า "ไม่มี image ก็รันได้" และเห็นว่าโหมด foreground ทำให้ terminal ค้าง
3. **เดินครบวงจรชีวิต run → stop → start → rm กับ container ชื่อ `c1`** — ดู STATUS เปลี่ยนจาก `Up` เป็น `Exited (0)`
   แล้วกลับมา `Up` ด้วย **ID เดิม** พิสูจน์ว่า **stop ไม่เท่ากับ rm**
4. **เทียบ `docker ps` กับ `docker ps -a` ด้วย `ubuntu`** — container ที่ทำงานเสร็จแล้วหายจาก `docker ps`
   แต่ยังอยู่ใน `docker ps -a` พิสูจน์ว่า container มีชีวิตเท่าที่ **process หลัก** ยังทำงาน
5. **ต่อท้ายคำสั่งให้ container ทำ** (`echo` · `sleep 5` · `sh -c "..."`) — พิสูจน์ว่าคำสั่งที่ต่อท้าย
   **แทนที่คำสั่งเริ่มต้น** ของ image และอายุของ container ยาวเท่าคำสั่งนั้นพอดี
6. **สำรวจของที่โหลดมาแล้วด้วย `docker pull` และ `docker images`** — เห็นว่า pull ซ้ำจะไม่โหลดใหม่
   และเห็นขนาดจริงของ image ที่เล็กกว่า VM หลายเท่า

---

## 0. เตรียมเครื่องเรียน

ทำบนเครื่องของเราเอง (ไม่ใช้ cloud) — เปิด container ที่ติดตั้ง Docker มาให้แล้ว

```bash
docker rm -f devtools
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> 📝 **คำอธิบาย:** สามบรรทัดนี้คือการ "เปิดเครื่องเรียน" ให้ทุกคนได้สภาพแวดล้อมเหมือนกันเป๊ะ ก่อนเริ่มแล็บ ·
> `docker rm -f devtools` ลบกล่องเรียนตัวเก่าทิ้งก่อน (`-f` = force คือสั่งลบได้แม้ container ยังทำงานอยู่)
> จะได้ไม่ชนชื่อกับตัวใหม่ · `-dit` คือสามตัวรวมกัน `-d` รันเบื้องหลัง · `-i` เปิด stdin ค้างไว้ · `-t` ให้มี terminal
> ทำให้กล่องไม่ดับทันที · `--privileged` ให้สิทธิ์เต็มเพื่อรัน **Docker ซ้อนข้างในกล่อง** (Docker-in-Docker) ซึ่งจำเป็นกับแล็บนี้ ·
> `-p 2222:22` ส่ง port 2222 ของเครื่องเรา เข้า port 22 (SSH) ของกล่อง (เรื่อง port mapping จะลงรายละเอียดใน LAB 2)
> สิ่งที่ควรเห็น: บรรทัดแรกพิมพ์ชื่อ `devtools` กลับมา บรรทัดสองพิมพ์ container ID ยาว ๆ แล้ว `ssh` จะถาม password
> (พิมพ์ `passwd` แล้ว prompt จะเปลี่ยนเป็นของเครื่องเรียน) — ถ้ายังไม่เคยสร้าง `devtools` มาก่อน บรรทัดแรกจะไม่พิมพ์
> อะไรออกมาเลย (เพราะ `-f` ทำให้ไม่ฟ้องเมื่อไม่พบ container) ถือว่าปกติ ข้ามไปบรรทัดถัดไปได้เลย

> ใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บทั้งหมดข้างใน

ตรวจว่าพร้อมใช้งาน :

```bash
docker --version
docker compose version
```

> 📝 **คำอธิบาย:** สองคำสั่งนี้ถามเวอร์ชันของ Docker Engine และของ Compose ที่ติดตั้งมาให้แล้ว เรารันตรงนี้เพื่อ
> **ยืนยันว่าคำสั่ง `docker` วิ่งถึง daemon ได้จริง** ก่อนจะเสียเวลาไปเจอ error กลางแล็บ · สิ่งที่ต้องดูคือ
> "มีเลขเวอร์ชันขึ้นมาไหม" ไม่ใช่ "เลขตรงกับเอกสารไหม" ถ้าขึ้น `Cannot connect to the Docker daemon` แปลว่า
> ยังอยู่นอกกล่องเรียนหรือ daemon ยังไม่ขึ้น ให้ย้อนไปทำข้อ 0 ใหม่

✅ **Expected output** — ขอแค่มี **เลขเวอร์ชัน** ขึ้นครบสองบรรทัด ไม่ใช่ error (เลขเวอร์ชันของแต่ละคนอาจไม่ตรงกับเอกสารนี้ ตาม image ที่ใช้):

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

> 📝 **คำอธิบาย:** `docker run <image>` ทำงานสามอย่างในคำสั่งเดียว — หา image ในเครื่อง ถ้าไม่มีก็ **pull** มาก่อน
> จากนั้น **สร้าง container** ใหม่จาก image นั้น แล้ว **เริ่มรัน** process หลักข้างใน · เรารันตัวนี้เป็นตัวแรกเพราะมันเห็น
> ทั้งขั้นตอน pull และขั้นตอน start ในจอเดียว · ยังไม่ใส่ flag อะไรเลย จึงเป็นโหมด **foreground** คือ terminal ของเรา
> ถูกผูกกับ log ของ nginx ไว้ สิ่งที่ต้องดูคือลำดับ: `Unable to find image ... locally` มาก่อน แล้วค่อยตามด้วยบรรทัด
> layer แล้วจึงเป็น log ของ nginx — และ prompt **จะไม่คืนมา** จนกว่าจะกด Ctrl+C

ครั้งแรกยังไม่มี image ในเครื่อง Docker จึง **pull ให้อัตโนมัติ** แล้วค่อยรัน :

✅ **Expected output** — จุดที่ต้องดูคือบรรทัดแรก `Unable to find image 'nginx:latest' locally` ซึ่งแปลว่า Docker ตัดสินใจ pull เอง (ค่า layer ID · digest · เวลา · จำนวน worker ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

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

> **อ่านให้ลึกอีกนิด :** เลข `1#1` คือ **PID 1** ในกล่อง — nginx เป็น process หมายเลข 1 ของ container นี้
> (นี่คือ PID Namespace ที่แยกจากเครื่องเรา) และจำนวน worker ที่ nginx เปิด (ค่า `worker_processes auto`) จะเท่ากับจำนวน CPU core ที่กล่องมองเห็น
> ดังนั้นเครื่องแต่ละคนจะได้ไม่เท่ากัน

พอกด **Ctrl+C** nginx จะรับสัญญาณ SIGINT แล้วปิดตัวเองอย่างเรียบร้อย :

✅ **Expected output** — ให้ดูบรรทัดสุดท้าย `1#1: exit` คือ process หลักจบแล้ว = container หยุด (เลข worker และเวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

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

> 📝 **คำอธิบาย:** คำสั่งนี้ล้าง container ทุกตัวในเครื่องให้เกลี้ยง เพื่อให้ข้อถัดไปเริ่มจากหน้าจอว่าง ๆ นับผลง่าย ·
> `docker ps -aq` คือ `-a` เอาทั้งหมดรวมตัวที่หยุดแล้ว + `-q` (quiet) พิมพ์เฉพาะ ID ไม่เอาหัวตาราง ·
> `$( ... )` เป็นไวยากรณ์ของ shell ที่เอา **ผลลัพธ์** ของคำสั่งข้างในมาเป็น argument ให้ `docker rm -f` อีกที
> ระวัง: มันลบ **ทุก** container จริง ๆ ใช้ได้เพราะนี่คือเครื่องเรียนที่ไม่มีของสำคัญ

✅ **Expected output** — Docker พิมพ์ ID ของตัวที่ลบไปคืนมาบรรทัดละตัว ที่ต้องดูคือ "มีบรรทัดขึ้นมา = ลบสำเร็จ" (ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้ · ถ้าไม่มี container เหลืออยู่เลย จะขึ้นข้อความ `docker: 'docker rm' requires at least 1 argument` พร้อม usage — ไม่ใช่ error ที่ต้องแก้ แค่แปลว่าไม่มีอะไรให้ลบ):

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

> 📝 **คำอธิบาย:** รัน nginx อีกครั้ง แต่คราวนี้ใส่ flag เพิ่มสองตัว · `-d` (detached) สั่งให้ container ไปทำงานเบื้องหลัง
> แล้วคืน prompt กลับมาทันที ไม่ผูก terminal ไว้กับ log อีก · `--name c1` ตั้งชื่อเองเพื่อให้คำสั่ง stop/start/rm ต่อจากนี้
> พิมพ์สั้น ๆ ได้ ไม่ต้องคัดลอก container ID ยาว ๆ สิ่งที่ต้องดูคือ **prompt กลับมาทันที** และมี ID ยาว 64 ตัวอักษรพิมพ์ออกมา
> ครั้งนี้ไม่มีบรรทัด `Unable to find image` แล้ว เพราะ image `nginx` อยู่ในเครื่องตั้งแต่ข้อ 1

✅ **Expected output** — ได้ **container ID เต็ม 64 ตัวอักษร** กลับมาบรรทัดเดียว ไม่ใช่ log ของ nginx (ID ของแต่ละคนจะไม่ซ้ำกัน):

```
c34b83fe3a48fd7c0d9cad8917f31bbb6c7b30354748cdcb175ca4d38a3b78b2
```

คราวนี้ได้ prompt คืนทันที — Docker พิมพ์ container ID ยาว ๆ ให้แล้วรันต่อเบื้องหลัง

```bash
docker ps
```

> 📝 **คำอธิบาย:** `docker ps` แสดงเฉพาะ container ที่ **กำลังทำงานอยู่** เรารันตรงนี้เพื่อพิสูจน์ว่า `-d` ไม่ได้ทำให้
> container ตาย แค่ย้ายไปทำงานเบื้องหลัง สิ่งที่ต้องดูคือคอลัมน์ **STATUS ขึ้นต้นด้วย `Up`** และคอลัมน์ NAMES เป็น `c1`
> ตามที่เราตั้งไว้ · สังเกตด้วยว่า CONTAINER ID ในตารางคือ **12 ตัวแรก** ของ ID ยาว 64 ตัวที่เพิ่งได้มา

✅ **Expected output** — ดูคอลัมน์ STATUS ต้องเป็น `Up ...` และ NAMES เป็น `c1` (ID · เวลา `CREATED`/`STATUS` ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS         PORTS     NAMES
c34b83fe3a48   nginx     "/docker-entrypoint.…"   10 seconds ago   Up 9 seconds   80/tcp    c1
```

**หยุด** container :

```bash
docker stop c1
docker ps -a
```

> 📝 **คำอธิบาย:** `docker stop c1` ส่งสัญญาณ SIGTERM ให้ process หลักในกล่องปิดตัวเองอย่างสุภาพ (ถ้าไม่ยอมปิดใน 10 วินาที
> จึงค่อยบังคับด้วย SIGKILL) — เลยใช้เวลานิดหน่อยก่อนคืน prompt · `docker ps -a` เติม `-a` (all) เพื่อให้เห็น
> **ตัวที่หยุดไปแล้วด้วย** ถ้าใช้ `docker ps` เฉย ๆ ตอนนี้จะเหลือแค่หัวตารางจนนึกว่า container หายไปแล้ว
> สิ่งที่ต้องดูคือ STATUS เปลี่ยนจาก `Up` เป็น `Exited (0)` แต่ **แถวยังอยู่**

✅ **Expected output** — `docker stop` พิมพ์ชื่อที่หยุดสำเร็จกลับมาเฉย ๆ ให้ดูว่าได้คำว่า `c1` ตรงกับชื่อที่เราสั่ง:

```
c1
```

✅ **Expected output** — จุดสำคัญคือ STATUS กลายเป็น `Exited (0)` และคอลัมน์ PORTS ว่างลง แต่แถวของ `c1` **ยังอยู่ในตาราง** (ID · เวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

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

> 📝 **คำอธิบาย:** `docker start` **ไม่ได้สร้างของใหม่** แต่ปลุก container เดิมที่ยังนอนอยู่ในดิสก์ให้กลับมาทำงานต่อ
> จึงไม่ต้องระบุ image ไม่ต้องระบุ flag ใด ๆ ซ้ำ — ค่าที่ตั้งไว้ตอน `run` ถูกจำไว้ในตัว container แล้ว ·
> เรารัน `docker ps` (ไม่ต้องมี `-a`) ต่อทันทีเพื่อยืนยันว่ามันกลับมาอยู่ในรายชื่อ "ตัวที่ทำงานอยู่" อีกครั้ง
> สิ่งที่ต้องดูคือ **CONTAINER ID ต้องเป็นตัวเดิม** ไม่ใช่ ID ใหม่

✅ **Expected output** — ได้ชื่อ `c1` กลับมาแปลว่าสั่ง start สำเร็จ:

```
c1
```

✅ **Expected output** — ดูสองอย่าง: STATUS กลับมาเป็น `Up ...` และ CONTAINER ID ยังเป็น **ตัวเดิม** กับตอนแรก (ID · เวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
CONTAINER ID   IMAGE     COMMAND                  CREATED          STATUS         PORTS     NAMES
c34b83fe3a48   nginx     "/docker-entrypoint.…"   22 seconds ago   Up 2 seconds   80/tcp    c1
```

สังเกตว่าเป็น **container ID เดิม** (`c34b83fe3a48`) — กลับมาทำงานต่อได้ ไม่ได้สร้างใหม่

> **ทำไม ID ถึงเดิม :** `stop` แค่ดับ process ข้างใน แต่ตัว container (ทั้ง metadata และชั้น writable layer ที่เก็บไฟล์ที่เขียนไว้)
> ยังอยู่ครบ `start` จึงเป็นการเปิดสวิตช์ของกล่องใบเดิม ไม่ใช่การสร้างกล่องใบใหม่

**ลบทิ้ง** ถาวร :

```bash
docker rm -f c1
docker ps -a
```

> 📝 **คำอธิบาย:** `docker rm` ลบ container ทิ้งถาวร ปกติต้อง `stop` ก่อนถึงจะลบได้ แต่ `-f` (force) สั่งให้หยุดแล้วลบรวดเดียว
> จึงใช้ได้แม้ตอนนี้ `c1` ยัง `Up` อยู่ · เราตามด้วย `docker ps -a` (ตัวที่เห็น "ทุกอย่างรวมที่หยุดแล้ว") เพราะถ้าใช้ `docker ps`
> เฉย ๆ จะแยกไม่ออกว่ามัน "แค่หยุด" หรือ "หายไปจริง" สิ่งที่ต้องดูคือ **ตารางเหลือแต่หัวตาราง ไม่มีแถวข้อมูลเลย**
> หมายเหตุ: ลบ container ไม่ได้ลบ image — `nginx` ยังอยู่ในเครื่อง เดี๋ยวจะเห็นในข้อ 6

✅ **Expected output** — ได้ชื่อ `c1` กลับมา = ลบสำเร็จ (ถ้าพิมพ์ชื่อผิด จะไม่มีอะไรพิมพ์ออกมาเลย เพราะ `-f` ไม่ฟ้องเมื่อไม่พบ container — ถ้าสั่ง `docker rm` เฉย ๆ จึงจะเห็น `No such container`):

```
c1
```

✅ **Expected output** — จุดที่ต้องดูคือ **ไม่มีแถวข้อมูลใต้หัวตารางเลย** แม้จะใส่ `-a` แล้วก็ตาม:

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

> 📝 **คำอธิบาย:** รัน image `ubuntu` แบบไม่ต่อท้ายคำสั่งใด ๆ คำสั่งเริ่มต้นของ image นี้คือ `/bin/bash` แต่เราไม่ได้ใส่
> `-i`/`-t` ให้มัน bash จึงไม่มีอะไรให้อ่านจากแป้นพิมพ์ **จบการทำงานทันที** และ container ก็ตายตาม ·
> เรารันตรงนี้เพื่อสร้าง container ที่ "ทำงานเสร็จแล้ว" ไว้เป็นตัวอย่างเปรียบเทียบ `docker ps` กับ `docker ps -a` ในสองข้อถัดไป
> สิ่งที่ต้องดูคือ prompt คืนมาเร็วมาก และไม่มี output ของ ubuntu ตามมาเลยหลังบรรทัด `Status:`

✅ **Expected output** — ให้ดูว่ามีแต่บรรทัดของการ pull แล้วจบ **ไม่มี output อะไรตามมา** และ prompt คืนทันที (layer ID · digest ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

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

> **สังเกตสองจังหวะ :** `Download complete` คือโหลดไฟล์ layer เสร็จ ส่วน `Pull complete` คือแตกไฟล์ลงดิสก์เสร็จแล้วพร้อมใช้
> Docker โหลดหลาย layer พร้อมกันได้ ลำดับบรรทัดของแต่ละคนจึงสลับกันได้ ไม่ผิด

```bash
docker ps             # แสดงเฉพาะที่ "กำลังทำงาน" → เหลือแค่หัวตาราง
```

> 📝 **คำอธิบาย:** ถามหา container ที่กำลังทำงาน หลังจากเพิ่งรัน `ubuntu` ไป — ที่ต้องดูคือ **ไม่มีแถวใด ๆ**
> อย่าเพิ่งตกใจว่าคำสั่งที่แล้วล้มเหลว มันแค่ทำงานเสร็จไปแล้ว จุดนี้คือกับดักคลาสสิกของมือใหม่ที่คิดว่า
> "รันแล้วแต่หาไม่เจอ = พัง"

✅ **Expected output** — เหลือแต่หัวตาราง ไม่มีแถวข้อมูล เพราะไม่มี container ตัวไหน **กำลัง** ทำงาน:

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

```bash
docker ps -a          # แสดงทั้งหมด รวมที่หยุดไปแล้ว
```

> 📝 **คำอธิบาย:** คำสั่งเดิมแต่เติม `-a` (all) — คราวนี้ Docker แสดง container ทุกตัวที่ยังมีอยู่ในเครื่อง
> ไม่ว่าจะกำลังทำงานหรือจบไปแล้ว เรารันคู่กันแบบนี้เพื่อให้เห็นว่า container จาก `docker run ubuntu` **ไม่ได้หายไปไหน**
> แค่ไม่แสดงใน `docker ps` ที่ต้องดูคือคอลัมน์ STATUS ว่าเป็น `Exited (0)` และคอลัมน์ NAMES ที่เป็นชื่อสุ่ม

✅ **Expected output** — ดูคำว่า `Exited (0)` ในคอลัมน์ STATUS และชื่อสุ่มในคอลัมน์ NAMES (ID · เวลา · ชื่อสุ่มของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
CONTAINER ID   IMAGE     COMMAND       CREATED         STATUS                     PORTS     NAMES
19ebcf0dcac8   ubuntu    "/bin/bash"   8 seconds ago   Exited (0) 7 seconds ago             jovial_shamir
```

> **บทเรียนสำคัญ :** container มีชีวิตอยู่ตราบเท่าที่ **process หลักในนั้นยังทำงาน** — พอ `/bin/bash` จบ container ก็ `Exited (0)` ทันที ไม่ใช่ว่ามัน "พัง" แต่มัน "ทำงานเสร็จแล้ว"

> เลข `(0)` คือ exit code — **0 = จบปกติ** · ชื่อ `jovial_shamir` คือชื่อสุ่มที่ Docker ตั้งให้ เพราะเราไม่ได้ใส่ `--name`

> **ขยายความ exit code :** เลขในวงเล็บคือค่าที่ process หลักคืนให้ระบบตอนจบ — `0` แปลว่าสำเร็จ ส่วนเลขอื่น
> (เช่น `Exited (1)` หรือ `Exited (137)` ที่แปลว่าโดน SIGKILL) คือสัญญาณว่ามีอะไรผิด เวลา debug ให้ดูเลขนี้ก่อนเสมอ

---

## 4. ต่อท้ายคำสั่ง (Append a command)

รูปแบบ : `docker run <image> <command>` — คำสั่งที่ต่อท้ายจะไป **แทนที่คำสั่งเริ่มต้น** ของ image นั้น

### 4.1 `echo`

```bash
docker run busybox echo hi there
```

> 📝 **คำอธิบาย:** ทุกอย่างหลังชื่อ image คือ **คำสั่งที่จะให้ container รันแทนคำสั่งเริ่มต้น** ตรงนี้คือ `echo hi there` ·
> เราเลือก `busybox` เพราะเป็น image จิ๋วมาก โหลดเสร็จในไม่กี่วินาที เหมาะกับการทดลองแนวคิดนี้ ·
> สิ่งที่ต้องดูคือ **บรรทัดสุดท้าย** ที่เป็นผลของ `echo` ไม่ใช่บรรทัดของการ pull ที่อยู่ข้างบน

✅ **Expected output** — ดูบรรทัดสุดท้าย `hi there` ซึ่งมาจาก `echo` ที่เราต่อท้าย ส่วนบรรทัดข้างบนคือขั้นตอน pull ตามปกติ (layer ID · digest ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

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

> **ทำไมถึงเล็กได้ขนาดนั้น :** busybox ยัดคำสั่งพื้นฐานหลายสิบตัว (`ls` `cat` `echo` …) ไว้ใน binary เดียว
> ไม่มี package manager ไม่มี service ของ OS จึงเหลือแค่ไฟล์ที่จำเป็นจริง ๆ

### 4.2 `sleep 5` — container มีชีวิตอยู่นานเท่าคำสั่ง

```bash
time docker run ubuntu sleep 5
```

> 📝 **คำอธิบาย:** `sleep 5` สั่งให้ process หลักในกล่อง "ไม่ทำอะไรเลย 5 วินาที" แล้วจบ — เท่ากับกำหนดอายุ container
> ด้วยมือ · `time` ข้างหน้าไม่ใช่ flag ของ docker แต่เป็นคำสั่งของ shell ที่จับเวลาคำสั่งทั้งบรรทัดให้ เรารันคู่กัน
> เพื่อ **พิสูจน์ด้วยตัวเลข** ว่า container อยู่นานเท่าคำสั่งจริง ๆ ที่ต้องดูคือค่า `real` ที่ต้องมากกว่า 5 วินาทีนิดหน่อย
> (ส่วนเกินคือเวลาที่ Docker ใช้สร้างและเก็บกวาด container)

✅ **Expected output** — ดูค่า `real` ที่เกาะอยู่ราว ๆ 5 วินาที ตรงกับ `sleep 5` พอดี และไม่มี output อื่นเลย (ตัวเลขเวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้ ขึ้นกับความเร็วเครื่อง):

```
real	0m5.520s
user	0m0.008s
sys	0m0.020s
```

ไม่มี output แต่ terminal ค้างไปประมาณ 5 วินาทีแล้วค่อยได้ prompt คืน (จับเวลาจริงได้ `0m5.520s`) — **container มีชีวิตอยู่ตอนนั้น** พอ `sleep 5` จบ container ก็จบตาม

> **อ่านสามบรรทัดนี้ให้เป็น :** `real` คือเวลานาฬิกาจริงที่ผ่านไป ส่วน `user`/`sys` คือเวลา CPU ที่ถูกใช้จริง
> ซึ่งเกือบเป็นศูนย์ — เพราะ 5 วินาทีนั้น process แค่ "นอนรอ" ไม่ได้เผา CPU เลย

### 4.3 หลายคำสั่งด้วย `sh -c`

```bash
docker run ubuntu sh -c "echo Hello && echo World && ls && pwd && date"
```

> 📝 **คำอธิบาย:** `docker run` ส่งคำสั่งให้ container ตรง ๆ ไม่ได้ผ่าน shell เครื่องหมาย `&&` จึงไม่มีความหมาย
> ถ้าไม่ห่อไว้ · `sh -c "..."` คือการสั่งให้ **เปิด shell ในกล่อง** แล้วให้ shell ตัวนั้นอ่านข้อความในเครื่องหมายคำพูด
> เป็นสคริปต์ (`-c` = command string) จึงรันได้หลายคำสั่งต่อกัน · ที่ต้องดูคือผลของ `ls` และ `pwd` ว่าเป็น
> **ระบบไฟล์ของกล่อง** ไม่ใช่โฟลเดอร์ที่เรายืนอยู่บนเครื่องเรียน

✅ **Expected output** — ห้าคำสั่งทำงานเรียงกันครบ ให้สังเกตว่าผลของ `ls` คือรากของ Ubuntu (`bin` `boot` `etc` …) และ `pwd` ได้ `/` (บรรทัด `date` ของแต่ละคนจะเป็นวันเวลาที่รันจริง จึงไม่ตรงกับเอกสารนี้):

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

> **เกร็ดเสริม :** `pwd` ได้ `/` เพราะ working directory เริ่มต้นของ image `ubuntu` คือราก และ `date` ขึ้น `UTC`
> เพราะ container ไม่ได้ตั้ง timezone ไว้ — สองอย่างนี้เป็นค่าที่ **image เป็นคนกำหนด** ไม่ได้ยืมจากเครื่องเรา

---

## 5. `docker pull` — ดาวน์โหลดอย่างเดียว

เราเคย pull `nginx` ไปแล้วตอน `docker run nginx` ในข้อ 1 — ลอง pull ซ้ำอีกครั้ง :

```bash
docker pull nginx
```

> 📝 **คำอธิบาย:** `docker pull` โหลด image มาเก็บไว้เฉย ๆ **ไม่สร้างและไม่รัน container** เรารันซ้ำตรงนี้เพราะ image
> อยู่ในเครื่องแล้ว จะได้เห็นพฤติกรรม "ไม่โหลดซ้ำ" ชัด ๆ · Docker จะเทียบ **digest** ของที่มีอยู่กับของบน registry ก่อน
> ถ้าเหมือนกันก็ข้ามการดาวน์โหลดทั้งหมด สิ่งที่ต้องดูคือ **ไม่มีบรรทัด layer โผล่มาเลย** และบรรทัด Status เปลี่ยนคำ

✅ **Expected output** — จุดชี้ขาดคือคำว่า `Image is up to date` (ไม่ใช่ `Downloaded newer image`) และ **ไม่มีบรรทัด layer สักบรรทัด** (ค่า digest ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

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

> **ข้อควรระวังเรื่อง `latest` :** มันไม่ได้แปลว่า "ใหม่ล่าสุดเสมอ" แต่เป็นแค่ **ชื่อ tag ตัวหนึ่ง** ที่เจ้าของ image
> ชี้ไปที่เวอร์ชันไหนก็ได้ วันนี้กับพรุ่งนี้จึงอาจได้คนละ image — ในงานจริงการล็อกเวอร์ชันช่วยให้ทีมได้ของชิ้นเดียวกันทุกคน

---

## 6. `docker images` — ดูของที่มีในเครื่อง

หลังทำแล็บมาถึงตรงนี้ เครื่องเรามี image อยู่ 3 ตัว :

```bash
docker images
```

> 📝 **คำอธิบาย:** แสดงรายการ image ทั้งหมดที่ **ดาวน์โหลดเก็บไว้ในเครื่อง** เรารันปิดท้ายเพื่อสรุปว่าตลอดแล็บนี้เราสะสม
> อะไรไว้บ้าง และเพื่อยืนยันว่า **ลบ container ไม่ได้ลบ image** — nginx ยังอยู่ในเครื่องทั้งที่เราลบ container `c1`
> ไปแล้ว (สังเกตว่าแถว busybox กับ ubuntu ยังติด `U` เพราะ container จากข้อ 3-4 ยังค้างอยู่ ส่วน nginx ไม่มี `U`
> เพราะ container ของมันถูกลบหมดแล้ว) สิ่งที่ต้องดูคือจำนวนแถว (ควรมี 3 ตัวตามที่ pull มา) และคอลัมน์ขนาดของแต่ละตัว

✅ **Expected output** — ควรเห็น 3 แถวคือ busybox · nginx · ubuntu ตรงกับ image ที่แล็บนี้ดึงมา (ค่า ID · ขนาด · ตัวอักษรในคอลัมน์ EXTRA ของแต่ละคนอาจไม่ตรงกับเอกสารนี้ ขึ้นกับเวอร์ชัน image และ container ที่ยังเหลืออยู่):

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

> **ทำไม DISK USAGE ถึงมากกว่า CONTENT SIZE :** ของที่โหลดมาถูกบีบอัดไว้ พอแตกไฟล์ลงดิสก์เพื่อใช้งานจริงจึงพองขึ้น
> และตัวเลขนี้ยังนับ layer ที่ **ใช้ร่วมกัน** ระหว่าง image ด้วย — บวกทุกแถวแล้วจะได้มากกว่าพื้นที่ที่หายไปจริงบนดิสก์

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

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `docker --version` และ `docker compose version` ขึ้น **เลขเวอร์ชัน** ทั้งสองคำสั่ง ไม่มี error
- [ ] เห็นบรรทัด `Unable to find image 'nginx:latest' locally` ตอนรัน `docker run nginx` ครั้งแรก
- [ ] เห็นบรรทัด `Pull complete` ของ layer และบรรทัด `Digest: sha256:...` ในผลของการ pull
- [ ] terminal ค้างพ่น log ของ nginx จนต้องกด **Ctrl+C** และเห็นบรรทัดปิดท้าย `1#1: exit`
- [ ] `docker run -d --name c1 nginx` คืน **container ID ยาว ๆ** และได้ prompt กลับมาทันที
- [ ] `docker ps` แสดงแถวของ `c1` โดยคอลัมน์ STATUS ขึ้นต้นด้วย `Up`
- [ ] หลัง `docker stop c1` แล้ว `docker ps -a` แสดง STATUS เป็น `Exited (0)` แต่แถวยังอยู่
- [ ] หลัง `docker start c1` แล้ว STATUS กลับเป็น `Up` โดย **CONTAINER ID ยังเป็นตัวเดิม**
- [ ] หลัง `docker rm -f c1` แล้ว `docker ps -a` เหลือแค่หัวตาราง ไม่มีแถวข้อมูล
- [ ] `docker run ubuntu` แล้วหาไม่เจอใน `docker ps` แต่เจอใน `docker ps -a` พร้อมชื่อสุ่มและ `Exited (0)`
- [ ] `docker run busybox echo hi there` พิมพ์คำว่า `hi there` เป็นบรรทัดสุดท้าย
- [ ] `time docker run ubuntu sleep 5` ได้ค่า `real` ราว ๆ 5 วินาที
- [ ] `docker run ubuntu sh -c "..."` พิมพ์ `Hello` · `World` · รายชื่อไฟล์ราก · `/` · วันเวลา ครบทั้งห้าคำสั่ง
- [ ] `docker pull nginx` ซ้ำ ได้ `Status: Image is up to date` โดยไม่มีบรรทัด layer
- [ ] `docker images` แสดง image ครบ 3 ตัว (busybox · nginx · ubuntu)
- [ ] อธิบายได้ว่า **stop ≠ rm** ต่างกันอย่างไร และทำไม container ที่ `Exited (0)` ถึงไม่ใช่ container ที่พัง

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` เมื่อ 10 ส.ค. 2026*
