# LAB 3 — Jenkins สั่ง devtools ผ่าน SSH: Connect → Clone → Build → Test → Push → Clean → Pull → Deploy ร้านอาหารแมว

> ⏱️ ประมาณ 50–60 นาที · 🧪 9 ขั้น · 🎯 จบเมื่อกด **Build** ใน Jenkins แล้วเปิด `http://localhost:3000` เห็นร้าน **Meow Mart** เวอร์ชันที่ Pipeline เพิ่ง build, push ขึ้น Docker Hub, pull กลับตาม digest และ deploy และผ่านรายการ **✅ ตรวจปิดแล็บ** ครบทุกข้อ

แล็บนี้ตอบคำถามว่า **“Jenkins ที่ไม่มี Docker อยู่ข้างในเลย จะ build → test → push → deploy ได้อย่างไร”** บนเครื่องของเรามี container พี่น้อง (sibling) สองตัวอยู่บน network `cicd-net` เดียวกัน `jenkins` เป็น **ผู้สั่ง** ส่วน `devtools` เป็น **ผู้ทำ** Jenkins SSH ไปที่ `devtools:22` ด้วยรหัสผ่านจาก Jenkins Credentials แล้วส่งสคริปต์ไปรันทีละ stage คำสั่ง `git clone` และ `docker build/run/push/pull` ทั้งหมดจึงรันบน `devtools` และร้านเปิดเป็น container `catfood-web` บน Docker ของ `devtools`

> **กติกาของแล็บ:** นักศึกษาไม่พิมพ์ `docker build`, `docker push` หรือ `git clone` ของร้านเอง ทุกอย่างเริ่มจากปุ่มบน Jenkins · `jenkins` เป็น image มาตรฐาน `jenkins/jenkins:lts-jdk21` **ไม่มี Docker CLI และไม่ mount `docker.sock`** (เพิ่มเพียงโปรแกรม `sshpass`) · Jenkinsfile ถูกวางในช่อง **Pipeline script** ของ job

{{fig:diagram_architecture}}

---

## 📚 แนวคิดที่ต้องรู้

### 1. ใครอยู่ตรงไหน

| container | อยู่บน Docker ของ | network | เข้าจากเครื่องเราทาง |
|---|---|---|---|
| `jenkins` | เครื่องของเรา | `cicd-net` | `localhost:8080` → `jenkins:8080` |
| `devtools` (`--privileged` มี Docker ของตัวเองข้างใน) | เครื่องของเรา | `cicd-net` | `localhost:2222` → `devtools:22` · `localhost:3000` → `devtools:3000` |
| `catfood-test-N` (ชั่วคราว) และ `catfood-web` (ร้าน) | **ข้างใน** `devtools` | bridge ข้างใน devtools | `devtools:3000` → `catfood-web:3000` |

- `jenkins` และ `devtools` อยู่บน network ที่เราสร้างเอง (user-defined) Docker DNS ของ network นี้แปลชื่อ container เป็น IP ให้ Jenkinsfile จึงเขียน `root@devtools` ได้ตรง ๆ ไม่ต้องหา IP
- เบราว์เซอร์เปิดร้านที่ `localhost:3000` ผ่านสองทอด: เครื่องเรา → `devtools:3000` → `catfood-web:3000` ที่ stage Deploy สร้าง

### 2. SSH ด้วยรหัสผ่าน และการ pin host key

- image ของ `devtools` เปิด SSH ให้ `root` ด้วยรหัสผ่านตั้งต้น `passwd` ซึ่งเป็นค่าของ image แล็บนี้เท่านั้น Jenkins เก็บคู่ `root` / `passwd` เป็น credential ชนิด **Username with password** ID `devtools-ssh`
- `ssh` ไม่รับรหัสผ่านจาก script จึงติดตั้ง `sshpass` ใน `jenkins` ครั้งเดียว Jenkinsfile ผูก credential เป็นตัวแปร `SSH_USER` และ `SSHPASS` แล้วเรียก `sshpass -e ssh ...` ตัวเลือก `-e` ให้ sshpass อ่านรหัสจาก environment `SSHPASS` รหัสจึงไม่อยู่ใน command line, console หรือไฟล์
- `StrictHostKeyChecking=yes` ให้ SSH ต่อเฉพาะเครื่องที่ host key ตรงกับใน `known_hosts` เราคัดลอก host key จากไฟล์ของ `devtools` เองผ่าน Docker ไปใส่ `known_hosts` ของ Jenkins **ก่อน** ต่อครั้งแรก ถ้ามีเครื่องอื่นแอบอ้างชื่อ `devtools` SSH จะปฏิเสธก่อนส่งรหัสผ่าน

> ⚠️ `root` บน `devtools` ที่รันแบบ `--privileged` สั่ง Docker ของ devtools ได้ทุกอย่าง รหัสผ่านนี้จึงมีอำนาจสูงและใช้ได้กับแล็บที่ลบทิ้งได้เท่านั้น ระบบจริงควรใช้ SSH key หรือ build agent ผู้ใช้ที่ไม่ใช่ `root` และเปลี่ยนรหัสตั้งต้นเสมอ

### 3. ค่าที่ส่งข้าม SSH ต้องสะอาด

ค่า parameter ถูกเขียนเป็นบรรทัด `NAME='value'` ต้นสคริปต์ที่ bash ของ devtools รัน ถ้าค่ามี `;`, `$( )` หรือช่องว่าง shell อาจรันเป็นคำสั่ง stage **Connect** จึงตรวจทุก parameter ด้วย regex บน Jenkins ก่อน SSH และ `onDevtools` ยอมรับเฉพาะอักขระ `A-Za-z0-9._:/@=+-` ส่วนคำสั่ง `sh` ที่เรียก SSH เป็นข้อความคงที่ใน `'...'` Groovy จึงไม่แทนค่าความลับลงในคำสั่ง

