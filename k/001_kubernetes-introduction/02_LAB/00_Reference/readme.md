# DevTools Base Learning Container

Ubuntu 24.04 สำหรับ DevTools labs — มี **Docker-in-Docker**, **Python 3**, **Node.js 22**, **JupyterLab** และ **SSH** พร้อมใช้

| หมวด | รายละเอียด |
|------|------------|
| **Base** | Ubuntu 24.04, timezone `Asia/Bangkok`, locale UTF-8 |
| **Docker-in-Docker** | docker-ce, containerd, buildx & compose plugins |
| **Python / Node.js** | python3, pip, venv — Node.js 22 LTS + npm/npx |
| **Tooling** | git, curl, wget, vim, nano, less, net-tools, ping, dnsutils |
| **Ports** | `22` SSH, `8888` JupyterLab |
| **SSH login** | ส่วนที่ 1: user `root` / password `passwd` — ส่วนที่ 2: key `devtoolSSH` |
| **Workdir** | `/workspace` |

> ⚠️ รหัสผ่าน `passwd` และ key ในโฟลเดอร์ `Devtool_SSH/` เป็นค่าเดียวกันทุกเครื่อง — ใช้เพื่อการเรียน/ทดลองบนเครื่องตัวเองเท่านั้น ไม่ควรเปิดพอร์ตออก internet

เลือกใช้ **ส่วนใดส่วนหนึ่ง** — ทั้งสองส่วนใช้ชื่อ container `devtools` และพอร์ตเดียวกัน ถ้าจะเปลี่ยนส่วนให้ลบ container เดิมก่อนด้วย `docker rm -f devtools`

---

# ส่วนที่ 1 — SSH ด้วย password

## 1.1 Run container

คำสั่งบรรทัดเดียว copy-paste ได้ทั้ง Windows และ Linux/macOS (ดึง image จาก Docker Hub ให้อัตโนมัติ)

```bash
docker run -dit --name devtools --privileged -p 2222:22 -p 8888:8888 tuchsanai/devtools:2569_1
```

| Flag | ความหมาย |
|------|----------|
| `-dit` | รันแบบ background พร้อม tty |
| `--name devtools` | ตั้งชื่อ container |
| `--privileged` | จำเป็นสำหรับ Docker-in-Docker ให้ `dockerd` ข้างในทำงานได้ |
| `-p 2222:22` | map SSH ออกมาที่ host พอร์ต `2222` |
| `-p 8888:8888` | map JupyterLab ออกมาที่ host พอร์ต `8888` |

ตรวจว่า container ทำงานแล้ว:

```bash
docker ps --filter name=devtools
# CONTAINER ID   IMAGE                       STATUS         PORTS
# xxxxxxxxxxxx   tuchsanai/devtools:2569_1   Up 5 seconds   0.0.0.0:2222->22/tcp, 0.0.0.0:8888->8888/tcp
```

## 1.2 SSH ด้วย password

```bash
ssh root@localhost -p 2222
# password: passwd
```

ครั้งแรกที่เชื่อมต่อ ssh จะถามยืนยัน host key ให้พิมพ์ `yes` แล้วใส่รหัสผ่าน `passwd`:

```text
$ ssh root@localhost -p 2222
The authenticity of host '[localhost]:2222 ([127.0.0.1]:2222)' can't be established.
ED25519 key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
root@localhost's password:
root@devtools:~# whoami
root
root@devtools:~# docker run --rm hello-world     # ทดสอบ Docker-in-Docker
```

### รันคำสั่งเดียวแล้วออก / copy ไฟล์เข้า-ออก container

ทุกคำสั่งจะถามรหัสผ่าน `passwd` เหมือนกัน

```bash
ssh -p 2222 root@localhost "hostname && docker --version"
scp -P 2222 ./hello.txt root@localhost:/workspace/
scp -P 2222 root@localhost:/workspace/hello.txt ./
```

| คำสั่ง | ทำอะไร |
|--------|--------|
| `ssh -p 2222 root@localhost "hostname && docker --version"` | เชื่อมต่อเข้า container แล้ว **รันคำสั่งในเครื่องหมาย `"..."` ครั้งเดียวแล้วออกทันที** (ไม่เปิด shell ค้างไว้) — `hostname` แสดงชื่อเครื่อง (`devtools`), `&&` = รันคำสั่งถัดไปเมื่อคำสั่งแรกสำเร็จ, `docker --version` แสดงเวอร์ชัน Docker ใน container ผลลัพธ์แสดงบนเครื่องเรา |
| `scp -P 2222 ./hello.txt root@localhost:/workspace/` | **copy ไฟล์จากเครื่องเรา → container**: ต้นทาง `./hello.txt` (ไฟล์ในโฟลเดอร์ปัจจุบันบนเครื่องเรา) ปลายทาง `root@localhost:/workspace/` (โฟลเดอร์ `/workspace` ใน container) |
| `scp -P 2222 root@localhost:/workspace/hello.txt ./` | **copy ไฟล์จาก container → เครื่องเรา**: สลับต้นทาง/ปลายทาง — ดึง `/workspace/hello.txt` ใน container มาไว้ที่โฟลเดอร์ปัจจุบัน (`./`) |

ส่วนประกอบของคำสั่ง:

| ส่วน | ความหมาย |
|------|----------|
| `root@localhost` | login เป็น user `root` ที่เครื่อง `localhost` (พอร์ต 2222 ถูก map ไปที่ SSH ของ container) |
| `-p 2222` / `-P 2222` | ระบุพอร์ต — `ssh` ใช้ `-p` (ตัวเล็ก) แต่ `scp` ใช้ `-P` (ตัวใหญ่) |
| `scp <ต้นทาง> <ปลายทาง>` | ฝั่งที่มี `user@host:` นำหน้า = ไฟล์ใน container, ฝั่งที่ไม่มี = ไฟล์บนเครื่องเรา |

