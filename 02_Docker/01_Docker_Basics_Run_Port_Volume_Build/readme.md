# Week 8 — Docker

Software Development Tools and Environments

Docker is an open-source platform that automates the deployment of applications inside software
containers. It provides an additional layer of abstraction and automation of OS-level virtualization
on Windows and Linux.

---

## สไลด์

เปิดไฟล์ [`Docker_Basics_Run_Port_Volume_Build.html`](./Docker_Basics_Run_Port_Volume_Build.html) ในเบราว์เซอร์
(ไฟล์เดียวจบ ไม่ต้องติดตั้งอะไร · กด `O` ดูสไลด์ทั้งหมด · `Ctrl+P` บันทึกเป็น PDF)

ผลการรันทุกอย่างในสไลด์ **รันจริง** บนเครื่องเรียน `tuchsanai/devtools:2569_1`

## เครื่องสำหรับทำแล็บ

ทำบนเครื่องเราเอง ผ่าน VS Code — **ไม่ใช้ cloud**

```bash
docker rm -f devtools
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> 📝 **คำอธิบาย:** บรรทัดแรกลบเครื่องเรียนตัวเดิมทิ้ง (ถ้าเคยสร้างไว้) เพื่อให้เริ่มจากของใหม่เสมอ ·
> บรรทัดที่สองสร้างเครื่องเรียนขึ้นมา โดย `-dit` ทำให้กล่องรันเบื้องหลังและไม่ดับทันที `--privileged`
> ให้สิทธิ์เต็มเพื่อ**รัน Docker ซ้อนอยู่ข้างในกล่อง** (Docker-in-Docker) และ `-p 2222:22` ส่ง port 2222
> ของเครื่องเรา เข้า port 22 (SSH) ของกล่อง · บรรทัดที่สาม ssh เข้าไปทำงานข้างใน
> — คำสั่ง `docker` ทุกคำสั่งในแล็บ **สั่งข้างในเครื่องเรียน** ไม่ใช่บนเครื่องเราโดยตรง

เข้าไปได้แล้วให้ตรวจก่อนว่า Docker ข้างในพร้อมใช้งาน :

```bash
docker --version
docker compose version
```

> 📝 **คำอธิบาย:** เป็นการเช็กว่า image เครื่องเรียนมี Docker ติดตั้งมาให้ครบแล้วจริง ถ้าทั้งสองคำสั่ง
> ขึ้นเลขเวอร์ชัน = พร้อมทำแล็บ ไม่ต้องติดตั้งอะไรเพิ่ม (สังเกตว่าเป็น `docker compose` เว้นวรรค
> ไม่ใช่ `docker-compose` ขีดกลาง ซึ่งเป็นรุ่นเก่าที่เลิกใช้แล้ว)

✅ **Expected output** — ได้เลขเวอร์ชันทั้งสองบรรทัด (เลขเวอร์ชันอาจต่างจากนี้เล็กน้อยตามรุ่นของ image) :

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

จากนั้นใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บข้างใน
(จะเปิดหน้าเว็บของแล็บในเบราว์เซอร์ ให้ forward port ที่แท็บ **PORTS** ของ VS Code)

## แล็บ

| แล็บในสไลด์ | โฟลเดอร์ | หัวข้อ | Port |
|---|---|---|---|
| **LAB 1** | [`001_LAB_Docker_Run`](./001_LAB_Docker_Run) | คำสั่ง `docker run` · `ps` · `pull` · `images` และวงจรชีวิต container | — |
| **LAB 2** | [`002_LAB_Nginx_Port_Mapping`](./002_LAB_Nginx_Port_Mapping) | Nginx + Port Mapping | 8080 |
| **LAB 3** | [`003_LAB_Nginx_Volume_Port_Mapping`](./003_LAB_Nginx_Volume_Port_Mapping) | Nginx + Volume + Port Mapping | 8083 |
| **LAB 4** | [`004_LAB_Node_Bulletin_Board`](./004_LAB_Node_Bulletin_Board) | Build image เอง (Node.js Bulletin Board) | 8085 |

> **เลขโฟลเดอร์ตรงกับเลขแล็บ** (`001`–`004` = LAB 1–4) — LAB 1 เป็นคำสั่งล้วน
> โฟลเดอร์ `001_LAB_Docker_Run` จึงมีเฉพาะเอกสาร ไม่มีไฟล์โค้ด

## Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Docker/01_Docker
```

> 📝 **คำอธิบาย:** สั่ง **ข้างในเครื่องเรียน** (หลัง ssh เข้าไปแล้ว) — สร้างโฟลเดอร์ที่ทำงาน `~/labwork`
> แล้วดึงโค้ดของทุกแล็บลงมาครั้งเดียว ใช้ได้ทั้ง LAB 1–4 ไม่ต้อง clone ซ้ำในแต่ละแล็บ
> เสร็จแล้วจะอยู่ในโฟลเดอร์ที่มีโฟลเดอร์ `001_LAB_Docker_Run` … `004_LAB_Node_Bulletin_Board` อยู่ข้างใน

## อ่านเอกสารแล็บอย่างไร

เอกสารของทุกแล็บใช้รูปแบบเดียวกัน :

| สัญลักษณ์ | ความหมาย |
|---|---|
| ` ```bash ` | คำสั่งที่ต้อง **พิมพ์เอง** ในเครื่องเรียน |
| 📝 **คำอธิบาย** | คำสั่งนั้นทำอะไร แต่ละ flag แปลว่าอะไร และให้สังเกตอะไร |
| ✅ **Expected output** | ผลลัพธ์ที่ควรได้ **ถ้าทำถูก** — ถ้าได้ไม่ตรง แปลว่าพลาดบางขั้น ให้ย้อนกลับไปดู |

> **ตัวเลขที่ไม่ต้องตรงกันก็ได้** — CONTAINER ID, IMAGE ID, digest `sha256:…`, วันเวลา และเวลาที่ใช้ build
> ของแต่ละคนจะไม่เหมือนในเอกสาร ให้ดูที่ **รูปแบบและสถานะ** (เช่น `Up`, `Exited (0)`, `200 OK`) เป็นหลัก

---

Happy Learning!