### 4. Tag, Digest และลำดับ Clean → Pull → Deploy

- **tag** (`lab3-2`) เป็นป้ายที่ย้ายได้ **digest** (`sha256:...`) คำนวณจากเนื้อหา image จึงเปลี่ยนไม่ได้ Push จด digest ไว้ แล้ว Pull และ Deploy ใช้ `repository@sha256:...` ตัวเดียวกัน
- **Clean** ทำหลัง Push สำเร็จเท่านั้น โดยลบ container ทดสอบ ร้านเดิม image ของ build นี้ และซอร์ส แล้ว **ยืนยันว่าไม่มี image ตาม tag และ digest นี้เหลือในเครื่อง** Pull จึงต้องดึงจาก Docker Hub จริง
- Clean ลบเฉพาะ container ที่มี label `devtools.lab=lab3` (ร้านต้องมี `devtools.role=app` ด้วย) ถ้าเจอ `catfood-web` ที่ไม่ได้สร้างโดยแล็บนี้ Clean จะหยุดโดยไม่ลบอะไร
- build ที่ล้ม **ก่อน** Clean ไม่แตะร้านเดิม · ตั้งแต่ Clean จนถึง Deploy เขียว ร้านจะปิดชั่วคราว (รอบทดสอบราว {{val:b2_downtime}}) แล็บนี้ไม่มี rollback อัตโนมัติ ถ้า Pull หรือ Deploy ล้ม ให้แก้สาเหตุแล้ว Build ใหม่

{{fig:diagram_pipeline}}

---

## 🎯 Learning Objectives — ผลลัพธ์การเรียนรู้

เมื่อจบแล็บนี้ นักศึกษาจะสามารถ

1. สร้าง `jenkins` และ `devtools` เป็น container พี่น้องบน network เดียวกัน และอธิบายได้ว่าทำไม Jenkins เรียกชื่อ `devtools` ได้
2. ตั้ง SSH แบบรหัสผ่านจาก Jenkins ด้วย credential ชนิด Username with password และ `sshpass -e` โดย pin host key ก่อนต่อครั้งแรก
3. อ่าน Jenkinsfile แล้วบอกได้ว่าคำสั่งใดรันบน Jenkins คำสั่งใดรันบน devtools และความลับแต่ละชิ้นเดินทางทางไหน
4. รัน Pipeline 8 stage แล้วสืบย้อนจากหน้าเว็บ → container → digest → build → commit ได้
5. แสดงได้ว่า parameter อันตราย, branch ที่ไม่มีอยู่ และรหัสผ่าน SSH ที่ผิด ทำให้ build ล้มโดยร้านเดิมยังเปิดอยู่

## 🗺️ ลำดับการทำ

| ขั้น | ทำที่ | ทำอะไร | หลักฐานที่ต้องได้ |
|---|---|---|---|
| 1 | 🖥️ host | สร้าง `cicd-net`, `devtools`, `jenkins` | สองแถว `Up` และทั้งคู่อยู่ใน `cicd-net` |
| 2 | 🖥️ host + เบราว์เซอร์ | ปลดล็อกและตั้งค่า Jenkins | Dashboard หลัง login |
| 3 | 🖥️ host | ติดตั้ง `sshpass` ใน `jenkins` | `/usr/bin/sshpass` และ `docker: none` |
| 4 | 🖥️ host | pin host key ของ `devtools` | fingerprint สองบรรทัดตรงกัน |
| 5 | 🖥️ host | ทดสอบ SSH ด้วยรหัสผ่าน | ได้ hostname ของ devtools โดยไม่ถาม `yes/no` |
| 6 | เบราว์เซอร์ | สร้าง credential `devtools-ssh` และ `dockerhub` | หน้า Credentials มีสองรายการ |
| 7 | เบราว์เซอร์ | สร้าง job แล้ว **Build Now** | #1 `SUCCESS` ครบ 8 stage ร้าน `v1.0.0` |
| 8 | เบราว์เซอร์ | Build with Parameters `APP_VERSION=1.1.0` | #2 Clean ลบร้านเดิม และ Pull/Deploy ใช้ digest เดียวกับ Push |
| 9 | เบราว์เซอร์ | ลองค่าผิด 3 แบบ | #3–#5 ล้ม ร้านยังเป็น #2 |

> 🖥️ **host** คือ terminal ของเครื่องเราที่สั่ง `docker` ได้ (Linux/macOS หรือ WSL บน Windows) ทุกคำสั่ง `docker` ในแล็บนี้พิมพ์ที่ host ไม่ต้อง SSH เข้า devtools

## 📂 ไฟล์ในโฟลเดอร์นี้

| ไฟล์ | หน้าที่ |
|---|---|
| `Jenkinsfile` | Pipeline 8 stage (เนื้อหาเดียวกับหัวข้อ “Jenkinsfile ฉบับสมบูรณ์” ด้านล่าง) |
| `catfood-shop/` | ซอร์สร้าน Meow Mart (Next.js) ที่ stage Clone ดึงจาก GitHub ไม่ต้อง copy เอง |
| `catfood-shop/Dockerfile` | single-stage + `HEALTHCHECK` รับ build-arg `APP_VERSION`, `BUILD_NUMBER`, `GIT_COMMIT`, `BUILD_TIME` |
| `images/` | แผนภาพประกอบ (`lab3_diagram_*`) และภาพหน้าจอจริงจากรอบทดสอบ |

