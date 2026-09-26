# LAB 3 — Jenkins สั่ง devtools ผ่าน SSH: Clone → Build → Test → Push → Pull → Deploy ร้านอาหารแมว

> ⏱️ ประมาณ 60–75 นาที · 🧪 10 การทดลอง · 🎯 จบเมื่อกด **Build** ใน Jenkins แล้วเปิด `http://localhost:3000` เห็นร้าน **Meow Mart** ที่ Pipeline เพิ่ง clone, build, push, pull และ deploy และผ่านรายการ **✅ ตรวจปิดแล็บ** ครบทุกข้อ

แล็บนี้ตอบคำถามว่า **“Jenkins ที่ไม่มี Docker อยู่ข้างในเลย จะสั่งให้เกิด build → test → push → deploy ได้อย่างไร”** คำตอบคือ Jenkins ทำหน้าที่ **ผู้สั่ง** ส่วน `devtools` ทำหน้าที่ **ผู้ทำ** Jenkins เปิด SSH กลับไปที่ port 22 ของ `devtools` แล้วส่งสคริปต์ไปรันทีละ stage ตั้งแต่ `git clone` ซอร์สร้านจาก GitHub ไปจนถึงเปิดร้านเป็น container พี่น้อง (sibling) บน Docker ของ `devtools` ที่ port 3000

> **กติกาของแล็บ:** นักศึกษาไม่พิมพ์ `docker build`, `docker push` หรือ `git clone` ของร้านเอง ทุกอย่างเริ่มจากปุ่มบน Jenkins และ container `jenkins` ยังเป็น image มาตรฐานตัวเดิมจาก LAB 1 — **ไม่ติดตั้ง Docker CLI, ไม่ mount `docker.sock`, ไม่สร้าง Jenkins ใหม่**

<!-- ภาพแนวคิดสถาปัตยกรรม (Docker สองชั้น + เส้นทาง SSH ผ่าน gateway ของ cicd-net) รอสร้างด้วย cyolo imagegen โดยผู้ประสานงาน -->

![หน้าแรกของร้าน Meow Mart](./images/lab3_f1_web_hero_b1.jpg)

*ภาพที่ 1 หน้าร้านที่ Pipeline deploy — **ภาพจากรอบทดสอบของ LAB 3 ฉบับก่อน (25 ก.ย. 2569)** ตัวแอปไม่ได้เปลี่ยน จึงหน้าตาเหมือนเดิม แต่ในฉบับนี้ chip และ Deployment info จะแสดงค่าของ build ของนักศึกษาเอง และช่อง Git commit จะมีค่าจริงแทน `none`*

---

## 📚 ทฤษฎีก่อนลงมือ

### 1. Docker สองชั้น: ใครอยู่บน daemon ตัวไหน

`devtools` เป็น container บนเครื่องของเรา แต่ข้างในมี **Docker daemon ของตัวเอง** (Docker-in-Docker ด้วย `--privileged`) ตั้งแต่ LAB 1 container `jenkins` จึงอยู่ **ข้างใน** `devtools` ไม่ได้อยู่ข้าง ๆ

| ชั้น | Docker daemon | สิ่งที่อยู่บนชั้นนี้ | port ที่เปิดออก |
|---|---|---|---|
| เครื่องของเรา | Docker ของเครื่องเรา (เช่น Docker Desktop) | container `devtools` | `2222→22`, `8080→8080`, `3000→3000`, `8000→8000` |
| ข้างใน `devtools` | Docker ของ `devtools` | `jenkins` (network `cicd-net`), `catfood-test-N` (ชั่วคราว), `catfood-web` (ร้าน) | `8080→8080` ของ `jenkins`, `3000→3000` ของ `catfood-web` |

ดังนั้น `localhost:3000` บนเบราว์เซอร์ → `-p 3000:3000` ของ `devtools` → `-p 3000:3000` ของ `catfood-web` ซึ่ง stage Deploy สร้างบน Docker ของ `devtools` เส้นทางเดียวกับ Jenkins ที่ `8080` ใน LAB 1

### 2. ทำไม `jenkins` เรียกชื่อ `devtools` ไม่ได้ และจะไปหา devtools ทางไหน

ชื่อ `devtools` เป็นชื่อ container บน **Docker ของเครื่องเรา** (ชั้นนอก) แต่ `jenkins` ถาม DNS จาก **embedded DNS ของ Docker ข้างใน `devtools`** (`nameserver 127.0.0.11`) ซึ่งรู้จักเฉพาะ container ที่อยู่ใน network เดียวกันบน daemon ตัวเอง คือ `jenkins` เท่านั้น ส่วน hostname ของ `devtools` เองก็เป็น container ID ไม่ใช่คำว่า `devtools` ชื่อนี้จึง **ไม่ถูก resolve ให้โดยอัตโนมัติ** (พิสูจน์ในการทดลองที่ 2)

แต่มีเส้นทางที่แน่นอนอยู่แล้ว: เมื่อ Docker ข้างใน `devtools` สร้าง network `cicd-net` มันสร้าง bridge interface ขึ้นใน `devtools` และตั้ง **gateway ของ `cicd-net` เป็น IP ของ `devtools` เอง** บน bridge นั้น packet จาก `jenkins` ไปที่ gateway จึงถึง `devtools` โดยตรง และ `sshd` ของ `devtools` ฟังอยู่ที่ port 22 ทุก interface

| คำถาม | คำตอบ |
|---|---|
| Jenkins ต่อไปที่ใคร | gateway ของ `cicd-net` = `devtools` port 22 |
| ทำไมไม่เขียน IP ตายตัว | subnet ของ `cicd-net` ถูกเลือกตอน `docker network create` ตาม subnet ที่ว่างบนเครื่องนั้น แต่ละเครื่องอาจได้ไม่เหมือนกัน จึงต้อง **อ่านค่าจริงด้วย `docker network inspect`** |
| เก็บค่าไว้ที่ไหน | SSH Host alias ชื่อ `devtools-gw` ใน `/var/jenkins_home/.ssh/config` ซึ่งอยู่ใน volume `jenkins_home` จึงอยู่รอดแม้ลบและสร้าง container `jenkins` ใหม่ (หลักการเดียวกับการทดลองที่ 7 ของ LAB 1) |
| ทำไมไม่ใช้ `--add-host` | ต้องลบและสร้าง Jenkins ใหม่ด้วยตัวเลือกพิเศษ แล็บนี้คงคำสั่งสร้าง Jenkins ของ LAB 1 ไว้ทุกตัวอักษร |
| ยืนยันว่าเป็นเครื่องจริงอย่างไร | บันทึก host key ของ `devtools` จากไฟล์ `/etc/ssh/ssh_host_ed25519_key.pub` ลง `known_hosts` ของ Jenkins ล่วงหน้า และตั้ง `StrictHostKeyChecking yes` ถ้าปลายทางไม่ใช่ `devtools` SSH จะปฏิเสธทันที |

