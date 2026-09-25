# LAB 3 — Build · Push · Pull · Deploy ร้านอาหารแมวด้วย Jenkins และ Docker Hub

> ⏱️ ประมาณ 60 นาที · 🧪 11 การทดลอง · 🎯 จบเมื่อเปิด `http://localhost:3000` แล้วเห็นร้าน **Meow Mart** ที่ Jenkins สั่ง build, push ขึ้น Docker Hub, pull กลับมา และ deploy ให้อัตโนมัติ และผ่านรายการ **✅ ตรวจปิดแล็บด้วยตา** ครบทุกข้อ

แล็บนี้ตอบคำถามว่า **“ซอร์สโค้ดหนึ่งชุดเดินทางจากเครื่องของเราไปเป็นเว็บที่รันได้บนเครื่องใดก็ได้อย่างไร”** นักศึกษาจะให้ Jenkins สั่งสร้าง Docker image ของเว็บขายอาหารแมวที่เขียนด้วย **Next.js** ทดสอบ image นั้น push ขึ้น **Docker Hub** แล้ว pull กลับมา deploy เป็นเว็บจริง โดย Jenkins ยังคงเป็น image มาตรฐาน `jenkins/jenkins:lts-jdk21` ที่ **ไม่มี Docker อยู่ข้างใน** ทุกคำสั่ง Docker ถูกส่งผ่าน **SSH** ไปทำบน container `devtools` จากนั้นพิสูจน์ด้วยผลการทดลองว่า image เดียวกันรันบนเครื่องที่สองได้ด้วย digest เดียวกัน ออกเวอร์ชันใหม่ได้ภายในไม่กี่วินาที และย้อนกลับ (rollback) ได้ในเวลาไม่ถึง 2 วินาที ทุกขั้นตรวจผลด้วยตาจากหน้าเว็บ Console Output และ Docker Hub ไม่ต้องใช้คำสั่ง API

![Build once, run anywhere](./images/lab3_theory_build_push_pull.png)

*ภาพที่ 1 ภาพรวมของแล็บ: Jenkins สั่งงานผ่าน SSH → devtools รัน `docker build` → Docker Hub เก็บ image → เครื่องใดก็ pull ไปรันได้ และทุกเครื่องได้ image ที่มี digest เดียวกัน*

**สิ่งที่จะได้เมื่อจบแล็บ** — ร้าน Meow Mart ที่ deploy โดย Pipeline (ภาพจริงจากการทดลอง แบบเต็มจอ 1920×1080):

![หน้าแรกของร้าน Meow Mart](./images/lab3_web_fullhd_hero.jpg)

*ภาพที่ 2 หน้าแรกของร้าน สังเกต chip สีเขียวบนแถบด้านบน `v1.0.0 · build #1` ซึ่งอ่านมาจาก image ที่ Jenkins สั่งสร้าง*

---

## 📚 ทฤษฎีก่อนลงมือ

### 1. Image, Container, Registry และคำสั่งหลักสี่คำสั่ง

| คำศัพท์ | ความหมาย | เปรียบเทียบ |
|---|---|---|
| **Image** | แพ็กเกจแบบอ่านอย่างเดียวที่มีระบบไฟล์ของแอป runtime และคำสั่งเริ่มต้น | “แม่พิมพ์” หรือกล่องอาหารแมวที่ปิดผนึก |
| **Container** | process ที่รันจาก image หนึ่งตัว มี writable layer ของตัวเอง | อาหารที่เทออกมาใส่ชาม |
| **Registry** | ที่เก็บและแจกจ่าย image เช่น Docker Hub | โกดังกลางที่ร้านทุกสาขามารับของ |
| **Repository / Tag** | ชื่อชุดของ image (`<DOCKER_USER>/catfood-shop`) และป้ายเวอร์ชัน (`1`, `2`, `latest`) | ชื่อสินค้าและรุ่น |

วงจรที่แล็บนี้ฝึกคือ `docker build` → `docker push` → `docker pull` → `docker run` ข้อดีสำคัญคือ **build ครั้งเดียว แล้วรันได้ทุกที่ (build once, run anywhere)** เครื่องปลายทางไม่ต้องมี Node.js, ไม่ต้อง `npm install` และไม่ต้องมีซอร์สโค้ด ขอเพียงมี Docker และเข้าถึง registry ได้

### 2. Dockerfile แบบ single-stage: อ่านทีละบรรทัด

image ประกอบด้วย **layer** ซ้อนกัน คำสั่ง `FROM`, `COPY`, `RUN` แต่ละบรรทัดใน Dockerfile สร้าง layer ใหม่ที่มีไฟล์ ส่วนคำสั่งอย่าง `ENV`, `ARG`, `EXPOSE`, `HEALTHCHECK`, `CMD` บันทึกเพียงค่าตั้งค่า (metadata) ขนาด 0 B แล็บนี้ใช้ Dockerfile แบบ **single-stage** คือมี `FROM` เพียงบรรทัดเดียว ทุกขั้นจึงอยู่ใน image เดียวและอ่านจากบนลงล่างได้ทันที (ตัดคอมเมนต์ออก):

```dockerfile
FROM node:22-alpine
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund && npm cache clean --force

COPY . .
RUN npm run build && rm -rf .next/cache

ENV NODE_ENV=production \
    PORT=3000

ARG APP_VERSION=dev
ARG BUILD_NUMBER=local
ARG GIT_COMMIT=none
ARG BUILD_TIME=unknown
ENV APP_VERSION=$APP_VERSION \
    BUILD_NUMBER=$BUILD_NUMBER \
    GIT_COMMIT=$GIT_COMMIT \
    BUILD_TIME=$BUILD_TIME

EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --start-period=30s --start-interval=1s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/api/health || exit 1
CMD ["npm", "start"]
```

| บรรทัด | ทำอะไร | ขนาด layer (วัดจริงในการทดลองที่ 4) |
|---|---|---:|
| `FROM node:22-alpine` | ใช้ Node.js 22 บน Alpine Linux เป็นฐาน | ≈ 177 MB |
| `WORKDIR /app` · `ENV NEXT_TELEMETRY_DISABLED=1` | กำหนดโฟลเดอร์ทำงาน และปิดการส่ง telemetry ของ Next.js | 8.19 kB · 0 B |
| `COPY package.json package-lock.json ./` | คัดลอกเฉพาะรายการ dependency | 45.1 kB |
| `RUN npm ci ... && npm cache clean --force` | ติดตั้ง dependency ตาม lock file แล้วลบ cache ของ npm | **357 MB** |
| `COPY . .` | คัดลอกซอร์สโค้ดของร้าน | 422 kB |
| `RUN npm run build && rm -rf .next/cache` | `next build` แล้วลบ cache ของการ build | 5.62 MB |
| `ENV NODE_ENV=production PORT=3000` | ค่าตั้งค่าตอนรัน | 0 B |
| `ARG` ×4 + `ENV APP_VERSION=...` | รับข้อมูล build จาก Jenkins แล้วเก็บเป็น env ของ image | 0 B |
| `EXPOSE 3000` · `CMD ["npm", "start"]` | ประกาศ port และคำสั่งเริ่ม `next start` | 0 B |
| `HEALTHCHECK ... CMD wget ...` | ให้ **Docker เอง** เข้าไปถามแอปว่ายังตอบอยู่หรือไม่ ช่วงเริ่มระบบ (30 วินาทีแรก) ถามทุก 1 วินาที หลังจากนั้นทุก 10 วินาที | 0 B |

หลักการสำคัญที่ซ่อนอยู่ใน Dockerfile นี้มีสี่ข้อ

1. **`FROM` หนึ่งบรรทัด = image หนึ่งตัว** ทุกอย่างที่ติดตั้งหรือสร้างในขั้นใดก็ตามจะติดอยู่ใน image สุดท้าย
2. **คัดลอก dependency ก่อนซอร์สโค้ด** `npm ci` คือ layer ที่ใหญ่และช้าที่สุด การ `COPY package*.json` แยกไว้ก่อน `COPY . .` ทำให้การแก้โค้ดของร้านไม่ทำให้ layer นี้ต้องสร้างใหม่ ขั้น `npm ci` จึงใช้ cache ได้ตราบที่ `package-lock.json` ไม่เปลี่ยน
3. **ลบของที่ไม่ใช้ใน `RUN` เดียวกัน** `npm cache clean --force` และ `rm -rf .next/cache` ต้องต่อท้ายด้วย `&&` ในบรรทัดเดียวกับคำสั่งที่สร้างไฟล์นั้น เพราะ layer ที่สร้างเสร็จแล้วแก้ไม่ได้ การเขียน `RUN rm ...` เป็นบรรทัดใหม่เพียงสร้าง layer ที่ “ซ่อน” ไฟล์ไว้ image ไม่ได้เล็กลง (การทดลองที่ 4 วัดผลต่างจริงให้ดู)
4. **ให้ Docker ตรวจสุขภาพแทนเรา** `HEALTHCHECK` ทำให้ทุก container ที่รันจาก image นี้มีสถานะสุขภาพติดตัว เริ่มจาก `starting` แล้วเปลี่ยนเป็น `healthy` เมื่อแอปตอบได้ (หรือ `unhealthy` ถ้าล้มเหลว 3 ครั้งติด) นักศึกษาเห็นสถานะนี้ได้ในคอลัมน์ STATUS ของ `docker ps` เช่น `Up 2 seconds (healthy)` ส่วน Pipeline อ่านค่าเดียวกันด้วย `docker inspect -f '{{.State.Health.Status}}'` ตัวเลือก `--start-interval=1s` ทำให้ Docker ถามถี่ทุก 1 วินาทีระหว่างเริ่มระบบ สถานะจึงเปลี่ยนเป็น `healthy` ได้ภายในไม่กี่วินาทีแทนที่จะรอรอบ 10 วินาที

