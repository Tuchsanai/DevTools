# LAB 3 — สร้าง image ของหน้าเว็บด้วย multi-stage

> โฟลเดอร์ `003_LAB_Build_The_Web` · ไฟล์ของแล็บ : `web/Dockerfile` · `web/Dockerfile.single` · `web/Dockerfile.shellform` · `web/` (source ของหน้าเว็บ) · `api/` · `db/initdb/` · `verify.sh`

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | image ของหน้าเว็บที่ส่งให้ลูกค้า ทำอย่างไรให้เหลือ **เฉพาะของที่ต้องใช้ตอนรัน** |
| **ต้องผ่านอะไรมาก่อน** | **LAB 1** (ยกฐานข้อมูล · `-e` · `-v`) · **LAB 2** (Dockerfile · layer cache · `docker history` · `docker inspect` หา IP บน default bridge) |
| **เวลา** | ~45 นาที · การทดลอง **9 อัน** อันละ 3–5 นาที |
| **จบแล้วต้องทำได้เอง** | อ่านและเขียน Dockerfile หลาย stage · บอกได้ว่าค่าไหนต้องมาตอน **build** ค่าไหนอ่านตอน **run** · พิสูจน์ได้ว่า image ที่ส่งมอบไม่ได้แบก toolchain · ตรวจได้ว่า CSS มาถึงเบราว์เซอร์จริง |
| **แล็บนี้ยัง *ไม่* สอน** | เรียกกันด้วย **ชื่อ** บน user-defined network → **LAB 4** (แล็บนี้ยังต่อกันด้วย IP แบบ LAB 2) · `compose.yaml` · `healthcheck` · `tag`/`push` ขึ้น registry → **LAB 5** |

---

## ทฤษฎีก่อนลงมือ

**โจทย์จากลูกค้า** : *"ผมอยากเห็นหน้าจอเดียวที่บอกว่าตอนนี้มีงานอะไรอยู่ในมือใครบ้าง"* (US-2 ใน `../docs/01_requirements.md`)
→ ต้องเอา `web` ใส่**กล่อง** และ image ที่ส่งมอบต้องไม่แบกเครื่องมือ build ไปด้วย

| ข้อจำกัดของงานจริง | เทคนิคที่เลือกใช้ |
|---|---|
| ลูกค้าไม่มีฝ่าย IT · เครื่องปลายทางไม่ควรมี Node ติดตั้ง | ใส่ `web` ลงกล่อง แล้วส่งเป็น image |
| image ที่ส่งมอบต้องเล็กและไม่มีเครื่องมือส่วนเกิน | **multi-stage** — stage build ถูกทิ้ง เหลือแต่ผลลัพธ์ |
| ชื่อระบบบนหัวเว็บเปลี่ยนได้ตอนส่งมอบ | `ARG` → ฝังตอน **build** |
| ที่อยู่ของบริการเบื้องหลังเปลี่ยนตามที่ติดตั้ง | `ENV` → อ่านตอน **run** |
| `docker stop` ต้องปิดงานให้จบ ไม่ใช่ถูกฆ่าทิ้ง | `CMD` **exec form** ให้ node เป็น PID 1 |

### สาม stage ของ `web/Dockerfile`

![แผนภาพ multi-stage : ฝั่งซ้ายคือ stage deps กับ builder ที่มี node_modules 505MB devDependencies typescript tailwindcss และ cache ของ next build 100MB ซึ่งถูกทิ้งทั้งก้อน ฝั่งขวาคือ stage runner ที่มี node:22-alpine 232MB บวก .next/standalone 49.7MB และ .next/static 680kB รวมเป็น image 298MB](./images/theory-multistage.svg)

> 🖼 **วิธีอ่านรูปนี้:** ลูกศร `COPY --from=builder` ตรงกลางขน **เฉพาะผลลัพธ์** ข้ามฝั่ง — ทุกอย่างในกรอบสีส้มฝั่งซ้ายไม่มีอะไรตามไปเลยแม้แต่ layer เดียว

| stage | ทำอะไร | อะไรตามไป stage สุดท้าย |
|---|---|---|
| `deps` | `npm ci` ติดตั้ง dependency ครบทุกตัว | ไม่มีเลย |
| `builder` | `npm run build` แปลง `.tsx` เป็นไฟล์ที่รันได้ | เฉพาะ `.next/standalone` และ `.next/static` |
| `runner` | ตั้งผู้ใช้ธรรมดา · `CMD ["node","server.js"]` | คือ image ที่ส่งมอบ |

> `output: "standalone"` ใน `next.config.ts` คือกุญแจ — Next รวม `server.js` กับ `node_modules` **เท่าที่ใช้จริง** ไว้ให้แล้ว
> stage สุดท้ายจึงหยิบไปวางได้เลยโดยไม่ต้อง `npm install` ซ้ำ

### `ARG` ตอน build กับ `ENV` ตอน run

