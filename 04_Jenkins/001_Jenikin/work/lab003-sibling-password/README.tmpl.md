# LAB 3 — Jenkins สั่ง devtools ผ่าน SSH: Connect → Clone → Build → Test → Push → Clean → Pull → Deploy ร้านอาหารแมว

> ⏱️ ประมาณ 50–60 นาที · 🧪 9 ขั้น · 🎯 จบเมื่อกด **Build** ใน Jenkins แล้ว `http://localhost:3000` แสดงร้าน **Meow Mart** เวอร์ชันที่ Pipeline เพิ่ง build → push ขึ้น Docker Hub → pull กลับตาม digest → deploy

## ภาพรวม

แล็บนี้ใช้ container สองตัวแทน **server สองเครื่อง** บน network `cicd-net`:

- **`jenkins`** — ควบคุม Pipeline ไม่มี Docker CLI และไม่ mount `docker.sock` (เพิ่มแค่ `sshpass`)
- **`devtools`** — รับคำสั่งจาก Jenkins ทาง SSH แล้วรัน `git clone` และคำสั่ง Docker ทุกคำสั่งของ Pipeline

image ที่ build ได้ถูก push ไปเก็บที่ **Docker Hub** แล้ว pull กลับมา deploy เป็นร้าน `catfood-web` ซึ่งรันบน Docker **ข้างใน devtools** ไม่ใช่ใน Jenkins (`docker push`/`pull` ก็รันบน devtools)

> **กติกา:** ห้ามพิมพ์ `docker build`, `docker push` หรือ `git clone` ของร้านเอง ทุกอย่างต้องเริ่มจากปุ่มใน Jenkins

{{fig:diagram_architecture}}

| container | รันอยู่บน | เข้าจากเครื่องเราทาง |
|---|---|---|
| `jenkins` | เครื่องของเรา (network `cicd-net`) | `localhost:8080` |
| `devtools` (`--privileged` มี Docker ของตัวเอง) | เครื่องของเรา (network `cicd-net`) | `localhost:2222` → SSH · `localhost:3000` → ร้าน |
| `catfood-test-N` (ชั่วคราว) และ `catfood-web` (ร้าน) | Docker **ข้างใน** `devtools` | `localhost:3000` → `devtools:3000` → `catfood-web:3000` |

> ⚠️ `root` บน `devtools` สั่ง Docker ของ devtools ได้ทุกอย่าง ใช้รหัสผ่านนี้กับแล็บที่ลบทิ้งได้เท่านั้น ระบบจริงควรใช้ SSH key หรือ build agent ที่ไม่ใช่ `root`

{{fig:diagram_pipeline}}

## 0. สิ่งที่ต้องมี

- terminal ที่ใช้ `docker` ได้ (Linux, macOS หรือ WSL) เรียกว่า 🖥️ **host** · คำสั่งที่มีป้าย 🖥️ host คือคำสั่ง**เตรียมแล็บ**ที่เราพิมพ์เอง ส่วนคำสั่ง Git/Docker ของแอปใน Pipeline นั้น Jenkins ส่งผ่าน SSH ไป**รันใน `devtools`**
- port `8080`, `2222`, `3000` ต้องว่าง
- บัญชี Docker Hub และ **Personal Access Token สิทธิ์ Read & Write** (Account settings → Personal access tokens) แนะนำให้สร้าง repository `catfood-shop` แบบ **Public** ไว้ก่อน

{{fig:hub_pat}}

stage Clone ดึงซอร์สร้านจากโฟลเดอร์นี้ใน repository ของรายวิชา:

{{fig:github_source}}

> ผลลัพธ์ในเอกสารมาจากการรันจริง ID, hostname, เวลา และ digest ของแต่ละเครื่องจะต่างกัน · รอบทดสอบใช้ `TAG_PREFIX` = `{{val:prefix}}` (ของนักศึกษาเป็น `lab3`) · `<DOCKER_USER>` คือชื่อบัญชี Docker Hub · คลิกภาพเพื่อดูภาพเต็ม

## ขั้นที่ 1 — สร้าง network และ container สองตัว (🖥️ host)

