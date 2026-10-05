# README-split — บท 005 Kubernetes ReplicaSet

ที่มาของภาพแต่ละภาพ (สร้างจาก `image-sources.tsv` ที่ `build_images.py` เขียน) — บทรวมเดิม: `logs/005_rs_deploy_svc/` (อ่านอย่างเดียว)

สรุป: Theory 36 ภาพ, LAB 20 ภาพ, รวม 56 — ใช้ prompt เดิมไม่แก้ 6, แก้จากบทรวม 9, ใหม่ 41; needs_test 16

| id | ไฟล์ | มาจาก | needs_test |
|---|---|---|---|
| T01 | 01-opening-lonely-pod-lost.png | บทรวม T01 01-opening-lonely-pod-lost.png (แก้) |  |
| T02 | 02-recap-three-chapters.png | ใหม่ |  |
| T03 | 03-metaphor-legend.png | บทรวม T02 02-new-metaphor-legend.png (แก้) |  |
| T04 | 04-reconcile-loop.png | บทรวม T03 03-reconcile-loop.png |  |
| T05 | 05-controllers-in-tower.png | บทรวม T04 04-controllers-in-tower.png (แก้) |  |
| T06 | 06-level-triggered.png | ใหม่ |  |
| T07 | 07-rs-anatomy.png | บทรวม T05 05-rs-anatomy.png |  |
| T08 | 08-rs-yaml-map.png | ใหม่ |  |
| T09 | 09-pod-naming.png | ใหม่ |  |
| T10 | 10-match-expressions.png | ใหม่ |  |
| T11 | 11-selector-template-mismatch.png | ใหม่ | ✓ |
| T12 | 12-owner-references.png | ใหม่ |  |
| T13 | 13-rs-status-columns.png | ใหม่ |  |
| T14 | 14-rs-self-healing.png | บทรวม T06 06-rs-self-healing.png |  |
| T15 | 15-delete-overlap-terminating.png | ใหม่ |  |
| T16 | 16-drain-single-vs-rs.png | ใหม่ |  |
| T17 | 17-node-down-timeline.png | ใหม่ | ✓ |
| T18 | 18-rs-scale.png | บทรวม T11 11-rs-scale.png |  |
| T19 | 19-scale-down-order.png | ใหม่ | ✓ |
| T20 | 20-rs-counts-by-label.png | บทรวม T07 07-rs-counts-by-label.png |  |
| T21 | 21-rs-adopts-stray.png | บทรวม T08 08-rs-adopts-stray.png (แก้) |  |
| T22 | 22-rs-deletes-extra.png | บทรวม T09 09-rs-deletes-extra.png |  |
| T23 | 23-overlapping-selectors.png | ใหม่ |  |
| T24 | 24-unlabel-for-debug.png | ใหม่ |  |
| T25 | 25-selector-immutable.png | ใหม่ | ✓ |
| T26 | 26-template-change-old-pods.png | บทรวม T12 12-rs-why-not-directly.png (แก้) |  |
| T27 | 27-rs-delete-cascade.png | บทรวม T10 10-rs-owner-cascade.png (แก้) |  |
| T28 | 28-orphan-readopt.png | ใหม่ |  |
| T29 | 29-replicationcontroller-history.png | ใหม่ |  |
| T30 | 30-rs-quota-cap.png | ใหม่ | ✓ |
| T31 | 31-psa-workload-warn.png | ใหม่ | ✓ |
| T32 | 32-anti-affinity-required.png | ใหม่ |  |
| T33 | 33-preferred-and-spread.png | ใหม่ |  |
| T34 | 34-names-ips-change.png | ใหม่ |  |
| T35 | 35-summary-checklist.png | ใหม่ |  |
| T36 | 36-next-chapters.png | ใหม่ |  |
| L01 | 01-lab0-prepare.png | บทรวม L01 01-lab0-prepare.png (แก้) |  |
| L02 | 02-lab1-first-rs.png | ใหม่ |  |
| L03 | 03-lab2-delete-watch.png | บทรวม L02 02-lab1-rs-self-heal.png (แก้) |  |
| L04 | 04-lab2-drain-rebirth.png | ใหม่ | ✓ |
| L05 | 05-lab3-scale.png | ใหม่ | ✓ |
| L06 | 06-lab4-label-trap.png | บทรวม L03 03-lab2-label-trap.png (แก้) |  |
| L07 | 07-lab5-template-old-pods.png | ใหม่ | ✓ |
| L08 | 08-lab6-cascade-orphan.png | ใหม่ |  |
| L09 | 09-lab7-quota.png | ใหม่ | ✓ |
| L10 | 10-lab8-spread.png | ใหม่ |  |
| L11 | 11-lab9-architecture.png | ใหม่ |  |
| L12 | 12-lab9-prepare-image.png | ใหม่ |  |
| L13 | 13-lab9-three-booths-two-ships.png | ใหม่ | ✓ |
| L14 | 14-lab9-port-forward-each.png | ใหม่ |  |
| L15 | 15-lab9-orders-mismatch.png | ใหม่ | ✓ |
| L16 | 16-lab9-delete-pod-data-lost.png | ใหม่ | ✓ |
| L17 | 17-lab9-scale-3-5-2.png | ใหม่ | ✓ |
| L18 | 18-lab9-template-promo.png | ใหม่ | ✓ |
| L19 | 19-lab9-manual-replace.png | ใหม่ | ✓ |
| L20 | 20-lab9-wrap-up-handoff.png | ใหม่ |  |

ภาพจากบทรวมที่ไม่ได้ใช้ในบทนี้: T13–T40, L04–L27 (ไปบท 006/007 ตามสัญญา) — L01–L03 และ T01–T12 ถูกใช้ทั้งหมด (T02 legend แยกเป็นของบทนี้, T12 กลายเป็น T26 template-change-old-pods)
