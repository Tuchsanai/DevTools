# LAB 4 — Docker Network : ภารกิจกู้ข้อความลับด้วย Embedded DNS

> โฟลเดอร์ `004_LAB_Docker_Network_DNS` = **LAB 4** ในสไลด์ `Docker_Week11_Slides.html`
> (แล็บนี้เป็นแล็บ CLI ล้วน — ไม่มีไฟล์โค้ดประกอบ เอกสารนี้คือทั้งหมดที่ต้องใช้)

## สิ่งที่จะได้เรียนรู้

- Docker แถม network มาให้ 3 วงตั้งแต่ติดตั้ง : **bridge** · **host** · **none** — แต่ละวงต่างกันอย่างไร
- บน **default bridge** container คุยกันด้วย **IP ได้** แต่เรียกกันด้วย **ชื่อไม่ได้** — และทำไมนั่นคือปัญหาใหญ่ของแอปจริง
- **user-defined network** เปิด **Embedded DNS** ให้อัตโนมัติ — container เรียกหากันด้วย **ชื่อ** ได้ทันที
- เห็น DNS server ลับของ Docker ตัวเป็น ๆ ที่ `nameserver 127.0.0.11` ใน `/etc/resolv.conf`
- `docker network connect` **เสียบ container ที่กำลังรันอยู่เข้า network ใหม่ได้สด ๆ** โดยไม่ต้อง restart — และ container มีขาได้หลายวงพร้อมกัน
- กำหนด **IP ตายตัว** ให้ container ได้เมื่อ network มี `--subnet` ของตัวเอง
- โหมดพิเศษ `--network host` (ไม่ต้อง `-p` เลย) กับ `--network none` (ตัดขาดโลก) เหมาะกับงานแบบไหน

## ภาพรวมของแล็บนี้

1. **เปิดเครื่องเรียนแล้วเช็กว่า Docker พร้อม** — ทุก container ของแล็บนี้จะรันซ้อนอยู่ข้างในกล่องเรียน
2. **สำรวจ network ที่ Docker แถมมา** — `docker network ls` แล้วเจาะดู `bridge` ว่าข้างในมี Subnet/Gateway อะไร เพื่อรู้ว่า "ค่าเริ่มต้น" ที่ทุก container ได้รับหน้าตาเป็นอย่างไร
3. **การทดลองที่ 1 : default bridge** — รัน `box1` `box2` แบบไม่ระบุ network แล้วพิสูจน์ว่า ping ด้วย **IP สำเร็จ** แต่ ping ด้วย **ชื่อล้มเหลว** — จบข้อนี้จะเกิดคำถามใหญ่: แล้วแอปจริงจะ config ยังไง ในเมื่อ IP เปลี่ยนทุกครั้งที่รันใหม่?
4. **การทดลองที่ 2 : user-defined network** — สร้าง `lab_net` เองแล้วรัน `box3` `box4` เข้าไป คราวนี้ ping ด้วย **ชื่อสำเร็จ** — แล้วเปิด `/etc/resolv.conf` เฉลยกลไกว่าใครเป็นคนแปลชื่อให้
5. **กำหนด IP เองได้เมื่อมี subnet** — รัน `box5` พร้อม `--ip 172.30.0.50` พิสูจน์ว่า network ที่เราสร้างเองควบคุมได้ละเอียดกว่า
6. **ภารกิจกู้ข้อความลับ 🕵️** — เอาทุกอย่างที่เรียนมาใช้จริง: `secret-server` ซ่อนอยู่ใน `lab_net` ส่วนสายลับ `spy` อยู่คนละวง ต้องหาทางเจาะเข้าไปอ่านข้อความลับให้ได้ **โดยไม่ restart container**
7. **โหมดพิเศษ host และ none** — สองขั้วสุดโต่งของ network: ใช้ network ของเครื่องตรง ๆ กับ ตัดขาดโลกภายนอกทั้งหมด
8. **ล้างกระดาน** — ลบ container และ network ทั้งหมดที่สร้าง ตรวจว่าเครื่องกลับมาสะอาดเหมือนก่อนเริ่ม

> **คำถามก่อนเริ่ม:** โค้ดแอปจริงเขียนกันว่า `Redis(host="redis")` หรือ `mysql://db:3306` — ทั้งที่ IP ของ container เปลี่ยนใหม่ได้ทุกครั้งที่รัน ชื่อ `redis` / `db` เหล่านี้ถูกแปลงเป็น IP ได้อย่างไร? ข้อ 4 จะเฉลยด้วยการทดลองจริง

---

## 0. เตรียมเครื่องเรียน

