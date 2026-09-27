# LAB 3 — Jenkins สั่ง devtools ผ่าน SSH key: Connect → Clone → Build → Test → Push → Deploy ร้านอาหารแมว

## ภาพรวม

แล็บนี้ใช้ container สองตัวแทน **server สองเครื่อง** บน network `cicd-net`:

- **`jenkins`** — ควบคุม Pipeline: อ่าน `Jenkinsfile` จาก GitHub เก็บ Credentials แล้วส่งคำสั่งทาง SSH · ไม่มี Docker CLI และไม่ mount `docker.sock`
- **`devtools`** — รับคำสั่ง SSH แล้วรัน `git clone` และคำสั่ง `docker` ทุกคำสั่ง · ร้าน `catfood-web` รันบน Docker **ข้างใน** devtools

<a href="./images/lab3_diagram_a_architecture.png"><img src="./images/lab3_diagram_a_architecture.png" width="1000" alt="แผนภาพ A สถาปัตยกรรม: Jenkins ใช้ credential devtools-ssh สั่ง devtools ผ่าน SSH และ devtools รัน git กับ Docker รวมถึง catfood-web"></a>

*แผนภาพ A — Jenkins ใช้ private key ใน credential `devtools-ssh` SSH เข้าไปสั่ง `devtools` ซึ่งยอมให้ login ด้วย public key จากโฟลเดอร์ `Devtool_SSH` ที่ mount ไว้ · คำสั่ง git และ Docker ทั้งหมดรันใน devtools และร้าน `catfood-web` ก็รันบน Docker ข้างใน devtools*

<a href="./images/lab3_diagram_b_pipeline.png"><img src="./images/lab3_diagram_b_pipeline.png" width="1000" alt="แผนภาพ B Pipeline 6 stage: Connect, Clone, Build, Test, Push, Deploy ที่ Jenkins สั่ง devtools ผ่าน SSH"></a>

*แผนภาพ B — Pipeline มี 6 stage คือ Connect → Clone → Build → Test → Push → Deploy โดย Jenkins คุมทุก stage ผ่าน SSH · devtools clone โค้ดจาก GitHub, build และ test image, push ขึ้น Docker Hub ด้วย credential `dockerhub` แล้ว deploy ร้านที่ `localhost:3000`*

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
├── Jenkinsfile          ← Pipeline 6 stage (ข้อ 4.3)
├── catfood-shop/        ← ซอร์สร้าน (devtools clone จาก GitHub เอง)
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

## ขั้นที่ 1 — สร้าง container สองตัว (🖥️ host)

### 1.1) สร้าง network และ container จาก image `devtools:2569_1` ที่เตรียมไว้

ก่อนเริ่ม เข้า**โฟลเดอร์ของแล็บนี้** (ที่มี `Devtool_SSH/`) — `${PWD}` ใช้ได้ทั้ง PowerShell และ Linux/macOS:

```bash
cd 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push   # จาก root ของ repository รายวิชา
```

<a href="./images/lab3_windows_lab_folder_annotated.svg"><img src="./images/lab3_windows_lab_folder_annotated.svg" width="910" alt="ภาพ Windows File Explorer จริงที่ครอปเฉพาะส่วนโฟลเดอร์แล็บ กรอบแดงที่ path และวงรีแดงที่โฟลเดอร์ Devtool_SSH"></a>

*ภาพที่ 2ก ภาพหน้าจอ Windows File Explorer จริง (ครอปเฉพาะส่วน path และรายการในโฟลเดอร์แล็บ · ปิดทับ path ส่วนตัวด้วยแถบดำ · คลิกเพื่อขยาย) มี `Devtool_SSH/` อยู่ข้างใน · เปิด terminal ที่โฟลเดอร์นี้ เพราะ `${PWD}/Devtool_SSH` จะถูก mount เป็น `/etc/devtools/ssh` ใน container · path ด้านหน้าแตกต่างกันแต่ละเครื่อง แต่ต่อท้ายด้วย `04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push` เหมือนกัน · ไม่ต้องเปิดไฟล์ private key ใน `Devtool_SSH`*

#### ส่วนที่ 1 — สร้าง Docker network `cicd-net`

<!-- lab3-test:host-setup-network -->
```bash
docker network create cicd-net
```