---

## 0. สิ่งที่ต้องมี

- Docker บนเครื่องของเรา และ port `8080`, `2222`, `3000` ว่าง
- บัญชี Docker Hub ที่ยืนยันอีเมลแล้ว และ **Personal Access Token สิทธิ์ Read & Write** (Account settings → Personal access tokens) แนะนำให้สร้าง repository `catfood-shop` แบบ **Public** เพื่อเปิดดูหน้า Tags ได้

{{fig:hub_pat}}

ซอร์สร้านอยู่ใน repository สาธารณะของรายวิชา stage Clone จะดึงเฉพาะโฟลเดอร์นี้:

{{fig:github_source}}

---

## ขั้นที่ 1 — สร้าง network และ container สองตัว (🖥️ host)

{{block:host-setup}}

| ส่วนของคำสั่ง | ทำไม |
|---|---|
| `docker rm -f jenkins devtools` | ลบ container ชื่อเดิมจากแล็บก่อน (ถ้าไม่มีก็ไม่ error) ⚠️ ของข้างใน `devtools` เดิม รวม Jenkins ของ LAB 1–2 จะหายไป |
| `docker network create cicd-net` | network ที่ทั้งสองตัวใช้ร่วมกัน ถ้าขึ้น `already exists` แปลว่ามีแล้ว ใช้ต่อได้ |
| `--network cicd-net` | ให้ `jenkins` เรียก `devtools` ด้วยชื่อได้ |
| `--privileged --tmpfs /run` | ให้ Docker ข้างใน `devtools` ทำงาน และบูตใหม่ได้โดย `docker.pid` เก่าไม่ค้าง (เหตุผลเดียวกับ LAB 1) |
| `-p 2222:22 -p 3000:3000` | SSH จากเครื่องเราเข้า devtools และหน้าร้าน |
| `-p 8080:8080 -v jenkins_home:/var/jenkins_home` | หน้าเว็บ Jenkins และเก็บสถานะ Jenkins ใน volume |
| `--restart unless-stopped` | Docker เปิดให้เองเมื่อเริ่มระบบใหม่ |

✅ **ผลจากรอบทดสอบ** (ID ของ network ตามด้วย ID ของ `devtools` และ `jenkins` · ของแต่ละเครื่องต่างกัน):

```text
{{out:host-setup}}
```

ตรวจว่าทั้งคู่ `Up` และอยู่ใน `cicd-net`:

{{block:host-check}}

```text
{{out:host-check}}
```

> รอบทดสอบ bind port ไว้ที่ `127.0.0.1` ด้วยเลขอื่นเพื่อไม่ชนกับเครื่องจริง ของนักศึกษาจะเห็น `0.0.0.0:8080->8080/tcp`, `0.0.0.0:2222->22/tcp` และ `0.0.0.0:3000->3000/tcp`

---

## ขั้นที่ 2 — ปลดล็อกและตั้งค่า Jenkins

{{block:unlock}}

✅ ได้สตริงเลขฐานสิบหก 32 ตัว เช่น `{{out:unlock}}` เปิด **http://localhost:8080** วางรหัสในช่อง **Administrator password** → **Continue** → **Install suggested plugins** → สร้างผู้ดูแล `admin` / `admin2569` → คง Jenkins URL เป็น `http://localhost:8080/` → **Save and Finish** → **Start using Jenkins** (รายละเอียดแต่ละหน้าอยู่ในการทดลองที่ 3–4 ของ [LAB 1](../001_LAB_Jenkins_On_Docker/README.md))

{{fig:unlock}}

{{fig:dashboard}}

> ถ้า volume `jenkins_home` บนเครื่องเรามีอยู่แล้วจากครั้งก่อน Jenkins จะไม่ถามรหัสปลดล็อก ให้ login ด้วยผู้ดูแลเดิมได้เลย

---

## ขั้นที่ 3 — ติดตั้ง `sshpass` ใน `jenkins` (🖥️ host)

{{block:sshpass}}

- `-u root` เพราะ `apt-get` ต้องใช้สิทธิ์ root ส่วน Jenkins เองยังรันเป็นผู้ใช้ `jenkins`
- ติดตั้งลงใน container ไม่ได้แก้ image ถ้าลบแล้วสร้าง `jenkins` ใหม่ ต้องรันขั้นนี้ซ้ำ
- บรรทัดที่สองยืนยันว่ามี `sshpass` แล้ว และ Jenkins ยัง **ไม่มี** Docker CLI

✅ **ผลจากรอบทดสอบ** (ส่วนท้าย):

```text
{{out:sshpass-tail}}
```

---

## ขั้นที่ 4 — pin host key ของ `devtools` (🖥️ host)

{{block:pin-hostkey}}

| บรรทัด | ทำอะไร |
|---|---|
| 1 | สร้างบรรทัด `known_hosts` รูปแบบ `devtools ssh-ed25519 AAAA...` จากไฟล์ host key ของ `devtools` เอง |
| 2–3 | คัดลอกผ่านเครื่องเราด้วย `docker cp` ไม่ผ่าน network จึงไม่มีใครแทรกแซงได้ |
| 4 | ผู้ใช้ `jenkins` วางไฟล์เป็น `/var/jenkins_home/.ssh/known_hosts` ซึ่งอยู่ใน volume `jenkins_home` จึงคงอยู่ถาวร |
| 5–6 | fingerprint ต้นทางกับที่ Jenkins บันทึกไว้ต้องตรงกัน |