ทำบนเครื่องของเราเอง (ไม่ใช้ cloud) — เปิด container ที่ติดตั้ง Docker มาให้แล้ว

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> 📝 **คำอธิบาย:** `docker start ... || docker run ...` เปิดเครื่องเรียนเดิมถ้ามี และสร้างใหม่เฉพาะเมื่อยังไม่มี จึงไม่ลบ clone จาก LAB ก่อนหน้า ·
> `-dit` คือ `-d` รันเบื้องหลัง + `-i` เปิด stdin ค้างไว้ + `-t` ให้มี terminal กล่องจะได้ไม่ดับทันที · `--privileged` ให้สิทธิ์เต็มเพื่อรัน **Docker ซ้อนข้างในกล่อง** (จำเป็น — `box1`–`box5` และเพื่อน ๆ ของแล็บนี้เป็น container ที่รันอยู่ข้างในเครื่องเรียนอีกที) ·
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
cd DevTools/03_Docker/04_Docker/004_LAB_Docker_Network_DNS
```

> 📝 **คำอธิบาย:** `mkdir -p ~/labwork` สร้างโฟลเดอร์เก็บงาน (`-p` = มีอยู่แล้วก็ไม่ error) · `git clone` ดึงรีโพของวิชาลงมา ทำครั้งเดียวใช้ได้ทุกแล็บของชุดนี้ · โฟลเดอร์แล็บนี้มีแค่ `readme.md` — ทุกคำสั่งของแล็บพิมพ์สด ๆ ใน terminal ได้จากที่ไหนก็ได้ ·
> ถ้าเคย clone ไว้ git จะบอกว่าโฟลเดอร์ไม่ว่าง — ข้ามไป `cd` ได้เลย

---

## 2. สำรวจ network ที่ Docker แถมมา

Docker ติดตั้งเสร็จปุ๊บก็มี network รอไว้ให้แล้ว 3 วง — ดูกันก่อนว่ามีอะไรบ้าง :

```bash
docker network ls
```

> 📝 **คำอธิบาย:** `docker network ls` แสดง network ทั้งหมดที่ daemon รู้จัก · คอลัมน์ที่ต้องดูคือ **DRIVER** — ตัวขับเคลื่อนที่กำหนดพฤติกรรมของ network วงนั้น ·
> สามวงนี้คือค่าตั้งต้น **ลบไม่ได้** : `bridge` (วง NAT ส่วนตัว — container ที่รันโดยไม่ระบุ `--network` จะถูกเสียบเข้าวงนี้อัตโนมัติ) · `host` (ไม่สร้างวงใหม่ ใช้ network ของเครื่องตรง ๆ) · `none` (ตัดขาดโลก — ไม่มี interface อะไรเลยนอกจาก loopback)

✅ **Expected output** — เห็น 3 แถว driver `bridge` / `host` / `null` (NETWORK ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
NETWORK ID     NAME      DRIVER    SCOPE
b3114e2547c3   bridge    bridge    local
a39fb678ffa4   host      host      local
3dc02e20d892   none      null      local
```

เจาะดูข้างในวง `bridge` ว่าตั้งค่าอะไรไว้ :

```bash
docker network inspect bridge
```

> 📝 **คำอธิบาย:** `docker network inspect <ชื่อ>` แสดงรายละเอียดเป็น JSON · จุดที่ต้องดูมี 3 จุด : `IPAM.Config` บอก **Subnet** (วง IP ที่จะแจกให้ container) กับ **Gateway** (ประตูออกสู่โลกภายนอก) · `Options` มี `com.docker.network.bridge.name: docker0` — ตัวตนจริงของวงนี้คือ interface `docker0` บนเครื่อง · `Containers` ตอนนี้ **ว่างเปล่า** เพราะยังไม่มีใครรันอยู่ ·
> Subnet ในกล่องเรียนคือ `172.18.0.0/16` — บนเครื่องเปล่า ๆ มักเป็น `172.17.0.0/16` แต่ Docker ในกล่องเรียนเลี่ยงไปใช้วงถัดไปเพราะ `172.17.x.x` ถูก network รอบนอกใช้แล้ว **เลขวงของแต่ละคนต่างกันได้ ไม่ใช่ความผิดพลาด**

✅ **Expected output** — ตัดมาเฉพาะท่อนที่ต้องดู (ID · เวลา · เลขวงของแต่ละคนอาจไม่ตรงกับเอกสารนี้):

```
[
    {
        "Name": "bridge",
        "Driver": "bridge",
        "IPAM": {
            "Config": [
                {
                    "Subnet": "172.18.0.0/16",
                    "Gateway": "172.18.0.1"
                }
            ]
        },
        ...
        "Options": {
            "com.docker.network.bridge.default_bridge": "true",
            ...
            "com.docker.network.bridge.name": "docker0",
        },
        "Containers": {},
        ...
    }
]
```

---

## 3. การทดลองที่ 1 : default bridge — IP ได้ แต่ชื่อไม่ได้

รัน container เปล่า ๆ 2 ตัวโดย **ไม่ระบุ network อะไรเลย** — ทั้งคู่จะตกลงวง `bridge` อัตโนมัติ :

```bash
docker run -d --name box1 alpine sleep infinity
docker run -d --name box2 alpine sleep infinity
docker ps
```

> 📝 **คำอธิบาย:** `-d` รันเบื้องหลัง · `--name box1` ตั้งชื่อไว้เรียกสั้น ๆ · `alpine` คือ Linux จิ๋ว (~3 MB) เหมาะกับการทดลอง · `sleep infinity` คือ "งาน" ของ container — alpine ไม่มี service อะไรรันเอง ถ้าไม่สั่งอะไรค้างไว้ container จะจบตัวเองทันที เราจึงให้มันนอนหลับตลอดกาลเพื่อเปิดค้างไว้ให้ `docker exec` เข้าไปได้ ·
> ครั้งแรกยังไม่มี image ในเครื่อง Docker จะ **pull ให้อัตโนมัติ** ก่อนรัน