<a href="./images/lab3_powershell_terminal_network_create_pending.svg"><img src="./images/lab3_powershell_terminal_network_create_pending.svg" width="1000" alt="ภาพประกอบ Windows PowerShell ที่โฟลเดอร์แล็บ พิมพ์คำสั่ง docker network create cicd-net รอไว้ ยังไม่ได้รัน"></a>

*ภาพที่ 2ข ภาพประกอบ (ไม่ใช่ภาพหน้าจอจริง) — คำสั่งพิมพ์รอไว้ใน PowerShell ที่โฟลเดอร์แล็บ ยังไม่ได้กด Enter จึงไม่มีผลลัพธ์ · คลิกเพื่อขยาย*

ถ้าขึ้น `already exists` ใช้ network เดิมได้เลย

#### ส่วนที่ 2 — รัน container `devtools`

> [!CAUTION]
> **แล็บนี้ต่างจากแล็บอื่น!** ตอนรัน `devtools` ต้อง mount `Devtool_SSH` ด้วย `-v "${PWD}/Devtool_SSH:/etc/devtools/ssh"` ทุกครั้ง และต้องรันจากโฟลเดอร์แล็บที่มี key pair อยู่ · ถ้าไม่ mount, public key จะไม่ถูกโหลด และ Jenkins จะ SSH ด้วย private key ไม่ได้
>
> private key (`devtoolSSH`) จะนำไปใส่ใน Jenkins Credential ส่วน `devtoolSSH.pub` devtools ติดตั้งให้อัตโนมัติตอน start

<!-- lab3-test:host-setup-devtools -->
```bash
docker run -dit --name devtools --privileged -p 2222:22 --network cicd-net --tmpfs /run --restart unless-stopped -p 3000:3000 -v "${PWD}/Devtool_SSH:/etc/devtools/ssh" devtools:2569_1
```

<a href="./images/lab3_powershell_terminal_devtools_run_pending.svg"><img src="./images/lab3_powershell_terminal_devtools_run_pending.svg" width="1000" alt="ภาพประกอบ Windows PowerShell ที่โฟลเดอร์แล็บ พิมพ์คำสั่ง docker run devtools พร้อม mount Devtool_SSH รอไว้ ยังไม่ได้รัน"></a>

*ภาพที่ 2ค ภาพประกอบ (ไม่ใช่ภาพหน้าจอจริง) — คำสั่ง `docker run` ที่พิมพ์รอไว้ ยังไม่ได้รัน · เป็นคำสั่งบรรทัดเดียว หน้าต่างตัดบรรทัดให้เอง · กรอบเขียวคือ mount `Devtool_SSH` · คลิกเพื่อขยาย*

ตรวจว่า devtools เปิด key login แล้ว:

```bash
docker logs devtools | grep "SSH key"
# [start.sh] SSH key login enabled: /etc/devtools/ssh/devtoolSSH.pub
```

ถ้าขึ้น `SSH key login disabled` แปลว่าไม่ได้รันในโฟลเดอร์แล็บ (mount ผิดที่) หรือไม่ได้ใช้ image `devtools:2569_1` → ลบ `devtools` แล้วทำ 1.1 ใหม่

#### ส่วนที่ 3 — รัน container `jenkins`

ขั้นนี้เป็นการ**สร้างครั้งแรก** · ถ้ามี `jenkins` อยู่แล้ว**ให้เก็บไว้ใช้ต่อ** ห้ามลบหรือสร้างใหม่ (ถ้าหยุดอยู่ใช้ `docker start jenkins`)

<!-- lab3-test:host-setup-jenkins -->
```bash
docker run -d --name jenkins --network cicd-net --restart unless-stopped -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21
```

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

**3.0) เปิดหน้าเพิ่ม credential** — คลิกตามลำดับ **Login → ⚙️ Manage Jenkins → Credentials → System → Global → + Add Credentials** (ภาพที่ 4ก–4ช ภาพหน้าจอจริงจาก Jenkins 2.568.3 คลิกภาพเพื่อขยาย)

**3.0ก) Login** — เปิด `http://localhost:8080` กรอก `admin` / `admin2569` แล้วกด **Sign in**

