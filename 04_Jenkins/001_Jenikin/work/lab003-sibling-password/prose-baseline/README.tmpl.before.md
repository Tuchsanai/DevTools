# LAB 3 — Jenkins สั่ง devtools ผ่าน SSH: Connect → Clone → Build → Test → Push → Clean → Pull → Deploy ร้านอาหารแมว

> ⏱️ ประมาณ 50–60 นาที · 🧪 9 ขั้น · 🎯 จบเมื่อกด **Build** ใน Jenkins แล้ว `http://localhost:3000` แสดงร้าน **Meow Mart** เวอร์ชันที่ Pipeline เพิ่ง build → push ขึ้น Docker Hub → pull กลับตาม digest → deploy

บนเครื่องของเรามี container พี่น้อง (sibling) สองตัวบน network `cicd-net` คือ `jenkins` **ผู้สั่ง** กับ `devtools` **ผู้ทำ** Jenkins SSH ไปที่ `devtools:22` ด้วยรหัสผ่านจาก Jenkins Credentials แล้วส่งสคริปต์ไปรันทีละ stage คำสั่ง `git clone` และ `docker build/run/push/pull` ทั้งหมดจึงรันบน `devtools` และร้านเปิดเป็น container `catfood-web` บน Docker ข้างใน `devtools`

> **กติกา:** ไม่พิมพ์ `docker build`, `docker push` หรือ `git clone` ของร้านเอง ทุกอย่างเริ่มจากปุ่มบน Jenkins · `jenkins` เป็น image มาตรฐาน `jenkins/jenkins:lts-jdk21` **ไม่มี Docker CLI และไม่ mount `docker.sock`** (เพิ่มเพียง `sshpass`)

{{fig:diagram_architecture}}

| container | อยู่บน Docker ของ | เข้าจากเครื่องเราทาง |
|---|---|---|
| `jenkins` | เครื่องของเรา (network `cicd-net`) | `localhost:8080` |
| `devtools` (`--privileged` มี Docker ของตัวเอง) | เครื่องของเรา (network `cicd-net`) | `localhost:2222` → SSH · `localhost:3000` → ร้าน |
| `catfood-test-N` (ชั่วคราว) และ `catfood-web` (ร้าน) | **ข้างใน** `devtools` | `localhost:3000` → `devtools:3000` → `catfood-web:3000` |

- Docker DNS ของ `cicd-net` แปลชื่อ container เป็น IP Jenkinsfile จึงเขียน `root@devtools` ได้ตรง ๆ
- credential `devtools-ssh` เก็บ `root` / `passwd` (รหัสตั้งต้นของ image แล็บนี้เท่านั้น) Jenkinsfile เรียก `sshpass -e ssh -o StrictHostKeyChecking=yes ...` รหัสอยู่ในตัวแปร `SSHPASS` ไม่อยู่ใน command line หรือ console และ SSH ต่อเฉพาะเมื่อ host key ของ `devtools` ตรงกับที่ pin ไว้ในขั้นที่ 4
- Push จด **digest** (`sha256:...`) ไว้ Pull และ Deploy ใช้ `repository@sha256:...` ตัวเดียวกัน · **Clean** ทำหลัง Push สำเร็จเท่านั้น และลบเฉพาะของที่มี label `devtools.lab=lab3` · ตั้งแต่ Clean ถึง Deploy ร้านปิดชั่วคราว (รอบทดสอบ {{val:b2_downtime}}) ไม่มี rollback อัตโนมัติ

> ⚠️ `root` บน `devtools` แบบ `--privileged` สั่ง Docker ของ devtools ได้ทุกอย่าง ใช้รหัสนี้กับแล็บที่ลบทิ้งได้เท่านั้น ระบบจริงใช้ SSH key หรือ build agent ที่ไม่ใช่ `root`

{{fig:diagram_pipeline}}

## 0. สิ่งที่ต้องมี

- terminal บนเครื่องที่สั่ง `docker` ได้ (Linux, macOS หรือ WSL) เรียกว่า 🖥️ **host** ทุกคำสั่ง `docker` ในแล็บนี้พิมพ์ที่ host และ port `8080`, `2222`, `3000` ว่าง
- บัญชี Docker Hub และ **Personal Access Token สิทธิ์ Read & Write** (Account settings → Personal access tokens) แนะนำให้สร้าง repository `catfood-shop` แบบ **Public**

{{fig:hub_pat}}

stage Clone ดึงซอร์สร้านจากโฟลเดอร์นี้ใน repository สาธารณะของรายวิชา:

{{fig:github_source}}

