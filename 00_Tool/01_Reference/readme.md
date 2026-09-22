# DevTools Base Learning Container

Container พื้นฐานสำหรับ DevTools labs — **Ubuntu 26.04 LTS** ที่มาพร้อม **Docker-in-Docker**,
**Python 3 + uv**, **Node.js 24 (LTS)**, **git ล่าสุด + gh** และ **SSH** ใช้งานได้ทันที

---

## สิ่งที่อยู่ใน image

| หมวด | รายละเอียด |
|------|------------|
| **Base** | Ubuntu 26.04 LTS (resolute), timezone `Asia/Bangkok`, locale UTF-8 |
| **Docker-in-Docker** | docker-ce 29.x, CLI, containerd, buildx & compose plugins |
| **Git** | git ล่าสุดจาก `git-core` PPA + `git-lfs` + GitHub CLI (`gh`) |
| **Python** | python3, pip, venv พร้อมใช้ที่ `/opt/venv` + [`uv`](https://docs.astral.sh/uv/) |
| **Node.js** | Node.js 24.x LTS + npm + corepack (`pnpm` / `yarn` เปิดใช้ได้ทันที) |
| **Tooling** | curl, wget, jq, ripgrep, tree, htop, tmux, rsync, unzip, build-essential, net-tools, ping, dnsutils, openssh |
| **Init** | `tini` เป็น PID 1 (reap zombie + `docker stop` ปิดสะอาด) |
| **Workdir** | `/workspace` |
| **Ports** | `22` (SSH) |
| **SSH login** | user `root` / password `passwd` |

> หมายเหตุ: container รันเป็น `root`

> ⚠️ รหัสผ่าน SSH ของ `root` คือ `passwd` และฝังอยู่ใน image (อ่านได้จาก `docker history`)
> — ใช้สำหรับการเรียน/ทดสอบเท่านั้น **ห้ามใช้ใน production**

> 💡 ทุกคำสั่งในเอกสารนี้เป็น **บรรทัดเดียว** copy-paste ได้ทั้ง Windows และ Linux/macOS

---

## 1. Build container แบบ local

Dockerfile ใช้ฟีเจอร์ BuildKit (`--mount=type=cache`, heredoc) ซึ่งเป็น default ของ Docker 23+ อยู่แล้ว
ไม่ต้องตั้งค่าอะไรเพิ่ม

```bash
# อยู่ในโฟลเดอร์ที่มี Dockerfile
docker build -t devtools:2569_2 .
```

ตรวจสอบว่า build สำเร็จ:

```bash
docker images devtools
```

### เปลี่ยนเวอร์ชันตอน build (optional)

ทุกเวอร์ชันถูกทำเป็น `ARG` ปรับได้โดยไม่ต้องแก้ไฟล์

```bash
# ย้อนกลับไปใช้ Ubuntu 24.04 + Node 22
docker build --build-arg UBUNTU_VERSION=24.04 --build-arg NODE_MAJOR=22 -t devtools:2569_1 .

# เปลี่ยนรหัสผ่าน root
docker build --build-arg ROOT_PASSWORD=mysecret -t devtools:2569_2 .
```

| ARG | ค่า default |
|-----|-------------|
| `UBUNTU_VERSION` | `26.04` |
| `NODE_MAJOR` | `24` |
| `TZ` | `Asia/Bangkok` |
| `ROOT_PASSWORD` | `passwd` |

### build ใหม่โดยไม่ใช้ cache

```bash
docker build --no-cache -t devtools:2569_2 .
```

---

## 2. Run container

ต้องใช้ `--privileged` เพราะข้างในรัน Docker daemon (Docker-in-Docker)

```bash
docker run -d --name devtools --privileged -p 2222:22 devtools:2569_2
```

| Flag | ความหมาย |
|------|----------|
| `-d` | รันแบบ background (detached) |
| `--name devtools` | ตั้งชื่อ container |
| `--privileged` | **จำเป็น** สำหรับ Docker-in-Docker ให้ `dockerd` ทำงานได้ |
| `-p 2222:22` | map SSH port ออกมาที่เครื่อง host พอร์ต 2222 |

entrypoint จะ **รอจนกว่า `dockerd` จะพร้อมจริง** ก่อนส่งต่อให้ shell
ถ้าลืมใส่ `--privileged` container จะหยุดพร้อมข้อความบอกสาเหตุใน `docker logs` ทันที
(ไม่ใช่เงียบ ๆ แล้วไปเจอตอนสั่ง `docker ps` ข้างใน)

รองรับทั้ง 3 รูปแบบการรัน:

```bash
docker run -d  --privileged --name devtools devtools:2569_2   # background — ค้างไว้ แล้ว docker exec เข้าไป
docker run -it --privileged --name devtools devtools:2569_2   # interactive — ได้ bash ทันที
docker run --rm --privileged devtools:2569_2 node -v          # สั่งคำสั่งเดียวแล้วจบ
```

### ตัวแปรควบคุม runtime

| ENV | default | ความหมาย |
|-----|---------|----------|
| `START_DOCKERD` | `1` | ตั้ง `0` เพื่อไม่ start dockerd (ใช้ตอนอยาก mount docker.sock ของ host แทน) |
| `DOCKERD_TIMEOUT` | `45` | วินาทีที่รอ dockerd พร้อม |

```bash
# ไม่ใช้ DinD แต่ยืม docker daemon ของ host แทน (ไม่ต้อง --privileged)
docker run -d --name devtools -e START_DOCKERD=0 -v /var/run/docker.sock:/var/run/docker.sock -p 2222:22 devtools:2569_2
```

---

## 3. เข้าใช้งาน container

### เข้าผ่าน shell โดยตรง

```bash
docker exec -it devtools bash
```

### เข้าผ่าน SSH

```bash
ssh root@localhost -p 2222
# password: passwd
```

### เช็คสถานะ

```bash
docker ps --filter name=devtools    # ดูคอลัมน์ STATUS จะมี (healthy)
docker logs devtools                # ดู log ของ entrypoint (sshd / dockerd)
```

---

## 4. ทดสอบว่าทุกอย่างใช้งานได้

```bash
# git
docker exec -it devtools git --version

# docker-in-docker
docker exec -it devtools docker run --rm hello-world

# docker compose
docker exec -it devtools docker compose version

# python / node
docker exec -it devtools bash -lc "python --version && uv --version && node --version"
```

---

## 5. แก้ปัญหาที่เจอบ่อย

| อาการ | สาเหตุ / วิธีแก้ |
|-------|------------------|
| `bind: An attempt was made to access a socket in a way forbidden...` ตอน `-p 2222:22` | Windows จองช่วงพอร์ตนั้นไว้ (Hyper-V/WinNAT) — เปลี่ยนเป็นพอร์ตอื่น เช่น `-p 2299:22` หรือดูช่วงที่ถูกจองด้วย `netsh interface ipv4 show excludedportrange protocol=tcp` |
| container `Exited (0)` ทันทีหลัง `docker run -d` | เวอร์ชันเก่า — เวอร์ชันนี้แก้แล้ว entrypoint จะค้างไว้เองเมื่อไม่มี TTY |
| `docker ps` ข้างใน container ขึ้น `Cannot connect to the Docker daemon` | ลืม `--privileged` — ดู `docker logs <name>` จะมี HINT บอก |
| `apt-get install <pkg>` ข้างใน container ขึ้น `Unable to locate package` | image ไม่ได้เก็บ apt lists ไว้ (เพื่อลดขนาด) — สั่ง `apt-get update` ก่อน |
| `pip install` ขึ้น `externally-managed-environment` | ไม่ควรเจอแล้ว เพราะมี `/opt/venv` อยู่ต้น `PATH` — ถ้าเจอ ให้เช็ก `which pip` ต้องได้ `/opt/venv/bin/pip` |

---

## 6. คำสั่งที่ใช้บ่อย

```bash
# ดู log การ start (sshd / dockerd)
docker logs devtools

# ดู log ของ dockerd ข้างใน
docker exec -it devtools tail -f /var/log/dockerd.log

# หยุด / เริ่มใหม่ / ลบ
docker stop devtools
docker start devtools
docker rm -f devtools

# ลบ image
docker rmi devtools:2569_2
```

---

## 7. Build & Tag สำหรับ push ขึ้น Docker Hub (optional)

```bash
docker tag devtools:2569_2 tuchsanai/devtools:2569_2
docker tag devtools:2569_2 tuchsanai/devtools:latest

docker login -u tuchsanai
docker push tuchsanai/devtools:2569_2
docker push tuchsanai/devtools:latest
```

### build ข้าม architecture (amd64 + arm64) ในครั้งเดียว

```bash
docker buildx build --platform linux/amd64,linux/arm64 -t tuchsanai/devtools:2569_2 --push .
```

---

## 8. ดึง image จาก Docker Hub (ใช้ image สำเร็จรูป)

image ถูก publish ไว้ที่ [`tuchsanai/devtools`](https://hub.docker.com/r/tuchsanai/devtools) — ไม่ต้อง build เองก็ได้

```bash
docker pull tuchsanai/devtools:2569_2

docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_2
```

---

## ภาคผนวก: Python กับ PEP 668

Ubuntu รุ่นใหม่ห้าม `pip install` ลง system Python (error `externally-managed-environment`)
image นี้แก้ให้แล้วด้วยการสร้าง venv ไว้ที่ `/opt/venv` และใส่ไว้ต้น `PATH`

```bash
pip install requests          # ลง /opt/venv ได้เลย ไม่ error
uv pip install pandas         # หรือใช้ uv ที่เร็วกว่ามาก
uv venv .venv && source .venv/bin/activate   # จะแยก venv ของ project ก็ได้
```
