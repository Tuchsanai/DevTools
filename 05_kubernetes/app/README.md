# SkillSpace สำหรับแล็บ Kubernetes

แอปตัวอย่าง 3 ชั้น: Next.js 16 + FastAPI + PostgreSQL 17 ยกโครงจากแล็บ Docker Compose เดิม
แล้วเพิ่มสถานะ Pod, runtime config, probes, Ingress และ persistent storageสำหรับสอน Kubernetes

## Build และ Compose

```bash
cd ~/labwork/DevTools/05_kubernetes/app
./build-images.sh
WEB_PORT=3000 docker compose up -d
curl http://localhost:3000/info | jq
docker compose down -v
```

image ที่ได้คือ `k8s-lab-web:v1`, `k8s-lab-web:v2`, `k8s-lab-api:v1`, `k8s-lab-db:v1`
โดย v1 ใช้ธีม blue และ v2 ใช้ธีม emerald จาก default ที่ฝังใน image

## ทดสอบบน kind

```bash
k8s-bootstrap
kind load docker-image k8s-lab-web:v1 k8s-lab-web:v2 k8s-lab-api:v1 k8s-lab-db:v1 --name devtools
kubectl apply -f k8s-reference/
kubectl wait -n k8s-lab-ref --for=condition=available deploy/db deploy/api deploy/web --timeout=180s
curl http://localhost:8080/info | jq
curl http://localhost:8080/api/whoami | jq
```

ค่าหลักของ web คือ `SITE_NAME`, `THEME`, `API_BASE_URL`, `POD_NAME`, `NODE_NAME`
และ API รองรับ `DATABASE_URL` หรือ `DB_HOST/DB_PORT/DB_NAME/DB_USER/DB_PASSWORD`
หน้า `/healthz`, `/readyz`, `/info` เป็น endpoint ของ web; `/health`, `/ready` เป็นของ API

โหมดเดี่ยวไม่ต้องตั้ง `API_BASE_URL`; เว็บและทุกเมนูยังเปิดได้โดยแสดงสถานะรอเชื่อมต่อ
manifest หลักใช้ PVC ส่วนตัวอย่าง DB แบบ no-volume และ emptyDir อยู่ใน `k8s-reference/storage-variants/`

```bash
kubectl delete namespace k8s-lab-ref
k8s-teardown
```
