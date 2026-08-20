# CI/CD ด้วย Jenkins บน Docker

ชุดแล็บภาษาไทยนี้พาจากการกด build ด้วยตนเอง ไปจนถึงวงจร `git push → test → build → push → deploy → verify` อัตโนมัติ โดยใช้ Jenkins, Gitea และ Docker ภายใน devtools container ตัวเดียว เรียนภาพรวมและสถาปัตยกรรมจาก [Jenkins_CICD_Docker_Slides.html](./Jenkins_CICD_Docker_Slides.html) แล้วลงมือทำ LAB 1–6 ตามลำดับ

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

## เริ่มระบบ

รันคำสั่ง canonical นี้บนเครื่องหลัก:

```bash
docker run -dit --name devtools-jenkins --privileged \
  --tmpfs /run -v jenkins-dind:/var/lib/docker \
  -p 2222:22 -p 8080:8080 -p 3000:3000 -p 8000:8000 \
  tuchsanai/devtools:2569_1
```

เข้า shell ของ devtools:

```bash
ssh root@localhost -p 2222
```

เมื่อ SSH ถามรหัสผ่าน ใช้ `passwd` จากนั้นทำ LAB ตามลำดับโดยใช้ container เดิมตลอดชุด

URL สำหรับผู้เรียน:

- Jenkins: `http://localhost:8080`
- Gitea: `http://localhost:3000`
- Webapp: `http://localhost:8000`

> `--privileged` ใช้สำหรับแล็บ disposable เท่านั้น ไม่ใช่รูปแบบ production

## เส้นทางการเรียน

| ครั้ง | LAB | โฟลเดอร์ | คำถามหลัก | เวลา |
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
docker exec devtools-jenkins sh -c \
  'until docker info >/dev/null 2>&1; do sleep 2; done; docker ps'
```

Jenkins, Gitea และ webapp ที่สร้างด้วย `--restart unless-stopped` จะกลับมาเอง งาน, build history และ repo อยู่ใน named volumes จึงไม่ต้องทำ wizard ซ้ำ

ถ้าตามไม่ทัน ให้เข้า devtools แล้วใช้ bootstrap ไปยังสถานะจบ LAB ที่ต้องการ:

```bash
docker exec -it devtools-jenkins bash
cd /workspace/001_Jenikin
bash tools/bootstrap/up_to_lab2.sh
```

ตั้งแต่สถานะ LAB 3 ขึ้นไป ต้องส่ง Docker Hub credential ผ่าน environment ด้วย placeholder เท่านั้น:

```bash
export DOCKER_USER='<DOCKER_USER>'
export DOCKER_TOKEN='<DOCKER_TOKEN>'
bash tools/bootstrap/up_to_lab3.sh
unset DOCKER_TOKEN
```

เปลี่ยนเลขท้ายเป็น `up_to_lab4.sh` หรือ `up_to_lab5.sh` ตามจุดที่ต้องการกู้ และรัน `check.sh` ของ LAB ล่าสุดเพื่อยืนยัน

## โครงสร้างชุดสอน

```text
001_Jenikin/
├── Jenkins_CICD_Docker_Slides.html   # สไลด์ self-contained
├── 001_LAB_... ถึง 006_LAB_...       # README, check.sh และไฟล์ทดลอง
├── slides_assets/                    # ภาพและวิดีโอในสไลด์
├── tools/bootstrap/                  # สคริปต์กู้สถานะ
├── tools/ui/                         # UI automation และ assertions
├── docs/                             # แผน, stack และผล integration
└── logs/                             # หลักฐานการรัน
```

เริ่มที่ LAB 1 หากทำต่อเนื่อง หรือเปิด LAB เป้าหมายแล้วใช้ bootstrap ตามหัวข้อกู้สถานะเมื่อเข้าชั้นเรียนกลางทาง
