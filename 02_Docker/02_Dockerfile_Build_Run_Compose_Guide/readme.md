# Dockerfile → Build → Run → Compose

ชุดแล็บ **7 แล็บ** ที่เรียบเรียงจากคู่มือ [`Dockerfile_Build_Run_Compose_Guide.html`](./Dockerfile_Build_Run_Compose_Guide.html)
(12 ตอน · มีฉบับ [PDF](./Dockerfile_Build_Run_Compose_Guide.pdf) ด้วย) โดยแปลงทุกตอนให้เป็น **การทดลองที่รันได้จริง**

ทุกคำสั่งและทุกบล็อก `✅ Expected output` ใน README ของแต่ละแล็บ **มาจากการรันจริง**
ในเครื่องเรียน `tuchsanai/devtools:2569_1` (Docker 29.6.2 · Ubuntu 24.04 · Python 3.12) เมื่อ 14 ส.ค. 2026
log ดิบของทุกขั้นเก็บไว้ที่ `test_logs/` ของแล็บนั้น ๆ ให้ตรวจย้อนได้

> **วงจรการเรียนที่ใช้ทั้งชุด:**
> ทายผล → รัน → สังเกตหลักฐาน → อธิบายเหตุผล → **ทดลองให้พัง** → แก้กลับ

## ผลลัพธ์การเรียนรู้

เมื่อจบชุดนี้ ผู้เรียนควรอธิบายและทดลองให้เห็นได้ว่า:

- Dockerfile, image และ container ต่างกันอย่างไร และเกิดคนละช่วงเวลากันอย่างไร
- ทำไม **ลำดับบรรทัดใน Dockerfile** ถึงทำให้ build ต่างกันจาก 18 วินาที เหลือ 0.8 วินาที
- `RUN` / `CMD` / `ENTRYPOINT` ทำงานคนละเวลา และสิ่งที่พิมพ์ต่อท้ายชื่อ image ไป**แทนที่**หรือไป**ต่อท้าย**อะไร
- image เดียวรันได้หลายสภาพแวดล้อมด้วย `ENV` / `--env-file` / `-e` และทำไม secret ห้ามอยู่ใน `ARG`/`ENV`
- registry ส่งต่อ image อย่างไร และทำไม **tag เชื่อถือไม่ได้เท่า digest**
- ทำไม container ต้องคุยกันด้วย **ชื่อ** ไม่ใช่ IP และ user-defined network ให้อะไรที่ default bridge ไม่มี
- `docker compose` จัดการ build, network, volume, env, healthcheck และ lifecycle ของหลาย service พร้อมกันได้อย่างไร
- multi-stage build ตัด toolchain ออกจาก image ที่นำไป deploy ได้อย่างไร

## เส้นทางแล็บ (ทำเรียงจาก 1 → 7)

