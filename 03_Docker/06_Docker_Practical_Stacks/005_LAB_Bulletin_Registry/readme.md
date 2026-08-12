# LAB 5 — Bulletin Board: Advanced Dockerfile และ Docker Registry

> นำแนวคิดและหน้าตาของ Bulletin Board จาก LAB เดิมมาทำสำเนาใหม่ในโฟลเดอร์นี้ แล้วปรับ source ให้ dependency ทันสมัยและ reproducible จาก `package-lock.json` แล็บนี้ไม่แก้ไฟล์ต้นฉบับใน `01_Docker`

## สิ่งที่จะได้เรียนรู้

- ใช้ `ARG` กำหนด Node base version และ application version ตอน build
- ใช้ `ENV` กำหนดค่า runtime ที่มี default และ override ได้
- อธิบายว่า `EXPOSE` เป็น metadata ไม่ได้เปิด port บน host
- สร้าง Dockerfile แบบ multi-stage แยก dependency stage ออกจาก runtime stage
- ลด build context ด้วย `.dockerignore`
- รัน process ด้วย non-root user
- เขียน `HEALTHCHECK` ที่เรียก HTTP endpoint จริงโดยไม่ติดตั้ง `curl`
- อ่านสถานะ `starting`, `healthy`, `unhealthy` และ health log
- เข้าใจชื่อ image รูปแบบ `<namespace>/<repository>:<tag>`
- login, tag, push, ลบ local, pull และ run เพื่อพิสูจน์ artifact จาก Registry
- อธิบายว่า `latest` เป็นเพียงชื่อ tag ไม่ได้แปลว่า image ใหม่ที่สุดเสมอ

## ภาพรวมของแล็บ

1. เปิดเครื่องเรียน `devtools-bulletin-registry` ที่ SSH port `2226`
2. ใช้ outer mapping `18085:8085` เพื่อให้ Playwright บน host เข้าเว็บได้
3. อ่าน source, `.dockerignore` และ Dockerfile ทีละส่วน
4. build ด้วย `APP_VERSION=course-2026.08`
5. run inner container ที่ `8085:8080`
6. รอ health status และทดสอบ HTML/health/API
7. ยืนยันว่า process เป็น non-root และค่า ARG ถูกส่งมาเป็น ENV
8. capture เว็บจริงด้วย Playwright CLI
9. tag/push ด้วย placeholder ในเอกสาร
10. ลบ local แล้ว pull/run กลับเพื่อพิสูจน์ Registry
11. logout และลบ outer container พร้อม anonymous volume

## โครงสร้างไฟล์

```text
005_LAB_Bulletin_Registry/
├── app/
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   ├── server.js
│   ├── index.html
│   ├── app.js
│   └── site.css
├── evidence/
├── readme.md
└── validation.md
```

ข้อมูลกิจกรรมในแอปเก็บใน memory เพื่อให้แล็บโฟกัสที่ image และ Registry ไม่ใช่ persistence ซึ่งเรียนใน LAB 3 และ LAB 6

## 0. เปิดเครื่องเรียน

สั่งบน host:

```bash
docker rm -fv devtools-bulletin-registry 2>/dev/null
docker run -dit \
  --name devtools-bulletin-registry \
  --privileged \
  -p 2226:22 \
  -p 18085:8085 \
  -v /home/workspace/DevTools/03_Docker/06_Docker_Practical_Stacks:/course \
  tuchsanai/devtools:2569_1
ssh root@localhost -p 2226
```

**password:** `passwd`

> 📝 `18085:8085` มีสองชั้น: browser บน host เข้า `18085` → outer container port `8085` → inner Docker publish `8085:8080` → Node application port `8080`

ตรวจ environment ภายใน:

```bash
docker --version
cd /course/005_LAB_Bulletin_Registry/app
pwd
ls -la
```

✅ **Expected output:** เห็น `Dockerfile`, `.dockerignore`, `package.json`, `package-lock.json` และ source files

## 1. ทำไมต้องปรับ Dockerfile เดิม

Dockerfile พื้นฐานเดิมใช้ stage เดียว:

```dockerfile
FROM node:<tag>
WORKDIR /usr/src/app
COPY package.json .
RUN npm install
COPY . .
CMD ["npm", "start"]
```

รูปแบบนี้สอนได้ดีในบทพื้นฐาน แต่ยังมีข้อจำกัด:

- ขั้นติดตั้ง dependency และ runtime อยู่ image เดียวกัน
- ไม่มี lockfile จึงอาจได้ transitive dependency ต่างกันในแต่ละวัน
- build context อาจมีไฟล์ที่ไม่ต้องใช้
- process มักรันเป็น root
- ไม่บอกว่าแอปพร้อมตอบ HTTP แล้วหรือยัง
- ไม่มี version metadata ของ build

## 2. อ่าน `.dockerignore`

```bash
cat .dockerignore
```

ไฟล์นี้ตัด `.git`, `.env`, `node_modules`, log, เอกสารและ evidence ออกจาก build context

> `.dockerignore` ไม่ได้ทำให้ไฟล์บนเครื่องหาย เพียงไม่ส่งไฟล์นั้นไปให้ builder และไม่เปิดโอกาสให้ `COPY . .` นำ secret เข้า image โดยไม่ตั้งใจ

ตรวจขนาด context ตอน build จากบรรทัด `transferring context` ห้ามคาดหวังจำนวน byte ตรงกันทุกเครื่อง

## 3. อ่าน Dockerfile ทีละช่วง

### 3.1 Global ARG และ dependency stage

```dockerfile
ARG NODE_VERSION=22
FROM node:${NODE_VERSION}-bookworm-slim AS dependencies
WORKDIR /build
COPY package.json package-lock.json ./
RUN npm ci --omit=dev && npm cache clean --force
```

- `ARG` มีผลตอน build และใช้เลือก base tag
- copy manifest/lockfile ก่อน source เพื่อใช้ layer cache
- `npm ci` ติดตั้งตาม lockfileและล้มเหลวหาก manifest ไม่สอดคล้อง
- stage นี้มีเครื่องมือ npm และ cache ได้ แต่ไม่ใช่ image สุดท้าย

ห้ามใช้ `ARG` ส่ง token หรือ password เพราะค่า build อาจปรากฏใน history/cache

### 3.2 Runtime stage, ARG และ ENV

```dockerfile
FROM node:${NODE_VERSION}-alpine AS runtime
ARG APP_VERSION=2.0.0
ENV NODE_ENV=production \
    PORT=8080 \
    APP_VERSION=${APP_VERSION}
```

`APP_VERSION` เป็น build argument แล้วถูกส่งต่อเป็น runtime environment เพื่อให้ `/health` รายงาน version ของ artifact ได้ ส่วน `PORT` override ตอน `docker run -e PORT=...` ได้

### 3.3 Copy เฉพาะของจำเป็นและใช้ non-root

```dockerfile
COPY --from=dependencies --chown=node:node /build/node_modules ./node_modules
COPY --chown=node:node package.json server.js index.html app.js site.css ./
USER node
EXPOSE 8080
```

- runtime ไม่มี npm cache และ source ที่ไม่จำเป็น
- file ownership เป็นของ user `node`
- `USER node` ลดสิทธิ์ของ process
- `EXPOSE 8080` บอกเจตนาเท่านั้น ถ้าไม่ใช้ `-p` host ยังเข้าไม่ได้

### 3.4 Healthcheck

```dockerfile
HEALTHCHECK --interval=5s --timeout=3s --start-period=5s --retries=5 \
  CMD ["node", "-e", "..."]
```

Healthcheck ใช้ Node built-in HTTP client เรียก `127.0.0.1:$PORT/health` จึงไม่ต้องติดตั้ง `curl` เพิ่มใน runtime image หากได้ status อื่นจาก 200 หรือเชื่อมต่อไม่ได้ คำสั่งจะ exit non-zero

> Health status เป็นข้อมูลให้ operator/Compose ใช้ตัดสินใจ Docker Engine ไม่ได้ restart container ที่ unhealthy โดยอัตโนมัติเพียงเพราะมี healthcheck

## 4. Build image จริง

```bash
time docker build \
  --build-arg NODE_VERSION=22 \
  --build-arg APP_VERSION=course-2026.08 \
  -t bulletinboard:2.0 .
```

✅ **Expected output:**

- มี stage `dependencies` และ `runtime`
- `npm ci --omit=dev` สำเร็จ
- output สุดท้ายตั้งชื่อ `bulletinboard:2.0`
- build context ไม่รวม `evidence`, `.env` หรือ `node_modules`

ตรวจ metadata:

```bash
docker image inspect bulletinboard:2.0 \
  --format 'User={{.Config.User}} Exposed={{json .Config.ExposedPorts}} Healthcheck={{json .Config.Healthcheck.Test}}'
docker history bulletinboard:2.0 --no-trunc
```

