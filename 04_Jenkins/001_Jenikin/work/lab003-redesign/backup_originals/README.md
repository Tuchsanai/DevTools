# LAB 3 — Jenkins สั่ง Build → Test → Push → Pull → Deploy ร้านอาหารแมวผ่าน SSH

> ⏱️ ประมาณ 60 นาที · 🧪 15 การทดลอง · 🎯 จบเมื่อกด **Build** ใน Jenkins แล้วเปิด `http://localhost:3000` เห็นร้าน **Meow Mart** เวอร์ชันที่ Pipeline เพิ่งสร้าง และผ่านรายการ **✅ ตรวจปิดแล็บด้วยตา** ครบทุกข้อ

แล็บนี้ให้นักศึกษา **เริ่มงานทุกอย่างจาก Jenkins Pipeline** ไม่พิมพ์ `docker build` เองแม้แต่ครั้งเดียว Jenkins เป็น image มาตรฐาน `jenkins/jenkins:lts-jdk21` ที่ **ไม่มี Docker อยู่ข้างใน** จึงส่งคำสั่งผ่าน **SSH** ไปให้ container `devtools` ซึ่งมี Docker และซอร์สโค้ดร้านอาหารแมวอยู่แล้วเป็นผู้ลงมือทำ

> **Jenkins เป็นผู้สั่งงาน ส่วน devtools เป็นผู้ประมวลผลคำสั่ง Docker** — ทุก stage ตั้งแต่ build, test, push ไปจนถึง pull และ deploy เริ่มจากปุ่มบน Jenkins

ผลลัพธ์ทุกค่าในเอกสารนี้ (เลข build, เวลา, digest, container ID) มาจากการทดลองจริงชุดเดียวกันตั้งแต่ต้นจนจบ นักศึกษาจะเห็นค่า digest, hostname และเวลาที่ต่างออกไปในเครื่องของตนเอง แต่ **ความสัมพันธ์ระหว่างค่าต้องเหมือนกัน** เช่น digest ที่ push ต้องเท่ากับ digest ที่ pull และเท่ากับที่ Docker Hub แสดง

![หน้าแรกของร้าน Meow Mart ที่ Pipeline deploy](./images/lab3_f1_web_hero_b1.jpg)

*ภาพที่ 1 สิ่งที่จะได้เมื่อจบแล็บ (ภาพจริงแบบเต็มจอ 1920×1080): chip สีเขียว `v1.0.0 · build #1` บนแถบด้านบนอ่านมาจาก image ที่ Jenkins สั่งสร้าง*

---

## 1. System Architecture — ใครอยู่ที่ไหน และคุยกันทางใด

![System architecture ของ LAB 3](./images/lab3_arch_system.png)

*ภาพที่ 2 สถาปัตยกรรมจริงของแล็บ ทุกชื่อ IP และ port ในภาพตรวจจากเครื่องที่ใช้ทดลอง (คำสั่งตรวจอยู่ในการทดลองที่ 3–4) เส้นสีน้ำเงินคือเส้นทาง **คำสั่ง** (SSH) เส้นสีส้มคือเส้นทาง **image** (push/pull) ซึ่งแยกจากกันโดยสิ้นเชิง*

| ส่วนประกอบ | อยู่ที่ไหน | หน้าที่ในแล็บนี้ |
|---|---|---|
| **ผู้เรียน** | เครื่องของตนเอง (Docker host เช่น Docker Desktop) | เปิด browser ไปที่ `localhost:8080` (Jenkins) และ `localhost:3000` (ร้าน) · ใช้ shell ของ devtools เตรียม key และอ่านไฟล์ |
| **devtools** | container บนเครื่องผู้เรียน (`--privileged`, สร้างใน LAB 1) | มี `sshd` (port 22), **Docker daemon ของตัวเอง** (Docker-in-Docker), ซอร์สโค้ดร้าน และ build cache |
| **Docker daemon ของ devtools** | ภายใน devtools | สร้างและรัน container ทุกตัวของแล็บ ได้แก่ `jenkins`, `catfood-test-N`, `catfood-web` |
| **jenkins** | container บน Docker ของ devtools · network `cicd-net` (172.19.0.2) | อ่าน Jenkinsfile, เก็บ Credentials, เปิด SSH ไปสั่ง devtools — **ไม่มี Docker CLI และไม่ได้ mount docker.sock** |
| **ซอร์สโค้ดร้าน** | `~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop` **บน devtools** | เป็น build context ของ `docker build` · Jenkins ไม่มีสำเนาซอร์สเลย |
| **Docker Hub** | อินเทอร์เน็ต `docker.io/<DOCKER_USER>/catfood-shop` | เก็บ image พร้อม tag `1`, `2`, `latest` · devtools push ขึ้นและ pull กลับลงมา |
| **catfood-web** | container บน Docker ของ devtools · default `bridge` (172.18.0.2) · `-p 3000:3000` | ร้าน Meow Mart ที่รันจาก image ที่ **pull กลับมาจาก Docker Hub** |

**เส้นทางสองเส้นที่ต้องแยกให้ออก**

1. **เส้นทางคำสั่ง (SSH)** — `jenkins` → `root@devtools` port 22 → `bash -s` บน devtools → `docker ...` → Docker daemon ของ devtools สิ่งที่วิ่งบนเส้นนี้มีแค่ข้อความสคริปต์และ log ที่พิมพ์กลับมา
2. **เส้นทาง image (HTTPS)** — Docker daemon ของ devtools ⇄ Docker Hub เมื่อ `docker push` และ `docker pull` layer ขนาดร้อยกว่า MB เดินทางบนเส้นนี้ **Jenkins ไม่เคยแตะข้อมูล image เลย**

> 📝 port ที่ผู้เรียนเปิดใน browser ผ่านสองชั้น: `localhost:8080` → `-p 8080:8080` ของ devtools → `-p 8080:8080` ของ container `jenkins` และ `localhost:3000` → devtools → `catfood-web` (port ทั้งสองเปิดไว้แล้วตั้งแต่ LAB 1)

### คำศัพท์ที่ใช้ตลอดแล็บ

| คำศัพท์ | ความหมาย |
|---|---|
| **Image** | แพ็กเกจอ่านอย่างเดียวที่มีระบบไฟล์ของแอปและคำสั่งเริ่มต้น ประกอบจาก **layer** ซ้อนกัน |
| **Container** | process ที่รันจาก image หนึ่งตัว |
| **Registry / Repository / Tag** | ที่เก็บ image (Docker Hub) / ชื่อชุด image (`<DOCKER_USER>/catfood-shop`) / ป้ายเวอร์ชันที่ย้ายได้ (`1`, `2`, `latest`) |
| **Digest** | ลายนิ้วมือ `sha256:...` ที่คำนวณจากเนื้อหา image — เนื้อหาเดียวกันได้ digest เดียวกันเสมอ |
| **Credential** | ความลับที่ Jenkins เก็บไว้แทนเรา แล้วให้ Pipeline อ้างถึงด้วย ID |

---

## 🎯 Learning Objectives — ผลลัพธ์การเรียนรู้

เมื่อจบแล็บนี้ นักศึกษาจะสามารถ

1. วาดและอธิบายสถาปัตยกรรมที่ Jenkins สั่งงาน Docker ของเครื่องอื่นผ่าน SSH โดยแยกเส้นทางคำสั่งออกจากเส้นทาง image ได้
2. ตรวจได้ด้วยตนเองว่า Jenkins ไม่มี Docker แต่มี SSH client และ devtools พร้อมรับงาน
3. เตรียม SSH key, เก็บ private key และ Docker Hub token ใน Jenkins Credentials และทดสอบการเชื่อมต่อจาก Jenkins ก่อน build
4. อ่าน Jenkinsfile แล้วบอกได้ว่าโค้ดส่วนใดทำงานบน Jenkins คำสั่งใดทำงานบน devtools และตัวแปรถูกแทนค่าที่ฝั่งใด
5. อ่านหลักฐานของทุก stage จากหน้า Stages / Console, Docker Hub และหน้าร้าน แล้วยืนยันว่า version, เลข build และ digest สัมพันธ์กัน
6. ออกเวอร์ชันใหม่ด้วย **Build with Parameters** และอธิบายผลของ layer cache และการย้าย tag ได้

## 🗺️ แผนที่การทดลอง

| ส่วน | การทดลอง | สิ่งที่ทำ | ผลจริงที่ได้ |
|---|---|---|---|
| 2. รู้จักสภาพแวดล้อม | 1–3 | เปิด Jenkins · ส่องข้างใน Jenkins · ส่อง devtools | `docker: not found` (exit 127) แต่มี `OpenSSH_10.0p2` · devtools มี Docker 29.8.1 และไฟล์ร้านครบ |
| 3. เครือข่าย + Credentials | 4–7 | `--add-host` → สร้าง key → เก็บ credential 2 ตัว → job ทดสอบ SSH | `devtools` = `172.18.0.1` · `Permission denied` ก่อนมี key · job ทดสอบพิมพ์ hostname ของ devtools |
| 6. Pipeline ทีละ stage | 8–14 | Build Now → Connect → Build → Test → Push → Pull → Deploy | build #1 เขียวทั้ง 6 stage ใน 1 นาที 6 วินาที · digest `046f4bd8af08…` ตรงกันทุกจุด · ร้านขึ้น `v1.0.0 · build #1` |
| 7. ออกเวอร์ชันใหม่ | 15 | Build with Parameters `1.1.0` | build #2 ใน 24 วินาที · `CACHED` 5 ขั้น · push ใหม่ 0 layer · digest `bd8c67e1adc8…` |

## 📂 ไฟล์ในโฟลเดอร์นี้

| ไฟล์ | หน้าที่ |
|---|---|
| `Jenkinsfile` | Pipeline 6 stage: Connect → Build → Test → Push → Pull → Deploy (ทุก stage ส่งคำสั่งผ่าน SSH ไปที่ devtools) |
| `catfood-shop/` | ซอร์สโค้ดร้าน Meow Mart (Next.js 16 + React 19) = build context |
| `catfood-shop/Dockerfile` | Dockerfile แบบ single-stage + `HEALTHCHECK` |

## สภาพตั้งต้น

ต้องจบ LAB 2 แล้ว: container `devtools` ทำงาน (สร้างตาม LAB 1 ส่วนที่ 0 ซึ่งเปิด `-p 2222:22 -p 8080:8080 -p 3000:3000` ไว้แล้ว) มี network `cicd-net`, container `jenkins` ที่สร้างจาก `jenkins/jenkins:lts-jdk21`, volume `jenkins_home` และ login ด้วย `admin / admin2569` ได้

> **Prerequisite Docker Hub:** สมัครบัญชี ยืนยันอีเมล สร้าง **Access Token สิทธิ์ Read & Write** และแนะนำให้สร้าง repository `catfood-shop` แบบ **Public** ไว้ก่อน (ถ้าไม่สร้าง Docker Hub จะสร้างให้ตอน push ตามค่า Default privacy ของบัญชี)

คำสั่งทุกคำสั่งที่เขียนว่า “**shell ของ devtools**” ให้รันใน terminal ที่เข้า devtools แล้ว (`ssh -p 2222 root@localhost` หรือ terminal ของ VS Code ที่ attach devtools)

