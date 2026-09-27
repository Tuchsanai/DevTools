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

`docker run` แค่เริ่ม container — Jenkins ข้างในยังต้องบูตสักครู่ และการติดตั้งครั้งแรกยังต้องผ่าน **Setup Wizard** (ปลดล็อก → ติดตั้ง plugin → สร้างผู้ดูแล) ลำดับเดียวกับการทดลอง **Verify / Unlock / Setup Wizard** ใน [LAB 1](../001_LAB_Jenkins_On_Docker/README.md) (เปิดอ่านอ้างอิงได้ ไม่ต้องทำ LAB 1 ซ้ำ) · คำสั่งในขั้นนี้พิมพ์ใน **terminal ของ host เดียวกับขั้นที่ 1** ไม่ใช่ใน container `devtools`

(ไม่บังคับ) ตรวจว่า Jenkins พร้อมแล้ว:

```bash
docker ps --filter name=jenkins
docker logs --tail 30 jenkins
```

✅ STATUS เป็น `Up ...` และใน log มี `Jenkins is fully up and running` · ถ้ายังไม่เห็นให้รอสักครู่แล้วดู log อีกครั้ง

> 🔁 **ถ้าเคยตั้งค่า Jenkins ไว้แล้ว** (ใช้ `jenkins_home` เดิม) หน้า http://localhost:8080 จะขึ้น **Sign in** แทนหน้า Unlock → login ด้วยผู้ดูแลเดิม แล้วข้ามไปข้อ 2.7 ไม่ต้องอ่านรหัสปลดล็อกหรือรีเซ็ตใหม่

**ติดตั้งครั้งแรก:** Jenkins สร้างไฟล์ `initialAdminPassword` ไว้**ภายใน container** คำสั่ง `docker exec` ด้านล่างเข้าไปอ่านไฟล์นั้นออกมาแสดง

<!-- lab3-test:unlock -->
```bash
docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

✅ ได้รหัสเลขฐานสิบหก 32 ตัวหนึ่งบรรทัด — คัดลอก**ทั้งบรรทัด** (แต่ละเครื่องได้ไม่เหมือนกัน ห้ามเผยแพร่) · ถ้าขึ้น `No such file or directory` มักแปลว่า Jenkins ยังบูตไม่เสร็จ ให้รอสักครู่ ดู `docker logs --tail 30 jenkins` แล้วลองใหม่ **ห้ามลบ** container หรือ volume

> 📷 ภาพที่ 3ก–3ฉ **นำมาจาก LAB 1** เป็นขั้นตอน Setup Wizard เดียวกัน ไม่ได้ถ่ายใหม่จาก LAB 3

**2.1) ปลดล็อก** เปิด **http://localhost:8080** บนเครื่องที่ทำแล็บ วางรหัสที่คัดลอกไว้ในช่อง **Administrator password** แล้วกด **Continue** — จากนั้น Wizard จะพาติดตั้ง plugin (2.2–2.3) แล้วให้สร้างบัญชีผู้ดูแลของเราเอง (2.4)

![หน้า Unlock Jenkins (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_01_unlock.png)

*ภาพที่ 3ก (จาก LAB 1) หน้า **Unlock Jenkins***

**2.2) เลือก Install suggested plugins** ให้ Jenkins ติดตั้งชุด plugin มาตรฐานให้อัตโนมัติ

![หน้า Customize Jenkins (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_02_plugins.png)

*ภาพที่ 3ข (จาก LAB 1) **Install suggested plugins** มี Pipeline, Git และ Pipeline Graph View แต่**ไม่มี SSH Agent** (ติดตั้งเพิ่มในข้อ 2.7)*

**2.3) รอติดตั้ง plugin** ประมาณ 2–4 นาที ถ้าบางตัวขึ้น **Retry** ให้กด Retry

![กำลังติดตั้ง plugin (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_03_installing.png)

*ภาพที่ 3ค (จาก LAB 1) เครื่องหมาย ✓ คือ plugin ที่ติดตั้งเสร็จแล้ว*

**2.4) สร้างผู้ดูแลระบบ** กรอกตามภาพ แล้วกด **Save and Continue** — รหัสปลดล็อกใน 2.1 ใช้ครั้งเดียว ต่อไป login ด้วยบัญชีที่สร้างตรงนี้

![แบบฟอร์ม Create First Admin User (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_04_admin_user.png)

*ภาพที่ 3ง (จาก LAB 1) Username `admin` · Password `admin2569` (2 ช่อง) · Full name `Admin` · Email `student@example.com`*

**2.5) คง Jenkins URL เป็น `http://localhost:8080/`** แล้วกด **Save and Finish**

![Instance Configuration (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_05_instance_url.png)

*ภาพที่ 3จ (จาก LAB 1) หน้า **Instance Configuration***

**2.6) กด Start using Jenkins**

![Jenkins is ready! (ภาพจาก LAB 1)](./images/lab3_setup_from_lab1_06_ready.png)

*ภาพที่ 3ฉ (จาก LAB 1) Setup Wizard เสร็จแล้ว*

**2.7) ติดตั้ง plugin SSH Agent** — plugin นี้ให้ `Jenkinsfile` ใช้คำสั่ง `sshagent(credentials: ['devtools-ssh']) { ... }` ซึ่งโหลด private key จาก credential เข้า `ssh-agent` ชั่วคราวเฉพาะในบล็อก คำสั่ง `ssh` ข้างในจึงใช้ key ได้โดยไม่ต้องมีไฟล์ key บนดิสก์ของ job · ตัว credential `devtools-ssh` จะสร้างใน**ขั้นที่ 3** ตอนนี้ติดตั้งแค่ plugin

