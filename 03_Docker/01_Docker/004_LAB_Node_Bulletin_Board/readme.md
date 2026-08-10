# LAB 4 — Build Docker Image เอง (Node.js Bulletin Board)

> โฟลเดอร์ `004_LAB_Node_Bulletin_Board` = **LAB 4** ในสไลด์ `Docker_Week08_Slides.html`

## สิ่งที่จะได้เรียนรู้

- อ่าน `Dockerfile` ทีละบรรทัด
- `docker build` สร้าง image ของตัวเองจากซอร์สโค้ด
- **Layer cache** — ทำไมต้อง `COPY package.json` ก่อน `COPY . .`

---

## 0. เตรียมเครื่องเรียน

```bash
docker rm -f devtools
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> ใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บทั้งหมดข้างใน

เช็กว่า Docker ในเครื่องเรียนพร้อมใช้งาน :

```bash
docker --version
```

```
Docker version 29.6.2, build dfc4efb
```

---

## 1. เข้าโฟลเดอร์แอป

ถ้ายังไม่เคย clone รีโพ ให้ clone ก่อน (ทำครั้งเดียว ใช้ได้ทุกแล็บ) :

```bash
mkdir -p ~/labwork ; cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
```

```bash
cd ~/labwork
cd DevTools/03_Docker/01_Docker/004_LAB_Node_Bulletin_Board/bulletin-board-app
ls
```

```
Dockerfile  LICENSE  app.js  backend  fonts  index.html  package.json  server.js  site.css
```

---

## 2. อ่าน Dockerfile

```dockerfile
FROM node:current-slim          # 1. เลือก base image (Node.js รุ่นเล็ก)

WORKDIR /usr/src/app            # 2. กำหนด working directory ในกล่อง
COPY package.json .             # 3. คัดลอกเฉพาะ package.json เข้ามาก่อน
RUN npm install                 # 4. ติดตั้ง dependencies

EXPOSE 8080                     # 5. ประกาศว่า container ฟังที่ port 8080
CMD [ "npm", "start" ]          # 6. คำสั่งที่รันเมื่อ container เริ่มทำงาน

COPY . .                        # 7. คัดลอกซอร์สโค้ดที่เหลือทั้งหมด
```

> **EXPOSE ไม่ได้เปิด port ให้จริง** — เป็นเพียงการประกาศเจตนา การเปิดจริงต้องใช้ `-p` ตอน `docker run`

> **ข้อสังเกต :** ไฟล์นี้วาง `COPY . .` ไว้หลัง `CMD` ซึ่งยังทำงานได้ปกติ (เพราะ `CMD` เป็นแค่การประกาศ ไม่ใช่การรันตอน build) แต่ตามธรรมเนียมที่ดีควรวางไว้ก่อน `EXPOSE`/`CMD`

---

## 3. Build image

```bash
docker build -t bulletinboard:1.0 .
```

ผลรันจริง (ย่อ) :

```
#1 [internal] load build definition from Dockerfile   transferring dockerfile: 164B   DONE 0.1s
#2 [internal] load metadata for docker.io/library/node:current-slim                   DONE 2.4s
#4 [internal] load .dockerignore                                                      DONE 0.0s
#5 [internal] load build context      transferring context: 31.91kB                   DONE 0.1s
#6 [1/5] FROM docker.io/library/node:current-slim@sha256:4ebb5ace66f1...              DONE 24.2s
#7 [2/5] WORKDIR /usr/src/app                                                         DONE 0.1s
#8 [3/5] COPY package.json .                                                          DONE 0.1s
#9 [4/5] RUN npm install
#9 6.700 added 115 packages, and audited 116 packages in 6s                           DONE 6.8s
#10 [5/5] COPY . .                                                                    DONE 0.1s
#11 naming to docker.io/library/bulletinboard:1.0 done                                DONE 1.3s

real    0m35.518s
```

`[1/5]` … `[5/5]` คือคำสั่งใน Dockerfile ที่ **สร้าง layer** — `EXPOSE` และ `CMD` ไม่นับ เพราะเป็นแค่ metadata

ขั้นที่กินเวลาที่สุดคือ `FROM` ที่ต้องโหลด base image (**24.2 วินาที**) และ `RUN npm install` (**6.8 วินาที**) — รวมทั้ง build **35.5 วินาที** จำตัวเลขนี้ไว้ แล้วดูข้อ 6

---

## 4. รัน container จาก image ที่เพิ่ง build

```bash
docker run -p 8085:8080 -d --name bb bulletinboard:1.0
```

```
b683cbce27c3b5166875f3d11443c35d7d8a029177e52b7cd8b0d7abbd62f90e
```

```bash
docker images
```

```
IMAGE               ID             DISK USAGE   CONTENT SIZE   EXTRA
bulletinboard:1.0   8aea598d47d9        399MB           94MB   U
```

```bash
docker ps
```

```
CONTAINER ID   IMAGE               COMMAND                  CREATED         STATUS         PORTS                                         NAMES
b683cbce27c3   bulletinboard:1.0   "docker-entrypoint.s…"   9 seconds ago   Up 8 seconds   0.0.0.0:8085->8080/tcp, [::]:8085->8080/tcp   bb
```

```bash
docker logs bb
```

```
> vue-event-bulletin@1.0.0 start
> node server.js

