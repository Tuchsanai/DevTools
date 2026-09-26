# LAB 3 — Jenkins สั่ง devtools ผ่าน SSH: Connect → Clone → Build → Test → Push → Clean → Pull → Deploy ร้านอาหารแมว

> ⏱️ ประมาณ 60–75 นาที · 🧪 10 การทดลอง · 🎯 จบเมื่อกด **Build** ใน Jenkins แล้วเปิด `http://localhost:3000` เห็นร้าน **Meow Mart** ที่ Pipeline เพิ่ง clone, build, test, push ขึ้น Docker Hub, pull กลับมาตาม digest และ deploy และผ่านรายการ **✅ ตรวจปิดแล็บ** ครบทุกข้อ

แล็บนี้ตอบคำถามว่า **“Jenkins ที่ไม่มี Docker อยู่ข้างในเลย จะสั่งให้เกิด build → test → push → deploy ได้อย่างไร”** คำตอบคือ Jenkins ทำหน้าที่ **ผู้สั่ง** ส่วน `devtools` ทำหน้าที่ **ผู้ทำ** Jenkins เปิด SSH กลับไปที่ port 22 ของ `devtools` แล้วส่งสคริปต์ไปรันทีละ stage ตั้งแต่ `git clone` ซอร์สร้านจาก GitHub ไปจนถึงเปิดร้านเป็น container พี่น้อง (sibling) บน Docker ของ `devtools` ที่ port 3000

> **กติกาของแล็บ:** นักศึกษาไม่พิมพ์ `docker build`, `docker push` หรือ `git clone` ของร้านเอง ทุกอย่างเริ่มจากปุ่มบน Jenkins และ container `jenkins` ยังเป็น image มาตรฐานตัวเดิมจาก LAB 1 — **ไม่ติดตั้ง Docker CLI, ไม่ mount `docker.sock`, ไม่สร้าง Jenkins ใหม่** ส่วน Jenkinsfile ถูก **คัดลอกไปวางในช่อง Pipeline script** ของ job (ไม่ได้ให้ Jenkins checkout จาก Git)

![แผนภาพสถาปัตยกรรมของ LAB 3](./images/lab3_diagram_architecture.png)

*ภาพที่ 1 (แผนภาพประกอบ ไม่ใช่ภาพหน้าจอ) `jenkins` และ `catfood-web` อยู่บน Docker daemon ข้างใน `devtools` · Jenkins ส่งคำสั่งทาง SSH ไปที่ `sshd :22` ของ devtools · `git clone` และคำสั่ง `docker` ทั้งหมดรันบน devtools · image ขึ้น/ลงจาก Docker Hub · เบราว์เซอร์เข้าผ่าน port 8080 และ 3000 ที่ publish ต่อกันสองชั้น*

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
| เก็บค่าไว้ที่ไหน | SSH Host alias ชื่อ `devtools-gw` ใน `/var/jenkins_home/.ssh/config` ซึ่งอยู่ใน volume `jenkins_home` จึง **คงอยู่ถาวร** แม้ restart หรือลบแล้วสร้าง container `jenkins` ใหม่ (หลักการเดียวกับการทดลองที่ 7 ของ LAB 1) |
| ทำไมไม่ใช้ `--add-host` | ต้องลบและสร้าง Jenkins ใหม่ด้วยตัวเลือกพิเศษ แล็บนี้คงคำสั่งสร้าง Jenkins ของ LAB 1 ไว้ทุกตัวอักษร |
| ยืนยันว่าเป็นเครื่องจริงอย่างไร | บันทึก host key ของ `devtools` จากไฟล์ `/etc/ssh/ssh_host_ed25519_key.pub` ลง `known_hosts` ของ Jenkins ล่วงหน้า (pin) และตั้ง `StrictHostKeyChecking yes` ถ้าปลายทางไม่ใช่ `devtools` SSH จะปฏิเสธทันที |

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
| ④ `sh` step ของ Pipeline | Jenkins รันให้ | `jenkins` | เรียก `ssh devtools-gw ...` |
| ⑤ `bash -s` บน devtools | ปลายทางของ SSH จาก ④ | `root` | `git clone`, `docker build/run/push/pull` |

ค่าที่ผู้ใช้กรอก (parameter) เดินทางจาก Groovy → ④ → ข้าม SSH → ⑤ โดยที่ SSH ส่ง **ข้อความคำสั่ง** ให้ shell ปลายทางตีความอีกครั้ง ถ้าค่ามีอักขระอย่าง `;`, `$( )` หรือช่องว่าง shell ปลายทางจะรันมันเป็นคำสั่ง Jenkinsfile จึงตรวจ parameter ทุกตัวด้วย regular expression **บน Jenkins ใน stage Connect** และฟังก์ชัน `onDevtools` ยังตรวจซ้ำทุกค่าก่อนเปิด SSH ให้ผ่านได้เฉพาะอักขระที่ไม่มีความหมายพิเศษใน shell (พิสูจน์ในการทดลองที่ 10)

### 5. ซอร์สมาจาก Git — clone บน devtools ไม่ใช่บน Jenkins

stage **Clone** รัน `git clone` **บน devtools** (context ⑤) ซอร์สไม่ผ่าน Jenkins เลย และไม่พึ่งโฟลเดอร์ใดที่นักศึกษาเตรียมไว้ก่อน ซอร์สร้านอยู่ใน repository สาธารณะของรายวิชา:

![ซอร์สร้านบน GitHub](./images/lab3_github_01_source.png)

*ภาพที่ 2 (ภาพหน้าจอจริง) โฟลเดอร์ `catfood-shop` บน GitHub ที่ stage Clone ดึงมา*

![Dockerfile บน GitHub](./images/lab3_github_02_dockerfile.png)

*ภาพที่ 3 (ภาพหน้าจอจริง) `Dockerfile` ของร้าน — single-stage, `HEALTHCHECK` และ build-arg ข้อมูล build อยู่ท้ายไฟล์*

| parameter | ค่าเริ่มต้น | ความหมาย |
|---|---|---|
| `GIT_URL` | `https://github.com/Tuchsanai/DevTools.git` | repository สาธารณะของรายวิชา |
| `GIT_REF` | `main` | branch หรือ tag |
| `APP_SUBDIR` | `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop` | โฟลเดอร์ที่มี `Dockerfile` = build context |
| `APP_VERSION` | `1.0.0` | เวอร์ชัน `X.Y.Z` ที่ฝังเข้า image และแสดงบนหน้าเว็บ |
| `TAG_PREFIX` | `lab3` | คำนำหน้า tag บน Docker Hub → tag จริงคือ `<TAG_PREFIX>-<BUILD_NUMBER>` เช่น `lab3-1` |

repository ของรายวิชามีขนาดใหญ่ จึง clone แบบ `--depth 1 --filter=blob:none --sparse` แล้ว `git sparse-checkout set <APP_SUBDIR>` ดึงเฉพาะ commit ล่าสุดและเฉพาะไฟล์ในโฟลเดอร์ร้าน stage Build ฝัง commit ที่ clone มาเข้า image เป็น `GIT_COMMIT` หน้าร้านจึงบอกได้ว่ามาจาก commit ใด

> ถ้า fork repository ไปเป็นของตัวเอง ให้เปลี่ยน `GIT_URL` ตอน **Build with Parameters** ได้ทันที โดยไม่ต้องแก้ Jenkinsfile

### 6. Image, Tag และ Digest

| คำศัพท์ | ความหมาย |
|---|---|
| **Image** | แพ็กเกจอ่านอย่างเดียว ประกอบจาก **layer** ซ้อนกัน |
| **Registry / Repository / Tag** | ที่เก็บ image (Docker Hub) / ชุด image (`<DOCKER_USER>/catfood-shop`) / ป้ายที่ย้ายได้ (`lab3-1`, `lab3-2`) |
| **Digest** | `sha256:...` ที่คำนวณจากเนื้อหา image — เนื้อหาเดียวกันได้ digest เดียวกันเสมอ และ **เปลี่ยนไม่ได้** ต่างจาก tag |

stage Push จด digest ที่ Docker Hub ตอบกลับ แล้ว stage Pull ดึง `repository@sha256:...` **ตาม digest นั้น** ไม่ใช่ตาม tag และ Deploy ก็รันจากชื่อเดียวกันนี้ image ที่ขึ้นเว็บจึงเป็นตัวเดียวกับที่ push ทุกบิต แม้ภายหลังจะมีคนย้าย tag ไปที่อื่น

### 7. ลำดับ 8 stage และช่วงที่เว็บหยุดให้บริการ

![แผนภาพลำดับ 8 stage](./images/lab3_diagram_pipeline_flow.png)

*ภาพที่ 4 (แผนภาพประกอบ ไม่ใช่ภาพหน้าจอ) ทุก stage รันบน devtools ผ่าน SSH · Clean เกิดหลัง Push สำเร็จเท่านั้น และลบเฉพาะ container/image ของแล็บ · Pull ใช้ digest ที่ Push จดไว้*

**Clean มาก่อน Pull และเป็นที่เดียวที่ลบร้านเดิม** — เมื่อ Push สำเร็จแล้ว (image ใหม่อยู่บน Docker Hub ปลอดภัยแล้ว) Clean จะลบ container ทดสอบ, **ร้านเดิม `catfood-web`**, image สองชื่อของ build นี้ และซอร์สที่ clone เพื่อให้ Pull ต้องดึงจาก Docker Hub จริง ๆ และ Deploy เริ่มบนเครื่องที่ว่าง

- ลบเฉพาะ container ที่มี label `devtools.lab=lab3` (และ `devtools.role=app` สำหรับร้าน) ถ้ามี container ชื่อ `catfood-web` ที่ **ไม่ได้** สร้างโดยแล็บนี้ Clean จะหยุด build โดยไม่ลบอะไร
- ไม่แตะ `jenkins`, network `cicd-net`, volume `jenkins_home` และ container/image อื่นบนเครื่อง
- ถ้า build ล้ม **ก่อน** Clean (เช่น parameter ผิด, clone ไม่ได้, test ไม่ผ่าน, push ไม่ได้) ร้านเดิมยังเปิดอยู่ตามเดิม

