# Week 9 — Docker &amp; Docker Compose

Software Development Tools and Environments

สัปดาห์ที่แล้วเราสร้าง container ขึ้นมาได้ — **สัปดาห์นี้เราจะบังคับมัน สอบสวนมัน ตั้งค่ามันจากข้างนอก
และประกอบมันเป็นระบบ** เนื้อหาเรียบเรียงใหม่จาก `02_Docker.pdf` และแล็บเดิมของชุดวิชานี้

---

## สไลด์

เปิดไฟล์ [`Docker_Week09_Slides.html`](./Docker_Week09_Slides.html) ในเบราว์เซอร์
(ไฟล์เดียวจบ · ไม่ต้องต่อเน็ต · 59 แผ่น)

| ปุ่ม | ทำอะไร |
|---|---|
| `←` `→` `Space` | เลื่อนสไลด์ |
| `O` | ดูสไลด์ทั้งหมดแล้วคลิกกระโดดไป |
| `F` | เต็มจอ |
| `?` | ดูปุ่มลัดทั้งหมด |
| `Ctrl+P` | บันทึกเป็น PDF |

> **ผลการรันทุกบรรทัดในสไลด์ รันจริง** บนเครื่องเรียน `tuchsanai/devtools:2569_1`
> ต้นฉบับของ output อยู่ในไฟล์ `evidence/transcript.md` ของแต่ละแล็บ

## เครื่องสำหรับทำแล็บ

ทำบนเครื่องเราเอง ผ่าน VS Code — **ไม่ใช้ cloud** · แต่ละแล็บใช้ชื่อและ port ของตัวเอง ไม่ชนกัน

```bash
docker rm -f devtools-lab001 2>/dev/null
docker run -dit --name devtools-lab001 --privileged -p 2222:22 -p 18081:8080 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

> 📝 `--privileged` จำเป็นเพราะเราจะรัน Docker **ซ้อนอยู่ข้างในกล่องเรียน** (Docker-in-Docker) ·
> `-p 2222:22` เปิดทาง SSH · `-p 18081:8080` เปิดทางให้หน้าเว็บของแล็บโผล่ออกมาที่เบราว์เซอร์ของเรา

ใน VS Code ใช้ **Remote-SSH** ต่อไปที่ `root@localhost:2222` แล้วทำแล็บข้างใน
(จะเปิดหน้าเว็บของแล็บ ให้ forward port ที่แท็บ **PORTS** ของ VS Code)

## แล็บทั้ง 5

| แล็บ | โฟลเดอร์ | เรื่องหลัก | SSH | เว็บ |
|---|---|---|---|---|
| **LAB 1** | [`001_LAB_Container_Control_Room`](./001_LAB_Container_Control_Room) | วงจรชีวิต · `ps` · `logs` · `exec` · `inspect` · `stats` · เก็บกวาดอย่างปลอดภัย | 2222 | 18081 |
| **LAB 2** | [`002_LAB_Env_Color_Factory`](./002_LAB_Env_Color_Factory) | Environment variables — image เดียว หลายบุคลิก · ลำดับความสำคัญ · secret ที่รั่ว | 2223 | 18021–18023 |
| **LAB 3** | [`003_LAB_Image_Diet`](./003_LAB_Image_Diet) | layer · build cache · `.dockerignore` · multi-stage · non-root | 2224 | 18031 |
| **LAB 4** | [`004_LAB_Vision_API_Compose`](./004_LAB_Vision_API_Compose) | สอง service ด้วย Compose — FastAPI + OpenCV คู่กับหน้าเว็บอัปโหลด | 2225 | 18041–18042 |
| **LAB 5** | [`005_LAB_Ops_Clinic`](./005_LAB_Ops_Clinic) | `HEALTHCHECK` · restart policy · resource limits · แผนที่วินิจฉัย | 2226 | 18051 |

**เลขโฟลเดอร์ตรงกับเลขแล็บในสไลด์** — ทำเรียงตั้งแต่ 1 ถึง 5 เพราะแต่ละแล็บใช้ของจากแล็บก่อนหน้า

## Clone โค้ดแล็บ

```bash
mkdir -p ~/labwork && cd ~/labwork
git clone https://github.com/Tuchsanai/DevTools.git
cd DevTools/03_Docker/02_Docker
```

## อ่านเอกสารแล็บอย่างไร

ทุกแล็บใช้รูปแบบเดียวกัน :

| สัญลักษณ์ | ความหมาย |
|---|---|
| ` ```bash ` | คำสั่งที่ต้อง **พิมพ์เอง** ในเครื่องเรียน |
| 📝 **คำอธิบาย** | คำสั่งนั้นทำอะไร แต่ละ flag แปลว่าอะไร และให้สังเกตอะไร |
| ✅ **Expected output** | ผลลัพธ์ที่ควรได้ **ถ้าทำถูก** — ถ้าได้ไม่ตรง แปลว่าพลาดบางขั้น ให้ย้อนกลับไปดู |