✅ **ผลจากรอบทดสอบ** (`SHA256:...` สองบรรทัดต้องเหมือนกัน):

```text
{{out:pin-hostkey}}
```

> ไฟล์ `devtools.known_hosts` ที่เหลือในโฟลเดอร์ปัจจุบันเป็น public key ลบทิ้งได้ · host key ติดมากับ image `tuchsanai/devtools:2569_1` (`root@buildkitsandbox`) ทุกเครื่องจึงได้ fingerprint เดียวกัน

---

## ขั้นที่ 5 — ทดสอบ SSH ด้วยรหัสผ่าน (🖥️ host)

{{block:ssh-test}}

พิมพ์ `passwd` เมื่อถูกถาม (ตัวอักษรไม่แสดงบนจอ) แล้วกด Enter

✅ **ผลจากรอบทดสอบ** (บรรทัดสุดท้ายคือ hostname ของ `devtools` ซึ่งเป็น container ID):

```text
{{out:ssh-test}}
```

ไม่มีคำถาม `Are you sure you want to continue connecting (yes/no)?` แปลว่า host key ที่ pin ไว้ถูกใช้แล้ว ถ้าไม่มีบรรทัดของ `devtools` ใน `known_hosts` SSH จะปฏิเสธทันทีก่อนถามรหัส (รอบทดสอบลองโดยชี้ `known_hosts` เป็นไฟล์ว่าง):

```text
{{out:unpinned}}
```

---

## ขั้นที่ 6 — เก็บรหัส SSH และ Docker Hub token ใน Jenkins Credentials

**Manage Jenkins → Credentials → System → Global credentials (unrestricted) → Add Credentials** ทำสองครั้ง:

| ช่อง | `devtools-ssh` | `dockerhub` |
|---|---|---|
| Kind | Username with password | Username with password |
| Username | `root` | `<DOCKER_USER>` (ตัวพิมพ์เล็ก) |
| Treat username as secret | ไม่ติ๊ก | ไม่ติ๊ก |
| Password | `passwd` | `<DOCKER_TOKEN>` |
| ID | `devtools-ssh` | `dockerhub` |
| Description | `SSH password: Jenkins to devtools` | `Docker Hub access token` |

{{fig:ssh_credential}}

✅ **สิ่งที่ต้องเห็น:** หน้า Global credentials มี `devtools-ssh` และ `dockerhub` แสดงเพียง ID และคำอธิบาย ไม่แสดงรหัสหรือ token

{{fig:credentials}}

> ⚠️ token วางได้ที่ Jenkins Credentials เท่านั้น ห้ามวางในแชต เอกสาร หรือ commit ลง Git · Jenkinsfile ตรวจว่า username ของ `dockerhub` มีเฉพาะ `a-z0-9` ก่อนนำไปประกอบชื่อ image

---

## ขั้นที่ 7 — สร้าง job แล้ว Build Now

### อ่าน Jenkinsfile ก่อนรัน

ทุก stage ที่ทำงานบน devtools เรียก `onDevtools(ตัวแปร, สคริปต์)` เช่น stage **Clone**:

```groovy
def commit = onDevtools([WORK_DIR: env.WORK_DIR, GIT_URL: params.GIT_URL,
                         GIT_REF: params.GIT_REF, APP_SUBDIR: params.APP_SUBDIR], '''
rm -rf "$WORK_DIR"
git clone --quiet --depth 1 --filter=blob:none --sparse --branch "$GIT_REF" -- "$GIT_URL" "$WORK_DIR" >&2
...
git rev-parse --short=12 HEAD
''', true).trim()
```

ส่วนหัวใจของ `onDevtools`:

```groovy
writeFile file: 'remote.sh', text: lines.join('\n') + '\n' + body + '\n'
withCredentials([usernamePassword(credentialsId: 'devtools-ssh',
                 usernameVariable: 'SSH_USER', passwordVariable: 'SSHPASS')]) {
  out = sh(script: 'sshpass -e ssh -o StrictHostKeyChecking=yes -o PreferredAuthentications=password "$SSH_USER@devtools" bash -s < remote.sh',
           returnStdout: capture)
}
```

| ส่วน | ทำงานที่ | ความหมาย |
|---|---|---|
| `'''...'''` | Groovy | อัญประกาศเดี่ยวสามตัว Groovy **ไม่แทนค่า** `$` สคริปต์ถูกเขียนลง `remote.sh` ตามตัวอักษร |
| `[WORK_DIR: ..., GIT_URL: ...]` | Groovy | ทุกค่าต้องผ่าน regex แล้วกลายเป็นบรรทัด `GIT_URL='https://...'` ต้น `remote.sh` ต่อจาก `set -euo pipefail` |
| `withCredentials([usernamePassword(...)])` | Jenkins | ใส่ `root` ใน `SSH_USER` และรหัสใน `SSHPASS` เฉพาะในบล็อกนี้ และปิดบังรหัสใน console เป็น `****` |
| `sh(script: '...')` | Jenkins | ข้อความคงที่ใน `'...'` ตัวแปร `$SSH_USER` ถูกแทนค่าโดย shell ของ Jenkins ไม่ใช่ Groovy |
| `sshpass -e ssh ... "$SSH_USER@devtools"` | shell ของ Jenkins | sshpass ป้อนรหัสจาก `SSHPASS` · ssh ตรวจ host key ที่ pin ไว้ · `PreferredAuthentications=password` ใช้รหัสผ่านเท่านั้น |
| `bash -s < remote.sh` | bash บน devtools | สคริปต์เดินทางทาง stdin ของ SSH และทุก `$` ในสคริปต์ถูกแทนค่าบน devtools |
| `returnStdout: true` | Jenkins | เก็บ stdout (เช่น commit, digest) กลับมาเป็นค่าใน Groovy ส่วนข้อความอธิบายพิมพ์ลง stderr (`>&2`) จึงยังเห็นใน console |

