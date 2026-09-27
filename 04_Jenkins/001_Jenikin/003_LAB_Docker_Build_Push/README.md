# LAB 3 — Jenkins สั่ง devtools ผ่าน SSH key: Connect → Clone → Build → Test → Push → Deploy ร้านอาหารแมว

> 📝 **ฉบับปรับใหม่ (2026-09-27):** Jenkins SSH เข้า `devtools` ด้วย **key `devtoolSSH`** ผ่าน plugin **SSH Agent** และตรวจ host key จาก `known_hosts` ที่ pin ไว้ · `Jenkinsfile` ถูกเขียนใหม่ให้สั้นเหลือ **6 stage** · ⚠️ ไฟล์ฉบับนี้ **ตรวจแบบ static แล้ว แต่ยังไม่ได้รันจริงบน Jenkins** · ภาพที่มีป้าย 🕰️ **ภาพเดิม** ถ่ายจาก workflow รุ่นก่อน (SSH ด้วยรหัสผ่าน, 8 stage) ใช้ดูหน้าตาหน้าเว็บเท่านั้น

> ⏱️ ประมาณ 50–60 นาที (รวม build image devtools ครั้งแรก) · 🧪 7 ขั้น · 🎯 จบเมื่อกด **Build** ใน Jenkins แล้ว `http://localhost:3000` แสดงร้าน **Meow Mart** เวอร์ชันที่ Pipeline เพิ่ง build → test → push ขึ้น Docker Hub → pull กลับมา deploy

## ภาพรวม

แล็บนี้ใช้ container สองตัวแทน **server สองเครื่อง** บน network `cicd-net`:

- **`jenkins`** — ควบคุม Pipeline: อ่าน `Jenkinsfile` จาก GitHub เก็บ Credentials แล้วส่งคำสั่งทาง SSH · ไม่มี Docker CLI และไม่ mount `docker.sock`
- **`devtools`** — รับคำสั่ง SSH แล้วรัน `git clone` และคำสั่ง `docker` ทุกคำสั่ง · ร้าน `catfood-web` รันบน Docker **ข้างใน** devtools

```mermaid
flowchart LR
  B([เบราว์เซอร์ของเรา]) -->|localhost:8080| J
  B -->|localhost:3000| D
  subgraph NET[network cicd-net]
    J["jenkins :8080<br/>Pipeline + Credentials<br/>plugin SSH Agent<br/>ไม่มี Docker"] -->|"ssh root@devtools<br/>key: devtools-ssh<br/>host key: known_hosts"| D["devtools :22<br/>git + Docker ของตัวเอง<br/>ร้าน catfood-web :3000"]
  end
  G[(GitHub)] -->|git clone| D
  D -->|docker push / pull| H[(Docker Hub)]
```

*แผนภาพ A — Jenkins ถือ private key ไว้ใน credential `devtools-ssh` แล้ว SSH ไป `devtools:22` · devtools ถือ public key (`Devtool_SSH/devtoolSSH.pub`) ใน `authorized_keys` · งาน git/docker ทั้งหมดรันบน devtools*

```mermaid
flowchart LR
  C[1 Connect<br/>ตรวจ key + host key] --> CL[2 Clone<br/>git clone บน devtools] --> BU[3 Build<br/>docker build] --> T[4 Test<br/>container ชั่วคราว + /api/health] --> P[5 Push<br/>login ด้วย token → push] --> DE[6 Deploy<br/>pull → run → health]
```

*แผนภาพ B — 6 stage ของ `Jenkinsfile` · ทุก stage คือ `ssh root@devtools ...` หนึ่งถึงสองครั้ง*

| container | รันอยู่บน | เข้าจากเครื่องเราทาง |
|---|---|---|
| `jenkins` | เครื่องของเรา (network `cicd-net`) | `localhost:8080` |
| `devtools` (`--privileged` มี Docker ของตัวเอง) | เครื่องของเรา (network `cicd-net`) | `localhost:2222` → SSH · `localhost:3000` → ร้าน |
| `catfood-test` (ชั่วคราว) และ `catfood-web` (ร้าน) | Docker **ข้างใน** `devtools` | `localhost:3000` → `devtools:3000` → `catfood-web:3000` |

> **กติกา:** ห้ามพิมพ์ `docker build`, `docker push` หรือ `git clone` ของร้านเอง ทุกอย่างต้องเริ่มจากปุ่มใน Jenkins

> ⚠️ key `devtoolSSH` แจกให้ทุกคนใช้ร่วมกันและ login เป็น `root` ได้ ใช้กับแล็บบนเครื่องตัวเองเท่านั้น ห้ามนำไปใช้กับ server จริง และห้ามเปิด port `2222` ออก internet

## 0. สิ่งที่ต้องมี

- terminal ที่ใช้ `docker` ได้ (Linux, macOS หรือ WSL) เรียกว่า 🖥️ **host** · คำสั่ง 🖥️ host คือคำสั่ง**เตรียมแล็บ**ที่เราพิมพ์เอง ส่วนคำสั่งของแอป Jenkins ส่งผ่าน SSH ไปรันใน `devtools`
- port `8080`, `2222`, `3000` ต้องว่าง · Jenkins ต้องออก internet ไป `github.com` และ plugin center ได้ · devtools ต้องไป `github.com` และ Docker Hub ได้
- บัญชี Docker Hub และ **Personal Access Token สิทธิ์ Read & Write** (Account settings → Personal access tokens)
- ไฟล์ในโฟลเดอร์แล็บนี้ (`04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/`):

```text
003_LAB_Docker_Build_Push/
├── Jenkinsfile          ← Pipeline 6 stage (ข้อ 4.4)
├── catfood-shop/        ← ซอร์สร้าน (devtools clone จาก GitHub เอง)
├── devtools-image/      ← Dockerfile + start.sh ของ devtools ที่รองรับ SSH key (สำเนาจาก 00_Tool/00_Reference)
└── Devtool_SSH/         ← key pair ของแล็บ → mount เข้า devtools ที่ /etc/devtools/ssh
    ├── devtoolSSH       ← private key: วางใน Jenkins credential devtools-ssh (ข้อ 3.1)
    └── devtoolSSH.pub   ← public key: start.sh ใส่ใน authorized_keys ของ devtools ให้เอง
```

[![หน้าสร้าง Personal Access Token บน Docker Hub](./images/lab3_hub_04_pat_setup_crop.png)](./images/lab3_hub_04_pat_setup.png)

