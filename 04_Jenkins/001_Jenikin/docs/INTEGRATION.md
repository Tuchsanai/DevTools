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

## Phase 5 — GitHub migration handoff (2026-08-20)

ส่วนนี้ supersede ข้อมูล SCM/webhook ของรายงาน Phase 3 ด้านบน การทดสอบ Phase 5 ใช้ GitHub.com, relay แยกสองเส้นทาง และ API/runtime postcondition ตาม `docs/PLAN_P5_GITHUB.md`

### ทะเบียนภาพ Phase 5

คอลัมน์ “mask” ระบุการปกปิดก่อนเขียนไฟล์ final; `n/a` หมายถึง viewport ไม่มี account/channel identifier ที่ต้องปกปิด ภาพ mock เป็นสื่อสอนลำดับคลิกเท่านั้นและไม่ใช่ runtime evidence

| LAB | file | ชนิด | mask / สถานะ |
|---:|---|---|---|
| 4 | `slides_assets/lab4_s01_github_new_repo.png` | mock auth-only จาก `slides_assets/mock/github_new_repo_hello.png` | placeholder `<GITHUB_USER>`; pending real authenticated capture |
| 4 | `slides_assets/lab4_s02_github_empty_repo.png` | real GitHub public | owner → `<GITHUB_USER>` ก่อน save |
| 4 | `slides_assets/lab4_s03_github_repo_files.png` | real GitHub public | owner → `<GITHUB_USER>` ก่อน save |
| 4 | `slides_assets/lab4_s04_jenkins_new_item.png` | real Jenkins | n/a; private-match scan = 0 |
| 4 | `slides_assets/lab4_s05_jenkins_scm_config.png` | real Jenkins | repository URL → `<GITHUB_USER>` ก่อน save |
| 4 | `slides_assets/lab4_s06_manual_build_console.png` | real Jenkins | n/a; private-match scan = 0 |
| 4 | `slides_assets/lab4_s07_poll_scm_trigger.png` | real Jenkins | n/a; private-match scan = 0 |
| 4 | `slides_assets/lab4_s08_git_polling_log.png` | real Jenkins | owner/URL → `<GITHUB_USER>` ก่อน save |
| 4 | `slides_assets/lab4_s09_scm_build_cause.png` | real Jenkins | owner/URL → `<GITHUB_USER>` ก่อน save |
| 5 | `slides_assets/lab5_s01_available_plugin.png` | real Jenkins | n/a |
| 5 | `slides_assets/lab5_s02_plugin_download_restart.png` | real Jenkins | n/a |
| 5 | `slides_assets/lab5_s03_smee_channel.png` | real smee | channel URL/id → `<SMEE_HELLO_URL>` ก่อน save |
| 5 | `slides_assets/lab5_s04_gwt_parameters.png` | real Jenkins | n/a |
| 5 | `slides_assets/lab5_s04b_gwt_after.png` | real Jenkins | n/a |
| 5 | `slides_assets/lab5_s04c_gwt_token_cause.png` | real Jenkins | n/a |
| 5 | `slides_assets/lab5_s05_gwt_filter.png` | real Jenkins | n/a |
| 5 | `slides_assets/lab5_s06_github_add_webhook.png` | mock auth-only จาก `slides_assets/mock/github_add_webhook_hello.png` | placeholders `<GITHUB_USER>`/`<SMEE_HELLO_URL>`; pending real authenticated capture |
| 5 | `slides_assets/lab5_s07_smee_ping.png` | real smee | account → `<GITHUB_USER>`; channel ไม่อยู่ใน viewport |
| 5 | `slides_assets/lab5_s08_smee_push.png` | real smee | account → `<GITHUB_USER>`; channel ไม่อยู่ใน viewport |
| 5 | `slides_assets/lab5_s08a_smee_commit_files.png` | real smee | account → `<GITHUB_USER>` ก่อน save |
| 5 | `slides_assets/lab5_s08b_smee_head_commit.png` | real smee | account → `<GITHUB_USER>` ก่อน save |
| 5 | `slides_assets/lab5_s09_github_push_build.png` | real Jenkins | account → `<GITHUB_USER>` ก่อน save |
| 5 | `slides_assets/lab5_s10_checkout_sha.png` | real Jenkins | account → `<GITHUB_USER>` ก่อน save |
| 6 | `slides_assets/lab6_s01_github_new_repo.png` | mock auth-only จาก `slides_assets/mock/github_new_repo_webapp.png` | placeholder `<GITHUB_USER>`; pending real authenticated capture |
| 6 | `slides_assets/lab6_s02_github_repo_after_push.png` | real GitHub public | account → `<GITHUB_USER>` ก่อน save |
| 6 | `slides_assets/lab6_s03_smee_channel.png` | real smee | channel URL/id → `<SMEE_WEBAPP_URL>` ก่อน save |
| 6 | `slides_assets/lab6_s04a_gwt_parameters.png` | real Jenkins | n/a |
| 6 | `slides_assets/lab6_s04b_gwt_token_cause.png` | real Jenkins | n/a |
| 6 | `slides_assets/lab6_s04c_gwt_filter.png` | real Jenkins | n/a |
| 6 | `slides_assets/lab6_s05_job_scm.png` | real Jenkins | repository URL → `<GITHUB_USER>` ก่อน save |
| 6 | `slides_assets/lab6_s05b_job_script_path.png` | real Jenkins | n/a |
| 6 | `slides_assets/lab6_s06_github_add_webhook.png` | mock auth-only จาก `slides_assets/mock/github_add_webhook_webapp.png` | placeholders `<GITHUB_USER>`/`<SMEE_WEBAPP_URL>`; pending real authenticated capture |
| 6 | `slides_assets/lab6_s07_smee_ping.png` | real smee | sensitive fields ไม่อยู่ใน viewport |
| 6 | `slides_assets/lab6_s08_pipeline_graph.png` | real Jenkins | n/a |
| 6 | `slides_assets/lab6_s09_console_pytest.png` | real Jenkins | account → `<GITHUB_USER>` ก่อน save |
| 6 | `slides_assets/lab6_s09b_console_verify.png` | real Jenkins | n/a |
| 6 | `slides_assets/lab6_s10_dashboard_v1.png` | real webapp | n/a |
| 6 | `slides_assets/lab6_s11_dashboard_v2.png` | real webapp | n/a |
| 6 | `slides_assets/lab6_s12_hub_public_tags.png` | real Docker Hub public | account → `<DOCKER_USER>` ก่อน save |