| Stage | ทำอะไร (บน devtools ยกเว้นระบุ) | ถ้าไม่ผ่าน |
|---|---|---|
| **1 Connect** | บน Jenkins: ตรวจ parameter 5 ตัวและ username Docker Hub · สร้าง tag `<TAG_PREFIX>-<BUILD_NUMBER>` · พิมพ์ว่า Jenkins ไม่มี docker · แล้ว SSH ไปถาม hostname, Docker และ git ของ devtools | ค่าผิดรูปแบบ, รหัสผ่านผิด หรือ host key ไม่ตรง → หยุดก่อนงานหนัก |
| **2 Clone** | sparse clone `GIT_URL`@`GIT_REF` ลง `/root/lab3-work/build-N` เก็บ commit 12 ตัว | branch ไม่มี หรือไม่มี `Dockerfile` ใน `APP_SUBDIR` |
| **3 Build** | `docker build` พร้อม label ของแล็บ และ build-arg เวอร์ชัน เลข build commit เวลา → `catfood-shop:build-N` | build ล้ม |
| **4 Test** | รัน `catfood-test-N` รอ `healthy` ≤ 30 วินาที อ่าน `/api/health` ต้องได้เวอร์ชันและ commit ที่สั่ง แล้วลบ container เสมอ | ไม่ผ่าน → ไม่ push |
| **5 Push** | login Docker Hub โดยส่ง token ทาง stdin ของ SSH (`--password-stdin`) ลงโฟลเดอร์ชั่วคราว `/tmp/lab3-docker-N` → tag และ push → จด **digest** | push ล้ม (ร้านเดิมยังอยู่) |
| **6 Clean** | ตรวจเจ้าของ `catfood-web` → ลบ container ทดสอบ, **ร้านเดิม**, image สองชื่อของ build นี้ และซอร์ส → ยืนยันว่าไม่เหลือ image ตาม tag/digest | `catfood-web` ไม่ใช่ของแล็บ → หยุดโดยไม่ลบ |
| **7 Pull** | `docker pull <repo>@<digest>` → ตรวจ RepoDigests → logout และลบโฟลเดอร์ login | ดึงไม่ได้ → ร้านยังปิด |
| **8 Deploy** | ตรวจว่าไม่มี `catfood-web` ค้างและ port 3000 ว่าง → `docker run -p 3000:3000` จาก `<repo>@<digest>` → รอ `healthy` → เทียบ version/build/commit | ไม่ตรง → ล้ม |

stage **Push** ใช้สอง credential พร้อมกัน: รหัส SSH อยู่ใน `SSHPASS` ส่วน token ถูก `printf` ส่งเข้า stdin ของ `ssh` ไปถึง `docker login --password-stdin` บน devtools ทั้งคู่ไม่อยู่ใน command line · `disableConcurrentBuilds()` ห้ามสอง build ทำงานพร้อมกันเพราะใช้ชื่อ `catfood-web` และ port 3000 เดียวกัน · `post { unsuccessful }` ลบ container ทดสอบ โฟลเดอร์ login และซอร์สของ build ที่ล้ม **แต่ไม่แตะร้าน** · `always { deleteDir() }` ลบ workspace ของ Jenkins (มีแค่ `remote.sh`)

### Jenkinsfile ฉบับสมบูรณ์

เนื้อหาเดียวกับไฟล์ [`Jenkinsfile`](./Jenkinsfile) ในโฟลเดอร์นี้ทุกตัวอักษร คัดลอกทั้งบล็อกไปวางใน Jenkins

```groovy
{{jenkinsfile}}
```

### สร้าง job และ build แรก

1. Dashboard → **New Item** → ชื่อ `docker-build-push` → เลือก **Pipeline** → **OK**
2. หัวข้อ **Pipeline → Definition: Pipeline script** วาง Jenkinsfile ทั้งไฟล์ คง **Use Groovy Sandbox** ไว้ → **Save**
3. กด **Build Now** — job ใหม่ยังไม่มีปุ่ม **Build with Parameters** จนกว่าจะรันครั้งแรก build แรกจึงใช้ค่า default ทั้งหมด (`APP_VERSION=1.0.0`, tag `lab3-1`)

{{fig:pipeline_config}}

### ผลของ build #1 ทีละ stage

✅ **ผลจากรอบทดสอบ** (ตัดบรรทัด `[Pipeline]` ออก · รอบทดสอบใช้ `TAG_PREFIX` = `{{val:prefix}}` เพื่อไม่ทับ tag เดิมบน Docker Hub ของนักศึกษาจะเป็น `lab3-1` · ชื่อบัญชี Docker Hub แทนด้วย `<DOCKER_USER>`) build #1 `{{val:b1_result}}` ใน {{val:b1_duration}}

{{fig:build1_graph}}

**1 Connect** — Jenkins ไม่มี docker แต่สั่ง devtools ได้ด้วยรหัสผ่าน

```text
{{out:b1-connect}}
```