✅ ควรเห็น `User=node`, `8080/tcp` และ healthcheck ที่ขึ้นต้นด้วย `node -e`

## 5. Run และรอให้ healthy

```bash
docker rm -f lab5-bulletin 2>/dev/null
docker run -d \
  --name lab5-bulletin \
  -p 8085:8080 \
  bulletinboard:2.0
```

ดู status ซ้ำจน healthy:

```bash
docker ps --filter name=lab5-bulletin
docker inspect lab5-bulletin --format '{{.State.Health.Status}}'
```

✅ **Expected output:** ช่วงแรกอาจเป็น `starting` จากนั้นเปลี่ยนเป็น `healthy` ภายในประมาณ 10–30 วินาที

หาก unhealthy:

```bash
docker inspect lab5-bulletin \
  --format '{{range .State.Health.Log}}{{.ExitCode}} {{.Output}}{{println}}{{end}}'
docker logs lab5-bulletin
```

## 6. ทดสอบ HTTP และ API

```bash
curl -i http://localhost:8085/health
curl -s http://localhost:8085/api/events
curl -i \
  -X POST http://localhost:8085/api/events \
  -H 'Content-Type: application/json' \
  -d '{"title":"Compose Day","detail":"หนึ่งไฟล์เปิดทั้งระบบ","date":"2026-08-15"}'
curl -s http://localhost:8085/api/events
```

✅ **Expected output:**

- health ได้ `HTTP/1.1 200 OK`, `status: ok`, `version: course-2026.08`
- GET แรกมีรายการเริ่มต้นสามรายการ
- POST ได้ `HTTP/1.1 201 Created` และ id ใหม่
- GET รอบสุดท้ายพบ `Compose Day`

ทดลอง validation error:

```bash
curl -i \
  -X POST http://localhost:8085/api/events \
  -H 'Content-Type: application/json' \
  -d '{"title":""}'
```

✅ ได้ `400 Bad Request` และ JSON `title is required`

## 7. พิสูจน์ non-root, ENV และ stage separation

```bash
docker exec lab5-bulletin sh -lc 'id; printenv NODE_ENV PORT APP_VERSION; pwd'
docker exec lab5-bulletin sh -lc 'test ! -d /root/.npm && echo "no root npm cache in runtime"'
```

✅ ควรเห็น user `node`, `production`, `8080`, `course-2026.08`, path `/usr/src/app` และข้อความ `no root npm cache in runtime`

## 8. Capture ด้วย Playwright CLI

เปิดคำสั่งนี้บน **host** ขณะที่ outer และ inner container ยังรันอยู่:

```bash
cd /home/workspace/DevTools/03_Docker/06_Docker_Practical_Stacks/005_LAB_Bulletin_Registry
playwright screenshot \
  --browser chromium \
  --viewport-size '1440,1000' \
  --wait-for-selector '.status.healthy' \
  --full-page \
  http://localhost:18085 \
  evidence/bulletin-board.png
```

✅ **Expected output:** ได้ไฟล์ `evidence/bulletin-board.png` ซึ่งเห็นหัวข้อ `Welcome to the Bulletin Board`, badge API พร้อม และ event cards อย่างน้อยสามใบ

## 9. Registry workflow

### กติกาความลับ

ในเอกสารและงานส่งให้ใช้ placeholder เท่านั้น:

```bash
export DOCKERHUB_USER='<dockerhub-user>'
read -rsp 'Docker Hub access token: ' DOCKERHUB_TOKEN; echo
printf '%s' "$DOCKERHUB_TOKEN" | \
  docker login -u "$DOCKERHUB_USER" --password-stdin
unset DOCKERHUB_TOKEN
```

ห้ามเขียน token ตรง ๆ ใน command, README, screenshot, `.env`, shell script หรือ Git history

### Tag และ push

```bash
export IMAGE_TAG='<dockerhub-user>/devtools-bulletin:course-lab5-<student-id>'
docker tag bulletinboard:2.0 "$IMAGE_TAG"
docker image inspect "$IMAGE_TAG" --format '{{index .RepoDigests 0}}' 2>/dev/null || true
docker push "$IMAGE_TAG"
```

✅ **Expected output:** layer แต่ละชั้นขึ้น `Pushed` หรือ `Layer already exists` และบรรทัดสุดท้ายมี `digest: sha256:...`