ส่วน `ARG`/`ENV` ที่เปลี่ยนทุก build ถูกวางไว้ **ท้ายสุด** ด้วยเหตุผลเรื่อง layer cache ในหัวข้อถัดไป

![Dockerfile แบบ single-stage](./images/lab3_theory_single_stage.png)

*ภาพที่ 3 Dockerfile แบบ single-stage: ทุกขั้นอยู่ใน image เดียว layer ที่ใหญ่ที่สุดคือ `npm ci` ตัวเลขในภาพมาจากการวัดจริงในการทดลองที่ 4*

> 📝 image ที่ใช้ใน production มักถูกลดขนาดลงอีกด้วยเทคนิคขั้นสูงกว่านี้ ซึ่งอยู่นอกขอบเขตของแล็บนี้

### 3. Layer cache: ทำไม build ครั้งที่สองเร็วขึ้น

Docker จำผลของแต่ละ layer ไว้ ถ้าคำสั่งและไฟล์ที่ป้อนให้ layer นั้นไม่เปลี่ยน ครั้งถัดไปจะใช้ของเดิม แต่เมื่อ layer ใดเปลี่ยน layer ที่อยู่ถัดลงไปทั้งหมดต้องสร้างใหม่ หลักการเขียน Dockerfile จึงเป็น **“เรียงจากสิ่งที่เปลี่ยนน้อยไปหาสิ่งที่เปลี่ยนบ่อย”**

ในแล็บนี้ทุก build เกิดขึ้นบน Docker ของ devtools ซึ่งใช้ **BuildKit** เป็นตัว build ทั้งตอนที่นักศึกษาพิมพ์ `docker build` เอง (การทดลองที่ 4) และตอนที่ Jenkins สั่งผ่าน SSH (การทดลองที่ 6 และ 10) จึงใช้ cache ชุดเดียวกัน BuildKit แสดงเฉพาะขั้นที่สร้างไฟล์เป็นบรรทัด `#N` ใน console ได้แก่ `#6` `WORKDIR`, `#7` `COPY package*.json`, `#8` `RUN npm ci`, `#9` `COPY . .` และ `#10` `RUN npm run build` ขั้นที่ใช้ cache จะขึ้นว่า `#6 CACHED` … `#10 CACHED` ส่วน `ENV`/`ARG`/`HEALTHCHECK`/`CMD` เป็น metadata ที่ถูกเขียนลงใน image config ตอนท้าย ไม่ถูกแสดงเป็นขั้นแยก

Dockerfile ของร้านวางข้อมูลที่เปลี่ยนทุก build (`APP_VERSION`, `BUILD_NUMBER`, `BUILD_TIME`) ไว้ **ท้ายสุด** ด้วย `ARG` + `ENV` ผลคือเมื่อออกเวอร์ชันใหม่ ทั้ง 5 ขั้นที่สร้างไฟล์ (รวม `npm ci` และ `next build`) ขึ้น `CACHED` สิ่งที่เปลี่ยนมีเพียง image config ที่เก็บค่า env ใหม่ ตอน push Docker Hub จึงตอบว่า `Layer already exists` ทุก layer (พิสูจน์ในการทดลองที่ 10)

![Layer cache](./images/lab3_theory_layer_cache.png)

*ภาพที่ 4 build #2 เปลี่ยนเฉพาะส่วนบนสุด (ค่าตั้งค่าของ image) ส่วน layer อื่นใช้ cache และไม่ต้องอัปโหลดซ้ำ*

### 4. Tag กับ Digest

- **Tag** คือป้ายชื่อที่ย้ายได้ เช่น `latest` ชี้ไปที่ build #1 แล้วภายหลังย้ายไปชี้ build #2
- **Digest** (`sha256:...`) คือลายนิ้วมือที่คำนวณจากเนื้อหาของ image เนื้อหาต่างกันแม้เพียงบิตเดียว digest ก็ต่างกัน และไม่มีวันเปลี่ยน

แนวปฏิบัติคือ **deploy ด้วย tag แต่ตรวจสอบด้วย digest** Jenkins console จะพิมพ์ digest หลัง push และหน้า Tags บน Docker Hub แสดง digest 12 ตัวแรก ซึ่งต้องตรงกัน

Pipeline ของแล็บ build ด้วย `docker build --provenance=false` เพื่อให้ image ที่ push ขึ้นไปเป็น **manifest เดี่ยว** digest ที่ Jenkins พิมพ์จึงเท่ากับ digest ที่หน้า Docker Hub แสดงทุกตัวอักษร ถ้าเปิด attestation ไว้ (ค่าเริ่มต้นของ BuildKit) สิ่งที่ถูก push จะเป็น **index** ที่ห่อ image กับเอกสาร provenance ไว้ด้วยกัน console จะพิมพ์ digest ของ index ขณะที่ Docker Hub แสดง digest ของ image ราย platform ซึ่งเป็นคนละค่า ผู้เขียนพบปัญหานี้จริงระหว่างทดสอบแล็บ จึงปิด provenance ไว้เพื่อให้การตรวจด้วยตาทำได้ตรงไปตรงมา

![Tag vs Digest](./images/lab3_theory_tag_digest.png)

*ภาพที่ 5 tag ย้ายได้ ส่วน digest ผูกกับเนื้อหาตลอดไป ค่า `7803b4edfb8a…` และ `0f85c4beb07e…` คือ digest จริงของ build #1 และ #2 ในการทดลองนี้*

### 5. Jenkins สั่ง Docker ผ่าน SSH ไปที่ devtools

Jenkins ในแล็บนี้คือ image มาตรฐาน `jenkins/jenkins:lts-jdk21` ตามที่ใช้มาตั้งแต่ LAB 2 **ไม่ติดตั้ง Docker CLI เพิ่ม ไม่ mount Docker socket และไม่ mount ซอร์สโค้ด** เหตุผลมีสามข้อ

1. **Jenkins มีหน้าที่ “สั่ง” ไม่ใช่ “ทำ”** Jenkins ควบคุมลำดับขั้น เก็บ log และเก็บ credential ส่วนงานหนักอย่าง build/test/push ให้เครื่องที่มีเครื่องมือครบทำ แนวคิดเดียวกับ **build agent** ในระบบจริงที่ Jenkins controller ส่งงานไปให้เครื่องลูกทำ
2. **image เล็กและเป็นมาตรฐาน** ไม่ต้องดูแล image ที่สร้างเอง อัปเกรด Jenkins ได้ด้วยการเปลี่ยน tag อย่างเดียว
3. **เครื่องที่เป็นเจ้าของ Docker ทำงานเอง** devtools มีทั้ง Docker daemon, ซอร์สโค้ด และ cache ของการ build อยู่แล้ว เมื่อสั่งให้ devtools build เองจึงใช้ cache เดียวกับที่นักศึกษา build ด้วยมือ

การเชื่อมต่อทำงานดังนี้

| ส่วน | ทำงานอย่างไร |
|---|---|
| ชื่อ `devtools` | ตอนสร้าง container `jenkins` ใส่ `--add-host devtools:host-gateway` Docker จะเขียนบรรทัด `<IP ของ gateway> devtools` ลงใน `/etc/hosts` ของ Jenkins IP นั้นคือ gateway ของ bridge network ซึ่งก็คือ Docker host = devtools เอง (Jenkins เป็น container ที่ Docker ของ devtools สร้าง) |
| ช่องทาง | devtools มี `sshd` ทำงานอยู่แล้ว Jenkins ใช้ SSH client ที่มีมากับ image มาตรฐาน ส่งคำสั่งแบบ `ssh root@devtools "docker ..."` |
| การยืนยันตัวตน | ใช้ **SSH key** ไม่ใช้รหัสผ่าน: private key เก็บใน **Jenkins Credentials** (ID `devtools-ssh`) เท่านั้น public key อยู่ใน `~/.ssh/authorized_keys` ของ devtools |
| host key | `-o StrictHostKeyChecking=accept-new` ยอมรับ host key ของ devtools อัตโนมัติในการเชื่อมต่อครั้งแรกแล้วจดไว้ ครั้งต่อไปถ้า host key เปลี่ยน SSH จะปฏิเสธ (ป้องกันการปลอมเครื่อง) |

![Jenkins สั่ง Docker ผ่าน SSH](./images/lab3_theory_ssh.png)

*ภาพที่ 6 Jenkins (image มาตรฐาน ไม่มี Docker) ใช้ private key จาก Credentials เชื่อมต่อ SSH ไปที่ `devtools` ผ่านชื่อที่ได้จาก host-gateway แล้ว devtools เป็นผู้รัน `docker build/run/push/pull` กับ Docker Hub*

> ⚠️ **Safety:** การ login เป็น `root` ผ่าน SSH ด้วย key ชุดเดียวที่ใช้ร่วมกัน เหมาะกับแล็บที่ลบทิ้งได้เท่านั้น ใครได้ private key นี้ไปก็สั่ง Docker ของ devtools ได้ทุกอย่าง ระบบ production ควรใช้ผู้ใช้หรือ build agent เฉพาะงาน จำกัดสิทธิ์ตามหลัก least privilege และแยก key ต่อเครื่อง

### 6. Credential ไม่อยู่ในโค้ด

แล็บนี้มีความลับสองชิ้น คือ **private key** สำหรับเข้า devtools (ID `devtools-ssh`) และ **Docker Hub token** (ID `dockerhub`) ทั้งสองเก็บใน **Jenkins Credentials** Jenkinsfile อ้างถึงด้วย ID เท่านั้น Pipeline ใช้มาตรการซ้อนกันหลายชั้น:

| มาตรการ | ป้องกันอะไร |
|---|---|
| `SSH_KEY = credentials('devtools-ssh')` ในบล็อก `environment` | Jenkins เขียน private key ลงไฟล์ชั่วคราวใน workspace แล้วส่ง path ให้ `ssh -i` ใช้ console แสดงเป็น `ssh -i ****` และไฟล์ถูกลบเมื่อจบ build |
| `withCredentials([usernamePassword(credentialsId: 'dockerhub', ...)])` | token มีอยู่เฉพาะในบล็อกที่ใช้ ไม่อยู่ใน environment ของทั้ง Pipeline |
| Groovy สตริงอัญประกาศเดี่ยว `'''...'''` | Groovy ไม่แทนค่า token ลงในสคริปต์ shell เป็นผู้อ่านค่าเอง |
| `set +x` | shell ไม่พิมพ์คำสั่งที่มี token ออก console |
| `echo "$DOCKER_TOKEN" \| ssh ... docker login --password-stdin` | token เดินทางผ่าน **stdin** ของ SSH ไปถึง `docker login` บน devtools ไม่ปรากฏใน command line ของ process ใดทั้งฝั่ง Jenkins และ devtools |
| `DOCKER_CONFIG=/tmp/jenkins-docker-<BUILD>` + `trap 'docker logout; rm -rf "$DOCKER_CONFIG"' EXIT` | ไฟล์ login ถูกเขียนในโฟลเดอร์ชั่วคราวของ build นั้น และถูกลบทันทีที่ push เสร็จ ไม่ว่าจะสำเร็จหรือล้มเหลว ผู้เขียนตรวจแล้วว่าไม่มีโฟลเดอร์ค้างบน devtools และจำนวน token ที่ปรากฏใน console = 0 |
| Masking ของ Jenkins | ถ้าความลับหลุดเข้า console จะแสดงเป็น `****` (เป็นเพียงด่านสุดท้าย ไม่ใช่การรับประกัน) |

---

## 🎯 Learning Objectives — ผลลัพธ์การเรียนรู้

เมื่อจบแล็บนี้ นักศึกษาจะสามารถ

1. อธิบายความสัมพันธ์ของ image, container, registry, tag และ digest และลำดับ build → push → pull → run ได้
2. อ่าน Dockerfile แบบ single-stage ทีละบรรทัด วัดขนาดของแต่ละ layer ด้วย `docker history` และอธิบายบทบาทของ `HEALTHCHECK` ได้
3. เรียงลำดับคำสั่งใน Dockerfile ให้ใช้ layer cache ได้คุ้มค่า และอ่านผล `CACHED` / `Layer already exists` ได้
4. ตั้งค่า Jenkins (image มาตรฐาน) ให้สั่ง build/push/deploy บน devtools ผ่าน SSH โดยเก็บ key และ token ใน Credentials
5. ยืนยันว่า image บน Docker Hub คือ image เดียวกับที่ Jenkins สั่ง build และที่รันอยู่บนทุกเครื่อง โดยใช้ digest
6. ออกเวอร์ชันใหม่และ rollback ด้วยการเปลี่ยน tag ได้
7. ตรวจผลด้วยการดูหน้าเว็บ/Console/Docker Hub แทนการใช้คำสั่ง API

## 🗺️ แผนที่การทดลอง

| ช่วง | การทดลอง | สิ่งที่ทำ | ผลที่ต้องได้ (ค่าจริงจากการทดลอง) |
|---|---|---|---|
| A. เตรียม Jenkins | 1–3 | Jenkins ไม่มี Docker → สร้าง SSH key → ให้ Jenkins เห็น devtools | `docker: not found` → key 2 ไฟล์ → `Permission denied (publickey,password)` (แปลว่าต่อถึงแล้ว รอ key) |
| B. รู้จัก image | 4 | build และรัน image ของร้านในเครื่อง + ส่อง layer | **693 MB** (ดาวน์โหลด **154 MB**), `healthy` ใน 3 วินาที, เว็บขึ้น `vdev · build #local` |
| C. Pipeline | 5–7 | credential 2 ตัว → job → build #1 | 5 stage เขียวใน 23 วินาที, `Login Succeeded`, digest `7803b4edfb8a…` |
| D. Registry & เว็บ | 8–9 | ดู Docker Hub, เปิดร้าน, pull บนเครื่องที่สอง | tag `1`/`latest`, เครื่องที่สอง pull 10.5 วินาที digest เดียวกัน |
| E. Release | 10–11 | build #2 v1.1.0 แล้ว rollback | build #2 ไม่มี layer ต้องอัปโหลด, rollback **1.7 วินาที**, ตรวจปิดแล็บด้วยตาผ่าน |

## 📂 ไฟล์ในโฟลเดอร์นี้

| ไฟล์ | หน้าที่ |
|---|---|
| `catfood-shop/` | ซอร์สโค้ดร้าน Meow Mart (Next.js 16 + React 19) |
| `catfood-shop/Dockerfile` | Dockerfile แบบ single-stage + `HEALTHCHECK` (ใช้จริงใน Pipeline) |
| `Jenkinsfile` | Pipeline 5 stage ผ่าน SSH: Connect devtools → Build image → Test image → Push → Pull & Deploy |

ภายใน `catfood-shop/` ที่ควรรู้จัก:

```text
catfood-shop/
├── app/page.js            # หน้าร้าน (อ่าน build info ทุก request)
├── app/components/Shop.js # ตัวกรองหมวด + ตะกร้า (ทำงานฝั่ง browser)
├── app/api/health/route.js# route ตรวจสุขภาพที่ HEALTHCHECK ใน Dockerfile เรียกใช้
├── data/products.js       # ข้อมูลสินค้า 6 รายการ
├── data/buildInfo.js      # อ่าน APP_VERSION, BUILD_NUMBER, GIT_COMMIT, BUILD_TIME
└── public/images/         # ภาพสินค้า
```

## สภาพตั้งต้น

ต้องจบ LAB 2 แล้ว: devtools container ทำงาน มี network `cicd-net`, container `jenkins` ที่สร้างจาก `jenkins/jenkins:lts-jdk21`, volume `jenkins_home` และ job `first-pipeline`

> **Prerequisite:** ร้านแมวของแล็บนี้เปิดที่ port `3000` — port 3000 เปิดไว้แล้วตั้งแต่ LAB 1 ส่วนที่ 0 (`-p 3000:3000`) ไม่ต้องสร้าง devtools ใหม่

> **Prerequisite Docker Hub:** สมัครบัญชี ยืนยันอีเมล และสร้าง **Access Token สิทธิ์ Read & Write** แนะนำให้สร้าง repository `catfood-shop` แบบ **Public** ไว้ก่อน (ถ้าไม่สร้าง Docker Hub จะสร้างให้อัตโนมัติตอน push ตามค่า Default privacy ของบัญชี)

ไฟล์ของแล็บนี้อยู่ที่ `~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push` ใน shell ของ devtools ตรวจว่า Jenkins จาก LAB 2 ยังทำงาน:

```bash
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

✅ **สิ่งที่ต้องเห็น:**

```text
NAMES     IMAGE                       STATUS
jenkins   jenkins/jenkins:lts-jdk21   Up ...
```

---

## ช่วง A — เตรียม Jenkins ให้สั่งงาน devtools ผ่าน SSH

### การทดลองที่ 1 — Jenkins มี Docker หรือไม่ และมี ssh หรือไม่?

**คำถาม:** Jenkins container จาก LAB 2 เรียกคำสั่ง `docker` ได้หรือไม่ และมีเครื่องมือใดที่ใช้ติดต่อเครื่องอื่นได้อยู่แล้ว?

```bash
docker exec jenkins sh -c 'docker version'; printf 'exit=%s\n' "$?"
docker exec jenkins ssh -V
```

✅ **ผลการทดลองจริง:**

```text
sh: 1: docker: not found
exit=127
OpenSSH_10.0p2 Debian-7+deb13u4, OpenSSL 3.5.7 9 Jun 2026
```

> 🔍 **วิเคราะห์ผล:** exit code `127` หมายถึงหาโปรแกรมไม่พบ Jenkins image มาตรฐานไม่มี Docker CLI **และแล็บนี้ตั้งใจให้เป็นเช่นนั้น** เราจะไม่ติดตั้ง Docker ลงใน Jenkins แต่ image มาตรฐานมี SSH client (OpenSSH) มาให้แล้ว ซึ่งเพียงพอสำหรับส่งคำสั่งไปให้ devtools ทำแทน

### การทดลองที่ 2 — สร้าง SSH key ให้ Jenkins ใช้เข้า devtools

**คำถาม:** Jenkins จะพิสูจน์ตัวตนกับ devtools โดยไม่ต้องใช้รหัสผ่านได้อย่างไร?

รันใน shell ของ devtools:

```bash
ssh-keygen -t ed25519 -N '' -C jenkins-to-devtools -f ~/.ssh/jenkins_devtools
cat ~/.ssh/jenkins_devtools.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
ls -l ~/.ssh
```

✅ **ผลการทดลองจริง** (`ssh-keygen` พิมพ์ fingerprint ซึ่งต่างกันในแต่ละเครื่อง เช่น `SHA256:Zf/xzHLP… jenkins-to-devtools`):

```text
-rw------- 1 root root 101 ... authorized_keys
-rw------- 1 root root 411 ... jenkins_devtools
-rw-r--r-- 1 root root 101 ... jenkins_devtools.pub
```

> 🔍 **วิเคราะห์ผล:** `ssh-keygen` สร้าง key เป็นคู่ `jenkins_devtools` คือ **private key** (411 ไบต์ สิทธิ์ `-rw-------` อ่านได้เฉพาะเจ้าของ) ใช้พิสูจน์ตัวตน ต้องเก็บเป็นความลับและจะถูกนำไปใส่ใน Jenkins Credentials เท่านั้น ส่วน `jenkins_devtools.pub` คือ **public key** (101 ไบต์) เปิดเผยได้ เมื่อต่อท้ายไว้ใน `authorized_keys` แล้ว sshd ของ devtools จะยอมให้ผู้ที่ถือ private key คู่กันเข้าได้ ขนาดของ `authorized_keys` เท่ากับ `.pub` พอดี (101 ไบต์) แสดงว่ามี public key อยู่ 1 ชุด `-N ''` หมายถึงไม่ตั้ง passphrase เพื่อให้ Jenkins ใช้ได้โดยไม่ต้องมีคนพิมพ์

### การทดลองที่ 3 — ให้ Jenkins เรียก devtools ด้วยชื่อได้ (image เดิม + volume เดิม)

**คำถาม:** เมื่อสร้าง container `jenkins` ใหม่จาก image เดิมพร้อม `--add-host` แล้ว Jenkins มองเห็น devtools หรือไม่ และ job จาก LAB 2 ยังอยู่หรือไม่?

```bash
docker rm -f jenkins
docker run -d --name jenkins --network cicd-net --restart unless-stopped \
  -p 8080:8080 --add-host devtools:host-gateway \
  -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21
