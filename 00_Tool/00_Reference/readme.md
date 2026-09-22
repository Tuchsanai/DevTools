# DevTools Base Learning Container

Container พื้นฐานสำหรับ DevTools labs — Ubuntu 24.04 ที่มาพร้อม **Docker-in-Docker**, **Python 3**,
**Node.js 22 (LTS)**, **JupyterLab** และ **SSH** ใช้งานได้ทันที

---

## สิ่งที่อยู่ใน image

| หมวด | รายละเอียด |
|------|------------|
| **Base** | Ubuntu 24.04, timezone `Asia/Bangkok`, locale UTF-8 |
| **Docker-in-Docker** | docker-ce, CLI, containerd, buildx & compose plugins |
| **Python** | python3, pip, venv (`python` → `python3`) |
| **Node.js** | Node.js 22.x LTS + npm/npx (สำหรับ Next.js / React / Vite) |
| **JupyterLab** | JupyterLab 4.x + extensions (ดูหัวข้อ 3.4) — kernel `python3` และ `bash` |
| **Tooling** | git, curl, wget, vim, nano, less, net-tools, ping, dnsutils, openssh-server |
| **Workdir** | `/workspace` |
| **Ports** | `22` (SSH), `8888` (JupyterLab) |
| **SSH login** | user `root` / password `passwd` (เปิด PasswordAuthentication + PermitRootLogin) |
| **JupyterLab login** | ไม่มีรหัสผ่าน (ตั้งได้ด้วย `-e JUPYTER_PASSWORD=...`) |

> หมายเหตุ: container รันเป็น `root` (ไม่มี user `student` แล้ว)

> ⚠️ รหัสผ่าน SSH ของ `root` คือ `passwd` และ JupyterLab เปิดแบบไม่มีรหัสผ่าน — ใช้สำหรับการเรียน/ทดสอบบนเครื่องตัวเองเท่านั้น ไม่ควรเปิดพอร์ตออก internet

> 💡 ทุกคำสั่งในเอกสารนี้เป็น **บรรทัดเดียว** copy-paste ได้ทั้ง Windows และ Linux/macOS

---

## 1. Build container แบบ local

build จาก `Dockerfile` ในโฟลเดอร์นี้ แล้วตั้งชื่อ image เป็น `devtools:2569_1`

```bash
# อยู่ในโฟลเดอร์ที่มี Dockerfile
cd 00_Tool/base-learning-container

# build เป็น image ชื่อ devtools tag 2569_1
docker build -t devtools:2569_1 .
```

ตรวจสอบว่า build สำเร็จ:

```bash
docker images devtools
# REPOSITORY   TAG       IMAGE ID       CREATED         SIZE
# devtools     2569_1    xxxxxxxxxxxx   x seconds ago   xxxMB
```

### build ใหม่โดยไม่ใช้ cache (ถ้าต้องการ)

```bash
docker build --no-cache -t devtools:2569_1 .
```

---

## 2. Run container

ต้องใช้ `--privileged` เพราะข้างในรัน Docker daemon (Docker-in-Docker)
คำสั่งนี้เป็นบรรทัดเดียว copy-paste ได้ทั้ง **Windows และ Linux/macOS**

```bash
docker run -d --name devtools --privileged -p 2222:22 -p 8888:8888 devtools:2569_1
```

| Flag | ความหมาย |
|------|----------|
| `-d` | รันแบบ background (detached) |
| `--name devtools` | ตั้งชื่อ container |
| `--privileged` | จำเป็นสำหรับ Docker-in-Docker ให้ `dockerd` ทำงานได้ |
| `-p 2222:22` | map SSH port ออกมาที่เครื่อง host พอร์ต 2222 |
| `-p 8888:8888` | map JupyterLab ออกมาที่ host พอร์ต 8888 |
| `-e JUPYTER_PASSWORD=xxx` | (optional) ตั้งรหัสผ่าน JupyterLab (ค่าเริ่มต้นไม่มีรหัสผ่าน) |

### 2.1 รันด้วย Docker Compose (แนะนำ)

ใช้ `docker-compose.yml` ในโฟลเดอร์นี้ — ตั้งค่า privileged, พอร์ต, รหัสผ่าน และ volume ให้ครบแล้ว

```bash
docker compose up -d            # ใช้ image จาก Docker Hub
docker compose up -d --build    # หรือ build จาก Dockerfile ในโฟลเดอร์นี้
docker compose logs -f          # ดู log (sshd / dockerd / jupyter)
docker compose down             # หยุดและลบ container (ไฟล์ใน ./workspace ยังอยู่)
```