[![หน้า Sign in to Jenkins](./images/lab3_nav_01_login.png)](./images/lab3_nav_01_login.png)

*ภาพที่ 4ก หน้า **Sign in to Jenkins***

**3.0ข) Dashboard → ไอคอนเฟือง ⚙️** — คลิกไอคอน**เฟือง** (Manage Jenkins) มุมขวาบน ข้างไอคอนแว่นขยาย

[![หน้า Dashboard มีไอคอนเฟือง Manage Jenkins มุมขวาบน](./images/lab3_nav_02_dashboard_large.png)](./images/lab3_nav_02_dashboard_large.png)

*ภาพที่ 4ข หน้า **Dashboard**: มุมขวาบนมีไอคอนแว่นขยาย (ค้นหา) · **เฟือง = Manage Jenkins** · ไอคอนผู้ใช้ · จุดแดงบนเฟืองคือการแจ้งเตือนของระบบ ไม่เกี่ยวกับแล็บนี้ (คลิกภาพเพื่อขยาย)*

**3.0ค) Manage Jenkins → Credentials** — หมวด **Security** คลิก **Credentials** (ไม่ใช่ **Credential Providers**)

[![หน้า Manage Jenkins วงกลมแดงและลูกศรชี้ไทล์ Credentials ในหมวด Security](./images/lab3_nav_03_manage_credentials_annotated.svg)](./images/lab3_nav_03_manage_credentials_annotated.svg)

*ภาพที่ 4ค หน้า **Manage Jenkins** หมวด **Security**: คลิก **Credentials** (วงกลมแดงและลูกศรวาดทับภาพหน้าจอจริง · [ภาพต้นฉบับ](./images/lab3_nav_03_manage.png))*

**3.0ง) Stores scoped to Jenkins → System**

[![หน้า Credentials และตาราง Stores scoped to Jenkins](./images/lab3_nav_04_credentials_large.png)](./images/lab3_nav_04_credentials_large.png)

*ภาพที่ 4ง หน้า **Credentials**: คลิกแถว **System** ในตาราง **Stores scoped to Jenkins** (คลิกภาพเพื่อขยาย)*

**3.0จ) System → Global** (Jenkins รุ่นก่อนเรียกว่า **Global credentials (unrestricted)**)

[![หน้า System แสดง domain Global](./images/lab3_nav_05_system_large.png)](./images/lab3_nav_05_system_large.png)

*ภาพที่ 4จ หน้า **System** (breadcrumb Manage Jenkins / Credentials / System): คลิกลิงก์ **Global** ใต้ปุ่ม **+ Add domain** (บรรทัดใต้ลิงก์เขียน *Credentials that should be available everywhere.*) · ไม่ต้องกด Add domain (คลิกภาพเพื่อขยาย)*

**3.0ฉ) Global → + Add Credentials**

[![หน้า Global ปุ่ม + Add Credentials](./images/lab3_nav_06_global_large.png)](./images/lab3_nav_06_global_large.png)

*ภาพที่ 4ฉ หน้า **Global**: กด **+ Add Credentials** (คลิกภาพเพื่อขยาย)*

**3.1) `devtools-ssh`** — เลือก Kind **SSH Username with private key** แล้วกรอก:

| ช่อง | ค่า |
|---|---|
| Kind | **SSH Username with private key** |
| Scope | Global |
| ID | `devtools-ssh` |
| Description | `SSH key: Jenkins to devtools` |
| Username | `root` |
| Treat username as secret | ไม่ติ๊ก |
| Private Key | เลือก **Enter directly** → กด **Add** → วาง**เนื้อหา**ของไฟล์ `Devtool_SSH/devtoolSSH` (ไม่มีนามสกุล) |
| Passphrase | เว้นว่าง (key ของแล็บไม่มี passphrase) |

**ไฟล์ที่ต้องคัดลอก** — ในโฟลเดอร์ `Devtool_SSH/` มีสองไฟล์ ใช้ไฟล์ **ไม่มีนามสกุล** เท่านั้น:

```text
Devtool_SSH/
├── devtoolSSH       ← ✅ private key → คัดลอกเนื้อหาไปวางใน Jenkins
└── devtoolSSH.pub   ← ❌ public key → ไม่ต้องใช้ (devtools ติดตั้งให้อัตโนมัติ)
```