### 3. SSH เป็นช่องทางสั่งงาน และสิทธิ์ที่มากับมัน

Jenkins ถือ private key ใน **Jenkins Credentials** ส่วน public key อยู่ใน `/root/.ssh/authorized_keys` ของ `devtools` ทุก stage ใช้ key นี้ login เป็น `root`

ต้องเข้าใจให้ชัดว่า key ชุดนี้ **มีอำนาจสูงมาก**:

- `root` บน `devtools` สั่ง Docker ของ `devtools` ได้ทุกอย่าง รวมถึงอ่าน volume `jenkins_home` (ซึ่งมี secret ของ Jenkins) และลบ `jenkins` ทิ้งได้
- `devtools` รันด้วย `--privileged` จึงเข้าถึงอุปกรณ์และ kernel ของเครื่องที่รันมันได้กว้างมาก
- การเลี่ยง `docker.sock` ไม่ได้ทำให้สิทธิ์ลดลงเป็นศูนย์ ข้อดีคือสิทธิ์ถูกผูกกับ **key หนึ่งชุดที่เห็น ตรวจ และเพิกถอนได้** (ลบบรรทัดใน `authorized_keys`) และ Jenkins image ยังเป็นของมาตรฐาน

> ⚠️ แบบนี้เหมาะกับแล็บที่ลบทิ้งได้เท่านั้น ระบบจริงควรใช้ build agent หรือผู้ใช้เฉพาะงานที่ไม่ใช่ `root` แยก key ต่อเครื่อง จำกัดต้นทางด้วยตัวเลือก `from="..."` ใน `authorized_keys` และไม่ใช้ container แบบ `--privileged`

### 4. คำสั่งหนึ่งบรรทัดผ่านมือใครบ้าง — shell context

แล็บนี้มี shell หลายชั้น ทุกคำสั่งในเอกสารระบุว่าให้พิมพ์ที่ไหน

| context | เข้าอย่างไร | ผู้ใช้ | ใช้ทำอะไรในแล็บ |
|---|---|---|---|
| ① terminal ของเครื่องเรา | เปิด terminal ปกติ | ผู้ใช้ของเรา | สร้าง/เริ่ม `devtools` เท่านั้น |
| ② shell ของ devtools | `ssh root@localhost -p 2222` | `root` | ตรวจสภาพ ตั้งค่า SSH ของ Jenkins สร้าง key |
| ③ ข้างใน `jenkins` | `docker exec jenkins ...` (พิมพ์ใน ②) | `jenkins` (uid 1000) | ส่องดูว่ามี/ไม่มีอะไร และทดสอบ SSH |
| ④ `sh` step ของ Pipeline | Jenkins รันให้ | `jenkins` | ตรวจ parameter แล้วเรียก `ssh devtools-gw ...` |
| ⑤ `bash -s` บน devtools | ปลายทางของ SSH จาก ④ | `root` | `git clone`, `docker build/run/push/pull` |

ค่าที่ผู้ใช้กรอก (parameter) เดินทางจาก Groovy → ④ → ข้าม SSH → ⑤ โดยที่ SSH ส่ง **ข้อความคำสั่ง** ให้ shell ปลายทางตีความอีกครั้ง ถ้าค่ามีอักขระอย่าง `;`, `$( )` หรือช่องว่าง shell ปลายทางจะรันมันเป็นคำสั่ง Jenkinsfile จึงตรวจ parameter ทุกตัวด้วย regular expression **บน Jenkins ก่อนเปิด SSH** ให้ผ่านได้เฉพาะอักขระที่ไม่มีความหมายพิเศษใน shell (พิสูจน์ในการทดลองที่ 10)

### 5. ซอร์สมาจาก Git — clone บน devtools ไม่ใช่บน Jenkins

stage **Clone** รัน `git clone` **บน devtools** (context ⑤) ซอร์สไม่ผ่าน Jenkins เลย และไม่พึ่งโฟลเดอร์ใดที่นักศึกษาเตรียมไว้ก่อน

| parameter | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `GIT_URL` | `https://github.com/Tuchsanai/DevTools.git` | repository สาธารณะของรายวิชา (repository เดียวกับที่ LAB 1 ใช้) |
| `GIT_REF` | `main` | branch หรือ tag |
| `APP_SUBDIR` | `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop` | โฟลเดอร์ที่มี `Dockerfile` = build context |
| `APP_VERSION` | `1.0.0` | เวอร์ชันที่ฝังเข้า image |

repository ของรายวิชามีขนาดใหญ่ (LAB 1 วัดได้ 1.3 GB) จึง clone แบบ `--depth 1 --filter=blob:none --sparse` แล้ว `git sparse-checkout set <APP_SUBDIR>` ดึงเฉพาะ commit ล่าสุดและเฉพาะไฟล์ในโฟลเดอร์ร้าน stage Build อ่าน commit ที่ clone มาแล้วฝังเข้า image เป็น `GIT_COMMIT` หน้าร้านจึงบอกได้ว่ามาจาก commit ใด

> ถ้า fork repository ไปเป็นของตัวเอง ให้เปลี่ยน `GIT_URL` ตอน **Build with Parameters** ได้ทันที โดยไม่ต้องแก้ Jenkinsfile

### 6. Image, Tag และ Digest

| คำศัพท์ | ความหมาย |
|---|---|
| **Image** | แพ็กเกจอ่านอย่างเดียว ประกอบจาก **layer** ซ้อนกัน |
| **Registry / Repository / Tag** | ที่เก็บ image (Docker Hub) / ชุด image (`<DOCKER_USER>/catfood-shop`) / ป้ายที่ย้ายได้ (`1`, `2`, `latest`) |
| **Digest** | `sha256:...` ที่คำนวณจากเนื้อหา image — เนื้อหาเดียวกันได้ digest เดียวกันเสมอ |

stage Pull ลบ image ในเครื่องทิ้งแล้วดึงกลับจาก registry จากนั้นเทียบ digest ถ้าตรงกันแปลว่า image ที่จะ deploy คือ image ที่เพิ่ง push ทุกบิต

---

## 🎯 Learning Objectives — ผลลัพธ์การเรียนรู้

เมื่อจบแล็บนี้ นักศึกษาจะสามารถ

1. อธิบาย Docker สองชั้นของแล็บ และเหตุผลที่ `jenkins` resolve ชื่อ `devtools` ไม่ได้
2. หา gateway ของ `cicd-net` จากเครื่องจริง แล้วตั้ง SSH Host alias ที่ตรวจ host key ได้ โดยไม่เขียน IP ตายตัวและไม่สร้าง Jenkins ใหม่
3. เตรียม SSH key และ Docker Hub token ใน Jenkins Credentials และอธิบายสิทธิ์ที่ key ชุดนั้นได้รับ
4. อ่าน Jenkinsfile แล้วบอกได้ว่าแต่ละบรรทัดทำงานใน context ใด และตัวแปรถูกแทนค่าที่ฝั่งใด
5. รัน Pipeline 7 stage แล้วสืบย้อนจากหน้าเว็บ → container → digest → build → commit ได้
6. ออกเวอร์ชันใหม่ด้วย Build with Parameters และเห็นผลของ layer cache
7. แสดงให้เห็นว่าการตรวจ parameter หยุดค่าอันตรายก่อนข้าม SSH

