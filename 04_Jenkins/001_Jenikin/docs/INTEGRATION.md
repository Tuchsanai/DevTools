# U8 — Integration Report (Phase 3)

วันที่ทดสอบ: 2026-08-20 UTC  
สถานะรวม: **FAIL** — full chain, checkpoints, capstone, checks และ cleanup ผ่าน แต่พบ 2 FINDING ที่ต้องแก้นอก scope U8

หลักฐานคำสั่งและ exit code ฉบับเต็ม: [`logs/U8.log`](../logs/U8.log)

## ขอบเขตและสภาพทดสอบ

- outer container: `devtools-jk8`
- SSH `2238`; Jenkins `18080→8080`; Gitea `18300→3000`; webapp `18800→8000`
- UI base URLs: `http://host.docker.internal:18080`, `:18300`, `:18800`
- credential Docker Hub รับจาก runtime environment เท่านั้น; ไม่บันทึกค่าจริงลงไฟล์/log
- เริ่มจาก outer container ใหม่และทำ LAB 1→6 ตาม README ต่อเนื่องในสถานะเดียว
- helper ที่มีปลายทาง screenshot ตายตัวรันผ่าน `tools/ui/int_u8_redirect.py` เพื่อเก็บภาพใน `logs/u8_evidence/` โดยไม่แก้ต้นฉบับหรือ assets

## ผล full-chain และเวลาจริง

เวลานี้เป็นเวลาของ automation บนเครื่อง integration ไม่ใช่เวลาของผู้เรียนจริง

| LAB | timebox | เวลาจริง | check.sh | ผลการทดลอง |
|---:|---:|---:|---:|---|
| 1 | 40 นาที | 3:40 นาที | 0 | PASS ทั้ง 8 การทดลอง |
| 2 | 30 นาที | 0:40 นาที | 0 | PASS ทั้ง 7 การทดลอง/build #1–#7 |
| 3 | 45 นาที | 1:55 นาที | 0 | Pipeline/Hub/check PASS; มี U3-01 |
| 4 | 40 นาที | 2:36 นาที | 0 | SCM/Poll build PASS |
| 5 | 30 นาที | 1:03 นาที | 0 | plugin/webhook/payload PASS |
| 6 | 45 นาที | 1:55 นาที | 0 | capstone v1→v2 PASS; มี VER-01 ที่ preflight |