1. **เปิดหน้าจัดการ plugin** — คลิก ⚙️ **Manage Jenkins** (มุมขวาบน) แล้วคลิก **Plugins**

<a href="./images/lab3_ssh_agent_01_manage.png"><img src="./images/lab3_ssh_agent_01_manage.png" width="1000" alt="หน้า Manage Jenkins มีลิงก์ Plugins ในหมวด System Configuration"></a>

*ภาพที่ 3ช หน้า **Manage Jenkins** → คลิก **Plugins***

2. **ค้นหาและเลือก SSH Agent** — เมนูซ้ายเลือก **Available plugins** → ช่องค้นหาพิมพ์ `SSH Agent` → ติ๊กแถว **SSH Agent** (plugin ID `ssh-agent`) → กด **Install**
   - ⚠️ อย่าเลือก **SSH Build Agents** ซึ่งเป็นคนละ plugin (ใช้ต่อ agent node)
   - ถ้าค้นแล้วไม่เจอใน Available plugins อาจติดตั้งไว้แล้ว → ข้ามไปตรวจที่ข้อ 4

<a href="./images/lab3_ssh_agent_02_available.png"><img src="./images/lab3_ssh_agent_02_available.png" width="1000" alt="หน้า Available plugins ค้นหา SSH Agent พบแถว SSH Agent และปุ่ม Install"></a>

*ภาพที่ 3ซ **Available plugins** ค้นหา `SSH Agent` → ติ๊กแถว **SSH Agent** → **Install***

3. **รอติดตั้งเสร็จ** — หน้า **Download progress** ต้องขึ้น **Success** ทั้งแถว **SSH Agent** และ **Loading plugin extensions** · plugin นี้โหลดได้ทันทีโดยไม่ต้อง restart จึง**ไม่ต้อง**ติ๊ก *Restart Jenkins when installation is complete* (ในการทดสอบจริงของแล็บนี้ติดตั้งสำเร็จโดยไม่ restart)

<a href="./images/lab3_ssh_agent_03_success.png"><img src="./images/lab3_ssh_agent_03_success.png" width="1000" alt="หน้า Download progress แสดง SSH Agent และ Loading plugin extensions เป็น Success"></a>

*ภาพที่ 3ฌ **SSH Agent** และ **Loading plugin extensions** ขึ้น **Success***

4. **ตรวจว่าติดตั้งแล้ว** — เมนูซ้ายเลือก **Installed plugins** → ค้นหา `SSH Agent` ต้องเห็นแถว **SSH Agent** และสวิตช์เปิดใช้งาน (enabled) ✅ พร้อมไปขั้นที่ 3 สร้าง Credentials

<a href="./images/lab3_ssh_agent_04_installed.png"><img src="./images/lab3_ssh_agent_04_installed.png" width="1000" alt="หน้า Installed plugins ค้นหา SSH Agent พบ plugin เปิดใช้งานอยู่"></a>

*ภาพที่ 3ญ **Installed plugins** มี **SSH Agent** เปิดใช้งานอยู่*

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

<a href="./images/lab3_windows_private_key_annotated.svg"><img src="./images/lab3_windows_private_key_annotated.svg" width="1000" alt="ภาพ Windows File Explorer จริงของโฟลเดอร์ Devtool_SSH วงรีแดงที่ไฟล์ devtoolSSH (private key) ส่วน devtoolSSH.pub ไม่ได้เลือก"></a>

*ภาพที่ 4ซ-1 ภาพหน้าจอ Windows File Explorer จริง (ครอปเฉพาะ path และรายการไฟล์ · ปิดทับ path ส่วนตัวด้วยแถบดำ · คลิกเพื่อขยาย) เปิดโฟลเดอร์ `Devtool_SSH` แล้วใช้ไฟล์ **`devtoolSSH` ที่ไม่มีนามสกุล** (วงรีแดง) — **ไม่ใช้** `devtoolSSH.pub` · คัดลอก**เนื้อหาในไฟล์**ทั้งหมดรวมบรรทัด `BEGIN`/`END` ไปวางในช่อง **Private Key** ของ Jenkins — **ไม่ใช่**วางชื่อไฟล์หรือ path*

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

**4.3) อ่าน `Jenkinsfile` ทั้งไฟล์ แล้วดูคำอธิบายทีละส่วน**

โค้ดด้านล่างคือ [`Jenkinsfile`](./Jenkinsfile) **ทั้งไฟล์ ตรงตัวทุกบรรทัด** · Jenkins อ่านไฟล์นี้จาก GitHub เองก่อนเริ่ม (ตาม Script Path ในข้อ 4.2) · คำอธิบายภาษาไทยของแต่ละส่วนอยู่ถัดจากโค้ด เรียงตามลำดับบนลงล่างของไฟล์

> ⚠️ **ไฟล์ฉบับนี้แก้แล้ว แต่ยังไม่ได้ push ขึ้น GitHub** — ไฟล์ด้านล่างเพิ่ม 2 บรรทัดใน `environment` (comment หนึ่งบรรทัด + `APP_VERSION  = "${params.APP_VERSION}"`) จาก commit `a8d0c0b` บน `main` · ไฟล์ฉบับแก้นี้ทดสอบบน Jenkins จริงโดยให้ job อ่าน `Jenkinsfile` จาก **Git repo จำลองในเครื่อง** (ไม่ใช่ GitHub) ส่วนซอร์สร้านยัง clone จาก GitHub ตามปกติ · **จนกว่าจะ push ไฟล์นี้** job ที่อ่านจาก GitHub ตามข้อ 4.2 จะยังได้ไฟล์เดิม และ **Build Now ครั้งแรกจะล้มที่ Test** (รายละเอียดในข้อ 5)