{{block:host-setup}}

- `docker rm -f` ลบ `jenkins`/`devtools` ตัวเดิม ถ้าขึ้น `No such container` ทำต่อได้ · ⚠️ ของใน `devtools` ตัวเดิม รวม Jenkins ของ LAB 1–2 จะหายไป
- `docker network create` ขึ้น `already exists` ใช้ network เดิมได้ · บน `cicd-net` Jenkins เรียก `devtools` ด้วยชื่อได้เลย
- `--privileged --tmpfs /run` ให้ Docker ข้างใน `devtools` ทำงานได้ · volume `jenkins_home` เก็บข้อมูล Jenkins

✅ ผลที่ได้ (ID ของ network, `devtools`, `jenkins`):

```text
{{out:host-setup}}
```

ตรวจว่าทั้งสองตัว `Up` และอยู่ใน `cicd-net`:

{{block:host-check}}

```text
{{out:host-check}}
```

> รอบทดสอบใช้ port อื่นบน `127.0.0.1` ของนักศึกษาจะเห็น `0.0.0.0:8080->8080/tcp`, `0.0.0.0:2222->22/tcp`, `0.0.0.0:3000->3000/tcp`

## ขั้นที่ 2 — ปลดล็อกและตั้งค่า Jenkins

{{block:unlock}}

✅ ได้รหัสเลขฐานสิบหก 32 ตัว (ห้ามเผยแพร่)

เปิด **http://localhost:8080** วางรหัส → **Continue** → **Install suggested plugins** → สร้างผู้ดูแล `admin` / `admin2569` → Jenkins URL `http://localhost:8080/` → **Save and Finish** → **Start using Jenkins** (ภาพทีละหน้าดูใน [LAB 1](../001_LAB_Jenkins_On_Docker/README.md)) · ถ้า volume `jenkins_home` มีอยู่แล้ว ให้ login ด้วยผู้ดูแลเดิม

{{fig:unlock}}

{{fig:dashboard}}

## ขั้นที่ 3 — ติดตั้ง `sshpass` ใน `jenkins` (🖥️ host)

{{block:sshpass}}

`-u root` จำเป็นสำหรับ `apt-get` · ถ้าสร้าง `jenkins` ใหม่ต้องรันขั้นนี้อีกครั้ง

✅ ท้ายผลลัพธ์ต้องมี `sshpass` และ Jenkins **ไม่มี** Docker CLI:

```text
{{out:sshpass-tail}}
```

## ขั้นที่ 4 — pin host key ของ `devtools` (🖥️ host)

บอก Jenkins ล่วงหน้าว่า `devtools` ตัวจริงมี key นี้ SSH จะได้ไม่ต่อผิดเครื่อง

{{block:pin-hostkey}}

อ่าน host key จาก `devtools` → `docker cp` ผ่านเครื่องเรา → วางเป็น `/var/jenkins_home/.ssh/known_hosts` ของผู้ใช้ `jenkins` → แสดง fingerprint สองฝั่ง

✅ `SHA256:...` สองบรรทัดต้องเหมือนกัน:

```text
{{out:pin-hostkey}}
```

> ถ้า key ไม่ตรงหรือไม่มี SSH จะหยุดก่อนส่งรหัสผ่าน · key นี้ติดมากับ image `tuchsanai/devtools:2569_1` ทุก container จาก image นี้จึงได้ key เดียวกัน ไม่ใช่ตัวตนเฉพาะเครื่อง · ไฟล์ `devtools.known_hosts` ที่เหลือเป็น public key ลบได้

## ขั้นที่ 5 — ทดสอบ SSH ด้วยรหัสผ่าน (🖥️ host)

{{block:ssh-test}}

พิมพ์ `passwd` เมื่อถูกถาม (ตัวอักษรจะไม่แสดง) แล้วกด Enter

✅ บรรทัดสุดท้ายเป็น hostname ของ `devtools` และ **ไม่มี** คำถาม `yes/no`:

```text
{{out:ssh-test}}
```

