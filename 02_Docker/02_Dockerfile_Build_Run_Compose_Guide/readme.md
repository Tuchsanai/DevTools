# Dockerfile → Build → Run → Compose

ชุดแล็บ **7 แล็บ** ที่เรียบเรียงจากคู่มือ [`Dockerfile_Build_Run_Compose_Guide.html`](./Dockerfile_Build_Run_Compose_Guide.html)
(12 ตอน) โดยแปลงทุกตอนให้เป็น **การทดลองที่รันได้จริง**

ทุกคำสั่งและทุกบล็อก `✅ Expected output` ใน README ของแต่ละแล็บ **มาจากการรันจริง**
ในเครื่องเรียน `tuchsanai/devtools:2569_1` (Docker 29.6.2 · Ubuntu 24.04 · Python 3.12) เมื่อ 14 ส.ค. 2026
ตัวเลขและข้อความทุกบล็อกจึงเป็นของที่เกิดขึ้นจริง ไม่ใช่ตัวอย่างสมมติ — และตรวจซ้ำได้เองด้วย `verify.sh` ของแต่ละแล็บ

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
| **5** | 35 นาที | [`005_LAB_Registry_Tag_Push_Pull`](./005_LAB_Registry_Tag_Push_Pull/readme.md) | 8 | push ทับ tag `1.0` ด้วย image คนละตัวแล้วเกิดอะไรขึ้น และ digest ช่วยอะไร |
| **6** | 35 นาที | [`006_LAB_Network_DNS`](./006_LAB_Network_DNS/readme.md) | 9 | ทำไม container บน default bridge เรียกกันด้วยชื่อไม่ได้ และต่อ network เพิ่มระหว่างที่รันอยู่ได้อย่างไร |
| **7** | 70 นาที | [`007_LAB_Compose_Multistage_Capstone`](./007_LAB_Compose_Multistage_Capstone/readme.md) | 10, 11, 12 | 4 service (web · api · redis · postgres) ขึ้นพร้อมกันด้วยไฟล์เดียวอย่างไร และ `down -v` ทำข้อมูลหายจริงไหม |

แต่ละแล็บมีครบ: ภาพรวม · Terminal Map · **ทฤษฎีก่อนลงมือ** (ภาพจำหลัก · กลไกจริง · กฎที่ต้องจำ · สิ่งที่มักเข้าใจผิด · ทายผลก่อนทดลอง) ·
คำสั่งพร้อม 📝 คำอธิบายทุก option · ✅ Expected output จากการรันจริง · ทดลองเพิ่มเติม (มี "ทำให้พัง" อย่างน้อย 1 อัน) ·
ตารางแก้ปัญหาที่พบบ่อย · Cleanup · สรุปคำสั่ง · เช็กลิสต์ก่อนจบ

## หัวข้อนี้เรียนที่แล็บไหน — ดัชนีกันเรียนซ้ำ

ทุกหัวข้อมี **"แล็บเจ้าของ" เพียงแล็บเดียว** ที่ลงมือทดลองเต็มรูปแบบ · แล็บอื่นจะ **แวะใช้แต่ไม่สอนซ้ำ**
และมีลิงก์บอกว่าให้ไปอ่านที่ไหน — ถ้ารู้สึกว่า "เคยทำมาแล้ว" ให้เทียบกับตารางนี้ก่อน จะเห็นว่าแต่ละครั้งพิสูจน์คนละประเด็น

