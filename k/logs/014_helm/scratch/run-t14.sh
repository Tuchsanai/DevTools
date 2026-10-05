cd /workspace/pc
kubectl -n helm-demo get secret -l owner=helm,name=hello --no-headers | wc -l
helm uninstall hello -n helm-demo --keep-history
helm list -n helm-demo; helm list -n helm-demo --uninstalled
kubectl -n helm-demo get all 2>&1 | head -3
helm history hello -n helm-demo --max 2 | cut -c1-120
helm rollback hello 11 -n helm-demo --wait 2>&1 | tail -1
helm list -n helm-demo
helm uninstall hello -n helm-demo
helm history hello -n helm-demo 2>&1
kubectl delete ns helm-demo --wait=false