![เส้นเวลาเทียบ ARG กับ ENV : จุด docker build ทางซ้ายผูกกับ ARG NEXT_PUBLIC_SITE_NAME ที่ถูกฝังลงไฟล์ผลลัพธ์จึงเปลี่ยนด้วย --build-arg เท่านั้น ส่วนจุด docker run ทางขวาผูกกับ ENV API_BASE_URL ที่อ่านใหม่ทุกครั้งที่สร้างกล่อง](./images/theory-arg-vs-env.svg)

> 🖼 **วิธีอ่านรูปนี้:** สองแถบล่างคือค่าคนละชนิดบนเส้นเวลาเดียวกัน — แถบสีส้มผูกกับจุด `docker build` ส่วนแถบสีเขียวผูกกับจุด `docker run` · ค่าที่ผูกกับ build เปลี่ยนตอน run ไม่ได้

| | `NEXT_PUBLIC_SITE_NAME` | `API_BASE_URL` |
|---|---|---|
| ประกาศไว้ที่ | `ARG` + `ENV` ใน stage `builder` | `-e` ตอน `docker run` |
| ถูกอ่านเมื่อ | ตอน `npm run build` | ตอนกล่องเริ่มทำงาน |
| เปลี่ยนค่าอย่างไร | `docker build --build-arg ...` (ต้อง build ใหม่) | `docker run -e ...` (image ก้อนเดิม) |

### `CMD` exec form กับสัญญาณ `SIGTERM`

`docker stop` ส่ง `SIGTERM` ให้ **process หมายเลข 1** ของกล่องเท่านั้น แล้วรอ 10 วินาที ถ้ายังไม่จบจึงส่ง `SIGKILL`

| รูปแบบ | สิ่งที่เป็น PID 1 | ผลตอน `docker stop` |
|---|---|---|
| `CMD ["node","server.js"]` (exec form) | `node` | ได้รับสัญญาณตรง ๆ จบทันที |
| `CMD node server.js; echo stopped` (shell form) | `/bin/sh` | `sh` รับสัญญาณแล้วไม่ส่งต่อ → รอครบ 10 วินาทีแล้วถูกฆ่า |

### กับดักของ Next.js 16 : `.next/static` ต้องยกมาทั้งก้อน

![แผนภาพกับดักการ COPY ไฟล์ static : แถบบนบอกว่าของจริงมีโฟลเดอร์ chunks ที่เก็บทั้ง js และ css กับโฟลเดอร์ build-id ส่วน .next/static/css ไม่มีอยู่จริง ฝั่งซ้ายคัดลอกทั้งก้อนแล้วได้ CSS 200 ฝั่งขวาเจาะ subfolder แล้ว build ล้มหรือได้หน้าเว็บไม่มี CSS](./images/theory-static-copy-trap.svg)

> 🖼 **วิธีอ่านรูปนี้:** กล่องแดงมุมขวาบนคือโฟลเดอร์ที่ตำราส่วนใหญ่บอกให้ copy — แต่ **ไม่มีอยู่จริง** ใน Next.js 16 · ไฟล์ `.css` ถูกวางปนอยู่กับ `.js` ใน `chunks/`

### สิ่งที่มักเข้าใจผิด

- **คิดว่า** ค่า `NEXT_PUBLIC_*` เปลี่ยนได้ด้วย `-e` ตอน `docker run` → **จริง ๆ** ถูกฝังลงไฟล์ไปแล้วตั้งแต่ตอน build (การทดลองที่ 5)
- **คิดว่า** shell form กับ exec form ต่างกันแค่รูปแบบการเขียน → **จริง ๆ** ต่างกันที่ใครเป็น PID 1 และผลคือ `docker stop` ช้าไป 10 วินาที (การทดลองที่ 7)
- **คิดว่า** ไฟล์ CSS ของ Next อยู่ที่ `.next/static/css` → **จริง ๆ** อยู่ที่ `.next/static/chunks` (การทดลองที่ 9)
- **คิดว่า** multi-stage ทำให้ทุกแอปเล็กลงอัตโนมัติ → **จริง ๆ** ต้องเลือกเองว่าจะขน artifact ชิ้นไหนเข้า stage สุดท้าย (การทดลองที่ 3)

---

## เตรียมเครื่องเรียน

### ขั้นที่ 1 — เปิดกล่องเรียน

รันบน **เครื่องของเราเอง** :

```bash
docker rm -f devtools-ops-lab3 2>/dev/null
docker run -dit --name devtools-ops-lab3 --privileged \
  -p 2240:22 -p 8189:3000 tuchsanai/devtools:2569_1
ssh root@localhost -p 2240        # password : passwd
```

> พอร์ต `8189` ของเครื่องเราถูกต่อเข้ากับพอร์ต `3000` ของกล่องเรียน — พอถึงการทดลองที่ 8 กล่องหน้าเว็บจะจองพอร์ต `3000` ในกล่องเรียน ทำให้เปิด `http://localhost:8189` บนเบราว์เซอร์ของเราได้

