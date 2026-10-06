set -v
cd /workspace/014_kubernetes_helm/02_LAB
cat labs/lab03-values/podinfo-values.yaml
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo -f labs/lab03-values/podinfo-values.yaml --set ui.message="--set ชนะ" --wait | head -7
kubectl -n helm-demo get deploy,ing
curl -s http://podinfo.localhost:30080 | grep -E '"(message|color)"'
helm get values hello -n helm-demo
helm get values hello -n helm-demo --all | grep -nE "^replicaCount|^  message|^  color|^ingress:|^  enabled" | head
echo "=== upgrade โดยไม่ส่ง values (ลองผิด)"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --wait | grep -E "REVISION|STATUS"
helm get values hello -n helm-demo
kubectl -n helm-demo get deploy,ing
curl -s -o /dev/null -w "%{http_code}\n" http://podinfo.localhost:30080
echo "=== --reuse-values ใช้ค่าของ revision ก่อน (ว่างแล้ว) — ส่งไฟล์กลับไปใหม่"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo -f labs/lab03-values/podinfo-values.yaml --wait | grep -E "REVISION|STATUS"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set ui.message="reuse-values จำค่าเดิม" --wait | grep -E "REVISION|STATUS"
helm get values hello -n helm-demo
curl -s http://podinfo.localhost:30080 | grep -E '"(message|color)"'
helm history hello -n helm-demo
