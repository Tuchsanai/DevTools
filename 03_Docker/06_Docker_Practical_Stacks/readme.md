# Docker Practical Stacks — ง่าย → ปานกลาง → ยาก

ชุดสื่อการสอนต่อเนื่องจาก `../01_Docker` สำหรับผู้เรียนที่รู้จัก image/container,
`docker run`, lifecycle, port mapping, bind mount และ Dockerfile พื้นฐานแล้ว

เนื้อหานี้ใช้จังหวะเดียวกับชุดเดิมทุก LAB:

> ปัญหา → ทำนายผล → ทดลองจริง → อ่าน output → ทำให้พังอย่างตั้งใจ → อธิบายสาเหตุ → พิสูจน์ข้อสรุป → cleanup

## ผลลัพธ์การเรียนรู้

เมื่อจบทั้งชุด ผู้เรียนจะสามารถ:

- สังเกตและแก้ปัญหา container ด้วย `exec`, `logs`, `inspect`, `stats` และ `cp`
- แยก configuration ออกจาก image ด้วย environment variables
- เชื่อม container ด้วย user-defined network และ DNS ชื่อ container/service
- เก็บ state ด้วย named volume และเลือก restart policy ได้เหมาะสม
- ทำนายผลของ `CMD`, `ENTRYPOINT`, CLI arguments และ `--entrypoint`
- ใช้ `ARG`, `ENV`, `EXPOSE`, `HEALTHCHECK`, `.dockerignore` และ multi-stage build
- ทำ workflow build → tag → push → pull โดยไม่เผย token
- เปลี่ยนคำสั่งหลายบรรทัดเป็น `compose.yaml` พร้อม readiness dependency
- ประกอบและ debug ระบบ REST API, two-container และ 3-tier application
- ส่งงานปล่อยเดี่ยวที่ผ่าน acceptance test ด้าน health, persistence และ security

## สไลด์

| ตอน | ระดับ | ไฟล์ HTML (source of truth) | PDF | LAB |
|---|---|---|---|---|
| 1 — คุมกล่องให้อยู่มือ | ง่าย | [`Docker_Part1_Easy.html`](./Docker_Part1_Easy.html) | [`Docker_Part1_Easy.pdf`](./Docker_Part1_Easy.pdf) | 1–3 |
| 2 — จากคำสั่งยาวสู่ไฟล์เดียว | ปานกลาง | [`Docker_Part2_Intermediate.html`](./Docker_Part2_Intermediate.html) | [`Docker_Part2_Intermediate.pdf`](./Docker_Part2_Intermediate.pdf) | 4–6 |
| 3 — ประกอบระบบจริง | ยาก | [`Docker_Part3_Advanced.html`](./Docker_Part3_Advanced.html) | [`Docker_Part3_Advanced.pdf`](./Docker_Part3_Advanced.pdf) | 7–9 |

HTML เปิด offline ได้และรองรับ `←` `→`, `Home`, `End`, `O` (overview), `F`
(fullscreen) และ `Ctrl+P` เช่นเดียวกับต้นแบบ ส่วน PPTX เป็นภาพเต็มหน้าเพื่อให้หน้าตา
ตรงกับ HTML ทุกเครื่อง จึงเหมาะกับการนำเสนอแต่แก้ข้อความใน PowerPoint ไม่ได้

## LAB และ port registry

| LAB | โฟลเดอร์ | ระดับ | Outer container | SSH | Web บน host |
|---|---|---|---|---:|---:|
| 1 | [`001_LAB_Nginx_Operations`](./001_LAB_Nginx_Operations) | ง่าย | `devtools-nginx-ops` | 2222 | 18081 |
| 2 | [`002_LAB_Flask_ENV`](./002_LAB_Flask_ENV) | ง่าย | `devtools-flask-env` | 2223 | 18101–18103 |
| 3 | [`003_LAB_MySQL_Network_Volume`](./003_LAB_MySQL_Network_Volume) | ง่าย | `devtools-mysql-netvol` | 2224 | — |
| 4 | [`004_LAB_CMD_ENTRYPOINT`](./004_LAB_CMD_ENTRYPOINT) | ปานกลาง | `devtools-cmd-entrypoint` | 2225 | — |
| 5 | [`005_LAB_Bulletin_Registry`](./005_LAB_Bulletin_Registry) | ปานกลาง | `devtools-bulletin-registry` | 2226 | 18085 |
| 6 | [`006_LAB_Compose_MySQL`](./006_LAB_Compose_MySQL) | ปานกลาง | `devtools-compose-mysql` | 2227 | — |
| 7 | [`007_LAB_FastAPI_OpenCV_Streamlit`](./007_LAB_FastAPI_OpenCV_Streamlit) | ยาก | `devtools-vision-stack` | 2228 | 18501 |
| 8 | [`008_LAB_Fullstack_Todo`](./008_LAB_Fullstack_Todo) | ยาก | `devtools-todo-stack` | 2229 | 18088 |
| 9 | [`009_LAB_Capstone`](./009_LAB_Capstone) | ยาก | `devtools-capstone` | 2230 | 18089 |

