# LAB 5 — Registry : Tag → Push → Pull

> โฟลเดอร์ `005_LAB_Registry_Tag_Push_Pull` · ไฟล์ของแล็บ : `Dockerfile` · `site/index.html` (รุ่น 1) · `site_v2/index.html` (รุ่น 2) · `verify.sh` · `images/`

### 🎯 แล็บนี้ใน 30 วินาที

| | |
|---|---|
| **คำถามเดียวที่ตอบให้จบ** | ถ้ามีคน `push` ทับ tag `1.0` ด้วย image คนละตัว — พรุ่งนี้เรา `pull` แล้วได้อะไร |
| **ต้องผ่านอะไรมาก่อน** | **LAB 1** (build/run) · **LAB 4** (`--build-arg`) |
| **เวลา** | ~35 นาที · การทดลอง **10 อัน** อันละ 2–4 นาที |
| **จบแล้วต้องทำได้เอง** | แกะชื่อ image ครบทุกส่วน · เดินวงจร build → tag → push → pull → run · เลือกใช้ tag หรือ digest ได้อย่างมีเหตุผล |
| **หมายเหตุ** | ใช้ **local registry** ทั้งแล็บ ไม่ต้องมีบัญชี Docker Hub · หัวข้อ Docker Hub ท้ายแล็บเป็น **เอกสารอ่านอย่างเดียว** |

---

## ทฤษฎีก่อนลงมือ

### ชื่อ image คือ "ที่อยู่จัดส่ง"

```
[REGISTRY/][NAMESPACE/]REPOSITORY[:TAG][@DIGEST]
```

![แผนภาพแยกชื่อ image เป็น registry namespace repository และ tag พร้อมตัวอย่างชื่อที่ push สำเร็จและล้มเหลว](./images/theory-image-naming.svg)

> 🖼 **วิธีอ่านรูปนี้:** ไล่จากซ้ายไปขวาตามสี — ปลายทาง / พื้นที่เจ้าของ / ชิ้นงาน / รุ่น · **กรอบแดง** คือชื่อที่ขาด namespace จนถูกส่งไป `library` ที่เราไม่มีสิทธิ์

| ส่วน | ตัวอย่างในแล็บนี้ | ถ้าไม่เขียน |
|---|---|---|
| **Registry** | `localhost:5000` | Docker เติม `docker.io` (Docker Hub) ให้ |
| **Namespace** | `workshop` | บน Docker Hub กลายเป็น `library` ซึ่งเรา push ไม่ได้ |
| **Repository** | `regdemo` | — (ต้องมีเสมอ) |
| **Tag** | `1.0` | Docker เติม `:latest` ให้ (ซึ่งก็เป็นแค่ tag ธรรมดา) |
| **Digest** | `@sha256:c346…` | — (ระบุเมื่อต้องการความแน่นอน) |

### tag ย้ายได้ · digest ย้ายไม่ได้

![แผนภาพเปรียบเทียบ tag ที่ย้ายจาก digest รุ่นแรกไปยังรุ่นสองกับ digest เดิมที่ยังดึง image เก่าได้](./images/theory-tag-vs-digest.svg)

> 🖼 **วิธีอ่านรูปนี้:** ตามลำดับ ①–③ — tag `1.0` ย้ายจากก้อนหนึ่งไปอีกก้อน แต่ **ก้อนเดิมยังอยู่** เข้าถึงได้ทาง digest เท่านั้น

| อ้างด้วย | พรุ่งนี้ได้ของเดิมไหม | เหมาะกับ |
|---|---|---|
| **Tag** `repo:1.0` | **ไม่รับประกัน** — เจ้าของ repo push ทับเมื่อไหร่ก็ได้ | งานพัฒนา อ่านง่าย |
| **Digest** `repo@sha256:…` | **ได้เหมือนเดิมเสมอ** เพราะคำนวณจากเนื้อหา | production / CI ที่ต้อง reproducible |

### สิ่งที่มักเข้าใจผิด

- **คิดว่า** `docker tag` สำเนา image อีกชุด → **จริง ๆ** แค่เพิ่มป้ายชี้ไปยังก้อนเดิม (การทดลองที่ 4)
- **คิดว่า** push/pull ส่ง image ทั้งก้อนทุกครั้ง → **จริง ๆ** ถ่ายโอนเฉพาะ layer ที่อีกฝั่งยังไม่มี
- **คิดว่า** `latest` แปลว่าใหม่ที่สุด → **จริง ๆ** เป็นแค่ tag ธรรมดาที่ใครก็ย้ายได้

