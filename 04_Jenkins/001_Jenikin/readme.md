# CI/CD ด้วย Jenkins บน Docker

ชุดแล็บภาษาไทยนี้พาจากการกด build ด้วยตนเอง ไปจนถึงวงจร `git push → build → test → push → deploy → verify` อัตโนมัติ โดยใช้ Jenkins, GitHub และ Docker ภายใน devtools container ตัวเดียว เรียนภาพรวมและสถาปัตยกรรมจาก [Jenkins_CICD_Docker_Slides.html](./Jenkins_CICD_Docker_Slides.html) แล้วลงมือทำ LAB 1–6 ตามลำดับ

สไลด์เดินตาม README ของแต่ละแล็บทีละขั้น ทุกแล็บเปิดด้วย **หน้าเปิดแล็บพื้นเข้มรูปแบบเดียวกัน** (เลข LAB · ชื่อ · โฟลเดอร์ · จำนวนการทดลอง · เวลา · เกณฑ์จบ · แผนที่ขั้นตอน) ตามด้วยหน้าการทดลองทีละข้อ ที่ใช้เลขเดียวกับหัวข้อ `## การทดลองที่ N` ใน README และมีภาพหน้าจอจริงครบทุกภาพ ปิดท้ายด้วยหน้าสรุปและหน้า “ลงมือทำ” โดยมีแถบบอกตำแหน่งบนทุกหน้าว่ากำลังอยู่การทดลองที่เท่าไรของแล็บใด

## สิ่งที่ต้องมีก่อนเรียน

- เครื่อง 64-bit ที่รัน Docker ได้ และมี RAM ว่างอย่างน้อย 4 GB
- Docker Engine หรือ Docker Desktop, Git และ terminal
- พื้นที่ดิสก์ว่างอย่างน้อย 5 GB
- อินเทอร์เน็ตสำหรับดาวน์โหลด image/plugin และ push ไป Docker Hub
- เว็บเบราว์เซอร์รุ่นปัจจุบัน

## เตรียม Docker Hub ก่อนคาบ

ทำรายการนี้ล่วงหน้าก่อนเริ่ม LAB 3:

1. สมัคร Docker Hub และยืนยันอีเมล
2. สร้าง Access Token สิทธิ์ **Read & Write** เท่านั้น
3. สร้าง public repository ชื่อ `ci-demo`
4. สร้าง public repository ชื่อ `cicd-webapp`
5. เก็บ username/token ไว้ใน password manager และอย่าเขียนลงไฟล์ชุดสอน

ดูขั้นตรวจความพร้อมและอาการผิดพลาดที่ [LAB 3 — Docker Build & Push](./003_LAB_Docker_Build_Push/README.md)

## เตรียม GitHub ก่อนคาบ

ทำรายการนี้ล่วงหน้าก่อนเริ่ม LAB 4:

1. สมัครบัญชี GitHub และยืนยันอีเมล
2. สร้าง Personal access token (classic) โดยเลือก scope `public_repo` และ `admin:repo_hook`
3. เก็บ username/token ไว้ใน password manager; ในเอกสารใช้ placeholder `<GITHUB_USER>` และ `<GITHUB_TOKEN>` เท่านั้น
4. ห้ามจับภาพหรือบันทึกหน้าที่แสดง token
5. ใน LAB 4 นักศึกษาสร้าง public repository ชื่อ `hello-ci` ของตนเองและทำงานใน repository นั้น ไม่แก้ไข course repository โดยตรง

## เริ่มระบบ

รันคำสั่ง canonical นี้บนเครื่องหลัก:

```bash
docker run -dit --name devtools-jenkins --privileged \
  --tmpfs /run -v jenkins-dind:/var/lib/docker \
  -p 2222:22 -p 8080:8080 -p 8000:8000 \
  tuchsanai/devtools:2569_1
docker ps
```

✅ **สิ่งที่ต้องเห็น** (ตัดเฉพาะแถวที่เกี่ยวข้อง):

```text
...
CONTAINER ID   IMAGE                         ...   NAMES
...            tuchsanai/devtools:2569_1    ...   devtools-jenkins
```