หมายเหตุ: port ฝั่ง host ใช้สำหรับผู้เขียน/ผู้สอน capture หลักฐานจริง ผู้เรียนที่ทำผ่าน
VS Code Remote-SSH สามารถ forward port ภายในเครื่องเรียนตาม README ของแต่ละ LAB ได้

## เตรียมเครื่องเรียน

ตัวอย่างต่อไปนี้ใช้ LAB 1; LAB อื่นให้เปลี่ยนชื่อและ port ตามตารางด้านบน

```bash
docker rm -fv devtools-nginx-ops 2>/dev/null
docker run -dit \
  --name devtools-nginx-ops \
  --privileged \
  -p 2222:22 \
  -p 18081:8081 \
  tuchsanai/devtools:2569_1

ssh root@localhost -p 2222
# password: passwd
```

หลัง SSH เข้าไปแล้ว ให้ตรวจว่า Docker-in-Docker พร้อม:

```bash
docker --version
docker compose version
docker info --format '{{.ServerVersion}}'
```

✅ **Expected output:** ทั้งสามคำสั่งคืนเลขเวอร์ชัน ไม่ใช่
`Cannot connect to the Docker daemon`

> เลข version, container ID, image digest, IP และเวลาที่ใช้ build เปลี่ยนได้ตามวันที่และเครื่อง
> ให้ตรวจรูปแบบ สถานะ `Up/healthy` และ HTTP status เป็นหลัก

## Credentials: ใช้จริงตอนทดลอง แต่ห้ามเขียนลงสื่อ

เอกสารและ source ในชุดนี้ใช้ placeholder เท่านั้น:

```bash
git config --global user.name "<YOUR_GIT_NAME>"
git config --global user.email "<YOUR_GIT_EMAIL>"

export GITHUB_TOKEN="<YOUR_GITHUB_TOKEN>"
export DOCKERHUB_USER="<YOUR_DOCKERHUB_USER>"
export DOCKERHUB_TOKEN="<YOUR_DOCKERHUB_TOKEN>"
printf '%s' "$DOCKERHUB_TOKEN" | docker login -u "$DOCKERHUB_USER" --password-stdin
```

- ห้าม commit `.env`, token, password หรือ Docker credential store
- `ARG` และ `ENV` ไม่ใช่ที่เก็บ build secret
- `.env` ช่วยแยก config จาก source แต่ไม่ใช่ production secret manager
- ภาพ capture ต้องไม่มี terminal history หรือค่าความลับ

## Cleanup ที่ต้องทำทุกครั้ง

ภายในเครื่องเรียน ให้ลบเฉพาะ resource ของ LAB ตามคำสั่งท้าย README ของ LAB นั้นก่อน
จากนั้นออกจาก SSH แล้วลบ outer container:

```bash
docker rm -fv devtools-<experiment>
docker ps -a --filter "name=^devtools-"
```

ใช้ `-v` เพิ่มจาก `rm -f` เพื่อเอา anonymous volume ของ Docker-in-Docker ที่ผูกกับ
`/var/lib/docker` ออกด้วย มิฉะนั้น container หายแต่พื้นที่ disk อาจยังค้างอยู่

> ห้ามใช้ `docker system prune`, `docker volume prune` หรือคำสั่งลบ container ทั้งเครื่อง
> เพราะอาจลบงานของผู้อื่น ให้ cleanup ด้วยชื่อ project/container/network/volume ของ LAB เท่านั้น

## วิธีอ่าน LAB

| สัญลักษณ์ | ความหมาย |
|---|---|
| `bash` block | คำสั่งที่ต้องพิมพ์เอง |
| 📝 **คำอธิบาย** | เหตุผล, ความหมาย flag และจุดที่ต้องสังเกต |
| ✅ **Expected output** | หลักฐานขั้นต่ำว่าขั้นนั้นสำเร็จ |
| ⚠️ **ทดลองให้พัง** | failure ที่ตั้งใจสร้างเพื่อเรียนรู้วิธีวินิจฉัย |
| 🧠 **Checkpoint** | หยุดทำนายผลก่อนรัน |
| 🧹 **Cleanup** | คืน resource แบบเจาะจง ไม่กระทบงานอื่น |

## เอกสารอ้างอิงหลัก

- [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)
- [User-defined bridge networks](https://docs.docker.com/engine/network/drivers/bridge/)
- [Restart policies](https://docs.docker.com/engine/containers/start-containers-automatically/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Compose startup order and readiness](https://docs.docker.com/compose/how-tos/startup-order/)

## การสร้างสไลด์และตรวจไฟล์

```bash
python3 tools/build_slides.py
python3 tools/export_decks.py
python3 tools/validate_course.py
```

ดู [`VALIDATION_REPORT.md`](./VALIDATION_REPORT.md) สำหรับผล build/run/capture/cleanup ที่บันทึกจาก
`tuchsanai/devtools:2569_1`