ทะเบียนต้นทาง `docs/IMAGE_REGISTRY_P5.md` มี mock auth-only **4 ไฟล์** และถูกนำไปสร้างภาพ final 4 ไฟล์ตามตาราง ไม่ใช่ 3 ไฟล์ ดังนั้น handoff ที่ระบุ “mock 3 ภาพ” ยังต้อง reconcile กับ registry; ทั้ง 4 ภาพรอสลับเป็น real masked capture เมื่อมี authenticated GitHub session cookie ตาม D5v2 ระหว่างนี้ทุก caption ต้องระบุ “ภาพจำลอง — UI จริงอาจต่างเล็กน้อย” พร้อม GitHub Docs link และ API postcondition

### ทะเบียน asset SCM เดิมที่ลบ

`logs/U-P5-6.log` บันทึกการลบ explicit 11 ไฟล์ และ commit หลักฐาน `1f768f7` แสดงรายชื่อดังนี้:

| file ที่ลบ | เหตุผล |
|---|---|
| `slides_assets/lab6_s01_gitea_repo_form.png` | หน้าสร้าง repository ของ SCM เดิม |
| `slides_assets/lab6_s02_gitea_repo_after_push.png` | หน้า repository ของ SCM เดิม |
| `slides_assets/lab6_s03_job_scm.png` | ลำดับ/ชื่อภาพเดิม ถูกแทนด้วยภาพ Phase 5 |
| `slides_assets/lab6_s04_job_trigger.png` | ลำดับ/ชื่อภาพเดิม ถูกแทนด้วยภาพ GWT แยก field |
| `slides_assets/lab6_s05_gitea_webhook.png` | หน้า webhook ของ SCM เดิม |
| `slides_assets/lab6_s06_pipeline_graph.png` | ลำดับภาพเดิม ถูกแทนด้วย `lab6_s08_pipeline_graph.png` |
| `slides_assets/lab6_s07_console_pytest.png` | ลำดับภาพเดิม ถูกแทนด้วย `lab6_s09_console_pytest.png` |
| `slides_assets/lab6_s08_console_verify.png` | ลำดับภาพเดิม ถูกแทนด้วย `lab6_s09b_console_verify.png` |
| `slides_assets/lab6_s09_dashboard_v1.png` | ลำดับภาพเดิม ถูกแทนด้วย `lab6_s10_dashboard_v1.png` |
| `slides_assets/lab6_s10_dashboard_v2.png` | ลำดับภาพเดิม ถูกแทนด้วย `lab6_s11_dashboard_v2.png` |
| `slides_assets/lab6_s11_hub_public_tags.png` | ลำดับภาพเดิม ถูกแทนด้วย `lab6_s12_hub_public_tags.png` |

### สถานะ handoff ปัจจุบัน

- คง `devtools-jk-lab` ให้ทำงานต่อ โดย `jenkins`, `smee-hello`, `smee-webapp` และ `webapp` ยัง Up บน network `cicd-net`
- คง relay สองตัวพร้อม channel/target/token แบบ 1:1 และ restart policy `unless-stopped`; restart/reconnect ของ `smee-hello` ผ่านแล้วและใช้ channel เดิม
- คง GitHub repositories `hello-ci`, `webapp`, hooks จริง, Jenkins jobs `hello-ci-pipeline`, `webapp-deploy` และ Docker Hub tags ไว้รอ U-P5-INT
- ไม่เก็บ token หรือ smee channel id จริงลงไฟล์/log; mock auth-only 4 ภาพเป็น pending เดียวที่ต้องใช้ session จากผู้ใช้เพื่อสลับเป็น real masked capture
