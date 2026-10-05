cd /workspace/pc
kubectl -n traefik get ingressclass -o yaml | grep -E "managed-by|release-name"
helm get manifest traefik -n traefik > addons/traefik-helm-manifest.yaml; helm get manifest metrics-server -n kube-system > addons/ms-helm-manifest.yaml
wc -l addons/*manifest.yaml
helm show chart podinfo/podinfo --version 6.15.0 | head -12
helm show values podinfo/podinfo --version 6.15.0 | grep -nE "^replicaCount|^ui:|  message|  color|^service:|^  type" | head
echo "=== install"
time helm install hello podinfo/podinfo --version 6.15.0 -n helm-demo --create-namespace --set replicaCount=2 --set ui.message="สวัสดีจากร้านน้องส้ม" --wait
helm list -n helm-demo
kubectl -n helm-demo get deploy,svc,pod
helm get values hello -n helm-demo
helm get values hello -n helm-demo --all | head -5
helm get notes hello -n helm-demo | head -5
helm get metadata hello -n helm-demo
kubectl -n helm-demo get secret -l owner=helm --show-labels
kubectl -n helm-demo get secret sh.helm.release.v1.hello.v1 -o jsonpath='{.type}'; echo
kubectl -n helm-demo get deploy hello-podinfo -o jsonpath='{.metadata.managedFields[*].manager}'; echo
kubectl -n helm-demo port-forward svc/hello-podinfo 9898:9898 >/dev/null 2>&1 & sleep 3; curl -s localhost:9898 | head -12; kill %1