`{{val:jenkins_host}}` คือ container `jenkins` ส่วน `{{val:devtools_host}}` คือ `devtools` ตรงกับขั้นที่ 5 · บรรทัด `+ sshpass -e ssh ...` ไม่มีรหัสผ่านอยู่เลย เพราะรหัสอยู่ใน `SSHPASS`

{{fig:build1_connect}}

**2 Clone** — ซอร์สมาจาก GitHub ลงบน devtools

```text
{{out:b1-clone}}
```

**3 Build** — build จากซอร์สที่เพิ่ง clone (เลือกเฉพาะบรรทัดหลัก)

```text
{{out:b1-build}}
```

**4 Test** — แอปใน image ตอบ health และเวอร์ชัน/commit ถูกต้อง

```text
{{out:b1-test}}
```

**5 Push** — login ด้วย token แล้ว push และจด digest

```text
{{out:b1-push}}
```

`WARNING! Your credentials are stored unencrypted` หมายถึงไฟล์ login ในโฟลเดอร์ชั่วคราว `/tmp/lab3-docker-N` บน devtools ซึ่ง stage Pull (หรือ `post` เมื่อ build ล้ม) logout และลบทิ้ง token ไม่ปรากฏใน console

**6 Clean** — ลบ image ของ build นี้ก่อน Pull (เครื่องใหม่ยังไม่มีร้านเดิมให้ลบ)

```text
{{out:b1-clean}}
```

**7 Pull** — ดึงกลับจาก Docker Hub ตาม digest

```text
{{out:b1-pull}}
```

`Already exists` คือ layer ที่ยังค้างใน content store ของ Docker ข้างใน devtools ส่วนตัว image ถูกลบแล้วตามที่ Clean ตรวจ Docker จึงต้องขอ manifest จาก Docker Hub ตาม digest (`Downloaded newer image`) ก่อนประกอบ image กลับมา

**8 Deploy** — ร้านเปิดที่ port 3000 จาก image ที่ pull มา

```text
{{out:b1-deploy}}
```

เปิด `http://localhost:3000` บนเครื่องของเรา chip บนแถบด้านบนต้องเป็น `v1.0.0 · build #1`

---

## ขั้นที่ 8 — ออกเวอร์ชันใหม่ `APP_VERSION=1.1.0`

1. เปิด job `docker-build-push` → **Build with Parameters**
2. เปลี่ยนเฉพาะ `APP_VERSION` เป็น `1.1.0` → **Build**

{{fig:build_parameters}}

✅ **ผลจากรอบทดสอบ** build #2 `{{val:b2_result}}` ใน {{val:b2_duration}} — stage Clean ลบร้านของ build #1 (`{{val:b1_short}}` คือ digest 12 ตัวแรกของ build #1):

```text
{{out:b2-clean}}
```

Push, Pull และ Deploy ของ build #2 ใช้ digest เดียวกัน:

```text
{{out:b2-digest}}
```

{{fig:build2_clean_pull}}

{{fig:build2_deploy}}

เปิด `http://localhost:3000` chip บนแถบด้านบนต้องเป็น `v1.1.0 · build #2`

{{fig:app_v110}}

หน้า Tags บน Docker Hub ต้องมี tag ของ build #1 และ #2 ที่ digest ตรงกับ console:

{{fig:hub_tags}}

🔍 **สืบย้อน:** chip `v1.1.0 · build #2` → container `catfood-web` (`host` ใน `/api/health`) → `image: <repo>@sha256:...` ใน Deploy → digest ที่ Push จดไว้ → build #2 ของ Jenkins → `commit` จาก stage Clone

---

## ขั้นที่ 9 — ค่าผิด 3 แบบ แล้วดูว่าร้านเดิมยังอยู่

**(ก) ค่าที่แฝงคำสั่ง shell:** Build with Parameters กรอก `APP_VERSION` = `1.2.0; id` ถ้าค่านี้ไปถึง bash ของ devtools ตรง ๆ คำสั่ง `id` จะรันเป็น `root`