*ภาพที่ 1 หน้าสร้าง token บน Docker Hub: ตั้งชื่อ เลือก **Access permissions = Repo Read & Write** แล้วกด **Generate** · token แสดงครั้งเดียว ให้คัดลอกเก็บทันที*

[![ภาพประกอบหน้า Docker Hub หลังกด Generate (ค่าสมมติ)](./images/lab3_hub_pat_demo.png)](./images/lab3_hub_pat_demo.png)

*ภาพที่ 1ก ภาพประกอบที่สร้างขึ้นเพื่อการสอน ไม่ใช่หน้าจอจริง · ชื่อผู้ใช้ `demo-student` และ token ในภาพเป็นค่าสมมติ ใช้งานไม่ได้*

stage Clone ดึงซอร์สร้านจากโฟลเดอร์นี้ใน repository ของรายวิชา:

[![ซอร์สร้านบน GitHub](./images/lab3_github_01_source_crop.png)](./images/lab3_github_01_source.png)

*ภาพที่ 2 โฟลเดอร์ `catfood-shop` บน GitHub ที่ stage Clone ดึงมา*

## ขั้นที่ 1 — สร้าง container สองตัวและ pin host key (🖥️ host)

### 1.1) build image devtools ที่รองรับ key แล้วสร้าง network และ container

image `tuchsanai/devtools:2569_1` บน Docker Hub **SSH ได้ด้วยรหัสผ่านอย่างเดียว** (ไม่อ่านโฟลเดอร์ key) แล็บนี้จึง build image จากโฟลเดอร์ `devtools-image/` ก่อน ซึ่งเป็นสำเนาไฟล์ build ของ `00_Tool/00_Reference` (ส่วนที่ 2) · ถ้าเคย build `devtools:2569_1` จาก 00_Reference แล้ว ข้ามบรรทัด `docker build` ได้

รันใน**โฟลเดอร์ของแล็บนี้** (ที่มี `Devtool_SSH/` และ `devtools-image/`) — `${PWD}` ใช้ได้ทั้ง PowerShell และ Linux/macOS:

<!-- lab3-test:host-setup -->
```bash
cd 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push   # จาก root ของ repository รายวิชา
docker build -t devtools:2569_1 ./devtools-image
docker rm -f jenkins devtools
docker network create cicd-net
docker run -dit --name devtools --network cicd-net --privileged --tmpfs /run --restart unless-stopped -p 2222:22 -p 3000:3000 -v "${PWD}/Devtool_SSH:/etc/devtools/ssh" devtools:2569_1
docker run -d --name jenkins --network cicd-net --restart unless-stopped -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21
```

| ส่วน | ความหมาย |
|---|---|
| `docker build -t devtools:2569_1 ./devtools-image` | build image ที่ `start.sh` อ่าน key จาก `/etc/devtools/ssh` (ครั้งแรกใช้เวลาหลายนาที) |
| `docker rm -f jenkins devtools` | ลบตัวเดิม ถ้าขึ้น `No such container` ทำต่อได้ · ⚠️ ของใน `devtools` ตัวเดิมจะหายไป |
| `docker network create cicd-net` | ขึ้น `already exists` ใช้ network เดิมได้ · บน `cicd-net` Jenkins เรียก `devtools` ด้วยชื่อได้เลย |
| `--privileged --tmpfs /run` | ให้ Docker ข้างใน `devtools` ทำงานได้ |
| `-v "${PWD}/Devtool_SSH:/etc/devtools/ssh"` | map โฟลเดอร์ key ของแล็บเข้า devtools → ตอน start `start.sh` นำ `devtoolSSH.pub` ไปใส่ใน `/root/.ssh/authorized_keys` |
| `-v jenkins_home:/var/jenkins_home` | volume เก็บข้อมูล Jenkins รวมถึง `~/.ssh/known_hosts` ในข้อ 1.2 |

ตรวจว่า devtools เปิด key login แล้ว:

```bash
docker logs devtools | grep "SSH key"
# [start.sh] SSH key login enabled: /etc/devtools/ssh/devtoolSSH.pub
```

ถ้าขึ้น `SSH key login disabled` แปลว่าไม่ได้รันในโฟลเดอร์แล็บ (mount ผิดที่) หรือใช้ image จาก Docker Hub → ลบ `devtools` แล้วทำ 1.1 ใหม่

### 1.2) pin host key ของ devtools ไว้ใน `known_hosts` ของ jenkins

SSH ยืนยันตัวตนสองทาง: **key ของเรา** (devtools ตรวจ Jenkins) และ **host key** (Jenkins ตรวจว่าคุยกับ devtools ตัวจริง) · `Jenkinsfile` ใช้ `StrictHostKeyChecking=yes` จึงต้องบอก Jenkins ล่วงหน้าว่า host key ของ `devtools` คืออะไร เราอ่านจากไฟล์ใน devtools โดยตรงด้วย `docker exec` (ไม่ผ่าน network จึงไม่มีใครปลอมได้) แล้วเขียนลง `~/.ssh/known_hosts` ของ user `jenkins`:

<!-- lab3-test:pin-host-key -->
```bash
docker exec jenkins sh -c 'mkdir -p ~/.ssh && touch ~/.ssh/known_hosts && ssh-keygen -R devtools'
docker exec devtools cat /etc/ssh/ssh_host_ed25519_key.pub | awk '{print "devtools", $1, $2}' | docker exec -i jenkins sh -c 'cat >> ~/.ssh/known_hosts'
docker exec jenkins ssh-keygen -lF devtools
docker exec devtools ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub
```

- บรรทัดแรกลบ host key เก่าของ `devtools` (ถ้ามี) · ครั้งแรกจะขึ้น `Host devtools not found in ...` ไม่เป็นไร
- ✅ บรรทัดที่ 3 (ฝั่ง jenkins) และ 4 (ฝั่ง devtools) ต้องได้ fingerprint `SHA256:...` **ตัวเดียวกัน** (ED25519)
- ทุกครั้งที่ลบแล้วสร้าง `devtools` ใหม่ host key จะเปลี่ยน ต้องทำข้อ 1.2 ซ้ำ

## ขั้นที่ 2 — ปลดล็อก ตั้งค่า Jenkins และติดตั้ง plugin SSH Agent

<!-- lab3-test:unlock -->
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

✅ ได้รหัสเลขฐานสิบหก 32 ตัว (ห้ามเผยแพร่)

> 📷 ภาพที่ 3ก–3ฉ **นำมาจาก LAB 1** เป็นขั้นตอน Setup Wizard เดียวกัน ไม่ได้ถ่ายใหม่จาก LAB 3