| LAB | เวลาโดยประมาณ | โฟลเดอร์ | ตอนในคู่มือ | คำถามที่ทดลองตอบ |
|---|---:|---|---|---|
| **1** | 40 นาที | [`001_LAB_Dockerfile_First_Image`](./001_LAB_Dockerfile_First_Image/readme.md) | 2, 3, 4 | Dockerfile 8 บรรทัดกลายเป็นเว็บที่ตอบ HTTP 200 ได้อย่างไร และ `.dockerignore` กัน secret หลุดเข้า image ได้จริงไหม |
| **2** | 35 นาที | [`002_LAB_Layer_Cache_Build_Options`](./002_LAB_Layer_Cache_Build_Options/readme.md) | 5, 4.1 | สลับแค่ 2 บรรทัดทำให้ build เร็วขึ้นกี่เท่า และ `CACHED` หายไปตอนไหน |
| **3** | 35 นาที | [`003_LAB_RUN_CMD_ENTRYPOINT`](./003_LAB_RUN_CMD_ENTRYPOINT/readme.md) | 6 | พิมพ์คำสั่งต่อท้ายชื่อ image แล้วมันไปแทนที่หรือไปต่อท้ายอะไร และทำไม container บางตัวหยุดช้า 10 วินาที |
| **4** | 35 นาที | [`004_LAB_ENV_ARG_Config`](./004_LAB_ENV_ARG_Config/readme.md) | 7 | image ตัวเดียวเปลี่ยนเป็น dev/staging/production ได้โดยไม่ build ใหม่อย่างไร และ secret รั่วออกทาง `docker history` ได้จริงไหม |
| **5** | 45 นาที | [`005_LAB_Registry_Tag_Push_Pull`](./005_LAB_Registry_Tag_Push_Pull/readme.md) | 8 | push ทับ tag `1.0` ด้วย image คนละตัวแล้วเกิดอะไรขึ้น และ digest ช่วยอะไร |
| **6** | 35 นาที | [`006_LAB_Network_DNS`](./006_LAB_Network_DNS/readme.md) | 9 | ทำไม container บน default bridge เรียกกันด้วยชื่อไม่ได้ และต่อ network เพิ่มระหว่างที่รันอยู่ได้อย่างไร |
| **7** | 70 นาที | [`007_LAB_Compose_Multistage_Capstone`](./007_LAB_Compose_Multistage_Capstone/readme.md) | 10, 11, 12 | 4 service (web · api · redis · postgres) ขึ้นพร้อมกันด้วยไฟล์เดียวอย่างไร และ `down -v` ทำข้อมูลหายจริงไหม |

แต่ละแล็บมีครบ: ภาพรวม · Terminal Map · คำสั่งพร้อม 📝 คำอธิบายทุก option · ✅ Expected output จากการรันจริง ·
ทดลองเพิ่มเติม (มี "ทำให้พัง" อย่างน้อย 1 อัน) · ตารางแก้ปัญหาที่พบบ่อย · Cleanup · สรุปคำสั่ง · เช็กลิสต์ก่อนจบ

## เตรียมเครื่องเรียน

ทุกแล็บรันในเครื่องเรียนแบบ **Docker-in-Docker** โดย **แต่ละแล็บมี container และพอร์ตของตัวเอง**
จึงเปิดค้างพร้อมกันได้โดยไม่ชนกัน (คำสั่งเต็มอยู่ในข้อ 0 ของแต่ละแล็บ) :

| LAB | container | SSH | พอร์ตอื่น |
|---|---|---:|---|
| 1 | `devtools-df-lab1` | 2231 | 8181 (เว็บ) |
| 2 | `devtools-df-lab2` | 2232 | 8182 (เว็บ) |
| 3 | `devtools-df-lab3` | 2233 | — |
| 4 | `devtools-df-lab4` | 2234 | 8184 (เว็บ) |
| 5 | `devtools-df-lab5` | 2235 | 5035 (registry) · 8185 (เว็บ) |
| 6 | `devtools-df-lab6` | 2236 | 8186 (เว็บ) |
| 7 | `devtools-df-lab7` | 2237 | 8187 (เว็บ) · 8087 (API) |

ตัวอย่างของ LAB 1 (แล็บอื่นเปลี่ยนชื่อและพอร์ตตามตาราง) :

```bash
docker rm -f devtools-df-lab1 2>/dev/null
docker run -dit --name devtools-df-lab1 --privileged \
  -p 2231:22 -p 8181:8181 tuchsanai/devtools:2569_1
ssh root@localhost -p 2231        # password : passwd
```

> `--privileged` ใช้เฉพาะ **disposable classroom container** นี้เพื่อรัน Docker ซ้อนข้างใน
> ไม่ใช่ค่าที่ควรใช้กับ production workload