> `devtoolSSH.pub` ถูกนำไปใส่ใน `/root/.ssh/authorized_keys` ของ devtools **อัตโนมัติ**ตอน container start (ผ่าน `-v "${PWD}/Devtool_SSH:/etc/devtools/ssh"` ในขั้นที่ 1.1) จึง**ไม่ต้อง**วางลงช่อง Key ของ Jenkins

[![ฟอร์ม SSH Username with private key ของ devtools-ssh ก่อนวาง key](./images/lab3_ssh_private_key_form.png)](./images/lab3_ssh_private_key_form.png)

*ภาพที่ 4ช ฟอร์มจริงของ `devtools-ssh` **ก่อนวาง key**: กรอก ID `devtools-ssh` · Username `root` · เลือก **Enter directly** แล้วกด **Add** เพื่อเปิดช่องวาง private key ของตัวเอง · ภาพนี้ยังไม่ได้วาง key จึงไม่มี key แสดง (คลิกภาพเพื่อขยาย)*

**ขั้นตอนคัดลอก–วาง:**

1. เปิดไฟล์ `Devtool_SSH/devtoolSSH` (ไม่มี `.pub`) ด้วย text editor เช่น Notepad / VS Code
2. กด **Ctrl+A** แล้ว **Ctrl+C** เพื่อคัดลอก**เนื้อหาทั้งไฟล์** รวมบรรทัด `-----BEGIN OPENSSH PRIVATE KEY-----` และ `-----END OPENSSH PRIVATE KEY-----` — **ไม่ใช่**คัดลอกชื่อไฟล์หรือ path
3. ใน Jenkins ช่อง **Private Key** เลือก **Enter directly** → กด **Add** → คลิกในช่อง **Key** แล้วกด **Ctrl+V**
4. ช่อง **Passphrase** เว้นว่าง แล้วกด **Create**

[![ฟอร์ม devtools-ssh หลังวาง key (เนื้อหา key ถูกแทนด้วยข้อความตัวอย่าง)](./images/lab3_ssh_private_key_pasted_redacted.png)](./images/lab3_ssh_private_key_pasted_redacted.png)

*ภาพที่ 4ซ ภาพหน้าจอจริงของฟอร์ม `devtools-ssh` **หลังวาง key** ในช่อง **Key** · เพื่อปกป้องความลับ เนื้อหาที่วางในภาพถูก**แทนด้วยข้อความตัวอย่าง (placeholder) ก่อนวาง** — ข้อความในภาพ**ไม่ใช่ key จริง ใช้งานไม่ได้ ห้ามนำไปใช้** · ของจริงต้องเห็นบรรทัด `BEGIN`/`END` และเนื้อหาจากไฟล์ `devtoolSSH` ของตัวเอง (คลิกภาพเพื่อขยาย)*

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
| **ข. ฝึกเขียนเอง** | พิมพ์ไฟล์ตามข้อ 4.3 ใน repository สาธารณะของตัวเอง แล้ว commit/push (หมายเหตุท้ายข้อ 4.3) | Repository URL, Branch และ Script Path ของตัวเอง |

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

**ปุ่มสั่ง Build อยู่ที่ไหน** — หลัง **Save** จะกลับมาหน้า job `docker-build-push` ปุ่มอยู่ที่เมนูด้านซ้ายใต้ **Changes**: การรันครั้งแรกกด **Build Now** · หลังจาก Jenkins อ่าน `parameters` จาก `Jenkinsfile` แล้ว (หลังรันครั้งแรก) ปุ่มตำแหน่งเดียวกันจะเปลี่ยนเป็น **Build with Parameters** (ใช้ในข้อ 6)

[![เมนูด้านซ้ายของ job docker-build-push มีปุ่ม Build with Parameters](./images/lab3_build_action_large.png)](./images/lab3_build_action_large.png)

*ภาพที่ 9ก ภาพหน้าจอจริงของเมนู job `docker-build-push` (2026-09-27) **ก่อนกดปุ่ม** — ไม่ใช่ผลการ build · job นี้เคยรันมาแล้วจึงแสดง **Build with Parameters** · job ที่เพิ่งสร้างใหม่จะเห็น **Build Now** ที่ตำแหน่งเดียวกัน*

