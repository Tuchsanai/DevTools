# Handoff — บท 011 Secret (container ทดลองที่เปิดค้างไว้สำหรับ screenshot)

| หัวข้อ | ค่า |
|-------|-----|
| container | `k8s-lab-secret011-9ffaf1` (owner `agent-011`, image `tuchsanai/devtools-kind:2569_1` = `8108a1bc7901`) |
| gateway (Docker host จากฝั่ง agent) | `172.18.0.1` |
| SSH | `ssh -p 2224 root@172.18.0.1` (รหัส `passwd` หรือ key ที่ container สร้างเอง `/etc/devtools/ssh/devtoolSSH`) — ตรวจแล้ว PASS ทั้งสองแบบ |
| NodePort 30080 (ร้าน HTTP) | host port **30090** → `http://172.18.0.1:30090` (บนเครื่องนักศึกษา = `http://localhost:30080`) |
| NodePort 30081 (LAB4 ngx-tls) | host port **30091** (ตอนนี้ไม่มี Service ใช้ — ลบไปตอนเก็บกวาด LAB1–8) |
| NodePort 30082 (ร้าน HTTPS) | host port **30092** → `https://172.18.0.1:30092` (cert self-signed CN=shop.som.local → เบราว์เซอร์เตือน กด Advanced → Proceed) |
| โฟลเดอร์ในcontainer | `/workspace/011_kubernetes_secret/02_LAB` (docker cp ไม่ได้ bind mount) |

ผู้ประสานงานเป็นคนลบ container เอง: `docker rm -fv k8s-lab-secret011-9ffaf1`

## สภาพปัจจุบัน (ตรวจเมื่อ 11:46 UTC = 18:46 ในcontainer)

- namespace `som-shop`: `som-db-0` (StatefulSet, `POSTGRES_PASSWORD` ← `secretKeyRef som-db-secret`), `som-web` 3/3 (web และ init `db-seed` ใช้ `DATABASE_URL` ← `secretKeyRef som-db-secret`), `som-https` 1/1 (nginx:1.27-alpine + Secret `som-tls`) 
- Secret: `som-db-secret` (Opaque 2 key, รหัสปัจจุบัน **`purr5678`** = เปลี่ยนรหัสแล้ว), `som-tls` (kubernetes.io/tls)
- ออเดอร์ **5** รายการ (`/api/stats` → `orders=5 products=6`) — ทั้ง 30090 และ 30092 ตอบ 200
- ServiceAccount `intern` + Role `intern-read` + context `intern` ใน kubeconfig (token อายุ 24h สร้างตอน 11:38 UTC 5 ต.ค. — หมดอายุแล้วให้รัน `./rbac/intern-context.sh` ใหม่ใน `som-shop-v7/`)
- default namespace ว่าง (เก็บกวาด LAB1–8 แล้ว), ไม่มี kind-registry ค้าง

## คำสั่งฉาก screenshot (รันใน container: `docker exec -it k8s-lab-secret011-9ffaf1 bash` แล้ว `cd /workspace/011_kubernetes_secret/02_LAB/som-shop-v7`)

ฉากทั่วไป:
```bash
kubectl -n som-shop get all,secret,cm,pvc
kubectl -n som-shop describe secret som-db-secret          # แสดงแค่ bytes
kubectl -n som-shop get secret som-db-secret -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d; echo
kubectl --context intern get secret som-db-secret          # → Error from server (Forbidden) ...
kubectl --context intern get deploy som-web -o yaml | grep -B1 -A3 secretKeyRef
curl -sk https://localhost:30082/api/stats
../labs/lab08-etcd/etcdget.sh /registry/secrets/som-shop/som-db-secret | grep -a -o 'postgres://[^@]*@'
```

ฉากเปลี่ยนรหัส (ทดสอบแล้วใน `handoff-test.log` ใช้รหัสที่ 3 `hiss9012`):
```bash
NS="-n som-shop"
# 1) เปลี่ยนรหัสใน DB อย่างเดียว
kubectl $NS exec som-db-0 -- psql -U som -d catshop -c "ALTER USER som PASSWORD 'hiss9012';"   # ALTER ROLE
# 2) restart โดยยังไม่แก้ Secret → Pod ใหม่ Init:Error, Pod เดิม 3 ตัวยังขาย (curl ได้ 200)
kubectl $NS rollout restart deploy/som-web; sleep 35; kubectl $NS get pod -l app=som-web
curl -s localhost:30080/api/stats
P=$(kubectl $NS get pod -l app=som-web --no-headers | grep -v ' Running ' | awk '{print $1}' | head -1); kubectl $NS logs $P -c db-seed | grep -E 'error:|routine'
# 3) แก้ Secret + rollout restart → ร้านกลับมา (≈18–25 วิ)
kubectl $NS create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=hiss9012 \
  --from-literal=DATABASE_URL=postgres://som:hiss9012@som-db-0.som-db:5432/catshop --dry-run=client -o yaml | kubectl apply -f -
kubectl $NS rollout restart deploy/som-web && kubectl $NS rollout status deploy/som-web --timeout=240s
kubectl $NS get pod; curl -s localhost:30080/api/stats
```

คืนสภาพ (กลับเป็น `purr5678` ตามภาพ/README — ทดสอบแล้ว):
```bash
kubectl $NS exec som-db-0 -- psql -U som -d catshop -c "ALTER USER som PASSWORD 'purr5678';"
kubectl $NS create secret generic som-db-secret --from-literal=POSTGRES_PASSWORD=purr5678 \
  --from-literal=DATABASE_URL=postgres://som:purr5678@som-db-0.som-db:5432/catshop --dry-run=client -o yaml | kubectl apply -f -
kubectl $NS rollout restart deploy/som-web && kubectl $NS rollout status deploy/som-web --timeout=240s
curl -s localhost:30080/api/stats; curl -sk https://localhost:30082/api/stats
```

หมายเหตุ: ทุก `rollout restart` เพิ่ม revision ใหม่ใน `rollout history` ที่ change-cause ซ้ำ `1.5 รหัส DB จาก Secret` (ตอนนี้แสดง revision 2–7 เพราะ revisionHistoryLimit 5 — revision 1 "ป้ายร้านจาก ConfigMap" หลุดไปแล้ว) ถ้าต้องการภาพ history สวย ให้ `kubectl $NS annotate deploy/som-web kubernetes.io/change-cause="1.5 เปลี่ยนรหัส DB" --overwrite` ก่อน restart