✅ **Expected output** — `box1` มี pull log นำหน้า ส่วน `box2` ได้ container ID ทันที (image มีแล้ว) และ `docker ps` เห็นครบสองตัวสถานะ `Up` (ID · digest · เวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
Unable to find image 'alpine:latest' locally
latest: Pulling from library/alpine
55afa1ecc21d: Pulling fs layer
        ... (Download complete → Pull complete) ...
Status: Downloaded newer image for alpine:latest
f85ec19ddb9a3deb8cd8722ba27fa7585c76966caab7c2547ab28372d5f7838f
932a874d9ba588d284933d804b2d7c7be425907461cb68f3bf4e3e6987200e12
CONTAINER ID   IMAGE     COMMAND            CREATED          STATUS          PORTS     NAMES
932a874d9ba5   alpine    "sleep infinity"   11 seconds ago   Up 10 seconds             box2
f85ec19ddb9a   alpine    "sleep infinity"   11 seconds ago   Up 10 seconds             box1
```

ถาม Docker ว่าแต่ละกล่องได้ IP อะไร :

```bash
docker inspect -f '{{.Name}} -> {{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' box1 box2
```

> 📝 **คำอธิบาย:** `docker inspect` ดึงข้อมูลทุกอย่างของ container (JSON ยาวหลายจอ) · `-f '...'` คือ Go template เลือกพิมพ์เฉพาะฟิลด์ที่สนใจ — `{{range .NetworkSettings.Networks}}...{{end}}` วนทุก network ที่ container เสียบอยู่ แล้วพิมพ์ `{{.IPAddress}}` ของแต่ละวง · ใส่ชื่อหลายตัวต่อท้ายได้ จะรายงานทีละบรรทัด ·
> สังเกตว่า IP ทั้งคู่อยู่ในวง `172.18.0.0/16` ของ `bridge` ตามที่เห็นในข้อ 2 — Docker แจกไล่ลำดับ `.2`, `.3`, ... ตามคิวการรัน

✅ **Expected output** — สอง IP อยู่วงเดียวกัน (เลขของแต่ละคนอาจไม่ตรงกับเอกสารนี้ — **จดค่า IP ของ box2 ไว้ใช้บรรทัดถัดไป**):

```
/box1 -> 172.18.0.2
/box2 -> 172.18.0.3
```

**ยกที่ 1 : ping ด้วย IP** — จาก `box1` ยิงไปหา IP ของ `box2` (แทน `172.18.0.3` ด้วยค่าจริงของเครื่องตัวเอง) :

```bash
docker exec box1 ping -c 2 172.18.0.3
```

> 📝 **คำอธิบาย:** `docker exec box1 <คำสั่ง>` สั่งให้คำสั่งไปรัน **ข้างใน** `box1` · `ping -c 2` ส่ง echo request แค่ **2 ครั้งแล้วหยุดเอง** (`-c` = count) — ถ้าไม่ใส่ ping ของ alpine จะยิงไปเรื่อย ๆ ไม่ยอมจบ ·
> อย่าลืมเปลี่ยน IP เป็นค่าที่ได้จากคำสั่ง inspect ของตัวเอง

✅ **Expected output** — `2 packets transmitted, 2 packets received, 0% packet loss` = คุยกันด้วย IP ได้ปกติ (ตัวเลขเวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
PING 172.18.0.3 (172.18.0.3): 56 data bytes
64 bytes from 172.18.0.3: seq=0 ttl=64 time=0.068 ms
64 bytes from 172.18.0.3: seq=1 ttl=64 time=0.074 ms

--- 172.18.0.3 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.068/0.071/0.074 ms
```

**ยกที่ 2 : ping ด้วยชื่อ** — คราวนี้เรียก `box2` ด้วยชื่อตรง ๆ :

```bash
docker exec box1 ping -c 2 box2
```

> 📝 **คำอธิบาย:** คำสั่งเดียวกันเป๊ะ เปลี่ยนแค่ IP เป็นชื่อ container · บน **default bridge ไม่มีบริการแปลชื่อ** — Docker ตั้งใจปิดไว้เพื่อความเข้ากันได้กับพฤติกรรมรุ่นเก่า `box1` จึงไม่รู้จักคำว่า `box2` เลย ·
> `bad address` = แปลชื่อเป็น IP ไม่ได้ตั้งแต่ต้น (คนละอาการกับ "แปลได้แต่ต่อไม่ติด" ซึ่งจะขึ้น timeout)

✅ **Expected output** — **ล้มเหลว** และนี่คือผลที่ถูกต้องของการทดลอง:

```
ping: bad address 'box2'
```

> **คำถามใหญ่ประจำแล็บ :** ping ด้วย IP ได้ แต่ IP ของ container **เปลี่ยนใหม่ได้ทุกครั้งที่รัน** (ลอง `docker rm -f box2` แล้วรันใหม่ อาจได้ `.5` แทน `.3`) — แล้วแอปจริงที่ต้อง config ปลายทางล่วงหน้า เช่น web ต้องรู้ที่อยู่ database จะเขียนอะไรลงไฟล์ config? ฮาร์ดโค้ด IP คือหายนะแน่นอน... ข้อถัดไปคือคำตอบ

---

## 4. การทดลองที่ 2 : user-defined network — DNS ในตัว

สร้าง network ของเราเองสักวง :

```bash
docker network create --driver bridge --subnet 172.30.0.0/24 lab_net
docker network ls
```

> 📝 **คำอธิบาย:** `docker network create` สร้าง network ใหม่ · `--driver bridge` ใช้ driver แบบเดียวกับวง default (ไม่ใส่ก็ได้ค่านี้อยู่แล้ว — เขียนให้ชัดว่าเราเลือกอะไร) · `--subnet 172.30.0.0/24` กำหนดวง IP เอง (มี 254 ที่ให้แจก) — จำเป็นถ้าอยากใช้ `--ip` กำหนดเลขตายตัวในข้อ 5 · `lab_net` คือชื่อวง ·
> เลือกวงที่ไม่ชนกับ `172.18.0.0/16` ของ default bridge — ถ้าตั้งวงซ้อนกัน Docker จะ error ตั้งแต่ create

✅ **Expected output** — ได้ ID ของ network ใหม่ และ `ls` เห็น `lab_net` เพิ่มเป็นวงที่ 4 (ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
358f85832b25bc5722aa5290b1b26ec27274c183a0eec0545f1d6de5e44a31bd
NETWORK ID     NAME      DRIVER    SCOPE
b3114e2547c3   bridge    bridge    local
a39fb678ffa4   host      host      local
358f85832b25   lab_net   bridge    local
3dc02e20d892   none      null      local
```

เช็กว่า subnet ตรงตามที่สั่ง :

```bash
docker network inspect lab_net
```

> 📝 **คำอธิบาย:** โครง JSON เดียวกับตอน inspect `bridge` ในข้อ 2 · จุดที่ต้องดู : `Subnet`/`Gateway` ตรงกับที่เราสั่ง และ `Containers` ยังว่าง — เดี๋ยวจะกลับมาดูอีกครั้งหลังมีสมาชิก

✅ **Expected output** — ตัดมาเฉพาะท่อน IPAM (ID · เวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
[
    {
        "Name": "lab_net",
        "Driver": "bridge",
        "IPAM": {
            "Config": [
                {
                    "Subnet": "172.30.0.0/24",
                    "Gateway": "172.30.0.1"
                }
            ]
        },
        "Containers": {},
        ...
    }
]
```

รัน container 2 ตัวใหม่ **เสียบเข้า `lab_net` ตั้งแต่เกิด** :

```bash
docker run -d --name box3 --network lab_net alpine sleep infinity
docker run -d --name box4 --network lab_net alpine sleep infinity
```

> 📝 **คำอธิบาย:** ทุกอย่างเหมือน `box1`/`box2` เป๊ะ เพิ่มแค่ `--network lab_net` — บอก Docker ว่า container นี้ให้เสียบเข้าวง `lab_net` แทน default bridge · image `alpine` มีในเครื่องแล้วจากข้อ 3 จึงไม่ pull ซ้ำ ได้ container ID กลับมาทันที

✅ **Expected output** — container ID สองบรรทัด (ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
5b6a5e73466dcc17301e988fc3ad84d15b187e6682c2fd829189a1b55142cc11
f01672af8f796afaf23f62eb544b11e747217f88f9d1b9b099a85377b551e85f
```

**ช่วงเวลาสำคัญของแล็บ** — ทำการทดลองเดิมที่เพิ่งล้มเหลวในข้อ 3 อีกครั้ง คราวนี้บนวงที่เราสร้างเอง :

```bash
docker exec box3 ping -c 2 box4
```

> 📝 **คำอธิบาย:** คำสั่งหน้าตาเดียวกับ "ยกที่ 2" ที่เพิ่งพ่าย `bad address` เมื่อกี้ทุกประการ — ต่างกันแค่คู่นี้อยู่บน `lab_net` · สังเกตบรรทัดแรกของผลลัพธ์ : `PING box4 (172.30.0.3)` — มีใครบางคน**แปลชื่อ `box4` เป็น IP ให้เรียบร้อย**ก่อนยิงจริง

✅ **Expected output** — **สำเร็จด้วยชื่อ!** `0% packet loss` (IP · ตัวเลขเวลาของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
PING box4 (172.30.0.3): 56 data bytes
64 bytes from 172.30.0.3: seq=0 ttl=64 time=0.065 ms
64 bytes from 172.30.0.3: seq=1 ttl=64 time=0.054 ms

--- box4 ping statistics ---
2 packets transmitted, 2 packets received, 0% packet loss
round-trip min/avg/max = 0.054/0.059/0.065 ms
```

ใครกันที่แปลชื่อให้? — เปิดไฟล์ตั้งค่า DNS ข้างใน `box3` ดู :

```bash
docker exec box3 cat /etc/resolv.conf
```

> 📝 **คำอธิบาย:** `/etc/resolv.conf` คือไฟล์มาตรฐานของ Linux ที่บอกว่า "จะแปลชื่อเป็น IP ให้ไปถามใคร" · จุดชี้ขาดคือ `nameserver 127.0.0.11` — IP วง loopback พิเศษที่ Docker แอบฝัง **Embedded DNS server** ไว้ข้างในทุก container ที่อยู่บน user-defined network · DNS ตัวนี้รู้จักชื่อ container ทุกตัวในวงเดียวกัน แปลชื่อ → IP ปัจจุบันให้สด ๆ ถ้าถามชื่อนอกวง (เช่น `google.com`) มันจะส่งต่อไป DNS จริงข้างนอกให้เอง

✅ **Expected output** — เห็น `nameserver 127.0.0.11` = DNS server ลับของ Docker ตัวเป็น ๆ (บรรทัดคอมเมนต์ท้ายไฟล์ของแต่ละคนอาจไม่ตรงกับเอกสารนี้):

```
# Generated by Docker Engine.
# This file can be edited; Docker Engine will not make further changes ...

nameserver 127.0.0.11
options ndots:0
...
```

> **นี่คือคำตอบของคำถามก่อนเริ่ม :** โค้ดจริงเขียน `Redis(host="redis")` ได้เพราะ container ทั้งคู่อยู่ user-defined network เดียวกัน — Embedded DNS แปลชื่อ `redis` เป็น IP ปัจจุบันให้เสมอ **ไม่ว่า IP จะสุ่มมาเป็นอะไร** ·
> และนี่คือสิ่งที่ `docker compose` ทำให้อัตโนมัติ: ทุก service ในไฟล์ compose ถูกเสียบเข้า network เดียวกันและเรียกหากันด้วยชื่อ service ได้ทันที — LAB 5 จะได้ใช้เต็ม ๆ

---

## 5. กำหนด IP เองได้เมื่อมี subnet

พอ network เป็นของเรา จะสั่งเลขเองก็ยังได้ :

```bash
docker run -d --name box5 --network lab_net --ip 172.30.0.50 alpine sleep infinity
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' box5
```

> 📝 **คำอธิบาย:** `--ip 172.30.0.50` ขอ IP ตายตัวแทนการรอแจก — ใช้ได้เพราะ `lab_net` ประกาศ `--subnet` ไว้ตอน create · เลขต้องอยู่ในวง `172.30.0.0/24` และไม่ซ้ำกับใคร ·
> มีประโยชน์กับของที่อยากให้ที่อยู่นิ่งสนิท (เช่น ตัวที่ firewall ต้องอ้างถึง) — แต่งานทั่วไป **ใช้ชื่อผ่าน DNS ดีกว่า** เพราะไม่ต้องจัดสรรเลขเอง

> ⚠️ ถ้าใช้ `--ip` กับ **default bridge** จะโดนปฏิเสธ: `user specified IP address is supported on user defined networks only` — นี่คือเหตุผลหนึ่งที่เราต้องสร้าง network เองก่อน

✅ **Expected output** — ได้ container ID แล้ว inspect ยืนยัน IP ตรงเป๊ะตามสั่ง (ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้ แต่ **IP ต้องตรง**):

```
2e345018cf74c93f61ee8149a18c4447e5fb8c636494f92c37933113427ef71e
172.30.0.50
```

แถม: `box5` ก็เรียกด้วยชื่อได้ทันทีเหมือนเพื่อนร่วมวง :

```bash
docker exec box3 ping -c 2 box5
```

> 📝 **คำอธิบาย:** สมาชิกใหม่ของ `lab_net` ถูกลงทะเบียนกับ Embedded DNS อัตโนมัติ — สังเกตว่า DNS แปล `box5` เป็น `172.30.0.50` เลขที่เรากำหนดเองเป๊ะ ๆ

✅ **Expected output** — ชื่อ `box5` ถูกแปลเป็น IP ที่เราสั่ง และ `0% packet loss`:

```
PING box5 (172.30.0.50): 56 data bytes
64 bytes from 172.30.0.50: seq=0 ttl=64 time=0.068 ms
        ...
2 packets transmitted, 2 packets received, 0% packet loss
```

---

## 6. ภารกิจกู้ข้อความลับ 🕵️

ถึงเวลาเอาความรู้ทั้งหมดมาใช้ — **โจทย์ :** มีเซิร์ฟเวอร์ลับซ่อนอยู่ใน `lab_net` ส่วนสายลับของเราเกิดมาอยู่ผิดวง (default bridge) ต้องหาทางเข้าไปอ่านข้อความลับให้ได้ **โดยห้าม restart container**

**ฝั่งเซิร์ฟเวอร์** — รัน nginx ใน `lab_net` แล้วฝังข้อความลับ :

```bash
docker run -d --name secret-server --network lab_net nginx:alpine
docker exec secret-server sh -c 'echo "<h1>ยินดีด้วย! คุณกู้ข้อความลับสำเร็จ 🎉 Embedded DNS ทำงานแล้ว</h1>" > /usr/share/nginx/html/index.html'
```

> 📝 **คำอธิบาย:** `nginx:alpine` คือ web server ตัวจริง (รุ่น alpine เล็ก ~20 MB) เปิด port 80 รออยู่ **ข้างใน network เท่านั้น** — สังเกตว่าเรา **ไม่ใส่ `-p` เลย** เพราะไม่อยากให้โลกภายนอกเห็น ให้เห็นเฉพาะสมาชิก `lab_net` ·
> บรรทัดที่สอง `docker exec ... sh -c '...'` เขียนทับหน้าแรกของ nginx (`/usr/share/nginx/html/index.html`) ด้วยข้อความลับ — ต้องครอบด้วย `sh -c` เพราะเครื่องหมาย `>` (redirect) เป็นความสามารถของ shell ไม่ใช่ของ `echo`

✅ **Expected output** — ครั้งแรกมี pull log ของ `nginx:alpine` ก่อน แล้วจบด้วย container ID ส่วนบรรทัด `exec` สำเร็จแบบเงียบ ๆ ไม่พิมพ์อะไร (digest · ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
Unable to find image 'nginx:alpine' locally
alpine: Pulling from library/nginx
62bec68d7c31: Pulling fs layer
        ... (รวม 7 layer · Pulling fs layer → Download complete → Pull complete ทีละ layer) ...
Status: Downloaded newer image for nginx:alpine
09de0fe2d4e7380086b42783cbc86253301ee763dc818113119515b2bf446521
```

**ฝั่งสายลับ** — เกิดบน default bridge (ไม่ระบุ `--network`) :

```bash
docker run -d --name spy alpine sleep infinity
```

> 📝 **คำอธิบาย:** จงใจให้ `spy` อยู่ **คนละวง** กับเป้าหมาย — สถานการณ์เดียวกับ `box1`/`box2` ในข้อ 3 แต่คราวนี้เป้าหมายคือ HTTP ไม่ใช่ ping

✅ **Expected output** — container ID หนึ่งบรรทัด (ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
081a4a8e8681c92fd7130f68007d19a484d1ad891d2c04dd40e8d6ac6366cd6a
```

**ความพยายามครั้งที่ 1** — ยิงตรง ๆ จากวงนอก :

```bash
docker exec spy wget -qO- --timeout=3 http://secret-server
```

> 📝 **คำอธิบาย:** alpine ไม่มี `curl` แต่มี `wget` ในตัว · `-q` ปิด progress log · `-O-` ส่งเนื้อหาที่โหลดได้ออก **stdout** แทนการบันทึกเป็นไฟล์ (ขีดหลัง `-O` แปลว่า stdout) · `--timeout=3` ยอมรอแค่ 3 วินาที — กันคำสั่งค้างถ้าปลายทางเงียบ ·
> ล้มเหลว 2 ชั้น: `spy` ไม่มี DNS ที่รู้จักชื่อ `secret-server` (อยู่ default bridge) และต่อให้รู้ IP ก็ข้ามวงไม่ได้ — คนละ network = **มองไม่เห็นกันโดยสิ้นเชิง** นี่แหละ network isolation

✅ **Expected output** — **ล้มเหลวตามคาด** สายลับยังเข้าไม่ถึง:

```
wget: bad address 'secret-server'
```

**อุปกรณ์ลับ : เสียบสายแลนสด ๆ** — เชื่อม `spy` ที่กำลังรันอยู่เข้า `lab_net` โดยไม่ต้อง restart :

```bash
docker network connect lab_net spy
```

> 📝 **คำอธิบาย:** `docker network connect <network> <container>` (ลำดับ: network ก่อน container) เสียบ container **ที่กำลังรันอยู่** เข้า network เพิ่มอีกวง — เทียบได้กับเสียบสายแลนเส้นที่สองให้เครื่องที่เปิดอยู่ ไม่มี downtime แม้แต่วินาทีเดียว · `spy` จะได้ interface ใหม่ + IP ในวง `172.30.0.x` + สิทธิ์ใช้ Embedded DNS ของวงนั้นทันที · คำสั่งสำเร็จแบบเงียบ ๆ ไม่พิมพ์อะไรออกมา

**ความพยายามครั้งที่ 2** — คำสั่งเดิมเป๊ะ :

```bash
docker exec spy wget -qO- http://secret-server
```

✅ **Expected output** — **ข้อความลับโผล่มา!** 🎉

```
<h1>ยินดีด้วย! คุณกู้ข้อความลับสำเร็จ 🎉 Embedded DNS ทำงานแล้ว</h1>
```

> 📝 **คำอธิบาย:** สิ่งที่เกิดขึ้นเบื้องหลัง: `wget` ถาม Embedded DNS (127.0.0.11) ว่า `secret-server` คือใคร → ได้ IP ในวง `172.30.0.x` → ต่อ HTTP port 80 ข้างในวงตรง ๆ → nginx ส่งหน้า index ที่เราฝังไว้กลับมา — ทั้งหมดโดยไม่มี `-p` ไม่มี port mapping ใด ๆ เพราะเป็นการคุยกัน **ภายใน network**

**หลักฐานประกอบคดี** — ดูว่าตอนนี้ `spy` มีขากี่วง :

```bash
docker inspect -f '{{json .NetworkSettings.Networks}}' spy | python3 -m json.tool
```

> 📝 **คำอธิบาย:** `{{json ...}}` พิมพ์ฟิลด์นั้นเป็น JSON ดิบ แล้วส่งต่อให้ `python3 -m json.tool` จัดย่อหน้าให้อ่านง่าย · จุดที่ต้องดู: มี **2 key** คือ `bridge` และ `lab_net` — container เดียวเสียบพร้อมกัน 2 วง แต่ละวงมี IP/Gateway ของตัวเอง · สังเกต `DNSNames` ในฝั่ง `lab_net` มีชื่อ `spy` = ลงทะเบียนกับ Embedded DNS แล้ว (ฝั่ง `bridge` เป็น `null` — วง default ไม่มีบริการนี้)

✅ **Expected output** — ตัดมาเฉพาะฟิลด์สำคัญ (ID · MAC · IP ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
{
    "bridge": {
        ...
        "Gateway": "172.18.0.1",
        "IPAddress": "172.18.0.4",
        "DNSNames": null
    },
    "lab_net": {
        ...
        "Gateway": "172.30.0.1",
        "IPAddress": "172.30.0.5",
        "DNSNames": [
            "spy",
            "081a4a8e8681"
        ]
    }
}
```

**พิสูจน์ย้อนกลับ** — ถอดสายแล้วยิงซ้ำ ต้องกลับไปล้มเหลวเหมือนเดิม :

```bash
docker network disconnect lab_net spy
docker exec spy wget -qO- --timeout=3 http://secret-server
```

> 📝 **คำอธิบาย:** `docker network disconnect` คือขาถอดของ `connect` — ถอดสด ๆ ได้เหมือนกัน · การทดลองที่ดีต้องพิสูจน์ได้สองทาง: เชื่อมแล้วเห็น **และ** ถอดแล้วต้องกลับไปมองไม่เห็น จึงสรุปได้ว่า network คือตัวแปรจริง ไม่ใช่ความบังเอิญ · ใส่ `--timeout=3` กลับมาด้วยกันคำสั่งค้าง

✅ **Expected output** — กลับไปล้มเหลวเหมือนความพยายามครั้งที่ 1 ทุกประการ:

```
wget: bad address 'secret-server'
```

> **สรุปคดี :** container จะเห็นกันได้ต้องอยู่ network เดียวกัน — และ `docker network connect/disconnect` ปรับผังวงได้ตลอดเวลาโดยไม่ต้อง restart ใครเลย

---

## 7. โหมดพิเศษ : host และ none

สองวงที่เหลือจากข้อ 2 ที่ยังไม่ได้ลอง — เป็นสองขั้วสุดโต่งของ network

**`--network host` : ไม่มีวงส่วนตัว ใช้ network ของเครื่องตรง ๆ**

```bash
docker run -d --name hostnginx --network host nginx:alpine
curl -s localhost:80 | grep -o "<title>.*</title>"
```

> 📝 **คำอธิบาย:** `--network host` ทำให้ container **ไม่มี network stack ของตัวเอง** — port 80 ที่ nginx เปิด คือ port 80 ของเครื่องเรียนโดยตรง · บรรทัดที่สองรันจาก **shell เครื่องเรียนตรง ๆ ไม่ผ่าน `docker exec`** : `curl -s` โหลดหน้าเว็บแบบเงียบ แล้ว `grep -o "<title>.*</title>"` ตัดมาเฉพาะแท็ก title ·
> จุดที่ต้องสังเกต: เราเข้าถึง nginx ได้ **โดยไม่มี `-p` เลย** — ข้อดีคือเร็ว (ไม่มีชั้น NAT) และง่าย ข้อเสียคือ **เสีย isolation**: port ชนกับโปรแกรมอื่นบนเครื่องได้ทันที และใช้ `-p` ควบคุมการเปิดเผยไม่ได้อีก · โหมดนี้ทำงานเต็มรูปแบบเฉพาะบน Linux

✅ **Expected output** — ได้ container ID แล้ว `curl` เห็นหน้า nginx ทันที (ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
45a3de8e5f032597318ff98a239c74df123bb9d4e5c694d579448f5f9144eba7
<title>Welcome to nginx!</title>
```

ดูคอลัมน์ PORTS ของมันสิ — ว่างเปล่า :

```bash
docker ps --filter name=hostnginx --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

> 📝 **คำอธิบาย:** `--filter name=hostnginx` กรองเฉพาะตัวที่สนใจ · `--format "table ..."` เลือกคอลัมน์เอง · PORTS **ว่าง** เพราะไม่มี mapping ให้แสดง — ไม่มีการ "ส่งต่อ" port ใด ๆ ทั้งสิ้น container ยืนอยู่บน network ของเครื่องเองเลย

✅ **Expected output** — สถานะ `Up` แต่ PORTS ว่างเปล่า:

```
NAMES       STATUS          PORTS
hostnginx   Up 13 seconds
```

**`--network none` : ตัดขาดโลกทั้งใบ**

```bash
docker run --rm --network none alpine ip addr
```

> 📝 **คำอธิบาย:** `--network none` ให้ container เกิดมาโดย **ไม่มี interface อะไรเลย** นอกจาก loopback · `--rm` ลบ container ทิ้งอัตโนมัติเมื่อจบ (งานนี้รันคำสั่งเดียวแล้วจบ ไม่ต้องเก็บ) · `ip addr` แสดง network interface ทั้งหมดที่ container มองเห็น ·
> ใช้กับงานที่ **ไม่ควรออกเน็ตได้เลย** เช่น batch ประมวลผลไฟล์ข้อมูลอ่อนไหว หรือรันโค้ดที่ไม่ไว้ใจ — ต่อให้โค้ดพยายามส่งข้อมูลออก ก็ไม่มีท่อให้ส่ง

✅ **Expected output** — มีแค่ `lo` (loopback) โผล่มาตัวเดียว ไม่มี `eth0` ใด ๆ:

```
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host
       valid_lft forever preferred_lft forever
```

> **ภาพรวม 3 โหมด :** `bridge` (โดยเฉพาะแบบสร้างเอง) = ค่ามาตรฐานของงานทั่วไป — isolation + DNS + เลือกเปิดเผยผ่าน `-p` ได้ · `host` = เร็วและง่ายแต่เสีย isolation ใช้เมื่อจำเป็นจริง ๆ · `none` = ห้องนิรภัยสำหรับงานที่ห้ามออกเน็ต

---

## 8. ล้างกระดาน (cleanup)

แล็บนี้สร้าง container ไว้ 8 ตัวกับ network อีก 1 วง — เก็บให้หมด :

```bash
docker rm -f box1 box2 box3 box4 box5 secret-server spy hostnginx
docker network rm lab_net
```

> 📝 **คำอธิบาย:** `docker rm -f` ลบหลายตัวได้ในคำสั่งเดียว (`-f` บังคับหยุดก่อนลบ เพราะทุกตัวยังรันอยู่) — ตัวที่รันด้วย `--rm` ในข้อ 7 ลบตัวเองไปแล้ว ไม่อยู่ในรายชื่อ · `docker network rm lab_net` ลบวงที่สร้างเอง ·
> **ลำดับสำคัญ**: ต้องลบ container ก่อนลบ network — ถ้ายังมีตัวเสียบอยู่จะเจอ `error ... has active endpoints` · ส่วน `bridge`/`host`/`none` เป็นวงตั้งต้นของ Docker ลบไม่ได้และไม่ต้องลบ · image `alpine`/`nginx:alpine` เก็บไว้ได้ แล็บถัดไปจะได้ไม่ต้อง pull ใหม่

✅ **Expected output** — Docker พิมพ์ชื่อทุกตัวที่ลบสำเร็จกลับมา ปิดท้ายด้วยชื่อ network:

```
box1
box2
box3
box4
box5
secret-server
spy
hostnginx
lab_net
```

ตรวจซ้ำว่าสะอาดจริง :

```bash
docker ps -a
docker network ls
```

> 📝 **คำอธิบาย:** `docker ps -a` ต้องเหลือแค่หัวตาราง (`-a` นับตัวที่หยุดแล้วด้วย) · `docker network ls` ต้องกลับมาเหลือ 3 วงตั้งต้นเหมือนตอนเปิดแล็บในข้อ 2 เป๊ะ — เทียบกับ output แรกสุดของแล็บได้เลย

✅ **Expected output** — ไม่เหลือ container และ network กลับมาเป็น 3 วงดั้งเดิม (NETWORK ID ของแต่ละคนจะไม่ตรงกับเอกสารนี้):

```
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
NETWORK ID     NAME      DRIVER    SCOPE
b3114e2547c3   bridge    bridge    local
a39fb678ffa4   host      host      local
3dc02e20d892   none      null      local
```

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ping: bad address 'box2'` ในข้อ 3 | **ไม่ใช่ความผิดพลาด** — default bridge ไม่มี DNS | นี่คือผลการทดลองที่ถูกต้อง อ่านต่อข้อ 4 |
| `ping: bad address ...` ทั้งที่อยู่ `lab_net` แล้ว | พิมพ์ชื่อผิด หรือปลายทางไม่ได้อยู่วงเดียวกันจริง | `docker network inspect lab_net` ดูรายชื่อใน `Containers` ว่ามีครบทั้งคู่ไหม |
| `docker run --ip` ฟ้อง `user specified IP address is supported on user defined networks only` | ใช้ `--ip` กับ default bridge | ใช้ได้เฉพาะ network ที่สร้างเองพร้อม `--subnet` — รันด้วย `--network lab_net` |
| `docker network rm` ฟ้อง `has active endpoints` | ยังมี container เสียบอยู่ในวง | `docker rm -f` (หรือ `docker network disconnect`) สมาชิกให้หมดก่อน แล้วค่อย `network rm` |
| `docker run` ฟ้องชื่อซ้ำ (`already in use`) | มี container ตัวเก่าจองชื่ออยู่ | `docker rm -f <ชื่อ>` แล้วรันใหม่ |
| `wget` ค้างนานผิดปกติแทนที่จะ error | ไม่ได้ใส่ `--timeout` แล้วปลายทางเงียบ | ใส่ `--timeout=3` ทุกครั้งที่คาดว่าอาจต่อไม่ติด |
| `curl localhost:80` ในข้อ 7 ไม่ได้อะไรกลับมา | nginx ยังไม่ทันพร้อม หรือ port 80 บนเครื่องถูกใช้อยู่ | รอ 1–2 วินาทีแล้วลองใหม่ · `docker logs hostnginx` ดูว่ามี error จอง port ไหม |

---

## สรุปสิ่งที่ได้เรียนรู้

| สิ่งที่ทำ | คำสั่ง/แนวคิดหลัก | ทำไมสำคัญ |
|---|---|---|
| สำรวจ network ตั้งต้น 3 วง | `docker network ls` · `docker network inspect bridge` | รู้ว่า container ที่ไม่ระบุ `--network` ไปอยู่ที่ไหน และวงนั้นมี Subnet/Gateway อะไร |
| พิสูจน์ข้อจำกัดของ default bridge | ping ด้วย IP สำเร็จ · ping ด้วยชื่อ `bad address` | IP เปลี่ยนทุกครั้งที่รันใหม่ — แอปจริงฮาร์ดโค้ด IP ไม่ได้ จึงต้องมีระบบชื่อ |
| สร้าง network เอง | `docker network create --driver bridge --subnet ... lab_net` | ปลดล็อก Embedded DNS + ควบคุมวง IP เองได้ |
| เรียก container ด้วยชื่อ | `ping box4` สำเร็จ · `nameserver 127.0.0.11` ใน `/etc/resolv.conf` | คือกลไกเบื้องหลัง `Redis(host="redis")` ของแอปจริง และสิ่งที่ compose ทำให้อัตโนมัติ |
| กำหนด IP ตายตัว | `docker run --ip 172.30.0.50` (ต้องมี `--subnet`) | ควบคุมที่อยู่ได้เมื่อจำเป็น — แต่งานทั่วไปใช้ชื่อผ่าน DNS ดีกว่า |
| เชื่อม/ถอด network สด ๆ | `docker network connect` / `disconnect` | ปรับผัง network ของ container ที่กำลังรันอยู่ได้โดยไม่มี downtime — และ container มีขาได้หลายวงพร้อมกัน |
| เข้าใจ isolation ข้ามวง | `spy` มองไม่เห็น `secret-server` จนกว่าจะอยู่วงเดียวกัน | network คือกำแพงความปลอดภัยชั้นแรกระหว่าง container |
| ลองโหมด host / none | `--network host` (ไม่มี `-p` ก็เข้าถึงได้) · `--network none` (เหลือแค่ `lo`) | รู้จักสองขั้วสุดโต่ง: แลก isolation กับความเร็ว vs ตัดขาดโลกเพื่อความปลอดภัย |

**แล็บนี้ตอบคำถามที่ค้างจาก LAB ก่อน ๆ แล้ว** — container หลายตัวคุยกันด้วย "ชื่อ" ได้อย่างไรโดยไม่ต้องรู้ IP ล่วงหน้า: คำตอบคือ **user-defined network + Embedded DNS** แต่สังเกตไหมว่าแล็บนี้เราต้องพิมพ์ `docker network create` เอง, `docker run --network ...` เองทีละตัว, ลบเองทีละตัว — พอแอปจริงมี 5 service ขั้นตอนพวกนี้จะยาวและพลาดง่ายมาก · **LAB 5 (Docker Compose)** จะยุบทั้งหมดนี้เหลือไฟล์ YAML ไฟล์เดียวกับคำสั่ง `docker compose up` คำสั่งเดียว — แล้วจะเห็นว่า network + DNS ที่เราสร้างมือในแล็บนี้ compose สร้างให้ฟรีโดยอัตโนมัติ

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `docker network ls` เห็น 3 วงตั้งต้น `bridge` / `host` / `none` และอธิบายได้ว่าต่างกันอย่างไร
- [ ] `docker network inspect bridge` ชี้ Subnet กับ Gateway ได้ (และไม่ตกใจถ้าเลขวงไม่ตรงกับเพื่อน)
- [ ] `box1` ping IP ของ `box2` สำเร็จ แต่ ping ชื่อ `box2` ได้ `bad address` — อธิบายได้ว่าทำไม
- [ ] สร้าง `lab_net` ด้วย `--subnet 172.30.0.0/24` แล้ว `box3` ping ชื่อ `box4` **สำเร็จ**
- [ ] เปิด `/etc/resolv.conf` เจอ `nameserver 127.0.0.11` และอธิบายได้ว่ามันคือใคร
- [ ] `box5` ได้ IP `172.30.0.50` ตรงตามที่สั่งด้วย `--ip`
- [ ] `spy` ยิง `secret-server` ครั้งแรก **ล้มเหลว** · หลัง `docker network connect` แล้ว **เห็นข้อความลับ** · หลัง `disconnect` กลับไป **ล้มเหลว**
- [ ] `docker inspect ... spy` เห็น 2 network พร้อมกัน และ `DNSNames` มีเฉพาะฝั่ง `lab_net`
- [ ] `hostnginx` เข้าถึงได้ทาง `curl localhost:80` โดยไม่มี `-p` และคอลัมน์ PORTS ว่างเปล่า
- [ ] `--network none` เห็นแค่ `lo` ไม่มี `eth0`
- [ ] ล้างกระดานแล้ว: `docker ps -a` เหลือแค่หัวตาราง และ `docker network ls` กลับมาเหลือ 3 วงดั้งเดิม

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` เมื่อ 12 ส.ค. 2026*