Magic happens on port 8080...
```

> หน้าเว็บไม่ขึ้น? ดู `docker logs bb` ก่อนเสมอ

---

## 5. ทดสอบแอป

```bash
curl -s http://localhost:8085 | head -30
```

```html
<title>Bulletin Board</title>
<h1>Welcome to the Bulletin Board</h1>
```

```bash
curl -s http://localhost:8085/api/events
```

```json
[{"id":1,"title":"Docker Workshop","detail":"Linuxing in London ","date":"2017-11-21"},
 {"id":2,"title":"WinOps #17","detail":"WinOps London","date":"2017-11-21"},
 {"id":3,"title":"Docker London","date":"2017-11-13"}]
```

```bash
docker exec bb sh -c "node -v; pwd; ls"
```

```
v26.7.0
/usr/src/app
Dockerfile  LICENSE  app.js  backend  fonts  index.html
node_modules  package-lock.json  package.json  server.js  site.css
```

`node_modules` ถูกสร้างขึ้น **ในกล่อง** ตอน `RUN npm install` — ไม่ได้ก๊อปมาจากเครื่องเรา

เปิดดูในเบราว์เซอร์ — ให้ VS Code forward port ของแล็บนี้ออกมาก่อน :
แท็บ **PORTS** → **Forward a Port** → พิมพ์ `8085` → เปิด `http://localhost:8085`
(ขั้นตอนเหมือนภาพด้านล่าง — แล็บนี้ใช้เลข **8085**)

![วิธี forward port ใน VS Code](./images/vscode-port-forward.png)

ทางเลือก : forward ด้วยคำสั่ง `ssh -L` จาก terminal บนเครื่องเรา — **ssh เข้าไปยัง port ภายในเครื่องเรียน** โดยตรง :

```bash
ssh -L 8085:localhost:8085 root@localhost -p 2222        # password : passwd
```

> **ทดลองเสร็จแล้ว ลบ tunnel ทุกครั้ง** — แบบ `ssh -L` พิมพ์ `exit` / กด `Ctrl+D` ·
> แบบ VS Code คลิกขวาที่ port ในแท็บ **PORTS** → **Stop Forwarding Port**

![Bulletin Board](./images/bulletinboard-8085.png)

---

## 6. พิสูจน์ Layer Cache

แก้เฉพาะซอร์สโค้ด **ไม่แตะ `package.json`** แล้ว build ใหม่ :

```bash
sed -i 's/Welcome to the Bulletin Board/Welcome to the Bulletin Board v1.1/' index.html
docker build -t bulletinboard:1.1 .
```

```
#5 [1/5] FROM docker.io/library/node:current-slim@sha256:4ebb5ace...   DONE 0.0s
#6 [2/5] WORKDIR /usr/src/app       CACHED
#7 [3/5] COPY package.json .        CACHED
#8 [4/5] RUN npm install            CACHED      <- ประหยัดไป 6.8 วินาที
#9 [5/5] COPY . .                                            DONE 0.1s
#10 naming to docker.io/library/bulletinboard:1.1 done       DONE 0.3s

real    0m1.730s
```

build รอบแรกใช้เวลา **35.518 วินาที** (ต้องโหลด base image + `npm install`)
build รอบสองเหลือ **1.730 วินาที** (เร็วขึ้น ~20 เท่า) — มีแค่ `COPY . .` ที่รันใหม่ เพราะ `index.html` เปลี่ยน

| เขียนแบบ | ผลที่ได้ |
|---|---|
| `COPY . .` ก่อน `RUN npm install` | แก้โค้ดตัวอักษรเดียว → cache หลุดหมด → `npm install` รันใหม่ทุกครั้ง |
| `COPY package.json` ก่อน (แบบนี้) | `package.json` ไม่เปลี่ยน → `npm install` **CACHED** ตลอด |

> **กฎง่าย ๆ :** สิ่งที่เปลี่ยนน้อยที่สุดไว้บนสุดของ Dockerfile · สิ่งที่เปลี่ยนบ่อยที่สุดไว้ล่างสุด

---

## 7. คำสั่งที่ใช้บ่อยหลัง build

```bash
docker logs -f bb                 # ตามดู log สด ๆ
docker exec -it bb sh             # เข้าไปใน shell ของกล่อง
docker stop bb                    # หยุด
docker rm bb                      # ลบ container
docker rmi bulletinboard:1.0      # ลบ image
```

เก็บกวาดท้ายแล็บ :

```bash
docker rm -f bb
```

```
bb
```

---

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1` เมื่อ 10 ส.ค. 2026*