### รูปแบบของทุกการทดลอง

ทุกการทดลองเขียนในรูปแบบเดียวกัน

1. 🎯 **เป้าหมาย** — ต้องการเรียนรู้อะไร
2. 🛠️ **ขั้นตอน** — ทำที่หน้าจอหรือเครื่องใด
3. 📝 **คำอธิบาย** — คำสั่งหรือโค้ดทำงานอย่างไร
4. ✅ **ผลที่ควรเห็น** — ตรวจจากจุดใด (ค่าจริงจากการทดลอง)
5. 💡 **ข้อสรุป** — ผลนั้นพิสูจน์อะไร

---

## 2. รู้จักสภาพแวดล้อม Jenkins

### การทดลองที่ 1 — เปิดหน้าเว็บ Jenkins

🎯 **เป้าหมาย:** ยืนยันว่า Jenkins จาก LAB 2 ยังทำงาน และรู้ว่าหน้าจอใดคือจุดเริ่มงานของแล็บนี้

🛠️ **ขั้นตอน (browser):** เปิด `http://localhost:8080` แล้ว login ด้วย `admin / admin2569`

📝 **คำอธิบาย:** request จาก browser ผ่าน port `8080` ของ devtools เข้า container `jenkins` หน้า Dashboard คือจุดที่จะสร้าง job และกด Build ทุกครั้งในแล็บนี้

✅ **ผลที่ควรเห็น:**

![Jenkins Dashboard](./images/lab3_a1_dashboard.png)

*ภาพที่ 3 Dashboard ของ Jenkins 2.568.3 มี job `first-freestyle` (LAB 1) และ `first-pipeline` (LAB 2) สีเขียว*

💡 **ข้อสรุป:** Jenkins พร้อมใช้งาน และข้อมูลจาก LAB ก่อนหน้ายังอยู่ใน volume `jenkins_home`

### การทดลองที่ 2 — ข้างใน Jenkins ไม่มี Docker แต่มี SSH

🎯 **เป้าหมาย:** พิสูจน์ด้วยตนเองว่า container `jenkins` สั่ง `docker` ไม่ได้ แต่มีเครื่องมือสำหรับสั่งงานเครื่องอื่นอยู่แล้ว

🛠️ **ขั้นตอน (shell ของ devtools):**

```bash
docker exec jenkins sh -c 'docker version'; printf 'exit=%s\n' "$?"
docker exec jenkins sh -c 'command -v ssh; ssh -V'
docker exec jenkins sh -c 'id; hostname'
```

📝 **คำอธิบาย:** `docker exec jenkins ...` รันคำสั่ง **ภายใน** container `jenkins` คำสั่งแรกลองเรียก Docker CLI คำสั่งที่สองหา SSH client คำสั่งที่สามดูว่า Jenkins รันเป็นผู้ใช้ใด

✅ **ผลที่ควรเห็น (ผลจริง):**

```text
sh: 1: docker: not found
exit=127
/usr/bin/ssh
OpenSSH_10.0p2 Debian-7+deb13u4, OpenSSL 3.5.7 9 Jun 2026
uid=1000(jenkins) gid=1000(jenkins) groups=1000(jenkins)
fe6b96ef4427
```

💡 **ข้อสรุป:** exit code `127` แปลว่าหาโปรแกรม `docker` ไม่พบ image มาตรฐานของ Jenkins **ตั้งใจไม่ใส่ Docker** และเราจะไม่ติดตั้งเพิ่ม แต่มี OpenSSH client มาให้แล้ว Jenkins จึงต้อง **ส่งคำสั่งไปให้เครื่องที่มี Docker ทำ** เหตุผลที่ออกแบบเช่นนี้

1. **Jenkins มีหน้าที่สั่ง ไม่ใช่ทำ** — ควบคุมลำดับขั้น เก็บ log และความลับ ส่วนงานหนักให้เครื่องที่มีเครื่องมือครบทำ เหมือน build agent ในระบบจริง
2. **image มาตรฐาน ดูแลง่าย** — ไม่ต้อง build Jenkins image เอง อัปเกรดด้วยการเปลี่ยน tag
3. **ปลอดภัยกว่าการ mount `docker.sock`** — ถ้า mount socket ผู้ที่ควบคุม Jenkins ได้ก็ควบคุม Docker ได้ทั้งหมดทันที ในแล็บนี้สิทธิ์ถูกจำกัดไว้ที่ SSH key หนึ่งชุดซึ่งเพิกถอนได้

### การทดลองที่ 3 — devtools มี Docker และไฟล์ร้านพร้อมใช้งาน

🎯 **เป้าหมาย:** ยืนยันว่าเครื่องปลายทางที่ Jenkins จะสั่งงานมีครบทั้ง Docker, sshd และซอร์สโค้ด และยังไม่มี image ร้านมาก่อน

🛠️ **ขั้นตอน (shell ของ devtools):**

```bash
hostname
docker version --format 'Client {{.Client.Version}} / Server {{.Server.Version}}'
(echo > /dev/tcp/127.0.0.1/22) 2>/dev/null && echo "sshd: port 22 open"
ls ~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop
docker image ls
```

📝 **คำอธิบาย:** `hostname` ของ devtools คือ container ID ของมัน ค่านี้จะใช้พิสูจน์ในการทดลองที่ 7 และ 9 ว่า SSH ไปถึงเครื่องที่ถูกต้อง บรรทัดที่สามเปิด TCP ไปที่ port 22 ของตัวเองเพื่อตรวจว่า sshd ฟังอยู่

✅ **ผลที่ควรเห็น (ผลจริง — hostname ของแต่ละเครื่องต่างกัน):**

```text
1b12b5e8724f
Client 29.8.1 / Server 29.8.1
sshd: port 22 open
Dockerfile  app  data  next.config.mjs  package-lock.json  package.json  public
IMAGE                       ID             DISK USAGE   CONTENT SIZE   EXTRA
jenkins/jenkins:lts-jdk21   c1e4c349365f        814MB          293MB   U
```

💡 **ข้อสรุป:** devtools มี Docker daemon ของตัวเอง, sshd พร้อมรับการเชื่อมต่อ และมีซอร์สโค้ดร้านพร้อม `Dockerfile` ส่วน `docker image ls` มีเพียง image ของ Jenkins แปลว่า **ยังไม่มีใคร build ร้านมาก่อน** — build ครั้งแรกจะเกิดจาก Jenkins ในการทดลองที่ 8

---

## 3. เครือข่ายและ Credentials

### Jenkins หา devtools เจอได้อย่างไร

| คำถาม | คำตอบ (ค่าจริงในแล็บ) |
|---|---|
| Jenkins เรียกปลายทางด้วยชื่ออะไร | `devtools` — เขียนไว้ใน Jenkinsfile เป็น `root@devtools` |
| ชื่อนี้มาจากไหน | ตอนสร้าง container `jenkins` ใส่ `--add-host devtools:host-gateway` Docker จะเขียน `172.18.0.1  devtools` ลงใน `/etc/hosts` ของ Jenkins |
| `172.18.0.1` คือใคร | gateway ของ default `bridge` บน Docker ของ devtools = **network interface ของ devtools เอง** (`host-gateway` หมายถึง “เครื่องที่เป็นเจ้าของ Docker daemon นี้”) |
| Jenkins อยู่ network ไหน | `cicd-net` (172.19.0.0/16) IP `172.19.0.2` ส่ง packet ไป `172.18.0.1` ผ่าน gateway `172.19.0.1` ซึ่งก็เป็น interface ของ devtools เช่นกัน |
| ใช้ port อะไร | **22** (sshd ของ devtools) |
| ยืนยันตัวตนอย่างไร | **SSH key** ไม่ใช้รหัสผ่าน: private key อยู่ใน Jenkins Credentials, public key อยู่ใน `~/.ssh/authorized_keys` ของ devtools |

> Pipeline ต้องเชื่อมต่อได้ **โดยไม่มีใครพิมพ์รหัสผ่านระหว่างทำงาน** จึงต้องตั้งค่า SSH credential ให้เสร็จก่อนเริ่ม build

### การทดลองที่ 4 — สร้าง Jenkins ใหม่ให้รู้จักชื่อ `devtools`

🎯 **เป้าหมาย:** ให้ Jenkins เรียก devtools ด้วยชื่อได้ โดยยังใช้ image และ volume เดิม แล้วพิสูจน์ว่าเส้นทางเครือข่ายถึง sshd จริง

🛠️ **ขั้นตอน (shell ของ devtools):**

```bash
docker rm -f jenkins
docker run -d --name jenkins --network cicd-net --restart unless-stopped \
  -p 8080:8080 --add-host devtools:host-gateway \
  -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts-jdk21
docker exec jenkins getent hosts devtools
docker exec jenkins ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new root@devtools true; printf 'exit=%s\n' "$?"
docker inspect -f '{{.Config.Image}}  {{.HostConfig.ExtraHosts}}' jenkins
docker network inspect bridge   -f '{{range .IPAM.Config}}{{.Subnet}} gw {{.Gateway}}{{end}}'
docker network inspect cicd-net -f '{{range .IPAM.Config}}{{.Subnet}} gw {{.Gateway}}{{end}}'
docker inspect -f '{{range $k,$v := .NetworkSettings.Networks}}{{$k}}={{$v.IPAddress}}{{end}}' jenkins
```

📝 **คำอธิบาย:** การลบ container ไม่ทำให้ job หรือผู้ใช้หาย เพราะข้อมูลทั้งหมดอยู่ใน volume `jenkins_home` (LAB 1) `BatchMode=yes` สั่งไม่ให้ SSH ถามรหัสผ่าน ส่วน `StrictHostKeyChecking=accept-new` ยอมรับ host key ของ devtools ในครั้งแรกแล้วจดไว้ ครั้งต่อไปถ้า host key เปลี่ยน SSH จะปฏิเสธ (ป้องกันการปลอมเครื่อง)

✅ **ผลที่ควรเห็น (ผลจริง — IP อาจต่างกันในแต่ละเครื่อง):**

```text
172.18.0.1      devtools
Warning: Permanently added 'devtools' (ED25519) to the list of known hosts.
root@devtools: Permission denied (publickey,password).
exit=255
jenkins/jenkins:lts-jdk21  [devtools:host-gateway]
172.18.0.0/16 gw 172.18.0.1
172.19.0.0/16 gw 172.19.0.1
cicd-net=172.19.0.2
```

💡 **ข้อสรุป:** ชื่อ `devtools` แปลงเป็น `172.18.0.1` ซึ่งเป็น gateway ของ bridge บน devtools บรรทัด `Permanently added 'devtools' (ED25519)` แสดงว่าคุยกับ sshd ของ devtools ได้จริง ส่วน `Permission denied (publickey,password)` เป็นผลที่ **ถูกต้อง** — เส้นทางเครือข่ายใช้ได้แล้ว ขาดเพียง key Jenkins ยังเป็น image มาตรฐานตัวเดิม เพิ่มเพียง host entry หนึ่งรายการ (รอ Jenkins เริ่มระบบสักครู่แล้ว login ใหม่ job เดิมยังอยู่ครบ)