---

## เตรียมเครื่องเรียน

### ขั้นที่ 1 — เปิดกล่องเรียน

รันบน **เครื่องของเราเอง** — แล็บนี้ใช้ **3 พอร์ต** :

```bash
docker rm -f devtools-df-lab5 2>/dev/null
docker run -dit --name devtools-df-lab5 --privileged \
  -p 2235:22 -p 5035:5000 -p 8185:8185 tuchsanai/devtools:2569_1
ssh root@localhost -p 2235        # password : passwd
```

> 📝 **`-p 5035:5000`** = พอร์ต 5035 ของเครื่องเรา → พอร์ต **5000 ของกล่องเรียน** ซึ่งจะเป็นที่อยู่ของ registry · **ในกล่องเรียนเราเรียก registry ที่ `localhost:5000` เสมอ ไม่ใช่ 5035**

### ขั้นที่ 2 — โหลดโค้ดแล็บ

**คำสั่งทุกอันหลังจากนี้พิมพ์ข้างในกล่องเรียน**

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide/005_LAB_Registry_Tag_Push_Pull
cat Dockerfile
```

✅ **สิ่งที่ต้องเห็น** — Dockerfile สั้นมาก แต่ build ได้ **สองรุ่น** ด้วย `ARG` :

```dockerfile
FROM nginx:1.27-alpine
ARG SITE_DIR=site
ARG RELEASE=1.0
LABEL org.opencontainers.image.title="regdemo"
LABEL release="${RELEASE}"
COPY ${SITE_DIR}/ /usr/share/nginx/html/
EXPOSE 80
```

> 📝 `ARG SITE_DIR=site` ทำให้ `COPY ${SITE_DIR}/ ...` เลือกได้ว่าจะเอาเว็บชุดไหนเข้า image (ทบทวน `ARG` จาก **LAB 4**)

---

## การทดลองที่ 1 — แกะชื่อ image ของจริง

**คำถาม:** ชื่อสั้น ๆ อย่าง `registry:2` เต็ม ๆ แล้วคืออะไร

```bash
docker pull registry:2
docker image inspect --format "TAGS   = {{.RepoTags}}"    registry:2
docker image inspect --format "DIGEST = {{.RepoDigests}}" registry:2
```

✅ **สิ่งที่ต้องเห็น** — สองแบบของชื่อ : แบบ `repo:tag` และแบบ `repo@sha256:...` :

```
TAGS   = [registry:2]
DIGEST = [registry@sha256:a3d8aaa63ed8681a604f1dea0aa03f100d5895b6a58ace528858a7b332415373]
```

> 📝 `registry:2` เขียนสั้นแบบไม่มี registry และไม่มี namespace ได้ เพราะเป็น **official image** ที่อยู่ใต้ `docker.io/library/` · `RepoDigests` จะมีค่าก็ต่อเมื่อ image นั้นเคย pull มาจาก registry หรือเคย push ขึ้นไปแล้ว

---

## การทดลองที่ 2 — เปิด registry ของตัวเอง

**คำถาม:** registry คืออะไรกันแน่

```bash
docker run -d --name lab-registry -p 5000:5000 registry:2
sleep 2
curl -s http://localhost:5000/v2/_catalog
```

✅ **สิ่งที่ต้องเห็น** — registry ขึ้นแล้วและ **ว่างเปล่า** :

```
{"repositories":[]}
```

> 📝 `registry:2` คือ **Distribution Registry** ตัวจริงที่ Docker Hub ก็ใช้เครื่องยนต์เดียวกัน · `/v2/` คือ **Registry HTTP API** มาตรฐานเดียวกันทุก registry — จะเห็นชัดในการทดลองที่ 6 ว่า registry เป็นแค่ HTTP server ธรรมดา

---

## การทดลองที่ 3 — build image รุ่นแรก

**คำถาม:** ชื่อที่ไม่มี registry นำหน้า Docker ตีความว่าอะไร

```bash
docker build -t regdemo:1.0 .
docker images regdemo
```

✅ **สิ่งที่ต้องเห็น** — Docker **เติม `docker.io/library/` ให้เองอัตโนมัติ** :

```
#7 naming to docker.io/library/regdemo:1.0 done