> 🔁 **ถ้าเคยตั้งค่า Jenkins ไว้แล้ว** ให้ login ด้วยผู้ดูแลเดิม แล้วข้ามไปข้อ 2.7

**2.1) ปลดล็อก** เปิด **http://localhost:8080** วางรหัสจากคำสั่งด้านบนในช่อง **Administrator password** แล้วกด **Continue**

![หน้า Unlock Jenkins (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_01_unlock.png)

*ภาพที่ 3ก (จาก LAB 1) หน้า **Unlock Jenkins***

**2.2) เลือก Install suggested plugins**

![หน้า Customize Jenkins (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_02_plugins.png)

*ภาพที่ 3ข (จาก LAB 1) **Install suggested plugins** มี Pipeline, Git และ Pipeline Graph View แต่**ไม่มี SSH Agent** (ติดตั้งเพิ่มในข้อ 2.7)*

**2.3) รอติดตั้ง plugin** ประมาณ 2–4 นาที ถ้าบางตัวขึ้น **Retry** ให้กด Retry

![กำลังติดตั้ง plugin (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_03_installing.png)

*ภาพที่ 3ค (จาก LAB 1) เครื่องหมาย ✓ คือ plugin ที่ติดตั้งเสร็จแล้ว*

**2.4) สร้างผู้ดูแลระบบ** กรอกตามภาพ แล้วกด **Save and Continue**

![แบบฟอร์ม Create First Admin User (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_04_admin_user.png)

*ภาพที่ 3ง (จาก LAB 1) Username `admin` · Password `admin2569` (2 ช่อง) · Full name `Admin` · Email `student@example.com`*

**2.5) คง Jenkins URL เป็น `http://localhost:8080/`** แล้วกด **Save and Finish**

![Instance Configuration (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_05_instance_url.png)

*ภาพที่ 3จ (จาก LAB 1) หน้า **Instance Configuration***

**2.6) กด Start using Jenkins**

![Jenkins is ready! (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_06_ready.png)

*ภาพที่ 3ฉ (จาก LAB 1) Setup Wizard เสร็จแล้ว*

**2.7) ติดตั้ง plugin SSH Agent** — ⚙️ **Manage Jenkins → Plugins → Available plugins** → ช่องค้นหาพิมพ์ `SSH Agent` → ติ๊ก **SSH Agent** (plugin ID `ssh-agent`) → **Install** → รอจนขึ้น Success

- plugin นี้ให้คำสั่ง `sshagent(credentials: ['devtools-ssh']) { ... }` ใน `Jenkinsfile`: โหลด private key จาก credential เข้า `ssh-agent` ชั่วคราวเฉพาะในบล็อก คำสั่ง `ssh` ข้างในจึงใช้ key ได้โดยไม่มีไฟล์ key บนดิสก์ของ job
- อย่าสับสนกับ **SSH Build Agents** (ใช้ต่อ agent node) ซึ่งเป็นคนละ plugin
- ✅ ตรวจที่ **Manage Jenkins → Plugins → Installed plugins** ต้องมี **SSH Agent**

## ขั้นที่ 3 — สร้าง Jenkins Credentials: `devtools-ssh` และ `dockerhub`

`Jenkinsfile` อ้างถึงแค่ **ID** ของ credential ไม่มี key หรือ token อยู่ในไฟล์ และ Jenkins ซ่อนค่าลับเป็น `****` ใน console ให้

| ID | ชนิด (Kind) | ใช้ทำอะไร | ใช้ใน stage |
|---|---|---|---|
| `devtools-ssh` | **SSH Username with private key** | user `root` + private key `Devtool_SSH/devtoolSSH` สำหรับ **SSH เข้า `devtools`** | ทุก stage และ `post` (ผ่าน `sshagent`) |
| `dockerhub` | **Username with password** | username + Personal Access Token ของ Docker Hub: username ใช้ตั้งชื่อ image `<DOCKER_USER>/catfood-shop` ส่วน token ใช้ `docker login` บน devtools | Push · Deploy |

**3.0) เปิดหน้าเพิ่ม credential** — คลิกตามลำดับ **Login → ⚙️ Manage Jenkins → Credentials → System → Global → + Add Credentials** (ภาพที่ 4ก–4ฉ ภาพหน้าจอจริงจาก Jenkins 2.568.3 คลิกภาพเพื่อขยาย)

**3.0ก) Login** — เปิด `http://localhost:8080` กรอก `admin` / `admin2569` แล้วกด **Sign in**

[![หน้า Sign in to Jenkins](./images/lab3_nav_01_login.png)](./images/lab3_nav_01_login.png)

*ภาพที่ 4ก หน้า **Sign in to Jenkins***

**3.0ข) Dashboard → ไอคอนเฟือง ⚙️** — คลิกไอคอน**เฟือง** (Manage Jenkins) มุมขวาบน ข้างไอคอนแว่นขยาย

[![หน้า Dashboard มีไอคอนเฟือง Manage Jenkins มุมขวาบน](./images/lab3_nav_02_dashboard.png)](./images/lab3_nav_02_dashboard.png)

*ภาพที่ 4ข หน้า **Dashboard**: มุมขวาบนมีไอคอนแว่นขยาย (ค้นหา) · **เฟือง = Manage Jenkins** · ไอคอนผู้ใช้ · จุดแดงบนเฟืองคือการแจ้งเตือนของระบบ ไม่เกี่ยวกับแล็บนี้*

**3.0ค) Manage Jenkins → Credentials** — หมวด **Security** คลิก **Credentials** (ไม่ใช่ **Credential Providers**)

[![หน้า Manage Jenkins วงกลมแดงและลูกศรชี้ไทล์ Credentials ในหมวด Security](./images/lab3_nav_03_manage_credentials_annotated.svg)](./images/lab3_nav_03_manage_credentials_annotated.svg)

*ภาพที่ 4ค หน้า **Manage Jenkins** หมวด **Security**: คลิก **Credentials** (วงกลมแดงและลูกศรวาดทับภาพหน้าจอจริง · [ภาพต้นฉบับ](./images/lab3_nav_03_manage.png))*

**3.0ง) Stores scoped to Jenkins → System**

[![หน้า Credentials และตาราง Stores scoped to Jenkins](./images/lab3_nav_04_credentials.png)](./images/lab3_nav_04_credentials.png)

*ภาพที่ 4ง หน้า **Credentials**: คลิกแถว **System** ในตาราง **Stores scoped to Jenkins***

**3.0จ) System → Global** (Jenkins รุ่นก่อนเรียกว่า **Global credentials (unrestricted)**)