**4.3) อ่าน `Jenkinsfile` ทีละ stage ตามลำดับที่รัน**

โค้ดด้านล่างตัดมาจาก [`Jenkinsfile`](./Jenkinsfile) ตรงตัวทุกบรรทัด (เปิดไฟล์เพื่อดูฉบับเต็ม) · Jenkins อ่านไฟล์นี้จาก GitHub เองก่อนเริ่ม ส่วน `skipDefaultCheckout()` บอกว่า Jenkins ไม่ต้อง checkout repository ลง workspace ของตัวเอง

**ค่าที่ทุก stage ใช้ร่วมกัน** — `environment` ประกาศคำสั่ง SSH และ path ต่าง ๆ ไว้ครั้งเดียว:

```groovy
  environment {
    SSH_DEVTOOLS = 'ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@devtools'
    GIT_URL      = 'https://github.com/Tuchsanai/DevTools.git'
    APP_PATH     = '04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop'
    WORK_DIR     = '/root/lab3-work/DevTools'      // ที่ clone repo บน devtools
    AUTH_DIR     = '/root/lab3-work/docker-auth'   // ไฟล์ login Docker Hub ชั่วคราวบน devtools
    APP_NAME     = 'catfood-shop'
    IMAGE_TAG    = "lab3-${env.BUILD_NUMBER}"
    LOCAL_IMAGE  = "catfood-shop:lab3-${env.BUILD_NUMBER}"
  }
```

- `SSH_DEVTOOLS` คือคำสั่ง SSH เข้า `root@devtools` · `accept-new` ให้ SSH จำ host key ของ devtools เองตอนต่อครั้งแรก และปฏิเสธถ้า key เปลี่ยนภายหลัง · `BatchMode=yes` ห้ามถามรหัสผ่าน key ใช้ไม่ได้ก็ล้มทันที
- ทุก stage ห่อคำสั่งด้วย `sshagent(credentials: ['devtools-ssh']) { ... }` ให้ `ssh` ใช้ private key จาก credential `devtools-ssh` (ข้อ 3.1) · รูปแบบ `$SSH_DEVTOOLS "A=... bash -ex" <<'EOF' ... EOF` ส่งสคริปต์หลายบรรทัดไปรัน**บน devtools** โดยส่งค่าไปเป็นตัวแปรนำหน้า `bash` (`-e` หยุดเมื่อคำสั่งใดล้ม `-x` พิมพ์คำสั่งลง console)

**Stage 1 — Connect**

```groovy
    stage('Connect') {
      steps {
        script {
          if (!(params.APP_VERSION ==~ /[0-9]+\.[0-9]+\.[0-9]+/)) {
            error 'APP_VERSION ต้องเป็นรูปแบบ X.Y.Z เช่น 1.0.0'
          }
        }
        sshagent(credentials: ['devtools-ssh']) {
          sh '$SSH_DEVTOOLS "hostname && whoami && docker --version && git --version"'
        }
      }
    }
```

ตรวจบน Jenkins ก่อนว่า `APP_VERSION` เป็นรูปแบบ `X.Y.Z` แล้ว SSH ด้วย private key ไปถาม `hostname`, `whoami` และเวอร์ชัน Docker/git ของ devtools เพื่อยืนยันว่าต่อได้จริง (ครั้งแรก SSH จะจำ host key ไว้ตรงนี้)

**Stage 2 — Clone** (ใน `sshagent` เหมือน Connect)

```groovy
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
```

`git clone` รัน**ข้างใน devtools** ลง `WORK_DIR` (`/root/lab3-work/DevTools`) · ลบของเก่าก่อน แล้ว sparse clone เฉพาะโฟลเดอร์ `catfood-shop` พร้อมแสดง commit และรายชื่อไฟล์

**Stage 3 — Build**

```groovy
          sh '''
$SSH_DEVTOOLS "SRC=$WORK_DIR/$APP_PATH IMAGE=$LOCAL_IMAGE VERSION=$APP_VERSION BUILD=$BUILD_NUMBER bash -ex" <<'EOF'
cd "$SRC"
COMMIT=$(git rev-parse --short HEAD)
TIME=$(date -u +%Y-%m-%dT%H:%M:%SZ)
docker build --build-arg APP_VERSION="$VERSION" --build-arg BUILD_NUMBER="$BUILD" --build-arg GIT_COMMIT="$COMMIT" --build-arg BUILD_TIME="$TIME" -t "$IMAGE" .
docker image ls "$IMAGE"
EOF
'''
```