## 🗺️ แผนที่การทดลอง

| ส่วน | การทดลอง | ทำอะไร | หลักฐานที่ต้องได้ |
|---|---|---|---|
| 0. เตรียมเครื่อง | — | เริ่มใหม่ หรือทำต่อจาก LAB 1–2 | `jenkins` `Up`, มี `cicd-net` และ `jenkins_home` |
| A. สำรวจ | 1–2 | Jenkins ไม่มี Docker · ชื่อ `devtools` resolve ไม่ได้ | `exit=127` · `devtools exit=2` |
| B. เส้นทาง SSH | 3–5 | หา gateway · ตั้ง `devtools-gw` · สร้าง key | `Permission denied (publickey,password)` ก่อนมี key · `key OK: root@...` |
| C. Credentials | 6 | เก็บ `devtools-ssh` และ `dockerhub` | หน้า Credentials มี 2 รายการ |
| D. Pipeline | 7–8 | สร้าง job `docker-build-push` แล้ว Build | build #1 `SUCCESS` ครบ 7 stage · ร้านขึ้นที่ `localhost:3000` |
| E. เวอร์ชันใหม่ | 9 | Build with Parameters `1.1.0` | `CACHED` 5 ขั้น · ร้านเป็น `v1.1.0 · build #2` |
| F. ป้องกันค่าอันตราย | 10 | กรอก parameter ผิดรูปแบบ | ล้มที่ Preflight โดยไม่มีบรรทัด `+ ssh` |

## 📂 ไฟล์ในโฟลเดอร์นี้

| ไฟล์ | หน้าที่ |
|---|---|
| `Jenkinsfile` | Pipeline 7 stage: Preflight → Clone → Build → Test → Push → Pull → Deploy (เนื้อหาเดียวกับหัวข้อ “Jenkinsfile ฉบับสมบูรณ์” ด้านล่าง) |
| `catfood-shop/` | ซอร์สร้าน Meow Mart (Next.js 16 + React 19) ซึ่ง stage Clone ดึงจาก GitHub — ไม่ต้อง copy เอง |
| `catfood-shop/Dockerfile` | Dockerfile แบบ single-stage + `HEALTHCHECK` รับ `APP_VERSION`, `BUILD_NUMBER`, `GIT_COMMIT`, `BUILD_TIME` |

---

## 0. เตรียมเครื่องเรียน

เลือก **ทางใดทางหนึ่ง** ตามสภาพเครื่องของตนเอง

### ทาง A — เริ่มใหม่ทั้งหมด (ยังไม่มี `devtools` หรือยอมทิ้งของเดิมทั้งหมด)

พิมพ์ใน **① terminal ของเครื่องเรา** — ชุดคำสั่งเดียวกับ LAB 1 ส่วนที่ 0:

```bash
docker rm -f devtools
docker run -dit --name devtools --privileged --tmpfs /run \
  -p 2222:22 -p 8080:8080 -p 3000:3000 -p 8000:8000 \
  tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> ⚠️ `docker rm -f devtools` **ลบทุกอย่างข้างใน devtools** รวม Jenkins, job และประวัติ build ของ LAB 1–2 ใช้ทาง A เฉพาะเมื่อตั้งใจเริ่มใหม่จริง ๆ · รหัส `passwd` ใช้ได้กับ image ของแล็บนี้เท่านั้น

จากนั้นใน **② shell ของ devtools** สร้าง Jenkins ด้วยคำสั่งเดิมของ LAB 1 ทุกตัวอักษร:

```bash
docker network create cicd-net
docker run -d --name jenkins --network cicd-net --restart unless-stopped \
  -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21
