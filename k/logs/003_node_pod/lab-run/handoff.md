# Handoff — LAB 003 (Node กับ Pod) container ที่เปิดค้างไว้ให้ถ่าย screenshot

| รายการ | ค่า |
|---|---|
| container | `k8s-lab-nodepod003-211945` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`) |
| SSH | host port **2224** → 22, user `root` รหัส `passwd` (เฉพาะ LAB นี้), ไม่ได้ publish Jupyter/NodePort |
| gateway (agent อยู่ใน container) | `172.18.0.1` — จากเครื่อง Windows ใช้ `localhost` ได้เลย |
| ไฟล์ LAB ใน container | `/workspace/003_kubernetes_node_pod/02_LAB` (`docker cp`, ไม่ bind mount) |
| คลัสเตอร์ | kind `lab` (context `kind-lab`), 3 node Ready, ไม่มี SchedulingDisabled, ไม่มี taint นอกจาก control-plane |

## สภาพปัจจุบัน (รีเซ็ตแล้ว 4 ต.ค. 2569 ~19:31 น.)

- `lab-worker` และ `lab-worker2` ติด label `shop=open`
- `som-shop-a` 2/2 Running บน **lab-worker** ("ร้านอาหารแมวน้องส้ม สาขา lab-worker") — มี **2 ออเดอร์** (สั่งไว้ให้ตรงภาพ L19)
- `som-shop-b` 2/2 Running บน **lab-worker2** ("ร้านอาหารแมวน้องส้ม สาขา lab-worker2") — 0 ออเดอร์
- port-forward ใน container (รันด้วย `setsid nohup`, log `/tmp/pf-a.log`, `/tmp/pf-b.log`):
  - `kubectl port-forward pod/som-shop-a 3001:3000 --address 127.0.0.1`
  - `kubectl port-forward pod/som-shop-b 3002:3000 --address 127.0.0.1`
- ไม่มี Pod `lab=03` ค้าง, ไม่มีไฟล์ static Pod ค้างใน `lab-worker:/etc/kubernetes/manifests`

## เปิด tunnel ดูหน้าร้าน

จากเครื่อง Windows / host:

```bash
ssh -p 2224 -L 3001:localhost:3001 -L 3002:localhost:3002 root@localhost   # รหัส passwd
# browser: http://localhost:3001  (สาขา lab-worker)   http://localhost:3002  (สาขา lab-worker2)
```

จาก agent ใน container (port ซ้ายเปลี่ยนเป็น 13001/13002 ได้ถ้าชน) แบบไม่ต้องพิมพ์รหัส:

```bash
printf '#!/bin/sh\necho passwd\n' > /tmp/askpass && chmod +x /tmp/askpass
SSH_ASKPASS=/tmp/askpass SSH_ASKPASS_REQUIRE=force DISPLAY=:0 setsid ssh -f -N -o ExitOnForwardFailure=yes \
  -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null \
  -p 2224 -L 13001:localhost:3001 -L 13002:localhost:3002 root@172.18.0.1 </dev/null
curl -s localhost:13001 | grep -o '<h1>[^<]*</h1>'
# ปิด tunnel: หา PID ด้วย  ss -ltnp | grep 1300  แล้ว kill <PID>
# (อย่าใช้ pkill -f "ssh -f -N ..." เพราะ pattern จะตรงกับ command line ของ shell ที่สั่งเองแล้วฆ่าตัวเอง)
```

ถ้า port-forward หลุด (เช่นหลังลบ/สร้าง Pod ใหม่) เปิดใหม่ด้วย:

```bash
docker exec k8s-lab-nodepod003-211945 bash -c 'pkill -f "[k]ubectl port-forward pod/som-shop"; \
  setsid nohup kubectl port-forward pod/som-shop-a 3001:3000 --address 127.0.0.1 > /tmp/pf-a.log 2>&1 < /dev/null & \
  setsid nohup kubectl port-forward pod/som-shop-b 3002:3000 --address 127.0.0.1 > /tmp/pf-b.log 2>&1 < /dev/null & sleep 2; cat /tmp/pf-*.log'
```

## คำสั่งจำลองสำหรับ screenshot (รันใน container ทดลองเท่านั้น: `docker exec k8s-lab-nodepod003-211945 ...` หรือใน SSH session port 2224)

สั่งซื้อเพิ่ม: `curl -s -X POST localhost:3001/api/orders -H 'Content-Type: application/json' -d '{"product_id":1,"qty":1}'`

**drain (L20)**

```bash
kubectl drain lab-worker --ignore-daemonsets                                   # error: cannot delete Pods with local storage ... (และ cordon ไปแล้ว)
kubectl drain lab-worker --ignore-daemonsets --delete-emptydir-data --force    # ~1 วิ: pod/som-shop-a evicted, node/lab-worker drained
kubectl get pod -l app=som-shop -o wide; kubectl get nodes                     # เหลือ som-shop-b, lab-worker Ready,SchedulingDisabled
kubectl apply -f /workspace/003_kubernetes_node_pod/02_LAB/som-shop-branches/k8s/som-shop-a.yaml   # Pending (anti-affinity + taint + unschedulable)
kubectl uncordon lab-worker                                                     # som-shop-a Running ภายใน ~7 วิ (ออเดอร์เริ่มที่ 0) → เปิด port-forward 3001 ใหม่
```

**เรือล่ม (L21)** — `docker` ที่นี่คือ dockerd *ภายใน* container ทดลอง

```bash
docker exec k8s-lab-nodepod003-211945 docker stop lab-worker2      # port-forward 3002 หลุดทันที (lost connection to pod)
kubectl get nodes -w                                                 # NotReady หลัง ~43–50 วิ
kubectl get pod -l app=som-shop -o wide -w                           # som-shop-b 2/2 Running ค้าง → Terminating ~60 วิหลัง NotReady
docker exec k8s-lab-nodepod003-211945 docker start lab-worker2     # Ready ใน ~2 วิ, som-shop-b หายใน ~5 วิ
kubectl apply -f .../k8s/som-shop-b.yaml                             # เปิดสาขา b ใหม่ (ออเดอร์ 0) แล้วเปิด port-forward 3002 ใหม่
```

คืนสภาพหลังถ่ายภาพ: `kubectl uncordon lab-worker lab-worker2` และตรวจ `kubectl get nodes` ทุกตัว `Ready`

## ลบเมื่อเสร็จ (ผู้ประสานงาน)

```bash
docker rm -fv k8s-lab-nodepod003-211945
```

ฝั่ง agent ไม่มี ssh tunnel หรือ askpass ค้าง (ลบ/ปิดแล้ว)
