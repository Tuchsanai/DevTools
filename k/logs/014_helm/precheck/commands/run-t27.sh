cd /workspace/pc
helm upgrade --install som final/charts/som-shop -n som-shop -f final/charts/values-prod.yaml --take-ownership --force-conflicts --wait --timeout 4m 2>&1 | cut -c1-900
helm history som -n som-shop | cut -c1-200
kubectl -n som-shop get deploy,sts,pvc,ing
curl -sk https://shop.localhost:30081/api/stats; echo