IMAGE         ID             DISK USAGE   CONTENT SIZE
regdemo:1.0   c3463cc89ec7       73.6MB           21MB
```

> 📝 นี่คือสาเหตุที่ `docker push regdemo:1.0` เฉย ๆ จะวิ่งไป Docker Hub แล้วโดนปฏิเสธ — ต้องตั้งชื่อให้ตรง registry ปลายทางก่อน (การทดลองถัดไป)

---

## การทดลองที่ 4 — `docker tag` สำเนา image ไหม

**คำถาม:** ติดชื่อที่สองแล้ว image ในเครื่องเพิ่มเป็น 2 ก้อนหรือเปล่า

```bash
docker tag regdemo:1.0 localhost:5000/workshop/regdemo:1.0
docker images | grep regdemo
docker image inspect --format "{{.Id}}" regdemo:1.0 localhost:5000/workshop/regdemo:1.0
```

✅ **สิ่งที่ต้องเห็น** — **หลักฐานชิ้นเอก** : สองแถว ชื่อคนละชื่อ แต่ **ID เดียวกัน** :

```
localhost:5000/workshop/regdemo:1.0   c3463cc89ec7       73.6MB           21MB
regdemo:1.0                           c3463cc89ec7       73.6MB           21MB

sha256:c3463cc89ec7fa6626be6773a8ac24bdc863ee53f15ac00ff39188ea079b5c7d
sha256:c3463cc89ec7fa6626be6773a8ac24bdc863ee53f15ac00ff39188ea079b5c7d
```

> 📝 **image = ก้อนข้อมูล · tag = ป้ายชื่อที่ชี้มาที่ก้อนนั้น** — ป้ายกี่ใบก็ได้ ไม่กินพื้นที่เพิ่ม · ชื่อใหม่มีครบสูตร : registry `localhost:5000` / namespace `workshop` / repository `regdemo` / tag `1.0`

---

## การทดลองที่ 5 — push ขึ้น registry

**คำถาม:** Docker รู้ได้อย่างไรว่าจะส่งไปที่ไหน

```bash
docker push localhost:5000/workshop/regdemo:1.0
```

✅ **สิ่งที่ต้องเห็น** — ทุก layer ขึ้น `Pushed` และปิดท้ายด้วย **digest** (เรียกค่านี้ว่า **D1**) :

```
The push refers to repository [localhost:5000/workshop/regdemo]
202431b9ce11: Pushed
d7e507024086: Pushed
1.0: digest: sha256:c3463cc89ec7fa6626be6773a8ac24bdc863ee53f15ac00ff39188ea079b5c7d size: 856
```

เก็บ digest ไว้ในตัวแปร จะได้ไม่ต้องคัดลอกด้วยมือ :

```bash
D1=$(docker image inspect --format '{{range .RepoDigests}}{{println .}}{{end}}' \
       localhost:5000/workshop/regdemo:1.0 | grep '^localhost:5000/')
echo "$D1"
```

✅ **สิ่งที่ต้องเห็น** — สตริงเต็มรูปแบบที่เอาไปต่อท้าย `docker pull` ได้เลย :

```
localhost:5000/workshop/regdemo@sha256:c3463cc89ec7fa6626be6773a8ac24bdc863ee53f15ac00ff39188ea079b5c7d
```

> ⚠️ **ทำไมต้อง `grep`:** image ก้อนนี้มี **หลายชื่อ** (`regdemo:1.0` และ `localhost:5000/...`) ดังนั้น `.RepoDigests` จึงเป็น **list** ที่ลำดับไม่แน่นอน — ถ้าใช้ `{{index .RepoDigests 0}}` เฉย ๆ อาจได้ `regdemo@sha256:...` ที่ไม่มี registry นำหน้า แล้ว `docker pull` จะวิ่งไป Docker Hub

> 📝 **Docker อ่านจาก "ชื่อ" เท่านั้น** ว่าจะส่งไปที่ไหน · มันส่ง manifest (สารบัญของ image) + **เฉพาะ layer ที่ registry ยังไม่มี** · ค่า digest ของแต่ละคนจะไม่ตรงกับเอกสารนี้ เพราะคำนวณจากเนื้อหา image ที่ build ในเครื่องตัวเอง

---

## การทดลองที่ 6 — คุยกับ registry ตรง ๆ ด้วย HTTP

**คำถาม:** registry เก็บอะไรไว้บ้าง

```bash
curl -s http://localhost:5000/v2/_catalog
curl -s http://localhost:5000/v2/workshop/regdemo/tags/list
```

✅ **สิ่งที่ต้องเห็น** — คราวนี้ไม่ว่างแล้ว :

```
{"repositories":["workshop/regdemo"]}
{"name":"workshop/regdemo","tags":["1.0"]}
```

ถามต่อว่า tag `1.0` ชี้ไป digest ไหน :

```bash
curl -sI -H "Accept: application/vnd.oci.image.index.v1+json" \
  http://localhost:5000/v2/workshop/regdemo/manifests/1.0 | grep -i "docker-content-digest"