[![หน้า System แสดง domain Global](./images/lab3_nav_05_system.png)](./images/lab3_nav_05_system.png)

*ภาพที่ 4จ หน้า **System**: domain **Global***

**3.0ฉ) Global → + Add Credentials**

[![หน้า Global ก่อนเพิ่ม credential](./images/lab3_nav_06_global.png)](./images/lab3_nav_06_global.png)

*ภาพที่ 4ฉ หน้า **Global**: กด **+ Add Credentials***

**3.1) `devtools-ssh`** — เลือก Kind **SSH Username with private key** แล้วกรอก:

| ช่อง | ค่า |
|---|---|
| Kind | **SSH Username with private key** |
| Scope | Global |
| ID | `devtools-ssh` |
| Description | `SSH key: Jenkins to devtools` |
| Username | `root` |
| Treat username as secret | ไม่ติ๊ก |
| Private Key | เลือก **Enter directly** → กด **Add** → วางเนื้อหา**ทั้งไฟล์** `Devtool_SSH/devtoolSSH` |
| Passphrase | เว้นว่าง (key ของแล็บไม่มี passphrase) |

กด **Create**

- เปิดไฟล์ `Devtool_SSH/devtoolSSH` ด้วย text editor แล้วคัดลอกทั้งหมด ตั้งแต่บรรทัด `-----BEGIN OPENSSH PRIVATE KEY-----` ถึง `-----END OPENSSH PRIVATE KEY-----` (ใช้ไฟล์ที่**ไม่มี** `.pub`)
- ห้ามวาง private key ในแชต เอกสาร หรือ commit ลง repository ของตัวเอง · หลังกด Create Jenkins จะไม่แสดง key อีก

**3.2) `dockerhub`** — กลับหน้า **Global** แล้วกด **+ Add Credentials** อีกครั้ง Kind **Username with password**:

| ช่อง | ค่า |
|---|---|
| Username | `<DOCKER_USER>` ชื่อบัญชี Docker Hub (ตัวพิมพ์เล็ก) |
| Treat username as secret | ไม่ติ๊ก |
| Password | `<DOCKER_TOKEN>` Personal Access Token จากภาพที่ 1 (Repo **Read & Write**) ไม่ใช่รหัสผ่านบัญชี |
| ID | `dockerhub` |
| Description | `Docker Hub access token` |

[![ฟอร์ม credential dockerhub](./images/lab3_scm_03_cred_dockerhub.png)](./images/lab3_scm_03_cred_dockerhub.png)

*ภาพที่ 5 ฟอร์มของ `dockerhub` · ใส่ชื่อสมมติ `demostudent` และ token สมมติ ให้ใส่บัญชีและ token ของตัวเอง*

[![รายการ credential สองตัว (ภาพเดิม)](./images/lab3_scm_04_credentials_list.png)](./images/lab3_scm_04_credentials_list.png)

*ภาพที่ 6 🕰️ **ภาพเดิม** รายการ Global credentials จากรุ่นที่ `devtools-ssh` ยังเป็นชนิดรหัสผ่าน (`root/******`) · ในแล็บนี้ `devtools-ssh` เป็นชนิด SSH key หน้ารายการจะแสดงต่างออกไป · ดูแค่ว่าต้องมี ID `devtools-ssh` และ `dockerhub` ครบ*

> ⚠️ ID ต้องสะกดตรงตัว เพราะ `Jenkinsfile` เรียกด้วย ID นี้

## ขั้นที่ 4 — สร้าง Pipeline job และทำความเข้าใจ `Jenkinsfile`

| ทางเลือก | ทำอะไร | ตั้งค่า job ในข้อ 4.2 |
|---|---|---|
| **ก. ใช้ไฟล์ของรายวิชา** (แนะนำรอบแรก) | ใช้ [`Jenkinsfile`](./Jenkinsfile) ใน repository ของรายวิชา ไม่ต้อง fork | ตามตารางในข้อ 4.2 |
| **ข. ฝึกเขียนเอง** | พิมพ์ไฟล์ตามข้อ 4.4 ใน repository สาธารณะของตัวเอง แล้ว commit/push (ข้อ 4.5) | Repository URL, Branch และ Script Path ของตัวเอง |

> 📷 ภาพที่ 7–9 เป็นภาพหน้าจอจริงของหน้าตั้งค่า job (2026-09-27) หน้าตั้งค่านี้ไม่ขึ้นกับเนื้อหา `Jenkinsfile`

**4.1) Dashboard → New Item → Pipeline** — ชื่อ `docker-build-push` → เลือก **Pipeline** → **OK**

[![หน้า New Item](./images/lab3_scm_05_new_item.png)](./images/lab3_scm_05_new_item.png)

*ภาพที่ 7 หน้า **New Item**: ชื่อ `docker-build-push` และชนิด **Pipeline***

**4.2) ตั้งค่า job: Pipeline script from SCM** — ส่วน **Pipeline** ตั้งค่าตามตาราง → **Save** (ยังไม่ต้อง Build)

| ช่อง | ค่า |
|---|---|
| Definition | **Pipeline script from SCM** |
| SCM | **Git** |
| Repository URL | `https://github.com/Tuchsanai/DevTools.git` |
| Credentials | `- none -` (repository สาธารณะ) |
| Branch Specifier | `*/main` |
| Script Path | `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile` |
| Lightweight checkout | ติ๊ก (ค่าเริ่มต้น) |

[![Definition Pipeline script from SCM](./images/lab3_scm_06_pipeline_from_scm.png)](./images/lab3_scm_06_pipeline_from_scm.png)

*ภาพที่ 8 Definition = **Pipeline script from SCM**, SCM = **Git**, Repository URL ของรายวิชา, Credentials = none*

[![Branch และ Script Path](./images/lab3_scm_07_branch_script_path_crop.png)](./images/lab3_scm_07_branch_script_path.png)

*ภาพที่ 9 Branch Specifier `*/main`, Script Path และ **Lightweight checkout** ติ๊กอยู่ · แถบกลางภาพคือรอยต่อของภาพที่เลื่อนหลายช่วง*

**4.3) ใครโหลดอะไร**

- Jenkins ดึง `Jenkinsfile` จาก GitHub เอง**ก่อน** Pipeline เริ่ม (Pipeline script from SCM) เพราะยังไม่รู้ว่าต้อง SSH ไปไหนจนกว่าจะอ่านไฟล์
- จากนั้นทุกอย่างของแอป (`git clone`, `docker build/run/push/pull`) Jenkins ส่งทาง SSH ไปรันบน `devtools`
- `skipDefaultCheckout()` ปิดการ checkout ทั้ง repository (ขนาดระดับ GB) ลง workspace ของ Jenkins ซึ่งแล็บนี้ไม่ใช้

