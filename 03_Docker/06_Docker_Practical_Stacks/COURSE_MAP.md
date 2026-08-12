# Course Map และหลักฐานการประเมิน

| Outcome | เนื้อหา | Demo/LAB | หลักฐานที่ตรวจได้ |
|---|---|---|---|
| E1 | exec/logs/inspect/stats/cp | LAB 1 | log มี GET 200, HTML marker, inspect fields, stats snapshot |
| E2 | runtime configuration | LAB 2 | image ID เดียว แต่ 3 container แสดง 3 สี |
| E3 | network DNS/isolation | LAB 3 | localhost fail, same-network DNS pass, isolated network fail |
| E4 | named volume/restart | LAB 3 | row อยู่หลัง recreate; restart count เพิ่มหลัง crash |
| M1 | CMD/ENTRYPOINT | LAB 4 | ตาราง 7 run cases ตรงกับ inspect config |
| M2 | ARG/ENV/EXPOSE/health | LAB 5 | image config และ `healthy` จาก endpoint จริง |
| M3 | `.dockerignore`/multi-stage | LAB 5 | build context/runtime image มีเฉพาะสิ่งจำเป็น |
| M4 | registry lifecycle | LAB 5 | version tag, digest, pull-back run |
| M5 | Compose/readiness | LAB 6 | db healthy ก่อน client, DNS `db`, down/down-v ต่างกัน |
| H1 | REST/JSON/status | LAB 7–9 | GET 200, POST 201, invalid request 4xx |
| H2 | two-container stack | LAB 7 | manual commands เทียบ Compose และ Streamlit result |
| H3 | 3-tier/security | LAB 8 | publish เฉพาะ frontend, DB private, reverse proxy `/api` |
| H4 | persistence/debug | LAB 8 | down/up เก็บข้อมูล, down-v reset, debug drills |
| H5 | independent synthesis | LAB 9 | clean-clone acceptance test + rubric 100 คะแนน |

## ลำดับเวลาแนะนำ

| ครั้ง | หัวข้อ | เวลา |
|---|---|---:|
| 1 | Container toolbox + LAB 1 | 2.5 ชม. |
| 2 | Environment variables + LAB 2 | 2.5 ชม. |
| 3 | Network, volume, restart + LAB 3 | 3 ชม. |
| 4 | Advanced Dockerfile + LAB 4 | 3 ชม. |
| 5 | Build optimization, Registry + LAB 5 | 3 ชม. |
| 6 | Compose + LAB 6 | 3 ชม. |
| 7 | REST, FastAPI/OpenCV + Streamlit + LAB 7 | 3 ชม. |
| 8 | 3-tier Todo + LAB 8 | 4 ชม. |
| 9 | LAB 9 รายบุคคลและสอบอธิบาย | 3–4 ชม. |

## กติกาหลักฐาน

- Screenshot เป็นหลักฐานประกอบ ไม่แทน acceptance test
- ผู้ตรวจต้องรันจากสภาพ clean ได้
- output ที่เป็น dynamic ให้ตรวจ pattern ไม่ตรวจเลข ID ตายตัว
- deliberate failure ต้องจบด้วยการอธิบาย fault domain และวิธีคืนสภาพ
- ทุก LAB ต้องมีหลักฐาน cleanup ทั้ง inner resources และ outer `devtools-*`