จากนั้นใช้ VS Code **Remote-SSH** ต่อไปที่ `root@localhost:<พอร์ต SSH ของแล็บ>` แล้วทำแล็บทั้งหมดข้างใน
และ clone โค้ดแล็บครั้งเดียวใช้ได้ทุกแล็บ :

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide
```

## ตรวจงานอัตโนมัติ

- **ในแต่ละแล็บ** — `bash verify.sh` (รันในเครื่องเรียน ตามจุดที่ README ระบุ)
  ผ่านครบทุกข้อจะพิมพ์ `ALL CHECKS PASSED` และคืน exit code 0
- **ตรวจตัวเอกสารทั้งชุด** (รันบนเครื่องไหนก็ได้ ไม่ต้องเปิด Docker) :

  ```bash
  python3 scripts/check_labs.py
  ```

  เป็น **static check** : ตรวจหัวข้อบังคับของทุก README · ชื่อ container/พอร์ตต้องไม่ชนข้ามแล็บ ·
  ไม่มี token/อีเมล/ชื่อบัญชีจริงหลุด · ห้าม `:latest` ลอย ๆ ในคำสั่งสอน · ห้าม `docker-compose` แบบขีดกลาง ·
  ลิงก์รูปและไฟล์ต้องมีอยู่จริง · หน้าเว็บของแล็บต้อง self-contained (ไม่โหลด asset จากภายนอก)

## ข้อควรรู้เรื่องเวอร์ชัน

เอกสารชุดนี้ทดสอบบน **Docker 29** ซึ่งเปลี่ยนพฤติกรรมบางอย่างไปจากรุ่นก่อน และแล็บเขียนตาม**ของจริงที่รันได้**
พร้อมหมายเหตุเทียบรุ่นเก่าไว้ในจุดที่ต่างกัน:

- `docker images` เปลี่ยนคอลัมน์เป็น `IMAGE / ID / DISK USAGE / CONTENT SIZE / EXTRA` (LAB 5)
- build ทับ tag เดิม **ไม่เหลือ image `<none>`** อีกแล้ว — dangling image เกิดเมื่อ build โดยไม่ใส่ `-t` (LAB 2)
- BuildKit **ไม่เตือน** `one or more build-args were not consumed` แล้ว แต่เตือน `SecretsUsedInArgOrEnv` แทน (LAB 4)
- BuildKit ส่งเข้า build context เฉพาะไฟล์ที่ `COPY` ต้องใช้ ผลของ `.dockerignore` จึงเห็นชัดเมื่อใช้ `COPY . .` (LAB 1)

## ขอบเขตของสิ่งที่แล็บพิสูจน์

- registry ในแล็บเป็น **HTTP บน localhost** เพื่อการเรียนเท่านั้น — ของจริงต้องมี TLS, authentication และการกำหนดสิทธิ์
- บัญชี/รหัสผ่านทั้งหมดในเอกสารเป็น **ค่าสำหรับแล็บ** และใช้ placeholder (`<DOCKER_USER>`, `<DOCKER_TOKEN>`) ทุกที่ที่เป็นของจริง
- `healthcheck` + `depends_on` ช่วยเรื่องลำดับการเริ่ม แต่ **โค้ดแอปยังต้อง retry เอง** เพราะ service ล้มหลังเริ่มแล้วได้
- named volume พิสูจน์การอยู่รอดข้ามการสร้าง container ใหม่ แต่ไม่ได้พิสูจน์ความทนทานต่อ disk/node failure
- แล็บสอน `docker compose` สำหรับเครื่องเดียว — งานหลายเครื่องต้องใช้ orchestrator เช่น Kubernetes

## เก็บกวาดหลังเลิกเรียน

แต่ละแล็บมีขั้นตอน Cleanup ของตัวเองอยู่ท้าย README (ลบทรัพยากรของแล็บ แล้วลบเครื่องเรียนของแล็บนั้น)
ถ้าต้องการล้างทุกแล็บพร้อมกันจากเครื่องของผู้เรียน :

```bash
docker rm -f $(docker ps -aq --filter "name=^devtools-df-") 2>/dev/null
docker ps -a --filter "name=^devtools-"        # ต้องเหลือแค่หัวตาราง
```

## ของเดิมในโฟลเดอร์นี้

- [`01_RabbitMQ/`](./01_RabbitMQ/readme.md) — ชุดแล็บ Message Queue (คนละเรื่อง ใช้เป็นต้นแบบรูปแบบเอกสารของชุดนี้)
- [`backup/`](./backup/) — แล็บชุดก่อนหน้าและไฟล์ต้นฉบับเก่า เก็บไว้อ้างอิงเท่านั้น