```

✅ **สิ่งที่ต้องเห็น** — **ตรงกับ D1 เป๊ะ** :

```
Docker-Content-Digest: sha256:c3463cc89ec7fa6626be6773a8ac24bdc863ee53f15ac00ff39188ea079b5c7d
```

เปิดในเบราว์เซอร์บนเครื่องเราที่ **`http://localhost:5035/v2/_catalog`** ก็เห็นข้อมูลชุดเดียวกัน :

![catalog ของ local registry เปิดผ่านเบราว์เซอร์](./images/registry-catalog.png)

> 📝 ต้องส่ง header `Accept: ...` บอกชนิด manifest ที่เรารับได้ ไม่งั้น registry จะตอบ `404` · `-I` = ขอเฉพาะ HTTP header

---

## การทดลองที่ 7 — ลบชื่อในเครื่องแล้ว pull กลับมา

**คำถาม:** ของอยู่บน registry จริงหรือแค่อยู่ในเครื่องเรา

```bash
docker image rm regdemo:1.0 localhost:5000/workshop/regdemo:1.0
docker images | grep regdemo || echo "(ไม่เหลือ regdemo ในเครื่องแล้ว)"
```

✅ **สิ่งที่ต้องเห็น** — `Untagged:` **สองบรรทัด** แล้วจึง `Deleted:` **หนึ่งบรรทัด** :

```
Untagged: regdemo:1.0
Untagged: localhost:5000/workshop/regdemo:1.0
Deleted: sha256:c3463cc89ec7fa6626be6773a8ac24bdc863ee53f15ac00ff39188ea079b5c7d

(ไม่เหลือ regdemo ในเครื่องแล้ว)
```

ดึงกลับมาแล้วรันจริง :

```bash
docker pull localhost:5000/workshop/regdemo:1.0
docker run -d --name regdemo-web -p 8185:80 localhost:5000/workshop/regdemo:1.0
sleep 2
curl -s http://localhost:8185/ | grep -E "RELEASE 1.0|BUILD 1"
```

✅ **สิ่งที่ต้องเห็น** — `Downloaded newer image` = ดึงมาจาก registry จริง และหน้าเว็บเป็นรุ่น 1 :

```
Digest: sha256:c3463cc89ec7fa6626be6773a8ac24bdc863ee53f15ac00ff39188ea079b5c7d
Status: Downloaded newer image for localhost:5000/workshop/regdemo:1.0

      <h1 id="release-title">RELEASE 1.0</h1>
      <span class="badge">BUILD 1</span>
```

เปิดเบราว์เซอร์บนเครื่องเราที่ **`http://localhost:8185`** :

![RELEASE 1.0 — image ที่ pull กลับมาจาก local registry](./images/site-release1.png)

> 📝 **ปิดวงจรครบแล้ว** : build → tag → push → ลบทิ้ง → pull → run · ข้อสำคัญคือ registry **ไม่ได้รัน container ให้เรา** มันแค่ "เก็บและส่งต่อ" ไฟล์ image เท่านั้น

---

## การทดลองที่ 8 — push ทับ tag เดิมด้วย image คนละตัว

**คำถาม:** registry จะปฏิเสธ, สร้าง tag ใหม่, หรือย้าย tag เดิมไปชี้ของใหม่

```bash
docker build --build-arg SITE_DIR=site_v2 --build-arg RELEASE=2.0 -t regdemo:2.0 .
docker tag regdemo:2.0 localhost:5000/workshop/regdemo:1.0
docker push localhost:5000/workshop/regdemo:1.0
```

✅ **สิ่งที่ต้องเห็น** — layer ฐานขึ้น `Layer already exists` มีแค่ layer ของเว็บใหม่ที่ `Pushed` และได้ **digest ตัวใหม่ (D2)** :

