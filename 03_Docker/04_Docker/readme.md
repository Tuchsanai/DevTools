# Week 11 — Docker ภาคสร้าง : Dockerfile → Registry → Network → Compose

สื่อการสอนชุดนี้เรียบเรียงใหม่จากสไลด์บรรยาย `04_Docker.pdf` โดยออกแบบแล็บใหม่ทั้งหมด
ทุกคำสั่งและผลลัพธ์ใน README ของแต่ละแล็บมาจาก**การรันจริง**ในเครื่องเรียน `tuchsanai/devtools:2569_1`

## สไลด์

- **[`new_Docker_Week11_Slides.html`](new_Docker_Week11_Slides.html)** — สไลด์ฉบับเรียบเรียงใหม่ 90 หน้า สำหรับนักศึกษาระดับง่าย–ปานกลาง (เปิดในเบราว์เซอร์ได้เลย ไฟล์เดียวจบ)
  - 1 สไลด์ = 1 แนวคิด (≤60 คำ) · ทุก section เรียงลำดับ ปัญหา → นิยาม → ไดอะแกรม → คำสั่งจริง → error → สรุป
  - มีสไลด์ **เช็คความเข้าใจ + เฉลย** 13 จุด (คลิกกล่องเฉลยเพื่อเปิดคำตอบ)
  - ปุ่ม `←`/`→` เปลี่ยนหน้า · `O` ดูภาพรวม · `F` เต็มจอ · `?` ปุ่มลัดทั้งหมด · `Ctrl+P` บันทึกเป็น PDF
  - หน้าจอ Docker Hub ทุกภาพเป็น **capture จริง** จาก hub.docker.com (ส.ค. 2026)
- [`Docker_Week11_Slides.html`](Docker_Week11_Slides.html) — สไลด์ฉบับ 53 หน้า (ต้นฉบับก่อนเรียบเรียงใหม่)
- ไฟล์ต้นฉบับภาพประกอบ (`.excalidraw` + `.svg`) อยู่ใน [`slides_assets/`](slides_assets/) — แก้ภาพแล้วรัน `python3 slides_assets/build_assets.py` เพื่อฝังกลับเข้าสไลด์ทั้งสองไฟล์ (สคริปต์ตรวจกติกาสไลด์: `slides_assets/check_rules.py`)

## แล็บทั้ง 5 (เรียงตามลำดับการสอน)

ทุกแล็บมี **`verify.sh`** — รันจากโฟลเดอร์แล็บตามจุดที่ README ระบุ ผ่านครบทุกข้อจะขึ้น `ALL CHECKS PASSED` (exit 0)

| LAB | โฟลเดอร์ | สิ่งที่ได้เรียน | เวลา |
|---|---|---|---|
| 1 | [`001_LAB_Dockerfile_First_Image`](001_LAB_Dockerfile_First_Image/README.md) | Dockerfile · `docker build` · layer/cache · ENV override · `.dockerignore` | ~20 นาที |
| 2 | [`002_LAB_CMD_vs_ENTRYPOINT`](002_LAB_CMD_vs_ENTRYPOINT/README.md) | `CMD` vs `ENTRYPOINT` ครบทุกกรณี — พิสูจน์ด้วย ASCII art | ~15 นาที |
| 3 | [`003_LAB_Docker_Hub_Registry`](003_LAB_Docker_Hub_Registry/README.md) | กติกาชื่อ image · Access Token · `tag`/`push`/`pull` · self-host registry | ~20 นาที |
| 4 | [`004_LAB_Docker_Network_DNS`](004_LAB_Docker_Network_DNS/README.md) | bridge/host/none · Embedded DNS · `network connect` — ภารกิจกู้ข้อความลับ 🕵️ | ~20 นาที |
| 5 | [`005_LAB_Docker_Compose_Voting`](005_LAB_Docker_Compose_Voting/README.md) | `docker compose` · healthcheck · `depends_on` · volume · compose watch | ~20 นาที |

ทุกแล็บเริ่มจากเครื่องเรียนเดียวกัน:

```bash
docker start devtools 2>/dev/null || \
  docker run -dit --name devtools --privileged -p 2222:22 tuchsanai/devtools:2569_1
ssh root@localhost -p 2222        # password : passwd
```

## หลักฐานการทดสอบ

- [`REPORT.md`](REPORT.md) — คะแนน C1–C8 ทุก iteration ของการเรียบเรียง + สรุปการทดสอบ
- [`test_logs/`](test_logs/) — log การรันจริงของทั้ง 5 แล็บ (คำสั่งครบทุกขั้น + ผล `verify.sh`)

## ล้างกระดานหลังเลิกเรียน (รันในเครื่องเรียน)

```bash
docker stop $(docker ps -a -q) 2>/dev/null || true
docker rm $(docker ps -a -q) 2>/dev/null || true
docker rmi -f $(docker images -q) 2>/dev/null || true
docker volume rm $(docker volume ls -q) 2>/dev/null || true
docker network prune -f
```

> ของเดิมก่อนเรียบเรียงใหม่ (แล็บชุดปี 2568 และแล็บชุดแรกของสัปดาห์นี้) ถูกย้ายไปเก็บที่ [`backup/`](backup/)
