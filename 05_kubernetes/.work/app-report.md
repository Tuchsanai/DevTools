สร้างและทดสอบแอปครบแล้วใน [app/](/root/workspace/DevTools/05_kubernetes/app) พร้อมลบ `devtools-k8s-app` เรียบร้อย

### ไฟล์สำคัญ

- [README.md](/root/workspace/DevTools/05_kubernetes/app/README.md) — ภาษาไทย 40 บรรทัด
- [build-images.sh](/root/workspace/DevTools/05_kubernetes/app/build-images.sh)
- [compose.yaml](/root/workspace/DevTools/05_kubernetes/app/compose.yaml)
- [web/](/root/workspace/DevTools/05_kubernetes/app/web) — Next.js 16, Tailwind 4, runtime themes, standalone mode และ status card
- [api/main.py](/root/workspace/DevTools/05_kubernetes/app/api/main.py) — FastAPI, business endpoints เดิม, probes, aliases และ request logging
- [db/](/root/workspace/DevTools/05_kubernetes/app/db) — PostgreSQL 17 พร้อม schema/seed เดิม
- [k8s-reference/](/root/workspace/DevTools/05_kubernetes/app/k8s-reference) — Namespace, ConfigMap, Secret, PVC, Deployments, Services และ Ingress
- [storage-variants/](/root/workspace/DevTools/05_kubernetes/app/k8s-reference/storage-variants) — no-volume และ emptyDir

### คำสั่งที่ใช้จริง

```bash
cd ~/labwork/DevTools/05_kubernetes/app
./build-images.sh

WEB_PORT=3000 docker compose up -d
docker compose down -v

k8s-bootstrap
kind load docker-image \
  k8s-lab-web:v1 k8s-lab-web:v2 \
  k8s-lab-api:v1 k8s-lab-db:v1 \
  --name devtools

kubectl apply -f k8s-reference/
kubectl wait -n k8s-lab-ref \
  --for=condition=available deploy/db deploy/api deploy/web \
  --timeout=240s
```

ผล clean build รอบสุดท้าย:

```text
k8s-lab-api:v1   26d6e4cd794c   181MB
k8s-lab-db:v1    d00ef726fb6e   297MB
k8s-lab-web:v1   d8bb0c14f52e   205MB
k8s-lab-web:v2   b5c1d0ac9265   205MB
```

Compose ขึ้นครบสาม service เป็น `healthy`; `/info` แสดง `api.reachable=true`, `db.status=up` และ dashboard มี seed `NEW=3, ASSIGNED=2, IN_PROGRESS=1, DONE=2` จากนั้น `compose down -v` แล้วไม่เหลือ service/volume

### ผลทดสอบ kind ทั้ง 10 ข้อ

1. Load balancing web 3 replicas — ผ่าน

```text
8  web-...-m47d9
8  web-...-tfvh2
14 web-...-thw6z
```

รอบสุดท้ายหลัง scale/rollout:

```text
12 web-85c5cff695-46fvj
 9 web-85c5cff695-j2whs
 9 web-85c5cff695-sqtll
```

ภาพการ์ดสองใบแสดง Pod ต่างกันจริง: `...-sqtll` และ `...-j2whs`

2. `/api/whoami` ผ่าน Ingress — ผ่าน

```json
{"pod":"api-7f8bf97467-csd4v","version":"v1","time":"2026-09-02T15:39:54+00:00"}
```

Header มี `X-Pod-Name: api-7f8bf97467-csd4v`

3. ระบบครบสามชั้นและ seed data — ผ่าน

```json
{"api":{"configured":true,"reachable":true},"db":{"status":"up"}}
```

Dashboard: tickets `3/2/1/2`, active loans `2`, low-stock parts `2`

4. Standalone web ไม่มี API/DB — ผ่าน

```text
/        200
/tickets 200
/loans   200
/parts   200
/healthz 200
/readyz  200
```

`/info` แสดง `api.configured=false`, `db.status=unknown` และ submit ฟอร์มคืนข้อความ error ที่อ่านรู้เรื่องโดยไม่เกิด 500

5. DB ล่มทำให้ API not-ready — ผ่าน