ถ้า `known_hosts` ไม่มี key ของ `devtools` SSH จะปฏิเสธก่อนถามรหัส:

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

`passwd` เป็นรหัสตั้งต้นของ image แล็บนี้เท่านั้น

{{fig:ssh_credential}}

{{fig:ssh_credential_id}}

{{fig:credentials}}

> ⚠️ วาง token ใน Jenkins Credentials เท่านั้น ห้ามวางในแชต เอกสาร หรือ commit ลง Git

## ขั้นที่ 7 — สร้าง job แล้ว Build Now

Pipeline อยู่ใน [`Jenkinsfile`](./Jenkinsfile) ทุก stage (ยกเว้นส่วนแรกของ Connect) รันบน devtools ผ่าน SSH:

| Stage | ทำอะไร (บน devtools ยกเว้นที่ระบุ) |
|---|---|
| **1 Connect** | บน Jenkins: ตรวจ parameter และ username Docker Hub สร้าง tag `<TAG_PREFIX>-<BUILD_NUMBER>` แล้ว SSH ไปถาม hostname, Docker, git ของ devtools |
| **2 Clone** | sparse clone `GIT_URL`@`GIT_REF` ลง `/root/lab3-work/build-N` และจด commit |
| **3 Build** | `docker build` → `catfood-shop:build-N` พร้อม label และ build-arg เวอร์ชัน/build/commit/เวลา |
| **4 Test** | รัน `catfood-test-N` รอ `healthy` ตรวจ `/api/health` แล้วลบทิ้ง |
| **5 Push** | login ด้วย token → push → จด digest |
| **6 Clean** | ลบ container ทดสอบ **ร้านเดิม** image ของ build นี้ และซอร์ส แล้วตรวจว่าไม่เหลือ image ตาม tag/digest (หยุดถ้า `catfood-web` ไม่ใช่ของแล็บ) |
| **7 Pull** | `docker pull <repo>@<digest>` แล้ว logout |
| **8 Deploy** | `docker run -p 3000:3000` จาก `<repo>@<digest>` → รอ `healthy` → เทียบ version/build/commit |

Clean ทำหลัง Push สำเร็จเท่านั้น ถ้าล้มก่อนนั้นร้านเดิมไม่ถูกแตะ · ช่วง Clean ถึง Deploy ร้านปิดชั่วคราว (รอบทดสอบ {{val:b2_downtime}}) และไม่มี rollback อัตโนมัติ

<details>
<summary><b>Jenkins ส่งคำสั่งไป devtools อย่างไร</b> (คลิกเพื่อเปิด)</summary>

ฟังก์ชัน `onDevtools(ตัวแปร, สคริปต์)` เขียนสคริปต์ของ stage เป็น `remote.sh` แล้วส่งทาง SSH:

```groovy
writeFile file: 'remote.sh', text: lines.join('\n') + '\n' + body + '\n'
withCredentials([usernamePassword(credentialsId: 'devtools-ssh',
                 usernameVariable: 'SSH_USER', passwordVariable: 'SSHPASS')]) {
  out = sh(script: 'sshpass -e ssh -o StrictHostKeyChecking=yes -o PreferredAuthentications=password "$SSH_USER@devtools" bash -s < remote.sh',
           returnStdout: capture)
}
```

- `sshpass -e` อ่านรหัสจากตัวแปร `SSHPASS` รหัสจึงไม่โผล่ใน command line หรือ console · `sh(script: '...')` เป็นข้อความคงที่ `$SSH_USER` จึงถูกแทนค่าโดย shell ไม่ใช่ Groovy · SSH ต่อเฉพาะเมื่อ host key ตรงกับที่ pin ในขั้นที่ 4
- สคริปต์อยู่ใน `'''...'''` Groovy จึงไม่แทนค่า `$` เอง แล้วส่งทาง stdin ไปรันด้วย bash บน devtools
- parameter ถูกตรวจด้วย regex (ยอมเฉพาะ `A-Za-z0-9._:/@=+-`) แล้วเขียนเป็น `NAME='value'` ต้น `remote.sh` ค่าที่แฝงคำสั่ง shell จึงไปไม่ถึง devtools
- Push ส่ง token ทาง stdin ให้ `docker login --password-stdin` บน devtools แล้วจด **digest** ให้ Pull/Deploy ใช้ `repository@sha256:...` ตัวเดียวกัน
- Clean ลบเฉพาะของที่มี label `devtools.lab=lab3` · `post { unsuccessful }` ลบของชั่วคราวของ build ที่ล้มโดยไม่แตะร้าน · `disableConcurrentBuilds()` กันสอง build ใช้ port 3000 พร้อมกัน