| สิ่งที่ compose ตั้งให้ | รายละเอียด |
|------|----------|
| `privileged: true` + `stdin_open/tty` | เหมือน `docker run -dit --privileged` |
| `env_file: /root/workspace/DGX_2024/.env` | โหลด credential ส่วนตัวเข้า container (ดูหัวข้อ 2.2; ไม่มีไฟล์ก็รันได้) |
| `./workspace:/workspace` | งานของนักศึกษาอยู่บนเครื่อง host ไม่หายเมื่อ `down` |
| `devtools-dind:/var/lib/docker` | named volume เก็บ image/container ของ Docker-in-Docker |
| `restart: unless-stopped` | เปิดเครื่องใหม่แล้ว container กลับมาเอง |

ปรับค่าได้ผ่าน environment หรือไฟล์ `.env` ข้าง `docker-compose.yml` (ทุกค่ามี default):

```bash
# .env
SSH_PORT=2222
JUPYTER_PORT=8888
JUPYTER_PASSWORD=          # ว่าง = ไม่มีรหัสผ่าน
```

### 2.2 โหลด credential จาก `/root/workspace/DGX_2024/.env`

`docker-compose.yml` กำหนด `env_file: /root/workspace/DGX_2024/.env` (`required: false`) — ทุกตัวแปรในไฟล์นี้
(เช่น `HF_TOKEN`, `GITHUB_TOKEN`, `DOCKER_USER` / `DOCKER_TOKEN`, `GIT_USER_NAME` / `GIT_USER_EMAIL`, `VAST_API_KEY`)
จะถูก inject เป็น environment ของ container ตอน `docker compose up`

```bash
docker compose up -d
docker exec devtools printenv HF_TOKEN      # ตรวจว่าโหลดแล้ว
```

| ที่ไหนเห็นตัวแปร | เห็นไหม |
|------|------|
| Terminal / kernel ใน JupyterLab, `docker exec` | ✅ สืบทอดจาก environment ของ container |
| SSH session (`ssh root@localhost -p 2222`) | ❌ sshd ไม่ส่ง env ของ container ให้ shell — ใช้ `set -a; . /root/workspace/DGX_2024/.env; set +a` หรือ mount ไฟล์เข้ามาเอง |

> * ถ้าไม่มีไฟล์นี้ (เช่นบนเครื่องอื่น) compose ยังรันได้ตามปกติเพราะตั้ง `required: false`
> * `env_file` ใช้กับ **environment ของ container** เท่านั้น — ค่า `SSH_PORT` / `JUPYTER_PORT` / `JUPYTER_PASSWORD` ที่ใช้ map พอร์ต
>   ยังอ่านจาก shell หรือ `.env` ข้าง `docker-compose.yml` ถ้าอยากใช้ไฟล์เดียวกันให้รัน `docker compose --env-file /root/workspace/DGX_2024/.env up -d`
> * `JUPYTER_TOKEN` ในไฟล์นี้ **ไม่มีผล** กับ JupyterLab เพราะ `/etc/jupyter/jupyter_server_config.py` ตั้ง `token = ""` ไว้แล้ว (ใช้ `JUPYTER_PASSWORD` แทนถ้าต้องการรหัสผ่าน)
> * ไฟล์นี้เป็น credential ส่วนตัว — อย่า commit และอย่า `docker commit` container ที่โหลดไว้

---

## 3. เข้าใช้งาน container

### เข้าผ่าน shell โดยตรง

```bash
docker exec -it devtools bash
```

### เข้าผ่าน SSH

login ด้วย user `root` รหัสผ่าน `passwd`

```bash
ssh root@localhost -p 2222
# password: passwd
```

### ทดสอบว่า Docker-in-Docker ทำงาน

```bash
docker exec -it devtools docker run --rm hello-world
```

### 3.4 เข้าใช้งาน JupyterLab

เปิดเบราว์เซอร์ที่ <http://localhost:8888> เข้าได้เลยไม่ต้องใส่รหัสผ่าน — file browser เริ่มที่ `/` (root ของ container) จึงเห็นทุกโฟลเดอร์ งานของ lab อยู่ที่ `/workspace`

file browser **แสดง hidden file / folder** (ชื่อขึ้นต้นด้วย `.` เช่น `.env`, `.git`, `.gitignore`, `.github/`) เป็นค่าเริ่มต้น
เปิดไว้สองฝั่ง: server `c.ContentsManager.allow_hidden = True` และ UI `showHiddenFiles: true` — ถ้าอยากซ่อนชั่วคราวให้ติ๊กออกที่เมนู *View → Show Hidden Files*

