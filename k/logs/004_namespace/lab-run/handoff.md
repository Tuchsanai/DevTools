# Handoff — container ทดลองบท 004 (เปิดไว้สำหรับ screenshot)

| หัวข้อ | ค่า |
|---|---|
| container | `k8s-lab-ns004-5cdb6e` (image `tuchsanai/devtools-kind:2569_1`, ID `8108a1bc7901`, `--privileged --hostname k8s-lab`) |
| SSH | host port **2224** → 22 (`root` / รหัส LAB `passwd`) |
| เข้าจากเครื่อง agent (อยู่ใน container) | ใช้ gateway `172.18.0.1:2224` แทน `localhost:2224` |
| คลัสเตอร์ | kind `lab` (K8s v1.37.0) 3 node, context ปัจจุบัน `kind-lab` (namespace `default`) |
| ไฟล์ LAB ใน container | `/workspace/004_kubernetes_namespace/02_LAB` |
| image ใน container | `som-shop-web:1.1` (ID `d1aecb886b11`), `postgres:17.11-alpine` (load เข้า node แล้ว) |

## สภาพตอนส่งมอบ

- namespace `som-dev`, `som-staging`, `som-prod` (labels env/team/PSA ตาม `k8s/00-namespaces.yaml`) + `prod-budget` / `prod-box-size` ใน som-prod + SA `intern`/Role/RoleBinding ใน som-dev
- Pod `som-shop` `2/2 Running` ทั้ง 3 โซน (dev/staging บน lab-worker, prod บน lab-worker2)
- ออเดอร์: **som-dev 1, som-staging 2, som-prod 3** (กล่อง "ออเดอร์ทั้งหมด" ต่างกัน)
- port-forward ใน container (setsid nohup, `--address 127.0.0.1`): `3001→som-dev`, `3002→som-staging`, `3003→som-prod` (log `/tmp/pf-300N.log`)
- context `intern@som-dev` (token อายุ 24 ชม. สร้าง 13:37 UTC) อยู่ใน kubeconfig แล้ว — ใช้ถ่าย `kubectl --context intern@som-dev get pods` / Forbidden ได้

## เปิดหน้าร้านใน browser

จากเครื่อง host (Windows):
```bash
ssh -p 2224 -L 3001:localhost:3001 -L 3002:localhost:3002 -L 3003:localhost:3003 root@localhost
# แล้วเปิด http://localhost:3001  http://localhost:3002  http://localhost:3003
```
จากเครื่อง agent (ไม่ต้องพิมพ์รหัส, port ฝั่ง agent 13001–13003):
```bash
printf '#!/bin/sh\necho passwd\n' > /tmp/askpass && chmod +x /tmp/askpass
SSH_ASKPASS=/tmp/askpass SSH_ASKPASS_REQUIRE=force DISPLAY=:0 setsid ssh -f -N \
  -o PubkeyAuthentication=no -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR \
  -p 2224 -L 13001:localhost:3001 -L 13002:localhost:3002 -L 13003:localhost:3003 root@172.18.0.1 </dev/null
# ปิด tunnel: ห้ามใช้ pkill -f ที่ pattern ตรงกับ command line ของ shell ตัวเอง → ใช้ pgrep -f "[s]sh -f -N" แล้ว kill <PID>
```

## ถ้า port-forward หลุด (เช่น Pod ถูกลบ/สร้างใหม่)

```bash
docker exec k8s-lab-ns004-5cdb6e bash -c 'pkill -f "[k]ubectl port-forward"; for p in 1 2 3; do ns=$(echo som-dev som-staging som-prod | cut -d" " -f$p); setsid nohup kubectl port-forward -n $ns pod/som-shop 300$p:3000 --address 127.0.0.1 > /tmp/pf-300$p.log 2>&1 < /dev/null & done'
```

## ฉากลบ som-dev (สำหรับ screenshot หลังถ่าย 3 แท็บแล้ว)

```bash
docker exec k8s-lab-ns004-5cdb6e bash -c 'time kubectl delete ns som-dev'   # ใช้จริง ~10 วิ
docker exec k8s-lab-ns004-5cdb6e bash -c 'kubectl get pods -A -l app=som-shop; kubectl get sa intern -n som-dev; kubectl --context intern@som-dev get pods'
# ผลจริง: เหลือ som-prod / som-staging, "Error from server (NotFound): namespaces \"som-dev\" not found",
#         "error: You must be logged in to the server (Unauthorized)"; แท็บ 3001 ใช้ไม่ได้ (port-forward จบด้วย "error: lost connection to pod" ตอนมีคนเข้าครั้งถัดไป), 3002/3003 ยังเปิดได้
```
คืนสภาพ som-dev (ออเดอร์จะเริ่มที่ 0):
```bash
docker exec k8s-lab-ns004-5cdb6e bash -c 'cd /workspace/004_kubernetes_namespace/02_LAB/som-shop-envs && kubectl apply -f k8s/00-namespaces.yaml && kubectl apply -f k8s/som-shop.yaml -n som-dev && kubectl apply -f k8s/intern-rbac.yaml && kubectl wait --for=condition=Ready pod/som-shop -n som-dev --timeout=180s'
# แล้วรัน port-forward 3001 ใหม่ และสร้าง token/context intern ใหม่ (token เก่าใช้ไม่ได้แล้ว)
```

## ลบ container (ผู้ประสานงานทำเอง)

```bash
docker rm -fv k8s-lab-ns004-5cdb6e
docker ps -a --filter "name=^k8s-lab-ns004"
```