หลักฐานราย LAB อยู่ที่ [`U8.log:L20-L97`](../logs/U8.log#L20-L97)

## Restart checkpoints

| จุดตรวจ | services หลัง restart | state ที่เทียบ | check ล่าสุด | ผล |
|---|---|---|---:|---|
| หลัง LAB 3 | Jenkins กลับเอง | job/build map ก่อน–หลังเหมือนกัน; setup marker อยู่ | LAB 3 = 0 | PASS |
| หลัง LAB 5 | Jenkins + Gitea กลับเอง | job/build map และ `hello-ci` HEAD เหมือนกัน; setup markerอยู่ | LAB 5 = 0 | PASS |

ทั้งสองรอบใช้ `docker restart devtools-jk8`, รอ inner dockerd, ตรวจ `docker ps -a` และไม่ทำ wizard/setup ซ้ำ หลักฐาน: [`U8.log:L49-L54`](../logs/U8.log#L49-L54), [`U8.log:L78-L83`](../logs/U8.log#L78-L83)

## Capstone end-to-end

| หลักฐาน | v1 | v2 |
|---|---|---|
| commit/push | `Trigger v1 deployment` | `Release dashboard v2 green` |
| Jenkins build | #1 SUCCESS | #2 SUCCESS |
| webapp | 1.0.0 / blue / build 1 | 2.0.0 / green / build 2 |
| browser | capture ก่อน | หน้าเดิม auto-refresh แล้ว capture หลัง |
| Hub | build tag 1 + latest | build tag 2 + latest |

- build #2: pytest 3 เคสผ่านก่อน push; Build-Test-Push, Deploy, Verify สำเร็จ
- Jenkins console, Hub tag `2` และ `latest` ชี้ digest เดียวกัน `sha256:87cb5278…6dd7b`
- Hub `last_updated` ใหม่กว่าเวลาเริ่ม build
- acceptance `006_LAB_CICD_Capstone/check.sh` exit 0 และผ่าน 15 assertions
- ภาพ: [`lab6_app_v1.png`](../logs/u8_evidence/lab6_app_v1.png), [`lab6_app_v2.png`](../logs/u8_evidence/lab6_app_v2.png), [`lab6_pipeline_full.png`](../logs/u8_evidence/lab6_pipeline_full.png), [`lab6_hub_tags.png`](../logs/u8_evidence/lab6_hub_tags.png)
- หลักฐาน log: [`U8.log:L85-L97`](../logs/U8.log#L85-L97)

## Cross-consistency

รัน `python3 tools/ui/int_consistency.py` exit 0: `CONSISTENCY SUMMARY: PASS (12/12)`

| รายการ | ผล | หมายเหตุ |
|---|---|---|
| container/network/volume canonical ใน README | PASS | `devtools-jenkins`, `jenkins`, `gitea`, `webapp`, `cicd-net`, `jenkins_home`, `gitea_data` |
| credentials/tokens | PASS | fixtures, `dockerhub`, `cicd2569-hello`, `cicd2569-webapp`, placeholders ตรง PLAN §4 |
| URL map | PASS | browser localhost, Jenkins→Gitea, Gitea→Jenkins, Jenkins→webapp ตรงบทบาท |
| code block drift | PASS | ไม่พบ agent-only port/host หรือ local registry ที่เลิกใช้แล้ว |
| relative links ใน README | PASS | 27 ลิงก์ชี้ไฟล์ที่มีจริง |
| deck LAB/folder | PASS | เปิด deck ด้วย headless Chromium, ดึง DOM text และพบ LAB 1–6 พร้อมลิงก์โฟลเดอร์จริงครบ |
| deck ↔ STACK_RESOLVED versions | PASS | Jenkins 2.568.2, Gitea 1.27.2, Docker CLI 26.1.5, GWT 2.4.2 |
| secret-pattern scan ในไฟล์ U8 | PASS | count=0 |

หมายเหตุ: แถว deck ↔ STACK ผ่านเพราะสอง artifact ตรงกัน แต่ runtime จาก LAB 3 เป็น 29.7.2 จึงยังเกิด VER-01 แยกต่างหาก หลักฐาน cross-check: [`U8.log:L99-L106`](../logs/U8.log#L99-L106)

## Findings และหน่วยที่ตีกลับ

| ID | ระดับ | ตีกลับ | เอกสารบอก | สิ่งที่เกิดจริง | หลักฐาน |
|---|---|---|---|---|---|
| U3-01 | minor | U3 | `lab3_credential.py` ต้องแสดง assertion แล้ว PASS ในการรันสร้าง credential | การรันครั้งแรกสร้าง `dockerhub` สำเร็จ แต่ exit 1 ที่ assertion หน้า list; ตรวจ XML/HTML พบ credential แล้ว และ rerun เดิมจึง exit 0 | [`U8.log:L44`](../logs/U8.log#L44) |
| VER-01 | major | U0 + U3 + U6; U7 รอ canonical | LAB 6/STACK/deck ระบุ Docker CLI 26.1.5 ขณะที่ LAB 3 ระบุ 29.7.2 | build ตาม Dockerfile ของ LAB 3 ติดตั้ง latest และได้ 29.7.2; LAB 6 preflight จึงไม่ตรง “สิ่งที่ต้องเห็น” แม้ pipeline ผ่าน | [`U8.log:L41`](../logs/U8.log#L41), [`U8.log:L87`](../logs/U8.log#L87), [`U8.log:L105-L106`](../logs/U8.log#L105-L106) |

ข้อเสนอให้เจ้าของหน่วยตัดสิน VER-01: pin Docker CLI ให้ reproducible แล้วแก้ LAB 3/LAB 6/STACK/deck ให้เป็นค่าเดียว หรือประกาศ expected เป็นรูปแบบไม่ผูก patch version; U8 ไม่แก้ไฟล์เหล่านี้ตาม scope guard

## DoD U8 ตาม PLAN §8

| ข้อ | เกณฑ์ | ผล | หลักฐาน |
|---:|---|---|---|
| 1 | devtools ใหม่ ไล่ LAB 1→6 ตาม README และ UI helpers | FAIL | chain/check ผ่าน แต่ U3-01 และ VER-01 ทำให้มีสิ่งที่เห็นไม่ตรง |
| 2 | restart checkpoint ×2, services/history/repo อยู่ ไม่ทำ setup ซ้ำ | PASS | `U8.log:L49-L54`, `L78-L83` |
| 3 | capstone แก้โค้ด→push→auto build→เว็บเปลี่ยน→Hub tag→check 0 | PASS | `U8.log:L85-L97` + ภาพใน `logs/u8_evidence/` |
| 4 | cross-check README/deck/folder/URL/stack | PASS | consistency 12/12, `U8.log:L99-L106` |
| 5 | global devtools ว่างและไม่มี junk/tmp | PASS | `U8.log:L115-L122` |

## Cleanup

- ลบ `.ipynb_checkpoints` ทุกจุดใต้ชุดสอน; final count=0
- ลบ generated `__pycache__`; ไม่พบ `.pyc`, `.tmp` หรือ editor backup ใน U8 UI scope
- `docker rm -f devtools-jk8` exit 0
- `docker ps -a --filter name=^devtools-` ว่างทั้ง global
- หลักฐาน: [`U8.log:L115-L122`](../logs/U8.log#L115-L122)

## ความเสี่ยงและสิ่งที่ค้าง

- Docker CLI ไม่ pin ทำให้ README/stack/deck drift ได้เมื่อ repository upstream เปลี่ยน
- helper credential มี race/selector หลัง Create; ผู้เรียนอาจเห็น automation fail ทั้งที่ credential ถูกสร้างแล้ว
- เวลาทดสอบเป็น automation บน cache/network ณ รอบนี้ ไม่แทนเวลาผู้เรียนจริง
- ต้องให้ U0/U3/U6 ตัดสิน version contract และ U3 แก้ helper แล้ว rerun U8 เฉพาะ chain ที่ได้รับผลกระทบก่อนประกาศ PASS

## Final status (2026-08-20 — supersedes ผลรอบแรก)

สถานะรวมปัจจุบัน: **PASS** สำหรับ integration scope ของชุดสอน ผล FAIL และ findings ในรายงาน U8 ด้านบนเก็บไว้เป็น historical record และถูก supersede โดยสถานะส่วนนี้

- `U3-01` และ `VER-01` ปิดโดย U-FIX3 แล้ว หลักฐานอยู่ที่ [`logs/UFIX3.log`](../logs/UFIX3.log); Docker CLI canonical และ runtime ที่พิสูจน์ซ้ำคือ **29.7.2**
- gates รอบ U-FINAL จาก course root copy ที่รักษา input ปัจจุบันและแยก screenshot output ออกจากไฟล์ส่งมอบ: `deck_offline_test.py` exit **0**, `deck_consistency_test.py` exit **0**, `int_consistency.py` exit **0** และสรุป `PASS (12/12)`
- fresh `devtools-jkF` ทำ sparse clone, ตั้ง `COURSE_ROOT`, ผ่าน LAB 1 restart/readiness, replay LAB 4–5, LAB 6 v1→v2 และ acceptance checks; หลักฐานคำสั่ง/exit code อยู่ที่ [`logs/UFINAL.log`](../logs/UFINAL.log)
- inventory cleanup ที่ orchestrator จัดการก่อนรอบนี้และ U-FINAL ตรวจยืนยันตาม scope: course test volume **0**, U-FINAL container/volume filter **0**, generated cache/temporary junk ของ U-FINAL **0**; ignored backup/checkpoint ที่ระบบภายนอกหรือผู้ใช้สร้างภายหลังไม่อยู่ใน ship artifact และไม่ถูกลบข้าม scope