</details>

<details>
<summary><b>Jenkinsfile ฉบับสมบูรณ์</b> (เหมือนไฟล์ <code>Jenkinsfile</code> ทุกตัวอักษร คลิกเพื่อเปิด)</summary>

```groovy
{{jenkinsfile}}
```

</details>

1. Dashboard → **New Item** → ชื่อ `docker-build-push` → **Pipeline** → **OK**
2. **Pipeline → Definition: Pipeline script** วาง Jenkinsfile ทั้งไฟล์ เปิด **Use Groovy Sandbox** ไว้ → **Save**
3. กด **Build Now** — job ใหม่ยังไม่มี **Build with Parameters** จนกว่าจะรันครั้งแรก build แรกจึงใช้ค่า default (`APP_VERSION=1.0.0`, tag `lab3-1`)

{{fig:pipeline_config}}

✅ build #1 `{{val:b1_result}}` ครบ 8 stage ใน {{val:b1_duration}}:

{{fig:build1_graph}}

stage **Connect** ยืนยันว่า Jenkins ไม่มี docker แต่สั่ง devtools ได้ · บรรทัด `+ sshpass -e ssh ...` ไม่มีรหัสผ่าน:

{{fig:build1_connect}}

{{fig:build1_connect_ssh}}

ผลของ stage **Push** และ **Deploy** ใน build #1:

```text
{{out:b1-push-digest}}
```

เปิด `http://localhost:3000` chip บนแถบด้านบนต้องเป็น `v1.0.0 · build #1`

## ขั้นที่ 8 — ออกเวอร์ชันใหม่ `APP_VERSION=1.1.0`

job `docker-build-push` → **Build with Parameters** → เปลี่ยนเฉพาะ `APP_VERSION` เป็น `1.1.0` → **Build**

{{fig:build_parameters}}

✅ build #2 `{{val:b2_result}}` ใน {{val:b2_duration}} · เลือก stage ทางซ้ายของหน้า build เพื่อดู log:

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

หน้า Tags บน Docker Hub มี tag ของ build #1 และ #2 และ digest ตรงกับ console:

{{fig:hub_tags}}

🔍 **สืบย้อนได้ครบ:** chip `v1.1.0 · build #2` → Container ใน Deployment info (`host` ใน `/api/health`) → `image: <repo>@sha256:...` ใน Deploy → digest ที่ Push จดไว้ → build #2 → commit จาก Clone

## ขั้นที่ 9 — ลองค่าผิด 3 แบบ ร้านเดิมต้องยังอยู่

**(ก)** Build with Parameters กรอก `APP_VERSION` = `1.2.0; id` → build #3 `{{val:b3_result}}` ที่ Connect ก่อนส่งค่านี้ผ่าน SSH (SSH ที่เห็นมาจาก `post` ซึ่งลบแค่ของชั่วคราว)

```text
{{out:b3}}
```

{{fig:build3}}

**(ข)** กรอก `GIT_REF` = `no-such-branch` (ผ่าน Connect เพราะรูปแบบถูก) → build #4 `{{val:b4_result}}` ที่ Clone

{{fig:build4}}

**(ค)** credential `devtools-ssh` → **Update** → **Change Password** เป็นค่าอื่น → **Save** → **Build Now** → build #5 `{{val:b5_result}}` ที่ Connect (`sshpass` exit code 5 = รหัสผิด) · **จากนั้นแก้ Password กลับเป็น `passwd`**

{{fig:build5}}

