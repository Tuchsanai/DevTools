# DevTools Base Learning Container

Container พื้นฐานสำหรับ DevTools labs — Ubuntu 24.04 ที่มาพร้อม **Docker-in-Docker**, **Python 3**
และ **SSH** ใช้งานได้ทันที

---

## สิ่งที่อยู่ใน image

| หมวด | รายละเอียด |
|------|------------|
| **Base** | Ubuntu 24.04, timezone `Asia/Bangkok`, locale UTF-8 |
| **Docker-in-Docker** | docker-ce, CLI, containerd, buildx & compose plugins |
| **Python** | python3, pip, venv (`python` → `python3`) |
| **Tooling** | git, curl, wget, vim, nano, less, net-tools, ping, dnsutils, openssh-server |
| **Workdir** | `/workspace` |
| **Ports** | `22` (SSH), `8000` |

> หมายเหตุ: container รันเป็น `root` (ไม่มี user `student` แล้ว)

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

```bash
docker run -d \
  --name devtools \
  --privileged \
  -p 2222:22 \
  -p 8000:8000 \
  devtools:2569_1
```

| Flag | ความหมาย |
|------|----------|
| `-d` | รันแบบ background (detached) |
| `--name devtools` | ตั้งชื่อ container |
| `--privileged` | จำเป็นสำหรับ Docker-in-Docker ให้ `dockerd` ทำงานได้ |
| `-p 2222:22` | map SSH port ออกมาที่เครื่อง host พอร์ต 2222 |
| `-p 8000:8000` | map พอร์ต 8000 สำหรับ dev server |

---

## 3. เข้าใช้งาน container

### เข้าผ่าน shell โดยตรง

```bash
docker exec -it devtools bash
```

### เข้าผ่าน SSH

```bash
ssh root@localhost -p 2222
```

### ทดสอบว่า Docker-in-Docker ทำงาน

```bash
docker exec -it devtools docker run --rm hello-world
```

---

## 4. คำสั่งที่ใช้บ่อย

```bash
# ดู log การ start (sshd / dockerd)
docker logs devtools

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
