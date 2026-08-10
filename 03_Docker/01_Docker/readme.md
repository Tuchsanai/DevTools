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

---

Happy Learning!
