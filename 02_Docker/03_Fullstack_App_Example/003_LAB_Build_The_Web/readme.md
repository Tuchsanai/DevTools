# LAB 3 — สร้าง Docker image สำหรับ Next.js แบบพื้นฐาน

> ใช้ `web/Dockerfile`, `verify.sh` และ source code ใน `web/`, `api/`, `db/`

## เป้าหมาย

LAB นี้ตอบคำถามเดียว: **จะนำ Next.js ที่มีอยู่มาสร้างเป็น Docker image และเปิดหน้าเว็บได้อย่างไร**

เมื่อจบ LAB ผู้เรียนจะสามารถ:

- อ่าน Dockerfile แบบ stage เดียวจากบนลงล่างได้
- อธิบาย `FROM`, `WORKDIR`, `COPY`, `RUN`, `ENV`, `EXPOSE` และ `CMD` ได้
- build image และเริ่ม Container ของ Next.js ได้
- ตรวจหน้า `/`, `/tickets`, `/loans` และ `/parts` จากระบบที่รันจริงได้

LAB นี้ตั้งใจใช้ Dockerfile แบบตรงไปตรงมา และไม่เพิ่มหัวข้อปรับแต่งขนาด image

## Dockerfile ที่ใช้

```dockerfile
FROM node:22-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOSTNAME=0.0.0.0

EXPOSE 3000
CMD ["npm", "start"]
```

อ่านเป็นหกขั้น:

| ขั้น | คำสั่ง | ความหมาย |
|---:|---|---|
| 1 | `FROM node:22-alpine` | เริ่มจาก image ที่มี Node.js |
| 2 | `WORKDIR /app` | ใช้ `/app` เป็นโฟลเดอร์ทำงาน |
| 3 | `COPY package…` + `RUN npm ci` | ติดตั้ง dependency ตาม lock file |
| 4 | `COPY . .` + `RUN npm run build` | คัดลอก source และ build Next.js |
| 5 | `ENV` + `EXPOSE 3000` | กำหนดค่าตอนรันและบอกพอร์ตของเว็บ |
| 6 | `CMD ["npm", "start"]` | เริ่ม Next.js production server |

การคัดลอก `package.json` ก่อน source ช่วยให้ Docker นำ layer ของ `npm ci` กลับมาใช้ได้เมื่อแก้เฉพาะโค้ดหน้าเว็บ

## เตรียมสภาพแวดล้อม

```bash
docker rm -f devtools-build-web 2>/dev/null
docker run -dit --name devtools-build-web --privileged -p 2224:22 -p 8324:3000 <DEVTOOLS_IMAGE>
ssh root@localhost -p 2224
cd <REPOSITORY>/02_Docker/03_Fullstack_App_Example/003_LAB_Build_The_Web
```

## การทดลองที่ 1 — อ่าน Dockerfile

```bash
nl -ba web/Dockerfile
grep -c '^FROM ' web/Dockerfile
```

ผลที่คาดหวัง: พบ `FROM` เพียงหนึ่งครั้ง และอ่านขั้นตอนต่อเนื่องจากติดตั้ง dependencyไปจนถึง `npm start`

## การทดลองที่ 2 — Build image

```bash
docker build -t skillspace-web:lab3 ./web
docker image ls skillspace-web:lab3
```

ผลที่คาดหวัง: build สำเร็จและพบ image ชื่อ `skillspace-web` tag `lab3`

## การทดลองที่ 3 — ดูค่าที่ image จะใช้ตอนเริ่ม

```bash
docker image inspect skillspace-web:lab3 \
  --format 'CMD={{json .Config.Cmd}} PORT={{json .Config.ExposedPorts}}'
```

ผลที่คาดหวัง: `CMD=["npm","start"]` และมีพอร์ต `3000/tcp`

## การทดลองที่ 4 — รันและตรวจทั้งระบบ

```bash
KEEP_STACK=1 WEB_PORT=3000 bash verify.sh
```

สคริปต์จะ:

1. ตรวจว่า Dockerfile เป็น stage เดียวและมีคำสั่งพื้นฐานครบ
2. build image ของ web และ api
3. เริ่ม db, api และ web
4. ตรวจหน้า `/`, `/tickets`, `/loans`, `/parts`
5. ตรวจว่า HTML และ CSS โหลดได้จริง

ผลที่ผ่านต้องลงท้ายด้วย `ALL CHECKS PASSED` และ `STACK KEPT`

บนเครื่องผู้เรียนเปิด `http://localhost:8324`

## การทดลองที่ 5 — Walkthrough หน้าเว็บ

| ขั้น | สิ่งที่ทำ | ภาพ |
|---:|---|---|
| 1 | เปิดหน้าสรุป | [Overview](./images/ui-web-01-overview.png) |
| 2 | เปิดกระดานงานซ่อม | [Tickets](./images/ui-web-02-tickets.png) |
| 3 | เลือกครุภัณฑ์ | [Asset](./images/ui-web-03-asset.png) |
| 4 | กรอกอาการ | [Details](./images/ui-web-04-details.png) |
| 5 | เลือกความเร่งด่วน | [Priority](./images/ui-web-05-priority.png) |
| 6 | กดแจ้งซ่อม | [Submit](./images/ui-web-06-submit.png) |
| 7 | เห็น ticket ใหม่ | [New card](./images/ui-web-07-new-card.png) |
| 8 | ระบุชื่อช่าง | [Assignee](./images/ui-web-08-assignee.png) |
| 9 | กดมอบหมาย | [Assign](./images/ui-web-09-assign.png) |
| 10 | เห็นสถานะมอบหมายแล้ว | [Assigned](./images/ui-web-10-assigned.png) |

สร้างภาพใหม่ได้ด้วย:

```bash
cd web
npm ci
npx playwright install --with-deps chromium
LAB_BASE_URL=http://localhost:3000 npm run capture:walkthrough
cd ..
```

## ตรวจงานอัตโนมัติโดยไม่คงระบบไว้

```bash
KEEP_STACK=0 bash verify.sh
echo "exit code = $?"
```

ผลที่ผ่านต้องมี `ALL CHECKS PASSED` และ exit code เป็น `0`

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `Cannot find module` ระหว่าง build | dependency ยังไม่ครบหรือ lock file ไม่ตรง | ตรวจ `package.json`, `package-lock.json` แล้วรัน `npm ci` |
| หน้าเว็บไม่ตอบ | Container ยังไม่ขึ้นหรือพอร์ตไม่ถูก publish | ตรวจ `docker ps` และ `docker logs vops3-web` |
| พอร์ตถูกใช้งานอยู่ | มี process หรือ Container ใช้พอร์ตเดิม | ลบ Container เดิมหรือเปลี่ยน `WEB_PORT` |
| หน้าเว็บเปิดได้แต่ข้อมูลไม่มา | web ติดต่อ api ไม่ได้ | ตรวจ `API_BASE_URL` และสถานะของ api/db |
| หน้าไม่มีรูปแบบ | CSS โหลดไม่สำเร็จ | ใช้ Developer Tools หรือ `curl` ตรวจไฟล์ใต้ `/_next/static/` |

## เก็บกวาด

```bash
docker rm -f vops3-web vops3-api vops3-db
docker volume rm vops3-pgdata
docker image rm vops3-web:verify vops3-api:verify skillspace-web:lab3 2>/dev/null
exit
docker rm -f devtools-build-web
```