`latest` จะเกิดเมื่อ tag หรือ push ชื่อที่ไม่ระบุ tag หรือระบุ `:latest` เท่านั้น มันไม่ใช่กลไกเรียงเวลาของ Registry สำหรับงานจริงควรใช้ version/commit tag ที่ย้อนตรวจได้

### ลบ local แล้ว pull กลับ

```bash
docker rm -f lab5-bulletin
docker image rm "$IMAGE_TAG" bulletinboard:2.0
docker pull "$IMAGE_TAG"
docker run -d --name lab5-pulled -p 8085:8080 "$IMAGE_TAG"
```

รอ healthy แล้วทดสอบ:

```bash
docker inspect lab5-pulled --format '{{.State.Health.Status}}'
curl -s http://localhost:8085/health
curl -s http://localhost:8085/api/events
```

การ pull แล้ว run ผ่านเป็นหลักฐานว่า artifact อยู่ใน Registry ไม่ได้อาศัย local tag เดิม

> ผู้ดูแลหลักสูตรอนุญาตการ validation จริงเฉพาะ tag `tuchsanai/devtools-bulletin:course-lab5-20260812` ผู้เรียนต้องใช้ namespace/tag ที่อาจารย์กำหนด ห้าม push ทับ tag อื่น

## Common errors

| อาการ | สาเหตุที่พบบ่อย | วิธีตรวจ/แก้ |
|---|---|---|
| `npm ci` แจ้ง lock mismatch | `package.json` กับ lockfile ไม่ตรง | regenerate lockfileอย่างตั้งใจแล้ว commit ทั้งคู่ |
| `COPY ... not found` | `.dockerignore` ตัดไฟล์จำเป็นหรือ build ผิด context | ดู `pwd`, `ls -la`, `.dockerignore` |
| container `unhealthy` | endpoint/port ผิด หรือ app crash | inspect health log และ `docker logs` |
| เข้า 8085 ไม่ได้ | ลืม `-p 8085:8080` | ดูคอลัมน์ PORTS ใน `docker ps` |
| host เข้า 18085 ไม่ได้ | outer ไม่ได้ map `18085:8085` | ตรวจ `docker port devtools-bulletin-registry` |
| push ถูก denied | login/namespace/tag ไม่ตรง | `docker info`, `docker image ls`, ตรวจ namespace |
| code เปลี่ยนแต่เว็บเก่า | ยังใช้ image เดิม | build ใหม่และ recreate container |
| token โผล่ใน history | ใส่ค่าโดยตรงใน command | revoke ทันทีและใช้ prompt + stdin |

## เก็บกวาด

ภายในเครื่องเรียน:

```bash
docker rm -f lab5-bulletin lab5-pulled 2>/dev/null
docker ps -a --filter 'name=lab5-'
docker logout
exit
```

บน host:

```bash
docker rm -fv devtools-bulletin-registry
docker ps -a --filter 'name=^devtools-bulletin-registry$'
```

ห้ามใช้ `docker system prune` เพราะอาจแตะ resource ของงานอื่น `docker rm -fv` ลบ outer container และ anonymous `/var/lib/docker` volume ของ LAB นี้เท่านั้น

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `.dockerignore` ตัด `.env`, `node_modules`, evidence และ Git metadata
- [ ] Dockerfile มีสอง stages
- [ ] ใช้ `ARG NODE_VERSION` และ `ARG APP_VERSION`
- [ ] runtime มี `ENV NODE_ENV`, `PORT`, `APP_VERSION`
- [ ] อธิบายได้ว่า `EXPOSE` ไม่ publish port
- [ ] final process รันด้วย user `node`
- [ ] `bulletinboard:2.0` build สำเร็จ
- [ ] container เปลี่ยนจาก starting เป็น healthy
- [ ] GET health/events ได้ 200
- [ ] POST event ที่ถูกต้องได้ 201 และ title ว่างได้ 400
- [ ] Playwright capture หน้าเว็บจริงสำเร็จ
- [ ] Registry command ในเอกสารไม่มี username/token จริง
- [ ] push หรือบันทึกเหตุผลที่ push ไม่ได้
- [ ] หาก pull สำเร็จ ได้ทดสอบ image ที่ pull กลับมาแล้ว
- [ ] logout และลบ outer ด้วย `docker rm -fv`

ผลรันจริงอยู่ใน [`validation.md`](./validation.md), [`evidence/validation-output.txt`](./evidence/validation-output.txt) และ [`evidence/bulletin-board.png`](./evidence/bulletin-board.png)