docker exec jenkins getent hosts devtools
docker exec jenkins ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new root@devtools true; printf 'exit=%s\n' "$?"
docker inspect -f '{{.Config.Image}}  {{.HostConfig.ExtraHosts}}' jenkins
```

✅ **ผลการทดลองจริง** (IP `172.18.0.1` อาจต่างกันในแต่ละเครื่อง):

```text
172.18.0.1      devtools
Warning: Permanently added 'devtools' (ED25519) to the list of known hosts.
root@devtools: Permission denied (publickey,password).
exit=255
jenkins/jenkins:lts-jdk21  [devtools:host-gateway]
```

> 🔍 **วิเคราะห์ผล:** ชื่อ `devtools` แปลงเป็น `172.18.0.1` ซึ่งเป็น gateway ของ bridge network นั่นคือ Docker host = devtools เอง บรรทัด `Permanently added 'devtools' (ED25519)` แสดงว่า SSH คุยกับ sshd ของ devtools ได้จริงและจด host key ไว้แล้ว (`accept-new`) ส่วน `Permission denied (publickey,password)` เป็นผลที่ **ถูกต้อง** เพราะ Jenkins ยังไม่มี private key (`BatchMode=yes` สั่งไม่ให้ถามรหัสผ่าน) ข้อความนี้จึงพิสูจน์ว่าเส้นทางเครือข่ายใช้งานได้แล้ว ขาดเพียง key ซึ่งจะใส่เป็น credential ในการทดลองที่ 5 บรรทัดสุดท้ายยืนยันว่า Jenkins ยังเป็น image มาตรฐานตัวเดิม เพิ่มเพียง host entry หนึ่งรายการ

จากนั้นเปิด `http://localhost:8080` login ด้วย `admin / admin2569` (Jenkins อาจใช้เวลาเริ่มระบบสักครู่) แล้วดูหน้า Dashboard: job `first-pipeline` ยังอยู่ เพราะข้อมูลทั้งหมดเก็บใน volume `jenkins_home` ไม่ใช่ใน container

---

## ช่วง B — รู้จัก image ของร้านก่อนให้ Jenkins สั่งสร้าง

### การทดลองที่ 4 — build และรัน image ของร้านในเครื่อง: layer ไหนใหญ่ที่สุด?

**คำถาม:** image ของร้านที่ build จาก `Dockerfile` มีขนาดเท่าไร layer ใดกินพื้นที่มากที่สุด container พร้อมใช้งานเร็วแค่ไหน และ build ซ้ำโดยไม่แก้อะไรใช้เวลาเท่าไร?

```bash
cd ~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop
time docker build -t catfood-shop:local .
docker image ls catfood-shop
docker history --format 'table {{.CreatedBy}}\t{{.Size}}' catfood-shop:local | head -14
docker run --rm catfood-shop:local sh -c 'du -sh /app/node_modules /app/.next'
```

✅ **ผลการทดลองจริง** (build ครั้งแรก ไม่มี cache ใช้เวลารวม 33 วินาที):

```text
IMAGE                ID             DISK USAGE   CONTENT SIZE
catfood-shop:local   7c1dade1e2f1        693MB          154MB

CREATED BY                                      SIZE
...                                             0B      (แถว CMD / HEALTHCHECK / EXPOSE / ENV / ARG)
RUN ... npm run build && rm -rf .next…          5.62MB
COPY . . # buildkit                             422kB
RUN ... npm ci --no-audit --no-fund &…          357MB
COPY package.json package-lock.json ./ # bui…   45.1kB

337.6M  /app/node_modules
5.3M    /app/.next
```

จากนั้นรัน container จาก image นี้ แล้วดูสถานะสุขภาพที่ `HEALTHCHECK` รายงาน:

```bash
docker run -d --name catfood-local -p 3000:3000 catfood-shop:local
docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'      # รอจน STATUS มี (healthy)
```

✅ **ผลการทดลองจริง** (สั่ง `docker ps` หลังรันประมาณ 3 วินาที):

```text
NAMES           STATUS                   PORTS
catfood-local   Up 2 seconds (healthy)   0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
```

ถ้าสั่งเร็วเกินไปจะเห็น `(health: starting)` ให้สั่ง `docker ps` ซ้ำอีกครั้ง เมื่อขึ้น `(healthy)` แล้ว เปิด **http://localhost:3000** ใน browser

![ร้านที่รันจาก image local](./images/lab3_s04_local_web.png)

*ภาพที่ 7 ร้านที่รันจาก `catfood-shop:local` chip บนแถบด้านบนแสดง `vdev · build #local`*

เลื่อนลงล่างสุดของหน้าไปที่ส่วน **Deployment info**

![Deployment info ของ image local](./images/lab3_s04_local_deploy_info.png)

*ภาพที่ 8 Deployment info ของ image ที่ build เอง: version `dev`, build `local`, commit `none`, built at `unknown`*

เมื่อดูเสร็จแล้ว ลบ container เพื่อคืน port 3000 ให้ Pipeline แล้วลอง build ซ้ำทันที:

```bash
docker rm -f catfood-local                  # คืน port 3000 ให้ Pipeline
time docker build -t catfood-shop:local .   # build ซ้ำทันที
```

build ซ้ำครั้งที่สองทุกขั้นขึ้น `CACHED` และเสร็จใน 1 วินาที

| วัดค่า | ผลจริง |
|---|---:|
| ขนาดบนดิสก์ (DISK USAGE) | 693 MB |
| ขนาดที่ต้องดาวน์โหลด (CONTENT SIZE) | 154 MB |
| layer `npm ci` (ใหญ่ที่สุด) | 357 MB |
| base image `node:22-alpine` | ≈ 177 MB |
| `node_modules` / `.next` ใน image | 337.6 MB / 5.3 MB |
| เวลาจาก `docker run` ถึง `(healthy)` | ≈ 3 วินาที |
| เวลา build ครั้งแรก / build ซ้ำ | 33 วินาที / 1 วินาที |

**ผลของการล้าง cache ใน `RUN` เดียวกัน** — ผู้เขียนวัดเปรียบเทียบกับ Dockerfile รุ่นที่ยังไม่มี `&& npm cache clean --force` ต่อท้าย `npm ci`:

| วัดค่า | ไม่ล้าง cache ของ npm | ล้างใน `RUN` เดียวกัน | ผลต่าง |
|---|---:|---:|---:|
| layer `npm ci` | 447 MB | 357 MB | −90 MB |
| DISK USAGE | 873 MB | 693 MB | ≈ −180 MB |
| CONTENT SIZE | 243 MB | 154 MB | −89 MB |

> 🔍 **วิเคราะห์ผล:** หน้าเว็บแสดง `dev` และ `local` เพราะเราไม่ได้ส่ง `--build-arg` ค่า `ARG` จึงใช้ค่า default ใน Dockerfile (Jenkins จะส่งค่าจริงให้ในการทดลองที่ 6) ส่วน `(healthy)` ภายในราว 3 วินาทีมาจาก `--start-interval=1s` ที่ให้ Docker ถามแอปทุกวินาทีตอนเริ่มระบบ ตาราง `docker history` ยืนยันว่า `node_modules` จากขั้น `npm ci` กินพื้นที่ราวครึ่งหนึ่งของ image ส่วนซอร์สโค้ดและผล `next build` รวมกันไม่ถึง 7 MB นี่คือเหตุผลที่ต้องวาง `npm ci` ไว้ก่อน `COPY . .` เพื่อให้ layer ที่ใหญ่ที่สุดถูกใช้ซ้ำจาก cache และการลบ cache ใน `RUN` เดียวกันลดขนาดที่ต้องดาวน์โหลดลงได้ราว 89 MB ทุกครั้งที่ push/pull

---

## ช่วง C — Pipeline: Connect → Build → Test → Push → Pull & Deploy

### การทดลองที่ 5 — เก็บ SSH key และ Docker Hub token ใน Jenkins Credentials

**คำถาม:** จะให้ Pipeline ใช้ private key และ token โดยไม่เขียนความลับลงในโค้ดได้อย่างไร?

1. เปิด `http://localhost:8080` และ login ด้วย `admin / admin2569`
2. เลือก **Manage Jenkins → Credentials** (หมวด Security)

![Manage Jenkins → Credentials](./images/lab3_s04a_manage_credentials.png)

*ภาพที่ 9 เมนู Credentials ในหมวด Security ของ Manage Jenkins*

#### (ก) SSH key สำหรับเข้า devtools

3. เลือก **System → Global credentials (unrestricted) → Add Credentials** แล้วเลือกชนิด **SSH Username with private key** → **Next**