| หัวข้อ | 🏠 เรียนเต็มที่ | แวะใช้ (ไม่สอนซ้ำ) |
|---|---|---|
| Dockerfile / image / container ต่างกันอย่างไร | **LAB 1** ข้อ 2–3 | ทุกแล็บใช้ต่อ |
| `docker build` + build context (จุด `.`) | **LAB 1** ข้อ 4 | ทุกแล็บใช้ต่อ |
| `EXPOSE` ไม่ได้เปิดพอร์ต · `-p` ต่างหากที่เปิด | **LAB 1** ข้อ 9 | LAB 6 ข้อ 8 (ทำไม backend ไม่ต้อง `-p`) |
| ลำดับตรวจปัญหา `image ls → ps -a → logs → exec` | **LAB 1** ข้อ 7 | LAB 7 ข้อ 13 (ฉบับ `docker compose`) |
| `.dockerignore` : ลดขนาด context + กัน secret หลุด | **LAB 1** ข้อ 6 | LAB 4 ข้อ 11 (ยืนยันกับ `.env.*`) · LAB 7 ข้อ 14 (เทมเพลตที่ควรมี) |
| `.dockerignore` : กัน **cache แตก** โดยไม่จำเป็น | **LAB 2** ข้อ 8 | — |
| layer cache · ลำดับบรรทัดมีผลกับเวลา build | **LAB 2** ข้อ 3–4 | LAB 1 ข้อ 3 (เหตุผลที่ `COPY` แยกสองบรรทัด) |
| Options ของ build : `--no-cache` · `--pull` · `-t` หลายอัน | **LAB 2** ข้อ 5 | LAB 1 ข้อ 4 (ใช้แค่ `-t` · `-f` · `--progress=plain`) |
| `docker history` · dangling image · คืนพื้นที่ | **LAB 2** ข้อ 6–7 | LAB 1 ข้อ 10 (`system df` อ่านอย่างเดียว) · LAB 4 ข้อ 9 (history เพื่อดู secret) |
| `RUN` vs `CMD` vs `ENTRYPOINT` | **LAB 3** ข้อ 2–6 | LAB 1 ทดลอง ก. (ชิมลาง: แทน `CMD` ตอน run) |
| exec form vs shell form · PID 1 · SIGTERM | **LAB 3** ข้อ 7–8 | — |
| ลำดับชั้น `ENV` < `--env-file` < `-e` | **LAB 4** ข้อ 3–5 | LAB 1 ทดลอง ค. (ชิมลาง) · LAB 7 ข้อ 9 (ฉบับ Compose) |
| `ARG` vs `ENV` · `ARG` ก่อน `FROM` | **LAB 4** ข้อ 8, 10 | LAB 2 ข้อ 5.4 (รู้จักรูปแบบ) · LAB 5 ข้อ 9 (ใช้ `--build-arg` จริง) |
| ห้ามเก็บ secret ใน `ARG`/`ENV` | **LAB 4** ข้อ 9 | LAB 7 ข้อ 9 (รหัสผ่านอยู่ `.env.app`) |
| ชื่อเต็มของ image · tag ย้ายได้ · digest ไม่เปลี่ยน | **LAB 5** ข้อ 2, 9–10 | — |
| `Untagged` ต่างจาก `Deleted` | **LAB 5** ข้อ 11 | LAB 2 ข้อ 7 (มุมของ dangling image) |
| user-defined network · DNS ของชื่อ container | **LAB 6** ข้อ 4–5 | LAB 7 ข้อ 10 (ฉบับ Compose + `internal: true`) |
| `docker compose` · healthcheck · named volume · init script | **LAB 7** ข้อ 3–4, 8, 11–12 | — |
| multi-stage build | **LAB 7** ข้อ 7, 14 | LAB 2 ข้อ 5.4 (`--target`) · LAB 4 ข้อ 9 (เป็นทางแก้เรื่อง secret) |

## เวลาที่ใช้ — เส้นทางเต็ม vs เส้นทางเร่งรัด

ทุกแล็บแบ่งเป็น **แกนหลัก** (ข้อที่มีเลข) กับ **ทดลองเพิ่มเติม** (ท้ายไฟล์ · ส่วนใหญ่เป็นข้อ 💥 ทำให้พัง)

| เส้นทาง | ทำอะไร | เวลารวม |
|---|---:|---:|
| **เร่งรัด** | เฉพาะข้อที่มีเลขของทั้ง 7 แล็บ + `verify.sh` | ~3 ชั่วโมง 30 นาที |
| **เต็ม** | แกนหลัก + ทดลองเพิ่มเติมทุกข้อ | ~4 ชั่วโมง 45 นาที |

> เวลาข้างต้นไม่รวมการ pull base image ครั้งแรกของแต่ละเครื่อง · หัวข้อ 💥 **ทำให้พัง** อยู่ในเช็กลิสต์ท้ายแล็บ
> เพราะการอ่าน error ให้ออกคือทักษะที่ใช้จริงมากที่สุด — ถ้าเวลาจำกัดให้ตัดข้ออื่นก่อน

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

ทุกแล็บมี `verify.sh` ของตัวเอง — รัน **ในเครื่องเรียน** ตามจุดที่ README ของแล็บนั้นระบุ :

```bash
cd ~/labwork/DevTools/02_Docker/02_Dockerfile_Build_Run_Compose_Guide/<โฟลเดอร์แล็บ>
bash verify.sh ; echo "exit code = $?"
```

ผ่านครบทุกข้อจะพิมพ์ `ALL CHECKS PASSED` และคืน exit code `0` · สคริปต์ **สร้างและลบของทดสอบของตัวเองเท่านั้น**
ไม่แตะ container/image ที่ผู้เรียนสร้างระหว่างทำแล็บ (ยกเว้นที่ README ของแล็บนั้นเตือนไว้ว่าจะเคลียร์พอร์ตให้)

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

- [`backup/`](./backup/) — แล็บชุดก่อนหน้าและไฟล์ต้นฉบับเก่า เก็บไว้อ้างอิงเท่านั้น
- รูปแบบเอกสารของชุดนี้ถอดแบบมาจากชุดแล็บ RabbitMQ ซึ่งอยู่ที่
  [`03_Application_Docker/02_Message_Brokers/01_RabbitMQ/`](../../03_Application_Docker/02_Message_Brokers/01_RabbitMQ/readme.md)
