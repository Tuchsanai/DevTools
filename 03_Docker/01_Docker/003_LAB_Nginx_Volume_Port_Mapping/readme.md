# LAB 3 — Nginx + Volume Mapping + Port Mapping

> โฟลเดอร์ `003_LAB_Nginx_Volume_Port_Mapping` = **LAB 3** ในสไลด์ `Docker_Week08_Slides.html`

## สิ่งที่จะได้เรียนรู้

- เห็นปัญหาจริงก่อน : **ลบ container = ข้อมูลข้างในหายทั้งหมด**
- `-v HOST_PATH:CONTAINER_PATH` เอาโฟลเดอร์บนเครื่องเราไปวางในกล่อง
- แก้ไฟล์บนเครื่อง → เว็บในกล่องเปลี่ยนทันที **โดยไม่ต้อง restart**
- `:ro` (read-only) ป้องกัน container เขียนทับไฟล์ของเรา
- ลบ container แล้ว **ข้อมูลไม่หาย** เพราะไฟล์อยู่บนดิสก์ของเราตลอด

---

## 0. เตรียมเครื่องเรียน

```bash
docker rm -f devtools
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> ใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บทั้งหมดข้างใน

ตรวจว่า Docker ในเครื่องเรียนพร้อมใช้ :

```bash
docker --version
docker compose version
```

```
Docker version 29.6.2, build dfc4efb
Docker Compose version v5.3.1
```

---

## 1. ปัญหา : ลบ container = ข้อมูลหาย

ก่อนจะรู้จัก volume มาดูปัญหากันก่อน — เขียนไฟล์ลงใน container แล้วลบ container ทิ้ง
ดูว่าเกิดอะไรขึ้น

### 1.1 สร้างกล่อง แล้วเขียนไฟล์ลงไปข้างใน

```bash
docker run -d --name box1 nginx
```

```
Unable to find image 'nginx:latest' locally
latest: Pulling from library/nginx
26c307b5e35a: Pull complete
        ... (รวม 7 layer) ...
Digest: sha256:8541484afbc9c8a5a8a99b379568ebbc957f658583ec9448fc43104229c03cf8
Status: Downloaded newer image for nginx:latest
17ed126bec8fd0ad3128d1e4d10d4138bebab01bceec68eb07135c36b73699fc
```

(ครั้งแรก Docker จะ pull image `nginx` ให้อัตโนมัติ — รันครั้งต่อไปจะไม่เห็นบรรทัด pull อีก)

```bash
docker exec box1 sh -c "echo ข้อมูลสำคัญของเรา > /note.txt"
docker exec box1 cat /note.txt
```

```
ข้อมูลสำคัญของเรา
```

ไฟล์อยู่ครบ — เขียนได้ อ่านได้ ปกติทุกอย่าง

### 1.2 ลบกล่องทิ้ง แล้วสร้างกล่องใหม่จาก image เดิม

```bash
docker rm -f box1
docker run -d --name box2 nginx
docker exec box2 cat /note.txt
```

```
cat: /note.txt: No such file or directory
```

exit code = **1** — ไฟล์หายไปพร้อมกับ `box1` แม้ `box2` จะสร้างจาก image เดียวกันก็ตาม

| เกิดอะไรขึ้น | ทางแก้ : Volume Mapping |
|---|---|
| ทุกอย่างที่เขียนลงไป**ในกล่อง** อยู่บนชั้นชั่วคราวของกล่องนั้น — **ลบกล่อง = ลบข้อมูล** ถ้าเป็นฐานข้อมูล ก็คือข้อมูลลูกค้าหายทั้งหมด | ผูกโฟลเดอร์จริง**บนเครื่องเรา**เข้ากับ path ในกล่อง → ข้อมูลถูกเขียนลงดิสก์ของเรา ไม่ได้อยู่ในกล่อง **ลบกล่องกี่รอบก็ไม่หาย** |

เก็บกวาดก่อนไปต่อ :

```bash
docker rm -f box2
```

---

## 2. เข้าโฟลเดอร์ของแล็บ

ถ้ายังไม่เคย clone รีโพ ให้ clone ก่อน (ทำครั้งเดียว ใช้ได้ทุกแล็บ) :

```bash
mkdir -p ~/labwork ; cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Docker/01_Docker/003_LAB_Nginx_Volume_Port_Mapping
ls -l web_demo
```

```
total 16
-rwxr-xr-x 1 root root 12316 Aug 10 23:12 index.html
```

`web_demo/index.html` คือหน้าเว็บของเราเอง (ใช้ **Tailwind CSS** ผ่าน CDN + มีนาฬิกา ปุ่มสลับโหมดมืด
และเอฟเฟกต์เล็ก ๆ) ที่จะเอาไปวางแทนหน้า default ของ Nginx

---

## 3. รัน Nginx พร้อม Volume + Port Mapping

```bash
docker run -d -p 8083:80 -v ${PWD}/web_demo:/usr/share/nginx/html:ro nginx
```

```
36a238b74a8aed07eab7036d7078186ba064f710556c37cb8a01a3667dcc714e
```

| ส่วนของคำสั่ง | ความหมาย |
|---|---|
| `-d` | รันเบื้องหลัง คืน prompt ให้ทันที |
| `-p 8083:80` | port 8083 ของเครื่องเรา → port 80 ในกล่อง |
| `-v ${PWD}/web_demo:/usr/share/nginx/html` | เอาโฟลเดอร์ `web_demo` ไปวางแทน web root ของ Nginx |
| `:ro` | กล่อง **อ่านได้อย่างเดียว เขียนไม่ได้** |

รูปแบบเต็มของ `-v` คือ `-v <HOST_PATH>:<CONTAINER_PATH>[:ro]` — `HOST_PATH` ต้องเป็น
absolute path (ใช้ `${PWD}` ช่วยได้) และของเดิมใน `CONTAINER_PATH` จะถูก **บังทับ**
ด้วยโฟลเดอร์จาก host ทั้งหมด ไม่ใช่การรวมกัน

ในขั้นตอนถัด ๆ ไป ให้แทน `<container>` ด้วย container ID ที่ได้จากคำสั่งนี้
(ใช้ตัวย่อได้ เช่น `36a238b74a8a` หรือดูจาก `docker ps`)

---

## 4. ทดสอบว่าได้หน้าเว็บของเรา ไม่ใช่หน้า default

```bash
curl -s http://localhost:8083 | grep -o "Welcome to Demo nginx Website"
```

```
Welcome to Demo nginx Website
```

เปิดดูในเบราว์เซอร์ — ให้ VS Code forward port ของแล็บนี้ออกมาก่อน :
แท็บ **PORTS** → **Forward a Port** → พิมพ์ `8083` → เปิด `http://localhost:8083`
(ขั้นตอนเหมือนภาพด้านล่าง — แล็บนี้ใช้เลข **8083**)