```groovy
// LAB 3 — Jenkins สั่ง devtools ผ่าน SSH ด้วย key: Connect → Clone → Build → Test → Push → Deploy
// ต้องมี: plugin "SSH Agent" · credential devtools-ssh (SSH key) และ dockerhub (username + token)
// ทุกคำสั่ง git/docker รันบน devtools: Jenkins แค่ส่งคำสั่งไปทาง SSH

pipeline {
  agent any

  options {
    disableConcurrentBuilds()   // ทุก build ใช้โฟลเดอร์ ชื่อ container และ port 3000 เดียวกัน ห้ามรันซ้อน
    skipDefaultCheckout()       // Jenkins ไม่ต้อง checkout repo เอง devtools clone ใน stage Clone
  }

  parameters {
    string(name: 'APP_VERSION', defaultValue: '1.0.0', description: 'เวอร์ชันรูปแบบ X.Y.Z ที่แสดงบนหน้าเว็บ')
  }

  environment {
    // accept-new: จำ host key ของ devtools ครั้งแรก ถ้าเปลี่ยนภายหลังจะปฏิเสธ · BatchMode: ไม่ถามรหัสผ่าน
    SSH_DEVTOOLS = 'ssh -o StrictHostKeyChecking=accept-new -o BatchMode=yes root@devtools'
    AUTH_DIR     = '/root/lab3-work/docker-auth'   // ไฟล์ login Docker Hub ชั่วคราวบน devtools
    IMAGE        = "catfood-shop:lab3-${env.BUILD_NUMBER}"
    // build แรก (Build Now) Jenkins ยังไม่รู้จัก parameter จึงไม่ส่ง $APP_VERSION ให้ sh: กำหนดจาก params เอง
    APP_VERSION  = "${params.APP_VERSION}"
  }

  stages {
    stage('Connect') {
      steps {
        script {
          // ค่านี้ถูกส่งต่อเข้า shell บน devtools จึงต้องเป็นตัวเลขกับจุดเท่านั้น
          if (!(params.APP_VERSION ==~ /[0-9]+\.[0-9]+\.[0-9]+/)) {
            error 'APP_VERSION ต้องเป็นรูปแบบ X.Y.Z เช่น 1.0.0'
          }
        }
        sshagent(credentials: ['devtools-ssh']) {
          sh '$SSH_DEVTOOLS "hostname && whoami && docker --version && git --version"'
        }
      }
    }

    stage('Clone') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
            $SSH_DEVTOOLS bash -ex <<'EOF'
              rm -rf /root/lab3-work/DevTools
              git clone --depth 1 --filter=blob:none --sparse \
                https://github.com/Tuchsanai/DevTools.git /root/lab3-work/DevTools
              cd /root/lab3-work/DevTools
              git sparse-checkout set 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop
              git log -1 --oneline
              ls 04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop
            EOF
            '''.stripIndent()
        }
      }
    }

    stage('Build') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
            $SSH_DEVTOOLS "IMAGE=$IMAGE APP_VERSION=$APP_VERSION BUILD_NUMBER=$BUILD_NUMBER bash -ex" <<'EOF'
              cd /root/lab3-work/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop
              COMMIT=$(git rev-parse --short HEAD)
              docker build \
                --build-arg APP_VERSION="$APP_VERSION" \
                --build-arg BUILD_NUMBER="$BUILD_NUMBER" \
                --build-arg GIT_COMMIT="$COMMIT" \
                --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
                -t "$IMAGE" .
              docker image ls "$IMAGE"
            EOF
            '''.stripIndent()
        }
      }
    }

    stage('Test') {
      steps {
        sshagent(credentials: ['devtools-ssh']) {
          sh '''
            $SSH_DEVTOOLS "IMAGE=$IMAGE APP_VERSION=$APP_VERSION BUILD_NUMBER=$BUILD_NUMBER bash -ex" <<'EOF'
              docker rm -f catfood-test || true
              docker run -d --name catfood-test "$IMAGE"
              trap 'docker rm -f catfood-test' EXIT   # ลบ container ทดสอบเสมอ แม้ test ไม่ผ่าน
              for i in $(seq 1 30); do
                [ "$(docker inspect -f '{{.State.Health.Status}}' catfood-test)" = healthy ] && break
                sleep 1
              done
              docker exec catfood-test wget -qO- http://127.0.0.1:3000/api/health |
                tr -d '"' | grep -F "version:$APP_VERSION,build:$BUILD_NUMBER,"
            EOF
            '''.stripIndent()
        }
      }
    }

    stage('Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
                         usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
          sshagent(credentials: ['devtools-ssh']) {
            // token ส่งทาง stdin เข้า --password-stdin: ไม่อยู่ใน command line และ console
            sh '''
              set +x
              echo "$HUB_TOKEN" | $SSH_DEVTOOLS "umask 077; docker --config $AUTH_DIR login -u $HUB_USER --password-stdin"
              set -x
              $SSH_DEVTOOLS docker tag $IMAGE $HUB_USER/$IMAGE
              $SSH_DEVTOOLS docker --config $AUTH_DIR push $HUB_USER/$IMAGE
              $SSH_DEVTOOLS docker image rm $IMAGE
              '''.stripIndent()
          }
        }
      }
    }

    stage('Deploy') {
      steps {
        // ใช้ HUB_USER ตั้งชื่อ image และใช้ไฟล์ login จาก stage Push (post ลบให้ตอนจบ)
        withCredentials([usernamePassword(credentialsId: 'dockerhub',
                         usernameVariable: 'HUB_USER', passwordVariable: 'HUB_TOKEN')]) {
          sshagent(credentials: ['devtools-ssh']) {
            sh '''
              $SSH_DEVTOOLS "AUTH_DIR=$AUTH_DIR IMAGE=$HUB_USER/$IMAGE APP_VERSION=$APP_VERSION BUILD_NUMBER=$BUILD_NUMBER bash -ex" <<'EOF'
                docker image rm "$IMAGE"                  # ลบ image ในเครื่อง เพื่อให้ pull มาจาก Docker Hub จริง
                docker --config "$AUTH_DIR" pull "$IMAGE"
                docker rm -f catfood-web || true          # ลบร้านเวอร์ชันเดิม
                docker run -d --name catfood-web --restart unless-stopped -p 3000:3000 "$IMAGE"
                for i in $(seq 1 30); do
                  [ "$(docker inspect -f '{{.State.Health.Status}}' catfood-web)" = healthy ] && break
                  sleep 1
                done
                curl -fsS http://localhost:3000/api/health |
                  tr -d '"' | grep -F "version:$APP_VERSION,build:$BUILD_NUMBER,"
              EOF
              '''.stripIndent()
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
      // ลบไฟล์ login Docker Hub บน devtools เสมอ ทั้งตอนสำเร็จและตอน build ล้มกลางทาง
      sshagent(credentials: ['devtools-ssh']) {
        sh '$SSH_DEVTOOLS "rm -rf $AUTH_DIR" || true'
      }
    }
  }
}
```