### การทดลองที่ 5 — สร้าง SSH key ให้ Jenkins ใช้เข้า devtools

🎯 **เป้าหมาย:** เตรียม key คู่หนึ่ง โดยให้ devtools รู้จัก public key

🛠️ **ขั้นตอน (shell ของ devtools):**

```bash
ssh-keygen -t ed25519 -N '' -C jenkins-to-devtools -f ~/.ssh/jenkins_devtools
cat ~/.ssh/jenkins_devtools.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
ls -l ~/.ssh
```

📝 **คำอธิบาย:** `ssh-keygen` สร้าง key เป็นคู่ `-N ''` คือไม่ตั้ง passphrase เพื่อให้ Jenkins ใช้ได้โดยไม่มีคนพิมพ์ การต่อท้าย `.pub` ลงใน `authorized_keys` ทำให้ sshd ยอมให้ผู้ที่ถือ private key คู่กันเข้าเป็น `root` ได้

✅ **ผลที่ควรเห็น (ผลจริง — fingerprint ต่างกันทุกเครื่อง เช่น `SHA256:NXRWiNiB… jenkins-to-devtools`):**

```text
-rw------- 1 root root 101 ... authorized_keys
-rw------- 1 root root 411 ... jenkins_devtools
-rw-r--r-- 1 root root 101 ... jenkins_devtools.pub
```

💡 **ข้อสรุป:** `jenkins_devtools` คือ **private key** (411 ไบต์ อ่านได้เฉพาะเจ้าของ) จะไปอยู่ใน Jenkins Credentials เท่านั้น `jenkins_devtools.pub` คือ **public key** (101 ไบต์) เปิดเผยได้ ขนาดของ `authorized_keys` เท่ากับ `.pub` พอดี แปลว่ามี public key อยู่หนึ่งชุด

> ⚠️ **Safety:** การ login เป็น `root` ด้วย key ชุดเดียวเหมาะกับแล็บที่ลบทิ้งได้เท่านั้น ใครได้ private key นี้ไปก็สั่ง Docker ของ devtools ได้ทุกอย่าง ระบบ production ควรใช้ผู้ใช้หรือ build agent เฉพาะงาน จำกัดสิทธิ์ตามหลัก least privilege และแยก key ต่อเครื่อง

### การทดลองที่ 6 — เก็บ SSH key และ Docker Hub token ใน Jenkins Credentials

🎯 **เป้าหมาย:** ให้ Pipeline ใช้ความลับสองชิ้นได้โดยไม่เขียนความลับลงในโค้ด และแยก credential ของ SSH ออกจาก Docker Hub

🛠️ **ขั้นตอน (browser):**

1. **Manage Jenkins → Credentials** (หมวด Security)

![Manage Jenkins → Credentials](./images/lab3_b3a_manage_jenkins.png)

*ภาพที่ 4 เมนู Credentials ในหมวด Security (กรอบแดง)*

2. เลือก **System → Global credentials (unrestricted)** จะเห็นหน้าว่าง แล้วกด **Add Credentials**

![Global credentials ยังว่าง](./images/lab3_b3a2_credentials_empty.png)

*ภาพที่ 5 ก่อนเริ่มยังไม่มี credential ใด*

**(ก) SSH key สำหรับเข้า devtools**

3. เลือกชนิด **SSH Username with private key** → **Next**

![เลือกชนิด SSH Username with private key](./images/lab3_b3b_credential_kind_ssh.png)

*ภาพที่ 6 Jenkins รุ่นนี้ให้เลือกชนิด credential ใน dialog ก่อนกรอกข้อมูล*

4. แสดง private key ใน shell ของ devtools แล้วคัดลอก **ทั้งไฟล์** รวมบรรทัด `-----BEGIN OPENSSH PRIVATE KEY-----` และ `-----END OPENSSH PRIVATE KEY-----`

```bash
cat ~/.ssh/jenkins_devtools
```

5. กรอก **ID** = `devtools-ssh`, **Description** = `SSH key: Jenkins to devtools`, **Username** = `root` เลือก **Private Key → Enter directly → Add** แล้ววางเนื้อหาที่คัดลอกมา ปล่อย **Passphrase** ว่าง → **Create**

![แบบฟอร์ม SSH key](./images/lab3_b3c_ssh_credential_form.png)

*ภาพที่ 7 ช่อง Key ในภาพใส่ข้อความตัวอย่างไว้แทน key จริง ให้วางเนื้อหาไฟล์ `~/.ssh/jenkins_devtools` ของตนเองทั้งไฟล์*

![ส่วนล่างของแบบฟอร์ม SSH key](./images/lab3_b3c2_ssh_credential_form_bottom.png)

*ภาพที่ 8 ส่วนล่างของแบบฟอร์ม: Passphrase ว่าง (key สร้างด้วย `-N ''`) แล้วกด Create*

**(ข) Docker Hub token**

6. **Add Credentials** อีกครั้ง เลือก **Username with password** → **Next** กรอก Username = `<DOCKER_USER>`, Password = `<DOCKER_TOKEN>`, ID = `dockerhub`, Description = `Docker Hub access token` → **Create** (แทน placeholder ด้วยค่าจริงของตนเอง)

![แบบฟอร์ม Docker Hub](./images/lab3_b3d_dockerhub_credential_form.png)

*ภาพที่ 9 ช่อง Password ถูกปิดบังเสมอ ID `dockerhub` คือชื่อที่ Jenkinsfile อ้างถึง*

📝 **คำอธิบาย:** credential สองตัวนี้ **ใช้คนละที่และคนละเวลา** — `devtools-ssh` ใช้ทุก stage เพื่อเปิด SSH ส่วน `dockerhub` ใช้เฉพาะ stage ที่ต้องรู้ชื่อบัญชีหรือ login Docker Hub การแยกกันทำให้เปลี่ยน token ได้โดยไม่แตะ key และเพิกถอนสิทธิ์ทีละอย่างได้

✅ **ผลที่ควรเห็น:** หน้า Global credentials มีสองรายการ

![รายการ credential สองตัว](./images/lab3_b3e_credentials_list.png)

*ภาพที่ 10 `devtools-ssh` และ `dockerhub` แสดงเพียง ID และคำอธิบาย*

💡 **ข้อสรุป:** หน้านี้ **ไม่แสดง private key หรือ token เลย** แม้ผู้ดูแลก็อ่านความลับกลับออกมาจากหน้าเว็บไม่ได้ Pipeline เท่านั้นที่ขอใช้ได้ผ่าน ID

> ⚠️ private key และ token วางได้ที่ Jenkins Credentials เท่านั้น ห้ามวางในแชต เอกสาร หรือ commit ลง Git

### การทดลองที่ 7 — ทดสอบ SSH จาก Jenkins ก่อนเริ่ม build

🎯 **เป้าหมาย:** ยืนยันว่า Jenkins ใช้ credential `devtools-ssh` เข้า devtools ได้จริง และไปถึง **เครื่องที่ถูกต้อง** ก่อนจะสั่งงานหนัก

🛠️ **ขั้นตอน (browser):**

1. Dashboard → **New Item** → ชื่อ `devtools-ssh-test` → เลือก **Pipeline** → **OK**

![New Item devtools-ssh-test](./images/lab3_b4a_new_item_ssh_test.png)

*ภาพที่ 11 job ทดสอบชนิด Pipeline*

2. ในส่วน **Pipeline** คง Definition เป็น **Pipeline script** วางสคริปต์นี้ → **Save**

```groovy
pipeline {
  agent any
  stages {
    stage('SSH to devtools') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY')]) {
          sh 'ssh -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new root@devtools "hostname; whoami; docker --version; ls ~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop"'
        }
      }
    }
  }
}
```

![สคริปต์ทดสอบ SSH](./images/lab3_b4b_ssh_test_script.png)

*ภาพที่ 12 สคริปต์ทดสอบใน editor ของ Jenkins*

3. กด **Build Now** แล้วเปิด **Console Output** ของ build #1

📝 **คำอธิบาย:** `withCredentials([sshUserPrivateKey(...)])` ให้ Jenkins เขียน private key ลงไฟล์ชั่วคราว แล้วเก็บ path ไว้ในตัวแปร `$SSH_KEY` เฉพาะภายในบล็อก เมื่อจบบล็อกไฟล์ถูกลบ `ssh -i "$SSH_KEY"` ใช้ไฟล์นั้นยืนยันตัวตน ข้อความในเครื่องหมายคำพูดหลัง `root@devtools` คือคำสั่งที่ **ไปรันบน devtools**

✅ **ผลที่ควรเห็น (ผลจริง):**

![Console ของ devtools-ssh-test](./images/lab3_b4c_ssh_test_console.png)

*ภาพที่ 13 `ssh -i ****` (path ของ key ถูก mask) ตามด้วย `1b12b5e8724f`, `root`, `Docker version 29.8.1, build 4a63305` และรายการไฟล์ของร้าน → `Finished: SUCCESS`*

💡 **ข้อสรุป:** `1b12b5e8724f` คือ hostname เดียวกับที่ได้ใน **การทดลองที่ 3** ไม่ใช่ hostname ของ Jenkins (`fe6b96ef4427` ในการทดลองที่ 2) และ Jenkins สั่ง `docker --version` ได้ทั้งที่ตัวเองไม่มี Docker — คำสั่งไปรันบน devtools จริง เส้นทางคำสั่งพร้อมแล้ว

> 💡 **ทำไมไม่ใช้ `environment { SSH_KEY = credentials('devtools-ssh') }`?** ผู้เขียนลองแล้ว: สำหรับ credential ชนิด SSH key รูปแบบนี้จะผูกตัวแปร `SSH_KEY_USR` (= `root`) มาด้วยและ **mask คำว่า `root` ทุกที่ใน console** ผลคือ `root@devtools` กลายเป็น `****@devtools` และ `whoami` พิมพ์ `****` ตรวจด้วยตาไม่ได้ว่าเข้าเครื่องถูกผู้ใช้หรือไม่ จึงใช้ `withCredentials([sshUserPrivateKey(... keyFileVariable: 'SSH_KEY')])` ซึ่งผูกเฉพาะไฟล์ key แทน

---

## 4. ซอร์สโค้ดร้านและ Dockerfile

### โครงสร้างไฟล์และ build context

build context คือโฟลเดอร์ที่ `docker build` ส่งให้ Docker daemon ใช้ ในแล็บนี้คือ `catfood-shop/` **บน devtools** (Jenkinsfile ตั้งไว้เป็น `APP_DIR`) และ `Dockerfile` อยู่ที่รากของโฟลเดอร์นั้น

```text
~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop/   ← build context
├── Dockerfile               # สูตรสร้าง image (single-stage + HEALTHCHECK)
├── .dockerignore            # ไม่ส่ง node_modules, .next, .git, *.md เข้า build context
├── package.json / package-lock.json
├── app/page.js              # หน้าร้าน (อ่าน build info ทุก request)
├── app/components/Shop.js   # ตัวกรองหมวด + ตะกร้า (ทำงานฝั่ง browser)
├── app/api/health/route.js  # /api/health ที่ HEALTHCHECK และ stage Deploy เรียก
├── data/products.js         # สินค้า 6 รายการ
├── data/buildInfo.js        # อ่าน APP_VERSION, BUILD_NUMBER, GIT_COMMIT, BUILD_TIME
└── public/images/           # ภาพสินค้า
```