### ขั้นที่ 2 — โหลดโค้ดแล็บ

**คำสั่งทุกอันหลังจากนี้พิมพ์ข้างในกล่องเรียน**

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone --depth 1 https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/03_Fullstack_App_Example/003_LAB_Build_The_Web
ls
```

> repo ก้อนนี้ใหญ่หลายร้อยเมกะไบต์ · `--depth 1` โหลดมาแค่ commit ล่าสุด ทำให้เสร็จในไม่กี่สิบวินาทีแทนที่จะเป็นหลายนาที

✅ **สิ่งที่ต้องเห็น** — โฟลเดอร์ของสามกล่อง พร้อมเอกสารและสคริปต์ตรวจงาน รวม 6 รายการ :

```
api
db
images
readme.md
verify.sh
web
```

> 📝 `web/` คือ source ของหน้าเว็บ (Next.js 16.3.1) · `api/` กับ `db/` คือของเดิมจาก LAB 1–2 ที่ยกมาใช้ประกอบในการทดลองที่ 8

---

## การทดลองที่ 1 — สาม stage ในไฟล์เดียว

**คำถาม:** `web/Dockerfile` แบ่งเป็นกี่ stage และ stage สุดท้ายหยิบอะไรข้ามมาบ้าง

```bash
grep -n '^FROM\|^COPY --from' web/Dockerfile
```

✅ **สิ่งที่ต้องเห็น** — `FROM` **3 ครั้ง** = 3 stage และมี `COPY --from` ขนของข้าม stage 3 บรรทัด (เลขบรรทัดตรงกันทุกคน) :

```
11:FROM node:22-alpine AS deps
21:FROM node:22-alpine AS builder
30:COPY --from=deps /app/node_modules ./node_modules
35:FROM node:22-alpine AS runner
47:COPY --from=builder --chown=webapp:webapp /app/.next/standalone ./
53:COPY --from=builder --chown=webapp:webapp /app/.next/static ./.next/static
```

> 📝 **`FROM` กี่ครั้ง = กี่ stage** · stage ที่ไม่มีใคร `COPY --from` ไปใช้และไม่ใช่ stage สุดท้าย จะถูกทิ้งทั้งก้อน · ชื่อหลัง `AS` มีไว้อ้างถึงเท่านั้น

---

## การทดลองที่ 2 — build แบบ stage เดียวก่อน

**คำถาม:** ถ้าไม่แยก stage เลย image จะใหญ่แค่ไหน

```bash
time docker build -f web/Dockerfile.single -t campusops-web:single ./web
docker image ls campusops-web
```

✅ **สิ่งที่ต้องเห็น** — build ผ่าน และ **`DISK USAGE` ทะลุ 1 GB** (เวลาและ ID ของแต่ละคนไม่ตรงกัน) :

```
#13 naming to docker.io/library/campusops-web:single done
#13 DONE 11.8s

real	0m36.686s