> **ตัวเลขที่ไม่ต้องตรงกันก็ได้** — CONTAINER ID, IMAGE ID, digest `sha256:…`, วันเวลา, เวลาที่ใช้ build
> และขนาดไฟล์ ของแต่ละคนจะไม่เหมือนในเอกสาร ให้ดูที่ **รูปแบบและสถานะ** (เช่น `Up`, `Exited (0)`,
> `CACHED`, `healthy`) เป็นหลัก

## กติกาการใช้ทรัพยากร

- ทำ**ทีละแล็บ** จะง่ายที่สุด · ถ้ารันพร้อมกันต้องไม่เกิน 7 container และห้ามใช้ port ซ้ำ
- เก็บกวาดด้วยชื่อหรือ label ของแล็บนั้นเท่านั้น **ห้าม**ใช้คำสั่งลบทั้งเครื่องบนเครื่องที่มีงานคนอื่นอยู่
- จบทุกแล็บให้ตรวจว่าไม่มีอะไรค้าง :

```bash
docker ps -a --filter "name=^devtools-"
```

## Credential safety

**ไม่มี token, รหัสผ่าน หรืออีเมลจริงฝังอยู่ในไฟล์ใดเลย** — ตัวอย่างที่ต้องใช้บัญชีจะใช้ placeholder
เช่น `<dockerhub-username>`, `<email@example.com>` · ค่าที่ดูเหมือนรหัสผ่านในแล็บ 2
(`not-a-real-password-1234`) เป็นค่าสมมติที่ใช้สาธิตว่า `ARG`/`ENV` เก็บความลับไม่ได้

> ข้อยกเว้นเดียวคือ **URL ของรีโพวิชานี้** ในคำสั่ง `git clone` ซึ่งต้องเป็นของจริงนักเรียนถึงจะ clone ได้
> (เป็น public repo ไม่ใช่ความลับ และใช้แบบเดียวกับสัปดาห์ที่ 8) — ถ้าต้องการให้เปลี่ยนเป็น placeholder
> ทั้งหมด แก้ได้ที่ `README.md` และ `README.md` ของแล็บทั้ง 5

---

## ไฟล์ประกอบ

| ที่อยู่ | คืออะไร |
|---|---|
| `slides_assets/*.svg` · `*.excalidraw` | ไดอะแกรม 12 รูปในสไลด์ (วาดด้วย Excalidraw — แก้ไขได้จากไฟล์ `.excalidraw`) |
| `tools/slides_body.html` | เนื้อสไลด์ (แก้ที่นี่ ไม่ใช่ที่ไฟล์ผลลัพธ์) |
| `tools/deck_template.html` | โครง CSS + JS ของสไลด์ |
| `tools/lab_outputs.py` | ผลการรันจริงที่ฝังลงสไลด์ คัดลอกมาจาก `evidence/transcript.md` |
| `tools/build_deck.py` | ประกอบทุกอย่างเป็น `Docker_Week09_Slides.html` ไฟล์เดียว |
| `tools/check_slides.py` | ตรวจว่าไม่มีเนื้อหาล้นกรอบ 1280×720 สักแผ่น |
| `Lab1/` … `Lab4/` | เอกสารและโค้ดชุดเดิมของสัปดาห์นี้ เก็บไว้อ้างอิง — เนื้อหาถูกเรียบเรียงใหม่ไปอยู่ใน `001_`–`005_` แล้ว |

สร้างสไลด์ใหม่หลังแก้เนื้อหา :

```bash
python3 tools/build_deck.py && /opt/venv/bin/python tools/check_slides.py
```

---

Happy Learning!
