set -v
cd /workspace/014_kubernetes_helm/02_LAB
echo "=== 12.9b (ผลจริง) รหัสใหม่ + ไม่ใส่ --wait → ล้มที่ hook"
helm install som charts/som-shop -n som-dev --create-namespace -f charts/values-dev.yaml --set db.password=meow1234 --wait | grep STATUS
helm uninstall som -n som-dev; sleep 8; kubectl -n som-dev get pvc --no-headers
time helm install som charts/som-shop -n som-dev -f charts/values-dev.yaml --set db.password=purr5678 --timeout 90s 2>&1 | tail -2
helm list -n som-dev
kubectl -n som-dev get pod,job
kubectl -n som-dev logs job/som-seed -c seed --tail=3 2>&1 | tail -3
helm uninstall som -n som-dev; kubectl delete ns som-dev