**คำสั่งแต่ละส่วนรันที่เครื่องไหน** — จุดสำคัญที่สุดของไฟล์นี้:

| ส่วนของ `Jenkinsfile` | รันที่ | ตัวอย่าง |
|---|---|---|
| โค้ด Groovy ของ pipeline (`script { if ... }`, `error`, `echo`, `"${params...}"`) | **Jenkins** | ตรวจ `APP_VERSION` ใน Connect, ข้อความใน `post` |
| บรรทัดใน `sh '...'` | shell บน **Jenkins** (`agent any` คือ node ของ Jenkins ในแล็บนี้) | `set +x`, `echo "$HUB_TOKEN" \|`, การแทนค่า `$IMAGE` ที่อยู่นอก heredoc |
| คำสั่งหลัง `$SSH_DEVTOOLS` และสคริปต์ใน `<<'EOF' ... EOF` | **devtools** (ปลายทาง SSH) | `git clone`, `docker build/run/push/pull`, `curl` |

**ส่วนหัว (comment 3 บรรทัดแรก)** — บรรทัดที่ขึ้นต้นด้วย `//` เป็น comment Jenkins ไม่รัน · บอกลำดับ 6 stage, สิ่งที่ต้องเตรียมก่อน (plugin **SSH Agent** จากข้อ 2.7 และ credential `devtools-ssh`, `dockerhub` จากขั้นที่ 3) และหลักของแล็บว่าคำสั่ง git/docker ทุกคำสั่งรันบน devtools

**`pipeline { agent any ... }`** — `pipeline` คือบล็อกนอกสุดของ Declarative Pipeline ทุกส่วนต้องอยู่ข้างใน · `agent any` ให้ Jenkins เลือก node ที่ว่างมารัน `sh` ในแล็บนี้มีแค่ตัว Jenkins เอง คำสั่ง `ssh` จึงออกจาก container `jenkins`

**`options`** — สองบรรทัดนี้จำเป็นต้องมี:

- `disableConcurrentBuilds()` ถ้ากด Build ซ้อนกัน build หนึ่งจะลบโฟลเดอร์ clone, ไฟล์ login หรือ container ของอีก build ทิ้ง จึงให้รอคิวทีละ build
- `skipDefaultCheckout()` ไม่ให้ Jenkins clone repository ทั้งก้อนลง workspace ของตัวเองโดยไม่มีใครใช้ ซอร์สที่ build มีชุดเดียวคือที่ devtools clone ใน stage Clone

**`parameters`** — มีตัวเดียวคือ `APP_VERSION` ชนิด `string` ค่า default `1.0.0` · Jenkins จะรู้จัก parameter นี้หลังอ่านไฟล์ครั้งแรก เมนู **Build with Parameters** จึงมาหลังรันครั้งแรก (ข้อ 6) · ในโค้ด Groovy อ่านค่าได้ที่ `params.APP_VERSION`

**`environment`** — ค่าที่ทุก stage ใช้ร่วมกัน มีสี่ค่า ค่าอื่น (URL ของ repo, path ของโฟลเดอร์) เขียนตรง ๆ ในจุดที่ใช้ · ค่าในบล็อกนี้กลายเป็นตัวแปร shell ใน `sh` ทุกตัว:

- `SSH_DEVTOOLS` คือคำสั่ง SSH เข้า `root@devtools` · `accept-new` ให้ SSH จำ host key ของ devtools เองตอนต่อครั้งแรก และปฏิเสธถ้า key เปลี่ยนภายหลัง · `BatchMode=yes` ห้ามถามรหัสผ่าน key ใช้ไม่ได้ก็ล้มทันที
- `AUTH_DIR` คือโฟลเดอร์**บน devtools** ที่ `docker --config` เก็บไฟล์ login Docker Hub ชั่วคราว (ไม่ใช้ไฟล์ login ปกติของ root) · `post` ลบทิ้งตอนจบ
- `IMAGE` คือชื่อ image ในเครื่อง `catfood-shop:lab3-<เลข build>` (`${env.BUILD_NUMBER}` คือเลข build ที่ Jenkins ตั้งให้) ส่วนชื่อบน Docker Hub คือ `$HUB_USER/$IMAGE`
- `APP_VERSION = "${params.APP_VERSION}"` ส่งค่า parameter ให้ `sh` เป็น `$APP_VERSION` **ทุก build รวมถึง build แรก** · ตอนกด **Build Now** ครั้งแรก job ยังไม่มี parameter Jenkins จึงไม่ตั้งตัวแปร `$APP_VERSION` ให้ `sh` เอง (แม้ `params.APP_VERSION` ใน Groovy จะได้ค่า default `1.0.0`) · ถ้าไม่มีบรรทัดนี้ build แรกจะส่ง `APP_VERSION=` ค่าว่างไปที่ devtools และ stage Test ล้มเพราะหา `version:,build:1,` ไม่เจอ (เจอจริงตอนทดสอบแล็บ)