```
f18232174bc9: Layer already exists
61ca4f733c80: Layer already exists
e68542110cc8: Pushed
1.0: digest: sha256:3930fe45a8a74857131ff3aa18a7f9ab6bcb15ca3e5dc19ef8bbcd77d64515c8 size: 856
```

ถาม registry ว่า tag `1.0` ตอนนี้ชี้ไปไหน :

```bash
curl -sI -H "Accept: application/vnd.oci.image.index.v1+json" \
  http://localhost:5000/v2/workshop/regdemo/manifests/1.0 | grep -i "docker-content-digest"
curl -s http://localhost:5000/v2/workshop/regdemo/tags/list
```

✅ **สิ่งที่ต้องเห็น** — digest เปลี่ยนจาก D1 (`c346…`) เป็น D2 (`3930…`) ทั้งที่ชื่อ tag เท่าเดิม :

```
Docker-Content-Digest: sha256:3930fe45a8a74857131ff3aa18a7f9ab6bcb15ca3e5dc19ef8bbcd77d64515c8
{"name":"workshop/regdemo","tags":["1.0"]}
```

ลอง pull ด้วย **tag เดิมเป๊ะ** ดูว่าได้อะไร :

```bash
docker rm -f regdemo-web
docker image rm -f localhost:5000/workshop/regdemo:1.0 regdemo:2.0
docker pull localhost:5000/workshop/regdemo:1.0
docker run -d --name regdemo-web -p 8185:80 localhost:5000/workshop/regdemo:1.0
sleep 2
curl -s http://localhost:8185/ | grep -E "RELEASE 2.0|BUILD 2"
```

✅ **สิ่งที่ต้องเห็น** — **คำสั่ง `docker pull` เหมือนเดิมทุกตัวอักษร แต่ได้คนละหน้า** :

```
      <h1 id="release-title">RELEASE 2.0</h1>
      <span class="badge">BUILD 2</span>
```

![RELEASE 2.0 — tag 1.0 เดิมถูก push ทับให้ชี้ image ใหม่](./images/site-release2.png)

> 📝 **เฉลย:** registry **ย้าย tag เดิมไปชี้ image ใหม่โดยไม่ถามอะไรเลย** และ image เก่ายังอยู่ครบ เพียงแต่ไม่มี tag ชี้ถึงแล้ว — เข้าถึงได้ทางเดียวคือผ่าน digest

---

## การทดลองที่ 9 — pull ด้วย digest ได้ของเดิมเสมอ

**คำถาม:** image รุ่น 1 หายไปจาก registry แล้วหรือยัง ในเมื่อไม่มี tag ชี้ถึง

```bash
docker pull "$D1"
docker run -d --name regdemo-old -p 8085:80 "$D1"
sleep 2
curl -s http://localhost:8085/ | grep RELEASE
curl -s http://localhost:8185/ | grep RELEASE
```

✅ **สิ่งที่ต้องเห็น** — **หลักฐานชี้ขาดของแล็บนี้** : repository เดียวกัน registry เดียวกัน แต่ digest ต่างกัน → ได้คนละ image :

```
      <h1 id="release-title">RELEASE 1.0</h1>      ← พอร์ต 8085 : อ้างด้วย digest เก่า
      <h1 id="release-title">RELEASE 2.0</h1>      ← พอร์ต 8185 : อ้างด้วย tag 1.0
```

> 📝 `$D1` คือตัวแปรที่เก็บไว้ตั้งแต่การทดลองที่ 5 · พอร์ต 8085 ไม่ได้ publish ออกนอกกล่องเรียน จึงดูได้ด้วย `curl` จากใน SSH เท่านั้น
>
> **ทำไม `latest` ไม่ได้แปลว่าใหม่ที่สุด:** มันเป็นเพียง tag ธรรมดาตัวหนึ่ง ใครที่มีสิทธิ์ push ก็ชี้ `latest` ไปที่ image เก่าเมื่อปีที่แล้วได้ทันที และ Docker จะไม่เตือนอะไรเลย · เวลา deploy จึงควรใช้ **version tag** เป็นอย่างน้อย และเมื่อต้องการความแน่นอนสูงสุดให้ **pin ด้วย digest**

---

## การทดลองที่ 10 — `Untagged` ต่างจาก `Deleted` อย่างไร

**คำถาม:** `docker rmi` ลบอะไรกันแน่

```bash
docker tag localhost:5000/workshop/regdemo:1.0 regdemo:2.0
docker rmi regdemo:2.0
```