> ผลลัพธ์ตัวอย่างในเอกสารมาจากการรันจริงหนึ่งรอบ ID, hostname, เวลา และ digest ของแต่ละเครื่องจะต่างกัน รอบทดสอบใช้ `TAG_PREFIX` = `{{val:prefix}}` (ของนักศึกษาเป็น `lab3`) และแทนชื่อบัญชี Docker Hub ด้วย `<DOCKER_USER>` · ภาพหน้าจอทุกภาพคลิกเพื่อเปิดภาพเต็มได้

## ขั้นที่ 1 — สร้าง network และ container สองตัว (🖥️ host)

{{block:host-setup}}

- `docker rm -f` ลบ `jenkins`/`devtools` เดิม ถ้ายังไม่มี container ชื่อนั้นจะขึ้น `Error response from daemon: No such container: ...` ไม่เป็นไร ทำต่อได้ · ⚠️ ของข้างใน `devtools` เดิม รวม Jenkins ของ LAB 1–2 จะหายไป
- ถ้า `docker network create` ขึ้น `already exists` ใช้ network เดิมต่อได้
- `--privileged --tmpfs /run` ให้ Docker ข้างใน `devtools` ทำงานและบูตใหม่ได้ · `-v jenkins_home:...` เก็บสถานะ Jenkins ใน volume

✅ ผลที่ได้ (ID ของ network, `devtools`, `jenkins`):

```text
{{out:host-setup}}
```

ตรวจว่าทั้งคู่ `Up` และอยู่ใน `cicd-net`:

{{block:host-check}}

```text
{{out:host-check}}
```

> รอบทดสอบ bind port ที่ `127.0.0.1` ด้วยเลขอื่น ของนักศึกษาจะเห็น `0.0.0.0:8080->8080/tcp`, `0.0.0.0:2222->22/tcp`, `0.0.0.0:3000->3000/tcp`

## ขั้นที่ 2 — ปลดล็อกและตั้งค่า Jenkins

{{block:unlock}}

✅ ได้รหัสเลขฐานสิบหก 32 ตัว (ของแต่ละเครื่องต่างกัน ห้ามเผยแพร่) เปิด **http://localhost:8080** วางรหัส → **Continue** → **Install suggested plugins** → สร้างผู้ดูแล `admin` / `admin2569` → Jenkins URL `http://localhost:8080/` → **Save and Finish** → **Start using Jenkins** (รายละเอียดแต่ละหน้าอยู่ใน [LAB 1](../001_LAB_Jenkins_On_Docker/README.md)) ถ้า volume `jenkins_home` มีอยู่แล้วจากครั้งก่อน Jenkins จะไม่ถามรหัสนี้ ให้ login ด้วยผู้ดูแลเดิม

{{fig:unlock}}

{{fig:dashboard}}

## ขั้นที่ 3 — ติดตั้ง `sshpass` ใน `jenkins` (🖥️ host)

{{block:sshpass}}

`-u root` เพราะ `apt-get` ต้องใช้ root (Jenkins เองยังรันเป็นผู้ใช้ `jenkins`) · ติดตั้งลง container ไม่ได้แก้ image ถ้าสร้าง `jenkins` ใหม่ต้องรันขั้นนี้ซ้ำ

✅ ส่วนท้ายของผล — มี `sshpass` และ Jenkins **ไม่มี** Docker CLI:

```text
{{out:sshpass-tail}}
```

## ขั้นที่ 4 — pin host key ของ `devtools` (🖥️ host)

{{block:pin-hostkey}}

บรรทัดแรกสร้างบรรทัด `known_hosts` จาก host key ของ `devtools` เอง สองบรรทัดถัดมาคัดลอกผ่านเครื่องเราด้วย `docker cp` บรรทัดที่ 4 ให้ผู้ใช้ `jenkins` วางเป็น `/var/jenkins_home/.ssh/known_hosts` (อยู่ใน volume จึงคงอยู่) สองบรรทัดสุดท้ายแสดง fingerprint ต้นทางกับที่ Jenkins บันทึก

✅ `SHA256:...` สองบรรทัดต้องเหมือนกัน:

```text
{{out:pin-hostkey}}
```

> การ pin ทำให้ SSH เทียบ key ของเครื่องปลายทางกับ key ของ `devtools` ที่เราคาดไว้ ถ้าไม่ตรงหรือไม่มีจะหยุดก่อนส่งรหัสผ่าน แต่ host key นี้ติดมากับ image `tuchsanai/devtools:2569_1` (`root@buildkitsandbox`) ทุก container ที่สร้างจาก image นี้จึงได้ key เดียวกัน ไม่ใช่ตัวตนเฉพาะเครื่อง · ไฟล์ `devtools.known_hosts` ในโฟลเดอร์ปัจจุบันเป็น public key ลบได้

