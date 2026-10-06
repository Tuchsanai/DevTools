set -v
cd /workspace/014_kubernetes_helm/02_LAB/labs/lab05-first
helm create mychart
tree mychart
grep -vE "^\s*#|^$" mychart/Chart.yaml
grep -nE "^replicaCount|^image:|^  repository|^  tag|^service:|^  type|^  port" mychart/values.yaml
helm lint mychart
helm template web mychart | grep -E "^kind:|image:"
time helm install web mychart -n first --create-namespace --wait
kubectl -n first get deploy,svc,pod
helm test web -n first --logs
kubectl -n first get pod