✅ **สิ่งที่ต้องเห็น** — มีแต่ `Untagged:` **ไม่มี `Deleted:`** เพราะยังมีชื่ออื่นชี้ก้อนนี้อยู่ :

```
Untagged: regdemo:2.0
```

ทีนี้ลบ **ชื่อสุดท้าย** ของ image รุ่น 1 :

```bash
docker rm -f regdemo-old
docker rmi "$D1"
```

✅ **สิ่งที่ต้องเห็น** — คราวนี้ได้ **ทั้ง `Untagged:` และ `Deleted:`** :

```
Untagged: localhost:5000/workshop/regdemo@sha256:c3463cc89ec7...
Deleted: sha256:c3463cc89ec7fa6626be6773a8ac24bdc863ee53f15ac00ff39188ea079b5c7d
```

> 📝 **กติกา:** `docker rmi` **ลบ "ชื่อ" ก่อนเสมอ** และจะลบ "ก้อน" ก็ต่อเมื่อชื่อสุดท้ายหายไปและไม่มี container ใดใช้อยู่ · **image ตัวนี้ยังอยู่บน registry นะ** — ที่เราลบคือสำเนาในเครื่องเรียนเท่านั้น สั่ง `docker pull` ด้วย digest เดิมก็ได้กลับมาอีก

---

## เอกสารอ่านอย่างเดียว — Docker Hub

> ⚠️ **ไม่ต้องทำในคาบ** — แล็บใช้ local registry เพื่อไม่ต้องผูกบัญชีจริงของใคร · ทุกที่ที่เห็น `<DOCKER_USER>` และ `<DOCKER_TOKEN>` ให้แทนด้วยค่าของตัวเองตอนใช้งานจริง **ห้ามพิมพ์ค่าจริงลงเอกสาร Git หรือ chat**

![แผนภาพวงจร build และ tag image ให้มี namespace ก่อน push ขึ้น Docker Hub แล้วลบ local เพื่อ pull กลับมารัน](./images/theory-registry-flow.svg)

> 🖼 **วิธีอ่านรูปนี้:** ตามหมายเลข ①–⑥ : build → ติดชื่อให้มี namespace → push → `rmi` ลบของในเครื่อง → pull กลับมา → run ได้เหมือนเดิม

**สร้าง Personal Access Token 7 ขั้น** — ตั้ง **Expiration date** ตามอายุงาน และเลือกสิทธิ์ตามหลัก **least privilege** (แค่ pull ให้เลือก Read-only · ต้อง push ค่อยใช้ Read & Write)

| ขั้น | ทำอะไร | ภาพ |
|---|---|---|
| 1 | เข้า `hub.docker.com` **ตรวจ domain ก่อนเสมอ** แล้วกด Sign in | ![ขั้นตอน 1](./images/dockerhub-step1.png) |
| 2 | ยืนยันตัวตนผ่านหน้าเว็บ (ยังไม่ใช่ `docker login`) | ![ขั้นตอน 2](./images/dockerhub-step2.png) |
| 3 | เข้า My Hub → Repositories แล้วคลิก avatar | ![ขั้นตอน 3](./images/dockerhub-step3.png) |
| 4 | เลือก **Account settings** | ![ขั้นตอน 4](./images/dockerhub-step4.png) |
| 5 | เปิด **Personal access tokens** → Generate new token | ![ขั้นตอน 5](./images/dockerhub-step5.png) |
| 6 | ตั้ง description / expiration / สิทธิ์ | ![ขั้นตอน 6](./images/dockerhub-step6.png) |
| 7 | **คัดลอก token (แสดงครั้งเดียวเท่านั้น)** เก็บใน password manager ทันที | ![ขั้นตอน 7](./images/dockerhub-step7.png) |

วงจรทำงานจริง :

```bash
# 1) login — เมื่อขึ้น Password: ให้ "วาง" token ค่าจะไม่แสดงบนหน้าจอ
docker login --username '<DOCKER_USER>'

# 2) ตั้งชื่อ image ให้ namespace ตรงกับบัญชีที่ login
docker tag localhost:5000/workshop/regdemo:1.0 <DOCKER_USER>/regdemo:1.0

# 3) push แล้วดู digest ที่ตอบกลับ
docker push <DOCKER_USER>/regdemo:1.0

# 4) เครื่องที่ใช้ร่วมกับคนอื่น ให้ logout ทุกครั้ง
docker logout
```