> ⏸️ **Downtime ที่ต้องรู้:** ตั้งแต่ Clean ลบร้านเดิมจนถึง Deploy รายงาน `healthy` เว็บที่ `localhost:3000` จะเปิดไม่ได้ ในรอบทดสอบช่วงนี้ใช้ราว 6 วินาที (Clean + Pull + Deploy ของ build #2) ถ้า Pull ช้าหรือ Docker Hub มีปัญหาจะนานกว่านี้ และถ้า Pull หรือ Deploy ล้ม ร้านจะยังปิดอยู่จนกว่าจะมี build ที่สำเร็จ (แล็บนี้ไม่มีระบบ rollback อัตโนมัติ — ให้แก้สาเหตุแล้วกด Build ใหม่)

---

## 🎯 Learning Objectives — ผลลัพธ์การเรียนรู้

เมื่อจบแล็บนี้ นักศึกษาจะสามารถ

1. อธิบาย Docker สองชั้นของแล็บ และเหตุผลที่ `jenkins` resolve ชื่อ `devtools` ไม่ได้
2. หา gateway ของ `cicd-net` จากเครื่องจริง แล้วตั้ง SSH Host alias ที่ pin host key ได้ โดยไม่เขียน IP ตายตัวและไม่สร้าง Jenkins ใหม่
3. เตรียม SSH key และ Docker Hub token ใน Jenkins Credentials และอธิบายสิทธิ์ที่ key ชุดนั้นได้รับ
4. อ่าน Jenkinsfile แล้วบอกได้ว่าแต่ละบรรทัดทำงานใน context ใด และตัวแปรถูกแทนค่าที่ฝั่งใด
5. รัน Pipeline 8 stage แล้วสืบย้อนจากหน้าเว็บ → container → digest → build → commit ได้
6. อธิบายว่าทำไม Clean ต้องมาก่อน Pull และเว็บหยุดให้บริการช่วงไหน
7. แสดงให้เห็นว่าการตรวจ parameter หยุดค่าอันตรายก่อนข้าม SSH และ build ที่ล้มก่อน Clean ไม่กระทบร้านเดิม

## 🗺️ แผนที่การทดลอง

| ส่วน | การทดลอง | ทำอะไร | หลักฐานที่ต้องได้ |
|---|---|---|---|
| 0. เตรียมเครื่อง | — | เริ่มใหม่ หรือทำต่อจาก LAB 1–2 · ตรวจ plugin · เตรียม Docker Hub | `jenkins` `Up`, มี `cicd-net` และ `jenkins_home` |
| A. สำรวจ | 1–2 | Jenkins ไม่มี Docker · ชื่อ `devtools` resolve ไม่ได้ | `exit=127` · `devtools exit=2` |
| B. เส้นทาง SSH | 3–5 | หา gateway · ตั้ง `devtools-gw` · สร้าง key | `Permission denied (publickey,password)` ก่อนมี key · `key OK: root@...` |
| C. Credentials | 6 | เก็บ `devtools-ssh` และ `dockerhub` | หน้า Credentials มี 2 รายการ |
| D. Pipeline | 7–8 | สร้าง job แล้ว **Build Now** | build #1 `SUCCESS` ครบ 8 stage · ร้านขึ้นที่ `localhost:3000` |
| E. เวอร์ชันใหม่ | 9 | Build with Parameters `1.1.0` | Clean ลบร้าน build #1 · Pull/Deploy digest เดียวกับที่ push |
| F. ค่าผิด / branch ผิด | 10 | กรอก parameter ผิดรูปแบบ และ branch ที่ไม่มี | ล้มที่ Connect / Clone · ร้านยังเป็น build #2 |

## 📂 ไฟล์ในโฟลเดอร์นี้

| ไฟล์ | หน้าที่ |
|---|---|
| `Jenkinsfile` | Pipeline 8 stage: Connect → Clone → Build → Test → Push → Clean → Pull → Deploy (เนื้อหาเดียวกับหัวข้อ “Jenkinsfile ฉบับสมบูรณ์” ด้านล่าง) |
| `catfood-shop/` | ซอร์สร้าน Meow Mart (Next.js 16 + React 19) ซึ่ง stage Clone ดึงจาก GitHub — ไม่ต้อง copy เอง |
| `catfood-shop/Dockerfile` | Dockerfile แบบ single-stage + `HEALTHCHECK` รับ `APP_VERSION`, `BUILD_NUMBER`, `GIT_COMMIT`, `BUILD_TIME` |
| `images/` | แผนภาพประกอบ 2 ภาพ (`lab3_diagram_*`) และภาพหน้าจอจริงจากรอบทดสอบ |

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

<!-- lab3-test:jenkins-launch -->
```bash
docker network create cicd-net
docker run -d --name jenkins --network cicd-net --restart unless-stopped \
  -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21
```

แล้วทำ **การทดลองที่ 3–4 ของ [LAB 1](../001_LAB_Jenkins_On_Docker/README.md)** ให้เสร็จ: เปิด `http://localhost:8080` ปลดล็อกด้วย `docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword` เลือก **Install suggested plugins** และสร้างผู้ดูแล `admin` / `admin2569`

![หน้า Unlock Jenkins](./images/lab3_jenkins_01_unlock.png)

*ภาพที่ 5 (ภาพหน้าจอจริง จากรอบทดลองแยกอีกรอบในวันเดียวกัน) หน้า Unlock Jenkins ของการติดตั้งครั้งแรก*

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
```bash
docker ps --filter name=^jenkins$ --format '{{.Names}}  {{.Image}}  {{.Status}}'
docker network inspect cicd-net --format '{{.Name}} {{range .IPAM.Config}}{{.Subnet}} gw {{.Gateway}}{{end}}'
docker volume ls --filter name=jenkins_home
```

✅ **ผลจากรอบทดสอบ** (subnet และเวลาของแต่ละเครื่องอาจต่างกัน):

```text
jenkins  jenkins/jenkins:lts-jdk21  Up 8 seconds
cicd-net 172.19.0.0/16 gw 172.19.0.1
DRIVER    VOLUME NAME
local     jenkins_home
```

> ถ้าไม่มีแถว `jenkins` หรือ network `cicd-net` แปลว่ายังไม่ได้ทำ LAB 1 ให้กลับไปทำทาง A · ถ้าขึ้น `Cannot connect to the Docker daemon` ดูแถว `docker.pid` ในแก้ปัญหาของ LAB 1

### ตรวจ login และ plugin ของ Jenkins

เปิด `http://localhost:8080` แล้ว login ด้วยผู้ดูแลที่สร้างไว้

![หน้า Sign in ของ Jenkins](./images/lab3_jenkins_02_signin.png)

*ภาพที่ 6 (ภาพหน้าจอจริง) หน้า Sign in*

![Dashboard หลัง login](./images/lab3_jenkins_03_dashboard.png)

*ภาพที่ 7 (ภาพหน้าจอจริง) Dashboard หลัง login*

แล็บนี้ใช้ plugin ที่มากับชุด **Install suggested plugins** อยู่แล้ว ไม่ต้องติดตั้งเพิ่ม ตรวจที่ **Manage Jenkins → Plugins → Installed plugins** ว่ามีครบ:

| plugin | ใช้ทำอะไร |
|---|---|
| **Pipeline** (`workflow-aggregator`) | job ชนิด Pipeline และ Declarative syntax |
| **Credentials Binding** | `withCredentials([...])` |
| **SSH Credentials** | ชนิด credential **SSH Username with private key** และ `sshUserPrivateKey(...)` |
| **Pipeline Graph View** | หน้า Stages แสดง 8 stage เป็นกราฟ (ไม่บังคับ แต่ช่วยอ่านผล) |

![รายการ plugin ที่ติดตั้ง](./images/lab3_jenkins_09_plugins.png)

*ภาพที่ 8 (ภาพหน้าจอจริง) plugin กลุ่ม Pipeline ที่ติดตั้งจากชุด suggested plugins*

> ถ้าตอนทำ LAB 1 เลือก **Select plugins to install** แล้วตัดบางตัวออก ให้ติดตั้งตัวที่ขาดจาก **Available plugins** แล้ว restart Jenkins

### Prerequisite Docker Hub

สมัครบัญชีและยืนยันอีเมล สร้าง **Personal Access Token สิทธิ์ Read & Write** (Account settings → Personal access tokens) เก็บ token ไว้สำหรับการทดลองที่ 6 เท่านั้น แนะนำให้สร้าง repository `catfood-shop` แบบ **Public** เพื่อเปิดดูหน้า Tags ได้โดยไม่ต้อง login (Pipeline login ทั้งตอน push และ pull จึงใช้กับ Private ได้เช่นกัน)

![repository catfood-shop บน Docker Hub](./images/lab3_hub_01_logged_in.png)

*ภาพที่ 9 (ภาพหน้าจอจริง) หน้า Repositories บน Docker Hub หลัง login มี `catfood-shop` แบบ Public — ของนักศึกษาจะเป็น `<DOCKER_USER>/catfood-shop`*

---

## A. สำรวจสภาพแวดล้อม

### การทดลองที่ 1 — ข้างใน Jenkins ไม่มี Docker แต่มี SSH client

**ทำอะไร:** ส่องเข้าไปใน container `jenkins` ว่ามีเครื่องมืออะไร

**ทำไม:** เพื่อยืนยันว่าทางเดียวที่ Jenkins จะสั่ง Docker ได้คือส่งคำสั่งไปให้เครื่องอื่น

ใน **② shell ของ devtools**:

<!-- lab3-test:exp1-no-docker -->
```bash
docker exec jenkins sh -c 'docker version'; echo "exit=$?"
docker exec jenkins sh -c 'id; echo "HOME=$HOME"; ssh -V'
```

✅ **ผลจากรอบทดสอบ:**

```text
sh: 1: docker: not found
exit=127
uid=1000(jenkins) gid=1000(jenkins) groups=1000(jenkins)
HOME=/var/jenkins_home
OpenSSH_10.0p2 Debian-7+deb13u4, OpenSSL 3.5.7 9 Jun 2026
```

🔍 **ตีความ:** exit code `127` = หาโปรแกรม `docker` ไม่เจอ Jenkins รันเป็นผู้ใช้ `jenkins` ที่มี home อยู่ที่ `/var/jenkins_home` (อยู่ใน volume) และมี OpenSSH client มาให้แล้ว — ไฟล์ `~/.ssh/config` ของผู้ใช้นี้จึงอยู่ใน volume `jenkins_home` ด้วย ซึ่งเป็นกุญแจของการทดลองที่ 4

### การทดลองที่ 2 — ชื่อ `devtools` ไม่มีความหมายใน network ของ Jenkins

**ทำอะไร:** ให้ `jenkins` ลอง resolve ชื่อ `devtools` เทียบกับชื่อตัวเอง

**ทำไม:** เพื่อเห็นด้วยตาว่าทำไมเขียน `root@devtools` ใน Jenkinsfile ตรง ๆ ไม่ได้ (ทฤษฎีข้อ 2)

<!-- lab3-test:exp2-dns -->
```bash
docker exec jenkins getent hosts devtools; echo "devtools exit=$?"
docker exec jenkins getent hosts jenkins; echo "jenkins exit=$?"
docker exec jenkins cat /etc/resolv.conf | grep nameserver
hostname
```

✅ **ผลจากรอบทดสอบ:**

```text
devtools exit=2
172.19.0.2      jenkins
jenkins exit=0
nameserver 127.0.0.11
79aca8352ad1
```

🔍 **ตีความ:** `getent` หา `devtools` ไม่เจอ (exit `2`) แต่หา `jenkins` เจอ เพราะ DNS `127.0.0.11` ของ Docker ข้างใน devtools รู้จักเฉพาะ container บน `cicd-net` ของตัวเอง บรรทัดสุดท้ายคือ hostname ของ devtools ซึ่งเป็น container ID ไม่ใช่ `devtools` — ชื่อ `devtools` มีอยู่เฉพาะบน Docker ของเครื่องเรา

---

## B. สร้างเส้นทาง SSH จาก Jenkins กลับมาที่ devtools

### การทดลองที่ 3 — หา gateway ของ `cicd-net`

**ทำอะไร:** อ่าน subnet และ gateway ของ `cicd-net` IP ของ `jenkins` และ IP ทั้งหมดของ devtools

<!-- lab3-test:exp3-gateway -->
```bash
docker network inspect cicd-net --format '{{range .IPAM.Config}}subnet={{.Subnet}} gateway={{.Gateway}}{{end}}'
docker inspect jenkins --format '{{range $n, $c := .NetworkSettings.Networks}}jenkins: {{$n}} {{$c.IPAddress}}{{end}}'
hostname -I
```

✅ **ผลจากรอบทดสอบ** (ตัวเลขของแต่ละเครื่องอาจต่างกัน — ใช้ค่าของเครื่องตนเอง):

```text
subnet=172.19.0.0/16 gateway=172.19.0.1
jenkins: cicd-net 172.19.0.2
172.17.0.2 172.18.0.1 172.19.0.1
```

🔍 **ตีความ:** gateway ของ `cicd-net` ปรากฏอยู่ในรายการ IP ของ devtools (`hostname -I`) จริง และ `jenkins` อยู่ subnet เดียวกัน → packet จาก `jenkins` ไปที่ gateway ถึง devtools โดยตรง นี่คือปลายทาง SSH ของเรา

### การทดลองที่ 4 — ตั้ง SSH Host alias `devtools-gw` แบบถาวรใน `jenkins_home`

**ทำอะไร:** เขียน `~/.ssh/config` และ `~/.ssh/known_hosts` ให้ผู้ใช้ `jenkins` จากค่าที่อ่านได้จริง

**ทำไม:** Jenkinsfile จะอ้างเพียงชื่อ `devtools-gw` ส่วน IP จริงอยู่ในไฟล์ config ที่เก็บใน volume — เปลี่ยนเครื่องก็แค่รันบล็อกนี้ใหม่

<!-- lab3-test:exp4-ssh-alias -->
```bash
GW=$(docker network inspect cicd-net --format '{{range .IPAM.Config}}{{println .Gateway}}{{end}}' | grep -E '^[0-9]+(\.[0-9]+){3}$' | head -n 1)
hostname -I | tr ' ' '\n' | grep -qFx "$GW" && echo "gateway ของ cicd-net = $GW (เป็น IP ของ devtools เอง)" || { echo "หา gateway ไม่ได้ หยุดก่อน"; false; }
docker exec -i -u jenkins jenkins sh -c 'umask 077; mkdir -p ~/.ssh; cat > ~/.ssh/config' <<EOF
Host devtools-gw
  HostName $GW
  Port 22
  User root
  HostKeyAlias devtools-gw
  StrictHostKeyChecking yes
  IdentitiesOnly yes
  BatchMode yes
  ConnectTimeout 10
  LogLevel ERROR
EOF
echo "devtools-gw $(cut -d' ' -f1,2 /etc/ssh/ssh_host_ed25519_key.pub)" |
  docker exec -i -u jenkins jenkins sh -c 'umask 077; cat > ~/.ssh/known_hosts'
docker exec jenkins ls -la /var/jenkins_home/.ssh
```

📝 **คำอธิบาย:**

- บรรทัดแรกอ่าน gateway จาก `docker network inspect` แล้วกรองเอาเฉพาะรูปแบบ IPv4 บรรทัดที่สองตรวจว่า IP นั้นเป็นของ devtools จริง ถ้าไม่ใช่จะหยุด ไม่เขียนไฟล์ผิด ๆ
- heredoc `<<EOF` (ไม่มีอัญประกาศ) ตั้งใจให้ shell ของ devtools แทนค่า `$GW` ก่อนส่งเนื้อหาเข้า `docker exec -i ... cat > ~/.ssh/config` ซึ่งรันเป็นผู้ใช้ `jenkins` (`-u jenkins`) ไฟล์จึงเป็นของ `jenkins` และ `umask 077` ทำให้ได้สิทธิ์ `600` ตามที่ OpenSSH ต้องการ
- `HostKeyAlias devtools-gw` + บรรทัด `known_hosts` ที่อ่านจาก `/etc/ssh/ssh_host_ed25519_key.pub` ของ devtools โดยตรง ทำให้ Jenkins รู้จัก host key ล่วงหน้า (pin) **โดยไม่ต้องเชื่อเครือข่ายครั้งแรก** และ `StrictHostKeyChecking yes` ปฏิเสธเครื่องที่ key ไม่ตรง
- `BatchMode yes` ห้ามถามรหัสผ่าน (Pipeline ไม่มีคนพิมพ์) `IdentitiesOnly yes` ใช้เฉพาะ key ที่ส่งมาด้วย `-i` และ `ConnectTimeout 10` ทำให้ล้มเร็วถ้าเส้นทางใช้ไม่ได้

✅ **ผลจากรอบทดสอบ:**

```text
gateway ของ cicd-net = 172.19.0.1 (เป็น IP ของ devtools เอง)
total 16
drwx------  2 jenkins jenkins 4096 Sep 26 06:46 .
drwxr-xr-x 13 jenkins jenkins 4096 Sep 26 06:46 ..
-rw-------  1 jenkins jenkins  190 Sep 26 06:46 config
-rw-------  1 jenkins jenkins   93 Sep 26 06:46 known_hosts
```

ทดสอบการเชื่อมต่อจากข้างใน `jenkins` (ยังไม่มี key — ตั้งใจให้ถูกปฏิเสธ):

<!-- lab3-test:exp4-test -->
```bash
docker exec jenkins ssh -G devtools-gw | grep -E '^(hostname|port|user|hostkeyalias|stricthostkeychecking) '
docker exec jenkins ssh devtools-gw true; echo "exit=$?"
```

✅ **ผลจากรอบทดสอบ:**

```text
user root
hostname 172.19.0.1
port 22
stricthostkeychecking true
hostkeyalias devtools-gw
root@172.19.0.1: Permission denied (publickey,password).
exit=255
```

🔍 **ตีความ:** `ssh -G` แสดงค่าที่ SSH จะใช้จริงสำหรับ `devtools-gw` ส่วน `Permission denied (publickey,password)` เป็นผลที่ **ถูกต้อง** — แปลว่าเส้นทางถึง `sshd` ของ devtools แล้ว และ host key ผ่านการตรวจแล้ว (ถ้า key ไม่ตรงจะเห็น `Host key verification failed` แทน) ที่ขาดอยู่มีเพียง credential

> ✅ ไม่ได้ลบหรือสร้าง `jenkins` ใหม่เลย · ถ้าภายหลังลบ network `cicd-net` แล้วสร้างใหม่ gateway อาจเปลี่ยน ให้รันบล็อกนี้ซ้ำ

### การทดลองที่ 5 — สร้าง SSH key ให้ Jenkins ใช้เข้า devtools

ใน **② shell ของ devtools**:

<!-- lab3-test:exp5-key -->
```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
[ -f ~/.ssh/jenkins_devtools ] || ssh-keygen -q -t ed25519 -N '' -C jenkins-to-devtools -f ~/.ssh/jenkins_devtools
touch ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
grep -qxF "$(cat ~/.ssh/jenkins_devtools.pub)" ~/.ssh/authorized_keys || cat ~/.ssh/jenkins_devtools.pub >> ~/.ssh/authorized_keys
ssh-keygen -lf ~/.ssh/jenkins_devtools.pub
grep -c jenkins-to-devtools ~/.ssh/authorized_keys
```

📝 **คำอธิบาย:** สร้าง key ed25519 เฉพาะเมื่อยังไม่มี (รันซ้ำได้ ไม่ทับ key เดิม) `-N ''` = ไม่มี passphrase เพื่อให้ Jenkins ใช้ได้โดยไม่มีคนพิมพ์ แล้วต่อ public key ท้าย `authorized_keys` เฉพาะเมื่อยังไม่มีบรรทัดนี้ `ssh-keygen -l` แสดง fingerprint และบรรทัดสุดท้ายนับว่ามี key นี้ใน `authorized_keys` กี่บรรทัด

✅ **ผลจากรอบทดสอบ** (fingerprint ของแต่ละเครื่องต่างกัน บรรทัดสุดท้ายต้องเป็น `1`):

```text
256 SHA256:I29vIKioU99wVOzS6JKtNZQrfN6qcbDAOCOOwzm9rWA jenkins-to-devtools (ED25519)
1
```

ลอง key กับ sshd ของ devtools ก่อนนำไปใส่ Jenkins:

<!-- lab3-test:exp5-keytest -->
```bash
ssh -i ~/.ssh/jenkins_devtools -o BatchMode=yes -o IdentitiesOnly=yes \
  -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  root@127.0.0.1 'echo "key OK: $(whoami)@$(hostname)"'
```

✅ **ผลจากรอบทดสอบ:**

```text
key OK: root@79aca8352ad1
```

> 📝 การทดสอบนี้ต่อเข้า `127.0.0.1` ของ devtools เอง จึงปิดการตรวจ host key เฉพาะคำสั่งนี้ ฝั่ง Jenkins ยังตรวจเข้มตามการทดลองที่ 4

---

## C. Credentials

### การทดลองที่ 6 — เก็บ SSH key และ Docker Hub token ใน Jenkins Credentials

**ทำไม:** Pipeline ต้องใช้ความลับสองชิ้นโดยไม่เขียนลงโค้ด แยก `devtools-ssh` (ทุก stage) ออกจาก `dockerhub` (เฉพาะ stage ที่ต้องรู้บัญชี) เพื่อเปลี่ยนหรือเพิกถอนทีละชิ้นได้

1. **Manage Jenkins → Credentials** → **System → Global credentials (unrestricted)** → **Add Credentials**

**(ก) SSH key สำหรับเข้า devtools**

2. เลือกชนิด **SSH Username with private key**
3. แสดง private key ใน **② shell ของ devtools** แล้วคัดลอก **ทั้งไฟล์** รวมบรรทัด `-----BEGIN OPENSSH PRIVATE KEY-----` และ `-----END OPENSSH PRIVATE KEY-----`

```bash
cat ~/.ssh/jenkins_devtools
```

4. กรอก **ID** = `devtools-ssh`, **Description** = `SSH key: Jenkins to devtools`, **Username** = `root` เลือก **Private Key → Enter directly** วางเนื้อหาที่คัดลอกมา ปล่อย **Passphrase** ว่าง → **Create**

![ค่าใน credential devtools-ssh](./images/lab3_jenkins_05_ssh_credential.png)

*ภาพที่ 10 (ภาพหน้าจอจริง) หน้าต่าง **Update credential** ของ `devtools-ssh` ที่บันทึกแล้ว — ใช้ตรวจค่าทุกช่องให้ตรงกับที่กรอกตอนสร้าง Jenkins ซ่อน key เป็น `Concealed for Confidentiality`*

**(ข) Docker Hub token**

5. **Add Credentials** อีกครั้ง → **Username with password** → Username = `<DOCKER_USER>` (ตัวพิมพ์เล็ก), Password = `<DOCKER_TOKEN>`, ID = `dockerhub`, Description = `Docker Hub access token` → **Create**

![ค่าใน credential dockerhub](./images/lab3_jenkins_06_dockerhub_credential.png)

*ภาพที่ 11 (ภาพหน้าจอจริง) หน้าต่าง **Update credential** ของ `dockerhub` ที่บันทึกแล้ว — token แสดงเป็น `Concealed` ID `dockerhub` คือชื่อที่ Jenkinsfile อ้างถึง*

✅ **สิ่งที่ต้องเห็น:** หน้า Global credentials มีสองรายการ `devtools-ssh` และ `dockerhub` แสดงเพียง ID และคำอธิบาย ไม่แสดง private key หรือ token

![รายการ credential สองตัว](./images/lab3_jenkins_04_credentials.png)

*ภาพที่ 12 (ภาพหน้าจอจริง) Global credentials มี `devtools-ssh` และ `dockerhub`*

> ⚠️ private key และ token วางได้ที่ Jenkins Credentials เท่านั้น ห้ามวางในแชต เอกสาร หรือ commit ลง Git · Jenkinsfile ตรวจ username ของ `dockerhub` ว่ามีเฉพาะ `a-z0-9` ตามกติกาชื่อบัญชี Docker Hub ก่อนนำไปประกอบชื่อ image

---

## D. Pipeline

### อ่าน Jenkinsfile ก่อนรัน

ทุก stage ที่ทำงานบน devtools เรียกฟังก์ชันเดียวกันคือ `onDevtools(ตัวแปร, สคริปต์)` ดู stage **Clone** เป็นตัวอย่าง:

```groovy
def commit = onDevtools([WORK_DIR: env.WORK_DIR, GIT_URL: params.GIT_URL,
                         GIT_REF: params.GIT_REF, APP_SUBDIR: params.APP_SUBDIR], '''
rm -rf "$WORK_DIR"
git clone --quiet --depth 1 --filter=blob:none --sparse --branch "$GIT_REF" -- "$GIT_URL" "$WORK_DIR" >&2
...
git rev-parse --short=12 HEAD
''', true).trim()
```

และตัวฟังก์ชัน:

```groovy
writeFile file: 'remote.sh', text: "set -euo pipefail\n${body}\n"
withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY')]) {
  out = sh(script: "ssh -i \"\$SSH_KEY\" devtools-gw \"${assigns.join(' ')} bash -s\" < remote.sh",
           returnStdout: capture)
}
```

| ส่วน | ทำงานที่ | อธิบาย |
|---|---|---|
| `'''...'''` (สคริปต์) | Groovy | อัญประกาศเดี่ยวสามตัว Groovy **ไม่แทนค่า** `$` สคริปต์ถูกเขียนเป็นไฟล์ `remote.sh` ใน workspace ของ Jenkins ทุกตัวอักษร |
| `[WORK_DIR: ..., GIT_URL: ...]` | Groovy | ทุกค่าต้องผ่าน regex `[A-Za-z0-9._:/@=+-]*` แล้วถูกครอบด้วย `'...'` เป็น `GIT_URL='https://...'` ถ้ามีอักขระอื่น build หยุดก่อนเปิด SSH |
| `withCredentials([sshUserPrivateKey(...)])` | Jenkins | เขียน private key เป็นไฟล์ชั่วคราว ใส่ path ใน `$SSH_KEY` และลบเมื่อจบบล็อก console แสดงเป็น `ssh -i ****` |
| `devtools-gw` | shell ④ | SSH อ่าน HostName/User/host key จาก `~/.ssh/config` (การทดลองที่ 4) |
| `"... bash -s" < remote.sh` | shell ④ → bash ⑤ | ตัวแปรกลายเป็น environment ของ `bash -s` บน devtools ส่วนเนื้อสคริปต์เดินทางทาง stdin ทุก `$` ในสคริปต์ถูกแทนค่าโดย bash ⑤ |
| `set -euo pipefail` | bash ⑤ | คำสั่งใดล้ม สคริปต์หยุดและ stage แดงทันที |
| `returnStdout: true` | Jenkins | เก็บ stdout (เช่น commit, digest) กลับมาเป็นค่าใน Groovy ส่วนข้อความอธิบายพิมพ์ลง stderr (`>&2`) จึงยังเห็นใน console |

| Stage | ทำงานที่ | ทำอะไร | ถ้าไม่ผ่าน |
|---|---|---|---|
| **1 Connect** | Jenkins แล้ว SSH | ตรวจ parameter 5 ตัวและ username Docker Hub · สร้าง tag `<TAG_PREFIX>-<BUILD_NUMBER>` · พิมพ์ว่า Jenkins ไม่มี docker · SSH ไปถามชื่อเครื่อง Docker และ git ของ devtools | ค่าผิดรูปแบบหรือ SSH ไม่ได้ → หยุดก่อนงานหนัก |
| **2 Clone** | devtools | sparse clone `GIT_URL`@`GIT_REF` ลง `/root/lab3-work/build-N` เก็บ commit 12 ตัว | branch ไม่มี หรือไม่มี `Dockerfile` ใน `APP_SUBDIR` → ล้ม |
| **3 Build** | devtools | `docker build --provenance=false` พร้อม label ของแล็บ และ build-arg เวอร์ชัน เลข build commit เวลา → `catfood-shop:build-N` | build ล้ม → ล้ม |
| **4 Test** | devtools | รัน `catfood-test-N` รอ `healthy` ≤ 30 วินาที อ่าน `/api/health` ต้องได้เวอร์ชันและ commit ที่สั่ง แล้วลบ container เสมอ (`trap`) | ไม่ผ่าน → ไม่ push |
| **5 Push** | devtools | login ด้วย token ทาง stdin ลงโฟลเดอร์ชั่วคราว `/tmp/lab3-docker-N` → tag และ push → จด **digest** | push ล้ม → ล้ม (ร้านเดิมยังอยู่) |
| **6 Clean** | devtools | ตรวจเจ้าของ `catfood-web` → ลบ container ทดสอบ, **ร้านเดิม**, image สองชื่อของ build นี้ และซอร์ส → ยืนยันว่าไม่เหลือ image ตาม digest | `catfood-web` ไม่ใช่ของแล็บ → หยุดโดยไม่ลบ |
| **7 Pull** | devtools | `docker pull <repo>@<digest>` จาก Docker Hub → ตรวจ RepoDigests → logout และลบโฟลเดอร์ login | ดึงไม่ได้ → ร้านยังปิด |
| **8 Deploy** | devtools | ตรวจว่าไม่มี `catfood-web` ค้างและ port 3000 ว่าง → `docker run` จาก `<repo>@<digest>` `-p 3000:3000 --restart unless-stopped` → รอ `healthy` → เทียบ version/build/commit | ไม่ตรง → ล้ม |

`disableConcurrentBuilds()` ห้ามสอง build ทำงานพร้อมกัน เพราะทุก build ใช้ชื่อ `catfood-web` และ port 3000 เดียวกัน · `post { unsuccessful }` ลบ container ทดสอบ, โฟลเดอร์ login และซอร์สของ build ที่ล้ม **แต่ไม่แตะร้าน** ส่วน `always { deleteDir() }` ลบ workspace ของ Jenkins (มีแค่ `remote.sh`)

### Jenkinsfile ฉบับสมบูรณ์

เนื้อหาเดียวกับไฟล์ [`Jenkinsfile`](./Jenkinsfile) ในโฟลเดอร์นี้ทุกตัวอักษร คัดลอกทั้งบล็อกไปวางใน Jenkins

```groovy
// LAB 3 — Jenkins เป็น "ผู้สั่ง" devtools เป็น "ผู้ทำ"
// jenkins เป็น image มาตรฐาน ไม่มี Docker CLI และไม่ได้ mount docker.sock
// ทุกงาน (git clone, docker build/run/push/pull) ถูกส่งผ่าน SSH ไปรันบน devtools port 22
// ปลายทาง devtools-gw เป็น Host alias ใน /var/jenkins_home/.ssh/config (ตั้งในขั้นที่ 4)

// ตรวจค่าก่อนส่งข้าม SSH: ต้องตรง regex ทั้งค่า มิฉะนั้นหยุด build ทันที
def requireMatch(String name, String value, String regex, String hint) {
  if (!(value ==~ regex)) {
    error("${name} ไม่ถูกต้อง: ${hint}")
  }
}

// รันสคริปต์ bash บน devtools ผ่าน SSH
// vars → ตัวแปรของสคริปต์ ทุกค่าถูกครอบด้วย ' ' และอนุญาตเฉพาะอักขระที่ไม่มีความหมายพิเศษใน shell
def onDevtools(Map vars, String body, boolean capture = false) {
  def keys = vars.keySet() as List
  def assigns = []
  for (int i = 0; i < keys.size(); i++) {
    def value = "${vars[keys[i]]}"
    if (!(value ==~ '[A-Za-z0-9._:/@=+-]*')) {
      error("ค่า ${keys[i]} มีอักขระที่ไม่อนุญาต")
    }
    assigns << "${keys[i]}='${value}'"
  }
  writeFile file: 'remote.sh', text: "set -euo pipefail\n${body}\n"
  def out = null
  withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY')]) {
    out = sh(script: "ssh -i \"\$SSH_KEY\" devtools-gw \"${assigns.join(' ')} bash -s\" < remote.sh",
             returnStdout: capture)
  }
  return out
}

pipeline {
  agent any

  options {
    disableConcurrentBuilds()   // ทุก build ใช้ container ชื่อ catfood-web และ port 3000 เดียวกัน
  }

  parameters {
    string(name: 'GIT_URL', defaultValue: 'https://github.com/Tuchsanai/DevTools.git',
           description: 'Git repository สาธารณะแบบ https:// ที่มีซอร์สร้าน')
    string(name: 'GIT_REF', defaultValue: 'main',
           description: 'branch หรือ tag ที่จะ clone')
    string(name: 'APP_SUBDIR', defaultValue: '04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop',
           description: 'โฟลเดอร์ใน repository ที่มี Dockerfile (path แบบ relative)')
    string(name: 'APP_VERSION', defaultValue: '1.0.0',
           description: 'เวอร์ชันรูปแบบ X.Y.Z ที่จะฝังเข้า image และแสดงบนหน้าเว็บ')
    string(name: 'TAG_PREFIX', defaultValue: 'lab3',
           description: 'คำนำหน้า tag บน Docker Hub → tag จริงคือ <TAG_PREFIX>-<BUILD_NUMBER>')
  }

  environment {
    APP_NAME    = 'catfood-shop'                              // ชื่อ image และ repository บน Docker Hub
    DEPLOY_NAME = 'catfood-web'                               // container ของร้านบน devtools (port 3000)
    TEST_NAME   = "catfood-test-${env.BUILD_NUMBER}"          // container ชั่วคราวของ stage Test
    WORK_DIR    = "/root/lab3-work/build-${env.BUILD_NUMBER}" // ที่ clone ซอร์สบน devtools (แยกตาม build)
    DOCKER_CFG  = "/tmp/lab3-docker-${env.BUILD_NUMBER}"      // ที่เก็บ login Docker Hub ชั่วคราว (Push → Pull)
    LOCAL_IMAGE = "catfood-shop:build-${env.BUILD_NUMBER}"    // ชื่อ image ในเครื่องก่อนติด tag ของ Hub
  }

  stages {
    stage('Connect') {
      steps {
        script {
          requireMatch('GIT_URL', params.GIT_URL,
                       'https://[A-Za-z0-9.-]+(/[A-Za-z0-9._-]+)+/?',
                       'ต้องเป็น https://host/path ไม่มีช่องว่าง ไม่มี user:password@')
          requireMatch('GIT_REF', params.GIT_REF,
                       '(?!-)(?!.*\\.\\.)[A-Za-z0-9._/-]{1,100}',
                       'ชื่อ branch/tag ใช้ได้เฉพาะ A-Z a-z 0-9 . _ / - และห้ามขึ้นต้นด้วย -')
          requireMatch('APP_SUBDIR', params.APP_SUBDIR,
                       '(?!-)(?!.*(^|/)\\.{1,2}(/|$))[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*',
                       'path แบบ relative ห้ามขึ้นต้นด้วย / หรือ - และห้ามมี . หรือ .. เป็นชื่อโฟลเดอร์')
          requireMatch('APP_VERSION', params.APP_VERSION,
                       '[0-9]+\\.[0-9]+\\.[0-9]+',
                       'ต้องเป็นรูปแบบ X.Y.Z เช่น 1.0.0')
          requireMatch('TAG_PREFIX', params.TAG_PREFIX,
                       '[a-z0-9][a-z0-9.-]{0,40}',
                       'ใช้ได้เฉพาะ a-z 0-9 . - ยาวไม่เกิน 41 ตัว')
          env.IMAGE_TAG = "${params.TAG_PREFIX}-${env.BUILD_NUMBER}"
          withCredentials([usernamePassword(credentialsId: 'dockerhub',
                           usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
            requireMatch('username ใน credential dockerhub', env.HUB_USER, '[a-z0-9]{4,30}',
                         'ต้องมีเฉพาะ a-z และ 0-9 ยาว 4–30 ตัว')
            env.HUB_REPO = "docker.io/${env.HUB_USER}/${env.APP_NAME}"
          }
        }
        sh '''
          echo "jenkins: $(hostname) docker CLI = $(command -v docker || echo none) docker.sock = $(test -S /var/run/docker.sock && echo yes || echo none)"
        '''
        script {
          onDevtools([:], '''
echo "devtools: $(hostname) user=$(whoami)"
docker version --format 'Docker Engine {{.Server.Version}}'
git --version
''')
          echo "จะ push ไปที่ ${env.HUB_REPO}:${env.IMAGE_TAG}"
        }
      }
    }

    stage('Clone') {
      steps {
        script {
          // สคริปต์พิมพ์รายละเอียดลง stderr (เห็นใน console) และพิมพ์ commit ลง stdout ให้ Jenkins เก็บไว้
          def commit = onDevtools([WORK_DIR: env.WORK_DIR, GIT_URL: params.GIT_URL,
                                   GIT_REF: params.GIT_REF, APP_SUBDIR: params.APP_SUBDIR], '''
rm -rf "$WORK_DIR"
mkdir -p "$(dirname "$WORK_DIR")"
git clone --quiet --depth 1 --filter=blob:none --sparse --branch "$GIT_REF" -- "$GIT_URL" "$WORK_DIR" >&2
cd "$WORK_DIR"
git sparse-checkout set "$APP_SUBDIR" >&2
test -f "$APP_SUBDIR/Dockerfile" || { echo "ไม่พบ $APP_SUBDIR/Dockerfile ใน $GIT_URL ($GIT_REF)" >&2; exit 1; }
{ echo "cloned to $(hostname):$WORK_DIR"
  git log -1 --format='commit %H%nsubject %s'
  ls "$APP_SUBDIR"; } >&2
git rev-parse --short=12 HEAD
''', true).trim()
          requireMatch('commit', commit, '[0-9a-f]{12}', 'อ่าน commit จาก git ไม่ได้')
          env.GIT_COMMIT_SHORT = commit
          echo "commit ที่จะ build: ${commit}"
        }
      }
    }

    stage('Build') {
      steps {
        script {
          onDevtools([SRC: "${env.WORK_DIR}/${params.APP_SUBDIR}", IMAGE: env.LOCAL_IMAGE,
                      VERSION: params.APP_VERSION, BUILD: env.BUILD_NUMBER, COMMIT: env.GIT_COMMIT_SHORT], '''
cd "$SRC"
docker build --provenance=false \\
  --label devtools.lab=lab3 --label devtools.build="$BUILD" \\
  --label org.opencontainers.image.revision="$COMMIT" \\
  --build-arg APP_VERSION="$VERSION" \\
  --build-arg BUILD_NUMBER="$BUILD" \\
  --build-arg GIT_COMMIT="$COMMIT" \\
  --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \\
  -t "$IMAGE" .
docker image ls "$IMAGE"
''')
        }
      }
    }

    stage('Test') {
      steps {
        script {
          onDevtools([IMAGE: env.LOCAL_IMAGE, NAME: env.TEST_NAME, BUILD: env.BUILD_NUMBER,
                      VERSION: params.APP_VERSION, COMMIT: env.GIT_COMMIT_SHORT], '''
docker rm -f "$NAME" >/dev/null 2>&1 || true
trap 'docker rm -f "$NAME" >/dev/null 2>&1 || true' EXIT
docker run -d --name "$NAME" --label devtools.lab=lab3 --label devtools.role=test \\
  --label devtools.build="$BUILD" "$IMAGE" >/dev/null
STATUS=starting
for i in $(seq 1 30); do
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' "$NAME")
  echo "health of $NAME: $STATUS"
  [ "$STATUS" = healthy ] && break
  sleep 1
done
[ "$STATUS" = healthy ]
HEALTH=$(docker exec "$NAME" wget -qO- http://127.0.0.1:3000/api/health)
echo "$HEALTH"
case "$HEALTH" in
  *"\\"version\\":\\"$VERSION\\""*"\\"commit\\":\\"$COMMIT\\""*) echo "test ผ่าน: image ตอบเวอร์ชัน $VERSION commit $COMMIT" ;;
  *) echo "test ไม่ผ่าน: ต้องได้ version $VERSION และ commit $COMMIT"; exit 1 ;;
esac
''')
        }
      }
    }

    stage('Push') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY'),
                         usernamePassword(credentialsId: 'dockerhub',
                           usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
          // token เดินทางทาง stdin ของ SSH เท่านั้น ไม่อยู่ใน command line และ console
          // login ถูกเก็บในโฟลเดอร์ชั่วคราว DOCKER_CFG ไม่ปนกับ ~/.docker ของ devtools
          sh '''set +x
            printf '%s\\n' "$HUB_TOKEN" | ssh -i "$SSH_KEY" devtools-gw \
              "umask 077; docker --config '$DOCKER_CFG' login docker.io -u '$HUB_USER' --password-stdin"
          '''
        }
        script {
          def digest = onDevtools([CFG: env.DOCKER_CFG, IMAGE: env.LOCAL_IMAGE,
                                   REMOTE: "${env.HUB_REPO}:${env.IMAGE_TAG}"], '''
docker tag "$IMAGE" "$REMOTE"
OUT=$(docker --config "$CFG" push "$REMOTE")
printf '%s\\n' "$OUT" | grep -v ': Waiting$' >&2   # ตัดบรรทัดรอคิวออก ให้เห็นผลของแต่ละ layer ชัด
printf '%s\\n' "$OUT" | sed -n 's/^.*: digest: \\(sha256:[0-9a-f]\\{64\\}\\) size: [0-9]*$/\\1/p'
''', true).trim()
          requireMatch('digest', digest, 'sha256:[0-9a-f]{64}', 'อ่าน digest จากผล docker push ไม่ได้')
          env.IMAGE_DIGEST = digest
          echo "บันทึก digest ที่ push แล้ว: ${env.HUB_REPO}@${digest}"
        }
      }
    }

    stage('Clean') {
      steps {
        script {
          // เคลียร์ devtools ก่อน Pull: container ทดสอบ, แอปเดิม catfood-web, image 2 ชื่อของ build นี้ และซอร์สที่ clone
          // ลบเฉพาะ container ที่มี label ของ LAB 3 ไม่แตะ jenkins, cicd-net, jenkins_home และของอื่น
          // ตั้งแต่ขั้นนี้จนจบ Deploy เว็บที่ port 3000 จะใช้ไม่ได้ชั่วคราว
          onDevtools([NAME: env.TEST_NAME, APP: env.DEPLOY_NAME, IMAGE: env.LOCAL_IMAGE, BUILD: env.BUILD_NUMBER,
                      REMOTE: "${env.HUB_REPO}:${env.IMAGE_TAG}", PUSHED: "${env.HUB_REPO}@${env.IMAGE_DIGEST}",
                      WORK_DIR: env.WORK_DIR], '''
if docker container inspect "$APP" >/dev/null 2>&1; then
  OWNER=$(docker inspect -f '{{index .Config.Labels "devtools.lab"}}/{{index .Config.Labels "devtools.role"}}' "$APP")
  [ "$OWNER" = lab3/app ] || { echo "พบ container $APP ที่ไม่ได้สร้างโดย LAB 3 (label=$OWNER) จึงไม่ลบ: ลบหรือเปลี่ยนชื่อเองก่อน"; exit 1; }
fi
docker ps -aq --filter label=devtools.lab=lab3 --filter label=devtools.role=test \\
  --filter label=devtools.build="$BUILD" | xargs -r docker rm -f
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker ps -a --filter "name=^$APP$" --filter label=devtools.lab=lab3 --filter label=devtools.role=app \\
  --format 'ลบแอปเดิม {{.Names}} ({{.Image}}, {{.Status}})'
docker ps -aq --filter "name=^$APP$" --filter label=devtools.lab=lab3 --filter label=devtools.role=app | xargs -r docker rm -f
docker image rm "$IMAGE" "$REMOTE"
rm -rf "$WORK_DIR"
if docker container inspect "$APP" >/dev/null 2>&1; then echo "ยังมี $APP ค้างอยู่"; exit 1; fi
for REF in "$REMOTE" "$PUSHED"; do
  if docker image inspect "$REF" >/dev/null 2>&1; then echo "ยังมี $REF ค้างอยู่"; exit 1; fi
done
echo "devtools ไม่มีแอปเดิมและไม่มี image ของ build $BUILD แล้ว: เว็บหยุดชั่วคราว และ stage ถัดไปต้องดึงจาก Docker Hub"
''')
        }
      }
    }

    stage('Pull') {
      steps {
        script {
          onDevtools([CFG: env.DOCKER_CFG, REF: "${env.HUB_REPO}@${env.IMAGE_DIGEST}",
                      DIGEST: env.IMAGE_DIGEST], '''
trap 'docker --config "$CFG" logout docker.io >/dev/null 2>&1 || true; rm -rf "$CFG"' EXIT
docker --config "$CFG" pull "$REF"
docker image inspect -f '{{range .RepoDigests}}{{println .}}{{end}}' "$REF" | grep -F "@$DIGEST"
echo "pull ตาม digest สำเร็จ: ได้ image ตัวเดียวกับที่ push"
''')
        }
      }
    }

    stage('Deploy') {
      steps {
        script {
          onDevtools([REF: "${env.HUB_REPO}@${env.IMAGE_DIGEST}", NAME: env.DEPLOY_NAME,
                      BUILD: env.BUILD_NUMBER, VERSION: params.APP_VERSION, COMMIT: env.GIT_COMMIT_SHORT], '''
if docker container inspect "$NAME" >/dev/null 2>&1; then echo "ยังมี $NAME อยู่ (ต้องถูกลบใน Clean)"; exit 1; fi
OTHERS=$(docker ps --filter publish=3000 --format '{{.Names}}')
[ -z "$OTHERS" ] || { echo "port 3000 ถูก container อื่นใช้อยู่: $OTHERS"; exit 1; }
docker run -d --name "$NAME" --restart unless-stopped -p 3000:3000 \\
  --label devtools.lab=lab3 --label devtools.role=app --label devtools.build="$BUILD" "$REF"
STATUS=starting
for i in $(seq 1 30); do
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' "$NAME")
  echo "health of $NAME: $STATUS"
  [ "$STATUS" = healthy ] && break
  sleep 1
done
[ "$STATUS" = healthy ]
docker ps --filter "name=^$NAME$" --format '{{.Names}}  {{.Status}}  {{.Ports}}'
docker inspect -f 'image: {{.Config.Image}}' "$NAME"
HEALTH=$(docker exec "$NAME" wget -qO- http://127.0.0.1:3000/api/health)
echo "$HEALTH"
case "$HEALTH" in
  *"\\"version\\":\\"$VERSION\\",\\"build\\":\\"$BUILD\\",\\"commit\\":\\"$COMMIT\\""*) ;;
  *) echo "เว็บไม่ได้ตอบ version $VERSION build $BUILD commit $COMMIT"; exit 1 ;;
esac
echo "เว็บตอบ version $VERSION build #$BUILD commit $COMMIT ตรงกับ Pipeline"
''')
        }
      }
    }
  }

  post {
    success {
      echo "เปิดร้านได้ที่ http://localhost:3000 (v${params.APP_VERSION} build #${env.BUILD_NUMBER} = ${env.HUB_REPO}@${env.IMAGE_DIGEST})"
    }
    unsuccessful {
      script {
        // build ล้มกลางทาง: ลบ container ทดสอบ, login ชั่วคราว และซอร์สที่ clone ของ build นี้
        // ถ้าเชื่อม devtools ไม่ได้ ให้ทำขั้นเก็บกวาดท้ายเอกสารด้วยมือ
        try {
          onDevtools([NAME: env.TEST_NAME, CFG: env.DOCKER_CFG, WORK_DIR: env.WORK_DIR], '''
docker rm -f "$NAME" >/dev/null 2>&1 || true
docker --config "$CFG" logout docker.io >/dev/null 2>&1 || true
rm -rf "$CFG" "$WORK_DIR"
echo "เก็บกวาดของ build ที่ล้มแล้ว: $NAME $CFG $WORK_DIR"
''')
        } catch (err) {
          echo 'เก็บกวาดบน devtools ไม่สำเร็จ (เช่น SSH ใช้ไม่ได้) ให้ลบเองตามหัวข้อเก็บกวาด'
        }
      }
    }
    always {
      deleteDir()   // ลบ workspace ของ job นี้บน Jenkins (มีแค่ remote.sh)
    }
  }
}
```

### การทดลองที่ 7 — สร้าง job `docker-build-push` แล้ววาง Jenkinsfile

1. Dashboard → **New Item** → ชื่อ `docker-build-push` → เลือก **Pipeline** → **OK**

![New Item ชนิด Pipeline](./images/lab3_jenkins_08_new_pipeline.png)

*ภาพที่ 13 (ภาพหน้าจอจริง) หน้า New Item ขณะเลือกชนิด **Pipeline** — ภาพนี้ถ่ายเพื่อแสดงหน้าจอเท่านั้น ในรอบทดสอบไม่ได้กด OK สร้าง job ซ้ำ*

2. หัวข้อ **Pipeline → Definition: Pipeline script** (ไม่ใช่ *Pipeline script from SCM*) วาง Jenkinsfile ฉบับสมบูรณ์ทั้งไฟล์ คง **Use Groovy Sandbox** ไว้ → **Save**

![ช่อง Pipeline script ที่วาง Jenkinsfile แล้ว](./images/lab3_jenkins_07_pipeline_config.png)

*ภาพที่ 14 (ภาพหน้าจอจริง) หน้า Configure ของ job ที่ Definition เป็น **Pipeline script** และมี Jenkinsfile ของแล็บนี้อยู่ในช่อง Script (ถ่ายจาก job ที่สร้างครั้งแรกก่อนปรับ stage Clean รอบสุดท้าย ส่วนต้นไฟล์ที่เห็น — คำอธิบายและฟังก์ชันช่วย — เหมือนฉบับสมบูรณ์)*

> 📝 job ที่เพิ่งสร้างยังไม่มีปุ่ม **Build with Parameters** เพราะ Jenkins จะรู้จัก `parameters { ... }` หลังรัน Jenkinsfile ครั้งแรก build แรกจึงกด **Build Now** ซึ่ง Declarative Pipeline ใส่ค่า default ให้ `params.*` ครบ (ตรวจแล้วในรอบทดสอบ: build แรกที่ไม่ส่ง parameter ได้ `params.GIT_URL` = `https://github.com/Tuchsanai/DevTools.git` และ `params.APP_VERSION` = `1.0.0`) tag แรกของนักศึกษาจึงเป็น `lab3-1`

### การทดลองที่ 8 — Build Now: ดูหลักฐานทีละ stage

กด **Build Now** แล้วเปิด build **#1** → **Console Output** (หรือหน้า Stages ของ Pipeline Graph View)

✅ **ผลจากรอบทดสอบ** (ตัดบรรทัด `[Pipeline]` ออก เลือกช่วงสำคัญของแต่ละ stage · รอบทดสอบใช้ `TAG_PREFIX` = `lab3-20260926r2` เพื่อไม่ชนกับ tag เดิมบน Docker Hub ของผู้ทดสอบ ของนักศึกษาจะเป็น `lab3-1` และ `<DOCKER_USER>` แทน `tuchsanai`):

**1 Connect** — Jenkins ไม่มี docker แต่สั่ง devtools ได้

```text
+ hostname
+ command -v docker
+ echo none
+ test -S /var/run/docker.sock
+ echo none
+ echo jenkins: cd3a16de4373 docker CLI = none docker.sock = none
jenkins: cd3a16de4373 docker CLI = none docker.sock = none
+ ssh -i **** devtools-gw  bash -s
devtools: 79aca8352ad1 user=root
Docker Engine 29.8.1
git version 2.55.0
จะ push ไปที่ docker.io/tuchsanai/catfood-shop:lab3-20260926r2-1
```

hostname `cd3a16de4373` คือ container `jenkins` ส่วน `79aca8352ad1` คือ hostname ของ devtools ตรงกับการทดลองที่ 2 และ `****` คือ path ของ key ที่ Jenkins ปิดบัง

**2 Clone** — ซอร์สมาจาก GitHub ลงบน devtools

```text
+ ssh -i **** devtools-gw WORK_DIR='/root/lab3-work/build-1' GIT_URL='https://github.com/Tuchsanai/DevTools.git' GIT_REF='main' APP_SUBDIR='04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop' bash -s
cloned to 79aca8352ad1:/root/lab3-work/build-1
commit 789e08d582e65e90dcfc5ca4e4612aa413b74ae3
subject 1
Dockerfile
app
data
next.config.mjs
package-lock.json
package.json
public
commit ที่จะ build: 789e08d582e6
```

commit ที่ได้คือ commit ล่าสุดของ `main` ในวันที่ทดสอบ ของนักศึกษาจะเป็น commit ล่าสุด ณ วันที่รัน

**3 Build** — image ถูกสร้างจากซอร์สที่เพิ่ง clone บนเครื่องที่ยังไม่มี cache ทุกขั้นจะรันจริง (ตัวอย่างจากการรันครั้งแรกบนเครื่องทดสอบในวันเดียวกัน):

```text
+ ssh -i **** devtools-gw SRC='/root/lab3-work/build-1/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop' IMAGE='catfood-shop:build-1' VERSION='1.0.0' BUILD='1' COMMIT='789e08d582e6' bash -s
#4 [1/6] FROM docker.io/library/node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402
#6 [2/6] WORKDIR /app
#7 [3/6] COPY package.json package-lock.json ./
#8 [4/6] RUN npm ci --no-audit --no-fund && npm cache clean --force
#8 9.860 added 24 packages in 10s
#9 [5/6] COPY . .
#10 [6/6] RUN npm run build && rm -rf .next/cache
#11 naming to docker.io/library/catfood-shop:build-1 done
IMAGE                  ID             DISK USAGE   CONTENT SIZE   EXTRA
catfood-shop:build-1   d52e068339ef        693MB          154MB
```

ส่วน build #1 ของรอบที่บันทึกไว้นี้ได้ `CACHED` ทุกขั้น เพราะเครื่องทดสอบเคย build ซอร์สเดียวกันมาก่อนหน้าไม่กี่นาที:

```text
+ ssh -i **** devtools-gw SRC='/root/lab3-work/build-1/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop' IMAGE='catfood-shop:build-1' VERSION='1.0.0' BUILD='1' COMMIT='789e08d582e6' bash -s
#4 [1/6] FROM docker.io/library/node:22-alpine@sha256:0a7108bf6c7bf5de370ffb1a3ed6be93d405b43ff159f681a8d18c0e2bc2e402
#6 [2/6] WORKDIR /app
#6 CACHED
#7 [5/6] COPY . .
#7 CACHED
#8 [3/6] COPY package.json package-lock.json ./
#8 CACHED
#9 [4/6] RUN npm ci --no-audit --no-fund && npm cache clean --force
#9 CACHED
#10 [6/6] RUN npm run build && rm -rf .next/cache
#10 CACHED
#11 naming to docker.io/library/catfood-shop:build-1 done
IMAGE                  ID             DISK USAGE   CONTENT SIZE   EXTRA
catfood-shop:build-1   8e69a91bd888        693MB          154MB
```

**4 Test** — แอปใน image ตอบ health และเวอร์ชัน/commit ถูกต้อง

```text
+ ssh -i **** devtools-gw IMAGE='catfood-shop:build-1' NAME='catfood-test-1' BUILD='1' VERSION='1.0.0' COMMIT='789e08d582e6' bash -s
health of catfood-test-1: starting
health of catfood-test-1: starting
health of catfood-test-1: healthy
{"status":"ok","app":"catfood-shop","version":"1.0.0","build":"1","commit":"789e08d582e6","builtAt":"2026-09-26T07:02:06Z","host":"48b8cd1f79c3"}
test ผ่าน: image ตอบเวอร์ชัน 1.0.0 commit 789e08d582e6
```

**5 Push** — login ด้วย token แล้ว push และจด digest (บนเครื่องที่ Docker Hub ยังไม่มี layer จะเห็น `Pushed` แทน `Layer already exists` เช่นรอบแรกในวันเดียวกันที่ push ใหม่ 5 layer)

```text
+ set +x
Login Succeeded

WARNING! Your credentials are stored unencrypted in '/tmp/lab3-docker-1/config.json'.
Configure a credential helper to remove this warning. See
https://docs.docker.com/go/credential-store/

+ ssh -i **** devtools-gw CFG='/tmp/lab3-docker-1' IMAGE='catfood-shop:build-1' REMOTE='docker.io/tuchsanai/catfood-shop:lab3-20260926r2-1' bash -s
The push refers to repository [docker.io/tuchsanai/catfood-shop]
e2de96513ba9: Layer already exists
e554276b05e6: Layer already exists
d39db1cf9caa: Layer already exists
f7f2d304681a: Layer already exists
b12d811778a6: Layer already exists
4b4f6f991e61: Layer already exists
26c43aab9fc0: Layer already exists
3bcff41df748: Layer already exists
5f421fe40249: Layer already exists
lab3-20260926r2-1: digest: sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621 size: 2006
บันทึก digest ที่ push แล้ว: docker.io/tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
```

`WARNING! Your credentials are stored unencrypted` หมายถึงไฟล์ login ในโฟลเดอร์ชั่วคราว `/tmp/lab3-docker-N` ซึ่ง stage Pull (หรือ `post` เมื่อ build ล้ม) logout และลบทิ้ง token ไม่เคยปรากฏใน console

**6 Clean** — เคลียร์ของ build นี้และร้านเดิมก่อน Pull

```text
+ ssh -i **** devtools-gw NAME='catfood-test-1' APP='catfood-web' IMAGE='catfood-shop:build-1' BUILD='1' REMOTE='docker.io/tuchsanai/catfood-shop:lab3-20260926r2-1' PUSHED='docker.io/tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621' WORK_DIR='/root/lab3-work/build-1' bash -s
ลบแอปเดิม catfood-web (d52e068339ef, Up 2 minutes (healthy))
2bca31b52544
Untagged: catfood-shop:build-1
Untagged: tuchsanai/catfood-shop:lab3-20260926r2-1
Deleted: sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
devtools ไม่มีแอปเดิมและไม่มี image ของ build 1 แล้ว: เว็บหยุดชั่วคราว และ stage ถัดไปต้องดึงจาก Docker Hub
```

บรรทัด `ลบแอปเดิม ...` ปรากฏเพราะเครื่องทดสอบมีร้านจากรอบก่อนหน้าอยู่แล้ว บรรทัดเลขฐาน 16 ถัดมาคือ ID ของ container ที่ถูกลบ ถ้าเป็นเครื่องใหม่ build #1 จะไม่มีสองบรรทัดนี้ `Untagged` / `Deleted` ยืนยันว่า image ของ build นี้ไม่อยู่ในเครื่องแล้ว

**7 Pull** — ดึงกลับจาก Docker Hub ตาม digest

```text
+ ssh -i **** devtools-gw CFG='/tmp/lab3-docker-1' REF='docker.io/tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621' DIGEST='sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621' bash -s
docker.io/tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621: Pulling from tuchsanai/catfood-shop
Digest: sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
Status: Downloaded newer image for tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
docker.io/tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
pull ตาม digest สำเร็จ: ได้ image ตัวเดียวกับที่ push
```

**8 Deploy** — ร้านเปิดที่ port 3000 จาก image ที่ pull มา

```text
+ ssh -i **** devtools-gw REF='docker.io/tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621' NAME='catfood-web' BUILD='1' VERSION='1.0.0' COMMIT='789e08d582e6' bash -s
8b03268293763cffa3d816c34c424ec6b392c9ffcf7819d96bf595d65e85358d
health of catfood-web: starting
health of catfood-web: starting
health of catfood-web: healthy
catfood-web  Up 2 seconds (healthy)  0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
image: docker.io/tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
{"status":"ok","app":"catfood-shop","version":"1.0.0","build":"1","commit":"789e08d582e6","builtAt":"2026-09-26T07:02:06Z","host":"8b0326829376"}
เว็บตอบ version 1.0.0 build #1 commit 789e08d582e6 ตรงกับ Pipeline
```

จากนั้นเปิด `http://localhost:3000` บนเครื่องของเรา chip บนแถบด้านบนต้องเป็น `v1.0.0 · build #1`

![หน้าร้าน v1.0.0 build #1](./images/lab3_app_01_version1.png)

*ภาพที่ 15 (ภาพหน้าจอจริง) หน้าร้านหลัง build #1 ของรอบทดสอบ chip บนแถบด้านบนแสดง `v1.0.0 · build #1`*

🔍 **สืบย้อน:** หน้าเว็บ → container `catfood-web` (`host` ใน `/api/health`) → `image: <repo>@sha256:...` ใน Deploy → digest ที่ Push จดไว้ → build #1 ของ Jenkins → `commit` จาก stage Clone

---

## E. ออกเวอร์ชันใหม่

### การทดลองที่ 9 — Build with Parameters `APP_VERSION=1.1.0`

1. เปิด job `docker-build-push` → **Build with Parameters**
2. เปลี่ยนเฉพาะ `APP_VERSION` เป็น `1.1.0` (ช่องอื่นคงค่าเดิม) → **Build**

![ฟอร์ม Build with Parameters](./images/lab3_jenkins_10_build_parameters.png)

*ภาพที่ 16 (ภาพหน้าจอจริง) ฟอร์ม Build with Parameters ที่ Jenkins สร้างจากบล็อก `parameters` หลัง build แรก กรอก `APP_VERSION` = `1.1.0` (รอบทดสอบกรอก `TAG_PREFIX` = `lab3-20260926r2` ด้วย ของนักศึกษาคง `lab3`) — ภาพนี้เป็นการเปิดฟอร์มดู build #2 จริงถูกสั่งด้วยค่าชุดเดียวกันผ่าน REST API ของ Jenkins*

ก่อน build #2 ร้านที่ให้บริการอยู่คือ build #1 ใน **② shell ของ devtools**:

```text
catfood-web 8e69a91bd888 Up 56 seconds (healthy) 0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp devtools.build=1,devtools.lab=lab3,devtools.role=app,org.opencontainers.image.revision=789e08d582e6
{"status":"ok","app":"catfood-shop","version":"1.0.0","build":"1","commit":"789e08d582e6","builtAt":"2026-09-26T07:02:06Z","host":"8b0326829376"}
```

✅ **ผลจากรอบทดสอบ** — stage Clean ของ build #2 ลบร้าน build #1 (`8e69a91bd888` คือ digest 12 ตัวแรกของ build #1):

```text
+ ssh -i **** devtools-gw NAME='catfood-test-2' APP='catfood-web' IMAGE='catfood-shop:build-2' BUILD='2' REMOTE='docker.io/tuchsanai/catfood-shop:lab3-20260926r2-2' PUSHED='docker.io/tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a' WORK_DIR='/root/lab3-work/build-2' bash -s
ลบแอปเดิม catfood-web (8e69a91bd888, Up About a minute (healthy))
8b0326829376
Untagged: catfood-shop:build-2
Untagged: tuchsanai/catfood-shop:lab3-20260926r2-2
Deleted: sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
devtools ไม่มีแอปเดิมและไม่มี image ของ build 2 แล้ว: เว็บหยุดชั่วคราว และ stage ถัดไปต้องดึงจาก Docker Hub
```

stage Pull และ Deploy ของ build #2 ใช้ digest เดียวกับที่ stage Push ของ build #2 จดไว้:

```text
lab3-20260926r2-2: digest: sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a size: 2006
บันทึก digest ที่ push แล้ว: docker.io/tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
```

```text
+ ssh -i **** devtools-gw CFG='/tmp/lab3-docker-2' REF='docker.io/tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a' DIGEST='sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a' bash -s
docker.io/tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a: Pulling from tuchsanai/catfood-shop
Digest: sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
Status: Downloaded newer image for tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
docker.io/tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
pull ตาม digest สำเร็จ: ได้ image ตัวเดียวกับที่ push
```

```text
+ ssh -i **** devtools-gw REF='docker.io/tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a' NAME='catfood-web' BUILD='2' VERSION='1.1.0' COMMIT='789e08d582e6' bash -s
fa874f49da640d0fc548f66ec749094cfe85be5f3a4a19fe93cfcdda8942a341
health of catfood-web: starting
health of catfood-web: starting
health of catfood-web: healthy
catfood-web  Up 2 seconds (healthy)  0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
image: docker.io/tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
{"status":"ok","app":"catfood-shop","version":"1.1.0","build":"2","commit":"789e08d582e6","builtAt":"2026-09-26T07:04:00Z","host":"fa874f49da64"}
เว็บตอบ version 1.1.0 build #2 commit 789e08d582e6 ตรงกับ Pipeline
```

![build #2 สำเร็จครบ 8 stage](./images/lab3_jenkins_11_build2_success.png)

*ภาพที่ 17 (ภาพหน้าจอจริง) build #2 สีเขียวครบ Connect → Deploy พร้อมข้อความสรุปท้าย build*

#### หน้า Stages ของ build #2 ทีละ stage

เปิด `http://localhost:8080/job/docker-build-push/2/stages/` แล้วคลิกทีละ stage ทางซ้าย ภาพทั้ง 8 ภาพด้านล่างเป็นภาพหน้าจอจริงของ build #2 (v1.1.0, tag `lab3-20260926r2-2`)

![stage Connect](./images/lab3_stage_01_connect.png)

*ภาพที่ 18 **Connect** — `docker CLI = none docker.sock = none` บน Jenkins แล้ว SSH ไปถาม Docker/git ของ devtools และประกาศปลายทาง push*

![stage Clone](./images/lab3_stage_02_clone.png)

*ภาพที่ 19 **Clone** — sparse clone ลง `/root/lab3-work/build-2` บน devtools แสดง commit และไฟล์ในโฟลเดอร์ร้าน*

![stage Build](./images/lab3_stage_03_build.png)

*ภาพที่ 20 **Build** — `docker build` บน devtools ทุกขั้นที่สร้างไฟล์เป็น `CACHED` ได้ `catfood-shop:build-2`*

![stage Test](./images/lab3_stage_04_test.png)

*ภาพที่ 21 **Test** — `catfood-test-2` ถึง `healthy` และ `/api/health` ตอบ version `1.1.0` กับ commit ที่ clone มา*

![stage Push](./images/lab3_stage_05_push.png)

*ภาพที่ 22 **Push** — `Login Succeeded` แล้ว push `lab3-20260926r2-2` และจด digest `c4db3e26a831...`*

![stage Clean](./images/lab3_stage_06_clean.png)

*ภาพที่ 23 **Clean** — `ลบแอปเดิม catfood-web (8e69a91bd888, ...)` คือร้านของ build #1 ถูกลบที่นี่ **ก่อน Pull** แล้ว `Untagged`/`Deleted` image ของ build #2*

![stage Pull](./images/lab3_stage_07_pull.png)

*ภาพที่ 24 **Pull** — ดึง `...@sha256:c4db3e26a831...` จาก Docker Hub digest เดียวกับที่ Push จดไว้*

![stage Deploy](./images/lab3_stage_08_deploy.png)

*ภาพที่ 25 **Deploy** — `catfood-web` ถึง `healthy` รันจาก `image: ...@sha256:c4db3e26a831...` และ health ตอบ `1.1.0` build `2`*

ตรวจจาก **② shell ของ devtools** ว่าร้านเป็น container พี่น้องบน Docker ของ devtools:

<!-- lab3-test:verify-web -->
```bash
docker ps --filter name=^catfood-web$ --format '{{.Names}}  {{.Image}}  {{.Status}}  {{.Ports}}'
curl -s http://localhost:3000/api/health; echo
ls /root/lab3-work
```

✅ **ผลจากรอบทดสอบ** (หลัง build #2 — `/root/lab3-work` ว่างเพราะ Clean ลบซอร์สแล้ว):

```text
catfood-web  c4db3e26a831  Up 4 seconds (healthy)  0.0.0.0:3000->3000/tcp, [::]:3000->3000/tcp
{"status":"ok","app":"catfood-shop","version":"1.1.0","build":"2","commit":"789e08d582e6","builtAt":"2026-09-26T07:04:00Z","host":"fa874f49da64"}
```

เปิด `http://localhost:3000` อีกครั้ง:

![หน้าร้าน v1.1.0 build #2](./images/lab3_app_03_version2.png)

*ภาพที่ 26 (ภาพหน้าจอจริง) หน้าร้านหลัง build #2 chip เปลี่ยนเป็น `v1.1.0 · build #2`*

![Deployment info ของ build #2](./images/lab3_app_04_build2_info.png)

*ภาพที่ 27 (ภาพหน้าจอจริง) หัวข้อ Deployment ของหน้าร้าน แสดง version, build, commit, เวลา build และ container `fa874f49da64` ตรงกับ `/api/health` ด้านบน*

| วัดค่า | build #1 (v1.0.0) | build #2 (v1.1.0) |
|---|---:|---:|
| ผล | `SUCCESS` | `SUCCESS` |
| ระยะเวลารวม (รอบทดสอบ) | 27 วินาที | 27 วินาที |
| tag บน Docker Hub | `lab3-20260926r2-1` | `lab3-20260926r2-2` |
| digest | `sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621` | `sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a` |
| ช่วงที่เว็บปิด (Clean + Pull + Deploy) | 7 วินาที | 6 วินาที |

🔍 **ตีความ:** ซอร์ส commit เดิม เปลี่ยนเพียง `APP_VERSION`, `BUILD_NUMBER` และ `BUILD_TIME` ซึ่ง Dockerfile วางไว้ท้ายสุดเป็น `ENV` (metadata) ทุกขั้นที่สร้างไฟล์จึง `CACHED` และไม่มี layer ใหม่ต้องอัปโหลด แต่ **digest เปลี่ยน** เพราะ config ของ image เปลี่ยน · Clean ของ build #2 เป็นที่เดียวที่ร้าน build #1 ถูกลบ Deploy จึงเริ่มบนเครื่องที่ไม่มี `catfood-web` และ image ที่ขึ้นเว็บคือ digest ที่เพิ่ง push

บน Docker Hub ที่ `https://hub.docker.com/r/<DOCKER_USER>/catfood-shop/tags` จะเห็น tag `lab3-1` และ `lab3-2` แต่ละตัวชี้ digest ของ build ตัวเอง ผลจาก API สาธารณะของ Docker Hub ในรอบทดสอบ:

```text
lab3-20260926-1 sha256:d52e068339ef73a7c1d837ca9634e9ed45589a2dec75b077cbc503ab26396d23
lab3-20260926r2-1 sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
lab3-20260926r2-2 sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
lab3-20260926r2-5 sha256:ab17aa4dc2503545f876d3717cc3fb43355d235059d28e85510cbf864294d3e0
```

(`lab3-20260926-1` เป็น tag ของการรันครั้งแรกในวันเดียวกันที่ถูกแทนด้วยรอบ `lab3-20260926r2` และ `lab3-20260926r2-5` มาจาก build #5 ที่ทดสอบการปฏิเสธของ Clean ดูสรุปผลการทดสอบ)

![หน้า Tags บน Docker Hub](./images/lab3_hub_02_pushed_tags.png)

*ภาพที่ 28 (ภาพหน้าจอจริง) หน้า Tags กรองด้วย `lab3-20260926r2` — tag `-1` ชี้ `8e69a91bd888` และ `-2` ชี้ `c4db3e26a831` ตรงกับ console*

![รายละเอียด digest บน Docker Hub](./images/lab3_hub_03_image_digest.png)

*ภาพที่ 29 (ภาพหน้าจอจริง) หน้ารายละเอียดของ image build #2 แสดง manifest digest เต็ม `sha256:c4db3e26a831...` ตัวเดียวกับที่ Pull และ Deploy ใช้*

---

## F. ป้องกันค่าอันตราย และ build ที่ล้มก่อน Clean

### การทดลองที่ 10 — กรอก parameter ผิด แล้วดูว่าร้านเดิมยังอยู่

**(ก) ค่าที่แฝงคำสั่ง shell:** Build with Parameters โดยกรอก `APP_VERSION` เป็น `1.2.0; id` (มี `;` และช่องว่าง) — ถ้าค่านี้ถูกส่งถึง shell ⑤ ตรง ๆ `id` จะถูกรันเป็น `root` บน devtools

✅ **ผลจากรอบทดสอบ** (build #3):

```text
Started by user labadmin
Running on Jenkins in /var/jenkins_home/workspace/docker-build-push
+ ssh -i **** devtools-gw NAME='catfood-test-3' CFG='/tmp/lab3-docker-3' WORK_DIR='/root/lab3-work/build-3' bash -s
เก็บกวาดของ build ที่ล้มแล้ว: catfood-test-3 /tmp/lab3-docker-3 /root/lab3-work/build-3
ERROR: APP_VERSION ไม่ถูกต้อง: ต้องเป็นรูปแบบ X.Y.Z เช่น 1.0.0
Finished: FAILURE
```

![build #3 ล้มที่ Connect](./images/lab3_jenkins_12_invalid_parameter.png)

*ภาพที่ 30 (ภาพหน้าจอจริง) build #3 Connect เป็นสีแดง stage ถัดไปทั้งหมดถูกข้าม (skipped) — ผลที่ตั้งใจให้เกิด*

🔍 **ตีความ:** build ล้มใน Connect ภายในราว 2 วินาที บรรทัด `+ ssh` บรรทัดเดียวใน console มาจาก `post { unsuccessful }` ที่เก็บกวาดหลัง build ล้ม **ไม่มี SSH ใดที่ส่งค่า `1.2.0; id`** (ค่าที่ส่งมีเพียงชื่อ container และ path ของ build) ข้อความ `ERROR:` ถูกพิมพ์ท้าย console เพราะ Jenkins รายงานสาเหตุหลัง post ทำงานเสร็จ

**(ข) branch ที่ไม่มีอยู่จริง:** Build with Parameters โดยกรอก `GIT_REF` = `no-such-branch` (รูปแบบถูก จึงผ่าน Connect)

✅ **ผลจากรอบทดสอบ** (build #4 เฉพาะ Clone และ post):

```text
+ ssh -i **** devtools-gw WORK_DIR='/root/lab3-work/build-4' GIT_URL='https://github.com/Tuchsanai/DevTools.git' GIT_REF='no-such-branch' APP_SUBDIR='04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop' bash -s
fatal: Remote branch no-such-branch not found in upstream origin
...
+ ssh -i **** devtools-gw NAME='catfood-test-4' CFG='/tmp/lab3-docker-4' WORK_DIR='/root/lab3-work/build-4' bash -s
เก็บกวาดของ build ที่ล้มแล้ว: catfood-test-4 /tmp/lab3-docker-4 /root/lab3-work/build-4
ERROR: script returned exit code 128
Finished: FAILURE
```

![build #4 ล้มที่ Clone](./images/lab3_jenkins_13_missing_branch.png)

*ภาพที่ 31 (ภาพหน้าจอจริง) build #4 ผ่าน Connect แต่ Clone เป็นสีแดงด้วย `Remote branch no-such-branch not found` stage ที่เหลือถูกข้าม — ผลที่ตั้งใจให้เกิด*

หลัง build #3 และ #4 ร้านยังเป็น build #2 container เดิม (ไม่มี container ทดสอบหรือโฟลเดอร์ login ค้าง):

```text
fa874f49da64 Up 48 seconds (healthy)
{"status":"ok","app":"catfood-shop","version":"1.1.0","build":"2","commit":"789e08d582e6","builtAt":"2026-09-26T07:04:00Z","host":"fa874f49da64"}
ls: cannot access '/tmp/lab3-docker-*': No such file or directory
```

🔍 **ตีความ:** ทั้งสอง build ล้ม **ก่อน Clean** ร้านเดิมจึงไม่ถูกแตะ และ `post` ลบเฉพาะของ build ที่ล้ม (`catfood-test-N`, `/tmp/lab3-docker-N`, `/root/lab3-work/build-N`) ลองแบบเดียวกันกับ `APP_SUBDIR` = `../../etc` จะได้ `APP_SUBDIR ไม่ถูกต้อง` ที่ Connect

---

## ✅ ตรวจปิดแล็บ

- [ ] `docker exec jenkins sh -c 'docker version'` ยังได้ `docker: not found` และ `jenkins` ยังเป็น container เดิมจาก LAB 1 (ไม่ได้สร้างใหม่)
- [ ] `docker exec jenkins ssh -G devtools-gw` แสดง `hostname` เป็น gateway ของ `cicd-net` ในเครื่องตนเอง และ `stricthostkeychecking true`
- [ ] หน้า Credentials มี `devtools-ssh` และ `dockerhub`
- [ ] job `docker-build-push` build #1 และ #2 เป็น `SUCCESS` ครบ Connect → Clone → Build → Test → Push → Clean → Pull → Deploy
- [ ] stage Clean ของ build #2 มีบรรทัด `ลบแอปเดิม catfood-web (...)` และ stage Deploy ของ build #2 แสดง `image: docker.io/<DOCKER_USER>/catfood-shop@sha256:...` ตรงกับ digest ใน stage Push
- [ ] หน้า Tags บน Docker Hub มี `lab3-1` และ `lab3-2` ที่ digest ตรงกับ console
- [ ] `http://localhost:3000` แสดง `v1.1.0 · build #2` และ `/api/health` มี `commit` ตรงกับ stage Clone
- [ ] build ที่กรอก `APP_VERSION=1.2.0; id` ล้มที่ Connect และ build ที่ `GIT_REF=no-such-branch` ล้มที่ Clone โดยร้านยังเป็น build #2

## 📊 สรุปผลการทดสอบของเอกสารนี้

ทดสอบเมื่อ 2026-09-26 06:45 UTC ใน container ทดลองแยกจาก image `tuchsanai/devtools:2569_1` (สร้างด้วย `--privileged --tmpfs /run` แบบเดียวกับทาง A) และ Jenkins 2.568.3 จาก `jenkins/jenkins:lts-jdk21` ด้วยคำสั่งสร้างของ LAB 1 ทุกตัวอักษร push/pull กับ **Docker Hub จริง** (`tuchsanai/catfood-shop`)

| รายการ | ผล |
|---|---|
| `jenkins` มี docker / docker.sock | ไม่มีทั้งคู่ (`docker CLI = none docker.sock = none`) |
| `jenkins` resolve `devtools` | ไม่ได้ (exit 2) |
| SSH ผ่าน `devtools-gw` → gateway ของ `cicd-net` | ถึง sshd และตรวจ host key แบบ pin ผ่าน |
| build แรกแบบ Build Now (ไม่ส่ง parameter) | `params.*` ได้ค่า default ครบ |
| build #1 (`1.0.0`, clone จาก GitHub `main`) | `SUCCESS` ครบ 8 stage ใน 27 วินาที · `lab3-20260926r2-1` |
| build #2 (`1.1.0`) | `SUCCESS` ใน 27 วินาที · Clean ลบร้าน build #1 · deploy `sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a` |
| build #3 (`1.2.0; id`) | `FAILURE` ที่ Connect ร้านยังเป็น build #2 |
| build #4 (`GIT_REF=no-such-branch`) | `FAILURE` ที่ Clone · post เก็บกวาดของ build #4 · ร้านยังเป็น build #2 |
| build #5 (มี `catfood-web` ที่ไม่ใช่ของแล็บอยู่ก่อน) | `FAILURE` ที่ Clean (`failure`) ด้วยข้อความ `พบ container catfood-web ที่ไม่ได้สร้างโดย LAB 3` container นั้นยังอยู่ · Pull/Deploy ถูกข้าม · image `catfood-shop:build-5` ที่ build แล้วค้างในเครื่อง (ลบด้วยบล็อกเก็บกวาด) |
| บล็อกเก็บกวาด | ลบ container ที่มี label ของ LAB 3, image ของร้าน และ `/root/lab3-work` · `jenkins`, `cicd-net`, `jenkins_home` และ `catfood-web` ที่ไม่มี label ของแล็บยังอยู่ · รอบทดสอบนี้ใช้ตัวเลือก image ตามชื่อ `catfood-shop` รุ่นก่อน บล็อกปัจจุบันเลือก image ด้วย label `devtools.lab=lab3` (ตรวจ syntax แล้ว แต่ไม่ได้รัน end-to-end ซ้ำ) |
| หมายเหตุการทดสอบ | การรันครั้งแรกของวัน (tag `lab3-20260926-1`) ส่ง config ของ job ผ่าน REST API โดยไม่ระบุ charset ข้อความไทยใน console จึงเพี้ยน จึงแก้เครื่องมือทดสอบให้ส่ง `charset=UTF-8` ลบ build นั้นและรันใหม่ด้วย prefix `lab3-20260926r2` tag เดิมยังอยู่บน Docker Hub เป็นหลักฐาน · นักศึกษาวาง Jenkinsfile ผ่านหน้าเว็บ จึงไม่พบปัญหานี้ |

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `ssh: Could not resolve hostname devtools-gw` | ยังไม่ได้ทำการทดลองที่ 4 หรือไฟล์ config ไม่ได้อยู่ใต้ `/var/jenkins_home/.ssh` | รันบล็อกของการทดลองที่ 4 แล้วตรวจด้วย `docker exec jenkins ssh -G devtools-gw` |
| `Connection timed out` / `No route to host` | gateway ใน config ไม่ใช่ของ `cicd-net` ปัจจุบัน (เช่น ลบแล้วสร้าง network ใหม่) หรือ `jenkins` ไม่ได้อยู่ใน `cicd-net` | รันบล็อกการทดลองที่ 3 เทียบค่า แล้วรันบล็อกการทดลองที่ 4 ซ้ำ |
| `Host key verification failed` | host key ใน `known_hosts` ไม่ตรงกับ devtools ปัจจุบัน (เช่น สร้าง devtools ใหม่แต่ใช้ volume เดิม) | รันบล็อกการทดลองที่ 4 ซ้ำ ซึ่งเขียน `known_hosts` จาก host key ปัจจุบัน |
| `Permission denied (publickey,password)` ใน Connect | public key ไม่อยู่ใน `authorized_keys` หรือวาง private key ใน credential ไม่ครบ BEGIN/END | รันการทดลองที่ 5 แล้วแก้ credential `devtools-ssh` เป็นเนื้อหา `~/.ssh/jenkins_devtools` ทั้งไฟล์ |
| `Bad owner or permissions on /var/jenkins_home/.ssh/config` | สร้างไฟล์ด้วยผู้ใช้ root หรือสิทธิ์กว้างเกินไป | รันบล็อกการทดลองที่ 4 (ใช้ `-u jenkins` และ `umask 077`) |
| `ERROR: Could not find credentials entry with ID ...` | ID สะกดไม่ตรง | ตั้ง ID เป็น `devtools-ssh` และ `dockerhub` ตรงตัว |
| `username ใน credential dockerhub ไม่ถูกต้อง` | กรอกอีเมลหรือตัวพิมพ์ใหญ่ในช่อง Username | ใช้ Docker Hub username ตัวพิมพ์เล็ก |
| `... ไม่ถูกต้อง: ...` ใน Connect | parameter ผิดรูปแบบ | แก้ค่าตามข้อความ (`X.Y.Z`, `https://...`, path แบบ relative) |
| `fatal: repository '...' not found` / `Remote branch ... not found` ใน Clone | `GIT_URL` ผิด เป็น repository ส่วนตัว หรือ `GIT_REF` ไม่มีอยู่ | เปิด URL ในเบราว์เซอร์ตรวจว่าเป็น Public และมี branch/tag นั้น |
| `ไม่พบ .../Dockerfile` ใน Clone | `APP_SUBDIR` ไม่ตรงกับโครงสร้าง repository | ตรวจ path บน GitHub ให้ชี้โฟลเดอร์ที่มี `Dockerfile` |
| stage Test ล้ม ไม่ถึง `healthy` | แอปเริ่มไม่ขึ้น | ใน ② `docker run -d --name debug-shop catfood-shop:build-N` แล้ว `docker logs debug-shop` (เสร็จแล้ว `docker rm -f debug-shop`) |
| `unauthorized` / `denied: requested access` ใน Push หรือ Pull | token ผิด หมดอายุ ไม่มีสิทธิ์ Write หรือ username ไม่ตรง | สร้าง token Read & Write ใหม่ แล้วแก้ credential `dockerhub` |
| `toomanyrequests` | Docker Hub rate limit | รอสักครู่แล้วสั่งใหม่ |
| `พบ container catfood-web ที่ไม่ได้สร้างโดย LAB 3` ใน Clean | มี container ชื่อ `catfood-web` ที่สร้างเอง (ไม่มี label `devtools.lab=lab3` / `devtools.role=app`) | ตรวจด้วย `docker inspect catfood-web` ถ้าไม่ใช้แล้วให้ลบเองหรือเปลี่ยนชื่อ แล้ว Build ใหม่ |
| `port 3000 ถูก container อื่นใช้อยู่: ...` ใน Deploy | มี container อื่นบน Docker ของ devtools publish 3000 (ร้านถูกลบใน Clean แล้ว เว็บจึงปิดอยู่) | ใน ② `docker ps --filter publish=3000` ลบเฉพาะตัวที่ตนสร้างและไม่ใช้แล้ว แล้ว Build ใหม่ |
| เปิด `localhost:3000` ไม่ได้ระหว่าง build | อยู่ในช่วง Clean → Deploy ตามที่ออกแบบไว้ | รอให้ Deploy เขียว |
| เปิด `localhost:3000` จากเครื่องเราไม่ได้ ทั้งที่ Deploy เขียว | `devtools` ไม่ได้ publish `-p 3000:3000` | ตรวจ `docker port devtools` บนเครื่องเรา ถ้าไม่มี 3000 ต้องสร้าง devtools ใหม่ตามทาง A (ข้อมูลข้างในจะหาย) |

## 🧹 เก็บกวาด

**ห้ามลบ** `devtools`, `jenkins`, volume `jenkins_home`, network `cicd-net` และ credential ทั้งสอง — LAB ถัดไปใช้ต่อ สิ่งที่แล็บนี้สร้างและลบได้อย่างปลอดภัย (ใน **② shell ของ devtools**) บล็อกนี้เลือกทั้ง container และ image ด้วย label `devtools.lab=lab3` ที่ Jenkinsfile ติดให้ตอน build/run จึงลบเฉพาะของที่แล็บสร้าง image หรือ container อื่นที่ไม่มี label นี้ (แม้ชื่อ `catfood-shop` เหมือนกัน) จะไม่ถูกแตะ:

<!-- lab3-test:cleanup -->
```bash
docker ps -a --filter label=devtools.lab=lab3 --format '{{.Names}}' | xargs -r docker rm -f    # catfood-web และ catfood-test-N ที่มี label ของ LAB 3 เท่านั้น
docker image ls -aq --filter label=devtools.lab=lab3 | sort -u | xargs -r docker image rm -f    # image ที่ build/pull จาก Jenkinsfile นี้ (มี label devtools.lab=lab3) เท่านั้น image อื่นแม้ชื่อ catfood-shop จะไม่ถูกลบ
rm -rf /root/lab3-work /tmp/lab3-docker-*        # ซอร์สที่ clone และ login ชั่วคราวที่อาจค้างเมื่อ build ถูกยกเลิกกลางทาง
docker ps -a --format '{{.Names}}'; docker network ls --filter name=cicd-net --format '{{.Name}}'; docker volume ls -q --filter name=jenkins_home
```

✅ **ผลจากรอบทดสอบ** (สามบรรทัดท้ายคือสิ่งที่ต้องยังอยู่: `jenkins`, `cicd-net`, `jenkins_home` · รอบทดสอบมี container ชื่อ `catfood-web` จาก image `jenkins/jenkins` ที่สร้างขึ้นเพื่อทดสอบว่า Clean ปฏิเสธของที่ไม่ใช่ของแล็บ มันไม่มี label ของ LAB 3 จึงไม่ถูกลบและยังปรากฏในรายการ — เครื่องนักศึกษาจะไม่มีบรรทัดนี้ · ผลนี้จับจากบล็อกรุ่นก่อนที่เลือก image ตามชื่อ `catfood-shop` ส่วนตัวเลือก image ด้วย label ในบล็อกปัจจุบันตรวจ syntax แล้วแต่ยังไม่ได้รัน end-to-end ซ้ำ รายการที่เหลือจึงเหมือนกันเพราะ image ของร้านในรอบทดสอบทุกตัวสร้างจาก Jenkinsfile ที่ติด label):

```text
Untagged: tuchsanai/catfood-shop@sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
Deleted: sha256:8e69a91bd88883c7d11582be916bb1fc1f9273be7bf2fa9343732d7c816da621
Untagged: catfood-shop:build-5
Untagged: tuchsanai/catfood-shop:lab3-20260926r2-5
Deleted: sha256:ab17aa4dc2503545f876d3717cc3fb43355d235059d28e85510cbf864294d3e0
Untagged: tuchsanai/catfood-shop@sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
Deleted: sha256:c4db3e26a831bcad768516433bc9cfc63c114181c385999dba6d62a796649c5a
Untagged: tuchsanai/catfood-shop@sha256:d52e068339ef73a7c1d837ca9634e9ed45589a2dec75b077cbc503ab26396d23
Deleted: sha256:d52e068339ef73a7c1d837ca9634e9ed45589a2dec75b077cbc503ab26396d23
catfood-web
jenkins
cicd-net
jenkins_home
```

เมื่อเลิกใช้ SSH จาก Jenkins แล้ว (เช่น จบรายวิชา) ให้ **เพิกถอนสิทธิ์**: ลบบรรทัดที่ลงท้าย `jenkins-to-devtools` ออกจาก `/root/.ssh/authorized_keys` ลบ credential `devtools-ssh` และ `dockerhub` ใน Jenkins และ revoke token ที่หน้า Docker Hub → Personal access tokens · tag `lab3-N` บน Docker Hub ลบได้ที่หน้า Tags ของ repository

## กู้สถานะเมื่อปิดเครื่องหรือเริ่มระบบใหม่

บน **① terminal ของเครื่องเรา** `docker start devtools` แล้วรอให้ Docker ข้างในและ `jenkins` กลับมา (ดู LAB 1 หัวข้อเดียวกัน) `catfood-web` มี `--restart unless-stopped` จึงกลับมาเองด้วย ไฟล์ `~/.ssh/config` ของ Jenkins, host key และ network `cicd-net` อยู่ข้างใน devtools ครบ gateway จึงเป็นค่าเดิม ไม่ต้องตั้งใหม่

## 🤔 คำถามทบทวน

1. ถ้าเขียน `ssh root@devtools` ใน Jenkinsfile จะเกิดอะไรขึ้น และทำไมการเปลี่ยนชื่อ container `devtools` บนเครื่องเราจึงไม่ช่วย
2. ทำไม `~/.ssh/config` ที่ตั้งไว้จึงยังอยู่หลัง `docker rm -f jenkins` แล้วสร้างใหม่ด้วยคำสั่งของ LAB 1
3. ถ้า private key ของ `devtools-ssh` รั่ว ผู้ที่ได้ไปทำอะไรได้บ้าง และเพิกถอนอย่างไร
4. ทำไม Clean ต้องเกิด **หลัง** Push สำเร็จ และถ้าย้าย Clean ไปไว้ก่อน Build จะเสียอะไร
5. ทำไม Pull และ Deploy ใช้ `repository@sha256:...` แทน `repository:tag`
6. ทำไมการตรวจ `APP_VERSION` ต้องเกิดบน Jenkins ก่อน `ssh` ไม่ใช่ในสคริปต์ฝั่ง devtools

➡️ **แล็บถัดไป:** [LAB 4 — Pipeline from Git](../004_LAB_Pipeline_From_Git/README.md)