> 📝 แล็บนี้ **ไม่ให้ build ด้วยมือบน devtools** image ของร้านจะถูกสร้างครั้งแรกโดย Jenkins ในการทดลองที่ 8 นักศึกษาอ่าน Dockerfile ให้เข้าใจก่อน แล้วดูผลของแต่ละบรรทัดจาก log ของ stage Build

### Dockerfile ทีละขั้น

```dockerfile
FROM node:22-alpine
WORKDIR /app
ENV NEXT_TELEMETRY_DISABLED=1

COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund && npm cache clean --force      # ① ติดตั้ง dependencies

COPY . .
RUN npm run build && rm -rf .next/cache                          # ② build เว็บไซต์

ENV NODE_ENV=production \
    PORT=3000

ARG APP_VERSION=dev
ARG BUILD_NUMBER=local
ARG GIT_COMMIT=none
ARG BUILD_TIME=unknown
ENV APP_VERSION=$APP_VERSION \
    BUILD_NUMBER=$BUILD_NUMBER \
    GIT_COMMIT=$GIT_COMMIT \
    BUILD_TIME=$BUILD_TIME                                       # ข้อมูล build จาก Jenkins

EXPOSE 3000
HEALTHCHECK --interval=10s --timeout=3s --start-period=30s --start-interval=1s --retries=3 \
  CMD wget -qO- http://127.0.0.1:3000/api/health || exit 1      # ④ ตรวจสุขภาพ
CMD ["npm", "start"]                                             # ③ เริ่มแอป
```

| ขั้น | บรรทัด | ทำอะไร | ขนาด layer จริง (`docker history` ของ image ที่ Jenkins สร้าง) |
|---|---|---|---:|
| ฐาน | `FROM node:22-alpine` · `WORKDIR /app` | Node.js 22 บน Alpine และโฟลเดอร์ทำงาน | ≈ 177 MB · 8.19 kB |
| ① ติดตั้ง dependencies | `COPY package*.json` แล้ว `RUN npm ci ... && npm cache clean --force` | ติดตั้งตาม lock file แล้วลบ cache ของ npm ใน `RUN` เดียวกัน | 45.1 kB · **357 MB** |
| ② build เว็บไซต์ | `COPY . .` แล้ว `RUN npm run build && rm -rf .next/cache` | คัดลอกซอร์สแล้ว `next build` ลบ cache ของการ build | 422 kB · 5.62 MB |
| ข้อมูล build | `ARG` ×4 + `ENV APP_VERSION=...` | รับค่าจาก Jenkins ผ่าน `--build-arg` แล้วเก็บเป็น env ของ image | 0 B |
| ③ เริ่มแอป | `EXPOSE 3000` · `CMD ["npm", "start"]` | ประกาศ port และเริ่ม `next start` | 0 B |
| ④ ตรวจสุขภาพ | `HEALTHCHECK ... wget /api/health` | ให้ **Docker เอง** ถามแอปทุก 1 วินาทีช่วง 30 วินาทีแรก หลังจากนั้นทุก 10 วินาที | 0 B |

ภาพรวมขนาด: **693 MB** บนดิสก์ และ **154 MB** ที่ต้องดาวน์โหลด (ค่าจาก stage Build ในการทดลองที่ 10) ใน image มี `node_modules` 337.6 MB และ `.next` 5.3 MB

![Dockerfile แบบ single-stage](./images/lab3_theory_single_stage.png)

*ภาพที่ 14 Dockerfile แบบ single-stage: layer ที่ใหญ่ที่สุดคือ `npm ci` ตัวเลขทุกตัวตรงกับ `docker history` ของ image ที่ Jenkins สร้าง*

หลักการสี่ข้อที่ซ่อนอยู่ใน Dockerfile นี้

1. **`FROM` หนึ่งบรรทัด = image หนึ่งตัว** ทุกอย่างที่ติดตั้งจะติดอยู่ใน image สุดท้าย
2. **คัดลอก dependency ก่อนซอร์สโค้ด** การแก้โค้ดร้านจึงไม่ทำให้ layer `npm ci` (357 MB) ต้องสร้างใหม่
3. **ลบของที่ไม่ใช้ใน `RUN` เดียวกัน** layer ที่สร้างเสร็จแล้วแก้ไม่ได้ `RUN rm ...` บรรทัดใหม่เพียงซ่อนไฟล์ image ไม่ได้เล็กลง
4. **ให้ Docker ตรวจสุขภาพแทนเรา** container มีสถานะ `starting` → `healthy` (หรือ `unhealthy`) ติดตัว stage Test และ Deploy อ่านค่านี้ด้วย `docker inspect -f '{{.State.Health.Status}}'`

### Layer cache: เรียงจากสิ่งที่เปลี่ยนน้อยไปหาสิ่งที่เปลี่ยนบ่อย

Docker จำผลของแต่ละ layer ไว้ ถ้าคำสั่งและไฟล์ที่ป้อนให้ layer นั้นไม่เปลี่ยน ครั้งถัดไปใช้ของเดิม (`CACHED`) Dockerfile ของร้านวางข้อมูลที่เปลี่ยนทุก build (`APP_VERSION`, `BUILD_NUMBER`, `BUILD_TIME`) ไว้ **ท้ายสุด** เมื่อออกเวอร์ชันใหม่ ทั้ง 5 ขั้นที่สร้างไฟล์จึง `CACHED` และตอน push Docker Hub ตอบ `Layer already exists` ทุก layer (พิสูจน์ในการทดลองที่ 15)

![Layer cache](./images/lab3_theory_layer_cache.png)

*ภาพที่ 15 build #2 เปลี่ยนเฉพาะค่าตั้งค่าของ image ส่วน layer อื่นใช้ cache และไม่ต้องอัปโหลดซ้ำ*

---

## 5. อ่าน Jenkinsfile ก่อนรัน

อ่านทีละส่วนโดยถามตัวเองเสมอว่า **“บรรทัดนี้ทำงานที่ Jenkins หรือที่ devtools”**

![Pipeline 6 stage ทำงานที่ใด](./images/lab3_arch_stages.png)

*ภาพที่ 16 ทุก stage เริ่มที่ Jenkins (แถวสีชมพู) ส่งสคริปต์ผ่าน SSH (แถวสีฟ้า) แล้วคำสั่ง Docker ทำงานบน devtools (แถวสีม่วง) แถวสีเขียวคือหลักฐานจริงจาก build #1*

### 5.1 `parameters` — ค่าที่ผู้สั่ง build กำหนดได้

```groovy
parameters {
  string(name: 'APP_VERSION', defaultValue: '1.0.0',
         description: 'เวอร์ชันที่จะฝังเข้า image และแสดงบนหน้าเว็บ')
}
```

build แรกใช้ค่า default `1.0.0` หลังจาก build แรก Jenkins ลงทะเบียน parameter แล้ว ปุ่ม **Build Now** จะเปลี่ยนเป็น **Build with Parameters** (ใช้ในการทดลองที่ 15)

### 5.2 `environment` — ค่าคงที่ของ Pipeline (ถูกแทนค่าบน Jenkins)

```groovy
environment {
  DEVTOOLS    = 'root@devtools'      // ปลายทาง SSH (ชื่อจาก --add-host, port 22)
  SSH_OPTS    = '-o StrictHostKeyChecking=accept-new -o LogLevel=ERROR'
  APP_DIR     = '~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop'
  APP_NAME    = 'catfood-shop'       // ชื่อ image และ repository บน Docker Hub
  DEPLOY_NAME = 'catfood-web'        // container ของร้าน (port 3000)
  VERSION     = "${params.APP_VERSION}"
}
```

| ตัวแปร | ใช้ทำอะไร |
|---|---|
| `DEVTOOLS`, `SSH_OPTS` | ปลายทางและตัวเลือกของ SSH `LogLevel=ERROR` ตัดข้อความเตือนออกจาก console |
| `APP_DIR` | path ของ build context **บน devtools** — เครื่องหมาย `~` ถูกขยายเป็น `/root` โดย shell ของ devtools |
| `APP_NAME`, `DEPLOY_NAME` | ชื่อ image/repository และชื่อ container ของร้าน |
| `VERSION` | สตริง Groovy แบบ `"..."` ถูกแทนค่า `params.APP_VERSION` บน Jenkins ตั้งแต่เริ่ม Pipeline ทำให้ shell เห็น `$VERSION` ได้ตั้งแต่ build แรก |

`$BUILD_NUMBER` ไม่ต้องประกาศ Jenkins ใส่ให้ทุก build อัตโนมัติ

### 5.3 Credentials — ใช้ที่ไหน และป้องกันอย่างไร

| ตำแหน่งในโค้ด | ผลบน Jenkins | ป้องกันอะไร |
|---|---|---|
| `withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY')])` ทุก stage | เขียน private key เป็นไฟล์ชั่วคราว ใส่ path ใน `$SSH_KEY` ลบไฟล์เมื่อจบบล็อก | console แสดง `ssh -i ****` ไม่มี key อยู่ในโค้ด |
| `usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')` ใน Push, Pull, Deploy | ผูกชื่อบัญชีและ token เฉพาะในบล็อก | Jenkins รุ่นนี้ mask ทั้งสองค่า console จึงแสดง `docker.io/****/catfood-shop` |
| `sh '''set +x ...` | shell ไม่พิมพ์คำสั่งที่มี token | token ไม่ปรากฏใน console |
| `echo "$DOCKER_TOKEN" \| ssh ... docker login --password-stdin` | token เดินทางทาง **stdin** ของ SSH | ไม่อยู่ใน command line ของ process ใดทั้งสองฝั่ง |
| `DOCKER_CONFIG=/tmp/jenkins-docker-$BUILD` + `trap 'docker logout; rm -rf "$DOCKER_CONFIG"' EXIT` | ไฟล์ login บน devtools อยู่ในโฟลเดอร์ชั่วคราวของ build นั้น | ถูกลบทันทีที่ push จบ ผู้เขียนตรวจหลัง build #2 แล้วไม่มีโฟลเดอร์ `/tmp/jenkins-docker-*` เหลือ |

### 5.4 กายวิภาคของหนึ่ง stage — ตัวแปรถูกแทนค่าที่ฝั่งใด

ทุก stage ยกเว้น Connect ใช้รูปแบบเดียวกัน ดู stage Build เป็นตัวอย่าง

```groovy
sh '''
  ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
    "APP_DIR=$APP_DIR IMAGE=$APP_NAME:$BUILD_NUMBER VERSION=$VERSION BUILD=$BUILD_NUMBER bash -s" <<'EOF'
set -e
cd "$APP_DIR"
docker build --provenance=false \
  --build-arg APP_VERSION="$VERSION" \
  --build-arg BUILD_NUMBER="$BUILD" \
  --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -t "$IMAGE" .
docker image ls "$IMAGE"
EOF
'''
```