```

แล้วทำ **การทดลองที่ 3–4 ของ [LAB 1](../001_LAB_Jenkins_On_Docker/README.md)** ให้เสร็จ (ปลดล็อกด้วย `initialAdminPassword`, เลือก **Install suggested plugins**, สร้างผู้ดูแล `admin` / `admin2569`) — ชุด suggested plugins มี Pipeline, Credentials Binding และ SSH Credentials ที่แล็บนี้ใช้

### ทาง B — ทำต่อจาก LAB 1–2 (แนะนำ)

**ห้าม** `docker rm -f devtools` และห้ามสร้าง Jenkins ใหม่ — Jenkins, ผู้ใช้ และ job เดิมอยู่ข้างใน `devtools` ครบแล้ว ใน **① terminal ของเครื่องเรา**:

```bash
docker start devtools
ssh root@localhost -p 2222        # password : passwd
```

`docker start` กับ container ที่รันอยู่แล้วไม่มีผลเสีย ถ้า `jenkins` ยังไม่ขึ้นให้รอสักครู่ (`--restart unless-stopped` จะเริ่มให้เอง)

### ตรวจสภาพตั้งต้น (ทั้งสองทาง)

ใน **② shell ของ devtools**:

<!-- lab3-test:check-state -->
{{block:check-state}}

✅ **ผลจากรอบทดสอบ** (subnet และเวลาของแต่ละเครื่องอาจต่างกัน):

```text
{{out:check-state}}
```

> ถ้าไม่มีแถว `jenkins` หรือ network `cicd-net` แปลว่ายังไม่ได้ทำ LAB 1 ให้กลับไปทำทาง A · ถ้าขึ้น `Cannot connect to the Docker daemon` ดูแถว `docker.pid` ในแก้ปัญหาของ LAB 1

**Prerequisite Docker Hub:** สมัครบัญชีและยืนยันอีเมล สร้าง **Personal Access Token สิทธิ์ Read & Write** (Account settings → Personal access tokens) เก็บ token ไว้สำหรับการทดลองที่ 6 เท่านั้น แนะนำให้สร้าง repository `catfood-shop` แบบ **Public** เพื่อเปิดดูหน้า Tags ได้โดยไม่ต้อง login (Pipeline login ทั้งตอน push และ pull จึงใช้กับ Private ได้เช่นกัน)

---

## A. สำรวจสภาพแวดล้อม

### การทดลองที่ 1 — ข้างใน Jenkins ไม่มี Docker แต่มี SSH client

**ทำอะไร:** ส่องเข้าไปใน container `jenkins` ว่ามีเครื่องมืออะไร

**ทำไม:** เพื่อยืนยันว่าทางเดียวที่ Jenkins จะสั่ง Docker ได้คือส่งคำสั่งไปให้เครื่องอื่น

ใน **② shell ของ devtools**:

<!-- lab3-test:exp1-no-docker -->
{{block:exp1-no-docker}}

✅ **ผลจากรอบทดสอบ:**

```text
{{out:exp1-no-docker}}
```

🔍 **ตีความ:** exit code `127` = หาโปรแกรม `docker` ไม่เจอ Jenkins รันเป็นผู้ใช้ `jenkins` ที่มี home อยู่ที่ `/var/jenkins_home` (อยู่ใน volume) และมี OpenSSH client มาให้แล้ว — ไฟล์ `~/.ssh/config` ของผู้ใช้นี้จึงอยู่ใน volume `jenkins_home` ด้วย ซึ่งเป็นกุญแจของการทดลองที่ 4

### การทดลองที่ 2 — ชื่อ `devtools` ไม่มีความหมายใน network ของ Jenkins

**ทำอะไร:** ให้ `jenkins` ลอง resolve ชื่อ `devtools` เทียบกับชื่อตัวเอง

**ทำไม:** เพื่อเห็นด้วยตาว่าทำไมเขียน `root@devtools` ใน Jenkinsfile ตรง ๆ ไม่ได้ (ทฤษฎีข้อ 2)

<!-- lab3-test:exp2-dns -->
{{block:exp2-dns}}

✅ **ผลจากรอบทดสอบ:**

```text
{{out:exp2-dns}}
```

🔍 **ตีความ:** `getent` หา `devtools` ไม่เจอ (exit `2`) แต่หา `jenkins` เจอ เพราะ DNS `127.0.0.11` ของ Docker ข้างใน devtools รู้จักเฉพาะ container บน `cicd-net` ของตัวเอง บรรทัดสุดท้ายคือ hostname ของ devtools ซึ่งเป็น container ID ไม่ใช่ `devtools` — ชื่อ `devtools` มีอยู่เฉพาะบน Docker ของเครื่องเรา

---

## B. สร้างเส้นทาง SSH จาก Jenkins กลับมาที่ devtools

### การทดลองที่ 3 — หา gateway ของ `cicd-net`

**ทำอะไร:** อ่าน subnet และ gateway ของ `cicd-net` IP ของ `jenkins` และ IP ทั้งหมดของ devtools

<!-- lab3-test:exp3-gateway -->
{{block:exp3-gateway}}

✅ **ผลจากรอบทดสอบ** (ตัวเลขของแต่ละเครื่องอาจต่างกัน — ใช้ค่าของเครื่องตนเอง):

```text
{{out:exp3-gateway}}
```

🔍 **ตีความ:** gateway ของ `cicd-net` ปรากฏอยู่ในรายการ IP ของ devtools (`hostname -I`) จริง และ `jenkins` อยู่ subnet เดียวกัน → packet จาก `jenkins` ไปที่ gateway ถึง devtools โดยตรง นี่คือปลายทาง SSH ของเรา

### การทดลองที่ 4 — ตั้ง SSH Host alias `devtools-gw` ไว้ใน `jenkins_home`

**ทำอะไร:** เขียน `~/.ssh/config` และ `~/.ssh/known_hosts` ให้ผู้ใช้ `jenkins` จากค่าที่อ่านได้จริง

**ทำไม:** Jenkinsfile จะอ้างเพียงชื่อ `devtools-gw` ส่วน IP จริงอยู่ในไฟล์ config ที่เก็บใน volume — เปลี่ยนเครื่องก็แค่รันบล็อกนี้ใหม่

<!-- lab3-test:exp4-ssh-alias -->
{{block:exp4-ssh-alias}}

📝 **คำอธิบาย:**

- บรรทัดแรกอ่าน gateway จาก `docker network inspect` แล้วกรองเอาเฉพาะรูปแบบ IPv4 บรรทัดที่สองตรวจว่า IP นั้นเป็นของ devtools จริง ถ้าไม่ใช่จะหยุด ไม่เขียนไฟล์ผิด ๆ
- heredoc `<<EOF` (ไม่มีอัญประกาศ) ตั้งใจให้ shell ของ devtools แทนค่า `$GW` ก่อนส่งเนื้อหาเข้า `docker exec -i ... cat > ~/.ssh/config` ซึ่งรันเป็นผู้ใช้ `jenkins` (`-u jenkins`) ไฟล์จึงเป็นของ `jenkins` และ `umask 077` ทำให้ได้สิทธิ์ `600` ตามที่ OpenSSH ต้องการ
- `HostKeyAlias devtools-gw` + บรรทัด `known_hosts` ที่อ่านจาก `/etc/ssh/ssh_host_ed25519_key.pub` ของ devtools โดยตรง ทำให้ Jenkins รู้จัก host key ล่วงหน้า **โดยไม่ต้องเชื่อเครือข่ายครั้งแรก** และ `StrictHostKeyChecking yes` ปฏิเสธเครื่องที่ key ไม่ตรง
- `BatchMode yes` ห้ามถามรหัสผ่าน (Pipeline ไม่มีคนพิมพ์) `IdentitiesOnly yes` ใช้เฉพาะ key ที่ส่งมาด้วย `-i` และ `ConnectTimeout 10` ทำให้ล้มเร็วถ้าเส้นทางใช้ไม่ได้

✅ **ผลจากรอบทดสอบ:**

```text
{{out:exp4-ssh-alias}}
```

ทดสอบการเชื่อมต่อจากข้างใน `jenkins` (ยังไม่มี key — ตั้งใจให้ถูกปฏิเสธ):

<!-- lab3-test:exp4-test -->
{{block:exp4-test}}

✅ **ผลจากรอบทดสอบ:**

```text
{{out:exp4-test}}
```

🔍 **ตีความ:** `ssh -G` แสดงค่าที่ SSH จะใช้จริงสำหรับ `devtools-gw` ส่วน `Permission denied (publickey,password)` เป็นผลที่ **ถูกต้อง** — แปลว่าเส้นทางถึง `sshd` ของ devtools แล้ว และ host key ผ่านการตรวจแล้ว (ถ้า key ไม่ตรงจะเห็น `Host key verification failed` แทน) ที่ขาดอยู่มีเพียง credential

> ✅ ไม่ได้ลบหรือสร้าง `jenkins` ใหม่เลย · ถ้าภายหลังลบ network `cicd-net` แล้วสร้างใหม่ gateway อาจเปลี่ยน ให้รันบล็อกนี้ซ้ำ

### การทดลองที่ 5 — สร้าง SSH key ให้ Jenkins ใช้เข้า devtools

ใน **② shell ของ devtools**:

<!-- lab3-test:exp5-key -->
{{block:exp5-key}}

📝 **คำอธิบาย:** สร้าง key ed25519 เฉพาะเมื่อยังไม่มี (รันซ้ำได้ ไม่ทับ key เดิม) `-N ''` = ไม่มี passphrase เพื่อให้ Jenkins ใช้ได้โดยไม่มีคนพิมพ์ แล้วต่อ public key ท้าย `authorized_keys` เฉพาะเมื่อยังไม่มีบรรทัดนี้ `ssh-keygen -l` แสดง fingerprint และบรรทัดสุดท้ายนับว่ามี key นี้ใน `authorized_keys` กี่บรรทัด

✅ **ผลจากรอบทดสอบ** (fingerprint ของแต่ละเครื่องต่างกัน บรรทัดสุดท้ายต้องเป็น `1`):

```text
{{out:exp5-key}}
```

ลอง key กับ sshd ของ devtools ก่อนนำไปใส่ Jenkins:

<!-- lab3-test:exp5-keytest -->
{{block:exp5-keytest}}

✅ **ผลจากรอบทดสอบ:**

```text
{{out:exp5-keytest}}
```

> 📝 การทดสอบนี้ต่อเข้า `127.0.0.1` ของ devtools เอง จึงปิดการตรวจ host key เฉพาะคำสั่งนี้ ฝั่ง Jenkins ยังตรวจเข้มตามการทดลองที่ 4

---

## C. Credentials

### การทดลองที่ 6 — เก็บ SSH key และ Docker Hub token ใน Jenkins Credentials

**ทำไม:** Pipeline ต้องใช้ความลับสองชิ้นโดยไม่เขียนลงโค้ด แยก `devtools-ssh` (ทุก stage) ออกจาก `dockerhub` (เฉพาะ stage ที่ต้องรู้บัญชี) เพื่อเปลี่ยนหรือเพิกถอนทีละชิ้นได้

> ภาพหน้าจอในหัวข้อนี้เป็น **ภาพจากรอบทดสอบของ LAB 3 ฉบับก่อน (25 ก.ย. 2569, Jenkins 2.568.3)** ฟอร์มและ ID ที่ใช้เหมือนเดิมทุกช่อง

1. เปิด `http://localhost:8080` → login `admin` / `admin2569` → **Manage Jenkins → Credentials** → **System → Global credentials (unrestricted)** → **Add Credentials**