## ขั้นที่ 5 — ทดสอบ SSH ด้วยรหัสผ่าน (🖥️ host)

{{block:ssh-test}}

พิมพ์ `passwd` เมื่อถูกถาม (ตัวอักษรไม่แสดง) แล้วกด Enter

✅ บรรทัดสุดท้ายคือ hostname ของ `devtools` และ **ไม่มี** คำถาม `yes/no`:

```text
{{out:ssh-test}}
```

ถ้าไม่มี key ของ `devtools` ใน `known_hosts` SSH จะปฏิเสธก่อนถามรหัส (รอบทดสอบลองด้วย `known_hosts` ว่าง):

```text
{{out:unpinned}}
```

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

{{fig:ssh_credential_id}}

{{fig:credentials}}

> ⚠️ วาง token ที่ Jenkins Credentials เท่านั้น ห้ามวางในแชต เอกสาร หรือ commit ลง Git

## ขั้นที่ 7 — สร้าง job แล้ว Build Now

Pipeline อยู่ในไฟล์ [`Jenkinsfile`](./Jenkinsfile) ของโฟลเดอร์นี้ ทุก stage ที่ทำงานบน devtools เรียกฟังก์ชัน `onDevtools(ตัวแปร, สคริปต์)`:

```groovy
writeFile file: 'remote.sh', text: lines.join('\n') + '\n' + body + '\n'
withCredentials([usernamePassword(credentialsId: 'devtools-ssh',
                 usernameVariable: 'SSH_USER', passwordVariable: 'SSHPASS')]) {
  out = sh(script: 'sshpass -e ssh -o StrictHostKeyChecking=yes -o PreferredAuthentications=password "$SSH_USER@devtools" bash -s < remote.sh',
           returnStdout: capture)
}
```

- สคริปต์ของแต่ละ stage เขียนใน `'''...'''` Groovy จึงไม่แทนค่า `$` และสคริปต์เดินทางทาง stdin ของ SSH ไปรันด้วย bash บน devtools
- ค่า parameter ถูกตรวจด้วย regex ก่อน แล้วเขียนเป็นบรรทัด `NAME='value'` ต้น `remote.sh` (ยอมเฉพาะ `A-Za-z0-9._:/@=+-`) ค่าที่แฝงคำสั่ง shell จึงไปไม่ถึง devtools
- `sh(script: '...')` เป็นข้อความคงที่ `$SSH_USER` ถูกแทนค่าโดย shell ของ Jenkins · stage Push ส่ง Docker Hub token ทาง stdin ไปที่ `docker login --password-stdin` บน devtools

| Stage | ทำอะไร (บน devtools ยกเว้นระบุ) |
|---|---|
| **1 Connect** | บน Jenkins: ตรวจ parameter และ username Docker Hub สร้าง tag `<TAG_PREFIX>-<BUILD_NUMBER>` แล้ว SSH ไปถาม hostname, Docker, git ของ devtools |
| **2 Clone** | sparse clone `GIT_URL`@`GIT_REF` ลง `/root/lab3-work/build-N` เก็บ commit |
| **3 Build** | `docker build` → `catfood-shop:build-N` พร้อม label และ build-arg เวอร์ชัน/build/commit/เวลา |
| **4 Test** | รัน `catfood-test-N` รอ `healthy` ตรวจ `/api/health` แล้วลบทิ้ง |
| **5 Push** | login ด้วย token → push → จด digest |
| **6 Clean** | ลบ container ทดสอบ **ร้านเดิม** image ของ build นี้ และซอร์ส แล้วยืนยันว่าไม่เหลือ image ตาม tag/digest (หยุดถ้า `catfood-web` ไม่ใช่ของแล็บ) |
| **7 Pull** | `docker pull <repo>@<digest>` แล้ว logout |
| **8 Deploy** | `docker run -p 3000:3000` จาก `<repo>@<digest>` → รอ `healthy` → เทียบ version/build/commit |

build ที่ล้มก่อน Clean ไม่แตะร้านเดิม · `post { unsuccessful }` ลบของชั่วคราวของ build ที่ล้มแต่ไม่แตะร้าน · `disableConcurrentBuilds()` กันสอง build ใช้ `catfood-web`/port 3000 พร้อมกัน

<details>
<summary><b>Jenkinsfile ฉบับสมบูรณ์</b> (เหมือนไฟล์ <code>Jenkinsfile</code> ทุกตัวอักษร คลิกเพื่อเปิด)</summary>

