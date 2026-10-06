set -v
cd /workspace/014_kubernetes_helm/02_LAB
# ดู hook seed เกิดแล้วหายระหว่าง upgrade (kubectl -w ดูได้ทีละชนิด)
helm upgrade som charts/som-shop -n som-dev -f charts/values-dev.yaml --set announcement="วันนี้ปลาทูสดมาก 🐟" --wait > /root/up.out 2>&1 &
timeout 25 kubectl -n som-dev get pod -w
wait; grep -E "REVISION|STATUS" /root/up.out
kubectl -n som-dev get job
kubectl -n som-dev get events --field-selector involvedObject.kind=Job | tail -3