**4.4) อ่าน `Jenkinsfile` ทีละส่วน**

ทุก stage ใช้รูปแบบเดียวกัน 3 อย่าง:

| รูปแบบ | ตัวอย่างในไฟล์ | ความหมาย |
|---|---|---|
| `sshagent(credentials: ['devtools-ssh']) { ... }` | ทุก stage | plugin SSH Agent โหลด private key จาก credential ให้คำสั่ง `ssh` ในบล็อกใช้ แล้วปิด agent เมื่อจบบล็อก |
| `$SSH_DEVTOOLS "..."` | Connect | `SSH_DEVTOOLS` = `ssh -o StrictHostKeyChecking=yes -o BatchMode=yes root@devtools` · `StrictHostKeyChecking=yes` ยอมเฉพาะ host key ที่ pin ไว้ในข้อ 1.2 · `BatchMode=yes` ห้ามถามรหัสผ่าน (key ใช้ไม่ได้ = ล้มทันที) |
| `$SSH_DEVTOOLS "A=$A B=$B bash -ex" <<'EOF' ... EOF` | Clone ถึง Deploy | ส่งสคริปต์หลายบรรทัดไปรันบน devtools · ค่าจาก `environment` ส่งไปเป็นตัวแปรนำหน้า `bash` · `'EOF'` มี quote จึงไม่มีอะไรในสคริปต์ถูกแทนค่าบน Jenkins · `-e` หยุดเมื่อคำสั่งใดล้ม `-x` พิมพ์ทุกคำสั่งลง console |

ความลับ:

- `sh '...'` / `sh '''...'''` ใช้ **single quote** เสมอ Groovy จึงไม่แทนค่า `$HUB_TOKEN` ลงในสคริปต์ shell เป็นผู้อ่านจาก environment เอง และ Jenkins ซ่อนค่าเป็น `****`
- token เข้า devtools ทาง stdin: `echo "$HUB_TOKEN" | ssh ... docker login --password-stdin` ไม่อยู่ใน command line
- `set +x` ก่อนบรรทัด token และ `set -x` หลังบรรทัดนั้น: ปิดการพิมพ์คำสั่งของ `sh -xe` ชั่วคราว token จึงไม่ถูกพิมพ์ลง console เลย ไม่ต้องพึ่งการซ่อน `****` ของ Jenkins
- `umask 077` ก่อน `docker login` บน devtools: ไฟล์ login ใน `AUTH_DIR` อ่านได้เฉพาะ `root`
- login เก็บในโฟลเดอร์ชั่วคราว `AUTH_DIR` แยกจาก `~/.docker` และถูกลบด้วย `trap 'rm -rf "$AUTH_DIR"' EXIT` ทันทีที่สคริปต์จบ (สำเร็จหรือล้ม) ส่วน `post { always }` ลบซ้ำอีกชั้นกรณี build หยุดกลางทาง

| Stage | ทำอะไรบน devtools |
|---|---|
| **1 Connect** | (บน Jenkins) ตรวจ `APP_VERSION` เป็น `X.Y.Z` และ `ssh-keygen -lF devtools` ว่ามี host key ที่ pin ไว้ → SSH ถาม `hostname`, `whoami`, เวอร์ชัน Docker/git |
| **2 Clone** | sparse clone เฉพาะโฟลเดอร์ `catfood-shop` ลง `/root/lab3-work/DevTools` แล้วแสดง commit |
| **3 Build** | `docker build` → `catfood-shop:lab3-N` ฝังเวอร์ชัน, เลข build, commit และเวลา |
| **4 Test** | รัน `catfood-test` รอ `healthy` แล้วตรวจว่า `/api/health` ตอบ `version` และ `build` ตรงกับ build นี้ · ลบ container ทิ้งเสมอ |
| **5 Push** | `docker login` ด้วย token → tag เป็น `<DOCKER_USER>/catfood-shop:lab3-N` → push → ลบไฟล์ login และ tag ในเครื่อง |
| **6 Deploy** | login → ลบ image ในเครื่องแล้ว **pull จาก Docker Hub** → แทน `catfood-web` ตัวเดิมด้วยตัวใหม่ที่ port 3000 → รอ `healthy` แล้ว `curl localhost:3000/api/health` ต้องตอบเวอร์ชันและ build ตรง |

ช่วงสั้น ๆ ระหว่างลบ `catfood-web` ตัวเดิมจนตัวใหม่ `healthy` ร้านจะปิดชั่วคราว · `disableConcurrentBuilds()` กันสอง build ใช้ชื่อ container และ port 3000 พร้อมกัน

<details>
<summary><b>Jenkinsfile ฉบับสมบูรณ์</b> (เหมือนไฟล์ <code>Jenkinsfile</code> ทุกตัวอักษร คลิกเพื่อเปิด)</summary>