เข้า shell ของ devtools:

```bash
ssh root@localhost -p 2222
```

✅ **สิ่งที่ต้องเห็น**:

```text
root@...:~#
```

เมื่อ SSH ถามรหัสผ่าน ใช้ `passwd` จากนั้นจัดเตรียมชุดสอนจาก public repository:

```bash
if [ -d "$HOME/DevTools/.git" ]; then
  git -C "$HOME/DevTools" pull
else
  git clone --depth 1 https://github.com/Tuchsanai/DevTools.git "$HOME/DevTools"
fi
export COURSE_ROOT="$HOME/DevTools/04_Jenkins/001_Jenikin"
echo 'export COURSE_ROOT="$HOME/DevTools/04_Jenkins/001_Jenikin"' > /etc/profile.d/course.sh
```

✅ **สิ่งที่ต้องเห็น** (รันครั้งแรก):

```text
Cloning into '/root/DevTools'...
...
```

ถ้ามี `~/DevTools` อยู่แล้ว ต้องเห็นผลจาก `git pull` เช่น `Already up to date.` แทน การวัดใน container ทดสอบพบว่า shallow clone ทั้ง repository มีขนาด `221M` ซึ่งไม่เกิน 300 MB จึงใช้ clone ธรรมดาและไม่ต้อง sparse checkout

URL สำหรับผู้เรียน:

- Jenkins: `http://localhost:8080`
- Webapp: `http://localhost:8000`

> `--privileged` ใช้สำหรับแล็บ disposable เท่านั้น ไม่ใช่รูปแบบ production

## เส้นทางการเรียน

| ครั้ง | LAB | โฟลเดอร์ | คำถามหลัก | เวลาประมาณการ |
|---|---:|---|---|---:|
| 1 | 1 | [`001_LAB_Jenkins_On_Docker`](./001_LAB_Jenkins_On_Docker/README.md) | ยก Jenkins ใน Docker อย่างไร | 40 นาที |
| 1 | 2 | [`002_LAB_Declarative_Pipeline`](./002_LAB_Declarative_Pipeline/README.md) | เปลี่ยนคลิกเป็นโค้ดอย่างไร | 30 นาที |
| 1 | 3 | [`003_LAB_Docker_Build_Push`](./003_LAB_Docker_Build_Push/README.md) | ให้ Jenkins build และ push image จริงอย่างไร | 45 นาที |
| 2 | 4 | [`004_LAB_Pipeline_From_Git`](./004_LAB_Pipeline_From_Git/README.md) | Jenkinsfile ไปอยู่ใน Git อย่างไร | 40 นาที |
| 2 | 5 | [`005_LAB_Webhook_Trigger`](./005_LAB_Webhook_Trigger/README.md) | push แล้ว build ทันทีอย่างไร | 30 นาที |
| 2 | 6 | [`006_LAB_CICD_Capstone`](./006_LAB_CICD_Capstone/README.md) | วง CI/CD เต็มหน้าตาเป็นอย่างไร | 45 นาที |

จบแต่ละ LAB ให้รัน `bash check.sh` ในโฟลเดอร์นั้น ต้องได้ exit code `0` ก่อนเดินต่อ

## กู้สถานะหลัง restart หรือปิดเครื่อง

เปิด devtools ตัวเดิมและรอ inner Docker ประมาณ 20 วินาที:

```bash
docker start devtools-jenkins
sleep 20
docker exec devtools-jenkins docker ps
```

✅ **สิ่งที่ต้องเห็น** (ตัดเฉพาะแถวที่เกี่ยวข้อง):

```text
devtools-jenkins
CONTAINER ID   IMAGE   ...   NAMES
...            ...     ...   jenkins
```

Jenkins และ webapp ที่สร้างด้วย `--restart unless-stopped` จะกลับมาเอง งานและ build history อยู่ใน named volumes จึงไม่ต้องทำ wizard ซ้ำ

ถ้าตามไม่ทัน ให้เข้า devtools แล้วใช้ bootstrap ไปยังสถานะจบ LAB ที่ต้องการ:

