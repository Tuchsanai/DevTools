# README-split — ที่มาของภาพบท 007 Kubernetes Deployment

แยกจากบทรวม `logs/005_rs_deploy_svc/` (ไฟล์ภาพเดิมอยู่ใต้ `005_kubernetes_replicaset_deployment_service/`). สร้างตารางจาก `image-sources.tsv` (ผลของ `python3 build_images.py`).

| id | ไฟล์ | มาจาก |
|---|---|---|
| T01 | 01-opening-manual-swap-stumble.png | บทรวม T01 01-opening-lonely-pod-lost.png (แก้) |
| T02 | 02-rs-template-no-change.png | บทรวม T12 12-rs-why-not-directly.png (แก้) |
| T03 | 03-new-metaphor-legend.png | บทรวม T02 02-new-metaphor-legend.png (แก้) |
| T04 | 04-deploy-hierarchy.png | บทรวม T13 13-deploy-hierarchy.png |
| T05 | 05-do-not-edit-owned-rs.png | ใหม่ |
| T06 | 06-deploy-manifest-anatomy.png | ใหม่ |
| T07 | 07-create-dry-run.png | ใหม่ |
| T08 | 08-ready-uptodate-available.png | ใหม่ |
| T09 | 09-pod-template-hash.png | บทรวม T14 14-pod-template-hash.png (แก้) |
| T10 | 10-what-triggers-rollout.png | ใหม่ |
| T11 | 11-rolling-update-steps.png | บทรวม T15 15-rolling-update-steps.png (แก้) |
| T12 | 12-max-surge-unavailable.png | บทรวม T16 16-max-surge-unavailable.png (แก้) |
| T13 | 13-recreate-vs-rolling.png | บทรวม T17 17-recreate-vs-rolling.png |
| T14 | 14-recreate-for-db.png | ใหม่ |
| T15 | 15-readiness-gates-rollout.png | บทรวม T18 18-readiness-gates-rollout.png |
| T16 | 16-probe-roles.png | ใหม่ |
| T17 | 17-termination-timeline.png | ใหม่ |
| T18 | 18-zero-downtime.png | บทรวม T38 38-zero-downtime.png (แก้) |
| T19 | 19-progress-deadline.png | บทรวม T19 19-progress-deadline.png |
| T20 | 20-no-auto-rollback.png | ใหม่ |
| T21 | 21-rollout-history.png | บทรวม T20 20-rollout-history.png |
| T22 | 22-change-cause-trap.png | ใหม่ |
| T23 | 23-rollout-undo.png | บทรวม T21 21-rollout-undo.png |
| T24 | 24-last-applied-warning.png | ใหม่ |
| T25 | 25-pause-resume.png | บทรวม T22 22-pause-resume.png |
| T26 | 26-revision-history-limit.png | บทรวม T23 23-revision-history-limit.png (แก้) |
| T27 | 27-ways-to-change.png | บทรวม T24 24-ways-to-change.png (แก้) |
| T28 | 28-apply-overwrites-replicas.png | ใหม่ |
| T29 | 29-adopt-rs.png | ใหม่ |
| T30 | 30-orphan-alternative.png | ใหม่ |
| T31 | 31-failure-modes.png | ใหม่ |
| T32 | 32-blue-green.png | บทรวม T25 25-blue-green.png |
| T33 | 33-canary-by-label.png | บทรวม T26 26-canary-by-label.png |
| T34 | 34-decision-table.png | บทรวม T39 39-decision-table.png (แก้) |
| T35 | 35-command-cheatsheet.png | ใหม่ |
| T36 | 36-next-chapter.png | บทรวม T40 40-next-chapter.png (แก้) |
| L01 | 01-lab0-prepare.png | บทรวม L01 01-lab0-prepare.png (แก้) |
| L02 | 02-lab1-first-deployment.png | บทรวม L04 04-lab3-first-deployment.png (แก้) |
| L03 | 03-lab1-rs-scale-reverted.png | ใหม่ |
| L04 | 04-lab2-rolling-rs.png | บทรวม L05 05-lab4-rolling-rs.png |
| L05 | 05-lab2-client-sees-mix.png | ใหม่ |
| L06 | 06-lab3-history-undo.png | บทรวม L06 06-lab4-history-undo.png (แก้) |
| L07 | 07-lab3-pause-restart.png | ใหม่ |
| L08 | 08-lab4-strategies.png | บทรวม L07 07-lab5-strategies.png (แก้) |
| L09 | 09-lab5-readiness-minready.png | ใหม่ |
| L10 | 10-lab6-broken-rollout.png | บทรวม L08 08-lab6-broken-rollout.png (แก้) |
| L11 | 11-lab7-zero-downtime.png | บทรวม L13 13-lab10-zero-downtime.png (แก้) |
| L12 | 12-lab8-migrate-rs.png | ใหม่ |
| L13 | 13-lab9-blue-green-canary.png | ใหม่ |
| L14 | 14-lab10-architecture.png | บทรวม L15 15-lab12-architecture.png (แก้) |
| L15 | 15-lab10-start-from-rs.png | ใหม่ |
| L16 | 16-lab10-convert-to-deployment.png | ใหม่ |
| L17 | 17-lab10-rollout-1-3.png | บทรวม L23 23-lab12-rollout-1-3.png (แก้) |
| L18 | 18-lab10-shop-1-3-page.png | บทรวม L19 19-lab12-open-shop-30080.png (แก้) |
| L19 | 19-lab10-history-undo.png | บทรวม L24 24-lab12-rollback.png (แก้) |
| L20 | 20-lab10-broken-1-4.png | บทรวม L25 25-lab12-broken-still-selling.png (แก้) |
| L21 | 21-lab10-scale-3-to-5.png | บทรวม L21 21-lab12-scale-3-to-5.png (แก้) |
| L22 | 22-lab10-db-lost-restart.png | บทรวม L26 26-lab12-db-pod-lost-data.png (แก้) |
| L23 | 23-lab10-wrap-up.png | บทรวม L27 27-lab12-wrap-up.png (แก้) |

สรุป: ทั้งหมด 59 ภาพ (Theory 36, LAB 23) — ใช้ prompt เดิม 10, แก้จากบทรวม 25, ใหม่ 24; needs_test 12 ภาพ (T29, L06, L08, L09, L11, L12, L16–L20, L22)