> 📝 **ห้ามพิมพ์ token ต่อท้ายคำสั่งเด็ดขาด** (เช่น `docker login -u ... -p <token>`) เพราะจะถูกบันทึกลง `~/.bash_history` · ถ้าจำเป็นต้องอัตโนมัติให้ใช้ `--password-stdin`

---

## ตรวจงานด้วย `verify.sh`

```bash
cd ~/labwork/DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide/005_LAB_Registry_Tag_Push_Pull
bash verify.sh ; echo "exit code = $?"
```

✅ **สิ่งที่ต้องเห็น** — `[PASS]` ครบทุกข้อ ปิดท้าย `ALL CHECKS PASSED` :

```
[PASS] คอนเทนเนอร์ lab-registry กำลังทำงาน
[PASS] registry catalog มี repository workshop/regdemo
[PASS] repository workshop/regdemo มี tag 1.0
[PASS] รัน image ชั่วคราวแล้วหน้าเว็บมีคำว่า RELEASE
[PASS] docker tag เพิ่มชื่อใหม่โดยไม่สำเนา image (IMAGE ID ตรงกัน)
ALL CHECKS PASSED
exit code = 0
```

> 📝 สคริปต์สร้าง container ชั่วคราวชื่อ `regdemo-verify` และ tag ชั่วคราว `regdemo:verify-tmp` แล้ว **เก็บกวาดของตัวเองทั้งหมด** ไม่แตะ image หรือ registry ของเรา

---

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `push access denied ... insufficient_scope` | ชื่อ image ไม่มี registry นำหน้า Docker จึงส่งไป `docker.io/library/` ที่เราไม่มีสิทธิ์ | `docker tag <ชื่อเดิม> localhost:5000/workshop/<repo>:<tag>` แล้ว push ชื่อใหม่ |
| `http: server gave HTTP response to HTTPS client` | Docker ต่อ registry ด้วย HTTPS เสมอ ยกเว้น `localhost` / `127.0.0.0/8` | ในแล็บให้อ้าง registry ด้วย `localhost:5000` เท่านั้น (อย่าใช้ IP ของเครื่อง) |
| `curl: (7) Failed to connect to localhost port 5000` | `lab-registry` ไม่ได้รันอยู่ หรือรันแล้ว exit | `docker ps -a --filter name=lab-registry` · `docker logs lab-registry` |
| `manifest unknown` ตอนขอ manifest ด้วย curl | สะกด repository/tag ผิด หรือลืม header `Accept` | ตรวจชื่อจาก `/v2/_catalog` ก่อน · ใส่ `-H "Accept: application/vnd.oci.image.index.v1+json"` |
| `Bind for 0.0.0.0:8185 failed: port is already allocated` | container เดิมยังจองพอร์ตอยู่ | `docker rm -f regdemo-web` ก่อน แล้วรันใหม่ |
| `image is being used by running container` ตอน `docker rmi` | ยังมี container ที่สร้างจาก image นั้น | `docker ps -a --filter ancestor=<image>` หา แล้ว `docker rm -f` |
| สั่ง `docker rmi` แล้วขึ้นแค่ `Untagged:` พื้นที่ไม่ลด | ก้อนนั้นยังมีชื่ออื่นชี้อยู่ | `docker images \| grep <ID>` ดูว่าเหลือกี่ชื่อ แล้วลบให้ครบ |
| pull แล้วได้หน้าเว็บคนละรุ่นกับที่คิด | tag ถูก push ทับให้ชี้ image ใหม่ (การทดลองที่ 8) | ตรวจ `Docker-Content-Digest` ก่อน · ต้องการรุ่นเดิมเป๊ะให้ pull ด้วย `@sha256:...` |
| เบราว์เซอร์เปิด `localhost:5000` ไม่ขึ้น | `5000` เป็นพอร์ตของ **กล่องเรียน** เครื่องเราต้องเข้าทาง `5035` | ใช้ `http://localhost:5035/v2/_catalog` บนเบราว์เซอร์ |

---

## เก็บกวาด

**ในกล่องเรียน:**

```bash
docker rm -f regdemo-web regdemo-old 2>/dev/null
docker rm -f lab-registry
docker ps -a
```

> 📝 **ข้อมูลใน registry เก็บอยู่ในตัว container** (ไม่ได้ผูก volume) ดังนั้นลบ `lab-registry` = image ที่ push ไว้หายไปด้วย ซึ่งตั้งใจให้เป็นแบบนั้นสำหรับห้องเรียน