```text
api-...-csd4v  0/1 Running
api-...-k7zcz  0/1 Running
endpoints/api  <none>
Ingress /api/ready -> HTTP 503
Ingress /          -> HTTP 200
```

ก่อน API ถูกถอดออกจาก endpoints `/info` แสดง `db.status=down`; scale DB กลับแล้ว API กลับ `1/1` ทั้งสองตัวโดยไม่ restart

6. Liveness restart — ผ่าน

```text
TARGET=api-7f8bf97467-csd4v BEFORE_RESTARTS=0
RESTARTED_AT=27s RESTARTS=1
Liveness probe failed: HTTP probe failed with statuscode: 503
Container api failed liveness probe, will be restarted
```

7. เปลี่ยน ConfigMap — ผ่าน

```json
{"version":"v1","theme":"amber","site_name":"ศูนย์บริการวิศวกรรม"}
```

เปลี่ยนหลัง `kubectl rollout restart deployment/web`

8. Rollout v1 → v2 — ผ่าน

```json
{"version":"v2","theme":"emerald","site_name":"SkillSpace"}
```

ค่า default ใน image ตรวจแล้วเป็น `v1/blue` และ `v2/emerald` โดยไม่ต้องตั้ง `THEME`

9. PVC เก็บข้อมูลหลัง DB Pod ถูกสร้างใหม่ — ผ่าน

สร้าง `K8S-PVC-VERIFY` ผ่านฟอร์มจริง:

```text
OLD_DB=db-85f6479857-l9kwb
NEW_DB=db-85f6479857-6sllb READY=true
9|K8S-PVC-VERIFY
db-data Bound ... 1Gi RWO
```

10. ลบ image แล้ว clean build ใหม่ — ผ่าน

ลบ tag ทั้ง 4 แบบเจาะจง แล้ว `./build-images.sh` ผ่านครบ รวม Next.js compile และ TypeScript

เพิ่มเติม: DB แบบ no-volume, emptyDir และ PVC รันจริงได้ทั้งหมด โดยแต่ละตัวอ่าน seed ได้ `12 assets`

### ภาพจริงจาก `shot.js`

- [Compose full stack v1](/root/workspace/DevTools/05_kubernetes/.work/app-screens/compose-full-stack-v1.png)
- [Standalone web](/root/workspace/DevTools/05_kubernetes/.work/app-screens/kind-standalone-web.png)
- [Kind full stack v1](/root/workspace/DevTools/05_kubernetes/.work/app-screens/kind-full-stack-v1.png)
- [Kind full stack v2](/root/workspace/DevTools/05_kubernetes/.work/app-screens/kind-full-stack-v2.png)
- [ConfigMap amber](/root/workspace/DevTools/05_kubernetes/.work/app-screens/kind-configmap-amber.png)
- [API not ready เมื่อ DB ล่ม](/root/workspace/DevTools/05_kubernetes/.work/app-screens/kind-api-not-ready-db-down.png)
- [Ticket ก่อนสร้าง DB Pod ใหม่](/root/workspace/DevTools/05_kubernetes/.work/app-screens/kind-ticket-created-before-db-delete.png)
- [Pod card A](/root/workspace/DevTools/05_kubernetes/.work/app-screens/kind-scale-pod-card-a.png)
- [Pod card B](/root/workspace/DevTools/05_kubernetes/.work/app-screens/kind-scale-pod-card-b.png)

### ข้อจำกัดที่พบ

Docker runner แยก network/mount namespace ทำให้ bind mount ใน outer container ปรากฏเป็นโฟลเดอร์ว่าง และ `localhost:20030/20080` จาก process host ถูกปฏิเสธ แม้ `docker port` แสดง mapping ถูกต้อง จึง sync source ด้วย `docker cp` และใช้ IP ของ container `172.17.0.2:3000/80` เฉพาะสำหรับ `shot.js` ส่วนการทดสอบ Compose/kind และ curl หลักทั้งหมดรันใน container ผ่าน `localhost:3000/80` จริง

Cleanup เสร็จแล้ว: namespace ถูกลบ, `k8s-teardown` ลบทั้งสาม kind nodes, Compose ว่าง และ `docker ps -a --filter name=^devtools-k8s-app$` ไม่คืนรายการใด ๆ ครับ