IMAGE                  ID             DISK USAGE   CONTENT SIZE   EXTRA
campusops-web:single   da97f9ae8dcd       1.09GB          310MB
```

> 📝 ไฟล์นี้ทำงานได้จริง หน้าเว็บขึ้นครบเหมือนกัน — ปัญหาคือมันแบก `node_modules` เต็มก้อน · `typescript` · `tailwindcss` · source `.tsx` และ cache ของ `next build` ไปด้วยทั้งหมด

---

## การทดลองที่ 3 — build แบบ multi-stage แล้วเทียบขนาด

**คำถาม:** ผลลัพธ์เหมือนกัน แต่ image ต่างกันเท่าไร

```bash
time docker build -t campusops-web:lab3 ./web
docker image ls campusops-web
```

✅ **สิ่งที่ต้องเห็น** — **1.09GB → 298MB** จากไฟล์ source ชุดเดียวกันเป๊ะ :

```
IMAGE                  ID             DISK USAGE   CONTENT SIZE   EXTRA
campusops-web:lab3     9d74ea055358        298MB         73.2MB
campusops-web:single   da97f9ae8dcd       1.09GB          310MB
```

> 📝 **เล็กลง ~73%** · Docker 29 แยกสองคอลัมน์ : `DISK USAGE` คือพื้นที่จริงบนดิสก์ (นับ layer ของ base ที่ใช้ร่วมกันด้วย) ส่วน `CONTENT SIZE` คือเนื้อของ image เอง — ดูคอลัมน์ไหนก็ได้ ขอให้เทียบคอลัมน์เดียวกัน

---

## การทดลองที่ 4 — stage สุดท้ายเหลืออะไรบ้าง

**คำถาม:** ขั้น `npm ci` กับ `npm run build` ติดมากับ image ที่จะส่งมอบไหม

```bash
docker history campusops-web:lab3
```

✅ **สิ่งที่ต้องเห็น** — **ไม่มีบรรทัด `npm` เลยแม้แต่บรรทัดเดียว** ของเราเองมีแค่ 4 layer (เวลาและ ID ของแต่ละคนไม่ตรงกัน) :

```
IMAGE          CREATED              CREATED BY                                      SIZE      COMMENT
9d74ea055358   6 seconds ago        CMD ["node" "server.js"]                        0B        buildkit.dockerfile.v0
<missing>      6 seconds ago        EXPOSE [3000/tcp]                               0B        buildkit.dockerfile.v0
<missing>      6 seconds ago        USER webapp                                     0B        buildkit.dockerfile.v0
<missing>      6 seconds ago        COPY --chown=webapp:webapp /app/.next/static…   680kB     buildkit.dockerfile.v0
<missing>      6 seconds ago        COPY --chown=webapp:webapp /app/.next/standa…   49.7MB    buildkit.dockerfile.v0
<missing>      25 seconds ago       RUN /bin/sh -c addgroup -g 10001 -S webapp &…   41kB      buildkit.dockerfile.v0
<missing>      25 seconds ago       ENV NODE_ENV=production NEXT_TELEMETRY_DISAB…   0B        buildkit.dockerfile.v0
<missing>      About a minute ago   WORKDIR /app                                    8.19kB    buildkit.dockerfile.v0
<missing>      2 weeks ago          CMD ["node"]                                    0B        buildkit.dockerfile.v0
<missing>      2 weeks ago          ENTRYPOINT ["docker-entrypoint.sh"]             0B        buildkit.dockerfile.v0
<missing>      2 weeks ago          COPY docker-entrypoint.sh /usr/local/bin/ # …   20.5kB    buildkit.dockerfile.v0
<missing>      2 weeks ago          RUN /bin/sh -c apk add --no-cache --virtual …   5.48MB    buildkit.dockerfile.v0
<missing>      2 weeks ago          ENV YARN_VERSION=1.22.22                        0B        buildkit.dockerfile.v0
<missing>      2 weeks ago          RUN /bin/sh -c addgroup -g 1000 node     && …   160MB     buildkit.dockerfile.v0
<missing>      2 weeks ago          ENV NODE_VERSION=22.23.2                        0B        buildkit.dockerfile.v0
<missing>      2 months ago         CMD ["/bin/sh"]                                 0B        buildkit.dockerfile.v0
<missing>      2 months ago         ADD alpine-minirootfs-3.24.1-x86_64.tar.gz /…   9.07MB    buildkit.dockerfile.v0
```

เก้าบรรทัดล่างสุดคือ base `node:22-alpine` · แปดบรรทัดบนคือของ `web/Dockerfile` เอง ซึ่ง **มีขนาดจริงแค่ 4 บรรทัด** : `680kB` · `49.7MB` · `41kB` · `8.19kB`

พิสูจน์อีกชั้นว่าเครื่องมือ build ไม่ตามมา :

```bash
docker run --rm campusops-web:lab3 sh -c 'ls node_modules | wc -l; ls -d node_modules/typescript'
docker run --rm campusops-web:single sh -c 'ls node_modules | wc -l; ls -d node_modules/typescript'
```

✅ **สิ่งที่ต้องเห็น** — image ที่ส่งมอบมี `node_modules` แค่ **12 รายการ** และ **error คือคำตอบที่ถูกต้อง** ส่วน image แบบ stage เดียวมี 35 รายการ รวม `typescript` :

```
12
ls: node_modules/typescript: No such file or directory
35
node_modules/typescript
```

> 📝 นี่คือคำตอบให้ลูกค้าโดยตรง — **image ที่ส่งมอบไม่มี compiler ไม่มี devDependencies** เหลือแต่ `server.js` กับ dependency ที่ Next รวมมาให้เท่าที่ใช้จริง

---

## การทดลองที่ 5 — ชื่อระบบบนหัวเว็บถูกฝังตั้งแต่ตอน build

**คำถาม:** ตั้ง `NEXT_PUBLIC_SITE_NAME` ใหม่ตอน `docker run` แล้วหน้าเว็บเปลี่ยนตามไหม

```bash
docker run -d --name ops-web-try -e NEXT_PUBLIC_SITE_NAME='ศูนย์ซ่อมบำรุง' campusops-web:lab3 && sleep 4
curl -s http://$(docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' ops-web-try):3000/no-such-page | grep -o '<title>[^<]*</title>' | head -1
```

✅ **สิ่งที่ต้องเห็น** — ยังเป็น `CampusOps` เหมือนเดิม **ไม่สนใจค่าที่เพิ่งส่งเข้าไป** (IP ของแต่ละคนไม่ตรงกัน) :

```
<title>CampusOps · ระบบงานซ่อมและครุภัณฑ์</title>
```

ทีนี้ส่งค่าเดียวกันตอน **build** :

```bash
docker build -q --build-arg NEXT_PUBLIC_SITE_NAME='ศูนย์ซ่อมบำรุง' -t campusops-web:rename ./web && docker run -d --name ops-web-try2 campusops-web:rename && sleep 4
curl -s http://$(docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' ops-web-try2):3000/no-such-page | grep -o '<title>[^<]*</title>' | head -1
```

✅ **สิ่งที่ต้องเห็น** — คราวนี้เปลี่ยนจริง :

```
<title>ศูนย์ซ่อมบำรุง · ระบบงานซ่อมและครุภัณฑ์</title>
```

> 📝 ค่า `NEXT_PUBLIC_*` ถูกแปลงเป็น **ตัวหนังสือคงที่ในไฟล์ผลลัพธ์** ตั้งแต่ `npm run build` · เรียกหน้าที่ไม่มีอยู่จริงเพื่อดูเฉพาะ layout โดยไม่ต้องมี `api`

---

## การทดลองที่ 6 — ที่อยู่ของบริการเบื้องหลังเปลี่ยนได้ตอน run

**คำถาม:** `API_BASE_URL` ต้อง build ใหม่ไหมถ้าอยากเปลี่ยน

```bash
docker run -d --name ops-web-noapi -e API_BASE_URL=http://no-api-yet:8000 campusops-web:lab3 && sleep 4
curl -s -o /dev/null -w 'GET / -> HTTP %{http_code}\n' http://$(docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' ops-web-noapi):3000/
```

✅ **สิ่งที่ต้องเห็น** — image ก้อน**เดิม** ตอบ `500` เพราะไปตามหาโฮสต์ชื่อใหม่ที่ไม่มีอยู่ (ID ของแต่ละคนไม่ตรงกัน) :

```
GET / -> HTTP 500
```

เปิด log ดูว่ามันไปตามหาที่ไหน :

```bash
docker logs ops-web-noapi 2>&1 | grep -A3 'cause'
```

✅ **สิ่งที่ต้องเห็น** — ชื่อโฮสต์ใหม่โผล่ใน log ทันทีโดยไม่ต้อง build ใหม่ (รหัสอาจเป็น `EAI_AGAIN` หรือ `ENOTFOUND` แล้วแต่จังหวะ DNS) :

```
  [cause]: Error: getaddrinfo EAI_AGAIN no-api-yet
      at ignore-listed frames {
    errno: -3001,
    code: 'EAI_AGAIN',
```

> 📝 ค่านี้อยู่ในตัวแปรสภาพแวดล้อมของ process จึงถูกอ่านใหม่ทุกครั้งที่สร้างกล่อง — **image ก้อนเดียวจึงใช้ได้ทั้งเครื่อง dev และเครื่องลูกค้า** เปลี่ยนแค่ `-e` ตอนติดตั้ง

---

## การทดลองที่ 7 — ใครเป็น PID 1 ในกล่อง

**คำถาม:** เขียน `CMD` คนละรูปแบบ แล้วใครได้รับ `SIGTERM` ตอน `docker stop`

ไฟล์ `web/Dockerfile.shellform` มีมาให้แล้วในโฟลเดอร์ — ต่อยอดจาก `campusops-web:lab3` แล้วเปลี่ยนแค่บรรทัด `CMD` ให้เป็น shell form

```bash
docker build -q -f web/Dockerfile.shellform -t campusops-web:shellform ./web && docker run -d --name ops-web-exec campusops-web:lab3 && docker run -d --name ops-web-shell campusops-web:shellform && sleep 4
docker exec ops-web-exec ps -o pid,args; docker exec ops-web-shell ps -o pid,args
```

✅ **สิ่งที่ต้องเห็น** — ฝั่ง exec form `node` เป็น PID 1 · ฝั่ง shell form มี `/bin/sh` คั่นอยู่ที่ PID 1 แล้ว `node` ไปเป็น PID 8 :

```
PID   COMMAND
    1 next-server (v
   19 ps -o pid,args

PID   COMMAND
    1 /bin/sh -c node server.js; echo stopped
    8 next-server (v
   20 ps -o pid,args
```

ทีนี้จับเวลาสั่งหยุดทั้งสองกล่อง :

```bash
time docker stop ops-web-exec
time docker stop ops-web-shell
```

✅ **สิ่งที่ต้องเห็น** — **0.2 วินาที กับ 10.2 วินาที** (ทศนิยมของแต่ละคนไม่ตรงกัน แต่ตัวหน้าต้องเป็น 0 กับ 10) :

```
ops-web-exec
real	0m0.248s

ops-web-shell
real	0m10.239s
```

> 📝 `/bin/sh` รับ `SIGTERM` แล้วไม่ส่งต่อให้ลูก Docker จึงรอครบ **10 วินาที** แล้ว `SIGKILL` ทิ้ง — แอปไม่ได้ปิดงานให้เรียบร้อย · exec form ตัดปัญหานี้ทั้งหมด

เก็บกล่องทดลองของการทดลองที่ 5–7 ออกก่อนไปต่อ :

```bash
docker rm -f ops-web-try ops-web-try2 ops-web-noapi ops-web-exec ops-web-shell
```

---

## การทดลองที่ 8 — ยกครบสามกล่องแล้วเปิดหน้าเว็บ

**คำถาม:** ต่อ `web` เข้ากับ `api` และ `db` ด้วย IP แบบ LAB 2 แล้วหน้าเว็บขึ้นจริงไหม

> ครั้งแรกช้าประมาณ **2 นาที** เพราะกล่องเรียนต้องดึง `postgres:17-alpine` (~424 MB) กับ `python:3.12-slim` มาก่อน แล้วยัง `pip install` ตอน build `campusops-api:lab3` อีก · เงียบไปนานเป็นเรื่องปกติ ยังไม่ค้าง

```bash
docker run -d --name ops-db -e POSTGRES_DB=campusops -e POSTGRES_USER=opsuser -e POSTGRES_PASSWORD=labpass \
  -v ops-pgdata:/var/lib/postgresql/data -v "$PWD/db/initdb:/docker-entrypoint-initdb.d:ro" postgres:17-alpine && sleep 10 \
  && docker build -q -t campusops-api:lab3 ./api && docker run -d --name ops-api \
  -e DATABASE_URL="postgresql://opsuser:labpass@$(docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' ops-db):5432/campusops" \
  campusops-api:lab3 && sleep 6
curl -s http://$(docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' ops-api):8000/health; echo
```

✅ **สิ่งที่ต้องเห็น** — บริการเบื้องหลังต่อฐานข้อมูลติดแล้ว (ID ของแต่ละคนไม่ตรงกัน) :

```
{"status":"ok","db":"up"}
```

ทีนี้ยกหน้าเว็บขึ้น แล้วชี้ `API_BASE_URL` ไปที่ IP ของ `ops-api` :

```bash
docker run -d --name ops-web -p 3000:3000 \
  -e API_BASE_URL="http://$(docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' ops-api):8000" campusops-web:lab3 && sleep 6
for p in / /tickets /loans /parts; do curl -s -o /dev/null -w "GET $p -> HTTP %{http_code} · %{size_download} ไบต์\n" "http://localhost:3000$p"; done
```

✅ **สิ่งที่ต้องเห็น** — ทั้งสี่หน้าตอบ `200` และหน้าแรกมีเนื้อหาจริง ~31 kB (จำนวนไบต์ของแต่ละคนไม่ตรงกันเพราะข้อมูลในฐานข้อมูลต่างกัน) :

```
GET / -> HTTP 200 · 31260 ไบต์
GET /tickets -> HTTP 200
GET /loans -> HTTP 200
GET /parts -> HTTP 200
```

เปิดในเบราว์เซอร์บนเครื่องเราที่ **`http://localhost:8189`** ได้เลย — พอร์ต `3000` ของกล่องเรียนถูกต่อออกมาไว้ตั้งแต่ตอนสร้างกล่อง

> 📝 `web` เรียก `api` จาก **ฝั่ง server** เท่านั้น เบราว์เซอร์จึงไม่ต้องเข้าถึง `api` เลย · `-p 3000:3000` มีที่ `web` กล่องเดียว ส่วน `db` ไม่เคย publish พอร์ตตาม NFR-3

---

## การทดลองที่ 9 — CSS มาถึงเบราว์เซอร์ครบไหม

**คำถาม:** HTML บอกให้โหลดไฟล์ CSS จากที่ไหน และไฟล์นั้นมีอยู่จริงไหม

```bash
CSS=$(curl -s http://localhost:3000/ | grep -o '<link rel="stylesheet" href="[^"]*"' | head -1 | sed 's/.*href="//; s/"$//'); echo "CSS = $CSS"
curl -s -o /dev/null -w "GET $CSS -> HTTP %{http_code} · %{size_download} ไบต์\n" "http://localhost:3000$CSS"
```

✅ **สิ่งที่ต้องเห็น** — เส้นทางอยู่ใต้ **`chunks/`** และโหลดได้ `200` ขนาดหลักหมื่นไบต์ (ชื่อไฟล์ของแต่ละคนไม่ตรงกัน) :

```
CSS = /_next/static/chunks/3sqcqigw583ti.css
GET /_next/static/chunks/3sqcqigw583ti.css -> HTTP 200 · 35235 ไบต์
```

ดูของจริงในกล่องว่าไฟล์วางอยู่ตรงไหน :

```bash
docker exec ops-web sh -c 'ls .next/static; ls .next/static/chunks/*.css; ls .next/static/css'
```

✅ **สิ่งที่ต้องเห็น** — ไฟล์ `.css` อยู่ปนกับ `.js` ใน `chunks/` และ **โฟลเดอร์ `css/` ไม่มีอยู่จริง** (ชื่อโฟลเดอร์ build-id ของแต่ละคนไม่ตรงกัน) :

```
ls: .next/static/css: No such file or directory
HOYpGTajBdkgQ8UcQh0NS
chunks
.next/static/chunks/3sqcqigw583ti.css
```

> 📝 **นี่คือเหตุผลที่ `web/Dockerfile` ต้อง `COPY` `.next/static` ทั้งก้อน** — ตำราส่วนใหญ่สอนให้เจาะ `.next/static/css` ซึ่ง Next.js 16 ไม่มีแล้ว ผลคือ build ล้ม หรือแย่กว่านั้นคือได้หน้าเว็บที่ตอบ `200` ทุกหน้าแต่ไม่มีสีสักจุด

---

## ตรวจงานด้วย `verify.sh`

```bash
bash verify.sh ; echo "exit code = $?"
```

✅ **สิ่งที่ต้องเห็น** — `[PASS]` ทุกบรรทัด ปิดท้าย `ALL CHECKS PASSED` (IP และชื่อไฟล์ CSS ของแต่ละคนไม่ตรงกัน) :

```
[PASS] web/Dockerfile มี FROM 3 ครั้ง = 3 stage (deps · builder · runner)
[PASS] multi-stage เล็กกว่า stage เดียวอย่างน้อย 2 เท่า (content size 73MB vs 310MB)
[PASS] docker history ของ image สุดท้ายไม่มีขั้น npm ci / npm run build เลย
[PASS] image สุดท้ายไม่มี node_modules/typescript — ไม่ได้แบก toolchain ไปด้วย
[PASS] CMD เป็น exec form : ["node","server.js"]
[PASS] โหลดไฟล์ CSS ได้ HTTP 200 ขนาด 35235 ไบต์
[PASS] ไม่มีโฟลเดอร์ .next/static/css จริง — ยืนยันว่าห้าม COPY เจาะ subfolder
----------------------------------------------
ALL CHECKS PASSED
exit code = 0
```

> 📝 สคริปต์สร้างของของตัวเองด้วย prefix `vops-` ทั้งหมด (`vops-db` · `vops-api` · `vops-web`) แล้วลบทิ้งเมื่อจบ — **ไม่แตะกล่อง `ops-` ของเรา** และไม่ต้องใช้พอร์ตบนเครื่องเลยเพราะต่อกันด้วย IP

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `Cannot find module '@tailwindcss/postcss'` ตอน `npm run build` | ตั้ง `ENV NODE_ENV=production` ไว้**ก่อน** `npm ci` → npm ข้าม devDependencies | ย้ายบรรทัด `ENV NODE_ENV=production` ไปไว้**หลัง** `RUN npm run build` |
| `failed to compute cache key: "/app/.next/static/css": not found` | `COPY --from=builder` เจาะโฟลเดอร์ย่อยที่ไม่มีอยู่จริง | คัดลอก `.next/static` **ทั้งก้อน** |
| หน้าเว็บทุกหน้าได้ `200` แต่ไม่มีสีเลย · `GET /_next/static/chunks/xxx.css -> HTTP 404` | ไฟล์ CSS ไม่ได้ถูกคัดลอกเข้า image | ตรวจด้วย `docker exec <กล่อง> ls .next/static/chunks/*.css` แล้วแก้บรรทัด `COPY` |
| `template parsing error: ... map has no entry for key "IPAddress"` | Docker 29 ไม่มี `.NetworkSettings.IPAddress` ชั้นบนสุดแล้ว | ใช้ `-f '{{.NetworkSettings.Networks.bridge.IPAddress}}'` |
| `Error: getaddrinfo ENOTFOUND <ชื่อ>` หรือ `EAI_AGAIN` ใน `docker logs` ของ `web` | `API_BASE_URL` ชี้ไปที่ชื่อที่ default bridge แปลงเป็น IP ไม่ได้ | ใช้ IP จาก `docker inspect` (การเรียกด้วย **ชื่อ** เป็นเรื่องของ **LAB 4**) |
| `ps -o pid,args` ขึ้น `1 /bin/sh -c node server.js; echo stopped` แล้ว `docker stop` กิน `real 0m10.2s` ทุกครั้ง | `CMD` เขียนเป็น shell form → `/bin/sh` เป็น PID 1 แทน `node` | เขียน `CMD` เป็น exec form : `CMD ["node","server.js"]` |
| `Bind for 0.0.0.0:3000 failed: port is already allocated` | มีกล่องเก่าจองพอร์ต `3000` ในกล่องเรียนอยู่ | `docker ps` หาว่าใครจอง แล้ว `docker rm -f <ชื่อ>` |
| ใส่ `-e NEXT_PUBLIC_SITE_NAME=...` แล้ว `<title>` ยังเป็น `<title>CampusOps · ระบบงานซ่อมและครุภัณฑ์</title>` เหมือนเดิม | `NEXT_PUBLIC_*` ถูกฝังลงไฟล์ผลลัพธ์ตอน build ไปแล้ว | `docker build --build-arg NEXT_PUBLIC_SITE_NAME=... ` แล้วรัน image ตัวใหม่ |

---

## เก็บกวาด

**ในกล่องเรียน:**

```bash
docker rm -f ops-web ops-api ops-db
docker volume rm ops-pgdata
docker image rm campusops-web:lab3 campusops-web:single campusops-web:rename campusops-web:shellform campusops-api:lab3
docker ps -a
```

✅ **สิ่งที่ต้องเห็น** — ตารางสุดท้ายเหลือแค่หัวตาราง :

```
ops-web
ops-api
ops-db
ops-pgdata
Untagged: campusops-web:lab3
Untagged: campusops-web:single
CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
```

> 📝 เก็บ `node:22-alpine` · `python:3.12-slim` · `postgres:17-alpine` ไว้ใช้ต่อใน LAB 4–5 ได้ ไม่ต้องลบ

**ออกจากกล่องแล้วลบกล่องบนเครื่องเรา:**

```bash
exit
docker rm -f devtools-ops-lab3
docker ps -a --filter "name=^devtools-"
```

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker build -t <ชื่อ:tag> ./web` | build จาก `Dockerfile` ในโฟลเดอร์ที่เป็น build context |
| `docker build -f web/Dockerfile.single -t <ชื่อ:tag> ./web` | เลือกไฟล์ Dockerfile เองด้วย `-f` โดย context ยังเป็น `./web` |
| `docker build --build-arg KEY=value ...` | ส่งค่าให้ `ARG` ใช้ **ตอน build** — วิธีเดียวที่เปลี่ยนค่าที่ถูกฝังไปแล้ว |
| `docker image ls <repo>` | ดู `DISK USAGE` และ `CONTENT SIZE` ของ image |
| `docker history <image>` | ดูทุก layer ของ image พร้อมขนาดที่แต่ละ layer เพิ่มเข้ามา |
| `docker run --rm <image> sh -c '<คำสั่ง>'` | เปิดกล่องชั่วคราวเพื่อส่องข้างใน image แล้วลบทิ้งทันที |
| `docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' <กล่อง>` | อ่าน IP ของกล่องบน default bridge |
| `docker run -e KEY=value ...` | ตั้งค่า `ENV` **ตอน run** — ไม่ต้อง build ใหม่ |
| `docker exec <กล่อง> ps -o pid,args` | ดูว่า process ไหนเป็น PID 1 ของกล่องนั้น |
| `time docker stop <กล่อง>` | จับเวลาการหยุดกล่อง — ดูบรรทัด `real` |
| `docker logs <กล่อง>` | อ่าน log ของแอปในกล่อง |

> **จำ 4 อย่าง:** `FROM` กี่ครั้ง = กี่ stage · `ARG` ผูกกับ build / `ENV` ผูกกับ run · `CMD` ต้องเป็น exec form · `.next/static` คัดลอกทั้งก้อนเท่านั้น

---

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] `grep -n '^FROM' web/Dockerfile` แล้วบอกได้ว่าแต่ละ stage ทำอะไรและอะไรตามไป stage สุดท้าย
- [ ] build `campusops-web:single` แล้วเห็น `DISK USAGE` ระดับ **1 GB**
- [ ] build `campusops-web:lab3` แล้วเทียบได้ว่าเหลือ **298MB** จาก source ชุดเดียวกัน
- [ ] `docker history campusops-web:lab3` ไม่มีบรรทัด `npm ci` / `npm run build` เลย
- [ ] `ls -d node_modules/typescript` ใน image ที่ส่งมอบ **ต้อง error** แต่ใน `:single` **ต้องเจอ**
- [ ] `-e NEXT_PUBLIC_SITE_NAME=...` ตอน run **ไม่เปลี่ยน** `<title>` แต่ `--build-arg` **เปลี่ยน**
- [ ] `-e API_BASE_URL=...` ตอน run มีผลทันทีโดยไม่ต้อง build ใหม่ (เห็นชื่อโฮสต์ใหม่ใน `docker logs`)
- [ ] `ps -o pid,args` เห็น `node` เป็น PID 1 ฝั่ง exec form และ `time docker stop` ได้ **0.x วิ กับ 10.x วิ**
- [ ] สามกล่องขึ้นครบ ต่อกันด้วย IP · เปิด `http://localhost:8189` เห็นหน้าเว็บจริง · ทั้งสี่หน้าได้ `200`
- [ ] `bash verify.sh` ขึ้น `ALL CHECKS PASSED` และเก็บกวาดจนไม่เหลือกล่อง `ops-` กับ volume `ops-pgdata`

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
