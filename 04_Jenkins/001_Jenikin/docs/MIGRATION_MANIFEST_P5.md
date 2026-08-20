# Phase 5 GitHub migration manifest

หน่วยงาน: **U-P5-0** · วันที่สแกน: **2026-08-20 UTC**

## ขอบเขตการสแกน

รันจากราก repository ด้วยคำสั่ง:

```bash
rg -n -i 'gitea|localhost:3000|gitea_data|student/hello-ci|student/webapp' . \
  -g '!logs/**' \
  -g '!backup/**' \
  -g '!.ipynb_checkpoints/**' \
  -g '!docs/LEDGER.md' \
  -g '!docs/CRITIQUE*'
```

ผล baseline คือ **376 matching lines ใน 44 files** ตารางด้านล่างมี 44 แถว จึงครอบคลุม **44/44 files (100%)** จำนวน hit หมายถึงจำนวนบรรทัดที่ `rg -n` รายงาน ไม่ใช่จำนวน occurrence ภายในบรรทัด

## File-level disposition

| File | Hits | Action |
|---|---:|---|
| `004_LAB_Pipeline_From_Git/Jenkinsfile` | 1 | rewrite — U-P5-4 |
| `004_LAB_Pipeline_From_Git/README.md` | 44 | rewrite — U-P5-4 |
| `004_LAB_Pipeline_From_Git/check.sh` | 14 | rewrite — U-P5-2 (LAB 4 check contract) |
| `004_LAB_Pipeline_From_Git/expected.txt` | 1 | rewrite — U-P5-4 |
| `004_LAB_Pipeline_From_Git/hello.sh` | 1 | rewrite — U-P5-4 |
| `005_LAB_Webhook_Trigger/README.md` | 28 | rewrite — U-P5-5 |
| `005_LAB_Webhook_Trigger/check.sh` | 7 | rewrite — U-P5-2 (LAB 5 check contract) |
| `006_LAB_CICD_Capstone/README.md` | 27 | rewrite — U-P5-6 |
| `006_LAB_CICD_Capstone/check.sh` | 9 | rewrite — U-P5-2 (LAB 6 check contract) |
| `Jenkins_CICD_Docker_Slides.html` | 18 | rewrite/generated — U-P5-8; generated from `tools/slides_src.html`, ห้ามแก้ generated deck โดยไม่แก้ source |
| `docs/INTEGRATION.md` | 5 | rewrite — U-P5-9 |
| `docs/LAB_TEMPLATE.md` | 2 | rewrite — U-P5-9 |
| `docs/PLAN.md` | 19 | rewrite to Phase 5 pointer — U-P5-9 |
| `docs/PLAN_P5_GITHUB.md` | 6 | keep-historical — FROZEN canonical plan ใช้คำเดิมเพื่อบันทึกต้นทาง migration |
| `docs/REWRITE_SPEC.md` | 2 | keep-historical — specification ของรอบก่อนหน้า ไม่ใช่ student runtime deliverable |
| `docs/STACK_RESOLVED.md` | 4 | rewrite — U-P5-9 |
| `prompt.md` | 3 | keep-historical — phase coordination record; ข้อความกล่าวถึง migration โดยเจตนา |
| `readme.md` | 3 | rewrite — U-P5-7 |
| `slides_assets/d7_polling_webhook.svg` | 1 | rewrite — U-P5-8 |
| `slides_assets/d8_capstone_topology.svg` | 2 | rewrite — U-P5-8 |
| `tools/bootstrap/common.sh` | 36 | rewrite — U-P5-1 |
| `tools/bootstrap/fixtures/hello-ci.Jenkinsfile` | 1 | rewrite — U-P5-1 |
| `tools/bootstrap/fixtures/hello-ci.expected.txt` | 1 | rewrite — U-P5-1 |
| `tools/bootstrap/fixtures/hello-ci.hello.sh` | 1 | rewrite — U-P5-1 |
| `tools/bootstrap/jobs/hello-ci-poll.xml` | 2 | rewrite — U-P5-1 |
| `tools/bootstrap/jobs/hello-ci-webhook.xml` | 2 | rewrite — U-P5-1 |
| `tools/bootstrap/up_to_lab4.sh` | 1 | rewrite — U-P5-1 |
| `tools/slides_src.html` | 16 | rewrite — U-P5-8; canonical source ของ `Jenkins_CICD_Docker_Slides.html` |
| `tools/ui/annotations/lab4.json` | 2 | rewrite — U-P5-4 |
| `tools/ui/annotations/lab6.json` | 3 | rewrite — U-P5-6 |
| `tools/ui/common.py` | 4 | rewrite — U-P5-0; remove `gitea_login` และ dead references |
| `tools/ui/deck_consistency_test.py` | 5 | rewrite — U-P5-9 |
| `tools/ui/int_consistency.py` | 6 | rewrite — U-P5-9 |
| `tools/ui/lab4_gitea_install.py` | 19 | delete — U-P5-0 |
| `tools/ui/lab4_scm_job.py` | 4 | rewrite — U-P5-4 |
| `tools/ui/lab4_scm_repo.py` | 14 | rewrite — U-P5-4; ห้าม U-P5-0 แก้ |
| `tools/ui/lab4_scm_rewrite_capture.py` | 24 | delete — U-P5-0 |
| `tools/ui/lab5_gitea_webhook.py` | 10 | delete — U-P5-0 |
| `tools/ui/lab5_payload.py` | 8 | rewrite — U-P5-5; ห้าม U-P5-0 แก้ |
| `tools/ui/lab5_push_build.py` | 1 | rewrite — U-P5-5 |
| `tools/ui/lab6_gitea_repo.py` | 9 | delete — U-P5-0 |
| `tools/ui/lab6_job.py` | 2 | rewrite — U-P5-6; ห้าม U-P5-0 แก้ |
| `tools/ui/lab6_pipeline.py` | 1 | rewrite — U-P5-6 |
| `tools/ui/lab6_webhook.py` | 7 | delete — U-P5-0 |

## Coverage check

- Baseline files: 44
- Manifest rows: 44
- Missing files: 0
- Duplicate file rows: 0
- Coverage: **100%**

รายการ `keep-historical` ไม่ได้แปลว่าเป็นข้อยกเว้นอัตโนมัติของ rg-zero gate; U-P5-9 ต้องตัดสิน allowlist/archive ตาม FROZEN plan โดยไม่แก้ประวัติย้อนหลัง