| ส่วน | แทนค่า / ทำงานที่ | อธิบาย |
|---|---|---|
| `sh '''...'''` | Jenkins | สตริง Groovy อัญประกาศเดี่ยวสามตัว Groovy **ไม่แทนค่า** `$` ใด ๆ ส่งทั้งก้อนให้ shell ของ Jenkins |
| `"APP_DIR=$APP_DIR IMAGE=$APP_NAME:$BUILD_NUMBER ..."` | **shell ของ Jenkins** | อยู่ในอัญประกาศคู่ shell ของ Jenkins แทนค่าจาก `environment` ก่อนส่ง console แสดงผลจริงว่า `APP_DIR=~/labwork/... IMAGE=catfood-shop:1 VERSION=1.0.0 BUILD=1 bash -s` |
| `ssh ... "$DEVTOOLS" "... bash -s"` | Jenkins → devtools | เปิด SSH ไปที่ `root@devtools` แล้วสั่ง `bash -s` = “อ่านสคริปต์จาก stdin” |
| `<<'EOF'` … `EOF` | ส่งทาง stdin | heredoc ที่ **ใส่อัญประกาศ** ทำให้ shell ของ Jenkins ไม่แตะเนื้อสคริปต์เลย |
| `cd "$APP_DIR"`, `$(date ...)`, `docker build ...` | **bash ของ devtools** | ตัวแปรในเนื้อสคริปต์คือค่าที่ส่งมาเป็น `VAR=value` เวลา `BUILD_TIME` จึงเป็นเวลาของ devtools และ `docker` คือ Docker CLI ของ devtools |
| `--provenance=false` | devtools | ให้ push เป็น manifest เดี่ยว digest ใน console จึงเท่ากับที่หน้า Docker Hub แสดงทุกตัวอักษร (ถ้าเปิด attestation ค่าเริ่มต้นของ BuildKit จะเป็นคนละค่า) |

**สรุปทั้ง Pipeline**

| Stage | โค้ดบน Jenkins | คำสั่งบน devtools | Credential |
|---|---|---|---|
| Connect | เปิด SSH หนึ่งบรรทัด | `hostname; whoami; docker --version; ls $APP_DIR/Dockerfile` | `devtools-ssh` |
| Build | ใส่ `IMAGE`, `VERSION`, `BUILD` | `docker build --provenance=false --build-arg ... -t catfood-shop:N .` | `devtools-ssh` |
| Test | ใส่ `IMAGE`, `NAME=catfood-test-N` | `docker run -d` → วนอ่าน health ≤ 30 ครั้ง → `docker rm -f` → ต้อง `healthy` | `devtools-ssh` |
| Push | `set +x`, ส่ง token ทาง stdin | `docker login` (DOCKER_CONFIG ชั่วคราว) → `docker tag` + `docker push :N` และ `:latest` → logout | `devtools-ssh` + `dockerhub` |
| Pull | ใส่ `HUB=docker.io/<user>/catfood-shop` | จำ digest → `docker image rm` ทุก tag ของ build นี้ → `docker pull :N` → เทียบ digest | `devtools-ssh` + ชื่อบัญชีจาก `dockerhub` |
| Deploy | ใส่ `VERSION`, `BUILD`, `NAME` | `docker run -d --name catfood-web -p 3000:3000 <HUB>:N` → รอ `healthy` → อ่าน `/api/health` → เทียบเวอร์ชัน | `devtools-ssh` + ชื่อบัญชีจาก `dockerhub` |

ทุก stage จบด้วยคำสั่งตรวจ ถ้าเงื่อนไขไม่จริง stage นั้นล้ม และ stage ถัดไปถูกข้าม (**fail fast**) image ที่ไม่ healthy จึงไม่ถูก push และ image ที่ digest ไม่ตรงจะไม่ถูก deploy

### 5.5 Jenkinsfile ฉบับสมบูรณ์

ไฟล์เดียวกับ `~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/Jenkinsfile` (แสดงใน shell ของ devtools ด้วย `cat` แล้วคัดลอกไปวางใน Jenkins)

```groovy
// LAB 3 — Jenkins เป็น "ผู้สั่ง" devtools เป็น "ผู้ทำ"
// Jenkins ไม่มี Docker อยู่ข้างใน ทุกคำสั่ง docker ถูกส่งผ่าน SSH ไปรันบน devtools
pipeline {
  agent any

  parameters {
    string(name: 'APP_VERSION', defaultValue: '1.0.0',
           description: 'เวอร์ชันที่จะฝังเข้า image และแสดงบนหน้าเว็บ')
  }

  environment {
    DEVTOOLS    = 'root@devtools'                  // ปลายทาง SSH (ชื่อ devtools มาจาก --add-host, port 22)
    SSH_OPTS    = '-o StrictHostKeyChecking=accept-new -o LogLevel=ERROR'
    APP_DIR     = '~/labwork/DevTools/04_Jenkins/001_Jenikin/003_LAB_Docker_Build_Push/catfood-shop'  // build context บน devtools
    APP_NAME    = 'catfood-shop'                   // ชื่อ image และชื่อ repository บน Docker Hub
    DEPLOY_NAME = 'catfood-web'                    // container ของร้านที่เปิดให้ลูกค้าใช้ (port 3000)
    VERSION     = "${params.APP_VERSION}"
  }

  stages {
    stage('Connect') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY')]) {
          sh 'ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" "hostname; whoami; docker --version; ls $APP_DIR/Dockerfile"'
        }
      }
    }

    stage('Build') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY')]) {
          sh '''
            ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "APP_DIR=$APP_DIR IMAGE=$APP_NAME:$BUILD_NUMBER VERSION=$VERSION BUILD=$BUILD_NUMBER bash -s" <<'EOF'
set -e
cd "$APP_DIR"
docker build --provenance=false \
  --build-arg APP_VERSION="$VERSION" \
  --build-arg BUILD_NUMBER="$BUILD" \
  --build-arg BUILD_TIME="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -t "$IMAGE" .
docker image ls "$IMAGE"
EOF
          '''
        }
      }
    }

    stage('Test') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY')]) {
          sh '''
            ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "IMAGE=$APP_NAME:$BUILD_NUMBER NAME=catfood-test-$BUILD_NUMBER bash -s" <<'EOF'
docker run -d --name "$NAME" "$IMAGE" >/dev/null
for i in $(seq 1 30); do
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' "$NAME")
  echo "health of $NAME: $STATUS"
  [ "$STATUS" = healthy ] && break
  sleep 1
done
docker rm -f "$NAME" >/dev/null
[ "$STATUS" = healthy ]
EOF
          '''
        }
      }
    }

    stage('Push') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY'),
                         usernamePassword(credentialsId: 'dockerhub',
                           usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
          sh '''set +x
            # token เดินทางทาง stdin ของ SSH เท่านั้น ไม่ปรากฏใน command line และ console
            echo "$DOCKER_TOKEN" | ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "DOCKER_CONFIG=/tmp/jenkins-docker-$BUILD_NUMBER docker login -u $DOCKER_USER --password-stdin"
            ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "IMAGE=$APP_NAME:$BUILD_NUMBER HUB=docker.io/$DOCKER_USER/$APP_NAME BUILD=$BUILD_NUMBER bash -s" <<'EOF'
set -eo pipefail
export DOCKER_CONFIG=/tmp/jenkins-docker-$BUILD
trap 'docker logout >/dev/null 2>&1; rm -rf "$DOCKER_CONFIG"' EXIT
for tag in "$BUILD" latest; do
  docker tag "$IMAGE" "$HUB:$tag"
  docker push "$HUB:$tag" | grep -v ': Waiting$'   # ตัดบรรทัดรอคิวออก ให้เห็นผลของแต่ละ layer ชัด
done
EOF
          '''
        }
      }
    }

    stage('Pull') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY'),
                         usernamePassword(credentialsId: 'dockerhub',
                           usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
          sh '''
            ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "IMAGE=$APP_NAME:$BUILD_NUMBER HUB=docker.io/$DOCKER_USER/$APP_NAME BUILD=$BUILD_NUMBER bash -s" <<'EOF'
set -e
PUSHED=$(docker image inspect -f '{{index .RepoDigests 0}}' "$HUB:$BUILD" | cut -d@ -f2)
echo "digest ที่ push: $PUSHED"
docker image rm "$IMAGE" "$HUB:$BUILD" "$HUB:latest"   # ลบ image ในเครื่องทิ้ง เพื่อพิสูจน์ว่าดึงจาก Docker Hub จริง
docker pull "$HUB:$BUILD"
PULLED=$(docker image inspect -f '{{index .RepoDigests 0}}' "$HUB:$BUILD" | cut -d@ -f2)
echo "digest ที่ pull: $PULLED"
[ "$PUSHED" = "$PULLED" ] && echo "digest ตรงกัน: image ที่ pull คือ image เดียวกับที่ push"
EOF
          '''
        }
      }
    }

    stage('Deploy') {
      steps {
        withCredentials([sshUserPrivateKey(credentialsId: 'devtools-ssh', keyFileVariable: 'SSH_KEY'),
                         usernamePassword(credentialsId: 'dockerhub',
                           usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_TOKEN')]) {
          sh '''
            ssh -i "$SSH_KEY" $SSH_OPTS "$DEVTOOLS" \
              "HUB=docker.io/$DOCKER_USER/$APP_NAME BUILD=$BUILD_NUMBER VERSION=$VERSION NAME=$DEPLOY_NAME bash -s" <<'EOF'
set -e
docker rm -f "$NAME" 2>/dev/null || true
docker run -d --name "$NAME" --restart unless-stopped -p 3000:3000 "$HUB:$BUILD"
for i in $(seq 1 30); do
  STATUS=$(docker inspect -f '{{.State.Health.Status}}' "$NAME")
  echo "health of $NAME: $STATUS"
  [ "$STATUS" = healthy ] && break
  sleep 1
done
[ "$STATUS" = healthy ]
docker ps --filter "name=^$NAME$" --format '{{.Names}}  {{.Image}}  {{.Status}}  {{.Ports}}'
docker exec "$NAME" wget -qO- http://127.0.0.1:3000/api/health; echo
[ "$(docker exec "$NAME" printenv APP_VERSION BUILD_NUMBER | paste -sd' ')" = "$VERSION $BUILD" ]
echo "เว็บตอบเวอร์ชัน $VERSION build #$BUILD ตรงกับ Pipeline"
EOF
          '''
        }
      }
    }
  }

  post {
    success {
      echo "เปิดร้านได้ที่ http://localhost:3000 (catfood-shop v${params.APP_VERSION} build #${env.BUILD_NUMBER})"
    }
  }
}
```

---

## 6. รัน Pipeline ทีละ stage

### การทดลองที่ 8 — สร้าง job `docker-build-push` และสั่ง build ครั้งแรก

🎯 **เป้าหมาย:** เริ่ม build ครั้งแรกของร้าน **จาก Jenkins** และดูภาพรวมของทั้ง 6 stage

🛠️ **ขั้นตอน (browser):**

1. Dashboard → **New Item** → ชื่อ `docker-build-push` → **Pipeline** → **OK**

![New Item docker-build-push](./images/lab3_d1a_new_item_pipeline.png)