รูปแบบที่ทุก stage ใช้ซ้ำ:

- ทุก stage (และ `post`) ห่อคำสั่งด้วย `sshagent(credentials: ['devtools-ssh']) { ... }` ให้ `ssh` บน Jenkins ใช้ private key จาก credential `devtools-ssh` (ข้อ 3.1) โดยไม่ต้องเขียน key ลงไฟล์ใน `Jenkinsfile` · console จะแสดง `[ssh-agent] Started.` ตอนเข้า และ `[ssh-agent] Stopped.` ตอนออกจากบล็อก
- รูปแบบ `$SSH_DEVTOOLS "A=... bash -ex" <<'EOF' ... EOF` ส่งสคริปต์หลายบรรทัดไปรัน**บน devtools** (`-e` หยุดเมื่อคำสั่งใดล้ม `-x` พิมพ์คำสั่งลง console) · `.stripIndent()` ตัดช่องว่างหน้าบรรทัดออกก่อนรัน โค้ดจึงย่อหน้าตามโครงได้ และ `EOF` ตัวปิดยังอยู่ต้นบรรทัดตามที่ shell ต้องการ
- **ใครแทนค่าตัวแปร:** `'''...'''` เป็น string แบบ single quote ของ Groovy Groovy จึงไม่แทนค่า `$...` เอง · shell บน Jenkins แทนค่าตัวแปรที่อยู่**นอก** heredoc เช่น `"IMAGE=$IMAGE APP_VERSION=$APP_VERSION ..."` แล้วส่งค่าที่ได้ไปเป็นตัวแปรนำหน้า `bash` บน devtools · ส่วน `<<'EOF'` มี quote ทำให้ shell บน Jenkins **ไม่**แทนค่าในสคริปต์ ข้อความส่งไปตรงตัว แล้ว bash บน devtools แทนค่า `$IMAGE`, `$(git rev-parse ...)`, `$(date ...)` เอง

**Stage 1 — Connect**

1. **บน Jenkins:** บล็อก `script` ใช้ `==~` (ต้องตรงรูปแบบทั้งข้อความ) ตรวจว่า `params.APP_VERSION` เป็น `X.Y.Z` ถ้าไม่ตรง `error` หยุด build ทันทีโดยยังไม่ SSH · ค่านี้ถูกส่งเข้า shell บน devtools การตรวจนี้จึงกันการแทรกคำสั่ง
2. **Jenkins → devtools:** `sh` รัน `ssh` บน Jenkins ด้วย private key จาก `sshagent` ส่งคำสั่งในเครื่องหมาย `"..."` ไปรัน**บน devtools**: `hostname`, `whoami`, `docker --version`, `git --version` เพื่อยืนยันว่าต่อได้ เป็น `root` และมี Docker/git พร้อม (ครั้งแรก SSH จะจำ host key ของ devtools ไว้ตรงนี้)

**Stage 2 — Clone** — Jenkins แค่ส่งสคริปต์ทาง SSH · ทุกบรรทัดในสคริปต์รัน**ข้างใน devtools** (stage นี้ไม่ต้องส่งตัวแปร จึงเป็น `bash -ex` เฉย ๆ):

- `rm -rf` ลบโฟลเดอร์ clone ของ build ก่อน ให้เริ่มจากซอร์สใหม่ทุกครั้ง
- `git clone --depth 1 --filter=blob:none --sparse` ดึงเฉพาะ commit ล่าสุดของ branch เริ่มต้นบน GitHub โดยยังไม่โหลดไฟล์ทั้ง repo · `git sparse-checkout set ...` เลือกให้มีเฉพาะโฟลเดอร์ `catfood-shop`
- `git log -1 --oneline` และ `ls` แสดง commit ที่ได้และรายชื่อไฟล์ใน console เป็นหลักฐานว่า clone อะไรมา
- หมายเหตุ: stage นี้ clone ใหม่เอง ไม่ได้ใช้ commit เดียวกับที่ Jenkins อ่าน `Jenkinsfile` ถ้ามี commit ใหม่เข้ามาระหว่างนั้น สองฝั่งอาจเป็นคนละ commit

**Stage 3 — Build** — shell บน Jenkins แทนค่า `IMAGE`, `APP_VERSION`, `BUILD_NUMBER` แล้วส่งไปเป็นตัวแปรของ bash บน devtools · สคริปต์ที่เหลือรัน**บน devtools**: `cd` เข้าโฟลเดอร์ `catfood-shop` ที่เพิ่ง clone → `git rev-parse --short HEAD` อ่าน commit → `docker build` ด้วย Docker ของ devtools เป็น image `catfood-shop:lab3-<เลข build>` โดยส่ง `--build-arg` สี่ตัว (เวอร์ชัน, เลข build, commit, เวลา UTC) ที่ `Dockerfile` เก็บเป็น environment ใน image ให้ `/api/health` อ่านตอนรัน → `docker image ls` แสดง image ที่ได้ · image นี้อยู่ใน devtools เท่านั้น ยังไม่ขึ้น Docker Hub

**Stage 4 — Test** — ส่งตัวแปรแบบเดียวกับ Build · ทุกคำสั่งรัน**บน devtools**:

1. `docker rm -f catfood-test || true` ลบ container ทดสอบที่อาจค้างจากรอบก่อน (`|| true` ไม่ให้ล้มถ้าไม่มี)
2. `docker run -d --name catfood-test "$IMAGE"` รัน image ใหม่แบบไม่เปิด port ออกนอก container · `trap ... EXIT` ลบ container นี้เสมอเมื่อสคริปต์จบ แม้ test ไม่ผ่าน
3. ลูป `for` ถาม `docker inspect` ทุก 1 วินาที สูงสุด 30 รอบ จนสถานะ `HEALTHCHECK` (ที่ประกาศใน `Dockerfile`) เป็น `healthy` · ถ้าครบ 30 รอบแล้วยังไม่ healthy ลูปจะจบเฉย ๆ ไม่ทำให้ stage ล้ม ตัวตัดสินคือขั้นถัดไป
4. `docker exec catfood-test wget ...` เรียก `/api/health` **จากข้างใน container** (เพราะไม่ได้เปิด port) → `tr -d '"'` ตัดเครื่องหมายคำพูดของ JSON → `grep -F` ต้องเจอ `version:<APP_VERSION>,build:<เลข build>,` ถ้าไม่เจอ `grep` คืนค่าผิดพลาด `bash -e` จึงหยุด และ stage Test ล้ม

**Stage 5 — Push** — `withCredentials` ดึง username/token จาก credential `dockerhub` มาเป็นตัวแปร `HUB_USER` และ `HUB_TOKEN` เฉพาะในบล็อก (Jenkins ซ่อนค่าเป็น `****` ใน console) แล้วห่อ `sshagent` ไว้ข้างใน:

1. `set +x` ปิดการพิมพ์คำสั่งของ `sh` ชั่วคราว → `echo "$HUB_TOKEN" |` ส่ง token ทาง stdin ผ่าน SSH เข้า `docker login --password-stdin` บน devtools token จึงไม่อยู่ใน command line หรือ console · `umask 077` ให้ไฟล์ login ใน `AUTH_DIR` อ่านได้เฉพาะ root · `set -x` เปิดการพิมพ์คำสั่งกลับ
2. `docker tag` ตั้งชื่อ image เป็น `<DOCKER_USER>/catfood-shop:lab3-<เลข build>` แล้ว `docker --config $AUTH_DIR push` ขึ้น Docker Hub ด้วยไฟล์ login นั้น
3. `docker image rm $IMAGE` ลบแค่ชื่อในเครื่อง `catfood-shop:lab3-<เลข build>` ชื่อ `$HUB_USER/...` ยังอยู่ให้ stage ถัดไป
4. stage นี้เป็นคำสั่งเดี่ยวจึงส่งตรงทีละบรรทัด ไม่ต้องใช้ `<<'EOF'` · `$AUTH_DIR`, `$HUB_USER`, `$IMAGE` ถูกแทนค่าโดย shell บน Jenkins ก่อนส่ง

**Stage 6 — Deploy** — ใช้ `withCredentials` + `sshagent` เหมือน Push แต่ใช้แค่ `HUB_USER` ตั้งชื่อ image · ส่ง `AUTH_DIR` และ `IMAGE=$HUB_USER/$IMAGE` (ชื่อเต็มบน Docker Hub) ไปให้สคริปต์บน devtools:

1. `docker image rm "$IMAGE"` ลบ image ในเครื่อง แล้ว `docker --config "$AUTH_DIR" pull` ดึงกลับมาจาก Docker Hub เพื่อพิสูจน์ว่า image บน Hub ใช้ได้จริง (console ขึ้น `Downloaded newer image`)
2. `docker rm -f catfood-web || true` ลบร้านเวอร์ชันเดิม → `docker run -d --name catfood-web --restart unless-stopped -p 3000:3000` รันตัวใหม่ที่ port `3000` ของ devtools ซึ่ง map ออกมาเป็น `localhost:3000` ของเครื่องเรา (ช่วงสั้น ๆ ระหว่างสลับ container ร้านจะปิดชั่วคราว)
3. รอ `healthy` แบบเดียวกับ Test แล้ว `curl -fsS http://localhost:3000/api/health` จากบน devtools ต้องได้เวอร์ชันและเลข build ตรงกับ build นี้

**`post`** — ทำงานหลังจบทุก stage:

- `success` ทำเมื่อ build ผ่านเท่านั้น: `echo` พิมพ์ URL ของร้านพร้อมเวอร์ชันและเลข build · string นี้ใช้ `"..."` Groovy จึงแทนค่า `${params.APP_VERSION}` และ `${env.BUILD_NUMBER}` บน Jenkins
- `always` ทำเสมอ ทั้งตอนสำเร็จและตอน build หยุดกลางทาง: SSH ไป `rm -rf $AUTH_DIR` ลบไฟล์ login Docker Hub บน devtools · `|| true` ไม่ให้ขั้นลบนี้ทำให้ผลของ build เปลี่ยน