✅ **ผลจากรอบทดสอบ** (build #3 `{{val:b3_result}}` ใน {{val:b3_duration}}):

```text
{{out:b3}}
```

บรรทัด `+ sshpass` บรรทัดเดียวมาจาก `post { unsuccessful }` ซึ่งส่งแค่ชื่อ container และ path ของ build นี้ **ไม่มี SSH ใดที่ส่งค่า `1.2.0; id`**

{{fig:build3}}

**(ข) branch ที่ไม่มีอยู่จริง:** กรอก `GIT_REF` = `no-such-branch` (รูปแบบถูก จึงผ่าน Connect)

✅ **ผลจากรอบทดสอบ** (build #4 `{{val:b4_result}}` เฉพาะ Clone และ post):

```text
{{out:b4}}
```

{{fig:build4}}

**(ค) รหัสผ่าน SSH ผิด:** เปิด credential `devtools-ssh` → **Update** → เปลี่ยน Password เป็นค่าอื่น → **Save** แล้ว **Build Now**

✅ **ผลจากรอบทดสอบ** (build #5 `{{val:b5_result}}` เฉพาะ Connect และ post):

```text
{{out:b5}}
```

`sshpass` คืน exit code `5` เมื่อรหัสผ่านถูกปฏิเสธ build หยุดที่ Connect และ `post` ก็ SSH ไม่ได้เช่นกันจึงแจ้งให้เก็บกวาดเอง (ไม่มีอะไรค้างเพราะยังไม่เริ่ม Clone) **แก้ Password กลับเป็น `passwd` ก่อนทำต่อ**

{{fig:build5}}

หลัง build #3–#5 ตรวจจาก host ว่าร้านยังเป็น build #2 container เดิม:

{{block:check-web}}

```text
{{out:web-b5}}
```

🔍 **ตีความ:** ทั้งสาม build ล้ม **ก่อน Clean** ร้านเดิมจึงไม่ถูกแตะ และ `post` ลบเฉพาะของ build ที่ล้มเมื่อ SSH ได้

---

## ✅ ตรวจปิดแล็บ

- [ ] `docker exec jenkins sh -c "command -v docker || echo 'docker: none'"` ยังได้ `docker: none` และ `docker network inspect cicd-net` มีทั้ง `jenkins` และ `devtools`
- [ ] `docker exec jenkins ssh-keygen -lF devtools` ได้ fingerprint ตรงกับ `docker exec devtools ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`
- [ ] หน้า Credentials มี `devtools-ssh` (Username with password, `root`) และ `dockerhub`
- [ ] job `docker-build-push` build #1 และ #2 เป็น `SUCCESS` ครบ Connect → Clone → Build → Test → Push → Clean → Pull → Deploy
- [ ] stage Clean ของ build #2 มีบรรทัด `ลบแอปเดิม catfood-web (...)` และ Deploy แสดง `image: docker.io/<DOCKER_USER>/catfood-shop@sha256:...` ตรงกับ digest ใน Push
- [ ] หน้า Tags บน Docker Hub มี `lab3-1` และ `lab3-2` ที่ digest ตรงกับ console
- [ ] `http://localhost:3000` แสดง `v1.1.0 · build #2`
- [ ] build ที่ `APP_VERSION=1.2.0; id` ล้มที่ Connect, `GIT_REF=no-such-branch` ล้มที่ Clone และรหัสผ่าน SSH ผิดล้มที่ Connect โดยร้านยังเป็น build #2 และแก้รหัสกลับเป็น `passwd` แล้ว

## 📊 สรุปผลการทดสอบของเอกสารนี้

ทดสอบเมื่อ {{val:test_date}} บน Docker ของเครื่องทดสอบด้วยคำสั่งในขั้นที่ 1–5 ของเอกสารนี้ทุกตัวอักษร โดยรันใน container ชุดแยก (`devtools-lab003-…` + `jenkins-lab003-…` บน network แยก ตั้ง network alias `devtools` และ `jenkins` และ bind port ที่ `127.0.0.1`) ชื่อในผลลัพธ์ถูกแทนกลับเป็น `devtools` และ `jenkins` · Jenkins {{val:jenkins_version}} จาก `jenkins/jenkins:lts-jdk21` เปิด security (ผู้ดูแลทดสอบ รหัสสุ่ม) · push/pull กับ **Docker Hub จริง** · ขั้นที่ 2 ในรอบทดสอบติดตั้ง plugin ชุดเดียวกับ suggested plugins ที่แล็บใช้ผ่าน update center ของ Jenkins แทนการคลิกหน้า wizard

| รายการ | ผล |
|---|---|
| `jenkins` มี docker / docker.sock | ไม่มีทั้งคู่ (`docker CLI = none docker.sock = none`) มีเพียง `sshpass` |
| `jenkins` resolve `devtools` บน `cicd-net` | ได้ (Docker DNS) |
| SSH ไม่มี host key ใน `known_hosts` | ถูกปฏิเสธ `Host key verification failed.` ก่อนถามรหัส |
| SSH ด้วยรหัสผ่านหลัง pin host key | ผ่าน ไม่มีคำถาม `yes/no` |
| build #1 (`1.0.0`) | `{{val:b1_result}}` ครบ 8 stage ใน {{val:b1_duration}} · `{{val:b1_tag}}` · `{{val:b1_digest}}` |
| build #2 (`1.1.0`) | `{{val:b2_result}}` ใน {{val:b2_duration}} · Clean ลบร้าน build #1 และยืนยันว่าไม่มี image ตาม tag/digest ก่อน Pull · Push/Pull/Deploy ใช้ `{{val:b2_digest}}` เดียวกัน |
| build #3 (`1.2.0; id`) | `{{val:b3_result}}` ที่ Connect ร้านยังเป็น build #2 |
| build #4 (`GIT_REF=no-such-branch`) | `{{val:b4_result}}` ที่ Clone · post เก็บกวาดของ build #4 · ร้านยังเป็น build #2 |
| build #5 (รหัสผ่าน SSH ผิด) | `{{val:b5_result}}` ที่ Connect (`sshpass` exit 5) · ร้านยังเป็น build #2 · แก้รหัสกลับแล้ว |
| ความลับ | รหัส SSH, token และรหัสผู้ดูแลทดสอบไม่ปรากฏใน console, ไฟล์ผลทดสอบ และเอกสารนี้ |
{{cleanup_row}}

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `sshpass: not found` ใน Connect | ยังไม่ได้ทำขั้นที่ 3 หรือสร้าง `jenkins` ใหม่หลังติดตั้ง | รันขั้นที่ 3 ซ้ำ |
| `Could not resolve hostname devtools` | container ไม่ได้ชื่อ `devtools` หรือไม่ได้อยู่ใน `cicd-net` | `docker network inspect cicd-net` ต้องเห็นทั้ง `jenkins` และ `devtools` ถ้าไม่เห็นให้ `docker network connect cicd-net devtools` |
| `Host key verification failed.` | ยังไม่ได้ pin หรือ host key เปลี่ยน | รันขั้นที่ 4 ซ้ำ |
| `Permission denied, please try again.` และ `script returned exit code 5` | รหัสผ่านใน `devtools-ssh` ผิด | แก้ Password ของ credential เป็น `passwd` |
| `ERROR: Could not find credentials entry with ID ...` | ID สะกดไม่ตรง | ตั้ง ID เป็น `devtools-ssh` และ `dockerhub` ตรงตัว |
| `user=****` หรือ `/****/lab3-work` ใน console | ติ๊ก **Treat username as secret** ไว้ Jenkins จึงปิดบังคำว่า `root` | ไม่ผิด แต่เอาติ๊กออกเพื่อให้อ่าน log ง่าย |
| `username ใน credential dockerhub ไม่ถูกต้อง` | กรอกอีเมลหรือตัวพิมพ์ใหญ่ | ใช้ Docker Hub username ตัวพิมพ์เล็ก |
| `... ไม่ถูกต้อง: ...` ใน Connect | parameter ผิดรูปแบบ | แก้ค่าตามข้อความ (`X.Y.Z`, `https://...`, path แบบ relative) |
| `Remote branch ... not found` / `repository ... not found` ใน Clone | `GIT_REF` ไม่มี หรือ `GIT_URL` ผิด/เป็น private | เปิด URL ในเบราว์เซอร์ตรวจว่าเป็น Public และมี branch นั้น |
| stage Test ไม่ถึง `healthy` | แอปเริ่มไม่ขึ้น | `docker exec devtools docker run -d --name debug-shop catfood-shop:build-N` แล้ว `docker exec devtools docker logs debug-shop` (เสร็จแล้ว `docker exec devtools docker rm -f debug-shop`) |
| `unauthorized` / `denied` ใน Push หรือ Pull | token ผิด หมดอายุ หรือไม่มีสิทธิ์ Write | สร้าง token Read & Write ใหม่ แล้วแก้ credential `dockerhub` |
| `toomanyrequests` | Docker Hub rate limit | รอสักครู่แล้ว Build ใหม่ |
| `พบ container catfood-web ที่ไม่ได้สร้างโดย LAB 3` ใน Clean | มี `catfood-web` ที่สร้างเอง (ไม่มี label ของแล็บ) | `docker exec devtools docker inspect catfood-web` ถ้าไม่ใช้แล้วให้ลบเอง แล้ว Build ใหม่ |
| `port 3000 ถูก container อื่นใช้อยู่` ใน Deploy | มี container อื่นบน Docker ของ devtools publish 3000 | `docker exec devtools docker ps --filter publish=3000` ลบเฉพาะตัวที่ไม่ใช้แล้ว แล้ว Build ใหม่ |
| เปิด `localhost:3000` ไม่ได้ทั้งที่ Deploy เขียว | `devtools` ไม่ได้ publish `-p 3000:3000` | `docker port devtools` ถ้าไม่มี 3000 ให้ทำขั้นที่ 1 ใหม่ |

## 🧹 เก็บกวาด (🖥️ host)

**ห้ามลบ** `devtools`, `jenkins`, volume `jenkins_home`, network `cicd-net` และ credential ทั้งสอง แล็บถัดไปใช้ต่อ บล็อกนี้ลบเฉพาะ container และ image บน Docker ของ devtools ที่มี label `devtools.lab=lab3` ที่ Jenkinsfile ติดไว้ และซอร์ส/login ชั่วคราวที่อาจค้างเมื่อ build ถูกยกเลิกกลางทาง

{{block:cleanup}}
{{outblock:cleanup}}
เมื่อเลิกใช้แล้ว (เช่น จบรายวิชา) ให้ลบ credential `devtools-ssh` และ `dockerhub` ใน Jenkins และ revoke token ที่ Docker Hub → Personal access tokens · tag `lab3-N` บน Docker Hub ลบได้ที่หน้า Tags ของ repository

## กู้สถานะเมื่อปิดเครื่องหรือเริ่มระบบใหม่

ทั้งสอง container มี `--restart unless-stopped` จึงกลับมาเองเมื่อ Docker เริ่มใหม่ ถ้าไม่ขึ้นให้สั่ง `docker start devtools jenkins` ที่ host `catfood-web` ข้างใน devtools ก็มี `--restart unless-stopped` · `sshpass` อยู่ใน container `jenkins` และ `known_hosts` อยู่ใน volume `jenkins_home` จึงยังอยู่ครบ ต้องทำขั้นที่ 3 ซ้ำเฉพาะเมื่อลบแล้วสร้าง `jenkins` ใหม่ และขั้นที่ 4 เมื่อสร้าง `devtools` ใหม่จาก image อื่น

## 🤔 คำถามทบทวน

1. ถ้าสร้าง `devtools` โดยไม่ใส่ `--network cicd-net` stage ใดจะล้มก่อน และข้อความ error คืออะไร
2. ทำไมการคัดลอก host key ด้วย `docker cp` จึงเชื่อถือได้มากกว่าการตอบ `yes` ตอน SSH ครั้งแรก
3. ถ้ารหัสผ่านใน `devtools-ssh` รั่ว ผู้ที่ได้ไปทำอะไรได้บ้าง และระบบจริงควรเปลี่ยนอะไร
4. ทำไม Jenkinsfile ใช้ `sshpass -e` แทน `sshpass -p passwd` และใช้ `sh '...'` แทน `sh "..."`
5. ทำไม Clean ต้องเกิด **หลัง** Push สำเร็จ และทำไม Pull/Deploy ใช้ `repository@sha256:...` แทน `repository:tag`

➡️ **แล็บถัดไป:** [LAB 4 — Pipeline from Git](../004_LAB_Pipeline_From_Git/README.md)