```groovy
{{jenkinsfile}}
```

</details>

1. Dashboard → **New Item** → ชื่อ `docker-build-push` → **Pipeline** → **OK**
2. **Pipeline → Definition: Pipeline script** วาง Jenkinsfile ทั้งไฟล์ คง **Use Groovy Sandbox** → **Save**
3. กด **Build Now** — job ใหม่ยังไม่มีปุ่ม **Build with Parameters** จนกว่าจะรันครั้งแรก build แรกจึงใช้ค่า default (`APP_VERSION=1.0.0`, tag `lab3-1`)

{{fig:pipeline_config}}

✅ build #1 `{{val:b1_result}}` ครบ 8 stage ใน {{val:b1_duration}}:

{{fig:build1_graph}}

stage **Connect** ยืนยันว่า Jenkins ไม่มี docker แต่สั่ง devtools ได้ บรรทัด `+ sshpass -e ssh ...` ไม่มีรหัสผ่านเพราะรหัสอยู่ใน `SSHPASS`:

{{fig:build1_connect}}

{{fig:build1_connect_ssh}}

stage **Push** และ **Deploy** ของ build #1:

```text
{{out:b1-push-digest}}
```

เปิด `http://localhost:3000` chip บนแถบด้านบนต้องเป็น `v1.0.0 · build #1`

## ขั้นที่ 8 — ออกเวอร์ชันใหม่ `APP_VERSION=1.1.0`

job `docker-build-push` → **Build with Parameters** → เปลี่ยนเฉพาะ `APP_VERSION` เป็น `1.1.0` → **Build**

{{fig:build_parameters}}

✅ build #2 `{{val:b2_result}}` ใน {{val:b2_duration}} ดู log ของแต่ละ stage ได้โดยเลือก stage ทางซ้ายของหน้า build:

{{fig:build2_clone}}

{{fig:build2_build}}

{{fig:build2_test}}

{{fig:build2_push}}

{{fig:build2_clean}}

{{fig:build2_pull}}

{{fig:build2_deploy}}

Push, Pull และ Deploy ของ build #2 ใช้ digest เดียวกัน:

```text
{{out:b2-digest}}
```

เปิด `http://localhost:3000` chip ต้องเป็น `v1.1.0 · build #2`:

{{fig:app_v110}}

{{fig:app_deployment}}

หน้า Tags บน Docker Hub มี tag ของ build #1 และ #2 ที่ digest ตรงกับ console:

{{fig:hub_tags}}

🔍 **สืบย้อน:** chip `v1.1.0 · build #2` → Container ใน Deployment info (`host` ใน `/api/health`) → `image: <repo>@sha256:...` ใน Deploy → digest ที่ Push จด → build #2 → commit จาก Clone

## ขั้นที่ 9 — ค่าผิด 3 แบบ ร้านเดิมต้องยังอยู่

**(ก)** Build with Parameters กรอก `APP_VERSION` = `1.2.0; id` → build #3 `{{val:b3_result}}` ที่ Connect ก่อน SSH ใด ๆ ส่งค่านี้ (SSH ครั้งเดียวที่เกิดมาจาก `post` ซึ่งส่งเพียงชื่อ container และ path ของ build นี้)

```text
{{out:b3}}
```

{{fig:build3}}

**(ข)** กรอก `GIT_REF` = `no-such-branch` (รูปแบบถูก จึงผ่าน Connect) → build #4 `{{val:b4_result}}` ที่ Clone

{{fig:build4}}

**(ค)** credential `devtools-ssh` → **Update** → **Change Password** เป็นค่าอื่น → **Save** แล้ว **Build Now** → build #5 `{{val:b5_result}}` ที่ Connect (`sshpass` คืน exit code 5 เมื่อรหัสผ่านถูกปฏิเสธ) **แล้วแก้ Password กลับเป็น `passwd`**

{{fig:build5}}

ตรวจจาก host ว่าร้านยังเป็น build #2 container เดิม:

{{block:check-web}}

```text
{{out:web-b5}}
```

ทั้งสาม build ล้ม **ก่อน Clean** ร้านเดิมจึงไม่ถูกแตะ

## ✅ ตรวจปิดแล็บ