หลัง stage **Deploy** เขียว (และ `post` ลบไฟล์ login แล้ว) ให้เปิด **[ร้าน Meow Mart บนเครื่อง lab ของเรา — http://localhost:3000](http://localhost:3000)** ในเบราว์เซอร์ของเครื่องที่รัน container `devtools` (ลิงก์ใช้ได้เฉพาะหลัง Deploy สำเร็จ) แล้วตรวจ chip บนแถบด้านบนว่าตรงกับ `APP_VERSION` และเลข build ที่เพิ่งรัน หน้าร้านจะมีลักษณะแบบนี้:

<a href="./images/lab3_localfix_shop_v100_build1_full.png"><img src="./images/lab3_localfix_shop_v100_build1_full.png" width="480" alt="หน้าร้าน Meow Mart ทั้งหน้า หลัง Build Now ครั้งแรกด้วย Jenkinsfile ฉบับแก้ chip แสดง v1.0.0 build #1"></a>

*ภาพที่ 10 ภาพหน้าจอจริงทั้งหน้า (2026-09-27) หลัง **Build Now ครั้งแรก** ด้วย `Jenkinsfile` ฉบับแก้ด้านบน · chip บนแถบด้านบนแสดง `v1.0.0 · build #1` · คลิกเพื่อดูขนาดเต็ม*

> 📌 **ทางเลือก ข (ฝึกเขียนเอง):** วางไฟล์ที่ root ของ repository สาธารณะของตัวเอง → `git add Jenkinsfile && git commit -m "Add LAB 3 Jenkinsfile" && git push` → job **Configure** ตั้ง Repository URL, Branch Specifier และ Script Path (`Jenkinsfile`) เป็นของตัวเอง · ทางเลือก ก ไม่ต้องทำอะไรเพิ่ม

## ขั้นที่ 5 — Build Now แล้วดู 6 stage ทำงาน

หน้า job `docker-build-push` กด **Build Now** ที่เมนูด้านซ้าย (ตำแหน่งตามภาพที่ 9ก) — build แรกใช้ค่า default `APP_VERSION=1.0.0` และ tag `lab3-1` (หลังรันครั้งแรกจึงมีเมนู **Build with Parameters**)

[![Console Output ช่วงเริ่ม build (ภาพเดิม)](./images/lab3_scm_08_console_obtained_crop.png)](./images/lab3_scm_08_console_obtained.png)

*ภาพที่ 11 🕰️ **ภาพเดิม** Console Output ช่วงแรก: `Obtained .../Jenkinsfile from git https://github.com/Tuchsanai/DevTools.git` แล้วเข้า stage `(Connect)` ทันที ไม่มี `Declarative: Checkout SCM` · ช่วงแรกนี้เหมือนกันในไฟล์ฉบับใหม่ ส่วน log ของแต่ละ stage จะต่างจากภาพ*

✅ สิ่งที่ต้องเห็นใน Console Output (ตรงกับ log ของการรันจริงด้วยไฟล์ฉบับแก้ 2026-09-27):

- **Connect:** ครั้งแรกที่ jenkins ยังไม่รู้จัก devtools จะมี `Warning: Permanently added 'devtools' (ED25519) to the list of known hosts.` (build ต่อไปไม่ขึ้นอีก) · บรรทัดที่ขึ้นต้นด้วย `[ssh-agent]` บอกว่าใช้ credential ของ `root` · ผล `devtools` / `root` / `Docker version ...` / `git version ...`
- **Clone:** บรรทัด `+ git clone ...` ตามด้วย commit ล่าสุด และรายชื่อไฟล์ของ `catfood-shop`
- **Test:** `+ grep -F version:1.0.0,build:1,` แล้วตามด้วย JSON `{status:ok,app:catfood-shop,version:1.0.0,build:1,...}`
- **Push:** `Login Succeeded` แล้ว `lab3-1: digest: sha256:... size: ...` · token แสดงเป็น `****`
- **Deploy:** `Status: Downloaded newer image for <DOCKER_USER>/catfood-shop:lab3-1` → health ตรง → `เปิดร้านได้ที่ http://localhost:3000 (v1.0.0 build #1)` → `Finished: SUCCESS`
- หน้า Stages ต้องเขียวครบ 6 stage: Connect → Clone → Build → Test → Push → Deploy ตามด้วย Post Actions

เมื่อ Deploy สำเร็จ เปิด [หน้าร้าน Meow Mart — http://localhost:3000](http://localhost:3000) chip บนแถบด้านบนต้องเป็น `v1.0.0 · build #1` (เหมือนภาพที่ 10)

> 🐞 **ทำไม `Jenkinsfile` ต้องเพิ่ม 2 บรรทัด** — ตอนทดสอบด้วยไฟล์เดิมจาก GitHub (`a8d0c0b`) กด **Build Now** ครั้งแรกแล้ว Connect, Clone, Build ผ่าน แต่ **Test ล้ม** (`+ grep -F version:,build:1,` → `ERROR: script returned exit code 1` → `Finished: FAILURE`) และ Push, Deploy ถูกข้าม · สาเหตุ: build แรก job ยังไม่มี parameter Jenkins จึงไม่ตั้งตัวแปร `$APP_VERSION` ให้ `sh` แม้ `params.APP_VERSION` ใน Groovy จะเป็น `1.0.0` ทำให้ devtools ได้ `APP_VERSION=` ค่าว่าง · **วิธีแก้:** เพิ่มใน `environment` สองบรรทัด
>
> ```groovy
>     // build แรก (Build Now) Jenkins ยังไม่รู้จัก parameter จึงไม่ส่ง $APP_VERSION ให้ sh: กำหนดจาก params เอง
>     APP_VERSION  = "${params.APP_VERSION}"
> ```
>
> ด้วยไฟล์ฉบับแก้ Build Now ครั้งแรกเขียวครบทันที เลข build จึงเป็นตามคู่มือ: **#1 = `1.0.0`**, **#2 = `1.1.0`** (ภาพที่ 11ก) · ถ้ายังใช้ไฟล์เดิมจาก GitHub build #1 จะล้ม ต้องกด **Build with Parameters** ด้วย `1.0.0` อีกรอบ เลข build ทั้งหมดจึงเลื่อนไปหนึ่ง (`1.0.0` = #2 และ `1.1.0` = #3)

[![หน้า Stages ของ job ที่อ่าน Jenkinsfile ฉบับแก้ build #1 และ #2 เขียวครบ 6 stage และ Post Actions](./images/lab3_localfix_stages_builds_1_2.png)](./images/lab3_localfix_stages_builds_1_2.png)

*ภาพที่ 11ก ภาพหน้าจอจริงหน้า **Stages** (2026-09-27) ของ job ทดสอบ `docker-build-push-localfix` ที่อ่าน `Jenkinsfile` ฉบับแก้จาก Git repo จำลองในเครื่อง · build **#1** (Build Now, `1.0.0`) และ **#2** (`1.1.0`) เขียวครบ Connect → Clone → Build → Test → Push → Deploy และ Post Actions · ของเราชื่อ job เป็น `docker-build-push`*

## ขั้นที่ 6 — ออกเวอร์ชันใหม่ `APP_VERSION=1.1.0`

job `docker-build-push` → **Build with Parameters** → `APP_VERSION` = `1.1.0` → **Build** (มี parameter เดียว)

✅ build #2 เขียวครบ 6 stage (แถว #2 ในภาพที่ 11ก) · Console ขึ้น `+ grep -F version:1.1.0,build:2,` และ `lab3-2: digest: sha256:...` · Deploy แทน `catfood-web` ของ build #1 · เปิด [หน้าร้าน Meow Mart — http://localhost:3000](http://localhost:3000) chip ต้องเป็น `v1.1.0 · build #2`

[![ส่วน Deployment info ของร้าน build #2 แสดง Version 1.1.0 และ Jenkins build #2](./images/lab3_shop_tour_05_deployment.png)](./images/lab3_shop_tour_05_deployment.png)

*ภาพที่ 12 ภาพหน้าจอจริง (2026-09-27) ส่วน **Deployment info** ท้ายหน้าร้านหลัง build #2: Version `1.1.0`, Jenkins build `#2`, Git commit `a8d0c0b`, Built at (UTC) และ Container ที่ตอบ · ท้ายหน้าเขียน `catfood-shop v1.1.0 · build #2 · commit a8d0c0b`*

หน้า **Tags** ของ repository `catfood-shop` บน Docker Hub ต้องมี `lab3-1` และ `lab3-2`:

[![หน้า Tags บน Docker Hub (ภาพเดิม)](./images/lab3_scm_dockerhub_tags_crop.png)](./images/lab3_scm_dockerhub_tags.png)

*ภาพที่ 13 🕰️ **ภาพเดิม** หน้า Tags บน Docker Hub ของรอบทดสอบเดิม (ชื่อ tag ในภาพเป็น `lab3-sibling-20260926r2-*`) · ของเราจะเป็น `lab3-1`, `lab3-2`*

## ขั้นที่ 7 — หน้าร้าน Meow Mart ที่ deploy แล้ว

ภาพทั้งหมดในข้อนี้เป็นภาพหน้าจอจริงจากเบราว์เซอร์ (2026-09-27) ของร้านที่ build #2 (`v1.1.0`) deploy ไว้ที่ `http://localhost:3000`

<a href="./images/lab3_localfix_shop_v110_build2_full.png"><img src="./images/lab3_localfix_shop_v110_build2_full.png" width="480" alt="หน้าร้าน Meow Mart ทั้งหน้า build #2 chip แสดง v1.1.0 build #2"></a>

*ภาพที่ 14 หน้าร้านทั้งหน้าหลัง build #2 · chip แสดง `v1.1.0 · build #2` · คลิกเพื่อดูขนาดเต็ม*

![ภาพเคลื่อนไหวพาชมร้าน 5 ภาพ: ส่วนบน, รายการสินค้า, กรองหมวดอาหารเปียก, ใส่ตะกร้า และ Deployment info](./images/lab3_shop_tour.gif)

*ภาพที่ 15 GIF วนซ้ำจากภาพหน้าจอจริง 5 ภาพ ภาพละ 2 วินาที (1440×1000): ส่วนบน → สินค้า → กรองหมวด → ใส่ตะกร้า → Deployment info · ภาพนิ่งแต่ละภาพ: [1](./images/lab3_shop_tour_01_hero.png) · [2](./images/lab3_shop_tour_02_products.png) · [3](./images/lab3_shop_tour_03_filter.png) · [4](./images/lab3_shop_tour_04_cart.png) · [5](./images/lab3_shop_tour_05_deployment.png)*

สิ่งที่หน้าร้านทำได้จริง (ตรวจในเบราว์เซอร์แล้ว):

- **แถบบนสุด** — ข้อความโปรโมชันและ chip `v<APP_VERSION> · build #<เลข build>` ที่อ่านจาก image ที่ deploy · แถบเมนู สินค้า / ทำไมต้องเรา / Deployment
- **สินค้า 6 รายการ** — การ์ดมีรูป ชื่อ รายละเอียด น้ำหนัก คะแนน ราคา และปุ่ม **+ ใส่ตะกร้า**
- **กรองหมวด** — ปุ่ม ทั้งหมด / อาหารเม็ด / อาหารเปียก / ขนมแมว · กด **อาหารเปียก** เหลือ 1 รายการ (ทูน่าเนื้อแน่น) · กด **ทั้งหมด** กลับมา 6 รายการ
- **ตะกร้า** — กดใส่ตะกร้าทูน่า ปุ่มตะกร้าเปลี่ยนจาก `0 ชิ้น · ฿0` เป็น `1 ชิ้น · ฿329`
- **Deployment info** — Version, Jenkins build, Git commit, Built at (UTC), Container และ Health API `/api/health` ที่ Pipeline ใช้ตรวจ ใช้ยืนยันว่า Pipeline deploy เวอร์ชันที่ต้องการแล้ว
