# Week 8 — Docker

Software Development Tools and Environments

Docker is an open-source platform that automates the deployment of applications inside software
containers. It provides an additional layer of abstraction and automation of OS-level virtualization
on Windows and Linux.

---

## สไลด์

เปิดไฟล์ [`Docker_Week08_Slides.html`](./Docker_Week08_Slides.html) ในเบราว์เซอร์
(ไฟล์เดียวจบ ไม่ต้องติดตั้งอะไร · กด `O` ดูสไลด์ทั้งหมด · `Ctrl+P` บันทึกเป็น PDF)

ผลการรันทุกอย่างในสไลด์ **รันจริง** บนเครื่องเรียน `tuchsanai/devtools:2569_1`

## เครื่องสำหรับทำแล็บ

ทำบนเครื่องเราเอง ผ่าน VS Code — **ไม่ใช้ cloud**

```bash
docker rm -f devtools
docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

จากนั้นใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บข้างใน
(จะเปิดหน้าเว็บของแล็บในเบราว์เซอร์ ให้ forward port ที่แท็บ **PORTS** ของ VS Code)

## แล็บ

| แล็บในสไลด์ | โฟลเดอร์ | หัวข้อ | Port |
|---|---|---|---|
| **LAB 1** | — (ไม่มีโค้ด) | คำสั่ง `docker run` · `ps` · `pull` · `images` และวงจรชีวิต container | — |
| **LAB 2** | [`01_LAB_Nginx_Port_Mapping`](./01_LAB_Nginx_Port_Mapping) | Nginx + Port Mapping | 8080 |
| **LAB 3** | [`02_LAB_Nginx_Volume_Port_Mapping`](./02_LAB_Nginx_Volume_Port_Mapping) | Nginx + Volume + Port Mapping | 8083 |
| **LAB 4** | [`03_LAB_Node_Bulletin_Board`](./03_LAB_Node_Bulletin_Board) | Build image เอง (Node.js Bulletin Board) | 8085 |

> หมายเลขโฟลเดอร์ (`01`/`02`/`03`) ต่างจากหมายเลขแล็บในสไลด์ (LAB 2/3/4) อยู่ 1
> เพราะ **LAB 1** เป็นคำสั่งพื้นฐานที่ไม่มีโฟลเดอร์โค้ดของตัวเอง

## Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Docker/01_Docker
```

---

Happy Learning!