![Manage Jenkins → Credentials](./images/lab3_b3a_manage_jenkins.png)

*ภาพที่ 2 เมนู Credentials ในหมวด Security (ภาพจากรอบทดสอบฉบับก่อน)*

**(ก) SSH key สำหรับเข้า devtools**

2. เลือกชนิด **SSH Username with private key** → **Next**

![เลือกชนิด SSH Username with private key](./images/lab3_b3b_credential_kind_ssh.png)

*ภาพที่ 3 เลือกชนิด credential (ภาพจากรอบทดสอบฉบับก่อน)*

3. แสดง private key ใน **② shell ของ devtools** แล้วคัดลอก **ทั้งไฟล์** รวมบรรทัด `-----BEGIN OPENSSH PRIVATE KEY-----` และ `-----END OPENSSH PRIVATE KEY-----`

```bash
cat ~/.ssh/jenkins_devtools
```

4. กรอก **ID** = `devtools-ssh`, **Description** = `SSH key: Jenkins to devtools`, **Username** = `root` เลือก **Private Key → Enter directly** วางเนื้อหาที่คัดลอกมา ปล่อย **Passphrase** ว่าง → **Create**

![แบบฟอร์ม SSH key](./images/lab3_b3c_ssh_credential_form.png)

*ภาพที่ 4 ช่อง Key ในภาพเป็นข้อความตัวอย่าง ให้วางเนื้อหาไฟล์ `~/.ssh/jenkins_devtools` ของตนเอง (ภาพจากรอบทดสอบฉบับก่อน)*

**(ข) Docker Hub token**

5. **Add Credentials** อีกครั้ง → **Username with password** → Username = `<DOCKER_USER>` (ตัวพิมพ์เล็ก), Password = `<DOCKER_TOKEN>`, ID = `dockerhub`, Description = `Docker Hub access token` → **Create**

![แบบฟอร์ม Docker Hub](./images/lab3_b3d_dockerhub_credential_form.png)

*ภาพที่ 5 ID `dockerhub` คือชื่อที่ Jenkinsfile อ้างถึง (ภาพจากรอบทดสอบฉบับก่อน)*

✅ **สิ่งที่ต้องเห็น:** หน้า Global credentials มีสองรายการ `devtools-ssh` และ `dockerhub` แสดงเพียง ID และคำอธิบาย ไม่แสดง private key หรือ token

![รายการ credential สองตัว](./images/lab3_b3e_credentials_list.png)

*ภาพที่ 6 (ภาพจากรอบทดสอบฉบับก่อน)*

> ⚠️ private key และ token วางได้ที่ Jenkins Credentials เท่านั้น ห้ามวางในแชต เอกสาร หรือ commit ลง Git · Jenkinsfile ตรวจ username ของ `dockerhub` ว่ามีเฉพาะ `a-z0-9` ตามกติกาชื่อบัญชี Docker Hub ก่อนนำไปประกอบชื่อ image

---

## D. Pipeline

### อ่าน Jenkinsfile ก่อนรัน

ทุก stage มีรูปแบบเดียวกัน ดู stage **Clone** เป็นตัวอย่าง:

```groovy
withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY')]) {
  sh '''
    ssh -i "$SSH_KEY" "$DEVTOOLS" \
      "WORK_DIR=$WORK_DIR GIT_URL=$GIT_URL GIT_REF=$GIT_REF APP_SUBDIR=$APP_SUBDIR bash -s" <<'EOF'
set -euo pipefail
...
git clone --depth 1 --filter=blob:none --sparse --branch "$GIT_REF" -- "$GIT_URL" "$WORK_DIR"
...
EOF
  '''
}
```

| ส่วน | ทำงานที่ | อธิบาย |
|---|---|---|
| `withCredentials([sshUserPrivateKey(...)])` | Jenkins | เขียน private key เป็นไฟล์ชั่วคราว ใส่ path ใน `$SSH_KEY` และลบเมื่อจบบล็อก console แสดงเป็น `ssh -i ****` |
| `sh '''...'''` | Groovy | อัญประกาศเดี่ยวสามตัว Groovy **ไม่แทนค่า** `$` ส่งทั้งก้อนให้ shell ④ |
| `"$DEVTOOLS"` | shell ④ | = `devtools-gw` → SSH อ่าน HostName/User/host key จาก `~/.ssh/config` (การทดลองที่ 4) |
| `"WORK_DIR=$WORK_DIR ... bash -s"` | shell ④ แทนค่า → shell ⑤ ตีความ | ค่าเหล่านี้ผ่านการตรวจใน Preflight แล้ว จึงไม่มีอักขระพิเศษของ shell `bash -s` = อ่านสคริปต์จาก stdin |
| `<<'EOF'` … `EOF` | ส่งทาง stdin | heredoc ที่ **มีอัญประกาศ** ทำให้ shell ④ ไม่แตะเนื้อสคริปต์ ทุก `$` ข้างในถูกแทนค่าโดย bash ⑤ บน devtools |
| `git clone ... -- "$GIT_URL"` | bash ⑤ | `--` บอก git ว่าต่อจากนี้ไม่ใช่ option และค่าทุกตัวอยู่ในอัญประกาศคู่ |

