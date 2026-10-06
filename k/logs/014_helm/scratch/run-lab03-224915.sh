set -v
cd /workspace/014_kubernetes_helm/02_LAB
cat labs/lab03-values/podinfo-values.yaml
time helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo -f labs/lab03-values/podinfo-values.yaml --set ui.message="--set ชนะ" --wait | grep -E "REVISION|STATUS"
kubectl -n helm-demo get deploy,ing
curl -s http://podinfo.localhost:30080 | grep -E '"(message|color)"'
helm get values hello -n helm-demo
helm get values hello -n helm-demo --all | grep -E "^replicaCount|^  color|^  message"
echo "=== ลองผิด: ส่งแค่ --set ค่าเดียว"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --set replicaCount=1 --wait | grep -E "REVISION|STATUS"
helm get values hello -n helm-demo
kubectl -n helm-demo get deploy,ing
curl -s -o /dev/null -w "%{http_code}\n" http://podinfo.localhost:30080
echo "=== แก้: ส่งไฟล์ทุกครั้ง หรือ --reuse-values"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo -f labs/lab03-values/podinfo-values.yaml --wait | grep -E "REVISION"
helm upgrade hello podinfo/podinfo --version 6.15.0 -n helm-demo --reuse-values --set ui.message="reuse-values จำค่าเดิม" --wait | grep -E "REVISION"
helm get values hello -n helm-demo | grep -E "replicaCount|message|color"
curl -s http://podinfo.localhost:30080 | grep -E '"(message|color)"'
helm history hello -n helm-demo
