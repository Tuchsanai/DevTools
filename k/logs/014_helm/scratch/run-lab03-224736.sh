set -v
cd /workspace/014_kubernetes_helm/02_LAB
echo "=== ส่งแค่ --set ค่าเดียว (ไม่ส่ง -f) → ค่าอื่นกลับค่าเริ่มต้นของ chart"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --set replicaCount=1 --wait | grep -E "REVISION|STATUS"
helm get values hello -n helm-demo
kubectl -n helm-demo get deploy,ing
curl -s -o /dev/null -w "%{http_code}\n" http://podinfo.localhost:30080
echo "=== --reuse-values + --set ค่าใหม่ → ค่าเดิมอยู่ครบ"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo -f labs/lab03-values/podinfo-values.yaml --wait | grep -E "REVISION"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set ui.message="reuse-values จำค่าเดิม" --wait | grep -E "REVISION"
helm get values hello -n helm-demo | grep -E "replicaCount|message|enabled"
curl -s http://podinfo.localhost:30080 | grep -E '"(message|color)"'
helm history hello -n helm-demo