ตรวจจาก host ว่าร้านยังเป็น container เดิมของ build #2:

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
- [ ] build ในขั้นที่ 9 ล้มตามที่คาด ร้านยังเป็น build #2 และแก้รหัส `devtools-ssh` กลับเป็น `passwd` แล้ว

## แก้ปัญหาที่พบบ่อย

| อาการ | วิธีแก้ |
|---|---|
| `sshpass: not found` ใน Connect | รันขั้นที่ 3 อีกครั้ง (เกิดเมื่อสร้าง `jenkins` ใหม่) |
| `Could not resolve hostname devtools` | `docker network inspect cicd-net` ต้องเห็นทั้งสองตัว ถ้าไม่เห็นให้ `docker network connect cicd-net devtools` |
| `Host key verification failed.` | ยังไม่ได้ pin หรือสร้าง `devtools` ใหม่จาก image อื่น → รันขั้นที่ 4 อีกครั้ง |
| `Permission denied, please try again.` / `exit code 5` | แก้ Password ของ `devtools-ssh` เป็น `passwd` |
| `Could not find credentials entry with ID ...` | ตั้ง ID เป็น `devtools-ssh` และ `dockerhub` ให้ตรงตัว |
| `user=****` หรือ `/****/lab3-work` ใน console | เอาติ๊ก **Treat username as secret** ของ `devtools-ssh` ออก |
| `... ไม่ถูกต้อง: ...` ใน Connect | แก้ parameter ตามข้อความ (`X.Y.Z`, `https://...`, username Docker Hub ตัวพิมพ์เล็ก) |
| `Remote branch ... not found` ใน Clone | ตรวจว่า `GIT_REF`/`GIT_URL` มีจริงและเป็น Public |
| `unauthorized` / `denied` ใน Push หรือ Pull | token ผิด หมดอายุ หรือไม่มีสิทธิ์ Write → สร้างใหม่แล้วแก้ `dockerhub` |
| `พบ container catfood-web ที่ไม่ได้สร้างโดย LAB 3` / `port 3000 ถูก container อื่นใช้อยู่` | `docker exec devtools docker ps -a` ลบเฉพาะตัวที่ไม่ใช้แล้ว แล้ว Build ใหม่ |
| เปิด `localhost:3000` ไม่ได้ทั้งที่ Deploy เขียว | `docker port devtools` ถ้าไม่มี 3000 ให้ทำขั้นที่ 1 ใหม่ |

## 🧹 เก็บกวาด (🖥️ host)

**ห้ามลบ** `devtools`, `jenkins`, volume `jenkins_home`, network `cicd-net` และ credential ทั้งสอง เพราะแล็บถัดไปใช้ต่อ บล็อกนี้ลบเฉพาะ container/image ที่มี label `devtools.lab=lab3` บน Docker ของ devtools และไฟล์ชั่วคราว:

{{block:cleanup}}

จบรายวิชาแล้วให้ลบ credential ทั้งสองและ revoke token ที่ Docker Hub · เปิดเครื่องใหม่ container ทั้งหมด (รวม `catfood-web`) จะกลับมาเอง (`--restart unless-stopped`) ถ้าไม่ขึ้นให้ `docker start devtools jenkins`

## 🤔 คำถามทบทวน

1. ถ้าสร้าง `devtools` โดยไม่ใส่ `--network cicd-net` stage ใดจะล้มก่อน และ error คืออะไร
2. การ pin host key ป้องกันอะไรได้ และทำไม fingerprint ของทุกคนในห้องจึงเหมือนกัน
3. ทำไม Jenkinsfile ใช้ `sshpass -e` แทน `sshpass -p passwd` และใช้ `sh '...'` แทน `sh "..."`
4. ทำไม Clean ต้องเกิด **หลัง** Push สำเร็จ และทำไม Pull/Deploy ใช้ `repository@sha256:...` แทน `repository:tag`

เอกสารนี้ทดสอบจริงครบทุกขั้นแล้ว ดู [รายงานผลทดสอบ](./LAB003_FINAL_REPORT.md)

➡️ **แล็บถัดไป:** [LAB 4 — Pipeline from Git](../004_LAB_Pipeline_From_Git/README.md)