- [ ] `docker exec jenkins sh -c "command -v docker || echo 'docker: none'"` ได้ `docker: none` และ `docker network inspect cicd-net` มีทั้ง `jenkins` และ `devtools`
- [ ] `docker exec jenkins ssh-keygen -lF devtools` ได้ fingerprint ตรงกับ `docker exec devtools ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`
- [ ] Credentials มี `devtools-ssh` (`root`) และ `dockerhub`
- [ ] build #1 และ #2 `SUCCESS` ครบ 8 stage · Clean ของ #2 มี `ลบแอปเดิม catfood-web (...)` · digest ใน Push, Pull, Deploy ตรงกัน
- [ ] หน้า Tags บน Docker Hub มี `lab3-1` และ `lab3-2` · `http://localhost:3000` แสดง `v1.1.0 · build #2`
- [ ] build ของขั้นที่ 9 ล้มตามที่คาด ร้านยังเป็น build #2 และแก้รหัส `devtools-ssh` กลับเป็น `passwd` แล้ว

## แก้ปัญหาที่พบบ่อย

| อาการ | วิธีแก้ |
|---|---|
| `sshpass: not found` ใน Connect | รันขั้นที่ 3 ซ้ำ (เกิดเมื่อสร้าง `jenkins` ใหม่) |
| `Could not resolve hostname devtools` | `docker network inspect cicd-net` ต้องเห็นทั้งสองตัว ถ้าไม่เห็นให้ `docker network connect cicd-net devtools` |
| `Host key verification failed.` | ยังไม่ได้ pin หรือสร้าง `devtools` ใหม่จาก image อื่น → รันขั้นที่ 4 ซ้ำ |
| `Permission denied, please try again.` / `exit code 5` | แก้ Password ของ `devtools-ssh` เป็น `passwd` |
| `Could not find credentials entry with ID ...` | ตั้ง ID เป็น `devtools-ssh` และ `dockerhub` ตรงตัว |
| `user=****` หรือ `/****/lab3-work` ใน console | เอาติ๊ก **Treat username as secret** ของ `devtools-ssh` ออก |
| `... ไม่ถูกต้อง: ...` ใน Connect | แก้ parameter ตามข้อความ (`X.Y.Z`, `https://...`, username Docker Hub ตัวพิมพ์เล็ก) |
| `Remote branch ... not found` ใน Clone | ตรวจ `GIT_REF`/`GIT_URL` ว่ามีจริงและเป็น Public |
| `unauthorized` / `denied` ใน Push หรือ Pull | token ผิด หมดอายุ หรือไม่มีสิทธิ์ Write → สร้างใหม่แล้วแก้ `dockerhub` |
| `พบ container catfood-web ที่ไม่ได้สร้างโดย LAB 3` / `port 3000 ถูก container อื่นใช้อยู่` | `docker exec devtools docker ps -a` ลบเฉพาะตัวที่ไม่ใช้แล้ว แล้ว Build ใหม่ |
| เปิด `localhost:3000` ไม่ได้ทั้งที่ Deploy เขียว | `docker port devtools` ถ้าไม่มี 3000 ให้ทำขั้นที่ 1 ใหม่ |

## 🧹 เก็บกวาด (🖥️ host)

**ห้ามลบ** `devtools`, `jenkins`, volume `jenkins_home`, network `cicd-net` และ credential ทั้งสอง แล็บถัดไปใช้ต่อ บล็อกนี้ลบเฉพาะ container/image ที่มี label `devtools.lab=lab3` บน Docker ของ devtools และไฟล์ชั่วคราวของแล็บ:

{{block:cleanup}}

เมื่อจบรายวิชา ลบ credential ทั้งสองใน Jenkins และ revoke token ที่ Docker Hub · หลังเปิดเครื่องใหม่ container ทั้งหมด (รวม `catfood-web`) กลับมาเองเพราะ `--restart unless-stopped` ถ้าไม่ขึ้นให้ `docker start devtools jenkins`

## 🤔 คำถามทบทวน

1. ถ้าสร้าง `devtools` โดยไม่ใส่ `--network cicd-net` stage ใดจะล้มก่อน และ error คืออะไร
2. การ pin host key ป้องกันอะไรได้ และทำไม fingerprint ของทุกคนในห้องจึงเหมือนกัน
3. ทำไม Jenkinsfile ใช้ `sshpass -e` แทน `sshpass -p passwd` และใช้ `sh '...'` แทน `sh "..."`
4. ทำไม Clean ต้องเกิด **หลัง** Push สำเร็จ และทำไม Pull/Deploy ใช้ `repository@sha256:...` แทน `repository:tag`

เอกสารนี้ทดสอบจริงครบทุกขั้นแล้ว ดู [รายงานผลทดสอบ](./LAB003_FINAL_REPORT.md)

➡️ **แล็บถัดไป:** [LAB 4 — Pipeline from Git](../004_LAB_Pipeline_From_Git/README.md)