<!-- jenkinsfile:begin -->
```groovy
// LAB 3 — Jenkins สั่ง devtools ผ่าน SSH ด้วย key: Connect → Clone → Build → Test → Push → Deploy
// ต้องมี: plugin "SSH Agent" · credential devtools-ssh (SSH key) และ dockerhub (username + token)
//         host key ของ devtools อยู่ใน ~/.ssh/known_hosts ของ jenkins แล้ว (README ข้อ 1.2)
// ทุกคำสั่ง git/docker รันบน devtools: Jenkins แค่ส่งคำสั่งไปทาง SSH

pipeline {
  agent any

  options {
    disableConcurrentBuilds()   // ทุก build ใช้ชื่อ container และ port 3000 เดียวกัน
    skipDefaultCheckout()       // Jenkins ไม่ต้อง checkout repo เอง devtools clone ใน stage Clone
  }

  parameters {
    string(name: 'APP_VERSION', defaultValue: '1.0.0', description: 'เวอร์ชันรูปแบบ X.Y.Z ที่แสดงบนหน้าเว็บ')
  }

  environment {
    SSH_DEVTOOLS = 'ssh -o StrictHostKeyChecking=yes -o BatchMode=yes root@devtools'
    GIT_URL      = 'https://github.com/Tuchsanai/DevTools.git'
    APP_PATH     = '04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop'
    WORK_DIR     = '/root/lab3-work/DevTools'      // ที่ clone repo บน devtools
    AUTH_DIR     = '/root/lab3-work/docker-auth'   // ไฟล์ login Docker Hub ชั่วคราวบน devtools
    APP_NAME     = 'catfood-shop'
    IMAGE_TAG    = "lab3-${env.BUILD_NUMBER}"
    LOCAL_IMAGE  = "catfood-shop:lab3-${env.BUILD_NUMBER}"
  }

  stages {
    stage('Connect') {
      steps {
        script {
          if (!(params.APP_VERSION ==~ /[0-9]+\.[0-9]+\.[0-9]+/)) {
            error 'APP_VERSION ต้องเป็นรูปแบบ X.Y.Z เช่น 1.0.0'
          }
        }
        sh 'ssh-keygen -lF devtools'   // host key ที่ pin ไว้ในข้อ 1.2 (ไม่มี = หยุดทันที)
        sshagent(credentials: ['devtools-ssh']) {
          sh '$SSH_DEVTOOLS "hostname && whoami && docker --version && git --version"'
        }
      }
    }

    stage('Clone') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
$SSH_DEVTOOLS "WORK_DIR=$WORK_DIR GIT_URL=$GIT_URL APP_PATH=$APP_PATH bash -ex" <<'EOF'
rm -rf "$WORK_DIR"
git clone --depth 1 --filter=blob:none --sparse "$GIT_URL" "$WORK_DIR"
cd "$WORK_DIR"
git sparse-checkout set "$APP_PATH"
git log -1 --oneline
ls "$APP_PATH"
EOF
'''
        }
      }
    }

    stage('Build') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
$SSH_DEVTOOLS "SRC=$WORK_DIR/$APP_PATH IMAGE=$LOCAL_IMAGE VERSION=$APP_VERSION BUILD=$BUILD_NUMBER bash -ex" <<'EOF'
cd "$SRC"
COMMIT=$(git rev-parse --short HEAD)
TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
docker build --build-arg APP_VERSION="$VERSION" --build-arg BUILD_NUMBER="$BUILD" --build-arg GIT_COMMIT="$COMMIT" --build-arg BUILD_TIME="$TIME" -t "$IMAGE" .
docker image ls "$IMAGE"
EOF
'''
        }
      }
    }

    stage('Test') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
$SSH_DEVTOOLS "IMAGE=$LOCAL_IMAGE VERSION=$APP_VERSION BUILD=$BUILD_NUMBER bash -ex" <<'EOF'
docker rm -f catfood-test || true
docker run -d --name catfood-test "$IMAGE"
trap 'docker rm -f catfood-test' EXIT   # ลบ container ทดสอบเสมอ แม้ test ไม่ผ่าน
for i in $(seq 1 30); do
  [ "$(docker inspect -f '{{.State.Health.Status}}' catfood-test)" = healthy ] && break
  sleep 1
done
HEALTH=$(docker exec catfood-test wget -qO- http://127.0.0.1:3000/api/health)
echo "$HEALTH" | tr -d '"' | grep -F "version:$VERSION,build:$BUILD,"
EOF
'''
        }
      }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
                         usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
          sshagent(credentials: ['devtools-ssh']) {
            // token ส่งทาง stdin ของ SSH เข้า --password-stdin: ไม่อยู่ใน command line และ console
            sh '''
set +x
echo "$HUB_TOKEN" | $SSH_DEVTOOLS "umask 077; docker --config $AUTH_DIR login -u $HUB_USER --password-stdin"
set -x
$SSH_DEVTOOLS "AUTH_DIR=$AUTH_DIR LOCAL_IMAGE=$LOCAL_IMAGE IMAGE=$HUB_USER/$APP_NAME:$IMAGE_TAG bash -ex" <<'EOF'
trap 'rm -rf "$AUTH_DIR"' EXIT   # ลบ login ชั่วคราวเสมอ แม้ push ล้ม
docker tag "$LOCAL_IMAGE" "$IMAGE"
docker --config "$AUTH_DIR" push "$IMAGE"
docker image rm "$LOCAL_IMAGE"
EOF
'''
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
                         usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
          sshagent(credentials: ['devtools-ssh']) {
            sh '''
set +x
echo "$HUB_TOKEN" | $SSH_DEVTOOLS "umask 077; docker --config $AUTH_DIR login -u $HUB_USER --password-stdin"
set -x
$SSH_DEVTOOLS "AUTH_DIR=$AUTH_DIR IMAGE=$HUB_USER/$APP_NAME:$IMAGE_TAG VERSION=$APP_VERSION BUILD=$BUILD_NUMBER bash -ex" <<'EOF'
trap 'rm -rf "$AUTH_DIR"' EXIT
docker image rm "$IMAGE"                  # ลบ image ในเครื่อง เพื่อให้ pull มาจาก Docker Hub จริง
docker --config "$AUTH_DIR" pull "$IMAGE"
docker rm -f catfood-web || true          # ลบร้านเวอร์ชันเดิม
docker run -d --name catfood-web --restart unless-stopped -p 3000:3000 "$IMAGE"
for i in $(seq 1 30); do
  [ "$(docker inspect -f '{{.State.Health.Status}}' catfood-web)" = healthy ] && break
  sleep 1
done
curl -fsS http://localhost:3000/api/health | tr -d '"' | grep -F "version:$VERSION,build:$BUILD,"
EOF
'''
          }
        }
      }
    }
  }

  post {
    success {
      echo "เปิดร้านได้ที่ http://localhost:3000 (v${params.APP_VERSION} build #${env.BUILD_NUMBER})"
    }
    always {
      // กันไฟล์ login ค้างบน devtools ถ้า build หยุดกลางทาง
      sshagent(credentials: ['devtools-ssh']) {
        sh '$SSH_DEVTOOLS "rm -rf $AUTH_DIR" || true'
      }
    }
  }
}
```
<!-- jenkinsfile:end -->

</details>

**4.5) นำ `Jenkinsfile` เข้า Git ให้ job อ่าน**

- **ทางเลือก ก:** ไฟล์อยู่ใน repository ของรายวิชาแล้ว ไม่ต้องทำอะไรเพิ่ม
- **ทางเลือก ข:** วางไฟล์ที่ root ของ repository สาธารณะของตัวเอง แล้ว commit/push:

```bash
cd <โฟลเดอร์ที่ clone repository ของตัวเองไว้>
git add Jenkinsfile
git commit -m "Add LAB 3 Jenkinsfile"
git push
```

จากนั้น job `docker-build-push` → **Configure** → ตั้ง Repository URL, Branch Specifier และ Script Path (`Jenkinsfile`) เป็นของตัวเอง → **Save** · แก้ไฟล์แล้ว commit/push ก็พอ Jenkins อ่านรุ่นล่าสุดทุกครั้งที่ build