![เลือกชนิด SSH Username with private key](./images/lab3_s05a_ssh_credential_type.png)

*ภาพที่ 10 เลือกชนิด credential แบบ SSH Username with private key*

4. แสดง private key ใน shell ของ devtools แล้วคัดลอก **ทั้งไฟล์** รวมบรรทัด `-----BEGIN OPENSSH PRIVATE KEY-----` และ `-----END OPENSSH PRIVATE KEY-----`

```bash
cat ~/.ssh/jenkins_devtools
```

5. กรอก ID = `devtools-ssh`, Description ตามภาพ, Username = `root` ในส่วน Private Key เลือก **Enter directly** → **Add** แล้ววางเนื้อหาที่คัดลอกมา

![แบบฟอร์ม SSH key](./images/lab3_s05b_ssh_credential_form.png)

*ภาพที่ 11 ID `devtools-ssh` คือชื่อที่ Jenkinsfile อ้างถึงใน `credentials('devtools-ssh')` และ Username `root` คือผู้ใช้บน devtools*

6. ปล่อยช่อง **Passphrase** ว่าง (key นี้สร้างด้วย `-N ''`) แล้วกด **Create**

![ส่วนล่างของแบบฟอร์ม SSH key](./images/lab3_s05b2_ssh_credential_form_bottom.png)

*ภาพที่ 12 ส่วนล่างของแบบฟอร์ม: ช่อง Passphrase ว่าง และปุ่ม Create*

> ⚠️ private key คือความลับ วางได้ที่ Jenkins Credentials เท่านั้น ห้ามวางในแชต เอกสาร หรือ commit ลง Git

#### (ข) Docker Hub token

7. กลับไปที่ **Global credentials (unrestricted) → Add Credentials** เลือกชนิด **Username with password** → **Next**

![เลือกชนิด credential](./images/lab3_s04c_credential_type.png)

*ภาพที่ 13 Jenkins รุ่นนี้ (2.568.3) ให้เลือกชนิด credential ใน dialog ก่อน*

8. กรอก Username = `<DOCKER_USER>`, Password = `<DOCKER_TOKEN>`, ID = `dockerhub`, Description ตามภาพ แล้วกด **Create** (แทน placeholder ด้วยค่าจริงของตนเอง)

![แบบฟอร์ม Username with password](./images/lab3_s04d_add_credential_form.png)

*ภาพที่ 14 ช่อง Password ถูกปิดบังเสมอ และ ID `dockerhub` คือชื่อที่ Jenkinsfile อ้างถึง*

✅ **สิ่งที่ต้องเห็น:** หน้า Global credentials มีสองรายการ

![รายการ credential สองตัว](./images/lab3_s05c_credentials_list.png)

*ภาพที่ 15 `devtools-ssh` (root) และ `dockerhub` (`<DOCKER_USER>/******`)*

> 🔍 **วิเคราะห์ผล:** ตรวจด้วยตาว่าหน้านี้แสดงเพียง ID ชื่อผู้ใช้ และคำอธิบาย **ไม่แสดง private key หรือ token เลย** แม้แต่ผู้ดูแลที่เปิดหน้านี้ก็อ่านความลับกลับออกมาไม่ได้ Pipeline เท่านั้นที่ขอใช้ได้ผ่าน ID

### การทดลองที่ 6 — สร้าง Pipeline และสั่ง build ครั้งแรก

**คำถาม:** Pipeline 5 stage ที่สั่งงานผ่าน SSH ทำงานผ่านครบหรือไม่ ใช้เวลาเท่าไร และคำสั่งไปรันที่เครื่องใดจริง?

#### อ่าน `Jenkinsfile` ก่อนใช้งาน

| ส่วน | หน้าที่ |
|---|---|
| `parameters { string(name: 'APP_VERSION', defaultValue: '1.0.0') }` | ให้กด **Build with Parameters** เพื่อกำหนดเวอร์ชันได้ |
| `environment { SSH_KEY = credentials('devtools-ssh') }` | Jenkins เขียน private key ลงไฟล์ชั่วคราว แล้วใส่ path ไว้ใน `$SSH_KEY` ให้ `ssh -i "$SSH_KEY"` ใช้ |
| `DEVTOOLS = 'root@devtools'` · `SSH_OPTS = '-o StrictHostKeyChecking=accept-new -o LogLevel=ERROR'` | ปลายทางของ SSH (ชื่อ `devtools` มาจาก `--add-host`) และตัวเลือกที่ยอมรับ host key ครั้งแรกพร้อมตัดข้อความเตือนออกจาก console |
| `APP_DIR = '~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop'` | path ของซอร์สโค้ด **บน devtools** Jenkins ไม่ต้องมีสำเนาของซอร์สเลย |
| `APP_NAME = 'catfood-shop'` · `DEPLOY_NAME = 'catfood-web'` | ชื่อ repository บน Docker Hub และชื่อ container ของร้านที่เปิดให้ลูกค้าใช้ |
| `VERSION = "${params.APP_VERSION}"` | ส่งค่า parameter เข้า shell ได้ตั้งแต่ build แรก (build แรกของ job ยังไม่มีตัวแปร `$APP_VERSION` ใน shell) |
| stage `Connect devtools` | `ssh ... "hostname; docker --version"` ตรวจว่าเข้า devtools ได้และที่นั่นมี Docker |
| stage `Build image` | `ssh ... "APP_DIR=... IMAGE=... VERSION=... BUILD=... bash -s" <<'EOF'` ค่าต่าง ๆ ถูกแทนบนฝั่ง Jenkins แล้วส่งไปเป็น `VAR=value` หน้าคำสั่ง ส่วนเนื้อสคริปต์ระหว่าง `<<'EOF'` … `EOF` ถูกส่งทาง stdin ไปให้ `bash -s` **รันบน devtools** (เครื่องหมาย `'EOF'` ทำให้ shell ฝั่ง Jenkins ไม่แทนค่า `$` ในเนื้อสคริปต์) สคริปต์ `cd $APP_DIR` แล้ว `docker build --provenance=false --build-arg APP_VERSION=... --build-arg BUILD_NUMBER=... --build-arg BUILD_TIME=... -t catfood-shop:<BUILD_NUMBER> .` |
| stage `Test image` | รัน container ชั่วคราว `catfood-test-N` แล้ววนอ่าน `docker inspect -f '{{.State.Health.Status}}'` ทุก 1 วินาที สูงสุด 30 ครั้ง จากนั้นลบ container ทิ้ง ถ้าสถานะสุดท้ายไม่ใช่ `healthy` stage ล้ม และไม่ push |
| stage `Push` | ส่ง token ทาง stdin ไปให้ `docker login --password-stdin` บน devtools โดยใช้ `DOCKER_CONFIG=/tmp/jenkins-docker-<BUILD>` แล้ว tag และ push `:<BUILD_NUMBER>` กับ `:latest` เมื่อจบ `trap` สั่ง `docker logout` และลบโฟลเดอร์นั้นทิ้ง |
| stage `Pull & Deploy` | `docker image rm` tag ในเครื่องทิ้งก่อน (พิสูจน์ว่าได้ image มาจาก Docker Hub จริง) → `docker pull` → สร้าง `catfood-web` ใหม่ด้วย `-p 3000:3000 --restart unless-stopped` → รอจน `healthy` |
| `post { success { echo ... } }` | พิมพ์ URL ของร้านเมื่อสำเร็จ |

#### ขั้นตอน

1. Dashboard → **New Item** → ชื่อ `docker-build-push` → เลือก **Pipeline** → **OK**

![New Item แบบ Pipeline](./images/lab3_s05a_new_item_pipeline.png)

*ภาพที่ 16 สร้าง job ชนิด Pipeline ชื่อ `docker-build-push`*

2. ในส่วน **Pipeline** คง Definition เป็น **Pipeline script** แล้ววางเนื้อหาของ `~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile` ทั้งไฟล์ → **Save**

```bash
cat ~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile
```

![Pipeline script](./images/lab3_s05d_pipeline_script.png)

*ภาพที่ 17 Jenkinsfile ใน editor เริ่มจากบล็อก `parameters` และ `environment` ที่อ้างถึง `credentials('devtools-ssh')`*

3. กด **Build Now** (build แรกใช้ค่า default `APP_VERSION=1.0.0`)

![Build Now](./images/lab3_s06a_build_now.png)

*ภาพที่ 18 เมนู Build Now ของ job — หลัง build แรก เมนูจะเปลี่ยนเป็น Build with Parameters*

4. รอให้ build จบ แล้วเปิด **Pipeline Overview** (หน้า Stages) ของ build #1