---

# ส่วนที่ 2 — SSH ด้วย key (`devtoolSSH`)

โฟลเดอร์ `Devtool_SSH/` ในโฟลเดอร์นี้มีคู่ key สำเร็จรูปของ lab ให้แล้ว เมื่อ map โฟลเดอร์นี้เข้า container
`start.sh` จะนำ public key ไปใส่ใน `/root/.ssh/authorized_keys` ให้เองตอน start

```text
00_Reference/
├── Dockerfile
└── Devtool_SSH/         ← map เป็น volume → /etc/devtools/ssh
    ├── devtoolSSH       ← private key (ใช้กับ ssh -i)
    └── devtoolSSH.pub   ← public key (ใส่ใน authorized_keys ให้อัตโนมัติ)
```

## 2.1 Build image

image บน Docker Hub (`tuchsanai/devtools:2569_1`) ยังไม่รองรับ SSH ด้วย key — ต้อง build จาก `Dockerfile` ในโฟลเดอร์นี้ก่อน

```bash
docker build -t devtools:2569_1 .
```

## 2.2 Run container พร้อม map โฟลเดอร์ key

รันในโฟลเดอร์นี้ (ที่มี `Devtool_SSH/`) — `${PWD}` ใช้ได้ทั้ง PowerShell และ Linux/macOS

```bash
docker run -dit --name devtools --privileged -p 2222:22 -p 8888:8888 -v "${PWD}/Devtool_SSH:/etc/devtools/ssh" devtools:2569_1
```

| Flag | ความหมาย |
|------|----------|
| `-v "${PWD}/Devtool_SSH:/etc/devtools/ssh"` | map โฟลเดอร์ key เข้า container (flag อื่นเหมือนส่วนที่ 1) |
| `devtools:2569_1` | image ที่ build เองในข้อ 2.1 |

ตรวจว่าเปิดใช้ key แล้ว:

```bash
docker logs devtools | grep "SSH key"
# [start.sh] SSH key login enabled: /etc/devtools/ssh/devtoolSSH.pub
```

## 2.3 SSH ด้วย key

Linux/macOS ต้องตั้ง permission ของ private key ก่อน (ครั้งเดียว — git ไม่เก็บ permission ไว้ ssh จะไม่ยอมใช้ key ที่คนอื่นอ่านได้):

```bash
chmod 600 Devtool_SSH/devtoolSSH
```

login ด้วย key — ไม่ถามรหัสผ่าน:

```bash
ssh -i Devtool_SSH/devtoolSSH root@localhost -p 2222
```

```text
$ ssh -i Devtool_SSH/devtoolSSH root@localhost -p 2222
root@devtools:~# whoami
root
```

### รันคำสั่งเดียวแล้วออก / copy ไฟล์ด้วย key

เหมือนข้อ 1.2 ทุกอย่าง แค่เพิ่ม `-i Devtool_SSH/devtoolSSH` — จึง **ไม่ถามรหัสผ่าน**

```bash
ssh -i Devtool_SSH/devtoolSSH -p 2222 root@localhost "hostname && docker --version"
scp -i Devtool_SSH/devtoolSSH -P 2222 ./hello.txt root@localhost:/workspace/
```

| คำสั่ง | ทำอะไร |
|--------|--------|
| `ssh -i Devtool_SSH/devtoolSSH -p 2222 root@localhost "hostname && docker --version"` | login ด้วย private key แล้วรัน `hostname` และ `docker --version` ใน container ครั้งเดียวแล้วออก |
| `scp -i Devtool_SSH/devtoolSSH -P 2222 ./hello.txt root@localhost:/workspace/` | copy `hello.txt` จากเครื่องเรา → `/workspace/` ใน container โดยใช้ key (ดึงกลับก็สลับต้นทาง/ปลายทางเหมือนข้อ 1.2) |

| ส่วน | ความหมาย |
|------|----------|
| `-i Devtool_SSH/devtoolSSH` | **i**dentity file — ระบุ private key ที่ใช้ยืนยันตัวตนแทนรหัสผ่าน (ใช้ `-i` ตัวเล็กทั้ง `ssh` และ `scp`) |
| `-p 2222` / `-P 2222` | พอร์ต — `ssh` ตัวเล็ก, `scp` ตัวใหญ่ (เหมือนข้อ 1.2) |

> * key คู่นี้ **แจกให้ทุกคนใช้ร่วมกัน** สำหรับ lab เท่านั้น — ห้ามนำไปใช้กับเครื่องจริง
> * อยากได้ key ใหม่: ลบไฟล์ทั้งสองใน `Devtool_SSH/` แล้ว `docker restart devtools` → container สร้างคู่ใหม่ให้ในโฟลเดอร์เดิม
> * login ด้วย password (`passwd`) ยังใช้ได้เหมือนส่วนที่ 1

---

# ใช้ร่วมกันทั้งสองส่วน

## JupyterLab

เปิดเบราว์เซอร์ที่ <http://localhost:8888> — เข้าได้เลยไม่ต้องใส่รหัสผ่าน งานของ lab อยู่ที่ `/workspace`

## คำสั่งที่ใช้บ่อย

```bash
docker logs devtools                 # ดู log ตอน start (sshd / dockerd / jupyter)
docker exec -it devtools bash        # เข้า shell โดยไม่ผ่าน SSH
docker stop devtools                 # หยุด container
docker start devtools                # เริ่มใหม่
docker rm -f devtools                # ลบ container
```
