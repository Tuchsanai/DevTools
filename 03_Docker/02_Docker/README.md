# Docker & Docker Compose — Practical Learning Journey

สื่อชุดนี้เรียบเรียงใหม่จาก `02_Docker.pdf` และ LAB เดิมในชุด DevTools โดยเน้นให้ผู้เรียนตั้งสมมติฐาน รันจริง และใช้หลักฐานอธิบายผล

| ลำดับ | LAB | แนวคิดหลัก | SSH | Web |
|---|---|---|---:|---:|
| 001 | [Container Detective](001_LAB_Container_Detective/README.md) | lifecycle, port, exec, inspect, logs | 2222 | 18081 |
| 002 | [Image Factory](002_LAB_Image_Factory/README.md) | Dockerfile, cache, ARG/ENV, non-root, registry | 2223 | 18082 |
| 003 | [Volume Time Machine](003_LAB_Volume_Time_Machine/README.md) | writable layer, bind, volume, persistence | 2224 | 18083 |
| 004 | [Compose Service Radar](004_LAB_Compose_Service_Radar/README.md) | Compose, DNS, networks, health gates, Redis | 2225 | 18084 |
| 005 | [Chaos Clinic](005_LAB_Chaos_Clinic/README.md) | health, logs, restart, limits, hardening | 2226 | 18085 |

เปิดสไลด์หลักจาก `Docker_Practical_Journey.html` (16:9, offline, ใช้ปุ่ม ←/→, `O` overview, `F` fullscreen)

## กติกา resource

- รัน outer LAB ทีละตัวจะง่ายที่สุด; หากรันพร้อมกันต้องไม่เกิน 7 container และห้ามใช้ port ซ้ำ
- cleanup ด้วยชื่อ/project ของ LAB เท่านั้น ไม่ใช้คำสั่งลบ container/image/volume ทั้งเครื่อง
- หลังจบให้ตรวจ `docker ps -a --filter "name=^devtools-"`

## Credential safety

ตัวอย่างเอกสารใช้ `<dockerhub-username>`, `<github-username>`, `<email@example.com>` และอ่าน token จาก prompt เท่านั้น ไม่มีชื่อ อีเมล หรือ token จริงฝังอยู่ในไฟล์