![วิธี forward port ใน VS Code](./images/vscode-port-forward.png)

ทางเลือก : forward ด้วยคำสั่ง `ssh -L` จาก terminal บนเครื่องเรา — **ssh เข้าไปยัง port ภายในเครื่องเรียน** โดยตรง :

```bash
ssh -L 8083:localhost:8083 root@localhost -p 2222        # password : passwd
```

> **ทดลองเสร็จแล้ว ลบ tunnel ทุกครั้ง** — แบบ `ssh -L` พิมพ์ `exit` / กด `Ctrl+D` ·
> แบบ VS Code คลิกขวาที่ port ในแท็บ **PORTS** → **Stop Forwarding Port**

![ก่อนแก้ — หน้าเว็บจาก web_demo ผ่าน volume](./images/volume-8083-before.png)

*ก่อนแก้ : หัวข้อยังเป็น "Welcome to Demo nginx Website" — เป็นหน้าเว็บของเราเอง ไม่ใช่หน้า "Welcome to nginx!" ของ image*

### พิสูจน์ว่า web root ถูกแทนที่จริง

```bash
docker exec <container> ls -l /usr/share/nginx/html
```

```
total 16
-rwxr-xr-x 1 root root 12316 Aug 10 16:12 index.html
```

เทียบกับ nginx ที่ **ไม่ได้** ผูก volume :

```bash
docker run --rm nginx ls -l /usr/share/nginx/html
```

```
total 8
-rw-r--r-- 1 root root 497 Jul 15 16:03 50x.html
-rw-r--r-- 1 root root 896 Jul 15 16:03 index.html
```

ของเดิมใน `CONTAINER_PATH` ถูก **บังทับทั้งหมด** ไม่ใช่การรวมกัน — ไม่มี `50x.html`
ของ nginx เหลืออยู่ เหลือแค่ไฟล์ของเรา

---

## 5. แก้ไฟล์บนเครื่อง → เห็นผลทันที

แก้หัวข้อในไฟล์บนเครื่องเรียน (ไม่แตะ container เลย) :

```bash
sed -i "s|Welcome to Demo nginx Website|สวัสดี Docker|" web_demo/index.html
curl -s http://localhost:8083 | grep -o "สวัสดี Docker"
```

```
สวัสดี Docker
```

**ไม่ได้ restart container เลยสักครั้ง** — นี่คือประโยชน์หลักของ volume ในงาน development

รีเฟรชเบราว์เซอร์ :

![หลังแก้ — หัวข้อเปลี่ยนเป็น สวัสดี Docker](./images/volume-8083-after.png)

*หลังแก้ : หัวข้อด้านบนเปลี่ยนเป็น "สวัสดี Docker" ทันทีที่รีเฟรช — แก้โค้ดบนเครื่อง เห็นผลในกล่องทันที ไม่ต้อง build ใหม่*

---

## 6. พิสูจน์ `:ro`

```bash
docker exec <container> sh -c "echo test >> /usr/share/nginx/html/index.html"
```

```
sh: 1: cannot create /usr/share/nginx/html/index.html: Read-only file system
```

exit code = **2** — container เขียนทับไฟล์ต้นฉบับของเราไม่ได้จริง
ถ้าแอปในกล่องถูกเจาะ หรือเขียนไฟล์มั่ว ก็แก้ไฟล์ต้นฉบับบนเครื่องเราไม่ได้

---

## 7. พิสูจน์ว่าข้อมูลอยู่รอด

```bash
docker rm -f <container>
ls -l web_demo/index.html
grep -o "สวัสดี Docker" web_demo/index.html
```

```
36a238b74a8a
-rwxr-xr-x 1 root root 12312 Aug 10 23:18 web_demo/index.html
สวัสดี Docker
```

ลบกล่องกี่รอบ ไฟล์ก็ยังอยู่ครบ (ข้อความที่แก้เป็น "สวัสดี Docker" ก็ยังอยู่)
เพราะไฟล์อยู่บน **ดิสก์ของเครื่องเรา** ตลอด กล่องแค่ "มอง" เข้าไป —
ต่างจาก `box1` ในข้อ 1 ที่เขียนไฟล์ลงในกล่องแล้วหายไปพร้อมกล่อง

---

## สรุป

| ใช้ทำอะไร | ตัวอย่าง |
|---|---|
| เก็บข้อมูลถาวร | ฐานข้อมูล — ลบ container แล้วข้อมูลไม่หาย |
| ใส่ไฟล์เข้าไปในกล่อง | โค้ด / หน้าเว็บ ตอนพัฒนา — แก้แล้วเห็นผลทันที |

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` เมื่อ 10 ส.ค. 2026*