*ภาพที่ 17 สร้าง job ชนิด Pipeline*

2. **Pipeline → Definition: Pipeline script** วาง Jenkinsfile ฉบับสมบูรณ์ทั้งไฟล์ → **Save**

![Jenkinsfile ใน editor](./images/lab3_d1b_pipeline_script.png)

*ภาพที่ 18 Jenkinsfile ใน editor เริ่มจาก `parameters` และ `environment`*

3. กด **Build Now**

![Build Now](./images/lab3_d1c_build_now.png)

*ภาพที่ 19 build แรกของ job ใช้ค่า default `APP_VERSION=1.0.0`*

4. ระหว่างรอ เลือก build **#1 → Pipeline Overview** (หน้า **Stages**) จะเห็น stage ที่กำลังทำงานและ log สด

![build #1 ระหว่างทำงาน](./images/lab3_d1d_overview_running_b1.png)

*ภาพที่ 20 build #1 ขณะอยู่ใน stage Build: log ของ devtools ไหลกลับมาที่ Jenkins ทีละบรรทัด (`npm ci` เสร็จใน 10.4 วินาที)*

📝 **คำอธิบาย:** Jenkins อ่าน Jenkinsfile แล้วรันทีละ stage หน้า Stages แสดง log แยกตาม stage ซึ่งอ่านง่ายกว่า Console Output ที่รวมทุกอย่างเป็นก้อนเดียว การทดลองที่ 9–14 จะคลิกอ่านทีละ stage

✅ **ผลที่ควรเห็น (ผลจริง):**

![build #1 สำเร็จทั้ง 6 stage](./images/lab3_d2a_overview_b1.png)

*ภาพที่ 21 build #1 เขียวครบ Connect → Build → Test → Push → Pull → Deploy → Post Actions ใช้เวลารวม 1 นาที 6 วินาที*

| Stage | Connect | Build | Test | Push | Pull | Deploy | Post Actions | **รวม** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| build #1 | 0.41 s | 30 s | 3 s | 24 s | 4 s | 3 s | 75 ms | **1 min 6 s** |

💡 **ข้อสรุป:** นักศึกษาไม่ได้พิมพ์คำสั่ง Docker เลย แต่ร้านถูก build, ทดสอบ, push, pull และ deploy ครบ เวลาส่วนใหญ่อยู่ที่ Build (build ครั้งแรกไม่มี cache) และ Push (อัปโหลดขึ้นอินเทอร์เน็ต)

### การทดลองที่ 9 — Stage Connect: เข้าถึงเครื่องที่ถูกต้องหรือไม่?

🎯 **เป้าหมาย:** ยืนยันว่า SSH สำเร็จและปลายทางคือ devtools ที่มี Docker

🛠️ **ขั้นตอน (browser):** หน้า Stages ของ build #1 → คลิก **Connect**

📝 **คำอธิบาย:** stage นี้ส่งคำสั่งสั้น ๆ บรรทัดเดียว `hostname; whoami; docker --version; ls $APP_DIR/Dockerfile` ถ้า SSH หรือไฟล์มีปัญหา Pipeline จะล้มตั้งแต่ตรงนี้ ไม่เสียเวลา build

✅ **ผลที่ควรเห็น (ผลจริง):**

![stage Connect](./images/lab3_e1_stage_connect_b1.png)

*ภาพที่ 22 `1b12b5e8724f` · `root` · `Docker version 29.8.1, build 4a63305` · `/root/labwork/.../catfood-shop/Dockerfile` ใน 0.41 วินาที*

💡 **ข้อสรุป:** hostname ตรงกับ `hostname` ของ devtools (การทดลองที่ 3) ผู้ใช้คือ `root` และ `~` ถูกขยายเป็น `/root` บน devtools แปลว่า **ไปถึงเครื่องที่ถูกต้อง ในบัญชีที่ถูกต้อง และเห็น build context แล้ว**

### การทดลองที่ 10 — Stage Build: สร้าง image จากซอร์สโค้ดร้าน

🎯 **เป้าหมาย:** เห็นว่า Dockerfile แต่ละบรรทัดทำงานอย่างไรบน devtools และได้ image ที่มี tag ตามเลข build

🛠️ **ขั้นตอน (browser):** คลิก **Build** แล้วเลื่อนอ่านสามช่วง

![stage Build ช่วงต้น](./images/lab3_e2a_stage_build_start_b1.png)

*ภาพที่ 23 บรรทัด `+ ssh ... root@devtools APP_DIR=~/labwork/... IMAGE=catfood-shop:1 VERSION=1.0.0 BUILD=1 bash -s` คือคำสั่งหลังจาก shell ของ Jenkins แทนค่าแล้ว ตามด้วยการดาวน์โหลด `node:22-alpine` (ไม่มี cache)*

![stage Build ช่วง npm ci](./images/lab3_e2b_stage_build_npm_b1.png)

*ภาพที่ 24 `[2/6] WORKDIR` → `[3/6] COPY package.json` → `[4/6] RUN npm ci` (`added 24 packages in 10s`) → `[5/6] COPY . .` → `[6/6] RUN npm run build` (Next.js 16.3.6)*

![stage Build ช่วงท้าย](./images/lab3_e2c_stage_build_end_b1.png)

*ภาพที่ 25 `exporting manifest sha256:046f4bd8af08…` แล้ว `docker image ls` แสดง `catfood-shop:1   046f4bd8af08   693MB   154MB`*

📝 **คำอธิบาย:** BuildKit ของ devtools แสดงแต่ละขั้นเป็น `#N [ขั้น/6]` ขั้น `FROM` ดาวน์โหลด base image (layer ใหญ่สุด 55.59 MB) ขั้น `npm ci` ติดตั้ง dependency 24 แพ็กเกจ แล้ว `next build` สร้างหน้าเว็บ สุดท้าย export เป็น image ชื่อ `catfood-shop:1` (เลข `1` คือ `$BUILD_NUMBER`)

✅ **ผลที่ควรเห็น:** stage Build เขียวใน 30 วินาที และบรรทัดสุดท้ายมี `catfood-shop:1` ขนาด `693MB` / `154MB`

**ตรวจเพิ่ม (ไม่บังคับ, shell ของ devtools):** ส่องขนาด layer ของ image ที่ Jenkins สร้าง (อ่านอย่างเดียว ไม่ได้ build ใหม่)

```bash
docker history --format '{{.Size}}\t{{.CreatedBy}}' <DOCKER_USER>/catfood-shop:1 | head -16
```

```text
0B      CMD ["npm" "start"]
0B      HEALTHCHECK {Test:[CMD-SHELL wget -qO- http:…
0B      EXPOSE [3000/tcp]
0B      ENV APP_VERSION=1.0.0 BUILD_NUMBER=1 GIT_COM…
0B      ARG BUILD_TIME=2026-09-25T13:27:54Z
0B      ARG GIT_COMMIT=none
0B      ARG BUILD_NUMBER=1
0B      ARG APP_VERSION=1.0.0
0B      ENV NODE_ENV=production PORT=3000
5.62MB  RUN /bin/sh -c npm run build && rm -rf .next…
422kB   COPY . . # buildkit
357MB   RUN /bin/sh -c npm ci --no-audit --no-fund &…
45.1kB  COPY package.json package-lock.json ./ # bui…
0B      ENV NEXT_TELEMETRY_DISABLED=1
8.19kB  WORKDIR /app
0B      CMD ["node"]
```

💡 **ข้อสรุป:** การ build เกิดบน Docker daemon ของ devtools จากซอร์สบน devtools ทั้งหมด Jenkins รับเพียง log กลับมาแสดง image ที่ได้มี tag ตรงกับเลข build (`catfood-shop:1`) และ layer `npm ci` 357 MB คือส่วนที่ใหญ่ที่สุดตามที่วิเคราะห์ไว้ในหัวข้อ 4

### การทดลองที่ 11 — Stage Test: image ที่ได้ใช้งานได้จริงหรือไม่?

🎯 **เป้าหมาย:** ทดสอบ image ก่อนส่งขึ้น registry โดยอาศัย `HEALTHCHECK`

🛠️ **ขั้นตอน (browser):** คลิก **Test**

📝 **คำอธิบาย:** devtools รัน container ชั่วคราว `catfood-test-1` (ไม่ publish port) แล้วอ่าน `docker inspect -f '{{.State.Health.Status}}'` ทุก 1 วินาที สูงสุด 30 ครั้ง จากนั้นลบ container ทิ้งเสมอ บรรทัดสุดท้าย `[ "$STATUS" = healthy ]` คือเงื่อนไขผ่าน/ไม่ผ่านของ stage

✅ **ผลที่ควรเห็น (ผลจริง):**

![stage Test](./images/lab3_e3_stage_test_b1.png)

*ภาพที่ 26 `health of catfood-test-1: starting` สองครั้ง แล้ว `healthy` ใน 3 วินาที*

💡 **ข้อสรุป:** แอปใน image ตอบ `/api/health` ได้จริง Pipeline จึงยอมให้เดินต่อไปที่ Push ถ้าสถานะไม่ถึง `healthy` stage นี้ล้มและ **ไม่มี image เสียขึ้น Docker Hub**

### การทดลองที่ 12 — Stage Push: ส่ง image ขึ้น Docker Hub

🎯 **เป้าหมาย:** เห็นการ login แบบไม่เปิดเผย token การอัปโหลด layer และ digest ของ image ที่ push

🛠️ **ขั้นตอน (browser):** คลิก **Push** แล้วเลื่อนลงจนสุด

![stage Push ช่วงต้น](./images/lab3_e4a_stage_push_b1.png)

*ภาพที่ 27 `Login Succeeded` ตามด้วย push tag `1`: base layer 4 ชั้น `Layer already exists` และ layer ของร้าน 5 ชั้น `Pushed` แล้ว `1: digest: sha256:046f4bd8af08…  size: 2006`*

![stage Push ช่วงท้าย](./images/lab3_e4b_stage_push_digest_b1.png)

*ภาพที่ 28 push tag `latest` ต่อทันที: ทั้ง 9 layer `Layer already exists` และ `latest: digest:` ค่าเดียวกับ tag `1`*

📝 **คำอธิบาย:** token เดินทางผ่าน stdin ของ SSH ไปที่ `docker login --password-stdin` บน devtools ข้อความ `WARNING! Your credentials are stored unencrypted in '/tmp/jenkins-docker-1/config.json'` คือโฟลเดอร์ชั่วคราวที่ `trap` ลบทิ้งทันทีเมื่อ push จบ สคริปต์กรองบรรทัด `Waiting` (สถานะรอคิวที่พิมพ์ซ้ำนับร้อยบรรทัด) ออกเพื่อให้เห็นผลของแต่ละ layer ชัดเจน

จากนั้นเปิด `https://hub.docker.com/r/<DOCKER_USER>/catfood-shop/tags` (หน้า Public ไม่ต้อง login)

✅ **ผลที่ควรเห็น (ผลจริง):**

![Docker Hub หลัง build #1](./images/lab3_e4d_hub_tags_b1.png)

*ภาพที่ 29 Docker Hub มี tag `latest` และ `1` ชี้ digest `046f4bd8af08` (กรอบเขียว) ตรงกับ console ขนาดที่ต้องดาวน์โหลด 146.53 MB*

💡 **ข้อสรุป:** tag `1` และ `latest` ได้ digest เดียวกันเพราะเป็น image ตัวเดียวที่ติดป้ายสองป้าย digest 12 ตัวแรกบน Docker Hub ต้องตรงกับบรรทัด `1: digest:` ใน console ทุกตัวอักษร (ได้ผลเช่นนี้เพราะ `--provenance=false`) ขนาด 146.53 MB คือ CONTENT SIZE 154 MB ในหน่วยฐาน 2 (MiB)

> 📝 base layer 4 ชั้นขึ้น `Layer already exists` เพราะ repository ของผู้เขียนมี layer ของ `node:22-alpine` อยู่แล้ว เมื่อนักศึกษา push ขึ้น repository ใหม่เป็นครั้งแรก layer เหล่านี้อาจขึ้นเป็น `Pushed` หรือ `Mounted from library/node` แทน stage Push จึงอาจใช้เวลานานกว่า 24 วินาที

### การทดลองที่ 13 — Stage Pull: ดึง image กลับจาก Docker Hub ลง devtools

🎯 **เป้าหมาย:** พิสูจน์ว่า image ที่จะ deploy มาจาก Docker Hub จริง และเป็นตัวเดียวกับที่ push

🛠️ **ขั้นตอน (browser):** คลิก **Pull**

📝 **คำอธิบาย:** สคริปต์จำ digest ที่ได้ตอน push → `docker image rm` ทุก tag ของ build นี้จน image ถูกลบจากรายการ (`Deleted: sha256:...`) → `docker pull <HUB>:1` → อ่าน digest อีกครั้งแล้วเทียบ ถ้าไม่ตรง stage ล้มและไม่ deploy

✅ **ผลที่ควรเห็น (ผลจริง):**

![stage Pull](./images/lab3_e5_stage_pull_b1.png)

*ภาพที่ 30 `digest ที่ push: sha256:046f4bd8…` → `Untagged` ×3 · `Deleted` → `1: Pulling from ****/catfood-shop` → `Digest: sha256:046f4bd8…` → `Status: Downloaded newer image` → `digest ตรงกัน`*

💡 **ข้อสรุป:** `Pulling from` และ `Digest:` เป็นคำตอบจาก Docker Hub ส่วนบรรทัดสุดท้ายยืนยันว่า digest ที่ pull เท่ากับ digest ที่ push ทุกตัวอักษร จึงเป็น **image ตัวเดียวกันทุกบิต** layer ขึ้น `Already exists` เพราะ devtools ยังเก็บเนื้อหา layer ไว้ใน build cache แม้รายการ image ถูกลบแล้ว Docker จึงดาวน์โหลดเพียง manifest และ config (เครื่องที่ไม่เคยมี layer เหล่านี้จะดาวน์โหลดจริงราว 146 MB)

### การทดลองที่ 14 — Stage Deploy: เปิดร้านจาก image ที่ pull มา

🎯 **เป้าหมาย:** รันร้านจาก image ที่ pull มา แล้วยืนยันว่าเว็บตอบเวอร์ชันและเลข build ที่ Pipeline ตั้งใจ

🛠️ **ขั้นตอน (browser):** คลิก **Deploy** จากนั้นเปิด `http://localhost:3000`

📝 **คำอธิบาย:** devtools ลบ `catfood-web` ตัวเก่า (ถ้ามี) แล้ว `docker run -d --name catfood-web --restart unless-stopped -p 3000:3000 docker.io/<DOCKER_USER>/catfood-shop:1` รอจน `healthy` แสดง `docker ps` อ่าน `/api/health` จากภายใน container และเทียบ `APP_VERSION BUILD_NUMBER` ของ container กับ `VERSION BUILD` ที่ Jenkins ส่งมา

✅ **ผลที่ควรเห็น (ผลจริง):**

![stage Deploy](./images/lab3_e6_stage_deploy_b1.png)

*ภาพที่ 31 `catfood-web  ****/catfood-shop:1  Up 2 seconds (healthy)  0.0.0.0:3000->3000/tcp` · `{"version":"1.0.0","build":"1","builtAt":"2026-09-25T13:27:54Z","host":"b5a6b93df587"}` · `เว็บตอบเวอร์ชัน 1.0.0 build #1 ตรงกับ Pipeline`*

เปิดหน้าร้านแล้วลองใช้งานตามภาพเคลื่อนไหว (9 ฉาก ยาว 21 วินาที)

![สาธิตการใช้งานร้าน](./images/lab3_f4_web_demo_b1.gif)

*ภาพที่ 32 สาธิตจริงบนเว็บที่ Pipeline deploy: chip เวอร์ชัน → รายการสินค้า → กรองหมวด → ใส่ตะกร้า 3 ชิ้น → Deployment info*

![รายการสินค้า](./images/lab3_f2_web_products_b1.jpg)

*ภาพที่ 33 สินค้า 6 รายการ แต่ละการ์ดมีภาพ ป้าย ขนาด คะแนน ราคา และปุ่มใส่ตะกร้า*

| Feature | ทำงานที่ | ทดลองอย่างไร | ผลจริง |
|---|---|---|---|
| chip เวอร์ชัน | server (อ่าน env ของ container ทุก request) | เปิดหน้าแรก | `v1.0.0 · build #1` |
| ตัวกรองหมวด | browser | คลิก “อาหารเปียก”, “ขนมแมว” | เหลือ 1 และ 2 รายการ |
| ตะกร้า | browser | ใส่ตะกร้าสินค้า 3 ชิ้นแรก | `3 ชิ้น · ฿937` (459 + 329 + 149) |
| Deployment info | server | เลื่อนลงล่างสุด หรือกด “ดูข้อมูล build” | version, build, commit, เวลา build, container |

![Deployment info ของ build #1](./images/lab3_f3_web_deploy_info_b1.png)

*ภาพที่ 34 Deployment info: Version `1.0.0` · Jenkins build `#1` · Built at `2026-09-25T13:27:54Z` · Container `b5a6b93df587`*

💡 **ข้อสรุป:** ค่าบนหน้าเว็บตรงกับ console ทุกช่อง — `builtAt` ตรงกับ `/api/health` และ Container `b5a6b93df587` ตรงกับ `host` ใน stage Deploy จึงสืบย้อนได้ครบว่า **หน้าเว็บที่เห็น ← container `catfood-web` ← image digest `046f4bd8…` ← Docker Hub ← build #1 ของ Jenkins** ช่อง Git commit เป็น `none` เพราะ LAB 3 ยังไม่ได้ดึงซอร์สจาก Git (LAB 4 จะเติมให้)

---

## 7. ออกเวอร์ชันใหม่ด้วย Pipeline

### การทดลองที่ 15 — Build with Parameters `1.1.0`: อะไรถูกสร้างใหม่ อะไรถูกใช้ซ้ำ?

🎯 **เป้าหมาย:** ออกเวอร์ชันใหม่โดยเปลี่ยนเพียงค่า parameter แล้วเปรียบเทียบกับ build #1 ทั้งเวลา cache digest และ tag บน Docker Hub

🛠️ **ขั้นตอน (browser):**

1. เปิด job `docker-build-push` → **Build with Parameters**

![Build with Parameters](./images/lab3_g1a_build_with_parameters.png)

*ภาพที่ 35 หลัง build แรก เมนูเปลี่ยนเป็น Build with Parameters*

2. กรอก `APP_VERSION` = `1.1.0` → **Build**

![กรอก APP_VERSION 1.1.0](./images/lab3_g1b_param_110.png)

*ภาพที่ 36 เปลี่ยนเฉพาะเลขเวอร์ชัน ซอร์สโค้ดเหมือนเดิมทุกไฟล์*

3. เปิดหน้า Stages ของ build #2 แล้วอ่าน Build, Push, Pull, Deploy

📝 **คำอธิบาย:** `APP_VERSION` เปลี่ยน ค่า `BUILD_NUMBER` เป็น `2` และ `BUILD_TIME` เป็นเวลาใหม่ ทั้งสามค่าอยู่ท้าย Dockerfile ขั้นที่สร้างไฟล์ทั้ง 5 ขั้นจึงไม่เปลี่ยน

✅ **ผลที่ควรเห็น (ผลจริง):**

![build #2 สำเร็จ](./images/lab3_g2_overview_b2.png)

*ภาพที่ 37 build #2 เขียวทั้ง 6 stage ใช้เวลารวม 24 วินาที มีเมนู Parameters แสดงค่าที่ใช้*

![stage Build ของ build #2](./images/lab3_g3_stage_build_cached_b2.png)

*ภาพที่ 38 `[2/6]`–`[6/6]` ขึ้น `CACHED` ครบ 5 ขั้น export เสร็จใน 0.1 วินาที ได้ `catfood-shop:2   bd8c67e1adc8   693MB   154MB`*

![stage Push ของ build #2](./images/lab3_g4_stage_push_b2.png)

*ภาพที่ 39 ทุก layer `Layer already exists` ไม่มี `Pushed` เลย และ `2: digest: sha256:bd8c67e1adc8…`*

![stage Pull ของ build #2](./images/lab3_g5_stage_pull_b2.png)

*ภาพที่ 40 digest ที่ push และ pull เป็น `sha256:bd8c67e1adc8…` เหมือนกัน*

![stage Deploy ของ build #2](./images/lab3_g6_stage_deploy_b2.png)

*ภาพที่ 41 `catfood-web ****/catfood-shop:2 ... (healthy)` · `"version":"1.1.0","build":"2"` · `เว็บตอบเวอร์ชัน 1.1.0 build #2 ตรงกับ Pipeline`*

refresh หน้า Tags บน Docker Hub

![Docker Hub หลัง build #2](./images/lab3_g7_hub_tags_b2.png)

*ภาพที่ 42 tag `latest` ย้ายมาชี้ digest ใหม่ `bd8c67e1adc8` เหมือน tag `2` (กรอบเขียว) ส่วน tag `1` ยังชี้ `046f4bd8af08` (กรอบแดง)*

refresh `http://localhost:3000`

![ร้านหลัง build #2](./images/lab3_g8_web_hero_b2.jpg)

*ภาพที่ 43 chip เปลี่ยนเป็น `v1.1.0 · build #2`*

![Deployment info ของ build #2](./images/lab3_g9_web_deploy_info_b2.png)

*ภาพที่ 44 Version `1.1.0` · build `#2` · Built at `2026-09-25T13:34:40Z` · Container `8580d8b66a2b`*

| วัดค่า | build #1 (v1.0.0) | build #2 (v1.1.0) |
|---|---:|---:|
| ระยะเวลารวม | 1 min 6 s | **24 s** |
| stage Build | 30 s | 2 s |
| stage Push | 24 s | 12 s |
| ขั้นที่ `CACHED` | 0 (ไม่มี cache) | **5** |
| บรรทัด `Pushed` | 5 | **0** |
| บรรทัด `Layer already exists` | 13 | 18 (9 layer × 2 tag) |
| digest | `046f4bd8af08…` | `bd8c67e1adc8…` |
| container ที่ตอบเว็บ | `b5a6b93df587` | `8580d8b66a2b` |

![Tag กับ Digest](./images/lab3_theory_tag_digest.png)

*ภาพที่ 45 tag ย้ายได้ ส่วน digest ผูกกับเนื้อหาตลอดไป ค่า `046f4bd8…` และ `bd8c67e1…` คือ digest จริงของ build #1 และ #2*

💡 **ข้อสรุป:** build #2 เปลี่ยนเพียงค่า `ENV` ซึ่งเป็น metadata ของ image ไม่ใช่ layer ของระบบไฟล์ ทุกขั้นจึง `CACHED` และทุก layer มีบน Docker Hub แล้ว สิ่งที่อัปโหลดใหม่มีเพียง config กับ manifest ขนาดเล็ก digest จึงเปลี่ยนทั้งที่ไม่มี layer ใดต้องอัปโหลด Pipeline ทั้งเส้นเร็วขึ้นจาก 1 นาที 6 วินาทีเหลือ 24 วินาที tag `latest` เป็นป้ายที่ย้ายตามเวอร์ชันล่าสุด ส่วน tag `1` ยังชี้ image เดิม — **deploy ด้วย tag แต่ตรวจสอบด้วย digest**

---

### ✅ ตรวจปิดแล็บด้วยตา

ตรวจทีละข้อ ทุกข้อต้องเป็นจริงจึงถือว่าจบแล็บ

- [ ] **Credentials:** หน้า Global credentials มี `devtools-ssh` และ `dockerhub` โดยไม่แสดง private key หรือ token
- [ ] **SSH test:** job `devtools-ssh-test` build #1 สีเขียว และ console พิมพ์ hostname เดียวกับ `hostname` ใน shell ของ devtools
- [ ] **Pipeline:** job `docker-build-push` มี build #1 และ #2 สีเขียว หน้า Stages แสดงครบ Connect → Build → Test → Push → Pull → Deploy
- [ ] **Cache:** stage Build ของ build #2 มี `CACHED` ครบ 5 ขั้น และ stage Push ไม่มีบรรทัด `Pushed`
- [ ] **Digest:** บรรทัด `digest ที่ push` และ `digest ที่ pull` ของ build #2 เป็นค่าเดียวกัน และหน้า Tags บน Docker Hub แสดง `latest` / `2` ด้วย digest 12 ตัวแรกเดียวกัน ส่วน `1` เป็นค่าของ build #1
- [ ] **ร้าน:** `http://localhost:3000` แสดง chip `v1.1.0 · build #2` และ Deployment info มี Container ตรงกับ `host` ใน stage Deploy ของ build #2
- [ ] **Jenkins ยังสะอาด:** `docker exec jenkins sh -c 'docker version'` ยังได้ `docker: not found`

---

## 📊 สรุปผลการทดลอง

| # | คำถาม | ผลจริง | ข้อสรุป |
|---|---|---|---|
| 1 | Jenkins พร้อมไหม | Dashboard มี `first-freestyle`, `first-pipeline` | สถานะจาก LAB ก่อนอยู่ใน volume |
| 2 | Jenkins มี Docker ไหม | `docker: not found` exit 127, มี `OpenSSH_10.0p2` | ต้องส่งคำสั่งไปให้เครื่องอื่นทำ |
| 3 | devtools พร้อมไหม | hostname `1b12b5e8724f`, Docker 29.8.1, sshd port 22, ไฟล์ร้านครบ, ยังไม่มี image ร้าน | ปลายทางมีครบ build ครั้งแรกจะมาจาก Jenkins |
| 4 | Jenkins เห็น devtools ไหม | `172.18.0.1 devtools`, `Permission denied (publickey,password)` | เครือข่ายใช้ได้ ขาดเพียง key |
| 5 | ยืนยันตัวตนอย่างไร | ed25519: private 411 B, public 101 B | private → Jenkins, public → devtools |
| 6 | ความลับเก็บที่ไหน | `devtools-ssh` + `dockerhub` ใน Credentials | โค้ดอ้างด้วย ID เท่านั้น |
| 7 | Jenkins เข้า devtools ได้จริงไหม | job ทดสอบพิมพ์ `1b12b5e8724f`, `root`, Docker 29.8.1 | เชื่อมต่อถูกเครื่องก่อนเริ่ม build |
| 8 | Pipeline ครบไหม | build #1 เขียว 6 stage ใน 1 min 6 s | ทุกอย่างเริ่มจากปุ่ม Build |
| 9 | Connect | hostname devtools ใน 0.41 s | SSH ถึงเครื่องที่ถูกต้อง |
| 10 | Build | `catfood-shop:1` 693MB/154MB ใน 30 s | build เกิดบน devtools จากซอร์สบน devtools |
| 11 | Test | `starting` → `healthy` ใน 3 s | image ใช้งานได้ก่อน push |
| 12 | Push | `Login Succeeded`, 5 × `Pushed`, digest `046f4bd8…` = Docker Hub | registry เก็บ image ตัวเดียวกับที่ build |
| 13 | Pull | digest ที่ pull = digest ที่ push | image ที่จะ deploy มาจาก Docker Hub จริง |
| 14 | Deploy | `(healthy)`, `/api/health` = 1.0.0 build 1, เว็บตรงกับ console | สืบย้อนเว็บ → image → build ได้ |
| 15 | Release | build #2 ใน 24 s, 5 `CACHED`, 0 `Pushed`, digest `bd8c67e1…`, `latest` ย้าย | ลำดับ Dockerfile ทำให้ออกเวอร์ชันเร็ว tag ย้ายได้ digest ไม่เปลี่ยน |

## แก้ปัญหาที่พบบ่อย

| อาการ | สาเหตุ | วิธีแก้ |
|---|---|---|
| `Could not resolve hostname devtools` ใน stage Connect | สร้าง `jenkins` โดยไม่มี `--add-host devtools:host-gateway` | ทำการทดลองที่ 4 ใหม่ แล้วตรวจด้วย `docker exec jenkins getent hosts devtools` |
| `Permission denied (publickey,password)` ใน job ทดสอบหรือ stage Connect | public key ไม่อยู่ใน `~/.ssh/authorized_keys`, วาง private key ไม่ครบบรรทัด BEGIN/END หรือวาง `.pub` ผิดไฟล์ | ทำการทดลองที่ 5 ใหม่ แล้วแก้ credential `devtools-ssh` ให้เป็นเนื้อหา `~/.ssh/jenkins_devtools` ทั้งไฟล์ |
| `ERROR: Could not find credentials entry with ID 'devtools-ssh'` หรือ `'dockerhub'` | ID สะกดไม่ตรง | เปิดหน้า Credentials ตรวจ ID ให้เป็น `devtools-ssh` และ `dockerhub` ตรงตัว |
| console แสดง `****@devtools` และ `whoami` ได้ `****` | ใช้ `environment { SSH_KEY = credentials('devtools-ssh') }` ซึ่ง mask username `root` ด้วย | ใช้ Jenkinsfile ของแล็บ (`withCredentials([sshUserPrivateKey(...)])`) |
| `docker: not found` ใน Pipeline | มีคำสั่ง `docker` ที่รันบน Jenkins โดยตรง | ทุกคำสั่ง Docker ต้องอยู่หลัง `ssh -i "$SSH_KEY" ... "$DEVTOOLS"` |
| `cd: ~/labwork/...: No such file or directory` ใน stage Build | ไม่ได้ clone รีโพของวิชาไว้ที่ `~/labwork/DevTools` ตาม LAB 1 | clone ตาม LAB 1 ส่วนที่ 0 แล้วสั่ง build ใหม่ |
| stage Test ล้ม ไม่ถึง `healthy` ภายใน 30 ครั้ง | แอปใน container เริ่มไม่ขึ้น | ใน shell ของ devtools: `docker run -d --name debug-shop catfood-shop:N` แล้ว `docker logs debug-shop` อ่านสาเหตุ (Pipeline ลบ container ทดสอบทิ้งเสมอ) |
| `401 Unauthorized` / `denied: requested access` ใน stage Push | token ผิด หมดอายุ ไม่มีสิทธิ์ Write หรือ username ไม่ตรง | สร้าง token Read & Write ใหม่ แล้วแก้ credential `dockerhub` |
| digest บน Docker Hub ไม่ตรงกับ console | build โดยไม่มี `--provenance=false` | ใช้ Jenkinsfile ของแล็บ แล้วสั่ง build ใหม่ |
| stage Pull ล้มหลังบรรทัด `digest ที่ pull` | digest ไม่ตรง (มีคน push tag เดียวกันทับระหว่างทาง) | สั่ง build ใหม่ และอย่า push tag เดียวกันจากที่อื่นพร้อมกัน |
| `Bind for 0.0.0.0:3000 failed: port is already allocated` ใน stage Deploy | มี container อื่นใช้ port 3000 | `docker ps --filter publish=3000` แล้วลบตัวที่ไม่ใช้ |
| stage Deploy ล้มที่การเทียบเวอร์ชัน | container ไม่ได้รันจาก image ของ build นี้ | ดูบรรทัด `docker ps` ใน stage Deploy ว่า IMAGE เป็น `:N` ของ build ปัจจุบัน |
| `429 Too Many Requests` | Docker Hub rate limit | รอสักครู่ แล้วลดความถี่ในการสั่ง build |
| หน้า Tags บน Docker Hub ว่างหรือ 404 | repository เป็น Private หรือ URL ผิด | ตั้ง `catfood-shop` เป็น Public แล้ว refresh |
| เปิด `localhost:3000` จากเครื่องหลักไม่ได้ | devtools ไม่ได้ publish port 3000 | สร้าง devtools ใหม่ตาม LAB 1 ส่วนที่ 0 (ต้องมี `-p 3000:3000`) |

## สรุป

LAB 3 แยกหน้าที่ให้ชัดเจน: **Jenkins สั่ง devtools ทำ** Jenkins ยังเป็น image มาตรฐานที่ไม่มี Docker ถือเพียง SSH key และ Docker Hub token ใน Credentials ทุก stage ส่งสคริปต์ผ่าน SSH ไปให้ devtools ซึ่งเป็นเจ้าของ Docker daemon ซอร์สโค้ด และ build cache เป็นผู้ build → test → push → pull → deploy ผลการทดลองยืนยันทีละขั้น: SSH ไปถึง hostname ของ devtools จริง image ขนาด 693 MB ผ่าน HEALTHCHECK ก่อนถูก push digest ที่ push เท่ากับที่ pull และที่ Docker Hub แสดง และหน้าเว็บบอกเวอร์ชัน เลข build เวลา build และ container ตรงกับ console ทุกช่อง การออก v1.1.0 ด้วย Build with Parameters ใช้ cache ครบ ไม่ต้องอัปโหลด layer ใหม่ และจบใน 24 วินาที

ข้อจำกัดที่เหลืออยู่คือซอร์สโค้ดยังมาจากโฟลเดอร์บน devtools และต้องกด Build เอง **LAB 4** จะย้ายร้านเดียวกันนี้ขึ้น GitHub ให้ Jenkins อ่าน `Jenkinsfile` จาก repository และ build อัตโนมัติทุกครั้งที่มี commit