| Stage | ทำงานที่ | ทำอะไร | ตรวจผ่าน/ไม่ผ่าน |
|---|---|---|---|
| **Preflight** | Jenkins (Groovy + ④) แล้ว SSH | ตรวจ parameter 4 ตัวและ username Docker Hub · พิมพ์ว่า Jenkins ไม่มี docker · SSH ไปถามชื่อเครื่อง ผู้ใช้ Docker และ git ของ devtools | ค่าผิดรูปแบบหรือ SSH ไม่ได้ → หยุดก่อนงานหนัก |
| **Clone** | devtools | sparse clone `GIT_URL`@`GIT_REF` ลง `/root/lab3-work/build-N` แสดง commit | ไม่มี `Dockerfile` ใน `APP_SUBDIR` → ล้ม |
| **Build** | devtools | `docker build --provenance=false` พร้อม build-arg เวอร์ชัน เลข build commit และเวลา → `catfood-shop:N` | build ล้ม → ล้ม |
| **Test** | devtools | รัน `catfood-test-N` รอ `healthy` ≤ 30 วินาที อ่าน `/api/health` ต้องมีเวอร์ชันที่สั่ง แล้วลบ container เสมอ | ไม่ `healthy` หรือเวอร์ชันไม่ตรง → ไม่ push |
| **Push** | devtools | login ด้วย token ทาง stdin ลง `DOCKER_CONFIG` ชั่วคราว → push `:N` และ `:latest` → logout และลบ config | push ล้ม → ล้ม |
| **Pull** | devtools | จำ digest → ลบ image ในเครื่อง → login → pull `:N` → เทียบ digest | digest ไม่ตรง → ไม่ deploy |
| **Deploy** | devtools | ตรวจว่า port 3000 ไม่ถูก container อื่นใช้ → แทน `catfood-web` ด้วย image ที่ pull มา `-p 3000:3000` → รอ `healthy` → เทียบเวอร์ชัน | ไม่ตรง → ล้ม |

`disableConcurrentBuilds()` ห้ามสอง build ทำงานพร้อมกัน เพราะทุก build แทนที่ container `catfood-web` และใช้ port 3000 เดียวกัน

### Jenkinsfile ฉบับสมบูรณ์

เนื้อหาเดียวกับไฟล์ [`Jenkinsfile`](./Jenkinsfile) ในโฟลเดอร์นี้ทุกตัวอักษร คัดลอกทั้งบล็อกไปวางใน Jenkins

```groovy
{{jenkinsfile}}
```

### การทดลองที่ 7 — สร้าง job `docker-build-push`

1. Dashboard → **New Item** → ชื่อ `docker-build-push` → **Pipeline** → **OK**

![New Item docker-build-push](./images/lab3_d1a_new_item_pipeline.png)

*ภาพที่ 7 สร้าง job ชนิด Pipeline (ภาพจากรอบทดสอบฉบับก่อน หน้าจอนี้ไม่เปลี่ยน)*

2. หัวข้อ **Pipeline → Definition: Pipeline script** วาง Jenkinsfile ฉบับสมบูรณ์ทั้งไฟล์ คง **Use Groovy Sandbox** ไว้ → **Save**

<!-- ภาพหน้าจอ editor ที่มี Jenkinsfile ฉบับนี้ รอผู้ประสานงานถ่ายจาก UI จริง -->

> 📝 build แรกยังไม่มีปุ่ม Build with Parameters เพราะ Jenkins จะรู้จัก `parameters { ... }` หลังรัน Jenkinsfile ครั้งแรก Jenkinsfile จึงคัดลอก `params.*` ลงบล็อก `environment` ให้ build แรกได้ค่า default ครบ (รอบทดสอบพบว่าถ้าไม่ทำเช่นนี้ build แรกได้ `GIT_URL=` ว่างแล้ว clone ล้ม)

### การทดลองที่ 8 — Build Now: ดูหลักฐานทีละ stage

กด **Build Now** แล้วเปิด build **#1** → **Console Output** (หรือหน้า Stages ของ Pipeline Graph View)

<!-- ภาพหน้าจอ Stages ของ build #1 และหน้า Tags บน Docker Hub รอผู้ประสานงานถ่ายจากการรันจริงกับ Docker Hub -->

✅ **ผลจากรอบทดสอบ** (ตัดบรรทัด `[Pipeline]` ออก เลือกช่วงสำคัญของแต่ละ stage):

**Preflight** — Jenkins ไม่มี docker แต่สั่ง devtools ได้

```text
{{out:b1-preflight}}
```

hostname `{{val:jenkins_host}}` คือ container `jenkins` ส่วน `{{val:devtools_host}}` คือ hostname ของ devtools ตรงกับการทดลองที่ 2 และ `****` คือ path ของ key ที่ Jenkins ปิดบัง

**Clone** — ซอร์สมาจาก GitHub ลงบน devtools

```text
{{out:b1-clone}}
```

commit ที่ได้คือ commit ล่าสุดของ `main` ในวันที่ทดสอบ ของนักศึกษาจะเป็น commit ล่าสุด ณ วันที่รัน

**Build** — image ถูกสร้างจากซอร์สที่เพิ่ง clone

```text
{{out:b1-build}}
```

**Test** — แอปใน image ตอบ health และเวอร์ชันถูกต้อง

```text
{{out:b1-test}}
```

**Push และ Pull** — ⏳ *รอหลักฐานจากการรันจริงกับ Docker Hub* รอบทดสอบของเอกสารนี้ไม่ได้ push ขึ้น Docker Hub จริง (ใช้ registry จำลองที่ต้อง login ภายใน container ทดลองแทน) จึงไม่แสดง output ที่นี่ สิ่งที่นักศึกษาต้องตรวจเองใน console:

- stage Push มี `Login Succeeded` และบรรทัด `1: digest: sha256:...` กับ `latest: digest: sha256:...` เป็นค่าเดียวกัน
- stage Pull มี `digest ที่ push: sha256:...` → `Untagged` / `Deleted` → `Pulling from ...` → `digest ที่ pull: sha256:...` และจบด้วย `digest ตรงกัน`
- เปิด `https://hub.docker.com/r/<DOCKER_USER>/catfood-shop/tags` เห็น tag `1` และ `latest` ที่ digest 12 ตัวแรกตรงกับ console (ได้ผลตรงกันเพราะ `--provenance=false`)

**Deploy** — ร้านเปิดที่ port 3000 จาก image ที่ pull มา

```text
{{out:b1-deploy}}
```

> 📝 รอบทดสอบใช้ registry จำลอง `localhost:5000` ชื่อ image ใน console จึงขึ้นต้นด้วย `localhost:5000/****/` ของนักศึกษาจะเป็น `docker.io/****/catfood-shop:1` (`****` คือ username ที่ Jenkins ปิดบัง) ส่วนบรรทัดอื่นมีรูปแบบเดียวกัน

ตรวจจาก **② shell ของ devtools** ว่าร้านเป็น container พี่น้องบน Docker ของ devtools:

<!-- lab3-test:verify-web -->
{{block:verify-web}}

✅ **ผลจากรอบทดสอบ** (หลัง build #1):

```text
{{out:verify-web-b1}}
```

จากนั้นเปิด `http://localhost:3000` บนเครื่องของเรา chip บนแถบด้านบนต้องเป็น `v1.0.0 · build #1` และ Deployment info ต้องแสดง commit และ container ตรงกับ `/api/health`

<!-- ภาพหน้าร้านและ Deployment info ของ build #1 จากการรันจริง รอผู้ประสานงานถ่ายผ่าน SSH tunnel -->

🔍 **สืบย้อน:** หน้าเว็บ → container `catfood-web` (`host` ใน `/api/health`) → image `:1` ที่ pull จาก registry → digest ที่เทียบแล้วใน stage Pull → build #1 ของ Jenkins → `commit` จาก stage Clone

---

## E. ออกเวอร์ชันใหม่

### การทดลองที่ 9 — Build with Parameters `APP_VERSION=1.1.0`

1. เปิด job `docker-build-push` → **Build with Parameters**
2. เปลี่ยนเฉพาะ `APP_VERSION` เป็น `1.1.0` (ช่องอื่นคงค่าเดิม) → **Build**

✅ **ผลจากรอบทดสอบ** — stage Build ของ build #2:

```text
{{out:b2-build}}
```

และ stage Deploy:

```text
{{out:b2-deploy}}
```

| วัดค่า | build #1 (v1.0.0) | build #2 (v1.1.0) |
|---|---:|---:|
| ระยะเวลารวม (รอบทดสอบ) | {{val:b1_duration}} | {{val:b2_duration}} |
| ขั้น `CACHED` ใน stage Build | {{val:b1_cached}} | {{val:b2_cached}} |
| บรรทัด `Pushed` ใน stage Push | {{val:b1_pushed}} | {{val:b2_pushed}} |

🔍 **ตีความ:** ซอร์ส commit เดิม เปลี่ยนเพียง `APP_VERSION`, `BUILD_NUMBER` และ `BUILD_TIME` ซึ่ง Dockerfile วางไว้ท้ายสุดเป็น `ENV` (metadata) ทุกขั้นที่สร้างไฟล์จึง `CACHED` และไม่มี layer ใหม่ต้องอัปโหลด แต่ digest ยังเปลี่ยนเพราะ config ของ image เปลี่ยน · Clone ของ build #2 ดึงซอร์สใหม่ลง `build-2` แต่ไฟล์ที่ได้เหมือนเดิม cache ของ `COPY . .` จึงยังใช้ได้

บน Docker Hub (ตรวจเอง — ⏳ รอหลักฐานจริง): tag `latest` ต้องย้ายมาชี้ digest เดียวกับ tag `2` ส่วน tag `1` ยังชี้ digest ของ build #1 — **deploy ด้วย tag แต่ตรวจสอบด้วย digest**

---

## F. ป้องกันค่าอันตรายก่อนข้าม SSH

### การทดลองที่ 10 — กรอก parameter ที่แฝงคำสั่ง shell

**ทำอะไร:** Build with Parameters โดยกรอก `APP_VERSION` เป็น `1.2.0; id` (มี `;` และช่องว่าง)

**ทำไม:** ถ้าค่านี้ถูกส่งถึง shell ⑤ ตรง ๆ `id` จะถูกรันเป็น `root` บน devtools

✅ **ผลจากรอบทดสอบ** (build #3):

```text
{{out:b3}}
```

🔍 **ตีความ:** build ล้มใน Preflight ภายในราว {{val:b3_duration}} และ console **ไม่มีบรรทัด `+ ssh` เลย** ค่าอันตรายไม่เคยออกจาก Jenkins ร้านยังเป็น build #2 ตามเดิม ลองแบบเดียวกันกับ `APP_SUBDIR` = `../../etc` ก็จะได้ `APP_SUBDIR ไม่ถูกต้อง` ส่วน `GIT_REF` ที่รูปแบบถูกแต่ไม่มีอยู่จริง (เช่น `no-such-branch`) ผ่าน Preflight แต่ไปล้มที่ Clone ด้วย `fatal: Remote branch no-such-branch not found in upstream origin`

---

## ✅ ตรวจปิดแล็บ

- [ ] `docker exec jenkins sh -c 'docker version'` ยังได้ `docker: not found` และ `jenkins` ยังเป็น container เดิมจาก LAB 1 (ไม่ได้สร้างใหม่)
- [ ] `docker exec jenkins ssh -G devtools-gw` แสดง `hostname` เป็น gateway ของ `cicd-net` ในเครื่องตนเอง
- [ ] หน้า Credentials มี `devtools-ssh` และ `dockerhub`
- [ ] job `docker-build-push` build #1 และ #2 เป็น `SUCCESS` ครบ Preflight → Clone → Build → Test → Push → Pull → Deploy
- [ ] stage Clone ของ build #2 แสดง commit และ `/api/health` ของร้านมี `commit` ตรงกับ 12 ตัวแรกของ commit นั้น
- [ ] stage Pull ของ build #2 จบด้วย `digest ตรงกัน` และหน้า Tags บน Docker Hub แสดง `latest` กับ `2` เป็น digest เดียวกัน
- [ ] `http://localhost:3000` แสดง `v1.1.0 · build #2`
- [ ] build ที่กรอก `APP_VERSION=1.2.0; id` ล้มที่ Preflight โดยไม่มีบรรทัด `+ ssh`

## 📊 สรุปผลการทดสอบของเอกสารนี้

ทดสอบเมื่อ {{val:test_date}} ใน container ทดลองแยกจาก image `tuchsanai/devtools:2569_1` (สร้างด้วย `--privileged --tmpfs /run` แบบเดียวกับทาง A) และ Jenkins จาก `jenkins/jenkins:lts-jdk21` ด้วยคำสั่งสร้างของ LAB 1 ทุกตัวอักษร

| รายการ | ผล |
|---|---|
| `jenkins` resolve `devtools` | ไม่ได้ (exit 2) |
| SSH ผ่าน `devtools-gw` → gateway ของ `cicd-net` | ถึง sshd และตรวจ host key ผ่าน |
| build #1 (clone จาก GitHub `main`) | `SUCCESS` ครบ 7 stage ใน {{val:b1_duration}} |
| build #2 (`1.1.0`) | `SUCCESS` ใน {{val:b2_duration}}, `CACHED` {{val:b2_cached}} ขั้น |
| build #3 (`1.2.0; id`) | `FAILURE` ที่ Preflight ไม่มีการเปิด SSH |
| `docker restart` ของ devtools แล้ว build ใหม่ | {{val:restart_result}} |
| Push/Pull กับ **Docker Hub จริง** และภาพหน้าจอ UI | ⏳ ยังไม่ได้ทดสอบ (รอบนี้ใช้ registry จำลองที่ต้อง login) |

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ssh: Could not resolve hostname devtools-gw` | ยังไม่ได้ทำการทดลองที่ 4 หรือไฟล์ config ไม่ได้อยู่ใต้ `/var/jenkins_home/.ssh` | รันบล็อกของการทดลองที่ 4 แล้วตรวจด้วย `docker exec jenkins ssh -G devtools-gw` |
| `Connection timed out` / `No route to host` | gateway ใน config ไม่ใช่ของ `cicd-net` ปัจจุบัน (เช่น ลบแล้วสร้าง network ใหม่) หรือ `jenkins` ไม่ได้อยู่ใน `cicd-net` | รันบล็อกการทดลองที่ 3 เทียบค่า แล้วรันบล็อกการทดลองที่ 4 ซ้ำ |
| `Host key verification failed` | host key ใน `known_hosts` ไม่ตรงกับ devtools ปัจจุบัน (เช่น สร้าง devtools ใหม่แต่ใช้ volume เดิม) | รันบล็อกการทดลองที่ 4 ซ้ำ ซึ่งเขียน `known_hosts` จาก host key ปัจจุบัน |
| `Permission denied (publickey,password)` ใน Preflight | public key ไม่อยู่ใน `authorized_keys` หรือวาง private key ใน credential ไม่ครบ BEGIN/END | รันการทดลองที่ 5 แล้วแก้ credential `devtools-ssh` เป็นเนื้อหา `~/.ssh/jenkins_devtools` ทั้งไฟล์ |
| `Bad owner or permissions on /var/jenkins_home/.ssh/config` | สร้างไฟล์ด้วยผู้ใช้ root หรือสิทธิ์กว้างเกินไป | รันบล็อกการทดลองที่ 4 (ใช้ `-u jenkins` และ `umask 077`) |
| `ERROR: Could not find credentials entry with ID ...` | ID สะกดไม่ตรง | ตั้ง ID เป็น `devtools-ssh` และ `dockerhub` ตรงตัว |
| `username ใน credential dockerhub ต้องมีเฉพาะ a-z และ 0-9` | กรอกอีเมลหรือตัวพิมพ์ใหญ่ในช่อง Username | ใช้ Docker Hub username ตัวพิมพ์เล็ก |
| `... ไม่ถูกต้อง: ...` ใน Preflight | parameter ผิดรูปแบบ | แก้ค่าตามข้อความ (`X.Y.Z`, `https://...`, path แบบ relative) |
| `fatal: repository '...' not found` / `Remote branch ... not found` ใน Clone | `GIT_URL` ผิด เป็น repository ส่วนตัว หรือ `GIT_REF` ไม่มีอยู่ | เปิด URL ในเบราว์เซอร์ตรวจว่าเป็น Public และมี branch/tag นั้น |
| `ไม่พบ .../Dockerfile` ใน Clone | `APP_SUBDIR` ไม่ตรงกับโครงสร้าง repository | ตรวจ path บน GitHub ให้ชี้โฟลเดอร์ที่มี `Dockerfile` |
| stage Test ล้ม ไม่ถึง `healthy` | แอปเริ่มไม่ขึ้น | ใน ② `docker run -d --name debug-shop catfood-shop:N` แล้ว `docker logs debug-shop` (เสร็จแล้ว `docker rm -f debug-shop`) |
| `unauthorized` / `denied: requested access` ใน Push หรือ Pull | token ผิด หมดอายุ ไม่มีสิทธิ์ Write หรือ username ไม่ตรง | สร้าง token Read & Write ใหม่ แล้วแก้ credential `dockerhub` |
| `toomanyrequests` | Docker Hub rate limit | รอสักครู่แล้วสั่งใหม่ |
| `port 3000 ถูก container อื่นใช้อยู่: ...` ใน Deploy | มี container อื่นบน Docker ของ devtools publish 3000 | ใน ② `docker ps --filter publish=3000` ลบเฉพาะตัวที่ตนสร้างและไม่ใช้แล้ว |
| เปิด `localhost:3000` จากเครื่องเราไม่ได้ ทั้งที่ Deploy เขียว | `devtools` ไม่ได้ publish `-p 3000:3000` | ตรวจ `docker port devtools` บนเครื่องเรา ถ้าไม่มี 3000 ต้องสร้าง devtools ใหม่ตามทาง A (ข้อมูลข้างในจะหาย) |

## 🧹 เก็บกวาด

**ห้ามลบ** `devtools`, `jenkins`, volume `jenkins_home`, network `cicd-net` และ credential ทั้งสอง — LAB ถัดไปใช้ต่อ สิ่งที่แล็บนี้สร้างและลบได้อย่างปลอดภัย (ใน **② shell ของ devtools**):

<!-- lab3-test:cleanup -->
{{block:cleanup}}

เมื่อเลิกใช้ SSH จาก Jenkins แล้ว (เช่น จบรายวิชา) ให้ **เพิกถอนสิทธิ์**: ลบบรรทัดที่ลงท้าย `jenkins-to-devtools` ออกจาก `/root/.ssh/authorized_keys` ลบ credential `devtools-ssh` และ `dockerhub` ใน Jenkins และ revoke token ที่หน้า Docker Hub → Personal access tokens

## กู้สถานะเมื่อปิดเครื่องหรือเริ่มระบบใหม่

บน **① terminal ของเครื่องเรา** `docker start devtools` แล้วรอให้ Docker ข้างในและ `jenkins` กลับมา (ดู LAB 1 หัวข้อเดียวกัน) `catfood-web` มี `--restart unless-stopped` จึงกลับมาเองด้วย ไฟล์ `~/.ssh/config` ของ Jenkins, host key และ network `cicd-net` อยู่ข้างใน devtools ครบ gateway จึงเป็นค่าเดิม ไม่ต้องตั้งใหม่

## 🤔 คำถามทบทวน

1. ถ้าเขียน `ssh root@devtools` ใน Jenkinsfile จะเกิดอะไรขึ้น และทำไมการเปลี่ยนชื่อ container `devtools` บนเครื่องเราจึงไม่ช่วย
2. ทำไม `~/.ssh/config` ที่ตั้งไว้จึงยังอยู่หลัง `docker rm -f jenkins` แล้วสร้างใหม่ด้วยคำสั่งของ LAB 1
3. ถ้า private key ของ `devtools-ssh` รั่ว ผู้ที่ได้ไปทำอะไรได้บ้าง และเพิกถอนอย่างไร
4. heredoc `<<EOF` ในการทดลองที่ 4 กับ `<<'EOF'` ใน Jenkinsfile ต่างกันอย่างไร และทำไมแต่ละที่จึงเลือกแบบนั้น
5. ทำไมการตรวจ `APP_VERSION` ต้องเกิดบน Jenkins ก่อน `ssh` ไม่ใช่ในสคริปต์ฝั่ง devtools

➡️ **แล็บถัดไป:** [LAB 4 — Pipeline from Git](../004_LAB_Pipeline_From_Git/README.md)