เข้าโฟลเดอร์ซอร์สที่เพิ่ง clone บน devtools แล้ว `docker build` เป็น image `catfood-shop:lab3-<เลข build>` โดยฝังเวอร์ชัน เลข build, commit และเวลาลงใน image

**Stage 4 — Test**

```groovy
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
```

รัน image ใหม่เป็น container ชั่วคราว `catfood-test` รอให้ `healthy` แล้วตรวจว่า `/api/health` ตอบ `version` และ `build` ตรงกับ build นี้ · `trap ... EXIT` ลบ container ทดสอบเสมอแม้ test ไม่ผ่าน

**Stage 5 — Push**

```groovy
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
```

`withCredentials` ดึง username/token จาก credential `dockerhub` · token ส่งทาง stdin เข้า `--password-stdin` และ `set +x` ปิดการพิมพ์คำสั่งบรรทัดนั้น token จึงไม่อยู่ใน command line หรือ console · จากนั้น tag เป็น `<DOCKER_USER>/catfood-shop:lab3-<เลข build>` แล้ว push ขึ้น Docker Hub และ `trap` ลบไฟล์ login ชั่วคราวใน `AUTH_DIR` เสมอ

**Stage 6 — Deploy** (ใน `withCredentials` + `sshagent` เหมือน Push)

```groovy
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
```

login อีกครั้ง ลบ image ในเครื่องแล้ว **pull จาก Docker Hub** เพื่อพิสูจน์ว่า image บน Hub ใช้ได้จริง → ลบ `catfood-web` ตัวเดิม → รันตัวใหม่ที่ port `3000` → รอ `healthy` แล้ว `curl` ต้องได้เวอร์ชันและ build ตรง (ช่วงสั้น ๆ ระหว่างสลับ container ร้านจะปิดชั่วคราว)

**หลังจบทุก stage** — `post` บอก URL ของร้าน และลบไฟล์ login ซ้ำอีกชั้นกรณี build หยุดกลางทาง:

```groovy
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
```

