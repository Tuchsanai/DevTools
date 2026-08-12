# 001 LAB — Container Detective

สืบเส้นทาง request ตั้งแต่ browser จนถึง Nginx พร้อมเดินวงจรชีวิต `run → stop → start → rm` และเก็บหลักฐานด้วย `ps`, `exec`, `inspect`, `logs`

## เป้าหมาย

- แยกให้ออกว่า image คือแม่แบบ ส่วน container คือ instance ที่กำลัง/เคยทำงาน
- อธิบาย `-d`, `--name`, `-p` และ bind mount แบบ read-only ได้
- พิสูจน์ว่า `stop` ไม่ใช่ `rm` และ `start` ใช้ container เดิม
- อ่านข้อมูลจาก `docker ps`, `docker inspect`, `docker logs`, `docker exec`

ใช้เวลาประมาณ 25 นาที · SSH `2222` · Web `18081`

## 0) เปิดเครื่อง LAB (ทำบนเครื่อง host)

รันจากโฟลเดอร์ `02_Docker`:

```bash
docker rm -f devtools-container-detective 2>/dev/null
docker run -dit \
  --name devtools-container-detective \
  --privileged \
  -p 2222:22 \
  -p 18081:8080 \
  tuchsanai/devtools:2569_1

docker exec devtools-container-detective mkdir -p /workspace/lab
docker cp 001_LAB_Container_Detective/. \
  devtools-container-detective:/workspace/lab/

ssh root@localhost -p 2222
# password: passwd
```

คำสั่งต่อจากนี้ทำ **ภายใน SSH**:

```bash
cd /workspace/lab
docker --version
```

## 1) เปิด Nginx และแผ่เส้นทาง port

```bash
docker run -d \
  --name devtools-lab1-nginx \
  --label devtools.lab=container-detective \
  -p 8080:80 \
  --mount type=bind,source="$PWD/site",target=/usr/share/nginx/html,readonly \
  nginx:1.29-alpine

docker ps --filter name=devtools-lab1-nginx
curl -I http://localhost:8080
```

เปิด `http://localhost:18081` บน browser ของเครื่อง host

เส้นทางจริงคือ:

```text
Browser :18081 → DevTools :8080 → Nginx :80 → /usr/share/nginx/html
```

## 2) พิสูจน์ `stop ≠ rm`

```bash
docker inspect -f '{{.Id}}' devtools-lab1-nginx
docker stop devtools-lab1-nginx
docker ps
docker ps -a --filter name=devtools-lab1-nginx
docker start devtools-lab1-nginx
docker inspect -f '{{.Id}}' devtools-lab1-nginx
```

ID ก่อนและหลัง `start` ต้องเหมือนกัน เพราะยังเป็น container เดิม

## 3) สอบปากคำ container

```bash
docker exec devtools-lab1-nginx nginx -v

docker inspect -f \
  'name={{.Name}} image={{.Config.Image}} ip={{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' \
  devtools-lab1-nginx

docker logs --tail 12 devtools-lab1-nginx
docker port devtools-lab1-nginx
```

ลองแก้ `site/index.html` ภายในเครื่อง LAB แล้ว refresh หน้าเว็บ สังเกตว่าไม่ต้อง build image ใหม่ เพราะนี่คือ bind mount

## ภารกิจจับผิด

ตอบให้ได้ก่อนจบ LAB:

1. `docker ps` กับ `docker ps -a` ต่างกันตรงไหน?
2. port ซ้ายและขวาของ `8080:80` อยู่คนละฝั่งอย่างไร?
3. เหตุใด mount นี้จึงใส่ `readonly`?

## Cleanup (บังคับ)

ใน SSH:

```bash
docker rm -f devtools-lab1-nginx
exit
```

บน host:

```bash
docker rm -f devtools-container-detective
docker ps -a --filter "name=^devtools-"
```

ผลที่คาดหวัง: ไม่พบ `devtools-container-detective` และ `devtools-lab1-nginx` อีก
