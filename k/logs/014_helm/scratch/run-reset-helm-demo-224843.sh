set -v
helm uninstall hello -n helm-demo --wait
kubectl delete ns helm-demo --wait=true
