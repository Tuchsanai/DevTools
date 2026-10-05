# บท 006 Service — ที่มาของภาพ (แยกจากบทรวม `logs/005_rs_deploy_svc`)

Theory 36 ภาพ, LAB 24 ภาพ (รวม 60) · ใช้ prompt เดิม 12, แก้จากเดิม 22, ใหม่ 26

สร้างโดย `python3 build_images.py` (อย่าแก้ไฟล์นี้ด้วยมือ) · "มาจาก" = id + ชื่อไฟล์ในบทรวม; "(แก้)" = ปรับป้าย/ฉาก เช่น Deployment → ReplicaSet, LAB12 → LAB10, บทที่ 5 → บทที่ 6

| id | ไฟล์ | มาจาก |
|---|---|---|
| T01 | `01-opening-booths-lost-customers.png` | T01 01-opening-lonely-pod-lost.png (แก้) |
| T02 | `02-service-metaphor-legend.png` | T02 02-new-metaphor-legend.png (แก้) |
| T03 | `03-port-forward-per-pod.png` | ใหม่ |
| T04 | `04-why-service.png` | T27 27-why-service.png |
| T05 | `05-clusterip-virtual.png` | ใหม่ |
| T06 | `06-service-manifest-anatomy.png` | ใหม่ |
| T07 | `07-selector-endpointslice.png` | T28 28-selector-endpointslice.png |
| T08 | `08-endpointslice-controller.png` | ใหม่ |
| T09 | `09-endpoints-deprecated.png` | ใหม่ |
| T10 | `10-service-cidr.png` | ใหม่ |
| T11 | `11-port-targetport-nodeport.png` | T29 29-clusterip-ports.png |
| T12 | `12-named-multi-port.png` | ใหม่ |
| T13 | `13-nodeport-every-node.png` | T33 33-nodeport.png (แก้) |
| T14 | `14-nodeport-path-from-browser.png` | ใหม่ |
| T15 | `15-nodeport-rules-errors.png` | ใหม่ |
| T16 | `16-loadbalancer-pending.png` | T34 34-loadbalancer-pending.png |
| T17 | `17-externalname-cname.png` | T35 35-externalname-headless.png (แก้) |
| T18 | `18-headless-phonebook.png` | T35 35-externalname-headless.png (แก้) |
| T19 | `19-service-dns-cross-ns.png` | T30 30-service-dns.png |
| T20 | `20-resolv-search-ndots.png` | ใหม่ |
| T21 | `21-service-env-vars.png` | ใหม่ |
| T22 | `22-kube-proxy-signposts.png` | T31 31-kube-proxy-signposts.png |
| T23 | `23-kube-proxy-watch-modes.png` | ใหม่ |
| T24 | `24-random-per-connection.png` | T32 32-load-distribution.png (แก้) |
| T25 | `25-keepalive-one-connection.png` | ใหม่ |
| T26 | `26-session-affinity.png` | T32 32-load-distribution.png (แก้) |
| T27 | `27-readiness-endpoints.png` | T37 37-readiness-endpoints.png |
| T28 | `28-terminating-serving.png` | T38 38-zero-downtime.png (แก้) |
| T29 | `29-debug-ladder.png` | ใหม่ |
| T30 | `30-selector-mismatch-debug.png` | T36 36-selector-mismatch-debug.png |
| T31 | `31-targetport-mismatch.png` | ใหม่ |
| T32 | `32-networkpolicy-after-dnat.png` | ใหม่ |
| T33 | `33-limits-remaining.png` | ใหม่ |
| T34 | `34-service-type-decision.png` | T39 39-decision-table.png (แก้) |
| T35 | `35-chapter-summary.png` | ใหม่ |
| T36 | `36-next-chapter-manager.png` | T40 40-next-chapter.png (แก้) |
| L01 | `01-lab0-prepare.png` | L01 01-lab0-prepare.png (แก้) |
| L02 | `02-lab1-ip-changes.png` | ใหม่ |
| L03 | `03-lab2-expose-endpointslice.png` | ใหม่ |
| L04 | `04-lab2-scale-endpoints-follow.png` | L21 21-lab12-scale-3-to-5.png (แก้) |
| L05 | `05-lab3-ports-named.png` | ใหม่ |
| L06 | `06-lab4-dns-env.png` | ใหม่ |
| L07 | `07-lab5-random-affinity.png` | L09 09-lab7-clusterip-dns.png (แก้) |
| L08 | `08-lab6-not-ready.png` | ใหม่ |
| L09 | `09-lab7-debug.png` | L10 10-lab8-debug-endpoints.png (แก้) |
| L10 | `10-lab8-nodeport-browser.png` | L11 11-lab9-nodeport-browser.png |
| L11 | `11-lab8-keepalive-lb.png` | L12 12-lab9-keepalive-vs-curl.png (แก้) |
| L12 | `12-lab9-cross-namespace.png` | L14 14-lab11-cross-namespace.png |
| L13 | `13-lab9-headless-externalname.png` | ใหม่ |
| L14 | `14-lab9-networkpolicy-targetport.png` | ใหม่ |
| L15 | `15-lab10-architecture.png` | L15 15-lab12-architecture.png (แก้) |
| L16 | `16-lab10-build-images.png` | L16 16-lab12-build-images.png |
| L17 | `17-lab10-db-service.png` | L17 17-lab12-db-service.png (แก้) |
| L18 | `18-lab10-stock-shelves-once.png` | L18 18-lab12-stock-shelves-once.png |
| L19 | `19-lab10-open-shop-30080.png` | L19 19-lab12-open-shop-30080.png (แก้) |
| L20 | `20-lab10-hit-orders-shared.png` | L20 20-lab12-curl-loop-balance.png (แก้) |
| L21 | `21-lab10-scale-and-heal.png` | L21 21-lab12-scale-3-to-5.png + L22 22-lab12-delete-web-pod.png (แก้) |
| L22 | `22-lab10-db-pod-lost-data.png` | L26 26-lab12-db-pod-lost-data.png (แก้) |
| L23 | `23-lab10-manual-update-pain.png` | ใหม่ |
| L24 | `24-lab10-wrap-up-bridge.png` | L27 27-lab12-wrap-up.png (แก้) |