หลัง stage **Deploy** เขียว (และ `post` ลบไฟล์ login แล้ว) ให้เปิด **[ร้าน Meow Mart บนเครื่อง lab ของเรา — http://localhost:3000](http://localhost:3000)** ในเบราว์เซอร์ของเครื่องที่รัน container `devtools` (ลิงก์ใช้ได้เฉพาะหลัง Deploy สำเร็จ) แล้วตรวจ chip บนแถบด้านบนว่าตรงกับ `APP_VERSION` และเลข build ที่เพิ่งรัน หน้าร้านจะมีลักษณะแบบนี้:

[![หน้าร้าน Meow Mart (ภาพเดิม)](./images/lab3_sib_app_v110_crop.png)](./images/lab3_sib_app_v110.png)

*ภาพที่ 10 🕰️ **ภาพเดิม — ตัวอย่างผลลัพธ์จากการรันจริงรอบก่อน** (2026-09-26, workflow รุ่นก่อน, ซอร์สร้านเดียวกัน) chip แสดง `v1.1.0 · build #2` · ภาพตัดเฉพาะหน้าเว็บ ไม่มีแถบ URL ของเบราว์เซอร์ · ใช้ดูหน้าตาร้านเท่านั้น **ไม่ใช่ผลยืนยันของ `Jenkinsfile` ฉบับนี้** ซึ่งยังไม่ได้รันจริงบน Jenkins · build แรกของเราต้องเห็น `v1.0.0 · build #1`*

> 📌 **ทางเลือก ข (ฝึกเขียนเอง):** วางไฟล์ที่ root ของ repository สาธารณะของตัวเอง → `git add Jenkinsfile && git commit -m "Add LAB 3 Jenkinsfile" && git push` → job **Configure** ตั้ง Repository URL, Branch Specifier และ Script Path (`Jenkinsfile`) เป็นของตัวเอง · ทางเลือก ก ไม่ต้องทำอะไรเพิ่ม

## ขั้นที่ 5 — Build Now แล้วดู 6 stage ทำงาน

หน้า job `docker-build-push` กด **Build Now** ที่เมนูด้านซ้าย (ตำแหน่งตามภาพที่ 9ก) — build แรกใช้ค่า default `APP_VERSION=1.0.0` และ tag `lab3-1` (หลังรันครั้งแรกจึงมีเมนู **Build with Parameters**)

[![Console Output ช่วงเริ่ม build (ภาพเดิม)](./images/lab3_scm_08_console_obtained_crop.png)](./images/lab3_scm_08_console_obtained.png)

*ภาพที่ 11 🕰️ **ภาพเดิม** Console Output ช่วงแรก: `Obtained .../Jenkinsfile from git https://github.com/Tuchsanai/DevTools.git` แล้วเข้า stage `(Connect)` ทันที ไม่มี `Declarative: Checkout SCM` · ช่วงแรกนี้เหมือนกันในไฟล์ฉบับใหม่ ส่วน log ของแต่ละ stage จะต่างจากภาพ*

✅ สิ่งที่ต้องเห็นใน Console Output (ยังไม่มีภาพของไฟล์ฉบับนี้):

- **Connect:** ครั้งแรกที่ jenkins ยังไม่รู้จัก devtools จะมี `Warning: Permanently added 'devtools' (ED25519) to the list of known hosts.` (build ต่อไปไม่ขึ้นอีก) · บรรทัดที่ขึ้นต้นด้วย `[ssh-agent]` บอกว่าใช้ credential ของ `root` · ผล `devtools` / `root` / `Docker version ...` / `git version ...`
- **Clone:** บรรทัด `+ git clone ...` ตามด้วย commit ล่าสุด และรายชื่อไฟล์ของ `catfood-shop`
- **Test:** บรรทัด `version:1.0.0,build:1,` ถูก `grep` เจอ
- **Push:** `Login Succeeded` แล้ว `lab3-1: digest: sha256:... size: ...` · token แสดงเป็น `****`
- **Deploy:** `Status: Downloaded newer image for <DOCKER_USER>/catfood-shop:lab3-1` → health ตรง → `เปิดร้านได้ที่ http://localhost:3000 (v1.0.0 build #1)`
- หน้า Stages ต้องเขียวครบ 6 stage: Connect → Clone → Build → Test → Push → Deploy

เมื่อ Deploy สำเร็จ เปิด [หน้าร้าน Meow Mart — http://localhost:3000](http://localhost:3000) chip บนแถบด้านบนต้องเป็น `v1.0.0 · build #1` (หน้าตาร้านเหมือนภาพที่ 10)

## ขั้นที่ 6 — ออกเวอร์ชันใหม่ `APP_VERSION=1.1.0`

job `docker-build-push` → **Build with Parameters** → `APP_VERSION` = `1.1.0` → **Build** (มี parameter เดียว)

✅ build #2 เขียวครบ 6 stage · Deploy แทน `catfood-web` ของ build #1 · เปิด [หน้าร้าน Meow Mart — http://localhost:3000](http://localhost:3000) chip ต้องเป็น `v1.1.0 · build #2` (ตรงกับภาพที่ 10 ในข้อ 4.3)

[![ส่วน Deployment info ของร้าน (ภาพเดิม)](./images/lab3_sib_app_deployment_crop.png)](./images/lab3_sib_app_deployment.png)

*ภาพที่ 12 🕰️ **ภาพเดิม** ส่วน Deployment info ท้ายหน้าร้าน: Version, Jenkins build, Git commit, Built at และ Container ที่ตอบ*

หน้า **Tags** ของ repository `catfood-shop` บน Docker Hub ต้องมี `lab3-1` และ `lab3-2`:

[![หน้า Tags บน Docker Hub (ภาพเดิม)](./images/lab3_scm_dockerhub_tags_crop.png)](./images/lab3_scm_dockerhub_tags.png)

*ภาพที่ 13 🕰️ **ภาพเดิม** หน้า Tags บน Docker Hub ของรอบทดสอบเดิม (ชื่อ tag ในภาพเป็น `lab3-sibling-20260926r2-*`) · ของเราจะเป็น `lab3-1`, `lab3-2`*