```bash
docker exec -it devtools-jenkins bash
```

✅ **สิ่งที่ต้องเห็น**:

```text
root@...:~#
```

จากนั้นรัน bootstrap ภายใน shell ของ devtools:

```bash
(
  cd "$COURSE_ROOT"
  bash tools/bootstrap/up_to_lab2.sh
)
```

✅ **สิ่งที่ต้องเห็น**:

```text
...
[assert] LAB 2 ready: first-pipeline last build is SUCCESS
```

ตั้งแต่สถานะ LAB 3 ขึ้นไป ต้องส่ง Docker Hub credential ผ่าน environment ด้วย placeholder เท่านั้น:

```bash
export DOCKER_USER='<DOCKER_USER>'
export DOCKER_TOKEN='<DOCKER_TOKEN>'
(
  cd "$COURSE_ROOT"
  bash tools/bootstrap/up_to_lab3.sh
)
unset DOCKER_TOKEN
```

✅ **สิ่งที่ต้องเห็น**:

```text
...
[assert] LAB 3 ready: Docker socket, dockerhub credential, green job, and Hub manifest verified
```

ตั้งแต่สถานะ LAB 4 ขึ้นไป ต้องส่ง GitHub credential เพิ่มด้วย:

```bash
export DOCKER_USER='<DOCKER_USER>'
export DOCKER_TOKEN='<DOCKER_TOKEN>'
export GITHUB_USER='<GITHUB_USER>'
read -rsp 'GitHub PAT: ' GITHUB_TOKEN
printf '\n'
export GITHUB_TOKEN
(
  cd "$COURSE_ROOT"
  bash tools/bootstrap/up_to_lab4.sh
)
unset DOCKER_TOKEN GITHUB_TOKEN
```

`read -rsp` ซ่อน PAT จากหน้าจอและไม่บันทึกค่าลง shell history; อย่าแทน token จริงในคำสั่ง `export` และต้อง `unset GITHUB_TOKEN` หลังใช้งาน

✅ **สิ่งที่ต้องเห็น**:

```text
...
[assert] LAB 4 พร้อม: public GitHub hello-ci/main, ownership marker, Poll SCM และ green SCM build ผ่าน
```

เปลี่ยนเลขท้ายเป็น `up_to_lab5.sh` ตามจุดที่ต้องการกู้ และรัน `check.sh` ของ LAB ล่าสุดเพื่อยืนยัน

## โครงสร้างชุดสอน

```text
001_Jenikin/
├── Jenkins_CICD_Docker_Slides.html   # สไลด์ self-contained
├── 001_LAB_... ถึง 006_LAB_...       # README, check.sh และไฟล์ทดลอง
├── slides_assets/                    # ภาพ วิดีโอ และ diagram (d0–d12) ของสไลด์
├── tools/slides_src.html             # ต้นฉบับสไลด์ก่อน embed asset
├── tools/diagrams.py                 # สร้าง diagram ทั้งชุดจาก visual kit เดียวกัน
├── tools/deck_crops.py               # ครอป screenshot เฉพาะที่ใช้ในสไลด์
├── tools/embed_assets.py             # ฝัง asset ทั้งหมดเป็นไฟล์เดียวแบบ offline
├── tools/check_deck_labs.py          # gate: สไลด์ต้องเดินตาม README ครบทุกขั้นและทุกภาพ
├── tools/check_deck_fit.py           # gate: ทุกหน้าต้องไม่มีเนื้อหาล้นกรอบ 1280×720
├── tools/fit_shots.py                # ขยายกล่องภาพให้เต็มพื้นที่ว่างของแต่ละหน้า
├── tools/bootstrap/                  # สคริปต์กู้สถานะ
├── tools/ui/                         # UI automation และ assertions
├── docs/                             # แผน, stack และผล integration
└── logs/                             # หลักฐานการรัน
```

เริ่มที่ LAB 1 หากทำต่อเนื่อง หรือเปิด LAB เป้าหมายแล้วใช้ bootstrap ตามหัวข้อกู้สถานะเมื่อเข้าชั้นเรียนกลางทาง