## ขั้นที่ 5 — Build Now แล้วดู 6 stage ทำงาน

หน้า job `docker-build-push` กด **Build Now** — build แรกใช้ค่า default `APP_VERSION=1.0.0` และ tag `lab3-1` (หลังรันครั้งแรกจึงมีเมนู **Build with Parameters**)

[![Console Output ช่วงเริ่ม build (ภาพเดิม)](./images/lab3_scm_08_console_obtained_crop.png)](./images/lab3_scm_08_console_obtained.png)

*ภาพที่ 10 🕰️ **ภาพเดิม** Console Output ช่วงแรก: `Obtained .../Jenkinsfile from git https://github.com/Tuchsanai/DevTools.git` แล้วเข้า stage `(Connect)` ทันที ไม่มี `Declarative: Checkout SCM` · ช่วงแรกนี้เหมือนกันในไฟล์ฉบับใหม่ ส่วน log ของแต่ละ stage จะต่างจากภาพ*

✅ สิ่งที่ต้องเห็นใน Console Output (ยังไม่มีภาพของไฟล์ฉบับนี้):

- **Connect:** `# Host devtools found` พร้อม fingerprint ตรงกับข้อ 1.2 · บรรทัดที่ขึ้นต้นด้วย `[ssh-agent]` บอกว่าใช้ credential ของ `root` · ผล `devtools` / `root` / `Docker version ...` / `git version ...`
- **Clone:** บรรทัด `+ git clone ...` ตามด้วย commit ล่าสุด และรายชื่อไฟล์ของ `catfood-shop`
- **Test:** บรรทัด `version:1.0.0,build:1,` ถูก `grep` เจอ
- **Push:** `Login Succeeded` แล้ว `lab3-1: digest: sha256:... size: ...` · token แสดงเป็น `****`
- **Deploy:** `Status: Downloaded newer image for <DOCKER_USER>/catfood-shop:lab3-1` → health ตรง → `เปิดร้านได้ที่ http://localhost:3000 (v1.0.0 build #1)`
- หน้า Stages ต้องเขียวครบ 6 stage: Connect → Clone → Build → Test → Push → Deploy

เปิด `http://localhost:3000` chip บนแถบด้านบนต้องเป็น `v1.0.0 · build #1`

## ขั้นที่ 6 — ออกเวอร์ชันใหม่ `APP_VERSION=1.1.0`

job `docker-build-push` → **Build with Parameters** → `APP_VERSION` = `1.1.0` → **Build** (มี parameter เดียว)

✅ build #2 เขียวครบ 6 stage · Deploy แทน `catfood-web` ของ build #1 · เปิด `http://localhost:3000` chip ต้องเป็น `v1.1.0 · build #2`:

[![หน้าร้าน v1.1.0 build #2 (ภาพเดิม)](./images/lab3_sib_app_v110_crop.png)](./images/lab3_sib_app_v110.png)

*ภาพที่ 11 🕰️ **ภาพเดิม** หน้าร้านหลัง build #2 ของรอบทดสอบ 2026-09-26 (ซอร์สร้านเดียวกัน) chip แสดง `v1.1.0 · build #2`*

[![ส่วน Deployment info ของร้าน (ภาพเดิม)](./images/lab3_sib_app_deployment_crop.png)](./images/lab3_sib_app_deployment.png)

*ภาพที่ 12 🕰️ **ภาพเดิม** ส่วน Deployment info ท้ายหน้าร้าน: Version, Jenkins build, Git commit, Built at และ Container ที่ตอบ*

หน้า **Tags** ของ repository `catfood-shop` บน Docker Hub ต้องมี `lab3-1` และ `lab3-2`:

[![หน้า Tags บน Docker Hub (ภาพเดิม)](./images/lab3_scm_dockerhub_tags_crop.png)](./images/lab3_scm_dockerhub_tags.png)

*ภาพที่ 13 🕰️ **ภาพเดิม** หน้า Tags บน Docker Hub ของรอบทดสอบเดิม (ชื่อ tag ในภาพเป็น `lab3-sibling-20260926r2-*`) · ของเราจะเป็น `lab3-1`, `lab3-2`*

## ขั้นที่ 7 — ลองให้ล้ม 2 แบบ ร้านเดิมต้องยังอยู่

**(ก) เวอร์ชันผิดรูปแบบ** — Build with Parameters กรอก `APP_VERSION` = `1.2.0; id` → build ล้มที่ **Connect** ด้วย `APP_VERSION ต้องเป็นรูปแบบ X.Y.Z เช่น 1.0.0` ก่อนส่งค่าใด ๆ ผ่าน SSH

**(ข) ไม่มี host key ที่ pin ไว้** — ลบ host key ออกจาก jenkins แล้ว **Build Now**:

```bash
docker exec jenkins ssh-keygen -R devtools
```

build ล้มที่ **Connect** ตรง `ssh-keygen -lF devtools` (exit code 1) และถ้าข้ามบรรทัดนั้นไป `ssh` ก็จะขึ้น `Host key verification failed.` เพราะ `StrictHostKeyChecking=yes` ไม่ยอมเชื่อ host ที่ไม่รู้จัก · **จากนั้นทำข้อ 1.2 ใหม่** แล้วกด Build อีกครั้งให้ผ่าน

ตรวจจาก host ว่าร้านยังเป็น build ล่าสุดที่สำเร็จ:

<!-- lab3-test:check-web -->
```bash
docker exec devtools curl -s -w "\n" localhost:3000/api/health
docker exec devtools docker ps --filter name=catfood --format '{{.Names}}  {{.Image}}  {{.Status}}'
```

✅ `/api/health` ตอบ `"version":"1.1.0","build":"2"` (หรือ build ล่าสุดที่ผ่าน) และมีแค่ `catfood-web` สถานะ `(healthy)` ไม่มี `catfood-test` ค้าง · ทั้งสองแบบล้มก่อน Deploy ร้านเดิมจึงไม่ถูกแตะ

## ✅ ตรวจปิดแล็บ

- [ ] `docker logs devtools | grep "SSH key"` ได้ `SSH key login enabled` · `docker exec jenkins sh -c "command -v docker || echo 'docker: none'"` ได้ `docker: none`
- [ ] `docker exec jenkins ssh-keygen -lF devtools` ได้ fingerprint ตรงกับ `docker exec devtools ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub`
- [ ] plugin **SSH Agent** ติดตั้งแล้ว · credential `devtools-ssh` เป็น **SSH Username with private key** (`root`) และ `dockerhub` เป็น **Username with password**
- [ ] build #1 และ #2 เขียวครบ 6 stage · หน้า Tags บน Docker Hub มี `lab3-1` และ `lab3-2`
- [ ] `http://localhost:3000` แสดง `v1.1.0 · build #2` · ไม่มีโฟลเดอร์ `/root/lab3-work/docker-auth` ค้างบน devtools (`docker exec devtools ls /root/lab3-work`)
- [ ] build ในขั้นที่ 7 ล้มตามที่คาด และทำข้อ 1.2 ใหม่แล้ว

## แก้ปัญหาที่พบบ่อย

| อาการ | วิธีแก้ |
|---|---|
| `No such DSL method 'sshagent'` | ยังไม่ได้ติดตั้ง plugin **SSH Agent** (ข้อ 2.7) |
| Connect ล้มที่ `+ ssh-keygen -lF devtools` ไม่มีผลลัพธ์ | ยังไม่ได้ pin host key → ทำข้อ 1.2 |
| `Host key verification failed.` / `REMOTE HOST IDENTIFICATION HAS CHANGED!` | `devtools` ถูกสร้างใหม่ host key จึงเปลี่ยน → ทำข้อ 1.2 ใหม่ (ห้ามแก้เป็น `StrictHostKeyChecking=no`) |
| `Permission denied (publickey,password)` | private key ใน `devtools-ssh` ไม่ตรงกับ `Devtool_SSH/devtoolSSH.pub` ที่ devtools ใช้ หรือ devtools ไม่ได้ mount key (`docker logs devtools \| grep "SSH key"`) → วาง key ใหม่ใน 3.1 หรือทำ 1.1 ใหม่ |
| `SSH key login disabled` ใน `docker logs devtools` | รัน `docker run` นอกโฟลเดอร์แล็บ หรือใช้ image `tuchsanai/devtools:2569_1` จาก Docker Hub → ทำ 1.1 ใหม่ในโฟลเดอร์แล็บ |
| `[ssh-agent] Could not find specified credentials` หรือ `Error loading key` | credential `devtools-ssh` ไม่ใช่ชนิด **SSH Username with private key** หรือวาง key ไม่ครบบรรทัด BEGIN/END → สร้างใหม่ตาม 3.1 |
| `Could not resolve hostname devtools` | `docker network inspect cicd-net` ต้องเห็นทั้งสองตัว ถ้าไม่เห็น `docker network connect cicd-net devtools` |
| `Unable to find .../Jenkinsfile from git` | ตรวจ Repository URL, Branch `*/main` และ Script Path ในข้อ 4.2 |
| `APP_VERSION ต้องเป็นรูปแบบ X.Y.Z` | กรอกเวอร์ชันแบบ `1.1.0` |
| Test ล้มที่ `grep -F "version:..."` | ดูบรรทัด `+ HEALTH=...` ใน console ว่าเว็บตอบอะไร · ถ้าไม่มีเลยแปลว่า container ไม่ `healthy` ใน 30 วินาที |
| `unauthorized: incorrect username or password` ใน Push/Deploy | token ผิดหรือหมดอายุ → สร้าง token ใหม่แล้ว **Update** credential `dockerhub` |
| `denied: requested access to the resource is denied` | token ไม่มีสิทธิ์ Write หรือ username ไม่ใช่ตัวพิมพ์เล็กตรงกับบัญชี |
| `port is already allocated` ใน Deploy | มี container อื่นบน devtools ใช้ port 3000 → `docker exec devtools docker ps` แล้วลบตัวที่ไม่ใช้ |
| เปิด `localhost:3000` ไม่ได้ทั้งที่ Deploy เขียว | `docker port devtools` ต้องมี `3000/tcp` ถ้าไม่มีให้ทำ 1.1 ใหม่ |

## 🧹 เก็บกวาด (🖥️ host)

**ห้ามลบ** `devtools`, `jenkins`, volume `jenkins_home`, network `cicd-net` และ credential ทั้งสอง เพราะแล็บถัดไปใช้ต่อ บล็อกนี้ลบเฉพาะร้าน image และไฟล์ชั่วคราวของแล็บนี้บน Docker ของ devtools:

<!-- lab3-test:cleanup -->
```bash
docker exec devtools sh -c "docker rm -f catfood-web catfood-test 2>/dev/null; true"
docker exec devtools sh -c "docker image ls --format '{{.Repository}}:{{.Tag}}' | grep 'catfood-shop:lab3-' | xargs -r docker image rm"
docker exec devtools rm -rf /root/lab3-work
docker exec devtools docker ps -a --format '{{.Names}}'
```

จบรายวิชาแล้วให้ลบ credential ทั้งสองและ revoke token ที่ Docker Hub · เปิดเครื่องใหม่ container ทั้งหมด (รวม `catfood-web`) จะกลับมาเอง (`--restart unless-stopped`) ถ้าไม่ขึ้นให้ `docker start devtools jenkins` · ถ้าสร้าง `devtools` ใหม่ ต้องทำข้อ 1.2 ใหม่ทุกครั้ง

## 🤔 คำถามทบทวน

1. ทำไมแล็บนี้ใช้ image `tuchsanai/devtools:2569_1` จาก Docker Hub ตรง ๆ ไม่ได้ และ `-v "${PWD}/Devtool_SSH:/etc/devtools/ssh"` ทำให้ `root@devtools` ยอมรับ key ของ Jenkins ได้อย่างไร
2. private key และ public key ของ `devtoolSSH` อยู่ที่ไหนบ้างในแล็บนี้ และทำไม `Jenkinsfile` จึงอ้างแค่ ID `devtools-ssh`
3. ข้อ 1.2 ป้องกันอะไร ถ้าเปลี่ยนเป็น `StrictHostKeyChecking=no` จะเสียอะไร และทำไมอ่าน host key ผ่าน `docker exec` แทนการถามผ่าน network
4. ทำไม token ต้องส่งด้วย `echo "$HUB_TOKEN" | ... --password-stdin` และทำไม `sh` ใช้ single quote `'...'` ไม่ใช่ `"..."`
5. `trap 'rm -rf "$AUTH_DIR"' EXIT` และ `trap 'docker rm -f catfood-test' EXIT` ช่วยอะไรเมื่อคำสั่งกลางสคริปต์ล้ม
6. ทำไม Deploy ลบ image ในเครื่องก่อน `docker pull` และ health check ใน Deploy พิสูจน์อะไรที่ `docker run` สำเร็จเฉย ๆ พิสูจน์ไม่ได้

➡️ **แล็บถัดไป:** [LAB 4 — Pipeline from Git](../004_LAB_Pipeline_From_Git/README.md)
