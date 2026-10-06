set -v
cd /workspace/014_kubernetes_helm/02_LAB
time helm install hello podinfo/podinfo --version 6.15.0 -n helm-demo --create-namespace --set replicaCount=2 --set ui.message="สวัสดีจากร้านน้องส้ม" --wait
helm list -n helm-demo
helm status hello -n helm-demo | head -6
helm get values hello -n helm-demo
helm get manifest hello -n helm-demo | grep -E "^kind:|^# Source"
helm get metadata hello -n helm-demo
kubectl -n helm-demo get deploy,svc,pod
kubectl -n helm-demo get secret -l owner=helm
kubectl get ns helm-demo --show-labels
kubectl -n helm-demo get deploy hello-podinfo -o jsonpath='{range .metadata.managedFields[*]}{.manager}{" "}{.operation}{"\n"}{end}'
kubectl -n helm-demo port-forward svc/hello-podinfo 9898:9898 >/dev/null 2>&1 &
sleep 3
curl -s localhost:9898 | grep -E '"(hostname|version|message|color)"'
kill %1
