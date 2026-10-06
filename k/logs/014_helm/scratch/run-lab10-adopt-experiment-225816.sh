set -v
# แก้ความผิดพลาดของการทดลอง: รอบ 1 สำเนามี SA ที่ namespace traefik (ของจริง) → kubectl delete รอบ 2 ลบ SA traefik/traefik ไปด้วย
# คืนด้วยไฟล์ static เดิมของบท (เหมือนสภาพท้ายบท 013)
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab10-addons
kubectl apply -f static-old/00-traefik.yaml
kubectl -n traefik rollout restart deploy/traefik && kubectl -n traefik rollout status deploy/traefik --timeout=120s
kubectl -n traefik get sa,deploy,pod
curl -sk https://shop.localhost:30081/api/stats; echo
curl -s -o /dev/null -w "%{http_code}\n" localhost:30080