| Extension | ใช้ทำอะไร |
|-----------|-----------|
| **Terminal** (built-in) | bash login shell — copy/paste ได้ตามตารางด้านล่าง |
| **jupytext** | เปิดไฟล์ `.py` / `.md` เป็น notebook, pair notebook ↔ script (คลิกขวาไฟล์ → *Open With*) |
| **jupyterlab-git** | Git UI ใน sidebar ซ้าย (stage / commit / diff / branch) |
| **jupyterlab-lsp** + `python-lsp-server` | autocomplete, hover, go-to-definition, lint สำหรับ Python |
| **jupyterlab-code-formatter** (black, isort) | จัดรูปแบบโค้ดใน cell / ไฟล์ |
| **jupyterlab-execute-time** | แสดงเวลาที่ใช้รันของแต่ละ cell |
| **jupyter-resource-usage** | แสดง CPU / Memory ที่ status bar |
| **ipywidgets** | interactive widgets |
| **bash_kernel** | เขียน notebook ด้วย Bash kernel (เหมาะกับ lab คำสั่ง shell / docker) |

**Copy / Paste ใน Terminal ของ JupyterLab**

| การกระทำ | คีย์ |
|----------|------|
| Paste | `Ctrl+V` หรือ `Shift+Insert` หรือ `Ctrl+Shift+V` หรือคลิกขวา → *Paste* |
| Copy (เมื่อเลือกข้อความอยู่) | `Ctrl+C` หรือ `Ctrl+Insert` หรือ `Ctrl+Shift+C` หรือคลิกขวา → *Copy* |
| ส่ง SIGINT (หยุดโปรเซส) | `Ctrl+C` เมื่อ **ไม่ได้** เลือกข้อความ |

> การ copy/paste ผ่านคลิกขวาและ `Ctrl+Shift+C/V` ใช้ Clipboard API ของเบราว์เซอร์ ซึ่งทำงานเฉพาะบน `localhost` หรือ `https://`
> ถ้าเข้าผ่าน `http://<ip>` ให้ใช้ `Ctrl+V` / `Shift+Insert` และเลือกข้อความแล้ว `Ctrl+C` แทน (ทำงานได้ทุกกรณี)

ไฟล์ที่เกี่ยวข้องใน image:

| ไฟล์ | หน้าที่ |
|------|--------|
| `/etc/jupyter/jupyter_server_config.py` | ค่า server: ip/port, root_dir = `/`, allow_root, `allow_hidden` (เห็น hidden file), terminal = `bash -l`, ปิด token |
| `/usr/local/share/jupyter/lab/settings/overrides.json` | ค่าเริ่มต้น UI: file browser `showHiddenFiles`, terminal `pasteWithCtrlV`, shortcut copy/paste, ปิด news/update check |
| `/usr/local/bin/start.sh` | entrypoint: sshd + dockerd + jupyter lab (ไม่มีรหัสผ่าน เว้นแต่ตั้ง `$JUPYTER_PASSWORD`) |
| `/var/log/jupyter.log` | log ของ JupyterLab |

---

## 4. คำสั่งที่ใช้บ่อย

```bash
# ดู log การ start (sshd / dockerd / jupyter)
docker logs devtools
docker exec devtools tail -f /var/log/jupyter.log

# หยุด container
docker stop devtools

# เริ่มใหม่
docker start devtools

# ลบ container
docker rm -f devtools

# ลบ image
docker rmi devtools:2569_1
```

---

## 5. Build & Tag สำหรับ push ขึ้น Docker Hub (optional)

ถ้าจะ push ขึ้น registry ให้ tag ด้วยชื่อ `<user>/<repo>:<tag>`

```bash
# tag จาก local image ไปเป็นชื่อบน Docker Hub
docker tag devtools:2569_1 tuchsanai/devtools:2569_1
docker tag devtools:2569_1 tuchsanai/devtools:latest

# login แล้ว push
docker login -u tuchsanai
docker push tuchsanai/devtools:2569_1
docker push tuchsanai/devtools:latest
```

---

## 6. ดึง image จาก Docker Hub (ใช้ image สำเร็จรูป)

image ถูก publish ไว้แล้วที่ [`tuchsanai/devtools`](https://hub.docker.com/r/tuchsanai/devtools) — ไม่ต้อง build เองก็ได้
ทุกคำสั่งเป็นบรรทัดเดียว copy-paste ได้ทั้ง **Windows และ Linux/macOS**

```bash
docker pull tuchsanai/devtools:2569_1

docker run -dit --name devtools --privileged -p 2222:22 -p 8888:8888 tuchsanai/devtools:2569_1
```