**ออกจากกล่องแล้วลบกล่องบนเครื่องเรา:**

```bash
exit
docker rm -f devtools-df-lab5
docker ps -a --filter "name=^devtools-"
```

---

## สรุปคำสั่งของแล็บนี้

| คำสั่ง | ความหมาย |
|---|---|
| `docker run -d --name lab-registry -p 5000:5000 registry:2` | เปิด local registry ที่พอร์ต 5000 ของกล่องเรียน |
| `docker tag <เดิม> localhost:5000/workshop/regdemo:1.0` | **เพิ่มชื่อ** ให้ image เดิมให้ตรงกับ registry ปลายทาง (ไม่สำเนา layers) |
| `docker push localhost:5000/workshop/regdemo:1.0` | ส่ง manifest + เฉพาะ layer ที่ registry ยังไม่มี แล้วตอบ digest กลับมา |
| `docker pull <repo>:<tag>` | ดึงตาม **tag** — ได้ของที่ tag ชี้อยู่ ณ ขณะนั้น |
| `docker pull <repo>@sha256:<digest>` | ดึงตาม **digest** — ได้ของเดิมเสมอ |
| `docker image inspect --format "{{.Id}}" <ชื่อ>` | อ่าน IMAGE ID เพื่อพิสูจน์ว่าสองชื่อชี้ก้อนเดียวกัน |
| `docker image inspect --format '{{index .RepoDigests 0}}' <ชื่อ>` | เอาชื่อแบบ `repo@sha256:...` มาเก็บไว้ในตัวแปร |
| `curl -s http://localhost:5000/v2/_catalog` | ถาม registry ว่ามี repository อะไรบ้าง |
| `curl -sI -H "Accept: ..." .../manifests/<tag>` | ดูหัว `Docker-Content-Digest` ว่า tag นี้ชี้ digest ไหน |
| `docker rmi <ชื่อ>` | ลบ **ชื่อ** ก่อน — `Untagged:` ถ้ายังมีชื่ออื่น, `Deleted:` เมื่อลบชื่อสุดท้าย |
| `docker login --username '<DOCKER_USER>'` / `docker logout` | เข้า/ออกจากบัญชี registry ภายนอก (วาง token ที่ prompt เท่านั้น) |

> จำสั้น ๆ : **image = ก้อนข้อมูล (ID/digest)** · **tag = ป้ายชื่อที่ย้ายได้** · **registry = ที่ฝากส่ง ไม่ใช่ที่รัน** · อยากได้ของเดิมเป๊ะเมื่อไหร่ → **pin ด้วย digest**

## ✅ เช็กลิสต์ก่อนจบแล็บ

- [ ] อธิบายชื่อ `localhost:5000/workshop/regdemo:1.0` ได้ครบว่าส่วนไหนคือ registry / namespace / repository / tag
- [ ] `lab-registry` รันอยู่ และ `curl .../v2/_catalog` ครั้งแรกตอบ `{"repositories":[]}`
- [ ] หลัง `docker tag` เห็น **2 แถวชื่อต่างกันแต่ IMAGE ID เดียวกัน**
- [ ] `docker push` จบด้วย `1.0: digest: sha256:...` และหัว `Docker-Content-Digest` ตรงกับค่านั้น
- [ ] ลบชื่อ local จนหมดแล้ว `docker pull` กลับมา `docker run` ได้ และ `http://localhost:8185` แสดง **RELEASE 1.0**
- [ ] push รุ่น 2 ทับ tag `1.0` แล้วเห็น `Layer already exists` กับ digest ตัวใหม่ที่ต่างจากเดิม
- [ ] pull ด้วย tag `1.0` ได้ **RELEASE 2.0** แต่ pull ด้วย `$D1` ยังได้ **RELEASE 1.0**
- [ ] `docker rmi` ชื่อแรกได้แค่ `Untagged:` · ลบชื่อสุดท้ายจึงได้ `Deleted:`
- [ ] อธิบายได้ว่าทำไม `latest` ไม่ได้แปลว่าใหม่ที่สุด
- [ ] `bash verify.sh` ขึ้น `ALL CHECKS PASSED` และเก็บกวาดจนไม่เหลือ container ของแล็บ

*ผลลัพธ์ทั้งหมดในเอกสารนี้มาจากการรันจริงในเครื่องเรียน `tuchsanai/devtools:2569_1`*