![Pipeline Graph build #1](./images/lab3_s06b_pipeline_graph_b1.png)

*ภาพที่ 19 build #1 ผ่านครบทั้ง 5 stage หน้าเว็บแสดง “Took 23 sec”*

✅ **ผลการทดลองจริง** (อ่านจากหน้า Stages):

| Stage | เวลาจริง |
|---|---:|
| Connect devtools | 0.34 s |
| Build image | 1.9 s |
| Test image | 2.8 s |
| Push | 12.5 s |
| Pull & Deploy | 4.6 s |
| Post Actions | 0.1 s |
| **รวม** | **23.0 s** |

5. เปิด **Console Output** ของ build #1 แล้วอ่านสามช่วงต่อไปนี้

![console: Connect devtools และเริ่ม Build image](./images/lab3_s06c_console_ssh_build_b1.png)

*ภาพที่ 20 stage Connect devtools พิมพ์ hostname `efd5852c2216` และ `Docker version 29.8.1, build 4a63305` ส่วนคำสั่ง ssh แสดงเป็น `ssh -i ****` เพราะ path ของ key ถูก mask*

![console: CACHED ใน Build image](./images/lab3_s06d_console_cache_test_b1.png)

*ภาพที่ 21 stage Build image: BuildKit ของ devtools แสดง `#6 CACHED` … `#10 CACHED`*

![console: health ของ catfood-test-1](./images/lab3_s06e_console_test_health_b1.png)

*ภาพที่ 22 stage Test image: `health of catfood-test-1: starting` สองครั้ง แล้วเปลี่ยนเป็น `healthy`*

> 🔍 **วิเคราะห์ผล:** `efd5852c2216` คือ hostname ของ **container devtools** ไม่ใช่ของ Jenkins และ `Docker version 29.8.1` มาจาก Docker ของ devtools ทั้งที่การทดลองที่ 1 พิสูจน์แล้วว่า Jenkins ไม่มีคำสั่ง `docker` จึงยืนยันได้ว่าคำสั่งทั้งหมดไปรันบน devtools จริง stage `Build image` ใช้เวลาเพียง 1.9 วินาทีเพราะ build เกิดบน Docker/BuildKit ของ devtools ตัวเดียวกับที่ใช้ในการทดลองที่ 4 จึงใช้ cache ได้ครบทั้ง 5 ขั้น (`#6`–`#10 CACHED`) แม้ค่า `--build-arg` จะต่างจากเดิม เพราะ `ARG`/`ENV` อยู่ท้าย Dockerfile ส่วน stage `Test image` แสดงว่า HEALTHCHECK ของ Docker ตอบ `healthy` หลังรอ 2 รอบ Pipeline จึงเดินต่อไปยัง Push

### การทดลองที่ 7 — Console พิสูจน์อะไรได้บ้าง?

**คำถาม:** console ของ build #1 ยืนยันการ login, push และการ pull กลับมา deploy ได้อย่างไร?

อ่าน **Console Output** ของ build #1 ใน browser ต่อจากการทดลองที่ 6 (เลื่อนลงหรือใช้ Ctrl+F ค้นคำในหน้าเว็บ)

![Login Succeeded](./images/lab3_s07a_console_login.png)

*ภาพที่ 23 `Login Succeeded` เกิดจาก `--password-stdin` บน devtools โดยไม่มี token ปรากฏใน console*

![push digest](./images/lab3_s07b_console_digest.png)

*ภาพที่ 24 ผล push สองบรรทัด: `1: digest: sha256:7803b4edfb8a3a4e5ecba20ff545d24a0f58d17366793509d464bc52cf56ae76 size: 2006` และ `latest: digest:` ค่าเดียวกัน `size: 2006`*

![pull และ deploy](./images/lab3_s07c_console_pull_deploy.png)

*ภาพที่ 25 stage Pull & Deploy: `1: Pulling from <DOCKER_USER>/catfood-shop` → `Status: Downloaded newer image for <DOCKER_USER>/catfood-shop:1` → `health of catfood-web: starting` สองครั้ง → `healthy`*

ท้าย console มีบรรทัดจาก `post { success }`:

```text
เปิดร้านได้ที่ http://localhost:3000 (catfood-shop v1.0.0 build #1)
```

> 🔍 **วิเคราะห์ผล:** tag `1` และ `latest` ได้ digest เดียวกัน `sha256:7803b4edfb8a…` เพราะเป็น image ตัวเดียวกันที่ติดป้ายสองป้าย `Downloaded newer image` ยืนยันว่า `catfood-web` รันจาก image ที่ดึงลงมาจาก Docker Hub จริง ไม่ใช่ image ที่เพิ่ง build ในเครื่อง (Pipeline ลบ tag ในเครื่องทิ้งก่อน pull) ในการทดลองของผู้เขียน ทุก layer ของ tag `1` ขึ้น `Layer already exists` (9 layer) เพราะ repository ของผู้เขียนมี layer ชุดนี้อยู่แล้วจากการทดสอบก่อนหน้า บน repository ใหม่ของนักศึกษา push ครั้งแรกจะขึ้น `Pushed` ครบ (อัปโหลดจริงราว 146 MB) stage Push จึงอาจใช้เวลานานกว่าตัวเลขในตาราง

---

## ช่วง D — Docker Hub และเปิดร้านจริง

### การทดลองที่ 8 — Docker Hub เก็บอะไรไว้ และร้านทำงานอย่างไร?

**คำถาม:** digest บน Docker Hub ตรงกับ console หรือไม่ และเว็บที่ deploy แล้วมี feature อะไร?

1. เปิด `https://hub.docker.com/r/<DOCKER_USER>/catfood-shop/tags` (หรือเมนู **My Hub → Repositories → catfood-shop → Tags**)

![Docker Hub หลัง build #1](./images/lab3_s08a_hub_tags_b1.png)

*ภาพที่ 26 Docker Hub แสดง tag `1` ที่มี digest `7803b4edfb8a` ตรงกับ console ในภาพที่ 24 ขนาดที่ต้องดาวน์โหลด (Compressed size) คือ 146.53 MB ภาพนี้ถ่ายหลังจบแล็บ หน้า Tags จริงจึงมี tag `2` และ `latest` อยู่ด้วย*

เทียบ digest 12 ตัวแรกบนหน้านี้กับบรรทัด `1: digest: sha256:7803b4edfb8a…` ใน console ด้วยตา ต้องตรงกันทุกตัวอักษร ตัวเลข 146.53 MB กับ CONTENT SIZE `154MB` ในการทดลองที่ 4 คือขนาดเดียวกันแต่ต่างหน่วย: 154 MB (หน่วยฐาน 10) ≈ 146.5 MiB (หน่วยฐาน 2)

2. เปิด **http://localhost:3000** — นี่คือร้านที่ Pipeline deploy ให้ ลองใช้งานตามภาพเคลื่อนไหวด้านล่าง (ยาวประมาณ 23 วินาที)

![สาธิตการใช้งานร้าน](./images/lab3_web_demo.gif)

*ภาพที่ 27 สาธิตจริงบนเว็บที่ deploy แล้ว: กรองหมวดสินค้า → ใส่ตะกร้า (ตัวเลขและยอดรวมเปลี่ยนทันที) → ดู Deployment info*

![รายการสินค้า](./images/lab3_web_fullhd_products.jpg)

*ภาพที่ 28 รายการสินค้า 6 รายการ แต่ละการ์ดมีภาพ ป้าย ขนาด คะแนน ราคา และปุ่มใส่ตะกร้า*

**Feature ของร้าน Meow Mart**

| Feature | ทำงานที่ | ทดลองอย่างไร | ผลที่เห็นจริง |
|---|---|---|---|
| หน้าแรก + chip เวอร์ชัน | server (อ่าน env ทุก request) | เปิดหน้าแรก | `v1.0.0 · build #1` |
| ตัวกรองหมวดสินค้า | browser (React state) | คลิก “อาหารเปียก”, “ขนมแมว” | เหลือ 1 และ 2 รายการ |
| ตะกร้าสินค้า | browser | กด “+ ใส่ตะกร้า” 3 ครั้ง | `🛒 3 ชิ้น · ฿867` (149 + 259 + 459) |
| Deployment info | server | เลื่อนลงล่างสุด | version, build, commit, เวลา build, container ID |
| Health check | Docker HEALTHCHECK | `docker ps` | `(healthy)` |

![สรุป feature สี่ภาพ](./images/lab3_web_features.png)

*ภาพที่ 29 (ซ้ายบน) กรองหมวดอาหารเปียก (ขวาบน) ใส่ตะกร้าชิ้นแรก (ซ้ายล่าง) ตะกร้า 3 ชิ้น ฿867 (ขวาล่าง) Deployment info*

![Deployment info](./images/lab3_web_fullhd_deploy.jpg)

*ภาพที่ 30 ส่วน Deployment info บอกว่าเว็บนี้มาจาก image ใด: `1.0.0`, Jenkins build `#1`, เวลา build และ container ที่กำลังตอบ (ภาพนี้ถ่ายระหว่าง rollback ในการทดลองที่ 11 ซึ่งรัน image `:1` ตัวเดียวกัน container ID จึงไม่ตรงกับ container ที่ build #1 สร้าง)*

> 🔍 **วิเคราะห์ผล:** ช่อง container ID ใน Deployment info คือ hostname ของ container ที่ตอบหน้าเว็บ จะเปลี่ยนทุกครั้งที่สร้าง container ใหม่ แม้ image เดิม ส่วน version, build และเวลา build ถูกอบไว้ใน image จึงคงที่ ช่อง `commit` เป็น `none` เพราะ LAB 3 ยังไม่ได้ดึงซอร์สจาก Git — LAB 4 จะทำให้ช่องนี้แสดง commit จริง

### การทดลองที่ 9 — Pull บนเครื่องที่สอง ได้ image เดียวกันจริงหรือ?

**คำถาม:** เครื่องที่ไม่เคย build และไม่มีซอร์สโค้ด จะรันร้านได้ด้วย `docker pull` เพียงอย่างเดียวหรือไม่ และได้ image ตัวเดียวกันหรือเปล่า?

ใช้ “เครื่อง B” ซึ่งเป็น Docker host อีกเครื่องที่ไม่ใช่ devtools ตัวเดิม เช่น Docker Desktop บนเครื่องหลักของนักศึกษา หรือเครื่องของเพื่อน **ไม่ต้อง login** เพราะ repository เป็น Public:

```bash
docker image ls
time docker pull <DOCKER_USER>/catfood-shop:1
docker image inspect --format '{{index .RepoDigests 0}}' <DOCKER_USER>/catfood-shop:1
docker run -d --name catfood-web -p 3001:3000 <DOCKER_USER>/catfood-shop:1
docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'
```

✅ **ผลการทดลองจริง** (`docker image ls` ว่างเปล่า เครื่อง B ยังไม่มี image ใดเลย):

```text
1: Pulling from <DOCKER_USER>/catfood-shop
...: Pull complete                        (รวม 9 layers)
Digest: sha256:7803b4edfb8a3a4e5ecba20ff545d24a0f58d17366793509d464bc52cf56ae76
Status: Downloaded newer image for <DOCKER_USER>/catfood-shop:1
docker.io/<DOCKER_USER>/catfood-shop:1

real    0m10.540s

<DOCKER_USER>/catfood-shop@sha256:7803b4edfb8a3a4e5ecba20ff545d24a0f58d17366793509d464bc52cf56ae76

NAMES         IMAGE                          STATUS                  PORTS
catfood-web   <DOCKER_USER>/catfood-shop:1   Up 1 second (healthy)   0.0.0.0:3001->3000/tcp
```

เปิด **http://localhost:3001** (เครื่อง B) คู่กับ **http://localhost:3000** (devtools ที่ Jenkins deploy) แล้วเทียบส่วน Deployment info

![สองเครื่อง digest เดียวกัน](./images/lab3_s09_two_servers_same_digest.png)

*ภาพที่ 31 Server A (deploy โดย Jenkins) และ Server B (pull อย่างเดียว) แสดง version/build/เวลา build เหมือนกันทุกช่อง ต่างกันเฉพาะ container ID*

> 🔍 **วิเคราะห์ผล:** digest บนเครื่อง B (`7803b4ed…`) ตรงกับที่ Jenkins push และที่ Docker Hub แสดง จึงยืนยันได้ว่าเป็น **image ตัวเดียวกันทุกบิต** แม้แต่เวลา build ก็เป็นเวลาเดียวกัน เพราะค่านี้ถูกอบเข้า image ตอน build ไม่ได้สร้างใหม่ตอนรัน เครื่อง B ใช้เวลา pull 10.5 วินาที และ container ขึ้น `(healthy)` ทันที โดยไม่ต้องมี Node.js, `npm` หรือซอร์สโค้ดเลย นี่คือความหมายของ *build once, run anywhere*

---

## ช่วง E — ออกเวอร์ชันใหม่และย้อนกลับ

### การทดลองที่ 10 — ออก v1.1.0: อะไรถูกสร้างใหม่และอะไรถูกใช้ซ้ำ?

**คำถาม:** เมื่อเปลี่ยนเพียงเลขเวอร์ชัน build และ push ครั้งที่สองต้องทำงานเท่าไร?

1. เปิด job `docker-build-push` แล้วเลือก **Build with Parameters**

![Build with Parameters](./images/lab3_s10a_build_with_parameters_menu.png)

*ภาพที่ 32 หลัง build แรก Jenkins ลงทะเบียน parameter แล้ว เมนูจึงเปลี่ยนเป็น Build with Parameters*

2. กรอก `APP_VERSION` = `1.1.0` แล้วกด **Build**

![กรอก APP_VERSION 1.1.0](./images/lab3_s10b_build_param_110.png)

*ภาพที่ 33 เปลี่ยนเฉพาะเลขเวอร์ชัน ซอร์สโค้ดเหมือนเดิมทุกไฟล์*

![Pipeline Graph build #2](./images/lab3_s10c_pipeline_graph_b2.png)

*ภาพที่ 34 build #2 ผ่านครบทุก stage ในเวลารวม 22.3 วินาที (Connect devtools 0.35 s · Build image 1.1 s · Test image 2.9 s · Push 12.4 s · Pull & Deploy 4.8 s)*

3. เปิด **Console Output** ของ build #2 แล้วอ่านช่วง Build image และ Push

![CACHED และ Layer already exists ใน console build #2](./images/lab3_s10e_console_cache_b2.png)

*ภาพที่ 35 console ของ build #2: `#6`–`#10 CACHED` ครบทั้ง 5 ขั้นที่สร้างไฟล์ ตามด้วย `Layer already exists` ทุก layer และ `2: digest: sha256:0f85c4beb07e4dc055fe3b231148cb8cf1adbef9f1540cb3bb4fcba492afe5a6 size: 2006`*

✅ **ผลการทดลองจริง** (นับจาก console ของ build #2): ขั้น `CACHED` 5 ขั้น, `Layer already exists` 18 บรรทัด (9 layers × 2 tags), `Pushed` **0** บรรทัด และ digest ใหม่ `sha256:0f85c4beb07e…`

4. เปิดหน้า Tags บน Docker Hub อีกครั้ง

![Docker Hub หลัง build #2](./images/lab3_s10d_hub_tags_b2.png)

*ภาพที่ 36 tag `latest` ย้ายมาชี้ digest ใหม่ `0f85c4beb07e` (กรอบเขียว) เหมือน tag `2` ส่วน tag `1` ยังชี้ `7803b4edfb8a` (กรอบแดง) เหมือนเดิม*

5. refresh **http://localhost:3000** — chip บนแถบด้านบนเปลี่ยนเป็น `v1.1.0 · build #2`

| วัดค่า | build #1 | build #2 |
|---|---:|---:|
| ระยะเวลารวม | 23.0 s | 22.3 s |
| stage `Build image` | 1.9 s | 1.1 s |
| ขั้นที่ `CACHED` | 5 | 5 |
| บรรทัด `Pushed` (layer ที่อัปโหลดใหม่) | 0 | **0** |
| บรรทัด `Layer already exists` | 18 | 18 (9 layers × 2 tags) |
| digest | `7803b4edfb8a…` | `0f85c4beb07e…` |

> 📝 ตัวเลข `Pushed` = 0 ของ build #1 เป็นผลเฉพาะ repository ของผู้เขียนที่มี layer ชุดนี้อยู่แล้ว ครั้งแรกที่นักศึกษา push ขึ้น repository ว่าง layer ทั้ง 9 จะขึ้นเป็น `Pushed` (อัปโหลดจริงราว 146 MB) แต่ build #2 ของนักศึกษาจะได้ `Pushed` = 0 เช่นเดียวกับตารางนี้ ซึ่งเป็นหลักฐานว่า registry เก็บ layer แบบไม่ซ้ำ (content-addressable)

> 🔍 **วิเคราะห์ผล:** build #2 เปลี่ยนเพียงค่า `ENV` (เวอร์ชัน เลข build และเวลา build) ซึ่งเป็น metadata ใน image config ไม่ใช่ layer ของระบบไฟล์ ทั้ง 5 ขั้นที่สร้างไฟล์จึงขึ้น `CACHED` และทั้ง 9 layer มีอยู่บน Docker Hub แล้ว สิ่งที่ต้องอัปโหลดใหม่มีเพียง config กับ manifest ขนาดเล็ก digest จึงเปลี่ยนจาก `7803…` เป็น `0f85…` ทั้งที่ไม่มี layer ใดต้องอัปโหลด นี่คือผลของการวาง `ARG/ENV` ที่เปลี่ยนบ่อยไว้ท้าย Dockerfile ถ้าย้ายสองบรรทัดนี้ไปไว้ต้นไฟล์ ทุก layer หลังจากนั้น (`npm ci`, `next build`) จะต้องสร้างใหม่และอัปโหลดใหม่ทุกครั้ง เวลาส่วนใหญ่ของ Pipeline (ราว 12 วินาที) จึงอยู่ที่การคุยกับ Docker Hub ไม่ใช่การ build

### การทดลองที่ 11 — Rollback ใช้เวลาเท่าไร?

**คำถาม:** ถ้า v1.1.0 มีปัญหา จะย้อนกลับไป v1.0.0 ได้เร็วแค่ไหน?

เพราะ image ของทุกเวอร์ชันยังอยู่บน Docker Hub การ rollback จึงเป็นแค่การรัน container จาก tag เก่า ไม่ต้อง build ใหม่ รันใน shell ของ devtools (วัดเวลาจนกว่า Docker จะรายงาน `healthy`):

```bash
time (
docker rm -f catfood-web
docker run -d --name catfood-web --restart unless-stopped -p 3000:3000 docker.io/<DOCKER_USER>/catfood-shop:1
until [ "$(docker inspect -f '{{.State.Health.Status}}' catfood-web)" = healthy ]; do sleep 0.5; done
)
```

✅ **ผลการทดลองจริง:**

```text
catfood-web
e1e38fd074cff9d56d162911f4b79df6b77ed0423af9a4bb55a52b7094ba777d

real    0m1.709s
```

refresh **http://localhost:3000** — chip เปลี่ยนกลับเป็น `v1.0.0 · build #1`

![release และ rollback](./images/lab3_s11_release_and_rollback.png)

*ภาพที่ 37 ซ้าย: หลัง build #2 chip แสดง `v1.1.0 · build #2` ขวา: หลัง rollback เหลือ `v1.0.0 · build #1` ภายใน 1.7 วินาที*

> 🔍 **วิเคราะห์ผล:** rollback เร็วเพราะ image `:1` ยังอยู่ในเครื่อง (stage Pull & Deploy ของ build #2 ลบเฉพาะ tag `2` และ `latest` ก่อน pull) ถ้าไม่มี Docker จะ pull จาก Docker Hub ให้อัตโนมัติ (ใช้เวลาเพิ่มราว 10 วินาทีตามผลการทดลองที่ 9) สังเกตว่า tag `latest` บน Docker Hub ยังชี้ build #2 อยู่ การ rollback แบบนี้จึงเป็นการแก้ชั่วคราวที่ต้องบันทึกไว้ให้ทีมรู้

**Roll forward กลับสู่เวอร์ชันล่าสุด:**

```bash
time (
docker pull docker.io/<DOCKER_USER>/catfood-shop:latest
docker rm -f catfood-web
docker run -d --name catfood-web --restart unless-stopped -p 3000:3000 docker.io/<DOCKER_USER>/catfood-shop:latest
until [ "$(docker inspect -f '{{.State.Health.Status}}' catfood-web)" = healthy ]; do sleep 0.5; done
)
```

ผลจริงใช้เวลาราว 3.2 วินาที (มีขั้น pull เพิ่มเข้ามา) refresh หน้าเว็บแล้ว chip กลับเป็น `v1.1.0 · build #2`

### ✅ ตรวจปิดแล็บด้วยตา

ตรวจทีละข้อ ทุกข้อต้องเป็นจริงจึงถือว่าจบแล็บ

- [ ] **Jenkins:** job `docker-build-push` มี build #2 สีเขียว หน้า Stages แสดงครบ 5 stage (Connect devtools → Build image → Test image → Push → Pull & Deploy)
- [ ] **Credentials:** หน้า Manage Jenkins → Credentials แสดง `devtools-ssh` และ `dockerhub` โดยไม่แสดง private key หรือ token
- [ ] **Digest:** Console Output ของ build #2 มีบรรทัด `latest: digest: sha256:0f85c4beb07e…` และหน้า Tags บน Docker Hub แสดง tag `latest` ด้วย digest 12 ตัวแรก `0f85c4beb07e` ตรงกัน
- [ ] **ร้าน:** http://localhost:3000 แสดง chip `v1.1.0 · build #2`
- [ ] **Jenkins ยังสะอาด:** `docker exec jenkins sh -c 'docker version'` ยังได้ `docker: not found` (Jenkins ไม่เคยได้ Docker เพิ่ม)
- [ ] **Container:** `docker ps` บน devtools แสดง `catfood-web` ที่ STATUS มี `(healthy)`

---

## 📊 สรุปผลการทดลอง

| # | คำถาม | ผลจริง | ข้อสรุป |
|---|---|---|---|
| 1 | Jenkins มี Docker / ssh ไหม | `docker: not found` exit 127, มี `OpenSSH_10.0p2` | ไม่ต้องเพิ่ม Docker ใช้ SSH ที่มีอยู่แล้ว |
| 2 | Jenkins จะพิสูจน์ตัวตนอย่างไร | key คู่ ed25519: private 411 B, public 101 B | private key ให้ Jenkins, public key ให้ devtools |
| 3 | Jenkins มองเห็น devtools ไหม | `172.18.0.1 devtools`, `Permission denied (publickey,password)`, job เดิมยังอยู่ | เครือข่ายใช้ได้ รอเพียง key, state อยู่ใน volume |
| 4 | Dockerfile single-stage มีอะไรบ้าง | 693 MB, `npm ci` 357 MB, `(healthy)` ใน 3 s, build ซ้ำ 1 s | dependency คือ layer ใหญ่สุด ต้องวางให้ใช้ cache ได้ |
| 5 | ความลับเก็บที่ไหน | `devtools-ssh` + `dockerhub` ใน Credentials, หน้าเว็บไม่แสดงความลับ | โค้ดอ้างถึงด้วย ID เท่านั้น |
| 6–7 | Pipeline ทำงานครบไหม | SUCCESS ใน 23.0 s, hostname `efd5852c2216`, digest `7803b4ed…` | Jenkins สั่ง devtools build → test → push → pull → deploy อัตโนมัติ |
| 8 | Docker Hub ตรงกับ console ไหม | digest `7803b4edfb8a` ตรงกัน, 146.53 MB | ตรวจย้อนได้ด้วย digest (`--provenance=false`) |
| 9 | เครื่องอื่นรันได้ไหม | pull 10.5 s, digest เดียวกัน, `(healthy)` | build once, run anywhere |
| 10 | build ใหม่ทำงานซ้ำแค่ไหน | 5 ขั้น `CACHED`, 0 layer ต้องอัปโหลด, digest `0f85c4be…` | ลำดับ Dockerfile มีผลต่อความเร็ว |
| 11 | rollback เร็วแค่ไหน | 1.7 วินาที (roll forward 3.2 วินาที) | image ทุกเวอร์ชันคือจุดย้อนกลับ |

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `Could not resolve hostname devtools` ใน stage Connect devtools | สร้าง container `jenkins` โดยไม่มี `--add-host devtools:host-gateway` | ทำการทดลองที่ 3 ใหม่ แล้วตรวจด้วย `docker exec jenkins getent hosts devtools` |
| `Permission denied (publickey,password)` ใน stage Connect devtools | public key ไม่อยู่ใน `~/.ssh/authorized_keys` ของ devtools, วาง private key ผิดไฟล์/ไม่ครบบรรทัด BEGIN/END หรือ credential ID ไม่ใช่ `devtools-ssh` | ทำการทดลองที่ 2 ใหม่ แล้วแก้ credential `devtools-ssh` ให้เป็นเนื้อหาของ `~/.ssh/jenkins_devtools` ทั้งไฟล์ |
| `No such DSL method 'credentials'` หรือ `CredentialsNotFound` / `devtools-ssh` | สะกด ID ของ credential ไม่ตรงกับ Jenkinsfile | เปิดหน้า Credentials ตรวจว่า ID เป็น `devtools-ssh` และ `dockerhub` ตรงตัว |
| `docker: not found` ใน Pipeline | มีคำสั่ง `docker` ที่รันตรงบน Jenkins โดยไม่ผ่าน `ssh` | ใช้ Jenkinsfile ของแล็บ ทุกคำสั่ง Docker ต้องอยู่หลัง `ssh -i "$SSH_KEY" ... "$DEVTOOLS"` |
| stage Test image ล้ม health เป็น `unhealthy` หรือไม่ถึง `healthy` ภายใน 30 ครั้ง | แอปใน container เริ่มไม่ขึ้น | ใน shell ของ devtools สั่ง `docker run -d --name catfood-test-N catfood-shop:N` แล้ว `docker logs catfood-test-N` เพื่ออ่านสาเหตุ (Pipeline ลบ container ทดสอบทิ้งเสมอ) |
| `Bind for 0.0.0.0:3000 failed` ตอน Pull & Deploy หลังการทดลองที่ 4 | ลืมลบ `catfood-local` ที่ยังจอง port 3000 | `docker rm -f catfood-local` แล้วสั่ง build ใหม่ |
| `Bind for 0.0.0.0:3000 failed: port is already allocated` (กรณีอื่น) | มี container อื่นใช้ port 3000 | `docker ps --filter publish=3000` แล้วลบตัวที่ไม่ใช้ |
| `401 Unauthorized` / `denied: requested access` | token ผิด หมดอายุ ไม่มีสิทธิ์ Write หรือ username ไม่ตรง | สร้าง token Read & Write ใหม่แล้วแก้ credential `dockerhub` |
| digest บนหน้า Docker Hub ไม่ตรงกับ console | build โดยไม่มี `--provenance=false` จึง push เป็น index ที่มี attestation | ใช้ Jenkinsfile ของแล็บ (มี `docker build --provenance=false`) แล้วสั่ง build ใหม่ |
| เว็บขึ้น `vdev` แทนเวอร์ชัน | Jenkinsfile ไม่มี `VERSION = "${params.APP_VERSION}"` | ใช้ Jenkinsfile ของแล็บ build แรกของ job ยังไม่มี `$APP_VERSION` ใน shell |
| `429 Too Many Requests` | Docker Hub rate limit | รอ แล้วลดความถี่ในการสั่ง build |
| เปิด `localhost:3000` จากเครื่องหลักไม่ได้ | devtools ไม่ได้ publish port 3000 | สร้าง devtools ใหม่ตาม LAB 1 ส่วนที่ 0 (ต้องมี `-p 3000:3000`) |
| หน้า Tags บน Docker Hub ว่าง / 404 | repository เป็น Private หรือ URL ผิด | ตั้ง `catfood-shop` เป็น Public แล้ว refresh |
| หน้าเว็บยังแสดง `build #1` ตอนตรวจปิดแล็บ | ยังอยู่ในสถานะ rollback | roll forward ด้วย `:latest` ตามท้ายการทดลองที่ 11 |

## สรุป

LAB 3 แยกหน้าที่ให้ชัดเจน: **Jenkins สั่ง devtools ทำ** Jenkins ยังเป็น image มาตรฐาน `jenkins/jenkins:lts-jdk21` ที่ไม่มี Docker อยู่ข้างใน ถือเพียง SSH key และ Docker Hub token ไว้ใน Credentials แล้วส่งคำสั่งผ่าน SSH ไปให้ devtools ซึ่งเป็นเจ้าของ Docker daemon ซอร์สโค้ด และ build cache เป็นผู้ build ทดสอบ push และ deploy ผลการทดลองยืนยันว่า image ขนาด 693 MB มี `npm ci` เป็น layer ใหญ่ที่สุด การเรียงคำสั่งให้ dependency ใช้ cache ได้ทำให้ build #2 ขึ้น `CACHED` ครบและไม่มี layer ต้องอัปโหลดใหม่ HEALTHCHECK ของ Docker ทำให้ทั้ง Pipeline และนักศึกษารู้ได้ว่า container พร้อมใช้งานหรือยัง image ย้ายไปรันเครื่องอื่นได้ด้วย digest เดียวกัน และ rollback ได้ใน 1.7 วินาที ทุกผลลัพธ์ตรวจได้ด้วยตาจากหน้า Jenkins, Console Output, Docker Hub และหน้าร้านเอง

ข้อจำกัดที่เหลืออยู่คือซอร์สโค้ดยังมาจากโฟลเดอร์บน devtools และต้องกด Build เอง **LAB 4** จะย้ายซอร์สร้านเดียวกันนี้ขึ้น GitHub ให้ Jenkins อ่าน `Jenkinsfile` จาก repository และ build ใหม่อัตโนมัติทุกครั้งที่มี commit
